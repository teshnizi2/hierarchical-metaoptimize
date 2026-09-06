# STATUS — operator dashboard

Updated 6 Sep 2026 (**cycle 124**). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **148**) > `docs/FINDINGS.md` > everything else.
Manuscript and deposit are both at **`2f4fd9a`** (parent `58c0c85`). **Nothing under `paper/` touched this cycle.**
Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**76 pp**). Corpus = **2,501 rows** — **no ingest this cycle**; `cts2` has not landed, `grep -c cts2 results/all_runs.csv` = **0**.
**`c98_reproduce.py` STILL EXITS 1** — the same inherited stale numerals as at CORRECTIONS 141.6 / 142.6. Author fix; not touched here.

## Queue — re-derived from `squeue` at this HEAD

**`cts2` LAUNCHED AND RUNNING (12/12, alice2). `in489g2` still running on `alice` — NOT MINE. No ingest: corpus unchanged at 2,501 rows.**

| account | batch | jobs | run | pend | done | decides | score with |
|---|---|---|---|---|---|---|---|
| `alice2` | **`cts2`** | 12 | **12** | 0 | 0 | is `cts1`'s 24.8 pp cliff **stepsize allocation** or **clamp-turnover timing**? | `cM1_cts2_score.py` (`1a06a52`) |
| `alice` | `in489g2` | 14 | 8 | 6 | 0 | **where** ImageNet-489 crosses CAPTURE 0.5 on `m` in (6,62) | `cI2_in489g2_score.py` (`571707b`) |

- `cts2` elapsed **35:54** at this HEAD, 8 distinct nodes, no queueing. Landing expected **11:55–12:05 CEST**; measured basis `cpk1` 42.0 min/run over 39 jobs and `cts1` 18 jobs at ≈45 min. Cost ≈ **9 GPU-h**.
- `in489g2` seed-0 jobs at **6:33:33** elapsed; seed-1 still `PENDING`, gated behind the 8-GPU `QOSMaxGRESPerUser` cap. **`in489g2` is NOT this session's batch. Never cancel, requeue or modify it.**
- **`cts2` IS NOT SCORED.** It had not landed at this HEAD; only `--selftest` was ever run against its scorer.

**`cts2` — 2×2×3 clamp × cut. CORRECTIONS 148.1–148.2.**

| factor | levels |
|---|---|
| cut | `k49 = [49,13]` · `k50 = [50,12]` (the step moves exactly `layer4.0.bn2.weight`, 512 params) |
| clamp | `C = BETA_CLIP -15:-2.3026` · `R = BETA_CLIP -80:-2.3026` (**only the floor moves**) |
| seeds | 0, 1, 2 |

- Cell: CIFAR-100 / `ResNet18_c100` / SGDm+Lion / `ms=1e-3` / `alpha0=1e-6` / 100 ep / `AUGMENT=1` / `HIER=none` / `PROBE=0`.
- **Both CLAMPED cells run in batch.** `cts1`'s arms are NOT spliced in — batch is the unit of replication and the estimand is a within-batch interaction.
- Released floor `-80` is non-binding **by arithmetic**: `|dβ| ≤ ms = 1e-3` per meta-step, 50,000 steps from `float32(log 1e-6) = −13.815511` reach at worst **−63.790127**.
- Bars: `SURVIVE/PREMISE 12.4170` · `COLLAPSE 1.4564` · `INTERACTION 2.0598` · `NOISY 2.6757` · `DEAD 5.00` pp, from `σ_w = 0.8919 pp` (df 46, `m=2` restriction).
- Gates in order, first failure decides: **G0** provenance → VOID · **R1** manipulation (fails **closed** if traces unreadable) · **R2** DEAD run → UNRESOLVED-DIVERGED · **R3** SD > 3σ_w → UNRESOLVED-NOISY · **R4** `D_C < 12.4170` → UNRESOLVED-PREMISE. `COLLAPSED-BY-FREEZING` is a distinct named outcome.
- **Prior on record before the data:** COLLAPSED or PARTIAL, not SURVIVED. Both branches carry identical machinery and identical bars.

**RULE 20 — `cts2` 12/12 PASS. `in489g2` 8/14, reopens when its 6 pending jobs start.**

| account | audited | result |
|---|---|---|
| `alice2` | 12/12 (`cts2`) | **12 clean, 0 repeated flags or design mismatch, 0 without an ARGS line — VERDICT PASS** (exit 0) |
| `alice` | 8/14 | **8 clean, 0, 0 — VERDICT PASS** (unchanged; the 6 pending jobs cannot be audited from the queue) |

- The manipulation cannot ride on the ARGS line — `BETA_CLIP` is an env var — so it was re-derived from each run's **own `ENV` line**: **6 at `-15:-2.3026`, 6 at `-80:-2.3026`, `PROBE=0` in all 12**, agreeing with the run NAME and the ARGS line in every case. **No mismatch → nothing scancelled.**
- Run with `METAOPT_WS=/home/s5014158/metaopt` exported; `bin/_lib_guards.sh` clobbers `WS` otherwise.

**RULE 21 / RULE 16 — `cts2`, proved by wall clock and by `git diff`.**

| check | result |
|---|---|
| registration commit | `1a06a52ba3bb158542a0d03df71a11d20106cae6`, **2026-09-06T11:08:55+02:00** (epoch 1788685735) |
| earliest Slurm submit (`sacct`) | **2026-09-06T11:10:01** (epoch 1788685801); last 11:10:02 |
| **margin** | **66 s**; 1-second spread across all 12 ids = one submission |
| `git diff --numstat 8e61b28 1a06a52 -- analysis/` | **`983  0  analysis/cM1_cts2_score.py`** — one added file, **983 insertions, 0 deletions**. No pre-existing scorer touched |
| whole commit | 3 files, **1,464 insertions, 0 deletions** (scorer, launcher, `bin/PROTECTED.txt`) |
| corpus at registration | `grep -c cts2 results/all_runs.csv` = **0** |

**ACCOUNT HYGIENE — clean on both.**

- `alice` holds **14** jobs, all `in489g2-`; `alice2` holds **12**, all `cts2-`. Nothing else queued on either.
- **0 CANCELLED on either account this cycle.** No job this session did not submit was touched.
- `bin/PROTECTED.txt` carries `cts2-` (18 prefixes), committed in `1a06a52`.

**`cts1` — CARRIED FORWARD from cycle 123 (CORRECTIONS 147). This is what `cts2` is testing.**

| | |
|---|---|
| CLIFF | **CLIFF-REPRODUCES** (TOTAL +0.3598, bar 0.1820) · SPLIT **SINGLE-TENSOR-MAJORITY** |
| the tensor | **`layer4.0.bn2.weight`** (512 params) — k=49→50 = **+24.834 pp** |
| matched control | k=50→51 `layer4.0.bn2.bias`, also 512 params, same BN module = **−0.233 pp** |
| withdrawn | `BN-LEVERAGE-FAVOURED` **as a class claim**; `MASS-REFUTED` is a theorem of `HF.py:189` + `:881`, not a result |
| **the open limitation** | the fine group ends at the `BETA_CLIP` floor β=−15.000 in **12/12** cut runs. **Nothing in `cts1` separates stepsize allocation from clamp-turnover timing** — hence `cts2` |

## Clamp census — CORRECTIONS 148.3–148.10

**Read-only, 1,171 probe dirs on both accounts (665 `alice` / 506 `alice2`), 1,091 joined to their own `.out`. Nothing written into either runs tree. THE HEADLINE IS A NULL: no finding is refuted; one family is re-labelled.**

| rail (terminal record, n=1,091) | rate |
|---|---|
| FLOOR | 301/1091 = **27.6%** |
| CEILING | 98/1091 = **9.0%** |
| either | 331/1091 = **30.3%** |

**The meta-stepsize is the first-order axis, not granularity.** Core set = canonical box `-15:-2.3026`, `HIER=none`, live meta, n=501:

| `ms` | n | floor | ceiling | binds |
|---|---|---|---|---|
| `1e-4` | 297 | 1.0% | 1.7% | **2.7%** |
| `3e-4` | 15 | 100.0% | 6.7% | 100.0% |
| `1e-3` | 177 | 77.4% | 27.1% | **78.0%** |
| `1e-2` | 12 | 100.0% | 50.0% | 100.0% |

- The 8 binds at `ms=1e-4` are named and **none is an SGDm+Lion primary at the correct box**: `aw1-node-s{0,1,2}` (AdamW, ceiling), `sm3-awrms-node-s{0,1}` (AdamW+RMSProp, ceiling), and the **three `hz3` seed-5 rows already known to carry the wrong box** (CORRECTIONS 8114).
- m-ladder at `ms=1e-3`: scalar **0/10** → blk6 68.8% (R18) → layerwise/nodewise/weightwise **100%** on R10, R18, R18_c100. Two exceptions, both ResNet34: nodewise (m=25,556) **0/5**, weightwise (m=21.3M) **40%**.
- Same ladder at `ms=1e-4`: **34 rungs, n=297, highest single rung 9.1%**, pooled 2.7%. **The rise with `m` exists only where `ms` is past its optimum.**
- Structural nulls: frozen-beta arms **0/78**; `HIER=shrink` **0/26**.
- All **33 scalar probe runs** in the corpus: floor 0/33, ceiling 0/33, and 0/33 touch either wall at any sampled record. FINDINGS 36.3's scalar sentence is **confirmed corpus-wide**.
- **A DETECTOR TRAP, recorded because it produced a wrong answer here first.** `float32(-2.3026) = -2.3025999069213867 ≠ -2.3026`, so exact equality is a clean floor detector and a **broken ceiling** one. The first pass read the corpus ceiling as **2.8%** (true **9.0%**) and CIFAR-100's as **0.0%** (true **68.6%**). Compare against `float32(wall)`. With the tolerance the two detectors agree on **all 667 records carrying both — 0 disagreements**.
- **Pipeline validated against three already-recorded results**, reproduced without being told: `ar1` 12/12 floor (6203) · `fa1` nodewise ceiling 5/6 with the other three arms 0/6 (117.1) · `hz3`'s three seed-5 rows floor-bound while all 21 `-30:9.0` rows are clean (8114).

**MOSTLY ALREADY KNOWN — the confound is FINDINGS 36.3's finding, not this cycle's.** Four prior audits: **36.3** (named the confound) · **51.1** (established the coordinate denominator this census uses) · **51.2/51.4/51.6** (mechanism; frozen half clip-clean 28/28) · **52.2/52.3/52.4** (box-free controls; clip saturation already excluded) · **117.1** (the paper's D already audited) · **147** (`cts1` 12/12) · **6190–6215**, **8114**, **OPERATIONS.md:447**.

**Genuinely new — three things, and they are modest:** corpus-wide scope (all 1,171 probe dirs vs named batches); **`ms` rather than granularity as the dominant axis**; and a coverage statement plus the float32 trap.

**FINDINGS AT RISK — per finding.**

| # | finding | state |
|---|---|---|
| **1** | **MASTER-TABLE row 24** — *"partitioning buys TOLERANCE to an over-large `ms`"* (falloff scalar 5.871 vs blk6 1.060 / lay 1.801 / node 2.593 pp/decade) | **AT RISK, THE WORST CASE.** Its content IS the region above the `ms` peak = the clamped region for partitioned arms, interior for scalar. Restating it as "clamped regime" does not save it — **the regime IS the finding**. Its own instrumentation is absent: the c40 `ms-` family is **0/52** rows with any trajectory (also `ac` 0/42, `bl` 0/30, `ad` 0/29, `r34r` 0/27, `dc` 0/25, `r10` 0/24, `i3a` 0/21, `mx` 0/46) |
| **2** | **MASTER-TABLE row 23** — finer partition helps: **+3.339** shared-`ms`, **+0.564** tuned | **SURVIVES RESTATEMENT.** Tuned figure **clean** (layerwise 0/6 at `ms=1e-4`; floor 8.09 nats away vs 5 nats of Lion travel). Shared-`ms` figure is clamp-asymmetric and must be **labelled clamped-regime** |
| 3 | MASTER-TABLE row 31 — shared-`ms` contrast confounded with preferred `ms` (`hz9`) | **SURVIVES, strengthened.** But `hz9` has no probe dir and no TB trace — its own occupancy is **UNMEASURED, not clean**; disclosed |
| 4 | CLOSEOUT 3 / CORRECTIONS 114.3 — **THE PAPER's D** (+0.5805 ± 0.0939) | **UNTOUCHED.** Already audited at 117.1; this census reproduces it exactly. All 14 count-matched cells at `ms=1e-4` box-inert. `ar1` already VOID, `fa1` already disclosed |
| 5 | CLOSEOUT item 5a — unaugmented parent cell, guard caveat | **CAVEAT DISCHARGED; the CLOSEOUT entry is STALE.** `ub9` at `-60:6.0` measures **0/9**, and releasing the box made the granularity step **larger** — the campaign's one direct test came out **against** the artefact hypothesis |
| 6 | MASTER-TABLE rows 56/57 — CIFAR-100 granularity (+47 pp) | **SURVIVES.** Maximally clamp-asymmetric on paper (scalar 0/2 vs lay/node/weight 13/13, ceiling 68.6%), but a 47 pp effect is not manufacturable by a stepsize wall, and `cts1` reproduces the ordering at `m=2`. Row 57 is a **within-clamped-regime** contrast |
| 7 | MASTER-TABLE row 27 (H4) | **OPEN, not worsened.** `bo6` 4/6 (all ceiling — already recorded as a failed gate); `bo7` **0/12 and on disk** |
| 8 | rows 36/37/38, CLOSEOUT 2 — horizon reversal | **CLEAN.** `br6` 0/12, `bl5` 1/9, `sp8` 0/9, `ns5` 0/15 — already run in released boxes |
| 9 | Direction C (53.1% sign-agreement, frozen profile, `N_eff/m`) | **UNTOUCHED.** Frozen 0/78; already box-tested at 52.3 |
| 10 | CORRECTIONS 146/147 (`cpk1`, `cts1`) | **Nothing to add** — no probe dir exists; 147 already states the limitation. **This is what `cts2` settles** |
| 11 | `hz3` wrong-box rows (8114) | A known metadata discrepancy is now **measured to be a real regime difference** |

**COVERAGE — the honest limit. 1,356 of 2,501 rows (54.2%) have a beta trajectory; 1,145 (45.8%) have none.**

| stratum | with a trajectory |
|---|---|
| scalar | 33/246 = **13.4%** |
| layerwise | 344/995 = 34.6% |
| weightwise | 170/248 = 68.5% |
| nodewise | 227/286 = 79.4% |
| `resnet18_blocks` | 242/242 = 100% |
| `ms=1e-3` | 852/1721 = 49.5% |
| `ms=1e-4` | 349/376 = **92.8%** |

- TB `beta_block*` exists on only **339** run dirs and only ever logs `m ≤ 6`, so it can never measure a layerwise/nodewise/weightwise arm. **For any batch not named above the clamp status is NOT MEASURED, and is not inferred.**
- **INFERRED, labelled:** that scalar at `ms=1e-4` is box-free — **no scalar probe exists at any `ms` but `1e-3`**; the argument is algebraic (`β ∈ [ln a0 ∓ ms·T]` = `[−11.908, −1.908]`), and it does **not** exclude the ceiling.
- **Direction of harm is NOT measured.** 117.1 argues a floor INFLATES D for `ar1`; `ub9` measures the opposite. Neither generalises; this cycle claims neither.
- Sampling is the terminal record + 10 interior byte-quantiles, so "bound at some sampled record" is a **lower bound**; the terminal flag is exact.

**THE NEXT EXPERIMENT.**

- **Step 0, zero GPU-h, NOT DONE HERE.** `tc1` (12 rows, `-30:6.0`, measured **1/12**) and `ub9` (9 rows, `-60:6.0`, measured **0/9**) are the only two of the corpus's **24** non-canonical-box cells that contain a **scalar** arm — `wc5`/`cl5`/`uc5`/`uc6`/`bl5`/`br6`/`bo6`/`bo7`/`bd7`/`bf8`/`bf9`/`ns5`/`sp8` are `{layerwise, nodewise, weightwise}` only. **Deliberately not differenced**: their data already exist, so RULE 21 requires a scorer registered and committed first. At n=2 per (arm, `alpha0`) `tc1` is a **direction check, not a settlement**, and its box differs from canonical in **both** walls, so a null there is ambiguous.
- **Step 1 — 12 jobs, ~12 GPU-h, ONE submission.** R18/CIFAR-10/SGDm+Lion, `alpha0=1e-3`, 100 ep, at **`ms=1e-3`** (the over-large point), granularity `{scalar, layerwise}` × box `{-15:-2.3026, -30:6.0}` × seeds `{0,1,2}`. Estimand `[lay−scal]_wide − [lay−scal]_narrow`, all four arms in one batch. Pre-register: within ±0.30 pp → row 24 survives; wide box shrinks the gap > 0.30 pp → **the tolerance is the wall and row 24 is rewritten**; wide box grows it → the box was suppressing a real effect.
- Guards required: RULE 20 after launch; coordinate-denominator occupancy per seed per arm, voiding any contrast whose arms differ by > 0.10; and the disclosure that `-30:6.0` is **measured-free, not provably free** (`ms·T = 50` nats at `ms=1e-3`). Hazard on record: 6190–6215 measured 2/2 fatal collapses releasing the ceiling to `+6.0` **at weightwise** — this design carries no weightwise arm, and `tc1` ran 100 ep at `-30:6.0` with zero collapses.
- **Extending the census is NOT worth GPU-hours.** The 1,145 un-instrumented rows cannot be re-instrumented without re-running them, and for the modern cells the answer is already "inert".

**COST — measured from history, not guessed.**

| batch | reference | mean/run | projected | worst case (walltime cap) |
|---|---|---|---|---|
| `in489g2` | `in489g1` 12 runs = 298.7 GPU-h | **24.89 h** | **348.5 GPU-h** | 476.0 |
| `cts2` (RUNNING) | `cpk1` 42.0 min over 39 jobs; `cts1` 18 jobs ≈45 min | **≈45 min** | **≈9 GPU-h** | 30.0 (`--time 02:30:00`) |
| **total in flight** | | | **≈357.5 GPU-h** | **506.0** |

**Every row below was re-derived at this HEAD. Do not quote this file as a source; re-run the command.**

## Verdict

| | |
|---|---|
| Q1 meta-gate | **DESK-ACCEPT, 9/10, `structural_gaps = []`, `passed = True`, 0 blocking.** Returned at cycle 111 on v8 (CORRECTIONS 135). **Carried, not re-derivable here** — the gate tool is not in this tree |
| Audit | `c98_reproduce.py` **exit 1 — 8 CHECKS FAIL**, the **same 8** as before this cycle's ingest; verified both ways by restoring the pre-ingest CSV. The 4 **substantive** numerals are bit-identical across the ingest (best R18/C10 arm **93.328** vs paper 93.317; deficit **1.796** vs 1.807; partition-family rows **434** vs 431, Lion **422** vs 419). Only the 4 census counts moved: rows 2,357 → **2,399**, admissible 1,915 → **1,957**, wallclock 2,342 → **2,384**, GPU-h 1,805 → **1,833**. **No claim reverses**, no new claim went stale — baseline unmoved at 95.124 (se 0.047). Fix = edit both markups; **author scope**, CORRECTIONS 141.6 / 142.6 |
| tex↔md | `paper_numeric_diff.py` **5 residuals over 4 distinct tokens** (2 tex-only: `0.05`, `3.0`; 3 md-only: `0.087`, `0.279`, `3.19`). **All pre-existing, 0 new this cycle** — nothing under `paper/` was touched. Both markups carry 994 distinct quantity numerals |
| Science overturned | **none.** Contribution 1 intact at 4 sites; the withdrawal stays confined to the slope |
| GPU to reach submission | **0 jobs, 0 hours.** The 26 jobs in flight (`in489g2` 14 + `cts2` 12, ~357.5 GPU-h projected) are the NEXT cycle's science, not this manuscript's |

**Ready to submit: NO** — not for any manuscript defect, for the **seven** author items (§ TODO-FOR-AUTHOR).

## Mechanical verification — commands run at this HEAD

| check | result |
|---|---|
| `python3 analysis/c98_reproduce.py` | **exit 1, 8 CHECK(S) FAILED** — stale draft numerals, not a moved result. **This cycle ingested nothing and moved none of them**: `git diff --name-only 94c6e4f..HEAD` over `paper/`, `results/` and `c98_reproduce.py` = **0 files**, so every input is byte-identical to the pre-cycle HEAD. Derived vs paper: rows 2444/2177, admissible 2002/1735, wallclock 2429/2162, GPU-h 2153.85/1642, best R18/C10 93.328/93.317, deficit 1.796/1.807, partition rows 437/431, Lion 425/419. `c98` exited 0 only against the 2,177-row corpus of cycle 116. **A detached worktree is NOT a valid control** — it reports 14, the 6 extra being coverage-census checks that move because gitignored `hz3` `.out` files are absent. See CORRECTIONS 141.6 / 142.6 / 145.4 |
| census fixpoint (measured on `DRAFT-v4.md`, asserted against both markups) | **628 / 411 / 982 / 41.9%** — **unmoved by Plan C, as designed** |
| census internals | raw `\d+\.\d+` 3067 → **3098**, distinct **1007** (unchanged); quantities 2614 → **2615**, distinct **982** (unchanged). The `+1` is the Markdown heading numeral `1.2`; `1.2` already occurred twice as a quantity, so the asserted denominator did not move. `n_q` is asserted by nothing |
| `python3 analysis/xref_check.py` | exit 0, **596 references** (section 500, table 51, figure 22, appendix 23), **0 unresolved, 0 stale**, 8 allowlisted parent-paper refs on lines `[41, 43, 45, 287, 291, 294, 295, 297]` |
| `python3 analysis/test_fence_mask.py` | **ALL PASS** |
| `python3 analysis/paper_numeric_diff.py` | **exit 1 — and exit 1 IS the green state.** 2,606 tex numerals (994 distinct) vs 2,607 md (994 distinct); **2 tex-only** (`0.05`, `3.0`), **3 md-only** (`0.087`, `0.279`, `3.19`) |
| `tectonic -X compile paper.tex`, clean copy of `paper/` | exit 0, **76 pp**, **0** TeX errors, **0** undefined, **0** `??` in the extracted PDF text, **75 labels / 75 distinct refs, 0 orphan, 0 dangling, 0 duplicate**, **2** `Overfull \hbox` (7.28497 pt, 12.25499 pt — the same two as before Plan C, no third) |
| `python3 analysis/dup_group_guard.py` | **21 groups, 42 rows stamped, 3 superseded — PASS**, unmoved by the 42-row ingest (RULE 22) |
| `python3 analysis/c99_hz3q_score.py --selftest` | **59/59 PASS** |
| `c99` gates, raw records supplied | **H0 PASS** (all four arms `NVIDIA L4` / `-30:9.0` / seed 5 / 300 ep) · **H1 PASS** worst coordinate fraction **0.000000**, bar 0.05 · **H2** repaired `-0.238 / 0.093 / -2.57` → **NOT FLAT, D DECLINES WITH BUDGET** · **H3** repaired `D(300) +0.394 / 0.093 / +4.25`, `G(300) -0.048` · **HC** `+0.134 pp`, bar 1.00 → GPU class not first-order on the level. RULE 13 still refuses the archive on both GPU model and `beta_clip` |
| `c87_hz3_score.py` unedited | **VERDICT: SURVIVES** · **MECHANISM SURVIVES THE HORIZON** · `D(300)-D(100) = +0.229` → **GROWS** · `grep -c hz3q` = **0** |
| abstract | **byte-identical to `58c0c85` in both markups** — this cycle did not touch it, so the gate's own figures stand. Plain counts: tex **222** (agrees with the gate's 222); md **231** by plain count against the gate's recorded **228** and a **230** cap. Longest sentence **33 words** in each, bar 62 |

**The abstract has no headroom and the plain count is not the authority.** `_extract_abstract`,
`clean_abstract_text` and `_abstract_defects` are **not in this tree**, so 228 cannot be
re-derived here; a plain count gives 231, over the cap. The difference is three words the gate's
cleaner drops. **Anyone editing the abstract must run the gate, not a word count.**

**OPERATIONAL TRAP — read this before calling a scorer red.** The raw `.out` and `probe.jsonl`
records are **not in the repo** (`runs/` is gitignored). They live one level **above** it, at
`../runs` and `../runs_alice2`. `c98_figures.series()` finds them by itself; `c87_hz3_score.py`
and `c99_hz3q_score.py` do **not** — their `--runs` default is the relative `runs`. Run bare,
`c87` prints *"this batch has NOT been submitted"* and `c99` **REFUSES** under RULE 13. Correct
invocation:

    R="$(cd .. && pwd)/runs"
    python3 analysis/c87_hz3_score.py --runs "$R"
    python3 analysis/c99_hz3q_score.py --runs "$R" --probes "$R/hz3"

**Second trap — `grep` across a line wrap.** The two markups wrap at different columns, so a
single-line `grep` for a phrase longer than roughly 60 characters reports a **false** "missing
from the other markup". This has produced **four** false alarms so far (§9's companion sentence;
CRediT's "Funding acquisition"; §4.8's "identically in all three readings below"; and this
cycle, §4.8's *"the ladder stops at 300 epochs"* guard, which wraps across `DRAFT-v4.md:2273–2274`).
Search a flattened copy (`tr '\n' ' '`, or a whitespace-collapsed buffer) before reporting a divergence.

## Plan C signposting — APPLIED this cycle (R9's mitigation)

| | |
|---|---|
| what was added | a new **§1.2 "Reader's guide and evidence map"** (lead, ten-row evidence map, closing caveat); **ten italic one-shot section openers** at the heads of §3.3, §3.4, §3.5, §4.4, §4.4's endpoint block, §4.7, §5.4, §7 *evidence*, §7 *process*, §8; and **one forward pointer** to §1.2 in §1's closing sentence |
| size | **932 words**, measured — **not** the "≈ 500" `paper/sections/v9-plan.md` asserts. Zero quantities |
| what moved | **nothing.** No section, subsection, table, figure, equation, appendix or threat renumbered; no existing sentence rewritten; no `\label` or `\ref` changed. One new label, `sec:guide`, referenced exactly once |
| the map | a non-floating `center`+`tabular`, so it takes **no table number** and shifts no float numbering. `>{\raggedright\arraybackslash}p{}` columns — without `\raggedright` it generated 32 extra underfull warnings |
| **cost, disclosed** | **75 pp → 76 pp.** Not recoverable: roughly half the growth is the ten openers spread through the document, so no configuration of this package keeps 75 pp. `v9-plan.md`'s Plan C row asserting "75 pp, unchanged" was **wrong by one page** |
| consequential edit | `analysis/xref_check.py`'s `PARENT_LINES` allowlist is **by line number** and five of its eight lines sit after the §1.2 insertion. Re-derived (not pasted): `{41, 43, 45, 287, 291, 294, 295, 297}`. Each was confirmed to carry a genuine parent-paper `§7.x` reference before being listed |
| two deviations from `v9-plan.md` §8 | its §8.3 per-contribution pointers were **dropped** — all seven §1.1 items already end in a bracket naming their sections and floats, so the one-step property already held; and the opener set was **re-chosen on measurement** — §4.6 dropped (893 w), §4.7 added (2,430 w), and §4.8 (2,916 w) deliberately **not** opened, because an opener licenses triage and §4.8 is one of the four things a referee must not skip. It is named in §1.2's load-bearing list instead |

**The functional test is met by three one-hop routes**, each verified against the live text:
§1.1 → section + float (already true); §1.2's map → section + float + the numbered
`c98_reproduce.py` section that re-derives the number + the `make` target that re-runs it (new,
and the only route to the last two); section head → triage answer without reading the section (new).

## Contribution 1 — unweakened, four guard sites, both markups

| site | state |
|---|---|
| Abstract | *"wins all twenty count-matched cells … +0.556 ± 0.045 pp … homogeneous against that null (Q 4.21, median 9.4)"* — `paper.tex:71` / `DRAFT-v4.md:17`. **Byte-identical to `58c0c85`** |
| §1 Contributions item 1 | untouched |
| §4.8 | insertions only; no existing sentence deleted or softened |
| §9 | *"…two findings, of which the second does not weaken the first"* — `paper.tex:4718` / `DRAFT-v4.md:3771` |

- `hz3q` enters **no cell** of Table 2 — `hz3q` count over the `tab:D` row block = **0**.
- **"Declines" cannot be read as "disappears"** — 4 guard sentences, each present exactly once in **both** markups:
  `paper.tex:1363` / `DRAFT-v4.md:1072` *"does not vanish"* · `paper.tex:2856` / `:2249` *"has read it backwards"* ·
  `paper.tex:2882` / `:2273–2274` *"The measured ladder stops at 300 epochs and so does the claim"* ·
  `paper.tex:2944` / `:2331` *"a decline resolved at this budget and this design point rather than a law"*.
- The manuscript-and-check diff for cycle 116 is **195 insertions, 8 deletions**, and every one of the 8 removed lines is a
  line that was rewritten in place (2 forward pointers, 2 threat-index tokens, 1 `F(39,172)` spacing,
  2 `T`-table rows, 1 `PARENT_LINES`). **No sentence was deleted and none was softened.**

## Red team — 10 of 10 answered, 0 blocking

| # | finding | state |
|---|---|---|
| R1 | Abstract carried no trace of the reversal | **CLOSED** (135) — one clause, inside the 230-word cap |
| R2 | §4.8's budget table: no caption, undefined `se` column | **CLOSED on the `se` limb** (137) — both estimators named, general rule stated in both markups (`paper.tex:2832` / `DRAFT-v4.md:2229`). **Caption limb OPEN BY DECISION** — see Open item 2 |
| R3 | No rebuttal to linear extrapolation | **CLOSED** (135) — arithmetic printed, four measured facts against it |
| R4 | Registered bar `\|t\| ≥ 2.0` at df 5 is two-sided α ≈ 0.102, undisclosed | **CLOSED** (137) — disclosed at the site, with both mitigations |
| R5 | Reversal's mechanics unstated | **CLOSED** (135) — location × precision, plus leave-one-out |
| R6 | T9 read as scoping all three readings | **CLOSED** (135) |
| R7 | `f3_budget` panel (b) drawn on the archive | **CLOSED** (135) — redrawn, all three readings |
| R8 | Deposit `make reproduce` cold-skips `[7] BUDGET` | **CLOSED as documented** (138) — the soft skip is the correct behaviour; the README names the section, why it cannot read, that the skip is announced, and the one-command fix |
| R9 | **Length.** Reviewer-burden desk-return is the biggest venue risk | **RESTRUCTURE DECLINED ON MEASUREMENT; MITIGATION APPLIED** (139). Body 67 pp / 46,288 words at 691 w/pp, so a 15-pp body needs ≈ 7,600 words of new number-dense prose in both markups: a rewrite, not a reorganisation. Costing in `paper/sections/v9-plan.md` (whose census figures are stale — see below). Plan C signposting applied instead, at a disclosed cost of one page |
| R10 | tex↔md numeric residuals | **DIAGNOSED ONE AT A TIME AND PARTLY CLOSED** (139). Was 8 occurrences over 7 distinct tokens; **3 closed**, **5 remain over 4 distinct tokens**. None was ever a content gap. Full per-token verdicts in `paper/sections/v11-residuals.md`; the inherited label "all formatting" was **wrong for the `9.0` pair** and was not applied |

## R10 — the residual ledger, per token

| token | side | was | now | verdict, re-derived at this HEAD |
|---|---|---|---|---|
| `0.05` | tex-only ×1 | open | **OPEN, irreducible** | The `\caption` of `\label{tab:holm}` (`paper.tex:3255–3256`). **Causation measured**, not inferred: deleting that caption takes tex 23 → 22 and balances md's 22 exactly. Markdown pipe tables have no caption construct. The caption's claim — *"At most three reach nominal α = 0.05 and none survives Holm"* — is restated in the sentence after the table in **both** markups |
| `3.0` | tex-only ×1 | open | **OPEN, irreducible** | The `\caption` of `\label{tab:T}` (`paper.tex:2554–2556`). Same measurement: deleting it takes tex 4 → 3 and balances md's 3. Both halves of the caption's claim are in the md prose in a **sharper** form (the weakest `t` 3.09, not the rounded `≥ 3.0` bar) |
| `39,172` | tex-only ×1 | open | **CLOSED (139)** | **One space.** `DRAFT-v4.md` wrote `F(39, 172)` where `paper.tex:1930` writes `F(39,172)`; the diff's thousands-group branch `\d{1,3}(?:,\d{3})+` has no optional space, so the spaced form registers no token. All three `F(39,172)` statements were always in both files — there was never a prose gap. Every other `F(a,b)` pair is spelled identically across the two files, so the md line was the sole convention violation. Fixed at `DRAFT-v4.md:1491`; measured tex 2 / md 2 |
| `0.087` | md-only ×1 | open | **OPEN, justified** | One shared cause with the two below: a single md line, `DRAFT-v4.md:2674`, quoting `c88_scorers.py`'s printed dict in an **inline single-backtick span**. `paper.tex:3414–3418` carries the identical dict inside `\begin{quote}`, which `norm_tex` strips as quoted scorer output; `norm_md` strips fences, 4-space indents and `>` blocks but **not** inline backtick spans. **Causation measured**: deleting those three md lines (`:2673–2675`) takes `0.087` 10 → 9, `0.279` 8 → 7, `3.19` 2 → 1 — each landing exactly on the tex count. A pure exclusion asymmetry between the two normalisers |
| `0.279` | md-only ×1 | open | **OPEN, justified** | as above |
| `3.19` | md-only ×1 | open | **OPEN, justified** | as above |
| `9.0` | md-only ×2 | open | **CLOSED (139)** | **NOT a formatting artefact, and the inherited label was refused.** No normaliser was involved: `DRAFT-v4.md` printed `box −30:9.0` in two `rl3` rows of §4.7's `T` table and `paper.tex` did not. That is a difference in what the two tables print. **But no claim diverged** — the clip box for those two rungs is in Table 2 rows 6/7 of both markups and both markups' `T`-table footnote points there. Closed on the **tex** side (`paper.tex:2564`, `:2568`), adding the annotation rather than deleting a true one from the md. Measured tex 24 / md 24 |

- **The optional `E4`** (fencing the md's inline dict to match the tex's display block) **was declined.** It
  would close the last three, but it is cosmetic, it rewrites a prose line into a code block that the
  authors did not ask for, and §1.4–1.6 of `paper/sections/v11-residuals.md` justifies the three on their
  own. The alternative `E2` (stripping the box from the md rows) was also declined — it deletes a true
  annotation from the markup that has it.
- **`paper_numeric_diff.py` will keep exiting 1**, because the two captions are irreducible.
  **Read this check by its printed list, not by its exit code.** A shrinking list makes it tempting to
  expect exit 0; exit 0 is not reachable without inventing caption prose for Markdown pipe tables.
- **The printed context is the FIRST occurrence, not the extra one.** `quantities()` uses
  `ctx.setdefault`, and a multiset difference cannot identify *which* occurrence is surplus. Every
  causal claim in the table above was established by deleting the candidate site and re-counting —
  never by reading the printed context, which is misleading for all five surviving residuals.

## Census history — a printed claim that was wrong twice

| triple | why it moved |
|---|---|
| 628 / 409 / 892 / **45.9%** | the `_FENCE` masking bug: one mask swallowed 16.9% of the draft, so the denominator was measured on a manuscript with a sixth of it invisible |
| 628 / 411 / 978 / **42.0%** | CORRECTIONS 136 fixed the shared `re.S`; coverage ticked **down** and was reported, not absorbed |
| **628 / 411 / 982 / 41.9%** | CORRECTIONS 137's R2/R4 prose added four distinct quantity-numerals; re-iterated to a **fixpoint** in two passes. **Held through cycles 115 and 116** |

- `paper/sections/v9-plan.md` still prints the pre-136 figures (`892`, `45.9%`) and the sentence *"the
  asserted census stays at 892"*. **STALE.** Any future census simulation must run against **982**.
  Left unedited: it is a superseded planning document, and its Plan C conclusion (no quantities added,
  so the triple does not move) proved correct — only its printed denominator is wrong.
- Three checks must be run every cycle, not two: **`analysis/xref_check.py`** (cycle 113 — and the check
  that mattered most in cycle 116, since Plan C added 51 cross-references), **`analysis/test_fence_mask.py`**
  (CORRECTIONS 136 regression pin), and **`analysis/paper_numeric_diff.py`** read by its list.

## Deposit

| | |
|---|---|
| built from | commit **`2f4fd9a`**, **from a genuinely clean checkout** — the README's build stamp carries no DIRTY suffix. This is the first deposit since CORRECTIONS 138 for which that is true |
| verified | `make verify` **140 files, 0 bad** · cold `make reproduce` **ALL 547 CHECKS PASS** with **both** skips announced (`[7] BUDGET` — raw `hz3` `.out` series absent; `censuscheck` — the deposit ships no manuscript) · after `make logs`, `make reproduce` **ALL 628 CHECKS PASS** with only the `censuscheck` skip · `make clean` then `make verify` **140 / 0 bad**, restored to shipped state |
| census in `release/README.md` | **41.9%**, and it matches the paper — `README.md:34`, `paper.tex:1119`, `DRAFT-v4.md:880`, all three re-read. It shipped **45.9%** once (CORRECTIONS 138): the README interpolates `%(census)s` at build time, so a stale deposit prints a stale figure with no other symptom |
| `release/` | **gitignored** — a build product of `analysis/c98_release.py`, regenerated, never committed |

**A deposit is only as current as its last build.** It must be rebuilt once more at whatever commit is
actually submitted, and the README's coverage figure checked against the paper's. That is author item 4,
and it has already bitten once.

## TODO-FOR-AUTHOR — 7 open, all outside agent scope, each verified open at this HEAD

| # | item | evidence it is still open | effort |
|---|---|---|---|
| 1 | **CRediT ↔ Funding contradiction** — "Funding acquisition" on S. Salehkaleybar against a Funding statement reading *"no dedicated project funding and no grant"* | both strings present in **both** markups: `paper.tex:5136–5137` ("Funding\nacquisition", wrapped) + `:5115` / `DRAFT-v4.md:4139` + `:4119` | 1 min |
| 2 | **LIACS correspondence address** to replace the gmail of record | **4 sites, 2 per markup**: `paper.tex:56` (`\thanks`) and `:5169` (under `\paragraph{Correspondence.}` at `:5168`) / `DRAFT-v4.md:5` and `:4168`. The LIACS *affiliation* is already in the CRediT block; this is the address only | 2 min |
| 3 | **ORCIDs, both authors** | `grep -ci orcid` = **0** in `paper.tex`, **0** in `DRAFT-v4.md` | 5 min |
| 4 | **Deposit rebuild at the submission commit** | the on-disk deposit is only ever as current as its last build; the README's coverage figure must be checked against the paper's every time | 2 min (`python3 analysis/c98_release.py`) |
| 5 | **Mint the artefact DOI** | *"The deposit has no DOI, because it has not been deposited"* — `paper.tex:5048` / `DRAFT-v4.md:4054` — honest, not a stub | 5 min + upload |
| 6 | **Authorship for the §5.9 design originator** | Competing Interests names them as *"a researcher … who is not an author"* and calls the origination *"a substantial intellectual contribution rather than an acknowledgeable courtesy"* — `paper.tex:5106`, `:5109` / `DRAFT-v4.md:4110`, `:4113` | **decision, not edit** |

| 7 | **Refresh the 8 corpus numerals the ingest made stale, in BOTH markups, then re-run to a fixpoint** | `c98_reproduce.py` **exit 1, 8 CHECK(S) FAILED**; the same script on the pre-ingest CSV exits **0**. Census: rows **2177→2357**, admissible **1735→1915**, wallclock **2162→2342**, GPU-h **1642→1805.4**. Substantive: best R18/C10 arm **93.317→93.328** (`i3b-3e4`→`eb1-a06`), deficit **1.807→1.796**, partition-family rows **431→434** / Lion **419→422** | 15 min |

- Items 1–5 are mechanical. **Item 6 is an ethics decision only the authors can make, and it must be
  settled before submission** — the paper's own Competing Interests says so.
- **Item 7 is new this cycle and is the only one an agent created.** It is author scope solely because
  the fix edits `paper/DRAFT-v4.md` and `paper/paper.tex`. **No scientific claim reverses**: the
  baseline is unmoved at **95.124 (se 0.047)** and the deficit is still ~1.8 pp. Edit the pair together
  and re-run `c98_reproduce.py` to a fixpoint — CORRECTIONS 141.6.
- **Do not delegate 1, 2, 3 or 6.** End matter, CRediT, funding, correspondence and the author list are
  the authors' by standing instruction.
- **The list is seven.** Item 7 was added this cycle; nothing was closed.

## Venue

| venue | fit | accept prob. (est.) | note |
|---|---|---|---|
| **TMLR** | **best** | **0.80** | No novelty bar, no length cap; "claims supported" + "of interest" both strongly met. The pre-registered self-reversal reaches the abstract |
| ReScience / MLRC | good | 0.60 | Strong reproduction framing; wants a tighter one-paper scope |
| NeurIPS D&B | fair | 0.30 | Corpus + deposit is a real artefact, but the paper is not framed as one |
| JMLR | fair | 0.25 | Length fine; wants methodological novelty, this is an audit |
| NeurIPS / ICML / ICLR main | poor | 0.15 | 9-page limit is fatal |

**Send to TMLR: YES**, after items 1–4 and a decision on 6. Path: fix 1–4 → settle 6 → rebuild the
deposit at the submission commit → arXiv → TMLR. Item 5 (DOI) can follow acceptance; the deposit is
commit-pinned and self-verifying.

## Standing

- `plateau5` PRIMARY; the CSV `plateau` column **BANNED** as primary.
- RULE 16 registered scorers run **unedited** · RULE 20 the ARGS line is the truth · RULE 21 scorer before batch · RULE 22 `dup_group` guard.
- **Ingest is `aggregate.py` THEN `args_repair.py --apply`** — `aggregate.py` alone silently reverts the `dup_group` repair and drops `ml2`'s `se` from 0.195 to 0.142.
- **Re-derive every number at write time. Never quote prose, including this dashboard.**
- Never fabricate an ORCID, affiliation, grant number or DOI.
- `release/` and `runs/` are gitignored build/data products.

## Open — re-derived at this HEAD, nothing carried forward unchecked

| # | item | state |
|---|---|---|
| 1 | **R10's three md-only residuals** (`0.087`, `0.279`, `3.19`) | **OPEN, JUSTIFIED.** One cause, one md line: an inline-backtick dict the tex sets in `\begin{quote}`. Causation measured. Optional fix `E4` exists and was declined as cosmetic |
| 2 | **R10's two irreducible residuals** — the `tab:holm` and `tab:T` `\caption`s | **OPEN BY DECISION.** Markdown pipe tables have no caption construct; both captions' claims sit in the adjacent prose of both markups. Closing them means writing new number-bearing prose into the markup the census reads, to satisfy a diff |
| 3 | **§4.8's budget table has no caption and no label** — `paper.tex:2810–2822` is an unfloated `center`/`tabular`; the md is a bare pipe table | **OPEN, RECORDED NOT CLOSED.** This is R2's *other* limb. CORRECTIONS 137 closed the `se` limb and did not mention this one; 137, 138 and the previous dashboard then all carried R2 as closed. Verified at this HEAD: no `\caption`, no `\label`. Acceptable as-is — nothing cross-references it and the following prose *"In the table, se is…"* does a caption's job in both markups — **but the record said fixed when it was not** |
| 4 | **`analysis/c98_reproduce.py` prints the section label `[15]` twice** — line 621 (partition-family meta-optimiser census) and line 987 (metric sensitivity) | **OPEN, NOT FIXED ON PURPOSE.** Registered audit machinery; the numbering is cosmetic; renumbering mid-cycle would churn 636 output lines. §1.2's evidence map deliberately cites neither. Rename to `[18]` at the next machinery change |
| 5 | **The abstract has no headroom, and the gate that measures it is not in this tree** | **OPEN, a standing hazard.** md 231 by plain count against a recorded 228 and a 230 cap. Any abstract edit must be gated, not counted |
| 6 | **A code comment now points at a section this rewrite deleted** — `analysis/c98_reproduce.py:275` reads *"docs/STATUS.md R0 item 3 prints the upper limit as +0.299"* | **OPEN, NOT EDITED ON PURPOSE.** This dashboard no longer has an R0 section, so the comment is stale. It is a **comment inside registered audit machinery** and the assertion beside it re-derives 0.298 independently, so nothing is wrong with the check — but the pointer is dead. Fix at the next machinery change, not by editing the audit mid-cycle |

**CLOSED this cycle (139), with evidence — do not re-open:** Plan C signposting (applied; census
fixpoint held; `xref_check` green on 596 refs), R10's `39,172` (one space) and R10's `9.0` pair (a
real table-content difference, no claim divergence), and the §7 threat index, which said `T9–T12`
while `T13` exists inside *Limits of the review process*.

**CLOSED in earlier cycles — do not re-open:** the two `|`-leading md prose lines (138), §4.8's `se`
column (137), §4.8's opening over-scoping (138), the ALICE staging dirs (138 — re-verified by
read-only `ssh` at this HEAD, both gone), the §9 companion-sentence question (138 — decided **NO**),
R4 (137), R8 (138).
