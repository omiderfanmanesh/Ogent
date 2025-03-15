"""Socket service interface for the controller service."""

import abc
from typing import Dict, Any, Optional, Callable, Awaitable, List


class SocketServiceInterface(abc.ABC):
    """Interface for socket services."""
    
    @abc.abstractmethod
    async def emit(self, event: str, data: Dict[str, Any], room: Optional[str] = None) -> bool:
        """Emit an event to a room or all connected clients.
        
        Args:
            event: The event to emit
            data: The data to emit
            room: Optional room to emit to
            
        Returns:
            bool: True if the event was emitted successfully, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def join_room(self, sid: str, room: str) -> bool:
        """Join a room.
        
        Args:
            sid: The Socket.IO session ID
            room: The room to join
            
        Returns:
            bool: True if the room was joined successfully, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def leave_room(self, sid: str, room: str) -> bool:
        """Leave a room.
        
        Args:
            sid: The Socket.IO session ID
            room: The room to leave
            
        Returns:
            bool: True if the room was left successfully, False otherwise
        """
        pass
    
    @abc.abstractmethod
    async def get_rooms(self, sid: str) -> List[str]:
        """Get the rooms a client is in.
        
        Args:
            sid: The Socket.IO session ID
            
        Returns:
            List[str]: List of rooms
        """
        pass
    
    @abc.abstractmethod
    async def get_room_members(self, room: str) -> List[str]:
        """Get the members of a room.
        
        Args:
            room: The room to get members of
            
        Returns:
            List[str]: List of Socket.IO session IDs
        """
        pass
    
    @abc.abstractmethod
    async def register_handler(self, event: str, handler: Callable[[str, Dict[str, Any]], Awaitable[None]]) -> None:
        """Register an event handler.
        
        Args:
            event: The event to handle
            handler: The handler function
        """
        pass
    
    @abc.abstractmethod
    async def disconnect(self, sid: str) -> bool:
        """Disconnect a client.
        
        Args:
            sid: The Socket.IO session ID
            
        Returns:
            bool: True if the client was disconnected successfully, False otherwise
        """
        pass 