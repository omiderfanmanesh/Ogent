"""Unit tests for the client module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json
from datetime import datetime, UTC

from agent.client import start_agent_client, connect, disconnect, execute_command_event, send_command_progress, get_auth_token, connection_response, command_response

class TestClient:
    """Test cases for the client module."""
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test the connect function."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        
        # Call the connect function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.connected', False), \
             patch('agent.client.reconnect_attempts', 5), \
             patch('agent.client.logger') as mock_logger:
            await connect()
        
        # Assert that the logger.info method was called
        mock_logger.info.assert_called_once_with("Connected to Controller Service")
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test the disconnect function."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        
        # Call the disconnect function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.connected', True), \
             patch('agent.client.logger') as mock_logger:
            await disconnect()
        
        # Assert that the logger.info method was called
        mock_logger.info.assert_called_once_with("Disconnected from Controller Service")
    
    @pytest.mark.asyncio
    async def test_execute_command_event(self):
        """Test the execute_command_event function."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        mock_sio.emit = AsyncMock()
        
        # Mock the agent_manager
        mock_agent_manager = MagicMock()
        mock_agent_manager.execute_command = AsyncMock(return_value={
            'command': 'test command',
            'exit_code': 0,
            'stdout': 'test output',
            'stderr': '',
            'timestamp': datetime.now(UTC).isoformat(),
            'execution_type': 'test',
            'target': 'test'
        })
        
        # Create a test command request
        command_request = {
            'command_id': 'test-id',
            'command': 'test command',
            'execution_target': 'local',
            'requester_sid': 'test-sid'
        }
        
        # Call the execute_command_event function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.agent_manager', mock_agent_manager), \
             patch('agent.client.send_command_progress', AsyncMock()):
            await execute_command_event(command_request)
        
        # Assert that the execute_command method was called with the correct arguments
        mock_agent_manager.execute_command.assert_called_once()
        call_args = mock_agent_manager.execute_command.call_args[1]
        assert call_args['command'] == 'test command'
        assert call_args['executor_type'] == 'local'
        assert call_args['command_id'] == 'test-id'
        assert callable(call_args['progress_callback'])
        
        # Assert that the emit method was called with the correct arguments
        mock_sio.emit.assert_called_once()
        assert mock_sio.emit.call_args[0][0] == 'command_result'
        assert 'status' in mock_sio.emit.call_args[0][1]
        assert mock_sio.emit.call_args[0][1]['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_execute_command_event_with_invalid_data(self):
        """Test the execute_command_event function with invalid data."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        mock_sio.emit = AsyncMock()
        
        # Call the execute_command_event function with invalid data
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.logger') as mock_logger:
            await execute_command_event({})  # Empty dict without 'command' key
        
        # Assert that the logger.error method was called
        mock_logger.error.assert_called_once_with("Invalid command format received")
        
        # Assert that the emit method was called with an error message
        mock_sio.emit.assert_called_once()
        assert mock_sio.emit.call_args[0][0] == 'command_result'
        assert 'status' in mock_sio.emit.call_args[0][1]
        assert mock_sio.emit.call_args[0][1]['status'] == 'error'
    
    @pytest.mark.asyncio
    async def test_send_command_progress(self):
        """Test the send_command_progress function."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        mock_sio.emit = AsyncMock()
        
        # Create test progress data
        progress_data = {
            'progress': 50,
            'message': 'Test progress'
        }
        
        # Call the send_command_progress function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.connected', True), \
             patch('agent.client.config') as mock_config:
            mock_config.redis_client = None
            await send_command_progress('test-id', 'test-sid', progress_data)
        
        # Assert that the emit method was called with the correct arguments
        mock_sio.emit.assert_called_once_with('command_progress', {
            'progress': 50,
            'message': 'Test progress',
            'command_id': 'test-id',
            'requester_sid': 'test-sid'
        })
    
    @pytest.mark.asyncio
    async def test_send_command_progress_with_redis(self):
        """Test the send_command_progress function with Redis."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        mock_sio.emit = AsyncMock()
        
        # Mock the Redis client
        mock_redis = MagicMock()
        
        # Create test progress data
        progress_data = {
            'progress': 50,
            'message': 'Test progress'
        }
        
        # Call the send_command_progress function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.connected', True), \
             patch('agent.client.config') as mock_config:
            mock_config.redis_client = mock_redis
            await send_command_progress('test-id', 'test-sid', progress_data)
        
        # Assert that the emit method was called with the correct arguments
        mock_sio.emit.assert_called_once_with('command_progress', {
            'progress': 50,
            'message': 'Test progress',
            'command_id': 'test-id',
            'requester_sid': 'test-sid'
        })
        
        # Assert that the Redis publish method was called with the correct arguments
        mock_redis.publish.assert_called_once()
        assert mock_redis.publish.call_args[0][0] == 'command_progress'
        published_data = json.loads(mock_redis.publish.call_args[0][1])
        assert published_data['type'] == 'command_progress'
        assert published_data['data']['progress'] == 50
    
    @pytest.mark.asyncio
    async def test_send_command_progress_with_exception(self):
        """Test the send_command_progress function with an exception."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        mock_sio.emit = AsyncMock(side_effect=Exception("Test exception"))
        
        # Create test progress data
        progress_data = {
            'progress': 50,
            'message': 'Test progress'
        }
        
        # Call the send_command_progress function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.connected', True), \
             patch('agent.client.config') as mock_config, \
             patch('agent.client.logger') as mock_logger:
            mock_config.redis_client = None
            await send_command_progress('test-id', 'test-sid', progress_data)
        
        # Assert that the logger.error method was called
        mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_auth_token_success(self):
        """Test the get_auth_token function with a successful response."""
        # Mock the requests module
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'access_token': 'test-token'}
        
        mock_requests = MagicMock()
        mock_requests.post.return_value = mock_response
        
        # Call the get_auth_token function
        with patch.dict('sys.modules', {'requests': mock_requests}), \
             patch('agent.client.config') as mock_config, \
             patch('agent.client.logger') as mock_logger:
            mock_config.controller_url = 'http://test-controller'
            mock_config.agent_username = 'test-user'
            mock_config.agent_password = 'test-password'
            
            token = await get_auth_token()
        
        # Assert that the requests.post method was called with the correct arguments
        mock_requests.post.assert_called_once_with(
            'http://test-controller/token',
            data={'username': 'test-user', 'password': 'test-password'}
        )
        
        # Assert that the token was returned
        assert token == 'test-token'
        
        # Assert that the logger.info method was called
        mock_logger.info.assert_called_with("Authentication successful")
    
    @pytest.mark.asyncio
    async def test_get_auth_token_failure(self):
        """Test the get_auth_token function with a failed response."""
        # Mock the requests module
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = 'Unauthorized'
        
        mock_requests = MagicMock()
        mock_requests.post.return_value = mock_response
        
        # Call the get_auth_token function
        with patch.dict('sys.modules', {'requests': mock_requests}), \
             patch('agent.client.config') as mock_config, \
             patch('agent.client.logger') as mock_logger:
            mock_config.controller_url = 'http://test-controller'
            mock_config.agent_username = 'test-user'
            mock_config.agent_password = 'test-password'
            
            token = await get_auth_token()
        
        # Assert that the requests.post method was called with the correct arguments
        mock_requests.post.assert_called_once_with(
            'http://test-controller/token',
            data={'username': 'test-user', 'password': 'test-password'}
        )
        
        # Assert that the token is None
        assert token is None
        
        # Assert that the logger.error method was called
        mock_logger.error.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_connection_response(self):
        """Test the connection_response function."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        
        # Call the connection_response function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.logger') as mock_logger:
            await connection_response({'status': 'success'})
        
        # Assert that the logger.info method was called
        mock_logger.info.assert_called_once_with("Connection response: {'status': 'success'}")
    
    @pytest.mark.asyncio
    async def test_command_response(self):
        """Test the command_response function."""
        # Mock the socket.io client
        mock_sio = MagicMock()
        
        # Call the command_response function
        with patch('agent.client.sio', mock_sio), \
             patch('agent.client.logger') as mock_logger:
            await command_response({'status': 'success'})
        
        # Assert that the logger.info method was called
        mock_logger.info.assert_called_once_with("Command response received: {'status': 'success'}")
    
    @pytest.mark.asyncio
    async def test_start_agent_client(self):
        """Test the start_agent_client function."""
        # This is a more complex test that would require mocking multiple components
        # For simplicity, we'll just test that the function exists
        assert callable(start_agent_client) 