#!/bin/bash
# Kontrollen fuer ctl_fest.py (fester rechter Automat). Aufruf aus analyse/m5_kein11/.
set -u
I=../invarianten
P1=1RB0RC_1LC1RD_1RA1LE_1LA0RD_0LE1RF_1LB---   # cryptids, CtlCert 3x2 (findet ctl_sat.py bei nL=3, nR=2)
H4=1RB1LB_1LA0LC_---1LD_1RD0RA                 # BB(4)-Champion, haelt
H5=1RB1LC_1RC1RB_1RD0LE_1LA1LD_---0LA          # BB(5)-Champion, haelt
mkdir -p zertifikate
echo "== Positivkontrolle: rechter DFA aus dem ctl_sat-Zertifikat von P1 fest vorgegeben, nL=3 muss SAT sein"
python3 $I/ctl_sat.py $P1 3 2 A --aus zertifikate/kontrolle_P1_frei.json | sed -n 1p
python3 ctl_fest.py $P1 json:zertifikate/kontrolle_P1_frei.json 3 A --aus zertifikate/kontrolle_P1_fest.json | sed -n 1p
python3 $I/ctl_pruefer.py zertifikate/kontrolle_P1_fest.json 1000000
echo "== Positivkontrolle 2: dieselbe Vorgabe, nL=2 muss UNSAT sein (ctl_sat findet bis 2x2 nichts)"
python3 ctl_fest.py $P1 json:zertifikate/kontrolle_P1_frei.json 2 A | sed -n 1p
echo "== Negativkontrolle: haltende Maschinen, beide festen rechten DFAs, nL=1..8, erwartet nur UNSAT"
for M in $H4 $H5; do for art in kein11 nullen; do
  sat=0
  for nL in 1 2 3 4 5 6 7 8; do
    out=$(python3 ctl_fest.py $M $art $nL A | sed -n 1p)
    case "$out" in *ergebnis=SAT*) sat=$((sat+1)); echo "FEHLER: $out";; esac
  done
  echo "$M $art: 8 Groessen, $sat mit Zertifikat (erwartet 0)"
done; done
