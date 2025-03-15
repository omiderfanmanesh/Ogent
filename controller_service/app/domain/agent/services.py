from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from ..agent.entities import Agent
from ..agent.value_objects import AgentStatus, AgentCapability, ConnectionInfo

class AgentRegistrationService:
    """
    Domain service for agent registration.
    """
    def register_agent(
        self,
        agent_id: str,
        sid: str,
        username: str,
        capabilities: List[Dict[str, Any]] = None,
        connection_info: Dict[str, Any] = None
    ) -> Agent:
        """
        Register a new agent in the system.
        
        Args:
            agent_id: The unique identifier for the agent
            sid: The socket ID for the agent
            username: The username associated with the agent
            capabilities: List of capabilities the agent supports
            connection_info: Connection information for the agent
            
        Returns:
            Agent: The registered agent entity
        """
        # Convert capabilities dictionaries to value objects
        agent_capabilities = []
        if capabilities:
            for cap in capabilities:
                agent_capabilities.append(AgentCapability(
                    command_type=cap.get('command_type', 'unknown'),
                    description=cap.get('description', ''),
                    parameters=cap.get('parameters', {})
                ))
        
        # Create the agent entity
        agent = Agent(
            agent_id=agent_id,
            sid=sid,
            username=username,
            capabilities=agent_capabilities,
            connection_info=connection_info or {}
        )
        
        return agent

class AgentManagementService:
    """
    Domain service for agent management.
    """
    def update_agent_status(self, agent: Agent, status: str) -> Agent:
        """
        Update the status of an agent.
        
        Args:
            agent: The agent to update
            status: The new status
            
        Returns:
            Agent: The updated agent
        """
        try:
            agent_status = AgentStatus(status)
            agent.update_status(agent_status)
        except ValueError:
            # Invalid status, keep the current one
            pass
        
        return agent
    
    def update_agent_heartbeat(self, agent: Agent) -> Agent:
        """
        Update the heartbeat timestamp of an agent.
        
        Args:
            agent: The agent to update
            
        Returns:
            Agent: The updated agent
        """
        agent.update_heartbeat()
        return agent
    
    def check_agent_timeout(self, agent: Agent, timeout_seconds: int = 60) -> bool:
        """
        Check if an agent has timed out based on its last heartbeat.
        
        Args:
            agent: The agent to check
            timeout_seconds: The number of seconds after which an agent is considered timed out
            
        Returns:
            bool: True if the agent has timed out, False otherwise
        """
        now = datetime.utcnow()
        time_diff = (now - agent.last_heartbeat).total_seconds()
        return time_diff > timeout_seconds 