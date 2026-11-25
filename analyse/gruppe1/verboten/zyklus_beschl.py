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
4. Zweite Sicherung (Justus, 25.11.): ab STICH_AB (10^12) an STICH_JE (30) Stellen je Zehnerpotenz eine
   zufaellige Automatenphase ganz mit dem Durchlaufmodell rechnen (Halt, K(C)) und mit der Regel vergleichen.
5. Haltekandidat: Halt in einer gerechneten Phase -> Schnappschuss davor als kandidat_<Start>_<n>.txt.gz und
   als BASE64-Zeile im Log, Lauf stoppt (nachrechnen: kandidat_nachrechnen.py). K(C) (notwendig, nicht
   hinreichend) -> Schnappschuss, Lauf geht weiter, die naechsten VERFOLGEN (5) Phasen ganz im Durchlaufmodell.

Aufruf: python3 -I zyklus_beschl.py <A|C|D> <Schritte> lauf|pruef [<datei r=0-Schnappschuesse>|-] [<STICH_AB>]
  lauf : so weit wie moeglich, Zusammenfassung je Zehnerpotenz.
  pruef: zusaetzlich jeden Rueckfall ganz rechnen und vergleichen; Schnappschuesse bei r = 0 als
         "n 0 crc" (wie beschleuniger.py pruef) in die Datei.
Negativkontrolle: ZB_FEHLER=paar (Paarkosten +1 je Paar), ZB_FEHLER=lokal (Eichung um 1 falsch) bzw.
  ZB_FEHLER=ueb (Zyklusuebergang 1 Schritt zu viel):
  der Abgleich mit beschleuniger.py muss dann scheitern. ZB_FEHLER=stich (Stichprobe: Regelkosten +1) muss
  einen Kandidaten melden; ZB_FEHLER=kc (einmal K(C) vorgetaeuscht ab 10^9) muss Schnappschuss und 5 verfolgte
  Phasen zeigen, ohne die Schrittzahl zu aendern.
"""
import base64
import bisect
import gzip
import random
import time
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
STICH_AB = 10**12   # Stichproben ab hier
STICH_JE = 30       # Stichproben je Zehnerpotenz


VERFOLGEN = 5       # nach K(C): so viele Phasen einzeln ganz mit dem Durchlaufmodell


T0 = time.time()


class Stop(Exception):
    pass


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

    def kurz(self):
        """Verkuerzte Liste fuer eine lokale Rechnung: Laeufe regulaerer Token im Inneren (nicht in den
        ersten RL und letzten RR Token) mit mehr als 2K+2 Token werden bis auf je K Token an beiden Seiten
        weggelassen. Rueckgabe (kurz, schnitte); schnitte = [(Position in kurz, a, e)], weggelassen ist
        [a, e) im Feld."""
        lo, hi = self.lo, self.hi
        grenzen = [lo + RL - 1] + [i for i in self.irr if lo + RL <= i < hi - RR] + [hi - RR]
        teile = []
        for x, y in zip(grenzen, grenzen[1:]):
            a0, e0 = x + 1, y          # regulaerer Lauf [a0, e0)
            if e0 - a0 > 2 * K + 2:
                teile.append((a0 + K, e0 - K))
        kurz = []
        schnitte = []
        pos = lo
        for a, e in teile:
            kurz.extend(zip([SEPS[c] for c in self.sep[pos:a].tolist()], self.val[pos:a].tolist()))
            schnitte.append((len(kurz), a, e))
            pos = e
        kurz.extend(zip([SEPS[c] for c in self.sep[pos:hi].tolist()], self.val[pos:hi].tolist()))
        return kurz, schnitte

    def einsetzen(self, Y, d, schnitte, lkurz):
        """Ergebnis Y der kurzen Rechnung zurueckschreiben; alle Schnitte sind in Y um d verschoben."""
        if not schnitte:
            self.setze_liste(Y)
            return
        sp0, a0, _ = schnitte[0]
        spl, _, el = schnitte[-1]
        neu_lo = a0 - (sp0 + d)
        neu_hi = el + (len(Y) - (spl + d))
        if neu_lo < 0 or neu_hi > len(self.val):
            # Feld zu klein: ganz neu aufbauen
            out = []
            pos = 0
            for sp, a, e in schnitte:
                out.extend(Y[pos:sp + d])
                out.extend(zip([SEPS[c] for c in self.sep[a:e].tolist()], self.val[a:e].tolist()))
                pos = sp + d
            out.extend(Y[pos:])
            self.setze_liste(out)
            return
        def schreib(ziel, stueck):
            if stueck:
                self.sep[ziel:ziel + len(stueck)] = [SEP[t] for t, _ in stueck]
                self.val[ziel:ziel + len(stueck)] = [v for _, v in stueck]
        schreib(neu_lo, Y[0:sp0 + d])
        for (sp, a, e), (sp2, a2, e2) in zip(schnitte, schnitte[1:]):
            schreib(e, Y[sp + d:sp2 + d])
        schreib(el, Y[spl + d:])
        self.lo, self.hi = neu_lo, neu_hi
        self.neu_irr()

    def summe(self, a, b):
        return int(self.val[a:b].sum()) if b > a else 0


class Lauf:
    def __init__(self, start, modus, schnapp=None, stich_ab=None):
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
        self.start = "ABCDEF"[start]
        # Stichproben: ab STICH_AB an STICH_JE Stellen je Zehnerpotenz (gleichmaessig in log n) wird eine
        # zufaellige Automatenphase im naechsten Zyklus ganz mit dem Durchlaufmodell gerechnet
        self.rng = random.Random(1000 + start)
        self.stich_ziel_n = stich_ab if stich_ab is not None else STICH_AB
        self.ziel_r = None
        self.stich = {"gerechnet": 0, "gleich": 0, "rueckfall": 0}
        self.kc_auftreten = []   # n der Schnappschuesse vor K(C)
        self.verfolgen = 0       # noch einzeln zu rechnende Phasen nach K(C)
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
            if s == 1 and self.r >= 4 and self.r != self.ziel_r:
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
        if self.ziel_r is not None and self.r > self.ziel_r:
            P = min(P, (self.r - self.ziel_r) // 2)
        if P < 2:
            return None
        kk = b.val[p - P + 1:p + 1][::-1].copy()   # val[p], val[p-1], ..., val[p-P+1]
        kk[1:] -= 1
        kk[0] = k
        c = kk + 3
        sc = int(c.sum())
        idx = np.arange(P, dtype=np.int64)
        if int(c.max()) * P * P >= 2**62:          # int64 koennte ueberlaufen: mit Python-Zahlen rechnen
            s_lc = sum(int(x) * (P - 1 - i) for i, x in enumerate(c.tolist()))
            self.z("paar:gross")
        else:
            s_lc = int((c * (P - 1 - idx)).sum())   # sum_i sum_{l<i} c_l
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
    def sichern(self):
        b = self.b
        return (b.sep[b.lo:b.hi].copy(), b.val[b.lo:b.hi].copy(), b.tail, self.n, self.r)

    def kandidat(self, grund, gesichert, stop=True):
        """Haltekandidat oder Abweichung: Schnappschuss davor sichern (Datei und Log), Lauf beenden.
        stop=False (Auftreten von K(C)): nur sichern; das Muster ist notwendig, nicht hinreichend, der Lauf
        geht weiter und die folgenden VERFOLGEN Phasen werden einzeln ganz mit dem Durchlaufmodell gerechnet."""
        sep, val, tail, n, r = gesichert
        tok = [(SEPS[a], int(v)) for a, v in zip(sep.tolist(), val.tolist())]
        text = f"start={self.start} n={n} r={r} tail={tail}\n{bs.zeile(tok, tail)}\n"
        name = f"kandidat_{self.start}_{n}.txt.gz"
        with gzip.open(name, "wt") as f:
            f.write(text)
        print(f"KANDIDAT ({grund}) Start {self.start} bei n={n} r={r}: Schnappschuss in {name}", flush=True)
        print("KANDIDAT-SCHNAPPSCHUSS-BASE64 " + base64.b64encode(gzip.compress(text.encode())).decode(), flush=True)
        if not stop:
            self.kc_auftreten.append(n)
            self.verfolgen = VERFOLGEN
            return
        self.halt = f"Kandidat bei n={n} ({grund})"
        raise Stop()

    def rueckfall(self, art):
        b = self.b
        tail = b.tail
        vorher = self.sichern()
        kc_vorher = self.kc
        if self.modus == "pruef":
            X = b.tok()
        kurz, schnitte = b.kurz()
        try:
            erg = (uebergang(kurz, schnitte, tail, b, self) if self.r == 0 else None) \
                or lokal(kurz, schnitte, tail, self.r, b, self)
            if erg is None:      # Einsetzen nicht eindeutig: ganze Liste rechnen
                self.lokal_ganz += 1
                Xg = b.tok()
                t2, tl2, r2, dn, kc = rechne(Xg, tail, self.r, self)
                self.kc += kc
                b.tail = tl2
                b.setze_liste(t2)
            else:
                Y, d, tl2, r2, dn = erg
                b.tail = tl2
                b.einsetzen(Y, d, schnitte, len(kurz))
        except bs.Halt as h:
            self.kandidat(f"Halt im Rueckfall, {h.args[0]} Schritte nach dem Schnappschuss", vorher)
        if self.kc > kc_vorher:
            self.kandidat("K(C) im Rueckfall", vorher, stop=False)
        if self.modus == "pruef":
            zb.Z = {"ueb": Zaehler(), "vs": Zaehler(), "na": Zaehler()}
            ganz = bs.rueckfall(X, tail, self.r)
            if (ganz[0], ganz[1], ganz[2], ganz[3]) != (b.tok(), b.tail, r2, dn):
                self.vergleich_fehler += 1
                print(f"ABWEICHUNG lokal/ganz bei n={self.n} art={art} dn {dn} / {ganz[3]}", flush=True)
        self.n += dn
        self.r = r2
        self.grenze_neu()

    def stichprobe(self):
        """Eine Automatenphase ganz mit dem Durchlaufmodell rechnen und mit der Regel vergleichen."""
        vorher = self.sichern()
        X = self.b.tok()
        tail = self.b.tail
        kc0 = self.kc
        try:
            Y, tl2, r2, dn, kc = rechne(X, tail, self.r, self)
        except bs.Halt as h:
            self.kandidat(f"Halt in Stichprobe, {h.args[0]} Schritte nach dem Schnappschuss", vorher)
        self.kc = kc0 + kc
        self.stich["gerechnet"] += 1
        if kc:
            self.kandidat("K(C) in Stichprobe", vorher, stop=False)
        g, kosten = self.schritt()        # r == ziel_r: Einzelschritt, kein Paar-Buendel
        self.ziel_r = None
        if kosten is None:
            # Regel greift nicht: dann ist es ohnehin ein Rueckfall; Ergebnis der ganzen Rechnung nehmen
            self.stich["rueckfall"] += 1
            self.b.tail = tl2
            self.b.setze_liste(Y)
            self.n += dn
            self.r = r2
            self.grenze_neu()
            self.z("rf:" + g)
            self.phasen += 1
            return
        if FEHLER == "stich":
            kosten += 1
        if g == "PAAR" or (self.b.tok(), self.b.tail, self.r - 1, kosten) != (Y, tl2, r2, dn):
            self.kandidat(f"Stichprobe weicht von Regel {g} ab", vorher)
        self.stich["gleich"] += 1
        self.stich["regel:" + g] = self.stich.get("regel:" + g, 0) + 1
        self.n += kosten
        self.r -= 1
        self.z(g)
        self.phasen += 1

    def voll_phase(self):
        """Nach K(C): eine Phase ganz mit dem Durchlaufmodell (keine Regel, kein Kuerzen); Halt -> Kandidat."""
        self.verfolgen -= 1
        vorher = self.sichern()
        try:
            Y, tl2, r2, dn, kc = rechne(self.b.tok(), self.b.tail, self.r, self)
        except bs.Halt as h:
            self.kandidat(f"Halt nach K(C), {h.args[0]} Schritte nach dem Schnappschuss", vorher)
        self.kc += kc
        if kc:
            self.kandidat("K(C) erneut", vorher, stop=False)
        if self.r == 0:
            self.zyklen += 1
        self.b.tail = tl2
        self.b.setze_liste(Y)
        self.n += dn
        self.r = r2
        self.grenze_neu()
        self.z("verfolgt")
        self.phasen += 1

    def lauf(self, N):
        naechste = 10
        try:
            self._lauf(N)
        except Stop:
            pass
        self.bericht("ende")
        if self.out:
            self.out.close()

    def _lauf(self, N):
        naechste = 10
        while self.n < N and self.halt is None:
            if self.verfolgen:
                self.voll_phase()
            elif self.r == 0:
                self.zyklen += 1
                if self.out:
                    self.out.write(f"{self.n} 0 {bs.crc(self.b.tok(), self.b.tail)}\n")
                self.rueckfall("ueb")
                self.z("ueb")
                self.phasen += 1
                self.ziel_r = None
                if self.n >= self.stich_ziel_n and self.r >= 1:
                    self.ziel_r = self.rng.randint(1, self.r)
                    while self.stich_ziel_n <= self.n:
                        self.stich_ziel_n *= 10 ** (1 / STICH_JE)
            elif self.r == self.ziel_r:
                self.stichprobe()
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

    def bericht(self, k):
        print(f"{k}: t={time.time() - T0:.0f}s n={self.n} phasen={self.phasen} zyklen={self.zyklen} token={self.b.hi - self.b.lo} "
              f"K(C)={self.kc} halt={self.halt} lokal_ganz={self.lokal_ganz} abweichungen={self.vergleich_fehler} "
              f"stichproben={self.stich} K(C)-Auftreten bei n={self.kc_auftreten} "
              f"{dict(sorted(self.zaehl.items()))}", flush=True)


# ---------------------------------------------------------------- lokale Rueckfall-Rechnung
WBITS = {("100", False): (1, 0, 0), ("011", True): (1, 1, 0), ("100", True): (0, 0, 1), ("011", False): (0, 1, 1)}


def oben(st, links, k):
    """Die k Zellen am Kopf (naechste zuerst), wie sweepmodell.peek, nur schneller."""
    out = []
    i = len(st) - 1
    while i >= 0 and len(out) < k:
        t = st[i]
        if t[0] == "b":
            out.append(t[1])
        else:
            w = WBITS[(t[1], links)]
            reps = t[2]
            while reps and len(out) < k:
                out.extend(w)
                reps -= 1
        i -= 1
    while len(out) < k:
        out.append(0)
    return out[:k]


# ---- C-Fassung von rechne (rechne.c, gleiche Rechnung; ZB_PY=1 erzwingt Python). Abgleich: test_rechne_c.py
def _lade_c():
    if os.environ.get("ZB_PY"):
        return None
    import ctypes
    import subprocess
    quelle = os.path.join(HIER, "rechne.c")
    so = os.path.join(HIER, "rechne.so")
    if not os.path.exists(so) or os.path.getmtime(so) < os.path.getmtime(quelle):
        subprocess.run(["cc", "-O2", "-shared", "-fPIC", "-o", so, quelle], check=True)
    lib = ctypes.CDLL(so)
    P = ctypes.c_void_p
    i64 = ctypes.c_int64
    lib.rechne.restype = ctypes.c_int
    lib.rechne.argtypes = [i64, P, P, i64, P, i64, P, P, i64, P, P, i64, P, P, P, P, i64]
    return lib


C_LIB = _lade_c()
SEP_NR = {"0": 0, "1": 1, "": 2}


class Endlos(Exception):
    pass


def rechne_c(X, tail, r, grenze=0):
    """Wie rechne_py, in C. Rueckgabe (Y, tail, r', dn, kc); Halt -> bs.Halt(Schritte)."""
    import ctypes
    sep = np.array([SEP_NR[t] for t, _ in X], dtype=np.int8)
    val = np.array([v for _, v in X], dtype=np.int64)
    tl = np.array([int(c) for c in tail], dtype=np.int8)
    cap = 2 * len(X) + 2 * len(tail) + 64
    while True:
        so = np.zeros(cap, dtype=np.int8)
        vo = np.zeros(cap, dtype=np.int64)
        to = np.zeros(cap, dtype=np.int8)
        aus = np.zeros(5, dtype=np.int64)    # ntok, ntail, r, n, kc
        z = lambda a: a.ctypes.data_as(ctypes.c_void_p)   # noqa: E731
        a = aus.ctypes.data
        ret = C_LIB.rechne(len(X), z(sep), z(val), len(tl), z(tl), int(r), z(so), z(vo), cap, a,
                           z(to), cap, a + 8, a + 16, a + 24, a + 32, int(grenze))
        if ret == 1:
            raise bs.Halt(int(aus[3]))
        if ret == 0:
            break
        if ret == 2:
            raise Endlos(grenze)
        if ret == -3:
            raise RuntimeError("rechne.c: Schrittzahl einer Phase ueber 2^61")
        cap *= 4
        if cap > 10**9:
            raise RuntimeError("rechne.c: kein Platz")
    nt, ntl = int(aus[0]), int(aus[1])
    Y = [(SEPS[x], v) for x, v in zip(so[:nt].tolist(), vo[:nt].tolist())]
    return Y, "".join(map(str, to[:ntl].tolist())), int(aus[2]), int(aus[3]), int(aus[4])


def rechne(X, tail, r, lauf):
    """Durchlaufmodell einer Phase (C-Fassung, sonst Python); zaehlt K(C)."""
    if C_LIB is None:
        tk, tl, rr, n, kc = rechne_py(X, tail, r)
    else:
        tk, tl, rr, n, kc = rechne_c(X, tail, r)
    if FEHLER == "kc" and lauf is not None and lauf.n > 10**9 and not lauf.kc_auftreten:
        kc += 1      # Negativkontrolle: einmal ein K(C) vortaeuschen
    return tk, tl, rr, n, kc


def rechne_py(X, tail, r, grenze=0):
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
    makro = 0
    while True:
        makro += 1
        if grenze and makro > grenze:
            raise Endlos(makro)
        if not erster and q == C_:
            rr = None
            if seite == "R" and oben(R, False, 2) == [0, 0]:
                rr = bs.rechts_muster(R, "z1")
            elif seite == "L" and oben(L, True, 1) == [0]:
                rr = bs.rechts_muster(R, "z2")
            if rr is not None:
                tk, tl = bs.canon(bs.bits_aus_l(L) if seite == "R" else bs.bits_aus_l(L)[:-1])
                return tk, tl, rr, n, kc
        erster = False
        if seite == "R" and q == C_ and R and R[-1][0] == "w" and R[-1][1] == "100":
            m = R.pop()[2]
            # letzter Eintritt des Durchlaufs: C auf die Zelle hinter dem Block (im Inneren immer 1 0 0)
            if oben(R, False, 3) == [0, 1, 1]:
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
            if nq == C_ and oben(R, False, 3) == [0, 1, 1]:
                kc += 1
        else:
            sm.push_zelle(R, w, False)
            seite = "L"
        q = nq


def lage(kurz, Y, schnitte):
    """Gemeinsame Verschiebung d aller Schnitte in Y: der Block aus je K Token links und rechts jedes
    Schnitts muss in Y an Position (Schnitt - K + d) stehen, fuer genau ein d. Sonst None."""
    kand = None
    for sp, _, _ in schnitte:
        block = kurz[sp - K:sp + K]
        lagen = set()
        for d in range(-40, 41):
            a = sp - K + d
            if 0 <= a and a + 2 * K <= len(Y) and Y[a:a + 2 * K] == block:
                lagen.add(d)
        kand = lagen if kand is None else (kand & lagen)
    if kand is None or len(kand) != 1:
        return None
    return kand.pop()


def lokal(kurz, schnitte, tail, r, band, lauf, extra_fest=None):
    """Rechnet die kurze Liste; Rueckgabe (Y, d, tail', r', dn) mit geeichten Schritten fuer die
    weggelassenen Laeufe, oder None."""
    Y, tl2, r2, dn, kc = rechne(kurz, tail, r, lauf)
    lauf.kc += kc
    if not schnitte:
        return Y, 0, tl2, r2, dn
    d = lage(kurz, Y, schnitte)
    if d is None:
        return None
    if extra_fest is not None:
        return Y, d, tl2, r2, dn + extra_fest
    extra = 0
    for si, (sp, a, e) in enumerate(schnitte):
        dd = []
        for wert in (1, 3):
            kurz2 = kurz[:sp] + [("1", wert)] + kurz[sp:]
            sch2 = [(p + (1 if j > si else 0), x, y) for j, (p, x, y) in enumerate(schnitte)]
            sch2[si] = (sp + 1, a, e)   # Block um den Schnitt enthaelt jetzt das eingefuegte Token
            Y2, tl22, r22, dn2, _ = rechne(kurz2, tail, r, lauf)
            if r22 != r2 or tl22 != tl2 or lage(kurz2, Y2, sch2) != d:
                return None
            dd.append(dn2 - dn)
        alpha = (dd[1] - dd[0]) // 2
        beta = dd[0] - alpha
        if alpha * 2 != dd[1] - dd[0]:
            return None
        if FEHLER == "lokal":
            beta += 1
        extra += alpha * band.summe(a, e) + beta * (e - a)
    return Y, d, tl2, r2, dn + extra


BMIN = 16


def uebergang(kurz, schnitte, tail, band, lauf):
    """Zyklusuebergang (r = 0): die Fressphase dauert b Runden (b = n des vorletzten Tokens). Statt sie
    ganz zu rechnen: lokal fuer b' = b0, b0+2, b0+4, b0+6 (b0 = 4 oder 5, gleiche Paritaet wie b).
    Verlangt: gleiches Ergebnis (Liste, Verschiebung) fuer alle b', r' linear und dn quadratisch in b'
    (vierter Wert als Probe). Dann r' und dn fuer das echte b durch Fortsetzen. Sonst None."""
    if tail != "" or len(kurz) < RR:
        return None
    sb, b = kurz[-2]
    if b < BMIN:
        return None
    b0 = 4 + (b % 2)
    werte = []
    extra = None
    for i in range(4):
        k2 = kurz[:-2] + [(sb, b0 + 2 * i), kurz[-1]]
        # Eichung der weggelassenen Laeufe nur bei i = 0 und i = 3 (muss gleich sein), sonst uebernommen
        w = lokal(k2, schnitte, tail, 0, band, lauf, None if i in (0, 3) else extra)
        if w is None:
            return None
        if i == 0:
            w0 = lokal(k2, schnitte, tail, 0, band, lauf, 0)
            extra = w[4] - w0[4]
        if i == 3:
            w3 = lokal(k2, schnitte, tail, 0, band, lauf, 0)
            if w[4] - w3[4] != extra:
                lauf.z("ueb:eichung_lauf")
                return None
        werte.append(w)
    Y, d, tl = werte[0][0], werte[0][1], werte[0][2]
    if any(w[0] != Y or w[1] != d or w[2] != tl for w in werte):
        lauf.z("ueb:eichung_liste")
        return None
    rr = [w[3] for w in werte]
    dd = [w[4] for w in werte]
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
    return Y, d, tl, r_echt, dn_echt


if __name__ == "__main__":
    st = ord(sys.argv[1]) - 65
    N = int(float(sys.argv[2]))
    modus = sys.argv[3]
    lauf = Lauf(st, modus, sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "-" else None,
                int(float(sys.argv[5])) if len(sys.argv) > 5 else None)
    lauf.lauf(N)
