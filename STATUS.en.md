# Project status (25 Nov 2026, evening)

Per group: what is **proved** (Rocq, with file and Actions run), what is only **observed** (with the bound
checked and the number of programs), and what is **open**. Every number points to the report it comes from
(tags below). Where reports disagree or were corrected later, the later one counts; corrections are listed at
the end. German version: `STATUS.md` (authoritative if the two differ).

**Overall:** No machine is decided. The only Rocq results are a reformulation for Group 1 (sweep
acceleration) and one rule on top of it (rule F). Everything else is observation up to a bound.

Reports (all in `analyse/`, German, merged with the PR in brackets):
[G1] `gruppe1.md` (PR 2) · [G1-2] `gruppe1_teil2.md` (PR 3) · [G1-3] `gruppe1_teil3.md` (PR 6) ·
[S1] `gruppe1_stufe1.md` (PR 7) · [S2a] `gruppe1_stufe2a.md` (PR 8) · [ZY] `gruppe1_zyklus.md` (PR 9) ·
[LE] `gruppe1_linkes_ende.md` (PR 10) · [VL] `gruppe1_vorlagen.md` (PR 11) · [P26] `gruppe1_pr26.md` (PR 11) ·
[GR] `gruppe1_groesse.md` (PR 16) · [VB] `gruppe1_verboten.md` (PR 17) · [INV] `invarianten.md` (PR 15) ·
[M1] `318_518.md` (PR 4) · [M2] `318_518_teil2.md` (PR 5) · [396] `396.md` (PR 13) ·
[VK] `verwandtschaft.md` (PR 12, corrected in PR 13; English summary `verwandtschaft_en.md`) ·
[DA] `stand/datenabgleich.md` (this PR).

## Data (check of 25 Nov 2026) [DA]

- `holdouts.json` re-downloaded from denniskoshta.com (`data/holdouts_2026-11-25.json`): **byte-identical** to
  the 10 Nov snapshot. The site has not regenerated the file since.
- busycoq read directly: branch BB6 still at `33209bc7` (3 Nov), so **nothing merged** since. 58 new PR refs
  (62 to 119, 9 to 25 Nov) contain strings of 63 holdouts. **None concerns 396, 88, 312, 449, Group 1 or the
  M5 group** (two programs agree line by line, plus a normal-form check; negative controls fire). Whether
  those PRs are open or closed was not checked.
- cryptids (commit `f01ee56`, 25 Nov): nothing on 396, 88, 449, Group 1, M5. 312 has a formal reduction there
  (not a decision). Holdout 587 has a proved acceleration in the same situation as 396 (`1011` does not halt,
  only `111` does); read only.

## Group 1: 114, 367, 378 (one table, three starts)

### Proved (Rocq)

File `rocq/gruppe1_durchlauf.v` (515 lines, sha256 starts `79fdf709fca14c75`, unchanged since commit `44d8ed5`).

| Statement | Content | **pruefen** run (both images green, Print Assumptions `Closed under the global context`) |
|---|---|---|
| `gruppe1_114`, `gruppe1_367`, `gruppe1_378` | The machine halts from blank tape iff the sweep model (rules S1, S2, E) started in A / D / C reaches "halt". A reformulation, **not a decision** [S1] | run 45599575217 (commit `8722d86`) [S1]; again in run 45602646558 [S2a] |
| `regel_F`, `regel_F_oft` | eating round `x \| y → x+4 \| y−1` for odd x, y ≥ 1, in 25 model steps; m rounds at once [S2a] | run 45602646558 (commit `44d8ed5`) [S2a] |
| `erreicht_halt_erreicht` | such a jump does not change halting [S2a] | run 45602646558 [S2a] |

Shown by hand, **not** machine-checked: **Lemma K(C)**. If the run starts on a tape that is blank to the right
of the head, every halt is preceded by a moment where C steps from the left onto `0 1 1`. Necessary, not
sufficient [VB, section 1.2]. Confirmed externally by Justus.

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| No halt, every step checked | 10^12 steps, all three starts | 2 (`direkt.c` run 45614962053; `zaehl_direkt.c` run 45668615893) | [LE §2], [VB §4] |
| No K(C) (`C> 0 1 1`) | 10^9 locally, 10^10 in Actions (run 45668615893); up to 10^12 only `zaehl_direkt.c` | 2 up to 10^10, 1 up to 10^12 | [VB §2, §4] |
| No halt, **conditional** (phase automaton rules only empirical) | 10^22 steps, all three starts, 900 samples without finding | 1 (cycle accelerator, local), validated against `beschleuniger.py` up to 10^12 | [VB §5] |
| Run beyond 10^22 | **running**: Actions run 45684698614 (stops after 340 min per start); no result yet | – | [VB §5] |
| Sweep model = direct simulation, byte for byte | 10^9 steps, 36,944 list lines | 2 (`sweepmodell.py`, `zweitpruefung.c`) | [G1-3 §2] |
| Check points (B/D reads 0, `11` to the right) 1.63 to 1.64 million per start, none with `111` | 10^9 | 2 (C, Rust) | [G1-2 §1] |
| Rule Z: `x = a + 4b + 7` at the end of every eating phase, 76/76, 77/77, 76/76 | 10^9 | lists from C, check in Python | [G1] |
| a even at all 232 cycle starts (so x odd, as rule F requires) | 10^9 | 2 (`zyklus.py`, `zyklus2.c`) | [ZY §5] |
| Cycle function predicts 68/76 (A), 67/76 (C), 66/77 (D) cycles exactly, **none wrong**; the rest "not applicable", always at the left end | 10^9 | 2 | [ZY] |
| Phase automaton (N1, N2, N2s, UA, LE, LG, VS) explains 99.995 % of phases | 10^17 (run 45614962053) | accelerator, equal to `direkt.c` at about 642,000 snapshots per start up to 10^12 | [LE §1, §2] |
| Left end: 2,877 unexplained cases in 13 core patterns; 13th pattern only at 8.2·10^16; "alt" share rising (0.7 % → 1.5 %) | 10^17 | 2 (`formen.py`, `formen2.awk`) | [LE §3, §4] |
| VS family as an 11-case rule: 1,656 of 1,656 observed cases right | 10^17 | rule against sweep model | [LE §4] |
| No conserved quantity; inside only m, S + r, x are conserved | 10^15 | 2 (`groesse.py`, `groesse2.c`), runs 45676439532, 45679952727 | [GR] |
| No CTL certificate (tape language with two automata) | all sizes up to 12×12 | SAT search, small sizes confirmed by enumeration | [INV] |
| The three starts do not merge | 10^9 | 1 | [G1 §1] |

### Open

- Whether Group 1 halts: **open** [VB §8].
- An invariant excluding K(C) or halting: none found [ZY §5], [GR §5], [INV], [VB §8].
- Phase automaton rules are not proved; halting beyond 10^12 is excluded only conditionally [VB §4].
- Left end: 7 of 8 families without a rule, "alt" cases without a rule, saturation not shown [LE §4].
- Rule Z and the first/last eating round not in Rocq [S2a]. Why a is always even is not proved [S2a], [ZY].
- Missing: an equation that ties the numbers together (like `gval G + 6 + κ = Q` in `PR_SBC.v`) [P26 §3].
- Per Justus (25 Nov): Group 1 rests at this stage; the run beyond 10^22 may finish.

## M5 group: 318, 518, 322, 274

### Proved (Rocq)

Nothing.

Shown by **table comparison** (holds for every step count, two programs, not in Rocq) [M1 §1]:
- All four are the 5-state machine M5 `1RB0LD_0RC1RA_1RD1RE_1LA0LE_0RA0LC` with one state split.
  Halting patterns: 318 and 322 `B> 1 1`, 518 and 274 `C> 1 1`.
- Start in M5: 318/518 from A, 322 from C, 274 from D (mirrored). Runs from C and D coincide from step 11 / 25.
- Exactly these four in the 608 list; none in `decided`.

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| No halting pattern (`B> 1 1`, `C> 1 1`) | 10^10 steps (runs from A and from C) | 2 (`m5sim.c`, `zweitpruefung.go`) | [M1 §3] |
| 318, 518 and M5 in lockstep | 10^9 | 1 (`m5sim gleich`) | [M1 §1] |
| Counter rules 1 to 3 (binary counter of digits Z/D1/D2/D3, separators W) | 3·10^8 | cycle files from 2 programs byte-identical, rule check Python only | [M1 §2] |
| Run from A does not meet run from C | 3·10^8 (cycle starts) | 1 | [M1 §1] |
| Accelerated simulator agrees at all cycle starts (40,324 from A, 41,794 from C) | 10^10 | 2 (`m5schnell.py`, `m5sim hash`) | [M2 §1] |
| Only three large rebuilds: from A at 29,754,240, from C at 87,823 and 874,896,314 | 8·10^14 (local; beyond 10^10 only every 5,000th cycle re-checked) | 1 (+ samples) | [M2 §3] |
| 83 / 88 wall passages (pairs) per run, not rebuilds | 8·10^14 | 1 | [M2 §2] |

### Open

- Whether M5 reaches `B> 1 1` / `C> 1 1`: **open**. Beyond 10^10 the halting pattern was not checked [M2 §4].
- How a rebuild places the new digits (position and phase): no formula found, hence **no proof plan** [M2 §4].
- Next rebuild, if any, beyond 8·10^14; `m5sim` reaches about 10^15 [M2 §6].
- Templates in the pin would be `SBCv6a2.v` (compute the orbit) or `SOBLv3.v` (residue-class invariant); both
  need the missing rebuild map [M2 §5].
- Justus posted the M5 reduction in #bb6 (per project memory, 25 Nov).

## 396 with 88, 312, 449 (family F12)

### Proved (Rocq)

Nothing by us. External: busycoq PR #59 (head `f23281d`, open, **not merged**, not built by us) proves by its
title that 88, 312 and 449 halt [396 §1], [DA].

Shown by **table comparison** [VK, section F12]:
- After merging the halting state, the cores of 88, 312, 396, 449 agree **except for E1**; only 88 and 312
  share a core and run in lockstep.
- 396 halts only via F1; F is reached via B1 or E1 (`0RF`).

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| The visit law of PR #59 holds for 396 except the halting rule: `V(1011x) = 0001x` instead of halting; 396 halts only at `111` | all words up to length 12 after the block | 1 (`gesetz.py`, running the table) | [396 §3] |
| 88 and 396 equal round by round, not step by step | round 27 (about 1.57 million steps) simulated directly | 3 routes to the round model agree (`direkt.c` 27 rounds, `naiv.py` 34 rounds, `runde.c`) | [396 §4, §5] |
| 88 halts in round 161,211, as computed in PR #59 | – | 1 own (`runde.c`), run 45676623019 | [396 §4] |
| 396: no halt, only two 1011 events (rounds 161,211 and 194,647) | round 260,000 (word of 1,615,087 cells) | 1 for the long run (`runde.c`), run 45676623019 | [396 §4] |
| Visit-law family among all 608 (mirrored, all state pairs): exactly 88, **110**, 312, 396, 449, 587; 110 = 396 except `V(111x)`, round-identical until the first visit hits 111 | all words up to length 12; 27 rounds direct | 2 (`suche_a.py`, `suche_b.c`), identical | [FB] `analyse/besuchsgesetz.md` |

### Running

- Thread "396, part 2" (branch `claude/project-thread-pzp4s2`, not merged yet): backward analysis and a second
  program `runde_b.cpp`; Actions run 45688978145 (`lauf_396b`) is running. Final result still missing.

### Open

- Whether 396 halts, i.e. whether `111` ever appears: **open** [396 §6].
- 396 still has no busycoq PR and no cryptids file [DA].
- The halting proof of PR #59 does **not** transfer to 396 [396].

## Relationship map (all 608 holdouts)

### Proved (Rocq)

Nothing. Shown by **table comparison**, two programs (`karte_a.py`, `karte_b.c`, same 1,619 lines) [VK §3, §4]:
- 376 of 608 holdouts in **141 families**, almost all "same table, different start" (298 holdout pairs).
- **403 distinct tables** up to renaming and mirroring (498 without mirroring) [VK, result].
- 69 holdouts with a 5-state core; lockstep shown for 17 pairs, 2 of them holdout pairs (318/518, 88/312).
- busycoq `Eqv*.v` and cryptids `Equivalences.lean`: no holdout–holdout pairs [VK §1].

### Observed

| Observation | Bound | Programs | Source |
|---|---|---|---|
| 6 more pairs in lockstep (e.g. 69/543, 166/391, 190/394, 489/598), **unproven** | 10^9 | 1 (`divergenz.c`), sieve in `karte_b.c` up to 10^6 | [VK §3] |
| None of the 510 same-table pairings merges | 10^6 (B), 10^5 (A) | 2 | [VK §3] |
| 14 families now lie entirely in new busycoq PRs, e.g. F1 {244, 279, 339, 473, 489, 598}, F26 {38, 59, 124}; not F12, F20 (M5) or Group 1 | PR refs up to 119, as of 25 Nov | 2 | [DA] |

### Open

- F1: why d833 halts and what distinguishes the starts; FAR starts (d581, d1250, d653, d934) [VK §3, §6].
- Whether cryptids accelerations transfer to other starts of the same table [VK §6].

## Corrections (later wins)

| earlier | later | source |
|---|---|---|
| F12 = "the same 5-state machine", "second M5-like family" | cores agree only except E1; only 88 and 312 share a core | [VK], corrected in PR 13 |
| lockstep of 88/312 with equivalents of 396 / 449: direction swapped | 88/312 with 396.2/.3/.5/.7; 396 with 449.1/.2 | [VK], [396 §6] |
| "likely" that the PR #59 law also decides 396 | does not transfer; 396 does not halt at `1011` | [396] |
| number of distinct tables not stated | 403 (498 without mirroring) | [VK], addendum PR 13 |
| left end: "verdict (a) with reservation", "alt share not rising" (draft up to 10^15) | verdict open; alt share rises to 1.5 % | [LE §7] |
| "no template in the pin for a regular + counter invariant" | `verify/PR_SBC.v` (busycoq PR #26) is such a template | [VL §4], [P26] |
| Lemma K(C) without hypothesis | holds only for runs with blank tape right of the start (Justus' counterexample) | [VB §7] |
| halting condition part 2 (B/D reads 0 before `111`) vs part 3 (C before `111`) | equivalent, checked | [G1-3 §3, addendum] |
| 11 check points at the left end unexplained (27/39 steps after a left record) | explained: C meets separator `<1>`, 14 or 26 cells from the end | [G1-2] → [G1-3 §2] |
| "x/2 ≥ list length" in 24 of 76 cycles (start A) | 19 of 77 with a different cut; what matters is the spread −64 to +27 | [G1] → [VL §3] |
| M5: left record from C at 29,550,874 read as a rebuild | not a large rebuild; real rebuilds from C only at 87,823 and 874,896,314 | [M1] → [M2 §2, §3] |
| M5: "no further rebuild up to 10^11" | none up to 8·10^14 | [M1] → [M2] |
| cycle runs without int64 guard (runs 45675033053, 45682765314) | do not use beyond 10^24; guard since commit `509fb21` | [VB §5, §6] |

## Not included here

- Final results of "396, part 2" and of the run beyond 10^22 (both running).
- The thread "Invariant against K(C)" (side track, no report yet).
- Status from Discord (#bb6); only Justus checks there who works on what.
