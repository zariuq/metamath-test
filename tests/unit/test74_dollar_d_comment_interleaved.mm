$( Unit Test 74: comment inside a $d statement $)
$( Should reject: False $)
$( Sec. 4.1.2: comments are whitespace and may appear between any two
   tokens; the parser must resume the $d accumulation afterwards, so the
   statement still reaches the terminator with two variables. $)

$c wff $.
$v x y $.
$d x $( interleaved comment $) y $.
