#!/usr/bin/env python3
"""Punkt 5: In welchen linken Umgebungen liest M5-D eine 0? Wertet die UMG-Zeilen von kein11.c aus.

Eingabe: Ausgabe von  kein11 <TM> R <N> --umgebung <Z> 0   (Z = der Zustand, der in dieser Maschine M5-D ist).
UMG-Zeile: 16 Zellen links vom Kopf, [Kopfzelle], 8 Zellen rechts, Anzahl.

Einteilung der linken 16 Zellen:
  P-Lauf    : Teilwort von (11111010)^unendlich (Periode von P = 11111010, also auch W = 11110101 usw.)
  P+Wort    : die Zellen -16..-9 sind ein Teilwort von P^unendlich, die letzten 8 nicht (Kopf mitten im Umschreiben
              eines 8er-Worts, z. B. im Lauf von A ueber Q oder von C ueber W)
  Bandende  : beginnt mit mindestens einer 0 und enthaelt links davon nur Nullen (Kopf nahe am linken Ende)
  sonst     : alles andere (Zaehlerbereich, Wenden)
Aufruf: python3 umgebung.py <lauf.txt> [--alle]
"""
import sys
from collections import Counter

P = '11111010'
PER = set((P * 4)[i:i+16] for i in range(8))
PER8 = set((P * 4)[i:i+8] for i in range(8))

def art(links):
    if links in PER:
        return 'P-Lauf'
    if links[:8] in PER8:
        return 'P+Wort'
    if links.startswith('0'):
        return 'Bandende'
    return 'sonst'

def main():
    f = sys.argv[1]
    L = [l.split() for l in open(f) if l.startswith('UMG ')]
    summe = sum(int(c) for _, w, c in L)
    rechts1 = sum(int(c) for _, w, c in L if w[19] == '1')
    print(f'{f}: {summe} Mal liest M5-D eine 0; {len(L)} verschiedene Fenster (16 links, Kopf, 8 rechts); '
          f'rechter Nachbar = 1: {rechts1} Mal')
    k = Counter(); fenster = Counter()
    for _, w, c in L:
        k[art(w[:16])] += int(c); fenster[art(w[:16])] += 1
    for a in ('P-Lauf', 'P+Wort', 'Bandende', 'sonst'):
        print(f'  {a:9s}: {k[a]:>12d} Mal ({100*k[a]/summe:.4f} %), {fenster[a]} Fenster')
    for a in ('P-Lauf', 'P+Wort'):
        print(f'  {a} nach den letzten 8 Zellen links und den 8 Zellen rechts:')
        c8 = Counter()
        for _, w, c in L:
            if art(w[:16]) == a: c8[(w[8:16], w[19:])] += int(c)
        for (x, r), n in sorted(c8.items(), key=lambda t: -t[1])[:20]:
            print(f'     ...{x} D> 0 {r}... : {n}')
        if len(c8) > 20: print(f'     ({len(c8) - 20} weitere, zusammen {sum(sorted(c8.values(), reverse=True)[20:])})')
    print('  sonst: linke 16 Zellen, Kopf, rechte 8 Zellen (haeufigste 40; --alle fuer alle):')
    rest = sorted(((int(c), w) for _, w, c in L if art(w[:16]) == 'sonst'), reverse=True)
    for n, w in (rest if '--alle' in sys.argv else rest[:40]):
        print(f'     {w[:16]} D> {w[17]} {w[19:]}  {n}')
    c8 = Counter()
    for n, w in rest: c8[w[8:16]] += n
    print(f'  sonst, nach den letzten 8 Zellen links ({len(c8)} verschiedene):')
    for x, n in sorted(c8.items(), key=lambda t: -t[1]):
        print(f'     ...{x} D> 0 : {n}')

if __name__ == '__main__':
    main()
