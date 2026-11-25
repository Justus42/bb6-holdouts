# Gruppe 1 (114, 367, 378): linkes Ende, Entscheidungstest

Stand 25.11.2026. Reine Analyse, **kein Rocq**. Werkzeuge und Rohergebnisse in `analyse/gruppe1/linkes_ende/`.
Auftrag: Justus' Nachricht vom 25.11. (Punkte 1 bis 4, Abbruchkriterium nach 1 Block).

## Ergebnis in Kürze

- **Urteil: weder (a) noch (b) sauber erreicht.** Auf der Ebene der Grundmuster ("Kernmuster") sieht es
  nach (a) aus, aber mit zwei Warnzeichen aus den Läufen bis 10^17. Bis 10^15 hatte ich (a) mit
  Einschränkung geschrieben; das nehme ich teilweise zurück.
- **Was für (a) spricht:** Alle 2.877 Fälle, die der Automat nicht erklärt (drei Starts, bis 10^17),
  gehören zu 13 Kernmustern. Innerhalb eines Kerns ist das Ergebnis stückweise linear in den Zahlen.
  Die größte Familie (VS, 59 % der Fälle) ist vollständig als Regel mit 11 Fällen aufgeschrieben und trifft
  alle 1.656 geprüften Fälle bis 10^17, keinen falsch.
- **Warnzeichen 1:** Das 13. Kernmuster (`0 0 e`) kam erst bei 8,2·10^16, nach 2.400 Fällen ohne neues
  Muster. Es ist eine kleine Variante der VS-Lage (`0 0 p → .p+2`), aber neu. Sättigung ist damit nicht
  belegt, nur wahrscheinlich langsam.
- **Warnzeichen 2:** Die Fälle, in denen zwei unregelmäßige Gruppen nahe beieinander stehen ("alt"),
  werden häufiger: 0,7 % bis 10^15, 0,9 % zwischen 10^15 und 10^16, 1,5 % zwischen 10^16 und 10^17
  (31 Fälle). Für sie gibt es keine Regel. Im Entwurf stand "Anteil steigt nicht"; das war falsch.
- **Wörtliche Formen sättigen nicht:** je Zehnerpotenz 10, 10, 19, 15 neue (alle drei Starts zusammen),
  fast alle neue Zahlenwerte in alten Kernen.
- **Beschleuniger:** funktioniert. Bis 10^12 stimmt er mit der direkten Simulation an allen rund 642.000
  Schnappschüssen je Start überein (Schrittzahl und r überall, die ganze Token-Liste an jedem
  Zyklusbeginn; bis 10^9 an jedem Schnappschuss), ebenso alle Rückfall-Protokolle. Gerechnet bis
  1,0·10^17 Schritte je Start (204 Mio. Phasen, 99,995 % davon übersprungen).
- **Wichtig:** In den übersprungenen Phasen wird **Halt nicht geprüft**. Geprüft ist Halt nur bis 10^12
  (direkte Simulation, jeder Schritt, alle drei Starts: kein Halt) und in den Rückfällen bis 10^17.

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
| A, C, D | 10^12 (Actions, crc nur bei r = 0) | 642.050 / 642.176 / 642.089 | ja | 52 / 60 / 65, alle gleich |

Negativkontrollen (`ergebnisse/negativkontrollen.txt`), alle schlagen an: Kostenformel N1 mit c = 13,
N2 mit k+4, LG fügt (1,3) an (Abweichung in Zeile 15, 14 bzw. 7); in `direkt.c` VS mit p+6 (32 statt 15
Sätze).

## 2. Wie weit gerechnet

| Start | Schritte | Phasen | davon Automat | Rückfälle VS | nicht anwendbar | Zyklusübergänge |
|---|---|---|---|---|---|---|
| A | 1,0·10^15 | 20.392.579 | 20.389.187 (99,983 %) | 450 | 336 (+14 Übergänge) | 2.606 |
| C | 1,0·10^15 | 20.393.026 | 20.389.709 (99,984 %) | 441 | 270 (+11) | 2.606 |
| D | 1,0·10^15 | 20.393.027 | 20.389.659 (99,983 %) | 445 | 317 (+7) | 2.606 |
| A | 1,0·10^17 | 204.066.180 | 204.055.536 (99,995 %) | 1.454 | 944 (+31) | 8.246 |
| C | 1,0·10^17 | 204.061.203 | 204.050.725 (99,995 %) | 1.362 | 870 (+31) | 8.246 |
| D | 1,0·10^17 | 204.072.439 | 204.061.809 (99,995 %) | 1.412 | 972 (+29) | 8.246 |

Die Zeilen bis 10^15 sind lokal gerechnet, die bis 10^17 in Actions (Run 45614962053; Laufzeit 1,8 bis
3,3 Stunden je Start). Die Rückfall-Protokolle aus Actions sind bis 10^15 zeilengleich mit den lokalen.

Halt: Im Durchlaufmodell (Rückfälle, Übergänge) wird jeder TM-Schritt abgebildet; dort trat kein Halt
auf. **Im übersprungenen Teil (Automatenphasen) wird Halt nicht geprüft.** Die direkte Simulation prüft
jeden Schritt bis 10^12: in keinem der drei Starts liest A eine 1 (`A_liest_1=0`). Zwischen 10^12 und
10^17 ist Halt also nur in rund 0,005 % der Phasen geprüft.

## 3. Formen am linken Ende (Punkt 3)

Gesammelt: jede Phase, die der Automat aus PR 9 nicht erklärt, und jeder Zyklusübergang, den die
Zyklusfunktion aus PR 9 nicht erklärt. Bis 10^15: 955 Fälle (A 350, C 281, D 324); bis 10^17: 2.877
(A 975, C 901, D 1.001). Jedes Fenster beginnt
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
| 10^15–10^16 | 696 | 19 | 1 | 0 |
| 10^16–10^17 | 1.226 | 15 | 1 | 1 |
| **gesamt** | **2.877** | **91** | **20** | **13** |

Die Zeilen ab 10^15 stammen aus Actions (`ergebnisse/actions_auswertung.txt`), je Start dort einzeln.
Neue Formen je Start in den beiden letzten Zehnerpotenzen: A 8, 12; C 12, 16; D 10, 16.

Je Start einzeln: neue Formen zwischen 10^12 und 10^15 A 2, 8, 7; C 4, 3, 6; D 0, 5, 8.

Die Kernmuster mit Häufigkeit bis 10^15 (bis 10^17 kamen `0 0 e` bei 8,2·10^16 dazu, ein Fall:
`I 0 0 p → .p+2`, und der Kern `R frei 0 .0 .o` mit bekanntem Muster bei 3,3·10^15) (Schreibweise: Zahl = Trenner 1, Punkt = Trenner 0;
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
10^10 lokal und bis 10^12 in Actions (alle drei Starts zeilengleich). Negativkontrollen bis 10^15: ohne
R/I- und frei/alt-Marken 12 statt 18 Kerne; ohne Abschneiden des gemeinsamen Anfangs 104 statt 57
Formen. Bis 10^17: 13 statt 20 Kerne bzw. 186 statt 91 Formen. Jeweils in beiden Programmen gleich; auch
bis 10^17 liefern `formen.py` und `formen2.awk` in jeder Zeile dieselben Zahlen, je Start und zusammen.

## 4. Urteil (Punkt 4) und Regelvorschlag

### Was für (a) spricht

1. **Kernmuster sättigen fast.** 12 Muster bis 4,1·10^11, danach über 2.000 Fälle ohne neues Muster, dann ein
   13. Muster bei 8,2·10^16 (ein einziger Fall). Neue Muster werden also sehr selten, hören aber nicht
   nachweislich auf.
2. **Neue Formen sind neue Parameter.** Die 21 neuen Formen zwischen 10^12 und 10^15 habe ich einzeln
   angesehen: alle gehören zu einem bekannten Kern. Beispiel: `1^5 5 3 3 3 1 3 0 16 p → 0 .2 3 3 3 7 5 5 5 2 .p+6`
   ist die VS-Regel mit einer Zone, die nicht nur aus Einsen besteht. Die 34 neuen Formen ab 10^15 habe
   ich nicht einzeln angesehen; 33 davon gehören zu bekannten Kernmustern (Zählung, nicht Einzelprüfung).
3. **Innerhalb eines Kerns stückweise linear.** Test `autofit.py`: künstliche Phasen mit zufälligen
   Zonen (bis 5 bzw. 10 Token links vom Kern, Werte 1 bis 15), je Gruppe (Zonenlänge, Zahlen im Kern,
   Klasse des ersten und letzten Zonen-Tokens) die Gestalt der Ausgabe bestimmt und jede Gestalt mit
   einer linearen Formel angepasst. Ergebnis für alle 8 Familien: **jede geprüfte Gestalt exakt
   linear** (zusammen über 5.000 Gruppen, 0 Ausnahmen), höchstens 4 Gestalten je Gruppe
   (`ergebnisse/autofit_k5.txt`, `autofit_k10.txt`). Negativkontrolle (nichtlinearer Zusatz
   (p·p)//7): 196 von 196 Gestalten "nicht linear".
   Ausgelassen habe ich Proben, bei denen die Phase über p hinaus auch das nächste Token ändert (z. B.
   Zone leer und Kern `.0 .1`); dort ist nur das Fenster größer als in meiner Vorlage.

### Was dagegen spricht

1. **Wörtliche Formen sättigen nicht** (10, 10, 19, 15 neue je Zehnerpotenz). Für sich allein harmlos,
   solange es nur neue Zahlenwerte sind; für einen Regelsatz heißt das aber: Die Regeln müssen beliebige
   Zonen links vom Kern abdecken, nicht nur die beobachteten.
2. **Die "alt"-Fälle wachsen.** Anteil 0,7 % → 0,9 % → 1,5 % (bis 10^15, 10^15–10^16, 10^16–10^17);
   absolut 7, 6, 18 Fälle. Dort stehen zwei unregelmäßige Gruppen dicht beieinander. Ob das zwei
   unabhängige bekannte Kerne sind, die sich nacheinander auflösen, oder neues Verhalten, habe ich nicht
   geprüft. Wenn es neues Verhalten ist und der Anteil weiter steigt, ist das (b).
3. **Neue Kernmuster sind nicht ausgeschlossen** (siehe `0 0 e` bei 8,2·10^16).

**Zusammen:** Für die "frei"-Fälle (98,9 %) halte ich endlich viele Regeln mit Parametern für
wahrscheinlich, belegt ist es nur für die VS-Familie. Für die "alt"-Fälle ist es offen, und genau die
nehmen zu. Deshalb kein (a) im Sinn des Auftrags.

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
Bis 10^17 (Actions): 1.656 von 1.656 geprüften Fällen richtig, 0 falsch; 43 weitere "frei"-Fälle mit
diesem Kern liegen außerhalb des Geltungsbereichs der Regel (Zyklusübergänge, Band-Rest) und sind
ungeprüft.

### Was zu einem vollständigen Regelsatz fehlt

- Formeln für die übrigen 7 Familien (zusammen 42 % der Fälle). Der Linearitätstest sagt, dass es sie
  gibt; aufgeschrieben und gegen alle Fälle geprüft sind sie nicht. Grobe Schätzung des Aufwands:
  1 bis 2 Blöcke (unbelegt).
- Die "alt"-Fälle (31 von 2.877, Anteil steigend): zwei unregelmäßige Gruppen nahe beieinander. Ob das
  endlich viele Regeln bleibt, ist offen.
- Das neue Kernmuster `0 0 e` (ein Fall) als Regel.
- Randschritte im Zyklusübergang, die das linke Ende treffen (32 Fälle): dieselben Kerne, aber mit dem
  verkürzten Fenster aus PR 9. Nicht einzeln geprüft.
- Schrittformeln für die neuen Regeln (für den Beschleuniger nötig, für einen Beweis nicht).

## 5. Empfehlung

**Noch kein Beweisprojekt.** Gruppe 1 jetzt in Rocq anzugehen, halte ich für verfrüht: Es fehlen ein
vollständiger Regelsatz und jede Idee für eine Invariante gegen Halt.

Wenn weiter, dann mit **einem** gezielten Analyse-Block und klarem Kriterium: die "alt"-Fälle
(31 Stück) zerlegen. Frage: Lösen sie sich als zwei bekannte Kerne nacheinander auf (dann reichen die
bekannten Familien, und ein Regelsatz ist realistisch), oder entsteht dort neues Verhalten (dann (b),
abbrechen)? Das ist billiger als alle 8 Familien aufzuschreiben und entscheidet die Frage besser.
Sonst abbrechen und Gruppe 1 ruhen lassen.

## 6. Prüfweg und Dateien

- `beschleuniger.py` (Modi `pruef`, `lauf`), `direkt.c` (zweites Programm), Workflow
  `.github/workflows/linkes_ende.yml` (startet bei Änderung von `auftrag.txt`).
- `formen.py`, `formen2.awk` (Zählung, zwei Programme), `neukern.py` (erstes Auftreten je Kern),
  `vsfam.py`, `vstest.py`, `abdeck.py` (VS-Familie), `autofit.py` (Linearitätstest), `synth.py`
  (künstliche Phasen von Hand).
- `auswertung.sh` mit Workflow `.github/workflows/linkes_ende_auswertung.yml`: wertet die Artefakte eines
  Actions-Laufs in Actions aus (startet bei Änderung von `auswertung.txt`). Grund: Die Artefakt-Ablage
  von GitHub ist aus der Cloud-Sitzung gesperrt (HTTP 403); ich habe sie nicht umgangen, sondern die
  Auswertung dorthin verlegt, wo die Daten liegen. Ergebnis: `ergebnisse/actions_auswertung.txt`.
- `ergebnisse/`: Validierung, Negativkontrollen, Rückfall-Protokolle bis 10^15 (gz), Zählungen,
  Actions-Auswertung bis 10^17. Die Protokolle bis 10^17 liegen nur als Actions-Artefakt (Run
  45614962053, 90 Tage).

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

**Ergebnis.** Der Phasen-Beschleuniger stimmt mit der direkten Simulation überein (bis 10^12, alle drei
Starts) und rechnet bis 10^17. Die Fälle am linken Ende ordnen sich in 13 Grundmuster mit linearen
Parametern; das spricht für (a), aber ein neues Muster bei 8,2·10^16 und der steigende Anteil
unerklärter "alt"-Fälle (bis 1,5 %) verhindern ein klares (a). Urteil: offen, Tendenz (a) für 99 % der
Fälle, kein Beweisprojekt jetzt.

**Belege.** Commits 3617b26 (Beschleuniger, `direkt.c`, Workflow), d622b8d (Formen, VS-Familie,
Linearitätstest), 590aadf (Entwurf), 82764ef und 0591034 (Auswertung in Actions, `neukern.py`) und der
Schluss-Commit dieses Berichts. Actions: Run 45614962053 (direkt bis 10^12, Beschleuniger bis 10^17,
Vergleich grün), Runs 45657021990 und 45658664733 (Auswertung). Lokal: `ergebnisse/validierung_lokal.txt`,
`negativkontrollen.txt`.

**Abweichungen und eigene Fehler.**
- Beschleuniger: Die erste Fassung war durch eine unnötig strenge Prüfung 100-mal langsamer (Abschnitt 1),
  und die Schnappschuss-Erkennung im Rückfall fehlte zunächst für eine Seite. Behoben, neu validiert.
- Die erste Negativkontrolle für die Formen-Zählung schlug nicht an; ersetzt durch zwei, die anschlagen.
- `vsfam.py` hatte zunächst einen Fall zu wenig (k = 3, g = 0, c_1 ≥ 3; 13 von 3.000 Zufallstests
  falsch). Ergänzt, danach 10.000 von 10.000 richtig.
- Im Entwurf (Stand 10^15) stand "Urteil (a) mit Einschränkung" und "alt-Anteil steigt nicht". Beides
  hielt den Daten bis 10^17 nicht stand.
- Die Artefakt-Ablage war gesperrt; Auswertung deshalb in Actions statt lokal (zusätzlicher Workflow,
  nicht im Auftrag vorgesehen). Ein Test-Lauf der Auswertung (Run 45633825750) lief absichtlich vor
  Ende der Rechnung und hat keine Aussagekraft.
- Beim Aufräumen habe ich versehentlich eine nicht committete Ergänzung von `autofit_k10.txt` verworfen
  und die fehlende Familie `e` neu gerechnet (12 von 12 Gestalten linear, wie bei k = 5).

**Offene Punkte.** Halt zwischen 10^12 und 10^17 nur in den Rückfällen geprüft. Die "alt"-Fälle, das
Muster `0 0 e` und 7 der 8 Familien haben keine aufgeschriebene Regel. Eine Invariante gegen Halt fehlt
ganz. Die 34 neuen Formen ab 10^15 sind nur gezählt, nicht einzeln angesehen.

**Empfehlung.** Kein Rocq-Projekt jetzt. Höchstens ein weiterer Analyse-Block zu den "alt"-Fällen mit
dem Kriterium aus Abschnitt 5; sonst abbrechen.

**Verbrauch.** Rund 1,5 Blöcke Arbeit (Budget 2), dazu rund 4 Stunden Laufzeit in Actions.
