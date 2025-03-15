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

The Ogent system consists of two main services that work together to provide secure, real-time command execution capabilities:

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

#### 3. Command Execution Details

When the Agent Service receives a command:

1. The `ClientService` handles the Socket.IO event and calls the `AgentManager`
2. The `AgentManager`:
   - Determines which executor to use (local or SSH)
   - Calls the appropriate executor to run the command
   - Tracks command history
   - Handles errors and timeouts

3. The executor (either `LocalExecutor` or `SSHExecutor`):
   - Executes the command on the target system
   - Captures stdout, stderr, and exit code
   - Provides real-time progress updates via callback

4. The result flows back through the same path:
   - Executor → AgentManager → ClientService → Controller Service → User

#### 4. Optional AI Processing

If AI processing is enabled:

1. The Controller Service sends the command to the AI service
2. The AI service:
   - Validates the command for security risks
   - Optimizes the command for better performance
   - Enriches the command with additional context
   - Returns the processed command

3. The Controller Service then sends the processed command to the Agent Service

### Scaling and Reliability

For scaling and reliability, the system can use:

1. **Redis**:
   - As a Socket.IO adapter for scaling the Controller Service
   - For message passing between services
   - For caching command results
   - Configurable for different deployment scenarios

2. **Reconnection Logic**:
   - Agents automatically reconnect to the Controller Service if disconnected
   - Commands are retried if execution fails

## Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (optional)
- OpenAI API Key (optional, for AI features)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ogent.git
   cd ogent
   ```

2. Set up the Controller Service:
   ```
   cd controller_service
   pip install -r requirements.txt
   cp .env.example .env  # Edit the .env file with your settings
   ```

3. Set up the Agent Service:
   ```
   cd agent_service
   pip install -r requirements.txt
   cp .env.example .env  # Edit the .env file with your settings
   ```

4. Set up the Redis Service (optional, if not using Docker):
   ```
   cd redis_service
   cp .env.example .env  # Edit the .env file with your settings
   ```

### Running with Docker

1. Set your OpenAI API key (optional):
   ```
   export OPENAI_API_KEY=your-api-key
   ```

2. Build and start the containers:
   ```
   docker-compose up -d
   ```

3. Access the Controller Service at http://localhost:8000

### Running Locally

1. Start Redis (optional):
   ```
   docker run -d -p 6379:6379 redis:7-alpine
   ```

2. Start the Controller Service:
   ```
   cd controller_service
   python run.py
   ```

3. Start the Agent Service:
   ```
   cd agent_service
   python agent.py
   ```

## Configuration

### Controller Service

Edit the `.env` file in the `controller_service` directory:

```
# Server settings
HOST=0.0.0.0
PORT=8000

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
CONTROLLER_URL=http://localhost:8000
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

## SSH Command Execution

The Agent Service can execute commands via SSH on remote targets. To enable SSH command execution:

1. Set `SSH_ENABLED=true` in the Agent Service `.env` file.
2. Configure the SSH connection parameters:
   - `SSH_HOST`: The hostname or IP address of the SSH target.
   - `SSH_PORT`: The SSH port (default: 22).
   - `SSH_USERNAME`: The SSH username.
   - `SSH_PASSWORD`: The SSH password (optional if using key-based authentication).
   - `SSH_KEY_PATH`: The path to the SSH private key (default: ~/.ssh/id_rsa).
   - `SSH_TIMEOUT`: The SSH connection timeout in seconds (default: 10).

3. When executing commands, specify the execution target:
   - `auto`: Automatically use SSH if enabled, otherwise use local execution.
   - `local`: Force local execution.
   - `ssh`: Force SSH execution.

## Real-time Feedback

Ogent provides real-time feedback during command execution:

1. **Progress Updates**: Receive progress updates during command execution.
2. **Stdout/Stderr Streaming**: See command output as it's generated.
3. **Status Updates**: Get status updates (running, completed, error).

## Redis Integration

Ogent can use Redis for scalable communication:

1. **Pub/Sub**: Use Redis pub/sub for command execution and results.
2. **Distributed Deployment**: Support for distributed deployments with multiple controllers and agents.
3. **Persistence**: Store command history and results in Redis.

## AI-powered Command Processing

Ogent can use LangChain and OpenAI to process commands:

1. **Command Validation**: Validate commands for security risks.
2. **Command Optimization**: Optimize commands for better performance and readability.
3. **Command Enrichment**: Enrich commands with additional context and information.

To use AI features:

1. Set your OpenAI API key in the Controller Service `.env` file.
2. When executing commands, set `use_ai=true` in the request.
3. Use the `/agents/{agent_id}/analyze` endpoint to analyze commands without executing them.

## API Usage

### Authentication

```
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin&password=password
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### List Agents

```
GET /agents
Authorization: Bearer <token>
```

Response:
```json
[
  {
    "sid": "1234567890",
    "hostname": "agent-1",
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

```
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
```

Response:
```json
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
  },
  "ai_processing": {
    "original_command": "echo 'Hello, World!'",
    "processed_command": "echo 'Hello, World!'",
    "validation": {
      "safe": true,
      "risk_level": "low",
      "risks": [],
      "suggestions": []
    },
    "optimization": {
      "optimized_command": "echo 'Hello, World!'",
      "improvements": [],
      "explanation": "The command is already optimal."
    },
    "enrichment": {
      "purpose": "Print the text 'Hello, World!' to the standard output",
      "components": [
        {
          "component": "echo",
          "function": "Print the arguments to the standard output"
        },
        {
          "component": "'Hello, World!'",
          "function": "The text to be printed"
        }
      ],
      "side_effects": [],
      "prerequisites": [],
      "related_commands": ["printf", "cat"]
    }
  },
  "timestamp": "2023-01-01T00:00:00.000000"
}
```

### Analyze Command

```
POST /agents/{agent_id}/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "command": "rm -rf /",
  "system": "Linux",
  "context": "Server administration"
}
```

Response:
```json
{
  "command": "rm -rf /",
  "processed_command": "rm -rf /",
  "ai_processing": {
    "original_command": "rm -rf /",
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
    },
    "optimization": {
      "optimized_command": "rm -rf /",
      "improvements": ["Command not optimized due to security risks"],
      "explanation": "Command not optimized due to security risks"
    },
    "enrichment": {
      "purpose": "Delete all files and directories on the system",
      "components": [
        {
          "component": "rm",
          "function": "Remove files or directories"
        },
        {
          "component": "-r",
          "function": "Recursively remove directories and their contents"
        },
        {
          "component": "-f",
          "function": "Force removal without prompting for confirmation"
        },
        {
          "component": "/",
          "function": "The root directory of the filesystem"
        }
      ],
      "side_effects": [
        "Complete system destruction",
        "Data loss",
        "System will become unusable"
      ],
      "prerequisites": [
        "Root or sudo privileges"
      ],
      "related_commands": ["find", "ls", "mkdir"]
    }
  },
  "agent_id": "1234567890",
  "timestamp": "2023-01-01T00:00:00.000000"
}
```

## WebSocket Events

### Client to Controller

- `execute_command_request`: Execute a command on an agent.
  ```json
  {
    "command": "echo 'Hello, World!'",
    "agent_id": "1234567890",
    "execution_target": "auto"
  }
  ```

### Controller to Client

- `agent_connected`: Notification when an agent connects.
- `agent_disconnected`: Notification when an agent disconnects.
- `command_response`: Response to a command execution request.
- `command_result`: Result of a command execution.
- `command_progress`: Progress updates during command execution.

### Controller to Agent

- `execute_command_event`: Request to execute a command.
  ```json
  {
    "command": "echo 'Hello, World!'",
    "command_id": "1234567890",
    "requester_sid": "0987654321",
    "execution_target": "auto"
  }
  ```

### Agent to Controller

- `command_result`: Result of a command execution.
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
    },
    "requester_sid": "0987654321",
    "timestamp": "2023-01-01T00:00:00.000000"
  }
  ```

- `command_progress`: Progress updates during command execution.
  ```json
  {
    "command_id": "1234567890",
    "requester_sid": "0987654321",
    "status": "running",
    "progress": 50,
    "stdout": "Processing...\n",
    "message": "Command running",
    "timestamp": "2023-01-01T00:00:00.000000"
  }
  ```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Using Postman

You can interact with the Ogent API using Postman. Here's how to set up and use the main endpoints:

### Setting Up Postman

1. Create a new collection in Postman for Ogent
2. Set up an environment with variables:
   - `base_url`: `http://localhost:8001`
   - `token`: (will be set automatically after authentication)

### Authentication

1. **Get Authentication Token**
   - Method: `POST`
   - URL: `{{base_url}}/token`
   - Headers:
     ```
     Content-Type: application/x-www-form-urlencoded
     ```
   - Body (x-www-form-urlencoded):
     ```
     username: admin
     password: password
     ```
   - Response:
     ```json
     {
       "access_token": "your.jwt.token",
       "token_type": "bearer"
     }
     ```
   - Test Script (to automatically set the token):
     ```javascript
     var jsonData = JSON.parse(responseBody);
     pm.environment.set("token", jsonData.access_token);
     ```

### Available Endpoints

1. **Health Check**
   - Method: `GET`
   - URL: `{{base_url}}/health`
   - No authentication required
   - Response:
     ```json
     {
       "status": "healthy"
     }
     ```

2. **List Connected Agents**
   - Method: `GET`
   - URL: `{{base_url}}/agents`
   - Headers:
     ```
     Authorization: Bearer {{token}}
     ```
   - Response:
     ```json
     {
       "connected_agents": {
         "agent_id": {
           "username": "admin",
           "connected_at": "2025-03-15T21:27:26.089505"
         }
       }
     }
     ```

### Tips for Using Postman

1. **Environment Variables**
   - Create an environment to store variables like `base_url` and `token`
   - Use `{{variable_name}}` syntax to reference variables in requests
   - The token is automatically set after successful authentication

2. **Collection Organization**
   - Group related requests in folders (e.g., "Authentication", "Agents", etc.)
   - Use descriptive names for requests
   - Add examples and documentation to requests

3. **Testing**
   - Use the "Tests" tab to write test scripts
   - Verify response status codes and data
   - Chain requests using environment variables

4. **Troubleshooting**
   - Check the Console in Postman for detailed request/response information
   - Verify the token is being set correctly
   - Ensure all required headers are included 