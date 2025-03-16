"""Simple tests for the refactored code."""

import pytest
from unittest.mock import MagicMock
from agent.domain.models import CommandRequest, CommandResponse, ExecutorInfo
from agent.application.agent_service import AgentService
from agent.application.command_service import CommandService
from agent.infrastructure.executor_factory import ExecutorFactory
from agent.infrastructure.command_repository import CommandRepository

def test_models():
    """Test that our models can be instantiated."""
    # Test CommandRequest
    cmd_request = CommandRequest(command="ls", executor_type="local")
    assert cmd_request.command == "ls"
    assert cmd_request.executor_type == "local"
    
    # Test CommandResponse
    cmd_response = CommandResponse(
        command="ls",
        command_id="test-id",
        exit_code=0,
        stdout="file1\nfile2",
        stderr="",
        timestamp="2023-01-01T00:00:00Z",
        execution_type="local",
        target="local",
        status="success"
    )
    assert cmd_response.command == "ls"
    assert cmd_response.exit_code == 0
    
    # Test ExecutorInfo
    executor_info = ExecutorInfo(
        type="local",
        available=True,
        target={"name": "local"}
    )
    assert executor_info.type == "local"
    assert executor_info.available is True

def test_agent_service():
    """Test that AgentService can be instantiated."""
    # Mock dependencies
    executor_factory = MagicMock(spec=ExecutorFactory)
    executor_factory.get_available_executors.return_value = {
        "local": ExecutorInfo(
            type="local",
            available=True,
            target={"name": "local"}
        )
    }
    
    # Create service
    service = AgentService(executor_factory=executor_factory)
    
    # Test get_available_executors
    executors = service.get_available_executors()
    assert "local" in executors
    assert executors["local"].type == "local"
    
    # Test get_agent_info
    info = service.get_agent_info()
    assert "version" in info
    assert "executors" in info

def test_command_service():
    """Test that CommandService can be instantiated."""
    # Mock dependencies
    command_repository = MagicMock(spec=CommandRepository)
    executor_factory = MagicMock(spec=ExecutorFactory)
    
    # Create service
    service = CommandService(
        command_repository=command_repository,
        executor_factory=executor_factory
    )
    
    # Test get_command_history
    command_repository.get_history.return_value = []
    history = service.get_command_history()
    assert isinstance(history, list)
    command_repository.get_history.assert_called_once_with(10) 