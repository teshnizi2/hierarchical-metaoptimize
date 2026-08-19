# RESULTS-VERIFIED

Independent re-derivation of every reported number from the raw Slurm `.out` artefacts.
No claim in any other document in this repo was taken on trust; where the numbers here
disagree with existing prose, the numbers here are the ones with a derivation attached.

**Date of extraction:** 2026-08-19
**Data refreshed:** `rsync` from `alice:/data1/salehkaleybars/metaopt/runs/` and
`alice2:/home/s5014158/metaopt/runs/` — both succeeded (exit 0) immediately before analysis.
**Aggregation:** `analysis/aggregate.py ../runs ../runs_alice2 > results/all_runs.csv` (561 runs).
**Analysis:** a separate re-parse of the same `.out` files was used for all tables below, because
the repo's `plateau` column is the mean of the last **20** epochs, and the primary metric
specified here is the mean of the last **5**. Both were computed; they do not change any verdict.

---

## 0. Population, exclusions, and two methodological corrections

### 0.1 Corpus

| | count |
|---|---|
| `.out` files parsed with a usable `ARGS:` line and ≥1 test accuracy | **561** |
| superseded (same `--run-name` resubmitted; shorter copy dropped) | 3 |
| completed their requested budget, budget ≥ 20 epochs | **504** |
| — of which 100-epoch | 452 |
| — of which 300-epoch | 16 |
| — of which 20-epoch | 36 |
| truncated 100-epoch runs (excluded: a run cut at epoch 55 has no plateau) | 25 |
| identity/smoke gates at 2–5 epochs (excluded from all result tables) | 29 |
| by cluster account | salehkaleybars 344, s5014158 217 |
| config provenance | `ENV:` line 452, reconstructed from run name 109 |

**Everything below reports `n` for every cell and suppresses cells with n < 3.**

### 0.2 Correction 1 — `best_test` inflation is real, and the brief's estimate is right

On clean (non-collapsed) guard-on ResNet18/CIFAR-10/100-epoch runs, n = 335:

| statistic | mean | sd | median |
|---|---|---|---|
| `best_test − plateau(last 5)` | **+0.266 pp** | 0.110 | 0.256 |
| `best_test − plateau(last 20)` | **+0.420 pp** | 0.315 | — |

The inflation is 0.27–0.42 pp depending on plateau window. Several effects reported in this
project are 0.2–1.0 pp. `best_test` is therefore never used as a primary metric here.
(On the full population including collapsed runs the gap averages 4.3 pp — a `best_test`
table would rank a run that peaked at 72 % and then collapsed to 10 % as a near-success.)

### 0.3 Correction 2 — the SwiftTD guard is a hidden blocking factor and MUST be stratified

`BETA_CLIP = -15:-2.3026` (the SwiftTD-style step-size guard) is present in 407 of the 504
analysable runs and absent in 97. It is **not** a nuisance variable. Within
SGDm/Lion/α₀=1e-6/plain/100ep:

| granularity | guard ON | guard OFF | difference |
|---|---|---|---|
| scalar | 87.89 ± 0.16 (n=11) | 87.90 ± 0.09 (n=6) | −0.01 pp, p = 0.82 |
| resnet18_blocks | 91.43 ± 0.17 (n=11) | 91.37 ± 0.18 (n=6) | +0.06 pp, p = 0.52 |
| layerwise | 90.91 ± 0.19 (n=20) | 91.00 ± 0.12 (n=4) | −0.10 pp, p = 0.24 |
| **weightwise** | **79.11 ± 0.39 (n=6)** | **10.00 ± 0.00 (n=10)** | **+69.11 pp, p < 0.001** |

The guard is inert for every granularity except per-weight, where it is the difference between
a working optimiser and 10/10 runs at chance. Any table that pools guarded and unguarded
per-weight runs produces a meaningless "35.91 ± 34.55" — a mixture of two configurations, not a
measurement. Below, per-weight is always reported guard-on; other granularities are pooled over
the guard with the inertness above as justification.

### 0.4 What is absent from the corpus

Three of the seven requested factors cannot be answered, and this is a data fact, not an
analysis choice:

- **ResNet34 / ResNet50 / ResNet101**: one truncated ResNet34 scalar run (71/100 epochs) and
  three 2-epoch smoke tests. Zero completed runs at any granularity. The scale axis is
  ResNet10 vs ResNet18 only.
- **CIFAR-100**: three runs in the entire corpus, of 3, 3, and 5 epochs. Two are byte-identical
  in their test series. Best accuracy reached: 20.99 %.
- **zpool at 300 epochs**: zero runs. The zpool sweep exists only at 100 epochs.

---

## (a) Granularity × base optimiser — the H4 interaction

ResNet18 / CIFAR-10 / 100 epochs / `hier=plain`. Cells are plateau(last 5), mean ± sd, n.
`[k fail]` marks k runs finishing below 60 pp.

### α₀ = 1e-6

| meta / base | scalar | resnet18_blocks | layerwise | nodewise | weightwise |
|---|---|---|---|---|---|
| Lion / **SGDm** | 87.89 ± 0.14 (n=17) | 91.41 ± 0.17 (n=17) | 90.92 ± 0.18 (n=24) | 91.74 ± 0.14 (n=8) | 79.11 ± 0.39 (n=6, guard-on) |
| Lion / **AdamW** | 91.62 ± 0.15 (n=3) | 91.35 ± 0.37 (n=3) | 91.51 ± 0.20 (n=3) | — (n=0) | 85.59 ± 0.26 (n=3) |
| Adam / **SGDm** | 58.62 ± 36.29 (n=7) **[3 fail]** | 90.74 ± 0.14 (n=7) | 90.45 ± 0.20 (n=12) | — (n=0) | 50.19 ± 0.86 (n=3) |
| Adam / **AdamW** | 91.60 ± 0.15 (n=6) | 91.73 ± 0.13 (n=6) | 91.80 ± 0.11 (n=6) | — (n=0) | — (n=0) |

### α₀ = 1e-4

| meta / base | scalar | resnet18_blocks | layerwise |
|---|---|---|---|
| Lion / SGDm | 87.79 ± 0.32 (n=7) | (n=2) | 90.93 ± 0.29 (n=7) |
| Adam / AdamW | 91.83 ± 0.10 (n=3) | 91.68 ± 0.14 (n=3) | 91.95 ± 0.10 (n=3) |

### α₀ = 1e-3

| meta / base | scalar | resnet18_blocks | layerwise |
|---|---|---|---|
| Lion / SGDm | 87.90 ± 0.19 (n=6) | (n=2) | 91.33 ± 0.06 (n=5) |
| Adam / SGDm | (n=2) | (n=2) | (n=2) |
| Adam / AdamW | 92.71 ± 0.08 (n=3) | 92.03 ± 0.10 (n=3) | 90.82 ± 0.18 (n=3) |

### The interaction (α₀ = 1e-6, meta = Lion — the only cell with both bases at n ≥ 3)

| granularity | SGDm − its scalar | AdamW − its scalar | interaction | verdict |
|---|---|---|---|---|
| resnet18_blocks | **+3.52** (n=17) | −0.26 (n=3) | **+3.78 ± 0.23 pp** | outside noise |
| layerwise | **+3.03** (n=24) | −0.11 (n=3) | **+3.13 ± 0.15 pp** | outside noise |
| weightwise (guard-on) | −8.79 (n=6) | −6.03 (n=3) | −2.76 ± 0.24 pp | outside noise |

Under meta=Adam the interaction is **not computable**: the SGDm/scalar reference is bimodal
(58.62 ± 36.29, 3 of 7 runs stuck at 18–21 %), so no contrast against it means anything.
This instability is not a guard artefact — 1 of 4 guarded runs fails too.

### Secondary metric — epochs to target (α₀ = 1e-6, plain), `[reached / total]`

| meta / base | metric | scalar | blocks | layerwise | nodewise | weightwise |
|---|---|---|---|---|---|---|
| Lion/SGDm | ep→88 | 90.9 ± 7.9 [11/17] | 36.2 ± 1.1 [17/17] | 36.0 ± 1.2 [24/24] | 36.6 ± 1.2 [8/8] | never [0/16] |
| Lion/SGDm | ep→90 | never [0/17] | 43.5 ± 1.7 [17/17] | 55.6 ± 4.2 [24/24] | 48.2 ± 1.8 [8/8] | never [0/16] |
| Lion/AdamW | ep→90 | 33.3 ± 2.5 [3/3] | 35.7 ± 0.6 [3/3] | 32.7 ± 2.1 [3/3] | — | never [0/3] |
| Adam/AdamW | ep→90 | 31.5 ± 3.9 [6/6] | 29.0 ± 2.3 [6/6] | 26.0 ± 1.7 [6/6] | — | — |

Under SGDm the speed benefit is large but **censored**: scalar never reaches 90 % at all, so
"granularity is faster" under SGDm is partly a statement that scalar never gets there. Under
AdamW every granularity reaches 90 % within 26–36 epochs and the ordering is flat.

### The level check that reframes the whole interaction

Best SGDm plain granularity (nodewise, 91.74 ± 0.14, n=8) versus AdamW's *scalar*
(91.62 ± 0.15, n=3): a difference of +0.12 pp. **Granularity under SGDm does not create
capability; it recovers the level AdamW reaches with a single scalar step size.** The
interaction is real and large, but it is an interaction with how badly the base optimiser is
served by one global step size — not evidence that fine granularity is a source of headroom.

At α₀ = 1e-3 the AdamW effect is not merely null but **negative**: layerwise 90.82 vs scalar
92.71, −1.89 pp (t = −16.3, p = 0.001, n = 3,3); blocks −0.68 pp (p = 0.001).

---

## (b) M1 additive pooling — plateau vs η-ratio r

ResNet18 / CIFAR-10 / 100 epochs / SGDm / Lion / layerwise / α₀ = 1e-6. All 45 runs guard-on.
Reference: plain layerwise **90.92 ± 0.18 (n=24)**.

| r | n | plateau | sd | Δ vs plain layerwise | ep→90 | ep→91 |
|---|---|---|---|---|---|---|
| 0.00 (full pooling) | 6 | 92.288 | 0.117 | +1.37 pp | 41.5 ± 0.5 | 44.5 ± 0.5 |
| 0.03 | 5 | 92.620 | 0.135 | +1.70 pp | 40.6 ± 0.5 | 42.8 ± 1.6 |
| 0.04 | 4 | 92.892 | 0.162 | +1.97 pp | 41.5 ± 0.6 | 42.8 ± 1.0 |
| 0.05 | 5 | 93.066 | 0.107 | +2.14 pp | 41.6 ± 0.5 | 44.0 ± 1.4 |
| **0.06** | 3 | **93.302** | 0.146 | **+2.38 pp** | 41.3 ± 0.6 | 44.3 ± 0.6 |
| **0.07** | 8 | **93.233** | 0.158 | **+2.31 pp** | 41.2 ± 0.5 | 44.1 ± 1.0 |
| 0.10 | 5 | 92.598 | 0.160 | +1.68 pp | 40.6 ± 1.1 | 43.8 ± 3.1 |
| 0.20 | 3 | 91.519 | 0.210 | +0.60 pp | 43.3 ± 2.5 | 56.0 ± 2.0 |
| 0.30 | 3 | 91.167 | 0.147 | +0.25 pp | 53.0 ± 5.0 | 72.0 ± 9.6 |
| 1.00 (no pooling) | 3 | 90.971 | 0.129 | +0.05 pp (p = 0.59) | 54.0 ± 2.0 | 85.3 ± 6.8 |
| *plain layerwise* | 24 | 90.921 | 0.178 | — | 55.6 ± 4.2 | 83.9 ± 8.5 [22/24] |

**Identity gate passes:** r = 1 reproduces plain layerwise to within 0.05 pp (p = 0.59),
confirming the parameterisation and that r = 0 is the full-pooling endpoint.

**Is there an interior optimum?** Yes, decisively.

| contrast | Δ | combined SE | test |
|---|---|---|---|
| peak (r=0.06) − r=0 | **+1.014 pp** | 0.097 | t = 10.5, p = 0.001 |
| peak (r=0.06) − r=1 | **+2.331 pp** | 0.112 | t = 20.7, p < 0.001 |

The peak exceeds both endpoints by 10× and 21× its own standard error. It is **not** inside noise.

**At what n, and how well localised?** The argmax cell r = 0.06 has only n = 3 and comes from a
single run family (`sc-ResNet18-add-s0/1/2`). But r = 0.07 sits at 93.233 with **n = 8 drawn
from two independent families on two different cluster accounts** (`ad-l-r007_*`, n=5, and
`zad-r007_*`, n=3; 93.06–93.41 across all eight). r=0.06 and r=0.07 are statistically
indistinguishable (Δ = 0.069, p = 0.53). The optimum is therefore best stated as
**r ∈ [0.05, 0.07]**, with r = 0.07 the best-supported single point. r = 0.05 (n=5) is 0.24 pp
below the peak at p = 0.084 — the plateau top is flat over that window.

**Speed:** the additive gain is an accuracy effect, not a speed effect, at the top of the curve.
Every r ≤ 0.1 reaches 90 % in 40.6–41.6 epochs — indistinguishable from each other, though all
~14 epochs faster than plain layerwise (55.6). The ep→91 column separates the arms much more
sharply than ep→90, because 90 % sits close to plain layerwise's asymptote.

---

## (c) zpool — plateau vs r, split by budget

### The budget split cannot be made

**zpool has zero runs at 300 epochs.** The complete zpool inventory: 68 runs at 100 epochs
(34 layerwise, 34 weightwise) and 6 single-seed runs at 20 epochs. The 300-epoch block
(16 runs total) contains only plain, shrink, and additive arms. The requested
100-vs-300 comparison for zpool does not exist in the data.

### zpool at 100 epochs, layerwise (SGDm/Lion/α₀=1e-6, all guard-on)

Reference: plain layerwise 90.92 ± 0.18 (n=24).

| r | n | plateau | Δ vs plain layerwise | ep→90 |
|---|---|---|---|---|
| 0 | 5 | 87.88 ± 0.16 | **−3.04 pp** | never [0/5] |
| 0.1 | 5 | 89.73 ± 0.14 | −1.19 pp | [2/5] |
| 0.3 | 5 | 89.68 ± 0.19 | −1.24 pp | [1/5] |
| 0.5 | 4 | 89.36 ± 0.12 | −1.56 pp | never [0/4] |
| 0.7 | 6 | 89.23 ± 0.25 | −1.69 pp | never [0/6] |
| 0.9 | 2 | 90.34 | — (n<3) | [2/2] |
| 0.95 | 1 | 90.62 | — (n<3) | [1/1] |
| 0.99 | 1 | 91.11 | — (n<3) | [1/1] |
| 1 | 5 | 91.04 ± 0.18 | +0.12 pp | 54.0 ± 3.4 [5/5] |

**zpool never helps layerwise at any r.** It is monotonically damaging as pooling increases,
and its best value is the no-pooling endpoint. Identity gate passes (r=1 ≡ plain, +0.12 pp).

### zpool at 100 epochs, weightwise (SGDm/Lion/α₀=1e-6, all guard-on)

Reference: plain weightwise, guard-on, 79.11 ± 0.39 (n=6).

| r | n | plateau | Δ vs plain weightwise |
|---|---|---|---|
| 0 | 5 | 87.94 ± 0.07 | **+8.83 pp** |
| 0.1 | 5 | 87.99 ± 0.11 | +8.88 pp |
| 0.3 | 5 | 88.09 ± 0.19 | +8.98 pp |
| 0.5 | 4 | 88.00 ± 0.17 | +8.89 pp |
| 0.7 | 6 | 88.26 ± 0.15 | +9.15 pp |
| 0.9 | 2 | 88.61 | — (n<3) |
| 0.99 | 1 | 89.11 | — (n<3) |
| 1 | 5 | 79.23 ± 0.35 | +0.12 pp (identity gate passes) |

**zpool's sign is granularity-dependent**: it costs layerwise 1–3 pp and buys per-weight
~9 pp. Across r ∈ [0, 0.7] the weightwise curve is flat within ±0.35 pp — there is no
interior structure worth reporting, only an on/off effect. Even fully rescued, per-weight
(88.3) remains below plain layerwise (90.9) and blocks (91.4). Nothing in the zpool block
reaches 90 % at any r except layerwise r = 1, i.e. no pooling at all.

### What the 300-epoch budget does contain (all SGDm/Lion/layerwise unless noted, n = 2 per cell)

| arm | 300 ep | 100 ep | Δ(gain vs plain) |
|---|---|---|---|
| plain layerwise | 91.76 ± 0.11 | 90.92 ± 0.18 (n=24) | — |
| additive r = 0 | 92.06 ± 0.41 | 92.29 ± 0.12 (n=6) | +0.29 vs +1.37 |
| additive r = 0.05 | 93.02 ± 0.14 | 93.07 ± 0.11 (n=5) | +1.25 vs +2.14 |
| additive r = 0.1 | 93.31 ± 0.36 | 92.60 ± 0.16 (n=5) | +1.55 vs +1.68 |
| shrink λ=0.1 | 91.86 ± 0.08 | 92.32 ± 0.10 (n=12) | — |
| plain scalar (α₀=1e-3) | 88.32 ± 0.15 | 87.90 ± 0.19 (n=6) | — |

Every 300-epoch cell is **n = 2** and is therefore below the reporting bar. Read only as a
direction: the *absolute* additive gain shrinks with budget (plain layerwise catches up by
0.84 pp while the additive arms move ≤ 0.3 pp), and the r = 0.05 / r = 0.1 ordering flips.
Both movements are of the same size as the n = 2 spreads.

---

## (d) Model scale × granularity

### Inventory

| network | completed 100-epoch runs | granularities covered |
|---|---|---|
| ResNet10 | 9 | scalar (3), layerwise (3), layerwise+additive r=0.06 (3) |
| ResNet18 | 443 | all five |
| **ResNet34** | **0** | one scalar run truncated at 71/100 epochs; one 2-epoch smoke test |
| ResNet50 | 0 | one 2-epoch smoke test |
| ResNet101 | 0 | one 2-epoch smoke test |

### The `sc` scale block — the only protocol-matched contrast (guard-on, α₀=1e-6, SGDm/Lion, 100 ep)

| | ResNet10 | ResNet18 | ResNet34 |
|---|---|---|---|
| scalar | 70.73 ± 0.87 (n=3) | 87.96 ± 0.20 (n=3) | **no completed run** |
| layerwise | 90.83 ± 0.24 (n=3) | 90.77 ± 0.15 (n=3) | **no run** |
| resnet18_blocks | no run | 91.51 ± 0.14 (n=3) | **no run** |
| additive r=0.06 | 90.92 ± 0.42 (n=3) | 93.30 ± 0.15 (n=3) | **no run** |
| **layerwise − scalar** | **+20.10 pp** (t=38.8, p<0.001) | **+2.82 pp** (t=19.5, p<0.001) | — |
| **additive − layerwise** | **+0.08 pp** (p = 0.78) | **+2.53 pp** (t=20.7, p<0.001) | — |

### Reading

Two effects move in **opposite** directions with scale, over a single doubling of depth:

1. **The granularity benefit collapses as the model grows** — +20.1 pp at ResNet10, +2.8 pp at
   ResNet18. This is entirely driven by the *scalar* arm improving (70.7 → 88.0); the layerwise
   arm is flat across scale (90.83 vs 90.77). The parent paper's premise — that a single global
   step size is increasingly inadequate as models grow — is **contradicted in the direction of
   the effect** over this range: one global step size gets *better*, not worse, from ResNet10
   to ResNet18.
2. **The M1 additive pooling benefit grows with scale** — null at ResNet10 (+0.08 pp, p = 0.78),
   +2.53 pp at ResNet18.

The ResNet10 scalar failure is a genuine asymptote, not an instability: all three seeds rise to
~70 % by epoch 25 and stay flat to epoch 100 (max at epochs 80/90/94, within 0.2 pp of the
plateau). But with **two** model sizes, three seeds each, these are two-point trends. A
two-point "trend" cannot distinguish a monotone scale law from a ResNet10-specific pathology,
and ResNet34 — the run that would break the tie — does not exist.

---

## (e) CIFAR-100 vs CIFAR-10

**Nothing replicates, because nothing was run.**

| run | network | epochs | best test acc | test series |
|---|---|---|---|---|
| `c100smoke_layer` | ResNet18_c100 | 3/3 | 1.16 % | 1.10, 1.16, 1.14 |
| `c100smoke_probe` | ResNet18_c100 | 3/3 | 1.16 % | 1.10, 1.16, 1.14 (byte-identical to the above) |
| `c100disc-c100` | ResNet18_c100 | 5/5 | 20.99 % | 5.72, 9.84, 12.23, 14.93, 20.99 |

Three CIFAR-100 runs exist in the entire corpus; two are duplicates of one configuration. The
longest is 5 epochs. There is no CIFAR-100 arm at any granularity, no seed replication, and no
plateau. **INSUFFICIENT DATA — the cross-dataset question is completely open.**

---

## (f) α₀ × granularity — does the ordering change once the startup handicap is removed?

ResNet18 / CIFAR-10 / 100 epochs, guard-on. Plateau(last 5), mean ± sd, n.

| arm | α₀ = 1e-6 | α₀ = 1e-4 | α₀ = 1e-3 |
|---|---|---|---|
| SGDm/Lion scalar | 87.89 ± 0.16 (n=11) | 87.79 ± 0.32 (n=7) | 87.90 ± 0.19 (n=6) |
| SGDm/Lion blocks | 91.43 ± 0.17 (n=11) | (n=2) | (n=2) |
| SGDm/Lion layerwise | 90.91 ± 0.19 (n=20) | 90.93 ± 0.29 (n=7) | 91.33 ± 0.06 (n=5) |
| SGDm/Lion layerwise + additive r=0.06 | 93.30 ± 0.15 (n=3) | 92.70 ± 0.09 (n=5) | (n=2) |
| SGDm/Lion layerwise + shrink λ=0.1 | 92.32 ± 0.10 (n=12) | (n=2) | 92.26 ± 0.15 (n=3) |
| SGDm/Adam layerwise + shrink λ=0.1 | 91.94 ± 0.15 (n=6) | (n=2) | (n=1) |
| AdamW/Adam scalar | 91.63 ± 0.15 (n=3) | 91.83 ± 0.10 (n=3) | **92.71 ± 0.08 (n=3)** |
| AdamW/Adam blocks | 91.77 ± 0.18 (n=3) | 91.68 ± 0.14 (n=3) | 92.03 ± 0.10 (n=3) |
| AdamW/Adam layerwise | 91.78 ± 0.16 (n=3) | 91.95 ± 0.10 (n=3) | **90.82 ± 0.18 (n=3)** |

### Does the ordering change?

**Under SGDm: no. The startup handicap is not the explanation for the scalar deficit.**

| α₀ | scalar | layerwise − scalar | test |
|---|---|---|---|
| 1e-6 | 87.89 (n=11) | **+3.02 pp** | t = 47.0, p < 0.001 |
| 1e-4 | 87.79 (n=7) | **+3.15 pp** | t = 19.2, p < 0.001 |
| 1e-3 | 87.90 (n=6) | **+3.43 pp** | t = 41.5, p < 0.001 |

Raising α₀ by three orders of magnitude moves the SGDm scalar plateau by 0.11 pp
(87.79 → 87.90, i.e. nothing) and *widens* the granularity gap slightly. Whatever limits the
scalar arm under SGDm, it is not the initialisation of the step size. It is an asymptote.

**Under AdamW: yes, the ordering inverts.** At α₀ = 1e-6 and 1e-4 the three granularities are
within ±0.2 pp of each other. At α₀ = 1e-3 scalar becomes the *best* arm and layerwise the
worst by 1.89 pp (t = −16.3, p = 0.001). The AdamW "null" is only null at small α₀; at the α₀
where AdamW performs best, granularity is actively harmful.

**Speed does respond to α₀** even where the plateau does not — SGDm/Lion layerwise reaches
88 % at epoch 36.0 (α₀=1e-6), 27.4 (1e-4), 23.0 (1e-3), and 90 % at 55.9 / 47.6 / 40.2.
The startup handicap is real for *time-to-target* and absent for *asymptote*. Any table that
mixes the two metrics will read these as one effect.

---

## (g) The non-meta baseline

ResNet18 / CIFAR-10 / 100 epochs / batch 100 / `AUGMENT=1` — identical data pipeline to every
meta-learned arm. Verified from the `ARGS:` and `ENV:` lines of the raw files.

### `fx_adamw_*` — plain AdamW, constant learning rate, no meta-learning

| lr | n | plateau | ep→90 | ep→91 |
|---|---|---|---|---|
| 1e-3 | 2 | 90.21 ± 0.09 | — (n<3) | — |
| **3e-4** | **5** | **91.85 ± 0.21** | 31.6 ± 1.1 | 41.2 ± 3.8 |
| 1e-4 | 5 | 91.34 ± 0.31 | 46.4 ± 7.2 | 66.4 ± 3.4 |
| 3e-3 | 2 | 85.83 ± 1.54 | — (n<3) | — |

### `fxcos_*` — plain AdamW + cosine schedule + warmup, no meta-learning

| lr | n | plateau | ep→90 | ep→91 |
|---|---|---|---|---|
| **1e-3** | **3** | **94.24 ± 0.08** | **21.3 ± 3.8** | **31.0 ± 3.0** |
| 3e-4 | 3 | 94.16 ± 0.06 | 25.3 ± 1.2 | 28.7 ± 0.6 |
| 1e-4 | 3 | 92.92 ± 0.26 | 32.3 ± 0.6 | 44.3 ± 2.5 |

### Head-to-head

| comparison | Δ | test |
|---|---|---|
| best meta arm (additive r=0.07, 93.23 ± 0.16, n=8) vs **AdamW+cosine** (94.24 ± 0.08, n=3) | **−1.01 pp** | t = −13.9, p < 0.001 |
| best meta arm (additive r=0.06, 93.30 ± 0.15, n=3) vs **AdamW+cosine** | **−0.94 pp** | t = −9.8, p = 0.002 |
| best meta arm (additive r=0.07) vs AdamW constant lr=3e-4 | +1.38 pp | t = 12.9, p < 0.001 |
| best *plain-granularity* meta arm (nodewise, 91.74 ± 0.14, n=8) vs AdamW constant lr=3e-4 | −0.11 pp | t = −1.06, **p = 0.33 (null)** |
| best plain-granularity meta arm vs AdamW+cosine | −2.50 pp | t = −37.4, p < 0.001 |

**This is the most consequential number in the corpus.** The entire hierarchical
meta-optimisation apparatus, at its best configuration and after ~600 runs of tuning, lands
0.94–1.01 pp *below* a three-line AdamW + cosine baseline, and reaches 91 % ten epochs later
(41 vs 31). Against constant-lr AdamW the picture is kinder — the pooled arm wins by 1.38 pp —
but every *plain* granularity arm, including the best one, is statistically tied with or below
constant-lr AdamW. Only the additive-pooled arm beats the weaker baseline at all.

Caveat, stated in both directions: the meta arms are SGDm-based with momentum 0.99 and weight
decay 0.1, the baselines are AdamW with library defaults; and the cosine baseline gets a
hand-designed schedule that the meta-learner is nominally supposed to replace. That is exactly
the comparison that matters — the claim of the method is that it removes the need for that
schedule, and here it does not match it.

---

## STEP 3 — Verdicts on previously-claimed results

### Claim 1: "granularity helps under SGDm and is null under AdamW"

**CONFIRMED as stated, but the framing is misleading.**

Under SGDm/Lion/α₀=1e-6: blocks +3.52 pp (n=17 vs 17), layerwise +3.03 pp (n=24 vs 17),
nodewise +3.85 pp (n=8 vs 17) over scalar, all p < 0.001. Under AdamW/Lion/α₀=1e-6:
blocks −0.26 pp (p = 0.34), layerwise −0.11 pp (p = 0.51), n = 3 each. Under
AdamW/Adam/α₀=1e-6: +0.12 pp (p = 0.15) and +0.20 pp (p = 0.02), n = 6 each. The
interaction is +3.13 ± 0.15 pp (layerwise) and +3.78 ± 0.23 pp (blocks) — far outside noise.

Three qualifications the existing framing omits:
- **It is a ceiling artefact.** AdamW/scalar (91.62) already equals SGDm's best plain
  granularity (nodewise 91.74, +0.12 pp apart). Granularity closes a gap; it does not open one.
- **"Null" is only true at low α₀.** At α₀ = 1e-3, AdamW layerwise is 1.89 pp *worse* than
  AdamW scalar (p = 0.001). The effect is null-to-negative, not null.
- **The AdamW side rests on n = 3–6 per cell** against n = 17–24 on the SGDm side.

### Claim 2: "M1 additive has an interior optimum near r = 0.05–0.07"

**CONFIRMED.** Peak 93.30 ± 0.15 (n=3) at r = 0.06 / 93.23 ± 0.16 (n=8) at r = 0.07, against
92.29 ± 0.12 (n=6) at the r = 0 endpoint and 90.97 ± 0.13 (n=3) at the r = 1 endpoint. The peak
beats r = 0 by +1.014 ± 0.097 pp (p = 0.001) and r = 1 by +2.331 ± 0.112 pp (p < 0.001) — ten
and twenty-one standard errors. The r = 1 endpoint reproduces plain layerwise to 0.05 pp
(p = 0.59), so the parameterisation is verified at the boundary. The optimum is flat over
[0.05, 0.07] (r=0.06 vs r=0.07: p = 0.53) and the r = 0.07 cell replicates across two
independent run families on two cluster accounts. This is the best-supported result in the
corpus.

### Claim 3: "pooling gains invert between 100 and 300 epochs"

**INSUFFICIENT DATA.**

For zpool, the comparison is impossible: **zero zpool runs exist at 300 epochs.** For M1
additive, all three 300-epoch cells are **n = 2**, below the reporting bar. What those n = 2
cells show is (i) an ordering flip between r = 0.05 and r = 0.1 (100 ep: 93.07 > 92.60;
300 ep: 93.02 < 93.31) whose size (0.3–0.7 pp) is comparable to the n = 2 spreads
(sd 0.14 and 0.36), and (ii) a *shrinking* absolute gain rather than an inverting one — plain
layerwise gains 0.84 pp from the longer budget while additive r = 0.05 gains 0. An inversion
would require additive to fall below plain; it does not, at either budget, at any sampled r.

### Claim 4: "per-weight fails by ~12 pp even with the SwiftTD guard"

**CONFIRMED**, with the reference point made explicit.

Guard-on per-weight, SGDm/Lion/α₀=1e-6/100 ep: **79.11 ± 0.39 (n=6)**.

| reference | Δ |
|---|---|
| vs nodewise (91.74, n=8) | **−12.63 pp** (t = −75.4, p < 0.001) |
| vs resnet18_blocks (91.41, n=17) | **−12.31 pp** (t = −74.3, p < 0.001) |
| vs layerwise (90.92, n=24) | **−11.81 pp** (t = −71.9, p < 0.001) |
| vs scalar (87.89, n=17) | −8.79 pp (t = −53.7, p < 0.001) |

"~12 pp" is accurate against every coarser *structured* granularity and understates nothing.
Two additions the claim should carry: **without** the guard the failure is not 12 pp but total —
10/10 unguarded runs finish at exactly 10.00 % (chance), so the guard converts a catastrophe
into a merely bad result; and per-weight is **partially rescuable** — zpool lifts it to
88.26 ± 0.15 (n=6, r=0.7), a +9.15 pp recovery that still leaves it 2.7 pp below plain
layerwise. Per-weight's failure is therefore a variance/estimation problem that pooling
attacks successfully but does not solve.

---

## STEP 4 — The three most valuable experiments not yet run

### 1. M1 additive pooling on top of AdamW (and on top of the cosine baseline)

**Why.** Every result in this project has one shape: granularity compensates for SGDm and does
nothing for AdamW, while *pooling* is the only intervention that produces headroom rather than
recovery (+2.4 pp over plain layerwise, and the only meta arm to beat constant-lr AdamW).
Pooling has been tested on exactly one base optimiser. The two mechanisms are logically
independent — granularity is about *which* step sizes exist, pooling is about *how their
meta-gradients are estimated* — yet no run separates them. The critical unknown is whether
additive pooling's +2.4 pp is a genuine estimation improvement (in which case it should
transfer to AdamW and close the 1.01 pp gap to the cosine baseline) or is simply repairing
noise that only SGDm's meta-gradients suffer from (in which case it will be null on AdamW,
exactly as granularity is, and the method has no result).

**Design.** AdamW base × {scalar, layerwise} × additive r ∈ {0, 0.03, 0.07, 0.3, 1} × α₀ ∈
{1e-6, 1e-3} × 5 seeds, 100 epochs, guard-on, meta = Lion and Adam. Plus the same additive
sweep layered on the cosine schedule. ≈ 100 runs. This is the experiment that decides whether
there is a paper.

### 2. A real scale ladder: ResNet34 and ResNet50 at 100 epochs, all three arms

**Why.** Section (d) is the project's only test of the parent paper's central premise and it
currently rests on **two** model sizes. It reports two opposite trends — granularity benefit
falling 20.1 → 2.8 pp, additive benefit rising 0.08 → 2.53 pp — from three points each, with
ResNet34 consisting of one run truncated at epoch 71. Both "trends" are lines through two
points. Worse, the direction of the first one contradicts the premise being tested (scalar gets
*better* with scale, 70.7 → 88.0), so a third point does not merely tighten an estimate — it
decides whether the headline is "granularity matters less as models grow" or "ResNet10 has a
pathology that has nothing to do with scale."

**Design.** {ResNet34, ResNet50} × {scalar, layerwise, layerwise+additive r=0.07} × 5 seeds,
100 epochs, α₀ = 1e-6, guard-on, identical `sc`-block protocol so the ResNet10/18 cells remain
comparable without re-running them. 30 runs. Re-run the three ResNet10 arms with 5 seeds to
match. Budget the wall-clock: ResNet50 at 100 epochs is the only expensive part of this project.

### 3. CIFAR-100 replication of the four arms that survived this audit

**Why.** Every number in this document is a single dataset. Three of the four surviving results
— the SGDm/AdamW interaction, the r ≈ 0.06 optimum, and the per-weight −12 pp — are quantitative
claims about how step-size estimation interacts with a loss surface, and none of them has been
shown to be a property of anything other than CIFAR-10/ResNet18. The corpus currently contains
three CIFAR-100 runs of ≤ 5 epochs, two of which are duplicates. This is not a robustness
nicety: the M1 interior optimum at a specific r ≈ 0.06 is precisely the kind of tuned constant
that fails to transfer, and if it does not transfer, "there is an interior optimum" survives as
a claim but "it is near 0.06" does not.

**Design.** CIFAR-100 × {SGDm, AdamW} × {scalar, layerwise, layerwise+additive r ∈ {0, 0.07, 1}}
× 5 seeds × 100 epochs, α₀ = 1e-6, guard-on. 60 runs. Include the AdamW+cosine baseline at
3 learning rates × 3 seeds — without it, a CIFAR-100 table repeats this corpus's main
methodological failure, which was running 600 meta-learning configurations before running the
baseline that beats all of them.

---

## Appendix: reporting rules applied

1. Primary metric is **plateau = mean test accuracy over the final 5 epochs**. `best_test` is
   never used for a comparison (it inflates by 0.27 pp, larger than several reported effects).
2. Secondary metric is **epochs to first reach a target**, always with `[reached/total]`
   censoring shown. Where an arm's plateau sits near the target, the crossing epoch measures
   noise, not speed, and ep→91 is reported alongside ep→90 for that reason.
3. Runs that did not complete their requested budget are excluded — they have no plateau.
4. Superseded resubmissions (3) excluded.
5. **The SwiftTD guard is a blocking factor**, stratified everywhere and pooled only for
   granularities where it was verified inert (|Δ| ≤ 0.10 pp, p ≥ 0.24).
6. `n < 3` cells are printed as `(n=k)` with no mean, and never enter a contrast.
7. All tests are Welch two-sample t-tests (unequal variance). Interaction standard errors are
   the root-sum-square of the four cell standard errors.
8. An effect is called real only if it exceeds ~2× its own combined standard error; anything
   else is labelled inside noise regardless of its p-value.
9. Legacy `--optimizer HF` pilot runs with no recorded meta-optimiser (17 runs, plateaus
   spanning 65–92 for nominally identical arms) are excluded from all result tables.
