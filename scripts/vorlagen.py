#!/usr/bin/env python3
"""Vorlagen fuer die Kandidaten der Klassen "Monotone list" und
"Shift-overflow structural counter" (nur beschreiben, nichts beweisen, nichts beanspruchen).

Fuer jede Maschine aus data/kandidaten.csv dieser Klassen:
  - die gemergten Beweisdateien derselben Klasse ("file" in "decided"), mit Pfad im Pin,
    geordnet nach struktureller Naehe (gleiche Uebergaenge unter bester Spiegelung/Umbenennung)
  - Verwandte: gleiche Tabelle bis auf Umbenennung der Zustaende, mit oder ohne Spiegelung,
    Startzustand beliebig (wie TM1/TM2 in PR_Loop4Mono.v); Gruppen und Abgleich mit einer
    unabhaengigen Zaehlung
  - Laufgleichheit per Tabellenvergleich (Paarrelation ab (A,A)), nicht per Simulation
  - worin sie sich von PR_Loop4Mono.v unterscheidet: Klasse, Uebergangstabelle, Halteuebergang,
    beobachtetes Verhalten in einer kurzen Simulation (Beobachtung, kein Beweis)

Aufruf: python3 -I scripts/vorlagen.py <busycoq/verify am Pin>   -> data/vorlagen.md
"""
import csv
import hashlib
import importlib.machinery
import importlib.util
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN = "33209bc7dc282b38c8cd6be507bfc551fea56108"
JSON_SHA256 = "84e7b8ac2ca92dedeac98bb2bfd5f57dd5aefdef38ee4da302f9c36df2b66810"
KLASSEN = ["Monotone list", "Shift-overflow structural counter"]
REF_FILE = "PR_Loop4Mono.v"
TM1 = "1RB1LE_0RC0LC_1LD0RA_0LA0LF_0LC0LE_0LD---"
TM2 = "1RB0LC_0RC0RF_1LD1RE_0LA0RA_0RA0RE_0RB---"
N_SIM = 3_000_000
URL = f"https://github.com/ccz181078/busycoq/blob/{PIN}/verify/"

_ld = importlib.machinery.SourceFileLoader("aussage_check", str(ROOT / "scripts" / "aussage_check"))
_spec = importlib.util.spec_from_loader("aussage_check", _ld)
ac = importlib.util.module_from_spec(_spec)
_ld.exec_module(ac)
STATES = ac.STATES


def best_match(a, b):
    """max. Anzahl gleicher Uebergaenge (von 12) von a und b unter Spiegelung und Umbenennung."""
    ta, tb = ac.parse_tm(a), ac.parse_tm(b)
    best = 0
    for flip in (False, True):
        for perm in itertools.permutations(STATES):
            pi = dict(zip(STATES, perm))
            k = 0
            for (q, s), tr in ta.items():
                x = None if tr is None else (tr[0], ({"L": "R", "R": "L"}[tr[1]] if flip else tr[1]), pi[tr[2]])
                k += tb[(pi[q], s)] == x
            best = max(best, k)
    return best


# Unabhaengige Zaehlung (Orchestrator, Auftrag vom 25.11.2026), nur zum Abgleich
ORCHESTRATOR = [{114, 367, 378}, {141, 315}, {31, 222}, {274, 518}, {318, 322}]


def images(m):
    """{Tabelle: [(gespiegelt, pi)]}: alle pi(flip^f(m)), pi beliebige Umbenennung (auch von A)."""
    e = ac.parse_tm(m)
    res = {}
    for f in (False, True):
        for perm in itertools.permutations(STATES):
            pi = dict(zip(STATES, perm))
            t = {}
            for (q, s), tr in e.items():
                t[(pi[q], s)] = None if tr is None else (tr[0], ({"L": "R", "R": "L"}[tr[1]] if f else tr[1]), pi[tr[2]])
            res.setdefault(ac.tm_str(t), []).append((f, pi))
    return res


def describe_rel(f, pi):
    inv = {v: k for k, v in pi.items()}
    ren = " ".join(pi[q] for q in STATES)
    start = "gleicher Start A" if pi["A"] == "A" else f"Start A dort = Zustand {inv['A']} hier"
    return f"{'gespiegelt' if f else 'ungespiegelt'}, Zustaende A..F hier = {ren} dort, {start}"


def run_relation(a, b, flip):
    """Paarrelation ab (A,A) ueber beide Symbole. Stimmen fuer jedes erreichbare Paar Schreiben und
    Bewegen ueberein (ausser wo eine Seite haelt), laufen a und b ab Leerband Schritt fuer Schritt
    gleich (gleiches Band, gleicher Kopf), bis eine ihr Haltefeld erreicht. Rueckgabe (R, Stopps)
    oder None bei Konflikt."""
    ta, tb = ac.parse_tm(a), ac.parse_tm(b)
    R, todo, stops, rows = {("A", "A")}, [("A", "A")], [], []
    while todo:
        p, q = todo.pop()
        for s in (0, 1):
            x, y = ta[(p, s)], tb[(q, s)]
            if x is None or y is None:
                stops.append((p, q, s, x, y))
                continue
            if x[0] != y[0] or x[1] != ({"L": "R", "R": "L"}[y[1]] if flip else y[1]):
                return None
            rows.append((p, q, s, x, y))
            n = (x[2], y[2])
            if n not in R:
                R.add(n)
                todo.append(n)
    return sorted(R), sorted(stops), sorted(rows)


def tr_s(x):
    return "---" if x is None else "".join(x)


def de(n):
    return f"{n:,}".replace(",", ".")


def halt_pos(m):
    rows = m.split("_")
    return ", ".join(f"{STATES[i]}{s}" for i, r in enumerate(rows) for s in (0, 1) if r[3 * s:3 * s + 3] == "---")


def compress(bits):
    out, i, n = [], 0, len(bits)
    while i < n:
        best = None
        for p in range(1, 7):
            blk = bits[i:i + p]
            if len(blk) < p or (p > 1 and len(set(blk)) == 1):
                continue
            e = 1
            while bits[i + e * p:i + (e + 1) * p] == blk:
                e += 1
            if e >= 3 and (best is None or e * p > best[1] * len(best[0])):
                best = (blk, e)
        if best:
            out.append(f"({best[0]})^{best[1]}" if len(best[0]) > 1 else f"{best[0]}^{best[1]}")
            i += len(best[0]) * best[1]
        else:
            out.append(bits[i])
            i += 1
    return out


def simulate(m, n_steps):
    """Dichtes Band; Rekord = Kopf betritt eine noch nie besuchte Zelle (Zustand nach dem Schritt)."""
    t = {}
    for qi, row in enumerate(m.split("_")):
        for s in (0, 1):
            tr = row[3 * s:3 * s + 3]
            t[(qi, s)] = None if tr == "---" else (int(tr[0]), 1 if tr[1] == "R" else -1, ord(tr[2]) - 65)
    size = 1 << 16
    tape = bytearray(size)
    pos = lo = hi = size // 2
    q = steps = 0
    rec = Counter()
    trace = []
    last = None
    while steps < n_steps:
        tr = t[(q, tape[pos])]
        if tr is None:
            return {"halt": steps, "rec": rec, "last": last, "trace": trace}
        w, d, q = tr
        tape[pos] = w
        pos += d
        steps += 1
        if pos < 0 or pos >= len(tape):
            ext = len(tape)
            tape = bytearray(ext) + tape + bytearray(ext)
            pos, lo, hi = pos + ext, lo + ext, hi + ext
        side = "L" if pos < lo else "R" if pos > hi else None
        if side:
            lo, hi = min(lo, pos), max(hi, pos)
            rec[(side, STATES[q])] += 1
            snap = bytes(tape[lo:hi + 1])
            last = (side, STATES[q], steps, snap)
            trace.append((steps, side, hashlib.sha256(snap).hexdigest()[:16]))
    return {"halt": None, "rec": rec, "last": last, "trace": trace}


def describe_sim(r):
    rec = r["rec"]
    nl = sum(v for (s, _), v in rec.items() if s == "L")
    nr = sum(v for (s, _), v in rec.items() if s == "R")
    side, st, at, snap = r["last"]
    bits = "".join(map(str, snap))
    toks = compress(bits)
    if side == "L":
        sample = f"0^inf <{st} " + " ".join(toks[:14]) + (" ..." if len(toks) > 14 else "")
    else:
        sample = ("... " if len(toks) > 14 else "") + " ".join(toks[-14:]) + f" {st}> 0^inf"
    top = ", ".join(q for (_, q), _ in Counter({k: v for k, v in rec.items() if k[0] == side}).most_common(2))
    return (f"waechst nach {'links' if nl > nr else 'rechts'} ({nl} neue Zellen links, {nr} rechts), "
            f"Rekorde dort meist in Zustand {top}; Band beim letzten Rekord (Schritt {de(at)}, Breite {len(bits)}): "
            f"`{sample}`")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    verify = Path(sys.argv[1])
    head = subprocess.run(["git", "-C", str(verify.parent), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != PIN:
        sys.exit(f"FEHLER: busycoq nicht auf {PIN} ({head})")
    raw = (ROOT / "data" / "holdouts.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != JSON_SHA256:
        sys.exit("FEHLER: SHA-256 von holdouts.json weicht ab")
    d = json.loads(raw)
    H = {h["tm"]: h for h in d["holdouts"]}
    lst = {h["tm"]: h["n"] for h in d["holdouts"]}
    dec = d["decided"]
    cands = [r for r in csv.DictReader(open(ROOT / "data" / "kandidaten.csv")) if r["Klasse"] in KLASSEN]

    # Beweisdateien je Klasse, mit Urteil aus den Haupttheoremen der Datei
    files = {}
    for k in KLASSEN:
        for x in dec:
            if x["class"] != k or x["by"] != "proof":
                continue
            p = verify / x["file"]
            if not p.exists():
                sys.exit(f"FEHLER: {x['file']} fehlt im Pin")
            f = files.setdefault((k, x["file"]), {"entries": [], "lines": None, "analyse": None})
            f["entries"].append(x)
            if f["analyse"] is None:
                src = p.read_text()
                f["lines"] = src.count("\n")
                f["analyse"] = ac.analyse(src)

    def verdict(fe, tm):
        machines, theorems, _ = fe["analyse"]
        # nur exakt oder Spiegelbild mit gleichem Start A: dann gilt das Urteil auch fuer tm
        twins = {t for t, pis in ac.mirror_twins(tm).items() if any(pi["A"] == "A" for pi in pis)}
        idx ={i for i, mc in enumerate(machines) if mc["tm"] == tm or mc["tm"] in twins}
        v = {th["verdict"] for th in theorems if th["machine"] in idx}
        form = "exakt" if any(machines[i]["tm"] == tm for i in idx) else ("gespiegelt" if idx else "?")
        return ({"halt": "haelt", "nonhalt": "haelt nicht"}.get(next(iter(v)), "?") if len(v) == 1 else "?"), form

    sims = {m: simulate(m, N_SIM) for m in [TM1] + [r["Maschinen-String"] for r in cands]}
    ref = sims[TM1]

    o = []
    w = o.append
    w("# Vorlagen fuer Kandidaten: Monotone list und Shift-overflow structural counter")
    w("")
    w("Erzeugt mit `python3 -I scripts/vorlagen.py <busycoq/verify>`. Nur Beschreibung: es wird nichts")
    w("bewiesen und nichts beansprucht. Vor jeder Arbeit an einer Maschine in #bb6 pruefen, ob jemand")
    w("anderes daran arbeitet.")
    w("")
    w(f"- Daten: `data/holdouts.json` (SHA-256 `{JSON_SHA256[:16]}…`), `data/kandidaten.csv`")
    w(f"- busycoq: `ccz181078/busycoq` @ `{PIN}`; Pfade unten relativ zu `verify/` am Pin")
    w("- **Naehe k/12**: groesste Zahl gleicher Uebergaenge unter Spiegelung (L/R) und beliebiger")
    w("  Umbenennung der Zustaende; 12/12 hiesse Spiegel-Zwilling bzw. Umbenennung. Ein grobes Mass,")
    w("  es sagt nichts darueber, ob eine Beweistechnik uebertragbar ist.")
    w(f"- **Simulation**: {de(N_SIM)} Schritte ab Leerband, Start A. Rekord = der Kopf betritt eine noch nie")
    w("  besuchte Zelle; angegeben ist der Zustand danach. Band in Kurzform, `(w)^e` = e-mal w.")
    w("  Das ist eine **Beobachtung** ueber den Anfang des Laufs, keine Aussage ueber das Verhalten.")
    w("")
    # Ueberblick
    cm = {r["Maschinen-String"]: r["n"] for r in cands}
    im = {a: images(a) for a in cm}
    rel = {}  # (a, b) -> [(f, pi)], b = pi(flip^f(a))
    for a in cm:
        for b in cm:
            if a != b and b in im[a]:
                rel[(a, b)] = im[a][b]
    parent = {a: a for a in cm}

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x
    for a, b in rel:
        parent[find(a)] = find(b)
    groups = {}
    for a in cm:
        groups.setdefault(find(a), set()).add(int(cm[a]))
    groups = sorted(groups.values(), key=lambda g: min(g))
    outside = {cm[a]: [f"Liste n={n2}" for t2, n2 in lst.items() if t2 in im[a] and t2 not in cm]
               + [f"decided n={x['n']}" for x in dec if x["tm"] in im[a]] for a in cm}
    runs = []
    for a, b in itertools.combinations(cm, 2):
        for f in (False, True):
            rr = run_relation(a, b, f)
            if rr:
                runs.append((a, b, f, rr))
    near = {a: best_match(a, TM1) for a in cm}
    fmt_g = lambda gs: " ".join("{" + ",".join(str(x) for x in sorted(g)) + "}" for g in gs)
    orch = sorted(ORCHESTRATOR, key=lambda g: min(g))
    w("## Auf einen Blick")
    w("")
    w("- **Gruppen** (gleiche Tabelle bis auf Umbenennung der Zustaende, mit oder ohne Spiegelung,")
    w(f"  Startzustand beliebig): {fmt_g(groups)}")
    for (a, b), lst_ab in sorted(rel.items(), key=lambda kv: (int(cm[kv[0][0]]), int(cm[kv[0][1]]))):
        if int(cm[a]) < int(cm[b]):
            w(f"  - {cm[a]} -> {cm[b]}: " + "; ".join(describe_rel(f, pi) for f, pi in lst_ab))
    w(f"- **Abgleich** mit der unabhaengigen Zaehlung {fmt_g(orch)}: "
      + ("stimmt ueberein." if [set(g) for g in groups] == [set(g) for g in orch] else
         "WEICHT AB: nur hier " + fmt_g([g for g in groups if g not in orch]) + ", nur dort " + fmt_g([g for g in orch if g not in groups])))
    w("  Abweichung zur Fassung vom 24.11.2026: Dort wurden nur Spiegel-Zwillinge gesucht (immer mit")
    w("  Spiegelung). Dadurch fehlte 318/322 (ungespiegelt, anderer Start), und 114/367 (ungespiegelt)")
    w("  war nur indirekt ueber 378 sichtbar. Die damalige Angabe \"318/518 bandgleich\" beruhte nur auf")
    w("  3 Mio. Simulationsschritten; sie ist unten durch einen Tabellenvergleich ersetzt. 318 und 518")
    w("  haben keine gleiche Tabelle und gehoeren deshalb nicht in eine Gruppe.")
    w("- Verwandte in Liste oder decided ausserhalb der Kandidaten: "
      + (", ".join(f"{n}: {v}" for n, v in outside.items() if v) or "keine"))
    for a, b, f, (R, stops, rows) in runs:
        w(f"- **Laufgleich bis zum Halten: {cm[a]} und {cm[b]}** ({'gespiegelt' if f else 'ungespiegelt'};"
          " Tabellenvergleich, keine Simulation noetig). Erreichbare Zustandspaare ab (A,A), ueber beide")
        w("  Symbole: " + ", ".join(f"({p},{q})" for p, q in R) + ". Die Zuordnung ist "
          + ("eine Umbenennung." if len({p for p, _ in R}) == len(R) == len({q for _, q in R}) else
             "**keine** Umbenennung: ein Zustand der einen Maschine entspricht teils zwei Zustaenden der anderen."))
        w(f"  Fuer jedes Paar und Symbol stimmen Schreiben und Bewegen ueberein ({len(R)} Paare x 2 Symbole,"
          f" davon {len(stops)} Haltefaelle, bleiben {len(rows)}):")
        w("")
        w(f"  | Paar | liest | {cm[a]} | {cm[b]} |")
        w("  |---|---|---|---|")
        for p, q, s, x, y in rows:
            w(f"  | ({p},{q}) | {s} | {p}{s}={tr_s(x)} | {q}{s}={tr_s(y)} |")
        w("")
        w("  Ausnahmen sind nur die Haltefelder:")
        for p, q, s, x, y in stops:
            who = cm[a] if x is None else cm[b]
            other = (cm[b], f"{q}{s}={tr_s(y)}") if x is None else (cm[a], f"{p}{s}={tr_s(x)}")
            w(f"  - Paar ({p},{q}) liest {s}: {who} haelt, {other[0]} macht {other[1]} weiter.")
        w(f"  Also: Ab Leerband laufen beide Schritt fuer Schritt gleich (gleiches Band, gleicher Kopf), bis")
        w("  eine ihr Haltefeld erreicht; das gilt fuer jede Schrittzahl, nicht nur fuer die Simulation. Ob das")
        w("  je geschieht, ist die offene Haltefrage selbst; daraus folgt nichts ueber Halten oder Nicht-Halten.")
        hs = [cm[m] for m in (a, b) if sims[m]["halt"] is not None]
        w(f"  In {de(N_SIM)} Simulationsschritten erreicht " + ("keine der beiden ihr Haltefeld." if not hs else
                                                            f"n={', '.join(hs)} das Haltefeld."))
    w(f"- Naehe zu PR_Loop4Mono TM1: {min(near.values())}–{max(near.values())}/12 bei allen Kandidaten"
      " (zum Vergleich: gleiche Tabelle haette 12/12)")
    for k in KLASSEN:
        cnt = Counter(verdict(fe, x["tm"])[0] for (kk, _), fe in files.items() if kk == k for x in fe["entries"])
        w(f"- {k}: Beweise im Pin " + ", ".join(f"{v}x {u}" for u, v in sorted(cnt.items())))
    w("")
    w(f"## Referenz: `{REF_FILE}`")
    w("")
    w(f"- Pfad im Pin: [`verify/{REF_FILE}`]({URL}{REF_FILE}); in decided Klasse Monotone list (n=652, n=950)")
    w(f"- TM1 `{TM1}` und TM2 `{TM2}`; TM2 ist der Spiegel-Zwilling von TM1 (Zustaende A..F = C D A B E F")
    w("  dort, Start A dort = Zustand C hier). Beide Theoreme: `halts tm c0` (die Maschinen **halten**).")
    w("- Technik laut Dateikopf: an linken Rekorden (Zustand D am linken Ende) ist das Band eine Liste")
    w("  `W(x0) s0 W(x1) s1 …` mit `W(e) = (10)^e` und Trennern `s` in {0,1}; ein Listenmodell mit")
    w("  `check` (native_compute) laeuft 1.307.718 Ticks bis zu einem Haltefenster.")
    w(f"- Halteuebergang: {halt_pos(TM1)}")
    w(f"- Simulation TM1: {describe_sim(ref)}")
    w("")

    for k in KLASSEN:
        cls = [r for r in cands if r["Klasse"] == k]
        fl = [(fn, fe) for (kk, fn), fe in sorted(files.items()) if kk == k]
        w(f"## {k}")
        w("")
        w(f"Gemergte Beweisdateien dieser Klasse (decided, by=proof): {len(fl)} Dateien, "
          f"{sum(len(fe['entries']) for _, fe in fl)} Maschinen.")
        w("")
        w("Urteil = Haupttheorem der Datei fuer die Maschine selbst (exakt) oder ihr Spiegelbild mit")
        w("Start A (gespiegelt); `?` = in keiner dieser Formen gefunden.")
        w("")
        w("| Datei (Pin) | Zeilen | Maschinen aus decided: n, Urteil laut Datei, Form in der Datei |")
        w("|---|---:|---|")
        for fn, fe in fl:
            ms = []
            for x in fe["entries"]:
                v, form = verdict(fe, x["tm"])
                ms.append(f"n={x['n']} `{x['tm']}` {v}, {form}")
            w(f"| [`verify/{fn}`]({URL}{fn}) | {fe['lines']} | " + "<br>".join(ms) + " |")
        w("")
        for r in cls:
            m = r["Maschinen-String"]
            h = H[m]
            s = sims[m]
            w(f"### n={r['n']} `{m}`")
            w("")
            w(f"- slugbird: Status `{(h['slugbird'] or {}).get('status')}`, simuliert {r['simulierte Schritte']} Schritte; "
              f"busycoq: `{h['busycoq']['status']}`, keine PR")
            if h["aliases"]:
                w(f"- Aequivalente Maschinen laut holdouts.json: {len(h['aliases'])}"
                  + (", busycoq erwaehnt sie in " + ", ".join(sorted({x['file'] for x in h['busycoq']['mentioned_in']}))
                     if h["busycoq"]["mentioned_in"] else ""))
            g = next(g for g in groups if int(r["n"]) in g)
            vw = [f"n={cm[b]} ({describe_rel(*rel[(m, b)][0])})" for b in cm if (m, b) in rel]
            w(f"- Gruppe {fmt_g([g])}; Verwandte: " + ("; ".join(vw) if vw else "keine")
              + (f"; ausserhalb der Kandidaten: {', '.join(outside[r['n']])}" if outside[r["n"]] else ""))
            for a, b, f, _ in runs:
                if m in (a, b):
                    w(f"- Laufgleich bis zum Halten mit n={cm[b] if m == a else cm[a]} (Tabellenvergleich, siehe Auf einen Blick)")
            ranked = sorted(((max(best_match(m, x["tm"]) for x in fe["entries"]), fn,
                              max(fe["entries"], key=lambda x: best_match(m, x["tm"]))["n"]) for fn, fe in fl),
                            key=lambda z: (-z[0], z[1]))
            w("- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): "
              + "; ".join(f"`verify/{fn}` {kk}/12 (n={nn})" for kk, fn, nn in ranked))
            w(f"- Unterschied zu `{REF_FILE}`:")
            w(f"  - Klasse: {k}" + (" (dieselbe wie PR_Loop4Mono)" if k == "Monotone list" else " (PR_Loop4Mono: Monotone list)"))
            w(f"  - Uebergangstabelle: Naehe zu TM1 {best_match(m, TM1)}/12 (TM2 ist Zwilling von TM1, gleicher Wert); "
              f"Halteuebergang {halt_pos(m)} (TM1: {halt_pos(TM1)})")
            w(f"  - Simulation: {describe_sim(s)}")
            w("")
    (ROOT / "data" / "vorlagen.md").write_text("\n".join(o) + "\n")
    print("data/vorlagen.md geschrieben")


if __name__ == "__main__":
    main()
