import pytest
import sys

def run_tests():
    """Run the test suite with detailed output."""
    print("Running Crypto Arbitrage Spotter tests...")
    result = pytest.main([
        "-v",                      # verbose output
        "--tb=short",             # shorter traceback format
        "--disable-warnings",      # disable warning capture
        "tests/test_data.py",     # test file to run
    ])
    return result

if __name__ == "__main__":
    sys.exit(run_tests()) 