"""Symbolische Ausfuehrung einer Phase im Durchlaufmodell (S1, S2, E) mit abstrakten Zahlen.

Tabelle 114: 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC.

Darstellung wie teil3/sweepmodell.py: Zustand (q, seite, L, R); L und R sind Stapel (oberstes Element am
Kopf zuerst). seite 'R': Kopf auf dem obersten Bit von R; seite 'L': Kopf auf dem obersten Bit von L.
Elemente:
  ('b', x)              ein Bit
  ('w', wort, n)        Block wort^n, wort = '011' (in L) oder '100' (in R); n abstrakt:
                        ('e', v)  genau v;   ('a', u) = {u, u+2, u+4, ...}
  ('S', name)           Stern: beliebig viele (auch 0) Kopien eines Musters (siehe STERNE)
  ('P',)                unbekanntes Band (beliebige Bits) -> liest der Kopf hier: "offen"
  ('_',)                unendlich leeres Band (Bit 0)
  ('#',)                Wand (Zelle p+3); C erreicht sie von links: Phase zu Ende; anderer Zustand: "offen"
Makroschritte:
  S1: q = C, seite R, R oben ('w','100',n): Block wird ('w','011',n) in L.  Innere C-Eintritte lesen 100.
  S2: q in {B, D}, seite L, L oben ('w','011',n): Block wird ('w','100',n) in R, B<->D bei ungeradem n.
      Innere C-Eintritte kommen von rechts (F1 schreibt 0 rechts daneben), also nie vor 11.
  E:  ein Tabellenschritt; ein Block wird dafuer aufgeteilt (Fallunterscheidung, wenn n = 0 moeglich).
Geprueft wird in jedem Zustand mit q = C und seite R (C kam von links): die Zellen x+1, x+2 duerfen nicht
1 1 sein (sonst K(C) oder C vor 111). Halt (fehlender Tabelleneintrag) ist ebenfalls verboten.
Alle Faelle werden erschoepfend durchsucht (Menge besuchter abstrakter Zustaende). Jeder abstrakte
Zustand steht fuer eine Menge echter Baender; jeder echte Lauf wird von einem abstrakten Pfad begleitet
(Ueberapproximation), also: kein Verstoss im abstrakten System => kein Verstoss in einem echten Lauf.
"""
import os
import sys

FEHLER = os.environ.get("SYMB_FEHLER", "")
TAB = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
A, B, C, D, E, F = range(6)
CAP = 6   # groessere Untergrenzen werden auf CAP/CAP+1 (gleiche Paritaet) abgeschnitten (Ueberapprox.)


def tabelle():
    T = {}
    for q, s in enumerate(TAB.split("_")):
        for b in range(2):
            e = s[3 * b:3 * b + 3]
            if e != "---":
                T[(q, b)] = (int(e[0]), 1 if e[1] == "R" else -1, ord(e[2]) - 65)
    if FEHLER == "tabelle":          # Negativkontrolle: E0 -> 1LD statt 1RD
        T[(E, 0)] = (1, -1, D)
    return T


T = tabelle()


class Verstoss(Exception):
    pass


# ------------------------------------------------------------------ abstrakte Zahlen
def kann_null(n):
    return n == ("e", 0) or n == ("a", 0)


def ohne_null(n):
    """Nicht-null-Teil oder None."""
    if n[0] == "e":
        return None if n[1] == 0 else n
    return ("a", 2) if n[1] == 0 else n


def minus1(n):
    """n >= 1 vorausgesetzt."""
    if n[0] == "e":
        return ("e", n[1] - 1)
    return ("a", n[1] - 1)


def plus(n, m):
    if n[0] == "e" and m[0] == "e":
        r = ("e", n[1] + m[1])
    else:
        r = ("a", n[1] + m[1])
    return deckel(r)


def deckel(n):
    if n[1] > CAP + 1:
        u = CAP if n[1] % 2 == CAP % 2 else CAP + 1
        return ("a", u)
    return n


def ungerade(n):
    return n[1] % 2 == 1


# ------------------------------------------------------------------ Sterne
# Muster als Elementliste, so wie es in dem jeweiligen Stapel steht (oberstes zuerst).
STERNE = {
    # unbearbeitete Zonen-Token links: Lauf 011^(ungerade >= 1), dann Trenner 1
    "Z": [("w", "011", ("a", 1)), ("b", 1)],
}
if FEHLER == "zone":   # Negativkontrolle: Zonen-Token beliebiger Paritaet
    STERNE["Z"] = [("w", "011", ("a", 0)), ("b", 1)]


# ------------------------------------------------------------------ Stapel
def norm(st, seite):
    """Exakte Umschreibungen: ein Wort aus Einzelbits neben einem Block wird in den Block gezogen;
    benachbarte Bloecke werden zusammengelegt."""
    st = list(st)
    wort = "011" if seite == "L" else "100"
    # Bits eines Worts in Stapelreihenfolge (oberstes = am Kopf naechstes)
    if seite == "L":
        einheit = [("b", 1), ("b", 1), ("b", 0)]       # Band ... 0 1 1 | Kopf: oben 1, dann 1, dann 0
    else:
        einheit = [("b", 1), ("b", 0), ("b", 0)]       # Kopf | 1 0 0 ...
    geaendert = True
    while geaendert:
        geaendert = False
        for i in range(len(st)):
            x = st[i]
            if st[i:i + 3] == einheit:
                st[i:i + 3] = [("w", wort, ("e", 1))]
                geaendert = True
                break
            if x[0] == "w" and x[1] == wort:
                # Einheit direkt ueber dem Block (naeher am Kopf)
                if i >= 3 and st[i - 3:i] == einheit:
                    st[i - 3:i + 1] = [("w", wort, plus(x[2], ("e", 1)))]
                    geaendert = True
                    break
                # Einheit direkt unter dem Block (weiter weg)
                if st[i + 1:i + 4] == einheit:
                    st[i:i + 4] = [("w", wort, plus(x[2], ("e", 1)))]
                    geaendert = True
                    break
                if i + 1 < len(st) and st[i + 1][0] == "w" and st[i + 1][1] == wort:
                    st[i:i + 2] = [("w", wort, plus(x[2], st[i + 1][2]))]
                    geaendert = True
                    break
    return tuple(st)


def pop(st, seite):
    """Liefert Liste von (bit | 'P' | '#', rest)."""
    if not st:
        raise RuntimeError("leerer Stapel")
    x = st[0]
    rest = st[1:]
    if x[0] == "b":
        return [(x[1], rest)]
    if x[0] == "_":
        return [(0, st)]
    if x[0] in ("P", "#"):
        return [(x[0], st)]
    if x[0] == "S":
        out = pop(rest, seite)                                   # null Kopien
        out += pop(tuple(STERNE[x[1]]) + st, seite)              # eine Kopie mehr
        return out
    # Block
    _, wort, n = x
    out = []
    if kann_null(n):
        out += pop(rest, seite)
    nz = ohne_null(n)
    if nz is not None:
        n1 = minus1(nz)
        if seite == "R":
            erste, oben = int(wort[0]), [("b", int(wort[1])), ("b", int(wort[2]))]
        else:
            erste, oben = int(wort[2]), [("b", int(wort[1])), ("b", int(wort[0]))]
        unten = () if n1 == ("e", 0) else (("w", wort, n1),)
        out.append((erste, tuple(oben) + unten + rest))
    return out


def peek(st, seite, k):
    """Alle moeglichen ersten k Bits (Ueberapproximation). 'P' -> 0 oder 1, '#' -> 0 (Zellen p+3, p+4 sind 0)."""
    if k == 0:
        return {()}
    out = set()
    if st and st[0][0] == "#":
        return {(0,) * k}
    if st and st[0][0] == "P":
        res = set()
        for b in (0, 1):
            for r in peek(st, seite, k - 1) if k > 1 else {()}:
                res.add((b,) + r)
        return res
    for b, rest in pop(st, seite):
        if b == "P":
            for bb in (0, 1):
                out |= {(bb,) + r for r in peek(rest, seite, k - 1)} if k > 1 else {(bb,)}
            continue
        if b == "#":
            out.add((0,) * k)
            continue
        out |= {(b,) + r for r in peek(rest, seite, k - 1)}
    return out


# ------------------------------------------------------------------ Schritt
def schritte(z):
    """Alle Nachfolger eines abstrakten Zustands; wirft Verstoss. Rueckgabe Liste von (art, z') oder 'ENDE'."""
    q, seite, L, R = z
    if q == C and seite == "R":
        for w in peek(R, "R", 3):
            if w[1] == 1 and w[2] == 1:
                raise Verstoss(f"C vor {w[0]}{w[1]}{w[2]}")
    # S1
    if q == C and seite == "R" and R[0][0] == "w" and R[0][1] == "100":
        n = R[0][2]
        out = []
        if kann_null(n):
            out.append(("S1-0", (q, seite, L, R[1:])))
        nz = ohne_null(n)
        if nz is not None:
            out.append(("S1", (C, "R", norm((("w", "011", nz),) + L, "L"), R[1:])))
        return out
    # S2
    if q in (B, D) and seite == "L" and L[0][0] == "w" and L[0][1] == "011":
        n = L[0][2]
        out = []
        if kann_null(n):
            out.append(("S2-0", (q, seite, L[1:], R)))
        nz = ohne_null(n)
        if nz is not None:
            q2 = (D if q == B else B) if ungerade(nz) else q
            if nz[0] == "a" and FEHLER == "paritaet":
                q2 = q
            out.append(("S2", (q2, "L", L[1:], norm((("w", "100", nz),) + R, "R"))))
        return out
    # E
    st = R if seite == "R" else L
    out = []
    for b, rest in pop(st, seite):
        if b == "#":
            if q == C:
                out.append(("ENDE", None))
                continue
            raise Verstoss(f"Wand in Zustand {'ABCDEF'[q]}")
        if b == "P":
            raise Verstoss("Kopf verlaesst den beschriebenen Bereich (P)")
        if (q, b) not in T:
            raise Verstoss("Halt")
        w, d, q2 = T[(q, b)]
        L2, R2 = (L, rest) if seite == "R" else (rest, R)
        if d == 1:
            out.append(("E", (q2, "R", norm((("b", w),) + L2, "L"), R2)))
        else:
            out.append(("E", (q2, "L", L2, norm((("b", w),) + R2, "R"))))
    return out


def falte(z):
    """Hook fuer Sterne (Induktion ueber die Zone); siehe zone.py."""
    return z


def suche(start, falte=falte, limit=2_000_000):
    """Erschoepfende Suche. Rueckgabe (ok, info)."""
    gesehen = {}
    stapel = [start]
    gesehen[start] = None
    enden = 0
    while stapel:
        z = stapel.pop()
        try:
            nf = schritte(z)
        except Verstoss as v:
            weg = []
            y = z
            while y is not None and len(weg) < 40:
                weg.append(y)
                y = gesehen[y]
            return False, {"grund": str(v), "weg": list(reversed(weg)), "zustaende": len(gesehen)}
        for art, z2 in nf:
            if art == "ENDE":
                enden += 1
                continue
            z2 = falte(z2)
            if z2 not in gesehen:
                gesehen[z2] = z
                stapel.append(z2)
                if len(gesehen) > limit:
                    return False, {"grund": "Limit", "weg": [], "zustaende": len(gesehen)}
    return True, {"zustaende": len(gesehen), "enden": enden, "menge": list(gesehen)}


def zeige(z):
    q, seite, L, R = z

    def f(x):
        if x[0] == "b":
            return str(x[1])
        if x[0] == "w":
            n = x[2]
            s = str(n[1]) if n[0] == "e" else f"{n[1]}+2k"
            return f"{x[1]}^{s}"
        if x[0] == "S":
            return f"({x[1]})*"
        return x[0]
    links = " ".join(f(x) for x in reversed(L))
    rechts = " ".join(f(x) for x in R)
    if seite == "R":
        return f"{links} {'ABCDEF'[q]}> {rechts}"
    return f"{links} <{'ABCDEF'[q]} {rechts}"
