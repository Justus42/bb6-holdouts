"""Zufallssuche mit beliebigem rechtestem Token T0 (Abschnitt 4 des Berichts): Phasen nach den Regel-
bedingungen aus validiere.py, aber T0 = (zufaelliger Trenner, 0..5). Bit-Simulation bis p+3 oder 20.000
Schritte; gemeldet wird jeder C-Eintritt von links vor ?11 und jeder Halt.
Aufruf: python3 -I t0_suche.py <Proben> <seed>"""
import os
import random
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validiere as v  # noqa: E402

N, seed = int(sys.argv[1]), int(sys.argv[2])
R = random.Random(seed)
gef = 0
nicht_p3 = 0
for it in range(N):
    regel = R.choice(["N1", "N2", "N2s", "UA", "LE0", "LE1", "LG"])
    tok, ende, npr = v.instanz(R, regel)
    tok[-1] = (R.choice("01"), R.randint(0, 5))
    r = R.randint(1, 3)
    L = "".join(t + "011" * n for t, n in tok)
    band = {i - len(L): int(c) for i, c in enumerate(L)}
    for i, c in enumerate("00" + "100" * r + "1"):
        band[i] = int(c)
    p, q = 0, 2
    for n in range(20000):
        bt = band.get(p, 0)
        if (q, bt) not in v.TT:
            print("HALT", regel, tok, r)
            gef += 1
            break
        w, d, q2 = v.TT[(q, bt)]
        band[p] = w
        p += d
        q = q2
        if q == 2 and d == 1 and band.get(p + 1, 0) == 1 and band.get(p + 2, 0) == 1:
            print("K(C)/111", regel, tok, r, n)
            gef += 1
            break
        if p == 3:
            nicht_p3 += q != 2
            break
print(f"Proben {N}: K(C)/Halt {gef}; Phasen, die p+3 nicht in C erreichen: {nicht_p3}")
