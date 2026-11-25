# Gruppe 1, Stufe 1: bewiesene Durchlauf-Beschleunigung (Rocq)

Stand 25.11.2026. Freigabe durch Justus am 25.11.2026 („OK für Rocq, Stufe 1“) mit sechs Auflagen.
Datei: `rocq/gruppe1_durchlauf.v`. Baut auf `analyse/gruppe1_teil3.md` (Abschnitt 3) auf.

## Ergebnis in Kürze

- Drei Hauptsätze, je einer pro Original-String, vom leeren Band, als Genau-dann-wenn:
  `halts (TM_from_str "<String>") c0 <-> erreicht_halt (start X)` mit X = A (114), D (367), C (378).
- Bau über den Workflow **pruefen** in beiden Images: **beide Jobs grün** (Run 45599575217, Commit 8722d86).
  Print Assumptions bei allen drei Sätzen: `Closed under the global context`.
- Das ist eine bewiesene Umformulierung, **kein** Halte- oder Nicht-Halte-Beweis.

## Die drei Hauptsätze (Auflage 2)

| Satz | Maschine (Original-String) | Modell-Start | Übertragung |
|---|---|---|---|
| `gruppe1_114` | `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC` | `start A` | direkt |
| `gruppe1_367` | `1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB` | `start D` | `Permute.v` (Umbenennung) |
| `gruppe1_378` | `1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---` | `start C` | `Flip.v` + `Permute.v` (Spiegel + Umbenennung) |

Im Klartext, für jede der drei Zeilen: **Die Maschine mit diesem String hält vom leeren Band (Zustand A)
genau dann, wenn das Durchlaufmodell, gestartet auf leerem Band im Zustand X der Tabelle 114, nach endlich
vielen Schritten keinen Folgezustand mehr hat.** Der String steht wörtlich in der Aussage; es gibt keinen
Satz nur über „Tabelle 114 ab Zustand D“.

Was „das Modell“ ist, legen diese Definitionen der Datei fest (sie gehören zur Aussage und sollten mit
gelesen werden, zusammen etwa 110 Zeilen, Zeilen 31–152):
- `zustand`: Zustand q, Seite (Kopf liest das oberste Stück links oder rechts), zwei Stapel aus
  `Bit s` und `Block n` (= n+1 Wörter `011` links bzw. `100` rechts).
- `start q`: leeres Band, beide Stapel leer, Zustand q.
- `next`: genau eine von drei Regeln. S1: C läuft über einen ganzen Block `100`^(n+1) nach rechts.
  S2: B oder D läuft über einen ganzen Block `011`^(n+1) nach links (B und D wechseln je Wort).
  E: sonst ein gewöhnlicher Schritt der Tabelle 114; fehlt der Tabelleneintrag (nur A1), gibt `next`
  nichts zurück.
- `erreicht_halt z`: Wiederholtes Anwenden von `next` ab z endet bei „nichts“.

Die Haltebedingung („A liest 1“ bzw. „C vor `111`“) steht in keinem Satz; sie ergibt sich aus E. Die
Gleichwertigkeit der Bedingungen aus Teil 2 und Teil 3 (Auflage 1) steht als Nachtrag in
`analyse/gruppe1_teil3.md`, Abschnitt 3.

## Alle bewiesenen Aussagen im Klartext (Auflage 6)

Bezeichnungen: `l {{q}}> r` = Kopf in Zustand q liest die erste Zelle von r; `l <{{q}} r` = Kopf liest die
erste Zelle von l. „→+“ = in mindestens einem TM-Schritt, „→*“ = in null oder mehr Schritten.

Kodierung (Stapel ↔ Band):
1. `const0_unfold`: Das leere Band ist eine 0 vor dem leeren Band.
2. `kopf_l_spec`, `kopf_r_spec`: Die Zelle am Kopf vom Stapel abnehmen (einen Block dafür aufteilen)
   ändert das dargestellte Band nicht.
3. `push_l_spec`, `push_r_spec`: Eine Zelle auf den Stapel legen (und dabei drei Bits zu einem Block
   zusammenfassen) stellt dasselbe Band dar wie die Zelle vor das Band zu setzen.
4. `lpow_SS`: w^(n+1) gefolgt von w^(m+1) ist w^(n+m+2).
5. `block_l_spec`, `block_r_spec`: Einen Block ablegen (und mit einem Block darunter verschmelzen)
   stellt dasselbe Band dar wie die Wörter vor das Band zu setzen.

Durchläufe (Tabelle 114):
6. `s1_wort`: `C> 100` →+ `011 C>` (für jedes Band links und rechts).
7. `s1_alle`: `C> 100^n` →* `011^n C>`, für jedes n.
8. `s1_lauf`: dasselbe für n+1 Wörter mit →+ (Regel S1).
9. `s2_wort_B`, `s2_wort_D`: `011 <B` →+ `<D 100` und `011 <D` →+ `<B 100`.
10. `s2_wort`, `wechsel_BD`: zusammengefasst für q ∈ {B, D}; der Wechsel bleibt in {B, D}.
11. `s2_alle`: `011^n <q` →* `<q' 100^n`, q' = q n-mal gewechselt, für q ∈ {B, D}.
12. `s2_lauf`: dasselbe für n+1 Wörter mit →+ (Regel S2).

Einzelschritt und Korrektheit von `next`:
13. `einzel_re`: Ein Einzelschritt des Modells ist genau ein TM-Schritt.
14. `einzel_none`: Liefert der Einzelschritt nichts, fehlt der Tabelleneintrag.
15. `encode_re`, `encode_li`: Das Band eines Modellzustands, mit der Kopfzelle abgenommen.
16. `next_re`, `next_li`: Regel E bildet mindestens einen TM-Schritt ab (beide Seiten).
17. `schritt_some`: **Jeder Schritt von `next` bildet mindestens einen TM-Schritt ab** (entspricht
    `step_some` in cryptids).
18. `schritt_none`: **Liefert `next` nichts, steht die Maschine im dargestellten Band still** (entspricht
    `step_none`).
19. `beschleunigung`: **Für jeden Modellzustand z: Die Maschine hält ab dem Band von z genau dann, wenn
    das Modell ab z „Halt“ erreicht** (entspricht `isHalt_iff_acceleration`).
20. `encode_start`: Das Band von `start q` ist das leere Band in Zustand q.

Übertragung auf 367 und 378:
21. `perm367`: 367 ist Tabelle 114 mit A..F = E C B A D F umbenannt (Eintrag für Eintrag).
22. `perm378`: 378 ist die gespiegelte Tabelle 114 mit A..F = F D A B C E umbenannt.
23. `perm_flipflip`: Zweimal gespiegelt ist Eintrag für Eintrag wieder Tabelle 114.
24. `halts_flip_iff`: Tabelle 114 hält ab leerem Band in q genau dann, wenn ihr Spiegelbild es tut.
25. Die drei Hauptsätze (oben).

## Prüfung vor dem Bau: aussage_check (Auflage 3)

`scripts/aussage_check` kennt jetzt mit `--modell <Referenz-String>` die Form
`halts <tm> c0 <-> P (start X)`:
- X wird nicht aus der Datei übernommen, sondern berechnet: Die Maschine muss eine Umbenennung pi der
  Referenz oder ihres Spiegelbilds sein, und X ist der Zustand der Referenz mit pi(X) = A. Für die drei
  Strings ergibt das A, D (Umbenennung) und C (Spiegel), wie in der Datei.
- `P` und `start` müssen oberste Definitionen der Datei sein, in allen Sätzen dieselben.
- Ohne `--modell` ist die Form verboten; nur `->` oder nur `<-` ist kein Haupttheorem.
- `--coq` erzeugt den Kern-Abgleich `Definition aussage_k : halts (TM_from_str "S") c0 <-> M.P (M.start X)
  := M.satz.`; der Bau prüft ihn im Kern.
- Der Workflow `pruefen` hat dafür die optionale Eingabe `modell` (leer = wie bisher).

Negativkontrollen (`scripts/test_aussage_check_iff.sh`, alle schlagen an, Positivkontrolle OK):

| Kontrolle | Ergebnis |
|---|---|
| falscher String im Satz (114, B1 `0LF`→`0LE`) | FAIL „weder ein erwarteter String …“ |
| falscher erwarteter String (Holdout Zeile 1 statt 114) | FAIL „kommt in der Datei nicht exakt vor“ |
| nur eine Richtung (`->` statt `<->`, 114) | FAIL „kein Haupttheorem“ |
| nur Rückrichtung (`<-`, 367) | FAIL „kein Haupttheorem“ |
| anderer Start: 114 mit B, 367 mit A, 378 mit A | FAIL „Modell-Start … passt nicht“ (je einzeln) |
| falsche Referenz (`--modell` = 367) | FAIL „Modell-Start … passt nicht“ |
| Genau-dann-wenn ohne `--modell` | FAIL |
| Start ist keine Definition der Datei | FAIL |
| zwei verschiedene Modelle in den Sätzen | FAIL |

Zusätzlich im Kern (lokal, VM-Image): der erzeugte Abgleich läuft durch; mit `start B` statt `start A`
oder mit `->` statt `<->` bricht `coqc` mit Typfehler ab.

Rückwirkung auf alte Prüfungen: Alle 180 gemergten Beweisdateien aus `decided` (by=proof) am Pin mit
altem und neuem aussage_check geprüft: Ergebnis (OK/FAIL) bei allen 180 gleich. Einziger Unterschied in
den Meldungen: In `Sk1Machines_v2.v` fällt eine FAIL-Zeile weg, weil die Abdeckung jetzt je String zählt
(benannte Definition und Literal mit demselben String decken einander ab). Die Datei bleibt FAIL.

Unterwegs gefunden: aussage_check schlug beim ersten Lauf an, weil meine Lemmata `s1`/`s2` hießen und
`s1` in busycoq ein geschützter Name ist. Umbenannt in `s1_lauf`/`s2_lauf`.

## Permute.v und Flip.v am Pin (Auflage 4)

Am Pin `33209bc7dc282b38c8cd6be507bfc551fea56108` gelesen und benutzt:
- `Permute.v`: `Perm tm tm' f` (Eintrag für Eintrag gleich bis auf Umbenennung f), `perm_halts` und
  `perm_halts'` für **beliebigen** Zustand q und beliebiges Band t. Damit geht der Start D bzw. C.
- `Flip.v`: `flip` (L und R tauschen), `flip_halts : halts tm c -> halts (flip tm) (flip_conf c)`.
- **Vorsicht:** `flip_involutive` und damit `flip_halts_iff` in `Flip.v` benutzen
  `functional_extensionality`, also ein Axiom. Ich benutze beide nicht. Die Rückrichtung läuft über
  `perm_flipflip` (zweimal gespiegelt ist Eintrag für Eintrag die alte Tabelle) und `perm_halts`.
  Print Assumptions bestätigt: kein Axiom.

## Bau (Auflage 5)

Workflow **pruefen**, Run 45599575217 auf Commit `8722d86`, Eingaben `datei=rocq/gruppe1_durchlauf.v`,
`maschine` = die drei Strings, `modell` = String 114.

| Job | Ergebnis | Abhängigkeiten | Bauzeit der Datei | Print Assumptions (streng) | Kern-Abgleich |
|---|---|---|---|---|---|
| aussage | grün (aussage_check OK, 3 Haupttheoreme) | – | – | – | – |
| bau-vm (`coqorg/coq:8.20.1`, Digest `3675f124…`) | grün | 11 s | **1 s** | alle drei `Closed under the global context` | OK |
| bau-nativ (`8.20.1-native`, Digest `89d0f190…`) | grün | 12 s | **1 s** | alle drei `Closed under the global context` | OK |

Die Bauzeit ist so kurz wie erwartet: Es gibt keine große Rechnung, nur kurze `execute`-Schritte für die
Wortregeln und Fallunterscheidungen über die 12 Tabelleneinträge. sha256 der gebauten Datei beginnt mit
`fcf4b2cfb0cc0bf0` (in beiden Jobs gleich, wie im aussage-Job).

## Umfang und Aufwand

- `rocq/gruppe1_durchlauf.v`: 447 Zeilen (davon etwa 110 Definitionen des Modells, Rest Beweise und
  Kommentare), 34 Lemmata/Sätze, keine großen Rechnungen.
- Lokal (VM-Image) übersetzt die Datei in 2 s.
- Verbrauchte Blöcke: 1 von 4 (ein Arbeitsgang am 25.11. vormittags).
- Werkzeuge: `scripts/aussage_check` (+~100 Zeilen), `scripts/test_aussage_check_iff.sh` (neu),
  `.github/workflows/pruefen.yml` (Eingabe `modell`).

## Schätzung für Stufe 2 (Regeln F und Z), unbelegt

Grundlage: Stufe 1 ging schnell, weil S1, S2 und E kurze, lokale Muster sind, die `execute` direkt
nachrechnet. F und Z sind anders:
- **F (Fressrunde, x|y → x+4|y−1):** Ich habe die Konfiguration am Anfang einer Fressrunde noch nicht
  vollständig als Modellzustand hingeschrieben (offen seit Teil 3). Danach wäre F eine Kette aus S1, S2
  und einigen E-Schritten mit Parametern x, y und einer Paritätsunterscheidung. Schätzung: 2–4 Blöcke,
  wenn die Konfiguration sauber ist; mehr, wenn das rechte Ende Sonderfälle hat.
- **Z (Zyklus, x = a+4b+7):** braucht F plus eine Induktion über b und die Pendelphasen am linken Ende.
  Für die Pendelphasen gibt es kein geschlossenes Modell (Teil 3, Abschnitt 4). Schätzung: 4–8 Blöcke,
  mit echtem Risiko, dass es ohne Modell der Pendelphasen nicht geht.
- **Was F und Z bringen:** weiterhin keine Entscheidung. Ein Halte- oder Nicht-Halte-Beweis bräuchte
  zusätzlich eine Invariante; die fehlt seit Teil 2.

Empfehlung: Stufe 2 nur mit F beginnen und nach 2 Blöcken neu bewerten.

## Nachprüfen

```bash
scripts/test_aussage_check_iff.sh                       # 12 Zeilen OK, exit 0
R=1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC
scripts/aussage_check rocq/gruppe1_durchlauf.v \
  "$R,1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB,1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---" \
  --modell "$R" --coq Pruefling /tmp/Kern_Pruefling.v
# Bau: Workflow pruefen, datei=rocq/gruppe1_durchlauf.v, maschine=die drei Strings, modell=$R
```

## Abweichungen und eigene Fehler

- Erster lokaler Übersetzungsversuch scheiterte an Kleinigkeiten (fehlendes `Require Import String`,
  `rewrite … at 1` zu eng, `Nat.leb_spec` nicht geladen, `cbn` rechnet `flip` nicht aus). Alle in
  wenigen Minuten behoben; keine Änderung an den Aussagen.
- Lemmata `s1`/`s2` kollidierten mit dem geschützten Namen `s1` (von aussage_check gefunden).
- Die Kontrolle „falscher erwarteter String“ hatte ich zuerst mit „nur 367 und 378 erwartet“ angesetzt.
  Das ist kein Fehler im Sinne von aussage_check, weil 114 Spiegel-Zwilling von 378 ist und Zwillinge mit
  eigenem Satz zulässig sind. Ersetzt durch einen fremden Holdout-String.

## Offene Punkte

- Nicht geprüft: ob das Rocq-Modell Schritt für Schritt dieselben Listen erzeugt wie
  `sweepmodell.py`. Für die Gültigkeit der Sätze ist das unerheblich (sie sind bewiesen), für Stufe 2
  wäre es nützlich. Die Rocq-Fassung fasst Bits schon beim Ablegen zu Blöcken zusammen.
- Kein coqchk (wie im Workflow festgelegt).
- Nichts bei busycoq eingereicht.
