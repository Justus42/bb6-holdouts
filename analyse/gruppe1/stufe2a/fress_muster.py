"""Stufe 2a: Wie oft passt Regel F (Rocq-Lemma regel_F) auf die Laeufe? Durchlaufmodell aus
../teil3/sweepmodell.py (Bausteine), ohne Schrittbudget innerhalb eines Makroschritts.

Muster am Anfang einer Runde (Rechts-Rekord in C, R leer, L von oben):
  W(x) 1 W(m) 1 ...  mit x ungerade, m >= 2            (Rocq: Block (k+k), Bit 1, Block (S b), Bit 1)
Regel F sagt: genau 25 Makroschritte spaeter  W(x+4) 1 W(m-1) 1 ..., Rest unveraendert.
Gezaehlt wird: an wie vielen Rechts-Rekorden das Muster vorliegt und wie oft F danach stimmt
(gleicher Zustand C, R leer, Stapel darunter unveraendert). Die Zahl der Muster laesst sich mit der
Zahl der Fressrunden vergleichen, die man aus den Listenzeilen (zweitpruefung.c liste) abliest.
Aufruf: python3 -I fress_muster.py <TM-Schritte> [A|C|D]
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "teil3"))
import sweepmodell as sm  # noqa: E402


def muster(L, R):
    if R or len(L) < 4:
        return None
    t1, t2, t3, t4 = L[-1], L[-2], L[-3], L[-4]
    if t1[0] == "w" and t1[1] == "011" and t1[2] % 2 == 1 and t2 == ("b", 1) \
            and t3[0] == "w" and t3[1] == "011" and t3[2] >= 2 and t4 == ("b", 1):
        return (t1[2], t3[2], len(L))
    return None


def main():
    N = int(sys.argv[1]); start = ord(sys.argv[2]) - 65 if len(sys.argv) > 2 else sm.A
    L, R, q, seite = [], [], start, "R"
    pos = hi = 0; n = mk = 0
    offen = []           # (mk_start, x, m, laenge, L-Kopie unter den 4 Stuecken)
    passt = falsch = 0
    while n < N:
        if seite == "R" and q == sm.C and R and R[-1][0] == "w" and R[-1][1] == "100":
            m = R.pop()[2]; sm.push_wort(L, "011", m); pos += 3 * m; n += 3 * m
        elif seite == "L" and q in (sm.B, sm.D) and L and L[-1][0] == "w" and L[-1][1] == "011":
            m = L.pop()[2]; sm.push_wort(R, "100", m); pos -= 3 * m; n += 3 * m
            if m % 2: q = sm.D if q == sm.B else sm.B
        else:
            links = seite == "L"; s = sm.pop_zelle(L if links else R, links)
            if (q, s) not in sm.TAB:
                print("HALT", n); break
            w, d, q = sm.TAB[(q, s)]; n += 1
            if d == 1: sm.push_zelle(L, w, True); seite = "R"
            else: sm.push_zelle(R, w, False); seite = "L"
            pos += d
        mk += 1
        # nach 25 Makroschritten pruefen
        while offen and offen[0][0] + 25 == mk:
            _, x, m, laenge, unten = offen.pop(0)
            ok = (q == sm.C and seite == "R" and not R and len(L) == laenge and L[:-4] == unten
                  and L[-1] == ("w", "011", x + 4) and L[-2] == ("b", 1)
                  and L[-3] == ("w", "011", m - 1) and L[-4] == ("b", 1))
            passt += ok; falsch += not ok
        if pos > hi:
            hi = pos
            if q == sm.C and seite == "R":
                mu = muster(L, R)
                if mu:
                    offen.append((mk, mu[0], mu[1], mu[2], list(L[:-4])))
    print(f"Start {'ABCDEF'[start]}, {n} TM-Schritte, {mk} Makroschritte: Muster {passt + falsch + len(offen)}, "
          f"F stimmt {passt}, F stimmt nicht {falsch}, offen am Ende {len(offen)}")


if __name__ == "__main__":
    main()
