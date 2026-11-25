"""Sweep-Modell (Tokenmodell) fuer Tabelle 114, unabhaengig vom direkten Simulator.

Zustand: (L, q, R, seite). L und R sind Stapel von Token, oberstes Element = Zelle am Kopf.
Token: ('b', bit) oder ('w', wort, n) = wort^n in Bandrichtung (links nach rechts).
seite = 'R': der Kopf liest die oberste Zelle von R; seite = 'L': die oberste Zelle von L
(wie busycoq: l {{q}}> r bzw. l <{{q}} r).

Regeln (ein Makroschritt = genau eine davon):
  S1  seite R, q = C, R oben ('w','100',n)        -> L bekommt ('w','011',n), 3n Schritte
  S2  seite L, q in {B,D}, L oben ('w','011',n)   -> R bekommt ('w','100',n), 3n Schritte,
      q wechselt B<->D genau dann, wenn n ungerade
  E   sonst ein einzelner TM-Schritt auf der Zelle am Kopf (Wort-Token wird dafuer aufgeteilt)
Nach jedem Ablegen einer Zelle werden drei Bits '011' links bzw. '100' rechts zu einem Wort
zusammengefasst (aendert das Band nicht, nur die Darstellung).

Ausgabe (Modus liste): bei jedem Rechts-Rekord in Zustand C dieselbe Zeile wie
zweitpruefung.c liste, damit beide Programme byteweise verglichen werden koennen.
Aufruf: python3 sweepmodell.py <schritte> liste [start]    Zeilen wie zweitpruefung.c liste
        python3 sweepmodell.py <schritte> zaehlen [start]  Zahl der Makroschritte
        python3 sweepmodell.py <schritte> pruefen [start]  Pruefpunkte (C vor 11) einordnen
Negativkontrollen: Umgebungsvariable SWEEP_FEHLER=paritaet (S2 ohne Wechsel B<->D) oder
SWEEP_FEHLER=s1_block (S1 schreibt einen falschen Block); dann muss der Vergleich scheitern.
"""
import sys

TM = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
A, B, C, D, E, F = range(6)


def tabelle(s):
    t = {}
    for qi, part in enumerate(s.split("_")):
        for r in range(2):
            x = part[3 * r:3 * r + 3]
            if x != "---":
                t[(qi, r)] = (int(x[0]), 1 if x[1] == "R" else -1, ord(x[2]) - 65)
    return t


TAB = tabelle(TM)
# Negativkontrollen: absichtlich falsche Regeln (nur zum Testen der Vergleiche)
import os
FEHLER = os.environ.get("SWEEP_FEHLER", "")


def pop_zelle(st, links):
    """Nimmt die Zelle am Kopf vom Stapel; leerer Stapel = Blank 0."""
    if not st:
        return 0
    top = st[-1]
    if top[0] == "b":
        st.pop()
        return top[1]
    _, w, n = st.pop()
    if n > 1:
        st.append(("w", w, n - 1))
    if links:   # naechste Zelle ist w[-1]; Rest des Blocks w[0], w[1]
        st.append(("b", int(w[0])))
        st.append(("b", int(w[1])))
        return int(w[2])
    st.append(("b", int(w[2])))
    st.append(("b", int(w[1])))
    return int(w[0])


def peek(st, links, k):
    """Die k Zellen am Kopf (naechste zuerst), ohne den Stapel zu aendern; Blank = 0."""
    out = []
    for tok in reversed(st):
        if tok[0] == "b":
            out.append(tok[1])
        else:
            w = tok[1][::-1] if links else tok[1]
            for _ in range(min(tok[2], k)):
                out.extend(int(c) for c in w)
        if len(out) >= k:
            return out[:k]
    return (out + [0] * k)[:k]


def push_wort(st, w, n):
    if st and st[-1][0] == "w" and st[-1][1] == w:
        st[-1] = ("w", w, st[-1][2] + n)
    else:
        st.append(("w", w, n))


def push_zelle(st, b, links):
    st.append(("b", b))
    if len(st) >= 3 and st[-1][0] == st[-2][0] == st[-3][0] == "b":
        if links and (st[-3][1], st[-2][1], st[-1][1]) == (0, 1, 1):
            del st[-3:]
            push_wort(st, "011", 1)
        elif not links and (st[-1][1], st[-2][1], st[-3][1]) == (1, 0, 0):
            del st[-3:]
            push_wort(st, "100", 1)


def nullabstaende(L, hi, lo):
    """Zeile wie zweitpruefung.c: Kopf steht bei hi (Blank 0), R ist leer."""
    out = []
    prev = hi
    k = 0
    pos = hi - 1          # Position der obersten Zelle von L
    for tok in reversed(L):
        if tok[0] == "b":
            cells = [tok[1]]
        else:
            cells = None
        if cells is not None:
            if tok[1] == 0:
                g = prev - pos
                if g == 3: k += 1
                else:
                    out.append(f" {k} |" if g == 4 else f" {k} <{g}>"); k = 0
                prev = pos
            pos -= 1
            continue
        _, w, n = tok
        # Zellen von rechts nach links: w[2], w[1], w[0], wiederholt n-mal
        offs = [i for i in range(3) if w[2 - i] == "0"]  # Abstand vom rechten Blockende
        if w == "011":   # eine Null pro Block, ganz links im Block
            first = pos - 2
            g = prev - first
            if g == 3: k += 1
            else:
                out.append(f" {k} |" if g == 4 else f" {k} <{g}>"); k = 0
            k += n - 1               # weitere Nullen im Abstand 3
            prev = first - 3 * (n - 1)
        else:            # allgemein, Block fuer Block
            for j in range(n):
                for o in offs:
                    z = pos - 3 * j - o
                    g = prev - z
                    if g == 3: k += 1
                    else:
                        out.append(f" {k} |" if g == 4 else f" {k} <{g}>"); k = 0
                    prev = z
        pos -= 3 * n
    assert pos == lo - 1, (pos, lo)
    return " 0 |" + "".join(out) + f" {k}"


def lauf(N, modus, start):
    L, R = [], []
    q, seite = start, "R"
    pos = lo = hi = 0
    n = 0
    makro = {"S1": 0, "S2": 0, "E": 0}
    out = sys.stdout
    zaehl = {}; beispiele = []; vorher = "-"; letzte_richtung = 1; wende_pos = None; wende_c0 = False
    while n < N:
        if seite == "R" and q == C and R and R[-1][0] == "w" and R[-1][1] == "100" \
                and n + 3 * R[-1][2] <= N:
            m = R.pop()[2]
            if FEHLER == "s1_block" and m >= 5:   # letzter Block falsch: 111 statt 011
                push_wort(L, "011", m - 1); L.extend([("b", 1), ("b", 1), ("b", 1)])
            else:
                push_wort(L, "011", m)
            pos += 3 * m; n += 3 * m; makro["S1"] += 1; vorher = "S1"; letzte_richtung = 1
            if pos > hi:   # der letzte Schritt des Durchlaufs kann eine neue Zelle betreten
                hi = pos
                if modus == "liste":
                    out.write(f"{n} C {hi - lo + 1} lead" + nullabstaende(L, hi, lo) + "\n")
            continue
        if seite == "L" and q in (B, D) and L and L[-1][0] == "w" and L[-1][1] == "011" \
                and n + 3 * L[-1][2] <= N:
            m = L.pop()[2]
            push_wort(R, "100", m); pos -= 3 * m; n += 3 * m
            if m % 2 and FEHLER != "paritaet": q = D if q == B else B
            makro["S2"] += 1; vorher = "S2"; letzte_richtung = -1
            if pos < lo: lo = pos
            continue
        # Einzelschritt
        links = seite == "L"
        st = L if links else R
        if modus == "pruefen" and q == C and not links:
            z = peek(R, False, 3)
            if z[0] == 1 and z[1] == 1:   # C vor 11: genau die Pruefpunkte (B/D las davor 0)
                art = "nach_C0_Wende" if (wende_c0 and wende_pos == pos) else \
                      ("Durchlaufende" if vorher == "S1" else "sonst")
                zaehl[art] = zaehl.get(art, 0) + 1
                if z[2] == 1: zaehl["mit_111"] = zaehl.get("mit_111", 0) + 1
                if art != "nach_C0_Wende" and len(beispiele) < 20:
                    zellen = []
                    for tok in L:   # von unten (linkes Ende) nach oben
                        zellen.extend([tok[1]] if tok[0] == "b" else [int(c) for c in tok[1] * tok[2]])
                    rechts = peek(R, False, 12)
                    links_s = "".join(map(str, zellen[:pos - lo]))
                    beispiele.append((n, art, pos - lo, links_s[:40] + "[" + "".join(map(str, rechts)) + "...]"))
        s = pop_zelle(st, links)
        if (q, s) not in TAB:
            if modus == "zaehlen":
                print(f"HALT bei Schritt {n}")
            return
        w, d, nq = TAB[(q, s)]
        n += 1; makro["E"] += 1
        # letzte Wende von rechts nach links merken (wie zweitpruefung.c)
        if d == -1 and letzte_richtung == 1:
            wende_pos = pos; wende_c0 = (q == C and s == 0)
        letzte_richtung = d; vorher = "E"
        if d == 1:
            push_zelle(L, w, True); seite = "R"
        else:
            push_zelle(R, w, False); seite = "L"
        pos += d; q = nq
        if pos < lo: lo = pos
        if pos > hi:
            hi = pos
            if modus == "liste" and q == C:
                out.write(f"{n} C {hi - lo + 1} lead" + nullabstaende(L, hi, lo) + "\n")
    if modus == "pruefen":
        print(f"schritte={n} pruefpunkte={sum(v for k, v in zaehl.items() if k != 'mit_111')} {zaehl}")
        for b in beispiele: print("  Ausnahme bei Schritt", b)
    if modus == "zaehlen":
        print(f"schritte={n} makroschritte={sum(makro.values())} {makro} breite={hi - lo + 1} zustand={'ABCDEF'[q]}")


if __name__ == "__main__":
    N = int(sys.argv[1]); modus = sys.argv[2]
    start = ord(sys.argv[3]) - 65 if len(sys.argv) > 3 else A
    lauf(N, modus, start)
