# REWRITE PACKAGE — `heterogeneity`

**Closes:** R0 checklist item 2 (gate blocking #2 / Q01). **Touches, and must be applied together
with:** R0 item 1 (`gn1`-GN removal), item 4 ("byte-identical" deletion + a β-box column).

**Scope of this file.** Finished replacement text for §4.4 and for every other place in
`paper/DRAFT-v2.md` that quotes a heterogeneity number, keyed to the heading and line it replaces,
plus the re-derivation behind every figure. **Nothing in `DRAFT-v2.md` was edited by this package** —
other packages are editing that file concurrently. An integrator can apply §§3–4 below verbatim.

---

## 0. Executive summary for the integrator

| | |
|---|---|
| **What §4.4 said** | D is heterogeneous *"for reasons we cannot attribute"* (Q 43.2/11, τ 0.215) |
| **What §4.4 now says** | D is heterogeneous, and **one identified moderator — the base optimiser — carries 88% of it**. Inside a fixed base the effect is **homogeneous** (Q 4.22 on 7 df, p 0.75, τ = 0.000, pool +0.555 ± 0.045) across 7 batches, 2 meta-stepsizes, 2 budgets, 3 β-boxes and 2 clusters |
| **The honest weakness, stated in the section itself** | after the `gn1`-GN removal, **three of the four base levels rest on a single batch each**, and two of those three (SGD, RMSProp) are two arms of *one* submission (`nl1`). The moderator is identified, not replicated. **R3 is exactly this experiment** |
| **Free strengthening available now** | `sm3` is an independent second AdamW batch. Once its 12 rows are ingested, AdamW becomes the second replicated level and the between-base share rises 88% → 92% |
| **Verdict change** | none. Every claim in the old §4.4 survives; it is joined by a stronger one and loses an over-claim |

---

## 1. Provenance and conventions

### 1.1 STANDING RULE 20 audit of every cell this section uses

Every cell in the pool was checked against **the runs' own `ARGS` line**, not against a script
header. The base-optimiser axis — the moderator this whole section rests on — reads:

```
nl1-sgd-ch-s0   ARGS: --optimizer HF --alg-base SGD    --weight-decay-base 0.1 --alg-meta Lion ...
nl1-rms-ch-s0   ARGS: --optimizer HF --alg-base RMSProp --normalizer-param-base 0.999 --weight-decay-base 0.1 --alg-meta Lion ...
aw1-ch-s0       ARGS: --optimizer HF --alg-base AdamW  --normalizer-param-base 0.999 --momentum-param-base 0.9  --weight-decay-base 0.1 --alg-meta Lion ...
cc1-ch-s3       ARGS: --optimizer HF --alg-base SGDm   --momentum-param-base 0.99 --weight-decay-base 0.1 --alg-meta Lion ...
```

`--alg-base` occurs **once** in every run of every cell used here (this reproduces the
`docs/ARGS-AUDIT.md` sweep: the partition, budget and step-size axes are single-occurrence corpus-wide).
Across all 11 cells `alpha0 = 1e-3`, `gamma = 1`, `batch-size = 100`, `AUGMENT = 1`, `HIER = none`
and `--weight-decay-base 0.1` are **constant**. The only things that vary are the base optimiser,
η ∈ {1e-4, 3e-4}, the budget ∈ {100, 300}, the β-box and the cluster — and the last four are shown
below to be null.

### 1.2 The arithmetic convention, and why `43.01` and `43.2` are both right

DerSimonian–Laird on the **printed three-decimal (D, se) pairs of Table 2** gives Q = **43.01**.
The same computation on **full-precision arm means straight from `results/all_runs.csv`** gives
Q = **43.19**. The 0.4% gap is *rounding of the published table*, nothing else; it is not a
discrepancy between analyses, and A.4's "reproduces exactly" is describing this.

> **Convention adopted here, and it should be stated in §3 or in A.4: every meta-analytic quantity
> in §4.4 is computed from the three-decimal (D, se) pairs as printed in Table 2, so that a referee
> holding only the paper reproduces every digit.** Full-precision values are given in the ledger
> below wherever they differ in the second decimal.

This alone removes gate item 125.1's sub-complaint *"Q re-derives to 43.01 and 36.29, not the
abstract's 43.2 / 36.4"*.

### 1.3 Verification performed for this package

* All **17** Table-2 D values re-derived from `results/all_runs.csv` (`plateau5`, Welch on the two
  arm means). **17 of 17 reproduce to the printed three decimals.** The count-matched uniform arm
  is the `-ch` arm in every batch (for `r50` that is `chunk295`, not `chunk884`; `chunk884` gives
  +1.202 ± 0.336 and is **not** the published cell).
* `sm3` is not in the local mirror or in the CSV. Its 12 `.out` files were read directly on the
  cluster (`/data1/salehkaleybars/metaopt/runs/sm3-awrms-*.out`, jobs 4842532–4842543, all
  100/100 epochs) and `plateau5` recomputed as the mean of the last five `Test Accuracy:` lines.
  Its `ARGS` line is quoted in §4.2 below.

---

## 2. Re-derivation ledger

### 2.1 The pool, before and after the `gn1`-GN removal

| pool | k | fixed-effect pool | Q / df | p | τ (DL) | rms se | I² |
|---|---|---|---|---|---|---|---|
| Table 2 as published (12 cells) | 12 | +0.545 ± 0.036 | **43.01 / 11** | 1.1e-5 | 0.214 | 0.151 | 74% |
| **After removing `gn1`-GN (11 cells)** | 11 | +0.570 ± 0.037 | **36.29 / 10** | 7.5e-5 | **0.203** | 0.152 | 72% |
| SGDm + BatchNorm subset | 8 | **+0.555 ± 0.045** | **4.22 / 7** | **0.754** | **0.000** | 0.146 | **0%** |

τ / rms-se ratio: 1.42× (12 cells) → **1.34×** (11 cells). One-sided 95% Q-profile upper limit on τ
inside the SGDm+BatchNorm subset: **0.109 pp** — below the single-cell measurement se (0.146 pp) and
below the corpus nondeterminism bound recovered from `ml2`'s same-seed pairs (mean |Δ`plateau5`|
0.163 pp, `docs/ARGS-AUDIT.md`; that figure is quoted, not re-derived here).

### 2.2 The decomposition

| grouping | total Q | within | between | share | p(between) |
|---|---|---|---|---|---|
| **11 cells, base optimiser (4 levels)** | **36.29 / 10** | **4.22 / 7** | **32.07 / 3** | **88%** | **5.1e-7** |
| 12 cells, base (4 levels), GroupNorm folded into SGDm | 43.01 / 11 | 10.23 / 8 | 32.78 / 3 | 76% | 3.6e-7 |
| 12 cells, base + normalisation (5 levels) | 43.01 / 11 | 4.22 / 7 | 38.78 / 4 | 90% | 7.7e-8 |
| 12 cells (11 + `sm3`), base (4 levels) | 69.92 / 11 | 5.85 / 8 | 64.07 / 3 | **92%** | 7.9e-14 |

> **`docs/STATUS.md` item 2 and CORRECTIONS 125.1 carry a denominator error.** They pair the
> **11-cell** numerator (32.1) with the **12-cell** denominator (43.01) and report "≈ 75%".
> 32.074 / 43.005 = 74.6%, which is where the figure came from, but the two pools are not the same
> analysis. **Once `gn1`-GN is removed there is only one consistent number: 32.07 / 36.29 = 88%.**
> The related "base + normalisation ≈ 89%" is 90.2% and is only defined if `gn1`-GN is *kept*.

### 2.3 Subgroup pools and their contrasts

| level | k (cells) | batches | base state (`ARGS`) | pool D | vs SGDm pool | z |
|---|---|---|---|---|---|---|
| SGD | 1 | 1 (`nl1`) | no momentum, no normaliser | +1.035 ± 0.109 | +0.480 ± 0.118 | +4.07 |
| RMSProp | 1 | 1 (`nl1`, same submission) | normaliser 0.999, **no momentum** | +0.973 ± 0.251 | +0.418 ± 0.255 | +1.64 |
| **SGDm** | **8** | **7** | momentum 0.99, no normaliser | **+0.555 ± 0.045** | — | — |
| AdamW | 1 | 1 (`aw1`) | momentum 0.9 + normaliser 0.999 | +0.279 ± 0.087 | −0.276 ± 0.098 | −2.82 |
| *AdamW with `sm3` ingested* | *2* | *2* | *as above* | *+0.189 ± 0.052* | *−0.366 ± 0.068* | *−5.36* |
| (`gn1`-GN, removed from the pool) | — | — | SGDm base, GroupNorm net | +0.202 ± 0.137 | −0.353 ± 0.144 | −2.46 |

### 2.4 Inside the homogeneous subset: what else could have been the moderator, and is not

| competing moderator | levels | between Q / df | p |
|---|---|---|---|
| β-box (−15:−2.3026 / −25:−2.3026 / −30:9.0) | 3 | 0.77 / 2 | 0.68 |
| meta-stepsize (1e-4 / 3e-4) | 2 | 0.68 / 1 | 0.41 |
| budget (100 / 300 epochs) | 2 | 3.00 / 1 | 0.083 |
| cluster account (alice / alice2) | 2 | 0.77 / 1 | 0.38 |

Leave-one-cell-out over the 8: pool ranges +0.544 … +0.602, Q 1.22 … 4.18 on 6 df, **τ = 0.000 in
all eight subsets**. Substituting the box-clean 5 v 5 `hz3` value (+0.455 ± 0.096, dropping the
seed-5 trio whose own `ENV` line reads `BETA_CLIP=−15:−2.3026`) moves the subset to
pool +0.569 ± 0.046, Q 3.04 / 7, and the between-base share to 91%.

### 2.5 Four exact replications of one design point

`cc1`, `mm1`, `pp1` and `gn1`-BN are four independent submissions of the **identical**
configuration (ResNet-18 / CIFAR-10 / SGDm + Lion / η 1e-4 / 100 epochs / α₀ 1e-3 / β-box
−15:−2.3026):

```
cc1 +0.727 +-0.200 | mm1 +0.485 +-0.161 | pp1 +0.581 +-0.141 | gn1-BN +0.587 +-0.153
pool +0.582 +-0.080,  Q = 0.89 on 3 df,  p = 0.83,  tau = 0.000
(adding rl3@1e-4 +0.681 +-0.173, same config in a different box: pool +0.600 +-0.073, Q 1.16/4, p 0.89)
```

### 2.6 `sm3` — an independent second AdamW batch, re-derived here

`ARGS` line, verbatim, from `sm3-awrms-ch-s0-4842533.out` (last-wins on the repeated `--alg-meta`,
so the meta-optimiser is **Lion**, not RMSProp — the batch is void as designed and salvageable only
as an `aw1` replicate):

```
--optimizer HF --alg-base AdamW --normalizer-param-base 0.999 --momentum-param-base 0.9
--weight-decay-base 0.1 --alg-meta RMSProp --normalizer-param-meta 0.999 --weight-decay-meta 0
--alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0
--dataset CIFAR10 --NN-name ResNet18 --batch-size 100 --gamma 1 --meta-stepsize 1e-4
--alpha0 1e-3 --num-epochs 100 --stepsize-groups chunk777 --seed 0
ENV: AUGMENT=1 BETA_CLIP=-15:-2.3026 HIER=none ...
```

Same β-box, same α₀, same η, same budget as `aw1`.

```
plateau5, chunk777 : 93.334  93.126  93.272   mean 93.2440
plateau5, nodewise : 93.120  93.070  93.118   mean 93.1027
D(sm3) = +0.141  se 0.064  t 2.22   (3 v 3, Welch)
D(aw1) = +0.279  se 0.087  t 3.19   (3 v 3, Welch)
replicate spread  aw1 - sm3 = +0.137 +- 0.108,  z +1.27  (consistent)
inverse-variance pool of the two cells : +0.189 +- 0.052
pooled 6 v 6 Welch on the six runs     : +0.210 +- 0.056, t 3.76
```

---

## 3. REPLACEMENT TEXT — `paper/DRAFT-v2.md` §4.4

**Replaces:** the whole of `### 4.4 D is genuinely heterogeneous` (DRAFT-v2 lines 451–462, from the
heading through *"…which is exactly the premise the prediction question in §5.8 needed."*).

**Precondition:** apply R0 item 1 first, so that Table 2 has 16 rows and the pool has 11 cells.
This text assumes `gn1`-GN is gone and that Table 2 has gained a β-box column (R0 item 4).

---

### 4.4 The heterogeneity is one identified moderator: the base optimiser

Restrict Table 2 to the eleven cells that run the same ResNet-18 partition contrast
(`nodewise` → `chunk777`) so that the contrast itself is held fixed. Those eleven are
heterogeneous: the fixed-effect pool is +0.570 ± 0.037 with

> **Q = 36.29 on 10 df, p = 7.5e-5**; DerSimonian–Laird **τ = 0.203 pp** against an rms measurement
> se of **0.152 pp**, i.e. I² = 72%.

That much the record already carried. What it did not carry is that **almost all of it is one
variable.** Split the eleven cells by the base optimiser, the axis §5.5 was already looking at:

| base optimiser | base state, from the runs' own `ARGS` line | cells | batches | pooled D (pp) |
|---|---|---|---|---|
| SGD | no momentum, no second moment | 1 | 1 | **+1.035 ± 0.109** |
| RMSProp | second moment 0.999, no momentum | 1 | 1 | **+0.973 ± 0.251** |
| SGDm | momentum 0.99, no second moment | 8 | 7 | **+0.555 ± 0.045** |
| AdamW | momentum 0.9 + second moment 0.999 | 1 | 1 | **+0.279 ± 0.087** |

**Between base optimisers, Q = 32.07 on 3 df (p = 5.1e-7) — 88% of the total.** The remaining 12%
is the within-SGDm residual, and it is not resolvable at all:

> Over the eight SGDm + BatchNorm cells — **seven separate submissions, two meta-stepsizes
> (1e-4, 3e-4), two budgets (100 and 300 epochs), three β-boxes and two clusters** — the pool is
> **+0.555 ± 0.045** with **Q = 4.22 on 7 df, p = 0.75, I² = 0%, τ = 0.000** (one-sided 95%
> Q-profile upper limit **0.109 pp**, below the 0.146 pp rms measurement se of the cells themselves).

Four of those eight are independent submissions of the *identical* configuration and land at
+0.727, +0.485, +0.581 and +0.587 — Q = 0.89 on 3 df, p = 0.83. Leave-one-cell-out over the eight
never resolves heterogeneity (Q 1.22–4.18 on 6 df; τ = 0.000 in all eight subsets), and no other
axis available inside the subset competes with the base: β-box Q = 0.77/2 (p 0.68), meta-stepsize
Q = 0.68/1 (p 0.41), budget Q = 3.00/1 (p 0.083), cluster account Q = 0.77/1 (p 0.38). In
particular the fact that the eleven cells span three β-boxes — which is why we no longer call the
contrast "byte-identical" (§3.3) — is **not** what makes them heterogeneous.

So the finding is not "D varies for reasons we cannot attribute". It is:

> **At a fixed base optimiser, D is a constant.** Under SGDm it is +0.555 ± 0.045 pp and it does
> not move with the meta-stepsize, the budget, the β-box, the cluster or the batch. **Between base
> optimisers it moves by a factor of 3.7**, and that single axis accounts for 88% of the observed
> heterogeneity.

**What we may not conclude from the direction.** The four levels happen to arrange themselves as a
2 × 2 in the base optimiser's own state: the two levels whose base carries **no momentum term**
(SGD, RMSProp) sit at ≈ +1.0, and the two that carry one (SGDm, AdamW) sit at ≈ +0.28…+0.56. As
contrasts, a momentum main effect of **−0.587 ± 0.145 (z −4.04)** against a second-moment main
effect of **−0.169 ± 0.145 (z −1.16)**, with an interaction of −0.214 ± 0.291 that the design
cannot resolve. This is consistent with §5.5, which kills second-moment normalisation as the axis
on the independent RMSProp-vs-AdamW contrast. **We register it as a prediction, not a result**, for
four reasons, and a referee should hold us to all four:

1. **Three of the four levels rest on one batch each.** Only SGDm is replicated (7 batches).
2. **SGD and RMSProp are not independent of each other:** they are the two halves of a single
   submission, `nl1` (job ids 4832408–4832431, one node pool). D is a within-batch contrast, so a
   batch-level offset cancels inside each half — but a batch × partition interaction peculiar to
   `nl1` would move both levels together, and nothing in this corpus would see it.
3. **The momentum coefficients are not matched** (0.99 under SGDm, 0.9 under AdamW), so "momentum
   present/absent" is a two-point contrast in a continuous parameter.
4. **Momentum alone is not sufficient.** Collapsing the four levels to momentum-present /
   momentum-absent leaves a residual Q of 12.19 on 8 df inside the momentum-present group — the
   SGDm-to-AdamW gap survives the collapse. The identified moderator is *the base optimiser*, not
   any single component of it.

**R3 is exactly the experiment this weakness names**: a second, independent batch at the SGD and
RMSProp bases (`nodewise` + `chunk777`, three seeds, 12 runs), which would replicate the moderator
at three of four levels and break the `nl1` co-dependence. Until it lands, "the base optimiser is a
moderator of D" is a within-corpus decomposition of eleven measurements, **not an out-of-sample
prediction rule** — which is why it does not contradict §5.8, where the predictors under test are
continuous properties of a configuration and the unit is the design point.

The one cell we removed from this pool is the GroupNorm arm of `gn1` (+0.202 ± 0.137): its own
registered scorer refuses to issue a verdict at a 1.37× budget ratio, so under our own rule (§3.4)
it may not be scored, and it is not reported here as a normalisation-scheme result. For the record,
keeping it as a fifth level would raise the explained share to 90% and lower the pooled D to
+0.545 ± 0.036 — i.e. the decomposition does not depend on the exclusion; only our right to quote
the cell does.

---

*(Optional insert, to be added only once `sm3`'s 12 rows are in `results/all_runs.csv` — see §5.3
below. Place it as the final paragraph of §4.4.)*

> **A second AdamW batch.** `sm3` (12 runs) was submitted as an AdamW × RMSProp-meta cell and is
> void as designed — its own `ARGS` line carries `--alg-meta RMSProp … --alg-meta Lion` and
> argparse takes the last, so it ran Lion (§8.2). What it *is* is an independent replicate of
> `aw1` at the same β-box, α₀, η and budget: D = **+0.141 ± 0.064** against `aw1`'s +0.279 ± 0.087,
> a replicate spread of +0.137 ± 0.108 (z 1.27). Pooling them gives AdamW = **+0.189 ± 0.052** over
> two batches, and the between-base share of the heterogeneity rises from 88% to **92%**
> (Q 64.07 on 3 df). AdamW is then the second base level to be replicated, leaving SGD and RMSProp
> as the only single-batch levels — which is precisely what R3 addresses.

---

## 4. KNOCK-ON REPLACEMENTS

### 4.1 Abstract (DRAFT-v2 lines 29–31)

**Delete:**

> Over the twelve cells sharing a byte-identical contrast the fixed-effect pool is +0.546
> with **Q = 43.2 on 11 df, p = 1.0e-5** — D varies genuinely across configurations
> (τ = 0.215 pp against 0.151 pp rms measurement error), not just noisily.

**Insert:**

> Over the eleven cells sharing the same ResNet-18 partition contrast, D varies genuinely across
> configurations (Q = 36.3 on 10 df, p = 7.5e-5) — and **88% of that variation is one identified
> moderator, the base optimiser** (between-base Q = 32.1 on 3 df). At a fixed base the effect is
> homogeneous: over eight SGDm cells spanning seven batches, two meta-stepsizes and two budgets,
> D = **+0.555 ± 0.045 pp** with Q = 4.22 on 7 df (p = 0.75, τ = 0.000).

*Note for the integrator:* the two sentences immediately above this in the abstract also need R0
item 1 applied — "four network variants" becomes three, and "seventeen cells" becomes sixteen.
Separately, `ml2`'s se in the abstract's range must move 0.142 → **0.195** (`ml2` is 3 independent
seeds run twice, not 6 seeds; `docs/ARGS-AUDIT.md`), so the range reads
"+0.456 ± 0.195 to +0.727 ± 0.200 across six independent batches". Those two edits belong to other
packages; they do not change any number in §4.4, because `ml2` is not in the pool. For the record,
adding `ml2` as a twelfth cell at the corrected se gives Q = 36.62 on 11 df, τ = 0.196,
pool +0.566 ± 0.036 — and inside the SGDm subset Q = 4.47 on 8 df, p = 0.81, τ still 0.000.

### 4.2 §5.8, the boxed draft sentence (DRAFT-v2 ~line 790)

**Delete:**

> *D is real, replicated across 17 count-matched within-batch cells, and varies genuinely across
> configurations (τ = 0.215 pp against 0.151 pp measurement noise). No measurable property of a
> configuration predicts D out of sample better than the corpus mean by a margin this design can
> resolve.*

**Insert:**

> *D is real, replicated across 16 count-matched within-batch cells. Its variation across
> configurations is not unattributed: 88% of it is the base optimiser (§4.4), and within a fixed
> base D is homogeneous (τ = 0.000, 95% upper limit 0.109 pp). What remains unpredictable is the
> **continuous** part — no measurable scalar property of a configuration predicts D out of sample
> better than the corpus mean by a margin this design, at 10 design points, can resolve.*

*Why this is the right repair, not a softening:* §5.8's failure is a **prediction** failure at the
design-point level over continuous covariates (level, headroom, m, singleton fraction). §4.4's
success is a **decomposition** over a categorical factor with three singleton levels. Both are
true; the old wording made them look contradictory, and gate item 125.1 #2 caught exactly that
("refuted by our own §5.5 three pages later").

### 4.3 §9 Conclusion (DRAFT-v2 lines 1021–1022)

**Delete:** `…and it is genuinely heterogeneous (Q 43.2 / 11 df, τ 0.215 pp against 0.151 pp noise).`

**Insert:** `…and its variation across configurations is dominated by one identified moderator —
the base optimiser carries 88% of the between-cell heterogeneity (Q 32.1 / 3 df), and inside a
fixed base the effect is homogeneous (Q 4.22 / 7 df, p 0.75, τ 0.000).`

Also delete the phrase *"for reasons we cannot attribute"* wherever it survives (it appears in §4.4
and in the §9/abstract framing; the string does not survive the §4.4 replacement above).

### 4.4 Appendix A.4 (DRAFT-v2 lines 1086–1090)

**Replace the whole entry with:**

> **A.4 — Heterogeneity τ, and the two Q's.** The record carried τ = 0.285 pp against 0.137 pp
> measurement noise. DerSimonian–Laird on the published cells with Welch standard errors gives
> **τ = 0.214 pp** against an rms se of **0.151 pp** on the 12-cell pool as first published, and
> **τ = 0.203 pp** against **0.152 pp** on the 11-cell pool after `gn1`-GN is removed (§4.4). The
> ratio is 1.3–1.4×, not 2×. Two Q values are in circulation and **both are correct**: computed
> from the three-decimal (D, se) pairs *as printed in Table 2*, Q = **43.01** on 11 df (36.29 on 10
> dropping GroupNorm); computed from full-precision arm means in `results/all_runs.csv`,
> Q = **43.19** (36.41). The gap is rounding of the printed table. **This paper reports the printed-table
> values throughout, so that every meta-analytic figure in §4.4 is reproducible from Table 2 alone.**
> The conclusion is unchanged and is now stronger: the excess over measurement error is real, and
> §4.4 attributes 88% of it.

### 4.5 §5.5 (DRAFT-v2 lines 691–696) — add one sentence, change nothing else

**Append to the end of §5.5:**

> This is the same conclusion §4.4 reaches from the other side: in the four-level base
> decomposition the second-moment main effect is −0.169 ± 0.145 (z −1.16) while the momentum main
> effect is −0.587 ± 0.145 (z −4.04). Neither of those contrasts is a result — three of the four
> levels are single batches — but they agree on which component of the base optimiser is *not* the
> axis.

### 4.6 Table 2 caption

Add, after the existing caption text:

> Cells 1–4 and 6–11 (SGDm and the three alternative bases, all ResNet-18/CIFAR-10) form the pool
> used for the heterogeneity decomposition in §4.4. The β-box column matters there: the pool spans
> three boxes, and box is shown in §4.4 not to be a moderator.

### 4.7 Figure F1 (R0 item 10) — spec, since this section is what it plots

Forest plot, one row per Table-2 cell, **grouped by base optimiser**, rows sorted within group by
se. Draw: (i) a diamond per base level at its subgroup pool; (ii) a vertical line at the SGDm pool
+0.555; (iii) the excluded `gn1`-GN and `ar1` cells as open markers below a rule, labelled
"excluded, shown for completeness". Annotate the panel with `Q_between = 32.07/3 (88%)` and
`Q_within(SGDm) = 4.22/7, p 0.75`. This is the single figure that carries §4.4; nothing else in the
section needs one.

---

## 5. Ledger of every number changed, with the re-derivation

| where | old | new | why |
|---|---|---|---|
| §4.4, abstract, §9 | Q 43.2 / 11 df | **36.29 / 10 df** | `gn1`-GN removed (R0 item 1). 43.2 → 43.01 is separately the printed-table convention (§1.2) |
| §4.4, abstract, §9, §5.8 | τ 0.215 pp | **0.203 pp** (11-cell) | recomputed after the removal; 0.214 on the 12-cell pool at the printed-table convention |
| §4.4, abstract | rms se 0.151 pp | **0.152 pp** | same |
| §4.4, abstract | pool +0.546 | **+0.570 ± 0.037** (11-cell grand pool) — but **quote +0.555 ± 0.045 (SGDm) instead** | a fixed-effect pool across four base optimisers is the wrong estimand once the base is shown to be the moderator. The grand pool is retained only as the heterogeneity anchor |
| §4.4 | "for reasons we cannot attribute" | deleted | 88% is attributed |
| §4.4 | "twelve cells … byte-identical" | "eleven cells … the same ResNet-18 partition contrast" | R0 items 1 and 4 |
| `docs/STATUS.md` item 2 / CORRECTIONS 125.1 | "between-base Q 32.1/3 ≈ **75%** of the total" | **88%** | denominator error: 32.07 is the 11-cell numerator, 43.01 the 12-cell denominator. With `gn1`-GN kept and folded into SGDm the correct figure is 76%; with it kept as its own level, base+normalisation is 90% (STATUS says 89%) |
| `docs/STATUS.md` item 2 | "k=8, **6 batches**" | **7 batches** | `cc1`, `mm1`, `pp1`, `gn1`, `rl3`, `fa1`, `hz3`. (`rl3` supplies two cells at two meta-stepsizes; `hz3` and `fa1` are each more than one physical submission, so 7 is a lower bound on submissions) |
| §5.8 boxed sentence | "17 count-matched cells" | **16** | R0 item 1 |
| §5.8 body (~line 759) | "collapse to **11 distinct design points**" | **10** | R0 item 1 removes `gn1`-GN, which was its own design point |
| §5.8 body + §5.8 boxed sentence + CORRECTIONS 124.1's power bound | "at 11 design points a predictor needs **\|r\| ≥ 0.602**" | **\|r\| ≥ 0.632** | at n = 10 the two-sided 5% critical correlation is t₈,.₀₂₅ / √(t² + 8) = 2.306 / 3.649 = 0.632. (Their 0.602 re-derives exactly at n = 11: 2.262 / 3.757.) The "≈ 25 design points to see \|r\| = 0.4" statement is unaffected |
| A.4 | "Q reproduces exactly (43.2 vs 43.0)" | explicit two-convention statement | closes gate 125.1 #2's sub-complaint |
| Abstract range | `ml2` +0.456 ± **0.142** | ± **0.195** | `ml2` is 3 seeds run twice (`docs/ARGS-AUDIT.md`). Not a §4.4 number — `ml2` is outside the pool — but it appears in the same abstract sentence |
| Table 2 row 15 (`r50`) | +0.881 ± 0.261 | **unchanged, confirmed** | the count-matched arm is `chunk295` (the `-ch` arm). Flagged because `chunk884` also exists in that batch and gives +1.202 ± 0.336; any scorer that picks the arm by group count rather than by the `-ch` name will report the wrong cell |

**Numbers that did NOT change and were re-verified:** all 17 Table-2 D values and their ses
(17/17 reproduce to three decimals from `results/all_runs.csv`); Q 4.22 / 7 df, p 0.754, τ 0.000,
pool +0.555 ± 0.045 for the SGDm+BatchNorm subset; between-base Q 32.07 / 3 df; the per-level
deviations from the SGDm pool (SGD +0.480, z 4.07; AdamW −0.276, z −2.82; GroupNorm −0.353,
z −2.46; RMSProp +0.418, z 1.64 — CORRECTIONS 125.1's z's reproduce to ±0.02).

### 5.1 Reproduction snippet (self-contained; no repo import, so it cannot drift)

```python
import math
D = {'cc1':(0.727,0.200),'mm1':(0.485,0.161),'pp1':(0.581,0.141),'gn1-BN':(0.587,0.153),
     'rl3@1e-4':(0.681,0.173),'rl3@3e-4':(0.591,0.096),'fa1':(0.629,0.123),'hz3':(0.428,0.086),
     'aw1':(0.279,0.087),'nl1-SGD':(1.035,0.109),'nl1-RMS':(0.973,0.251)}      # 11 cells, gn1-GN removed
def dl(names):
    y=[D[n][0] for n in names]; s=[D[n][1] for n in names]
    w=[1/x**2 for x in s]; W=sum(w); mu=sum(a*b for a,b in zip(w,y))/W
    Q=sum(a*(b-mu)**2 for a,b in zip(w,y)); df=len(names)-1
    C=W-sum(a*a for a in w)/W
    return mu, W**-0.5, Q, df, max(0.,(Q-df)/C)**0.5
S8=['cc1','mm1','pp1','gn1-BN','rl3@1e-4','rl3@3e-4','fa1','hz3']
print(dl(list(D)))   # (+0.5696, 0.0370, 36.294, 10, tau 0.2026)
print(dl(S8))        # (+0.5552, 0.0447,  4.220,  7, tau 0.0000)
print(dl(list(D))[2]-dl(S8)[2])   # between-base Q = 32.074 on 3 df -> 88% of 36.294
```

### 5.2 Cell-level input table, for Appendix B / the reproduction target

| cell | batch | base | η | epochs | β-box | cluster | n | D | se |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `cc1` | SGDm | 1e-4 | 100 | −15:−2.3026 | alice | 3 v 3 | +0.727 | 0.200 |
| 2 | `mm1` | SGDm | 1e-4 | 100 | −15:−2.3026 | alice | 3 v 3 | +0.485 | 0.161 |
| 3 | `pp1` | SGDm | 1e-4 | 100 | −15:−2.3026 | alice | 3 v 3 | +0.581 | 0.141 |
| 4 | `gn1` | SGDm | 1e-4 | 100 | −15:−2.3026 | alice2 | 4 v 4 | +0.587 | 0.153 |
| 5 | `rl3` | SGDm | 1e-4 | 100 | −30:9.0 | alice2 | 3 v 3 | +0.681 | 0.173 |
| 6 | `rl3` | SGDm | 3e-4 | 100 | −30:9.0 | alice2 | 3 v 3 | +0.591 | 0.096 |
| 7 | `fa1` | SGDm | 3e-4 | 100 | −25:−2.3026 | alice | 6 v 6 | +0.629 | 0.123 |
| 8 | `hz3` | SGDm | 1e-4 | **300** | −30:9.0 (one seed-5 run at −15:−2.3026) | alice | 6 v 6 | +0.428 | 0.086 |
| 9 | `aw1` | **AdamW** | 1e-4 | 100 | −15:−2.3026 | alice2 | 3 v 3 | +0.279 | 0.087 |
| 10 | `nl1` | **SGD** | 1e-4 | 100 | −15:−2.3026 | alice | 3 v 3 | +1.035 | 0.109 |
| 11 | `nl1` | **RMSProp** | 1e-4 | 100 | −15:−2.3026 | alice | 3 v 3 | +0.973 | 0.251 |
| — | `sm3` | *AdamW (pending ingest)* | 1e-4 | 100 | −15:−2.3026 | alice | 3 v 3 | *+0.141* | *0.064* |
| — | `gn1`-GN | *SGDm/GroupNorm — **excluded**, scorer refuses a verdict* | 1e-4 | 100 | −15:−2.3026 | alice2 | 8 v 8 | *+0.202* | *0.137* |

Rows 10 and 11 are **the same submission** (`nl1`, job ids 4832408–4832431), split only by the
`base` column. This must be visible in the table, because it is the reason the SGD and RMSProp
levels are not independent of each other.

### 5.3 Dependencies on other in-flight packages

| depends on | what changes here if it lands |
|---|---|
| **R0 item 1** (`gn1`-GN removal) — **hard precondition** | §3's text is written for the 11-cell pool. If the removal is *not* applied, use the "12 cells, base + normalisation (5 levels)" row of §2.2 instead: total 43.01/11, between 38.78/4, share 90%, and say "base optimiser and normalisation scheme" throughout |
| **R0 item 4** ("byte-identical" deletion, β-box column) | §3 already avoids "byte-identical" and quotes the box null (Q 0.77/2). The β-box column of §5.2 is ready to paste |
| **`sm3` ingest** (housekeeping item 1) | apply the optional insert at the end of §3; update the abstract share 88% → 92% only if the insert is applied. **Do not hand-edit the `meta` column** — `aggregate.py`'s parser is last-wins and writes `Lion` by itself |
| **`ml2` se correction** (0.142 → 0.195) | no §4.4 number moves (`ml2` is outside the pool). Only the abstract's quoted range |
| **R2** (`hz3` seed-5 re-run in box −30:9.0) | if it lands, `hz3` becomes +0.455 ± 0.096 at 5 v 5 or a clean 6 v 6; the SGDm subset goes to pool +0.569 ± 0.046, Q 3.04/7, and the between-base share to 91%. The verdict does not move |
| **R3** (2nd SGD and RMSProp batch) | the "registered as a prediction, not a result" paragraph of §3 is written to be *replaced* by R3's outcome. If R3 replicates, the four reasons collapse to two (unmatched momentum coefficients; momentum-only insufficiency) |

---

## 6. What this package deliberately did not do

* **It did not edit `DRAFT-v2.md`.** Concurrent packages are editing the same file.
* **It did not remove `gn1`-BN.** R0 item 1 removes only the **GroupNorm** arm; the BatchNorm arm
  of `gn1` is an ordinary D cell whose scorer has no complaint, and it is one of the four exact
  replications in §2.5. An integrator over-deleting the whole `gn1` batch would drop the SGDm
  subset from 8 cells to 7 (pool +0.552 ± 0.047, Q 4.17/6 — verdict unchanged, but the replication
  count in §2.5 falls from four to three).
* **It did not run a random-effects meta-regression** with base as a factor. With three singleton
  levels the subgroup decomposition *is* the saturated model; a regression would print coefficients
  and standard errors that look like inference and are not.
* **It did not claim a mechanism.** "The base optimiser moderates D" is where the evidence stops.
  The momentum reading in §3 is registered as a prediction for R3 and is labelled as such.
* **It ran no GPU jobs.** The only cluster access was reading twelve existing `sm3` `.out` files.
