"""Progress response model."""

from typing import Optional
from pydantic import BaseModel, Field


class ProgressResponse(BaseModel):
    """Progress update response model."""
    status: str = Field(..., description="Progress status")
    progress: int = Field(..., description="Progress percentage")
    message: str = Field(..., description="Progress message")
    timestamp: str = Field(..., description="Progress timestamp")
    command_id: str = Field(..., description="Command ID")
    requester_sid: Optional[str] = Field(None, description="Requester session ID") 