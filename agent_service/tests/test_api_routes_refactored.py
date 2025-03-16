"""Tests for the refactored API routes."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from datetime import datetime, timezone

from agent.api.routes import router
from agent.domain.models import CommandResponse, ExecutorInfo
from agent.application.command_service import CommandService
from agent.application.agent_service import AgentService

# Create test app
app = FastAPI()
app.include_router(router)

# Create test client
client = TestClient(app)

# Mock authentication
@pytest.fixture
def mock_auth():
    with patch("agent.api.auth.authenticate", return_value=True):
        yield

# Mock command service
@pytest.fixture
def mock_command_service():
    service = MagicMock(spec=CommandService)
    
    # Mock execute_command
    async_execute = AsyncMock()
    async_execute.return_value = CommandResponse(
        command="test command",
        command_id="test-id",
        exit_code=0,
        stdout="test output",
        stderr="",
        timestamp=datetime.now(timezone.utc).isoformat(),
        execution_type="local",
        target="local",
        status="success"
    )
    service.execute_command = async_execute
    
    # Mock get_command_history
    service.get_command_history.return_value = [
        CommandResponse(
            command="test command",
            command_id="test-id",
            exit_code=0,
            stdout="test output",
            stderr="",
            timestamp=datetime.now(timezone.utc).isoformat(),
            execution_type="local",
            target="local",
            status="success"
        )
    ]
    
    with patch("agent.application.command_service.CommandService", return_value=service):
        yield service

# Mock agent service
@pytest.fixture
def mock_agent_service():
    service = MagicMock(spec=AgentService)
    
    # Mock get_agent_info
    service.get_agent_info.return_value = {
        "version": "1.0.0",
        "hostname": "test-host",
        "executors": {
            "local": ExecutorInfo(
                type="local",
                available=True,
                target={"name": "local"}
            )
        }
    }
    
    # Mock get_available_executors
    service.get_available_executors.return_value = {
        "local": ExecutorInfo(
            type="local",
            available=True,
            target={"name": "local"}
        )
    }
    
    with patch("agent.application.agent_service.AgentService", return_value=service):
        yield service

# Tests
def test_get_info(mock_auth, mock_agent_service):
    """Test get_info endpoint."""
    # Override dependency
    app.dependency_overrides = {
        AgentService: lambda: mock_agent_service
    }
    
    # Make request
    response = client.get("/agent/info", headers={"Authorization": "Bearer test-token"})
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["hostname"] == "test-host"
    assert "executors" in data
    assert "local" in data["executors"]
    
    # Verify service call
    mock_agent_service.get_agent_info.assert_called_once()

def test_get_executors(mock_auth, mock_agent_service):
    """Test get_executors endpoint."""
    # Override dependency
    app.dependency_overrides = {
        AgentService: lambda: mock_agent_service
    }
    
    # Make request
    response = client.get("/agent/executors", headers={"Authorization": "Bearer test-token"})
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert "local" in data
    assert data["local"]["type"] == "local"
    assert data["local"]["available"] is True
    
    # Verify service call
    mock_agent_service.get_available_executors.assert_called_once()

def test_get_history(mock_auth, mock_command_service):
    """Test get_history endpoint."""
    # Override dependency
    app.dependency_overrides = {
        CommandService: lambda: mock_command_service
    }
    
    # Make request
    response = client.get("/agent/history", headers={"Authorization": "Bearer test-token"})
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["command"] == "test command"
    assert data[0]["command_id"] == "test-id"
    
    # Verify service call
    mock_command_service.get_command_history.assert_called_once_with(10)

def test_execute_command(mock_auth, mock_command_service):
    """Test execute_command endpoint."""
    # Override dependency
    app.dependency_overrides = {
        CommandService: lambda: mock_command_service
    }
    
    # Make request
    response = client.post(
        "/agent/execute",
        headers={"Authorization": "Bearer test-token"},
        json={"command": "test command", "executor_type": "local"}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["command"] == "test command"
    assert data["command_id"] == "test-id"
    assert data["exit_code"] == 0
    
    # Verify service call
    mock_command_service.execute_command.assert_called_once_with(
        command="test command",
        executor_type="local"
    ) 