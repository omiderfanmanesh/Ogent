# Implementation Plan: Controller Service and Agent Service Integration

This document outlines the specific code changes needed to integrate the Controller Service with the Agent Service in the Ogent system.

## Phase 1: Basic Integration

### Controller Service Changes

#### 1. Infrastructure Layer Implementation

Create the infrastructure implementations for the repository interfaces:

**1.1. Create `controller_service/app/infrastructure/repositories/in_memory_agent_repository.py`**

```python
"""In-memory agent repository implementation."""

from typing import Dict, Any, List, Optional
from ...domain.models.agent import Agent
from ...domain.interfaces.agent_repository import AgentRepositoryInterface

class InMemoryAgentRepository(AgentRepositoryInterface):
    """In-memory implementation of the agent repository."""
    
    def __init__(self):
        """Initialize the repository."""
        self.agents: Dict[str, Agent] = {}
        self.sid_to_agent_id: Dict[str, str] = {}
    
    async def add_agent(self, agent: Agent) -> None:
        """Add an agent to the repository."""
        self.agents[agent.agent_id] = agent
        self.sid_to_agent_id[agent.sid] = agent.agent_id
    
    async def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the repository."""
        if agent_id in self.agents:
            sid = self.agents[agent_id].sid
            del self.agents[agent_id]
            if sid in self.sid_to_agent_id:
                del self.sid_to_agent_id[sid]
    
    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)
    
    async def get_agent_by_sid(self, sid: str) -> Optional[Agent]:
        """Get an agent by Socket.IO session ID."""
        agent_id = self.sid_to_agent_id.get(sid)
        if agent_id:
            return self.agents.get(agent_id)
        return None
    
    async def get_all_agents(self) -> List[Agent]:
        """Get all agents."""
        return list(self.agents.values())
    
    async def update_agent(self, agent: Agent) -> None:
        """Update an agent in the repository."""
        if agent.agent_id in self.agents:
            old_sid = self.agents[agent.agent_id].sid
            if old_sid != agent.sid:
                if old_sid in self.sid_to_agent_id:
                    del self.sid_to_agent_id[old_sid]
                self.sid_to_agent_id[agent.sid] = agent.agent_id
            self.agents[agent.agent_id] = agent
```

**1.2. Create `controller_service/app/infrastructure/repositories/in_memory_command_repository.py`**

```python
"""In-memory command repository implementation."""

from typing import Dict, Any, List, Optional
from ...domain.models.command import Command
from ...domain.interfaces.command_repository import CommandRepositoryInterface

class InMemoryCommandRepository(CommandRepositoryInterface):
    """In-memory implementation of the command repository."""
    
    def __init__(self):
        """Initialize the repository."""
        self.commands: Dict[str, Command] = {}
        self.agent_commands: Dict[str, List[str]] = {}
        self.requester_commands: Dict[str, List[str]] = {}
    
    async def add_command(self, command: Command) -> None:
        """Add a command to the repository."""
        self.commands[command.command_id] = command
        
        # Add to agent commands
        if command.agent_id not in self.agent_commands:
            self.agent_commands[command.agent_id] = []
        self.agent_commands[command.agent_id].append(command.command_id)
        
        # Add to requester commands if available
        if command.requester_id:
            if command.requester_id not in self.requester_commands:
                self.requester_commands[command.requester_id] = []
            self.requester_commands[command.requester_id].append(command.command_id)
    
    async def get_command(self, command_id: str) -> Optional[Command]:
        """Get a command by ID."""
        return self.commands.get(command_id)
    
    async def get_commands_by_agent(self, agent_id: str, limit: int = 10) -> List[Command]:
        """Get commands by agent ID."""
        command_ids = self.agent_commands.get(agent_id, [])
        commands = [self.commands[cmd_id] for cmd_id in command_ids if cmd_id in self.commands]
        commands.sort(key=lambda cmd: cmd.timestamp, reverse=True)
        return commands[:limit]
    
    async def get_commands_by_requester(self, requester_id: str, limit: int = 10) -> List[Command]:
        """Get commands by requester ID."""
        command_ids = self.requester_commands.get(requester_id, [])
        commands = [self.commands[cmd_id] for cmd_id in command_ids if cmd_id in self.commands]
        commands.sort(key=lambda cmd: cmd.timestamp, reverse=True)
        return commands[:limit]
    
    async def update_command(self, command: Command) -> None:
        """Update a command in the repository."""
        if command.command_id in self.commands:
            self.commands[command.command_id] = command
    
    async def delete_command(self, command_id: str) -> None:
        """Delete a command from the repository."""
        if command_id in self.commands:
            command = self.commands[command_id]
            
            # Remove from agent commands
            if command.agent_id in self.agent_commands:
                if command_id in self.agent_commands[command.agent_id]:
                    self.agent_commands[command.agent_id].remove(command_id)
            
            # Remove from requester commands
            if command.requester_id and command.requester_id in self.requester_commands:
                if command_id in self.requester_commands[command.requester_id]:
                    self.requester_commands[command.requester_id].remove(command_id)
            
            # Remove command
            del self.commands[command_id]
```

**1.3. Create `controller_service/app/infrastructure/services/socketio_service.py`**

```python
"""Socket.IO service implementation."""

import logging
from typing import Dict, Any, Optional, Callable, Awaitable, List
import socketio

from ...domain.interfaces.socket_service import SocketServiceInterface

logger = logging.getLogger("controller.socketio_service")

class SocketIOService(SocketServiceInterface):
    """Socket.IO implementation of the socket service interface."""
    
    def __init__(self, sio: socketio.AsyncServer):
        """Initialize the service.
        
        Args:
            sio: Socket.IO server instance
        """
        self.sio = sio
    
    async def emit(self, event: str, data: Dict[str, Any], room: Optional[str] = None) -> bool:
        """Emit an event to a room or all connected clients."""
        try:
            await self.sio.emit(event, data, room=room)
            return True
        except Exception as e:
            logger.error(f"Error emitting event {event}: {str(e)}")
            return False
    
    async def join_room(self, sid: str, room: str) -> bool:
        """Join a room."""
        try:
            self.sio.enter_room(sid, room)
            return True
        except Exception as e:
            logger.error(f"Error joining room {room}: {str(e)}")
            return False
    
    async def leave_room(self, sid: str, room: str) -> bool:
        """Leave a room."""
        try:
            self.sio.leave_room(sid, room)
            return True
        except Exception as e:
            logger.error(f"Error leaving room {room}: {str(e)}")
            return False
    
    async def get_rooms(self, sid: str) -> List[str]:
        """Get the rooms a client is in."""
        try:
            return list(self.sio.rooms(sid))
        except Exception as e:
            logger.error(f"Error getting rooms for {sid}: {str(e)}")
            return []
    
    async def get_room_members(self, room: str) -> List[str]:
        """Get the members of a room."""
        try:
            return list(self.sio.manager.get_members(room))
        except Exception as e:
            logger.error(f"Error getting members for room {room}: {str(e)}")
            return []
    
    async def register_handler(self, event: str, handler: Callable[[str, Dict[str, Any]], Awaitable[None]]) -> None:
        """Register an event handler."""
        try:
            @self.sio.on(event)
            async def event_handler(sid, data):
                await handler(sid, data)
        except Exception as e:
            logger.error(f"Error registering handler for {event}: {str(e)}")
    
    async def disconnect(self, sid: str) -> bool:
        """Disconnect a client."""
        try:
            await self.sio.disconnect(sid)
            return True
        except Exception as e:
            logger.error(f"Error disconnecting {sid}: {str(e)}")
            return False
```

#### 2. Dependency Injection Container

**2.1. Create `controller_service/app/infrastructure/container.py`**

```python
"""Dependency injection container."""

import logging
from typing import Dict, Any, Optional
import socketio

from ..domain.interfaces.agent_repository import AgentRepositoryInterface
from ..domain.interfaces.command_repository import CommandRepositoryInterface
from ..domain.interfaces.socket_service import SocketServiceInterface
from ..domain.interfaces.ai_service import AIServiceInterface

from .repositories.in_memory_agent_repository import InMemoryAgentRepository
from .repositories.in_memory_command_repository import InMemoryCommandRepository
from .services.socketio_service import SocketIOService

from ..application.services.agent_service import AgentService
from ..application.services.command_service import CommandService
from ..application.services.socket_service import SocketService
from ..application.services.ai_service import AIService

logger = logging.getLogger("controller.container")

class Container:
    """Dependency injection container."""
    
    def __init__(self, sio: socketio.AsyncServer):
        """Initialize the container.
        
        Args:
            sio: Socket.IO server instance
        """
        self.sio = sio
        self._repositories = {}
        self._services = {}
        
        # Initialize repositories
        self._repositories["agent_repository"] = InMemoryAgentRepository()
        self._repositories["command_repository"] = InMemoryCommandRepository()
        
        # Initialize services
        self._services["socket_service_interface"] = SocketIOService(sio)
        
        # Initialize application services
        self._services["agent_service"] = AgentService(self._repositories["agent_repository"])
        self._services["socket_service"] = SocketService(self._services["socket_service_interface"])
        self._services["ai_service"] = AIService()
        self._services["command_service"] = CommandService(
            self._repositories["command_repository"],
            self._services["ai_service"],
            self._services["socket_service_interface"]
        )
    
    def get_agent_repository(self) -> AgentRepositoryInterface:
        """Get the agent repository."""
        return self._repositories["agent_repository"]
    
    def get_command_repository(self) -> CommandRepositoryInterface:
        """Get the command repository."""
        return self._repositories["command_repository"]
    
    def get_agent_service(self) -> AgentService:
        """Get the agent service."""
        return self._services["agent_service"]
    
    def get_command_service(self) -> CommandService:
        """Get the command service."""
        return self._services["command_service"]
    
    def get_socket_service(self) -> SocketService:
        """Get the socket service."""
        return self._services["socket_service"]
    
    def get_ai_service(self) -> AIService:
        """Get the AI service."""
        return self._services["ai_service"]
```

#### 3. Update Socket Manager

**3.1. Update `controller_service/app/socket_manager.py`**

```python
# Add the following imports
from .infrastructure.container import Container
from .application.services.agent_service import AgentService
from .application.services.command_service import CommandService
from .application.services.socket_service import SocketService
from .application.dtos.command_dto import CommandRequestDTO

# In the SocketManager.__init__ method, add:
self.container = Container(self.sio)
self.agent_service = self.container.get_agent_service()
self.command_service = self.container.get_command_service()
self.socket_service = self.container.get_socket_service()

# Update the handle_connect method:
async def handle_connect(self, sid, environ):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    
    # Get authentication data
    auth = environ.get('HTTP_AUTHORIZATION', '')
    if auth.startswith('Bearer '):
        token = auth[7:]
        # Validate token and get user
        # ...
    
    # Store client connection
    self.clients[sid] = {
        "connected_at": datetime.now().isoformat(),
        "user_id": None  # Set user ID if authenticated
    }

# Update the handle_disconnect method:
async def handle_disconnect(self, sid):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")
    
    # Check if this is an agent
    agent = await self.agent_service.get_agent_by_sid(sid)
    if agent:
        # Unregister agent
        await self.agent_service.unregister_agent(agent.agent_id)
        logger.info(f"Agent unregistered: {agent.agent_id}")
    
    # Remove client
    if sid in self.clients:
        del self.clients[sid]

# Update the handle_register method:
async def handle_register(self, sid, data):
    """Handle agent registration."""
    logger.info(f"Agent registration: {data}")
    
    # Validate data
    if not isinstance(data, dict) or 'agent_id' not in data:
        logger.error("Invalid registration data")
        return
    
    # Register agent
    agent_id = data['agent_id']
    agent_info = data.get('agent_info', {})
    
    agent = await self.agent_service.register_agent(sid, agent_id, agent_info)
    
    # Join agent room
    await self.socket_service.register_agent_connection(agent_id, sid)
    
    # Send registration confirmation
    await self.sio.emit('registration_response', {
        'status': 'success',
        'agent_id': agent_id
    }, room=sid)
    
    logger.info(f"Agent registered: {agent_id}")

# Update the handle_execute_command method:
async def handle_execute_command(self, sid, data):
    """Handle command execution request."""
    logger.info(f"Command execution request: {data}")
    
    # Validate data
    if not isinstance(data, dict) or 'command' not in data or 'agent_id' not in data:
        logger.error("Invalid command execution request")
        return
    
    # Create command request DTO
    command_request = CommandRequestDTO(
        command=data['command'],
        agent_id=data['agent_id'],
        execution_target=data.get('execution_target', 'auto'),
        use_ai=data.get('use_ai', False),
        system=data.get('system', 'Linux'),
        context=data.get('context', 'Server administration'),
        requester_id=sid
    )
    
    # Execute command
    command = await self.command_service.execute_command(command_request)
    
    logger.info(f"Command execution initiated: {command.command_id}")
```

### Agent Service Changes

#### 1. Update Client Service

**1.1. Update `agent_service/agent/application/services/client_service.py`**

```python
# Update the handle_execute_command method:
async def handle_execute_command(self, data):
    """Handle command execution request from the Controller Service."""
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
```

## Phase 2: Enhanced Features

### Controller Service Changes

#### 1. Implement AI Command Processing

**1.1. Update `controller_service/app/application/services/ai_service.py`**

```python
# Implement the AI service interface
from ...domain.interfaces.ai_service import AIServiceInterface

# Create an OpenAI implementation
class OpenAIService(AIServiceInterface):
    """OpenAI implementation of the AI service interface."""
    
    def __init__(self, api_key: str):
        """Initialize the service."""
        import openai
        openai.api_key = api_key
        self.client = openai.Client()
        self._enabled = True
    
    async def validate_command(self, command: str, system: str = "Linux", context: str = "Server administration"):
        """Validate a command for security risks."""
        # Implementation...
    
    async def optimize_command(self, command: str, system: str = "Linux", context: str = "Server administration"):
        """Optimize a command for better performance and readability."""
        # Implementation...
    
    async def enrich_command(self, command: str, system: str = "Linux", context: str = "Server administration"):
        """Enrich a command with additional context and information."""
        # Implementation...
    
    async def process_command(self, command: str, system: str = "Linux", context: str = "Server administration"):
        """Process a command with AI."""
        # Implementation...
    
    @property
    def enabled(self) -> bool:
        """Check if the AI service is enabled."""
        return self._enabled
```

#### 2. Implement Redis Messaging

**2.1. Create `controller_service/app/infrastructure/services/redis_messaging_service.py`**

```python
"""Redis messaging service implementation."""

import logging
import json
import redis.asyncio as redis
from typing import Dict, Any, Optional, Callable, Awaitable

from ...domain.interfaces.messaging_service import MessagingServiceInterface

logger = logging.getLogger("controller.redis_messaging_service")

class RedisMessagingService(MessagingServiceInterface):
    """Redis implementation of the messaging service interface."""
    
    def __init__(self, redis_url: str):
        """Initialize the service."""
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        self.subscribers = {}
        self._connected = True
    
    async def publish(self, channel: str, message: Dict[str, Any]) -> bool:
        """Publish a message to a channel."""
        try:
            message_str = json.dumps(message)
            await self.redis.publish(channel, message_str)
            return True
        except Exception as e:
            logger.error(f"Error publishing to {channel}: {str(e)}")
            return False
    
    async def subscribe(self, channel: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]) -> bool:
        """Subscribe to a channel."""
        try:
            await self.pubsub.subscribe(channel)
            self.subscribers[channel] = callback
            return True
        except Exception as e:
            logger.error(f"Error subscribing to {channel}: {str(e)}")
            return False
    
    async def unsubscribe(self, channel: str) -> bool:
        """Unsubscribe from a channel."""
        try:
            await self.pubsub.unsubscribe(channel)
            if channel in self.subscribers:
                del self.subscribers[channel]
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing from {channel}: {str(e)}")
            return False
    
    async def set(self, key: str, value: Dict[str, Any], expiration: Optional[int] = None) -> bool:
        """Set a key-value pair."""
        try:
            value_str = json.dumps(value)
            if expiration:
                await self.redis.setex(key, expiration, value_str)
            else:
                await self.redis.set(key, value_str)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key}: {str(e)}")
            return False
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get a value by key."""
        try:
            value_str = await self.redis.get(key)
            if value_str:
                return json.loads(value_str)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {str(e)}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key-value pair."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key}: {str(e)}")
            return False
    
    @property
    def connected(self) -> bool:
        """Check if the messaging service is connected."""
        return self._connected
```

### Agent Service Changes

#### 1. Implement Executor Selection

**1.1. Update `agent_service/agent/application/services/agent_manager.py`**

```python
# Update the _get_executor method:
def _get_executor(self, executor_type: str) -> Optional[CommandExecutorInterface]:
    """Get an executor of the specified type."""
    # If auto, determine the best executor to use
    if executor_type == "auto":
        # Try SSH first if available
        if "ssh" in self.executors and self.executors["ssh"].is_available():
            return self.executors["ssh"]
        # Fall back to local
        elif "local" in self.executors:
            return self.executors["local"]
        # No suitable executor found
        else:
            return None
    
    # Get the specified executor if available
    if executor_type in self.executors:
        return self.executors[executor_type]
    
    # No suitable executor found
    return None
```

## Phase 3: Scaling and Reliability

### Controller Service Changes

#### 1. Implement Redis Socket.IO Adapter

**1.1. Update `controller_service/app/main.py`**

```python
# Update the Socket.IO server initialization:
if os.getenv("REDIS_URL"):
    logger.info("Initializing Socket.IO server with Redis adapter")
    sio = socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins='*',
        logger=True,
        engineio_logger=True,
        client_manager=socketio.AsyncRedisManager(os.getenv("REDIS_URL"))
    )
else:
    logger.info("Initializing Socket.IO server without Redis adapter")
    sio = socketio.AsyncServer(
        async_mode='asgi',
        cors_allowed_origins='*',
        logger=True,
        engineio_logger=True
    )
```

### Agent Service Changes

#### 1. Implement Reconnection Logic

**1.1. Update `agent_service/agent/application/services/client_service.py`**

```python
# Update the __init__ method:
def __init__(self, agent_manager: Optional[AgentManager] = None):
    """Initialize the client service."""
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

# Update the start method:
async def start(self):
    """Start the client service."""
    logger.info(f"Starting client service with agent ID: {self.agent_id}")
    
    while True:
        try:
            # Get authentication token
            token = await self.get_auth_token()
            if not token:
                logger.error("Failed to get authentication token")
                await asyncio.sleep(config.reconnect_delay)
                continue
            
            # Connect to the controller service
            await self.sio.connect(
                config.controller_url,
                auth={"agent_id": self.agent_id, "token": token},
                wait_timeout=60
            )
            
            # Wait for disconnect
            await self.sio.wait()
            
            # If we get here, we've been disconnected
            logger.info("Disconnected from controller service")
            
            # Wait before reconnecting
            await asyncio.sleep(config.reconnect_delay)
            
        except Exception as e:
            logger.error(f"Error connecting to controller service: {str(e)}")
            self.connected = False
            
            # Wait before reconnecting
            await asyncio.sleep(config.reconnect_delay)
```

## Testing

### Unit Tests

**1. Controller Service Tests**

Create tests for the controller service components:

- Repository tests
- Service tests
- Socket.IO event handler tests

**2. Agent Service Tests**

Create tests for the agent service components:

- Executor tests
- Agent manager tests
- Client service tests

### Integration Tests

Create integration tests to verify the communication between services:

- Agent registration flow
- Command execution flow
- Error handling

### End-to-End Tests

Create end-to-end tests to verify the complete system:

- Agent connection and registration
- Command execution with different executors
- Real-time progress updates
- AI command processing