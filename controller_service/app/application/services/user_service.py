"""User service for the controller service."""

import logging
import uuid
from typing import List, Optional

from ...domain.models.user import User
from ...domain.interfaces.user_repository import UserRepositoryInterface
from ..dtos.user_dto import UserDTO

logger = logging.getLogger("controller.user_service")


class UserService:
    """Service for user management."""
    
    def __init__(self, user_repository: UserRepositoryInterface):
        """Initialize the user service.
        
        Args:
            user_repository: User repository
        """
        self.user_repository = user_repository
    
    async def create_user(self, username: str, password: str, roles: List[str] = None) -> User:
        """Create a new user.
        
        Args:
            username: Username
            password: Password
            roles: User roles
            
        Returns:
            User: The created user
        """
        if roles is None:
            roles = ["user"]
        
        user = User(
            username=username,
            hashed_password="",  # Will be hashed by the repository
            roles=roles,
            disabled=False
        )
        
        created_user = await self.user_repository.create_user(user, password)
        logger.info(f"Created user: {username}")
        return created_user
    
    async def get_user(self, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            username: Username
            
        Returns:
            Optional[User]: The user, or None if not found
        """
        return await self.user_repository.get_user(username)
    
    async def get_all_users(self) -> List[User]:
        """Get all users.
        
        Returns:
            List[User]: List of all users
        """
        return await self.user_repository.get_all_users()
    
    async def update_user(self, username: str, user_data: UserDTO) -> Optional[User]:
        """Update a user.
        
        Args:
            username: Username
            user_data: User data
            
        Returns:
            Optional[User]: The updated user, or None if not found
        """
        user = await self.user_repository.get_user(username)
        if not user:
            logger.warning(f"User not found for update: {username}")
            return None
        
        # Update user fields
        if user_data.roles is not None:
            user.roles = user_data.roles
        
        if user_data.disabled is not None:
            user.disabled = user_data.disabled
        
        updated_user = await self.user_repository.update_user(user)
        logger.info(f"Updated user: {username}")
        return updated_user
    
    async def delete_user(self, username: str) -> bool:
        """Delete a user.
        
        Args:
            username: Username
            
        Returns:
            bool: True if deleted, False otherwise
        """
        result = await self.user_repository.delete_user(username)
        if result:
            logger.info(f"Deleted user: {username}")
        else:
            logger.warning(f"User not found for deletion: {username}")
        return result
    
    async def change_password(self, username: str, current_password: str, new_password: str) -> bool:
        """Change a user's password.
        
        Args:
            username: Username
            current_password: Current password
            new_password: New password
            
        Returns:
            bool: True if password changed, False otherwise
        """
        # First authenticate with current password
        user = await self.user_repository.authenticate_user(username, current_password)
        if not user:
            logger.warning(f"Password change failed - invalid current password: {username}")
            return False
        
        result = await self.user_repository.update_password(username, new_password)
        if result:
            logger.info(f"Changed password for user: {username}")
        return result 