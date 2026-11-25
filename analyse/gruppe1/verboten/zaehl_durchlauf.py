"""Programm 2 fuer "Halt als verbotenes Muster": dieselbe Zaehlung wie zaehl_direkt.c, aber im
Durchlaufmodell (teil3/sweepmodell.py, Regeln S1/S2/E, Bloecke 011^n links und 100^n rechts) und
unabhaengig von zaehl_direkt.c geschrieben.

Gezaehlt wird jeder TM-Schritt, der den Kopf nach rechts bewegt: Zustand X danach und die drei Zellen
ab der neuen Kopfposition. Im Modell gibt es Rechtsbewegungen in E-Schritten und in S1 (C> 100 -> 011 C>);
fuer einen Block 100^m ergeben sich je Einheit drei Eintritte (E auf die erste 0, D auf die zweite 0,
C auf die Zelle hinter der Einheit); die Zellen dahinter werden mit peek gelesen. S2 bewegt nur nach links.

Aufruf: python3 -I zaehl_durchlauf.py <A|C|D> <schritte>     Ausgabe "gesamt X zzz anzahl" (Schritte 0..N-1)
Negativkontrolle: ZAEHL_FEHLER=s1 (S1 zaehlt bei der letzten Einheit die Zellen falsch: wie im Blockinneren).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "teil3"))
import sweepmodell as sm  # noqa: E402

FEHLER = os.environ.get("ZAEHL_FEHLER", "")
C, B, D = 2, 1, 3


class Zaehler:
    def __init__(self):
        self.t = {}

    def add(self, x, z, k=1):
        if k:
            key = (x, z)
            self.t[key] = self.t.get(key, 0) + k

    def s1(self, m, R):
        """Block 100^m wurde schon von R genommen; R zeigt die Zellen dahinter."""
        a, b, c = sm.peek(R, False, 3)
        self.add(4, "001", m - 1)   # E
        self.add(3, "010", m - 1)   # D
        self.add(2, "100", m - 1)   # C
        if FEHLER == "s1":
            a, b, c = 1, 0, 0
        self.add(4, f"00{a}")
        self.add(3, f"0{a}{b}")
        self.add(2, f"{a}{b}{c}")

    def zeilen(self, praefix):
        return [f"{praefix} {'ABCDEF'[x]} {z} {v}" for (x, z), v in sorted(self.t.items())]


def lauf(start, N):
    L, R = [], []
    q, seite = start, "R"
    n = 0
    z = Zaehler()
    while n < N:
        if seite == "R" and q == C and R and R[-1][0] == "w" and R[-1][1] == "100" and n + 3 * R[-1][2] <= N:
            m = R.pop()[2]
            z.s1(m, R)
            sm.push_wort(L, "011", m)
            n += 3 * m
            continue
        if seite == "L" and q in (B, D) and L and L[-1][0] == "w" and L[-1][1] == "011" and n + 3 * L[-1][2] <= N:
            m = L.pop()[2]
            sm.push_wort(R, "100", m)
            n += 3 * m
            if m % 2:
                q = D if q == B else B
            continue
        links = seite == "L"
        st = L if links else R
        s = sm.pop_zelle(st, links)
        if (q, s) not in sm.TAB:
            print(f"HALT bei Schritt {n}")
            break
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
    return z


if __name__ == "__main__":
    st = ord(sys.argv[1]) - 65
    N = int(float(sys.argv[2]))
    print("\n".join(lauf(st, N).zeilen("gesamt")))
