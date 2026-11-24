#!/usr/bin/env python3
"""Vorlagen fuer die Kandidaten der Klassen "Monotone list" und
"Shift-overflow structural counter" (nur beschreiben, nichts beweisen, nichts beanspruchen).

Fuer jede Maschine aus data/kandidaten.csv dieser Klassen:
  - die gemergten Beweisdateien derselben Klasse ("file" in "decided"), mit Pfad im Pin,
    geordnet nach struktureller Naehe (gleiche Uebergaenge unter bester Spiegelung/Umbenennung)
  - Spiegel-Zwillinge in Liste oder decided (wie TM1/TM2 in PR_Loop4Mono.v)
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
    pairs = sorted({tuple(sorted((cm[a], cm[b]), key=int)) for a in cm for b in cm
                    if a != b and b in ac.mirror_twins(a)}, key=lambda p: (int(p[0]), int(p[1])))
    same = sorted({tuple(sorted((cm[a], cm[b]), key=int)) for a in cm for b in cm
                   if a != b and sims[a]["trace"] == sims[b]["trace"]})
    dec_tw = [cm[a] for a in cm if any(x["tm"] in ac.mirror_twins(a) for x in dec)]
    near = {a: best_match(a, TM1) for a in cm}
    w("## Auf einen Blick")
    w("")
    w("- Spiegel-Zwillingspaare unter den Kandidaten (wie TM1/TM2 in PR_Loop4Mono, jeweils mit anderem")
    w("  Startzustand): " + ", ".join(f"{a}/{b}" for a, b in pairs))
    w("- In der Simulation bandgleich (ohne Zwillinge zu sein): " + (", ".join(f"{a}/{b}" for a, b in same) or "keine"))
    w("- Spiegel-Zwilling einer gemergten Maschine (decided): " + (", ".join(dec_tw) or "keiner der Kandidaten"))
    w(f"- Naehe zu PR_Loop4Mono TM1: {min(near.values())}–{max(near.values())}/12 bei allen Kandidaten"
      " (zum Vergleich: ein Spiegel-Zwilling haette 12/12)")
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
            tw = ac.mirror_twins(m)
            twl = []
            for t2, n2 in lst.items():
                if t2 in tw and t2 != m:
                    pi = tw[t2][0]
                    inv = {v: kk for kk, v in pi.items()}
                    twl.append(f"n={n2} (Start A dort = Zustand {inv['A']} hier)")
            for x in dec:
                if x["tm"] in tw and x["tm"] != m:
                    twl.append(f"decided n={x['n']} {x['file']}")
            w("- Spiegel-Zwillinge in Liste/decided: " + ("; ".join(twl) if twl else "keine"))
            same = [r2["n"] for r2 in cands if r2 is not r and sims[r2["Maschinen-String"]]["trace"] == s["trace"]]
            if same:
                w(f"- In der Simulation bandgleich mit n={', '.join(same)} (gleiche Rekordschritte und Baender)")
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
