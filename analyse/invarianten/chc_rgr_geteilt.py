#!/usr/bin/env python3
"""Weg 1, Hilfsversuch: wie chc_rgr.py, aber der Zustandsraum ist von Hand in zwei Praedikate geteilt
(P: n3 <= n2, Q: n3 > n2 in S0-Koordinaten c <= b bzw. c > b). Das ist ein menschlicher Hinweis
(die Fallunterscheidung aus busycoqs WF), keine eigenstaendige Leistung des Loesers."""
import sys, time, z3
fp = z3.Fixedpoint(); fp.set(engine='spacer')
I = z3.IntSort()
P = z3.Function('P', I, I, I, I, z3.BoolSort()); Q = z3.Function('Q', I, I, I, I, z3.BoolSort())
Bad = z3.Function('Bad', z3.BoolSort())
fp.register_relation(P, Q, Bad)
a, b, c, d = z3.Ints('a b c d'); fp.declare_var(a, b, c, d)
nn = z3.And(a >= 0, b >= 0, c >= 0, d >= 0)
def ziel(A, B, C, D):  # Nachfolger in P oder Q je nach Fall
    return [(P(A, B, C, D), C <= B), (Q(A, B, C, D), C > B)]
fp.rule(P(4, 5, 2, 1))
for R in (P, Q):
    for kopf, bed in ziel(a + 1, b + 1, c + 1, d + 1):
        fp.rule(kopf, [R(a, b + 2, c + 2, d), nn, bed])
    for kopf, bed in ziel(a + 2, b + 1, d + 1, 0):
        fp.rule(kopf, [R(a, b + 1, 1, d), nn, bed])
    for kopf, bed in ziel(3, a + 1, c + 2, d + 1):
        fp.rule(kopf, [R(a + 4, 1, c + 2, d), nn, bed])
    schlecht = z3.Not(z3.Or(z3.And(b >= 2, c >= 2), z3.And(b >= 1, c == 1), z3.And(a >= 4, b == 1, c >= 2)))
    fp.rule(Bad(), [R(a, b, c, d), nn, schlecht])
z3.set_param('timeout', int(sys.argv[1]) * 1000 if len(sys.argv) > 1 else 180000)
t = time.time(); r = fp.query(Bad()); print('geteilt', r, f'{time.time()-t:.1f}s')
if r == z3.unsat:
    print('P:', fp.get_cover_delta(-1, P).sexpr()); print('Q:', fp.get_cover_delta(-1, Q).sexpr())
