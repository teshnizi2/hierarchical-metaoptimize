# STATUS — operator dashboard

Updated 31 Aug 2026. Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins) > `docs/FINDINGS.md` > everything else.

## Verdict

| | |
|---|---|
| Do we have a paper? | **Yes.** Reframed 31 Aug. Not the original idea. |
| Title | *A granularity gain is a tuning gain* |
| Thesis | "Number of step sizes" is **4 variables**, not 1. Each moves the effect by more than the effect. |
| Runs / GPU-h | 1,984 / ~1,250 |
| Biggest risk | External validity: 1 base optimiser, 1 meta optimiser, 0 rows at the parent's own eta=1e-3 |

## The four claims

| # | claim | number | state |
|---|---|---|---|
| 1 | Meta-stepsize dominates | layerwise−scalar +3.291 at eta=1e-3, **+0.655 tuned** | GREEN |
| 2 | alpha0 sets the sign | monotone up at 1e-6, down at 1e-3 | GREEN |
| 3 | Count is convex in log m, not a slope | 10 rungs, 5.25 decades | GREEN |
| 4 | Size distribution at fixed count | D +0.595 (R18) / +0.666 (R34) / +1.640 (C100) | GREEN |
| — | Alignment is NOT the carrier | −0.009, t −0.06 | GREEN |
| — | Practitioner: merge 1-D tensors | +0.756 (8% count, 92% tail) | GREEN |

## Dead — do not reopen

Hierarchical pooling · Idea 1 (cosine prior) · Idea 2 · Direction C (N_eff/m predicts accuracy) ·
sqrt(N) attribution to Adam-mini/Adalayer/SGG · singleton-fraction law · horizon reversal as a
granularity claim · ImageNet (val set unlabelled) · method competitiveness (−1.81 pp vs cosine)

## Corrections that cost us claims

| what | why |
|---|---|
| "Adam-mini groups per channel" | It is **one block per tensor** — ships our prescription |
| "Size-1 groups are the carrier" | Removing singletons buys +0.115 (t 0.87). Unit is the **tensor** |
| "C100 has the largest D" | Incommensurable scale; on relative error it is the **smallest** |
| `ar1` as replication | Box-bound asymmetrically → VOID |
| Count slope −0.49 | In-batch value is **+0.135**. Four imported values were wrong |
| Our anomaly reframe | Parent §7.1 has no seed count and no error bars |

## Closed this week

| test | result |
|---|---|
| `g3m` ResNet-34 | Mechanism generalises. D +0.666, D−G +0.495 |
| `gc1` CIFAR-100 | D +1.640. Screen only, no mechanism leg |
| `gn1` GroupNorm | **No verdict** — commensurability gate fired (1.37x budget ratio) |
| `rl3` Rule 11 | **CLOSED.** dD −0.090, t −0.51 |
| `fa1` floor fix | rec_lo 0.0000 on 24/24 |

## Queue

| batch | acct | jobs | question | risk |
|---|---|---|---|---|
| `hz3` | alice | 24 (13 done) | Does D survive 300 epochs? | **HIGH — D is negative for most of training** |
| `ub9` | alice2 | 9 | Is the parent's own cell a clipping artefact? | Either answer is publishable |
| `aw1` | — | 12 | AdamW base (zero coverage today) | not built |
| `gf2` | — | 20 | granularity x eta surface | not built |
| `r50` | — | 30 | ResNet-50 (kill was premature) | not built |

## Open

1. Tail vs BatchNorm — under-identified, `gn1` could not separate
2. Rule 11 on R34 / C100 — no ladder there
3. Mechanism on CIFAR-100 — no tail-removed arm
4. Base-optimiser axis — 112/112 rows are SGDm

## Standing rules that bite

Batch is the unit of replication (F=5.47), seed is null · box occupancy from per-coordinate rails,
never the 62-element beta summary · count-match or correct · never compare raw pp across error
budgets · register the scorer before the runs · test guards in both directions
