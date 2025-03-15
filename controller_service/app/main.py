import os
import socketio
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from .routes import agents
from .socket_manager import socket_manager
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    fake_users_db,
    oauth2_scheme
)

# Get the Socket.IO server instance
sio = socket_manager.sio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Controller Service", description="Real-time command execution system")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(agents.router)

# Authentication settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
ALGORITHM = "HS256"

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Store connected agents
connected_agents = {}

# Authentication functions
def verify_password(plain_password, hashed_password):
    # In production, use proper password hashing like bcrypt
    # For this example, we'll use a simple comparison
    return plain_password == "password" and hashed_password == fake_users_db["admin"]["hashed_password"]

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return User(username=user.username, disabled=user.disabled)

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Socket.IO authentication middleware
async def authenticate_socket(sid, auth):
    """Authenticate a Socket.IO connection"""
    if not auth or "token" not in auth:
        logger.warning(f"Authentication failed for {sid}: No token provided")
        return False
    
    try:
        token = auth["token"]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            logger.warning(f"Authentication failed for {sid}: Invalid token payload")
            return False
        
        user = get_user(fake_users_db, username=username)
        if user is None:
            logger.warning(f"Authentication failed for {sid}: User not found")
            return False
        
        if user.disabled:
            logger.warning(f"Authentication failed for {sid}: User disabled")
            return False
        
        # Store user information in the session
        await sio.save_session(sid, {"user": username})
        logger.info(f"Authentication successful for {sid}: {username}")
        return True
    
    except JWTError:
        logger.warning(f"Authentication failed for {sid}: JWT error")
        return False

# Socket.IO event handlers
@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    logger.info(f"Connection attempt from {sid}")
    
    # Authenticate the connection
    if not await authenticate_socket(sid, auth):
        logger.warning(f"Rejecting connection from {sid}: Authentication failed")
        return False
    
    # Get user from session
    session = await sio.get_session(sid)
    username = session.get("user", "unknown")
    
    # Check if this is an agent connection
    is_agent = auth.get("is_agent", False)
    if is_agent:
        logger.info(f"Agent connected: {username} ({sid})")
        connected_agents[sid] = {
            "username": username,
            "connected_at": datetime.utcnow().isoformat()
        }
    
    # Send connection response
    await sio.emit('connection_response', {'status': 'connected'}, room=sid)
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    # Remove from connected agents if applicable
    if sid in connected_agents:
        logger.info(f"Agent disconnected: {connected_agents[sid]['username']} ({sid})")
        del connected_agents[sid]
    
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def execute_command(sid, data):
    """Handle command execution request"""
    # Get user from session
    session = await sio.get_session(sid)
    username = session.get("user", "unknown")
    
    logger.info(f"Received command execution request from {username} ({sid}): {data}")
    
    # Validate the request
    if not isinstance(data, dict) or 'command' not in data:
        await sio.emit('command_response', {
            'status': 'error', 
            'message': 'Invalid request format'
        }, room=sid)
        return
    
    # Check if we have any connected agents
    if not connected_agents:
        await sio.emit('command_response', {
            'status': 'error',
            'message': 'No agents available to execute command',
            'timestamp': datetime.utcnow().isoformat()
        }, room=sid)
        return
    
    # For simplicity, we'll send the command to the first connected agent
    # In a real implementation, you would have logic to select the appropriate agent
    agent_sid = next(iter(connected_agents))
    
    # Store the requester's SID so we can route the response back
    data['requester_sid'] = sid
    
    # Forward the command to the agent
    await sio.emit('execute_command_event', data, room=agent_sid)
    
    # Send an acknowledgment to the requester
    await sio.emit('command_response', {
        'status': 'pending',
        'command': data['command'],
        'message': 'Command sent to agent for execution',
        'timestamp': datetime.utcnow().isoformat()
    }, room=sid)

@sio.event
async def command_result(sid, data):
    """Handle command execution result from an agent"""
    # Get user from session
    session = await sio.get_session(sid)
    username = session.get("user", "unknown")
    
    logger.info(f"Received command result from agent {username} ({sid}): {data}")
    
    # Validate the result
    if not isinstance(data, dict) or 'command' not in data:
        logger.error(f"Invalid command result format from agent {username} ({sid})")
        return
    
    # Get the requester's SID
    requester_sid = data.pop('requester_sid', None)
    
    # If we have a requester SID, forward the result
    if requester_sid:
        await sio.emit('command_response', {
            'status': data.get('status', 'unknown'),
            'command': data.get('command', ''),
            'result': data.get('result', {}),
            'timestamp': datetime.utcnow().isoformat()
        }, room=requester_sid)
    else:
        logger.warning(f"Command result received but no requester SID provided: {data}")

# FastAPI routes
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Endpoint to obtain an access token"""
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: Dict = Depends(get_current_active_user)):
    """Endpoint to get the current user's information"""
    return {"username": current_user["username"], "disabled": current_user.get("disabled", False)}

@app.get("/agents")
async def list_agents(current_user: User = Depends(get_current_active_user)):
    """Endpoint to list connected agents"""
    return {
        "agents": [
            {
                "id": sid,
                "username": info["username"],
                "connected_at": info["connected_at"]
            }
            for sid, info in connected_agents.items()
        ]
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Controller Service",
        "version": "0.1.0",
        "documentation": "/docs"
    }

# Mount the Socket.IO app
app.mount("/", socket_manager.app) 