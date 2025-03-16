"""Command request DTO."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class CommandRequestDTO:
    """Command request data transfer object."""
    
    command: str
    agent_id: str
    execution_target: str = "auto"
    use_ai: bool = False
    system: str = "Linux"
    context: str = "Server administration"
    requester_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command request to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the command request
        """
        return {
            "command": self.command,
            "agent_id": self.agent_id,
            "execution_target": self.execution_target,
            "use_ai": self.use_ai,
            "system": self.system,
            "context": self.context,
            "requester_id": self.requester_id
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
            agent_id=data.get("agent_id", ""),
            execution_target=data.get("execution_target", "auto"),
            use_ai=data.get("use_ai", False),
            system=data.get("system", "Linux"),
            context=data.get("context", "Server administration"),
            requester_id=data.get("requester_id")
        ) 