$( Test 56: Duplicate $d normalization - duplicates allowed; should ACCEPT per Sec 4.2.4 (union of DV pairs) $)

$c wff |- $.
$v x $.

$d x x $.
$d x x $.

f1 $f wff x $.
a1 $a |- x $.
p1 $p |- x $= f1 a1 $.
