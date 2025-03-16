"""Command request data transfer object for the agent service."""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CommandRequestDTO:
    """Command request data transfer object."""
    
    command: str
    executor_type: str = "local"
    command_id: Optional[str] = None
    with_progress: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command request to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command request
        """
        return {
            "command": self.command,
            "executor_type": self.executor_type,
            "command_id": self.command_id,
            "with_progress": self.with_progress
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandRequestDTO':
        """Create a command request from a dictionary.
        
        Args:
            data: Dictionary representation of the command request
            
        Returns:
            CommandRequestDTO: Command request instance
        """
        return cls(
            command=data.get("command", ""),
            executor_type=data.get("executor_type", "local"),
            command_id=data.get("command_id"),
            with_progress=data.get("with_progress", False)
        ) 