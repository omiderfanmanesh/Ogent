"""Command response data transfer object for the agent service."""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass
class CommandResponseDTO:
    """Command response data transfer object."""
    
    command: str
    command_id: str
    executor_type: str
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
            "executor_type": self.executor_type,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "timestamp": self.timestamp.isoformat(),
            "execution_type": self.execution_type,
            "target": self.target,
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandResponseDTO':
        """Create a command response from a dictionary.
        
        Args:
            data: Dictionary representation of the command response
            
        Returns:
            CommandResponseDTO: Command response instance
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
            exit_code=data.get("exit_code", 1),
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            timestamp=timestamp,
            execution_type=data.get("execution_type", "command"),
            target=data.get("target", "unknown"),
            status=data.get("status", "error")
        ) 