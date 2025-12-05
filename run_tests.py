#!/usr/bin/env python3
"""
Simple test runner script
Runs all unit tests
"""

import unittest
import sys


def run_tests():
    loader = unittest.TestLoader()
    suite = loader.discover('unittests', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)


if __name__ == '__main__':
    run_tests()
