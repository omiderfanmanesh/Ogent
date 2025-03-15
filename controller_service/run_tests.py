#!/usr/bin/env python
"""
Test runner for the controller service
"""

import unittest
import sys
import os

def run_tests():
    """Run all tests in the tests directory"""
    # Add the parent directory to the path so we can import the app
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return the number of failures and errors
    return len(result.failures) + len(result.errors)

if __name__ == "__main__":
    # Exit with the number of test failures
    sys.exit(run_tests()) 