#!/usr/bin/env python3
"""Analyse 318/518 (Python-Teil). Nur Beschreibung, kein Beweis.

  m5analyse.py abbild <BB6_holdouts_608.txt> <holdouts.json>
      Sucht in der Liste und in "decided" alle Maschinen, deren Tabelle sich auf die
      5-Zustands-Maschine M5 abbilden laesst (Zustaende zusammenlegen, mit/ohne Spiegelung),
      und gibt Start in M5 und das Haltemuster in M5 aus.
  m5analyse.py regeln <zyklen-datei>
      Zerlegt das Band an jedem Zyklusbeginn in Bausteine und prueft die Zaehlerregeln.
  m5analyse.py umbau <zyklen-datei>
      Listet die Zyklen, an denen sich der Aufbau (linker Rest, Zahl der Ziffern) aendert.
  m5analyse.py treffen <zyklen-datei-1> <zyklen-datei-2>
      Erster Zyklusbeginn, an dem beide Laeufe dieselbe Konfiguration haben (Zustand und Band
      ohne fuehrende Nullen; der Kopf steht jeweils rechts vom Band auf einer leeren Zelle).
  m5analyse.py negativ <zyklen-datei>
      Negativkontrollen fuer abbild und regeln.

<zyklen-datei>: Ausgabe von "m5sim zyklen ..." bzw. "zweitpruefung zyklen ..." (Zeilen: Schritt Zustand Band).
"""
import itertools
import json
import sys
from collections import Counter

M5 = "1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC"


def tabelle(s):
    t = {}
    for i, g in enumerate(s.split("_")):
        for b in range(2):
            u = g[3 * b:3 * b + 3]
            t[(i, b)] = None if u == "---" else (int(u[0]), u[1], ord(u[2]) - 65)
    return t


def abbildungen(s, ziel=M5):
    """Alle (gespiegelt, f) mit f: Zustaende von s -> Zustaende von M5."""
    t, z = tabelle(s), tabelle(ziel)
    n, k = len(s.split("_")), len(ziel.split("_"))
    erg = []
    for sp in (False, True):
        for f in itertools.product(range(k), repeat=n):
            if all(u is None or z[(f[q], b)] == (u[0], ("L" if u[1] == "R" else "R") if sp else u[1], f[u[2]])
                   for (q, b), u in t.items()):
                erg.append((sp, f))
    return erg


def haltemuster(s, f):
    t = tabelle(s)
    aus = []
    for (q, b), u in t.items():
        if u is None:
            vor = [f"{chr(65 + p)}{c}" for (p, c), v in t.items() if v is not None and v[2] == q]
            aus.append((f"{chr(65 + q)}{b}", [f"{chr(65 + f[int(ord(x[0]) - 65)])}{x[1]}" for x in vor]))
    return aus


def cmd_abbild(liste, js):
    lst = [l.strip() for l in open(liste) if l.strip()]
    dec = [d["tm"] for d in json.load(open(js))["decided"]]
    for name, ms in (("Liste", lst), ("decided", dec)):
        treffer = 0
        for n, s in enumerate(ms, 1):
            for sp, f in abbildungen(s):
                treffer += 1
                for h, vor in haltemuster(s, f):
                    print(f"{name} n={n} {s} {'gespiegelt' if sp else 'ungespiegelt'} "
                          f"Bild={''.join(chr(65 + x) for x in f)} Start in M5={chr(65 + f[0])} "
                          f"Halt bei {h}; davor in M5: {', '.join(vor)}")
        print(f"{name}: {len(ms)} Maschinen, {treffer} Abbildungen auf M5")


# Bausteine an Zyklusbeginn, als Folge der Einser-Laengen (getrennt durch einzelne Nullen)
BAUSTEINE = [("D2", (1, 1, 7, 1)), ("D1", (1, 9, 1)), ("U", (5, 1)), ("Z", (3, 1)), ("D3", (11, 1)), ("W", (7, 1))]
PHASE = {"Z": 0, "D1": 1, "D2": 2, "D3": 3}


def zerlege(band):
    """Von rechts nach links in Bausteine zerlegen; was links uebrig bleibt, ist der linke Rest."""
    r = [len(x) for x in band.split("0")]
    ende, r = r[-1], r[:-1]
    i, aus = len(r), []
    while i > 0:
        for name, muster in BAUSTEINE:
            k = len(muster)
            if i >= k and tuple(r[i - k:i]) == muster:
                aus.append(name)
                i -= k
                break
        else:
            break
    return tuple(r[:i]), aus[::-1], ende


def lies_zyklen(datei):
    for zeile in open(datei):
        teile = zeile.split()
        if len(teile) == 3:
            yield int(teile[0]), teile[1], teile[2]


def pruefe_regeln(zyklen):
    """zyklen: Liste (Schritt, Band). Gibt Zaehler zurueck."""
    z = Counter()
    ausn = []
    vorher = None
    for schritt, band in zyklen:
        rest, bs, ende = zerlege(band)
        sym = [b for b in bs if b != "U"]
        cur = (schritt, rest, sym, len(band))
        if vorher is None:
            vorher = cur
            continue
        a, b = vorher, cur
        vorher = cur
        if a[1] != b[1] or len(a[2]) != len(b[2]):
            z["Aufbau geaendert (nicht geprueft)"] += 1
            continue
        z["Zyklenpaare geprueft"] += 1
        if any((x == "W") != (y == "W") for x, y in zip(a[2], b[2])):
            z["W verschoben"] += 1
        ziff = [i for i, x in enumerate(a[2]) if x != "W"]
        d = [(PHASE[a[2][i]], (PHASE[b[2][i]] - PHASE[a[2][i]]) % 4) for i in reversed(ziff)]
        ok = True
        if not d:
            continue
        if d[0][1] != 1:
            z["Regel 1 verletzt (rechte Ziffer nicht +1)"] += 1
            ok = False
        if any(x[1] not in (0, 1) for x in d):
            z["Regel 2 verletzt (Ziffer springt)"] += 1
            ok = False
        for j in range(len(d) - 1):
            ausl = d[j][1] == 1 and d[j][0] in (2, 3)
            if ausl == (d[j + 1][1] == 1):
                z["Regel 3 passend"] += 1
            else:
                z["Regel 3 verletzt"] += 1
                ok = False
        if b[3] - a[3] == 4:
            z["Breite +4"] += 1
        else:
            z["Breite nicht +4"] += 1
            ok = False
        if not ok:
            ausn.append(b[0])
    return z, ausn


def cmd_regeln(datei):
    z, ausn = pruefe_regeln([(s, b) for s, _, b in lies_zyklen(datei)])
    for k in sorted(z):
        print(f"{k}: {z[k]}")
    print("Zyklen mit Abweichung (Schritt):", ausn[:50], "..." if len(ausn) > 50 else "")
    return z


def kurz(rest, bs):
    out = []
    for b in bs:
        if b == "U" and out and out[-1][0] == "U":
            out[-1] = ("U", out[-1][1] + 1)
        elif b == "U":
            out.append(("U", 1))
        else:
            out.append((b, 0))
    return "Rest(" + ".".join(map(str, rest)) + ") " + " ".join(x if x != "U" else f"U^{k}" for x, k in out)


def cmd_umbau(datei):
    vorher = None
    n = 0
    for schritt, _, band in lies_zyklen(datei):
        rest, bs, _ = zerlege(band)
        sym = [b for b in bs if b != "U"]
        if vorher and (vorher[1] != rest or len(vorher[2]) != len(sym)):
            n += 1
            print(f"{vorher[0]} -> {schritt}  Breite {vorher[3]} -> {len(band)}  Ziffern+W {len(vorher[2])} -> {len(sym)}")
            print("   vorher:", vorher[4][:400])
            print("   nachher:", kurz(rest, bs)[:400])
        vorher = (schritt, rest, sym, len(band), kurz(rest, bs))
    print("Aufbauwechsel:", n)


def treffen(d1, d2):
    erst = {}
    for schritt, q, band in lies_zyklen(d1):
        erst.setdefault((q, band.lstrip("0")), schritt)
    gem, erster = 0, None
    for schritt, q, band in lies_zyklen(d2):
        k = (q, band.lstrip("0"))
        if k in erst:
            gem += 1
            if erster is None:
                erster = (erst[k], schritt, len(k[1]))
    return gem, erster


def cmd_treffen(d1, d2):
    gem, erster = treffen(d1, d2)
    if erster:
        print(f"gemeinsame Zyklusbeginne: {gem}; erster: Schritt {erster[0]} (Datei 1) = Schritt {erster[1]} (Datei 2), Breite {erster[2]}")
    else:
        print("keine gemeinsame Konfiguration an Zyklusbeginnen")


def cmd_negativ(datei):
    ok = True
    # 1. Abbildung: 518 mit E0=1RA statt 0RA darf keine Abbildung haben; 518 selbst muss eine haben.
    n1 = len(abbildungen("1RB0LD_0RC1RA_1RD1RF_1LA0LE_1RA0LC_0RA---"))
    n0 = len(abbildungen("1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---"))
    print(f"Negativ 1: 518 hat {n0} Abbildung(en), 518 mit E0=1RA hat {n1} (erwartet 1 und 0)")
    ok &= (n0 == 1 and n1 == 0)
    # 2. Regeln: in einem Zyklus mitten im Lauf eine innere Ziffer D1 <-> D2 vertauschen.
    zyk = [(s, b) for s, _, b in lies_zyklen(datei)]
    z0, _ = pruefe_regeln(zyk)
    mitte = len(zyk) // 2
    s, b = zyk[mitte]
    j = b.rfind("01011111111101")  # 0 + D1 (1.9.1) + Rest, von rechts
    if j < 0:
        print("Negativ 2: keine D1-Ziffer im Zyklus gefunden, Kontrolle nicht durchfuehrbar")
        ok = False
    else:
        # D1 = 1 0 1^9 0 1 0 -> D2 = 1 0 1 0 1^7 0 1 0 (gleiche Laenge)
        b2 = b[:j + 1] + "10101111111" + b[j + 1 + 11:]
        assert len(b2) == len(b)
        zyk2 = list(zyk)
        zyk2[mitte] = (s, b2)
        z1, _ = pruefe_regeln(zyk2)
        v0 = z0["Regel 1 verletzt (rechte Ziffer nicht +1)"] + z0["Regel 2 verletzt (Ziffer springt)"] + z0["Regel 3 verletzt"]
        v1 = z1["Regel 1 verletzt (rechte Ziffer nicht +1)"] + z1["Regel 2 verletzt (Ziffer springt)"] + z1["Regel 3 verletzt"]
        print(f"Negativ 2: Verletzungen ohne Eingriff {v0}, mit vertauschter Ziffer in Schritt {s}: {v1} (erwartet mehr)")
        ok &= v1 > v0
    print("Negativkontrollen:", "alle schlagen an" if ok else "FEHLER")


if __name__ == "__main__":
    a = sys.argv
    if len(a) >= 4 and a[1] == "abbild":
        cmd_abbild(a[2], a[3])
    elif len(a) >= 3 and a[1] == "regeln":
        cmd_regeln(a[2])
    elif len(a) >= 3 and a[1] == "umbau":
        cmd_umbau(a[2])
    elif len(a) >= 4 and a[1] == "treffen":
        cmd_treffen(a[2], a[3])
    elif len(a) >= 3 and a[1] == "negativ":
        cmd_negativ(a[2])
    else:
        print(__doc__)
        sys.exit(2)
