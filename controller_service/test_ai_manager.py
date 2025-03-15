import os
import asyncio
import logging
from app.ai_manager import AIManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_ai_manager")

# Set the API key
# IMPORTANT: Never hardcode API keys in your code
# Use environment variables or secure configuration methods
api_key = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
# For testing purposes only, you can set the API key here if not in environment
# os.environ["OPENAI_API_KEY"] = api_key

# If no API key is provided, log a warning
if api_key == "your-api-key-here":
    logger.warning("No OpenAI API key provided. Set the OPENAI_API_KEY environment variable.")
    logger.warning("Tests will not work without a valid API key.")

async def test_ai_manager():
    # Initialize the AI manager
    ai_manager = AIManager()
    
    # Check if the AI manager is enabled
    logger.info(f"AI Manager enabled: {ai_manager.enabled}")
    
    # Test the process_command method
    command = "ls -la"
    system = "Linux"
    context = "Server administration"
    
    logger.info(f"Processing command: {command}")
    result = await ai_manager.process_command(command, system, context)
    
    logger.info("Command processing result:")
    logger.info(f"Original command: {result.get('original_command')}")
    logger.info(f"Processed command: {result.get('processed_command')}")
    logger.info(f"Validation: {result.get('validation')}")
    logger.info(f"Optimization: {result.get('optimization')}")
    logger.info(f"Enrichment: {result.get('enrichment')}")

if __name__ == "__main__":
    asyncio.run(test_ai_manager()) 