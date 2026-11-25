# Zweites Programm: Besuchsgesetz naiv, ein Besuch nach dem anderen (Python, rekursiv auf Liste), exakt.
import sys
sys.setrecursionlimit(100000)
class Halt(Exception): pass
def visit(w, i, modus):
    # wendet einen Besuch auf w ab Index i an (w wird nach Bedarf mit Nullen verlaengert)
    while len(w) < i+4: w.append(0)
    a,b,c,d = w[i],w[i+1],w[i+2],w[i+3]
    if a == 0: w[i] = 1; return
    if b == 1 and c == 1: raise Halt('111')
    if b == 0 and c == 0 or b == 1 and c == 0:
        w[i] = w[i+1] = w[i+2] = 0; visit(w, i+3, modus); return
    if b == 0 and c == 1 and d == 0:
        visit(w, i+4, modus); visit(w, i+4, modus); return
    if b == 0 and c == 1 and d == 1:
        if modus == '88': raise Halt('1011')
        w[i] = w[i+1] = w[i+2] = 0; return
modus = sys.argv[1]; R = int(sys.argv[2])
s = [int(ch) for ch in (sys.argv[3] if len(sys.argv) > 3 else '1')]
for k in range(1, R+1):
    w = [1,0] + s
    try:
        visit(w, 0, modus)
    except Halt as h:
        print('HALT', h, 'Runde', k); break
    while w and w[-1] == 0: w.pop()
    s = w
    print('R', k, ''.join(map(str, s)))
