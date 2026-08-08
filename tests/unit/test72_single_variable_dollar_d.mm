$( Unit Test 72: single-variable $d statement $)
$( Should reject: True $)
$( Book 4.2.4: a simple $d has two different active variables; the
   appendix grammar requires at least two. metamath.exe errors;
   metamath-knife also rejects (nonzero exit), reporting it at warning
   severity: "A $d statement which lists only one variable is
   meaningless". $)

$c wff $.
$v x $.
$d x $.
