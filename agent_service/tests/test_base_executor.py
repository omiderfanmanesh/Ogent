"""Unit tests for the base executor class."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from agent.executors.base_executor import CommandExecutor

# Create a concrete implementation of the abstract base class for testing
@pytest.fixture
def test_executor():
    """Fixture to provide a test executor instance."""
    class _TestExecutor(CommandExecutor):
        """Test executor implementation for testing."""
        
        def __init__(self):
            """Initialize the test executor."""
            super().__init__()
        
        def is_available(self):
            """Check if the executor is available."""
            return True
        
        def get_target_info(self):
            """Get information about the execution target."""
            return {"type": "test"}
        
        async def execute(self, command, command_id=None, progress_callback=None):
            """Execute a command."""
            result = self._create_base_result(
                command=command,
                exit_code=0,
                stdout="test output",
                stderr="",
                execution_type="test",
                target="test"
            )
            return result
    
    return _TestExecutor()

class TestBaseExecutor:
    """Test cases for the base executor class."""
    
    def test_init(self, test_executor):
        """Test initialization of the executor."""
        assert test_executor.enabled is True
    
    def test_create_base_result(self, test_executor):
        """Test creation of base result dictionary."""
        result = test_executor._create_base_result(
            command="test command",
            exit_code=0,
            stdout="test output",
            stderr="test error",
            execution_type="test",
            target="test target"
        )
        
        assert result["command"] == "test command"
        assert result["exit_code"] == 0
        assert result["stdout"] == "test output"
        assert result["stderr"] == "test error"
        assert result["execution_type"] == "test"
        assert result["target"] == "test target"
        assert "timestamp" in result
        assert "command_id" in result
    
    @pytest.mark.asyncio
    async def test_send_progress_update_with_callback(self, test_executor):
        """Test sending progress updates with a callback."""
        mock_callback = AsyncMock()
        command_id = "test-id"
        
        await test_executor._send_progress_update(
            command_id=command_id,
            progress_callback=mock_callback,
            data={"status": "running", "progress": 50}
        )
        
        # Check that the callback was called with the correct data
        mock_callback.assert_called_once()
        call_args = mock_callback.call_args[0][0]
        assert call_args["command_id"] == command_id
        assert call_args["status"] == "running"
        assert call_args["progress"] == 50
    
    @pytest.mark.asyncio
    async def test_send_progress_update_without_callback(self, test_executor):
        """Test sending progress updates without a callback."""
        # This should not raise an exception
        await test_executor._send_progress_update(
            command_id="test-id",
            progress_callback=None,
            data={"status": "running", "progress": 50}
        )
    
    @pytest.mark.asyncio
    async def test_send_progress_update_with_exception(self, test_executor):
        """Test sending progress updates with a callback that raises an exception."""
        mock_callback = AsyncMock(side_effect=Exception("Test exception"))
        
        # This should not raise an exception
        await test_executor._send_progress_update(
            command_id="test-id",
            progress_callback=mock_callback,
            data={"status": "running", "progress": 50}
        )
    
    @pytest.mark.asyncio
    async def test_execute_method(self, test_executor):
        """Test the execute method of the test executor."""
        result = await test_executor.execute("test command")
        
        assert result["command"] == "test command"
        assert result["exit_code"] == 0
        assert result["stdout"] == "test output"
        assert result["stderr"] == ""
        assert result["execution_type"] == "test"
        assert result["target"] == "test" 