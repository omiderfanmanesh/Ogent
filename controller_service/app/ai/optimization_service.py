import json
import logging
from typing import Dict, Any
from .base import AIServiceBase

# Configure logging
logger = logging.getLogger("optimization_service")

class OptimizationService(AIServiceBase):
    """Service for optimizing commands for better performance and readability"""
    
    async def process(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Optimize a command for better performance and readability
        
        Args:
            command: The command to optimize
            system: The target system type
            context: The execution context
            
        Returns:
            Dict[str, Any]: Optimization result with improved command
        """
        if not self.is_enabled():
            logger.warning("AI features are disabled, skipping command optimization")
            return {
                "optimized_command": command,
                "improvements": ["AI optimization is disabled"],
                "explanation": "AI optimization is disabled"
            }
        
        try:
            logger.info(f"Optimizing command: {command}")
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a shell command optimization expert. "
                     "Analyze the command and suggest optimizations for better performance, "
                     "readability, and maintainability."},
                    {"role": "user", "content": f"Please optimize the following command:\n\n"
                     f"Command: {command}\n\n"
                     f"Target system: {system}\n\n"
                     f"Execution context: {context}\n\n"
                     f"Provide your optimization in JSON format with the following fields:\n"
                     f"- optimized_command: the optimized version of the command\n"
                     f"- improvements: array of improvements made\n"
                     f"- explanation: explanation of the optimizations\n"}
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON result
            try:
                optimization = json.loads(response.choices[0].message.content)
                logger.info(f"Command optimization result: {optimization}")
                return optimization
            except json.JSONDecodeError:
                logger.error(f"Error parsing optimization result: {response}")
                return {
                    "optimized_command": command,
                    "improvements": ["Error parsing optimization result"],
                    "explanation": "Error parsing optimization result"
                }
        
        except Exception as e:
            logger.error(f"Error optimizing command: {str(e)}")
            return {
                "optimized_command": command,
                "improvements": [f"Error optimizing command: {str(e)}"],
                "explanation": f"Error optimizing command: {str(e)}"
            } 