"""Command response model for the agent service."""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass
class CommandResponse:
    """Command response model representing the result of a command execution."""
    
    command: str
    command_id: str
    exit_code: int
    stdout: str
    stderr: str
    timestamp: datetime
    execution_type: str
    target: str
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command response to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command response
        """
        return {
            "command": self.command,
            "command_id": self.command_id,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "timestamp": self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else self.timestamp,
            "execution_type": self.execution_type,
            "target": self.target,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandResponse':
        """Create a command response from a dictionary.
        
        Args:
            data: Dictionary representation of the command response
            
        Returns:
            CommandResponse: CommandResponse instance
        """
        # Convert ISO format timestamp to datetime if it's a string
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        elif timestamp is None:
            timestamp = datetime.now()
            
        return cls(
            command=data.get("command", ""),
            command_id=data.get("command_id", ""),
            exit_code=data.get("exit_code", -1),
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            timestamp=timestamp,
            execution_type=data.get("execution_type", ""),
            target=data.get("target", ""),
            status=data.get("status", "")
        ) 