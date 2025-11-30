$( Unit Test 67: Top-level $e statements $)
$( Tests: Essential hypotheses at the outermost scope level
   Spec allows this - no restriction in EBNF or spec text.
   metamath-knife incorrectly REJECTS this (non-compliant).
   Official Metamath correctly ACCEPTS this. $)
$( Should accept: True $)

$c wff |- $.
$v ph ps $.
wp $f wff ph $.
wq $f wff ps $.

$( Top-level essential hypothesis - not inside any ${  $} block $)
hyp1 $e |- ph $.

$( This assertion has hyp1 as a mandatory hypothesis $)
ax1 $a |- ps $.
