from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

class TokenType(Enum):
    """
    Enumeration of possible token types.
    """
    ACCESS = "access"
    REFRESH = "refresh"

class Token:
    """
    Value object representing an authentication token.
    """
    def __init__(
        self,
        token_value: str,
        token_type: TokenType,
        expires_at: datetime,
        user_id: str,
        scopes: List[str] = None
    ):
        self.token_value = token_value
        self.token_type = token_type
        self.expires_at = expires_at
        self.user_id = user_id
        self.scopes = scopes or []
        self.created_at = datetime.utcnow()
    
    def is_expired(self) -> bool:
        """Check if the token is expired."""
        return datetime.utcnow() > self.expires_at
    
    def has_scope(self, scope: str) -> bool:
        """Check if the token has a specific scope."""
        return scope in self.scopes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the token to a dictionary."""
        return {
            'token_value': self.token_value,
            'token_type': self.token_type.value,
            'expires_at': self.expires_at.isoformat(),
            'user_id': self.user_id,
            'scopes': self.scopes,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Token':
        """Create a token from a dictionary."""
        token = cls(
            token_value=data['token_value'],
            token_type=TokenType(data['token_type']),
            expires_at=datetime.fromisoformat(data['expires_at']),
            user_id=data['user_id'],
            scopes=data.get('scopes', [])
        )
        
        if 'created_at' in data:
            token.created_at = datetime.fromisoformat(data['created_at'])
        
        return token

class Credentials:
    """
    Value object representing user credentials.
    """
    def __init__(
        self,
        username: str,
        password: str
    ):
        self.username = username
        self.password = password 