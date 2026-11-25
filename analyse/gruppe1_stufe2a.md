# Gruppe 1, Stufe 2a: Regel F in Rocq

Stand 25.11.2026. Freigabe durch Justus am 25.11.2026: Budget 2 Blöcke, danach Neubewertung.
Baut auf `analyse/gruppe1_stufe1.md` und `rocq/gruppe1_durchlauf.v` auf.

## Ergebnis in Kürze

- **Abgleich:** Das Rocq-`next` (per `vm_compute` ausgewertet) und `sweepmodell.py` liefern in den
  ersten 10^4 Modellschritten für alle drei Starts **dieselben Zustände**, Schritt für Schritt. Es gibt
  keine Abweichung in der Darstellung außer der bekannten Zählweise (siehe unten).
- **Regel F ist bewiesen** (`regel_F`): Eine Fressrunde `x | y → x+4 | y−1` ist für jedes ungerade x,
  jedes y ≥ 1 und jeden Rest der Liste genau 25 Schritte von `next`. Dazu kommt `regel_F_oft`, die
  m Runden hintereinander zusammenfasst.
- Bau über **pruefen**: Run 45602646558, beide Images grün. Print Assumptions ergibt für die drei Hauptsätze
  und für `regel_F`, `regel_F_oft` und `erreicht_halt_erreicht` jeweils `Closed under the global context`.
- Die Halteeigenschaft bleibt dabei unberührt: `erreicht_halt_erreicht` zeigt, dass so ein Sprung am
  Halten des Modells nichts ändert. Entschieden ist weiterhin nichts.

## 1. Abgleich Rocq-`next` gegen sweepmodell.py

`analyse/gruppe1/stufe2a/abgleich_rocq.v` lädt die Beweisdatei und gibt mit `Eval vm_compute` die ersten
10.000 Schritte von `next` ab `start A`, `start D` und `start C` aus (je Zustand: q, Seite, beide Stapel).
Die Ausgabe ist gepackt eingecheckt (`abgleich_rocq.out.gz`, 3,1 MB entpackt). `abgleich.py` rechnet
dieselben Schritte mit den Bausteinen von `sweepmodell.py` nach und vergleicht. Außerdem lässt es
`sweepmodell.lauf()` selbst bis zur selben TM-Schrittzahl laufen und prüft, dass es genau 10.000
Makroschritte zählt.

| Start | Zustände verglichen | gleich | TM-Schritte für 10^4 Makroschritte | größter Block | lauf() zählt |
|---|---:|---|---:|---:|---:|
| A (114) | 10.001 | ja | 51.121 | 61 Wörter | 10.000 |
| D (367) | 10.001 | ja | 49.292 | 27 Wörter | 10.000 |
| C (378) | 10.001 | ja | 51.779 | 37 Wörter | 10.000 |

Negativkontrolle: Ist der B/D-Wechsel in S2 abgeschaltet (`ABGLEICH_FEHLER=paritaet`), meldet der
Vergleich bei allen drei Starts eine Abweichung, ab Zustand 9, 17 bzw. 7.

Unterschiede in der Darstellung, dokumentiert:
- **Blockzählung:** In Rocq steht `Block n` für n+1 Wörter, in Python `('w', w, n)` für n Wörter. Rocq
  kann so keinen leeren Block haben. Beim Vergleich wird umgerechnet.
- **Verschmelzen:** Es ist in beiden gleich. Drei Bits `011` links bzw. `100` rechts werden beim Ablegen
  zu einem Block, und ein Block auf einem Block verschmilzt. Python fasst nach dem Ablegen zusammen, Rocq
  schon im Ablegen (`push_l`, `block_l`). Im Ergebnis ist das kein Unterschied: die Zustände sind gleich.
- **Wechsel B/D in S2:** Python wechselt bei ungerader Wortzahl, Rocq wechselt (n+1)-mal. Das ist dasselbe.
- **Schrittbudget:** Python führt S1/S2 nur aus, wenn das TM-Schrittbudget reicht. Das betrifft nur den
  letzten Schritt eines Laufs, nicht den Vergleich.

## 2. Die Konfiguration am Anfang einer Fressrunde

An einem Rechts-Rekord in Zustand C ist das Band rechts vom Kopf leer. Links liegt, vom Kopf aus gelesen:

```
[011]^x  1  [011]^(y+1)  1  Rest
```

In der Listenschreibweise von Teil 1 ist das `x | y`, Rest wie zuvor. Eine Runde besteht aus drei
Unterrunden mit je einem Rechts-Rekord: `x | y → x+2 <1> y → x+3 <1> y → x+4 | y−1`. Im Modell sind das
11 + 7 + 7 = **25 Schritte von `next`**, unabhängig von x und y, weil S1 und S2 die langen Blöcke in je
einem Schritt überqueren. Der Kopf greift nur in den Block `[011]^(y+1)` hinein, Rest und Bandende links
bleiben unberührt.

**x ist immer ungerade.** Die Unterrunden hängen von der Parität ab, denn S2 wechselt B/D je Wort. Bis
10^8 TM-Schritte gibt es 1.204 / 1.196 / 1.180 Fressrunden (Start A / D / C), und in allen ist x
ungerade. Gezählt habe ich das an den Listenzeilen. Nach Regel Z (x = a + 4b + 7) heißt das, dass a stets gerade ist;
das ist eine Beobachtung, kein Beweis.

Zweite Zählung, unabhängig von den Listenzeilen: `fress_muster.py` sucht das Muster direkt in den
Stapeln des Modells und prüft 25 Makroschritte später das Ergebnis.

| Start | Muster an Rekorden | F stimmt | F stimmt nicht |
|---|---:|---:|---:|
| A | 1.204 | 1.204 | 0 |
| D | 1.196 | 1.196 | 0 |
| C | 1.180 | 1.180 | 0 |

Beide Zählungen stimmen überein. Für den Beweis sind die Zählungen nicht nötig: `regel_F` gilt für
alle passenden x, y und Reste. Sie zeigen nur, dass das Lemma die tatsächlich vorkommenden Runden trifft.

## 3. Bewiesene Aussagen im Klartext

In Rocq: x = 2k+1 ist `Block (k+k)`, und [011]^(y+1) mit y = b+1 ist `Block (S b)`.

1. `erreicht z z'`: Definition. Wiederholtes Anwenden von `next` führt von z nach z' (null oder mehr
   Schritte).
2. `erreicht_trans`: Wer z2 von z1 aus erreicht und z3 von z2 aus, erreicht z3 von z1 aus.
3. `erreicht_halt_erreicht`: Wenn z' von z aus erreicht wird, dann erreicht das Modell ab z „Halt“
   genau dann, wenn es das ab z' tut. Zusammen mit `beschleunigung` aus Stufe 1 heißt das: Die
   Maschine hält ab dem Band von z genau dann, wenn sie es ab dem Band von z' tut.
4. `wechsel_wechsel`, `wechseln_SS`, `wechseln_gerade`: Zweimal wechseln ändert nichts, und eine gerade
   Zahl von Wechseln ändert den Zustand nicht.
5. **`regel_F`:** Für alle k, b und jeden Rest: Von „C, Kopf rechts, rechts leer, links
   `[011]^(2k+1) 1 [011]^(b+2) 1 Rest`“ erreicht `next` den Zustand „C, Kopf rechts, rechts leer, links
   `[011]^(2k+5) 1 [011]^(b+1) 1 Rest`“. In Listenschreibweise: **x | y → x+4 | y−1 für ungerades x und
   y ≥ 1.**
6. **`regel_F_oft`:** Für alle m, k, b und jeden Rest: Von `[011]^(2k+1) 1 [011]^(m+b+1) 1 Rest` aus
   erreicht `next` den Zustand `[011]^(2k+4m+1) 1 [011]^(b+1) 1 Rest`. In Listenschreibweise:
   **x | y → x+4m | y−m für ungerades x und m ≤ y.**

Die Hauptsätze aus Stufe 1 sind unverändert.

Was F **nicht** abdeckt:
- die letzte Runde (y = 0, dort entsteht `<1> 0` und danach `<5>`);
- die erste Runde eines Zyklus, die anders aussieht (Teil 1);
- den Weg vom Ende der Fressphase über den weiten Lauf nach links und zurück. Das ist Regel Z bzw. der
  „ganze Zyklus“ und Thema des anderen Threads.

## 4. Bau

Workflow **pruefen**, Run 45602646558 auf Commit `44d8ed5`. Eingaben: `datei=rocq/gruppe1_durchlauf.v`,
`maschine` = die drei Strings, `modell` = String 114, `lemmata=regel_F regel_F_oft erreicht_halt_erreicht`.

| Job | Ergebnis | Bauzeit der Datei | Print Assumptions (streng), 6 Sätze | Kern-Abgleich |
|---|---|---|---|---|
| aussage | grün | – | – | – |
| bau-vm | grün | 1 s (Schritt gesamt 17 s mit Abhängigkeiten) | alle `Closed under the global context` | OK |
| bau-nativ | grün | 1 s (Abhängigkeiten 17 s) | alle `Closed under the global context` | OK |

Die sha256 der gebauten Datei beginnt mit `79fdf709fca14c75`. Am längsten dauert `do 25 schritt` mit 0,04 s.

Neu im Workflow ist die optionale Eingabe `lemmata`. Die dort genannten Lemmata müssen ebenfalls
Print Assumptions streng bestehen. Für sie gibt es keinen Kern-Abgleich der Aussage, denn sie reden über
das Modell, nicht über `halts`. Ihre Aussagen stehen deshalb hier im Klartext.

Negativkontrolle, lokal im VM-Image mit `build_check.sh`: Ich habe den Beweis von `regel_F` durch
`Admitted` ersetzt. Ergebnis: `STRENG FAIL regel_F` und `STRENG FAIL regel_F_oft`, exit 1;
`gruppe1_114` bleibt OK.

## 5. Umfang und Aufwand

- `rocq/gruppe1_durchlauf.v`: jetzt 515 Zeilen (+68 für Stufe 2a). Der Beweis von `regel_F` ist eine Zeile
  (`do 25 schritt`) plus eine Taktik `schritt`, die `next` symbolisch ausrechnet. Lokale Übersetzung: 2 s.
- Werkzeuge in `analyse/gruppe1/stufe2a/`: `abgleich_rocq.v`, `abgleich.py`, `fress_muster.py`.
  Rocq braucht für die Auswertung lokal 48 s.
- Verbrauchte Blöcke: 1 von 2.

## Abweichungen und eigene Fehler

- Der Workflow hat eine zweite neue Eingabe (`lemmata`). Ohne sie wäre `regel_F` nicht streng geprüft
  worden, weil aussage_check nur Haupttheoreme der Form `halts …` meldet.
- In `abgleich_rocq.v` wurde `0` zuerst als Bandsymbol statt als Zahl gelesen (busycoq-Notation).
  Behoben, die Ausgabe betraf das nicht.

## Offene Punkte

- Der Grund, warum x in den Fressrunden immer ungerade ist, ist nicht bewiesen. Für einen vollen Zyklus
  in Rocq braucht man ihn, oder eine zweite Fassung von F für gerades x.
- Erste und letzte Runde eines Zyklus sowie Regel Z: erst nach deinem OK und nach dem Ergebnis des
  Threads „ganzer Zyklus“.

## Empfehlung

F ist abgeschlossen, und das mit 1 von 2 Blöcken. Die nächsten Teile (erste und letzte Runde) wären
ähnlich kurz, solange sie aus festen Schrittfolgen bestehen. Der eigentliche Engpass ist der weite Lauf
nach links (Thread 2). Ich würde Z erst angehen, wenn dort die Zyklusregel vollständig ist.
