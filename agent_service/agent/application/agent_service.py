"""Agent service for managing agent information and executors."""

import logging
from typing import Dict, Any
from fastapi import Depends

from ..domain.models import ExecutorInfo, AgentInfo
from ..config import config
from ..infrastructure.executor_factory import ExecutorFactory

logger = logging.getLogger("agent.application.agent_service")

class AgentService:
    """Service for managing agent information and executors.
    
    This class follows the Single Responsibility Principle by focusing only on
    agent-related functionality.
    """
    
    def __init__(
        self,
        executor_factory: ExecutorFactory = Depends()
    ):
        """Initialize the agent service.
        
        Args:
            executor_factory: Factory for creating command executors
        """
        self.executor_factory = executor_factory
        self.version = "1.0.0"  # Should be moved to config or version file
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get agent information.
        
        Returns:
            Dict[str, Any]: Agent information
        """
        return {
            "version": self.version,
            "hostname": config.hostname,
            "executors": self.get_available_executors()
        }
    
    def get_available_executors(self) -> Dict[str, ExecutorInfo]:
        """Get information about available executors.
        
        Returns:
            Dict[str, ExecutorInfo]: Dictionary of executor information
        """
        return self.executor_factory.get_available_executors() 