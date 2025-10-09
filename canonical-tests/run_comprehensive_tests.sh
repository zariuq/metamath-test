#!/bin/bash
# Comprehensive test runner for all Metamath verifiers
# Tests in CORE (strict) and POLICY (permissive) modes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verifiers
GOVERIFY="/home/zar/claude/hyperon/metamath/goverify/mmverify"
METAMATH_KNIFE="metamath-knife --verify"

# Mode
MODE="${1:---strict}"  # Default to strict

echo "========================================"
echo "Metamath Verifier Comprehensive Test"
echo "Mode: $MODE"
echo "========================================"
echo

# CORE tests (always run)
CORE_TESTS=(
    "test01_non_printable.mm"
    "test07_valid_minimal.mm"
    "test42_duplicate_include_main.mm"
    "test47_constant_inner_scope_main.mm"
    "test48_variable_conflict_main.mm"
    "test45_variable_redeclaration.mm"
)

# POLICY tests (only with --permissive)
POLICY_TESTS=(
    "test46_duplicate_include_main.mm"
)

# Test expectations (1=pass, 0=fail)
declare -A EXPECTED
EXPECTED["test01_non_printable.mm"]=0
EXPECTED["test07_valid_minimal.mm"]=1
EXPECTED["test42_duplicate_include_main.mm"]=1
EXPECTED["test47_constant_inner_scope_main.mm"]=0
EXPECTED["test48_variable_conflict_main.mm"]=0
EXPECTED["test45_variable_redeclaration.mm"]=1
EXPECTED["test46_duplicate_include_main.mm"]=1  # In permissive mode

test_verifier() {
    local verifier_name=$1
    local verifier_cmd=$2
    local tests=("${!3}")
    local pass=0
    local fail=0
    local total=0

    echo -e "${BLUE}Testing ${verifier_name}...${NC}"
    echo "---"

    for test in "${tests[@]}"; do
        if [ ! -f "$test" ]; then
            continue
        fi

        total=$((total + 1))
        local expected=${EXPECTED[$test]}

        # Run verifier
        if $verifier_cmd "$test" > /dev/null 2>&1; then
            local result=1
        else
            local result=0
        fi

        # Check expectation
        if [ $result -eq $expected ]; then
            echo -e "${GREEN}✓${NC} $test"
            pass=$((pass + 1))
        else
            if [ $expected -eq 1 ]; then
                echo -e "${RED}✗${NC} $test (should ACCEPT, but REJECTED)"
            else
                echo -e "${RED}✗${NC} $test (should REJECT, but ACCEPTED)"
            fi
            fail=$((fail + 1))
        fi
    done

    echo "---"
    echo -e "${verifier_name}: ${pass}/${total} tests passed"
    if [ $fail -gt 0 ]; then
        echo -e "${RED}Failures: ${fail}${NC}"
    fi
    echo
}

# Run CORE tests
echo -e "${YELLOW}=== CORE Tests (Binding Spec) ===${NC}"
echo

if [ -x "$GOVERIFY" ]; then
    test_verifier "goverify" "$GOVERIFY" CORE_TESTS[@]
else
    echo "goverify not found"
fi

if command -v metamath-knife &> /dev/null; then
    test_verifier "metamath-knife" "$METAMATH_KNIFE" CORE_TESTS[@]
else
    echo "metamath-knife not found"
fi

# Run POLICY tests if permissive mode
if [ "$MODE" = "--permissive" ]; then
    echo -e "${YELLOW}=== POLICY Tests (Permissive Mode) ===${NC}"
    echo

    if [ -x "$GOVERIFY" ]; then
        test_verifier "goverify (permissive)" "$GOVERIFY" POLICY_TESTS[@]
    fi

    # metamath-knife doesn't support permissive mode
    echo "Note: metamath-knife uses strict interpretation only"
    echo
fi

echo "========================================"
echo "Test run complete"
echo "========================================"
