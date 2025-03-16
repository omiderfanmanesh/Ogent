"""Executor information model."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class ExecutorInfo(BaseModel):
    """Executor information model."""
    type: str = Field(..., description="Executor type")
    available: bool = Field(..., description="Whether the executor is available")
    target: Dict[str, Any] = Field(..., description="Target information")
    description: Optional[str] = Field(None, description="Executor description") 