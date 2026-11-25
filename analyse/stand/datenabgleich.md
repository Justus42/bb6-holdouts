# Datenabgleich 25.11.2026: holdouts.json neu geholt, busycoq und cryptids gelesen

Thread „Stand festhalten“, 25.11.2026. Nur Daten lesen und vergleichen, kein Rocq, nichts veröffentlicht.

## Ergebnis in Kürze

- **holdouts.json von denniskoshta.com ist unverändert.** Neu geholt (`data/holdouts_2026-11-25.json`), aber
  byte-gleich mit der Datei vom 10.11. (gleiche SHA-256, `generated_at` 2026-11-10). Aus ihr allein folgt
  also nichts Neues. Herkunft in `data/QUELLE.md`.
- **Deshalb busycoq direkt gelesen** (öffentliches Repo, nur `git fetch`, nichts geschrieben):
  - Zweig `BB6` steht weiter auf `33209bc7` (03.11.2026). **Seit dem Schnappschuss wurde nichts gemergt**, also
    ist in busycoq keine Holdout-Maschine neu gelöst.
  - Die PR-Köpfe 1 bis 61 sind unverändert. **Neu sind die PR-Refs 62 bis 119 (58 Stück)**, erstellt
    09.11. bis 25.11. In ihrem Inhalt stehen die Maschinen-Strings von **63 Holdouts**; 62 davon waren am 10.11.
    noch „open“, einer (38) hatte schon PR 61.
  - Ob ein PR offen, geschlossen oder abgelehnt ist, zeigt `git` nicht; das habe ich **nicht** geprüft
    (GitHub-API für fremde Repos ist in dieser Sitzung nicht freigegeben). „Steht im PR“ heißt auch nicht
    „wird dort bewiesen“; die Titel unten sagen, was der PR behauptet.
- **Betroffen von den neuen PRs: keine unserer Maschinen.** 396, 88, 312, 449, Gruppe 1 (114, 367, 378) und die
  M5-Gruppe (318, 518, 322, 274) kommen in keinem neuen PR vor, auch nicht umbenannt oder gespiegelt. 88, 312
  und 449 stehen weiter nur in PR #59 (Kopf `f23281d`, unverändert).
- **cryptids** (`google-deepmind/cryptids`, Commit `f01ee56`, 25.11.2026): keine Datei zu 396, 88, 449,
  Gruppe 1 oder M5. 312 hat dort eine formale Rückführung (`HasOdometerReduction`, „BMO Problem 10“), keine
  Entscheidung. Auffällig für 396: Holdout **587** (`1RB1LD_0RC0LF_1LD1RE_0LA0RB_0RD1RB_0LD---`) hat in cryptids
  eine bewiesene Beschleunigung mit demselben Wortgesetz wie 312, bei der laut Dateikopf `1011` **nicht** hält
  und `111` das einzige Haltemuster ist, also dieselbe Lage wie bei 396. Nur gelesen, nicht nachgeprüft; an den
  Thread „396, Teil 2“ weitergegeben.

## Wie geprüft

Bare-Klon von `https://github.com/ccz181078/busycoq` mit `refs/heads/BB6` und allen `refs/pull/*/head`
(119 Refs, Abruf 25.11.2026 ca. 19:55 UTC). Verglichen mit `busycoq.pr_snapshot` in `data/holdouts.json`.

| Programm | Verfahren |
|---|---|
| `pr_abgleich.py` (Programm 1, Python) | je neuem/geändertem PR alle hinzugefügten oder geänderten Dateien ab dem Merge-Base mit BB6 lesen, Maschinen-Strings per Regex, Abgleich mit `tm` und `aliases` |
| `pr_abgleich2.sh` (Programm 2, Bash/jq/grep, getrennt geschrieben) | nur die `+`-Zeilen von `git diff`, `grep -F` gegen alle Holdout-Strings; zusätzlich für die Zielmaschinen `git grep` über den **ganzen Baum** jedes PR-Kopfs, minus Treffer im BB6-Stand |
| `kanon_abgleich.py` | alle gefundenen Strings über die Normalform aus `karte_a.py` (Umbenennung + Spiegelung) gegen die Zielmaschinen und alle Holdouts |
| `cryptids_abgleich.py` | alle Dateien eines cryptids-Checkouts, Normalform wie oben |

- Programm 1 und 2: **zeilengleich** für alle 58 PRs (`ergebnis_programm1.txt`, `ergebnis_programm2.txt`), je
  63 verschiedene Holdouts.
- Kanonisch: 88 Strings in den neuen PRs, 86 gehören zu Holdouts, 2 (PR 65) zum BB(6)-Rekordhalter; kein
  Treffer für die Zielmaschinen.
- Negativkontrollen (`negativkontrollen.txt`): künstliche PR-Refs mit einem Alias von 396 und mit 396
  umbenannt+gespiegelt werden von allen drei Programmen gemeldet (der umbenannte Fall erwartungsgemäß nur von
  `kanon_abgleich.py`).

Aufrufe:
```
git init --bare bc && git -C bc fetch https://github.com/ccz181078/busycoq \
  "refs/heads/BB6:refs/heads/BB6" "+refs/pull/*/head:refs/pr/*"
python3 -I analyse/stand/pr_abgleich.py bc data/holdouts.json
bash analyse/stand/pr_abgleich2.sh bc data/holdouts.json
python3 -I analyse/stand/kanon_abgleich.py bc data/holdouts.json
git clone --depth 1 https://github.com/google-deepmind/cryptids cr
python3 -I analyse/stand/cryptids_abgleich.py cr data/holdouts.json
```

## Neue busycoq-PR-Refs 62 bis 119

Spalten: PR-Nummer, Kopf-Commit, Commit-Datum, Autor, Holdouts (n in der 608er-Liste), Betreff des
Kopf-Commits (nicht zwingend der PR-Titel). PR 108 hat denselben Kopf wie PR 98.

| PR | Kopf | Datum | Autor | Holdouts | Betreff |
|---|---|---|---|---|---|
| 62 | 02bef43a | 2026-11-09 | Dennis Koshta | 38 59 124 | Nonhalting for two more starts of the long translated cycler table |
| 63 | 265f4c43 | 2026-11-09 | Dennis Koshta | 38 131 | Translated cycler proof for 1RB0LA_1LC0RD_0LD1LA_1LF0RE_1LB1RE_1RD--- |
| 64 | 6fedfbeb | 2026-11-09 | Dennis Koshta | 293 | Halting proof for 1RB0RB_0LC1RA_1RD1LC_1LA1LE_1LF0LD_---0LA |
| 65 | f7f821f6 | 2026-11-09 | Dennis Koshta | - | Add SOBCv5_TimeBound: explicit lower bounds on the halting time and the number of ones of the BB(6) champion |
| 66 | d518d258 | 2026-11-10 | Dennis Koshta | 568 | Add Halt_1RB1LB_1RC0RD.v: 1RB1LB_1RC0RD_0LA1RE_0RF1LC_1LA0RB_---1LC halts |
| 67 | 1f98c7a2 | 2026-11-07 | Alex Havrilla | 56 445 | Add nonhalting proofs for BB(6) subtower twin holdouts #56 and #445 |
| 68 | 34748a33 | 2026-11-09 | Alex Havrilla | 221 | Prove 1RB1LF_1RC1RB_1RD0RB_0LE0LF_---1LD_0LE1LA nonhalting |
| 69 | f862617a | 2026-11-14 | Claude | 42 140 | Prove 1RB0LF_1LC0LA_1RA0RD_---1RE_1LA1RC_0LB0RC nonhalting (opaque-block certificate) |
| 70 | 5784ad83 | 2026-11-14 | Claude | 42 140 | Prove 1RB0RD_1RC0LF_1LA0LB_---1RE_1LB1RA_0LC0RA nonhalting (opaque-block certificate) |
| 71 | 625a3270 | 2026-11-14 | Claude | 236 | Prove 1RB0RC_0RC1RC_0LD0RA_1LE0LF_0LA1LC_---1LA nonhalting (verified symbolic executor) |
| 72 | c5d5cdb1 | 2026-11-14 | Claude | 123 223 | Prove 1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA0RE_1RE--- halts (visit law with two forms of visit) |
| 73 | 390b1258 | 2026-11-14 | Claude | 123 223 | Prove 1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA1RB_1RE--- halts (visit law with two forms of visit) |
| 74 | 272e2808 | 2026-11-15 | Claude | 125 | Prove 1RB0RC_1LA0LD_1RB0RD_1LE0RF_0LB0RB_1RC--- nonhalting (bouncer with a fixed far end) |
| 75 | edca3f4e | 2026-11-16 | Claude | 87 | Prove 1RB1LE_0LC1RE_---1LD_0RD1LA_0RF1RF_1RA0LB halts |
| 76 | 594cece3 | 2026-11-16 | Claude | 581 | Prove 1RB1RD_1RC1RB_1LD0RA_1RA0LE_1LF0LC_---1LE halts |
| 77 | 7e615fbe | 2026-11-16 | Claude | 117 405 | Eqv_TailWord: 1RB---_1LC0RF_1LD0LC_0RE0LF_0RD1LA_1RB0LE halts iff 1RB0RA_0LC0RF_0LB1RD_1LE---_1RA0LF_1LE0RC halts |
| 78 | 453cb4a0 | 2026-11-14 | Alex Havrilla | 104 | Prove 1RB0LD_1LC0RD_1LA0LC_1RE0LB_1RB1RF_0LD--- nonhalting |
| 79 | 391dcb97 | 2026-11-14 | Alex Havrilla | 58 | Add non-halting proof for BB(6) holdout 1RB0LC_1RC1RF_1LD0RA_1LE0LD_1RC0LA_0LA--- |
| 80 | a0b2af8f | 2026-11-15 | Alex Havrilla | 176 600 | Prove 1RB1RE_1LC0RA_1LA0LD_1LB0LF_0RB0LE_0LA--- and 1RB0RF_1RC0LD_1RD0RA_1LB1LE_0LB0RE_0RD--- do not halt |
| 81 | 06818bd2 | 2026-11-15 | Alex Havrilla | 566 | Prove 1RB---_1RC0LE_1RD1RF_1LB0LB_0RD0LD_0RC0RA halts |
| 82 | eb9728c4 | 2026-11-15 | Alex Havrilla | 244 279 | Prove 1RB0LE_1RC1RA_1LD0RE_1LA1LD_1LD0RF_0RA--- and 1RB0LC_1RC1RA_1LD0RE_1LA1LD_0RA1RF_0LC--- halt |
| 83 | 6a205cba | 2026-11-15 | Alex Havrilla | 220 | Prove 1RB1RE_0RC0RF_1LC1RD_1RA0LE_0RA0LD_0RA--- halts |
| 84 | 07ec3536 | 2026-11-15 | Alex Havrilla | 339 473 | Prove 1RB0LE_1RC1RB_1LD0RE_1LA1LC_1RB0LF_0LC--- and 1RB0LE_1RC1RB_1LD0RA_1LA1LC_0LC1LF_0RA--- halt |
| 85 | ccfbc839 | 2026-11-15 | Alex Havrilla | 390 | Prove 1RB0RA_0RC1LD_0LD0RE_1LB1LE_1RA0LF_0LC--- does not halt |
| 86 | 4f774cf9 | 2026-11-15 | Alex Havrilla | 428 | Prove 1RB0RE_1LC0RA_1RE1LD_0LB0LF_1RA1RA_0LD--- does not halt (#428) |
| 87 | afce978b | 2026-11-15 | Alex Havrilla | 44 | Prove 1RB0LF_1RC0RB_0RD1LE_0LE0RA_1LC1LA_0LD--- (#44 in 608) nonhalting |
| 88 | 26ca40a8 | 2026-11-15 | Alex Havrilla | 286 | Prove 1RB0RD_1RC0LF_0LA0RB_1RE---_1LB1RA_0LE0LF (#286 in 608) halts |
| 89 | 32445556 | 2026-11-15 | Alex Havrilla | 228 | Prove 1RB1RD_0LC0LB_0RE0LD_1LB0RB_1RF---_0RA0RC (#228 in 608) halts |
| 90 | b6aa8911 | 2026-11-16 | Alex Havrilla | 302 | Nonhalt of 1RB1LC_1LA0RD_1LA0LA_---1RE_1RB0RF_1RC0RA |
| 91 | c72cd7e6 | 2026-11-17 | Alex Havrilla | 5 | Prove 1RB1LD_1LC0RF_0RD0LB_1LB0LE_1LA---_0RA0RF halting |
| 92 | ad5d79bc | 2026-11-15 | Alex Havrilla | 121 | Prove non-halting for 1RB0RE_1LC0LB_1RD0LB_1RF0LA_1RC---_0RA0LD |
| 93 | aaa730e0 | 2026-11-15 | Alex Havrilla | 489 598 | Prove 1RB1RD_1LC0RE_1LD1LC_1RA0LE_1LC0RF_0RD--- and 1RB1RD_1LC0RE_1LD1LC_1RA0LB_0RD0RF_0RD--- halt (#489 and #598) |
| 94 | 42828dcd | 2026-11-17 | Alex Havrilla | 235 | Prove 1RB0RA_0RC0LE_1LC0LD_1RA1LF_---1LD_1LD1LB halting |
| 95 | 3812175c | 2026-11-16 | Alex Havrilla | 300 | Prove 1RB0RE_1LC1LF_1RA0LD_1LB1LA_1RB1RC_---0LA does not halt |
| 96 | 57150156 | 2026-11-17 | Alex Havrilla | 122 | Nonhalt of 1RB1LF_0LC0RE_1LA1RD_0LB1LB_1RC1RD_0LD--- |
| 97 | 81e92440 | 2026-11-18 | Alex Havrilla | 585 | Nonhalt of 1RB0LE_1RC0LB_1RD0RC_1LA1RC_---1LF_1LB1LD |
| 98 | b70e0449 | 2026-11-18 | Claude | 539 608 | Print Assumptions halt at the end of the file |
| 99 | bc0826af | 2026-11-18 | valu42 | 608 | Connect the published blank-tape halting theorem for BB(6) ID 181655 |
| 100 | cdbb2630 | 2026-11-18 | valu42 | 448 608 | Prove halting of BB(6) line 448 from the blank tape |
| 101 | 89a6fed8 | 2026-11-18 | valu42 | 448 608 | Prove halting of 1RB1RD_1LC0RE_1LD1LC_1RA0LB_0RD0RF_0LC--- |
| 102 | 51427c58 | 2026-11-18 | valu42 | 247 608 | Prove halting of 1RB0LE_1RC1RB_1LD0RA_1LA1LC_0LC0LF_0RB--- |
| 103 | fe5cd9c9 | 2026-11-19 | Alex Havrilla | 211 | Prove non-halting of 1RB1LF_0RC0RB_0LD1RB_1LE0LB_0LA1LC_0LB--- |
| 104 | fa58c7cb | 2026-11-19 | Alex Havrilla | 238 | Prove non-halting of 1RB1LC_1LA1RF_0RD1RD_0RA0LE_1LA0LE_0RC--- |
| 105 | 8b9d0b36 | 2026-11-19 | Alex Havrilla | 500 | Prove halting of 1RB1LE_1LC1RE_1LE1LD_1LC0LA_1RF0LA_---0RA |
| 106 | 1ac594f3 | 2026-11-19 | Alex Havrilla | 446 | Prove halting of 1RB0LD_0RC0LE_1RD1RA_0RE1RF_1LF0RC_0LA--- |
| 107 | 9f5dac21 | 2026-11-19 | Alex Havrilla | 137 | Prove non-halting of 1RB0LA_0RC0LE_0RD1RC_1LD1RE_1LA1RF_---0RB |
| 108 | b70e0449 | 2026-11-18 | Claude | 539 608 | Print Assumptions halt at the end of the file |
| 109 | 6dc49dfe | 2026-11-18 | Claude | 608 | Prove 1RB1RA_1LC0RD_1LD1LB_1LE0LF_0RA---_0LB0LE halts (PR 93's fast engine changed for T4, from start A, plus a detour lemma) |
| 110 | 50174332 | 2026-11-22 | Alex Havrilla | 259 578 | Prove 1RB0RA_1RC0RD_1RD0LC_1LE1RA_---1LF_1RB0LC and 1RB0LA_1LC1RF_---1LD_1RE0LA_1RA0RB_1RE0RF do not halt |
| 111 | 1e879210 | 2026-11-22 | Alex Havrilla | 273 | Prove 1RB0RC_1RC1LB_1LD1RA_1LE0LB_---1LF_0LF0LC halts |
| 112 | 5aa77717 | 2026-11-22 | Alex Havrilla | 119 | Prove 1RB0LC_0LA1RD_1LA0RE_1RE0RF_1LF---_1LB1RF does not halt |
| 113 | 5d1a6ae1 | 2026-11-24 | Alex Havrilla | 74 | Prove 1RB0RD_1LC0LE_0RA0LB_1RC1RF_1LB1RD_0RC--- does not halt |
| 114 | 7d210471 | 2026-11-25 | Alex Havrilla | 304 | Prove 1RB1LE_1RC1RF_0RD0LB_1LD0RA_0LA0LE_0RC--- does not halt |
| 115 | 39bcfcd9 | 2026-11-25 | Alex Havrilla | 437 | Prove 1RB0LF_1LC0LA_---1RD_1RF1RE_1LF1RD_1LB0RE does not halt |
| 116 | 8202418b | 2026-11-25 | Alex Havrilla | 380 | Prove 1RB1LD_1RC0LA_1LA0RE_1LB1LA_1RF0RB_---0LB does not halt |
| 117 | d7bb2311 | 2026-11-25 | Alex Havrilla | 521 | Prove 1RB0LC_1LC0RE_1RA1LD_1LA1LC_1RF0RA_---0LA does not halt |
| 118 | c2814b21 | 2026-11-25 | Alex Havrilla | 501 | Prove 1RB1RF_1LC0RF_1LE0LD_1RC0LB_---1RA_1LB1RA does not halt |
| 119 | 7154862a | 2026-11-25 | Alex Havrilla | 364 | Prove 1RB0LE_1LC1RD_1LA0RB_1RC1RB_1LF0LC_---0RC does not halt |

### Familien aus der Verwandtschaftskarte, die jetzt ganz in neuen PRs stehen

F1 {244, 279, 339, 473, 489, 598} (PR 82, 84, 93), F19 {247, 448, 539, 608}, F26 {38, 59, 124} (PR 62, 63),
F67 {364, 380, 521}, F70 {5, 286}, F77 {42, 140}, F78 {44, 390}, F80 {56, 445}, F81 {58, 104},
F92 {117, 405}, F93 {122, 238}, F107 {176, 600}, F117 {259, 578}, F138 {437, 501}; F99 nur 581 (133 nicht).
F12 {88, 312, 396, 449} und F20 (M5) sind nicht dabei. Gruppe 1 ebenfalls nicht.

## Grenzen

- PR-Zustand (offen/geschlossen) und Kommentare nicht gelesen; Lean-Beweise außerhalb von cryptids (laut
  Discord ein großer Teil der rund 70 wartenden Beweise) nicht erfasst. Ob jemand an 396 arbeitet, klärt nur
  Justus in #bb6.
- Nur Maschinen-Strings im Format `1RB0LB_…` werden gefunden. Ein PR, der eine Maschine nur über eine andere
  Schreibweise nennt, fiele durch.
