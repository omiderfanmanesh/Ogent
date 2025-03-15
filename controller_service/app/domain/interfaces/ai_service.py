"""AI service interface for the controller service."""

import abc
from typing import Dict, Any, Optional
from ..models.command import CommandValidation, CommandOptimization, CommandEnrichment, CommandAIProcessing


class AIServiceInterface(abc.ABC):
    """Interface for AI services."""
    
    @abc.abstractmethod
    async def validate_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> CommandValidation:
        """Validate a command for security risks.
        
        Args:
            command: The command to validate
            system: The system the command will be executed on
            context: The context in which the command will be executed
            
        Returns:
            CommandValidation: Validation results
        """
        pass
    
    @abc.abstractmethod
    async def optimize_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> CommandOptimization:
        """Optimize a command for better performance and readability.
        
        Args:
            command: The command to optimize
            system: The system the command will be executed on
            context: The context in which the command will be executed
            
        Returns:
            CommandOptimization: Optimization results
        """
        pass
    
    @abc.abstractmethod
    async def enrich_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> CommandEnrichment:
        """Enrich a command with additional context and information.
        
        Args:
            command: The command to enrich
            system: The system the command will be executed on
            context: The context in which the command will be executed
            
        Returns:
            CommandEnrichment: Enrichment results
        """
        pass
    
    @abc.abstractmethod
    async def process_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> CommandAIProcessing:
        """Process a command with AI.
        
        Args:
            command: The command to process
            system: The system the command will be executed on
            context: The context in which the command will be executed
            
        Returns:
            CommandAIProcessing: AI processing results
        """
        pass
    
    @property
    @abc.abstractmethod
    def enabled(self) -> bool:
        """Check if the AI service is enabled.
        
        Returns:
            bool: True if the AI service is enabled, False otherwise
        """
        pass 