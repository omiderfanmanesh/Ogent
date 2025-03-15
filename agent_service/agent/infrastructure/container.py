"""Dependency injection container for the agent service."""

import logging
from typing import Dict, Any, Optional

from agent.domain.interfaces.command_executor import CommandExecutorInterface
from agent.infrastructure.executors.local_executor import LocalExecutor
from agent.infrastructure.executors.ssh_executor import SSHExecutor
from agent.infrastructure.config.config import config
from agent.application.services.agent_manager import AgentManager
from agent.application.services.client_service import ClientService

logger = logging.getLogger("agent.container")


class Container:
    """Dependency injection container for the agent service."""
    
    def __init__(self):
        """Initialize the container."""
        self._instances: Dict[str, Any] = {}
        self._initialize()
    
    def _initialize(self):
        """Initialize the container with default instances."""
        # Register executors
        self.register_executor("local", LocalExecutor())
        
        # Register SSH executor if enabled
        if config.ssh_enabled:
            try:
                ssh_executor = SSHExecutor()
                self.register_executor("ssh", ssh_executor)
                logger.info("SSH executor registered")
            except Exception as e:
                logger.error(f"Error initializing SSH executor: {str(e)}")
                logger.warning("SSH executor will not be available")
        
        # Register agent manager
        self._instances["agent_manager"] = AgentManager(self.get_executors())
        
        # Register client service
        self._instances["client_service"] = ClientService()
    
    def register_executor(self, name: str, executor: CommandExecutorInterface):
        """Register an executor.
        
        Args:
            name: Executor name
            executor: Executor instance
        """
        if "executors" not in self._instances:
            self._instances["executors"] = {}
        
        self._instances["executors"][name] = executor
        logger.info(f"Registered executor: {name}")
    
    def get_executors(self) -> Dict[str, CommandExecutorInterface]:
        """Get all registered executors.
        
        Returns:
            Dict[str, CommandExecutorInterface]: Dictionary of executors
        """
        return self._instances.get("executors", {})
    
    def get_executor(self, name: str) -> Optional[CommandExecutorInterface]:
        """Get an executor by name.
        
        Args:
            name: Executor name
            
        Returns:
            Optional[CommandExecutorInterface]: Executor instance, or None if not found
        """
        executors = self.get_executors()
        return executors.get(name)
    
    def get_agent_manager(self) -> AgentManager:
        """Get the agent manager.
        
        Returns:
            AgentManager: Agent manager instance
        """
        return self._instances["agent_manager"]
    
    def get_client_service(self) -> ClientService:
        """Get the client service.
        
        Returns:
            ClientService: Client service instance
        """
        return self._instances["client_service"]
    
    def cleanup(self):
        """Clean up resources used by the container."""
        # Clean up executors
        for executor in self.get_executors().values():
            executor.cleanup()
        
        # Clean up agent manager
        if "agent_manager" in self._instances:
            self._instances["agent_manager"].cleanup()
        
        # Clean up client service
        if "client_service" in self._instances:
            self._instances["client_service"].cleanup()


# Create a singleton instance
container = Container() 