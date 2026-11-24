#!/usr/bin/env python3
"""Simulator 1 (Python): Turingmaschinen im bbchallenge-Textformat.

Bandmodell: ein dichtes bytearray, das bei Bedarf nach links/rechts verdoppelt
wird; die Kopfposition ist ein Index in dieses Array.

Konventionen: Start in Zustand A auf leerem Band (0). Ein Schritt = ein ausgefuehrter
Uebergang; der Halte-Uebergang zaehlt als Schritt und schreibt sein Symbol.
Zielzustand ausserhalb der definierten Zustaende (Z, H, ...) = Halt; "---" = 1RZ.
Ausgabe: eine JSON-Zeile {"machine","halted","steps","ones"}.
Aufruf: sim1.py <maschine> [schrittlimit=100000000]
"""
import json
import re
import sys

HALT = -1


def parse(machine):
    groups = machine.split("_")
    nstates = len(groups)
    if nstates < 1 or nstates > 26:
        raise ValueError("Anzahl Zustaende ungueltig")
    nsym = len(groups[0]) // 3
    if nsym < 2 or any(len(g) != 3 * nsym for g in groups):
        raise ValueError("Gruppenlaengen ungleich oder ungueltig")
    table = []
    for g in groups:
        row = []
        for i in range(nsym):
            t = g[3 * i:3 * i + 3]
            if t == "---":
                t = "1RZ"
            m = re.fullmatch(r"([0-9])([LR])([A-Z])", t)
            if not m or int(m.group(1)) >= nsym:
                raise ValueError(f"Uebergang ungueltig: {g[3*i:3*i+3]!r}")
            nxt = ord(m.group(3)) - ord("A")
            row.append((int(m.group(1)), 1 if m.group(2) == "R" else -1,
                        nxt if nxt < nstates else HALT))
        table.append(tuple(row))
    return table


def run(machine, limit):
    table = parse(machine)
    tape = bytearray(1024)
    pos = 512
    state = 0
    steps = 0
    halted = False
    while steps < limit:
        write, move, nxt = table[state][tape[pos]]
        tape[pos] = write
        steps += 1
        if nxt == HALT:
            halted = True
            break
        state = nxt
        pos += move
        if pos < 0:
            n = len(tape)
            tape[0:0] = bytes(n)
            pos += n
        elif pos >= len(tape):
            tape.extend(bytes(len(tape)))
    return {"machine": machine, "halted": halted, "steps": steps,
            "ones": sum(1 for c in tape if c == 1)}


def main(argv):
    if len(argv) not in (2, 3):
        print(__doc__, file=sys.stderr)
        return 2
    try:
        limit = int(argv[2]) if len(argv) == 3 else 100_000_000
        res = run(argv[1], limit)
    except ValueError as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 2
    print(json.dumps(res, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
