# Invarianten-Suche mit Prüfwerkzeugen (Versuch, 1 Block)

Stand 25.11.2026. Reine Analyse, **kein Rocq**. Werkzeuge und Rohergebnisse in `analyse/invarianten/`.
Auftrag: Justus' Nachricht vom 25.11. (Thread "Invarianten-Suche mit Prüfwerkzeugen").

## Ergebnis in Kürze

**Für Gruppe 1 funktioniert es nicht.** Ich habe zwei Wege ausprobiert, beide mit Positivkontrolle an
einer Maschine, deren Nichthalten schon bewiesen ist.

- **Weg 1, Zählerebene (CHC-Löser Z3/Spacer und Eldarica):** Schon die Positivkontrolle scheitert.
  Für RGRv1 aus busycoq (4 Zähler, 3 Regeln, bewiesen) findet keiner der Löser die Invariante,
  obwohl es eine gibt (die busycoq-Invariante, von mir übersetzt, ist für Z3 und für eine Aufzählung
  ohne Z3 gültig). Fehler im Modell findet Spacer sofort, wenn sie kurz sind. Für Gruppe 1 lässt sich
  das Phasenmodell gar nicht als CHC aufschreiben: der Zustand ist eine unbeschränkte Liste, das linke
  Ende hat keine vollständigen Regeln, und "Halt" ist in Token-Sprache nicht formuliert.
- **Weg 2, Bandsprache (SAT-Suche nach zwei Automaten wie die CTL-Zertifikate in cryptids):**
  Das Werkzeug funktioniert. Bei der Positivkontrolle findet es **genau** das Zertifikat, mit dem
  cryptids die Maschine `1RB0RC_1LC1RD_1RA1LE_1LA0RD_0LE1RF_1LB---` beweist. Für Gruppe 1 gibt es
  auf der echten Tabelle **kein** solches Zertifikat bis zu den unten genannten Größen, für keinen der
  drei Starts. Das ist bewiesen im Sinne von "SAT-Löser sagt UNSAT", für die kleinen Größen von einem
  zweiten Programm (vollständige Aufzählung) bestätigt.
- **Empfehlung:** abbrechen. Weg 1 ist für unbeschränkte Listen ungeeignet; Weg 2 kann man größer
  rechnen, aber ich erwarte (unbelegt, Begründung in Abschnitt 4) dass Gruppe 1 keine Invariante dieser
  Art hat.

## 1. Weg 1: Zählerebene mit CHC-Lösern

**Positivkontrolle:** `busycoq/verify/RGRv1.v` am Pin, Maschine `1RB1LA_0LC0RE_---1LD_1LA0LF_1RB1RE_1RB0LB`
(dort `nonhalt0`, bewiesen). Zustand `S0 n1 n2 n3 n4`, drei Regeln (Inc, ROv, LOv), Start `S0 4 5 2 1`.
"Schlecht" ist jeder Zustand, auf den keine Regel passt. busycoq beweist das Nichthalten mit einer
Invariante WF, die eine Fallunterscheidung braucht; in S0-Koordinaten:
`b≥1, c≥1, d≥0, a≥0` und `(c≤b und a+b ≥ c+d+4)` oder `(c>b und a+b ≥ c+d+6)`.

| Versuch | Ergebnis |
|---|---|
| Spacer (Z3 5.4.1, `chc_rgr.py`), 5 Min. | keine Antwort (abgebrochen) |
| Spacer, drei Einstellungen (`spacer_opts.py`), je 3 Min. | `unknown` |
| Eldarica 2.1 (`rgr.smt2`), 5 Min. | keine Antwort (abgebrochen) |
| Spacer, 30 Min. | siehe unten (ERG_SPACER30) |
| Spacer mit menschlichem Hinweis: Zustandsraum von Hand in die zwei Fälle geteilt (`chc_rgr_geteilt.py`) | keine Antwort in 200 s (abgebrochen) |
| Hand-Invariante WF prüfen (`rgr_wf_check.py`): Z3 und Aufzählung ohne Z3 bis 40 je Zähler | gültig (Start, Erhalt unter allen 3 Regeln, kein schlechter Zustand; 1.040.690 Zustände, 0 Fehler) |

Negativkontrollen (Modell mit eingebautem Fehler):
- Start `S0 0 2 3 0` (nach einem Schritt hängt das System): Spacer findet den Gegenbeispielpfad in 0,02 s.
- ROv mit `1+n1` statt `2+n1` (System hängt nach 246 Regelschritten, nachgerechnet): Spacer findet
  den Pfad in 5 Min. **nicht**. Spacer findet also nur kurze Fehler, und tiefe weder Fehler noch Beweis.
- Erst gewählte Negativkontrollen waren falsch: Start `S0 0 1 1 0` und LOv mit 2 statt 3 hängen gar
  nicht (Spacer bewies den ersten Fall zu Recht sicher; der zweite läuft 10^6 Regelschritte ohne Hängen).
  Ich habe sie durch die obigen ersetzt.

**Gruppe 1 auf dieser Ebene:** nicht formulierbar, aus drei Gründen.
1. Ein CHC-Löser über ganzen Zahlen braucht eine feste Zahl von Zählern. Der Phasenzustand von
   Gruppe 1 ist eine Token-Liste mit tausenden Elementen (bei 10^15 rund 7.800), die Grenze wandert
   über die ganze Liste. Listen als Arrays würden Invarianten mit Allquantoren verlangen; damit
   kommen die Löser noch schlechter zurecht als mit RGRv1.
2. Das linke Ende hat keine vollständigen Regeln (13 Kernmuster bis 10^17, nicht gesättigt,
   `gruppe1_linkes_ende.md`). Ein Übergangssystem ohne diese Fälle wäre falsch; mit "beliebig"
   an dieser Stelle wäre jede Invariante wertlos.
3. "Halt" (bzw. das Vorzeichen `C> 0 1 1`) ist in Token-Sprache nicht ausgedrückt
   (`gruppe1_zyklus.md` Abschnitt 5): die Prüfstellen liegen mitten in Pendelschwüngen, die das
   Phasenmodell überspringt.

Wenn die Löser schon RGRv1 (4 Zähler) nicht schaffen, ist von einer Listenversion nichts zu erwarten.

## 2. Weg 2: Bandsprache per SAT

Idee: statt Zählern eine **reguläre** Invariante auf der echten Maschine, also ohne jede unbewiesene
Regel. Format genau wie `CtlCertificate.lean` in google-deepmind/cryptids: ein Automat für das linke
Halbband, einer für das rechte, eine Menge angenommener Tupel (linker Zustand, TM-Zustand, gelesenes
Bit, rechter Zustand). Die Bedingungen (Start angenommen, kein angenommenes Tupel hält, jeder
abstrakte Nachfolger angenommen) sind endlich prüfbar; cryptids hat dafür einen Lean-Beweis
(`ctl_certificate_implies_is_does_not_halt`). Ein gefundenes Zertifikat wäre also unmittelbar in Lean
nutzbar und in Rocq leicht nachzubauen.

- `ctl_sat.py` kodiert die Suche für feste Größen nL × nR als SAT (CaDiCaL über python-sat),
  mit Symmetriebrechung (Automatenzustände in Breitensuche-Reihenfolge).
- `ctl_pruefer.py` (zweites Programm, ohne SAT): prüft ein Zertifikat Bedingung für Bedingung wie
  `ctlCheck` und lässt zusätzlich die echte Maschine laufen (jede Konfiguration muss angenommen sein).
- `ctl_brute.py` (drittes Programm, ohne SAT): zählt für kleine Größen **alle** Automatenpaare auf und
  bestätigt so die Aussagen "kein Zertifikat dieser Größe" unabhängig von SAT-Kodierung und
  Symmetriebrechung.

**Positivkontrollen** (`ergebnisse/kontrollen_ctl.txt`):
- cryptids `M_1RB0RC_1LC1RD_1RA1LE_1LA0RD_0LE1RF_1LBHHH` (Nichthalten in cryptids per CTL-Zertifikat
  bewiesen): kleinste Größe 3×2, gefunden in < 0,1 s, **identisch** mit dem Zertifikat in der
  Lean-Datei (gleiche Automaten, gleiche 4 Tupel). Prüfer: gültig, 10^6 Schritte ohne Verstoß.
- cryptids `M_1RB0RC_1LC0LD_1RA1RC_1RA1LE_0LB1RE_HHH1RA`: 1×1 genügt (Zustand F wird nie betreten,
  also trivial). Prüfer: gültig.

**Negativkontrollen:**
- Haltende Maschinen (BB(4)-Sieger, 107 Schritte; BB(5)-Sieger, 47.176.870 Schritte): kein Zertifikat
  in allen 36 Größen bis 6×6, wie es sein muss.
- Prüfer mit 6 verfälschten Zertifikaten (Tupel entfernt, je ein Automatenübergang geändert,
  Halt-Tupel ergänzt, falscher Start, haltende Tabelle): alle 6 abgelehnt.
- Mit und ohne Symmetriebrechung: gleiche Ergebnisse in allen 16 Größen bis 4×4, für 4 Maschinen.
- SAT gegen Aufzählung (`abgleich_brute.sh`, `ergebnisse/abgleich_brute.txt`): 321 Fälle (Gruppe 1 mit
  allen drei Starts bis 3×3, dazu 50 Zufallstabellen mit je einem Haltübergang bis 3×2/2×3), davon 162 mit
  Zertifikat, **0 Abweichungen**.

**Gruppe 1** (Tabelle `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC`; 367 und 378 sind dieselbe Tabelle
ab D und C, Umbenennung und Spiegelung ändern die Existenz eines Zertifikats nicht, die Spiegelung
tauscht nur nL und nR):

ERG_G1

Auffällig: Große linke Automaten mit kleinem rechten werden in Bruchteilen einer Sekunde verworfen,
die schweren Fälle sind die mit großem rechtem Automaten.

## 3. Prüfweg und Abweichungen

- Kein Rocq, kein Workflow `pruefen` (es wurde nichts bewiesen, was eingereicht würde).
- Zählungen, auf die sich das Urteil stützt: "kein Zertifikat bis Größe …" kommt von `ctl_sat.py`;
  für alle Größen bis 3×3 bestätigt `ctl_brute.py` unabhängig. Für größere Größen gibt es nur das
  SAT-Ergebnis plus die indirekten Kontrollen oben. Das ist eine Lücke.
- Eigene Fehler: zwei Negativkontrollen für Weg 1 waren zuerst falsch gewählt (siehe Abschnitt 1).
  Ein Abbruchbefehl (`pkill -f ctl_sat`) hat nebenbei einen Kontrolllauf mit beendet; wiederholt.
- Versionen: Z3 5.4.1 (pip z3-solver), python-sat 1.9.dev25 mit CaDiCaL 1.5.3,
  Eldarica 2.1. cryptids Stand f01ee56 (25.11.2026), busycoq Pin 33209bc7.

## 4. Warum vermutlich keine reguläre Invariante (unbelegt)

Ein CTL-Zertifikat liest links und rechts **unabhängig**; es kann nur endlich viele Fälle unterscheiden.
Im Phasenmodell läuft rechts ein Zähler r (die `100`-Blöcke, von x−1 bis 0), links wandert die Grenze
pro zwei Phasen ein Element. Ob der Kopf an einem `0 1 1`-Fenster in C oder D ankommt, hängt an der
Parität der passierten `011`-Blöcke. Wenn der Ausschluss von `C> 0 1 1` davon abhängt, dass r und die
Lage der Grenze zusammenpassen (eine Gleichung zwischen zwei unbeschränkten Zahlen), dann kann ihn
kein endlicher Automat ausdrücken, egal wie groß. Das ist eine Vermutung; geprüft habe ich nur, dass
es bis zu den genannten Größen nichts gibt.

## 5. Offene Punkte

- Weg 2 größer rechnen (in Actions) ist möglich, aber nach Abschnitt 4 wenig aussichtsreich.
- Weg 1 würde erst sinnvoll, wenn Gruppe 1 auf endlich viele Zähler zurückgeführt ist; das ist genau
  die offene Frage aus `gruppe1_linkes_ende.md`.
- Das SAT-Werkzeug (`ctl_sat.py` + `ctl_pruefer.py`) ist allgemein; man könnte es über alle 608
  Holdouts laufen lassen. Erwartung: kaum Treffer, weil bbchallenge solche Verfahren (FAR, CTL) schon
  angewendet hat (unbelegt, nicht nachgesehen).

## Aufrufe

```
cd analyse/invarianten
pip install z3-solver python-sat
python3 chc_rgr.py [ok|fehler_rov|fehler_init]      # Weg 1, RGRv1
python3 rgr_wf_check.py 40                          # Hand-Invariante pruefen
./kontrollen_ctl.sh                                 # Weg 2, Kontrollen
python3 ctl_sat.py <TM> <nL> <nR> [Start] [--aus z.json]
python3 ctl_pruefer.py z.json 1000000
./ctl_suche.sh <TM> <Start> <MAX> <Zeitlimit_s> <Log>   # alle Groessen bis MAX x MAX
./abgleich_brute.sh                                 # SAT gegen Aufzaehlung
```
