from datetime import datetime
from typing import Dict, Any, Optional, List
import uuid

from ..command.value_objects import CommandStatus, CommandResult, ExecutionTarget

class Command:
    """
    Command entity representing a command to be executed by an agent.
    """
    def __init__(
        self,
        command_id: str,
        command_text: str,
        agent_id: str,
        requester_id: str,
        execution_target: ExecutionTarget = ExecutionTarget.AUTO,
        execution_context: Optional[Dict[str, Any]] = None
    ):
        self.command_id = command_id
        self.command_text = command_text
        self.agent_id = agent_id
        self.requester_id = requester_id
        self.execution_target = execution_target
        self.execution_context = execution_context or {}
        self.status = CommandStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.progress_updates = []
    
    def mark_as_executing(self) -> None:
        """Mark the command as executing."""
        self.status = CommandStatus.EXECUTING
        self.started_at = datetime.utcnow()
    
    def complete(self, result: CommandResult) -> None:
        """
        Mark the command as completed with the given result.
        
        Args:
            result: The result of the command execution
        """
        self.status = CommandStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.result = result
    
    def fail(self, error_message: str) -> None:
        """
        Mark the command as failed with the given error message.
        
        Args:
            error_message: The error message
        """
        self.status = CommandStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.result = CommandResult(
            stdout="",
            stderr=error_message,
            exit_code=1
        )
    
    def add_progress_update(self, progress: int, message: str, stdout: str = "", stderr: str = "") -> None:
        """
        Add a progress update to the command.
        
        Args:
            progress: The progress percentage (0-100)
            message: A message describing the progress
            stdout: Standard output from the command
            stderr: Standard error from the command
        """
        self.progress_updates.append({
            'timestamp': datetime.utcnow().isoformat(),
            'progress': progress,
            'message': message,
            'stdout': stdout,
            'stderr': stderr
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the command to a dictionary."""
        result_dict = None
        if self.result:
            result_dict = self.result.to_dict()
        
        return {
            'command_id': self.command_id,
            'command_text': self.command_text,
            'agent_id': self.agent_id,
            'requester_id': self.requester_id,
            'execution_target': self.execution_target.value,
            'execution_context': self.execution_context,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'result': result_dict,
            'progress_updates': self.progress_updates
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Command':
        """Create a command from a dictionary."""
        command = cls(
            command_id=data['command_id'],
            command_text=data['command_text'],
            agent_id=data['agent_id'],
            requester_id=data['requester_id'],
            execution_target=ExecutionTarget(data.get('execution_target', ExecutionTarget.AUTO.value)),
            execution_context=data.get('execution_context', {})
        )
        
        # Set status
        command.status = CommandStatus(data.get('status', CommandStatus.PENDING.value))
        
        # Set timestamps
        if 'created_at' in data:
            command.created_at = datetime.fromisoformat(data['created_at'])
        
        if data.get('started_at'):
            command.started_at = datetime.fromisoformat(data['started_at'])
        
        if data.get('completed_at'):
            command.completed_at = datetime.fromisoformat(data['completed_at'])
        
        # Set result
        if data.get('result'):
            command.result = CommandResult.from_dict(data['result'])
        
        # Set progress updates
        command.progress_updates = data.get('progress_updates', [])
        
        return command
    
    @staticmethod
    def generate_id() -> str:
        """Generate a unique command ID."""
        return str(uuid.uuid4()) 