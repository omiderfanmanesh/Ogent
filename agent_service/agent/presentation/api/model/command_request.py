"""Command request model."""

from pydantic import BaseModel, Field


class CommandRequest(BaseModel):
    """Command execution request model."""
    command: str = Field(..., description="Command to execute")
    executor_type: str = Field("local", description="Executor type (local or ssh)")
    with_progress: bool = Field(False, description="Whether to receive progress updates") 