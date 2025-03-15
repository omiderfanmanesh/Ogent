from typing import Dict, Any, Optional, List
import json
import logging

from ...domain.command.entities import Command
from ...application.command_service import CommandRepository

class RedisCommandRepository(CommandRepository):
    """
    Redis implementation of the command repository.
    """
    def __init__(self, redis_manager, logger: Optional[logging.Logger] = None):
        self.redis_manager = redis_manager
        self.logger = logger or logging.getLogger(__name__)
        self.key_prefix = "command:"
        self.index_prefix = "index:command:"
    
    async def save(self, command: Command) -> None:
        """
        Save a command to Redis.
        
        Args:
            command: The command to save
        """
        try:
            # Save the command
            command_key = f"{self.key_prefix}{command.command_id}"
            await self.redis_manager.set(command_key, command.to_dict())
            
            # Add to agent index
            agent_index_key = f"{self.index_prefix}agent:{command.agent_id}"
            await self.redis_manager.sadd(agent_index_key, command.command_id)
            
            # Add to requester index
            requester_index_key = f"{self.index_prefix}requester:{command.requester_id}"
            await self.redis_manager.sadd(requester_index_key, command.command_id)
            
            # Add to status index
            status_index_key = f"{self.index_prefix}status:{command.status.value}"
            await self.redis_manager.sadd(status_index_key, command.command_id)
            
            self.logger.debug(f"Command saved: {command.command_id}")
        except Exception as e:
            self.logger.error(f"Error saving command: {str(e)}")
            raise
    
    async def find_by_id(self, command_id: str) -> Optional[Command]:
        """
        Find a command by ID.
        
        Args:
            command_id: The ID of the command to find
            
        Returns:
            Optional[Command]: The command if found, None otherwise
        """
        try:
            command_key = f"{self.key_prefix}{command_id}"
            command_data = await self.redis_manager.get(command_key)
            
            if not command_data:
                return None
            
            return Command.from_dict(command_data)
        except Exception as e:
            self.logger.error(f"Error finding command by ID: {str(e)}")
            return None
    
    async def find_by_agent_id(self, agent_id: str) -> List[Command]:
        """
        Find commands by agent ID.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            List[Command]: List of commands for the agent
        """
        try:
            # Get command IDs from agent index
            agent_index_key = f"{self.index_prefix}agent:{agent_id}"
            command_ids = await self.redis_manager.smembers(agent_index_key)
            
            commands = []
            for command_id in command_ids:
                command = await self.find_by_id(command_id)
                if command:
                    commands.append(command)
            
            return commands
        except Exception as e:
            self.logger.error(f"Error finding commands by agent ID: {str(e)}")
            return []
    
    async def find_by_requester_id(self, requester_id: str) -> List[Command]:
        """
        Find commands by requester ID.
        
        Args:
            requester_id: The ID of the requester
            
        Returns:
            List[Command]: List of commands for the requester
        """
        try:
            # Get command IDs from requester index
            requester_index_key = f"{self.index_prefix}requester:{requester_id}"
            command_ids = await self.redis_manager.smembers(requester_index_key)
            
            commands = []
            for command_id in command_ids:
                command = await self.find_by_id(command_id)
                if command:
                    commands.append(command)
            
            return commands
        except Exception as e:
            self.logger.error(f"Error finding commands by requester ID: {str(e)}")
            return []
    
    async def find_by_status(self, status: str) -> List[Command]:
        """
        Find commands by status.
        
        Args:
            status: The status to filter by
            
        Returns:
            List[Command]: List of commands with the given status
        """
        try:
            # Get command IDs from status index
            status_index_key = f"{self.index_prefix}status:{status}"
            command_ids = await self.redis_manager.smembers(status_index_key)
            
            commands = []
            for command_id in command_ids:
                command = await self.find_by_id(command_id)
                if command:
                    commands.append(command)
            
            return commands
        except Exception as e:
            self.logger.error(f"Error finding commands by status: {str(e)}")
            return []
    
    async def find_all(self) -> List[Command]:
        """
        Find all commands.
        
        Returns:
            List[Command]: List of all commands
        """
        try:
            # Get all command keys
            pattern = f"{self.key_prefix}*"
            command_keys = await self.redis_manager.keys(pattern)
            
            commands = []
            for key in command_keys:
                command_data = await self.redis_manager.get(key)
                if command_data:
                    try:
                        command = Command.from_dict(command_data)
                        commands.append(command)
                    except Exception as e:
                        self.logger.error(f"Error deserializing command data: {str(e)}")
            
            return commands
        except Exception as e:
            self.logger.error(f"Error finding all commands: {str(e)}")
            return [] 