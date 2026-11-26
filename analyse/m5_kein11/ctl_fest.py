#!/usr/bin/env python3
"""M5, Punkt 4: CTL-Suche mit FESTEM rechten Automaten (analyse/invarianten/ctl_sat.py, Semantik unveraendert).

Der rechte DFA liest wie in ctl_sat.py die Zellen strikt rechts vom Kopf, vom leeren Ende zum Kopf, Start 0.
Er wird hier nicht gesucht, sondern fest vorgegeben; gesucht werden nur linker DFA (nL Zustaende, mit
Symmetriebrechung wie in ctl_sat.py) und Annahmemenge. Ein gefundenes Zertifikat hat dasselbe Format wie bei
ctl_sat.py und wird mit dem unabhaengigen Pruefer analyse/invarianten/ctl_pruefer.py geprueft.

Feste rechte Automaten:
  kein11 (3 Zustaende): 0 = zuletzt 0 (oder noch nichts), 1 = zuletzt 1, 2 = "11" gesehen (Senke).
  nullen (8 Zustaende): 0 = nur Nullen (leeres Ende), 1 = zuletzt 1, 2/3/4 = 1 dann 1/2/3 Nullen,
                        5 = 1 dann >= 4 Nullen, 6 = "11" gesehen (Senke), 7 = ">= 4 Nullen zwischen zwei Einsen" (Senke).
Welche rechten Zustaende erlaubt sind, entscheidet wie immer die Annahmemenge (der Loeser).

Aufruf: python3 ctl_fest.py <TM> <kein11|nullen|json:zertifikat.json> <nL> [Startzustand] [--aus datei.json]
"""
import sys, os, json, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'invarianten'))
from ctl_sat import Enc, parse_tm
from pysat.solvers import Solver

FEST = {
    'kein11': [[0, 1], [0, 2], [2, 2]],
    'nullen': [[0, 1], [2, 6], [3, 1], [4, 1], [5, 1], [5, 7], [6, 6], [7, 7]],
}

class EncFest(Enc):
    def __init__(self, tm, nS, nL, dRfest, start):
        super().__init__(tm, nS, nL, len(dRfest), start, sb=True)
        self.dRfest = dRfest
    def dfa(self, name, n):
        if name != 'R':
            return super().dfa(name, n)
        for q in range(n):
            for a in range(2):
                for r in range(n):
                    self.cl.append([self.v('R', q, a, r)] if self.dRfest[q][a] == r else [-self.v('R', q, a, r)])

def suche(tmstr, art, nL, start=0, solver='cadical153'):
    tm, nS = parse_tm(tmstr)
    dR = FEST[art] if art in FEST else json.load(open(art.split(':', 1)[1]))['dR']   # 'json:<zertifikat>'
    e = EncFest(tm, nS, nL, dR, start)
    cl = e.baue()
    with Solver(name=solver, bootstrap_with=cl) as S:
        if not S.solve():
            return None, len(cl)
        m = set(x for x in S.get_model() if x > 0)
    nR = len(dR)
    dL = [[next(r for r in range(nL) if e.v('L', p, a, r) in m) for a in range(2)] for p in range(nL)]
    dRm = [[next(r for r in range(nR) if e.v('R', q, a, r) in m) for a in range(2)] for q in range(nR)]
    assert dRm == dR
    acc = sorted([(p, s, a, q) for p in range(nL) for s in range(nS) for a in range(2) for q in range(nR)
                  if e.v('X', p, s, a, q) in m])
    return {'tm': tmstr, 'start': start, 'nL': nL, 'nR': nR, 'dL': dL, 'dR': dR, 'acc': acc}, len(cl)

if __name__ == '__main__':
    tmstr, art, nL = sys.argv[1], sys.argv[2], int(sys.argv[3])
    start = ord(sys.argv[4]) - 65 if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else 0
    aus = sys.argv[sys.argv.index('--aus') + 1] if '--aus' in sys.argv else None
    t = time.time()
    z, ncl = suche(tmstr, art, nL, start)
    print(f'{tmstr} start={chr(65+start)} rechts={art} nL={nL} klauseln={ncl} zeit={time.time()-t:.1f}s '
          f'ergebnis={"SAT" if z else "UNSAT"}', flush=True)
    if z:
        if aus:
            json.dump(z, open(aus, 'w'), indent=1)
        print(json.dumps(z), flush=True)
