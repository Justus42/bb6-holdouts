# 396: Rückführung auf ein Wortsystem in Rocq

Thread „396, Teil 2“, 25.11.2026. Rocq-OK von Justus um 21:43 Uhr, Budget 4 Blöcke. Datei:
`rocq/rueckfuehrung_396.v`.

## Ergebnis

**Bewiesen, beide Richtungen:**

```
Theorem rueckfuehrung : halts tm c0 <-> W.trifft111 W.start.
tm = TM_from_str "1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---"   (Holdout 396)
```

396 hält ab Leerband genau dann, wenn im Wortsystem `W` ab dem Startwort `1` in irgendeiner Runde ein
Besuch auf den Block `111` trifft. Ob das je geschieht, ist damit **nicht** entschieden. Der Satz ist eine
bewiesene Umformulierung, auf demselben Stand wie 587 in cryptids.

## Was bewiesen ist, im Klartext

**Das Wortsystem (Modul `W`, ohne Bezug auf die Maschine).** Ein Wort ist eine endliche Liste von Zellen,
und rechts davon stehen nur Nullen. Ein Besuch auf einem Wort endet mit einem neuen Wort (`Vis w y`) oder
trifft 111 (`Hit w`), nach diesen Regeln:

| Block am Anfang | Besuch |
|---|---|
| `0x` | endet: `1x` |
| `100x`, `110x` | `000` und dann ein Besuch auf `x` |
| `1010x` | `1010` und dann zwei Besuche auf `x` |
| `1011x` | endet: `0001x` |
| `111x` | trifft 111 |

- Eine Runde setzt `1 0` vor das Wort und macht einen Besuch.
- `Runde w0 k s` heißt: nach k Runden ab w0 steht das Wort s.
- `trifft111 w0` heißt: es gibt eine Runde, in der der Besuch auf 111 trifft.
- Das Startwort ist `start = [1]`.

**Die bewiesenen Aussagen:**

1. **Ausführbare Fassung gleichwertig** (`WX.runden_korrekt`, `WX.runden_vollstaendig`,
   `WX.trifft111_iff_runden`).
   - `runden f k w0` rechnet k Runden mit Schrittgrenze f.
   - Liefert es ein Wort oder „Treffer in Runde j“, dann gilt das auch im Wortsystem.
   - Umgekehrt liefert es mit genügend großer Schrittgrenze alles, was im Wortsystem gilt.
   - Folgerung: `trifft111 w0` gilt genau dann, wenn es f, k und j gibt mit `runden f k w0 = Treffer j`.
2. **Jeder Besuch endet oder trifft 111** (`WT.besuch_endet_oder_trifft111`). Für jedes Wort w gilt
   `Hit w` oder es gibt y mit `Vis w y`.
3. **Dreizehn Annahmen über die Maschine, für beliebige Bandreste bewiesen** (durch Ausführen der Tabelle
   mit der Taktik `law` aus PR #59).
   - Elf davon in der Form aus PR #59: vis_0, vis_H, vis_G, vis_L, hv_H, hv_G, hv_L1, hv_L2,
     round_step, round_halt, blank_start.
   - Zwei neue an Stelle von hv_1011:
     - vis_K: ein Besuch auf `1011` endet mit `0001`.
     - hv_111: ein Besuch auf `111` hält.
4. **Vom Wort zum Band** (`band_vis`, `band_hit`, `runde_band`).
   - Endet ein Besuch im Wortsystem mit y, dann tut es die Maschine auf dem Band genauso.
   - Trifft er 111, dann hält die Maschine.
   - Nach k Runden des Wortsystems erreicht die Maschine ab Leerband die Rundengrenze mit genau diesem
     Wort.
5. **Halt-Richtung** (`halt_richtung`): Trifft das Wortsystem 111, dann hält 396.
6. **Andere Richtung** (`nichthalt_richtung`): Hält 396, dann trifft das Wortsystem 111.
   - Beweis mit 2: Jede Runde endet oder trifft 111.
   - Endet sie, dann braucht die Maschine dafür mindestens einen Schritt.
   - Eine haltende Maschine hat aber nur endlich viele Schritte. Also muss irgendwann eine Runde 111 treffen.
   - Konstruktiv, ohne Axiome.

## Abweichung von der Vorgabe: der Längen-Hinweis

Die Vorgabe zu 2 lautete: „Induktion über die Wortlänge; ein Besuch verlängert ein Wort um höchstens 1“.
**Das stimmt nicht.** Wegen der Nullen hinter dem Wortende kann ein Besuch ein kurzes Wort stark verlängern.

- Beispiel: V(`1010101`) = `101010100000001`, das ist Länge 7 → 15.
- Der größte Zuwachs wächst mit der Wortlänge: Länge 3 → +5, Länge 7 → +8, Länge 11 → +11 (alle Wörter
  bis Länge 14 durchgerechnet).

Bewiesen habe ich 2 deshalb anders:

- Betrachtet werden n Besuche nacheinander auf dasselbe Wort.
- Induktion lexikografisch über (Wortlänge, n).
- Jeder Block reicht die Besuche an ein kürzeres Restwort weiter oder verbraucht einen Besuch am Ort:
  - `100`, `110`: ⌈n/2⌉ Besuche gehen weiter.
  - `1010`: 2n Besuche gehen weiter.
  - `0` und `1011`: ein Besuch endet am Ort.
- Das leere Wort hat ein eigenes Lemma, Induktion über n.

## Prüfungen

- **aussage_check `--wortsystem`** (neu, vor dem Bau).
  - Die Datei muss das Modul aus `scripts/referenz/wortsystem_396.v` Satz für Satz enthalten (Kommentare
    zählen nicht).
  - Vor dem Modul dürfen nur Importe stehen.
  - Der Hauptsatz muss genau `halts <tm> c0 <-> W.trifft111 W.start` lauten.
  - Negativkontrollen (`scripts/test_aussage_check_wort.sh`, 15 Fälle): alle schlagen an, unveränderte
    Datei OK. Geprüft wurden:
    - falscher String in der Datei
    - falscher erwarteter String (Zeile 1, 587)
    - nur eine Richtung (`->`, `<-`)
    - anderes Startwort im Satz und im Modul
    - Regel 1011 → 1000 (System von 587)
    - anderes Prädikat
    - Satz nicht auf oberster Ebene
    - Admitted
    - Umdefinition von `tl` vor dem Modul
    - ohne `--wortsystem`
  - Der Kern-Abgleich nach dem Bau prüft
    `halts (TM_from_str "...") c0 <-> M.W.trifft111 M.W.start := M.rueckfuehrung`.
- **Python-Abgleich** (`analyse/396/rocq_abgleich/`).
  - Rocq rechnet `WX.runden`, Python rechnet unabhängig nach den sechs Regeln.
  - Startwörter: `1` (35 Runden) und 40 Zufallswörter mit 1011/111/011 (je 15 Runden).
  - Ergebnis: 635 Runden, 8 Läufe mit Treffer, **0 Abweichungen**. Wörter ab `1` auch gleich mit
    `runde.c` (35 Runden).
  - Negativkontrolle: Python mit der 587-Regel (1011 → 1000) gibt 9 Abweichungen.
- **Bau:**
  - Lokal VM-Image: Bau OK in 2 s, Print Assumptions für `rueckfuehrung` „Closed under the global context“.
  - Lokal natives Image: Bau OK in 2 s.
  - Actions-Lauf `pruefen` 45700149762: Jobs `aussage`, `bau-vm`, `bau-nativ` grün.
    - Print Assumptions streng „Closed under the global context“ für `rueckfuehrung`, `halt_richtung`,
      `nichthalt_richtung`, `WT.besuch_endet_oder_trifft111`, `WX.trifft111_iff_runden`,
      `WX.runden_korrekt`, `WX.runden_vollstaendig` und die 13 Band-Lemmata.
    - Kern-Abgleich OK.
    - Bauschritt (Abhängigkeiten, Bau, Print Assumptions) etwa 24 s (VM) und 27 s (nativ).

## Zahlen

- Beweisdatei 613 Zeilen, 44 Lemmata/Sätze.
- Referenz des Wortsystems 74 Zeilen.
- Bauzeit lokal 2 s (beide Images), in Actions etwa 24 s (VM) und 27 s (nativ) für den ganzen Bauschritt.
- Verbraucht: 1 von 4 Blöcken.

## Herkunft

Das Gerüst stammt aus busycoq PR #59 (alkrssve, offen, Commit f23281d). Übernommen:

- die Definitionen `sym`, `lw`, `Zinf` und die Bandformen von Besuch, Halt und Rundengrenze
- die Form von elf Annahmen
- die Taktik `law` mit ihren Hilfstaktiken

Nicht übernommen ist der Rechenteil (`check 161210`). Die Datei liegt nur in unserem Repo. Bei busycoq und
in Discord ist nichts geschehen.
