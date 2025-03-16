"""Error response model."""

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Error response model."""
    status: str = Field("error", description="Response status")
    message: str = Field(..., description="Error message") 