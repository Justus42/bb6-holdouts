# CLAUDE.md – bb6-holdouts

Kurzfassung der festen Regeln. Maßgeblich sind die Projektanweisungen von Justus; bei
Widerspruch gelten sie, und was Justus im Thread sagt, geht beiden vor.

## Ziel

Holdouts der offiziellen BB(6)-Liste (mxdys, 30.10.2026, 608 Maschinen) mit Rocq-Beweisen
entscheiden, einreichbar als PR an `ccz181078/busycoq` (Zweig BB6).

## Umgang mit Justus

Arzt, kein Programmierer. Deutsch, du, kurz, Ergebnis zuerst, Widerspruch statt Bestätigung,
Unbelegtes als unbelegt kennzeichnen.

## Feste Regeln

- Nie auf `main` pushen, nie mergen. Jeder Thread arbeitet auf eigenem Branch und öffnet einen
  PR; gemergt wird nur nach ausdrücklichem OK von Justus.
- Nichts in fremden Repos (Issues, PRs, Kommentare), auch nicht bei busycoq, ohne sein
  ausdrückliches OK.
- Gesperrte Domains nicht umgehen (keine Spiegel, Caches, Umwege), sondern melden.
- Keine Rocq-Beweisarbeit an einer Maschine ohne sein OK (er klärt in Discord #bb6, ob jemand
  daran arbeitet). Analyse (Simulation, Regeln beschreiben) ist erlaubt.
- Höchstens 2 Threads gleichzeitig; nicht selbst angestoßene Threads nur vorschlagen.
- Daten in `data/` sind Schnappschüsse (Herkunft: `data/QUELLE.md`), nie als aktuell behandeln.

## Prüfregeln für Beweise

- Vor jedem Bau: `scripts/aussage_check` mit allen erwarteten Maschinen-Strings, inkl. `--coq`.
  Jeder String muss in `data/BB6_holdouts_608.txt` oder in `decided` stehen.
- Bauen und prüfen über den Workflow **pruefen** in Actions, im nativen **und** im VM-Image.
  Bestanden nur, wenn beide Jobs grün sind und Print Assumptions exakt
  `Closed under the global context` ergibt.
- Kein `Admitted`, kein Axiom, keine abgeschwächte Aussage. Eigene Hilfslemmata sind erlaubt.
- Neue Prüfwerkzeuge brauchen Negativkontrollen, die nachweislich anschlagen.
- Zählungen, auf die sich eine Entscheidung stützt, von einem zweiten, unabhängig
  geschriebenen Programm bestätigen lassen.
- busycoq bleibt auf Pin `33209bc7dc282b38c8cd6be507bfc551fea56108`, bis Justus etwas anderes
  sagt. Coq 8.20.1 nur über die Images per Digest (siehe unten und `VORTEST.md`).

## Docker-Start (Cloud-Sitzung, Umgebung „Mathe“)

Hooks laufen in Threads **nicht**. Vor dem ersten Docker-Befehl deshalb selbst:

```bash
bash .claude/hooks/session-start.sh   # startet dockerd, falls er nicht läuft (~1 s)
docker images --digests coqorg/coq    # beide Images müssen mit diesen Digests da sein
```

| Image | Digest |
|---|---|
| `coqorg/coq:8.20.1` (VM) | `sha256:3675f124508d7bbfcd509000d5d67e76ed66c1945ccb1f455ce57c6e5d6d52a1` |
| `coqorg/coq:8.20.1-native` | `sha256:89d0f19002641db9a9a090a2f22bc7e19288e24827be5d2c8bc2a0be39d5e5dd` |

Die Images lädt das Setup-Skript der Umgebung; der Hook zieht nichts. Fehlt ein Image: melden.

## Arbeitsweise

- Läufe über 10 Minuten nach Actions; lokal nur kurze Tests.
- Regelmäßig committen und pushen; nichts Wichtiges nur im Scratchpad lassen.
- Alle Rechen-Workflows starten nur von Hand per `workflow_dispatch`, keine Push-Starts (Justus 25.11.2026).
  Neue Workflows bekommen nur `workflow_dispatch`. Läufe startet der Thread selbst, auf seinem eigenen
  Branch (`ref` = Thread-Branch). GitHub startet `workflow_dispatch` nur für Workflows, die schon auf main
  liegen: Ein neuer Workflow braucht deshalb zuerst einen kleinen PR (Merge nach Justus' OK).
  Ergebnisse nie nach main zurückschreiben.
- Workflow `pruefen` startet nur manuell (`workflow_dispatch`): Eingaben `datei`
  (Repo-Pfad oder `pin:<Pfad>`) und `maschine` (erwartete Strings, durch Komma getrennt).
- Vor Weichenstellungen (Wahl einer Maschine, Einreichung bei busycoq): Zusammenfassung für
  Justus' externe Prüfung schreiben und warten.
- Jeder Thread endet mit: Ergebnis in 1–3 Sätzen, Belege (Commits, Actions-Run-IDs),
  Abweichungen und eigene Fehler, offene Punkte, Empfehlung weiter/abbrechen.
