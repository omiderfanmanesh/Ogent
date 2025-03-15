from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class CommandPublisher(ABC):
    """
    Interface for publishing commands and command results.
    """
    
    @abstractmethod
    async def publish_command(
        self,
        agent_id: str,
        command_id: str,
        command_data: Dict[str, Any]
    ) -> bool:
        """
        Publish a command to an agent.
        
        Args:
            agent_id: The ID of the agent to send the command to
            command_id: The ID of the command
            command_data: The command data
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def publish_command_result(
        self,
        requester_id: str,
        command_id: str,
        result: Dict[str, Any],
        status: str,
        error: Optional[str] = None
    ) -> bool:
        """
        Publish a command result to a requester.
        
        Args:
            requester_id: The ID of the requester
            command_id: The ID of the command
            result: The command result
            status: The status of the command (success, error, etc.)
            error: Optional error message
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        pass 