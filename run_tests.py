#!/usr/bin/env python3
"""
Test runner for the music recommendation engine.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --coverage         # Run with coverage report
"""

import pytest
import sys
import os
import argparse


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run tests for music recommendation engine')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Base pytest arguments
    pytest_args = []
    
    if args.verbose:
        pytest_args.append('-v')
    
    if args.coverage:
        pytest_args.extend(['--cov=src', '--cov-report=html', '--cov-report=term'])
    
    # Determine which tests to run
    if args.unit:
        pytest_args.append('tests/test_feature_engineering.py')
        pytest_args.append('tests/test_model_training.py')
    elif args.integration:
        pytest_args.append('tests/test_integration.py')
    else:
        # Run all tests
        pytest_args.append('tests/')
    
    # Run tests
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()

