"""Authentication utilities for the API."""

import logging
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from agent.infrastructure.config.config import config

logger = logging.getLogger("agent.api.auth")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def authenticate(token: str = Depends(oauth2_scheme)) -> bool:
    """Authenticate the request.
    
    Args:
        token: OAuth2 token
        
    Returns:
        bool: True if authenticated
        
    Raises:
        HTTPException: If authentication fails
    """
    if token != config.api_token:
        logger.warning("Authentication failed with invalid token")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True 