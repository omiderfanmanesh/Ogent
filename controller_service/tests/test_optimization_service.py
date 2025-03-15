import unittest
import asyncio
import json
from unittest.mock import patch, MagicMock

from app.ai.optimization_service import OptimizationService

class TestOptimizationService(unittest.TestCase):
    """Tests for the OptimizationService class"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = OptimizationService(api_key="test_key")
        
        # Create a mock response for OpenAI
        self.mock_response = MagicMock()
        self.mock_response.choices = [MagicMock()]
        self.mock_response.choices[0].message = MagicMock()
        self.mock_response.choices[0].message.content = json.dumps({
            "optimized_command": "ls -lah",
            "improvements": ["Added -h for human-readable sizes"],
            "explanation": "The -h flag makes file sizes human-readable"
        })
    
    def test_init(self):
        """Test initialization"""
        self.assertTrue(self.service.is_enabled())
        self.assertEqual(self.service.api_key, "test_key")
    
    @patch.object(OptimizationService, "is_enabled")
    async def test_process_disabled(self, mock_is_enabled):
        """Test process method when service is disabled"""
        mock_is_enabled.return_value = False
        result = await self.service.process("ls -la")
        self.assertEqual(result["optimized_command"], "ls -la")
        self.assertEqual(result["improvements"], ["AI optimization is disabled"])
        self.assertEqual(result["explanation"], "AI optimization is disabled")
    
    @patch.object(OptimizationService, "is_enabled")
    @patch.object(OptimizationService, "client")
    async def test_process_enabled(self, mock_client, mock_is_enabled):
        """Test process method when service is enabled"""
        mock_is_enabled.return_value = True
        mock_client.chat.completions.create.return_value = self.mock_response
        
        result = await self.service.process("ls -la")
        
        self.assertEqual(result["optimized_command"], "ls -lah")
        self.assertEqual(result["improvements"], ["Added -h for human-readable sizes"])
        self.assertEqual(result["explanation"], "The -h flag makes file sizes human-readable")
        
        # Verify the OpenAI client was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4o-mini")
        self.assertEqual(len(call_args["messages"]), 2)
        self.assertEqual(call_args["response_format"], {"type": "json_object"})
    
    @patch.object(OptimizationService, "is_enabled")
    @patch.object(OptimizationService, "client")
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
        
        self.assertEqual(result["optimized_command"], "ls -la")
        self.assertEqual(result["improvements"], ["Error parsing optimization result"])
        self.assertEqual(result["explanation"], "Error parsing optimization result")
    
    @patch.object(OptimizationService, "is_enabled")
    @patch.object(OptimizationService, "client")
    async def test_process_exception(self, mock_client, mock_is_enabled):
        """Test process method with exception"""
        mock_is_enabled.return_value = True
        mock_client.chat.completions.create.side_effect = Exception("Test error")
        
        result = await self.service.process("ls -la")
        
        self.assertEqual(result["optimized_command"], "ls -la")
        self.assertEqual(result["improvements"], ["Error optimizing command: Test error"])
        self.assertEqual(result["explanation"], "Error optimizing command: Test error")

def run_async_test(coro):
    """Helper function to run async tests"""
    return asyncio.run(coro)

if __name__ == "__main__":
    unittest.main() 