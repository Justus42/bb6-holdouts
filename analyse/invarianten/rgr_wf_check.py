#!/usr/bin/env python3
"""Prueft die von Hand uebersetzte busycoq-Invariante WF (RGRv1.v) im S0-Koordinatensystem:
  W(a,b,c,d) := b>=1 & c>=1 & d>=0 & a>=0 & ((c<=b & a+b>=c+d+4) | (c>b & a+b>=c+d+6))
(1) mit Z3 als SMT-Frage (Init, Erhalt je Regel, kein schlechter Zustand),
(2) unabhaengig ohne Z3 durch Aufzaehlung aller Zustaende mit Werten < N.
Zweck: zeigt, dass die CHC-Formulierung in chc_rgr.py stimmt und eine Invariante hat;
das Problem der Loeser ist also die Suche, nicht das Modell."""
import sys, z3
def W(a,b,c,d, And=lambda *x: all(x), Or=lambda *x: any(x)):
    return And(b>=1, c>=1, d>=0, a>=0, Or(And(c<=b, a+b>=c+d+4), And(c>b, a+b>=c+d+6)))
def schlecht(a,b,c,d, And=lambda *x: all(x), Or=lambda *x: any(x), Not=lambda x: not x):
    return Not(Or(And(b>=2,c>=2), And(b>=1,c==1), And(a>=4,b==1,c>=2)))
regeln = [  # (Vorbedingung, Nachfolger) in S0-Koordinaten
  ('Inc', lambda a,b,c,d,And: And(b>=2,c>=2), lambda a,b,c,d: (a+1,b-1,c-1,d+1)),
  ('ROv', lambda a,b,c,d,And: And(b>=1,c==1), lambda a,b,c,d: (a+2,b,d+1,0)),
  ('LOv', lambda a,b,c,d,And: And(a>=4,b==1,c>=2), lambda a,b,c,d: (3,a-3,c,d+1)),
]
a,b,c,d = z3.Ints('a b c d')
zA = dict(And=z3.And, Or=z3.Or)
s = z3.Solver(); s.add(z3.Not(W(4,5,2,1,**zA))); print('Z3 Init:', 'OK' if s.check()==z3.unsat else 'FEHLER')
for name, pre, post in regeln:
    s = z3.Solver(); s.add(W(a,b,c,d,**zA), pre(a,b,c,d,z3.And), z3.Not(W(*post(a,b,c,d),**zA)))
    print(f'Z3 Erhalt {name}:', 'OK' if s.check()==z3.unsat else f'FEHLER {s.model()}')
s = z3.Solver(); s.add(W(a,b,c,d,**zA), schlecht(a,b,c,d,Not=z3.Not,**zA)); print('Z3 kein schlechter Zustand:', 'OK' if s.check()==z3.unsat else 'FEHLER')
N = int(sys.argv[1]) if len(sys.argv)>1 else 40
fehl = 0; n = 0
assert W(4,5,2,1)
for A in range(N):
  for B in range(N):
    for C in range(N):
      for D in range(N):
        if not W(A,B,C,D): continue
        n += 1
        if schlecht(A,B,C,D): fehl += 1
        for name, pre, post in regeln:
            if pre(A,B,C,D,lambda *x: all(x)) and not W(*post(A,B,C,D)): fehl += 1
print(f'Aufzaehlung bis {N}: {n} Zustaende in W, {fehl} Fehler')
