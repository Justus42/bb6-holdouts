#!/usr/bin/env python3
"""Auswertung A (Thread "396 Wachstumsmuster", 26.11.2026) der Ausgabe von defizit.c (ZEILEN=1 APRE=1 PRUEF=1).

Fragen:
 1. Anfangsfenster: Die ersten m Zellen nach dem L-Lauf (m = 8, 16, ..., 320). Kleinste Periode P(m) auf der
    zweiten Haelfte der Runden (nur P <= halbe Spanne, also mindestens zwei volle Wiederholungen), und ab welcher
    Runde die Folge mit P(m) periodisch ist. Verfahren: Kandidaten P aus den frueheren Vorkommen des letzten Werts,
    jeweils ganz geprueft (anders als zweit.c, das die Rand-Funktion von Knuth-Morris-Pratt benutzt).
 2. Wiederholungen des Anfangsfensters (m = 256, 320) und des Endfensters (letzte M Zellen) ab Runde VON.
 3. L-Lauf k gegen r/2, Junk-Ereignisse (J), Halt.
Aufruf: auswertung.py <datei> [von]
"""
import sys, collections

def lies(pfad):
    A = {}; Z = {}; J = []; sonst = []
    with open(pfad) as f:
        for zeile in f:
            t = zeile.split()
            if not t: continue
            if t[0] == 'A': A[int(t[1])] = t[2]
            elif t[0] == 'Z': Z[int(t[1])] = (int(t[2]), int(t[3]), t[4], int(t[5]))
            elif t[0] == 'J': J.append(tuple(int(x) for x in t[1:]))
            elif t[0] in ('HALT', 'ENDE'): sonst.append(zeile.strip())
    return A, Z, J, sonst

def periode(folge):
    """kleinste P <= len/2 mit folge[i] == folge[i+P] fuer alle i, sonst None"""
    n = len(folge); letzt = folge[-1]
    for P in range(1, n // 2 + 1):
        if folge[n - 1 - P] != letzt: continue
        if all(folge[i] == folge[i + P] for i in range(n - P)): return P
    return None

def main():
    A, Z, J, sonst = lies(sys.argv[1])
    von = int(sys.argv[2]) if len(sys.argv) > 2 else 194647
    runden = sorted(A); R = runden[-1]
    print(f'Runden mit A-Zeile: {runden[0]} bis {R} ({len(runden)})')
    for s in sonst: print(s)
    print(f'Junk-Ereignisse (J runde stelle abstand_vom_ende): {len(J)}')
    for j in J: print('  J', *j)
    abw = collections.Counter(Z[r][1] - r // 2 for r in Z)
    print('k - floor(r/2):', dict(abw.most_common(5)))
    # 1. Perioden der Anfangsfenster
    halb = [r for r in runden if r > R // 2]
    if halb != list(range(halb[0], R + 1)): print('WARNUNG: Runden nicht lueckenlos')
    print(f'Perioden der Anfangsfenster auf den Runden {halb[0]}..{R}:')
    for m in range(8, 4 * len(A[R]) + 1, 8):
        h = m // 4
        folge = [A[r][:h] for r in halb]
        P = periode(folge)
        if P is None:
            print(f'  m={m:3d}: keine Periode <= {len(folge)//2}, verschiedene Fenster {len(set(folge))}')
            continue
        # Beginn der Periodizitaet ueber alle Runden
        alle = [A[r][:h] for r in runden]
        i = len(alle) - 1 - P
        while i >= 0 and alle[i] == alle[i + P]: i -= 1
        print(f'  m={m:3d}: Periode {P} (2er-Potenz: {P & (P-1) == 0}), periodisch ab Runde {runden[i+1]}')
    # 2. Wiederholungen ab Runde von
    for name, folge in (('Anfang 256', [(r, A[r][:64]) for r in runden if r >= von]),
                        ('Anfang 320', [(r, A[r]) for r in runden if r >= von]),
                        ('Ende M', [(r, Z[r][2]) for r in sorted(Z) if r >= von])):
        letzt = {}; abst = collections.Counter()
        for r, w in folge:
            if w in letzt: abst[r - letzt[w]] += 1
            letzt[w] = r
        print(f'{name} ab Runde {von}: {len(folge)} Runden, {len(letzt)} verschieden, Wiederholungen {sum(abst.values())}, '
              f'haeufigste Abstaende {abst.most_common(5)}')

main()
