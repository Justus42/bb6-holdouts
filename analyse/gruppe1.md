# Analyse Gruppe 1: n=114, 367, 378 (Monotone list)

Stand 25.11.2026. Nur Simulation und Beschreibung. Es wurde **kein Beweis** geführt und nichts
über Halten oder Nicht-Halten entschieden. Werkzeuge: `analyse/gruppe1/gruppe1.py` (Python) und
`analyse/gruppe1/zweitpruefung.c` (C, unabhängig geschrieben). busycoq-Pin `33209bc7`.

## Ergebnis in Kürze

1. **Eine Maschine, drei Starts.** 367 und 378 sind die Tabelle von 114, nur umbenannt (378 zusätzlich
   gespiegelt) und in einem anderen Zustand gestartet: 367 = Tabelle 114 ab Zustand D, 378 = Spiegelbild
   von Tabelle 114 ab Zustand C. Schritt für Schritt geprüft (1 Mio. Schritte je Maschine). Die drei Läufe
   **verschmelzen nicht**: bis 10^9 Schritte hat keiner einen Rechts-Rekord mit derselben Liste wie ein
   anderer. Ein Beweis für eine Maschine deckt die anderen also nicht automatisch ab.
2. **Verhalten als Liste.** Das Band ist fast überall dreiperiodisch (`011011…` bzw. `100100…`); dazwischen
   liegen einzelne Stellen mit Abstand 4. Liest man die Abstände als Trenner, ist das Band eine Liste von
   Zahlen. Die Maschine arbeitet in Zyklen: rechts „frisst“ ein Zähler das Nachbarelement, dann läuft der
   Kopf weit nach links und zurück und erhöht dabei Elemente um 2. Zwei Regeln sind bis 10^9 Schritte
   ausnahmslos bestätigt (siehe unten), der Rest ist Beobachtung.
3. **Halten** ist nur über den Übergang A1 möglich, und A wird nur über C1 → E1 erreicht. Die Maschine hält
   also genau dann, wenn Zustand C nach rechts laufend auf **drei Einsen in Folge** trifft. Im beobachteten
   Lauf kommt das nicht vor. Ob es je vorkommt, ist offen.
4. **Warum Loop4Mono v2–v6 diese Maschinen nicht entscheiden:** Jede dieser Dateien beweist nur die
   Maschinen, deren Tabelle sie fest einträgt (`TM_from_str "…"`), plus deren Spiegel/Umbenennung. Keine der
   Tabellen dort gehört zu Gruppe 1 (geprüft). Es gibt im Pin keinen allgemeinen Entscheider, der auf
   114/367/378 „nicht angeschlagen“ hätte. Auch inhaltlich passt keine dieser Dateien direkt: v2–v6 und
   PR_Loop4Mono arbeiten mit Wörtern der Periode 2 oder 4 (`10`, `11`, `0011`), Gruppe 1 hat Periode 3.
   Näher liegt ein Modul aus der älteren Datei `Loop4Mono.v` (v1, nicht im Auftrag): TM53 arbeitet mit
   `(011)^a` und hat dieselbe Art von Durchläufen (`100 → 011` nach rechts, `011 → 100` nach links).

## 1. Gleiche Tabelle, verschiedene Starts

| n | Maschine | Bezug zu Tabelle 114 |
|---|---|---|
| 114 | `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC` | selbst, Start A |
| 367 | `1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB` | umbenannt (A..F bei 114 = E C B A D F dort), ungespiegelt, Start = Zustand D von 114 |
| 378 | `1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---` | umbenannt (A..F bei 114 = F D A B C E dort), gespiegelt, Start = Zustand C von 114 |

- Zuordnung selbst gesucht (alle 720 Umbenennungen × Spiegelung), stimmt mit `data/vorlagen.md` überein.
- `gruppe1.py aequivalenz`: Zustand und Kopfposition in jedem der ersten 1.000.000 Schritte gleich, Band alle
  100.000 Schritte gleich.
- Verschmelzen: Rechts-Rekorde in Zustand C (Liste wie in Abschnitt 2) der Läufe ab A, C, D bis 10^9
  Schritte verglichen: keine gemeinsame Liste außer der trivialen ganz am Anfang.

Ab hier wird nur Tabelle 114 betrachtet; „Start D“ steht für 367, „Start C“ für 378 (gespiegelt).

## 2. Verhalten als Regeln

### Lokale Bausteine (vollständig, durch Durchprobieren aller 3er-Blöcke)

Die wichtigsten Durchläufe (`gruppe1.py bloecke` listet alle):

- nach rechts: `C> 100 → 011 C>` (Zustand C läuft über `100` und macht daraus `011`)
- nach links: `011 <B → <D 100` und `011 <D → <B 100` (B und D wechseln sich ab)
- An einer Stelle mit Abstand 4 (`1000` bzw. `0111`) laufen diese Zustände **nicht** durch, dort kehrt der
  Kopf um oder wechselt in andere Zustände.

Folge: Jeder weite Lauf über das Band **vertauscht 0 und 1** im überquerten Stück. An den Rekorden rechts
(Zustand C) sieht das Band so aus: wenige Nullen im Abstand 3, z. B. `1011101110110110…`; an den Rekorden
links (Zustand B) umgekehrt.

### Listenform

Liest man an einem Rechts-Rekord in Zustand C die Abstände zwischen aufeinanderfolgenden Nullen von rechts
nach links, so sind fast alle Abstände 3. Gezählt wird, wie viele 3er-Abstände zwischen zwei Abständen
anderer Länge liegen; `|` = Abstand 4, `<g>` = Abstand g. Beispiel (Start A, Schritt 326.002):

```
10 | 10 | 10 | 10 | 10 | 10 | 10 | 12 | 18 | 4 | 6 | 4 | 6 | 6 | 6 | 4 | 2 | 4 | 4 | 4 | 4 | 4 | 14 | 0 | 2 | 0 | 2 | 2 | 2 | 2 | 2 | 4 | 0
```

Links steht das rechte Bandende. Python und C erzeugen diese Listen unabhängig voneinander; für die ersten
3·10^6 Schritte sind die Ausgaben bytegleich, für alle drei Starts.

### Ein Zyklus

Am Anfang eines Zyklus seien `a` das rechteste und `b` das nächste Element.

1. **Fressphase** (Regel F, bestätigt): Der Kopf pendelt nur im rechten Teil des Bandes hin und her.
   Mit `x` = rechtes Element und `y` = Nachbar gilt pro Runde (drei Rechts-Rekorde, 9 neue Zellen):
   `x | y  →  x+2 <1> y  →  x+3 <1> y  →  x+4 | y−1`. Der Rest der Liste bleibt unverändert.
   Nur die erste Runde eines Zyklus sieht anders aus.
2. **Ende der Fressphase** (Regel Z, bestätigt): Wenn `y` aufgebraucht ist, gilt **x = a + 4b + 7**.
3. **Weiter Lauf nach links und zurück** (Beobachtung, nicht als Regel geprüft): Danach sind die nächsten
   Elemente jeweils um genau 2 größer. Die Zahl der so erhöhten Elemente liegt nahe x/2 (siehe Zählung
   unten). Das passt zu der Lesart, dass `x` nach links getragen wird und jedem Element 2 abgibt, bis es
   aufgebraucht ist; ein Rest wird am linken Ende zu neuen Elementen (meist `0`, `2`) oder zu einer
   Sonderstelle (`<1>`, `<5>`). Diese Lesart ist **unbelegt**; die Regeln am linken Ende und an
   Sonderstellen (z. B. das Zusammenfassen zu `14`) habe ich nicht ausgearbeitet.

Damit wirkt die Liste wie eine Warteschlange: rechts werden pro Zyklus zwei Elemente verbraucht, links
entstehen neue, und jedes Element wird bei jedem Durchlauf, der es erreicht, älter (um 2 größer).

### Zählungen (bis 10^9 Schritte, Listen aus dem C-Programm, geprüft mit `gruppe1.py pruefe`)

| Start | Zyklen | Regel F: Runden passend / nicht passend | davon erste Runde eines Zyklus | Regel Z passend / abweichend |
|---|---:|---:|---:|---:|
| A (114) | 77 | 3938 / 79 | 77 | 76 / 0 |
| D (367) | 78 | 3922 / 80 | 78 | 77 / 0 |
| C (378) | 77 | 3884 / 79 | 77 | 76 / 0 |

Die zwei übrigen Abweichungen bei Regel F liegen ganz am Anfang des Laufs (Schritt 2.983 und 8.746 bei
Start A). Regel Z hat eine Prüfung weniger als Zyklen, weil der erste Zyklus kein vollständiges Paar hat.

Weitere Zahlen, Start A, bei 10^9 Schritten: Bandbreite 37.620, Listenlänge zuletzt etwa 260, x zuletzt
450–490. Die Zahl der um 2 erhöhten Elemente minus x/2 (abgerundet) liegt zwischen −30 und +1; in 23 von
76 Zyklen ist sie genau +1. In 24 von 76 Zyklen ist x/2 mindestens so groß wie die Listenlänge, dann reicht
der Übertrag bis ans linke Ende.

Kein Halt bis 10^9 Schritte, für alle drei Maschinen mit ihrer eigenen Tabelle, bestätigt von zwei
Programmen: `zweitpruefung.c` und `sim2_rust` aus dem Repo (Einsen bei 10^9: 24.044 / 23.195 / 20.324).
slugbird gibt 1,6·10^14 bzw. 2,0·10^14 simulierte Schritte an; meine Läufe gehen nicht darüber hinaus.

### Haltebedingung

- Einziger Halteübergang: A1. Nach A führt nur E1 (`1RA`), nach E nur C1 (`0RE`).
- Also: Halt genau dann, wenn C auf einer 1 steht, rechts davon eine 1 und rechts davon noch eine 1 liegt.
- In den ersten 3·10^6 Schritten wurde A 19.370-mal betreten und las jedes Mal 0. A steht dabei immer an
  der Grenze zwischen schon umgedrehtem und noch nicht umgedrehtem Band (`…101[0]0100…`).
- Ich habe zusätzlich 320 Abwandlungen einer Zyklusliste laufen lassen (288-mal eines der 24 linken
  Elemente auf 0–11 gesetzt, 600.000 Schritte; 32-mal eines der beiden rechten auf 0–15, 400.000 Schritte): kein Halt. Das ist nur eine Stichprobe, kein Hinweis in die eine oder
  andere Richtung.

## 3. Vergleich mit `PR_Loop4Mono.v`

| | PR_Loop4Mono (n=652, 950; hält) | Gruppe 1 (114, 367, 378; offen) |
|---|---|---|
| Wachstum | nach links | 114 und 367 nach rechts, 378 nach links (Spiegel) |
| Wort | `W(e) = (10)^e`, Periode 2, Trenner 0 oder 1 | `(011)^e` bzw. `(100)^e`, Periode 3, Trenner = Abstand 4 |
| Band nach Durchlauf | Elemente bleiben gleich („passive“ Elemente werden unverändert überquert) | 0 und 1 werden vertauscht; Elemente werden um 2 größer |
| Zähler | `x0` vorne in der Liste | `x` am wachsenden Ende, frisst das Nachbarelement (Regel F, Z) |
| Übertrag | gerades Element wird über passive getragen, +8 je Element (`FF`) | vermutlich: `x` wird nach links getragen, +2 je Element (unbelegt) |
| Halten | F1; durch Rechnen im Listenmodell (`check`, 1.307.718 Takte) bis zu einem Haltefenster | A1 nur über `C> 111`; ob es eintritt, ist offen |
| Zweite Maschine | Spiegel-Zwilling, Start C; eigener Startrekord `init_C`, gleiches Listenmodell | zwei weitere Starts derselben Tabelle; Läufe verschmelzen nicht |

Gemeinsam ist die Bauart: Band = Liste von Zahlen, ein Zähler, weite Durchläufe, die die Liste gleichmäßig
verändern. Die Datei nutzt `ES_v3` für die lokalen Lemmas und ein Listenmodell mit `native_compute`.
Übertragbar wäre höchstens dieser Aufbau, nicht ein einziges Lemma: alle Lemmas (`skipR`, `headerR`,
`carryA` …) hängen an Wörtern der Periode 2 und an der Tabelle von TM1.

## 4. Warum die Loop4Mono-Fassungen im Pin diese Maschinen nicht entscheiden

**Formal (geprüft):** `gruppe1.py pin` liest alle Tabellen aus `TM_from_str "…"` und vergleicht sie unter
allen Umbenennungen und Spiegelung mit Gruppe 1.

| Datei | Maschinen (6 Zustände, 2 Symbole) | davon Gruppe 1 | Urteil laut Datei |
|---|---:|---:|---|
| `Loop4Mono.v` (v1) | 52 | 0 | hält nicht |
| `Loop4Mono_v2.v` | 2 | 0 | hält nicht |
| `Loop4Mono_v3.v` | 2 | 0 | hält nicht |
| `Loop4Mono_v4.v` | 2 | 0 | hält nicht |
| `Loop4Mono_v5.v` | 1 | 0 | hält nicht |
| `Loop4Mono_v6.v` | 2 | 0 | hält |
| `PR_Loop4Mono.v` | 2 | 0 | hält |

Jede Datei beweist Aussagen der Form `~halts tm c0` oder `halts tm c0` für ihre fest eingetragenen
Tabellen. v2 und v3 enthalten Hilfssätze zur Umbenennung, aber nur zwischen ihren eigenen Maschinen. Es gibt
also nichts, was auf 114/367/378 hätte „angewendet“ werden können. Die Frage „warum entscheiden sie diese
Maschinen nicht“ hat damit eine schlichte Antwort: Sie wurden für andere Tabellen geschrieben.

**Inhaltlich (gelesen, nicht gebaut):** Die Wortfamilien der Dateien:

| Datei | Wörter |
|---|---|
| v1 | 52 Module mit verschiedenen Wörtern, meist Periode 1, 2 oder 4 (`1^n 0001`, `(10)^n`, `(0111)^a`); in 7 Modulen (TM35, 36, 37, 44, 45, 51, 53) auch Periode 3, z. B. `(011)^a`, `(111)^n` |
| v2 | `011 (0011)^n`, `111 (0011)^n`, `11 (0011)^n`, Periode 4 |
| v3 | `01010 (1010)^n`, `010 (1010)^n`, Periode 2 |
| v4, v5 | `011 (11)^n`, `01 (11)^n`, Periode 2 |
| v6 | `001 (11)^n`, `0011 (11)^n`, `01 (11)^n`, `011 (11)^n`, Periode 2; Listenmodell als Warteschlange („strict FIFO model“) |
| PR_Loop4Mono | `(10)^e`, Periode 2 |

Gruppe 1 braucht `(011)^n` mit Periode 3 und zusätzlich das Vertauschen von 0 und 1 bei jedem Durchlauf.
v2–v6 und PR_Loop4Mono haben keine Wörter dieser Form. Vom Ablauf her kommt v6 am nächsten: auch dort ein
Listenmodell als Warteschlange, das bis zum Halten gerechnet wird.

Nachtrag außerhalb des Auftrags: In `Loop4Mono.v` (v1) hat **TM53** (`1LB0RB_1LC1RE_0RD0LF_1RA1RD_1LF0RA_---0LB`,
etwa 200 Zeilen, „hält nicht“) Wörter `(011)^a` und dieselben vertauschenden Durchläufe wie Gruppe 1
(`A> 100 → 011 A>`, `011 <C → <C 100`; ermittelt mit derselben Blockrechnung wie oben). Gruppe 1 hat
mit TM53 keine gleiche Tabelle. Ob TM53 als Vorlage taugt, habe ich **nicht** geprüft.

## 5. Wie nachprüfen

```
python3 -I analyse/gruppe1/gruppe1.py aequivalenz
python3 -I analyse/gruppe1/gruppe1.py bloecke
python3 -I analyse/gruppe1/gruppe1.py pin <busycoq-Checkout @33209bc7>/verify
gcc -O2 -o zp analyse/gruppe1/zweitpruefung.c
./zp 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC 1000000000 liste A > a.txt   # ebenso D, C; je ca. 7 s
python3 -I analyse/gruppe1/gruppe1.py pruefe a.txt
python3 -I analyse/gruppe1/gruppe1.py liste 3000000 A | cmp - <(./zp 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC 3000000 liste A)
python3 -I analyse/gruppe1/gruppe1.py negativ a.txt
```

SHA-256 der Listendateien bis 10^9 (nicht eingecheckt, je etwa 10 MB): Start A `ad12c4ba…21d5`,
Start C `8f8f7f91…d602`, Start D `03cc3a7f…963d`.

**Negativkontrollen** (`gruppe1.py negativ`), alle schlagen an:
- Äquivalenz mit absichtlich geändertem Übergang bei 367 (D0 `1RA` → `0RA`): keine Umbenennung gefunden,
  Schrittvergleich weicht bei Schritt 18 ab.
- Listendatei mit einer um 1 veränderten Zahl mitten in einer Fressrunde: Regel F meldet eine Runde mehr als
  nicht passend (bei 3·10^6 Schritten 183/17 statt 184/16).
- Gruppensuche mit einer Testdatei, die 378 enthält: findet 1 Treffer.

## Abweichungen und eigene Fehler

- Meine erste Negativkontrolle für Regel F schlug **nicht** an: die veränderte Zeile lag in der ersten
  Runde eines Zyklus, die ohnehin als „nicht passend“ zählt. Korrigiert: jetzt wird eine Zeile mitten in
  einer regulären Runde verändert.
- Die Erkennung „Zyklusanfang“ ist eine Faustregel (großer Zeitsprung zwischen zwei Rechts-Rekorden). Sie
  trifft in allen geprüften Läufen; bewiesen ist sie nicht.
- Ich habe zusätzlich einen beschleunigten Simulator (Blöcke mit Lauflängen) gebaut und gegen die direkte
  Simulation geprüft, ihn aber für keine Aussage hier verwendet und nicht eingecheckt.

## Offene Punkte

- Regeln für den Durchlauf nach links vollständig machen: linkes Ende, Sonderstellen `<1>`, `<2>`, `<5>`,
  Zusammenfassen von Elementen. Erst dann gibt es ein vollständiges Listenmodell.
- Mit einem vollständigen Listenmodell viel weiter rechnen als 10^9 Schritte und nach `C> 111` suchen.
- `Loop4Mono.v`, Modul TM53, als mögliche Vorlage lesen (Periode 3, gleiche Art von Durchläufen).
- Ob jemand in #bb6 an diesen Maschinen arbeitet (slugbird: Status „rules“, also Regeln bekannt), ist
  ungeklärt.

## Empfehlung

**Weiter, aber nur als Analyse und erst nach Klärung in #bb6.** Das Verhalten ist regelmäßig und lässt sich
als Liste beschreiben; zwei Regeln halten ausnahmslos. Für einen Beweis fehlt noch das vollständige
Listenmodell, und ob die Maschinen halten, ist offen. Ein Beweis wäre nach Aufbau eher ein eigenes Projekt
in der Art von PR_Loop4Mono oder v6 als eine Anpassung einer vorhandenen Datei.
