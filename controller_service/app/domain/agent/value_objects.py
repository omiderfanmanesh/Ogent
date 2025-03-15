from enum import Enum
from typing import Dict, Any, Optional

class AgentStatus(Enum):
    """
    Enumeration of possible agent statuses.
    """
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    BUSY = "busy"
    IDLE = "idle"

class AgentCapability:
    """
    Value object representing a capability of an agent.
    """
    def __init__(
        self, 
        command_type: str, 
        description: str,
        parameters: Optional[Dict[str, Any]] = None
    ):
        self.command_type = command_type
        self.description = description
        self.parameters = parameters or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the capability to a dictionary."""
        return {
            'command_type': self.command_type,
            'description': self.description,
            'parameters': self.parameters
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCapability':
        """Create a capability from a dictionary."""
        return cls(
            command_type=data['command_type'],
            description=data.get('description', ''),
            parameters=data.get('parameters', {})
        )

class ConnectionInfo:
    """
    Value object representing connection information for an agent.
    """
    def __init__(
        self,
        host: str,
        port: int,
        protocol: str = "websocket",
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the connection info to a dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConnectionInfo':
        """Create connection info from a dictionary."""
        return cls(
            host=data['host'],
            port=data['port'],
            protocol=data.get('protocol', 'websocket'),
            metadata=data.get('metadata', {})
        ) 