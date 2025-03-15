import logging
import asyncio
import json
from typing import Dict, Any, Optional, Callable, Awaitable, List

from app.domain.interfaces.event_handler import EventHandler, EventHandlerType
from app.infrastructure.messaging.redis_manager import RedisManager

class RedisEventHandler(EventHandler):
    """
    Redis implementation of the event handler interface.
    """
    
    def __init__(
        self,
        redis_manager: RedisManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Redis event handler.
        
        Args:
            redis_manager: The Redis manager
            logger: Optional logger
        """
        self.redis_manager = redis_manager
        self.logger = logger or logging.getLogger(__name__)
        self.handlers = {}
        self.running = False
    
    async def register_handler(
        self,
        event: str,
        handler: EventHandlerType
    ) -> None:
        """
        Register a handler for an event.
        
        Args:
            event: The event name
            handler: The handler function
        """
        try:
            # Register handler
            self.handlers[event] = handler
            
            # Subscribe to the event channel
            await self.redis_manager.subscribe(event)
            
            self.logger.info(f"Registered handler for event: {event}")
            
            # Start message loop if not already running
            if not self.running:
                self.running = True
                asyncio.create_task(self._message_loop())
        except Exception as e:
            self.logger.error(f"Error registering handler for event {event}: {str(e)}")
    
    async def unregister_handler(
        self,
        event: str
    ) -> None:
        """
        Unregister a handler for an event.
        
        Args:
            event: The event name
        """
        try:
            # Unregister handler
            if event in self.handlers:
                del self.handlers[event]
            
            # Unsubscribe from the event channel
            await self.redis_manager.unsubscribe(event)
            
            self.logger.info(f"Unregistered handler for event: {event}")
        except Exception as e:
            self.logger.error(f"Error unregistering handler for event {event}: {str(e)}")
    
    async def emit(
        self,
        event: str,
        data: Dict[str, Any],
        room: str = None
    ) -> None:
        """
        Emit an event.
        
        Args:
            event: The event name
            data: The event data
            room: Optional room to emit to (ignored in Redis implementation)
        """
        try:
            # Prepare message
            message = {
                "event": event,
                "data": data
            }
            
            # Add room if provided
            if room:
                message["room"] = room
            
            # Publish message to the event channel
            await self.redis_manager.publish(event, message)
            
            self.logger.info(f"Emitted event: {event}")
        except Exception as e:
            self.logger.error(f"Error emitting event {event}: {str(e)}")
    
    async def _message_loop(self) -> None:
        """
        Process messages from subscribed channels.
        """
        try:
            self.logger.info("Starting Redis event handler message loop")
            
            while self.running:
                try:
                    # Get a message
                    message = await self.redis_manager.get_message()
                    
                    if message:
                        channel = message.get("channel")
                        data = message.get("data")
                        
                        # Process message if it's an event we're handling
                        if channel in self.handlers:
                            handler = self.handlers[channel]
                            
                            # Extract event data
                            event_data = data.get("data", {})
                            
                            # Call handler
                            await handler(channel, event_data)
                    
                    # Sleep to avoid high CPU usage
                    await asyncio.sleep(0.01)
                except Exception as e:
                    self.logger.error(f"Error in message loop: {str(e)}")
                    await asyncio.sleep(1)
        except Exception as e:
            self.logger.error(f"Error in message loop: {str(e)}")
            self.running = False 