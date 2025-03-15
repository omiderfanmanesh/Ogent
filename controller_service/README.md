# Controller Service

The Controller Service is the central management component of the Ogent application that handles user authentication, agent management, command distribution, and result aggregation. It follows Domain-Driven Design (DDD) principles with a clean architecture approach.

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
│   AgentService             CommandService                 │
│                                                           │
│   UserService              AuthService                    │
│                                                           │
│   AIService                SocketService                  │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                     Domain Layer                          │
│                                                           │
│   Agent Model              Command Model                  │
│                                                           │
│   User Model               Repository Interfaces          │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌───────────────────────────────────────────────────────────┐
│                  Infrastructure Layer                      │
│                                                           │
│   Repositories             Socket.IO Service              │
│                                                           │
│   Redis Messaging          AI Service Implementation      │
│                                                           │
│   Container (DI)                                          │
└───────────────────────────────────────────────────────────┘
```

### 1. Domain Layer

The core business logic and entities of the application.

- **Models**: Core domain entities
  - `Agent`: Represents a connected agent
  - `Command`: Represents a command to be executed
  - `User`: Represents a user of the system

- **Interfaces**: Abstractions for domain services
  - `AgentRepositoryInterface`: Interface for agent storage
  - `CommandRepositoryInterface`: Interface for command storage
  - `UserRepositoryInterface`: Interface for user storage
  - `SocketServiceInterface`: Interface for socket communication
  - `AIServiceInterface`: Interface for AI command processing
  - `MessagingServiceInterface`: Interface for messaging

### 2. Application Layer

The use cases and application services that orchestrate the domain.

- **Services**: Application services
  - `AgentService`: Manages agent registration and information
  - `CommandService`: Manages command execution and results
  - `UserService`: Manages user accounts and authentication
  - `AuthService`: Handles authentication and token generation
  - `AIService`: Processes commands with AI
  - `SocketService`: Manages Socket.IO communication

- **DTOs**: Data Transfer Objects
  - `AgentDTO`: DTO for agent information
  - `CommandRequestDTO`: DTO for command requests
  - `CommandResponseDTO`: DTO for command responses
  - `UserDTO`: DTO for user information

### 3. Infrastructure Layer

The technical details and implementations of the domain interfaces.

- **Repositories**: Repository implementations
  - `InMemoryAgentRepository`: In-memory implementation of agent repository
  - `InMemoryCommandRepository`: In-memory implementation of command repository
  - `InMemoryUserRepository`: In-memory implementation of user repository

- **Services**: Service implementations
  - `SocketIOService`: Socket.IO implementation of socket service
  - `OpenAIService`: OpenAI implementation of AI service
  - `RedisMessagingService`: Redis implementation of messaging service

- **Container**: Dependency injection
  - `Container`: Dependency injection container

### 4. Presentation Layer

The user interface and API of the application.

- **API**: FastAPI routes and models
  - `routes/`: API routes for the controller service
  - `models/`: API models for request/response validation

## Role in the Ogent System

The Controller Service is the central hub of the Ogent system, responsible for coordinating all activities between users and agents.

### User Interaction

1. **Authentication**:
   - Users authenticate with the Controller Service to obtain a JWT token
   - The token is used for subsequent API requests and WebSocket connections

2. **Agent Management**:
   - Users can view connected agents and their capabilities
   - Users can register new agents and unregister existing ones

3. **Command Execution**:
   - Users can send commands to specific agents
   - Users receive real-time progress updates during command execution
   - Users receive the final result when command execution completes

### Agent Interaction

1. **Authentication**:
   - Agents authenticate with the Controller Service to obtain a JWT token
   - The token is used for subsequent WebSocket connections

2. **Registration**:
   - Agents register with the Controller Service upon connection
   - They provide information about their capabilities and available executors
   - The Controller Service assigns a unique ID to each agent

3. **Command Execution**:
   - The Controller Service forwards command execution requests to agents
   - It receives real-time progress updates from agents
   - It receives the final result when command execution completes
   - It forwards progress updates and results to the requesting user

### AI Command Processing

If AI processing is enabled:

1. The Controller Service sends the command to the AI service
2. The AI service:
   - Validates the command for security risks
   - Optimizes the command for better performance
   - Enriches the command with additional context
   - Returns the processed command
3. The Controller Service then sends the processed command to the agent

### Scaling and Reliability

For scaling and reliability, the Controller Service can use:

1. **Redis**:
   - As a Socket.IO adapter for scaling across multiple instances
   - For message passing between services
   - For caching command results

2. **Persistence**:
   - Repository implementations can be swapped to use persistent storage
   - Command history and results can be stored for later retrieval

## API Endpoints

- `POST /token`: Authenticate and get a JWT token
- `GET /agents`: Get all connected agents
- `GET /agents/{agent_id}`: Get information about a specific agent
- `POST /agents/{agent_id}/execute`: Execute a command on a specific agent
- `GET /commands`: Get command history
- `GET /commands/{command_id}`: Get information about a specific command
- `WebSocket /ws`: WebSocket endpoint for real-time communication

## Authentication

The API uses OAuth2 password bearer authentication. To get an access token:

```
POST /token
Content-Type: application/x-www-form-urlencoded

username=admin&password=password
```

Use the token in subsequent requests:

```
GET /agents
Authorization: Bearer <token>
```

## Running the Service

The service can be run using:

```
python run.py
```

Or with Docker:

```
docker-compose up controller
```

## Configuration

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