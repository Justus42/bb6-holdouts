# Familie Besuchsgesetz: Suche in allen 608 Holdouts

Thread „Familie Besuchsgesetz“, 25.11.2026. Nur Analyse, kein Rocq. busycoq und cryptids nur gelesen.

## Ergebnis

**Die Familie hat genau 6 Mitglieder: 88, 110, 312, 396, 449, 587.** Neu ist nur **110**
(`1RB0LB_0RC0LD_1LD1RE_0LA0RF_1RB0RD_0RB---`). 110 hat dieselbe 1011-Regel wie 396 (`0001x`, kein Halt)
und weicht nur bei `111` ab. Bis zum ersten Besuch auf `111` laufen 110 und 396 deshalb Runde für Runde
gleich; bei 396 kam bis Runde 260.000 kein solcher Besuch vor. Folgerung (unter dem für 110 nur getesteten
Gesetz): **Hält 396 nie, dann hält auch 110 nie** (getestet, nicht bewiesen; Nachtrag 26.11.). Die Umkehrung gilt nicht.

Gespiegelte Mitglieder oder solche mit anderem Zustandspaar gibt es nicht: alle 6 haben Eintritt C,
Rückkehr A, ungespiegelt, und dieselbe Rundenform.

## Tabelle

| Holdout | Tabelle | V(1011x) | V(111x) | Wörter ab Leerband wie 396 | busycoq Pin `33209bc7` | busycoq PR-Refs 1–120 | cryptids `f01ee56` | Wiki |
|---|---|---|---|---|---|---|---|---|
| 88 | `1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD1RB_0RC---` | hält | uneinheitlich (Halt oder Wort) | bis Runde 161.210; in Runde 161.211 trifft ein Besuch `1011`, 88 hält | nur Äquivalenzsatz (`Eqv_v3.v`) | PR #59 (hält; Kopf `f23281d`) | nichts | keine Seite |
| 110 | `1RB0LB_0RC0LD_1LD1RE_0LA0RF_1RB0RD_0RB---` | `= 0001x` (wie 396) | uneinheitlich (`1111…` hält, `11101…` → `1010 1…`, `11100…` mal Halt, mal Wort) | bis zum ersten Besuch auf `111`; bei 396 keiner bis Runde 260.000 | nur Äquivalenzsatz (`Eqv_v2.v`) | nichts | nichts | keine Seite |
| 312 | `1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD1RF_0RC---` | hält | hält | bis Runde 161.210, hält in 161.211 | nur Äquivalenzsätze (`Eqv_Misc.v`, `Eqv_v2.v`, `Eqv_v3.v`) | PR #59 | Rückführung `HasOdometerReduction` (keine Entscheidung) | BMO Problem 10, dort unter „Solved“: hält nach etwa 2^80000 Schritten (Ivapragovna, von „67“ bestätigt, Beleg nur Discord) |
| 396 | `1RB0LB_0RC0LF_1LD1RE_0LA0RB_0RD0RF_0LA---` | `= 0001x` | hält | – (Bezug) | nur Äquivalenzsätze (`Eqv_Misc.v`, `Eqv_v3.v`) | nichts | nichts | keine Seite |
| 449 | `1RB0LB_0RC0LD_1LD1RE_0LA0RF_0RD0LC_0RC---` | hält | uneinheitlich (Halt oder Wort) | bis Runde 161.210, hält in 161.211 | nur Äquivalenzsatz (`Eqv_v3.v`) | PR #59 | nichts | keine Seite |
| 587 | `1RB1LD_0RC0LF_1LD1RE_0LA0RB_0RD1RB_0LD---` | `= 1000x` | hält | bis Runde 161.210; in Runde 161.211 schreibt 587 `1000` statt `0001`, ab da verschieden | nichts | nichts | Beschleunigung bewiesen (`IsValidAcceleration`, beide Richtungen) und `HasOdometerReduction`; keine Entscheidung | keine Seite |

Erläuterungen:

- **Gesetz** (alle 6): `V(0x) = 1x`, `V(100x) = V(110x) = 000 V(x)`, `V(1010x) = 1010 V(V(x))`, dazu
  „Halt wird durchgereicht“ wie in PR #59. Geprüft durch direkte Simulation an allen Wörtern bis Länge 12
  (mit Block), für beide Werte der Zelle links neben der Null. Für 396 ist das Gesetz in Rocq bewiesen
  (`rocq/rueckfuehrung_396.v`), für die anderen nur so getestet.
- **Rundenform** (alle 6 gleich): Band `0^∞ 1 0 C> w`. Nach dem Besuch schreibt die Maschine links `10`
  vor das Ergebnis und beginnt den nächsten Besuch, ohne das Wort zu lesen. Erste Runde ab Leerband auf dem
  leeren Wort. Also: Startwort `s = V(leer) = 1`, Runde `s ← V(10 s)`, wie bei 396.
- **„uneinheitlich“** heißt: das Ergebnis hängt vom Rest hinter dem Block ab. Zahlen (Wörter bis Länge 12,
  beide x): 88 hält in 388 von 2.046 Fällen, 449 in 1.350, 110 in 1.108. Bei 110: `111` gefolgt von `1` hält
  immer; `1110` gefolgt von `1` gibt `1010 1…` (kein Halt); `11100…` hält oder nicht, ohne einfache Regel.
- **Wörter ab Leerband:** Bei allen 6 sind die Wörter der ersten 27 Runden direkt simuliert gleich (rund
  1,57 Mio. Schritte). Die weiteren Rundenzahlen folgen aus dem Gesetz zusammen mit den Läufen aus dem
  Thread 396: Runde 161.211 ist die erste mit einem Besuch auf `1011` (Run 45676623019, 88 hält dort wie in
  PR #59), 396 trifft bis Runde 260.000 nie `111` (derselbe Run). 312 und 449 habe ich nicht lang simuliert.
- **busycoq:** Zweig BB6 steht weiter auf `33209bc7`. „Nur Äquivalenzsatz“ heißt: Die Maschine steht dort in
  einem Satz `halts tm c0 <-> halts tm' c0` mit einer anderen Maschine; entschieden ist sie damit nicht.
  PR-Refs 1 bis 120 gelesen (neu seit dem letzten Abgleich: Ref 120, betrifft keines der Mitglieder). Ob
  PR #59 offen oder geschlossen ist, konnte ich nicht prüfen (siehe Abweichungen).
- **Wiki:** BMO-Seite zuletzt geändert am 21.11.2026. Problem 10 ist das Wortsystem von 312 (Regeln wie oben,
  `#1011` als Halt). Nur gelesen, nicht nachgeprüft.

## Wie gesucht wurde

Für jede der 608 Maschinen, ungespiegelt und gespiegelt, und für jedes Paar (Eintrittszustand c,
Rückkehrzustand a) aus 6 × 6 Zuständen. Das Gesetz nennt nur c und a, damit ist jede Umbenennung der
Zustände abgedeckt.

- **Besuch:** Zelle −2 = x, Zelle −1 = 0, das Wort ab Zelle 0, rechts Nullen, Kopf auf Zelle 0 im Zustand c.
  Der Besuch endet beim ersten Mal, dass der Kopf im Zustand a auf Zelle −2 steht; dann müssen die Zellen −1
  und −2 unverändert sein. Geht der Kopf weiter nach links, zählt das als Fehlschlag.
- **Rundenform:** Ab Leerband sind die ersten Konfigurationen „Zustand c, links daneben 0“ Kandidaten für den
  Rundenbeginn. Gesucht ist ein fester Linkskontext u und ein festes Präfix p, so dass nach jedem Besuch
  wieder `0^∞ u 0 c> p y` entsteht (y = Ergebnis des Besuchs).

| | Programm A (`suche_a.py`, Python) | Programm B (`suche_b.c`, C, getrennt geschrieben) |
|---|---|---|
| Gesetz | prüft jede Regel einzeln: V des Wortes gegen die Regel mit V des Restes | rechnet die Vorhersage des Gesetzes rekursiv über das ganze Wort (nur Blöcke `1011` und `111` simuliert) und vergleicht mit der Simulation des ganzen Besuchs |
| Rundenform | rechnet das Stück zwischen zwei Besuchen einmal symbolisch durch (Wort unbekannt, darf nicht gelesen werden) | simuliert ab Leerband direkt (10^6 Schritte) und prüft für jede beobachtete Runde (25), dass das nächste Wort `p · V(altes Wort)` ist |
| 608 Holdouts | 28 s | 0,6 s |

**A und B sind auf allen 608 Maschinen zeilengleich** (bis auf die Zählspalte, die bei A je Regel und bei B
insgesamt zählt): 6 Treffer, jeweils mit gleicher 1011-/111-Einordnung und gleicher Rundenform. Den Stand in
busycoq und cryptids haben ebenfalls zwei Programme ermittelt (`stand_a.py`: alle 240 Schreibweisen je
Tabelle wörtlich gesucht; `stand_b.py`: alle Maschinen-Strings ausgelesen und in Normalform verglichen);
Ausgaben `stand_a.txt` und `stand_b.txt` sind gleich.

## Kontrollen

Alles mit `bash analyse/besuchsgesetz/kontrollen.sh` (lokal 33 s, alle OK):

- **Positivkontrolle:** 88, 312, 449, 396, 587 werden von A und B gefunden.
- **Spiegelung und Umbenennung:** Die 5 Kontrollmaschinen in 4 Schreibweisen (original, gespiegelt,
  Zustände B–F zufällig umbenannt, beides) = 20 Fälle: alle gefunden, A = B (`testfaelle.py umbenannt`).
- **Negativkontrollen** (müssen anschlagen, tun es):
  - `FEHLER=1` (falsche Regel `V(1010x) = 1010 V(x)`): A und B finden nichts.
  - `FEHLER=2` (ohne Spiegelung): nur 10 der 20 Fälle.
  - `FEHLER=3` (falsche Rundenform verlangt): keine Rundenform gefunden.
- **Direkte Simulation:** Wörter der Runden 0 bis 27 bei allen 6 gleich wie bei 396 (`direkt.c` aus
  `analyse/396`).
- Zusätzlich (nicht im Skript): Alle 253 Einzel-Mutationen von 396 durchsucht: 5 erfüllen das Gesetz, alle 5
  mit derselben Rundenform; A = B. Gleiche Tabellen mit anderem Startzustand (25 Fälle) landen ebenfalls in
  derselben Rundenform (Startwort leer oder `1`). Die Rundenform ist also robust; eine Maschine mit Gesetz,
  aber ohne Rundenform, gab es in keiner Testmenge, deshalb die künstliche Kontrolle `FEHLER=3`.

## Bericht

- **Ergebnis:** Unter den 608 Holdouts erfüllen genau 6 das Besuchsgesetz aus PR #59 mit der Rundenform von
  396: 88, 110, 312, 396, 449, 587. Neu ist 110. 110 läuft wie 396, bis ein Besuch auf `111` trifft (bei
  396 bis Runde 260.000 nie); wer zeigt, dass 396 nie hält, hat damit auch 110 (bis auf den Beweis des
  Gesetzes für 110; die Folgerung ist also nur getestet, nicht bewiesen, Nachtrag 26.11.).
- **Belege:** Branch `claude/project-thread-493yq5`; Ausgaben `ergebnis_a.tsv`, `ergebnis_b.tsv`,
  `stand_a.txt`, `stand_b.txt`; `kontrollen.sh` grün (lokal). Kein Actions-Lauf nötig (alles unter 1 Minute,
  nur die Stand-Suche dauerte 5 min). Lange Läufe aus dem Thread 396: Run 45676623019.
- **Abweichungen und eigene Fehler:**
  - Die Seite github.com ist aus der Sitzung gesperrt (403). Ob PR #59 offen ist, habe ich deshalb nicht
    geprüft und nicht umgangen. Gelesen wurde nur per `git fetch` (öffentlich).
  - Mein erster Ansatz für die Rundenform nahm die erste Konfiguration „Zustand c, links 0“ nach dem Besuch.
    Das ist bei allen Mitgliedern ein kleiner Zwischenbesuch auf `0…`, nicht der Rundenbeginn. Behoben über
    den Linkskontext, gemeldet hat es die Positivkontrolle.
  - Programm 1 zum Stand war zuerst zu langsam (ein Lauf hing, abgebrochen); jetzt durchsucht es in den
    PR-Köpfen nur die gegenüber BB6 geänderten Dateien.
  - Eine Nebenzählung (Maschinen mit nur einem Teil des Gesetzes) habe ich nach 10 min abgebrochen; sie ist
    nicht im Bericht.
  - Die Rundenzahlen 161.211 und 260.000 stammen aus einem einzigen langen Lauf (`runde.c`) des Threads 396;
    für 110, 312, 449 sind sie gefolgert, nicht simuliert.
- **Offene Punkte:** (1) Gesetz und Rundenform für 110 sind nur getestet, nicht bewiesen; mit der Vorlage
  `rocq/rueckfuehrung_396.v` wäre der Beweis vermutlich kurz (Rocq braucht dein OK). (2) Ob jemand an 110
  arbeitet, nur über Discord klärbar. (3) Die Bedeutung von 110 hängt an der offenen Frage, ob das
  Wortsystem ab `1` je `111` trifft.
- **Empfehlung:** 110 als zweite Maschine an die 396-Frage hängen (gleiches Wortsystem, nur andere
  111-Regel) und in #bb6 erwähnen, wenn du 396 ansprichst. Keine weitere Suche nach dieser Familie nötig.
