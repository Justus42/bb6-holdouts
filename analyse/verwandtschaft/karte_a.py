"""Programm A der Verwandtschaftskarte (Python).

Sucht in einer Liste von 6-Zustands-Maschinen (Standardformat, '---' = Halt) drei Verwandtschaften:

  tabelle      gleiche Tabelle bis auf Umbenennung der Zustaende und ggf. Spiegelung (L<->R),
               Start beliebig. Methode: kanonische Form = kleinste Zeichenkette ueber alle
               720 Umbenennungen x 2 Spiegelungen, Startzustand ignoriert.
  kern         Zusammenlegen von Zustaenden: ein Halteuebergang gilt als Joker. Fuer jedes Paar
               {P,Q} wird die kleinste Kongruenz berechnet, die P und Q vereinigt (Union-Find,
               Abschluss ueber Ziele). Gueltig, wenn alle Zustaende eines Blocks je Symbol gleich
               schreiben, gleich laufen und in denselben Block gehen (Joker ausgenommen).
               Kern = Quotientenmaschine; verglichen ueber kanonische Form (Start ignoriert).
  gleichschritt  ab Leerband Schritt fuer Schritt gleich bis eine der beiden ihr Haltefeld erreicht.
               Methode: Produktautomat ab (A,A); jedes symbolisch erreichbare Paar (p,q) muss je
               Symbol gleich schreiben und laufen, ausser eine Seite haelt. Auch gespiegelt.

Aufruf: python3 -I karte_a.py <universum.tsv: label TAB maschine> > ausgabe.tsv
Labels: hN = Holdout N, aN.k = k-te Aequivalente von Holdout N (mxdys), dN = decided N.
Ausgabe: Zeilen 'T', 'K', 'G', 'Q' (siehe Kopfzeilen), sortiert, fuer den Abgleich mit Programm B.
Fehler-Schalter fuer Negativkontrollen: Umgebungsvariable KARTE_A_FEHLER=spiegel|joker|produkt
"""
import sys, os, itertools

FEHLER = os.environ.get("KARTE_A_FEHLER", "")
NSIM = int(os.environ.get("KARTE_NSIM", "100000"))
S = "ABCDEFGH"


def parse(tm):
    tab = []
    for grp in tm.split("_"):
        row = []
        for k in range(0, len(grp), 3):
            t = grp[k:k + 3]
            row.append(None if t[2] == "-" else (int(t[0]), t[1], S.index(t[2])))
        tab.append(row)
    return tab


def fmt(tab):
    out = []
    for row in tab:
        out.append("".join("---" if t is None else f"{t[0]}{t[1]}{S[t[2]]}" for t in row))
    return "_".join(out)


def rename(tab, perm, mirror):
    """perm[alt] = neu. Liefert Tabelle mit neuen Namen."""
    k = len(tab)
    new = [None] * k
    for q in range(k):
        row = []
        for t in tab[q]:
            if t is None:
                row.append(None)
            else:
                d = t[1]
                if mirror:
                    d = "L" if d == "R" else "R"
                row.append((t[0], d, perm[t[2]]))
        new[perm[q]] = row
    return new


PERMS = {k: list(itertools.permutations(range(k))) for k in range(1, 7)}


def canon(tab):
    """kleinste Zeichenkette ueber Umbenennungen und Spiegelungen; dazu eine Zeugen-Abbildung."""
    best = None
    mirrors = (0,) if FEHLER == "spiegel" else (0, 1)
    for m in mirrors:
        for p in PERMS[len(tab)]:
            s = fmt(rename(tab, p, m))
            if best is None or s < best[0]:
                best = (s, p, m)
    return best


def congruence(tab, P, Q):
    """kleinste Kongruenz mit P~Q (Halt = Joker) oder None."""
    n = len(tab)
    par = list(range(n))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def u(a, b):
        a, b = f(a), f(b)
        if a != b:
            par[max(a, b)] = min(a, b)
            return True
        return False

    u(P, Q)
    changed = True
    while changed:
        changed = False
        for s in range(2):
            rep = {}
            for q in range(n):
                t = tab[q][s]
                if t is None and FEHLER != "joker":
                    continue
                if t is None:
                    t = (9, "X", q)  # Fehler-Schalter: Halt wie ein normaler Uebergang
                b = f(q)
                if b in rep:
                    t2 = rep[b]
                    if (t[0], t[1]) != (t2[0], t2[1]):
                        return None
                    if u(t[2], t2[2]):
                        changed = True
                else:
                    rep[b] = t
    blocks = sorted({f(q) for q in range(n)})
    return [blocks.index(f(q)) for q in range(n)]


def quotient(tab, part):
    k = max(part) + 1
    qt = [[None, None] for _ in range(k)]
    for q in range(len(tab)):
        for s in range(2):
            t = tab[q][s]
            if t is not None:
                qt[part[q]][s] = (t[0], t[1], part[t[2]])
    return qt


def lockstep(t1, t2, mirror):
    seen = {(0, 0)}
    todo = [(0, 0)]
    while todo:
        p, q = todo.pop()
        for s in range(2):
            a, b = t1[p][s], t2[q][s]
            if a is None or b is None:
                continue
            db = b[1]
            if mirror:
                db = "L" if db == "R" else "R"
            if FEHLER == "produkt":
                db = a[1]
            if (a[0], a[1]) != (b[0], db):
                return None
            nxt = (a[2], b[2])
            if nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return sorted(seen)


def run_configs(tab, start, n):
    """Laeuft n Schritte ab Leerband im Zustand start; liefert Liste der Konfigurationen
    (Zustand, Band relativ zum Kopf, ohne Randnullen) fuer t = 0..n (oder bis Halt)."""
    tape = bytearray(2 * n + 3)
    h = n + 1
    lo = hi = h
    q = start
    out = []
    for t in range(n + 1):
        a, b = lo, hi
        while a <= b and tape[a] == 0:
            a += 1
        while b >= a and tape[b] == 0:
            b -= 1
        out.append((q, h - a, bytes(tape[a:b + 1])) if a <= b else (q, 0, b""))
        tr = tab[q][tape[h]]
        if tr is None:
            break
        tape[h] = tr[0]
        h += 1 if tr[1] == "R" else -1
        q = tr[2]
        lo, hi = min(lo, h), max(hi, h)
    return out


def merge(tab, s1, s2, n):
    """erster Zeitpunkt, zu dem Lauf ab s1 und Lauf ab s2 (gleiche Tabelle, Leerband) dieselbe
    Konfiguration haben: (t1, t2) oder None (innerhalb n Schritten je Lauf)."""
    r1 = {c: t for t, c in enumerate(run_configs(tab, s1, n))}
    for t2, c in enumerate(run_configs(tab, s2, n)):
        if c in r1:
            return r1[c], t2
    return None


def cs(t, X, m):
    """kanonische Form mit festem Start: kleinste Zeichenkette ueber Umbenennungen mit X -> A."""
    best = None
    for p in PERMS[len(t)]:
        if p[X] != 0:
            continue
        f_ = fmt(rename(t, p, m))
        if best is None or f_ < best:
            best = f_
    return best


def gruppe(lab):
    return lab.split(".")[0][1:] if lab[0] in "ha" else lab


def zaehlt(a, b):
    """nur Paare mit mindestens einem Holdout und aus verschiedenen Aequivalenzgruppen"""
    return (a[0] == "h" or b[0] == "h") and gruppe(a) != gruppe(b)


def main():
    rows = [l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip()]
    labs = [r[0] for r in rows]
    ms = [r[1] for r in rows]
    tabs = [parse(m) for m in ms]
    N = len(ms)
    out = []

    # --- tabelle
    can = [canon(t) for t in tabs]
    by = {}
    for i, c in enumerate(can):
        by.setdefault(c[0], []).append(i)
    for key, idx in by.items():
        for i, j in itertools.combinations(idx, 2):
            if not zaehlt(labs[i], labs[j]):
                continue
            ziel = cs(tabs[j], 0, 0)
            wege = [f"{m}{S[X]}" for m in (0, 1) for X in range(6) if cs(tabs[i], X, m) == ziel]
            out.append(f"T\t{labs[i]}\t{labs[j]}\t" + ",".join(wege))
            mg = merge(tabs[i], 0, S.index(wege[0][1]), NSIM)
            out.append(f"V\t{labs[i]}\t{labs[j]}\t" + ("-" if mg is None else f"{mg[0]}\t{mg[1]}"))

    # --- kern
    qinfo = {}
    for i, t in enumerate(tabs):
        seen = set()
        for P, Q in itertools.combinations(range(6), 2):
            part = congruence(t, P, Q)
            if part is None or tuple(part) in seen:
                continue
            seen.add(tuple(part))
            qt = quotient(t, part)
            c = canon(qt)
            joker = any(t[q][s] is None for q in range(6) for s in range(2)
                        if sum(1 for r in range(6) if part[r] == part[q]) > 1)
            blocks = "|".join("".join(S[q] for q in range(6) if part[q] == b) for b in range(max(part) + 1))
            out.append(f"Q\t{labs[i]}\t{blocks}\t{len(qt)}\t{int(joker)}\t{c[0]}")
            qinfo.setdefault(c[0], []).append((i, qt, part[0]))
    for key, lst in qinfo.items():
        for (i, qi, si), (j, qj, sj) in itertools.combinations(lst, 2):
            if not zaehlt(labs[i], labs[j]):
                continue
            ziel = cs(qj, sj, 0)
            wege = [(m, X) for m in (0, 1) for X in range(len(qi)) if cs(qi, X, m) == ziel]
            w = ",".join(f"{m}{S[X]}" for m, X in wege)
            mg = merge(qi, si, wege[0][1], NSIM)
            out.append(f"K\t{labs[i]}\t{labs[j]}\t{S[si]}\t{w}\t{key}")
            out.append(f"W\t{labs[i]}\t{labs[j]}\t" + ("-" if mg is None else f"{mg[0]}\t{mg[1]}"))

    # --- gleichschritt
    for i in range(N):
        for j in range(i + 1, N):
            if not zaehlt(labs[i], labs[j]):
                continue
            for m in (0, 1):
                r = lockstep(tabs[i], tabs[j], m)
                if r is not None and ms[i] != ms[j]:
                    out.append(f"G\t{labs[i]}\t{labs[j]}\t{m}\t" + " ".join(S[p] + S[q] for p, q in r))
    for l in sorted(out):
        print(l)


if __name__ == "__main__":
    main()
