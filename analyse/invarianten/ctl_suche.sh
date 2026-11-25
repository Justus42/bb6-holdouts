#!/bin/bash
# Durchsucht alle Groessen nL,nR <= MAX (aufsteigend nach nL+nR) fuer eine TM und einen Start.
# Aufruf: ctl_suche.sh <TM> <Start> <MAX> <Zeitlimit_s> <Logdatei>
TM=$1; ST=$2; MAX=$3; TL=$4; LOG=$5
for s in $(seq ${MIN:-2} $((2*MAX))); do
  for nL in $(seq 1 $MAX); do
    nR=$((s-nL)); [ $nR -lt 1 ] && continue; [ $nR -gt $MAX ] && continue
    out=$(timeout $TL python3 ctl_sat.py $TM $nL $nR $ST --aus zertifikate/fund_${ST}_${nL}_${nR}.json 2>&1 | head -1)
    [ -z "$out" ] && out="$TM start=$ST nL=$nL nR=$nR ergebnis=ZEITLIMIT(${TL}s)"
    echo "$out" >> $LOG
    case "$out" in *ergebnis=SAT*) echo "FUND" >> $LOG; exit 0;; esac
  done
done
