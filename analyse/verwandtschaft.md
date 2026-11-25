# Verwandtschaftskarte der BB(6)-Holdouts

Thread „Verwandtschaftskarte“, 25.11.2026. Nur Analyse, kein Rocq. Daten: Liste mxdys vom 30.10.2026
(608 Maschinen), `data/holdouts.json` (Stand 10.11.2026) mit den 695 Äquivalenten aus mxdys'
Äquivalenzgruppen und 846 decided. Alles ist ein Schnappschuss.

## Ergebnis in drei Sätzen

376 der 608 Holdouts haben mindestens einen Verwandten in der Liste; sie bilden 141 Familien (72 mit 2,
48 mit 3, 18 mit 4, 2 mit 5 Maschinen, eine mit 6), fast alle sind „gleiche Tabelle, anderer Start“. Echte
Rückführungen auf eine kleinere Maschine oder Gleichschritt gibt es nur in wenigen Familien; neben M5
(274/318/322/518) ist die wichtigste neue Familie {88, 312, 396, 449}: nach dem Zusammenlegen des
Haltezustands stimmen ihre 5-Zustands-Tabellen bis auf den Übergang E1 überein (**nicht** dieselbe
5-Zustands-Maschine; Korrektur 25.11., siehe F12), 88/312 laufen beweisbar im Gleichschritt, 88/312/449 sind
laut busycoq-PR #59 (offen) haltend, 396 ist der einzige ohne PR. Keine der 510 Paarungen „gleiche Tabelle“ führt zu Läufen, die verschmelzen
(geprüft bis 10^6 Schritte je Lauf); aus der Karte folgt also keine Entscheidung, nur Bündelung.

Die 608 Holdouts haben **403 verschiedene Tabellen** bis auf Umbenennung der Zustände und Spiegelung
(Start nicht berücksichtigt; ohne Spiegelung 498). Zwei Verfahren stimmen überein (Nachtrag 25.11.,
siehe Abschnitt 4).

Dateien: [`data/verwandtschaft.csv`](../data/verwandtschaft.csv) (647 Paare),
[`analyse/verwandtschaft/familien.tsv`](verwandtschaft/familien.tsv) (141 Familien),
englische Kurzfassung [`analyse/verwandtschaft_en.md`](verwandtschaft_en.md).

## 1. Was schon erfasst ist

| Quelle | Stand | Verwandtschaften zwischen zwei Holdouts |
|---|---|---|
| busycoq `verify/Eqv*.v` am Pin `33209bc7` (9 Dateien, 3.596 Sätze `eqv: halts tm c0 <-> halts tm' c0`) | Pin | **keine**. 236 Sätze betreffen einen Holdout, aber immer zusammen mit einer Maschine außerhalb der Liste (165-mal eine Äquivalente desselben Holdouts laut mxdys, 71-mal eine Maschine, die in unseren Daten nicht vorkommt). Kein Satz verbindet zwei Holdouts oder Holdout und decided. Werkzeug: `analyse/verwandtschaft/eqv_pin.py`, Ausgabe `eqv_pin.tsv`. |
| cryptids `BusyBeaver/BB6/Equivalences.lean` (Commit `f01ee56`, 25.11.2026) | aktuell | **keine**. Ein einziger Satz: 470 ⟺ `…_---1LC`; das ist mxdys' Äquivalente 470.2, also dieselbe Gruppe. In Kommentaren nennt cryptids einzelne „macro twins“ und „structural twins“, ohne Beweis. |
| mxdys' Äquivalenzgruppen (in `holdouts.json`, Feld `aliases`) | 30.10. | 695 Äquivalente, keine davon ist selbst ein Holdout. Die Liste fasst also nur halte-äquivalente Maschinen zusammen, nicht „gleiche Tabelle, anderer Start“. |
| bbchallenge-Wiki, alle 247 Weiterleitungen (API, 25.11.) | aktuell | 4 Gruppen, in denen Holdout-Seiten auf einen anderen Holdout weiterleiten: {62, 212, 369, 377}, {185, 422, 441, 490, 538}, {23, 215, 288, 502}, {186, 317, 573}. Alle vier sind bei uns „gleiche Tabelle“. |
| eigene Analysen | 25.11. | `data/vorlagen.md`: {31,222} {114,367,378} {141,315} {274,518} {318,322}; `analyse/318_518*.md`: M5 = 274/318/322/518, 318/518 im Gleichschritt. |

Nicht geprüft: Discord (nur Justus), die Äquivalenzdatei von mxdys selbst (nur über `holdouts.json`).

## 2. Was gesucht wurde

Für jedes Paar aus 608 Holdouts, 695 Äquivalenten und 846 decided, bei dem mindestens ein Holdout
beteiligt ist und beide nicht schon in derselben mxdys-Gruppe liegen:

1. **tabelle**: gleiche Tabelle bis auf Umbenennung der Zustände, mit oder ohne Spiegelung, anderer Start.
   Die CSV sagt, ab welchem Zustand von n1 die Maschine n2 läuft.
2. **kern**: Zusammenlegen von Zuständen, wobei der Halteübergang als Joker zählt (er darf mit allem
   übereinstimmen). Für jedes Zustandspaar die kleinste gültige Zusammenlegung; Ergebnis ist eine kleinere
   Maschine (Kern). Zwei Maschinen sind verwandt, wenn ihre Kerne bis auf Umbenennung/Spiegelung gleich
   sind (Start egal). So entsteht M5 aus 318.
3. **gleichschritt**: ab Leerband Schritt für Schritt gleich, bis eine ihr Haltefeld erreicht. Beleg durch
   Tabellenvergleich (Produktautomat über alle symbolisch erreichbaren Zustandspaare); gilt dann für jede
   Schrittzahl.
4. Zusätzlich **verschmelzen**: Für jedes Tabellen- und Kern-Paar wurde geprüft, ob die beiden Läufe
   irgendwann dieselbe Konfiguration erreichen (dann wären sie ab da ein Lauf).
5. Zusätzlich **gleichschritt_beobachtet**: Programm B siebt alle Paare per Simulation (gleiche Folge von
   Schreiben/Richtung über 10^6 Schritte). Paare, die das schaffen, aber nicht per Tabellenvergleich belegt
   sind, wurden mit `divergenz.c` bis 10^9 Schritte nachgeprüft.

## 3. Ergebnisse

| Art | Paare mit Holdout | davon Holdout–Holdout |
|---|---|---|
| tabelle | 510 | 298 |
| kern | 113 | 35 |
| gleichschritt (belegt) | 17 | 2 (318/518, 88/312) |
| gleichschritt_beobachtet (**unbelegt**, nur bis 1e9 simuliert) | 7 Zeilen = 6 Paare | 4 |
| Läufe verschmelzen | 1 (274/322 im Kern M5, Schritt 25/11) | 0 bei „tabelle“ |

- **Kerne**: 69 Holdouts lassen sich auf eine 5-Zustands-Maschine zusammenlegen, immer über den
  Haltezustand (keine Maschine hat zwei gleichwertige Zustände ohne Halt). 306 und 461 haben je zwei Kerne.
- **Verschmelzen**: Keine der 510 Tabellen-Paarungen verschmilzt innerhalb von 10^6 Schritten je Lauf
  (Programm B; Programm A bis 10^5 gleich). Die einzige Verschmelzung ist die bekannte 274/322 in M5.
  Gleiche Tabelle heißt also hier fast immer: verschiedene Läufe, nicht dieselbe Haltefrage.
- **Klassen** der Community-Tabelle sind innerhalb der Familien einheitlich, mit einer Ausnahme
  (F54 = {217, 387, 417}: „Skelet 1-like Class 1“ und „Chaotic Ack-like Bell“). Das stützt die Suche,
  ist aber kein Beweis.

### Größte Familien

| Familie | Holdouts | Art | Klasse | Bemerkung |
|---|---|---|---|---|
| F1 | 244, 339, 489 · 279, 473, 598 | tabelle, kern, gleichschritt_beobachtet (unbelegt) | Chaotic Bell 1 | zwei fast gleiche Tabellen mit je drei Starts; 244↔279, 339↔473, 489↔598 bis 1e9 gleich (unbelegt). **Dieselbe Tabelle wie 244/339/489 ab ihrem eigenen Start ist d833, und d833 hält** (busycoq `ChaoticBell1Halt.v`). |
| F2 | 54, 200, 272, 545, 570 | tabelle | Chaotic Bell 3 | fünf Starts einer Tabelle |
| F3 | 185, 422, 441, 490, 538 | tabelle | Chaotic 1dCA-like | Wiki bekannt; cryptids hat eine Beschleunigung nur für 185 |
| F12 | 88, 312, 396, 449 | kern, gleichschritt | Shift-overflow counter | siehe unten |
| F20 | 274, 318, 322, 518 | kern, gleichschritt, tabelle | SO structural counter | M5, bekannt |
| F11 | 69, 166, 391, 543 | tabelle, gleichschritt_beobachtet (unbelegt) | Skelet 1-like | 69↔543 und 166↔391 bis 1e9 gleich (unbelegt) |
| F16 | 147, 190, 277, 394 | tabelle, gleichschritt_beobachtet (unbelegt) | Shift-overflow counter | 190↔394 bis 1e9 gleich (unbelegt; Bandbreite nur 163) |

Vollständige Liste: `analyse/verwandtschaft/familien.tsv`.

### F12 = {88, 312, 396, 449}: Kerne gleich bis auf E1

**Korrektur (25.11., Hinweis Justus, extern nachgerechnet, hier bestätigt):** Die erste Fassung nannte F12
„dieselbe 5-Zustands-Maschine“ und „die zweite M5-artige Familie“. Das ist falsch. Nach dem Zusammenlegen
des Haltezustands mit seinem Zwilling (bei 88/312/449: F mit B; bei 396: F mit D) sind A, B, C, D und E0 bei
allen vier gleich (A `1RB0LB`, B `0RC0LD`, C `1LD1RE`, D `0LA0RB`, E0 `0RD`), aber E1 nicht:

| Holdout | E1 im Original | E1 im Kern | Haltefeld im Original |
|---|---|---|---|
| 88 | `1RB` | `1RB` | F1, F über D1 erreicht (F = Kopie von B) |
| 312 | `1RF` | `1RB` | F1, F über D1 oder E1 erreicht (F = Kopie von B) |
| 449 | `0LC` | `0LC` | F1, F über D1 erreicht (F = Kopie von B) |
| 396 | `0RF` | `0RD` | F1, F über B1 oder E1 erreicht (F = Kopie von D) |

Nur 88 und 312 haben denselben Kern. Es gibt also drei verschiedene 5-Zustands-Kerne, und bei 396 liegt
zusätzlich das Haltefeld an anderer Stelle. Was das für PR #59 bedeutet, steht in
[`analyse/396.md`](396.md).

Weitere Befunde (zwei Punkte am 25.11. berichtigt):

- 88, 312, 449 sind dieselbe Tabelle bis auf E1 (`1RB`, `1RF`, `0LC`); busycoq-PR #59 „Prove three BB(6)
  machines halt: one doubling law, E1 = 1RF, 1RB or 0LC“ (offen, Stand 10.11.) beweist laut Titel, dass alle
  drei **halten**.
- 88 und 312 haben denselben 5-Zustands-Kern und laufen per Tabellenvergleich im Gleichschritt.
  88 und 312 laufen im Gleichschritt mit vier Äquivalenten von 396 (396.2, .3, .5, .7), 396 mit zwei
  Äquivalenten von 449 (449.1, .2), jeweils per Tabellenvergleich. (Erste Fassung hatte die Richtung
  vertauscht.)
- **396 ist das einzige Mitglied ohne PR** (busycoq `open`, slugbird `rules`). Die erste Fassung nannte es
  „naheliegend“, dass das „doubling law“ aus PR #59 auch 396 trifft. Nachgeprüft in
  [`analyse/396.md`](396.md): Das Besuchsgesetz gilt für 396 bis auf die Halteregel; der Halte-Beweis ist
  **nicht übertragbar**.

### Holdouts mit gleicher Tabelle wie eine decided Maschine

| decided | Beweis | Holdouts (gleiche Tabelle, anderer Start) |
|---|---|---|
| d833 | `ChaoticBell1Halt.v`, hält | 244, 339, 489 |
| d581 | `FARv1.v`, hält nicht | 66, 438, 532 |
| d1250 | `FARv1.v`, hält nicht | 398, 530 |
| d653 | `FARv1.v`, hält nicht | 262 |
| d934 | `FARv1.v`, hält nicht | 527 |

Daraus folgt nichts über die Holdouts: der Beweis gilt für einen Start. Bei FAR wäre zu prüfen, ob die
Sprache des Zertifikats auch den Leerband-Start im anderen Zustand enthält (unwahrscheinlich, weil die
Entscheider vermutlich schon auf allen Holdouts liefen; unbelegt).

### Abgleich mit bekannten Gruppen

| bekannt | gefunden |
|---|---|
| {31,222} {114,367,378} {141,315} {274,518} {318,322} (vorlagen.md) | alle als tabelle, gleiche Starts und Spiegelung wie dort |
| M5 = {274, 318, 322, 518} | alle 6 Paare als kern; 318/518 gleichschritt; 274/322 verschmelzen im Kern nach 25/11 Schritten (wie in `analyse/318_518.md`) |
| 4 Wiki-Gruppen | alle als tabelle |
| busycoq/cryptids | keine Holdout-Paare, also nichts abzugleichen |

## 4. Programme und Kontrollen

Ordner `analyse/verwandtschaft/`:

- `karte_a.py` (Python): kanonische Formen über alle 720 Umbenennungen × 2 Spiegelungen; Kerne per
  Union-Find-Abschluss; Gleichschritt per Produktautomat; Verschmelzen mit exakten Bandkopien.
- `karte_b.c` (C, unabhängig geschrieben, andere Verfahren): Tabellen paarweise per Breitensuche-Zuordnung;
  Kerne durch Durchprobieren aller 203 Zerlegungen der 6 Zustände; Kerne paarweise durch alle
  Umbenennungen; Verschmelzen mit rollendem Hash und exakter Nachprüfung; zusätzlich Simulationssieb.
- **Abgleich**: A und B liefern auf dem ganzen Universum (2.149 Maschinen) dieselben 1.619 Zeilen
  (T, V, Q, K, W, G), bei 10^5 Schritten. B mit 10^6 Schritten: T/Q/K/G unverändert, Verschmelzen unverändert.
- `test_karte.sh`: Positivkontrollen (114/367/378, M5, 318/518, 88/312, künstliche h9001 = h22 ab E
  gespiegelt, verschmilzt nach 1 Schritt), Negativkontrollen (künstlich veränderte 367, 518, 318 dürfen
  nichts finden) und 7 Fehler-Schalter (A: spiegel, joker, produkt; B: spiegel, joker, produkt, hash), die
  den Abgleich nachweislich brechen. Ergebnis: „ALLE KONTROLLEN BESTANDEN“.
- `divergenz.c`: zwei Maschinen nebeneinander; Ergebnisse bis 10^9 in `divergenz_1e9.txt`.
- `csv_bauen.py` baut CSV und Familienliste; `eqv_pin.py` liest busycoq.

Nachbau: `python3 -I karte_a.py universum.tsv > a.tsv`, `gcc -O2 -o kb karte_b.c && ./kb universum.tsv 100000 1000000 > b.tsv`,
`bash vergleich.sh a.tsv b.tsv`, `bash test_karte.sh`.

## 5. Grenzen

- „kern“ erfasst nur Zusammenlegungen, bei denen die Zustände Übergang für Übergang gleich sind. Was nur
  auf dem tatsächlich erreichten Teil gleich ist (wie die 7 beobachteten Gleichschritte), findet nur die
  Simulation; dafür gibt es keinen Beweis, nur 10^9 Schritte.
- Gleichschritt mit Spiegelung kommt nicht vor: alle Maschinen beginnen mit `1RB`.
- Verschmelzen nur bis 10^6 Schritte je Lauf geprüft. Spätere Verschmelzung ist nicht ausgeschlossen.
- Status (PR, offen) aus `holdouts.json` vom 10.11.; laut Discord warten rund 70 neuere Beweise.

## 6. Bericht

- **Ergebnis**: Karte mit 647 Paaren und 141 Familien (376 Holdouts). Bündelung ja, Entscheidung nein.
  Neue Spur: Familie F12, in der 396 als einziges Mitglied ohne PR dasteht.
- **Belege**: Branch `claude/project-thread-ubfhyu`, Commits siehe PR; A = B auf 1.619 Zeilen;
  `test_karte.sh` grün; Läufe lokal (A 2 min, B 4,5 min), kein Actions-Lauf nötig.
- **Abweichungen und eigene Fehler**: Erste Fassung von `eqv_pin.py` übersah `Theorem eqv` in
  `Eqv_RegularPairs.v` (9 Sätze), korrigiert. Die erste Verschmelzen-Prüfung lief nur über Holdout-Paare,
  danach auf das ganze Universum erweitert. „Gleichschritt beobachtet“ ist eine Erweiterung über den
  Auftrag hinaus und klar als unbelegt markiert.
- **Offene Punkte**: (1) PR #59 lesen und prüfen, ob das „doubling law“ 396 abdeckt. (2) F1: Warum hält
  d833, und was unterscheidet die Starts 244/339/489? (3) F26 = {38, 59, 124}: 38 hat einen Beweis als
  langer translated cycler (PR #61); ob 59/124 in denselben Zyklus laufen, ist offen (Läufe > 1e27).
  (4) Beschleunigungen in cryptids gelten für eine Tabelle; bei F3, F6, F11, F12, F30, F87 gibt es sie nur für
  ein Mitglied. Übertragbarkeit auf die anderen Starts ungeprüft.
- **Empfehlung**: weiter, aber gezielt: ein Block „PR #59 lesen, auf 396 anwenden“ (Analyse, kein Rocq).
  Vorher in #bb6 klären, ob jemand an 396 arbeitet. Die Karte selbst ist abgeschlossen.
