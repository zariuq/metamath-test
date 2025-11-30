$( Unit Test 50: Include as token splice in proof $)
$( Should reject: True - include inside statement is invalid in strict mode $)
$( Category: CORE - Strict include semantics $)
$( Spec Section 4.1.2: "include directives are processed at outermost level" $)
$( Spec Appendix E: Include not allowed inside statements $)

$c wff |- $.
$v x $.
fx $f wff x $.
ax-x $a |- x $.

$( Include splices proof steps from external file - INVALID $)
th $p |- x $= $[ ./helpers/test50_helper.mm $] $.
