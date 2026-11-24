# Vorlagen fuer Kandidaten: Monotone list und Shift-overflow structural counter

Erzeugt mit `python3 -I scripts/vorlagen.py <busycoq/verify>`. Nur Beschreibung: es wird nichts
bewiesen und nichts beansprucht. Vor jeder Arbeit an einer Maschine in #bb6 pruefen, ob jemand
anderes daran arbeitet.

- Daten: `data/holdouts.json` (SHA-256 `84e7b8ac2ca92ded…`), `data/kandidaten.csv`
- busycoq: `ccz181078/busycoq` @ `33209bc7dc282b38c8cd6be507bfc551fea56108`; Pfade unten relativ zu `verify/` am Pin
- **Naehe k/12**: groesste Zahl gleicher Uebergaenge unter Spiegelung (L/R) und beliebiger
  Umbenennung der Zustaende; 12/12 hiesse Spiegel-Zwilling bzw. Umbenennung. Ein grobes Mass,
  es sagt nichts darueber, ob eine Beweistechnik uebertragbar ist.
- **Simulation**: 3.000.000 Schritte ab Leerband, Start A. Rekord = der Kopf betritt eine noch nie
  besuchte Zelle; angegeben ist der Zustand danach. Band in Kurzform, `(w)^e` = e-mal w.
  Das ist eine **Beobachtung** ueber den Anfang des Laufs, keine Aussage ueber das Verhalten.

## Auf einen Blick

- Spiegel-Zwillingspaare unter den Kandidaten (wie TM1/TM2 in PR_Loop4Mono, jeweils mit anderem
  Startzustand): 31/222, 114/378, 141/315, 274/518, 367/378
- In der Simulation bandgleich (ohne Zwillinge zu sein): 318/518
- Spiegel-Zwilling einer gemergten Maschine (decided): keiner der Kandidaten
- Naehe zu PR_Loop4Mono TM1: 4–5/12 bei allen Kandidaten (zum Vergleich: ein Spiegel-Zwilling haette 12/12)
- Monotone list: Beweise im Pin 4x haelt, 10x haelt nicht
- Shift-overflow structural counter: Beweise im Pin 5x haelt, 7x haelt nicht

## Referenz: `PR_Loop4Mono.v`

- Pfad im Pin: [`verify/PR_Loop4Mono.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/PR_Loop4Mono.v); in decided Klasse Monotone list (n=652, n=950)
- TM1 `1RB1LE_0RC0LC_1LD0RA_0LA0LF_0LC0LE_0LD---` und TM2 `1RB0LC_0RC0RF_1LD1RE_0LA0RA_0RA0RE_0RB---`; TM2 ist der Spiegel-Zwilling von TM1 (Zustaende A..F = C D A B E F
  dort, Start A dort = Zustand C hier). Beide Theoreme: `halts tm c0` (die Maschinen **halten**).
- Technik laut Dateikopf: an linken Rekorden (Zustand D am linken Ende) ist das Band eine Liste
  `W(x0) s0 W(x1) s1 …` mit `W(e) = (10)^e` und Trennern `s` in {0,1}; ein Listenmodell mit
  `check` (native_compute) laeuft 1.307.718 Ticks bis zu einem Haltefenster.
- Halteuebergang: F1
- Simulation TM1: waechst nach links (3614 neue Zellen links, 212 rechts), Rekorde dort meist in Zustand D, A; Band beim letzten Rekord (Schritt 2.995.182, Breite 3827): `0^inf <A 0 (01)^33 0 (01)^117 0 (01)^117 0 (01)^117 0 (01)^117 0 (01)^117 0 (01)^109 ...`

## Monotone list

Gemergte Beweisdateien dieser Klasse (decided, by=proof): 7 Dateien, 14 Maschinen.

Urteil = Haupttheorem der Datei fuer die Maschine selbst (exakt) oder ihr Spiegelbild mit
Start A (gespiegelt); `?` = in keiner dieser Formen gefunden.

| Datei (Pin) | Zeilen | Maschinen aus decided: n, Urteil laut Datei, Form in der Datei |
|---|---:|---|
| [`verify/FARv1.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/FARv1.v) | 487 | n=462 `1RB1LB_1LC1RE_0RD0LB_0LB1RA_1LA0RF_---0RC` haelt nicht, exakt<br>n=1182 `1RB0LD_1LC1RC_1RE1LA_---0LE_0LF0RC_0RC1LB` haelt nicht, gespiegelt<br>n=1509 `1RB1LE_0LC0RA_0RA1LD_1LA1RA_1RD0LF_---0LB` haelt nicht, gespiegelt |
| [`verify/Loop4Mono_v2.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/Loop4Mono_v2.v) | 2382 | n=306 `1RB0LE_0RC1RB_1LD0RA_1LA---_1LA1LF_0LE1LC` haelt nicht, gespiegelt<br>n=1427 `1RB0LC_1RC---_1LD0RE_0LA1LD_1RC1RF_0RE1RA` haelt nicht, exakt |
| [`verify/Loop4Mono_v3.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/Loop4Mono_v3.v) | 3437 | n=80 `1RB1RF_0LC0RB_1LA0LD_1LE---_1RF1LF_1LC0RA` haelt nicht, gespiegelt<br>n=1512 `1RB1LB_1LC0RE_1LE0LD_1LA---_1RF1RB_0LC0RF` haelt nicht, gespiegelt |
| [`verify/Loop4Mono_v4.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/Loop4Mono_v4.v) | 724 | n=76 `1RB1RA_1LC1RE_---1LD_1LE0LF_0RA0LB_0RF0LA` haelt nicht, gespiegelt<br>n=1068 `1RB0RF_0LC0RD_1LD1LC_1RE1LB_---1RA_0LF0RC` haelt nicht, exakt |
| [`verify/Loop4Mono_v5.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/Loop4Mono_v5.v) | 1122 | n=177 `1RB1RA_1LC1RE_1LA1LD_1LC0LF_---0RA_1LA0LA` haelt nicht, gespiegelt |
| [`verify/Loop4Mono_v6.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/Loop4Mono_v6.v) | 1533 | n=79 `1RB1LE_0LC0RF_1LD1RD_1RC1RA_0LB0LA_0RC---` haelt, gespiegelt<br>n=1285 `1RB1RC_1LA1RA_1RE1LD_0LE0LC_0LB0RF_0RB---` haelt, gespiegelt |
| [`verify/PR_Loop4Mono.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/PR_Loop4Mono.v) | 1676 | n=652 `1RB1LE_0RC0LC_1LD0RA_0LA0LF_0LC0LE_0LD---` haelt, exakt<br>n=950 `1RB0LC_0RC0RF_1LD1RE_0LA0RA_0RA0RE_0RB---` haelt, exakt |

### n=114 `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC`

- slugbird: Status `rules`, simuliert 1.6e14 Schritte; busycoq: `open`, keine PR
- Aequivalente Maschinen laut holdouts.json: 2, busycoq erwaehnt sie in Eqv_v2.v
- Spiegel-Zwillinge in Liste/decided: n=378 (Start A dort = Zustand C hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/FARv1.v` 4/12 (n=462); `verify/Loop4Mono_v2.v` 4/12 (n=306); `verify/Loop4Mono_v3.v` 4/12 (n=80); `verify/Loop4Mono_v5.v` 4/12 (n=177); `verify/Loop4Mono_v6.v` 4/12 (n=79); `verify/PR_Loop4Mono.v` 4/12 (n=652); `verify/Loop4Mono_v4.v` 3/12 (n=76)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Monotone list (dieselbe wie PR_Loop4Mono)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang A1 (TM1: F1)
  - Simulation: waechst nach rechts (157 neue Zellen links, 2006 rechts), Rekorde dort meist in Zustand C, E; Band beim letzten Rekord (Schritt 2.825.262, Breite 2164): `... (011)^19 (101)^17 (110)^19 1^3 (011)^17 (101)^31 (110)^21 1^3 (011)^21 (101)^21 (110)^21 (101)^105 1 0 C> 0^inf`

### n=141 `1RB0LE_0RC---_1RD0LA_1RE0RA_1LC0LF_0RC1LC`

- slugbird: Status `rules`, simuliert 4.0e15 Schritte; busycoq: `open`, keine PR
- Spiegel-Zwillinge in Liste/decided: n=315 (Start A dort = Zustand E hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/Loop4Mono_v2.v` 5/12 (n=306); `verify/FARv1.v` 4/12 (n=462); `verify/Loop4Mono_v3.v` 4/12 (n=80); `verify/Loop4Mono_v5.v` 4/12 (n=177); `verify/Loop4Mono_v6.v` 4/12 (n=79); `verify/PR_Loop4Mono.v` 4/12 (n=652); `verify/Loop4Mono_v4.v` 3/12 (n=76)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Monotone list (dieselbe wie PR_Loop4Mono)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang B1 (TM1: F1)
  - Simulation: waechst nach rechts (71 neue Zellen links, 1906 rechts), Rekorde dort meist in Zustand D, E; Band beim letzten Rekord (Schritt 2.990.878, Breite 1978): `... 0 1^5 0 1 0 1^5 0 1 0 1^5 0 1 1 0 E> 0^inf`

### n=315 `1RB0RF_1LC0RD_1LA0LD_1LE0RA_0LB---_0LB1RB`

- slugbird: Status `rules`, simuliert 4.4e15 Schritte; busycoq: `open`, keine PR
- Spiegel-Zwillinge in Liste/decided: n=141 (Start A dort = Zustand D hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/Loop4Mono_v2.v` 5/12 (n=306); `verify/FARv1.v` 4/12 (n=462); `verify/Loop4Mono_v3.v` 4/12 (n=80); `verify/Loop4Mono_v5.v` 4/12 (n=177); `verify/Loop4Mono_v6.v` 4/12 (n=79); `verify/PR_Loop4Mono.v` 4/12 (n=652); `verify/Loop4Mono_v4.v` 3/12 (n=76)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Monotone list (dieselbe wie PR_Loop4Mono)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang E1 (TM1: F1)
  - Simulation: waechst nach links (2067 neue Zellen links, 27 rechts), Rekorde dort meist in Zustand C, A; Band beim letzten Rekord (Schritt 2.994.013, Breite 2095): `0^inf <A 0 1 1 0 1^5 0 1 0 1^5 0 1 0 1^5 0 ...`

### n=367 `1RB0LC_1LA0RD_0RB0LF_1RA1RE_1RC---_1LC0LB`

- slugbird: Status `rules`, simuliert 2.0e14 Schritte; busycoq: `open`, keine PR
- Spiegel-Zwillinge in Liste/decided: n=378 (Start A dort = Zustand B hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/FARv1.v` 4/12 (n=462); `verify/Loop4Mono_v2.v` 4/12 (n=306); `verify/Loop4Mono_v3.v` 4/12 (n=80); `verify/Loop4Mono_v5.v` 4/12 (n=177); `verify/Loop4Mono_v6.v` 4/12 (n=79); `verify/PR_Loop4Mono.v` 4/12 (n=652); `verify/Loop4Mono_v4.v` 3/12 (n=76)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Monotone list (dieselbe wie PR_Loop4Mono)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang E1 (TM1: F1)
  - Simulation: waechst nach rechts (155 neue Zellen links, 2017 rechts), Rekorde dort meist in Zustand B, D; Band beim letzten Rekord (Schritt 2.906.201, Breite 2173): `... (110)^19 1^3 (011)^19 (101)^19 (110)^19 1^3 (011)^23 (101)^21 (110)^21 1^3 (011)^21 (101)^21 (011)^111 0 B> 0^inf`

### n=378 `1RB0LC_1LA0RD_1LB1LF_0LA0RE_1RD0RA_1LD---`

- slugbird: Status `rules`, simuliert 2.0e14 Schritte; busycoq: `open`, keine PR
- Spiegel-Zwillinge in Liste/decided: n=114 (Start A dort = Zustand F hier); n=367 (Start A dort = Zustand B hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/FARv1.v` 4/12 (n=462); `verify/Loop4Mono_v2.v` 4/12 (n=306); `verify/Loop4Mono_v3.v` 4/12 (n=80); `verify/Loop4Mono_v5.v` 4/12 (n=177); `verify/Loop4Mono_v6.v` 4/12 (n=79); `verify/PR_Loop4Mono.v` 4/12 (n=652); `verify/Loop4Mono_v4.v` 3/12 (n=76)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Monotone list (dieselbe wie PR_Loop4Mono)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang F1 (TM1: F1)
  - Simulation: waechst nach links (1947 neue Zellen links, 156 rechts), Rekorde dort meist in Zustand A, C; Band beim letzten Rekord (Schritt 2.689.863, Breite 2104): `0^inf <A (011)^109 0 (101)^17 (110)^17 1^3 (011)^17 (101)^17 (110)^17 1^3 (011)^17 (101)^17 (110)^19 1^3 (011)^15 ...`

## Shift-overflow structural counter

Gemergte Beweisdateien dieser Klasse (decided, by=proof): 7 Dateien, 12 Maschinen.

Urteil = Haupttheorem der Datei fuer die Maschine selbst (exakt) oder ihr Spiegelbild mit
Start A (gespiegelt); `?` = in keiner dieser Formen gefunden.

| Datei (Pin) | Zeilen | Maschinen aus decided: n, Urteil laut Datei, Form in der Datei |
|---|---:|---|
| [`verify/PR_SOBL.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/PR_SOBL.v) | 2562 | n=47 `1RB0RC_1RC0LD_1LD1RA_1LF0LE_---0RD_1LB0LA` haelt, exakt |
| [`verify/SBCv10.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/SBCv10.v) | 1726 | n=49 `1RB0LE_0RC0RE_1LD1RA_0LA0RF_0RC0RD_1RB---` haelt nicht, exakt<br>n=1003 `1RB1LC_0RC0LF_1LD0RE_0LA0LE_0LA0LB_1LD---` haelt nicht, gespiegelt |
| [`verify/SBCv6a.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/SBCv6a.v) | 809 | n=376 `1RB1LE_0RC0LB_1LD0RA_0LA0LD_0LF0LA_1LD---` haelt nicht, gespiegelt<br>n=711 `1RB0RD_1RC0RC_0LA1RA_1LE0RC_0LF---_0LD1LC` haelt nicht, exakt<br>n=926 `1RB---_1RC0RE_0RD0RD_1LE0RB_0LF1RF_1RA0LD` haelt nicht, exakt |
| [`verify/SBCv6a2.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/SBCv6a2.v) | 1271 | n=1386 `1RB0RD_1RC1RF_0LA1RA_0RE0RC_1LE1LB_---0LE` haelt nicht, exakt |
| [`verify/SOBLv1.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/SOBLv1.v) | 1145 | n=441 `1RB0LC_1LA0LF_1LD---_1RE0RA_1RF0RE_1LB0RD` haelt, exakt<br>n=971 `1RB0RE_1RC1LC_1LD1RE_1LB0LC_0RF0RA_---1RC` haelt, exakt<br>n=1349 `1RB0RC_1LC0RD_1RA1LD_0LB1LE_1LB0LF_---0LB` haelt, gespiegelt |
| [`verify/SOBLv2.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/SOBLv2.v) | 823 | n=151 `1RB1RA_1RC1RC_1LD1RE_1RA0LC_0RB0RF_---0RC` haelt, exakt |
| [`verify/SOBLv3.v`](https://github.com/ccz181078/busycoq/blob/33209bc7dc282b38c8cd6be507bfc551fea56108/verify/SOBLv3.v) | 1085 | n=729 `1RB0LF_1LC0RE_0LA1RD_---1RE_1RC1RA_0RB1RF` haelt nicht, exakt |

### n=31 `1RB1LF_1LC1RB_1LF1LD_1LE0RD_1LB---_1LA0LA`

- slugbird: Status `rules`, simuliert 1.0e17 Schritte; busycoq: `open`, keine PR
- Aequivalente Maschinen laut holdouts.json: 1, busycoq erwaehnt sie in Eqv_v2.v
- Spiegel-Zwillinge in Liste/decided: n=222 (Start A dort = Zustand B hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/SBCv6a.v` 5/12 (n=926); `verify/SOBLv1.v` 5/12 (n=441); `verify/PR_SOBL.v` 4/12 (n=47); `verify/SBCv10.v` 4/12 (n=49); `verify/SOBLv2.v` 4/12 (n=151); `verify/SBCv6a2.v` 3/12 (n=1386); `verify/SOBLv3.v` 3/12 (n=729)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Shift-overflow structural counter (PR_Loop4Mono: Monotone list)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang E1 (TM1: F1)
  - Simulation: waechst nach links (2873 neue Zellen links, 50 rechts), Rekorde dort meist in Zustand A, F; Band beim letzten Rekord (Schritt 2.999.607, Breite 2924): `0^inf <A 0 1^8 (011101)^308 (01)^6 1^6 0 1^7 0 1^9 0 1 0 1^7 0 ...`

### n=222 `1RB1LA_1RC1RE_1RD0RD_1LA1RC_1RF0LE_1RA---`

- slugbird: Status `rules`, simuliert 1.0e17 Schritte; busycoq: `open`, keine PR
- Spiegel-Zwillinge in Liste/decided: n=31 (Start A dort = Zustand D hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/SBCv6a.v` 5/12 (n=926); `verify/SOBLv1.v` 5/12 (n=441); `verify/PR_SOBL.v` 4/12 (n=47); `verify/SBCv10.v` 4/12 (n=49); `verify/SOBLv2.v` 4/12 (n=151); `verify/SBCv6a2.v` 3/12 (n=1386); `verify/SOBLv3.v` 3/12 (n=729)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Shift-overflow structural counter (PR_Loop4Mono: Monotone list)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang F1 (TM1: F1)
  - Simulation: waechst nach rechts (59 neue Zellen links, 2802 rechts), Rekorde dort meist in Zustand D, C; Band beim letzten Rekord (Schritt 2.997.164, Breite 2862): `... 1^7 0 1^9 (01)^4 1^8 (01)^4 1^6 (01)^7 (110101)^319 1 1 0 1^8 0 D> 0^inf`

### n=274 `1RB0RE_1LC0RA_0LD1LB_1LA1LF_0LB0RD_0LB---`

- slugbird: Status `rules`, simuliert 1.0e17 Schritte; busycoq: `open`, keine PR
- Aequivalente Maschinen laut holdouts.json: 1, busycoq erwaehnt sie in Eqv_v2.v
- Spiegel-Zwillinge in Liste/decided: n=518 (Start A dort = Zustand B hier)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/SBCv6a.v` 5/12 (n=376); `verify/SBCv10.v` 4/12 (n=49); `verify/SBCv6a2.v` 4/12 (n=1386); `verify/SOBLv1.v` 4/12 (n=441); `verify/SOBLv2.v` 4/12 (n=151); `verify/PR_SOBL.v` 3/12 (n=47); `verify/SOBLv3.v` 3/12 (n=729)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Shift-overflow structural counter (PR_Loop4Mono: Monotone list)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang F1 (TM1: F1)
  - Simulation: waechst nach links (2903 neue Zellen links, 34 rechts), Rekorde dort meist in Zustand C, D; Band beim letzten Rekord (Schritt 2.995.189, Breite 2938): `0^inf <A 0 1 0 1^5 0 1 0 1^5 0 1 0 1^5 0 1 ...`

### n=318 `1RB---_0RC1RA_1RD1RF_1LE0LF_1RB0LD_0RE0LC`

- slugbird: Status `rules`, simuliert 1.0e20 Schritte; busycoq: `open`, keine PR
- Aequivalente Maschinen laut holdouts.json: 1, busycoq erwaehnt sie in Eqv_v2.v
- Spiegel-Zwillinge in Liste/decided: keine
- In der Simulation bandgleich mit n=518 (gleiche Rekordschritte und Baender)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/SBCv10.v` 5/12 (n=49); `verify/SBCv6a.v` 5/12 (n=376); `verify/SOBLv1.v` 5/12 (n=1349); `verify/PR_SOBL.v` 4/12 (n=47); `verify/SBCv6a2.v` 4/12 (n=1386); `verify/SOBLv2.v` 4/12 (n=151); `verify/SOBLv3.v` 3/12 (n=729)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Shift-overflow structural counter (PR_Loop4Mono: Monotone list)
  - Uebergangstabelle: Naehe zu TM1 5/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang A1 (TM1: F1)
  - Simulation: waechst nach rechts (32 neue Zellen links, 2827 rechts), Rekorde dort meist in Zustand B, C; Band beim letzten Rekord (Schritt 2.999.311, Breite 2860): `... 1 0 1^5 0 1 0 1^5 0 1 0 1^5 0 1 0 D> 0^inf`

### n=322 `1RB1RF_1LC0LF_1RD0LB_0RA1RE_1RD---_0RC0LA`

- slugbird: Status `rules`, simuliert 1.0e17 Schritte; busycoq: `open`, keine PR
- Aequivalente Maschinen laut holdouts.json: 1, busycoq erwaehnt sie in Eqv_v2.v
- Spiegel-Zwillinge in Liste/decided: keine
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/SBCv10.v` 5/12 (n=49); `verify/SBCv6a.v` 5/12 (n=376); `verify/SOBLv1.v` 5/12 (n=1349); `verify/PR_SOBL.v` 4/12 (n=47); `verify/SBCv6a2.v` 4/12 (n=1386); `verify/SOBLv2.v` 4/12 (n=151); `verify/SOBLv3.v` 3/12 (n=729)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Shift-overflow structural counter (PR_Loop4Mono: Monotone list)
  - Uebergangstabelle: Naehe zu TM1 5/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang E1 (TM1: F1)
  - Simulation: waechst nach rechts (32 neue Zellen links, 2905 rechts), Rekorde dort meist in Zustand B, D; Band beim letzten Rekord (Schritt 2.995.175, Breite 2938): `... 1 0 1^5 0 1 0 1^5 0 1 0 1^5 0 1 0 B> 0^inf`

### n=518 `1RB0LD_0RC1RA_1RD1RF_1LA0LE_0RA0LC_0RA---`

- slugbird: Status `rules`, simuliert 1.0e17 Schritte; busycoq: `open`, keine PR
- Spiegel-Zwillinge in Liste/decided: n=274 (Start A dort = Zustand D hier)
- In der Simulation bandgleich mit n=318 (gleiche Rekordschritte und Baender)
- Vorlagen (Naehe zur naechsten decided-Maschine der Datei): `verify/SBCv6a.v` 5/12 (n=376); `verify/SBCv10.v` 4/12 (n=49); `verify/SBCv6a2.v` 4/12 (n=1386); `verify/SOBLv1.v` 4/12 (n=441); `verify/SOBLv2.v` 4/12 (n=151); `verify/PR_SOBL.v` 3/12 (n=47); `verify/SOBLv3.v` 3/12 (n=729)
- Unterschied zu `PR_Loop4Mono.v`:
  - Klasse: Shift-overflow structural counter (PR_Loop4Mono: Monotone list)
  - Uebergangstabelle: Naehe zu TM1 4/12 (TM2 ist Zwilling von TM1, gleicher Wert); Halteuebergang F1 (TM1: F1)
  - Simulation: waechst nach rechts (32 neue Zellen links, 2827 rechts), Rekorde dort meist in Zustand B, C; Band beim letzten Rekord (Schritt 2.999.311, Breite 2860): `... 1 0 1^5 0 1 0 1^5 0 1 0 1^5 0 1 0 D> 0^inf`

