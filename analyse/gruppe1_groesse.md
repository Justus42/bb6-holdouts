# Gruppe 1 (114, 367, 378): Suche nach einer erhaltenen Größe

Stand 25.11.2026. Reine Analyse, **kein Rocq**. Werkzeuge und Rohergebnisse in `analyse/gruppe1/groesse/`.
Auftrag: Justus' Nachricht vom 25.11., Punkt 2 (1 Block).

## Ergebnis in Kürze

- **Es gibt keine Größe, die bei allen Regeln gleich bleibt.** Geprüft habe ich acht Kandidaten
  (Summe S der Token-Werte, Zahl m der Token, Token mit Trenner 0, Token mit ungeradem Wert,
  unregelmäßige Token, r, x, y) und **alle** ganzzahligen gewichteten Kombinationen davon, systematisch
  über den Nullraum der beobachteten Änderungen. Über alle Regeln zusammen: keine Kombination. Modulo 2
  bleibt nur "S + Zahl der ungeraden Token ist gerade" erhalten; das gilt für jede Liste und sagt nichts.
- **Im Inneren erhalten** (N1, N2, N2s, UA; 99,98 % aller Phasen): genau drei Größen, nämlich
  **m**, **S + r** und **x**; dazu die Bandlänge L, die aus m, S und r folgt. Jede weitere erhaltene
  Kombination ist eine Summe dieser drei.
- **Am linken Ende** ändern sie sich um feste Beträge: LG: S + r gleich, m +1; LE: S + r +1, m −1;
  VS: S + r +1, m −3. Bei den Kernmustern ändert sich S + r um +1 bis +3, m je nach Fall.
- **Übergang:** Beim Fressen ändert sich x + 4y um genau +3 (passt zu Regel F: je Runde bleibt x + 4y
  gleich). Bei J bleibt S + r gleich. Über den ganzen Übergang ändert sich alles regellos.
- **Halt:** Mit diesen Größen lässt sich Halt **weder ausschließen noch vorhersagen** (Abschnitt 5).
  Grund: Sie sind Summen über das ganze Band; das Haltemuster `C> 0 1 1` ist eine örtliche
  Bedingung, und die Größen enthalten keine Information über die Lage, in der es entstehen könnte.
- Zwei Programme (Python und C, getrennt geschrieben) liefern bis 10^15 für alle drei Starts
  **zeilengleiche** Tabellen (rund 6.750 Zeilen je Start). Negativkontrollen schlagen an.

## 1. Was gemessen wurde

Schnappschuss wie im Thread "Linkes Ende": Kopf in Zustand C auf einer 0, rechts `0 (100)^r 1`, links
die Token-Liste. Kandidaten an jedem Schnappschuss:

| Zeichen | Bedeutung |
|---|---|
| S | Summe der Werte n aller Token |
| m | Zahl der Token |
| z | Token mit Trenner 0 |
| u | Token mit ungeradem n |
| q | unregelmäßige Token (Trenner 0 oder n gerade) |
| r | Zähler rechts vom Kopf |
| x, y | n des rechtesten Tokens und seines linken Nachbarn |
| L | Bandlänge = Trennerbits + 3S + 3r + 3 (Zellen vom linken bis zum rechten Ende) |

Je Ereignis wird der Vektor der Änderungen (ΔS, Δm, …, ΔL) gezählt, getrennt nach Klasse: N1, N2, N2s,
UA, LE0, LE1, LG, VS, jedes Kernmuster am linken Ende (Phasen und Zyklusübergänge getrennt), Fressen, J,
die beiden Randschritte des Übergangs und der Übergang im Ganzen. Fressen und J sind keine Phasen; ihre
Zwischenstände habe ich mit der Zyklusfunktion aus PR 9 berechnet, dort ist r formal 0.

Einordnung je Klasse und Größe: **0** (bleibt gleich), **+c** (immer derselbe Betrag), **var**
(verschiedene Beträge; Spanne und Zahl der Werte in den Rohdaten).

## 2. Ergebnis je Regel (bis 10^15, alle drei Starts zusammen)

Phasen des Automaten und VS:

| Regel | Fälle | S | m | z | u | q | r | x | y | L | S+r |
|---|---|---|---|---|---|---|---|---|---|---|---|
| N1 | 30.560.929 | +1 | 0 | −1 | +1 | −1 | −1 | 0 | var 0/+1 | 0 | **0** |
| N2 | 30.557.922 | +1 | 0 | +1 | var ±1 | var −1..1 | −1 | 0 | var 0/+2 | 0 | **0** |
| N2s | 3.311 | +1 | 0 | 0 | var ±1 | var −1..1 | −1 | 0 | 0 | 0 | **0** |
| UA | 3.640 | +1 | 0 | 0 | var ±1 | var −1/0 | −1 | 0 | 0 | 0 | **0** |
| LG | 39.555 | +1 | +1 | 0 | +1 | 0 | −1 | 0 | 0 | +1 | **0** |
| LE0 | 3.011 | +2 | −1 | 0 | 0 | −1 | −1 | var 0/+2 | 0 | +2 | +1 |
| LE1 | 187 | +2 | −1 | −1 | 0 | −2 | −1 | 0 | 0 | +2 | +1 |
| VS | 1.336 | +2 | −3 | +2 | −4 | +2 | −1 | 0 | 0 | 0 | +1 |

Übergang (7.786 erklärte Übergänge; die Teile nach der Zyklusfunktion):

| Teil | S | m | z | u | q | r | x | y | x+4y | S+r |
|---|---|---|---|---|---|---|---|---|---|---|
| Randschritt Rückweg | je nach Regel wie oben (N1, N2, LG, LE, VS …), r bleibt 0 | | | | | | | | | |
| Randschritt Fressen | ebenso | | | | | | | | | |
| Fressen | var (= 3b+2) | 0 | +1 | −1 | +1 | 0 | var | var | **+3** | var |
| J | var | −2 | −1 | −2 | 0 | var (0 → x−1) | var | var | var | **0** |
| Übergang gesamt | var | var | var | var | var | var | var | var | var | var |

Kernmuster am linken Ende: Abschnitt 3.

**Warum die Spalten so aussehen** (aus den Regeln selbst, die Messung bestätigt es): Jede Innenregel
verschiebt genau eine Einheit vom Zähler r in die Liste (S +1, r −1) und lässt Zahl der Token und
Bandlänge gleich. Ob u und q sich ändern, hängt von der Parität des linken Nachbarn G ab (N2 nimmt
ihm 1 weg); deshalb "var". y ändert sich nur, wenn die Grenze das zweite Token von rechts ist.

## 3. Kernmuster am linken Ende

Phasen, die der Automat nicht erklärt, nach Kernmuster (Definition wie im Thread "Linkes Ende"),
bis 10^15. Bis dahin kommen 12 der 13 Kernmuster vor; `0 0 e` erscheint erst bei 8,2·10^16 und liegt
außerhalb dieser Daten. Aus seiner Form `I 0 0 p → .p+2` folgt (nicht gemessen): S +2, m −2.

| Kernmuster | Fälle | S | m | r | L | S+r |
|---|---|---|---|---|---|---|
| `0 e` (VS-Familie) | 543 | var +2/+3 | var −4..+8 | −1 | var 0..14 | var +1/+2 |
| `.0 .o` | 141 | +2 | var +2..+8 | −1 | var 5..11 | **+1** |
| `0 .0 e` | 88 | var +2/+3 | var −3/−1 | −1 | var 0..3 | var +1/+2 |
| `e` (ganz links) | 78 | +2 | var 0..16 | −1 | var 3..19 | **+1** |
| `0 .o .0 e` | 33 | var +2/+3 | var −3..9 | −1 | var 0..15 | var +1/+2 |
| `0 .0 .o` | 14 | var +2/+3 | var −3..14 | −1 | var 0..20 | var +1/+2 |
| `0 0` | 14 | var +2..+4 | var −3..3 | −1 | var 0..12 | var +1..+3 |
| `keine Grenze` (Anlauf) | 7 | +1 | var 0/1 | −1 | var 0/1 | **0** |
| `.o` (Anlauf) | 3 | +3 | +4 | −1 | +10 | **+2** |
| `0 .e e .0 e` | 1 | +2 | −3 | −1 | 0 | +1 |
| `e .0 e` | 1 | +3 | +7 | −1 | +13 | +2 |

Zyklusübergänge, die die Zyklusfunktion nicht erklärt (32 Fälle, Kernmuster `0 e`, `.o .o`, `e`,
`0 .o .0 e`, `.o`): dort ändert sich jede Größe regellos, wie beim Übergang im Ganzen.

**Zusammengefasst:** In jeder Phase am linken Ende sinkt r um 1, S steigt um 1 bis 4, S + r steigt um
0 bis 3 (nie fällt es), m und L ändern sich je nach Zone links vom Kern. Eine Größe, die über alle
Kernmuster gleich bleibt oder um einen festen Betrag springt, gibt es nicht; feste Beträge für S + r
haben nur `.0 .o` und `e` (+1) sowie die Einzelfälle.

## 4. Gewichtete Kombinationen

Gesucht: alle ganzzahligen Gewichte w_S, w_m, …, w_y, sodass w · Δ = 0 für **jeden** beobachteten
Änderungsvektor gilt (Nullraum über den rationalen Zahlen; dasselbe modulo 2). Ergebnis
(`ergebnisse/actions_1e15/auswertung_p1.txt`, Abschnitt 2):

| Regelgruppe | erhalten (über Q) | erhalten (mod 2) |
|---|---|---|
| N1, N2, N2s, UA | m; S + r; x | dazu nur S + u |
| alle Automatenregeln (mit LE, LG) | **keine** | S + u; x |
| Automat + VS | keine | S + u; x |
| alle Phasen mit linkem Ende | keine | S + u |
| alles, mit Übergängen | keine | S + u |
| Übergang gesamt | keine | S + u; r |

- "S + u mod 2" ist keine Entdeckung: n + (n mod 2) ist immer gerade, also gilt es für jede Liste.
- "r mod 2 beim Übergang": r ist nach jedem Übergang gerade, weil r = x − 1 und x in allen
  Fressrunden ungerade war. Das ist die bekannte, **unbewiesene** Paritätsbeobachtung aus PR 9.
- Kontrolle der Suche: Hänge ich eine künstliche Spalte K = S + r an, findet die Suche genau S + r − K
  als einzige Kombination über alle Regeln (`ergebnisse/negativkontrollen.txt`).

**Monoton statt erhalten:** L wächst nie (das Band schrumpft nicht; trivial). S + r fällt innerhalb
eines Zyklus nie: Innenregeln und LG lassen es gleich, LE und VS erhöhen es um 1, die Kernmuster um 1
bis 3. Bis zum nächsten Übergang ist S + r also eine Uhr, die nur am linken Ende tickt. Beim
Fressen springt es um 3b+2.

## 5. Halt ausschließen oder vorhersagen? (Absatz zum Auftrag)

Mit diesen Größen gar nicht, und ich sehe auch keinen Umweg über sie. Ein Halt setzt `C> 0 1 1`
voraus, also eine **örtliche** Lage: Der Kopf kommt in Zustand C statt D an einer Stelle an, an der
rechts noch `1 1` steht. Die gefundenen Größen (m, S + r, L) sind dagegen Summen über das ganze Band;
in 99,98 % der Phasen ändern sie sich um immer dieselben Beträge, egal wo die Grenze steht und wie die
Token um sie herum aussehen. Sie können deshalb nicht unterscheiden, ob eine Phase gefährlich ist.
Eine erhaltene Größe schließt Halt nur aus, wenn die Haltelagen einen anderen Wert hätten als alle
erreichbaren Lagen; hier nehmen S, m und r jeden Wert an, und modulo 2 ist nichts erhalten außer
einer Tautologie. Was die Größen leisten: Sie zählen genau mit, **wann** das linke Ende erreicht
wird (S + r tickt nur dort, m ändert sich nur dort), also wo überhaupt neue Formen und damit neue
Gelegenheiten für das Haltemuster entstehen. Für einen Beweis wären sie höchstens Buchhaltung im Stil
der Gleichung aus PR 26 (`PR_SBC.v`); das eigentliche Hindernis bleibt eine **örtliche** Invariante,
also eine Beschreibung der Token-Fenster um die Grenze, die `C> 0 1 1` ausschließt. Die Stichprobe
(Abschnitt 6) passt dazu: Die Beinahe-Treffer liegen nahe an der Grenze und kommen in D an; was C von
D trennt, ist eine örtliche Parität, keine der globalen Summen (Vermutung, nicht belegt).

## 6. Stichprobe Haltemuster in den Phasen

`haltemuster.py`: prüft in ausgewählten Phasen jeden TM-Schritt im Durchlaufmodell (Einzelschritte;
in den Blocksprüngen S1, S2 kann das Muster nicht auftreten, Begründung im Code), ob der Kopf auf einer
0 mit `1 1` rechts davon steht, in welchem Zustand und wo relativ zur Grenze. Geprüft: jede Phase, die
der Beschleuniger ohnehin simuliert (VS, linkes Ende, Übergänge), und jede k-te Automatenphase; dort
wird zusätzlich das Ergebnis des Durchlaufmodells mit der Automatenregel verglichen.

Actions bis 10^15 (Run 45677822205, `ergebnisse/haltemuster_1e15/`), jede 10.001. Automatenphase
plus alle Rückfälle und Übergänge:

| Start | geprüfte Phasen | davon Automat | `C> 0 1 1` | `D> 0 1 1` | `E> 0 1 1` | Automat = Durchlaufmodell |
|---|---|---|---|---|---|---|
| A | 5.430 | 2.038 | **0** | 38.486 | 664 | ja (0 Abweichungen) |
| C | 5.355 | 2.038 | **0** | 37.341 | 636 | ja |
| D | 5.406 | 2.038 | **0** | 37.460 | 662 | ja |

Fast alle Beinahe-Treffer liegen in Übergängen und Rückfällen am linken Ende, nahe an der Grenze
(−30 bis +381 Zellen). In den Automatenphasen der Stichprobe gab es nur 3 bis 57 je Start. Einmal kam
der Kopf in Zustand B an (A, Rückfall).

Lokal (Start A): bis 10^8 **jede** Phase geprüft (19.825), bis 10^12 jede 101. Automatenphase:
`C> 0 1 1` 0-mal; Beinahe-Treffer `D> 0 1 1` in N1, N2, UA, LG, LE0, Rückfällen und Übergängen,
außerdem `E> 0 1 1` in Rückfällen. Automatenregel und Durchlaufmodell gleich in allen geprüften Phasen.
Negativkontrolle (Zustand D als C zählen): 4.871 Treffer bis 10^8, schlägt also an. Für diese
Stichprobe gibt es **kein** zweites Programm; auf ihr ruht keine Entscheidung.

## 7. Prüfweg

- Programm 1 `groesse.py` (Python): fährt den Beschleuniger aus dem Thread "Linkes Ende" (unverändert
  importiert); Änderungen der Automatenphasen aus dem Fenster um die Grenze, laufend aufsummiert und an
  jedem Rückfall gegen eine volle Neuberechnung geprüft (0 Abweichungen). Schreibt ein Protokoll aller
  Nicht-Automaten-Ereignisse.
- Programm 2 `groesse2.c` (C, getrennt geschrieben): rechnet jede Automatenphase selbst (eigene Regeln,
  eigene Schrittformel), berechnet an **jedem** Schnappschuss alle Größen neu aus der ganzen Liste,
  rechnet VS und die Zyklusfunktion (Randschritte, Fressen, J) selbst und eigene Kernmuster. Aus dem
  Protokoll übernimmt es nur das Ergebnis und die Schrittzahl der Rückfälle, die kein Automat erklärt;
  davor vergleicht es die ganze eigene Liste mit der Liste im Protokoll.
- Vergleich: sortierte Tabellen müssen zeilengleich sein. Bis 10^12 lokal und bis 10^15 in Actions
  (Run 45676439532; Run 45679952727 mit nach Phase und Übergang getrennten Kernmustern) für A, C, D
  zeilengleich, ebenso die beiden daraus berechneten Auswertungen; Automatenphasen je Start 20.389.187 /
  20.389.709 / 20.389.659 (gleich den Zahlen aus dem Thread "Linkes Ende").
- Negativkontrollen (`ergebnisse/negativkontrollen.txt`, Start A bis 10^10), alle schlagen an:
  Programm 1 mit zu kleinem Fenster bei N2 (4 Zeilen verschieden), LG ohne das neue Token in u (2);
  Programm 2 mit falscher UA-Regel (Abbruch am nächsten Protokoll-Ereignis), Kernmuster ohne
  Trennerzeichen (12 Zeilen), Bandlänge ohne 3r (622 Zeilen); ohne Fehler 0 Zeilen.

Aufrufe (im Ordner `analyse/gruppe1/groesse/`):

```
python3 groesse.py A 1e12 /tmp/A          # /tmp/A_delta.txt, /tmp/A_proto.txt
gcc -O2 -o groesse2 groesse2.c && ./groesse2 A 1e12 /tmp/A_proto.txt /tmp/A_c.txt
cmp <(LC_ALL=C sort /tmp/A_delta.txt) <(LC_ALL=C sort /tmp/A_c.txt)
python3 auswertung.py /tmp/A_delta.txt    # Tabellen und Nullraum
python3 haltemuster.py A 1e8 1            # Stichprobe Haltemuster
```

## 8. Abschluss

**Ergebnis.** Es gibt keine erhaltene Größe für Gruppe 1, auch keine gewichtete Kombination und
keine modulo 2. Im Inneren bleiben nur m, S + r und x (und damit die Bandlänge) gleich; am linken Ende
und im Übergang ändern sie sich. Für einen Beweis gegen Halt tragen diese Größen nichts bei, weil das
Haltemuster örtlich ist.

**Belege.** Commits c37b27e (Programme, Workflow), 12c3697 (Stichprobe), 6c13988 (Kernmuster getrennt,
Workflows nicht auf main), 294c043 (Bericht); Actions: Run 45676439532 und Run 45679952727 (groesse,
bis 10^15, beide grün, Ergebnis-Commits 91a0daf und 4c43ac1), Run 45677822205 (haltemuster, Abschnitt 6).
Lokal: `ergebnisse/lokal_1e12/`, `ergebnisse/negativkontrollen.txt`, `ergebnisse/haltemuster_lokal/`.

**Abweichungen und eigene Fehler.**
- Programm 2 kannte zuerst VS nicht als Randschritt im Übergang (1e12: 7 Übergänge als "nicht erklärt"
  gemeldet, Programm 1 erklärte sie). Ergänzt, danach zeilengleich.
- Der erste Lauf bis 10^15 warf Kernmuster aus Phasen und aus Übergängen zusammen; dadurch sahen
  einige Kernmuster regellos aus. Lauf 2 trennt sie (zusätzliche Actions-Zeit rund 20 Minuten).
- Eine Negativkontrolle (Bandlänge ohne den Rest hinter der letzten Token-Gruppe) schlug nicht an,
  weil dieser Rest nach dem Anlauf immer leer ist; ersetzt durch "Bandlänge ohne 3r", die anschlägt.
- Die Stichprobe zum Haltemuster war nicht verlangt; ich habe sie für den Absatz in Abschnitt 5
  gemacht. Sie hat kein zweites Programm.
- `0 0 e` liegt jenseits 10^15; dafür nur die Ableitung aus der Form, keine Messung.

**Offene Punkte.** Was bei den Beinahe-Treffern C von D trennt, ist nicht untersucht (Vermutung:
örtliche Parität). Die Größen bis 10^17 habe ich nicht gemessen.

**Empfehlung.** Diese Linie abbrechen: Eine globale Erhaltungsgröße führt hier nicht zum Ziel. Wenn
weiter, dann nur örtlich: die Token-Fenster an der Grenze in den Phasen mit Beinahe-Treffern
beschreiben und prüfen, ob eine örtliche Regel `C> 0 1 1` ausschließt (1 Block, kein Rocq).
Das ist eine neue Frage und bräuchte dein OK.
