$( Minimal test for compressed proof with multiple floating hypotheses $)

$c term |- |= $.
$v R S T $.

tR $f term R $.
tS $f term S $.
tT $f term T $.

${
  syl.1 $e |- R |= S $.
  syl.2 $e |- S |= T $.
  $( Syllogism axiom $)
  ax-syl $a |- R |= T $.
$}

${
  th.1 $e |- R |= S $.
  th.2 $e |- S |= T $.
  $( Theorem using compressed proof - should push tR, tS, tT before ax-syl $)
  th $p |- R |= T $= ( ax-syl ) ABCDEF $.
$}
