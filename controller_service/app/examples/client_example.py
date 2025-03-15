import asyncio
import logging
import os
import sys
import socketio
import json
import argparse
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("client_example")

class SocketIOClient:
    """
    Socket.IO client for connecting to the controller service.
    """
    
    def __init__(
        self,
        server_url: str,
        agent_id: str,
        username: str = "agent",
        logger=None
    ):
        """
        Initialize the Socket.IO client.
        
        Args:
            server_url: The URL of the Socket.IO server
            agent_id: The agent ID
            username: The username
            logger: Optional logger
        """
        self.server_url = server_url
        self.agent_id = agent_id
        self.username = username
        self.logger = logger or logging.getLogger(__name__)
        
        # Create Socket.IO client
        self.sio = socketio.AsyncClient(logger=self.logger, engineio_logger=self.logger)
        
        # Register event handlers
        self.sio.on("connect", self._handle_connect)
        self.sio.on("disconnect", self._handle_disconnect)
        self.sio.on("command", self._handle_command)
    
    async def _handle_connect(self):
        """Handle connection event."""
        self.logger.info(f"Connected to server: {self.server_url}")
        
        # Register with the server
        await self.register()
    
    async def _handle_disconnect(self):
        """Handle disconnection event."""
        self.logger.info("Disconnected from server")
    
    async def _handle_command(self, data):
        """
        Handle command event.
        
        Args:
            data: The command data
        """
        try:
            self.logger.info(f"Received command: {data}")
            
            # Extract command information
            command_id = data.get("command_id")
            command_data = data.get("data", {})
            
            if not command_id:
                self.logger.error("Missing command_id in command data")
                return
            
            # Execute the command
            self.logger.info(f"Executing command {command_id}: {command_data}")
            
            # Simulate command execution
            await asyncio.sleep(1)
            
            # Prepare result
            result = {
                "output": f"Command {command_id} executed successfully",
                "exit_code": 0
            }
            
            # Send result
            await self.send_command_result(command_id, result, "success")
        except Exception as e:
            self.logger.error(f"Error handling command: {str(e)}")
    
    async def connect(self):
        """Connect to the server."""
        try:
            await self.sio.connect(self.server_url)
        except Exception as e:
            self.logger.error(f"Error connecting to server: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from the server."""
        try:
            await self.sio.disconnect()
        except Exception as e:
            self.logger.error(f"Error disconnecting from server: {str(e)}")
    
    async def register(self):
        """Register with the server."""
        try:
            # Prepare registration data
            data = {
                "agent_id": self.agent_id,
                "username": self.username
            }
            
            # Emit registration event
            await self.sio.emit("register", data)
            self.logger.info(f"Registered as agent {self.agent_id}")
        except Exception as e:
            self.logger.error(f"Error registering with server: {str(e)}")
    
    async def send_command_result(
        self,
        command_id: str,
        result: Dict[str, Any],
        status: str,
        error: str = None
    ):
        """
        Send a command result to the server.
        
        Args:
            command_id: The command ID
            result: The command result
            status: The status of the command (success, error, etc.)
            error: Optional error message
        """
        try:
            # Prepare result data
            data = {
                "command_id": command_id,
                "result": result,
                "status": status
            }
            
            # Add error if provided
            if error:
                data["error"] = error
            
            # Emit result event
            await self.sio.emit("command_result", data)
            self.logger.info(f"Sent result for command {command_id}")
        except Exception as e:
            self.logger.error(f"Error sending command result: {str(e)}")

async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Socket.IO client example")
    parser.add_argument("--server", default="http://localhost:8000/ws", help="Server URL")
    parser.add_argument("--agent-id", default="agent-1", help="Agent ID")
    parser.add_argument("--username", default="agent", help="Username")
    args = parser.parse_args()
    
    # Create client
    client = SocketIOClient(
        server_url=args.server,
        agent_id=args.agent_id,
        username=args.username,
        logger=logger
    )
    
    # Connect to server
    await client.connect()
    
    # Keep the client running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Exiting...")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 