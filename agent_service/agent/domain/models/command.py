"""Command model for the agent service."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class Command:
    """Command model representing a command to be executed."""
    
    command: str
    command_id: str
    executor_type: str
    timestamp: datetime
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    execution_type: Optional[str] = None
    target: Optional[str] = None
    status: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command
        """
        return {
            "command": self.command,
            "command_id": self.command_id,
            "executor_type": self.executor_type,
            "timestamp": self.timestamp.isoformat(),
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "execution_type": self.execution_type,
            "target": self.target,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Command':
        """Create a command from a dictionary.
        
        Args:
            data: Dictionary representation of the command
            
        Returns:
            Command: Command instance
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
            executor_type=data.get("executor_type", "local"),
            timestamp=timestamp,
            exit_code=data.get("exit_code"),
            stdout=data.get("stdout"),
            stderr=data.get("stderr"),
            execution_type=data.get("execution_type"),
            target=data.get("target"),
            status=data.get("status")
        ) 