# Gruppe 1 (114, 367, 378): Invariante gegen K(C) je Automatenregel

Stand 25.11.2026. Reine Analyse, **kein Rocq**. Werkzeuge und Rohergebnisse in `analyse/gruppe1/invariante/`.
Auftrag: Justus, 25.11. 19:50 (Ergänzung 1) und 20:10 (Start): Für jede Automatenregel (N1, N2, N2s, UA,
LE, LG) zeigen oder widerlegen, dass während der Phase weder `C> 0 1 1` noch ein anderer Weg zum Halt
auftreten kann. Ergebnis je Regel: Argument / Gegenbeispiel / offen.

## Ergebnis in Kürze

| Regel | Ergebnis | abstrakte Zustände | unabhängiger Prüfer | kleine Phasen vollständig (C-Programm) |
|---|---|---|---|---|
| N1 | **Argument** | 210 | bestätigt | 32.760, 0 Verstöße |
| N2 | **Argument** | 850 | bestätigt | 262.080, 0 Verstöße |
| N2s | **Argument** | 866 | bestätigt | 262.080, 0 Verstöße |
| UA | **Argument** | 516 | bestätigt | 262.080, 0 Verstöße |
| LE (f = 0) | **Argument** | 171 | bestätigt | 8.190, 0 Verstöße |
| LE (f = 1) | **Argument** | 250 | bestätigt | 32.760, 0 Verstöße |
| LG | **Argument** | 122 | bestätigt | 8.184, 0 Verstöße |

- **Aussage (für jede Regel einzeln):** Startet eine Phase an einem Schnappschuss, auf den die Regel passt
  (Bedingungen wie in `zyklus_beschl.py`, Abschnitt 1), dann tritt bis zum Ende der Phase C nie von links
  vor `? 1 1` (also weder K(C) = `C> 0 1 1` noch `C> 1 1 1`), A liest nie eine 1 (kein Halt), der Kopf
  verlässt den Bereich nicht nach links über das beschriebene Stück hinaus, und die Phase endet in Zustand
  C auf Zelle p+3. Das gilt für **alle** Zahlenwerte und **jede** Länge der Zone.
- **Art des Arguments:** rechnergestützt, kein Beweis von Hand und nicht in Rocq. Eine erschöpfende
  symbolische Ausführung mit abstrakten Zahlen (gerade/ungerade, Mindestwert) und einem Stern für "beliebig
  viele Zonen-Token" findet eine endliche, abgeschlossene Menge abstrakter Zustände ohne Verbot. Diese
  Menge (das Zertifikat) prüft ein zweites, unabhängig geschriebenes Programm nach.
- **Eine Voraussetzung ist wesentlich:** das rechteste Token ist (1, gerade ≥ 2). `zyklus_beschl.py`
  (PR 17) prüft das vor jedem Überspringen ("rechts?"), `linkes_ende/beschleuniger.py` (PR 10) nicht. Ohne
  diese Voraussetzung scheitert das Argument bei 6 von 7 Regeln (Abschnitt 4). Ein K(C) habe ich auch
  dann nicht gefunden.
- **Was das für den bedingten Halt-Ausschluss bis 10^22 heißt:** Von den zwei Bedingungen aus PR 17
  (Abschnitt 4 dort) ist "in den übersprungenen Phasen entsteht kein K(C) und kein Halt" jetzt
  rechnergestützt gezeigt. Offen bleibt die andere: dass die Regeln die **richtige Token-Liste** liefern
  (Ergebnis der Phase). Das bleibt empirisch (direkt bis 10^12, Zufallstests, Stichproben).

## 1. Was genau gezeigt ist

Tabelle `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC`. Schnappschuss wie in PR 9/10: Kopf in C auf Zelle p
(Bit 0), rechts davon `0 (100)^r 1` bis zum Bandende, links die kanonische Token-Liste T, kein Rest.
Ende der Phase: der Kopf betritt zum ersten Mal Zelle p+3.

**Startmengen** (je Regel; Grenze = rechtestes unregelmäßiges Token außer dem letzten; "Zone" = die
regulären Token (1, ungerade) zwischen Grenze und T0; "beliebig" = jeder Bandinhalt):

| Regel | Band links vom Kopf, von links nach rechts |
|---|---|
| N1 | beliebig · (0, k gerade) · Zone · T0 |
| N2 | beliebig · G = (s, g ≥ 1) · (1, k gerade) · Zone · T0 |
| N2s | beliebig · G = (s, g ≥ 1) · (0, k ungerade) · Zone · T0 |
| UA | beliebig · (s, g ≥ 1) · (1, 0) · (0, k ungerade) · Zone · T0 |
| LE (f = 0) | leer · (1, 0) · Zone · T0 |
| LE (f = 1) | leer · (1, 0) · (0, k ungerade) · Zone · T0 |
| LG | leer · Zone (mindestens 1 Token) · T0 |

Dazu immer: T0 = (1, gerade ≥ 2), r ≥ 1, Zone beliebig lang (bei LG ≥ 1), alle Zahlen beliebig. Der
Trenner s von G und alles links davon ist "beliebig". Gezeigt ist zusätzlich, dass der Kopf diesen
beliebigen Teil nie liest; das Ergebnis hängt also nicht davon ab, was dort steht.

**Verbote**, die nie erreicht werden:
1. C tritt von links auf x und x+1 = x+2 = 1 (K(C) oder C vor 111). C von rechts (über F1) ist harmlos:
   F1 schreibt 0 auf x+1.
2. Ein fehlender Tabelleneintrag (A liest 1 = Halt). Halt gibt es nur so; vorher stünde C vor 111.
3. Der Kopf liest eine Zelle des "beliebigen" Teils oder betritt p+3 in einem anderen Zustand als C.

Die Phase endet bei p+3 in C; dort ist nach Definition der nächste Schnappschuss (p+3, p+4 = 0 0, dann
(100)^(r−1) 1). Dass vorher kein Schnappschuss liegt, prüft `validiere.py` in den Zufallsphasen.

**C-Eintritte von links, die überhaupt vorkommen** (alle Regeln gleich, in allen drei Programmen):
`C> 0 0 1`, `0 1 0`, `1 0 0`, `1 0 1`, `1 1 0`. Das ist dieselbe Liste wie in PR 17, Abschnitt 4, dort
nur empirisch bis 10^12.

## 2. Verfahren

**Symbolische Ausführung** (`symb.py`, `zone.py`, Startmengen in `lauf_m.py`) auf dem Durchlaufmodell
aus Teil 3: Makroschritte S1 (`C> 100^n → 011^n C>`), S2 (`011^n <B/D → <D/B 100^n`, Wechsel bei
ungeradem n) und Einzelschritte E. S1 und S2 sind in Rocq bewiesen (`rocq/gruppe1_durchlauf.v`, Lemmata
`s1_lauf`, `s2_lauf`, PR 7).
- Blocklängen sind abstrakt: genau v, oder "u, u+2, u+4, …". Muss ein Block aufgeteilt werden und kann er
  leer sein, wird verzweigt.
- Zonen-Token links sind ein Stern (beliebig viele (1, ungerade)); bearbeitete Token rechts (`0 100^ungerade`)
  und fertige Token links werden in Sterne zurückgefaltet. Jede Faltung macht die beschriebene Menge
  größer, nie kleiner.
- Innere Schritte von S1 und S2 brauchen keine eigene Prüfung: in S1 tritt C von links nur vor `100`, in S2
  tritt C nur von rechts auf (nach F1, mit 0 rechts daneben).
- Die Suche läuft, bis keine neuen abstrakten Zustände entstehen. Dann ist die Menge abgeschlossen: Jeder
  echte Lauf aus einer Startform wird Schritt für Schritt von ihr begleitet. Kein Zustand darin ist
  verboten, also auch kein Zustand eines echten Laufs.

**Warum das ein Argument ist und kein Test:** Die Startmengen enthalten jede Zonenlänge und jeden
Zahlenwert. Jede Vereinfachung (abstrakte Zahl, Stern, Faltung, Abschneiden großer Untergrenzen) vergrößert
nur die Menge. Was in der größeren Menge nicht vorkommt, kommt im echten Lauf nicht vor.

## 3. Prüfungen

| Prüfung | Programm | Ergebnis |
|---|---|---|
| Zertifikat unabhängig nachprüfen: Starts gedeckt, jeder Nachfolger gedeckt, kein Verbot | `pruefe.py` (eigene Semantik, Inklusion über Automaten, kein Code aus `symb.py`) | alle 7 bestätigt (`ergebnisse/pruefe.txt`) |
| Exakte Rechnung = Bit-Simulation | `validiere.py`: 7.000 Zufallsphasen (1.000 je Regel, Zone bis 8 Token, Zahlen bis 41) | Band, Schrittzahl, Ende in C bei p+3, kein früherer Schnappschuss: 7.000 von 7.000 gleich |
| Feste Zonenlänge 0 bis 4 ohne Sterne | `lauf_m.py` | alle ok |
| Alle kleinen Phasen vollständig, zweites Programm | `zweit.c` (C, Bitebene): Zone bis 5 Token mit n ∈ {1,3,5,7}, T0 ∈ {2,4,6}, Grenzwerte bis 7, r ∈ {1,2} | 868.134 Phasen, 278 Mio. Schritte, 0 Verstöße |

**Negativkontrollen** (alle schlagen an):
- `pruefe.py`: jeder 7. Zustand gelöscht, Tabellenfehler E0 → 1LD, Stern mit geraden Läufen: alle 7
  Regeln "nicht bestätigt" (`ergebnisse/pruefe_negativ.txt`).
- `zone.py` mit Tabellenfehler E0 → 1LD: alle 7 offen; ohne B/D-Wechsel in S2: 3 von 7 offen
  (`ergebnisse/zone_varianten.txt`).
- K(C)-Detektor: Zufallsbänder mit leerem rechten Teil (dort gibt es K(C) nach dem Satz aus PR 17).
  `negativ.py`: 33 von 33 Treffern der Bit-Simulation im selben Schritt erkannt, keine Fehlalarme.
  `zweit.c kc`: 137 Treffer in 1 Mio. Bändern, kein Halt ohne vorherigen Treffer.
- `zweit.c fehler` (Zonen-Token gerade, T0 ungerade): Prüfungen "Bereich verlassen" und "Ende nicht in
  C" schlagen an.

## 4. Die Voraussetzung T0 = (1, gerade ≥ 2)

Lässt man T0 beliebig (`SYMB_T0=frei`), scheitert das Argument bei N1, N2, UA (Kopf liest links über die
Grenze hinaus), LE (f = 0), LE (f = 1) und LG (Kopf erreicht p+3 in Zustand D). Nur N2s geht auch dann
durch. Das ist kein Gegenbeispiel zu K(C): Eine Zufallssuche mit beliebigem T0 (`t0_suche.py`, 200.000
Phasen) fand weder K(C) noch Halt, aber 1.195 Phasen, die p+3 nicht in Zustand C erreichen. Ohne diese
Voraussetzung beschreibt die Regel die Phase also nicht mehr.

- `zyklus_beschl.py` (PR 17, Lauf bis 10^22) springt nur, wenn T0 = (1, gerade ≥ 2) gilt; sonst rechnet es
  die Phase ganz. Für diesen Lauf ist die Voraussetzung also immer erfüllt.
- `linkes_ende/beschleuniger.py` (PR 10, Lauf bis 10^17) prüft T0 nicht. Dort ist sie nur über die
  Beobachtung "a ist an jedem Zyklusanfang gerade" (PR 9) und den Abgleich mit der direkten Simulation bis
  10^12 gedeckt. Für die Zahlen bis 10^22 zählt der PR-17-Lauf, also ändert das nichts am Stand.
- Während der Phasen eines Zyklus bleibt T0 unverändert; es ändert sich nur beim Fressen und Übergang J,
  und die rechnet der Beschleuniger ganz.

## 5. Was nicht gezeigt ist

- **Das Ergebnis der Regel** (die neue Token-Liste und die Schrittzahl). Die abstrakte Suche verliert die
  genauen Zahlen; sie zeigt nur, dass unterwegs nichts Verbotenes passiert und die Phase regulär bei p+3
  endet. Für den bedingten Halt-Ausschluss jenseits 10^12 bleibt damit die Bedingung "die Regeln stimmen
  für alle vorkommenden Listen" offen (empirisch belegt wie in PR 17).
- Die gebündelten N2/N1-Paare in `zyklus_beschl.py` sind abgedeckt, soweit jede Phase im Bündel eine
  N2- bzw. N1-Phase mit den obigen Bedingungen ist; das Bündeln selbst ist in PR 17 nur gegen die
  ungebündelte Fassung geprüft.
- Nicht in Rocq. Das Zertifikat ließe sich grundsätzlich als Lemma-Kette übertragen (je abstrakter Zustand
  eine Aussage), das wäre aber ein eigenes Projekt.

## 6. Belege

- Werkzeuge: `analyse/gruppe1/invariante/` — `symb.py` (symbolische Ausführung), `zone.py` (Sterne,
  Suche, Zertifikat), `lauf_m.py` (Startmengen), `pruefe.py` (unabhängiger Prüfer), `validiere.py`
  (Gegenprobe zur Bit-Simulation), `negativ.py` (Detektor-Kontrolle), `zweit.c` (zweites Programm),
  `t0_suche.py` (beliebiges T0), `cps.py` (erster, gescheiterter Ansatz).
- Rohergebnisse: `ergebnisse/` (alle Ausgaben, `zertifikat.json.gz`).
- Alle Läufe lokal, jeweils unter 2 Minuten; keine Actions-Läufe nötig.

Aufrufe (im Ordner `analyse/gruppe1/invariante/`):

```
ZERTIFIKAT=z.json python3 -I zone.py alle      # Suche, schreibt das Zertifikat
python3 -I pruefe.py z.json                     # unabhaengige Nachpruefung
python3 -I validiere.py 1000 2                  # exakt = Bit-Simulation
python3 -I negativ.py 200000 1                  # K(C)-Detektor
gcc -O2 -o zweit zweit.c && ./zweit 5 && ./zweit 3 fehler && ./zweit 1000000 kc
```

## 7. Abweichungen und eigene Fehler

- Erster Ansatz (n-Gramm-Abschluss mit Paritätsmarken, `cps.py`) hat bis n = 10 keine Regel geschafft:
  Nach den Zickzack-Bewegungen sind die Läufe gegen die Marken verschoben, und die Parität langer Läufe geht
  verloren. Verworfen, im Repo als Beleg belassen.
- In `validiere.py` zählte ich den letzten Schritt zuerst doppelt und schnitt große Zahlen ab; beides
  Fehler der Gegenprobe, nicht der Suche. Behoben, danach 7.000 von 7.000 gleich.
- `negativ.py` meldete zuerst "schlägt nicht an", weil die symbolische Rechnung einen Schritt zu früh
  abbrach. Behoben.
- Die Fensterliste der Suche enthält zusätzlich `000`: Das ist der Endzustand vor der Wand (dort sind
  die Zellen p+3, p+4 als 0 angesetzt), kein echter C-Eintritt.

## 8. Offene Punkte und Empfehlung

Offen: Ergebnis der Regeln (Token-Liste) nicht gezeigt; nicht in Rocq; die Voraussetzung T0 ist im
PR-17-Lauf erzwungen, aber nicht bewiesen, dass sie im Lauf immer gilt (sie ist die Paritätsbedingung
"a gerade" aus PR 9).

Empfehlung: **Hier anhalten, Gruppe 1 ruht wie beschlossen.** Wenn Gruppe 1 später wieder aufgenommen
wird, wäre der nächste Schritt derselbe Ansatz mit Variablen statt abstrakter Zahlen, um auch das
Ergebnis jeder Regel zu zeigen. Damit wäre der Halt-Ausschluss bis 10^22 nur noch von der Korrektheit des
Beschleuniger-Codes abhängig. Das wäre ein eigener Block.
