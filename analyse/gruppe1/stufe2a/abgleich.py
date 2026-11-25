"""Abgleich Stufe 2a: Rocq-[next] (aus abgleich_rocq.v) gegen sweepmodell.py, Makroschritt fuer Makroschritt.

Aufruf: python3 -I abgleich.py <coq-ausgabe> [K]
Die Python-Seite benutzt die Bausteine von ../teil3/sweepmodell.py (TAB, pop_zelle, push_zelle,
push_wort) und dieselbe Regelreihenfolge wie dessen lauf() (S1, dann S2, dann E), ohne
Schrittbudget. Kodierung wie in abgleich_rocq.v: [q, seite, len L, L von oben..., R von oben...],
Bit b -> b, Wort-Token mit n Woertern -> n+1 (Rocq: Block (n-1) -> n+1). 99 = Halt.
Negativkontrolle: ABGLEICH_FEHLER=paritaet (S2 ohne Wechsel) muss eine Abweichung melden.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "teil3"))
import sweepmodell as sm  # noqa: E402

FEHLER = os.environ.get("ABGLEICH_FEHLER", "")


def kod(q, seite, L, R):
    t = lambda tok: tok[1] if tok[0] == "b" else tok[2] + 1
    return [q, 0 if seite == "L" else 1, len(L)] + [t(x) for x in reversed(L)] + [t(x) for x in reversed(R)]


def spur(start, K):
    """Liefert (Zustaende, TM-Schritte); TM-Schritte: S1/S2 je 3 pro Wort, E einer."""
    L, R, q, seite = [], [], start, "R"
    out = [kod(q, seite, L, R)]
    n = 0
    for _ in range(K):
        if seite == "R" and q == sm.C and R and R[-1][0] == "w" and R[-1][1] == "100":
            m = R.pop()[2]; sm.push_wort(L, "011", m); n += 3 * m
        elif seite == "L" and q in (sm.B, sm.D) and L and L[-1][0] == "w" and L[-1][1] == "011":
            m = L.pop()[2]; sm.push_wort(R, "100", m); n += 3 * m
            if m % 2 and FEHLER != "paritaet":
                q = sm.D if q == sm.B else sm.B
        else:
            links = seite == "L"
            s = sm.pop_zelle(L if links else R, links)
            if (q, s) not in sm.TAB:
                out.append([99]); return out, n
            w, d, q = sm.TAB[(q, s)]; n += 1
            if d == 1:
                sm.push_zelle(L, w, True); seite = "R"
            else:
                sm.push_zelle(R, w, False); seite = "L"
        out.append(kod(q, seite, L, R))
    return out, n


def lauf_original(start, N):
    """sweepmodell.lauf selbst (Modus zaehlen) fuer N TM-Schritte: Zahl der Makroschritte."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        sm.lauf(N, "zaehlen", start)
    return int(re.search(r"makroschritte=(\d+)", buf.getvalue()).group(1)), buf.getvalue().strip()


def lies_coq(pfad):
    txt = open(pfad).read()
    bloecke = re.findall(r"=\s*\[(\[.*?\])\]\s*:\s*list", txt, re.S)
    res = []
    for b in bloecke:
        res.append([[int(x) for x in re.findall(r"\d+", inner)] for inner in re.findall(r"\[([^\[\]]*)\]", b)])
    return res


def main():
    pfad = sys.argv[1]; K = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    coq = lies_coq(pfad)
    assert len(coq) == 3, f"erwartet 3 Spuren, gefunden {len(coq)}"
    gesamt = 0
    for (name, st), cs in zip((("114 (A)", sm.A), ("367 (D)", sm.D), ("378 (C)", sm.C)), coq):
        ps, N = spur(st, K)
        mk, zeile = lauf_original(st, N)
        print(f"  sweepmodell.lauf({N} TM-Schritte, zaehlen): {zeile}")
        if mk != K:
            print(f"  ABWEICHUNG: lauf() zaehlt {mk} Makroschritte, erwartet {K}"); gesamt += 1
        n = min(len(ps), len(cs))
        erste = next((i for i in range(n) if ps[i] != cs[i]), None)
        if erste is None and len(ps) != len(cs):
            erste = n
        maxblock = max((x - 1 for z in cs for x in z[3:] if x >= 2), default=0)
        print(f"{name}: Rocq {len(cs)} Zustaende, Python {len(ps)}, groesster Block {maxblock} Woerter, "
              + ("GLEICH" if erste is None else f"ABWEICHUNG ab Zustand {erste}: Rocq {cs[erste] if erste < len(cs) else '-'} "
                 f"Python {ps[erste] if erste < len(ps) else '-'}"))
        gesamt += erste is not None
    print("ERGEBNIS:", "alle gleich" if not gesamt else f"{gesamt} Start(s) mit Abweichung")
    return 1 if gesamt else 0


if __name__ == "__main__":
    sys.exit(main())
