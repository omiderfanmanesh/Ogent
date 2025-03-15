from typing import Dict, Any, Optional, List
import json
import logging

from ...domain.auth.entities import User
from ...application.auth_service import UserRepository

class RedisUserRepository(UserRepository):
    """
    Redis implementation of the user repository.
    """
    def __init__(self, redis_manager, logger: Optional[logging.Logger] = None):
        self.redis_manager = redis_manager
        self.logger = logger or logging.getLogger(__name__)
        self.key_prefix = "user:"
    
    async def save(self, user: User) -> None:
        """
        Save a user to Redis.
        
        Args:
            user: The user to save
        """
        try:
            # Save the user
            user_key = f"{self.key_prefix}{user.username}"
            user_dict = user.to_dict()
            
            # Add the hashed password to the dictionary
            user_dict['hashed_password'] = user.hashed_password
            
            await self.redis_manager.set(user_key, user_dict)
            
            # Add to users set
            await self.redis_manager.sadd("users", user.username)
            
            self.logger.debug(f"User saved: {user.username}")
        except Exception as e:
            self.logger.error(f"Error saving user: {str(e)}")
            raise
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by username.
        
        Args:
            username: The username of the user to find
            
        Returns:
            Optional[User]: The user if found, None otherwise
        """
        try:
            user_key = f"{self.key_prefix}{username}"
            user_data = await self.redis_manager.get(user_key)
            
            if not user_data:
                return None
            
            # Create user from data
            return User(
                username=user_data['username'],
                hashed_password=user_data['hashed_password'],
                email=user_data.get('email'),
                full_name=user_data.get('full_name'),
                disabled=user_data.get('disabled', False),
                roles=user_data.get('roles', ["user"])
            )
        except Exception as e:
            self.logger.error(f"Error finding user by username: {str(e)}")
            return None
    
    async def find_all(self) -> List[User]:
        """
        Find all users.
        
        Returns:
            List[User]: List of all users
        """
        try:
            # Get all usernames
            usernames = await self.redis_manager.smembers("users")
            
            users = []
            for username in usernames:
                user = await self.find_by_username(username)
                if user:
                    users.append(user)
            
            return users
        except Exception as e:
            self.logger.error(f"Error finding all users: {str(e)}")
            return []
    
    async def delete(self, username: str) -> None:
        """
        Delete a user from Redis.
        
        Args:
            username: The username of the user to delete
        """
        try:
            # Delete the user
            user_key = f"{self.key_prefix}{username}"
            await self.redis_manager.delete(user_key)
            
            # Remove from users set
            await self.redis_manager.srem("users", username)
            
            self.logger.debug(f"User deleted: {username}")
        except Exception as e:
            self.logger.error(f"Error deleting user: {str(e)}")
            raise 