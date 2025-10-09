#!/usr/bin/env python3
import re
from collections import defaultdict

with open('test_results_20251008_102001.txt', 'r') as f:
    content = f.read()

# Count results per verifier
verifiers = ['metamath.exe', 'metamath-knife', 'mm-lean4', 'mm-lean4 --perm', 'mmverify_pure', 'mmverify_pure --perm', 'goverify']
results = {v: {'PASS': 0, 'FAIL': 0} for v in verifiers}

for line in content.split('\n'):
    for verifier in verifiers:
        if line.strip().startswith(verifier + ':'):
            if 'PASS' in line:
                results[verifier]['PASS'] += 1
            elif 'FAIL' in line:
                results[verifier]['FAIL'] += 1

print("="*80)
print("COMPREHENSIVE TEST RESULTS SUMMARY")
print("="*80)
print()
print(f"{'Verifier':<25} {'PASS':>8} {'FAIL':>8} {'Total':>8}")
print("-"*80)

for verifier in verifiers:
    total = results[verifier]['PASS'] + results[verifier]['FAIL']
    print(f"{verifier:<25} {results[verifier]['PASS']:>8} {results[verifier]['FAIL']:>8} {total:>8}")

print("="*80)
