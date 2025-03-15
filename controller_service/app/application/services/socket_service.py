"""Socket service for the controller service."""

import logging
import json
from typing import Dict, Any, Optional, Callable, List, Union

from ...domain.interfaces.socket_service import SocketServiceInterface
from ...domain.models.agent import Agent
from ...domain.models.command import Command

logger = logging.getLogger("controller.socket_service")


class SocketService:
    """Service for socket operations."""
    
    def __init__(self, socket_service_interface: SocketServiceInterface):
        """Initialize the socket service.
        
        Args:
            socket_service_interface: Socket service interface implementation
        """
        self.socket_service = socket_service_interface
        self.agent_sid_map: Dict[str, str] = {}  # Maps agent_id to socket_id
        self.user_sid_map: Dict[str, str] = {}   # Maps username to socket_id
    
    async def register_agent_connection(self, agent_id: str, socket_id: str) -> None:
        """Register an agent connection.
        
        Args:
            agent_id: Agent ID
            socket_id: Socket ID
        """
        self.agent_sid_map[agent_id] = socket_id
        logger.info(f"Registered agent connection: {agent_id} -> {socket_id}")
    
    async def unregister_agent_connection(self, agent_id: str) -> None:
        """Unregister an agent connection.
        
        Args:
            agent_id: Agent ID
        """
        if agent_id in self.agent_sid_map:
            del self.agent_sid_map[agent_id]
            logger.info(f"Unregistered agent connection: {agent_id}")
    
    async def register_user_connection(self, username: str, socket_id: str) -> None:
        """Register a user connection.
        
        Args:
            username: Username
            socket_id: Socket ID
        """
        self.user_sid_map[username] = socket_id
        logger.info(f"Registered user connection: {username} -> {socket_id}")
    
    async def unregister_user_connection(self, username: str) -> None:
        """Unregister a user connection.
        
        Args:
            username: Username
        """
        if username in self.user_sid_map:
            del self.user_sid_map[username]
            logger.info(f"Unregistered user connection: {username}")
    
    async def get_agent_socket_id(self, agent_id: str) -> Optional[str]:
        """Get the socket ID for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Optional[str]: Socket ID, or None if not found
        """
        return self.agent_sid_map.get(agent_id)
    
    async def get_user_socket_id(self, username: str) -> Optional[str]:
        """Get the socket ID for a user.
        
        Args:
            username: Username
            
        Returns:
            Optional[str]: Socket ID, or None if not found
        """
        return self.user_sid_map.get(username)
    
    async def emit_to_agent(self, agent_id: str, event: str, data: Dict[str, Any]) -> bool:
        """Emit an event to an agent.
        
        Args:
            agent_id: Agent ID
            event: Event name
            data: Event data
            
        Returns:
            bool: True if emitted, False otherwise
        """
        socket_id = await self.get_agent_socket_id(agent_id)
        if not socket_id:
            logger.warning(f"Agent not connected: {agent_id}")
            return False
        
        try:
            await self.socket_service.emit(socket_id, event, data)
            logger.debug(f"Emitted {event} to agent {agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error emitting to agent {agent_id}: {str(e)}")
            return False
    
    async def emit_to_user(self, username: str, event: str, data: Dict[str, Any]) -> bool:
        """Emit an event to a user.
        
        Args:
            username: Username
            event: Event name
            data: Event data
            
        Returns:
            bool: True if emitted, False otherwise
        """
        socket_id = await self.get_user_socket_id(username)
        if not socket_id:
            logger.warning(f"User not connected: {username}")
            return False
        
        try:
            await self.socket_service.emit(socket_id, event, data)
            logger.debug(f"Emitted {event} to user {username}")
            return True
        except Exception as e:
            logger.error(f"Error emitting to user {username}: {str(e)}")
            return False
    
    async def emit_command_to_agent(self, agent_id: str, command: Command) -> bool:
        """Emit a command to an agent.
        
        Args:
            agent_id: Agent ID
            command: Command to emit
            
        Returns:
            bool: True if emitted, False otherwise
        """
        command_data = {
            "command_id": command.command_id,
            "command": command.command,
            "with_progress": command.with_progress
        }
        
        return await self.emit_to_agent(agent_id, "execute_command", command_data)
    
    async def emit_command_result_to_user(self, username: str, command: Command) -> bool:
        """Emit a command result to a user.
        
        Args:
            username: Username
            command: Command with results
            
        Returns:
            bool: True if emitted, False otherwise
        """
        command_data = {
            "command_id": command.command_id,
            "command": command.command,
            "agent_id": command.agent_id,
            "exit_code": command.exit_code,
            "stdout": command.stdout,
            "stderr": command.stderr,
            "status": command.status,
            "timestamp": command.timestamp.isoformat() if command.timestamp else None,
            "execution_type": command.execution_type,
            "target": command.target
        }
        
        if command.ai_processing:
            command_data["ai_processing"] = {
                "original_command": command.ai_processing.original_command,
                "processed_command": command.ai_processing.processed_command,
                "validation": command.ai_processing.validation.__dict__ if command.ai_processing.validation else None,
                "optimization": command.ai_processing.optimization.__dict__ if command.ai_processing.optimization else None,
                "enrichment": {
                    "purpose": command.ai_processing.enrichment.purpose if command.ai_processing.enrichment else "",
                    "components": [c.__dict__ for c in command.ai_processing.enrichment.components] if command.ai_processing.enrichment and command.ai_processing.enrichment.components else [],
                    "side_effects": command.ai_processing.enrichment.side_effects if command.ai_processing.enrichment else [],
                    "prerequisites": command.ai_processing.enrichment.prerequisites if command.ai_processing.enrichment else [],
                    "related_commands": command.ai_processing.enrichment.related_commands if command.ai_processing.enrichment else []
                } if command.ai_processing.enrichment else None
            }
        
        return await self.emit_to_user(username, "command_result", command_data)
    
    async def emit_command_progress_to_user(
        self, 
        username: str, 
        command_id: str, 
        agent_id: str, 
        progress: str
    ) -> bool:
        """Emit command progress to a user.
        
        Args:
            username: Username
            command_id: Command ID
            agent_id: Agent ID
            progress: Progress message
            
        Returns:
            bool: True if emitted, False otherwise
        """
        progress_data = {
            "command_id": command_id,
            "agent_id": agent_id,
            "progress": progress
        }
        
        return await self.emit_to_user(username, "command_progress", progress_data)
    
    async def emit_agent_status_to_users(self, agent: Agent) -> None:
        """Emit agent status to all connected users.
        
        Args:
            agent: Agent
        """
        agent_data = {
            "agent_id": agent.agent_id,
            "hostname": agent.hostname,
            "platform": agent.platform,
            "status": agent.status,
            "last_seen": agent.last_seen.isoformat() if agent.last_seen else None,
            "executors": [
                {
                    "type": executor_type,
                    "available": info.get("available", False),
                    "target": info.get("target", {}),
                    "description": info.get("description", "")
                }
                for executor_type, info in agent.executors.items()
            ]
        }
        
        # Broadcast to all connected users
        for username in self.user_sid_map.keys():
            await self.emit_to_user(username, "agent_status", agent_data)
    
    async def register_event_handler(
        self, 
        event: str, 
        handler: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Register an event handler.
        
        Args:
            event: Event name
            handler: Event handler function
        """
        await self.socket_service.register_handler(event, handler)
        logger.info(f"Registered handler for event: {event}")
    
    async def disconnect_client(self, socket_id: str) -> None:
        """Disconnect a client.
        
        Args:
            socket_id: Socket ID
        """
        await self.socket_service.disconnect(socket_id)
        logger.info(f"Disconnected client: {socket_id}")
    
    async def get_connected_clients(self) -> List[str]:
        """Get connected clients.
        
        Returns:
            List[str]: List of connected socket IDs
        """
        return await self.socket_service.get_connected_clients()
    
    async def broadcast(self, event: str, data: Dict[str, Any]) -> None:
        """Broadcast an event to all connected clients.
        
        Args:
            event: Event name
            data: Event data
        """
        await self.socket_service.broadcast(event, data)
        logger.info(f"Broadcasted event: {event}")
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self.agent_sid_map.clear()
        self.user_sid_map.clear()
        await self.socket_service.cleanup()