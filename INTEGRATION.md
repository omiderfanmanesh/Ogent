# Integration Guide: Controller Service and Agent Service

This document outlines the approach for integrating the Controller Service with the Agent Service in the Ogent system.

## Architecture Overview

The Ogent system consists of two main components:

1. **Controller Service**: Central management service that handles user authentication, command distribution, and result aggregation.
2. **Agent Service**: Deployed on target systems to execute commands and report results back to the controller.

## Integration Points

### 1. Authentication Flow

The Agent Service authenticates with the Controller Service using the following flow:

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

### 2. Command Execution Flow

Commands are executed using the following flow:

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

### 3. Agent Status Updates

Agent status is updated using the following flow:

```
Agent Service                                Controller Service
     |                                              |
     |  Socket.IO "agent_info"                      |
     |--------------------------------------------->|
     |                                              |
     |  Store agent information                     |
     |                                              |
```

## Implementation Details

### Controller Service Changes

1. **Domain Layer**:
   - Use the existing `Agent` and `Command` domain models
   - Implement the repository interfaces for agent and command storage

2. **Application Layer**:
   - Use the existing services for agent and command management
   - Ensure the `SocketService` properly handles agent connections and command execution

3. **Infrastructure Layer**:
   - Implement the repository interfaces using appropriate storage mechanisms
   - Implement the socket service interface using Socket.IO

### Agent Service Changes

1. **Configuration**:
   - Update the configuration to connect to the controller service
   - Configure authentication credentials

2. **Client Service**:
   - Ensure proper authentication with the controller service
   - Handle command execution requests
   - Send command results and progress updates

3. **Agent Manager**:
   - Properly manage executors for command execution
   - Track command history and status

## Deployment Considerations

1. **Network Connectivity**:
   - Ensure agents can reach the controller service
   - Configure firewalls to allow WebSocket connections

2. **Scaling**:
   - Use Redis for Socket.IO adapter when scaling the controller service
   - Configure proper reconnection settings for agents

3. **Security**:
   - Use HTTPS for all connections
   - Implement proper authentication and authorization
   - Validate and sanitize all commands

## Testing the Integration

1. **Unit Tests**:
   - Test individual components in isolation
   - Mock external dependencies

2. **Integration Tests**:
   - Test the communication between services
   - Verify command execution flow

3. **End-to-End Tests**:
   - Test the complete system with real agents
   - Verify all features work as expected

## Implementation Plan

1. **Phase 1: Basic Integration**
   - Connect agent service to controller service
   - Implement authentication flow
   - Test basic command execution

2. **Phase 2: Enhanced Features**
   - Implement real-time progress updates
   - Add support for different executor types
   - Implement AI command processing

3. **Phase 3: Scaling and Reliability**
   - Add Redis for scaling
   - Implement reconnection logic
   - Add monitoring and logging 