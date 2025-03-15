"""Agent DTOs for the controller service."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class AgentInfoDTO:
    """Agent information data transfer object."""
    
    hostname: Optional[str] = None
    platform: Optional[str] = None
    version: Optional[str] = None
    python_version: Optional[str] = None
    ssh_enabled: bool = False
    ssh_target: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent info to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the agent info
        """
        return {
            "hostname": self.hostname,
            "platform": self.platform,
            "version": self.version,
            "python_version": self.python_version,
            "ssh_enabled": self.ssh_enabled,
            "ssh_target": self.ssh_target
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentInfoDTO':
        """Create an agent info from a dictionary.
        
        Args:
            data: Dictionary representation of the agent info
            
        Returns:
            AgentInfoDTO: Agent info instance
        """
        return cls(
            hostname=data.get("hostname"),
            platform=data.get("platform"),
            version=data.get("version"),
            python_version=data.get("python_version"),
            ssh_enabled=data.get("ssh_enabled", False),
            ssh_target=data.get("ssh_target")
        )


@dataclass
class AgentDTO:
    """Agent data transfer object."""
    
    agent_id: str
    sid: str
    connected_at: datetime
    agent_info: AgentInfoDTO
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
            "agent_info": self.agent_info.to_dict(),
            "executors": self.executors or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentDTO':
        """Create an agent from a dictionary.
        
        Args:
            data: Dictionary representation of the agent
            
        Returns:
            AgentDTO: Agent instance
        """
        # Convert ISO format timestamp to datetime if it's a string
        connected_at = data.get("connected_at")
        if isinstance(connected_at, str):
            connected_at = datetime.fromisoformat(connected_at)
        elif connected_at is None:
            connected_at = datetime.now()
        
        # Extract agent info
        agent_info_data = data.get("agent_info", {})
        agent_info = AgentInfoDTO.from_dict(agent_info_data)
        
        return cls(
            agent_id=data.get("agent_id", ""),
            sid=data.get("sid", ""),
            connected_at=connected_at,
            agent_info=agent_info,
            executors=data.get("executors", {})
        ) 