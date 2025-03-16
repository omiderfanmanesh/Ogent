"""Command response DTO."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

from controller_service.app.application.dtos.command.command_ai_processing_dto import CommandAIProcessingDTO


@dataclass
class CommandResponseDTO:
    """Command response data transfer object."""
    
    command: str
    command_id: str
    agent_id: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    status: str = "pending"
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    execution_type: Optional[str] = None
    target: Optional[str] = None
    ai_processing: Optional[CommandAIProcessingDTO] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command response to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command response
        """
        result = {
            "command": self.command,
            "command_id": self.command_id,
            "agent_id": self.agent_id,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "execution_type": self.execution_type,
            "target": self.target
        }
        
        if self.ai_processing:
            result["ai_processing"] = self.ai_processing.to_dict()
        
        return result
    
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
        
        # Create AI processing if present
        ai_processing = None
        if "ai_processing" in data:
            ai_processing = CommandAIProcessingDTO.from_dict(data["ai_processing"])
        
        return cls(
            command=data.get("command", ""),
            command_id=data.get("command_id", ""),
            agent_id=data.get("agent_id", ""),
            exit_code=data.get("exit_code"),
            stdout=data.get("stdout"),
            stderr=data.get("stderr"),
            status=data.get("status", "pending"),
            timestamp=timestamp,
            execution_type=data.get("execution_type"),
            target=data.get("target"),
            ai_processing=ai_processing
        ) 