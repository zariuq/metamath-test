#!/bin/bash
# Show sample outputs from verifiers

echo "========================================================================"
echo "SAMPLE ERROR MESSAGES FROM VERIFIERS"
echo "========================================================================"
echo ""

echo "--- Test 47: $c in inner scope (SHOULD REJECT) ---"
echo ""

echo "1. mm-lean4 (strict mode):"
/home/zar/claude/hyperon/metamath/mm-lean4/.lake/build/bin/mm-lean4 test47_constant_inner_scope_main.mm 2>&1 | head -3
echo ""

echo "2. mmverify_pure (strict mode):"
python3 /home/zar/claude/hyperon/metamath/metamath-test/gpt5_final_package/mmverify_pure.py test47_constant_inner_scope_main.mm 2>&1 | tail -1
echo ""

echo "3. metamath-knife (strict mode):"
metamath-knife --verify test47_constant_inner_scope_main.mm 2>&1 | head -3
echo ""

echo "4. goverify (BUG - incorrectly accepts):"
/home/zar/claude/hyperon/metamath/goverify/mmverify test47_constant_inner_scope_main.mm 2>&1 | head -1
echo ""

echo "========================================================================"
echo ""

echo "--- Test 47: $c in inner scope WITH --permissive (SHOULD ACCEPT) ---"
echo ""

echo "1. mm-lean4 --permissive:"
/home/zar/claude/hyperon/metamath/mm-lean4/.lake/build/bin/mm-lean4 --permissive test47_constant_inner_scope_main.mm 2>&1
echo ""

echo "2. mmverify_pure --permissive:"
python3 /home/zar/claude/hyperon/metamath/metamath-test/gpt5_final_package/mmverify_pure.py --permissive test47_constant_inner_scope_main.mm 2>&1 | tail -1
echo ""

echo "========================================================================"
echo ""

echo "--- Test 48: Variable conflict (SHOULD REJECT) ---"
echo ""

echo "1. mm-lean4:"
/home/zar/claude/hyperon/metamath/mm-lean4/.lake/build/bin/mm-lean4 test48_variable_conflict_main.mm 2>&1 | head -3
echo ""

echo "2. mmverify_pure:"
python3 /home/zar/claude/hyperon/metamath/metamath-test/gpt5_final_package/mmverify_pure.py test48_variable_conflict_main.mm 2>&1 | tail -1
echo ""

echo "3. goverify (BUG - incorrectly accepts):"
/home/zar/claude/hyperon/metamath/goverify/mmverify test48_variable_conflict_main.mm 2>&1 | head -1
echo ""

echo "========================================================================"
