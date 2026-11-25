"""Haltekandidat aus zyklus_beschl.py nachrechnen (Thread "Halt als verbotenes Muster").

Liest kandidat_<Start>_<n>.txt.gz (oder die BASE64-Zeile aus dem Actions-Log, Option -b) und rechnet ab dem
Schnappschuss Phase fuer Phase mit dem Durchlaufmodell (rueckfall_gezaehlt aus zaehl_beschl.py, ohne jede
Regel). Ausgabe je Phase: n, r, Tokenzahl; am Ende Halt ja/nein und K(C)-Zaehlung.
Aufruf: python3 -I kandidat_nachrechnen.py <datei.gz | -b BASE64> [phasen]"""
import base64
import gzip
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "linkes_ende"))
sys.path.insert(0, HIER)
import beschleuniger as bs  # noqa: E402
import zaehl_beschl as zb  # noqa: E402
from zaehl_durchlauf import Zaehler  # noqa: E402


def lies(text):
    kopf, liste = text.strip().split("\n")[:2]
    f = dict(x.split("=", 1) for x in kopf.split())
    teile, tail = liste.rsplit("/", 1)
    tok = []
    for w in teile.split():
        t, n = w.split(":")
        tok.append(("" if t == "_" else t, int(n)))
    return f["start"], int(f["n"]), int(f["r"]), tok, tail


def main():
    if sys.argv[1] == "-b":
        text = gzip.decompress(base64.b64decode(sys.argv[2])).decode()
        rest = sys.argv[3:]
    else:
        with gzip.open(sys.argv[1], "rt") as f:
            text = f.read()
        rest = sys.argv[2:]
    phasen = int(rest[0]) if rest else 3
    start, n, r, tok, tail = lies(text)
    print(f"Schnappschuss: Start {start}, n={n}, r={r}, {len(tok)} Token")
    zb.Z = {"ueb": Zaehler(), "vs": Zaehler(), "na": Zaehler()}
    zb.PH = {"ueb": 0, "vs": 0, "na": 0}
    halt = None
    for i in range(phasen):
        try:
            tok, tail, r, dn, _ = zb.rueckfall_gezaehlt(tok, tail, r)
        except bs.Halt as h:
            halt = n + h.args[0]
            break
        n += dn
        print(f"Phase {i + 1}: n={n} r={r} Token={len(tok)}")
    kc = sum(z.t.get((2, "011"), 0) for z in zb.Z.values())
    print(f"Halt: {'JA bei n=' + str(halt) if halt is not None else 'nein'}   K(C) in den gerechneten Phasen: {kc}")


main()
