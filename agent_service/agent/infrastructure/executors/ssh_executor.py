"""SSH executor for command execution."""

import asyncio
import logging
import os
from typing import Dict, Any, Optional, Callable, Awaitable, List, Tuple
from datetime import datetime, UTC

from agent.infrastructure.executors.base_executor import BaseExecutor
from agent.infrastructure.config.config import config

logger = logging.getLogger("agent.executor.ssh")

try:
    import asyncssh
    SSH_AVAILABLE = True
except ImportError:
    logger.warning("asyncssh not installed, SSH executor will not be available")
    SSH_AVAILABLE = False


class SSHExecutor(BaseExecutor):
    """SSH command executor."""
    
    def __init__(self, 
                host: str = None, 
                port: int = 22, 
                username: str = None, 
                password: str = None, 
                key_path: str = None,
                timeout: int = 10):
        """Initialize the SSH executor.
        
        Args:
            host: SSH host
            port: SSH port
            username: SSH username
            password: SSH password
            key_path: Path to SSH key file
            timeout: Connection timeout in seconds
        """
        super().__init__()
        self.executor_type = "ssh"
        
        # SSH connection parameters
        self.host = host or config.ssh_host
        self.port = int(port or config.ssh_port)
        self.username = username or config.ssh_username
        self.password = password or config.ssh_password
        self.key_path = key_path or config.ssh_key_path
        self.timeout = int(timeout or config.ssh_timeout)
        
        # Expand the key path
        if self.key_path:
            self.key_path = os.path.expanduser(self.key_path)
        
        # SSH connection
        self.connection = None
        self.connected = False
        
        # Target info
        self.target_info = {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "key_path": self.key_path,
            "connected": self.connected
        }
        
        # Connect to SSH server if enabled
        if config.ssh_enabled and SSH_AVAILABLE:
            asyncio.create_task(self.connect())
    
    async def connect(self) -> bool:
        """Connect to the SSH server.
        
        Returns:
            bool: True if connected successfully, False otherwise
        """
        if not SSH_AVAILABLE:
            logger.error("asyncssh not installed, cannot connect to SSH server")
            self.connected = False
            self.target_info["connected"] = False
            return False
        
        if not self.host:
            logger.error("SSH host not specified")
            self.connected = False
            self.target_info["connected"] = False
            return False
        
        try:
            logger.info(f"Connecting to SSH server {self.host}:{self.port}")
            
            # Connection options
            options = {
                "host": self.host,
                "port": self.port,
                "username": self.username,
                "connect_timeout": self.timeout
            }
            
            # Add password or key file
            if self.password:
                options["password"] = self.password
            elif self.key_path and os.path.exists(self.key_path):
                options["client_keys"] = [self.key_path]
            
            # Connect to the SSH server
            self.connection = await asyncssh.connect(**options)
            self.connected = True
            self.target_info["connected"] = True
            
            # Get target info
            try:
                # Get system information
                result = await self.connection.run("uname -a")
                if result.exit_status == 0:
                    self.target_info["system"] = result.stdout.strip()
                
                # Get hostname
                result = await self.connection.run("hostname")
                if result.exit_status == 0:
                    self.target_info["hostname"] = result.stdout.strip()
                
                # Get current directory
                result = await self.connection.run("pwd")
                if result.exit_status == 0:
                    self.target_info["cwd"] = result.stdout.strip()
            except Exception as e:
                logger.warning(f"Error getting target info: {str(e)}")
            
            logger.info(f"Connected to SSH server {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to SSH server: {str(e)}")
            self.connected = False
            self.target_info["connected"] = False
            self.target_info["error"] = str(e)
            return False
    
    async def _execute_command(self, 
                              command: str, 
                              result: Dict[str, Any],
                              progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command via SSH and update the result.
        
        Args:
            command: The command to execute
            result: The result dictionary to update
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Updated command execution result
        """
        logger.info(f"Executing SSH command: {command}")
        
        # Send initial progress update
        if progress_callback:
            await progress_callback({
                "progress": 0,
                "message": f"Executing command: {command}",
                "timestamp": datetime.now(UTC).isoformat()
            })
        
        # Check if connected
        if not self.connected:
            logger.warning("Not connected to SSH server, attempting to connect")
            connected = await self.connect()
            if not connected:
                logger.error("Failed to connect to SSH server")
                result["exit_code"] = 1
                result["stderr"] = "Failed to connect to SSH server"
                result["timestamp"] = datetime.now(UTC).isoformat()
                
                # Send error progress update
                if progress_callback:
                    await progress_callback({
                        "progress": 100,
                        "message": "Failed to connect to SSH server",
                        "timestamp": datetime.now(UTC).isoformat(),
                        "result": result
                    })
                
                return result
        
        try:
            # Send progress update
            if progress_callback:
                await progress_callback({
                    "progress": 10,
                    "message": "Connected to SSH server",
                    "timestamp": datetime.now(UTC).isoformat()
                })
            
            # Execute the command
            process = await self.connection.create_process(command)
            
            # Send progress update
            if progress_callback:
                await progress_callback({
                    "progress": 20,
                    "message": "Process started",
                    "timestamp": datetime.now(UTC).isoformat()
                })
            
            # Read output with progress updates
            stdout_data, stderr_data = await self._read_output_with_progress(process, progress_callback)
            
            # Wait for the process to complete
            exit_code = await process.wait()
            
            # Update the result
            result["exit_code"] = exit_code
            result["stdout"] = stdout_data
            result["stderr"] = stderr_data
            result["timestamp"] = datetime.now(UTC).isoformat()
            
            # Send final progress update
            if progress_callback:
                await progress_callback({
                    "progress": 100,
                    "message": f"Command completed with exit code {exit_code}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "result": result
                })
            
            logger.info(f"Command completed with exit code {exit_code}")
            
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            result["exit_code"] = 1
            result["stderr"] = f"Error executing command: {str(e)}"
            result["timestamp"] = datetime.now(UTC).isoformat()
            
            # Send error progress update
            if progress_callback:
                await progress_callback({
                    "progress": 100,
                    "message": f"Error executing command: {str(e)}",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "result": result
                })
        
        return result
    
    async def _read_output_with_progress(self, 
                                        process: 'asyncssh.SSHClientProcess',
                                        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Tuple[str, str]:
        """Read output from the SSH process with progress updates.
        
        Args:
            process: The SSH process to read output from
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple[str, str]: Stdout and stderr data
        """
        stdout_chunks: List[str] = []
        stderr_chunks: List[str] = []
        
        # Read stdout and stderr
        while not process.stdout.at_eof() or not process.stderr.at_eof():
            # Read from stdout
            if not process.stdout.at_eof():
                try:
                    stdout_chunk = await asyncio.wait_for(process.stdout.read(1024), 0.1)
                    if stdout_chunk:
                        stdout_chunks.append(stdout_chunk)
                except asyncio.TimeoutError:
                    pass
            
            # Read from stderr
            if not process.stderr.at_eof():
                try:
                    stderr_chunk = await asyncio.wait_for(process.stderr.read(1024), 0.1)
                    if stderr_chunk:
                        stderr_chunks.append(stderr_chunk)
                except asyncio.TimeoutError:
                    pass
            
            # Send progress update if there's new output
            if progress_callback and (stdout_chunks or stderr_chunks):
                await progress_callback({
                    "progress": 50,
                    "message": "Command in progress",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "stdout": "".join(stdout_chunks),
                    "stderr": "".join(stderr_chunks)
                })
            
            # Check if the process has completed
            if process.exit_status is not None and process.stdout.at_eof() and process.stderr.at_eof():
                break
            
            # Sleep to avoid busy waiting
            await asyncio.sleep(0.1)
        
        return "".join(stdout_chunks), "".join(stderr_chunks)
    
    def is_available(self) -> bool:
        """Check if the SSH executor is available.
        
        Returns:
            bool: True if the executor is available, False otherwise
        """
        return self.enabled and SSH_AVAILABLE and self.connected
    
    def cleanup(self) -> None:
        """Clean up resources used by the executor."""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.connected = False
            self.target_info["connected"] = False 