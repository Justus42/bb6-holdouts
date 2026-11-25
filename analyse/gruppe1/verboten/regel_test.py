"""Halteprüfung je Automatenregel (Thread "Halt als verbotenes Muster").

Für jede Regel des Phasen-Automaten (N1, N2, N2s, UA, LE0, LE1, LG) werden zufällige Token-Listen gebaut,
auf die genau diese Regel passt (Band.schritt aus beschleuniger.py entscheidet), mit zufälligem r >= 1,
zufälligen Zahlen (klein und groß) und zufälligem linkem Teil. Die Phase wird im Durchlaufmodell
gerechnet (gezählte Fassung von rueckfall aus zaehl_beschl.py). Geprüft wird:
  (a) Ergebnis = Vorhersage der Regel (Token-Liste, r' = r - 1, Schrittzahl = Kostenformel),
  (b) kein Ereignis K(C) (Zustand C tritt von links auf eine Zelle mit 0 1 1),
  (c) kein Halt.
Ausgegeben wird je Regel die Zahl der Proben, Fehler (a)/(b)/(c) und die Menge der vorkommenden
Rechtsschritt-Typen (Zustand, drei Zellen).
Aufruf: python3 -I regel_test.py <Proben je Regel> <seed>
Negativkontrolle: REGEL_FEHLER=1 nimmt ganz zufällige Listen ohne Regel-Bedingung; dann muss K(C) in
einem Teil der Proben auftreten (zeigt, dass die Erkennung anschlägt)."""
import os
import random
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "linkes_ende"))
sys.path.insert(0, HIER)
import beschleuniger as bs  # noqa: E402
import zaehl_beschl as zb  # noqa: E402
from zaehl_durchlauf import Zaehler  # noqa: E402

FEHLER = os.environ.get("REGEL_FEHLER", "")


def zahl(R, art):
    """art: 'o' ungerade >= 1, 'e' gerade >= 0, 'e+' gerade >= 2, 'p' >= 1, 'a' >= 0."""
    gross = R.random() < 0.15
    x = R.randint(0, 10**6 if gross else 15)
    if art == "o":
        return x | 1
    if art == "e":
        return x & ~1
    if art == "e+":
        return max(2, x & ~1)
    if art == "p":
        return max(1, x)
    return x


def zufalls_token(R):
    u = R.random()
    if u < 0.6:
        return ("1", zahl(R, "o"))
    if u < 0.75:
        return ("1", zahl(R, "e"))
    if u < 0.9:
        return ("0", zahl(R, "a"))
    return ("1", 0)


def baue(R, regel):
    """Liste von links nach rechts: links, Kern, Zone (regulär), rechtestes Token (1, gerade)."""
    links = [zufalls_token(R) for _ in range(R.randint(0, 6))]
    zone = [("1", zahl(R, "o")) for _ in range(R.randint(0, 8))]
    rechts = [("1", zahl(R, "e+"))]   # wie im Lauf: rechtestes Token (1, gerade >= 2)
    G = (R.choice("01"), zahl(R, "p"))
    if regel == "N1":
        kern = [("0", zahl(R, "e"))]
    elif regel == "N2":
        kern = [G, ("1", zahl(R, "e"))]
    elif regel == "N2s":
        kern = [G, ("0", zahl(R, "o"))]
    elif regel == "UA":
        kern = [G, ("1", 0), ("0", zahl(R, "o"))]
    elif regel == "LE0":
        links, kern = [], [("1", 0)]
    elif regel == "LE1":
        links, kern = [], [("1", 0), ("0", zahl(R, "o"))]
    elif regel == "LG":
        links, kern = [], []
        zone = [("1", zahl(R, "o")) for _ in range(R.randint(1, 8))]
    return links + kern + zone + rechts


def probe(R, regel):
    for _ in range(1000):
        tok = baue(R, regel)
        b = bs.Band(tok, "")
        g, kosten = b.schritt()
        if g == regel:
            break
    else:
        return None
    r = R.randint(1, 60) if R.random() < 0.8 else R.randint(1, 10**6)
    zb.Z = {"ueb": Zaehler(), "vs": Zaehler(), "na": Zaehler()}
    zb.PH = {"ueb": 0, "vs": 0, "na": 0}
    if FEHLER:
        tok = [zufalls_token(R) for _ in range(R.randint(1, 12))]
    try:
        t2, tl2, r2, dn, ln = zb.rueckfall_gezaehlt(tok, "", r, grenze=200000)
    except bs.Halt:
        return regel, "halt", None
    except zb.Endlos:
        return regel, "endlos", None
    z = zb.Z["na"].t
    for k, v in zb.Z["vs"].t.items():
        z[k] = z.get(k, 0) + v
    kc = z.get((2, "011"), 0)
    ok = (t2 == b.tok() and tl2 == "" and r2 == r - 1 and dn == kosten)
    return regel, ok, kc, set(z)


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    R = random.Random(seed)
    gesamt_kc = 0
    for regel in ("N1", "N2", "N2s", "UA", "LE0", "LE1", "LG"):
        n = falsch = kc = halt = 0
        typen = set()
        for _ in range(N):
            p = probe(R, regel)
            if p is None:
                continue
            n += 1
            if FEHLER and p[1] not in ("halt", "endlos"):
                kc += p[2] > 0
                continue
            if p[1] in ("halt", "endlos"):
                halt += 1
                continue
            _, ok, k, ty = p
            falsch += not ok
            kc += k > 0
            typen |= ty
        gesamt_kc += kc
        print(f"{regel:4s} Proben {n:6d}  Regel falsch {falsch}  mit K(C) {kc}  Halt/ohne Schnappschuss {halt}  "
              f"Typen: {' '.join('ABCDEF'[x] + '>' + z for x, z in sorted(typen))}")
    print("K(C) gesamt:", gesamt_kc)


main()
