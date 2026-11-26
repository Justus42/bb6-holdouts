#!/bin/sh
# Prueft den in busycoq (seit 33209bc7, Pin jetzt 9c078ca) gemergten Beweis aus PR #32 (verify/PR_Loop4Mono.v),
# kompiliert als M284.v. Aufruf im coqorg/coq:8.20.1-Container, cwd = busycoq/verify.
#   check_m284.sh deps     -> nur Abhaengigkeiten bauen
#   check_m284.sh main     -> M284.v kompilieren + Print Assumptions (streng)
#   check_m284.sh all      -> beides
set -eu
PIN=9c078caa3443e8027f5d2704e26c7228c1c86aa8
DEPS="LibTactics Helper Eqb HashTable TM Compute Flip Permute Pigeonhole Enumerate Individual BB62 Individual62 RWLAcc RWLAcc62 FastRev ES_v3"
THEOREMS="TM1.halt TM2.halt"
export PATH=/home/coq/.opam/4.13.1+flambda/bin:$PATH
now() { date +%s; }

head_sha=$(git -C .. rev-parse HEAD 2>/dev/null || echo unknown)
echo "busycoq HEAD: $head_sha"
[ "$head_sha" = "$PIN" ] || { echo "FEHLER: busycoq nicht auf $PIN"; exit 2; }
coqc --version | head -1

do_deps() {
  for m in $DEPS; do
    t0=$(now); coqc -Q . BusyCoq "$m.v"; echo "dep $m: $(( $(now) - t0 ))s"
  done
}

do_main() {
  [ -f M284.v ] || cp PR_Loop4Mono.v M284.v
  t0=$(now); coqc -Q . BusyCoq M284.v; echo "M284.v kompiliert: $(( $(now) - t0 ))s"
  fail=0
  for th in $THEOREMS; do
    printf 'From BusyCoq Require M284.\nPrint Assumptions M284.%s.\n' "$th" > PA_M284.v
    out=$(coqc -Q . BusyCoq PA_M284.v 2>&1)
    echo "--- Print Assumptions M284.$th:"; echo "$out"
    # streng: Ausgabe muss exakt diese eine Zeile sein
    if [ "$out" = "Closed under the global context" ]; then echo "OK $th"; else echo "FAIL $th"; fail=1; fi
  done
  rm -f PA_M284.v PA_M284.vo PA_M284.vok PA_M284.vos PA_M284.glob .PA_M284.aux
  return $fail
}

case "${1:-all}" in
  deps) do_deps ;;
  main) do_main ;;
  all)  do_deps; do_main ;;
  *) echo "usage: $0 deps|main|all"; exit 2 ;;
esac
