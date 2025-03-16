"""Command component model."""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class CommandComponent:
    """Command component information."""
    
    component: str
    function: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the component
        """
        return {
            "component": self.component,
            "function": self.function
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandComponent':
        """Create a component from a dictionary.
        
        Args:
            data: Dictionary representation of the component
            
        Returns:
            CommandComponent: Component instance
        """
        return cls(
            component=data.get("component", ""),
            function=data.get("function", "")
        ) 