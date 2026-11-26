#!/bin/bash
# Punkt 4: CTL-Suche mit festem rechten Automaten fuer 318 und 518 (Start A), linker DFA nL = 1..14.
# Je Groesse hoechstens $GRENZE Sekunden (lokal); bei Zeitueberschreitung bricht die Reihe fuer diese Kombination ab.
GRENZE=${GRENZE:-480}
T318=1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC
T518=1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---
art=$1; name=$2; eval M=\$T$name
for nL in $(seq 1 ${3:-14}); do
  out=$(timeout $GRENZE python3 ctl_fest.py $M $art $nL A --aus zertifikate/m5_${name}_${art}_$nL.json | sed -n 1p)
  if [ -z "$out" ]; then echo "$name $art nL=$nL ZEITGRENZE ${GRENZE}s"; break; fi
  echo "$name $art $out"
  case "$out" in *ergebnis=SAT*) python3 ../invarianten/ctl_pruefer.py zertifikate/m5_${name}_${art}_$nL.json 1000000; break;; esac
done
