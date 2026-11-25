"""Beschleuniger auf Phasenebene fuer Tabelle 114 (Gruppe 1: Starts A, C, D).

Zustand an einem Phasen-Schnappschuss: Kopf in Zustand C auf einer 0, rechts davon 0 (100)^r 1 bis
zum rechten Bandende (wie snap.py / zyklus2.c). Links vom Kopf: Token-Liste (t, n) wie canon.py
(Trennerbit t, dann n-mal 011; t = '' nur ganz links) plus ein Rest ("tail", normalerweise leer).

Je Phase (Schnappschuss r -> naechster Schnappschuss):
  * r >= 1 und eine Automatenregel N1, N2, N2s, UA, LE (f=0 / f=1) oder LG greift:
      Token-Liste nach der Regel aus PR 9 (automat.py), Schritte nach der Kostenformel
      12*S - 2*m + 12*k + c(Regel)  (S = Summe der n rechts der Grenze, m = Zahl dieser Token,
      k = n der Grenze; c: N1 11, N2 21, N2s 15, UA 15, LE0 25, LE1 17, LG 11).
      In dieser Phase wird nichts simuliert, also auch Halt NICHT geprueft.
  * sonst (VS, "nicht anwendbar", r = 0 = Zyklusuebergang): Rueckfall auf das Durchlaufmodell
      (sweepmodell.py, Regeln S1/S2/E) nur bis zum naechsten Schnappschuss. Dort wird jeder TM-Schritt
      abgebildet, Halt wird geprueft.
Jeder Rueckfall wird mit Vorher/Nachher protokolliert (Formen am linken Ende).

Ausgabe-Modi:
  python3 beschleuniger.py <Start A|C|D> <Schritte> pruef <datei> <crc_bis>   je Schnappschuss "n r crc"
          (crc32 der Token-Zeile wie direkt.c; crc nur fuer n < crc_bis oder r = 0, sonst "-")
  python3 beschleuniger.py <Start> <Schritte> lauf <praefix>          lange Laeufe: Protokoll der Rueckfaelle
          (<praefix>_rueckfall.txt), Uebergaenge (<praefix>_uebergang.txt), Zusammenfassung auf stdout
Negativkontrollen (Umgebungsvariable BESCHL_FEHLER): kosten_n1 (N1 mit c = 13 statt 11),
  n2 (N2 schreibt k+4 statt k+2), lg (LG fuegt (1,3) statt (1,1) an). Der Abgleich muss dann scheitern.
"""
import os
import re
import sys
import zlib

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "teil3"))
sys.path.insert(0, os.path.join(HIER, "..", "zyklus"))
import sweepmodell as sm  # noqa: E402  Durchlaufmodell (S1, S2, E), unveraendert
from automat import step as auto_step, rand2  # noqa: E402  nur fuer den Zyklus-Abgleich an Uebergaengen

FEHLER = os.environ.get("BESCHL_FEHLER", "")
CRC_BIS = 0
A, B, C, D, E, F = range(6)
KOSTEN = {"N1": 13 if FEHLER == "kosten_n1" else 11, "N2": 21, "N2s": 15, "UA": 15,
          "LE0": 25, "LE1": 17, "LG": 11}

# ---------------------------------------------------------------- Token <-> Bits
LAUF = re.compile("(?:011)+")


def canon(b):
    """wie canon.py: greedy von links; Rueckgabe Liste [(t, n)] und Rest."""
    out = []
    i = 0
    for mo in LAUF.finditer(b):
        sep = b[i:mo.start()]
        n = (mo.end() - mo.start()) // 3
        if sep == "":
            out.append(("", n))
        else:
            for c in sep[:-1]:
                out.append((c, 0))
            out.append((sep[-1], n))
        i = mo.end()
    return out, b[i:]


def zeile(tok, tail):
    """Text einer Token-Liste (links nach rechts), gleich wie direkt.c: 't:n' durch Leerzeichen, dann '/'+Rest."""
    return " ".join(("_" if t == "" else t) + ":" + str(n) for t, n in tok) + " /" + tail


def crc(tok, tail):
    return zlib.crc32(zeile(tok, tail).encode())


# ---------------------------------------------------------------- Rueckfall: Durchlaufmodell
def rechts_muster(Rs, zustand):
    """Prueft, ob der rechte Stapel (oben = Kopf) die Zellen <Praefix> (100)^r 1 und dann Ende hat.
    zustand 'z1': Praefix 0 0 ; 'B0': kein Praefix. Rueckgabe r oder None."""
    st = zustand
    r = 0
    for idx in range(len(Rs) - 1, -1, -1):
        tok = Rs[idx]
        if tok[0] == "w" and tok[1] == "100" and st == "B0":
            r += tok[2]
            continue
        if tok[0] == "b":
            zellen = (tok[1],)
        else:   # ein Wort: hoechstens eine Kopie pruefen, ausser 100 in B0 (oben schon behandelt)
            zellen = [int(c) for c in tok[1]] * min(tok[2], 2)
        for z in zellen:
            if st == "z1":
                if z != 0: return None
                st = "z2"
            elif st == "z2":
                if z != 0: return None
                st = "B0"
            elif st == "B0":
                if z != 1: return None
                st = "B1"
            elif st == "B1":
                if z != 0: return None
                st = "B2"
            else:  # B2
                if z != 0: return None
                r += 1
                st = "B0"
    return r if st == "B1" else None


def l_aus_token(tok, tail):
    L = []
    for t, n in tok:
        if t != "":
            L.append(("b", int(t)))
        if n:
            L.append(("w", "011", n))
    for c in tail:
        L.append(("b", int(c)))
    return L


def bits_aus_l(L):
    return "".join(str(x[1]) if x[0] == "b" else x[1] * x[2] for x in L)


class Halt(Exception):
    pass


def rueckfall(tok, tail, r):
    """Vom Schnappschuss (tok, tail, r) mit dem Durchlaufmodell bis zum naechsten Schnappschuss.
    Rueckgabe (tok', tail', r', schritte, links_erweitert)."""
    L = l_aus_token(tok, tail)
    R = [("b", 1)]
    if r:
        R.append(("w", "100", r))
    R += [("b", 0), ("b", 0)]
    q, seite = C, "R"
    pos = 0
    links_neu = 0       # wie weit der Kopf links ueber das bisherige linke Ende hinaus kam
    tiefe = 0           # aktuelle Zahl der Zellen links vom Kopf, die nicht im Stapel L liegen
    n = 0
    erster = True
    while True:
        if not erster and q == C:
            # Schnappschuss: Kopf liest 0, rechts 0 (100)^r 1 bis zum rechten Ende. Der Kopf kann auf R
            # (kam von links) oder auf L stehen (kam von rechts, z. B. nach F1 -> 0LC).
            rr = None
            if seite == "R" and sm.peek(R, False, 2) == [0, 0]:
                rr = rechts_muster(R, "z1")
            elif seite == "L" and sm.peek(L, True, 1) == [0]:
                rr = rechts_muster(R, "z2")
            if rr is not None:
                tk, tl = canon(bits_aus_l(L) if seite == "R" else bits_aus_l(L)[:-1])
                return tk, tl, rr, n, links_neu
        erster = False
        if seite == "R" and q == C and R and R[-1][0] == "w" and R[-1][1] == "100":
            m = R.pop()[2]
            sm.push_wort(L, "011", m)
            n += 3 * m
            continue
        # S2 ohne Schnappschuss-Pruefung im Inneren: dort liest C nur am linken Ende eines Blocks eine 0,
        # rechts davon stehen 0 0, das Muster verlangt aber 0 und dann 100 oder die End-1 -> nie erfuellt.
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
            # Kopf betritt eine nie besuchte Zelle links
            links_neu += 1
        s = sm.pop_zelle(st, links)
        if (q, s) not in sm.TAB:
            raise Halt(n)
        w, d, nq = sm.TAB[(q, s)]
        n += 1
        if d == 1:
            sm.push_zelle(L, w, True)
            seite = "R"
        else:
            sm.push_zelle(R, w, False)
            seite = "L"
        q = nq


# ---------------------------------------------------------------- Automat auf umgedrehter Liste
def regulaer(t, n):
    return t == "1" and n % 2 == 1


class Band:
    """Token-Liste umgedreht: T[0] = rechtestes Token (am Kopf). Grenze j = kleinster Index >= 1 mit
    unregelmaessigem Token (j = len(T): keine Grenze). S = Summe n ueber T[0..j-1]."""

    def __init__(self, tok, tail):
        self.T = list(reversed(tok))
        self.tail = tail
        self.neu_grenze()

    def tok(self):
        return list(reversed(self.T))

    def neu_grenze(self):
        T = self.T
        if not T:
            self.j = 0
            self.S = 0
            return
        self.S = T[0][1]
        self.j = 1
        self.weiter(1)

    def weiter(self, j):
        T = self.T
        S = self.S
        while j < len(T) and regulaer(*T[j]):
            S += T[j][1]
            j += 1
        self.j = j
        self.S = S

    def schritt(self):
        """Ein Automatenschritt (Regeln wie automat.step). Rueckgabe (Regel, Schritte) oder (Grund, None)."""
        T = self.T
        if self.tail != "" or len(T) < 2:
            return "rest", None
        L = len(T)
        j = self.j
        if j >= L:   # keine Grenze: LG
            kosten = 12 * self.S - 2 * L + KOSTEN["LG"]
            T.append(("1", 3 if FEHLER == "lg" else 1))
            self.S += T[-1][1]
            self.j = L + 1
            return "LG", kosten
        s, k = T[j]
        kosten0 = 12 * self.S - 2 * j + 12 * k
        if s == "0" and k % 2 == 0:
            T[j] = ("1", k + 1)
            self.S += k + 1
            self.weiter(j + 1)
            return "N1", kosten0 + KOSTEN["N1"]
        if j == L - 1:   # Grenze ganz links (f = 0)
            if T[j] == ("1", 0):
                T.pop()
                s1, k1 = T[j - 1]
                T[j - 1] = ("1", k1 + 2)
                self.neu_grenze()
                return "LE0", kosten0 + KOSTEN["LE0"]
            return "links?", None
        sg, g = T[j + 1]
        if j == L - 2 and T[j + 1] == ("1", 0) and s == "0" and k % 2 == 1:   # f = 1
            T.pop()
            T[j] = ("1", k + 2)
            self.neu_grenze()
            return "LE1", kosten0 + KOSTEN["LE1"]
        if g >= 1 and ((s == "0" and k % 2 == 1) or (s == "1" and k % 2 == 0)):
            T[j + 1] = (sg, g - 1)
            T[j] = ("0", k + (4 if FEHLER == "n2" else 2))
            return ("N2s" if s == "0" else "N2"), kosten0 + KOSTEN["N2s" if s == "0" else "N2"]
        if s == "0" and k % 2 == 1 and T[j + 1] == ("1", 0) and j + 2 < L and T[j + 2][1] >= 1:
            s2, g2 = T[j + 2]
            T[j + 2] = (s2, g2 - 1)
            T[j + 1] = ("0", 0)
            T[j] = ("1", k + 2)
            self.S += k + 2
            self.weiter(j + 1)
            return "UA", kosten0 + KOSTEN["UA"]
        if s == "1" and k % 2 == 0 and k >= 2 and T[j + 1] == ("1", 0):
            m = k // 2 + 3
            if j + 1 + m < L and all(T[i] == ("1", 1) for i in range(j + 2, j + 2 + m)):
                return "VS", None          # VS: Token und Schritte aus dem Durchlaufmodell
            return "VS-zuwenig", None
        return "Sonder", None


# ---------------------------------------------------------------- Hauptschleife
def lauf(start, N, modus, ziel):
    tok, tail, r = [], "", None
    # Anlauf: vom leeren Band mit dem Durchlaufmodell bis zum ersten Schnappschuss
    n, tok, tail, r = anlauf(start, N)
    band = Band(tok, tail)
    zaehl = {}
    out = open(ziel, "w") if modus == "pruef" else None
    rf = open(ziel + "_rueckfall.txt", "w") if modus == "lauf" else None
    ue = open(ziel + "_uebergang.txt", "w") if modus == "lauf" else None
    naechste_dekade = 10
    phasen = 0
    while True:
        if n >= N:
            break
        if out:
            if n < CRC_BIS or r == 0:
                out.write(f"{n} {r} {crc(band.tok(), band.tail)}\n")
            else:
                out.write(f"{n} {r} -\n")
        if r >= 1:
            vor = None
            grund, kosten = band.schritt()
            if kosten is not None:
                n += kosten
                r -= 1
                zaehl[grund] = zaehl.get(grund, 0) + 1
                phasen += 1
                continue
            # Rueckfall nur fuer diese Phase
            vor = band.tok()
            vortail = band.tail
            try:
                t2, tl2, r2, dn, ln = rueckfall(vor, vortail, r)
            except Halt as h:
                print(f"HALT im Durchlaufmodell bei Schritt {n + h.args[0]}")
                return
            if grund == "VS":
                # Vorhersage der VS-Regel aus PR 9 zum Vergleich
                fv = [x for x in vor]
                u, why = auto_step(fv)
                art = "VS" if (u == t2 and r2 == r - 1) else "VS-falsch"
            else:
                art = "na:" + grund
            zaehl[art] = zaehl.get(art, 0) + 1
            if rf and art != "VS":
                rf.write(f"{n} {r} {art} | {zeile(vor, vortail)} | {zeile(t2, tl2)} | r'={r2} # dn={dn} links_neu={ln}\n")
            n += dn
            r = r2
            band = Band(t2, tl2)
            phasen += 1
        else:
            vor = band.tok()
            vortail = band.tail
            try:
                t2, tl2, r2, dn, ln = rueckfall(vor, vortail, r)
            except Halt as h:
                print(f"HALT im Durchlaufmodell bei Schritt {n + h.args[0]}")
                return
            erg = zyklus_uebergang(vor) if vortail == "" else (None, "rest")
            ok = erg[0] is not None and erg[0] == t2 and tl2 == ""
            art = "Ueb-ok" if ok else ("Ueb-falsch" if erg[0] is not None else "Ueb-na:" + str(erg[1]))
            zaehl[art] = zaehl.get(art, 0) + 1
            if ue:
                ue.write(f"{n} {art} {dn} {ln} r'={r2} len={len(t2)} rechts={zeile(t2[-4:], '')}\n")
            if rf and not ok:
                rf.write(f"{n} {r} {art} | {zeile(vor, vortail)} | {zeile(t2, tl2)} | r'={r2} # dn={dn} links_neu={ln}\n")
            n += dn
            r = r2
            band = Band(t2, tl2)
            phasen += 1
        while n >= naechste_dekade:
            if modus == "lauf":
                print(f"10^{len(str(naechste_dekade)) - 1}: n={n} phasen={phasen} token={len(band.T)} {zaehl}",
                      flush=True)
            naechste_dekade *= 10
    if out:
        out.close()
    print(f"start={'ABCDEF'[start]} schritte={n} phasen={phasen} token={len(band.T)} {sorted(zaehl.items())}")


def zyklus_uebergang(tok):
    """Vorhersage der Zyklusfunktion (PR 9) vom Schnappschuss r=0 bis zum ersten Schnappschuss des
    naechsten Laufs: Randschritt Rueckweg, Randschritt Fressen, Fressen, J."""
    T, why = rand2(list(tok), 1)
    if T is None: return None, "rand_rueck:" + why
    T, why = rand2(T, 2)
    if T is None: return None, "rand_fressen:" + why
    if len(T) < 4: return None, "kurz"
    (s3, e3), (s2, b), (s1, a) = T[-3:]
    if s1 != "1" or e3 < 1: return None, "fressen"
    x = a + 4 * b + 3
    Ef = T[:-3] + [(s3, e3 - 1), ("0", 0), ("1", x)]
    (s4, e4), (s3_, e3_) = Ef[-4:-2]
    if e4 < 1: return None, "J"
    return Ef[:-4] + [(s4, e4 - 1), ("1", e3_ + 2)], "ok"


def anlauf(start, N):
    """Direkt (Einzelschritte) vom leeren Band bis zum ersten Schnappschuss; klein (< 100 Schritte)."""
    TAB = sm.TAB
    band = {}
    p = lo = hi = 0
    q = start
    n = 0
    while True:
        s = band.get(p, 0)
        if q == C and s == 0 and band.get(p + 1, 0) == 0 and n > 0:
            j = p + 2
            r = 0
            while j + 2 <= hi and band.get(j, 0) == 1 and band.get(j + 1, 0) == 0 and band.get(j + 2, 0) == 0:
                r += 1
                j += 3
            if j == hi and band.get(j, 0) == 1:
                b = "".join(str(band.get(i, 0)) for i in range(lo, p))
                tk, tl = canon(b)
                return n, tk, tl, r
        w, d, nq = TAB[(q, s)]
        band[p] = w
        p += d
        q = nq
        n += 1
        lo = min(lo, p)
        hi = max(hi, p)


if __name__ == "__main__":
    st = ord(sys.argv[1]) - 65
    N = int(float(sys.argv[2]))
    CRC_BIS = int(float(sys.argv[5])) if len(sys.argv) > 5 else 0
    lauf(st, N, sys.argv[3], sys.argv[4])
