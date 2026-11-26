// luecke.go - zweites, unabhaengig geschriebenes Programm zu luecke.c (stehende Luecke, Vorstufen von "A> 0 0001").
//
// Anderes Prinzip als luecke.c: Hier wird NICHT angenommen, dass Luecken nur bei Linksschritten entstehen. Gefuehrt
// wird die Menge ALLER Luecken "1 0^k 1" (k >= 4) auf dem ganzen besuchten Band; nach jedem Schreiben, das ein Bit
// aendert, wird die Umgebung der Zelle neu vermessen (vorige 1, naechste 1). Eine Episode beginnt, sobald eine Luecke
// mit linker 1 strikt rechts vom Kopf in der Menge steht, und endet, sobald der Kopf auf ihrer linken 1 steht oder die
// Luecke verschwindet. Muster werden durch Vergleich von Zeichenketten erkannt.
//
// Aufruf: luecke <TM> <N> [--start Z] [--band W K] [--stoer S O V]...   (Ausgabe im Format von luecke.c, ohne R5-Liste)
package main

import (
	"fmt"
	"os"
	"sort"
	"strconv"
	"strings"
)

type regel struct {
	ok       bool
	schreibe byte
	dir      int64
	neu      int
}

const GROESSE = 1 << 26

func main() {
	a := os.Args
	zeilen := strings.Split(a[1], "_")
	tab := make([][2]regel, len(zeilen))
	for q, z := range zeilen {
		for s := 0; s < 2; s++ {
			t := z[3*s : 3*s+3]
			if strings.ContainsAny(t, "-HZ") {
				continue
			}
			d := int64(1)
			if t[1] == 'L' {
				d = -1
			}
			tab[q][s] = regel{true, t[0] - '0', d, int(t[2] - 'A')}
		}
	}
	N, _ := strconv.ParseInt(a[2], 10, 64)
	band := make([]byte, GROESSE)
	kopf := int64(GROESSE / 2)
	lo, hi := kopf, kopf
	zust := 0
	type stoer struct{ s, o int64; v byte }
	var st []stoer
	for i := 3; i < len(a); i++ {
		switch a[i] {
		case "--start":
			i++
			zust = int(a[i][0] - 'A')
		case "--band":
			w := a[i+1]
			k, _ := strconv.ParseInt(a[i+2], 10, 64)
			i += 2
			for j := 0; j < len(w); j++ {
				band[kopf-k+int64(j)] = w[j] - '0'
			}
			if kopf-k < lo {
				lo = kopf - k
			}
			if kopf-k+int64(len(w))-1 > hi {
				hi = kopf - k + int64(len(w)) - 1
			}
		case "--stoer":
			s, _ := strconv.ParseInt(a[i+1], 10, 64)
			o, _ := strconv.ParseInt(a[i+2], 10, 64)
			v, _ := strconv.Atoi(a[i+3])
			i += 3
			st = append(st, stoer{s, o, byte(v)})
		default:
			fmt.Fprintln(os.Stderr, "unbekannt:", a[i])
			os.Exit(2)
		}
	}
	// Menge aller Luecken: linke 1 -> k
	luecken := map[int64]int64{}
	vorige1 := func(x int64) int64 { // naechste 1 links von x im besuchten Bereich, sonst -1
		for j := x - 1; j >= lo; j-- {
			if band[j] == 1 {
				return j
			}
		}
		return -1
	}
	naechste1 := func(x int64) int64 {
		for j := x + 1; j <= hi; j++ {
			if band[j] == 1 {
				return j
			}
		}
		return -1
	}
	neuVermessen := func(x int64) {
		// alle Luecken, die x beruehren, entfernen und die Umgebung neu eintragen
		l := vorige1(x)
		r := naechste1(x)
		if l >= 0 {
			delete(luecken, l)
		}
		delete(luecken, x)
		paar := func(u, v int64) {
			if u >= 0 && v >= 0 && v-u-1 >= 4 {
				luecken[u] = v - u - 1
			}
		}
		if band[x] == 1 {
			paar(l, x)
			paar(x, r)
		} else {
			paar(l, r)
		}
	}
	// Anfangsmenge vollstaendig
	{
		l := int64(-1)
		for j := lo; j <= hi; j++ {
			if band[j] == 1 {
				if l >= 0 && j-l-1 >= 4 {
					luecken[l] = j - l - 1
				}
				l = j
			}
		}
	}
	str := func(von, bis int64) string { // Zellen von..bis einschliesslich
		var sb strings.Builder
		for j := von; j <= bis; j++ {
			sb.WriteByte('0' + band[j])
		}
		return sb.String()
	}
	namen := [8][2]string{}
	for q := 0; q < 8; q++ {
		namen[q][0] = string(rune('A'+q)) + "0"
		namen[q][1] = string(rune('A'+q)) + "1"
	}
	var cT, cVB, cVE, cP1, cP2, cP3 int64
	type r5w struct{ n, erst, letzt int64 }
	r5 := map[string]*r5w{}
	type ep struct {
		beginn int64
		k      int64
		ueb    string
		ctx    string
	}
	aktiv := map[int64]*ep{}
	var epzahl, maxoffen, mehrfach int64
	vorher := []string{"-0", "-0"}
	halt := 0
	var n int64
	si := 0
	var ausgabe []string
	for n = 0; n < N; n++ {
		for si < len(st) && st[si].s == n {
			z := kopf + st[si].o
			if z < lo {
				lo = z
			}
			if z > hi {
				hi = z
			}
			band[z] = st[si].v
			neuVermessen(z)
			si++
		}
		sym := band[kopf]
		r := tab[zust][sym]
		if !r.ok {
			halt = 1
			break
		}
		name := namen[zust][sym]
		ist5 := band[kopf+1] == 0 && band[kopf+2] == 0 && band[kopf+3] == 0 && band[kopf+4] == 0 && band[kopf+5] == 1
		if ist5 && str(kopf+1, kopf+5) == "00001" {
			w := r5[name]
			if w == nil {
				w = &r5w{0, n, n}
				r5[name] = w
			}
			w.n++
			w.letzt = n
			if name == "B1" {
				cVB++
			}
			if name == "E0" {
				cVE++
			}
		}
		if name == "A0" && band[kopf+4] == 1 && str(kopf+1, kopf+4) == "0001" {
			cT++
		}
		if name == "A0" && band[kopf+6] == 1 && str(kopf+1, kopf+6) == "100001" {
			cP1++
		}
		if name == "D1" && band[kopf-1] == 0 && band[kopf+4] == 1 && str(kopf+1, kopf+4) == "0001" {
			cP2++
		}
		if name == "C1" && band[kopf+6] == 1 && str(kopf+1, kopf+6) == "000001" {
			cP3++
		}
		alt := band[kopf]
		band[kopf] = r.schreibe
		if alt != r.schreibe {
			neuVermessen(kopf)
		}
		kopf += r.dir
		if kopf < lo {
			lo = kopf
		}
		if kopf > hi {
			hi = kopf
		}
		zust = r.neu
		vorher[0], vorher[1] = vorher[1], name
		// Episoden pflegen (Menge leer: nichts zu tun; maxoffen aendert sich dann nicht)
		if len(luecken) == 0 && len(aktiv) == 0 {
			continue
		}
		for pos, e := range aktiv {
			k, da := luecken[pos]
			if pos <= kopf || !da || k != e.k {
				ankunft := "-"
				if pos == kopf {
					ankunft = string(rune('A' + zust))
				}
				ausgabe = append(ausgabe, fmt.Sprintf("EP %d %d %d %d %s %s %s", e.beginn, n+1, n+1-e.beginn, e.k, ankunft, e.ueb, e.ctx))
				delete(aktiv, pos)
			}
		}
		for pos, k := range luecken {
			if pos > kopf && aktiv[pos] == nil {
				aktiv[pos] = &ep{n + 1, k, vorher[0] + vorher[1], str(pos-32, pos-1)}
				epzahl++
				if int64(len(aktiv)) > 1 {
					mehrfach++
				}
			}
		}
		if int64(len(aktiv)) > maxoffen {
			maxoffen = int64(len(aktiv))
		}
	}
	for _, e := range aktiv {
		ausgabe = append(ausgabe, fmt.Sprintf("EP %d -1 %d %d - %s %s", e.beginn, n-e.beginn, e.k, e.ueb, e.ctx))
	}
	for _, z := range ausgabe {
		fmt.Println(z)
	}
	fmt.Printf("ERGEBNIS schritte=%d halt=%d T=%d VB=%d VE=%d P1=%d P2=%d P3=%d episoden=%d max_gleichzeitig=%d mehrfach=%d\n",
		n, halt, cT, cVB, cVE, cP1, cP2, cP3, epzahl, maxoffen, mehrfach)
	var rnamen []string
	for k := range r5 {
		rnamen = append(rnamen, k)
	}
	sort.Strings(rnamen)
	for _, k := range rnamen {
		w := r5[k]
		fmt.Printf("R5SUMME %s %d erster=%d letzter=%d\n", k, w.n, w.erst, w.letzt)
	}
}
