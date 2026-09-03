# Package `v7-inflight-and-counts`

**Scope.** N3 (the paper describes a cancelled batch as live) and the eight failing corpus-count
checks in `analysis/c98_reproduce.py`. Written against **HEAD 17b9af7**, `results/all_runs.csv`
at **2,177 rows**. Nothing here was applied to `paper/paper.tex` or `paper/DRAFT-v4.md`; this
file carries the exact replacement text, keyed to anchors verified `count == 1` against the live
files. **75 keyed replacements: 40 in `paper.tex`, 35 in `DRAFT-v4.md`.**

---

## 0. Verification actually run (not asserted)

| what | how | result |
|---|---|---|
| the reversal, re-derived | `c99_hz3q_score.py --runs runs --probes runs/hz3 --qprobes runs/hz3`, **run UNEDITED**, on the cluster | H2 repaired **−0.238 ± 0.093, t −2.57, df 5 → `NOT FLAT`** |
| the scorer is the registered one | `shasum -a 256` on both copies; cluster copy `md5sum` identical | `c99` **50d95083c8…**, `c87` **0be1f5201d…** (the sha the paper already prints) |
| the scorer's own selftest | `c99_hz3q_score.py --selftest` | **59/59 PASS**, exit 0 |
| RULE 20 | `argsline_guard.py` over the four `hz3q` `.out` files | **4 clean, 0 repeated flags, VERDICT PASS** |
| non-overwrite | `c87_hz3_score.py --runs runs --probes runs/hz3`, **UNEDITED**, after the ingest | `grep -c hz3q` = **0**; verdicts unchanged (`SURVIVES`, `MECHANISM SURVIVES THE HORIZON`) |
| the trio really was cancelled | `sacct -j 4855960,4855961,4855962` | `CANCELLED by 2344`, **Elapsed 00:00:00**, Start `None`, NodeList `None assigned`, End `2026-09-03T00:01:32`; **no `.out` file exists for any of the three ids** |
| the quartet really was one submission on one card | `sacct -j 4864632..4864635` | all four `COMPLETED`, partition `gpu-l4-24g`, **Start `2026-09-03T00:00:53`**, **NodeList `node883`** for all four |
| every corpus count | re-derived from the 2,177-row CSV with `c98_figures.load()` | table in §2 below |
| the two upstream log counts | `find`/`grep -rl` on **both** cluster run directories | `runs` 1,326 / 1,322 `ARGS:` / 1,223 `ENV:`; `runs_alice2` 919 / 919 / 894 |
| the audit, end to end | patched literals + patched manuscripts, run in a scratch copy | **exit 0, ALL 565 CHECKS PASS** |
| the census fixpoint | `c98_reproduce.py` re-run to a fixpoint on the edited markups | **557 / 373 / 857 / 43.5%**, reached in one step and stable across two further runs |
| LaTeX | `tectonic -X compile paper.tex` on the edited file | exit 0, `paper.pdf` written, **two** overfull hboxes at 7.28 pt and 12.25 pt — the baseline's **third** (20.28 pt, `tab:inflight`) is **gone** |

---

## 1. N3 — what was stale, and what actually happened

The registered R2 was **three** jobs, `hz3-{ch,c23,n1d}-s5` (Slurm 4855960–62), pinned to
`gpu-2080ti-11g` so that seed 5's re-run would sit on the same GPU class as its **archived**
`nodewise` comparator. They never started: `sacct` records elapsed `00:00:00`, no node ever
assigned, and cancellation at `2026-09-03T00:01:32`. The queue's own start estimate for them stood
at roughly a week.

They were replaced by **four** jobs, `hz3q-{node,ch,n1d,c23}-s5` (Slurm 4864632–35), which
completed on one card (`node883`, an NVIDIA L4) in one submission — all four share a `Start` of
`2026-09-03T00:00:53` and a `NodeList` of `node883`.

**Why the redesign is better, stated as (b) asks — plainly, and without dressing the cause up as
foresight.** The registered trio was correct only under two conditions it did not control: that the
queue would deliver the pinned partition, and that the *archived* seed-5 `nodewise` run it leaned on
was what its metadata said it was. The quartet controls both by construction — it re-runs **all
four** arms, so box and GPU class are identical across the contrast whatever the scheduler does, and
the seed-5 `D` it delivers depends on no archived run at all. We changed the design because a
week-long queue made the registered one unaffordable. It happens also to be the better design, and
it buys one measurement the original could not make: because the quartet's class differs from seeds
0–4's, the batch carries an explicit cross-class control (HC) instead of assuming the class term
away, and that control puts the class term at **+0.134 pp on the level** against a registered bar of
1.00 pp.

**The cost, stated too.** `hz3q` does *not* make `hz3`'s archived seed-5 GPU-class label true — it
ran on an L4, not on the 2080 Ti the cancelled trio was pinned to. Two sites in §7 T9 said R2 would
make that label true; both are corrected to say what is actually the case: the archived label stays
wrong, and the quartet makes it *irrelevant to the contrast* rather than correct.

**Sites found.** The briefing listed eight; exhaustive search found **twenty-two** N3-touched sites
across the two files, including three the briefing did not name:

* `paper.tex:4392` / `DRAFT-v4.md:3511` — the §7 "experiments that would break the impasse"
  paragraph. **The two files disagreed with each other and both were wrong.** `paper.tex` said
  *"Two of the four … have been read"* and then listed **three**; `DRAFT-v4.md` said *"Two remain:
  … (R1, complete on disk and deliberately unscored) and … (R2, queued)"*, which contradicts its own
  `tab:inflight` row R1 (`SCORED — null REPLICATED`). Both now read **"All four … have now been
  read"**, and R1's stale "deliberately unscored" is deleted.
* `paper.tex:2628` / `DRAFT-v4.md:2078` — §4.8's own paragraph ends *"is registered and will settle
  it; until it lands this cell carries its sensitivity in the text."* R2 landed and did settle it,
  so this could not be left. **This block overlaps any dedicated flatness-reversal package: if one
  exists, reconcile there rather than applying **TEX-20 / MD-19** twice.**
* `paper.tex:4768` / `DRAFT-v4.md:3840` — §9's withdrawal list still reads *"a budget flatness claim
  demoted to an unresolved trend"*; on the repaired seed that trend **resolves**.

**One thing deliberately *not* changed.** The twenty batches that carry a count-matched contrast
still contribute **332 runs, of which 332 are admissible**. `hz3q` is a new batch and is not one of
them: it enters no cell of Table 2 (`c98_figures.arm()` matches on the prefix `hz3-ch` / `hz3-node`,
which `hz3q-…` does not satisfy), and per the registration it is not a replication, not a new design
point and not a new cell. The audit confirms this independently — every Table 2 cell, the pools and
the cell count (20) all still PASS unchanged.

---

## 2. The eight failing checks — every count re-derived from the 2,177-row CSV

`analysis/c98_reproduce.py` mirrors the manuscript's printed values as **literals**, so exit 0
requires the manuscript and those literals to be corrected *together*. The derivations below are the
authority; §3 gives the literal patch.

| quantity | derivation | was | **is** |
|---|---|---|---|
| rows in `results/all_runs.csv` | `len(rows)` | 2,173 | **2,177** |
| admissible rows | `len(adm)` | 1,731 | **1,735** |
| runs carrying a wallclock | non-empty `wallclock_min` | 2,158 | **2,162** |
| GPU-hours | Σ`wallclock_min`/60 = 98,493 min = **1,641.55 h** | 1,632 | **1,642** (`%.0f`), **1,641.5** in the ledger (`%.1f`) |
| admissible GPU-hours | Σ over `adm` = 94,512 min | 1,565.3 | **1,575.2** |
| excluded GPU-hours (the braced `66.3`) | 0.65 + 63.10 + 2.60 = 66.35 | 66.3 | **66.3, unchanged** — all four `hz3q` rows are admissible; and 1,641.5 − 1,575.2 = 66.3 closes exactly |
| admissible runs in the partition families | `granularity ∈ {nodewise, nodewise1d, chunk*, permnode*}` | 427 | **431** |
| …with meta = Lion | " | 415 | **419** |
| …with meta = RMSProp | " | 12 | **12, unchanged** |
| count-matched-family rows outside `rp1` | `chunk*`/`permnode*`/`nodewise1d`, not `rp1*` | 238 | **241** |
| …of which admissible | " | 238 | **241** |
| all count-matched-family rows | 241 outside `rp1` + 18 inside | 256 | **259** |
| distinct nodes | | 29 | **29, unchanged** |
| rows failing `window_ok` / `complete` / no `plateau5` | | 425 / 17 / 25 | **unchanged** — the four `hz3q` rows pass all three |
| the 442 inadmissible, by granularity | `layerwise` 136, `weightwise` 111, `nodewise` 108, `resnet18_blocks` 56, `scalar` 30, no-partition 1 | | **unchanged** |

**The attrition ledger's upstream rows, measured on the clusters** (the audit's stated scope excludes
these, so they were measured directly):

| stage | derivation | was | **is** |
|---|---|---|---|
| Slurm `.out` files on the two clusters | `find … -name '*.out' \| wc -l` → 1,326 + 919 | 2,241 | **2,245** |
| — infrastructure jobs, no training | the same four named files, still the only ones without `ARGS:` | −4 | **−4, unchanged** |
| **jobs that entered the training script** | `grep -rl '^ARGS:'` → 1,322 + 919 | 2,237 | **2,241** |
| — crashed or cancelled before epoch 1 | 2,241 − 2,177 | −64 | **−64, unchanged** |
| files carrying `ENV:` | `grep -rl '^ENV:'` → 1,223 + 894 | 2,113 | **2,117** |
| files without `ENV:` | 2,245 − 2,117 | 128 | **128, unchanged** |

The ledger closes exactly: **2,245 − 4 − 64 = 2,177**. The three cancelled trio jobs are correctly
absent from it — they produced no `.out` file, and the ledger reconciles *logs* against the run
table. Verified: `ls runs | grep -c 4855` = 0.

**Corpus counts the audit does not check but the manuscript prints** (all re-derived; leaving them
would have contradicted the corrected totals in the same paragraph):

| §3.1 quantity | was | **is** |
|---|---|---|
| CIFAR-10 rows (of 2,177) | 1,967 | **1,971** (CIFAR-100 **206**, unchanged) |
| ResNet-18 rows | 1,872 (1,667 C10) | **1,876 (1,671 C10)**; 188 C100 and 17 GN unchanged |
| ResNet-34 / -10 / -50 / -101 | 150 / 119 / 31 / 1 | **unchanged** |
| mini-batch size 100 in all N runs | 2,173 | **2,177** |
| augmentation on / off / unrecorded | 2,059 / 27 / 87 | **2,063** / 27 / 87 |
| augmentation on in the partition family | 534 of 535 | **538 of 539** |
| 300-epoch runs | 62 | **66** |
| 100-epoch / 20-epoch / other budgets | 1,614 / 392 / 105 | **unchanged** |
| §6.1 and §8: runs swept for a repeated flag | 2,237 | **2,241**; the **36** with a repeated flag is **unchanged** (`argsline_guard` returns 0 repeated flags on all four `hz3q` files) |
| §3.3: 1,735 vs the 1,724 of earlier versions | "7 higher … for one reason only" | **"11 higher … for two reasons"** — `rp1`'s 7 refreshed rows **and** the 4 `hz3q` rows |
| A.1's partition-family census in `paper.tex` | **420 / 408** — `paper.tex` and `DRAFT-v4.md` disagreed here before this package (md carried 427 / 415) | **431 / 419 in both** |
| A.8: the correction register | entry 131 | **entry 133** (this package writes 133; see §5) |
| §3.4 census triple | 557 / 372 / 849 / 43.8% | **557 / 373 / 857 / 43.5%** (fixpoint, §4) |

**One historical figure kept as history, with its scope made explicit.** §4.6.1's rp1-rebuild
sentence reads *"(2,173 rows in and out; 0 added, 0 removed, 8 changed …)"*. That measurement was
made on a 2,173-row table and is true of it; restating it as 2,177 would be false. It now reads
*"(the table then stood at 2,173 rows: 2,173 rows in and out; …)"*. Likewise §8's *"Earlier versions
of this paper read 249 of 256"* keeps its own denominator, now written as *"249 of the 256 such rows
the corpus then held"*.

---

## 3. The audit literals — apply these **with** the manuscript edits, never before

`c98_reproduce.py` compares each derived value against the value **the paper prints**, held as a
literal. The eight failures are the mirror going stale, not a derivation changing. No tolerance, no
predicate, no derivation and no check is touched below — only the eight mirrored paper values, each
set to the number re-derived in §2.

**Applying these alone would turn the audit green against a stale manuscript. Apply §6's blocks
first, or in the same commit.**

```diff
--- a/analysis/c98_reproduce.py
+++ b/analysis/c98_reproduce.py
@@ line 87
-    chk("rows in results/all_runs.csv", len(rows), 2173, "abstract, §8", "%.0f")
-    chk("admissible rows", len(adm), 1731, "§3.3, A.8", "%.0f")
+    chk("rows in results/all_runs.csv", len(rows), 2177, "abstract, §8", "%.0f")
+    chk("admissible rows", len(adm), 1735, "§3.3, A.8", "%.0f")
@@ line 90
-    chk("runs carrying a wallclock", len(wc), 2158, "§8", "%.0f")
-    chk("GPU-hours", sum(wc) / 60.0, 1632, "abstract, §8", "%.0f")
+    chk("runs carrying a wallclock", len(wc), 2162, "§8", "%.0f")
+    chk("GPU-hours", sum(wc) / 60.0, 1642, "abstract, §8", "%.0f")
@@ line 484
-    chk("admissible runs in the partition families", len(sel), 427,
+    chk("admissible runs in the partition families", len(sel), 431,
@@ line 486
-    chk("   ...with meta = Lion", sum(1 for r in sel if r["meta"] == "Lion"), 415,
+    chk("   ...with meta = Lion", sum(1 for r in sel if r["meta"] == "Lion"), 419,
@@ line 498
-    chk("count-matched-family rows outside the in-flight rp1 batch", len(norp), 238,
+    chk("count-matched-family rows outside the in-flight rp1 batch", len(norp), 241,
@@ line 500
-    chk("   ...of which admissible", sum(1 for r in norp if F.admissible(r)), 238,
+    chk("   ...of which admissible", sum(1 for r in norp if F.admissible(r)), 241,
```

Result, executed on a scratch copy carrying both these literals and every block in §6:
**exit 0, `ALL 565 CHECKS PASS`**, with `[7] BUDGET` running (it needs the `.out` mirror; set
`METAOPT_RUNS` if it reports `SECTION SKIPPED`, or the census will come out 546/366 and the §3.4
triple below will be wrong).

---

## 4. The §3.4 coverage census

The edits move the numeral pool, so §3.4's self-referential triple goes stale and the audit says so.
Re-iterated to a fixpoint on the edited markups, it is **557 assertion sites, 373 distinct
quantity-numerals asserted, 857 distinct quantity-numerals in the draft, 43.5%** — reached in one
step and unchanged over two further runs. The triple is carried in blocks **TEX-09** and **MD-09**.

**If any other package lands in the same commit, this triple must be re-iterated after it.** Run
`python3 analysis/c98_reproduce.py --census` and write the printed triple into §3.4 in both files
until the run comes back clean.

---

## 5. The pipeline trap — `docs/CORRECTIONS.md` entry **133**, and a guard

Both parts of item (d) are **already applied in the working tree** (they touch neither manuscript):

* **`docs/CORRECTIONS.md` § 133** — appended. The register now runs to **133**, which is what A.8's
  replacement text in blocks **TEX-37 / MD-32** prints. *If another package appends its own entry
  concurrently, renumber and set A.8 to the highest number at integration.*
* **`analysis/dup_group_guard.py`** — new file. It imports `args_repair.GROUPS` rather than
  restating the eighteen pairs, so it cannot drift from the repair it guards, and it asserts:
  every member of every pair stamped and stamped with the right group; **21 distinct `dup_group`s
  over 42 rows** (18 pairs + the 3 run-name collisions `aggregate.py` finds by itself); exactly 2
  members per group; and `superseded = 1` on exactly the 3 `a0` rows. On failure it exits 1 and
  prints the remediation command.

```
$ python3 analysis/dup_group_guard.py
dup_group_guard: all_runs.csv -- 21 groups, 42 rows stamped, 3 superseded. VERDICT: PASS   (exit 0)

$ python3 analysis/dup_group_guard.py --selftest
selftest: 5/5 PASS                                                                          (exit 0)
```

The selftest passes the live table and **fails** all four revert modes: a bare `aggregate.py`
rebuild (all 36 stamps wiped), a single lost stamp, a stamp rewritten to a wrong group, and an
invented supersession. The standing rule it enforces: **the ingest is `aggregate.py` THEN
`args_repair.py --apply`** — run alone, `aggregate.py` silently reverts the A3 repair and `ml2`'s
`se` falls 0.195 → 0.142 with `t` rising 2.34 → 3.20.

---

## 6. Two things the integrator must handle that this package cannot

1. **The deposit is stale, and three of the blocks below are false until it is rebuilt.** `release/`
   was built on 2026-09-02 from `ea9058b`: `release/data/all_runs.csv` holds **2,173** rows and
   `release/logs/raw_out.tar.gz` holds **2,241** members, while the clusters now hold **2,245**
   `.out` files and the run table **2,177** rows. Blocks **TEX-25, TEX-26, TEX-27, TEX-38** and
   **MD-24, MD-25, MD-33** print the *post-rebuild* counts (2,177 rows; 2,245 / 2,241 / 2,117 log files),
   because §8's own corrected scope is *"every `.out` file in the two clusters' Slurm run
   directories"* and that is now 2,245. **Rebuild the deposit before or with this integration**, then
   confirm `tar tzf release/logs/raw_out.tar.gz | wc -l` = 2,245 and
   `wc -l release/data/all_runs.csv` = 2,178. `release/` is untracked, so this is a build step, not a
   git operation. Re-derive the deposit's size from `head -1 release/MANIFEST.md5` afterwards — §8
   and the End matter both print **6.4 MB**, and that number moves with every build.
2. **One number in the R2 prose is not re-derivable after the fact:** the queue's ~one-week start
   estimate for jobs 4855960–62. Slurm keeps no record of a start estimate for a cancelled job, so
   `sacct` can confirm only that the three never started and were cancelled. The blocks below phrase
   it as *"the queue's own start estimate for them stood at roughly a week"* — an operator
   observation, deliberately not given a false precision. Everything else in those blocks is
   measured.

---

## 7. COLLISION NOTICE — `paper/sections/v7-budget-reversal.md`

That package appeared in `paper/sections/` while this one was being written, and it owns the
budget reversal proper. **Six of its anchors overlap six of mine.** Do not apply both at these
sites; reconcile once, then re-iterate the §3.4 triple (§4 above), because the winning text
changes the numeral pool.

| site | this package | `v7-budget-reversal` | note |
|---|---|---|---|
| §3.5, the R2 result paragraph | **MD-15** (md 977–983), **TEX-16** (tex 1231–1239) | md 977–983 | **identical range.** Mine also carries the RULE 20 discharge, the H0 both-directions gate, the HC control and the non-overwrite check; take whichever is fuller, not both |
| §4.8, the flatness paragraph | **MD-19** (md 2078–2088), **TEX-20** (tex 2628–2640) | md 2078–2090 | theirs is the wider range and this is their subject; **prefer theirs**, and check the result still says the three readings are reported together |
| §7 T9, "R2 makes the label true again" | **MD-22** (md 3064–3065), **TEX-23** (tex 3849–3850) | md 3064–3065 | identical range |
| §7 T9, the seed-5 outlier | **MD-23** (md 3077–3079), **TEX-24** (tex 3863–3866) | md 3073–3079 | theirs is wider |
| Table 2's † footnote | **MD-16** (md 1139), **TEX-17** (tex 1470) | md 1140–1141 | adjacent; check for a double edit |
| §7 impasse paragraph | **MD-30** (md 3511–3516) | md 3516–3517 | **mine is the one that fixes R1**, which that paragraph also gets wrong (`paper.tex` says "Two … have been read" and lists three; `DRAFT-v4.md` calls R1 "deliberately unscored" against its own table). Whichever text is taken must keep that repair |

Sites that package touches and this one does not — md 2064–2076, 2098–2100, 2120–2123, 2260–2261,
3454–3455, 3569–3571 — are outside this package's scope and are unaffected by anything here.

**One methodological note in its favour.** That package reports that `c99_hz3q_score.py`'s H1 box
gate cannot be evaluated from the local backup tree, because `runs/hz3/probe_*_hz3q_s5/` are empty
there. That is correct, and it is why the H1 figure quoted in §0 above — worst coordinate fraction
**exactly 0.000000** on `n = 500` per arm at epochs 100/200/300 — was taken from a run of the same
unedited scorer **on the cluster**, where the `probe.jsonl` records actually live. Any local
re-run of that gate will print `NO OCCUPANCY IS MEASURABLE` until the probe records are synced.

**Unrelated working-tree observation, not this package's doing.** `git status` shows
`results/all_runs.csv.pre-argsrepair-20260902-191705.bak` and `…-204301.bak` as deleted. This
package deleted nothing under `results/`; another agent removed them.


---

# KEYED REPLACEMENTS --- `paper/paper.tex`  (40 blocks)
Every ANCHOR below was verified `count == 1` against the live `paper/paper.tex` at HEAD 17b9af7. Line numbers are where the anchor sits in that file and are advisory; the anchor text is authoritative.

## TEX-01  lines 69--69

ANCHOR (count == 1)

```latex
artefact, patched only to add partitions. The sampling frame is a 2{,}173-run
```

REPLACE WITH

```latex
artefact, patched only to add partitions. The sampling frame is a 2{,}177-run
```

## TEX-02  lines 109--109

ANCHOR (count == 1)

```latex
that question up with 2{,}173 runs ($\approx$1{,}632 GPU-hours; 1{,}731 admissible) on CIFAR-10
```

REPLACE WITH

```latex
that question up with 2{,}177 runs ($\approx$1{,}642 GPU-hours; 1{,}735 admissible) on CIFAR-10
```

## TEX-03  lines 229--229

ANCHOR (count == 1)

```latex
once: of the 427 admissible runs in the partition families, 415 carry a \textbf{Lion}
```

REPLACE WITH

```latex
once: of the 431 admissible runs in the partition families, 419 carry a \textbf{Lion}
```

## TEX-04  lines 541--543

ANCHOR (count == 1)

```latex
partition anywhere in the project} (\S\ref{sec:metric}, \S\ref{sec:threats} T12). 1{,}967 of the
2{,}173 runs are CIFAR-10 and 206 are CIFAR-100. \textbf{Subject systems.} Networks are
instantiated by the parent release's \texttt{build\_network.py}: ResNet-18 on 1{,}872 rows (1{,}667
```

REPLACE WITH

```latex
partition anywhere in the project} (\S\ref{sec:metric}, \S\ref{sec:threats} T12). 1{,}971 of the
2{,}177 runs are CIFAR-10 and 206 are CIFAR-100. \textbf{Subject systems.} Networks are
instantiated by the parent release's \texttt{build\_network.py}: ResNet-18 on 1{,}876 rows (1{,}671
```

## TEX-05  lines 547--552

ANCHOR (count == 1)

```latex
\textbf{Training scenario.} Mini-batch size 100 in all 2{,}173 runs; one test-set evaluation after
every training epoch; augmentation is \texttt{RandomCrop(32, padding=4)} followed by a random
horizontal flip (\texttt{patches/patch\_augment.py}), recorded on in 2{,}059 rows, off in 27, and
unrecorded in 87 early rows --- and on in 534 of the 535 partition-family rows, the one exception
carrying no value in that column. \textbf{Budgets.} 100 epochs is the standard workload (1{,}614
runs); the budget ladder of \S\ref{sec:budget} extends it to 300 (62 runs); 392 runs are 20-epoch
```

REPLACE WITH

```latex
\textbf{Training scenario.} Mini-batch size 100 in all 2{,}177 runs; one test-set evaluation after
every training epoch; augmentation is \texttt{RandomCrop(32, padding=4)} followed by a random
horizontal flip (\texttt{patches/patch\_augment.py}), recorded on in 2{,}063 rows, off in 27, and
unrecorded in 87 early rows --- and on in 538 of the 539 partition-family rows, the one exception
carrying no value in that column. \textbf{Budgets.} 100 epochs is the standard workload (1{,}614
runs); the budget ladder of \S\ref{sec:budget} extends it to 300 (66 runs); 392 runs are 20-epoch
```

## TEX-06  lines 559--559

ANCHOR (count == 1)

```latex
RTX 2080 Ti 11 GB, A100 80 GB and A100 MIG 40 GB partitions; 1{,}632 GPU-hours over 29 nodes
```

REPLACE WITH

```latex
RTX 2080 Ti 11 GB, A100 80 GB and A100 MIG 40 GB partitions; 1{,}642 GPU-hours over 29 nodes
```

## TEX-07  lines 720--720

ANCHOR (count == 1)

```latex
redundant: \textbf{17 of 2{,}173 runs pass \texttt{window\_ok} while having completed under 95\%
```

REPLACE WITH

```latex
redundant: \textbf{17 of 2{,}177 runs pass \texttt{window\_ok} while having completed under 95\%
```

## TEX-08  lines 728--731

ANCHOR (count == 1)

```latex
inside the primary contrasts is zero. Of 2{,}173 rows, \textbf{1{,}731 are admissible}.
(This count is 7 higher than the 1{,}724 of earlier versions of this paper for one reason only: \arm{rp1}'s eight
mid-flight snapshot rows have been refreshed from the completed \texttt{.out} files, so seven of
them now pass the \texttt{complete} gate. No other row moved.)
```

REPLACE WITH

```latex
inside the primary contrasts is zero. Of 2{,}177 rows, \textbf{1{,}735 are admissible}.
(This count is 11 higher than the 1{,}724 of earlier versions of this paper for two reasons and no
others: \arm{rp1}'s eight mid-flight snapshot rows have been refreshed from the completed
\texttt{.out} files, so seven of them now pass the \texttt{complete} gate; and the four \arm{hz3q}
rows of \S\ref{sec:inflight} were ingested, all four admissible. No other row moved.)
```

## TEX-09  lines 1040--1041

ANCHOR (count == 1)

```latex
audit executes \textbf{557 claim-carrying assertions covering 372 of the 849 distinct
quantity-numerals} in this manuscript, which is 43.8\% of them. Those three figures are not
```

REPLACE WITH

```latex
audit executes \textbf{557 claim-carrying assertions covering 373 of the 857 distinct
quantity-numerals} in this manuscript, which is 43.5\% of them. Those three figures are not
```

## TEX-10  lines 1054--1054

ANCHOR (count == 1)

```latex
\subsection{Four pre-registered batches: three scored, one never started}
```

REPLACE WITH

```latex
\subsection{Four pre-registered batches: all four now scored, one after a forced redesign}
```

## TEX-11  lines 1058--1066

ANCHOR (count == 1)

```latex
are addressed by the four batches of Table~\ref{tab:inflight}, submitted while this paper was
being written. Three of the four ---
\arm{bm2}, \arm{sm4} and \arm{rp1} --- have since completed and been scored by running their
registered scorers \textbf{unedited}, and their verdicts are folded into \S\ref{sec:moderator},
\S\ref{sec:alignment}, \S\ref{sec:prescription}, \S\ref{sec:tail}, \S\ref{sec:normalisation} and
\S\ref{sec:threats}. One --- the \arm{hz3} seed-5 trio --- is not scored, and \textbf{no number
from it enters any claim in this paper}. The registrations are stated here in full regardless of
outcome, so that the decision rules are on the record ahead of the numbers, and so that a reader
can check that the three verdicts we did read are the ones we said we would read.
```

REPLACE WITH

```latex
are addressed by the four batches of Table~\ref{tab:inflight}, submitted while this paper was
being written. \textbf{All four} --- \arm{bm2}, \arm{sm4}, \arm{rp1} and the \arm{hz3} seed-5
repair --- have since been scored by running their registered scorers \textbf{unedited}, and their
verdicts are folded into \S\ref{sec:budget}, \S\ref{sec:moderator}, \S\ref{sec:alignment},
\S\ref{sec:prescription}, \S\ref{sec:tail}, \S\ref{sec:normalisation} and \S\ref{sec:threats}.
One of the four did not run in the form it was registered in: R2's three queued jobs were
cancelled before they started and were replaced by a four-arm batch, \arm{hz3q}, described below.
The registrations are stated here in full regardless of outcome, so that the decision rules are on
the record ahead of the numbers, and so that a reader can check that the four verdicts we read are
the ones we said we would read. \textbf{One of them reverses a sentence this project published},
and \S\ref{sec:budget} carries the reversal rather than burying it.
```

## TEX-12  lines 1078--1080

ANCHOR (count == 1)

```latex
\caption{The four pre-registered batches. Three have been scored by running their registered
scorers unedited; the fourth, the \arm{hz3} seed-5 trio, is queued and has never started and
contributes no number to this paper.}
```

REPLACE WITH

```latex
\caption{The four pre-registered batches. All four have now been scored by running their
registered scorers unedited. R2 is the exception in one respect only: the trio it registered was
cancelled before it started, and was replaced by the four-arm \arm{hz3q} batch, whose scorer was
committed before those runs existed and imports the same parent reader unedited.}
```

## TEX-13  lines 1089--1091

ANCHOR (count == 1)

```latex
R2 & \arm{hz3} seed-5 trio & 3 & the budget cell's clip-box and GPU-class mismatch
     (\S\ref{sec:budget}, \S\ref{sec:threats} T9) & \texttt{c87\_hz3\_score.py}, reused
     unedited & \textbf{queued, not started} \\
```

REPLACE WITH

```latex
R2 & \arm{hz3q} & 4 & the budget cell's clip-box and GPU-class mismatch
     (\S\ref{sec:budget}, \S\ref{sec:threats} T9); replaces the \arm{hz3} seed-5 trio, cancelled
     unstarted & \texttt{c99\_hz3q\_score.py} & \textbf{SCORED --- \texttt{NOT FLAT};
     flatness WITHDRAWN} \\
```

## TEX-14  lines 1126--1140

ANCHOR (count == 1)

```latex
\paragraph{R2 --- the \arm{hz3} seed-5 trio, re-run box- and hardware-matched.}
\arm{hz3-ch-s5}, \arm{hz3-c23-s5} and \arm{hz3-n1d-s5} re-run at 300 epochs in the batch's own
box $-30{:}9.0$ and pinned to the batch's own GPU class for seed 5 (RTX 2080 Ti), restoring a
matched 6 v 6 at every budget. Nothing else in \arm{hz3} is touched; its seed-5 \arm{nodewise}
partner is already in the right box. The composed argument line was verified byte-identical to
the original \arm{hz3-ch-s5} run's own \texttt{ARGS:} line modulo the partition flag, and the
box arithmetic was pre-registered: at
$\text{ms}\cdot T = 10^{-4} \times 300 \times 500 = 15.0$ nats of travel from
$\beta_0 = -6.907755$, $\beta$ is confined to $[-21.908, +8.092]$, so \textbf{both rails of
$-30{:}9.0$ are provably unreachable} while the superseded box's floor of $-15$ is reachable
from epoch 162 --- which is exactly what the probe records show happened
(\S\ref{sec:threats} T9). This batch changes the data the registered reader reads; it does not
change the reader. \texttt{analysis/c87\_hz3\_score.py} is reused \textbf{unedited}
(sha256 \texttt{0be1f5201d\ldots}, selftest 144/144 PASS) rather than a second scorer being
written, because writing one would create two registrations for one question.
```

REPLACE WITH

```latex
\paragraph{R2 --- the \arm{hz3} seed-5 repair: registered as a trio, delivered as a quartet.}
\emph{As registered.} \arm{hz3-ch-s5}, \arm{hz3-c23-s5} and \arm{hz3-n1d-s5} re-run at 300 epochs
in the batch's own box $-30{:}9.0$ and pinned to the batch's own GPU class for seed 5
(RTX 2080 Ti), restoring a matched 6 v 6 at every budget against the archived seed-5
\arm{nodewise} run, which is already in the right box.
\emph{What happened.} Those three jobs (Slurm 4855960--62) never started. They sat on
\texttt{gpu-2080ti-11g} with elapsed time \texttt{0:00} and no node ever assigned; the queue's own
start estimate for them stood at roughly a week, and we cancelled them rather than hold the paper
for it. No \texttt{.out} file exists for any of the three job ids, which is why they appear nowhere
in the attrition ledger of \S\ref{sec:repro}: that ledger reconciles logs against the run table,
and these three produced no log.
\emph{What we ran instead, and why the replacement is the better design.} \arm{hz3q}:
\emph{four} arms --- \arm{nodewise}, \arm{chunk777}, \arm{nodewise1d} and \arm{chunk2325} --- at
seed 5, 300 epochs, box $-30{:}9.0$, in \textbf{one} submission (Slurm 4864632--35) on
\textbf{one} card (\texttt{node883}, an NVIDIA L4 on \texttt{gpu-l4-24g}). The registered trio
matched an \emph{archived} comparator by pinning a partition, so it was correct only if the queue
delivered that partition and only if the archived run it leaned on was what its metadata said. The
quartet generates its comparator inside itself: box and GPU class are identical across the four
arms \textbf{by construction}, and the seed-5 contrast depends on no archived run at all. We
changed the design because a week-long queue made the registered one unaffordable, and we say that
rather than present the redesign as foresight; it is nonetheless the better design, and it buys a
measurement the original could not make (HC below). Its one cost is that the quartet sits on a
different GPU class from seeds 0--4, which is exactly why that control is carried.
\emph{The registration.} Under STANDING RULE 21, \texttt{analysis/c99\_hz3q\_score.py} (sha256
\texttt{50d95083c8\ldots}, selftest 59/59 PASS) was committed \textbf{before the runs existed}, and
it writes no reader of its own: it imports \texttt{analysis/c87\_hz3\_score.py} (sha256
\texttt{0be1f5201d\ldots}) \textbf{unedited} under STANDING RULE 16, so the quartet changes the data
the registered reader reads and not the reader. Its flatness bar, $|t| < 2.0$, is frozen in
\texttt{band\_flat()} and predates the runs. The box arithmetic is unchanged from the registration:
at $\text{ms}\cdot T = 10^{-4} \times 300 \times 500 = 15.0$ nats of travel from
$\beta_0 = -6.907755$, $\beta$ is confined to $[-21.908, +8.092]$, so \textbf{both rails of
$-30{:}9.0$ are provably unreachable}, while the superseded box's floor of $-15$ is reachable from
epoch 162 --- which is what the probe records show happened (\S\ref{sec:threats} T9). The gate
measures that rather than asserting it: the worst coordinate fraction over all four arms at epochs
100, 200 and 300 is \textbf{exactly $0.000000$} on $n = 500$ coordinates per arm, against a
registered bar of $0.05$.
```

## TEX-15  lines 1206--1207

ANCHOR (count == 1)

```latex
changed exactly those eight rows and \textbf{no other row in the corpus} (2{,}173 rows in and
out; 0 added, 0 removed, 8 changed, 0 of them outside \arm{rp1}).
```

REPLACE WITH

```latex
changed exactly those eight rows and \textbf{no other row in the corpus} (the table then stood at
2{,}173 rows: 2{,}173 in and out; 0 added, 0 removed, 8 changed, 0 of them outside \arm{rp1}).
```

## TEX-16  lines 1231--1239

ANCHOR (count == 1)

```latex
\textbf{R2 is still queued and has never started.} The three seed-5 jobs (\arm{hz3-ch-s5},
\arm{hz3-c23-s5}, \arm{hz3-n1d-s5}) sit \texttt{PENDING} with elapsed time \texttt{0:00} and no
assigned start time, on the same congested partition on which the original \arm{hz3} seed-3 and
seed-4 runs waited 16 and 23 hours, so a wait is expected rather than anomalous. No \texttt{.out}
file exists for any of the three job ids, so STANDING RULE 20's post-launch ARGS check
\textbf{remains owed} and cannot be discharged yet; it is owed the moment they start, and the batch
is to be cancelled on any \texttt{BETA\_CLIP} mismatch. Until they run, the box-matched 6 v 6 at 300
epochs does not exist and \textbf{\S\ref{sec:budget}'s budget verdict is unchanged}.

```

REPLACE WITH

```latex
\textbf{R2 landed, and it reversed a sentence.} The quartet completed and was scored by running
\texttt{c99\_hz3q\_score.py} \textbf{unedited}. Its provenance gate H0 reads node, GPU model and
\texttt{BETA\_CLIP} off each run's own header rather than from any declaration, and passes: all
four arms \texttt{node883}, \texttt{NVIDIA L4}, $-30{:}9.0$, seed 5, 300 epochs. Turned on the
archive it repairs, the same gate \textbf{refuses} it --- those four runs carry two GPU models and
two clip boxes --- so the gate is shown to cut in both directions before a number is read. STANDING
RULE 20 is discharged on all four \texttt{.out} files: \texttt{analysis/argsline\_guard.py} returns
\textbf{4 clean, 0 with a repeated flag or a design mismatch, VERDICT PASS}.

\textbf{The primary, H2: is $\Dstat$ flat from 100 to 300 epochs?} Paired within seed on \plateau{},
the registered reader returns three readings and the scorer prints all three. \arm{hz3} as
published, six archived seeds: $\mathbf{-0.149 \pm 0.105}$, $t\ -1.42$ --- \texttt{FLAT}. \arm{hz3}
with seed 5 dropped, five seeds: $\mathbf{-0.207 \pm 0.107}$, $t\ -1.94$ --- \texttt{FLAT}.
\textbf{Repaired}, archived seeds 0--4 plus \arm{hz3q}'s seed 5: $\mathbf{-0.238 \pm 0.093}$,
$t\ -2.57$, $df\ 5$ --- \textbf{\texttt{NOT FLAT}, and the sign names the direction: $\Dstat$
declines with budget.} The project record's sentence ``$\Dstat$ is present and resolved at a
$3\times$ budget and is statistically flat from 100 to 300 epochs'' does not stand on the repaired
data and is \textbf{withdrawn}. All three readings are reported together, always: the repaired one
does not replace the published one in the record, it is the disclosed repair of the one seed whose
contrast was cross-box and cross-class. \textbf{The gap itself is untouched.} Repaired,
$\Dstat(300) = +0.394 \pm 0.093$, $t\ 4.25$, against the published $+0.428 \pm 0.086$, $t\ 4.94$;
$\Gstat(300) = -0.048$ against $-0.057$. $\Dstat$ shrinks as the budget grows; it does not vanish,
and no cell of Table~\ref{tab:D} moves.

\textbf{HC, the cross-class control --- reporting, not gating.} \arm{hz3q-node-s5} on the L4 reads
\plateau{}$(300) = 92.908$; the archived \arm{hz3-node-s5} on the RTX 2080 Ti reads $92.774$. Same
seed, same box, same flags, same code; only the GPU class differs. $\Delta = +0.134$ pp against a
registered bar of $|\Delta| \le 1.00$ pp: \textbf{GPU class is not first-order on the level.} This
is a measurement \arm{hz3}'s own design --- which assigns GPU class as a function of seed --- could
never make. It decides what this paper may say about \arm{hz3}'s \emph{levels}; it does not touch
$\Dstat$, which is a within-seed, within-class contrast in both batches.

\textbf{The non-overwrite check, which is not optional.} \arm{hz3q} adds rows; it overwrites
nothing. \texttt{c87\_hz3\_score.py} was re-run \textbf{unedited} after the ingest, its output
contains the string \texttt{hz3q} \textbf{zero} times --- its own glob predicate rejects every
\arm{hz3q} file name, and \arm{hz3q}'s probe directories are disjoint from \arm{hz3}'s --- and its
verdicts are unchanged (\texttt{SURVIVES} on the primary, \texttt{MECHANISM SURVIVES THE HORIZON}
on the secondary). The four \arm{hz3q} rows enter \texttt{results/all\_runs.csv} with no
\texttt{dup\_group} and no supersession, and they enter no cell of Table~\ref{tab:D}. \arm{hz3q}
repairs one seed of one batch: it is not a replication, not a new design point and not a new cell,
and it is counted as none of them.
```

## TEX-17  lines 1470--1470

ANCHOR (count == 1)

```latex
a 0.086 pp $\se$. Run R2 (\S\ref{sec:inflight}) restores a matched 6 v 6.
```

REPLACE WITH

```latex
a 0.086 pp $\se$. The \arm{hz3q} quartet of \S\ref{sec:inflight} (R2) re-runs seed 5 box- and
class-matched, but it is a separate batch under a separate registration and does not enter this
cell, whose reading is unchanged; the repaired 6 v 6 is read off the \texttt{.out} series in
\S\ref{sec:budget}.
```

## TEX-18  lines 1512--1518

ANCHOR (count == 1)

```latex
of the 2{,}173 runs, every batch that ever ran a \arm{nodewise} arm alongside a count-matched
uniform-chunk arm is one of these twenty-two (the twenty above, \arm{gn1}-GroupNorm, and
\arm{ar1}), and every other batch carrying a \arm{nodewise} arm has no arm to match it against.
The enumeration also shows that no such cell could have been lost to the admissibility gate: all
256 uniform-chunk, \arm{nodewise1d} and \arm{permnode} runs in the corpus --- 238 of them outside
\arm{rp1}, and now all 18 of \arm{rp1}'s \arm{permnode} rows as well --- are admissible, and the
twenty batches involved contribute 332 runs of which 332 are admissible
```

REPLACE WITH

```latex
of the 2{,}177 runs, every batch that ever ran a \arm{nodewise} arm alongside a count-matched
uniform-chunk arm is one of these twenty-two (the twenty above, \arm{gn1}-GroupNorm, and
\arm{ar1}), and every other batch carrying a \arm{nodewise} arm has no arm to match it against.
The enumeration also shows that no such cell could have been lost to the admissibility gate: all
259 uniform-chunk, \arm{nodewise1d} and \arm{permnode} runs in the corpus --- 241 of them outside
\arm{rp1}, and now all 18 of \arm{rp1}'s \arm{permnode} rows as well --- are admissible, and the
twenty batches involved contribute 332 runs of which 332 are admissible
```

## TEX-19  lines 2420--2421

ANCHOR (count == 1)

```latex
$^{\ddagger}$ \arm{hz3} matched at 5 v 5 (seed-5 trio excluded for the clip-box and hardware
mismatch of \S\ref{sec:threats} T9): $\mathbf{+0.328 \pm 0.084}$, $t\ 3.89$.
```

REPLACE WITH

```latex
$^{\ddagger}$ \arm{hz3} matched at 5 v 5 (seed-5 trio excluded for the clip-box and hardware
mismatch of \S\ref{sec:threats} T9): $\mathbf{+0.328 \pm 0.084}$, $t\ 3.89$. The \arm{hz3q}
quartet of \S\ref{sec:inflight} repairs that seed but is a separate registration and enters no
pool here.
```

## TEX-20  lines 2628--2640

ANCHOR (count == 1)

```latex
\textbf{The trend is not robust, and we do not claim it.} Within-run,
$\Dstat(300) - \Dstat(100) = \mathbf{-0.149 \pm 0.105}$, $t\ -1.42$ over all six seeds and
$\mathbf{-0.207 \pm 0.107}$, $t\ -1.94$ over the five clean ones. Neither resolves at
$|t| \ge 2$, but the second is close enough that the difference matters, so we say where it comes
from: 76\% of the shift is at the \textbf{100-epoch} end (the six-seed $\Dstat(100)$ rises by
0.086 pp when seed 5 is removed, against 0.027 pp at 300 epochs), and seed 5's low
$\Dstat(100)$ is \textbf{not} explained by either defect --- the clip box is provably inert
before epoch 162, and the hardware term (\S\ref{sec:variance}) points the other way. It is an
unexplained extreme value in an $n = 6$ cell. The honest statement is therefore the weaker one:
\textbf{$\Dstat$ does not grow with budget from 100 to 300 epochs, and we cannot resolve whether
it decays.} We do not report flatness as a result. A box- and hardware-matched replacement trio
(R2, \S\ref{sec:inflight}) is registered and will settle it; until it lands this cell carries its
sensitivity in the text.
```

REPLACE WITH

```latex
\textbf{The trend was not resolved as published; on the repaired seed set it resolves, and it
resolves downward.} Within-run and as published,
$\Dstat(300) - \Dstat(100) = \mathbf{-0.149 \pm 0.105}$, $t\ -1.42$ over all six seeds and
$\mathbf{-0.207 \pm 0.107}$, $t\ -1.94$ over the five clean ones; neither crosses $|t| \ge 2$.
Seed 5 entered both of those readings on a run that sat in a narrower clip box and on a different
GPU class from its own comparator (\S\ref{sec:threats} T9), and the \arm{hz3q} quartet of
\S\ref{sec:inflight} re-runs that seed with all four arms in one submission on one card. On the
repaired seed set --- the five clean archived seeds plus \arm{hz3q}'s seed 5 --- the same
registered reader returns $\mathbf{-0.238 \pm 0.093}$, $t\ -2.57$, $df\ 5$, which crosses the
$|t| \ge 2$ bar that \texttt{c99\_hz3q\_score.py} froze in \texttt{band\_flat()} before the quartet
existed: \textbf{\texttt{NOT FLAT} --- $\Dstat$ declines with budget.} We report all three readings
together and always; the repaired one does not replace the published one in the record, it is the
disclosed repair of the one seed whose contrast was cross-box and cross-class. \textbf{What does
not change is the gap.} Repaired, $\Dstat(300) = +0.394 \pm 0.093$, $t\ 4.25$, against the
published $+0.428 \pm 0.086$, $t\ 4.94$: $\Dstat$ shrinks as the budget grows and it does not
disappear. Where the shift sits is worth stating, because it is not where the published readings
put it: as published, 76\% of the $-0.149$ to $-0.207$ move was at the \textbf{100-epoch} end (the
six-seed $\Dstat(100)$ rises by 0.086 pp when seed 5 is removed, against 0.027 pp at 300 epochs),
and the repaired seed reproduces that end rather than the archived outlier ---
$\Dstat(100) = +0.482$ against the archive's $+0.148$ (\S\ref{sec:threats} T9). Table~\ref{tab:D}'s
\arm{hz3} cell is a separate, CSV-based reading of a separate registration and is unmoved by any of
this.
```

## TEX-21  lines 3525--3525

ANCHOR (count == 1)

```latex
over the 2{,}237 runs carrying an \texttt{ARGS:} line on both clusters, exactly \textbf{36 carry a
```

REPLACE WITH

```latex
over the 2{,}241 runs carrying an \texttt{ARGS:} line on both clusters, exactly \textbf{36 carry a
```

## TEX-22  lines 3666--3668

ANCHOR (count == 1)

```latex
\arm{nodewise1d}, \arm{chunk*} or \arm{permnode*}. There are \textbf{427} of them, of which
\textbf{415 are meta $=$ Lion and 12 are meta $=$ RMSProp}; the twelve are \arm{sm4}. Before
\arm{sm4} the count was 415 of 415. (An earlier version of this paper quoted ``367 of 367'' here.
```

REPLACE WITH

```latex
\arm{nodewise1d}, \arm{chunk*} or \arm{permnode*}. There are \textbf{431} of them, of which
\textbf{419 are meta $=$ Lion and 12 are meta $=$ RMSProp}; the twelve are \arm{sm4}. Absent
\arm{sm4} the census reads 419 of 419. (An earlier version of this paper quoted ``367 of 367'' here.
```

## TEX-23  lines 3849--3850

ANCHOR (count == 1)

```latex
file-freeze rule we do not edit a registered scorer after its data exist, so the correction is
recorded here, and R2 makes the label true again.
```

REPLACE WITH

```latex
file-freeze rule we do not edit a registered scorer after its data exist, so the correction is
recorded here. \textbf{R2 does not make that label true.} The replacement quartet ran on an NVIDIA
L4, not on the RTX 2080 Ti the cancelled trio was pinned to, so \arm{hz3}'s archived seed-5 label
is wrong and stays wrong. What the quartet does is make the label \emph{irrelevant} to the
contrast: its four arms share one card, so the seed-5 $\Dstat$ it delivers is within-class whatever
that class is, and its HC control measures the class term directly at $+0.134$ pp on the level
(\S\ref{sec:inflight}).
```

## TEX-24  lines 3863--3866

ANCHOR (count == 1)

```latex
the hardware term (\S\ref{sec:variance}: A100 $-$ 2080 Ti $= +0.112$ pp) sits on the arm that would
\emph{inflate} $\Dstat$, not deflate it. The 100-epoch outlier is unexplained. \S\ref{sec:budget}
reports the budget contrast both with and without seed 5 for this reason, and a replacement seed-5
trio in the original box and on matched hardware is R2 (\S\ref{sec:inflight}).
```

REPLACE WITH

```latex
the hardware term (\S\ref{sec:variance}: A100 $-$ 2080 Ti $= +0.112$ pp) sits on the arm that would
\emph{inflate} $\Dstat$, not deflate it. The 100-epoch outlier is unexplained --- and it did not
reproduce. \arm{hz3q}'s box- and class-matched seed 5 returns $\Dstat(100) = +0.482$, close to
though still below the five archived seeds' range of $+0.548$ to $+0.990$, against the archived
$+0.148$. We do not attribute that 0.334 pp: the box is provably inert at 100 epochs, so only GPU
class and run-to-run nondeterminism remain, and the cross-class control puts the class term at
$+0.134$ pp on a \emph{level}, which is both too small and, being common to the two arms, largely
cancelled inside $\Dstat$. \S\ref{sec:budget} reports the budget contrast as published, without
seed 5, and repaired, for this reason, and the replacement batch is R2 (\S\ref{sec:inflight}).
```

## TEX-25  lines 4034--4034

ANCHOR (count == 1)

```latex
\texttt{data/all\_runs.csv}, 2{,}173 rows, one per run, with the full configuration (network,
```

REPLACE WITH

```latex
\texttt{data/all\_runs.csv}, 2{,}177 rows, one per run, with the full configuration (network,
```

## TEX-26  lines 4046--4053

ANCHOR (count == 1)

```latex
\texttt{logs/raw\_out.tar.gz}. The shipped log set is \textbf{2{,}241 files, which is every
\texttt{.out} file in the two clusters' Slurm run directories} (1{,}322 and 919).
\textbf{Neither provenance line is universal, and these are the counts.} \textbf{2{,}237} of the
2{,}241 carry their own \texttt{ARGS:} line --- the \textbf{four} that do not are infrastructure
jobs that ran no training (\texttt{gtest}, \texttt{gtest2}, \texttt{mo-smoke},
\texttt{ts-pretok}) --- and \textbf{2{,}113} carry their own \texttt{ENV:} line, so \textbf{128
do not}: those four plus 124 that carry \texttt{ARGS:} without \texttt{ENV:} (103 on the first
account, 25 on the second). The \texttt{ENV:} line was added to the submission template partway
```

REPLACE WITH

```latex
\texttt{logs/raw\_out.tar.gz}. The shipped log set is \textbf{2{,}245 files, which is every
\texttt{.out} file in the two clusters' Slurm run directories} (1{,}326 and 919).
\textbf{Neither provenance line is universal, and these are the counts.} \textbf{2{,}241} of the
2{,}245 carry their own \texttt{ARGS:} line --- the \textbf{four} that do not are infrastructure
jobs that ran no training (\texttt{gtest}, \texttt{gtest2}, \texttt{mo-smoke},
\texttt{ts-pretok}) --- and \textbf{2{,}117} carry their own \texttt{ENV:} line, so \textbf{128
do not}: those four plus 124 that carry \texttt{ARGS:} without \texttt{ENV:} (103 on the first
account, 25 on the second). The \texttt{ENV:} line was added to the submission template partway
```

## TEX-27  lines 4056--4056

ANCHOR (count == 1)

```latex
authority on what that run actually did, and RULE 20 is enforced on all 2{,}237 \texttt{ARGS:}
```

REPLACE WITH

```latex
authority on what that run actually did, and RULE 20 is enforced on all 2{,}241 \texttt{ARGS:}
```

## TEX-28  lines 4077--4077

ANCHOR (count == 1)

```latex
Slurm \texttt{.out} files on the two clusters & 2{,}241 & --- &
```

REPLACE WITH

```latex
Slurm \texttt{.out} files on the two clusters & 2{,}245 & --- &
```

## TEX-29  lines 4081--4081

ANCHOR (count == 1)

```latex
\textbf{jobs that entered the training script} & \textbf{2{,}237} & --- &
```

REPLACE WITH

```latex
\textbf{jobs that entered the training script} & \textbf{2{,}241} & --- &
```

## TEX-30  lines 4085--4086

ANCHOR (count == 1)

```latex
\textbf{rows in \texttt{results/all\_runs.csv}} & \textbf{2{,}173} & 1{,}631.7 &
  2{,}158 carry a wallclock \\
```

REPLACE WITH

```latex
\textbf{rows in \texttt{results/all\_runs.csv}} & \textbf{2{,}177} & 1{,}641.5 &
  2{,}162 carry a wallclock \\
```

## TEX-31  lines 4093--4093

ANCHOR (count == 1)

```latex
\textbf{admissible} & \textbf{1{,}731} & 1{,}565.3 & the gate of Eq.~\ref{eq:adm} \\
```

REPLACE WITH

```latex
\textbf{admissible} & \textbf{1{,}735} & 1{,}575.2 & the gate of Eq.~\ref{eq:adm} \\
```

## TEX-32  lines 4145--4147

ANCHOR (count == 1)

```latex
\textbf{256 of 256}, \arm{rp1} included
--- is admissible, so no count-matched cell could have been lost to the gate even in principle.
(Earlier versions of this paper read 249 of 256, the seven exceptions being \arm{rp1}'s mid-flight snapshots;
```

REPLACE WITH

```latex
\textbf{259 of 259}, \arm{rp1} included
--- is admissible, so no count-matched cell could have been lost to the gate even in principle.
(Earlier versions of this paper read 249 of the 256 such rows the corpus then held, the seven
exceptions being \arm{rp1}'s mid-flight snapshots;
```

## TEX-33  lines 4160--4160

ANCHOR (count == 1)

```latex
2{,}158 runs carry a wallclock; they total \textbf{1{,}632 GPU-hours} over 29 distinct nodes and
```

REPLACE WITH

```latex
2{,}162 runs carry a wallclock; they total \textbf{1{,}642 GPU-hours} over 29 distinct nodes and
```

## TEX-34  lines 4290--4290

ANCHOR (count == 1)

```latex
therefore run a different experiment from the one it declares. Over the 2{,}237 runs carrying an
```

REPLACE WITH

```latex
therefore run a different experiment from the one it declares. Over the 2{,}241 runs carrying an
```

## TEX-35  lines 4392--4398

ANCHOR (count == 1)

```latex
\textbf{The experiments that would break the impasse}, in the order we would run them. Two of the
four registered in \S\ref{sec:inflight} have been read: R3, the base-moderator replication at fresh
seeds, which replicated both levels and is in \S\ref{sec:moderator}; R4, the second-moment
corner, which refuted its mechanism and is in \S\ref{sec:normalisation}; and R1, the alignment
replication with the permutation seed decoupled, which replicated the null at twice the power and
is in \S\ref{sec:alignment}. One remains: the box- and hardware-matched budget trio (R2, queued and
not yet started). To those we add two experiments the
```

REPLACE WITH

```latex
\textbf{The experiments that would break the impasse}, in the order we would run them. \textbf{All
four} registered in \S\ref{sec:inflight} have now been read: R3, the base-moderator replication at
fresh seeds, which replicated both levels and is in \S\ref{sec:moderator}; R4, the second-moment
corner, which refuted its mechanism and is in \S\ref{sec:normalisation}; R1, the alignment
replication with the permutation seed decoupled, which replicated the null at twice the power and
is in \S\ref{sec:alignment}; and R2, the seed-5 budget repair, whose registered trio was cancelled
unstarted and whose replacement quartet returned \texttt{NOT FLAT} and withdrew a flatness
sentence (\S\ref{sec:budget}). None of the four is outstanding. To those we add two experiments the
```

## TEX-36  lines 4446--4447

ANCHOR (count == 1)

```latex
and the one batch that varies the meta-optimiser is a single cell: of the 420 admissible runs in
the partition families, 408 are meta $=$ Lion and 12 are meta $=$ RMSProp. \textbf{One cell is not
```

REPLACE WITH

```latex
and the one batch that varies the meta-optimiser is a single cell: of the 431 admissible runs in
the partition families, 419 are meta $=$ Lion and 12 are meta $=$ RMSProp. \textbf{One cell is not
```

## TEX-37  lines 4556--4560

ANCHOR (count == 1)

```latex
The record variously says 1{,}960 / 2{,}077 / 2{,}113 runs and $\sim$1{,}200--1{,}400 GPU-hours. At
write time: \textbf{2{,}173 rows, 1{,}731 admissible, 1{,}632 GPU-hours} summed over the 2{,}158 runs
carrying a wallclock, with 2{,}237 jobs having entered the training script and nothing awaiting
ingest (\S\ref{sec:repro}, Table~\ref{tab:attrition}). The correction register runs to
entry 131.
```

REPLACE WITH

```latex
The record variously says 1{,}960 / 2{,}077 / 2{,}113 runs and $\sim$1{,}200--1{,}400 GPU-hours. At
write time: \textbf{2{,}177 rows, 1{,}735 admissible, 1{,}642 GPU-hours} summed over the 2{,}162 runs
carrying a wallclock, with 2{,}241 jobs having entered the training script and nothing awaiting
ingest --- the last batch to land, the \arm{hz3q} quartet of \S\ref{sec:inflight}, is scored and its
four rows are in the table (\S\ref{sec:repro}, Table~\ref{tab:attrition}). The correction register
runs to entry 133.
```

## TEX-38  lines 4652--4654

ANCHOR (count == 1)

```latex
The complete run table (\texttt{results/all\_runs.csv}, 2{,}173 rows), the raw per-epoch Slurm logs
(2{,}241 \texttt{.out} files, of which 2{,}237 carry their own \texttt{ARGS:} line and
2{,}113 their own \texttt{ENV:} line; \S\ref{sec:repro} itemises the exceptions), all
```

REPLACE WITH

```latex
The complete run table (\texttt{results/all\_runs.csv}, 2{,}177 rows), the raw per-epoch Slurm logs
(2{,}245 \texttt{.out} files, of which 2{,}241 carry their own \texttt{ARGS:} line and
2{,}117 their own \texttt{ENV:} line; \S\ref{sec:repro} itemises the exceptions), all
```

## TEX-39  lines 4740--4740

ANCHOR (count == 1)

```latex
MetaOptimize implementation), Validation, Formal analysis, Investigation (all 2{,}173 runs), Data
```

REPLACE WITH

```latex
MetaOptimize implementation), Validation, Formal analysis, Investigation (all 2{,}177 runs), Data
```

## TEX-40  lines 4768--4769

ANCHOR (count == 1)

```latex
registered scorer refuses to compute the contrast it rested on, a budget flatness claim demoted to
an unresolved trend, and a variance claim that did not reproduce --- and two whole batches were
```

REPLACE WITH

```latex
registered scorer refuses to compute the contrast it rested on, a budget flatness claim demoted to
an unresolved trend and then, on a repaired seed, resolved as a decline, and a variance claim that
did not reproduce --- and two whole batches were
```


---

# KEYED REPLACEMENTS --- `paper/DRAFT-v4.md`  (35 blocks)
Every ANCHOR below was verified `count == 1` against the live `paper/DRAFT-v4.md` at HEAD 17b9af7. Line numbers are where the anchor sits in that file and are advisory; the anchor text is authoritative.

## MD-01  lines 15--15

ANCHOR (count == 1)

```markdown
released artefact, patched only to add partitions. The sampling frame is a 2,173-run
```

REPLACE WITH

```markdown
released artefact, patched only to add partitions. The sampling frame is a 2,177-run
```

## MD-02  lines 52--52

ANCHOR (count == 1)

```markdown
question up with 2,173 runs (≈1,632 GPU-hours; 1,731 admissible) on CIFAR-10 and CIFAR-100 —
```

REPLACE WITH

```markdown
question up with 2,177 runs (≈1,642 GPU-hours; 1,735 admissible) on CIFAR-10 and CIFAR-100 —
```

## MD-03  lines 149--149

ANCHOR (count == 1)

```markdown
the meta-optimiser once: of the 427 admissible runs in the partition families, 415 carry a **Lion**
```

REPLACE WITH

```markdown
the meta-optimiser once: of the 431 admissible runs in the partition families, 419 carry a **Lion**
```

## MD-04  lines 380--382

ANCHOR (count == 1)

```markdown
validation partition anywhere in the project** (§3.3, §7 T12). 1,967 of the 2,173 runs are
CIFAR-10 and 206 are CIFAR-100. **Subject systems.** Networks are instantiated by the parent
release's `build_network.py`: ResNet-18 on 1,872 rows (1,667 CIFAR-10, 188 CIFAR-100, 17 the
```

REPLACE WITH

```markdown
validation partition anywhere in the project** (§3.3, §7 T12). 1,971 of the 2,177 runs are
CIFAR-10 and 206 are CIFAR-100. **Subject systems.** Networks are instantiated by the parent
release's `build_network.py`: ResNet-18 on 1,876 rows (1,671 CIFAR-10, 188 CIFAR-100, 17 the
```

## MD-05  lines 385--390

ANCHOR (count == 1)

```markdown
ResNet-50 (one). **Training scenario.** Mini-batch size 100 in all 2,173 runs; one test-set
evaluation after every training epoch; augmentation is `RandomCrop(32, padding=4)` followed by a
random horizontal flip (`patches/patch_augment.py`), recorded on in 2,059 rows, off in 27, and
unrecorded in 87 early rows — and on in 534 of the 535 partition-family rows, the one exception
carrying no value in that column. **Budgets.** 100 epochs is the standard workload (1,614 runs);
the budget ladder of §4.8 extends it to 300 (62 runs); 392 runs are 20-epoch probes, and the
```

REPLACE WITH

```markdown
ResNet-50 (one). **Training scenario.** Mini-batch size 100 in all 2,177 runs; one test-set
evaluation after every training epoch; augmentation is `RandomCrop(32, padding=4)` followed by a
random horizontal flip (`patches/patch_augment.py`), recorded on in 2,063 rows, off in 27, and
unrecorded in 87 early rows — and on in 538 of the 539 partition-family rows, the one exception
carrying no value in that column. **Budgets.** 100 epochs is the standard workload (1,614 runs);
the budget ladder of §4.8 extends it to 300 (66 runs); 392 runs are 20-epoch probes, and the
```

## MD-06  lines 397--397

ANCHOR (count == 1)

```markdown
partitions; 1,632 GPU-hours over 29 nodes (§8).
```

REPLACE WITH

```markdown
partitions; 1,642 GPU-hours over 29 nodes (§8).
```

## MD-07  lines 555--555

ANCHOR (count == 1)

```markdown
redundant: **17 of 2,173 runs pass `window_ok` while having completed under 95% of their
```

REPLACE WITH

```markdown
redundant: **17 of 2,177 runs pass `window_ok` while having completed under 95% of their
```

## MD-08  lines 562--565

ANCHOR (count == 1)

```markdown
attrition inside the primary contrasts is zero. Of 2,173 rows, **1,731 are
admissible**. (This count is 7 higher than the 1,724 of earlier versions of this paper for one reason only:
`rp1`'s eight mid-flight snapshot rows have been refreshed from the completed `.out` files, so
seven of them now pass the `complete` gate. No other row moved.)
```

REPLACE WITH

```markdown
attrition inside the primary contrasts is zero. Of 2,177 rows, **1,735 are
admissible**. (This count is 11 higher than the 1,724 of earlier versions of this paper for two
reasons and no others: `rp1`'s eight mid-flight snapshot rows have been refreshed from the
completed `.out` files, so seven of them now pass the `complete` gate; and the four `hz3q` rows of
§3.5 were ingested, all four admissible. No other row moved.)
```

## MD-09  lines 832--833

ANCHOR (count == 1)

```markdown
audit executes **557 claim-carrying assertions covering 372 of the 849 distinct
quantity-numerals** in this manuscript, which is 43.8% of them. Those three figures are not
```

REPLACE WITH

```markdown
audit executes **557 claim-carrying assertions covering 373 of the 857 distinct
quantity-numerals** in this manuscript, which is 43.5% of them. Those three figures are not
```

## MD-10  lines 845--845

ANCHOR (count == 1)

```markdown
### 3.5 Four pre-registered batches: three scored, one never started
```

REPLACE WITH

```markdown
### 3.5 Four pre-registered batches: all four now scored, one after a forced redesign
```

## MD-11  lines 847--854

ANCHOR (count == 1)

```markdown
Three weaknesses this paper states about itself, and one experiment it declares was never run, are
addressed by the four batches tabulated below, submitted while this paper was being written. Three of the four — `bm2`,
`sm4` and `rp1` — have since completed and been scored by running their registered scorers
**unedited**, and their verdicts are folded into §4.4, §4.6, §4.7, §5.4, §5.5 and §7. One — the
`hz3` seed-5 trio — is not scored, and **no number from it enters any claim in this paper**. The
registrations are stated here in full regardless of outcome, so that the decision rules are on the
record ahead of the numbers, and so that a reader can check that the three verdicts we did read are
the ones we said we would read.
```

REPLACE WITH

```markdown
Three weaknesses this paper states about itself, and one experiment it declares was never run, are
addressed by the four batches tabulated below, submitted while this paper was being written.
**All four** — `bm2`, `sm4`, `rp1` and the `hz3` seed-5 repair — have since been scored by running
their registered scorers **unedited**, and their verdicts are folded into §4.4, §4.6, §4.7, §4.8,
§5.4, §5.5 and §7. One of the four did not run in the form it was registered in: R2's three queued
jobs were cancelled before they started and were replaced by a four-arm batch, `hz3q`, described
below. The registrations are stated here in full regardless of outcome, so that the decision rules
are on the record ahead of the numbers, and so that a reader can check that the four verdicts we
read are the ones we said we would read. **One of them reverses a sentence this project
published**, and §4.8 carries the reversal rather than burying it.
```

## MD-12  lines 865--865

ANCHOR (count == 1)

```markdown
| R2 | `hz3` seed-5 trio | 3 | the budget cell's clip-box and GPU-class mismatch (§4.8, §7 T9) | `analysis/c87_hz3_score.py`, reused unedited | **queued, not started** |
```

REPLACE WITH

```markdown
| R2 | `hz3q` | 4 | the budget cell's clip-box and GPU-class mismatch (§4.8, §7 T9); replaces the `hz3` seed-5 trio, cancelled unstarted | `analysis/c99_hz3q_score.py` | **SCORED — `NOT FLAT`; flatness WITHDRAWN (§4.8)** |
```

## MD-13  lines 889--900

ANCHOR (count == 1)

```markdown
**R2 — the `hz3` seed-5 trio, re-run box- and hardware-matched.** `hz3-ch-s5`, `hz3-c23-s5` and
`hz3-n1d-s5` re-run at 300 epochs in the batch's own box `−30:9.0` and pinned to the batch's own
GPU class for seed 5 (RTX 2080 Ti), restoring a matched 6 v 6 at every budget. Nothing else in
`hz3` is touched; its seed-5 `nodewise` partner is already in the right box. The composed argument
line was verified byte-identical to the original `hz3-ch-s5` run's own `ARGS:` line modulo the
partition flag, and the box arithmetic was pre-registered: at ms·T = 1e-4 × 300 × 500 = 15.0 nats
of travel from β₀ = −6.907755, β is confined to [−21.908, +8.092], so **both rails of `−30:9.0`
are provably unreachable** while the superseded box's floor of −15 is reachable from epoch 162 —
which is exactly what the probe records show happened (§7 T9). This batch changes the data the
registered reader reads; it does not change the reader. `analysis/c87_hz3_score.py` is reused
**unedited** (sha256 `0be1f5201d…`, selftest 144/144 PASS) rather than a second scorer being
written, because writing one would create two registrations for one question.
```

REPLACE WITH

```markdown
**R2 — the `hz3` seed-5 repair: registered as a trio, delivered as a quartet.**
*As registered.* `hz3-ch-s5`, `hz3-c23-s5` and `hz3-n1d-s5` re-run at 300 epochs in the batch's own
box `−30:9.0` and pinned to the batch's own GPU class for seed 5 (RTX 2080 Ti), restoring a matched
6 v 6 at every budget against the archived seed-5 `nodewise` run, which is already in the right box.
*What happened.* Those three jobs (Slurm 4855960–62) never started. They sat on `gpu-2080ti-11g`
with elapsed time `0:00` and no node ever assigned; the queue's own start estimate for them stood at
roughly a week, and we cancelled them rather than hold the paper for it. No `.out` file exists for
any of the three job ids, which is why they appear nowhere in the attrition ledger of §8: that
ledger reconciles logs against the run table, and these three produced no log.
*What we ran instead, and why the replacement is the better design.* `hz3q`: *four* arms —
`nodewise`, `chunk777`, `nodewise1d` and `chunk2325` — at seed 5, 300 epochs, box `−30:9.0`, in
**one** submission (Slurm 4864632–35) on **one** card (`node883`, an NVIDIA L4 on `gpu-l4-24g`).
The registered trio matched an *archived* comparator by pinning a partition, so it was correct only
if the queue delivered that partition and only if the archived run it leaned on was what its
metadata said. The quartet generates its comparator inside itself: box and GPU class are identical
across the four arms **by construction**, and the seed-5 contrast depends on no archived run at all.
We changed the design because a week-long queue made the registered one unaffordable, and we say
that rather than present the redesign as foresight; it is nonetheless the better design, and it buys
a measurement the original could not make (HC below). Its one cost is that the quartet sits on a
different GPU class from seeds 0–4, which is exactly why that control is carried.
*The registration.* Under STANDING RULE 21, `analysis/c99_hz3q_score.py` (sha256 `50d95083c8…`,
selftest 59/59 PASS) was committed **before the runs existed**, and it writes no reader of its own:
it imports `analysis/c87_hz3_score.py` (sha256 `0be1f5201d…`) **unedited** under STANDING RULE 16,
so the quartet changes the data the registered reader reads and not the reader. Its flatness bar,
|t| < 2.0, is frozen in `band_flat()` and predates the runs. The box arithmetic is unchanged from
the registration: at ms·T = 1e-4 × 300 × 500 = 15.0 nats of travel from β₀ = −6.907755, β is
confined to [−21.908, +8.092], so **both rails of `−30:9.0` are provably unreachable**, while the
superseded box's floor of −15 is reachable from epoch 162 — which is what the probe records show
happened (§7 T9). The gate measures that rather than asserting it: the worst coordinate fraction
over all four arms at epochs 100, 200 and 300 is **exactly 0.000000** on n = 500 coordinates per
arm, against a registered bar of 0.05.
```

## MD-14  lines 954--955

ANCHOR (count == 1)

```markdown
differently-named same-experiment pairs. The rebuild changed exactly those eight rows and **no
other row in the corpus** (2,173 rows in and out; 0 added, 0 removed, 8 changed, 0 of them outside
```

REPLACE WITH

```markdown
The rebuild changed exactly those eight rows and **no
other row in the corpus** (the table then stood at 2,173 rows: 2,173 rows in and out; 0 added,
0 removed, 8 changed, 0 of them outside
```

## MD-15  lines 977--983

ANCHOR (count == 1)

```markdown
**R2 is still queued and has never started.** The three seed-5 jobs (`hz3-ch-s5`, `hz3-c23-s5`,
`hz3-n1d-s5`) sit `PENDING` with elapsed time `0:00` and no assigned start time, on the same
congested partition on which the original `hz3` seed-3 and seed-4 runs waited 16 and 23 hours, so a
wait is expected rather than anomalous. No `.out` file exists for any of the three job ids, so
STANDING RULE 20's post-launch ARGS check **remains owed** and cannot be discharged yet; it is owed
the moment they start, and the batch is to be cancelled on any `BETA_CLIP` mismatch. Until they run,
the box-matched 6 v 6 at 300 epochs does not exist and **§4.8's budget verdict is unchanged**.
```

REPLACE WITH

```markdown
**R2 landed, and it reversed a sentence.** The quartet completed and was scored by running
`c99_hz3q_score.py` **unedited**. Its provenance gate H0 reads node, GPU model and `BETA_CLIP` off
each run's own header rather than from any declaration, and passes: all four arms `node883`,
`NVIDIA L4`, `−30:9.0`, seed 5, 300 epochs. Turned on the archive it repairs, the same gate
**refuses** it — those four runs carry two GPU models and two clip boxes — so the gate is shown to
cut in both directions before a number is read. STANDING RULE 20 is discharged on all four `.out`
files: `analysis/argsline_guard.py` returns **4 clean, 0 with a repeated flag or a design mismatch,
VERDICT PASS**.

**The primary, H2: is D flat from 100 to 300 epochs?** Paired within seed on `plateau5`, the
registered reader returns three readings and the scorer prints all three. `hz3` as published, six
archived seeds: **−0.149 ± 0.105, t −1.42** — `FLAT`. `hz3` with seed 5 dropped, five seeds:
**−0.207 ± 0.107, t −1.94** — `FLAT`. **Repaired**, archived seeds 0–4 plus `hz3q`'s seed 5:
**−0.238 ± 0.093, t −2.57, df 5** — **`NOT FLAT`, and the sign names the direction: D declines with
budget.** The project record's sentence "D is present and resolved at a 3× budget and is
statistically flat from 100 to 300 epochs" does not stand on the repaired data and is
**withdrawn**. All three readings are reported together, always: the repaired one does not replace
the published one in the record, it is the disclosed repair of the one seed whose contrast was
cross-box and cross-class. **The gap itself is untouched.** Repaired, D(300) = **+0.394 ± 0.093,
t 4.25**, against the published **+0.428 ± 0.086, t 4.94**; G(300) = −0.048 against −0.057. D
shrinks as the budget grows; it does not vanish, and no cell of Table 2 moves.

**HC, the cross-class control — reporting, not gating.** `hz3q-node-s5` on the L4 reads
`plateau5`(300) = 92.908; the archived `hz3-node-s5` on the RTX 2080 Ti reads 92.774. Same seed,
same box, same flags, same code; only the GPU class differs. Δ = **+0.134 pp** against a registered
bar of |Δ| ≤ 1.00 pp: **GPU class is not first-order on the level.** This is a measurement `hz3`'s
own design — which assigns GPU class as a function of seed — could never make. It decides what this
paper may say about `hz3`'s *levels*; it does not touch D, which is a within-seed, within-class
contrast in both batches.

**The non-overwrite check, which is not optional.** `hz3q` adds rows; it overwrites nothing.
`c87_hz3_score.py` was re-run **unedited** after the ingest, its output contains the string `hz3q`
**zero** times — its own glob predicate rejects every `hz3q` file name, and `hz3q`'s probe
directories are disjoint from `hz3`'s — and its verdicts are unchanged (`SURVIVES` on the primary,
`MECHANISM SURVIVES THE HORIZON` on the secondary). The four `hz3q` rows enter
`results/all_runs.csv` with no `dup_group` and no supersession, and they enter no cell of Table 2.
`hz3q` repairs one seed of one batch: it is not a replication, not a new design point and not a new
cell, and it is counted as none of them.
```

## MD-16  lines 1139--1139

ANCHOR (count == 1)

```markdown
Run R2 (§3.5) restores a matched 6 v 6.
```

REPLACE WITH

```markdown
The `hz3q` quartet of §3.5 (R2) re-runs seed 5 box- and class-matched, but it is a separate batch
under a separate registration and does not enter this cell, whose reading is unchanged; the
repaired 6 v 6 is read off the `.out` series in §4.8.
```

## MD-17  lines 1165--1170

ANCHOR (count == 1)

```markdown
also positive.** We verified this by enumeration rather than by recollection: of the 2,173 runs,
every batch that ever ran a `nodewise` arm alongside a count-matched uniform-chunk arm is one of
these twenty-two (the twenty above, `gn1`-GroupNorm, and `ar1`), and every other batch carrying a
`nodewise` arm has no arm to match it against. The enumeration also shows that no such cell could
have been lost to the admissibility gate: all 256 uniform-chunk, `nodewise1d` and `permnode` runs in
the corpus — 238 of them outside `rp1`, and now all 18 of `rp1`'s `permnode` rows as well — are
```

REPLACE WITH

```markdown
also positive.** We verified this by enumeration rather than by recollection: of the 2,177 runs,
every batch that ever ran a `nodewise` arm alongside a count-matched uniform-chunk arm is one of
these twenty-two (the twenty above, `gn1`-GroupNorm, and `ar1`), and every other batch carrying a
`nodewise` arm has no arm to match it against. The enumeration also shows that no such cell could
have been lost to the admissibility gate: all 259 uniform-chunk, `nodewise1d` and `permnode` runs in
the corpus — 241 of them outside `rp1`, and now all 18 of `rp1`'s `permnode` rows as well — are
```

## MD-18  lines 1911--1912

ANCHOR (count == 1)

```markdown
‡ `hz3` matched at 5 v 5 (seed-5 trio excluded for the clip-box and hardware mismatch of §7 T9):
**+0.328 ± 0.084, t 3.89**.
```

REPLACE WITH

```markdown
‡ `hz3` matched at 5 v 5 (seed-5 trio excluded for the clip-box and hardware mismatch of §7 T9):
**+0.328 ± 0.084, t 3.89**. The `hz3q` quartet of §3.5 repairs that seed but is a separate
registration and enters no pool here.
```

## MD-19  lines 2078--2088

ANCHOR (count == 1)

```markdown
**The trend is not robust, and we do not claim it.** Within-run, D(300) − D(100) = **−0.149 ±
0.105, t −1.42** over all six seeds and **−0.207 ± 0.107, t −1.94** over the five clean ones.
Neither resolves at |t| ≥ 2, but the second is close enough that the difference matters, so we say
where it comes from: 76% of the shift is at the **100-epoch** end (the six-seed D(100) rises by
0.086 pp when seed 5 is removed, against 0.027 pp at 300 epochs), and seed 5's low D(100) is
**not** explained by either defect — the clip box is provably inert before epoch 162, and the
hardware term (§6.3) points the other way. It is an unexplained extreme value in an n = 6 cell.
The honest statement is therefore the weaker one: **D does not grow with budget from 100 to 300
epochs, and we cannot resolve whether it decays.** We do not report flatness as a result. A
box- and hardware-matched replacement trio (R2, §3.5) is registered and will settle it; until it
lands this cell carries its sensitivity in the text.
```

REPLACE WITH

```markdown
**The trend was not resolved as published; on the repaired seed set it resolves, and it resolves
downward.** Within-run and as published, D(300) − D(100) = **−0.149 ± 0.105, t −1.42** over all six
seeds and **−0.207 ± 0.107, t −1.94** over the five clean ones; neither crosses |t| ≥ 2. Seed 5
entered both of those readings on a run that sat in a narrower clip box and on a different GPU class
from its own comparator (§7 T9), and the `hz3q` quartet of §3.5 re-runs that seed with all four arms
in one submission on one card. On the repaired seed set — the five clean archived seeds plus
`hz3q`'s seed 5 — the same registered reader returns **−0.238 ± 0.093, t −2.57, df 5**, which
crosses the |t| ≥ 2 bar that `c99_hz3q_score.py` froze in `band_flat()` before the quartet existed:
**`NOT FLAT` — D declines with budget.** We report all three readings together and always; the
repaired one does not replace the published one in the record, it is the disclosed repair of the one
seed whose contrast was cross-box and cross-class. **What does not change is the gap.** Repaired,
D(300) = **+0.394 ± 0.093, t 4.25**, against the published **+0.428 ± 0.086, t 4.94**: D shrinks as
the budget grows and it does not disappear. Where the shift sits is worth stating, because it is not
where the published readings put it: as published, 76% of the −0.149 to −0.207 move was at the
**100-epoch** end (the six-seed D(100) rises by 0.086 pp when seed 5 is removed, against 0.027 pp at
300 epochs), and the repaired seed reproduces that end rather than the archived outlier —
D(100) = **+0.482** against the archive's **+0.148** (§7 T9). Table 2's `hz3` cell is a separate,
CSV-based reading of a separate registration and is unmoved by any of this.
```

## MD-20  lines 2781--2781

ANCHOR (count == 1)

```markdown
job's actual `ARGS:` line afterwards. Swept over the 2,237 runs carrying an `ARGS:` line on both
```

REPLACE WITH

```markdown
job's actual `ARGS:` line afterwards. Swept over the 2,241 runs carrying an `ARGS:` line on both
```

## MD-21  lines 2902--2903

ANCHOR (count == 1)

```markdown
`chunk*` or `permnode*`. There are **427** of them, of which **415 are meta = Lion and 12 are
meta = RMSProp**; the twelve are `sm4`. Before `sm4` the count was 415 of 415. (An earlier version
```

REPLACE WITH

```markdown
`chunk*` or `permnode*`. There are **431** of them, of which **419 are meta = Lion and 12 are
meta = RMSProp**; the twelve are `sm4`. Absent `sm4` the census reads 419 of 419. (An earlier version
```

## MD-22  lines 3064--3065

ANCHOR (count == 1)

```markdown
we do not edit a registered scorer after its data exist, so the correction is recorded here, and
R2 makes the label true again.
```

REPLACE WITH

```markdown
a defect in the registered scorer's metadata, not in its statistics; under our own file-freeze rule
we do not edit a registered scorer after its data exist, so the correction is recorded here.
**R2 does not make that label true.** The replacement quartet ran on an NVIDIA L4, not on the
RTX 2080 Ti the cancelled trio was pinned to, so `hz3`'s archived seed-5 label is wrong and stays
wrong. What the quartet does is make the label *irrelevant* to the contrast: its four arms share one
card, so the seed-5 D it delivers is within-class whatever that class is, and its HC control
measures the class term directly at +0.134 pp on the level (§3.5).
```

## MD-23  lines 3077--3079

ANCHOR (count == 1)

```markdown
*inflate* D, not deflate it. The 100-epoch outlier is unexplained. §4.8 reports the budget contrast
both with and without seed 5 for this reason, and a replacement seed-5 trio in the original box and
on matched hardware is R2 (§3.5).
```

REPLACE WITH

```markdown
*inflate* D, not deflate it. The 100-epoch outlier is unexplained — and it did not reproduce.
`hz3q`'s box- and class-matched seed 5 returns D(100) = **+0.482**, close to though still below the
five archived seeds' range of +0.548 to +0.990, against the archived **+0.148**. We do not
attribute that 0.334 pp: the box is provably inert at 100 epochs, so only GPU class and
run-to-run nondeterminism remain, and the cross-class control puts the class term at +0.134 pp on a
*level*, which is both too small and, being common to the two arms, largely cancelled inside D.
§4.8 reports the budget contrast as published, without seed 5, and repaired, for this reason, and
the replacement batch is R2 (§3.5).
```

## MD-24  lines 3224--3224

ANCHOR (count == 1)

```markdown
**Data.** `data/all_runs.csv`, 2,173 rows, one per run, with the full configuration
```

REPLACE WITH

```markdown
**Data.** `data/all_runs.csv`, 2,177 rows, one per run, with the full configuration
```

## MD-25  lines 3234--3243

ANCHOR (count == 1)

```markdown
`.out` files in `logs/raw_out.tar.gz`. The shipped log set is **2,241 files, which is every
`.out` file in the two clusters' Slurm run directories** (1,322 and 919). **Neither provenance
line is universal, and these are the counts.** **2,237** of the 2,241 carry their own `ARGS:`
line — the **four** that do not are infrastructure jobs that ran no training (`gtest`,
`gtest2`, `mo-smoke`, `ts-pretok`) — and **2,113** carry their own `ENV:` line, so **128 do
not**: those four plus 124 that carry `ARGS:` without `ENV:` (103 on the first account, 25 on
the second). The `ENV:` line was added to the submission template partway through the corpus, so
every file missing one carries a Slurm job id at or below 4,680,828 while every file carrying
one is at or above 4,680,676. Where a line is present it is the authority on what that run
actually did, and RULE 20 is enforced on all 2,237 `ARGS:` lines. There is no shortfall in the
```

REPLACE WITH

```markdown
`.out` files in `logs/raw_out.tar.gz`. The shipped log set is **2,245 files, which is every
`.out` file in the two clusters' Slurm run directories** (1,326 and 919). **Neither provenance
line is universal, and these are the counts.** **2,241** of the 2,245 carry their own `ARGS:`
line — the **four** that do not are infrastructure jobs that ran no training (`gtest`,
`gtest2`, `mo-smoke`, `ts-pretok`) — and **2,117** carry their own `ENV:` line, so **128 do
not**: those four plus 124 that carry `ARGS:` without `ENV:` (103 on the first account, 25 on
the second). The `ENV:` line was added to the submission template partway through the corpus, so
every file missing one carries a Slurm job id at or below 4,680,828 while every file carrying
one is at or above 4,680,676. Where a line is present it is the authority on what that run
actually did, and RULE 20 is enforced on all 2,241 `ARGS:` lines. There is no shortfall in the
```

## MD-26  lines 3259--3267

ANCHOR (count == 1)

```markdown
| Slurm `.out` files on the two clusters | 2,241 | — | `runs/` + `runs_alice2/` + the on-cluster copies |
| — infrastructure jobs, no training | −4 | — | `gtest`, `gtest2`, `mo-smoke`, `ts-pretok`; no `ARGS` line, no CSV row |
| **jobs that entered the training script** | **2,237** | — | each logs one `ARGS` line |
| — crashed or cancelled before epoch 1 | −64 | ≈0 | itemised below; **not one logged a single epoch** |
| **rows in `results/all_runs.csv`** | **2,173** | 1,631.7 | 2,158 carry a wallclock |
| — no readable `plateau5` | −25 | } 66.3 | 2–5-epoch smoke tests |
| — `window_ok = 0`, `plateau5` present | −400 | } | budget ≤ 20 epochs; `window_ok` is `epochs_done > 20` |
| — `window_ok = 1`, `complete = 0` | −17 | } | truncated runs; `complete` is `epochs_done ≥ 0.95 × requested` |
| **admissible** | **1,731** | 1,565.3 | the gate of Eq. 11 |
```

REPLACE WITH

```markdown
| Slurm `.out` files on the two clusters | 2,245 | — | `runs/` + `runs_alice2/` + the on-cluster copies |
| — infrastructure jobs, no training | −4 | — | `gtest`, `gtest2`, `mo-smoke`, `ts-pretok`; no `ARGS` line, no CSV row |
| **jobs that entered the training script** | **2,241** | — | each logs one `ARGS` line |
| — crashed or cancelled before epoch 1 | −64 | ≈0 | itemised below; **not one logged a single epoch** |
| **rows in `results/all_runs.csv`** | **2,177** | 1,641.5 | 2,162 carry a wallclock |
| — no readable `plateau5` | −25 | } 66.3 | 2–5-epoch smoke tests |
| — `window_ok = 0`, `plateau5` present | −400 | } | budget ≤ 20 epochs; `window_ok` is `epochs_done > 20` |
| — `window_ok = 1`, `complete = 0` | −17 | } | truncated runs; `complete` is `epochs_done ≥ 0.95 × requested` |
| **admissible** | **1,735** | 1,575.2 | the gate of Eq. 11 |
```

## MD-27  lines 3304--3306

ANCHOR (count == 1)

```markdown
**every** uniform-chunk, `nodewise1d` and `permnode` run in the corpus — **256 of 256**, `rp1`
included — is admissible, so no count-matched cell could have been lost to the gate even in
principle. (Earlier versions of this paper read 249 of 256, the seven exceptions being `rp1`'s mid-flight
```

REPLACE WITH

```markdown
**every** uniform-chunk, `nodewise1d` and `permnode` run in the corpus — **259 of 259**, `rp1`
included — is admissible, so no count-matched cell could have been lost to the gate even in
principle. (Earlier versions of this paper read 249 of the 256 such rows the corpus then held,
the seven exceptions being `rp1`'s mid-flight
```

## MD-28  lines 3317--3317

ANCHOR (count == 1)

```markdown
**Compute.** 2,158 runs carry a wallclock; they total **1,632 GPU-hours** over 29 distinct
```

REPLACE WITH

```markdown
**Compute.** 2,162 runs carry a wallclock; they total **1,642 GPU-hours** over 29 distinct
```

## MD-29  lines 3414--3414

ANCHOR (count == 1)

```markdown
run a different experiment from the one it declares. Over the 2,237 runs carrying an
```

REPLACE WITH

```markdown
run a different experiment from the one it declares. Over the 2,241 runs carrying an
```

## MD-30  lines 3511--3516

ANCHOR (count == 1)

```markdown
**The experiments that would break the impasse**, in the order we would run them. Two of the four
registered in §3.5 have been read: R3, the base-moderator replication at fresh seeds, which
replicated both levels and is in §4.4; and R4, the second-moment corner, which refuted its
mechanism and is in §5.5. Two remain: the alignment replication with the permutation seed
decoupled (R1, complete on disk and deliberately unscored) and the box- and hardware-matched
budget trio (R2, queued). To those we add two experiments the last cycle created rather than
```

REPLACE WITH

```markdown
**The experiments that would break the impasse**, in the order we would run them. **All four**
registered in §3.5 have now been read: R3, the base-moderator replication at fresh seeds, which
replicated both levels and is in §4.4; R4, the second-moment corner, which refuted its
mechanism and is in §5.5; R1, the alignment replication with the permutation seed decoupled, which
replicated the null at twice the power and is in §4.6.1; and R2, the seed-5 budget repair, whose
registered trio was cancelled unstarted and whose replacement quartet returned `NOT FLAT` and
withdrew a flatness sentence (§4.8). None of the four is outstanding. To those we add two
experiments the last cycle created rather than
```

## MD-31  lines 3560--3561

ANCHOR (count == 1)

```markdown
the meta-optimiser is a single cell: of the 427 admissible runs in the partition families,
415 are meta = Lion and 12 are meta = RMSProp. **One cell is not an axis, and no meta-optimiser
```

REPLACE WITH

```markdown
the meta-optimiser is a single cell: of the 431 admissible runs in the partition families,
419 are meta = Lion and 12 are meta = RMSProp. **One cell is not an axis, and no meta-optimiser
```

## MD-32  lines 3655--3658

ANCHOR (count == 1)

```markdown
**A.8 — Corpus size.** The record variously says 1,960 / 2,077 / 2,113 runs and ~1,200–1,400
GPU-hours. At write time: **2,173 rows, 1,731 admissible, 1,632 GPU-hours** summed over the 2,158
runs carrying a wallclock, with 2,237 jobs having entered the training script and nothing awaiting
ingest (§8, Table 3). The correction register runs to entry 131.
```

REPLACE WITH

```markdown
**A.8 — Corpus size.** The record variously says 1,960 / 2,077 / 2,113 runs and ~1,200–1,400
GPU-hours. At write time: **2,177 rows, 1,735 admissible, 1,642 GPU-hours** summed over the 2,162
runs carrying a wallclock, with 2,241 jobs having entered the training script and nothing awaiting
ingest — the last batch to land, the `hz3q` quartet of §3.5, is scored and its four rows are in the
table (§8, Table 3). The correction register runs to entry 133.
```

## MD-33  lines 3728--3730

ANCHOR (count == 1)

```markdown
The complete run table (`results/all_runs.csv`, 2,173 rows), the
raw per-epoch Slurm logs (2,241 `.out` files, of which 2,237 carry their own `ARGS:` line and
2,113 their own `ENV:` line; §8 itemises the exceptions),
```

REPLACE WITH

```markdown
The complete run table (`results/all_runs.csv`, 2,177 rows), the
raw per-epoch Slurm logs (2,245 `.out` files, of which 2,241 carry their own `ARGS:` line and
2,117 their own `ENV:` line; §8 itemises the exceptions),
```

## MD-34  lines 3814--3814

ANCHOR (count == 1)

```markdown
Investigation (all 2,173 runs), Data curation, Writing – original draft, Visualization, Project
```

REPLACE WITH

```markdown
Investigation (all 2,177 runs), Data curation, Writing – original draft, Visualization, Project
```

## MD-35  lines 3840--3840

ANCHOR (count == 1)

```markdown
rested on, a budget flatness claim demoted to an unresolved trend, and a variance claim that
```

REPLACE WITH

```markdown
rested on, a budget flatness claim demoted to an unresolved trend and then, on a repaired seed,
resolved as a decline, and a variance claim that
```
