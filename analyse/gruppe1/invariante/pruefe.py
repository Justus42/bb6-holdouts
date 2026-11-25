"""Unabhaengige Nachpruefung des Zertifikats aus zone.py (eigene Semantik, eigener Inklusionstest).

Das Zertifikat ist je Regel eine endliche Menge M abstrakter Zustaende (q, seite, L, R) und die Startformen.
Geprueft wird, ohne Code aus symb.py / zone.py zu benutzen:
  (1) Jede Startform ist in einem Element von M enthalten (Sprachinklusion).
  (2) Fuer jedes Element von M: kein Verbot (C von links vor ?11, Halt, Wand in anderem Zustand als C,
      Lesen von P), und jeder Nachfolger nach einem Makroschritt (S1, S2 oder Einzelschritt) ist in einem
      Element von M enthalten.
Daraus folgt per Induktion: jeder echte Lauf aus einer Startform bleibt bis zum Phasenende in M und
erreicht nie ein Verbot.

Sprache eines Stapels: Woerter ueber {0,1,P,_,#} vom Kopf nach aussen gelesen. Ein Block 011^n links liest
sich vom Kopf aus als (110)^n, ein Block 100^n rechts als (100)^n. Zahlen ('e', v) = genau v,
('a', u) = u, u+2, u+4, ... Sterne (Bedeutung hier eigenstaendig festgelegt):
  Z (links): beliebig viele Token (1, ungerade): vom Kopf aus (110)^(ungerade) 1
  Y (rechts): beliebig viele Stuecke 0 100^(ungerade)
P, _ und # sind Endzeichen (P = unbekannter Rest, _ = leeres Band, # = Wand).
Inklusion zweier NFAs: Teilmengenkonstruktion auf der rechten Seite, Breitensuche ueber Paare.
Aufruf: python3 -I pruefe.py <zertifikat.json>
Negativkontrollen (PRUEFE_FEHLER): loesche (jeder 7. Zustand fehlt), tabelle (E0 -> 1LD),
stern (Z mit geraden Laeufen). Jede muss "NICHT BESTAETIGT" liefern.
"""
import json
import os
import sys

FEHLER = os.environ.get("PRUEFE_FEHLER", "")   # Negativkontrollen: loesche | tabelle | stern

TAB = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
UEB = {}
for zst, teil in enumerate(TAB.split("_")):
    for gelesen in (0, 1):
        e = teil[3 * gelesen:3 * gelesen + 3]
        if e[0] != "-":
            UEB[(zst, gelesen)] = (int(e[0]), +1 if e[1] == "R" else -1, "ABCDEF".index(e[2]))
ZC = 2
if FEHLER == "tabelle":
    UEB[(4, 0)] = (1, -1, 3)       # E0 -> 1LD statt 1RD


# ---------------------------------------------------------------- NFA aus Stapel
class Nfa:
    def __init__(self):
        self.eps = []
        self.sym = []

    def neu(self):
        self.eps.append(set())
        self.sym.append([])
        return len(self.eps) - 1


def wort_kette(nfa, a, wort):
    for c in wort:
        b = nfa.neu()
        nfa.sym[a].append((c, b))
        a = b
    return a


def anzahl(nfa, a, einheit, n):
    """einheit^n, n = ('e', v) oder ('a', u)."""
    art, v = n
    for _ in range(v):
        a = wort_kette(nfa, a, einheit)
    if art == "a":
        schleife = nfa.neu()
        nfa.eps[a].add(schleife)
        b = wort_kette(nfa, schleife, einheit + einheit)
        nfa.eps[b].add(schleife)
        a = schleife
    return a


def stern(nfa, a, name):
    s = nfa.neu()
    nfa.eps[a].add(s)
    if name == "Z":
        b = wort_kette(nfa, s, "110")
        b = anzahl(nfa, b, "110", ("a", 0))
        if FEHLER == "stern":      # Z nur mit Laeufen 1, 3, 5, ... statt ungerade: hier gerade Laeufe
            b = wort_kette(nfa, b, "110")
        b = wort_kette(nfa, b, "1")
    elif name == "Y":
        b = wort_kette(nfa, s, "0100")
        b = anzahl(nfa, b, "100", ("a", 0))
    else:
        raise ValueError(name)
    nfa.eps[b].add(s)
    return s


def baue(stapel, seite):
    nfa = Nfa()
    start = nfa.neu()
    a = start
    for x in stapel:
        k = x[0]
        if k == "b":
            a = wort_kette(nfa, a, str(x[1]))
        elif k == "w":
            wort = x[1]
            einheit = wort[::-1] if seite == "L" else wort
            a = anzahl(nfa, a, einheit, tuple(x[2]))
        elif k == "S":
            a = stern(nfa, a, x[1])
        elif k in ("P", "_", "#"):
            a = wort_kette(nfa, a, k)
        else:
            raise ValueError(x)
    return nfa, start, a


def huelle(nfa, menge):
    out = set(menge)
    st = list(menge)
    while st:
        v = st.pop()
        for w in nfa.eps[v]:
            if w not in out:
                out.add(w)
                st.append(w)
    return frozenset(out)


def schritt(nfa, menge, c):
    return huelle(nfa, {b for v in menge for (d, b) in nfa.sym[v] if d == c})


CACHE = {}


def nfa_von(stapel, seite):
    key = (json.dumps(stapel), seite)
    if key not in CACHE:
        CACHE[key] = baue(stapel, seite)
    return CACHE[key]


def enthalten(st1, st2, seite):
    """Sprache(st1) Teilmenge von Sprache(st2)?"""
    n1, s1, e1 = nfa_von(st1, seite)
    n2, s2, e2 = nfa_von(st2, seite)
    anfang = (huelle(n1, {s1}), huelle(n2, {s2}))
    gesehen = {anfang}
    todo = [anfang]
    while todo:
        m1, m2 = todo.pop()
        if e1 in m1 and e2 not in m2:
            return False
        zeichen = {c for v in m1 for (c, _) in n1.sym[v]}
        for c in zeichen:
            k1 = schritt(n1, m1, c)
            k2 = schritt(n2, m2, c)
            if not k1:
                continue
            if not k2:
                # Wort aus st1 mit diesem Praefix, das st2 nicht kennt: nur ok, wenn st1 hier nicht
                # zu Ende kommen kann (alle Woerter sind endlich und enden mit P/_/#, also nicht ok)
                return False
            p = (k1, k2)
            if p not in gesehen:
                gesehen.add(p)
                todo.append(p)
    return True


# ---------------------------------------------------------------- Semantik (eigenstaendig)
def kopf_auf(st):
    """Liste von (zelle, rest): zelle in {0, 1, 'P', '#'}; rest = Stapel ohne diese Zelle.
    Seite wird ueber das Wort im Block bestimmt (011 nur links, 100 nur rechts)."""
    if not st:
        raise ValueError("leer")
    x, rest = st[0], st[1:]
    k = x[0]
    if k == "b":
        return [(x[1], rest)]
    if k == "_":
        return [(0, st)]
    if k in ("P", "#"):
        return [(k, st)]
    if k == "S":
        aus = kopf_auf(rest)
        if x[1] == "Z":
            kopie = [["w", "011", ["a", 1]], ["b", 1]]
        else:
            kopie = [["b", 0], ["w", "100", ["a", 1]]]
        return aus + kopf_auf(kopie + st)
    if k == "w":
        wort, (art, v) = x[1], x[2]
        aus = []
        null_moeglich = v == 0
        if null_moeglich:
            aus += kopf_auf(rest)
        # n >= 1: eine Einheit abspalten
        if art == "e" and v >= 1:
            rest_n = ["e", v - 1]
        elif art == "a":
            rest_n = ["a", v - 1] if v >= 1 else ["a", 1]
        else:
            return aus
        if wort == "011":      # links: vom Kopf aus 1, 1, 0
            zellen = [1, 1, 0]
        else:                  # rechts: vom Kopf aus 1, 0, 0
            zellen = [1, 0, 0]
        neu = [["b", zellen[1]], ["b", zellen[2]]] + [["w", wort, rest_n]] + rest
        aus.append((zellen[0], neu))
        return aus
    raise ValueError(x)


def erste_zellen(st, k):
    if k == 0:
        return {()}
    aus = set()
    for z, rest in kopf_auf(st):
        if z == "#":
            aus.add((0,) * k)
        elif z == "P":
            for b in (0, 1):
                aus |= {(b,) + t for t in erste_zellen(st, k - 1)}
        else:
            aus |= {(z,) + t for t in erste_zellen(rest, k - 1)}
    return aus


class Verbot(Exception):
    pass


def nachfolger(z):
    q, seite, L, R = z
    if q == ZC and seite == "R":
        for t in erste_zellen(R, 3):
            if t[1] == 1 and t[2] == 1:
                raise Verbot(f"C vor {t}")
    # S1: C, Kopf rechts, oben ein 100-Block
    if q == ZC and seite == "R" and R[0][0] == "w" and R[0][1] == "100":
        art, v = R[0][2]
        aus = []
        if v == 0:
            aus.append((q, seite, L, R[1:]))
        n = ["a", 2] if (art == "a" and v == 0) else ([art, v] if v >= 1 else None)
        if n is not None:
            aus.append((ZC, "R", [["w", "011", n]] + L, R[1:]))
        return aus
    # S2: B oder D, Kopf links, oben ein 011-Block
    if q in (1, 3) and seite == "L" and L[0][0] == "w" and L[0][1] == "011":
        art, v = L[0][2]
        aus = []
        if v == 0:
            aus.append((q, seite, L[1:], R))
        n = ["a", 2] if (art == "a" and v == 0) else ([art, v] if v >= 1 else None)
        if n is not None:
            q2 = (4 - q) if n[1] % 2 == 1 else q      # B=1 <-> D=3
            aus.append((q2, "L", L[1:], [["w", "100", n]] + R))
        return aus
    # Einzelschritt
    aus = []
    for zelle, rest in kopf_auf(R if seite == "R" else L):
        if zelle == "#":
            if q == ZC:
                continue      # Phasenende
            raise Verbot("Wand")
        if zelle == "P":
            raise Verbot("P gelesen")
        if (q, zelle) not in UEB:
            raise Verbot("Halt")
        w, d, q2 = UEB[(q, zelle)]
        if seite == "R":
            L2, R2 = L, rest
        else:
            L2, R2 = rest, R
        if d == +1:
            aus.append((q2, "R", [["b", w]] + L2, R2))
        else:
            aus.append((q2, "L", L2, [["b", w]] + R2))
    return aus


def gedeckt(z, index):
    q, seite, L, R = z
    for (L2, R2) in index.get((q, seite), ()):
        if enthalten(L, L2, "L") and enthalten(R, R2, "R"):
            return True
    return False


def main():
    zert = json.load(open(sys.argv[1]))
    alles_ok = True
    for regel, inhalt in zert.items():
        M = [tuple(z) for z in inhalt["menge"]]
        if FEHLER == "loesche":
            M = [z for i, z in enumerate(M) if i % 7 != 3]
        index = {}
        for q, seite, L, R in M:
            index.setdefault((q, seite), []).append((L, R))
        fehler = None
        for st in inhalt["starts"]:
            if not gedeckt(tuple(st), index):
                fehler = "Start nicht gedeckt"
        geprueft = 0
        for z in M:
            if fehler:
                break
            try:
                nf = nachfolger(z)
            except Verbot as v:
                fehler = f"Verbot: {v}"
                break
            for z2 in nf:
                if not gedeckt(z2, index):
                    fehler = f"Nachfolger nicht gedeckt: {z2}"
                    break
            geprueft += 1
        if fehler:
            alles_ok = False
            print(f"{regel:4s} NICHT BESTAETIGT: {fehler}")
        else:
            print(f"{regel:4s} bestaetigt: {len(M)} Zustaende abgeschlossen, Starts gedeckt, keine Verbote")
    print("Zertifikat", "BESTAETIGT" if alles_ok else "NICHT BESTAETIGT")
    sys.exit(0 if alles_ok else 1)


if __name__ == "__main__":
    main()
