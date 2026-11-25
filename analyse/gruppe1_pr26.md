# Gruppe 1: busycoq PR #26 lesen (Token-Übersetzer, INV) und Abgleich

Stand 25.11.2026. Reines Lesen, **kein Rocq**, nichts gebaut. Quelle: `ccz181078/busycoq`,
`refs/pull/26/head` = Commit `c12a4d3` (Dennis Koshta, 15.10.2026, „Prove a spread-digit bouncer counter
nonhalting“). Der PR fügt genau eine Datei hinzu:
`verify/M_1RB0LF_0RCHHH_1RD0RA_1LE0RC_0LA0LE_1LE1LB.v` (1.327 Zeilen).

**Der Beweis ist in unserem Pin.** PR 26 wurde am 16.10.2026 gemergt (Merge-Commit `153141e`, Vorfahr
von `33209bc7`). Am selben Tag hat ccz181078 die Datei in `verify/PR_SBC.v` umbenannt (Commit `2733f61`,
„add 35 proofs from PR“): neuer Kopfkommentar, Inhalt in `Module TM1`, Satz `TM1.nonhalt`. Alle unten
genannten Lemma-Namen gibt es dort unverändert (geprüft per grep, 24 Namen). Zeilennummern unten beziehen
sich auf die PR-Fassung.

Write-up: `materials/spread-counter/1RB0LF_0RC---_1RD0RA_1LE0RC_0LA0LE_1LE1LB_writeup.md` im Fork von
DennisKoshta (Commit `bbd8dec7`, 691 Zeilen). Ich habe es nicht selbst gelesen. Ein Hilfsagent hat es
gelesen und zusammengefasst. Was ich daraus übernehme, ist unten als „laut Write-up“ markiert und nicht
selbst geprüft. Auf dem PR gibt es keine Reviews und keine Kommentare.

## Ergebnis in Kürze

1. **Die Maschine ist ein Zähler, keine Warteschlange.** Links ein Vorlauf a (unär, Blöcke `100`), rechts ein
   Binärzähler, dessen Ziffern durch Lücken `(100)^g` getrennt sind, ganz rechts ein „Schwanz“ aus
   Bits. Bei jedem Überlauf läuft der Übertrag in den Schwanz. Der antwortet **S** (Zähler läuft still
   über) oder **N** (seltener Umbau: Der linke Teil erstarrt zu einer „Wand“ aus Zonen, die eine lange Pause
   abbaut und dabei jede Lücke neu setzt und neue Ziffern einfügt).
2. **Token-Übersetzer** (`retf`, `retf_spec`): Nach dem Überlauf läuft C nach rechts über ein Wort ohne
   `00` (`Csweep`), dreht an der ersten `00` (`CT0`) und läuft zurück. Der Rückweg ist ein **endlicher
   Automat** mit zwei Zuständen (E, F) und vier Regeln, der „bearbeitete“ Token (P = `01`, PZ = `010`)
   in neue Token (T0 = `00`, T1 = `01`, TZ = `100`) übersetzt. Er ist einmal für alle Wörter per
   Induktion über die Länge bewiesen. Mit `retf_app` (Hintereinanderschalten) und geschlossenen Formeln
   für Blöcke (`RB_E2`, `RB_F2`, `retf_LD`, `retf_lead`) ersetzt das laut Kopf eine Tabelle mit 16.384
   Einträgen. Der Umbau selbst ist `wallOv` (Wand = Zonen `zw`), dann `Zone`/`Zones` (Zone g →
   neue Lücke, Zähler 2v + 2g) und `ZXN`/`ZXP` als Abschluss.
3. **INV** (`INV a G r1 St`): Mit Q = 2^(Länge G + r1) gilt erstens die **exakte Gleichung**
   `gval G + 6 + κ = Q`, κ ∈ {2, 8}. Zweitens ist `a = s + Q + κ`, wobei s in einem **Intervall** liegt,
   das von den vorderen zwei Schwanz-Bits abhängt (`11`: 24 ≤ s ≤ Q+2; `10`: 8 ≤ s ≤ 4Q−14 oder
   4Q+24 ≤ s ≤ 8Q). Drittens hat der Schwanz die feste Form `Lst` (15 Bits an festen Stellen, dann eine
   beliebige Bitliste e). Dazu kommen „alle Lücken ≥ 2“ und 64 ≤ Q. Laut Write-up ist die Fassung dort
   strenger (Lücken ≥ 7, M = 4Q ≥ 256), und die `.v` nutzt bewusst die schwächere.
4. **Abschluss** (`step`): Fallunterscheidung nach Schwanzfront (`11`/`10`), Schwanzantwort (`Tail11`:
   N oder S, je ein Blatt pro Lage der ersten 0) und Intervall von s. Das ergibt vier Wege (`pathS`,
   `pathP1`, `pathP1S`, `pathP3`). Für jeden Weg werden die neuen Werte ausgerechnet, und `lia` zeigt
   die neue INV, wobei 2^(…) als ein Symbol Q behandelt wird (`Q1`, `Q3`). Kein Automatenzertifikat,
   sondern Handarbeit: Gleichung plus Intervalle. Start: 92.299 Schritte bis `KX 121 [28] 5 St0`
   (`init`, `INV0`). Halt ist ausgeschlossen wie in v3, durch Vollständigkeit (`progress_nonhalt_cond`
   in `nonhalt`).
5. **Abgleich mit Gruppe 1:** Unser Phasen-Automat passt gut zu `retf`, die VS-Regel zum
   Schwanzbeweis `Tail11`/`Tail11_end`. **Es fehlen uns zwei Dinge:** eine feste Form für das linke Ende,
   die unter allen Ereignissen erhalten bleibt (bei PR 26 `Lst`, bei uns 13 Kernmuster, nicht gesättigt,
   „alt“-Fälle), und vor allem die **exakte Gleichung**, die die Zahlen bindet (bei PR 26
   `gval G + 6 + κ = Q`, bei uns keine).
6. **Korrektur zu meinem v3/v6-Bericht (PR 11):** Dort schrieb ich, eine Invariante „regulär plus
   Zählerbedingung“ habe keine Vorlage. PR 26 **ist** so eine Vorlage:
   reguläre Schwanzfamilie plus Gleichung und Intervalle, Abschluss per `lia`. Sie liegt sogar **im Pin**
   (`verify/PR_SBC.v`). Meine Aussage in PR 11 war also falsch, weil ich nur v3/v6 angesehen hatte.
   Meine Einschätzung
   „Forschungsproblem“ ist damit schwächer, aber nicht hinfällig: Bei PR 26 legt die Binärzähler-Struktur
   die Gleichung nahe, bei uns fehlt der Kandidat.

## 1. Aufbau von PR 26

Tabelle `1RB0LF_0RC---_1RD0RA_1LE0RC_0LA0LE_1LE1LB`, Halt bei B1.

- **Token** (rechts vom Vorlauf): T0 = `00`, T1 = `01`, TZ = `100`. Nach einem Rechtslauf von C sind sie
  „bearbeitet“: P = `01` (aus T0/T1), PZ = `010` (aus TZ) (`Csweep`, `proc`, `prc`). Das ist dieselbe
  Art 0/1-Vertauschung wie bei uns (`C> 100 → 011`).
- **Zähler** `ctr gs v`: Ziffern `b TZ T1 TZ^g`, niedrigste zuerst (`ctr`, `IncC`, `IncL`).
  Normalbetrieb: `Inc` (ein Abpraller links, Vorlauf a → a+1, Zähler v → v+1).
- **Konfigurationen**: `KP W p gs v H St` = Wand W, Vorlauf p, Zähler, Suffix, Schwanz St.
  `KX a G r1 St` = Überlauf im Normalbetrieb, Zähler voll (alle Einsen), Lücken `G ++ 2 :: 1^r1`.
- **Überlauf** (`OvRet`, `OvN1`, `OvN0`, `OvS1`): Rechtslauf über den Zähler, Wende im Schwanz
  (`TailRet`), Rücklauf mit `retf`, über den R-Block (`RB_*`), Rand.
  - **S** (`OvSp`, `SILENT`, `SILENTP`): Zähler auf 0, weiter wie vorher. Weg `pathS`: a → a + 4Q.
  - **N** (`OvNp`, `NOrb`, `POrb`): Der bearbeitete linke Teil wird zur Wand aus Zonen
    (`wallOv`, `zw`). In der folgenden Pause frisst die Maschine die Wand mit je zwei Schritten
    (`TwoInc`, `P100s`, `P010s`), jede Zone g wird zu einer neuen Lücke `(p+2)` und der Zähler zu
    `2v + 2g` (`Zone`, `Zones`, Zählfunktionen `zv`, `zg`, `zp`). Abschluss `ZXN`/`ZXP`.
- **Schwanz**: `tailw x y z b4 … b15 e` = feste Folge aus T1/TZ mit 15 freien Bits und einer freien
  Bitliste e, dann `01` und leeres Band. `Lst y z` = alle solchen Schwänze mit x = 1 und Front (y, z).
  `Tail10`, `Tail0z`, `Tail11` (ein Fall je Lage der ersten 0 unter b4…b15) und `Tail11_end`
  (erste 0 in e, Lage j beliebig, per `e_split`) zeigen: Jede Antwort ist N oder S, und der Schwanz
  danach liegt wieder in `Lst`. Das ist die reguläre Hälfte der Invariante.

## 2. INV und ihr Abschluss

```
INV a G r1 St :=  alle Lücken in G ≥ 2,  64 ≤ Q,  Q = 2^(|G| + r1),
                  ∃ κ ∈ {2,8}, s:  gval G + 6 + κ = Q  ∧  a = s + Q + κ  ∧
                  ( St ∈ Lst 1 1 ∧ 24 ≤ s ≤ Q+2
                  ∨ St ∈ Lst 1 0 ∧ (8 ≤ s ≤ 4Q−14 ∨ 4Q+24 ≤ s ≤ 8Q) )
```

`gval G = 2·(g_1 + gval G')` misst die Wand. Die Gleichung sagt: Der Inhalt der Wand plus eine kleine
Konstante ist genau die nächste Zweierpotenz. Sie sorgt dafür, dass der Abbau der Wand in der Pause
genau aufgeht (`NOrb`: `gval G + 2 < 2^(…)`, `Zones`: `zv L v < 2^(…)`).

| Weg | wann | Ergebnis |
|---|---|---|
| `pathS` | Front 11, Schwanz antwortet S | a + 4Q, G, r1 gleich, Front danach 10 |
| `pathP1` | Front 11 und Antwort N, oder Front 10 und s ≤ 4Q−14 | a' = 8Q+12−s, neue Lücke Q+2+κ, r1+1 |
| `pathP1S` | Front 10, s ≥ 4Q+24, zweite Antwort S | a' = 24Q+12−s, neue Lücke Q+2+κ, r1+1 |
| `pathP3` | Front 10, s ≥ 4Q+24, zweite Antwort N | a' = 68Q+40−s, drei neue Lücken 7, 4Q+1, Q+2+κ, r1+2 |

In `step` wird für jeden Weg gezeigt, dass die neuen Werte wieder INV erfüllen. Das gelingt, weil die neue
Gleichung aus der alten folgt (neue Lücke Q+2+κ, neues Q = 4Q bzw. 32Q) und die neuen s-Werte
(4Q+10−s, s+4Q, 20Q+10−s, 36Q+32−s) wieder in den Intervallen liegen. Mehr Rechnung braucht es nicht.

**Wie selten der Umbau ist:** „Selten“ heißt hier: nur bei einem Überlauf des Zählers, und der kommt nur
alle rund 2^N Erhöhungen. Die Abstände wachsen also wie Q. Laut Write-up gibt es Zählerstände an den
Schritten 92.299, 1.006.516, 14.514.329 und 114.113.163, also etwa Faktor 10 je Überlauf. Am Überlauf
selbst ist N die Regel: S kommt nur von Front 11, danach ist die Front 10 (aus den Wegen ablesbar). Laut
Write-up läuft die Front im Kreis `10 → 01 → 11 → 00 → 10` (alles N), mit der Abkürzung `11 → 10` (S).

Das ist ein wichtiger Unterschied zu uns. Bei PR 26 werden die Ereignisse am Rand exponentiell seltener,
und jedes Ereignis findet eine feste Schablone vor. Bei uns erreicht die Welle das linke Ende in
17 bis 32 von 77 Zyklen (PR 11), also in einem festen Anteil der Zyklen. Und das Ende sieht jedes Mal
anders aus.

## 3. Abgleich mit Gruppe 1

| PR 26 | Gruppe 1 (Stand PR 9/10) | passt? |
|---|---|---|
| Token T0/T1/TZ, bearbeitet P/PZ (0/1 vertauscht) | Token (t, n): Trennbit + `011`^n; Durchläufe vertauschen 0/1 (S1/S2, in Rocq bewiesen) | ja, gleiche Bauart; unsere Blöcke sind länger (n unbeschränkt), das ist dort die Lücke `TZ^g` |
| `retf`: endlicher Automat für einen ganzen Rücklauf, `retf_spec` per Induktion | Phasen-Automat N1/N2/N2s/UA/LE/LG: eine Regel je Pendelschwung, Grenze wandert 1 Token je 2 Phasen | **ja, als Vorlage.** Die x−1 Phasen eines Zyklus ließen sich als ein `retf`-artiger Übersetzer über die Token schreiben und einmal per Induktion beweisen. Das wäre unsere Zyklusfunktion aus PR 9, nur als Beweisobjekt |
| geschlossene Formeln `RB_E2`, `retf_LD` für Blöcke | Regel F (x \| y → x+4 \| y−1, bewiesen), Schrittformel 12S − 2m + 12k + c | ja |
| Schwanz `Lst`: feste Folge, 15 freie Bits, freie Liste e; ein Fall je Lage der ersten 0 (`Tail11`), unbeschränkter Fall per `e_split` (`Tail11_end`) | linkes Ende: 13 Kernmuster; VS-Familie als Regel mit 11 Fällen (`vsfam.py`), parametrisch in f und k | **teilweise.** VS hat genau die Bauart von `Tail11_end` (ein Parameter für die Lage, Rest frei). Es fehlt eine **feste Form** des linken Endes, die nach jedem Ereignis wieder gilt. Bei PR 26 ändert jede Antwort nur die vorderen Bits. Bei uns wächst das Band links, die Formen sättigen nicht, und die „alt“-Fälle (zwei Bruchstellen nah beieinander, Anteil steigend) haben keine Regel |
| Wand + `Zones`: seltener Umbau, jede Zone wird neue Lücke | Welle erreicht das linke Ende (LE, LG, VS): neue Token links | ähnlich in der Rolle, nicht in der Form. Bei uns ist es kein seltenes Ereignis, sondern betrifft je nach Zählweise 17 bis 32 von 77 Zyklen (PR 11) |
| **INV: exakte Gleichung `gval G + 6 + κ = Q`** | keine. x = a + 4b + 7, die Kenngröße x/2 − Länge streut von −64 bis +27 (PR 11) | **fehlt.** Das ist der Kern |
| INV: Intervalle für s entscheiden den Weg | ob die Welle das linke Ende erreicht, entscheidet ein Zahlenvergleich (x gegen Länge) | **gleiche Rolle.** Bei PR 26 liegen die Intervalle fest in Vielfachen von Q, bei uns ist kein Muster bekannt |
| Abschluss per Fallunterscheidung + `lia`, Q als Symbol | — | Werkzeug wäre übertragbar, sobald es eine Gleichung gibt |
| Halt durch Vollständigkeit | Halt nur bei „C vor 111“; bis 10^12 lückenlos geprüft | gleich gedacht: Jede Regel für alle n beweisen, dann bleibt Halt nur in nicht abgedeckten Fällen |

**Was davon zu den 13 Kernmustern passt:** Die Kernmuster sind lokale Fälle an der Grenze, und jeder ist
in den Zahlen stückweise linear (autofit, PR 10). Im PR-26-Schema wären das die Blätter des Schwanzbeweises.
Eine endliche Zahl von Blättern genügt dort, weil der Schwanz eine feste Schablone hat (`tailx`). Bei uns
müsste man erst eine Schablone für das linke Ende finden, in der alle 13 Kerne und die „alt“-Fälle
vorkommen und die nach jedem Kern wieder gilt. Eine solche Schablone haben wir nicht. Ob es sie gibt, ist
offen.

**Was fehlt, in der Reihenfolge, in der es eine Beweisidee bräuchte (Einschätzung, unbelegt):**
1. Eine Gleichung oder Ungleichung, die die Zahlen am rechten Ende (a, b, damit x) mit der Liste
   verbindet, so wie `gval G + 6 + κ = Q`. Kandidat wäre etwas wie „Summe der Listenwerte gegen Länge“.
   Darauf habe ich nicht gezählt.
2. Eine Schablone für das linke Ende (Gegenstück zu `Lst`), unter der die 13 Kerne und die „alt“-Fälle
   abgeschlossen sind.
3. Erst dann wären Phasen-Automat als `retf`-Übersetzer und die Kernmuster als Blätter Beweisarbeit nach
   Vorlage.

## 4. Nachprüfen

```
git -C busycoq fetch origin refs/pull/26/head:pr26
git -C busycoq show c12a4d3 --stat                 # eine Datei, 1.327 Zeilen
git -C busycoq show c12a4d3:verify/M_1RB0LF_0RCHHH_1RD0RA_1LE0RC_0LA0LE_1LE1LB.v
git -C busycoq show 33209bc7:verify/PR_SBC.v          # dieselbe Datei im Pin, in Module TM1
git -C busycoq log --oneline --name-status 153141e..33209bc7 -- verify/M_1RB0LF_0RCHHH_1RD0RA_1LE0RC_0LA0LE_1LE1LB.v
```

Wichtige Stellen: `retf` und `retf_spec` (Zeilen 100–146), `OvRet` (237), Schwanz `tailw`/`Lst`/`Tail11`
(298–499), `Zone`/`Zones` (821–863), `NOrb`/`POrb` (965–1018), Wege (1059–1190), `INV`/`step`/`nonhalt`
(1191–1310), Kurzübersicht der Makroregeln im Kommentar am Dateiende.
