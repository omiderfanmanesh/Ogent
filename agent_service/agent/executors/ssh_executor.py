"""SSH executor for command execution."""

import os
import logging
import paramiko
from typing import Dict, Any, Optional, Callable, Awaitable, Tuple
from datetime import datetime, UTC

from .base_executor import CommandExecutor

logger = logging.getLogger("agent.executor.ssh")

class SSHExecutor(CommandExecutor):
    """Executor for SSH command execution."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the SSH executor.
        
        Args:
            config: SSH configuration dictionary
        """
        super().__init__()
        self.enabled = config.get("enabled", False)
        self.host = config.get("host", "")
        self.port = int(config.get("port", 22))
        self.username = config.get("username", "")
        self.password = config.get("password", "")
        self.key_path = os.path.expanduser(config.get("key_path", "~/.ssh/id_rsa"))
        self.timeout = int(config.get("timeout", 10))
        self.client = None
        
        # Validate configuration
        if not self.host or not self.username:
            logger.warning("SSH host or username not provided, SSH execution is disabled")
            self.enabled = False
    
    def is_available(self) -> bool:
        """Check if the SSH executor is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        return self.enabled and self.client is not None
    
    def get_target_info(self) -> Dict[str, Any]:
        """Get information about the SSH target.
        
        Returns:
            Dict[str, Any]: SSH target information
        """
        return {
            "hostname": self.host,
            "port": self.port,
            "username": self.username,
            "connected": self.client is not None
        }
    
    def connect(self) -> bool:
        """Connect to the SSH server.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("SSH execution is disabled")
            return False
        
        try:
            logger.info(f"Connecting to SSH server {self.host}:{self.port}")
            
            # Create a new SSH client
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try to connect with key first, then password
            try:
                self.client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_path,
                    timeout=self.timeout
                )
                logger.info(f"Connected to SSH server {self.host} using key authentication")
                return True
            except Exception as e:
                logger.warning(f"Failed to connect using key authentication: {str(e)}")
                
                # Try password authentication if key authentication failed
                if self.password:
                    try:
                        self.client.connect(
                            hostname=self.host,
                            port=self.port,
                            username=self.username,
                            password=self.password,
                            timeout=self.timeout
                        )
                        logger.info(f"Connected to SSH server {self.host} using password authentication")
                        return True
                    except Exception as e:
                        logger.error(f"Failed to connect using password authentication: {str(e)}")
                
                # If both authentication methods failed, close the client
                self.client.close()
                self.client = None
                return False
        
        except Exception as e:
            logger.error(f"Error connecting to SSH server: {str(e)}")
            if self.client:
                self.client.close()
                self.client = None
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the SSH server."""
        if self.client:
            logger.info(f"Disconnecting from SSH server {self.host}")
            client = self.client  # Store a reference to the client
            self.client = None    # Set client to None first
            client.close()        # Then close the stored reference
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test the SSH connection.
        
        Returns:
            Tuple[bool, str]: Success status and message
        """
        if not self.enabled:
            return False, "SSH execution is disabled"
        
        # Try to connect
        if not self.client and not self.connect():
            return False, "Failed to connect to SSH server"
        
        try:
            # Execute a simple command to test the connection
            stdin, stdout, stderr = self.client.exec_command("echo 'SSH connection test'")
            exit_code = stdout.channel.recv_exit_status()
            
            if exit_code == 0:
                return True, "SSH connection test successful"
            else:
                stderr_output = stderr.read().decode('utf-8').strip()
                return False, f"SSH connection test failed with exit code {exit_code}: {stderr_output}"
        
        except Exception as e:
            logger.error(f"Error testing SSH connection: {str(e)}")
            return False, f"Error testing SSH connection: {str(e)}"
    
    async def execute(self, 
                     command: str, 
                     command_id: Optional[str] = None,
                     progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command via SSH and return the result.
        
        Args:
            command: The command to execute
            command_id: Optional ID for the command
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Command execution result
        """
        if not self.enabled:
            logger.warning("SSH execution is disabled")
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'error',
                'progress': 100,
                'message': 'SSH execution is disabled',
                'timestamp': datetime.now(UTC).isoformat()
            })
            return self._create_base_result(
                command=command,
                exit_code=-1,
                stdout="",
                stderr="SSH execution is disabled",
                execution_type="ssh",
                target=f"{self.username}@{self.host}"
            )
        
        try:
            # Send initial progress update
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'connecting',
                'progress': 10,
                'message': f'Connecting to SSH server {self.host}',
                'timestamp': datetime.now(UTC).isoformat()
            })
            
            # Connect to SSH server if not already connected
            if not self.client and not self.connect():
                await self._send_progress_update(command_id, progress_callback, {
                    'status': 'error',
                    'progress': 100,
                    'message': 'Failed to connect to SSH server',
                    'timestamp': datetime.now(UTC).isoformat()
                })
                return self._create_base_result(
                    command=command,
                    exit_code=-1,
                    stdout="",
                    stderr="Failed to establish SSH connection",
                    execution_type="ssh",
                    target=f"{self.username}@{self.host}"
                )
            
            # Send progress update
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'running',
                'progress': 30,
                'message': f'Executing command via SSH: {command}',
                'timestamp': datetime.now(UTC).isoformat()
            })
            
            # Execute the command
            logger.info(f"Executing command via SSH: {command}")
            stdin, stdout, stderr = self.client.exec_command(command)
            
            # Read output
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            exit_code = stdout.channel.recv_exit_status()
            
            # Send final progress update
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'completed',
                'progress': 100,
                'message': f'Command completed with exit code {exit_code}',
                'timestamp': datetime.now(UTC).isoformat()
            })
            
            # Create the result
            result = self._create_base_result(
                command=command,
                exit_code=exit_code,
                stdout=stdout_data,
                stderr=stderr_data,
                execution_type="ssh",
                target=f"{self.username}@{self.host}"
            )
            
            logger.info(f"Command executed via SSH with exit code: {exit_code}")
            return result
        
        except Exception as e:
            logger.error(f"Error executing SSH command: {str(e)}")
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'error',
                'progress': 100,
                'message': f'Error executing SSH command: {str(e)}',
                'timestamp': datetime.now(UTC).isoformat()
            })
            return self._create_base_result(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Error executing SSH command: {str(e)}",
                execution_type="ssh",
                target=f"{self.username}@{self.host}"
            ) 