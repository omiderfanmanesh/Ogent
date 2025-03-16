"""Command validation DTO."""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class CommandValidationDTO:
    """Command validation data transfer object."""
    
    safe: bool
    risk_level: str
    risks: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the validation
        """
        return {
            "safe": self.safe,
            "risk_level": self.risk_level,
            "risks": self.risks,
            "suggestions": self.suggestions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandValidationDTO':
        """Create a validation from a dictionary.
        
        Args:
            data: Dictionary representation of the validation
            
        Returns:
            CommandValidationDTO: Validation instance
        """
        return cls(
            safe=data.get("safe", True),
            risk_level=data.get("risk_level", "unknown"),
            risks=data.get("risks", []),
            suggestions=data.get("suggestions", [])
        ) 