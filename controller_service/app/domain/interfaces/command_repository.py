"""Command repository interface for the controller service."""

import abc
from typing import Dict, Any, List, Optional
from ..models.command import Command


class CommandRepositoryInterface(abc.ABC):
    """Interface for command repositories."""
    
    @abc.abstractmethod
    async def add_command(self, command: Command) -> None:
        """Add a command to the repository.
        
        Args:
            command: The command to add
        """
        pass
    
    @abc.abstractmethod
    async def get_command(self, command_id: str) -> Optional[Command]:
        """Get a command by ID.
        
        Args:
            command_id: The ID of the command to get
            
        Returns:
            Optional[Command]: The command, or None if not found
        """
        pass
    
    @abc.abstractmethod
    async def get_commands_by_agent(self, agent_id: str, limit: int = 10) -> List[Command]:
        """Get commands by agent ID.
        
        Args:
            agent_id: The ID of the agent
            limit: Maximum number of commands to return
            
        Returns:
            List[Command]: List of commands
        """
        pass
    
    @abc.abstractmethod
    async def get_commands_by_requester(self, requester_id: str, limit: int = 10) -> List[Command]:
        """Get commands by requester ID.
        
        Args:
            requester_id: The ID of the requester
            limit: Maximum number of commands to return
            
        Returns:
            List[Command]: List of commands
        """
        pass
    
    @abc.abstractmethod
    async def update_command(self, command: Command) -> None:
        """Update a command in the repository.
        
        Args:
            command: The command to update
        """
        pass
    
    @abc.abstractmethod
    async def delete_command(self, command_id: str) -> None:
        """Delete a command from the repository.
        
        Args:
            command_id: The ID of the command to delete
        """
        pass 