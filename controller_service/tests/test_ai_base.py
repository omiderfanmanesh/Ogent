import unittest
import os
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from app.ai.base import AIServiceBase

class TestAIService(AIServiceBase):
    """Test implementation of AIServiceBase for testing"""
    
    async def process(self, *args, **kwargs) -> Dict[str, Any]:
        """Test implementation of process method"""
        if not self.is_enabled():
            return {"enabled": False}
        return {"enabled": True}

class TestAIServiceBase(unittest.TestCase):
    """Tests for the AIServiceBase class"""
    
    def setUp(self):
        """Set up test environment"""
        # Save original environment
        self.original_api_key = os.environ.get("OPENAI_API_KEY")
        
        # Clear environment for tests
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
    
    def tearDown(self):
        """Tear down test environment"""
        # Restore original environment
        if self.original_api_key:
            os.environ["OPENAI_API_KEY"] = self.original_api_key
        elif "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
    
    def test_init_with_api_key(self):
        """Test initialization with API key"""
        service = TestAIService(api_key="test_key")
        self.assertTrue(service.is_enabled())
        self.assertEqual(service.api_key, "test_key")
    
    def test_init_without_api_key(self):
        """Test initialization without API key"""
        service = TestAIService()
        self.assertFalse(service.is_enabled())
        self.assertIsNone(service.api_key)
    
    def test_init_with_env_api_key(self):
        """Test initialization with API key from environment"""
        os.environ["OPENAI_API_KEY"] = "env_test_key"
        service = TestAIService()
        self.assertTrue(service.is_enabled())
        self.assertEqual(service.api_key, "env_test_key")
    
    @patch("app.ai.base.OpenAI")
    def test_init_with_openai_error(self, mock_openai):
        """Test initialization with OpenAI error"""
        mock_openai.side_effect = Exception("Test error")
        service = TestAIService(api_key="test_key")
        self.assertFalse(service.is_enabled())

if __name__ == "__main__":
    unittest.main() 