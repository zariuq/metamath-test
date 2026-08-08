$( Unit Test 76: unterminated $d at end of file $)
$( Should reject: True $)
$( Classification check: an unterminated $d must be reported as an
   unclosed statement, NOT as a too-short one -- the arity gate applies
   only to statements that actually reach their $. terminator. $)

$c wff $.
$v x $.
$d x
