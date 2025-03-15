"""User DTOs for the controller service."""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class UserDTO:
    """User data transfer object."""
    
    username: str
    disabled: bool = False
    roles: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the user to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the user
        """
        return {
            "username": self.username,
            "disabled": self.disabled,
            "roles": self.roles or []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserDTO':
        """Create a user from a dictionary.
        
        Args:
            data: Dictionary representation of the user
            
        Returns:
            UserDTO: User instance
        """
        return cls(
            username=data.get("username", ""),
            disabled=data.get("disabled", False),
            roles=data.get("roles", [])
        )


@dataclass
class UserCredentialsDTO:
    """User credentials data transfer object."""
    
    username: str
    password: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the user credentials to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the user credentials
        """
        return {
            "username": self.username,
            "password": self.password
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserCredentialsDTO':
        """Create user credentials from a dictionary.
        
        Args:
            data: Dictionary representation of the user credentials
            
        Returns:
            UserCredentialsDTO: User credentials instance
        """
        return cls(
            username=data.get("username", ""),
            password=data.get("password", "")
        )


@dataclass
class TokenDTO:
    """Token data transfer object."""
    
    access_token: str
    token_type: str = "bearer"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the token to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the token
        """
        return {
            "access_token": self.access_token,
            "token_type": self.token_type
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TokenDTO':
        """Create a token from a dictionary.
        
        Args:
            data: Dictionary representation of the token
            
        Returns:
            TokenDTO: Token instance
        """
        return cls(
            access_token=data.get("access_token", ""),
            token_type=data.get("token_type", "bearer")
        ) 