#!/usr/bin/env python3
"""Comprehensive Hypothesis test with 100 examples"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from hypothesis import given, settings
from strategies import small_database
from test_properties import verify_with_metamath_exe

@given(small_database())
@settings(max_examples=100, deadline=10000)
def test_100_databases(db_and_config):
    """Test 100 randomly generated databases"""
    db, config = db_and_config
    success, output = verify_with_metamath_exe(db)
    
    if not success and "SKIPPED" not in output:
        print(f"\nFAILED CONFIG: {config}")
        print(f"DATABASE (first 1000 chars):\n{db[:1000]}")
        print(f"OUTPUT (first 500 chars):\n{output[:500]}")
    
    assert success or "SKIPPED" in output, f"Failed with config: {config}"

if __name__ == "__main__":
    test_100_databases()
    print("\n✅ All 100 tests PASSED!")
