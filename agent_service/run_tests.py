#!/usr/bin/env python
"""Test runner script for the agent service."""

import os
import sys
import pytest

def main():
    """Run the tests."""
    # Add the current directory to the path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Run the tests
    args = [
        "-v",  # Verbose output
        "--cov=agent",  # Coverage for agent module
        "--cov-report=term",  # Coverage report in terminal
        "tests"  # Test directory
    ]
    
    # Add any additional arguments
    args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(args)

if __name__ == "__main__":
    sys.exit(main()) 