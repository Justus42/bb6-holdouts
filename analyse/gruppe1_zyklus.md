# Gruppe 1 (114, 367, 378): ganzer Zyklus als Listenregel

Stand 25.11.2026. Reine Analyse, kein Rocq. Werkzeuge und Rohergebnisse in `analyse/gruppe1/zyklus/`.

## Ergebnis in Kürze

- **Zyklusregel: unvollständig, und zwar nur am linken Bandende.** Eine Funktion Liste → Liste für
  einen ganzen Zyklus (`zyklus.py`, zweites Programm `zyklus2.c`) sagt bis 10^9 Schritte
  68 von 76 (Start A), 67 von 76 (C) und 66 von 77 (D) Zyklen exakt voraus. **Keine einzige
  Vorhersage ist falsch.** In den übrigen 8, 9 und 11 Zyklen meldet die Funktion selbst „Regel nicht
  anwendbar“, immer in einer Phase, in der der Lauf das linke Bandende erreicht (13, 18 und 14
  Phasen von je rund 19.800).
- **Justus' Frage „alle Listenelemente gerade“: nein, das bleibt nicht erhalten.** Es gilt nur an
  35 von 77 (A), 33 von 77 (C) und 49 von 78 (D) Zyklusanfängen. Es bricht nicht erst am linken
  Ende, sondern im Lauf selbst: Jede Phase „leiht“ sich eine Einheit vom linken Nachbarn (Regel N2),
  und die nächste gibt sie zurück (N1). Am Zyklusanfang steht die Bruchstelle immer im linken
  Teil der Liste, mindestens 14 Elemente vom rechten Ende entfernt.
- **Was für x zählt, bleibt erhalten:** a ist an allen 232 Zyklusanfängen gerade, also x = a+4b+7
  in allen Fressrunden ungerade. Der Grund ist eine einfache Regel, die an allen 229 Zyklen gilt:
  **a(neu) = drittes Element von rechts + 2.** Das dritte Element war in allen Fällen gerade mit
  Trenner `|`. Das ist ein **Kandidat** für die Invariante, die Regel F braucht, nicht bewiesen.
- **Invariante, die H ausschließt: nein.** Ich habe keine gefunden. Die Normalform „höchstens eine
  Marke“ scheitert an 16 von 232 Zyklusanfängen (zwei Bruchstellen gleichzeitig).

## 1. Schreibweise

Das Band links vom Kopf zerlege ich in Token `(t, n)`: ein Trennerbit t, dann n-mal das Wort `011`.
Ein Trenner aus mehreren Bits wird zu mehreren Token mit n = 0. Kurzform: `5` heißt (1,5),
`.5` heißt (0,5), `0` heißt (1,0).

Zur Textliste aus Teil 1: Ein Token (1,n) mit Trenner `|` ist das Listenelement n−1; ganz rechts
(Element a, direkt am Kopf) ist es n. „Alle Listenelemente gerade“ heißt also: alle Token haben
Trenner 1, alle sind ungerade außer dem rechtesten, das gerade ist. Ein Token mit Trenner 0 oder
gerader Länge nenne ich **unregelmäßig**. Die Sonderstellen `<1>` und `<5>` der Textliste sind
Gruppen unregelmäßiger Token. Eine Ausnahme: Einsen links von der linkesten Null sieht die
Textliste nicht; deshalb weichen Text- und Tokenzählung an genau einem Zyklusanfang ab
(A, Schritt 285.684.587), sonst nirgends.

## 2. Ein Zyklus in fünf Teilen

Zyklusanfang = erster Rechts-Rekord in Zustand C nach dem letzten Pendelschwung. Die Token-Liste
endet rechts auf …, e3, b, a.

1. **Randschritt beim Fressen:** ein Automatenschritt (Abschnitt 3), dessen Grenze die letzten zwei
   Token nicht berücksichtigt.
2. **Fressen:** …, (t3,e3), (t2,b), (1,a) → …, (t3,e3−1), (0,0), (1,x) mit x = a+4b+3 in Token
   (= a+4b+7 in der Textliste).
3. **Übergang J:** …, (t4,e4), (t3,e3'), (0,0), (1,x) → …, (t4,e4−1), (1,e3'+2). Danach beginnt der
   lange Lauf mit x−1 Pendelschwüngen; rechts vom Kopf steht 0 (100)^r 1, r zählt von x−1 auf 0.
4. **x−1 Phasen:** je Pendelschwung genau ein Automatenschritt.
5. **Randschritt auf dem Rückweg:** ein Automatenschritt, Grenze ohne das letzte Token.

Teil 1, 2, 3 und 5 stimmen bis 3·10^8 (Teile einzeln, `check_rand2.py`) und bis 10^9 (ganzer Zyklus)
in allen Fällen.

## 3. Der Phasen-Automat

**Grenze** = das rechteste unregelmäßige Token außer dem letzten. Je Phase gilt genau eine Regel:

| Regel | vorher | nachher |
|---|---|---|
| N1 | Grenze (0,k), k gerade | (1,k+1) |
| N2 | G=(t,g≥1), Grenze (1,k), k gerade | (t,g−1), (0,k+2) |
| N2s | G=(t,g≥1), Grenze (0,k), k ungerade | (t,g−1), (0,k+2) |
| UA | G=(t,g≥1), (1,0), Grenze (0,k), k ungerade | (t,g−1), (0,0), (1,k+2) |
| LE | linkes Ende: (1,0), (t,k) | (1,k+2) |
| VS | (1,1)^(f/2+3), (1,0), Grenze (1,f), f gerade, (t,p) | (1,0), (0,2), (1,3)^((f−2)/2), (1,2), (0,p+4) |
| LG | keine Grenze | (1,1) links anfügen (Band wächst) |

N2 und N1 wechseln sich ab. Das ist der Grund, warum „alle gerade“ nicht erhalten bleibt: N2
verkleinert den Nachbarn G um 1 (gerade Textzahl wird ungerade), die Grenze wandert dabei je zwei
Phasen ein Element nach links. Ist sie am linken Ende angekommen, räumen LE, LG oder VS auf.

Ergebnis bis 10^9, beide Programme gleich (`ergebnisse/auto_*.txt`, `ergebnisse/c_erg_*.txt`):

| Start | Phasen | N1 | N2 | N2s | UA | LE | VS | LG | nicht erklärt |
|---|---|---|---|---|---|---|---|---|---|
| A | 19.787 | 9.618 | 9.581 | 47 | 45 | 33 | 17 | 433 | 13 |
| C | 19.759 | 9.583 | 9.548 | 59 | 45 | 29 | 17 | 460 | 18 |
| D | 19.855 | 9.680 | 9.657 | 34 | 30 | 45 | 9 | 386 | 14 |

## 4. Wo genau die Regel unvollständig ist

Alle 45 nicht erklärten Phasen (`ergebnisse/left_*.txt`) liegen am linken Bandende:

- **VS mit zu wenig Einsen** (27-mal): Links von der Marke stehen weniger als f/2+3 Token (1,1).
  Beobachtete Formen, p = rechter Nachbar:
  `0 2 p → 1 0 .(p+4)`, `1 0 2 → .2 .3`, `1 1 0 2 p → 1 0 .(p+6)`, `1 1 1 0 2 p → 4 .(p+4)`,
  `1 0 6 → .2 .7`, `1 1 0 6 7 → 1 1 1 1 1 0 .13`.
- **Folgeschritt danach** (11-mal): `.0 .7 p → 1 1 1 1 1 0 .(p+4)` und `.0 .11 7 → 1^9 0 .11`.
  Hier wächst das Band links um mehrere Token auf einmal.
- **Seltene tiefe Fälle** (4-mal): z. B. `1^7 0 .1 .0 14 7 → 0 3^7 .10` (A, 2.103.637) und
  `4 5 → 1 1 1 .8` (A, 303.825.454).
- **Anlauf** (3-mal, Schritt 69, 180, 301): `.1 → 2`.

Die Formen wiederholen sich über die drei Starts, aber ich habe keine allgemeine Regel dafür, die
für jede Zahl von Einsen gilt. Eine Tabelle der beobachteten Fälle wäre möglich, wäre aber nur
für die gesehenen Fälle belegt. Das ist die offene Stelle.

## 5. Bedingung H und Invariante

**Parität von a (für Regel F):** Bis 10^9 an allen Zyklusanfängen geprüft, beide Programme:

| Start | Zyklusanfänge | a gerade | a(neu) = e3 + 2 | drei rechte Elemente regulär | alle Elemente gerade |
|---|---|---|---|---|---|
| A | 77 | 77 | 76/76 | 76/76 | 35 |
| C | 77 | 77 | 76/76 | 76/76 | 33 |
| D | 78 | 78 | 77/77 | 77/77 | 49 |

(`zyklus2.c` erkennt Zyklusanfänge ohne die Zeitlücken-Heuristik und findet zusätzlich 3 bis 5
frühe Zyklen vor Schritt 23.000; auch dort ist a gerade, 81 von 81 je Start.)

Wo „alle gerade“ bricht (`gerade2.py`): ungerades Element neben einem `<1>` (78-mal), ein `<5>`
(24-mal), seltene Kombinationen davon oder ein `<1>` ohne ungerades Element (13-mal). Die Bruchstelle liegt höchstens 61 Elemente vom linken
Ende und mindestens 14 vom rechten Ende entfernt.

**Kandidat für die Parität:** „Die drei rechten Elemente sind gerade und durch `|` getrennt.“
Daraus folgt a(neu) = e3+2 gerade und damit x ungerade in der nächsten Fressrunde. Damit sich der
Kandidat selbst trägt, müsste man zeigen, dass die Grenze in jedem Zyklus weit genug nach links
läuft, bevor der Zyklus endet. Eine Überlegung dazu (unbelegt): J macht e4 unregelmäßig, also das
vierte Element von rechts; in x−1 Phasen wandert die Grenze rund (x−1)/2 Elemente nach links, und x
ist mindestens 7.

**H:** Halt verlangt C vor 111 (Teil 3). Ich habe H nicht in die Token-Sprache übersetzen können:
Während eines Pendelschwungs steht rechts vom Kopf die Form `100` statt `011`, und die Prüfpunkte
aus Teil 2 liegen mitten in diesen Schwüngen. Eine Invariante, die H ausschließt: **nein**,
keine gefunden. Die Normalform „höchstens eine Marke links“ (`nf_check.py`) scheitert an 16 von
232 Zyklusanfängen, weil dort zwei Bruchstellen gleichzeitig stehen.

## 6. Prüfweg

- Erstes Programm: `zyklus.py` (Zyklusfunktion) und `zyklus_liste.py` auf den Zeilen von
  `zweitpruefung.c liste` (in Teil 3 byteweise gleich mit dem Durchlaufmodell). Phasen über
  `snap.py` (eigener direkter Simulator) und `test_automat.py`.
- Zweites Programm: `zyklus2.c`, in C neu geschrieben: eigener Simulator, eigene Token-Zerlegung,
  eigener Automat, eigene Zyklusfunktion, eigene Erkennung der Zyklusanfänge.
- Abgleich bis 10^9, alle drei Starts: Phasenzählungen je Regel identisch; je Zyklus
  `ergebnisse/py_zyklen_*.txt` gegen `ergebnisse/c_zyklen_*.txt` zeilengleich (C und D ganz, A bis
  auf die eine Zeile 285.684.587, siehe Abschnitt 1).
- Negativkontrollen (`ZYK_FEHLER=n1|fress|j`, beide Programme, Start A): N1 mit k+3 statt k+1,
  Fressregel mit +1 statt +3, J mit +1 statt +2. Ergebnis C bis 10^8: 1, 0 und 0 statt 40 Zyklen
  ok; Python bis 10^9: 0 statt 68 ok (68, 68 und 74 falsch). Alle drei schlagen an.

Aufrufe (im Ordner `analyse/gruppe1/zyklus/`, Listen aus `zweitpruefung.c` vorher erzeugen):

```
../zp 1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC 1000000000 liste A > a.txt   # ebenso C, D
python3 zyklus_liste.py a.txt                 # je Zyklus eine Zeile
gcc -O2 -o zyklus2 zyklus2.c && ./zyklus2 A 1e9 c_zyklen_A.txt
python3 test_automat.py A 1e9                 # Phasen je Regel (ca. 3 Min.)
```

## 7. Offene Punkte

- Linkes Ende: allgemeine Regel für VS mit zu wenig Einsen und die Folgeschritte.
- Beweis, dass die Bruchstellen nie in die drei rechten Elemente kommen (für Regel F).
- H in Token-Sprache; dafür müsste man die Prüfpunkte innerhalb eines Pendelschwungs verfolgen.
