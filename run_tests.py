#!/usr/bin/env python3
"""
Batata VPN - Test Runner

Runs all unit tests and reports results.
Note: Some tests require Windows 10/11 for full verification.
"""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """
    Run all unit tests.
    """
    print("\n" + "="*80)
    print("Batata VPN - Unit Test Suite")
    print("="*80 + "\n")

    # Run pytest
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=Path(__file__).parent
    )

    return result.returncode


if __name__ == "__main__":
    exit_code = run_tests()
    
    print("\n" + "="*80)
    if exit_code == 0:
        print("\u2713 All unit tests passed")
        print("\nNote: These are unit/integration tests that run on Linux/Cloud.")
        print("Real Windows VPN functionality must be tested on Windows 10/11.")
    else:
        print("\u2717 Some tests failed")
    print("="*80 + "\n")
    
    sys.exit(exit_code)
