import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from openai import OpenAI

# Configure logging
logger = logging.getLogger("ai_service")

class AIServiceBase(ABC):
    """Base class for AI services"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the AI service base class
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        logger.info(f"API Key present: {self.api_key is not None}")
        
        self.enabled = self.api_key is not None
        self.client = None
        
        if not self.enabled:
            logger.warning("OpenAI API key not provided, AI features are disabled")
            return
        
        try:
            # Initialize OpenAI client
            self.client = OpenAI(api_key=self.api_key)
            logger.info(f"{self.__class__.__name__} initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing {self.__class__.__name__}: {str(e)}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if the AI service is enabled
        
        Returns:
            bool: True if enabled, False otherwise
        """
        return self.enabled
    
    @abstractmethod
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Process a request with the AI service
        
        Returns:
            Dict[str, Any]: The processed result
        """
        pass 