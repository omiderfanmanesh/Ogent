from typing import Dict, Any, Optional, List
import re
import shlex

from ..command.entities import Command
from ..command.value_objects import CommandStatus, CommandResult, ExecutionTarget, CommandValidationResult

class CommandValidationService:
    """
    Domain service for command validation.
    """
    def __init__(self):
        # Define patterns for potentially dangerous commands
        self.dangerous_patterns = [
            r"rm\s+-rf\s+/",  # Remove root directory
            r"dd\s+if=/dev/zero\s+of=/dev/sd[a-z]",  # Overwrite disk
            r":\(\)\{\s*:\|:\s*&\s*\};\s*:",  # Fork bomb
            r"chmod\s+-R\s+777\s+/",  # Chmod root directory
            r"mkfs\s+/dev/sd[a-z]",  # Format disk
            r"wget\s+.+\s*\|\s*bash",  # Download and execute
            r"curl\s+.+\s*\|\s*bash",  # Download and execute
        ]
    
    def validate_command(self, command_text: str, context: Dict[str, Any] = None) -> CommandValidationResult:
        """
        Validate a command for security and correctness.
        
        Args:
            command_text: The command text to validate
            context: Additional context for validation
            
        Returns:
            CommandValidationResult: The validation result
        """
        # Check for empty command
        if not command_text or not command_text.strip():
            return CommandValidationResult(
                is_valid=False,
                error_message="Command cannot be empty"
            )
        
        # Check for dangerous commands
        warnings = []
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command_text):
                return CommandValidationResult(
                    is_valid=False,
                    error_message="Command contains potentially dangerous operations",
                    warnings=["Command matches pattern for dangerous operations"]
                )
        
        # Check command syntax
        try:
            shlex.split(command_text)
        except ValueError as e:
            return CommandValidationResult(
                is_valid=False,
                error_message=f"Command syntax error: {str(e)}"
            )
        
        # Add warnings for commands that might be problematic
        if "sudo" in command_text:
            warnings.append("Command uses sudo, which may require interactive authentication")
        
        if "|" in command_text or ">" in command_text or "<" in command_text:
            warnings.append("Command uses shell redirection or pipes, which may behave differently in non-interactive shells")
        
        # Command is valid
        return CommandValidationResult(
            is_valid=True,
            warnings=warnings
        )

class CommandExecutionService:
    """
    Domain service for command execution.
    """
    def prepare_command_for_execution(
        self, 
        command: Command,
        agent_capabilities: List[Dict[str, Any]] = None
    ) -> Command:
        """
        Prepare a command for execution based on agent capabilities.
        
        Args:
            command: The command to prepare
            agent_capabilities: The capabilities of the agent
            
        Returns:
            Command: The prepared command
        """
        # If execution target is AUTO, determine the best target
        if command.execution_target == ExecutionTarget.AUTO:
            # Check if SSH is available and preferred
            ssh_available = False
            if agent_capabilities:
                for cap in agent_capabilities:
                    if cap.get('command_type') == 'ssh' and cap.get('enabled', False):
                        ssh_available = True
                        break
            
            # If SSH is available and the command might benefit from it, use SSH
            if ssh_available and self._should_use_ssh(command.command_text):
                command.execution_target = ExecutionTarget.SSH
            else:
                command.execution_target = ExecutionTarget.LOCAL
        
        return command
    
    def _should_use_ssh(self, command_text: str) -> bool:
        """
        Determine if a command should use SSH based on its content.
        
        Args:
            command_text: The command text
            
        Returns:
            bool: True if SSH should be used, False otherwise
        """
        # Commands that might benefit from SSH
        ssh_preferable_commands = [
            'apt', 'apt-get', 'yum', 'dnf',  # Package management
            'systemctl', 'service',  # Service management
            'ifconfig', 'ip',  # Network configuration
            'mount', 'umount',  # Filesystem operations
            'useradd', 'userdel',  # User management
        ]
        
        # Check if the command starts with any of the SSH preferable commands
        command_parts = shlex.split(command_text)
        if command_parts and any(command_parts[0] == cmd for cmd in ssh_preferable_commands):
            return True
        
        return False 