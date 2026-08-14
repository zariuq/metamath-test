#!/bin/sh
# Driver for mm-lean4 (the batteries-only Lean 4 Metamath verifier).
#
# Contract (same as mmexe.sh): exit 0 on accept, non-zero on reject.
#
# Unlike metamath-exe (whose REPL always returns 0, forcing an output grep),
# mm-lean4 reports its verdict directly through the process exit code:
#   exit 0  -> "verified, N objects"   (accept)
#   exit 1  -> "at <pos>: <err>"        (reject)
# so we can simply forward the exit status.
#
# Mode: zar is the binary's default and the suite's spec-facing comparison
# configuration -- the same mode the existing ./test-mm-lean4 driver uses.

set -u

# Fail-closed: the suite must name the exact binary it tests.  A silent
# default can point at a stale build and make the whole run meaningless.
: "${MM_LEAN4:?MM_LEAN4 must name the freshly built mm-lean4 binary}"
if [ ! -x "$MM_LEAN4" ]; then
  echo "MM_LEAN4 is not an executable file: $MM_LEAN4" >&2
  exit 2
fi

exec "$MM_LEAN4" "$1"
