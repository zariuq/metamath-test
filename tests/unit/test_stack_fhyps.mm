$( Test for floating hypothesis consumption from stack $)

$c wff |- term |= $.
$v R S T $.

wR $f term R $.
wS $f term S $.
wT $f term T $.

${
  ax-syl.1 $e |- R |= S $.
  ax-syl.2 $e |- S |= T $.
  $( Syllogism: if R implies S and S implies T, then R implies T $)
  ax-syl $a |- R |= T $.
$}

${
  syl.1 $e |- R |= S $.
  syl.2 $e |- S |= T $.
  $( Proof using ax-syl - should need 5 items on stack:
     3 floating hyps (term R, term S, term T) + 2 essential hyps $)
  syl $p |- R |= T $= wR wS wT syl.1 syl.2 ax-syl $.
$}
