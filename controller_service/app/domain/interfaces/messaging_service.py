"""Messaging service interface for the controller service."""

import abc
from typing import Dict, Any, Optional, Callable, Awaitable


class MessagingServiceInterface(abc.ABC):
    """Interface for messaging services."""
    
    @abc.abstractmethod
    async def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish a message to a channel.
        
        Args:
            channel: The channel to publish to
            message: The message to publish
            
        Returns:
            bool: True if the message was published successfully, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> bool:
        """Subscribe to a channel.
        
        Args:
            channel: The channel to subscribe to
            callback: The callback to call when a message is received
            
        Returns:
            bool: True if the subscription was successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def unsubscribe(self, channel: str) -> bool:
        """Unsubscribe from a channel.
        
        Args:
            channel: The channel to unsubscribe from
            
        Returns:
            bool: True if the unsubscription was successful, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def set(self, key: str, value: Dict[str, Any], expiration: Optional[int] = None) -> bool:
        """Set a key-value pair.
        
        Args:
            key: The key to set
            value: The value to set
            expiration: Optional expiration time in seconds
            
        Returns:
            bool: True if the key-value pair was set successfully, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value by key.
        
        Args:
            key: The key to get
            
        Returns:
            Optional[Dict[str, Any]]: The value, or None if not found
        """
        pass
    
    @abc.abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a key-value pair.
        
        Args:
            key: The key to delete
            
        Returns:
            bool: True if the key-value pair was deleted successfully, False otherwise
        """
        pass
    
    @property
    @abc.abstractmethod
    def connected(self) -> bool:
        """Check if the messaging service is connected.
        
        Returns:
            bool: True if the messaging service is connected, False otherwise
        """
        pass 