"""Repository for command execution history."""

import logging
from typing import List, Dict, Any
from fastapi import Depends

from ..domain.models import CommandResponse

logger = logging.getLogger("agent.infrastructure.command_repository")

class CommandRepository:
    """Repository for command execution history.
    
    This class follows the Repository pattern to abstract the storage
    of command execution history.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a new instance if one doesn't exist."""
        if cls._instance is None:
            cls._instance = super(CommandRepository, cls).__new__(cls)
            cls._instance.command_history = []
            cls._instance.max_history_size = 100
        return cls._instance
    
    def __init__(self):
        """Initialize the command repository."""
        # Initialize command_history only if it doesn't exist
        if not hasattr(self, "command_history"):
            self.command_history: List[CommandResponse] = []
            self.max_history_size = 100
    
    def add(self, command_result: CommandResponse) -> None:
        """Add a command execution result to history.
        
        Args:
            command_result: Command execution result
        """
        self.command_history.append(command_result)
        
        # Trim history if it exceeds max size
        if len(self.command_history) > self.max_history_size:
            self.command_history = self.command_history[-self.max_history_size:]
        
        logger.debug(f"Added command to history: {command_result.command_id}")
    
    def get_history(self, limit: int = 10) -> List[CommandResponse]:
        """Get command execution history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List[CommandResponse]: List of command execution results
        """
        return self.command_history[-limit:] if limit > 0 else self.command_history
    
    def get_by_id(self, command_id: str) -> CommandResponse:
        """Get a command execution result by ID.
        
        Args:
            command_id: Command ID
            
        Returns:
            CommandResponse: Command execution result
            
        Raises:
            KeyError: If command ID is not found
        """
        for result in self.command_history:
            if result.command_id == command_id:
                return result
        
        raise KeyError(f"Command ID not found: {command_id}")
    
    def clear(self) -> None:
        """Clear command execution history."""
        self.command_history = []
        logger.debug("Command history cleared") 