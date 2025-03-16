"""Authentication utilities for the agent API."""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from ..config import config

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
        logger.warning(f"Authentication failed with token: {token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True 