"""Kuenstliche Phasen: baut eine Token-Liste (linkes Ende links, dann Kern, dann (1,p) und ein fester
regulaerer Rest), laesst genau eine Phase im Durchlaufmodell laufen (beschleuniger.rueckfall) und zeigt
das veraenderte Fenster. Aufruf: python3 synth.py "1 1 1 0 2 5" ".0 .7 5" ...
Schreibweise: Zahl = (1,n), .Zahl = (0,n)."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import beschleuniger as bz  # noqa: E402

CTX = [("1", 7), ("1", 9), ("1", 9), ("1", 4)]


def tok(s):
    return [("0", int(x[1:])) if x.startswith(".") else ("1", int(x)) for x in s.split()]


def fmt(t):
    return " ".join(("" if s == "1" else "." if s == "0" else "_") + str(n) for s, n in t)


def phase(left, r=5):
    """Eine Phase ab der Liste left + CTX; Rueckgabe (Y, rest, r')."""
    Y, yt, r2, dn, ln = bz.rueckfall(left + CTX, "", r)
    return Y, yt, r2


def run(left, r=5):
    X = left + CTX
    try:
        Y, yt, r2 = phase(left, r)
    except bz.Halt:
        return "HALT"
    s = 0
    if yt == "":
        while s < min(len(X), len(Y)) and X[-1 - s] == Y[-1 - s]:
            s += 1
    return f"{fmt(X[:len(X) - s])} -> {fmt(Y[:len(Y) - s])} {'<' + yt + '>' if yt else ''} r'={r2}"


if __name__ == "__main__":
    for S in sys.argv[1:]:
        print(S, "|", run(tok(S)))
