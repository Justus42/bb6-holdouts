#!/usr/bin/env python3
"""Unabhaengiger Pruefer fuer CTL-Zertifikate (zweites Programm zu ctl_sat.py).

Bewusst anders geschrieben als ctl_sat.py: eigener TM-Parser, kein SAT, reine Aufzaehlung,
Bedingungen 1:1 nach ctlCheck/closureOk in google-deepmind/cryptids
(BusyBeaver/Calculi/CtlCertificate.lean).
Zusaetzlich: Plausibilitaetstest, dass jede bis N Schritte erreichte Konfiguration der echten
Maschine angenommen ist (Abstraktion direkt aus dem Band berechnet).

Aufruf: python3 ctl_pruefer.py zertifikat.json [N]
Exit 0 = gueltig, 1 = ungueltig.
"""
import sys, json

def tabelle(s):
    out = []
    for zeile in s.split('_'):
        paar = []
        for i in (0, 3):
            w = zeile[i:i+3]
            if '-' in w or w[2] in 'HZ':
                paar.append(None)
            else:
                paar.append((int(w[0]), 1 if w[1] == 'R' else -1, 'ABCDEFGH'.index(w[2])))
        out.append(paar)
    return out

def pruefe(z):
    T = tabelle(z['tm'])
    nL, nR, dL, dR = z['nL'], z['nR'], z['dL'], z['dR']
    acc = set(tuple(x) for x in z['acc'])
    fehler = []
    if dL[0][0] != 0: fehler.append('dL(0,0) != 0')
    if dR[0][0] != 0: fehler.append('dR(0,0) != 0')
    if (0, z['start'], 0, 0) not in acc: fehler.append('Starttupel fehlt')
    for (p, s, a, q) in sorted(acc):
        t = T[s][a]
        if t is None:
            fehler.append(f'Halt-Tupel angenommen: {(p,s,a,q)}'); continue
        b, d, s2 = t
        if d == 1:
            for a2 in (0, 1):
                for q2 in range(nR):
                    if dR[q2][a2] == q and (dL[p][b], s2, a2, q2) not in acc:
                        fehler.append(f'{(p,s,a,q)} -> {(dL[p][b], s2, a2, q2)} fehlt')
        else:
            for a2 in (0, 1):
                for p2 in range(nL):
                    if dL[p2][a2] == p and (p2, s2, a2, dR[q][b]) not in acc:
                        fehler.append(f'{(p,s,a,q)} -> {(p2, s2, a2, dR[q][b])} fehlt')
    return fehler

def lauf(z, N):
    """Echte Maschine N Schritte; jede Konfiguration muss angenommen sein.
    Halbbaender als Stapel (fernes Ende unten), dazu der DFA-Zustand nach jedem Stapelelement."""
    T = tabelle(z['tm']); dL, dR = z['dL'], z['dR']
    acc = set(tuple(x) for x in z['acc'])
    L, Ls = [], [0]      # linke Zellen, DFA-Zustaende (Ls[i] = Zustand nach i Zellen)
    R, Rs = [], [0]
    kopf, s = 0, z['start']
    for i in range(N):
        tup = (Ls[-1], s, kopf, Rs[-1])
        if tup not in acc:
            return f'Schritt {i}: Abstraktion {tup} nicht angenommen'
        t = T[s][kopf]
        if t is None:
            return f'Schritt {i}: Halt'
        b, d, s2 = t
        if d == 1:
            L.append(b); Ls.append(dL[Ls[-1]][b])
            if R: kopf = R.pop(); Rs.pop()
            else: kopf = 0
        else:
            R.append(b); Rs.append(dR[Rs[-1]][b])
            if L: kopf = L.pop(); Ls.pop()
            else: kopf = 0
        s = s2
    return None

if __name__ == '__main__':
    z = json.load(open(sys.argv[1]))
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    f = pruefe(z)
    l = lauf(z, N) if not f else 'nicht gelaufen'
    print(f"{z['tm']} start={'ABCDEF'[z['start']]} nL={z['nL']} nR={z['nR']} |acc|={len(z['acc'])}")
    print('Abschlusspruefung:', 'OK' if not f else f'{len(f)} Fehler, z.B. {f[:3]}')
    print(f'Lauf {N} Schritte:', 'OK' if l is None else l)
    sys.exit(0 if (not f and l is None) else 1)
