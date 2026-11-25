"""Beschleuniger auf Zyklusebene fuer Tabelle 114 (Gruppe 1), mit Halteprüfung.

Baut auf linkes_ende/beschleuniger.py auf (gleicher Zustand an Phasen-Schnappschuessen, gleiche Regeln,
gleiche Kostenformel), mit drei Aenderungen:

1. N2/N1-Paare gebuendelt: Steht die Grenze auf (1,k), k gerade, und links davon liegen M regulaere Token
   (1, ungerade), dann laufen die naechsten 2P Phasen (P = min(M, r//2)) als P Paare N2, N1 ab:
     Grenze (1,k) -> (1,k+3); die P-1 Token links davon je +2; das P-te Token links -1 (neue Grenze).
   Schritte: Summe der Kostenformel ueber alle 2P Phasen, geschlossen gerechnet (numpy). Gleiche
   Rechnung wie 2P Einzelphasen von beschleuniger.Band (Abgleich: Modus pruef).
2. Rueckfaelle (VS, "nicht anwendbar", Zyklusuebergang r = 0) lokal: lange Laeufe regulaerer Token in
   der Liste werden auf je K Token an beiden Seiten verkuerzt, das Durchlaufmodell rechnet die kurze
   Liste, die Laeufe werden wieder eingesetzt. Die Schritte fuer die weggelassenen Token werden je Lauf
   geeicht (zwei Zusatzrechnungen mit einem eingefuegten Token (1,1) bzw. (1,3)). Klappt das Einsetzen
   nicht eindeutig, wird die ganze Liste gerechnet. Modus pruef rechnet jeden Rueckfall zusaetzlich ganz
   und vergleicht.
3. Halteprüfung: In jeder durchgerechneten (lokalen) Phase wird das notwendige Muster K(C) gezaehlt
   (Zustand C tritt von links auf eine Zelle mit 0 1 1) und Halt erkannt. Fuer Automatenphasen gilt:
   kein Halt, SOFERN die Regel fuer diese Liste stimmt und in ihr kein K(C) entsteht (geprueft:
   zaehl_direkt.c bis 10^12 je Regel, regel_test.py zufaellig; nicht bewiesen). Eine Automatenregel wird
   nur angewandt, wenn das rechteste Token (1, gerade >= 2) ist (Bedingung von regel_test.py), sonst
   Rueckfall.

Aufruf: python3 -I zyklus_beschl.py <A|C|D> <Schritte> lauf|pruef [<datei r=0-Schnappschuesse>]
  lauf : so weit wie moeglich, Zusammenfassung je Zehnerpotenz.
  pruef: zusaetzlich jeden Rueckfall ganz rechnen und vergleichen; Schnappschuesse bei r = 0 als
         "n 0 crc" (wie beschleuniger.py pruef) in die Datei.
Negativkontrolle: ZB_FEHLER=paar (Paarkosten +1 je Paar), ZB_FEHLER=lokal (Eichung um 1 falsch) bzw.
  ZB_FEHLER=ueb (Zyklusuebergang 1 Schritt zu viel):
  der Abgleich mit beschleuniger.py muss dann scheitern.
"""
import bisect
import os
import sys

import numpy as np

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "linkes_ende"))
sys.path.insert(0, HIER)
import beschleuniger as bs  # noqa: E402
import zaehl_beschl as zb  # noqa: E402
from zaehl_durchlauf import Zaehler  # noqa: E402

FEHLER = os.environ.get("ZB_FEHLER", "")
K = 8              # Token, die an jedem Ende eines verkuerzten Laufs stehen bleiben
RL, RR = 80, 40    # Token am linken / rechten Ende, die nie verkuerzt werden
KOST = {"N1": 11, "N2": 21, "N2s": 15, "UA": 15, "LE0": 25, "LE1": 17, "LG": 11}
SEP = {"0": 0, "1": 1, "": 2}
SEPS = ["0", "1", ""]


def regulaer_tok(t):
    return t[0] == "1" and t[1] % 2 == 1


class ZBand:
    """Token-Liste von links nach rechts in numpy-Feldern sep/val, belegt [lo, hi)."""

    def __init__(self, tok, tail):
        cap = max(1 << 16, 8 * len(tok))
        self.sep = np.zeros(cap, np.int8)
        self.val = np.zeros(cap, np.int64)
        self.lo = cap // 2
        self.hi = self.lo
        self.tail = tail
        self.setze_liste(tok)

    # ---- Grundoperationen
    def setze_liste(self, tok):
        n = len(tok)
        if n + 16 > len(self.val) // 2:
            cap = 8 * n
            self.sep = np.zeros(cap, np.int8)
            self.val = np.zeros(cap, np.int64)
        mitte = len(self.val) // 2
        self.lo = mitte - n // 2
        self.hi = self.lo + n
        if n:
            self.sep[self.lo:self.hi] = [SEP[t] for t, _ in tok]
            self.val[self.lo:self.hi] = [v for _, v in tok]
        self.neu_irr()

    def tok(self):
        s = self.sep[self.lo:self.hi].tolist()
        v = self.val[self.lo:self.hi].tolist()
        return [(SEPS[a], b) for a, b in zip(s, v)]

    def neu_irr(self):
        s = self.sep[self.lo:self.hi]
        v = self.val[self.lo:self.hi]
        self.irr = (np.flatnonzero(~((s == 1) & ((v & 1) == 1))) + self.lo).tolist()

    def regulaer(self, i):
        return self.sep[i] == 1 and self.val[i] & 1

    def setz(self, i, s, v):
        war = not self.regulaer(i)
        self.sep[i] = s
        self.val[i] = v
        ist = not self.regulaer(i)
        if war != ist:
            k = bisect.bisect_left(self.irr, i)
            if ist:
                self.irr.insert(k, i)
            else:
                del self.irr[k]

    def letztes_irr_vor(self, i):
        """groesster irregulaerer Index < i, sonst None."""
        k = bisect.bisect_left(self.irr, i)
        return self.irr[k - 1] if k > 0 else None

    def vorn_weg(self):
        """linkestes Token entfernen."""
        if self.irr and self.irr[0] == self.lo:
            del self.irr[0]
        self.lo += 1

    def vorn_dran(self, s, v):
        if self.lo == 0:
            self.setze_liste(self.tok())
        self.lo -= 1
        self.sep[self.lo] = s
        self.val[self.lo] = v
        if not self.regulaer(self.lo):
            self.irr.insert(0, self.lo)

    def summe(self, a, b):
        return int(self.val[a:b].sum()) if b > a else 0


class Lauf:
    def __init__(self, start, modus, schnapp=None):
        n, tok, tail, r = bs.anlauf(start, 10**30)
        self.n, self.r = n, r
        self.b = ZBand(tok, tail)
        self.modus = modus
        self.zaehl = {}
        self.kc = 0              # K(C) in durchgerechneten Phasen
        self.halt = None
        self.vergleich_fehler = 0
        self.lokal_ganz = 0      # Rueckfaelle, bei denen das Einsetzen nicht ging (ganz gerechnet)
        self.phasen = 0
        self.zyklen = 0
        self.out = open(schnapp, "w") if schnapp else None
        self.grenze_neu()

    def z(self, k, d=1):
        self.zaehl[k] = self.zaehl.get(k, 0) + d

    # ---- Grenze und S (wie Band: j = Zahl der Token rechts der Grenze, S = deren Summe)
    def grenze_neu(self):
        b = self.b
        if b.hi - b.lo == 0:
            self.p = None
            self.S = 0
            return
        self.p = b.letztes_irr_vor(b.hi - 1)
        a = (self.p + 1) if self.p is not None else b.lo
        self.S = b.summe(a, b.hi)

    def weiter_ab(self, p_alt):
        """Grenze von p_alt (jetzt regulaer) nach links zum naechsten irregulaeren Token; S nachziehen."""
        b = self.b
        q = b.letztes_irr_vor(p_alt)
        a = (q + 1) if q is not None else b.lo
        self.S += b.summe(a, p_alt + 1)
        self.p = q

    # ---- ein Automatenschritt (wie Band.schritt) oder ein Paar-Buendel
    def schritt(self):
        b = self.b
        L = b.hi - b.lo
        if b.tail != "" or L < 2:
            return "rest", None
        if not (b.sep[b.hi - 1] == 1 and b.val[b.hi - 1] % 2 == 0 and b.val[b.hi - 1] >= 2):
            return "rechts?", None
        p = self.p
        if p is None:   # LG
            j = L
            kosten = 12 * self.S - 2 * j + KOST["LG"]
            b.vorn_dran(1, 1)
            self.S += 1
            return "LG", kosten
        j = b.hi - 1 - p
        s, k = int(b.sep[p]), int(b.val[p])
        kosten0 = 12 * self.S - 2 * j + 12 * k
        if s == 0 and k % 2 == 0:
            b.setz(p, 1, k + 1)
            self.weiter_ab(p)
            return "N1", kosten0 + KOST["N1"]
        if p == b.lo:
            if s == 1 and k == 0:
                b.vorn_weg()
                b.setz(b.lo, 1, int(b.val[b.lo]) + 2)
                self.grenze_neu()
                return "LE0", kosten0 + KOST["LE0"]
            return "links?", None
        sg, g = int(b.sep[p - 1]), int(b.val[p - 1])
        if p == b.lo + 1 and sg == 1 and g == 0 and s == 0 and k % 2 == 1:
            b.vorn_weg()
            b.setz(p, 1, k + 2)
            self.grenze_neu()
            return "LE1", kosten0 + KOST["LE1"]
        if g >= 1 and ((s == 0 and k % 2 == 1) or (s == 1 and k % 2 == 0)):
            if s == 1 and self.r >= 4:
                erg = self.paare(p, j, k)
                if erg is not None:
                    return erg
            b.setz(p - 1, sg, g - 1)
            b.setz(p, 0, k + 2)
            return ("N2s" if s == 0 else "N2"), kosten0 + KOST["N2s" if s == 0 else "N2"]
        if s == 0 and k % 2 == 1 and sg == 1 and g == 0 and p - 2 >= b.lo and b.val[p - 2] >= 1:
            b.setz(p - 2, int(b.sep[p - 2]), int(b.val[p - 2]) - 1)
            b.setz(p - 1, 0, 0)
            b.setz(p, 1, k + 2)
            self.S += k + 2
            self.p = p - 1
            return "UA", kosten0 + KOST["UA"]
        if s == 1 and k % 2 == 0 and k >= 2 and sg == 1 and g == 0:
            return "VS", None
        return "Sonder", None

    def paare(self, p, j, k):
        """P Paare N2, N1 auf einmal (siehe Kopf). Rueckgabe ("PAAR", kosten) oder None (P < 2)."""
        b = self.b
        q = b.letztes_irr_vor(p)
        start = (q + 1) if q is not None else b.lo
        M = p - start                     # regulaere Token links der Grenze
        P = min(M, self.r // 2)
        if P < 2:
            return None
        kk = b.val[p - P + 1:p + 1][::-1].copy()   # val[p], val[p-1], ..., val[p-P+1]
        kk[1:] -= 1
        kk[0] = k
        c = kk + 3
        sc = int(c.sum())
        idx = np.arange(P, dtype=np.int64)
        s_lc = int((c * (P - 1 - idx)).sum())       # sum_i sum_{l<i} c_l
        sum_S = P * self.S + s_lc
        kosten = 24 * sum_S - 4 * (P * j + P * (P - 1) // 2) + 24 * int(kk.sum()) + 56 * P
        if FEHLER == "paar":
            kosten += P
        # Band nachziehen
        b.setz(p, 1, k + 3)
        b.val[p - P + 1:p] += 2                     # bleiben regulaer
        b.setz(p - P, 1, int(b.val[p - P]) - 1)     # wird gerade -> neue Grenze
        self.S += sc
        self.p = p - P
        self.r -= 2 * P - 1                          # das letzte -1 macht die Hauptschleife
        self.z("N2", P)
        self.z("N1", P)
        self.phasen += 2 * P
        return "PAAR", kosten

    # ---- Rueckfall
    def rueckfall(self, art):
        b = self.b
        X = b.tok()
        tail = b.tail
        try:
            erg = (uebergang(X, tail, self) if self.r == 0 else None) or lokal(X, tail, self.r, self)
        except bs.Halt as h:
            self.halt = self.n + h.args[0]
            raise
        if self.modus == "pruef":
            zb.Z = {"ueb": Zaehler(), "vs": Zaehler(), "na": Zaehler()}
            ganz = bs.rueckfall(X, tail, self.r)
            if ganz[:4] != erg[:4]:
                self.vergleich_fehler += 1
                print(f"ABWEICHUNG lokal/ganz bei n={self.n} art={art} dn {erg[3]} / {ganz[3]}", flush=True)
        t2, tl2, r2, dn = erg[:4]
        b.tail = tl2
        b.setze_liste(t2)
        self.n += dn
        self.r = r2
        self.grenze_neu()

    def lauf(self, N):
        naechste = 10
        while self.n < N and self.halt is None:
            if self.r == 0:
                self.zyklen += 1
                if self.out:
                    self.out.write(f"{self.n} 0 {bs.crc(self.b.tok(), self.b.tail)}\n")
                self.rueckfall("ueb")
                self.z("ueb")
                self.phasen += 1
            else:
                g, kosten = self.schritt()
                if kosten is not None:
                    self.n += kosten
                    self.r -= 1
                    if g != "PAAR":
                        self.z(g)
                        self.phasen += 1
                else:
                    self.rueckfall(g)
                    self.z("rf:" + g)
                    self.phasen += 1
            while self.n >= naechste:
                self.bericht(f"10^{len(str(naechste)) - 1}")
                naechste *= 10
        self.bericht("ende")
        if self.out:
            self.out.close()

    def bericht(self, k):
        print(f"{k}: n={self.n} phasen={self.phasen} zyklen={self.zyklen} token={self.b.hi - self.b.lo} "
              f"K(C)={self.kc} halt={self.halt} lokal_ganz={self.lokal_ganz} abweichungen={self.vergleich_fehler} "
              f"{dict(sorted(self.zaehl.items()))}", flush=True)


# ---------------------------------------------------------------- lokale Rueckfall-Rechnung
def rechne(X, tail, r, lauf):
    """Durchlaufmodell auf X (wie beschleuniger.rueckfall), zaehlt nur K(C): Zustand C tritt von links auf
    eine Zelle mit 0 1 1. Rueckgabe (Y, tail, r', dn, Zahl K(C))."""
    sm = bs.sm
    A_, B_, C_, D_ = 0, 1, 2, 3
    L = bs.l_aus_token(X, tail)
    R = [("b", 1)]
    if r:
        R.append(("w", "100", r))
    R += [("b", 0), ("b", 0)]
    q, seite = C_, "R"
    n = 0
    kc = 0
    erster = True
    TAB = sm.TAB
    while True:
        if not erster and q == C_:
            rr = None
            if seite == "R" and sm.peek(R, False, 2) == [0, 0]:
                rr = bs.rechts_muster(R, "z1")
            elif seite == "L" and sm.peek(L, True, 1) == [0]:
                rr = bs.rechts_muster(R, "z2")
            if rr is not None:
                tk, tl = bs.canon(bs.bits_aus_l(L) if seite == "R" else bs.bits_aus_l(L)[:-1])
                return tk, tl, rr, n, kc
        erster = False
        if seite == "R" and q == C_ and R and R[-1][0] == "w" and R[-1][1] == "100":
            m = R.pop()[2]
            # letzter Eintritt des Durchlaufs: C auf die Zelle hinter dem Block (im Inneren immer 1 0 0)
            if sm.peek(R, False, 3) == [0, 1, 1]:
                kc += 1
            sm.push_wort(L, "011", m)
            n += 3 * m
            continue
        if seite == "L" and q in (B_, D_) and L and L[-1][0] == "w" and L[-1][1] == "011":
            m = L.pop()[2]
            sm.push_wort(R, "100", m)
            n += 3 * m
            if m % 2:
                q = D_ if q == B_ else B_
            continue
        links = seite == "L"
        st = L if links else R
        c = sm.pop_zelle(st, links)
        if (q, c) not in TAB:
            raise bs.Halt(n)
        w, d, nq = TAB[(q, c)]
        n += 1
        if d == 1:
            sm.push_zelle(L, w, True)
            seite = "R"
            if nq == C_ and sm.peek(R, False, 3) == [0, 1, 1]:
                kc += 1
        else:
            sm.push_zelle(R, w, False)
            seite = "L"
        q = nq


def lokal(X, tail, r, lauf):
    L = len(X)
    # Laeufe regulaerer Token, die verkuerzt werden: Laenge > 2K + 2, nicht das rechteste Token
    # Nur im Inneren: die ersten RL und die letzten RR Token bleiben immer stehen (dort aendern
    # VS/Randschritte und Fressen/J die Liste auch ueber mehrere regulaere Token hinweg).
    laeufe = []
    i = RL
    while i < L - RR:
        if regulaer_tok(X[i]):
            a = i
            while i < L - RR and regulaer_tok(X[i]):
                i += 1
            if i - a > 2 * K + 2:
                laeufe.append((a, i))
        else:
            i += 1
    if not laeufe:
        t2, tl2, r2, dn, kc = rechne(X, tail, r, lauf)
        lauf.kc += kc
        return t2, tl2, r2, dn
    # kurze Liste bauen
    kurz = []
    schnitt = []      # (Position des Schnitts in kurz, weggelassene Token)
    pos = 0
    for a, e in laeufe:
        kurz.extend(X[pos:a + K])
        schnitt.append((len(kurz), X[a + K:e - K]))
        pos = e - K
    kurz.extend(X[pos:])
    Y, tl2, r2, dn, kc = rechne(kurz, tail, r, lauf)
    lauf.kc += kc
    ergebnis = einsetzen(kurz, Y, schnitt)
    if ergebnis is None:
        lauf.lokal_ganz += 1
        t2, tl2b, r2b, dnb, kcb = rechne(X, tail, r, lauf)
        lauf.kc += kcb - kc
        return t2, tl2b, r2b, dnb
    # Eichung je Schnitt: ein Token (1,1) bzw. (1,3) zusaetzlich einsetzen
    extra = 0
    for si, (sp, weg) in enumerate(schnitt):
        d = []
        for wert in (1, 3):
            kurz2 = kurz[:sp] + [("1", wert)] + kurz[sp:]
            Y2, _, r22, dn2, _ = rechne(kurz2, tail, r, lauf)
            schnitt2 = [(p + (1 if j > si else 0), w) for j, (p, w) in enumerate(schnitt)]
            schnitt2[si] = (sp + 1, weg)
            # das eingefuegte Token muss unveraendert durchgereicht werden
            if r22 != r2 or einsetzen(kurz2, Y2, schnitt2, pruef_extra=(si, wert)) is None:
                lauf.lokal_ganz += 1
                t2, tl2b, r2b, dnb, kcb = rechne(X, tail, r, lauf)
                lauf.kc += kcb - kc
                return t2, tl2b, r2b, dnb
            d.append(dn2 - dn)
        alpha = (d[1] - d[0]) // 2
        beta = d[0] - alpha
        if alpha * 2 != d[1] - d[0]:
            raise RuntimeError("Eichung nicht ganzzahlig")
        if FEHLER == "lokal":
            beta += 1
        extra += alpha * sum(v for _, v in weg) + beta * len(weg)
    return ergebnis, tl2, r2, dn + extra


BMIN = 16


def uebergang(X, tail, lauf):
    """Zyklusuebergang (r = 0): die Fressphase dauert b Runden (b = n des vorletzten Tokens). Statt sie
    ganz zu rechnen: lokal fuer b' = b0, b0+2, b0+4, b0+6 (b0 = 4 oder 5, gleiche Paritaet wie b).
    Verlangt: gleiche Token-Liste fuer alle b', r' linear und dn quadratisch in b' (vierter Wert als
    Probe). Dann r' und dn fuer das echte b durch Fortsetzen. Sonst None (normale Rechnung)."""
    if tail != "" or len(X) < 6:
        return None
    sb, b = X[-2]
    if b < BMIN:
        return None
    b0 = 4 + (b % 2)
    werte = []
    for i in range(4):
        X2 = X[:-2] + [(sb, b0 + 2 * i), X[-1]]
        werte.append(lokal(X2, tail, 0, lauf))
    Y = werte[0][0]
    if any(w[0] != Y or w[1] != werte[0][1] for w in werte):
        lauf.z("ueb:eichung_liste")
        return None
    rr = [w[2] for w in werte]
    dd = [w[3] for w in werte]
    if rr[2] - 2 * rr[1] + rr[0] != 0 or rr[3] - 2 * rr[2] + rr[1] != 0:
        lauf.z("ueb:eichung_r")
        return None
    d1 = [dd[i + 1] - dd[i] for i in range(3)]
    d2 = [d1[i + 1] - d1[i] for i in range(2)]
    if d2[0] != d2[1]:
        lauf.z("ueb:eichung_dn")
        return None
    t = (b - b0) // 2
    r_echt = rr[0] + t * (rr[1] - rr[0])
    dn_echt = dd[0] + t * d1[0] + t * (t - 1) // 2 * d2[0]
    if FEHLER == "ueb":
        dn_echt += 1
    lauf.z("ueb:geeicht")
    return Y, werte[0][1], r_echt, dn_echt


def einsetzen(kurz, Y, schnitt, pruef_extra=None):
    """Weggelassene Token wieder einsetzen. Jeder Schnitt ist von K Token je Seite eingerahmt; dieser Block
    (2K Token) muss in Y genau an einer Stelle stehen, mit derselben Verschiebung fuer alle Schnitte."""
    kandidaten = None
    for sp, _ in schnitt:
        block = kurz[sp - K:sp + K]
        lagen = set()
        for d in range(-40, 41):
            a = sp - K + d
            if 0 <= a and a + 2 * K <= len(Y) and Y[a:a + 2 * K] == block:
                lagen.add(d)
        kandidaten = lagen if kandidaten is None else (kandidaten & lagen)
    if kandidaten is None or len(kandidaten) != 1:
        return None
    d = kandidaten.pop()
    out = []
    pos = 0
    for sp, weg in schnitt:
        out.extend(Y[pos:sp + d])
        out.extend(weg)
        pos = sp + d
    out.extend(Y[pos:])
    return out


if __name__ == "__main__":
    st = ord(sys.argv[1]) - 65
    N = int(float(sys.argv[2]))
    modus = sys.argv[3]
    lauf = Lauf(st, modus, sys.argv[4] if len(sys.argv) > 4 else None)
    try:
        lauf.lauf(N)
    except bs.Halt:
        print(f"HALT im Durchlaufmodell bei Schritt {lauf.halt}")
        lauf.bericht("halt")
