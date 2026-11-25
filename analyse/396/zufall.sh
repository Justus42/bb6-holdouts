#!/bin/bash
# Vergleich runde.c (Zaehler-Verfahren) mit naiv.py (Besuch fuer Besuch) auf Zufalls-Startwoertern, die 1011 und 111 enthalten koennen.
# Aufruf: zufall.sh <anzahl> <runden>; mit FEHLER=1 muss der Vergleich scheitern.
n=$1; R=$2; bad=0; halt111=0; ev=0
for i in $(seq 1 $n); do
  w=$(python3 -c "import random;random.seed($i);L=random.randint(4,24);print('1'+''.join(random.choice('0001') if random.random()<0.7 else random.choice('01') for _ in range(L)))")
  for m in 88 396; do
    a=$(python3 naiv.py $m $R $w | sed 's/0*$//')
    b=$(./runde $m $R $R $w | grep -E '^(R|HALT)' | sed -E 's/^HALT (111|1011) in Runde ([0-9]+).*/HALT \1 Runde \2/' | sed 's/0*$//')
    if [ "$a" != "$b" ]; then bad=$((bad+1)); fi
    echo "$a" | grep -q 'HALT 111' && halt111=$((halt111+1))
  done
  ./runde 396 $R 0 $w | grep -q EREIGNIS && ev=$((ev+1))
done
echo "Woerter $n, Runden $R: Abweichungen $bad, Laeufe mit Halt bei 111: $halt111, Woerter mit 1011-Ereignis (396): $ev"
