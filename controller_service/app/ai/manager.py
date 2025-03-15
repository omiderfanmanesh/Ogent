import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .validation_service import ValidationService
from .optimization_service import OptimizationService
from .enrichment_service import EnrichmentService

# Configure logging
logger = logging.getLogger("ai_manager")

class AIManager:
    """AI Manager for command enrichment, validation, and optimization"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI Manager with its component services
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
        """
        # Initialize services
        self.validation_service = ValidationService(api_key)
        self.optimization_service = OptimizationService(api_key)
        self.enrichment_service = EnrichmentService(api_key)
        
        # Manager is enabled if at least one service is enabled
        self.enabled = (
            self.validation_service.is_enabled() or
            self.optimization_service.is_enabled() or
            self.enrichment_service.is_enabled()
        )
        
        if self.enabled:
            logger.info("AI Manager initialized successfully")
        else:
            logger.warning("AI Manager initialized but all services are disabled")
    
    @property
    def is_enabled(self) -> bool:
        """Check if the AI Manager is enabled
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.enabled
    
    async def validate_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Validate a command for security risks
        
        Args:
            command: The command to validate
            system: The target system type
            context: The execution context
            
        Returns:
            Dict[str, Any]: Validation result
        """
        return await self.validation_service.process(command, system, context)
    
    async def optimize_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Optimize a command for better performance and readability
        
        Args:
            command: The command to optimize
            system: The target system type
            context: The execution context
            
        Returns:
            Dict[str, Any]: Optimization result
        """
        return await self.optimization_service.process(command, system, context)
    
    async def enrich_command(self, command: str, system: str = "Linux") -> Dict[str, Any]:
        """Enrich a command with additional context and information
        
        Args:
            command: The command to enrich
            system: The target system type
            
        Returns:
            Dict[str, Any]: Enrichment result
        """
        return await self.enrichment_service.process(command, system)
    
    async def process_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Process a command with validation, optimization, and enrichment
        
        Args:
            command: The command to process
            system: The target system type
            context: The execution context
            
        Returns:
            Dict[str, Any]: Processed command result
        """
        if not self.enabled:
            logger.warning("AI features are disabled, skipping command processing")
            return {
                "original_command": command,
                "processed_command": command,
                "validation": {
                    "safe": True,
                    "risk_level": "unknown",
                    "risks": ["AI validation is disabled"],
                    "suggestions": []
                },
                "optimization": {
                    "optimized_command": command,
                    "improvements": ["AI optimization is disabled"],
                    "explanation": "AI optimization is disabled"
                },
                "enrichment": {
                    "purpose": "Unknown (AI enrichment is disabled)",
                    "components": [],
                    "side_effects": [],
                    "prerequisites": [],
                    "related_commands": []
                }
            }
        
        try:
            logger.info(f"Processing command: {command}")
            
            # Validate the command
            validation = await self.validate_command(command, system, context)
            
            # Optimize the command if it's safe
            if validation.get("safe", False):
                optimization = await self.optimize_command(command, system, context)
                processed_command = optimization.get("optimized_command", command)
            else:
                optimization = {
                    "optimized_command": command,
                    "improvements": ["Command not optimized due to security risks"],
                    "explanation": "Command not optimized due to security risks"
                }
                processed_command = command
            
            # Enrich the command
            enrichment = await self.enrich_command(command, system)
            
            # Return the processed command
            return {
                "original_command": command,
                "processed_command": processed_command,
                "validation": validation,
                "optimization": optimization,
                "enrichment": enrichment,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                "original_command": command,
                "processed_command": command,
                "validation": {
                    "safe": False,
                    "risk_level": "unknown",
                    "risks": [f"Error processing command: {str(e)}"],
                    "suggestions": []
                },
                "optimization": {
                    "optimized_command": command,
                    "improvements": [],
                    "explanation": f"Error processing command: {str(e)}"
                },
                "enrichment": {
                    "purpose": "Unknown",
                    "components": [],
                    "side_effects": [],
                    "prerequisites": [],
                    "related_commands": []
                },
                "timestamp": datetime.utcnow().isoformat()
            } 