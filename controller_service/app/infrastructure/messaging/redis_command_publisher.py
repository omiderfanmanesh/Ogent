import json
import logging
from typing import Dict, Any, Optional

from app.domain.interfaces.command_publisher import CommandPublisher
from app.infrastructure.messaging.redis_manager import RedisManager

class RedisCommandPublisher(CommandPublisher):
    """
    Redis implementation of the command publisher interface.
    """
    
    def __init__(
        self,
        redis_manager: RedisManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Redis command publisher.
        
        Args:
            redis_manager: The Redis manager
            logger: Optional logger
        """
        self.redis_manager = redis_manager
        self.logger = logger or logging.getLogger(__name__)
        self.command_channel = "commands"
        self.result_channel = "command_results"
    
    async def publish_command(
        self,
        agent_id: str,
        command_id: str,
        command_data: Dict[str, Any]
    ) -> bool:
        """
        Publish a command to an agent via Redis.
        
        Args:
            agent_id: The ID of the agent to send the command to
            command_id: The ID of the command
            command_data: The command data
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            # Prepare the message
            message = {
                "agent_id": agent_id,
                "command_id": command_id,
                "data": command_data
            }
            
            # Store the command in Redis
            command_key = f"command:{command_id}"
            await self.redis_manager.set(command_key, message)
            
            # Publish the command to the commands channel
            success = await self.redis_manager.publish(self.command_channel, message)
            
            if success:
                self.logger.info(f"Published command {command_id} to agent {agent_id}")
            else:
                self.logger.error(f"Failed to publish command {command_id} to agent {agent_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"Error publishing command {command_id} to agent {agent_id}: {str(e)}")
            return False
    
    async def publish_command_result(
        self,
        requester_id: str,
        command_id: str,
        result: Dict[str, Any],
        status: str,
        error: Optional[str] = None
    ) -> bool:
        """
        Publish a command result to a requester via Redis.
        
        Args:
            requester_id: The ID of the requester
            command_id: The ID of the command
            result: The command result
            status: The status of the command (success, error, etc.)
            error: Optional error message
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            # Prepare the message
            message = {
                "requester_id": requester_id,
                "command_id": command_id,
                "result": result,
                "status": status
            }
            
            # Add error if provided
            if error:
                message["error"] = error
            
            # Store the result in Redis
            result_key = f"result:{command_id}"
            await self.redis_manager.set(result_key, message)
            
            # Publish the result to the command_results channel
            success = await self.redis_manager.publish(self.result_channel, message)
            
            if success:
                self.logger.info(f"Published result for command {command_id} to requester {requester_id}")
            else:
                self.logger.error(f"Failed to publish result for command {command_id} to requester {requester_id}")
            
            return success
        except Exception as e:
            self.logger.error(f"Error publishing result for command {command_id} to requester {requester_id}: {str(e)}")
            return False 