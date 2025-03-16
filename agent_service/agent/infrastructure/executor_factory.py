"""Factory for creating command executors."""

import logging
from typing import Dict, Any, Type
from fastapi import Depends

from ..domain.models import ExecutorInfo
from ..executors.base_executor import CommandExecutor
from ..executors.local_executor import LocalExecutor
from ..executors.ssh_executor import SSHExecutor
from ..config import config

logger = logging.getLogger("agent.infrastructure.executor_factory")

class ExecutorFactory:
    """Factory for creating command executors.
    
    This class follows the Factory pattern to create and manage command executors.
    It also implements the Singleton pattern to ensure only one instance exists.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a new instance if one doesn't exist."""
        if cls._instance is None:
            cls._instance = super(ExecutorFactory, cls).__new__(cls)
            cls._instance.executors = {}
            cls._instance._initialize_executors()
        return cls._instance
    
    def __init__(self):
        """Initialize the executor factory."""
        # Initialize executors only if they don't exist
        if not hasattr(self, "executors"):
            self.executors: Dict[str, CommandExecutor] = {}
            self._initialize_executors()
    
    def _initialize_executors(self) -> None:
        """Initialize command executors."""
        # Initialize local executor
        local_executor = LocalExecutor()
        self.executors["local"] = local_executor
        logger.info("Local executor initialized")
        
        # Initialize SSH executor if enabled
        if config.ssh_enabled:
            try:
                ssh_executor = SSHExecutor(config.ssh_config)
                if ssh_executor.enabled:
                    self.executors["ssh"] = ssh_executor
                    logger.info("SSH executor initialized")
                    
                    # Test SSH connection
                    if ssh_executor.connect():
                        logger.info("SSH connection successful")
                        ssh_executor.disconnect()
                    else:
                        logger.warning("SSH connection failed, but executor is still available")
                else:
                    logger.warning("SSH executor is disabled due to invalid configuration")
            except Exception as e:
                logger.error(f"Failed to initialize SSH executor: {str(e)}")
    
    def get_executor(self, executor_type: str = "auto") -> CommandExecutor:
        """Get a command executor by type.
        
        Args:
            executor_type: Type of executor to get
            
        Returns:
            CommandExecutor: Command executor
            
        Raises:
            ValueError: If executor type is not found
        """
        # If auto, select the best available executor
        if executor_type == "auto":
            # Prefer SSH if available
            if "ssh" in self.executors and self.executors["ssh"].is_available():
                return self.executors["ssh"]
            # Fall back to local
            elif "local" in self.executors and self.executors["local"].is_available():
                return self.executors["local"]
            else:
                raise ValueError("No available executors found")
        
        # Get specific executor
        if executor_type in self.executors:
            executor = self.executors[executor_type]
            if executor.is_available():
                return executor
            else:
                raise ValueError(f"Executor {executor_type} is not available")
        else:
            raise ValueError(f"Executor type not found: {executor_type}")
    
    def get_available_executors(self) -> Dict[str, ExecutorInfo]:
        """Get information about available executors.
        
        Returns:
            Dict[str, ExecutorInfo]: Dictionary of executor information
        """
        result = {}
        for name, executor in self.executors.items():
            if executor.is_available():
                result[name] = ExecutorInfo(
                    type=name,
                    available=True,
                    target=executor.get_target_info()
                )
        return result 