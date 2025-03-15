"""User repository interface for the controller service."""

import abc
from typing import Dict, Any, List, Optional
from ..models.user import User


class UserRepositoryInterface(abc.ABC):
    """Interface for user repositories."""
    
    @abc.abstractmethod
    async def add_user(self, user: User) -> None:
        """Add a user to the repository.
        
        Args:
            user: The user to add
        """
        pass
    
    @abc.abstractmethod
    async def get_user(self, username: str) -> Optional[User]:
        """Get a user by username.
        
        Args:
            username: The username of the user to get
            
        Returns:
            Optional[User]: The user, or None if not found
        """
        pass
    
    @abc.abstractmethod
    async def get_all_users(self) -> List[User]:
        """Get all users.
        
        Returns:
            List[User]: List of all users
        """
        pass
    
    @abc.abstractmethod
    async def update_user(self, user: User) -> None:
        """Update a user in the repository.
        
        Args:
            user: The user to update
        """
        pass
    
    @abc.abstractmethod
    async def delete_user(self, username: str) -> None:
        """Delete a user from the repository.
        
        Args:
            username: The username of the user to delete
        """
        pass
    
    @abc.abstractmethod
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user.
        
        Args:
            username: The username of the user to authenticate
            password: The password to authenticate with
            
        Returns:
            Optional[User]: The authenticated user, or None if authentication fails
        """
        pass 