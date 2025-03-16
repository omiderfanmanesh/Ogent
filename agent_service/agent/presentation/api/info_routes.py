"""Information-related API routes."""

import logging
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException

from agent.presentation.api.auth import authenticate
from agent.presentation.api.model import InfoResponse, ExecutorInfo
from agent.infrastructure.container import container
from agent.infrastructure.config.config import config

logger = logging.getLogger("agent.api.info")

# Create router
router = APIRouter(tags=["agent-info"])


@router.get("/info", response_model=InfoResponse)
async def get_info(authenticated: bool = Depends(authenticate)) -> InfoResponse:
    """Get agent information.
    
    Returns:
        InfoResponse: Agent information
    """
    logger.debug("Getting agent information")
    return InfoResponse(
        version=config.version,
        hostname=config.hostname,
        platform=config.platform,
        python_version=config.python_version
    )


@router.get("/executors", response_model=Dict[str, ExecutorInfo])
async def get_executors(authenticated: bool = Depends(authenticate)) -> Dict[str, ExecutorInfo]:
    """Get available executors.
    
    Returns:
        Dict[str, ExecutorInfo]: Available executors
    """
    logger.debug("Getting available executors")
    try:
        agent_manager = container.get_agent_manager()
        executors_data = agent_manager.get_available_executors()
        
        # Convert to ExecutorInfo models
        result = {}
        for executor_type, executor_data in executors_data.items():
            result[executor_type] = ExecutorInfo(
                type=executor_type,
                available=executor_data.get("available", False),
                target=executor_data.get("target", {}),
                description=executor_data.get("description")
            )
        
        return result
    except Exception as e:
        logger.error(f"Error getting executors: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting executors: {str(e)}"
        )


@router.get("/history", response_model=List[Dict[str, Any]])
async def get_history(limit: int = 10, authenticated: bool = Depends(authenticate)) -> List[Dict[str, Any]]:
    """Get command execution history.
    
    Args:
        limit: Maximum number of history items to return
        
    Returns:
        List[Dict[str, Any]]: Command execution history
    """
    logger.debug(f"Getting command history with limit {limit}")
    try:
        agent_manager = container.get_agent_manager()
        return agent_manager.get_command_history(limit)
    except Exception as e:
        logger.error(f"Error getting command history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting command history: {str(e)}"
        ) 