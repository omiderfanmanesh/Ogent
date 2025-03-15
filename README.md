# Ogent - Agent-Based Command Execution System

Ogent is a distributed command execution system that allows you to manage and execute commands on multiple agents from a centralized controller. It features real-time communication, secure authentication, and AI-powered command analysis.

## Features

### Agent Management
- Real-time agent connection and status monitoring
- Unique agent identification with automatic ID generation
- Support for both local and SSH command execution
- Detailed agent information including platform, version, and capabilities

### Command Execution
- Execute commands on specific agents
- Choose between local or SSH execution
- Real-time command progress and result updates
- Command execution timeout handling

### Security
- JWT-based authentication for API access
- Secure WebSocket connections with authentication
- Optional AI-powered command validation and risk assessment
- Role-based access control

### AI Integration
- Command analysis and validation
- Risk assessment for command execution
- Command optimization and improvement suggestions
- Context-aware command processing

### Scalability
- Redis support for distributed deployments
- Pub/Sub messaging for real-time updates
- Stateless controller design
- Horizontal scaling capability

## Recent Updates

### Agent Identification Enhancement
- Implemented unique agent IDs in the format `agent-{sid}`
- Optimized hostname storage by only storing when different from agent ID
- Improved agent registration response with agent ID confirmation
- Streamlined agent information structure

### API Improvements
- Enhanced `/agents` endpoint response format
- Added detailed agent information in responses
- Implemented efficient data storage and retrieval
- Added command analysis endpoints

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ogent.git
cd ogent
```

2. Build and start the services:
```bash
docker-compose build
docker-compose up -d
```

## Configuration

### Environment Variables
- `REDIS_URL`: Redis connection URL (optional)
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `JWT_ALGORITHM`: Algorithm for JWT token generation (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time in minutes

### Docker Configuration
The project includes two main services:
- `controller`: The central management service
- `agent`: The command execution service

## API Documentation

### Authentication
```bash
# Get authentication token
curl -X POST http://localhost:8001/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=password"
```

### Agent Management
```bash
# List all agents
curl -H "Authorization: Bearer {token}" http://localhost:8001/agents

# Get specific agent
curl -H "Authorization: Bearer {token}" http://localhost:8001/agents/{agent_id}
```

### Command Execution
```bash
# Execute command on agent
curl -X POST http://localhost:8001/agents/{agent_id}/execute \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la", "execution_target": "auto"}'

# Analyze command without execution
curl -X POST http://localhost:8001/agents/{agent_id}/analyze \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"command": "rm -rf /", "system": "Linux"}'
```

## Development

### Project Structure
```
ogent/
├── controller_service/
│   ├── app/
│   │   ├── routes/
│   │   ├── socket_manager.py
│   │   ├── auth.py
│   │   └── main.py
│   └── Dockerfile
├── agent_service/
│   ├── agent/
│   │   ├── client.py
│   │   └── executor.py
│   └── Dockerfile
└── docker-compose.yml
```

### Adding New Features
1. Follow the existing code structure
2. Implement proper error handling
3. Add appropriate logging
4. Update tests if applicable
5. Document changes in the README

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