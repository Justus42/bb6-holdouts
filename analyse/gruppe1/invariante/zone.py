"""Induktion ueber die Zone: Zonen-Token als Stern ('S','Z') links, Faltung bearbeiteter Token.

Faltung (jede Regel ist eine Ueberapproximation, also solide):
  L: Muster Z = [('w','011', ungerade >= 1), ('b',1)]  (Zonen-Token (1, ungerade), wie unbearbeitet)
  R: Muster Y = [('b',0), ('w','100', ungerade >= 1)]  (Zonen-Token nach dem Linksdurchlauf)
  * Muster direkt ueber oder unter einem Stern desselben Musters wird in den Stern gezogen.
  * Zwei benachbarte Muster werden zu einem Stern (Stern = 0 oder mehr Kopien, also mehr als vorher).
Damit wird der abstrakte Zustandsraum endlich, und die Suche deckt jede Zonenlaenge ab.
Aufruf: python3 -I zone.py [Regel|alle]
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import symb as s            # noqa: E402
import lauf_m as lm         # noqa: E402

s.STERNE["Y"] = [("b", 0), ("w", "100", ("a", 1))]
if s.FEHLER == "zone":
    s.STERNE["Y"] = [("b", 0), ("w", "100", ("a", 0))]


def teilmenge(n, m):
    """abstrakte Zahl n in m enthalten?"""
    if m[0] == "e":
        return n == m
    return n[1] >= m[1] and n[1] % 2 == m[1] % 2


def passt(items, muster):
    if len(items) != len(muster):
        return False
    for x, y in zip(items, muster):
        if x[0] != y[0]:
            return False
        if x[0] == "b" and x != y:
            return False
        if x[0] == "w" and (x[1] != y[1] or not teilmenge(x[2], y[2])):
            return False
    return True


def falte_stapel(st, name):
    muster = s.STERNE[name]
    k = len(muster)
    stern = ("S", name)
    st = list(st)
    geaendert = True
    while geaendert:
        geaendert = False
        for i in range(len(st)):
            if passt(st[i:i + k], muster) and i + k < len(st) and st[i + k] == stern:
                st[i:i + k + 1] = [stern]
                geaendert = True
                break
            if st[i] == stern and passt(st[i + 1:i + 1 + k], muster):
                st[i:i + 1 + k] = [stern]
                geaendert = True
                break
            if passt(st[i:i + k], muster) and passt(st[i + k:i + 2 * k], muster):
                st[i:i + 2 * k] = [stern]
                geaendert = True
                break
            if i + 1 < len(st) and st[i] == stern and st[i + 1] == stern:
                st[i:i + 2] = [stern]
                geaendert = True
                break
    return tuple(st)


def falte(z):
    q, seite, L, R = z
    return (q, seite, falte_stapel(L, "Z"), falte_stapel(R, "Y"))


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "alle"
    regeln = list(lm.REGELN) if arg == "alle" else arg.split(",")
    alle_ok = True
    zert = {}
    for rg in regeln:
        zone = [("S", "Z")]
        if rg == "LG":
            zone = lm.ZT + [("S", "Z")]      # mindestens ein Token ausser T0
        ergebnisse = []
        for st in lm.starts(rg, 0, zone=zone):
            ok, info = s.suche(falte(st), falte=falte)
            ergebnisse.append((ok, info))
            if not ok:
                break
            zert.setdefault(rg, {"starts": [], "menge": []})
            zert[rg]["starts"].append(st)
            zert[rg]["menge"].extend(info["menge"])
        if all(ok for ok, _ in ergebnisse):
            print(f"{rg:4s} BEWIESEN: {sum(i['zustaende'] for _, i in ergebnisse)} abstrakte Zustaende, "
                  f"{sum(i['enden'] for _, i in ergebnisse)} Phasenenden, {len(ergebnisse)} Startformen")
        else:
            alle_ok = False
            ok, info = ergebnisse[-1]
            print(f"{rg:4s} OFFEN: {info['grund']}")
            for z in info["weg"][-14:]:
                print("     ", s.zeige(z))
    print("alle bewiesen" if alle_ok else "nicht alle bewiesen")
    ziel = os.environ.get("ZERTIFIKAT")
    if ziel and alle_ok:
        json.dump(zert, open(ziel, "w"))
        print("Zertifikat geschrieben:", ziel)


if __name__ == "__main__":
    main()
