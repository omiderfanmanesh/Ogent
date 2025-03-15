"""Base executor for command execution."""

import abc
import uuid
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime
import platform
import logging

from ..utils import UTC

logger = logging.getLogger("agent.executor")

class CommandExecutor(abc.ABC):
    """Base class for command executors."""
    
    def __init__(self):
        """Initialize the command executor."""
        self.enabled = True
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if the executor is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def get_target_info(self) -> Dict[str, Any]:
        """Get information about the execution target.
        
        Returns:
            Dict[str, Any]: Target information
        """
        pass
    
    def _create_base_result(self, command: str, exit_code: int, stdout: str, stderr: str, execution_type: str, target: str) -> Dict[str, Any]:
        """Create a base result dictionary.
        
        Args:
            command: The command that was executed
            exit_code: The exit code of the command
            stdout: The standard output of the command
            stderr: The standard error of the command
            execution_type: The type of execution (local, ssh, etc.)
            target: The target of the execution
            
        Returns:
            Dict[str, Any]: Base result dictionary
        """
        return {
            "command": command,
            "command_id": str(uuid.uuid4()),  # Generate a unique ID if not provided
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "timestamp": datetime.now(UTC).isoformat(),
            "execution_type": execution_type,
            "target": target
        }
    
    async def _send_progress_update(self, 
                                   command_id: Optional[str], 
                                   progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]], 
                                   data: Dict[str, Any]) -> None:
        """Send a progress update.
        
        Args:
            command_id: The ID of the command
            progress_callback: The callback for progress updates
            data: The progress data to send
        """
        if not command_id or not progress_callback:
            return
        
        try:
            # Add command ID to progress data
            data['command_id'] = command_id
            
            # Call the progress callback
            await progress_callback(data)
        except Exception as e:
            logger.error(f"Error sending command progress: {str(e)}") 