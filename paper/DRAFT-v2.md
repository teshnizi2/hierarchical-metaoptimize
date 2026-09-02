# The partition, not the count: a count-matched measurement of step-size granularity in online meta-gradient optimisation — and eight mechanisms it is not

**Draft v2.** Every number in this document was re-derived from `results/all_runs.csv` and from the
raw per-epoch `.out` series at the time of writing, under the admissibility gate
`window_ok == 1 AND complete == 1 AND plateau5 present`. Where a registered scorer exists for a
batch it was run **unedited** and its output quoted. Numbers that failed to reproduce from the
project's internal record are listed in **Appendix A**, not silently corrected.

---

## Abstract

MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) meta-learns one step size per
parameter group and closes by observing that finer partitions help inconsistently: *"while
increasing the number of step sizes is anticipated to enhance performance, our experimental
findings in Section 7 reveal that this improvement is not consistent across the MetaOptimize
approximations evaluated."* We take that question up with 2,113 runs (≈1,582 GPU-hours; 1,671
admissible) on ResNet-10/18/34/50 and CIFAR-10/100, and report one robust measurement, one clean
refutation, and a mechanism we could not find.

**The measurement.** Replacing an architecture-aligned partition (one step size per output
channel, `nodewise`) by a uniform one of the *same group count* (fixed-size chunks of K weights)
is worth a positive amount of final accuracy in **every one of 17 within-batch, count-matched
cells we measured**, spanning four network variants
(ResNet-18, ResNet-18 with GroupNorm, ResNet-34, ResNet-50), 2 datasets, 4 base optimisers,
2 meta-stepsizes, 2 budgets and 2 normalisation schemes. On ResNet-18/CIFAR-10 with an SGDm base the effect
D = +0.456 ± 0.142 to +0.727 ± 0.200 pp across **six independent batches**; on ResNet-34 D = +0.666 ±
0.094 (9 v 9); on ResNet-50 D = +0.881 ± 0.261; on CIFAR-100 D = +1.640 ± 0.245 and +1.485 ±
0.238. Over the twelve cells sharing a byte-identical contrast the fixed-effect pool is +0.546
with **Q = 43.2 on 11 df, p = 1.0e-5** — D varies genuinely across configurations
(τ = 0.215 pp against 0.151 pp rms measurement error), not just noisily.

**The refutation.** Architecture *alignment* is not the carrier. Permuting **which** weights share
a group while holding the group count **and the exact per-tensor group-size multiset** fixed is
worth **−0.009 ± 0.157 pp (t −0.06)**, against a pre-registered symmetric band. What is left is the
group-**size distribution**; alignment as such does nothing.

**What we could not find.** We report eight candidate mechanisms that died, because they are half
the contribution. Chief among them: the obvious carrier — degenerate size-1 groups — is not it
(removing 100% of a network's singletons buys +0.115 ± 0.133 pp, t 0.87); the tail story is
base-specific (D − G = +0.715 ± 0.248 under SGDm, +0.047 ± 0.124 under AdamW); no summary
statistic of the size distribution is *identifiable* from this corpus, because at fixed count the
design contains exactly one contrast type and every candidate collapses to an indicator for the
aligned arm; and **no measurable property of a configuration predicts D out of sample** better
than the corpus mean by a margin that survives the power bound (|r| ≥ 0.602 needed at 11 design
points).

**Scope, stated here and not deferred to a threats section.** (i) Everything is CIFAR-resolution
vision with ResNets and one meta-learning framework; ImageNet is out of reach on our data
allocation (489 of 1000 train classes present, validation set unlabelled). (ii) The best
MetaOptimize cell in the corpus reaches 93.317 ± 0.083 pp against a tuned SGD+cosine baseline at
95.124 ± 0.047 (n=5, the interior maximum of a bracketed grid) — a **1.807 pp deficit**. We make
no competitiveness claim. (iii) All 367 partition-programme runs use a **Lion** meta-optimiser;
the base optimiser has been varied four ways, the meta-optimiser never. (iv) The effect is
≈0.6 pp inside a method that is 1.8 pp behind a cosine schedule. (v) We inherit, and partly
overlap with, Choi et al. on tuning-protocol sensitivity, Zheng & Kwok on blockwise adaptivity,
and CAM-HD on the granularity ladder and its interior optimum; §2 states exactly what is left.

---

## 1. Introduction

Adaptive-step-size methods that *learn* their step sizes online — IDBD, Autostep, hypergradient
descent, SwiftTD, MetaOptimize — all face a design choice that is usually made silently: how many
weights share one step size. Call this the **granularity** of the partition. The choice ranges from
one global step size (m = 1) to one per weight (m = P), and every method in the family exposes it,
but almost none of them study it.

MetaOptimize exposes the choice and flags it as unresolved. Its §7.1 CIFAR-10 experiment uses two
granularities, scalar (m = 1) and a "blockwise" partition of six blocks — *"one for each linear
layer and four blocks for the ResNet modules"*; §7.2's non-stationary experiment uses a
"blockwise" of **two**. So the paper runs exactly two granularity values anywhere, and the value of
its coarse arm differs between experiments. Its §7.3 ImageNet aside reports *"Unlike CIFAR10, here
the blockwise versions of MetaOptimize showed no improvement over the scalar versions"*, and its
Limitations section asks for future work on *"the layer and weight levels"*.

That is an unusually clean open question, and the obvious way to answer it is to build the ladder
and read off the shape. We did that, and the shape is not the answer — because "the number of step
sizes" is not one experimental variable. Along the way we found that:

* moving the shared meta-stepsize η by one decade moves the measured layerwise-minus-scalar gap
  from **+3.291 ± 0.146 pp** (η = 1e-3, the paper's own default) to **+0.655 ± 0.176 pp**
  (η = 1e-4), within one batch at fixed seeds — so four fifths of the reported granularity benefit
  at the default η is tolerance to an over-large meta-step, not accuracy (§4.1);
* the initial step size α₀ sets the *sign* of the ordering at the parent's own configuration
  (§4.1);
* the group count, holding the partition *family* fixed, is a smooth function of log m whose local
  slope runs from **+0.350 to +0.828 pp/decade** inside a single batch, so no single "count slope"
  exists to import (§4.2);
* and — this is the paper — **at fixed group count the partition still matters**, by an amount
  larger than the count effect it is usually confused with (§4.3).

The last of these is the measurement we can defend. The rest of the paper is about how far it
generalises (§4.4–§4.8), what it is *not* (§5), and what we could not measure (§6–§7).

**We do not have a mechanism.** We think that is worth saying in the first section rather than the
last. The result is robust — 17 cells, every one positive, four network variants, two datasets, four
base optimisers — and eight separate candidate explanations for it are dead, six of them killed by
tests we registered in advance and one killed by a reviewer after it had passed its own
cross-validation. A cross-validated *null* at n = 11 is defensible in a way a cross-validated
success at n = 11 never is; we report both, and the null is the one that survives.

### 1.1 Contributions

1. **A count-matched isolation of the group-size distribution from the group count** in
   meta-learned step sizes, replicated in 17 within-batch cells across four network variants, 2 datasets
   and 4 base optimisers (§4.3–§4.5, Table 2).
2. **A pre-registered permutation null** showing architecture alignment is not the carrier:
   −0.009 ± 0.157 pp at fixed count *and* fixed per-tensor size multiset (§4.6).
3. **A ranking of the four variables** that "the number of step sizes" conflates, with the
   within-batch magnitude of each (§4.1–§4.2).
4. **Eight dead mechanisms and two nulls**, reported as a section rather than an appendix (§5),
   including the identifiability limit that makes the ninth unanswerable from this corpus.
5. **A practitioner prescription with its scope attached**: merging each one-dimensional tensor
   into a single group is worth **+0.337 ± 0.069 to +1.363 ± 0.151 pp** across ten within-batch
   cells under SGDm, SGD and RMSProp bases, and costs nothing — but under an AdamW base it is
   worth +0.091 ± 0.078, i.e. nothing measurable (§4.7, §5.4).
6. **A measurement-discipline appendix** documenting a batch that failed silently on its own axis,
   a metric column that produced two withdrawn headlines, and an internal variance claim that did
   not reproduce (§6, Appendix A).

---

## 2. Related work, and what is left

### 2.1 MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, arXiv:2402.02342)

The parent method learns `α = exp(β)` per group from a discounted meta-gradient carried by an
eligibility trace `h`. Its configuration, extracted from the released text rather than recalled:
ResNet-18, CIFAR-10, batch size 100; (base, meta) ∈ {(AdamW, Adam), (Lion, Lion), (RMSProp, Adam),
(SGDm, Adam)}; η = 1e-3 for every MetaOptimize row; α₀ = 1e-6; γ = 1; blockwise = six blocks.
§7.5 states that η *"works universally well… with no sweeping required"*.

Three points matter for what follows and are easy to get wrong.

* **§7.1 makes no blockwise-beats-scalar claim in its own text.** Its stated CIFAR-10 finding is
  *"In every tested combination, MetaOptimize outperforms its corresponding fixed-step-size
  baseline"* — the method against a tuned fixed LR. The positive granularity reading rests on the
  §7.3 aside and one figure.
* **§7.1 states no seed count and shows no error bars.** `grep -icE "error bar|shaded|standard
  deviation|confidence interval"` over the full text returns 0; the only "averaged over 5 random
  seeds" sentence belongs to §7.2. So the curves supporting the granularity inference are of
  unstated replication.
* **The §9 sentence is indexed by approximation**, verbatim: *"this improvement is not consistent
  **across the MetaOptimize approximations evaluated**."* It is not a claim that an
  accuracy-versus-m curve turns down; no such curve was measured. Any paper claiming to *explain a
  reported non-monotonicity of the granularity curve* is answering a sentence that does not exist.
  We do not make that claim.

We also record that six blocks on a ResNet-18 have sizes **[1856, 147968, 525568, 2099712,
8393728, 5130]** weights: the parent's coarse arm **cannot contain a size-1 group**, so no
degenerate-group story can be about the parent's own experiment.

### 2.2 Choi et al., *On Empirical Comparisons of Optimizers for Deep Learning* (arXiv:1910.05446)

Choi et al. show that optimiser rankings are set by the hyperparameter tuning protocol, and that
where an **inclusion relationship** holds — optimiser A's hyperparameter space contains a setting
that reproduces B — the more general optimiser never underperforms once tuned. This pre-empts a
large part of our §4.1: our layerwise-minus-scalar gap moving from +3.291 to +0.655 pp when both
arms are tuned is exactly their phenomenon, and we say so.

It does **not** pre-empt §4.3, and the reason is structural rather than empirical. Granularity is
not an inclusion relationship in Choi's sense. The finer partition's extra degrees of freedom are
**state** (the per-group β), not hyperparameters. In the released reduction, the coarse partition's
meta-gradient is a *raw sum* over its members' meta-gradients with no per-group normalisation
(`block_product`, `patches/HF_patched.py:161-172`: `scalar` returns
`[sum((u*v).sum() for all tensors)]`; `layerwise` returns the per-tensor sums), so a coarse group
is not obtainable from a fine partition by tying anything the search space exposes. The single
hyperparameter setting at which every granularity coincides is η = 0, where β never moves and all
arms degenerate to a fixed step size. So the inclusion holds only at a point where the method is
switched off. That is why a granularity comparison can be non-monotone *at each arm's own optimum*,
and §4.5 shows that it is: tuning each arm to its own argmax moves D by −0.090 ± 0.178 pp.

### 2.3 Zheng & Kwok, *Blockwise Adaptivity* (arXiv:1905.09899)

Zheng & Kwok partition network parameters into blocks and make the **second-moment normaliser**
blockwise rather than coordinate-wise, arguing theoretically for comparable convergence and better
uniform stability, and reporting lower test error than Adam on CIFAR-10 ResNet-56/110 for all four
of their block constructions. Those constructions are: per parameter tensor/matrix/vector; per
output dimension/output channel; per convolution kernel; and per input dimension with a **single
stepsize per parameter vector**. The last of these is, structurally, the prescription we arrive at
independently in §4.7 — a whole 1-D tensor gets one group.

Two things separate their work from ours, and one caveat is ours to declare. They adapt a
second-moment *preconditioner*, not a meta-learned step size, so the object being grouped is
different. And their four schemes vary group **count** and group-size **distribution**
simultaneously, so their ranking of block constructions cannot separate the two — which is the
confound the present paper exists to remove. The caveat: the markdown rendering of the paper we
hold locally collapses every scheme label to the same token, so **we cannot identify from our copy
which of their four schemes they report as best**, and we make no claim about their ranking beyond
"all four beat Adam".

### 2.4 CAM-HD — Jie, Gao, Vasnev & Tran, *Adaptive Multi-level Hyper-gradient Descent* (arXiv:2008.07277)

This is the closest prior work and it must be cited in the first paragraph of any granularity
claim. Working in the hypergradient-descent framework, CAM-HD extends learning-rate adaptation to
**layer-wise, unit-wise and parameter-wise** levels, and:

* **states the small-sample mechanism, in words, four years before us**: *"For the model involving
  a large number of learning rates for different groups of parameters, the updating for each
  learning rate only depends on the average of a small number of examples. Therefore, when the
  batch size is also not large, over-parameterization is an issue to be concerned."*
* **reports the interior optimum explicitly**: *"usually the optimal performance is neither at full
  global level nor full layer/filter level, but a weighted combination of two levels of adaptive
  learning rates."*
* **fixes it with the classically correct remedy**: a learned weighted combination of levels, i.e.
  hierarchical partial pooling / shrinkage, with the combination weights themselves trained.

What is not in CAM-HD, and is therefore ours: degenerate and size-1 groups, and one-dimensional
tensors as a distinguished object; the decomposition of the granularity contrast into a
**size-distribution** part and an **alignment** part, with the alignment null; and **count
matching** — CAM-HD's levels differ in group count and in size distribution simultaneously, so its
interior optimum is exactly the confound we remove.

CAM-HD also frames the referee question we owe an answer to: *the classical remedy for noisy small
groups is shrinkage, and CAM-HD already published partial pooling for this. Why a hard rule rather
than the soft, classically optimal version?* We answer it with data in §5.9: three pooling
operators were implemented and all three failed their own controls. In particular, full pooling in
meta-gradient space (`zpool`, r = 0) lands at **87.880 ± 0.070 (n=5)**, which is
**87.879 ± 0.046 (n=12)** — plain scalar — to one part in a thousand, confirming the operator does
what it says; and at the good partition it is monotone harmful, r = 1 → 91.037 ± 0.079 versus
r = 0 → 87.880 (−3.157 pp). The best interior cell we can see on layerwise is r = 0.99 at 91.112
(n=1), +0.075 pp over no pooling and well inside seed noise. Pooling *does* rescue an
over-fine partition — weightwise goes 79.235 ± 0.154 (r=1) to 89.272 ± 0.162 (r=0.99), a +10.04 pp
rescue — but the rescued arm is still **2.18 pp below plain six-block (91.448 ± 0.049)** and
2.47 pp below plain nodewise. Shrinkage repairs a bad partition; it does not beat a good one.

### 2.5 Methods that ship a tensor-level rule and do not justify it

| method | what it does to 1-D tensors | stated reason |
|---|---|---|
| **Adam-mini** (arXiv:2406.16793) | Algorithm 3, *Partition for non-Transformers*, is verbatim `for name, param in parameters: param_blocks[name] = param` — **one block per tensor**. On a ResNet, Adam-mini is layerwise and already ships our prescription. | Its stated principle is Hessian sub-block **alignment** — which our permutation null (§4.6) refutes as the carrier in this regime. |
| **Adalayer** (Zhao et al., arXiv:2407.07972) | LayerNorm parameters form whole-tensor blocks. | Concludes that adaptivity **on** the last layer and LayerNorm is *necessary*. Note the direction: this is about **merging across** norm tensors versus **shattering within** one, and about a second-moment preconditioner, not a meta-learned step size. It is not evidence for or against our contrast; we flag it because a careless reading makes it look like both. |
| **Muon** | 1-D parameters, embeddings and the head are routed to AdamW. | Tensor **rank**, from the geometry of Newton–Schulz orthogonalisation. |
| **LARS / LAMB** (arXiv:1708.03888) | BatchNorm and bias parameters conventionally exempted from the layer-wise trust ratio. | Folklore: tiny norms, unstable ratio. |
| **bitsandbytes** (arXiv:2110.02861) | Tensors with < 4096 elements kept at 32-bit. | Precision, not grouping. |
| **Shampoo** | `max_preconditioner_dim` is a cap from *above*; 1-D parameters get diagonal Adam. | Cubic preconditioner cost — the opposite direction. |
| **Adafactor** | `min_dim_size_to_factor` falls back to full per-coordinate second moments below a threshold. | Memory — again the opposite direction. |

No method in this survey imposes a **minimum group size** on step sizes; two impose a maximum. Our
§4.7 supplies the first count-matched measurement of what such a floor buys, and §5.4 supplies its
scope limit.

**An attribution we withdraw.** An earlier version of this project attributed a
√N noise-averaging argument for coarse grouping to Adam-mini, Adalayer and SGG. Reading all three
in full, that attribution is wrong and is withdrawn: Adam-mini's non-Transformer partition is
per-tensor and its stated principle is Hessian block structure, and Adalayer's conclusion runs the
other way. We record the withdrawal because the misattribution was ours.

---

## 3. Method and experimental setup

### 3.1 The partitions

All partitions are defined over the network's `named_parameters()` list and are constructed, not
assumed; every count below is re-derived analytically and cross-checked against the optimiser's own
allocated `beta` on the cluster.

**Table 1 — the partitions, on ResNet-18 (62 tensors, 11,173,962 weights).**

| arm | rule | ResNet-18: m | min group | size-1 groups | size CV |
|---|---|---|---|---|---|
| `scalar` | one group | 1 | 11,173,962 | 0 | — |
| `resnet18_blocks` | the parent's six blocks | 6 | 1,856 | 0 | — |
| `layerwise` | one per tensor | 62 | 10 | 0 | — |
| `nodewise` | one per output channel / row | **14,420** | **1** | **9,610 (66.64%)** | **1.916** |
| `permnode` | nodewise's exact per-tensor size multiset, membership randomised **within each tensor** | 14,420 | 1 | 9,610 | 1.916 |
| `chunk777` | uniform chunks of K = 777 weights | **14,421** | 10 | 0 | 0.045 |
| `nodewise1d` | one per output channel, but **each 1-D tensor is one group** | **4,851** | 10 | 0 | 0.756 |
| `chunk2325` | uniform chunks of K = 2325 | **4,851** | 10 | 0 | 0.088 |
| `weightwise` | one per weight | 11,173,962 | 1 | all | 0 |

ResNet-18 has 62 parameter tensors and 11,173,962 weights, of which **41 tensors are
one-dimensional** — every BatchNorm scale and shift plus the classifier bias — totalling **9,610
weights = 0.0860% of the network**. `nodewise` gives each of those 9,610 weights its own step size;
that is where two thirds of its groups live, over less than a thousandth of its parameters.

### 3.2 The contrasts

Four differences, all **within batch**, all **count-matched by construction**:

* **D = chunk777 − nodewise** (m = 14,421 vs 14,420 — one group apart, 0.00003 decades). Uniform
  versus architecture-aligned at matched count. *The primary.*
* **G = chunk2325 − nodewise1d** (m = 4,851 **exactly**, on ResNet-18 and ResNet-18/CIFAR-100 within
  2 groups). The same contrast with the size-1 tail **already removed from both arms**. `D − G` is
  therefore the tail's contribution, and carries no cross-batch floor.
* **A = permnode − nodewise** (m = 14,420, identical per-tensor size multiset). The alignment leg.
* **U = chunk2325 − chunk777** (0.4732 decades of count, partition family fixed). The pure count
  axis.
* **T = nodewise1d − nodewise** (the practitioner's move: merge the 1-D tensors). Count-confounded
  by construction: `T = (D − G) + U`.

On ResNet-34, ResNet-50 and ResNet-18/CIFAR-100 the count matching is close but not exact:
chunk835 25,562 vs nodewise 25,556 (R34); chunk295 79,796 vs 79,700 and chunk884 26,715 vs 26,677
(R50); chunk771 14,595 vs 14,600 and chunk2293 4,943 vs 4,941 (C100). The largest mismatch,
0.14% of the count, is 685× below the resolution floor at the measured count slope.

**A structural caveat specific to ResNet-50.** Its largest 1-D tensor has 2,048 elements, which
exceeds K = 295, so `chunk295` **splits** some 1-D tensors across groups instead of giving each one
a single group. It still contains no size-1 group (min group size 10). ResNet-18, ResNet-34 and
ResNet-18/CIFAR-100 all have largest 1-D tensor 512 < K, so their chunk arms give each 1-D tensor
exactly one group. The ResNet-50 D is therefore a slightly different object and is reported as
such.

### 3.3 Metric, admissibility, and units of replication

**Metric.** `plateau5`, the mean test accuracy over the last 5 epochs of the requested budget, is
the primary throughout. The 20-epoch analogue is present in the corpus and is **not used**: two of
this project's headlines were withdrawn for quoting it (Appendix A.2).

**Admissibility.** A run enters an analysis only if `window_ok == 1 AND complete == 1` and it
carries a readable `plateau5`. The second condition is not redundant: **17 of 2,113 runs pass
`window_ok` while having completed under 90% of their requested epochs**, and one of them
(29 of 100 epochs, `plateau5` 85.228) sits inside a primary arm, where including it moves that
arm's mean by 1.22 pp and inflates its sem 19-fold. Of 2,113 rows, 1,671 are admissible.

**Box occupancy.** β is clipped to a box, and a run at a guard is uninterpretable. Occupancy is read
**per coordinate and per seed**, never from a per-tensor summary — reading the 62-element summary
instead reported 0.000000 occupancy on 24 runs that were clipped in every record and inverted an
arm ranking, which voided one batch (`ar1`, excluded from every primary here). The scorers report
`rec_lo`/`rec_hi` per run; all `cc1`, `mm1`, `pp1` and `bn1` arms read 0.0000 on both guards.

**Unit of replication.** Every primary contrast is taken **within one batch** (one contiguous
submission), so any offset shared by the two arms cancels identically. §6 reports what we can and
cannot say about the size of such offsets.

### 3.4 Registration discipline

Where a batch has a scorer committed before its runs existed, that scorer is run **unedited** and
its printed verdict is quoted rather than paraphrased. This rule exists because it was broken: two
cycle-91/92 headlines were withdrawn after being produced by reductions hand-written at read time
(Appendix A.2). The scorers used here are `analysis/c76_mm1_score.py`, `c77_pp1_score.py`,
`c78_bn1_score.py`, `c81_cc1_score.py`, `c82_fa1_score.py`, `c83_gc1_score.py`,
`c87_rl3_score.py`, and `c88_scorers.py` (committed at `5129e74`, before any `ub9`/`aw1` run
existed; md5 `0363bcccb4d3bbad50beb19c9281b9be`).

---

## 4. Results

### 4.1 The meta-stepsize and the initial step size each move the granularity gap by more than the gap

**Meta-stepsize.** Within one batch (`ms`), at fixed seeds, ResNet-18/CIFAR-10, SGDm base + Lion
meta, α₀ = 1e-3:

| η | layerwise | scalar | layerwise − scalar |
|---|---|---|---|
| 1e-3 (the parent's default) | 91.259 ± 0.076 (n=3) | 87.967 ± 0.124 (n=3) | **+3.291 ± 0.146, t 22.6** |
| 1e-4 (both arms' bracketed optimum) | 92.960 ± 0.024 (n=3) | 92.305 ± 0.174 (n=3) | **+0.655 ± 0.176, t 3.72** |

Both arms are **better** at η = 1e-4 than at η = 1e-3 — scalar by 4.338 pp, layerwise by 1.701 pp.
The granularity gap at the default η is therefore mostly the scalar arm's greater sensitivity to an
over-large meta-step. This is Choi et al.'s tuning-protocol effect, in the specific place where the
parent's protocol fixes η and states that no sweeping is needed.

**Initial step size.** At the parent's own (AdamW base, Adam meta, η = 1e-3) configuration:

| α₀ | scalar | six blocks | layerwise |
|---|---|---|---|
| 1e-6 | 91.630 (n=3) | 91.681 (n=6) | 91.781 (n=3) |
| 1e-3 | 92.631 (n=6) | 92.237 (n=9) | 91.382 (n=16) |

The ordering is monotone **increasing** in granularity at α₀ = 1e-6 and monotone **decreasing** at
α₀ = 1e-3. (These cells pool across batches with unequal composition and are descriptive; the
in-batch statement is the η pair above.)

**The parent's own cell, checked for a clipping artefact.** The 18 unaugmented AdamW/Adam runs at
η = 1e-3, α₀ = 1e-6 — the only cell in the corpus that touches the parent's actual experiment —
read scalar 73.830 ± 0.103, six blocks 74.352 ± 0.180, layerwise 73.449 ± 0.119 (n = 6 each), i.e.
the parent's blockwise-beats-scalar step reproduces at **+0.522** and the *next* rung reverses it.
Because β₀ = ln(1e-6) = −13.8155 sits 1.1845 nats above a −15 floor while the travel budget is
50 nats, this cell is arithmetically capable of binding on both guards, and no probe existed. We
re-ran it (`ub9`, 9 jobs) in a wide box with clip counting on. The registered scorer's verdict,
verbatim: *"REPRODUCTION STANDS. The parent's blockwise>scalar step survives a box in which
clipping is measured rather than assumed, AND the next rung still reverses it."* In the wide box
the step is **+2.375** and the reversal at the next rung is **−0.806**.

### 4.2 The group count is smooth within a family, but shallow and sign-unstable across cells

Holding the partition family fixed (uniform chunks) inside **one** batch (`ck1`), ResNet-18,
SGDm + Lion, η = 1e-4:

| arm | m | plateau5 (n=3) |
|---|---|---|
| chunk1 (per weight) | 11,173,962 | 90.979 ± 0.131 |
| chunk2 | 5,586,981 | 91.095 ± 0.024 |
| chunk16 | 698,373 | 91.411 ± 0.277 |
| chunk128 | 87,297 | 92.159 ± 0.063 |
| chunk1024 | 10,913 | 92.526 ± 0.077 |

The five-rung ascent is **+1.547 ± 0.152 pp (t 10.2)** over 3.01 decades. Its *local* secants, in
ladder order from finest to coarsest, run **+0.383, +0.350, +0.828, +0.407** pp/decade — a factor
of 2.4 between adjacent rungs of one curve, which is why mutually incompatible "count slopes" can
all be fitted to one corpus.

Measured *directly*, at fixed partition family and inside a batch, the count axis is small and
sign-unstable. Over twelve in-batch measurements of **U = chunk2325 − chunk777** (0.4732 decades):

| cell | U | cell | U |
|---|---|---|---|
| cc1 | +0.101 ± 0.190 | ml2 | +0.337 ± 0.088 |
| rl3 @1e-4 | +0.064 ± 0.154 | g3m (R34) | +0.263 ± 0.074 |
| rl3 @3e-4 | +0.017 ± 0.098 | r50 (R50) | +0.321 ± 0.259 |
| fa1 | +0.019 ± 0.094 | gm2 (C100) | −0.054 ± 0.196 |
| hz3 (300 ep) | −0.148 ± 0.080 | nl1/SGD | +0.182 ± 0.283 |
| aw1 (AdamW) | +0.045 ± 0.097 | nl1/RMSProp | −0.037 ± 0.085 |

U changes sign across cells and its magnitude never exceeds +0.34 pp — smaller than D in every cell where both
are measured, and of the opposite sign in two. **No single count slope exists to import**, and any count correction must be measured in the batch and at the budget being
corrected.

### 4.3 The primary: at fixed group count, the partition matters

**Table 2 — D = uniform chunk − architecture-aligned nodewise, count-matched, within batch,
`plateau5`.** Welch difference of arm means; se from the two arm variances; every cell is a
separate contiguous submission except the two `rl3` rungs and the two `nl1` bases, which share a
batch.

| # | batch | network | dataset | base | η | epochs | n | **D (pp)** | se | t |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cc1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.727** | 0.200 | 3.63 |
| 2 | mm1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.485** | 0.161 | 3.01 |
| 3 | pp1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.581** | 0.141 | 4.11 |
| 4 | gn1 | ResNet-18 (BN) | C10 | SGDm | 1e-4 | 100 | 4 v 4 | **+0.587** | 0.153 | 3.83 |
| 5 | ml2 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 6 v 6 | **+0.456** | 0.142 | 3.20 |
| 6 | rl3 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.681** | 0.173 | 3.93 |
| 7 | rl3 | ResNet-18 | C10 | SGDm | 3e-4 | 100 | 3 v 3 | **+0.591** | 0.096 | 6.18 |
| 8 | fa1 | ResNet-18 | C10 | SGDm | 3e-4 | 100 | 6 v 6 | **+0.629** | 0.123 | 5.11 |
| 9 | hz3 | ResNet-18 | C10 | SGDm | 1e-4 | **300** | 6 v 6 | **+0.428** | 0.086 | 4.94 |
| 10 | gn1 | ResNet-18 (**GroupNorm**) | C10 | SGDm | 1e-4 | 100 | 8 v 8 | **+0.202** | 0.137 | 1.48 |
| 11 | aw1 | ResNet-18 | C10 | **AdamW** | 1e-4 | 100 | 3 v 3 | **+0.279** | 0.087 | 3.19 |
| 12 | nl1 | ResNet-18 | C10 | **SGD** | 1e-4 | 100 | 3 v 3 | **+1.035** | 0.109 | 9.54 |
| 13 | nl1 | ResNet-18 | C10 | **RMSProp** | 1e-4 | 100 | 3 v 3 | **+0.973** | 0.251 | 3.87 |
| 14 | g3m | **ResNet-34** | C10 | SGDm | 1e-4 | 100 | 9 v 9 | **+0.666** | 0.094 | 7.08 |
| 15 | r50 | **ResNet-50** | C10 | SGDm | 1e-4 | 100 | 3 v 3 | **+0.881** | 0.261 | 3.37 |
| 16 | gc1 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | 4 v 4 | **+1.640** | 0.245 | 6.71 |
| 17 | gm2 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | 3 v 3 | **+1.485** | 0.238 | 6.24 |

**D is positive in every cell.** Sixteen of seventeen are resolved at t ≥ 3; the exception is the
GroupNorm cell at t 1.48. A further cell (`ar1`, D = +0.697 ± 0.118) is **excluded** as
box-void — it bound on the guards asymmetrically, in the direction that inflates D — and is
reported here only so that its exclusion is visible.

**A commensurability warning we obey.** A percentage point is not comparable across error budgets.
ResNet-18/CIFAR-10 sits on a ≈7–8 pp budget and CIFAR-100 on ≈29–30 pp. On **relative** error
reduction CIFAR-100's +1.640 pp is D/headroom = 0.055, the **smallest** value among BatchNorm
cells, not the largest. We therefore never average CIFAR-10 and CIFAR-100 D's, and never plot them
on one axis.

### 4.4 D is genuinely heterogeneous

Over the twelve cells that share a **byte-identical** partition contrast (ResNet-18
`nodewise` → `chunk777`; rows 1–4, 6–13 above), the fixed-effect pool is **+0.546** with

> **Q = 43.2 on 11 df, p = 1.0e-5**; DerSimonian–Laird **τ = 0.215 pp** against an rms measurement
> se of **0.151 pp**.

Dropping the GroupNorm cell: Q = 36.4 on 10 df, p = 7.2e-5. Adding `ml2` as a thirteenth cell:
Q = 43.6 on 12 df, p = 1.8e-5, τ = 0.206. So D varies across configurations by roughly 1.4× its
measurement error, for reasons we cannot attribute — which is exactly the premise the prediction
question in §5.8 needed.

### 4.5 Tuning each arm to its own optimum does not remove D

The referee objection ranked most likely to sink this result is that D compares two arms at one
arm's favourable meta-stepsize. We closed it inside one batch (`rl3`, 24 runs, four arms × η ∈
{1e-4, 3e-4} × 3 seeds). The registered scorer's H3, verbatim:

```
D(ms=1e-4) = +0.681  se 0.126
D_own      = +0.591  se 0.126        (each arm at its OWN argmax)
dD         = -0.090  se 0.178  t -0.51 (16 df)
VERDICT: RULE 11 CLOSED ON R18/CIFAR-10 -- tuning each arm to its
own argmax does not resolvably move D.
```

The reportable sentence is *"D is unchanged at matched optima to within 0.356 pp"*. This closes the
objection **on ResNet-18/CIFAR-10 and nowhere else**: no meta-stepsize ladder exists on ResNet-34,
ResNet-50 or CIFAR-100, and no ladder exists under AdamW.

The same batch measures D's sensitivity to η directly: +0.681 → +0.591 across 0.477 decades, i.e.
**−0.189 pp per decade of η**, within one batch. That is the number to use; the cross-batch
cross-box value the record previously carried is superseded.

### 4.6 Alignment is not the carrier

`permnode` holds nodewise's group **count** and its **exact per-tensor size multiset** and
randomises only *which* weights share a group, within each tensor. Registered five-way in advance
with a symmetric band. The scorer's P2, verbatim:

```
permnode<S> (m=14420, nodewise's EXACT size multiset, membership randomised)  92.003 +-0.090 (n=3)
nodewise    (m=14420, output channels)                                        92.012 +-0.129 (n=3)
A = permnode - nodewise = -0.009 pp   (se 0.157, t -0.06)
registered: A > +0.30 HURTS | (+0.15,+0.30] UND | [-0.15,+0.15] NULL | ... 
-> **NULL**
```

In the same batch D = +0.581 ± 0.141 and B = chunk777 − permnode = **+0.590 ± 0.107 (t 5.53)**, so
by construction A + B = D and the shares are **alignment −1.6%, size distribution +101.6%**.

This is the most surprising result in the corpus, and it contradicts the stated principle of at
least one shipped method: Adam-mini justifies its blocks by Hessian sub-block **alignment**, and in
our regime alignment is worth nothing once the size multiset is held fixed.

**Its limits, printed with it.** `permnode` permutes **within** each tensor, so this is a
within-layer statement; it does not test whether *layer* boundaries matter. It is a statement at
η = 1e-4. And it uses the run seed as its permutation seed, so this batch cannot separate
permutation variance from seed variance — which widens the interval rather than narrowing it.

### 4.7 The prescription, and its exact scope

The practitioner's move implied by §4.3 and §4.6 is: **give each one-dimensional tensor a single
step size instead of one per element.** Measured as T = `nodewise1d` − `nodewise`, within batch:

| batch | network / setting | n | T (pp) | se | t |
|---|---|---|---|---|---|
| bn1 | R18 / C10 / SGDm | 3 v 3 | +0.427 | 0.041 | 10.43 |
| ml2 | R18 / C10 / SGDm | 6 v 6 | +0.619 | 0.133 | 4.66 |
| fa1 | R18 / C10 / SGDm, η 3e-4 | 6 v 6 | +0.649 | 0.110 | 5.88 |
| g3m | **R34** / C10 / SGDm | 9 v 9 | +0.758 | 0.093 | 8.13 |
| cc1 | R18 / C10 / SGDm | 3 v 3 | +0.816 | 0.159 | 5.13 |
| r50 | **R50** / C10 / SGDm | 3 v 3 | +1.049 | 0.317 | 3.31 |
| gm2 | R18 / **C100** / SGDm | 3 v 3 | +1.363 | 0.151 | 9.00 |
| hz3 | R18 / C10 / SGDm, **300 ep** | 6 v 6 | +0.337 | 0.069 | 4.85 |
| nl1 | R18 / C10 / **SGD** | 3 v 3 | +0.692 | 0.135 | 5.12 |
| nl1 | R18 / C10 / **RMSProp** | 3 v 3 | +0.916 | 0.242 | 3.79 |
| aw1 | R18 / C10 / **AdamW** | 3 v 3 | **+0.091** | 0.078 | 1.16 |

The move costs nothing — it *reduces* the number of learned quantities from 14,420 to 4,851 — and
under an SGDm, SGD or RMSProp base it is worth **+0.337 to +1.363 pp** across ten within-batch
cells, every one resolved at t ≥ 3.3. **Under AdamW it is worth nothing measurable
(+0.091 ± 0.078, t 1.16).** That is the scope line, and §5.4 explains why it is where it is.

Decomposing T = (D − G) + U on `rl3` at η = 1e-4: T = +0.756 = 0.692 + 0.064. The **count**
component is 8% of the effect; the tail component is the rest. Any account that treats "merge the
1-D tensors" as a count reduction has the decomposition backwards.

### 4.8 Budget: the effect is present at 3× the budget and is statistically flat

`hz3` ran the four arms for 300 epochs at 6 seeds in one batch, so D at 100 and at 300 epochs can
be taken **within run**, per seed, cancelling seed, run, batch, box and GPU class identically.
From the raw epoch series:

| budget | D (paired, n = 6) | se |
|---|---|---|
| 100 | +0.576 | 0.109 |
| 200 | +0.514 | 0.115 |
| 300 | +0.428 | 0.071 |

**D(300) − D(100) = −0.149 ± 0.105, t −1.42.** So D is present and resolved at a 3× budget and is
statistically **flat** from 100 to 300 epochs. It is not an artefact of the last fifth of training,
and it does **not** grow. (An earlier internal reading claimed growth; that reading used a 50-epoch
trailing window, which at B = 100 spans epochs 50–99 and therefore *contains* the mid-training
trough documented below, while at B = 300 it contains none. The window injects the trough at
exactly one budget: at w = 50 the same data give +0.229 ± 0.045, t +5.11. See Appendix A.2.)

**The trajectory is not monotone, and we publish it.** Within run, D goes significantly *negative*
in mid-training and recovers:

| epoch | cc1 (n=3) | g3m, ResNet-34 (n=9) |
|---|---|---|
| 25 | +0.625 ± 0.170 | −0.081 ± 0.156 |
| 55 | **−0.560 ± 0.150 (t −3.73)** | **−0.518 ± 0.128 (t −4.04)** |
| 75 | +0.345 ± 0.129 | — |
| 100 | +0.727 ± 0.146 | +0.666 ± 0.091 |

Any claim about D is a claim about the end of training at these budgets.

---

## 5. Eight dead mechanisms and two nulls

This section is the second half of the contribution, not an appendix. Six of these were killed by
tests registered before their data existed; one was killed by a reviewer after it had passed its
own cross-validation; one was withdrawn after re-reading the sources it was attributed to.

**Index of the eight, and where each dies.**

| # | candidate mechanism | verdict | where |
|---|---|---|---|
| M1 | √N estimator-noise averaging over group members | **untested, not refuted** — our instrument measures the wrong quantity; its literature attribution withdrawn | §5.1, §2.5 |
| M2 | Meta-gradient correlation (an N_eff/m field) predicts accuracy | **dropped** on its own pre-registered gate: anti-concordant t −11.14, dissociation t −23.26 | §5.2 |
| M3 | Degenerate size-1 groups are the carrier | **refused**: removing 100% of singletons buys +0.115 ± 0.133 (t 0.87) | §5.3 |
| M4 | The size-1 tail carries it universally | **narrowed to SGDm**: D − G = +0.715 ± 0.248 (SGDm) vs +0.047 ± 0.124 (AdamW) | §5.4 |
| M5 | Choi-style inclusion — a finer partition contains the coarser one once tuned | **inapplicable**: granularity is state, not hyperparameters; the only setting where the arms coincide is η = 0 | §2.2, §4.5 |
| M6 | The base optimiser's own second-moment normalisation | **refuted**: RMSProp and AdamW both carry one and differ by +0.694 ± 0.266 (t 2.61) | §5.5 |
| M7 | D tracks the aligned arm's accuracy level | **falsified within batch** by up to 7 se; null inside CIFAR-10 (−0.021 ± 0.077) | §5.6 |
| M8 | Some summary statistic of the group-size distribution | **not identifiable** from this design (rank 3, one contrast type) | §5.7 |

**The two nulls**: architecture alignment (§4.6, §5.10) and out-of-sample predictability of D
(§5.8). §5.9 adds the failure of the classical remedy — hierarchical partial pooling — which is a
dead *fix* rather than a dead mechanism, and is included because CAM-HD makes it the obvious
question to ask.

### 5.1 Dead: √N estimator-noise averaging

The natural story is that a group of size N averages N meta-gradient samples, so a coarse group's
step-size estimate has noise ∝ 1/√N and fine partitions are noisier. We built a per-group drift
instrument to test it and got the wrong sign in every fit — 6 of 6 — where a 1/√N model requires a
log-log slope of −0.500. *(That count is carried from the project record and was **not**
re-derived at write time; see Appendix A.9. Nothing below rests on it.)*

**We do not present that as a refutation of the variance claim, because it is not one.** The
instrument measures *drift* — the per-step magnitude |Δβ̄| — which is net systematic movement, not
an estimator variance; and under Lion's sign update |Δβ| = η per step exactly, so the statistic is
**censored at the meta-stepsize** (two published fits ran through arms pinned at exactly 1.000e-03).
The surviving fits are 4-point log-log OLS with R² as low as 0.08. The only sentence this
instrument supports is: *the net drift of a group's step-size exponent does not fall like
1/√(group size); we did not measure the estimator variance.* The variance mechanism is
**untested**, not refuted, and we say so.

Separately, and this is a correction to our own earlier writing: the attribution of a √N
noise-averaging argument to Adam-mini, Adalayer and SGG is **withdrawn** (§2.5).

### 5.2 Dead: the meta-gradient correlation field predicts accuracy

A natural design principle for grouping is "put weights with correlated meta-gradients together",
which suggests an effective-sample-size statistic N_eff/m as a predictor. We instrumented it and
registered a five-way concordance test in advance. The `cc1` scorer, verbatim:

```
C2  aligned vs uniform at m=14,420
    d_acc = +0.727 pp (t +3.63, RESOLVED)   d_N_eff/m = -0.0237 (t -11.14, RESOLVED)
    -> **ANTI-CONCORDANT**
C3  aligned vs uniform at m=4,851, size-1 tail already gone
    d_acc = +0.011 pp (t +0.08, unresolved)  d_N_eff/m = -0.0529 (t -23.26, RESOLVED)
    -> **DISSOCIATION**
-> **MIXED: THE FIELD IS NOT A SUFFICIENT STATISTIC.**
```

The negative is strong, not weak. The field channel resolves at t −11 and t −23 — it is not too
noisy to read. It reads decisively, and decisively *against* accuracy on one contrast and silently
on the other. This is the sharpest thing we can say to the meta-gradient-correlation line of
argument: the correlation statistic that line reaches for does not track the outcome it is meant
to justify.

### 5.3 Dead: size-1 groups are the carrier

The most attractive explanation of §4.3 is that D is caused by the 9,610 degenerate size-1 groups
in `nodewise`. Inside one batch (`ck1`) we removed **100% of a network's singletons** by going from
one step size per weight (chunk1, m = 11,173,962, 100% singletons) to one per pair (chunk2,
m = 5,586,981, **0%** singletons):

> chunk1 90.979 ± 0.131 → chunk2 91.095 ± 0.024. **Step = +0.115, se 0.133, t 0.87 — unresolved**,
> against a count-only prediction of +0.13 to +0.16 from the family's own local secants.

The ladder is smooth in log m with **no kink** at the one step where singleton fraction collapses
from 100% to 0%. Reported against our own interest, and **with its power limit**: that step
re-groups 100% of 11.17M coordinates, whereas the tail in `nodewise` is 0.086% of the weights. It
refuses a general *size law*; it cannot rule out a tail-specific effect. The unit is the **tensor**,
not the group size.

### 5.4 Dead: the tail carries it universally

`D − G` isolates the size-1 tail's contribution — G is the same contrast with the tail already
removed from both arms, count-matched exactly.

| cell | D | G | **D − G** | t |
|---|---|---|---|---|
| cc1 (SGDm) | +0.727 ± 0.200 | +0.011 ± 0.147 | **+0.715 ± 0.248** | 2.88 |
| rl3 @1e-4 (SGDm) | +0.681 ± 0.173 | −0.011 ± 0.087 | **+0.692 ± 0.194** | 3.57 |
| fa1 (SGDm) | +0.629 ± 0.123 | −0.001 ± 0.076 | **+0.630 ± 0.145** | 4.35 |
| hz3 (SGDm, 300 ep) | +0.428 ± 0.086 | −0.057 ± 0.061 | **+0.484 ± 0.106** | 4.57 |
| g3m (SGDm, R34) | +0.666 ± 0.094 | +0.171 ± 0.073 | **+0.495 ± 0.119** | 4.15 |
| r50 (SGDm, R50) | +0.881 ± 0.261 | +0.153 ± 0.314 | **+0.729 ± 0.409** | 1.78 |
| gm2 (SGDm, C100) | +1.485 ± 0.238 | +0.068 ± 0.069 | **+1.417 ± 0.248** | 5.72 |
| nl1 (RMSProp) | +0.973 ± 0.251 | +0.020 ± 0.049 | **+0.953 ± 0.256** | 3.72 |
| ml2 (SGDm) | +0.456 ± 0.142 | +0.173 ± 0.071 | **+0.282 ± 0.159** | 1.77 |
| rl3 @3e-4 (SGDm) | +0.591 ± 0.096 | +0.217 ± 0.128 | **+0.375 ± 0.160** | 2.34 |
| nl1 (SGD) | +1.035 ± 0.109 | +0.525 ± 0.294 | **+0.510 ± 0.314** | 1.63 |
| **aw1 (AdamW)** | +0.279 ± 0.087 | **+0.232 ± 0.089** | **+0.047 ± 0.124** | **0.38** |

Under SGDm, removing the tail removes the gap. **Under AdamW it does not**: G is resolved at
t 2.62 and D − G collapses to +0.047. The pre-registration for that batch said, before the data
existed, that *"a RESOLVED non-null G would say the tail story is base-dependent and must be
re-scoped."* It is, and it is.

> **"The gap lives in the degenerate size-1 tail" may not be written as a general claim.** It holds
> under an SGDm base with a Lion meta-optimiser and is scoped to that.

The same batch's D itself is **UNRESOLVED** on its own registered rule: `analysis/c88_scorers.py
--score aw1` prints `{'D_adamw': 0.279, 'se': 0.087, 't': 3.19, 'rule': "UNRESOLVED at n=6.
Report the interval. Do NOT re-cut the data, and do NOT describe it as 'partially transferring'."}`
The registered bar was a 95% lower bound above +0.30; the realised bound is **+0.108** (normal
approximation; **+0.038** on Welch df 4), so the bar is not cleared. The registration also
specified 6 seeds where only 3 reached the contrast, so the primary ran at half its registered
power. **D under AdamW is reported as an interval, +0.279 [0.108, 0.450], not as a transfer.**

### 5.5 Dead: base-optimiser normalisation

If the mechanism were "a base optimiser that already normalises per coordinate does not need the
partition to do it", then RMSProp and AdamW — both carrying a second moment — should behave alike.
They do not: **D(RMSProp) − D(AdamW) = +0.694, se 0.266, t 2.61**. Whatever separates the base
optimisers here, second-moment normalisation is not it.

### 5.6 Dead: D tracks the accuracy level of the aligned arm

Over all 11 design points, regressing D on the aligned arm's `plateau5` gives slope
**−0.043 ± 0.014, t −3.20, r −0.729** — which looks like a law and is not one, because level and
dataset are the same column: the single CIFAR-100 design point sits at level 70.44 and the ten
CIFAR-10 design points at 89.33–92.98.

* **Inside CIFAR-10 the slope is zero:** **−0.021 ± 0.077, t −0.27, r −0.096** over 10 design
  points. Its *sign* is set by which points are included — an earlier reading of the same corpus
  with two fewer batches gave +0.026 ± 0.088.
* **The decisive within-batch test falsifies it.** `gn1` ran BatchNorm and GroupNorm ResNet-18 in
  the **same batch** — one variable changed, batch cancels. Level moves **−2.670 pp**
  (92.000 → 89.330). Every version of the level model predicts D should **rise**: the three slopes
  the project record has carried (−0.392, −0.289, −0.136) predict **+1.047, +0.772, +0.363**, and
  the two slopes re-derived here (−0.043 over all design points, −0.021 within CIFAR-10) predict
  **+0.115** and **+0.056**. Observed **dD = −0.385 ± 0.205: it falls.** That is 7.0, 5.6, 3.6,
  2.4 and 2.2 se wrong-signed respectively — a model whose prediction is wrong-signed at every
  slope anyone has fitted to it.
* It is not a shared-arm artefact: D and level share the `nodewise` arm, which mechanically induces
  a slope of about −0.013 across CIFAR-10 points, one twentieth of the effect that was claimed.

This is a **gain, not a loss**: "the partition matters" is not a restatement of where the aligned
arm lands, and a covariate the paper would otherwise have had to defend is removed.

### 5.7 Dead (and un-killable): a summary statistic of the size distribution

We constructed exact group-size multisets for every (network, granularity) cell we could
instantiate — 150 of 163 attempted, the rest being block partitions applied to the wrong network
depth, which the optimiser rejects — by instantiating the optimiser on CPU and reading sizes off
its own allocated state, with two receipts asserted on every cell
(`Σ size × count = Σ p.numel()`; `Σ count = beta elements allocated`) passing on all 150, and
reproducing every group count in this paper exactly. We then scored twenty
candidate statistics — mean/median/sd/CV/skew/min/max, harmonic and geometric mean, sd of log size,
categorical and weighted entropy, inverse participation ratio, Gini, singleton fractions by group
and by weight, threshold fractions, and a heterogeneity index.

An earlier analysis nominated the degeneracy indicator with an apparently decisive fit. **That
positive claim is deleted, and the reason it is deleted is the finding.** `frac_groups_size1` takes
exactly **two values** across the entire count-matched design — 0.6664 on `nodewise`, 0.0000 on all
three other arms, on every network. Re-running the analyst's own shape test with (a) that
statistic, (b) a bare 1/0 "is this arm nodewise" dummy, (c) an arbitrary two-level regressor, and
(d) the plain test that the three non-nodewise arms share a mean gives χ² values **identical to
five figures**. The fit *is* the three-arm equality test, relabelled; a regressor whose fit is
invariant to its own values is not a predictor.

**The structural limit governs everything above.** At fixed count the corpus contains exactly one
contrast type — architecture-aligned versus uniform chunk — plus one zero-dose control
(`permnode`). Over the four count-matched arms the candidates are collinear at |r| ≥ 0.93 and the
design matrix has **rank 3**, so at most two statistics are jointly identifiable and all twenty
collapse into about two equivalence classes. Cross-validation cannot catch this: leave-one-batch-out
leaves the arm structure intact in every fold. The licensed sentence is therefore a **limit**, not
a search result:

> At fixed group count the corpus contains a single contrast type, so every candidate summary of
> the size distribution reduces to an indicator for the architecture-aligned arm and none is
> identifiable. The size distribution remains the surviving carrier; **which** property of it is an
> open question requiring new runs of a kind this corpus does not contain.

§9 states the experiment that would break the degeneracy.

### 5.8 Null: D is not predictable from configuration properties

The seventeen D cells of Table 2 collapse to **11 distinct design points** (the six byte-identical ResNet-18/SGDm/
η=1e-4/100-epoch batches are one point; the two CIFAR-100 batches are one). Leave-one-design-
point-out, refitting each single-predictor model on the held-in 10:

| model | LOO RMSE | vs "predict the corpus mean" |
|---|---|---|
| **mean (baseline)** | **0.4052** | — |
| D ∝ level (OLS) | 0.3161 | −22% |
| D ∝ k·log(headroom) | 0.3293 | −19% |
| D ∝ k·headroom | 0.3441 | −15% |
| CIFAR-100 dummy | 0.3972 | −2% |

**None of this is a result, and here is why.** The margin is dominated by the single CIFAR-100
fold (mean error −0.935, best model −0.559); restricted to the ten CIFAR-10 folds the models win by
0.006–0.012 RMSE, i.e. nothing. A sign test over 11 folds gives 9/11, two-sided **p = 0.065**. The
functional form is itself the winner of about ten candidates scored on the same 11 points, so any
apparent improvement is a best-of-ten selection statistic before it is anything else. And the power
bound is decisive: **at 11 design points a predictor needs |r| ≥ 0.602 — it must explain ≥ 36% of
the between-design-point variance — to be visible at p < 0.05**; seeing |r| = 0.4 would need ≈ 25
design points, which is not reachable by brute force.

Three aliasings make the corpus look richer than it is. (i) `frac_groups_size1`, log m, log
params, log(n classes) and the CIFAR-100 dummy are **not five predictors**: the singleton fraction
is pinned near 2/3 by a structural identity (every convolution has `bias=False` and is followed by
one affine norm), taking 0.66644 on every CIFAR-10 cell and 0.66438 on the CIFAR-100 cells, so
regressing D on it is regressing D on the dataset dummy. Anyone who writes *"D scales with the
singleton fraction"* from this corpus has written *"CIFAR-100 is different"*. (ii) m and params are
1-vs-10 leverage contrasts resting on one architecture point each. (iii) G shares a batch with D
and has no predictive content anyway.

> **The draft sentence:** *D is real, replicated across 17 count-matched within-batch cells, and
> varies genuinely across configurations (τ = 0.215 pp against 0.151 pp measurement noise). No
> measurable property of a configuration predicts D out of sample better than the corpus mean by a
> margin this design can resolve.*

### 5.9 Dead: hierarchical partial pooling as the fix

Covered in §2.4 with numbers. Summarised here so the section is complete: three pooling operators
were implemented. The `zpool` figures in §2.4 were re-derived at write time on `plateau5`; the
`M0`/`M1` statements below are carried from the project record and were **not** (Appendix A.9).
`M0 shrink` is withdrawn because the operator saturates (it applies every step, so
any λ ≥ 0.001 has a half-life ≤ 693 steps against ≈50,000 — the sweep measured full pooling three
times over); `M1 additive r` shows an interior optimum that is largely an α₀ escape-rate artefact
and transfers to no other architecture or dataset; and the confound-free `zpool` rescues an
over-fine partition by +10.04 pp and still lands 2.18 pp below plain six-block. The r-dial is a
meta-learning-rate knob wearing a pooling costume: under Lion every increment is exactly ±η, so
pooling divides the effective meta-stepsize by |2p − 1|.

**We therefore do not propose a new pooling design.** CAM-HD's remedy is the right classical
instrument and we could not make it beat a good partition.

### 5.10 Null: alignment (repeated here because it is a deliverable)

§4.6. A = −0.009 ± 0.157, t −0.06, against a band registered in advance. A clean negative is worth
as much as the positive and it is what redirected this programme from architecture alignment to
group-size homogeneity.

---

## 6. Measurement discipline: what our own instrument did to us

This section reports three defects in our own process. Each cost a claim; each is cheap for a
reader to avoid.

### 6.1 A batch that failed silently on its own axis

`ml2` (24 runs) was built to fill the corpus's largest external-validity hole: **every
count-matched partition run uses a Lion meta-optimiser**. It was to add meta = Adam and
meta = RMSProp at a fixed SGDm base. It did not. The submission script composes the base/meta flags
into a variable and then appends a second `--alg-meta Lion` after it, and `argparse` takes the last
occurrence. The runs' own logged argument line reads:

```
--alg-meta Adam --normalizer-param-meta 0.999 --momentum-param-meta 0.9 --weight-decay-meta 0
--alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0
```

and the runtime warns `args_meta includes unnecessary attributes {'normalizer_param'}` — Lion does
not use it. **All 24 `ml2` runs are meta = Lion**, and its two nominal halves are byte-identical
configurations. The corpus census confirms the hole is still open: **367 of 367 partition-programme
runs are meta = Lion**, across four base optimisers.

Reported as such, `ml2` is still informative, in a way we would not have bought deliberately: it is
two independent 3 v 3 measurements of the *same* D in the *same* batch. They read **+0.554 ± 0.217**
and **+0.357 ± 0.211**. A 0.197 pp spread between replicates of one measurement, inside one batch,
is a direct bound on what a single n = 3 v 3 D cell can carry — and it is of the same order as
τ = 0.215 pp (§4.4). Pooled, `ml2` gives D = +0.456 ± 0.142 (6 v 6), which is row 5 of Table 2.

### 6.2 The metric column, and the registered-scorer rule

Two headlines were withdrawn in this project for the same two habits: quoting the 20-epoch plateau
column instead of the 5-epoch primary, and scoring a batch with a reduction written after the data
arrived instead of the scorer committed before the runs existed. On `aw1`, the two columns give
G = +0.226 (t 3.23) and G = +0.232 (t 2.62); the difference is small but the *verdict* moved,
because the registered rule was a 95% lower bound and the hand-rolled prose restated it as a point
estimate with t ≥ 2. On `hz3`, a 50-epoch trailing window turned a flat budget effect into a
growing one (§4.8). Both are one-line mistakes that survived internal review.

The rule we now follow, and recommend: **if a batch has a registered scorer, it is scored by that
scorer, unedited, and its output is quoted, not paraphrased.** A hand-rolled reduction may be a
cross-check; disagreements resolve in favour of the committed code.

### 6.3 Batch and seed as sources of variance — and a claim of ours that did not reproduce

Every primary in this paper is within-batch, which cancels any offset shared by the two arms
regardless of how large it is. That design choice is safe and we keep it. What we can no longer
support is the *reason* we previously gave for it.

Re-derived at write time: taking every configuration key (network, dataset, batch size,
granularity, base, meta, η, α₀, γ, augmentation, β-box, hierarchical mode, λ, r, epoch budget) that
appears in **two or more batches at n ≥ 3 per batch**, with fixed-LR baselines excluded and
non-converged regimes removed by a dataset-relative floor, gives **26 configurations over 237
runs**. Within-config, across-batch:

* **F(39, 172) = 0.71** — batch is **not** resolvable as a variance component;
* random-effects **sd_batch = 0.000 pp** against a pooled within-arm **sd of 0.193 pp**;
* observed batch-mean spread per configuration: **median 0.100 pp, mean 0.126 pp, max 0.319 pp**.

The largest single replication series in the corpus is the `nodewise` cell at η = 1e-4, present in
**seven** batches: 91.890 / 91.961 / 92.000 / 92.012 / 92.044 / 92.064 / 92.184 — a 0.294 pp spread
over 25 runs.

A two-way batch × seed ANOVA on the 14 configuration cells carrying a complete rectangle gives
**SEED F(30, 30) = 1.50, p = 0.138** — seed is null, which agrees with the internal record. But the
same reduction gives **BATCH F(14, 30) = 0.54, p = 0.89**, and no cell definition we could
construct reproduced the record's **F(62, 85) = 5.47, sd_batch ≈ 0.21 pp**. Including
non-converged runs sends batch F to 722, which is a statement about accuracy regimes, not batches.
**We therefore withdraw the claim that batch is a large random effect on this cluster** and replace
it with what we can measure:

> At byte-identical science and n ≥ 3 per batch, cross-batch offsets on this cluster are bounded by
> about 0.32 pp and are not separable from within-arm noise; seed is null (F 1.50, p 0.138). We
> keep every primary within-batch because the offset, while small on average, is not bounded
> *a priori* and is half the size of the effect at its observed maximum — and because at least one
> batch in this corpus is known to have run with unintended state (a modified optimiser file
> timestamped 33 s before submission), which no variance model would have caught.

Hardware was excluded by direct measurement: within (configuration × family), 2080Ti − L4 = +0.035
(n = 45), A100 − L4 = −0.021 (n = 21), A100 − 2080Ti = +0.112 (n = 5), over 29 distinct nodes.

---

## 7. Threats to validity

**T1 — One meta-optimiser.** All 367 partition-programme runs use Lion. Lion's sign update makes the
per-group α the *only* thing setting per-coordinate update magnitude, which is precisely the regime
where the partition should matter most. So our headline is measured at the most favourable point of
the axis we never varied. §6.1 explains why the batch built to fix this did not. **This is the
paper's largest hole.**

**T2 — The mechanism is missing, and one candidate is not identifiable from this design.** §5.7. We
know the carrier is the size distribution rather than alignment; we cannot say which property of it,
and this corpus provably cannot tell us.

**T3 — Scale and domain.** CIFAR-resolution vision, ResNets, one framework. ImageNet-1k is not
available to us: the copy on our allocation has 489 of 1000 training classes and an unlabelled
validation set. No transformer, no language model, no reinforcement learning — and the parent
method's own home is reinforcement learning.

**T4 — Competitiveness.** The best MetaOptimize cell in 2,113 runs is 93.317 ± 0.083 (n = 3;
six blocks, AdamW base + Adam meta, η = 1e-3, α₀ = 3e-4, itself the interior maximum of a 7-rung α₀
ladder). Tuned SGD + cosine at the same budget is 95.124 ± 0.047 (n = 5; lr 0.1, the interior
maximum of a bracketed 4-point grid: 94.172 / 94.844 / **95.124** / 94.181). The deficit is
**−1.807 pp**. MetaOptimize does beat a constant-LR AdamW tuned over four rungs (91.849 ± 0.092),
which is the comparison the parent paper makes. We make no competitiveness claim beyond that.

**T5 — Rule 11 is closed on one cell only.** §4.5 closes the "you compared at one arm's favourable
η" objection on ResNet-18/CIFAR-10. No meta-stepsize ladder exists on ResNet-34, ResNet-50,
CIFAR-100 or under AdamW.

**T6 — The 100-epoch horizon, and non-monotonicity within it.** D goes significantly negative at
epoch 55 on two independent batches and recovers by epoch 100 (§4.8). Our claims are about the end
of training at 100 and 300 epochs.

**T7 — BatchNorm and "size-1 tail" are under-identified.** On every network we ran, the only 1-D
tensors are normalisation parameters and one bias, so "the groups are degenerate" and "the groups
are on the normalisation parameters" coincide exactly. `gn1` was the designated separator and
**issued no verdict**: its pre-registered commensurability gate fired on a 1.37× error-budget ratio
between the BatchNorm and GroupNorm halves. Its face values may not be quoted as a transfer result,
and throughout this paper we write *"normalisation scalars or, more generally, one-dimensional
tensors"* rather than committing.

**T8 — n = 3 in ten of seventeen cells.** Seed is statistically null on this cluster (§6.3), and a
k-of-k per-seed agreement at n = 3 has exact p = 0.25 and carries no evidence, so we report no sign
tests. But ten cells rest on 3 v 3, and §6.1 shows two such cells of the same quantity differing by
0.197 pp.

**T9 — Excluded and unusable data.** One batch (`ar1`, D = +0.697 ± 0.118) is excluded as box-void
throughout. Three `hz3` rows carry a `beta_clip` metadata value inconsistent with their batch; any
scorer that groups on that column silently drops them and reads D(300) = +0.464 instead of the
authoritative +0.428. Neither exclusion changes a verdict; both are disclosed because they are the
asymmetries a referee finds first.

**T10 — Filter sensitivity.** Several quantities in this corpus move by 0.5–0.7 pp between two
defensible row filters. Every number here is re-derived at write time under the single stated gate
(§3.3), and we recommend the same discipline to anyone reusing the data.

**T11 — Novelty scoping.** We claim no absolute priority. CAM-HD built the granularity ladder,
named the small-sample mechanism, and reported an interior optimum in 2020–2022; Zheng & Kwok
studied blockwise adaptivity in 2019; Choi et al. established tuning-protocol sensitivity in 2019.
What we add is count matching, the alignment null, the 1-D-tensor object, and the negative results
in §5.

---

## 8. Reproducibility

**Data.** `results/all_runs.csv`, 2,113 rows, one per run, with the full configuration
(network, dataset, batch size, granularity, base, meta, η, α₀, γ, augmentation, β-box, hierarchical
mode, λ, r, seed), the outcome columns (`best_test`, `final_test`, `plateau`, `plateau5`, `auc`,
epochs-to-threshold), the provenance columns (`job_id`, `account`, `node`, `wallclock_min`), and
the two admissibility flags (`window_ok`, `complete`). Raw per-epoch series are the Slurm `.out`
files; per-group β trajectories are `probe.jsonl` under `runs/<batch>/probe_*/`.

**Compute.** 2,098 runs carry a wallclock; they total **1,582 GPU-hours** on a Slurm cluster over
29 distinct nodes and two accounts, on NVIDIA L4 24 GB, 2080Ti 11 GB, A100 80 GB and MIG 40 GB
partitions. GPU class is recorded per run and was measured to have no systematic offset (§6.3).

**Seeds.** Every run records its seed; seeds are 0–8. Batches specify their seed set in the
submission script; the scorers assert the registered seed set is present before scoring.

**Code.** The optimiser is the released MetaOptimize `HF.py` plus the patches in `patches/`
(`patch_chunkwise.py`, `patch_nodebn.py`, `patch_permnode.py`, `patch_zpool.py`, the probe patches,
and the augmentation patch), each of which carries an identity test against the authors' own
working `blockwise` path. Analysis is 60+ scorers under `analysis/`; the ones used for each claim
are named in §3.4 and quoted verbatim where they gate a verdict.

**Registration.** Batches carry a submission script under `bin/` with numbered pre-submission
guards (CSV present; required patches present in the live tree; group counts **measured** on the
instantiated optimiser and asserted equal to the registered values; no name collision; comparator
batch present; disk and queue headroom). Decision rules and bands are committed before submission.
`analysis/c88_scorers.py --selftest` runs 31 assertions in both directions; it currently reports
one failure, `S6e`, which asserts that the count-matched partition rows are all one base optimiser
— an assertion made true at cycle 88 and made false, deliberately, by the `aw1` and `nl1` batches.

**Deviations from the parent's configuration, stated so absolute numbers are not misread.**
(i) We enable RandomCrop + horizontal flip; the parent's text and released code appear not to.
Without augmentation ResNet-18 memorises CIFAR-10 within an epoch and there is no optimisation
headroom for a step-size method to exploit, so we regard augmentation as scientifically necessary —
but it means our absolute accuracies are not comparable to the parent's. (ii) Our headline
partition programme uses a Lion meta-optimiser where the parent's SGDm arm uses Adam. (iii) We clip
β to a box; the parent mentions no clipping. Box occupancy is measured per run and reported.

**What a reader can falsify on their own hardware in an afternoon.** Merge your one-dimensional
tensors into one step-size group each and measure the difference at fixed group count; and re-tune
both arms of any granularity comparison you have and see how much of the gap survives.

---

## 9. Conclusion

"The number of step sizes" is not one experimental variable. Within one batch, moving the shared
meta-stepsize by a decade moves the layerwise-minus-scalar gap from +3.291 to +0.655 pp; the
initial step size flips the sign of the ordering at the parent's own configuration; and the group
count, at fixed partition family, is worth at most +0.34 pp across 0.47 decades with an
inconsistent sign.

What remains after all three are controlled is a real effect. At **matched group count**, replacing
an architecture-aligned partition by a uniform one is worth a positive amount of accuracy in
**every one of 17 within-batch cells** across four network variants, two datasets, four base
optimisers, two meta-stepsizes and two budgets; it survives tuning each arm to its own optimum
(−0.090 ± 0.178); it is present and flat at 3× the budget; and it is genuinely heterogeneous
(Q 43.2 / 11 df, τ 0.215 pp against 0.151 pp noise). Architecture **alignment** is not the carrier:
holding the count *and* the per-tensor size multiset and permuting only membership is worth
−0.009 ± 0.157 pp. What is left is the group-size distribution.

**We cannot say which property of it, and the design cannot tell us.** At fixed count this corpus
contains one contrast type; twenty candidate statistics collapse to two equivalence classes and the
best-fitting one is an arm indicator in disguise. Eight further mechanisms are dead: √N averaging
(untested, not refuted, and its literature attribution withdrawn), the meta-gradient correlation
field (anti-concordant at t −11.14), size-1 groups as such (+0.115 ± 0.133), the tail as a
universal carrier (SGDm-specific), Choi-style inclusion (granularity is state, not
hyperparameters), base-optimiser normalisation (RMSProp and AdamW differ by +0.694 ± 0.266),
accuracy level (wrong-signed within batch at every slope anyone has fitted, by 2.2 to 7.0 se),
and any size-distribution summary statistic
(not identifiable). And D is not predictable out of sample from any configuration property this
design can resolve.

The honest description of this paper is therefore: **a robust, replicated, count-matched
measurement, a clean refutation of the mechanism most people would guess, a prescription that costs
nothing and works under three of four base optimisers, and no mechanism.** We would rather publish
that than a mechanism that does not survive its own controls — this project produced one of those
too, and killed it (§5.7).

**The one experiment that would break the impasse** is additive rather than subtractive. Every
count-matched arm we have ever run *removes* the size-1 tail, so "tail" is perfectly confounded with
"architecture-aligned". The decisive design creates, for the first time, an arm that is **neither
aligned nor tail-free**: arm A1 = plain `chunk2325` (m = 4,851, min size 10, size CV 0.088); arm
A2 = `chunk2325` with one large convolution tensor split into 9,610 size-1 groups and merging
elsewhere to hold m = 4,851 **exactly**. Two arbitrary partitions, identical count, differing only
in whether a size-1 tail exists. If the tail is the carrier, A2 loses ≈0.6 pp to A1. If A2 − A1 is
null, the degeneracy statistic is dead as a carrier and the size-1 tail is only a proxy. Pair it
with a heterogeneity sweep at **zero** degeneracy — uniform-count partitions at m = 4,851, minimum
size ≥ 10, prescribed size CV in {0.09, 0.40, 0.76, 1.90} — which dissociates CV, Gini, sd-log and
the heterogeneity index from the singleton fraction for the first time. Run both under AdamW and
SGDm, because that is precisely where the two candidate carriers disagree. Roughly 40 jobs. It is
registered and unfunded.

---

## Appendix A. Discrepancy register

Numbers carried in this project's internal record that **did not reproduce** at write time, and
what replaced them.

**A.1 — The meta-optimiser axis does not exist.** The record carried "meta axis (ResNet-18/CIFAR-10,
base = SGDm): Lion +0.727 · Adam +0.554 · RMSProp +0.357". The arithmetic is right and the labels
are wrong: the `ml2` batch's two halves both ran meta = Lion (§6.1), so +0.554 and +0.357 are two
replicates of one configuration, not two meta-optimisers. Every partition-programme run in the
corpus (367/367) is meta = Lion. **No meta-optimiser axis may be reported.** Consequently the
record's "G is not null under an RMSProp meta (+0.276, t 3.21)" is also mislabelled: that is
`ml2`'s second Lion replicate, and its companion replicate reads +0.071 ± 0.103.

**A.2 — Two values from the banned metric column.** The record carried
G(AdamW) = +0.226, t 3.23 and hz3 "the gap grows with budget, +0.229, t 3.27". Both come from
20-epoch and 50-epoch trailing windows respectively. On the primary 5-epoch window:
G(AdamW) = **+0.232 ± 0.089, t 2.62**; and the budget effect is **−0.149 ± 0.105, t −1.42** — flat.
Both replacements match the project's own later corrections; we record the originals so the
supersession is visible.

**A.3 — Batch as a large random effect: not reproduced.** The record carried
BATCH F(62,85) = 5.47, p = 6.9e-13, sd_batch ≈ 0.21 pp. Under every cell definition we could
construct, restricted to converged runs, batch is not resolvable (F(39,172) = 0.71; random-effects
sd_batch = 0.000 against within-arm sd 0.193). The seed half of the claim reproduces
(F(30,30) = 1.50, p = 0.138). See §6.3 for the replacement statement.

**A.4 — Heterogeneity τ.** The record carried τ = 0.285 pp against 0.137 pp measurement noise.
DerSimonian–Laird on the twelve byte-identical cells with Welch standard errors gives
**τ = 0.215 pp** against an **rms se of 0.151 pp**. Q reproduces exactly (43.2 vs 43.0 on 11 df;
36.4 vs 36.3 on 10 df dropping GroupNorm). The conclusion — heterogeneity exceeds measurement error
— is unchanged; the ratio is 1.4×, not 2×.

**A.5 — The prediction null has weakened slightly with two new batches.** The record stated that
inside CIFAR-10 the corpus mean *wins* out of sample (0.2791 vs 0.2863) with a sign test of 8/11,
p = 0.227. With `r50` and `ml2` added, the headroom models are marginally ahead inside CIFAR-10
(0.2967 vs 0.3052) and the sign test is 9/11, p = 0.065. The verdict is unchanged — nothing reaches
significance, the margin is dominated by one CIFAR-100 fold, and the functional form is a
best-of-ten selection — but the direction of the residual margin moved, and we report that rather
than the older phrasing.

**A.6 — `fa1`'s ceiling caveat, stated precisely.** The record variously described `fa1`'s
`nodewise` arm as grazing the ceiling in "5 of 6 seeds". The scorer's own occupancy table: all 24
arms read `rec_lo` 0.0000 exactly (the floor is free), and on the `nodewise` arm five of six seeds
have non-zero `rec_hi`, of which **three** exceed the 5% gate (0.1673, 0.2193, 0.0601). Both
statements are true of different thresholds; we quote both.

**A.7 — Adaptation versus a frozen β.** The record carried "+2.551 pp over frozen β". The frozen-β
runs on disk are 20-epoch probes and fail this paper's admissibility gate (`window_ok = 0`), so the
claim is **not re-derivable** under our own stated rule and is dropped rather than restated.

**A.9 — Two blocks carried from the record without re-derivation.** Two statements are **not**
re-derived at write time and are marked where they appear: (i) the "6 of 6 fits with the wrong
sign" count for the drift-versus-group-size instrument (§5.1) — the instrument's own interpretation
is disowned in the same paragraph, so nothing rests on the count; and (ii) the `M0 shrink` and
`M1 additive r` pooling failures (§2.4, §5.9), whose replacement is the `zpool` sweep, which **was**
re-derived on `plateau5` and carries that section's argument on its own. No claim in §4 depends on
either.

**A.8 — Corpus size.** The record variously says 1,960 / 2,077 / 2,113 runs and ~1,200–1,400
GPU-hours. At write time: **2,113 rows, 1,671 admissible, 1,582 GPU-hours** summed over the 2,098
runs carrying a wallclock. The correction register has 120 distinct numbered entries running to
number 124 (two number collisions are documented in the register itself and were left in place
rather than renumbered mid-campaign).

---

## Appendix B. The full arm table for the primary contrast

`plateau5` arm means with sem, ResNet-18/CIFAR-10 unless stated, all within batch.

| batch | nodewise | chunk777 | nodewise1d | chunk2325 |
|---|---|---|---|---|
| cc1 | 91.890 ± 0.077 | 92.617 ± 0.185 | 92.706 ± 0.139 | 92.717 ± 0.046 |
| mm1 | 92.044 ± 0.058 | 92.529 ± 0.150 | — | — |
| pp1 | 92.012 ± 0.129 | 92.593 ± 0.058 | — | — |
| pp1 `permnode` (m = 14,420) | 92.003 ± 0.090 | | | |
| bn1 | 92.184 ± 0.033 | — | 92.611 ± 0.025 | 92.906 ± 0.041 |
| gn1 (BN) | 92.000 | 92.587 | — | — |
| gn1 (GN) | 89.330 | 89.532 | — | — |
| ml2 | 92.064 | 92.519 | 92.683 | 92.856 |
| rl3 @1e-4 | 91.908 | 92.589 | 92.664 | 92.653 |
| rl3 @3e-4 | 92.507 | 93.098 | 92.898 | 93.115 |
| fa1 @3e-4 | 92.327 | 92.957 | 92.976 | 92.975 |
| hz3 @300 ep | 92.816 | 93.244 | 93.153 | 93.096 |
| aw1 (AdamW) | 92.978 | 93.257 | 93.069 | 93.301 |
| nl1 (SGD) | 91.156 | 92.191 | 91.848 | 92.373 |
| nl1 (RMSProp) | 92.155 | 93.129 | 93.071 | 93.091 |
| g3m (R34) | 91.336 | 92.002 (chunk835) | 92.094 | 92.265 (chunk2500) |
| r50 (R50) | 89.631 | 90.513 (chunk295) | 90.681 | 90.833 (chunk884) |
| gc1 (C100) | 70.311 ± 0.227 | 71.951 ± 0.092 (chunk771) | — | — |
| gm2 (C100) | 70.569 | 72.054 (chunk771) | 71.932 | 72.000 (chunk2293) |

---

## End matter

**Data availability.** The complete run table (`results/all_runs.csv`, 2,113 rows), the raw
per-epoch training logs, the per-group β probe traces, all submission scripts (`bin/`) and all
scorers (`analysis/`) are held in the project repository and will be released with the paper. No
number in this paper requires data that is not in that release.

**Code availability.** The optimiser patches (`patches/`) apply to the authors' released
MetaOptimize implementation and are released with the paper, each with its identity test against
the authors' own `blockwise` path.

**Ethics.** No human or animal subjects; no personal data. CIFAR-10 and CIFAR-100 are standard
public benchmarks used under their stated terms.

**Competing interests.** One author of this work supervises it and is a co-author of the parent
paper (MetaOptimize). This is disclosed because it is a direct competing interest in the evaluation
of that method: several results here are negative about it, including the 1.807 pp deficit against a
tuned baseline in §7 T4, and the supervising author had no role in setting the pre-registered
decision rules used for the negative results in §5.

**Funding.** [to be completed by the authors at submission.]

**Author contributions.** [to be completed by the authors at submission.]

**Use of AI assistance.** Analysis scripts, batch submission scripts, the correction register and
this draft were produced with substantial assistance from a large language model operating on the
project repository under human direction. Every number in the draft was re-derived from the run
table or the raw logs at the time of writing rather than copied from earlier prose, and the
discrepancies that procedure surfaced are recorded in Appendix A rather than corrected silently.
Registered decision rules and bands were committed to version control before the corresponding runs
were submitted.
