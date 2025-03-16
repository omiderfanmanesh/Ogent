"""WebSocket connection manager for the agent API."""

import logging
from typing import List, Dict, Any
from fastapi import WebSocket

logger = logging.getLogger("agent.api.websocket")

class ConnectionManager:
    """WebSocket connection manager.
    
    Responsible for managing WebSocket connections and sending messages to clients.
    Follows the Singleton pattern to ensure only one instance exists.
    """
    
    _instance = None
    
    def __new__(cls):
        """Create a new instance if one doesn't exist."""
        if cls._instance is None:
            cls._instance = super(ConnectionManager, cls).__new__(cls)
            cls._instance.active_connections = []
        return cls._instance
    
    def __init__(self):
        """Initialize the connection manager."""
        # Initialize active_connections only if it doesn't exist
        if not hasattr(self, "active_connections"):
            self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Connect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client.
        
        Args:
            websocket: WebSocket connection
        """
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_progress(self, websocket: WebSocket, data: Dict[str, Any]):
        """Send progress update to a WebSocket client.
        
        Args:
            websocket: WebSocket connection
            data: Progress data
        """
        try:
            await websocket.send_json(data)
        except Exception as e:
            logger.error(f"Error sending progress update: {str(e)}")
            # Remove the connection if it's closed
            if websocket in self.active_connections:
                self.disconnect(websocket)
    
    async def broadcast(self, data: Dict[str, Any]):
        """Broadcast a message to all connected clients.
        
        Args:
            data: Message data
        """
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            if connection in self.active_connections:
                self.disconnect(connection) 