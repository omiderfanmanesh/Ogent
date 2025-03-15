"""Agent package for the Ogent application.

This package follows Domain-Driven Design principles with a clean architecture:

1. Domain Layer: Core business logic and entities
   - Models: Command, Executor
   - Interfaces: CommandExecutorInterface

2. Application Layer: Use cases and application services
   - Services: AgentManager, ClientService
   - DTOs: CommandRequestDTO, CommandResponseDTO

3. Infrastructure Layer: Technical details and implementations
   - Executors: BaseExecutor, LocalExecutor, SSHExecutor
   - Config: Configuration settings

4. Presentation Layer: User interface and API
   - API: FastAPI routes and models
"""

__version__ = "1.0.0"

from .config import config
from .manager import agent_manager
from .api import router
from .client import start_agent_client

__all__ = ["config", "agent_manager", "router", "start_agent_client"] 