import os
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI

# Configure logging
logger = logging.getLogger("ai_manager")

class AIManager:
    """AI Manager for command enrichment, validation, and optimization"""
    
    def __init__(self):
        """Initialize the AI Manager"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        logger.info(f"API Key present: {self.api_key is not None}")
        
        self.enabled = self.api_key is not None
        
        if not self.enabled:
            logger.warning("OpenAI API key not provided, AI features are disabled")
            return
        
        try:
            # Initialize OpenAI client
            self.client = OpenAI(api_key=self.api_key)
            logger.info("AI Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing AI Manager: {str(e)}")
            self.enabled = False
    
    async def validate_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Validate a command for security risks"""
        if not self.enabled:
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
    
    async def optimize_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Optimize a command for better performance and readability"""
        if not self.enabled:
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
    
    async def enrich_command(self, command: str, system: str = "Linux") -> Dict[str, Any]:
        """Enrich a command with additional context and information"""
        if not self.enabled:
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
    
    async def process_command(self, command: str, system: str = "Linux", context: str = "Server administration") -> Dict[str, Any]:
        """Process a command with validation, optimization, and enrichment"""
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

# Create a singleton instance
ai_manager = AIManager() 