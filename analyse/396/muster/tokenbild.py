#!/usr/bin/env python3
"""Tokenbild (Thread "396 Wachstumsmuster", 26.11.2026): fasst W-Zeilen von defizit.c zusammen.
W r L<n> H<n> ...: Wort am Rundenende in Tokenform (L=1010, H=100, Z=000; X/Y = einzelne Zelle 1/0 ausserhalb).
Je Runde: Zellen, Tokens je Art, L-Lauf k, Stufenpfad (L = +1, H/Z = -1; Hoechststand und Lage), Anfang und Ende."""
import sys
for zeile in open(sys.argv[1]):
    if not zeile.startswith('W '): continue
    t = zeile.split(); r = int(t[1]); laeufe = [(x[0], int(x[1:])) for x in t[2:]]
    anz = {}; zellen = 0; stufe = 0; hoch = (0, 0); pos = 0
    for a, n in laeufe:
        anz[a] = anz.get(a, 0) + n; zellen += n * {'L': 4, 'H': 3, 'Z': 3}.get(a, 1); pos += n
        if a == 'L':
            stufe += n
            if stufe > hoch[0]: hoch = (stufe, pos)
        elif a in 'HZ': stufe -= n
    k = laeufe[0][1] if laeufe and laeufe[0][0] == 'L' else 0
    print(f'R {r}: Zellen {zellen}, Tokens {sum(anz.values())} {dict(sorted(anz.items()))}, L-Lauf k={k}, '
          f'Stufe hoechstens {hoch[0]} bei Token {hoch[1]}, am Ende {stufe}, Laeufe {len(laeufe)}')
    print('  Anfang:', ' '.join(f'{a}{n}' for a, n in laeufe[:40]))
    print('  Ende:  ', ' '.join(f'{a}{n}' for a, n in laeufe[-40:]))
