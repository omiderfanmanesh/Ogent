"""Command request model for the agent service."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CommandRequest:
    """Command request model representing a request to execute a command."""
    
    command: str
    executor_type: str = "local"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command request to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command request
        """
        return {
            "command": self.command,
            "executor_type": self.executor_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandRequest':
        """Create a command request from a dictionary.
        
        Args:
            data: Dictionary representation of the command request
            
        Returns:
            CommandRequest: CommandRequest instance
        """
        return cls(
            command=data.get("command", ""),
            executor_type=data.get("executor_type", "local")
        ) 