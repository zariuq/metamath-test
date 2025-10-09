#!/bin/bash
# Update all test files with proper spec citations and categories
# Based on TEST_CATALOGUE.md

# Test 46 is now POLICY (permissive mode)
echo "Updating Test 46 to POLICY category..."
if [ -f test46_duplicate_include_main.mm ]; then
    # Already has UTF-8 fix from earlier, just add POLICY marker
    sed -i '2 a $( Category: POLICY - Permissive include mode $)' test46_duplicate_include_main.mm
fi

# Test 47 - CRITICAL CORE test
echo "Updating Test 47 (CRITICAL)..."
if [ -f test47_constant_inner_scope_main.mm ]; then
    sed -i '1 a $( Category: CORE - CRITICAL scoping test $)' test47_constant_inner_scope_main.mm
fi

# Test 48 - CRITICAL CORE test
echo "Updating Test 48 (CRITICAL)..."
if [ -f test48_variable_conflict_main.mm ]; then
    sed -i '1 a $( Category: CORE - CRITICAL scoping test $)' test48_variable_conflict_main.mm
fi

# Tests 49-50 - POLICY (optional token splice)
for test in test49_token_splice_axiom_main.mm test50_token_splice_proof_main.mm; do
    if [ -f "$test" ]; then
        echo "Updating $test to POLICY..."
        sed -i '2 a $( Category: POLICY - Optional token splice $)' "$test"
    fi
done

echo "Test headers updated with categories"
