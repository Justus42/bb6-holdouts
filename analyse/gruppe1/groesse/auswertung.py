"""Auswertung der Aenderungsvektoren aus groesse.py / groesse2.c.

Eingabe: eine oder mehrere Dateien "Klasse | dS dm dz du dq dr dx dy dL | Anzahl" (Starts werden addiert).
Ausgabe:
  1. je Klasse und Kandidat: "0" (bleibt gleich), "+c" (fester Betrag) oder "var a..b (k Werte)"
     (aendert sich je nach Lage), dazu einige feste Kombinationen (S+r, x+4y, L).
  2. gewichtete Kombinationen: alle ganzzahligen Gewichte w mit w . d = 0 fuer jeden beobachteten
     Vektor d (Nullraum ueber Q, gekuerzt), je Klasse und fuer Gruppen von Klassen; ebenso modulo 2.
Aufruf: python3 auswertung.py <datei> [<datei> ...]
Negativkontrolle: AUSW_KONTROLLE=1 haengt eine kuenstliche Groesse K = S + r als zehnte Spalte an; sie
  muss in allen Klassen mit dS + dr = 0 als "0" erscheinen und im Nullraum als S + r - K auftauchen.
"""
import os
import sys
from collections import defaultdict
from fractions import Fraction
from math import gcd

NAMEN = ["S", "m", "z", "u", "q", "r", "x", "y"]   # Basis fuer den Nullraum (L ist S, m, r plus Trenner)
ALLE = NAMEN + ["L"]
KONTROLLE = os.environ.get("AUSW_KONTROLLE") == "1"
if KONTROLLE:
    NAMEN = NAMEN + ["K"]
    ALLE = ALLE + ["K"]


def lies(dateien):
    d = defaultdict(lambda: defaultdict(int))
    for fn in dateien:
        for z in open(fn):
            kl, v, c = z.rstrip("\n").split(" | ")
            v = tuple(int(x) for x in v.split())
            if KONTROLLE:
                v = v + (v[0] + v[5],)
            d[kl][v] += int(c)
    return d


def gruppe(kl):
    if kl in ("N1", "N2", "N2s", "UA", "LE0", "LE1", "LG"):
        return "Automat"
    if kl == "VS":
        return "VS"
    if kl.startswith("Kern:"):
        return "linkes Ende"
    return "Uebergang"


def einordnen(werte):
    w = sorted(set(werte))
    if w == [0]:
        return "0"
    if len(w) == 1:
        return "%+d" % w[0]
    return "var %d..%d (%d)" % (w[0], w[-1], len(w))


def nullraum(vektoren, p=None):
    """Basis des Nullraums {w : w.v = 0 fuer alle v}; p=None ueber Q (ganzzahlig gekuerzt), sonst mod p."""
    k = len(NAMEN)
    zeilen = []
    for v in vektoren:
        zeilen.append([Fraction(x) if p is None else x % p for x in v[:len(NAMEN)]] if not KONTROLLE
                      else [Fraction(x) if p is None else x % p for x in (v[:8] + (v[9],))])
    # Gauss auf den Zeilen (Bedingungen), freie Variablen -> Basis
    A = [list(z) for z in zeilen]
    piv = []
    zr = 0
    for c in range(k):
        pr = None
        for i in range(zr, len(A)):
            if A[i][c] != 0:
                pr = i
                break
        if pr is None:
            continue
        A[zr], A[pr] = A[pr], A[zr]
        if p is None:
            f = A[zr][c]
            A[zr] = [x / f for x in A[zr]]
        else:
            f = pow(A[zr][c], -1, p)
            A[zr] = [(x * f) % p for x in A[zr]]
        for i in range(len(A)):
            if i != zr and A[i][c] != 0:
                g = A[i][c]
                A[i] = [(a - g * b) if p is None else (a - g * b) % p for a, b in zip(A[i], A[zr])]
        piv.append(c)
        zr += 1
        if zr == len(A):
            break
    frei = [c for c in range(k) if c not in piv]
    basis = []
    for fc in frei:
        w = [Fraction(0) if p is None else 0] * k
        w[fc] = Fraction(1) if p is None else 1
        for i, c in enumerate(piv):
            w[c] = -A[i][fc] if p is None else (-A[i][fc]) % p
        if p is None:
            nenner = 1
            for x in w:
                nenner = nenner * x.denominator // gcd(nenner, x.denominator)
            w = [int(x * nenner) for x in w]
            g = 0
            for x in w:
                g = gcd(g, abs(x))
            w = [x // g for x in w]
            if next(x for x in w if x != 0) < 0:
                w = [-x for x in w]
        basis.append(w)
    return basis


def schreib(w):
    teile = []
    for c, n in zip(w, NAMEN):
        if c == 0:
            continue
        if c == 1:
            teile.append("+" + n)
        elif c == -1:
            teile.append("-" + n)
        else:
            teile.append("%+d%s" % (c, n))
    s = " ".join(teile)
    return s[1:] if s.startswith("+") else s


def main(dateien):
    d = lies(dateien)
    reihen = sorted(d, key=lambda k: (["Automat", "VS", "Uebergang", "linkes Ende"].index(gruppe(k)), k))
    print("== 1. Aenderung je Klasse (0 = bleibt gleich, +c = fester Betrag, var a..b (k) = k verschiedene Werte)")
    kopf = "%-26s %9s  " % ("Klasse", "Faelle") + " ".join("%-15s" % n for n in ALLE) + \
        " %-15s %-15s" % ("S+r", "x+4y")
    print(kopf)
    for kl in reihen:
        V = d[kl]
        anz = sum(V.values())
        spalten = [einordnen([v[i] for v in V]) for i in range(len(ALLE))]
        spalten.append(einordnen([v[0] + v[5] for v in V]))
        spalten.append(einordnen([v[6] + 4 * v[7] for v in V]))
        print("%-26s %9d  " % (kl, anz) + " ".join("%-15s" % s for s in spalten))
    print()
    print("== 2. Gewichtete Kombinationen, die in jedem beobachteten Fall gleich bleiben (Nullraum-Basis)")
    gruppen = defaultdict(list)
    for kl in reihen:
        gruppen[gruppe(kl)].append(kl)
    auswahl = [(kl, [kl]) for kl in reihen]
    auswahl += [("GRUPPE Automat (N1 N2 N2s UA LE0 LE1 LG)", gruppen["Automat"]),
                ("GRUPPE N1 N2 N2s UA (Inneres)", ["N1", "N2", "N2s", "UA"]),
                ("GRUPPE Automat + VS", gruppen["Automat"] + gruppen["VS"]),
                ("GRUPPE Uebergang gesamt", ["Ueb gesamt"]),
                ("GRUPPE alle Phasen (Automat, VS, linkes Ende)", gruppen["Automat"] + gruppen["VS"] +
                 gruppen["linkes Ende"]),
                ("GRUPPE alles (mit Uebergaengen gesamt)", gruppen["Automat"] + gruppen["VS"] +
                 gruppen["linkes Ende"] + ["Ueb gesamt"])]
    for name, kls in auswahl:
        vek = [v for kl in kls if kl in d for v in d[kl]]
        if not vek:
            continue
        q = nullraum(vek)
        z = nullraum(vek, 2)
        print("%-46s Q: %s" % (name, "; ".join(schreib(w) for w in q) if q else "keine"))
        print("%-46s mod 2: %s" % ("", "; ".join(schreib(w) for w in z) if z else "keine"))


if __name__ == "__main__":
    main(sys.argv[1:])
