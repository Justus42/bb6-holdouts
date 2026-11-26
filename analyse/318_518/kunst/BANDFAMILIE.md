# Bandfamilie für die Umbau-Messung an künstlichen Bändern (Auflage 1)

Festgelegt 26.11.2026, **vor** dem ersten Lauf auf künstlichen Bändern. Freigabe: Prüfstelle und Justus,
Nachricht vom 26.11. (Idee 1 der Lückenkarte, sechs Auflagen). Maschine M5 = `1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC`.

## Bausteine (wie Teil 1/2, `m5schnell.py`)

| Name | Zellen | Rolle |
|---|---|---|
| `U` | `11111010` | Füllstück (Lücke) |
| `Z` | `111010` | Ziffer Phase 0 |
| `D1` | `10111111111010` | Ziffer Phase 1 |
| `D2` | `10101111111010` | Ziffer Phase 2 |
| `D3` | `11111111111010` | Ziffer Phase 3 |
| `W` | `1111111010` | Trennstelle |

## Eingabefamilie F

Jedes Eingabeband ist ein Zyklusbeginn: Zustand A, Kopf direkt rechts vom Band auf einer leeren Zelle, links
vom Band nur Nullen. Das Band lautet

    R  U^g1 X1  U^g2 X2 ... U^gn Xn  U^u  1^e

mit

- **Rest R** aus der Liste der Reste, aus denen ein natürlicher Umbau gestartet ist:
  - `RC1` = `11111111101011111111111110101011111111111010101111111111111010` (62 Zellen), Vorzustand des Umbaus ab C
    bei Schritt 87.823 (eigener Lauf, CRC wie `m5sim hash`);
  - `RX` = `11111111101011111111111010111111101010111111111110` (50 Zellen), laut Teil 2 §2 der Rest vor dem Umbau ab C
    bei 874.896.314 und der Rest des Laufs ab A seit 5,75·10^14. Wird mit der Kontrolle (Auflage 2) bestätigt,
    falls die Kontrolle über 10^7 Schritte freigegeben wird; sonst so gekennzeichnet.
  - Der Rest vor dem Umbau ab A (29.754.240) kommt dazu, **falls** die Kontrolle freigegeben wird; er ist bisher nicht
    gespeichert.
- **Bausteine X1..Xn** aus {`D2`, `D3`, `W`}, mindestens eine Ziffer. Nur D2/D3, weil dann der Übertrag durch alle
  Ziffern in den Rest läuft (so war es vor allen drei natürlichen Umbauten, Teil 2 §3). Z und D1 kommen in F nicht vor.
- **Lücken** g1..gn ≥ 0, **u** ≥ 0, **Ende** e ∈ {0, 4}.

## Teilfamilien und Erzeugung (fester Zufallskeim 20261126, Programm `familie.py`)

| Teil | Inhalt | Anzahl |
|---|---|---|
| **F-voll** | vollständiges Raster: n = 1, 2, 3 Ziffern (kein W), jede Phase D2/D3, jede Lücke 0..5, u ∈ {0, 1, 2}, e ∈ {0, 4}, beide Reste | n=1: 2·6·3·2·2 = 144; n=2: 4·36·3·2·2 = 1.728; n=3: 8·216·3·2·2 = 20.736; zusammen 22.608 |
| **F-W** | wie F-voll mit n = 2 Ziffern, dazu **ein** `W` an jeder möglichen Stelle (vor der 1., zwischen, nach der 2. Ziffer) mit Lücke 0..3 davor | 4·36·3·3·4·2·2 = 20.736 → **Stichprobe 3.000** |
| **F-groß** | n = 4..12 Ziffern, Lücken etwa verdoppelt wie im natürlichen Lauf: g_k = round(c·2^(k−1)) + j_k mit c ∈ {1, 1,5, 2, 3}, j_k zufällig in −2..2 (≥ 0); Phasen zufällig; 0 bis 3 `W` an zufälligen Stellen mit Lücke 0..3; u zufällig 0..3; e zufällig; Breite ≤ 9.000 Zellen | **Stichprobe 1.500** |

Breitengrenze: Ein Umbau dauert rund 0,1·Breite² Schritte (Teil 2 §3). Mit Breite ≤ 9.000 bleibt er unter 10^7.

## Lauf und Einteilung des Ergebnisses

Je Eingabe ein Lauf von `kunst umbau A 10000000 100 5` (höchstens 10^7 Schritte, höchstens 5 Zyklusbeginne). Jeder
Lauf zählt beide Haltemuster (B1 → A liest 1; C1 → E liest 1) über **alle** seine Schritte.

| Klasse | Bedeutung |
|---|---|
| **H** | ein Haltemuster kommt vor (Befund, wird einzeln berichtet; Lauf geht trotzdem weiter) |
| **U** | erster Zyklus dauert mehr als 10·Breite (großer Umbau, wie Teil 2) und danach zerlegt sich das Band an einem der folgenden Zyklusbeginne mit Rest < 200 Zellen (wie `umbau_karte.py`) |
| **U-R** | wie U, aber der Rest danach ist keiner der Reste aus F |
| **U-X** | großer Umbau, aber kein folgender Zyklusbeginn zerlegt sich (verlässt das Schema) |
| **K** | kein großer Umbau: der erste Zyklus ist kurz (Übertrag ändert nur den Rest) |
| **L** | Schrittgrenze 10^7 erreicht, bevor der Umbau endet |

U-R, U-X, K und L **verlassen** die Familie bzw. das Schema; sie werden gezählt und mit Beispielen gezeigt, nicht
verworfen (Auflage 4).

## Was gemessen wird

Für jede Klasse U / U-R: Lage der alten Ziffern, `W` und des Endes; Lage, Art und Phase der neuen Bausteine nach dem
Umbau (wie `umbau_karte.py`): Zuordnung alte Ziffer → nächstes neues `W` (Versatz), Ziffern je Abschnitt zwischen
neuen `W` (Abstand vom linken `W`, Phase), Dauer, neuer Rest.

Gesammelt wird mit **einem** Programm (`kunst.c` + `familie.py`). Jede daraus behauptete Regel wird mit einem
**zweiten**, unabhängig geschriebenen Programm geprüft, bevor sie im Bericht als Regel steht (Auflage 5).
Kein Rocq. Rechenzeit insgesamt unter 10 Minuten (Auflage 6).
