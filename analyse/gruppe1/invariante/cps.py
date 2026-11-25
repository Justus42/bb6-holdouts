"""ERSTER, GESCHEITERTER ANSATZ (nur zur Dokumentation): n-Gramm-CPS mit Geisterzeichen.
Ergebnis bis n = 10: keine Regel bewiesen; die n-Gramme verlieren die Paritaet langer Laeufe nach den
Zickzack-Bewegungen. Ersetzt durch symb.py / zone.py.

Invariante gegen K(C) je Automatenregel: abgeschlossene Positionsmenge (n-Gramm-CPS) mit Geisterzeichen.

Tabelle 114: 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC (Zustaende A..F = 0..5).

Frage (Justus 25.11.): Kann waehrend einer Phase, auf die eine Automatenregel (N1, N2, N2s, UA, LE0, LE1, LG)
passt, C von links auf x treten mit x+1 = x+2 = 1 (K(C) = "C> 0 1 1" oder Halt "C> 1 1 1"), oder anders
gehalten werden?

Verfahren (Ueberapproximation, solide):
  * Startmenge: ALLE Schnappschuesse, auf die die Regel passt (Token-Bedingungen wie Band.schritt in
    linkes_ende/beschleuniger.py, r >= 1), fuer alle Zahlenwerte. Kopf in C auf Zelle p (0), p+1 = 0,
    p+2 = 1; ab p+3 eine "Wand" '#'.
  * Jede Zelle traegt neben dem Bit ein festes Geisterzeichen (Rolle des Tokens, Abstand vom rechten
    Token-Ende mod 6). Die Maschine liest nur das Bit; das Geisterzeichen bleibt an der Zelle und aendert
    nie etwas am Lauf. Es dient nur dazu, dass die n-Gramme Paritaeten "sehen".
  * Zellen links der Grenzumgebung (Rolle P) haben beliebige Bits. Liest der Kopf eine P-Zelle, gilt die
    Regel als "offen" (der Kopf verlaesst den beschriebenen Bereich).
  * Linkes Bandende (LE, LG): unendlich viele '_'-Zellen mit Bit 0.
  * CPS: Mengen der linken und rechten n-Gramme (vom Kopf nach aussen) und der lokalen Konfigurationen
    (Zustand, n links, Kopfzelle, n rechts); Abschluss unter allen Schritten. Jede erreichbare Konfiguration
    hat alle ihre n-Gramme in diesen Mengen (Induktion ueber die Schritte).
  * Betritt der Kopf die Wand (Zelle p+3) in Zustand C, ist die Phase zu Ende (dort liest C eine 0,
    p+3, p+4 = 0 0, danach (100)^(r-1) 1: das ist der naechste Schnappschuss). In jedem anderen Zustand:
    "offen".
  * Verboten: Zustand C mit Bits 1 1 in den zwei Zellen rechts vom Kopf (deckt K(C) und C vor 111 ab,
    egal aus welcher Richtung), Zustand A auf einer 1 (Halt).
Ergebnis je Regel: "BEWIESEN (n=...)" wenn der Abschluss ohne Verbotenes und ohne "offen" erreicht wird.
Sonst wird die erste Verletzung mit Weg (abstrakt) ausgegeben.

Aufruf: python3 -I cps.py <Regel|alle> [n_max]
Negativkontrollen (CPS_FEHLER): 'tabelle' (C1 -> 1RE statt 0RE: dann muss etwas Verbotenes erreichbar
sein), 'zone' (Zonen-Token auch gerade zulassen), 'wand' (keine Wand: Reservoir 100 100 ... beliebig).
"""
import os
import sys
from collections import deque

FEHLER = os.environ.get("CPS_FEHLER", "")
TAB = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
A, B, C, D, E, F = range(6)


def tabelle():
    T = {}
    for q, s in enumerate(TAB.split("_")):
        for b in range(2):
            e = s[3 * b:3 * b + 3]
            if e != "---":
                T[(q, b)] = (int(e[0]), 1 if e[1] == "R" else -1, ord(e[2]) - 65)
    if FEHLER == "tabelle":
        T[(C, 1)] = (1, 1, E)
    return T


T = tabelle()

# ------------------------------------------------------------------ Symbole
# Ein Symbol ist (bit, geist). geist: (rolle, j mod 6) fuer Token-Zellen, 'P' (beliebig), '_' (leer links),
# 'R0','R1','R2' (Zellen p, p+1, p+2), '#' (Wand).
SYM = {}
SYMLIST = []


def sym(bit, geist):
    k = (bit, geist)
    if k not in SYM:
        SYM[k] = len(SYMLIST)
        SYMLIST.append(k)
    return SYM[k]


def bit(s):
    return SYMLIST[s][0]


def geist(s):
    return SYMLIST[s][1]


# ------------------------------------------------------------------ Startsprache (linke Haelfte, vom Kopf nach aussen)
# NFA: Knoten -> Liste (symbol, folgeknoten). Segmente werden von rechts nach links (vom Kopf weg) verkettet.
class NFA:
    def __init__(self):
        self.kanten = []

    def knoten(self):
        self.kanten.append([])
        return len(self.kanten) - 1

    def kante(self, a, s, b):
        self.kanten[a].append((s, b))


def lauf_seg(nfa, ein, rolle, minu, par):
    """Lauf 011^k (k >= minu, k mod 2 == par oder par None), gelesen von rechts nach links.
    Zellen je Einheit i (von rechts): j=3i bit1, j=3i+1 bit1, j=3i+2 bit0. Rueckgabe: Liste von Ausgangsknoten
    (Knoten nach einer erlaubten Zahl von Einheiten) als einzelner Knoten mit Epsilon-freier Konstruktion:
    wir bauen Knoten (c, parity) und geben den Knoten 'aus' zurueck, an den Folgesegmente anschliessen."""
    # Zustaende: (c = min(k, minu), k mod 2); Einheit = 3 Zellen mit Geist abhaengig von k mod 2 (j mod 6)
    st = {}

    def S(c, p):
        if (c, p) not in st:
            st[(c, p)] = nfa.knoten()
        return st[(c, p)]

    # Anfang: k = 0
    erster = S(0, 0)
    # ein -> erster per Epsilon: wir geben 'erster' zurueck und der Aufrufer verbindet; einfacher: Epsilon-Liste
    todo = [(0, 0)]
    gesehen = set()
    while todo and par != "null":
        c, p = todo.pop()
        if (c, p) in gesehen:
            continue
        gesehen.add((c, p))
        a = S(c, p)
        # eine Einheit lesen: k -> k+1; Offset j = 3k .. 3k+2, j mod 6 = 3*(k mod 2) + 0..2
        c2, p2 = min(c + 1, minu), 1 - p
        m1, m2 = nfa.knoten(), nfa.knoten()
        nfa.kante(a, sym(1, (rolle, 3 * p + 0)), m1)
        nfa.kante(m1, sym(1, (rolle, 3 * p + 1)), m2)
        nfa.kante(m2, sym(0, (rolle, 3 * p + 2)), S(c2, p2))
        todo.append((c2, p2))
    if par == "null":
        return erster, [erster]
    ausgaenge = [S(c, p) for (c, p) in st if c >= minu and (par is None or p == par)]
    return erster, ausgaenge


def sep_seg(nfa, rolle, bits, par_von_lauf=None):
    """Trennerzelle (j = 3k): Geist (rolle, 'S')."""
    return [sym(b, (rolle, "S")) for b in bits]


def baue_links(spec):
    """spec: Liste von Teilen vom Kopf nach aussen:
       ('tok', rolle, minu, par, sepbits)   ein Token (Lauf, dann Trenner)
       ('zone',)                           beliebig viele regulaere Token (1, ungerade)
       ('ende', 'P' | '_')                 unendlicher Rest
    Rueckgabe (nfa, startknoten, endknoten_mit_schleife)."""
    nfa = NFA()
    start = nfa.knoten()
    frei = [start]       # Knoten, an die das naechste Teil angeschlossen wird (Epsilon-Ersatz: wir kopieren Kanten)
    eps = {}             # Epsilon-Kanten

    def verbinde(von_liste, nach):
        for v in von_liste:
            eps.setdefault(v, set()).add(nach)

    for teil in spec:
        if teil[0] == "tok":
            _, rolle, minu, par, sepbits = teil
            ein, aus = lauf_seg(nfa, None, rolle, minu, par)
            verbinde(frei, ein)
            nach = nfa.knoten()
            for a in aus:
                for s in sep_seg(nfa, rolle, sepbits):
                    nfa.kante(a, s, nach)
            frei = [nach]
        elif teil[0] == "zone":
            # Schleife: Knoten z; z -> Token -> z
            z = nfa.knoten()
            verbinde(frei, z)
            zpar = None if FEHLER == "zone" else 1
            ein, aus = lauf_seg(nfa, None, "Z", 1, zpar)
            verbinde([z], ein)
            for a in aus:
                for s in sep_seg(nfa, "Z", [1]):
                    nfa.kante(a, s, z)
            frei = [z]
        elif teil[0] == "ende":
            e = nfa.knoten()
            verbinde(frei, e)
            if teil[1] == "P":
                for b in (0, 1):
                    nfa.kante(e, sym(b, "P"), e)
            else:
                nfa.kante(e, sym(0, "_"), e)
            frei = []
    # Epsilon-Abschluss
    def abschluss(v):
        out = {v}
        st = [v]
        while st:
            x = st.pop()
            for y in eps.get(x, ()):
                if y not in out:
                    out.add(y)
                    st.append(y)
        return out
    kant = []
    for v in range(len(nfa.kanten)):
        ks = set()
        for x in abschluss(v):
            for s, y in nfa.kanten[x]:
                for z in abschluss(y):
                    ks.add((s, z))
        kant.append(ks)
    return kant, start


def ngramme(kant, start, n):
    """Alle Woerter der Laenge n, die als Teilwort (ab einer beliebigen erreichbaren Stelle) einer unendlichen
    linken Haelfte vorkommen. Erreichbare Knoten ab start; nur Knoten, von denen aus es unendlich weitergeht
    (alle Knoten fuehren hier zum Ende-Knoten mit Schleife, ausser Sackgassen; die werden gestutzt)."""
    N = len(kant)
    # Stutzen: Knoten, von denen ein unendlicher Weg ausgeht
    lebend = set(range(N))
    while True:
        neu = {v for v in lebend if any(y in lebend for _, y in kant[v])}
        if neu == lebend:
            break
        lebend = neu
    erreich = set()
    st = [start]
    while st:
        v = st.pop()
        if v in erreich or v not in lebend:
            continue
        erreich.add(v)
        for _, y in kant[v]:
            st.append(y)
    # Woerter der Laenge n ab jedem erreichbaren Knoten
    out = set()
    erste = set()
    front = {(v, ()) for v in erreich}
    for i in range(n):
        nf = set()
        for v, w in front:
            for s, y in kant[v]:
                if y in lebend:
                    nf.add((y, w + (s,)))
        front = nf
    for v, w in front:
        out.add(w)
    front = {(start, ())}
    for i in range(n):
        front = {(y, w + (s,)) for v, w in front for s, y in kant[v] if y in lebend}
    erste = {w for _, w in front}
    return out, erste


# ------------------------------------------------------------------ Regeln (Startsprachen)
# rechtestes Token T0: im Lauf (1, gerade >= 2) (Zyklusregel a(neu) = e3 + 2, Kandidat aus PR 9);
# Band.schritt prueft es nicht. Mit CPS_T0=frei wird T0 beliebig zugelassen.
LAST = ("tok", "L", 0, None, [0, 1]) if os.environ.get("CPS_T0") == "frei" else ("tok", "L", 2, 0, [1])
ZONE1 = ("tok", "Z", 1, 1, [1])
REGELN = {
    "N1": [LAST, ("zone",), ("tok", "K", 0, 0, [0]), ("ende", "P")],
    "N2": [LAST, ("zone",), ("tok", "K", 0, 0, [1]), ("tok", "G", 1, None, []), ("ende", "P")],
    "N2s": [LAST, ("zone",), ("tok", "K", 1, 1, [0]), ("tok", "G", 1, None, []), ("ende", "P")],
    "UA": [LAST, ("zone",), ("tok", "K", 1, 1, [0]), ("tok", "U", 0, "null", [1]), ("tok", "G", 1, None, []),
           ("ende", "P")],
    "LE0": [LAST, ("zone",), ("tok", "K", 0, "null", [1]), ("ende", "_")],
    "LE1": [LAST, ("zone",), ("tok", "K", 1, 1, [0]), ("tok", "U", 0, "null", [1]), ("ende", "_")],
    "LG": [LAST, ("zone",), ZONE1, ("ende", "_")],   # mindestens ein Token ausser T0 (len(T) >= 2)
}


def fix_run0(spec):
    """('tok', rolle, 0, 0, ...) mit Lauf genau 0 (fuer (1,0)) -> minu 0, par 0 erlaubt k = 0, 2, 4, ...
    Fuer U und LE0-K brauchen wir k = 0 exakt: Kennzeichen maxu=0."""
    return spec


# ------------------------------------------------------------------ CPS
def cps(regel, n, verbose=False):
    spec = REGELN[regel]
    if regel == "LG":
        # mindestens ein Zonen-Token (len(T) >= 2) -- Ueberapproximation mit 0 Token ist ebenfalls solide
        pass
    kant, start = baue_links_exakt(spec)
    Lg, Lerste = ngramme(kant, start, n)
    WAND = sym(0, "#")
    R0, R1, R2 = sym(0, "R0"), sym(0, "R1"), sym(1, "R2")
    if FEHLER == "wand":
        # Reservoir beliebig lang statt Wand: rechts 100 100 ... (Bits ohne Wand-Erkennung)
        rechts = [R1, R2] + [sym(0, "W"), sym(0, "W"), sym(1, "W")] * (n + 2)
        Rg = set()
        for i in range(len(rechts) - n + 1):
            Rg.add(tuple(rechts[i:i + n]))
        Rg.add(tuple(([sym(0, "W"), sym(0, "W"), sym(1, "W")] * (n + 2))[1:1 + n]))
        Rg.add(tuple(([sym(0, "W"), sym(0, "W"), sym(1, "W")] * (n + 2))[2:2 + n]))
        rstart = tuple(rechts[:n])
    else:
        rechts = [R1, R2] + [WAND] * (n + 1)
        Rg = {tuple(rechts[i:i + n]) for i in range(3)}
        rstart = tuple(rechts[:n])
    Lg = set(Lg)
    konf = set()
    queue = deque()
    herkunft = {}
    for l in Lerste:
        k = (C, l, R0, rstart)
        konf.add(k)
        queue.append(k)
        herkunft[k] = None
    # Abhaengigkeiten: wenn ein n-Gramm dazukommt, muessen alle Konfigurationen erneut expandiert werden,
    # deren Fortsetzung davon abhaengt. Einfach: Index nach (n-1)-Praefix.
    l_idx = {}
    r_idx = {}
    for g in Lg:
        l_idx.setdefault(g[:-1], set()).add(g[-1])
    for g in Rg:
        r_idx.setdefault(g[:-1], set()).add(g[-1])
    warte_l = {}   # (n-1)-Praefix -> Konfigurationen, die darauf warten
    warte_r = {}

    def fehler(k, grund):
        return {"ergebnis": "OFFEN", "grund": grund, "konf": k, "weg": weg(k)}

    def weg(k):
        w = []
        while k is not None and len(w) < 60:
            w.append(k)
            k = herkunft.get(k)
        return list(reversed(w))

    def add_konf(k, von):
        if k not in konf:
            konf.add(k)
            herkunft[k] = von
            queue.append(k)

    def add_l(g, von_list):
        if g not in Lg:
            Lg.add(g)
            p = g[:-1]
            l_idx.setdefault(p, set()).add(g[-1])
            for k in warte_l.get(p, ()):
                queue.append(k)

    def add_r(g):
        if g not in Rg:
            Rg.add(g)
            p = g[:-1]
            r_idx.setdefault(p, set()).add(g[-1])
            for k in warte_r.get(p, ()):
                queue.append(k)

    while queue:
        k = queue.popleft()
        q, l, s, r = k
        b = bit(s)
        gs = geist(s)
        if gs == "P":
            return fehler(k, "Kopf liest Zelle ausserhalb des beschriebenen Bereichs (P)")
        if gs == "#":
            return fehler(k, "Kopf auf der Wand")
        if q == A and b == 1:
            return fehler(k, "Halt (A liest 1)")
        if q == C and bit(r[0]) == 1 and bit(r[1]) == 1:
            return fehler(k, "C vor ?11 (K(C) oder Halt)")
        if (q, b) not in T:
            return fehler(k, "Halt")
        w, d, q2 = T[(q, b)]
        neu = sym(w, gs)
        if d == 1:
            # neue Kopfzelle r[0]
            if geist(r[0]) == "#":
                if q2 == C:
                    continue   # Phasenende
                return fehler(k, f"Wand in Zustand {'ABCDEF'[q2]}")
            gl = (neu,) + l[:-1]
            add_l((neu,) + l[:n - 1] if n > 1 else (neu,), None)
            praef = r[1:]
            warte_r.setdefault(praef, set()).add(k)
            for x in list(r_idx.get(praef, ())):
                nr = praef + (x,)
                add_konf((q2, gl, r[0], nr), k)
        else:
            gr = (neu,) + r[:-1]
            add_r((neu,) + r[:n - 1])
            praef = l[1:]
            warte_l.setdefault(praef, set()).add(k)
            for x in list(l_idx.get(praef, ())):
                nl = praef + (x,)
                add_konf((q2, nl, l[0], gr), k)
    return {"ergebnis": "BEWIESEN", "n": n, "konf": len(konf), "lg": len(Lg), "rg": len(Rg)}


def baue_links_exakt(spec):
    """Wie baue_links, aber Token mit genau 0 Einheiten (Rolle U, LE0-K) exakt: minu 0, par 0 und max 0."""
    spec2 = []
    for teil in spec:
        spec2.append(teil)
    nfa_k, start = baue_links(spec2)
    return nfa_k, start


def zeige(k):
    q, l, s, r = k
    def f(x):
        b, g = SYMLIST[x]
        return f"{b}{'' if isinstance(g, str) else g[0] + str(g[1])}" if not isinstance(g, str) else f"{b}{g}"
    return f"{'ABCDEF'[q]} | {' '.join(f(x) for x in reversed(l))} [{f(s)}] {' '.join(f(x) for x in r)}"


def main():
    regel = sys.argv[1]
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    regeln = list(REGELN) if regel == "alle" else [regel]
    gesamt = 0
    for rg in regeln:
        for n in range(2, nmax + 1):
            res = cps(rg, n)
            if res["ergebnis"] == "BEWIESEN":
                print(f"{rg:4s} BEWIESEN mit n={n}: {res['konf']} lokale Konfigurationen, "
                      f"{res['lg']} linke / {res['rg']} rechte n-Gramme")
                gesamt += 1
                break
        else:
            print(f"{rg:4s} OFFEN bis n={nmax}: {res['grund']}")
            for k in res["weg"][-12:]:
                print("    ", zeige(k))
    print(f"bewiesen {gesamt} von {len(regeln)}")


if __name__ == "__main__":
    main()
