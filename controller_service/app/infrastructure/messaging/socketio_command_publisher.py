import logging
from typing import Dict, Any, Optional

from app.domain.interfaces.command_publisher import CommandPublisher
from app.infrastructure.messaging.socket_manager import SocketManager

class SocketIOCommandPublisher(CommandPublisher):
    """
    Socket.IO implementation of the command publisher interface.
    """
    
    def __init__(
        self,
        socket_manager: SocketManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Socket.IO command publisher.
        
        Args:
            socket_manager: The Socket.IO manager
            logger: Optional logger
        """
        self.socket_manager = socket_manager
        self.logger = logger or logging.getLogger(__name__)
    
    async def publish_command(
        self,
        agent_id: str,
        command_id: str,
        command_data: Dict[str, Any]
    ) -> bool:
        """
        Publish a command to an agent via Socket.IO.
        
        Args:
            agent_id: The ID of the agent to send the command to
            command_id: The ID of the command
            command_data: The command data
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            # Get the agent's socket ID
            agent_session = await self.socket_manager.get_session(agent_id)
            
            if not agent_session or 'sid' not in agent_session:
                self.logger.error(f"Agent {agent_id} not found or has no socket ID")
                return False
            
            agent_sid = agent_session['sid']
            
            # Prepare the message
            message = {
                "command_id": command_id,
                "data": command_data
            }
            
            # Emit the command to the agent
            await self.socket_manager.emit(
                event="command",
                data=message,
                room=agent_sid
            )
            
            self.logger.info(f"Published command {command_id} to agent {agent_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error publishing command {command_id} to agent {agent_id}: {str(e)}")
            return False
    
    async def publish_command_result(
        self,
        requester_id: str,
        command_id: str,
        result: Dict[str, Any],
        status: str,
        error: Optional[str] = None
    ) -> bool:
        """
        Publish a command result to a requester via Socket.IO.
        
        Args:
            requester_id: The ID of the requester
            command_id: The ID of the command
            result: The command result
            status: The status of the command (success, error, etc.)
            error: Optional error message
            
        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            # Get the requester's socket ID
            requester_session = await self.socket_manager.get_session(requester_id)
            
            if not requester_session or 'sid' not in requester_session:
                self.logger.error(f"Requester {requester_id} not found or has no socket ID")
                return False
            
            requester_sid = requester_session['sid']
            
            # Prepare the message
            message = {
                "command_id": command_id,
                "result": result,
                "status": status
            }
            
            # Add error if provided
            if error:
                message["error"] = error
            
            # Emit the result to the requester
            await self.socket_manager.emit(
                event="command_result",
                data=message,
                room=requester_sid
            )
            
            self.logger.info(f"Published result for command {command_id} to requester {requester_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error publishing result for command {command_id} to requester {requester_id}: {str(e)}")
            return False