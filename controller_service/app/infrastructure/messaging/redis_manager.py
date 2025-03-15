import redis
import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union

class RedisManager:
    """
    Redis manager for messaging and caching.
    """
    def __init__(
        self,
        redis_url: str,
        logger: Optional[logging.Logger] = None,
        decode_responses: bool = True
    ):
        self.redis_url = redis_url
        self.logger = logger or logging.getLogger(__name__)
        self.decode_responses = decode_responses
        self.redis = None
        self.pubsub = None
        self.subscribed_channels = set()
        self.message_handlers = {}
        self.connected = False
    
    def connect(self) -> bool:
        """
        Connect to Redis.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        try:
            self.redis = redis.Redis.from_url(
                self.redis_url,
                decode_responses=self.decode_responses
            )
            self.pubsub = self.redis.pubsub()
            self.connected = True
            self.logger.info(f"Connected to Redis at {self.redis_url}")
            return True
        except Exception as e:
            self.logger.error(f"Error connecting to Redis: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Redis."""
        try:
            if self.pubsub:
                self.pubsub.close()
            
            if self.redis:
                self.redis.close()
            
            self.connected = False
            self.logger.info("Disconnected from Redis")
        except Exception as e:
            self.logger.error(f"Error disconnecting from Redis: {str(e)}")
    
    async def set(
        self,
        key: str,
        value: Union[str, Dict, List],
        expire_seconds: Optional[int] = None
    ) -> bool:
        """
        Set a key-value pair in Redis.
        
        Args:
            key: The key
            value: The value (string, dict, or list)
            expire_seconds: Optional expiry time in seconds
            
        Returns:
            bool: True if set successfully, False otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # Serialize value if it's a dict or list
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            # Set the value
            self.redis.set(key, value)
            
            # Set expiry if provided
            if expire_seconds:
                self.redis.expire(key, expire_seconds)
            
            return True
        except Exception as e:
            self.logger.error(f"Error setting key {key}: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Union[str, Dict, List]]:
        """
        Get a value from Redis.
        
        Args:
            key: The key
            
        Returns:
            Optional[Union[str, Dict, List]]: The value if found, None otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return None
            
            # Get the value
            value = self.redis.get(key)
            
            if not value:
                return None
            
            # Try to deserialize as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Return as is if not JSON
                return value
        except Exception as e:
            self.logger.error(f"Error getting key {key}: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key: The key
            
        Returns:
            bool: True if deleted successfully, False otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # Delete the key
            self.redis.delete(key)
            return True
        except Exception as e:
            self.logger.error(f"Error deleting key {key}: {str(e)}")
            return False
    
    async def keys(self, pattern: str) -> List[str]:
        """
        Get keys matching a pattern.
        
        Args:
            pattern: The pattern to match
            
        Returns:
            List[str]: List of matching keys
        """
        try:
            if not self.connected:
                if not self.connect():
                    return []
            
            # Get keys matching the pattern
            keys = self.redis.keys(pattern)
            return keys
        except Exception as e:
            self.logger.error(f"Error getting keys with pattern {pattern}: {str(e)}")
            return []
    
    async def sadd(self, key: str, member: str) -> bool:
        """
        Add a member to a set.
        
        Args:
            key: The set key
            member: The member to add
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # Add the member to the set
            self.redis.sadd(key, member)
            return True
        except Exception as e:
            self.logger.error(f"Error adding member {member} to set {key}: {str(e)}")
            return False
    
    async def srem(self, key: str, member: str) -> bool:
        """
        Remove a member from a set.
        
        Args:
            key: The set key
            member: The member to remove
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # Remove the member from the set
            self.redis.srem(key, member)
            return True
        except Exception as e:
            self.logger.error(f"Error removing member {member} from set {key}: {str(e)}")
            return False
    
    async def smembers(self, key: str) -> List[str]:
        """
        Get all members of a set.
        
        Args:
            key: The set key
            
        Returns:
            List[str]: List of members
        """
        try:
            if not self.connected:
                if not self.connect():
                    return []
            
            # Get all members of the set
            members = self.redis.smembers(key)
            return list(members)
        except Exception as e:
            self.logger.error(f"Error getting members of set {key}: {str(e)}")
            return []
    
    async def publish(self, channel: str, message: Union[str, Dict, List]) -> bool:
        """
        Publish a message to a channel.
        
        Args:
            channel: The channel
            message: The message (string, dict, or list)
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # Serialize message if it's a dict or list
            if isinstance(message, (dict, list)):
                message = json.dumps(message)
            
            # Publish the message
            self.redis.publish(channel, message)
            return True
        except Exception as e:
            self.logger.error(f"Error publishing to channel {channel}: {str(e)}")
            return False
    
    async def subscribe(self, channel: str, handler: Optional[Callable] = None) -> bool:
        """
        Subscribe to a channel.
        
        Args:
            channel: The channel
            handler: Optional handler function for messages
            
        Returns:
            bool: True if subscribed successfully, False otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # Subscribe to the channel
            self.pubsub.subscribe(channel)
            self.subscribed_channels.add(channel)
            
            # Register handler if provided
            if handler:
                self.message_handlers[channel] = handler
            
            self.logger.info(f"Subscribed to channel: {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error subscribing to channel {channel}: {str(e)}")
            return False
    
    async def unsubscribe(self, channel: str) -> bool:
        """
        Unsubscribe from a channel.
        
        Args:
            channel: The channel
            
        Returns:
            bool: True if unsubscribed successfully, False otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return False
            
            # Unsubscribe from the channel
            self.pubsub.unsubscribe(channel)
            self.subscribed_channels.discard(channel)
            
            # Remove handler if registered
            if channel in self.message_handlers:
                del self.message_handlers[channel]
            
            self.logger.info(f"Unsubscribed from channel: {channel}")
            return True
        except Exception as e:
            self.logger.error(f"Error unsubscribing from channel {channel}: {str(e)}")
            return False
    
    async def get_message(self) -> Optional[Dict[str, Any]]:
        """
        Get a message from subscribed channels.
        
        Returns:
            Optional[Dict[str, Any]]: The message if available, None otherwise
        """
        try:
            if not self.connected:
                if not self.connect():
                    return None
            
            # Get a message
            message = self.pubsub.get_message()
            
            if not message:
                return None
            
            # Skip subscription confirmation messages
            if message['type'] in ('subscribe', 'unsubscribe'):
                return None
            
            # Process the message
            channel = message['channel']
            data = message['data']
            
            # Try to deserialize as JSON
            try:
                if isinstance(data, str):
                    data = json.loads(data)
            except (json.JSONDecodeError, TypeError):
                # Use as is if not JSON
                pass
            
            # Call handler if registered
            if channel in self.message_handlers:
                asyncio.create_task(self.message_handlers[channel](channel, data))
            
            return {
                'channel': channel,
                'data': data
            }
        except Exception as e:
            self.logger.error(f"Error getting message: {str(e)}")
            return None
    
    async def start_message_loop(self) -> None:
        """Start a loop to process messages from subscribed channels."""
        try:
            if not self.connected:
                if not self.connect():
                    return
            
            self.logger.info("Starting Redis message loop")
            
            while True:
                try:
                    # Get a message
                    message = await self.get_message()
                    
                    # Sleep to avoid high CPU usage
                    await asyncio.sleep(0.01)
                except Exception as e:
                    self.logger.error(f"Error in message loop: {str(e)}")
                    await asyncio.sleep(1)
        except Exception as e:
            self.logger.error(f"Error starting message loop: {str(e)}")
    
    def start_message_loop_background(self) -> None:
        """Start the message loop in the background."""
        asyncio.create_task(self.start_message_loop()) 