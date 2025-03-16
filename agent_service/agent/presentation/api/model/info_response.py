"""Information response model."""

from pydantic import BaseModel, Field


class InfoResponse(BaseModel):
    """Information response model."""
    version: str = Field(..., description="Agent version")
    hostname: str = Field(..., description="Agent hostname")
    platform: str = Field(..., description="Agent platform")
    python_version: str = Field(..., description="Python version") 