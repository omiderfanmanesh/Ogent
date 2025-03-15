"""Agent manager for handling command execution."""

import logging
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from datetime import datetime, UTC

from agent.domain.interfaces.command_executor import CommandExecutorInterface
from agent.domain.models.command import Command
from agent.domain.models.executor import Executor
from agent.application.dtos.command_dto import CommandRequestDTO, CommandResponseDTO

logger = logging.getLogger("agent.manager")


class AgentManager:
    """Manager for handling command execution and managing executors."""
    
    def __init__(self, executors: Dict[str, CommandExecutorInterface] = None):
        """Initialize the agent manager.
        
        Args:
            executors: Dictionary of command executors
        """
        self.executors: Dict[str, CommandExecutorInterface] = executors or {}
        
        # Command history
        self.command_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
    
    def get_available_executors(self) -> Dict[str, Dict[str, Any]]:
        """Get available executors.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of available executors
        """
        available_executors = {}
        for name, executor in self.executors.items():
            executor_info = executor.get_info()
            available_executors[name] = executor_info
        
        return available_executors
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get command execution history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List[Dict[str, Any]]: List of command execution results
        """
        # Return the most recent history items
        return self.command_history[-limit:] if limit > 0 else []
    
    def _add_to_history(self, result: Dict[str, Any]) -> None:
        """Add a command execution result to the history.
        
        Args:
            result: Command execution result
        """
        # Add the result to the history
        self.command_history.append(result)
        
        # Trim the history if it exceeds the maximum size
        if len(self.command_history) > self.max_history_size:
            self.command_history = self.command_history[-self.max_history_size:]
    
    async def execute_command(self, 
                             command: str, 
                             executor_type: str = "auto",
                             command_id: Optional[str] = None,
                             progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command using the specified executor.
        
        Args:
            command: The command to execute
            executor_type: The type of executor to use (local, ssh, or auto)
            command_id: Optional ID for the command
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Command execution result
        """
        # Generate a command ID if not provided
        if command_id is None:
            command_id = str(uuid.uuid4())
        
        # Determine the executor to use
        executor = self._get_executor(executor_type)
        if executor is None:
            logger.error(f"No suitable executor found for type: {executor_type}")
            result = {
                "command": command,
                "command_id": command_id,
                "exit_code": 1,
                "stdout": "",
                "stderr": f"No suitable executor found for type: {executor_type}",
                "timestamp": datetime.now(UTC).isoformat(),
                "execution_type": "error",
                "target": "agent",
                "status": "error"
            }
            self._add_to_history(result)
            return result
        
        # Execute the command
        try:
            logger.info(f"Executing command: {command} using executor: {executor_type}")
            result = await executor.execute(command, command_id, progress_callback)
            
            # Add status to the result
            result["status"] = "success" if result.get("exit_code", 1) == 0 else "error"
            
            # Add the result to the history
            self._add_to_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            result = {
                "command": command,
                "command_id": command_id,
                "exit_code": 1,
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat(),
                "execution_type": "error",
                "target": "agent",
                "status": "error"
            }
            self._add_to_history(result)
            return result
    
    def _get_executor(self, executor_type: str) -> Optional[CommandExecutorInterface]:
        """Get an executor of the specified type.
        
        Args:
            executor_type: The type of executor to get (local, ssh, or auto)
            
        Returns:
            Optional[CommandExecutorInterface]: The executor, or None if not found
        """
        # If auto, determine the best executor to use
        if executor_type == "auto":
            # Try SSH first if available
            if "ssh" in self.executors and self.executors["ssh"].is_available():
                return self.executors["ssh"]
            # Fall back to local
            elif "local" in self.executors:
                return self.executors["local"]
            # No suitable executor found
            else:
                return None
        
        # Get the specified executor if available
        if executor_type in self.executors:
            return self.executors[executor_type]
        
        # No suitable executor found
        return None
    
    def cleanup(self) -> None:
        """Clean up resources used by the manager."""
        for executor in self.executors.values():
            executor.cleanup()


# Create a singleton instance
agent_manager = AgentManager() 