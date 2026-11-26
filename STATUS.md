# Stand des Projekts (26.11.2026, früh; Abgleich mit busy-beaver-explorer; berichtigt 26.11. mittags nach Prüfstelle; M5 nachgezogen 26.11. nach PR 31; 396 nachgezogen 26.11. nach PR 34; slugbirds Guide nachgetragen 26.11. nachmittags; 133 nachgezogen 26.11. nach Run 45817990655)

Kurzfassung je Gruppe: was **bewiesen** ist (Rocq, mit Datei und Actions-Lauf), was nur **beobachtet** ist
(mit Prüfgrenze und Zahl der Programme), was **offen** ist. Jede Zahl verweist auf den Bericht, aus dem sie
stammt (Kürzel siehe unten). Wo Berichte sich widersprechen oder später korrigiert wurden, gilt der spätere;
die Korrekturen stehen am Ende. Englische Fassung: `STATUS.en.md`.

**Insgesamt:** Von uns ist keine Maschine entschieden. Bewiesen in Rocq sind Umformulierungen: für Gruppe 1
(Durchlauf-Beschleunigung) mit einer Regel darauf (Regel F), und für 396 die Rückführung auf ein Wortsystem
(PR 21). Alles andere ist Beobachtung bis zu einer Prüfgrenze.

**Extern (26.11.):** busycoq hat PR #59 und #55 nach BB6 gemergt. Damit sind **88, 312, 449 (halten)** und
**471 (hält nicht)** upstream entschieden. 123 und 223 halten laut busy-beaver-explorer (Lean und Coq;
busycoq-PR #72/#73 offen). Zu 396 hatte busy-beaver-explorer am 24.11. alles, was wir gefunden haben, und mehr;
**unser 396-Ergebnis ist eine unabhängige Bestätigung, keine Neuheit** [AB].

**Prüfstelle (26.11., 11:45 Uhr, eigener Code):** bestätigt Gruppe 1 (367 = Start D, 378 = Start C gespiegelt),
die M5-Abbildung aller vier, das Besuchsgesetz für 396 (20.000 Zufallswörter, 30 Runden direkt), den Lauf 396 bis
Runde 260.000 (Ereignisse 161.210/211 und 194.646/647), 403 Tabellen, 509 Holdouts ohne BB6-Eintrag und ohne offenen PR.

Berichte (alle in `analyse/`, gemergt mit PR in Klammern):
[G1] `gruppe1.md` (PR 2) · [G1-2] `gruppe1_teil2.md` (PR 3) · [G1-3] `gruppe1_teil3.md` (PR 6) ·
[S1] `gruppe1_stufe1.md` (PR 7) · [S2a] `gruppe1_stufe2a.md` (PR 8) · [ZY] `gruppe1_zyklus.md` (PR 9) ·
[LE] `gruppe1_linkes_ende.md` (PR 10) · [VL] `gruppe1_vorlagen.md` (PR 11) · [P26] `gruppe1_pr26.md` (PR 11) ·
[GR] `gruppe1_groesse.md` (PR 16) · [VB] `gruppe1_verboten.md` (PR 17) · [INV] `invarianten.md` (PR 15) ·
[M1] `318_518.md` (PR 4) · [M2] `318_518_teil2.md` (PR 5) · [396] `396.md` (PR 13) ·
[VK] `verwandtschaft.md` (PR 12, korrigiert in PR 13) · [DA] `stand/datenabgleich.md` (PR 18) · [FB] `besuchsgesetz.md` (PR 23) ·
[RF] `396_rueckfuehrung.md` (PR 21) · [T2] `396_teil2.md` (PR 24) · [AB] `abgleich_bbe.md` (Abgleich mit busy-beaver-explorer) ·
[M3] `318_518_teil3.md` (PR 31, Haltemuster bis 8·10^14) · [WM] `396_wachstumsmuster.md` (PR 34) ·
[133] `133_581.md` (PR 32 und Folge-PR).
Fremde Quelle: [GU] slugbirds BB(6) Holdout Guide, Stand 3.11.2026 (Abschnitt unten).

## Datenstand (Abgleich 25.11.2026) [DA]

- `holdouts.json` von denniskoshta.com neu geholt (`data/holdouts_2026-11-25.json`): **byte-gleich** mit dem
  Stand vom 10.11. Die Seite hat die Datei seitdem nicht neu erzeugt.
- busycoq direkt gelesen: Zweig BB6 unverändert auf `33209bc7` (03.11.), also **nichts neu gemergt**. 58 neue
  PR-Refs (62 bis 119, 09.11. bis 25.11.) mit Strings von 63 Holdouts. **Keiner betrifft 396, 88, 312, 449,
  Gruppe 1 oder die M5-Gruppe** (zwei Programme zeilengleich, dazu Normalform-Abgleich, Negativkontrollen
  schlagen an). Ob die PRs offen oder geschlossen sind, ist nicht geprüft.
- cryptids (Commit `f01ee56`, 25.11.): nichts zu 396, 88, 449, Gruppe 1, M5. 312 hat dort eine formale
  Rückführung (keine Entscheidung). Holdout 587 hat eine bewiesene Beschleunigung mit derselben Lage wie 396
  (`1011` hält nicht, nur `111`); nur gelesen.

## Abgleich mit busycoq und busy-beaver-explorer (26.11.2026) [AB]

- **busycoq** (per git, nur gelesen): Zweig BB6 jetzt auf `9c078ca` (26.11.), 25 PRs gemergt, darunter #59
  (88, 312, 449 halten) und #55 (u. a. 471 hält nicht). Unser Pin ist seit 26.11. `9c078ca` (PR 27, Justus' OK;
  vorher `33209bc7`). In BB6 (neu seit dem alten Pin) und in den PR-Refs 1–120 nennt keine Datei 396, 110, 587,
  Gruppe 1 oder M5.
- **Offene busycoq-PRs** (26.11. mittags): `git ls-remote` zeigt `refs/pull/N/merge` nur für offene PRs ohne
  Konflikt, also eine Untergrenze: **53 offen** (3 bis 120). Gegenüber BB6 fügt keiner eine Zeile mit 114, 367,
  378, 318, 518, 322, 274, 396, 110 oder 587 hinzu (mit `---` und `HHH` gesucht; Kontrolle: 581 in PR 76 gefunden).
  Ein Programm von uns; deckt sich mit der Zählung der Prüfstelle.
- **bbe Übertragungs-Abgleich** (26.11., `holdouts/recent-proofs/followup/invariant-transfer.md`, Commit
  `0e077e33`, nur gelesen, nicht nachgebaut): drei Siebe über 509 offene Holdouts gegen 236.071 bewiesene
  Tabellen, **nichts entschieden, nichts übertragbar**. Für unsere zehn Maschinen laut bbes Datendateien
  (Suche nach unseren Strings): kein bewiesenes Geschwister gleicher Tabelle, keine verstummenden Übergänge;
  alle Nachbarn mit 1–2 anderen Übergängen trennen sich ohne Wiedervereinigung (396: 63 Paare, 587: 10, 378: 7,
  367: 6, 114: 4, 110: 3, 318/518/322/274: je 1).
- **busy-beaver-explorer** (bbe, `github.com/fractal-geometry-explorer/busy-beaver-explorer`, Kopf `662e215`):
  je Holdout ein Ordner mit Belegstufen. Lean-Sätze dort stehen auf bbes eigenen Definitionen, nicht auf
  busycoqs; „native“ heißt `native_decide`. Je Gruppe unten unter „Extern (bbe)“.
- **Gleichwertige Strings** (`holdouts.json`, Feld `aliases`): 14 für unsere 11 Maschinen (396: 8, 114: 2,
  110, 274, 318, 322: je 1; 133, 367, 378, 518, 587: keine). Eigene Nachsuche (26.11. nachmittags, ein
  Programm): in den 53 offenen PRs (hinzugefügte Zeilen gegen BB6) und in bbe (Kopf `923e0537`) keiner. In BB6
  stehen 11 der 14: je einer von 110, 114 (`1RB1RF_1RC0LD_…`; der zweite von 114 steht nirgends) und 318 sowie
  alle acht von 396, und zwar nur in den Äquivalenzbeweisen `Eqv_v2.v`, `Eqv_v3.v`, `Eqv_Misc.v` (Lemma `eqv`, seit 30.10.; daraus ist die Liste der
  608 gebildet), in keinem Entscheidungsbeweis. Kontrollen schlagen an: 581 in PR 76, der 396-String in bbe.
  Die Prüfstelle hatte „kein Treffer in BB6“ gemeldet, weil ihre Suche die Eqv-Dateien ausklammerte; sie hat den
  Befund bestätigt (26.11., 15:55).
- Ab jetzt gilt (CLAUDE.md): vor jeder Arbeit an einer Maschine busycoq, bbe, `holdouts.json` samt
  gleichwertigen Strings, slugbirds Guide und das Wiki prüfen; die Discord-Regel entfällt.

## slugbirds Holdout-Guide (Stand 3.11.2026) [GU]

Quelle: „slugbird’s BB(6) Holdout Guide“, Stand „November 3, 2026“ (claude.ai/artifact/8B8E5ms18otN4XHbEnxaP2,
in `holdouts.json` unter `sources.slugbird`). Am 26.11. mit Justus' Freigabe nur gelesen. Die Seite ist laut
eigener Fußzeile von KI-Agenten (Claude, „Heron“) geschrieben. Ihre Schrittzahlen stimmen mit den Feldern
`slugbird` in `holdouts.json` überein. Sinngemäß zu unseren Maschinen:

- **114, 367, 378** („Monotone list“, Regeln bekannt, kein Beweis): „eine Tabelle, drei Starts“; Halt nur aus
  bestimmten Wörtern am linken Ende, bisher passt keines zu einem echten Zustand. Simuliert 1,6·10^14 (114),
  2·10^14 (367, 378). Das ist im Kern unser Befund [LE], [VB], dort schon beschrieben.
- **274, 322** („Shift-overflow structural counter“, Regeln bekannt): exakter Binärzähler aus wandernden Atomen
  auf einem Hintergrund der Periode 8; Überläufe bauen das ferne Ende um. **318, 518**: gleicher Mechanismus
  (Binärzähler auf periodischem Hintergrund). Der Guide führt Paare (274~518, 318~322), keine gemeinsame
  5-Zustands-Maschine. Simuliert 10^17 (274, 322, 518), 10^20 (318).
- **396, 110, 587** sowie 88, 449 („Shift-overflow counter“, Regeln bekannt): gleich Beaver Math Olympiad
  Problem 10, ein Übertragssystem aus sieben Regeln; „die Regeln sind in Rocq bewiesen“. Laut Prüfstelle ist die
  Ausgangsmaschine von Problem 10 im Wiki (`Beaver_Math_Olympiad`) die 312 (Wiki von uns nicht gelesen).
  88, 312, 449 sind seit 26.11. upstream entschieden [AB].
- **133** („Skelet 1-like Class 1“): „Reported by others“, also von anderen bearbeitet oder besprochen; keine
  Schrittzahl angegeben.
- **385**: Der Guide (3.11.) nennt „offenen PR 44, der Nicht-Halt beweist“. Überholt: PR 44 steckt inzwischen in
  BB6, aber ohne 385. Sein letzter Commit `c94a67d` (Alk, 5.11.) entfernt den Beweis wieder (432 Zeilen; laut
  Commit-Nachricht „mostly data (an automaton with 11,253 states)“, von uns nicht nachgezählt). 385 verfolgen wir nicht
  (keine Portierung, Justus 26.11.).

**Folge:** „Wir sind weiter“ behaupten wir nur noch gegenüber bbe. Gegenüber slugbird ist es nicht belegt:
Gruppe 1 hat der Guide bis 1,6·10^14 (114) bzw. 2·10^14 (367, 378) simuliert, wir haben 10^12 lückenlos und
10^24/10^25 nur bedingt; M5 hat der Guide bis 10^17/10^20 simuliert, wir bis 8·10^14; die Regeln der 396-Familie sind dort als in Rocq bewiesen
genannt (wo, von uns nicht geprüft).

## Gruppe 1: 114, 367, 378 (eine Tabelle, drei Starts)

### Bewiesen (Rocq)

Datei `rocq/gruppe1_durchlauf.v` (515 Zeilen, sha256 beginnt `79fdf709fca14c75`, seit Commit `44d8ed5`
unverändert).

| Aussage | Inhalt | Lauf **pruefen** (beide Images grün, Print Assumptions `Closed under the global context`) |
|---|---|---|
| `gruppe1_114`, `gruppe1_367`, `gruppe1_378` | Maschine hält vom leeren Band genau dann, wenn das Durchlaufmodell (Regeln S1, S2, E) ab Start A / D / C „Halt“ erreicht. Umformulierung, **keine Entscheidung** [S1] | Run 45599575217 (Commit `8722d86`) [S1]; erneut in Run 45602646558 [S2a] |
| `regel_F`, `regel_F_oft` | Fressrunde `x \| y → x+4 \| y−1` für ungerades x, y ≥ 1, in 25 Schritten des Modells; m Runden am Stück [S2a] | Run 45602646558 (Commit `44d8ed5`) [S2a] |
| `erreicht_halt_erreicht` | ein solcher Sprung ändert am Halten nichts [S2a] | Run 45602646558 [S2a] |

Von Hand gezeigt, **nicht** maschinell geprüft: **Satz K(C)**. Startet der Lauf auf einem Band, das rechts vom
Kopf leer ist, geht jedem Halt ein Moment voraus, in dem C von links auf `0 1 1` tritt. Notwendig, nicht
hinreichend [VB, Abschnitt 1.2]. Von Justus extern bestätigt.

### Beobachtet

| Beobachtung | Prüfgrenze | Programme | Quelle |
|---|---|---|---|
| Kein Halt, jeder Schritt geprüft | 10^12 Schritte, alle drei Starts | 2 (`direkt.c` Run 45614962053; `zaehl_direkt.c` Run 45668615893) | [LE §2], [VB §4] |
| Kein K(C) (`C> 0 1 1`) | 10^9 lokal, 10^10 in Actions (Run 45668615893); bis 10^12 nur `zaehl_direkt.c` | 2 bis 10^10, 1 bis 10^12 | [VB §2, §4] |
| Kein Halt, **bedingt** (Regeln des Phasen-Automaten nur empirisch) | 10^24 (A, C) bzw. 10^25 (D), 1.110 Stichproben ohne Befund | Zyklus-Beschleuniger; zwei Actions-Läufe an jeder gemeinsamen Zehnerpotenz gleich (Runs 45684698614, 45682765314); bis 10^12 gegen `beschleuniger.py` validiert | [VB §5], PR 25 |
| Durchlaufmodell = direkte Simulation, byteweise | 10^9 Schritte, 36.944 Listenzeilen | 2 (`sweepmodell.py`, `zweitpruefung.c`) | [G1-3 §2] |
| Prüfpunkte (B/D liest 0, rechts `11`) 1,63 bis 1,64 Mio. je Start, keiner mit `111` | 10^9 | 2 (C, Rust) | [G1-2 §1] |
| Regel Z: `x = a + 4b + 7` am Ende jeder Fressphase, 76/76, 77/77, 76/76 | 10^9 | Listen aus C, Prüfung in Python | [G1] |
| a gerade an allen 232 Zyklusanfängen (also x ungerade, Voraussetzung von Regel F) | 10^9 | 2 (`zyklus.py`, `zyklus2.c`) | [ZY §5] |
| Zyklusfunktion sagt 68/76 (A), 67/76 (C), 66/77 (D) Zyklen exakt voraus, **keine falsch**; Rest „nicht anwendbar“, immer am linken Ende | 10^9 | 2 | [ZY] |
| Phasen-Automat (N1, N2, N2s, UA, LE, LG, VS) erklärt 99,995 % der Phasen | 10^17 (Run 45614962053) | Beschleuniger, bis 10^12 gegen `direkt.c` an rund 642.000 Schnappschüssen je Start gleich | [LE §1, §2] |
| Linkes Ende: 2.877 nicht erklärte Fälle in 13 Kernmustern; 13. Muster erst bei 8,2·10^16; „alt“-Anteil steigend (0,7 % → 1,5 %) | 10^17 | 2 (`formen.py`, `formen2.awk`) | [LE §3, §4] |
| VS-Familie als Regel mit 11 Fällen: 1.656 von 1.656 beobachteten Fällen richtig | 10^17 | Regel gegen Durchlaufmodell | [LE §4] |
| Keine erhaltene Größe; im Inneren nur m, S + r, x erhalten | 10^15 | 2 (`groesse.py`, `groesse2.c`), Runs 45676439532, 45679952727 | [GR] |
| Kein CTL-Zertifikat (Bandsprache mit zwei Automaten) | alle Größen bis 12×12 | SAT-Suche, kleine Größen durch Aufzählung bestätigt | [INV] |
| Läufe der drei Starts verschmelzen nicht | 10^9 | 1 | [G1 §1] |

### Offen

- Ob Gruppe 1 hält: **offen** [VB §8].
- Eine Invariante, die K(C) bzw. Halt ausschließt: keine gefunden [ZY §5], [GR §5], [INV], [VB §8].
- Regeln des Phasen-Automaten sind nicht bewiesen; Halt jenseits 10^12 nur bedingt ausgeschlossen [VB §4].
- Linkes Ende: 7 der 8 Familien ohne Regel, „alt“-Fälle ohne Regel, Sättigung nicht belegt [LE §4].
- Regel Z und erste/letzte Fressrunde nicht in Rocq [S2a]. Warum a immer gerade ist, ist nicht bewiesen [S2a], [ZY].
- Es fehlt eine Gleichung, die die Zahlen bindet (wie `gval G + 6 + κ = Q` in `PR_SBC.v`) [P26 §3].
- Laut Justus (25.11.): Gruppe 1 ruht mit diesem Stand.

### Extern (bbe, Stand 13.11.) [AB]

- Lean-Kern: Haltekonfigurationen, 10^4 Schritte, Umkodier-Durchläufe (114: 6 Regeln, 367: 8, 378:
  Verschieberegeln); native: 10^7 Schritte. Gerechnet: 10^9 (alle), 114 beschleunigt bis 1,29·10^10.
- Vermutet: „jeder Eintrag wächst je Zyklus um 2“. Gleiche Tabelle mit drei Starts erkennt bbe auch.
- **Gegenüber bbe sind wir weiter** (Rocq-Beschleunigung, Regel F, 10^12 lückenlos, 10^24/10^25 bedingt). Kein
  Widerspruch. Gegenüber slugbird nicht belegt: dort Halt nur vom linken Ende schon beschrieben, simuliert 1,6·10^14 (114)
  bis 2·10^14 (367, 378); wir 10^12 lückenlos, 10^24/10^25 bedingt [GU].

## M5-Gruppe: 318, 518, 322, 274

### Bewiesen (Rocq)

Nichts.

Durch **Tabellenvergleich** belegt (gilt für jede Schrittzahl, zwei Programme, nicht in Rocq) [M1 §1]:
- Alle vier sind die 5-Zustands-Maschine M5 `1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC` mit aufgeteiltem Zustand.
  Haltemuster: 318 und 322 `B> 1 1`, 518 und 274 `C> 1 1`.
- Start in M5: 318/518 ab A, 322 ab C, 274 ab D (gespiegelt). Die Läufe ab C und D sind ab Schritt 11 bzw. 25 gleich.
- In der 608er-Liste genau diese vier; in `decided` keine.

### Beobachtet

| Beobachtung | Prüfgrenze | Programme | Quelle |
|---|---|---|---|
| Kein Haltemuster (`B> 1 1`, `C> 1 1`) | 10^10 Schritte (Läufe ab A und ab C) | 2 (`m5sim.c`, `zweitpruefung.go`) | [M1 §3] |
| Kein Haltemuster (`B> 1 1`, `C> 1 1`), jeder Übergang gezählt | **8·10^14** (Läufe ab A, C, D) | bis 10^10 drei (`blocksim.c`, `zweitzaehlung.go`, `m5sim paare`); bis 10^11 dazu die direkte Simulation der Prüfstelle (Code nicht im Repo); 10^11 bis 8·10^14 zwei Programme, **ein Prinzip** (Sprünge bei exakt wiederholter Lage, Satz in [M3 §2]); Kontrollen 9/9, darunter ein eingebautes Haltemuster | [M3] |
| 318, 518 und M5 im Gleichschritt | 10^9 | 1 (`m5sim gleich`) | [M1 §1] |
| Zählerregeln 1 bis 3 (Binärzähler aus Ziffern Z/D1/D2/D3, Trenner W) | 3·10^8 | Zyklusdateien 2 Programme bytegleich, Regelprüfung nur Python | [M1 §2] |
| Lauf ab A trifft Lauf ab C nicht | 3·10^8 (Zyklusbeginne) | 1 | [M1 §1] |
| Beschleunigter Simulator stimmt an allen Zyklusbeginnen (40.324 ab A, 41.794 ab C) | 10^10 | 2 (`m5schnell.py`, `m5sim hash`) | [M2 §1] |
| Nur drei große Umbauten: ab A bei 29.754.240, ab C bei 87.823 und 874.896.314 | 8·10^14 (lokal, jenseits 10^10 nur jeder 5.000. Zyklus nachgeprüft) | 1 (+ Stichproben) | [M2 §3] |
| 83 bzw. 88 Wanddurchgänge (Paare) je Lauf, keine Umbauten | 8·10^14 | 1 | [M2 §2] |

### Offen

- Ob M5 bei `B> 1 1` / `C> 1 1` ankommt: **offen**. Bis 8·10^14 kommt es nicht vor [M3]; darüber von uns nicht geprüft.
  **Keine neue Grenze:** Laut `data/holdouts.json` (Stand 10.11.) simuliert slugbird (Holdout Guide, 3.11.) 274, 322 und 518
  bis 1,0·10^17 und 318 bis 1,0·10^20 Schritte (Status „rules“), das RobinCodes-Sheet (9.10.) alle vier bis mindestens 10^15.
  Nicht nachgeprüft, Programme dort unbekannt. Neu an [M3] ist nur die offen gelegte Zählung jedes Übergangs mit zwei Programmen.
- Wie ein Umbau die neuen Ziffern setzt (Lage und Phase): keine Formel gefunden, daher **kein Beweisplan** [M2 §4].
- Nächster Umbau, falls überhaupt, jenseits 8·10^14; `m5sim` reicht bis etwa 10^15 [M2 §6].
- Vorlagen im Pin wären `SBCv6a2.v` (Bahn ausrechnen) oder `SOBLv3.v` (Restklassen-Invariante); beide brauchen
  die fehlende Umbau-Abbildung [M2 §5].
- Justus hat die M5-Rückführung in #bb6 gepostet (laut Projektgedächtnis, 25.11.).

### Extern (bbe, Stand 8.11.) [AB]

- Lean-Kern: Durchläufe je Maschine; **318/518 im Gleichschritt bis zum ersten Bruch** (`Twin.lean`).
  Gerechnet: kein Halt bis 2·10^10 (318), 10^11 (322, 518), 10^9 (274).
- bbe kennt die Paare 318~322, 274~518 (gleiche Tabelle), 318~518 (gleicher Lauf), 322~274 (gleiche Bänder),
  aber nicht die gemeinsame 5-Zustands-Maschine M5. Unsere Umbau-Verfolgung bis 8·10^14 hat bbe nicht.
- Kein Widerspruch. Umbau „ab A bei 29.754.240“ gegen bbe „Schritt 29.787.121“: derselbe Umbau; 29.754.240 ist
  der Beginn des Zyklus, bei 29.787.121 erreicht der Kopf in C das linke Ende (direkt nachgerechnet) [M3 §1a].
- `Twin.lean` (Gleichschritt 318/518, Paare A-A, B-B, C-C, D-D, E-A, F-E, F-F) passt zu unserer M5-Zuordnung [M3 §1a].
- Bei 10^9 stimmen unsere Bänder ab C und D mit bbe überein (47.247 Zellen, 30.462 bzw. 30.463 Einsen) [M3 §1a].
- bbe-Ordner der vier Maschinen unverändert seit 13.11. (274: 24.11.), geprüft bis bbe-Kopf `47856cd8` (Prüfstelle).

## 396 mit 110, 587 und 88, 312, 449 (Familie Besuchsgesetz)

### Bewiesen (Rocq)

Von uns: **Rückführung** `halts tm c0 <-> W.trifft111 W.start` für 396 (`rocq/rueckfuehrung_396.v`, axiomfrei,
pruefen-Lauf 45700149762 in beiden Images, PR 21). Umformulierung, **keine Entscheidung** [RF].

Extern: busycoq #59 (Kopf `f23281d`) ist seit 26.11. in BB6 gemergt (`1ff6eba`): **88, 312, 449 halten**
(Runde 161.211, Block `1011`). Von uns nicht gebaut; bbe hat es mit Coq 8.20.1 gebaut [AB].

Durch **Tabellenvergleich** belegt [VK, Abschnitt F12]:
- Nach dem Zusammenlegen des Haltezustands sind die Kerne von 88, 312, 396, 449 gleich **bis auf E1**;
  nur 88 und 312 haben denselben Kern und laufen im Gleichschritt.
- 396 hält nur über F1, F wird über B1 oder E1 (`0RF`) erreicht.

### Beobachtet

| Beobachtung | Prüfgrenze | Programme | Quelle |
|---|---|---|---|
| Besuchsgesetz aus PR #59 gilt für 396, nur die Halteregel nicht: `V(1011x) = 0001x` statt Halt; 396 hält nur bei `111` | alle Wörter bis Länge 12 hinter dem Block | 1 (`gesetz.py`, Ausführen der Tabelle) | [396 §3] |
| 88 und 396 rundengleich, nicht schrittgleich | Runde 27 (rund 1,57 Mio. Schritte) direkt simuliert | 3 Wege zum Rundenmodell zeilengleich (`direkt.c` 27 Runden, `naiv.py` 34 Runden, `runde.c`) | [396 §4, §5] |
| 88 hält in Runde 161.211, wie in der Rechnung von PR #59 | – | 1 eigenes (`runde.c`), Run 45676623019 | [396 §4] |
| 396: kein Halt, nur zwei 1011-Ereignisse (Runden 161.211 und 194.647) | Runde 260.000 (Wort 1.615.087 Zellen) | 1 für den langen Lauf (`runde.c`), Run 45676623019 | [396 §4] |
| Familie des Besuchsgesetzes unter allen 608 (gespiegelt, alle Zustandspaare): genau 88, 110, 312, 396, 449, 587; 110 = 396 bis auf `V(111x)`, rundengleich bis zum ersten 111-Besuch. Folgerung „hält 396 nie, dann hält 110 nie“: **getestet, nicht bewiesen** (Gesetz für 110 nur so weit geprüft wie in dieser Zeile). **Nicht erfasst** (andere Lage oder Regel): 123, 223 (um eine Zelle verschoben, 123 mit zweiter Besuchsform; halten), 471 (`V(110x) = 001x`; hält nicht) | alle Wörter bis Länge 12; 27 Runden direkt | 2 (`suche_a.py`, `suche_b.c`), zeilengleich; Nachtrag 123/223/471 Stichprobe, 1 Programm | [FB], [AB §2] |
| 396: kein Halt, nie `111`, nie `011`; `11` am Rundenende nur in 161.210 und 194.646, danach je ein 1011-Ereignis | Runde 748.162 (A), bis 573.850 zeilengleich mit B | 2 (`runde.c`, `runde_b.cpp`), Run 45688978145 | [T2] |
| 396: kein Halt; Junk-Runden 161.210, 194.646, 757.565, 906.775, 1.042.306 (wie bbe). Keine Gestalt nach Art von 471 (L^(k+at) A B^t C D^t E T^(v+bt)): hinter L^k ein Binärzähler, die ersten m Zellen sind periodisch mit Zweierpotenz-Perioden, die mit m wachsen (2^18 bei m = 224, keine Periode ≤ 300.000 ab m = 232); ein gemeinsames P müsste Vielfaches von 2^18 sein | Runde 1.200.000 (X), B bis 1.238.663; Prüfstelle mit eigenem Code bis 300.000 (Tabelle bis m = 208) | 2 Rundenprogramme (`defizit.c`, `runde_b_anf.cpp`), jede Runde Anfangsfenster gleich; 2 Periodensuchen; Run 45771362724 | [WM] |

### Extern (bbe, Stand 26.11., Kopf `8515a2a4`) [AB §2, §3]

- **Lean-Kern** (für 396 und 110): Besuchsgesetz und Rundenform (seit 13.11.); Wortrechnung = Maschine, beide
  Richtungen (`halts_of_run`, `not_halts_of_run`); `junk_offset1` (harmlos), `junk_offset2_halts` (Halt);
  Defizitform des Zählers (2^e − c). **native:** 10^7 Schritte, erste 2.000 Runden.
- **Gerechnet:** 10^11 Schritte direkt; **bis Runde 4.000.000 kein `111`** (Commit `195c1340`, 26.11.;
  `piperun.c`, wortgleich mit `wordrun.c`/`deficit.c` nur bis 20.000 bzw. 200.000 Runden geprüft, also ein
  Programm mit Teilabgleichen; Wort dann 24.856.760 Zellen). 18 junk-Ereignisse, alle harmlos (nach einem
  Verdoppler, gerades Defizit 6). Gleiche Angabe im Ordner von 110. Von uns nur gelesen, nicht nachgerechnet;
  unsere eigenen Läufe enden bei Runde 748.162 [T2] und 1.200.000 [WM].
- **Gefahrenbedingung:** Halt nur, wenn ein junk mit Versatz 2 getroffen wird; das braucht ein ungerades Defizit
  beim Eintritt in den letzten `000`-Block.
- **Keine Invariante nur über das Wortende:** Mit beliebigem Zähler erreichen die letzten 48 Zellen `111` in 2–3
  Runden; ein bis zwei Besuche mehr führen etwa alle 3.500 Runden zu `111`. Für 587 findet SAT kein Zertifikat
  mit bis zu 7 Zuständen (auch nicht für das Gesetz von 110).
- 587 zusätzlich in Lean: `1011` und `111` nur am rechten Wortende; Lauf bis Runde 4.000.000.
- **Unsere Zahlen stimmen überein** (Ereignisrunden, Wortlänge je Runde). Was gegenüber bbe nur wir haben: die
  Rückführung in Rocq auf busycoqs Definitionen und das zweite unabhängige Rundenprogramm. Laut slugbirds Guide
  sind die Regeln (Beaver Math Olympiad Problem 10) schon in Rocq bewiesen; darüber hinaus ist nichts belegt [GU].

### Offen

- Ob 396 hält, also ob `111` je entsteht: **offen** [T2], [AB].
- Ob die Perioden der Anfangsfenster unbeschränkt wachsen (dann gäbe es für 396 keine Gestalt nach Art von 471,
  für kein P): **offen**, nur beobachtet bis Runde 1.200.000 [WM]. Den Zähler selbst beschreibt bbe schon auf
  Ereignisebene; neu ist bei uns nur die Periodentabelle je Runde. **396 ruht** (Justus 26.11.).
- „396 hält nie ⇒ 110 hält nie“ ist bei uns **getestet, nicht bewiesen**: Das Besuchsgesetz für 110 ist nur bis
  Wortlänge 12 und 27 Runden direkt geprüft, nicht in Rocq [FB]. bbe hat es in Lean auf eigenen Definitionen;
  von uns nicht geprüft.
- 396, 110, 587 haben weiterhin keinen PR in busycoq (auch unter den 53 offenen nicht, 26.11.); nur 587 hat eine Datei in cryptids [DA], [AB].
- Der Halte-Beweis von PR #59 ist **nicht** auf 396 übertragbar [396].
- Vorlage busycoq #55 (471, `1011 → 0001` wie 396, hält nicht): Ihre Gestalt mit festem Block hinter L^k gibt es
  bei 396 bis Runde 1.200.000 nicht, dort sitzt ein Zähler [WM]. Die Beweisidee „kein Besuch endet auf einer 0 direkt vor 11“ ruht (Justus
  26.11.); laut bbe reicht eine Aussage nur über das Wortende dafür nicht [AB §3].

## Einzelfall 133 (gleiche Tabelle wie 581) [133]

### Bewiesen (Rocq)

Nichts. Durch **Tabellenvergleich** belegt (eigenes Programm `tabelle.py`, dazu [VK] und bbe): 581 ist 133 mit
A↔C, B↔D vertauscht und gespiegelt, einzige Abbildung. 581 ist also die Tabelle von 133 **ab C**; eine andere
Rechnung. busycoq-PR 76 (offen) beweist nur 581; **133 ist dadurch nicht entschieden.**

### Beobachtet

| Beobachtung | Prüfgrenze | Programme | Quelle |
|---|---|---|---|
| 133 hält nicht, PR-76-Simulator (Python-Portierung) ab dem Start von 133 | **2^28 Runden = 7,92·10^334 Schritte (exakt gezählt)** | **1** (Portierung); frühe Besuche schrittgenau von `direkt133.c` bestätigt | [133], Run 45817990655 |
| Läufe 133 und 581 treffen sich nicht | Besuche bis Wortlänge 10^5 (wir), 10^9 Schritte (bbe) | 2 + bbe | [133], [VK] |

### Offen

- 133 **ruht** (Justus, 26.11.). Kein Rocq zu 133, bis geklärt ist, was slugbird als „Reported by others“ führt
  (`holdouts.json`; Justus sieht in Discord nach).

## Verwandtschaftskarte (alle 608 Holdouts)

### Bewiesen (Rocq)

Nichts. Durch **Tabellenvergleich** belegt, zwei Programme (`karte_a.py`, `karte_b.c`, gleiche 1.619 Zeilen) [VK §3, §4]:
- 376 von 608 Holdouts in **141 Familien**, fast alle „gleiche Tabelle, anderer Start“ (298 Holdout-Paare).
- **403 verschiedene Tabellen** bis auf Umbenennung und Spiegelung (498 ohne Spiegelung) [VK, Ergebnis].
- 69 Holdouts mit 5-Zustands-Kern; Gleichschritt belegt für 17 Paare, davon 2 Holdout-Paare (318/518, 88/312).
- busycoq `Eqv*.v` und cryptids `Equivalences.lean`: keine Holdout-Holdout-Paare [VK §1].

### Beobachtet

| Beobachtung | Prüfgrenze | Programme | Quelle |
|---|---|---|---|
| 6 weitere Paare im Gleichschritt (z. B. 69/543, 166/391, 190/394, 489/598), **unbelegt** | 10^9 | 1 (`divergenz.c`), Sieb in `karte_b.c` bis 10^6 | [VK §3] |
| Keine der 510 Tabellen-Paarungen verschmilzt | 10^6 (B), 10^5 (A) | 2 | [VK §3] |
| 14 Familien stehen jetzt ganz in neuen busycoq-PRs, z. B. F1 {244, 279, 339, 473, 489, 598}, F26 {38, 59, 124}; F12, F20 (M5) und Gruppe 1 nicht | PR-Refs bis 119, Stand 25.11. | 2 | [DA] |

### Offen

- F1: warum d833 hält und was die Starts unterscheidet; FAR-Starts (d581, d1250, d653, d934) [VK §3, §6].
- Übertragbarkeit der cryptids-Beschleunigungen auf andere Starts derselben Tabelle [VK §6].

## Korrekturen (später gilt)

| früher | später | Quelle |
|---|---|---|
| F12 = „dieselbe 5-Zustands-Maschine“, „zweite M5-artige Familie“ | Kerne gleich nur bis auf E1; nur 88 und 312 haben denselben Kern | [VK] korrigiert in PR 13 |
| Gleichschritt 88/312 mit Äquivalenten von 396 / 449: Richtung vertauscht | 88/312 mit 396.2/.3/.5/.7; 396 mit 449.1/.2 | [VK], [396 §6] |
| „naheliegend“, dass das Gesetz aus PR #59 auch 396 entscheidet | nicht übertragbar, 396 hält bei `1011` nicht | [396] |
| Zahl der verschiedenen Tabellen nicht angegeben | 403 (498 ohne Spiegelung) | [VK], Nachtrag PR 13 |
| Linkes Ende: „Urteil (a) mit Einschränkung“, „alt-Anteil steigt nicht“ (Entwurf bis 10^15) | Urteil offen; alt-Anteil steigt bis 1,5 % | [LE §7] |
| „Für Invariante regulär + Zählerbedingung gibt es im Pin keine Vorlage“ | `verify/PR_SBC.v` (busycoq PR #26) ist so eine Vorlage | [VL §4], [P26] |
| Satz K(C) ohne Voraussetzung | gilt nur für Läufe mit leerem Band rechts vom Start (Gegenbeispiel von Justus) | [VB §7] |
| Haltebedingung Teil 2 (B/D liest 0 vor `111`) vs. Teil 3 (C vor `111`) | gleichwertig, nachgerechnet | [G1-3 §3, Nachtrag] |
| 11 Prüfpunkte am linken Ende ungeklärt (27/39 Schritte nach Links-Rekord) | erklärt: C trifft auf Trenner `<1>`, 14 oder 26 Zellen vom Ende | [G1-2] → [G1-3 §2] |
| „x/2 ≥ Listenlänge“ in 24 von 76 Zyklen (Start A) | 19 von 77 mit anderer Abgrenzung; maßgeblich ist die Streuung −64 bis +27 | [G1] → [VL §3] |
| M5: Links-Rekord ab C bei 29.550.874 als Umbau gelesen | kein großer Umbau; echte Umbauten nur 87.823 und 874.896.314 (ab C) | [M1] → [M2 §2, §3] |
| M5: „bis 10^11 kein weiterer Umbau“ | bis 8·10^14 keiner | [M1] → [M2] |
| M5: Haltemuster „jenseits 10^10 nicht geprüft“ | bis 8·10^14 geprüft, kein Vorkommen | [M2 §4] → [M3] |
| M5: 8·10^14 als weiteste Prüfgrenze gelesen | keine neue Grenze: slugbird 10^17 (274, 322, 518) bzw. 10^20 (318), Sheet ≥ 10^15 (`holdouts.json`) | [M3] → Prüfstelle 26.11. |
| M5: 29.754.240 gegen bbe 29.787.121 „nicht abgeglichen“ | derselbe Umbau, zwei Zeitpunkte | [AB] → [M3 §1a] |
| Zyklus-Läufe ohne int64-Schutz (Runs 45675033053, 45682765314) | jenseits 10^24 nicht verwenden; Schutz seit Commit `509fb21` | [VB §5, §6] |
| busycoq BB6 „unverändert auf `33209bc7`“, PR #59 „offen, nicht gemergt“ | seit 26.11. `9c078ca`, #59 und #55 gemergt; 88, 312, 449, 471 upstream entschieden | [DA] → [AB §1] |
| 110 „neu“ in der Familie Besuchsgesetz | bei bbe seit 13.11. bekannt, mit Lean-Beweis des Gesetzes | [FB] → [AB §2] |
| Familie „genau 6“, „keine weitere Suche nötig“ | gilt nur für die wörtliche Lage; 123, 223 (verschoben) und 471 (andere `110`-Regel) sind Verwandte, alle drei entschieden | [FB] → [AB §2] |
| 396-Ergebnis (Teil 2) als eigener Befund | unabhängige Bestätigung von bbe (Stand 24.11.), keine Neuheit | [T2] → [AB] |
| „Unser Pin bleibt `33209bc7`“ (Abschnitt Abgleich) | Pin ist seit 26.11. `9c078ca` (PR 27) | Prüfstelle 26.11. |
| bbe 396/110: kein `111` bis Runde 3.000.000, 14 junk-Ereignisse | bis Runde 4.000.000, 18, alle harmlos (bbe `195c1340`) | [AB] → Prüfstelle 26.11. |
| „Hält 396 nie, dann hält auch 110 nie“ ohne Kennzeichnung | getestet, nicht bewiesen (Gesetz für 110 nur getestet) | [FB] → Prüfstelle 26.11. |
| „Wir sind weiter“ (Gruppe 1), „Was nur wir haben“ (396) ohne Bezug | nur gegenüber bbe; slugbird simuliert Gruppe 1 bis 1,6–2·10^14 (wir 10^12 lückenlos, 10^24/10^25 bedingt), M5 bis 10^17/10^20, die 396-Regeln laut Guide in Rocq | [GU], Prüfstelle 26.11. |
| 385: „offener PR 44 beweist Nicht-Halt“ (Guide 3.11.) | PR 44 in BB6 ohne 385, Beweis am 5.11. entfernt (`c94a67d`, Alk) | Prüfstelle 26.11., per git nachgesehen |
| Ob busycoq-PRs offen sind, „per git nicht sichtbar“ | sichtbar über `refs/pull/N/merge` (nur offene ohne Konflikt, Untergrenze); 53 am 26.11. | [DA] → Prüfstelle 26.11. |

## Was dieser Stand nicht enthält

- Den Thread „Invariante gegen K(C)“ (PR 19) nur indirekt (Regeln des Phasen-Automaten weiter empirisch).
- Den Stand von cryptids nach dem 25.11. (`f01ee56`) und Lean-PRs, die nicht in busycoq liegen.
- Das Wiki (BB(6), Beaver_Math_Olympiad, Klassenseiten) und die Beweisformen im Guide: von uns nicht gelesen,
  Angaben dazu laut Prüfstelle. Ob die gemeinsame M5 anderswo als bei uns steht, ist nicht geprüft.
- Inhalte aus Discord. Statt „erst in Discord fragen“ gilt jetzt: busycoq und bbe per git prüfen (CLAUDE.md).
