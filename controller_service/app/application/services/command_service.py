"""Command service for the controller service."""

import logging
import uuid
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime

from ...domain.models.command import Command, CommandAIProcessing
from ...domain.interfaces.command_repository import CommandRepositoryInterface
from ...domain.interfaces.ai_service import AIServiceInterface
from ...domain.interfaces.socket_service import SocketServiceInterface
from ..dtos.command_dto import CommandRequestDTO, CommandResponseDTO

logger = logging.getLogger("controller.command_service")


class CommandService:
    """Service for managing commands."""
    
    def __init__(
        self,
        command_repository: CommandRepositoryInterface,
        ai_service: AIServiceInterface,
        socket_service: SocketServiceInterface
    ):
        """Initialize the command service.
        
        Args:
            command_repository: Command repository
            ai_service: AI service
            socket_service: Socket service
        """
        self.command_repository = command_repository
        self.ai_service = ai_service
        self.socket_service = socket_service
        self.command_callbacks: Dict[str, Callable[[Dict[str, Any]], Awaitable[None]]] = {}
    
    async def execute_command(
        self,
        command_request: CommandRequestDTO,
        callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None
    ) -> Command:
        """Execute a command.
        
        Args:
            command_request: Command request
            callback: Optional callback for command results
            
        Returns:
            Command: The created command
        """
        # Generate command ID
        command_id = str(uuid.uuid4())
        
        # Process command with AI if requested
        ai_processing = None
        if command_request.use_ai and self.ai_service.enabled:
            try:
                ai_processing = await self.ai_service.process_command(
                    command_request.command,
                    command_request.system,
                    command_request.context
                )
                
                # Use processed command if available
                command = ai_processing.processed_command
            except Exception as e:
                logger.error(f"Error processing command with AI: {str(e)}")
                command = command_request.command
        else:
            command = command_request.command
        
        # Create command
        command = Command(
            command=command,
            command_id=command_id,
            agent_id=command_request.agent_id,
            requester_id=command_request.requester_id,
            execution_target=command_request.execution_target,
            use_ai=command_request.use_ai,
            system=command_request.system,
            context=command_request.context,
            timestamp=datetime.now(),
            status="pending",
            ai_processing=ai_processing
        )
        
        # Add command to repository
        await self.command_repository.add_command(command)
        
        # Store callback if provided
        if callback:
            self.command_callbacks[command_id] = callback
        
        # Emit command to agent
        await self.socket_service.emit(
            "execute_command_event",
            {
                "command": command.command,
                "command_id": command.command_id,
                "requester_sid": command.requester_id,
                "execution_target": command.execution_target
            },
            room=command_request.agent_id
        )
        
        logger.info(f"Command executed: {command_id}")
        
        return command
    
    async def get_command(self, command_id: str) -> Optional[Command]:
        """Get a command by ID.
        
        Args:
            command_id: Command ID
            
        Returns:
            Optional[Command]: The command, or None if not found
        """
        return await self.command_repository.get_command(command_id)
    
    async def get_commands_by_agent(self, agent_id: str, limit: int = 10) -> List[Command]:
        """Get commands by agent ID.
        
        Args:
            agent_id: Agent ID
            limit: Maximum number of commands to return
            
        Returns:
            List[Command]: List of commands
        """
        return await self.command_repository.get_commands_by_agent(agent_id, limit)
    
    async def get_commands_by_requester(self, requester_id: str, limit: int = 10) -> List[Command]:
        """Get commands by requester ID.
        
        Args:
            requester_id: Requester ID
            limit: Maximum number of commands to return
            
        Returns:
            List[Command]: List of commands
        """
        return await self.command_repository.get_commands_by_requester(requester_id, limit)
    
    async def update_command_result(self, command_id: str, result: Dict[str, Any]) -> Optional[Command]:
        """Update command result.
        
        Args:
            command_id: Command ID
            result: Command result
            
        Returns:
            Optional[Command]: The updated command, or None if not found
        """
        # Get command
        command = await self.command_repository.get_command(command_id)
        if not command:
            logger.warning(f"Command not found: {command_id}")
            return None
        
        # Update command
        command.exit_code = result.get("exit_code")
        command.stdout = result.get("stdout")
        command.stderr = result.get("stderr")
        command.status = "success" if result.get("exit_code") == 0 else "error"
        command.execution_type = result.get("execution_type")
        command.target = result.get("target")
        
        # Update command in repository
        await self.command_repository.update_command(command)
        
        # Call callback if registered
        if command_id in self.command_callbacks:
            try:
                await self.command_callbacks[command_id](command.to_dict())
            except Exception as e:
                logger.error(f"Error calling command callback: {str(e)}")
            finally:
                # Remove callback
                del self.command_callbacks[command_id]
        
        logger.info(f"Command result updated: {command_id}")
        
        return command
    
    async def update_command_progress(self, command_id: str, progress: Dict[str, Any]) -> Optional[Command]:
        """Update command progress.
        
        Args:
            command_id: Command ID
            progress: Command progress
            
        Returns:
            Optional[Command]: The command, or None if not found
        """
        # Get command
        command = await self.command_repository.get_command(command_id)
        if not command:
            logger.warning(f"Command not found: {command_id}")
            return None
        
        # Update command status if provided
        if "status" in progress:
            command.status = progress["status"]
            
            # Update command in repository
            await self.command_repository.update_command(command)
        
        # Emit progress to requester if provided
        requester_sid = progress.get("requester_sid") or command.requester_id
        if requester_sid:
            await self.socket_service.emit(
                "command_progress",
                progress,
                room=requester_sid
            )
        
        return command
    
    async def analyze_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> Optional[CommandAIProcessing]:
        """Analyze a command with AI.
        
        Args:
            command: The command to analyze
            system: The system the command will be executed on
            context: The context in which the command will be executed
            
        Returns:
            Optional[CommandAIProcessing]: AI processing results, or None if AI is disabled
        """
        if not self.ai_service.enabled:
            logger.warning("AI service is disabled")
            return None
        
        try:
            return await self.ai_service.process_command(command, system, context)
        except Exception as e:
            logger.error(f"Error analyzing command with AI: {str(e)}")
            return None 