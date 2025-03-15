import os
import redis
import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger("redis_manager")

class RedisManager:
    """Redis manager for pub/sub and caching"""
    
    def __init__(self, url: Optional[str] = None):
        """Initialize the Redis manager"""
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = None
        self.pubsub = None
        self.connected = False
        
        # Connect to Redis
        self.connect()
    
    def connect(self) -> bool:
        """Connect to Redis"""
        try:
            logger.info(f"Connecting to Redis at {self.url}")
            self.client = redis.from_url(self.url)
            self.pubsub = self.client.pubsub()
            self.connected = True
            logger.info("Connected to Redis")
            return True
        except Exception as e:
            logger.error(f"Error connecting to Redis: {str(e)}")
            self.connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.client:
            logger.info("Disconnecting from Redis")
            self.client.close()
            self.client = None
            self.pubsub = None
            self.connected = False
    
    def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish a message to a channel"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            logger.debug(f"Publishing message to channel {channel}")
            self.client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Error publishing message to channel {channel}: {str(e)}")
            return False
    
    def subscribe(self, channel: str) -> None:
        """Subscribe to a channel"""
        if not self.connected:
            if not self.connect():
                return
        
        try:
            logger.info(f"Subscribing to channel {channel}")
            self.pubsub.subscribe(channel)
        except Exception as e:
            logger.error(f"Error subscribing to channel {channel}: {str(e)}")
    
    def get_message(self) -> Optional[Dict[str, Any]]:
        """Get a message from the subscribed channels"""
        if not self.connected or not self.pubsub:
            return None
        
        try:
            message = self.pubsub.get_message()
            if message and message["type"] == "message":
                return json.loads(message["data"])
            return None
        except Exception as e:
            logger.error(f"Error getting message: {str(e)}")
            return None
    
    def set(self, key: str, value: Any, expiry: Optional[int] = None) -> bool:
        """Set a key-value pair in Redis"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            if expiry:
                self.client.setex(key, expiry, json.dumps(value))
            else:
                self.client.set(key, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {str(e)}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {str(e)}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {str(e)}")
            return False

# Create a singleton instance
redis_manager = RedisManager() 