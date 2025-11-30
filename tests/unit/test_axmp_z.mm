$( Minimal test: ax-mp with essential hypotheses and Z marker $)

$c wff |- e ( , ) $.
$v x y $.

wx $f wff x $.
wy $f wff y $.

$( Binary connective $)
wi $a wff e ( x , y ) $.

$( Modus ponens with essential hypotheses $)
${
  ax-mp.1 $e |- x $.
  ax-mp.2 $e |- e ( x , y ) $.
  ax-mp $a |- y $.
$}

$( A simple axiom to use $)
ax1 $a |- e ( x , e ( y , x ) ) $.

$(
  Compressed proof using Z:
  Goal: |- e ( x , e ( y , x ) )

  Labels: wx=0, wy=1, wi=2, ax-mp=3, ax1=4

  Proof steps for normal proof:
  wx wy ax1 => |- e ( x , e ( y , x ) )

  As compressed: ( wi ax-mp ax1 ) ABC
    A=0=wx, B=1=wy, C=2=ax1
$)
th1 $p |- e ( x , e ( y , x ) ) $= ( wi ax-mp ax1 ) ABC $.
