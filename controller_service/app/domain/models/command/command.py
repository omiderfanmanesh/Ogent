"""Command model."""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

from controller_service.app.domain.models.command.command_ai_processing import CommandAIProcessing


@dataclass
class Command:
    """Command model representing a command to be executed."""
    
    command: str
    command_id: str
    agent_id: str
    requester_id: Optional[str] = None
    execution_target: str = "auto"
    use_ai: bool = False
    system: str = "Linux"
    context: str = "Server administration"
    timestamp: datetime = field(default_factory=lambda: datetime.now())
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    status: str = "pending"
    ai_processing: Optional[CommandAIProcessing] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command
        """
        result = {
            "command": self.command,
            "command_id": self.command_id,
            "agent_id": self.agent_id,
            "requester_id": self.requester_id,
            "execution_target": self.execution_target,
            "use_ai": self.use_ai,
            "system": self.system,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "status": self.status
        }
        
        if self.ai_processing:
            result["ai_processing"] = self.ai_processing.to_dict()
        
        return result
    
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
        
        # Create AI processing if present
        ai_processing = None
        if "ai_processing" in data:
            ai_processing = CommandAIProcessing.from_dict(data["ai_processing"])
        
        return cls(
            command=data.get("command", ""),
            command_id=data.get("command_id", ""),
            agent_id=data.get("agent_id", ""),
            requester_id=data.get("requester_id"),
            execution_target=data.get("execution_target", "auto"),
            use_ai=data.get("use_ai", False),
            system=data.get("system", "Linux"),
            context=data.get("context", "Server administration"),
            timestamp=timestamp,
            exit_code=data.get("exit_code"),
            stdout=data.get("stdout"),
            stderr=data.get("stderr"),
            status=data.get("status", "pending"),
            ai_processing=ai_processing
        ) 