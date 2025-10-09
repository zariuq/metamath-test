#!/usr/bin/env python3
"""Test the constructive Metamath generator"""

import sys
import os

# Add generators to path
sys.path.insert(0, os.path.dirname(__file__))

from generators.mm_constructive import generate_valid_metamath

# Test generation
print("=" * 70)
print("Generating 100-line Metamath database with constructive proofs")
print("=" * 70)
print()

db = generate_valid_metamath(lines=100, seed=42)

print(db)
print()
print("=" * 70)
print(f"Generated {len(db.splitlines())} lines")
print("=" * 70)

# Save to file for verification
output_file = "/tmp/generated_metamath.mm"
with open(output_file, 'w') as f:
    f.write(db)

print(f"\nSaved to: {output_file}")
print("\nTo verify with metamath.exe:")
print(f"  cd /home/zar/claude/hyperon/metamath")
print(f"  ./metamath 'read \"{output_file}\"' 'verify proof *' quit")
