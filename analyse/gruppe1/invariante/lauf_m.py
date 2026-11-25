"""Treiber: jede Regel mit fester Zonenlaenge m (alle Zahlenwerte abstrakt)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symb as s

def a(u): return ("a", u)
def run(n): return ("w", "011", n)
def b(x): return ("b", x)
T0 = [run(a(2)), b(1)]            # (1, gerade >= 2)  -- im Lauf so (Zyklusregel a(neu) = e3 + 2)
T0_FREI = [[run(a(0)), b(0)], [run(a(1)), b(0)], [run(a(0)), b(1)], [run(a(1)), b(1)]]   # beliebig
ZT = [run(a(1)), b(1)]            # Zonen-Token (1, ungerade)
def G(): return [[run(a(1)), ("P",)], [run(a(2)), ("P",)]]   # (s, g >= 1), g ungerade / gerade
REGELN = {
    "N1":  lambda: [[run(a(0)), b(0), ("P",)]],
    "N2":  lambda: [[run(a(0)), b(1)] + g for g in G()],
    "N2s": lambda: [[run(a(1)), b(0)] + g for g in G()],
    "UA":  lambda: [[run(a(1)), b(0), b(1)] + g for g in G()],
    "LE0": lambda: [[b(1), ("_",)]],
    "LE1": lambda: [[run(a(1)), b(0), b(1), ("_",)]],
    "LG":  lambda: [[("_",)]],
}
def starts(regel, m, zone=None):
    out = []
    t0s = T0_FREI if os.environ.get("SYMB_T0") == "frei" else [T0]
    for t0 in t0s:
        for rest in REGELN[regel]():
            z = zone if zone is not None else ZT * m
            if regel == "LG" and zone is None and m == 0:
                continue
            L = tuple(t0 + z + rest)
            R = (b(0), b(0), b(1), ("#",))
            out.append((s.C, "R", L, R))
    return out
if __name__ == "__main__":
    regeln = sys.argv[1].split(",") if len(sys.argv) > 1 and sys.argv[1] != "alle" else list(REGELN)
    mmax = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    for rg in regeln:
        for m in range(mmax + 1):
            for st in starts(rg, m):
                ok, info = s.suche(st)
                if not ok:
                    print(rg, "m =", m, "VERSTOSS:", info["grund"])
                    for z in info["weg"][-10:]:
                        print("   ", s.zeige(z))
                    break
            else:
                print(rg, "m =", m, "ok", info["zustaende"])
                continue
            break
