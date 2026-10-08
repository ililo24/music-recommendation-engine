#!/usr/bin/env python3
"""
Test runner for the music recommendation engine.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit             # Run only unit tests
    python run_tests.py --integration      # Run only integration tests
    python run_tests.py --coverage         # Run with coverage report (80% gate)
    python run_tests.py --verbose          # Verbose output
"""

import argparse
import sys

import pytest

# Must match the coverage gate enforced in CI (.github/workflows/ci.yml).
COVERAGE_FAIL_UNDER = 80


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Run tests for music recommendation engine")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Run with coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Base pytest arguments
    pytest_args = []

    if args.verbose:
        pytest_args.append("-v")

    if args.coverage:
        # Measure the maintained package only — not the legacy top-level
        # src/*.py modules — and enforce the same gate as CI.
        pytest_args.append("--cov=musicrec")
        pytest_args.append("--cov-report=html")
        pytest_args.append("--cov-report=term")
        pytest_args.append(f"--cov-fail-under={COVERAGE_FAIL_UNDER}")

    # Determine which tests to run
    if args.unit:
        pytest_args.append("tests/test_feature_engineering.py")
        pytest_args.append("tests/test_model_training.py")
        pytest_args.append("tests/unit")
    elif args.integration:
        pytest_args.append("tests/test_integration.py")
        pytest_args.append("tests/integration")
    else:
        # Run all tests
        pytest_args.append("tests/")

    # Run tests
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
