"""Stichprobe zum Satz "Halt => vorher Muster K(C)" (Bericht, Abschnitt 1), unabhaengig von den Zaehlern.

Zufaellige Startbaender: Kopf bei 0, Zellen links (-W..-1) zufaellig, Zellen >= 0 leer, Startzustand zufaellig.
(Der Satz braucht nur, dass rechts vom Startkopf leeres Band liegt; so entstehen viele Halte.)
Fuer jeden Lauf, der haelt (A liest 1 bei h), x = h - 2, wird geprueft:
  K  : vorher ein Schritt nach rechts auf x, Zustand C, Zellen x, x+1, x+2 = 0 1 1
  K2 : vorher ein Schritt nach rechts auf x+1, Zustand C, Zellen x+1, x+2 = 0 1, und der folgende Schritt
       uebernaechste Schritt ist D liest 1 (bei x)
Negativkontrollen (muessen bei manchen Halten FEHLEN): N1 = wie K, aber Zustand D; N2 = wie K, aber auf x+1.
Aufruf: python3 -I lemma_test.py <laeufe> <seed> [rechts]
Mit "rechts" sind auch die Zellen 0..W-1 zufaellig (Voraussetzung des Satzes verletzt). Dann muss es Halte
OHNE K geben (Gegenprobe: zeigt, dass die Voraussetzung noetig ist; vgl. Justus' Beispiel C> 1 1 0 0 1 1 1).
"""
import random
import sys

TM = "1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC"
T = {}
for qi, part in enumerate(TM.split("_")):
    for r in range(2):
        x = part[3 * r:3 * r + 3]
        if x != "---":
            T[(qi, r)] = (int(x[0]), 1 if x[1] == "R" else -1, ord(x[2]) - 65)


def lauf(rng, W=24, maxn=4000, rechts=False):
    band = {i: rng.randint(0, 1) for i in range(-W, W if rechts else 0)}
    q = rng.randrange(6)
    p = 0
    ereig = []   # (Zustand, Position, Zellen p..p+2) bei jedem Schritt nach rechts; und D1-Marken
    for n in range(maxn):
        s = band.get(p, 0)
        if (q, s) not in T:
            return p, ereig
        w, d, nq = T[(q, s)]
        if q == 3 and s == 1:
            ereig.append(("D1", p, None, n))
        band[p] = w
        p += d
        q = nq
        if d == 1:
            ereig.append(("R", p, (q, band.get(p, 0), band.get(p + 1, 0), band.get(p + 2, 0)), n))
    return None, ereig


def main():
    laeufe, seed = int(sys.argv[1]), int(sys.argv[2])
    rechts = len(sys.argv) > 3 and sys.argv[3] == "rechts"
    rng = random.Random(seed)
    halte = 0
    ok = {"K": 0, "K2": 0, "N1": 0, "N2": 0}
    for _ in range(laeufe):
        h, ev = lauf(rng, rechts=rechts)
        if h is None:
            continue
        halte += 1
        x = h - 2
        rs = [e for e in ev if e[0] == "R"]
        if any(e[1] == x and e[2] == (2, 0, 1, 1) for e in rs):
            ok["K"] += 1
        if any(e[1] == x and e[2] == (3, 0, 1, 1) for e in rs):
            ok["N1"] += 1
        if any(e[1] == x + 1 and e[2] == (2, 0, 1, 1) for e in rs):
            ok["N2"] += 1
        # K2: Rechtsschritt auf x+1 in C mit (0,1,?) und direkt danach D liest 1 bei x
        d1 = {(e[1], e[3]) for e in ev if e[0] == "D1"}
        if any(e[1] == x + 1 and e[2][:3] == (2, 0, 1) and (x, e[3] + 2) in d1 for e in rs):
            ok["K2"] += 1
    print(f"laeufe={laeufe} halte={halte} K={ok['K']} K2={ok['K2']} "
          f"Negativkontrollen N1={ok['N1']} N2={ok['N2']} (muessen < halte sein)")
    if rechts:
        print(f"Gegenprobe: Halte ohne K: {halte - ok['K']} (muss > 0 sein)")
        sys.exit(0 if ok["K"] < halte else 1)
    sys.exit(0 if ok["K"] == ok["K2"] == halte and ok["N1"] < halte and ok["N2"] < halte else 1)


main()
