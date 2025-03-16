"""Command progress model for the agent service."""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass
class CommandProgress:
    """Command progress model representing the progress of a command execution."""
    
    command_id: str
    status: str
    progress: int
    message: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command progress to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command progress
        """
        return {
            "command_id": self.command_id,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandProgress':
        """Create a command progress from a dictionary.
        
        Args:
            data: Dictionary representation of the command progress
            
        Returns:
            CommandProgress: CommandProgress instance
        """
        # Convert ISO format timestamp to datetime if it's a string
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
            
        return cls(
            command_id=data.get("command_id", ""),
            status=data.get("status", ""),
            progress=data.get("progress", 0),
            message=data.get("message", ""),
            timestamp=timestamp
        ) 