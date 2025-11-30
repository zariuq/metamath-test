$( Minimal test of compressed proof with Z (save) marker $)

$c wff |- $.
$v ph ps $.
wph $f wff ph $.
wps $f wff ps $.

$( A simple axiom - implication introduction $)
ax-1 $a |- ( ph -> ( ps -> ph ) ) $.

$( Axiom using ax-1 as basis $)
wi $a wff ( ph -> ps ) $.

$( Prove something using Z - save and reuse $)
$( This proof:
   - A = index 0 = wph (mandatory f-hyp for ph)
   - B = index 1 = wps (mandatory f-hyp for ps)
   - C = index 2 = wi (explicit label)
   - D = index 3 = ax-1 (explicit label)
   So: ( wi ax-1 ) A B C Z D means:
   1. Push wph -> get "wff ph" on stack
   2. Push wps -> get "wff ps" on stack
   3. Apply wi -> get "wff ( ph -> ps )" on stack
   4. Z = save top (which is "wff ( ph -> ps )")
   5. Apply ax-1 with substitutions -> get "|- ( ph -> ( ps -> ph ) )"
   Actually, let me simplify...
$)

$( Simple proof without Z first to verify basic compressed proofs work $)
simple1 $p wff ( ph -> ps ) $= ( wi ) AB $.

$( Now with Z $)
$.
