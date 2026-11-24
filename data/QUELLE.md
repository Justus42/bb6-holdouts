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
