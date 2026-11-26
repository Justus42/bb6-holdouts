# VORTEST – BB(6)-Pipeline in Claude-Code-Cloud-Sitzung

Stand: 24.11.2026. Ziel war zu klären, ob in dieser Umgebung Rocq/Coq-Beweise für BB(6)-Holdouts
geprüft werden können. Es wurde **kein neuer Beweis** geführt, und in fremden Repos wurde nichts
angelegt (keine Issues, PRs oder Kommentare).

## Ergebnis in Kürze

| Frage | Antwort |
|---|---|
| Coq 8.20 lauffähig? | **Ja**, auf zwei Wegen: lokal per Docker und in GitHub Actions, mit demselben offiziellen Image per Digest |
| Gemergter Beweis aus PR #32 prüfbar? | **Ja.** Print Assumptions ergibt für beide Theoreme exakt `Closed under the global context`. Bauzeit 20–26 min mit VM, **7 min nativ** |
| Laufzeit-Widerspruch zum PR-Text | geklärt: die 2,5 min gelten nur für die erste PR-Fassung ohne `halt_C` |
| Negativkontrolle a (Übergang geändert) | erkannt: `coqc` bricht nach 1 s ab |
| Negativkontrolle b (`Admitted`) | erkannt: `coqc` läuft durch, Print Assumptions zeigt das Axiom |
| coqchk | **nicht geprüft.** VM-Image: nach dem 20-min-Limit abgebrochen. Natives Image: übersprungen, weil der Bau 427 s dauerte (Regel: nur unter 5 min) |
| BB(5)-Champion, zwei Simulatoren | beide 47.176.870 Schritte und 4.098 Einsen, 0 Abweichungen auf 70 Varianten |
| Datenlage | 608 Holdouts; die JSON stimmt mit der offiziellen Liste überein (Menge und Reihenfolge); 75 Kandidaten |
| **Empfehlung** | **weiter** (Begründung am Ende) |

## Versionen und Pins

| Komponente | Version / Pin |
|---|---|
| Coq (VM) | `coqorg/coq:8.20.1@sha256:3675f124508d7bbfcd509000d5d67e76ed66c1945ccb1f455ce57c6e5d6d52a1` (= Tag `8.20`), Coq 8.20.1, OCaml 4.13.1+flambda, Native-Compiler **aus** |
| Coq (nativ) | `coqorg/coq:8.20.1-native@sha256:89d0f19002641db9a9a090a2f22bc7e19288e24827be5d2c8bc2a0be39d5e5dd` (= Tag `8.20-native`), OCaml 4.13.1, Native-Compiler **an** |
| busycoq | `ccz181078/busycoq`, Zweig BB6, Pin `33209bc7dc282b38c8cd6be507bfc551fea56108` (03.11.2026); seit 26.11.2026 Pin `9c078caa3443e8027f5d2704e26c7228c1c86aa8` (nur neue `verify/M_*.v`-Dateien, Kern unverändert) |
| Daten | `data/holdouts.json` (SHA-256 `84e7b8ac…6810`), `data/BB6_holdouts_608.txt` (SHA-256 `81b29741…00a5`) |
| BB(5)-Quellen | `bbchallenge/bbchallenge-paper` @ `c563cb33`; `ccz181078/Coq-BB5` @ `9142e219` |
| Werkzeuge | Docker 29.9.3 (Client und Daemon), Python 3.13.18, Rust 1.97.0 |

Die Image-Digests wurden über die Docker-Registry-API ermittelt, nicht geraten.

## Block 1 – Werkzeugkette

- **apt:** bietet nur Coq 8.18.0, nicht verwendet.
- **opam:** `opam.ocaml.org` sperrt der Proxy (403).
- **GitHub-Releases (Web):** gesperrt (403). git über HTTPS funktioniert.
- **Gewählter Weg A:** lokaler Docker-Daemon, der installiert ist, aber nicht von selbst läuft (`dockerd` von Hand starten), plus offizielles Image. Coq lief nach **98 s**, davon 60 s Pull (6,3 GB).
- **Weg B:** GitHub Actions mit dem Image per Digest. Der erste Lauf scheiterte mit `coqc: not found`, weil Actions den Entrypoint `opam exec --` umgeht. Lösung: den opam-Switch in `$GITHUB_PATH` eintragen. Danach grün, etwa 45 s.
- **Actions-Ergebnisse** (Status, Jobs, vollständige Logs) kann ich selbst lesen, aber erst nach Job-Ende.
- **Wichtig:** Zwischen den Blöcken wird die VM neu gestartet. Dateien und Images bleiben erhalten, Prozesse nicht, also muss `dockerd` jedes Mal neu gestartet werden. Abhilfe: Hook-Vorschlag unten.

## Block 2 – gemergter Beweis aus PR #32

- **Datei:** Der Pfad `verify/1RB1LE_0RC0LC_1LD0RA_0LA0LF_0LC0LE_0LD---.v` existiert in `33209bc7` **nicht**.
  - Der PR-Autor hat sie im PR selbst umbenannt (`57c9956`, `M_…HHH.v`, mit Spiegel-Zwilling) und den alten Namen gelöscht (`427fd6d`).
  - Nach dem Merge (`65d937f`) hat der Maintainer daraus `verify/PR_Loop4Mono.v` gemacht (`5812872`). Inhaltlich ist nur der Code in `Module TM1`/`TM2` eingepackt; `halt_twin` heißt jetzt `TM2.halt`.
  - Geprüft wurde `PR_Loop4Mono.v` aus dem Pin, byte-gleich nach `M284.v` kopiert, mit `coqc -Q . BusyCoq M284.v`.
- **Abhängigkeiten:** 17 Module, etwa 13.200 Zeilen (zusammen mit M284 etwa 14.900). Bauzeit 22 s lokal, 9 s Actions.
- **Ergebnis:**

  | | lokal (4 Kerne) | Actions (Nachbau aus frischem Checkout) |
  |---|---:|---:|
  | `M284.v` (VM) | 1403 s | 1175 s |
  | Print Assumptions `TM1.halt`, `TM2.halt` | exakt `Closed under the global context` | ebenso |

  Actions ist **keine unabhängige Prüfung**: gleiches Image, gleicher Kern. Es ist ein sauberer Nachbau aus frischem Checkout.
- **Negativkontrolle a:** A0 `1RB`→`0RB`. `coqc` scheitert nach 1 s in Zeile 46 (`skipR`).
- **Negativkontrolle b:** Beweis von `check_spec` durch `Admitted.` ersetzt. `coqc` läuft durch (exit 0, 1392 s). Print Assumptions listet bei beiden Theoremen `M284b.TM1.check_spec`, die strenge Auswertung ergibt FAIL. Die Lücke wird also erkannt.
- **coqchk -o (VM-Image):** nach **1200 s abgebrochen** (exit 124).
  - In etwa 10 min waren Stdlib, alle Abhängigkeiten und M284 bis vor `TM1.halt` geprüft.
  - In `TM1.halt` steckte coqchk dann über 10 min, obwohl coqc dafür etwa 2:45 min braucht. Auch coqchk prüft den Cast laut Warnung per VM.
  - Kontrolle b mit coqchk entfiel deshalb.

## Block 2c – Laufzeit geklärt

- **Frage:** Der PR-Text nennt etwa 2,5 min ohne native; bei uns waren es 23 min, davon gut 16 min in `halt_C`.
- **Befund aus der Git-Historie:** `halt_C` kam **nicht beim Merge** dazu.
  - Der erste PR-Commit `1e45f1b` enthält nur `halt`. Sein Kommentar sagt: „1307718 ticks; about 2.5 minutes where native_compute falls back to vm_compute“.
  - Der zweite PR-Commit `57c9956`, ebenfalls vom PR-Autor, ergänzt `halt_C` (3.121.228 Ticks, „2.4 times as many“) für den Spiegel-Zwilling.
  - Die 2,5 min beziehen sich also nur auf `halt`.
  - Die Abhängigkeiten sind zwischen `57c9956` und dem Pin unverändert.
- **Messungen** (`coqc -time`, Zeit pro Satz):

  | Fassung | Image | wo | Bauzeit | langsamster Satz | Print Assumptions |
  |---|---|---|---:|---|---|
  | `1e45f1b` (nur `halt`) | VM | lokal | 164 s | `Qed` von `halt`: 154 s | `halt` OK |
  | `1e45f1b` | VM | Actions | 152 s | `Qed` von `halt`: 145 s | `halt` OK |
  | `57c9956` (PR-Endfassung) | VM | Actions | 1580 s | `Qed` von `halt_C`: 1352 s; `halt`: 187 s; `init_C` (`execute`): 32 s | `halt`, `halt_C`, `halt_twin` OK |
  | `PR_Loop4Mono.v` = M284 | **nativ** | Actions | **427 s** | `Qed` von `halt_C`: 344 s; `halt`: 42 s; `init_C`: 32 s | `TM1.halt`, `TM2.halt` OK |

  Zum Vergleich aus Block 2: M284 mit VM brauchte 1403 s lokal und 1175 s in Actions.

- **Bewertung:**
  - Die 2,5 min aus dem PR stimmen für `1e45f1b`: gemessen 152–164 s.
  - Die gemergte Fassung ist langsamer, weil `halt_C` dazukommt. Das liegt **nicht** an unserer Umgebung.
  - Der Kommentar „2.4 times as many“ bezieht sich auf die Zahl der Ticks. In Zeit kostet `halt_C` etwa 7–8-mal so viel wie `halt` (VM 1352/187, nativ 344/42), vermutlich weil ein Tick bei größeren Zahlen bzw. längeren Listen teurer wird.
  - Natives Image: im selben Workflow-Lauf etwa 3,7-mal schneller als die PR-Endfassung mit VM (427 s gegenüber 1580 s) (`halt` ~3,5–4,5×, `halt_C` ~3,9×). Das `execute` in `init_C` (32 s) beschleunigt es nicht, weil es kein nativer Cast ist.
  - Die Actions-Runner streuen deutlich: dieselbe Arbeit (M284 bzw. `57c9956`, VM) dauerte einmal 1175 s, einmal 1580 s; `halt` allein 145 s bzw. 187 s. Einzelmessungen sind daher etwa ±30 % unsicher.
- **coqchk nativ:** nicht ausgeführt. M284 baut nativ in 427 s, also über der Vorgabe „nur unter 5 min“. Damit entfiel auch Kontrolle b mit coqchk; der Workflow hat beide Schritte regelgerecht übersprungen.
- **Werkzeuge:** `scripts/build_check.sh` (Bau mit `coqc -time` und strenger Print-Assumptions-Prüfung, optional coqchk) und `.github/workflows/laufzeit.yml` (drei Jobs, Images per Digest). Run `45502581287`.

## Block 2b – Datenlage

- **Kein Netzabruf.** `denniskoshta.com` ist gesperrt (403); die Dateien kamen per `git fetch` von main. Beide SHA-256 stimmen mit `data/QUELLE.md` überein.
- **Abgleich** `holdouts.json` ↔ `BB6_holdouts_608.txt`:
  - dieselbe Menge (608/608, keine Duplikate)
  - dieselbe Reihenfolge (`n` = Zeilennummer, 1..608 lückenlos)
  - alle Zeilen im gültigen 6×2-Format
  - keine Abweichungen
- **busycoq.head.sha** = `33209bc7…`, passt zum Pin.
- **busycoq-Status:**

  | Status | Anzahl |
  |---|---:|
  | open | 569 |
  | pr_open | 38 |
  | solved | 1 |

  Abweichung in der Datei: `counts.by_status` meldet `open 562 + sim_halt 7`. Die 7 „Energy vampire“ stehen in den Einträgen als `open`.
- **Tabelle je Klasse** (27 Klassen) mit Beweisen aus `decided` (`by=proof`): siehe `data/auswertung_holdouts.md`.
  - Von 819 Beweisen in `decided` haben 229 keine Klasse.
  - 11 Klassennamen in `decided` kommen bei den Holdouts nicht vor.
  - Die Zahl „Beweise je Klasse“ ist daher eine **Untergrenze**.
- **Kandidaten:** `data/kandidaten.csv`, **75 Maschinen**.

  | Filterstufe | verbleibend |
  |---|---:|
  | busycoq open | 569 |
  | ohne jede PR | 556 |
  | slugbird `rules` | 91 |
  | ohne Tags | 90 |
  | Klasse mit ≥5 Beweisen in `decided` | 75 |

  Nach Klassen:
  - Shift-overflow counter: 37
  - Quadratic Mess: 11
  - Bell-like: 10
  - Shift-overflow structural counter: 6
  - Monotone list: 5
  - Structural counter + chaotic edge: 4
  - je 1 in Shift-overflow bouncer counter und Skelet 1-like Class 1

  „Ohne PR“ ist streng ausgelegt: Auch nur erwähnende oder geschlossene PRs schließen aus.
- **Discord-Angaben** wurden nicht verwendet, weil sie unvollständig sind. Ob jemand an einer Maschine arbeitet, muss direkt in #bb6 geprüft werden. (Ersetzt am 26.11.2026: stattdessen busycoq und busy-beaver-explorer per git prüfen, siehe CLAUDE.md.)
- Das ist **nur eine Auswertung**; es wird nichts beansprucht.

## Block 3 – zwei unabhängige Simulatoren (BB(5))

- **Wiki gesperrt:** `wiki.bbchallenge.org` (und `bbchallenge.org`) sperrt der Proxy. Die Gegenprüfung lief deshalb über die bbchallenge-Quellen auf GitHub:
  - Paper `bbchallenge-paper.tex`, Zeile 770: `1RB1LC_1RC1RB_1RD0LE_1LA1LD_1RZ0LA`, S(5) = 47.176.870, Σ(5) = 4.098
  - Coq-BB5: `BB5_champion` ist dieselbe Maschine, `BB5 := 47176870`
- **Simulatoren:**

  | | sim1 | sim2 |
  |---|---|---|
  | Sprache | Python (`sim1_python/sim1.py`) | Rust, nur std (`sim2_rust/`) |
  | Bandmodell | dichtes `bytearray`, verdoppelt sich, Kopf als Index | zwei Stacks plus Kopfzelle |
  | Autor | Hauptsitzung | eigener Agent, nur aus der Spezifikation, ohne Sicht auf sim1 |
  | Champion | 47.176.870 / 4.098 in 4,6 s | 47.176.870 / 4.098 in 0,19 s |

  Die Zählweise (Halte-Übergang zählt als Schritt, `---` = `1RZ`) war für beide gleich vorgegeben.
- **Negativkontrolle:** D1 `1LD`→`1LB`. Beide liefern 54 Schritte und 6 Einsen.
- **Zusatz:** alle 70 Ein-Feld-Varianten, Limit 10⁶. 29 halten, 0 Abweichungen (`scripts/vergleich_sim.py`, 11 s).
- **Hinweis:** Eine Änderung nur am Halte-Übergang ändert die Schrittzahl nicht. Eine Negativkontrolle muss deshalb einen Übergang ändern, der nicht hält.

## Probleme und Abweichungen (gesammelt)

1. Die vorgegebene Datei aus PR #32 liegt im Pin nur umbenannt vor (`PR_Loop4Mono.v`), siehe Block 2.
2. Die „2,5 min“ aus dem PR gelten nur für `halt`, nicht für die gemergte Fassung mit `halt_C`, siehe Block 2c.
3. coqchk ist mit dem VM-Image für diesen Beweis zu langsam.
4. Die VM-Neustarts beenden `dockerd`.
5. Im Image fehlt `bc`; die Zeitmessung im Skript ist auf Ganzzahlen umgestellt.
6. Ein eigener Skriptfehler (SIGPIPE unter `pipefail` in `build_check.sh`) hat den ersten Laufzeit-Run unbrauchbar gemacht. Er ist behoben (`8d0c54f`).
7. Frühe Pushes haben ungewollt jeweils einen 20-min-`coq-check`-Lauf ausgelöst. Seit `a56b83e` laufen die Workflows nur noch bei Änderungen an ihren eigenen Dateien.
8. Gesperrte Hosts: siehe Domain-Liste.

## Vorschlag (nicht umgesetzt): Setup-Skript für eine Umgebung „Mathe“

Das Skript lädt beide Coq-Images per Digest vor. `dockerd` läuft nur während des Skripts. Getestet
habe ich es in diesem Container, nachdem ich beide Images gelöscht und `dockerd` gestoppt hatte:
**109 s**, danach läuft kein Daemon mehr. In einer frisch gebauten Umgebung ist es **nicht** getestet.
Offen ist dort, ob das Setup-Skript dieselbe Proxy- und CA-Konfiguration sieht wie die Sitzung.

```bash
#!/bin/bash
# Umgebung "Mathe": Coq-Images per Digest vorab ziehen. dockerd nur fuer die Dauer des Skripts.
set -euo pipefail
VM=coqorg/coq@sha256:3675f124508d7bbfcd509000d5d67e76ed66c1945ccb1f455ce57c6e5d6d52a1      # 8.20.1
NATIVE=coqorg/coq@sha256:89d0f19002641db9a9a090a2f22bc7e19288e24827be5d2c8bc2a0be39d5e5dd  # 8.20.1-native
command -v dockerd >/dev/null || { echo "dockerd fehlt im Image" >&2; exit 1; }
started=0
if ! docker info >/dev/null 2>&1; then
  dockerd >/var/log/dockerd-setup.log 2>&1 &
  pid=$!; started=1
  for _ in $(seq 1 60); do docker info >/dev/null 2>&1 && break; sleep 1; done
  docker info >/dev/null 2>&1 || { echo "dockerd startet nicht" >&2; exit 1; }
fi
docker pull -q "$VM" && docker tag "$VM" coqorg/coq:8.20.1
docker pull -q "$NATIVE" && docker tag "$NATIVE" coqorg/coq:8.20.1-native
docker images --digests coqorg/coq
if [ "$started" = 1 ]; then kill "$pid"; wait "$pid" || true; fi
```

## Vorschlag (nicht umgesetzt): SessionStart-Hook, der `dockerd` startet

Der Cache der Umgebung hält Dateien, also auch die Images, aber keine Prozesse. Der Hook startet
deshalb nur `dockerd` und zieht keine Images. Er ist synchron und dauert etwa 1 s.

Getestet:
- `dockerd` aus: Start in 1 s, der Daemon überlebt das Hook-Ende (`setsid`).
- `dockerd` an: No-op.
- außerhalb der Cloud: No-op.

`.claude/hooks/session-start.sh`:

```bash
#!/bin/bash
# dockerd starten, falls er nicht laeuft. Zieht keine Images.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
docker info >/dev/null 2>&1 && exit 0
command -v dockerd >/dev/null || { echo "session-start: dockerd fehlt" >&2; exit 0; }
setsid nohup dockerd >/tmp/dockerd.log 2>&1 < /dev/null &
for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && exit 0; sleep 1; done
echo "session-start: dockerd nach 30 s nicht bereit, siehe /tmp/dockerd.log" >&2
exit 0
```

`.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command", "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh" } ] }
    ]
  }
}
```

## Domains

**In Block 1–3 gesperrt und wirklich gebraucht:**

| Domain | Wofür | Begründung |
|---|---|---|
| `denniskoshta.com` | aktuelle `holdouts.json` (Status, Klassen, `decided`, PR-Zuordnung) | einzige maschinenlesbare Quelle für diese Zusammenführung; ohne sie muss jemand jeden Snapshot von Hand liefern, wie am 24.11. |
| `wiki.bbchallenge.org` | Sollwerte und Klassenbeschreibungen; Holdout-Listen-Historie (`base_list.file` liegt dort) | die verlangte Gegenprüfung im Wiki war nicht möglich; Ersatz über Paper und Coq-BB5 |
| `bbchallenge.org` | offizielle Liste `BB6_holdouts_608.txt` (`list.file`) | ersetzt den manuellen Discord-Download der offiziellen Liste |

**Gesperrt, aber nicht gebraucht:**
- `opam.ocaml.org`: Coq kommt über das Docker-Image.
- `github.com` per Web (Releases): git über HTTPS funktioniert.
- `discuss.bbchallenge.org`: wurde nur einmal auf Erreichbarkeit geprüft und für keinen Block gebraucht.

**Erreichbar und für das Setup nötig:**
- `registry-1.docker.io`, `auth.docker.io` und die Docker-Download-CDN: Image-Pulls.
- `hub.docker.com`: Tag-Prüfung.
- `github.com` (git): busycoq, Paper, Coq-BB5.

In einer neuen Umgebung „Mathe“ mit eingeschränktem Netz müssen diese ebenfalls erlaubt sein. Hier
liefen sie ohne eigenen Eintrag. Ob das an „Paketmanager erlauben“ hängt, wurde nicht geprüft.

## Empfehlung

**Weiter.** Keines der Abbruchkriterien ist eingetreten:
- Coq 8.20 läuft auf beiden Wegen.
- Der Beweis aus PR #32 ist prüfbar (gemergte Fassung aus dem Pin, Print Assumptions streng OK).
- Kontrolle b wird von Print Assumptions erkannt.

Bedingungen für die nächste Phase:
1. **Prüfungen über das native Image in Actions.** M284 baut dort in etwa 7 statt 20–26 min. Lokal nur kurze Läufe; der Grundsatz „über 10 min nach Actions“ hat sich bewährt.
2. **Print Assumptions (streng) ist das maßgebliche Kriterium.**
   - coqchk ist für Beweise mit großen VM- oder nativen Casts in dieser Form zu langsam: VM-Image über 20 min allein in `TM1.halt`.
   - Ob coqchk mit dem nativen Image oder mit mehr Zeit durchläuft, ist **offen**. Das wäre ein eigener Actions-Lauf ohne das 5-min-Kriterium und mit einem großzügigen Limit, z. B. 60 min (nur Vorschlag).
3. **Umgebung:** Das Setup-Skript und der SessionStart-Hook oben würden die manuellen `dockerd`-Starts und Pulls ersetzen. Ohne die drei Domains muss weiterhin jemand Datenstände von Hand liefern.
4. **Kandidaten:** Die 75 Einträge in `data/kandidaten.csv` sind nur eine Auswertung. Vor jeder Arbeit an einer Maschine sind busycoq (BB6 und offene PRs) und busy-beaver-explorer per git zu prüfen (Regel seit 26.11.2026, CLAUDE.md; vorher: in #bb6 fragen); die Discord-Daten in der Datei taugen dafür nicht.
