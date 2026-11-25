#!/bin/bash
# Direkte TM-Simulation gegen Rundenmodell (runde.c) ab Zufalls-Startwoertern, fuer 396 und 587 (Thread "396, Teil 2").
# Prueft das Rundenmodell einschliesslich 1011-Regel (396: 0001x, 587: 1000x) und Halt bei 111 an der echten Maschine.
# Aufruf: bash tm_zufall.sh <anzahl> [runden]   Negativkontrollen: FEHLER=1 (an runde.c durchgereicht), TAUSCH=1 (Rundenmodell der jeweils anderen Maschine).
set -u
cd "$(dirname "$0")"
N=${1:-100}; R=${2:-10}
declare -A TM=( [396]=1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA--- [587]=1RB1LD_0RC0LF_1LD1RE_0LA0RB_0RD1RB_0LD--- )
abw=0; halt=0; k1011=0; n=0; schritte=0
for i in $(seq 1 "$N"); do
  w=$(python3 -c "import random; random.seed($i); L=random.randint(4,14); print(''.join(random.choice('01') for _ in range(L)).rstrip('0') or '1')")
  for m in 396 587; do
    d=$(./direkt_start "${TM[$m]}" $m "$w" "$R" 300000000)
    if echo "$d" | grep -q '^SCHRITTE\|^RAND'; then schritte=$((schritte+1)); continue; fi
    rm_=$m; [ -n "${TAUSCH:-}" ] && { [ $m = 396 ] && rm_=587 || rm_=396; }
    r=$(./runde $rm_ "$R" "$R" "$w" 2>/dev/null)
    a=$(echo "$d" | awk '/^R/ && $2>0 {print "R",$2,$3} /^HALT/ {print "HALT",$2}')
    b=$(echo "$r" | awk '/^R / {print "R",$2,$3} /^HALT 111 in Runde/ {sub(",","",$5); print "HALT",$5}')
    n=$((n+1))
    echo "$b" | grep -q HALT && halt=$((halt+1))
    echo "$r" | grep -q 'EREIGNIS 1011' && k1011=$((k1011+1))
    if [ "$a" != "$b" ]; then abw=$((abw+1)); [ $abw -le 3 ] && { echo "ABWEICHUNG $m $w"; diff <(echo "$a") <(echo "$b") | head -4; }; fi
  done
done
echo "tm_zufall: $n Laeufe verglichen ($halt mit Halt, $k1011 mit 1011-Ereignis), $schritte wegen Schrittgrenze ausgelassen, Abweichungen: $abw"
