$( A variable declared in an outer block stays active after a deeper
   nested block closes. $)
$c wff $.
${
  $v x $.
  ${
    $v y $.
  $}
  fx $f wff x $.
$}
