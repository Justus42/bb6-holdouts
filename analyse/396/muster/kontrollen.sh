#!/bin/bash
# Kontrollen fuer den Thread "396 Wachstumsmuster" (Workflow lauf_muster, Job kontrollen). Dauer ca. 1 min.
set -u
cd "$(dirname "$0")"
fehler=0; ok(){ echo "OK   $*"; }; nein(){ echo "FEHLER $*"; fehler=1; }
gcc -O2 -Wall -o defizit defizit.c && gcc -O2 -Wall -o runde ../runde.c && g++ -O2 -Wall -o runde_b ../runde_b.cpp \
  && g++ -O2 -Wall -o runde_b_anf runde_b_anf.cpp && gcc -O2 -Wall -o zweit zweit.c || exit 1
# 1. X gegen runde.c (Teil 2): Pruefsummen alle 1000 Runden bis 20000
PRUEF=1 ./defizit 20000 | grep '^H' > k_x.txt; PROTO=1 ./runde 396 20000 | grep '^H' > k_a.txt
cmp -s k_x.txt k_a.txt && [ "$(wc -l < k_x.txt)" = 20 ] && ok "X = runde.c (20 Pruefsummen bis 20000)" || nein "X != runde.c"
# 2. Negativkontrolle: falsche Ziffernregel in X muss abweichen
FEHLER=1 PRUEF=1 ./defizit 3000 | grep '^H' > k_f.txt; PROTO=1 ./runde 396 3000 | grep '^H' > k_a3.txt
cmp -s k_f.txt k_a3.txt && nein "FEHLER=1 nicht erkannt" || ok "Negativkontrolle FEHLER=1 schlaegt an"
# 3. runde_b_anf rechnet wie runde_b (E/H bis 5000)
./runde_b 5000 | grep -E '^(E|H)' > k_b0.txt; ./runde_b_anf 5000 | grep -E '^(E|H)' > k_b1.txt
cmp -s k_b0.txt k_b1.txt && ok "runde_b_anf = runde_b (E/H bis 5000)" || nein "runde_b_anf != runde_b"
# 4. Anfangsfenster und Pruefsummen X gegen B bis 10000
ZEILEN=1 APRE=1 PRUEF=1 M=320 ./defizit 10000 | grep -E '^(A|H)' > k_xa.txt; ANF=1 ./runde_b_anf 10000 | grep -E '^(A|H)' > k_ba.txt
cmp -s k_xa.txt k_ba.txt && ok "A+H X = B bis 10000 ($(wc -l < k_xa.txt) Zeilen)" || nein "A+H X != B"
# 5. Negativkontrolle Vergleich: eine Ziffer in einer A-Zeile geaendert
sed '5000s/^\(A [0-9]* \)./\1z/' k_ba.txt > k_bz.txt; cmp -s k_xa.txt k_bz.txt && nein "Aenderung nicht erkannt" || ok "Negativkontrolle Vergleich schlaegt an"
# 6. Periodensuche an kuenstlichen Folgen (Periode von m = 4h Zellen ist 2^h)
python3 kuenstlich.py > k_s.txt; STOER=1 python3 kuenstlich.py > k_s2.txt
p1=$(python3 auswertung.py k_s.txt 1 | grep -c 'Periode .* periodisch ab Runde 1$'); p2=$(./zweit k_s.txt | grep -c 'periodisch ab Runde 1$')
python3 auswertung.py k_s.txt 1 | grep 'm= 40'; ./zweit k_s.txt | grep 'm= 40'
[ "$p1" = 5 ] && [ "$p2" = 5 ] && [ "$(python3 auswertung.py k_s.txt 1 | grep -c 'm= 32: Periode 256 ')" = 1 ] && [ "$(./zweit k_s.txt | grep -c 'm= 32: Periode 256,')" = 1 ] \
  && ok "Periodensuche findet 4,16,64,256,1024 (m=8..40), beide Programme" || nein "Periodensuche kuenstlich ($p1/$p2)"
q1=$(python3 auswertung.py k_s2.txt 1 | grep -c 'm= 40: keine'); q2=$(./zweit k_s2.txt | grep -c 'm= 40: keine')
[ "$q1" = 1 ] && [ "$q2" = 1 ] && ok "Negativkontrolle Stoerung: m=40 ohne Periode, beide Programme" || nein "Stoerung nicht erkannt ($q1/$q2)"
# 7. echte Daten bis 20000: beide Periodensuchen gleich
ZEILEN=1 APRE=1 M=320 ./defizit 20000 > k_x20.txt
python3 auswertung.py k_x20.txt 15000 | grep '  m=' | sed 's/ (2er-Potenz: [A-Za-z]*)//;s/, verschiedene Fenster [0-9]*//' > k_p1.txt
./zweit k_x20.txt | grep '  m=' > k_p2.txt
diff <(sed 's/,//' k_p1.txt) <(sed 's/,//' k_p2.txt) > /dev/null && ok "Perioden bis 20000: auswertung.py = zweit.c" || { nein "Perioden verschieden"; diff k_p1.txt k_p2.txt | head; }
rm -f k_*.txt defizit runde runde_b runde_b_anf zweit
[ $fehler = 0 ] && echo "ALLE KONTROLLEN OK" || { echo "KONTROLLEN MIT FEHLERN"; exit 1; }
