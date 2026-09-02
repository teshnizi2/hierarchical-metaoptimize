# Rewrite package `alignment-null`

**Closes:** gate blocking item #3, Q02, Q14, red-team #4.
**Target document:** `paper/DRAFT-v2.md` at commit `06d6539`. **This package does not edit that
file.** It supplies finished prose plus exact replacement text, keyed to the headings and the
line ranges it replaces, so an integrator can apply it without judgement calls.

**The single change this package makes.** The permutation result is currently written as a
**refutation** ("alignment is not the carrier", "alignment as such does nothing", "alignment is
worth nothing"). The measurement is an `n = 3` v `3`, single-batch, single-cell null whose 95%
interval spans from −55% to +51% of the effect it is supposed to explain. That is enough to
**exclude a large alignment effect and not enough to exclude a moderate one.** Everywhere the
document asserts the refutation, it is replaced by the bounded statement, with the interval, the
minimum detectable effect and the registration defect printed inline rather than deferred.

**What is *not* changed.** The measurement itself, the registered scorer, its `NULL` verdict, the
`A + B = D` receipt, and the direction of the finding. `A` is still the smallest leg by a wide
margin and `B` is still resolved at `t 5.5`. Nothing here rescues alignment as a carrier; it
stops the paper claiming a precision it does not have.

---

## 0. Re-derivation ledger

Everything below was re-derived at write time from the raw per-epoch `.out` series, not from the
CSV `plateau` column and not from any prose in the project record.

### 0.1 Provenance

| item | value |
|---|---|
| batch | `pp1` (9 runs, alice), `bin/c77_permuted_partition.sh` |
| raw series | `/Users/teshnizi/Saber Optimization/alice-backup/runs/pp1-{node,perm,ch}-s{0,1,2}-*.out` |
| probes | `/Users/teshnizi/Saber Optimization/alice-backup/runs/pp1/probe_*_pp1_s*` |
| registered scorer | `analysis/c77_pp1_score.py`, run **unedited**, `--selftest` **139/139 PASS** |
| config | ResNet-18 / CIFAR-10 / SGDm base / Lion meta / η = 1e-4 / α₀ = 1e-3 / 100 ep / `AUGMENT=1` / `BETA_CLIP=-15:-2.3026` |
| admissibility | all 9 runs `window_ok == 1`, `complete == 1`, `epochs_done == 100`; `P0 9/9`, `P0.2 9/9` (`n_beta` 14420/14420/14421 measured from allocated β), `P0.3 9/9`, `P0.4 9/9 box-free` on all four per-coordinate rails |
| metric | `plateau5` = mean test accuracy over epochs 95–99. The `plateau` column (mean-of-last-20) is **not** used anywhere in this package |

### 0.2 The three arms, `plateau5`, re-derived from the `.out` series

| arm | granularity | m | s0 | s1 | s2 | mean | sem (n=3) |
|---|---|---|---|---|---|---|---|
| `node` | `nodewise` | 14,420 | 92.114 | 91.756 | 92.166 | **92.0120** | 0.1289 |
| `perm` | `permnode<S>` | 14,420 | 92.082 | 92.102 | 91.824 | **92.0027** | 0.0895 |
| `ch` | `chunk777` | 14,421 | 92.572 | 92.702 | 92.504 | **92.5927** | 0.0581 |

These reproduce the scorer's own printed arm table (`92.012 ±0.129`, `92.003 ±0.090`,
`92.593 ±0.058`) and the nine CSV `plateau5` values exactly.

### 0.3 The three legs

`se(leg) = sqrt(sem_x² + sem_y²)`; `t = leg / se`.

| leg | definition | value | se | t |
|---|---|---|---|---|
| **A** (alignment) | `permnode − nodewise` | **−0.0093** | 0.1569 | **−0.059** |
| **B** (size distribution) | `chunk777 − permnode` | +0.5900 | 0.1067 | +5.529 |
| **D** (both) | `chunk777 − nodewise` | +0.5807 | 0.1414 | +4.108 |

`A + B − D = 0.000e+00` — an arithmetic receipt on the reduction, not a finding.

### 0.4 The interval, the MDE, and the registration defect

All computed at the **realised** `se(A) = 0.1569` on `n = 3` v `3`, and expressed as a fraction of
the **same batch's own** `D = 0.5807` (the only denominator for which A and D share a batch, a
cell, a seed set and a metric).

| quantity | derivation | value |
|---|---|---|
| 95% CI, normal approximation | `−0.0093 ± 1.95996 × 0.1569` | **[−0.317, +0.298]** |
| the same, as a share of D | `÷ 0.5807` | **[−55%, +51%] of D** |
| 95% CI, Welch *t*, `df = 3.566` | `−0.0093 ± 2.9151 × 0.1569` | [−0.467, +0.448] = **[−80%, +77%] of D** |
| 95% CI for `se(A)` itself, χ² on 3.566 df | `0.1569 × sqrt(df/χ²)` | **[0.092, 0.496]** |
| MDE, 80% power, two-sided α = 0.05, normal | `(1.95996 + 0.84162) × 0.1569` | **0.440 pp = 76% of D** |
| the same, Welch *t* at `df = 3.566` | `(2.9151 + 0.9414) × 0.1569` | 0.607 pp = **105% of D** |
| power to detect an alignment effect equal to all of D | `1 − Φ(1.96 − 0.5807/0.1569)` | 0.96 |
| power to detect **half** of D | `1 − Φ(1.96 − 0.2904/0.1569)` | **0.46** |
| pre-registered NULL band half-width | `bin/c77_permuted_partition.sh:71` | **0.15** |
| P(a genuinely zero effect scores NULL) | `Φ(0.15/0.1569) − Φ(−0.15/0.1569)` | **0.661** |
| P(a genuinely zero effect is **mis-scored** UNDECIDED or worse) | `1 − 0.661` | **0.339** |
| share `A/D`, with the CI carried through | `−0.0093/0.5807`, `[−0.317,+0.298]/0.5807` | −1.6%, CI **[−55%, +51%]** |

**Rounding note, so the integrator is not surprised.** `docs/STATUS.md` (R0 checklist item 3) and
`docs/CORRECTIONS.md` 125 print the interval as **[−0.317, +0.299]**. That is the same interval
computed from the 3-dp-rounded inputs `A = −0.009`, `se = 0.157`
(`−0.009 ± 1.95996 × 0.157 = [−0.3167, +0.2987]`). At full precision the upper limit is
**+0.2982**. The replacement text below prints **+0.298**; the 0.001 pp difference is
rounding order and nothing else. Either is defensible; printing the full-precision one is
cheaper than explaining the discrepancy to a referee who recomputes it.

**Denominator robustness.** Against the twelve-cell fixed-effect pool `D = +0.546` instead of
`pp1`'s own `+0.581`, the same interval is [−58%, +55%] of D. The conclusion does not depend on
the choice, and the in-batch denominator is the conservative one.

### 0.5 The registration defect, stated exactly

The band was registered five-way and symmetric in `bin/c77_permuted_partition.sh:65–79`, before
the data existed:

```
A >  +0.30      -> ALIGNMENT HURTS
(+0.15, +0.30]  -> UNDECIDED
[-0.15, +0.15]  -> NULL
[-0.30, -0.15)  -> UNDECIDED
A <= -0.30      -> ALIGNMENT HELPS
```

The defect is arithmetic, not procedural: **the NULL band's half-width, 0.15, is narrower than
the standard error the batch actually achieved, 0.157.** A design whose resolution is coarser than
its own decision band cannot separate the hypotheses the band names. Concretely, had the true
alignment effect been exactly zero, this batch would have scored it `NULL` only **66% of the
time**; the other **34%** it would have landed in an UNDECIDED wing or beyond. A `NULL` verdict
from this instrument is therefore weak evidence of a small effect, not strong evidence of a zero
one — and the sign of the defect matters: the band was set from `mm1`'s *effect-size* scale
(deliberately, so the two legs read on one axis) rather than from a power calculation at the
achieved `n`. No power calculation appears anywhere in the registration.

### 0.6 The permutation seed is the run seed — confounded by construction

`bin/c77_permuted_partition.sh:447`, verbatim:

```
  # permnode<S> uses the RUN SEED as its permutation seed, so seeds 0-2 are three
  # different permutations as well as three different inits (stated in the header).
```

and the script's own header block at `:115–119` and the scorer's "WHAT THIS SCORER WILL NOT DO"
block at `analysis/c77_pp1_score.py:112–114` both declare it. The consequence: the three `perm`
runs differ from each other in **two** ways at once, so `sem(perm) = 0.0895` is a compound of
draw-to-draw variance and seed-to-seed variance and **the batch cannot separate them.** The
direction is conservative — folding a second source into the sem can only widen `se(A)`, never
narrow it — but it also means the paper cannot say how much of the interval is permutation
variance, which is the quantity a reader wants when the claim is "membership does not matter".

### 0.7 The manipulation was not inert — an honest complication that must be printed

A reader's first objection to a null is that the knob was never turned. It was. From the scorer's
`P5` table (descriptive, no registered direction; sems are over the 3 seeds):

| arm | `N_eff/m` | `dev_bias` |
|---|---|---|
| `nodewise` | 0.0547 ± 0.0010 | 0.02334 |
| `permnode<S>` | 0.0414 ± 0.0003 | 0.02176 |
| `chunk777` | 0.0358 ± 0.0012 | 0.00355 |

Permuting membership moves `N_eff/m` by **−0.0133 ± 0.0010, t −12.7** — 70% of the whole
`nodewise → chunk777` move — while moving accuracy by −0.009 ± 0.157. On the other field channel
it moves 8% of the way. So the two channels disagree about what the permutation "is like", and
neither licenses an accuracy claim: §5.2 already established that `N_eff/m` is **not** a sufficient
statistic for accuracy (anti-concordant at `t −11.14`), so its motion here is evidence that the
instrument fired and nothing more. That is exactly why it belongs in the section: it forecloses
"the permutation did nothing" as an explanation of `A ≈ 0` without being smuggled in as support
for the null.

### 0.8 Scope facts that hold `A` to one point in the design

* `A` is measured in **one batch, one cell, one η, one base optimiser, one network, one dataset,
  one budget.** `D` is measured in 17 within-batch count-matched cells across four network
  variants, two datasets and four base optimisers. The two headlines are not on the same
  evidential footing and the document currently presents them as though they were.
* `permnode` permutes **within each tensor.** It asks whether an output channel is special among
  the same-sized subsets *of its own layer*. It does **not** test whether layer boundaries matter.
  The scorer refuses to report a confirmed `P2` as "architecture is irrelevant" for this reason
  (`c77_pp1_score.py:105–108`, selftested).
* `nodewise` is read at η = 1e-4, which is `mm1`'s inherited η and **not** `nodewise`'s own argmax
  (3e-4). Every verdict in the batch is a statement at η = 1e-4.

---

## 1. Exact replacement text

Nine edits. Each gives the anchor, the current text verbatim, and the replacement. Line numbers
are from `paper/DRAFT-v2.md` at `06d6539` and are advisory only — match on the quoted text.

---

### R-1 · Abstract lead-in strapline (≈ line 18–19)

**REPLACE**

> admissible) on ResNet-10/18/34/50 and CIFAR-10/100, and report one robust measurement, one clean
> refutation, and a mechanism we could not find.

**WITH**

> admissible) on ResNet-10/18/34/50 and CIFAR-10/100, and report one robust measurement, one
> bounded null, and a mechanism we could not find.

---

### R-2 · Abstract, "The refutation." paragraph (≈ lines 33–36)

**REPLACE the whole paragraph**

> **The refutation.** Architecture *alignment* is not the carrier. Permuting **which** weights share
> a group while holding the group count **and the exact per-tensor group-size multiset** fixed is
> worth **−0.009 ± 0.157 pp (t −0.06)**, against a pre-registered symmetric band. What is left is the
> group-**size distribution**; alignment as such does nothing.

**WITH**

> **The bounded null.** Architecture *alignment* is not a large carrier, and we can put a number on
> how large it could still be. Permuting **which** weights share a group while holding the group
> count **and the exact per-tensor group-size multiset** fixed is worth **−0.009 ± 0.157 pp
> (t −0.06, 3 v 3, one batch)**, scored `NULL` against a symmetric band registered in advance. The
> 95% interval is **[−0.317, +0.298] pp = [−55%, +51%] of the same batch's D**, and the effect this
> design could have detected at 80% power is **0.440 pp = 76% of D**. So an alignment effect
> accounting for most of D is excluded; one accounting for half of it is **not** — power against
> `A = D/2` is 0.46. We also record a defect in our own registration: the NULL band's half-width
> (0.15) is **narrower than the standard error the batch achieved** (0.157), so a genuinely zero
> effect would have scored `NULL` only 66% of the time. What is left as the leading carrier is the
> group-**size distribution**, which takes **+0.590 ± 0.107 (t 5.53)** of the same decomposition.

---

### R-3 · §1.1 Contributions, item 2 (≈ lines 108–109)

**REPLACE**

> 2. **A pre-registered permutation null** showing architecture alignment is not the carrier:
>    −0.009 ± 0.157 pp at fixed count *and* fixed per-tensor size multiset (§4.6).

**WITH**

> 2. **A pre-registered permutation null, reported with its resolution**: at fixed count *and* fixed
>    per-tensor size multiset, membership is worth −0.009 ± 0.157 pp, 95% CI [−0.317, +0.298] =
>    [−55%, +51%] of D, MDE 0.440 pp. This **bounds** alignment's contribution rather than
>    eliminating it, in one batch at one design point, and we report the registration defect that
>    limits it (§4.6).

---

### R-4 · §2.5 table, the Adam-mini row, right-hand cell (≈ line 232)

**REPLACE the cell text**

> Its stated principle is Hessian sub-block **alignment** — which our permutation null (§4.6) refutes
> as the carrier in this regime.

**WITH**

> Its stated principle is Hessian sub-block **alignment**. Our permutation null (§4.6) bounds what
> that principle can be buying in this regime — at fixed count and fixed per-tensor size multiset,
> membership is worth −0.009 ± 0.157 pp, 95% CI [−0.317, +0.298] — which excludes a large
> alignment effect within one layer at one design point and does not exclude a moderate one.

---

### R-5 · §4.6 — heading and entire section (≈ lines 486–510)

**REPLACE the heading**

> ### 4.6 Alignment is not the carrier

**WITH**

> ### 4.6 Alignment: a bounded null, and what it does not settle

**REPLACE the section body** (from "`permnode` holds nodewise's group **count**…" through
"…which widens the interval rather than narrowing it.") **WITH the following, in full:**

---

`permnode` holds nodewise's group **count** and its **exact per-tensor size multiset** and
randomises only *which* weights share a group, within each tensor. Both properties are measured
from the allocated `beta` on the built network by the submission script's own guard, not inherited
from a comment. The contrast was registered five-way with a symmetric band before the runs
existed. The scorer's `P2`, run unedited, verbatim:

```
permnode<S> (m=14420, nodewise's EXACT size multiset, membership randomised)  92.003 +-0.090 (n=3)
nodewise    (m=14420, output channels)                                        92.012 +-0.129 (n=3)
A = permnode - nodewise = -0.009 pp   (se 0.157, t -0.06)
registered: A > +0.30 HURTS | (+0.15,+0.30] UND | [-0.15,+0.15] NULL | [-0.30,-0.15) UND | A <= -0.30 HELPS
-> **NULL**
```

In the same batch `D = +0.581 ± 0.141 (t 4.11)` and `B = chunk777 − permnode = +0.590 ± 0.107
(t 5.53)`, and `A + B − D = 0` exactly — a receipt on the reduction, not a finding.

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
   rather than at its own argmax of 3e-4. `D` is measured in seventeen count-matched within-batch
   cells across four network variants, two datasets and four base optimisers. The two results are
   not on the same evidential footing and we do not present them as though they were.

**What would settle it, and it is running.** A single batch closes all three of the statistical
gaps above: **`R1` — `permnode` at three permutation draws × six seeds with the permutation seed
decoupled from the run seed, plus a six-seed `nodewise` arm; 24 jobs, ≈24 GPU-hours.** No patch is
needed — `permnode<S>` already accepts an explicit `S`; `c77` simply passed the run seed. That
design (i) takes `se(A)` from 0.157 to ≈0.09, which brings the MDE to ≈0.25 pp, below half of D and
inside the pre-registered band for the first time; (ii) yields a **two-way variance decomposition**
that separates permutation variance from seed variance, so limit 2 above becomes a measured number
instead of a caveat; and (iii) supplies the replication `A` has never had. Until it reports, the
sentence this paper is entitled to is the bounded one above and not a stronger one. **If `R1`
returns an interval that still spans half of D, the alignment leg should be reported as
underdetermined rather than as a null**, and we register that in advance here.

---

### R-6 · §5 opening, "The two nulls" paragraph (≈ lines 592–596)

**REPLACE**

> **The two nulls**: architecture alignment (§4.6, §5.10) and out-of-sample predictability of D
> (§5.8).

**WITH**

> **The two nulls**: architecture alignment (§4.6, §5.10) — a *bounded* null, `A = −0.009 ± 0.157`,
> 95% CI [−55%, +51%] of D, from one batch at one design point — and out-of-sample predictability
> of D (§5.8).

*(Leave the remainder of the paragraph, from "§5.9 adds the failure of the classical remedy", as
it stands.)*

---

### R-7 · §5.10 — heading and body (≈ lines 811–815)

**REPLACE the heading**

> ### 5.10 Null: alignment (repeated here because it is a deliverable)

**WITH**

> ### 5.10 Bounded null: alignment (repeated here because it is a deliverable)

**REPLACE the body**

> §4.6. A = −0.009 ± 0.157, t −0.06, against a band registered in advance. A clean negative is worth
> as much as the positive and it is what redirected this programme from architecture alignment to
> group-size homogeneity.

**WITH**

> §4.6. `A = −0.009 ± 0.157, t −0.06`, scored `NULL` against a band registered in advance, with a
> 95% interval of [−0.317, +0.298] pp = [−55%, +51%] of D and an MDE of 0.440 pp = 76% of D. It
> excludes alignment as the principal carrier and leaves a moderate contribution open, from one
> batch at one design point, with permutation variance confounded with seed variance and with a
> registration defect we print (band half-width 0.15 < realised se 0.157). Read at that strength it
> is still what redirected this programme from architecture alignment to group-size homogeneity,
> and it is still worth as much as the positive — a negative reported with its resolution is a
> deliverable; a negative reported without one is a claim we cannot support. `R1` (24 jobs, in
> flight) is designed to halve the interval and to decompose the two variance sources.

---

### R-8 · §7, threat T2 (≈ lines 910–912)

**REPLACE**

> **T2 — The mechanism is missing, and one candidate is not identifiable from this design.** §5.7. We
> know the carrier is the size distribution rather than alignment; we cannot say which property of it,
> and this corpus provably cannot tell us.

**WITH**

> **T2 — The mechanism is missing, one candidate is not identifiable from this design, and the
> alignment null is underpowered.** §5.7 and §4.6. The size distribution is the surviving carrier
> and takes +0.590 ± 0.107 of the decomposition, but we cannot say which property of it and this
> corpus provably cannot tell us. Separately, the leg that redirected us there is measured once, at
> `n = 3` v `3`, with an interval spanning [−55%, +51%] of D and with permutation variance
> confounded with seed variance: **a moderate alignment contribution is not excluded**, and the
> batch that would exclude it (`R1`, 24 jobs) is running rather than reported.

---

### R-9 · §9 Conclusion — two sentences (≈ lines 1022–1024 and 1038–1039)

**R-9a. REPLACE** — note this sentence shares a paragraph with the heterogeneity `Q` clause, which
another package is editing. Replace **only** from "Architecture **alignment**" to the end of the
"What is left" sentence, leaving the `Q 43.2 / 11 df` clause exactly as the heterogeneity package
leaves it.

> Architecture **alignment** is not the carrier:
> holding the count *and* the per-tensor size multiset and permuting only membership is worth
> −0.009 ± 0.157 pp. What is left is the group-size distribution.

**WITH**

> Architecture **alignment** is bounded out as the principal carrier, in one batch at one design
> point: holding the count *and* the per-tensor size multiset and permuting only membership is
> worth −0.009 ± 0.157 pp, 95% CI [−0.317, +0.298] = [−55%, +51%] of D, against an MDE of 0.440 pp.
> A moderate alignment contribution is not excluded and a further batch is running to bound it more
> tightly. The surviving carrier is the group-size distribution, which takes +0.590 ± 0.107
> (t 5.53) of the same three-arm decomposition.

**R-9b. REPLACE**

> The honest description of this paper is therefore: **a robust, replicated, count-matched
> measurement, a clean refutation of the mechanism most people would guess, a prescription that costs
> nothing and works under three of four base optimisers, and no mechanism.**

**WITH**

> The honest description of this paper is therefore: **a robust, replicated, count-matched
> measurement; a single-batch bounded null that excludes the mechanism most people would guess as
> the principal carrier without excluding it as a contributor; a prescription that costs nothing and
> works under three of four base optimisers; and no mechanism.**

---

## 2. Numbers changed, with the derivation

Nothing in this package changes a measured value. Every change is a claim strength, a
newly-printed uncertainty, or a rounding correction.

| # | number | before | after | derivation |
|---|---|---|---|---|
| 1 | `A` | −0.009 ± 0.157 | **unchanged** | `92.0027 − 92.0120`; `se = sqrt(0.0895² + 0.1289²)`. Re-derived from raw `.out`: −0.00933, se 0.15690, t −0.0595 |
| 2 | 95% CI on `A` | **not printed** | **[−0.317, +0.298]** | `−0.00933 ± 1.95996 × 0.15690`. The record's +0.299 is the same interval from 3-dp-rounded inputs; see §0.4 |
| 3 | CI as a share of D | **not printed** | **[−55%, +51%]** | `[−0.3169, +0.2982] ÷ 0.5807`. Against the 12-cell pool `D = 0.546` it is [−58%, +55%] |
| 4 | MDE | **not printed** | **0.440 pp = 76% of D** | 80% power, two-sided α = 0.05, normal: `(1.95996 + 0.84162) × 0.15690 = 0.4396`; `÷ 0.5807 = 75.7%` |
| 5 | registration defect | **not printed** | **band half-width 0.15 < se 0.157** | `bin/c77_permuted_partition.sh:71` vs §0.3. P(NULL \| A = 0) = `Φ(0.9560) − Φ(−0.9560) = 0.661` |
| 6 | permutation seed | in §4.6 as a trailing caveat | **promoted into the result, with the file:line** | `bin/c77_permuted_partition.sh:447` |
| 7 | share of D | "alignment −1.6%" as a bare figure | **−1.6%, 95% CI [−55%, +51%]** | ratio interval from row 3 |
| 8 | `D` in `pp1` | +0.581 ± 0.141 | **unchanged** | `92.5927 − 92.0120`, `se = sqrt(0.0581² + 0.1289²) = 0.1414`, t 4.108 |
| 9 | `B` in `pp1` | +0.590 ± 0.107 | **unchanged**, promoted to the abstract | `92.5927 − 92.0027`, `se = sqrt(0.0581² + 0.0895²) = 0.1067`, t 5.529 |
| 10 | claim strength | "refutes" / "does nothing" / "worth nothing" | **"bounds" / "excludes a large effect" / "does not exclude a moderate one"** | the content of rows 2–5 |
| 11 | `N_eff/m` move under permutation | **not printed** | **−0.0133 ± 0.0010, t −12.7 (70% of the node→chunk move)** | scorer `P5` table, `perm − node`, `se = sqrt(0.0003² + 0.0010²)`. Descriptive; §5.2 governs its interpretation |

---

## 3. Standing-rule compliance

* **STANDING RULE 16.** `analysis/c77_pp1_score.py` was run **unedited**
  (`--root <runs>/pp1`, `--selftest` 139/139 PASS) and its `P2` block is quoted verbatim in R-5.
  The scorer's own free-text *reading* line ("Randomising membership … changes nothing") is
  **not** adopted into the paper's voice: a `NULL` verdict at `se = 0.157` does not license it, and
  the calibration paragraph immediately after the quote says so explicitly. The quoted verdict and
  the paper's claim are kept visibly distinct rather than the verdict being softened in place.
* **STANDING RULE 20.** The batch's science was read off the runs' own `ARGS` line, not the script
  header. All nine `pp1` runs carry single-occurrence `--alg-base SGDm`, `--alg-meta Lion`,
  `--stepsize-groups`, `--meta-stepsize 1e-4`, `--alpha0 1e-3`, `--num-epochs 100`, `--seed`;
  `pp1` is **not** among the batches flagged by `docs/ARGS-AUDIT.md`, and the audit's duplicate-flag
  sweep found repeated flags in exactly two batches, `ml2` and `sm3`, neither of which appears here.
* **plateau5** is primary throughout; the `plateau` column is not used.
* **Within-batch.** `A`, `B` and `D` are all differences between arms of the same batch, so any
  batch offset cancels identically in each.
* Every number was re-derived at write time from `runs/pp1-*.out` and the `pp1` probe directories;
  none was copied from the briefing, from `docs/STATUS.md`, or from `DRAFT-v2.md`.

---

## 4. Left open for the integrator, and for R1

1. **§9 paragraph collision.** R-9a sits in the same paragraph as the `Q 43.2 / 11 df` heterogeneity
   clause, which the heterogeneity package rewrites. Apply R-9a to the alignment sentences only.
2. **Cell count.** This package deliberately quotes "seventeen count-matched within-batch cells"
   to match `DRAFT-v2` as it stands. If the `sm3` ingest package raises that to eighteen, the
   figure appears once in R-5 limit 3 and once in R-8's neighbourhood and must be updated with the
   rest of the document. No number in this package's own arithmetic depends on it.
3. **§6.3 dependency avoided.** This package makes no use of the batch-variance numbers in §6.3,
   which is under concurrent rewrite (the `F(62,85) = 5.47` claim is withdrawn there). `A` is
   within-batch, so no cross-batch floor enters it.
4. **`R1` is registered here in advance** (end of R-5): if the decoupled batch returns an interval
   still spanning half of D, the leg is to be reported as **underdetermined**, not as a null. That
   sentence should survive into the `R1` scorer's own registration when it is written — and per
   **STANDING RULE 21** that scorer must exist and be committed before `R1` is submitted.
5. **Not attempted here.** A between-layer permutation (`permlayer`) that would test whether *layer*
   boundaries matter. Limit 1 in R-5 states the gap; no run in the corpus closes it, and `R1` does
   not close it either.
