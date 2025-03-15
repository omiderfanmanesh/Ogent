# Ogent - Real-time Command Execution System

Ogent is a real-time command execution system that allows you to execute commands on remote machines through a secure, centralized controller. It consists of three main components:

1. **Controller Service**: A FastAPI-based web service that authenticates users, manages connections, and routes commands.
2. **Agent Service**: A service that connects to the Controller Service and executes commands on the local machine or via SSH on remote targets.
3. **Redis Service**: A message broker and caching service that facilitates communication between components.

## Features

- **Real-time Command Execution**: Execute commands on remote machines in real-time.
- **Authentication and Authorization**: Secure access with JWT-based authentication.
- **WebSocket Communication**: Efficient, bidirectional communication between the Controller and Agents.
- **Docker Support**: Run the system in Docker containers for easy deployment.
- **SSH Command Execution**: Execute commands on remote machines via SSH.
- **API Access**: RESTful API for integration with other systems.
- **Real-time Feedback**: Get real-time progress updates during command execution.
- **Redis Integration**: Scalable communication with Redis pub/sub for distributed deployments.
- **AI-powered Command Processing**: Validate, optimize, and enrich commands using LangChain and OpenAI.
- **Ubuntu Target**: Ready-to-use Ubuntu container with SSH for testing and development.
- **Customizable Redis**: Dedicated Redis service with configurable settings for optimal performance.

## Architecture

The Ogent system follows Domain-Driven Design (DDD) principles with a clean architecture approach:

```
┌───────────────────────────────────────────────────────────┐
│                   Presentation Layer                       │
│                                                           │
│   API Routes (FastAPI)          API Models (Pydantic)     │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                   Application Layer                        │
│                                                           │
│   AgentManager             ClientService                  │
│                                                           │
│   CommandRequestDTO        CommandResponseDTO             │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                     Domain Layer                          │
│                                                           │
│   Command Model            Executor Model                 │
│                                                           │
│   CommandExecutorInterface                                │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                      │
│                                                           │
│   BaseExecutor             LocalExecutor                  │
│                                                           │
│   SSHExecutor              Config                         │
│                                                           │
│   Container (DI)                                          │
└───────────────────────────────────────────────────────────┘
```

### Domain-Driven Design Layers

1. **Domain Layer**: Contains the core business logic and entities
   - Models: Command, Executor
   - Interfaces: CommandExecutorInterface

2. **Application Layer**: Contains the use cases and application services
   - Services: AgentManager, ClientService
   - DTOs: CommandRequestDTO, CommandResponseDTO

3. **Infrastructure Layer**: Contains technical details and implementations
   - Executors: BaseExecutor, LocalExecutor, SSHExecutor
   - Config: Configuration settings
   - Container: Dependency injection

4. **Presentation Layer**: Contains the user interface and API
   - API: FastAPI routes and models

### Benefits of DDD Architecture

- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Components can be tested in isolation
- **Maintainability**: Easier to understand and modify
- **Extensibility**: New features can be added without modifying existing code
- **Dependency Inversion**: Higher layers depend on abstractions, not concrete implementations

## System Architecture and Data Flow

### System Components

1. **Controller Service**: The central management service that handles:
   - User authentication and authorization
   - Agent registration and management
   - Command distribution and routing
   - Result aggregation and storage
   - Optional AI processing of commands

2. **Agent Service**: Deployed on target systems to:
   - Execute commands locally or via SSH
   - Report results back to the controller
   - Provide real-time progress updates
   - Manage connection state and reconnection

3. **Redis Service**: Provides infrastructure for:
   - Message passing between services
   - Caching command results and agent information
   - Socket.IO adapter for scaling the Controller Service
   - Pub/Sub for real-time updates

### Data Flow in the Ogent System

#### 1. Agent Authentication Flow

```
Agent Service                                Controller Service
     |                                              |
     |  POST /token (username, password)            |
     |--------------------------------------------->|
     |                                              |
     |  Response: JWT token                         |
     |<---------------------------------------------|
     |                                              |
     |  Socket.IO connect (with token)              |
     |--------------------------------------------->|
     |                                              |
     |  Connection established                      |
     |<---------------------------------------------|
```

1. The Agent Service authenticates with the Controller Service by sending credentials
2. The Controller Service validates credentials and returns a JWT token
3. The Agent Service establishes a Socket.IO connection using the token
4. The Controller Service registers the agent and confirms the connection

#### 2. Command Execution Flow

```
User                  Controller Service                Agent Service
  |                          |                               |
  | Execute command          |                               |
  |------------------------->|                               |
  |                          | Socket.IO "execute_command"   |
  |                          |------------------------------>|
  |                          |                               |
  |                          |                               | Execute command
  |                          |                               | using appropriate
  |                          |                               | executor
  |                          |                               |
  |                          | Socket.IO "command_progress"  |
  |                          |<------------------------------|
  |                          |                               |
  | Real-time progress       |                               |
  |<-------------------------|                               |
  |                          |                               |
  |                          | Socket.IO "command_result"    |
  |                          |<------------------------------|
  |                          |                               |
  | Command result           |                               |
  |<-------------------------|                               |
```

1. A user sends a command execution request to the Controller Service
2. The Controller Service:
   - Validates the request
   - Optionally processes the command with AI (if enabled)
   - Generates a unique command ID
   - Forwards the command to the appropriate Agent Service via Socket.IO

3. The Agent Service:
   - Receives the command
   - Selects the appropriate executor (local or SSH)
   - Executes the command
   - Sends real-time progress updates back to the Controller Service
   - Sends the final result back to the Controller Service

4. The Controller Service:
   - Forwards progress updates to the user
   - Stores the command result
   - Forwards the final result to the user

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional)
- OpenAI API Key (optional, for AI features)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ogent.git
cd ogent
```

2. Set up the Controller Service:
```bash
cd controller_service
pip install -r requirements.txt
cp .env.example .env  # Edit the .env file with your settings
```

3. Set up the Agent Service:
```bash
cd agent_service
pip install -r requirements.txt
cp .env.example .env  # Edit the .env file with your settings
```

4. Set up the Redis Service (optional, if not using Docker):
```bash
cd redis_service
cp .env.example .env  # Edit the .env file with your settings
```

### Running with Docker

1. Set your OpenAI API key (optional):
```bash
export OPENAI_API_KEY=your-api-key
```

2. Build and start the containers:
```bash
docker-compose up -d
```

3. Access the Controller Service at http://localhost:8001

### Running Locally

1. Start Redis (optional):
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

2. Start the Controller Service:
```bash
cd controller_service
python run.py
```

3. Start the Agent Service:
```bash
cd agent_service
python agent.py
```

## Configuration

### Controller Service

Edit the `.env` file in the `controller_service` directory:

```
# Server settings
HOST=0.0.0.0
PORT=8001

# Security settings
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Admin user
ADMIN_USERNAME=admin
ADMIN_PASSWORD=password

# Redis settings
REDIS_URL=redis://localhost:6379/0

# OpenAI settings
OPENAI_API_KEY=your-openai-api-key
```

### Agent Service

Edit the `.env` file in the `agent_service` directory:

```
# Controller settings
CONTROLLER_URL=http://localhost:8001
AGENT_USERNAME=admin
AGENT_PASSWORD=password

# Connection settings
RECONNECT_DELAY=5
MAX_RECONNECT_ATTEMPTS=10

# Redis settings
REDIS_URL=redis://localhost:6379/0

# SSH settings
SSH_ENABLED=false
SSH_HOST=192.168.1.100
SSH_PORT=22
SSH_USERNAME=ubuntu
SSH_PASSWORD=password
SSH_KEY_PATH=~/.ssh/id_rsa
SSH_TIMEOUT=10
```

## API Documentation

### Authentication

```bash
# Get authentication token
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin&password=password

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### List Agents

```bash
GET /agents
Authorization: Bearer <token>

Response:
[
  {
    "sid": "1234567890",
    "agent_id": "agent-1234567890",
    "connected_at": "2023-01-01T00:00:00.000000",
    "agent_info": {
      "platform": "Linux",
      "version": "5.10.0",
      "python": "3.9.5",
      "ssh_enabled": true,
      "ssh_target": "ubuntu@192.168.1.100"
    }
  }
]
```

### Execute Command

```bash
POST /agents/{agent_id}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "command": "echo 'Hello, World!'",
  "execution_target": "auto",
  "use_ai": true,
  "system": "Linux",
  "context": "Server administration"
}

Response:
{
  "status": "success",
  "command": "echo 'Hello, World!'",
  "result": {
    "command": "echo 'Hello, World!'",
    "exit_code": 0,
    "stdout": "Hello, World!\n",
    "stderr": "",
    "timestamp": "2023-01-01T00:00:00.000000",
    "execution_type": "local",
    "target": "agent-1"
  }
}
```

### Analyze Command

```bash
POST /agents/{agent_id}/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "command": "rm -rf /",
  "system": "Linux",
  "context": "Server administration"
}

Response:
{
  "command": "rm -rf /",
  "processed_command": "rm -rf /",
  "validation": {
    "safe": false,
    "risk_level": "high",
    "risks": [
      "This command will delete all files and directories on the system",
      "System will become unusable",
      "Data loss is permanent and unrecoverable"
    ],
    "suggestions": [
      "Use 'rm -rf' with specific directories only",
      "Add safeguards like '--preserve-root' option",
      "Consider using less destructive commands"
    ]
  }
}
```

## WebSocket Events

### Client to Controller

- `execute_command_request`: Execute a command on an agent
```json
{
  "command": "echo 'Hello, World!'",
  "agent_id": "1234567890",
  "execution_target": "auto"
}
```

### Controller to Client

- `agent_connected`: Notification when an agent connects
- `agent_disconnected`: Notification when an agent disconnects
- `command_response`: Response to a command execution request
- `command_result`: Result of a command execution
- `command_progress`: Progress updates during command execution

### Controller to Agent

- `execute_command_event`: Request to execute a command
```json
{
  "command": "echo 'Hello, World!'",
  "command_id": "1234567890",
  "requester_sid": "0987654321",
  "execution_target": "auto"
}
```

### Agent to Controller

- `command_result`: Result of a command execution
```json
{
  "status": "success",
  "command": "echo 'Hello, World!'",
  "command_id": "1234567890",
  "result": {
    "command": "echo 'Hello, World!'",
    "exit_code": 0,
    "stdout": "Hello, World!\n",
    "stderr": "",
    "timestamp": "2023-01-01T00:00:00.000000",
    "execution_type": "ssh",
    "target": "ubuntu@192.168.1.100"
  }
}
```

## Best Practices

### Agent Implementation
- Always handle connection errors gracefully
- Implement proper reconnection logic
- Store agent ID received from controller
- Validate commands before execution

### Controller Implementation
- Validate all incoming requests
- Implement proper error handling
- Use appropriate logging levels
- Handle timeouts properly

### Security Considerations
- Never store sensitive information in plain text
- Validate all user inputs
- Implement proper access control
- Use secure communication channels

## Troubleshooting

### Common Issues

1. Agent Connection Issues
   - Check network connectivity
   - Verify authentication credentials
   - Check logs for detailed error messages

2. Command Execution Problems
   - Verify agent is connected
   - Check command syntax
   - Review execution target settings

3. Redis Connection Issues
   - Verify Redis URL
   - Check Redis service status
   - Ensure proper Redis configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 