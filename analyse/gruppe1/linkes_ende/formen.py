"""Formen am linken Ende: ordnet die Rueckfall-Protokolle (beschleuniger.py lauf, direkt.c) und zaehlt
neue Formen und neue Kerne je Zehnerpotenz Schritte. Zweites Programm: formen2.awk (gleiche Definition,
getrennt geschrieben). Definition (auch im Bericht):

Satz: "n r art | V | N | r'=..." (Kommentar ab " #" entfaellt); V, N Token-Listen "t:n ... /rest".
Fenster: X = Token aus V, Y = Token aus N. Bei Zyklusuebergaengen (art beginnt mit "Ueb") und |X| >= 5,
  |Y| >= 3: X ohne die letzten 4, Y ohne die letzten 2 Token (rechtes Ende: Fressen und J).
  s = Laenge des gemeinsamen Endes (nur wenn beide Reste leer), i = Laenge des gemeinsamen Anfangs
  (i <= min(|X|,|Y|) - s). Fenster a = X[i : |X|-s], b = Y[i : |Y|-s].
Form: "R" (i = 0, Fenster beginnt am linken Bandende) oder "I", dann a -> b; die Zahl des letzten Tokens
  von a heisst p, die des letzten Tokens von b p+c (nur wenn a, b nicht leer und beide Reste leer).
  Schreibweise je Token: Trenner 1 -> nichts, 0 -> ".", kein Trenner -> "_", dann n.
Kern: Z = X ohne das letzte Token (bei Uebergaengen: X ohne die letzten 4, wenn |X| >= 5).
  Grenze = rechtestes unregelmaessiges Token in Z (Trenner nicht 1 oder n gerade). Kern = die
  zusammenhaengende Gruppe unregelmaessiger Token, die an der Grenze endet; Code je Token: Trenner wie
  oben, dann 0 (n = 0), o (ungerade), e (gerade). Davor "R"/"I" wie bei der Form und "frei" (links
  vom Kern nur regulaere Token) oder "alt" (dort steht noch ein unregelmaessiges Token).
Kernmuster: der Kern ohne die Marken R/I und frei/alt.
Aufruf: python3 formen.py <datei_A> [<datei_C> <datei_D> ...]   (Start = Buchstabe hinter dem ersten '_')
Negativkontrollen: FORMEN_FEHLER=kern (Kern ohne R/I und frei/alt) und FORMEN_FEHLER=fenster (gemeinsamer
Anfang wird nicht abgeschnitten) muessen andere Zahlen liefern.
"""
import os
import sys

FEHLER = os.environ.get("FORMEN_FEHLER", "")


def lies(zeile):
    toks, rest = zeile.strip().rsplit("/", 1)
    out = []
    for x in toks.split():
        t, n = x.split(":")
        out.append(("" if t == "_" else t, int(n)))
    return out, rest.strip()


def fmt(t):
    return " ".join({"1": "", "0": ".", "": "_"}[s] + str(n) for s, n in t)


def unreg(tok):
    return tok[0] != "1" or tok[1] % 2 == 0


def fenster(art, X, xt, Y, yt):
    if art.startswith("Ueb") and len(X) >= 5 and len(Y) >= 3:
        X, Y = X[:-4], Y[:-2]
    s = 0
    if xt == "" and yt == "":
        while s < min(len(X), len(Y)) and X[-1 - s] == Y[-1 - s]:
            s += 1
    i = 0
    while FEHLER != "fenster" and i < min(len(X), len(Y)) - s and X[i] == Y[i]:
        i += 1
    return i, X[i:len(X) - s], Y[i:len(Y) - s]


def form(art, X, xt, Y, yt):
    i, a, b = fenster(art, X, xt, Y, yt)
    rand = "R" if i == 0 else "I"
    if a and b and xt == "" and yt == "":
        c = b[-1][1] - a[-1][1]
        A = (fmt(a[:-1]) + " " if len(a) > 1 else "") + {"1": "", "0": ".", "": "_"}[a[-1][0]] + "p"
        B = (fmt(b[:-1]) + " " if len(b) > 1 else "") + {"1": "", "0": ".", "": "_"}[b[-1][0]] + \
            ("p" if c == 0 else "p%+d" % c)
    else:
        A = fmt(a) + ("<" + xt + ">" if xt else "")
        B = fmt(b) + ("<" + yt + ">" if yt else "")
    return f"{rand} {A} -> {B}", i


def kern(art, X, xt, Y, yt):
    i, _, _ = fenster(art, X, xt, Y, yt)
    if art.startswith("Ueb"):
        Z = X[:-4] if len(X) >= 5 else X
    else:
        Z = X[:-1]
    f = None
    for j in range(len(Z) - 1, -1, -1):
        if unreg(Z[j]):
            f = j
            break
    if f is None:
        return "keine Grenze" + ("<" + xt + ">" if xt else "")
    j = f
    while j - 1 >= 0 and unreg(Z[j - 1]):
        j -= 1
    frei = all(not unreg(t) for t in Z[:j])

    def code(t):
        v = "0" if t[1] == 0 else ("o" if t[1] % 2 else "e")
        return {"1": "", "0": ".", "": "_"}[t[0]] + v
    if FEHLER == "kern":   # Negativkontrolle: ohne R/I und frei/alt
        return " ".join(code(t) for t in Z[j:f + 1]) + ("<" + xt + ">" if xt else "")
    return ("R " if i == 0 else "I ") + ("frei " if frei else "alt ") + \
        " ".join(code(t) for t in Z[j:f + 1]) + ("<" + xt + ">" if xt else "")


def saetze(fn):
    for z in open(fn):
        z = z.split(" #")[0].rstrip("\n")
        kopf, V, N, _ = z.split(" | ")
        X, xt = lies(V)
        Y, yt = lies(N)
        n, r, art = kopf.split()
        yield int(n), art, X, xt, Y, yt


def auswerten(dateien, titel):
    ev = []
    for fn in dateien:
        for n, art, X, xt, Y, yt in saetze(fn):
            k = kern(art, X, xt, Y, yt)
            muster = " ".join(k.split()[2:]) if k[:2] in ("R ", "I ") else k
            ev.append((n, form(art, X, xt, Y, yt)[0], k, muster))
    ev.sort(key=lambda e: e[0])
    gf, gk, gm, dek = {}, {}, {}, {}
    for n, f, k, mu in ev:
        d = len(str(n)) - 1
        D = dek.setdefault(d, [0, 0, 0, 0])
        D[0] += 1
        if f not in gf:
            gf[f] = n
            D[1] += 1
        if k not in gk:
            gk[k] = n
            D[2] += 1
        if mu not in gm:
            gm[mu] = n
            D[3] += 1
    print(f"== {titel}: Faelle {len(ev)}, Formen {len(gf)}, Kerne {len(gk)}, Kernmuster {len(gm)}")
    for d in sorted(dek):
        print("  10^%d..10^%d  Faelle %5d  neue Formen %3d  neue Kerne %2d  neue Kernmuster %2d" % (d, d + 1, *dek[d]))
    return gf, gk


if __name__ == "__main__":
    dateien = sys.argv[1:]
    for fn in dateien:
        auswerten([fn], os.path.basename(fn))
    if len(dateien) > 1:
        gf, gk = auswerten(dateien, "alle Starts zusammen")
        print("Kerne (erstes Auftreten):")
        for k, n in sorted(gk.items(), key=lambda kv: kv[1]):
            print("  %.2e  %s" % (n, k))
