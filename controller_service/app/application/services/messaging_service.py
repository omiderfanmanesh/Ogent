"""Messaging service for the controller service."""

import logging
import json
from typing import Dict, Any, Optional, List, Callable

from ...domain.interfaces.messaging_service import MessagingServiceInterface

logger = logging.getLogger("controller.messaging_service")


class MessagingService:
    """Service for messaging operations."""
    
    def __init__(self, messaging_service_interface: Optional[MessagingServiceInterface] = None):
        """Initialize the messaging service.
        
        Args:
            messaging_service_interface: Messaging service interface implementation
        """
        self.messaging_service = messaging_service_interface
        self.enabled = self.messaging_service is not None
        self.handlers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
    
    async def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish a message to a channel.
        
        Args:
            channel: Channel name
            message: Message data
            
        Returns:
            bool: True if published, False otherwise
        """
        if not self.enabled or not self.messaging_service:
            logger.warning(f"Messaging service is disabled, cannot publish to {channel}")
            return False
        
        try:
            message_str = json.dumps(message)
            await self.messaging_service.publish(channel, message_str)
            logger.debug(f"Published message to {channel}")
            return True
        except Exception as e:
            logger.error(f"Error publishing to {channel}: {str(e)}")
            return False
    
    async def subscribe(self, channel: str) -> bool:
        """Subscribe to a channel.
        
        Args:
            channel: Channel name
            
        Returns:
            bool: True if subscribed, False otherwise
        """
        if not self.enabled or not self.messaging_service:
            logger.warning(f"Messaging service is disabled, cannot subscribe to {channel}")
            return False
        
        try:
            await self.messaging_service.subscribe(channel, self._message_handler)
            logger.info(f"Subscribed to channel: {channel}")
            return True
        except Exception as e:
            logger.error(f"Error subscribing to {channel}: {str(e)}")
            return False
    
    async def unsubscribe(self, channel: str) -> bool:
        """Unsubscribe from a channel.
        
        Args:
            channel: Channel name
            
        Returns:
            bool: True if unsubscribed, False otherwise
        """
        if not self.enabled or not self.messaging_service:
            logger.warning(f"Messaging service is disabled, cannot unsubscribe from {channel}")
            return False
        
        try:
            await self.messaging_service.unsubscribe(channel)
            logger.info(f"Unsubscribed from channel: {channel}")
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing from {channel}: {str(e)}")
            return False
    
    async def register_handler(self, channel: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Register a message handler for a channel.
        
        Args:
            channel: Channel name
            handler: Message handler function
        """
        if channel not in self.handlers:
            self.handlers[channel] = []
        
        self.handlers[channel].append(handler)
        logger.info(f"Registered handler for channel: {channel}")
        
        # Subscribe to the channel if not already subscribed
        if self.enabled and self.messaging_service:
            await self.subscribe(channel)
    
    async def unregister_handler(self, channel: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Unregister a message handler for a channel.
        
        Args:
            channel: Channel name
            handler: Message handler function
        """
        if channel in self.handlers and handler in self.handlers[channel]:
            self.handlers[channel].remove(handler)
            logger.info(f"Unregistered handler for channel: {channel}")
            
            # Unsubscribe from the channel if no handlers left
            if not self.handlers[channel] and self.enabled and self.messaging_service:
                await self.unsubscribe(channel)
    
    async def _message_handler(self, channel: str, message: str) -> None:
        """Handle a message from a channel.
        
        Args:
            channel: Channel name
            message: Message data
        """
        try:
            message_data = json.loads(message)
            
            if channel in self.handlers:
                for handler in self.handlers[channel]:
                    try:
                        await handler(message_data)
                    except Exception as e:
                        logger.error(f"Error in handler for {channel}: {str(e)}")
        except json.JSONDecodeError:
            logger.error(f"Error decoding message from {channel}: {message}")
        except Exception as e:
            logger.error(f"Error handling message from {channel}: {str(e)}")
    
    async def publish_command_progress(
        self, 
        command_id: str, 
        agent_id: str, 
        progress: str
    ) -> bool:
        """Publish command progress.
        
        Args:
            command_id: Command ID
            agent_id: Agent ID
            progress: Progress message
            
        Returns:
            bool: True if published, False otherwise
        """
        progress_data = {
            "command_id": command_id,
            "agent_id": agent_id,
            "progress": progress
        }
        
        return await self.publish("command_progress", progress_data)
    
    async def publish_command_result(
        self, 
        command_id: str, 
        agent_id: str, 
        result: Dict[str, Any]
    ) -> bool:
        """Publish command result.
        
        Args:
            command_id: Command ID
            agent_id: Agent ID
            result: Result data
            
        Returns:
            bool: True if published, False otherwise
        """
        result_data = {
            "command_id": command_id,
            "agent_id": agent_id,
            "result": result
        }
        
        return await self.publish("command_result", result_data)
    
    async def publish_agent_status(self, agent_id: str, status: Dict[str, Any]) -> bool:
        """Publish agent status.
        
        Args:
            agent_id: Agent ID
            status: Status data
            
        Returns:
            bool: True if published, False otherwise
        """
        status_data = {
            "agent_id": agent_id,
            "status": status
        }
        
        return await self.publish("agent_status", status_data)
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self.enabled and self.messaging_service:
            for channel in list(self.handlers.keys()):
                await self.unsubscribe(channel)
            
            self.handlers.clear()
            await self.messaging_service.cleanup() 