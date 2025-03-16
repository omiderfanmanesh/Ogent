"""API module for the agent service."""

from agent.presentation.api.routes import router
from agent.presentation.api.info_routes import router as info_router
from agent.presentation.api.command_routes import router as command_router
from agent.presentation.api.auth import authenticate
from agent.presentation.api.model import (
    CommandRequest,
    CommandResponse,
    WebSocketRedirectResponse,
    ProgressResponse,
    InfoResponse,
    ExecutorInfo,
    ErrorResponse
)

__all__ = [
    "router", 
    "info_router", 
    "command_router", 
    "authenticate",
    "CommandRequest",
    "CommandResponse",
    "WebSocketRedirectResponse",
    "ProgressResponse",
    "InfoResponse",
    "ExecutorInfo",
    "ErrorResponse"
]
