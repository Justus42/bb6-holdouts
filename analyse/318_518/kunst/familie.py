#!/usr/bin/env python3
"""Umbau-Messung an kuenstlichen Baendern (Idee 1 der Lueckenkarte), Sammelprogramm.

Erzeugt die Eingabefamilie F aus BANDFAMILIE.md (fester Keim), laesst jedes Band mit `kunst umbau` laufen,
teilt das Ergebnis in die Klassen H/U/U-R/U-X/K/L ein und schreibt je Lauf eine JSON-Zeile.

Aufruf:
  familie.py <kunst-Programm> <ausgabe.jsonl> [--teil voll|W|gross|alle] [--rest RC1,RX,...] [--nur N]
  familie.py <kunst-Programm> --einzeln <band> [<zustand>]   (ein Band, Ausgabe auf stdout)
"""
import json
import os
import random
import subprocess
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from m5schnell import zerlege, TOK  # noqa: E402

RESTE = {
    "RC1": "11111111101011111111111110101011111111111010101111111111111010",
    "RX": "11111111101011111111111010111111101010111111111110",
}
KEIM = 20261126
MAXS = 10_000_000
K = 100
MAXZ = 5
PROG = None


def band_aus(rest, items, u, e):
    return rest + "".join(TOK["U"] * g + TOK[a] for a, g in items) + TOK["U"] * u + "1" * e


def familie(teile, reste):
    out = []
    if "voll" in teile:
        for rn in reste:
            for n in (1, 2, 3):
                def rek(pref):
                    if len(pref) == n:
                        yield list(pref)
                        return
                    for ph in ("D2", "D3"):
                        for g in range(6):
                            yield from rek(pref + [(ph, g)])
                for items in rek([]):
                    for u in (0, 1, 2):
                        for e in (0, 4):
                            out.append(("voll", rn, items, u, e))
    rnd = random.Random(KEIM)
    if "W" in teile:
        alle = []
        for rn in reste:
            for p1 in ("D2", "D3"):
                for p2 in ("D2", "D3"):
                    for g1 in range(6):
                        for g2 in range(6):
                            for u in (0, 1, 2):
                                for wp in (0, 1, 2):
                                    for wg in range(4):
                                        for e in (0, 4):
                                            it = [(p1, g1), (p2, g2)]
                                            it.insert(wp, ("W", wg))
                                            alle.append(("W", rn, it, u, e))
        out += rnd.sample(alle, 3000)
    if "gross" in teile:
        k = 0
        while k < 1500:
            rn = rnd.choice(reste)
            n = rnd.randint(4, 12)
            c = rnd.choice((1, 1.5, 2, 3))
            items = [(rnd.choice(("D2", "D3")), max(0, round(c * 2 ** i) + rnd.randint(-2, 2))) for i in range(n)]
            for _ in range(rnd.randint(0, 3)):
                items.insert(rnd.randint(0, len(items)), ("W", rnd.randint(0, 3)))
            u, e = rnd.randint(0, 3), rnd.choice((0, 4))
            if len(band_aus(RESTE[rn], items, u, e)) > 9000:
                continue
            out.append(("gross", rn, items, u, e))
            k += 1
    return out


def lage(m, versatz=0):
    """Bausteine eines Modells mit Anfangsposition (relativ zum Eingabeband)."""
    p = len(m.rest) + versatz
    res = []
    for a, u in m.items:
        p += 8 * u
        res.append((a, p))
        p += len(TOK[a])
    p += 8 * m.uende
    return res, p  # p = Lage des Endes (erste Zelle nach dem letzten U)


def laufe(band, zustand="A"):
    r = subprocess.run([PROG, "umbau", zustand, str(MAXS), str(K), str(MAXZ)], input=band + "\n",
                       capture_output=True, text=True, check=True).stdout.split("\n")
    zyk, mus, ende = [], {}, None
    for z in r:
        f = z.split()
        if not f:
            continue
        if f[0] == "Z":
            zyk.append((int(f[1]), f[2], int(f[3]), f[4]))
        elif f[0] == "MUSTER":
            mus[f[1]] = (int(f[2]), int(f[3]))
        elif f[0] == "ENDE":
            ende = (int(f[1]), f[2])
    return zyk, mus, ende


def auswerten(arg):
    idx, (teil, rn, items, u, e) = arg
    band = band_aus(RESTE[rn], items, u, e)
    zyk, mus, ende = laufe(band)
    d = {"id": idx, "teil": teil, "rest": rn, "items": items, "u": u, "e": e, "breite": len(band),
         "muster": mus, "ende": ende, "zyklen": [(s, z, lo, len(b)) for s, z, lo, b in zyk]}
    halt = mus.get("BA", (0, -1))[0] > 0 or mus.get("CE", (0, -1))[0] > 0
    if not zyk:
        d["klasse"] = "L"
    elif zyk[0][0] <= 10 * len(band):
        d["klasse"] = "K"
        m = zerlege(zyk[0][3])
        d["nach_kurz"] = m.kurz() if m else zyk[0][3][:120]
    else:
        d["dauer"] = zyk[0][0]
        nach = None
        for j, (s, z, lo, b) in enumerate(zyk):
            m = zerlege(b)
            if m is not None and len(m.rest) < 200:
                nach = (j, s, z, lo, m)
                break
        if nach is None:
            d["klasse"] = "U-X"
            d["nach_kurz"] = zyk[-1][3][:200]
        else:
            j, s, z, lo, m = nach
            d["klasse"] = "U" if m.rest in RESTE.values() else "U-R"
            d["nach_zyklus"], d["nach_schritt"], d["nach_zustand"], d["lo_rel"] = j, s, z, lo
            d["nach_rest"] = m.rest
            d["nach_items"] = m.items
            d["nach_uende"], d["nach_ende"] = m.uende, m.ende
            mv = zerlege(band)
            alt, alt_ende = lage(mv)
            neu, neu_ende = lage(m, lo)
            d["alt_lage"], d["alt_endlage"] = alt, alt_ende
            d["neu_lage"], d["neu_endlage"] = neu, neu_ende
            d["nach_kurz"] = m.kurz()
    d["halt"] = halt
    return d


def init(p):
    global PROG
    PROG = p


def main():
    global PROG
    PROG = sys.argv[1]
    if sys.argv[2] == "--einzeln":
        zyk, mus, ende = laufe(sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else "A")
        for s, z, lo, b in zyk:
            m = zerlege(b)
            print(s, z, lo, len(b), m.kurz() if m else "(nicht zerlegbar)")
        print(mus, ende)
        return
    ausg = sys.argv[2]
    teil = sys.argv[sys.argv.index("--teil") + 1] if "--teil" in sys.argv else "alle"
    teile = ("voll", "W", "gross") if teil == "alle" else (teil,)
    reste = sys.argv[sys.argv.index("--rest") + 1].split(",") if "--rest" in sys.argv else list(RESTE)
    fam = familie(teile, reste)
    if "--nur" in sys.argv:
        fam = fam[: int(sys.argv[sys.argv.index("--nur") + 1])]
    print(f"{len(fam)} Eingaben", file=sys.stderr)
    with Pool(4, initializer=init, initargs=(PROG,)) as pool, open(ausg, "w") as f:
        for d in pool.imap(auswerten, list(enumerate(fam)), chunksize=16):
            f.write(json.dumps(d) + "\n")


if __name__ == "__main__":
    main()
