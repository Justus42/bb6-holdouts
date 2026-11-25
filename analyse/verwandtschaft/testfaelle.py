"""Erzeugt das Test-Universum fuer die Negativ-/Positivkontrollen der Verwandtschaftskarte.
Aufruf: python3 -I testfaelle.py <universum.tsv> > test_universum.tsv
Echte Holdouts plus kuenstliche Maschinen h90xx (Labels mit h, damit sie mitgezaehlt werden)."""
import sys
U = dict(l.rstrip("\n").split("\t") for l in open(sys.argv[1]) if l.strip())
S = "ABCDEF"


def neu_start(tm, X, spiegel):
    """gleiche Tabelle, Start X, ggf. gespiegelt; Zustaende in Breitensuche-Reihenfolge ab X umbenannt."""
    g = [[tm.split("_")[q][3 * s:3 * s + 3] for s in range(2)] for q in range(6)]
    order = [S.index(X)]
    for q in order:
        for t in g[q]:
            if t[2] != "-" and S.index(t[2]) not in order:
                order.append(S.index(t[2]))
    for q in range(6):
        if q not in order:
            order.append(q)
    ren = {old: new for new, old in enumerate(order)}
    out = []
    for old in order:
        row = ""
        for t in g[old]:
            if t[2] == "-":
                row += "---"
            else:
                d = t[1] if not spiegel else ("L" if t[1] == "R" else "R")
                row += t[0] + d + S[ren[S.index(t[2])]]
        out.append(row)
    return "_".join(out)


def aendere(tm, q, s, neu):
    g = tm.split("_")
    g[q] = g[q][:3 * s] + neu + g[q][3 * s + 3:]
    return "_".join(g)


rows = []
for n in ["h22", "h114", "h367", "h378", "h318", "h518", "h274", "h322", "h88", "h312"]:
    rows.append((n, U[n]))
# h9001: Tabelle von h22 ab E, gespiegelt. E0 = 1RB wie A0 -> Laeufe verschmelzen nach 1 Schritt.
rows.append(("h9001", neu_start(U["h22"], "E", True)))
# h9002: h367 mit geaendertem B0 (Schreibsymbol umgedreht) -> keine Tabellen-Verwandtschaft mehr
b0 = U["h367"].split("_")[1][:3]
rows.append(("h9002", aendere(U["h367"], 1, 0, ("0" if b0[0] == "1" else "1") + b0[1:])))
# h9003: h518 mit D0 = 1RA statt 1LA -> kein Gleichschritt mit h318
rows.append(("h9003", aendere(U["h518"], 3, 0, "1RA")))
# h9004: h318 mit C1 = 1RE statt 1RF -> kein gemeinsamer Kern mit h274/h322/h518
rows.append(("h9004", aendere(U["h318"], 2, 1, "1RE")))
for n, m in rows:
    print(f"{n}\t{m}")
