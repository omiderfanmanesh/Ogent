from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import logging

from ..domain.auth.entities import User
from ..domain.auth.value_objects import Token, TokenType, Credentials
from ..domain.auth.services import PasswordHashingService, AuthenticationService

# This will be defined in the infrastructure layer
class UserRepository:
    """Interface for user repository."""
    async def save(self, user: User) -> None:
        """Save a user to the repository."""
        pass
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username."""
        pass
    
    async def find_all(self) -> List[User]:
        """Find all users."""
        pass
    
    async def delete(self, username: str) -> None:
        """Delete a user from the repository."""
        pass

# This will be defined in the infrastructure layer
class TokenRepository:
    """Interface for token repository."""
    async def save(self, token: Token) -> None:
        """Save a token to the repository."""
        pass
    
    async def find_by_value(self, token_value: str) -> Optional[Token]:
        """Find a token by value."""
        pass
    
    async def delete(self, token_value: str) -> None:
        """Delete a token from the repository."""
        pass
    
    async def delete_for_user(self, user_id: str) -> None:
        """Delete all tokens for a user."""
        pass

class AuthApplicationService:
    """
    Application service for authentication.
    """
    def __init__(
        self,
        user_repository: UserRepository,
        token_repository: TokenRepository,
        password_service: PasswordHashingService,
        auth_service: AuthenticationService,
        logger: Optional[logging.Logger] = None,
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7
    ):
        self.user_repository = user_repository
        self.token_repository = token_repository
        self.password_service = password_service
        self.auth_service = auth_service
        self.logger = logger or logging.getLogger(__name__)
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
    
    async def register_user(
        self,
        username: str,
        password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        roles: List[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            username: The username for the new user
            password: The password for the new user
            email: Optional email for the new user
            full_name: Optional full name for the new user
            roles: Optional roles for the new user
            
        Returns:
            Dict[str, Any]: Response with registration status
        """
        try:
            # Check if user already exists
            existing_user = await self.user_repository.find_by_username(username)
            if existing_user:
                self.logger.warning(f"User registration failed: Username already exists: {username}")
                return {
                    'status': 'error',
                    'message': 'Username already exists'
                }
            
            # Hash the password
            hashed_password = self.password_service.hash_password(password)
            
            # Create the user
            user = User(
                username=username,
                hashed_password=hashed_password,
                email=email,
                full_name=full_name,
                roles=roles or ["user"]
            )
            
            # Save the user
            await self.user_repository.save(user)
            
            self.logger.info(f"User registered: {username}")
            
            return {
                'status': 'success',
                'message': 'User registered successfully',
                'username': username
            }
        
        except Exception as e:
            self.logger.error(f"Error registering user: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error registering user: {str(e)}'
            }
    
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Authenticate a user and generate tokens.
        
        Args:
            username: The username to authenticate
            password: The password to authenticate
            
        Returns:
            Dict[str, Any]: Response with authentication status and tokens
        """
        try:
            # Find the user
            user = await self.user_repository.find_by_username(username)
            if not user:
                self.logger.warning(f"Authentication failed: User not found: {username}")
                return {
                    'status': 'error',
                    'message': 'Invalid username or password'
                }
            
            # Create credentials
            credentials = Credentials(username=username, password=password)
            
            # Authenticate the user
            if not self.auth_service.authenticate_user(credentials, user):
                self.logger.warning(f"Authentication failed: Invalid password for user: {username}")
                return {
                    'status': 'error',
                    'message': 'Invalid username or password'
                }
            
            # Update last login
            user.update_last_login()
            await self.user_repository.save(user)
            
            # Generate tokens
            access_token = self.auth_service.create_token(
                user,
                token_type=TokenType.ACCESS,
                expires_delta=timedelta(minutes=self.access_token_expire_minutes)
            )
            
            refresh_token = self.auth_service.create_token(
                user,
                token_type=TokenType.REFRESH,
                expires_delta=timedelta(days=self.refresh_token_expire_days)
            )
            
            # Save tokens
            await self.token_repository.save(access_token)
            await self.token_repository.save(refresh_token)
            
            self.logger.info(f"User authenticated: {username}")
            
            return {
                'status': 'success',
                'message': 'Authentication successful',
                'access_token': access_token.token_value,
                'token_type': 'bearer',
                'expires_in': self.access_token_expire_minutes * 60,
                'refresh_token': refresh_token.token_value,
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'roles': user.roles
                }
            }
        
        except Exception as e:
            self.logger.error(f"Error authenticating user: {str(e)}")
            return {
                'status': 'error',
                'message': f'Error authenticating user: {str(e)}'
            } 