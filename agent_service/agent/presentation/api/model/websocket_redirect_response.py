"""WebSocket redirect response model."""

from pydantic import BaseModel, Field


class WebSocketRedirectResponse(BaseModel):
    """WebSocket redirect response model."""
    status: str = Field("redirect", description="Response status")
    message: str = Field(..., description="Response message")
    websocket_url: str = Field(..., description="WebSocket URL for progress updates") 