# Zweites, getrennt geschriebenes Programm zu formen.py (gleiche Definition von Form und Kern, siehe dort
# und im Bericht). Eingabe: Rueckfall-Saetze, nach n sortiert, z. B.
#   sed 's/ #.*//' a.txt c.txt d.txt | sort -n -k1,1 | awk -f formen2.awk
# Ausgabe: je Zehnerpotenz Faelle, neue Formen, neue Kerne; am Ende die Gesamtzahlen.
# Negativkontrollen: awk -v FEHLER=kern (Kern ohne R/I und frei/alt), -v FEHLER=fenster (gemeinsamer Anfang
# wird nicht abgeschnitten) muessen andere Zahlen liefern.

function zerlege(text, S, N,    k, w, i, m, teil) {
  # text: "t:n t:n ... /rest" ; S[i] Trenner ("1","0","_"), N[i] Zahl ; Rueckgabe Anzahl, REST global
  m = index(text, "/")
  REST = substr(text, m + 1); gsub(/ /, "", REST)
  teil = substr(text, 1, m - 1)
  k = split(teil, w, " ")
  for (i = 1; i <= k; i++) { S[i] = substr(w[i], 1, 1); N[i] = substr(w[i], 3) + 0 }
  return k
}
function zeichen(s) { return s == "1" ? "" : (s == "0" ? "." : "_") }
function unregel(s, n) { return (s != "1") || (n % 2 == 0) }
function stelle(S, N, von, bis,    i, out) {
  out = ""
  for (i = von; i <= bis; i++) out = out (i > von ? " " : "") zeichen(S[i]) N[i]
  return out
}
{
  zeile = $0
  sub(/ #.*/, "", zeile)
  split(zeile, teile, " \\| ")
  split(teile[1], kopf, " ")
  n = kopf[1]; art = kopf[3]
  delete XS; delete XN; delete YS; delete YN
  lx = zerlege(teile[2], XS, XN); xr = REST
  ly = zerlege(teile[3], YS, YN); yr = REST
  ux = lx; uy = ly                                  # benutzte Laengen
  if (art ~ /^Ueb/ && lx >= 5 && ly >= 3) { ux = lx - 4; uy = ly - 2 }
  s = 0
  if (xr == "" && yr == "") {
    while (s < (ux < uy ? ux : uy) && XS[ux - s] == YS[uy - s] && XN[ux - s] == YN[uy - s]) s++
  }
  i = 0
  grenze = (ux < uy ? ux : uy) - s
  while (FEHLER != "fenster" && i < grenze && XS[i + 1] == YS[i + 1] && XN[i + 1] == YN[i + 1]) i++
  # Fenster: X[i+1 .. ux-s], Y[i+1 .. uy-s]
  ax = i + 1; ex = ux - s; ay = i + 1; ey = uy - s
  rnd = (i == 0) ? "R" : "I"
  if (ex >= ax && ey >= ay && xr == "" && yr == "") {
    c = YN[ey] - XN[ex]
    A = stelle(XS, XN, ax, ex - 1); if (A != "") A = A " "; A = A zeichen(XS[ex]) "p"
    B = stelle(YS, YN, ay, ey - 1); if (B != "") B = B " "
    B = B zeichen(YS[ey]) (c == 0 ? "p" : (c > 0 ? "p+" c : "p" c))
  } else {
    A = stelle(XS, XN, ax, ex) (xr != "" ? "<" xr ">" : "")
    B = stelle(YS, YN, ay, ey) (yr != "" ? "<" yr ">" : "")
  }
  formschl = rnd " " A " -> " B
  # Kern
  if (art ~ /^Ueb/) zl = (lx >= 5) ? lx - 4 : lx; else zl = lx - 1
  g = 0
  for (j = zl; j >= 1; j--) if (unregel(XS[j], XN[j])) { g = j; break }
  if (g == 0) kernschl = "keine Grenze" (xr != "" ? "<" xr ">" : "")
  else {
    a = g
    while (a - 1 >= 1 && unregel(XS[a - 1], XN[a - 1])) a--
    frei = "frei"
    for (j = 1; j < a; j++) if (unregel(XS[j], XN[j])) { frei = "alt"; break }
    kk = ""
    for (j = a; j <= g; j++) {
      v = (XN[j] == 0) ? "0" : ((XN[j] % 2) ? "o" : "e")
      kk = kk (j > a ? " " : "") zeichen(XS[j]) v
    }
    kernschl = (FEHLER == "kern" ? "" : rnd " " frei " ") kk (xr != "" ? "<" xr ">" : "")
  }
  d = length(n "") - 1
  faelle[d]++
  if (!(formschl in formen)) { formen[formschl] = n; neuf[d]++; anzf++ }
  if (!(kernschl in kerne)) { kerne[kernschl] = n; neuk[d]++; anzk++ }
  muster = (g == 0) ? kernschl : kk (xr != "" ? "<" xr ">" : "")
  if (!(muster in mus)) { mus[muster] = n; neum[d]++; anzm++ }
  if (d > maxd) maxd = d
  gesamt++
}
END {
  printf "Faelle %d, Formen %d, Kerne %d, Kernmuster %d\n", gesamt, anzf, anzk, anzm
  for (d = 0; d <= maxd; d++) if (faelle[d] > 0)
    printf "  10^%d..10^%d  Faelle %5d  neue Formen %3d  neue Kerne %2d  neue Kernmuster %2d\n", d, d + 1, faelle[d], neuf[d] + 0, neuk[d] + 0, neum[d] + 0
}
