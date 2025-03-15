"""Unit tests for the agent manager class."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from agent.manager import AgentManager
from agent.executors import CommandExecutor

class MockExecutor(CommandExecutor):
    """Mock executor for testing."""
    
    def __init__(self, available=True):
        """Initialize the mock executor."""
        super().__init__()
        self.available = available
        self.execute_called = False
        self.command = None
        self.command_id = None
        self.progress_callback = None
    
    def is_available(self):
        """Check if the executor is available."""
        return self.available
    
    def get_target_info(self):
        """Get information about the execution target."""
        return {"type": "mock"}
    
    async def execute(self, command, command_id=None, progress_callback=None):
        """Execute a command."""
        self.execute_called = True
        self.command = command
        self.command_id = command_id
        self.progress_callback = progress_callback
        
        result = self._create_base_result(
            command=command,
            exit_code=0,
            stdout="mock output",
            stderr="",
            execution_type="mock",
            target="mock"
        )
        return result
    
    def disconnect(self):
        """Disconnect from the target."""
        self.disconnect_called = True

class TestAgentManager:
    """Test cases for the agent manager class."""
    
    @patch('agent.manager.LocalExecutor')
    @patch('agent.manager.SSHExecutor')
    @patch('agent.manager.config')
    def test_init(self, mock_config, mock_ssh_executor, mock_local_executor):
        """Test initialization of the agent manager."""
        # Setup mocks
        mock_config.ssh_enabled = False
        mock_local_executor.return_value = MockExecutor()
        
        manager = AgentManager()
        
        assert "local" in manager.executors
        assert len(manager.executors) == 1
        assert manager.command_history == []
        assert manager.max_history_size == 100
    
    @patch('agent.manager.LocalExecutor')
    @patch('agent.manager.SSHExecutor')
    @patch('agent.manager.config')
    def test_init_with_ssh(self, mock_config, mock_ssh_executor, mock_local_executor):
        """Test initialization with SSH enabled."""
        # Setup mocks
        mock_config.ssh_enabled = True
        mock_config.ssh_config = {"enabled": True}
        
        mock_local_executor.return_value = MockExecutor()
        
        ssh_executor = MockExecutor()
        ssh_executor.connect = MagicMock(return_value=True)
        mock_ssh_executor.return_value = ssh_executor
        
        manager = AgentManager()
        
        assert "local" in manager.executors
        assert "ssh" in manager.executors
        assert len(manager.executors) == 2
    
    @patch('agent.manager.LocalExecutor')
    @patch('agent.manager.SSHExecutor')
    @patch('agent.manager.config')
    def test_init_with_ssh_connection_failure(self, mock_config, mock_ssh_executor, mock_local_executor):
        """Test initialization with SSH connection failure."""
        # Setup mocks
        mock_config.ssh_enabled = True
        mock_config.ssh_config = {"enabled": True}
        
        mock_local_executor.return_value = MockExecutor()
        
        ssh_executor = MockExecutor()
        ssh_executor.connect = MagicMock(return_value=False)
        mock_ssh_executor.return_value = ssh_executor
        
        manager = AgentManager()
        
        assert "local" in manager.executors
        assert "ssh" in manager.executors  # SSH executor is still added even if connection fails
        assert len(manager.executors) == 2
        assert ssh_executor.connect.called  # Verify that connect was called
    
    def test_get_available_executors(self):
        """Test getting available executors."""
        manager = AgentManager()
        
        # Replace executors with mocks
        manager.executors = {
            "local": MockExecutor(available=True),
            "ssh": MockExecutor(available=False)
        }
        
        executors = manager.get_available_executors()
        
        assert "local" in executors
        assert "ssh" not in executors
        assert executors["local"]["type"] == "local"
        assert executors["local"]["available"] is True
    
    def test_get_command_history(self):
        """Test getting command history."""
        manager = AgentManager()
        
        # Add some history items
        manager.command_history = [
            {"command": "command1", "exit_code": 0},
            {"command": "command2", "exit_code": 1},
            {"command": "command3", "exit_code": 0}
        ]
        
        # Get all history
        history = manager.get_command_history(limit=0)
        assert len(history) == 3
        
        # Get limited history
        history = manager.get_command_history(limit=2)
        assert len(history) == 2
        assert history[0]["command"] == "command2"
        assert history[1]["command"] == "command3"
    
    def test_add_to_history(self):
        """Test adding to command history."""
        manager = AgentManager()
        
        # Add an item
        manager._add_to_history({"command": "test", "exit_code": 0})
        assert len(manager.command_history) == 1
        
        # Add many items to test trimming
        manager.max_history_size = 3
        manager._add_to_history({"command": "test2", "exit_code": 0})
        manager._add_to_history({"command": "test3", "exit_code": 0})
        manager._add_to_history({"command": "test4", "exit_code": 0})
        
        assert len(manager.command_history) == 3
        assert manager.command_history[0]["command"] == "test2"
        assert manager.command_history[2]["command"] == "test4"
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test successful command execution."""
        manager = AgentManager()
        
        # Replace executors with mocks
        mock_executor = MockExecutor()
        manager.executors = {"local": mock_executor}
        
        result = await manager.execute_command("test command")
        
        assert mock_executor.execute_called is True
        assert mock_executor.command == "test command"
        assert result["command"] == "test command"
        assert result["exit_code"] == 0
        assert result["stdout"] == "mock output"
        assert result["status"] == "success"
        assert len(manager.command_history) == 1
    
    @pytest.mark.asyncio
    async def test_execute_command_with_unknown_executor(self):
        """Test command execution with unknown executor."""
        manager = AgentManager()
        
        # Replace executors with mocks
        manager.executors = {"local": MockExecutor()}
        
        result = await manager.execute_command("test command", executor_type="unknown")
        
        assert result["exit_code"] == -1
        assert "not found" in result["stderr"]
        assert result["status"] == "error"
        assert len(manager.command_history) == 1
    
    @pytest.mark.asyncio
    async def test_execute_command_with_unavailable_executor(self):
        """Test command execution with unavailable executor."""
        manager = AgentManager()
        
        # Replace executors with mocks
        manager.executors = {"ssh": MockExecutor(available=False)}
        
        result = await manager.execute_command("test command", executor_type="ssh")
        
        assert result["exit_code"] == -1
        assert "not available" in result["stderr"]
        assert result["status"] == "error"
        assert len(manager.command_history) == 1
    
    @pytest.mark.asyncio
    async def test_execute_command_with_exception(self):
        """Test command execution with an exception."""
        manager = AgentManager()
        
        # Create a mock executor that raises an exception
        mock_executor = MockExecutor()
        mock_executor.execute = AsyncMock(side_effect=Exception("Test exception"))
        manager.executors = {"local": mock_executor}
        
        result = await manager.execute_command("test command")
        
        assert result["exit_code"] == -1
        assert "Error executing command" in result["stderr"]
        assert "Test exception" in result["stderr"]
        assert result["status"] == "error"
        assert len(manager.command_history) == 1
    
    def test_cleanup(self):
        """Test cleanup of resources."""
        manager = AgentManager()
        
        # Create mock executors
        local_executor = MockExecutor()
        ssh_executor = MockExecutor()
        ssh_executor.disconnect = MagicMock()
        
        manager.executors = {
            "local": local_executor,
            "ssh": ssh_executor
        }
        
        manager.cleanup()
        
        # Verify SSH executor was disconnected
        ssh_executor.disconnect.assert_called_once() 