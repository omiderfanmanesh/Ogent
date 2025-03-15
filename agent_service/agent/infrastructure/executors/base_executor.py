"""Base executor for command execution."""

import abc
import uuid
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
import platform
import logging

from agent.domain.interfaces.command_executor import CommandExecutorInterface
from agent.utils import UTC

logger = logging.getLogger("agent.executor")


class BaseExecutor(CommandExecutorInterface):
    """Base class for command executors."""
    
    def __init__(self):
        """Initialize the command executor."""
        self.enabled = True
        self.executor_type = "base"
        self.target_info = {
            "hostname": platform.node(),
            "platform": platform.system(),
            "version": platform.version()
        }
    
    async def execute(self, 
                     command: str, 
                     command_id: Optional[str] = None,
                     progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command and return the result.
        
        Args:
            command: The command to execute
            command_id: Optional ID for the command
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Command execution result
        """
        # Generate a command ID if not provided
        if command_id is None:
            command_id = str(uuid.uuid4())
        
        # Create the result dictionary
        result = {
            "command": command,
            "command_id": command_id,
            "exit_code": None,
            "stdout": "",
            "stderr": "",
            "timestamp": datetime.now(UTC).isoformat(),
            "execution_type": self.executor_type,
            "target": self.target_info.get("hostname", "unknown")
        }
        
        # Execute the command (to be implemented by subclasses)
        return await self._execute_command(command, result, progress_callback)
    
    @abc.abstractmethod
    async def _execute_command(self, 
                              command: str, 
                              result: Dict[str, Any],
                              progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command and update the result.
        
        Args:
            command: The command to execute
            result: The result dictionary to update
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Updated command execution result
        """
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the executor.
        
        Returns:
            Dict[str, Any]: Executor information
        """
        return {
            "type": self.executor_type,
            "available": self.is_available(),
            "target": self.target_info
        }
    
    def is_available(self) -> bool:
        """Check if the executor is available.
        
        Returns:
            bool: True if the executor is available, False otherwise
        """
        return self.enabled
    
    def cleanup(self) -> None:
        """Clean up resources used by the executor."""
        pass 