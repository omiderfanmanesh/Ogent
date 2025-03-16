"""Information-related API models."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class InfoResponse(BaseModel):
    """Information response model."""
    version: str = Field(..., description="Agent version")
    hostname: str = Field(..., description="Agent hostname")
    platform: str = Field(..., description="Agent platform")
    python_version: str = Field(..., description="Python version")


class ExecutorInfo(BaseModel):
    """Executor information model."""
    type: str = Field(..., description="Executor type")
    available: bool = Field(..., description="Whether the executor is available")
    target: Dict[str, Any] = Field(..., description="Target information")
    description: Optional[str] = Field(None, description="Executor description") 