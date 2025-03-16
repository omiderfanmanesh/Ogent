"""Executor information model for the agent service."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ExecutorInfo:
    """Executor information model representing details about a command executor."""
    
    type: str
    available: bool
    target: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the executor info to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the executor info
        """
        return {
            "type": self.type,
            "available": self.available,
            "target": self.target
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutorInfo':
        """Create an executor info from a dictionary.
        
        Args:
            data: Dictionary representation of the executor info
            
        Returns:
            ExecutorInfo: ExecutorInfo instance
        """
        return cls(
            type=data.get("type", ""),
            available=data.get("available", False),
            target=data.get("target", {})
        ) 