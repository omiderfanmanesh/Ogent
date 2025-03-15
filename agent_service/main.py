"""Main entry point for the Agent Service."""

import os
import asyncio
import logging
import requests
import time
from agent import agent_manager
from agent.client import start_agent_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("agent.main")

CONTROLLER_URL = os.getenv("CONTROLLER_URL", "http://controller:8001")

async def wait_for_controller():
    """Wait for the controller service to be ready."""
    max_retries = 30
    retry_delay = 2
    retries = 0
    
    while retries < max_retries:
        try:
            response = requests.get(f"{CONTROLLER_URL}/health")
            if response.status_code == 200:
                logger.info("Controller service is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        
        retries += 1
        logger.info(f"Waiting for controller service (attempt {retries}/{max_retries})")
        await asyncio.sleep(retry_delay)
    
    logger.error("Controller service not available after maximum retries")
    return False

async def main():
    """Main entry point."""
    try:
        logger.info("Starting agent service")
        
        # Wait for controller service to be ready
        if not await wait_for_controller():
            logger.error("Failed to connect to controller service. Exiting.")
            return 1
        
        # Start agent client
        logger.info("Starting agent client")
        await start_agent_client()
        
        return 0
    except KeyboardInterrupt:
        logger.info("Agent service stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code) 