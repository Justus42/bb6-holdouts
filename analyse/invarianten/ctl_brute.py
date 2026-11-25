#!/usr/bin/env python3
"""Zweites, unabhaengiges Programm fuer die Aussage "kein CTL-Zertifikat der Groesse nL x nR".
Ohne SAT: zaehlt ALLE DFA-Paare (ohne Symmetriebrechung, nur d(0,0)=0) auf und berechnet fuer jedes
Paar die kleinste abgeschlossene Annahmemenge ab dem Starttupel (Vorwaertssuche). Ein Zertifikat
existiert genau dann, wenn diese Menge kein Halt-Tupel enthaelt.
Aufruf: python3 ctl_brute.py <TM> <nL> <nR> [Start]   (praktisch bis etwa 3x3)"""
import sys, itertools

def tm_lesen(s):
    T = {}
    for q, z in enumerate(s.split('_')):
        for a in (0, 1):
            w = z[3*a:3*a+3]
            T[q, a] = None if ('-' in w or w[2] in 'HZ') else (int(w[0]), w[1], ord(w[2]) - ord('A'))
    return T

def alle_dfas(n):
    zellen = [(p, a) for p in range(n) for a in (0, 1) if (p, a) != (0, 0)]
    for werte in itertools.product(range(n), repeat=len(zellen)):
        d = {(0, 0): 0}
        d.update(zip(zellen, werte))
        yield d

def abschluss_ok(T, dL, nL, dR, nR, start):
    vorL = {}; vorR = {}
    for (p, a), r in dL.items(): vorL.setdefault(r, []).append((p, a))
    for (q, a), r in dR.items(): vorR.setdefault(r, []).append((q, a))
    gesehen = {(0, start, 0, 0)}; stapel = [(0, start, 0, 0)]
    while stapel:
        p, s, a, q = stapel.pop()
        t = T[s, a]
        if t is None: return False
        b, d, s2 = t
        if d == 'R':
            neu = [(dL[p, b], s2, a2, q2) for (q2, a2) in vorR.get(q, [])]
        else:
            neu = [(p2, s2, a2, dR[q, b]) for (p2, a2) in vorL.get(p, [])]
        for x in neu:
            if x not in gesehen:
                gesehen.add(x); stapel.append(x)
    return True

if __name__ == '__main__':
    tm, nL, nR = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    start = ord(sys.argv[4]) - 65 if len(sys.argv) > 4 else 0
    T = tm_lesen(tm)
    Rs = list(alle_dfas(nR))
    gef = 0; paare = 0
    for dL in alle_dfas(nL):
        for dR in Rs:
            paare += 1
            if abschluss_ok(T, dL, nL, dR, nR, start): gef += 1
    print(f'{tm} start={chr(65+start)} nL={nL} nR={nR} paare={paare} mit_zertifikat={gef} ergebnis={"SAT" if gef else "UNSAT"}')
