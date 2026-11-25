# Gruppe 1 (114, 367, 378): Halt als verbotenes Muster

Stand 25.11.2026. Reine Analyse, **kein Rocq**. Werkzeuge und Rohergebnisse in `analyse/gruppe1/verboten/`.
Auftrag: Justus' Nachrichten vom 25.11. (17:33, 17:48, 18:14, 18:22).

## Ergebnis in Kürze

- **Notwendiges Muster:** Jedem Halt geht ein Ereignis **K(C)** voraus: Zustand C tritt von links auf eine
  Zelle x, und x, x+1, x+2 lesen `0 1 1`. Das gilt für jeden Lauf, der auf einem Band startet, das rechts
  vom Startkopf leer ist (also für alle drei Läufe ab Leerband). **Von Hand bewiesen**, nicht in Rocq.
  Notwendig, nicht hinreichend.
- **Zählung:** K(C) kommt in keinem der drei Läufe vor, gezählt mit zwei unabhängigen Programmen bis 10^9
  (lokal) und 10^10 (Actions), Ergebnisse gleich. Der nächste Verwandte ist K(D) (gleiche Zellen, Zustand D
  statt C), rund 1,63 Mio. Mal bis 10^9 je Start. Darauf folgt jedes Mal der Prüfpunkt `C> 1 1 0`, also
  kein Halt, weil die vierte Zelle 0 ist.
- **Halt lückenlos ausgeschlossen bis 10^12** (direkte Simulation, jeder Schritt, alle drei Starts).
  Darüber nur **bedingt**: bis 10^22 für alle drei Starts (lokal; der Actions-Lauf rechnet weiter, Ergebnis folgt) (Zyklus-Beschleuniger). Die Bedingung lautet, dass die Regeln des
  Phasen-Automaten für alle vorkommenden Listen stimmen und in den übersprungenen Phasen kein K(C)
  entsteht. Belegt ist das nur empirisch, nicht bewiesen (Abschnitt 4).
- **Kein Haltekandidat, kein K(C)** bis dahin, weder in den gerechneten Rückfall-Phasen noch in den
  900 Stichproben jenseits 10^12 (300 je Start).

## 1. Das Muster

### 1.1 Rückwärts vom Halt (von Hand, aus der Tabelle)

Tabelle `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC`.

- **H0:** Halt nur über A1. A wird nur über E1 erreicht, E nur über C1. Also gilt: Halt bei h ⟺ C steht
  auf x = h−2 und x, x+1, x+2 = `1 1 1` ("C vor 111").
- C wird erreicht über B0 (0RC) und D0 (1RC) von links, über F1 (0LC) von rechts.

### 1.2 Satz K(C)

**Voraussetzung:** Der Lauf startet bei p0 in einem beliebigen Zustand, und jede Zelle rechts von p0 ist 0.
Das Band links von p0 ist beliebig.

**Aussage:** Steht C irgendwann auf x vor `1 1 1` (Halt), dann ist C vorher von links auf x getreten, als
dort `0 1 1` stand (K(C)). Zweite Stufe: Noch früher stand `C> 0 1` auf x+1, und danach las D eine 1 auf x.

**Beweis (von Hand):** Jede 1 rechts vom Kopf wurde geschrieben, als der Kopf diese Zelle zuletzt nach
links verließ. Nach links mit Schreiben einer 1 gehen nur C0 (1LD) und F0 (1LB). F scheidet aus, weil F nur
über B1 betreten wird und B1 auf x+1 eine 0 schreibt. Daraus folgen Stufe 1 und 2.

**Grenzen:**
- Ohne die Voraussetzung ist der Satz falsch. Justus' Gegenbeispiel `C> 1 1 0 0 1 1 1` hält nach
  6 Schritten ohne K(C). Gegenprobe `lemma_test.py … rechts`: 9.998 Halte ohne K(C).
- Mit der Voraussetzung: 200.000 Zufallsläufe, 1.164 Halte, alle mit K(C) und Stufe 2
  (`ergebnisse/lemma_test.txt`).
- Der Satz ist eine Aussage über den ganzen Lauf ab Leerband. Für eine einzelne Phase mitten im Lauf gilt
  er nicht von selbst, weil das Band rechts vom Kopf dort nicht leer ist.

### 1.3 Notwendig, nicht hinreichend

Was nach K(C) passiert, hängt davon ab, wie C auf x kam:

- **Über B0** (x−1 = 0): Halt nach 5 Schritten, immer, unabhängig von allem links davon.
- **Über D0** (x−1 = 1, die "1 links daneben"): kein sofortiger Halt. D liest die 1 und geht als B nach
  links. Mit leerem Band rechts von x+2 hält der Lauf je nach den Zellen links davon nach 8, 11, 18 oder 51
  Schritten. Bei `1 0 1` links hält er in 200 Schritten nicht (Aufzählung aller Muster bis Länge 3).

Darum wird im Beschleuniger jedes K(C) einzeln weiterverfolgt (Abschnitt 3).

### 1.4 In Token-Sprache

Im Durchlaufmodell bedeutet K(C), dass der rechte Stapel oben `b0 b1 b1` trägt oder `b0 b1` und dann ein
Wort `100`. Das passiert, wenn C einen Durchlauf über `100^m` beendet oder ein Einzelschritt nach rechts
in C endet. An beiden Stellen zählen die Programme mit.

## 2. Zählung bis 10^9 / 10^10 (zwei Programme)

- `zaehl_direkt.c` (Bitebene) und `zaehl_durchlauf.py` (Durchlaufmodell) zählen jeden Rechtsschritt
  nach Zustand und den drei Zellen davor.
- Bis 10^9 lokal (A, C, D) und bis 10^10 in Actions (Run 45668615893, Jobs durchlauf): alle Zahlen gleich.
- Negativkontrollen `ZAEHL_FEHLER=zustand` und `ZAEHL_FEHLER=s1` schlagen an.

| bis 10^9, Start A | Anzahl |
|---|---|
| K(C) = `C> 0 1 1` | **0** (B, C, D: 0) |
| `C> 1 1 1` (Halt) | 0 |
| K(D) = `D> 0 1 1` | 1.630.856 |
| `C> 1 1 0` (Prüfpunkt) | 1.638.656 |

So nah kommt der Lauf an ein K(C) heran: Bei K(D) steht dasselbe Zellmuster vor dem Kopf, nur im falschen
Zustand. D schreibt 1 und geht als C auf x+1, dort steht `1 1 0`. Für einen Halt müsste die vierte Zelle
1 sein. Dann wäre aber nach dem Satz vorher ein K(C) auf x+1 nötig gewesen.

## 3. Halteprüfung im Beschleuniger

Werkzeug: `zyklus_beschl.py` (Zyklusebene), das Durchlaufmodell der Rückfälle steckt in `rechne.c`.

- **Gerechnete Phasen** (Rückfälle VS, "nicht anwendbar", Zyklusübergang): Das Durchlaufmodell erkennt
  Halt (A liest 1) und zählt K(C).
- **Übersprungene Phasen** (Automatenregeln N1, N2, N2s, UA, LE0, LE1, LG, gebündelte N2/N1-Paare):
  Kein Halt, **sofern** die Regel für diese Liste stimmt und in der Phase kein K(C) entsteht. Belege siehe
  Abschnitt 4.
- **K(C) in einer gerechneten Phase:** Schnappschuss davor sichern (Datei und BASE64-Zeile im Log). Der Lauf
  geht weiter, die nächsten 5 Phasen werden ganz im Durchlaufmodell gerechnet.
- **Halt:** Schnappschuss davor sichern, Lauf stoppt. Nachrechnen mit `kandidat_nachrechnen.py`. Es wird
  nichts verkündet.
- **Stichproben (zweite Sicherung):** ab 10^12 30 je Zehnerpotenz. Eine zufällig gewählte Automatenphase
  wird ganz im Durchlaufmodell gerechnet (Halt, K(C)) und mit der Regel verglichen.

**Prüfungen des Werkzeugs:**
- Bis 10^12 alle Zyklusanfänge (Token-Liste per CRC, Schrittzahl) für A, C und D gleich mit
  `linkes_ende/beschleuniger.py`, das bis 10^12 gegen `direkt.c` geprüft ist. Jeder Rückfall wurde
  zusätzlich ganz gerechnet: 0 Abweichungen.
- In Actions bis 10^15 gleich (Run 45675033053, Jobs pruef), Python-Fassung.
- In Actions bis 10^16 mit der C-Fassung (Run 45682765314, Jobs pruef): läuft noch.
- `rechne.c` gegen die Python-Fassung: 8.594 Eingaben (zufällige Bit-Bänder, zufällige Token-Listen, alle
  2.594 echten Rückfall-Listen bis 10^11), 0 verschieden (`ergebnisse/test_rechne_c.txt`). Bis 10^18
  stimmen auch die Schrittzahlen an den Zehnerpotenzen mit dem reinen Python-Lauf (lokal) überein.
- Negativkontrollen, alle schlagen an: `ZB_FEHLER=paar|lokal|ueb` (Abgleich scheitert),
  `stich` (Kandidat gemeldet), `kc` (vorgetäuschtes K(C) wird gesichert und 5 Phasen verfolgt, die
  Schrittzahl bleibt gleich), `RC_FEHLER=1` (457 verschieden).

## 4. Begründung je Regel: warum kein Halt in einer übersprungenen Phase

Bewiesen ist hier nichts (Justus: Regeln jetzt nicht beweisen). Je Regel gibt es drei empirische Belege:

1. **Direkte Simulation bis 10^12, aufgeteilt nach Regel** (`zaehl_direkt.c`, Run 45668615893, Jobs
   direkt): In keinem Start und in keiner Regel kommt ein Rechtsschritt
   `C 011` (K(C)) oder `C 111` vor. In jeder Regel treten Rechtsschritte nach C nur als `C 001`, `C 010`,
   `C 100`, `C 101`, `C 110` auf. Bis 10^12 sind je Start rund 319.000 N1- und N2-Phasen dabei, dazu
   180 bis 227 N2s, 202 bis 251 UA, 160 bis 192 LE und 2.271 bis 2.432 LG. Zahlen in
   `ergebnisse/actions_direkt_1e12.txt`.
2. **Zufallstest je Regel** (`regel_test.py`, 3.000 Proben je Regel): zufällige kanonische Listen, auf die
   genau diese Regel passt, mit Zahlen bis 10^5 und r bis 10^6. Ergebnis: Regel stimmt überall (Vergleich
   auf Bitebene), kein K(C), kein Halt (`ergebnisse/regel_test.txt`). In jeder Regel kommen dieselben
   18 Rechtsschritt-Typen vor, darunter für C nur `001 010 100 101 110`, also nie `011` oder `111`.
   - Negativkontrolle: zufällige Bit-Bänder ohne Regelbedingung, Phasen bis zum Halt gerechnet. 8 Halte,
     alle 8 mit erkanntem K(C).
3. **Stichproben im Lauf jenseits 10^12:** 900 Stichproben zwischen 10^12 und 10^22 (300 je Start), alle ohne Halt
   und ohne K(C), und alle stimmen mit der Regel überein. Getroffen wurden nur N1 und N2 (siehe Abschnitt 7).

Fällt die Bedingung einer Regel weg, wird nicht übersprungen, sondern zurückgefallen. Das gilt, wenn das
rechteste Token nicht (1, gerade ≥ 2) ist, die Liste links nicht passt ("links?") oder bei VS und
Sonderfällen. Diese Phasen werden ganz gerechnet.

Lücke: Für Listen, wie sie erst jenseits 10^12 vorkommen, stützt sich "Regel stimmt und kein K(C)" nur auf
den Zufallstest und die Stichproben. Ein Beweis der Regeln (Rocq, wie die Fast-Forward-Lemmata in
PR_Loop4Mono.v) würde die Lücke schließen.

## 5. Lauf Richtung 10^22

Lokal mit `zyklus_beschl.py` (C-Fassung), Logs in `ergebnisse/lokal/zyklus_1e22_*.txt`:

| Start | Schritte | Zeit | Phasen | Zyklen | Token | K(C) | Halt | Stichproben |
|---|---|---|---|---|---|---|---|---|
| A | 1,0000010·10^22 | 453 s | 6,45·10^10 | 146.681 | 440.042 | 0 | nein | 300, alle gleich |
| C | 1,0000141·10^22 | 473 s | 6,45·10^10 | 146.682 | 440.066 | 0 | nein | 300, alle gleich |
| D | 1,0000185·10^22 | 480 s | 6,45·10^10 | 146.682 | 440.079 | 0 | nein | 300, alle gleich |

- Davon gerechnet (Rückfälle, ganz im Durchlaufmodell): je Start rund 190.000 Phasen (Zyklusübergänge,
  VS, Sonder, "links?"). Übersprungen: 99,9997 %.
- Zeit je Zehnerpotenz wächst etwa um den Faktor 2,3. Phasen wachsen wie n^(1/2), Zyklen und Token wie
  n^(1/4).
- Bis 10^18 stimmt die Schrittzahl an jeder Zehnerpotenz mit der reinen Python-Fassung überein.
- int64-Schutz: Die größte Teilsumme der Paarkosten wächst je Zehnerpotenz etwa um den Faktor 5,6
  (6·10^15 bei 10^21). Um 10^24 hätte sie den int64-Bereich gesprengt. Seit 509fb21 wird dort mit
  Python-Zahlen gerechnet.
- Actions-Lauf mit Schutz (Run 45684698614, bis 340 min je Start): läuft noch, das Ergebnis trage ich hier nach.

## 6. Belege

- Commits auf `claude/project-thread-sz20pr`: 4f51e34 (Zähler, Satztest), 79d2ee0 (englische
  Beschreibungen), ad96679 (Zyklus-Beschleuniger, Regeltest), 0bb0c90 (Stichproben, Kandidaten),
  d36cde9 (kein Start durch Push auf main), 14b51e4 (Durchlaufmodell in C), 509fb21 (int64-Schutz)
- Actions: 45668615893 (verboten: direkt bis 10^12, durchlauf bis 10^10, beschleuniger bis 10^14),
  45675033053 (zyklus, Python-Fassung: pruef bis 10^15, lauf), 45682765314 (zyklus, C-Fassung ohne int64-Schutz: pruef bis 10^16; lauf nur bis 10^24 verwertbar), 45684698614 (zyklus, mit Schutz: lauf so weit wie möglich)
- Englische Problembeschreibungen: `analyse/gemini/gruppe1_en.md`, `analyse/gemini/m5_en.md`

## 7. Abweichungen und eigene Fehler

- Den Satz habe ich zuerst ohne Voraussetzung formuliert ("jedem Halt geht C> 0 1 1 voraus"). Das war zu
  weit, Justus' Gegenbeispiel zeigt es. Jetzt steht er mit Voraussetzung da.
- Die erste Negativkontrolle im Regeltest schlug nicht an: Zufällige Token-Listen erzeugen weder Halt noch
  K(C). Ersetzt durch zufällige Bit-Bänder.
- Der Regeltest meldete zuerst "Regel falsch". Ursachen waren Testfehler: nicht kanonische Zufallslisten,
  und die Regel liefert manchmal eine andere Zerlegung desselben Bandes (z. B. `(1,7) (0,0) (1,0) (1,13)`
  statt `(1,21)`). Jetzt wird auf Bitebene verglichen; in 2 von 3.000 N1-Proben tritt das auf.
- Ein Probelauf mit falsch gebündelter Stichprobe meldete einen "Kandidaten". Das war ein Programmfehler,
  kein Halt. Behoben, die Datei ist gelöscht.
- Die Stichproben treffen fast nur N1 und N2, weil die Phase gleichmäßig aus dem Zyklus gezogen wird. Die
  seltenen Regeln (LG, LE, UA, N2s) sind nur über den Zufallstest und die direkte Simulation bis 10^12
  abgedeckt.
- Die Zählung bis 10^17 (Auftrag 17:33) habe ich nicht mit zwei Programmen auf Schrittebene gemacht. Über
  10^10 gibt es nur den Beschleuniger, und der zählt K(C) nur in gerechneten Phasen.

## 8. Offene Punkte und Empfehlung

Offen:
- Ergebnis des Actions-Laufs jenseits 10^22 (Run 45684698614), pruef bis 10^16 (Run 45682765314).
- Die Regeln sind nicht bewiesen. Jenseits 10^12 ist Halt nur unter der Bedingung aus Abschnitt 4
  ausgeschlossen.
- Der Download der Actions-Logs als ZIP ist aus der Sitzung gesperrt (results-receiver.actions.githubusercontent.com,
  403). Ich habe die Zahlen aus den Job-Logs abgeschrieben, nicht umgangen.

Empfehlung: **Das Rechnen nicht weiter treiben.** Mehr Zehnerpotenzen ändern am Status "bedingt" nichts.
Für einen Beweis von Nicht-Halten wäre der nächste Schritt eine Invariante, die K(C) ausschließt. Am
naheliegendsten ist eine Aussage der Form "rechts vom Kopf steht beim Eintritt von C nie `0 1 1`", als
Eigenschaft der Token-Listen, die jede Regel erhält. Die Belege in Abschnitt 4 zeigen, welche
Rechtsschritt-Typen je Regel vorkommen. Das wäre die Liste, die eine solche Invariante abdecken müsste.
Ob das trägt, ist offen; Rocq erst nach deinem OK.
