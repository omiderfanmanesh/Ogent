# Agent Service

The Agent Service is a component of the Ogent application that provides command execution capabilities on local and remote systems. It follows Domain-Driven Design (DDD) principles with a clean architecture approach.

## Architecture

The application is structured according to the following layers:

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

### 1. Domain Layer

The core business logic and entities of the application.

- **Models**: Core domain entities
  - `Command`: Represents a command to be executed
  - `Executor`: Represents a command executor

- **Interfaces**: Abstractions for domain services
  - `CommandExecutorInterface`: Interface for command executors

### 2. Application Layer

The use cases and application services that orchestrate the domain.

- **Services**: Application services
  - `AgentManager`: Manages command execution and executors
  - `ClientService`: Handles communication with the controller service

- **DTOs**: Data Transfer Objects
  - `CommandRequestDTO`: DTO for command requests
  - `CommandResponseDTO`: DTO for command responses

### 3. Infrastructure Layer

The technical details and implementations of the domain interfaces.

- **Executors**: Command executor implementations
  - `BaseExecutor`: Base class for command executors
  - `LocalExecutor`: Executes commands locally
  - `SSHExecutor`: Executes commands via SSH

- **Config**: Configuration settings
  - `Config`: Configuration class for the agent service

- **Container**: Dependency injection
  - `Container`: Dependency injection container

### 4. Presentation Layer

The user interface and API of the application.

- **API**: FastAPI routes and models
  - `routes.py`: API routes for the agent service
  - `models.py`: API models for request/response validation

## Role in the Ogent System

The Agent Service plays a critical role in the Ogent system by providing command execution capabilities on target systems. It interacts with the Controller Service to receive commands, execute them, and report results.

### Communication with Controller Service

The Agent Service communicates with the Controller Service using the following flow:

1. **Authentication**:
   - The Agent Service authenticates with the Controller Service using username/password
   - It receives a JWT token that is used for subsequent WebSocket connections
   - It establishes a Socket.IO connection with the Controller Service

2. **Registration**:
   - Upon connection, the Agent Service registers itself with the Controller Service
   - It provides information about its capabilities, including available executors
   - The Controller Service assigns a unique ID to the Agent Service

3. **Command Execution**:
   - The Agent Service receives command execution requests via Socket.IO
   - It selects the appropriate executor (local or SSH) based on the request
   - It executes the command and captures stdout, stderr, and exit code
   - It sends real-time progress updates back to the Controller Service
   - It sends the final result back to the Controller Service

4. **Status Updates**:
   - The Agent Service periodically sends status updates to the Controller Service
   - It reports changes in its configuration or capabilities
   - It handles reconnection if the connection to the Controller Service is lost

### Command Execution Process

When the Agent Service receives a command execution request:

1. The `ClientService` receives the Socket.IO event and extracts the command details
2. It calls the `AgentManager` to execute the command
3. The `AgentManager` selects the appropriate executor based on the request
4. The executor (local or SSH) executes the command and captures the output
5. Progress updates are sent back to the Controller Service in real-time
6. The final result is sent back to the Controller Service when execution completes

### Executors

The Agent Service supports multiple executor types:

1. **LocalExecutor**: Executes commands on the local system
   - Uses Python's `subprocess` module to execute commands
   - Captures stdout, stderr, and exit code
   - Provides real-time progress updates

2. **SSHExecutor**: Executes commands on remote systems via SSH
   - Uses `asyncssh` to establish SSH connections
   - Executes commands on the remote system
   - Captures stdout, stderr, and exit code
   - Provides real-time progress updates

The executor selection is based on the command request:
- If `executor_type` is "auto", it uses SSH if available, otherwise local
- If `executor_type` is "local", it forces local execution
- If `executor_type` is "ssh", it forces SSH execution (fails if SSH is not available)

## Dependency Injection

The application uses a simple dependency injection container to manage dependencies between layers. This ensures that:

1. Higher layers depend on abstractions, not concrete implementations
2. Dependencies are injected rather than created directly
3. Components can be easily replaced or mocked for testing

## Running the Service

The service can be run in three modes:

1. **API Mode**: Only runs the API server
   ```
   python main.py --mode api
   ```

2. **Agent Mode**: Only runs the agent client
   ```
   python main.py --mode agent
   ```

3. **Both Mode**: Runs both the API server and agent client (default)
   ```
   python main.py
   ```

## API Endpoints

- `GET /agent/info`: Get agent information
- `GET /agent/executors`: Get available executors
- `GET /agent/history`: Get command execution history
- `POST /agent/execute`: Execute a command
- `WebSocket /agent/execute/ws`: Execute a command with WebSocket progress updates

## Authentication

The API uses OAuth2 password bearer authentication. To get an access token:

```
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin&password=password
```

Use the token in subsequent requests:

```
GET /agent/info
Authorization: Bearer <token>
``` 