"""Abgleich der ausfuehrbaren Fassung des Wortsystems (WX.runden in rocq/rueckfuehrung_396.v) mit Python.

Aufruf:
  python3 -I abgleich.py erzeuge > abgleich_rocq.v     (Rocq-Datei mit den Startwoertern schreiben;
      sie laedt die Beweisdatei als BusyCoq.R396: rocq/rueckfuehrung_396.v als verify/R396.v bauen)
  python3 -I abgleich.py vergleich <coq-ausgabe> [<runde-c-ausgabe>]
      (Ausgabe von coqc abgleich_rocq.v pruefen; optional zusaetzlich die Woerter ab s0 = 1 gegen
       die R-Zeilen von "../runde 396 35 35", ohne Nullen am Ende)
Startwoerter: W.start = 1 (35 Runden) und 40 Zufallswoerter mit 1011 / 111 / 011 (je 15 Runden, Seed fest).
Python rechnet das Wortsystem unabhaengig von Rocq nach den sechs Regeln, auf Listen mit derselben
Darstellung (Zellen hinter dem Ende sind 0, tl [] = []): Woerter werden exakt verglichen.
Kodierung je Runde k: Wort -> Liste der Zellen; Treffer j -> [7, j]; Schrittgrenze -> [9].
Negativkontrolle: ABGLEICH_FEHLER=1 rechnet mit der Regel von 587 (1011 -> 1000) und muss abweichen.
"""
import os
import random
import re
import sys

sys.setrecursionlimit(1000000)
FEHLER = os.environ.get("ABGLEICH_FEHLER") == "1"
K0, K = 35, 15


class Treffer(Exception):
    pass


def z(w):
    return w[0] if w else 0


def V(w):
    a, b, c, d = z(w), z(w[1:]), z(w[2:]), z(w[3:])
    if a == 0:
        return [1] + w[1:]
    if b == 1 and c == 1:
        raise Treffer
    if c == 0:
        return [0, 0, 0] + V(w[3:])
    if d == 0:
        return [1, 0, 1, 0] + V(V(w[4:]))
    return ([1, 0, 0, 0] if FEHLER else [0, 0, 0, 1]) + w[4:]


def spur(s, k):
    out = [list(s)]
    for j in range(k):
        try:
            s = V([1, 0] + s)
        except Treffer:
            out += [[7, j]] * (k - j)
            return out
        out.append(s)
    return out


def starts():
    random.seed(396)
    ws = [[1]]
    while len(ws) < 41:
        L = random.randint(3, 16)
        w = [random.choice([0, 0, 1]) for _ in range(L)]
        t = "".join(map(str, w))
        if "1011" in t or "111" in t or "011" in t:
            ws.append(w)
    return ws


def erzeuge():
    ws = starts()
    b = lambda w: "[" + "; ".join("true" if x else "false" for x in w) + "]"
    print("(** Abgleich: WX.runden aus rocq/rueckfuehrung_396.v auswerten (kein Beweis). Erzeugt von abgleich.py. *)")
    print("From BusyCoq Require Import Individual62.")
    print("From BusyCoq Require Import R396.")
    print("From Coq Require Import Lists.List. Import ListNotations.")
    print("Definition bits (w : list bool) : list nat := map (fun x : bool => if x then S O else O) w.")
    print("Definition kodiere (e : WX.ergebnis) : list nat :=")
    print("  match e with WX.Wort s => bits s | WX.Treffer j => [7; j] | WX.Grenze => [9] end.")
    print("Definition spur (k : nat) (s : list bool) : list (list nat) :=")
    print("  map (fun i => kodiere (WX.runden 5000 i s)) (seq O (S k)).")
    print("Set Printing Width 1000000.")
    print(f"Eval vm_compute in spur {K0} W.start.")
    for w in ws[1:]:
        print(f"Eval vm_compute in spur {K} {b(w)}.")


def lese(pfad):
    txt = open(pfad).read()
    bloecke = re.findall(r"=\s*(\[.*?\])\s*:\s*list \(list nat\)", txt, re.S)
    return [[[int(x) for x in re.findall(r"\d+", inner)] for inner in re.findall(r"\[([^\[\]]*)\]", blk)]
            for blk in bloecke]


def vergleich(pfad):
    rocq = lese(pfad)
    ws = starts()
    py = [spur(ws[0], K0)] + [spur(w, K) for w in ws[1:]]
    if len(rocq) != len(py):
        print(f"ABWEICHUNG: {len(rocq)} Spuren von Rocq, {len(py)} von Python"); return 1
    abw = 0; treffer = 0; runden = 0; grenze = 0
    for i, (a, b) in enumerate(zip(rocq, py)):
        runden += len(a) - 1
        if any(x == [9] for x in a): grenze += 1
        if any(len(x) == 2 and x[0] == 7 for x in b): treffer += 1
        if a != b:
            abw += 1
            if abw <= 3:
                j = next(j for j in range(min(len(a), len(b))) if a[j] != b[j]) if len(a) == len(b) else -1
                print(f"ABWEICHUNG Startwort {i} ({''.join(map(str, ws[i]))}), Runde {j}")
    print(f"abgleich: {len(py)} Startwoerter, {runden} Runden, davon {treffer} Laeufe mit Treffer 111, "
          f"Schrittgrenze erreicht: {grenze}, Abweichungen: {abw}")
    print(f"s0 = 1: {K0} Runden, Wortlaenge zuletzt {len(py[0][-1])}")
    if len(sys.argv) > 3:
        c = [l.split()[2] for l in open(sys.argv[3]) if l.startswith("R ")]
        r0 = ["".join(map(str, w)).rstrip("0") for w in rocq[0][1:]]
        gleich = c == r0
        print(f"runde.c (s0 = 1, {len(c)} Runden) gegen Rocq: {'gleich' if gleich else 'ABWEICHUNG'}")
        if not gleich:
            abw += 1
    return 1 if abw or grenze else 0


if __name__ == "__main__":
    if sys.argv[1] == "erzeuge":
        erzeuge()
    else:
        sys.exit(vergleich(sys.argv[2]))
