from typing import Dict, Any, Optional, List
from datetime import datetime

class User:
    """
    User entity representing a user in the system.
    """
    def __init__(
        self,
        username: str,
        hashed_password: str,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        disabled: bool = False,
        roles: List[str] = None
    ):
        self.username = username
        self.hashed_password = hashed_password
        self.email = email
        self.full_name = full_name
        self.disabled = disabled
        self.roles = roles or ["user"]
        self.created_at = datetime.utcnow()
        self.last_login = None
    
    def has_role(self, role: str) -> bool:
        """Check if the user has a specific role."""
        return role in self.roles
    
    def update_last_login(self) -> None:
        """Update the user's last login time."""
        self.last_login = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the user to a dictionary."""
        return {
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'disabled': self.disabled,
            'roles': self.roles,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create a user from a dictionary."""
        user = cls(
            username=data['username'],
            hashed_password=data['hashed_password'],
            email=data.get('email'),
            full_name=data.get('full_name'),
            disabled=data.get('disabled', False),
            roles=data.get('roles', ["user"])
        )
        
        # Set timestamps
        if 'created_at' in data:
            user.created_at = datetime.fromisoformat(data['created_at'])
        
        if data.get('last_login'):
            user.last_login = datetime.fromisoformat(data['last_login'])
        
        return user 