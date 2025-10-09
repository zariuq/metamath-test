#!/bin/bash
# COMPREHENSIVE test of ALL 5 verifiers on ALL canonical tests
# No shortcuts - test everything

set +e  # Don't exit on error

# Find all main test files (exclude helpers/fragments/shared)
MAIN_TESTS=$(ls test*.mm 2>/dev/null | grep -v "helper\|fragment\|shared\|inner" | sort)
PERMISSIVE_TESTS=$(ls permissive/*.mm 2>/dev/null | grep -v "helper\|fragment" | sort)

# Count tests
CORE_COUNT=$(echo "$MAIN_TESTS" | wc -l)
PERM_COUNT=$(echo "$PERMISSIVE_TESTS" | wc -l)
TOTAL_COUNT=$((CORE_COUNT + PERM_COUNT))

echo "========================================================================"
echo "COMPREHENSIVE METAMATH VERIFIER TEST - ALL VERIFIERS, ALL TESTS"
echo "========================================================================"
echo "Date: $(date)"
echo "Location: $(pwd)"
echo ""
echo "CORE Tests: $CORE_COUNT"
echo "PERMISSIVE Tests: $PERM_COUNT"
echo "TOTAL Tests: $TOTAL_COUNT"
echo ""

# Verifier paths
METAMATH_EXE="/home/zar/.local/bin/metamath"
METAMATH_KNIFE="metamath-knife"
MM_LEAN4="/home/zar/claude/hyperon/metamath/mm-lean4/.lake/build/bin/mm-lean4"
MMVERIFY_PURE="/home/zar/claude/hyperon/metamath/metamath-test/gpt5_final_package/mmverify_pure.py"
GOVERIFY="/home/zar/claude/hyperon/metamath/goverify/mmverify"

# Test a single file with a single verifier
test_file() {
    local verifier_cmd="$1"
    local test_file="$2"
    
    if [ ! -f "$test_file" ]; then
        echo "SKIP"
        return
    fi
    
    if eval "$verifier_cmd \"$test_file\"" >/dev/null 2>&1; then
        echo "PASS"
    else
        echo "FAIL"
    fi
}

# Arrays to store results
declare -A results_metamath_exe
declare -A results_metamath_knife
declare -A results_mm_lean4
declare -A results_mm_lean4_perm
declare -A results_mmverify_pure
declare -A results_mmverify_pure_perm
declare -A results_goverify

echo "Testing verifiers on ALL tests..."
echo ""

# Test CORE tests
for test in $MAIN_TESTS; do
    echo -n "Testing $test... "
    
    # metamath.exe
    results_metamath_exe[$test]=$(test_file "$METAMATH_EXE \"\$test_file\" 'read \"\$test_file\"' 'verify proof *' 'exit' 2>&1 | grep -qi error && exit 1 || exit 0" "$test")
    
    # metamath-knife
    results_metamath_knife[$test]=$(test_file "$METAMATH_KNIFE --verify" "$test")
    
    # mm-lean4
    results_mm_lean4[$test]=$(test_file "$MM_LEAN4" "$test")
    
    # mm-lean4 --permissive
    results_mm_lean4_perm[$test]=$(test_file "$MM_LEAN4 --permissive" "$test")
    
    # mmverify_pure
    results_mmverify_pure[$test]=$(test_file "python3 $MMVERIFY_PURE" "$test")
    
    # mmverify_pure --permissive
    results_mmverify_pure_perm[$test]=$(test_file "python3 $MMVERIFY_PURE --permissive" "$test")
    
    # goverify
    results_goverify[$test]=$(test_file "$GOVERIFY" "$test")
    
    echo "done"
done

# Test PERMISSIVE tests
for test in $PERMISSIVE_TESTS; do
    echo -n "Testing $test... "
    
    # metamath.exe
    results_metamath_exe[$test]=$(test_file "$METAMATH_EXE \"\$test_file\" 'read \"\$test_file\"' 'verify proof *' 'exit' 2>&1 | grep -qi error && exit 1 || exit 0" "$test")
    
    # metamath-knife
    results_metamath_knife[$test]=$(test_file "$METAMATH_KNIFE --verify" "$test")
    
    # mm-lean4
    results_mm_lean4[$test]=$(test_file "$MM_LEAN4" "$test")
    
    # mm-lean4 --permissive
    results_mm_lean4_perm[$test]=$(test_file "$MM_LEAN4 --permissive" "$test")
    
    # mmverify_pure
    results_mmverify_pure[$test]=$(test_file "python3 $MMVERIFY_PURE" "$test")
    
    # mmverify_pure --permissive
    results_mmverify_pure_perm[$test]=$(test_file "python3 $MMVERIFY_PURE --permissive" "$test")
    
    # goverify
    results_goverify[$test]=$(test_file "$GOVERIFY" "$test")
    
    echo "done"
done

echo ""
echo "========================================================================"
echo "RESULTS - CORE TESTS"
echo "========================================================================"
echo ""

# Print header
printf "%-50s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s\n" \
    "TEST" "m.exe" "m-k" "lean" "l-p" "py" "py-p" "gov"
echo "--------------------------------------------------------------------------------"

# Print results for CORE tests
for test in $MAIN_TESTS; do
    printf "%-50s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s\n" \
        "$test" \
        "${results_metamath_exe[$test]}" \
        "${results_metamath_knife[$test]}" \
        "${results_mm_lean4[$test]}" \
        "${results_mm_lean4_perm[$test]}" \
        "${results_mmverify_pure[$test]}" \
        "${results_mmverify_pure_perm[$test]}" \
        "${results_goverify[$test]}"
done

echo ""
echo "========================================================================"
echo "RESULTS - PERMISSIVE TESTS"
echo "========================================================================"
echo ""

printf "%-50s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s\n" \
    "TEST" "m.exe" "m-k" "lean" "l-p" "py" "py-p" "gov"
echo "--------------------------------------------------------------------------------"

for test in $PERMISSIVE_TESTS; do
    printf "%-50s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s | %-4s\n" \
        "$test" \
        "${results_metamath_exe[$test]}" \
        "${results_metamath_knife[$test]}" \
        "${results_mm_lean4[$test]}" \
        "${results_mm_lean4_perm[$test]}" \
        "${results_mmverify_pure[$test]}" \
        "${results_mmverify_pure_perm[$test]}" \
        "${results_goverify[$test]}"
done

echo ""
echo "========================================================================"
echo "SUMMARY"
echo "========================================================================"
echo ""

# Calculate totals
for verifier in metamath_exe metamath_knife mm_lean4 mm_lean4_perm mmverify_pure mmverify_pure_perm goverify; do
    pass=0
    fail=0
    skip=0
    
    eval "declare -A arr=(\${results_${verifier}[@]})"
    
    for test in $MAIN_TESTS $PERMISSIVE_TESTS; do
        eval "result=\${results_${verifier}[$test]}"
        case "$result" in
            PASS) ((pass++)) ;;
            FAIL) ((fail++)) ;;
            SKIP) ((skip++)) ;;
        esac
    done
    
    echo "$verifier: $pass PASS, $fail FAIL, $skip SKIP (out of $TOTAL_COUNT)"
done

echo ""
echo "Legend:"
echo "  m.exe = metamath.exe"
echo "  m-k   = metamath-knife"
echo "  lean  = mm-lean4 (strict)"
echo "  l-p   = mm-lean4 --permissive"
echo "  py    = mmverify_pure (strict)"
echo "  py-p  = mmverify_pure --permissive"
echo "  gov   = goverify"
echo ""

