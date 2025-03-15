from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Awaitable

# Type for event handlers
EventHandlerType = Callable[[str, Dict[str, Any]], Awaitable[None]]

class EventHandler(ABC):
    """
    Interface for handling events.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def unregister_handler(
        self,
        event: str
    ) -> None:
        """
        Unregister a handler for an event.
        
        Args:
            event: The event name
        """
        pass
    
    @abstractmethod
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
        pass 