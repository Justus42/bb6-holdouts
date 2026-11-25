#!/bin/bash
# Abgleich ctl_sat.py (SAT, mit Symmetriebrechung) gegen ctl_brute.py (Aufzaehlung) auf Zufallstabellen
# und Gruppe 1. Ausgabe: je Fall beide Ergebnisse, am Ende Zahl der Abweichungen.
G1=1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC
python3 - > /tmp/claude-0/-home-user/0eba6a1f-2e90-5f97-8ba2-eb99d06db2b3/scratchpad/zufall.txt <<'PY'
import random
random.seed(20261125)
for i in range(50):
    zellen = []
    halt = random.randrange(12)
    for k in range(12):
        if k == halt: zellen.append('---')
        else: zellen.append(f"{random.randint(0,1)}{random.choice('LR')}{random.choice('ABCDEF')}")
    zellen[0] = '1R' + zellen[0][2] if zellen[0] != '---' else '1RB'
    print('_'.join(zellen[2*q]+zellen[2*q+1] for q in range(6)))
PY
n=0; ab=0; sat=0
run() { # tm nL nR start
  a=$(python3 ctl_sat.py $1 $2 $3 $4 2>/dev/null | head -1 | sed 's/.*ergebnis=//')
  b=$(python3 ctl_brute.py $1 $2 $3 $4 | sed 's/.*ergebnis=//')
  n=$((n+1)); [ "$a" = SAT ] && sat=$((sat+1))
  [ "$a" != "$b" ] && { ab=$((ab+1)); echo "ABWEICHUNG $1 $2x$3 $4: sat=$a brute=$b"; }
}
for S in A D C; do for g in "1 1" "1 2" "2 1" "2 2" "3 2" "2 3" "3 3"; do run $G1 $g $S; done; done
while read M; do for g in "1 1" "2 1" "1 2" "2 2" "3 2" "2 3"; do run $M $g A; done; done < /tmp/claude-0/-home-user/0eba6a1f-2e90-5f97-8ba2-eb99d06db2b3/scratchpad/zufall.txt
echo "Faelle: $n, davon SAT: $sat, Abweichungen: $ab"
