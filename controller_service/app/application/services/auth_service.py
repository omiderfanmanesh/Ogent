"""Auth service for the controller service."""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from jose import jwt, JWTError

from ...domain.models.user import User
from ...domain.interfaces.user_repository import UserRepositoryInterface
from ..dtos.user_dto import UserDTO, TokenDTO

logger = logging.getLogger("controller.auth_service")


class AuthService:
    """Service for authentication and authorization."""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        """Initialize the auth service.
        
        Args:
            user_repository: User repository
        """
        self.user_repository = user_repository
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-for-development-only")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Optional[User]: The authenticated user, or None if authentication fails
        """
        return await self.user_repository.authenticate_user(username, password)
    
    async def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create an access token.
        
        Args:
            data: Token data
            expires_delta: Optional expiration time
            
        Returns:
            str: Access token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a token.
        
        Args:
            token: Token to verify
            
        Returns:
            Optional[Dict[str, Any]]: Token payload, or None if verification fails
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            logger.warning("Invalid token")
            return None
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get the current user from a token.
        
        Args:
            token: Token
            
        Returns:
            Optional[User]: The current user, or None if the token is invalid
        """
        payload = await self.verify_token(token)
        if not payload:
            return None
        
        username = payload.get("sub")
        if not username:
            return None
        
        return await self.user_repository.get_user(username)
    
    async def login(self, username: str, password: str) -> Optional[TokenDTO]:
        """Login a user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Optional[TokenDTO]: Token, or None if login fails
        """
        user = await self.authenticate_user(username, password)
        if not user:
            logger.warning(f"Authentication failed for user: {username}")
            return None
        
        if user.disabled:
            logger.warning(f"User is disabled: {username}")
            return None
        
        access_token = await self.create_access_token(
            data={"sub": user.username}
        )
        
        return TokenDTO(
            access_token=access_token,
            token_type="bearer"
        ) 