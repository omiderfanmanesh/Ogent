"""Agent model for the controller service."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Agent:
    """Agent model representing a connected agent."""
    
    agent_id: str
    sid: str
    connected_at: datetime
    hostname: Optional[str] = None
    platform: Optional[str] = None
    version: Optional[str] = None
    python_version: Optional[str] = None
    ssh_enabled: bool = False
    ssh_target: Optional[str] = None
    executors: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the agent
        """
        return {
            "agent_id": self.agent_id,
            "sid": self.sid,
            "connected_at": self.connected_at.isoformat(),
            "hostname": self.hostname,
            "platform": self.platform,
            "version": self.version,
            "python_version": self.python_version,
            "ssh_enabled": self.ssh_enabled,
            "ssh_target": self.ssh_target,
            "executors": self.executors or {},
            "agent_info": {
                "hostname": self.hostname,
                "platform": self.platform,
                "version": self.version,
                "python_version": self.python_version,
                "ssh_enabled": self.ssh_enabled,
                "ssh_target": self.ssh_target
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create an agent from a dictionary.
        
        Args:
            data: Dictionary representation of the agent
            
        Returns:
            Agent: Agent instance
        """
        # Convert ISO format timestamp to datetime if it's a string
        connected_at = data.get("connected_at")
        if isinstance(connected_at, str):
            connected_at = datetime.fromisoformat(connected_at)
        elif connected_at is None:
            connected_at = datetime.now()
        
        # Extract agent info if present
        agent_info = data.get("agent_info", {})
        
        return cls(
            agent_id=data.get("agent_id", ""),
            sid=data.get("sid", ""),
            connected_at=connected_at,
            hostname=data.get("hostname") or agent_info.get("hostname"),
            platform=data.get("platform") or agent_info.get("platform"),
            version=data.get("version") or agent_info.get("version"),
            python_version=data.get("python_version") or agent_info.get("python_version"),
            ssh_enabled=data.get("ssh_enabled", False) or agent_info.get("ssh_enabled", False),
            ssh_target=data.get("ssh_target") or agent_info.get("ssh_target"),
            executors=data.get("executors", {})
        ) 