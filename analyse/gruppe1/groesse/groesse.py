"""Erhaltene Groesse fuer Gruppe 1 (Tabelle 114, Starts A, C, D): Programm 1 (Python).

Faehrt den Phasen-Beschleuniger aus ../linkes_ende/beschleuniger.py (Band, rueckfall, anlauf,
zyklus_uebergang; unveraendert importiert) und misst je Ereignis die Aenderung von Kandidaten-Groessen.

Kandidaten an einem Schnappschuss (Token-Liste T links vom Kopf, Rest tail, Zaehler r):
  S  Summe der n aller Token            m  Zahl der Token
  z  Token mit Trenner 0                u  Token mit ungeradem n
  q  unregelmaessige Token (Trenner nicht 1 oder n gerade)
  r  Zaehler rechts vom Kopf (0 (100)^r 1)
  x  n des rechtesten Tokens            y  n des Tokens links daneben
  L  Bandlaenge = Summe der Trennerbits + 3S + |tail| + 3r + 3 (Zellen vom linken bis zum rechten Ende)

Ereignisklassen (je Phase genau eine, Zyklusuebergaenge zusaetzlich zerlegt):
  N1 N2 N2s UA LE0 LE1 LG        Automatenregeln (Phase ohne Simulation, Aenderung aus dem Fenster
                                 um die Grenze gerechnet, laufend aufsummiert)
  VS                             VS-Regel aus PR 9 (Rueckfall, Ergebnis = Vorhersage)
  Kern:<Kernmuster>              Phasen, die der Automat nicht erklaert (Kernmuster wie formen.py, ohne
                                 die Marken R/I und frei/alt)
  KernUeb:<Kernmuster>           Zyklusuebergaenge, die die Zyklusfunktion nicht erklaert
  Ueb gesamt                     jeder erklaerte Zyklusuebergang (Schnappschuss r=0 bis naechster)
  UebRueck:<Regel> UebFress:<Regel> Fressen J
                                 Teile eines erklaerten Uebergangs nach der Zyklusfunktion (PR 9);
                                 die Zwischenstaende sind keine Schnappschuesse, dort gilt r = 0 formal.

Ausgabe:
  <praefix>_delta.txt   je Klasse und je verschiedenem Aenderungsvektor eine Zeile
                        "Klasse | dS dm dz du dq dr dx dy dL | Anzahl"  (sortiert; Vergleich mit Programm 2)
  <praefix>_proto.txt   jedes Ereignis, das nicht Automatenregel ist (VS, Kern, Uebergang), mit Liste
                        vorher und nachher, r, r', dn (Eingabe fuer Programm 2, das die Automatenphasen
                        selbst rechnet)
Aufruf: python3 groesse.py <A|C|D> <Schritte> <praefix>
Negativkontrolle: GROESSE_FEHLER=n2 (bei N2 wird das Fenster um ein Token zu klein genommen, der linke
  Nachbar fehlt) und GROESSE_FEHLER=lg (bei LG zaehlt das neue Token nicht fuer u); der Vergleich mit
  Programm 2 muss dann scheitern.
"""
import os
import sys
from collections import Counter

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HIER, "..", "linkes_ende"))
import beschleuniger as bs  # noqa: E402
from formen import kern as formen_kern  # noqa: E402
from automat import rand2  # noqa: E402  (ueber beschleuniger im Pfad)

FEHLER = os.environ.get("GROESSE_FEHLER", "")
NAMEN = ["S", "m", "z", "u", "q", "r", "x", "y", "L"]


def irr(t, n):
    return t != "1" or n % 2 == 0


def teil(tok):
    """(S, m, z, u, q, sep) fuer eine Liste von Token; sep = Zahl der Trennerbits."""
    S = m = z = u = q = sep = 0
    for t, n in tok:
        S += n
        m += 1
        z += t == "0"
        u += n % 2
        q += irr(t, n)
        sep += t != ""
    return [S, m, z, u, q, sep]


def voll(tok, tail, r):
    """Alle Kandidaten einer Konfiguration (tok links nach rechts)."""
    S, m, z, u, q, sep = teil(tok)
    x = tok[-1][1] if len(tok) >= 1 else 0
    y = tok[-2][1] if len(tok) >= 2 else 0
    L = sep + 3 * S + len(tail) + 3 * r + 3
    return (S, m, z, u, q, r, x, y, L)


def diff(a, b):
    return tuple(bb - aa for aa, bb in zip(a, b))


def zeile(tok, tail):
    return bs.zeile(tok, tail)


def muster(art, X, xt, Y, yt):
    k = formen_kern(art, X, xt, Y, yt)
    return " ".join(k.split()[2:]) if k[:2] in ("R ", "I ") else k


def lauf(start, N, praefix):
    n, tok, tail, r = bs.anlauf(start, N)
    band = bs.Band(tok, tail)
    # laufende Summen (fuer die Automatenphasen inkrementell)
    S, m, z, u, q, sep = teil(tok)
    zaehl = {}            # Klasse -> Counter(Vektor)
    proto = open(praefix + "_proto.txt", "w")
    proto.write(f"START {n} {r} | {zeile(tok, tail)}\n")
    kontrollen = 0

    def buche(kl, v):
        zaehl.setdefault(kl, Counter())[v] += 1

    while n < N:
        T = band.T
        if r >= 1 and band.tail == "":
            L0 = len(T)
            j = band.j
            a = max(0, j - 1)
            if FEHLER == "n2":
                a = max(0, j)       # Negativkontrolle: linker Nachbar der Grenze fehlt im Fenster
            b = min(L0, j + 3)
            vorher = T[a:b]
            x0 = T[0][1] if L0 >= 1 else 0
            y0 = T[1][1] if L0 >= 2 else 0
            grund, kosten = band.schritt()
            if kosten is not None:
                T = band.T
                L1 = len(T)
                nachher = T[a:b + (L1 - L0)]
                tv = teil(vorher)
                tn = teil(nachher)
                if FEHLER == "lg" and grund == "LG":
                    tn[3] -= 1
                d = [tn[i] - tv[i] for i in range(6)]
                x1 = T[0][1] if L1 >= 1 else 0
                y1 = T[1][1] if L1 >= 2 else 0
                dL = d[5] + 3 * d[0] - 3
                v = (d[0], d[1], d[2], d[3], d[4], -1, x1 - x0, y1 - y0, dL)
                buche(grund, v)
                S += d[0]; m += d[1]; z += d[2]; u += d[3]; q += d[4]; sep += d[5]
                n += kosten
                r -= 1
                continue
            # Rueckfall (VS oder nicht anwendbar)
            vor, vortail = band.tok(), band.tail
            t2, tl2, r2, dn, ln = bs.rueckfall(vor, vortail, r)
            if grund == "VS":
                u_, why = bs.auto_step(list(vor))
                art = "VS" if (u_ == t2 and r2 == r - 1 and tl2 == "") else "na:VS-falsch"
            else:
                art = "na:" + grund
        elif r >= 1:
            vor, vortail = band.tok(), band.tail
            t2, tl2, r2, dn, ln = bs.rueckfall(vor, vortail, r)
            art = "na:rest"
        else:
            vor, vortail = band.tok(), band.tail
            t2, tl2, r2, dn, ln = bs.rueckfall(vor, vortail, r)
            erg = bs.zyklus_uebergang(vor) if vortail == "" else (None, "rest")
            ok = erg[0] is not None and erg[0] == t2 and tl2 == ""
            art = "Ueb-ok" if ok else ("Ueb-falsch" if erg[0] is not None else "Ueb-na:" + str(erg[1]))
        # volle Rechnung fuer das Ereignis
        fv = voll(vor, vortail, r)
        # Kontrolle der laufenden Summen gegen die volle Rechnung
        laufend = (S, m, z, u, q)
        if laufend != fv[:5] or sep + 3 * S + len(vortail) + 3 * r + 3 != fv[8]:
            print(f"SUMMENFEHLER bei n={n}: laufend {laufend} voll {fv[:5]}", flush=True)
            kontrollen += 1
            S, m, z, u, q, sep = teil(vor)
        fn = voll(t2, tl2, r2)
        dv = diff(fv, fn)
        if art == "VS":
            buche("VS", dv)
        elif art == "Ueb-ok":
            buche("Ueb gesamt", dv)
            # Teile nach der Zyklusfunktion
            T1, w1 = rand2(list(vor), 1)
            T2, w2 = rand2(T1, 2)
            (s3, e3), (s2, bb), (s1, aa) = T2[-3:]
            x_ = aa + 4 * bb + 3
            T3 = T2[:-3] + [(s3, e3 - 1), ("0", 0), ("1", x_)]
            (s4, e4), (s3_, e3_) = T3[-4:-2]
            T4 = T3[:-4] + [(s4, e4 - 1), ("1", e3_ + 2)]
            assert T4 == t2
            f1, f2, f3 = voll(T1, "", 0), voll(T2, "", 0), voll(T3, "", 0)
            buche("UebRueck:" + w1, diff(fv, f1))
            buche("UebFress:" + w2, diff(f1, f2))
            buche("Fressen", diff(f2, f3))
            buche("J", diff(f3, fn))
        elif art.startswith("Ueb"):
            buche("KernUeb:" + muster(art, vor, vortail, t2, tl2), dv)
        else:
            buche("Kern:" + muster(art, vor, vortail, t2, tl2), dv)
        proto.write(f"{n} {r} {art} {dn} {r2} | {zeile(vor, vortail)} | {zeile(t2, tl2)}\n")
        n += dn
        r = r2
        band = bs.Band(t2, tl2)
        S, m, z, u, q, sep = teil(t2)
    proto.write(f"ENDE {n}\n")
    proto.close()
    with open(praefix + "_delta.txt", "w") as f:
        for kl in sorted(zaehl):
            for v, c in sorted(zaehl[kl].items()):
                f.write(f"{kl} | {' '.join(map(str, v))} | {c}\n")
    print(f"start={'ABCDEF'[start]} schritte={n} summenfehler={kontrollen} klassen={len(zaehl)}")


if __name__ == "__main__":
    lauf(ord(sys.argv[1]) - 65, int(float(sys.argv[2])), sys.argv[3])
