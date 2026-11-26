#!/usr/bin/env python3
"""Zusatz der Pruefstelle, Punkt 1: Vorstufen von T = "A> 0 | 0001" (M5-A liest 0, rechts davon 0001).

Reine Aufzaehlung, unabhaengig von luecke.c: alle Fenster (Zustand, Zellen -R..+R) von M5 werden d Schritte vorwaerts
gerechnet (d = 1..D). Gesammelt wird jede Startkonfiguration, die nach genau d Schritten T erreicht. Geprueft wird:
  d = 1: jede passt auf  VB = B> 1 | 00001  oder  VE = E> 0 | 00001
  d = 2: jede passt auf  P1 = A> 0 | 100001,  P2 = 0 D> 1 | 0001,  P3 = C> 1 | 000001
  d >= 2: die Konfiguration zwei Schritte vor T passt immer auf P1, P2 oder P3 (folgt aus d = 2, hier nachgezaehlt)
Positivkontrolle: aus jedem Muster wird T tatsaechlich erreicht (mit allen Belegungen der uebrigen Zellen).
Negativkontrolle: ein absichtlich falsches Muster (P1 mit 100011) wird als "erreicht T nicht" erkannt.

Teil 2 (Punkt 2): Auf welchen Wegen kann eine Luecke "1 0^k 1" (k >= 4, beide Einsen strikt rechts vom Kopf) entstehen?
Aufgezaehlt werden alle Zwei-Schritt-Wege, vor denen im Fenster keine solche Luecke strikt rechts vom Kopf stand und
nach denen eine steht (Fensterpruefung; Wege sind eine Obermenge der echten). Ausgegeben: Uebergangspaare und die
Zellen links der neuen Luecken-1.

Aufruf: python3 vorstufen.py [R] [D]   (Vorgabe R=7, D=3)
"""
import sys

M5 = '1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC'
Z = 'ABCDE'
TM = {}
for q, z in enumerate(M5.split('_')):
    for a in (0, 1):
        w = z[3*a:3*a+3]
        TM[(q, a)] = (int(w[0]), 1 if w[1] == 'R' else -1, Z.index(w[2]))

def ist_T(s, zellen, k):
    return s == 0 and zellen[k] == 0 and zellen[k+1:k+5] == [0, 0, 0, 1]

# Muster: (Zustand, {Versatz zum Kopf: Bit})
def muster(zustand, links, kopf, rechts):
    m = {0: kopf}
    for j, c in enumerate(reversed(links)): m[-(j+1)] = int(c)
    for j, c in enumerate(rechts): m[j+1] = int(c)
    return (Z.index(zustand), m)

M1 = {'VB': muster('B', '', 1, '00001'), 'VE': muster('E', '', 0, '00001')}
M2 = {'P1': muster('A', '', 0, '100001'), 'P2': muster('D', '0', 1, '0001'), 'P3': muster('C', '', 1, '000001')}

def passt(s, zellen, k, mu):
    q, m = mu
    return s == q and all(0 <= k + o < len(zellen) and zellen[k + o] == v for o, v in m.items())

def laufe(s, zellen, k, d):
    zellen = list(zellen)
    for _ in range(d):
        b, r, s2 = TM[(s, zellen[k])]
        zellen[k] = b; k += r; s = s2
        if not (0 <= k < len(zellen) - 5): return None
    return s, zellen, k

def main():
    R = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    D = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    n = 2 * R + 1
    print(f'Fenster R={R}, Tiefe bis {D}')
    for d in range(1, D + 1):
        treffer = 0; passend = {}; fremd = 0
        for s in range(5):
            for bits in range(1 << n):
                zellen = [(bits >> i) & 1 for i in range(n)]
                e = laufe(s, zellen, R, d)
                if e is None or not ist_T(*e): continue
                treffer += 1
                # Konfiguration zwei Schritte vor T (bei d = 1: einen Schritt vor T)
                if d == 1:
                    vor = (s, zellen, R); muster_ = M1
                else:
                    vor = laufe(s, zellen, R, d - 2); muster_ = M2
                namen = [nm for nm, mu in muster_.items() if passt(*vor, mu)]
                if len(namen) == 1: passend[namen[0]] = passend.get(namen[0], 0) + 1
                else: fremd += 1
        print(f'  d={d}: {treffer} Fensterbelegungen erreichen T nach genau {d} Schritten; '
              f'{"einen" if d == 1 else "zwei"} Schritt(e) vor T: {passend}, auf kein (oder mehr als ein) Muster: {fremd}')
    # Positivkontrolle und Negativkontrolle
    def erreicht(mu, schritte):
        q, m = mu
        frei = [o for o in range(-R, R + 1) if o not in m]
        alle = True
        for bits in range(1 << len(frei)):
            zellen = [0] * n
            for o, v in m.items(): zellen[R + o] = v
            for j, o in enumerate(frei): zellen[R + o] = (bits >> j) & 1
            e = laufe(q, zellen, R, schritte)
            if e is None or not ist_T(*e): alle = False; break
        return alle
    for nm, mu in list(M1.items()) + list(M2.items()):
        print(f'  Positivkontrolle {nm}: erreicht T nach {1 if nm in M1 else 2} Schritt(en) bei jeder Belegung: '
              f'{erreicht(mu, 1 if nm in M1 else 2)}')
    falsch = muster('A', '', 0, '100011')
    print(f'  Negativkontrolle (A> 0 | 100011): erreicht T: {erreicht(falsch, 2)} (erwartet False)')
    teil2(R)

def luecke_rechts(zellen, k):
    # gibt es i > k mit zellen[i] = 1, dann >= 4 Nullen, dann eine 1 (im Fenster)?
    for i in range(k + 1, len(zellen)):
        if zellen[i] != 1: continue
        j = i + 1
        while j < len(zellen) and zellen[j] == 0: j += 1
        if j < len(zellen) and j - i - 1 >= 4: return i
    return None

def teil2(R):
    n = 2 * R + 1; wege = {}
    for s in range(5):
        for bits in range(1 << n):
            zellen = [(bits >> i) & 1 for i in range(n)]
            k = R
            if luecke_rechts(zellen, k) is not None: continue
            folge = []; z = list(zellen); q = s
            for schritt in range(2):
                a = z[k]; b, r, q2 = TM[(q, a)]
                folge.append(Z[q] + str(a)); z[k] = b; k += r; q = q2
                if not (0 <= k < n): break
                i = luecke_rechts(z, k)
                if i is not None:
                    key = (' '.join(folge), ''.join(map(str, zellen[R - 2:R + 7])) if schritt == 1 else '')
                    wege[' '.join(folge)] = wege.get(' '.join(folge), 0) + 1
                    break
    print(f'Teil 2: Wege, auf denen eine Luecke (k >= 4) strikt rechts vom Kopf entsteht (Fenster R={R}):')
    for f, c in sorted(wege.items()): print(f'  {f:8s}: {c} Fensterbelegungen')

if __name__ == '__main__':
    main()
