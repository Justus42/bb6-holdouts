# extern/ – Prüfprogramme der externen Prüfstelle

Diese Programme stammen nicht aus den Projekt-Threads. Sie wurden im begleitenden Prüf-Chat (24.–26.11.2026) unabhängig geschrieben, um Kernaussagen der Threads gegenzurechnen. Sie sind klein, nur Python-Standardbibliothek, und werden vom Projekt nicht aufgerufen.

Aufruf jeweils aus dem Repo-Wurzelverzeichnis.

| Programm | Prüft | Aufruf | Ergebnis im Prüf-Chat |
|---|---|---|---|
| `abgleich.py` | offizielle Liste gegen `holdouts.json`: gleiche Menge, gleiche Reihenfolge | `python3 extern/abgleich.py data/holdouts.json data/BB6_holdouts_608.txt` | 608 von 608 gleich |
| `analyse.py` | Zählung je Klasse (offen, PR, gelöst, Beweise in `decided`) | `python3 extern/analyse.py data/holdouts.json` | Grundlage der Kandidatenwahl |
| `kandidaten.py` | Kandidatenfilter (offen ohne PR, Regeln bekannt, ohne Tags, Klasse mit mind. 5 Beweisen) | `python3 extern/kandidaten.py data/holdouts.json` | 75 Kandidaten |
| `zwillinge.py` | Verwandtschaft unter den Kandidaten (gleiche Tabelle bis auf Umbenennung/Spiegelung); Vergleich 318/518 | `python3 extern/zwillinge.py data/kandidaten.csv` | fünf Gruppen; 318/518 keine gleiche Tabelle |
| `reduktion.py` | Rückführung auf eine 5-Zustands-Maschine durch Zusammenlegen zweier Zustände | `python3 extern/reduktion.py data/BB6_holdouts_608.txt 274 318 322 518` | alle vier dieselbe Normalform; 88 und 312 gleich, 396 und 449 weichen ab |
| `muster114.py` | Vorgänger des Halts bei Tabelle 114; Gegenbeispiel zur lokalen Fassung des Muster-Satzes | `python3 extern/muster114.py` | Halt nach 6 Schritten ohne das Muster, wenn rechts schon `111` liegt |
| `gesetz396.py` | Besuchsgesetz von 396 gegen direkte Simulation, alle Wörter bis Länge L; Negativkontrolle | `python3 extern/gesetz396.py 15` | 32.768 Wörter, keine Abweichung; Negativkontrolle schlägt an |
| `runde396.py` | Rundenform ab leerem Band gegen das Wortsystem; Vergleich mit 88 | `python3 extern/runde396.py 20000000` | 35 Runden wortgleich |
| `entsteh111.py` | Wie entsteht ein neues `111` im Wortsystem von 396 (alle Wörter bis Länge 14) | `python3 extern/entsteh111.py` | nur wenn ein Besuch auf einer 0 direkt vor `11` endet (782 Fälle) |
| `fam_check.py` | Ob 123, 223, 471 dasselbe Besuchsgesetz erfüllen | `python3 extern/fam_check.py` | nur teilweise (512/740, 512/740, 607/740); 396 und 110 voll |
| `dm_abgleich.py` | Welche Maschinen stehen im Klon von google-deepmind/cryptids | `python3 extern/dm_abgleich.py <cryptids>/BusyBeaver data/BB6_holdouts_608.txt` | 118 Maschinen der Liste, keiner der damaligen Kandidaten |

Hinweise:
- `runde396.py` und `fam_check.py` laden `gesetz396.py` aus demselben Ordner.
- Die Zahlen in der letzten Spalte gelten für den Datenstand vom 10.11.2026 (`holdouts.json`) bzw. die Liste vom 30.10.2026.
- `reduktion.py` und `muster114.py` wurden für diese Ablage neu aufgeschrieben; die ursprünglichen Rechnungen liefen als Einzeiler und kamen zum selben Ergebnis.
- Nicht abgelegt, weil nur von Hand geführt: die Herleitung des Muster-Satzes für Tabelle 114 und die Durchsicht der Rocq-Dateien.
