import socketio
import logging
import asyncio
import json
import os
from typing import Dict, Any, Optional, List, Callable, Awaitable, Union
from datetime import datetime

from ...domain.command.entities import Command
from ...application.command_service import CommandPublisher
from app.domain.interfaces.event_handler import EventHandler, EventHandlerType

class SocketManager(EventHandler):
    """
    Socket.IO manager for real-time communication.
    """
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        cors_allowed_origins: List[str] = None,
        redis_url: Optional[str] = None
    ):
        """
        Initialize the Socket.IO manager.
        
        Args:
            logger: Optional logger
            cors_allowed_origins: CORS allowed origins
            redis_url: Optional Redis URL for Socket.IO adapter
        """
        self.logger = logger or logging.getLogger(__name__)
        self.cors_allowed_origins = cors_allowed_origins or ["*"]
        self.redis_url = redis_url
        
        # Create Socket.IO server
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=self.cors_allowed_origins,
            logger=self.logger,
            engineio_logger=self.logger
        )
        
        # Use Redis adapter if URL provided
        if self.redis_url:
            try:
                self.sio.attach(socketio.AsyncRedisManager(self.redis_url))
                self.logger.info(f"Using Redis adapter for Socket.IO at {self.redis_url}")
            except Exception as e:
                self.logger.error(f"Error attaching Redis adapter: {str(e)}")
        
        # Create ASGI app
        self.app = socketio.ASGIApp(self.sio)
        
        # Session storage
        self.sessions = {}
        
        # Register default event handlers
        self.sio.on("connect", self._handle_connect)
        self.sio.on("disconnect", self._handle_disconnect)
    
    async def _handle_connect(self, sid, environ):
        """
        Handle client connection.
        
        Args:
            sid: Socket ID
            environ: WSGI environment
        """
        try:
            self.logger.info(f"Client connected: {sid}")
            
            # Store session
            self.sessions[sid] = {
                "sid": sid,
                "connected_at": asyncio.get_event_loop().time()
            }
        except Exception as e:
            self.logger.error(f"Error handling connect for {sid}: {str(e)}")
    
    async def _handle_disconnect(self, sid):
        """
        Handle client disconnection.
        
        Args:
            sid: Socket ID
        """
        try:
            self.logger.info(f"Client disconnected: {sid}")
            
            # Remove session
            if sid in self.sessions:
                del self.sessions[sid]
        except Exception as e:
            self.logger.error(f"Error handling disconnect for {sid}: {str(e)}")
    
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
            # Create wrapper to match Socket.IO signature
            async def wrapper(sid, data):
                try:
                    # Get session
                    session = self.sessions.get(sid, {"sid": sid})
                    
                    # Call handler with session and data
                    await handler(session, data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event}: {str(e)}")
            
            # Register handler
            self.sio.on(event, wrapper)
            self.logger.info(f"Registered handler for event: {event}")
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
            self.sio.handlers.pop(event, None)
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
            room: Optional room to emit to
        """
        try:
            # Emit event
            await self.sio.emit(event, data, room=room)
            
            if room:
                self.logger.info(f"Emitted event {event} to room {room}")
            else:
                self.logger.info(f"Emitted event {event} to all clients")
        except Exception as e:
            self.logger.error(f"Error emitting event {event}: {str(e)}")
    
    async def get_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a session by user ID.
        
        Args:
            user_id: The user ID
            
        Returns:
            Optional[Dict[str, Any]]: The session if found, None otherwise
        """
        try:
            # Find session by user ID
            for sid, session in self.sessions.items():
                if session.get("user_id") == user_id:
                    return session
            
            return None
        except Exception as e:
            self.logger.error(f"Error getting session for user {user_id}: {str(e)}")
            return None
    
    async def save_session(self, sid: str, data: Dict[str, Any]) -> bool:
        """
        Save session data.
        
        Args:
            sid: Socket ID
            data: Session data
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Get existing session or create new one
            session = self.sessions.get(sid, {"sid": sid})
            
            # Update session
            session.update(data)
            
            # Save session
            self.sessions[sid] = session
            
            return True
        except Exception as e:
            self.logger.error(f"Error saving session for {sid}: {str(e)}")
            return False 