// naiv.go - zweites, unabhaengig geschriebenes Programm zu kein11.c (M5, Ansatz "nie 11 strikt rechts vom Kopf").
//
// Absichtlich naiv: nach JEDEM Schritt wird der ganze besuchte Bereich auf der geprueften Seite des Kopfes
// nach zwei benachbarten Einsen abgesucht (keine Fortschreibung). Das Band ist eine Map von Ort auf Bit.
// Gleiche Aufrufzeile und gleiche HASH-Zeile wie kein11.c, damit die Laeufe Zeile fuer Zeile vergleichbar sind.
//
//   naiv <TM> <Seite R|L> <N> [--start Z] [--band W K] [--stoer S O V]... [--stop]
package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

type regel struct {
	def      bool
	schreibe int
	richtung int
	neu      int
}

func main() {
	a := os.Args
	if len(a) < 4 {
		fmt.Fprintln(os.Stderr, "Aufruf: naiv <TM> <R|L> <N> ...")
		os.Exit(2)
	}
	zeilen := strings.Split(a[1], "_")
	tab := make([][2]regel, len(zeilen))
	for q, z := range zeilen {
		for s := 0; s < 2; s++ {
			t := z[3*s : 3*s+3]
			if strings.ContainsAny(t, "-HZ") {
				continue
			}
			r := regel{def: true, schreibe: int(t[0] - '0'), neu: int(t[2] - 'A')}
			if t[1] == 'R' {
				r.richtung = 1
			} else {
				r.richtung = -1
			}
			tab[q][s] = r
		}
	}
	seite := a[2]
	N, _ := strconv.ParseInt(a[3], 10, 64)
	zust := 0
	band := map[int64]int{}
	var kopf int64 = 0
	lo, hi := int64(0), int64(0)
	type stoer struct {
		s int64
		o int64
		v int
	}
	var st []stoer
	stop := false
	for i := 4; i < len(a); i++ {
		switch a[i] {
		case "--start":
			i++
			zust = int(a[i][0] - 'A')
		case "--band":
			w := a[i+1]
			k, _ := strconv.ParseInt(a[i+2], 10, 64)
			i += 2
			for j := 0; j < len(w); j++ {
				if w[j] == '1' {
					band[int64(j)-k] = 1
				}
			}
			if -k < lo {
				lo = -k
			}
			if int64(len(w))-1-k > hi {
				hi = int64(len(w)) - 1 - k
			}
		case "--stoer":
			s, _ := strconv.ParseInt(a[i+1], 10, 64)
			o, _ := strconv.ParseInt(a[i+2], 10, 64)
			v, _ := strconv.Atoi(a[i+3])
			i += 3
			st = append(st, stoer{s, o, v})
		case "--stop":
			stop = true
		default:
			fmt.Fprintln(os.Stderr, "unbekannt:", a[i])
			os.Exit(2)
		}
	}
	// verletzt: sucht den ganzen besuchten Bereich ab
	verletzt := func() bool {
		if seite == "R" {
			for i := kopf + 1; i < hi+1; i++ {
				if band[i] == 1 && band[i+1] == 1 {
					return true
				}
			}
		} else {
			for i := lo - 1; i+1 < kopf; i++ {
				if band[i] == 1 && band[i+1] == 1 {
					return true
				}
			}
		}
		return false
	}
	var brueche, erster int64 = 0, -1
	if verletzt() {
		brueche, erster = 1, 0
	}
	halt := 0
	var n int64
	si := 0
	for n = 0; n < N; n++ {
		for si < len(st) && st[si].s == n {
			z := kopf + st[si].o
			band[z] = st[si].v
			if z < lo {
				lo = z
			}
			if z > hi {
				hi = z
			}
			if verletzt() && erster < 0 {
				erster = n
			}
			si++
		}
		sym := band[kopf]
		r := tab[zust][sym]
		if !r.def {
			halt = 1
			break
		}
		band[kopf] = r.schreibe
		kopf += int64(r.richtung)
		zust = r.neu
		if kopf < lo {
			lo = kopf
		}
		if kopf > hi {
			hi = kopf
		}
		if verletzt() {
			brueche++
			if erster < 0 {
				erster = n + 1
			}
			if stop {
				n++
				break
			}
		}
	}
	var h uint64 = 1469598103934665603
	mix := func(x uint64) { h ^= x; h *= 1099511628211 }
	mix(uint64(zust))
	mix(uint64(kopf - lo))
	for j := lo; j <= hi; j++ {
		mix(uint64(band[j]))
	}
	fmt.Printf("ERGEBNIS schritte=%d halt=%d brueche=%d erster_bruch=%d breite=%d\n", n, halt, brueche, erster, hi-lo+1)
	fmt.Printf("HASH %016x zustand=%c kopf_rel=%d\n", h, 'A'+zust, kopf-lo)
}
