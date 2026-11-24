#!/usr/bin/env python3
"""Auswertung von data/holdouts.json (nur lesen, nichts beanspruchen).

Ausgaben:
  data/kandidaten.csv          Klasse, n, Maschinen-String, simulierte Schritte
  data/auswertung_holdouts.md  Zaehltabellen

Regeln (Vorgabe Block 2b):
  - busycoq-Status zaehlen, gesamt und je Klasse
  - je Klasse die per Beweis entschiedenen Maschinen aus "decided" (by == "proof")
  - Kandidat: busycoq.status == "open" UND busycoq.prs leer (streng: auch keine
    erwaehnenden/geschlossenen PRs), slugbird.status == "rules", tags leer,
    Klasse hat >= 5 Eintraege mit by == "proof" in "decided" (exakter Klassenname)
  - Discord-Angaben werden nicht verwendet.
Aufruf: python3 -I scripts/auswertung_holdouts.py
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "holdouts.json"
EXPECTED_SHA256 = "84e7b8ac2ca92dedeac98bb2bfd5f57dd5aefdef38ee4da302f9c36df2b66810"
PIN = "33209bc7dc282b38c8cd6be507bfc551fea56108"
MIN_PROOFS = 5
STATUSES = ["open", "pr_open", "solved"]

raw = SRC.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
assert sha == EXPECTED_SHA256, f"SHA-256 weicht ab: {sha}"
d = json.loads(raw)
H, D = d["holdouts"], d["decided"]

head = d["busycoq"]["head"]["sha"]
lines = []
out = lines.append
out("# Auswertung data/holdouts.json")
out("")
out(f"- Datei-SHA-256: `{sha}` (= QUELLE.md)")
out(f"- generated_at: {d['generated_at']}, Liste vom {d['list']['published']} ({d['list']['count']} Maschinen)")
out(f"- busycoq.head.sha: `{head}` -> {'passt zum Pin' if head == PIN else 'PASST NICHT zum Pin'} `{PIN[:8]}`")
out(f"- slugbird-Guide: {d['sources']['slugbird']['as_of']}")
out("")

bc = Counter(h["busycoq"]["status"] for h in H)
unknown = set(bc) - set(STATUSES)
assert not unknown, f"unbekannte busycoq-Status: {unknown}"
out("## busycoq-Status gesamt")
out("")
out("| Status | Anzahl |")
out("|---|---:|")
for s in STATUSES:
    out(f"| {s} | {bc[s]} |")
out(f"| **Summe** | **{sum(bc.values())}** |")
cnt = d["counts"]["by_status"]
out("")
out(f"Zum Vergleich `counts.by_status` in der Datei: {json.dumps(cnt)} "
    f"(dort wird `sim_halt` getrennt gefuehrt; in den Eintraegen selbst stehen diese als `open`).")
out("")

proofs = Counter(x["class"] for x in D if x["by"] == "proof")
by_dec = Counter(x["by"] for x in D)
per_class = defaultdict(Counter)
for h in H:
    per_class[h["class"]][h["busycoq"]["status"]] += 1

out("## je Klasse (Holdouts nach busycoq-Status, dazu Beweise aus `decided`)")
out("")
out(f"`decided`: {len(D)} Eintraege, davon by=proof {by_dec['proof']}, by=equivalence {by_dec['equivalence']}; "
    f"{sum(1 for x in D if x['by'] == 'proof' and not x['class'])} proof-Eintraege ohne Klasse.")
out("")
out("| Klasse | open | pr_open | solved | Holdouts | Beweise in decided |")
out("|---|---:|---:|---:|---:|---:|")
for c in sorted(per_class, key=lambda c: (-sum(per_class[c].values()), c)):
    pc = per_class[c]
    out(f"| {c} | {pc['open']} | {pc['pr_open']} | {pc['solved']} | {sum(pc.values())} | {proofs.get(c, 0)} |")
out("")

cand = []
for h in H:
    b, sb = h["busycoq"], h.get("slugbird") or {}
    if (b["status"] == "open" and not b["prs"] and sb.get("status") == "rules"
            and not h["tags"] and proofs.get(h["class"], 0) >= MIN_PROOFS):
        cand.append((h["class"], h["n"], h["tm"], sb.get("simulated") or ""))
cand.sort()
with open(ROOT / "data" / "kandidaten.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Klasse", "n", "Maschinen-String", "simulierte Schritte"])
    w.writerows(cand)

# Trichter zur Nachvollziehbarkeit
s1 = [h for h in H if h["busycoq"]["status"] == "open"]
s2 = [h for h in s1 if not h["busycoq"]["prs"]]
s3 = [h for h in s2 if (h.get("slugbird") or {}).get("status") == "rules"]
s4 = [h for h in s3 if not h["tags"]]
s5 = [h for h in s4 if proofs.get(h["class"], 0) >= MIN_PROOFS]
out("## Kandidaten (data/kandidaten.csv)")
out("")
out("| Filterstufe | verbleibend |")
out("|---|---:|")
for name, s in [("busycoq open", s1), ("+ keine PR (auch keine erwaehnende/geschlossene)", s2),
                ("+ slugbird-Status rules", s3), ("+ keine Tags", s4),
                (f"+ Klasse mit >= {MIN_PROOFS} Beweisen in decided", s5)]:
    out(f"| {name} | {len(s)} |")
out("")
out("Ausgeschlossen in der letzten Stufe (Klasse, Beweise in decided): "
    + ", ".join(f"{c} ({proofs.get(c, 0)})" for c in sorted({h['class'] for h in s4} - {h['class'] for h in s5})))
out("")
out("| Klasse | Kandidaten | Beweise in decided |")
out("|---|---:|---:|")
for c, k in sorted(Counter(x[0] for x in cand).items(), key=lambda t: (-t[1], t[0])):
    out(f"| {c} | {k} | {proofs[c]} |")
out("")
out("`simulierte Schritte` = Feld `slugbird.simulated` (unveraendert uebernommen; leer, wenn nicht angegeben).")

(ROOT / "data" / "auswertung_holdouts.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
