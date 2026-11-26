#!/bin/bash
# Kontrollen fuer analyse/133_581.md (rund 3 Minuten ohne den 581-Lauf, mit --voll rund 2,5 Minuten mehr).
set -u
cd "$(dirname "$0")"
T133=1RB0LC_1LC0RE_1LD1LB_1LA1LD_1RF0RA_---1RE
echo "== Tabelle 133 gegen 581 und gegen den RWLAccHalt-Geschwister"
python3 tabelle.py $T133 1RB1RD_1RC1RB_1LD0RA_1RA0LE_1LF0LC_---1LE
python3 tabelle.py $T133 1RB0LE_1RC1RA_1RD1RC_1LA0RB_1LF0LD_---1LE
echo "== Negativkontrolle Tabelle (ein Feld von 581 geaendert, 0LC -> 0LB): keine Zeile erwartet"
python3 tabelle.py $T133 1RB1RD_1RC1RB_1LD0RA_1RA0LE_1LF0LB_---1LE
gcc -O2 -o /tmp/direkt133 direkt133.c
echo "== Portierung gegen direkte Simulation (Besuche bis Wortlaenge 100.000)"
python3 port_visits.py C 3000000 100000 > /tmp/port_vis.txt 2>/dev/null
/tmp/direkt133 3000000000 > /tmp/direkt_vis.txt 2>/dev/null
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis.txt; echo "rc=$? (erwartet 0)"
echo "== Negativkontrolle 1: Besuche von 581 gegen den direkten Lauf von 133"
python3 port_visits.py A 3000000 100000 > /tmp/port_vis_A.txt 2>/dev/null
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis_A.txt; echo "rc=$? (erwartet 1)"
echo "== Negativkontrolle 2: ein Hash nach Sprung verfaelscht"
python3 -c "
L=open('/tmp/port_vis.txt').read().splitlines()
i=[k for k,l in enumerate(L) if l.endswith(' J')][5]
p=L[i].split(); p[2]=p[2][:-1]+('0' if p[2][-1]!='0' else '1'); L[i]=' '.join(p)
open('/tmp/port_vis_bad.txt','w').write('\n'.join(L)+'\n')"
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis_bad.txt; echo "rc=$? (erwartet 1)"
echo "== Negativkontrolle 3: zwei Besuche vertauscht"
awk 'NR==500{a=$0;next} NR==501{print;print a;next}{print}' /tmp/port_vis.txt > /tmp/port_vis_swap.txt
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis_swap.txt; echo "rc=$? (erwartet 1)"
if [ "${1:-}" = "--voll" ]; then
  echo "== Positivkontrolle: 581 ab A, erwartet HALT in Runde 19026768 (Zahl aus PR 76)"
  python3 pr76_port.py A 33554432
fi
