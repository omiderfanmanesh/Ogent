"""Local executor for command execution."""

import asyncio
import shlex
import logging
import platform
import os
from typing import Dict, Any, Optional, Callable, Awaitable, List, Tuple
from datetime import datetime, UTC

from agent.infrastructure.executors.base_executor import BaseExecutor

logger = logging.getLogger("agent.executor.local")


class LocalExecutor(BaseExecutor):
    """Local command executor."""
    
    def __init__(self):
        """Initialize the local executor."""
        super().__init__()
        self.executor_type = "local"
        self.target_info = {
            "hostname": platform.node(),
            "platform": platform.system(),
            "version": platform.version(),
            "python_version": platform.python_version(),
            "cwd": os.getcwd()
        }
    
    async def _execute_command(self, 
                              command: str, 
                              result: Dict[str, Any],
                              progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Dict[str, Any]:
        """Execute a command locally and update the result.
        
        Args:
            command: The command to execute
            result: The result dictionary to update
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dict[str, Any]: Updated command execution result
        """
        logger.info(f"Executing local command: {command}")
        
        # Send initial progress update
        if progress_callback:
            await progress_callback({
                "progress": 0,
                "message": f"Executing command: {command}",
                "timestamp": datetime.now(UTC).isoformat()
            })
        
        try:
            # Parse the command
            if platform.system() == "Windows":
                # On Windows, we need to use shell=True
                cmd = command
                shell = True
            else:
                # On Unix-like systems, we can use shlex to parse the command
                cmd = shlex.split(command)
                shell = False
            
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=shell
            )
            
            # Send progress update
            if progress_callback:
                await progress_callback({
                    "progress": 10,
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
                                        process: asyncio.subprocess.Process,
                                        progress_callback: Optional[Callable[[Dict[str, Any]], Awaitable[None]]] = None) -> Tuple[str, str]:
        """Read output from the process with progress updates.
        
        Args:
            process: The process to read output from
            progress_callback: Optional callback for progress updates
            
        Returns:
            Tuple[str, str]: Stdout and stderr data
        """
        stdout_chunks: List[str] = []
        stderr_chunks: List[str] = []
        
        # Read stdout and stderr concurrently
        while process.returncode is None:
            # Check if there's data available on stdout
            if process.stdout.at_eof():
                stdout_chunk = b""
            else:
                try:
                    stdout_chunk = await asyncio.wait_for(process.stdout.read(1024), 0.1)
                except asyncio.TimeoutError:
                    stdout_chunk = b""
            
            # Check if there's data available on stderr
            if process.stderr.at_eof():
                stderr_chunk = b""
            else:
                try:
                    stderr_chunk = await asyncio.wait_for(process.stderr.read(1024), 0.1)
                except asyncio.TimeoutError:
                    stderr_chunk = b""
            
            # Append chunks to the output
            if stdout_chunk:
                stdout_chunks.append(stdout_chunk.decode("utf-8", errors="replace"))
            if stderr_chunk:
                stderr_chunks.append(stderr_chunk.decode("utf-8", errors="replace"))
            
            # Send progress update if there's new output
            if progress_callback and (stdout_chunk or stderr_chunk):
                await progress_callback({
                    "progress": 50,
                    "message": "Command in progress",
                    "timestamp": datetime.now(UTC).isoformat(),
                    "stdout": "".join(stdout_chunks),
                    "stderr": "".join(stderr_chunks)
                })
            
            # Check if the process has completed
            if not stdout_chunk and not stderr_chunk:
                await asyncio.sleep(0.1)
                if process.returncode is not None:
                    break
        
        # Read any remaining output
        stdout_chunk, stderr_chunk = await process.communicate()
        if stdout_chunk:
            stdout_chunks.append(stdout_chunk.decode("utf-8", errors="replace"))
        if stderr_chunk:
            stderr_chunks.append(stderr_chunk.decode("utf-8", errors="replace"))
        
        return "".join(stdout_chunks), "".join(stderr_chunks) 