#!/usr/bin/env python3
"""
Properly score verifier results based on expected outcomes.
PASS when should PASS = correct
FAIL when should FAIL = correct
Otherwise = incorrect
"""

import re

# Define expected outcomes based on TEST_CATALOGUE.md
# Format: test_number: ('ACCEPT' or 'REJECT', 'description')
EXPECTED = {
    1: ('REJECT', 'Non-printable ASCII'),
    2: ('REJECT', 'Unclosed comment'),
    3: ('REJECT', 'Unmatched block close'),
    4: ('REJECT', 'Missing $. terminator'),
    5: ('REJECT', 'Empty label'),
    6: ('REJECT', 'Invalid token'),
    7: ('REJECT', 'Constant redeclaration'),  # Note: was listed as test 07 = "Valid minimal" but actually is redeclaration
    8: ('REJECT', 'Variable out of scope'),
    9: ('REJECT', 'Missing $d constraint'),
    10: ('REJECT', 'Duplicate label'),
    11: ('REJECT', 'Undefined variable'),
    12: ('REJECT', 'Undefined constant'),
    13: ('REJECT', 'Missing $f for variable'),
    14: ('REJECT', 'Variable without $f hypothesis'),
    15: ('REJECT', 'Multiple $f for variable'),
    16: ('REJECT', 'Conflicting typecodes'),
    17: ('REJECT', 'Include scope violation'),
    18: ('REJECT', 'Invalid proof step'),
    19: ('REJECT', 'Type mismatch in proof'),
    20: ('REJECT', 'Unknown step (should accept with warning)'),  # Actually might ACCEPT with warning
    21: ('REJECT', 'Self-referential proof'),
    22: ('REJECT', 'Typecode mismatch in substitution'),
    23: ('REJECT', 'Using non-essential hypotheses'),
    24: ('REJECT', 'Undefined label in proof'),
    25: ('REJECT', 'Missing space before comment'),
    26: ('REJECT', 'Wrong conclusion in proof'),
    27: ('REJECT', 'Disjoint variable constraint violation'),
    28: ('ACCEPT', 'Self-include (ignored)'),
    29: ('REJECT', 'Compressed proof header mismatch'),
    30: ('REJECT', 'Invalid compressed format'),  # Or ACCEPT if ? is allowed
    31: ('REJECT', 'Nested comments'),
    32: ('REJECT', 'Forward reference in proof'),
    33: ('REJECT', 'Compressed proof stack underflow'),
    34: ('REJECT', 'Label token in math context'),
    35: ('REJECT', '$f scope after block'),
    36: ('REJECT', 'Whitespace in compressed proof'),
    37: ('ACCEPT', 'RPN interleaving'),
    38: ('ACCEPT', 'Valid compressed (complex)'),
    39: ('ACCEPT', 'Basic include'),
    40: ('ACCEPT', 'Scoped include'),
    41: ('ACCEPT', 'Multiple includes'),
    42: ('ACCEPT', 'Duplicate include (2nd ignored)'),
    43: ('ACCEPT', 'Path canonicalization'),
    44: ('ACCEPT', 'Cycle detection (cycle ignored)'),
    45: ('ACCEPT', 'Variable redeclaration (sequential)'),
    46: ('ACCEPT_PERM', 'Include in inner blocks (permissive)'),
    47: ('REJECT', '$c in inner scope'),
    48: ('REJECT', 'Variable conflict via include'),
    49: ('ACCEPT_PERM', 'Token splice in axiom'),
    50: ('ACCEPT_PERM', 'Token splice in proof'),
}

# Read results
with open('test_results_20251008_102001.txt', 'r') as f:
    content = f.read()

# Parse results
verifiers = {
    'metamath.exe': {},
    'metamath-knife': {},
    'mm-lean4': {},
    'mm-lean4 --perm': {},
    'mmverify_pure': {},
    'mmverify_pure --perm': {},
    'goverify': {}
}

current_test = None
for line in content.split('\n'):
    # Match test lines like "Test: test07_redeclaration_of_constant.mm"
    test_match = re.match(r'Test: test(\d+)_.*\.mm', line)
    if test_match:
        current_test = int(test_match.group(1))
        continue
    
    # Match result lines
    for vname in verifiers.keys():
        if line.strip().startswith(vname + ':'):
            result = 'PASS' if 'PASS' in line else 'FAIL' if 'FAIL' in line else 'UNKNOWN'
            if current_test:
                verifiers[vname][current_test] = result

# Score each verifier
print("="*90)
print("PROPERLY SCORED VERIFIER RESULTS")
print("="*90)
print()
print("Scoring: CORRECT = got expected result, INCORRECT = got wrong result")
print()

for vname in ['metamath-knife', 'mm-lean4', 'mm-lean4 --perm', 'mmverify_pure', 'mmverify_pure --perm', 'goverify', 'metamath.exe']:
    results = verifiers[vname]
    
    correct_accept = 0
    correct_reject = 0
    incorrect_accept = 0  # Accepted when should reject
    incorrect_reject = 0  # Rejected when should accept
    not_tested = 0
    
    for test_num, (expected, desc) in EXPECTED.items():
        if test_num not in results:
            not_tested += 1
            continue
            
        actual = results[test_num]
        
        # For permissive-only tests, only count permissive mode verifiers
        if expected == 'ACCEPT_PERM':
            if '--perm' not in vname and vname != 'goverify':
                # Strict mode verifiers should reject permissive tests
                if actual == 'FAIL':
                    correct_reject += 1
                else:
                    incorrect_accept += 1
                continue
            else:
                # Permissive mode should accept
                expected = 'ACCEPT'
        
        if expected == 'ACCEPT':
            if actual == 'PASS':
                correct_accept += 1
            else:
                incorrect_reject += 1
        elif expected == 'REJECT':
            if actual == 'FAIL':
                correct_reject += 1
            else:
                incorrect_accept += 1
    
    total_correct = correct_accept + correct_reject
    total_incorrect = incorrect_accept + incorrect_reject
    total_tested = total_correct + total_incorrect
    
    accuracy = (total_correct / total_tested * 100) if total_tested > 0 else 0
    
    print(f"{vname:25s}")
    print(f"  Correct: {total_correct:3d} ({correct_accept} accept, {correct_reject} reject)")
    print(f"  Incorrect: {total_incorrect:3d} ({incorrect_accept} wrong accept, {incorrect_reject} wrong reject)")
    print(f"  Accuracy: {accuracy:5.1f}%")
    print()

