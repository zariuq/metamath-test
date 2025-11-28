$( Test 57: Case sensitivity for labels - labels are case-sensitive per Sec 4.1.3; should ACCEPT $)

$c wff |- $.
$v ph $.

f1 $f wff ph $.
ax $a |- ph $.
Ax $a |- ph $.

p1 $p |- ph $= f1 ax $.
p2 $p |- ph $= f1 Ax $.
