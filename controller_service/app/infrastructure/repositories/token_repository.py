from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime

from ...domain.auth.entities import User
from ...domain.auth.value_objects import Token, TokenType
from ...application.auth_service import TokenRepository

class RedisTokenRepository(TokenRepository):
    """
    Redis implementation of the token repository.
    """
    def __init__(self, redis_manager, logger: Optional[logging.Logger] = None):
        self.redis_manager = redis_manager
        self.logger = logger or logging.getLogger(__name__)
        self.key_prefix = "token:"
        self.index_prefix = "index:token:"
    
    async def save(self, token: Token) -> None:
        """
        Save a token to Redis.
        
        Args:
            token: The token to save
        """
        try:
            # Save the token
            token_key = f"{self.key_prefix}{token.token_value}"
            await self.redis_manager.set(token_key, token.to_dict(), expire_seconds=self._get_ttl(token))
            
            # Add to user index
            user_index_key = f"{self.index_prefix}user:{token.user_id}"
            await self.redis_manager.sadd(user_index_key, token.token_value)
            
            # Add to type index
            type_index_key = f"{self.index_prefix}type:{token.token_type.value}"
            await self.redis_manager.sadd(type_index_key, token.token_value)
            
            self.logger.debug(f"Token saved: {token.token_value} for user {token.user_id}")
        except Exception as e:
            self.logger.error(f"Error saving token: {str(e)}")
            raise
    
    async def find_by_value(self, token_value: str) -> Optional[Token]:
        """
        Find a token by value.
        
        Args:
            token_value: The value of the token to find
            
        Returns:
            Optional[Token]: The token if found, None otherwise
        """
        try:
            token_key = f"{self.key_prefix}{token_value}"
            token_data = await self.redis_manager.get(token_key)
            
            if not token_data:
                return None
            
            return Token.from_dict(token_data)
        except Exception as e:
            self.logger.error(f"Error finding token by value: {str(e)}")
            return None
    
    async def find_by_user_id(self, user_id: str) -> List[Token]:
        """
        Find tokens by user ID.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[Token]: List of tokens for the user
        """
        try:
            # Get token values from user index
            user_index_key = f"{self.index_prefix}user:{user_id}"
            token_values = await self.redis_manager.smembers(user_index_key)
            
            tokens = []
            for token_value in token_values:
                token = await self.find_by_value(token_value)
                if token:
                    tokens.append(token)
            
            return tokens
        except Exception as e:
            self.logger.error(f"Error finding tokens by user ID: {str(e)}")
            return []
    
    async def delete(self, token_value: str) -> None:
        """
        Delete a token from Redis.
        
        Args:
            token_value: The value of the token to delete
        """
        try:
            # Get the token first to get the user ID and type
            token = await self.find_by_value(token_value)
            if not token:
                return
            
            # Delete the token
            token_key = f"{self.key_prefix}{token_value}"
            await self.redis_manager.delete(token_key)
            
            # Remove from user index
            user_index_key = f"{self.index_prefix}user:{token.user_id}"
            await self.redis_manager.srem(user_index_key, token_value)
            
            # Remove from type index
            type_index_key = f"{self.index_prefix}type:{token.token_type.value}"
            await self.redis_manager.srem(type_index_key, token_value)
            
            self.logger.debug(f"Token deleted: {token_value}")
        except Exception as e:
            self.logger.error(f"Error deleting token: {str(e)}")
            raise
    
    async def delete_for_user(self, user_id: str) -> None:
        """
        Delete all tokens for a user.
        
        Args:
            user_id: The ID of the user
        """
        try:
            # Get all tokens for the user
            tokens = await self.find_by_user_id(user_id)
            
            # Delete each token
            for token in tokens:
                await self.delete(token.token_value)
            
            # Delete the user index
            user_index_key = f"{self.index_prefix}user:{user_id}"
            await self.redis_manager.delete(user_index_key)
            
            self.logger.debug(f"All tokens deleted for user: {user_id}")
        except Exception as e:
            self.logger.error(f"Error deleting tokens for user: {str(e)}")
            raise
    
    def _get_ttl(self, token: Token) -> int:
        """
        Get the time-to-live for a token in seconds.
        
        Args:
            token: The token
            
        Returns:
            int: The TTL in seconds
        """
        now = datetime.utcnow()
        expires_at = token.expires_at
        
        # Calculate the time difference in seconds
        ttl = int((expires_at - now).total_seconds())
        
        # Ensure a minimum TTL
        return max(ttl, 60) 