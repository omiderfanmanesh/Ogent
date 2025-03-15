"""Executor model for the agent service."""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class Executor:
    """Executor model representing a command executor."""
    
    type: str
    available: bool
    target: Dict[str, Any]
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the executor to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the executor
        """
        return {
            "type": self.type,
            "available": self.available,
            "target": self.target,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Executor':
        """Create an executor from a dictionary.
        
        Args:
            data: Dictionary representation of the executor
            
        Returns:
            Executor: Executor instance
        """
        return cls(
            type=data.get("type", ""),
            available=data.get("available", False),
            target=data.get("target", {}),
            description=data.get("description")
        ) 