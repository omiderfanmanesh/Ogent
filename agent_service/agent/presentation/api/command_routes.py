"""Command execution API routes."""

import logging
from typing import Dict, Any, Union
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException

from agent.presentation.api.auth import authenticate
from agent.presentation.api.model import (
    CommandRequest, 
    CommandResponse, 
    WebSocketRedirectResponse,
    ErrorResponse,
    ProgressResponse
)
from agent.infrastructure.container import container

logger = logging.getLogger("agent.api.command")

# Create router
router = APIRouter(tags=["agent-commands"])


@router.post("/execute", response_model=Union[Dict[str, Any], WebSocketRedirectResponse])
async def execute_command(request: CommandRequest, authenticated: bool = Depends(authenticate)) -> Dict[str, Any]:
    """Execute a command.
    
    Args:
        request: Command execution request
        
    Returns:
        Dict[str, Any]: Command execution result or WebSocket redirect
    """
    logger.info(f"Executing command: {request.command} with executor: {request.executor_type}")
    
    # Check if progress updates are requested
    if request.with_progress:
        # Return a WebSocket URL for progress updates
        return WebSocketRedirectResponse(
            status="redirect",
            message="Use WebSocket for progress updates",
            websocket_url=f"/agent/execute/ws?command={request.command}&executor_type={request.executor_type}"
        ).dict()
    
    try:
        # Execute the command
        agent_manager = container.get_agent_manager()
        result = await agent_manager.execute_command(
            command=request.command,
            executor_type=request.executor_type
        )
        
        return result
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error executing command: {str(e)}"
        )


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
            await websocket.send_json(
                ErrorResponse(
                    status="error",
                    message="Command parameter is required"
                ).dict()
            )
            await websocket.close()
            return
        
        logger.info(f"Executing command via WebSocket: {command} with executor: {executor_type}")
        
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
        logger.error(f"Error executing command via WebSocket: {str(e)}")
        try:
            await websocket.send_json(
                ErrorResponse(
                    status="error",
                    message=f"Error executing command: {str(e)}"
                ).dict()
            )
        except:
            logger.error("Failed to send error message to WebSocket")
    finally:
        try:
            await websocket.close()
        except:
            logger.error("Failed to close WebSocket connection") 