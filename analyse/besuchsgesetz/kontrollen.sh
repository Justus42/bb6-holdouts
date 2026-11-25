#!/bin/bash
# Kontrollen fuer die Familien-Suche (Thread "Familie Besuchsgesetz", 25.11.2026). Laufzeit lokal ca. 1 min.
# Aufruf aus dem Repo-Wurzelverzeichnis: bash analyse/besuchsgesetz/kontrollen.sh
set -u
D=analyse/besuchsgesetz; T=$(mktemp -d); fail=0
gcc -O2 -w -o $T/suche_b $D/suche_b.c || exit 1
ok(){ echo "OK   $1"; }; nein(){ echo "FEHL $1"; fail=1; }
# 1. Alle 608: A und B zeilengleich (ohne die Zaehlspalte), und gleich den gespeicherten Ergebnissen
python3 -I $D/suche_a.py data/BB6_holdouts_608.txt 12 > $T/a.tsv
$T/suche_b data/BB6_holdouts_608.txt 12 > $T/b.tsv 2>/dev/null
diff <(cut -f1-5,7- $T/a.tsv) <(cut -f1-5,7- $T/b.tsv) >/dev/null && ok "A = B auf 608 ($(wc -l < $T/a.tsv) Treffer)" || nein "A != B"
cmp -s $T/a.tsv $D/ergebnis_a.tsv && cmp -s $T/b.tsv $D/ergebnis_b.tsv && ok "gleich ergebnis_a/b.tsv" || nein "weicht von gespeicherten Ergebnissen ab"
# 2. Positivkontrolle
for n in 88 312 449 396 587; do grep -q "^$n	" $T/a.tsv && grep -q "^$n	" $T/b.tsv && ok "Positivkontrolle $n gefunden" || nein "Positivkontrolle $n fehlt"; done
# 3. Spiegelung/Umbenennung: 5 Kontrollen x 4 Schreibweisen = 20 Faelle, alle gefunden, A = B
python3 -I $D/testfaelle.py data/BB6_holdouts_608.txt umbenannt | cut -f1 > $T/u.txt
python3 -I $D/suche_a.py $T/u.txt 12 > $T/ua; $T/suche_b $T/u.txt 12 > $T/ub 2>/dev/null
[ "$(cut -f1 $T/ua | sort -un | wc -l)" = 20 ] && diff <(cut -f1-5,7- $T/ua) <(cut -f1-5,7- $T/ub) >/dev/null && ok "20 gespiegelte/umbenannte Faelle gefunden, A = B" || nein "Umbenennung/Spiegelung"
# 4. Negativkontrollen (muessen anschlagen)
[ "$(FEHLER=1 python3 -I $D/suche_a.py $T/u.txt 12 | wc -l)" = 0 ] && [ "$(FEHLER=1 $T/suche_b $T/u.txt 12 2>/dev/null | wc -l)" = 0 ] && ok "FEHLER=1 (1010-Regel falsch): nichts gefunden" || nein "FEHLER=1 schlaegt nicht an"
[ "$(FEHLER=2 python3 -I $D/suche_a.py $T/u.txt 12 | wc -l)" = 10 ] && [ "$(FEHLER=2 $T/suche_b $T/u.txt 12 2>/dev/null | wc -l)" = 10 ] && ok "FEHLER=2 (ohne Spiegelung): nur 10 von 20" || nein "FEHLER=2 schlaegt nicht an"
[ "$(FEHLER=3 python3 -I $D/suche_a.py $T/u.txt 12 | grep -c 'u=')" = 0 ] && [ "$(FEHLER=3 $T/suche_b $T/u.txt 12 2>/dev/null | grep -c 'u=')" = 0 ] && ok "FEHLER=3 (falsche Rundenform): keine Rundenform" || nein "FEHLER=3 schlaegt nicht an"
# 5. Direkte Simulation ab Leerband: Woerter der ersten 27 Runden bei allen Mitgliedern gleich (direkt.c aus analyse/396)
gcc -O2 -o $T/direkt analyse/396/direkt.c
for n in $(cut -f1 $T/a.tsv); do $T/direkt $(sed -n ${n}p data/BB6_holdouts_608.txt) 3000000000 27 | grep '^R ' | sed 's/  schritt=.*//' > $T/d_$n; done
for n in $(cut -f1 $T/a.tsv); do cmp -s $T/d_396 $T/d_$n && ok "$n: Woerter der Runden 0..27 gleich 396 ($(wc -l < $T/d_$n) Zeilen)" || nein "$n: Woerter weichen ab"; done
rm -rf $T; exit $fail
