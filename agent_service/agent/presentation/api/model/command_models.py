"""Command-related API models."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    """Command execution request model."""
    command: str = Field(..., description="Command to execute")
    executor_type: str = Field("local", description="Executor type (local or ssh)")
    with_progress: bool = Field(False, description="Whether to receive progress updates")


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


class WebSocketRedirectResponse(BaseModel):
    """WebSocket redirect response model."""
    status: str = Field("redirect", description="Response status")
    message: str = Field(..., description="Response message")
    websocket_url: str = Field(..., description="WebSocket URL for progress updates")


class ProgressResponse(BaseModel):
    """Progress update response model."""
    status: str = Field(..., description="Progress status")
    progress: int = Field(..., description="Progress percentage")
    message: str = Field(..., description="Progress message")
    timestamp: str = Field(..., description="Progress timestamp")
    command_id: str = Field(..., description="Command ID")
    requester_sid: Optional[str] = Field(None, description="Requester session ID") 