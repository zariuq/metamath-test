# Metamath Canonical Test Suite

A comprehensive test suite for Metamath verifier implementations.

**Total Tests:** 92 (56 unit + 31 small canonical + 3 large canonical + 2 optional categories)

## Organization

```
canonical-tests/
├── unit-tests/              # Custom spec tests (56 tests)
│   └── test*.mm            # 20 positive, 38 negative
├── canonical/              # Canonical tests from metamath community
│   ├── small/              # Small tests (31 tests)
│   │   └── *.mm           # 17 positive, 14 negative
│   └── large/              # Large databases (3 symlinks)
│       ├── set.mm         # 796k lines (positive)
│       ├── miu.mm         # 144 lines (positive)
│       └── demo0-full.mm  # 1323 lines (positive)
├── drivers/                
│   └── test_runner.py     # Multi-verifier test runner
└── [documentation]
```

## Quick Start

### Test Single File
```bash
# With metamath-knife (recommended)
cd canonical/small
metamath-knife --verify anatomy.mm

# With mmexe.sh
cd ~/claude/hyperon/metamath/metamath-test
./mmexe.sh canonical-tests/canonical/small/anatomy.mm

# With test runner
cd canonical-tests
python3 drivers/test_runner.py --verifier mmverify \
    --test-file canonical/small/anatomy.mm
```

### Test Directory
```bash
cd canonical-tests
python3 drivers/test_runner.py --verifier mmverify \
    --test-dir canonical/small/ --verbose
```

## Test Statistics

| Category | Tests | Positive | Negative | Source |
|----------|-------|----------|----------|--------|
| Unit tests | 56 | 20 | 38 | Custom (spec compliance) |
| Canonical small | 31 | 17 | 14 | ~/claude/hyperon/metamath/tests/ |
| Canonical large | 3 | 3 | 0 | Production databases |
| **TOTAL** | **90** | **40** | **52** | |

## Documentation

- **CANONICAL_TESTS_COMPLETE.md** - Complete canonical test documentation
  - All 31 small tests classified with metamath-knife + mmexe.sh
  - Positive/negative determination
  - Expected errors for negative tests
  
- **TEST_INVENTORY.md** - Complete test inventory (all 92 tests)

- **TEST_CATALOGUE.md** - Unit test details

- **README.md** - This file (quick start)

- **REORGANIZATION_SUMMARY.md** - How tests were reorganized

## Available Verifiers

List verifiers:
```bash
python3 drivers/test_runner.py --list-verifiers
```

Supported:
- `metamath` - metamath.exe (reference C)
- `mmverify_canonical` - mmverify_canonical.py (reference Python)
- `mmverify` - mmverify.py (fixed mmverify_pure.py)
- `mmverify_original` - Original mmverify.py

## Quick Examples

```bash
cd ~/claude/hyperon/metamath/metamath-test/canonical-tests

# Test positive case
python3 drivers/test_runner.py --verifier mmverify \
    --test-file canonical/small/anatomy.mm
# Expected: ✓ PASS

# Test negative case  
python3 drivers/test_runner.py --verifier mmverify \
    --test-file canonical/small/disjoint1.mm
# Expected: ✗ FAIL (correctly rejects invalid test)

# Test large database
python3 drivers/test_runner.py --verifier mmverify \
    --test-file canonical/large/miu.mm
# Expected: ✓ PASS
```

## Classification

Tests classified using both reference implementations:
- **metamath-knife** (Rust, most reliable)
- **mmexe.sh** (C reference, metamath.exe)

Agreement: 100% (all tests agree)

---

**Last Updated:** 2025-10-28
**Canonical tests verified:** 34 (31 small + 3 large)
