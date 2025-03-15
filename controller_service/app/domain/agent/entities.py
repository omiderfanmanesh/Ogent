from datetime import datetime
from typing import Dict, Any, Optional, List
from ..agent.value_objects import AgentStatus, AgentCapability

class Agent:
    """
    Agent entity representing a connected agent in the system.
    """
    def __init__(
        self, 
        agent_id: str, 
        sid: str,
        username: str,
        capabilities: List[AgentCapability] = None,
        connection_info: Dict[str, Any] = None
    ):
        self.agent_id = agent_id
        self.sid = sid
        self.username = username
        self.capabilities = capabilities or []
        self.connection_info = connection_info or {}
        self.status = AgentStatus.CONNECTED
        self.connected_at = datetime.utcnow()
        self.last_heartbeat = datetime.utcnow()
    
    def update_status(self, status: AgentStatus) -> None:
        """Update the agent's status."""
        self.status = status
        if status == AgentStatus.CONNECTED:
            self.last_heartbeat = datetime.utcnow()
    
    def can_execute(self, command_type: str) -> bool:
        """Check if the agent can execute a specific command type."""
        return any(cap.command_type == command_type for cap in self.capabilities)
    
    def update_heartbeat(self) -> None:
        """Update the agent's last heartbeat time."""
        self.last_heartbeat = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the agent to a dictionary."""
        return {
            'agent_id': self.agent_id,
            'sid': self.sid,
            'username': self.username,
            'capabilities': [cap.to_dict() for cap in self.capabilities],
            'connection_info': self.connection_info,
            'status': self.status.value,
            'connected_at': self.connected_at.isoformat(),
            'last_heartbeat': self.last_heartbeat.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create an agent from a dictionary."""
        agent = cls(
            agent_id=data['agent_id'],
            sid=data['sid'],
            username=data['username'],
            connection_info=data.get('connection_info', {})
        )
        
        # Set capabilities
        agent.capabilities = [
            AgentCapability.from_dict(cap) 
            for cap in data.get('capabilities', [])
        ]
        
        # Set status
        agent.status = AgentStatus(data.get('status', AgentStatus.CONNECTED.value))
        
        # Set timestamps
        if 'connected_at' in data:
            agent.connected_at = datetime.fromisoformat(data['connected_at'])
        
        if 'last_heartbeat' in data:
            agent.last_heartbeat = datetime.fromisoformat(data['last_heartbeat'])
        
        return agent 