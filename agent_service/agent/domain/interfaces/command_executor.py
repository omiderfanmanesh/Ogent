"""Command executor interface for the agent service."""

import abc
from typing import Dict, Any, Optional, Callable, Awaitable


class CommandExecutorInterface(abc.ABC):
    """Interface for command executors."""
    
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
    def get_info(self) -> Dict[str, Any]:
        """Get information about the executor.
        
        Returns:
            Dict[str, Any]: Executor information
        """
        pass
    
    @abc.abstractmethod
    def is_available(self) -> bool:
        """Check if the executor is available.
        
        Returns:
            bool: True if the executor is available, False otherwise
        """
        pass
    
    @abc.abstractmethod
    def cleanup(self) -> None:
        """Clean up resources used by the executor."""
        pass 