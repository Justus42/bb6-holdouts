"""Halteprüfung je Automatenregel (Thread "Halt als verbotenes Muster").

Für jede Regel des Phasen-Automaten (N1, N2, N2s, UA, LE0, LE1, LG) werden zufällige Token-Listen gebaut,
kanonisch zerlegt wie im Lauf, auf die genau diese Regel passt (Band.schritt aus beschleuniger.py entscheidet), mit zufälligem r >= 1,
zufälligen Zahlen (klein und groß) und zufälligem linkem Teil. Die Phase wird im Durchlaufmodell
gerechnet (gezählte Fassung von rueckfall aus zaehl_beschl.py). Geprüft wird:
  (a) Ergebnis = Vorhersage der Regel (Token-Liste, r' = r - 1, Schrittzahl = Kostenformel),
  (b) kein Ereignis K(C) (Zustand C tritt von links auf eine Zelle mit 0 1 1),
  (c) kein Halt.
Ausgegeben wird je Regel die Zahl der Proben, Fehler (a)/(b)/(c) und die Menge der vorkommenden
Rechtsschritt-Typen (Zustand, drei Zellen).
Aufruf: python3 -I regel_test.py <Proben je Regel> <seed>
Negativkontrolle: REGEL_FEHLER=1 nimmt ganz zufällige linke Bänder (Bits) ohne Regel-Bedingung und rechnet
Phasen bis zum Halt; es muss Halte geben, und bei jedem muss K(C) erkannt werden (zeigt, dass Halt- und
K(C)-Erkennung anschlagen). Zufällige Token-Listen allein erzeugen weder Halt noch K(C)."""
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
    x = R.randint(0, 10**5 if gross else 15)
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


def kanonisch(tok):
    """Wie im Lauf: Token-Liste aus den Bits neu zerlegen (canon). Zufaellige Listen sind sonst oft nicht
    kanonisch, z. B. (0,0) (1,0) (1,n) = Bits 0 1 1 011^n, also ein Block mehr."""
    t, rest = bs.canon(bs.bits_aus_l(bs.l_aus_token(tok, "")))
    return t if rest == "" and all(x[0] != "" for x in t) else None


def bits(tok):
    return bs.bits_aus_l(bs.l_aus_token(tok, ""))


def probe(R, regel):
    for _ in range(1000):
        tok = kanonisch(baue(R, regel))
        if tok is None:
            continue
        b = bs.Band(tok, "")
        g, kosten = b.schritt()
        if g == regel:
            break
    else:
        return None
    r = R.randint(1, 60) if R.random() < 0.8 else R.randint(1, 10**6)
    zb.Z = {"ueb": Zaehler(), "vs": Zaehler(), "na": Zaehler()}
    zb.PH = {"ueb": 0, "vs": 0, "na": 0}
    def kc_bisher():
        z = dict(zb.Z["na"].t)
        for k, v in zb.Z["vs"].t.items():
            z[k] = z.get(k, 0) + v
        return z, z.get((2, "011"), 0)
    try:
        t2, tl2, r2, dn, ln = zb.rueckfall_gezaehlt(tok, "", r, grenze=200000)
    except bs.Halt:
        return regel, "halt", kc_bisher()[1]
    except zb.Endlos:
        return regel, "endlos", kc_bisher()[1]
    z, kc = kc_bisher()
    # Vergleich auf Bit-Ebene: die Regel kann eine nicht kanonische Zerlegung desselben Bandes liefern,
    # z. B. (1,7) (0,0) (1,0) (1,13) statt (1,21); der Lauf zerlegt beim naechsten Rueckfall ohnehin neu.
    ok = (bits(t2) == bits(b.tok()) and tl2 == "" and r2 == r - 1 and dn == kosten)
    anders = ok and t2 != b.tok()
    return regel, ok, kc, set(z), anders


def negativ(N, R):
    """Negativkontrolle: ganz zufaelliges linkes Band (Bits, kanonisch zerlegt), r zufaellig, rechts das Modell
    1 (100)^r 0 0 ...; Phasen nacheinander rechnen bis Halt. Jeder Halt muss mit K(C) im selben Lauf
    einhergehen und die Erkennung muss dabei anschlagen (K(C) > 0)."""
    halte = mit_kc = kc_laeufe = 0
    for _ in range(N):
        bits = "".join(R.choice("01") for _ in range(R.randint(1, 30)))
        tok, tail = bs.canon(bits)
        r = R.randint(0, 6)
        zb.Z = {"ueb": Zaehler(), "vs": Zaehler(), "na": Zaehler()}
        zb.PH = {"ueb": 0, "vs": 0, "na": 0}
        h = False
        try:
            for _ in range(30):
                tok, tail, r, dn, ln = zb.rueckfall_gezaehlt(tok, tail, r, grenze=20000)
        except bs.Halt:
            h = True
        except (zb.Endlos, IndexError, KeyError, ValueError):
            pass
        kc = sum(z.t.get((2, "011"), 0) for z in zb.Z.values())
        halte += h
        mit_kc += h and kc > 0
        kc_laeufe += kc > 0
    print(f"Negativkontrolle: Laeufe {N}  Halte {halte}  davon mit K(C) {mit_kc}  Laeufe mit K(C) {kc_laeufe}")
    ok = halte > 0 and mit_kc == halte
    print("Negativkontrolle", "SCHLAEGT AN" if ok else "SCHLAEGT NICHT AN")
    sys.exit(0 if ok else 1)


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    R = random.Random(seed)
    if FEHLER:
        negativ(N, R)
    gesamt_kc = 0
    for regel in ("N1", "N2", "N2s", "UA", "LE0", "LE1", "LG"):
        n = falsch = kc = halt = zerl = 0
        typen = set()
        for _ in range(N):
            p = probe(R, regel)
            if p is None:
                continue
            n += 1
            if p[1] in ("halt", "endlos"):
                halt += 1
                kc += p[2] > 0
                continue
            if FEHLER:
                kc += p[2] > 0
                continue
            _, ok, k, ty, anders = p
            falsch += not ok
            zerl += anders
            kc += k > 0
            typen |= ty
        gesamt_kc += kc
        print(f"{regel:4s} Proben {n:6d}  Regel falsch {falsch} (davon nur andere Zerlegung: {zerl} nicht mitgezaehlt)  mit K(C) {kc}  Halt/Endlos {halt}  "
              f"Typen: {' '.join('ABCDEF'[x] + '>' + z for x, z in sorted(typen))}")
    print("K(C) gesamt:", gesamt_kc)


main()
