$( Test 53: $[ ... $] inside a $d statement - must REJECT per Sec 4.1.2 (includes only at outermost level) and Sec 4.2.4 (varlist only) $)

$c wff |- $.
$v x y $.

$d $[ ./helpers/test40_include_scope_correct_inner.mm $] x y $.
