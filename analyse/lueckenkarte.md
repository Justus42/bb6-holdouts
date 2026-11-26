# Lückenkarte M5 und Gruppe 1 (nur lesen)

Thread „Lückenkarte für M5 und Gruppe 1“, 26.11.2026. Auftrag der Prüfstelle (über Justus, Nachrichten 13:10,
14:15, 15:20, 15:35). Nur gelesen; einzige Rechnung ist der kurze lokale Quick_Sim-Test (Abschnitt 6). Kein Rocq,
nichts in fremden Repos, kein Discord. Ergebnis geht an die Prüfstelle, **bevor** gerechnet wird.

## Ergebnis in drei Sätzen

1. Von bbes acht Vorschlägen A bis H ist für M5 und Gruppe 1 **keiner gezielt angewandt**; M5 lief nur im
   allgemeinen Sieb von C (Sweep-Carries) mit, ohne Abschluss, und bbe führt beide Gruppen im „Rest ohne
   gemeinsame Technik“ (F01 bzw. F07).
2. Die Leitfrage „M5-Umbau als Reset mit einer Bedingung, die jeder Umbau wieder erfüllt“ lässt sich
   **stellen, aber mit unseren Daten nicht beantworten**: In den Skelet-Beweisen ist der Reset eine Abbildung
   auf zwei Zahlen mit einer Rechenbedingung, bei M5 eine Abbildung auf Ziffernlisten (10 + 1 → 19 + 10 Bausteine),
   von der nur drei natürliche Beispiele bekannt sind und deren Ziffernlage keiner Formel folgt.
3. Quick_Sim beweist auf 318 und 322 in 150 s **keine einzige Regel**; mit Blockgröße 8 läuft es als schneller
   Simulator bis rund 10^11,5 Schritte und damit durch alle drei bekannten Umbauten hindurch, aber nicht per
   Regel. Drei eigene Ideen stehen in Abschnitt 7; die stärkste ist, die Umbau-Abbildung an **künstlichen
   Startbändern** zu messen statt an den drei natürlichen.

## 0. Pflichtprüfung je Maschine (CLAUDE.md, 26.11., nur gelesen)

Maschinen: Gruppe 1 = 114, 367, 378; M5 = 274, 318, 322, 518. Gesucht wurden die 7 Strings und die 5
gleichwertigen Strings aus `data/holdouts.json` (`aliases`), je mit `---` und `HHH`.

**busycoq** (`git fetch` wie in CLAUDE.md, Stand 26.11. 14:10 UTC):
- BB6 steht auf `9c078ca` (= unser Pin). Treffer nur in `verify/Eqv_v2.v` (Gleichwertigkeitsbeweise der
  aliases zu 114, 274, 318, 322), keine Entscheidung. Bekannt aus PR 36.
- Offene PRs: `git ls-remote … 'refs/pull/*/merge'` zeigt **53** (Untergrenze, offene PRs mit Konflikt fehlen).
  Vergleich `git diff o/BB6 refs/prm/N`, nur hinzugefügte Zeilen: **kein Treffer**.
- Zusätzlich alle 120 PR-Köpfe (`o/BB6...refs/pr/N`, auch geschlossene) mit denselben Strings plus 31 und 222:
  **kein Treffer**.
- Kontrolle schlägt an: der String von 581 wird in PR 76 gefunden, in beiden Verfahren (4 bzw. 1 Zeile).
- Ein Programm (Shell/grep); deckt sich mit dem Stand der Prüfstelle (14 Strings, kein Treffer).

**busy-beaver-explorer (bbe)**, Kopf `c70be037` (26.11., 13:52 UTC). Ordner `holdouts/<Maschine>/`:

| Maschine | letzte Änderung | Stand laut README/status.json |
|---|---|---|
| 318 | 13.11. | „Open“; Zählerdurchläufe gegen Simulator bis 10^8 geprüft; 10 Besuche am linken Ende (letzter 29.787.121), keiner bis 2·10^10 |
| 518 | 13.11. | „Open“; Durchläufe und Wende rechts in Lean (Kern); linker Zähler nur beobachtet; 10^11 ohne Halt |
| 322 | 13.11. | „Open“; zwei Sweeps und Haltebedingung in Lean; 10^11 ohne Halt |
| 274 | 24.11. | „Open“; Rückwärtssuche bis Tiefe 20.000 erfolglos (Nachlauf 24.11.); CTL K=3..6, n-Gramm 3..7, Invariante mod 2..12: nichts; 10^9 |
| 114 | 18.11. | „Open“; sechs Umkodierregeln in Lean; Beschleuniger `rleaccel.cpp` bis 1,29·10^10 (das ist die Änderung vom 18.11.) |
| 367, 378 | 13.11. | „Open“; Umkodierregeln in Lean; `rsim` 1,4·10^9 |

Keine neue Grenze und kein neuer Ansatz von bbe zu unseren Maschinen seit unserem Abgleich (PR 28/36).

**`data/holdouts.json`** (Schnappschuss 10.11.), Felder `slugbird` / `sheet` / `notes`:

| n | slugbird Status | slugbird simuliert | Sheet ≥ 10^ | notes |
|---|---|---|---|---|
| 114 | rules | 1,6·10^14 | 14 | leer |
| 367, 378 | rules | 2,0·10^14 | 14 | leer |
| 274, 322, 518 | rules | 1,0·10^17 | 15 | leer |
| 318 | rules | 1,0·10^20 | 15 | leer |

Gegenüber unseren Grenzen (Gruppe 1: lückenlos 10^12, bedingt 10^24/10^25; M5: 8·10^14) ist hier nichts neu.
Die `slugbird`-Felder in `holdouts.json` stimmen für alle 607 Maschinen des Guides **exakt** mit Status und
Simulationstiefe im Guide überein (eigener Vergleich, ein Programm). Der Guide bringt also nur die Textnotizen neu.

## 1. Quellen und was nicht lesbar war

| Quelle | gelesen? |
|---|---|
| bbe `holdouts/recent-proofs/technique-survey-nov26.md` (Commit `cd4594d5`, Nachtrag `439123ce`) und `followup/lap-carry-transducers.md`, `FAMILIES.md`, Maschinenordner | ja |
| slugbirds Holdout-Guide, `claude.ai/artifact/8B8E5ms18otN4XHbEnxaP2` | ja (Freigabe beim Abruf erteilt). Im Seitencode `ASOF = "November 3, 2026"`. Fußzeile: „This page and its notes were written by AI agents (Claude) working on the holdouts … — Claude (Heron)“. **Inhalt also KI-geschrieben, nicht geprüft.** Auszug: `analyse/lueckenkarte/guide_auszug.tsv` |
| Wiki `wiki.bbchallenge.org/wiki/Shift_overflow_counter` | ja (Stub, Stand 21.2.2026) |
| `sligocki.com/2023/02/05/shift-overflow.html` (Reset-Invariante) | **nein: Proxy sperrt sligocki.com (HTTP 403).** Nicht umgangen. |
| Forum-Beiträge zu Skelet 15/26/33/34/35 (`discuss.bbchallenge.org`) | **nein: Host nicht erreichbar.** Nicht umgangen. |
| Skelet-Beweise selbst | als Rocq-Dateien in busycoq (`verify/Skelet15.v`, `26`, `33`, `34`, `35`, Zweig BB6) gelesen. Das ist unsere reguläre Quelle, kein Spiegel des Forums; `Skelet34.v` sagt selbst „Following sligocki.com/2023/02/02/skelet-34.html“. Ob das als Ersatz für die Forum-Links zählt, entscheidet die Prüfstelle. |
| `github.com/Laturas/shift_overflow_subset_decider` (Kopf `b4c1c6f`, 2.6.2025) | ja |
| `github.com/sligocki/busy-beaver` (Kopf `4359559`, 26.11.) | ja, für Quick_Sim |

Wenn die Prüfstelle die beiden gesperrten Seiten braucht: Freigabe im Netzwerk der Umgebung „Mathe“ nötig.

## 2. bbes Verfahren A bis H gegen M5 und Gruppe 1

bbe ordnet unsere Maschinen so ein (`FAMILIES.md`, 21.11.): M5 = Familie **F01** „Periodic blocks driven by a bounded
engine (rest)“, Gruppe 1 = **F07** „Chaotic bells over block lists (rest)“, beide im Abschnitt „No technique shared
by several of these is in sight“. Community-Klasse: M5 „Shift-overflow structural counter“, Gruppe 1 „Monotone list“.
Tabellen-Nachbarn (Abstand ≤ 1) haben beide nur innerhalb der Gruppe (bbe-Tabellenmengen T59, T86, T25).

| bbe | Idee in einem Satz | M5 (274, 318, 322, 518) | Gruppe 1 (114, 367, 378) |
|---|---|---|---|
| **A** Horn-Löser | Zählerprogramm aus bewiesenen Regeln an Z3/Eldarica geben, Invariante suchen | **nicht versucht.** Es gibt kein Zählerprogramm: Umbau ohne Regel. Laut bbe-Nachtrag 26.11. fand A auch sonst nichts | **nicht versucht.** Unser Phasen-Automat (7 Regeln) wäre so ein Programm, aber nur empirisch [VB], [INV] |
| **B** Zusammenfassungen mit abstraktem Schwanz | Ausflüge als Verträge „aus Kontext X kommt Form Y zurück“, Zahlen abstrahiert | nicht versucht, nicht als Ziel genannt | nicht versucht, nicht als Ziel genannt |
| **C** Sweep-Carries als Wandler | Kreuzungsfolgen je Durchlauf als endlicher Wandler, dann Abschluss prüfen | **im Sieb:** alle vier mit „each-return“-Runden endlich (144 bis 472 Carries, `lap-carry-screen.tsv`), nicht mit vollen Durchläufen. bbes Abschlussprüfung über alle sättigenden Fälle schloss für **keine** Maschine; ein Einzelergebnis für M5 ist nicht veröffentlicht | nicht im Sieb (keine sättigenden Carries) |
| **D** Invarianten übertragen | nicht mehr benutzte Übergänge; Einweg-Simulation zu bewiesenen Nachbarn | gelaufen (`invariant-transfer.md`, 26.11.): nichts, nur je 1 Nachbar ohne Wiedervereinigung (schon in STATUS) | gelaufen: nichts (378: 7, 367: 6, 114: 4 Nachbarn) |
| **E** Halte-Wiederholung in Segmenten | Halt weit weg in Stücken nachrechnen | passt nicht (kein Halt in Sicht) | passt nicht |
| **F** automatische Folge | regelmäßige Seite = Zähler, dessen Ereignisfolge einen endlichen „wilden Rand“ treibt; per Produktautomat entscheidbar | **nicht versucht, aber M5 hat genau diese Gestalt** (Binärzähler rechts, unregelmäßiger Rest links). Voraussetzung (Rand endlich bei gegebener Folge) ungeprüft | teilweise ähnlich (Liste + linkes Ende), nicht versucht |
| **G** Restklassen-Mengen | geschlossene Restklassenmenge für eine geschlossene Abbildung | passt nicht (keine geschlossene Abbildung) | passt nicht |
| **H** hierarchische Invarianten | Grammatik „Ebene k aus Kopien von Ebene k−1“ | nicht versucht; nach einem Umbau stehen Zähler in Abschnitten zwischen neuen `W` (Ebenen-artig), unbelegt | nicht versucht |

Aus bbes Liste „What has failed“ betrifft uns: reguläre Sprachen auf Zellen (CTL, n-Gramm; für 274 und Gruppe 1
ausdrücklich gescheitert, bei uns ebenso [INV]); Rückwärtssuche (274, bis Tiefe 20.000). **Schablonen-Verpflanzung:**
`busycoq_templates.json` hat für keine unserer 7 Maschinen einen Eintrag, d. h. bbe hat dort keine busycoq-Vorlage
angesetzt.

**Was bbe bei M5 selbst als nächsten Schritt nennt** (318, „For later“): den Durchlauf als exakten Wandler herleiten
„including the groups 2.3, 3.5, 2.6, 6.8“; „a nonhalting proof then needs a description of all tapes that the
rebuilds can produce“. Gemacht hat bbe das nicht. **Bei Gruppe 1** (114): ganzen Zyklus als Regel, linkes Ende als
Abbildung, dann Invariante („Looks tractable“). Nicht gemacht; wir sind dort weiter (Stufe 1, Regel F in Rocq).

## 3. slugbirds Guide (Stand 3.11., KI-geschrieben)

Statusbedeutung laut Seite: **rules** = „The exact behaviour is written down, often proved in Rocq, but nothing yet
rules out a halt“; **pattern** = „Experiments show a pattern, but no exact rules yet“.

**Unsere Maschinen** (wörtlich):
- 318, 518: „Same mechanism as a wide structural counter: an exact binary counter on a periodic background.“
- 274, 322: „An exact binary counter of drifting atoms on a period-8 background. Overflows rebuild the far end.“
- 114, 367, 378: „One table, three starts: a monotone list. It can only halt from certain left-end words, and none
  matches a real state so far.“

**Klassengeschwister:**
- Shift-overflow structural counter (9 Maschinen = 31, 87, 130, 222, 457 und unsere vier):
  31, 222 „One table, two starts. Law proved in Rocq, plus a terminal regime: tapes of one specific form never halt.
  Open question: does the real run from blank reach that form?“ (rules, 10^17).
  87, 130, 457 „Nested shift-overflow counters on 2-cell units with base-4 levels. The first overflow freezes the
  old tape.“ (pattern, 10^17). Auffällig: M5 hat ebenfalls 4-phasige Ziffern und liest sich in 2-Zellen-Symbolen
  (bbe: `01`, `11`); ob das mehr als ein Anklang ist, ist **unbelegt** (bbe: keine Tabellen-Nachbarschaft).
- Monotone list (6 = 114, 367, 378, 141, 315, 388): 141, 315 „One table, two starts: a three-level list written at
  one end and read at the other“ (rules, 4·10^15); 388 „A monotone list whose frozen region is a non-regular
  counter“ (pattern).

**Beweisform 31/222 und 2-Zellen-Familie.** Der Guide sagt nur je einen Satz; die genannten Rocq-Gesetze liegen
**weder in BB6 noch in einem der 120 PR-Köpfe** (Suche nach 31, 222, 231, 246, Kontrolle s. o.). Lesbar ist also nur
die Form:
- 31/222: (i) Gesetz der Zählphase in Rocq, (ii) eine Bandform F mit Satz „aus F kein Halt“, (iii) offen: erreicht
  der Lauf F.
- 2-Zellen-Familie (231, 246, 265, 352, 407, 466, 493, 529): lokale Regeln in Rocq; der Zustand vor dem Halt wird
  **nur bei Überläufen** betreten. Damit reduziert sich die Frage auf die Überläufe.

**Familien, die an EINER fehlenden Aussage hängen** (nur aufgelistet, slugbirds laufende Arbeit; Stichwortsuche in
den Notizen, ein Programm, kann unvollständig sein):

| fehlende Aussage (Guide) | Maschinen (n) |
|---|---|
| „bound on a cascade of carries“ (Trenner verdreifachen, bedingte Rocq-Beweise vorhanden) | 8, 9, 34, 43, 82, 107, 164, 225, 226, 230, 242, 425, 488, 517 (14) |
| Halt-Zustand nur bei Überläufen, „No proof“ (2-Zellen-Binärzähler) | 231, 246, 265, 352, 407, 466, 493, 529 (8) |
| „about 4 parity walls at once and runs show at most 2, but that bound is not proved“ | 30, 73, 169, 354 (4) |
| erreicht der Lauf die Endform? (31/222, s. o.) | 31, 222 |
| jeder Zustand kehrt zurück? (3/2-Abbildung mit Ereignismodell) | 344, 475, 579 |
| Invariante braucht lineare Schranke | 176, 600 |
| Zahl = exakte Zweierpotenz, aus selbst geschriebener Warteschlange | 196, 404 |
| kleine Blockgruppe mit falschem Übertrag | 376, 519 |
| Restklassen-Kandidat hält auf Läufen, schließt aber nicht | 152, 324 |
| Halt braucht einen Fall, den echte Übergänge meiden | 12, 440 |
| Einzelne: Treffer einer kleinen Zielmenge (58); Größenschranke nicht induktiv (74); Zufall beim Überlauf (551) | 58, 74, 551 |

Keine dieser Familien enthält eine unserer Maschinen.

## 4. Pflichtlektüre: was dort über Reset und Beweisform steht

**Wiki „Shift overflow counter“** (Stub): Ziffern als kurze feste Blöcke; Doppelzähler, bis eine Seite überläuft und
die Blockversätze ungültig werden; danach „Reset Phase where the contents are 'reparsed', creating a new double
counter configuration. The new configuration could lead to halting.“ Keine Formel, kein Beweisverfahren; Beispiele
Skelet 15, 26, 33, 34, 35 und fünf haltende Maschinen.

**Skelet-Beweise in busycoq** (gemeinsame Bibliothek `ShiftOverflow.v`, `ShiftOverflowBins.v`). Alle haben dieselbe
Form:
1. Zählphase `D n m`: links Zahl n, rechts Binärzahl m (Bitblöcke); `D_run`: n und m zählen gemeinsam hoch, bis m
   voll ist (`all1 m`).
2. Überlauf `start_reset`: `D n m -->* E (n+1) …`.
3. Reset-Schritt `step_reset`: `E n m -->* E n' m'` mit **n' < n** und einer Bedingung, die erhalten bleibt;
   Induktion über n (`do_reset`) führt zurück nach `D 0 m'` bzw. `E 1 m'`.
4. Schluss mit `progress_nonhalt_cond`: eine Bedingung auf m, die jede Runde wiederherstellt.

Die Bedingungen sind **Rechenbedingungen auf zwei Zahlen**:
- Skelet 34/35: `n <= b m` (b m = Zahl der Zählschritte, bis m nur noch aus Einsen besteht, also Abstand zum
  nächsten Überlauf; `ShiftOverflowBins.v`).
- Skelet 26: `m >= 2` und `b m + 1 = 2^k + 2^(k+1)·n'` mit `n' >= 2`.
- Skelet 33: n beginnt binär mit `11` (`leads'`) und `b m = 3·2^q + r` mit `2n <= r < 2^q`.
- **Skelet 15 = Skelet 26 mit anderem Startzustand:** Der Beweis benennt die Zustände um (`Perm`), läuft endlich
  viele Schritte bis zu einer Konfiguration `Skelet26.D 0 0 1` und benutzt dann den **allgemeinen** Satz
  `Skelet26.D0_nonhalt` (gilt für jedes m). Das ist genau unsere Lage „eine Tabelle, mehrere Starts“.

**Laturas-Decider:** beweist **Halten** einer Teilklasse (Binärzähler plus Unärzähler, Halt nach Restklasse mod 3);
alle 15 Eingaben halten. Für M5 passt die Form nicht (kein Unärzähler, kein Halt in Sicht). Übertragbar ist aber
der Arbeitsschritt: Die **Reset-Übergänge werden an künstlich gebauten Bändern** (50 Binärziffern, gewählte Unärzahl)
ausgemessen, nicht am natürlichen Lauf.

## 5. Antworten auf die beiden Fragen der Prüfstelle

**(a) Lässt sich der M5-Umbau als Reset mit einer Bedingung schreiben, die jeder Umbau wieder erfüllt?**
Als Gerüst ja, mit Inhalt nein, nicht mit unseren Daten.
- In den Skelet-Beweisen ist der Reset eine Abbildung auf **zwei Zahlen**, schrittweise mit n' < n. Bei M5 ist der
  Umbau eine Abbildung auf **Ziffernlisten**: 10 Ziffern + 1 `W` → 19 + 10 (ab A, 2,98·10^7), 4 + 0 → 11 + 5 und
  12 + 5 → 23 + 15 (ab C) [M2 §3]. Die neuen `W` folgen einer Regel (feste Versätze an alten Ziffern), Lage und
  Phase der neuen Ziffern **keiner** gefundenen Formel [M2 §4].
- Eine Bedingung „jeder Umbau stellt sie wieder her“ muss also über Listen gehen. Vorbilder dafür im Pin:
  `SBCv6a2.v` (Umbau als Listenabbildung `transform`, Bahn geschlossen) und `SOBLv3.v` (Restklassen-Invariante über
  Listen) [M2 §5]. Beide brauchen die exakte Abbildung, die fehlt.
- Ein Hinweis aus beiden Läufen: Der Rest `11111111101011111111111010111111101010111111111110` (50 Zellen), aus dem
  ab C der Umbau bei 874.896.314 startete, steht im Lauf ab A seit 5,75·10^14 [M2 §2]. Ein Reset-Schema müsste
  also mindestens diesen Rest abdecken; dass er in beiden Läufen vorkommt, spricht für eine kleine Zahl von
  Rest-Formen. **Unbelegt.**

**(b) Lässt sich für M5 die Form von 31/222 bzw. der 2-Zellen-Familie aufstellen (Halt nur beim Umbau)?**
- **2-Zellen-Form („Halt nur bei Überläufen“): plausibel, nicht gezeigt.** In den Zählzyklen sehen B und C nur
  Umgebungen mit 0 rechts (Teil 1: 7 bzw. 9 Umgebungen), und bis 8·10^14 kommt kein Haltemuster vor, jeder Übergang
  gezählt [M1], [M3]. Die Zusatzumgebungen lagen am linken Rand. Als Satz bräuchte das: Zählzyklus und Wanddurchgang
  als Regeln für alle Ziffernlisten (bbe hat für 518 die Durchläufe schon in Lean). Dann bliebe genau Umbau und
  linker Rand übrig.
- **31/222-Form („Endform F, aus F kein Halt“): passt schlecht.** Ein Binärzähler mit endlich vielen Ziffern läuft
  zwangsläufig über; eine Endform ohne weiteren Umbau gibt es nur, wenn der linke Rest dauerhaft neue Ziffern
  nachliefert. Gerade der eine Rest, den beide Läufe teilen, hat ab C einen großen Umbau ausgelöst. Eine Endform
  müsste also den Umbau selbst enthalten, d. h. sie wäre eine Reset-Bedingung wie in (a).
- Fazit: Beide Formen führen bei M5 auf dieselbe Lücke, die Umbau-Abbildung.

## 6. Quick_Sim auf 318 und 322 (lokal, kurz)

Vorher geprüft: bbe hat Quick_Sim (Commit `cc35611`, `-r`, 2-Minuten-Sieb) auf viele Holdouts angewandt und nur
Läufe eingetragen, die die bekannte Tiefe um das Zehnfache übertreffen (`accel_runs.json`, Commit `fd81af04`). Für
M5 gibt es **keinen Eintrag** und nirgends eine Notiz; der Guide nennt Quick_Sim nicht. In unserem Repo: nichts.

Aufruf (Kopf `4359559`, Programm unverändert, je 150 s, Ausgaben gekürzt in `analyse/lueckenkarte/quick_sim/`):
`python3 Code/Quick_Sim.py --rules [-n 8] <Maschine>`

| Lauf | Blockgröße | Schritte nach 150 s | bewiesene Regeln | Bandbreite |
|---|---|---|---|---|
| 318 (= M5 ab A) | 2 (selbst gewählt) | 2,09·10^6 | 0 | 2.400 |
| 322 (= M5 ab C) | 2 (selbst gewählt) | 2,05·10^6 | 0 | 2.454 |
| 318 | 8 (vorgegeben) | ≈ 10^11,5 | 0 | 892.456 |
| 322 | 8 (vorgegeben) | ≈ 10^11,1 | 0 | 580.888 |

- **Regeln:** keine, auch keine Zählregel. Der Prover findet keine wiederkehrende Bandgestalt, weil jeder Durchlauf
  über den ganzen Zähler geht und dessen Ziffern sich jedes Mal anders ändern.
- **Über einen Umbau?** Mit Blockgröße 8 ja, aber nur als schneller Simulator (Ketten-Schritte über gleiche Blöcke):
  10^11,5 bzw. 10^11,1 liegen hinter allen drei bekannten Umbauten (2,98·10^7; 8,75·10^8). Ein Umbau wird nicht
  als Regel erfasst.
- Plausibilität: Die Bandbreite passt zum Wurzelwachstum unserer Läufe (52.296 Zellen bei 10^9 ab A, also rund
  9·10^5 bei 3·10^11). Am Ende des 318-Laufs zeigt Quick_Sim die Zählerfolge `01111101^6952 … 10100100^14043
  10010010^27682`: Abstände verdoppeln sich wie in [M1]. Schrittzahlen von Quick_Sim nicht gegen unsere Programme
  abgeglichen (kein Ziel; Schrittrekord nicht gesucht).
- Folge: Quick_Sim hilft bei M5 nicht über einen Umbau hinweg. Nichts entschieden.

## 7. Eigene Ideen (je ein Satz, geprüft gegen bbes Technik-Übersicht)

1. **Umbau-Abbildung an künstlichen Bändern messen (M5).** Idee: M5 auf selbst gebaute Zählerbänder setzen (alle
   Ziffern in D2/D3, gewählte Abstände, `W`-Lagen und einer der bekannten Reste), den Umbau laufen lassen und so
   hunderte Paare „Liste vorher → Liste nachher“ statt drei sammeln, um f zu finden oder zu widerlegen. Warum bbe
   das nicht hat: bbe kennt nur die natürlichen Läufe (10 Besuche am linken Ende, letzter 2,98·10^7) und nennt die
   Beschreibung aller Umbau-Ergebnisse nur als offenen Punkt; in A bis H kommt Messen an künstlichen Eingaben nicht
   vor (Laturas macht es für seine Teilklasse). Kosten: Umbau dauert ≈ 0,1·Breite², bei Breiten 10^3 bis 10^4 je
   höchstens 10^7 Schritte, lokal. **Rechnen, also erst nach OK.**
2. **Ein Beweis für vier Holdouts über eine Bandsprache auf Bausteinebene (M5).** Idee: eine Menge S von Bändern aus
   M5-Bausteinen (Ziffern Z/D1–D3 mit beliebigen Lücken `U^n`, `W`, endlich viele Rest-Formen) zeigen, die Zählzyklus,
   Wanddurchgang und Umbau nie verlassen und in der `B> 1 1`/`C> 1 1` nicht vorkommt; dann reicht wie bei Skelet 15
   → 26 je ein endlicher Vorlauf ab A und ab C, und 274, 318, 322, 518 fallen zusammen, **ohne** dass die genaue Lage
   der neuen Ziffern bekannt sein muss. Warum bbe das nicht hat: bbe kennt M5 nicht als gemeinsame Maschine
   (`Twin.lean` gilt nur bis zum ersten Bruch); bbes C arbeitet auf Zellfenstern (k ≤ 24) und schloss für keine
   Maschine, gescheiterte CTL arbeitete auf rohen Zellen; hier ist das Alphabet M5s Bausteine mit unbeschränkten
   Exponenten. Risiko: Ob die Rest-Formen endlich sind, ist offen [M2 §2]; Wanddurchgänge lassen Phasen springen.
3. **Linkes Ende von Gruppe 1 als endliche Ereignismenge über alle drei Starts.** Idee: die Übergänge der
   Linksende-Wörter (bei uns 13 Kernmuster [LE]) aus allen drei Läufen plus künstlichen Startwörtern sammeln und
   prüfen, ob sie eine geschlossene endliche Menge bilden, die kein Haltewort erreicht (bbes Form N5, „closed finite
   set of round-end classes“; der Guide sagt ebenfalls „can only halt from certain left-end words“). Warum bbe das
   nicht hat: bbe hat N5 nur an anderen Maschinen benutzt und bei 114 das linke Ende nur als „For later“ notiert.
   Risiko: Das 13. Muster kam erst bei 8,2·10^16 und der „alt“-Anteil steigt [LE §4]; die Menge ist vielleicht nicht
   endlich. Gruppe 1 ruht (Justus), daher nur gelistet.

Regel je Maschine (CLAUDE.md): Bei keiner der drei Ideen ist bbe oder busycoq mit demselben Ansatz gleich weit oder
weiter (Belege Abschnitte 0 und 2). Idee 2 ist bbes C verwandt; der Unterschied (Bausteine statt Zellfenster) ist
oben benannt. Vor einem Start ist zu entscheiden, ob die Prüfstelle Idee 2 als neuen Ansatz oder als C ansieht.

## Abweichungen und eigene Fehler

- Die Reset-Invariante bei sligocki und die Forum-Beiträge konnte ich **nicht lesen** (gesperrt bzw. nicht
  erreichbar); statt der Forum-Links habe ich die Skelet-Dateien in busycoq gelesen. Gemeldet, nicht umgangen.
- Der erste Abruf des Guides scheiterte an der fehlenden Freigabe für fremde Artifacts; beim zweiten wurde gefragt
  und freigegeben. Die Notizen stehen im Seitencode als Datentabelle; ich habe sie selbst ausgelesen.
- Familienliste in Abschnitt 3 per Stichwortsuche, ein Programm; Vollständigkeit nicht belegt.
- Quick_Sim lief auf dem aktuellen Kopf `4359559`, nicht auf bbes `cc35611`.
- Bei der Suche über alle PR-Köpfe hatte mein erster Befehl einen Tippfehler (grep-Fehler, keine Suche); der zweite
  Lauf mit Musterdatei ist der gültige, mit Kontrolle.

## Offene Punkte

- Freigabe der Hosts sligocki.com und discuss.bbchallenge.org, falls die Prüfstelle die Originale braucht.
- Ob 87/130/457 („2-cell units with base-4 levels“) mit M5 mehr als den Namen teilen: nicht geprüft (wäre ein
  Tabellen- und Bandvergleich, also Rechnen).
- Ob bbes Abschlussprüfung C für M5 tatsächlich lief und woran sie scheiterte: dort nicht veröffentlicht.

## Empfehlung

Weiter mit **M5, Idee 1** (Umbau an künstlichen Bändern messen), lokal und kurz, sobald die Prüfstelle das freigibt;
sie liefert die Daten, ohne die weder (a) noch Idee 2 beantwortbar sind. Quick_Sim nicht weiter verfolgen.
Gruppe 1 weiter ruhen lassen.

## Nachprüfen

```bash
# busycoq (nur lesen)
git fetch https://github.com/ccz181078/busycoq "+refs/heads/BB6:refs/remotes/o/BB6" "+refs/pull/*/head:refs/pr/*" "+refs/pull/*/merge:refs/prm/*"
git ls-remote https://github.com/ccz181078/busycoq 'refs/pull/*/merge' | wc -l        # 53 am 26.11.
for r in $(git for-each-ref --format='%(refname)' refs/prm/); do git diff o/BB6 $r | grep '^+' | grep -F -f muster.txt; done
# Quick_Sim (github.com/sligocki/busy-beaver, Kopf 4359559), je 150 s
timeout 150 python3 Code/Quick_Sim.py --rules -n 8 1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC
timeout 150 python3 Code/Quick_Sim.py --rules -n 8 1RB1RF_1LC0LF_1RD0LB_0RA1RE_1RD---_0RC0LA
```

Kürzel: [M1] `318_518.md`, [M2] `318_518_teil2.md`, [M3] `318_518_teil3.md`, [LE] `gruppe1_linkes_ende.md`,
[VB] `gruppe1_verboten.md`, [INV] `gruppe1_invariante.md` / `invarianten.md`.
