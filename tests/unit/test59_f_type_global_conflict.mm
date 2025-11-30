$( test59_f_type_global_conflict.mm - ACCEPT (SPEC DIVERGENCE!)
   Spec 4.1.3 L156-158 says:
   "The type declared by a $f statement for a given label is global even if
   the variable is not (e.g., a database may not have wff P in one local
   scope and class P in another)."

   HOWEVER: All three verifiers (metamath.exe, metamath-knife, mmverify.py)
   ACCEPT having the same variable with different types in different scopes!

   This is documented as a SPEC DIVERGENCE: the spec says REJECT, but
   all implementations ACCEPT. The convention in set.mm is to never do this,
   so it's never been caught.

   For our test suite, we follow the IMPLEMENTATIONS (ACCEPT), not the spec.
$)

$c wff class |- $.

$( First scope: x is wff $)
${
  $v x $.
  wx $f wff x $.
  ax1 $a wff x $.
$}

$( Second scope: x is class - spec says REJECT, implementations say ACCEPT $)
${
  $v x $.
  cx $f class x $.
  ax2 $a class x $.
$}
