# Analyse Gruppe 1, Teil 3: Beschleunigung vorbereiten (Schritte 1 bis 3)

Stand 25.11.2026. Nur Analyse, **kein Rocq**. Schritt 4 (Rocq) wartet auf das OK von Justus.
Baut auf `analyse/gruppe1.md` und `analyse/gruppe1_teil2.md` auf. Neues Werkzeug:
`analyse/gruppe1/teil3/sweepmodell.py`.

## Ergebnis in Kürze

- **cryptids:** Dort ist eine „Beschleunigung“ ein vereinfachtes Ersatzsystem mit vier Teilen: ein
  Zustandstyp, ein Startzustand, eine Übersetzung in TM-Konfigurationen und eine Schrittfunktion, die
  entweder einen neuen Zustand oder „Halt“ liefert. Bewiesen wird, dass jeder Schritt des Ersatzsystems
  mindestens einen echten TM-Schritt abbildet und dass „Halt“ wirklich zum Halten führt. Daraus folgt
  allgemein: die Maschine hält genau dann, wenn das Ersatzsystem „Halt“ erreicht. Das ist eine
  Umformulierung, **kein** Beweis über Halten oder Nicht-Halten.
- **Listenmodell:** Geschlossen und vollständig ist es jetzt auf der Ebene der **Durchläufe**: Das Band ist
  eine Liste von Blöcken `011`^n (links vom Kopf) und `100`^n (rechts vom Kopf), getrennt durch kurze
  Bitfolgen. Drei Regeln genügen (zwei Durchlaufregeln und ein Einzelschritt). Das Modell gibt bis 10^9
  Schritte für alle drei Starts **byteweise dieselben** Listen wie das C-Programm aus (36.944 Zeilen).
  Ein Makroschritt ersetzt im Mittel etwa 54 TM-Schritte.
- **Die 11 Prüfstellen am linken Ende** sind erklärt: Es sind Stellen, an denen ein Rechtsdurchlauf von
  C, der am linken Bandende beginnt, auf den Trenner `<1>` (Bits `1100`) trifft, 14 oder 26 Zellen
  vom linken Ende entfernt. Die dritte Zelle ist dort jedes Mal 0. Alle 1,6 Mio. Prüfpunkte je Start sind
  damit einer von zwei Arten zugeordnet; die Zahlen stimmen exakt mit dem C- und dem Rust-Programm überein.
- **Vorschlag für die Aussage** (Abschnitt 3): „Tabelle 114 hält ab Start A / D / C genau dann, wenn das
  Durchlaufmodell ab dem leeren Band in diesem Zustand einen Zustand erreicht, in dem A eine 1 liest
  (gleichwertig: C steht vor `111`).“ Bitte prüfen; erst nach deinem OK beginne ich mit Rocq.
- **Regeln F und Z** gehören nicht in dieses Grundmodell. Sie wären eine zweite, gröbere Stufe darüber.
  Dafür fehlt weiterhin das Modell der Pendelphasen (Abschnitt 4); das ist nicht geschlossen.

## 1. cryptids: was eine Beschleunigung ist

Quelle: `google-deepmind/cryptids`, Commit `3647718b5df22e1a61462dec0376bd204526285a` (12.11.2026), nur
gelesen. Dateien: `BusyBeaver/BB6/Accelerations/README.md`, `BusyBeaver/Defs/Patterns.lean`
(`CollatzHalts`, `IsValidAcceleration`), `BusyBeaver/Basic.lean` (`IsValidAcceleration.isHalt_iff`) und als
Beispiel das kürzeste Modul `M_1RB1LF_0RC0RB_0LD1RB_1LE0LB_0LA1LC_0LB---.lean` (263 Zeilen).

Aufbau (in Lean, für eine Maschine M):

1. `S`: ein eigener Zustandstyp, z. B. `D (L R : List ℕ)`: zwei Listen von Zahlen für die beiden
   Bandhälften.
2. `start : S` und `encode : S → Konfiguration`: übersetzt jeden Zustand in ein konkretes Band. Im Beispiel
   steht jede Zahl k für das Stück `0^k 1`; so ist **jede** Liste ein gültiges Band.
3. `next : S → Option S`: die beschleunigte Regel. `none` bedeutet Halt.
4. `IsValidAcceleration M start encode next` verlangt drei Beweise:
   - M kommt vom leeren Band zu `encode start` (`init_reaches`);
   - für **jeden** Zustand s mit `next s = some s'` kommt M von `encode s` in mindestens einem Schritt zu
     `encode s'` (`step_some`);
   - für jeden Zustand mit `next s = none` erreicht M von `encode s` aus eine Haltekonfiguration
     (`step_none`).
5. Daraus folgt allgemein `isHalt_iff_acceleration : IsHalt M ↔ CollatzHalts next start`, wobei
   `CollatzHalts` heißt: wiederholtes Anwenden von `next` ab `start` liefert irgendwann `none`.

Wichtig für uns:
- Die Schrittregeln müssen für **alle** Zustände des Typs stimmen, nicht nur für die im Lauf erreichten.
  Der Zustandstyp muss also so gewählt sein, dass jede Kombination ein echtes Band beschreibt und `next`
  überall definiert ist.
- Im Beispiel ist die Haltebedingung eine einfache Form der Liste (`L` beginnt mit `2, 0`).
- Bewiesen wird jeweils eine Fallunterscheidung über `next` plus ein Induktionslemma für den langen
  Durchlauf (`sweepB_spec`). Genau so ist auch unser Modell gebaut (Abschnitt 3).
- Viele Module beweisen zusätzlich eine zweite, gröbere Stufe (`HighLevelState`, `highLevelNext`), die
  ganze Durchgänge zusammenfasst. Bei uns wäre das die Stufe der Regeln F und Z.
- In busycoq (Pin) gibt es kein fertiges Gegenstück zu `IsValidAcceleration`. Die Bausteine sind da:
  `halts`, `-->*` (`evstep`), `-->+` (`progress`), `skip_halts`, `progress_nonhalt` in `TM.v`. Die Definition
  und den Satz `isHalt_iff` müssten wir selbst als Hilfslemmata schreiben (erlaubt, kein Axiom nötig).

## 2. Durchlaufmodell für Tabelle 114

Tabelle: `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC`.

### Zustand

`(q, Seite, L, R)`: q ist der TM-Zustand; L und R sind die Bandhälften links und rechts, jeweils als Stapel
mit dem Stück am Kopf oben. Ein Stück ist ein einzelnes Bit oder ein Block `011`^n (nur in L) bzw. `100`^n
(nur in R), n ≥ 1. „Seite“ sagt, ob der Kopf auf dem obersten Bit von R steht (Kopf bewegt sich nach
rechts) oder auf dem obersten Bit von L (Kopf bewegt sich nach links). Das ist dieselbe Schreibweise wie
`l {{q}}> r` und `l <{{q}} r` in busycoq. Jenseits der Stapel ist das Band leer (0).

### Regeln (jeder Makroschritt ist genau eine davon)

| Regel | Bedingung | Wirkung | TM-Schritte |
|---|---|---|---|
| S1 | q = C, Kopf auf R, R beginnt mit `100`^n | Block wandert als `011`^n nach L, Kopf dahinter, weiter C | 3n |
| S2 | q = B oder D, Kopf auf L, L beginnt mit `011`^n | Block wandert als `100`^n nach R, Kopf davor; q wechselt B↔D genau bei ungeradem n | 3n |
| E | sonst | ein gewöhnlicher TM-Schritt auf dem Bit am Kopf (ein Block wird dafür bei Bedarf aufgeteilt) | 1 |

Dazu kommt eine reine Umschreibung ohne TM-Schritt: drei Bits `011` links bzw. `100` rechts werden zu
einem Block zusammengefasst. Halt tritt nur in Regel E auf, wenn A eine 1 liest.

S1 und S2 folgen aus den Blockregeln in Teil 1 (`C> 100 → 011 C>`, `011 <B → <D 100`, `011 <D → <B 100`).
Damit sieht man die Listen aus Teil 1 direkt: die Zahlen n sind die Elemente, die Bitfolgen dazwischen die
Trenner. Beispiel: das Bit `1` zwischen zwei `011`-Blöcken links ist der Trenner `|` (Abstand 4).

### Prüfung mit dem zweiten Programm

`sweepmodell.py` (Python, Stapel aus Blöcken) ist unabhängig von `zweitpruefung.c` (C, Band als Array)
geschrieben. Es gibt bei jedem Rechts-Rekord in Zustand C dieselbe Zeile aus wie `zweitpruefung.c liste`.

| Start | Schritte | Zeilen | Vergleich mit C-Programm | Makroschritte (S1 / S2 / E) |
|---|---:|---:|---|---|
| A (114) | 10^9 | 12.384 | byteweise gleich | 18.384.001 (3.313.703 / 3.321.055 / 11.749.243) |
| D (367) | 10^9 | 12.340 | byteweise gleich | 18.335.899 (3.308.747 / 3.313.549 / 11.713.603) |
| C (378) | 10^9 | 12.220 | byteweise gleich | 18.348.701 (3.304.449 / 3.313.783 / 11.730.469) |

Bandbreite am Ende ebenfalls gleich (37.620 / 37.503 / 37.168).

**Negativkontrollen** (beide schlagen an, Vergleich bis 3·10^6 Schritte):
- `SWEEP_FEHLER=paritaet` (S2 ohne Wechsel B↔D): Unterschied in Zeile 3.
- `SWEEP_FEHLER=s1_block` (S1 schreibt bei n ≥ 5 einen Block `111` statt `011`): Unterschied in Zeile 8.

### Die Prüfpunkte im Durchlaufmodell

Ein Prüfpunkt (B oder D liest 0, rechts davon `11`) ist im Modell der Moment, in dem C auf der rechten
Seite vor `11` steht. Halt genau dann, wenn danach noch eine 1 kommt. `sweepmodell.py pruefen` ordnet jeden
Prüfpunkt danach ein, wie C dorthin kam:

| Start | Prüfpunkte | direkt nach einer C0-Wende | am Ende eines Durchlaufs S1 | mit `111` |
|---|---:|---:|---:|---:|
| A | 1.638.656 | 1.638.653 | 3 | 0 |
| D | 1.633.568 | 1.633.566 | 2 | 0 |
| C | 1.636.098 | 1.636.092 | 6 | 0 |

Alle Zahlen stimmen mit Teil 2 (C- und Rust-Programm) überein, ebenso die Schrittnummern der 11
Sonderfälle (hier jeweils um 1 größer, weil C einen Schritt nach B/D gezählt wird).

**Die 11 Sonderfälle am linken Ende:** In allen 11 Fällen beginnt der Durchlauf S1 am linken Bandende und
läuft über `100`-Blöcke, bis rechts davon die Bits `1100` folgen, also der Trenner `<1>`. Dort steht C vor
`11` mit einer 0 danach. Die Stelle liegt 14 Zellen (8 Fälle) oder 26 Zellen (3 Fälle) vom linken Ende
entfernt; das Band links davon ist jeweils `0 011 011 0 011 011` bzw. `0 011 011 0 011 011 011 011 011`, rechts
davon steht `11 001 001 001 0…` (also `<1>`, dann reguläre Abstände). Alle 11 Fälle so geprüft. Eine eigene
Regel braucht das linke Ende im Durchlaufmodell nicht: dort wirken dieselben drei Regeln, nur meist E.

Der Einordner selbst hat keine eigene Negativkontrolle; seine Summen stimmen aber mit den unabhängig
gezählten Werten aus C und Rust überein.

## 3. Vorschlag: die Aussage der Beschleunigung in Worten (zur Freigabe)

**Zustandstyp S:** `(q, Seite, L, R)` wie in Abschnitt 2, Blockzahlen n ≥ 1 (in Rocq als `n+1`
gespeichert, damit es keinen leeren Block gibt).

**encode:** Band = leeres Band links, dann L (unterstes Stück ganz außen), Kopf, R, leeres Band rechts;
der Kopf liest je nach Seite das oberste Bit von R oder von L.

**next:** S1, S2 oder E wie in der Tabelle. Bei E wird ein oberster Block zuerst in seine Bits zerlegt.
`next = Halt` genau dann, wenn q = A und das Bit am Kopf 1 ist.

**Start:** jeweils das leere Band, Kopf rechtsseitig, L = R = leer;
- 114: Tabelle 114 in Zustand A;
- 367: Tabelle 114 in Zustand D (367 ist Tabelle 114 umbenannt; Übertragung mit `Permute.v` aus busycoq,
  `perm_halts` erlaubt einen beliebigen Startzustand);
- 378: Tabelle 114 in Zustand C (378 ist das Spiegelbild der umbenannten Tabelle; Übertragung mit
  `Flip.v` und `Permute.v`).

**Satz (je Start):** Die Maschine hält vom leeren Band genau dann, wenn wiederholtes Anwenden von next ab
dem Startzustand irgendwann „Halt“ liefert.

**Bedingung H:** „A liest 1.“ Gleichwertig und einfacher zu lesen: „C steht rechtsseitig vor `111`“
(A wird nur über C1 → E1 erreicht). In Listensprache: Ein Rechtsdurchlauf von C endet an einer Bitfolge,
die mit `111` beginnt.

**Nachtrag 25.11.2026 (Auflage 1 von Justus): Die Haltebedingungen aus Teil 2 und Teil 3 sind gleichwertig.**
Teil 2: „B oder D liest 0, rechts davon steht `111`“. Teil 3: „C steht vor `111`“ (gleichbedeutend mit
„A liest 1“). An der Tabelle 114 (`1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC`) nachgerechnet:
- Halt gibt es nur bei A1. A wird nur über E1 (`1RA`) erreicht, E nur über C1 (`0RE`). Also hält die
  Maschine genau dann, wenn C eine 1 liest und die beiden Zellen rechts davon 1 und 1 sind: C vor `111`.
- C wird nur über drei Übergänge erreicht: B0 (`0RC`), D0 (`1RC`) und F1 (`0LC`).
- Über B0 und D0 geht der Kopf nach rechts; C liest dann die Zelle rechts der Zelle, auf der B oder D die
  0 gelesen hat. „C vor `111`“ heißt dort genau „B oder D liest 0 mit `111` rechts davon“.
- F1 schreibt eine 0 und geht nach links. Rechts von der Zelle, die C dann liest, liegt diese 0, also
  steht C nicht vor `111`; auf diesem Weg kein Halt.
- Ab dem Start (leeres Band) steht C ebenfalls nicht vor `111` (betrifft 378, Start in C).

Beide Bedingungen beschreiben also dieselben Halte-Zeitpunkte. Die Rocq-Datei
`rocq/gruppe1_durchlauf.v` braucht keine der beiden: dort ist „Halt“ einfach „next liefert keinen Zustand“,
und das tritt nur ein, wenn der Tabelleneintrag fehlt (A1). Details in `analyse/gruppe1_stufe1.md`.

**Zu beweisende Teile in Rocq** (Schritt 4, erst nach OK):
1. Definitionen und der allgemeine Satz „gültige Beschleunigung ⇒ Halten genau dann, wenn H erreicht“,
   nachgebaut nach cryptids, gegen `TM.v` am Pin.
2. Zwei Induktionslemmata für S1 und S2 (S2 mit der Paritätsfallunterscheidung).
3. Ein Lemma für E (alle 12 Einträge der Tabelle, mit Aufteilen eines Blocks).
4. Die drei Starts, für 367 und 378 über `Permute.v` und `Flip.v`.

**Was dieser Satz nicht leistet:** Er entscheidet nichts. Er ersetzt die Maschine durch ein Listensystem,
das etwa 54-mal weniger Schritte braucht, und legt die Werkzeuge an, auf denen eine gröbere Stufe (F, Z)
und eine Invariante aufbauen können.

**Regeln F und Z:** Sie fassen viele Durchläufe am rechten Ende zusammen (eine Fressrunde, ein ganzer
Zyklus) und wären Lemmata der Form „von Liste x | y … kommt das Durchlaufmodell zu x+4 | y−1 …“. Das ist
die zweite Stufe. F betrifft nur das rechte Ende und sollte sich auf den Regeln S1, S2, E aufbauen lassen.
Dafür muss ich die Konfiguration am Anfang einer Fressrunde vollständig hinschreiben; das ist noch nicht
gemacht.

## 4. Was weiter offen ist: die Pendelphasen

Beim Lauf nach links (nach der Fressphase) arbeitet die Maschine in Phasen (beobachtet bei Start A, Schritt
214.000 bis 218.000, nicht als Regel geprüft):
- In jeder Phase wird ein weiteres Element der Liste um 2 erhöht (im Beispiel 8 → 10), und der Vorrat am
  rechten Rand sinkt um 2.
- Innerhalb einer Phase läuft eine kleine Störung im Zickzack über alle schon erhöhten Elemente; jeder
  Zickzack ist ein Prüfpunkt (Art 1). Deshalb wächst die Zahl der Prüfpunkte etwa quadratisch.

Für die Stufe F/Z und erst recht für einen Nicht-Halte-Beweis müssten diese Phasen als Regeln stehen. Das
habe ich nicht geschlossen.

Ein Hinweis für später, **unbelegt** (nur Stichprobe: jeder 5.000. Makroschritt bis 10^8, Start A): Die
Trenner rechts vom Kopf waren nur `0`, `1`, `01`, `101`, `00`; keiner enthält `11`. Halten bräuchte rechts
einen Trenner mit `111` oder `11` vor einem `100`-Block. Wenn sich zeigen ließe, dass rechts nur endlich viele
harmlose Trenner vorkommen, wäre das eine Invariante in der Art von `Loop4Mono_v3.v`.

## Nachprüfen

```
gcc -O2 -o zp analyse/gruppe1/zweitpruefung.c
M=1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC
python3 -I analyse/gruppe1/teil3/sweepmodell.py 1000000000 liste A > a.txt   # ebenso D, C; je ca. 2 Min.
./zp $M 1000000000 liste A > b.txt
cmp a.txt b.txt
python3 -I analyse/gruppe1/teil3/sweepmodell.py 1000000000 pruefen A
./zp $M 3000000 liste A > b3.txt
SWEEP_FEHLER=paritaet python3 -I analyse/gruppe1/teil3/sweepmodell.py 3000000 liste A | cmp - b3.txt   # muss scheitern
SWEEP_FEHLER=s1_block python3 -I analyse/gruppe1/teil3/sweepmodell.py 3000000 liste A | cmp - b3.txt   # muss scheitern
```

## Abweichungen und eigene Fehler

- Auftrag war, das Listenmodell aus Teil 1 (Zyklusebene) zu vervollständigen. Geschlossen habe ich es auf
  der feineren Durchlaufebene. Die Zyklusebene (Phasen beim Lauf nach links) ist weiter offen. Ich halte
  die Durchlaufebene für die richtige Grundlage der Beschleunigung, weil nur dort jede Regel für alle
  Listen gilt.
- Erste Fassung des Modells: zwei Fehler, beide vom Vergleich gefunden. Ein Durchlauf S1 kann mit seinem
  letzten Schritt einen neuen Rechts-Rekord setzen; das fehlte (fehlende Zeile bei Schritt 145). Und die
  Spalte „lead“ war falsch berechnet. Beides behoben, danach byteweise gleich.
- Eine erste Negativkontrolle (`s1_kurz`) schlug nicht an, weil sie in Wahrheit keinen Fehler einbaute
  (sie ließ nur einen Block für später liegen). Ersetzt durch `s1_block`, die anschlägt.

## Offene Punkte

- Deine Freigabe der Aussage in Abschnitt 3 (oder Änderungswünsche), bevor Rocq beginnt.
- Stufe 2 (F, Z): Ausgangskonfiguration einer Fressrunde vollständig beschreiben.
- Pendelphasen als Regeln; Trenner-Invariante prüfen (Abschnitt 4).
