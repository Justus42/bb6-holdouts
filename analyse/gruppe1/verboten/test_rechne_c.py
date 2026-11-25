"""Abgleich rechne.c gegen die Python-Fassung rechne_py (zyklus_beschl.py) und gegen beschleuniger.rueckfall.

Eingaben: (1) zufaellige Bit-Baender (kanonisch zerlegt, Rest), r zufaellig, auch Halte;
(2) zufaellige Token-Listen mit grossen Zahlen; (3) echte Listen aus einem Lauf bis 10^11 (alle Rueckfaelle).
Verglichen wird alles: Token-Liste, Rest, r', Schritte, K(C), Halt mit Schrittzahl.
Aufruf: python3 -I test_rechne_c.py <proben> <seed>
Negativkontrolle: RC_FEHLER=1 veraendert die C-Ergebnisse (Schritte +1 bei jeder 7. Probe); muss Fehler zeigen."""
import os
import random
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import zyklus_beschl as zb  # noqa: E402

bs = zb.bs
FEHLER = os.environ.get("RC_FEHLER", "")
GRENZE = 200000   # Makroschritte; zufaellige Listen beenden die Phase oft nicht


def lauf_py(X, tail, r):
    try:
        return zb.rechne_py(X, tail, r, GRENZE)
    except bs.Halt as h:
        return ("HALT", h.args[0])
    except zb.Endlos:
        return ("ENDLOS",)


def lauf_c(X, tail, r, i):
    try:
        e = zb.rechne_c(X, tail, r, GRENZE)
    except bs.Halt as h:
        return ("HALT", h.args[0])
    except zb.Endlos:
        return ("ENDLOS",)
    if FEHLER and i % 7 == 0:
        e = (e[0], e[1], e[2], e[3] + 1, e[4])
    return e


def main():
    N, seed = int(sys.argv[1]), int(sys.argv[2])
    R = random.Random(seed)
    proben = []
    for _ in range(N):
        bits = "".join(R.choice("01") for _ in range(R.randint(1, 40)))
        tok, tail = bs.canon(bits)
        proben.append(("bits", tok, tail, R.randint(0, 8)))
    for _ in range(N):
        tok = []
        for _ in range(R.randint(1, 30)):
            u = R.random()
            v = R.randint(0, 10**5) if R.random() < 0.2 else R.randint(0, 15)
            tok.append((R.choice(["0", "1", ""]) if u < 0.3 else "1", v | (1 if u > 0.5 else 0)))
        if tok[0][0] == "" and tok[0][1] == 0:
            tok[0] = ("1", 1)
        tail = "".join(R.choice("01") for _ in range(R.randint(0, 2)))
        proben.append(("token", tok, tail, R.randint(0, 50) if R.random() < 0.8 else R.randint(0, 10**5)))
    # echte Listen: ein Lauf bis 10^11 mit Python-rechne, alle Eingaben mitschreiben
    echte = []
    alt = zb.rechne

    def mit(X, tail, r, lauf):
        echte.append(("echt", list(X), tail, r))
        return alt(X, tail, r, lauf)
    zb.rechne = mit
    zb.Lauf(0, "lauf", None, 10**30).lauf(10**11)
    zb.rechne = alt
    proben += echte
    fehler = halte = 0
    endlos = [0]
    globals()["endlos"] = endlos
    arten = {}
    for i, (art, tok, tail, r) in enumerate(proben):
        a, b = lauf_py(tok, tail, r), lauf_c(tok, tail, r, i)
        arten[art] = arten.get(art, 0) + 1
        halte += a[0] == "HALT"
        endlos = globals().setdefault("endlos", [0])
        endlos[0] += a[0] == "ENDLOS"
        if a != b:
            fehler += 1
            if fehler <= 3:
                print("VERSCHIEDEN", art, tok[:6], tail, r, "\n  py", str(a)[:200], "\n  c ", str(b)[:200])
    print(f"Proben {len(proben)} {arten}  davon Halt {halte}, Grenze erreicht {endlos[0]}  verschieden {fehler}")
    sys.exit(1 if fehler else 0)


main()
