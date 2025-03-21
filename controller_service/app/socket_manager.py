import socketio
import logging
import asyncio
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from .redis_manager import redis_manager

logger = logging.getLogger("controller")

# Store connected agents (accessible from other modules)
connected_agents = {}

class SocketManager:
    def __init__(self):
        # Check if Redis is enabled
        self.redis_enabled = os.getenv("REDIS_URL") is not None
        
        # Create Socket.IO server with Redis adapter if enabled
        if self.redis_enabled:
            logger.info("Initializing Socket.IO server with Redis adapter")
            self.sio = socketio.AsyncServer(
                async_mode='asgi',
                cors_allowed_origins='*',
                logger=True,
                engineio_logger=True,
                client_manager=socketio.AsyncRedisManager(os.getenv("REDIS_URL"))
            )
        else:
            logger.info("Initializing Socket.IO server without Redis adapter")
            self.sio = socketio.AsyncServer(
                async_mode='asgi',
                cors_allowed_origins='*',
                logger=True,
                engineio_logger=True
            )
        
        self.app = socketio.ASGIApp(self.sio)
        self.clients = {}  # Store connected clients
        self.command_results = {}  # Store command results
        self.command_callbacks = {}  # Store callbacks for command results
        
        # Register event handlers
        self.register_handlers()
        
        # Start background task for real-time feedback
        if self.redis_enabled:
            self.sio.start_background_task(self.process_redis_messages)
    
    async def process_redis_messages(self):
        """Process messages from Redis pub/sub"""
        try:
            # Subscribe to command result channel
            redis_manager.subscribe("command_results")
            
            # Process messages
            while True:
                try:
                    message = redis_manager.get_message()
                    if message:
                        logger.info(f"Received message from Redis: {message}")
                        
                        # Process command result
                        if message.get("type") == "command_result":
                            await self.process_command_result(message.get("data", {}))
                except Exception as e:
                    logger.error(f"Error processing Redis message: {str(e)}")
                    # Try to reconnect
                    try:
                        redis_manager.disconnect()
                        if redis_manager.connect():
                            redis_manager.subscribe("command_results")
                    except Exception as reconnect_error:
                        logger.error(f"Error reconnecting to Redis: {str(reconnect_error)}")
                
                # Sleep to avoid high CPU usage
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in Redis message processing loop: {str(e)}")
            # Don't crash the background task, just log the error
    
    async def process_command_result(self, data):
        """Process a command result from Redis"""
        try:
            logger.info(f"Processing command result: {data}")
            
            # Store the result
            command_id = data.get('command_id', str(datetime.utcnow().timestamp()))
            self.command_results[command_id] = data
            
            # Check if there's a requester SID
            requester_sid = data.get('requester_sid')
            if requester_sid and requester_sid in self.clients:
                # Forward the result to the specific client
                await self.sio.emit('command_result', data, room=requester_sid)
            else:
                # Broadcast to all clients
                await self.sio.emit('command_result', data, room='clients')
            
            # Check if there's a callback waiting for this result
            if command_id in self.command_callbacks:
                callback = self.command_callbacks.pop(command_id)
                callback(data)
        except Exception as e:
            logger.error(f"Error processing command result: {str(e)}")
    
    def register_handlers(self):
        """Register Socket.IO event handlers"""
        @self.sio.event
        async def connect(sid, environ, auth):
            """Handle new connections"""
            try:
                logger.info(f"Connection attempt from {sid} with auth: {auth}")
                
                # Check if authentication is provided
                if not auth or 'token' not in auth:
                    logger.warning(f"Connection attempt without authentication from {sid}")
                    return False
                
                # Determine if this is an agent or a client
                is_agent = auth.get('is_agent', False)
                agent_id = auth.get('agent_id')
                
                logger.info(f"Connection from {sid} - is_agent: {is_agent}, agent_id: {agent_id}")
                
                if is_agent:
                    # This is an agent connection
                    agent_info = auth.get('agent_info', {})
                    
                    # Generate a unique agent ID if not provided
                    agent_id = f"agent-{sid}"
                    
                    # Only store hostname if it's different from agent_id
                    hostname = agent_info.get('hostname', agent_id)
                    
                    # Store agent information
                    connected_agents[sid] = {
                        'sid': sid,
                        'agent_id': agent_id,  # Store the agent ID
                        'connected_at': datetime.utcnow().isoformat(),
                        'agent_info': {
                            'platform': agent_info.get('platform', 'unknown'),
                            'version': agent_info.get('version', 'unknown'),
                            'python_version': agent_info.get('python_version', 'unknown'),
                            'ssh_enabled': agent_info.get('ssh_enabled', False),
                            'ssh_target': agent_info.get('ssh_target', None)
                        }
                    }
                    
                    # Only add hostname if it's different from agent_id
                    if hostname != agent_id:
                        connected_agents[sid]['hostname'] = hostname
                    
                    logger.info(f"Stored agent in connected_agents: {connected_agents[sid]}")
                    logger.info(f"Connected agents: {connected_agents}")
                    
                    # Store agent in Redis if enabled
                    if self.redis_enabled:
                        redis_manager.set(f"agent:{sid}", connected_agents[sid])
                        redis_manager.publish("agent_events", {
                            "type": "agent_connected",
                            "data": connected_agents[sid]
                        })
                    
                    # Join the agents room
                    await self.sio.enter_room(sid, 'agents')
                    
                    # Send connection response
                    await self.sio.emit('connection_response', {
                        'status': 'connected'
                    }, room=sid)
                    
                    return True
                else:
                    # This is a client connection
                    username = auth.get('username', 'anonymous')
                    
                    logger.info(f"Client connected: {username} (SID: {sid})")
                    
                    # Store client information
                    self.clients[sid] = {
                        'sid': sid,
                        'username': username,
                        'connected_at': datetime.utcnow().isoformat()
                    }
                    
                    # Store client in Redis if enabled
                    if self.redis_enabled:
                        redis_manager.set(f"client:{sid}", self.clients[sid])
                    
                    # Join the clients room
                    await self.sio.enter_room(sid, 'clients')
                
                # Send connection response
                await self.sio.emit('connection_response', {
                    'status': 'success',
                    'message': 'Connected successfully',
                    'is_agent': is_agent
                }, room=sid)
                
                return True
            
            except Exception as e:
                logger.error(f"Error handling connection: {str(e)}")
                return False
        
        @self.sio.event
        async def disconnect(sid):
            """Handle disconnections"""
            try:
                # Check if this was an agent
                if sid in connected_agents:
                    agent = connected_agents.pop(sid)
                    logger.info(f"Agent disconnected: {agent['hostname']} (SID: {sid})")
                    
                    # Remove agent from Redis if enabled
                    if self.redis_enabled:
                        redis_manager.delete(f"agent:{sid}")
                        redis_manager.publish("agent_events", {
                            "type": "agent_disconnected",
                            "data": {
                                'sid': sid,
                                'hostname': agent['hostname'],
                                'disconnected_at': datetime.utcnow().isoformat()
                            }
                        })
                    
                    # Notify clients about the agent disconnection
                    await self.sio.emit('agent_disconnected', {
                        'sid': sid,
                        'hostname': agent['hostname'],
                        'disconnected_at': datetime.utcnow().isoformat()
                    }, room='clients')
                
                # Check if this was a client
                elif sid in self.clients:
                    client = self.clients.pop(sid)
                    logger.info(f"Client disconnected: {client['username']} (SID: {sid})")
                    
                    # Remove client from Redis if enabled
                    if self.redis_enabled:
                        redis_manager.delete(f"client:{sid}")
            
            except Exception as e:
                logger.error(f"Error handling disconnection: {str(e)}")
        
        @self.sio.event
        async def command_result(sid, data):
            """Handle command results from agents"""
            try:
                logger.info(f"Received command result from agent {sid}: {data}")
                
                # Store the result
                command_id = data.get('command_id', str(datetime.utcnow().timestamp()))
                self.command_results[command_id] = data
                
                # Store result in Redis if enabled
                if self.redis_enabled:
                    redis_manager.set(f"command_result:{command_id}", data)
                    redis_manager.publish("command_results", {
                        "type": "command_result",
                        "data": data
                    })
                
                # Check if there's a requester SID
                requester_sid = data.get('requester_sid')
                if requester_sid and requester_sid in self.clients:
                    # Forward the result to the specific client
                    await self.sio.emit('command_result', data, room=requester_sid)
                else:
                    # Broadcast to all clients
                    await self.sio.emit('command_result', data, room='clients')
                
                # Check if there's a callback waiting for this result
                if command_id in self.command_callbacks:
                    callback = self.command_callbacks.pop(command_id)
                    callback(data)
            
            except Exception as e:
                logger.error(f"Error handling command result: {str(e)}")
        
        @self.sio.event
        async def command_progress(sid, data):
            """Handle command progress updates from agents"""
            try:
                logger.info(f"Received command progress from agent {sid}: {data}")
                
                # Check if there's a requester SID
                requester_sid = data.get('requester_sid')
                if requester_sid and requester_sid in self.clients:
                    # Forward the progress to the specific client
                    await self.sio.emit('command_progress', data, room=requester_sid)
                else:
                    # Broadcast to all clients
                    await self.sio.emit('command_progress', data, room='clients')
                
                # Publish to Redis if enabled
                if self.redis_enabled:
                    redis_manager.publish("command_progress", {
                        "type": "command_progress",
                        "data": data
                    })
            
            except Exception as e:
                logger.error(f"Error handling command progress: {str(e)}")
        
        @self.sio.event
        async def execute_command_request(sid, data):
            """Handle command execution requests from clients"""
            try:
                if sid not in self.clients:
                    logger.warning(f"Command execution request from non-client: {sid}")
                    await self.sio.emit('command_response', {
                        'status': 'error',
                        'message': 'Not authorized to execute commands'
                    }, room=sid)
                    return
                
                # Validate the request
                if not isinstance(data, dict) or 'command' not in data or 'agent_id' not in data:
                    logger.warning(f"Invalid command execution request from {sid}: {data}")
                    await self.sio.emit('command_response', {
                        'status': 'error',
                        'message': 'Invalid command format'
                    }, room=sid)
                    return
                
                # Get the target agent
                agent_id = data['agent_id']
                agent = self.get_agent(agent_id)
                if not agent:
                    logger.warning(f"Command execution request for non-existent agent {agent_id} from {sid}")
                    await self.sio.emit('command_response', {
                        'status': 'error',
                        'message': f'Agent {agent_id} not found'
                    }, room=sid)
                    return
                
                # Get agent's socket ID
                agent_sid = agent.get('sid')
                if not agent_sid:
                    logger.warning(f"Agent {agent_id} has no socket ID")
                    await self.sio.emit('command_response', {
                        'status': 'error',
                        'message': f'Agent {agent_id} has no socket ID'
                    }, room=sid)
                    return
                
                # Get execution target if specified
                execution_target = data.get('execution_target', 'auto')
                
                # Check if SSH is requested but not available
                if execution_target == "ssh" and not agent.get("agent_info", {}).get("ssh_enabled", False):
                    logger.warning(f"SSH execution requested but agent {agent_id} does not have SSH enabled")
                    await self.sio.emit('command_response', {
                        'status': 'error',
                        'message': f'SSH execution requested but agent does not have SSH enabled'
                    }, room=sid)
                    return
                
                # Generate a unique command ID
                command_id = f"{datetime.utcnow().timestamp()}"
                
                # Store command in Redis if enabled
                if self.redis_enabled:
                    redis_manager.set(f"command:{command_id}", {
                        'command': data['command'],
                        'agent_id': agent_id,
                        'requester_sid': sid,
                        'execution_target': execution_target,
                        'timestamp': datetime.utcnow().isoformat()
                    })
                
                # Forward the command to the agent
                logger.info(f"Forwarding command to agent {agent_id} (SID: {agent_sid}): {data['command']}")
                await self.sio.emit('execute_command', {
                    'command': data['command'],
                    'command_id': command_id,
                    'requester_sid': sid,
                    'execution_target': execution_target
                }, room=agent_sid)
                
                # Send response to the client
                await self.sio.emit('command_response', {
                    'status': 'success',
                    'message': f'Command sent to agent {agent_id}',
                    'command': data['command'],
                    'command_id': command_id,
                    'agent_id': agent_id,
                    'timestamp': datetime.utcnow().isoformat()
                }, room=sid)
            
            except Exception as e:
                logger.error(f"Error handling command execution request: {str(e)}")
                await self.sio.emit('command_response', {
                    'status': 'error',
                    'message': f'Error executing command: {str(e)}'
                }, room=sid)
        
        @self.sio.event
        async def register_agent(sid, data):
            """Handle agent registration."""
            try:
                logger.info(f"Registering agent {sid} with data: {data}")
                
                # Extract agent information
                agent_info = data.get('agent_info', {})
                
                # Generate a unique agent ID
                agent_id = f"agent-{sid}"
                
                # Only store hostname if it's different from agent_id
                hostname = agent_info.get('hostname', agent_id)
                
                # Update agent information (preserve existing data)
                if sid in connected_agents:
                    connected_agents[sid].update({
                        'agent_info': {
                            'platform': agent_info.get('platform', 'unknown'),
                            'version': agent_info.get('version', 'unknown'),
                            'python_version': agent_info.get('python_version', 'unknown'),
                            'ssh_enabled': agent_info.get('ssh_enabled', False),
                            'ssh_target': agent_info.get('ssh_target', None)
                        }
                    })
                    # Only add hostname if it's different from agent_id
                    if hostname != agent_id:
                        connected_agents[sid]['hostname'] = hostname
                    else:
                        connected_agents[sid].pop('hostname', None)  # Remove hostname if it's the same as agent_id
                else:
                    # Store new agent information
                    connected_agents[sid] = {
                        'sid': sid,
                        'agent_id': agent_id,  # Store the agent ID
                        'connected_at': datetime.utcnow().isoformat(),
                        'agent_info': {
                            'platform': agent_info.get('platform', 'unknown'),
                            'version': agent_info.get('version', 'unknown'),
                            'python_version': agent_info.get('python_version', 'unknown'),
                            'ssh_enabled': agent_info.get('ssh_enabled', False),
                            'ssh_target': agent_info.get('ssh_target', None)
                        }
                    }
                    # Only add hostname if it's different from agent_id
                    if hostname != agent_id:
                        connected_agents[sid]['hostname'] = hostname
                
                # Store agent in Redis if enabled
                if self.redis_enabled:
                    redis_manager.set(f"agent:{sid}", connected_agents[sid])
                    redis_manager.publish("agent_events", {
                        "type": "agent_registered",
                        "data": connected_agents[sid]
                    })
                
                # Send registration response with agent ID
                await self.sio.emit('registration_response', {
                    'status': 'success',
                    'message': 'Agent registered successfully',
                    'agent_id': connected_agents[sid]['agent_id']  # Include agent ID in response
                }, room=sid)
                
                logger.info(f"Agent {sid} registered successfully with ID {connected_agents[sid]['agent_id']}")
            except Exception as e:
                logger.error(f"Error registering agent {sid}: {str(e)}")
                await self.sio.emit('registration_response', {
                    'status': 'error',
                    'message': f'Registration failed: {str(e)}'
                }, room=sid)
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get a list of all connected agents"""
        return list(connected_agents.values())
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent"""
        # First, check the in-memory dictionary
        for sid, agent in connected_agents.items():
            if agent.get('agent_id') == agent_id:
                return agent
        
        # If not found and Redis is enabled, check Redis
        if self.redis_enabled:
            try:
                # Try to get the agent from Redis
                agent_data = redis_manager.get(f"agent:{agent_id}")
                if agent_data:
                    logger.info(f"Found agent {agent_id} in Redis: {agent_data}")
                    return agent_data
            except Exception as e:
                logger.error(f"Error retrieving agent from Redis: {str(e)}")
        
        return None
    
    async def execute_command(self, agent_id: str, command: str, execution_target: str = "auto", username: str = "api") -> Optional[Dict[str, Any]]:
        """Execute a command on a specific agent and wait for the result"""
        try:
            agent = self.get_agent(agent_id)
            if not agent:
                logger.warning(f"Command execution request for non-existent agent {agent_id}")
                return None
            
            # Check if SSH is requested but not available
            if execution_target == "ssh" and not agent.get("agent_info", {}).get("ssh_enabled", False):
                logger.warning(f"SSH execution requested but agent {agent_id} does not have SSH enabled")
                return None
            
            # Generate a unique command ID
            command_id = f"{datetime.utcnow().timestamp()}"
            
            # Create a future to wait for the result
            future = asyncio.Future()
            
            # Store the callback
            def callback(result):
                if not future.done():
                    future.set_result(result)
            
            self.command_callbacks[command_id] = callback
            
            # Store command in Redis if enabled
            if self.redis_enabled:
                redis_manager.set(f"command:{command_id}", {
                    'command': command,
                    'agent_id': agent_id,
                    'requester': username,
                    'execution_target': execution_target,
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Send the command to the agent
            logger.info(f"API user {username} executing command on agent {agent_id}: {command}")
            await self.sio.emit('execute_command_event', {
                'command': command,
                'command_id': command_id,
                'requester': username,
                'execution_target': execution_target
            }, room=agent['sid'])
            
            # Wait for the result with a timeout
            try:
                result = await asyncio.wait_for(future, timeout=60)  # 60-second timeout
                return result
            except asyncio.TimeoutError:
                logger.error(f"Timeout waiting for command result from agent {agent_id}")
                self.command_callbacks.pop(command_id, None)
                return {
                    'status': 'error',
                    'message': 'Command execution timed out',
                    'command': command,
                    'agent_id': agent_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return None

# Create a singleton instance
socket_manager = SocketManager()

# Export the Socket.IO server instance for use in other modules
sio = socket_manager.sio 