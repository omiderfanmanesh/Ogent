import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.ai.manager import AIManager
from app.ai.validation_service import ValidationService
from app.ai.optimization_service import OptimizationService
from app.ai.enrichment_service import EnrichmentService

class TestAIManager(unittest.TestCase):
    """Tests for the AIManager class"""
    
    def setUp(self):
        """Set up test environment"""
        # Create the manager with a test API key
        self.manager = AIManager(api_key="test_key")
        
        # Create mock validation result
        self.mock_validation_result = {
            "safe": True,
            "risk_level": "low",
            "risks": [],
            "suggestions": ["Use -h for human-readable sizes"]
        }
        
        # Create mock optimization result
        self.mock_optimization_result = {
            "optimized_command": "ls -lah",
            "improvements": ["Added -h for human-readable sizes"],
            "explanation": "The -h flag makes file sizes human-readable"
        }
        
        # Create mock enrichment result
        self.mock_enrichment_result = {
            "purpose": "List files in long format",
            "components": {"ls": "List directory", "-la": "Long format, all files"},
            "side_effects": ["None, read-only command"],
            "prerequisites": ["None"],
            "related_commands": ["ls -lh", "find", "du"]
        }
    
    def test_init(self):
        """Test initialization"""
        self.assertTrue(self.manager.is_enabled)
        self.assertIsInstance(self.manager.validation_service, ValidationService)
        self.assertIsInstance(self.manager.optimization_service, OptimizationService)
        self.assertIsInstance(self.manager.enrichment_service, EnrichmentService)
    
    @patch.object(AIManager, "is_enabled", False)
    async def test_process_command_disabled(self):
        """Test process_command method when manager is disabled"""
        result = await self.manager.process_command("ls -la")
        
        self.assertEqual(result["original_command"], "ls -la")
        self.assertEqual(result["processed_command"], "ls -la")
        self.assertEqual(result["validation"]["safe"], True)
        self.assertEqual(result["validation"]["risk_level"], "unknown")
        self.assertEqual(result["validation"]["risks"], ["AI validation is disabled"])
        self.assertEqual(result["optimization"]["optimized_command"], "ls -la")
        self.assertEqual(result["optimization"]["improvements"], ["AI optimization is disabled"])
        self.assertEqual(result["enrichment"]["purpose"], "Unknown (AI enrichment is disabled)")
    
    @patch.object(AIManager, "validate_command")
    @patch.object(AIManager, "optimize_command")
    @patch.object(AIManager, "enrich_command")
    async def test_process_command_enabled(self, mock_enrich, mock_optimize, mock_validate):
        """Test process_command method when manager is enabled"""
        # Set up mocks
        mock_validate.return_value = self.mock_validation_result
        mock_optimize.return_value = self.mock_optimization_result
        mock_enrich.return_value = self.mock_enrichment_result
        
        # Call the method
        result = await self.manager.process_command("ls -la")
        
        # Verify the result
        self.assertEqual(result["original_command"], "ls -la")
        self.assertEqual(result["processed_command"], "ls -lah")
        self.assertEqual(result["validation"], self.mock_validation_result)
        self.assertEqual(result["optimization"], self.mock_optimization_result)
        self.assertEqual(result["enrichment"], self.mock_enrichment_result)
        
        # Verify the service methods were called
        mock_validate.assert_called_once_with("ls -la", "Linux", "Server administration")
        mock_optimize.assert_called_once_with("ls -la", "Linux", "Server administration")
        mock_enrich.assert_called_once_with("ls -la", "Linux")
    
    @patch.object(AIManager, "validate_command")
    @patch.object(AIManager, "optimize_command")
    @patch.object(AIManager, "enrich_command")
    async def test_process_command_unsafe(self, mock_enrich, mock_optimize, mock_validate):
        """Test process_command method with unsafe command"""
        # Set up mocks
        unsafe_validation = {
            "safe": False,
            "risk_level": "high",
            "risks": ["Command could delete files"],
            "suggestions": ["Use with caution"]
        }
        mock_validate.return_value = unsafe_validation
        mock_enrich.return_value = self.mock_enrichment_result
        
        # Call the method
        result = await self.manager.process_command("rm -rf /")
        
        # Verify the result
        self.assertEqual(result["original_command"], "rm -rf /")
        self.assertEqual(result["processed_command"], "rm -rf /")
        self.assertEqual(result["validation"], unsafe_validation)
        self.assertEqual(result["optimization"]["optimized_command"], "rm -rf /")
        self.assertEqual(result["optimization"]["improvements"], ["Command not optimized due to security risks"])
        self.assertEqual(result["enrichment"], self.mock_enrichment_result)
        
        # Verify the service methods were called
        mock_validate.assert_called_once_with("rm -rf /", "Linux", "Server administration")
        mock_optimize.assert_not_called()
        mock_enrich.assert_called_once_with("rm -rf /", "Linux")
    
    @patch.object(AIManager, "validate_command")
    async def test_process_command_exception(self, mock_validate):
        """Test process_command method with exception"""
        # Set up mock to raise exception
        mock_validate.side_effect = Exception("Test error")
        
        # Call the method
        result = await self.manager.process_command("ls -la")
        
        # Verify the result
        self.assertEqual(result["original_command"], "ls -la")
        self.assertEqual(result["processed_command"], "ls -la")
        self.assertEqual(result["validation"]["safe"], False)
        self.assertEqual(result["validation"]["risk_level"], "unknown")
        self.assertEqual(result["validation"]["risks"], ["Error processing command: Test error"])
        
        # Verify the service method was called
        mock_validate.assert_called_once_with("ls -la", "Linux", "Server administration")

def run_async_test(coro):
    """Helper function to run async tests"""
    return asyncio.run(coro)

if __name__ == "__main__":
    unittest.main() 