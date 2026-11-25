#!/usr/bin/env python3
"""Weg 2: Suche nach einer Bandsprache-Invariante (zwei DFAs + Annahmemenge, "CTL"-Zertifikat
wie google-deepmind/cryptids BusyBeaver/Calculi/CtlCertificate.lean) per SAT-Loeser.

Semantik (exakt wie ctlCheck in cryptids):
  Abstraktion einer Konfiguration = (dL-Zustand des linken Halbbands, Zustand s, gelesenes Bit a,
  dR-Zustand des rechten Halbbands); beide DFAs lesen vom leeren Ende zum Kopf, Start 0, d(0,0)=0.
  Bedingungen: (0, start, 0, 0) angenommen; jedes angenommene Tupel hat einen definierten,
  nicht haltenden Uebergang, und jeder abstrakte Nachfolger ist wieder angenommen.
  Rechtsbewegung (s,a)->(b,R,s'): fuer alle a',q' mit dR(q',a')=q: (dL(p,b), s', a', q') angenommen.
  Linksbewegung  (s,a)->(b,L,s'): fuer alle a',p' mit dL(p',a')=p: (p', s', a', dR(q,b)) angenommen.

Aufruf: python3 ctl_sat.py <TM> <nL> <nR> [Startzustand A..F] [--aus datei.json]
Ergebnis: SAT (Zertifikat, als JSON gespeichert) oder UNSAT (es gibt keins dieser Groesse,
mit Symmetriebrechung: alle DFA-Zustaende von 0 aus erreichbar, BFS-Nummerierung).
"""
import sys, json, time, itertools
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool

def parse_tm(s):
    zeilen = s.split('_')
    tm = {}
    for q, z in enumerate(zeilen):
        for a in range(2):
            t = z[3*a:3*a+3]
            if t[2] in '-HZ' or t == '---':
                tm[(q, a)] = None
            else:
                tm[(q, a)] = (int(t[0]), t[1], ord(t[2]) - 65)
    return tm, len(zeilen)

class Enc:
    def __init__(self, tm, nS, nL, nR, start, sb=True):
        self.sb = sb
        self.pool = IDPool()
        self.cl = []
        self.tm, self.nS, self.nL, self.nR, self.start = tm, nS, nL, nR, start
    def v(self, *k): return self.pool.id(k)
    def eins(self, lits):
        # genau eins
        self.cl.append(list(lits))
        for x, y in itertools.combinations(lits, 2):
            self.cl.append([-x, -y])
    def dfa(self, name, n):
        for p in range(n):
            for a in range(2):
                self.eins([self.v(name, p, a, r) for r in range(n)])
        self.cl.append([self.v(name, 0, 0, 0)])
        if not self.sb: return
        # Symmetriebrechung (BFS-Nummerierung, Ulyantsev-Stil): Uebergang k = 2p+a.
        # par(j,k): Zustand j (>=1) wird zuerst ueber Uebergang k erreicht.
        T = lambda k, j: self.v(name, k // 2, k % 2, j)
        for j in range(1, n):
            ks = list(range(0, 2 * j))           # nur von Zustaenden < j
            self.eins([self.v(name + 'par', j, k) for k in ks])
            for k in ks:
                P = self.v(name + 'par', j, k)
                self.cl.append([-P, T(k, j)])
                for k2 in range(k):
                    self.cl.append([-P, -T(k2, j)])
            # Eltern monoton: par(j,k) -> par(j+1,k') nur mit k' >= k
            if j + 1 < n:
                for k in ks:
                    for k2 in range(k):
                        self.cl.append([-self.v(name + 'par', j, k), -self.v(name + 'par', j + 1, k2)])
    def baue(self):
        tm, nS, nL, nR = self.tm, self.nS, self.nL, self.nR
        self.dfa('L', nL); self.dfa('R', nR)
        X = lambda p, s, a, q: self.v('X', p, s, a, q)
        L = lambda p, a, r: self.v('L', p, a, r)
        R = lambda q, a, r: self.v('R', q, a, r)
        self.cl.append([X(0, self.start, 0, 0)])
        for p in range(nL):
            for s in range(nS):
                for a in range(2):
                    for q in range(nR):
                        t = tm[(s, a)]
                        if t is None:
                            self.cl.append([-X(p, s, a, q)]); continue
                        b, d, s2 = t
                        if d == 'R':
                            for a2 in range(2):
                                for q2 in range(nR):
                                    for p2 in range(nL):
                                        self.cl.append([-X(p, s, a, q), -R(q2, a2, q), -L(p, b, p2), X(p2, s2, a2, q2)])
                        else:
                            for a2 in range(2):
                                for p2 in range(nL):
                                    for q2 in range(nR):
                                        self.cl.append([-X(p, s, a, q), -L(p2, a2, p), -R(q, b, q2), X(p2, s2, a2, q2)])
        return self.cl

def suche(tmstr, nL, nR, start=0, solver='cadical153', sb=True):
    tm, nS = parse_tm(tmstr)
    e = Enc(tm, nS, nL, nR, start, sb)
    cl = e.baue()
    with Solver(name=solver, bootstrap_with=cl) as S:
        ok = S.solve()
        if not ok:
            return None, len(cl)
        m = set(x for x in S.get_model() if x > 0)
    dL = [[next(r for r in range(nL) if e.v('L', p, a, r) in m) for a in range(2)] for p in range(nL)]
    dR = [[next(r for r in range(nR) if e.v('R', q, a, r) in m) for a in range(2)] for q in range(nR)]
    acc = sorted([(p, s, a, q) for p in range(nL) for s in range(nS) for a in range(2) for q in range(nR)
                  if e.v('X', p, s, a, q) in m])
    return {'tm': tmstr, 'start': start, 'nL': nL, 'nR': nR, 'dL': dL, 'dR': dR, 'acc': acc}, len(cl)

if __name__ == '__main__':
    tmstr, nL, nR = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    start = ord(sys.argv[4]) - 65 if len(sys.argv) > 4 and not sys.argv[4].startswith('--') else 0
    aus = sys.argv[sys.argv.index('--aus') + 1] if '--aus' in sys.argv else None
    t = time.time()
    z, ncl = suche(tmstr, nL, nR, start, sb=('--ohne-sb' not in sys.argv))
    dt = time.time() - t
    print(f'{tmstr} start={chr(65+start)} nL={nL} nR={nR} klauseln={ncl} zeit={dt:.1f}s ergebnis={"SAT" if z else "UNSAT"}')
    if z:
        if aus:
            json.dump(z, open(aus, 'w'), indent=1)
        print(json.dumps(z), flush=True)
