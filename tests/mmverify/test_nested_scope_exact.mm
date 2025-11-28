$( Test case mimicking HOL's dfov1/dfov2 structure exactly $)

$c term |- |= $.
$v R S T A $.

tr $f term R $.
ts $f term S $.
tt $f term T $.
ta $f term A $.

$( Base axiom $)
${
  ax.1 $e |- R |= S $.
  ax.2 $e |- S |= T $.
  ax $a |- R |= T $.
$}

$( Mimics dfov1/dfov2 structure:
   outer scope has e1, e2, e3
   inner scope adds e4, defines thm1
   outer scope continues with e5, defines thm2
   thm2 should only see e1, e2, e3, e5 = 4 ehyps, NOT e4
$)
${
  e1 $e |- R |= S $.
  e2 $e |- S |= T $.
  e3 $e |- T |= A $.

  ${
    e4 $e |- R |= T $.
    $( inner-thm uses e4 and e3 $)
    inner-thm $p |- R |= A $= tr tt ta e4 e3 ax $.
  $}

  e5 $e |- R |= T $.
  $( outer-thm should use e5 and e3 = 2 ehyps from current scope $)
  $( If e4 leaks, make_assertion will think it needs 3 ehyps $)
  outer-thm $p |- R |= A $= tr tt ta e5 e3 ax $.
$}
