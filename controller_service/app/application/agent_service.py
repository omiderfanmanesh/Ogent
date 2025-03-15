from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..domain.agent.entities import Agent
from ..domain.agent.value_objects import AgentStatus, AgentCapability
from ..domain.agent.services import AgentRegistrationService, AgentManagementService

# This will be defined in the infrastructure layer
class AgentRepository:
    """Interface for agent repository."""
    async def save(self, agent: Agent) -> None:
        """Save an agent to the repository."""
        pass
    
    async def find_by_id(self, agent_id: str) -> Optional[Agent]:
        """Find an agent by ID."""
        pass
    
    async def find_by_sid(self, sid: str) -> Optional[Agent]:
        """Find an agent by socket ID."""
        pass
    
    async def find_all(self) -> List[Agent]:
        """Find all agents."""
        pass
    
    async def delete(self, agent_id: str) -> None:
        """Delete an agent from the repository."""
        pass

class AgentApplicationService:
    """
    Application service for agent management.
    """
    def __init__(
        self,
        agent_repository: AgentRepository,
        agent_registration_service: AgentRegistrationService,
        agent_management_service: AgentManagementService,
        logger: Optional[logging.Logger] = None
    ):
        self.agent_repository = agent_repository
        self.agent_registration_service = agent_registration_service
        self.agent_management_service = agent_management_service
        self.logger = logger or logging.getLogger(__name__)
    
    async def register_agent(
        self,
        agent_id: str,
        sid: str,
        username: str,
        capabilities: List[Dict[str, Any]] = None,
        connection_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Register a new agent in the system.
        
        Args:
            agent_id: The unique identifier for the agent
            sid: The socket ID for the agent
            username: The username associated with the agent
            capabilities: List of capabilities the agent supports
            connection_info: Connection information for the agent
            
        Returns:
            Dict[str, Any]: Response with registration status
        """
        try:
            # Check if agent already exists
            existing_agent = await self.agent_repository.find_by_id(agent_id)
            if existing_agent:
                # Update the existing agent with new connection info
                existing_agent.sid = sid
                existing_agent.update_status(AgentStatus.CONNECTED)
                existing_agent.update_heartbeat()
                
                # Save the updated agent
                await self.agent_repository.save(existing_agent)
                
                self.logger.info(f"Agent reconnected: {agent_id} (SID: {sid})")
                
                return {
                    'status': 'success',
                    'message': 'Agent reconnected successfully',
                    'agent_id': agent_id
                }
            
            # Register a new agent
            agent = self.agent_registration_service.register_agent(
                agent_id=agent_id,
                sid=sid,
                username=username,
                capabilities=capabilities,
                connection_info=connection_info
            )
            
            # Save the agent
            await self.agent_repository.save(agent)
            
            self.logger.info(f"Agent registered: {agent_id} (SID: {sid})")
            
            return {
                'status': 'success',
                'message': 'Agent registered successfully',
                'agent_id': agent_id
            }
        
        except Exception as e:
            self.logger.error(f"Error registering agent: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error registering agent: {str(e)}'
            }
    
    async def disconnect_agent(self, sid: str) -> Dict[str, Any]:
        """
        Handle agent disconnection.
        
        Args:
            sid: The socket ID of the disconnecting agent
            
        Returns:
            Dict[str, Any]: Response with disconnection status
        """
        try:
            # Find the agent by socket ID
            agent = await self.agent_repository.find_by_sid(sid)
            if not agent:
                self.logger.warning(f"Disconnect request for unknown agent with SID: {sid}")
                return {
                    'status': 'warning',
                    'message': f'No agent found with SID: {sid}'
                }
            
            # Update agent status
            agent.update_status(AgentStatus.DISCONNECTED)
            
            # Save the updated agent
            await self.agent_repository.save(agent)
            
            self.logger.info(f"Agent disconnected: {agent.agent_id} (SID: {sid})")
            
            return {
                'status': 'success',
                'message': 'Agent disconnected successfully',
                'agent_id': agent.agent_id
            }
        
        except Exception as e:
            self.logger.error(f"Error disconnecting agent: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error disconnecting agent: {str(e)}'
            }
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific agent.
        
        Args:
            agent_id: The ID of the agent to get
            
        Returns:
            Optional[Dict[str, Any]]: Agent information or None if not found
        """
        try:
            agent = await self.agent_repository.find_by_id(agent_id)
            if not agent:
                return None
            
            return agent.to_dict()
        
        except Exception as e:
            self.logger.error(f"Error getting agent: {str(e)}")
            return None
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all connected agents.
        
        Returns:
            List[Dict[str, Any]]: List of agent information
        """
        try:
            agents = await self.agent_repository.find_all()
            return [agent.to_dict() for agent in agents]
        
        except Exception as e:
            self.logger.error(f"Error listing agents: {str(e)}")
            return []
    
    async def update_agent_heartbeat(self, sid: str) -> Dict[str, Any]:
        """
        Update the heartbeat timestamp of an agent.
        
        Args:
            sid: The socket ID of the agent
            
        Returns:
            Dict[str, Any]: Response with update status
        """
        try:
            # Find the agent by socket ID
            agent = await self.agent_repository.find_by_sid(sid)
            if not agent:
                self.logger.warning(f"Heartbeat update request for unknown agent with SID: {sid}")
                return {
                    'status': 'warning',
                    'message': f'No agent found with SID: {sid}'
                }
            
            # Update agent heartbeat
            self.agent_management_service.update_agent_heartbeat(agent)
            
            # Save the updated agent
            await self.agent_repository.save(agent)
            
            return {
                'status': 'success',
                'message': 'Agent heartbeat updated successfully',
                'agent_id': agent.agent_id
            }
        
        except Exception as e:
            self.logger.error(f"Error updating agent heartbeat: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error updating agent heartbeat: {str(e)}'
            } 