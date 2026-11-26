#!/bin/bash
# Punkt 3, Negativkontrollen mit vorgegebenem Startband: beide Programme (vergleich.sh) muessen den Bruch melden.
#   A> 0 0001 (Zustand = M5-A der jeweiligen Maschine; 274 gespiegelt, Seite L): Bruch genau bei Schritt 4.
#   "11" direkt auf der geprueften Seite: Bruch bei Schritt 0.   Gegenprobe A> 0 0101: kein Bruch.
T274=1RB0RE_1LC0RA_0LD1LB_1LA1LF_0LB0RD_0LB---; T318=1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC
T322=1RB1RF_1LC0LF_1RD0LB_0RA1RE_1RD---_0RC0LA; T518=1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---
V=./vergleich.sh
$V vgl $T318 R 20 --start A --band 00001 0
$V vgl $T518 R 20 --start A --band 00001 0
$V vgl $T322 R 20 --start C --band 00001 0
$V vgl $T274 L 20 --start B --band 10000 4
$V vgl $T318 R 20 --start A --band 0011 0
$V vgl $T518 R 20 --start A --band 0011 0
$V vgl $T322 R 20 --start C --band 0011 0
$V vgl $T274 L 20 --start B --band 1100 3
$V vgl $T318 R 20 --start A --band 00101 0
