$( Unit Test 100: A compressed-proof header must not repeat an implicit
   mandatory hypothesis. Appendix B permits only non-mandatory hypotheses in
   the parenthesized label list. If the duplicate were accepted, BC would use
   the second wx heap entry and then apply ax, so the malformed proof would
   otherwise verify successfully. $)
$( Should reject: True $)

$c wff |- $.
$v x $.

wx $f wff x $.
ax $a |- x $.

bad $p |- x $= ( wx ax ) BC $.
