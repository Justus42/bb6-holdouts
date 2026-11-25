"""Gegenprobe der symbolischen Ausfuehrung (symb.py) mit exakten Zahlen gegen eine direkte Bit-Simulation.

Fuer zufaellige konkrete Schnappschuesse jeder Regel (Token-Bedingungen wie in lauf_m.py, T0 = (1, gerade >= 2),
Zone 0..8 Token, Zahlen klein und gross, r = 1..4):
  * Bit-Simulation (eigener Code hier, Band als dict) bis der Kopf zum ersten Mal Zelle p+3 betritt;
    notiert jeden C-Eintritt von links mit den Zellen x, x+1, x+2 und die Schrittzahl.
  * symb.py mit exakten Zahlen ('e', v): muss genau einen Pfad liefern, mit ENDE enden; Band am Ende und
    Schrittzahl (E = 1, S1/S2 = 3n) muessen gleich sein.
  * Zusaetzlich: vorher kein Schnappschuss (Definition wie zyklus/snap.py), bei p+3 einer mit r-1.
Aufruf: python3 -I validiere.py <Proben je Regel> <seed>
"""
import os
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symb as s   # noqa: E402
s.CAP = 10 ** 9   # exakte Zahlen: kein Abschneiden

TAB = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
TT = {}
for q, st in enumerate(TAB.split("_")):
    for bb in range(2):
        e = st[3 * bb:3 * bb + 3]
        if e != "---":
            TT[(q, bb)] = (int(e[0]), 1 if e[1] == "R" else -1, ord(e[2]) - 65)


def zahl(R, art):
    x = R.randint(0, 40) if R.random() < 0.2 else R.randint(0, 9)
    if art == "o":
        return x | 1
    if art == "e":
        return x & ~1
    if art == "e2":
        return max(2, x & ~1)
    if art == "p":
        return max(1, x)
    return x


def instanz(R, regel):
    """Token-Liste links -> rechts (sep, n) und Ende-Art ('P' beliebig / '_' leer)."""
    zone = [("1", zahl(R, "o")) for _ in range(R.randint(0 if regel != "LG" else 1, 8))]
    T0 = [("1", zahl(R, "e2"))]
    praef = [(R.choice("01"), zahl(R, "a")) for _ in range(R.randint(0, 3))]
    G = (R.choice("01"), zahl(R, "p"))
    if regel == "N1":
        kern, ende = [("0", zahl(R, "e"))], "P"
    elif regel == "N2":
        kern, ende = [G, ("1", zahl(R, "e"))], "P"
    elif regel == "N2s":
        kern, ende = [G, ("0", zahl(R, "o"))], "P"
    elif regel == "UA":
        kern, ende = [G, ("1", 0), ("0", zahl(R, "o"))], "P"
    elif regel == "LE0":
        kern, ende, praef = [("1", 0)], "_", []
    elif regel == "LE1":
        kern, ende, praef = [("1", 0), ("0", zahl(R, "o"))], "_", []
    else:
        kern, ende, praef = [], "_", []
    return praef + kern + zone + T0, ende, len(praef)


def schnappschuss(band, p, hi):
    """Definition wie zyklus/snap.py: C liest 0, rechts 0, dann (100)^r und die 1 am rechten Ende hi."""
    if band.get(p, 0) != 0 or band.get(p + 1, 0) != 0:
        return None
    j, r = p + 2, 0
    while j + 2 <= hi and band.get(j, 0) == 1 and band.get(j + 1, 0) == 0 and band.get(j + 2, 0) == 0:
        r += 1
        j += 3
    return r if j == hi and band.get(j, 0) == 1 else None


def bitsim(tok, r):
    L = "".join(t + "011" * n for t, n in tok)
    band = {}
    for i, c in enumerate(L):
        band[i - len(L)] = int(c)
    Rr = "00" + "100" * r + "1"
    for i, c in enumerate(Rr):
        band[i] = int(c)
    p, q, n = 0, s.C, 0
    hi = len(Rr) - 1
    lo = -len(L)
    fenster = set()
    while True:
        bt = band.get(p, 0)
        if (q, bt) not in TT:
            return None
        w, d, q2 = TT[(q, bt)]
        band[p] = w
        p += d
        q = q2
        n += 1
        lo = min(lo, p)
        if q == s.C and d == 1:
            fenster.add((band.get(p, 0), band.get(p + 1, 0), band.get(p + 2, 0)))
        if q == s.C and p != 3 and schnappschuss(band, p, hi) is not None:
            fenster.add(("frueher Schnappschuss",))
        if p == 3:
            if schnappschuss(band, p, hi) != r - 1:
                fenster.add(("kein Schnappschuss bei p+3",))
            return q, n, band, fenster, lo


def stapel(tok, ende, npraef):
    L = []
    for i, (t, n) in enumerate(reversed(tok)):
        idx = len(tok) - 1 - i
        if idx < npraef:
            break
        if n:
            L.append(("w", "011", ("e", n)))
        L.append(("b", int(t)))
    if ende == "P":
        L.append(("P",))
    else:
        L.append(("_",))
    return tuple(L)


def symbolisch(L):
    z = (s.C, "R", L, (("b", 0), ("b", 0), ("b", 1), ("#",)))
    n = 0
    while True:
        nf = s.schritte(z)
        if len(nf) != 1:
            raise AssertionError(f"nicht eindeutig: {len(nf)}")
        art, z2 = nf[0]
        if art == "ENDE":
            return z, n
        q, seite, L0, R0 = z
        if art == "S1":
            n += 3 * R0[0][2][1]
        elif art == "S2":
            n += 3 * L0[0][2][1]
        elif art == "E":
            n += 1
        z = z2


def bits_links(L):
    out = []
    for x in L:
        if x[0] == "b":
            out.append(str(x[1]))
        elif x[0] == "w":
            out.append(x[1][::-1] * x[2][1])
        else:
            break
    return "".join(out)[::-1]


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    R = random.Random(seed)
    fehler = 0
    for regel in ("N1", "N2", "N2s", "UA", "LE0", "LE1", "LG"):
        gleich = 0
        alle_f = set()
        fs = set()
        for _ in range(N):
            tok, ende, npraef = instanz(R, regel)
            r = R.randint(1, 4)
            res = bitsim(tok, r)
            if res is None:
                print(regel, "HALT in Bit-Simulation", tok)
                fehler += 1
                continue
            q, n, band, fenster, lo = res
            alle_f |= {f for f in fenster if len(f) == 3}
            zs, ns = symbolisch(stapel(tok, ende, npraef))
            # Band links vom Kopf (Zellen lo .. 2) aus der Bit-Simulation
            links_bit = "".join(str(band.get(i, 0)) for i in range(lo, 3))
            praef_len = sum(1 + 3 * nn for _, nn in tok[:npraef])
            links_sym = bits_links(zs[2])
            # symbolisch: Zellen ab Ende des Praefixes (bzw. ab linkem Bandende) bis p+2
            start = -sum(1 + 3 * nn for _, nn in tok) + praef_len
            # bei '_' kann das Band links gewachsen sein: fuehrende Nullen angleichen
            ziel = "".join(str(band.get(i, 0)) for i in range(min(lo, start - len(links_sym)), 3))
            ok = (q == s.C and n == ns and ziel.endswith(links_sym)
                  and set(ziel[:len(ziel) - len(links_sym)]) <= {"0"} | (set("01") if ende == "P" else set())
                  and zs[0] == s.C and zs[1] == "R")
            # Praefix unveraendert (bei P): Zellen links von start gleich wie am Anfang
            if ende == "P":
                Lalt = "".join(t + "011" * nn for t, nn in tok)
                for i in range(-len(Lalt), start):
                    if band.get(i, 0) != int(Lalt[i + len(Lalt)]):
                        ok = False
            if not ok or any(len(f) == 1 or (f[1] == 1 and f[2] == 1) for f in fenster):
                fehler += 1
                if fehler < 5:
                    print("ABWEICHUNG", regel, tok, r, q, n, ns)
            else:
                gleich += 1
        print(f"{regel:4s} {gleich}/{N} gleich (Band, Schritte, Ende in C bei p+3); "
              f"C-Fenster von links: {' '.join(''.join(map(str, f)) for f in sorted(alle_f))}")
    print("Abweichungen:", fehler)
    sys.exit(1 if fehler else 0)


if __name__ == "__main__":
    main()
