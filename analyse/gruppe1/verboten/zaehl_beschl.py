"""Zaehlung "verbotenes Muster" bis 10^17: beschleuniger.py (linkes_ende) unveraendert, nur die Funktion
rueckfall wird durch eine gezaehlte Fassung ersetzt. Gezaehlt wird also NUR in den Phasen, die der
Beschleuniger mit dem Durchlaufmodell nachrechnet (Zyklusuebergaenge r = 0, VS, "nicht anwendbar");
in den uebersprungenen Automatenphasen wird nichts gezaehlt (dort wird auch Halt nicht geprueft).

Zaehlung wie zaehl_durchlauf.py / zaehl_direkt.c: jeder Schritt nach rechts, Zustand danach, drei Zellen
ab dem Kopf. Getrennt nach Art der Phase: ueb (r = 0), vs, na.
Ausgabe: nach jeder Zehnerpotenz Zeilen "stand 10^k <art> X zzz anzahl" (kumuliert, Phasen bis zum ersten
Schnappschuss >= 10^k, wie zaehl_direkt.c "phase ...") und "phasen 10^k <art> anzahl".
Aufruf: python3 -I zaehl_beschl.py <A|C|D> <schritte> <praefix>   (praefix wie beschleuniger.py lauf)
"""
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "linkes_ende"))
sys.path.insert(0, HIER)
import beschleuniger as bs  # noqa: E402
from zaehl_durchlauf import Zaehler  # noqa: E402

sm = bs.sm
A, B, C, D, E, F = range(6)
Z = {"ueb": Zaehler(), "vs": Zaehler(), "na": Zaehler()}
PH = {"ueb": 0, "vs": 0, "na": 0}


class Endlos(Exception):
    pass


def rueckfall_gezaehlt(tok, tail, r, grenze=None):
    """Wie beschleuniger.rueckfall (Zeile fuer Zeile), zusaetzlich mit Zaehlung der Rechtsschritte."""
    if r == 0:
        art = "ueb"
    else:
        grund = bs.Band(tok, tail).schritt()[0]
        art = "vs" if grund == "VS" else "na"
    PH[art] += 1
    z = Z[art]
    L = bs.l_aus_token(tok, tail)
    R = [("b", 1)]
    if r:
        R.append(("w", "100", r))
    R += [("b", 0), ("b", 0)]
    q, seite = C, "R"
    links_neu = 0
    n = 0
    erster = True
    makro = 0
    while True:
        makro += 1
        if grenze is not None and makro > grenze:
            raise Endlos(makro)
        if not erster and q == C:
            rr = None
            if seite == "R" and sm.peek(R, False, 2) == [0, 0]:
                rr = bs.rechts_muster(R, "z1")
            elif seite == "L" and sm.peek(L, True, 1) == [0]:
                rr = bs.rechts_muster(R, "z2")
            if rr is not None:
                tk, tl = bs.canon(bs.bits_aus_l(L) if seite == "R" else bs.bits_aus_l(L)[:-1])
                return tk, tl, rr, n, links_neu
        erster = False
        if seite == "R" and q == C and R and R[-1][0] == "w" and R[-1][1] == "100":
            m = R.pop()[2]
            z.s1(m, R)
            sm.push_wort(L, "011", m)
            n += 3 * m
            continue
        if seite == "L" and q in (B, D) and L and L[-1][0] == "w" and L[-1][1] == "011":
            m = L.pop()[2]
            sm.push_wort(R, "100", m)
            n += 3 * m
            if m % 2:
                q = D if q == B else B
            continue
        links = seite == "L"
        st = L if links else R
        if links and not L:
            links_neu += 1
        s = sm.pop_zelle(st, links)
        if (q, s) not in sm.TAB:
            raise bs.Halt(n)
        w, d, nq = sm.TAB[(q, s)]
        n += 1
        if d == 1:
            sm.push_zelle(L, w, True)
            seite = "R"
            z.add(nq, "".join(map(str, sm.peek(R, False, 3))))
        else:
            sm.push_zelle(R, w, False)
            seite = "L"
        q = nq


class Ausgabe:
    """Leitet stdout durch; nach jeder Zehnerpotenz-Zeile des Beschleunigers die Zaehlung anhaengen."""
    def __init__(self, s):
        self.s = s
        self.puffer = ""

    def write(self, text):
        self.puffer += text
        while "\n" in self.puffer:
            zeile, self.puffer = self.puffer.split("\n", 1)
            self.s.write(zeile + "\n")
            if zeile.startswith("10^") or zeile.startswith("start="):
                k = zeile.split(":")[0] if zeile.startswith("10^") else "ende"
                for art in ("ueb", "vs", "na"):
                    self.s.write(f"phasen {k} {art} {PH[art]}\n")
                    for zl in Z[art].zeilen(f"stand {k} {art}"):
                        self.s.write(zl + "\n")
                self.s.flush()

    def flush(self):
        self.s.flush()


if __name__ == "__main__":
    bs.rueckfall = rueckfall_gezaehlt
    sys.stdout = Ausgabe(sys.stdout)
    st = ord(sys.argv[1]) - 65
    N = int(float(sys.argv[2]))
    bs.lauf(st, N, "lauf", sys.argv[3])
