"""Negativkontrolle fuer den Verbots-Detektor von symb.py: Er muss K(C) und Halt erkennen, wo sie wirklich
vorkommen.

Zufaellige Baender (links 1..14 zufaellige Bits, rechts leer, Startzustand zufaellig) werden mit einer
eigenen Bit-Simulation gerechnet, bis C von links vor ?11 tritt (K(C) oder C vor 111) oder 300 Schritte
vergehen. Dieselben Baender laufen durch symb.py (exakte Zahlen, rechts unendlich leer '_'): der Detektor
muss in genau den Faellen anschlagen, in denen die Bit-Simulation das Muster findet, und im selben Schritt.
Aufruf: python3 -I negativ.py <Proben> <seed>
"""
import os
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symb as s       # noqa: E402
import validiere as v  # noqa: E402
s.CAP = 10 ** 9


def bit_lauf(bits, q0, grenze):
    band = {i - len(bits): b for i, b in enumerate(bits)}
    p, q = 0, q0
    for n in range(grenze):
        bt = band.get(p, 0)
        if (q, bt) not in v.TT:
            return ("Halt", n)
        w, d, q2 = v.TT[(q, bt)]
        band[p] = w
        p += d
        q = q2
        if q == s.C and d == 1 and band.get(p + 1, 0) == 1 and band.get(p + 2, 0) == 1:
            return ("Muster", n + 1)
    return (None, grenze)


def sym_lauf(bits, q0, grenze):
    L = tuple(("b", b) for b in reversed(bits)) + (("_",),)
    z = (q0, "R", L, (("_",),))
    n = 0
    while n < grenze:
        try:
            nf = s.schritte(z)
        except s.Verstoss as e:
            return ("Halt" if "Halt" in str(e) else "Muster", n)
        assert len(nf) == 1
        art, z2 = nf[0]
        q, seite, L0, R0 = z
        n += 3 * R0[0][2][1] if art == "S1" else 3 * L0[0][2][1] if art == "S2" else 1
        z = z2
    return (None, n)


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    R = random.Random(seed)
    tab = {}
    for _ in range(N):
        bits = [R.randint(0, 1) for _ in range(R.randint(1, 14))]
        q0 = R.randint(0, 5)
        a = bit_lauf(bits, q0, 300)
        b = sym_lauf(bits, q0, 300)
        key = (a[0], b[0] if a[0] is None else (b == a))
        tab[key] = tab.get(key, 0) + 1
    gef = sum(c for (x, _), c in tab.items() if x)
    richtig = sum(c for (x, y), c in tab.items() if x and y is True)
    falsch_alarm = sum(c for (x, y), c in tab.items() if x is None and y is not None)
    print(f"Proben {N}: Muster/Halt in Bit-Simulation {gef}, davon vom Detektor im selben Schritt erkannt "
          f"{richtig}; Fehlalarme {falsch_alarm}")
    ok = gef > 0 and richtig == gef and falsch_alarm == 0
    print("Negativkontrolle", "SCHLAEGT AN" if ok else "SCHLAEGT NICHT AN")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
