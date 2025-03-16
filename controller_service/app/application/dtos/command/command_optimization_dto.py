"""Command optimization DTO."""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class CommandOptimizationDTO:
    """Command optimization data transfer object."""
    
    optimized_command: str
    improvements: List[str] = field(default_factory=list)
    explanation: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the optimization to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the optimization
        """
        return {
            "optimized_command": self.optimized_command,
            "improvements": self.improvements,
            "explanation": self.explanation
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandOptimizationDTO':
        """Create an optimization from a dictionary.
        
        Args:
            data: Dictionary representation of the optimization
            
        Returns:
            CommandOptimizationDTO: Optimization instance
        """
        return cls(
            optimized_command=data.get("optimized_command", ""),
            improvements=data.get("improvements", []),
            explanation=data.get("explanation")
        ) 