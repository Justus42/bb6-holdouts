# Analyse Gruppe 1, Teil 2: Haltebedingung, Invarianten, TM53, Beweisplan

Stand 25.11.2026. Nur Analyse, **kein Beweis**, keine Rocq-Arbeit. Baut auf `analyse/gruppe1.md` auf.
Neue Werkzeuge: `gruppe1/zweitpruefung.c` (erweitert, C) und `gruppe1/inv2` (Rust, unabhängig
geschrieben, Band als zwei Stapel statt als Array). Beide zählen dasselbe, Ergebnisse stimmen überein.

## Ergebnis in Kürze

- **Kein fertiger Beweisplan in Sicht.** Die Haltebedingung lässt sich genau angeben und hängt an einem
  kleinen, lokalen Muster. Es gibt aber keine einfache Invariante auf der Liste (Parität, Untergrenze), die
  sie ausschließt. Das gefährliche Muster steht sogar regelmäßig auf dem Band, nur nie an der Stelle, an der
  geprüft wird. Für einen Beweis braucht man ein Modell der einzelnen Pendelschwünge (etwa 21.000 pro Zyklus),
  nicht nur der Zyklen. Das ist ein Aufwand in der Größenordnung von `Loop4Mono_v3.v` (3.437 Zeilen); diese
  Schätzung ist **unbelegt**.
- **Haltebedingung:** Die Maschine hält genau dann, wenn B oder D eine 0 liest und rechts davon `111` steht.
  Dieser „Prüfpunkt“ kommt bis 10^9 Schritte rund 1,6 Mio. Mal je Start vor, nie mit `111`.
- **Zwei Arten von Prüfpunkten:**
  1. Fast alle (alle bis auf 11) liegen direkt links einer Wende von rechts nach links, die durch C auf
     einer 0 ausgelöst wurde. Dann prüft die Maschine genau die zwei Zellen, die C beim Wenden rechts von sich
     hatte. Bestanden heißt: dort stand `10`. Es stand immer `100`.
  2. Die übrigen 11 (3 / 6 / 2 je Start) liegen am **linken Bandende**, jeweils genau 27 oder 39 Schritte
     nach einem Links-Rekord.
- **TM53** (`Loop4Mono.v`) beschreibt den ganzen Lauf als eine Folge `S0 n` mit nur **einem** Parameter und
  zeigt `S0 n → S0 (n+1)`. So eine geschlossene Form gibt es für Gruppe 1 nicht: die Zykluslisten sind
  unregelmäßig und für die drei Starts verschieden. Übertragbar sind höchstens die Werkzeuge (Signale, die über
  `(011)^a`-Wörter laufen), nicht die Invariante.
- **Für die Wahl der Gruppe:** Gruppe 1 ist teuer. Ich würde sie nicht zuerst nehmen, außer 318/518 sieht
  noch schlechter aus.

## 1. Haltebedingung

### Mechanisch aus der Tabelle (vollständig)

Tabelle 114: `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC`.

- Einziger Halteübergang ist A1. Nach A führt nur E1 (`1RA`), nach E nur C1 (`0RE`), nach C nur B0 (`0RC`)
  und D0 (`1RC`).
- Halt heißt also: B oder D liest an Stelle i eine 0 und geht nach rechts, dann stehen bei i+1, i+2, i+3
  drei Einsen (C liest 1, E liest 1, A liest 1).
- Steht bei i+3 eine 0, besucht die Maschine A und läuft normal weiter. Diese Stelle heißt hier
  **Prüfpunkt**: B oder D liest 0, rechts davon `11`. Halt genau dann, wenn an einem Prüfpunkt die dritte
  Zelle eine 1 ist.

### Gezählt bis 10^9 Schritte (C und Rust, Werte identisch)

| Start | Prüfpunkte | davon mit `111` | direkt nach C0-Wende bei i+1 | davon mit Wendekontext `100` | übrige |
|---|---:|---:|---:|---:|---:|
| A (114) | 1.638.656 | 0 | 1.638.653 | 1.638.653 | 3 |
| D (367) | 1.633.568 | 0 | 1.633.566 | 1.633.566 | 2 |
| C (378) | 1.636.098 | 0 | 1.636.092 | 1.636.092 | 6 |

Jeder Besuch in A (außer dem Start bei 114) folgt auf einen Prüfpunkt; A las bis 10^9 nie eine 1.

### Art 1: Prüfung direkt nach einer Wende

„C0-Wende bei i+1“ heißt: Die letzte Richtungsänderung von rechts nach links vor dem Prüfpunkt war C liest
0 an Stelle r = i+1 (schreibt 1, geht nach links).

Warum dann nur zwei Zellen zählen (einfaches Argument, kein Rechnerergebnis): Nach der Wende bei r läuft der
Kopf erst nur nach links, dann nur nach rechts bis zum Prüfpunkt i = r−1. Er kommt also nicht mehr an r und
nicht rechts davon vorbei. Zelle r ist 1 (von C0 geschrieben); r+1 und r+2 sind unverändert seit der Wende.
Der Prüfpunkt liest i+1 = r, i+2 = r+1, i+3 = r+2. Er besteht genau dann, wenn beim Wenden rechts von C
`1 0` stand.

In allen gezählten Fällen stand dort `1 0 0`. In der Listensprache: C läuft nach rechts über das umgedrehte
Band (1-dünn, Einsen im Abstand 3) und wendet an einem Trenner (Abstand 4, `1000`). Danach folgt der nächste
Block, der mit `100` beginnt. Halten würde verlangen, dass **direkt nach einem Trenner zwei Einsen
nebeneinander** stehen, in der Liste also: ein Trenner, unmittelbar gefolgt von einem Abstand 1. Diese
Übersetzung ist aus den Kontexten abgelesen, nicht als eigene Zählung geprüft.

### Art 2: Prüfung am linken Ende

Die 11 übrigen Prüfpunkte liegen 9 bzw. 21 Zellen **rechts** der letzten Wende, also in einem Bereich, den die
letzte Wende nicht vorbereitet hat. Alle 11 kommen genau 27 oder 39 Schritte nach einem Links-Rekord (Start A:
Schritt 562.485, 559.898.637, 622.882.905; Start C: 3.686, 24.027.486, 79.105.789, 86.494.324, 205.293.587,
219.974.800; Start D: 845.547, 187.085.359). Ein Beweis muss das linke Ende also gesondert behandeln.

## 2. Invarianten

Geprüft an jedem Rechts-Rekord in Zustand C (12.384 / 12.340 / 12.220 Stück je Start) auf der Liste der
Nullabstände (wie in Teil 1). Zweimal unabhängig gezählt: Python aus den Listen des C-Programms und das
Rust-Programm direkt am Band.

| Kandidat | Ergebnis bis 10^9, alle drei Starts | taugt zum Ausschließen des Haltens? |
|---|---|---|
| I1: alle Nullabstände in {1, …, 5} | gilt, 0 Verletzungen | nein, allein zu schwach |
| I2: nie zwei Abstände < 3 direkt nebeneinander | gilt, 0 Verletzungen | nein, allein zu schwach |
| „nie Trenner direkt vor Abstand 1“ | **gilt nicht**: 1.344 / 1.213 / 2.455 Vorkommen | wäre die passende Aussage, ist aber falsch, wenn man sie fürs ganze Band verlangt |
| Parität (Elemente zwischen zwei Trennern gerade) | **gilt nicht**, z. B. 852 ungerade Elemente zwischen zwei regulären Trennern abseits des rechten Randes (Start A) | nein |
| Untergrenzen, Monotonie der Elemente | nicht weiter untersucht: die Prüfung hängt an Abständen direkt nach Trennern, nicht an der Größe der Elemente | – |

Wo das gefährliche Muster steht (Start A): meist am rechten Rand (Ende der Fressphase, `x <1> 0 |`) und in
der Gegend des linken Endes (Trenner 16–41 von rechts, Formen wie `1 <1> 0 | 0`). Es steht also auf dem Band,
aber nicht dort, wo C gerade wendet. Eine Invariante müsste deshalb sagen, **an welcher Stelle** der
Pendelbereich gerade liegt. Das geht nur mit einem Modell der einzelnen Schwünge.

Abstände insgesamt (Start A, alle C-Rekorde): Abstand 3: 75.095.535; 4: 2.139.894; 1: 9.308; 5: 5.439;
2: 141.

## 3. Listenmodell: was fehlt

Teil 1 beschreibt einen Zyklus mit zwei Regeln (Fressen, x = a+4b+7). Der lange Lauf nach links ist aber
**kein einzelner Durchlauf**. Er besteht aus vielen Pendelschwüngen mit wandernden Wendepunkten. Pro
Schwung gibt es einen Prüfpunkt, im Mittel etwa 1,64 Mio. / 77 Zyklen ≈ 21.000 pro Zyklus (Start A).
Momentaufnahmen dazu habe ich angesehen (Schritt 214.077 bis 326.002): der Vorrat x am rechten Rand nimmt
in kleinen Schritten ab, während die Wendepunkte nach links wandern.

Das linke Ende und die Sonderstellen (`<1>`, `<2>`, `<5>`) habe ich **nicht** in Regeln gefasst. Für die
Haltefrage reicht das Zyklusmodell nicht, also hätte das Ergänzen allein nicht geholfen. Nötig wäre zuerst das
Schwungmodell. Erst daran lässt sich die Aussage „C wendet nur an Trennern, auf die `100` folgt“ beweisen.

## 4. TM53 in `Loop4Mono.v` (v1)

Maschine `1LB0RB_1LC1RE_0RD0LF_1RA1RD_1LF0RA_---0LB`, etwa 200 Zeilen, Urteil „hält nicht“.

- **Werkzeuge:** Die Bibliothek `Longitudinal` aus busycoq. Ein „Signal“ ist ein Zustand mit festem
  Nachbarstück (`hL := (C,[1])`, `hR := (B,<[0])`, zweite Sorte `hL'`, `hR'`). Lemmas der Form `segRLs` und
  `sideRLs` sagen: Läuft eine Folge von Signalen über ein Wort, kommt eine bestimmte Folge heraus und das
  Wort ändert sich so. Wörter: `D1 a b`, `D2 a b` mit `(0111)^…` und `DH1 a b` mit `(011)^a`.
- **Invariante:** Keine Eigenschaft einer allgemeinen Liste, sondern eine **geschlossene Formel**: Der Lauf
  erreicht `S0 0`, und für jedes n gilt `S0 n →+ S0 (n+1)` (Lemma `BigStep`). `S0 n` ist durch die eine
  Zahl n vollständig bestimmt. Nicht-Halten folgt mit `progress_nonhalt_simple`.
- **Übertragbar?** Die Invariante nicht. Bei Gruppe 1 sind die Zykluslisten unregelmäßig (z. B.
  `… 14 | 0 | 2 | 0 | 2 | 2 …`), wachsen in der Länge und unterscheiden sich zwischen den drei Starts. Eine
  Ein-Parameter-Formel ist nicht in Sicht. Die Werkzeuge vermutlich schon: TM53 lässt Signale über
  `(011)^a`-Wörter laufen, genau die Wortform von Gruppe 1. Ob die Signale von Gruppe 1 so einfach sind, ist
  **nicht geprüft**.
- **Bessere Vorlage für unregelmäßige Listen:** `Loop4Mono_v3.v`. Dort ist die Invariante (`boundary_inv`)
  eine Eigenschaft aus endlich vielen „Kontexten“ und Ketten, die per Rechnung geprüft wird
  (`context_certificate`). Das passt zu der Lage hier: eine Bedingung, die nur am Pendelbereich gelten muss.
  Auch hier: gelesen, nicht nachgebaut.

## 5. Beweisplan in Worten (Skizze, nicht ausgearbeitet)

Ein Beweis, dass Gruppe 1 nicht hält (falls das stimmt; offen), bräuchte nach meinem Stand:

1. Lokale Lemmas für das Durchlaufen von `(011)^a` und `(100)^a` in den Zuständen B/D, C, F (aus der
   Blocktabelle in Teil 1), mit `ES_v3`/`Longitudinal` wie in TM53.
2. Ein Schwungmodell: Konfiguration = Liste plus Lage der beiden Wendepunkte und des Vorrats x; Regeln für
   einen Schwung.
3. Eine Invariante in der Art von v3: Endlich viele erlaubte Formen um den Pendelbereich herum, darunter
   „auf jeden Trenner im Pendelbereich folgt ein regulärer Block“. Sie muss unter Schwung, Fressphase und den
   Ereignissen am linken Ende erhalten bleiben.
4. Die drei Starts getrennt bis in eine Konfiguration führen, in der die Invariante gilt.

Schritt 2 und 3 sind offen, und ich sehe noch nicht, wie die Invariante genau lauten muss. Deshalb: **kein
Plan in Sicht**, nur eine Richtung.

## 6. Nachprüfen

```
gcc -O2 -o zp analyse/gruppe1/zweitpruefung.c
(cd analyse/gruppe1/inv2 && cargo build --release)
M=1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC
./zp $M 1000000000 - A          # ebenso D, C; je ca. 7 s
analyse/gruppe1/inv2/target/release/inv2 $M 1000000000 A
./zp $M 1000000000 liste A > a.txt && python3 -I analyse/gruppe1/gruppe1.py abstaende a.txt
python3 -I analyse/gruppe1/gruppe1.py negativ a.txt
```

**Negativkontrollen** (alle schlagen an):
- Prüfpunkt-Zähler: Testmaschine `1RB1LB_1RC1RC_1RD1RD_1LE1LE_1LF1LF_1LA1LA` erzeugt B liest 0 vor `111`;
  beide Programme melden 8 Prüfpunkte mit `111` (in 100 Schritten).
- I1 (Rust): `1RB---_1RC---_1RD---_1RE---_1RF---_0RA---` (Nullen im Abstand 6): 120 Verletzungen.
- I2 (Rust): `1RC---_1RC---_0RD---_0RE---_0RC---_1RA---` (Nullen nebeneinander): 1.650 Verletzungen.
- I1, I2 (Python, `gruppe1.py negativ`): Listendatei mit eingefügtem `<7> 0 <1> 0 <1>`: je 1 Verletzung statt 0.
- Der Zähler „direkt nach C0-Wende“ hat keine eigene Kontrolle. Er zeigt aber in echten Läufen Ausnahmen
  (11 Stück), schlägt also nicht immer gleich aus.

## Abweichungen und eigene Fehler

- Meine erste Vermutung war falsch: dass jeder Prüfpunkt an einer Stelle liegt, die der Kopf seit einer
  C0-Wende **bei i+3** nicht mehr besucht hat (0 von 19.369 Fällen). Richtig ist: Wende bei i+1.
- Im Rust-Programm stand zunächst eine wirkungslose Zeile (Einfügen und sofortiges Entfernen am Stapel);
  entfernt, Ergebnisse unverändert.
- Die Lage des gefährlichen Musters (rechter Rand, linkes Ende) habe ich nur für Start A ausgezählt.

## Offene Punkte

- Schwungmodell und Invariante (Abschnitt 5, Schritte 2 und 3).
- Die 11 Prüfpunkte am linken Ende einzeln verstehen.
- Ob Gruppe 1 überhaupt nicht hält, ist offen; nichts hier spricht für Halten.

## Empfehlung

**Abbrechen für jetzt** bzw. zurückstellen, bis 318/518 bewertet ist. Gruppe 1 braucht ein eigenes
Schwungmodell und eine v3-artige Invariante. Das ist viel Arbeit ohne Gewissheit, dass am Ende ein Beweis
steht.
