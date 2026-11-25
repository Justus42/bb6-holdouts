"""Liest alle Eqv*.v am busycoq-Pin und listet je Modul die Paare (tm, tm') aus Lemma eqv.
Aufruf: python3 -I eqv_pin.py <busycoq/verify> <BB6_holdouts_608.txt> <holdouts.json>
Ausgabe (stdout, TSV): datei modul tm tm2 n_tm n_tm2 decided_tm decided_tm2
"""
import sys, re, json
from pathlib import Path
verify, liste, hj = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
H = [l.strip() for l in open(liste) if l.strip()]
hn = {m: i+1 for i, m in enumerate(H)}
D = json.load(open(hj))["decided"]
dn = {x["tm"]: (x["n"], x["by"], x["file"]) for x in D}
rx_mod = re.compile(r"^Module (\w+)\.", re.M)
rx_def = re.compile(r"Definition (tm'?)\s*:=\s*(?:Eval compute in\s*)?\(?\s*TM_from_str\s+\"([^\"]+)\"")
print("datei\tmodul\ttm\ttm_strich\tholdout_tm\tholdout_tm_strich\tdecided_tm\tdecided_tm_strich")
for f in sorted(verify.glob("Eqv*.v")):
    txt = f.read_text()
    starts = [(m.start(), m.group(1)) for m in rx_mod.finditer(txt)] + [(len(txt), None)]
    for (a, name), (b, _) in zip(starts, starts[1:]):
        body = txt[a:b]
        defs = dict(rx_def.findall(body))
        if "tm" in defs and "tm'" in defs and re.search(r"(Lemma|Theorem) eqv\s*:", body):
            t, t2 = defs["tm"], defs["tm'"]
            g = lambda m: str(hn.get(m, "")); d = lambda m: ("%d/%s/%s" % dn[m]) if m in dn else ""
            print(f"{f.name}\t{name}\t{t}\t{t2}\t{g(t)}\t{g(t2)}\t{d(t)}\t{d(t2)}")
