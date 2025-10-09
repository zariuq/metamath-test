#!/bin/bash
# Comprehensive test of all 5 verifiers on canonical test suite
# Tests both strict and permissive modes

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Verifier paths
METAMATH_EXE="/home/zar/.local/bin/metamath"
METAMATH_KNIFE="metamath-knife"
MM_LEAN4="/home/zar/claude/hyperon/metamath/mm-lean4/.lake/build/bin/mm-lean4"
MMVERIFY_PURE="/home/zar/claude/hyperon/metamath/metamath-test/gpt5_final_package/mmverify_pure.py"
GOVERIFY="/home/zar/claude/hyperon/metamath/goverify/mmverify"

# CORE tests (strict mode - all should pass these expectations)
CORE_TESTS=(
    "test07_redeclaration_of_constant.mm:reject"
    "test45_variable_redeclaration.mm:accept"
    "test47_constant_inner_scope_main.mm:reject"
    "test48_variable_conflict_main.mm:reject"
)

# POLICY tests (permissive mode only)
POLICY_TESTS=(
    "permissive/test46_duplicate_include_main.mm:accept"
    "permissive/test49_token_splice_axiom_main.mm:accept"
    "permissive/test50_token_splice_proof_main.mm:accept"
)

echo "========================================================================"
echo "          COMPREHENSIVE METAMATH VERIFIER TEST SUITE"
echo "========================================================================"
echo "Date: $(date)"
echo "Location: $(pwd)"
echo ""

# Helper function to test a file
test_file() {
    local verifier_name=$1
    local verifier_cmd=$2
    local test_file=$3
    local expected=$4  # "accept" or "reject"

    if [ ! -f "$test_file" ]; then
        echo "  ⚠  $test_file (file not found)"
        return 2
    fi

    # Run verifier
    local result
    if eval "$verifier_cmd \"$test_file\"" >/dev/null 2>&1; then
        result="accept"
    else
        result="reject"
    fi

    # Check expectation
    if [ "$result" = "$expected" ]; then
        echo -e "  ${GREEN}✓${NC} $test_file (${expected})"
        return 0
    else
        echo -e "  ${RED}✗${NC} $test_file (expected: ${expected}, got: ${result})"
        return 1
    fi
}

test_verifier() {
    local name=$1
    local cmd=$2
    local tests_array=$3
    local mode=$4  # "strict" or "permissive"

    echo -e "${BLUE}Testing ${name} [${mode}]...${NC}"

    local pass=0
    local fail=0
    local total=0

    eval "local test_list=(\"\${${tests_array}[@]}\")"

    for test_spec in "${test_list[@]}"; do
        IFS=':' read -r test_file expected <<< "$test_spec"
        total=$((total + 1))

        if test_file "$name" "$cmd" "$test_file" "$expected"; then
            pass=$((pass + 1))
        else
            fail=$((fail + 1))
        fi
    done

    echo "  ---"
    if [ $fail -eq 0 ]; then
        echo -e "  ${GREEN}Score: ${pass}/${total}${NC}"
    else
        echo -e "  ${YELLOW}Score: ${pass}/${total} (${fail} failures)${NC}"
    fi
    echo ""
}

echo "========================================================================"
echo "PART 1: CORE TESTS (STRICT MODE - REQUIRED)"
echo "========================================================================"
echo ""

# metamath.exe
if [ -x "$METAMATH_EXE" ]; then
    test_verifier "metamath.exe" \
        "$METAMATH_EXE \"\$test_file\" 'read \"\$test_file\"' 'verify proof *' 'exit' 2>&1 | grep -qi error && exit 1 || exit 0" \
        "CORE_TESTS" "strict"
else
    echo -e "${YELLOW}metamath.exe not found${NC}\n"
fi

# metamath-knife
if command -v $METAMATH_KNIFE &> /dev/null; then
    test_verifier "metamath-knife" \
        "$METAMATH_KNIFE --verify" \
        "CORE_TESTS" "strict"
else
    echo -e "${YELLOW}metamath-knife not found${NC}\n"
fi

# mm-lean4 (strict)
if [ -x "$MM_LEAN4" ]; then
    test_verifier "mm-lean4" \
        "$MM_LEAN4" \
        "CORE_TESTS" "strict"
else
    echo -e "${YELLOW}mm-lean4 not found${NC}\n"
fi

# mmverify_pure (strict)
if [ -f "$MMVERIFY_PURE" ]; then
    test_verifier "mmverify_pure" \
        "python3 $MMVERIFY_PURE" \
        "CORE_TESTS" "strict"
else
    echo -e "${YELLOW}mmverify_pure not found${NC}\n"
fi

# goverify
if [ -x "$GOVERIFY" ]; then
    test_verifier "goverify" \
        "$GOVERIFY" \
        "CORE_TESTS" "strict"
else
    echo -e "${YELLOW}goverify not found${NC}\n"
fi

echo "========================================================================"
echo "PART 2: POLICY TESTS (PERMISSIVE MODE - OPTIONAL)"
echo "========================================================================"
echo ""

# mm-lean4 (permissive)
if [ -x "$MM_LEAN4" ]; then
    test_verifier "mm-lean4 --permissive" \
        "$MM_LEAN4 --permissive" \
        "POLICY_TESTS" "permissive"
else
    echo -e "${YELLOW}mm-lean4 not found${NC}\n"
fi

# mmverify_pure (permissive)
if [ -f "$MMVERIFY_PURE" ]; then
    test_verifier "mmverify_pure --permissive" \
        "python3 $MMVERIFY_PURE --permissive" \
        "POLICY_TESTS" "permissive"
else
    echo -e "${YELLOW}mmverify_pure not found${NC}\n"
fi

# goverify (implicit permissive)
if [ -x "$GOVERIFY" ]; then
    test_verifier "goverify (implicit permissive)" \
        "$GOVERIFY" \
        "POLICY_TESTS" "permissive"
else
    echo -e "${YELLOW}goverify not found${NC}\n"
fi

echo "========================================================================"
echo "TEST SUITE COMPLETE"
echo "========================================================================"
