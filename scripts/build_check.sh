#!/bin/bash
# Baut eine busycoq-Beweisdatei im Coq-Container und wertet Print Assumptions streng aus.
# Aufruf (cwd = busycoq/verify, busycoq auf Pin):
#   build_check.sh <git-rev>:<pfad> <Modulname> <Theorem>...
#   build_check.sh 57c9956:verify/M_...HHH.v M284pr halt halt_twin
# Umgebungsvariablen:
#   COQCHK_IF_UNDER=<sek>  coqchk -o laufen lassen, wenn der Bau schneller war (Limit COQCHK_LIMIT, Std. 1200 s)
set -euo pipefail
PIN=33209bc7dc282b38c8cd6be507bfc551fea56108
DEPS="LibTactics Helper Eqb HashTable TM Compute Flip Permute Pigeonhole Enumerate Individual BB62 Individual62 RWLAcc RWLAcc62 FastRev ES_v3"
src=$1; mod=$2; shift 2; theorems="$*"

# coqc aus dem opam-Switch des Images (Name je nach Image verschieden)
COQBIN=$(dirname "$(ls /home/coq/.opam/*/bin/coqc | head -1)")
export PATH=$COQBIN:$PATH
coqc --version | head -1
coqc -config | grep -E "^NATIVE_COMPILER_DEFAULT|^COQ_NATIVE" || true

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
echo "Langsamste Saetze (Zeichenbereich, Satz, Sekunden):"
grep -E '^Chars ' "$mod.time.log" | awk '{for(i=1;i<=NF;i++) if($i=="secs") print $(i-1), $0}' | sort -rn | head -6 | cut -d' ' -f2- | cut -c1-90
# Zeilennummern der langsamen Qed zuordnen
grep -E '^Chars ' "$mod.time.log" | awk '{for(i=1;i<=NF;i++) if($i=="secs" && $(i-1)>5) print $2}' | while read -r off; do
  line=$(head -c "$off" "$mod.v" | wc -l); echo "  >5s endet nahe Zeile $((line+1)): $(grep -nE '^(Theorem|Lemma)' "$mod.v" | awk -F: -v L=$((line+1)) '$1<=L' | tail -1 | cut -c1-70)"
done

fail=0
for th in $theorems; do
  printf 'From BusyCoq Require %s.\nPrint Assumptions %s.%s.\n' "$mod" "$mod" "$th" > "PA_$mod.v"
  out=$(coqc -Q . BusyCoq "PA_$mod.v" 2>&1)
  echo "--- Print Assumptions $mod.$th:"; echo "$out"
  if [ "$out" = "Closed under the global context" ]; then echo "STRENG OK $th"; else echo "STRENG FAIL $th"; fail=1; fi
done
rm -f "PA_$mod".*

if [ -n "${COQCHK_IF_UNDER:-}" ]; then
  if [ "$build" -lt "$COQCHK_IF_UNDER" ]; then
    lim=${COQCHK_LIMIT:-1200}; t0=$(date +%s)
    set +e; timeout "$lim" coqchk -o -Q . BusyCoq "BusyCoq.$mod" > "coqchk_$mod.log" 2>&1; rc=$?; set -e
    echo "COQCHK $mod: exit=$rc nach $(( $(date +%s) - t0 ))s (Limit ${lim}s)"
    sed -n '/CONTEXT SUMMARY/,$p' "coqchk_$mod.log" | head -40
    [ $rc -eq 0 ] || { tail -5 "coqchk_$mod.log"; fail=1; }
  else
    echo "COQCHK uebersprungen: Bau ${build}s >= ${COQCHK_IF_UNDER}s"
  fi
fi
exit $fail
