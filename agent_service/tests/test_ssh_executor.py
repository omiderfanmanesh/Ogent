"""Unit tests for the SSH executor class."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

from agent.executors.ssh_executor import SSHExecutor

class TestSSHExecutor:
    """Test cases for the SSH executor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "enabled": True,
            "host": "test-host",
            "port": 22,
            "username": "test-user",
            "password": "test-password",
            "key_path": "~/.ssh/id_rsa",
            "timeout": 10
        }
    
    def test_init(self):
        """Test initialization of the SSH executor."""
        executor = SSHExecutor(self.config)
        assert executor.enabled is True
        assert executor.host == "test-host"
        assert executor.port == 22
        assert executor.username == "test-user"
        assert executor.password == "test-password"
        assert executor.client is None
    
    def test_init_with_missing_host(self):
        """Test initialization with missing host."""
        config = self.config.copy()
        config["host"] = ""
        executor = SSHExecutor(config)
        assert executor.enabled is False
    
    def test_init_with_missing_username(self):
        """Test initialization with missing username."""
        config = self.config.copy()
        config["username"] = ""
        executor = SSHExecutor(config)
        assert executor.enabled is False
    
    def test_is_available(self):
        """Test checking if the SSH executor is available."""
        executor = SSHExecutor(self.config)
        assert executor.is_available() is False  # Not connected yet
        
        # Mock the client
        executor.client = MagicMock()
        assert executor.is_available() is True
    
    def test_get_target_info(self):
        """Test getting information about the SSH target."""
        executor = SSHExecutor(self.config)
        info = executor.get_target_info()
        
        assert info["hostname"] == "test-host"
        assert info["port"] == 22
        assert info["username"] == "test-user"
        assert info["connected"] is False
        
        # Mock the client
        executor.client = MagicMock()
        info = executor.get_target_info()
        assert info["connected"] is True
    
    @patch('paramiko.SSHClient')
    def test_connect_success_with_key(self, mock_ssh_client):
        """Test successful connection with key authentication."""
        # Setup mock
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        executor = SSHExecutor(self.config)
        result = executor.connect()
        
        assert result is True
        assert executor.client is not None
        mock_client.set_missing_host_key_policy.assert_called_once()
        mock_client.connect.assert_called_once_with(
            hostname="test-host",
            port=22,
            username="test-user",
            key_filename=executor.key_path,
            timeout=10
        )
    
    @patch('paramiko.SSHClient')
    def test_connect_success_with_password(self, mock_ssh_client):
        """Test successful connection with password authentication after key fails."""
        # Setup mock
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        # Make key authentication fail
        mock_client.connect.side_effect = [Exception("Key auth failed"), None]
        
        executor = SSHExecutor(self.config)
        result = executor.connect()
        
        assert result is True
        assert executor.client is not None
        assert mock_client.connect.call_count == 2
        
        # Check second call used password
        second_call_kwargs = mock_client.connect.call_args_list[1][1]
        assert second_call_kwargs["hostname"] == "test-host"
        assert second_call_kwargs["port"] == 22
        assert second_call_kwargs["username"] == "test-user"
        assert second_call_kwargs["password"] == "test-password"
    
    @patch('paramiko.SSHClient')
    def test_connect_failure(self, mock_ssh_client):
        """Test failed connection."""
        # Setup mock
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        # Make both authentication methods fail
        mock_client.connect.side_effect = Exception("Auth failed")
        
        executor = SSHExecutor(self.config)
        result = executor.connect()
        
        assert result is False
        assert executor.client is None
        mock_client.close.assert_called_once()
    
    def test_disconnect(self):
        """Test disconnection."""
        executor = SSHExecutor(self.config)
        mock_client = MagicMock()
        executor.client = mock_client
        
        executor.disconnect()
        
        assert executor.client is None
        mock_client.close.assert_called_once()
    
    @patch('paramiko.SSHClient')
    def test_test_connection_success(self, mock_ssh_client):
        """Test successful connection test."""
        # Setup mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_stdout = MagicMock()
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_client.exec_command.return_value = (None, mock_stdout, None)
        
        executor = SSHExecutor(self.config)
        executor.client = mock_client
        
        success, message = executor.test_connection()
        
        assert success is True
        assert "successful" in message
        mock_client.exec_command.assert_called_once_with("echo 'SSH connection test'")
    
    @patch('paramiko.SSHClient')
    def test_test_connection_failure(self, mock_ssh_client):
        """Test failed connection test."""
        # Setup mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_stdout = MagicMock()
        mock_stdout.channel.recv_exit_status.return_value = 1
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"Error message"
        
        mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        executor = SSHExecutor(self.config)
        executor.client = mock_client
        
        success, message = executor.test_connection()
        
        assert success is False
        assert "failed" in message
        assert "Error message" in message
    
    @pytest.mark.asyncio
    @patch('paramiko.SSHClient')
    async def test_execute_success(self, mock_ssh_client):
        """Test successful command execution."""
        # Setup mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b"test output"
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        executor = SSHExecutor(self.config)
        executor.client = mock_client
        
        result = await executor.execute("test command")
        
        assert result["command"] == "test command"
        assert result["exit_code"] == 0
        assert result["stdout"] == "test output"
        assert result["stderr"] == ""
        assert result["execution_type"] == "ssh"
        assert result["target"] == "test-user@test-host"
        mock_client.exec_command.assert_called_once_with("test command")
    
    @pytest.mark.asyncio
    async def test_execute_disabled(self):
        """Test command execution when SSH is disabled."""
        config = self.config.copy()
        config["enabled"] = False
        executor = SSHExecutor(config)
        
        mock_callback = AsyncMock()
        result = await executor.execute("test command", "test-id", mock_callback)
        
        assert result["exit_code"] == -1
        assert "SSH execution is disabled" in result["stderr"]
        mock_callback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_not_connected(self):
        """Test command execution when not connected."""
        executor = SSHExecutor(self.config)
        
        # Mock connect to fail
        executor.connect = MagicMock(return_value=False)
        
        mock_callback = AsyncMock()
        result = await executor.execute("test command", "test-id", mock_callback)
        
        assert result["exit_code"] == -1
        assert "Failed to establish SSH connection" in result["stderr"]
        assert mock_callback.call_count >= 2
    
    @pytest.mark.asyncio
    @patch('paramiko.SSHClient')
    async def test_execute_with_exception(self, mock_ssh_client):
        """Test command execution with an exception."""
        # Setup mocks
        mock_client = MagicMock()
        mock_ssh_client.return_value = mock_client
        
        # Make exec_command raise an exception
        mock_client.exec_command.side_effect = Exception("Test exception")
        
        executor = SSHExecutor(self.config)
        executor.client = mock_client
        
        mock_callback = AsyncMock()
        result = await executor.execute("test command", "test-id", mock_callback)
        
        assert result["exit_code"] == -1
        assert "Error executing SSH command" in result["stderr"]
        assert "Test exception" in result["stderr"]
        assert mock_callback.call_count >= 2 