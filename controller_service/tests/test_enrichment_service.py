import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock

from app.ai.enrichment_service import EnrichmentService

class TestEnrichmentService(unittest.TestCase):
    """Tests for the EnrichmentService class"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = EnrichmentService(api_key="test_key")
        
        # Create a mock response for OpenAI
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message = MagicMock()
        self.mock_response.choices[0].message.content = json.dumps({
            "purpose": "List files in long format",
            "components": {"ls": "List directory", "-la": "Long format, all files"},
            "side_effects": ["None, read-only command"],
            "prerequisites": ["None"],
            "related_commands": ["ls -lh", "find", "du"]
        })
    
    def test_init(self):
        """Test initialization"""
        self.assertTrue(self.service.is_enabled())
        self.assertEqual(self.service.api_key, "test_key")
    
    @patch.object(EnrichmentService, "is_enabled")
    async def test_process_disabled(self, mock_is_enabled):
        """Test process method when service is disabled"""
        mock_is_enabled.return_value = False
        result = await self.service.process("ls -la")
        self.assertEqual(result["purpose"], "Unknown (AI enrichment is disabled)")
        self.assertEqual(result["components"], [])
        self.assertEqual(result["side_effects"], [])
        self.assertEqual(result["prerequisites"], [])
        self.assertEqual(result["related_commands"], [])
    
    @patch.object(EnrichmentService, "is_enabled")
    @patch.object(EnrichmentService, "client")
    async def test_process_enabled(self, mock_client, mock_is_enabled):
        """Test process method when service is enabled"""
        mock_is_enabled.return_value = True
        mock_client.chat.completions.create.return_value = self.mock_response
        
        result = await self.service.process("ls -la")
        
        self.assertEqual(result["purpose"], "List files in long format")
        self.assertEqual(result["components"], {"ls": "List directory", "-la": "Long format, all files"})
        self.assertEqual(result["side_effects"], ["None, read-only command"])
        self.assertEqual(result["prerequisites"], ["None"])
        self.assertEqual(result["related_commands"], ["ls -lh", "find", "du"])
        
        # Verify the OpenAI client was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o-mini")
        self.assertEqual(len(call_args["messages"]), 2)
        self.assertEqual(call_args["response_format"], {"type": "json_object"})
    
    @patch.object(EnrichmentService, "is_enabled")
    @patch.object(EnrichmentService, "client")
    async def test_process_json_error(self, mock_client, mock_is_enabled):
        """Test process method with JSON parsing error"""
        mock_is_enabled.return_value = True
        
        # Create an invalid JSON response
        invalid_response = MagicMock()
        invalid_response.choices = [MagicMock()]
        invalid_response.choices[0].message = MagicMock()
        invalid_response.choices[0].message.content = "Invalid JSON"
        
        mock_client.chat.completions.create.return_value = invalid_response
        
        result = await self.service.process("ls -la")
        
        self.assertEqual(result["purpose"], "Unknown")
        self.assertEqual(result["components"], [])
        self.assertEqual(result["side_effects"], [])
        self.assertEqual(result["prerequisites"], [])
        self.assertEqual(result["related_commands"], [])
    
    @patch.object(EnrichmentService, "is_enabled")
    @patch.object(EnrichmentService, "client")
    async def test_process_exception(self, mock_client, mock_is_enabled):
        """Test process method with exception"""
        mock_is_enabled.return_value = True
        mock_client.chat.completions.create.side_effect = Exception("Test error")
        
        result = await self.service.process("ls -la")
        
        self.assertEqual(result["purpose"], "Unknown")
        self.assertEqual(result["components"], [])
        self.assertEqual(result["side_effects"], [])
        self.assertEqual(result["prerequisites"], [])
        self.assertEqual(result["related_commands"], [])

def run_async_test(coro):
    """Helper function to run async tests"""
    return asyncio.run(coro)

if __name__ == "__main__":
    unittest.main() 