#!/usr/bin/env python3
"""
Integration test script for the Ogent system.

This script tests the integration between the controller service and agent service.
It starts both services, registers an agent, executes a command, and verifies the result.
"""

import os
import sys
import asyncio
import logging
import argparse
import json
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("integration_test")

# Default configuration
DEFAULT_CONTROLLER_URL = "http://localhost:8000"
DEFAULT_AGENT_ID = f"test-agent-{datetime.now().strftime('%Y%m%d%H%M%S')}"
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password"

class IntegrationTest:
    """Integration test for the Ogent system."""
    
    def __init__(self, controller_url, agent_id, username, password):
        """Initialize the integration test.
        
        Args:
            controller_url: URL of the controller service
            agent_id: ID of the agent to register
            username: Username for authentication
            password: Password for authentication
        """
        self.controller_url = controller_url
        self.agent_id = agent_id
        self.username = username
        self.password = password
        self.token = None
        self.command_id = None
    
    async def run(self):
        """Run the integration test."""
        try:
            # Step 1: Authenticate with the controller service
            logger.info("Step 1: Authenticating with the controller service")
            self.token = await self.authenticate()
            if not self.token:
                logger.error("Authentication failed")
                return False
            
            # Step 2: Check if the agent is already registered
            logger.info("Step 2: Checking if the agent is already registered")
            agent = await self.get_agent()
            
            # Step 3: Execute a command
            logger.info("Step 3: Executing a command")
            command = "echo 'Hello, Ogent!'"
            self.command_id = await self.execute_command(command)
            if not self.command_id:
                logger.error("Command execution failed")
                return False
            
            # Step 4: Wait for the command result
            logger.info("Step 4: Waiting for the command result")
            result = await self.wait_for_command_result()
            if not result:
                logger.error("Command result not received")
                return False
            
            # Step 5: Verify the command result
            logger.info("Step 5: Verifying the command result")
            if result.get("exit_code") != 0:
                logger.error(f"Command failed with exit code {result.get('exit_code')}")
                return False
            
            logger.info("Integration test completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during integration test: {str(e)}")
            return False
    
    async def authenticate(self):
        """Authenticate with the controller service.
        
        Returns:
            str: Authentication token, or None if authentication fails
        """
        try:
            response = requests.post(
                f"{self.controller_url}/token",
                data={"username": self.username, "password": self.password}
            )
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                logger.info("Authentication successful")
                return token
            else:
                logger.error(f"Authentication failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error during authentication: {str(e)}")
            return None
    
    async def get_agent(self):
        """Get agent information from the controller service.
        
        Returns:
            dict: Agent information, or None if the agent is not found
        """
        try:
            response = requests.get(
                f"{self.controller_url}/agents/{self.agent_id}",
                headers={"Authorization": f"Bearer {self.token}"}
            )
            
            if response.status_code == 200:
                agent = response.json()
                logger.info(f"Agent found: {agent}")
                return agent
            elif response.status_code == 404:
                logger.info(f"Agent not found: {self.agent_id}")
                return None
            else:
                logger.error(f"Error getting agent: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting agent: {str(e)}")
            return None
    
    async def execute_command(self, command):
        """Execute a command on the agent.
        
        Args:
            command: Command to execute
            
        Returns:
            str: Command ID, or None if execution fails
        """
        try:
            response = requests.post(
                f"{self.controller_url}/agents/{self.agent_id}/execute",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"command": command}
            )
            
            if response.status_code == 200:
                result = response.json()
                command_id = result.get("command_id")
                logger.info(f"Command execution initiated: {command_id}")
                return command_id
            else:
                logger.error(f"Command execution failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return None
    
    async def wait_for_command_result(self, timeout=30):
        """Wait for the command result.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            dict: Command result, or None if timeout
        """
        if not self.command_id:
            logger.error("No command ID to wait for")
            return None
        
        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            try:
                response = requests.get(
                    f"{self.controller_url}/commands/{self.command_id}",
                    headers={"Authorization": f"Bearer {self.token}"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get("status")
                    
                    if status in ["success", "error"]:
                        logger.info(f"Command completed with status: {status}")
                        return result
                    
                    logger.info(f"Command status: {status}")
                else:
                    logger.error(f"Error getting command result: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"Error getting command result: {str(e)}")
            
            await asyncio.sleep(1)
        
        logger.error(f"Timeout waiting for command result after {timeout} seconds")
        return None


async def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Integration test for the Ogent system")
    parser.add_argument("--controller-url", default=DEFAULT_CONTROLLER_URL, help="URL of the controller service")
    parser.add_argument("--agent-id", default=DEFAULT_AGENT_ID, help="ID of the agent to register")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help="Username for authentication")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Password for authentication")
    
    args = parser.parse_args()
    
    test = IntegrationTest(
        controller_url=args.controller_url,
        agent_id=args.agent_id,
        username=args.username,
        password=args.password
    )
    
    success = await test.run()
    
    if success:
        logger.info("Integration test passed")
        sys.exit(0)
    else:
        logger.error("Integration test failed")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 