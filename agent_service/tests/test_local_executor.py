"""Unit tests for the local executor class."""

import pytest
import asyncio
import platform
from unittest.mock import AsyncMock, MagicMock, patch

from agent.executors.local_executor import LocalExecutor

class TestLocalExecutor:
    """Test cases for the local executor class."""
    
    def test_init(self):
        """Test initialization of the local executor."""
        executor = LocalExecutor()
        assert executor.enabled is True
    
    def test_is_available(self):
        """Test checking if the local executor is available."""
        executor = LocalExecutor()
        assert executor.is_available() is True
    
    def test_get_target_info(self):
        """Test getting information about the local system."""
        executor = LocalExecutor()
        info = executor.get_target_info()
        
        assert "hostname" in info
        assert "platform" in info
        assert "version" in info
        assert "python_version" in info
        assert info["platform"] == platform.system()
    
    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful command execution."""
        executor = LocalExecutor()
        
        # Use a simple command that should work on all platforms
        if platform.system() == "Windows":
            command = "echo Hello, World!"
        else:
            command = "echo 'Hello, World!'"
        
        result = await executor.execute(command)
        
        assert result["command"] == command
        assert result["exit_code"] == 0
        assert "Hello, World!" in result["stdout"]
        assert result["stderr"] == ""
        assert result["execution_type"] == "local"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_execute_failure(self):
        """Test failed command execution."""
        executor = LocalExecutor()
        
        # Use a command that should fail on all platforms
        command = "command_that_does_not_exist"
        
        result = await executor.execute(command)
        
        assert result["command"] == command
        assert result["exit_code"] != 0
        assert result["execution_type"] == "local"
        assert "timestamp" in result
    
    @pytest.mark.asyncio
    async def test_execute_with_progress_callback(self):
        """Test command execution with progress callback."""
        executor = LocalExecutor()
        mock_callback = AsyncMock()
        
        # Use a simple command that should work on all platforms
        if platform.system() == "Windows":
            command = "echo Hello, World!"
        else:
            command = "echo 'Hello, World!'"
        
        result = await executor.execute(command, "test-id", mock_callback)
        
        # Check that the callback was called at least twice (start and end)
        assert mock_callback.call_count >= 2
        
        # Check the first call (should be 'running')
        first_call_args = mock_callback.call_args_list[0][0][0]
        assert first_call_args["status"] == "running"
        assert first_call_args["command_id"] == "test-id"
        
        # Check the last call (should be 'completed')
        last_call_args = mock_callback.call_args_list[-1][0][0]
        assert last_call_args["status"] == "completed"
        assert last_call_args["command_id"] == "test-id"
        assert last_call_args["progress"] == 100
    
    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        """Test command execution with timeout."""
        executor = LocalExecutor()
        
        # Mock the subprocess.Popen to simulate a timeout
        with patch('subprocess.Popen', side_effect=asyncio.TimeoutError):
            result = await executor.execute("sleep 10")
            
            assert result["command"] == "sleep 10"
            assert result["exit_code"] == -1
            assert "Command execution timed out" in result["stderr"]
            assert result["execution_type"] == "local"
    
    @pytest.mark.asyncio
    async def test_execute_with_exception(self):
        """Test command execution with an exception."""
        executor = LocalExecutor()
        
        # Mock the subprocess.Popen to simulate an exception
        with patch('subprocess.Popen', side_effect=Exception("Test exception")):
            result = await executor.execute("test command")
            
            assert result["command"] == "test command"
            assert result["exit_code"] == -1
            assert "Error executing command" in result["stderr"]
            assert result["execution_type"] == "local" 