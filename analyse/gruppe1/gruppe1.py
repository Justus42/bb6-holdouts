#!/usr/bin/env python3
"""Analyse Gruppe 1 (n=114, 367, 378). Nur Simulation und Beschreibung, kein Beweis.

Aufrufe (alle ohne Netz, nur Standardbibliothek):
  gruppe1.py aequivalenz            367 und 378 Schritt fuer Schritt gegen die Tabelle von 114 pruefen
  gruppe1.py bloecke                Durchlaufregeln ueber 3er-Bloecke und Haltebedingung ausgeben
  gruppe1.py liste <schritte> [S]   Liste bei jedem Rechts-Rekord in Zustand C (Tabelle 114, Start S)
                                    im selben Format wie zweitpruefung.c ausgeben
  gruppe1.py pruefe <listendatei>   Fressregel, Zyklusregel x=a+4b+7 und +2-Regel gegen eine Listendatei pruefen
  gruppe1.py pin <busycoq/verify>   Maschinen aus PR_Loop4Mono.v und Loop4Mono*.v gegen Gruppe 1 pruefen
  gruppe1.py negativ <listendatei>  Negativkontrollen: jede Pruefung muss bei absichtlich falschen Daten anschlagen

Bandkonvention wie bbchallenge: Start auf Leerband, "---" ist der Halteuebergang.
"""
import re
import sys
import itertools

M114 = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
M367 = "1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB"
M378 = "1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---"
S = "ABCDEF"


def parse(m):
    t = {}
    for i, g in enumerate(m.split("_")):
        for s in (0, 1):
            x = g[3 * s:3 * s + 3]
            t[(S[i], s)] = None if x == "---" else (int(x[0]), 1 if x[1] == "R" else -1, x[2])
    return t


def run(m, start, n_steps, mirror=False):
    """Erzeugt (zustand, kopf, band-dict) nach jedem Schritt; mirror spiegelt die Richtung."""
    t = parse(m)
    tape, p, q = {}, 0, start
    for _ in range(n_steps):
        tr = t[(q, tape.get(p, 0))]
        if tr is None:
            yield ("HALT", p, tape)
            return
        w, d, q = tr
        tape[p] = w
        p += -d if mirror else d
        yield (q, p, tape)


# ---------------------------------------------------------------- Aequivalenz
def find_map(m_from, m_to):
    """Sucht Umbenennung f (und Spiegelung) mit Tabelle(m_to)[f(q)] = f(Tabelle(m_from)[q])."""
    a, b = parse(m_from), parse(m_to)
    hits = []
    for perm in itertools.permutations(S):
        f = dict(zip(S, perm))
        for mir in (False, True):
            ok = True
            for q in S:
                for s in (0, 1):
                    x, y = a[(q, s)], b[(f[q], s)]
                    if (x is None) != (y is None):
                        ok = False
                    elif x is not None and (y[0] != x[0] or y[2] != f[x[2]] or y[1] != (-x[1] if mir else x[1])):
                        ok = False
            if ok:
                hits.append((f, mir))
    return hits


def aequivalenz(n_steps=1_000_000, paare=None):
    for name, m in (paare or (("367", M367), ("378", M378))):
        for f, mir in find_map(M114, m):
            inv = {v: k for k, v in f.items()}
            start114 = inv["A"]
            print(f"n={name}: Tabelle 114 umbenannt {''.join(f[q] for q in S)} (A..F bei 114 -> dort), "
                  f"{'gespiegelt' if mir else 'ungespiegelt'}; Start A dort = Zustand {start114} bei 114")
            g1 = run(M114, start114, n_steps)
            g2 = run(m, "A", n_steps)
            k = 0
            for (q1, p1, t1), (q2, p2, t2) in zip(g1, g2):
                k += 1
                pp = -p1 if mir else p1
                if (q1 == "HALT") != (q2 == "HALT") or (q1 != "HALT" and f[q1] != q2) or pp != p2:
                    print("  ABWEICHUNG bei Schritt", k)
                    break
                if k % 100_000 == 0:
                    t1m = {(-x if mir else x): v for x, v in t1.items() if v}
                    if t1m != {x: v for x, v in t2.items() if v}:
                        print("  BAND-ABWEICHUNG bei Schritt", k)
                        break
            else:
                print(f"  {k} Schritte gleich (Zustand, Kopf; Band alle 100.000 Schritte verglichen)")


# ---------------------------------------------------------------- Bloecke
def cross(t, w, q, side, maxn=1000):
    tape = list(w)
    p = 0 if side == "L" else len(w) - 1
    n = 0
    while 0 <= p < len(tape) and n < maxn:
        tr = t[(q, tape[p])]
        if tr is None:
            return None
        wr, d, q = tr
        tape[p] = wr
        p += d
        n += 1
    if 0 <= p < len(tape):
        return None
    return ("R" if p >= len(tape) else "L", q, "".join(map(str, tape)), n)


def bloecke():
    t = parse(M114)
    print("Durchlaufregeln der Tabelle von 114 ueber 3er-Bloecke (Kopf tritt ein und auf der anderen Seite aus):")
    for w in itertools.product((0, 1), repeat=3):
        ws = "".join(map(str, w))
        for q in S:
            for side in "LR":
                r = cross(t, list(w), q, side)
                if r and r[0] != side:
                    if side == "L":
                        print(f"  {q}> {ws}  ->  {r[2]} {r[1]}>   ({r[3]} Schritte)")
                    else:
                        print(f"  {ws} <{q}  ->  <{r[1]} {r[2]}   ({r[3]} Schritte)")
    print("Halteuebergang: A1. Uebergaenge nach A:",
          [f"{q}{s}" for q in S for s in (0, 1) if t[(q, s)] and t[(q, s)][2] == "A"],
          " nach E:", [f"{q}{s}" for q in S for s in (0, 1) if t[(q, s)] and t[(q, s)][2] == "E"])


# ---------------------------------------------------------------- Listen
def liste(n_steps, start="A", out=sys.stdout):
    t = parse(M114)
    size = n_steps // 2 + 1000
    tape = bytearray(size)
    p = size // 2
    lo = hi = p
    q = start
    for n in range(n_steps):
        tr = t[(q, tape[p])]
        if tr is None:
            out.write(f"HALT {n}\n")
            return
        w, d, q = tr
        tape[p] = w
        p += d
        lo = min(lo, p)
        if p > hi:
            hi = p
            if q == "C":
                z = [i for i in range(hi, lo - 1, -1) if tape[i] == 0]
                parts, k = [], 0
                for a, b in zip(z, z[1:]):
                    g = a - b
                    if g == 3:
                        k += 1
                    else:
                        parts.append(f"{k} |" if g == 4 else f"{k} <{g}>")
                        k = 0
                parts.append(str(k))
                out.write(f"{n + 1} C {hi - lo + 1} lead {hi - z[0]} | " + " ".join(parts) + "\n")


def lese(fn):
    L = [l.rstrip("\n") for l in open(fn)]
    steps = [int(l.split()[0]) for l in L]
    return L, steps


def body(l):
    return l.split("|", 1)[1].strip()


def zahlen(l):
    return [int(x) for x in body(l).split() if x != "|" and not x.startswith("<")]


def zyklusanfaenge(steps):
    """Index des ersten C-Rechts-Rekords nach einem langen Lauf nach links (Zyklusende)."""
    return [i for i in range(2, len(steps))
            if steps[i] - steps[i - 1] > 8 * (steps[i - 1] - steps[i - 2]) and steps[i] - steps[i - 1] > 5000]


def pruefe(fn):
    L, steps = lese(fn)
    anf = zyklusanfaenge(steps)
    anfset = set(anf)
    # Fressregel
    ok, bad, bad_anf = 0, 0, 0
    rx = re.compile(r"(\d+) (\||<\d+>) (\d+)(.*)$")
    sp = [rx.match(body(l)) for l in L]
    for i in range(len(L) - 3):
        g = sp[i]
        if not g or g.group(2) != "|" or int(g.group(3)) < 1:
            continue
        x, y, rest = int(g.group(1)), int(g.group(3)), g.group(4)
        exp = [(x + 2, "<1>", y), (x + 3, "<1>", y), (x + 4, "|", y - 1)]
        good = True
        for j, e in zip((1, 2, 3), exp):
            h = sp[i + j]
            if not h or (int(h.group(1)), h.group(2), int(h.group(3))) != e or h.group(4) != rest:
                good = False
        if good:
            ok += 1
        else:
            bad += 1
            bad_anf += i in anfset
    print(f"Fressregel: {ok} Runden passen, {bad} nicht (davon {bad_anf} erste Runde eines Zyklus)")
    # Zyklusregel x = a + 4b + 7 und +2-Regel
    okx, badx, rows = 0, [], []
    for c0, c1 in zip(anf, anf[1:]):
        a, b = zahlen(L[c0])[:2]
        before = zahlen(L[c1 - 1])
        x, mid = before[0], before[1:]
        after = zahlen(L[c1])
        if x == a + 4 * b + 7:
            okx += 1
        else:
            badx.append(steps[c1 - 1])
        k = 0
        while k < min(len(after), len(mid)) and after[k] == mid[k] + 2:
            k += 1
        rows.append((steps[c1 - 1], x, len(mid), k))
    print(f"Zyklen: {len(anf)}; Zyklusregel x = a+4b+7 passt {okx}, weicht ab {len(badx)} {badx[:5]}")
    print("letzte Zyklen (Schritt, x, Listenlaenge, Laenge des +2-Praefix):")
    for r in rows[-5:]:
        print("  ", *r)
    from collections import Counter
    print("Verteilung (+2-Praefix minus x//2):", sorted(Counter(r[3] - r[1] // 2 for r in rows).items()))


# ---------------------------------------------------------------- Pin
def kanon(m):
    """Kleinste Darstellung unter Umbenennung (Start beliebig) und Spiegelung: Menge der Tabellen."""
    t = parse(m)
    forms = set()
    for perm in itertools.permutations(S):
        f = dict(zip(S, perm))
        for mir in (False, True):
            rows = {}
            for q in S:
                cells = []
                for s in (0, 1):
                    x = t[(q, s)]
                    cells.append("---" if x is None else f"{x[0]}{'R' if (x[1] == 1) != mir else 'L'}{f[x[2]]}")
                rows[f[q]] = "".join(cells)
            forms.add("_".join(rows[q] for q in S))
    return min(forms)


def pin(verify):
    import glob
    import os
    ziel = kanon(M114)
    for m in (M367, M378):
        assert kanon(m) == ziel
    files = sorted(glob.glob(os.path.join(verify, "Loop4Mono*.v")))
    files = [f for f in files if "2x5" not in f] + [os.path.join(verify, "PR_Loop4Mono.v")]
    for fn in files:
        tms = re.findall(r'TM_from_str\s+"([^"]+)"', open(fn).read())
        andere = [m for m in tms if not re.fullmatch(r"([01][LR][A-F]|---){2}(_([01][LR][A-F]|---){2}){5}", m)]
        tms = [m for m in tms if m not in andere]
        if andere:
            print(f"{os.path.basename(fn)}: {len(andere)} Maschinen nicht im Format 6 Zustaende/2 Symbole (uebersprungen)")
        treffer = [m for m in tms if kanon(m) == ziel]
        print(f"{os.path.basename(fn)}: {len(tms)} Maschinen, davon in Gruppe 1: {len(treffer)}")


def negativ(fn):
    import io
    import os
    import tempfile
    import contextlib
    print("1) Aequivalenz gegen 367 mit einem geaenderten Uebergang (D0 1RA -> 0RA):")
    falsch = M367.replace("1RA1RE", "0RA1RE")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        aequivalenz(200_000, (("367*", falsch),))
    out = buf.getvalue()
    # Mit falscher Tabelle gibt es keine Umbenennung mehr; erzwingen ueber die echte Zuordnung:
    if not out.strip():
        f, mir = find_map(M114, M367)[0]
        g1, g2 = run(M114, "D", 200_000), run(falsch, "A", 200_000)
        k = 0
        for (q1, p1, _), (q2, p2, _) in zip(g1, g2):
            k += 1
            if q1 == "HALT" or q2 == "HALT" or f[q1] != q2 or p1 != p2:
                out = f"keine Umbenennung gefunden; Schrittvergleich weicht bei Schritt {k} ab"
                break
        else:
            out = "NICHT ERKANNT"
    print("   ", out.strip().replace("\n", " / "))
    print("2) Listendatei mit einer veraenderten Zahl mitten in einer Fressrunde (Form x <1> y):")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        pruefe(fn)
    print("    unveraendert:", buf.getvalue().splitlines()[0])
    L = open(fn).read().split("\n")
    rx = re.compile(r"(\d+) <1> (\d+)(.*)$")
    for i, l in enumerate(L):
        m = rx.match(body(l)) if l else None
        vor = re.match(r"(\d+) \| (\d+)", body(L[i - 1])) if m and i > 0 else None
        if m and vor and int(vor.group(1)) + 2 == int(m.group(1)) and vor.group(2) == m.group(2) and i > 100:
            pre, b = l.split("|", 1)
            L[i] = pre + "| " + re.sub(r"^(\d+) <1> (\d+)", lambda mm: f"{mm.group(1)} <1> {int(mm.group(2)) + 1}", b.strip())
            break
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as tf:
        tf.write("\n".join(L))
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        pruefe(tf.name)
    os.unlink(tf.name)
    print("    veraendert:  ", buf.getvalue().splitlines()[0])
    print("3) Gruppensuche mit einer Datei, die 378 enthaelt:")
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "Loop4Mono_test.v"), "w").write('Definition tm := TM_from_str "%s".' % M378)
        open(os.path.join(d, "PR_Loop4Mono.v"), "w").write("")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pin(d)
        print("   ", buf.getvalue().splitlines()[0])


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "aequivalenz":
        aequivalenz()
    elif cmd == "bloecke":
        bloecke()
    elif cmd == "liste":
        liste(int(float(sys.argv[2])), sys.argv[3] if len(sys.argv) > 3 else "A")
    elif cmd == "pruefe":
        pruefe(sys.argv[2])
    elif cmd == "pin":
        pin(sys.argv[2])
    elif cmd == "negativ":
        negativ(sys.argv[2])
    else:
        print(__doc__)
