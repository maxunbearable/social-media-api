#!/usr/bin/env python3
"""
Simple test runner for the social media API
"""
import subprocess
import sys

def run_tests():
    """Run the test suite"""
    print("Running tests for social media API...")
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                          capture_output=False)
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code) 