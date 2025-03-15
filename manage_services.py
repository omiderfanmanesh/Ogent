#!/usr/bin/env python3
import subprocess
import sys
import time
import argparse
import logging
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("service_manager")

class ServiceManager:
    """Manager for Ogent services."""
    
    def __init__(self):
        """Initialize the service manager."""
        self.services = ["redis", "controller", "agent", "ubuntu-target"]
    
    def run_command(self, command: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run a shell command.
        
        Args:
            command: The command to run as a list of strings
            check: Whether to check the return code
            
        Returns:
            subprocess.CompletedProcess: The completed process
        """
        try:
            logger.info(f"Running command: {' '.join(command)}")
            result = subprocess.run(
                command,
                check=check,
                capture_output=True,
                text=True
            )
            return result
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with exit code {e.returncode}")
            logger.error(f"stdout: {e.stdout}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    def build_services(self, services: Optional[List[str]] = None):
        """
        Build specified services or all services.
        
        Args:
            services: Optional list of services to build
        """
        services = services or self.services
        logger.info(f"Building services: {services}")
        
        try:
            self.run_command(["docker-compose", "build"] + services)
            logger.info("Services built successfully")
        except Exception as e:
            logger.error(f"Error building services: {str(e)}")
            sys.exit(1)
    
    def start_services(self, services: Optional[List[str]] = None):
        """
        Start specified services or all services.
        
        Args:
            services: Optional list of services to start
        """
        services = services or self.services
        logger.info(f"Starting services: {services}")
        
        try:
            self.run_command(["docker-compose", "up", "-d"] + services)
            logger.info("Services started successfully")
        except Exception as e:
            logger.error(f"Error starting services: {str(e)}")
            sys.exit(1)
    
    def stop_services(self, services: Optional[List[str]] = None):
        """
        Stop specified services or all services.
        
        Args:
            services: Optional list of services to stop
        """
        services = services or self.services
        logger.info(f"Stopping services: {services}")
        
        try:
            self.run_command(["docker-compose", "stop"] + services)
            logger.info("Services stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping services: {str(e)}")
            sys.exit(1)
    
    def restart_services(self, services: Optional[List[str]] = None):
        """
        Restart specified services or all services.
        
        Args:
            services: Optional list of services to restart
        """
        services = services or self.services
        logger.info(f"Restarting services: {services}")
        
        try:
            self.run_command(["docker-compose", "restart"] + services)
            logger.info("Services restarted successfully")
        except Exception as e:
            logger.error(f"Error restarting services: {str(e)}")
            sys.exit(1)
    
    def view_logs(self, services: Optional[List[str]] = None, tail: str = "100"):
        """
        View logs for specified services or all services.
        
        Args:
            services: Optional list of services to view logs for
            tail: Number of lines to show from the end of logs
        """
        services = services or self.services
        logger.info(f"Viewing logs for services: {services}")
        
        try:
            self.run_command(["docker-compose", "logs", "--tail", tail, "-f"] + services)
        except KeyboardInterrupt:
            logger.info("Stopped viewing logs")
        except Exception as e:
            logger.error(f"Error viewing logs: {str(e)}")
            sys.exit(1)
    
    def check_service_health(self, service: str) -> bool:
        """
        Check if a service is healthy.
        
        Args:
            service: The service to check
            
        Returns:
            bool: True if the service is healthy, False otherwise
        """
        try:
            result = self.run_command(
                ["docker-compose", "ps", "-q", service],
                check=False
            )
            
            if not result.stdout.strip():
                logger.error(f"Service {service} is not running")
                return False
            
            container_id = result.stdout.strip()
            
            result = self.run_command(
                ["docker", "inspect", "-f", "{{.State.Health.Status}}", container_id],
                check=False
            )
            
            status = result.stdout.strip()
            
            if status == "healthy":
                logger.info(f"Service {service} is healthy")
                return True
            else:
                logger.error(f"Service {service} is not healthy (status: {status})")
                return False
        except Exception as e:
            logger.error(f"Error checking health for service {service}: {str(e)}")
            return False
    
    def deploy_and_test(self):
        """Deploy all services and run tests."""
        try:
            # Build and start services
            self.build_services()
            self.start_services()
            
            # Wait for services to be ready
            logger.info("Waiting for services to be ready...")
            time.sleep(10)
            
            # Check service health
            healthy = True
            for service in self.services:
                if not self.check_service_health(service):
                    healthy = False
            
            if not healthy:
                logger.error("Some services are not healthy")
                sys.exit(1)
            
            # Run tests
            logger.info("Running service tests...")
            result = self.run_command(["python", "test_services.py"], check=False)
            
            if result.returncode != 0:
                logger.error("Service tests failed")
                sys.exit(1)
            
            logger.info("All services deployed and tested successfully!")
        except Exception as e:
            logger.error(f"Error during deployment and testing: {str(e)}")
            sys.exit(1)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage Ogent services")
    parser.add_argument("action", choices=["build", "start", "stop", "restart", "logs", "deploy"], help="Action to perform")
    parser.add_argument("--services", nargs="+", help="Services to act on")
    parser.add_argument("--tail", default="100", help="Number of log lines to show")
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    if args.action == "build":
        manager.build_services(args.services)
    elif args.action == "start":
        manager.start_services(args.services)
    elif args.action == "stop":
        manager.stop_services(args.services)
    elif args.action == "restart":
        manager.restart_services(args.services)
    elif args.action == "logs":
        manager.view_logs(args.services, args.tail)
    elif args.action == "deploy":
        manager.deploy_and_test()

if __name__ == "__main__":
    main() 