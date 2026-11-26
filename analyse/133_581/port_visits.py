#!/usr/bin/env python3
"""Protokolliert die Besuche (Zustand A, vorn leer) der PR-76-Portierung als Worthashes, zum Abgleich mit direkt133.c."""
import sys
sys.path.insert(0, '.')
import pr76_port as P

def decode(b, limit):
    out = []  # nearest first
    n = 0
    for x in b:
        if x[0] == 'B':
            out.append(x[1]); n += 1
        else:
            n += len(x[1]) * x[2]
            if n > limit: return None
            for _ in range(x[2]): out.extend(x[1])
        if n > limit: return None
    w = ''.join(map(str, reversed(out))).lstrip('0')
    return w

def h(w):
    x = 1469598103934665603
    for ch in w.encode():
        x ^= ch; x = (x * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return '%016x' % x

start, rounds, limit = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
if '--ohne-sprung' in sys.argv: P.tryJump = lambda b: None
rnd = P.make_round(P.TM581)
c = (True, [], [], start)
for i in range(1, rounds + 1):
    if c[0] and not c[1] and c[3] == 'A':
        w = decode(c[2], limit)
        if w is None: print('ENDE Laenge', file=sys.stderr); break
        print('%d %d %s %d' % (i, len(w), h(w), P.STEPS[0]))
        j0 = P.STAT['jumps']
        s0 = P.STEPS[0]
        c1 = P.atVisit(c)
        if P.STAT['jumps'] > j0:
            w = decode(c1[2], limit)
            if w is None: print('ENDE Laenge', file=sys.stderr); break
            print('%d %d %s %d J' % (i, len(w), h(w), P.STEPS[0]))
        P.STAT['jumps'] = j0  # atVisit wird in round erneut aufgerufen
        P.STEPS[0] = s0
    c = rnd(c)
    if c is None: print('HALT', i); break
