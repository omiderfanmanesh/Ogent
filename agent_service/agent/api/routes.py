"""API routes for the agent service."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from ..manager import agent_manager
from ..config import config

logger = logging.getLogger("agent.api")

# Create router
router = APIRouter(prefix="/agent", tags=["agent"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class CommandRequest(BaseModel):
    """Command execution request model."""
    command: str
    executor_type: str = "local"

class CommandResponse(BaseModel):
    """Command execution response model."""
    command: str
    command_id: str
    exit_code: int
    stdout: str
    stderr: str
    timestamp: str
    execution_type: str
    target: str
    status: str

class ExecutorInfo(BaseModel):
    """Executor information model."""
    type: str
    available: bool
    target: Dict[str, Any]

# Authentication dependency
async def authenticate(token: str = Depends(oauth2_scheme)) -> bool:
    """Authenticate the request.
    
    Args:
        token: OAuth2 token
        
    Returns:
        bool: True if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    if token != config.api_token:
        logger.warning(f"Authentication failed with token: {token}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

# Routes
@router.get("/info", response_model=Dict[str, Any])
async def get_info(authenticated: bool = Depends(authenticate)) -> Dict[str, Any]:
    """Get agent information.
    
    Returns:
        Dict[str, Any]: Agent information
    """
    logger.info("Getting agent information")
    return {
        "version": "1.0.0",
        "hostname": config.hostname,
        "executors": agent_manager.get_available_executors()
    }

@router.get("/executors", response_model=Dict[str, ExecutorInfo])
async def get_executors(authenticated: bool = Depends(authenticate)) -> Dict[str, ExecutorInfo]:
    """Get available executors.
    
    Returns:
        Dict[str, ExecutorInfo]: Available executors
    """
    logger.info("Getting available executors")
    return agent_manager.get_available_executors()

@router.get("/history", response_model=List[CommandResponse])
async def get_history(limit: int = 10, authenticated: bool = Depends(authenticate)) -> List[CommandResponse]:
    """Get command execution history.
    
    Args:
        limit: Maximum number of history items to return
        
    Returns:
        List[CommandResponse]: Command execution history
    """
    logger.info(f"Getting command history with limit: {limit}")
    return agent_manager.get_command_history(limit)

@router.post("/execute", response_model=CommandResponse)
async def execute_command(request: CommandRequest, authenticated: bool = Depends(authenticate)) -> CommandResponse:
    """Execute a command.
    
    Args:
        request: Command execution request
        
    Returns:
        CommandResponse: Command execution result
    """
    logger.info(f"Executing command: {request.command} with executor: {request.executor_type}")
    result = await agent_manager.execute_command(
        command=request.command,
        executor_type=request.executor_type
    )
    return result

# WebSocket connection manager
class ConnectionManager:
    """WebSocket connection manager."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Connect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
        """
        self.active_connections.remove(websocket)
    
    async def send_progress(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send progress update to a WebSocket client.
        
        Args:
            websocket: WebSocket connection
            data: Progress data
        """
        await websocket.send_json(data)

# Create connection manager
manager = ConnectionManager()

@router.websocket("/ws/{command_id}")
async def websocket_endpoint(websocket: WebSocket, command_id: str):
    """WebSocket endpoint for command progress updates.
    
    Args:
        websocket: WebSocket connection
        command_id: Command ID
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/execute_with_progress", response_model=CommandResponse)
async def execute_command_with_progress(request: CommandRequest, authenticated: bool = Depends(authenticate)) -> CommandResponse:
    """Execute a command with progress updates via WebSocket.
    
    Args:
        request: Command execution request
        
    Returns:
        CommandResponse: Command execution result
    """
    logger.info(f"Executing command with progress: {request.command} with executor: {request.executor_type}")
    
    async def progress_callback(data: Dict[str, Any]):
        """Send progress updates to all connected WebSocket clients.
        
        Args:
            data: Progress data
        """
        for connection in manager.active_connections:
            await manager.send_progress(connection, data)
    
    result = await agent_manager.execute_command(
        command=request.command,
        executor_type=request.executor_type,
        progress_callback=progress_callback
    )
    
    return result 