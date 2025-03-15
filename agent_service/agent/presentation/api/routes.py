"""API routes for the agent service."""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer

from agent.presentation.api.models import CommandRequest, CommandResponse, ExecutorInfo, InfoResponse
from agent.infrastructure.container import container
from agent.infrastructure.config.config import config

logger = logging.getLogger("agent.api")

# Create router
router = APIRouter(prefix="/agent", tags=["agent"])

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
    return {
        "version": config.version,
        "hostname": config.hostname,
        "platform": config.platform,
        "python_version": config.python_version
    }


@router.get("/executors", response_model=Dict[str, Any])
async def get_executors(authenticated: bool = Depends(authenticate)) -> Dict[str, Any]:
    """Get available executors.
    
    Returns:
        Dict[str, Any]: Available executors
    """
    agent_manager = container.get_agent_manager()
    return agent_manager.get_available_executors()


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_history(limit: int = 10, authenticated: bool = Depends(authenticate)) -> List[Dict[str, Any]]:
    """Get command execution history.
    
    Args:
        limit: Maximum number of history items to return
        
    Returns:
        List[Dict[str, Any]]: Command execution history
    """
    agent_manager = container.get_agent_manager()
    return agent_manager.get_command_history(limit)


@router.post("/execute", response_model=Dict[str, Any])
async def execute_command(request: CommandRequest, authenticated: bool = Depends(authenticate)) -> Dict[str, Any]:
    """Execute a command.
    
    Args:
        request: Command execution request
        
    Returns:
        Dict[str, Any]: Command execution result
    """
    # Check if progress updates are requested
    if request.with_progress:
        # Return a WebSocket URL for progress updates
        return {
            "status": "redirect",
            "message": "Use WebSocket for progress updates",
            "websocket_url": f"/agent/execute/ws?command={request.command}&executor_type={request.executor_type}"
        }
    
    # Execute the command
    agent_manager = container.get_agent_manager()
    result = await agent_manager.execute_command(
        command=request.command,
        executor_type=request.executor_type
    )
    
    return result


@router.websocket("/execute/ws")
async def execute_command_ws(websocket: WebSocket):
    """Execute a command with WebSocket progress updates.
    
    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    
    try:
        # Get command parameters from query
        params = websocket.query_params
        command = params.get("command")
        executor_type = params.get("executor_type", "local")
        
        if not command:
            await websocket.send_json({
                "status": "error",
                "message": "Command parameter is required"
            })
            await websocket.close()
            return
        
        # Create a progress callback
        async def progress_callback(progress_data):
            await websocket.send_json(progress_data)
        
        # Execute the command
        agent_manager = container.get_agent_manager()
        result = await agent_manager.execute_command(
            command=command,
            executor_type=executor_type,
            progress_callback=progress_callback
        )
        
        # Send the final result
        await websocket.send_json({
            "status": "complete",
            "result": result
        })
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        try:
            await websocket.send_json({
                "status": "error",
                "message": f"Error executing command: {str(e)}"
            })
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass 