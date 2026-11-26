# Abgleich mit busy-beaver-explorer

Thread „Abgleich mit busy-beaver-explorer“, 26.11.2026, 1 Block, nur lesen. Kein Rocq, nichts in fremden Repos
geschrieben.

Gelesen per `git clone` / `git fetch` (öffentlich, nur lesen):

- **bbe** = `github.com/fractal-geometry-explorer/busy-beaver-explorer`, Kopf `662e215` (26.11., 04:32 UTC).
  Je Holdout ein Ordner `holdouts/<Maschine>/` mit `README.md`, `status.json` (Belegstufen) und Lean-Dateien.
- **busycoq** = `ccz181078/busycoq`, Zweig BB6 jetzt auf **`9c078ca`** (26.11., 00:34 UTC), PR-Refs 1 bis 120.

Belegstufen von bbe (aus `status.json`, so übernommen): **Kern** = Lean, nur vom Lean-Kern geprüft;
**native** = Lean mit `native_decide` (kompilierter Code, schwächer); **gerechnet** = C/Python-Programm, nicht
bewiesen; **Heuristik** = Argument oder Beobachtung. bbe benutzt **eigene Lean-Definitionen**, nicht die von
busycoq. Ein Lean-Satz von bbe ist deshalb nicht direkt bei busycoq einreichbar.

## Ergebnis in drei Sätzen

1. Zu **396** (und dem Zwilling 110) hatte bbe am 24.11. alles, was wir am 25./26.11. gefunden haben, und mehr:
   Besuchsgesetz und Rundenform in Lean seit 13.11., Lauf bis Runde 3.000.000, dieselben zwei Beinahe-Fälle,
   eine Gefahrenbedingung („Versatz 2“, Defizit ungerade) und den Nachweis, dass eine Invariante nur über das
   Wortende nicht reicht. **Unser 396-Ergebnis ist eine unabhängige Bestätigung, keine Neuheit.** Was nur wir
   haben: die Rückführung **in Rocq auf busycoqs Definitionen** (`rocq/rueckfuehrung_396.v`, PR 21).
2. **busycoq hat heute Nacht 25 PRs nach BB6 gemergt**, darunter **#59** (88, 312, 449 halten) und **#55**
   (471 hält nicht). 88, 312, 449 und 471 sind damit upstream entschieden. Unser Pin `33209bc7` bleibt, bis du
   etwas anderes sagst.
3. Zu **Gruppe 1** und **M5** sind wir weiter als bbe (dort Stand 8. bzw. 13.11.); Widersprüche gibt es keine.

## 1. busycoq: was sich seit unserem Abgleich vom 25.11. geändert hat

- BB6: `33209bc7` → `9c078ca`, 52 Commits, 25 gemergte PRs (#43–46, 48–52, 55, 57, 59, 67, 68, 81, 82, 86, 90,
  97, 100, 103, 110, 112–114), 37 neue Dateien. `33209bc7` ist Vorfahr von `9c078ca` (geprüft).
- **#59** (Alk, `f23281d`, gemergt in `1ff6eba`): 88, 312, 449 **halten** (Runde 161.211, Block `1011`).
- **#55** (Alk, `2787cb8`, gemergt in `765f97f`): unter anderem **471 hält nicht**
  (`verify/M_1RB0LB_0RC0LD_1LD1RE_0LA0RB_0RD1RF_1LAHHH.v`). In unseren Daten stand das als offene PR.
- **#72, #73** (14.11., von der bbe-Sitzung eingereicht, **nicht gemergt**): 123 und 223 **halten** (Besuchsgesetz
  in zwei Formen, Coq 8.20.1, `vm_compute` rund 15 min).
- **Keine** Datei in BB6 (neu seit Pin) und **keine** in den PR-Refs 1–120 (nur gegenüber BB6 geänderte Dateien,
  voller Text) nennt 396, 110, 587, Gruppe 1 oder M5. Kontrolle: dieselbe Suche findet 123 in PR #72.
- Der Merge-Zustand der übrigen PRs ist per git nur für gemergte sichtbar (Vorfahr von BB6); offen oder
  geschlossen ist nicht unterscheidbar.

## 2. Je Maschine

Spalten: **bbe bewiesen** (Kern / native), **bbe gerechnet** (C/Python, Grenze), **bbe vermutet**,
**nur wir**, **nur bbe**, **Widerspruch**.

### 396 `1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---` (bbe-Stand 24.11.)

| | |
|---|---|
| bbe Kern | Haltekonfigurationen; kein Halt in 10^4 Schritten; Durchlaufregeln; Zählerschritte (10 Sätze); **Besuchsgesetz** `vis_0, vis_100, vis_110, vis_1010, vis_1011`, `vis_111_halts`, Rundenform `start`, `round` (`lean/Visit.lean`, seit 13.11.); **Wortrechnung = Maschine** in beiden Richtungen (`run_sound`, `halts_of_run`, `not_halts_of_run`, `lean/Word.lean`); **`junk_offset1`** (harmlos) und **`junk_offset2_halts`** (Halt); **Defizitform** `visd_eq`, `roundW_visd`, `visd_digit_exact` (`lean/Deficit.lean`) |
| bbe native | kein Halt in 10^7 Schritten; erste **2.000 Runden** ohne Halt (`run_2000_ok`, rund 10^300 Besuche) |
| bbe gerechnet | kein Halt in 10^11 Schritten direkt; Wortrechnung **bis Runde 3.000.000** ohne `111` (`piperun.c`, ein Programm; gegen `wordrun.c` bei Runde 20.000 und `deficit.c` bei 200.000 zellgleich); **14 junk-Ereignisse** (Runden 161.210, 194.646, 757.565, 906.775, 1.042.306, 1.489.725, 1.731.288, 1.768.130, 1.794.988, 1.799.191, 1.802.854, 1.975.596, 2.717.689, 2.959.136), alle harmlos und alle mit demselben Ende `1010 000 1 1` |
| bbe vermutet | „Einziger junk ist `11`“ (Argument, nicht in Lean) |
| nur wir | Rückführung **in Rocq** auf busycoqs `halts`/`c0`: `halts tm c0 <-> W.trifft111 W.start`, axiomfrei, pruefen-Lauf 45700149762 in beiden Images (PR 21). Zweites unabhängiges Programm (`runde_b.cpp`, exakter Zähler) zeilengleich bis Runde 573.850 (PR 24). Rückwärts-Analyse der Wege zu `111` (`rueckwaerts.py`, Wörter bis Länge 8 vollständig). |
| nur bbe | Lauf bis 3.000.000 statt 748.162; Gefahrenbedingung (Versatz 2, ungerades Defizit); Endfenster-Suche und Störungsrechnung (siehe Abschnitt 3); Defizitform in Lean |
| Widerspruch | **keiner.** Unsere Zahlen stimmen mit bbe überein: junk (bei uns „`11` am Rundenende“) in 161.210 und 194.646, `1011` in 161.211 und 194.647, kein weiteres Ereignis bis 748.162 (bbe: nächstes junk in 757.565). Wortlänge passt (bbe 1.055.794 Zellen nach Runde 169.999, wir 1.615.087 nach 260.000; beide rund 6,21 Zellen je Runde). |

### 110 `1RB0LB_0RC0LD_1LD1RE_0LA0RF_1RB0RD_0RB---`

| | |
|---|---|
| bbe | wie 396 (gleiche Dateien, gleiche Läufe). Unterschied nur bei `111`: für `11100…` hat bbe keine Regel (`junk_offset2_first` statt `..._halts`). bbe sagt schon seit 13.11.: „Die beiden Maschinen laufen gleich, bis ein Besuch `111` trifft.“ |
| nur wir | Suche über alle 608 mit zwei Programmen (PR 23) |
| nur bbe | alles in Lean (Besuchsgesetz für 110 ist bei uns nur getestet) |
| Widerspruch | keiner. **Korrektur:** In PR 23 nannten wir 110 „neu“. bbe hatte 110 seit dem 13.11. |

### 587 `1RB1LD_0RC0LF_1LD1RE_0LA0RB_0RD1RB_0LD---`

| | |
|---|---|
| bbe Kern | Besuchsgesetz (`1011 → 1000`, `111` hält); **`1011` und `111` nur am rechten Wortende** (`right_end_1011`, `right_end_halt`, `halts_iff_right_end`, `lean/Cascade.lean`, ohne `native_decide`); **Schiebegesetz und „schmutziger Stopp“** (`shift`, `never_at_stop`, `dirty`, `dirty_next`, `fin_r0`, `lean/Shift.lean`); Trägersystem mit 8 Regeln |
| bbe native | 10^7 Schritte |
| bbe gerechnet | 10^10 Schritte direkt; Besuchsgesetz **bis Runde 4.000.000** ohne Halt (`visp.c`), 20 `1011`-Besuche, alle am rechten Ende; **Zählbedingung**: an allen 4 schmutzigen Stopps bis Runde 10^6 ist die Zahl c eine Zweierpotenz (sonst in nur 46 % der Runden); keine DFA-Zertifikate bis 7 Zustände (SAT) |
| nur wir | Hinweis auf cryptids (`Accelerations` 2.3, bewiesene Beschleunigung in Lean), den bbe nicht nennt; unser Lauf (Run 45693422057, 611.107 Runden) |
| Widerspruch | keiner |

### 88, 312, 449 (Familie PR #59)

| | |
|---|---|
| Stand | **upstream entschieden: halten.** busycoq #59 seit 26.11. in BB6 (`1ff6eba`). bbe hat #59 selbst mit Coq 8.20.1 gebaut (axiomfrei). |
| bbe eigene | nur Zähler- und Durchlaufregeln in Lean, „offen“ ohne #59 |
| nur wir | 88 hält in Runde 161.211 auch in unserem eigenen Programm (`runde.c`, Run 45676623019) |
| Widerspruch | keiner. **Korrektur bei uns:** STATUS nannte #59 „offen, nicht gemergt“; das galt bis 25.11. |

### 123, 223, 471: warum unser Suchlauf sie nicht findet

bbe zählt sie zur Familie G11-Y („zwei Zähler, die zusammen ticken“). Das ist eine Familie nach dem
**Verhalten**. Unser Suchlauf (PR 23) verlangt das Besuchsgesetz **wörtlich**: Kopf im Zustand c auf der ersten
Zelle des Wortes, links davon `0` und eine beliebige Zelle x, Rückkehr im Zustand a auf x, dazu
`V(0r)=1r`, `V(100r)=V(110r)=000V(r)`, `V(1010r)=1010V(V(r))`. Das scheitert bei den drei an verschiedenen
Stellen. Nachgerechnet mit unserer eigenen Besuchsfunktion aus `suche_a.py` an 300 Zufallsresten r (Länge 0
bis 8) und beiden x:

| Holdout | was anders ist | Folge für unsere Suche | Entscheidung |
|---|---|---|---|
| **471** `1RB0LB_0RC0LD_1LD1RE_0LA0RB_0RD1RF_1LA---` | Gleiche Lage wie 396, gleiche Regeln für `0`, `100`, `1010`, **`1011 → 0001`** (wie 396), `111` hält. **Aber `V(110r) = 001r`** (kein innerer Besuch). Bei uns: `110`-Regel 0 von 600, `001r` 600 von 600. | scheitert an der `110`-Regel | **hält nicht**, busycoq #55, seit 26.11. gemergt |
| **223** `1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA1RB_1RE---` | Gleiche Regeln wie PR #59 (`1011` hält), aber **um eine Zelle verschoben**: Der Besuch beginnt auf einer festen `0` (Führungszelle), links davon noch eine `0`, Rückkehr zwei Zellen weiter links. Runde `0^∞ A> 1 0 0 s`. In dieser Lage gelten alle Regeln (bei uns 600/600, 560/560, 528/528). | In unserer Lage gehört die Führungszelle zum Wort; dann ist schon `V(0r)=1r` falsch. | **hält**, Runde 161.211. bbe: Lean (native) und Coq (axiomfrei); busycoq PR #73, nicht gemergt |
| **123** `1RB0LB_0RC0LE_1RD0RF_1LB1RB_0LA0RE_1RE---` | Wie 223 verschoben, dazu **zwei Besuchsformen**: V (Eintritt in C) und W (Eintritt in F). In `1010` ist der erste innere Besuch ein W. W weicht bei `110` ab (`W(1100r) = 1010…`; bei uns 0 von 562). `V(1010r)=1010V(V(r))` gilt nur in 442 von 530 Fällen, `1010 W, dann V` in 522 von 522. | Lage und zweite Form | **hält**, Runde 161.211. bbe: Lean (native) und Coq; busycoq PR #72, nicht gemergt |

Der externe Befund „sie erfüllen das Gesetz nur teilweise“ passt dazu: 471 erfüllt alles außer `110`; 123 und
223 erfüllen es in einer um eine Zelle verschobenen Lage (123 zusätzlich mit zweiter Form). **Unser Satz „Keine
weitere Suche nach dieser Familie nötig“ (PR 23) war damit zu stark:** Die Suche deckt Umbenennung und Spiegelung
ab, aber keine verschobene Lage, keine zwei Besuchsformen und keine abweichende `110`-Regel. Für 396 ändert das
nichts: Keine der drei hat dieselbe `111`-Regel wie 396 und zugleich dasselbe Wortsystem.

Für 396 wichtig: **471 ist ein bewiesener Nicht-Halter mit `1011 → 0001` und Halt bei `111`.** Der Unterschied
zu 396 ist nur `110 → 001` statt `000 V(…)`. Die Beweistechnik von #55 (Token-Wandler mit „schwebendem“ Stück,
periodische Zonen `B^t C D^t`, Abschluss nach 7.696 Runden) ist eine mögliche Vorlage. Ob sie auf 396 passt, ist
**nicht geprüft**: Bei 396 nistet `110` einen Besuch, das ändert die Zählung grundlegend.

### Gruppe 1: 114, 367, 378 (bbe-Stand 13.11.)

| | |
|---|---|
| bbe Kern | je Maschine: Haltekonfigurationen, 10^4 Schritte, **Umkodier-Durchläufe** (114: sechs Regeln; 367: acht; 378: Verschieberegeln) |
| bbe native | 10^7 Schritte |
| bbe gerechnet | 10^9 Schritte (alle); 114 beschleunigt bis 1,29·10^10 (`rleaccel`); `rsim` 1,4 bis 1,9·10^9 (Heuristik, Sprünge nicht bewiesen); CTL und NGramCPS scheitern |
| bbe vermutet | „jeder Eintrag wächst je Zyklus um 2“ (114), Treppe der Lauflängen (367), Dreiergruppen von Bereichen (378) |
| nur wir | **Rocq**: Durchlauf-Beschleunigung (`rocq/gruppe1_durchlauf.v`, alle drei Starts) und Regel F; Satz K(C) (von Hand); kein Halt **lückenlos bis 10^12** (2 Programme), **bedingt bis 10^24** (A, C) bzw. **10^25** (D); Phasen-Automat mit 7 rechnergestützt geprüften Regeln (PR 19); keine Erhaltungsgröße (PR 16) |
| nur bbe | nichts Wesentliches darüber hinaus; die gleiche Tabelle mit drei Starts erkennt bbe auch |
| Widerspruch | keiner. bbe beschreibt das Band in anderen Wörtern (`001`, `0001`); „jeder Eintrag +2“ und unsere Regel F sind verschiedene Koordinaten, nicht abgeglichen |

### M5-Gruppe: 274, 318, 322, 518 (bbe-Stand 8.11., 274 zuletzt 24.11. Rückwärtssuche)

| | |
|---|---|
| bbe Kern | Haltekonfigurationen, 10^4 Schritte; 274: 12 Verschieberegeln; 322: Durchläufe und `halt11`; 518: Durchläufe und Wende am rechten Ende; **318/518 im Gleichschritt bis zum ersten Bruch** (`lean/Twin.lean`: `lock_or_break`, `not_halts_of_noBreak`) |
| bbe native | 10^7 Schritte |
| bbe gerechnet | kein Halt: 318 bis 2·10^10, 322 und 518 bis 10^11, 274 bis 10^9; 318: zehn Umbauten bis Schritt 29.787.121, keiner bis 2·10^10; Zählerregel an 4.133 Durchläufen bis 10^8 |
| bbe Paare | 318~322 und 274~518 gleiche Tabelle, anderer Start; 318~518 gleicher Lauf (10^7, Lean bis Bruch); 322~274 gleiche Bänder in anderem Tempo (10^7) |
| nur wir | **alle vier als eine 5-Zustands-Maschine M5** (Tabellenvergleich, 2 Programme); Umbauten bis **8·10^14** verfolgt (ein Programm plus Stichproben) |
| nur bbe | Lean-Satz zum Gleichschritt 318/518; längere direkte Haltprüfung (10^11 für 322/518, wir 10^10 mit 2 Programmen) |
| Widerspruch | keiner gefunden. **Nicht abgeglichen:** unser großer Umbau „ab A bei 29.754.240“ gegen bbe „Schritt 29.787.121“ (Kopf erreicht das linke Ende in C). Vermutlich andere Definition des Zeitpunkts, nicht nachgeprüft. Haltemuster in eigener Benennung von bbe passen zu unseren (`B> 1 1` / `C> 1 1` in M5-Namen). |

## 3. 396: Was bbe zur Invariante versucht hat

Alles aus `holdouts/1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---/README.md` (Abschnitte vom 22. und 24.11.) und
dem 587-Ordner (23./24.11.). Belegstufe jeweils angegeben.

**junk.** Jeder Block, den eine Runde durchläuft, wird `000`, `100` oder `1010`; zwei benachbarte `1` entstehen
nur dort, wo der Zähler ausläuft: auf der letzten `0` eines Ziffernblocks direkt vor einer `1`. Das nennt bbe ein
junk-Ereignis; es geht nur am Wortende (Argument, nicht Lean; für 587 ist das Gegenstück `Casc.clean` in Lean
bewiesen). Das entspricht unserem Befund B2/B3 (PR 24, Stichprobe).

**Versatz 2 (`junk_offset2_halts`, Lean-Kern).** Nach einem junk-Ereignis endet das Wort auf `… 0 1 1`. Die
nächste Runde setzt ihren Block 1 oder 2 Zellen in den letzten Block der Vorrunde (Phasenregel aus PR #59):
- **Versatz 1:** liest `0 0 1 1`, zwei Besuche geben über `1011` ein `0001` (`junk_offset1`, harmlos).
- **Versatz 2:** liest `0 1 1`, der zweite Besuch trifft `111`, **die Maschine hält**.

Welcher Versatz kommt, hängt vom letzten Ziffernblock vor dem junk ab: Gefährlich ist es nur, wenn dieser Block
genau **3** Besuche bekommt statt 2. In der Defizitform (Zähler = 2^e − c, Lean-Kern): **gefährlich nur bei
ungeradem Defizit c beim Eintritt in den letzten `000`-Block.** Ein Verdoppler (`1010`) direkt davor macht c
gerade und damit sicher. Alle 14 junk-Ereignisse bis Runde 3.000.000 hatten einen Verdoppler davor.

**Beinahe-Fälle.** bbe meint damit etwas anderes als wir (bei uns: die zwei Runden mit `11` am Ende). bbe
verändert in jeder Runde die Zahl der Besuche n an einem Blockanfang rund 60 Zellen vor dem Wortende und
rechnet 6 Runden weiter (`nearmiss.c`, gerechnet, über 500.000 Runden):

| Änderung | Runden, nach denen binnen 6 Runden `111` folgt |
|---|---:|
| n − 2, n − 1 | 0 |
| n + 1 | 47 |
| n + 2 | 105 |
| 2n | 15.526 |
| n/2 | 10.524 |

Die Tabelle gilt für 110 (über 500.000 Runden); für 396 sind die Zahlen in den ersten 200.000 Runden gleich,
nur n/2 weicht ab. Ein oder zwei Besuche mehr reichen also etwa alle 3.500 Runden für `111` zwei Runden später.
bbe hat das später eingeschränkt (`nearmiss_level.c`, 200.000 Runden): 91 der 141 Fälle bräuchten einen Zähler
über 2^Stufe, den keine Runde erzeugen kann; die übrigen 50 bräuchten Defizit 0 oder 1, wo der echte Lauf 1, 2
oder 3 hatte.

**Warum eine Invariante nur über die letzten Blöcke nicht reicht** (gerechnet, `endbfs.py`): bbe nimmt die
letzten 48 Zellen des echten Wortes und lässt jede spätere Runde mit **beliebigem** Zähler der Form 2^a − d
eintreten (sogar nur mit exakten Zweierpotenzen, d = 0). Breitensuche erreicht `111` nach 3 Runden (ab Runde 11
und 2.000) bzw. 2 Runden (ab Runde 5.000). Das Modell gibt mit den echten Zählern in 98,5 % der Runden das
echte nächste Fenster. **Folgerung von bbe:** Was den Lauf von `111` fernhält, ist nicht die Form des Wortendes,
sondern die genaue Größe des Zählers, die von vorn durch das ganze Wort getragen wird (das Defizit c, das sich
an jedem Ziffernblock halbiert und an jedem Verdoppler verdoppelt). Ein Beweis braucht einen Griff auf dieses
Defizit **entlang des ganzen Wortes**. Für 587 dasselbe mit SAT: kein Automat mit bis zu 7 Zuständen
(Annahme-Garantie-Stil wie busycoq #112) beweist das Besuchsgesetz sicher; das gilt auch für das Gesetz von 110,
also das Wortsystem von 396 bis auf `111`.

**Vorschlag von bbe als nächster Schritt:** die Parität des Defizits durch die letzten Ziffernblöcke rückwärts
bis zu den Bits verfolgen, aus denen sie stammt (eine Folge von k Ziffernblöcken liest Bit k des Defizits);
oder weiterrechnen, bis ein junk mit ungeradem Defizit auftritt.

**Bezug zu unserer gestoppten Beweisidee** („kein Besuch endet auf einer 0 direkt vor 11“, 3 Blöcke, auf Eis):
Das ist genau die Aussage „kein junk mit Versatz 2“. bbe hält sie für **nicht lokal beweisbar** (Endfenster-Suche,
Störungsrechnung, SAT bei 587). Ein Plan dafür müsste das Defizit von vorn mitführen, nicht nur die letzten
Blöcke.

## 4. Neue CLAUDE.md-Regel

Eingetragen (Wortlaut in `CLAUDE.md`, Abschnitt „Feste Regeln“): Vor jeder Arbeit an einer Maschine busycoq
(Zweig BB6 und offene PRs, per `git fetch` der PR-Refs) und busy-beaver-explorer (per git) prüfen und den Befund
im Bericht nennen. Die Regel „erst in Discord fragen“ ist gestrichen. Das Rocq-OK von Justus bleibt.
**In den Projektanweisungen auf claude.ai steht die Discord-Regel noch;** die kann nur Justus ändern.

## Bericht

- **Ergebnis:** Zu 396/110 ist bbe uns in allem voraus außer dem Rocq-Beweis der Rückführung; widersprochen
  haben wir uns nirgends. busycoq hat #59 und #55 gemergt, damit sind 88, 312, 449 (halten) und 471 (hält nicht)
  upstream entschieden; 123 und 223 halten laut bbe (Lean native und Coq), busycoq-PR #72/#73 offen. Bei Gruppe
  1 und M5 sind wir weiter.
- **Belege:** bbe Kopf `662e215`, busycoq BB6 `9c078ca`; Nachrechnung zu 123/223/471 mit
  `analyse/abgleich_bbe/teilgesetz.py` (unsere Lage) und `verschoben.py` (Lage von 123/223), beide mit `besuch`
  aus `analyse/besuchsgesetz/suche_a.py`, Ausgaben `teilgesetz.txt`, `verschoben.txt` (je unter 1 s).
  Kontrollen: 396 erfüllt in `teilgesetz.py` alle Regeln (Nenner enthalten Reste, die selbst halten; die
  `111`-Spalte ist trivial, weil der Eintrittszustand dort sofort hält); 471 fällt bei `110` durch, 123 bei
  `1010` mit zwei V-Besuchen: das Werkzeug schlägt also an. Kein Actions-Lauf.
- **Abweichungen und eigene Fehler:**
  - In PR 23 nannte ich 110 „neu“ und schrieb „keine weitere Suche nötig“. Beides war falsch, siehe oben.
  - Die PR-Suche in busycoq erfasst nur Dateien, die eine PR gegenüber BB6 ändert; gemergte PRs zählen jetzt
    zu BB6. Offen oder geschlossen ist per git nicht sichtbar.
  - Die Nachrechnung zu 123/223/471 ist eine Stichprobe (300 Reste bis Länge 8), nur ein Programm. Für die
    Entscheidungen stütze ich mich auf busycoq (#55) und bbe, nicht auf sie.
  - bbe-Ordner zu Gruppe 1 und M5 sind 2 bis 3 Wochen alt; ich habe nur gelesen, nichts nachgerechnet.
- **Offene Punkte:** Zeitpunkt des M5-Umbaus (29.754.240 gegen 29.787.121) nicht abgeglichen. Ob die Technik von
  #55 (471) auf 396 passt, nicht geprüft. Projektanweisungen auf claude.ai noch mit Discord-Regel.
- **Empfehlung:** 396 nicht als eigene Neuheit melden. Vor einer Beweisidee zu 396 erst #55 (471) und die
  Defizitform von bbe lesen; die bisherige Idee (nur Wortende) ist laut bbe zu schwach.
