# Relationship map of the BB(6) holdouts (short English summary)

Date 2026-11-25. Analysis only, no Rocq. Input: mxdys' holdout list of 2026-10-30 (608 machines),
its 695 equivalent machines (equivalence groups) and 846 decided machines, from a 2026-11-10 snapshot.
Full German report: `analyse/verwandtschaft.md`; data: `data/verwandtschaft.csv`, `analyse/verwandtschaft/familien.tsv`.

## Result

- **The 608 holdouts have 403 distinct transition tables** up to renaming of states and mirroring
  (start state ignored; 498 without mirroring). Two independent methods agree (canonical forms over all
  720 renamings x 2 mirrorings, and the pairwise "same table" links of the map).
- **376 of 608 holdouts have at least one relative on the list; they form 141 families** (72 of size 2,
  48 of size 3, 18 of size 4, 2 of size 5, 1 of size 6).
- Almost all links are **"same table, different start"** (up to renaming of states and mirroring):
  298 holdout pairs. None of these pairs has runs that merge within 10^6 steps each, so they are
  genuinely different halting questions on a shared transition table. No decision follows from the map.
- **Reduction to a smaller machine** (merging the halting state with a state that agrees on the other
  symbol): 69 holdouts reduce to a 5-state core. Shared core beyond "same table": M5 = {274, 318, 322, 518}
  (known). **Correction (2026-11-25):** an earlier version also listed {88, 312, 396, 449} as one shared core.
  That is wrong: after merging, their 5-state tables agree except for the transition E1 (88 and 312 share
  one core with E1 = `1RB`; 449 has E1 = `0LC`, 396 has E1 = `0RD`), and in 396 the halting state is a copy
  of D instead of B.
- **Lockstep from the blank tape until a halting transition**, proven by comparing tables:
  318/518 (known) and 88/312, plus 15 links via equivalent machines.
  **Unproven** (observed only: identical up to 10^9 steps by simulation, no proof): the 6 pairs 69/543,
  166/391, 190/394, 489/598, 244↔279, 339↔473.

## What was already recorded

| Source | Holdout–holdout relations |
|---|---|
| busycoq `verify/Eqv*.v` at pin `33209bc7` (3,596 `eqv` lemmas) | none; 236 lemmas touch a holdout, always paired with a machine off the list |
| cryptids `BusyBeaver/BB6/Equivalences.lean` (commit `f01ee56`) | none; its one equivalence pairs #470 with a member of its own equivalence group |
| mxdys' equivalence groups | none; no equivalent machine is itself a holdout |
| bbchallenge wiki redirects | 4 groups: {62,212,369,377}, {185,422,441,490,538}, {23,215,288,502}, {186,317,573}, all "same table" |

## Largest families

| Family | Holdouts | Relation | Class (community) | Note |
|---|---|---|---|---|
| F1 | 244, 339, 489 / 279, 473, 598 | table, core, lockstep (unproven, observed to 10^9) | Chaotic Bell 1 | two near-identical tables with three starts each; the table of 244/339/489, started from its own start, is decided machine #833, which **halts** (busycoq `ChaoticBell1Halt.v`) |
| F2 | 54, 200, 272, 545, 570 | table | Chaotic Bell 3 | five starts of one table |
| F3 | 185, 422, 441, 490, 538 | table | Chaotic 1dCA-like | known from the wiki; cryptids has an acceleration for 185 only |
| F12 | 88, 312, 396, 449 | core (equal except E1), lockstep | Shift-overflow counter | busycoq PR #59 (open) claims 88, 312, 449 halt ("one doubling law"); **396 is the only member without a PR**, and the PR's proof does not carry over to it (see `analyse/396.md`) |
| F20 | 274, 318, 322, 518 | core, lockstep, table | Shift-overflow structural counter | M5, known |

Same table as a decided machine (different start): 244/339/489 ~ #833 (halts); 66/438/532 ~ #581,
398/530 ~ #1250, 262 ~ #653, 527 ~ #934 (all non-halting by FAR). Nothing transfers automatically.

## Method and checks

Two independently written programs: A (Python; canonical forms, union-find congruence closure, product
automaton, exact tape copies) and B (C; pairwise BFS isomorphism, enumeration of all 203 partitions,
brute-force isomorphism of cores, rolling hash with exact re-check, simulation sieve). On all 2,149 machines
they agree line by line (1,619 lines). Positive controls (known groups, M5, a synthetic restart that merges
after one step), negative controls (three mutated machines must find nothing) and seven fault switches that
must break the agreement all behave as expected.

## Limits

Cores only cover exact transition-by-transition agreement. Mirrored lockstep cannot occur (all machines start
with `1RB`). Merging of runs was checked only up to 10^6 steps. PR/open status is from 2026-11-10.
