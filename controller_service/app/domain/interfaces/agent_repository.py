"""Agent repository interface for the controller service."""

import abc
from typing import Dict, Any, List, Optional
from ..models.agent import Agent


class AgentRepositoryInterface(abc.ABC):
    """Interface for agent repositories."""
    
    @abc.abstractmethod
    async def add_agent(self, agent: Agent) -> None:
        """Add an agent to the repository.
        
        Args:
            agent: The agent to add
        """
        pass
    
    @abc.abstractmethod
    async def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the repository.
        
        Args:
            agent_id: The ID of the agent to remove
        """
        pass
    
    @abc.abstractmethod
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to get
            
        Returns:
            Optional[Agent]: The agent, or None if not found
        """
        pass
    
    @abc.abstractmethod
    async def get_agent_by_sid(self, sid: str) -> Optional[Agent]:
        """Get an agent by Socket.IO session ID.
        
        Args:
            sid: The Socket.IO session ID
            
        Returns:
            Optional[Agent]: The agent, or None if not found
        """
        pass
    
    @abc.abstractmethod
    async def get_all_agents(self) -> List[Agent]:
        """Get all agents.
        
        Returns:
            List[Agent]: List of all agents
        """
        pass
    
    @abc.abstractmethod
    async def update_agent(self, agent: Agent) -> None:
        """Update an agent in the repository.
        
        Args:
            agent: The agent to update
        """
        pass 