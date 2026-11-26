# analyse/lueckenkarte/

Belege zum Bericht `analyse/lueckenkarte.md` (26.11.2026).

- `guide_auszug.tsv`: Notizen aus slugbirds Holdout-Guide (Stand 3.11., laut Fusszeile von KI-Agenten geschrieben),
  wortgleich aus der Datentabelle im Seitencode ausgelesen: unsere 7 Maschinen, die Klassengeschwister und die
  Familien, die an einer fehlenden Aussage haengen. Fremddaten, nicht geprueft.
- `quick_sim/*.txt`: gekuerzte Ausgaben von Quick_Sim.py (github.com/sligocki/busy-beaver, Kopf 4359559, unveraendert),
  je 150 s: `318`, `322` (Blockgroesse selbst gewaehlt = 2), `318n8`, `322n8` (`-n 8`). Aufruf:
  `timeout 150 python3 Code/Quick_Sim.py --rules [-n 8] <Maschine>`. Je Datei: Blockfinder-Ergebnis und letzter
  Zwischenstand (Zeilen auf 400 Zeichen gekuerzt).
