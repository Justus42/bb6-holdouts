#!/usr/bin/env python3
# Testfaelle fuer die Kontrollen (Thread "Familie Besuchsgesetz"): die 5 Positivkontrollen gespiegelt, mit
# umbenannten Zustaenden (B..F permutiert, A bleibt Start) und beides; dazu alle Einzel-Mutationen von 396
# (jeder Uebergang durch jeden anderen ersetzt), um Faelle "Gesetz ja, Rundenform nein" zu finden.
# Aufruf: testfaelle.py <holdouts.txt> umbenannt|mutanten
import sys, random
ms = [l.strip() for l in open(sys.argv[1])]
def zer(s):
    return [[t[:3], t[3:]] for t in s.split('_')]
def zus(T):
    return '_'.join(a + b for a, b in T)
def spiegel(s):
    return zus([[t if t[2] == '-' else t[0] + ('L' if t[1] == 'R' else 'R') + t[2] for t in z] for z in zer(s)])
def umbenennen(s, perm):  # perm: Liste, neuer Name von Zustand i = perm[i]
    T = zer(s); neu = [None] * 6
    for i in range(6):
        neu[perm[i]] = [t if t[2] == '-' else t[:2] + 'ABCDEF'[perm[ord(t[2]) - 65]] for t in T[i]]
    return zus(neu)
if sys.argv[2] == 'umbenannt':
    random.seed(1125)
    for n in (88, 312, 396, 449, 587):
        s = ms[n - 1]
        p = [0] + random.sample(range(1, 6), 5)
        print(f'{s}\t{n} original')
        print(f'{spiegel(s)}\t{n} gespiegelt')
        print(f'{umbenennen(s, p)}\t{n} umbenannt {"".join("ABCDEF"[x] for x in p)}')
        print(f'{spiegel(umbenennen(s, p))}\t{n} gespiegelt+umbenannt {"".join("ABCDEF"[x] for x in p)}')
elif sys.argv[2] == 'mutanten':
    s = ms[395]; T = zer(s)
    alle = [w + d + q for w in '01' for d in 'LR' for q in 'ABCDEF']
    for i in range(6):
        for b in range(2):
            if T[i][b][2] == '-': continue
            for t in alle:
                if t == T[i][b]: continue
                U = [list(z) for z in T]; U[i][b] = t
                print(f'{zus(U)}\t396 {"ABCDEF"[i]}{b}={t}')
if sys.argv[2] == 'andererstart':
    # gleiche Tabelle, Start in einem anderen Zustand X (X wird zu A umbenannt, A zu X)
    for n in (88, 312, 396, 449, 587):
        s = ms[n - 1]
        for X in range(1, 6):
            p = list(range(6)); p[0], p[X] = X, 0
            print(f'{umbenennen(s, p)}\t{n} Start {"ABCDEF"[X]}')
