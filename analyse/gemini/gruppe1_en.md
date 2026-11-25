# Problem statement: BB(6) holdouts 114 / 367 / 378 (one 6-state table, three starts)

*Status 25 Nov 2026. Everything below is from simulation unless marked "proved". Nothing is decided.*

## Machines
- 114: `1RB---_0RC0LF_1LD0RE_1RC0LB_1RD1RA_1LB0LC` (start state A, blank tape).
- 367 and 378 are the same table, renamed (378 also mirrored), started in states D and C. So the
  question is: does table 114 halt from a blank tape when started in A, in D, or in C?
- The three runs do not merge (no common configuration found up to 10^9 steps).
- The only halting transition is A reading 1. A is entered only via E1, E only via C1, so
  **halt ⟺ state C reads 1 with `1 1` directly to its right ("C before 111")** (proved, by inspection).

## Observed behaviour
- Tape is almost everywhere period 3: left of the head blocks `011`, right of the head blocks `100`.
  Macro rules (proved as Rocq lemmas in our repo): `C> 100 → 011 C>`; `011 <B → <D 100`, `011 <D → <B 100`.
- Reading the tape left of the head as tokens `(t, n)` = separator bit t followed by `011^n`, the run is a
  list-rewriting system. A "phase" = one pendulum swing of the head. A 7-rule phase automaton (N1, N2,
  N2s, UA, LE, VS, LG) predicts 99.995 % of all phases exactly (checked against direct simulation up to
  10^12 steps). The main pair: N2 takes 1 from the left neighbour of the "frontier" token and makes the
  frontier `(0,k+2)`; N1 turns `(0,k)` (k even) into `(1,k+1)`. Net effect: the frontier walks left and
  every token it passes grows by 2.
- Cycles: the rightmost element "eats" its neighbour (`x | y → x+4 | y−1` for odd x, proved in Rocq), then x−1
  phases follow. Observed: phase count grows roughly like steps^(1/2), cycle count like steps^(1/4).
- The unexplained phases (0.005 %) all occur at the left tape end: 2,877 cases up to 10^17 in 13
  "core patterns"; new core patterns are rare but still appear (last one at 8.2·10^16).

## What is known about halting
- **Proved (short argument):** before any halt, C must step right onto a 0 that is followed by `1 1`
  (pattern `C> 0 1 1`). Reason: every 1 right of the head was written by C0 or F0 when the head last left
  that cell moving left; F is impossible here because F is only entered via B1, which writes 0 to its right.
- Observed: `C> 0 1 1` never occurs up to 10^9 (all three starts; two independent programs agree).
  The nearest events occur ~1.6 million times per 10^9 steps: the head arrives at exactly that cell
  with `0 1 1` to its right, but in state D instead of C (then it continues harmlessly to "C before 110").
- Halting has been checked at every single step only up to 10^12. Up to 10^17 an accelerator runs the
  phase automaton but checks halting only in the 0.005 % of phases it simulates in full.

## What is open (the actual question)
1. An invariant (e.g. a regular language of token lists / a closed set of configurations) that is
   preserved by all phases and excludes `C> 0 1 1`. Known failures: "all elements even" is not preserved;
   "at most one irregular group" fails at 16 of 232 cycle starts.
2. Or a reason why the left-end behaviour stays in finitely many parametrised rules.
3. Related class: busycoq `verify/PR_Loop4Mono.v` (same "Monotone list" class) proves machines that
   HALT after ~10^20 to 10^22 steps, so non-halting must not be assumed.

Question to you: what kind of invariant or acceleration argument would you try, given that the
dangerous event is a phase/alignment condition (arrival in state C instead of D at a `0 1 1` window)?
