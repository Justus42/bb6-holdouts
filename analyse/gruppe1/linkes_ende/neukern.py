"""Zeigt zu jedem Kern das erste Auftreten (Schritt, Datei, Form) und je Zehnerpotenz die Zahl der
"alt"-Faelle. Fuer Kerne, die erst ab <ab> (Vorgabe 1e15) zum ersten Mal auftreten, alle Faelle mit Form.
Aufruf: python3 neukern.py <rueckfall-Dateien> [--ab 1e15]"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from formen import saetze, kern, form

args = sys.argv[1:]
ab = 1e15
if "--ab" in args:
    i = args.index("--ab"); ab = float(args[i + 1]); del args[i:i + 2]
ev = []
for fn in args:
    for n, art, X, xt, Y, yt in saetze(fn):
        ev.append((n, os.path.basename(fn), art, kern(art, X, xt, Y, yt), form(art, X, xt, Y, yt)[0]))
ev.sort()
erst = {}
for e in ev:
    erst.setdefault(e[3], e)
print("Kern | erstes Auftreten | Datei | Art | Form (gekuerzt)")
for k, e in sorted(erst.items(), key=lambda kv: kv[1][0]):
    print("%-22s %.3e %s %s  %s" % (k, e[0], e[1], e[2], e[4][:200]))
alt = {}
for n, fn, art, k, f in ev:
    d = len(str(n)) - 1
    a = alt.setdefault(d, [0, 0])
    a[0] += 1
    if " alt " in " " + k + " ":
        a[1] += 1
print("alt-Faelle je Zehnerpotenz (Faelle, davon alt):", {"10^%d" % d: tuple(v) for d, v in sorted(alt.items())})
neu = {k for k, e in erst.items() if e[0] >= ab}
print("Faelle der Kerne mit erstem Auftreten ab %.0e:" % ab)
for n, fn, art, k, f in ev:
    if k in neu:
        print("  %.3e %s %s %s  %s" % (n, fn, art, k, f[:300]))
