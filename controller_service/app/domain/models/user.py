"""User model for the controller service."""

from dataclasses import dataclass
from typing import Dict, Any, Optional, List


@dataclass
class User:
    """User model representing a system user."""
    
    username: str
    hashed_password: str
    disabled: bool = False
    roles: List[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the user to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the user
        """
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "disabled": self.disabled,
            "roles": self.roles or []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a user from a dictionary.
        
        Args:
            data: Dictionary representation of the user
            
        Returns:
            User: User instance
        """
        return cls(
            username=data.get("username", ""),
            hashed_password=data.get("hashed_password", ""),
            disabled=data.get("disabled", False),
            roles=data.get("roles", [])
        ) 