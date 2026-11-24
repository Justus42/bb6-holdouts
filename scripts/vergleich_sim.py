#!/usr/bin/env python3
"""Vergleicht sim1 (Python) und sim2 (Rust) auf dem BB(5)-Champion und allen
Varianten mit genau einem geaenderten Uebergangsfeld.
Aufruf (Repo-Wurzel): python3 -I scripts/vergleich_sim.py [limit=1000000]"""
import json, subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent
SIM1 = [sys.executable, "-I", str(R / "sim1_python" / "sim1.py")]
SIM2 = [str(R / "sim2_rust" / "target" / "release" / "sim2")]
CHAMP = "1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA"   # bbchallenge-paper @ c563cb33, Z. 770
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000

def run(cmd, m, lim):
    out = subprocess.run(cmd + [m, str(lim)], capture_output=True, text=True, check=True).stdout
    return json.loads(out)

def variants(m):
    g = m.split("_")
    for gi, grp in enumerate(g):
        for ti in range(2):
            t = grp[3*ti:3*ti+3]
            alts = {("1" if t[0] == "0" else "0") + t[1:], t[0] + ("L" if t[1] == "R" else "R") + t[2]}
            alts |= {t[:2] + s for s in "ABCDEZ" if s != t[2]}
            for a in sorted(alts):
                gg = list(g); gg[gi] = grp[:3*ti] + a + grp[3*ti+3:]
                yield f"{'ABCDE'[gi]}{ti}:{t}->{a}", "_".join(gg)

c1, c2 = run(SIM1, CHAMP, 100_000_000), run(SIM2, CHAMP, 100_000_000)
print("Champion sim1:", c1); print("Champion sim2:", c2)
ok = c1 == c2 and c1["halted"] and c1["steps"] == 47_176_870 and c1["ones"] == 4098
print("Champion == Sollwerte (47176870 / 4098) und sim1 == sim2:", ok)
n = diff = halt = 0
for label, m in variants(CHAMP):
    a, b = run(SIM1, m, LIMIT), run(SIM2, m, LIMIT)
    n += 1; halt += a["halted"]
    if a != b:
        diff += 1; print("ABWEICHUNG", label, a, b)
print(f"Varianten: {n}, davon haltend (<= {LIMIT}): {halt}, Abweichungen sim1/sim2: {diff}")
sys.exit(0 if ok and diff == 0 else 1)
