"""Unit tests for the config module."""

import pytest
from unittest.mock import patch, MagicMock
import os

from agent.config import Config, config

class TestConfig:
    """Test cases for the config module."""
    
    def test_default_config(self):
        """Test that the default configuration is loaded correctly."""
        # Check that the config object has the expected attributes
        assert hasattr(config, 'controller_url')
        assert hasattr(config, 'agent_username')
        assert hasattr(config, 'agent_password')
        assert hasattr(config, 'api_token')
        assert hasattr(config, 'ssh_enabled')
        assert hasattr(config, 'hostname')
        assert hasattr(config, 'platform')
        assert hasattr(config, 'version')
    
    def test_env_variables(self):
        """Test that environment variables are used correctly."""
        # Mock environment variables
        env_vars = {
            'CONTROLLER_URL': 'http://test-controller:8000',
            'AGENT_USERNAME': 'test-user',
            'AGENT_PASSWORD': 'test-password',
            'API_TOKEN': 'test-token',
            'SSH_ENABLED': 'true',
            'SSH_HOST': 'test-host',
            'SSH_PORT': '2222',
            'SSH_USERNAME': 'ssh-user',
            'SSH_PASSWORD': 'ssh-password'
        }
        
        # Patch os.getenv to return our mock values
        with patch.dict(os.environ, env_vars):
            # Create a new config instance
            test_config = Config()
            
            # Assert that the config was initialized with the environment variables
            assert test_config.controller_url == 'http://test-controller:8000'
            assert test_config.agent_username == 'test-user'
            assert test_config.agent_password == 'test-password'
            assert test_config.api_token == 'test-token'
            assert test_config.ssh_enabled is True
            assert test_config.ssh_host == 'test-host'
            assert test_config.ssh_port == '2222'
            assert test_config.ssh_username == 'ssh-user'
            assert test_config.ssh_password == 'ssh-password'
    
    def test_ssh_config(self):
        """Test the ssh_config property."""
        # Create a config instance with specific SSH settings
        test_config = Config()
        test_config.ssh_enabled = True
        test_config.ssh_host = 'test-host'
        test_config.ssh_port = '2222'
        test_config.ssh_username = 'ssh-user'
        test_config.ssh_password = 'ssh-password'
        test_config.ssh_key_path = '/path/to/key'
        test_config.ssh_timeout = '30'
        
        # Get the SSH config
        ssh_config = test_config.ssh_config
        
        # Assert that the SSH config contains the expected values
        assert ssh_config['enabled'] is True
        assert ssh_config['host'] == 'test-host'
        assert ssh_config['port'] == '2222'
        assert ssh_config['username'] == 'ssh-user'
        assert ssh_config['password'] == 'ssh-password'
        assert ssh_config['key_path'] == '/path/to/key'
        assert ssh_config['timeout'] == '30'
    
    def test_str_representation(self):
        """Test the string representation of the config."""
        # Create a config instance with sensitive information
        test_config = Config()
        test_config.agent_password = 'secret-password'
        test_config.api_password = 'api-secret'
        test_config.ssh_password = 'ssh-secret'
        test_config.api_token = 'secret-token'
        
        # Get the string representation
        config_str = str(test_config)
        
        # Assert that sensitive information is masked
        assert 'secret-password' not in config_str
        assert 'api-secret' not in config_str
        assert 'ssh-secret' not in config_str
        assert 'secret-token' not in config_str
        assert '********' in config_str
    
    def test_redis_connection(self):
        """Test Redis connection handling."""
        # Mock the redis module
        mock_redis = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis.from_url.return_value = mock_redis_client
        
        # Patch the redis module and os.getenv
        with patch.dict('sys.modules', {'redis': mock_redis}), \
             patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379/0'}):
            # Create a new config instance
            test_config = Config()
            
            # Assert that the Redis client was created
            assert test_config.redis_client is not None
            mock_redis.from_url.assert_called_once_with('redis://localhost:6379/0')
    
    def test_redis_connection_failure(self):
        """Test Redis connection failure handling."""
        # Mock the redis module to raise an exception
        mock_redis = MagicMock()
        mock_redis.from_url.side_effect = Exception("Connection failed")
        
        # Patch the redis module, os.getenv, and logger
        with patch.dict('sys.modules', {'redis': mock_redis}), \
             patch.dict(os.environ, {'REDIS_URL': 'redis://localhost:6379/0'}), \
             patch('agent.config.logger') as mock_logger:
            # Create a new config instance
            test_config = Config()
            
            # Assert that the Redis client is None and an error was logged
            assert test_config.redis_client is None
            mock_logger.error.assert_called_once()
    
    def test_cleanup(self):
        """Test the cleanup method."""
        # Create a config instance with a mock Redis client
        test_config = Config()
        mock_redis_client = MagicMock()
        test_config.redis_client = mock_redis_client
        
        # Call the cleanup method
        with patch('agent.config.logger') as mock_logger:
            test_config.cleanup()
            
            # Assert that the Redis client was closed and set to None
            mock_redis_client.close.assert_called_once()
            assert test_config.redis_client is None
            mock_logger.info.assert_called_once_with("Closing Redis connection") 