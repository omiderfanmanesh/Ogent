"""API routes for the agent service."""

import logging
from fastapi import APIRouter

from agent.presentation.api.info_routes import router as info_router
from agent.presentation.api.command_routes import router as command_router

logger = logging.getLogger("agent.api")

# Create main router
router = APIRouter(prefix="/agent")

# Include sub-routers
router.include_router(info_router)
router.include_router(command_router) 