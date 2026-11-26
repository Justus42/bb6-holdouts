#!/bin/bash
# Baut eine busycoq-Beweisdatei im Coq-Container und wertet Print Assumptions streng aus.
# Aufruf (cwd = busycoq/verify, busycoq auf Pin):
#   build_check.sh <git-rev>:<pfad> <Modulname> <Theorem>...
#   build_check.sh 57c9956:verify/M_...HHH.v M284pr halt halt_twin
#   build_check.sh file:Pruefling.v Pruefling TM1.halt TM2.halt
# coqchk ist gestrichen (Werkzeuge haerten, 24.11.2026); massgeblich ist Print Assumptions streng.
set -euo pipefail
PIN=9c078caa3443e8027f5d2704e26c7228c1c86aa8
DEPS="LibTactics Helper Eqb HashTable TM Compute Flip Permute Pigeonhole Enumerate Individual BB62 Individual62 RWLAcc RWLAcc62 FastRev ES_v3"
[ $# -ge 3 ] || { echo "FEHLER: Aufruf build_check.sh <quelle> <Modul> <Theorem>... (mindestens ein Theorem)"; exit 2; }
src=$1; mod=$2; shift 2; theorems="$*"

# coqc aus dem opam-Switch des Images (Name je nach Image verschieden)
COQBIN=$(dirname "$(ls /home/coq/.opam/*/bin/coqc | head -1)")
export PATH=$COQBIN:$PATH
coqc --version | head -1
coqc -config | grep -E "^NATIVE_COMPILER_DEFAULT|^COQ_NATIVE" || true
# Nativ kompilierte Casts laufen auf dem System-Stack; mit 8 MB brach PR_Loop4Mono.v lokal beim
# Qed von halt_C mit "Dynlink error ... Stack overflow" ab. Stack anheben, soweit das Hard-Limit erlaubt.
ulimit -s unlimited 2>/dev/null || ulimit -s "$(ulimit -Hs)" 2>/dev/null || true
echo "Stack-Limit: $(ulimit -s) (hart: $(ulimit -Hs))"

head_sha=$(git -C .. rev-parse HEAD)
[ "$head_sha" = "$PIN" ] || { echo "FEHLER: busycoq nicht auf $PIN ($head_sha)"; exit 2; }

t0=$(date +%s)
for m in $DEPS; do [ -f "$m.vo" ] || coqc -Q . BusyCoq "$m.v"; done
echo "Abhaengigkeiten: $(( $(date +%s) - t0 ))s"

case "$src" in
  file:*) [ "${src#file:}" = "$mod.v" ] || cp "${src#file:}" "$mod.v"; echo "Quelle: lokale Datei ${src#file:}" ;;
  *) git -C .. show "$src" > "$mod.v"; echo "Quelle: $src ($(git -C .. rev-parse "${src%%:*}"))" ;;
esac
echo "sha256 $mod.v: $(sha256sum "$mod.v" | cut -c1-16)"
t0=$(date +%s)
coqc -time -Q . BusyCoq "$mod.v" > "$mod.time.log" 2>&1 || { tail -30 "$mod.time.log"; echo "coqc FEHLER"; exit 1; }
build=$(( $(date +%s) - t0 ))
echo "BAUZEIT $mod: ${build}s"; echo "$build" > "$mod.buildtime"
set +o pipefail   # head schliesst Pipes frueh (SIGPIPE), das ist hier gewollt
echo "Langsamste Saetze (Zeichenbereich, Satz, Sekunden):"
grep -E '^Chars ' "$mod.time.log" | awk '{for(i=1;i<=NF;i++) if($i=="secs") print $(i-1), $0}' | sort -rn | head -6 | cut -d' ' -f2- | cut -c1-90
# Zeilennummern der langsamen Qed zuordnen
grep -E '^Chars ' "$mod.time.log" | awk '{for(i=1;i<=NF;i++) if($i=="secs" && $(i-1)>5) print $2}' | while read -r off; do
  line=$(head -c "$off" "$mod.v" | wc -l); echo "  >5s endet nahe Zeile $((line+1)): $(grep -nE '^(Theorem|Lemma)' "$mod.v" | awk -F: -v L=$((line+1)) '$1<=L' | tail -1 | cut -c1-70)"
done

set -o pipefail
fail=0
for th in $theorems; do
  printf 'From BusyCoq Require %s.\nPrint Assumptions %s.%s.\n' "$mod" "$mod" "$th" > "PA_$mod.v"
  out=$(coqc -Q . BusyCoq "PA_$mod.v" 2>&1)
  echo "--- Print Assumptions $mod.$th:"; echo "$out"
  if [ "$out" = "Closed under the global context" ]; then echo "STRENG OK $th"; else echo "STRENG FAIL $th"; fail=1; fi
done
rm -f "PA_$mod".*
exit $fail
