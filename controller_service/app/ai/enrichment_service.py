import json
import logging
from typing import Dict, Any
from .base import AIServiceBase

# Configure logging
logger = logging.getLogger("enrichment_service")

class EnrichmentService(AIServiceBase):
    """Service for enriching commands with additional context and information"""
    
    async def process(self, command: str, system: str = "Linux") -> Dict[str, Any]:
        """Enrich a command with additional context and information
        
        Args:
            command: The command to enrich
            system: The target system type
            
        Returns:
            Dict[str, Any]: Enrichment result with additional information
        """
        if not self.is_enabled():
            logger.warning("AI features are disabled, skipping command enrichment")
            return {
                "purpose": "Unknown (AI enrichment is disabled)",
                "components": [],
                "side_effects": [],
                "prerequisites": [],
                "related_commands": []
            }
        
        try:
            logger.info(f"Enriching command: {command}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a shell command expert. "
                     "Analyze the command and provide additional context and information."},
                    {"role": "user", "content": f"Please enrich the following command with additional context:\n\n"
                     f"Command: {command}\n\n"
                     f"Target system: {system}\n\n"
                     f"Provide your enrichment in JSON format with the following fields:\n"
                     f"- purpose: the likely purpose of the command\n"
                     f"- components: breakdown of command components and their functions\n"
                     f"- side_effects: potential side effects of running this command\n"
                     f"- prerequisites: prerequisites for running this command\n"
                     f"- related_commands: related commands that might be useful\n"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON result
            try:
                enrichment = json.loads(response.choices[0].message.content)
                logger.info(f"Command enrichment result: {enrichment}")
                return enrichment
            except json.JSONDecodeError:
                logger.error(f"Error parsing enrichment result: {response}")
                return {
                    "purpose": "Unknown",
                    "components": [],
                    "side_effects": [],
                    "prerequisites": [],
                    "related_commands": []
                }
        
        except Exception as e:
            logger.error(f"Error enriching command: {str(e)}")
            return {
                "purpose": "Unknown",
                "components": [],
                "side_effects": [],
                "prerequisites": [],
                "related_commands": []
            } 