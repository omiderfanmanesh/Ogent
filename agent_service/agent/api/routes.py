"""API routes for the agent service."""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..domain.models import CommandRequest, CommandResponse, ExecutorInfo
from ..application.command_service import CommandService
from ..application.agent_service import AgentService
from .auth import authenticate
from .websocket import ConnectionManager

logger = logging.getLogger("agent.api")

# Create router
router = APIRouter(prefix="/agent", tags=["agent"])

# Create connection manager
manager = ConnectionManager()

# Routes
@router.get("/info", response_model=Dict[str, Any])
async def get_info(
    agent_service: AgentService = Depends(),
    authenticated: bool = Depends(authenticate)
) -> Dict[str, Any]:
    """Get agent information.
    
    Returns:
        Dict[str, Any]: Agent information
    """
    logger.info("Getting agent information")
    return agent_service.get_agent_info()

@router.get("/executors", response_model=Dict[str, ExecutorInfo])
async def get_executors(
    agent_service: AgentService = Depends(),
    authenticated: bool = Depends(authenticate)
) -> Dict[str, ExecutorInfo]:
    """Get available executors.
    
    Returns:
        Dict[str, ExecutorInfo]: Available executors
    """
    logger.info("Getting available executors")
    return agent_service.get_available_executors()

@router.get("/history", response_model=List[CommandResponse])
async def get_history(
    limit: int = 10,
    command_service: CommandService = Depends(),
    authenticated: bool = Depends(authenticate)
) -> List[CommandResponse]:
    """Get command execution history.
    
    Args:
        limit: Maximum number of history items to return
        
    Returns:
        List[CommandResponse]: Command execution history
    """
    logger.info(f"Getting command history with limit: {limit}")
    return command_service.get_command_history(limit)

@router.post("/execute", response_model=CommandResponse)
async def execute_command(
    request: CommandRequest,
    command_service: CommandService = Depends(),
    authenticated: bool = Depends(authenticate)
) -> CommandResponse:
    """Execute a command.
    
    Args:
        request: Command execution request
        
    Returns:
        CommandResponse: Command execution result
    """
    logger.info(f"Executing command: {request.command} with executor: {request.executor_type}")
    result = await command_service.execute_command(
        command=request.command,
        executor_type=request.executor_type
    )
    return result

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
async def execute_command_with_progress(
    request: CommandRequest,
    command_service: CommandService = Depends(),
    authenticated: bool = Depends(authenticate)
) -> CommandResponse:
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
    
    result = await command_service.execute_command(
        command=request.command,
        executor_type=request.executor_type,
        progress_callback=progress_callback
    )
    
    return result 