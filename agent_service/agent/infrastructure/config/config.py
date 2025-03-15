"""Configuration module for the agent service."""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent.log")
    ]
)
logger = logging.getLogger("agent")


class Config:
    """Configuration class for the agent service."""
    
    def __init__(self):
        """Initialize the configuration."""
        # Controller settings
        self.controller_url = os.getenv("CONTROLLER_URL", "http://localhost:8000")
        self.agent_username = os.getenv("AGENT_USERNAME", "admin")
        self.agent_password = os.getenv("AGENT_PASSWORD", "password")
        self.reconnect_delay = int(os.getenv("RECONNECT_DELAY", "5"))
        self.max_reconnect_attempts = int(os.getenv("MAX_RECONNECT_ATTEMPTS", "10"))
        
        # Redis settings
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_client = None
        
        # Initialize Redis client if URL is provided
        if self.redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(self.redis_url)
                logger.info(f"Connected to Redis at {self.redis_url}")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self.redis_client = None
        
        # API settings
        self.api_token = os.getenv("API_TOKEN", "agent-token")
        self.api_username = os.getenv("API_USERNAME", "admin")
        self.api_password = os.getenv("API_PASSWORD", "password")
        self.api_host = os.getenv("API_HOST", "0.0.0.0")
        self.api_port = int(os.getenv("API_PORT", "8080"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # SSH settings
        self.ssh_enabled = os.getenv("SSH_ENABLED", "false").lower() == "true"
        self.ssh_host = os.getenv("SSH_HOST", "")
        self.ssh_port = os.getenv("SSH_PORT", "22")
        self.ssh_username = os.getenv("SSH_USERNAME", "")
        self.ssh_password = os.getenv("SSH_PASSWORD", "")
        self.ssh_key_path = os.getenv("SSH_KEY_PATH", "~/.ssh/id_rsa")
        self.ssh_timeout = os.getenv("SSH_TIMEOUT", "10")
        
        # System info
        import platform
        self.hostname = platform.node()
        self.platform = platform.system()
        self.version = platform.version()
        self.python_version = platform.python_version()
    
    @property
    def ssh_config(self) -> Dict[str, Any]:
        """Get the SSH configuration.
        
        Returns:
            Dict[str, Any]: SSH configuration dictionary
        """
        return {
            "enabled": self.ssh_enabled,
            "host": self.ssh_host,
            "port": self.ssh_port,
            "username": self.ssh_username,
            "password": self.ssh_password,
            "key_path": self.ssh_key_path,
            "timeout": self.ssh_timeout
        }
    
    def __str__(self) -> str:
        """String representation of the configuration.
        
        Returns:
            str: String representation
        """
        # Create a copy of the configuration without sensitive information
        config_dict = self.__dict__.copy()
        # Mask sensitive information
        if config_dict.get("agent_password"):
            config_dict["agent_password"] = "********"
        if config_dict.get("api_password"):
            config_dict["api_password"] = "********"
        if config_dict.get("ssh_password"):
            config_dict["ssh_password"] = "********"
        if config_dict.get("api_token"):
            config_dict["api_token"] = "********"
        # Remove redis client from string representation
        if "redis_client" in config_dict:
            config_dict["redis_client"] = "<redis client>" if self.redis_client else None
        
        return f"Config({config_dict})"
    
    def cleanup(self):
        """Clean up resources."""
        if self.redis_client:
            logger.info("Closing Redis connection")
            self.redis_client.close()
            self.redis_client = None


# Create a singleton instance
config = Config() 