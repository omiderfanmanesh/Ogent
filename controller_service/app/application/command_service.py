from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import uuid

from ..domain.command.entities import Command
from ..domain.command.value_objects import CommandStatus, CommandResult, ExecutionTarget, CommandValidationResult
from ..domain.command.services import CommandValidationService, CommandExecutionService

# This will be defined in the infrastructure layer
class CommandRepository:
    """Interface for command repository."""
    async def save(self, command: Command) -> None:
        """Save a command to the repository."""
        pass
    
    async def find_by_id(self, command_id: str) -> Optional[Command]:
        """Find a command by ID."""
        pass
    
    async def find_by_agent_id(self, agent_id: str) -> List[Command]:
        """Find commands by agent ID."""
        pass
    
    async def find_all(self) -> List[Command]:
        """Find all commands."""
        pass

# This will be defined in the infrastructure layer
class CommandPublisher:
    """Interface for command publisher."""
    async def publish_command(self, agent_sid: str, command: Command) -> bool:
        """Publish a command to an agent."""
        pass
    
    async def publish_command_result(self, requester_sid: str, command: Command) -> bool:
        """Publish a command result to a requester."""
        pass

class CommandApplicationService:
    """
    Application service for command management.
    """
    def __init__(
        self,
        command_repository: CommandRepository,
        command_publisher: CommandPublisher,
        command_validation_service: CommandValidationService,
        command_execution_service: CommandExecutionService,
        logger: Optional[logging.Logger] = None
    ):
        self.command_repository = command_repository
        self.command_publisher = command_publisher
        self.command_validation_service = command_validation_service
        self.command_execution_service = command_execution_service
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute_command(
        self,
        command_text: str,
        agent_id: str,
        requester_id: str,
        agent_sid: str,
        execution_target: str = "auto",
        execution_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a command on an agent.
        
        Args:
            command_text: The command text to execute
            agent_id: The ID of the agent to execute the command on
            requester_id: The ID of the user requesting the command execution
            agent_sid: The socket ID of the agent
            execution_target: The execution target (auto, local, ssh)
            execution_context: Additional context for command execution
            
        Returns:
            Dict[str, Any]: Response with execution status
        """
        try:
            # Validate the command
            validation_result = self.command_validation_service.validate_command(
                command_text,
                context=execution_context
            )
            
            if not validation_result.is_valid:
                self.logger.warning(f"Command validation failed: {validation_result.error_message}")
                return {
                    'status': 'error',
                    'message': validation_result.error_message,
                    'warnings': validation_result.warnings
                }
            
            # Create a command entity
            command_id = Command.generate_id()
            command = Command(
                command_id=command_id,
                command_text=command_text,
                agent_id=agent_id,
                requester_id=requester_id,
                execution_target=ExecutionTarget(execution_target),
                execution_context=execution_context or {}
            )
            
            # Prepare the command for execution
            command = self.command_execution_service.prepare_command_for_execution(
                command,
                agent_capabilities=[]  # In a real implementation, get agent capabilities
            )
            
            # Save the command
            await self.command_repository.save(command)
            
            # Publish the command to the agent
            success = await self.command_publisher.publish_command(agent_sid, command)
            
            if not success:
                command.fail("Failed to publish command to agent")
                await self.command_repository.save(command)
                
                self.logger.error(f"Failed to publish command to agent: {agent_id}")
                return {
                    'status': 'error',
                    'message': 'Failed to publish command to agent',
                    'command_id': command_id
                }
            
            self.logger.info(f"Command sent to agent: {agent_id}, Command ID: {command_id}")
            
            return {
                'status': 'pending',
                'message': 'Command sent to agent for execution',
                'command_id': command_id,
                'warnings': validation_result.warnings
            }
        
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error executing command: {str(e)}'
            }
    
    async def update_command_progress(
        self,
        command_id: str,
        progress: int,
        message: str,
        stdout: str = "",
        stderr: str = ""
    ) -> Dict[str, Any]:
        """
        Update the progress of a command.
        
        Args:
            command_id: The ID of the command
            progress: The progress percentage (0-100)
            message: A message describing the progress
            stdout: Standard output from the command
            stderr: Standard error from the command
            
        Returns:
            Dict[str, Any]: Response with update status
        """
        try:
            # Find the command
            command = await self.command_repository.find_by_id(command_id)
            if not command:
                self.logger.warning(f"Progress update for unknown command: {command_id}")
                return {
                    'status': 'error',
                    'message': f'Command not found: {command_id}'
                }
            
            # Add progress update
            command.add_progress_update(progress, message, stdout, stderr)
            
            # Save the updated command
            await self.command_repository.save(command)
            
            self.logger.info(f"Command progress updated: {command_id}, Progress: {progress}%")
            
            return {
                'status': 'success',
                'message': 'Command progress updated',
                'command_id': command_id
            }
        
        except Exception as e:
            self.logger.error(f"Error updating command progress: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error updating command progress: {str(e)}'
            }
    
    async def complete_command(
        self,
        command_id: str,
        stdout: str,
        stderr: str,
        exit_code: int,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a command with its result.
        
        Args:
            command_id: The ID of the command
            stdout: Standard output from the command
            stderr: Standard error from the command
            exit_code: Exit code of the command
            execution_time: Time taken to execute the command
            metadata: Additional metadata about the execution
            
        Returns:
            Dict[str, Any]: Response with completion status
        """
        try:
            # Find the command
            command = await self.command_repository.find_by_id(command_id)
            if not command:
                self.logger.warning(f"Completion request for unknown command: {command_id}")
                return {
                    'status': 'error',
                    'message': f'Command not found: {command_id}'
                }
            
            # Create a result
            result = CommandResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=exit_code,
                execution_time=execution_time,
                metadata=metadata or {}
            )
            
            # Complete the command
            command.complete(result)
            
            # Save the updated command
            await self.command_repository.save(command)
            
            self.logger.info(f"Command completed: {command_id}, Exit code: {exit_code}")
            
            # Publish the result to the requester
            # In a real implementation, get the requester's SID
            # await self.command_publisher.publish_command_result(requester_sid, command)
            
            return {
                'status': 'success',
                'message': 'Command completed',
                'command_id': command_id
            }
        
        except Exception as e:
            self.logger.error(f"Error completing command: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error completing command: {str(e)}'
            }
    
    async def get_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific command.
        
        Args:
            command_id: The ID of the command to get
            
        Returns:
            Optional[Dict[str, Any]]: Command information or None if not found
        """
        try:
            command = await self.command_repository.find_by_id(command_id)
            if not command:
                return None
            
            return command.to_dict()
        
        except Exception as e:
            self.logger.error(f"Error getting command: {str(e)}")
            return None
    
    async def list_commands(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List commands, optionally filtered by agent ID.
        
        Args:
            agent_id: Optional agent ID to filter by
            
        Returns:
            List[Dict[str, Any]]: List of command information
        """
        try:
            if agent_id:
                commands = await self.command_repository.find_by_agent_id(agent_id)
            else:
                commands = await self.command_repository.find_all()
            
            return [command.to_dict() for command in commands]
        
        except Exception as e:
            self.logger.error(f"Error listing commands: {str(e)}")
            return [] 