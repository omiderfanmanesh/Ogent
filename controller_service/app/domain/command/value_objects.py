from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime

class CommandStatus(Enum):
    """
    Enumeration of possible command statuses.
    """
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMEOUT = "timeout"

class ExecutionTarget(Enum):
    """
    Enumeration of possible execution targets.
    """
    AUTO = "auto"
    LOCAL = "local"
    SSH = "ssh"

class CommandResult:
    """
    Value object representing the result of a command execution.
    """
    def __init__(
        self,
        stdout: str,
        stderr: str,
        exit_code: int,
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.execution_time = execution_time
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary."""
        return {
            'stdout': self.stdout,
            'stderr': self.stderr,
            'exit_code': self.exit_code,
            'execution_time': self.execution_time,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandResult':
        """Create a result from a dictionary."""
        result = cls(
            stdout=data.get('stdout', ''),
            stderr=data.get('stderr', ''),
            exit_code=data.get('exit_code', 0),
            execution_time=data.get('execution_time'),
            metadata=data.get('metadata', {})
        )
        
        if 'timestamp' in data:
            result.timestamp = datetime.fromisoformat(data['timestamp'])
        
        return result

class CommandValidationResult:
    """
    Value object representing the result of command validation.
    """
    def __init__(
        self,
        is_valid: bool,
        error_message: Optional[str] = None,
        warnings: Optional[list] = None,
        suggestions: Optional[list] = None
    ):
        self.is_valid = is_valid
        self.error_message = error_message
        self.warnings = warnings or []
        self.suggestions = suggestions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation result to a dictionary."""
        return {
            'is_valid': self.is_valid,
            'error_message': self.error_message,
            'warnings': self.warnings,
            'suggestions': self.suggestions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandValidationResult':
        """Create a validation result from a dictionary."""
        return cls(
            is_valid=data.get('is_valid', True),
            error_message=data.get('error_message'),
            warnings=data.get('warnings', []),
            suggestions=data.get('suggestions', [])
        ) 