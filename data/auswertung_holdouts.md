# Auswertung data/holdouts.json

- Datei-SHA-256: `84e7b8ac2ca92dedeac98bb2bfd5f57dd5aefdef38ee4da302f9c36df2b66810` (= QUELLE.md)
- generated_at: 2026-11-10T00:00:02.365Z, Liste vom 2026-10-30 (608 Maschinen)
- busycoq.head.sha: `33209bc7dc282b38c8cd6be507bfc551fea56108` -> passt zum Pin `33209bc7`
- slugbird-Guide: November 3, 2026

## Abgleich mit data/BB6_holdouts_608.txt (offizielle Liste)

- Liste: SHA-256 `81b29741c6179b56e60123b672ac4b58149869af04271fb05b57f9421e4500a5` (= QUELLE.md), 608 Zeilen, CRLF: nein, Zeilen mit Leer-/Steuerzeichen: 0
- Zeilen, die nicht dem 6-Zustand-2-Symbol-Format entsprechen: keine
- Duplikate: Liste 0, holdouts.json 0
- Gleiche Menge: ja (nur in Liste: 0, nur in JSON: 0)
- n in JSON: 1..608 lueckenlos, aufsteigend
- Gleiche Reihenfolge (tm von n == Zeile n): ja
- Aliase in holdouts.json, die selbst in der Liste stehen: 0

## busycoq-Status gesamt

| Status | Anzahl |
|---|---:|
| open | 569 |
| pr_open | 38 |
| solved | 1 |
| **Summe** | **608** |

Zum Vergleich `counts.by_status` in der Datei: {"open": 562, "pr_open": 38, "sim_halt": 7, "solved": 1} (dort wird `sim_halt` getrennt gefuehrt; in den Eintraegen selbst stehen diese als `open`).

## je Klasse (Holdouts nach busycoq-Status, dazu Beweise aus `decided`)

`decided`: 846 Eintraege, davon by=proof 819, by=equivalence 27; 229 proof-Eintraege ohne Klasse.

| Klasse | open | pr_open | solved | Holdouts | Beweise in decided |
|---|---:|---:|---:|---:|---:|
| Shift-overflow counter | 81 | 11 | 0 | 92 | 286 |
| Skelet 1-like Class 1 | 85 | 1 | 0 | 86 | 18 |
| Unknown | 74 | 6 | 0 | 80 | 0 |
| Bell-like | 68 | 4 | 0 | 72 | 9 |
| Quadratic Mess | 46 | 1 | 0 | 47 | 10 |
| Cubic Mess | 42 | 2 | 0 | 44 | 13 |
| Chaotic Bell Class 3 | 20 | 2 | 0 | 22 | 0 |
| Shift-overflow bouncer counter | 22 | 0 | 0 | 22 | 20 |
| Bouncer + Chaotic Edge | 16 | 1 | 0 | 17 | 14 |
| Chaotic Bell Class 1 | 17 | 0 | 0 | 17 | 2 |
| Spaghetti | 17 | 0 | 0 | 17 | 2 |
| Chaotic 1dCA-like in bouncer | 13 | 0 | 0 | 13 | 3 |
| Bell eats counter | 5 | 6 | 0 | 11 | 33 |
| Structural counter + chaotic edge | 11 | 0 | 0 | 11 | 6 |
| Chaotic 1dCA-like in bell | 9 | 0 | 0 | 9 | 0 |
| Shift-overflow structural counter | 9 | 0 | 0 | 9 | 12 |
| Chaotic Ack-like Bell | 7 | 1 | 0 | 8 | 4 |
| Chaotic Bell Class 2 | 7 | 0 | 0 | 7 | 8 |
| Monotone list | 6 | 0 | 0 | 6 | 14 |
| Chaotic Fractal Type 1 | 4 | 0 | 0 | 4 | 18 |
| Counter Class 2 | 3 | 0 | 0 | 3 | 4 |
| Counter Class 3 | 0 | 3 | 0 | 3 | 4 |
| Translated Counter | 3 | 0 | 0 | 3 | 3 |
| Skelet 1-like Class 2 | 2 | 0 | 0 | 2 | 13 |
| Chaotic Fractal Others | 1 | 0 | 0 | 1 | 9 |
| Fractal in Bouncer | 0 | 0 | 1 | 1 | 8 |
| Sync bouncer counter | 1 | 0 | 0 | 1 | 13 |

## Kandidaten (data/kandidaten.csv)

| Filterstufe | verbleibend |
|---|---:|
| busycoq open | 569 |
| + keine PR (auch keine erwaehnende/geschlossene) | 556 |
| + slugbird-Status rules | 91 |
| + keine Tags | 90 |
| + Klasse mit >= 5 Beweisen in decided | 75 |

Ausgeschlossen in der letzten Stufe (Klasse, Beweise in decided): Counter Class 2 (4), Unknown (0)

| Klasse | Kandidaten | Beweise in decided |
|---|---:|---:|
| Shift-overflow counter | 37 | 286 |
| Quadratic Mess | 11 | 10 |
| Bell-like | 10 | 9 |
| Shift-overflow structural counter | 6 | 12 |
| Monotone list | 5 | 14 |
| Structural counter + chaotic edge | 4 | 6 |
| Shift-overflow bouncer counter | 1 | 20 |
| Skelet 1-like Class 1 | 1 | 18 |

`simulierte Schritte` = Feld `slugbird.simulated` (unveraendert uebernommen; leer, wenn nicht angegeben).
