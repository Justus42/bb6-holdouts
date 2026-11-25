"""Baut data/verwandtschaft.csv und die Familienliste aus den Ausgaben von Programm A und B.

Aufruf (aus analyse/verwandtschaft/):
  python3 -I csv_bauen.py ergebnis_a_1e5.tsv ergebnis_b_1e6.tsv ergebnis_b_1e5.tsv divergenz_1e9.txt \
      ../../data/verwandtschaft.csv familien.tsv

Bezeichnungen in der CSV: 114 = Holdout n=114 der Liste vom 30.10.2026; 322.1 = erste Aequivalente
von 322 laut mxdys-Aequivalenzgruppen (holdouts.json, Feld aliases); d833 = decided n=833.
"""
import sys, collections

S = "ABCDEF"
fa, fb, fs, fdiv, fcsv, ffam = sys.argv[1:7]
A = [l.rstrip("\n").split("\t") for l in open(fa)]
B = [l.rstrip("\n").split("\t") for l in open(fb) if not l.startswith("S")]
B += [l.rstrip("\n").split("\t") for l in open(fs) if l.startswith("S")]
DIV = {}
for l in open(fdiv):
    if l.startswith("#"):
        continue
    p = l.split()
    DIV[(p[0], p[1])] = l.split(" ", 3)[3].strip()


def name(lab):
    return lab[1:] if lab[0] in "ha" else lab


def gruppe(lab):
    return lab.split(".")[0][1:] if lab[0] in "ha" else lab


# bekannte Gruppen (Quellen siehe Bericht)
WIKI = [{62, 212, 369, 377}, {185, 422, 441, 490, 538}, {23, 215, 288, 502}, {186, 317, 573}]
VORLAGEN = [{31, 222}, {114, 367, 378}, {141, 315}, {274, 518}, {318, 322}]
M5 = {274, 318, 322, 518}


def bekannt(a, b, art):
    if a[0] != "h" or b[0] != "h":
        return ""
    x, y = int(a[1:]), int(b[1:])
    q = []
    if any(x in g and y in g for g in WIKI):
        q.append("wiki-weiterleitung")
    if art == "tabelle" and any(x in g and y in g for g in VORLAGEN):
        q.append("data/vorlagen.md")
    if art in ("kern", "gleichschritt") and x in M5 and y in M5:
        q.append("analyse/318_518.md")
    return ";".join(q)


# Verschmelzen: V/W aus B (laengerer Lauf); Kern-Bloecke aus A (Q-Zeilen)
VB = {(l[1], l[2]): l[3:] for l in B if l[0] == "V"}
WB = collections.defaultdict(list)
for l in B:
    if l[0] == "W":
        WB[(l[1], l[2])].append(l[3:])
QA = collections.defaultdict(list)
for l in A:
    if l[0] == "Q":
        QA[l[1]].append((l[2], l[5]))

rows = []
kcount = collections.Counter()
for l in A:
    if l[0] == "T":
        a, b, wege = l[1], l[2], l[3]
        m, X = wege.split(",")[0][0], wege.split(",")[0][1]
        v = VB[(a, b)]
        rows.append([name(a), name(b), "tabelle", "ja" if m == "1" else "nein",
                     f"{name(b)} = Tabelle von {name(a)} ab {X}" + (f" (weitere: {wege})" if "," in wege else ""),
                     "", "nein" if v == ["-"] else f"ja, Schritt {v[0]}/{v[1]}", bekannt(a, b, "tabelle")])
    elif l[0] == "K":
        a, b, sa, wege, key = l[1], l[2], l[3], l[4], l[5]
        k = kcount[(a, b)]
        kcount[(a, b)] += 1
        w = WB[(a, b)][k]
        m, X = wege.split(",")[0][0], wege.split(",")[0][1]
        blocks_a = [bl for bl, kk in QA[a] if kk == key][0].split("|")
        blocks_b = [bl for bl, kk in QA[b] if kk == key][0].split("|")
        rows.append([name(a), name(b), "kern", "ja" if m == "1" else "nein",
                     f"{name(b)} startet im Kern von {name(a)} bei Block {blocks_a[S.index(X)]}"
                     + (f" (weitere: {wege})" if "," in wege else ""),
                     f"{name(a)}: {'|'.join(blocks_a)}; {name(b)}: {'|'.join(blocks_b)}; Kern {key}",
                     "nein" if w == ["-"] else f"ja, Schritt {w[0]}/{w[1]}", bekannt(a, b, "kern")])
    elif l[0] == "G":
        a, b, m, paare = l[1], l[2], l[3], l[4]
        rows.append([name(a), name(b), "gleichschritt", "ja" if m == "1" else "nein",
                     "gleicher Start A", f"Zustandspaare {paare}", "", bekannt(a, b, "gleichschritt")])
G = {(l[1], l[2]) for l in A if l[0] == "G"}
for l in B:
    if l[0] == "S" and (l[1], l[2]) not in G:
        a, b = l[1], l[2]
        rows.append([name(a), name(b), "gleichschritt_beobachtet", "ja" if l[3] == "1" else "nein",
                     "gleicher Start A", DIV.get((a, b), "nicht nachgeprueft"), "", bekannt(a, b, "gleichschritt")])

with open(fcsv, "w") as f:
    f.write("# Verwandtschaften zwischen BB(6)-Holdouts (Liste mxdys 30.10.2026, 608 Maschinen); "
            "Erzeugt von analyse/verwandtschaft/csv_bauen.py; Erklaerung in analyse/verwandtschaft.md\n")
    f.write("n1,n2,art,gespiegelt,start,detail,laeufe_verschmelzen,bekannt_in\n")
    for r in rows:
        f.write(",".join('"' + c.replace('"', "'") + '"' if ("," in c or " " in c) else c for c in r) + "\n")

# Familien: Holdout-Gruppen (Aequivalente zaehlen zu ihrem Holdout), verbunden durch eine der Arten
par = {}


def fnd(x):
    par.setdefault(x, x)
    while par[x] != x:
        x = par[x]
    return x


arten = collections.defaultdict(set)
dec = collections.defaultdict(set)
for l in A + [x for x in B if x[0] == "S"]:
    if l[0] not in "TKGS":
        continue
    a, b = l[1], l[2]
    if a[0] == "d" or b[0] == "d":
        h = a if a[0] != "d" else b
        dd = b if a[0] != "d" else a
        dec[gruppe(h)].add(dd)
        continue
    if l[0] == "S" and (a, b) in G:
        continue
    ga, gb = gruppe(a), gruppe(b)
    par[fnd(ga)] = fnd(gb)
fam = collections.defaultdict(set)
for x in list(par):
    fam[fnd(x)].add(int(x))
art_von = collections.defaultdict(set)
code = {"T": "tabelle", "K": "kern", "G": "gleichschritt", "S": "gleichschritt_beobachtet"}
for l in A + [x for x in B if x[0] == "S"]:
    if l[0] in "TKGS" and l[1][0] != "d" and l[2][0] != "d" and not (l[0] == "S" and (l[1], l[2]) in G):
        art_von[fnd(gruppe(l[1]))].add(code[l[0]])
famlist = sorted(fam.items(), key=lambda kv: (-len(kv[1]), min(kv[1])))
with open(ffam, "w") as f:
    f.write("familie\tgroesse\tholdouts\tarten\tdecided_mit_gleicher_tabelle\n")
    for i, (root, mem) in enumerate(famlist):
        d = sorted({x for m in mem for x in dec.get(str(m), ())})
        f.write(f"F{i+1}\t{len(mem)}\t{','.join(map(str, sorted(mem)))}\t{','.join(sorted(art_von[root]))}\t{','.join(d)}\n")
print("Zeilen CSV:", len(rows), "Familien:", len(famlist), "Holdouts in Familien:", sum(len(m) for m in fam.values()))
print(collections.Counter(r[2] for r in rows))
print(collections.Counter(len(m) for m in fam.values()))
