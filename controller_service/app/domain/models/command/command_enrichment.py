"""Command enrichment model."""

from dataclasses import dataclass, field
from typing import Dict, Any, List

from controller_service.app.domain.models.command.command_component import CommandComponent


@dataclass
class CommandEnrichment:
    """Command enrichment results."""
    
    purpose: str
    components: List[CommandComponent] = field(default_factory=list)
    side_effects: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the enrichment to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the enrichment
        """
        return {
            "purpose": self.purpose,
            "components": [component.to_dict() for component in self.components],
            "side_effects": self.side_effects,
            "prerequisites": self.prerequisites,
            "related_commands": self.related_commands
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandEnrichment':
        """Create an enrichment from a dictionary.
        
        Args:
            data: Dictionary representation of the enrichment
            
        Returns:
            CommandEnrichment: Enrichment instance
        """
        components = [
            CommandComponent.from_dict(component)
            for component in data.get("components", [])
        ]
        
        return cls(
            purpose=data.get("purpose", ""),
            components=components,
            side_effects=data.get("side_effects", []),
            prerequisites=data.get("prerequisites", []),
            related_commands=data.get("related_commands", [])
        ) 