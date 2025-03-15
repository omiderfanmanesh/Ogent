"""Client service for the agent service."""

import os
import asyncio
import logging
import json
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime

import socketio

from agent.infrastructure.config.config import config
from agent.application.services.agent_manager import AgentManager
from agent.utils import UTC

logger = logging.getLogger("agent.client")


class ClientService:
    """Client service for the agent service."""
    
    def __init__(self, agent_manager: Optional[AgentManager] = None):
        """Initialize the client service.
        
        Args:
            agent_manager: Agent manager instance
        """
        # Store the agent manager
        self.agent_manager = agent_manager
        
        # Create a Socket.IO client
        self.sio = socketio.AsyncClient(
            reconnection=True, 
            reconnection_attempts=config.max_reconnect_attempts, 
            reconnection_delay=config.reconnect_delay, 
            logger=True, 
            engineio_logger=True
        )
        
        # Generate a unique agent ID
        self.agent_id = os.getenv("AGENT_ID", f"agent-{os.getpid()}")
        self.sio.agent_id = self.agent_id
        
        # Track connection state
        self.connected = False
        self.reconnect_attempts = 0
        
        # Register event handlers
        self.sio.on("connect", self.handle_connect)
        self.sio.on("disconnect", self.handle_disconnect)
        self.sio.on("connection_response", self.handle_connection_response)
        self.sio.on("command_response", self.handle_command_response)
        self.sio.on("execute_command", self.handle_execute_command)
    
    async def start(self):
        """Start the client service."""
        logger.info(f"Starting client service with agent ID: {self.agent_id}")
        
        # Get authentication token
        token = await self.get_auth_token()
        
        try:
            # Connect to the controller service
            await self.sio.connect(
                config.controller_url,
                auth={
                    "agent_id": self.agent_id, 
                    "token": token,
                    "is_agent": True
                },
                wait_timeout=60
            )
            
            # Wait for disconnect
            await self.sio.wait()
            
        except Exception as e:
            logger.error(f"Error connecting to controller service: {str(e)}")
            self.connected = False
    
    async def get_auth_token(self) -> Optional[str]:
        """Get authentication token from the Controller Service.
        
        Returns:
            Optional[str]: Authentication token, or None if authentication fails
        """
        try:
            logger.info(f"Requesting authentication token from {config.controller_url}/token")
            import requests  # Import here to avoid circular imports
            
            response = requests.post(
                f"{config.controller_url}/token",
                data={"username": config.agent_username, "password": config.agent_password}
            )
            
            if response.status_code == 200:
                token = response.json()["access_token"]
                logger.info("Authentication successful")
                return token
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None
    
    async def handle_connect(self):
        """Handle successful connection to the Controller Service."""
        self.connected = True
        self.reconnect_attempts = 0
        logger.info("Connected to Controller Service")
        
        # Register the agent with the Controller Service
        await self.sio.emit("register", {"agent_id": self.agent_id})
    
    async def handle_disconnect(self):
        """Handle disconnection from the Controller Service."""
        self.connected = False
        logger.info("Disconnected from Controller Service")
    
    async def handle_connection_response(self, data):
        """Handle connection response from the Controller Service.
        
        Args:
            data: Connection response data
        """
        logger.info(f"Connection response: {data}")
    
    async def handle_command_response(self, data):
        """Handle command response from the Controller Service.
        
        Args:
            data: Command response data
        """
        logger.info(f"Command response received: {data}")
    
    async def handle_execute_command(self, data):
        """Handle command execution request from the Controller Service.
        
        Args:
            data: Command execution request data
        """
        logger.info(f"Received command execution request: {data}")
        
        # Validate the request
        if not isinstance(data, dict) or 'command' not in data:
            logger.error("Invalid command format received")
            await self.sio.emit('command_result', {
                'status': 'error',
                'message': 'Invalid command format',
                'timestamp': datetime.now(UTC).isoformat()
            })
            return
        
        # Store the requester's SID if provided
        requester_sid = data.get('requester_sid')
        
        # Get command ID if provided
        command_id = data.get('command_id')
        
        # Get execution target if specified
        executor_type = data.get('execution_target', 'auto')
        
        # Create a progress callback
        async def progress_callback(progress_data):
            await self.send_command_progress(command_id, requester_sid, progress_data)
        
        # Get the agent manager
        if not self.agent_manager:
            # Import here to avoid circular imports
            from agent.infrastructure.container import container
            self.agent_manager = container.get_agent_manager()
        
        # Execute the command using the agent manager
        result = await self.agent_manager.execute_command(
            command=data['command'],
            executor_type=executor_type,
            command_id=command_id,
            progress_callback=progress_callback
        )
        
        # Send the result back to the Controller Service
        await self.sio.emit('command_result', {
            'status': 'success' if result['exit_code'] == 0 else 'error',
            'command': data['command'],
            'command_id': command_id,
            'result': result,
            'requester_sid': requester_sid,
            'timestamp': datetime.now(UTC).isoformat()
        })
        
        # Publish to Redis if available
        if config.redis_client:
            config.redis_client.publish('command_results', json.dumps({
                'type': 'command_result',
                'data': {
                    'status': 'success' if result['exit_code'] == 0 else 'error',
                    'command': data['command'],
                    'command_id': command_id,
                    'result': result,
                    'requester_sid': requester_sid,
                    'timestamp': datetime.now(UTC).isoformat()
                }
            }))
    
    async def send_command_progress(self, command_id, requester_sid, progress_data):
        """Send command progress updates to the Controller Service.
        
        Args:
            command_id: Command ID
            requester_sid: Requester's Socket.IO session ID
            progress_data: Progress data
        """
        if not command_id:
            return
        
        try:
            # Add command ID and requester SID to progress data
            progress_data['command_id'] = command_id
            progress_data['requester_sid'] = requester_sid
            
            # Send progress update via Socket.IO
            if self.connected:
                await self.sio.emit('command_progress', progress_data)
            
            # Publish to Redis if available
            if config.redis_client:
                config.redis_client.publish('command_progress', json.dumps({
                    'type': 'command_progress',
                    'data': progress_data
                }))
        except Exception as e:
            logger.error(f"Error sending command progress: {str(e)}")
    
    def cleanup(self):
        """Clean up resources used by the client service."""
        if self.connected:
            asyncio.create_task(self.sio.disconnect())


# Create a singleton instance
client_service = ClientService() 