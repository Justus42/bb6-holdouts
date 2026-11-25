# Gruppe 1 (114, 367, 378): linkes Ende, Entscheidungstest

Stand 25.11.2026. Reine Analyse, **kein Rocq**. Werkzeuge und Rohergebnisse in `analyse/gruppe1/linkes_ende/`.
Auftrag: Justus' Nachricht vom 25.11. (Punkte 1 bis 4, Abbruchkriterium nach 1 Block).

## Ergebnis in Kürze

- **Urteil: (a), mit Einschränkung.** Die Fälle am linken Ende gehören zu wenigen Grundmustern
  ("Kerne"). Bis 10^15 gibt es 12 Kernmuster; das letzte neue kam bei 4·10^11, danach in 778 Fällen
  (10^12 bis 10^15, drei Starts) kein neues mehr. [ACTIONS_KERNE] Innerhalb eines Kerns ist das Ergebnis
  einer Phase **stückweise linear** in den Zahlen: Die größte Familie (VS, 58 % aller Fälle) habe ich
  vollständig als eine Regel mit 11 Fällen aufgeschrieben; sie trifft alle 537 beobachteten Fälle mit freier Zone und
  10.000 Zufallstests, keinen falsch. Für die übrigen 7 Familien zeigt ein Linearitätstest dasselbe
  Bild, die Formeln sind aber **noch nicht** aufgeschrieben.
- **Einschränkung (Widerspruch zur Lesart "sättigt"):** Die wörtlichen Formen sättigen **nicht**:
  je Zehnerpotenz kommen etwa 10 neue dazu. Das sind aber neue Zahlenwerte und Zonenlängen in alten
  Kernen, kein neues Verhalten. Ein vollständiger Regelsatz wäre groß: geschätzt 60 bis 100 Fälle
  (unbelegt, hochgerechnet aus der VS-Familie mit 11 Fällen). Außerdem fehlen die seltenen Fälle, in
  denen links vom Kern noch ein älteres unregelmäßiges Token steht (7 von 955).
- **Was (a) nicht liefert:** Ein Regelsatz ist nötig, aber kein Beweis. Für einen Beweis fehlt weiter
  eine Invariante, die Halt ausschließt und zeigt, dass jede erreichbare Konfiguration in den
  Geltungsbereich der Regeln fällt. Die gibt es nicht (PR 9: keine gefunden; hier nicht gesucht).
- **Beschleuniger:** funktioniert. Er stimmt bis 10^9 an allen rund 19.900 Phasen-Schnappschüssen je
  Start (Schrittzahl, r und die ganze Token-Liste) mit einer direkten Simulation überein, alle drei
  Starts. Abbruchkriterium also nicht erfüllt. 10^12 Schritte dauern 10 s, 10^15 rund 7 Minuten je
  Start. [ACTIONS_WEIT]
- **Wichtig:** In den Phasen, die der Automat überspringt (99,98 % aller Phasen), wird **Halt nicht
  geprüft**. Geprüft wird nur in den Rückfällen auf das Durchlaufmodell und in der direkten Simulation
  bis 10^12 [ACTIONS_HALT].

## 1. Beschleuniger auf Phasenebene

`beschleuniger.py`. Zustand an einem Phasen-Schnappschuss wie in PR 9: Kopf in Zustand C auf einer 0,
rechts davon `0 (100)^r 1` bis zum Bandende, links die Token-Liste.

- **r ≥ 1 und eine Automatenregel aus PR 9 greift** (N1, N2, N2s, UA, LE, LG): neue Token-Liste nach der
  Regel, Schrittzahl nach einer Formel. Die Formel habe ich aus den Daten bis 2·10^8 abgelesen:
  Schritte = 12·S − 2·m + 12·k + c. Dabei ist S die Summe der n aller Token rechts der Grenze, m ihre
  Anzahl, k das n der Grenze; c = 11 (N1), 21 (N2), 15 (N2s, UA), 25 (LE ganz links), 17 (LE an zweiter
  Stelle), 11 (LG). Je Phase kostet das im Mittel O(1) Rechenschritte.
- **sonst** (VS, "nicht anwendbar", Zyklusübergang bei r = 0): Rückfall auf das Durchlaufmodell aus
  Teil 3 (`sweepmodell.py`, Regeln S1, S2, E), **nur bis zum nächsten Schnappschuss**. Jeder Rückfall wird
  mit Token-Liste vorher und nachher protokolliert.

Ein Fehler, den ich unterwegs gemacht und behoben habe: Die erste Fassung prüfte im Rückfall vor jedem
Block-Sprung S2, ob ein Schnappschuss im Inneren liegen könnte, und machte dann Einzelschritte. Die
Prüfung war unnötig streng (im Inneren von S2 ist das Muster nie erfüllt, Begründung im Code) und
machte den Lauf 100-mal langsamer; die Ergebnisse waren gleich. Dafür fehlte zunächst der Fall, dass
der Kopf von rechts kommend auf dem Schnappschuss steht; jetzt sind beide Seiten abgedeckt.

### Validierung (Punkt 1)

Zweites Programm `direkt.c`: direkte Simulation Zelle für Zelle, eigene Token-Zerlegung, eigene
Schnappschuss-Erkennung, Automat aus `zyklus2.c` (PR 9, unabhängig von `automat.py` geschrieben).
Verglichen wird je Schnappschuss die Zeile `n r crc32(Token-Liste)`.

| Start | bis | Schnappschüsse | gleich | Rückfall-Sätze gleich |
|---|---|---|---|---|
| A | 10^9 | 19.869 | ja | 15 von 15 |
| C | 10^9 | 19.841 | ja | 20 von 20 |
| D | 10^9 | 19.937 | ja | 15 von 15 |
| A | 10^10 (crc nur bei r = 0) | 63.424 | ja | 23 von 23 |
[ACTIONS_VALID]

Negativkontrollen (`ergebnisse/negativkontrollen.txt`), alle schlagen an: Kostenformel N1 mit c = 13,
N2 mit k+4, LG fügt (1,3) an (Abweichung in Zeile 15, 14 bzw. 7); in `direkt.c` VS mit p+6 (32 statt 15
Sätze).

## 2. Wie weit gerechnet

| Start | Schritte | Phasen | davon Automat | Rückfälle VS | nicht anwendbar | Zyklusübergänge |
|---|---|---|---|---|---|---|
| A | 1,0·10^15 | 20.392.579 | 20.389.187 (99,983 %) | 450 | 336 (+14 Übergänge) | 2.606 |
| C | 1,0·10^15 | 20.393.026 | 20.389.709 (99,984 %) | 441 | 270 (+11) | 2.606 |
| D | 1,0·10^15 | 20.393.027 | 20.389.659 (99,983 %) | 445 | 317 (+7) | 2.606 |
[ACTIONS_TABELLE]

Halt: Im Durchlaufmodell (Rückfälle, Übergänge) wird jeder TM-Schritt abgebildet; dort trat kein Halt
auf. **Im übersprungenen Teil (Automatenphasen) wird Halt nicht geprüft.** Die direkte Simulation prüft
jeden Schritt bis 10^12 [ACTIONS_HALT].

## 3. Formen am linken Ende (Punkt 3)

Gesammelt: jede Phase, die der Automat aus PR 9 nicht erklärt, und jeder Zyklusübergang, den die
Zyklusfunktion aus PR 9 nicht erklärt. Bis 10^15: 955 Fälle (A 350, C 281, D 324). Jedes Fenster beginnt
höchstens 50 Token vom linken Bandende (die Liste hat bei 10^15 rund 7.800 Token).

**Definitionen** (gleich in `formen.py` und `formen2.awk`):
- *Fenster*: der Teil der Token-Liste, der sich ändert (gemeinsamer Anfang und gemeinsames Ende
  abgeschnitten; bei Übergängen das rechte Ende ohne Fressen/J).
- *Form*: Fenster vorher → nachher, das letzte Token als Parameter p, dazu die Marke R (Fenster beginnt
  am linken Bandende) oder I.
- *Kern*: die Gruppe unregelmäßiger Token an der Grenze, je Token nur Trenner und "0 / ungerade /
  gerade", dazu die Marken R/I und frei/alt (alt = links vom Kern steht noch ein unregelmäßiges Token).
- *Kernmuster*: der Kern ohne die Marken.

**Kennzahl: neue Formen je Zehnerpotenz** (alle drei Starts zusammen; je Start in
`ergebnisse/formen_lokal_1e15.txt`):

| Schritte | Fälle | neue Formen | neue Kerne | neue Kernmuster |
|---|---|---|---|---|
| bis 10^8 | 32 | 11 | 7 | 6 |
| 10^8–10^9 | 18 | 3 | 2 | 1 |
| 10^9–10^10 | 24 | 8 | 3 | 3 |
| 10^10–10^11 | 44 | 5 | 1 | 1 |
| 10^11–10^12 | 59 | 9 | 3 | 1 |
| 10^12–10^13 | 110 | 1 | 0 | 0 |
| 10^13–10^14 | 251 | 10 | 1 | 0 |
| 10^14–10^15 | 417 | 10 | 1 | 0 |
| **gesamt** | **955** | **57** | **18** | **12** |
[ACTIONS_FORMEN]

Je Start einzeln: neue Formen in den letzten drei Zehnerpotenzen A 2, 8, 7; C 4, 3, 6; D 0, 5, 8.

Die 12 Kernmuster mit Häufigkeit bis 10^15 (Schreibweise: Zahl = Trenner 1, Punkt = Trenner 0;
0/o/e = n null/ungerade/gerade):

| Kernmuster | Fälle | erstes Auftreten | Beispiel (Form) |
|---|---|---|---|
| `0 e` (VS) | 556 | 3,6·10^3 | `1 1 1 0 2 p → 4 .p+4` |
| `.0 .o` | 141 | 4,3·10^3 | `.0 .7 p → 1 1 1 1 1 0 .p+4` |
| `0 .0 e` | 88 | 5,0·10^7 | `1 1 0 .0 2 p → 0 3 .p+3` |
| `e` (ganz links) | 79 | 3,0·10^8 | `4 p → 1 1 1 .p+3` |
| `0 .o .0 e` | 34 | 2,1·10^6 | `1^7 0 .1 .0 14 p → 0 3^7 .p+3` |
| `.o .o` | 16 | 5,9·10^9 | `.1 .5 p → 1 1 1 1 1 0 .p+4` |
| `0 .0 .o` | 14 | 3,1·10^9 | `0 .0 .11 p → 5 3 2 .p+4` |
| `0 0` | 14 | 3,1·10^9 | `1 1 1 0 0 p → 0 .1 .p+4` |
| `.o` | 4 | 21 | Anlauf |
| keine Grenze | 7 | 46 | Anlauf |
| `e .0 e` | 1 | 1,6·10^10 | `0 .2 3 2 .0 16 p → …` |
| `0 .e e .0 e` | 1 | 4,1·10^11 | |

Zweites Programm: `formen2.awk` (getrennt geschrieben, awk) liefert für alle drei Starts einzeln und
zusammen **dieselben** Zahlen in jeder Zeile. Die Rückfall-Sätze selbst bestätigt `direkt.c` bis
10^10 lokal [ACTIONS_DIREKT]. Negativkontrollen: ohne R/I- und frei/alt-Marken 12 statt 18 Kerne; ohne
Abschneiden des gemeinsamen Anfangs 104 statt 57 Formen, in beiden Programmen gleich.

## 4. Urteil (Punkt 4) und Regelvorschlag

### Warum (a)

1. **Kernmuster sättigen.** 12 Muster, das letzte neue bei 4,1·10^11; danach 778 Fälle (10^12 bis 10^15) ohne neues Muster.
   [ACTIONS_URTEIL]
2. **Neue Formen sind neue Parameter.** Ich habe die 21 neuen Formen ab 10^12 einzeln angesehen: alle
   gehören zu einem bekannten Kern. Beispiel: `1^5 5 3 3 3 1 3 0 16 p → 0 .2 3 3 3 7 5 5 5 2 .p+6` ist
   die VS-Regel mit einer Zone, die nicht nur aus Einsen besteht.
3. **Innerhalb eines Kerns stückweise linear.** Test `autofit.py`: künstliche Phasen mit zufälligen
   Zonen (bis 5 bzw. 10 Token links vom Kern, Werte 1 bis 15), je Gruppe (Zonenlänge, Zahlen im Kern,
   Klasse des ersten und letzten Zonen-Tokens) die Gestalt der Ausgabe bestimmt und jede Gestalt mit
   einer linearen Formel angepasst. Ergebnis für alle 8 Familien: **jede geprüfte Gestalt exakt
   linear** (zusammen über 5.000 Gruppen, 0 Ausnahmen), höchstens 3 Gestalten je Gruppe
   (`ergebnisse/autofit_k5.txt`, `autofit_k10.txt`). Negativkontrolle (nichtlinearer Zusatz
   (p·p)//7): 196 von 196 Gestalten "nicht linear".
   Ausgelassen habe ich Proben, bei denen die Phase über p hinaus auch das nächste Token ändert (z. B.
   Zone leer und Kern `.0 .1`); dort ist nur das Fenster größer als in meiner Vorlage.

### Regelvorschlag: VS-Familie vollständig (`vsfam.py`)

Lage: links nur reguläre Token c_1 … c_k (alle (1, ungerade), bis zum Bandende), dann (1,0), dann die
Grenze (1,f) mit f gerade ≥ 2, dann (t,p). m = f/2 + 3, g = f + 4 − 2k, 1^x = x-mal (1,1).

| Fall | Ergebnis |
|---|---|
| k ≥ m (nur die letzten m Token z_1 … z_m zählen) | (1,z_1−1), (0,z_2+1), (1,z_3+2) … (1,z_{m−2}+2), (1,z_{m−1}+1), (0,p+3+z_m) |
| k = 0 | 1^(f−1), (1,0), (0,p+4) |
| k = 1 | 1^(c_1−1), (0,2), (0,f+1), (t,p) |
| k = 2, c_1 = 1 | 1^(f−1), (1,0), (0,p+5+c_2) |
| k = 2, c_1 ≥ 3 | 1^(f+c_1−4), (1,0), (0,p+7+c_2) |
| k = 3, c_1 ≥ 3, g = 0 | 1^(c_1−2), (0,c_2+4), (0,p+3+c_3) |
| k = 3, sonst | 1^(g+max(0,c_1−3)), (1,c_2+3 bzw. +5 bei c_1 ≥ 3), (0,p+3+c_3) |
| 4 ≤ k < m, c_1 = 1 | 1^g, (1,c_2+4), M |
| 4 ≤ k < m, c_1 ≥ 3, g > 0 | 1^(g+c_1−3), (1,c_2+6), M |
| 4 ≤ k < m, c_1 ≥ 3, g = 0 | 1^(c_1−2), (0,c_2+5), M |

mit M = (1,c_3+2) … (1,c_{k−2}+2), (1,c_{k−1}+1), (0,p+3+c_k). Die VS-Regel aus PR 9 ist der erste Fall
mit lauter Einsen.

Prüfung: 10.000 Zufallsfälle (f bis 30, k bis m+3, Werte bis 13) gegen das Durchlaufmodell: alle richtig
(`ergebnisse/vstest.txt`). Alle beobachteten Fälle mit Kern `0 e` und "frei" bis 10^15: 537 von 537
richtig (`ergebnisse/abdeck_lokal_1e15.txt`; die übrigen 19 mit diesem Kernmuster sind 13 Zyklusübergänge und 6 "alt"-Fälle). Negativkontrolle (c_2+5 statt c_2+4 in einem Fall): 66 von 500 Zufallsfällen falsch.

### Was zu einem vollständigen Regelsatz fehlt

- Formeln für die übrigen 7 Familien (zusammen 42 % der Fälle). Der Linearitätstest sagt, dass es sie
  gibt; aufgeschrieben und gegen alle Fälle geprüft sind sie nicht. Grobe Schätzung des Aufwands:
  1 bis 2 Blöcke (unbelegt).
- Die "alt"-Fälle (7 von 955): zwei unregelmäßige Gruppen nahe beieinander. Ob das endlich viele Regeln
  bleibt, ist offen; die Fälle sind selten, ihr Anteil steigt nicht (0,7 %).
- Randschritte im Zyklusübergang, die das linke Ende treffen (32 Fälle): dieselben Kerne, aber mit dem
  verkürzten Fenster aus PR 9. Nicht einzeln geprüft.
- Schrittformeln für die neuen Regeln (für den Beschleuniger nötig, für einen Beweis nicht).

## 5. Empfehlung

**Weiter, aber noch nicht als Rocq-Projekt.** Nächster Schritt wäre ein Analyse-Thread: alle 8
Familien als Regeln aufschreiben, den Beschleuniger damit erweitern und zeigen, dass bis 10^17 kein
einziger Rückfall mehr nötig ist (Ziel: Rest 0). Erst wenn das steht, lohnt die Suche nach einer
Invariante gegen Halt, und erst danach Rocq. Abbrechen würde ich, wenn dabei neue Kernmuster
auftauchen oder die "alt"-Fälle eigene Regelketten brauchen.

## 6. Prüfweg und Dateien

- `beschleuniger.py` (Modi `pruef`, `lauf`), `direkt.c` (zweites Programm), Workflow
  `.github/workflows/linkes_ende.yml` (startet bei Änderung von `auftrag.txt`).
- `formen.py`, `formen2.awk` (Zählung, zwei Programme), `vsfam.py`, `vstest.py`, `abdeck.py`
  (VS-Familie), `autofit.py` (Linearitätstest), `synth.py` (künstliche Phasen von Hand).
- `ergebnisse/`: Validierung, Negativkontrollen, Rückfall-Protokolle bis 10^15 (gz), Zählungen.

Aufrufe (im Ordner `analyse/gruppe1/linkes_ende/`):

```
gcc -O2 -o direkt direkt.c
./direkt A 1e9 1e9 d_A.txt d_A_f.txt                    # direkte Simulation
python3 beschleuniger.py A 1e9 pruef b_A.txt 1e9         # Schnappschuesse
cmp d_A.txt b_A.txt
python3 beschleuniger.py A 1e15 lauf l_A                 # l_A_rueckfall.txt, l_A_uebergang.txt
python3 formen.py l_A_rueckfall.txt l_C_rueckfall.txt l_D_rueckfall.txt
sed 's/ #.*//' l_[ACD]_rueckfall.txt | sort -s -n -k1,1 | awk -f formen2.awk
python3 vstest.py 10000 1 ; python3 abdeck.py l_*_rueckfall.txt ; python3 autofit.py VS 40000 5
```

## 7. Abschluss

[ABSCHLUSS]
