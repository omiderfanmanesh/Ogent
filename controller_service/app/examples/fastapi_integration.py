import asyncio
import logging
import os
import sys
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.infrastructure.messaging import MessagingFactory
from app.domain.interfaces import EventHandlerType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fastapi_integration")

# Create FastAPI app
app = FastAPI(title="Ogent Controller API")

# Create messaging factory
redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
factory = MessagingFactory(redis_url=redis_url, logger=logger)

# Create Socket.IO manager
socket_manager = factory.create_socket_manager()

# Create command publisher
command_publisher = factory.create_command_publisher("socketio")

# Mount Socket.IO app
app.mount("/ws", socket_manager.app)

# Pydantic models
class CommandRequest(BaseModel):
    agent_id: str
    command: str
    execution_target: str = "shell"
    execution_context: Dict[str, Any] = {}

class CommandResponse(BaseModel):
    command_id: str
    agent_id: str
    status: str

class AgentInfo(BaseModel):
    agent_id: str
    username: Optional[str] = None
    status: str
    connected_at: Optional[str] = None

# In-memory storage for connected agents
connected_agents = {}

# Example event handler for agent registration
async def handle_agent_registration(session, data):
    logger.info(f"Agent registration from session {session.get('sid')}: {data}")
    
    # Extract agent information
    agent_id = data.get("agent_id")
    username = data.get("username")
    
    if not agent_id:
        logger.error("Missing agent_id in registration data")
        return
    
    # Update session with agent information
    await socket_manager.save_session(session["sid"], {
        "user_id": agent_id,
        "username": username,
        "type": "agent"
    })
    
    # Store agent information
    connected_agents[agent_id] = {
        "agent_id": agent_id,
        "username": username,
        "status": "connected",
        "connected_at": asyncio.get_event_loop().time(),
        "sid": session["sid"]
    }
    
    logger.info(f"Agent {agent_id} registered successfully")

# Example event handler for command results
async def handle_command_result(session, data):
    logger.info(f"Command result from session {session.get('user_id', 'unknown')}: {data}")
    
    # Process the result
    command_id = data.get("command_id")
    result = data.get("result", {})
    status = data.get("status", "unknown")
    
    logger.info(f"Command {command_id} completed with status {status}: {result}")

# Register event handlers
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up FastAPI application")
    
    # Register event handlers
    await socket_manager.register_handler("register", handle_agent_registration)
    await socket_manager.register_handler("command_result", handle_command_result)
    
    logger.info("Event handlers registered")

# API endpoints
@app.get("/agents", response_model=List[AgentInfo])
async def get_agents():
    """Get all connected agents."""
    return [
        AgentInfo(
            agent_id=agent_id,
            username=info.get("username"),
            status=info.get("status", "unknown"),
            connected_at=info.get("connected_at")
        )
        for agent_id, info in connected_agents.items()
    ]

@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(agent_id: str):
    """Get information about a specific agent."""
    if agent_id not in connected_agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    info = connected_agents[agent_id]
    return AgentInfo(
        agent_id=agent_id,
        username=info.get("username"),
        status=info.get("status", "unknown"),
        connected_at=info.get("connected_at")
    )

@app.post("/commands", response_model=CommandResponse)
async def execute_command(command_request: CommandRequest):
    """Execute a command on an agent."""
    agent_id = command_request.agent_id
    
    # Check if agent is connected
    if agent_id not in connected_agents:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    
    # Generate command ID
    command_id = f"cmd-{asyncio.get_event_loop().time()}"
    
    # Prepare command data
    command_data = {
        "command": command_request.command,
        "execution_target": command_request.execution_target,
        "execution_context": command_request.execution_context
    }
    
    # Publish command
    success = await command_publisher.publish_command(
        agent_id=agent_id,
        command_id=command_id,
        command_data=command_data
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to publish command")
    
    return CommandResponse(
        command_id=command_id,
        agent_id=agent_id,
        status="pending"
    )

if __name__ == "__main__":
    uvicorn.run("fastapi_integration:app", host="0.0.0.0", port=8000, reload=True) 