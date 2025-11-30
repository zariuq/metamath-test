$( Unit Test 49: Include as token splice in axiom $)
$( Should reject: True - include inside statement is invalid in strict mode $)
$( Category: CORE - Strict include semantics $)
$( Spec Section 4.1.2: "include directives are processed at outermost level" $)
$( Spec Appendix E: Include not allowed inside statements $)

$c wff |- $.
$v x $.
fx $f wff x $.

$( Include splices tokens into the middle of this statement - INVALID $)
ax-splice $a $[ ./helpers/test49_helper.mm $]
