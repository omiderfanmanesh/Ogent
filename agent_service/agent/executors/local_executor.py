"""Local executor for command execution."""

import os
import sys
import asyncio
import subprocess
import platform
import logging
from typing import Dict, Any, Optional, Callable, Awaitable
from datetime import datetime

from ..utils import UTC
from .base_executor import CommandExecutor

logger = logging.getLogger("agent.executor.local")

class LocalExecutor(CommandExecutor):
    """Executor for local command execution."""
    
    def __init__(self):
        """Initialize the local executor."""
        super().__init__()
        self.enabled = True
    
    def is_available(self) -> bool:
        """Check if the local executor is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        return self.enabled
    
    def get_target_info(self) -> Dict[str, Any]:
        """Get information about the local system.
        
        Returns:
            Dict[str, Any]: Local system information
        """
        return {
            "hostname": platform.node(),
            "platform": platform.system(),
            "version": platform.version(),
            "python_version": platform.python_version()
        }
    
    async def execute(self, 
                     command: str, 
                     command_id: Optional[str] = None,
                     progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command locally and return the result.
        
        Args:
            command: The command to execute
            command_id: Optional ID for the command
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Command execution result
        """
        try:
            logger.info(f"Executing command locally: {command}")
            
            # Create a platform-appropriate shell command
            if platform.system() == "Windows":
                shell = True
            else:
                shell = True  # Using shell=True for Unix-like systems for simplicity
                              # In production, you might want to use shell=False for security
            
            # Send initial progress update
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'running',
                'progress': 0,
                'message': 'Command started',
                'timestamp': datetime.now(UTC).isoformat()
            })
            
            # Execute the command
            process = subprocess.Popen(
                command,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Read output in real-time
            stdout_lines = []
            stderr_lines = []
            
            # Use asyncio to read output without blocking
            async def read_output():
                for i, line in enumerate(iter(process.stdout.readline, '')):
                    if line:
                        stdout_lines.append(line)
                        # Send progress update every 10 lines or when buffer reaches 1KB
                        if i % 10 == 0 or sum(len(l) for l in stdout_lines) > 1024:
                            await self._send_progress_update(command_id, progress_callback, {
                                'status': 'running',
                                'progress': 50,  # Arbitrary progress value
                                'stdout': ''.join(stdout_lines[-10:]),  # Send last 10 lines
                                'message': 'Command running',
                                'timestamp': datetime.now(UTC).isoformat()
                            })
                    await asyncio.sleep(0.01)  # Small sleep to avoid CPU hogging
                
                for i, line in enumerate(iter(process.stderr.readline, '')):
                    if line:
                        stderr_lines.append(line)
                        # Send progress update for stderr
                        if i % 10 == 0:
                            await self._send_progress_update(command_id, progress_callback, {
                                'status': 'running',
                                'progress': 75,  # Arbitrary progress value
                                'stderr': ''.join(stderr_lines[-10:]),  # Send last 10 lines
                                'message': 'Command running (with stderr output)',
                                'timestamp': datetime.now(UTC).isoformat()
                            })
                    await asyncio.sleep(0.01)  # Small sleep to avoid CPU hogging
            
            # Start reading output
            asyncio.create_task(read_output())
            
            # Wait for the process to complete
            exit_code = await asyncio.get_event_loop().run_in_executor(None, process.wait)
            
            # Get any remaining output
            stdout_remainder = process.stdout.read()
            stderr_remainder = process.stderr.read()
            
            if stdout_remainder:
                stdout_lines.append(stdout_remainder)
            if stderr_remainder:
                stderr_lines.append(stderr_remainder)
            
            # Combine all output
            stdout = ''.join(stdout_lines)
            stderr = ''.join(stderr_lines)
            
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
                stdout=stdout,
                stderr=stderr,
                execution_type="local",
                target=platform.node()
            )
            
            logger.info(f"Command executed with exit code: {exit_code}")
            return result
        
        except asyncio.TimeoutError:
            logger.error(f"Command timed out: {command}")
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'error',
                'progress': 100,
                'message': 'Command timed out',
                'timestamp': datetime.now(UTC).isoformat()
            })
            return self._create_base_result(
                command=command,
                exit_code=-1,
                stdout="",
                stderr="Command execution timed out",
                execution_type="local",
                target=platform.node()
            )
        
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            await self._send_progress_update(command_id, progress_callback, {
                'status': 'error',
                'progress': 100,
                'message': f'Error executing command: {str(e)}',
                'timestamp': datetime.now(UTC).isoformat()
            })
            return self._create_base_result(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Error executing command: {str(e)}",
                execution_type="local",
                target=platform.node()
            ) 