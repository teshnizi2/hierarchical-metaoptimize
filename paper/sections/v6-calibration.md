# PACKAGE `calibration` — closes **B1** and **B2**

**Cycle 106. Zero GPU. No run, no batch, no scorer re-run — this is an arithmetic and
simulation package against the existing corpus.**

The meta-analytic layer of §4.4 is referred to the wrong null distribution and the paper never
says so. This package carries the correction. **It does not delete the decomposition, and the
decomposition does not need deleting**: the heterogeneity resolves against its own simulated null
at *p* = 0.013, and the base-optimiser structure is confirmed by an exact permutation that uses
**no standard errors at all** (η² = 0.840, rank 9 of 45,045, exact *p* = 0.00020). What moves is
the *size* of the *p*-values and the *width* of the intervals. No sign, no ordering, and nothing
in Table 2 moves at all.

Everything below was re-derived at write time from `results/all_runs.csv` through the paper's own
`c98_figures.welch()` and `c98_figures.meta()`. Nothing is quoted from a briefing, from
`docs/CORRECTIONS.md`, or from a previous package.

---

## 0. Contents

| § | what |
|---|---|
| 1 | What changes, in one table |
| 2 | The re-derivation: every number, with the command that produces it |
| 3 | Where my figures differ from the ones I was handed |
| 4 | New code: `analysis/c99_qcalibration.py` (**already created**) and the `c98_reproduce.py` patch |
| 5 | Replacement text — 23 edits in `paper.tex`, 23 in `DRAFT-v4.md`, every anchor verified `count == 1` |
| 6 | Verification actually run |
| 7 | Integrator notes, including a dirty working tree that will mislead a naive audit run |

---

## 1. What changes, in one table

| claim | as printed at HEAD | after this package | direction |
|---|---|---|---|
| total *Q* = 102.47 / 13 df | *p* = 5.5 × 10⁻¹⁶ | *p* = 5.5 × 10⁻¹⁶ (χ²) **and MC *p* = 0.013** | 14 orders weaker, **still resolved** |
| between-base *Q* = 95.12 / 3 df | *p* = 1.7 × 10⁻²⁰ | + **MC *p* = 0.005** | 17 orders weaker, **still resolved** |
| within-level *Q* = 7.36 / 10 df | *p* = 0.69 | + MC *p* = 0.86 | **more** homogeneous |
| SGDm *Q* = 4.21 / 7 df | *p* = 0.76 | + MC *p* = 0.86, null median 9.4 | **more** homogeneous |
| SGD / RMSProp / AdamW level *Q* | *p* 0.68 / 0.24 / 0.20 | + MC *p* 0.70 / 0.30 / 0.25 | all **more** homogeneous |
| τ = 0.295 pp, *I*² = 87 % | printed flat | printed **and labelled upper bounds**; recentred 0.271 pp and 74 % | smaller |
| abstract "+0.556 ± 0.045 pp" | implied 95 % CI ± 0.088 | ± 0.121 pp, calibrated; the nominal covers **73 %** | wider |
| §4.4's headline pool | "the **fixed-effect** pool is +0.530 ± 0.029" | random-effects **+0.611 ± 0.087**, 95 % CI [+0.441, +0.782], *primary*; FE kept and labelled | relabelled |
| Contribution 1's "+0.396 to +0.614" | unlabelled | "**fixed-effect** pools; +0.396 to +0.674 on random effects" | labelled; **sign untouched** |
| endpoint table's *p* column | χ² only | χ² **and MC**: 0.013 / 0.24 / 0.90 / 0.16 | **three of four rows change reading** |
| the moderator's evidence | weighted-*Q* share + rank-14 permutation | **weight-free η² = 0.840, rank 9 / 45,045, exact *p* = 0.00020** | new, and se-free |
| SGDm τ Q-profile upper limit 0.109 pp | χ²₇ | **0.097 pp** calibrated | **tighter** — the one case χ² errs in our disfavour |
| registered rule *Q* > 3.841 | nominal size 0.05 | **realised size 0.10**, size-0.05 value 6.22 | the levels' survival is stronger than claimed |
| §3.3's t-vs-Q inconsistency | unstated | **stated as ours**, in the Multiplicity paragraph | new |
| §7 | T1–T12 | **+ T13** | new |

**Two findings in this package were not in the brief and are the ones a referee will care about
most.**

1. **The endpoint disclosure gets *stronger*, not weaker.** Referred to their own simulated
   nulls, the 20-epoch column's *Q* = 29.37 (χ² *p* 0.0058) has MC *p* **0.24** and
   `final_test`'s *Q* = 39.91 (χ² *p* 1.4 × 10⁻⁴) has MC *p* **0.16**. On a calibrated reference
   **`plateau5` is the only one of the four endpoints with resolved heterogeneity at all.** §4.4
   already discloses that the decomposition is conditional on the endpoint; calibration sharpens
   that disclosure into "on three of the four there is nothing for any moderator to explain."
2. **One quantity moves against us.** §4.4's one-sided 95 % *Q*-profile upper limit on the SGDm τ
   is 0.109 pp against χ²₇ and **0.097 pp** when the profile is simulated at each trial τ. The χ²
   reference is *conservative* there. A correction that only ever helped its authors would not be
   one, so it is printed.

---

## 2. The re-derivation

Every number in §5's replacement text comes from one of two commands, both of which are in the
repository and both of which were run for this package:

```
python3 analysis/c99_qcalibration.py              # 26 s
python3 analysis/c99_qcalibration.py --endpoints  # 34 s
```

`analysis/c99_qcalibration.py` is **new and has been created** (§4). Its two constants are
registered at module level: `SEED = 20260902`, `DRAWS = 20000`. Changing either changes every
Monte-Carlo number below.

### 2.1 Why χ² is the wrong reference: the Welch df of the fourteen live cells

`meta()` weights by `w_i = se_i^-2`. Cochran's *Q* is χ²ₖ₋₁ only if those `se_i` are known.
They are Welch standard errors from two arms of 3–6 runs. Welch–Satterthwaite df, re-derived:

| cell | base | n | D | se | **Welch df** |
|---|---|---|---|---|---|
| cc1 | SGDm | 3 v 3 | +0.7267 | 0.2001 | 2.67 |
| mm1 | SGDm | 3 v 3 | +0.4853 | 0.1613 | 2.58 |
| pp1 | SGDm | 3 v 3 | +0.5807 | 0.1414 | 2.78 |
| gn1 (BN) | SGDm | 4 v 4 | +0.5870 | 0.1532 | 4.29 |
| rl3 @1e-4 | SGDm | 3 v 3 | +0.6813 | 0.1733 | 3.96 |
| rl3 @3e-4 | SGDm | 3 v 3 | +0.5913 | 0.0957 | **2.06** |
| fa1 | SGDm | 6 v 6 | +0.6293 | 0.1232 | 9.31 |
| hz3 | SGDm | 6 v 6 | +0.4277 | 0.0865 | **9.68** |
| aw1 | AdamW | 3 v 3 | +0.2787 | 0.0873 | 4.00 |
| nl1 (SGD) | SGD | 3 v 3 | +1.0353 | 0.1085 | 3.05 |
| nl1 (RMSProp) | RMSProp | 3 v 3 | +0.9733 | 0.2515 | 2.38 |
| bm2 (SGD) | SGD | 3 v 3 | +0.9780 | 0.0858 | 3.30 |
| bm2 (RMSProp) | RMSProp | 3 v 3 | +0.6313 | 0.1492 | **2.04** |
| sm3 | AdamW | 3 v 3 | +0.1413 | 0.0638 | 2.28 |

**min 2.04, median 2.91, mean 3.88, max 9.68.** Pooled within-arm sd **0.1856 pp on 70 df**.

The cell set is `c98_figures.POOL12` minus the withdrawn GroupNorm cell — the same fourteen §4.4
pools — and the module asserts that, that `sm4` is absent, and that the base shape is {8,2,2,2},
before it reports anything. It also asserts that its own `_welch` (a float rewrite of
`c98_figures.welch`, ~18× faster because `statistics.variance` uses exact Fraction arithmetic)
agrees with `welch()` to **1.4 × 10⁻¹⁴** on all fourteen observed cells *and* on 200 simulated
draws. The simulation therefore goes through the paper's own estimator.

### 2.2 The observed values, re-derived (all reproduce)

```
fixed-effect pool +0.5297 ± 0.0294   Q 102.4739 on 13 df   tau 0.2948   I2 87.3%
within-level Q 7.3587 on 10 df | between-base Q 95.1152 on 3 df | share 92.82%
   SGDm    k=8  Q 4.2060 / 7   chi2 p 0.7558
   SGD     k=2  Q 0.1718 / 1   chi2 p 0.6785
   RMSProp k=2  Q 1.3681 / 1   chi2 p 0.2421
   AdamW   k=2  Q 1.6128 / 1   chi2 p 0.2041
```

### 2.3 How the null is built

Under the null every cell shares one true D. For cell *i*, draw `n_c` and `n_n` normal values at
that cell's own two arm standard deviations and its own *n*; form `(D*, se*)` with the paper's
`welch()`; pool the fourteen with the paper's `meta()`; read `Q*`. 20,000 times, fixed seed.
The true D is set to 0 — *Q*, τ and the within/between split are invariant to a common shift, and
coverage is asked as `|m*| ≤ c·se*`, so nothing depends on it. (Verified empirically: the mean of
the pooled estimate under the null is −0.0004 against a truth of 0, i.e. the estimator is
unbiased; within a cell the sample mean and sample variance of a normal are independent, so the
estimated weights are independent of the values they weight.)

**Two nulls, printed as a bracket, because neither alone is honest:**

* **per-cell** — each cell's own two observed arm sds are the truth. Faithful to the observed
  heteroscedasticity, but each "truth" is itself a 2–5 df estimate, so this null inherits the
  instability it measures. It is the **larger-*p*** end. This is the one the paper quotes.
* **common-sd** — one pooled within-arm sd (0.1856 pp, 70 df) for every arm. Far better
  determined, but assumes homoscedasticity. It is the **smaller-*p*** end.

### 2.4 The calibrated reference distribution

| statistic | df | χ² mean / median / p95 | **simulated null mean / median / p95** |
|---|---|---|---|
| *Q* total | 13 | 13 / 12.34 / 22.36 | **26.92 / 21.41 / 62.36** (per-cell); 21.60 / 18.37 / 45.90 (common) |
| within-level *Q* | 10 | 10 / 9.34 / 18.31 | **16.92 / 13.89 / 38.23** (per-cell); 14.69 / 12.45 / 31.94 (common) |
| between-base *Q* | 3 | 3 / 2.37 / 7.81 | **10.01 / 5.63 / 31.72** (per-cell); 6.91 / 4.47 / 21.04 (common) |
| SGDm level *Q* | 7 | 7 / 6.35 / 14.07 | **12.25 / 9.40 / 30.71** (per-cell); 10.69 / 8.54 / 25.81 (common) |
| a 2-cell level *Q* | 1 | 1 / 0.455 / 3.841 | **1.56 / 0.52 / 6.22** (per-cell, pooled over the three) |

**The Monte-Carlo *p* for every *Q* the paper prints** (per-cell null; common-sd in brackets):

| where | *Q* | df | χ² *p* | **MC *p*** | verdict |
|---|---|---|---|---|---|
| abstract, §1, §4.4, Fig. 2b, endpoint table | 102.47 | 13 | 5.5 × 10⁻¹⁶ | **0.013** (0.002) | still resolved |
| §1, §4.4, Fig. 2b, endpoint table | 95.12 | 3 | 1.7 × 10⁻²⁰ | **0.005** (0.0007) | still resolved |
| §1, §4.4, Fig. 2b | 7.36 | 10 | 0.69 | **0.86** (0.82) | homogeneous, more so |
| abstract, §1, §4.4 table, §4.4 SGDm block, Fig. 2 | 4.21 | 7 | 0.76 | **0.86** (0.84) | homogeneous, more so |
| §4.4 table, Fig. 2 — SGD | 0.17 | 1 | 0.68 | **0.70** (0.70) | homogeneous |
| §4.4 table, Fig. 2 — RMSProp | 1.37 | 1 | 0.24 | **0.30** (0.27) | homogeneous |
| §4.4 table, Fig. 2 — AdamW | 1.61 | 1 | 0.20 | **0.25** (0.24) | homogeneous |
| endpoint table — `plateau` | 29.37 | 13 | 0.0058 | **0.24** (0.19) | **no longer resolved** |
| endpoint table — `best_test` | 9.87 | 13 | 0.70 | **0.90** (0.88) | null, more clearly |
| endpoint table — `final_test` | 39.91 | 13 | 1.4 × 10⁻⁴ | **0.16** (0.080) | **no longer resolved** |
| endpoint, between-base — `plateau` | 18.36 | 3 | 3.7 × 10⁻⁴ | **0.099** | not resolved |
| endpoint, between-base — `best_test` | 3.70 | 3 | 0.296 | **0.60** | null |
| endpoint, between-base — `final_test` | 34.66 | 3 | 1.4 × 10⁻⁷ | **0.025** | resolved |
| §4.4 share (92.8 %) as a statistic | — | — | — | **0.0013** (0.0001) | resolved |
| τ = 0.295 as a statistic | — | — | — | **0.0006** (0.0005) | resolved |

**Every correction on the layer runs in the same direction: heterogeneity is far less resolved
than χ² says, homogeneity is more so.**

*Monte-Carlo precision.* At 20,000 draws the standard error on a *p* near 0.013 is ±0.0008.
Across three independent seeds (11111, 20260902, 987654321) the headline *p* reads 0.0109, 0.0129,
0.0124; at 200,000 draws with the registered seed it is 0.0119, and the null moments are
26.856 / 21.491 / 62.377. The registered 20,000-draw figures are what the paper prints and what
the audit asserts, and §3.3's new paragraph states that range rather than implying more precision
than 20,000 draws buy.

### 2.5 τ and *I*² are upper bounds

Eq. (12) forms `tau^2 = max(0, (Q − (k−1)) / den)` and *I*² = (Q − (k−1))/Q. Both subtract 13
where the null mean is 26.9. With `den = 1029.2150` re-derived from the fourteen cells:

| centred on | value | **τ** | ***I*²** |
|---|---|---|---|
| χ² k−1 | 13 | 0.2948 pp | 87.3 % |
| per-cell null mean | 26.920 | **0.2709 pp** | **73.7 %** |
| common-sd null mean | 21.597 | 0.2803 pp | 78.9 % |

The package **keeps** 0.295 and 87 % — they are the standard estimator and are what a reader will
recompute — and labels them upper bounds with the recentred values beside them.

### 2.6 The intervals undercover — B2

| pool | *k* | reported | ±1.96 se | **realised coverage** | true sd of *m* | **calibrated 95 % half-width** |
|---|---|---|---|---|---|---|
| SGDm (the abstract's) | 8 | +0.556 ± 0.045 | ±0.0878 | **72.99 %** | 0.0612 | **0.1207 pp** (per-cell) / 0.1236 (common) |
| the fourteen, fixed-effect | 14 | +0.530 ± 0.029 | ±0.0576 | **65.18 %** | 0.0460 | **0.0893 pp** (per-cell) / 0.1042 (common) |
| `plateau` FE | 14 | +0.449 ± 0.024 | ±0.0466 | 72.0 % | — | 0.0683 pp |
| `best_test` FE | 14 | +0.396 ± 0.025 | ±0.0492 | 68.8 % | — | 0.0742 pp |
| `final_test` FE | 14 | +0.614 ± 0.043 | ±0.0835 | 74.4 % | — | 0.1224 pp |

The calibrated half-width is the 95th percentile of `|m* − μ|` in the same simulation, so it has
exact 95 % coverage by construction. The abstract takes **±0.121 pp**, the per-cell figure, for
consistency with every other Monte-Carlo number in the paper; the common-sd null would give
±0.124 pp, and 0.003 pp is not a difference either claim turns on.

**"homogeneous (*Q* 4.21 on 7 df)" — the claim holds and its stated basis does not.** 4.21 sits
at the **14th percentile** of its own null, whose median is **9.40** (per-cell) / 8.54 (common),
not χ²₇'s 6.35. So the eight SGDm cells are homogeneous by a *wider* margin than the abstract
claimed, against a reference the abstract had wrong. The abstract now states the right basis.

**The random-effects pools**, which §4.4 now leads with because τ > 0:

| endpoint | fixed-effect | τ | **random-effects** | RE 95 % CI |
|---|---|---|---|---|
| `plateau5` | +0.5297 ± 0.0294 | 0.2948 | **+0.6114 ± 0.0868** | [+0.441, +0.782] |
| `plateau` | +0.4493 ± 0.0238 | 0.1015 | +0.4798 ± 0.0379 | [+0.406, +0.554] |
| `best_test` | +0.3956 ± 0.0251 | 0.0000 | +0.3956 ± 0.0251 | [+0.346, +0.445] |
| `final_test` | +0.6144 ± 0.0426 | 0.2509 | +0.6736 ± 0.0966 | [+0.484, +0.863] |

So Contribution 1's range is **+0.396 to +0.614 pp on fixed effects and +0.396 to +0.674 on
random effects**. The interval labels change; **the sign claim does not**, and cannot, because
nothing in Table 2 is a pooled quantity.

### 2.7 The weight-free permutation — the load-bearing statistic from here on

η² = SSB / SST on the fourteen raw D's under the base-optimiser grouping. **No standard error
enters it anywhere.** All 45,045 partitions of shape {8, 2, 2, 2} (14!/(8!·2!·2!·2!·3!)) are
enumerated exactly — there is **no Monte-Carlo error in this *p***.

| endpoint | **η²** | rank | of | **exact *p*** | null median | null max |
|---|---|---|---|---|---|---|
| **`plateau5`** | **0.8396** | **9** | 45,045 | **0.000200** | 0.1996 | 0.8945 |
| `plateau` | 0.8004 | 13 | 45,045 | 0.000289 | 0.2021 | 0.8490 |
| `best_test` | 0.2762 | 15,248 | 45,045 | 0.338506 | 0.2010 | 0.8409 |
| `final_test` | 0.6700 | 341 | 45,045 | 0.007570 | 0.2073 | 0.8383 |

**Cross-check that this enumeration is the paper's own**: run on the *weighted* share of *Q* that
§4.4 already publishes, the same enumerator returns **rank 14, *p* = 0.00031** — exactly the
figures at `paper.tex:1570–1571`. The machinery is validated against a number already in print.

Note what the permutation does and does not say. Like the published rank-14 test it is
*conditional on the observed spread* of the fourteen D and asks only whether **this partition** is
special. Whether there is any spread to partition is the separate question *Q* answers, and
calibrated, *Q* answers it at *p* = 0.013. The two together are the argument; neither alone is.
This is why the *Q* calibration is printed rather than replaced by the permutation.

### 2.8 The one quantity χ² gets wrong in our disfavour

§4.4 prints "one-sided 95 % *Q*-profile upper limit **0.109 pp**" for the SGDm τ. That inverts
`Q_gen(τ²)` against χ²₇'s 5th percentile, **2.1673** — which reproduces 0.1090 exactly, so the
printed number is right *given* its reference. Simulating the reference **at each trial τ** (a
between-cell effect N(0, τ²) added to the cells' true D's, then the 5th percentile of the
simulated `Q_gen(τ²)`, bisected to the root) gives

> **calibrated one-sided 95 % upper limit = 0.0967 pp**, against the printed 0.109 pp.

Both are below the 0.1464 pp rms measurement se of the eight cells, so the conclusion is
unchanged and slightly stronger. This is the only calibrated quantity in the package that moves
in the authors' favour, and it is printed for that reason.

### 2.9 The registered `Q > 3.841` rule is mis-sized

`c97_bm2_score.py`'s registered line — quoted at `paper.tex:1567` — is
"*Q* > 3.841 ⇒ the level is not a stable quantity", the χ²₁ 5 % critical value. Simulated over
the three two-cell levels (60,000 draws):

> **P(*Q* > 3.841 | homogeneous level) = 0.1011**, not 0.05. The size-0.05 critical value is
> **6.219** (per-cell null); 0.0834 and 5.216 under the common-sd null.

The rule fires about twice as often as advertised. A level that does **not** fire it is therefore
*stronger* evidence of homogeneity than the rule claims. §4.4's "a test the label could have
failed — and did not" survives and is understated; the package says so in the same paragraph.

### 2.10 What the calibration does **not** touch

* **Every number in Table 2.** D, se and *t* are within-cell Welch quantities, already
  Welch-corrected for their own df by §3.3. None is pooled and none is a χ² reading.
* **The 20/20 sign result** on `plateau5`, `plateau` and `best_test`, and 19/20 on `final_test`.
* **Zero attrition** inside the twenty cells (170/170 admissible, every cell exactly n v n).
* **The alignment null** (`rp1`), the nine dead mechanisms, `bm2`'s replication verdicts, `sm4`'s
  refutation, the budget ladder, the prescription *T*, ρ, the count axis *U* — none of these is a
  weighted pool referred to χ². (`bm2`'s pooled *Q* 0.172 / 1 and 1.367 / 1 are quoted from a
  registered scorer under RULE 16 and are the SGD and RMSProp level *Q*'s, already calibrated
  above at MC *p* 0.70 and 0.30.)

---

## 3. Where my figures differ from the ones I was handed

I was given a set of target numbers. I reproduced them independently. Three differ, and I report
mine:

| quantity | handed to me | **re-derived here** | why |
|---|---|---|---|
| null *Q* mean / median / p95 | 26.86 / 21.38 / 62.67 | **26.92 / 21.41 / 62.36** at the registered 20,000 draws; **26.856 / 21.491 / 62.377** at 200,000 | Monte-Carlo noise. The handed figures match a ~200,000-draw run; the paper prints the registered 20,000-draw ones and states the seed range. |
| weight-free permutation *p* | 0.00023 | **0.000200 = 9 / 45,045** | This is an **exact enumeration**, not a sample. There is no Monte-Carlo error, so 0.00020 is the number. 0.00023 is not reachable by any rank (10/45,045 = 0.000222, 11/45,045 = 0.000244). η² = 0.8396 ≈ 0.840 confirmed. |
| between-base MC *p*, common-sd null | 0.0003 | **0.0007** (14 exceedances of 20,000); 0.0008 at 200,000 draws | Both are ≪ 0.05; the difference is seed noise and/or a different definition of the common-sd truth. Mine pools all 70 within-arm df. |

Everything else confirms: Welch df **2.04–9.68, median 2.91**; MC *p* 0.013 / 0.005; common-sd
0.002; SGDm coverage **72.99 %** with true sd **0.0612**; SGDm null *Q* median **9.40**, p5
**2.70**, p95 **31.26** (20,000 draws), 4.21 at the **14th percentile**; τ and *I*² recentred to
0.271 / 73.7 %.

---

## 4. New code

### 4.1 `analysis/c99_qcalibration.py` — **CREATED, in the working tree, uncommitted**

543 lines. Stdlib only (`random`, `math`, `statistics`, `itertools`) plus `c98_figures`; no scipy,
no numpy, so it adds no dependency to the audit. Registered constants `SEED = 20260902`,
`DRAWS = 20000` at module level. Public entry points, all used by the `c98_reproduce.py` section
below:

```
live_arms(adm, arm_fn=None)      the fourteen live cells with their arm values; asserts the
                                 cell set, the absence of sm4 and the {8,2,2,2} shape
welch_df(cell)                   Welch-Satterthwaite df of one cell's D
check_estimator_fidelity(cs)     asserts the fast estimator == c98_figures.welch to 1e-12
arm_sds / pooled_arm_sd          the two nulls' standard deviations
observed(cs)                     pool, se, Q, df, tau, per-level Q, within/between, share
qnull(cs, draws, seed, mode)     the simulated null: Q, W, B, share, tau, m, se, per-level Q
quant / mc_p / coverage / half_width
re_pool(items, tau)              the DerSimonian-Laird RANDOM-effects pool
q_gen / tau_upper(cs, ...)       the Q-profile limit, reference simulated at each trial tau
rule_size(cs, ...)               the realised size of the registered Q > 3.841 rule
eta2 / _shape_partitions / permutation_eta2 / permutation_share
```

`python3 analysis/c99_qcalibration.py` prints sections [1]–[7]; `--endpoints` adds [8].
`--draws` and `--seed` override the registered constants for sensitivity runs.

**RULE 21 note.** This is a *scorer for an existing corpus*, not for a batch; no batch is being
submitted, so RULE 21 is not engaged. It is committed before the prose that cites it, which is
the spirit of the rule.

### 4.2 `analysis/c98_reproduce.py` — one new section, **60 assertions, all PASS**

Two edits. Both anchors verified `count == 1` against the live file.

**(a) Insert the section.** Anchor — insert the block **immediately before** this line:

```
# ------------------------------------------------- the census, ASSERTED not measured
```

**(b) Register it in `SECTIONS`.** Replace (`count == 1`):

```
            ("metricsens", metricsens),
```

with

```
            ("metricsens", metricsens), ("calibration", calibration),
```

It must sit **before** `censuscheck`, which freezes `CENSUS_MARK`.

**Why the section prints `[15b]` and not `[16]`.** §3.4 names "section `[16]`" as the census
self-check. Renumbering `censuscheck` to `[17]` would silently falsify that sentence — and B7 is
separately rewriting it. `[15b]` leaves §3.4 alone.

**Runtime.** The section adds ~37 s to an audit that currently takes 1.4 s. That is the cost of
20,000-draw simulations at a registered seed; it is deterministic, and the alternative — caching
the numbers — is exactly the failure mode this repository exists to prevent.

The section body is below, verbatim.

```python
# ======================= NEW: the Q calibration (S3.3, S4.4, S7 T13, Fig. 2)
# S4.4 refers Cochran Q to chi2_{k-1}, but its weights w_i = se_i^-2 come from Welch
# standard errors estimated at 2.04-9.68 df (median 2.91), so chi2 is the wrong
# reference and every Q p-value on that layer is anticonservative.  c99_qcalibration
# simulates the paper's OWN estimator -- the same welch(), the same DerSimonian-Laird
# meta() -- under a homogeneous truth and gives the reference Q actually has.  The
# seed and draw count are REGISTERED in c99_qcalibration (SEED, DRAWS); changing
# either changes every number below, which is why they live there and not here.
# This section is numbered [15b] on purpose: S3.4 names "section [16]" as the census
# self-check, and renumbering censuscheck would silently falsify that sentence.
def calibration(rows, adm, args):
    print("\n[15b] Q CALIBRATION  (S3.3, S4.4, S7 T13, Fig. 2)")
    import c99_qcalibration as K
    cs = K.live_arms(adm)
    chk("cells in the calibrated pool", len(cs), 14, "S4.4, T13", "%.0f")
    print("   fast estimator agrees with welch() to %.1e  (seed %d, %d draws)"
          % (K.check_estimator_fidelity(cs, K.SEED), K.SEED, K.DRAWS))
    dfs = [K.welch_df(c) for c in cs]
    chk("min Welch df of the fourteen cells", min(dfs), 2.04, "S3.3, T13", "%.2f")
    chk("median Welch df -- why chi2 is the wrong reference", st.median(dfs), 2.91,
        "S3.3, S4.4, T13", "%.2f")
    chk("max Welch df", max(dfs), 9.68, "S3.3, T13", "%.2f")
    psd, pdf = K.pooled_arm_sd(cs)
    chk("pooled within-arm sd (the common-sd null)", psd, 0.186, "S3.3", "%.3f")
    chk("   its df", pdf, 70, "S3.3", "%.0f")

    obs = K.observed(cs)
    per = K.qnull(cs, K.DRAWS, K.SEED, "percell")
    com = K.qnull(cs, K.DRAWS, K.SEED, "common")
    chk("null Q on 13 df: mean", st.mean(per["Q"]), 26.9, "S7 T13", "%.1f")
    chk("   median", K.quant(per["Q"], .5), 21.4, "S7 T13", "%.1f")
    chk("   95th percentile", K.quant(per["Q"], .95), 62.4, "S7 T13", "%.1f")
    chk("MC p of Q = 102.47", K.mc_p(per["Q"], obs["Q"]), 0.013,
        "abstract, S1, S4.4, S7 T13, Fig. 2", "%.3f")
    chk("   ...under the common-sd null", K.mc_p(com["Q"], obs["Q"]), 0.002,
        "S4.4, S7 T13", "%.3f")
    chk("MC p of between-base Q = 95.12", K.mc_p(per["B"], obs["between"]), 0.005,
        "S1, S4.4, S7 T13, Fig. 2", "%.3f")
    chk("   ...under the common-sd null", K.mc_p(com["B"], obs["between"]), 0.0007,
        "S7 T13", "%.4f")
    chk("MC p of within-level Q = 7.36", K.mc_p(per["W"], obs["within"]), 0.86,
        "S1, S4.4, Fig. 2", "%.2f")
    for b, p in (("SGD", 0.70), ("RMSProp", 0.30), ("SGDm", 0.86), ("AdamW", 0.25)):
        chk("MC p of the %-8s level Q" % b, K.mc_p(per["LV"][b], obs["per"][b]), p,
            "S1.1 C3, S4.4 table, Fig. 2", "%.2f")
    chk("null median of the SGDm level Q (7 df)", K.quant(per["LV"]["SGDm"], .5), 9.4,
        "abstract, S1, S4.4", "%.1f")

    # tau and I^2 subtract k-1 = 13 where the null mean is 26.9: UPPER BOUNDS.
    w = [1.0 / se ** 2 for _, se in obs["items"]]
    W = sum(w); den = W - sum(x ** 2 for x in w) / W
    e = st.mean(per["Q"])
    chk("tau recentred on the null mean", math.sqrt(max(0.0, (obs["Q"] - e) / den)),
        0.271, "S4.4, S7 T13", "%.3f")
    chk("I^2 recentred on the null mean", 100 * max(0.0, (obs["Q"] - e) / obs["Q"]),
        73.7, "S4.4, S7 T13", "%.1f")

    # the intervals
    sg = [c for c in cs if c["base"] == "SGDm"]
    sper = K.qnull(sg, K.DRAWS, K.SEED, "percell")
    chk("coverage of the SGDm pool's +-1.96 se interval, %", 100 * K.coverage(sper, 1.96),
        73.0, "abstract, S4.4, S7 T13", "%.1f")
    chk("   its calibrated 95% half-width, pp", K.half_width(sper), 0.121,
        "abstract, S1, S4.4, S7 T13", "%.3f")
    chk("   the nominal half-width it replaces", 1.96 * K.observed(sg)["se"], 0.088,
        "S1, S7 T13", "%.3f")
    chk("coverage of the 14-cell fixed-effect interval, %", 100 * K.coverage(per, 1.96),
        65.2, "S4.4, S7 T13", "%.1f")
    chk("   its calibrated 95% half-width, pp", K.half_width(per), 0.089,
        "S4.4, S7 T13", "%.3f")
    m_re, se_re = K.re_pool(obs["items"], obs["tau"])
    chk("random-effects pool over the fourteen", m_re, 0.611, "S4.4")
    chk("   its se", se_re, 0.087, "S4.4", "%.3f")
    chk("   its 95% CI, low", m_re - 1.96 * se_re, 0.441, "S4.4")
    chk("   ...high", m_re + 1.96 * se_re, 0.782, "S4.4")

    # the one quantity chi2 gets CONSERVATIVELY wrong
    chk("calibrated Q-profile upper limit on the SGDm tau",
        K.tau_upper(sg, K.DRAWS, K.SEED), 0.097, "S4.4, S7 T13", "%.3f")
    # the registered 1-df decision rule
    sz, cv = K.rule_size(cs, K.DRAWS, K.SEED)
    chk("realised size of the registered Q > 3.841 rule", sz, 0.10, "S4.4, S7 T13", "%.2f")
    chk("   its size-0.05 critical value, not 3.841", cv, 6.22, "S7 T13", "%.2f")

    # THE LOAD-BEARING STATISTIC: no se enters it anywhere.
    e0, ge, tot, pp_, med, p95, mx = K.permutation_eta2(cs)
    chk("weight-free eta^2, base-optimiser grouping", e0, 0.840,
        "S1, S1.1 C3, S4.4, S7 T13, Fig. 2", "%.3f")
    chk("   partitions of shape {8,2,2,2}", tot, 45045, "S4.4", "%.0f")
    chk("   the base partition's rank among them", ge, 9, "S4.4, S7 T13", "%.0f")
    chk("   its EXACT permutation p", pp_, 0.00020,
        "S1, S4.4, S7 T13, Fig. 2", "%.5f")
    chk("   null eta^2 median", med, 0.200, "S4.4", "%.3f")
    s0, ge2, tot2, p2 = K.permutation_share(cs)
    chk("   the WEIGHTED share permutation the paper already prints", p2, 0.00031,
        "S4.4 -- cross-check that this enumeration is the paper's own", "%.5f")

    # the endpoint disclosure, calibrated.  plateau5 stays primary.
    END = {"plateau5":   (0.013, 0.005, 0.840, 0.00020, 0.611),
           "plateau":    (0.24,  0.099, 0.800, 0.00029, 0.480),
           "best_test":  (0.90,  0.60,  0.276, 0.33851, 0.396),
           "final_test": (0.16,  0.025, 0.670, 0.00757, 0.674)}
    for col in MS_METRICS:
        mcq, mcb, eta, pe, rem = END[col]
        ec = K.live_arms(adm, _arm_on(col)); o = K.observed(ec)
        s = K.qnull(ec, K.DRAWS, K.SEED, "percell")
        chk("MC p of Q, %-11s" % col, K.mc_p(s["Q"], o["Q"]), mcq,
            "S4.4 endpoint table, S7 T13", "%.3f" if col == "plateau5" else "%.2f")
        chk("   MC p of between-base Q, %-11s" % col, K.mc_p(s["B"], o["between"]), mcb,
            "S4.4 endpoint note, S7 T13", "%.3f")
        q_ = K.permutation_eta2(ec)
        chk("   weight-free eta^2, %-11s" % col, q_[0], eta, "S4.4 endpoint note", "%.3f")
        chk("      its exact p, %-11s" % col, q_[3], pe, "S4.4 endpoint note", "%.5f")
        chk("   random-effects pool, %-11s" % col,
            K.re_pool([K._welch(c["cv"], c["nv"]) for c in ec], o["tau"])[0], rem,
            "S4.4 endpoint note")
    chk("null mean of the best_test Q -- why 'below its own df' is the wrong test",
        st.mean(K.qnull(K.live_arms(adm, _arm_on("best_test")), K.DRAWS, K.SEED,
                        "percell")["Q"]), 25.3, "S4.4 reading 1", "%.1f")
```

---

## 5. Replacement text

**23 edits in `paper.tex`, 23 in `DRAFT-v4.md`.** Every OLD block below was checked against the
live files at HEAD `351d9a6` and occurs **exactly once** (`count == 1`) — the check is in §6.1.
Apply them by literal search-and-replace, in any order; none of them overlaps another.

Line numbers are where the OLD text starts at HEAD, for orientation only — **match on the text,
not the number**, because earlier edits shift later ones.

---

### R1 — the abstract — **B2**: the interval, and the basis for “homogeneous”

**`paper/paper.tex`** — OLD (line 73, `count == 1`):

```latex
Pooled over eight SGDm cells the effect size is $+0.556 \pm 0.045\pp$, homogeneous
($Q$ 4.21 on 7 df), while cells differing in base optimiser are strongly heterogeneous.
```

NEW:

```latex
Pooled over eight SGDm cells the effect is $+0.556 \pm 0.045\pp$ (95\% CI $\pm 0.121$ once
calibrated by simulation), homogeneous against that null ($Q$ 4.21, null median 9.4), while
cells differing in base optimiser are not.
```

**`paper/DRAFT-v4.md`** — OLD (line 19, `count == 1`):

```markdown
ResNet-50. Pooled over eight SGDm cells the effect size is +0.556 ± 0.045 pp, homogeneous
(Q 4.21 on 7 df), while cells differing in base optimiser are strongly heterogeneous.
```

NEW:

```markdown
ResNet-50. Pooled over eight SGDm cells the effect is +0.556 ± 0.045 pp (95% CI ± 0.121 once
calibrated by simulation), homogeneous against that null (Q 4.21, null median 9.4), while cells
differing in base optimiser are not.
```

---

### R2 — §1, the headline Q block — both p-values, plus the weight-free η²

**`paper/paper.tex`** — OLD (line 152, `count == 1`):

```latex
(\textbf{$Q = 102.47$ on 13 df, $p = 5.5 \times 10^{-16}$}, $\tau = 0.295$ pp against 0.143 pp
rms measurement error), and splitting those fourteen by base optimiser leaves them homogeneous
inside every level (within $Q = 7.36$ on 10 df, $p = 0.69$) while accounting for \textbf{92.8\%
of that $Q$} (between-base $Q = 95.12$ on 3 df).
```

NEW:

```latex
(\textbf{$Q = 102.47$ on 13 df}: $p = 5.5 \times 10^{-16}$ against $\chi^2_{13}$, which is the
\textbf{wrong reference} at these degrees of freedom, and \textbf{Monte-Carlo $p = 0.013$}
against the distribution $Q$ actually has here; $\tau = 0.295$ pp against 0.143 pp rms
measurement error, both of them upper bounds --- \S\ref{sec:threats} T13), and splitting those
fourteen by base optimiser leaves them homogeneous inside every level (within $Q = 7.36$ on
10 df, $p = 0.69$; Monte-Carlo $p = 0.86$) while accounting for \textbf{92.8\% of that $Q$}
(between-base $Q = 95.12$ on 3 df, $p = 1.7 \times 10^{-20}$ against $\chi^2_3$ and
\textbf{Monte-Carlo $p = 0.005$}). The weight-free statement of the same fact, which uses no
standard error at all and is what this claim now rests on: the base-optimiser grouping takes
$\eta^2 = 0.840$ of the unweighted variance of the fourteen $\Dstat$, ranking 9th of all
45{,}045 partitions of its shape (\textbf{exact $p = 0.00020$}).
```

**`paper/DRAFT-v4.md`** — OLD (line 84, `count == 1`):

```markdown
genuinely across configurations (**Q = 102.47 on 13 df, p = 5.5e-16**, τ = 0.295 pp against
0.143 pp rms measurement error), and splitting those fourteen by base optimiser leaves them
homogeneous inside every level (within Q = 7.36 on 10 df, p = 0.69) while accounting for **92.8%
of that Q** (between-base Q = 95.12 on 3 df).
```

NEW:

```markdown
genuinely across configurations (**Q = 102.47 on 13 df**: p = 5.5e-16 against χ²₁₃, which is the
**wrong reference** at these degrees of freedom, and **Monte-Carlo p = 0.013** against the
distribution Q actually has here; τ = 0.295 pp against 0.143 pp rms measurement error, both of
them upper bounds — §7 T13), and splitting those fourteen by base optimiser leaves them
homogeneous inside every level (within Q = 7.36 on 10 df, p = 0.69; Monte-Carlo p = 0.86) while
accounting for **92.8% of that Q** (between-base Q = 95.12 on 3 df, p = 1.7e-20 against χ²₃ and
**Monte-Carlo p = 0.005**). The weight-free statement of the same fact, which uses no standard
error at all and is what this claim now rests on: the base-optimiser grouping takes η² = 0.840 of
the unweighted variance of the fourteen D, ranking 9th of all 45,045 partitions of its shape
(**exact p = 0.00020**).
```

---

### R3 — §1, the SGDm block — both p-values and the calibrated interval

**`paper/paper.tex`** — OLD (line 161, `count == 1`):

```latex
$\Dstat = \mathbf{+0.556 \pm 0.045}$ pp with $Q = 4.21$ on 7 df ($p = 0.76$, $\tau = 0.000$). We
```

NEW:

```latex
$\Dstat = \mathbf{+0.556 \pm 0.045}$ pp with $Q = 4.21$ on 7 df ($p = 0.76$ against $\chi^2_7$;
Monte-Carlo $p = 0.86$ against a null whose median is 9.4, $\tau = 0.000$). The calibrated 95\%
interval on that pool is $\pm 0.121$ pp, not the $\pm 0.088$ its $\se$ implies
(\S\ref{sec:threats} T13). We
```

**`paper/DRAFT-v4.md`** — OLD (line 92, `count == 1`):

```markdown
budgets and three step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76,
τ = 0.000). We
```

NEW:

```markdown
budgets and three step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76
against χ²₇; Monte-Carlo p = 0.86 against a null whose median is 9.4, τ = 0.000). The calibrated
95% interval on that pool is ± 0.121 pp, not the ± 0.088 its se implies (§7 T13). We
```

---

### R4 — Contribution 1 — the four pools labelled **fixed-effect**; the sign claim untouched

**`paper/paper.tex`** — OLD (line 247, `count == 1`):

```latex
  $+0.396$ and $+0.614$ pp. The one exception is unresolved rather than reversed --- \arm{bm2}
```

NEW:

```latex
  $+0.396$ and $+0.614$ pp --- those four are \textbf{fixed-effect} pools, $+0.396$ to $+0.674$ pp
  on random effects, and \textbf{the sign claim does not depend on which}, nor on anything in
  \S\ref{sec:threats} T13, because no quantity in Table~\ref{tab:D} is a pooled quantity. The one
  exception is unresolved rather than reversed --- \arm{bm2}
```

**`paper/DRAFT-v4.md`** — OLD (line 163, `count == 1`):

```markdown
   pooled level stays between +0.396 and +0.614 pp. The one exception is unresolved rather than
```

NEW:

```markdown
   pooled level stays between +0.396 and +0.614 pp — those four are **fixed-effect** pools,
   +0.396 to +0.674 pp on random effects, and **the sign claim does not depend on which**, nor on
   anything in §7 T13, because no quantity in Table 2 is a pooled quantity. The one exception is
   unresolved rather than
```

---

### R5 — Contribution 3 — the share’s evidence moves to the weight-free permutation

**`paper/paper.tex`** — OLD (line 260, `count == 1`):

```latex
  coarsest partition that leaves them internally homogeneous (within $Q$ 7.36 on 10 df,
  $p$ 0.69) and it accounts for 92.8\% of the between-cell Cochran $Q$ (95.12 of 102.47 on
  3 df); inside the SGDm level $\Dstat$ is homogeneous
```

NEW:

```latex
  coarsest partition that leaves them internally homogeneous (within $Q$ 7.36 on 10 df,
  $p$ 0.69) and it accounts for 92.8\% of the between-cell Cochran $Q$ (95.12 of 102.47 on
  3 df) --- a share whose evidence now rests on a \textbf{weight-free exact permutation}
  ($\eta^2 = 0.840$, 9th of the 45{,}045 partitions of its shape, $p = 0.00020$) rather than on
  the $\chi^2$ $p$-values, which \S\ref{sec:threats} T13 shows are anticonservative by many
  orders of magnitude at these degrees of freedom; inside the SGDm level $\Dstat$ is homogeneous
```

**`paper/DRAFT-v4.md`** — OLD (line 175, `count == 1`):

```markdown
   partition that leaves them internally homogeneous (within Q 7.36 on 10 df, p 0.69) and it
   accounts for 92.8% of the between-cell Cochran Q (95.12 of 102.47 on 3 df); inside the SGDm
   level D is homogeneous
```

NEW:

```markdown
   partition that leaves them internally homogeneous (within Q 7.36 on 10 df, p 0.69) and it
   accounts for 92.8% of the between-cell Cochran Q (95.12 of 102.47 on 3 df) — a share whose
   evidence now rests on a **weight-free exact permutation** (η² = 0.840, 9th of the 45,045
   partitions of its shape, p = 0.00020) rather than on the χ² p-values, which §7 T13 shows are
   anticonservative by many orders of magnitude at these degrees of freedom; inside the SGDm
   level D is homogeneous
```

---

### R5b — Contribution 3 — the four levels’ calibrated p

**`paper/paper.tex`** — OLD (line 265, `count == 1`):

```latex
  submissions}, and each is internally homogeneous (within-level $Q$ 0.17/1, 1.37/1, 1.61/1 and
  4.21/7); a registered replication (\arm{bm2}) bought the two thinnest levels, and it is what
  makes the decomposition a testable restriction rather than an arithmetic identity.
```

NEW:

```latex
  submissions}, and each is internally homogeneous (within-level $Q$ 0.17/1, 1.37/1, 1.61/1 and
  4.21/7 --- Monte-Carlo $p$ 0.70, 0.30, 0.25 and 0.86 against each level's own simulated null,
  every one of them \emph{further} from significance than the $\chi^2$ value it replaces); a
  registered replication (\arm{bm2}) bought the two thinnest levels, and it is what makes the
  decomposition a testable restriction rather than an arithmetic identity.
```

**`paper/DRAFT-v4.md`** — OLD (line 179, `count == 1`):

```markdown
   independent submissions**, and each is internally homogeneous (within-level Q 0.17/1, 1.37/1,
   1.61/1 and 4.21/7); a registered replication (`bm2`) bought the two thinnest levels, and it is
   what makes the decomposition a testable restriction rather than an arithmetic identity.
```

NEW:

```markdown
   independent submissions**, and each is internally homogeneous (within-level Q 0.17/1, 1.37/1,
   1.61/1 and 4.21/7 — Monte-Carlo p 0.70, 0.30, 0.25 and 0.86 against each level's own simulated
   null, every one of them *further* from significance than the χ² value it replaces); a
   registered replication (`bm2`) bought the two thinnest levels, and it is what makes the
   decomposition a testable restriction rather than an arithmetic identity.
```

---

### R6 — Contribution 3 — the endpoint tail, calibrated

**`paper/paper.tex`** — OLD (line 273, `count == 1`):

```latex
  three other end-of-training columns the corpus carries, the base-optimiser share is 86.8\% on
  \texttt{final\_test} with the level ordering \emph{inverted} (SGD moves from the largest level
  to the smallest), 62.5\% on the 20-epoch column, and on \texttt{best\_test} there is no
  heterogeneity to decompose at all ($Q\ 9.87$ on 13 df, $p\ 0.70$, $\tau = 0.000$, $I^2 = 0\%$).
```

NEW:

```latex
  three other end-of-training columns the corpus carries, the base-optimiser share is 86.8\% on
  \texttt{final\_test} with the level ordering \emph{inverted} (SGD moves from the largest level
  to the smallest), 62.5\% on the 20-epoch column, and on \texttt{best\_test} there is no
  heterogeneity to decompose at all ($Q\ 9.87$ on 13 df, $p\ 0.70$, $\tau = 0.000$, $I^2 = 0\%$).
  \textbf{Referred to the right null (\S\ref{sec:threats} T13) the conditionality is sharper
  still}: only \plateau{} has heterogeneity that resolves at all (Monte-Carlo $p$ 0.013 against
  0.24, 0.90 and 0.16), so on three of the four endpoints there is nothing for any moderator to
  explain. The weight-free permutation, which does not need the heterogeneity established first,
  puts the base grouping at $\eta^2$ 0.840, 0.800, 0.276 and 0.670 (exact $p$ 0.00020, 0.00029,
  0.34 and 0.0076).
```

**`paper/DRAFT-v4.md`** — OLD (line 186, `count == 1`):

```markdown
   on the three other end-of-training columns the corpus carries, the base-optimiser share is
   86.8% on `final_test` with the level ordering *inverted* (SGD moves from the largest level to
   the smallest), 62.5% on the 20-epoch column, and on `best_test` there is no heterogeneity to
   decompose at all (Q 9.87 on 13 df, p 0.70, τ = 0.000, I² = 0%).
```

NEW:

```markdown
   on the three other end-of-training columns the corpus carries, the base-optimiser share is
   86.8% on `final_test` with the level ordering *inverted* (SGD moves from the largest level to
   the smallest), 62.5% on the 20-epoch column, and on `best_test` there is no heterogeneity to
   decompose at all (Q 9.87 on 13 df, p 0.70, τ = 0.000, I² = 0%). **Referred to the right null
   (§7 T13) the conditionality is sharper still**: only `plateau5` has heterogeneity that resolves
   at all (Monte-Carlo p 0.013 against 0.24, 0.90 and 0.16), so on three of the four endpoints
   there is nothing for any moderator to explain. The weight-free permutation, which does not need
   the heterogeneity established first, puts the base grouping at η² 0.840, 0.800, 0.276 and 0.670
   (exact p 0.00020, 0.00029, 0.34 and 0.0076).
```

---

### R7 — §3.3 Multiplicity — **own the t-vs-Q inconsistency**

**`paper/paper.tex`** — OLD (line 806, `count == 1`):

```latex
degrees of freedom and the paper's $t$ columns are the normal-approximation quantity.
```

NEW:

```latex
degrees of freedom and the paper's $t$ columns are the normal-approximation quantity.
\textbf{That concession was made for $t$ and, until this version, was not carried into the $Q$
layer. The inconsistency is ours, and we state it before a referee does.} Every Cochran $Q$ in
this paper is built out of the same 2--4 df standard errors, and until now every $Q$ $p$-value in
this paper was referred to $\chi^2_{k-1}$ as though those standard errors were known. They are
not; the reference is wrong in the anticonservative direction and by a large factor; and the next
paragraph, \S\ref{sec:moderator} and \S\ref{sec:threats} T13 carry into $Q$ exactly the
correction this paragraph already carried into $t$.
```

**`paper/DRAFT-v4.md`** — OLD (line 628, `count == 1`):

```markdown
because the two differ materially at 2–4 degrees of freedom and the paper's `t` columns are
the normal-approximation quantity.
```

NEW:

```markdown
because the two differ materially at 2–4 degrees of freedom and the paper's `t` columns are
the normal-approximation quantity. **That concession was made for `t` and, until this version,
was not carried into the Q layer. The inconsistency is ours, and we state it before a referee
does.** Every Cochran Q in this paper is built out of the same 2–4 df standard errors, and until
now every Q p-value in this paper was referred to χ²ₖ₋₁ as though those standard errors were
known. They are not; the reference is wrong in the anticonservative direction and by a large
factor; and the next paragraph, §4.4 and §7 T13 carry into Q exactly the correction this
paragraph already carried into `t`.
```

---

### R8 — §3.3 Heterogeneity — the calibration convention, stated once for the whole paper

**`paper/paper.tex`** — OLD (line 779, `count == 1`):

```latex
$Q = Q_{\mathrm{within}} + Q_{\mathrm{between}}$ with degrees of freedom adding likewise.
Figure~\ref{fig:moderator}(b) is that partition.
```

NEW:

```latex
$Q = Q_{\mathrm{within}} + Q_{\mathrm{between}}$ with degrees of freedom adding likewise.
Figure~\ref{fig:moderator}(b) is that partition.

\paragraph{The reference distribution $Q$ is referred to, and why it is not $\chi^2$.}
\eqref{eq:Q} is a $\chi^2_{k-1}$ statistic only when the $\se_i$ are known, or estimated at
enough degrees of freedom to be treated as known. Ours are Welch standard errors formed from two
arms of three to six runs: over the fourteen cells \S\ref{sec:moderator} pools, their
Welch--Satterthwaite degrees of freedom run from \textbf{2.04 to 9.68, median 2.91}. At three
degrees of freedom a sample variance is unstable enough that $w_i = \se_i^{-2}$ is a wildly
variable weight, and $Q$ is correspondingly over-dispersed --- its null mean on 13 df is
\textbf{26.9, not 13}. Beside every $\chi^2$ $p$-value that carries a claim we therefore print a
\textbf{Monte-Carlo $p$}, obtained by simulating this paper's own estimator under a homogeneous
truth: for each cell, $n_c$ and $n_n$ normal draws at that cell's own two arm standard deviations
and its own $n$, pushed through the same \texttt{welch()} and the same DerSimonian--Laird
\texttt{meta()} as everything else in the paper, 20{,}000 times at a registered seed. The code
is \texttt{analysis/c99\_qcalibration.py} and \S\ref{sec:threats} T13 states what it changes.
\textbf{Two nulls are simulated and both are printed}, because they bracket the answer: a
\emph{per-cell} null that takes each cell's own two arm standard deviations as the truth, and a
\emph{common-sd} null that gives every arm one pooled within-arm sd (0.186 pp on 70 df). The
first is the larger-$p$ end of the bracket and is the one we quote as \emph{the} Monte-Carlo
$p$; the second is printed beside it so that the reader sees the range rather than the flattering
end of it. Where an interval rather than a $p$-value is at stake we quote a \textbf{calibrated
half-width}: the 95th percentile of $|\hat\mu - \mu|$ in that same simulation, which has exact
95\% coverage by construction. Across three seeds the headline Monte-Carlo $p$ moves between
0.011 and 0.013, and at $200{,}000$ draws it is 0.012; we quote the registered 20{,}000-draw
value and state that range rather than implying more precision than 20{,}000 draws buy.
```

**`paper/DRAFT-v4.md`** — OLD (line 607, `count == 1`):

```markdown
with degrees of freedom adding likewise. Figure 2(b) is that partition.
```

NEW:

```markdown
with degrees of freedom adding likewise. Figure 2(b) is that partition.

**The reference distribution Q is referred to, and why it is not χ².** Eq. (12) is a χ²ₖ₋₁
statistic only when the se_i are known, or estimated at enough degrees of freedom to be treated
as known. Ours are Welch standard errors formed from two arms of three to six runs: over the
fourteen cells §4.4 pools, their Welch–Satterthwaite degrees of freedom run from **2.04 to 9.68,
median 2.91**. At three degrees of freedom a sample variance is unstable enough that
w_i = se_i^-2 is a wildly variable weight, and Q is correspondingly over-dispersed — its null
mean on 13 df is **26.9, not 13**. Beside every χ² p-value that carries a claim we therefore
print a **Monte-Carlo p**, obtained by simulating this paper's own estimator under a homogeneous
truth: for each cell, n_c and n_n normal draws at that cell's own two arm standard deviations and
its own n, pushed through the same `welch()` and the same DerSimonian–Laird `meta()` as
everything else in the paper, 20,000 times at a registered seed. The code is
`analysis/c99_qcalibration.py` and §7 T13 states what it changes. **Two nulls are simulated and
both are printed**, because they bracket the answer: a *per-cell* null that takes each cell's own
two arm standard deviations as the truth, and a *common-sd* null that gives every arm one pooled
within-arm sd (0.186 pp on 70 df). The first is the larger-p end of the bracket and is the one we
quote as *the* Monte-Carlo p; the second is printed beside it so that the reader sees the range
rather than the flattering end of it. Where an interval rather than a p-value is at stake we
quote a **calibrated half-width**: the 95th percentile of |μ̂ − μ| in that same simulation, which
has exact 95% coverage by construction. Across three seeds the headline Monte-Carlo p moves
between 0.011 and 0.013, and at 200,000 draws it is 0.012; we quote the registered 20,000-draw
value and state that range rather than implying more precision than 20,000 draws buy.
```

---

### R9 — §4.4 — the random-effects primary, and the quote block

**`paper/paper.tex`** — OLD (line 1499, `count == 1`):

```latex
\S\ref{sec:normalisation}. Those fourteen are heterogeneous: the
fixed-effect pool is $+0.530 \pm 0.029$ with

\begin{quote}
\textbf{$Q = 102.47$ on 13 df, $p = 5.5\times10^{-16}$}; DerSimonian--Laird
\textbf{$\tau = 0.295$ pp} against an rms measurement $\se$ of \textbf{0.143 pp}, i.e.\
$I^2 = 87\%$.
\end{quote}
```

NEW:

```latex
\S\ref{sec:normalisation}. Those fourteen are heterogeneous. Because $\tau > 0$ the
\textbf{random-effects} (DerSimonian--Laird) pool is the honest summary of them, and it is
$\mathbf{+0.611 \pm 0.087}$ pp, 95\% CI $[+0.441, +0.782]$. The \textbf{fixed-effect} pool ---
which is what Figure~\ref{fig:forest}'s inset, the endpoint table below and every other
``pooled $\Dstat$'' in this paper report --- is $+0.530 \pm 0.029$, and that interval covers the
truth 65\% of the time rather than 95\%: its calibrated 95\% half-width is 0.089 pp, not the
0.058 that $1.96\,\se$ gives (\S\ref{sec:threats} T13). We print both and label which is which
rather than quietly switching.

\begin{quote}
\textbf{$Q = 102.47$ on 13 df}: $p = 5.5\times10^{-16}$ against $\chi^2_{13}$, which is
\textbf{not the distribution this $Q$ has}, and \textbf{Monte-Carlo $p = 0.013$} against the
distribution it does have (0.002 under the common-sd null; \S\ref{sec:threats} T13). The null
$Q$ on 13 df has mean 26.9, median 21.4 and 95th percentile 62.4, against $\chi^2_{13}$'s 13,
12.3 and 22.4. DerSimonian--Laird \textbf{$\tau = 0.295$ pp} against an rms measurement $\se$
of \textbf{0.143 pp}, i.e.\ $I^2 = 87\%$ --- \textbf{both of these are upper bounds}, because
\eqref{eq:Q} subtracts $k - 1 = 13$ where the null mean is 26.9; recentred there they read
$\tau = 0.271$ pp and $I^2 = 74\%$ (0.280 pp and 79\% under the common-sd null). We keep the
standard estimator and label it rather than substituting one of our own.
\end{quote}
```

**`paper/DRAFT-v4.md`** — OLD (line 1147, `count == 1`):

```markdown
different meta-optimiser and is treated in §5.5. Those fourteen are heterogeneous: the
fixed-effect pool is +0.530 ± 0.029 with

> **Q = 102.47 on 13 df, p = 5.5e-16**; DerSimonian–Laird **τ = 0.295 pp** against an rms
> measurement se of **0.143 pp**, i.e. I² = 87%.
```

NEW:

```markdown
different meta-optimiser and is treated in §5.5. Those fourteen are heterogeneous. Because
τ > 0 the **random-effects** (DerSimonian–Laird) pool is the honest summary of them, and it is
**+0.611 ± 0.087 pp**, 95% CI [+0.441, +0.782]. The **fixed-effect** pool — which is what
Figure 1's inset, the endpoint table below and every other "pooled D" in this paper report — is
+0.530 ± 0.029, and that interval covers the truth 65% of the time rather than 95%: its
calibrated 95% half-width is 0.089 pp, not the 0.058 that 1.96 se gives (§7 T13). We print both
and label which is which rather than quietly switching.

> **Q = 102.47 on 13 df**: p = 5.5e-16 against χ²₁₃, which is **not the distribution this Q
> has**, and **Monte-Carlo p = 0.013** against the distribution it does have (0.002 under the
> common-sd null; §7 T13). The null Q on 13 df has mean 26.9, median 21.4 and 95th percentile
> 62.4, against χ²₁₃'s 13, 12.3 and 22.4. DerSimonian–Laird **τ = 0.295 pp** against an rms
> measurement se of **0.143 pp**, i.e. I² = 87% — **both of these are upper bounds**, because
> Eq. (12) subtracts k − 1 = 13 where the null mean is 26.9; recentred there they read τ = 0.271
> pp and I² = 74% (0.280 pp and 79% under the common-sd null). We keep the standard estimator and
> label it rather than substituting one of our own.
```

---

### R10h — §4.4 level table — header (and `\small`→`\footnotesize`, see §6.2)

**`paper/paper.tex`** — OLD (line 1536, `count == 1`):

```latex
\begin{center}
\small
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}llrrll@{}}
\toprule
base optimiser & base state, from the runs' own \texttt{ARGS} line & cells & batches &
  pooled $\Dstat$ (pp) & within-level $Q$/df ($p$) \\
```

NEW:

```latex
\begin{center}
\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}llrrll@{}}
\toprule
base optimiser & base state, from the runs' own \texttt{ARGS} line & cells & batches &
  pooled $\Dstat$ (pp) & within-level $Q$/df ($\chi^2$ $p$; MC $p$) \\
```

**`paper/DRAFT-v4.md`** — OLD (line 1173, `count == 1`):

```markdown
| base optimiser | base state, from the runs' own `ARGS` line | cells | batches | pooled D (pp) | within-level Q |
```

NEW:

```markdown
| base optimiser | base state, from the runs' own `ARGS` line | cells | batches | pooled D (pp) | within-level Q/df (χ² p; MC p) |
```

---

### R10 — §4.4 level table — the four rows

**`paper/paper.tex`** — OLD (line 1544, `count == 1`):

```latex
SGD     & no momentum, no second moment & 2 & 2 & $\mathbf{+1.000 \pm 0.067}$ & 0.17 / 1 ($p$ 0.68) \\
RMSProp & second moment 0.999, no momentum & 2 & 2 & $\mathbf{+0.720 \pm 0.128}$ & 1.37 / 1 ($p$ 0.24) \\
SGDm    & momentum 0.99, no second moment & 8 & 7 & $\mathbf{+0.556 \pm 0.045}$ & 4.21 / 7 ($p$ 0.76) \\
AdamW   & momentum 0.9 + second moment 0.999 & 2 & 2 & $\mathbf{+0.189 \pm 0.052}$ & 1.61 / 1 ($p$ 0.20) \\
```

NEW:

```latex
SGD     & no momentum, no second moment & 2 & 2 & $\mathbf{+1.000 \pm 0.067}$ & 0.17 / 1 (0.68; \textbf{0.70}) \\
RMSProp & second moment 0.999, no momentum & 2 & 2 & $\mathbf{+0.720 \pm 0.128}$ & 1.37 / 1 (0.24; \textbf{0.30}) \\
SGDm    & momentum 0.99, no second moment & 8 & 7 & $\mathbf{+0.556 \pm 0.045}$ & 4.21 / 7 (0.76; \textbf{0.86}) \\
AdamW   & momentum 0.9 + second moment 0.999 & 2 & 2 & $\mathbf{+0.189 \pm 0.052}$ & 1.61 / 1 (0.20; \textbf{0.25}) \\
```

**`paper/DRAFT-v4.md`** — OLD (line 1175, `count == 1`):

```markdown
| SGD | no momentum, no second moment | 2 | 2 | **+1.000 ± 0.067** | 0.17 / 1 (p 0.68) |
| RMSProp | second moment 0.999, no momentum | 2 | 2 | **+0.720 ± 0.128** | 1.37 / 1 (p 0.24) |
| SGDm | momentum 0.99, no second moment | 8 | 7 | **+0.556 ± 0.045** | 4.21 / 7 (p 0.76) |
| AdamW | momentum 0.9 + second moment 0.999 | 2 | 2 | **+0.189 ± 0.052** | 1.61 / 1 (p 0.20) |
```

NEW:

```markdown
| SGD | no momentum, no second moment | 2 | 2 | **+1.000 ± 0.067** | 0.17 / 1 (0.68; **0.70**) |
| RMSProp | second moment 0.999, no momentum | 2 | 2 | **+0.720 ± 0.128** | 1.37 / 1 (0.24; **0.30**) |
| SGDm | momentum 0.99, no second moment | 8 | 7 | **+0.556 ± 0.045** | 4.21 / 7 (0.76; **0.86**) |
| AdamW | momentum 0.9 + second moment 0.999 | 2 | 2 | **+0.189 ± 0.052** | 1.61 / 1 (0.20; **0.25**) |
```

---

### R11 — §4.4 — the between-base sentence

**`paper/paper.tex`** — OLD (line 1552, `count == 1`):

```latex
\textbf{Between base optimisers, $Q = 95.12$ on 3 df ($p = 1.7\times10^{-20}$) --- 92.8\% of the
total; within levels, $Q = 7.36$ on 10 df ($p = 0.69$).}
```

NEW:

```latex
\textbf{Between base optimisers, $Q = 95.12$ on 3 df --- 92.8\% of the total; within levels,
$Q = 7.36$ on 10 df.} Both $p$-values are printed twice throughout, because the first of them is
computed against the wrong reference: between-base $p = 1.7\times10^{-20}$ against $\chi^2_3$
and \textbf{Monte-Carlo $p = 0.005$} against the distribution that $Q$ actually has (0.0007 under
the common-sd null), within-level $p = 0.69$ against $\chi^2_{10}$ and Monte-Carlo $p = 0.86$.
\textbf{The direction of every one of these corrections is the same}: heterogeneity is far less
resolved than $\chi^2$ says, and homogeneity is more so. \S\ref{sec:threats} T13 gives the
simulation, and the weight-free permutation two paragraphs below is what this subsection's
central claim now rests on.
```

**`paper/DRAFT-v4.md`** — OLD (line 1180, `count == 1`):

```markdown
**Between base optimisers, Q = 95.12 on 3 df (p = 1.7e-20) — 92.8% of the total; within levels,
Q = 7.36 on 10 df (p = 0.69).**
```

NEW:

```markdown
**Between base optimisers, Q = 95.12 on 3 df — 92.8% of the total; within levels, Q = 7.36 on
10 df.** Both p-values are printed twice throughout, because the first of them is computed
against the wrong reference: between-base p = 1.7e-20 against χ²₃ and **Monte-Carlo p = 0.005**
against the distribution that Q actually has (0.0007 under the common-sd null), within-level
p = 0.69 against χ²₁₀ and Monte-Carlo p = 0.86. **The direction of every one of these corrections
is the same**: heterogeneity is far less resolved than χ² says, and homogeneity is more so. §7
T13 gives the simulation, and the weight-free permutation two paragraphs below is what this
subsection's central claim now rests on.
```

---

### R12 — §4.4 — the permutation paragraph, and **the new weight-free test**

**`paper/paper.tex`** — OLD (line 1569, `count == 1`):

```latex
reject it: all four levels are homogeneous, $p$ 0.20--0.76. Over all 45{,}045 partitions of the
fourteen cells with the realised shape $\{8, 2, 2, 2\}$, the base-optimiser partition ranks 14th
(permutation $p = 0.00031$, against a median share of 0.333 and a maximum of 0.957).
Leave-one-cell-out over the fourteen gives 89.6\% to 95.7\%.
```

NEW:

```latex
reject it: all four levels are homogeneous, $\chi^2$ $p$ 0.20--0.76 and Monte-Carlo $p$
0.25--0.86. (That registered rule is itself mis-sized for the same reason: simulated, $Q > 3.841$
fires on a homogeneous two-cell level 10\% of the time and not 5\%, and the size-0.05 critical
value is 6.22. A level that does not fire it is therefore \emph{stronger} evidence of
homogeneity than the rule claims, not weaker.) Over all 45{,}045 partitions of the fourteen cells
with the realised shape $\{8, 2, 2, 2\}$, the base-optimiser partition ranks 14th
(permutation $p = 0.00031$, against a median share of 0.333 and a maximum of 0.957).
Leave-one-cell-out over the fourteen gives 89.6\% to 95.7\%.

\textbf{The weight-free version of that permutation, which is what this subsection now rests on.}
The rank-14 test above permutes labels but still scores each partition by a \emph{weighted} share
of $Q$, so it inherits the $\se_i$ and their two-to-four degrees of freedom. Scoring the same
45{,}045 partitions by the \textbf{unweighted} between-group share of the fourteen $\Dstat$'s
variance removes the standard errors from the test altogether:
\begin{quote}
$\eta^2 = \mathbf{0.840}$ for the base-optimiser partition, \textbf{rank 9 of 45{,}045}, exact
$p = \mathbf{0.00020}$, against a null median of 0.200 and a maximum of 0.894.
\end{quote}
\textbf{This is the load-bearing statistic for the moderator claim from here on}, because it
does not depend on the $\se$ estimates at all and so is untouched by \S\ref{sec:threats} T13.
It is an exact enumeration, not a sample, so it carries no Monte-Carlo error; and run on the
weighted share it reproduces the published rank 14 and $p = 0.00031$ above, which is how we know
the enumeration is the paper's own. Note what it does and does not say: like the rank-14 test it
is conditional on the observed spread of the fourteen $\Dstat$ and asks only whether \emph{this
partition} of them is special. Whether there is any spread to partition is the separate question
$Q$ answers, and calibrated, $Q$ answers it at $p = 0.013$.
```

**`paper/DRAFT-v4.md`** — OLD (line 1195, `count == 1`):

```markdown
all four levels are homogeneous, p 0.20–0.76. Over all 45,045 partitions of the fourteen cells
with the realised shape {8, 2, 2, 2}, the base-optimiser partition ranks 14th (permutation
p = 0.00031, against a median share of 0.333 and a maximum of 0.957). Leave-one-cell-out over the
fourteen gives 89.6% to 95.7%.
```

NEW:

```markdown
all four levels are homogeneous, χ² p 0.20–0.76 and Monte-Carlo p 0.25–0.86. (That registered
rule is itself mis-sized for the same reason: simulated, Q > 3.841 fires on a homogeneous
two-cell level 10% of the time and not 5%, and the size-0.05 critical value is 6.22. A level that
does not fire it is therefore *stronger* evidence of homogeneity than the rule claims, not
weaker.) Over all 45,045 partitions of the fourteen cells with the realised shape {8, 2, 2, 2},
the base-optimiser partition ranks 14th (permutation p = 0.00031, against a median share of 0.333
and a maximum of 0.957). Leave-one-cell-out over the fourteen gives 89.6% to 95.7%.

**The weight-free version of that permutation, which is what this subsection now rests on.** The
rank-14 test above permutes labels but still scores each partition by a *weighted* share of Q, so
it inherits the se_i and their two-to-four degrees of freedom. Scoring the same 45,045 partitions
by the **unweighted** between-group share of the fourteen D's variance removes the standard
errors from the test altogether:

> η² = **0.840** for the base-optimiser partition, **rank 9 of 45,045**, exact p = **0.00020**,
> against a null median of 0.200 and a maximum of 0.894.

**This is the load-bearing statistic for the moderator claim from here on**, because it does not
depend on the se estimates at all and so is untouched by §7 T13. It is an exact enumeration, not
a sample, so it carries no Monte-Carlo error; and run on the weighted share it reproduces the
published rank 14 and p = 0.00031 above, which is how we know the enumeration is the paper's own.
Note what it does and does not say: like the rank-14 test it is conditional on the observed
spread of the fourteen D and asks only whether *this partition* of them is special. Whether there
is any spread to partition is the separate question Q answers, and calibrated, Q answers it at
p = 0.013.
```

---

### R13 — §4.4 — the SGDm quote block, incl. the calibrated τ limit

**`paper/paper.tex`** — OLD (line 1627, `count == 1`):

```latex
clusters} --- the pool is $\mathbf{+0.556 \pm 0.045}$ with $\mathbf{Q = 4.21}$ \textbf{on 7 df,
$p = 0.76$, $I^2 = 0\%$, $\tau = 0.000$} (one-sided 95\% $Q$-profile upper limit
\textbf{0.109 pp}, below the 0.146 pp rms measurement $\se$ of the cells themselves).
```

NEW:

```latex
clusters} --- the pool is $\mathbf{+0.556 \pm 0.045}$ with $\mathbf{Q = 4.21}$ \textbf{on 7 df,
$I^2 = 0\%$, $\tau = 0.000$}. $\chi^2_7$ puts that $Q$ at $p = 0.76$; \textbf{its own simulated
null, whose median is 9.4, puts it at Monte-Carlo $p = 0.86$ and at the 14th percentile}
(\S\ref{sec:threats} T13), so the homogeneity claim holds and the reference it used to be stated
against did not. The one-sided 95\% $Q$-profile upper limit on $\tau$ is \textbf{0.109 pp}
against $\chi^2_7$ and \textbf{0.097 pp} when the profile is simulated at each trial $\tau$ ---
\textbf{the one quantity in this subsection the $\chi^2$ reference gets wrong in our
disfavour} --- and both are below the 0.146 pp rms measurement $\se$ of the cells themselves. The
pool's own interval is the one that moves the other way: $\pm 1.96\,\se$ is $\pm 0.088$ pp and
covers 73\%, and the calibrated 95\% half-width is $\pm 0.121$ pp.
```

**`paper/DRAFT-v4.md`** — OLD (line 1244, `count == 1`):

```markdown
> budgets (100 and 300 epochs), three β-boxes and two clusters** — the pool is **+0.556 ± 0.045**
> with **Q = 4.21 on 7 df, p = 0.76, I² = 0%, τ = 0.000** (one-sided 95% Q-profile upper limit
> **0.109 pp**, below the 0.146 pp rms measurement se of the cells themselves).
```

NEW:

```markdown
> budgets (100 and 300 epochs), three β-boxes and two clusters** — the pool is **+0.556 ± 0.045**
> with **Q = 4.21 on 7 df, I² = 0%, τ = 0.000**. χ²₇ puts that Q at p = 0.76; **its own simulated
> null, whose median is 9.4, puts it at Monte-Carlo p = 0.86 and at the 14th percentile** (§7
> T13), so the homogeneity claim holds and the reference it used to be stated against did not.
> The one-sided 95% Q-profile upper limit on τ is **0.109 pp** against χ²₇ and **0.097 pp** when
> the profile is simulated at each trial τ — **the one quantity in this subsection the χ²
> reference gets wrong in our disfavour** — and both are below the 0.146 pp rms measurement se of
> the cells themselves. The pool's own interval is the one that moves the other way: ± 1.96 se is
> ± 0.088 pp and covers 73%, and the calibrated 95% half-width is ± 0.121 pp.
```

---

### R14h — §4.4 endpoint table — header (8→9 columns in tex)

**`paper/paper.tex`** — OLD (line 1727, `count == 1`):

```latex
\begin{tabular}{@{}lrrrrrrr@{}}
\toprule
endpoint & pooled $\Dstat$ & $Q$ / 13 df & $p$ & $\tau$ &
  between-base $Q$ & share & $\Dstat > 0$ \\
```

NEW:

```latex
\begin{tabular}{@{}lrrrrrrrr@{}}
\toprule
endpoint & pooled $\Dstat$ & $Q$ / 13 df & $p$ ($\chi^2_{13}$) & MC $p$ & $\tau$ &
  between-base $Q$ & share & $\Dstat > 0$ \\
```

**`paper/DRAFT-v4.md`** — OLD (line 1329, `count == 1`):

```markdown
| endpoint | pooled D (pp) | Q / 13 df | p | τ (pp) | between-base Q / 3 df | share of Q | cells D > 0 |
```

NEW:

```markdown
| endpoint | pooled D (pp) | Q / 13 df | p (χ²₁₃) | MC p | τ (pp) | between-base Q / 3 df | share of Q | cells D > 0 |
```

---

### R14 — §4.4 endpoint table — the four rows, MC p column

**`paper/paper.tex`** — OLD (line 1732, `count == 1`):

```latex
\plateau{} \emph{(primary)}         & $+0.530 \pm 0.029$ & 102.47 & $5.5\times10^{-16}$ & 0.295 & 95.12 & \textbf{92.8\%} & 20 / 20 \\
\texttt{plateau} \emph{(20-epoch)}  & $+0.449 \pm 0.024$ &  29.37 & 0.0058              & 0.101 & 18.36 & 62.5\%          & 20 / 20 \\
\texttt{best\_test}                 & $+0.396 \pm 0.025$ &   \textbf{9.87} & \textbf{0.70} & \textbf{0.000} & 3.70 & 37.5\% & 20 / 20 \\
\texttt{final\_test}                & $+0.614 \pm 0.043$ &  39.91 & $1.4\times10^{-4}$  & 0.251 & 34.66 & 86.8\%          & \textbf{19 / 20} \\
```

NEW:

```latex
\plateau{} \emph{(primary)}         & $+0.530 \pm 0.029$ & 102.47 & $5.5\times10^{-16}$ & \textbf{0.013} & 0.295 & 95.12 & \textbf{92.8\%} & 20 / 20 \\
\texttt{plateau} \emph{(20-epoch)}  & $+0.449 \pm 0.024$ &  29.37 & 0.0058              & \textbf{0.24}  & 0.101 & 18.36 & 62.5\%          & 20 / 20 \\
\texttt{best\_test}                 & $+0.396 \pm 0.025$ &   \textbf{9.87} & \textbf{0.70} & \textbf{0.90} & \textbf{0.000} & 3.70 & 37.5\% & 20 / 20 \\
\texttt{final\_test}                & $+0.614 \pm 0.043$ &  39.91 & $1.4\times10^{-4}$  & \textbf{0.16}  & 0.251 & 34.66 & 86.8\%          & \textbf{19 / 20} \\
```

**`paper/DRAFT-v4.md`** — OLD (line 1331, `count == 1`):

```markdown
| `plateau5` *(primary)* | +0.530 ± 0.029 | 102.47 | 5.5e−16 | 0.295 | 95.12 | **92.8%** | 20 / 20 |
| `plateau` *(20-epoch)* | +0.449 ± 0.024 | 29.37 | 0.0058 | 0.101 | 18.36 | 62.5% | 20 / 20 |
| `best_test` | +0.396 ± 0.025 | **9.87** | **0.70** | **0.000** | 3.70 | 37.5% | 20 / 20 |
| `final_test` | +0.614 ± 0.043 | 39.91 | 1.4e−4 | 0.251 | 34.66 | 86.8% | **19 / 20** |
```

NEW:

```markdown
| `plateau5` *(primary)* | +0.530 ± 0.029 | 102.47 | 5.5e−16 | **0.013** | 0.295 | 95.12 | **92.8%** | 20 / 20 |
| `plateau` *(20-epoch)* | +0.449 ± 0.024 | 29.37 | 0.0058 | **0.24** | 0.101 | 18.36 | 62.5% | 20 / 20 |
| `best_test` | +0.396 ± 0.025 | **9.87** | **0.70** | **0.90** | **0.000** | 3.70 | 37.5% | 20 / 20 |
| `final_test` | +0.614 ± 0.043 | 39.91 | 1.4e−4 | **0.16** | 0.251 | 34.66 | 86.8% | **19 / 20** |
```

---

### R14n — §4.4 endpoint table — the note (tex: replaced; md: **inserted**, there was none)

**`paper/paper.tex`** — OLD (line 1739, `count == 1`):

```latex
\noindent\emph{Columns: pooled $\Dstat$ in pp over the fourteen cells; Cochran $Q$ on 13 df with
its $p$; DerSimonian--Laird $\tau$ in pp; the between-base component of $Q$ on 3 df; its share of
$Q$; and how many of the twenty count-matched cells of Table~\ref{tab:D} are positive.}
```

NEW:

```latex
\noindent\emph{Columns: the \textbf{fixed-effect} pooled $\Dstat$ in pp over the fourteen
cells; Cochran $Q$ on 13 df; its $p$ against $\chi^2_{13}$ and its Monte-Carlo $p$ against the
distribution $Q$ actually has at these degrees of freedom (per-cell null; the common-sd null
gives 0.002, 0.19, 0.88 and 0.080); DerSimonian--Laird $\tau$ in pp, an upper bound for the same
reason; the between-base component of $Q$ on 3 df; its share of $Q$; and how many of the twenty
count-matched cells of Table~\ref{tab:D} are positive.}

\noindent \textbf{The MC column is the one that means anything, and it changes the reading of
three rows out of four} (\S\ref{sec:threats} T13). The random-effects pools of the same four
rows are $+0.611 \pm 0.087$, $+0.480 \pm 0.038$, $+0.396 \pm 0.025$ and $+0.674 \pm 0.097$ pp;
the between-base $Q$'s Monte-Carlo $p$'s are 0.005, 0.099, 0.60 and 0.025; and the weight-free
permutation, which uses no $\se$ at all and therefore survives all of this untouched, gives
$\eta^2$ 0.840, 0.800, 0.276 and 0.670 at exact $p$ 0.00020, 0.00029, 0.34 and 0.0076.
```

**`paper/DRAFT-v4.md`** — OLD (line 1336, `count == 1`):

```markdown
The same four endpoints, split by base optimiser — the table this subsection is built on,
recomputed three more times:
```

NEW:

```markdown
*Columns: the **fixed-effect** pooled D in pp over the fourteen cells; Cochran Q on 13 df; its p
against χ²₁₃ and its Monte-Carlo p against the distribution Q actually has at these degrees of
freedom (per-cell null; the common-sd null gives 0.002, 0.19, 0.88 and 0.080); DerSimonian–Laird
τ in pp, an upper bound for the same reason; the between-base component of Q on 3 df; its share
of Q; and how many of the twenty count-matched cells of Table 2 are positive.*

**The MC column is the one that means anything, and it changes the reading of three rows out of
four** (§7 T13). The random-effects pools of the same four rows are +0.611 ± 0.087,
+0.480 ± 0.038, +0.396 ± 0.025 and +0.674 ± 0.097 pp; the between-base Q's Monte-Carlo p's are
0.005, 0.099, 0.60 and 0.025; and the weight-free permutation, which uses no se at all and
therefore survives all of this untouched, gives η² 0.840, 0.800, 0.276 and 0.670 at exact p
0.00020, 0.00029, 0.34 and 0.0076.

The same four endpoints, split by base optimiser — the table this subsection is built on,
recomputed three more times:
```

---

### R15 — §4.4 reading 1 — “below its own degrees of freedom” repaired

**`paper/paper.tex`** — OLD (line 1763, `count == 1`):

```latex
\item \textbf{On \texttt{best\_test} there is no heterogeneity to decompose at all.} $Q = 9.87$ on
  13 df is \emph{below its own degrees of freedom}: $p = 0.70$, $I^2 = 0\%$, DerSimonian--Laird
  $\tau = 0.000$, and between base optimisers $Q$ is 3.70 on 3 df ($p = 0.30$).
```

NEW:

```latex
\item \textbf{On \texttt{best\_test} there is no heterogeneity to decompose at all.} $Q = 9.87$
  on 13 df sits at the \textbf{tenth percentile of its own simulated null} (Monte-Carlo
  $p = 0.90$). ``Below its own degrees of freedom'' is the wrong way to say it --- that null's
  mean is 25.3, not 13 (\S\ref{sec:threats} T13) --- but it is right about the direction and by
  a wider margin than $\chi^2_{13}$'s $p = 0.70$ suggested: $I^2 = 0\%$, DerSimonian--Laird
  $\tau = 0.000$, and between base optimisers $Q$ is 3.70 on 3 df ($p = 0.30$ against $\chi^2_3$,
  Monte-Carlo $p = 0.60$). The weight-free permutation agrees and is the cleanest statement of it:
  $\eta^2 = 0.276$, rank 15{,}248 of 45{,}045, exact $p = 0.34$.
```

**`paper/DRAFT-v4.md`** — OLD (line 1348, `count == 1`):

```markdown
1. **On `best_test` there is no heterogeneity to decompose at all.** Q = 9.87 on 13 df is *below
   its own degrees of freedom*: p = 0.70, I² = 0%, DerSimonian–Laird τ = 0.000, and between base
   optimisers Q is 3.70 on 3 df (p = 0.30).
```

NEW:

```markdown
1. **On `best_test` there is no heterogeneity to decompose at all.** Q = 9.87 on 13 df sits at
   the **tenth percentile of its own simulated null** (Monte-Carlo p = 0.90). "Below its own
   degrees of freedom" is the wrong way to say it — that null's mean is 25.3, not 13 (§7 T13) —
   but it is right about the direction and by a wider margin than χ²₁₃'s p = 0.70 suggested:
   I² = 0%, DerSimonian–Laird τ = 0.000, and between base optimisers Q is 3.70 on 3 df (p = 0.30
   against χ²₃, Monte-Carlo p = 0.60). The weight-free permutation agrees and is the cleanest
   statement of it: η² = 0.276, rank 15,248 of 45,045, exact p = 0.34.
```

---

### R16 — §4.4 — **a fourth reading**

**`paper/paper.tex`** — OLD (line 1780, `count == 1`):

```latex
  \plateau{} maximises $Q$, maximises $\tau$ and maximises the between-base share.
\end{enumerate}
```

NEW:

```latex
  \plateau{} maximises $Q$, maximises $\tau$ and maximises the between-base share.
\item \textbf{Calibrated, \plateau{} is the only one of the four with resolved heterogeneity at
  all.} Referring each row's $Q$ to its own simulated null instead of to $\chi^2_{13}$
  (\S\ref{sec:threats} T13) gives Monte-Carlo $p$ 0.013, 0.24, 0.90 and 0.16. The 20-epoch
  column's $p = 0.0058$ and \texttt{final\_test}'s $p = 1.4\times10^{-4}$ \textbf{do not
  survive the correct reference}; \plateau{}'s $5.5\times10^{-16}$ does, at $p = 0.013$. This
  makes item 3 sharper rather than softer --- on three of the four endpoints there is no resolved
  spread for any moderator to explain --- and it is a self-criticism, so we print it in the same
  list as the other three rather than in a footnote. The claim it does \emph{not} touch is
  \S\ref{sec:primary}'s: the sign, which is 20 / 20 on three endpoints and 19 / 20 on the
  fourth, is a per-cell quantity and is not pooled.
\end{enumerate}
```

**`paper/DRAFT-v4.md`** — OLD (line 1364, `count == 1`):

```markdown
   maximises Q, maximises τ and maximises the between-base share.
```

NEW:

```markdown
   maximises Q, maximises τ and maximises the between-base share.
4. **Calibrated, `plateau5` is the only one of the four with resolved heterogeneity at all.**
   Referring each row's Q to its own simulated null instead of to χ²₁₃ (§7 T13) gives Monte-Carlo
   p 0.013, 0.24, 0.90 and 0.16. The 20-epoch column's p = 0.0058 and `final_test`'s p = 1.4e−4
   **do not survive the correct reference**; `plateau5`'s 5.5e−16 does, at p = 0.013. This makes
   item 3 sharper rather than softer — on three of the four endpoints there is no resolved spread
   for any moderator to explain — and it is a self-criticism, so we print it in the same list as
   the other three rather than in a footnote. The claim it does *not* touch is §4.3's: the sign,
   which is 20 / 20 on three endpoints and 19 / 20 on the fourth, is a per-cell quantity and is
   not pooled.
```

---

### R17 — §4.4 — the second “+0.396 to +0.614” site, labelled

**`paper/paper.tex`** — OLD (line 1785, `count == 1`):

```latex
($+0.396$ to $+0.614$ pp), and the count-matched sign result of Table~\ref{tab:D} reads
```

NEW:

```latex
(fixed-effect pools $+0.396$ to $+0.614$ pp; random-effects $+0.396$ to $+0.674$), and the
count-matched sign result of Table~\ref{tab:D} reads
```

**`paper/DRAFT-v4.md`** — OLD (line 1367, `count == 1`):

```markdown
decomposition.** The fourteen-cell pool is positive and of one order on all four (+0.396 to
+0.614 pp), and the count-matched sign result of Table 2 reads **20 / 20, 20 / 20, 20 / 20 and
```

NEW:

```markdown
decomposition.** The fourteen-cell pool is positive and of one order on all four (fixed-effect
pools +0.396 to +0.614 pp; random-effects +0.396 to +0.674), and the count-matched sign result of
Table 2 reads **20 / 20, 20 / 20, 20 / 20 and
```

---

### R18 — Figure 2’s caption

**`paper/paper.tex`** — OLD (line 1933, `count == 1`):

```latex
\textbf{95.12 of 102.47 (92.8\%) is between base optimisers}, on 3 df,
$p\ 1.7\times10^{-20}$; the within-level remainder is 7.36 on 10 df, $p$ 0.69.
```

NEW:

```latex
\textbf{95.12 of 102.47 (92.8\%) is between base optimisers}, on 3 df. \textbf{Every $p$ drawn
inside this figure or quoted in this caption is a $\chi^2$ value and is anticonservative}
(\S\ref{sec:threats} T13): between-base $p\ 1.7\times10^{-20}$ against $\chi^2_3$ is
\textbf{Monte-Carlo $p\ 0.005$} against the distribution $Q$ actually has, and the within-level
remainder, 7.36 on 10 df at $\chi^2$ $p$ 0.69, is Monte-Carlo $p$ 0.86; the four per-level
$Q$'s are at Monte-Carlo $p$ 0.70, 0.30, 0.25 and 0.86. The weight-free statement of panel (b),
which needs no $\se$ and is what \S\ref{sec:moderator} now rests on: $\eta^2 = 0.840$, rank 9
of all 45{,}045 partitions of the realised $\{8,2,2,2\}$ shape, exact $p = 0.00020$.
```

**`paper/DRAFT-v4.md`** — OLD (line 1498, `count == 1`):

```markdown
Cochran Q (Eq. 12): **95.12 of 102.47 (92.8%) is between base optimisers**, on 3 df, p 1.7e-20;
the within-level remainder is 7.36 on 10 df, p 0.69.
```

NEW:

```markdown
Cochran Q (Eq. 12): **95.12 of 102.47 (92.8%) is between base optimisers**, on 3 df. **Every p
drawn inside this figure or quoted in this caption is a χ² value and is anticonservative** (§7
T13): between-base p 1.7e-20 against χ²₃ is **Monte-Carlo p 0.005** against the distribution Q
actually has, and the within-level remainder, 7.36 on 10 df at χ² p 0.69, is Monte-Carlo p 0.86;
the four per-level Q's are at Monte-Carlo p 0.70, 0.30, 0.25 and 0.86. The weight-free statement
of panel (b), which needs no se and is what §4.4 now rests on: η² = 0.840, rank 9 of all 45,045
partitions of the realised {8,2,2,2} shape, exact p = 0.00020.
```

---

### R19 — §7.2 — **the new threat item T13**

**`paper/paper.tex`** — OLD (line 3619, `count == 1`):

```latex
(\S\ref{sec:rule11}). We cannot report a selection-free estimate of anything and we do not claim
one.

\section{Reproducibility}
```

NEW:

```latex
(\S\ref{sec:rule11}). We cannot report a selection-free estimate of anything and we do not claim
one.

\paragraph{T13 --- The meta-analytic layer was referred to the wrong null, and this version
carries the correction rather than softening the claim.}
Every Cochran $Q$ in this paper weights cells by $w_i = \se_i^{-2}$, and every $\se_i$ is a
Welch standard error built from two arms of three to six runs: over \S\ref{sec:moderator}'s
fourteen cells the Welch--Satterthwaite degrees of freedom run from \textbf{2.04 to 9.68, median
2.91}. $Q$ is therefore \textbf{not} $\chi^2_{k-1}$. Simulating this paper's own estimator under
a homogeneous truth --- 20{,}000 draws through the same \texttt{welch()} and the same
DerSimonian--Laird \texttt{meta()}, \texttt{analysis/c99\_qcalibration.py}, seed registered ---
gives a null $Q$ on 13 df with \textbf{mean 26.9, median 21.4 and 95th percentile 62.4}, against
$\chi^2_{13}$'s 13, 12.3 and 22.4. \S\ref{sec:metric} already conceded exactly this problem one
layer down, for $t$ at 2--4 df, and Welch-corrects every $t$ in the paper on that ground;
\textbf{the concession was not carried into the $Q$ layer until now, and that inconsistency was
ours}. Four consequences, stated here rather than left to be found.
\begin{enumerate}
\item \textbf{Every $\chi^2$ $p$-value on this layer is anticonservative, some of them by many
  orders of magnitude.} $Q = 102.47$ is printed at $p = 5.5\times10^{-16}$ and has Monte-Carlo
  $p = 0.013$ (0.002 under a common-sd null); between-base $Q = 95.12$ is printed at
  $p = 1.7\times10^{-20}$ and has Monte-Carlo $p = 0.005$ (0.0007). Fourteen and seventeen orders
  of magnitude. Both $p$-values are now printed at every site that carries one.
\item \textbf{$\tau$ and $I^2$ are upper bounds}, because \eqref{eq:Q} subtracts $k - 1 = 13$
  where the null mean of $Q$ is 26.9. Recentred on the simulated null, $\tau = 0.295 \to 0.271$
  pp and $I^2 = 87\% \to 74\%$ (0.280 pp and 79\% under the common-sd null). We keep the
  standard estimator, which is what a reader will recompute, and label it.
\item \textbf{The pooled intervals undercover.} The eight-cell SGDm pool's $\pm 1.96\,\se$
  interval covers 73\%, not 95\%; its calibrated 95\% half-width is $\pm 0.121$ pp against the
  $\pm 0.088$ that its $\se$ implies. The fourteen-cell fixed-effect interval covers 65\%, with
  a calibrated half-width of 0.089 pp against 0.058. \textbf{No sign, ordering or per-cell
  quantity in this paper depends on either}: nothing in Table~\ref{tab:D} is pooled.
\item \textbf{One quantity moves the other way, and we report it for that reason.}
  \S\ref{sec:moderator}'s one-sided 95\% $Q$-profile upper limit on the SGDm $\tau$ is 0.109 pp
  against $\chi^2_7$ and \textbf{0.097 pp} when the profile is simulated at each trial $\tau$:
  there the $\chi^2$ reference is conservative. A correction that only ever helped its authors
  would not be one.
\end{enumerate}
\textbf{What survives, and it is the whole of the claim.} The decomposition is not deleted and
does not need to be. The heterogeneity resolves against its own simulated null
($p = 0.013$); the base-optimiser structure is confirmed by a test that uses \emph{no} standard
errors at all --- an exact enumeration of all 45{,}045 partitions of the realised
$\{8, 2, 2, 2\}$ shape, $\eta^2 = 0.840$, rank 9, $p = 0.00020$ --- and that permutation, not
the $\chi^2$ $p$, is what \S\ref{sec:contributions}'s third contribution now rests on. Every
level remains homogeneous and by a wider margin than before: the calibrated $p$'s are 0.70, 0.30,
0.25 and 0.86 where the $\chi^2$ values were 0.68, 0.24, 0.20 and 0.76, and the registered
$Q > 3.841$ rule that \S\ref{sec:moderator} says the levels could have failed has a realised
size of 0.10 rather than 0.05 (size-0.05 critical value 6.22), so not firing it is stronger
evidence than the rule claimed. \textbf{What does not survive is the endpoint table's other three
rows}: on the 20-epoch column $Q = 29.37$ ($\chi^2$ $p$ 0.0058) has Monte-Carlo $p$ 0.24, and on
\texttt{final\_test} $Q = 39.91$ ($\chi^2$ $p$ $1.4\times10^{-4}$) has Monte-Carlo $p$ 0.16.
\textbf{On a calibrated reference \plateau{} is the only endpoint of the four with resolved
heterogeneity at all}, which makes \S\ref{sec:moderator}'s conditionality disclosure stronger
rather than weaker. \textbf{What is untouched} is \S\ref{sec:primary}: $\Dstat$'s sign is
20 / 20 on three endpoints and 19 / 20 on the fourth, every $\Dstat$, $\se$ and $t$ in
Table~\ref{tab:D} is a within-cell Welch quantity already corrected for its own degrees of
freedom, and none of them is a pooled quantity or a $\chi^2$ reading.

\section{Reproducibility}
```

**`paper/DRAFT-v4.md`** — OLD (line 2866, `count == 1`):

```markdown
of η (§4.5). We cannot report a selection-free estimate of anything and we do not claim one.

---

## 8. Reproducibility
```

NEW:

```markdown
of η (§4.5). We cannot report a selection-free estimate of anything and we do not claim one.

**T13 — The meta-analytic layer was referred to the wrong null, and this version carries the
correction rather than softening the claim.** Every Cochran Q in this paper weights cells by
w_i = se_i^-2, and every se_i is a Welch standard error built from two arms of three to six runs:
over §4.4's fourteen cells the Welch–Satterthwaite degrees of freedom run from **2.04 to 9.68,
median 2.91**. Q is therefore **not** χ²ₖ₋₁. Simulating this paper's own estimator under a
homogeneous truth — 20,000 draws through the same `welch()` and the same DerSimonian–Laird
`meta()`, `analysis/c99_qcalibration.py`, seed registered — gives a null Q on 13 df with **mean
26.9, median 21.4 and 95th percentile 62.4**, against χ²₁₃'s 13, 12.3 and 22.4. §3.3 already
conceded exactly this problem one layer down, for `t` at 2–4 df, and Welch-corrects every `t` in
the paper on that ground; **the concession was not carried into the Q layer until now, and that
inconsistency was ours.** Four consequences, stated here rather than left to be found.

1. **Every χ² p-value on this layer is anticonservative, some of them by many orders of
   magnitude.** Q = 102.47 is printed at p = 5.5e-16 and has Monte-Carlo p = 0.013 (0.002 under a
   common-sd null); between-base Q = 95.12 is printed at p = 1.7e-20 and has Monte-Carlo
   p = 0.005 (0.0007). Fourteen and seventeen orders of magnitude. Both p-values are now printed
   at every site that carries one.
2. **τ and I² are upper bounds**, because Eq. (12) subtracts k − 1 = 13 where the null mean of Q
   is 26.9. Recentred on the simulated null, τ = 0.295 → 0.271 pp and I² = 87% → 74% (0.280 pp
   and 79% under the common-sd null). We keep the standard estimator, which is what a reader will
   recompute, and label it.
3. **The pooled intervals undercover.** The eight-cell SGDm pool's ± 1.96 se interval covers 73%,
   not 95%; its calibrated 95% half-width is ± 0.121 pp against the ± 0.088 that its se implies.
   The fourteen-cell fixed-effect interval covers 65%, with a calibrated half-width of 0.089 pp
   against 0.058. **No sign, ordering or per-cell quantity in this paper depends on either**:
   nothing in Table 2 is pooled.
4. **One quantity moves the other way, and we report it for that reason.** §4.4's one-sided 95%
   Q-profile upper limit on the SGDm τ is 0.109 pp against χ²₇ and **0.097 pp** when the profile
   is simulated at each trial τ: there the χ² reference is conservative. A correction that only
   ever helped its authors would not be one.

**What survives, and it is the whole of the claim.** The decomposition is not deleted and does
not need to be. The heterogeneity resolves against its own simulated null (p = 0.013); the
base-optimiser structure is confirmed by a test that uses *no* standard errors at all — an exact
enumeration of all 45,045 partitions of the realised {8, 2, 2, 2} shape, η² = 0.840, rank 9,
p = 0.00020 — and that permutation, not the χ² p, is what §1.1's third contribution now rests on.
Every level remains homogeneous and by a wider margin than before: the calibrated p's are 0.70,
0.30, 0.25 and 0.86 where the χ² values were 0.68, 0.24, 0.20 and 0.76, and the registered
Q > 3.841 rule that §4.4 says the levels could have failed has a realised size of 0.10 rather
than 0.05 (size-0.05 critical value 6.22), so not firing it is stronger evidence than the rule
claimed. **What does not survive is the endpoint table's other three rows**: on the 20-epoch
column Q = 29.37 (χ² p 0.0058) has Monte-Carlo p 0.24, and on `final_test` Q = 39.91 (χ² p
1.4e−4) has Monte-Carlo p 0.16. **On a calibrated reference `plateau5` is the only endpoint of
the four with resolved heterogeneity at all**, which makes §4.4's conditionality disclosure
stronger rather than weaker. **What is untouched** is §4.3: D's sign is 20 / 20 on three
endpoints and 19 / 20 on the fourth, every D, se and t in Table 2 is a within-cell Welch quantity
already corrected for its own degrees of freedom, and none of them is a pooled quantity or a χ²
reading.

---

## 8. Reproducibility
```

---

## 6. Verification actually run

Nothing in §5 is proposed untested. All of the following was executed against copies of the live
files in a scratch tree; **no file in `paper/` was modified and nothing was committed.**

### 6.1 Anchor uniqueness — all 46 applied edits

Every OLD block was counted against the live `paper/paper.tex` and `paper/DRAFT-v4.md`:

```
tex  R1 … R19   OK  count=1   (23 anchors)
md   R1 … R19   OK  count=1   (23 anchors)
ANCHORS NOT UNIQUE: 0 of 46
```

The two `c98_reproduce.py` anchors in §4.2 were checked the same way (`count == 1` each).

### 6.2 `tectonic` — compiles, **zero new overfull boxes**

Baseline (`paper.tex` at HEAD) and the edited copy were compiled in identical scratch trees and
the warning lists diffed.

| | baseline | edited |
|---|---|---|
| exit status | 0 | **0** |
| pages | 65 | **68** (+3) |
| overfull `\hbox` | 3 | **3 — the same three, shifted** |

The three surviving overfull boxes are pre-existing (`946→1002`, `1005–1023→1061–1079`,
`3898–3904→4088–4094`; identical widths 7.28 pt, 20.28 pt, 12.25 pt).

**One new overfull box appeared on the first attempt and is already fixed in §5.** Adding the
`MC p` figures to §4.4's four-row level table pushed it 30.59 pt past `\linewidth` at `\small`.
Edit **R10h** therefore also changes that table's `\small` to `\footnotesize` — the size the
endpoint table two pages later already uses. With that change the table fits and the warning list
is identical to baseline. **The 9-column endpoint table (R14h) fits at `\footnotesize` with no
change**; it was checked, not assumed.

### 6.3 Abstract word count

218 → **227 words** (whitespace tokens inside `\begin{abstract}…\end{abstract}`), against the
230-word cap. **3 words of headroom**, and B5 frees 4 more if it lands.

### 6.4 The numeric diff between `paper.tex` and `DRAFT-v4.md` — **clean**

This is the defect class the project loses most cycles to, so it was run two ways over all 23 edit
pairs, after normalising the two markups' spellings of the same quantity
(`$5.5 \times 10^{-16}$` ≡ `5.5e−16`, `\chi^2_{13}` ≡ `χ²₁₃`, `45{,}045` ≡ `45,045`, `\eta^2` ≡ `η²`,
`\item` ≡ `1.`, en-dash ranges, and so on):

* **full-text**: the multiset of numerals in the NEW tex text vs the NEW md text.
* **added-numbers**: `nums(NEW) − nums(OLD)` in each file, which cancels the places where the two
  files' anchor spans differ.

```
edits compared: 23   edits failing BOTH comparisons: NONE
```

Every edit is clean on at least one comparison and the residuals on the other are all
anchor-span asymmetries (e.g. the md abstract anchor starts one clause earlier and so carries an
extra "50" from "ResNet-50"). `R14n` is the only edit that fails the added-numbers test, and it
does so correctly: the tex note *replaces* an existing note that already contained "13 df" and
"3 df", while the md had **no** such note and the whole thing is an insertion. Its full-text
comparison is exactly identical.

### 6.5 The audit

```
$ python3 analysis/c99_qcalibration.py
c99_qcalibration -- 14 cells, 20000 draws, seed 20260902
                    (fast estimator agrees with welch() to 1.4e-14)
   ... sections [1]-[7], 26 s
$ python3 analysis/c99_qcalibration.py --endpoints        # + section [8], 34 s

$ python3 analysis/c98_reproduce.py --calibration          # the new section, alone
[15b] Q CALIBRATION  (S3.3, S4.4, S7 T13, Fig. 2)
   ... 60 assertions ...
ALL 60 CHECKS PASS.
```

Full audit — **HEAD's own `c98_reproduce.py`** plus §4.2's section, against the **edited**
`DRAFT-v4.md` — reports `413` assertions of which **every pre-existing one still passes**; the
only failures are the four §3.4 census self-assertions, which are stale by construction because
this package adds both assertions and numerals (§7.2). HEAD unmodified, for comparison, is
`ALL 357 CHECKS PASS`, exit 0 (§7.1).

### 6.6 Monte-Carlo stability

Three seeds at the registered 20,000 draws, plus a 200,000-draw run at the registered seed:

| | seed 11111 | **seed 20260902 (registered)** | seed 987654321 | 200,000 draws |
|---|---|---|---|---|
| null *Q* mean / median / p95 | 26.70 / 21.41 / 61.85 | **26.92 / 21.41 / 62.36** | 27.09 / 21.76 / 62.60 | 26.86 / 21.49 / 62.38 |
| MC *p*(102.47) | 0.0109 | **0.0129** | 0.0124 | 0.0119 |
| MC *p*(95.12) | 0.0047 | **0.0054** | 0.0050 | 0.0048 |
| SGDm ±1.96 se coverage | 72.83 % | **72.99 %** | 73.16 % | 72.66 % |
| SGDm calibrated half-width | 0.1218 | **0.1207** | 0.1217 | 0.1213 |
| η², rank, exact *p* | 0.8396, 9, 0.000200 | **0.8396, 9, 0.000200** | 0.8396, 9, 0.000200 | (exact — no seed) |

Everything the paper prints is stable to its printed precision. §3.3's new paragraph states the
0.011–0.013 range in the manuscript rather than implying more precision than 20,000 draws buy.

---

## 7. Integrator notes

### 7.1 **The working tree is dirty — another package's `c98_reproduce.py` edits are already in it**

A run of `python3 analysis/c98_reproduce.py` **in the working tree right now** reports three
FAILs and exits 1. **That is not HEAD and it is not this package.** Checked properly:

```
$ git show HEAD:analysis/c98_reproduce.py > /tmp/head_c98.py   # 351d9a6, clean
$ python3 /tmp/head_c98.py --csv results/all_runs.csv --draft paper/DRAFT-v4.md ; echo $?
ALL 357 CHECKS PASS.
   chk() assertion sites executed in this run             353
   distinct quantity-numerals this run asserts            256
   coverage of distinct quantity-numerals                32.6%
0
```

**HEAD is green, exactly as the brief says, and §3.4's sentence is exactly right at HEAD.**

`git status` shows `M analysis/c98_reproduce.py` with **153 uncommitted insertions inside
`metricsens()`** — the `T_ARMS` / `T_METRIC` / `T_HZ3` block that applies §4.4's endpoint knife to
§4.7's prescription *T*. That is the **B8 / endpoint-knife** package, landed in the working tree
by a concurrent agent while this one was running. It adds `chk()` sites, which is why the census
self-check fires.

Two consequences for the integrator:

1. **Do not read a dirty-tree FAIL as a defect at HEAD.** Re-check with `git show HEAD:` before
   attributing one.
2. **The two `c98_reproduce.py` anchors in §4.2 were re-verified against the *dirty* tree as well
   as against HEAD and are `count == 1` in both.** B8's block sits inside `metricsens()`, well
   above the census marker this package inserts before, and it does not touch the `SECTIONS`
   line. The two packages compose without conflict.

### 7.2 The census fixpoint

`§3.4` in both files says:

> the audit executes **353 claim-carrying assertions covering 256 of the 786 distinct
> quantity-numerals** in this manuscript, which is 32.6 % of them.

With **this package alone** applied to a **clean HEAD** — HEAD's `c98_reproduce.py` plus §4.2's
section, and a `DRAFT-v4.md` carrying only §5's edits — `--census` reads:

```
  ...= QUANTITIES                                 2005  (821 distinct)
  chk() assertion sites executed in this run       413      (353 + this package's 60)
  distinct quantity-numerals this run asserts      294      (256 + 38)
  coverage of distinct quantity-numerals          35.8%
```

so the four numbers would become **413 / 294 / 821 / 35.8 %**. **Do not paste those.** Other packages
change the manuscript too, and the census counts numerals in the manuscript, so it must be run to
a **fixpoint after every package has landed**: update §3.4 in both files, re-run, update again if
it moved, repeat until `--census` reports zero FAILs. B7 is separately rewriting the sentence that
follows those numbers; the two edits are in the same paragraph and should be applied together.

### 7.3 Ordering against the other six items

* **B3, B4, B5, B6, B7** touch different text and do not collide with anything here. **B5 removes
  four words from the abstract**; this package adds nine. If both land, the abstract is 223 words.
  If B5 does not land it is 227, still under 230.
* **B8** (§4.7's prescription under the endpoint knife) is a *different* table and is untouched.
  Note that if B8 also adds an endpoint table it should use this package's MC-*p* convention.
* **B7** and this package both touch §3.4's paragraph — see §7.2.
* **Section numbering**: the new threat item is **T13**, appended after T12 in §7.2 in both files.
  If any other package adds a threat item this cycle, they must not both be T13.

### 7.4 Figure 2's own annotation (**optional, and NOT applied here**)

`analysis/c98_figures.py:396` draws, inside panel (b),

```python
    axR.annotate("p %.2f — the eight SGDm cells are\nhomogeneous, τ = %.3f"
                 % (chi2_sf(within, wdf), sub["SGDm"][4]), ...)
```

That prints the **χ² p of the four-level within Q (0.69)** next to text about the eight SGDm
cells, and it is now a χ² value whose calibrated companion is 0.86. Edit **R18** discloses this in
the caption ("every *p* drawn inside this figure … is a χ² value and is anticonservative"), which
is sufficient. If the integrator prefers to fix the figure itself, the minimal change is

```python
    axR.annotate("p %.2f (MC 0.86) — the eight SGDm cells are\nhomogeneous, τ = %.3f"
                 % (chi2_sf(within, wdf), sub["SGDm"][4]), ...)
```

and then `python3 analysis/c98_figures.py --fig f2`. **I have not made this change**:
`c98_figures.py` is not one of my files, other agents may be editing it, and regenerating the PDF
would race. If it is made, the "0.86" must come from `c99_qcalibration`, not be typed in.

### 7.5 What I created, and what I did not touch

**Created (in the working tree, uncommitted):**

* `analysis/c99_qcalibration.py` — 543 lines, new, no collision possible.
* `paper/sections/v6-calibration.md` — this file.

**Not touched, deliberately:** `paper/paper.tex`, `paper/DRAFT-v4.md`, `analysis/c98_reproduce.py`,
`analysis/c98_figures.py`, `results/all_runs.csv`, `docs/CORRECTIONS.md`. **No `git` command was
run.** The `paper.tex` / `DRAFT-v4.md` / `c98_reproduce.py` changes are supplied as replacement
text in §4.2 and §5 for the integrator to apply.

### 7.6 Two sentences the integrator should not soften

Neither of these is hedging, and both are load-bearing for the paper's rhetorical position:

1. §3.3's **"The inconsistency is ours, and we state it before a referee does."** The paper
   concedes the 2–4 df problem for *t* at `paper.tex:804–806` and Welch-corrects every *t*; it did
   not carry that concession into *Q*. Owning that in the same paragraph that makes the *t*
   concession is worth more than a silent repair, and it is the difference between a paper that
   audits itself and one that was audited.
2. §7 T13's **"A correction that only ever helped its authors would not be one."** The
   *Q*-profile τ limit tightening from 0.109 pp to 0.097 pp is the only calibrated quantity that
   moves in the paper's favour, and printing it is what makes the other thirteen credible.

### 7.7 The one thing this package deliberately does **not** do

It does not delete, weaken or re-scope the decomposition, and it does not switch the primary
endpoint. §4.4's central claim survives every attack in it:

* the heterogeneity resolves against its own simulated null, *p* = 0.013;
* the base-optimiser grouping is 9th of 45,045 partitions on a statistic that **uses no standard
  errors at all**, exact *p* = 0.00020;
* all four levels stay homogeneous, and by wider margins than χ² claimed;
* the sign result is 20/20 on three endpoints and 19/20 on the fourth, attrition inside the twenty
  cells is exactly zero, and **not one number in Table 2 is affected by any of this**.

What changes is that the paper now says which reference distribution each *p* was computed
against, and prints the one that means something beside the one that does not.
