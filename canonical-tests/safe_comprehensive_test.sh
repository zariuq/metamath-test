#!/bin/bash
# COMPREHENSIVE test - outputs to file to avoid terminal issues

OUTPUT_FILE="test_results_$(date +%Y%m%d_%H%M%S).txt"

exec > "$OUTPUT_FILE" 2>&1

echo "========================================================================"
echo "COMPREHENSIVE METAMATH VERIFIER TEST"
echo "========================================================================"
echo "Date: $(date)"
echo ""

# Find all main test files
MAIN_TESTS=$(find . -maxdepth 1 -name "test*.mm" -type f | grep -v "helper\|fragment\|shared\|inner" | sort)
PERM_TESTS=$(find permissive -name "test*.mm" -type f 2>/dev/null | grep -v "helper\|fragment" | sort)

CORE_COUNT=$(echo "$MAIN_TESTS" | wc -l)
PERM_COUNT=$(echo "$PERM_TESTS" | wc -l)

echo "Core tests: $CORE_COUNT"
echo "Permissive tests: $PERM_COUNT"
echo ""

# Verifiers
METAMATH_EXE="/home/zar/.local/bin/metamath"
METAMATH_KNIFE="metamath-knife"
MM_LEAN4="/home/zar/claude/hyperon/metamath/mm-lean4/.lake/build/bin/mm-lean4"
MMVERIFY_PURE="/home/zar/claude/hyperon/metamath/metamath-test/gpt5_final_package/mmverify_pure.py"
GOVERIFY="/home/zar/claude/hyperon/metamath/goverify/mmverify"

test_one() {
    local cmd="$1"
    local file="$2"
    
    if [ ! -f "$file" ]; then
        echo "SKIP"
        return
    fi
    
    if timeout 10 bash -c "$cmd \"$file\" >/dev/null 2>&1"; then
        echo "PASS"
    else
        echo "FAIL"
    fi
}

echo "========================================================================"
echo "TESTING CORE TESTS"
echo "========================================================================"
echo ""

for test in $MAIN_TESTS; do
    basename=$(basename "$test")
    echo "Test: $basename"
    
    echo -n "  metamath.exe:        "
    test_one "$METAMATH_EXE \"\$1\" 'read \"\$1\"' 'verify proof *' 'exit' 2>&1 | grep -qi error && exit 1 || exit 0" "$test"
    
    echo -n "  metamath-knife:      "
    test_one "$METAMATH_KNIFE --verify" "$test"
    
    echo -n "  mm-lean4:            "
    test_one "$MM_LEAN4" "$test"
    
    echo -n "  mm-lean4 --perm:     "
    test_one "$MM_LEAN4 --permissive" "$test"
    
    echo -n "  mmverify_pure:       "
    test_one "python3 $MMVERIFY_PURE" "$test"
    
    echo -n "  mmverify_pure --perm:"
    test_one "python3 $MMVERIFY_PURE --permissive" "$test"
    
    echo -n "  goverify:            "
    test_one "$GOVERIFY" "$test"
    
    echo ""
done

echo "========================================================================"
echo "TESTING PERMISSIVE TESTS"
echo "========================================================================"
echo ""

for test in $PERM_TESTS; do
    basename=$(basename "$test")
    echo "Test: $basename"
    
    echo -n "  metamath.exe:        "
    test_one "$METAMATH_EXE \"\$1\" 'read \"\$1\"' 'verify proof *' 'exit' 2>&1 | grep -qi error && exit 1 || exit 0" "$test"
    
    echo -n "  metamath-knife:      "
    test_one "$METAMATH_KNIFE --verify" "$test"
    
    echo -n "  mm-lean4:            "
    test_one "$MM_LEAN4" "$test"
    
    echo -n "  mm-lean4 --perm:     "
    test_one "$MM_LEAN4 --permissive" "$test"
    
    echo -n "  mmverify_pure:       "
    test_one "python3 $MMVERIFY_PURE" "$test"
    
    echo -n "  mmverify_pure --perm:"
    test_one "python3 $MMVERIFY_PURE --permissive" "$test"
    
    echo -n "  goverify:            "
    test_one "$GOVERIFY" "$test"
    
    echo ""
done

echo "========================================================================"
echo "TEST COMPLETE - Results saved to $OUTPUT_FILE"
echo "========================================================================"

