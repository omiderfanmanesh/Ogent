import asyncio
import logging
import aiohttp
import socketio
import redis
import paramiko
import sys
import os
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("service_tester")

class ServiceTester:
    """Test runner for Ogent services."""
    
    def __init__(self):
        """Initialize the service tester."""
        self.controller_url = "http://localhost:8001"
        self.redis_url = "redis://localhost:6379/0"
        self.ssh_host = "localhost"
        self.ssh_port = 2222
        self.ssh_username = "ubuntu"
        self.ssh_password = "password"
    
    async def test_controller(self) -> bool:
        """Test the controller service."""
        try:
            logger.info("Testing controller service...")
            
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                async with session.get(f"{self.controller_url}/health") as response:
                    if response.status != 200:
                        logger.error(f"Controller health check failed: {response.status}")
                        return False
                    
                    data = await response.json()
                    logger.info(f"Controller health check response: {data}")
            
            # Test Socket.IO connection
            sio = socketio.AsyncClient()
            
            @sio.event
            async def connect():
                logger.info("Connected to controller Socket.IO server")
            
            @sio.event
            async def disconnect():
                logger.info("Disconnected from controller Socket.IO server")
            
            # Get authentication token
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.controller_url}/token",
                    data={"username": "admin", "password": "password"}
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get auth token: {response.status}")
                        return False
                    token_data = await response.json()
                    token = token_data["access_token"]
            
            # Connect with authentication
            await sio.connect(
                self.controller_url,
                auth={"token": token, "is_agent": False}
            )
            await asyncio.sleep(1)
            await sio.disconnect()
            
            logger.info("Controller service test passed")
            return True
        except Exception as e:
            logger.error(f"Error testing controller service: {str(e)}")
            return False
    
    async def test_redis(self) -> bool:
        """Test the Redis service."""
        try:
            logger.info("Testing Redis service...")
            
            # Create Redis client
            r = redis.Redis.from_url(self.redis_url, decode_responses=True)
            
            # Test connection
            if not r.ping():
                logger.error("Redis ping failed")
                return False
            
            # Test basic operations
            r.set("test_key", "test_value")
            value = r.get("test_key")
            
            if value != "test_value":
                logger.error(f"Redis get returned wrong value: {value}")
                return False
            
            # Clean up
            r.delete("test_key")
            r.close()
            
            logger.info("Redis service test passed")
            return True
        except Exception as e:
            logger.error(f"Error testing Redis service: {str(e)}")
            return False
    
    async def test_ssh_target(self) -> bool:
        """Test the Ubuntu SSH target."""
        try:
            logger.info("Testing SSH target...")
            
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to SSH server
            ssh.connect(
                hostname=self.ssh_host,
                port=self.ssh_port,
                username=self.ssh_username,
                password=self.ssh_password
            )
            
            # Execute test command
            stdin, stdout, stderr = ssh.exec_command("echo 'Hello from SSH'")
            output = stdout.read().decode().strip()
            
            if output != "Hello from SSH":
                logger.error(f"SSH command returned wrong output: {output}")
                return False
            
            # Clean up
            ssh.close()
            
            logger.info("SSH target test passed")
            return True
        except Exception as e:
            logger.error(f"Error testing SSH target: {str(e)}")
            return False
    
    async def test_agent(self) -> bool:
        """Test the agent service."""
        try:
            logger.info("Testing agent service...")
            
            # Wait for agent to register with controller
            await asyncio.sleep(5)
            
            # Get authentication token
            async with aiohttp.ClientSession() as session:
                # Get token
                async with session.post(
                    f"{self.controller_url}/token",
                    data={"username": "admin", "password": "password"}
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get auth token: {response.status}")
                        return False
                    token_data = await response.json()
                    token = token_data["access_token"]
                
                # Check agent registration through controller API
                headers = {"Authorization": f"Bearer {token}"}
                async with session.get(f"{self.controller_url}/agents", headers=headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to get agents: {response.status}")
                        return False
                    
                    agents = await response.json()
                    logger.info(f"Connected agents: {agents}")
                    
                    if not agents:
                        logger.error("No agents connected")
                        return False
            
            logger.info("Agent service test passed")
            return True
        except Exception as e:
            logger.error(f"Error testing agent service: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all service tests."""
        try:
            # Test services in order
            redis_ok = await self.test_redis()
            if not redis_ok:
                logger.error("Redis test failed, stopping tests")
                return False
            
            controller_ok = await self.test_controller()
            if not controller_ok:
                logger.error("Controller test failed, stopping tests")
                return False
            
            ssh_ok = await self.test_ssh_target()
            if not ssh_ok:
                logger.error("SSH target test failed, stopping tests")
                return False
            
            agent_ok = await self.test_agent()
            if not agent_ok:
                logger.error("Agent test failed")
                return False
            
            logger.info("All service tests passed!")
            return True
        except Exception as e:
            logger.error(f"Error running tests: {str(e)}")
            return False

async def main():
    """Main entry point."""
    tester = ServiceTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main()) 