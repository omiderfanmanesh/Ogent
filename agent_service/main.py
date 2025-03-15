"""Main entry point for the Agent Service."""

import asyncio
import logging
import uvicorn
import signal
import sys
import argparse
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

# Import from clean architecture layers
from agent.infrastructure.config.config import config
from agent.infrastructure.container import container
from agent.presentation.api.routes import router

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("agent.log")
    ]
)

logger = logging.getLogger("agent.main")

# Create FastAPI application
app = FastAPI(
    title="Agent Service",
    description="Service for executing commands on local or remote systems",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include agent router
app.include_router(router)

# Token endpoint
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login to get an access token.
    
    Args:
        form_data: OAuth2 password request form
        
    Returns:
        Dict[str, str]: Access token
        
    Raises:
        HTTPException: If authentication fails
    """
    if form_data.username != config.api_username or form_data.password != config.api_password:
        logger.warning(f"Authentication failed for user: {form_data.username}")
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": config.api_token, "token_type": "bearer"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint.
    
    Returns:
        Dict[str, str]: Welcome message
    """
    return {"message": "Welcome to the Agent Service"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        Dict[str, str]: Health status
    """
    return {"status": "healthy"}

# Signal handlers for graceful shutdown
def signal_handler(sig, frame):
    """Handle signals for graceful shutdown.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    logger.info(f"Received signal {sig}, shutting down...")
    container.cleanup()
    config.cleanup()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def run_agent():
    """Run the agent client."""
    try:
        logger.info("Starting agent client")
        client_service = container.get_client_service()
        await client_service.start()
        return 0
    except Exception as e:
        logger.error(f"Error running agent client: {str(e)}")
        return 1

def run_api():
    """Run the API server."""
    logger.info(f"Starting API server on {config.api_host}:{config.api_port}")
    uvicorn.run(
        "main:app",
        host=config.api_host,
        port=config.api_port,
        reload=config.debug
    )

if __name__ == "__main__":
    # Determine the mode based on command line arguments
    parser = argparse.ArgumentParser(description="Agent Service")
    parser.add_argument("--mode", choices=["api", "agent", "both"], default="both",
                        help="Run mode: api, agent, or both (default)")
    args = parser.parse_args()
    
    logger.info(f"Starting agent service in {args.mode} mode")
    
    if args.mode == "api":
        # Run only the API server
        run_api()
    elif args.mode == "agent":
        # Run only the agent client
        exit_code = asyncio.run(run_agent())
        sys.exit(exit_code)
    else:
        # Run both the API server and agent client
        # Start the agent client in a separate thread
        import threading
        agent_thread = threading.Thread(
            target=lambda: asyncio.run(run_agent()),
            daemon=True
        )
        agent_thread.start()
        
        # Run the API server in the main thread
        run_api() 