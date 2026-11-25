// Zweitprogramm Gruppe 1, Teil 2 (unabhaengig von gruppe1.py/zweitpruefung.c):
// direkte Simulation mit zwei Stapeln (Vec) statt Array; zaehlt
//  - A-Besuche und wie oft A dabei eine 1 liest (= Halt)
//  - Lesungen "B oder D liest 0" mit folgendem 11 (Pruefpunkt) und deren viertes Feld
//  - an jedem Rechts-Rekord in Zustand C: Nullabstaende von rechts; Invariante
//    I1: alle Abstaende in {1,..,5}; I2: nie zwei Abstaende < 3 direkt hintereinander.
use std::env;
fn main() {
    let a: Vec<String> = env::args().collect();
    let m = a[1].as_bytes();
    let limit: u64 = a[2].parse().unwrap();
    let start = a.get(3).map(|s| s.as_bytes()[0] - b'A').unwrap_or(0) as usize;
    // Tabelle
    let mut tab = [[(0u8, false, 0usize); 2]; 6];
    let groups: Vec<&[u8]> = m.split(|&c| c == b'_').collect();
    for (q, g) in groups.iter().enumerate() {
        for s in 0..2 {
            let t = &g[3 * s..3 * s + 3];
            tab[q][s] = if t[0] == b'-' { (1, true, 99) } else { (t[0] - b'0', t[1] == b'R', (t[2] - b'A') as usize) };
        }
    }
    // Band: links-Stapel (Index 0 = ganz links), rechts-Stapel (letztes = direkt rechts vom Kopf)
    let mut left: Vec<u8> = Vec::new();
    let mut right: Vec<u8> = Vec::new();
    let mut head: u8 = 0;
    let mut q = start;
    let mut pos: i64 = 0; let mut lo: i64 = 0; let mut hi: i64 = 0;
    let (mut a_vis, mut a_one, mut tests, mut test_bad, mut crec, mut i1_bad, mut i2_bad) = (0u64, 0u64, 0u64, 0u64, 0u64, 0u64, 0u64);
    let mut steps = 0u64;
    // letzte Wende rechts->links: Position, ob durch C0, Band dahinter (3 Zellen)
    let (mut wpos, mut wc0, mut wctx, mut dir_r) = (i64::MIN, false, [0u8; 3], true);
    let (mut t_turn, mut t_ctx100) = (0u64, 0u64);
    let get_r = |right: &Vec<u8>, k: usize| -> u8 { if right.len() >= k { right[right.len() - k] } else { 0 } };
    while steps < limit {
        if q == 0 { a_vis += 1; if head == 1 { a_one += 1; } }
        if (q == 1 || q == 3) && head == 0 && get_r(&right, 1) == 1 && get_r(&right, 2) == 1 {
            tests += 1; if get_r(&right, 3) == 1 { test_bad += 1; }
            if wc0 && wpos == pos + 1 { t_turn += 1; if wctx == [1, 0, 0] { t_ctx100 += 1; } }
        }
        let (w, r, nq) = tab[q][head as usize];
        if nq == 99 { break; }
        if dir_r && !r { wpos = pos; wc0 = q == 2 && head == 0; wctx = [get_r(&right, 1), get_r(&right, 2), get_r(&right, 3)]; }
        dir_r = r;
        if r { left.push(w); head = right.pop().unwrap_or(0); pos += 1; }
        else { right.push(w); head = left.pop().unwrap_or(0); pos -= 1; }
        q = nq; steps += 1;
        if pos < lo { lo = pos; }
        if pos > hi {
            hi = pos;
            if q == 2 {
                crec += 1;
                // Band vom rechten Ende (Kopf) nach links: head, dann left rueckwaerts; nur bis lo
                let width = (hi - lo) as usize; // Zellen links vom Kopf innerhalb besuchter Zone
                let mut last: Option<usize> = if head == 0 { Some(0) } else { None };
                let mut prev_small = false;
                for k in 1..=width {
                    let c = if left.len() >= k { left[left.len() - k] } else { 0 };
                    if c == 0 {
                        if let Some(l) = last {
                            let g = k - l;
                            if g < 1 || g > 5 { i1_bad += 1; }
                            let small = g < 3;
                            if small && prev_small { i2_bad += 1; }
                            prev_small = small;
                        }
                        last = Some(k);
                    }
                }
            }
        }
    }
    println!("{} start={} steps={} A_besuche={} A_liest_1={} pruefpunkte={} pruefpunkt_mit_111={} nach_C0_Wende_bei_i+1={} davon_Kontext_100={} C_rechtsrekorde={} I1_verletzt={} I2_verletzt={}",
        a[1], (b'A' + start as u8) as char, steps, a_vis, a_one, tests, test_bad, t_turn, t_ctx100, crec, i1_bad, i2_bad);
}
