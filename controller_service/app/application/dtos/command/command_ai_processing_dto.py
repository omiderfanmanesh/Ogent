"""Command AI processing DTO."""

from dataclasses import dataclass
from typing import Dict, Any

from controller_service.app.application.dtos.command.command_validation_dto import CommandValidationDTO
from controller_service.app.application.dtos.command.command_optimization_dto import CommandOptimizationDTO
from controller_service.app.application.dtos.command.command_enrichment_dto import CommandEnrichmentDTO


@dataclass
class CommandAIProcessingDTO:
    """Command AI processing data transfer object."""
    
    original_command: str
    processed_command: str
    validation: CommandValidationDTO
    optimization: CommandOptimizationDTO
    enrichment: CommandEnrichmentDTO
    
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
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandAIProcessingDTO':
        """Create an AI processing from a dictionary.
        
        Args:
            data: Dictionary representation of the AI processing
            
        Returns:
            CommandAIProcessingDTO: AI processing instance
        """
        return cls(
            original_command=data.get("original_command", ""),
            processed_command=data.get("processed_command", ""),
            validation=CommandValidationDTO.from_dict(data.get("validation", {})),
            optimization=CommandOptimizationDTO.from_dict(data.get("optimization", {})),
            enrichment=CommandEnrichmentDTO.from_dict(data.get("enrichment", {}))
        ) 