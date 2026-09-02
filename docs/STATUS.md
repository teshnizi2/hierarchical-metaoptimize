# STATUS — operator dashboard

Updated 2 Sep 2026 (cycle 99). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **126**) > `docs/FINDINGS.md` > everything else.

## Verdict

| | |
|---|---|
| Draft | **`paper/DRAFT-v3.md`** — R0 applied in full; `DRAFT-v2.md` kept alongside, superseded |
| Cycle-98 verdict on v2 | **DESK-REJECT**, defensibility 6/10, 15 blocking items |
| R0 (13 zero-GPU items) | **DONE.** Six rewrite packages integrated; see CORRECTIONS 126 |
| R1 / R2 / R3 / R4 | **IN FLIGHT.** `rp1` running, `hz3`-s5 trio pending, `bm2` COMPLETE+UNSCORED, `sm4` running |
| Claims withdrawn this cycle | 3 — alignment refutation → bounded null; M7 falsification → not separable; budget flatness → unresolved trend (126.1) |
| Mechanism tally | **3 refuted** (M2/M3/M6), 1 narrowed (M4), 1 not separable (M7), 3 undecidable (M1/M5/M8) |
| Verification | 55/55 tabled quantities re-derived; 0 placeholders; 4/4 figures on disk; 12/12 equations numbered; `c98_reproduce.py` exit 0 |
| Runs / GPU-h | 2,113 rows + 12 un-ingested `sm3` = **2,125** / ~1,594; +51 jobs in flight |
| Cluster | **BUSY.** 4 batches, 51 jobs |

## Cycle 99 — what changed

* `paper/DRAFT-v3.md` assembled from `paper/sections/*.md` + `docs/ARGS-AUDIT.md`. Every
  cross-package numeric conflict re-derived from `results/all_runs.csv`; the table of conflicts and
  resolutions is CORRECTIONS **126.2**.
* **Convention fixed (STANDING RULE 22):** pooled quantities are computed at **full precision** from
  the run table (Q 43.19 / 36.40), not from Table 2's printed 3-dp values (43.01 / 36.29). Both are
  printed in A.4. This is what made two packages look like they disagreed.
* **Corrections to this dashboard**, from 126.2: the between-base share is **88.4% of the 11-cell Q
  (32.20 / 36.40)** or 74.6% of the legacy 12-cell Q — item 2's "≈75%" paired an 11-cell numerator
  with a 12-cell denominator. Item 2's "k=8, 6 batches" is **7 batches**. Item 3's `+0.299` is
  **+0.298**. Item 15's pooled SGDm D−G `+0.499 ± 0.062` is **+0.514 ± 0.056**.
* **Item 1 could not be followed as written.** It said to rebuild M7 on the within-C10 slope and
  downgrade it to a weak null. Removing `gn1`-GN takes that slope from −0.021 ± 0.077 (t −0.27) to
  −0.161 ± 0.067 (t −2.38, exact perm p 0.0454) — nominally resolved, the *other* way. M7 is
  **not separable**, not null. See 126.1.
* **Two defects found at integration that no package caught** (126.3): `ml2`'s `U` and `T` were
  still tabled at their uncollapsed standard errors. `U` → +0.337 ± 0.112 (t 3.02); `T` → t 3.52.
* `release/` is **not** committed — build product, and `.gitignore` would make its manifest
  unverifiable. Rebuild from a clean checkout with `python3 analysis/c98_release.py`.

## Next cycle, in order

1. **Ingest `sm3`'s 12 rows** (2,113 → 2,125) with `analysis/aggregate.py` **unedited**, then add the
   four-line `CELLS` entry in `analysis/c98_figures.py` named in `paper/sections/production.md` §8.4,
   regenerate the figures and re-run `c98_reproduce.py`. Table 2 goes to 17 cells; the abstract's
   counts and both figure captions move with it.
2. **Score `bm2` (R3)**: `python3 analysis/c97_bm2_score.py`, **unedited**, quote the verdict.
3. Verify R2's ARGS/ENV lines once the trio starts:
   `for J in 4848866 4848867 4848868; do grep -m1 '^ARGS:' .../runs/*-$J.out; done` — `scancel` on
   any mismatch (STANDING RULE 20).
4. Score `rp1` (R1) and `sm4` (R4) when they finish, each with its own registered scorer, unedited.
5. Mint the DOI; rebuild `release/` from a clean checkout; fill the six `⟨…⟩` author-only items.

## Venue table (from the gate)

| venue | as-is | after fixes | the one thing |
|---|---|---|---|
| NeurIPS/ICML/ICLR | 3–5% | 12–18% | transfer probe OUTSIDE MetaOptimize |
| **TMLR** | 30–40% | **65–75%** | rescope the three overstated headlines |
| ML (Springer) / Neurocomputing | ~15% / ~30% | 55–65% | figures, equations, artefact DOI, fill placeholders |
| Workshop (OPT / HiLD) | 55–65% | ~80% | cut to one story + one figure |

## sm3 — COMPLETED, VOID AS DESIGNED, SALVAGED (CORRECTIONS 125.2)

**The second-moment corner does not exist.** `bin/c96_secondmoment.sh` carries the SAME
`--alg-meta` last-wins bug as `c94_meta_ladder.sh`: `BFLAGS` sets `--alg-meta RMSProp`, the
sbatch line then appends `--alg-meta Lion`. The runs' own ARGS line proves it, and the runtime
warns `args_meta includes unnecessary attributes {'normalizer_param'}` (Lion has none).

**So sm3 is a byte-identical independent replicate of `aw1`** (AdamW base × Lion meta, box
−15:−2.3026, ms 1e-4, α0 1e-3, 100 ep, 3 seeds). Re-derived from the raw `.out` series:

| arm | aw1 | sm3 | offset |
|---|---|---|---|
| nodewise | 92.978 | 93.103 | +0.125 |
| chunk777 | 93.257 | 93.244 | −0.013 |
| nodewise1d | 93.069 | 93.019 | −0.050 |
| chunk2325 | 93.301 | 93.315 | +0.014 |

| contrast | aw1 (3v3) | sm3 (3v3) | pooled (6v6) |
|---|---|---|---|
| D | +0.279 ± 0.087 (t 3.19) | **+0.141 ± 0.064 (t 2.22)** | **+0.210 ± 0.056 (t 3.76)** |
| G | +0.232 ± 0.089 (t 2.62) | **+0.296 ± 0.096 (t 3.07)** | **+0.264 ± 0.060 (t 4.42)** |
| D − G | +0.047 | −0.155 | −0.054 |

**Three things this buys, all free:**
1. **An 18th count-matched cell, still positive** → "positive in every cell" survives, and the
   completeness sentence the gate asked for gets stronger.
2. **G under AdamW is now RESOLVED IN TWO INDEPENDENT BATCHES** (t 2.62, t 3.07). The rewrite the
   panel demanded for §5.4 / M4 is now a replicated fact: **the tail carries ~none of D under
   AdamW** (D − G = −0.054 at 6v6), and most of it under SGDm.
3. **The base-optimiser moderator has 2 design points at AdamW instead of 1** — the exact gap
   Q01 says makes the moderator unvalidatable out of sample. AdamW is now covered; SGD, RMSProp
   and GroupNorm are still n=1.

**Batch offsets ≤ 0.125 pp across four arms** — an independent confirmation of the withdrawn
"batch is a large random effect" claim's replacement bound.

## What to run, ranked by what the REVIEW demanded

| # | run | jobs / GPU-h | demanded by | buys |
|---|---|---|---|---|
| **R0** | **zero-GPU rewrite package** (13 of 15 blocking items) | 0 | gate S1/S3/S5/S6/S9/S11 + Q01/Q03/Q04/Q05/Q08/Q09/Q15/Q17/Q20/Q21/Q22 | the desk-accept. **Do this first; nothing else matters until it is done** |
| **R1** | **permnode 3 perm-draws × 6 seeds, permutation seed DECOUPLED from run seed** + 6-seed nodewise arm | 24 / ~24 | Q02, Q14, red-team #4, gate blocking #3 | turns the 2nd headline from an n=3 single-batch null (CI = [−55%,+51%] of D) into a two-way variance decomposition. se 0.157 → ~0.09 |
| **R2** | **hz3 seed-5 trio re-run in box −30:9.0** (`ch`, `c23`, `n1d` @300 ep) | 3 / ~9 | red-team #2, gate blocking #4 | repairs the ONLY budget-generalisation result. Restores 6v6 box-matched; today the "flat" verdict (t −1.42) depends on the contaminated pair (t −1.93 without it) |
| **R3** | **base-moderator replication**: 2nd independent batch at SGD and RMSProp bases, node+chunk777, 3 seeds | 12 / ~12 | Q01 / gate blocking #2 (the §4.4 rewrite's weak flank) | the new headline is "base optimiser explains ~75% of Q". Today SGD/RMSProp are ONE batch (`nl1`) each. This makes the moderator replicated at every level except GroupNorm |
| **R4** | **non-meta transfer probe**: same 4 partitions as a per-group LR scale on plain SGDm/AdamW, no meta-learning | ~24 / ~24 + patch | Q16, venue table (main-track "one thing") | the ONLY route from 12–18% to a main-track paper. Converts an internal audit of one framework into a claim about step-size granularity. Needs design work — a fixed per-group LR scale is not a straight port |
| R5 | additive tail test A1/A2 (chunk2325 ± a manufactured 9,610-singleton tail at m = 4,851 exactly) | ~40 / ~40 + patch + suite | **NOBODY** | breaks the tail/alignment confound. Registered at 124.6, still the best mechanism experiment — but no reviewer asked for a mechanism, and §5.7's non-identifiability is already an accepted limit |

## CUT

| candidate | why cut |
|---|---|
| **TinyStories** | **WEEKS, not days, and zero reviewers asked for it.** Data IS ready (50 pretok `.bin` shards, 10 G, staged 19 Aug) and `train.py` already takes `--stepsize-groups`. But that tree's `HF.py` supports only `scalar/layerwise/nodewise/weightwise/*_blocks` — **no chunkwise, no nodewise1d, no permnode, no probe5**. The whole instrument must be ported and re-verified (4 patches + a Transformer count-matching census + the equivalence suite), then η/α0 calibrated from scratch (zero training runs have EVER been executed there; only `ts-pretok`), then a primary. ≥3 weeks and ≥300 GPU-h before the first contrast. And it answers a scope limit the abstract already states honestly — **not** the reviewers' ask, which is transfer outside MetaOptimize (R4), not a new modality inside it |
| more G cells | R0 needs a Holm rule over the 12 existing G tests, not a 13th |
| more seeds on existing D cells | seed is null; the cells are balanced with zero attrition |
| budget-matched GroupNorm rescue | the gate asked for gn1-GN to be REMOVED. Removal is free |

## Do before anything else (R0 checklist, in gate order)

| # | item | zero GPU |
|---|---|---|
| 1 | **Remove `gn1`-GN** from Table 2, from the 12-cell pool, from the abstract's counts, and from §5.6. Its own registered scorer prints *"NO TRANSFER VERDICT IS ISSUED … THIS IS NOT A NULL"*. Rebuild M7 on the within-C10 slope alone and downgrade it to a weak null | yes |
| 2 | **§4.4 → a decomposition.** Total Q 43.0/11; within SGDm+BN (k=8, 6 batches, 2 η, 2 budgets) **Q 4.22/7, p 0.75, τ 0.000**, pool +0.555 ± 0.045; between-base Q 32.1/3. Delete *"for reasons we cannot attribute"* from §4.4, the abstract and §9 | yes |
| 3 | **Alignment → a BOUNDED NULL.** Print A = −0.009 [−0.317, +0.299] = [−55%, +51%] of D, MDE 0.44 pp, and the registration defect (band half-width 0.15 < realised se 0.157). Delete "REFUTED"/"does nothing" from title strapline, abstract, §1.1 #2, §4.6, §9 | yes |
| 4 | **Delete "byte-identical"** — the 12 cells span 3 β-boxes; `c87_rl3_score.py`'s own header forbids cross-box pooling. Add a box column to Table 2 and Appendix B | yes |
| 5 | **Rewrite T9**: the three `hz3` seed-5 rows are NOT a metadata defect. Their own ENV line reads `BETA_CLIP=−15:−2.3026`; the config really differs. hz3 is also not one contiguous submission (job span 32,288) | yes |
| 6 | **§3.3: disclose test-set selection.** No validation split was held out; every tuning decision selects on `plateau5`. Label §4.5's dD = −0.090 an UPPER BOUND; note T4's deficit is conservative | yes |
| 7 | **Attrition table**: 2,113 attempted / 442 dropped (window_ok 400, no plateau5 25, incomplete 17) crossed with granularity + the two defusing facts (392 of 442 are 20-ep probes; **admissible n == submitted n in all 17 cells**) | yes |
| 8 | **G decision rule**: state it, apply it to all 12 cells, report 3 of 12 resolved at nominal α (aw1 2.62, ml2 2.44, g3m 2.34), none surviving Holm. Change M4 to "base-dependent". **Now backed by sm3's replicate** | yes |
| 9 | **Q04's unwritten sentence** — "Table 2 plus the excluded `ar1` cell is the COMPLETE set of count-matched contrasts in the corpus; none is omitted and the excluded one is also positive." Strongest available sentence, currently unsaid | yes |
| 10 | **4 figures, one palette**: F1 forest of the cells by base; F2 ck1 ladder vs log m; F3 within-run D(epoch) trough; F4 A/B/D decomposition with the share interval | yes |
| 11 | **Numbered display equations** for D/G/A/U/T, plateau5, the admissibility predicate | yes |
| 12 | **Fill both end-matter placeholders**; ship a DOI/anon URL, framework+CUDA versions, per-batch {script, commit, scorer, md5, seeds registered vs realised}, `make reproduce-table2`, and a corrected `beta_clip` column | yes |
| 13 | **Fix the count**: title says eight dead mechanisms; the M-table says M1 "untested", M5 "inapplicable", M4 "narrowed", M8 "not identifiable". Retitle or re-partition the index | yes |
| 14 | **T4 superlative**: 93.317 is the best **ResNet-18** cell, not the corpus max. State the grouping key and report both deficits | yes |
| 15 | Unicode → LaTeX macros (152 lines); Appendix order A.7→A.9→A.8; Table 2 caption (gn1's two rows share a batch); "17 under 90%" is 16; label the two ses for rl3's D; quote the POOLED SGDm D−G (+0.499 ± 0.062), not cc1's max; re-obtain Zheng & Kwok from arXiv source; hedge Adam-mini as Adalayer is hedged; state CAM-HD's method was never implemented | yes |

## Ingest / housekeeping

| # | item |
|---|---|
| 1 | **Ingest sm3's 12 rows** into `results/all_runs.csv` (→ 2,125). Its `meta` column must read **Lion**, not RMSProp |
| 2 | **AUDIT EVERY BATCH'S ARGS LINE, not its submission script.** `c94` and `c96` both shipped a double `--alg-meta`. `c43/c44/c48/c49/c57/c58/c72/c83/c84/c87` each contain ≥2 `--alg-meta` occurrences and are unaudited |
| 3 | **STANDING RULE 20**: a batch's science is what the runs' own ARGS line says, never what the script header claims. Every batch report must quote one ARGS line verbatim |
| 4 | **STANDING RULE 21**: no batch is submitted without a registered scorer. `sm3` had none (`analysis/` has no `c96_*`), which is why a void batch ran to completion unremarked |
| 5 | `ar1` admissibility must be the SAME rule in every analysis (box-VOID, 117.1) |
| 6 | `nl1` is ONE batch, not two |
