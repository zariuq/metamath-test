$( Minimal test of compressed proof with Z (save) marker $)
$( This is designed to be the simplest possible Z test that should pass $)

$c wff ( ) -> $.
$v ph ps $.
wph $f wff ph $.
wps $f wff ps $.

$( Binary connective - implication $)
wi $a wff ( ph -> ps ) $.

$( Simple proof using Z:
   Prove: wff ( ( ph -> ps ) -> ( ph -> ps ) )

   Labels: wph=0, wps=1, wi=2

   Proof steps:
   A = 0 = push wph -> stack: [wff ph]
   B = 1 = push wps -> stack: [wff ph, wff ps]
   C = 2 = apply wi -> stack: [wff ( ph -> ps )]
   Z = -1 = save top -> saved: [wff ( ph -> ps )], stack: [wff ( ph -> ps )]
   D = 3 = recall saved[0] -> stack: [wff ( ph -> ps ), wff ( ph -> ps )]
   C = 2 = apply wi -> stack: [wff ( ( ph -> ps ) -> ( ph -> ps ) )]

   Compressed: ABCZDC
$)
th1 $p wff ( ( ph -> ps ) -> ( ph -> ps ) ) $= ( wi ) ABCZDC $.
