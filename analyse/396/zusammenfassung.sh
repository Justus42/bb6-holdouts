#!/bin/bash
# Zusammenfassung eines Protokolls (runde.c PROTO=1 oder runde_b.cpp) fuers Actions-Log.
f=$1
echo "--- Ende";            grep -E '^(ENDE|HALT 111 [0-9]+ [0-9]+$)' "$f" || true
echo "--- letzte Pruefsummen"; grep '^H ' "$f" | tail -n 3 || true
echo "--- 1011-Ereignisse (K): $(grep -c '^K ' "$f" || true)"; grep '^K ' "$f" | head -n 200 || true
echo "--- Bloecke mit 011 (Z): $(grep -c '^Z ' "$f" || true)"; grep '^Z ' "$f" | head -n 200 || true
echo "--- Runden mit 11 im Wort am Rundenende (E): $(grep -c '^E ' "$f" || true)"; grep '^E ' "$f" | head -n 60 || true
echo "... letzte:"; grep '^E ' "$f" | tail -n 20 || true
echo "--- Runden mit 111 im Wort am Rundenende: $(awk '$1=="E" && $4>0' "$f" | wc -l)"; awk '$1=="E" && $4>0' "$f" | head -n 50
echo "--- Wortenden um Ereignisse (W): $(grep -c '^W ' "$f" || true) Zeilen"; grep '^W ' "$f" | head -n 400 || true
