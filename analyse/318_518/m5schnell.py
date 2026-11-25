#!/usr/bin/env python3
"""Beschleunigter Simulator fuer M5 auf Zaehlerebene (Analyse 318/518, Teil 2).

Zustand an jedem Zyklusbeginn (Kopf rechts vom Band auf leerer Zelle, Zustand A):
    Rest (woertlich) | Bausteine (Ziffer Z/D1/D2/D3 oder Trenner W, je mit Zahl der U links davon)
    | U^u_ende | Ende (0 oder 4 Einsen)
Regelmaessiger Zyklus (Regeln aus Teil 1, Zeitformel aus Teil 2):
  - rechte Ziffer +1 Phase; Uebertrag nach links, solange die Ziffer nach 3 oder 0 kommt (W uebersprungen)
  - Ziffer kommt nach 0 (D3->Z): ihre U links +1;  Ziffer kommt nach 1 (Z->D1): U links des rechten
    Nachbarbausteins -1 (bzw. u_ende -1)
  - Ende 0 -> 4; Ende 4 -> 0 und u_ende +1
  - Dauer = 38*U rechts der Wendeziffer + 52*#(D2->D3) + 74*#(D3->Z) + 44*#W rechts der Wendeziffer
            + (30 bei Z->D1, 66 bei D1->D2 an der Wendeziffer) + (30 falls Ende 4)
Alles andere (Uebertrag in den Rest, unbekannte Bausteine) rechnet das C-Programm direkt
("m5sim weiter"), danach wird neu zerlegt.

Aufruf:
  m5schnell.py <m5sim-Programm> <start A|C|D> <max_schritte> [--hash] [--stichprobe N] [--umbau DATEI]
    --hash        je Zyklusbeginn "Schritt Zustand Laenge CRC32" ausgeben (zum Abgleich mit "m5sim hash")
    --stichprobe N  jeden N-ten regelmaessigen Zyklus zusaetzlich direkt rechnen und vergleichen
    --umbau DATEI   jeden direkt gerechneten Zyklus (Band davor/danach in Bausteinen) in DATEI schreiben
"""
import subprocess
import sys
import zlib

M5 = "1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC"
K = 100
TOK = {"U": "11111010", "Z": "111010", "D1": "10111111111010", "D2": "10101111111010",
       "D3": "11111111111010", "W": "1111111010"}
RUNS = [("D2", (1, 1, 7, 1)), ("D1", (1, 9, 1)), ("U", (5, 1)), ("Z", (3, 1)), ("D3", (11, 1)), ("W", (7, 1))]
PH = {"Z": 0, "D1": 1, "D2": 2, "D3": 3}
NAME = ["Z", "D1", "D2", "D3"]


class Modell:
    def __init__(self, rest, items, uende, ende):
        self.rest = rest        # String
        self.items = items      # Liste [art, u_links]
        self.uende = uende
        self.ende = ende

    def band(self):
        teile = [self.rest]
        for art, u in self.items:
            teile.append(TOK["U"] * u)
            teile.append(TOK[art])
        teile.append(TOK["U"] * self.uende)
        teile.append("1" * self.ende)
        return "".join(teile)

    def kurz(self):
        r = self.rest if len(self.rest) <= 80 else self.rest[:40] + "..." + self.rest[-40:]
        t = " ".join((f"U^{u} " if u else "") + a for a, u in self.items)
        return f"Rest[{len(self.rest)}:{r}] {t} U^{self.uende} |{self.ende}"


def zerlege(band):
    """Band -> Modell oder None, wenn das Ende nicht 0/4 ist."""
    r = [len(x) for x in band.split("0")]
    ende, r = r[-1], r[:-1]
    if ende not in (0, 4):
        return None
    i, aus = len(r), []
    while i > 0:
        for name, muster in RUNS:
            k = len(muster)
            if i >= k and tuple(r[i - k:i]) == muster:
                aus.append(name)
                i -= k
                break
        else:
            break
    aus.reverse()
    rest = "".join("1" * x + "0" for x in r[:i])
    items, u = [], 0
    for a in aus:
        if a == "U":
            u += 1
        else:
            items.append([a, u])
            u = 0
    return Modell(rest, items, u, ende)


def regelzyklus(m):
    """Wendet einen regelmaessigen Zyklus an. Rueckgabe: Dauer oder None (nicht regelmaessig)."""
    ziff = [i for i, (a, _) in enumerate(m.items) if a != "W"]
    if not ziff:
        return None
    vor = []
    for i in reversed(ziff):
        neu = (PH[m.items[i][0]] + 1) % 4
        vor.append((i, neu))
        if neu not in (3, 0):
            break
    else:
        return None  # Uebertrag liefe in den Rest
    j = vor[-1][0]
    # Dauer aus dem Zustand vorher
    u_rechts = sum(u for _, u in m.items[j + 1:]) + m.uende
    w_rechts = sum(1 for a, _ in m.items[j + 1:] if a == "W")
    t = 38 * u_rechts + 44 * w_rechts + (30 if m.ende == 4 else 0)
    for i, neu in vor[:-1]:
        t += 52 if neu == 3 else 74
    t += 30 if vor[-1][1] == 1 else 66
    # Aenderungen (erst auf Kopie; negative Luecke = nicht regelmaessig)
    items = [list(x) for x in m.items]
    uende = m.uende
    for i, neu in vor:
        items[i][0] = NAME[neu]
        if neu == 0:
            items[i][1] += 1
        elif neu == 1:
            if i + 1 < len(items):
                items[i + 1][1] -= 1
            else:
                uende -= 1
    if m.ende == 4:
        uende += 1
    if uende < 0 or any(u < 0 for _, u in items):
        return None
    m.items, m.uende, m.ende = items, uende, 4 - m.ende
    return t


def direkt(prog, band, zustand, limit):
    p = subprocess.run([prog, "weiter", M5, zustand, str(limit), str(K)], input=band + "\n",
                       capture_output=True, text=True, check=True)
    out = p.stdout.split()
    if out[0] in ("LIMIT", "HALT", "Band"):
        return None
    return int(out[0]), out[1], out[2]


def main():
    prog, start, maxs = sys.argv[1], sys.argv[2], int(sys.argv[3])
    hsh = "--hash" in sys.argv
    stich = int(sys.argv[sys.argv.index("--stichprobe") + 1]) if "--stichprobe" in sys.argv else 0
    umf = open(sys.argv[sys.argv.index("--umbau") + 1], "w") if "--umbau" in sys.argv else None
    schritt, zustand, band = 0, start, ""
    # erster Zyklusbeginn direkt (vom Leerband)
    m = None
    nreg = ndir = nstich = 0
    out = sys.stdout
    while True:
        if m is not None and zustand == "A":
            mm = Modell(m.rest, [list(x) for x in m.items], m.uende, m.ende) if stich else None
            t = regelzyklus(m)
            if t is not None:
                if schritt + t > maxs:
                    break
                if stich and nreg % stich == 0 and t - 3 >= K:
                    d = direkt(prog, mm.band(), "A", 10**15)
                    if d is None or d[0] != t or d[1] != "A" or d[2] != m.band():
                        print(f"STICHPROBE FEHLER bei Schritt {schritt}", file=sys.stderr)
                        sys.exit(1)
                    nstich += 1
                schritt += t
                nreg += 1
                # Zyklusbeginn im Sinne von m5sim: Rechts-Rekord nach >= K Schritten ohne Rekord.
                # Ein regelmaessiger Zyklus beginnt mit 3 Rekorden in Folge (Schritt +1..+3).
                if hsh and t - 3 >= K:
                    b = m.band()
                    out.write(f"{schritt} A {len(b)} {zlib.crc32(b.encode())}\n")
                continue
        # direkt rechnen
        if m is not None:
            band = m.band()
        vorher = m.kurz() if m is not None else "(Leerband)"
        d = direkt(prog, band, zustand, maxs - schritt)
        if d is None:
            break
        dt, zustand, band = d
        schritt += dt
        ndir += 1
        m = zerlege(band)
        if umf:
            umf.write(f"{schritt - dt} -> {schritt} Dauer {dt} Breite {len(band)}\n  vorher:  {vorher}\n"
                      f"  nachher: {m.kurz() if m else band[:200]} Zustand {zustand}\n")
            umf.flush()
        if hsh:
            out.write(f"{schritt} {zustand} {len(band)} {zlib.crc32(band.encode())}\n")
        if m is None:
            m = None
    print(f"# Ende bei Schritt {schritt}: regelmaessig {nreg}, direkt {ndir}, Stichproben {nstich}",
          file=sys.stderr)
    if m is not None:
        print(f"# letzter Stand: {m.kurz()}", file=sys.stderr)


if __name__ == "__main__":
    main()
