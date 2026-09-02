# STATUS — operator dashboard

Updated 2 Sep 2026. Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins) > `docs/FINDINGS.md` > everything else.

## Verdict

| | |
|---|---|
| Do we have a paper? | **Yes.** A MEASUREMENT paper. Not a mechanism paper, not a prediction paper. |
| Title | *A granularity gain is a tuning gain* |
| Thesis | "Number of step sizes" is **4 variables**, not 1. Each moves the effect by more than the effect. |
| Runs / GPU-h | 2,077 / ~1,300 |
| Biggest risk | **No mechanism.** 7 candidate carriers dead; the 8th is not identifiable from this corpus |

## Cycle 96 — two zero-GPU analyses, both NULL (CORRECTIONS 124)

| analysis | question | verdict | survives review |
|---|---|---|---|
| 1 — carrier | which property of the size distribution carries D? | **NOT IDENTIFIABLE** | verdict yes, its positive claim **DELETED** |
| 2 — prediction | can D be predicted from cell properties? | **NOT PREDICTABLE** | **yes, intact — paper-ready** |

* Analysis 1's "degeneracy indicator carries D, β −0.986, t −12.5" **is an arm dummy.**
  `frac_groups_size1` is 0.6664 on nodewise and 0.0000 on all three other arms; its shape test is
  χ² 7.5665/10 — **identical to five figures** to a bare nodewise dummy, to an arbitrary two-level
  regressor, and to the plain "the other three arms share a mean" test. Refuted out of sample by
  `ck1` (+0.106 ± 0.18 vs +0.986 claimed, 4.9 se).
* Root cause: at fixed count the corpus has **one contrast type**; design-matrix **rank 3**;
  20 candidates collinear at |r| ≥ 0.93 collapse to ~2 classes. CV cannot catch this.
* Analysis 2: LOO over 11 design points. Mean baseline RMSE **0.4005**. Best model 0.3284, and
  **100% of that margin is the single CIFAR-100 point**. Inside CIFAR-10 the **mean wins**
  (0.2791 vs 0.2863). Sign test p 0.227. Power bound: n=11 needs |r| ≥ 0.602.
* **PRESERVED:** D is genuinely heterogeneous — Q 43.0/11 df, p 1.1e-5, τ 0.285 pp vs 0.137 pp noise.

## Newly dead this cycle

| what | how it died |
|---|---|
| **Level slope −0.392** (cycle 95 headline) | exact permutation **p 0.167** (4/24); **+0.026 ± 0.088** inside CIFAR-10; `gn1`'s within-batch BN/GN pair moves D the **WRONG WAY by up to 7 se** |
| Size-distribution carrier, any named statistic | not identifiable — arm indicator in disguise |
| D as a predictable quantity | no model beats the corpus mean out of sample |

**Gain, not loss:** *"partition matters" is NOT a restatement of where the aligned arm lands* — now
supported from the other direction, and a covariate we would have had to defend is gone.

## Do before anything else

| # | item |
|---|---|
| 1 | **Fix CSV:** `hz3-c23-s5`, `hz3-ch-s5`, `hz3-n1d-s5` carry `beta_clip -15:-2.3026`; the batch is `-30:9.0`. A scorer grouping on `beta_clip` reads D(300) **+0.464 instead of +0.428** |
| 2 | `ar1` admissibility must be the SAME rule in every analysis (box-VOID, 117.1) |
| 3 | **`nl1` is ONE batch**, not two. Non-SGDm evidence is 2 batches / 6 df |

## Next batch to build (registered, NOT submitted — CORRECTIONS 124.6)

Additive tail test: **A1 = chunk2325** vs **A2 = chunk2325 with a manufactured 9,610-group size-1
tail at m = 4,851 EXACTLY**. First arm ever that is neither architecture-aligned nor tail-free.
Plus a **heterogeneity sweep at zero degeneracy** (CV 0.09/0.40/0.76/1.90, min size ≥ 10).
Both under **AdamW and SGDm**. ~40 jobs, 2 batches. Prioritise over more G cells.

**Do NOT buy:** more seeds (seed null; sd of D across 4 owned batches 0.0994 < 0.1719 seed-noise
expectation) · another R18/SGDm/CIFAR-10/100-ep replicate · anything moving count and partition together.

## The four claims

| # | claim | number | state |
|---|---|---|---|
| 1 | Meta-stepsize dominates | layerwise−scalar +3.291 at eta=1e-3, **+0.655 tuned** | GREEN |
| 2 | alpha0 sets the sign | monotone up at 1e-6, down at 1e-3 | GREEN |
| 3 | Count is convex in log m, not a slope | 10 rungs, 5.25 decades | GREEN |
| 4 | Size distribution at fixed count | **15 cells**, D +0.202 … +1.640; Q 43.0/11 df, τ 0.285 pp | GREEN |
| — | Alignment is NOT the carrier | −0.009, t −0.06 | GREEN |
| — | **WHICH property of the size distribution** | not identifiable — needs new runs (124.1) | **OPEN** |
| — | **D is not predictable** | no model beats the mean; LOO 0.3284 vs 0.4005, all of it 1 point | GREEN (null) |
| — | Practitioner: merge 1-D tensors | +0.756 (8% count, 92% tail) | GREEN, **SGDm-scoped** |

## Dead — do not reopen

Hierarchical pooling · Idea 1 (cosine prior) · Idea 2 · Direction C (N_eff/m predicts accuracy) ·
sqrt(N) attribution to Adam-mini/Adalayer/SGG · singleton-fraction law · horizon reversal as a
granularity claim · ImageNet (val set unlabelled) · method competitiveness (−1.81 pp vs cosine) ·
base-optimiser normalisation · **the −0.392 level slope** · **D as a predictable quantity** ·
**any named size-distribution statistic as "the carrier"**

## Corrections that cost us claims

| what | why |
|---|---|
| "Adam-mini groups per channel" | It is **one block per tensor** — ships our prescription |
| "Size-1 groups are the carrier" | Removing singletons buys +0.115 (t 0.87). Unit is the **tensor** |
| "C100 has the largest D" | Incommensurable scale; on relative error it is the **smallest** |
| `ar1` as replication | Box-bound asymmetrically → VOID |
| Count slope −0.49 | In-batch value is **+0.135**. Four imported values were wrong |
| Our anomaly reframe | Parent §7.1 has no seed count and no error bars |
| "D ~ aligned-arm LEVEL, slope −0.392" | permutation p 0.167; +0.026 inside C10; `gn1` falsifies it by up to 7 se |
| "Degeneracy indicator carries D, t −12.5" | It is an **arm dummy** — χ² identical to a bare nodewise indicator |

## Closed this week

| test | result |
|---|---|
| **carrier analysis** (0 GPU) | **NOT IDENTIFIABLE.** 150 multisets constructed, R1/R2 receipts pass; rank-3 design |
| **prediction analysis** (0 GPU) | **NOT PREDICTABLE.** 15 cells → 11 design points; mean wins inside CIFAR-10 |
| `g3m` ResNet-34 | Mechanism generalises. D +0.666, D−G +0.495 |
| `gc1` CIFAR-100 | D +1.640. Screen only, no mechanism leg |
| `gn1` GroupNorm | **No verdict** — commensurability gate fired (1.37x budget ratio) |
| `rl3` Rule 11 | **CLOSED.** dD −0.090, t −0.51 |
| `fa1` floor fix | rec_lo 0.0000 on 24/24 |

## Queue

| batch | acct | jobs | question | risk |
|---|---|---|---|---|
| `r50` | alice | 12 | ResNet-50, the 4th architecture | **RUNNING — do not disturb** |
| `ml2` | alice2 | 24 | meta-optimizer axis (Adam / RMSProp) | **RUNNING — do not disturb** |
| `tl1` | — | ~20 | **additive tail test** A1 vs A2 at m=4,851 exactly (124.6) | not built — **TOP PRIORITY** |
| `hv1` | — | ~20 | heterogeneity sweep at zero degeneracy, CV 0.09→1.90 | not built |
| `lv1` | — | ~16 | **within-batch level ladder** — the only way to test level properly | not built |
| `gf2` | — | 20 | granularity x eta surface | not built |
| `ub9` | alice2 | 9 | parent's own cell a clipping artefact? | **status UNVERIFIED this cycle** |
| — | — | — | *closed since: `hz3`, `aw1`, `nl1`, `gm2`* | — |

## Open

1. **WHICH property of the size distribution** — unidentifiable at fixed count; needs `tl1` + `hv1`
2. Tail vs BatchNorm — under-identified, `gn1` could not separate
3. Rule 11 on R34 / C100 — no ladder there
4. Only **ONE** CIFAR-100 design point; dataset / level / singleton-fraction are the SAME column
5. `m` and `params` are 1-vs-10 leverage contrasts (`g3m` alone) — LOO RMSE 13.3 / 38.8

## Standing rules that bite

Batch is the unit of replication (F=5.47), seed is null · box occupancy from per-coordinate rails,
never the 62-element beta summary · count-match or correct · never compare raw pp across error
budgets · register the scorer before the runs · test guards in both directions · **RULE 16: run the
registered scorer UNEDITED and quote it, never hand-roll a reduction** · **state the identifiability
bound BEFORE the coefficients, not after**
