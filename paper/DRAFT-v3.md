# The partition, not the count: a count-matched measurement of step-size granularity in online meta-gradient optimisation — and the mechanism we could not find

**Draft v3.** Every number in this document was re-derived from `results/all_runs.csv` and from the
raw per-epoch `.out` series at the time of writing, under the admissibility gate
`window_ok == 1 AND complete == 1 AND plateau5 present`, and is asserted against what this text
prints by `analysis/c98_reproduce.py`, which exits non-zero if any headline fails to reproduce.
Where a registered scorer exists for a batch it was run **unedited** and its output quoted — including
where its verdict cost us a subsection (§5.6, §7 T7). Numbers that failed to reproduce from the
project's internal record are listed in **Appendix A**, not silently corrected. Four batches are in
flight; their pre-registrations are stated in §3.5 and **no number from any of them enters a claim in
this paper.**

**Meta-analytic convention.** Every pooled estimate, Cochran *Q* and DerSimonian–Laird τ in this
paper is computed from full-precision arm means in the run table, which is what the deposited code
computes and what `make reproduce` re-derives. Computing the same quantities from the
three-decimal (D, se) pairs *as printed in Table 2* gives values that differ in the second decimal
(43.19 → 43.01 on twelve cells; 36.40 → 36.29 on eleven); both are given in Appendix A.4 so that a
referee who recomputes from the printed table alone finds no surprise.

---

## Abstract

MetaOptimize (Sharifnassab, Salehkaleybar & Sutton, ICML 2025) meta-learns one step size per
parameter group and closes by observing that finer partitions help inconsistently: *"while
increasing the number of step sizes is anticipated to enhance performance, our experimental
findings in Section 7 reveal that this improvement is not consistent across the MetaOptimize
approximations evaluated."* We take that question up with 2,113 runs (≈1,582 GPU-hours; 1,671
admissible) on ResNet-10/18/34/50 and CIFAR-10/100, and report one robust measurement, one
bounded null, and a mechanism we could not find.

**The measurement.** Replacing an architecture-aligned partition (one step size per output
channel, `nodewise`) by a uniform one of the *same group count* (fixed-size chunks of K weights)
is worth a positive amount of final accuracy in **every one of 16 within-batch, count-matched
cells we measured**, spanning three networks (ResNet-18, ResNet-34, ResNet-50), 2 datasets,
4 base optimisers, 2 meta-stepsizes and 2 budgets. On ResNet-18/CIFAR-10 with an SGDm base the
effect D = +0.456 ± 0.195 to +0.727 ± 0.200 pp across **six independent batches**; on ResNet-34
D = +0.666 ± 0.094 (9 v 9); on ResNet-50 D = +0.881 ± 0.261; on CIFAR-100 D = +1.640 ± 0.245 and
+1.485 ± 0.238. Over the eleven cells that run the same ResNet-18 partition contrast, D varies
genuinely across configurations (**Q = 36.4 on 10 df, p = 7.2e-5**, τ = 0.203 pp against 0.152 pp
rms measurement error) — and **88% of that variation is one identified moderator, the base
optimiser** (between-base Q = 32.2 on 3 df, p = 4.8e-7). At a fixed base the effect is homogeneous:
over eight SGDm cells spanning seven separate submissions, two meta-stepsizes, two budgets and three
step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76, τ = 0.000).

**The bounded null.** Architecture *alignment* is not a large carrier, and we can put a number on
how large it could still be. Permuting **which** weights share a group while holding the group
count **and the exact per-tensor group-size multiset** fixed is worth **−0.009 ± 0.157 pp
(t −0.06, 3 v 3, one batch)**, scored `NULL` against a symmetric band registered in advance. The
95% interval is **[−0.317, +0.298] pp = [−55%, +51%] of the same batch's D**, and the effect this
design could have detected at 80% power is **0.440 pp = 76% of D**. So an alignment effect
accounting for most of D is excluded; one accounting for half of it is **not** — power against
A = D/2 is 0.46. We also record a defect in our own registration: the NULL band's half-width (0.15)
is **narrower than the standard error the batch achieved** (0.157), so a genuinely zero effect would
have scored `NULL` only 66% of the time. What is left as the leading carrier is the group-**size
distribution**, which takes **+0.590 ± 0.107 (t 5.53)** of the same decomposition.

**What we could not find.** We examined eight candidate mechanisms and refuted three of them,
narrowed a fourth to one base optimiser, found a fifth not separable from the axes it is aliased
with, and found the remaining three undecidable by this instrument or this design; we report all
eight, because they are half the contribution. Chief among them: the obvious carrier — degenerate
size-1 groups — is not it (removing 100% of a network's singletons buys +0.115 ± 0.133 pp, t 0.87);
the tail story is base-specific (pooled D − G = +0.514 ± 0.056 under SGDm, +0.047 ± 0.124 under
AdamW); no summary statistic of the size distribution is *identifiable* from this corpus, because at
fixed count the design contains exactly one contrast type and every candidate collapses to an
indicator for the aligned arm; and **no measurable property of a configuration predicts D out of
sample** better than the corpus mean by a margin that survives the power bound (|r| ≥ 0.632 needed
at 10 design points).

**Scope, stated here and not deferred to a threats section.** (i) Everything is CIFAR-resolution
vision with ResNets and one meta-learning framework; ImageNet is out of reach on our data
allocation (489 of 1000 train classes present, validation set unlabelled). (ii) MetaOptimize trails
a tuned schedule at every scale we ran: on ResNet-18 its best plain cell reaches 93.317 ± 0.083 pp
against a tuned SGD+cosine baseline at 95.124 ± 0.047 (n=5, the interior maximum of a bracketed
grid), a **1.807 pp deficit**, and the deficit widens to 2.56 pp on ResNet-34 and 4.21 pp on
ResNet-50. We make no competitiveness claim. (iii) All 367 partition-programme runs reported here
use a **Lion** meta-optimiser; the base optimiser has been varied four ways, the meta-optimiser never
— a batch that was to fix this ran a different experiment from the one it declared (§6.1), and the
replacement is in flight (§3.5). (iv) The effect is ≈0.6 pp inside a method that is 1.8 to 4.2 pp
behind a cosine schedule. (v) Every accuracy here is a test-set quantity and no validation split was
held out anywhere (§3.3, §7 T12). (vi) We inherit, and partly overlap with, Choi et al. on
tuning-protocol sensitivity, Zheng & Kwok on blockwise adaptivity, and CAM-HD on the granularity
ladder and its interior optimum; §2 states exactly what is left.

**Four pre-registered batches are in flight** and are described in §3.5 with their decision rules,
because three of them exist to repair specific weaknesses this paper states about itself: the
alignment null's power and its permutation-seed confound (`rp1`), the one budget cell's clip-box and
hardware mismatch (`hz3`-R2), the base-optimiser moderator's single-batch levels (`bm2`), and the
second-moment corner that §6.1's void batch failed to test (`sm4`). None of them contributes a
number to this draft.

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
last. The result is robust — 16 cells, every one positive, three networks, two datasets, four
base optimisers — and eight separate candidate explanations for it have now been examined: three
are refuted, one survives only under an SGDm base, one is not separable from the network and
base-optimiser axes it is aliased with, and three cannot be decided by this instrument or this
design at all. Of the three refutations, one rests on a gate registered before its data existed
(§5.2) and two are post-hoc contrasts on data collected for other purposes (§5.3, §5.5), which we
say rather than leave to inference. A cross-validated *null* at n = 10 is defensible in a way a
cross-validated success at n = 10 never is; we report both, and the null is the one that survives.

### 1.1 Contributions

1. **A count-matched isolation of the group-size distribution from the group count** in
   meta-learned step sizes, replicated in 16 within-batch cells across three networks, 2 datasets
   and 4 base optimisers (§4.3–§4.5, Table 2, Figure 1).
2. **A pre-registered permutation null, reported with its resolution**: at fixed count *and* fixed
   per-tensor size multiset, membership is worth −0.009 ± 0.157 pp, 95% CI [−0.317, +0.298] =
   [−55%, +51%] of D, MDE 0.440 pp. This **bounds** alignment's contribution rather than
   eliminating it, in one batch at one design point, and we report the registration defect that
   limits it (§4.6).
3. **An identified moderator for the effect's heterogeneity**: the base optimiser carries 88% of
   the between-cell Cochran Q, and inside a fixed base D is homogeneous (τ = 0.000, 95% upper limit
   0.109 pp) across seven submissions, two meta-stepsizes, two budgets and three clip boxes
   (§4.4, Figure 2).
4. **A ranking of the four variables** that "the number of step sizes" conflates, with the
   within-batch magnitude of each (§4.1–§4.2).
5. **Eight candidate mechanisms — three refuted, one narrowed to a single base optimiser, one not
   separable, three undecidable by this design — and two nulls**, reported as a section rather than
   an appendix (§5), including the identifiability limit that makes a ninth unanswerable from this
   corpus.
6. **A practitioner prescription with its scope attached**: merging each one-dimensional tensor
   into a single group is worth **+0.328 ± 0.084 to +1.363 ± 0.151 pp** across ten within-batch
   cells under SGDm, SGD and RMSProp bases, and costs nothing — but under an AdamW base it is
   worth +0.091 ± 0.078, i.e. nothing measurable (§4.7, §5.4).
7. **A measurement-discipline appendix** documenting a batch that failed silently on its own axis,
   a metric column that produced two withdrawn headlines, an argument-line defect that voided two
   batches, and an internal variance claim that did not reproduce (§6, Appendix A).

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
| **Adam-mini** (arXiv:2406.16793) | Algorithm 3, *Partition for non-Transformers*, is verbatim `for name, param in parameters: param_blocks[name] = param` — **one block per tensor**. On a ResNet, Adam-mini is layerwise and already ships our prescription. | Its stated principle is Hessian sub-block **alignment**. Our permutation null (§4.6) bounds what that principle can be buying in this regime — at fixed count and fixed per-tensor size multiset, membership is worth −0.009 ± 0.157 pp, 95% CI [−0.317, +0.298] — which excludes a large alignment effect within one layer at one design point and does not exclude a moderate one. |
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

Write $\mathcal{P}$ for a partition of the network's weights into $m$ step-size groups
and $\mu(\mathcal{P})$ for the mean `plateau5` of the arm that trains under it, taken over
the seeds of one batch. All four differences below are **within batch** and
**count-matched by construction**.

The primary contrast replaces an architecture-aligned partition by a uniform one at the
same group count:

$$
D \;=\; \mu(\texttt{chunk777}) \;-\; \mu(\texttt{nodewise}),
\qquad m = 14{,}421 \ \text{vs}\ 14{,}420
\tag{1}
$$

— one group apart, $3\times10^{-5}$ decades of count. The same contrast with the
degenerate size-1 tail **already removed from both arms**, count-matched exactly, is

$$
G \;=\; \mu(\texttt{chunk2325}) \;-\; \mu(\texttt{nodewise1d}),
\qquad m = 4{,}851 \ \text{exactly}
\tag{2}
$$

so that $D - G$ is the tail's contribution and, being a difference of two within-batch
differences taken in the same batch, carries no cross-batch floor. The alignment leg holds
the count *and* the exact per-tensor group-size multiset and randomises only which weights
share a group, within each tensor:

$$
A \;=\; \mu(\texttt{permnode}) \;-\; \mu(\texttt{nodewise}),
\qquad m = 14{,}420,\ \ \text{size multiset identical}
\tag{3}
$$

The pure count axis holds the partition *family* fixed and moves only $m$:

$$
U \;=\; \mu(\texttt{chunk2325}) \;-\; \mu(\texttt{chunk777}),
\qquad \log_{10}\!\big(14{,}421/4{,}851\big) = 0.4732\ \text{decades}
\tag{4}
$$

and the practitioner's move — merge each one-dimensional tensor into a single group — is

$$
T \;=\; \mu(\texttt{nodewise1d}) \;-\; \mu(\texttt{nodewise}).
\tag{5}
$$

$T$ is count-confounded by construction, and the confound is exact rather than
approximate:

$$
T \;=\; (D - G) \;+\; U .
\tag{6}
$$

Two further identities are used and are exact by construction, not by fitting. With
$B = \mu(\texttt{chunk777}) - \mu(\texttt{permnode})$,

$$
A + B \;=\; D ,
\tag{7}
$$

which is what licenses reporting alignment and size-distribution as *shares* of one
effect in §4.6.

Every difference in (1)–(5) is reported with a Welch standard error formed from the two
arms' own variances, never from a pooled or an assumed one:

$$
\widehat{\mathrm{se}}(\mu_1-\mu_2)\;=\;\sqrt{\frac{s_1^{2}}{n_1}+\frac{s_2^{2}}{n_2}}\,,
\qquad t=\frac{\mu_1-\mu_2}{\widehat{\mathrm{se}}} .
\tag{8}
$$

Because a percentage point is not comparable across error budgets, the commensurable
companion to $D$ is the share of the aligned arm's remaining error that it removes:

$$
\rho \;=\; \frac{D}{100 - \mu(\texttt{nodewise})} .
\tag{9}
$$

Figure 1(b) plots $\rho$; §4.3 states, and this paper obeys, the rule that CIFAR-10 and
CIFAR-100 values of $D$ are never averaged and never placed on one percentage-point axis.

On ResNet-34, ResNet-50 and ResNet-18/CIFAR-100 the count matching in (1) is close but not
exact: chunk835 25,562 vs nodewise 25,556 (R34); chunk295 79,796 vs 79,700 and chunk884
26,715 vs 26,677 (R50); chunk771 14,595 vs 14,600 and chunk2293 4,943 vs 4,941 (C100). The
largest mismatch, 0.14% of the count, is 685× below the resolution floor at the measured
count slope.

**A structural caveat specific to ResNet-50.** Its largest 1-D tensor has 2,048 elements,
which exceeds K = 295, so `chunk295` **splits** some 1-D tensors across groups instead of
giving each one a single group. It still contains no size-1 group (min group size 10).
ResNet-18, ResNet-34 and ResNet-18/CIFAR-100 all have largest 1-D tensor 512 < K, so their
chunk arms give each 1-D tensor exactly one group. The ResNet-50 $D$ is therefore a
slightly different object and is reported as such.

### 3.3 Metric, admissibility, multiplicity, and units of replication

**Metric.** For a run $r$ that completed $E_r$ test epochs with accuracies
$a_r(1),\dots,a_r(E_r)$, the primary metric throughout is

$$
\texttt{plateau5}(r)\;=\;\frac{1}{5}\sum_{e=E_r-4}^{E_r} a_r(e).
\tag{10}
$$

The 20-epoch analogue $\frac{1}{20}\sum_{e=E_r-19}^{E_r} a_r(e)$ is present in the corpus
as the CSV's `plateau` column and is **not used**: two of this project's headlines were
withdrawn for quoting it (Appendix A.2), and it is banned as a primary.

**Admissibility.** A run enters an analysis iff

$$
\mathrm{adm}(r)\;=\;\big[\,\texttt{window\_ok}(r)=1\,\big]\ \wedge\
\big[\,\texttt{complete}(r)=1\,\big]\ \wedge\
\big[\,\texttt{plateau5}(r)\ \text{readable}\,\big],
\tag{11}
$$

where $\texttt{window\_ok}(r) = [\,E_r > 20\,]$ — the tail in (10) must be a genuine
plateau and not most of a short probe — and
$\texttt{complete}(r) = [\,E_r \ge 0.95\,E^{\mathrm{req}}_r\,]$. The second condition is not
redundant: **17 of 2,113 runs pass `window_ok` while having completed under 95% of their
requested epochs** (16 of the 17 finished under 90%; the seventeenth stopped at 94 of 100).
The worst of them, `rs-blk6-1e4-s2`, ran 29 of 100 epochs and still reports `plateau5`
85.228; it sits in a `resnet18_blocks` arm of the `rs` meta-stepsize sweep, where including
it moves that arm's mean by 1.22 pp and inflates its sem 19-fold. **None of the 17 is in a
count-matched arm** — see the attrition ledger in §8, where attrition inside the primary
contrasts is zero. Of 2,113 rows, **1,671 are admissible**.

**Selection on the test set, stated in full.** **No validation split was held out anywhere in
this project.** CIFAR-10 and CIFAR-100 ship a 50,000/10,000 train/test split; we trained on
the 50,000 and evaluated on the 10,000, and `plateau5` is a mean of five of those test
evaluations. Every tuning decision in this paper was therefore made on the same 10,000 images
the paper reports accuracy on. Six places where that matters:

1. **The metric is the test set.** Every accuracy in this paper, including both numbers in
   §7 T4, is a test accuracy with no held-out estimate behind it.
2. **The operating point.** η = 1e-4 and α₀ = 1e-3 were chosen because both arms score better
   there (§4.1). `D` depends on η at −0.189 pp per decade within batch (§4.5), so `D` is
   reported at a test-selected operating point, not at a random one.
3. **§4.5's per-arm optima** are argmaxes over a two-rung η ladder taken on the same test
   accuracies that define `D`.
4. **§7 T4's absolute numbers are all argmaxes**: the MetaOptimize cell is the maximum of
   a seven-rung α₀ ladder and the baseline the maximum of a four-rung learning-rate grid, both
   scored on the test set.
5. **The β-box** was widened between batches in response to observed clipping, which is an
   analysis-affecting choice made after seeing runs (*Box occupancy* below, §6).
6. **The metric window.** `plateau5` was made primary after the 20-epoch column produced two
   withdrawn headlines (Appendix A.2). The choice has a mechanical justification — a
   trailing window longer than the plateau contains the mid-training trough of §4.8 at short
   budgets and not at long ones — and it has been applied uniformly since, but it was not
   fixed before the first analysis.

Over the campaign, **418 distinct admissible configuration cells** were scored on that test
set. Two consequences, and we separate them because they are not the same size.
**For absolute accuracies the effect is the usual one and it is not small**: every level in
this paper should be read as an optimistic, selection-inflated estimate, and we make no
claim that any of them would survive on a genuinely held-out split.
**For the contrasts it is much smaller, and for a structural reason**: `D`, `G`, `A`, `T` and
`U` are differences between two arms trained and evaluated identically inside one batch,
and **no arm and no cell was ever selected** — §4.3 shows that every count-matched contrast
the corpus contains is reported, including the one that is excluded. What is selected is the
operating point at which the contrast is measured, not the contrast. A reader should read
`D` as "the effect at a tuned operating point", which is the setting a practitioner
is in, and should not read any absolute accuracy in this paper as a benchmark result.

**Box occupancy.** β is clipped to a box, and a run at a guard is uninterpretable. Occupancy is read
**per coordinate and per seed**, never from a per-tensor summary — reading the 62-element summary
instead reported 0.000000 occupancy on 24 runs that were clipped in every record and inverted an
arm ranking, which voided one batch (`ar1`, excluded from every primary here). The scorers report
`rec_lo`/`rec_hi` per run; all `cc1`, `mm1`, `pp1` and `bn1` arms read 0.0000 on both guards. The
box is **not** constant across cells: the eleven-cell pool of §4.4 spans three boxes, and one cell
(`hz3`) contains a single seed whose two arms sit in *different* boxes (§7 T9, §4.8).

**Unit of replication.** Every primary contrast is taken **within one batch** (one contiguous
submission), so any offset shared by the two arms cancels identically. §6.3 reports what we can and
cannot say about the size of such offsets. Two cells are exceptions to "one contiguous submission"
and are marked as such in Table 2: the two `rl3` rungs and the two `nl1` bases each share a batch,
and `hz3` is *two* submissions 32,288 job ids apart.

**Heterogeneity.** Across $k$ cells with estimates $y_i$ and standard errors
$\mathrm{se}_i$, writing $w_i = \mathrm{se}_i^{-2}$ and
$\bar{y} = \sum w_i y_i / \sum w_i$, we report Cochran's

$$
Q\;=\;\sum_{i=1}^{k} w_i\,(y_i-\bar{y})^2
\quad\text{on } k-1 \text{ df},
\qquad
\hat\tau^{2}=\max\!\left(0,\ \frac{Q-(k-1)}{\sum w_i-\dfrac{\sum w_i^{2}}{\sum w_i}}\right)
\tag{12}
$$

(DerSimonian–Laird), and, where a moderator is claimed, the exact partition of $Q$ into
its within-level and between-level parts, $Q = Q_{\mathrm{within}} + Q_{\mathrm{between}}$
with degrees of freedom adding likewise. Figure 2(b) is that partition.

**Multiplicity.** One family of tests in this paper is large enough that an uncorrected
nominal α would be misleading: the secondary contrast `G`, which is measured once in every
count-matched cell. We declare the family — the `G` leg of every cell in Table 2 that has
one, twelve tests — and report Holm–Bonferroni step-down adjusted p-values for all twelve in
§5.4. The primary `D` is **not** corrected and is not presented as a family of hypothesis
tests: it is one quantity estimated in sixteen cells, reported as sixteen intervals and
pooled once, and the claim made of it is "positive in every cell", not "significant in *k*
cells". Where a p-value is quoted anywhere in this paper it is two-sided; at n = 3 v 3 we
give the Welch–Satterthwaite value as primary and the normal approximation alongside it,
because the two differ materially at 2–4 degrees of freedom and the paper's `t` columns are
the normal-approximation quantity.

**Duplicate runs.** Eighteen pairs of differently-named runs in the corpus resolve to the same
experiment — the same effective argument line *including* `--seed`. The run table carries a
`dup_group` column marking them, and the rule the column encodes is: **any n, se or t computed
over rows sharing a `dup_group` averages within the group first and counts n as the number of
distinct groups.** Twelve of the eighteen pairs are `ml2`'s, which is why `ml2` is a 3 v 3 cell
with se 0.195 and not a 6 v 6 cell with se 0.142 (§6.1).

### 3.4 Registration discipline

Where a batch has a scorer committed before its runs existed, that scorer is run **unedited** and
its printed verdict is quoted rather than paraphrased. This rule exists because it was broken: two
cycle-91/92 headlines were withdrawn after being produced by reductions hand-written at read time
(Appendix A.2). The scorers used here are `analysis/c76_mm1_score.py`, `c77_pp1_score.py`,
`c78_bn1_score.py`, `c81_cc1_score.py`, `c82_fa1_score.py`, `c83_gc1_score.py`,
`c87_rl3_score.py`, `c87_hz3_score.py`, `c88_scorers.py` (committed at `5129e74`, before any
`ub9`/`aw1` run existed; md5 `0363bcccb4d3bbad50beb19c9281b9be`), and `c84_gn1_score.py`
(md5 `82c515d1ad490228ecb20f83288a510f`), **which halted `gn1` at its commensurability gate and
issued no verdict; we report that outcome rather than the contrast it declined to compute
(§5.6, §7 T7).**

This list is a list of the scorers we *have*, not a claim of coverage. **Five batches behind
material reported in this paper have no scorer that was registered before their runs existed** —
`ml2`, `nl1`, `r50`, `gm2` and `sm3` — and the per-batch provenance table in §8 marks each one.
`nl1` is the serious case: it supplies two of Table 2's rows and both of the single-batch levels
of the base-optimiser moderator in §4.4, so the newest headline's weakest flank is also its
unregistered one. Their run-table values were reconciled field-by-field against their own runs'
`ARGS:` lines with zero mismatches; what is missing is not the data but the
commitment-before-the-fact, and the replication that repairs it is in flight (§3.5).

Every figure in this paper is generated by `analysis/c98_figures.py` directly from
`results/all_runs.csv` and the raw `.out` series; `--numbers` prints each plotted value,
and `analysis/c98_reproduce.py` re-derives every number in the text and asserts it
against what is printed here. **No figure contains a value that was typed.**

### 3.5 Four pre-registered batches in flight

Three weaknesses this paper states about itself, and one experiment it declares was never run, are
addressed by four batches submitted while this draft was being written. **No result from any of
them enters any claim in this paper**; their registrations are stated here so that the decision
rules are on the record before the numbers are, and so that a reader can tell what this paper would
be entitled to say next and what it would not.

Every one of the four was submitted under the two rules that the failures in §6.1 paid for:
**STANDING RULE 20** — a batch's science is what the runs' own `ARGS:` line says, never what the
submission script's header claims — enforced by `analysis/argsline_guard.py` and
`bin/_lib_guards.sh` before and after launch; and **STANDING RULE 21** — no batch is submitted
without a scorer that already exists, whose selftest already passes, and whose sha256 is recorded.

| tag | batch | jobs | what it repairs | registered scorer |
|---|---|---|---|---|
| R1 | `rp1` | 24 | the alignment null's power **and** its permutation-seed confound (§4.6) | `analysis/c97_rp1_score.py` |
| R2 | `hz3` seed-5 trio | 3 | the budget cell's clip-box and GPU-class mismatch (§4.8, §7 T9) | `analysis/c87_hz3_score.py`, reused unedited |
| R3 | `bm2` | 12 | the base-optimiser moderator's single-batch SGD and RMSProp levels (§4.4) | `analysis/c97_bm2_score.py` |
| R4 | `sm4` | 12 | the second-moment corner the void batch of §6.1 failed to test | `analysis/c97_sm4_score.py` |

**R1 — `rp1`, the alignment replication and the two-way variance decomposition.** `nodewise` × 6
fresh run seeds plus `permnode{101,202,303}` × the same 6 seeds, fully crossed: 24 jobs at `pp1`'s
own cell (ResNet-18/CIFAR-10, SGDm + Lion, η = 1e-4, α₀ = 1e-3, 100 epochs, box −15:−2.3026). The
permutation seed is an explicit constant **decoupled from the run seed**, which `pp1` could not do
(§4.6, limit 2), and the guard asserts on the live tree that each draw reproduces `nodewise`'s
per-tensor size multiset exactly, is a true non-identity permutation, differs from the other two
draws, and coincides with none of `pp1`'s. Registered in advance: the design takes se(A) from 0.157
to ≈0.09 and the minimum detectable effect from 0.440 pp to ≈0.25 pp — below half of D and inside
the pre-registered band for the first time — and yields a permutation-draw × run-seed variance
decomposition. **Also registered in advance, and this is the part that binds us**: *if `rp1`
returns an interval that still spans half of D, the alignment leg is to be reported as
**underdetermined**, not as a null.* The scorer additionally prints `pp1`'s registration defect
(band half-width 0.15 < realised se 0.157) whichever way the new data land.

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

**R3 — `bm2`, the base-moderator replication.** One submission, four arms (`SGD`/`RMSProp` ×
`nodewise`/`chunk777`), three **fresh** seeds (3, 4, 5 against `nl1`'s 0, 1, 2), 12 jobs at `nl1`'s
own cell taken from `nl1`'s own `ARGS:` line. Independence is bought twice — a separate submission,
so the batch random effect is resampled, and fresh seeds, so the `ml2` failure mode (two
"independent" halves that shared their seeds) cannot recur. Registered bands, committed before the
runs existed: `REPLICATES` if D′ ≥ 0.30 and t ≥ 2; `FAILS TO REPLICATE` if D′ ≤ 0.15 **and**
se ≤ 0.15; `UNDECIDED` otherwise; agreement with `nl1` if |D′ − D_nl1| ≤ 0.5, the unmodelled
cross-batch offset. The registration also states, in advance, that **the powered-null branch is
unreachable on the planning noise** — se(D′) = 0.194 exceeds the 0.15 the null branch requires — so
a small D′ must read `UNDECIDED` and may not be written up as a refutation. That sentence exists
because this project has already published an underpowered null as a refutation once (§4.6).

**R4 — `sm4`, the second-moment corner, properly composed.** AdamW base × **RMSProp** meta at four
granularities × 3 seeds, 12 jobs: the cell that `sm3` declared and did not run (§6.1). The payload
is built once in a single shell array and handed to `sbatch` unmodified, so the `$BFLAGS`-then-append
shape that voided both `ml2` and `sm3` is absent by construction; the first launched job's own
`ARGS:` line was read off the cluster and carries **exactly one** `--alg-meta`, reading `RMSProp`,
and the runtime prints neither of the attribute-mismatch warnings that `sm3` printed. Registered in
advance against anchors re-derived at write time (`aw1` D +0.279 ± 0.087, `sm3` D +0.141 ± 0.064,
pooled AdamW + Lion D +0.210 ± 0.056): **REFUTED** if D ≥ +0.55; **CONSISTENT** if D ≤ +0.279 and
the 95% upper bound is below +0.55; **UNDECIDED** otherwise, in which case the registration forbids
adding seeds to this batch and requires a fresh registered replicate instead. A blocking
operating-point gate fires first: an RMSProp meta-optimiser has never run anywhere in this corpus
and its meta-stepsize was matched to `aw1` rather than tuned, so if the 12-run mean `plateau5` lands
more than 3.0 pp from the 93.161 anchor **every contrast in the batch is demoted to descriptive and
labelled off-anchor** — reported, never discarded.

**Status at the time of writing, stated because "in flight" is not a uniform state.** `rp1` and
`sm4` are running; the R2 trio is queued behind a congested partition, and the original `hz3`
seed-3 and seed-4 runs waited 16 and 23 hours in the same queue, so a wait is expected rather than
anomalous. `bm2`'s twelve jobs have **completed**, 100/100 epochs each, after this draft's numbers
were frozen; it has not been scored, and it will be scored by running
`analysis/c97_bm2_score.py` unedited and quoting its verdict. We state that plainly rather than
letting a completed batch sit unmentioned: the reason no `bm2` number appears in this paper is a
freeze date and a registration, not a filter.

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
the parent's blockwise-beats-scalar step reproduces at **+0.522 ± 0.207** and the *next* rung reverses
it at **−0.903 ± 0.215**.
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
| cc1 | +0.101 ± 0.190 | ml2 | +0.337 ± 0.112 |
| rl3 @1e-4 | +0.064 ± 0.154 | g3m (R34) | +0.263 ± 0.074 |
| rl3 @3e-4 | +0.017 ± 0.098 | r50 (R50) | +0.321 ± 0.259 |
| fa1 | +0.019 ± 0.094 | gm2 (C100) | −0.054 ± 0.196 |
| hz3 (300 ep) | −0.148 ± 0.080 | nl1/SGD | +0.182 ± 0.283 |
| aw1 (AdamW) | +0.045 ± 0.097 | nl1/RMSProp | −0.037 ± 0.085 |

U changes sign across cells and its magnitude never exceeds +0.34 pp — smaller than D in every cell where both
are measured, and of the opposite sign in two. (`ml2`'s entry is computed on its three seed groups, not its
six runs, per §3.3: on six runs it would read ± 0.088 rather than ± 0.112.) **No single count slope exists to import**, and any count correction must be measured in the batch and at the budget being
corrected.

### 4.3 The primary: at fixed group count, the partition matters

**Table 2 — D (Eq. 1) = uniform chunk − architecture-aligned nodewise, count-matched, within batch,
`plateau5`.** Welch difference of arm means (Eq. 8); se from the two arm variances. Every cell is a
separate contiguous submission except the two `rl3` rungs and the two `nl1` bases, which share a
batch, and **`hz3` (row 9), which is two submissions 32,288 job ids apart, in two clip boxes and on
two GPU classes** — see §7 T9. The β-box column matters in §4.4: the pool spans three boxes, and box
is shown there not to be a moderator.

| # | batch | network | dataset | base | η | epochs | β-box | n | **D (pp)** | se | t |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | cc1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.727** | 0.200 | 3.63 |
| 2 | mm1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.485** | 0.161 | 3.01 |
| 3 | pp1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.581** | 0.141 | 4.11 |
| 4 | gn1 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | −15:−2.3026 | 4 v 4 | **+0.587** | 0.153 | 3.83 |
| 5 | ml2 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 (×2 reruns) | **+0.456** | 0.195 | 2.34 |
| 6 | rl3 | ResNet-18 | C10 | SGDm | 1e-4 | 100 | −30:9.0 | 3 v 3 | **+0.681** | 0.173 | 3.93 |
| 7 | rl3 | ResNet-18 | C10 | SGDm | 3e-4 | 100 | −30:9.0 | 3 v 3 | **+0.591** | 0.096 | 6.18 |
| 8 | fa1 | ResNet-18 | C10 | SGDm | 3e-4 | 100 | −25:−2.3026 | 6 v 6 | **+0.629** | 0.123 | 5.11 |
| 9† | hz3 | ResNet-18 | C10 | SGDm | 1e-4 | **300** | −30:9.0 (one seed at −15:−2.3026) | 6 v 6 | **+0.428** | 0.086 | 4.94 |
| 10 | aw1 | ResNet-18 | C10 | **AdamW** | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.279** | 0.087 | 3.19 |
| 11 | nl1 | ResNet-18 | C10 | **SGD** | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+1.035** | 0.109 | 9.54 |
| 12 | nl1 | ResNet-18 | C10 | **RMSProp** | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.973** | 0.251 | 3.87 |
| 13 | g3m | **ResNet-34** | C10 | SGDm | 1e-4 | 100 | −15:−2.3026 | 9 v 9 | **+0.666** | 0.094 | 7.08 |
| 14 | r50 | **ResNet-50** | C10 | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.881** | 0.261 | 3.37 |
| 15 | gc1 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | −15:−2.3026 | 4 v 4 | **+1.640** | 0.245 | 6.71 |
| 16 | gm2 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+1.485** | 0.238 | 6.24 |

† `hz3`'s seed-5 `chunk777` run sits in a narrower clip box and on a different GPU class from its
`nodewise` partner (§7 T9). The matched 5 v 5 reading is **+0.455 ± 0.096, t 4.75**; the cell's
sign, magnitude and resolution are unchanged, the difference being 0.027 pp against a 0.086 pp se.
Run R2 (§3.5) restores a matched 6 v 6.

**Row 5's `n` is three, not six.** `ml2`'s two nominal halves are the same effective command line
*including* `--seed`, so the batch is three seeds run twice rather than six seeds (§6.1). The point
estimate is unaffected; the standard error is 0.195 rather than 0.142 and the *t* is 2.34 rather
than 3.20.

**D is positive in every cell.** Fifteen of the sixteen are resolved at t ≥ 3.0; the exception is
`ml2` at t 2.34, whose three independent seeds were run twice under two names. A further cell
(`ar1`, D = +0.697 ± 0.118) is **excluded** as box-void — it bound on the guards asymmetrically, in
the direction that inflates D — and is reported here only so that its exclusion is visible. A
**seventeenth** contrast exists and is also excluded: `gn1`'s ResNet-18/GroupNorm arms. Its
registered scorer's commensurability gate fired (BatchNorm error budget 7.707 pp against GroupNorm's
10.569 pp, ratio 1.37×, registered bar 2.0 pp) and the scorer printed **"NO TRANSFER VERDICT IS
ISSUED … THIS IS NOT A NULL"** before reaching the contrast at all. We therefore quote no D for it
here or anywhere else; its arm means are in Appendix B and its role in the design is discussed under
T7 in §7. Consequently **every cell in this paper uses BatchNorm.**

**Table 2 together with the excluded `ar1` cell is the complete set of count-matched
`nodewise`-versus-uniform-chunk contrasts in this corpus. None is omitted, and the excluded one is
also positive.** We verified this by enumeration rather than by recollection: of the 2,113 runs,
every batch that ever ran a `nodewise` arm alongside a count-matched uniform-chunk arm is one of
these eighteen (the sixteen above, `gn1`-GroupNorm, and `ar1`), and every other batch carrying a
`nodewise` arm has no arm to match it against. The enumeration also shows that no such cell could
have been lost to the admissibility gate: all 214 uniform-chunk, `nodewise1d` and `permnode` runs in
the corpus are admissible, and the sixteen batches involved contribute 272 runs of which 272 are
admissible (§8, Table 3). Two further count-matched contrasts exist in the corpus and are reported
elsewhere in this paper rather than in Table 2, because neither yields a `D`: `bn1` ran `nodewise1d`
and `chunk2325` at m = 4,851 without a `chunk777` arm, giving G = +0.295 ± 0.048 and no `D` (§5.4),
and `pp1`'s `permnode` arm is the alignment leg `A` at m = 14,420 (§4.6). There is no third.

**A commensurability warning we obey.** A percentage point is not comparable across error budgets.
ResNet-18/CIFAR-10 sits on a ≈7–8 pp budget and CIFAR-100 on ≈29–30 pp. On **relative** error
reduction (Eq. 9) CIFAR-100's +1.640 pp is D/headroom = 0.055, the **smallest** value among the
cells, not the largest. We therefore never average CIFAR-10 and CIFAR-100 D's, and never plot them
on one axis. The rule is worth something measurable rather than being a stylistic preference:
adding a single CIFAR-100 cell to the percentage-point `D − G` pool of §5.4 moves the estimate by
+0.044 pp and multiplies its Cochran Q from 4.52 on 7 df to 17.17 on 8 df.

![Figure 1](figures/f1_forest_D.png)

**Figure 1 — D in every count-matched cell, and the same effect made commensurable.**
(a) D = uniform chunk − architecture-aligned nodewise, `plateau5`, taken within batch,
with 95% intervals from the Welch standard error of Table 2. Colour is the base
optimiser, marker shape the dataset, marker size the network depth. **D is positive in
every one of the sixteen cells.** The horizontal rule separates CIFAR-10 from
CIFAR-100: the two sit on ≈7–8 pp and ≈29–30 pp error budgets and a percentage point does
not mean the same thing across it, so panel (a) must not be read across the rule.
(b) The same sixteen contrasts as a share of the aligned arm's remaining error,
ρ = D / (100 − aligned) (Eq. 9), which *is* commensurable. On that scale CIFAR-100's +1.640 pp is
0.055 — the **smallest** value in the corpus, not the largest. The inset
gives the fixed-effect pool over the eleven cells that run the same ResNet-18 partition contrast.

### 4.4 The heterogeneity is one identified moderator: the base optimiser

Restrict Table 2 to the eleven cells that run the same ResNet-18 partition contrast
(`nodewise` → `chunk777`, count-matched to +1 group on 14,420; rows 1–4 and 6–12) so that the
contrast itself is held fixed. Those eleven are heterogeneous: the fixed-effect pool is
+0.571 ± 0.037 with

> **Q = 36.40 on 10 df, p = 7.2e-5**; DerSimonian–Laird **τ = 0.203 pp** against an rms measurement
> se of **0.152 pp**, i.e. I² = 72%.

That much the record already carried. What it did not carry is that **almost all of it is one
variable.** Split the eleven cells by the base optimiser, the axis §5.5 was already looking at:

| base optimiser | base state, from the runs' own `ARGS` line | cells | batches | pooled D (pp) |
|---|---|---|---|---|
| SGD | no momentum, no second moment | 1 | 1 | **+1.035 ± 0.109** |
| RMSProp | second moment 0.999, no momentum | 1 | 1 | **+0.973 ± 0.251** |
| SGDm | momentum 0.99, no second moment | 8 | 7 | **+0.556 ± 0.045** |
| AdamW | momentum 0.9 + second moment 0.999 | 1 | 1 | **+0.279 ± 0.087** |

**Between base optimisers, Q = 32.20 on 3 df (p = 4.8e-7) — 88% of the total.** The remaining 12%
is the within-SGDm residual, and it is not resolvable at all:

> Over the eight SGDm cells — **seven separate submissions, two meta-stepsizes (1e-4, 3e-4), two
> budgets (100 and 300 epochs), three β-boxes and two clusters** — the pool is **+0.556 ± 0.045**
> with **Q = 4.21 on 7 df, p = 0.76, I² = 0%, τ = 0.000** (one-sided 95% Q-profile upper limit
> **0.109 pp**, below the 0.146 pp rms measurement se of the cells themselves).

Four of those eight are independent submissions of the *identical* configuration and land at
+0.727, +0.485, +0.581 and +0.587 — Q = 0.89 on 3 df, p = 0.83. Leave-one-cell-out over the eight
never resolves heterogeneity (Q 1.21–4.17 on 6 df, pool +0.544 to +0.603; τ = 0.000 in all eight subsets), and no other
axis available inside the subset competes with the base: β-box Q = 0.76/2 (p 0.68), meta-stepsize
Q = 0.68/1 (p 0.41), budget Q = 2.99/1 (p 0.084), cluster account Q = 0.76/1 (p 0.38).

**These eleven cells are not one configuration, and we do not call them one.** They span three
step-size clip boxes — `−15:−2.3026` (7 cells), `−30:9.0` (3), `−25:−2.3026` (1) — and
`analysis/c87_rl3_score.py`'s registered header forbids pooling across boxes, on the ground that a
box change moves the optimiser and not merely the instrument. We pool anyway, and we justify it by
measurement rather than by assertion: partitioning Q by box gives **between-box Q = 1.08 on 2 df
(p = 0.58)** against **within-box Q = 35.32 on 8 df**. The box carries none of the heterogeneity, and
the same partition on the twelve-cell pool that used to include the GroupNorm cell gives
between-box Q = 0.60 on 2 df. A `β-box` column is carried in Table 2 and in Appendix B so the
reader can redo this split.

So the finding is not "D varies for reasons we cannot attribute". It is:

> **At a fixed base optimiser, D is a constant.** Under SGDm it is +0.556 ± 0.045 pp and it does
> not move with the meta-stepsize, the budget, the β-box, the cluster or the batch. **Between base
> optimisers it moves by a factor of 3.7**, and that single axis accounts for 88% of the observed
> heterogeneity.

**Say which denominator.** The between-base Q of 32.20 is 88.4% of the eleven-cell Q of 36.40, which
is the pool the decomposition is computed on. Against the legacy twelve-cell Q of 43.19 — the pool
that contained the withdrawn GroupNorm cell — the same 32.20 is 74.6%. Both are true of different
denominators, and quoting the second without naming it is how "≈75%" reads as though the GroupNorm
cell were still in the partition, which it is not.

**What we may not conclude from the direction.** The four levels happen to arrange themselves as a
2 × 2 in the base optimiser's own state: the two levels whose base carries **no momentum term**
(SGD, RMSProp) sit at ≈ +1.0, and the two that carry one (SGDm, AdamW) sit at ≈ +0.28…+0.56. As
contrasts, a momentum main effect of **−0.587 ± 0.145 (z −4.04)** against a second-moment main
effect of **−0.169 ± 0.145 (z −1.16)**, with an interaction whose magnitude is 0.215 ± 0.291 and which the design
cannot resolve. This is consistent with §5.5, which kills second-moment normalisation as the axis
on the independent RMSProp-versus-AdamW contrast. **We register it as a prediction, not a result**,
for four reasons, and a referee should hold us to all four:

1. **Three of the four levels rest on one batch each.** Only SGDm is replicated (7 batches).
2. **SGD and RMSProp are not independent of each other:** they are the two halves of a single
   submission, `nl1` (job ids 4832408–4832431, one node pool). D is a within-batch contrast, so a
   batch-level offset cancels inside each half — but a batch × partition interaction peculiar to
   `nl1` would move both levels together, and nothing in this corpus would see it. This is strictly
   worse than "one design point per level".
3. **The momentum coefficients are not matched** (0.99 under SGDm, 0.9 under AdamW), so "momentum
   present/absent" is a two-point contrast in a continuous parameter.
4. **Momentum alone is not sufficient.** Collapsing the four levels to momentum-present /
   momentum-absent leaves a residual Q of 12.17 on 8 df inside the momentum-present group — the
   SGDm-to-AdamW gap survives the collapse. The identified moderator is *the base optimiser*, not
   any single component of it.

**R3 (`bm2`, §3.5) is exactly the experiment this weakness names**: a second, independent batch at
the SGD and RMSProp bases with fresh seeds, which would replicate the moderator at three of four
levels and break the `nl1` co-dependence. Until it is scored, "the base optimiser is a moderator of
D" is a within-corpus decomposition of eleven measurements, **not an out-of-sample prediction rule**
— which is why it does not contradict §5.8, where the predictors under test are continuous
properties of a configuration and the unit is the design point. It should also be read against §3.4:
`nl1` is one of the five batches with no scorer registered before its runs existed, so the two
levels doing the most work here are the two with the least procedural protection.

The one cell we removed from this pool is the GroupNorm arm of `gn1` (+0.202 ± 0.137): its own
registered scorer refuses to issue a verdict at a 1.37× budget ratio, so under our own rule (§3.4)
it may not be scored, and it is not reported here as a normalisation-scheme result. For the record,
keeping it as a fifth level would raise the explained share to 90% and lower the pooled D to
+0.546 ± 0.036 — i.e. the decomposition does not depend on the exclusion; only our right to quote
the cell does. Adding `ml2` as a twelfth cell at its corrected se gives pool +0.567 ± 0.036,
Q = 36.74 on 11 df, τ = 0.196.

A second AdamW measurement exists but is not in the pool: `sm3` (§6.1) is void as designed and
salvageable only as an independent replicate of `aw1`, and its twelve runs are not yet ingested into
the run table. Re-derived from its raw `.out` series it reads D = +0.141 ± 0.064 against `aw1`'s
+0.279 ± 0.087, a replicate spread of +0.137 ± 0.108 (z 1.27). We report that as a consistency check
and do not pool it into Table 2 or into this decomposition, because a number that is not in the
deposited run table cannot be re-derived by a reader running `make reproduce`.

![Figure 2](figures/f2_base_moderator.png)

**Figure 2 — the heterogeneity in D is a base-optimiser effect, not an unattributable one.**
(a) The eleven same-contrast ResNet-18 cells, grouped by base optimiser; each group's band is its
own inverse-variance pool ± 1.96 se. The eight SGDm cells — seven separate submissions, two
meta-stepsizes, two budgets and three clip boxes — are **homogeneous**: Q 4.21 on 7 df, p 0.76,
DerSimonian–Laird τ = 0.000, pooling to +0.556 ± 0.045. (b) Partitioning the eleven-cell Cochran Q
(Eq. 12): **32.20 of 36.40 (88%) is between base optimisers**, on 3 df, p 4.8e-7. (Against the
legacy twelve-cell Q of 43.19 that the withdrawn GroupNorm cell used to enter, the same 32.20 is
74.6% — the "≈75%" figure, whose denominator must always be named.) This is the figure that
replaces "for reasons we cannot attribute".

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

**`dD` is an upper bound in magnitude, and here is why.** The two rungs are η ∈ {1e-4, 3e-4}
and the argmax was taken on the same test accuracies that define `D` (§3.3). Both arms'
argmax landed on the same rung, η = 3e-4, so `D_own` is itself a clean within-batch
count-matched contrast and carries no cross-arm selection. What it does carry is rung
selection over two rungs at n = 3, and a test-selected argmax rewards the noisier arm more:
at the selected rung the `nodewise` arm has sd 0.164 against the `chunk777` arm's 0.021
(`plateau5`, n = 3 each). Selection therefore pushes `D_own` down and pushes the measured
shrinkage `dD` away from zero, so **−0.090 ± 0.178 is the largest shrinkage this two-rung
ladder can produce on this metric, not an unbiased estimate of it.** The conclusion — that
re-tuning does not remove `D` — is conservative in the direction that matters, and we state
it as a bound rather than as a null.

The same batch measures D's sensitivity to η directly: +0.681 → +0.591 across 0.477 decades, i.e.
**−0.189 pp per decade of η**, within one batch. That is the number to use; the cross-batch
cross-box value the record previously carried is superseded.

### 4.6 Alignment: a bounded null, and what it does not settle

`permnode` holds nodewise's group **count** and its **exact per-tensor size multiset** and
randomises only *which* weights share a group, within each tensor. Both properties are measured
from the allocated `beta` on the built network by the submission script's own guard, not inherited
from a comment. The contrast was registered five-way with a symmetric band before the runs
existed. The scorer's `P2`, run unedited (`--selftest` 139/139 PASS), verbatim:

```
permnode<S> (m=14420, nodewise's EXACT size multiset, membership randomised)  92.003 +-0.090 (n=3)
nodewise    (m=14420, output channels)                                        92.012 +-0.129 (n=3)
A = permnode - nodewise = -0.009 pp   (se 0.157, t -0.06)
registered: A > +0.30 HURTS | (+0.15,+0.30] UND | [-0.15,+0.15] NULL | [-0.30,-0.15) UND | A <= -0.30 HELPS
-> **NULL**
```

In the same batch `D = +0.581 ± 0.141 (t 4.11)` and `B = chunk777 − permnode = +0.590 ± 0.107
(t 5.53)`, and `A + B − D = 0` exactly (Eq. 7) — a receipt on the reduction, not a finding.

**What the verdict licenses, printed to the same precision as the verdict.** `NULL` is a decision
about a band; it is not an estimate. The estimate is `A = −0.009` with a 95% interval of
**[−0.317, +0.298] pp**, which against this batch's own `D = +0.581` is **[−55%, +51%] of D**.
The smallest alignment effect this design could have detected at 80% power is **0.440 pp, i.e.
76% of D**; its power against an alignment effect equal to *half* of D is **0.46**. The honest
reading is therefore two-sided and asymmetric in its usefulness:

* **Excluded.** Alignment as the *principal* carrier of D. An effect of `+0.58` — alignment
  explaining all of D — would have been detected here with probability 0.96, and was not.
* **Not excluded.** Alignment as a *contributing* carrier at up to roughly half of D, in either
  direction. The interval covers `+0.29` and `−0.32`.

The point estimate's share of D, −1.6%, is quoted in the project record and should be read with
the same interval attached: the share is **−1.6%, 95% CI [−55%, +51%]**. A ratio whose numerator
is a null is not a precise quantity and we do not present it as one.

**A defect in our own registration, since we require it of others.** The NULL band's half-width
(0.15) is **narrower than the standard error the batch achieved** (0.157). The band was set from
`mm1`'s effect-size scale — deliberately, so that the alignment and size-distribution legs would be
read on one axis — and no power calculation was performed at the planned `n`. The consequence is
computable: had the true effect been exactly zero, this batch would have returned `NULL` on only
**66%** of realisations and an UNDECIDED wing or worse on the other **34%**. The verdict is
therefore correctly *scored* and weakly *powered*, and we report it as such. The standard error is
itself estimated on 3.6 degrees of freedom, with 95% interval [0.092, 0.496]; on a Welch *t* rather
than a normal approximation the interval on `A` widens to [−0.467, +0.448] = [−80%, +77%] of D. We
print the normal-approximation interval as the headline because it is the one registered in the
project record, and the *t* interval here so that a reader recomputing it finds no surprise.

**The manipulation was not inert.** The natural objection to any null is that the knob never
turned. It did. Over the same nine runs, permuting membership moves the effective-sample-size field
`N_eff/m` from 0.0547 ± 0.0010 to 0.0414 ± 0.0003 — **−0.0133 ± 0.0010, t −12.7**, which is 70% of
the whole `nodewise → chunk777` move in that statistic — while moving `plateau5` by −0.009 ± 0.157.
This is descriptive and carries no registered direction, and §5.2 has already shown that `N_eff/m`
does **not** track accuracy. It establishes one thing only, and that thing matters here: the
permutation demonstrably changed the optimiser's internal state, so `A ≈ 0` is a statement about
accuracy's insensitivity to alignment and not about a manipulation that failed to apply.

**Three scope limits, printed with the result rather than below it.**

1. **Within-layer only.** `permnode` permutes *inside* each tensor, so this asks whether an output
   channel is special among the same-sized subsets **of its own layer**. It does not test whether
   *layer* boundaries matter. The registered scorer refuses to report this verdict as "architecture
   is irrelevant", and neither do we.
2. **Permutation variance is confounded with seed variance.** `permnode<S>` takes `S =` the run
   seed (`bin/c77_permuted_partition.sh:447`), so seeds 0–2 are three different permutations *and*
   three different initialisations. `se(A) = 0.157` is a compound of the two and this batch
   **cannot** decompose it. The direction is conservative — a second variance source can only widen
   the interval — but it means we cannot say how much of [−0.317, +0.298] is draw-to-draw variation
   in the permutation itself, which is precisely the quantity the claim is about.
3. **One point in the design.** `A` is measured in **one batch, at one cell**: ResNet-18 /
   CIFAR-10 / SGDm base / Lion meta / η = 1e-4 / 100 epochs, with `nodewise` read at η = 1e-4
   rather than at its own argmax of 3e-4. `D` is measured in sixteen count-matched within-batch
   cells across three networks, two datasets and four base optimisers. The two results are
   not on the same evidential footing and we do not present them as though they were.

**What would settle it, and it is running.** A single batch closes all three of the statistical
gaps above: **R1 — `rp1`, `permnode` at three permutation draws × six seeds with the permutation
seed decoupled from the run seed, plus a six-seed `nodewise` arm; 24 jobs (§3.5).** No patch is
needed — `permnode<S>` already accepts an explicit `S`; `c77` simply passed the run seed. That
design (i) takes `se(A)` from 0.157 to ≈0.09, which brings the MDE to ≈0.25 pp, below half of D and
inside the pre-registered band for the first time; (ii) yields a **two-way variance decomposition**
that separates permutation variance from seed variance, so limit 2 above becomes a measured number
instead of a caveat; and (iii) supplies the replication `A` has never had. Until it reports, the
sentence this paper is entitled to is the bounded one above and not a stronger one. **If `rp1`
returns an interval that still spans half of D, the alignment leg is to be reported as
underdetermined rather than as a null**, and we register that in advance here and in that batch's
own scorer.

### 4.7 The prescription, and its exact scope

The practitioner's move implied by §4.3 and §4.6 is: **give each one-dimensional tensor a single
step size instead of one per element.** Measured as T = `nodewise1d` − `nodewise` (Eq. 5), within
batch:

| batch | network / setting | n | T (pp) | se | t |
|---|---|---|---|---|---|
| bn1 | R18 / C10 / SGDm | 3 v 3 | +0.427 | 0.041 | 10.43 |
| ml2 | R18 / C10 / SGDm | 3 v 3 (×2 reruns) | +0.619 | 0.176 | 3.52 |
| fa1 | R18 / C10 / SGDm, η 3e-4 | 6 v 6 | +0.649 | 0.110 | 5.88 |
| g3m | **R34** / C10 / SGDm | 9 v 9 | +0.758 | 0.093 | 8.13 |
| cc1 | R18 / C10 / SGDm | 3 v 3 | +0.816 | 0.159 | 5.13 |
| r50 | **R50** / C10 / SGDm | 3 v 3 | +1.049 | 0.317 | 3.31 |
| gm2 | R18 / **C100** / SGDm | 3 v 3 | +1.363 | 0.151 | 9.00 |
| hz3‡ | R18 / C10 / SGDm, **300 ep** | 6 v 6 | +0.337 | 0.069 | 4.85 |
| nl1 | R18 / C10 / **SGD** | 3 v 3 | +0.692 | 0.135 | 5.12 |
| nl1 | R18 / C10 / **RMSProp** | 3 v 3 | +0.916 | 0.242 | 3.79 |
| aw1 | R18 / C10 / **AdamW** | 3 v 3 | **+0.091** | 0.078 | 1.16 |

‡ `hz3` matched at 5 v 5 (seed-5 trio excluded for the clip-box and hardware mismatch of §7 T9):
**+0.328 ± 0.084, t 3.89**.

The move costs nothing — it *reduces* the number of learned quantities from 14,420 to 4,851 — and
under an SGDm, SGD or RMSProp base it is worth **+0.328 to +1.363 pp** across ten within-batch
cells, every one resolved at t ≥ 3.3. **Under AdamW it is worth nothing measurable
(+0.091 ± 0.078, t 1.16).** That is the scope line, and §5.4 explains why it is where it is.

Decomposing T by Eq. 6 on `rl3` at η = 1e-4: T = +0.756 = 0.692 + 0.064. The **count**
component is 8% of the effect; the tail component is the rest. Any account that treats "merge the
1-D tensors" as a count reduction has the decomposition backwards.

### 4.8 Budget: the effect survives 3× the budget; whether it decays is not resolved

`hz3` ran the four arms for 300 epochs at 6 seeds, so D at 100, 200 and 300 epochs can be taken
**within run**, per seed. That pairing cancels the seed, the run and the batch identically. It does
**not** cancel the step-size clip box or the GPU class, because `hz3` is two submissions: its
seed-5 `chunk777`, `nodewise1d` and `chunk2325` runs were resubmitted in the narrower box
`−15:−2.3026` and on an A100, while everything else — including their own seed-5 `nodewise` partner
— ran at `−30:9.0` on an L4 or a 2080 Ti (§7 T9). We therefore report the budget contrast **twice**:
as submitted, and over the five clean seeds.

| budget | D, 6 seeds as submitted | se | D, 5 clean seeds | se |
|---|---|---|---|---|
| 100 | +0.576 | 0.109 | **+0.662** | 0.083 |
| 200 | +0.514 | 0.115 | **+0.575** | 0.119 |
| 300 | +0.428 | 0.071 | **+0.455** | 0.081 |

**The level is robust, and it is the claim we make.** D(300) reads +0.428 ± 0.086 at 6 v 6
(t 4.94) and +0.455 ± 0.096 at 5 v 5 (t 4.75) on the Welch estimator used everywhere else in this
paper; all six seeds favour `chunk777` at 300 epochs (exact binomial p = 0.0156). **The partition
gap is not an artefact of a 100-epoch budget.**

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

One further reading must be disclosed rather than buried, because the batch's own registered scorer
prints it. `analysis/c87_hz3_score.py` fixes its primary window at **50 epochs**, not at
`plateau5`'s 5, and on that window returns D(300) − D(100) = **+0.229 ± 0.070, t 3.27**, verdict
`GROWS`. The windows disagree because at B = 100 a 50-epoch trailing mean spans epochs 50–99 and
therefore *contains* the mid-training trough documented below, while at B = 300 it contains none:
the window injects the trough at exactly one budget. `plateau5` is this paper's primary metric
throughout and we do not switch it here — but the registered verdict is `GROWS`, our
primary-window reading is a non-significant decline, and a reader is entitled to both. See
Appendix A.2.

**The trajectory is not monotone, and we publish it.** Within run, D goes significantly *negative*
in mid-training and recovers:

| epoch | cc1 (n=3) | g3m, ResNet-34 (n=9) |
|---|---|---|
| 25 | +0.625 ± 0.170 | −0.081 ± 0.156 |
| 55 | **−0.560 ± 0.150 (t −3.73)** | **−0.518 ± 0.128 (t −4.04)** |
| 75 | +0.345 ± 0.129 | — |
| 100 | +0.727 ± 0.146 | +0.666 ± 0.091 |

Any claim about D is a claim about the end of training at these budgets.

![Figure 3](figures/f3_budget.png)

**Figure 3 — D at 1×, 2× and 3× the budget, paired WITHIN run, and what one box-mismatched seed
does to it.** `hz3` ran the four arms for 300 epochs at six seeds, so D can be read off the same
run at three budgets, cancelling seed, run and batch identically. (a) Faint lines are the six
per-seed trajectories; the two heavy lines are the arm-set means with 95% intervals. **Seed 5 is
drawn in red because it is not box-matched**: its chunk arm ran in β-box −15:−2.3026 and its
nodewise arm in −30:9.0, so that seed's D is a cross-box difference and the other five are not.
(b) The budget slope both ways. D is present and resolved at every budget, and the slope does not
resolve either on all six seeds (−0.149 ± 0.105, t −1.42) or on the five box-matched seeds alone
(−0.207 ± 0.107, t −1.94). Neither interval excludes zero, so the verdict does not turn on the
contaminated seed — but its *t* does, and we print both rather than choosing.

---

## 5. Eight candidate mechanisms — three refuted — and two nulls

This section is the second half of the contribution, not an appendix. Of the eight, **three are
refuted** (M2, M3, M6), **one is narrowed** to an SGDm base and remains alive there (M4), **one is
not separable** from the axes it is aliased with (M7), and **three cannot be decided by this
instrument or this design** (M1 untested, M5 inapplicable, M8 not identifiable). One refutation
rests on a gate registered before its data existed (M2); two are post-hoc contrasts on data
collected for other purposes (M3, M6). One further candidate, M1, had its literature attribution
withdrawn after we re-read the sources.

**An earlier draft of this paper claimed four refutations**, the fourth being M7, on the strength of
a within-batch contrast that the relevant batch's own registered scorer refuses to compute (§5.6,
§7 T7). We withdrew the contrast and the refutation with it. That is the most expensive single
application of §3.4's rule in this paper and it is the reason the rule is worth stating as a
contribution.

**The refutations carry their own power limits and we print them with the verdicts.** M3 in
particular refuses a general *size law* at t 0.87 and cannot rule out a tail-specific effect;
"refuted" there means the general form is refuted, not that the tail is exonerated (§5.3).

**Index of the eight candidates, the verdict on each, and where each is decided.**

| # | candidate mechanism | verdict | where |
|---|---|---|---|
| M1 | √N estimator-noise averaging over group members | **untested, not refuted** — our instrument measures the wrong quantity; its literature attribution withdrawn | §5.1, §2.5 |
| M2 | Meta-gradient correlation (an N_eff/m field) predicts accuracy | **refuted** on its own pre-registered gate: anti-concordant t −11.14, dissociation t −23.26 | §5.2 |
| M3 | Degenerate size-1 groups are the carrier | **refuted** as a general size law: removing 100% of singletons buys +0.115 ± 0.133 (t 0.87) | §5.3 |
| M4 | The size-1 tail carries it universally | **narrowed to SGDm**: pooled D − G = +0.514 ± 0.056 over the 8 CIFAR-10 SGDm cells vs +0.047 ± 0.124 under AdamW. No individual `G` survives Holm over the 12-test family | §5.4 |
| M5 | Choi-style inclusion — a finer partition contains the coarser one once tuned | **inapplicable**: granularity is state, not hyperparameters; the only setting where the arms coincide is η = 0 | §2.2, §4.5 |
| M6 | The base optimiser's own second-moment normalisation | **refuted**: RMSProp and AdamW both carry one and differ by +0.694 ± 0.266 (t 2.61) | §5.5 |
| M7 | D tracks the aligned arm's accuracy level | **not separable**: the registered within-batch separator issued no verdict; the surviving slope is aliased with network and base optimiser (−0.119 ± 0.022 holding base, −0.386 ± 0.105 holding network, −0.187 ± 0.125 holding both) | §5.6 |
| M8 | Some summary statistic of the group-size distribution | **not identifiable** from this design (rank 3, one contrast type) | §5.7 |

**The two nulls**: architecture alignment (§4.6, §5.10) — a *bounded* null, `A = −0.009 ± 0.157`,
95% CI [−55%, +51%] of D, from one batch at one design point — and out-of-sample predictability
of D (§5.8). §5.9 adds the failure of the classical remedy — hierarchical partial pooling — which
is a dead *fix* rather than a dead mechanism, and is included because CAM-HD makes it the obvious
question to ask.

### 5.1 Untested, not refuted: √N estimator-noise averaging

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

### 5.2 Refuted: the meta-gradient correlation field predicts accuracy

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

### 5.3 Refuted as a size law: size-1 groups are the carrier

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


### 5.4 Narrowed to SGDm: the tail as a universal carrier

`D − G` (Eqs. 1–2) isolates the size-1 tail's contribution — G is the same contrast with the tail
already removed from both arms, count-matched exactly.

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
| ml2 (SGDm) | +0.456 ± 0.195 | +0.173 ± 0.073 | **+0.282 ± 0.208** | 1.36 |
| rl3 @3e-4 (SGDm) | +0.591 ± 0.096 | +0.217 ± 0.128 | **+0.375 ± 0.160** | 2.34 |
| nl1 (SGD) | +1.035 ± 0.109 | +0.525 ± 0.294 | **+0.510 ± 0.314** | 1.63 |
| **aw1 (AdamW)** | +0.279 ± 0.087 | **+0.232 ± 0.089** | **+0.047 ± 0.124** | **0.38** |

`ml2`'s three standard errors are computed on **three** independent seeds, not six runs: its
two nominal halves are the same command line including `--seed`, so the batch is three seeds
run twice rather than six seeds (§6.1). Averaging within seed before differencing gives
D +0.456 ± 0.195 (t 2.34), G +0.173 ± 0.073 (t 2.38), D − G +0.282 ± 0.208 (t 1.36). **Every
point estimate is unchanged**; only the standard errors move. `hz3` matched at 5 v 5 for the
seed-5 mismatch of §7 T9 reads D +0.455 ± 0.096, G −0.050 ± 0.075, D − G +0.506 ± 0.121, t 4.16 —
same verdict.

**The twelve `G` tests, corrected for multiplicity.** `G` is measured once per count-matched
cell, so the twelve values above are a family and the ones that reach nominal significance
should not be read one at a time. We declared the family as the `G` leg of every Table 2 cell
that has one — twelve tests, fixed before the correction was computed — and applied
Holm–Bonferroni step-down at α = 0.05. Each `p` is the two-sided Welch test on the two arm
means; `p (z)` is the normal approximation, which is the quantity the paper's `t` columns
report and is anti-conservative at 2–4 degrees of freedom. Each Holm column is computed on its
own ordering.

| cell | G | se | t | df | p (Welch) | p Holm | p (z) | p Holm (z) |
|---|---|---|---|---|---|---|---|---|
| g3m (SGDm, R34) | +0.171 | 0.073 | 2.34 | 16.0 | **0.033** | 0.39 | 0.0195 | 0.20 |
| aw1 (AdamW) | +0.232 | 0.089 | 2.62 | 3.5 | 0.067 | 0.74 | 0.0089 | 0.11 |
| ml2 (SGDm) | +0.173 | 0.073 | 2.38 | 4.0 | 0.076 | 0.76 | 0.0171 | 0.19 |
| rl3 @3e-4 (SGDm) | +0.217 | 0.128 | 1.69 | 3.9 | 0.168 | 1.00 | 0.091 | 0.73 |
| nl1 (SGD) | +0.525 | 0.294 | 1.79 | 2.8 | 0.177 | 1.00 | 0.074 | 0.67 |
| gm2 (SGDm, C100) | +0.068 | 0.069 | 0.99 | 3.5 | 0.386 | 1.00 | 0.322 | 1.00 |
| hz3 (SGDm, 300 ep) | −0.057 | 0.061 | −0.93 | 6.2 | 0.389 | 1.00 | 0.354 | 1.00 |
| r50 (SGDm, R50) | +0.153 | 0.314 | 0.49 | 3.9 | 0.653 | 1.00 | 0.627 | 1.00 |
| nl1 (RMSProp) | +0.020 | 0.049 | 0.41 | 3.4 | 0.710 | 1.00 | 0.686 | 1.00 |
| rl3 @1e-4 (SGDm) | −0.011 | 0.087 | −0.12 | 2.1 | 0.913 | 1.00 | 0.902 | 1.00 |
| cc1 (SGDm) | +0.011 | 0.147 | 0.08 | 2.4 | 0.944 | 1.00 | 0.938 | 1.00 |
| fa1 (SGDm) | −0.001 | 0.076 | −0.01 | 9.8 | 0.993 | 1.00 | 0.993 | 1.00 |

**At most three of the twelve reach nominal α = 0.05 and none survives Holm.** On the normal
approximation the three are `aw1` (t 2.62), `ml2` (t 2.38) and `g3m` (t 2.34), with smallest
adjusted p = 0.11; on the Welch degrees of freedom only `g3m` reaches nominal α, with
smallest adjusted p = 0.39. **We therefore make no claim that `G` is resolved in any
individual cell**, and an earlier version of this section, which rested on `G` being resolved
under AdamW, is withdrawn as a per-cell claim.

What survives the correction is not a cell but a **contrast between base optimisers**, which
is a single pre-specified comparison and needs no family correction: `D − G` is
+0.047 ± 0.124 (t 0.38) under AdamW against a fixed-effect pool of **+0.514 ± 0.056 (t 9.2)**
over the eight CIFAR-10 SGDm cells (Q 4.52 on 7 df; restricted to the six ResNet-18/CIFAR-10
cells it is +0.514 ± 0.064, the same point estimate). Adding the CIFAR-100 cell would give
+0.558 ± 0.055 with Q 17.17 on 8 df, which §4.3's commensurability rule forbids and which is
that rule doing measurable work rather than being a stylistic preference. The tail accounts for
essentially none of `D` under AdamW and for essentially all of it under SGDm, and that
difference — not any single `G` — is the result.

An independent AdamW measurement points the same way and is *not* pooled into the numbers above,
because its runs are not yet in the deposited run table: `sm3`, re-derived from its raw `.out`
series, gives G = +0.296 ± 0.096 and D − G = −0.155 ± 0.116 at the same cell as `aw1` (§6.1).
Taken with `aw1` that would be D − G = −0.054 ± 0.082 over six seeds. We report it as a
consistency check on the direction and make no claim from it.

**Two `G` contrasts exist in the corpus outside this table**, and we name them so the family
is auditable rather than convenient. `bn1` ran `nodewise1d` and `chunk2325` (m = 4,851 in
both arms) but no `chunk777` arm, so it yields a `G` and no `D`: G = +0.295 ± 0.048, the
largest `G` in the corpus and the only large positive `G` under an SGDm base — which cuts
against "under SGDm, removing the tail removes the gap". `sm3` yields G = +0.296 ± 0.096.
Enlarging the family to all fourteen and re-running Holm changes the count but not the verdict
on the tabled twelve: on the Welch degrees of freedom **nothing survives Holm at fourteen
either**; on the normal approximation `bn1` (adjusted p = 1.1e-8) and `sm3` (adjusted
p = 0.030) survive and no cell in the table does. The fourteen-test family is also
heterogeneous (Q = 40.1 on 13 df, p = 1.3e-4) where the tabled twelve is not (Q = 18.2 on
11 df, p = 0.077), driven by `bn1`; `bn1` and `cc1` are the same configuration in different
batches and their `G` values differ by 0.284 ± 0.155 (t 1.83), i.e. not resolved, which is what
§6.3's cross-batch bound predicts. We disclose it rather than leave a referee to find it.

Under SGDm, removing the tail removes the gap. **Under AdamW it does not**: `D − G` collapses
to +0.047 ± 0.124 in `aw1`, against +0.514 ± 0.056 pooled over the eight CIFAR-10 SGDm cells.
`G` itself is positive under AdamW (+0.232 ± 0.089) but survives Holm over the `G` family in
neither convention, so the base-dependence is carried by the `D − G` contrast, which is one
pre-specified comparison, not by a per-cell `G` verdict. The pre-registration for that batch
said, before the data existed, that *"a RESOLVED non-null G would say the tail story is
base-dependent and must be re-scoped."* The re-scoping is warranted on the contrast; the word
"resolved" is not, and we do not use it.

> **"The gap lives in the degenerate size-1 tail" may not be written as a general claim.** It holds
> under an SGDm base with a Lion meta-optimiser and is scoped to that.

The same batch's D itself is **UNRESOLVED** on its own registered rule: `analysis/c88_scorers.py
--score aw1` prints `{'D_adamw': 0.279, 'se': 0.087, 't': 3.19, 'rule': "UNRESOLVED at n=6.
Report the interval. Do NOT re-cut the data, and do NOT describe it as 'partially transferring'."}`
The registered bar was a 95% lower bound above +0.30; the realised bound is **+0.108** (normal
approximation; **+0.038** on Welch df 4), so the bar is not cleared. The registration also
specified 6 seeds where only 3 reached the contrast, so the primary ran at half its registered
power — a registration deviation disclosed again, with its cause, in §8. **D under AdamW is
reported as an interval, +0.279 [0.108, 0.450], not as a transfer.**

![Figure 4](figures/f4_decomposition.png)

**Figure 4 — D splits into a tail-free part G and a size-1-tail part D − G, and the split is
base-dependent.** (a) For every batch that ran all four arms, D is drawn as the sum of G (hatched:
the same uniform-versus-aligned contrast with the size-1 tail *already removed from both arms*,
count-matched exactly at m = 4,851) and D − G (solid: what the tail contributes). The black tick
and whisker are D itself with its 95% interval. Under an SGDm base the hatched part is ≈0 and the
tail carries essentially all of D. Under **AdamW** it does not: G is +0.232 ± 0.089 and D − G
collapses to +0.047 ± 0.124. (b) D − G alone, with 95% intervals and each cell's *t*. CIFAR-100 is
placed below the rule for the reason given in Figure 1. The pooled SGDm/CIFAR-10 value is
**+0.514 ± 0.056** over eight cells (Q 4.52 on 7 df); we quote that pool rather than `cc1`'s
+0.715, which is the maximum.

### 5.5 Refuted: base-optimiser normalisation

If the mechanism were "a base optimiser that already normalises per coordinate does not need the
partition to do it", then RMSProp and AdamW — both carrying a second moment — should behave alike.
They do not: **D(RMSProp) − D(AdamW) = +0.694, se 0.266, t 2.61**. Whatever separates the base
optimisers here, second-moment normalisation is not it.

This is the same conclusion §4.4 reaches from the other side: in the four-level base
decomposition the second-moment main effect is −0.169 ± 0.145 (z −1.17) while the momentum main
effect is −0.587 ± 0.145 (z −4.04). Neither of those contrasts is a result — three of the four
levels are single batches — but they agree on which component of the base optimiser is *not* the
axis.

### 5.6 Not dead, not separable: D and the aligned arm's accuracy level

Over all 10 design points, regressing D on the aligned arm's `plateau5` gives slope
**−0.044 ± 0.011, t −4.06, r −0.821** — which looks like a law and is not one, because level and
dataset are the same column: the single CIFAR-100 design point sits at level 70.44 and the nine
CIFAR-10 design points at 89.63–92.98.

Inside CIFAR-10 the slope is **−0.161 ± 0.067, t −2.38, r −0.669** over 9 design points (exact
permutation over all 9! = 362,880 orderings, p = 0.0454). We report that it is nominally resolved,
and then report the four things that stop it being a mechanism.

* **It is at the resolution floor by construction.** At 9 design points the two-sided 5% critical
  correlation is |r| = 0.666. The realised |r| is 0.669. A result that clears its own critical
  value in the third decimal place is a coin landing on its edge, not a law.
* **It is aliased with the network and with the base optimiser, and the alias is the whole
  effect.** The two lowest-level CIFAR-10 design points are `r50` (a different network) and
  `nl1`/SGD (a different base optimiser). Holding the base fixed at SGDm (6 points, spanning
  ResNet-18/34/50) gives **−0.119 ± 0.022**; holding the network fixed at ResNet-18 (7 points,
  spanning four bases) gives **−0.386 ± 0.105**; holding **both** fixed — the only four points
  where "level" varies with nothing else structural — gives **−0.187 ± 0.125, t −1.49, exact
  permutation p = 0.333, unresolved.** A slope whose magnitude moves by 3.2× depending on which
  confound you hold, and which vanishes when you hold both, is measuring the confounds.
* **An instrument that does not share an arm with D does not resolve it.** D and level share the
  `nodewise` arm. The mechanical slope this induces is −0.017 (the mean sampling variance of a
  `nodewise` arm mean, 0.01808, over the variance of level across the nine points, 1.07971), one
  tenth of −0.161, so the artefact is not the explanation. But replacing level by an independent
  instrument — the mean of the `chunk2325` and `nodewise1d` arms, neither of which enters D —
  gives **−0.167 ± 0.101, t −1.65** within CIFAR-10 and does not clear the bar.
* **The one within-batch contrast left in the corpus does not resolve it either.** `rl3` ran both
  meta-stepsize rungs in one batch: level moves +0.599 pp (91.908 → 92.507) and D moves −0.090
  (+0.681 → +0.591), an implied within-batch slope of **−0.150 ± 0.331 (t −0.45)**. Same sign as
  the between-point slope, and an interval that contains zero and all three sub-slopes above. It is
  also confounded with η, which is why it is a consistency check and not a test.

**The registered within-batch separator issued no verdict.** `gn1` was built to answer exactly
this question — one batch, one variable changed (BatchNorm → GroupNorm), batch cancels — and its
pre-registered commensurability gate fired: the two halves sit on error budgets of 7.707 pp and
10.569 pp, a 1.37× ratio against a registered bar of 2.0 pp, so a percentage-point contrast
between them is not defined. Its scorer prints **"NO TRANSFER VERDICT IS ISSUED … THIS IS NOT A
NULL"** and halts before computing either contrast. An earlier version of this paper quoted that
batch's face values as a falsification of the level model — a within-batch `dD` of −0.385 ± 0.205,
described as wrong-signed by 2.2 to 7.0 se. We withdraw that, and we withdraw the falsification
with it. **Both legs of the earlier argument came from the withdrawn cell**: it was the
within-batch test, and it was also the low-level point that flattened the within-CIFAR-10 slope,
which without it moves from −0.021 ± 0.077 (t −0.27) to the −0.161 ± 0.067 above. The paper is
weaker here than the previous draft claimed, and in the direction the level model predicts.

**What is left is an honest negative-space statement, not a dead mechanism.** The accuracy level
of the aligned arm is not separable from the network and the base optimiser in this corpus, at 9
CIFAR-10 design points and a critical |r| of 0.666. We do not claim it is a carrier; we do not
claim it is not; and §5.8 shows that as a *predictor* it is the worst of the four models we tried,
out of sample. The design needed to separate it — a level contrast at fixed network, fixed base
and commensurable error budget — is stated in §9.

### 5.7 Not identifiable (and un-killable): a summary statistic of the size distribution

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

The sixteen D cells of Table 2 collapse to **10 distinct design points** (the six identical
ResNet-18/SGDm/η=1e-4/100-epoch batches are one point; the two CIFAR-100 batches are one).
Leave-one-design-point-out, refitting each single-predictor model on the held-in 9:

| model | LOO RMSE | vs "predict the corpus mean" |
|---|---|---|
| **mean (baseline)** | **0.3859** | — |
| D ∝ k·log(headroom) | 0.2693 | −30% |
| CIFAR-100 dummy | 0.3765 | −2% |
| D ∝ k·headroom | 0.3796 | −2% |
| D ∝ level (OLS) | 0.8379 | **+117% WORSE** |

**None of this is a result, and here is why.** The margin is dominated by the single CIFAR-100
fold: the mean errs by −0.888 there and `k·log(headroom)` by −0.457, and restricted to the nine
CIFAR-10 folds the best model wins by 0.040 RMSE (0.2791 → 0.2395, −14%; the level model,
0.2358, −16%), with a sign test of 7/9, two-sided p = 0.180. Over all ten folds the sign test is
8/10, p = 0.109. The functional form is itself the winner of about ten candidates scored on
the same points, so any apparent improvement is a best-of-ten selection statistic before it is
anything else. And the power bound is decisive: **at 10 design points a predictor needs |r| ≥
0.632 — it must explain ≥ 40% of the between-design-point variance — to be visible at p < 0.05**;
seeing |r| = 0.4 would need ≈ 25 design points, which is not reachable by brute force.

The level model earns its own sentence. Fitted on the nine CIFAR-10 points it predicts
D(CIFAR-100) = **+4.11 against +1.56 observed**, an error of +2.55 pp — nearly three times the
error of simply predicting the corpus mean. A covariate that is nominally resolved *within*
CIFAR-10 (§5.6) and catastrophic the moment it is asked to leave it is a within-regime
association, not a law.

Three aliasings make the corpus look richer than it is. (i) `frac_groups_size1`, log m, log
params, log(n classes) and the CIFAR-100 dummy are **not five predictors**: the singleton fraction
is pinned near 2/3 by a structural identity (every convolution has `bias=False` and is followed by
one affine norm), taking 0.66644 on every CIFAR-10 cell and 0.66438 on the CIFAR-100 cells, so
regressing D on it is regressing D on the dataset dummy. Anyone who writes *"D scales with the
singleton fraction"* from this corpus has written *"CIFAR-100 is different"*. (ii) m and params are
1-vs-9 leverage contrasts resting on one architecture point each. (iii) G shares a batch with D
and has no predictive content anyway.

> **The draft sentence:** *D is real, replicated across 16 count-matched within-batch cells. Its
> variation across configurations is not unattributed: 88% of it is the base optimiser (§4.4), and
> within a fixed base D is homogeneous (τ = 0.000, 95% upper limit 0.109 pp). What remains
> unpredictable is the **continuous** part — no measurable scalar property of a configuration
> predicts D out of sample better than the corpus mean by a margin this design, at 10 design
> points, can resolve.*

The two statements are not in tension, and the estimands are worth separating explicitly. §4.4 is a
**within-corpus decomposition** over a categorical factor with three singleton levels; §5.8 is
**out-of-sample prediction** over continuous covariates at the design-point level. A factor can
account for most of the observed heterogeneity and still support no prediction rule, and here it
does exactly that.

### 5.9 Dead fix: hierarchical partial pooling

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


### 5.10 Bounded null: alignment (repeated here because it is a deliverable)

§4.6. `A = −0.009 ± 0.157, t −0.06`, scored `NULL` against a band registered in advance, with a
95% interval of [−0.317, +0.298] pp = [−55%, +51%] of D and an MDE of 0.440 pp = 76% of D. It
excludes alignment as the principal carrier and leaves a moderate contribution open, from one
batch at one design point, with permutation variance confounded with seed variance and with a
registration defect we print (band half-width 0.15 < realised se 0.157). Read at that strength it
is still what redirected this programme from architecture alignment to group-size homogeneity,
and it is still worth as much as the positive — a negative reported with its resolution is a
deliverable; a negative reported without one is a claim we cannot support. R1 (`rp1`, 24 jobs, in
flight, §3.5) is designed to halve the interval and to decompose the two variance sources.

---

## 6. Measurement discipline: what our own instrument did to us

This section reports four defects in our own process. Each cost a claim; each is cheap for a
reader to avoid.

### 6.1 Two batches that failed silently on their own axis

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
not use it. **All 24 `ml2` runs are meta = Lion.** Worse, after last-wins its two nominal halves
resolve to **the same command line including `--seed`**, differing only in an output path. `ml2` is
therefore three seeds run twice, not six seeds, and its standard errors are computed on three
groups (§3.3, *Duplicate runs*). The corpus census confirms the hole is still open: **367 of 367
partition-programme runs are meta = Lion**, across four base optimisers.

**One cycle later, the same defect voided a second batch.** `sm3` (12 runs) was built to test the
one untested corner of the base × meta grid — an AdamW base with an **RMSProp** meta-optimiser,
where both components carry a second moment. Its own `ARGS:` line reads
`--alg-meta RMSProp … --alg-meta Lion`, so it ran Lion. **The second-moment corner is untested, not
refuted**, and the batch is salvageable only as an independent replicate of `aw1`: D = +0.141 ±
0.064, G = +0.296 ± 0.096, at the same box, α₀, η and budget. Its twelve rows are not yet in the
deposited run table, so no number from it enters a claim in this paper; it appears in §4.4 and §5.4
as a consistency check and nowhere else. The properly composed replacement (R4, `sm4`) is in
flight (§3.5).

Reported as such, `ml2` is still informative, in a way we would not have bought deliberately: it is
**two nondeterministic reruns of one 3 v 3 measurement** in one batch. They read **+0.554 ± 0.217**
and **+0.357 ± 0.211**. A 0.197 pp spread between reruns of one measurement, at fixed seeds inside
one batch, is a direct **nondeterminism** bound — not a seed bound and not a batch bound — and it is
of the same order as τ = 0.203 pp (§4.4). Over all twelve same-seed pairs the bound is mean
|Δ`plateau5`| **0.163 pp**, max **0.472 pp**. Collapsed to its three groups, `ml2` gives
D = +0.456 ± 0.195, which is row 5 of Table 2.

**What we now do about it, mechanically.** `analysis/argsline_guard.py` reads a run's own `ARGS:`
line, fails on any repeated flag, and checks a declared design; `bin/_lib_guards.sh` refuses to
`sbatch` a command line that does not match the declared design and re-reads the first launched
job's actual `ARGS:` line afterwards. Swept over the 2,189 runs carrying an `ARGS:` line on both
clusters, exactly **36 carry a repeated flag, and they are exactly `ml2`'s 24 and `sm3`'s 12**. No
other batch on either cluster is affected: `--alg-base`, `--stepsize-groups`, `--meta-stepsize`,
`--alpha0`, `--num-epochs`, `--seed` and `--normalizer-param-*` are single-occurrence in every run
in the corpus, so **the partition axis, the budget axis and the step-size axis were never
overwritten anywhere.** Ten further submission scripts had been flagged by a text search for
carrying two or more `--alg-meta` occurrences; all ten are clean, verified two ways — no run they
produced carries a repeated flag, and every extra occurrence in their text is inside a comment or
inside a guard's quoted assertion array. The text search that produced that list was a
false-positive generator, which is itself the argument for STANDING RULE 20: audit the runs, not
the scripts.

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
cross-check; disagreements resolve in favour of the committed code. The most expensive application
of that rule in this paper is `gn1`: its scorer halts before computing the contrast a whole
subsection had been written around, and the subsection was rewritten rather than the scorer
overridden (§5.6, §7 T7).

The rule's companion — **no batch is submitted without a scorer registered first** — was broken
more often than the record said. Five batches behind material reported here have no
pre-registered scorer: `ml2`, `nl1`, `r50`, `gm2` and `sm3`. Two of them supply live Table 2 rows
and one, `nl1`, supplies both single-batch levels of the base-optimiser moderator in §4.4. Their
values reconcile field-by-field against their own runs' `ARGS:` lines; the gap is procedural, and
§8's provenance table marks each one rather than letting §3.4's scorer list read as coverage.

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

> At matched science — same network, dataset, granularity, base, meta, η, α₀, γ, augmentation, clip
> box, budget — and n ≥ 3 per batch, cross-batch offsets on this cluster are bounded by
> about 0.32 pp and are not separable from within-arm noise; seed is null (F 1.50, p 0.138). We
> keep every primary within-batch because the offset, while small on average, is not bounded
> *a priori* and is half the size of the effect at its observed maximum — and because at least one
> batch in this corpus is known to have run with unintended state (a modified optimiser file
> timestamped 33 s before submission), which no variance model would have caught.

Hardware was excluded by direct measurement: within (configuration × family), 2080Ti − L4 = +0.035
(n = 45), A100 − L4 = −0.021 (n = 21), A100 − 2080Ti = +0.112 (n = 5), over 29 distinct nodes.
That last figure is used in §7 T9 to show that the one hardware mismatch in the corpus points the
*wrong* way to explain the outlier it sits on.

### 6.4 A guard with a blind spot

`analysis/argsline_guard.py` is the corpus's only automated defence against the defect of §6.1, and
its file collector globs `<dir>/*.out` without descending, so it silently skips the twelve local
`.out` files under `runs/failed_hier_v1/`. All twelve are clean and none is in the run table, so
nothing in this paper is affected — but a guard with an unstated blind spot is worse than a guard
with a stated limit, and we record it here rather than in a commit message. The corpus sweep quoted
in §6.1 was run with a recursive collector for this reason.

---

## 7. Threats to validity

**T1 — One meta-optimiser.** All 367 partition-programme runs use Lion. Lion's sign update makes the
per-group α the *only* thing setting per-coordinate update magnitude, which is precisely the regime
where the partition should matter most. So our headline is measured at the most favourable point of
the axis we never varied. §6.1 explains why the two batches built to fix this did not, and §3.5
states the replacement that is running. **This is the paper's largest hole.**

**T2 — The mechanism is missing, one candidate is not identifiable from this design, and the
alignment null is underpowered.** §5.7 and §4.6. The size distribution is the surviving carrier
and takes +0.590 ± 0.107 of the decomposition, but we cannot say which property of it and this
corpus provably cannot tell us. Separately, the leg that redirected us there is measured once, at
`n = 3` v `3`, with an interval spanning [−55%, +51%] of D and with permutation variance
confounded with seed variance: **a moderate alignment contribution is not excluded**, and the
batch that would exclude it (R1, `rp1`, 24 jobs) is running rather than reported.

**T3 — Scale and domain.** CIFAR-resolution vision, ResNets, one framework. ImageNet-1k is not
available to us: the copy on our allocation has 489 of 1000 training classes and an unlabelled
validation set. No transformer, no language model, no reinforcement learning — and the parent
method's own home is reinforcement learning.

**T4 — Competitiveness.** We state the grouping key, because the answer depends on it. Among
the cells in this corpus that run **plain** MetaOptimize (no hierarchical pooling), the
highest is 93.317 ± 0.083 (n = 3; ResNet-18, six blocks, AdamW base + Adam meta, η = 1e-3,
α₀ = 3e-4, the interior maximum of a 7-rung α₀ ladder scored on the test set). Tuned
SGD + cosine on the same network and budget is 95.124 ± 0.047 (n = 5; lr 0.1, the interior
maximum of a bracketed 4-point grid: 94.172 / 94.844 / **95.124** / 94.181). The deficit is
**−1.807 ± 0.095 pp**.

That is the *smallest* deficit in the corpus, not a typical one, and the network is doing the
work. On ResNet-34 the best plain cell is 92.265 ± 0.053 (n = 9) against 94.823 ± 0.035 for
AdamW + cosine, a deficit of **−2.558 ± 0.063**; on ResNet-50 it is 90.833 ± 0.236 against
95.047 ± 0.110, a deficit of **−4.214 ± 0.260**. **The honest range is −1.8 to −4.2 pp behind
a tuned schedule, and it widens with depth.**

The single highest MetaOptimize cell anywhere in the corpus is not the one above: it is
93.967 ± 0.074 (n = 3; ResNet-34, layerwise, SGDm + Lion, η = 1e-3, α₀ = 1e-6, with this
project's own additive hierarchical pooling at η-ratio 0.025), −0.857 ± 0.081 behind the
ResNet-34 baseline. We do not lead with it: it is the last rung of a four-rung η-ratio ladder
within its own batch, so its argmax is at the ladder boundary and is interior only when a
second batch's rungs are appended, and §5.9 reports that this pooling operator does not
generalise. It is stated here so that no reader can find a higher cell in the released table
than the paper admits to.

MetaOptimize does beat a constant-LR AdamW tuned over four rungs (91.849 ± 0.092), which is
the comparison the parent paper makes. We make no competitiveness claim beyond that, and all
six numbers in this item are test-set argmaxes with no held-out estimate behind them (T12).

**T5 — Rule 11 is closed on one cell only.** §4.5 closes the "you compared at one arm's favourable
η" objection on ResNet-18/CIFAR-10. No meta-stepsize ladder exists on ResNet-34, ResNet-50,
CIFAR-100 or under AdamW.

**T6 — The 100-epoch horizon, and non-monotonicity within it.** D goes significantly negative at
epoch 55 on two independent batches and recovers by epoch 100 (§4.8). Our claims are about the end
of training at 100 and 300 epochs.

**T7 — BatchNorm and "size-1 tail" are under-identified.** On every network we ran, the only 1-D
tensors are normalisation parameters and one bias, so "the groups are degenerate" and "the groups
are on the normalisation parameters" coincide exactly. `gn1` was the designated separator and
**issued no verdict**: its pre-registered commensurability gate fired on a 1.37× error-budget
ratio between the BatchNorm and GroupNorm halves (7.707 pp against 10.569 pp, registered bar
2.0 pp), and its scorer halts before computing either contrast. **We therefore report its
GroupNorm arm means (Appendix B) and no GroupNorm contrast: no D from those arms enters Table 2,
the heterogeneity pool of §4.4, the design-point set of §5.8, or any count in the abstract.**
Consequently **every cell in this paper uses BatchNorm**, and this limitation is therefore
*un-probed* rather than probed-and-null; throughout we write *"normalisation scalars or, more
generally, one-dimensional tensors"* rather than committing. One consequence must be stated
plainly: because the scorer halts before T1, the retained `gn1` BatchNorm cell (Table 2 row 4,
+0.587 ± 0.153) is a **re-derivation from the four arm means the scorer does print**, not a scorer
verdict. Its T0 gate passes on 4/4 seeds per arm and T0.6 gates the percentage-point comparison of
the two halves rather than the BatchNorm contrast itself; had T1 been reached, +0.587 at t 3.83
would have cleared its registered bar of +0.30 and t ≥ 2. A maximally conservative reader may drop
that row too: the eleven-cell pool then becomes ten cells at +0.570 ± 0.038 with Q 36.39 on 9 df —
a move of 0.001 pp, which is why we keep it and label it. The design that would separate the
normaliser question — a level contrast at fixed network, fixed base and commensurable error budget
— is `gn2a`/`gn2b`, specified in advance in `bin/c84_normaliser_transfer.sh` and not run.

**T8 — n = 3 in ten of sixteen cells.** Seed is statistically null on this cluster (§6.3), and a
k-of-k per-seed agreement at n = 3 has exact p = 0.25 and carries no evidence, so we report no sign
tests. But ten cells rest on 3 v 3, and §6.1 shows two reruns of one such cell differing by
0.197 pp.

**T9 — Excluded data, and one batch that is two.** One batch (`ar1`, D = +0.697 ± 0.118) is
excluded as box-void throughout: it bound on the step-size guards asymmetrically, in the direction
that inflates D.

`hz3` carries a second, different defect, and it is a **configuration** defect, not a metadata one.
The batch is two submissions: twenty-one runs at job ids 4782007–4782027 in the clip box `−30:9.0`,
and three seed-5 runs — `chunk777`, `nodewise1d`, `chunk2325` — resubmitted 32,288 job ids later at
4814293–4814295 in the narrower box `−15:−2.3026`. Their `ENV` lines say so and
`results/all_runs.csv` records it faithfully; nothing here is repairable by fixing a column.
`BETA_CLIP` is the only effective difference: every `ARGS` flag matches the corresponding seed-4
run exactly.

Two things follow, and they are not the same thing.

*First, the box.* Sweeping all 30,000 probe records of all 24 runs, no coordinate of any run
reaches either rail before **step 81,000 = epoch 162**; from there the three narrow-box runs sit on
their floor to the end (peak 138/14,421, 100/4,851 and 46/4,851 coordinates), while all
twenty-one wide-box runs stay at 0/N throughout and the ceiling is never touched by anything. So
the box difference is **inert at the 100-epoch reading and live at the 200- and 300-epoch
readings**, one-sidedly, on the arm D favours. It is small — 0.95% of coordinates at its peak,
against the registered 5% occupancy gate, which the batch's scorer duly passes — but it is real and
it is asymmetric.

*Second, the hardware.* The resubmitted trio also ran on an A100 80 GB while their seed-5
`nodewise` partner ran, with the rest of the original submission, on an RTX 2080 Ti. The batch was
designed to assign GPU class **by seed** precisely so that a seed's four arms share it; the
resubmission broke that, and the batch's registered scorer still labels all four seed-5 runs
`gpu-2080ti-11g`. This mismatch applies at **every** budget, the 100-epoch reading included. It is
a defect in the registered scorer's metadata, not in its statistics; under our own file-freeze rule
we do not edit a registered scorer after its data exist, so the correction is recorded here, and
R2 makes the label true again.

Consequently §4.8's within-run pairing cancels seed, run and batch, but **not** the clip box (from
epoch 162) and **not** the GPU class (throughout). An earlier draft claimed both, and that was
wrong. The same applies to T = `nodewise1d` − `nodewise`; G and U are matched inside their pairs
at every seed and are unaffected.

Seed 5 is also the batch's per-seed outlier at 100 epochs — D(100) = **+0.148** against **+0.548,
+0.564, +0.586, +0.622, +0.990** — and unremarkable at 300 (+0.290, against a seed-2 low of
+0.168). We note explicitly that **neither defect explains that outlier**: the box is inert at 100
epochs, and the hardware term (§6.3: A100 − 2080 Ti = +0.112 pp) sits on the arm that would
*inflate* D, not deflate it. The 100-epoch outlier is unexplained. §4.8 reports the budget contrast
both with and without seed 5 for this reason, and a replacement seed-5 trio in the original box and
on matched hardware is R2 (§3.5).

Finally, for reuse: a scorer that groups on `beta_clip` drops exactly those three runs, keeps
`nodewise` seed 5, and reads an **unbalanced** D(300) = +0.464 ± 0.084 in place of the balanced
+0.428 ± 0.086. That is an artefact of the grouping, not a second estimate.

Neither `ar1`'s exclusion nor `hz3`'s split changes a **sign**. The `hz3` split does move one
verdict's **margin**, which is why §4.8 carries it inline rather than leaving it here.

**T10 — Filter sensitivity.** Several quantities in this corpus move by 0.5–0.7 pp between two
defensible row filters. Every number here is re-derived at write time under the single stated gate
(Eq. 11), and we recommend the same discipline to anyone reusing the data.

**T11 — Novelty scoping.** We claim no absolute priority. CAM-HD built the granularity ladder,
named the small-sample mechanism, and reported an interior optimum in 2020–2022; Zheng & Kwok
studied blockwise adaptivity in 2019; Choi et al. established tuning-protocol sensitivity in 2019.
What we add is count matching, the alignment null, the 1-D-tensor object, and the negative results
in §5.

**T12 — Selection on the test set; no validation split.** No held-out validation split exists
anywhere in this project. `plateau5` is a test-set quantity, the operating point (η, α₀, the
β-box) was chosen on it, and all the absolute numbers in T4 are argmaxes of ladders scored on
it; 418 distinct configuration cells were scored on that same test set over the campaign
(§3.3). Every absolute accuracy in this paper is therefore an optimistic estimate and none is
offered as a benchmark result. The within-batch contrasts are much less exposed — no arm and
no cell was selected, and §4.3 shows the reported set of count-matched contrasts is complete —
but they are measured at a test-selected operating point, and `D` moves −0.189 pp per decade
of η (§4.5). We cannot report a selection-free estimate of anything and we do not claim one.

---

## 8. Reproducibility

**One command.** The deposit reproduces every number in this paper:

    make reproduce            # every headline, re-derived and checked against the paper
    make reproduce-table2     # Table 2 and Figure 1 alone
    make figures              # regenerate all four figures from the CSV
    make verify               # md5 every file against the manifest

`make reproduce` runs in seconds on a laptop, needs `python3` and `matplotlib` and nothing
else — no GPU, no PyTorch, no cluster — and **exits non-zero if any headline fails to
reproduce**. It prints one line per number: *derived value | paper value | PASS/FAIL |
where it appears in this paper*. Its output at the time of writing is included in the
deposit as `REPRODUCTION-AUDIT.txt`.

**Artefact and DOI.** The deposit is ≈6 MB in 137 files, with `MANIFEST.md5` covering
every one of them. **DOI: pending**; a reserved DOI is minted at submission and written
into the paper, into `CITATION.cff` and into the Data-availability statement before
camera-ready. Until then the artefact is identified by its repository commit.

**Data.** `data/all_runs.csv`, 2,113 rows, one per run, with the full configuration
(network, dataset, batch size, granularity, base, meta, η, α₀, γ, augmentation, β-box,
hierarchical mode, λ, r, seed), the outcome columns (`best_test`, `final_test`,
`plateau5`, `plateau`, `auc`, epochs-to-threshold), the provenance columns (`job_id`,
`account`, `node`, `wallclock_min`), the two admissibility flags (`window_ok`,
`complete`), and a `dup_group` column marking the eighteen pairs of differently-named runs
that resolve to the same experiment (§3.3). Raw per-epoch series are the Slurm
`.out` files in `logs/raw_out.tar.gz`; each carries its own `ARGS:` and `ENV:` line, which
is the authority on what that run actually did. The shipped log set is 2,181 files; the two
clusters together hold 2,189 with an `ARGS:` line, plus the 12 un-ingested `sm3` runs, and we
state the shortfall rather than the shipped count alone.

**Attrition — every job we launched, and where each one went.** The ledger below reconciles
the Slurm output directories on both clusters against the run table, so that a reader can
confirm nothing was dropped silently. It is exhaustive: the two categories of loss are
"crashed before epoch 1" and "budget too short for a plateau window", and neither touches a
count-matched arm.

**Table 3 — attrition ledger.** Job counts; GPU-hours where a wallclock was recorded. The
exclusions are applied in the order shown, which matters: 425 rows fail `window_ok`, but 25 of
them have no readable `plateau5` and are removed first, so the `window_ok` line reads 400.

| stage | n | GPU-h | note |
|---|---|---|---|
| Slurm `.out` files on the two clusters | 2,193 | — | `runs/` + `runs_alice2/` + the on-cluster copies |
| — infrastructure jobs, no training | −4 | — | `gtest`, `gtest2`, `mo-smoke`, `ts-pretok`; no `ARGS` line, no CSV row |
| **jobs that entered the training script** | **2,189** | — | each logs one `ARGS` line |
| — crashed or cancelled before epoch 1 | −64 | ≈0 | itemised below; **not one logged a single epoch** |
| — completed but not yet ingested (`sm3`) | −12 | 10.1 | 12/12 complete at 100 epochs; §6.1 |
| **rows in `results/all_runs.csv`** | **2,113** | 1,582.2 | 2,098 carry a wallclock |
| — no readable `plateau5` | −25 | } 66.3 | 2–5-epoch smoke tests |
| — `window_ok = 0`, `plateau5` present | −400 | } | budget ≤ 20 epochs; `window_ok` is `epochs_done > 20` |
| — `window_ok = 1`, `complete = 0` | −17 | } | truncated runs; `complete` is `epochs_done ≥ 0.95 × requested` |
| **admissible** | **1,671** | 1,515.9 | the gate of Eq. 11 |

**The 64 that never produced an epoch**, by cause, read off their own tracebacks:

| n | cause | batches |
|---|---|---|
| 36 | `LAM='na'` reached `float()` in the patched `HF.py` | `am4`, `amx` |
| 12 | `BETA_CLIP` without the colon separator reached `str.split(':')` | `hs`, `ha` |
| 6 | a block partition applied to the wrong network depth | `sc` |
| 6 | CUDA device-side assert (CIFAR-100 label range) | `uc5` |
| 4 | Slurm `CANCELLED` | `a0`, `g1` |

All 64 died in `build_optimizer` or in the first minibatch, all are configuration errors that
a later pre-submission guard now catches, and none consumed measurable GPU time. **None is in
a count-matched arm**, so no contrast in Table 2, §4.6 or §5.4 is affected. Two of the five
causes do touch material reported elsewhere and we name the contact rather than leave it to be
found: the four Slurm cancellations are all `scalar`-arm runs (`g1-adamw-scal-s{0,1,2}` at
α₀ = 1e-6, `a0-scal-1e3-s0` at α₀ = 1e-3), so the `scalar` column of §4.1's α₀ table is short
by four runs relative to what was submitted — which is one of the reasons that table is
labelled descriptive and cross-batch there, and why the in-batch η pair above it carries the
claim; and the 48 `am4`/`amx`/`hs`/`ha` crashes are all hierarchical-pooling runs, in the
region of §2.4 and §5.9 that Appendix A.9 already marks as carried from the project record
rather than re-derived.

**The 442 inadmissible rows are not failures; they are short-budget probes.** All 425
`window_ok = 0` rows requested ≤ 20 epochs (392 at 20, 33 at 2–5) and so could never carry a
five-epoch plateau at their requested budget. Only 17 of the 442 are full-budget runs, and those
are the truncated ones. By granularity, the 442 are: `layerwise` 136, `weightwise` 111,
`nodewise` 108, `resnet18_blocks` 56, `scalar` 30, no-partition baseline 1 — i.e. attrition is
concentrated in the coarse and the maximally fine arms of the exploratory ladders, which is
where the 20-epoch probes were run.

**Attrition inside the primary contrasts is exactly zero.** The sixteen batches that carry a
count-matched contrast contribute **272 runs, of which 272 are admissible**. More strongly:
**every** uniform-chunk, `nodewise1d` and `permnode` run in the corpus — 214 rows — is
admissible, so no count-matched cell could have been lost to the gate even in principle.
Submitted `n` equals admissible `n` in all sixteen cells of Table 2 and in the excluded
`ar1` cell.

**One registration deviation, disclosed here as well as in §5.4.** `aw1`'s registered
scorer (`analysis/c88_scorers.py`, committed before the runs) specifies "12 jobs: `nodewise`
and `chunk777` × 6 seeds". The submission script `bin/c90_awbase.sh` ran 4 arms × 3 seeds =
12 jobs instead: the same job count, four arms instead of two, and half the registered
per-arm power on the primary. Every other batch's realised seed set matches its submission
script's `SEEDS` line.

**Compute.** 2,098 runs carry a wallclock; they total **1,582 GPU-hours** over 29 distinct
nodes and two accounts, on NVIDIA L4 24 GB, RTX 2080 Ti 11 GB, A100 80 GB and A100 MIG
40 GB partitions. GPU class is recorded per run and was measured to carry no systematic
offset between arms (§6.3); every primary is within batch, so a per-node offset shared by
the two arms cancels identically. The one exception, where a resubmission broke arm-level
hardware matching inside a single seed, is §7 T9.

**Environment.** One virtual environment, both accounts, verified identical at write time:

| | |
|---|---|
| Python | 3.10.4 (`Python/3.10.4-GCCcore-11.3.0`) |
| PyTorch | **2.0.1+cu118** |
| CUDA (torch build) | **11.8** |
| torchvision | 0.15.2+cu118 |
| numpy | 1.26.4 (torch 2.0.1 is incompatible with numpy ≥ 2) |
| scheduler | Slurm |

**Seeds.** Every run records its seed; seeds are 0–11. Batches specify their seed set in the
submission script and the scorers assert the registered set is present before scoring. The
table below gives, per batch, the seeds actually realised — which is not always the
registered set, and where it is not, we say so.

**Per-batch provenance.** Every batch behind a cell in Table 2, with the script that
submitted it, the scorer registered for it, that scorer's md5, the seeds realised, the
β-box, and the account. **Five batches have no scorer that was registered before their
runs existed**; we mark them rather than let the reader infer coverage from §3.4.

| batch | submission script | registered scorer | scorer md5 (first 12) | seeds realised | n | β-box | account |
|---|---|---|---|---|---|---|---|
| `cc1` | `c81_concordance.sh` | `c81_cc1_score.py` | `c138eab327c1` | 3,4,5 | 12 | −15:−2.3026 | A |
| `mm1` | `c76_matched_m_partition.sh` | `c76_mm1_score.py` | `57e48c32e066` | 0,1,2 | 6 | −15:−2.3026 | A |
| `pp1` | `c77_permuted_partition.sh` | `c77_pp1_score.py` | `3c6aa6f97627` | 0,1,2 | 9 | −15:−2.3026 | A |
| `bn1` (G only, no D) | `c78_degenerate_tail.sh` | `c78_bn1_score.py` | `285632b3b8a6` | 0,1,2 | 9 | −15:−2.3026 | A |
| `gn1` | `c84_normaliser_transfer.sh` | `c84_gn1_score.py` | `82c515d1ad49` | 0–7 | 24 | −15:−2.3026 | B |
| `ml2` | `c94_meta_ladder.sh` | **none registered** | — | 0,1,2 (each run twice) | 24 | −15:−2.3026 | B |
| `rl3` | `c87_rule11_ladder.sh` | `c87_rl3_score.py` | `b008216753a0` | 0,1,2 | 24 | −30:9.0 | B |
| `fa1` | `c82_field_wideclip.sh` | `c82_fa1_score.py` | `b96ab2080cfa` | 0–5 | 24 | −25:−2.3026 | A |
| `hz3` | `c87_horizon_300ep.sh` | `c87_hz3_score.py` | `16769a161630` | 0–5 | 24 | −30:9.0 **and** −15:−2.3026 | A |
| `aw1` | `c90_awbase.sh` | `c88_scorers.py` | `0363bcccb4d3` | 0,1,2 | 12 | −15:−2.3026 | B |
| `nl1` | `c92_norm_ladder.sh` | **none registered** | — | 0,1,2 | 24 | −15:−2.3026 | A |
| `g3m` | `c83_gen_r34_merged.sh` | `c83_gen_score.py` | `ffdabe0a1790` | 0–8 | 36 | −15:−2.3026 | A |
| `r50` | `c93_resnet50.sh` | **none registered** | — | 0,1,2 | 12 | −15:−2.3026 | A |
| `gc1` | `c83_gen_c100_screen.sh` | `c83_gc1_score.py` | `5e775f417031` | 0,1,2,3 | 8 | −15:−2.3026 | A |
| `gm2` | `c91_c100_mech.sh` | **none registered** | — | 0,1,2 | 12 | −15:−2.3026 | B |
| `sm3` (not ingested) | `c96_secondmoment.sh` | **none registered** | — | 0,1,2 | 12 | −15:−2.3026 | A |
| `ar1` (excluded) | `c79_argmax_robustness.sh` | `c79_ar1_score.py` | `2396e5cf2372` | 0,1,2 | 12 | −15:−2.3026 | A |

Three things this table is meant to stop a reader from having to guess.
(i) **The β-box is not constant across cells**, so `rl3` (−30:9.0) and `fa1`
(−25:−2.3026) are not box-matched to the rest, and `hz3` contains one seed whose two arms
sit in *different* boxes (Figure 3, §4.8, T9). Nothing is pooled across boxes without the
between-box Q partition of §4.4 being printed alongside.
(ii) **`ml2`'s three seeds were each run twice** under two names; the run table's `dup_group`
column records the eighteen such pairs corpus-wide, and any n, se or t computed over rows
sharing a `dup_group` averages within the group first and counts n as the number of
distinct groups. That is what makes `ml2` a 3 v 3 cell with se 0.195, not a 6 v 6 cell with
se 0.142 (§6.1). The reproduction audit enforces the rule, so a reader cannot accidentally
recover the wrong number.
(iii) **Five batches have no pre-registered scorer** — `ml2`, `nl1`, `r50`, `gm2` and `sm3`.
`nl1` alone supplies two of Table 2's rows and both of the single-batch levels of the
base-optimiser moderator in §4.4. Their CSV values were checked field-by-field against their own
runs' `ARGS:` lines and are correct; what is missing is not the data but the
commitment-before-the-fact, and we mark it rather than claim coverage we do not have. The
replication that repairs the most exposed of them is R3 (§3.5).

**Code.** The optimiser is the released MetaOptimize `HF.py` plus the patches in
`patches/` (`patch_chunkwise.py`, `patch_nodebn.py`, `patch_permnode.py`,
`patch_zpool.py`, the probe patches, and the augmentation patch), each of which carries an
identity test against the authors' own working `blockwise` path. Analysis is 60+ scorers
under `analysis/`; the ones that gate a verdict are named in §3.4 and quoted verbatim. The
figures are `analysis/c98_figures.py` and contain no typed value.

**Registration.** Batches carry a submission script under `bin/` with numbered
pre-submission guards: the run table must be present; the required patches must be present
in the live tree; group counts are **measured** on the instantiated optimiser and asserted
equal to the registered values; there must be no name collision; the comparator batch must
exist; and there must be disk and queue headroom. Since the failures of §6.1 the guards also
enforce STANDING RULES 20 and 21 mechanically: the scorer must already exist and pass its own
selftest before a job is composed, the composed command line is rejected if any flag repeats
or if it does not match the declared design, and the first launched job's actual `ARGS:` line
is re-read after `sbatch`. Decision rules and bands are committed before submission.
`analysis/c88_scorers.py --selftest` runs 31 assertions in both directions; it currently
reports one failure, `S6e`, which asserts that the count-matched partition rows are all one
base optimiser — an assertion made true at cycle 88 and made false, deliberately, by the `aw1`
and `nl1` batches.

**An integrity check a reader can run on our own logs.**
`analysis/argsline_guard.py` sweeps every run's own `ARGS:` line for a repeated flag,
because argparse silently takes the last occurrence and a submission script can therefore
run a different experiment from the one it declares. Over the 2,189 runs carrying an
`ARGS:` line on both clusters it finds exactly 36 with a repeated flag, in two batches, and
those two batches are reported as void-as-designed in §6.1. The partition axis, the budget
axis and the step-size axis (`--alg-base`, `--stepsize-groups`, `--meta-stepsize`,
`--alpha0`, `--num-epochs`, `--seed`, `--normalizer-param-*`) are single-occurrence in every
run in the corpus. We recommend the check to anyone running batch experiments through a
shell wrapper; it cost us two batches to learn, and §6.4 records the blind spot the tool
itself still had when we found it.

**Deviations from the parent's configuration, stated so absolute numbers are not
misread.** (i) We enable RandomCrop + horizontal flip; the parent's text and released code
appear not to. Without augmentation ResNet-18 memorises CIFAR-10 within an epoch and there
is no optimisation headroom for a step-size method to exploit, so we regard augmentation as
scientifically necessary — but it means our absolute accuracies are not comparable to the
parent's. (ii) Our headline partition programme uses a Lion meta-optimiser where the
parent's SGDm arm uses Adam. (iii) We clip β to a box; the parent mentions no clipping.
Box occupancy is measured per run, **per coordinate** from the `n_at_lo`/`n_at_hi` rails
and never from the 62-element per-tensor summary — reading the summary instead reported
0.000000 occupancy on 24 runs that were clipped in every record and inverted an arm
ranking, which voided the `ar1` batch (§3.3).

**What a reader can falsify on their own hardware in an afternoon.** Merge your
one-dimensional tensors into one step-size group each and measure the difference at fixed
group count; and re-tune both arms of any granularity comparison you have and see how much
of the gap survives.

---

## 9. Conclusion

"The number of step sizes" is not one experimental variable. Within one batch, moving the shared
meta-stepsize by a decade moves the layerwise-minus-scalar gap from +3.291 to +0.655 pp; the
initial step size flips the sign of the ordering at the parent's own configuration; and the group
count, at fixed partition family, is worth at most +0.34 pp across 0.47 decades with an
inconsistent sign.

What remains after all three are controlled is a real effect. At **matched group count**, replacing
an architecture-aligned partition by a uniform one is worth a positive amount of accuracy in
**every one of 16 within-batch cells** across three networks, two datasets, four base
optimisers, two meta-stepsizes and two budgets; it survives tuning each arm to its own optimum
(−0.090 ± 0.178, itself an upper bound in magnitude); it is present and resolved at 3× the budget;
and its variation across configurations is dominated by one identified moderator — the base
optimiser carries 88% of the between-cell heterogeneity (Q 32.2 / 3 df), and inside a fixed base
the effect is homogeneous (Q 4.21 / 7 df, p 0.76, τ 0.000, pool +0.556 ± 0.045). Architecture
**alignment** is bounded out as the principal carrier, in one batch at one design point: holding
the count *and* the per-tensor size multiset and permuting only membership is worth
−0.009 ± 0.157 pp, 95% CI [−0.317, +0.298] = [−55%, +51%] of D, against an MDE of 0.440 pp.
A moderate alignment contribution is not excluded and a further batch is running to bound it more
tightly. The surviving carrier is the group-size distribution, which takes +0.590 ± 0.107 (t 5.53)
of the same three-arm decomposition.

**We cannot say which property of it, and the design cannot tell us.** At fixed count this corpus
contains one contrast type; twenty candidate statistics collapse to two equivalence classes and the
best-fitting one is an arm indicator in disguise. Eight further mechanisms were examined and three
are refuted, with the other five narrowed, unseparable or undecidable: √N averaging
(untested, not refuted, and its literature attribution withdrawn), the meta-gradient correlation
field (anti-concordant at t −11.14), size-1 groups as such (+0.115 ± 0.133), the tail as a
universal carrier (SGDm-specific: pooled D − G +0.514 ± 0.056 under SGDm against +0.047 ± 0.124
under AdamW), Choi-style inclusion (granularity is state, not hyperparameters), base-optimiser
normalisation (RMSProp and AdamW differ by +0.694 ± 0.266), and any size-distribution summary
statistic (not identifiable). An eighth candidate, the aligned arm's accuracy level, is neither
confirmed nor separable: it is aliased with the network and the base optimiser, and the
within-batch separator we registered for it issued no verdict (§5.6, §7 T7). And D is not
predictable out of sample from any configuration property this design can resolve.

The honest description of this paper is therefore: **a robust, replicated, count-matched
measurement; an identified moderator for its heterogeneity that is not yet replicated at three of
its four levels; a single-batch bounded null that excludes the mechanism most people would guess as
the principal carrier without excluding it as a contributor; a prescription that costs nothing and
works under three of four base optimisers; and no mechanism.** We would rather publish
that than a mechanism that does not survive its own controls — this project produced one of those
too, and killed it (§5.7) — or than a refutation that does not survive its own registered scorer,
which this project also produced and withdrew (§5.6).

**The experiments that would break the impasse**, in the order we would run them. Three are in
flight and are described with their decision rules in §3.5: the alignment replication with the
permutation seed decoupled (R1), the box- and hardware-matched budget trio (R2), and the
base-moderator replication at fresh seeds (R3). A fourth, R4, tests the one untested corner of the
base × meta grid that §6.1's void batch failed to reach.

Beyond those, the decisive mechanism design is additive rather than subtractive. Every
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

Two further designs are named because this paper states limits it cannot close without them. For
the level covariate, a normaliser or width contrast run at a **commensurable error budget** —
`gn1` failed its own commensurability gate at a 1.37× budget ratio, and `gn2a`/`gn2b` were
specified for exactly this and not run. And for external validity, the same four partitions applied
as a fixed per-group learning-rate scale on a plain SGDm or AdamW run with **no meta-learning at
all**, which is the only design in the queue that would convert an internal audit of one framework
into a claim about step-size granularity.

---

## Appendix A. Discrepancy register

Numbers carried in this project's internal record that **did not reproduce** at write time, and
what replaced them.

**A.1 — The meta-optimiser axis does not exist.** The record carried "meta axis (ResNet-18/CIFAR-10,
base = SGDm): Lion +0.727 · Adam +0.554 · RMSProp +0.357". The arithmetic is right and the labels
are wrong: the `ml2` batch's two halves both ran meta = Lion (§6.1), so +0.554 and +0.357 are two
nondeterministic reruns of one configuration at the same seeds, not two meta-optimisers. Every
partition-programme run in the corpus (367/367) is meta = Lion. **No meta-optimiser axis may be
reported.** Consequently the record's "G is not null under an RMSProp meta (+0.276, t 3.21)" is also
mislabelled: that is `ml2`'s second Lion rerun, and its companion reads +0.071 ± 0.103.

**A.2 — Two values from the banned metric column.** The record carried
G(AdamW) = +0.226, t 3.23 and hz3 "the gap grows with budget, +0.229, t 3.27". Both come from
20-epoch and 50-epoch trailing windows respectively. On the primary 5-epoch window:
G(AdamW) = **+0.232 ± 0.089, t 2.62**; and the budget effect is **−0.149 ± 0.105, t −1.42**, i.e. a
decline that does not resolve — **−0.207 ± 0.107, t −1.94** once `hz3`'s mismatched seed-5 pair is
set aside (§7 T9, §4.8). Both replacements match the project's own later corrections; we record the
originals so the supersession is visible. Note that the 50-epoch reading is not merely a discarded
internal note: it is the **registered primary** of `analysis/c87_hz3_score.py`, whose verdict is
`GROWS`. We keep `plateau5` as this paper's primary metric and print both, rather than quietly
preferring the window that suits the narrative.

**A.3 — Batch as a large random effect: not reproduced.** The record carried
BATCH F(62,85) = 5.47, p = 6.9e-13, sd_batch ≈ 0.21 pp. Under every cell definition we could
construct, restricted to converged runs, batch is not resolvable (F(39,172) = 0.71; random-effects
sd_batch = 0.000 against within-arm sd 0.193). The seed half of the claim reproduces
(F(30,30) = 1.50, p = 0.138). See §6.3 for the replacement statement.

**A.4 — Heterogeneity τ, and the two Q's.** The record carried τ = 0.285 pp against 0.137 pp
measurement noise. DerSimonian–Laird with Welch standard errors gives **τ = 0.215 pp** against an
rms se of **0.151 pp** on the twelve-cell pool as first published, and **τ = 0.203 pp** against
**0.152 pp** on the eleven-cell pool after `gn1`-GroupNorm is removed (§4.4). The ratio is 1.3–1.4×,
not 2×. **Two Q values are in circulation and both are correct.** Computed from full-precision arm
means in `results/all_runs.csv` — the convention this paper adopts, because it is what the deposited
code computes — Q = **43.19** on 11 df (36.40 on 10 dropping GroupNorm). Computed from the
three-decimal (D, se) pairs *as printed in Table 2*, Q = **43.01** (36.29), with pool +0.545
(+0.570), τ 0.214 (0.203). The gap is rounding of the printed table and nothing else; an earlier
appendix described it as "reproduces exactly", which a 43.2-versus-43.0 mismatch does not support.
The between-base share of §4.4 is 88.4% under both conventions. The conclusion is unchanged and is
now stronger: the excess over measurement error is real, and §4.4 attributes 88% of it.

**A.5 — The prediction null has weakened slightly with two new batches, and again with a removal.**
The record stated that inside CIFAR-10 the corpus mean *wins* out of sample (0.2791 vs 0.2863) with
a sign test of 8/11, p = 0.227. With `r50` and `ml2` added the headroom models were marginally
ahead inside CIFAR-10 and the sign test was 9/11, p = 0.065. After the `gn1`-GroupNorm removal the
design-point set is 10, the best model wins inside CIFAR-10 by 0.040 RMSE (0.2791 → 0.2395, −14%)
and the sign tests are 8/10 (p 0.109) overall and 7/9 (p 0.180) inside CIFAR-10. The verdict is
unchanged — nothing reaches significance, the margin is dominated by one CIFAR-100 fold, the
functional form is a best-of-ten selection, and the power bound |r| ≥ 0.632 is not approached — but
the null now holds by less than the earlier draft implied, and we report that rather than the older
phrasing.

**A.6 — `fa1`'s ceiling caveat, stated precisely.** The record variously described `fa1`'s
`nodewise` arm as grazing the ceiling in "5 of 6 seeds". The scorer's own occupancy table: all 24
arms read `rec_lo` 0.0000 exactly (the floor is free), and on the `nodewise` arm five of six seeds
have non-zero `rec_hi`, of which **three** exceed the 5% gate (0.1673, 0.2193, 0.0601). Both
statements are true of different thresholds; we quote both.

**A.7 — Adaptation versus a frozen β.** The record carried "+2.551 pp over frozen β". The frozen-β
runs on disk are 20-epoch probes and fail this paper's admissibility gate (`window_ok = 0`), so the
claim is **not re-derivable** under our own stated rule and is dropped rather than restated.

**A.8 — Corpus size.** The record variously says 1,960 / 2,077 / 2,113 runs and ~1,200–1,400
GPU-hours. At write time: **2,113 rows, 1,671 admissible, 1,582 GPU-hours** summed over the 2,098
runs carrying a wallclock, with 2,189 jobs having entered the training script and 12 completed
`sm3` runs awaiting ingest (§8, Table 3). The correction register runs to entry 126.

**A.9 — Two blocks carried from the record without re-derivation.** Two statements are **not**
re-derived at write time and are marked where they appear: (i) the "6 of 6 fits with the wrong
sign" count for the drift-versus-group-size instrument (§5.1) — the instrument's own interpretation
is disowned in the same paragraph, so nothing rests on the count; and (ii) the `M0 shrink` and
`M1 additive r` pooling failures (§2.4, §5.9), whose replacement is the `zpool` sweep, which **was**
re-derived on `plateau5` and carries that section's argument on its own. No claim in §4 depends on
either.

**A.10 — Two headline conventions, superseded by measurement.** Two phrases the record carried are
withdrawn on evidence rather than on taste. *"Byte-identical contrast"*, used of the twelve-cell
pool, is false three times over: the cells span three step-size clip boxes, `hz3` spans two boxes
inside a single cell, and a registered scorer's own header forbids pooling across boxes. The
replacement is measurement, not silence: between-box Q = 1.08 on 2 df (p 0.58) against within-box
Q = 35.32 on 8 df over the eleven-cell pool (§4.4). And *"a CSV metadata defect"*, used of `hz3`'s
three seed-5 rows, is wrong in the direction that matters: the run table is faithful to those runs'
own `ENV` lines and the defect is in the experiment (§7 T9).

---

## Appendix B. The full arm table for the primary contrast

`plateau5` arm means with sem, ResNet-18/CIFAR-10 unless stated, all within batch. The `β-box`
column is carried so a reader can redo §4.4's between-box partition of Q.

| batch | β-box | nodewise | chunk777 | nodewise1d | chunk2325 |
|---|---|---|---|---|---|
| cc1 | −15:−2.3026 | 91.890 ± 0.077 | 92.617 ± 0.185 | 92.706 ± 0.139 | 92.717 ± 0.046 |
| mm1 | −15:−2.3026 | 92.044 ± 0.058 | 92.529 ± 0.150 | — | — |
| pp1 | −15:−2.3026 | 92.012 ± 0.129 | 92.593 ± 0.058 | — | — |
| pp1 `permnode` (m = 14,420) | −15:−2.3026 | 92.003 ± 0.090 | | | |
| bn1 | −15:−2.3026 | 92.184 ± 0.033 | — | 92.611 ± 0.025 | 92.906 ± 0.041 |
| gn1 | −15:−2.3026 | 92.000 | 92.587 | — | — |
| gn1 GroupNorm arms (no contrast formed)§ | −15:−2.3026 | 89.330 | 89.532 | — | — |
| ml2 (3 seeds, each run twice) | −15:−2.3026 | 92.064 | 92.519 | 92.683 | 92.856 |
| rl3 @1e-4 | −30:9.0 | 91.908 | 92.589 | 92.664 | 92.653 |
| rl3 @3e-4 | −30:9.0 | 92.507 | 93.098 | 92.898 | 93.115 |
| fa1 @3e-4 | −25:−2.3026 | 92.327 | 92.957 | 92.976 | 92.975 |
| hz3 @300 ep | −30:9.0 (seed-5 chunk arms at −15:−2.3026) | 92.816 | 93.244 | 93.153 | 93.096 |
| aw1 (AdamW) | −15:−2.3026 | 92.978 | 93.257 | 93.069 | 93.301 |
| nl1 (SGD) | −15:−2.3026 | 91.156 | 92.191 | 91.848 | 92.373 |
| nl1 (RMSProp) | −15:−2.3026 | 92.155 | 93.129 | 93.071 | 93.091 |
| g3m (R34) | −15:−2.3026 | 91.336 | 92.002 (chunk835) | 92.094 | 92.265 (chunk2500) |
| r50 (R50) | −15:−2.3026 | 89.631 | 90.513 (chunk295) | 90.681 | 90.833 (chunk884) |
| gc1 (C100) | −15:−2.3026 | 70.311 ± 0.227 | 71.951 ± 0.092 (chunk771) | — | — |
| gm2 (C100) | −15:−2.3026 | 70.569 | 72.054 (chunk771) | 71.932 | 72.000 (chunk2293) |
| `ar1` (excluded, box-void) | −15:−2.3026 | — | — | — | — |
| `sm3` (not ingested; raw `.out` only) | −15:−2.3026 | 93.103 | 93.244 | 93.019 | 93.315 |

§ The `gn1` GroupNorm arms are reported here for completeness because the batch's registration
requires its four-arm table to be reported whole. **No contrast is formed from them anywhere in
this paper**: the registered scorer's commensurability gate fired at a 1.37× error-budget ratio and
issued no verdict (§7 T7). The two `gn1` lines above share one batch and 24 runs.

`sm3`'s four arm means are re-derived from its raw `.out` series; its twelve runs are not in the
deposited run table, so no claim in this paper rests on them and `make reproduce` does not check
them. `ar1`'s arm means are omitted because the batch is box-void and quoting them invites the
contrast we exclude; its D (+0.697 ± 0.118) is quoted in §4.3 solely so the exclusion is visible.

---

## End matter

**Data availability.** The complete run table (`results/all_runs.csv`, 2,113 rows), the
raw per-epoch Slurm logs (2,181 `.out` files, each carrying its own `ARGS:` and `ENV:` line),
all submission scripts (`bin/`), all optimiser patches (`patches/`), all registered scorers
(`analysis/`), the figure code and the reproduction audit are deposited as a single archive.
**DOI: pending** — a reserved DOI is minted at submission and inserted here and in
`CITATION.cff`; until then the artefact is identified by its repository commit. The archive is
≈6 MB, carries an md5 manifest for every file, and reproduces every number in this paper with
`make reproduce` on a laptop in seconds, with no GPU and no dependency beyond `python3` and
`matplotlib`. **No number in this paper requires data that is not in that deposit.** Two
exceptions, stated because they are exceptions: the per-group β trajectories (`probe*.jsonl`,
≈42 GB) are excluded for size and are available from the authors on request, with the
box-occupancy summaries derived from them carried in the run table's `beta_clip` column and in
the scorers' printed output; and the twelve `sm3` runs quoted as a consistency check in §4.4,
§5.4 and Appendix B are not yet ingested into the run table, which is why no claim rests on them.

**Code availability.** The optimiser is the released MetaOptimize `HF.py` plus the patches
in `patches/`, distributed as patches rather than as a fork, each carrying an identity test
against the authors' own working `blockwise` path (`tests/`). Analysis code, figure code
and the reproduction audit are released under MIT; the run table, logs and documentation
under CC-BY-4.0; the patches carry the parent work's license.

**Ethics.** No human or animal subjects and no personal data. CIFAR-10 and CIFAR-100 are
standard public benchmarks used under their stated terms; no other data was collected. The
work is a methodological audit of an optimisation method and we see no dual-use or
deployment risk specific to it. The one ethical exposure we do carry is a conflict of
interest, disclosed in full below rather than in a footnote, and the mitigation for it was
put in place before the results existed rather than after.

**Competing interests.** **A supervising author of this work is a co-author of
MetaOptimize (Sharifnassab, Salehkaleybar & Sutton), the method this paper audits.** We
state this plainly because several of this paper's results are negative about that method:
the 1.8-to-4.2 pp deficit against a tuned schedule (§7 T4), the finding that four
fifths of the reported granularity benefit at the parent's own default meta-stepsize is
tolerance to an over-large meta-step rather than accuracy (§4.1), and the mechanism verdicts of
§5. The mitigation is procedural and is auditable in the deposit: every
decision rule and acceptance band for the negative results was committed to version
control **before** the corresponding runs were submitted, in a scorer that is run unedited
and whose printed verdict is quoted rather than paraphrased (§3.4, §6.2); the supervising
author had no role in setting those rules; and where a batch has **no** such
pre-registered scorer we say so explicitly in the provenance table in §8 rather than
letting the reader assume coverage. ⟨If the final author list includes a further co-author
of the parent paper, that must be stated here in the same sentence, and §5.9's negative
result on hierarchical partial pooling — an idea originated by a proposed co-author — must
be disclosed as a second, independent conflict of the same kind.⟩ The authors declare no
financial competing interests.

**Funding.** ⟨To be completed by the authors with any grant identifiers.⟩ This work was
carried out as an MSc research project at LIACS, Leiden University, and received no
dedicated project funding; compute was drawn from the institutional allocation
acknowledged below. The absence of a compute budget is a scope limit rather than a
formality: it is the reason ImageNet-scale replication is out of reach (§7) and the reason
the additive tail experiment proposed in §9 is registered but unfunded.

**Acknowledgements.** This work was performed using the compute resources from the
Academic Leiden Interdisciplinary Cluster Environment (ALICE) provided by Leiden
University. We thank the ALICE support team. ⟨Any further acknowledgements to be added by
the authors; note that a contribution of idea origination is co-authorship, not an
acknowledgement — see Author contributions.⟩

**Author contributions.** Stated in CRediT terms. ⟨The author list is to be finalised by
the authors; the roles below describe the work as it was actually done and must be
reassigned, not rewritten, if the list changes.⟩
**M. Ahmaditeshnizi** — Conceptualization (equal), Methodology, Software (the chunkwise,
1-D-tensor, permuted-node and probe partitions and their identity tests, as patches to the
released MetaOptimize implementation), Validation, Formal analysis, Investigation (all
2,113 runs), Data curation, Writing – original draft, Visualization, Project
administration.
**S. Salehkaleybar** — Conceptualization (equal), Supervision, Resources, Funding
acquisition, Writing – review & editing, and continuity with the parent work. Explicitly
**not** involved in setting the pre-registered decision rules or acceptance bands used for
the negative results in §5.
⟨A third contributor originated the hierarchical partial-pooling design evaluated and
withdrawn in §2.4 and §5.9. Idea origination of that specificity is a substantial
intellectual contribution and is co-authorship rather than an acknowledgement; the authors
are to settle inclusion and order before submission.⟩
All authors accept accountability for the integrity of the work as a whole.

**Use of AI assistance.** Analysis scripts, batch submission scripts, the correction
register, the figures and this draft were produced with substantial assistance from a
large language model operating on the project repository under human direction, including
at the analysis-design stage and not only at the writing stage. We disclose this as a
first-class integrity item rather than a footnote, and we state the controls that make it
checkable rather than asking to be trusted. Every number in this paper is re-derived from
the run table or the raw logs by committed code at build time and asserted against what the
paper prints (`analysis/c98_reproduce.py`, in the deposit; it exits non-zero if any
headline fails to reproduce); registered decision rules and bands were committed to version
control before the corresponding runs were submitted; and the discrepancies this procedure
surfaced between the project's internal record and the data are recorded in Appendix A
rather than corrected silently. Several claims were withdrawn by that procedure during
writing — an alignment refutation downgraded to a bounded null, a mechanism refutation
withdrawn because the batch's own registered scorer refuses to compute the contrast it
rested on, a budget flatness claim demoted to an unresolved trend, and a variance claim that
did not reproduce — and two whole batches were found to have run a different experiment from
the one they declared (§6.1). All of those outcomes are reported.

**Correspondence.** ⟨author email⟩.
