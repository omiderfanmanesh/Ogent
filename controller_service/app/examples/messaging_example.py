import asyncio
import logging
import os
import sys

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.infrastructure.messaging import MessagingFactory
from app.domain.interfaces import EventHandlerType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("messaging_example")

# Example event handler
async def handle_command(session, data):
    logger.info(f"Received command from session {session.get('user_id', 'unknown')}: {data}")
    
    # Process the command
    command_id = data.get("command_id")
    command_data = data.get("data", {})
    
    # Simulate command execution
    logger.info(f"Executing command {command_id}: {command_data}")
    await asyncio.sleep(1)  # Simulate work
    
    # Return result
    result = {
        "output": f"Command {command_id} executed successfully",
        "exit_code": 0
    }
    
    return result

# Example event handler for agent registration
async def handle_agent_registration(session, data):
    logger.info(f"Agent registration from session {session.get('sid')}: {data}")
    
    # Extract agent information
    agent_id = data.get("agent_id")
    username = data.get("username")
    
    if not agent_id:
        logger.error("Missing agent_id in registration data")
        return
    
    # Update session with agent information
    session["user_id"] = agent_id
    session["username"] = username
    session["type"] = "agent"
    
    logger.info(f"Agent {agent_id} registered successfully")

async def main():
    # Create messaging factory
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    factory = MessagingFactory(redis_url=redis_url, logger=logger)
    
    # Create Socket.IO event handler
    socketio_handler = factory.create_event_handler("socketio")
    
    # Register event handlers
    await socketio_handler.register_handler("command", handle_command)
    await socketio_handler.register_handler("register", handle_agent_registration)
    
    # Create command publisher
    command_publisher = factory.create_command_publisher("socketio")
    
    # Example: Publish a command to an agent
    agent_id = "agent-1"
    command_id = "cmd-123"
    command_data = {
        "command": "echo 'Hello, World!'",
        "execution_target": "shell",
        "execution_context": {}
    }
    
    # Wait for connections
    logger.info("Waiting for connections...")
    await asyncio.sleep(5)
    
    # Publish command
    logger.info(f"Publishing command {command_id} to agent {agent_id}")
    success = await command_publisher.publish_command(
        agent_id=agent_id,
        command_id=command_id,
        command_data=command_data
    )
    
    if success:
        logger.info(f"Command {command_id} published successfully")
    else:
        logger.error(f"Failed to publish command {command_id}")
    
    # Keep the application running
    logger.info("Example running. Press Ctrl+C to exit.")
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Exiting...")

if __name__ == "__main__":
    asyncio.run(main())