#!/bin/bash
# Kontrollen fuer analyse/133_581.md (rund 4 Minuten ohne den 581-Lauf, mit --voll rund 2,5 Minuten mehr).
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
echo "== Portierung ohne Spruenge gegen direkte Simulation (Besuche und Schrittzahlen)"
python3 port_visits.py C 3000000 100000 --ohne-sprung > /tmp/port_vis0.txt 2>/dev/null
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis0.txt; echo "rc=$? (erwartet 0)"
echo "== Negativkontrolle 4: Schrittzahl nach einem Sprung um 1 erhoeht"
awk '/J$/ && !d {$4=$4+1; d=1} {print}' /tmp/port_vis.txt > /tmp/port_vis_s.txt
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis_s.txt; echo "rc=$? (erwartet 1)"
echo "== Negativkontrolle 5: Sprungformel verfaelscht (15V -> 16V)"
mkdir -p /tmp/nk133 && sed 's/tot = 15 \* V/tot = 16 * V/' pr76_port.py > /tmp/nk133/pr76_port.py && cp port_visits.py /tmp/nk133/
grep -c "tot = 16 \* V" /tmp/nk133/pr76_port.py
(cd /tmp/nk133 && python3 port_visits.py C 3000000 100000 > /tmp/port_vis_f.txt 2>/dev/null)
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis_f.txt; echo "rc=$? (erwartet 1)"
echo "== Negativkontrolle 3: zwei Besuche vertauscht"
awk 'NR==500{a=$0;next} NR==501{print;print a;next}{print}' /tmp/port_vis.txt > /tmp/port_vis_swap.txt
python3 abgleich.py /tmp/direkt_vis.txt /tmp/port_vis_swap.txt; echo "rc=$? (erwartet 1)"
if [ "${1:-}" = "--voll" ]; then
  echo "== Positivkontrolle: 581 ab A, erwartet HALT in Runde 19026768 (PR 76) und"
  echo "   853177647932005270554892218084645935472995035642746848454477793277027802995098762076895667304703808111420498351739937140047615589683 Schritte (bbe, mit Halteuebergang)"
  python3 pr76_port.py A 33554432 | tee /tmp/k581.txt
  grep -q "Runde 19026768 " /tmp/k581.txt && grep -q ": 853177647932005270554892218084645935472995035642746848454477793277027802995098762076895667304703808111420498351739937140047615589683$" /tmp/k581.txt && echo "Positivkontrolle OK" || { echo "Positivkontrolle FEHLER"; exit 1; }
fi
