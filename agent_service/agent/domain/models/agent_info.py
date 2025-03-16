"""Agent information model for the agent service."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class AgentInfo:
    """Agent information model representing agent details."""
    
    version: str
    hostname: str
    executors: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent info to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the agent info
        """
        return {
            "version": self.version,
            "hostname": self.hostname,
            "executors": self.executors
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfo':
        """Create an agent info from a dictionary.
        
        Args:
            data: Dictionary representation of the agent info
            
        Returns:
            AgentInfo: AgentInfo instance
        """
        return cls(
            version=data.get("version", ""),
            hostname=data.get("hostname", ""),
            executors=data.get("executors", {})
        ) 