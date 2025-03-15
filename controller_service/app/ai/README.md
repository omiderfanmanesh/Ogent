# AI Module

This module provides AI-powered command processing capabilities for the controller service.

## Architecture

The AI module follows a clean, object-oriented design with the following components:

### Base Class

- `AIServiceBase`: Abstract base class for all AI services, providing common functionality for initialization and API key management.

### Services

- `ValidationService`: Validates commands for security risks.
- `OptimizationService`: Optimizes commands for better performance and readability.
- `EnrichmentService`: Enriches commands with additional context and information.

### Manager

- `AIManager`: Orchestrates the services to provide a unified command processing interface.

## Usage

```python
from app.ai import ai_manager

# Process a command
result = await ai_manager.process_command("ls -la", system="Linux", context="Server administration")

# Access individual services
validation_result = await ai_manager.validate_command("ls -la")
optimization_result = await ai_manager.optimize_command("ls -la")
enrichment_result = await ai_manager.enrich_command("ls -la")
```

## Configuration

The AI module requires an OpenAI API key to function. This can be provided in two ways:

1. Environment variable: Set the `OPENAI_API_KEY` environment variable.
2. Direct initialization: Pass the API key to the `AIManager` constructor.

## Testing

Unit tests are provided for all components of the AI module. Run the tests using:

```bash
python run_tests.py
``` 