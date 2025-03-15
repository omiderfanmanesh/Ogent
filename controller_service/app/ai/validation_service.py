import json
import logging
from typing import Dict, Any
from .base import AIServiceBase

# Configure logging
logger = logging.getLogger("validation_service")

class ValidationService(AIServiceBase):
    """Service for validating commands for security risks"""
    
    async def process(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Validate a command for security risks
        
        Args:
            command: The command to validate
            system: The target system type
            context: The execution context
            
        Returns:
            Dict[str, Any]: Validation result with safety assessment
        """
        if not self.is_enabled():
            logger.warning("AI features are disabled, skipping command validation")
            return {
                "safe": True,
                "risk_level": "unknown",
                "risks": ["AI validation is disabled"],
                "suggestions": []
            }
        
        try:
            logger.info(f"Validating command: {command}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a security expert tasked with validating shell commands. "
                     "Analyze the command for security risks, potential harmful operations, "
                     "and suggest safer alternatives if needed."},
                    {"role": "user", "content": f"Please validate the following command for security risks:\n\n"
                     f"Command: {command}\n\n"
                     f"Target system: {system}\n\n"
                     f"Execution context: {context}\n\n"
                     f"Provide your analysis in JSON format with the following fields:\n"
                     f"- safe: boolean indicating if the command is safe to execute\n"
                     f"- risk_level: low, medium, or high\n"
                     f"- risks: array of identified risks\n"
                     f"- suggestions: array of safer alternatives or improvements\n"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON result
            try:
                validation = json.loads(response.choices[0].message.content)
                logger.info(f"Command validation result: {validation}")
                return validation
            except json.JSONDecodeError:
                logger.error(f"Error parsing validation result: {response}")
                return {
                    "safe": False,
                    "risk_level": "unknown",
                    "risks": ["Error parsing validation result"],
                    "suggestions": []
                }
        
        except Exception as e:
            logger.error(f"Error validating command: {str(e)}")
            return {
                "safe": False,
                "risk_level": "unknown",
                "risks": [f"Error validating command: {str(e)}"],
                "suggestions": []
            } 