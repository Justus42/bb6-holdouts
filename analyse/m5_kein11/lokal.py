#!/usr/bin/env python3
"""M5, neuer Ansatz "nie 11 strikt rechts vom Kopf" (26.11.2026), Punkt 2: (a) und (b) maschinell.

Eigenschaft I(c): auf dem Band gibt es keine zwei benachbarten Einsen an Stellen i, i+1 mit i > Kopf
(also beide Zellen strikt rechts vom Kopf).

Vorgehen: reine Aufzaehlung lokaler Fenster. Ein Fenster = Zustand + Zellen -R..+R um den Kopf, alle 2^(2R+1)
Inhalte. Es wird hoechstens K Schritte gerechnet (K <= R, der Kopf bleibt also im Fenster). I wird nur auf den
Fensterzellen geprueft; das ist schwaecher als I auf dem ganzen Band, die gefundenen Wege sind also eine
OBERMENGE der echten. "Kein Weg gefunden" ist damit eine gueltige Aussage fuer das ganze Band.

(a) Gibt es einen Weg c_0 -> ... -> c_k, k = 0..K, bei dem c_k haelt (undefinierter Uebergang) und ALLE c_i
    (i = 0..k) I erfuellen? Gesucht: das kleinste k, ab dem es keinen solchen Weg gibt.
(b) Alle Wege c_0 -> ... -> c_k, bei denen c_0..c_{k-1} I erfuellen und c_k I verletzt. Ausgegeben werden die
    Folgen der benutzten Uebergaenge (Zustand+gelesenes Bit), fuer k = 1..K.

Ausserdem: Zuordnung der 6-Zustands-Maschinen auf M5 (Homomorphismus der Zustaende, per Durchprobieren).

Aufruf: python3 lokal.py [R] [K]     (Vorgabe R=6, K=5)
"""
import sys, itertools

MASCHINEN = {
    'M5':  ('1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC', 'A'),
    '274': ('1RB0RE_1LC0RA_0LD1LB_1LA1LF_0LB0RD_0LB---', 'A'),
    '318': ('1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC', 'A'),
    '322': ('1RB1RF_1LC0LF_1RD0LB_0RA1RE_1RD---_0RC0LA', 'A'),
    '518': ('1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---', 'A'),
}
def spiegeln(s):
    return s.translate(str.maketrans('LR', 'RL'))
# 274 ist laut bbe die gespiegelte Tabelle; '274m' = 274 mit L und R vertauscht (Band gespiegelt, gleiche Dynamik).
MASCHINEN['274m'] = (spiegeln(MASCHINEN['274'][0]), 'A')
# Negativkontrolle fuer (b): M5 mit B1 = 1LA statt 1RA. Dann kann auch B1 "11" rechts vom Kopf erzeugen;
# (b) muss B1 als letzten Uebergang melden.
MASCHINEN['Kontrolle-B1L'] = ('1RB0LD_0RC1LA_1RD1RE_1LA0LE_0RA0LC', 'A')
Z = 'ABCDEF'

def tabelle(s):
    t = {}
    for q, zeile in enumerate(s.split('_')):
        for a in (0, 1):
            w = zeile[3*a:3*a+3]
            t[(q, a)] = None if '-' in w else (int(w[0]), 1 if w[1] == 'R' else -1, Z.index(w[2]))
    return t, len(s.split('_'))

def I_ok(zellen, kopf):
    # zellen: Liste, Index = Fensterposition; kopf: Index des Kopfes
    for i in range(kopf + 1, len(zellen) - 1):
        if zellen[i] and zellen[i+1]:
            return False
    return True

def wege(tm, nS, R, K):
    """Erzeugt alle Wege der Laenge 0..K ab allen Fenstern. Liefert (art, k, uebergaenge, start)
    art = 'halt' (alle Konfigurationen erfuellen I, letzte haelt) oder 'bruch' (letzte verletzt I, alle davor nicht)."""
    n = 2*R + 1
    for s0 in range(nS):
        for bits in range(1 << n):
            zellen = [(bits >> i) & 1 for i in range(n)]
            kopf, s = R, s0
            if not I_ok(zellen, kopf):
                continue
            folge = []
            for k in range(K + 1):
                a = zellen[kopf]
                t = tm[(s, a)]
                if t is None:
                    yield ('halt', k, tuple(folge), (s0, tuple(zellen)))
                    break
                if k == K:
                    break
                b, d, s2 = t
                folge.append(Z[s] + str(a))
                zellen = list(zellen); zellen[kopf] = b
                kopf += d; s = s2
                if not (0 <= kopf < n):
                    break
                if not I_ok(zellen, kopf):
                    yield ('bruch', k + 1, tuple(folge), (s0, tuple(zellen)))
                    break

def homomorphismus(tm6, n6, tm5):
    loes = []
    for h in itertools.product(range(5), repeat=n6):
        ok = True
        for (s, a), t in tm6.items():
            if t is None: continue
            b, d, s2 = t
            u = tm5[(h[s], a)]
            if u is None or u != (b, d, h[s2]):
                ok = False; break
        if ok: loes.append(h)
    return loes

def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    K = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    assert K <= R
    tm5, _ = tabelle(MASCHINEN['M5'][0])
    print(f'Fenster R={R} (Zellen -{R}..+{R}), hoechstens K={K} Schritte\n')
    print('== Zuordnung auf M5 (Zustand der Maschine -> Zustand von M5)')
    for name in ('274', '274m', '318', '322', '518'):
        tm6, n6 = tabelle(MASCHINEN[name][0])
        hs = homomorphismus(tm6, n6, tm5)
        halt = [Z[s] + str(a) for (s, a), t in tm6.items() if t is None]
        for h in hs:
            print(f'  {name}: ' + ' '.join(f'{Z[i]}->{Z[h[i]]}' for i in range(n6)) +
                  f'   Halt bei {halt[0]} (= M5 {Z[h[Z.index(halt[0][0])]]}{halt[0][1]}), Start A -> M5 {Z[h[0]]}')
        if not hs: print(f'  {name}: KEINE Zuordnung')
    print()
    for name, (s, _) in MASCHINEN.items():
        tm, nS = tabelle(s)
        halt_k = {}
        bruch = {}
        for art, k, folge, start in wege(tm, nS, R, K):
            if art == 'halt':
                halt_k.setdefault(k, set()).add(folge)
            else:
                bruch.setdefault(k, set()).add(folge)
        print(f'== {name} {s}')
        if name not in ('M5', 'Kontrolle-B1L'):
            print('  (a) Wege zum Halt, bei denen jede Konfiguration I erfuellt (nach Laenge k):')
            for k in range(K + 1):
                fs = sorted(halt_k.get(k, ()))
                print(f'     k={k}: {len(fs)} Uebergangsfolgen' + (f'  z.B. {" ".join(fs[0]) or "(Haltekonfiguration selbst)"}' if fs else ''))
            kmin = next((k for k in range(K + 1) if not halt_k.get(k)), None)
            if kmin is not None and all(not halt_k.get(k) for k in range(kmin, K + 1)):
                print(f'     => ab k={kmin} kein solcher Weg: jeder Halt nach mindestens {kmin} Schritten hat unter den letzten {kmin+1} Konfigurationen eine mit "11" strikt rechts vom Kopf.')
        print('  (b) Wege, deren letzte Konfiguration I erstmals verletzt (Folge der Uebergaenge, letzter = verletzender Schritt):')
        for k in range(1, K + 1):
            fs = sorted(bruch.get(k, ()))
            letzte = sorted(set(f[-1] for f in fs))
            print(f'     k={k}: {len(fs)} Folgen; letzter Uebergang immer in {letzte}')
            # Folgen, die ueber k Schritte unter I laufen, gruppiert nach den letzten min(k,4) Uebergaengen
            enden = sorted(set(f[-min(k, 4):] for f in fs))
            if k <= 4:
                print(f'        Folgen: {[" ".join(f) for f in enden]}')
            else:
                print(f'        letzte 4 Uebergaenge: {[" ".join(f) for f in enden]}')
        print()

if __name__ == '__main__':
    main()
