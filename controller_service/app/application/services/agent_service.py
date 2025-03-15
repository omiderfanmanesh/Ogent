"""Agent service for the controller service."""

import logging
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...domain.models.agent import Agent
from ...domain.interfaces.agent_repository import AgentRepositoryInterface
from ..dtos.agent_dto import AgentDTO, AgentInfoDTO

logger = logging.getLogger("controller.agent_service")


class AgentService:
    """Service for managing agents."""
    
    def __init__(self, agent_repository: AgentRepositoryInterface):
        """Initialize the agent service.
        
        Args:
            agent_repository: Agent repository
        """
        self.agent_repository = agent_repository
    
    async def register_agent(self, sid: str, agent_id: Optional[str] = None, agent_info: Optional[Dict[str, Any]] = None) -> Agent:
        """Register an agent.
        
        Args:
            sid: Socket.IO session ID
            agent_id: Optional agent ID (generated if not provided)
            agent_info: Optional agent information
            
        Returns:
            Agent: The registered agent
        """
        # Generate agent ID if not provided
        if not agent_id:
            agent_id = f"agent-{uuid.uuid4()}"
        
        # Create agent
        agent = Agent(
            agent_id=agent_id,
            sid=sid,
            connected_at=datetime.now(),
            hostname=agent_info.get("hostname") if agent_info else None,
            platform=agent_info.get("platform") if agent_info else None,
            version=agent_info.get("version") if agent_info else None,
            python_version=agent_info.get("python_version") if agent_info else None,
            ssh_enabled=agent_info.get("ssh_enabled", False) if agent_info else False,
            ssh_target=agent_info.get("ssh_target") if agent_info else None,
            executors=agent_info.get("executors", {}) if agent_info else {}
        )
        
        # Add agent to repository
        await self.agent_repository.add_agent(agent)
        
        logger.info(f"Agent registered: {agent_id}")
        
        return agent
    
    async def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent.
        
        Args:
            agent_id: Agent ID
        """
        # Remove agent from repository
        await self.agent_repository.remove_agent(agent_id)
        
        logger.info(f"Agent unregistered: {agent_id}")
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Optional[Agent]: The agent, or None if not found
        """
        return await self.agent_repository.get_agent(agent_id)
    
    async def get_agent_by_sid(self, sid: str) -> Optional[Agent]:
        """Get an agent by Socket.IO session ID.
        
        Args:
            sid: Socket.IO session ID
            
        Returns:
            Optional[Agent]: The agent, or None if not found
        """
        return await self.agent_repository.get_agent_by_sid(sid)
    
    async def get_all_agents(self) -> List[Agent]:
        """Get all agents.
        
        Returns:
            List[Agent]: List of all agents
        """
        return await self.agent_repository.get_all_agents()
    
    async def update_agent(self, agent: Agent) -> None:
        """Update an agent.
        
        Args:
            agent: The agent to update
        """
        await self.agent_repository.update_agent(agent)
        
        logger.info(f"Agent updated: {agent.agent_id}")
    
    async def update_agent_info(self, agent_id: str, agent_info: Dict[str, Any]) -> Optional[Agent]:
        """Update agent information.
        
        Args:
            agent_id: Agent ID
            agent_info: Agent information
            
        Returns:
            Optional[Agent]: The updated agent, or None if not found
        """
        # Get agent
        agent = await self.agent_repository.get_agent(agent_id)
        if not agent:
            logger.warning(f"Agent not found: {agent_id}")
            return None
        
        # Update agent information
        agent.hostname = agent_info.get("hostname", agent.hostname)
        agent.platform = agent_info.get("platform", agent.platform)
        agent.version = agent_info.get("version", agent.version)
        agent.python_version = agent_info.get("python_version", agent.python_version)
        agent.ssh_enabled = agent_info.get("ssh_enabled", agent.ssh_enabled)
        agent.ssh_target = agent_info.get("ssh_target", agent.ssh_target)
        agent.executors = agent_info.get("executors", agent.executors)
        
        # Update agent in repository
        await self.agent_repository.update_agent(agent)
        
        logger.info(f"Agent information updated: {agent_id}")
        
        return agent 