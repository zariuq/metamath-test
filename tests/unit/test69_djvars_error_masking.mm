$( Test 69: $d with undeclared symbol should reject. $)
$( This currently exposes a parser diagnostic masking path in mm-lean4:
   the immediate token error can be overwritten by EOF unclosed-$d reporting. $)

$c wff $.
$v x $.

$d x y $.
