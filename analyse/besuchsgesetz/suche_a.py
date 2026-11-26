#!/usr/bin/env python3
# Programm A (Thread "Familie Besuchsgesetz", 25.11.2026): sucht unter allen Holdouts Maschinen mit dem
# Besuchsgesetz aus busycoq PR #59, fuer jede Spiegelung und jedes Zustandspaar (c = Eintritt, a = Rueckkehr);
# damit ist jede Umbenennung der Zustaende abgedeckt (das Gesetz nennt nur c und a).
#
# Besuch (wie PR #59, Definition Vis): Zelle -2 = x, Zelle -1 = 0, Wort w ab Zelle 0, rechts Nullen,
# Kopf auf Zelle 0 im Zustand c. Ende beim ersten Mal, dass der Kopf im Zustand a auf Zelle -2 steht;
# dann muessen Zelle -1 = 0 und Zelle -2 = x sein. Geht der Kopf links an -2 vorbei: "links".
# Gesetz (in der Form der Annahmen aus PR #59, als Implikationen):
#   V(0r) = 1r                       (fuer jedes r)
#   V(r)=y      -> V(100r)=000y, V(110r)=000y;   V(r) haelt -> V(100r), V(110r) halten
#   V(r)=y, V(y)=z -> V(1010r)=1010z;  V(r) haelt oder V(y) haelt -> V(1010r) haelt
# Getestet auf allen Woertern w bis Laenge L (Standard 12) inkl. Block, x in {0,1}.
# Rundenform: ab Leerband die erste Konfiguration "Zustand c, Zelle links daneben 0" = Rundenbeginn mit
# Wort w0 (rechts davon) und Linkskontext u. Nach dem Besuch laeuft die Maschine (ohne das Wort zu lesen)
# bis zur naechsten solchen Konfiguration; dort steht p vor dem Ergebnis y, und links wieder u. Gilt das,
# ist jede Runde gleich gebaut: w_{k+1} = p . V(w_k).
# Aufruf: suche_a.py <holdouts.txt> [L]   FEHLER=1: falsche 1010-Regel (V(1010r)=1010 V(r)); FEHLER=2: keine Spiegelung;
# FEHLER=3: Zwischenspiel muss einen falschen Linkskontext (u0 + 0) herstellen (Rundenform darf dann nie gefunden werden)
import sys, os, itertools

FEHLER = os.environ.get('FEHLER', '0')
SCHRITTE = 200000

def lies(s, spiegel):
    T = {}
    for i, teil in enumerate(s.split('_')):
        for b in (0, 1):
            t = teil[3*b:3*b+3]
            if t[2] in '-HZ' or t[0] == '-':
                T[(i, b)] = None
            else:
                d = 1 if t[1] == 'R' else -1
                if spiegel: d = -d
                T[(i, b)] = (int(t[0]), d, ord(t[2]) - 65)
    return T

def besuch(T, w, x, c, a):
    band = {-2: x, -1: 0}
    for i, b in enumerate(w): band[i] = b
    p, q = 0, c
    for _ in range(SCHRITTE):
        if p == -2 and q == a:
            if band[-1] != 0 or band[-2] != x: return 'falsch_zurueck'
            hi = max(k for k in band) if band else 0
            o = [band.get(i, 0) for i in range(0, hi + 1)]
            while o and o[-1] == 0: o.pop()
            return tuple(o)
        if p < -2: return 'links'
        t = T[(q, band.get(p, 0))]
        if t is None: return 'halt'
        band[p] = t[0]; p += t[1]; q = t[2]
    return 'grenze'

def pruefe(T, c, a, L):
    memo = {}
    def V(w, x):
        k = (w, x)
        if k not in memo: memo[k] = besuch(T, w, x, c, a)
        return memo[k]
    # Vorsieb: wenige Woerter
    for x in (0, 1):
        for w in [(), (0,), (0, 1), (0, 1, 1), (1, 0, 0), (1, 1, 0, 1)]:
            pass
        for w in [(), (0,), (0, 1), (0, 1, 1, 0, 1)]:
            if V(w, x) != (1,) + w[1:] and not (w == () and V(w, x) == (1,)):
                return None
    zahl = {'0': 0, '100': 0, '110': 0, '1010': 0}
    for x in (0, 1):
        for n in range(L + 1):
            for w in itertools.product((0, 1), repeat=n):
                v = V(w, x)
                if n == 0 or w[0] == 0:
                    soll = norm((1,) + w[1:])
                    if v != soll: return None
                    zahl['0'] += 1
                elif w[:3] in ((1, 0, 0), (1, 1, 0)):
                    r = V(w[3:], x)
                    if isinstance(r, tuple):
                        if v != norm((0, 0, 0) + r): return None
                        zahl[''.join(map(str, w[:3]))] += 1
                    elif r == 'halt':
                        if v != 'halt': return None
                        zahl[''.join(map(str, w[:3]))] += 1
                elif w[:4] == (1, 0, 1, 0):
                    r = V(w[4:], x)
                    if isinstance(r, tuple):
                        z = V(r, x) if FEHLER != '1' else r
                        if isinstance(z, tuple):
                            if v != (1, 0, 1, 0) + z: return None
                            zahl['1010'] += 1
                        elif z == 'halt':
                            if v != 'halt': return None
                            zahl['1010'] += 1
                    elif r == 'halt':
                        if v != 'halt': return None
                        zahl['1010'] += 1
    return zahl, V

def norm(t):
    t = list(t)
    while t and t[-1] == 0: t.pop()
    return tuple(t)

def sonder(V, block, L):
    """Verhalten von V(block r) fuer alle r bis Laenge L-len(block), x in {0,1}."""
    erg = {}
    for x in (0, 1):
        for n in range(L - len(block) + 1):
            for r in itertools.product((0, 1), repeat=n):
                v = V(block + r, x)
                if isinstance(v, tuple):
                    # Form q r mit festem q (4 bzw. 3 Zellen)?
                    k = len(block)
                    vv = v + (0,) * max(0, k + n - len(v))
                    if norm(vv[k:]) == norm(r): erg.setdefault('wort:' + ''.join(map(str, vv[:k])) + 'x', 0)
                    else: erg.setdefault('wort:sonst', 0)
                    key = 'wort:' + ''.join(map(str, vv[:k])) + 'x' if norm(vv[k:]) == norm(r) else 'wort:sonst'
                    erg[key] += 1
                else:
                    erg[v] = erg.get(v, 0) + 1
    if len(erg) == 1:
        k = next(iter(erg))
        return k.replace('wort:', '= ') if k.startswith('wort:') else k
    return 'uneinheitlich(' + ','.join(f'{k}:{v}' for k, v in sorted(erg.items())) + ')'

def links(band, P):  # Linkskontext: Zellen < P-1, fuehrende Nullen weg
    ks = [k for k in band if k < P - 1 and band[k]]
    if not ks: return ()
    return tuple(band.get(i, 0) for i in range(min(ks), P - 1))

def zwischenspiel(T, c, a, u0):
    """Band 0^inf u0 0 | mit Kopf im Zustand a auf der letzten Zelle von u0 (= x), Wort ab | unbekannt.
    Laeuft bis zur ersten Konfiguration 'Zustand c, links daneben 0, Linkskontext wieder u0' links von |.
    Das Wort ab | darf dabei nicht gelesen werden."""
    P = 0; band = {}
    for i, b in enumerate(u0): band[P - 1 - len(u0) + i] = b
    band[P - 1] = 0
    p, q = P - 2, a
    for _ in range(10000):
        ziel = u0 + (0,) if FEHLER == '3' else u0
        if q == c and p <= P and band.get(p - 1, 0) == 0 and links(band, p) == ziel:
            return tuple(band.get(i, 0) for i in range(p, P)), 'ok'
        if p >= P: return None, 'Zwischenspiel liest das Wort'
        t = T[(q, band.get(p, 0))]
        if t is None: return None, 'Zwischenspiel haelt'
        band[p] = t[0]; p += t[1]; q = t[2]
    return None, 'Zwischenspiel endet nicht'

def rundenform(T, c, a, kandidaten=6):
    """Ab Leerband: die ersten Konfigurationen 'Zustand c, links daneben 0' sind Kandidaten fuer den
    Rundenbeginn (Wort w0 rechts, Linkskontext u0). Der erste Kandidat, bei dem das Zwischenspiel nach dem
    Besuch wieder Linkskontext u0 herstellt, gibt die Rundenform (u0, p, w0)."""
    band = {}; p = 0; q = 0; gruende = []
    for _ in range(SCHRITTE):
        if q == c and band.get(p - 1, 0) == 0:
            hi = max([k for k in band if band[k]] + [p - 1])
            w0 = norm(tuple(band.get(i, 0) for i in range(p, hi + 1)))
            u0 = links(band, p)
            if u0:
                pre, g = zwischenspiel(T, c, a, u0)
                if pre is not None: return (u0, pre, w0), 'ok'
                gruende.append(g)
            else:
                gruende.append('kein Linkskontext')
            if len(gruende) >= kandidaten: break
        t = T[(q, band.get(p, 0))]
        if t is None: break
        band[p] = t[0]; p += t[1]; q = t[2]
    return None, ';'.join(gruende) or 'kein Rundenbeginn'

def main():
    ms = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    L = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    sp = (False,) if FEHLER == '2' else (False, True)
    for n, s in enumerate(ms, 1):
        for spiegel in sp:
            T = lies(s, spiegel)
            for c in range(6):
                for a in range(6):
                    r = pruefe(T, c, a, L)
                    if r is None: continue
                    zahl, V = r
                    k = sonder(V, (1, 0, 1, 1), L)
                    h = sonder(V, (1, 1, 1), L)
                    rf, grund = rundenform(T, c, a)
                    rtxt = 'u=%s p=%s w0=%s' % tuple(''.join(map(str, t)) or '-' for t in rf) if rf else 'keine:' + grund
                    print(f"{n}\t{s}\t{'gespiegelt' if spiegel else 'normal'}\t{'ABCDEF'[c]}\t{'ABCDEF'[a]}\t"
                          f"{zahl['0']},{zahl['100']},{zahl['110']},{zahl['1010']}\t1011:{k}\t111:{h}\t{rtxt}", flush=True)

if __name__ == '__main__':
    main()
