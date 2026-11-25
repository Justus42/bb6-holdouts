# bb6-holdouts

Ziel: Holdouts der offiziellen BB(6)-Liste (mxdys, 30.10.2026, 608 Maschinen) mit
maschinengeprüften Rocq/Coq-Beweisen entscheiden, einreichbar als PR an
[`ccz181078/busycoq`](https://github.com/ccz181078/busycoq) (Zweig BB6).

Bisher ist hier **kein eigener Beweis** geführt. Das Repo enthält den Prüfweg, die Datenlage und
Analysen. Früherer Name: `bb6-vortest`.

## Inhalt

| Pfad | Inhalt |
|---|---|
| `VORTEST.md` | Vortest vom 24.11.2026: Werkzeugkette, Laufzeiten, Negativkontrollen, Domains, Empfehlung |
| `CLAUDE.md` | Kurzfassung der Arbeitsregeln und Docker-Start für Claude-Sitzungen |
| `.github/workflows/pruefen.yml` | **Prüfweg für Beweise** (siehe unten) |
| `.github/workflows/laufzeit.yml`, `coq-check.yml` | Vortest-Workflows (Laufzeit, Nachbau von PR #32) |
| `scripts/aussage_check` | prüft vor dem Bau, welche Maschinen eine Beweisdatei behandelt und was die Haupttheoreme aussagen |
| `scripts/build_check.sh` | Bau mit `coqc -time` und strenger Auswertung von Print Assumptions |
| `scripts/auswertung_holdouts.py`, `scripts/vorlagen.py` | Auswertung der Holdout-Daten, Kandidaten, Vorlagen |
| `sim1_python/`, `sim2_rust/`, `scripts/vergleich_sim.py` | zwei unabhängig geschriebene TM-Simulatoren und ihr Abgleich |
| `data/` | Holdout-Liste und Schnappschuss `holdouts.json` (Herkunft und SHA-256: `data/QUELLE.md`), Auswertung, Kandidaten, Vorlagen |

## Daten

`data/holdouts.json` ist vom 10.11.2026. Neuere Beweise (z. B. noch nicht gemergte) fehlen darin. Neu geholt am 25.11.2026: unverändert (`data/holdouts_2026-11-25.json`); Abgleich mit busycoq in
`analyse/stand/datenabgleich.md`. Gesamtstand: `STATUS.md` (englisch `STATUS.en.md`).
Der Status einer Maschine ist deshalb nie als aktuell anzusehen.

## Prüfweg

Workflow **pruefen**, nur manuell (Actions → pruefen → Run workflow):

- `datei`: Pfad im Repo oder `pin:<Pfad>` für eine Datei aus busycoq am Pin
- `maschine`: erwartete Maschinen-Strings (6×2, Halt als `---`), durch Komma getrennt

Ablauf:

1. `aussage_check` vor dem Bau (Maschinen, Haupttheoreme, Liste bzw. `decided`).
2. Bau derselben Datei (SHA-256 geprüft) im **nativen** und im **VM**-Image.
3. Print Assumptions streng: jedes Haupttheorem muss exakt `Closed under the global context`
   ergeben; danach Kern-Abgleich der Aussagen.

Bestanden nur, wenn beide Bau-Jobs grün sind.

## Versionen

| Komponente | Pin |
|---|---|
| busycoq | Zweig BB6, `33209bc7dc282b38c8cd6be507bfc551fea56108` |
| Coq 8.20.1 (VM) | `coqorg/coq:8.20.1@sha256:3675f124508d7bbfcd509000d5d67e76ed66c1945ccb1f455ce57c6e5d6d52a1` |
| Coq 8.20.1 (nativ) | `coqorg/coq:8.20.1-native@sha256:89d0f19002641db9a9a090a2f22bc7e19288e24827be5d2c8bc2a0be39d5e5dd` |
| GitHub Actions | `checkout` v7.0.1, `upload-artifact` v7.0.2, `download-artifact` v8.0.2, jeweils per Commit-SHA (Node 24) |
