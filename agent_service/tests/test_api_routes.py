"""Unit tests for the API routes module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Depends

from agent.api.routes import router, authenticate, get_info, get_executors, get_history, execute_command

class TestAPIRoutes:
    """Test cases for the API routes module."""
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self):
        """Test successful authentication with a valid API token."""
        # Mock the oauth2_scheme dependency
        mock_token = "valid-token"
        
        # Mock the config
        with patch('agent.api.routes.config') as mock_config, \
             patch('agent.api.routes.oauth2_scheme', return_value=mock_token):
            mock_config.api_token = "valid-token"
            # Call the authenticate function with a valid token
            result = await authenticate(mock_token)
            # Assert that the result is True
            assert result is True
    
    @pytest.mark.asyncio
    async def test_authenticate_failure(self):
        """Test failed authentication with an invalid API token."""
        # Mock the oauth2_scheme dependency
        mock_token = "invalid-token"
        
        # Mock the config
        with patch('agent.api.routes.config') as mock_config, \
             patch('agent.api.routes.oauth2_scheme', return_value=mock_token):
            mock_config.api_token = "valid-token"
            # Call the authenticate function with an invalid token
            with pytest.raises(HTTPException) as excinfo:
                await authenticate(mock_token)
            # Assert that the exception has the correct status code and detail
            assert excinfo.value.status_code == 401
            assert "Invalid authentication credentials" in excinfo.value.detail
    
    @pytest.mark.asyncio
    async def test_get_info(self):
        """Test the GET /info endpoint."""
        # Mock the authenticate dependency
        mock_authenticate = MagicMock(return_value=True)
        
        # Mock the config
        with patch('agent.api.routes.authenticate', mock_authenticate), \
             patch('agent.api.routes.config') as mock_config:
            mock_config.version = "1.0.0"
            
            # Call the get_info function
            result = await get_info(authenticated=True)
            
            # Assert that the result contains the expected data
            assert "version" in result
            assert result["version"] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_get_executors(self):
        """Test the GET /executors endpoint."""
        # Mock the authenticate dependency
        mock_authenticate = MagicMock(return_value=True)
        
        # Mock the agent_manager
        with patch('agent.api.routes.authenticate', mock_authenticate), \
             patch('agent.api.routes.agent_manager') as mock_agent_manager:
            mock_agent_manager.get_available_executors.return_value = {
                "local": {"type": "local", "available": True, "target": {"host": "localhost"}},
                "ssh": {"type": "ssh", "available": True, "target": {"host": "remote-host"}}
            }
            
            # Call the get_executors function
            result = await get_executors(authenticated=True)
            
            # Assert that the result contains the expected data
            assert "local" in result
            assert "ssh" in result
            assert result["local"]["type"] == "local"
            assert result["ssh"]["type"] == "ssh"
    
    @pytest.mark.asyncio
    async def test_get_history(self):
        """Test the GET /history endpoint."""
        # Mock the authenticate dependency
        mock_authenticate = MagicMock(return_value=True)
        
        # Mock the agent_manager
        with patch('agent.api.routes.authenticate', mock_authenticate), \
             patch('agent.api.routes.agent_manager') as mock_agent_manager:
            mock_agent_manager.get_command_history.return_value = [
                {
                    "command": "ls",
                    "command_id": "test-id",
                    "exit_code": 0,
                    "stdout": "file1 file2",
                    "stderr": "",
                    "timestamp": "2023-01-01T00:00:00",
                    "execution_type": "command",
                    "target": "local",
                    "status": "success"
                }
            ]
            
            # Call the get_history function
            result = await get_history(limit=10, authenticated=True)
            
            # Assert that the result contains the expected data
            assert len(result) == 1
            assert result[0]["command"] == "ls"
            assert result[0]["exit_code"] == 0
    
    @pytest.mark.asyncio
    async def test_execute_command(self):
        """Test the POST /execute endpoint."""
        # Mock the authenticate dependency
        mock_authenticate = MagicMock(return_value=True)
        
        # Mock the agent_manager
        with patch('agent.api.routes.authenticate', mock_authenticate), \
             patch('agent.api.routes.agent_manager') as mock_agent_manager:
            mock_agent_manager.execute_command = AsyncMock(return_value={
                "command": "ls",
                "command_id": "test-id",
                "exit_code": 0,
                "stdout": "file1 file2",
                "stderr": "",
                "timestamp": "2023-01-01T00:00:00",
                "execution_type": "command",
                "target": "local",
                "status": "success"
            })
            
            # Create a command request
            from agent.api.routes import CommandRequest
            request = CommandRequest(command="ls", executor_type="local")
            
            # Call the execute_command function
            result = await execute_command(request=request, authenticated=True)
            
            # Assert that the result contains the expected data
            assert result["command"] == "ls"
            assert result["exit_code"] == 0
            assert result["stdout"] == "file1 file2" 