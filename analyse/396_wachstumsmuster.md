# 396: Wachstumsmuster nach dem Vorbild von 471

Thread „396 Wachstumsmuster“, 26.11.2026, 2 Blöcke, nur Analyse, kein Rocq.
Programme in `analyse/396/muster/`, Workflow `lauf_muster` (PR 28).

## Ergebnis: (b) kein Muster

- **Die Gestalt von 471 gibt es bei 396 bis Runde 1.200.000 nicht.** Direkt hinter L^k sitzt ein Binärzähler. Die
  ersten m Zellen dort sind ab spätestens Runde 97 periodisch, und ihre kleinste Periode ist eine Zweierpotenz, die mit
  m wächst: 4 (m = 8), 128 (m = 64), 4.096 (m = 128), 262.144 (m = 224). Für m ≥ 232 gibt es keine Periode bis 300.000.
- Die Gestalt bräuchte **ein** P für alle m. Nach den Daten müsste P ein Vielfaches von 2^18 = 262.144 sein, und das
  Fenster aus 256 Zellen wiederholt sich zwischen Runde 194.647 und 1.200.000 kein einziges Mal (1.005.354 Runden).
  Dazu kommen Junk-Ereignisse in unregelmäßigem Abstand. Wächst die Periode mit m so weiter wie bisher, gibt es
  überhaupt kein solches P. Das ist beobachtet, nicht bewiesen.
- **Neu gegenüber busy-beaver-explorer:** die Zählerstruktur hinter L^k mit ihren Zweierpotenz-Perioden. Ihre
  Junk-Ereignisse bis Runde 1.042.306 bestätigt unser Lauf unabhängig, Runde für Runde.

## Pflichtprüfung vor der Arbeit (CLAUDE.md, 26.11.2026)

- **busycoq:** Zweig BB6 auf `9c078ca` (26.11., 08:34 +0800) und alle 120 PR-Refs per `git fetch`, nur gelesen.
  - 396 (`1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---`) steht auf BB6 nur in den Äquivalenzlisten `Eqv_Misc.v`
    und `Eqv_v3.v`, in keiner PR-Datei.
  - 110 steht nur in `Eqv_v2.v`, in keiner PR-Datei.
  - Gegenprobe der Suche: Der String von PR #72 wird in `refs/pr/72` gefunden.
- **busy-beaver-explorer** (Kopf `7c6cf3e`, 25.11. 21:51 −0800), Ordner der Maschine, gelesen:
  - 396 ist dort weiter offen. Der Lauf reicht jetzt bis Runde 4.000.000, ohne 111.
  - Es gibt dort 18 Junk-Ereignisse, das erste 161.210 und das letzte 3.951.813 (Liste unten).
  - Die Defizitform (`lean/Deficit.lean`) schreibt den Zähler als 2^e − c mit kleinem Defizit c. Dazu gibt es eine
    Gefahrenbedingung: Junk ist nur gefährlich, wenn das Defizit vor dem letzten `000`-Block ungerade ist.
  - **Nach einer Gestalt wie bei 471 (Blöcke B^t, D^t, Periode P) wurde dort nicht gesucht.** Weder bei 396 noch
    bei 110 oder 471 steht etwas dazu. Der busycoq-Beweis zu 471 (PR #55) wird dort nicht erwähnt.

## 1. Der Beweis zu 471 und was davon für 396 gilt

Datei `verify/M_1RB0LB_0RC0LD_1LD1RE_0LA0RB_0RD1RF_1LAHHH.v` aus busycoq BB6 `9c078ca`, per git gelesen. Die
Regeln von 471 und 396 sind gleich bis auf eine: Bei 471 gilt V(110x) = 001x (der Besuch endet), bei 396 gilt
V(110x) = 000 V(x) (der Besuch geht weiter). Die Regel V(1011x) = 0001x haben beide.

| Baustein im 471-Beweis | Inhalt | gilt für 396? |
|---|---|---|
| Token L = 1010, H = 100, Z = 000 | n Besuche auf L geben 2n darunter, H/Z sind eine Binärziffer | ja (nur Regeln 0, 100, 1010) |
| `xstep`, Fälle P10, P00, P0+Z, PE | ein angestoßenes Stück (10, 00, 0) liest die Token neu | ja, dieselben Regeln |
| `xstep`, Fälle P0+H und P0+L | brauchen `vis_c` (110 → 001) | **nein**, hängt an der 110-Regel |
| `sstep`, Zählform 2^a x − c | Durchlauf mit unbekanntem x | Arithmetik ja, Tabelle wie `xstep` nur teilweise |
| `zone`, `zone_ok`, `ar_layer` | B^t C D^t als ineinanderliegende Paare, 2^64 x − c hinein, 2^b x − e hinaus | ja, rein arithmetisch |
| `VS_T`, T = HZZZ | genau 2^(4v) Besuche hängen ein T an | ja (nur Ziffern) |
| `closure`, `sw` | Bandfamilie L^(k+3848t) A B^t C D^t E T^(v+962t) | Form ja, Inhalt nein |
| `check` mit rs = 26.128, P = 7.696, Blocklängen | aus dem Lauf von 471 abgelesen | nein, 471-Daten |

Bei 396 macht ein angestoßenes `0` vor `100` daraus nach zwei Besuchen `000` und ein anstehendes Stück `1`
(`0100 → 1100 → 0001`). Dieses Stück `1` vor einem Token, das mit 1 beginnt, ist genau das `11` (Junk). Bei 471 gibt
es dieses Stück nicht, die Wörter bestehen dort nur aus Token. Ein Beweis nach dem Muster von 471 bräuchte für 396
eine neue `xstep`-Tabelle mit dem zusätzlichen Stück `1`.

## 2. Suche nach der Gestalt bei 396

### Werkzeuge

- **Programm X** (`defizit.c`, neu): Rundenrechnung in der Defizitform. Es ist bis Runde 20.000 prüfsummengleich
  mit `runde.c` (Teil 2) und 3,7-mal schneller. Negativkontrolle: Mit `FEHLER=1` (falsche Ziffernregel) weicht es ab.
- **Zweites Programm** (`runde_b_anf.cpp`): `runde_b.cpp` aus Teil 2 mit exaktem Zähler, unverändert in der Rechnung.
  Ergänzt ist nur die Ausgabe des Anfangsfensters.
- **Periodensuche zweimal:** `auswertung.py` (Kandidaten aus Wiederholungen) und `zweit.c` (Rand-Funktion nach
  Knuth-Morris-Pratt), unabhängig geschrieben. Kontrollen an künstlichen Folgen mit bekannter Periode und eine
  Negativkontrolle mit einer gestörten Stelle, beide schlagen wie erwartet an (`kontrollen.sh`).

### Warum das Anfangsfenster entscheidet

In der Gestalt L^(k+at) A B^t C D^t E T^(v+bt) steht direkt hinter dem L-Lauf A, dann B, B, …. Gilt die Gestalt ab
Runde r0 mit Periode P, dann sind die ersten m Zellen hinter dem L-Lauf in Runde r und r+P gleich, sobald A B^t
mindestens m Zellen lang ist. Das gilt für jedes m und mit **demselben** P. Die Folge der m-Zellen-Fenster
muss also für jedes m schließlich die Periode P haben. Ihre kleinste Periode muss dann P teilen.

### Befund

Lauf: Run 45771362724, Job x, Programm X bis Runde 1.200.000 in 5.274 s, kein Halt. Beide Periodensuchen
(`auswertung.py`, `zweit.c`) liefern auf denselben Daten Zeile für Zeile dasselbe.

| m (Zellen hinter L^k) | kleinste Periode | periodisch ab Runde |
|---:|---:|---:|
| 8 | 4 | 4 |
| 16 | 8 | 5 |
| 24 | 16 | 12 |
| 32 / 40 | 32 | 16 / 20 |
| 48 | 64 | 20 |
| 56 bis 80 | 128 | 20 bis 39 |
| 88 | 256 | 43 |
| 96 | 512 | 44 |
| 104 / 112 | 1.024 | 58 / 64 |
| 120 bis 168 | 4.096 | 72 bis 86 |
| 176 | 8.192 | 88 |
| 184 / 192 | 32.768 | 88 / 92 |
| 200 / 208 | 65.536 | 93 / 94 |
| 216 / 224 | 262.144 | 96 / 97 |
| 232 bis 320 | keine ≤ 300.000 | – |

Geprüft ist jeweils die zweite Hälfte der Runden (600.001 bis 1.200.000), der Beginn der Periodizität rückwärts
über alle Runden. Alle gefundenen Perioden sind Zweierpotenzen.

**Folgerungen für die Gestalt L^(k+at) A B^t C D^t E T^(v+bt):**

- Ab Runde 97 ist das Fenster aus 224 Zellen genau 2^18-periodisch. Eine Gestalt mit Periode P ließe dieses Fenster
  schließlich P-periodisch werden. Also müsste P ein Vielfaches von 262.144 sein.
- Das Fenster aus 256 Zellen wiederholt sich von Runde 194.647 bis 1.200.000 nie. Eine Gestalt mit
  r0 + P ≤ 1.200.000 ist damit ausgeschlossen (sofern A B^t dort schon 256 Zellen lang ist).
- Junk-Ereignisse (ein neues `11` am Wortende) in Runde 161.210, 194.646, 757.565, 906.775 und 1.042.306.
  - Bei einer Gestalt aus reinen Token wie bei 471 gibt es nach r0 kein Junk mehr. Also wäre r0 > 1.042.306.
  - Selbst wenn ein Block Junk enthalten dürfte, müssten die Ereignisse nach r0 mit Periode P wiederkehren. Die
    Abstände nach 757.565 sind 149.210 und 284.741, keiner ist ein Vielfaches von 2^18. Also wäre r0 > 757.565.
- busy-beaver-explorer meldet weitere Junk-Ereignisse bis Runde 3.951.813 in unregelmäßigen Abständen (z. B.
  1.794.988, 1.799.191, 1.802.854). Das ist deren Rechnung, von uns nur bis 1.042.306 nachgeprüft.
- Grenze der Aussage: Eine Gestalt mit P ≥ 262.144 (Vielfaches von 2^18), die erst nach Runde 1.042.306 einsetzt,
  ist durch endliches Rechnen nicht auszuschließen. Ausschließen ließe sie sich nur mit einem Beweis, dass die
  Perioden der Anfangsfenster unbeschränkt wachsen.

### Was stattdessen wächst

Stichrunden aus dem Tokenbild (L = 1010, H = 100, Z = 000):

| Runde | Zellen | L | H | Z | L-Lauf k |
|---:|---:|---:|---:|---:|---:|
| 200.000 | 1.242.388 | 177.484 | 80.273 | 97.211 | 100.000 |
| 600.000 | 3.727.654 | 532.522 | 241.665 | 290.857 | 300.000 |
| 1.000.000 | 6.212.941 | 887.563 | 402.510 | 485.053 | 500.000 |
| 1.200.000 | 7.456.162 | 1.065.166 | 482.731 | 582.435 | 600.000 |

- **Linear wachsen:** der L-Lauf (k = r/2 oder r/2 + 1 in allen 1,2 Mio. Runden, wie bei 471), die Wortlänge (etwa
  6,2 Zellen je Runde) und die Zahl der Token jeder Art. Es gibt so viele L wie Ziffern H und Z zusammen, bis auf höchstens 2.
  Der Stufenpfad (L hebt, H/Z senkt) steigt bis zum Ende des L-Laufs auf k und kommt am Wortende auf −1 bis 2 zurück.
- **Nicht periodisch, sondern wie ein Zählwerk:** der Bereich direkt hinter L^k. Je etwa 8 bis 16 Zellen tiefer
  verdoppelt sich die Periode. Bei 471 ist dieser Bereich der feste Block A, dort ist das Zählwerk nach 7.696 Runden
  geschlossen.
- **Unregelmäßig:** das Wortende. Das Fenster aus den letzten 256 Zellen wiederholt sich in 1.005.354 Runden nur
  184-mal, fast immer nach 8 Runden, sonst ist es jedes Mal neu. Die Junk-Ereignisse kommen in Abständen von 33.436,
  562.919, 149.210 und 135.531 Runden. Bei 471 steht am Ende das gleichmäßige T^v mit T = HZZZ.
- Woher der Unterschied kommt, vermute ich in der 110-Regel (Abschnitt 1). Bei 471 endet ein Besuch auf `110`, bei
  396 geht er weiter. Belegt ist das nicht.

## 3. Defizitform von busy-beaver-explorer

`lean/Deficit.lean` und README von busy-beaver-explorer (Stand `7c6cf3e`) gelesen.

- Der Zähler wird dort als 2^e − c geschrieben. Die Stufe e steigt bei `1010` und fällt bei jeder Ziffer, das
  Defizit c ist klein. Regeln: 0 am Blockanfang c + 1, Ziffer schreibt `100` bei geradem und `000` bei ungeradem
  c und halbiert c, `1010` verdoppelt c, `1011` gibt c + 1. Das ist dieselbe Rechnung wie unser Programm X.
- Daraus folgt dort: Ein Durchlauf mit c = 0 lässt alle Ziffern stehen. Junk ist nur gefährlich, wenn das Defizit vor
  dem letzten `000`-Block ungerade ist. Alle 18 Junk-Ereignisse bis Runde 4 Mio. waren ungefährlich.
- **Eine Suche nach einer periodischen Gestalt steht dort nicht.** Die Defizitform wird nur für das Wortende und die
  Gefahrenbedingung benutzt.
- Bezug zu unserem Befund: Hinter L^k kommt der Zähler immer mit Defizit 0 an. Ändern kann sich dort nur etwas durch
  das angestoßene Stück `10` am Anfang und die Nullen am Blockanfang. Das Zählwerk hinter L^k entsteht also allein aus
  diesem Stück, nicht aus großen Defiziten.

## Belege

- **Run 45771362724** (Workflow `lauf_muster`, Branch `claude/project-thread-6ahuss`, Commit `05720ab`):
  - Job kontrollen grün (`kontrollen.sh`: X = runde.c, runde_b_anf = runde_b, A-Zeilen X = B bis 10.000,
    Periodensuche an künstlichen Folgen, drei Negativkontrollen schlagen an).
  - Job x grün: Programm X bis Runde 1.200.000, Auswertung und zweite Auswertung im Log.
  - Job b und vergleich: VERGLEICH_PLATZHALTER
- **PR 28** (Workflow, gemergt 26.11.), Commits `3ed932d` (Workflow) und `05720ab` (Programme).
- Lokal bis Runde 200.000: dieselben Perioden bis m = 168 und m = 192 (32.768).

## Abweichungen und eigene Fehler

- Mein erster Versuch, 471 zum Vergleich mit demselben Programm zu rechnen (`MODUS=471`), lief sofort in ein zu
  großes Defizit. Bei 471 ist der Zähler offenbar nicht von der Form 2^e − c mit kleinem c. Ich habe den Modus wieder
  entfernt und nichts damit gerechnet. Der Vergleich mit 471 stützt sich deshalb nur auf den busycoq-Beweis.
- Die Protokoll-Artefakte liegen wieder auf dem gesperrten Speicher-Host. Ausgewertet wurde deshalb nur im Workflow
  selbst, die Ergebnisse stehen in den Logs.

## Offene Punkte

- **Beweis des Zählwerks:** Wachsen die Perioden der Anfangsfenster unbeschränkt? Wenn ja, ist jede Gestalt nach Art
  von 471 für 396 ausgeschlossen, für jedes P. Der Bereich hinter L^k entwickelt sich allein aus sich selbst (der Zähler
  kommt dort immer als exakte Zweierpotenz an). Das macht einen Beweis denkbar, ausgearbeitet ist er nicht.
- Eine Gestalt mit P ≥ 262.144, die erst nach Runde 1.042.306 einsetzt, ist durch Rechnen nicht auszuschließen.
- Eine eigene `xstep`-Tabelle für 396 mit dem zusätzlichen Stück `1` ist nicht aufgestellt.

## Empfehlung

- **Die Suche nach der 471-Gestalt bei 396 abbrechen.** Der Weg über einen festen Block A hinter L^k ist durch das
  Zählwerk versperrt, so weit gerechnet wurde.
- Wenn weiter an 396/110 gearbeitet wird, dann an einer Beschreibung, die das Zählwerk zulässt: Statt fester Blöcke
  ein Zähler mit Stellen wachsender Länge, wie ein Binärzähler. Das wäre ein anderes Beweismuster als bei 471. Ob es
  in busycoq eine Vorlage dafür gibt, habe ich nicht geprüft.
