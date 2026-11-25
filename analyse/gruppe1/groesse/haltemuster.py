"""Wo in einer Phase das Haltemuster liegen koennte: Stichprobe mit dem Durchlaufmodell.

Haltemuster (von Justus akzeptiert, notwendig, nicht hinreichend): vor jedem Halt steht der Kopf in
Zustand C auf einer 0, rechts davon 1 1 ("C> 0 1 1"). Hier wird fuer ausgewaehlte Phasen jeder TM-Schritt
im Durchlaufmodell (sweepmodell.py, wie im Rueckfall des Beschleunigers) daraufhin geprueft, ob der Kopf
auf einer 0 mit 1 1 rechts davon steht, in welchem Zustand, und wo relativ zum Trennerbit der Grenze.
In den Blocksprungen S1/S2 kann das Muster nicht auftreten (S1: C liest nur die 1 von 100; S2: die
gelesenen Nullen haben 0 0 rechts), deshalb werden nur Einzelschritte geprueft.

Ausgewaehlt: jede Phase, die ohnehin zurueckfaellt (VS, linkes Ende, Uebergang), und jede k-te
Automatenphase (k aus der Kommandozeile); dort wird das Ergebnis des Durchlaufmodells zusaetzlich mit der
Automatenregel verglichen.
Aufruf: python3 haltemuster.py <A|C|D> <Schritte> <k>
Ausgabe: Zaehlung (Regel, Zustand, Abstand zur Grenze in Zellen) und Zahl der Faelle "C> 0 1 1".
Negativkontrolle: HALTEMUSTER_FEHLER=d zaehlt Zustand D als C; dann muss "C> 0 1 1" > 0 sein.
"""
import os
import sys
from collections import Counter

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "linkes_ende"))
import beschleuniger as bs  # noqa: E402
import sweepmodell as sm  # noqa: E402

A, B, C, D, E, F = range(6)
FEHLER = os.environ.get("HALTEMUSTER_FEHLER", "")


def zellen(st):
    return sum(1 if x[0] == "b" else 3 * x[2] for x in st)


def phase_mit_muster(tok, r, treffer, regel, grenz_pos):
    """Wie bs.rueckfall, zusaetzlich Musterpruefung je Einzelschritt. Rueckgabe (tok', tail', r')."""
    L = bs.l_aus_token(tok, "")
    R = [("b", 1)]
    if r:
        R.append(("w", "100", r))
    R += [("b", 0), ("b", 0)]
    q, seite = C, "R"
    erster = True
    while True:
        if not erster and q == C:
            rr = None
            if seite == "R" and sm.peek(R, False, 2) == [0, 0]:
                rr = bs.rechts_muster(R, "z1")
            elif seite == "L" and sm.peek(L, True, 1) == [0]:
                rr = bs.rechts_muster(R, "z2")
            if rr is not None:
                tk, tl = bs.canon(bs.bits_aus_l(L) if seite == "R" else bs.bits_aus_l(L)[:-1])
                return tk, tl, rr
        erster = False
        if seite == "R" and q == C and R and R[-1][0] == "w" and R[-1][1] == "100":
            m = R.pop()[2]
            sm.push_wort(L, "011", m)
            continue
        if seite == "L" and q in (B, D) and L and L[-1][0] == "w" and L[-1][1] == "011":
            m = L.pop()[2]
            sm.push_wort(R, "100", m)
            if m % 2:
                q = D if q == B else B
            continue
        # Einzelschritt: Muster pruefen
        if seite == "R":
            z = sm.peek(R, False, 3)
        else:
            z = sm.peek(L, True, 1) + sm.peek(R, False, 2)
        if z == [0, 1, 1]:
            pos = zellen(L) - (0 if seite == "R" else 1)
            zst = "C" if (q == C or (FEHLER == "d" and q == D)) else "ABCDEF"[q]
            treffer[(regel, zst, pos - grenz_pos)] += 1
        links = seite == "L"
        st = L if links else R
        s = sm.pop_zelle(st, links)
        if (q, s) not in sm.TAB:
            raise bs.Halt(0)
        w, d, nq = sm.TAB[(q, s)]
        if d == 1:
            sm.push_zelle(L, w, True)
            seite = "R"
        else:
            sm.push_zelle(R, w, False)
            seite = "L"
        q = nq


def grenze_zelle(tok):
    """Zellposition (von links, ab 0) des Trennerbits der Grenze; ohne Grenze -1."""
    F = -1
    for i in range(len(tok) - 2, -1, -1):
        if not bs.regulaer(*tok[i]):
            F = i
            break
    if F < 0:
        return -1
    return sum((1 if t != "" else 0) + 3 * n for t, n in tok[:F])


def lauf(start, N, k):
    n, tok, tail, r = bs.anlauf(start, N)
    band = bs.Band(tok, tail)
    treffer = Counter()
    geprueft = Counter()
    abw = 0
    zaehler = 0
    while n < N:
        vor = band.tok()
        if r >= 1 and band.tail == "":
            zaehler += 1
            stich = zaehler % k == 0
            gp = grenze_zelle(vor) if stich else 0
            grund, kosten = band.schritt()
            if kosten is not None:
                if stich:
                    t2, tl2, r2 = phase_mit_muster(vor, r, treffer, grund, gp)
                    geprueft[grund] += 1
                    if t2 != band.tok() or r2 != r - 1:
                        abw += 1
                n += kosten
                r -= 1
                continue
        # Rueckfall-Phase: immer pruefen
        art = "Uebergang" if r == 0 else "Rueckfall"
        if band.tail == "":
            gp = grenze_zelle(vor)
            phase_mit_muster(vor, r, treffer, art, gp)
            geprueft[art] += 1
        t2, tl2, r2, dn, ln = bs.rueckfall(vor, band.tail, r)
        n += dn
        r = r2
        band = bs.Band(t2, tl2)
    print(f"start={'ABCDEF'[start]} bis={n} geprueft={dict(geprueft)} abweichungen_automat={abw}")
    c011 = sum(v for (g, z, d), v in treffer.items() if z == "C")
    print(f"C> 0 1 1: {c011}")
    kurz = {}
    for (g, z, d), v in treffer.items():
        e = kurz.setdefault((g, z), [0, set()])
        e[0] += v
        e[1].add(d)
    for (g, z), (v, ds) in sorted(kurz.items()):
        ds = sorted(ds)
        print(f"  {g:10s} {z}> 0 1 1: {v:6d} mal, Abstand zur Grenze {ds[0]:+d}..{ds[-1]:+d} Zellen "
              f"({len(ds)} Werte, gerade {sum(1 for x in ds if x % 2 == 0)})")


if __name__ == "__main__":
    lauf(ord(sys.argv[1]) - 65, int(float(sys.argv[2])), int(sys.argv[3]))
