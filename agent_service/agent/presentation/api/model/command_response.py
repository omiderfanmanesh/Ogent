"""Command response model."""

from pydantic import BaseModel, Field


class CommandResponse(BaseModel):
    """Command execution response model."""
    command: str = Field(..., description="Command that was executed")
    command_id: str = Field(..., description="Unique command ID")
    exit_code: int = Field(..., description="Command exit code")
    stdout: str = Field("", description="Command standard output")
    stderr: str = Field("", description="Command standard error")
    timestamp: str = Field(..., description="Execution timestamp")
    execution_type: str = Field(..., description="Executor type used")
    target: str = Field(..., description="Execution target")
    status: str = Field(..., description="Execution status") 