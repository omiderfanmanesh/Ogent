from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import OAuth2PasswordBearer
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from ..auth import get_current_user
from ..socket_manager import socket_manager
from ..ai import ai_manager

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    responses={404: {"description": "Not found"}},
)

logger = logging.getLogger("controller")

@router.get("/", response_model=List[Dict[str, Any]])
async def list_agents(current_user: Dict = Depends(get_current_user)):
    """
    List all connected agents
    """
    agents = socket_manager.get_agents()
    return agents

@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: str, current_user: Dict = Depends(get_current_user)):
    """
    Get information about a specific agent
    """
    agent = socket_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    return agent

@router.post("/{agent_id}/execute", response_model=Dict[str, Any])
async def execute_command(
    agent_id: str, 
    command: str = Body(..., embed=True),
    execution_target: Optional[str] = Body("auto", embed=True),
    use_ai: Optional[bool] = Body(False, embed=True),
    system: Optional[str] = Body("Linux", embed=True),
    context: Optional[str] = Body("Server administration", embed=True),
    current_user: Dict = Depends(get_current_user)
):
    """
    Execute a command on a specific agent
    
    - **command**: The command to execute
    - **execution_target**: Where to execute the command (auto, local, ssh)
    - **use_ai**: Whether to use AI for command processing
    - **system**: The target system type (Linux, Windows, macOS)
    - **context**: The execution context
    """
    # Validate execution_target
    if execution_target not in ["auto", "local", "ssh"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid execution_target: {execution_target}. Must be one of: auto, local, ssh"
        )
    
    # Check if agent exists
    agent = socket_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Check if SSH is requested but not available
    if execution_target == "ssh" and not agent.get("agent_info", {}).get("ssh_enabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSH execution requested but agent does not have SSH enabled"
        )
    
    # Process command with AI if requested
    processed_command = command
    ai_result = None
    
    if use_ai:
        try:
            # Get the actual system type from agent info
            agent_system = agent.get("agent_info", {}).get("platform", "Linux")
            if agent_system == "Darwin":
                agent_system = "macOS"
            
            # Process the command with AI
            ai_result = await ai_manager.process_command(command, agent_system, context)
            
            # Check if the command is safe to execute
            if not ai_result.get("validation", {}).get("safe", True):
                risk_level = ai_result.get("validation", {}).get("risk_level", "unknown")
                risks = ai_result.get("validation", {}).get("risks", [])
                
                # If the risk level is high, reject the command
                if risk_level == "high":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Command rejected due to high security risks: {', '.join(risks)}"
                    )
            
            # Use the processed command
            processed_command = ai_result.get("processed_command", command)
            
        except Exception as e:
            logger.error(f"Error processing command with AI: {str(e)}")
            # Continue with the original command if AI processing fails
    
    # Execute the command
    logger.info(f"User {current_user['username']} executing command on agent {agent_id}: {processed_command}")
    result = await socket_manager.execute_command(agent_id, processed_command, execution_target, current_user["username"])
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute command"
        )
    
    # Add AI result to the response if available
    if ai_result:
        result["ai_processing"] = ai_result
    
    return result

@router.post("/{agent_id}/analyze", response_model=Dict[str, Any])
async def analyze_command(
    agent_id: str, 
    command: str = Body(..., embed=True),
    system: Optional[str] = Body("Linux", embed=True),
    context: Optional[str] = Body("Server administration", embed=True),
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze a command using AI without executing it
    
    - **command**: The command to analyze
    - **system**: The target system type (Linux, Windows, macOS)
    - **context**: The execution context
    """
    # Check if agent exists
    agent = socket_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID {agent_id} not found"
        )
    
    # Get the actual system type from agent info
    agent_system = agent.get("agent_info", {}).get("platform", "Linux")
    if agent_system == "Darwin":
        agent_system = "macOS"
    
    # Process the command with AI
    try:
        ai_result = await ai_manager.process_command(command, agent_system, context)
        
        # Return the AI analysis
        return {
            "command": command,
            "processed_command": ai_result.get("processed_command", command),
            "ai_processing": ai_result,
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing command with AI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing command: {str(e)}"
        )

@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_command_without_agent(
    command: str = Body(..., embed=True),
    system: Optional[str] = Body("Linux", embed=True),
    context: Optional[str] = Body("Server administration", embed=True),
    current_user: Dict = Depends(get_current_user)
):
    """
    Analyze a command using AI without executing it and without requiring an agent
    
    - **command**: The command to analyze
    - **system**: The target system type (Linux, Windows, macOS)
    - **context**: The execution context
    """
    # Process the command with AI
    try:
        ai_result = await ai_manager.process_command(command, system, context)
        
        # Return the AI analysis
        return {
            "command": command,
            "processed_command": ai_result.get("processed_command", command),
            "ai_processing": ai_result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error analyzing command with AI: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing command: {str(e)}"
        ) 