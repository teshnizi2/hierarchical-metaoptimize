# STATUS — operator dashboard

Updated 8 Sep 2026 (**cycle 141**). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **167**) > `docs/FINDINGS.md` > everything else.
Manuscript and deposit are both at **`2f4fd9a`** (parent `58c0c85`). **Nothing under `paper/` touched this cycle** (`git status --porcelain paper/` empty).
Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**76 pp**). Corpus = **2,638 rows** (+15 this cycle — `cpg1` LANDED, SCORED, INGESTED). **BOTH queues EMPTY.**
**`c98_reproduce.py` STILL EXITS 1** — reported as-is, inherited, **author scope, deliberately not fixed**. Stale draft numerals (CORRECTIONS 141.6 / 142.6). 628 `chk()` sites, 411 distinct quantity numerals, 41.9% coverage.

## CYCLE 141 (this one) — **`cdn1` REGISTERED AND LAUNCHED: THE CIFAR-100 DENOMINATOR.** CORRECTIONS **167**. NOTHING LANDED, SCORED OR INGESTED

**THE HOLE.** There is **no tuned non-meta baseline anywhere in this corpus outside CIFAR-10**, so nobody knows how far below a plain optimiser the CIFAR-100 phenomenon sits. On CIFAR-10 the denominator is in the abstract (`bl-sgd-01` **95.124** n=5 vs 93.317 n=3 = **−1.807 pp**, `119.11`). On CIFAR-100 there is nothing. Corpus best CIFAR-100 cell, **re-derived this cycle** with `cdn1-*` excluded: **`gm2-ch` 72.054, n=3** (`ResNet18_c100 / chunk771 / ms 1e-4 / α₀ 1e-3 / −15:−2.3026 / batch 100 / AUGMENT=1 / SGDm+Lion`); runners-up `gm2-c22` 72.000, `gc1-ch` 71.951, `gm2-n1d` 71.932.

**24 jobs, ONE submission, `alice2`, ids `4920408`–`4920431`, Submit spread 0 s, seeds {0,1,2}.**

| arm | n | what | horizon |
|---|---|---|---|
| **A** `cdn1-lr{001,002,005,01,02,03}-s*` | 18 | plain **SGD** m 0.9 / wd 5e-4 / cosine-to-0, 1000-step warmup; LR **{0.01,0.02,0.05,0.1,0.2,0.3}** | 100 ep |
| **M** `cdn1-m-s*` | 3 | **in-batch replicate of `gm2-ch`** — makes the gap WITHIN batch and MEASURES the offset | 100 ep |
| **C** `cdn1-h2-s*` | 3 | arm A at lr 0.1, cosine rescaled; **SECONDARY** | 200 ep |

**NOTHING PATCHED.** `--optimizer SGD` routes through the **pre-existing** `SGD_optimizer` branch (cycle 35) in `build_optimizer.py`, sha256 `25a899b3…54c7ec2` pinned by guard 3. `SGD_WD`/`SGD_MOM` **deliberately left at 5e-4/0.9** because `run_cifar.sh` does not echo them and an env value would be unauditable; `COS_TOTAL`/`COS_WARMUP` **are** echoed, so they are passed and audited (**50000**/1000 at 100 ep, **100000**/1000 at 200 — 500 steps/epoch). Live-model checks before submission: `chunk771` allocates **m = 14,595** on today's `HF.py`, byte-matching `gm2`; `ResNet18_c100` is the **CIFAR-style** 3×3-stem R18, 11,220,132 params.

**FLOOR, RE-DERIVED (not copied):** `σ_seed` **0.3713** pp (df **49**, 28 cells, C100/100ep/complete/mean ≥ 60; the unrestricted pool 0.7624 is dominated by the collapsed cut-position arms and is **not** the bar). **SE = 0.30317 pp.** CIFAR-10 tuned-SGD σ is 0.1201, so the bar is conservative by 3.1×.

**PRIMARY `GAP_in` = arm A best − arm M**, both n=3, within batch. Predictions **A 76.0 / M 72.05 / C 77.5** ⇒ **+3.95 pp = 13.0 SE**. Branches (6.60 SE apart): **BELOW-BY-A-LOT** ≥ +3.0 · **CIFAR-10-LIKE** +1.0…+3.0 · **NO-RESOLVABLE-DEFICIT** \|g\| < 1.0 · **ABOVE** ≤ −1.0. Gates in order **V0** 24/24 complete · **V1** every arm > 40.0 · **V2 BRACKETING** argmax must be INTERIOR or every gap is a **LOWER BOUND** · **V3** \|M − 72.054\| ≤ 2 SE = 0.606.

**NO ARM NEAR A FLOOR** (the `cpr1` defect designed out): floors **1.000** (chance) and **22.727** (the corpus's m=1 `ResNet18_c100` `scalar` floor, 10 cells). Worst level under **any** registered account, adverse included, is **+154.9 SE** above m=1 and **+226.6 SE** above chance; the *"arm just died"* model sits **≥ 226 SE** from every account. Live at epoch 6: `lr01-s0` 47.26/52.51, `lr03-s0` 33.36/41.95 — all climbing.

**SCOPE REGISTERED IN ADVANCE:** a gap of any size is a **SCOPE** fact about where the **family** sits, and **refutes no granularity finding** — every granularity contrast is within-MetaOptimize and within-batch, and a common additive offset cancels out of all of them. A small gap would strengthen none of them either.

**RULE 21 margin 72 s** (`1e8e538` epoch **1788848854** → earliest Submit **1788848926**), the NORMAL claim: this scorer has runs of its own. **RULE 20:** 24/24 composed lines PASS pre-submission; post-launch **21/24** `.out` audited clean (arm C PENDING on `QOSMaxGRESPerUser`), `--batch-consistency --strict` PASS per family. **Coverage is NOT yet FULL — no number may be quoted until 24/24.** **Separate ENV audit PASS**, arm A exactly **1** distinct `ENV:` line. Scorer `analysis/cdn1_denominator_score.py` **34/34 `--selftest`**, **default invocation takes no arguments**, guard 5 imports it and proves the default resolves and that the script's ladder **is** the scorer's ladder (`164.2`); every corpus reader excludes `cdn1-*` and §I **verifies** it (`161.9`). **RULE 16:** `git diff -- analysis/` is **additions only** (one new file, 660 lines).

**BUDGET ≈ 22 GPU-h** (A 13.5 / M 3.5 / C 5), ~32 worst case, inside the ~60 h share. Every arm fits `gpu-short`'s 4 h so nothing stalls (`hz3-R2` lesson). 21/24 started within 1 s. **ETA ≈ 11:30 CEST today.**

**NEXT:** at 24/24 — re-run the ARGS audit at FULL coverage, re-run `--envaudit`, ingest, then `python3 analysis/cdn1_denominator_score.py` (no arguments) and score **V0 → V1 → V2 → V3** before `GAP_in` is quoted.

## CYCLE 141 (this one, second batch) — **`cru1` REGISTERED AND LAUNCHED: RULE 11 ON THE HEADLINE CIFAR-100 CELL.** CORRECTIONS **168**. NOTHING LANDED, SCORED OR INGESTED

**THE HOLE.** RULE 11 — compare tuned arms at their own optima — is **open on the exact cell every recent headline comes from**, and `160`'s alias makes the obvious fix impossible. **Re-derived this cycle:** CIFAR-100 carries **exactly two** `ms` levels; **all 42** `scalar`, **all 101** `layerwise` and **all 38** `resnet18_blocks` rows sit at `ms=1e-3`; the **entire** `ms=1e-4` stratum is 20 rows, **all** at `α₀=1e-3`, granularities only {`chunk771`, `nodewise`, `chunk2293`, `nodewise1d`} — **no scalar, no layerwise, no blk6, no cut-position arm.**

**WHY THE ALIAS IS MECHANICALLY FORCED** (guard 4b, off the live source). `HF.Lion_meta_update` is `beta ← (1−ms·wd)·beta − ms·sign(·)`, and every line passes `--weight-decay-meta 0`, so **`|Δβ| = ms` EXACTLY** per minibatch. 100 ep × 500 = **50,000 meta-steps**, so `TRAVEL = 50000·ms` regardless of the loss surface. With clamp `[−15, −2.3026]`, `D_up = −2.3026 − ln(α₀)`. **At `α₀=1e-6`, `D_up = 11.513` and `ms=1e-4` gives `TRAVEL = 5.0`: α can never exceed `1.4841e-4` in the whole run.** That is *why* no such row exists — and why **a ladder in `ms` alone cannot break the alias.**

**WHY THE HEADLINE CELL IS OFF-OPTIMUM, from the corpus itself.** Best CIFAR-100 `plateau5` anywhere = **72.408** (`gm2-ch-s1`), best `best_test` = **72.80** (`gc1-ch-s3`) — **both at `ms=1e-4`/`α₀=1e-3`**, the standard cell otherwise. There `chunk771` 71.9954, `chunk2293` 72.0000, `nodewise1d` 71.9320, `nodewise` 70.4220 — **all above** the headline `layerwise` **69.5945 / 69.5321** at `ms=1e-3`. And on CIFAR-10, the only place this contrast has been laddered, `lay−sc` goes **+3.3711 pp** at the shared `ms=1e-3` → **+0.6241 pp** at `ms=1e-4` where **both** arms peak: a **5.40× shrink**.

| | design |
|---|---|
| arms | `sc` = `scalar` (m 1), `lay` = `layerwise` (m 62) |
| **LADDER A** `α₀=1e-3` | `ms` ∈ {1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3} |
| **LADDER B** `α₀=1e-6` | `ms` ∈ {1e-4, 3e-4, 1e-3, 3e-3} |
| seeds / horizon / probe | **{15,16,17}** (zero collisions anywhere) / 100 ep / `PROBE=100` |
| jobs | **60**, ids 4920444–4920503, Submit spread **4 s = ONE submission** |
| cost | **~45 GPU-h** (median 42.0 min over 274 same-cell runs; `PROBE=100` cost `cfr2` +7.2 %) |

**FOUR `ms` levels {1e-4, 3e-4, 1e-3, 3e-3} appear at BOTH `α₀` for BOTH arms — the alias is broken BY CONSTRUCTION**, and gate `G2` verifies the crossing in the landed runs.

**BAR, re-derived, `cru1-*` excluded from every reader** (and verified excluded, not asserted — `161.9`): σ scalar+layerwise **0.528555** (df 36), **σ scalar 0.613640** (df 18), σ layerwise 0.426833 (df 18). **Frozen rule σ_w = max = 0.613640.** `SE_GAP` **0.501035**, `SE_ΔGAP` 0.708570; bars **1.00207** / **1.41714**. Registered in advance: **the gate uses `max(σ_w, σ_in-batch)`**.

**THREE ACCOUNTS** — **T** tuning-irrelevant (`RATIO ≥ 0.5`), **D** descent-limit (`RATIO < 0.5`, gap monotone in TRAVEL, gap ≤ 2 SE at every FROZEN rung), **F** granularity-inoperative-at-frozen (a **negative control**: `|gap| ≤ 2 SE` at `ms ∈ {1e-5,3e-5}`/`α₀=1e-3`; CIFAR-10 precedent **+0.004** and **+0.027 pp**). **If F fails, the gap is not a step-size-adaptation phenomenon at all and both T and D are incomplete** — the most consequential outcome available. **TWO point-predictors that DISAGREE** and neither adjudicates: X (CIFAR-10 error-ratio transfer, `R_sc` 6.377982 / `R_lay` 3.407429) says **75.762** for `lay` at `ms=1e-4`/`α₀=1e-3`; Y (corpus-internal) caps at **72.408**.

**BRANCHES:** `ADAPTATION-NOT-NEEDED` (argmax rung FROZEN — **terminal, not unresolved**) > `UNRESOLVED-OPTIMUM-AT-LADDER-EDGE` > `GAP-REVERSES` > `GAP-CLOSES` > `GAP-SHRINKS` > `GAP-SURVIVES-TUNING`. Stamps alongside: `TRAVEL-CONFOUNDED`, `MONOTONE-IN-TRAVEL`, `F-HOLDS`/`F-FAILS`, `ALIAS-BROKEN`.

**FLOORS.** Chance 1.000; degenerate-saturation 22.7957 (scalar at the FREE rungs, n 23). **Every model-valid cell clears chance by > 30 SE, worst +57.1 SE.** The **branch-deciding** scalar cells are **53.0 / 68.0 / 78.6 SE ABOVE saturation** — a "the arm just died" model cannot produce them (`cpr1`'s defect at `164`, closed by construction). Three cells get **no point prediction and no branch weight**: `ms=3e-3` ×2 (**no flat-cell CIFAR-10 anchor exists — every `3e-3` row carries `hier=additive`**) and `ms=1e-4`/`α₀=1e-6` (mechanism control).

**THE CONFOUND, NAMED IN THE REGISTRATION:** lowering `ms` tunes **and** limits the descent. Addressed by the automatic `TRAVEL-CONFOUNDED` stamp, by crossing `α₀` (which varies `D_up` 4.605 vs 11.513 at matched TRAVEL — no `ms`-only ladder can), and by `PROBE=100`'s 500 β snapshots per run. **The probe is a SKIP, never a FAIL.**

**RULE 21 margin 193 s** (`180755c` epoch **1788849218** → earliest Submit **1788849411**), the NORMAL claim. Scorer `analysis/cY1_cru1_score.py` sha256 `0de0604c…f516204`, **58/58 `--selftest`**; **default invocation `python3 analysis/cY1_cru1_score.py <runsdir>` has no second argument to forget**, and guard 8 imports the scorer and proves the default probe resolver returns `runs/cru1` (`164.2`). Launcher `bin/cY1_rule11_ms_alpha0.sh`. **RULE 16:** `git diff -- analysis/` **additions only**; `argsline_guard.py` **not edited**. **RULE 20 pre-submission: 60/60 lines PASS** through the unedited guard, checked twice per line. Live `HF.py` sha256 `0d8ee431…42a3892`, **0** `PATCH_REDNORM` markers, recorded in `runs/cru1/PROVENANCE.txt`; the sibling patch is **opt-in by `tn:` spec prefix** and none of these 60 lines carries one. The `cX1` prefix was already taken by the sibling reduction batch, so this batch's artefacts were **renumbered to `cY1` rather than overwriting**.

**OPEN OBLIGATIONS — NO NUMBER MAY BE QUOTED UNTIL BOTH PASS AT 60/60.** All 60 jobs are `PENDING (QOSMaxGRESPerUser)`; the account's GPU cap is saturated by `cdn1`. **No `.out` exists yet, so the RULE 20 post-launch audit and the separate ENV audit CANNOT have been run.**

```
export METAOPT_WS=/home/s5014158/metaopt
python3 analysis/argsline_guard.py $METAOPT_WS/runs --name cru1- --batch-consistency
grep -h '^ENV:' $METAOPT_WS/runs/cru1-*.out | sort | uniq -c    # must be ONE line, ×60
python3 analysis/cY1_cru1_score.py $METAOPT_WS/runs
```

**ETA ~14:00–19:00 CEST today.** Walltime `03:00:00` = 1.51× the slowest same-cell run ever observed (119 min), so this cannot repeat `hz3-R2`'s unschedulability.

**SCOPE, BINDING:** `resnet18_blocks` and the `k49` cut-position arm were **dropped** — either at the full ladder is +30 jobs and +22 GPU-h, and the standing instruction is to prioritise **bracketing** over adding arms. **`cru1` closes RULE 11 for `scalar`-vs-`layerwise` on CIFAR-100/`ResNet18_c100` at 100 ep ONLY — not for blk6, not for cut position, not for class count, not for ImageNet.** The scorer prints that under every verdict.

## CYCLE 140 — **`cpg1` LANDS, SCORED and INGESTED.** CORRECTIONS **166**

**`FINAL: CONTIGUITY-OPERATIVE | INTERACTION-ABSENT | COARSE-MASS-REFUTED-AT-EXACT-MATCH | KC-REPLICATES`** (scorer `cW1_cpg1_score.py` `939ba875…c7755b16`, UNEDITED, exit 0; `--selftest` **137/137 PASS**).

**RULE 20 CLOSED AT FULL COVERAGE:** UNEDITED `argsline_guard.py` (`81cea8b5…b04e5388`) over all **15** `.out` files → **15 clean, 0 mismatch, 0 without an ARGS line, batch-consistency across 15, VERDICT PASS**. **`165.8`'s prohibition is DISCHARGED.** ENV audit: **1** distinct `ENV:` line; exactly **5** `--stepsize-groups` values × 3 jobs. **RULE 21 margin 29 s** as measured (`faac2001` `05:12:26` → earliest Submit `05:12:55`); 15 jobs `COMPLETED`, Submit spread **2 s**, **11.95 GPU-h**. **RULE 16:** `git diff -- analysis/` **EMPTY**; scorer hash identical at `faac2001`, `HEAD`, worktree, `alice2`.

| arm | coarse | TEST (sd) | TRAIN | per-seed TEST s12/s13/s14 |
|---|---|---|---|---|
| `k01` `scalar` | — | **22.9407** (0.3668) | 22.7340 | 22.7420 / 22.7160 / 23.3640 |
| `kP` | `{1..49}` | **55.6280** (0.4118) | 62.6193 | 55.4860 / 56.0920 / 55.3060 |
| `kE` | `{1..47,49,52}` | **55.5013** (0.6579) | 61.9947 | 56.1780 / 55.4620 / 54.8640 |
| `kC` | `{1..48,52}` | **46.6053** (0.2230) | 51.0733 | 46.8260 / 46.3800 / 46.6100 |
| `kG` | `{1..48,51}` | **45.7567** (0.5180) | 50.2673 | 46.3360 / 45.3380 / 45.5960 |

Gates: **G0/G1 PASS** · **R2** 15/15 alive · **R3** worst sd 0.6579 vs bar 2.7766 · **R-CTRL** +32.6873 vs bar 16.1970 · **R-FLOOR** all four INFORMATIVE (worst +30.19 SE) · **R-CEIL** descriptive.

Contrasts (bar **1.511363** = 2 SE, SE 0.755682): `DE` **−0.126667** (−0.17 SE, TRAIN −0.624667) · `DC` **−9.022667** (−11.94 SE, TRAIN −11.546000) · `DG` **−9.871333** (−13.06 SE, TRAIN −12.352000). **Registered vs measured on `DE`: H-COGROUP +7.598000 → resid −7.724667 = −10.22 SE EXCLUDED · H-CONTIG −0.141334 → resid +0.014667 = +0.02 SE WITHIN BAR · H-INERT −9.110667 → resid +8.984000 = +11.89 SE EXCLUDED.** 2×2 `I` **−0.975333 = −0.91 SE_INT** → `INTERACTION-ABSENT`, agrees with primary. Cross-batch `DC` replication resid **+0.012000 = +0.01 SE**.

**KILLS:** co-grouping (−10.22 SE) · inert-beyond-first-hole (+11.89 SE) · **coarse mass AT EXACT MATCH** — `kG` and `cpr1` `kS` share **3,956,288** coarse params and read **45.7567 vs 21.6773**; H-MASS resid **+31.22 SE**, a lower bound since `kS` is floor-saturated.

**`164.5` IS SUPERSEDED IN PLACE (`166.6`) — the prior author's self-correction is UPHELD.** Its `kS`-vs-`kC` contrast conflated hole count with tensor identity: **both leave `conv2` FINE**, and the pair's symmetric difference is a BN scale (50) vs a conv (52). Identity alone predicts `kC − kS = +32.166000` vs measured **+24.428000** — it **over**-predicts by **−10.24 SE**, so the residual has the **opposite** sign to the one claimed. Per arm: `kS` pays **−24.460667** vs `S50 −24.459333` (**−0.00 SE**); `kC` pays **−0.032700** vs `S52 +7.706667` (**−10.24 SE shortfall**). Non-contiguity **costs**. `164.4` had already published that residual three paragraphs earlier. Superseded wording kept verbatim; the **mass** bullet stands.

**WHAT `CONTIGUITY-OPERATIVE` DOES NOT LICENSE (`166.7`) — READ THIS BEFORE QUOTING IT.** (a) **Not** "any hole-separated tensor pays ~0": `cpr1`'s `kS` puts tensor 50 **one** hole out and it pays in **full** (−0.00 SE). The effect rests on **ONE tensor**, `layer4.0.shortcut.0.weight`. (b) **`cpg1` cannot separate it from a no-contiguity "is `conv2` coarse" account** — `level = kP − S49·[conv2 fine]` fits all four sweep arms within bar (worst −1.15 SE), and with one `bn2.weight` term fits **all five** `[49,13]` arms in **both** batches. The two accounts differ on `DE` by **0.19 SE**, 8× under the bar. The only thing favouring contiguity is the prefix-cut anchor `S52` measured at a **different group size** — the composition `164.8(b)` forbids. (c) Structurally unresolvable at `[49,13]`: making 52 contiguous with 49 forces `bn2.weight` in.

**INGEST.** `aggregate.py ../runs ../runs_alice2 > results/all_runs.csv` (**to STDOUT**, `146.7` avoided) then `args_repair.py --apply` (36 `dup_group` recomputations). Row-keyed diff: **2,623 → 2,638, ADDED 15, CHANGED 0, REMOVED 0**, header identical. **Selftest sweep: all 91 `--selftest` files captured in full pre and post, 15 drift, 76 byte-identical, rc=0 62 → 61.** **`165`'s invariance claim HELD and was checked:** `cW1` differs in **exactly one line**, its own designed `0 found → 15 found` sentinel, **137/137 PASS both sides**. **Three verdicts moved:** **`cV1_cpr1_score.py` PASS → FAIL** (its *"no FOREIGN row uses the `sets:` grammar"* exclusivity check, 0 → 12 found — **false-by-construction, LEFT UNFIXED under RULE 16**; `cpr1`'s **scored** `FINAL: UNRESOLVED-PATTERN-UNREGISTERED` and every arm level are **unchanged**), `cK1` 7 → 8 failed checks, `cL1` 6 → 7. All other drift is row counts and the pooled `scalar` archive (22.7739 n=20/7 → 22.7957 n=23/8). **No `FINAL` of any landed batch changes.**

**`161.7e` NEEDS NO NEW RIDER (`166.9`)** — it is already scoped to single-tensor **PREFIX-CUT** steps and `cpg1` adds none; the `161.7b` census table is untouched and no row changes `informative` status. `cpg1` only **strengthens `164.8`'s rider (a)**: the site-52 non-prefix null is now measured twice, on disjoint seed triples, and **with `conv2` coarse**.

**`c98_reproduce.py` STILL EXITS 1** — inherited, author scope, **not fixed**. `git status --porcelain paper/` **empty**.

**NEXT:** second-tensor replication of the out-of-prefix null at **`layer4.0.conv1.weight` (46)** — `cpk3`'s `[45,17]`/`[46,16]` rows give `S46` at `plateau5@100` for **zero GPU**, then one 15-run `[49,13]` batch. If 46 also collapses, contiguity generalises; if it pays in full, the *"only `conv2` matters"* account wins and the token must be renamed.

## CYCLE 139 — **`cpg1` REGISTERED AND LAUNCHED.** CORRECTIONS **165**. NOTHING LANDED, SCORED OR INGESTED

`cpg1` on **`alice2`**: 15 jobs (`4919796`–`4919811`, `4919800` is another submitter's), Submit spread **2 s** = ONE submission, 100 ep, m = 2 and sizes **[49,13] throughout**, seeds **{12,13,14}** (zero `ResNet18_c100` rows anywhere carry them), `PROBE=0`, **~12 GPU-h**, ETA **≤ 18:15 today** (11 started within 5 s; Slurm's backfill puts the four `s14` jobs at 08:13/11:15/14:15/17:15).

**THE QUESTION.** `164.7` killed single-tensor additivity — tensor 52 `layer4.0.shortcut.0.weight` is worth **+7.706667 pp** joining `{1..51}` and **−0.032667 pp** joining `{1..48}` — but `cpr1`'s `kC` moved **three** things at once, so the operative **context variable** is unidentified. `cpg1` adds **one** arm, `kE`, coarse `{1..47, 49, 52}`: `conv2` **IN**, shortcut **IN**, non-contiguous by the **same 3 holes and same max ordinal 52** as `kC`.

| arm | coarse | coarse params | max ord | holes | role |
|---|---|---|---|---|---|
| `k01` `scalar` | — | — | — | — | in-batch m=1 **FLOOR ANCHOR** |
| `kP` | `{1..49}` | 6,315,072 | 49 | 0 | anchor; spec byte-identical to `cpr1`'s `kP` |
| `kE` | `{1..47,49,52}` | 6,445,632 | 52 | 3 | **THE ARM** |
| `kC` | `{1..48,52}` | 4,086,848 | 52 | 3 | fresh-seed replicate of `cpr1`'s `kC` |
| `kG` | `{1..48,51}` | **3,956,288** | 51 | 2 | coarse **AND** fine mass **EXACTLY `cpr1` `kS`'s** — free EXACT-mass control |

**THREE ACCOUNTS REGISTERED, NOT `164.11`'s TWO.** `SIGMA_W` **0.925518** (max of four re-derived estimators, `cpg1` excluded from every reader), `SE_ARM_DIFF` **0.755682**, `READ_BAR` **1.511363**.

| contrast | H-COGROUP | H-CONTIG | H-INERT | H-MASS |
|---|---|---|---|---|
| `DE = kE − kP` | **+7.598000** | **−0.141334** | **−9.110667** | undefined |
| `DC = kC − kP` | −9.034667 | −9.034667 | −9.002000 | −9.034667 |
| `DG = kG − kP` | −8.768667 | −9.002000 | −9.002000 | **−33.462667** |
| `I = (kE−kP)−(kC−kG)` | **+7.864000** | **−0.108667** | **−9.110667** | — |

Separations on `DE`: **A−B 10.24 SE**, B−C 11.87 SE, A−C 22.11 SE — all ≥ 5.1 bars. `H-INERT` is `164.7`'s own zero-parameter rival (fits `cpr1`'s `DC` to −0.04 SE); B and C agree **exactly** on `kC` and `kG`, so **`kE` is the only separating arm**. `kG` re-kills H-MASS at **32.37 SE** at an EXACT mass match.

**NO LIVE ACCOUNT PUTS ANY ARM NEAR THE FLOOR — `164.6`'s defect is designed out and `--selftest` §I enforces it.** Worst of 4 sweep arms × 3 live accounts: **+23.2554 pp above the predicted in-batch floor 22.7739 = 30.77 SE = 15.39 FLOOR_BARs** (`kE` under H-INERT). Predicted levels: `kP` 55.14 · `kE` **62.7380 / 54.9987 / 46.0293** · `kC` 46.11 · `kG` 46.37/46.14. Highest prediction sits **6.7941 pp = 8.99 SE BELOW** the pooled same-cell `layerwise` reference 69.5321 — `R-CEIL` is **cross-batch, DESCRIPTIVE, gates nothing**. **No arm puts tensor 50 `layer4.0.bn2.weight` in the coarse group**: §J re-derives that all 21 floor-saturated m=2 rows (coarse ≥ 17) in this cell have it there and all 51 rows without it are informative.

**THE INVOCATION IS IMPOSSIBLE TO GET WRONG (`164.2`).** `--manifest` is **OPTIONAL and DEFAULTED**; the launcher writes the manifest to **both** of the resolver's first two paths; **guard 8 imports the scorer and proves the default resolves, at submit time**. Documented invocation: `python3 analysis/cW1_cpg1_score.py <runsdir>`.

**RECEIPTS.** Scorer `analysis/cW1_cpg1_score.py` sha256 `939ba875…c7755b16`, **identical Mac/`alice2`**, `--selftest` **137/137 PASS on both**. **RULE 21 margin 29 s** (commit `faac2001` `05:12:26+02:00` → earliest Submit `05:12:55`; both hosts reported epoch `1788837231` in one command, so the clocks agree — **thin vs `cpr1`'s 140 s, reported as measured**). **RULE 16: `git diff -- analysis/` is additions only**, `argsline_guard.py` untouched (`81cea8b5…b04e5388`). **RULE 20 post-launch guard 7 PASS** on a real ARGS line inside the window (`cpr1`'s sat at `RC=2` for a day). `--batch-consistency` **11 clean / 0 mismatch / PASS** at 11 of 15 started — **the 15-run audit is PENDING and no `cpg1` number may be quoted before it passes**; in its place all **15 `SubmitLine` records passed the UNEDITED guard, 0 mismatch, 10 `--expect` flags each**. **ENV audit:** 1 distinct `ENV:` line, 1 distinct non-axis residual, 1 distinct `--export` string, exactly 5 `--stepsize-groups` values × 3 jobs. **No `kL`/`R-EQUIV` arm** — `164.10` forbids quoting it as proof of inertness; guard 1d re-runs `tests/test_namesets.py` on the LIVE tree instead (`ALL CHECKS PASSED`). `bin/PROTECTED.txt` carries `cpg1-`. Corpus **unchanged at 2,623**; `git status --porcelain paper/` **empty**.

## CYCLE 138 — **BOTH BATCHES LAND, SCORED AND INGESTED.** CORRECTIONS **163** (`in489g2`) + **164** (`cpr1`)

| batch | where | runs | scorer (UNEDITED) | **FINAL** |
|---|---|---|---|---|
| **`in489g2`** | `alice` (read-only) | 14/14 COMPLETE | `cI2_in489g2_score.py` `a01ffd94…` | **`COUNT-DISQUALIFIED-POSITION-DOMINATES`** |
| **`cpr1`** | `alice2` | 15/15 COMPLETE | `cV1_cpr1_score.py` `390fb4a4…` | **`UNRESOLVED-PATTERN-UNREGISTERED`** |

**RULE 20 PASS on both** (14 clean / 15 clean, batch-consistency, guard UNEDITED) — this **discharges** the `cpr1` ARGS audit `162.9` left PENDING, so `cpr1` numbers are quotable. RULE 16 clean: `git diff -- analysis/` empty.

**`cpr1`'s VERDICT WAS CORRECTED UPWARD.** `UNRESOLVED-NOT-COMPARABLE` is what the scorer prints when `--manifest` is **omitted**; the manifest was written by the launcher at submit time. Run as documented: **G0/G1/R2/R3/R-EQUIV/R-CTRL all PASS**, `FINAL: UNRESOLVED-PATTERN-UNREGISTERED`.

### `in489g2` — the count statistic is dead, the verdict token is not English

`CAPTURE` at m = 1, 8, 16, 32, 45, 62 = **+0.0000, +0.0080, +0.0250, +0.4566, +0.8762, +1.0000** (TEST 0.9610 … 49.2460; TRAIN 0.9960 … 44.8560; TRAINCAP within 0.0031 everywhere). **R2 FIRES:** at matched **m = 8**, `[8,8,8,8,8,8,7,7]` 1.3450 vs `[45,3,3,3,2,2,2,2]` **8.1870** — **dTEST +6.8420 pp, dCAPTURE +0.1417, t +25.68**, TRAIN agreeing to 0.0010 in capture. Capture is **not** a function of `m`. Pooled within-arm SD 0.266388 (df 7). M50 bracket (32,45], interpolated 33.15, registered `[16,62]` **HIT**, never gating.

- **`POSITION-DOMINATES` is a BAR NAME (`SHAPE_BAR = 0.10`) and is BARRED FROM PROSE.** The position range is **14.17 %** of the count range here, against **71.17 %** on CIFAR-100 — the figure **`160` struck as an overclaim** — and `cJ1` reserves `-DOMINATES` for ratio **≥ 1.000**. Entitled: position **disqualifies** count; it is **not** shown to exceed it. 14.17 % is a **lower bound** (one alternative arm).
- **`144`'s "SIX GROUPS ARE NOT ENOUGH … 47.4 pp cliff" is SUPERSEDED IN PLACE.** Not a cliff (largest adjacent rise +0.4316 < 0.60 bar, R3 silent); not about six (at m = 8 capture spans +0.0080…+0.1497 on cut position alone). Parent-paper corroboration untouched.
- **The `in489g1` anchor pair REPLICATES** at matched E = 84: scalar 1.0333 → 0.9610, layerwise 49.1840 → 49.2460, gap 48.1507 → 48.2850 — both shifts **< 0.3** pooled SD.
- `cI2`'s printed "capture SE ~0.00552" is the **pooled per-run SD** in capture units; the SE of an arm mean at n=2 is **0.003901**. Conservative, no bar affected, not edited (RULE 16).

### `cpr1` — the class account fails on its own control

`SIGMA_W` 0.917280, `SE_ARM_DIFF` 0.748956, bar **1.497912**.

| arm | TEST | sd | TRAIN | vs floor |
|---|---|---|---|---|
| `k01` `scalar` | 22.9140 | 0.1180 | 22.9287 | — |
| `kL` `[49,13]` | 55.5480 | 1.1388 | 62.5387 | +32.6340 INFORMATIVE |
| `kP` `sets:1-49/50-62` | 55.1400 | 1.2741 | 62.2073 | +32.2260 INFORMATIVE |
| `kS` conv2→bn2.weight | 21.6773 | 0.5267 | 21.7187 | **−1.2367 NOT-INFORMATIVE (floor)** |
| `kC` conv2→shortcut.0.weight | 46.1053 | 0.6231 | 50.6920 | **+23.1913 INFORMATIVE** |

`DS = −33.462667` (−44.68 SE, TRAIN −40.488667) · `DC = −9.034667` (−12.06 SE, TRAIN −11.515333).
Registered **H-CLASS** `DS −33.461333`, `DC −1.295333`; **H-POSITION** 0, 0.
**Residual on `DC`: −7.739333 = −10.33 SE** (TRAIN −10.152000). `CLASS-OPERATIVE` needs `|DC| ≤ 1.4979` — it misses by **6.03×**; `CONTIGUITY-OR-COARSE-MASS` needs `|DS−DC| ≤ 1.4979` — **24.4280**, **16.31×**. **The registered branch is arithmetically unreachable.**

**WHAT THE ATTACKS ESTABLISHED — the class account is 0-for-1 on informative arms:**
1. **The `DS` "hit" is WITHDRAWN as evidence.** `kS` is floor-saturated, and the empirical saturation band for this cell at 100 ep is **[21.188, 24.192]** (3.004 pp = 4.01 SE) — H-CLASS's implied level 21.6787 sits inside it. A **content-free** rival, **H-FLOOR** ("the arm just died and reads the floor"), predicts `−32.226000` and is **1.65 SE** from the measurement — **not rejected**; H-CLASS and H-FLOOR are **1.65 SE apart — not separable**. Quotable: the **sign** and the **BOUND `DS ≤ −30.728088`**. **Not** quotable: `−33.462667` as an effect size, or the −0.001333 residual as agreement.
2. **The refuted object is SINGLE-TENSOR ADDITIVITY, not merely "class".** `layer4.0.shortcut.0.weight` (a conv) is worth **+7.706667 pp** joining a coarse group that holds 49/50/51, and **−0.032667 pp** joining `{1..48}` with 49/50/51 fine — **+7.739333 pp = +10.33 SE** vs the registered literal, **+5.97 SE** with all six anchors' noise propagated. Mass and class are **context-invariant**; neither can produce this. (Honest limit: the miss localises to the **pair**, not to either tensor.)
3. **Coarse mass and contiguity die on `cpr1`'s own rows.** `kS`/`kC` are **3.30 %** apart in coarse mass and **≥ 21.69 pp** apart in outcome, while `kP`/`kC` are 35.28 % apart and 9.03 pp apart — no monotone mass function fits both. `kC` has **3 holes** to `kS`'s **1**, its extra tensor at a **farther** ordinal, and beats it by **≥ +21.693421 = +28.96 SE**: **contiguity is refuted with the sign reversed.**
4. **A mass-proportional model fitted exactly to `DC`** then predicts the `cts1` `k51→k52` step at **+0.531451** against a measured **+7.706667** — **+9.58 SE**. Dead.
5. `kS < k01` is **NOT significant** (−1.651 SE, bar 1.4979); 2 of 3 `kS` seeds sit inside the corpus scalar range. **No claim that two groups beat one in reverse.**
6. **A zero-parameter POST-HOC rival, `H-INERT-EXTRA`** ("the out-of-prefix tensor buys nothing", `DC = −9.002000`), fits `DC` to **−0.04 SE** and is **refuted on `DS` at −32.66 SE**. Named as a description of the residual, **never** as a confirmed account.

### WHAT THIS DOES TO CORRECTIONS 161's CLASS PATTERN

**The 15/15 sign census is NOT withdrawn** — every row is a directly measured **prefix-cut** step and `cpr1` contradicts none of them. `161.7e`'s ENTITLED sentence **stands verbatim** (already scoped to prefix cuts). **Three things are narrowed, materially,** and a rider is placed at `161.7e` in place:
- **the boundary is measured** — the first **non-prefix** conv addition in the corpus (site 52, one of the census's own conv sites) reads **NULL, −0.032667 ± 0.748956**. "Moving a convolution into the coarse group raises plateau5" is **false outside contiguous prefixes**;
- **the census's values may NOT be composed** — any per-tensor ledger built by adding/differencing these steps is refuted at **10.33 SE**;
- **`CLASS-OPERATIVE` is retired as an available conclusion** — `cpr1` was the batch built to lift the `index mod 3` alias and it failed to reach the claim on its own control.

`147.6` untouched. `161.7c(i)`'s 256× class/mass alias untouched. `152.12` rival (c) still **UNTESTED**.

### INGEST + SELFTEST AUDIT

`aggregate.py … > results/all_runs.csv` then `args_repair.py --apply` (stdout **to the corpus**, per `146.7`). **added 29 | changed 0 | removed 0**, **2,594 → 2,623**, 38 fields identical. Ingested `plateau5` matches an independent `.out` re-parse to **7.105e-15 pp** on all 29. `args_repair`: 36 rows updated vs the freshly regenerated file (`dup_group` backfill only), **net zero** on pre-existing rows.

**Selftest sweep over the 93 `analysis/` files that mention `selftest`, pre- and post-ingest: 28 → 31 non-zero.** Drifters: **`cI2`** (its own RULE-21 "zero `in489g2` rows" premise — the `156.9` defect), **`cR1`** (`SIGMA_W` 0.917280 → 0.925518, scalar baseline n 17→20, `[49,13]` 9→12 rows — all `cpr1`'s own rows), **`cS1`** (the same equality, inherited). Verified by running each scorer with identical arguments against both corpora: **`cI2` and `cV1` score output byte-identical; no verdict moves anywhere.** The **only** `FINAL` string that changes is `cU1`'s **PREMISE token, `PASS` → `CENSUS-CHANGED`** — a designed self-report; its four substantive tokens are unchanged, so `160`'s recorded `cU1` string is stale in that token only. **`cV1` is the first genuinely ingest-proof scorer in the corpus** (every reader excludes `cpr1-*`); `162.6`'s claim is confirmed by measurement. **Copy `cV1`, not `cI2`.**

**NEXT:** one `cpr1`-sized batch (5 arms × 3 seeds, 100 ep, `m = 2`, sizes `[49,13]`, ~12 GPU-h) to separate **CO-GROUPING WITH `conv2`** from **CONTIGUITY** — the two readings `kC` cannot tell apart. Arms `k01` / `kP` / **`E`** (conv2 IN, shortcut IN, non-contiguous) / `kC` (replicate) / **`G`** (both OUT, coarse mass exactly `kS`'s, a free mass control). Registered read: `E − kP ≈ +7.65` refutes contiguity, `≈ −0.06` keeps it — **10.3 SE apart, no arm near the floor.** Register predictions and scorer **before** submission (RULE 21). See `CORRECTIONS 164.11`.

**No MASTER-TABLE verdict moves. No FINDINGS entry moves. Nothing under `paper/` touched.**

## CYCLE 137 — **`cpr1` REGISTERED AND LAUNCHED.** CORRECTIONS **162**

The batch that breaks the `class == index mod 3` alias `161.7c(ii)` says no prefix cut can break. **A HARNESS CHANGE WAS REQUIRED AND IS THE MAIN DELIVERABLE.** **NOTHING LANDED, SCORED OR INGESTED — corpus stands at 2,594 rows, `grep -c '^cpr1-'` = 0.**

| # | deliverable | outcome |
|---|---|---|
| 1 | **`patches/patch_namesets.py`** — adds ONE `--stepsize-groups` form, `sets:<g1>/<g2>/…` over 1-based indices, ranges and literal parameter **names** | 2 insertions, **no existing line edited**; routing unchanged (`blockwise`, same `beta` shape, same `block_product`) |
| 2 | **backward-compatibility proof** vs the **UNPATCHED** file, run on the LIVE tree | **56 checks, 56 PASS.** N1: **50/50** corpus-drawn specs byte-identical. N2: `sets:1-49/50-62` **==** `[49,13]` exactly. N3: identical `init_meta` state. N5: 11/11 malformed specs raise |
| 3 | **RULE 20 compatibility** — `analysis/argsline_guard.py` **NOT EDITED** | spec is one token of `[A-Za-z0-9_.,:/-]`; `--cmdline` **PASS**, `--batch-consistency` over 15 synthetic runs **PASS**, and the **negative control** (injected duplicate `--stepsize-groups`) is still **DETECTED** → `FAIL`, exit 1 |
| 4 | **the arms**, on the live-model manifest | `kL` `[49,13]` and `kP` `sets:1-49/50-62` compose to the **IDENTICAL** partition; `kS` and `kC` each exchange **exactly 1 out / 1 in** at **identical size 49**; coarse sizes across all four `m=2` arms = `{49}` |
| 5 | **pre-registration** | H-CLASS `DS −33.461333`, `DC −1.295333`; H-POSITION `0`, `0`; bar `SWAP_BAR = 1.497912` → the accounts are **44.68 SE = 22.3 bars** apart on `DS`. Predicted branch **`CLASS-OPERATIVE`** |
| 6 | **noise floor**, RE-DERIVED at registration | `SIGMA_100` **0.917280** (df 58, cells 29, members 87) — horizon-matched **and** the larger, so **USED**; `SIGMA_772` 0.864841 (df 26, cells 13, members 39); `SIGMA_W` **0.917280** |
| 7 | **RULE 21** | commit `76a8fb2` **22:39:15+02:00**, earliest Submit **22:41:35** → **margin 140 s**; Submit spread **2 s = ONE submission**; 15 contiguous job ids |

**ARMS.** 5 × 3 seeds {9,10,11} = **15 runs, 100 epochs, PROBE=0, ~12 GPU-h.** `k01` `scalar` (m=1 floor anchor) · `kL` `[49,13]` (legacy grammar) · `kP` `sets:1-49/50-62` (new grammar, same partition) · **`kS`** swaps `layer4.0.conv2.weight` (2,359,296, **conv**) for `layer4.0.bn2.weight` (512, **BN scale**) · **`kC`** swaps it for `layer4.0.shortcut.0.weight` (131,072, **conv**). Coarse mass `kP` 6,315,072 / `kS` 3,956,288 / `kC` 4,086,848 — `kS` and `kC` differ by **3.30 %**, so a coarse-mass account predicts `kS ≈ kC` while a class account predicts `kC ≈ kP`.

**WHY 15 RUNS AND NOT THE BRIEFING'S 6.** `+k01` because the registered prediction says `kS` lands **below** the m=1 floor and the truncation must be detectable. `+kL` because the batch rests on a harness change and a **measured** equivalence is worth 3 runs (`R-EQUIV`, bar 1.497912; power stated — it can only exclude patch effects **> 1.5 pp**, the static proof is primary). **`+kC` because without it `CLASS-OPERATIVE` is not claimable at all** — `kS` alone leaves class, mass threshold, coarse mass and **contiguity** indistinguishable.

**TWO BRIEFING CLAIMS DECLINED, IN ADVANCE.** (a) The swap does **NOT** separate class from a **mass threshold** — on ResNet-18 the smallest conv is 131,072 and the largest BN tensor 512, a **256×** gap with no overlap, so the two are the same predicate (`161.7c i`). `CLASS-OPERATIVE` therefore ships with a **permanent rider**. (b) **`PROBE` stays 0**, so `152.12`'s rival (c) **remains untested**: at `m=2` `block_product` reduces `<h,g>` to one scalar **per group** before `_probe`, so no interval recovers a per-tensor quantity; getting it needs a **second** patch in the same batch, which is exactly what RULE 20 exists to prevent. Also noted: the briefing's index set `{0..47, 50}` names the **shift**, not the scale — the **names** were followed and the discrepancy recorded.

**POST-LAUNCH RULE 20 — PARTIALLY PENDING, SAID PLAINLY.** `guard_postlaunch` returned **RC=2 UNVERIFIED** (its documented "no job started in 900 s" state — **not** a mismatch): all 15 are `PENDING/Priority`, this account's priority **629,382** is the lowest of five users queued on the three partitions, and Slurm's earliest estimated start is **2026-09-08T02:46:44+02:00** (~4.1 h after submit; full-batch bracket **~5–48 h**). **The `ARGS`-line audit must be re-run when the first job starts** — `python3 analysis/argsline_guard.py $WS/runs --name cpr1- --batch-consistency` — and **no `cpr1` number may be quoted before it passes.** In its place, **Slurm's own `sacct SubmitLine` records** for all 15 jobs were put through the **UNEDITED** guard: **15 clean, 0 repeated-flag/design mismatch, VERDICT PASS** on `--batch-consistency` and again on 9 `--expect` design flags. **SEPARATE ENV audit: PASS** — 15 job ids, 15 distinct ARGS md5s, **1** distinct `--export` string, **1** distinct non-axis ARGS residual, and all 5 arms' `--stepsize-groups` equal to their registered specs.

**No MASTER-TABLE verdict moves. No FINDINGS entry moves. Nothing under `paper/` touched.**

## CYCLE 136 — **`cpk3` LANDS.** CORRECTIONS **161**

**`FINAL: PEAK-CONFIRMED-AT-49 | CONVERGED`** (my own run, scorer `analysis/cS2_cpk3_score.py` **UNEDITED**, sha256 `603971aa…59286d99`, identical Mac / `alice2`; `runsdir` is **POSITIONAL**). 21/21 complete, RULE 20 **PASS** (21 clean, 0 mismatch, batch-consistency across 21, exactly **1** distinct ENV line), RULE 21 margin **120 s**, 1-s Submit spread = **ONE submission**, 12 nodes, 21 distinct md5s.

| # | deliverable | outcome |
|---|---|---|
| 1 | **`cpk3`** — the peak's LOCATION on the consecutive grid | **`PEAK-CONFIRMED-AT-49`**, best `k49` **56.0453** over `k46` **49.5060** by **6.5393 pp = 8.21 SE** (bar 1.5930) |
| 2 | convergence | **ALL SEVEN ARMS CONVERGED** (`CONV_BAR` 0.024235). `k46` (+0.00549) and `k50` (+0.00607) converged but **NOT tight** (`TIGHT_BAR` 0.00426) |
| 3 | in-batch `m=1` floor | **22.8180 @100 → 23.1780 @E**, moved **+0.3600 = 0.45 SE**. All six sweep arms **INFORMATIVE at both horizons** (+7.93 … +32.87) |
| 4 | the five single-tensor steps | measured **in batch**, both horizons, **TRAIN agrees on every sign** (table below) |
| 5 | the registered prediction | **branch HELD, mechanism HALF-REFUTED** — H-MASS mis-decomposes 2 of its 4 steps by **+4.19** and **−3.42 SE**; H-EQUI refuted outright |
| 6 | ingest | **+21 added, 0 changed, 0 removed.** Corpus **2,573 → 2,594**. **0 `in489g2` rows** |
| 7 | selftest audit (92 files, pre vs post) | **26 → 28 non-zero.** `cS2` fails as **PREDICTED** (159) and **no verdict moves** (`score()` output byte-identical pre/post); `cU1` is a **second, unpredicted** drifter and is **benign** |

**THE FIVE CONSECUTIVE SINGLE-TENSOR STEPS** (step = `level(k+1) − level(k)`; positive = moving that tensor into the coarse group HELPS):

| step | tensor | class | params | TEST@100 | TEST@E | SE | TRAIN@E | per-seed sign |
|---|---|---|---|---|---|---|---|---|
| 45→46 | `layer4.0.conv1.weight` | conv | 1,179,648 | **+5.7740** | **+5.7227** | +7.18 | +6.1967 | 3/3 |
| 46→47 | `layer4.0.bn1.weight` | BN **scale** | 512 | **−2.5773** | **−2.7220** | −3.42 | −3.6367 | 3/3 |
| 47→48 | `layer4.0.bn1.bias` | BN **shift** | 512 | +0.1087 | +0.0640 | +0.08 | +0.2573 | 2/3 |
| 48→49 | `layer4.0.conv2.weight` | conv | 2,359,296 | **+9.0020** | **+9.1973** | +11.55 | +11.5767 | 3/3 |
| 49→50 | `layer4.0.bn2.weight` | BN **scale** | 512 | **−24.4593** | **−18.2707** | −22.94 | −18.4107 | 3/3 |

### THE CLASS PATTERN — **WHERE IT MAY AND MAY NOT BE QUOTED**

**`CORRECTIONS 147.6` STANDS.** It withdrew *"a BatchNorm scale has leverage a BatchNorm shift does not"* **as a class-level MECHANISM claim**, on the ground that the property fails to predict the capture **LEVEL** across cut positions. **`cpk3` does not test that proposition** — it measures single-tensor **intervention signs** — so it neither restores nor weakens the withdrawal. **One of `147.6`'s three grounds IS retired**: the "opposite-way" counterexample `k45→k47` (+3.449 pp) is now split in batch into conv **+5.7227** and scale **−2.7220**; the aggregate was positive **because the conv outweighed the scale**.

**MAY BE QUOTED** — as a **sign census**, with the scope sentence attached: over the whole corpus, **every** single-tensor prefix-cut step measured **off** the `m=1` floor carries its tensor's class sign — **conv 3/3 POSITIVE** (3 sites, +5.72…+9.20), **BN scale 7/7 NEGATIVE** (2 sites, −2.72…−25.16), **BN shift 2/2 NULL** (2 sites, both < 0.30 SE); **15/15 sign-consistent** including the 3 floor-saturated `scl1` steps, over 6 batches, 2 horizons, 2 clamp levels, **3 disjoint seed triples**.

> **[NARROWED BY CYCLE 138 / CORRECTIONS `164.8`. The sentence above stands — it is scoped to **prefix-cut** steps — but its boundary is now measured and its values may not be composed.]** `cpr1`'s first **non-prefix** conv addition (site 52, one of the three conv sites counted above) reads **NULL, −0.032667 ± 0.748956**, against **+7.706667** for the same tensor in the prefix context. So "moving a convolution into the coarse group raises plateau5" is **false outside contiguous prefixes**, and any per-tensor ledger built by adding/differencing these steps is **refuted at 10.33 SE** (`cpr1`'s `DC`). **`CLASS-OPERATIVE` is retired as an available conclusion.**

**MAY NOT BE QUOTED** — and the reason is structural, not statistical: **`class == index mod 3` holds at EVERY index 1…60 of `named_parameters()`** (tensors 1–60 are exactly 20 `conv/scale/shift` triples). `--stepsize-groups [k,62−k]` takes a **contiguous prefix**, so **no prefix cut on this architecture can ever separate tensor class from ordinal position** — `cpk3` cannot, and neither can any successor of the same shape (`152.8` reproduced). Class is **also** inseparable from a **mass threshold**: in the measured range the smallest conv (131,072) is **256×** the largest BatchNorm tensor (512), with no overlap anywhere in ResNet-18. So: **no leverage claim, no mechanism, no effect-size law by class, and nothing outside `layer4.0`** — every measured step lies in indices 45…55, one residual junction.

**`152.12`'s three registered rivals, scored on this window:** *(a) norm scale* predicted the largest step at `46→47` — it is the **smallest** non-null magnitude there: **REFUTED**. *(b) first to leave* predicted `45→46` — it is second: **REFUTED**. *(c) clamp turnover* is the only survivor, and only on a loose reading; it explains the two **largest** steps and **fails outright at `45→46`**, which moves the coarse-group terminal `beta` by **0.0000 nats** and still buys **+5.7227 pp**. `PROBE=0`, so (c)'s registered per-tensor `<h,g>` test **was not run**.

**`−18.2707 pp` IS A 772-EPOCH OBJECT AND IS STILL SHRINKING** — **−24.4593 @100 → −18.2707 @E**, a **25.3 %** in-batch attenuation, alongside the coarse-group `beta` gap falling **5.17 → 1.39 nats**. `k50`'s `beta` is still annealing (**−0.004413 nats/epoch** at E). Quote it **with its horizon**; the asymptote stays **UNMEASURED**. Not threatened: the sign (3/3), the rank, or the peak verdict.

**NEXT:** **`cpr1`** — an explicit **name-list** partition (`HF.polish_the_stepsize_groups` already accepts one; the obstacle is `train.py`'s `--stepsize-groups type=str` grammar) that swaps `layer4.0.conv2.weight` for `layer4.0.bn2.weight` **at fixed group count and fixed cut position**. It is the **only** design that breaks the `index mod 3` alias. Then **`cpk4`**, the same five-step decomposition at `layer3.0` or `layer2.0`, for the first class measurement outside `layer4.0`.

**No MASTER-TABLE verdict moves. No FINDINGS entry moves. Nothing under `paper/` touched.**

**CYCLE 135 WAS ZERO GPU AND AUDITED THE RECORD.** CORRECTIONS **160**. Two claims from a four-lens viability assessment were re-derived from `results/all_runs.csv`. **(A) The "cut position dominates group count" overclaim REPRODUCES as an overclaim** — the count range **exceeds** the position range — and three doc lines are corrected **in place, superseded wording kept verbatim**. **(B) The alleged 24.6 pp alpha0 confound on the headline CIFAR-100 cell DOES NOT EXIST** — `FINAL: INTERACTION-ALPHA0-x-GRANULARITY | ORDER-PRESERVED | ASSESSMENT-DOES-NOT-REPRODUCE | PREMISE PASS`. **Nothing submitted, nothing cancelled, nothing ingested; corpus unchanged at 2,573.**

## Cycle 135 — the deliverables

| # | deliverable | outcome |
|---|---|---|
| 1 | **A — the overclaim** | **UPHELD as an overclaim.** Count range **46.783 pp** > position range **33.297 pp**; position recovers **71.2%** of the count span |
| 2 | A — `cbl1`'s registered verdict, re-derived from the CSV | `COUNT-LAW-UNRESOLVED-BALANCE-COMPARABLE`, `BAL_RANGE` **0.4095** / `CNT_RANGE` **0.7841** = **0.5222** (R2 `BALANCE-DOMINATES` fires only at ≥ 1.000) |
| 3 | A — doc corrections | **3 lines**, all in `docs/CORRECTIONS.md`; **0** in STATUS / FINDINGS / MASTER-TABLE / `paper/` |
| 4 | **B — `cU1`** registered (`c47934c`), run **UNEDITED** | `--selftest` **21/21 PASS**; **`ASSESSMENT-DOES-NOT-REPRODUCE`** |
| 5 | `cU1`'s RULE-21 status | **NOT a RULE 21 label** and **NOT a blind test** — states both in its own header. Commit-before-first-execution only: **07:59:16Z → 07:59:21Z, margin 5 s** |
| 6 | ingest / GPU | **NONE.** Corpus stays **2,573**. `results/all_runs.csv` byte-unchanged. No job touched on either account |

### A — the two ranges, re-derived (filters stated in CORRECTIONS 160.1)

Cell: `ResNet18_c100`/CIFAR100/SGDm+Lion/ms 1e-3/α₀ 1e-6/γ=1/AUG 1/box `-15:-2.3026`/batch 100/**100 ep**/`hier` unset/`collapsed=0`/`complete=1`/`superseded=0`. Column **`plateau5`**.

| axis | low | high | range |
|---|---|---|---|
| **COUNT** m = 1 → 62 | `scalar` **22.7492** (n=17) | `layerwise` **69.5321** (n=20) | **46.783 pp** |
| **POSITION** at fixed m = 2 (16 arms) | `[53,9]` **22.0753** (n=3) | `[49,13]` **55.3727** (n=9) | **33.297 pp** |

- Batch-pooled instead of row-pooled: **33.297 / 46.829 = 0.7110**. Same answer.
- Defensible replacement, adopted: **"position at fixed count recovers ~71% of the range the entire count ladder spans."**
- Corrected in place (original wording kept): **145.1 design table**, **146 heading**, **146.3**. `cJ1`'s verbatim R5 quote at 143 is **NOT touched** — it is a scorer quote and its scope (entropy vs position) is correct.

### B — `cU1`: the α₀ × granularity table, TEST and TRAIN

`DELTA = mean plateau5 @ α₀=1e-3 − @ α₀=1e-6`, batch-pooled over the only two batches carrying **both** α₀ levels for **all three** arms (`c100` n=2/cell, `c100b` n=3/cell — balanced 2×3×2, same 5 seeds each side). `SIGMA_W` **0.552209** (df 40, 23 cells, 63 members) re-derived at registration; `MAIN_BAR` **0.712899**, `INTERACTION_BAR` **1.008191**, `ARGMAX_BAR` **0.712899**.

| arm | TEST 1e-6 | TEST 1e-3 | **Δ TEST** | TRAIN 1e-6 | TRAIN 1e-3 | **Δ TRAIN** |
|---|---|---|---|---|---|---|
| `scalar` | 22.6923 | 22.5387 | **−0.1537** | 22.9008 | 22.5342 | **−0.3667** |
| `resnet18_blocks` | 53.0803 | 51.5753 | **−1.5050** | 64.5450 | 63.0942 | **−1.4508** |
| `layerwise` | 69.5532 | 69.7433 | **+0.1902** | 99.0150 | 99.2917 | **+0.2767** |

TRAIN column = `final_train` (the campaign's `train5` is not in the CSV).

- **The claim tested, pre-stated:** `Δ(layerwise) ≤ −20.0` AND `|Δ(scalar)| ≤ 1.0`. Measured **+0.1902** and **−0.1537** ⇒ **`ASSESSMENT-DOES-NOT-REPRODUCE`**. Layerwise moves in the **opposite** direction, by **less than a third of `MAIN_BAR`**.
- **`ORDER-PRESERVED`.** `layerwise > blk6 > scalar` at **both** α₀; every adjacent gap ≫ `ARGMAX_BAR`. **The headline cell's arm ordering does NOT depend on α₀.**
- **What IS there:** a **~1.7 pp** interaction carried **entirely by `resnet18_blocks`** (−1.505 pp = 2.11 × `MAIN_BAR`, same sign on TRAIN). Both endpoint arms are flat.
- **Where 44.968 came from — a stratification artefact:**

| pool (layerwise @ α₀=1e-3) | n | mean `plateau5` |
|---|---|---|
| P0 matched primary stratum | 5 | **69.6540** |
| P1 matched stratum, all batches | 8 | **69.5945** |
| P2 + 20/5-ep rows | 26 | 56.0968 |
| P3 + `hier` additive/shrink, box C, ep ≥ 20 | **39** | 48.2268 |
| P4 everything (any `hier`, box, horizon) | 46 | **44.9773** |

  The assessment reported **n=39, 44.968**: its **value** is P4's, its **count** is P3's — **no single pool reproduces both**.

### Cell census — CIFAR-100, 100 ep, ms=1e-3, `hier` unset, box C

| granularity | α₀=1e-6 | α₀=1e-3 |
|---|---|---|
| `scalar` | **17** (6 batches) | **5** (`c100`,`c100b`) |
| `resnet18_blocks` | **8** (3) | **5** (`c100`,`c100b`) |
| `layerwise` | **20** (7) | **8** (`c100`,`c100b`,`c1b`) |
| `nodewise` / `weightwise` | 0 | 3 / 3 (`c100f`) |

**The meta-stepsize axis on CIFAR-100 is ALIASED, not merely unmapped.** All **33** CIFAR-100 `scalar` rows sit at ms=1e-3; the whole ms=1e-4 stratum is **20 rows, all 20 at α₀=1e-3**, granularities exactly `{chunk2293, chunk771, nodewise, nodewise1d}` — **no scalar, no layerwise, no blk6, no cut-position arm**. Best `plateau5` anywhere in it: **72.4080**. ⇒ **no ms contrast at fixed α₀ exists for any granularity-ladder arm**; `cU1` issues **no ms claim**.

### What cycle 135 changes

- **No MASTER-TABLE verdict moves. No FINDINGS entry moves. `paper/` untouched.**
- MASTER-TABLE's CIFAR-100 transfer row (*"essentially insensitive to alpha0"*, **CONFIRMED**) is **corroborated** by an independent count-matched re-derivation — **one scope line added**: that phrase is exact for the two endpoint arms and **slightly too strong for blk6** (−1.505 pp, resolved).
- **The cut-position thread is untouched and cannot be touched by this:** every cut-position arm in the corpus lives at α₀=1e-6 and **none exists at α₀=1e-3**. Recorded as a scope line on the whole thread.
- **RULE 11 is not closed and is worse than recorded:** on CIFAR-100 ms and α₀ are **perfectly collinear** off ms=1e-3.

## Cycle 134 — the deliverables

| # | deliverable | outcome |
|---|---|---|
| 1 | **`cS1`** — the `k50`/`k52` rate-law break, from `.out` files already on disk | **RUN. `DIFFERENT-KIND \| NON-EXPONENTIAL`.** `k50` is a textbook single exponential (τ **194.9**, ρ within **0.16 bar** of the parameter-free null at every *f*); `k52` is **1.87 bar** off it at *f*=0.90 (τ **80.2**) |
| 2 | `cS1`'s RULE-21 status | **NOT a RULE 21 label** — it has no batch. Claims **commit-before-first-execution only**: `0d82018` **08:23:00** → first run **08:23:05**, **margin 5 s**. The file says so in its own header |
| 3 | **`cpk3`** — the peak's **LOCATION** | **REGISTERED (`a523c3e`), DRY-RUN, LAUNCHED 21/21.** RULE 21 margin **120 s**; 1-s Submit spread = **ONE submission** |
| 4 | the design expanded 6 → 21 runs | every addition justified with what is **lost** without it; **`k=44` DECLINED** with its cost stated |
| 5 | ingest | **NONE.** Corpus stays **2,573**. `results/all_runs.csv` untouched |

## `cS1` — the trajectory verdict (CORRECTIONS 159.2–159.4)

Registered **before first execution**, run **UNEDITED**, sha256 `45b95380…0c6ae8f9`, `git diff -- analysis/` **empty**. Primary column `W(e)` = trailing 5-epoch mean of test accuracy at **every** epoch; `W(771)` **is** `cR1`'s `tail5(772)` and `W(99)` **is** its `tail5(100)`, so the endpoints reproduce 158 to the last digit. CSV `plateau` **banned and never read**.

    python3 analysis/cS1_ratelaw_shape.py ../runs_alice2 --cts3 ../runs_alice2

**The deciding quantity is ρ, which is τ-FREE by construction** — under a single exponential of *any* τ, ρ(f) = ln(1/(1−f)) is a **pure number**.

| arm | τ (sd) | D | ρ(.25) | ρ(.50) | ρ(.75) | **ρ(.90)** | R² | **signrun** |
|---|---|---|---|---|---|---|---|---|
| **k50** | **194.90** (48.28) | 5.9176 | 0.2999 | 0.6848 | 1.3647 | **2.4135** | 0.996–0.998 | 0.054–0.068 |
| **k52** | **80.19** (23.91) | 1.9856 | 0.3205 | 0.5487 | 1.5469 | **4.9799** | 0.889–0.970 | **0.171–0.347** |
| *exp. null* | *any* | — | *0.2877* | *0.6931* | *1.3863* | ***2.3026*** | — | — |

- **Separation at f=0.90 only:** k52−k50 = **+2.5664**, bar **1.4350**, **1.79×**. At f = .25/.50/.75 the ratios are 0.26 / 0.73 / 0.65 — **no** separation.
- **Eligibility was gated in advance.** `k01/k45/k47/k49` all fail **E1** (mean slope@100 between −0.00235 and +0.00051 = converged at 100) and are **printed in full, then excluded**. In-batch `SIGMA_TAIL` **0.109408** (df 882) → `AMP_BAR` **0.489287**.
- **`PI` localises the break IN TIME.** `PI = [W(199)−W(99)]/[100·slope@100]`: k50 **0.684**, **k52 0.275**. **k52's slope@100 over-predicts even the NEXT 100 epochs by 3.6×** — the rate law is already wrong at epoch **199**, not slowly over 672.
- **Cross-batch replication, descriptive:** `cts3`'s k50 (seeds {0,1,2}) gives ρ **0.2865 / 0.6735 / 1.4093 / 2.3759** vs `cpk2`'s. **k50 is exponential in two batches on disjoint seeds** — so k52's departure is not an estimator artefact.
- **THE HONEST WEAKNESS:** the primary statistic is **1.79 bar on df 4**. Real on the registered rule, **not overwhelming**. Corroborated by signrun, R², the 1.87-bar departure from the parameter-free null, and cts3 — but it must be quoted as 1.79/df 4.
- **MAY NOT CLAIM:** any **mechanism**; any **repaired rate law**; an asymptote (A is fitted over a 672-epoch window); anything pooled across batches; anything about k46/k48 or any other cut, cell or horizon.

## `cpk3` — **LANDED, SCORED, INGESTED** (CORRECTIONS 161); the design below is 159.5–159.11 as registered

| | |
|---|---|
| shape | `k` ∈ **{45,46,47,48,49,50}** (CONSECUTIVE) + `k01` scalar floor × seeds **{6,7,8}** = **21 runs**, 772 ep, ONE submission |
| why consecutive | **every step moves EXACTLY ONE TENSOR** (guard 4d, on the live model): `45→46` `layer4.0.conv1.weight` **1,179,648** · `46→47` `bn1.weight` 512 · `47→48` `bn1.bias` 512 · `48→49` `conv2.weight` **2,359,296** · `49→50` `bn2.weight` 512 |
| what that buys | `cpk2` could only measure the **two-tensor aggregates** `45→47` (+2.3847) and `47→49` (+10.5140). `cpk3` **splits both, in batch** |
| k49 in batch | so **“k48 > k49 relocates the peak” is decided WITHIN batch** (F(62,85)=5.47) |
| k50 in batch | so **k49 is STRICTLY INTERIOR**, not at the grid edge — the exact defect cpk2 was criticised for |
| floor in batch | **YES** — one cpk2 measurement is not a replication, and a splice would make the *informativeness* gate cross-batch. Price: `FLOOR_BAR` **1.5930** (3v3) is **wider** than cR1's 1.1488 |
| seeds {6,7,8} | at {3,4,5} **12 of 21** runs would be exact-configuration re-executions (the CORRECTIONS 152 defect). {6,7,8} appear **nowhere in this cell** → **ZERO duplicates**, and a **third** disjoint seed set on k49 |
| **k=44 DECLINED** | closes **no** gap inside 45..50 and cannot move the peak (k45 is 12.8987 pp below k49; left-flank arms gain ~1 pp). **Cost would be 3 runs / ~16.5 GPU-h.** ⇒ **cpk3 may NOT claim monotonicity on 44→49, nor k\* over any range wider than 45..50** |
| 100-ep control | registered again (free). guard 4f: `num_epochs` occurs **exactly twice** in the live `train.py` (line 42 decl, line 135 loop) |
| cost / ETA | **~117 GPU-h** (21 × cpk2's measured 5.546 h); request 11:00:00 each. Slurm says last start **2026-09-09T08:25** — treat as an **upper bound**: for cpk2 Slurm was **2 d 14 h** pessimistic and submit→last completion measured **10 h 58 m** |

**σ_w RE-DERIVED, both horizons, not copied** (156's drift lesson): **100 ep 0.917280** (df 58, 29 cells, 87 members) · **772 ep 0.975496** (df **14**, **7** cells, 21 members). **Frozen rule `SIGMA_W = max(...) = 0.975496`** — horizon-matched *and* larger. ⇒ `SE_ARM_DIFF` **0.796489**, `PEAK_BAR` = `FLOOR_BAR` = **1.5930** (2 SE), `NOISY_BAR` **2.9265**, `PREMISE_BAR` **12.4170** (half cts1's own 24.8340), `CONV_BAR` **0.024235**, `TIGHT_BAR` **0.00426**.

**POINT PREDICTION — `H-MASS`, and it is SEPARABLE from its named alternative.** Mass is *not* a complete law (k49 vs k50 differ by **512 of 11,220,132** params and **20.4993 pp**), but it is not irrelevant (2.00× the mass → 4.41× the gain across the two steps). `H-MASS` = each tensor takes a share of a step ∝ its parameter count:

| arm | **H-MASS (registered)** | H-EQUI (alternative) |
|---|---|---|
| **k46** | **45.8976** | 44.7063 |
| **k48** | **45.9009** | 51.1557 |

**Both should land ON TOP OF k47 (45.8987)**, the whole +10.5140 arriving at `48→49`. The two hypotheses are **5.2547 pp = 6.60 SE** apart on k48 — **this batch separates them**. Predicted branch **PEAK-CONFIRMED-AT-49**, margin **10.5117 pp = 13.20 SE**. **The standing “k48 ∈ [45.8987, 56.4127]” prediction is satisfied at its LOWER ENDPOINT** — recorded now so it cannot later be retold as an unremarkable interval hit. **cpk3 is exactly the test of whether tensors 47 and 48 are “special” the way tensor 50 (the −20.4993 cliff) is.** H-MASS says no; a large |k47−k48| says yes and would be **the first mechanistic handle this thread has had**.

**BRANCHES:** `PEAK-CONFIRMED-AT-49` / `-RELOCATES-TO-46` / `-TO-48` (and −45/−47/−50) / **`PEAK-PLATEAU`** (best−second ≤ bar) / `UNRESOLVED-{NOT-CONVERGED, PROVENANCE, DIVERGED, NOISY, PREMISE, CONTROL, **SATURATED**}`. **`R-CTRL` is deliberately NOT cpk2's** — asserting the 100-ep argmax over a grid containing the never-run cuts would prejudge the measurement; it asserts only `M(k49)>M(k47)>M(k45)` at 100 with `k49−k47 > PEAK_BAR`.

- **RULE 21:** `a523c3e` **08:33:20** → earliest `sacct` Submit **08:35:20** (3 jobs) / 08:35:21 (18). **Margin 120 s**, 1-s spread = ONE submission. Ids **4915304–4915325** (**not contiguous** — 4915307 is another user's).
- **RULE 20 at partial coverage (13 of 21 started):** `argsline_guard --batch-consistency` **13 clean, 0 mismatch, 0 without an ARGS line — PASS**, *“every non-axis flag identical across 13 runs”*. **Horizon verified on the ARGS line: 13/13 `--num-epochs 772`.** No unregistered `--stepsize-groups`. **To be re-run at full 21-run coverage before any number is quoted.**
- **ENV audit (separate — these cannot ride ARGS):** **ONE** distinct `ENV:` line; 13/13 `AUGMENT=1`, `BETA_CLIP=-15:-2.3026`, `PROBE=0`, `HIER=none`, `SCHED=none`.
- **Byte-match to cpk2:** `diff` of the composed `CMD` block vs `bin/cR1_cut_position_horizon.sh` = **exactly two lines**, both `cpk2-`→`cpk3-` in `--job-name`/`--run-name`. `PARTS`/`WALL`/clamp/ms/α₀/epochs/batch/γ/AUG/dataset/net all unchanged.
- **guard 4g:** `scalar` still routes by exact string match in `init_meta`; **the code-path confound is DISCLOSED, NOT LIFTED.** `bin/PROTECTED.txt` carries **`cpk3-`**.
- **PREDICTED IN ADVANCE:** cpk3's 18 `m=2` rows land in **`SIGMA_772`'s own stratum**, so `cS2 --selftest` **will FAIL its `SIGMA_772` equality check after its own ingest**. Bars derive from the **frozen** literal, so **no verdict can move with it** — that FAIL is the audit working.

**MAY NOT CLAIM:** anything at all from cpk3 until it lands and is scored by `analysis/cS2_cpk3_score.py` run **UNEDITED**; any m claim; any CAPTURE (**no layerwise anchor**); an asymptote; a pooled estimate across cpk2/cts3/cpk3; any mechanism for any step.

## Cycle 133 — the deliverables

**This cycle LANDED, SCORED and INGESTED `cpk2` — the cut-position ladder at 772 epochs on FRESH seeds {3,4,5}.** CORRECTIONS **158**. **`FINAL: k*-UNMOVED | CONVERGED`.** The argmax at `E = 772` is **`k49` 56.4127 pp**, runner-up `k47` 45.8987 — **margin 10.5140 pp = 14.04 SE**, bar 1.4979; **every arm converged** at `E`. The in-batch 100-epoch control reproduces `cpk1`'s peak on seeds that batch never used (**`k49` by 10.4073 pp = 13.90 SE**), so the un-moved argmax is attributable to the **budget**, not the seed draw. **THE PRE-REGISTERED BRANCH IS CONFIRMED AND ITS CURVE MODEL IS REFUTED:** the forecast predicted **three rank swaps** with `k52` rising to runner-up; **zero** occurred, and `k52` misses by **−8.2225 pp** where every other arm is within 1.6. **No MASTER-TABLE verdict moves. No FINDINGS entry moves.**


| # | deliverable | outcome |
|---|---|---|
| 1 | `cpk2` — the argmax at a converged budget | **LANDED 18/18, SCORED, INGESTED.** `k*-UNMOVED` **and** `CONVERGED`, both on the registered rule |
| 2 | four attacks pressed before banking | **`k52` residual = weak MODEL, not a different shape** (0 rank inversions); **argmax is grid-edge-bounded** (`k=46,48` unrun anywhere); **0 of 18 runs duplicate a corpus row**; **the floor did not move** (+0.3513 pp, 0.47 SE) |
| 3 | ingest | **+18 rows, 0 changed, 0 removed.** Corpus **2,555 → 2,573**. **0 `in489g2` rows** |
| 4 | corpus-derived constant drift (CORRECTIONS 155 class) | **ALL 88 `--selftest`s run pre- and post-ingest. 0 changed exit code; 8 changed output.** One real move: **`cI2_in489g2`'s seed-null `F(11,2087)=0.170`/328 cells → `F(11,2105)=0.171`/332 cells** — still null, **flagged for whoever lands `in489g2`** |
| 5 | one prose claim withdrawn | 157.6's *"the curve becomes MORE asymmetric"* — measured **2.451 → 1.950**, i.e. **LESS**; the registered model implied the same. **No gate, no verdict touched** |

## `cpk2` — LANDED, SCORED, INGESTED (CORRECTIONS 158)

Scorer `analysis/cR1_cpk2_score.py` run **UNEDITED**, sha256 `06b7de18…5d5191f2`, **byte-identical on the Mac and in the `alice2` staging checkout**; both machines' full outputs `diff` **IDENTICAL**; `git diff -- analysis/` **empty**. **`runsdir` is POSITIONAL.**

    python3 analysis/cR1_cpk2_score.py /home/s5014158/metaopt/runs

| arm | spec | test@100 | **test@E** | gain | train@100 | **train@E** | slope@100 | slope@E |
|---|---|---|---|---|---|---|---|---|
| **`k49`** | `[49,13]` | 55.4880 | **56.4127** | +0.9247 | 62.4660 | **64.0633** | −0.00228 | −0.00047 |
| `k47` | `[47,15]` | 45.0807 | **45.8987** | +0.8180 | 49.7480 | 50.9860 | −0.00235 | −0.00293 |
| `k45` | `[45,17]` | 42.4960 | **43.5140** | +1.0180 | 47.2487 | 48.6227 | +0.00051 | −0.00509 |
| `k52` | `[52,10]` | 37.3967 | **39.8387** | +2.4420 | 41.3967 | 46.0113 | **+0.06763** | −0.00338 |
| `k50` | `[50,12]` | 29.9753 | **35.9133** | **+5.9380** | 31.9287 | 42.4307 | +0.03750 | −0.00331 |
| `k01` | `scalar` | 23.0167 | 23.3680 | +0.3513 | 23.2427 | 23.5307 | +0.00048 | **+0.00243** |

**TRAIN ranks the arms exactly as TEST at both horizons — no dissociation anywhere.**

- **Gates, all in batch.** `G0` PASS (18 runs, 18 job ids, 772/772, NAME==ARGS==ENV). **`R1` CLIFF PASS** `D100` **25.5127 pp = 34.06 SE**, bar 12.4170 (`DE` **20.4993**, `dD` **−5.0133 = −4.73 SE_dD`**; `cts3`'s −5.6747 is **CROSS-BATCH, descriptive, not poolable**). **`R-CTRL` PEAK PASS.** `R2` PASS. `R3` PASS (worst SD 1.7857 ≤ 2.7518). **`R-FLOOR` PASS — 5 of 5 informative at `E`**, closest `k50` **+12.5453 = 10.9×** bar. **`R-CONV` PASS — every arm converged**, 5 of 6 TIGHT.
- **Prediction vs measured.** Branch `k*-UNMOVED` ✔, argmax `k49` ✔, **runner-up predicted `k52` / measured `k47`** ✘, margin 7.8612 → **10.5140**. Residuals `k01` +0.0764, `k45` +0.5828, `k49` +0.4903, `k47` −1.1940, `k50` −1.5699, **`k52` −8.2225**.
- **The `k52` miss is the MODEL, not the shape.** Re-feeding the same line `cpk2`'s **own** in-batch `slope@100` (**+0.06763**, larger than the +0.06072 registered) makes it **worse**: predicted +10.9469 vs measured **+2.4420**. `k52`'s slope is **1.80×** `k50`'s but its gain is **0.41×** — **gain is NOT monotone in `slope@100` on the right flank**. `cts3`'s rate law is **true of `k50`, false of `k52`**. New, negative, unexplained.
- **RULE 21 margin 94 s** (`d5c6eb6` `20:23:14+02:00` → earliest `sacct` `Submit` `20:24:48`; 3 stamps at :48, 15 at :49; ids **4914387–4914404** contiguous). **RULE 20 at FULL coverage: 18 clean, 0 mismatch, 0 without an ARGS line — PASS** (157.8 could only reach 5 of 18). **ONE distinct `ENV:` line across all 18.** 18/18 `COMPLETED`, 18/18 `RUN_DONE`, 0 tracebacks.
- **Cost measured:** 18 × elapsed = **99.84 GPU-h**, mean **5.546 h**, max **06:20:34** (request 11:00:00). **The ETA was far too conservative** — Slurm put the last start at `2026-09-09T16:15`, actual `2026-09-07T01:57`, **2 d 14 h earlier**; submit → last completion **10 h 58 m** against a registered *1.5–3.2 days*.
- **`--selftest` PASSES pre- AND post-ingest.** 157.5's corpus-conditional RULE 21 check flips `0 → 18` and **stays PASS** — **the first landed batch in this thread whose own scorer did not acquire a known-false assertion on ingest** (the 156.9 defect, fixed in practice).

**WHAT IS NOW LIFTED from CORRECTIONS 156's 100-epoch scope:** `k* = 49` **among {45,47,49,50,52}** at 772 ep with every arm converged on fresh seeds; the `k49→k50` cliff at 772 now has a **fresh-seed replication** (`DE` 20.4993 vs `cts3`'s 19.3427); the shrinkage **direction**; and the `m=1` scalar floor at 772 (**23.3680**).

**WHAT IS STILL 100-EPOCH-SCOPED — 156's qualifier stands:** `cpk1`'s **single-peakedness** (`k = 17,24,31,38,42,55,60` unrun above 100 ep); `cpk1`'s **CAPTURE** curve (**no `layerwise` anchor in `cpk2`** — CAPTURE is not computable from it and may not be computed from it later); **147's cliff numerals 24.834 / 25.163 / 24.767 pp**; the peak's **sub-grid location**; every other horizon and every other cell.

**MAY NOT CLAIM:** an asymptote; a **mechanism** for `k52`; a **pooled `dD`** across `cts3`+`cpk2`; any `CAPTURE`; that the prediction was a good model (**confirmed on its branch, refuted on its curve**); that the `scalar` code-path confound is lifted (it is not — `scalar` still routes by exact string match in `init_meta`).

**NEXT EXPERIMENT — `cpk3`, close the grid-edge hole.** `k ∈ {46, 48}` × seeds {3,4,5} at 772 ep = **6 runs, ~33 GPU-h**. **Neither cut has ever been run at ANY horizon** in this cell, and they are the only measurement that converts *"`k*` = 49 among the five sampled cuts"* into *"`k*` = 49"*. Sharp prediction: `k48` should land between `k47` **45.8987** and `k49` **56.4127`**; **`k48 > k49` relocates the peak.** **BUT FIRST, A FREE ANALYSIS:** the broken rate law on the right flank needs the 100→772 **trajectory** for `k50` vs `k52`, which the existing `.out` files **already contain**. Register and run that before buying GPU time.

## Cycle 132 — the deliverables (CORRECTIONS 156)

**Cycle 132 LANDED, SCORED and INGESTED `cts3` — the 772-epoch horizon test.** CORRECTIONS **156**. **TWO verdicts, and neither is quotable without the other:** the `k=49 → k=50` cliff **SURVIVED** the horizon (`DE` **19.3427 pp = 26.00 SE**, 1.56× the survive bar) and **SHRINKS** on it (`dD` **−5.6747 pp = −5.39 SE**, bar ±2.1040). **`SHRINKS` was the REGISTERED PREDICTION** (−7.3320 pp; measured landed **+1.58 SE** inside the same branch) — **not a surprise and not a null.** **THE CONSEQUENCE IS A RESCOPING, NOT A RE-LITIGATION:** CORRECTIONS 147's cliff numerals (**24.834 / 25.163 / 24.767 pp**) are **budget-dependent** and now require **“at 100 epochs”** in the same sentence, and `cpk1`'s capture curve, its single-peakedness and its argmax **`k*=49`** are **100-epoch objects** that `cts1`/`cts2`/`scl1` all inherit. **No MASTER-TABLE verdict moves.** — **SUPERSEDED IN PART by CORRECTIONS 158 (cycle 133): `cpk2` lifts the 100-epoch scope on the ARGMAX, for the five cuts {45,47,49,50,52} only. The capture curve, the single-peakedness and 147's three cliff numerals stay 100-epoch objects.**

| # | deliverable | outcome |
|---|---|---|
| 1 | `cts3` — the 772-epoch horizon test | **LANDED 6/6, SCORED, INGESTED.** **SURVIVED** *and* **SHRINKS**, both on the registered rule |
| 2 | the rescoping those verdicts force | **147's cliff numerals + `cpk1`'s `k*=49` are 100-epoch objects.** Scope annotated in `docs/STATUS.md`; **`docs/FINDINGS.md` and `docs/MASTER-TABLE.md` need no edit — they never cite them** |
| 3 | ingest | **+6 rows, 0 changed, 0 removed.** Corpus **2,549 → 2,555.** First **>100-epoch** rows the corpus has ever held |
| 4 | corpus-derived constant drift (the CORRECTIONS 155 class) | **CHECKED, NONE.** `cQ1` row 24 **bit-identical** post-ingest. But the `cts3` scorer's `--selftest` **FAILS 5 checks** — 2 correctly, 3 from a **`scl1`-driven** drift that predates this cycle |
| 5 | `docs/MASTER-TABLE.md` | **NOT EDITED** — no cliff numeral or `cpk1` argmax appears in it. Its stale header count is carried, not silently fixed |

## `cts3` — LANDED, SCORED, INGESTED (CORRECTIONS 156)

Scorer `analysis/cO1_cts3_score.py` run **UNEDITED**, sha256 `ba8cac24…77ccf3ad`, **identical on the Mac and in the `alice2` staging checkout** and identical to the blob at the registration commit `327e3f0`; `git diff -- analysis/` **empty**. **`runsdir` is POSITIONAL, not `--runs`**; `--tb` is a documented argument, so passing it is **not an edit** — without it the clamp note prints `UNREAD`.

    python3 analysis/cO1_cts3_score.py /home/s5014158/metaopt/runs \
        --tb /home/s5014158/metaopt/runs/cts3/Tensorboard_outputs

| arm | test@100 | test@E | train@100 | train@E |
|---|---|---|---|---|
| **k49** `[49,13]` | 55.2353 | **56.2487** | 62.4253 | 64.1033 |
| **k50** `[50,12]` | 30.2180 | **36.9060** | 31.9353 | 43.8327 |

| axis | verdict | evidence |
|---|---|---|
| **(a) SIZE at long budget** | **SURVIVED** | `DE` **19.3427 pp = 26.00 SE_ARM_DIFF** — **1.56×** survive bar 12.4170, **13.00×** collapse bar 1.4878 |
| **(b) DIRECTION** | **SHRINKS** | `dD` **−5.6747 pp = −5.39 SE_dD**, bar ±2.1040 |

- **Neither verdict is quotable alone.** "SURVIVED" alone overstates; "SHRINKS" alone understates. The cliff is still **26 SE** wide at 772 epochs, but **22.7% smaller** than these same runs' own 100-epoch cliff — so the 100-epoch numeral **overstates the cliff once the losing arm has converged** (R4: k50 converged at E, not at 100). **Two budgets, two measurements — NOT a monotone trend and NOT an asymptote**; the registration forbids both.
- **`SHRINKS` was PRE-REGISTERED.** Predicted **−7.3320 pp (−6.97 SE)**; measured **−5.6747 (−5.39 SE)** — **+1.58 SE** inside the same branch. **May never be retold as a surprise or as a null.**
- **DECOMPOSITION — the losing arm improves, the winner does not decay.** `d(k49)` **+1.0133**, `d(k50)` **+6.6880**; k50 gains **6.60×** more.
- **Gates.** G0 PASS (6 runs, 6 job ids, 772/772, NAME==ARGS==ENV). **R1 PREMISE PASS** in batch from epochs 95–99 of these same runs: `D100` **25.0173 pp = 33.63 SE**, bar 12.4170 (`cts1`'s own cliff **24.8340**, DESCRIPTIVE only — **no batch splice**). **R2 PASS. R3 NOISE PASS** (worst cell SD 1.6129 ≤ 2.7333). **R4 HORIZON EFFECTIVENESS PASS** — k50's terminal 20-ep OLS slope **+0.03966 at 100 → −0.00199 at E** (bar 0.024235; `cts2` measured 0.04847; registered prediction at E 0.004329). k49 **+0.00239 → +0.00287**, converged at both. **The 772 epochs were not decorative.**
- **RULE 20** `--batch-consistency`: **6 clean, 0 mismatch, 0 without an ARGS line — PASS.** **RULE 21** margin **62 s** (`327e3f0` 12:46:11 → all six `Submit` **12:47:13, zero spread** = ONE submission). 6/6 `COMPLETED`, 6/6 `RUN_DONE`, **0 tracebacks**. ENV **6/6 `AUGMENT=1`**, **6/6 `BETA_CLIP=-15:-2.3026`**, `PROBE=0` 6/6.
- **Cost measured, not projected:** elapsed 04:33:01–05:33:11 × 6 = **31.12 GPU-h** (projected 33.0).

**CLAMP SCOPE (with `--tb`) — reported, never a gate.** Both arms' fine group (`block1`) sits on the −15 floor **95.2–95.4%** of the trace, last value exactly **−15.0000**. The arms differ on the coarse group:

| arm | `block0` min | `block0` last | on-floor |
|---|---|---|---|
| **k49** | **−15.0000** (3/3 reach it) | −14.9230 / −14.4218 / −14.7449 | **4.3 / 6.1 / 3.1%** |
| **k50** | **−13.8155** = the init — **never reaches it** | −13.4934 / −12.9812 / −12.9512 | **0.0 / 0.0 / 0.0%** |

**MAY NOT CLAIM:** the asymptote (registration says so in advance); any horizon but 100 and 772; the released floor at long budget; any cut but 49/50 — **`cpk1`'s `k*` at long budget is UNMEASURED**; any CAPTURE; any other cell; the **mechanism** of the shrinkage.

**NEXT EXPERIMENT — `cpk2`, the argmax at a long budget.** `cts3` leaves exactly one gap open and names it: `k*=49` is an argmax **measured at 100 epochs**, and `cts3` shows the two arms either side of it converge at **very different rates** (k50 +6.6880 vs k49 +1.0133). **Nothing in the corpus establishes that the argmax is still 49 once both arms have converged**, and a two-point contrast cannot relocate it.

| | |
|---|---|
| shape | `k` ∈ {45, 47, 49, 51, 53} × seeds **{3,4,5}** = **15 runs**, at the `cts3` horizon (772 ep) |
| controls | the 100-epoch control **in batch** (as `cts3` did) — no cross-batch splice |
| also fixes | **fresh seeds break the {0,1,2} reuse** CORRECTIONS 152 flagged across `cpk1`/`cts1`/`cts2`/`scl1` |
| cost | ~5.2 GPU-h/run ⇒ **~78 GPU-h** — the thread's most expensive batch |
| must register in advance | **whether it predicts `k*` to move**, and the σ_w it uses (**re-derived, not 0.9111 copied forward**) |

**Cheaper alternatives, recorded so they are not confused with the above:** re-running `cpk1`'s full ladder at 772 ep is ~10× the cost and buys resolution the question does not need; and any 100-epoch batch, however large, **cannot** address a scope defect that is by construction about budget.

## The rescoping — every doc row touched

**`docs/FINDINGS.md` and `docs/MASTER-TABLE.md`: ZERO edits, and that is a measurement, not an omission.** Both files contain **0 occurrences** of `cpk1`, `cts1`, `cts2`, `cts3` and `scl1`, and **0 occurrences** of 24.834 / 25.163 / 24.767. (`FINDINGS.md:9327/9337/9595` contain the string `24.83x` — an unrelated **startup/steady ratio**, deliberately **not** touched. `MASTER-TABLE.md:77`'s "argmax" is the pooling `r*`, not `k*`.) **The whole cut-position thread lives in `docs/STATUS.md` + `docs/CORRECTIONS.md`.**

| file | line (this HEAD) | numeral rescoped | edited? |
|---|---|---|---|
| `docs/STATUS.md` | **483** (threat row 10) | `cts2`'s cliff **24.7673 pp** → "**at 100 epochs**"; *"147's cliff needs no regime qualifier"* now carries an explicit **budget** qualifier, with the 772-epoch value **19.3427 pp** beside it | **YES** |
| `docs/STATUS.md` | **285** | cliff left-edges **k=49 / k=52** — flagged as `cpk1` grid points **measured at 100 epochs** | **YES** |
| `docs/STATUS.md` | **294** | `cpk1`'s **k=45 → k=49** window — flagged **a 100-epoch window**, and `k*=49` a 100-epoch argmax | **YES** — **partially lifted at CORRECTIONS 158** |
| `docs/STATUS.md` | **261** | `cpk1`'s second cliff **14.9700 pp** — **at 100 epochs** | **YES** |
| `docs/STATUS.md` | **273** | `scl1`'s **15.8080 pp** single-tensor attribution | **no** — the sentence already opens *"CIFAR-100 / `ResNet18_c100`, …, 100 ep"*. **Checked, correct as written** |
| `docs/FINDINGS.md` | — | — | **no** — 0 occurrences of the numerals or the batch names |
| `docs/MASTER-TABLE.md` | — | — | **no** — same; its rows 56/57 are the CIFAR-100 **granularity** arms, not cut position |

**4 rows edited, 1 verified-and-left, 2 files untouched. No verdict changed anywhere.**

## `cfr2` — LANDED, SCORED, INGESTED (CORRECTIONS 155)

Scorer `analysis/cO2_cfr2_score.py` run **UNEDITED**, sha256 `1e4f531a…d2a3b3ba` **identical on the Mac and in the `alice2` checkout**, `git diff -- analysis/` **empty on both**. `--selftest` **PASSED 0 failures pre- AND post-ingest** (the RULE 21 gate correctly degrading to `[INFO] NOT APPLICABLE`) — **the registration's claim about its own selftest is TRUE, unlike `cfr1`'s**. Every figure below re-derived this cycle from the raw `.out` files and the **6,000 raw probe records** with independent parsers.

| arm | box | **plateau5** | sd | train5 | sd |
|---|---|---|---|---|---|
| scalar | CLAMPED `-15:-2.3026` | **88.7680** | 0.1376 | 93.6340 | 0.4240 |
| layerwise | CLAMPED | **92.0647** | 0.0888 | 99.9127 | 0.0031 |
| scalar | RELEASED `-80:-2.3026` | **89.0780** | **0.4146** | 93.6833 | 0.3898 |
| layerwise | RELEASED | **92.0507** | 0.0842 | 99.9147 | 0.0064 |

| contrast | pp | SE units |
|---|---|---|
| `G_C` (lay − sc, CLAMPED) | **+3.2967** | 18.78 `SE_GAP` (train +6.2787) |
| `G_R` (lay − sc, RELEASED) | **+2.9727** | 16.93 `SE_GAP` (train +6.2313) |
| **`DID = G_R − G_C`** | **−0.3240** | **−1.31 `SE_DID`**, bar 0.4966, CI **[−0.8106, +0.1626]** |
| negative control (scalar `R − C`) | **+0.3100** | bar ±0.3512 — **88.3% of its own bar**, `cfr1` read +0.0067 |
| layerwise `R − C` | **−0.0140** | — |

- **G0/R1/R2/R3/R4 all PASS.** 12/12 COMPLETED, 12/12 `RUN_DONE`, 0 tracebacks, 100/100 epochs. RULE 21 margin **114 s** (`dfd9339` 16:31:52 → all 12 `Submit` 16:33:46, **zero spread**). RULE 20 `--batch-consistency`: **12 clean, 0 mismatch, PASS**, every non-axis flag identical. ENV audit **6 × `-15` / 6 × `-80`**, `PROBE=100` 12/12.
- **Detector validated empirically, not assumed:** largest single-stride `|dβ|` anywhere in the batch = **0.030041** ≤ the registered tolerance **0.0304**, so the wall detector has **no false negatives**.
- **`R4(ii)` PASSED — and the premise it tested is now measured for the first time.** Clamped layerwise **3/3** reach exactly −15.0000, first arrival at **99.5–99.9%** of the theoretically earliest step (26,975) — **free-fall** — with occupancy at this rung's **0.4600** ceiling (`lay-C-s0` sits exactly on it, 230/230). Released layerwise bottoms at −21.80…−21.83, **99.3–99.5%** of the float32 travel bound −21.907576, `n_at_lo = 0` at every record, never within 0.0304 of −80. **Ceiling untouched 12/12** ⇒ the floor is the only wall and a one-factor release is a **complete** box audit here.
- **cfr2's CLAMPED cells replicate the corpus cell** (agreement, never a splice): scalar 88.7680 vs 88.7444, layerwise 92.0647 vs 91.9264, gap 3.2967 vs 3.1820 (inside `2·SE_GAP` = 0.3511).

**Four attacks — 2 land hard, 1 is a scope fix, 1 is a refusal.**

| attack | found |
|---|---|
| **the interval (LANDS)** | CI as % of `G_C` = **[−24.59%, +4.93%]**, point **−9.83%**; `ATTENUATED` is **0.70 SE** away (`cfr1`: 1.87 SE). **80% power only against ≥0.7055 pp = 21.40% of `G_C`; 24% power against the effect actually seen.** *"Within the bar"* at this width licenses **"bounded above by ~25%"**, **not** *"does not move the gap"* |
| **the negative control (LANDS HARDEST)** | **it is not a control.** 3/3 clamped scalar runs hit −15.0000 and sit there **31.6–31.8%** of the trajectory; at the **coordinate** denominator `m=1` is pinned **5.7×** more than `m=62` (**31.7%** vs **5.53%**). Released, the scalar coordinate descends to **−19.70 = 85.3% of maximum travel** (vs **8.3%** at `cfr1`'s rung) and **ends training frozen**, 0.30 nats from the registered `COLLAPSED-BY-FREEZING` threshold. `DID` = (lay −0.0140) − (sc **+0.3100**): **the arm assumed inert supplies 100% of the estimate.** Per seed **+0.232 / +0.628 / +0.070 — 3/3 same sign** (layerwise is sign-mixed), with a **31.6% counterfactual dose** measured in the same runs. `sigma_w` **is** understated for that one cell (sd 0.4146, `P(χ²₂>x)` = 0.024) though the batch's pooled 0.2268 (df 8) is consistent with the registered 0.2150; on the batch's own sigma the CI only **widens** to [−0.8374, +0.1894] |
| **direction / pooling (REFUSAL)** | `cfr1` +0.0320 and `cfr2` −0.3240 are **statistically indistinguishable** (`Q` = 1.02, df 1, p 0.312; direct contrast z = −1.01). Fixed-effect pool **−0.1468 ± 0.1760, p 0.404**. **Legitimate ONLY as a joint-null test** — recorded, **never quotable as an effect size**: exposure differs structurally (**83.81%** vs **46.05%** of trajectory), `BATCH` is the unit of replication, and the scalar arm binds at one rung and not the other. Even the pooled CI still admits **−0.49 pp** |
| **the premise / 148.4 (SCOPE FIX)** | `cfr2` is the **first probe of any `m=62` or `m=1` run at `ms=3e-4`**. 153.8's *"100% bound"* was, when written, an extrapolation from a `m ≥ 777` census (154.5) — **amended in CORRECTIONS 155.8: the claim survives, its provenance is corrected from 148.4 to `cfr2`** (`m=62` 3/3, `m=1` 3/3). The *"94.7%"* in the same line is the `cfr1`-excluded reading; with `cfr1`'s rows in it is **93.12%**. Both recorded |

**ADDITION TO 148.5's m-LADDER (scope caution, not refutation).** 148.5 is headed *"Core set, `ms=1e-3`"*, where `m=1` reads **0.0%**. At **`ms=3e-4`** the run-level ladder is **FLAT** (scalar 3/3 = 100%, layerwise 3/3 = 100%) and the **coordinate-level ladder is INVERTED** (31.7% vs 5.5%). Binding is **non-monotone in `ms`** for `m=1`. **148.5's monotone-in-`m` reading may not be extended to `ms=3e-4`.**

## Row 24 — DISCHARGED / CONSTRAINED / UNAUDITABLE (CORRECTIONS 155.9)

| segment | status |
|---|---|
| `scalar`/`layerwise` @ **`ms=1e-4`** | **DISCHARGED by arithmetic** — min reachable β **−11.914545** > −15; no wall can exist |
| `scalar`/`layerwise` @ **`ms=1e-3`** | **DISCHARGED** (`cfr1`) |
| `scalar`/`layerwise` @ **`ms=3e-4`** | **CONSTRAINED, NOT DISCHARGED** — wall-driven refuted at 7.87 SE, but ≤24.6% not excluded and the estimate rides the mislabelled control arm |
| **peak-location-free headline** (loss at fixed `ms=1e-3` vs own peak), scalar vs layerwise | **DISCHARGED AT BOTH ENDPOINTS** — it uses only `1e-4` (arithmetic) and `1e-3` (`cfr1`). This is row 24's preferred headline and it is now the box-audited one |
| `blk6`, `nodewise` (incl. nodewise's peak @ `3e-4`) | **UNAUDITED** — neither `cfr1` nor `cfr2` ran those arms; `cQ1`'s stratum is the **clamped** box |
| **every rung above `ms=1e-3`** (`3e-3`, `1e-2`) | **UNAUDITABLE WITH THIS BOX** — travel bound at `3e-3` is **−156.9**, so the released **−80 floor is itself reachable**. `blk6`'s and `nodewise`'s **upper chords sit here** |

**Which rungs the four numerals rest on:** `scalar` (peak `1e-4` → `3e-4`, `1e-3`) and `layerwise` (same) now rest **entirely on audited rungs**; `blk6` and `nodewise` each carry a chord on an **unauditable** rung, and `nodewise`'s **peak** sits on clamped `3e-4`. A second, independent reason not to claim the sub-ordering 154 already declined.

## Row 24's numerals DRIFTED on this ingest — measured, not discovered later

`cfr2`'s six **clamped** rows are legitimately inside `cQ1`'s stratum, so ingesting this batch **moves row 24's own re-derived numerals**. `cQ1` re-run **UNEDITED** (sha `aa0bf548…`), `--selftest` **38/38**:

| arm | CORRECTIONS 154 | **post-`cfr2` HEAD** | Δ |
|---|---|---|---|
| `scalar` | 5.8976 ± 0.1659 | **5.8884 ± 0.1547** | −0.0092 |
| `blk6` | 0.9148 ± 0.1843 | **0.9148 ± 0.1827** | 0.0000 |
| `layerwise` | 1.8437 ± 0.1319 | **1.7893 ± 0.1183** | **−0.0544** |
| `nodewise` | 0.7532 ± 0.1701 | **0.7532 ± 0.1687** | 0.0000 |

`sigma_w` 0.1967 (df 216) → **0.1951 (df 222)**; the `ms=3e-4` cells go **n=5 → 8** for both arms; the corpus clamped gap at that rung **3.1820 → 3.2250** and the share-of-decade **93.12% → 94.68%**. **No conclusion moves** — Test A still 3 of 4 AGREE with `nodewise` still DISAGREEing by −1.8398, Test B still resolved at 2 SE, and **B-ALT is completely unchanged** (4.4219 / 0.9144 / 1.6749 / 0.1993) because it touches only cells `cfr2` does not populate. Row 24's printed numerals are **re-stamped and dated**. **This is FINDINGS 58.8(a)'s corpus-growth fragility — the one that broke `nodewise` at 154 — biting `scalar` and `layerwise`, harmlessly, and it will bite again on the next ingest into this stratum.**


## Row 24 — the numerals RE-DERIVED (CORRECTIONS 154, `cQ1`)

`analysis/cQ1_row24_falloff_score.py` (`573c08c`, sha256 `aa0bf548…`) run **UNEDITED**: `--selftest` **38/38**, then `--score`. Zero GPU. Pooled `sigma_w(plateau5)` re-derived at run time = **0.1967** (df 216, 39 cells). Recipe = **mean chord slope** from each arm's peak to every higher rung of the canonical ladder.

**The two questions are scored SEPARATELY and they do not agree.**

| arm | peak (n) | **falloff ± SE** | printed | Δ | 2 SE | **Test A** |
|---|---|---|---|---|---|---|
| `scalar` | 92.2624 @ `1e-4` (5) | **5.8976 ± 0.1659** | 5.871 | +0.0266 | 0.3318 | **AGREE** |
| `blk6` | 92.5300 @ `1e-4` (5) | **0.9148 ± 0.1843** | 1.060 | −0.1452 | 0.3685 | **AGREE** [N1] |
| `layerwise` | 92.8865 @ `1e-4` (11) | **1.8437 ± 0.1319** | 1.801 | +0.0427 | 0.2639 | **AGREE** |
| `nodewise` | 92.4533 @ **`3e-4`** (11) | **0.7532 ± 0.1701** | 2.593 | **−1.8398** | 0.3401 | **DISAGREE** [N1] |

| test | PRIMARY (ladder) | SECONDARY_ALL (every rung) |
|---|---|---|
| `scalar − blk6` | **+4.9829** (2 SE 0.4959) | +5.0228 (0.8347) |
| `scalar − layerwise` | **+4.0540** (2 SE 0.4239) | +4.0939 (0.7950) |
| `scalar − nodewise` | **+5.1445** (2 SE 0.4752) | +5.1844 (0.8229) |
| verdict | **B-POINT + B-2SE HOLD** | **B-POINT + B-2SE HOLD** |

- **B-ALT (peak-location-free, preferred headline)** — loss at the FIXED over-large `ms=1e-3` below each arm's own peak: scalar **4.4219** ≫ layerwise **1.6749** > blk6 **0.9144** > nodewise **0.1993** pp. **HOLDS**, and reproduces FINDINGS 58.8's ordering (4.480/1.736/1.022/0.098) at enlarged `n`.
- **Registered branch (i) fires: sentence CONFIRMED, numerals CORRECTED.** Row 24's verdict stays **CONFIRMED** — attached to **the sentence, not the numerals**.
- **CORRECTIONS 153's blanket "the four numerals do not re-derive" is PARTLY SUPERSEDED, in BOTH directions:** too broad on the values (3 of 4 AGREE), right about `nodewise` and right about the provenance.
- **The column swap is NOT what broke the row.** On the banned `plateau` column the same recipe gives 5.8895 / 0.9249 / 1.8207 / 0.6745 — every arm within **0.08 pp/decade**. The breakage is **corpus growth**: `nodewise`'s peak migrated `1e-3 → 3e-4` as `n` went **1 → 11** — the fragility FINDINGS 58.8(a) flagged and nothing acted on.
- **PROVENANCE DEFECT — the printed row is MIXED-COLUMN.** blk6/layerwise/nodewise reproduce on `plateau` (residuals ≤0.001); **scalar reproduces on `best_test`** (5.8706) and FAILS on `plateau` (+0.0209). Asserted as selftests **T1/T2**, not as a remark. Computed by an **uncommitted ad-hoc script** in cycle 57 (`775eb6b`) — whose CSV **has no `plateau5` column at all** (verified: `plateau` col 33 only; this HEAD has 33 **and** 35). Every `5.871` under `analysis/`+`bin/` is a comment or a registered constant, **never a computation**.
- **NOT claimed:** the sub-ordering among partitions (nodewise 0.753 < blk6 0.915 < layerwise 1.844 — finer is **not** monotonically more tolerant). Both rest on **n=1** cells. Only **partition-vs-none** is asserted.
- **Clamp scope UNCHANGED.** `cQ1`'s stratum **is** the clamped box `-15:-2.3026`; the recomputed `blk6` and `nodewise` falloffs sit on a **still-clamped** surface — and they are the two arms whose numerals moved.

## `cfr2` — the LAUNCH record (CORRECTIONS 154), retained; **superseded by the LANDED section above**

One-factor floor release at **`ms=3e-4`**, the rung `cfr1` left open. `{scalar, layerwise}` × box `{C = -15:-2.3026, R = -80:-2.3026}` × seeds `{0,1,2}`, **all four cells IN BATCH**. Byte-match to `cfr1` proven: `diff` of the two launchers' sbatch composition blocks is **EMPTY**; the only scalar-setting difference is `MST=1e-3 → MST=3e-4`.

| guard | result |
|---|---|
| **ONE submission** | ids **4913096–4913107** contiguous, **all `Submit` 16:33:46, zero spread across 12** |
| **RULE 21** | commit `dfd9339` 16:31:52 → earliest Submit 16:33:46 = **114 s** |
| **RULE 16** | `git diff --name-status 90d314b..HEAD -- analysis/` = **`A`,`A`**; 0 deletions, 0 modifications |
| **RULE 20** | `--batch-consistency` over 7 started `.out`: *"every non-axis flag identical across 7 runs / 7 clean, 0 mismatch"* → **PASS** |
| **ENV audit** (separate — `BETA_CLIP`/`PROBE` cannot ride `ARGS`) | **7/7 agree with run NAME**: 4 × `-15:-2.3026`, 3 × `-80:-2.3026`; `AUGMENT=1 HIER=none SCHED=none PROBE=100`, distinct `PROBE_DIR` each |
| **axes, checked independently of the guard** | `--meta-stepsize 3e-4` in **7/7**; granularity and seed match the name in **7/7** |
| **outcome** | **no mismatch → nothing cancelled.** Re-run at commit time after an 8th job started: **8 clean, 0 mismatch, PASS**; `cfr2-lay-R-s1` (4913103) carries `-80:-2.3026`/`layerwise`/`seed 1`/`3e-4`, all agreeing with its NAME. **4 `PENDING`** get the same audit on start |

- **Instrument re-verified at this rung on the live source.** Float32 travel bound at `ms=3e-4` = **[−21.907576, +8.090129]**. **−80 UNREACHABLE** (58.09 nats / 193,641 non-existent meta-steps — a **wider** margin than `cfr1`'s 23.11). **−15 REACHABLE** (6.9076 nats / 23,025 steps spare; first attainable at meta-step **26,975 = 53.95%**), capping floor exposure at **46.05%** of a run vs 83.81% at `cfr1`'s rung. `T` measured: 50,000 imgs / batch 100 / no `drop_last` → **50,000 meta-steps**. Guard 4f fails closed and passed.
- **Registered bars** (re-derived by the selftest, not quoted): `sigma_w` **0.2150** (df 80, 32 cells; `cfr2-` excluded, `cfr1`'s rows IN), `SE_GAP` 0.1755, `SE_DID` **0.2483**, bar **0.4966**. Power **1.0000** at the registered stake, **0.8857** at 25% of the gap; 80% power against any wall carrying **≥22.17%**.
- **`R4(ii)` is a LIVE gate, not a formality** — see the census defect below.
- **Refused:** a `blk6` arm at this rung (148.5's dose-response table is headed *"Core set, `ms=1e-3`"*; `blk6`'s binding rate at `3e-4` is **unmeasured**, so the arm would open a **second** unmeasured premise); loosening `PROBE` to 333; repeating `cfr1`'s false "selftest stays green post-ingest" claim.

## CORRECTIONS 148.4's census is NARROWER than it has been cited as being

Re-verified this cycle by joining every `ms=3e-4` `HIER=none` run on `alice2` to its **own** `ENV` line:

| granularity at `ms=3e-4` | probe |
|---|---|
| `chunk2325` ×3, `chunk777` ×3, `nodewise` ×3, `nodewise1d` ×3 | `PROBE=5` — **all `m ≥ 777` or `nodewise`** |
| **`scalar` ×5, `layerwise` ×5** | **NO `PROBE` AT ALL** |
| `scalar` ×4, `layerwise` ×3 at `PROBE=100` | **`cfr2`'s own, launched this cycle** |

- 148.4's *"ms=3e-4, n=15, floor 100.0%"* is measured on **`m ≥ 777` / `nodewise` runs ONLY**. **Binding at `m=1` or `m=62` at `ms=3e-4` is UNMEASURED IN THE CORPUS.**
- It is cited in **CORRECTIONS 153.8** and in **row 24's CORRECTIONS-153 annotation** as evidence the layerwise arm binds at that rung. **It is not evidence of that.** Row 24's annotation was narrowed at 154; **153.8 was amended at CORRECTIONS 155.8** — both are now done.
- **SETTLED.** `cfr2`'s clamped arms are the measurement: **`m=62` 3/3 and `m=1` 3/3 reach −15.0000 at `ms=3e-4`**. **The claim survives; its evidence is now `cfr2`, not 148.4.** And the undesigned half — `m=1` binding at all — is what broke the design's negative control (CORRECTIONS 155.6).

## `cfr1` — LANDED, SCORED, INGESTED (CORRECTIONS 153)

12/12 COMPLETED, scorer `analysis/cO1_cfr1_score.py` run **UNEDITED** (sha256 `3c52e678…e41114c`; `git diff -- analysis/` empty). Every figure re-derived here from the raw `.out` files and the 12 `probe.jsonl` traces with an independent parser and an independent probe reducer.

| arm | box | **plateau5** | sd | train5 |
|---|---|---|---|---|
| scalar | CLAMPED `-15:-2.3026` | **87.8707** | 0.2392 | 93.8987 |
| layerwise | CLAMPED | **91.3133** | 0.1406 | 99.8920 |
| scalar | RELEASED `-80:-2.3026` | **87.8773** | 0.0221 | 94.0340 |
| layerwise | RELEASED | **91.3520** | 0.3083 | 99.8933 |

| contrast | pp | SE units |
|---|---|---|
| `G_C` (lay − sc, CLAMPED) | **3.4427** | 19.52 `SE_GAP` |
| `G_R` (lay − sc, RELEASED) | **3.4747** | 19.70 `SE_GAP` |
| **`DID = G_R − G_C`** | **+0.0320** | **0.13 `SE_DID`** (bar 0.4988) |
| negative control (scalar `R − C`) | **+0.0067** | bar ±0.3527, **unmoved** |
| layerwise `R − C` | **+0.0387** | — |

- `VERDICT ROW24-SURVIVES`. G0/R1/R2/R3/R4 all PASS. Ceiling never touched on any clamped layerwise run (12/12) ⇒ the floor is the only wall **at this cell**.
- **Manipulation, coordinate denominator, full trajectory (500 records/run, `n_beta` 62 lay / 1 sc):** clamped layerwise hits exactly **−15.0000** in 3/3 with **27–30 of 62** coordinates pinned and **83.2–83.4%** of records bound against a theoretical maximum of **83.8%**; released layerwise bottoms at −56.51…−56.60, within **0.29–0.38 nats** of the exact float32 bound −56.888439 and **23.4 nats clear** of −80, `n_at_lo = 0` at every record; scalar never within **3.74 nats** of the floor in either box.
- **Bars re-derived independently of the scorer:** `sigma_w` **0.2160** (df 76, 30 cells, **cfr1 excluded**), `SE_GAP` 0.1763, `SE_DID` 0.2494, bar 0.4988 — all exact. **80% power against any wall carrying ≥20.6% of `G_C`**; power ≈ **1.0000** against the registered threat magnitude 2.7343 pp. 95% CI on `DID` **[−0.457, +0.521]** = **[−13.3%, +15.1%] of `G_C`**. **Not an underpowered null.**

**Five attacks — 3 land, 2 do not. None dented a number.**

| attack | found |
|---|---|
| **scope (LANDS)** | row 24 is a multi-rung slope; `cfr1` audits ONE rung. `ms=3e-4` is **100% bound** (census, n=15) and carries **94.7%** of the `ms=1e-3` gap — **unaudited**. Above `ms=1e-3` the **−80 floor is itself reachable** (min −156.9 at 3e-3, −506.9 at 1e-2), so the instrument does not transfer. `blk6` (68.8% bound) and `nodewise` unaudited by registration |
| **wrong cell (DOES NOT LAND)** | FINDINGS 57.2's stratum re-derived from the CSV **is** `cfr1`'s cell — R18/CIFAR-10/SGDm+Lion/**a0=1e-3**/AUG=1/100 ep/canonical box — and the `ms=1e-3` cell is **six ARM-BALANCED families**, not `rs-`-only |
| **which row (LANDS as a re-label)** | 3.44 pp is **row 23's** quantity, not row 24's. Upside: **row 23's headline now replicates inside ONE submission** — 3.4427 vs 3.3585 cross-batch, **0.48 `SE_GAP`** apart |
| **statistical (DOES NOT LAND)** | every registered constant re-derives to 4 dp; power ≈ 1 against every stated form of the threat |
| **numerals (LANDS, unasked)** | row 24's **5.871 / 1.060 / 1.801 / 2.593 do not re-derive** — no script computes them, they sit on the **BANNED k=20 `plateau`** column, and at this HEAD the two natural recipes give 3.778/1.119/1.942/0.285 and 4.427/0.761/1.693/1.125. The **SENTENCE** survives: on plateau5 scalar's drop below its own peak is **3.66×** layerwise's at 3e-4 and **2.61×** at 1e-3 (57.2 published 3.8× / 2.6×) |

- **Mechanism, disclosed:** `exp(−15) = 3.06e−07` vs the same runs' largest coordinate at `1.75e−02…2.34e−02`. Releasing the floor moves pinned coordinates from **4.8** to **22.8** orders of magnitude below the live ones — **off in both boxes** — and both boxes reach **99.89%** train. The measured content is *"nearly-off vs utterly-off costs +0.03 ± 0.49 pp"*. Written so the null is not banked as a surprising rescue.
- **DISCHARGED:** the `1e-4 → 1e-3` decade for the scalar/layerwise pair (lower endpoint clamp-free **by arithmetic**, min reachable β **−11.9078** > −15; upper endpoint now box-free to ±0.5 pp). **NOT DISCHARGED:** `ms=3e-4`; every rung above `1e-3`; `blk6` + `nodewise`; row 24's printed numerals.
- **`row N` = MASTER-TABLE FILE LINE N** — verified (lines 23/24/27/31/100/106 all resolve, incl. the `blk6`-refusal citation). The convention is written down nowhere; any line inserted above the tables silently re-numbers every citation.

## `scl1` — LANDED, SCORED, INGESTED (CORRECTIONS 152)

12/12 COMPLETED, scorer `analysis/cP1_scl1_score.py` run **UNEDITED** (sha256 `c2024f4b…880883e` = `git show aac1bf0:` blob; `git diff -- analysis/` empty). Every figure re-derived from the raw `.out` files with an independent parser, exact to 4 dp, additivity exact.

| cut | spec | n | **plateau5** | sd | train5 |
|---|---|---|---|---|---|
| k52 | `[52,10]` | 3 | **37.8833** | 1.0716 | 41.9247 |
| k53 | `[53,9]` | 3 | **22.0753** | 0.8840 | 22.2713 |
| k54 | `[54,8]` | 3 | **22.2133** | 0.7409 | 22.3507 |
| k55 | `[55,7]` | 3 | **23.3347** | 1.0822 | 23.4853 |

| step | k→k+1 | tensor that moves | params | **dTEST pp** | SE | **dTRAIN pp** |
|---|---|---|---|---|---|---|
| DROP1 | 52→53 | `layer4.0.shortcut.1.weight` (BN **scale**) | 512 | **15.8080** | **21.25** | **19.6533** |
| DROP2 | 53→54 | `layer4.0.shortcut.1.bias` (same BN's **shift**) | 512 | **−0.1380** | −0.19 | −0.0793 |
| DROP3 | 54→55 | `layer4.1.conv1.weight` (**conv**) | 2,359,296 | **−1.1213** | −1.51 | −1.1347 |
| TOTAL | 52→55 | all three | 2,360,320 | **14.5487** | 19.56 | 18.4393 |

- `FINAL: CLIFF CLIFF-REPRODUCES | SPLIT SINGLE-TENSOR-MAJORITY | TENSOR layer4.0.shortcut.1.weight | MECHANISM SHARED-MECHANISM`. R1/R2/R3 none fire. Q1/Q3/Q4/Q5/Q6/Q7 HELD, **Q2 REFUTED**. DROP1 leads **3/3** seeds (16.574 / 15.472 / 15.378).
- Bars re-derived pre-ingest by calling the scorer's own functions: `SIGMA_W` **0.9110578** (df 50, 25 cells, **no `scl1` row** — not circular), `SE_ARM_DIFF` 0.743910, `SE_ADJ` 1.288490, `CLIFF_BAR` 7.4850, `EVEN_BAND`/`SEPARATION`/`ASYM` 2.3476.
- `cpk1`'s own second cliff, DESCRIPTIVE, different batch, **at 100 epochs** (CORRECTIONS 156): **14.9700 pp**.

**Five lenses, 5 of 5 refuted or narrowed the interpretation. Not one dented a number.**

| lens | found |
|---|---|
| arithmetic / narrowing | 147.6 withdrew a claim about predicting **capture LEVEL across cut positions**; `scl1` measured a **within-step attribution** at a step selected for being costly. Different propositions |
| independence | **6 of 12 runs are exact-configuration re-executions** (`[52,10]` in `cpk1`+`cts1`; `[55,7]` in `cpk1`+`cbl1`); only `[53,9]`/`[54,8]` are new. `SIGMA_REPRO` **0.2266** vs `SIGMA_W` 0.9111 = **4.02×**; `CLIFF_BAR` sits **28.6 re-execution SE** below `cpk1`'s own value ⇒ **R1 had no power** |
| structural / live model | the two winners are the **two branch scales of ONE `layer4.0` residual junction**, 1-based indices **50 and 53**; the structural condition holds at **20 of 61 cuts (32.8%)** — an artefact of `named_parameters()` order |
| mechanism / optimiser state | at k53/k54/k55 **both** groups sit at the −15 clamp floor for **58–64%** of the logged trace — the same occupancy as the **scalar** arm `cts1-k01` (0.63); at k52 the leading group ends −10.21 with **0.00** at the floor |
| implementation / provenance | **no defect.** Scorer byte-identical to registration, glob prefix-isolated under a deliberately contaminated run dir, `--selftest` clean pre-ingest, every bar traceable to the corpus |

**THE CLAIM THE CORPUS IS ENTITLED TO** — CIFAR-100 / `ResNet18_c100`, SGDm+Lion, `ms=1e-3`, `alpha0=1e-6`, 100 ep, m=2, this `named_parameters()` order, seeds {0,1,2}: cliff 2 is carried by a single **512-parameter normalisation scale** — moving `layer4.0.shortcut.1.weight` out of the trailing group costs **15.8080 pp (21.25 SE)**, its own 512-param bias one step later costs **−0.1380 pp**, and the adjacent **2,359,296**-param conv **gains** 1.1213 pp; TRAIN agrees. That drop **exceeds the k=52 arm's entire 15.1342 pp advantage** over the pooled same-cell m=1 scalar baseline (**22.7492**, n=17, six batches).

**WHAT MAY NOT BE WRITTEN.**

| forbidden | why |
|---|---|
| *"147.6's withdrawal was TOO CAUTIOUS"* / *"a PATTERN for this sub-class"* | **in the registration blob `aac1bf0` (twice)** — pre-registered, and pre-registration does not license an inference. **147.6 STANDS.** Verdict string NOT edited (RULE 16); its **interpretation** is withheld, exactly as 147.6 did to `BN-LEVERAGE-FAVOURED` |
| any **share-of-TOTAL** for DROP1 (≈109%) | 147.6's fifth narrowing: the denominator is a non-monotone path sum with two negative legs. **Print no percentage** |
| *"reproduces in an INDEPENDENT batch"* | submission independent, **sample is not** — seeds {0,1,2} shared with `cpk1`/`cts1`/`cts2`; `cpk1-k55-s0` and `scl1-k55-s0` both return **23.696** |
| *"at a DIFFERENT site"* | one residual junction, two branch scales, three indices apart |
| *"the matched 512-vs-512 control shows a shift lacks a scale's leverage"* | **not identified at cliff 2** — k53 (−1.18 SE), k54 (−0.94 SE), k55 (+1.03 SE) are **at** the scalar baseline, so DROP2≈0 / DROP3≤0 is what a floor predicts for **any** class. And Q5's statistic `15.9460` is **bit-identical to R3's**. `cts1`'s k50 sits **+7.5855 pp / +13.30 SE** above the same baseline — cliff 1 has no such defect. `SCALE-SHIFT-ASYMMETRIC` stays **descriptive at ONE site** |

**THE `first tensor to leave` RIVAL CANNOT BE SEPARATED BY EXISTING DATA — said plainly.** Both winners are `DROP1` and **had to be**: both cliff left-edges (k=49, k=52 — **`cpk1` grid points measured at 100 epochs**, CORRECTIONS 156; both are **also measured at 772 ep** by `cts3`/`cpk2`, but **this single-tensor decomposition is 100-epoch**, CORRECTIONS 158) are `cpk1` grid points immediately after a conv, so the tensor at k is necessarily a BN scale. All **six** single-tensor steps in the corpus run **scale → shift → conv**, because `named_parameters()` orders conv → `bn.weight` → `bn.bias` and `--stepsize-groups [k,62−k]` takes a **contiguous prefix** — **no contiguous-prefix cut on this architecture can move a shift before its own scale**. Three rivals stay live: **norm scale**, **first to leave**, **clamp turnover**.

**147.6's grounds, all re-derived here and all untouched.**

- Condition satisfied at `cpk1` k31/k49/k52/k55 with captures **+0.2190 / +0.6965 / +0.3324 / +0.0139** — the peak and the **worst** cut. It also holds at **both** k=52 (37.8833) and k=55 (23.3347) **inside `scl1`**, 14.5487 pp / 19.56 SE apart.
- Base rate: of `cpk1`'s adjacent m=2 steps moving ≥1 norm scale out, **7 RAISE, 2 LOWER** — and `scl1` decomposed one of the 2. **Selection on the dependent variable.**
- Counterexample k=45→47 moves a 512-param BN scale out and **GAINS +3.4487 pp**. Unaddressed.
- **CORPUS NUMERAL CORRECTED:** 147.5c's *"10 steps, 8 raise, 2 lower"* is **7 of 9** on the same manifest (k47→49 moves no scale). 147.6's conclusion is unaffected; **do not re-quote 8/10**.

**NEXT EXPERIMENT — one batch breaks BOTH confounds (class×ordinal and seed reuse).** Decompose `cpk1`'s **k=45 → k=49** window (**a 100-epoch window**; CORRECTIONS 156 made `k*=49` a 100-epoch argmax and **CORRECTIONS 158 lifts that for `k* = 49` among {45,47,49,50,52} at 772 ep, converged, on fresh seeds — the WINDOW's single-tensor decomposition is still 100-epoch, and `k=46`/`k=48` are unrun at any horizon**) at single-tensor resolution, on seeds **{3,4,5}**, with in-batch anchors:

| step | tensor | class | params |
|---|---|---|---|
| 45→46 | `layer4.0.conv1.weight` | **conv** | 1,179,648 |
| 46→47 | `layer4.0.bn1.weight` | **scale** | 512 |
| 47→48 | `layer4.0.bn1.bias` | **shift** | 512 |
| 48→49 | `layer4.0.conv2.weight` | **conv** | 2,359,296 |

- Class-by-position order is **conv, scale, shift, conv** ⇒ a conv is first to leave and a scale sits in position 2. **No code change, no non-contiguous partition, no scorer exemption.**
- **Off the floor throughout**: `cpk1` M(45)=42.2393, M(47)=45.6880, M(49)=55.4473 — 19.5–32.7 pp above the 22.7492 scalar baseline — and the window **RISES** +13.21 pp net.
- Seeds {3,4,5} make it the **first batch that samples the seed nuisance instead of re-executing it**.
- Shape: k∈{45,46,47,48,49} × {3,4,5} = 15 jobs **+ `scalar` and `layerwise` anchors × {3,4,5}** = 6 ⇒ **21 jobs**, ~15 GPU-h, non-axis flags byte-matched to `scl1`.
- Register in advance: (a) *norm scale* → largest step at 46→47; (b) *first to leave* → 45→46; (c) *clamp turnover* → wherever the leading group's terminal β crosses the floor. **The scorer MUST carry a floor gate**: no drop scored informative if either neighbouring arm is within 2 SE of the in-batch m=1 anchor.
- Weaker variants, recorded so they are not confused with this one: k=56/57 added to `scl1` (6 jobs) breaks the ordinal confound alone **but lands on the saturated floor**; a third cliff on seeds {0,1,2} adds a step and **no** independence.

## Queue — re-derived from `squeue` at this HEAD

| account | batch | jobs | run | pend | done | state | scorer |
|---|---|---|---|---|---|---|---|
| `alice2` | **`cpk2`** | **18** | **5** | **13** | 0 | **REGISTERED AND LAUNCHED this cycle** (CORRECTIONS 157). Cut-position ladder `k∈{45,47,49,50,52}` + `scalar` floor anchor × seeds **{3,4,5}** at **772 ep**, ONE submission, ids **4914387–4914404**. 100-ep control **in run** (ep 95–99). **RULE 21 margin 94 s**; RULE 20 batch-consistency **PASS (5/18 started)**; ENV audit **1 distinct `ENV:` line**. ~93 GPU-h. **Do NOT score or ingest.** | `cR1_cpk2_score.py` (`d5c6eb6`) |
| `alice2` | **`cts3`** | 6 | 0 | 0 | **6** | **LANDED, SCORED, INGESTED this cycle** (CORRECTIONS 156). 6/6 `COMPLETED`, 6/6 `RUN_DONE`, 0 tracebacks, **772/772 epochs** | `cO1_cts3_score.py` (`327e3f0`), run **UNEDITED** |
| `alice2` | **`cfr2`** | 12 | 0 | 0 | **12** | landed, scored, ingested last cycle (CORRECTIONS 155) | `cO2_cfr2_score.py` (`dfd9339`) |
| `alice2` | `cfr1` | 12 | 0 | 0 | **12** | landed, scored, ingested last cycle (CORRECTIONS 153) | `cO1_cfr1_score.py` (`dbf90db`), run UNEDITED |
| `alice` | `in489g2` | 14 | — | — | — | **RUNNING — NOT OURS, never touch.** `squeue` read-only. Never `scancel`, never submit, nothing written to `/data1/salehkaleybars` | `cI2_in489g2_score.py` (`571707b`) |
| `alice2` | `scl1` | 12 | 0 | 0 | **12** | landed and ingested last cycle (CORRECTIONS 152) | `cP1_scl1_score.py` (`aac1bf0`) |

- **`alice2` holds 18 `cpk2` jobs** (5 RUNNING, 13 PENDING). Slurm's own `--start` puts the last (4914404) at **2026-09-09T16:15**; those estimates ignore backfill, so the honest range to completion is **~1.5–3.2 days**. `cts3` cleared its queue in 44 min, but that is **not** claimed here.
- **NOTHING WAS INGESTED THIS CYCLE.** Corpus stays **2,555 rows**. `cpk2` has not landed; **do not score it and do not ingest it.**
- Re-run when all 18 have started: `export METAOPT_WS=/home/s5014158/metaopt; python3 analysis/argsline_guard.py $METAOPT_WS/runs --name cpk2- --batch-consistency --strict`
- `in489g2` on `alice` is **NOT OURS**. **Read with `squeue` only. Never cancel, requeue, modify or submit.** Nothing was written to `/data1/salehkaleybars`.
- **This session cancelled nothing and requeued nothing on either account, and submitted only the 18 `cpk2` jobs on `alice2`.** Remote writes: the staging checkout `/home/s5014158/metaopt/hmo-cpk2/` (at `d5c6eb6`, tree clean, scorer sha256 identical to the Mac's) and `runs/cpk2/PARTITION-MANIFEST.txt`.

## INGEST — `cts3`, **+6 rows** (CORRECTIONS 156.7)

    python3 analysis/aggregate.py ../runs ../runs_alice2 > results/all_runs.csv   # STDOUT, not a log
    python3 analysis/args_repair.py --apply

| | |
|---|---|
| **ADDED** | **6** — exactly `cts3`, ids 4912733–4912738 |
| **CHANGED** | **0** |
| **REMOVED** | **0** |
| corpus | **2,549 → 2,555** |

- **`epochs_requested=772` CHECKED, not assumed.** All six land `epochs_requested=772`, `epochs_done=772`, `window_ok=1`, `complete=1` — **not dropped, not truncated, not coerced to 100**. Each row's `plateau5` equals the scorer's own per-seed `test@E` to the digit.
- **A DRAFTED CLAIM WAS WRONG AND IS CORRECTED:** it is **not** true that no earlier row exceeds 100 epochs — **72 do** (300 and 600), **all on `network=ResNet18`**. What is new is the **value 772**, and any horizon >100 **on `ResNet18_c100`** (previous max **exactly 100**). Only the latter flips a registered premise.
- **`args_repair` reported "36 rows updated"; the keyed diff shows 0 changed fields — and this cycle establishes WHY.** Diffing the tool's own backup shows all 36 touch **exactly one field, `dup_group`**, always `'' → '<name>'`: `aggregate.py` **blanks** it, `args_repair` **restores** it. **A fixed round-trip artefact that will recur on every ingest.** Never read it as a corpus change.

## Corpus-derived constants — the CORRECTIONS 155 class, checked

- **`cQ1` row 24: BIT-IDENTICAL post-ingest.** `sigma_w` 0.1951 (df 222, 39 cells); `scalar` 5.8884±0.1547, `blk6` 0.9148±0.1827, `layerwise` 1.7893±0.1183, `nodewise` 0.7532±0.1687; B-ALT 4.4219 / 0.9144 / 1.6749. **Structurally immune** — `cQ1` pins CIFAR-10 / `ResNet18` / 100 **both** epoch columns; `cts3` fails all three.
- **Every scorer carrying a verdict pins epochs (usually twice) or reads by run-name prefix.** What moves is **bookkeeping**, and **every counter was already stale before this cycle**: `c73` header (2,537/2,222.0 vs CSV **2,555/2,263.7**), `cH1`'s *"ZERO int-list partitions"* (105 → **111**, asserting 0 since `cpk1`), `c98`/`c68` row censuses, `c57`'s denominator. `c69_orphan_census`: `cts3` is **STRICT-CITED**, so **no new orphan** — ORPHAN stays **1 family / 1 run**.
- **`docs/MASTER-TABLE.md` was NOT edited.** Two of `c73`'s five failures (74 vs 73 rows; CONFIRMED 32 vs 31) cannot be fixed without re-litigating verdicts. **Carried, visible, not silently patched.**

## `cts3` scorer `--selftest` — **FAILS 5 CHECKS. 2 ARE THE BATCH SUCCEEDING.**

| check | got | want | reading |
|---|---|---|---|
| `RULE 21: no cts3- row exists` | 6 | 0 | **CORRECT — the rows landed** |
| `no ResNet18_c100 run exceeds 100 ep` | 772 | 100 | **CORRECT — the entire point of the batch** |
| `SIGMA_W` / `df` / `cells` | 0.9173 / 58 / 29 | 0.9111 / 50 / 25 | **`scl1`-driven drift that PREDATES this cycle** |

- **The scorer registered this in advance:** *"once cts3 rows land, the 'no cts3 row exists' check and the corpus-dependent noise floor may legitimately move, and the scorer is NOT edited to make them green (RULE 16, precedent CORRECTIONS 150.7)."*
- **At the registration commit `327e3f0` the corpus reproduced 0.9111 / df 50 / 25 cells EXACTLY.** The stratum then grew 75 → 87 members; the twelve additions are **`scl1-k52/k53/k54/k55 × s{0,1,2}`** (ids 4912717–4912728), which entered at **`c6a282c` (15:17:43) — 2.5 h AFTER** the cts3 registration. **`cts3` itself added nothing** (`_in_cell` pins `epochs_done == 100`).
- **No verdict can move:** `SIGMA_W` is a **frozen literal** and every bar derives from it; only `--selftest` re-derives. The scorer was run **before and after** ingest and the PRIMARY block is **bit-identical**. **The FAIL is the audit working.**
- **Carried:** on the live corpus the honest bar is `sigma_w` **0.9173** (`NOISY_BAR` 2.7519 vs 2.7333). R3 passes under either (worst cell SD 1.6129). **No future `cts*` registration should copy 0.9111 forward without re-deriving it.**

## INGEST (cycle 129, `cfr1`) — the diff, read both ways (CORRECTIONS 146.7)

    python3 analysis/aggregate.py ../runs ../runs_alice2 > results/all_runs.csv   # STDOUT, not a log
    python3 analysis/args_repair.py --apply

| | |
|---|---|
| before / after | **2,525 → 2,537 rows** |
| **ADDED** | **12** — `cfr1-{sc,lay}-{C,R}-s{0,1,2}`, job ids `4912745`–`4912756` |
| **CHANGED** | **0** (keyed on `run`+`job_id`, whole-row compare) |
| **REMOVED** | **0** |
| `args_repair.py --apply` | 36 `dup_group` stamps re-applied (aggregate regenerates without them); **0 accuracy/config values changed**, 0 `superseded` changed. Net vs the pre-ingest CSV: **0 changed rows** |
| ingested rows spot-check | all 12 `epochs_done=100`; the four cell means reproduce the scorer exactly (87.8707 / 91.3133 / 87.8773 / 91.3520) |
| **NOT ingested** | — (that cycle's deferral of `cts3` was discharged this cycle: **+6 rows**, CORRECTIONS 156.7) |

**RULE 20 — `cfr2` 8/8 started runs, re-derived at this HEAD** (4 `PENDING` get the same audit on start):

    export METAOPT_WS=/home/s5014158/metaopt
    python3 analysis/argsline_guard.py --name cfr2- --batch-consistency /home/s5014158/metaopt/runs/cfr2-*.out

- **8 clean, 0 with repeated flags or design mismatch, 0 without an ARGS line — VERDICT PASS.** *"every non-axis flag is identical across 8 runs"*. (Audited at 7 started, re-run at 8 when `cfr2-lay-R-s1` began; both PASS.)
- **`BETA_CLIP` and `PROBE` audited SEPARATELY from each run's own `ENV` line** — they are environment variables and **cannot ride the `ARGS` line**. 4 × `-15:-2.3026`, 3 × `-80:-2.3026`, **each agreeing with its run NAME**; `AUGMENT=1 HIER=none SCHED=none PROBE=100` and a distinct `PROBE_DIR` in all seven.
- **Axes checked independently of the guard:** `--meta-stepsize 3e-4` in 7/7; `--stepsize-groups` and `--seed` match the run name in 7/7. **No mismatch → nothing cancelled.**

**RULE 20 — `cfr1` 12/12 (cycle 129). This CLOSED CORRECTIONS 151.4's 11/12 INCOMPLETE audit.**

    python3 analysis/argsline_guard.py --name cfr1- --batch-consistency ../runs_alice2/cfr1-*.out   # exit 0

- **12 clean, 0 with repeated flags or design mismatch, 0 without an ARGS line — VERDICT PASS.** *"every non-axis flag is identical across 12 runs"*.
- ENV audit (`BETA_CLIP` cannot ride the ARGS line — RULE 20's known blind spot): **6** runs `-15:-2.3026`, **6** runs `-80:-2.3026`, each agreeing with its own run NAME. `RUN_DONE` 12/12, tracebacks 0/12, 12 distinct job ids.

**RULE 21 — `cfr2` 114 s.**

| batch | commit | commit epoch | earliest `sacct` Submit | **margin** | spread |
|---|---|---|---|---|---|
| **`cfr2`** | **`dfd9339`** | 1788705112 (16:31:52) | 1788705226 (16:33:46) | **114 s** | **0 s across all 12** |
| `cfr1` | `dbf90db` | 1788691708 (12:48:28) | 1788691838 (12:50:38) | **130 s** | 1 s |
| `cts3` | `327e3f0` | 1788691571 | 1788691633 | 62 s | 0 s |
| `scl1` | `aac1bf0` | 1788691465 | 1788691498 | 33 s | 1 s |

**RULE 16 — no scorer edited, by anyone, at any point this cycle.** `git diff --name-status 90d314b..HEAD -- analysis/` returns **`A`, `A` and nothing else**; `--numstat` gives `1484/0` (`cO2_cfr2_score.py`), `654/0` (`cQ1_row24_falloff_score.py`) — **0 deletions, 0 modifications**. sha256 parity Mac ↔ `alice2` holds for `cO2_cfr2_score.py` (`1e4f531a…`) and its launcher (`ac782ce7…`); the `alice2` checkout is clean at `dfd9339`.

**RULE 21 does NOT apply to `cQ1`, and the weaker guarantee is stated instead of the label.** `cQ1` has **no runs of its own** — it is a zero-GPU re-derivation over rows that predate it, so no ordering against an `sacct` Submit exists. What is proven is **commit-before-first-execution**: `573c08c` at 16:23:31, first execution 3 s later. Disclosed: a `py_compile` byte-compile preceded the commit; it does not execute the module body.

| check | result |
|---|---|
| `git status --porcelain analysis/ paper/` | **empty**, start and end |
| `git diff --stat -- analysis/` | **empty** |
| `shasum -a 256 analysis/cO1_cfr1_score.py` | `3c52e678cbd086df5acaeb8d0c7b270dbc2d38a4f23c49f5ae48d79cbe41114c` (matches registration) |
| `--selftest` **pre**-ingest | **PASSED, 0 failures** |
| `--selftest` **post**-ingest | **FAILED, 1 failure — BY CONSTRUCTION**: *"no `cfr1-` row exists in the corpus yet"* (12 found), the RULE 21 pre-registration guard, which can only pass before landing. `SIGMA_W` / `CORPUS_GAP` / every bar still re-derive **green** (the registration exempted `SIGMA_W` from `cfr1`'s rows but not this guard, so its claim that the selftest *"stays green after landing"* is **false**). **NOT edited** (RULE 16) |
| score output pre- vs post-ingest | **byte-identical** — the scorer reads `.out` files and probes, not the CSV |

**Cost — `cfr1` spent, measured from `sacct`.**

| batch | state | GPU-h |
|---|---|---|
| `cfr1` | **SPENT** — 12 runs, elapsed 31:26–1:31:56, summed | **9.98** |
| `scl1` | **SPENT** — landed last cycle | 9.80 |
| `cts3` | **SPENT** — landed this cycle | **31.12** |
| `in489g2` | **NOT OURS** (`alice`) | ~348.5, **not counted** |

**NEXT EXPERIMENT — `cfr2`, the rung that actually closes row 24.** `{scalar, layerwise}` × `{-15:-2.3026, -80:-2.3026}` × seeds `{0,1,2}` at **`ms = 3e-4`**, every other flag byte-matched to `cfr1`. It is the only *binding* rung inside row 24's own decade with no clamp-free replicate, it carries **93.5%** of the granularity rise, and `-80` stays unreachable there (min reachable **−21.91**) so the one-factor instrument transfers unchanged. 12 jobs, ~10 GPU-h. Secondary: `cfr3`, `blk6` × `{-15, -80}` × 3 seeds at `ms=1e-3`, 6 jobs, converting the census's 68.8% into the middle rung of a 0% / 68.8% / 100% dose-response. Zero-GPU: re-derive row 24's four falloffs on **plateau5** with a committed script and a stated recipe.

**Live-model manifest — verified here, not accepted from the launcher.**

- `PARTITION-MANIFEST.txt`: **62** tensors, **11,220,132** params. I set-differenced the `FIRSTGROUP` name lists myself and checked the 1-based convention against **all four** specs (`FIRSTGROUP == names[:k]`). Partition **nested**, each step moves **exactly one** tensor, and it is the registered one. Leading-group params 6,447,168 → 6,447,680 → 6,448,192 → 8,807,488.
- The three steps move **49.4519%** of the k=52 trailing group vs `cts1`'s 2.6931% — **homologous in CLASS, not in MASS**, and registered as such in advance.
- **Terminology, once:** at m=2 both groups carry exactly **one** `β` (`HF.py` blockwise), so neither is "finer". Write **trailing → leading**, not "fine → coarse".

**Cost — `scl1` spent, measured.**

| batch | state | GPU-h |
|---|---|---|
| `scl1` | **SPENT** — 12 runs, elapsed 35:07–1:25:38, summed | **9.80** |
| `cfr1` | **SPENT** — landed and ingested THIS cycle (CORRECTIONS 153) | **9.98** |
| `cts3` | **SPENT** — landed this cycle | **31.12** |
| `in489g2` | **NOT OURS** (`alice`) | ~348.5, **not counted** |

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
| 10 | CORRECTIONS 146/147 (`cpk1`, `cts1`) | **SETTLED at this contrast by `cts2`** (CORRECTIONS 150): floor released 65 nats, cliff `24.7673 pp` **at 100 epochs**, `INT` `0.3953 pp` = 0.38 SE_INT. 147's cliff needs no **regime** qualifier — but **CORRECTIONS 156 adds a BUDGET one**: at 772 epochs the same contrast reads **19.3427 pp**, so `24.834 / 25.163 / 24.767` are **100-epoch numerals and an upper bound on the converged cliff**. Nothing else in 147.6 is restored |
| 11 | `hz3` wrong-box rows (8114) | A known metadata discrepancy is now **measured to be a real regime difference** |

**COVERAGE — the honest limit. 1,356 of 2,501 rows (54.2%) have a beta trajectory; 1,145 (45.8%) have none.** *(Measured on the pre-`cts2` 2,501-row corpus. The 12 `cts2` rows all carry a trajectory. `scl1`'s 12 rows ran `PROBE=0` and have **no `probe.jsonl`** (verified: 0 probe files under `runs/scl1/`), though they do carry TB `beta_block*` traces because m=2 — so the probe-based numerator is **unmoved** and the denominator is not: **1,368/2,525 = 54.2%**. Every stratum row below is unrestated.)*

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

- **Step 0, zero GPU-h, STILL NOT DONE.** `tc1` (12 rows, `-30:6.0`, measured **1/12**) and `ub9` (9 rows, `-60:6.0`, measured **0/9**) are the only two of the corpus's **24** non-canonical-box cells that contain a **scalar** arm — `wc5`/`cl5`/`uc5`/`uc6`/`bl5`/`br6`/`bo6`/`bo7`/`bd7`/`bf8`/`bf9`/`ns5`/`sp8` are `{layerwise, nodewise, weightwise}` only. **Deliberately not differenced**: their data already exist, so RULE 21 requires a scorer registered and committed first. At n=2 per (arm, `alpha0`) `tc1` is a **direction check, not a settlement**.
- **Step 1 — SUPERSEDED AND EXECUTED AS `cfr1` THIS CYCLE. The design written here was DEFECTIVE; do not resurrect it.** The old text specified box `{-15:-2.3026}` × `{-30:6.0}`, which **moves BOTH walls at once** — CORRECTIONS 149 showed that exact defect is what makes `tc1`/`ub9` ambiguous, and it would have made Step 1 ambiguous in the same way. `cfr1` is the **one-factor** replacement: ceiling **identical at `-2.3026`** in both arms, floor released `-15 → -80` only. Registered `dbf90db`, RULE 21 margin 130 s, running now — see the queue section.
- **What `cfr1` fixed beyond the box.** The released floor is **provably unreachable** (`TRAVEL_LO −56.888439` vs `−80`, from `|Δβ| ≤ ms` over `META_STEPS 50000`), not merely "measured-free" as `-30:6.0` was. Occupancy is read at the **coordinate denominator** with a stride bound (`ms·PROBE = 0.1` nats) that gives the wall detector **no false negatives** — the direct answer to CORRECTIONS 149.7's lower-bound problem. And gate **R4(ii)** requires the clamped fine arm to **actually reach the wall**, so a null cannot be laundered into a vindication of row 24.
- **The ceiling was refused as a third level, on the record**: FINDINGS 6190–6215 measured **2/2 fatal collapses** at `+6.0`, and a diverged arm is `UNRESOLVED-DIVERGED` by gate R2. A `SURVIVES` verdict from `cfr1` therefore discharges the **floor half of the threat only** — the ceiling release is the registered next experiment if the diagnostic shows any clamped layerwise coordinate on `-2.3026`.
- **Extending the census is NOT worth GPU-hours.** The 1,145 un-instrumented rows cannot be re-instrumented without re-running them, and for the modern cells the answer is already "inert".

**COST — measured from history, not guessed.**

| batch | reference | mean/run | projected | worst case (walltime cap) |
|---|---|---|---|---|
| `scl1` (**in flight**) | `cpk1` 39 runs on this cell, 0 TIMEOUT | **42.0 min** | **8.40 GPU-h** | 30.0 (`--time 02:30:00`) |
| `cfr1` (**in flight**) | 191 layerwise + 65 scalar R18/C10 runs on this account | 42.9 / 67.2 min | **11.01 GPU-h** | 36.0 (`--time 03:00:00`) |
| `cts3` (**SPENT**) | **measured**: elapsed 04:33:01–05:33:11 over 6 runs | **4.55–5.55 h** | **31.12 GPU-h** (projected 33.00) | 66.0 (`--time 11:00:00`) |
| **total committed this cycle** | 30 jobs, `alice2` | | **52.41 GPU-h** | **132.0** |
| `cts2` (**DONE**, cycle 126) | measured: 528 wallclock-min over 12 runs | **44.0 min** | **8.80 GPU-h** (spent) | 30.0 |
| `in489g2` (**NOT OURS**, `alice`) | `in489g1` 12 runs = 298.7 GPU-h | **24.89 h** | **348.5 GPU-h** | 476.0 |

**Every row below was re-derived at this HEAD. Do not quote this file as a source; re-run the command.**

## Verdict

| | |
|---|---|
| Q1 meta-gate | **DESK-ACCEPT, 9/10, `structural_gaps = []`, `passed = True`, 0 blocking.** Returned at cycle 111 on v8 (CORRECTIONS 135). **Carried, not re-derivable here** — the gate tool is not in this tree |
| Audit | `c98_reproduce.py` **exit 1 — 8 CHECKS FAIL** at this HEAD after the `cfr2` ingest (rows **2549**/2177, admissible **2107**/1735, wallclock **2534**/2162, GPU-h **2233**/1642, best R18/C10 **93.328**/93.317, deficit **1.796**/1.807, partition-family rows **437**/431, Lion **425**/419). **All 4 substantive numerals (93.328, 1.796, 437, 425) are BIT-IDENTICAL across this ingest** — `cfr2`'s 12 rows are not in the partition families; **only the 4 census counts moved** (2537→**2549**, 2095→**2107**, 2522→**2534**, 2222→**2233**), and the failure count stays at **8**. **No claim reverses.** Historical note, unchanged: verified both ways by restoring the pre-ingest CSV. The 4 **substantive** numerals are bit-identical across the ingest (best R18/C10 arm **93.328** vs paper 93.317; deficit **1.796** vs 1.807; partition-family rows **434** vs 431, Lion **422** vs 419). Only the 4 census counts moved: rows 2,357 → **2,399**, admissible 1,915 → **1,957**, wallclock 2,342 → **2,384**, GPU-h 1,805 → **1,833**. **No claim reverses**, no new claim went stale — baseline unmoved at 95.124 (se 0.047). Fix = edit both markups; **author scope**, CORRECTIONS 141.6 / 142.6 |
| tex↔md | `paper_numeric_diff.py` **5 residuals over 4 distinct tokens** (2 tex-only: `0.05`, `3.0`; 3 md-only: `0.087`, `0.279`, `3.19`). **All pre-existing, 0 new this cycle** — nothing under `paper/` was touched. Both markups carry 994 distinct quantity numerals |
| Science overturned | **none.** Contribution 1 intact at 4 sites; the withdrawal stays confined to the slope |
| GPU to reach submission | **0 jobs, 0 hours.** `cfr1`'s **9.98** GPU-h are spent and landed (CORRECTIONS 153); `scl1`'s 9.80 landed at 152; `cts3`'s **31.12** are spent and landed (CORRECTIONS 156); `in489g2`'s ~348.5 on `alice` are **not ours**. None of it is this manuscript's science |

**Ready to submit: NO** — not for any manuscript defect, for the **seven** author items (§ TODO-FOR-AUTHOR).

## Mechanical verification — commands run at this HEAD

| check | result |
|---|---|
| `python3 analysis/c98_reproduce.py` | **exit 1, 8 CHECK(S) FAILED** at this HEAD — stale draft numerals, not a moved result; **inherited, author scope, deliberately NOT fixed**. Derived vs paper after the `cfr2` ingest: rows **2549**/2177, admissible **2107**/1735, wallclock **2534**/2162, GPU-h **2233**/1642, best R18/C10 **93.328**/93.317, deficit **1.796**/1.807, partition-family **437**/431, Lion **425**/419 — the 4 substantive numerals **bit-identical** to the pre-ingest HEAD. Historical detail from cycle 127, unchanged: `git diff --name-only 94c6e4f..HEAD` over `paper/`, `results/` and `c98_reproduce.py` = **0 files**, so every input is byte-identical to the pre-cycle HEAD. Derived vs paper: rows 2444/2177, admissible 2002/1735, wallclock 2429/2162, GPU-h 2153.85/1642, best R18/C10 93.328/93.317, deficit 1.796/1.807, partition rows 437/431, Lion 425/419. `c98` exited 0 only against the 2,177-row corpus of cycle 116. **A detached worktree is NOT a valid control** — it reports 14, the 6 extra being coverage-census checks that move because gitignored `hz3` `.out` files are absent. See CORRECTIONS 141.6 / 142.6 / 145.4 |
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
