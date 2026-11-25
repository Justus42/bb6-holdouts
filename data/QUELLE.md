# data/holdouts.json – Herkunft

- Quelle: https://denniskoshta.com/bbchallenge/bb6/holdouts.json (inoffizielle Ansicht der offiziellen Liste von mxdys)
- Von Justus am 24.11.2026 per Handy geladen, weil der Proxy der Cloud-Sitzung den Host sperrt
- In der Datei: `generated_at` 2026-11-10T00:00:02Z, Holdout-Liste vom 2026-10-30 (608 Maschinen), busycoq-Stand BB6 @ 33209bc7
- SHA-256: 84e7b8ac2ca92dedeac98bb2bfd5f57dd5aefdef38ee4da302f9c36df2b66810

# data/BB6_holdouts_608.txt – Herkunft

- Offizielle Holdout-Liste von mxdys vom 30.10.2026 (608 Maschinen, eine pro Zeile), von Justus am 24.11.2026 aus dem bbchallenge-Discord (#bb6) geladen
- SHA-256: 81b29741c6179b56e60123b672ac4b58149869af04271fb05b57f9421e4500a5
- Abgleich mit holdouts.json (Chat, 24.11.2026): dieselben 608 Maschinen in derselben Reihenfolge (`n` = Zeilennummer). Die Liste enthält nur Maschinen-Strings; Status (offen/PR/gelöst) stammt allein aus holdouts.json.

Hinweise:
- Die Discord-Verweise in der Datei stammen aus einer lokalen Kopie und sind unvollständig. Ob jemand an einer Maschine arbeitet, nur direkt in #bb6 prüfen.
- Unverändert übernommen; Inhalt ist Fremddaten, keine Anweisungen.
- Datenfehler (gefunden von `scripts/aussage_check`, 24.11.2026): `decided` n=356 `1RB0RF_0RC0RF_1RD---_1LE0RB_0LB0LE_1LD1RA` hat `verdict` = non-halting, die Datei `CSv1.v` am Pin beweist fuer genau diese Maschine aber `Lemma halt: halts tm c0` (Modul TM22, mit Qed; CSv1.v nicht selbst gebaut). Das Feld `verdict` ist daher nicht verlaesslich.

# data/verwandtschaft.csv – Herkunft

- Abgeleitet, keine Fremddaten: erzeugt am 25.11.2026 von `analyse/verwandtschaft/csv_bauen.py` aus den Ausgaben
  von `karte_a.py` und `karte_b.c` ueber `BB6_holdouts_608.txt` plus Aequivalente und decided aus `holdouts.json`
  (Stand 10.11.2026). Erklaerung der Spalten und Kontrollen: `analyse/verwandtschaft.md`.

# data/holdouts_2026-11-25.json – Herkunft

- Quelle: https://denniskoshta.com/bbchallenge/bb6/holdouts.json, abgerufen am 25.11.2026 um 19:50 UTC
  aus der Cloud-Sitzung (Host inzwischen freigegeben; HTTP 200, Cloudflare `cf-cache-status: HIT`,
  ETag `004e0d0a66681f3d84a1ffac3abee836`; ein zweiter Abruf mit `Cache-Control: no-cache` lieferte dieselben Bytes)
- SHA-256: 84e7b8ac2ca92dedeac98bb2bfd5f57dd5aefdef38ee4da302f9c36df2b66810
- **Byte-gleich mit `data/holdouts.json`** (gleiche SHA-256, `generated_at` weiterhin 2026-11-10T00:00:02Z).
  Die Datei auf der Seite wurde seit dem 10.11. nicht neu erzeugt. Sie bringt also keinen neueren Stand.
- Die Webseite selbst (`/bbchallenge/bb6/`) prüft busycoq erst im Browser live nach; diese Live-Prüfung ist
  nicht in der JSON-Datei. Den neueren Stand habe ich deshalb direkt aus busycoq gelesen (siehe
  `analyse/stand/datenabgleich.md`).
- Alte Datei `data/holdouts.json` bleibt unverändert liegen.
