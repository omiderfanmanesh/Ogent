"""Command AI processing model."""

from dataclasses import dataclass
from typing import Dict, Any

from controller_service.app.domain.models.command.command_validation import CommandValidation
from controller_service.app.domain.models.command.command_optimization import CommandOptimization
from controller_service.app.domain.models.command.command_enrichment import CommandEnrichment


@dataclass
class CommandAIProcessing:
    """Command AI processing results."""
    
    original_command: str
    processed_command: str
    validation: CommandValidation
    optimization: CommandOptimization
    enrichment: CommandEnrichment
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the AI processing to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the AI processing
        """
        return {
            "original_command": self.original_command,
            "processed_command": self.processed_command,
            "validation": self.validation.to_dict(),
            "optimization": self.optimization.to_dict(),
            "enrichment": self.enrichment.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandAIProcessing':
        """Create an AI processing from a dictionary.
        
        Args:
            data: Dictionary representation of the AI processing
            
        Returns:
            CommandAIProcessing: AI processing instance
        """
        return cls(
            original_command=data.get("original_command", ""),
            processed_command=data.get("processed_command", ""),
            validation=CommandValidation.from_dict(data.get("validation", {})),
            optimization=CommandOptimization.from_dict(data.get("optimization", {})),
            enrichment=CommandEnrichment.from_dict(data.get("enrichment", {}))
        ) 