"""AI service for the controller service."""

import os
import logging
import json
from typing import Dict, Any, Optional, List, Tuple

from ...domain.interfaces.ai_service import AIServiceInterface
from ..dtos.command_dto import (
    CommandValidationDTO,
    CommandOptimizationDTO,
    CommandEnrichmentDTO,
    CommandAIProcessingDTO
)

logger = logging.getLogger("controller.ai_service")


class AIService:
    """Service for AI-related operations."""
    
    def __init__(self, ai_service_interface: Optional[AIServiceInterface] = None):
        """Initialize the AI service.
        
        Args:
            ai_service_interface: AI service interface implementation
        """
        self.ai_service = ai_service_interface
        self.enabled = self.ai_service is not None
        self.system_prompt = os.getenv("AI_SYSTEM_PROMPT", """
            You are an AI assistant specialized in analyzing shell commands.
            Your task is to analyze commands for safety, optimization, and provide enrichment information.
            Respond with structured JSON only.
        """)
    
    async def process_command(
        self, 
        command: str, 
        system: str = None,
        context: List[str] = None
    ) -> Optional[CommandAIProcessingDTO]:
        """Process a command with AI.
        
        Args:
            command: Command to process
            system: System information
            context: Command context (previous commands)
            
        Returns:
            Optional[CommandAIProcessingDTO]: AI processing results, or None if AI is disabled
        """
        if not self.enabled or not self.ai_service:
            logger.warning("AI service is disabled or not configured")
            return None
        
        try:
            # Prepare the prompt
            prompt = self._prepare_prompt(command, system, context)
            
            # Get AI response
            response = await self.ai_service.generate_response(
                system_prompt=self.system_prompt,
                user_prompt=prompt
            )
            
            # Parse the response
            return self._parse_ai_response(command, response)
            
        except Exception as e:
            logger.error(f"Error processing command with AI: {str(e)}")
            return None
    
    def _prepare_prompt(self, command: str, system: str = None, context: List[str] = None) -> str:
        """Prepare the prompt for the AI.
        
        Args:
            command: Command to process
            system: System information
            context: Command context (previous commands)
            
        Returns:
            str: Prepared prompt
        """
        prompt = f"Analyze this command: {command}\n\n"
        
        if system:
            prompt += f"System information: {system}\n\n"
        
        if context and len(context) > 0:
            prompt += "Previous commands:\n"
            for cmd in context:
                prompt += f"- {cmd}\n"
            prompt += "\n"
        
        prompt += """
        Provide a structured analysis with the following sections:
        1. Validation: Is the command safe to run? What are the risks?
        2. Optimization: Can the command be optimized? How?
        3. Enrichment: What is the purpose of the command? What are its components?
        
        Format your response as JSON with the following structure:
        {
            "validation": {
                "safe": true/false,
                "risk_level": "none/low/medium/high",
                "risks": ["risk1", "risk2"],
                "suggestions": ["suggestion1", "suggestion2"]
            },
            "optimization": {
                "optimized_command": "optimized version",
                "improvements": ["improvement1", "improvement2"],
                "explanation": "explanation of optimizations"
            },
            "enrichment": {
                "purpose": "purpose of the command",
                "components": [
                    {"component": "component1", "function": "function1"},
                    {"component": "component2", "function": "function2"}
                ],
                "side_effects": ["effect1", "effect2"],
                "prerequisites": ["prerequisite1", "prerequisite2"],
                "related_commands": ["related1", "related2"]
            }
        }
        """
        
        return prompt
    
    def _parse_ai_response(self, original_command: str, response: str) -> CommandAIProcessingDTO:
        """Parse the AI response.
        
        Args:
            original_command: Original command
            response: AI response
            
        Returns:
            CommandAIProcessingDTO: Parsed AI processing results
        """
        try:
            # Extract JSON from response (in case there's text before or after)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON found in AI response")
                return self._create_fallback_processing(original_command)
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            # Extract validation data
            validation = data.get("validation", {})
            validation_dto = CommandValidationDTO(
                safe=validation.get("safe", True),
                risk_level=validation.get("risk_level", "low"),
                risks=validation.get("risks", []),
                suggestions=validation.get("suggestions", [])
            )
            
            # Extract optimization data
            optimization = data.get("optimization", {})
            optimization_dto = CommandOptimizationDTO(
                optimized_command=optimization.get("optimized_command", original_command),
                improvements=optimization.get("improvements", []),
                explanation=optimization.get("explanation", "")
            )
            
            # Extract enrichment data
            enrichment = data.get("enrichment", {})
            components_data = enrichment.get("components", [])
            components = [
                CommandComponentDTO(
                    component=comp.get("component", ""),
                    function=comp.get("function", "")
                ) for comp in components_data
            ]
            
            enrichment_dto = CommandEnrichmentDTO(
                purpose=enrichment.get("purpose", ""),
                components=components,
                side_effects=enrichment.get("side_effects", []),
                prerequisites=enrichment.get("prerequisites", []),
                related_commands=enrichment.get("related_commands", [])
            )
            
            # Create the final DTO
            return CommandAIProcessingDTO(
                original_command=original_command,
                processed_command=optimization_dto.optimized_command,
                validation=validation_dto,
                optimization=optimization_dto,
                enrichment=enrichment_dto
            )
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._create_fallback_processing(original_command)
    
    def _create_fallback_processing(self, command: str) -> CommandAIProcessingDTO:
        """Create fallback processing results when AI fails.
        
        Args:
            command: Original command
            
        Returns:
            CommandAIProcessingDTO: Fallback processing results
        """
        validation = CommandValidationDTO(
            safe=True,
            risk_level="unknown",
            risks=["AI processing failed"],
            suggestions=["Manually verify the command"]
        )
        
        optimization = CommandOptimizationDTO(
            optimized_command=command,
            improvements=[],
            explanation="AI processing failed"
        )
        
        enrichment = CommandEnrichmentDTO(
            purpose="Unknown (AI processing failed)",
            components=[],
            side_effects=[],
            prerequisites=[],
            related_commands=[]
        )
        
        return CommandAIProcessingDTO(
            original_command=command,
            processed_command=command,
            validation=validation,
            optimization=optimization,
            enrichment=enrichment
        )


class CommandComponentDTO:
    """DTO for command components."""
    
    def __init__(self, component: str, function: str):
        """Initialize the command component DTO.
        
        Args:
            component: Component name
            function: Component function
        """
        self.component = component
        self.function = function
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "component": self.component,
            "function": self.function
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandComponentDTO':
        """Create from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            CommandComponentDTO: Created DTO
        """
        return cls(
            component=data.get("component", ""),
            function=data.get("function", "")
        ) 