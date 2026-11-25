#!/bin/bash
# Positiv- und Negativkontrollen fuer Weg 2 (ctl_sat.py + ctl_pruefer.py). Ausgabe nach stdout.
set -u
P1=1RB0RC_1LC1RD_1RA1LE_1LA0RD_0LE1RF_1LB---   # cryptids, CtlCert 3x2
P2=1RB0RC_1LC0LD_1RA1RC_1RA1LE_0LB1RE_---1RA   # cryptids, CtlCert 1x3
H4=1RB1LB_1LA0LC_---1LD_1RD0RA                 # BB(4)-Champion, haelt nach 107 Schritten
H5=1RB1LC_1RC1RB_1RD0LE_1LA1LD_---0LA          # BB(5)-Champion, haelt nach 47.176.870 Schritten
echo "== Positivkontrollen: kleinste Groesse mit Zertifikat, danach unabhaengiger Pruefer =="
for M in $P1 $P2; do
  for s in 2 3 4 5 6; do
    gef=0
    for nL in $(seq 1 $((s-1))); do nR=$((s-nL))
      out=$(python3 ctl_sat.py $M $nL $nR A --aus zertifikate/pos_${M:0:12}.json 2>/dev/null | head -1); echo "$out"
      case "$out" in *ergebnis=SAT*) gef=1; break;; esac
    done
    [ $gef = 1 ] && break
  done
  python3 ctl_pruefer.py zertifikate/pos_${M:0:12}.json 1000000
done
echo "== Negativkontrolle 1: haltende Maschinen, kein Zertifikat bis 6x6 erlaubt =="
for M in $H4 $H5; do
  n=0; sat=0
  for nL in $(seq 1 6); do for nR in $(seq 1 6); do
    out=$(python3 ctl_sat.py $M $nL $nR A 2>/dev/null | head -1); n=$((n+1))
    case "$out" in *ergebnis=SAT*) sat=$((sat+1)); echo "FEHLER: $out";; esac
  done; done
  echo "$M: $n Groessen, $sat mit Zertifikat (erwartet 0)"
done
echo "== Negativkontrolle 2: Symmetriebrechung aendert kein Ergebnis (bis 4x4, mit/ohne) =="
for M in $P1 $P2 $H4 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC; do
  diff=0
  for nL in 1 2 3 4; do for nR in 1 2 3 4; do
    a=$(python3 ctl_sat.py $M $nL $nR A 2>/dev/null | head -1 | sed 's/.*ergebnis=//')
    b=$(python3 ctl_sat.py $M $nL $nR A --ohne-sb 2>/dev/null | head -1 | sed 's/.*ergebnis=//')
    [ "$a" != "$b" ] && { diff=$((diff+1)); echo "ABWEICHUNG $M $nL $nR: $a / $b"; }
  done; done
  echo "$M: 16 Groessen, $diff Abweichungen"
done
