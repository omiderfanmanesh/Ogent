"""Socket.IO client for the Agent Service."""

import os
import asyncio
import socketio
import logging
import json
from datetime import datetime, UTC

from .config import config
from .manager import agent_manager

# Configure logging
logger = logging.getLogger("agent.client")

# Create a Socket.IO client
sio = socketio.AsyncClient(
    reconnection=True, 
    reconnection_attempts=config.max_reconnect_attempts, 
    reconnection_delay=config.reconnect_delay, 
    logger=True, 
    engineio_logger=True
)

# Track connection state
connected = False
reconnect_attempts = 0

async def get_auth_token():
    """Get authentication token from the Controller Service"""
    try:
        logger.info(f"Requesting authentication token from {config.controller_url}/token")
        import requests  # Import here to avoid circular imports
        
        response = requests.post(
            f"{config.controller_url}/token",
            data={"username": config.agent_username, "password": config.agent_password}
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            logger.info("Authentication successful")
            return token
        else:
            logger.error(f"Authentication failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error during authentication: {str(e)}")
        return None

async def send_command_progress(command_id, requester_sid, progress_data):
    """Send command progress updates to the Controller Service"""
    if not command_id:
        return
    
    try:
        # Add command ID and requester SID to progress data
        progress_data['command_id'] = command_id
        progress_data['requester_sid'] = requester_sid
        
        # Send progress update via Socket.IO
        if connected:
            await sio.emit('command_progress', progress_data)
        
        # Publish to Redis if available
        if config.redis_client:
            config.redis_client.publish('command_progress', json.dumps({
                'type': 'command_progress',
                'data': progress_data
            }))
    except Exception as e:
        logger.error(f"Error sending command progress: {str(e)}")

# Socket.IO event handlers
@sio.event
async def connect():
    """Handle successful connection to the Controller Service"""
    global connected, reconnect_attempts
    connected = True
    reconnect_attempts = 0
    logger.info("Connected to Controller Service")

@sio.event
async def disconnect():
    """Handle disconnection from the Controller Service"""
    global connected
    connected = False
    logger.info("Disconnected from Controller Service")

@sio.event
async def connection_response(data):
    """Handle connection response from the Controller Service"""
    logger.info(f"Connection response: {data}")

@sio.event
async def command_response(data):
    """Handle command response from the Controller Service"""
    logger.info(f"Command response received: {data}")

@sio.event
async def execute_command_event(data):
    """Handle command execution request from the Controller Service"""
    logger.info(f"Received command execution request: {data}")
    
    # Validate the request
    if not isinstance(data, dict) or 'command' not in data:
        logger.error("Invalid command format received")
        await sio.emit('command_result', {
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
        await send_command_progress(command_id, requester_sid, progress_data)
    
    # Execute the command using the agent manager
    result = await agent_manager.execute_command(
        command=data['command'],
        executor_type=executor_type,
        command_id=command_id,
        progress_callback=progress_callback
    )
    
    # Send the result back to the Controller Service
    await sio.emit('command_result', {
        'status': 'success' if result['exit_code'] == 0 else 'error',
        'command': data['command'],
        'command_id': command_id,
        'result': result,
        'requester_sid': requester_sid,
        'timestamp': datetime.now(UTC).isoformat()
    })
    
    # Publish to Redis if available
    if config.redis_client:
        config.redis_client.publish('command_results', json.dumps({
            'type': 'command_result',
            'data': {
                'status': 'success' if result['exit_code'] == 0 else 'error',
                'command': data['command'],
                'command_id': command_id,
                'result': result,
                'requester_sid': requester_sid,
                'timestamp': datetime.now(UTC).isoformat()
            }
        }))

async def connect_to_controller():
    """Connect to the Controller Service with authentication"""
    global reconnect_attempts
    
    while not connected and (reconnect_attempts < config.max_reconnect_attempts or config.max_reconnect_attempts <= 0):
        try:
            # Get authentication token
            token = await get_auth_token()
            if not token:
                logger.error("Failed to get authentication token")
                reconnect_attempts += 1
                await asyncio.sleep(config.reconnect_delay)
                continue
            
            # Connect to the Controller Service with authentication
            logger.info(f"Connecting to Controller Service at {config.controller_url}")
            
            # Get target info from executors
            local_info = agent_manager.executors.get("local", {}).get_target_info() if "local" in agent_manager.executors else {}
            ssh_info = agent_manager.executors.get("ssh", {}).get_target_info() if "ssh" in agent_manager.executors else {}
            
            await sio.connect(
                config.controller_url, 
                auth={
                    "token": token,
                    "is_agent": True,  # Identify as an agent
                    "agent_info": {
                        "hostname": local_info.get("hostname", "unknown"),
                        "platform": local_info.get("platform", "unknown"),
                        "version": local_info.get("version", "unknown"),
                        "python_version": local_info.get("python_version", "unknown"),
                        "ssh_enabled": "ssh" in agent_manager.executors and agent_manager.executors["ssh"].enabled,
                        "ssh_target": f"{ssh_info.get('username', '')}@{ssh_info.get('hostname', '')}" if "ssh" in agent_manager.executors else None
                    }
                }
            )
            
            # Wait until disconnected
            await sio.wait()
            
        except socketio.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            reconnect_attempts += 1
            await asyncio.sleep(config.reconnect_delay)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            reconnect_attempts += 1
            await asyncio.sleep(config.reconnect_delay)
    
    if not connected:
        logger.critical(f"Failed to connect after {reconnect_attempts} attempts")
        return False
    
    return True

async def start_agent_client():
    """Start the Agent Service client"""
    logger.info("Starting Agent Service client")
    
    try:
        # Test SSH connection if enabled
        if "ssh" in agent_manager.executors:
            ssh_executor = agent_manager.executors["ssh"]
            if ssh_executor.enabled:
                logger.info("Testing SSH connection...")
                success, message = ssh_executor.test_connection()
                
                if success:
                    logger.info(f"SSH connection test successful: {message}")
                else:
                    logger.error(f"SSH connection test failed: {message}")
        
        # Connect to the Controller Service
        success = await connect_to_controller()
        if not success:
            logger.critical("Failed to connect to Controller Service. Exiting.")
            return 1
        
    except KeyboardInterrupt:
        logger.info("Agent Service client stopped by user")
    
    except Exception as e:
        logger.critical(f"Unhandled exception: {str(e)}")
        return 1
    
    finally:
        # Ensure the Socket.IO client is disconnected
        if connected:
            await sio.disconnect()
        
        # Clean up resources
        agent_manager.cleanup()
    
    logger.info("Agent Service client stopped")
    return 0 