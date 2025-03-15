"""API models for the agent service."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class CommandRequest(BaseModel):
    """Command execution request model."""
    command: str
    executor_type: str = "local"
    with_progress: bool = False


class CommandResponse(BaseModel):
    """Command execution response model."""
    command: str
    command_id: str
    exit_code: int
    stdout: str
    stderr: str
    timestamp: str
    execution_type: str
    target: str
    status: str


class ExecutorInfo(BaseModel):
    """Executor information model."""
    type: str
    available: bool
    target: Dict[str, Any]
    description: Optional[str] = None


class InfoResponse(BaseModel):
    """Information response model."""
    version: str
    hostname: str
    platform: str
    python_version: str 