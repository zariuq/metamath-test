$( Unit Test 41: Multiple includes $)
$( Should reject: False - multiple includes should work $)

$c wff |- $.

$( Include file A $)
$[ ./helpers/test41_helper_a.mm $]

$( Include file B $)
$[ ./helpers/test41_helper_b.mm $]

$( Use content from both includes $)
th-a $p |- var-a $= fa ax-a $.
th-b $p |- var-b $= fb ax-b $.
