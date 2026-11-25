# Gruppe 1: Vorlagen Loop4Mono_v3 und _v6 lesen

Stand 25.11.2026. Reines Lesen und Analysieren, **kein Rocq**, nichts gebaut. Gelesen am busycoq-Pin
`33209bc7` (`verify/Loop4Mono_v3.v`, 3.437 Zeilen; `verify/Loop4Mono_v6.v`, 1.533 Zeilen).
Kurze Zählung mit zwei Programmen in `analyse/gruppe1/vorlagen/`.

## Ergebnis in Kürze

1. **v6 ist keine Vorlage für Nicht-Halten.** Beide Maschinen in v6 werden als **haltend** bewiesen
   (`Theorem halt: halts tm c0` in `TM1` und `TM2`). Es gibt dort keine abgeschlossene Menge und keinen
   Haltausschluss. Bewiesen wird, dass eine beschleunigte Simulation bis zum Halt durchläuft
   (`certificate`, `stopped_run8_halts`, Halt-Lemma `D1_0_A3_halt`). Für unsere Frage bleibt v3.
2. **v3, Maschine `TM1`** (`1LB1RB_1RC0LE_1RE0RD_1RA---_1LF1LB_0RC0LF`; `TM2` ist eine Umbenennung
   davon mit anderem Startzustand, `variant_old_nonhalt`). Die abgeschlossene Menge ist `boundary_inv`: Das Band ist eine Liste von Wörtern, und die
   ganze Liste wird durch ein Wort über **11 Buchstaben** beschrieben. Die Zahlen in der Liste sind
   durch die Buchstaben und ihre Position festgelegt. Erlaubt sind nur Buchstabenwörter einer
   **regulären Sprache** (101 Kontexte, dazwischen Ketten aus 3 Blocksorten). Dass man nach 6 oder 8
   Generationen wieder in der Menge landet, prüft ein endlicher Automat (`boundary_macro_step`,
   `context_certificate`).
3. **Das linke Ende ist in v3 fast nichts.** Dort wird das linke Wort verbraucht. Sein Wert ist
   immer **genau 2 × Listenlänge plus ein kleiner Buchstabenwert** (`ParametersN`, Gleichung `Ecount` in
   `local_reset`). Darum läuft jeder Durchgang garantiert bis ans andere Ende und hat dort noch 1 bis 7
   Restaufrufe übrig. **Achtung, gespiegelt:** v3s linkes Ende ist bei uns das rechte Ende (Fressen).
   Unserem linken Ende (dort wächst das Band) entspricht v3s **rechter Rand**. Dort steht eine endliche
   Tabelle mit 25 Fällen (`flow`) und eine einzige Zahl (`zparameter`, Werte 1 bis 3).
4. **Halt wird in v3 an keiner einzelnen Stelle ausgeschlossen, sondern durch Vollständigkeit.**
   Jeder Makroschritt ist eine bewiesene echte Rechnung (`macro_actual_step`). Sie ist aus lokalen
   Lemmas zusammengesetzt, die für alle Zahlen ohne Halt gelten (`D1_Inc11` … `D20_rh_Inc2`, `Inc`, `Ov`).
   Halt könnte nur in Fällen passieren, die das Modell nicht kennt (`flow` liefert nichts, falscher
   Randparameter). Dass diese Fälle nie eintreten, ist genau der Inhalt des Abschlusszertifikats.
   Schluss: `boundary_inv_nonhalt` mit `progress_nonhalt_cond`, dann `nonhalt`.
5. **Bei Tabelle 114 scheitert dieselbe Konstruktion an Punkt 3, nicht an der Periode 3 selbst.**
   Bei uns ist die Reichweite eines Durchgangs **nicht** an die Listenlänge gekoppelt. Die Kenngröße
   „x/2 minus Listenlänge“ (in v3 entspricht ihr der Überschuss am Rand, immer 1 bis 7 Aufrufe, nie negativ) streut bis 10^9 zwischen −64 und +27. Nur in 19, 17 bzw. 32
   von 77 bis 78 Zyklen ist sie ≥ 0 (Start A, C, D; zwei Programme gleich). Folge: Die meisten Durchgänge
   enden **mitten in der Liste**, hinterlassen dort eine Bruchstelle, und mehrere Bruchstellen
   treffen am linken Ende aufeinander. Das sind die „alt“-Fälle und die nicht sättigenden Formen aus dem
   letzten Bericht. Ob die nächste Welle eine alte Bruchstelle erreicht, hängt davon ab, wie eine Zahl
   vom rechten Ende (a + 4b + 7) im Vergleich zu einer Position in der Liste ausfällt. Einen solchen
   Vergleich kann ein endlicher Automat nicht ausdrücken. Darum fällt der Schritt „reguläre Sprache
   plus Automatenzertifikat“ weg.

## 1. Was v6 beweist (kurz)

- Modell: `Loop4MonoFast` mit Wörtern `A n | B n | C n | D n` (= `D1..D4`, Periode 2) und einer
  Warteschlange `dseq`. `step` liefert einen neuen Zustand, `Halt` oder `Failed`.
- Die Warteschlange speichert nur **Restwerte** e. Das echte Wort ist
  `D1 (e + 2·(Anzahl dahinter + 1))` (`layer`). Das ist dieselbe Kopplung an die Position wie in v3. Im
  Beweis von `reset_list_sound` sieht man es: `Ov` macht daraus den Zähler, `cross_layer` trägt die
  Marke durch die ganze Schlange, `layer_ext_side_n … (e+7)` macht e + 7 Aufrufe am Rand.
- Halt: `D1_0_A3_halt` (lokal: `D1 0` vor zehnmal `D1 3` hält), `halt_edge_sound`,
  `service_haltb_sound`. Mit `certificate` (`native_check_eq`: `run8 10 18000 init109` endet in `Halt`)
  folgt über `stopped_run8_halts` der Satz `halt`.
- Für uns: v6 ist das Gegenstück zu unserem Beschleuniger (Phasen überspringen, rechnen bis zum
  Ereignis). Für einen Nicht-Halte-Beweis fehlt dort die abgeschlossene Menge. Das ist die Lücke, die
  auch wir haben.

## 2. v3, TM1: die drei Ebenen

### Ebene 1: Band als Wortliste

- Konfiguration `S' (n, r) = 0inf {{{F}}} [1;0;1;0]^^n *> r`: Kopf ganz links, rechts davon ein Zähler
  `(1010)^n`, dann die Liste r aus Wörtern `D1 n = 01010 (1010)^n` und `D2 n = 010 (1010)^n`
  (`rword = R1 n | R2 n`, `rside`, `rconfig`).
- `Inc`: Ein Hin- und Rückweg über die ganze Liste kostet eine Zählereinheit (`S'(1+n,r) -->+ S'(n,r')`).
- `Ov`: Ist der Zähler leer, wird das **linke Wort** `D1 n` zum neuen Zähler `2+n`, und das nächste
  Wort wird zur Marke `D2`.
- `pair_step`: Zwei Durchgänge schieben die Marke `R2` ein Wort nach rechts. Das übersprungene Wort
  wird um 2 größer, alle anderen bleiben gleich (`D1_Inc11`: Durchgang lässt `D1 n` unverändert). Am
  rechten Ende entstehen neue Wörter (`D1_rh_Inc3`, `D2_rh_Inc3`, `D20_rh_Inc2`).
- `reset_step` (Lemma `reset_step_sound`): linkes Wort weg, a+2 Aufrufe (`service`), echte Rechnung `-->+`.

### Ebene 2: Buchstabenwort statt Zahlen

- `letter` (11 Buchstaben `LA`…`LK`) mit Wert `lvalue` (0–6), Verschiebung `ldelta` und Phase `lphase`.
- **Kern:** `ParametersN`: Die Zahl des i-ten Wortes ist
  `2·(Abstand zum rechten Ende) − 5 + lvalue(Buchstabe) − offset`, wobei offset die Summe der `ldelta`
  davor ist. Die Zahlen sind damit **vollständig durch das Buchstabenwort bestimmt**. `represents`
  verbindet Wort und Liste. Es bleibt **eine** freie Zahl am rechten Rand (`zparameter`).
- In `local_reset` folgt daraus `Ecount`: a + 2 = 2·(Länge des Rests) + lvalue x + 1. Der Zähler reicht
  also **immer genau** bis ans rechte Ende plus 1 bis 7 Aufrufe. Was dort passiert, steht in `flow`
  (25 Paare „verbrauchter Buchstabe, Randbuchstabe“) mit `edge_certificate`.
- Damit wird ein Durchgang zu einem Schritt eines **Warteschlangensystems auf Buchstaben**: vorne einen
  Buchstaben weg, den letzten nach `flow` ersetzen und anhängen (`symbolic_step`, `zstep`,
  `symbolic_step_sound`). Eine Generation = so viele Schritte, wie das Wort lang ist (`zgen`).

### Ebene 3: abgeschlossene Menge und Haltausschluss

- `boundary_inv z`: gültiges Buchstabenwort (`zvalid`), Randparameter `= 2`, und das Wort hat die Form
  `context_word c hs as_` = H-Blöcke ++ Brücke ++ A-Blöcke ++ Schluss. Dabei ist `c` einer von 101
  Kontexten (`context_codes`, `all_contexts`: 8 Brücken, 2 Schlüsse, Randblöcke). `hs` und `as_` sind
  Ketten aus Bitpaaren (`BP10`, `BP01`, `BP00`) mit erlaubten Nachfolgern (`hnext`, `anext`). Das ist
  eine reguläre Sprache.
- Abschluss: `boundary_macro_step`: aus `boundary_inv z` folgt nach 6 oder 8 Generationen wieder
  `boundary_inv z'`. Geprüft durch Rechnen: Die Generationen laufen als gestapelte Wandler
  (`sm_generation`, `slayer`, `pipe_action`), die erreichbaren Automatenzustände über beliebig lange
  Blockketten werden abgeschlossen (`qclosure`, `qclosedb`, `qmode`), und für jeden der 101 Kontexte muss
  das Ergebnis wieder ein Kontext sein (`macro_ok`, `context_certificate`).
- Start: `init`, drei `reset_step`, dann 17 Generationen bis `boundary0` (`generation0_to_boundary0`,
  `boundary0_inv`).
- Haltausschluss: `macro_actual_step` (jeder Makroschritt `-->+` und bleibt in der Menge) →
  `boundary_inv_nonhalt` (`progress_nonhalt_cond`) → `nonhalt`. Das Halten in D1 kommt nirgends als
  Muster vor. Es ist ausgeschlossen, weil jede lokale Regel als Satz über **alle** n bewiesen ist und
  das Zertifikat zeigt, dass nie ein nicht abgedeckter Fall eintritt.

## 3. Übertrag auf Tabelle 114 (Periode 3)

| Baustein v3 | Gegenstück bei 114 | Stand |
|---|---|---|
| Wörter `D1`/`D2`, Durchgang lässt Wort unverändert (`D1_Inc11`) | Blöcke `011`^n / `100`^n; ein Durchgang vertauscht 0 und 1, bei S2 hängt der Zustand B/D von der Parität ab | in Rocq bewiesen (Stufe 1, Durchlaufmodell). **Kein** Hindernis, nur mehr Buchstaben |
| Zähler links (`S'`), `Inc`, `Ov` | Zähler rechts: x = a + 4b + 7 (Fressen, Regel F/Z), dann x − 1 Pendelschwünge | F bewiesen (PR 8), Z nicht |
| Marke `R2` wandert 1 Wort je 2 Durchgänge, +2 für das überquerte Wort (`pair_step`) | Grenze wandert 1 Token je 2 Phasen nach links (N2/N1), +2 | Automat aus PR 9, bis 10^17 bestätigt (nicht bewiesen) |
| **`ParametersN` / `Ecount`: Zähler = 2·Länge + Buchstabenwert, Marke erreicht immer das Ende** | **fehlt**: x/2 − Listenlänge streut von −64 bis +27 | **Bruchstelle** |
| rechter Rand: `flow`, 25 Fälle, eine Zahl `zparameter` ∈ {1,2,3} | linkes Ende: 13 Kernmuster, 91 Formen bis 10^17, nicht gesättigt, mehrere Bruchstellen („alt“) | offen (PR 10) |
| reguläre Sprache + Automatenzertifikat | nicht formulierbar, solange Ebene 2 fehlt | — |

**Woran genau es scheitert.** In v3 hat jedes Wort genau die Zahl, die seine Position verlangt. Jeder
Durchgang läuft deshalb bis zum Ende, und hinter ihm bleibt kein Rest in der Liste. Bei 114 wird die
Reichweite x durch die beiden rechten Elemente bestimmt (x = a + 4b + 7), aber nicht durch die Länge der
Liste. Die Welle endet meist vorher, und an der Stelle, an der sie stehen bleibt, bleibt eine
Bruchstelle zurück. Die Werte in der Liste sind deshalb nicht „Position mal 2“, sondern Treppen. Beispiel
Start A bei 9,97·10^8 (Ausschnitt, rechtes Bandende links):
`98 | 98 | 98 | 108 | 94 | … | 90 (12-mal) | … | 78 (13-mal) | … | 14 (16-mal) | … | 2 (13-mal) <5> 0 (14-mal)`.
Jede Stufe ist eine Stelle, an der früher eine Welle stehen blieb.

Zählung bis 10^9 an allen Zyklusanfängen (`reich.py` und `zweit.awk`, unabhängig, Ausgaben gleich):

| Start | Zyklen | x/2 − Länge: min / max | davon ≥ 0 | Länge am Ende | größter Wert unter den 50 linken Elementen | Differenz Nachbarn min / max |
|---|---|---|---|---|---|---|
| A | 77 | −64 / +27 | 19 | 263 | 32 | −14 / +18 |
| C | 77 | −57 / +24 | 17 | 294 | 32 | −16 / +22 |
| D | 78 | −59 / +20 | 32 | 241 | 32 | −14 / +18 |

Länge = Zahl der Elemente der Textliste aus `zweitpruefung.c`, a und b eingerechnet. „x/2 − Länge ≥ 0“ ist
nur ein grobes Maß dafür, ob die Welle das linke Ende erreicht. Der alte Bericht `gruppe1.md` zählte
mit einer anderen Abgrenzung 24 von 76 (Start A).

**Was die Zahlen hergeben (Beobachtung, nicht bewiesen):**
- Die Unterschiede zwischen Nachbarn bleiben bis 10^9 klein (−16 bis +22), obwohl die Liste von 55 auf
  263 Elemente wächst. Eine Kodierung „Buchstabe = Unterschied zum Nachbarn plus Trenner“ wäre also
  vielleicht endlich. Das wäre das Gegenstück zu v3s Buchstaben.
- Was dann fehlt, ist die Kopplung: Die Reichweite x/2 ist eine Summe über die ganze Liste, das Ziel ist
  eine Position. Ein Beweis im Stil von v3 bräuchte zusätzlich zur regulären Sprache eine **Zahl mit
  Ungleichung**, etwa „Reichweite − Abstand der letzten Bruchstelle“, und müsste zeigen, dass sie in
  einem endlichen Bereich bleibt oder sich in einem festen Muster bewegt. So etwas gibt es weder in v3 noch
  in v6.
- Die 50 linken Elemente bleiben klein (höchstens 32 bis 10^9). Ob das so bleibt, ist offen.

## 4. Folgerung für die Beweisidee

- v3 lässt sich nicht übertragen, indem man nur die Wörter austauscht. Ebene 1 hätten wir schon. Ebene 2
  bricht, weil die Kalibrierung `Ecount` fehlt, und damit fällt auch Ebene 3 weg.
- Brauchbar aus v3 bleibt das Muster **„Halt durch Vollständigkeit ausschließen“**: Jede Phasenregel
  (N1, N2, N2s, UA, LE, LG, VS) als Satz für alle Zahlen beweisen. Dann bleibt Halt nur in den Fällen
  am linken Ende möglich, die keine Regel abdeckt. Das passt zum Thread „Halt als verbotenes Muster“.
  Der kann prüfen, ob „C vor 111“ überhaupt in diesen Fällen entstehen kann.
- Eine Beweisidee müsste die Lage der Bruchstellen relativ zur Reichweite der Wellen fassen. Das wäre
  eine neue Art Invariante (regulär **plus** Zählerbedingung), für die es im Pin keine Vorlage gibt.
  Meine Einschätzung, **unbelegt**: Das ist eher ein Forschungsproblem als Beweisarbeit nach Vorlage.

## 5. Nachprüfen

```
git -C busycoq checkout 33209bc7dc282b38c8cd6be507bfc551fea56108   # verify/Loop4Mono_v3.v, _v6.v
gcc -O2 -o zp analyse/gruppe1/zweitpruefung.c
./zp 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC 1000000000 liste A > A.txt          # ebenso C, D; je ca. 5 s
Z=analyse/gruppe1/zyklus/ergebnisse/py_zyklen_A.txt
python3 -I analyse/gruppe1/vorlagen/reich.py A.txt $Z > r1; awk -v modus=reich -f analyse/gruppe1/vorlagen/zweit.awk $Z A.txt > r2; cmp r1 r2
python3 -I analyse/gruppe1/vorlagen/diff.py  A.txt $Z > d1; awk -v modus=diff  -f analyse/gruppe1/vorlagen/zweit.awk $Z A.txt > d2; cmp d1 d2
```

Spalten in `reich_X.txt`: Schritt, x, Länge, x/2 − Länge, größter Wert unter den 50 linken Elementen.
In `diff_X.txt`: Schritt, größte und kleinste Differenz zu Nachbarn, Zahl der Nachbarn mit Differenz ≠ 0.
Eine Negativkontrolle für diese Zählung gibt es nicht. Sie trägt keine Entscheidung, nur die Aussage
„streut stark“.
