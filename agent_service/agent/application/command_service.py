"""Command service for executing commands and managing command history."""

import logging
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime, timezone
from fastapi import Depends

from ..domain.models import CommandResponse
from ..infrastructure.command_repository import CommandRepository
from ..infrastructure.executor_factory import ExecutorFactory

logger = logging.getLogger("agent.application.command_service")

class CommandService:
    """Service for executing commands and managing command history.
    
    This class follows the Single Responsibility Principle by focusing only on
    command execution and history management.
    """
    
    def __init__(
        self,
        command_repository: CommandRepository = Depends(),
        executor_factory: ExecutorFactory = Depends()
    ):
        """Initialize the command service.
        
        Args:
            command_repository: Repository for command history
            executor_factory: Factory for creating command executors
        """
        self.command_repository = command_repository
        self.executor_factory = executor_factory
    
    def get_command_history(self, limit: int = 10) -> List[CommandResponse]:
        """Get command execution history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List[CommandResponse]: Command execution history
        """
        return self.command_repository.get_history(limit)
    
    async def execute_command(
        self,
        command: str,
        executor_type: str = "auto",
        command_id: Optional[str] = None,
        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> CommandResponse:
        """Execute a command using the specified executor.
        
        Args:
            command: Command to execute
            executor_type: Type of executor to use
            command_id: Optional command ID
            progress_callback: Optional callback for progress updates
            
        Returns:
            CommandResponse: Command execution result
        """
        # Generate command ID if not provided
        if not command_id:
            command_id = str(uuid.uuid4())
        
        # Get appropriate executor
        executor = self.executor_factory.get_executor(executor_type)
        
        # Log command execution
        logger.info(f"Executing command with {executor.get_type()} executor: {command}")
        
        # Send initial progress update
        if progress_callback:
            await progress_callback({
                "command_id": command_id,
                "status": "starting",
                "progress": 0,
                "message": f"Starting command execution with {executor.get_type()} executor",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Execute command
        result = await executor.execute(command, command_id, progress_callback)
        
        # Store result in history
        self.command_repository.add(result)
        
        return result 