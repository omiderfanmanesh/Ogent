from typing import Dict, Any, Optional, List
import json
import logging

from ...domain.agent.entities import Agent
from ...application.agent_service import AgentRepository

class RedisAgentRepository(AgentRepository):
    """
    Redis implementation of the agent repository.
    """
    def __init__(self, redis_manager, logger: Optional[logging.Logger] = None):
        self.redis_manager = redis_manager
        self.logger = logger or logging.getLogger(__name__)
        self.key_prefix = "agent:"
    
    async def save(self, agent: Agent) -> None:
        """
        Save an agent to Redis.
        
        Args:
            agent: The agent to save
        """
        try:
            # Save by agent ID
            agent_key = f"{self.key_prefix}id:{agent.agent_id}"
            await self.redis_manager.set(agent_key, agent.to_dict())
            
            # Save by socket ID for quick lookup
            sid_key = f"{self.key_prefix}sid:{agent.sid}"
            await self.redis_manager.set(sid_key, agent.agent_id)
            
            self.logger.debug(f"Agent saved: {agent.agent_id}")
        except Exception as e:
            self.logger.error(f"Error saving agent: {str(e)}")
            raise
    
    async def find_by_id(self, agent_id: str) -> Optional[Agent]:
        """
        Find an agent by ID.
        
        Args:
            agent_id: The ID of the agent to find
            
        Returns:
            Optional[Agent]: The agent if found, None otherwise
        """
        try:
            agent_key = f"{self.key_prefix}id:{agent_id}"
            agent_data = await self.redis_manager.get(agent_key)
            
            if not agent_data:
                return None
            
            return Agent.from_dict(agent_data)
        except Exception as e:
            self.logger.error(f"Error finding agent by ID: {str(e)}")
            return None
    
    async def find_by_sid(self, sid: str) -> Optional[Agent]:
        """
        Find an agent by socket ID.
        
        Args:
            sid: The socket ID of the agent to find
            
        Returns:
            Optional[Agent]: The agent if found, None otherwise
        """
        try:
            # Get the agent ID from the socket ID
            sid_key = f"{self.key_prefix}sid:{sid}"
            agent_id = await self.redis_manager.get(sid_key)
            
            if not agent_id:
                return None
            
            # Get the agent by ID
            return await self.find_by_id(agent_id)
        except Exception as e:
            self.logger.error(f"Error finding agent by SID: {str(e)}")
            return None
    
    async def find_all(self) -> List[Agent]:
        """
        Find all agents.
        
        Returns:
            List[Agent]: List of all agents
        """
        try:
            # Get all agent keys
            pattern = f"{self.key_prefix}id:*"
            agent_keys = await self.redis_manager.keys(pattern)
            
            agents = []
            for key in agent_keys:
                agent_data = await self.redis_manager.get(key)
                if agent_data:
                    try:
                        agent = Agent.from_dict(agent_data)
                        agents.append(agent)
                    except Exception as e:
                        self.logger.error(f"Error deserializing agent data: {str(e)}")
            
            return agents
        except Exception as e:
            self.logger.error(f"Error finding all agents: {str(e)}")
            return []
    
    async def delete(self, agent_id: str) -> None:
        """
        Delete an agent from Redis.
        
        Args:
            agent_id: The ID of the agent to delete
        """
        try:
            # Get the agent first to get the socket ID
            agent = await self.find_by_id(agent_id)
            if not agent:
                return
            
            # Delete by agent ID
            agent_key = f"{self.key_prefix}id:{agent_id}"
            await self.redis_manager.delete(agent_key)
            
            # Delete by socket ID
            sid_key = f"{self.key_prefix}sid:{agent.sid}"
            await self.redis_manager.delete(sid_key)
            
            self.logger.debug(f"Agent deleted: {agent_id}")
        except Exception as e:
            self.logger.error(f"Error deleting agent: {str(e)}")
            raise 