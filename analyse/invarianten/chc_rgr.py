#!/usr/bin/env python3
"""Weg 1, Positivkontrolle: Regelsystem RGRv1 (busycoq-Pin, verify/RGRv1.v) als CHC fuer Z3/Spacer.

Zustand S0(n1,n2,n3,n4) wie in RGRv1.v:
  0^inf 1^n1 0 1^n2 QR> (01)^n3 000 (10)^n4 0^inf
Regeln (in busycoq je Maschine per shift_rule bewiesen):
  Inc : S0 n1 (2+n2) (2+n3) n4 -->+ S0 (1+n1) (1+n2) (1+n3) (1+n4)
  ROv : S0 n1 (1+n2) 1 n4      -->+ S0 (2+n1) (1+n2) (1+n4) 0
  LOv : S0 (4+n1) 1 (2+n3) n4  -->+ S0 3 (1+n1) (2+n3) (1+n4)
  init: c0 -->* S0 4 5 2 1
"Schlecht" = Zustand, auf den keine Regel passt (dort ist das Verhalten unbekannt, Halt moeglich).
Der Loeser soll eine Invariante finden, die von init erreicht wird, unter allen Regeln erhalten
bleibt und keinen schlechten Zustand enthaelt.

Aufruf: python3 chc_rgr.py [variante]   variante: ok (Standard) | fehler_rov | fehler_init
Ausgabe: Ergebnis (unsat = schlecht unerreichbar = Invariante gefunden), Invariante als SMT-LIB-Text.
"""
import sys, time
import z3

def baue(variante):
    fp = z3.Fixedpoint()
    fp.set(engine='spacer')
    I = z3.IntSort()
    Inv = z3.Function('Inv', I, I, I, I, z3.BoolSort())
    Bad = z3.Function('Bad', z3.BoolSort())
    fp.register_relation(Inv, Bad)
    a, b, c, d = z3.Ints('a b c d')
    fp.declare_var(a, b, c, d)
    nn = z3.And(a >= 0, b >= 0, c >= 0, d >= 0)
    # init
    if variante == 'fehler_init':
        fp.rule(Inv(0, 2, 3, 0))       # Negativkontrolle: nach einem Inc-Schritt (1,1,2,1), keine Regel passt
    else:
        fp.rule(Inv(4, 5, 2, 1))
    # Inc: (n1, 2+n2, 2+n3, n4) -> (1+n1, 1+n2, 1+n3, 1+n4)
    fp.rule(Inv(a + 1, b + 1, c + 1, d + 1), [Inv(a, b + 2, c + 2, d), nn])
    # ROv: (n1, 1+n2, 1, n4) -> (2+n1, 1+n2, 1+n4, 0)
    rov_plus = 1 if variante == 'fehler_rov' else 2   # Negativkontrolle: 1+n1 statt 2+n1 (System haengt nach 246 Regelschritten)
    fp.rule(Inv(a + rov_plus, b + 1, d + 1, 0), [Inv(a, b + 1, 1, d), nn])
    # LOv: (4+n1, 1, 2+n3, n4) -> (3, 1+n1, 2+n3, 1+n4)
    fp.rule(Inv(3, a + 1, c + 2, d + 1), [Inv(a + 4, 1, c + 2, d), nn])
    # schlecht: keine Regel passt
    inc_ok = z3.And(b >= 2, c >= 2)
    rov_ok = z3.And(b >= 1, c == 1)
    lov_ok = z3.And(a >= 4, b == 1, c >= 2)
    fp.rule(Bad(), [Inv(a, b, c, d), nn, z3.Not(z3.Or(inc_ok, rov_ok, lov_ok))])
    return fp, Inv, Bad

def main():
    variante = sys.argv[1] if len(sys.argv) > 1 else 'ok'
    fp, Inv, Bad = baue(variante)
    t = time.time()
    r = fp.query(Bad())
    dt = time.time() - t
    print(f'variante={variante} ergebnis={r} zeit={dt:.2f}s')
    if r == z3.unsat:
        inv = fp.get_cover_delta(-1, Inv)
        print('INVARIANTE (Variablen: Inv(n1,n2,n3,n4) = Var(0..3)):')
        print(inv.sexpr())
    elif r == z3.sat:
        print('GEGENBEISPIEL (Ableitung bis zum schlechten Zustand):')
        print(fp.get_answer())

if __name__ == '__main__':
    main()
