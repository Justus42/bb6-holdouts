#!/usr/bin/env python3
"""Punkt 4, Diagnose: Warum findet ctl_fest.py mit festem rechten Automaten "nullen" nichts?

1. Kuerzester abstrakter Weg vom Start zum Halt, wenn der linke Automat nichts weiss (nL = 1). Abstrakte
   Konfiguration = (Zustand, gelesenes Bit, rechter Zustand q), Uebergaenge wie in ctl_sat.py.
2. Welche (Zustand, Bit, q) kommen im echten Lauf ab Leerband ueberhaupt vor (q aus dem ganzen rechten Band).
3. Erste Stelle des abstrakten Wegs, die im echten Lauf nie vorkommt.

Aufruf: python3 ctl_diagnose.py <TM> <schritte> [kein11|nullen]   (Vorgabe nullen)
"""
import sys, os, re
from collections import deque
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'invarianten'))
from ctl_fest import FEST
from ctl_sat import parse_tm

Z = 'ABCDEF'

def abstrakter_weg(tm, dR):
    nR = len(dR)
    start = (0, 0, 0); par = {start: None}; Q = deque([start]); ziel = None
    while Q:
        x = Q.popleft(); s, a, q = x
        t = tm[(s, a)]
        if t is None: ziel = x; break
        b, d, s2 = t
        if d == 'R':
            nach = [(s2, a2, q2) for a2 in range(2) for q2 in range(nR) if dR[q2][a2] == q]
        else:
            nach = [(s2, a2, dR[q][b]) for a2 in range(2)]
        for y in nach:
            if y not in par: par[y] = x; Q.append(y)
    weg = []
    while ziel is not None: weg.append(ziel); ziel = par[ziel]
    return weg[::-1]

def rechter_zustand(R, dR):
    q = 0
    for c in reversed(R):   # vom leeren Ende zum Kopf
        q = dR[q][c]
    return q

def beobachtet(tm, dR, N):
    W = 1 << 20; t = bytearray(W); h = W // 2; s = 0; hi = h + 1
    obs = {}
    for n in range(N):
        a = t[h]
        q = rechter_zustand(t[h+1:hi+1], dR)
        obs[(s, a, q)] = obs.get((s, a, q), 0) + 1
        x = tm[(s, a)]
        if x is None: break
        b, d, s2 = x
        t[h] = b; h += 1 if d == 'R' else -1; s = s2; hi = max(hi, h + 1)
    return obs

def main():
    tmstr, N = sys.argv[1], int(sys.argv[2])
    art = sys.argv[3] if len(sys.argv) > 3 else 'nullen'
    tm, nS = parse_tm(tmstr); dR = FEST[art]
    weg = abstrakter_weg(tm, dR)
    obs = beobachtet(tm, dR, N)
    print(f'{tmstr}, rechter Automat "{art}", linker Automat trivial (nL=1)')
    print(f'Beobachtete (Zustand, Bit, q) im echten Lauf, {N} Schritte ab Leerband:')
    for k in sorted(obs): print(f'   {Z[k[0]]}{k[1]} q={k[2]}: {obs[k]}')
    print('Kuerzester abstrakter Weg zum Halt (* = kommt im echten Lauf nie vor):')
    erst = None
    for i, (s, a, q) in enumerate(weg):
        neu = (s, a, q) not in obs
        if neu and erst is None: erst = i
        print(f'   {i:2d}: {Z[s]}{a} q={q}' + ('  *' if neu else ''))
    if erst is not None:
        print(f'Erste nie beobachtete Stelle: Schritt {erst} ({Z[weg[erst][0]]}{weg[erst][1]} q={weg[erst][2]}), '
              f'davor {Z[weg[erst-1][0]]}{weg[erst-1][1]} q={weg[erst-1][2]}')

if __name__ == '__main__':
    main()
