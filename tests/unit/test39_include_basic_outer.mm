$( Unit Test 39: Basic include - outer file $)
$( Should reject: False - legitimate include should work $)

$( Include provides constants, variables, and axioms $)
$[ ./helpers/test39_helper.mm $]

$( Use the included axiom to prove something $)
th1 $p |- ph $= wph ax-1 $.
