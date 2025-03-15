import logging
from typing import Optional, Dict, Any

from app.domain.interfaces.command_publisher import CommandPublisher
from app.domain.interfaces.event_handler import EventHandler
from app.infrastructure.messaging.redis_manager import RedisManager
from app.infrastructure.messaging.socket_manager import SocketManager
from app.infrastructure.messaging.redis_command_publisher import RedisCommandPublisher
from app.infrastructure.messaging.socketio_command_publisher import SocketIOCommandPublisher
from app.infrastructure.messaging.redis_event_handler import RedisEventHandler

class MessagingFactory:
    """
    Factory for creating messaging components.
    """
    
    def __init__(
        self,
        redis_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the messaging factory.
        
        Args:
            redis_url: Optional Redis URL
            logger: Optional logger
            config: Optional configuration
        """
        self.redis_url = redis_url
        self.logger = logger or logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize components
        self.redis_manager = None
        self.socket_manager = None
    
    def create_redis_manager(self) -> RedisManager:
        """
        Create a Redis manager.
        
        Returns:
            RedisManager: The Redis manager
        """
        if not self.redis_manager:
            self.redis_manager = RedisManager(
                redis_url=self.redis_url,
                logger=self.logger
            )
            self.redis_manager.connect()
        
        return self.redis_manager
    
    def create_socket_manager(self) -> SocketManager:
        """
        Create a Socket.IO manager.
        
        Returns:
            SocketManager: The Socket.IO manager
        """
        if not self.socket_manager:
            cors_allowed_origins = self.config.get("cors_allowed_origins", ["*"])
            
            self.socket_manager = SocketManager(
                logger=self.logger,
                cors_allowed_origins=cors_allowed_origins,
                redis_url=self.redis_url
            )
        
        return self.socket_manager
    
    def create_command_publisher(self, publisher_type: str = "socketio") -> CommandPublisher:
        """
        Create a command publisher.
        
        Args:
            publisher_type: The type of publisher to create (socketio or redis)
            
        Returns:
            CommandPublisher: The command publisher
        """
        if publisher_type == "socketio":
            socket_manager = self.create_socket_manager()
            return SocketIOCommandPublisher(
                socket_manager=socket_manager,
                logger=self.logger
            )
        elif publisher_type == "redis":
            redis_manager = self.create_redis_manager()
            return RedisCommandPublisher(
                redis_manager=redis_manager,
                logger=self.logger
            )
        else:
            raise ValueError(f"Invalid publisher type: {publisher_type}")
    
    def create_event_handler(self, handler_type: str = "socketio") -> EventHandler:
        """
        Create an event handler.
        
        Args:
            handler_type: The type of handler to create (socketio or redis)
            
        Returns:
            EventHandler: The event handler
        """
        if handler_type == "socketio":
            return self.create_socket_manager()
        elif handler_type == "redis":
            redis_manager = self.create_redis_manager()
            return RedisEventHandler(
                redis_manager=redis_manager,
                logger=self.logger
            )
        else:
            raise ValueError(f"Invalid handler type: {handler_type}") 