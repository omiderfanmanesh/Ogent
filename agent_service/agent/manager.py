"""Agent manager for handling command execution."""

import logging
import uuid
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable, List
from datetime import datetime, UTC

from .executors import CommandExecutor, LocalExecutor, SSHExecutor
from .config import config

logger = logging.getLogger("agent.manager")

class AgentManager:
    """Manager for handling command execution and managing executors."""
    
    def __init__(self):
        """Initialize the agent manager."""
        self.executors: Dict[str, CommandExecutor] = {}
        self._initialize_executors()
        
        # Command history
        self.command_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
    
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
    
    def get_available_executors(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available executors.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of executor information
        """
        result = {}
        for name, executor in self.executors.items():
            if executor.is_available():
                result[name] = {
                    "type": name,
                    "available": True,
                    "target": executor.get_target_info()
                }
        return result
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get command execution history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List[Dict[str, Any]]: List of command execution results
        """
        return self.command_history[-limit:] if limit > 0 else self.command_history
    
    def _add_to_history(self, result: Dict[str, Any]) -> None:
        """Add a command execution result to history.
        
        Args:
            result: Command execution result
        """
        self.command_history.append(result)
        
        # Trim history if it exceeds max size
        if len(self.command_history) > self.max_history_size:
            self.command_history = self.command_history[-self.max_history_size:]
    
    async def execute_command(self, 
                             command: str, 
                             executor_type: str = "auto",
                             command_id: Optional[str] = None,
                             progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command using the specified executor.
        
        Args:
            command: The command to execute
            executor_type: Type of executor to use (local, ssh, auto)
            command_id: Optional ID for the command
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Command execution result
        """
        # Generate a command ID
        if not command_id:
            command_id = str(uuid.uuid4())
        
        # Determine executor type if auto
        if executor_type == "auto":
            # Use SSH if available, otherwise use local
            if "ssh" in self.executors and self.executors["ssh"].is_available():
                executor_type = "ssh"
            else:
                executor_type = "local"
        
        # Get the executor
        executor = self.executors.get(executor_type)
        
        if not executor:
            logger.error(f"Executor type '{executor_type}' not found")
            result = {
                "command": command,
                "command_id": command_id,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Executor type '{executor_type}' not found",
                "timestamp": datetime.now(UTC).isoformat(),
                "execution_type": executor_type,
                "target": "unknown",
                "status": "error"
            }
            self._add_to_history(result)
            return result
        
        if not executor.is_available():
            logger.error(f"Executor '{executor_type}' is not available")
            result = {
                "command": command,
                "command_id": command_id,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Executor '{executor_type}' is not available",
                "timestamp": datetime.now(UTC).isoformat(),
                "execution_type": executor_type,
                "target": "unknown",
                "status": "error"
            }
            self._add_to_history(result)
            return result
        
        try:
            # Execute the command
            logger.info(f"Executing command with {executor_type} executor: {command}")
            result = await executor.execute(command, command_id, progress_callback)
            
            # Add status based on exit code
            result["status"] = "success" if result["exit_code"] == 0 else "error"
            
            # Add to history
            self._add_to_history(result)
            
            return result
        
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            result = {
                "command": command,
                "command_id": command_id,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}",
                "timestamp": datetime.now(UTC).isoformat(),
                "execution_type": executor_type,
                "target": "unknown",
                "status": "error"
            }
            self._add_to_history(result)
            return result
    
    def cleanup(self) -> None:
        """Clean up resources used by executors."""
        for name, executor in self.executors.items():
            if name == "ssh":
                # Call disconnect for SSH executor
                ssh_executor = executor
                ssh_executor.disconnect()
                logger.info("SSH executor disconnected")

# Create a singleton instance
agent_manager = AgentManager() 