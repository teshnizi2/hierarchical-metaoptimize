# v4 — PACKAGE `calibration`

**Closes B1, B2, B3, B4, B6; verifies B5 closed.**
Written against `paper/DRAFT-v3.md` at HEAD `6a374f4`, `results/all_runs.csv` = **2,173 rows,
1,724 admissible**. Every number below was re-derived at write time from the CSV and, where the
budget window is involved, from the raw per-epoch `.out` series under
`/Users/teshnizi/Saber Optimization/alice-backup/runs{,_alice2}`. Nothing here is quoted from prose,
from `docs/`, or from the briefing that commissioned this package.

`DRAFT-v3.md` was **not** edited by this package. Every change is given below as an exact
REPLACE/WITH pair keyed to the heading it lives under. Where a change has a dependency on another
package, it is marked **PAIRED EDIT** and the dependency is named.

---

## 0. Apply order and dependencies

| # | Item | Section touched | Depends on |
|---|---|---|---|
| 1 | B5 verification | — (no edit) | none |
| 2 | B1 — moderator claim | Abstract, §1.1 C3, §4.4 (+ Fig 2 caption), §9 | `analysis/c98_figures.py` CELLS patch (§2.7 below) |
| 3 | B2 — minimum interesting effect | §3.3 (new para), Abstract | none |
| 4 | B3 — practical significance | §4.7 (new para), Abstract scope (iv), §7 T4 | none |
| 5 | B4 — scorer exceptions | §3.4 (new para) | none |
| 6 | B6 — network list | Abstract | none |

Two edits below are **PAIRED**: they must be applied together with an edit another package owns, or
not at all. They are flagged in place, and §7 lists them again as cross-package notes.

---

## 1. B5 — VERIFIED CLOSED. Do not redo.

Checked at HEAD `6a374f4`:

```
$ wc -l results/all_runs.csv
    2174 results/all_runs.csv          # 2,173 data rows + 1 header
$ python3 -c "... csv.DictReader ..." → nrows 2173, admissible 1724
$ grep sm3 → 12 rows, all (base=AdamW, meta=Lion, meta_stepsize=1e-4)
```

`sm3`'s twelve rows record **`meta = Lion`** — the effective last-wins value from the runs' own
`ARGS` line, not the declared RMSProp — across all four arms (`chunk777`, `nodewise`,
`chunk2325`, `nodewise1d`), seeds 0–2, `ResNet18` / `CIFAR10` / 100 ep / `α₀ = 1e-3` /
box `−15:−2.3026`. `bm2` (12 rows: 6 SGD, 6 RMSProp, meta = Lion, seeds 3–5) and `sm4` (12 rows:
AdamW base, **meta = RMSProp**, seeds 0–2) are also present. **B5 is closed. No edit.**

One consequence of the ingest that the draft has not absorbed, and that this package's edits depend
on: `results/all_runs.csv` no longer holds 2,113 rows, so **every corpus count in the manuscript is
stale**. See §7.1.

---

## 2. B1 — the moderator claim

### 2.1 The objection is arithmetically correct as stated, and it is not the whole story

On the eleven-cell pool as published:

```
total    Q = 36.4048 on 10 df   (p 7.17e-05)   τ = 0.2033   rms measurement se 0.1520
  SGDm    k=8   pool +0.5556 ± 0.0448   Q = 4.2060 / 7
  SGD     k=1   pool +1.0353 ± 0.1085   Q = 0      / 0
  RMSProp k=1   pool +0.9733 ± 0.2515   Q = 0      / 0
  AdamW   k=1   pool +0.2787 ± 0.0873   Q = 0      / 0
  within  Q = 4.2060 / 7   between Q = 32.1988 / 3   share = 88.45%
```

Three levels carry `k = 1`, so their within-level Q is **zero by construction, not by
measurement**. Therefore

> Q_between ≡ Q_total − Q(the eight-cell group) = 36.4048 − 4.2060 = **32.1988**

for **any** four-way partition of those eleven cells that keeps those eight together and isolates
the other three, whatever the isolated cells are called. The statistic is a property of the
**grouping**, not of the **label**. The reviewer's arithmetic is exactly right.

What the reviewer's version omits is that the grouping itself is not arbitrary. Enumerating all
`C(11,8) = 165` partitions of shape `{8,1,1,1}`:

```
observed share 0.8845 — rank 2 of 165 → permutation p = 0.012
distribution: max 0.9094, p90 0.6659, median 0.1661, min 0.0023
```

So "88%" is not a number any relabelling could have produced; it is a number any *co-varying*
label could have produced. That distinction is the whole of B1: the eleven-cell decomposition
established that **some** property shared by `cc1, mm1, pp1, gn1(BN), rl3@1e-4, rl3@3e-4, fa1, hz3`
and not by `aw1, nl1(SGD), nl1(RMSProp)` accounts for 88% of the heterogeneity. It could not
establish that the property is the base optimiser.

### 2.2 The competing label, and why it was fatal before `bm2`

The obvious competitor is **batch identity** — the paper's own METHODS result makes BATCH a large
random effect (F(62,85) = 5.47, p 6.9e-13). On the eleven cells:

| partition | levels | between Q / df | within Q / df | share |
|---|---|---|---|---|
| base optimiser | 4 | 32.1988 / 3 | 4.2060 / 7 | 88.4% |
| batch / submission | 9 | 36.1468 / 8 (p 1.7e-05) | 0.2579 / 2 | **99.3%** |

Nested comparison against their common refinement (base × batch, 10 levels, within Q 0.2067 / 1):

```
adding batch GIVEN base  :  ΔQ = 3.9993 on 6 df   p 0.677
adding base  GIVEN batch :  ΔQ = 0.0513 on 1 df   p 0.821
```

**On the eleven cells the base optimiser adds essentially nothing beyond knowing which submission a
cell came from (ΔQ 0.05 on 1 df).** That is the honest statement of B1's severity, and it is
stronger than "the number is label-invariant": it names the specific rival label, and the rival wins.
This was unpublishable as "one identified moderator".

### 2.3 What `bm2` fixes — recomputed, not assumed

`bm2` is a second, independent submission at the SGD and RMSProp bases, fresh seeds 3–5, at `nl1`'s
own cell (ResNet-18 / CIFAR-10 / Lion meta / η 1e-4 / α₀ 1e-3 / 100 ep / box `−15:−2.3026`). Its two
cells are the byte-identical `nodewise → chunk777` contrast (m 14,420 vs 14,421) that defines the
pool, so they enter it on the pool's own stated rule. Re-derived from the CSV with the same
`arm`/`welch`/`meta` code path `analysis/c98_figures.py` uses:

```
bm2 (SGD)      3 v 3   D = +0.9780 ± 0.0858  (t 11.40)
bm2 (RMSProp)  3 v 3   D = +0.6313 ± 0.1492  (t  4.23)
```

These reproduce `analysis/c97_bm2_score.py`'s R1 readings to the digits the scorer prints. **The
scorer's own verdict is quoted, not paraphrased, in the §4.4 replacement below; this package did not
edit it and did not re-run it locally, because R0.5 measures box occupancy on `bm2`'s own probe
records and those probes are not in this repository** (running the scorer here without `--root`
correctly drops all four arms — see §7.4).

The thirteen-cell decomposition:

```
total    Q = 55.4021 on 12 df  (p 1.53e-07)   τ = 0.2307   rms measurement se 0.1477
  SGDm    k=8   pool +0.5556 ± 0.0448   Q = 4.2060 / 7  (p 0.756)   τ 0.0000
  SGD     k=2   pool +1.0001 ± 0.0673   Q = 0.1718 / 1  (p 0.679)   τ 0.0000
  RMSProp k=2   pool +0.7204 ± 0.1283   Q = 1.3681 / 1  (p 0.242)   τ 0.1254
  AdamW   k=1   pool +0.2787 ± 0.0873   Q = 0      / 0
  within  Q = 5.7459 / 9 (p 0.765)   between Q = 49.6562 / 3 (p 9.46e-11)   share = 89.63%
```

Three things change, and only three:

1. **Two of the three singleton levels stop being singletons.** 1.5399 of the 5.7459 within-level Q
   now comes, on 2 df, from levels that had none. Those two df are a real test — the SGD level would
   have failed it at Q > 3.841 and did not (0.1718), and so would RMSProp (1.3681). The
   scorer's registered R2 line is `Q ≤ 3.841 → REPLICATED`; both levels replicate.
2. **The rival label loses its edge.** On thirteen cells, batch (10 levels) gives between Q
   51.0874 / 9 = 92.2%, still numerically above base's 89.6%. But nested against base × batch
   (12 levels, within Q 0.2067 / 1):

   ```
   adding batch GIVEN base  :  ΔQ = 5.5392 on 8 df   p 0.699    ← batch adds nothing
   adding base  GIVEN batch :  ΔQ = 4.1080 on 2 df   p 0.128    ← base adds something, unresolved
   ```

   The second line was ΔQ 0.0513 on 1 df (p 0.821) before `bm2`. So `bm2` moves "base is
   indistinguishable from batch" to "base is the parsimonious description — four levels lose
   nothing against ten — but base is still not *separated* from batch at p < 0.05."
3. **The moderator makes, and survives, its first out-of-sample test.** `nl1` predicted the two
   `bm2` cells at +1.0353 and +0.9733; the corpus mean predicted both at +0.5707.

   ```
   SGD      predicted +1.0353   observed +0.9780   error −0.0573 (se 0.1383, z −0.41)
   RMSProp  predicted +0.9733   observed +0.6313   error −0.3420 (se 0.2924, z −1.17)
   RMSE, base-level predictor  0.2452 pp
   RMSE, grand-mean predictor  0.2911 pp   → 29% of squared prediction error removed, on n = 2
   ```

   Neither error is resolved, and on RMSProp alone the grand mean predicts *better* (+0.0606 against
   −0.3420). This is a two-point test and must be written as one.

Robustness of the share: leave-one-cell-out over the thirteen gives **84.0% – 94.3%**.
Permutation context: over all **19,305** partitions of the thirteen cells with the realised shape
`{8,2,2,1}`, the base partition ranks **29th → p = 0.0015** (max 0.9509, median 0.3075).

### 2.4 What `bm2` does **not** fix

* **AdamW is still a singleton in the pool.** Its level contributes Q = 0 on 0 df, so 89.63% is
  still partly an arithmetic identity — just a smaller part of one than 88.45% was.
* **Base is still not separated from batch** (ΔQ 4.1080 on 2 df, p 0.128). The claim "one
  *identified* moderator" is not yet earned. "Identified" would require that the label beat the
  nuisance variable it co-varies with; it does not, at p < 0.05.
* **The direction is still a prediction, not a result.** On thirteen cells the 2 × 2 in the base's
  own state now reads

  ```
  momentum main effect       −0.4431 ± 0.0875 (z −5.06)
  second-moment main effect  −0.2783 ± 0.0875 (z −3.18)
  interaction                +0.0027 ± 0.1750 (z +0.02)
  ```

  (11-cell reading was −0.5872 ± 0.1455, −0.1695 ± 0.1455, +0.2146 ± 0.2910.) The second-moment
  main effect has become *resolved*, which the eleven-cell text explicitly said it was not. This does
  **not** contradict §5.5 — the direct RMSProp-vs-AdamW contrast is +0.4417 ± 0.1552 (z 2.85), so two
  bases that both carry a second moment still differ, and a second moment is not the axis — but the
  sentence "consistent with §5.5, which kills second-moment normalisation as the axis" can no longer
  be written without that qualification. It is rewritten below.
* **Collapsing to momentum present/absent still fails**: momentum-present k=9 pools +0.4979 ± 0.0399
  with Q 12.1680 on 8 df (p 0.144), i.e. the SGDm-to-AdamW gap survives the collapse. Reason 4 of the
  four reservations stands unchanged.

### 2.5 Two further cells exist and are deliberately **not** pooled

* **`sm4`** (AdamW base, **RMSProp meta**, seeds 0–2) is a count-matched cell at
  D = +0.8893 ± 0.2285. It is excluded from the base pool because the pool is defined by a
  byte-identical contrast object at a **Lion** meta-optimiser, and `sm4` is the corpus's only
  non-Lion partition cell. Pooling it would silently convert a base-optimiser decomposition into a
  base × meta one. `analysis/c97_sm4_score.py`'s own scope note forbids pooling it with `aw1` or
  `sm3` in any case.
* **`sm3`** (AdamW base, Lion meta, seeds 0–2) is at the pool's exact cell and reads
  D = +0.1413 ± 0.0638 (t 2.22). Adding it as a fourteenth cell gives AdamW a two-batch level
  (+0.1891 ± 0.0515, Q 1.6128 on 1 df, p 0.204 → replicates) and raises the share to **92.82%**
  (total Q 102.4739 / 13, between 95.1152 / 3, within 7.3587 / 10). **We report this as a
  sensitivity and not as the primary**, because `sm3` is one of the five batches §3.4 names as having
  no scorer registered before its runs existed — its own registration scored the RMSProp-meta
  experiment it did not run. The draft's stated reason for excluding `sm3` ("a number that is not in
  the deposited run table cannot be re-derived by a reader running `make reproduce`") is **false at
  HEAD** and must be replaced by the registration reason; the replacement text below does that.

### 2.6 REPLACEMENT TEXT

---

#### EDIT B1-a — **Abstract**, the moderator sentence

**REPLACE** (under `## Abstract`, in the paragraph beginning `**The measurement.**`):

```
+1.485 ± 0.238. Over the eleven cells that run the same ResNet-18 partition contrast, D varies
genuinely across configurations (**Q = 36.4 on 10 df, p = 7.2e-5**, τ = 0.203 pp against 0.152 pp
rms measurement error) — and **88% of that variation is one identified moderator, the base
optimiser** (between-base Q = 32.2 on 3 df, p = 4.8e-7). At a fixed base the effect is homogeneous:
over eight SGDm cells spanning seven separate submissions, two meta-stepsizes, two budgets and three
step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76, τ = 0.000).
```

**WITH:**

```
+1.485 ± 0.238. Over the thirteen ResNet-18 cells that run the same partition contrast — the eleven
of Table 2 plus the two of the replication batch `bm2` — D varies genuinely across configurations
(**Q = 55.40 on 12 df, p = 1.5e-7**, τ = 0.231 pp against 0.148 pp rms measurement error). Splitting
them by base optimiser leaves them **homogeneous inside every level** (within Q = 5.75 on 9 df,
p = 0.77) and accounts for **89.6% of that Q** (between-base Q = 49.66 on 3 df, p = 9.5e-11); over
eight SGDm cells spanning seven separate submissions, two meta-stepsizes, two budgets and three
step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76, τ = 0.000).
**We do not claim the base optimiser is identified.** The share is a property of the grouping and
not of the label: any covariate inducing the same grouping earns the same 89.6%, and the obvious
rival — batch identity, which this paper's own methods make a large random effect — accounts for
92.2%. What the base optimiser has that a relabelling does not is that dropping it from the
batch partition still costs ΔQ = 4.11 on 2 df (p = 0.13) while adding batch on top of it costs
nothing (ΔQ = 5.54 on 8 df, p = 0.70), that three of its four levels now rest on two independent
batches each and passed a within-level replication test that could have failed, and that it
predicted `bm2`'s two new cells with 29% less squared error than the corpus mean — on two points.
**The defensible claim is that the base optimiser is the coarsest partition of these thirteen cells
that leaves them internally homogeneous, not that it is the cause of their heterogeneity.**
```

*Re-derivation.* 13-cell pool +0.6345 ± 0.0331; Q 55.4021/12 (p 1.533e-07); τ 0.2307; rms
measurement se 0.1477; within 5.7459/9 (p 0.7651); between 49.6562/3 (p 9.456e-11); share 89.63%.
Batch partition (10 levels): between 51.0874/9 (p 6.72e-08) = 92.2%. Nested against base × batch
(12 levels, within 0.2067/1): ΔQ(batch | base) 5.5392/8 p 0.6987; ΔQ(base | batch) 4.1080/2
p 0.1282. Out-of-sample RMSE 0.2452 vs 0.2911 → 1 − 0.2452²/0.2911² = 0.291.

---

#### EDIT B1-b — **§1.1 Contributions**, item 3

**REPLACE:**

```
3. **An identified moderator for the effect's heterogeneity**: the base optimiser carries 88% of
   the between-cell Cochran Q, and inside a fixed base D is homogeneous (τ = 0.000, 95% upper limit
   0.109 pp) across seven submissions, two meta-stepsizes, two budgets and three clip boxes
   (§4.4, Figure 2).
```

**WITH:**

```
3. **A candidate moderator for the effect's heterogeneity, with its confound measured rather than
   asserted**: over thirteen same-contrast ResNet-18 cells the base optimiser is the coarsest
   partition that leaves them internally homogeneous (within Q 5.75 on 9 df, p 0.77) and it accounts
   for 89.6% of the between-cell Cochran Q; inside the SGDm level D is homogeneous (τ = 0.000, 95%
   upper limit 0.109 pp) across seven submissions, two meta-stepsizes, two budgets and three clip
   boxes. Three of the four levels now carry two independent batches each, and a registered
   replication (`bm2`) confirmed both formerly single-batch levels (Q 0.17 and 1.37, each on 1 df).
   **We report, in the same place, that this is not yet identification**: the share is invariant to
   any relabelling that induces the same grouping, batch identity accounts for 92.2%, and base
   survives conditioning on batch only at ΔQ 4.11 on 2 df, p 0.13 (§4.4, Figure 2).
```

---

#### EDIT B1-c — **§4.4**, heading and the whole opening through the four reservations

**REPLACE the heading:**

```
### 4.4 The heterogeneity is one identified moderator: the base optimiser
```

**WITH:**

```
### 4.4 The heterogeneity has a candidate moderator, the base optimiser — and a rival we can measure but not exclude
```

**REPLACE**, from `Restrict Table 2 to the eleven cells` down to and including the sentence
`**Between base optimisers, Q = 32.20 on 3 df (p = 4.8e-7) — 88% of the total.** The remaining 12%
is the within-SGDm residual, and it is not resolvable at all:`

**WITH:**

```
Restrict the corpus to the cells that run the same ResNet-18 partition contrast (`nodewise` →
`chunk777`, count-matched to +1 group on 14,420) so that the contrast itself is held fixed. There
are thirteen: the eleven of Table 2 (rows 1–4 and 6–12) and the two produced by `bm2`, the
registered replication batch of §3.5, which ran that same contrast at the SGD and RMSProp bases on
fresh seeds 3–5. Those thirteen are heterogeneous: the fixed-effect pool is +0.635 ± 0.033 with

> **Q = 55.40 on 12 df, p = 1.5e-7**; DerSimonian–Laird **τ = 0.231 pp** against an rms measurement
> se of **0.148 pp**.

`bm2`'s two cells are quoted from its registered scorer, `analysis/c97_bm2_score.py`, run unedited
on the cluster where its probe records live (RULE 16; the box gate R0.5 is measured on `bm2`'s own
twelve probe dirs, T = 10,000 records, all rails 0.0000):

> `D'_SGD = +0.9780 ± 0.0858, t 11.40` → **REPLICATES** (`nl1` read +1.0353; |Δ| 0.057, inside the
> registered ±0.50 cross-batch offset band). `D'_RMS = +0.6313 ± 0.1492, t 4.23` → **REPLICATES**
> (`nl1` read +0.9733; |Δ| 0.342, inside the band). R2, the two-batch moderator levels:
> **SGD +1.0000 ± 0.0673, between-batch Q 0.172 on 1 df → REPLICATED**; **RMSProp +0.7204 ± 0.1283,
> Q 1.367 on 1 df → REPLICATED.** R3, the within-batch base contrast, `dD' = +0.3467 ± 0.1721,
> t 2.01` → **"SGD AND RMSProp AGREE WITHIN RESOLUTION"**, which the scorer's own R3 text forbids
> being written as "identical".

Split the thirteen by the base optimiser, the axis §5.5 was already looking at:

| base optimiser | base state, from the runs' own `ARGS` line | cells | batches | pooled D (pp) | within Q / df |
|---|---|---|---|---|---|
| SGD | no momentum, no second moment | 2 | 2 | **+1.000 ± 0.067** | 0.17 / 1 |
| RMSProp | second moment 0.999, no momentum | 2 | 2 | **+0.720 ± 0.128** | 1.37 / 1 |
| SGDm | momentum 0.99, no second moment | 8 | 7 | **+0.556 ± 0.045** | 4.21 / 7 |
| AdamW | momentum 0.9 + second moment 0.999 | 1 | 1 | **+0.279 ± 0.087** | — |

**Between base optimisers, Q = 49.66 on 3 df (p = 9.5e-11) — 89.6% of the total; within levels,
Q = 5.75 on 9 df (p = 0.77).** Before stating what that does and does not license, we state the
arithmetic that limits it, because a referee will find it otherwise.

**The share is a property of the grouping, not of the label.** A level with one cell contributes
Q = 0 by construction. In the eleven-cell pool of the previous draft, *three* of the four levels
were singletons, so Q_between was identically Q_total minus the eight-cell SGDm Q —
36.4048 − 4.2060 = 32.1988 — for **any** partition isolating those three cells, whatever it called
them. The grouping itself was not arbitrary (over all 165 partitions of shape {8,1,1,1} the observed
one ranked 2nd, permutation p = 0.012), but the *label* was untested at three of four levels.
`bm2` removes two of the three singletons: 1.54 of the present 5.75 within-level Q now sits, on
2 df, in levels that previously had none, and those 2 df were a test the label could have failed —
the scorer's registered line is Q > 3.841 → the level is not a stable quantity — and did not. Over
all 19,305 partitions of the thirteen cells with the realised shape {8,2,2,1}, the base-optimiser
partition ranks 29th (p = 0.0015). One singleton, AdamW, remains.

**The rival label, measured.** The variable most likely to induce this grouping by accident is
batch identity, which this paper's own methods section makes a large random effect
(F(62,85) = 5.47, p 6.9e-13). Partitioning the thirteen cells by submission gives ten levels,
between Q = 51.09 on 9 df — **92.2%, more than the base optimiser's 89.6%**. Nesting both inside
their common refinement (base × batch, twelve levels, within Q = 0.21 on 1 df) separates them:

> Adding **batch given base** costs **ΔQ = 5.54 on 8 df, p = 0.70** — once you know the base
> optimiser, which submission a cell came from explains nothing further. Adding **base given batch**
> costs **ΔQ = 4.11 on 2 df, p = 0.13** — knowing the base optimiser does add something beyond
> submission identity, but not at p < 0.05.

On the eleven-cell pool the second of those two numbers was **ΔQ = 0.05 on 1 df, p = 0.82**: base
added nothing whatsoever beyond batch. That is what `bm2` bought, and it is a smaller purchase than
"the moderator is now replicated" would suggest. **The base optimiser is the parsimonious
description of these thirteen cells — four levels lose nothing against ten — and it is not yet
separated from the nuisance variable it co-varies with.** We therefore write "candidate moderator",
not "identified moderator", and we do not write that the base optimiser *carries* or *explains* the
heterogeneity.

**The one out-of-sample test that exists.** `bm2` is the first occasion on which the moderator made
a prediction before the data existed. `nl1`'s levels predicted +1.0353 (SGD) and +0.9733 (RMSProp);
the corpus mean predicted +0.5707 for both. Observed: +0.9780 and +0.6313, prediction errors −0.057
(z −0.41) and −0.342 (z −1.17). The base-level predictor's RMSE is 0.245 pp against the grand
mean's 0.291 pp — **29% of the squared prediction error removed, on two points**, and on RMSProp
alone the grand mean was the better predictor. This is offered as the direction the evidence points,
not as a validated rule; §5.8's out-of-sample null, whose unit is the design point and whose
predictors are continuous, is unaffected.

The remaining within-level residual is not resolvable at all:
```

**REPLACE** the paragraph beginning `**These eleven cells are not one configuration, and we do not
call them one.**`, in full, **WITH:**

```
**These thirteen cells are not one configuration, and we do not call them one.** They span three
step-size clip boxes — `−15:−2.3026` (9 cells), `−30:9.0` (3), `−25:−2.3026` (1) — and
`analysis/c87_rl3_score.py`'s registered header forbids pooling across boxes, on the ground that a
box change moves the optimiser and not merely the instrument. We pool anyway; §3.4 lists this as one
of the paper's three departures from a registered scorer. **The measurement that justifies it is
weaker here than it was on eleven cells, and we report the weakening rather than the number that
flatters us.** On the eleven-cell pool, partitioning Q by box gave between-box Q = 1.08 on 2 df
(p = 0.58) against within-box Q = 35.32 on 8 df. On thirteen it gives **between-box Q = 5.14 on 2 df
(p = 0.077)** — not because the box has started to matter, but because `bm2`'s two cells both sit in
`−15:−2.3026`, so that box now contains all four non-SGDm cells and the box axis has become partly
confounded with the axis under study. The test that is not confounded is the one taken inside a
single base: over the eight SGDm cells, which between them span all three boxes, between-box Q is
**0.76 on 2 df, p = 0.68**, with pools +0.582 ± 0.080 (`−15`), +0.629 ± 0.123 (`−25`) and
+0.523 ± 0.060 (`−30`). **That** is what the pooling rests on. A `β-box` column is carried in
Table 2 and in Appendix B so the reader can redo either split.
```

**REPLACE** the block beginning `So the finding is not "D varies for reasons we cannot attribute".`
together with the indented summary that follows it, **WITH:**

```
So the finding is not "D varies for reasons we cannot attribute", and it is not "one identified
moderator" either. It is:

> **Inside a base optimiser, D does not move.** Under SGDm it is +0.556 ± 0.045 pp across seven
> submissions, two meta-stepsizes, two budgets, three β-boxes and two clusters (Q 4.21 / 7,
> τ = 0.000); under SGD it is +1.000 ± 0.067 and under RMSProp +0.720 ± 0.128, each across two
> independent submissions (Q 0.17 and Q 1.37, each on 1 df). **Between base optimisers the pooled
> level moves by a factor of 3.6**, and a four-way split on that axis leaves the thirteen cells
> internally homogeneous while accounting for 89.6% of their Cochran Q. **What we cannot say is that
> the base optimiser is the cause.** The same 89.6% would be earned by any covariate inducing the
> same grouping; the grouping's chief rival, batch identity, accounts for 92.2%; and conditioning
> one on the other leaves base adding ΔQ 4.11 on 2 df, p 0.13 — real, and not resolved.
```

**REPLACE** the paragraph beginning `**Say which denominator.**` **WITH:**

```
**Say which denominator.** The between-base Q of 49.66 is 89.6% of the thirteen-cell Q of 55.40,
which is the pool the decomposition is computed on. On the eleven-cell pool of the previous draft
the corresponding figures were 32.20 of 36.40 = 88.4%; against the legacy twelve-cell Q of 43.19 —
the pool that contained the withdrawn GroupNorm cell — the same 32.20 was 74.6%. All three are true
of different pools, and a share quoted without its denominator is not a number. Leave-one-cell-out
over the thirteen gives 84.0% to 94.3%.
```

**REPLACE** the block beginning `**What we may not conclude from the direction.**` down to the end
of numbered reservation 4, **WITH:**

```
**What we may not conclude from the direction.** The four levels happen to arrange themselves as a
2 × 2 in the base optimiser's own state: the two levels whose base carries **no momentum term**
(SGD, RMSProp) sit at +1.000 and +0.720, and the two that carry one (SGDm, AdamW) sit at +0.556 and
+0.279. As contrasts on the thirteen-cell pools, a momentum main effect of **−0.443 ± 0.088
(z −5.06)**, a second-moment main effect of **−0.278 ± 0.088 (z −3.18)**, and an interaction of
**+0.003 ± 0.175** that is indistinguishable from zero. Two of these three readings changed when
`bm2` entered: the eleven-cell pool gave −0.587 ± 0.146, −0.169 ± 0.146 and +0.215 ± 0.291, i.e. an
unresolved second-moment effect and an unresolved interaction. **The second-moment main effect is
now resolved, and the previous draft's sentence that this reading is "consistent with §5.5, which
kills second-moment normalisation as the axis" is withdrawn as written.** What §5.5 refutes is that
the second moment is *the* axis, and that survives: the direct RMSProp-versus-AdamW contrast, two
bases that both carry one, is +0.442 ± 0.155 (z 2.85). What is no longer supportable is the stronger
reading that the second moment does not move D at all. `sm4` (§3.5, R4) points the same way from the
other side: at the corner where a second-moment normaliser sits in **both** base and meta, D is
+0.889 ± 0.229, the largest value in the AdamW family, so "a second moment shrinks D wherever it
sits" is false.

**We register the 2 × 2 as a prediction, not a result**, for four reasons, and a referee should
hold us to all four:

1. **One of the four levels still rests on one cell.** AdamW contributes Q = 0 on 0 df, so its
   position in the 2 × 2 is untested by any within-level comparison. SGD, RMSProp and SGDm now carry
   two, two and seven batches respectively.
2. **The base optimiser is not separated from batch identity.** ΔQ = 4.11 on 2 df, p = 0.13. `bm2`
   broke the `nl1` co-dependence — SGD and RMSProp are no longer two halves of a single submission —
   which is why this number is 4.11 and not the 0.05 it was; it did not finish the job.
3. **The momentum coefficients are not matched** (0.99 under SGDm, 0.9 under AdamW), so "momentum
   present/absent" is a two-point contrast in a continuous parameter.
4. **Momentum alone is not sufficient.** Collapsing the four levels to momentum-present /
   momentum-absent leaves a residual Q of 12.17 on 8 df (p 0.14) inside the momentum-present group —
   the SGDm-to-AdamW gap survives the collapse. The candidate moderator is *the base optimiser*, not
   any single component of it.
```

**REPLACE** the paragraph beginning `**R3 (`bm2`, §3.5) is exactly the experiment this weakness
names**` **WITH:**

```
**`bm2` (R3, §3.5) was exactly the experiment this weakness named, and it has now been scored.** It
delivered two of the three repairs it was designed for: it resampled the batch random effect at the
SGD and RMSProp levels, and it broke the `nl1` co-dependence under which a batch × partition
interaction peculiar to one submission would have moved both levels together with nothing in the
corpus able to see it. It did not deliver the third: the base optimiser is still not separated from
batch identity (ΔQ 4.11 on 2 df, p 0.13), and AdamW is still a single cell in this pool. So "the
base optimiser is a moderator of D" remains a within-corpus decomposition of thirteen measurements
with one two-point out-of-sample check attached, **not an out-of-sample prediction rule** — which is
why it does not contradict §5.8, where the predictors under test are continuous properties of a
configuration and the unit is the design point. It should also be read against §3.4: `nl1` is one of
the five batches with no scorer registered before its runs existed, and it still supplies half of
the SGD and RMSProp levels; `bm2`, which supplies the other half, was registered before any of its
runs could exist.
```

**REPLACE** the final paragraph of §4.4, beginning `A second AdamW measurement exists but is not in
the pool:` **WITH:**

```
A second AdamW measurement exists and is still not in the pool, but the reason has changed. `sm3`
(§6.1) is void as designed and salvageable only as an independent replicate of `aw1`; **its twelve
runs are now in the run table** (they were not when the previous draft was written), and re-derived
from it they read D = +0.1413 ± 0.0638 against `aw1`'s +0.2787 ± 0.0873, a replicate spread of
+0.1374 ± 0.1081 (z 1.27). Entering it as a fourteenth cell would give AdamW a two-batch level
(+0.1891 ± 0.0515, between-batch Q 1.61 on 1 df, p 0.20 → replicates), remove the last singleton and
raise the explained share to 92.8% of a total Q of 102.47 on 13 df. **We report that as a
sensitivity and keep it out of the primary decomposition**, because `sm3` is one of the five batches
§3.4 names as having no scorer registered before its runs existed: the registration that exists
scored the RMSProp-meta experiment `sm3` did not run. The previous draft gave a different reason —
that `sm3` was not in the deposited run table — and that reason is no longer true.

A fifteenth same-contrast cell also exists and is excluded on a different ground: `sm4`
(AdamW base, **RMSProp meta**, D = +0.8893 ± 0.2285) is the corpus's only partition cell with a
non-Lion meta-optimiser. This pool is defined by a byte-identical contrast object at a Lion meta,
and pooling `sm4` into it would silently convert a base-optimiser decomposition into a base × meta
one; `analysis/c97_sm4_score.py`'s own scope note forbids pooling it with `aw1` or `sm3`. It is
reported in §4.3 and in the scope discussion, not here.
```

**REPLACE** the Figure 2 caption **WITH** (**PAIRED EDIT** — requires the `c98_figures.py` patch of
§2.7 and a regenerated figure; do not apply the caption without regenerating the figure):

```
**Figure 2 — the heterogeneity in D has a base-optimiser structure, and a rival we can measure.**
(a) The thirteen same-contrast ResNet-18 cells, grouped by base optimiser; each group's band is its
own inverse-variance pool ± 1.96 se. Three of the four levels now carry two or more independent
submissions: the eight SGDm cells are **homogeneous** (Q 4.21 on 7 df, p 0.76, τ = 0.000, pool
+0.556 ± 0.045), and the two levels `bm2` replicated are homogeneous across batches (SGD Q 0.17,
RMSProp Q 1.37, each on 1 df). AdamW is still one cell. (b) Partitioning the thirteen-cell Cochran Q
(Eq. 12): **49.66 of 55.40 (89.6%) is between base optimisers**, on 3 df, p 9.5e-11, leaving
5.75 on 9 df within. The share is a property of the grouping and not of the label — batch identity,
on ten levels, accounts for 92.2% — so the panel is captioned as a decomposition and not as an
attribution; the conditional test that distinguishes them (ΔQ 4.11 on 2 df, p 0.13) is in the text.
```

---

#### EDIT B1-d — **§9 Conclusion**

**REPLACE:**

```
and its variation across configurations is dominated by one identified moderator — the base
optimiser carries 88% of the between-cell heterogeneity (Q 32.2 / 3 df), and inside a fixed base
the effect is homogeneous (Q 4.21 / 7 df, p 0.76, τ 0.000, pool +0.556 ± 0.045).
```

**WITH:**

```
and its variation across configurations has a candidate moderator that we can decompose but not
identify — splitting the thirteen same-contrast ResNet-18 cells by base optimiser leaves them
homogeneous inside every level (Q 5.75 / 9 df, p 0.77) and accounts for 89.6% of the between-cell
heterogeneity (Q 49.66 / 3 df), and inside the SGDm level the effect is homogeneous
(Q 4.21 / 7 df, p 0.76, τ 0.000, pool +0.556 ± 0.045). That share is a property of the grouping
rather than of the label: batch identity accounts for 92.2% of the same Q, and the base optimiser
survives conditioning on it only at ΔQ 4.11 on 2 df, p 0.13. A registered replication (`bm2`)
gave the SGD and RMSProp levels a second independent batch each and both replicated, which moved
that conditional test from ΔQ 0.05 on 1 df to ΔQ 4.11 on 2 df; it did not finish it.
```

**REPLACE** (the "honest description" sentence):

```
measurement; an identified moderator for its heterogeneity that is not yet replicated at three of
its four levels; a single-batch bounded null that excludes the mechanism most people would guess as
```

**WITH:**

```
measurement; a candidate moderator for its heterogeneity, replicated at three of its four levels and
still not separated from the batch identity it co-varies with; a single-batch bounded null that
excludes the mechanism most people would guess as
```

**REPLACE** (in the "experiments that would break the impasse" paragraph):

```
**The experiments that would break the impasse**, in the order we would run them. Three are in
flight and are described with their decision rules in §3.5: the alignment replication with the
permutation seed decoupled (R1), the box- and hardware-matched budget trio (R2), and the
base-moderator replication at fresh seeds (R3). A fourth, R4, tests the one untested corner of the
base × meta grid that §6.1's void batch failed to reach.
```

**WITH:**

```
**The experiments that would break the impasse**, in the order we would run them. Two of the four
registered in §3.5 have landed and are reported above: the base-moderator replication at fresh
seeds (R3, `bm2`) and the second-moment corner that §6.1's void batch failed to reach (R4, `sm4`).
Two remain in flight, with their decision rules on the record: the alignment replication with the
permutation seed decoupled (R1, `rp1`) and the box- and hardware-matched budget trio (R2). The
experiment that would convert the base optimiser from a candidate moderator into an identified one
is not among them: it is a **second independent batch at the AdamW level**, which is the one level
still resting on a single cell, run at fresh seeds under the same registration discipline as `bm2`.
Twelve jobs. Until it exists, the base optimiser and the submission it arrived in cannot be told
apart at p < 0.05.
```

### 2.7 PAIRED EDIT — `analysis/c98_figures.py`

Figure 2 and the `--numbers` printout are generated from a hard-coded `CELLS` list that predates the
ingest. §4.4's replacement text and the Figure 2 caption above require two entries to be added and
`POOL12` widened. **This package did not make the edit** (another package is in the same file). The
exact patch:

```python
# add to CELLS, after the ("nl1 (RMSProp)", ...) entry:
 ("bm2 (SGD)","ResNet-18",     "C10",  "SGD",     "1e-4", 100,
  ("bm2-sgd-ch","chunk777"), ("bm2-sgd-node","nodewise"), None, None),
 ("bm2 (RMSProp)","ResNet-18", "C10",  "RMSProp", "1e-4", 100,
  ("bm2-rms-ch","chunk777"), ("bm2-rms-node","nodewise"), None, None),

# and widen the same-contrast pool:
POOL12 = {"cc1","mm1","pp1","gn1 (BN)","rl3 @1e-4","rl3 @3e-4","fa1","hz3",
          "gn1 (GN)","aw1","nl1 (SGD)","nl1 (RMSProp)",
          "bm2 (SGD)","bm2 (RMSProp)"}
```

After the patch, `python3 analysis/c98_figures.py --all --numbers` must print, under `== F2 ==`:
`byte-identical pool over 13 cells: +0.635 ± 0.033  Q 55.40 / 12  tau 0.231`, the four level lines
of the table above, and `base explains 89.6% of the 13-cell Q`. If it prints anything else, **do not
apply the §4.4 or Figure 2 text.**

---

## 3. B2 — a minimum interesting effect for the corpus headline

### 3.1 What is actually registered, re-derived from the scorers

The corpus has carried one interesting-effect band, unchanged, since `mm1`. Read out of the scorer
sources, not out of prose:

| scorer | constant | value |
|---|---|---|
| `c76_mm1_score.py` | `M1_REFUTE_AT` / `M1_CONFIRM_AT` | 0.15 / 0.30 |
| `c77_pp1_score.py` | `P2_NULL` / `P2_STRONG` | 0.15 / 0.30 |
| `c78_bn1_score.py` | T1 five-way band | ±0.15 / ±0.30 |
| `c79_ar1_score.py` | A1 five-way band | ±0.15 / ±0.30 |
| `c81_cc1_score.py` | `NULL_HALF` / `DECIDE` | 0.15 / 0.30 |
| `c84_gn1_score.py` | T2 | 0.15 / 0.30 |
| `c88_scorers.py` | `_aw1_rule` | 0.15 / 0.30 |
| `c97_bm2_score.py` | `NULL_HALF` / `DECIDE` | 0.15 / 0.30 (`# unchanged from cc1/gn1/aw1`) |

Eight registered scorers, one band. **0.30 pp is this campaign's minimum interesting effect and it
was fixed before any of the data it now judges existed.** Two variants of the rule are in use and
must not be conflated: `mm1`/`pp1`/`bn1`/`ar1`/`cc1`/`gn1`/`bm2` apply it to the **point estimate**
(with a t or se side condition); `aw1` applies it to the **95% interval** (`lo > 0.30` → TRANSFERS).

### 3.2 What it does and does not license for the pooled headline

`+0.556 ± 0.045` is an eight-cell inverse-variance pool. **No scorer ever registered a bar for a
pooled quantity**, and retro-fitting one to a pool because the per-cell bar happens to clear is
exactly the move §3.4 exists to prohibit. So the headline is reported as an **estimate**, and the
0.30 line is reported as **context with its provenance and its unit named**. Both readings, computed:

```
point-estimate rule (mm1 family):   +0.5556 > 0.30                    clears
interval rule (aw1 family):         lower 95% limit +0.4678 > 0.30    clears
per cell, interval rule, 8 SGDm cells:
  rl3 @3e-4 +0.4037 CLEARS   fa1       +0.3879 CLEARS
  rl3 @1e-4 +0.3417 CLEARS   cc1       +0.3345 CLEARS
  pp1       +0.3036 CLEARS   gn1 (BN)  +0.2867 does not
  hz3       +0.2581 does not mm1       +0.1692 does not
  → 5 of 8 clear individually; 8 of 8 clear on the point estimate (min +0.428)
13-cell pool +0.6345 ± 0.0331, lower 95% limit +0.5695
```

### 3.3 REPLACEMENT TEXT

---

#### EDIT B2-a — **§3.3**, new paragraph, to be inserted immediately before the subsection's closing
paragraph (alongside the multiplicity and units-of-replication material)

**INSERT:**

```
**The minimum interesting effect, and where it was fixed.** Every registered scorer in this campaign
judges a within-batch difference against the same three-way band: |Δ| ≤ 0.15 pp is a null, |Δ| > 0.30
pp is an effect, and (0.15, 0.30] is registered **in advance** as undecided so that a middling result
cannot be argued into either camp afterwards. The band was fixed in `analysis/c76_mm1_score.py`
before `mm1` ran and has been transcribed unchanged into seven further scorers —
`c77_pp1_score.py`, `c78_bn1_score.py`, `c79_ar1_score.py`, `c81_cc1_score.py`,
`c84_gn1_score.py`, `c88_scorers.py` (`aw1`) and `c97_bm2_score.py` — the last of which records the
provenance in its own source (`DECIDE = 0.30  # the REPLICATES line, unchanged from cc1/gn1/aw1`).
**0.30 pp is therefore this paper's pre-registered minimum interesting effect, at the level of a
single within-batch cell.** Two forms of the rule are in use and we say which applies where: most
scorers test the point estimate with a t or se side condition, while `aw1`'s tests the 95% interval.

**It is registered for a cell, not for a pool, and we do not extend it.** The headline
+0.556 ± 0.045 pp is an inverse-variance pool over eight cells; no scorer registered a bar for a
pooled quantity, and inventing one after the pooling is exactly the failure mode §3.4 exists to
prevent. **We therefore report the pooled headline as an estimate with its interval, not as a
threshold clearance.** For a reader who wants the comparison anyway, it is stated once and not
relied on: the pool clears the 0.30 line on both forms of the rule (point estimate +0.556; 95% lower
limit +0.468), and cell by cell all eight clear it on the point estimate (minimum +0.428) while five
of eight clear it on the interval — `mm1` (+0.169), `hz3` (+0.258) and `gn1`'s BatchNorm arm
(+0.287) do not. That spread is the reason we pool, and it is also the reason the pool's clearance
is not evidence the individual cells were each registered-significant.
```

---

#### EDIT B2-b — **Abstract**, one clause added to the measurement paragraph

**REPLACE:**

```
step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76, τ = 0.000).
```

*(as it stands after EDIT B1-a)*

**WITH:**

```
step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76, τ = 0.000). We
report that as an estimate and not as a threshold clearance: this campaign's pre-registered minimum
interesting effect, 0.30 pp, was fixed before `mm1` ran and carried unchanged into eight registered
scorers, but it is registered for a single within-batch cell and never for a pool (§3.3).
```

---

## 4. B3 — practical significance

### 4.1 The objection, and the number that decides it

Scope item (iv) raises the objection and drops it: ≈0.6 pp inside a method 1.8–4.2 pp behind a tuned
cosine schedule. A practitioner-facing answer is not available, and pretending otherwise would be
the paper's worst sentence. The designer-facing answer is available, and it needs one number the
draft has never reported: **what the swap costs.**

Re-derived from `wallclock_min` over the thirteen same-contrast cells, chunk arm against nodewise
arm, 100-epoch cells and `hz3`'s 300-epoch cell:

```
median per-cell ratio chunk777 / nodewise = 1.185   (range 1.086 – 1.360, 13 cells)
pooled means 74.9 min vs 64.4 min over 46 + 46 runs  (+16.4%)
and it is NOT node heterogeneity — the ratio holds inside every node we can pair on:
  node887 1.172 (7v8)   node883 1.182 (4v5)   node885 1.189 (5v4)   node884 1.164 (3v5)
  node886 1.169 (3v2)   node882 1.182 (3v1)   node881 1.198 (2v3)   node880 1.172 (1v2)
  node876 1.286 (4v2)   node874 1.286 (2v1)   node869 1.245 (4v2)   node868 1.313 (3v6)
  node867 1.384 (2v3)
```

So the swap is **not free in wallclock in our implementation**, by about 17%. It *is* free in
everything the method learns: m is 14,421 against 14,420, the parameter count is identical, and the
meta-state is identical in size. The overhead is our indexing code — a flat gather/scatter over
11.17 M weights against `nodewise`'s per-tensor view — not a property of the partition.

The comparison that decides practical significance is then obvious and we can run it, once, on the
only batch with the budget headroom. On `hz3`, paired within run, spending the same extra wallclock
on extra **epochs** of the aligned arm instead of on the swap:

```
nodewise, plateau5 at B=100 → B=109  (hz3's own 1.086 ratio):  +0.194 ± 0.100  (t 1.94, n=6)
nodewise, plateau5 at B=100 → B=117  (the other cells' 1.19):  +0.448 ± 0.084  (t 5.35, n=6)
swap the partition at B=100, same six seeds:                   +0.576 ± 0.109  (t 5.28)
difference (swap − 17% more epochs), paired:                   +0.129 ± 0.101  (t 1.27)
```

`plateau5` is a five-epoch trailing mean and the epoch-gain is not monotone in B (+0.313 at 113,
+0.448 at 117, +0.394 at 119), so the honest statement is a range and an unresolved ordering, not a
winner.

### 4.2 REPLACEMENT TEXT

---

#### EDIT B3-a — **§4.7**, new subsection, inserted after the paragraph beginning `Decomposing T by
Eq. 6 on `rl3``

**INSERT:**

```
**Practical significance, answered rather than volunteered.** Scope item (iv) of the abstract puts
the objection in its sharpest form — the effect is ≈0.6 pp inside a method that is 1.8 to 4.2 pp
behind a tuned cosine schedule — and it deserves an answer rather than a restatement. **The answer
is that this result is addressed to whoever builds the step-size adapter, not to whoever trains the
model**, and the two audiences get different verdicts.

*For a practitioner choosing an optimiser, this paper recommends nothing.* §7 T4 gives the deficit
against a tuned schedule at three depths and it widens with depth; +0.556 pp does not close a
1.807 pp gap on ResNet-18 and is irrelevant to a 4.214 pp gap on ResNet-50. Worse, the swap is not
even free in wallclock as we have implemented it. Over the thirteen same-contrast cells the uniform
`chunk777` arm ran a median **1.185×** longer than the `nodewise` arm (range 1.086–1.360; pooled
74.9 against 64.4 minutes over 46 runs each), and the ratio holds inside each of the thirteen
compute nodes on which both arms ran, so it is not node heterogeneity. On `hz3`, the only cell with
the budget headroom to test it, spending that same extra wallclock on extra **epochs** of the
aligned arm instead is worth between +0.194 ± 0.100 (at `hz3`'s own 1.086 ratio) and +0.448 ± 0.084
(at the other cells' 1.19), against +0.576 ± 0.109 for the swap; paired within run, the swap leads
by +0.129 ± 0.101, t 1.27, which does not resolve. **At equal wallclock, in the one cell where we
can measure it, changing the partition and training 17% longer are worth about the same, and we
cannot order them.**

*For someone designing a step-size adapter, the verdict is different, and it is the reason we
report the result.* The 17% is an artefact of our indexing, not of the partition: the two arms learn
14,421 and 14,420 step sizes respectively, carry identical parameter counts and identical meta-state,
and differ only in which weight index maps to which group. The intrinsic cost of the choice is
**zero** — and it is a choice every method in this family makes and none of them measures. IDBD,
Autostep, hypergradient descent, SwiftTD, CAM-HD, blockwise adaptivity and MetaOptimize itself all
default to an architecture-aligned partition (per layer, per block, per channel) on the unstated
premise that the architecture's own decomposition is the right one. On this corpus that premise is
measurably the wrong way round: at fixed group count the architecture-aligned partition is worse
than an arbitrary uniform one in every count-matched cell we have, by +0.556 ± 0.045 pp under an
SGDm base, by +1.000 ± 0.067 under SGD, and by up to +1.640 ± 0.245 on CIFAR-100. As a share of the
aligned arm's remaining error that is ρ = 0.0730 ± 0.0059 pooled over the eight SGDm cells, and
0.084 to 0.124 across the four SGD and RMSProp cells. It is also larger than the lever it is usually confused with: one decade of
group count, at fixed partition family, is worth +0.350 to +0.828 pp (§4.2), so the partition is
worth roughly two thirds of a decade to one and a half decades of count — a variable that method
papers do tune.

*What would make it a practitioner result, and why we do not claim it.* Every measurement here is
inside one meta-learning framework that trails a tuned schedule. Whether the same ordering holds in
a competitive method is untested: the design that would test it — the four partitions applied as a
fixed per-group learning-rate scale on a plain SGDm or AdamW run with no meta-learning at all — is
named in §9 and was not run. Until it is, the correct reading of this paper is that a design
parameter the field sets by architectural intuition has a measurable and consistent optimum in the
opposite direction, on one framework, at CIFAR resolution.
```

---

#### EDIT B3-b — **Abstract**, scope item (iv)

**REPLACE:**

```
replacement is in flight (§3.5). (iv) The effect is ≈0.6 pp inside a method that is 1.8 to 4.2 pp
behind a cosine schedule. (v) Every accuracy here is a test-set quantity and no validation split was
```

**WITH:**

```
replacement is in flight (§3.5). (iv) The effect is ≈0.6 pp inside a method that is 1.8 to 4.2 pp
behind a cosine schedule, and in our implementation the uniform arm also costs ≈17% more wallclock —
so this is a **designer-facing** result, addressed to whoever chooses where the groups go in a
step-size adapter, and not a recommendation to any practitioner to adopt this method or this
partition (§4.7). (v) Every accuracy here is a test-set quantity and no validation split was
```

---

#### EDIT B3-c — **§7 T4**, one sentence appended to the threat

**INSERT** at the end of T4, after the paragraph beginning `The single highest MetaOptimize cell
anywhere in the corpus`:

```
**This threat is not answered by the size of D, and we do not attempt to answer it that way.** The
practical-significance argument for the partition result is given in §4.7 and it is designer-facing:
the choice of partition is free of learned parameters and free of memory, it is the one lever in
this family that no method measures, and the deficit reported here is the reason we make no
recommendation to adopt the method.
```

---

## 5. B4 — the three registered-scorer exceptions, in one place

A stated rule with undisclosed exceptions is worse than no rule. All three are already visible
individually in the draft; none of them is visible from §3.4, which is where a reader is told the
rule.

### 5.1 The three, verified against the scorer sources

1. **§4.4 pools across step-size clip boxes.** `analysis/c87_rl3_score.py`'s registered header says
   so in terms — line 143, `NO POOLING ACROSS BOXES`, on the registered ground (lines 94–99) that
   `rl3`'s box is not the anchors' box and that a box change moves the optimiser and not merely the
   instrument. §4.4 pools thirteen cells spanning `−15:−2.3026` (9 cells), `−30:9.0` (3) and
   `−25:−2.3026` (1) anyway, and justifies it by measurement. That justification weakens on the
   thirteen-cell pool: between-box Q was 1.08 on 2 df (p 0.58) against within-box 35.32 on 8 df at
   eleven cells, and is **5.14 on 2 df (p 0.077)** at thirteen, because `bm2`'s two cells put all
   four non-SGDm cells into one box. The unconfounded test, inside the SGDm level alone, is
   **0.76 on 2 df (p 0.68)**, and that is what the pooling rests on.
2. **Table 2 row 4 is re-derived past the point where its scorer halts.** `analysis/c84_gn1_score.py`
   evaluates T0 first, per run, and T0.5 is box occupancy measured on `gn1`'s own probe records.
   With the probes excluded from the deposit the scorer halts there and never reaches **T1**, the
   positive-control gate at which `D_BN` would have been computed. Table 2 row 4 (`gn1` BatchNorm,
   +0.587 ± 0.153, 4 v 4) is our own re-derivation of exactly that quantity.
3. **§4.8 declines its scorer's registered primary window.** `analysis/c87_hz3_score.py` fixes
   `DENSE = 50`: the primary reading is a 50-epoch mean, not `plateau5`'s five. On that window the
   batch reads D(300) − D(100) = **+0.229**, verdict `GROWS`; on `plateau5` the same batch reads
   −0.149 ± 0.105 (t −1.42). §4.8 reports the `plateau5` reading as the claim and the registered
   verdict as a disclosure.

### 5.2 REPLACEMENT TEXT

---

#### EDIT B4-a — **§3.4**, new paragraph inserted immediately after the paragraph ending
`(§5.6, §7 T7).**` and before `This list is a list of the scorers we *have*`

**INSERT:**

```
**The rule has exactly three exceptions in this paper, and they are listed here rather than left to
be discovered.** In each case we depart from a registered scorer's own instruction, we say so at the
point of use, and we say so again here so that a reader is not required to reconstruct the set.

1. **§4.4 pools across step-size clip boxes, and `analysis/c87_rl3_score.py`'s registered header
   forbids it** — "NO POOLING ACROSS BOXES", on the registered ground that a box change moves the
   optimiser and not merely the instrument. The base-optimiser decomposition pools thirteen cells
   spanning three boxes (`−15:−2.3026`, nine cells; `−30:9.0`, three; `−25:−2.3026`, one). Our
   justification is a measurement rather than an assertion, and it is weaker than the previous draft
   reported. On the eleven-cell pool, partitioning Q by box left between-box Q 1.08 on 2 df, p 0.58,
   against within-box Q 35.32 on 8 df. On the thirteen-cell pool it leaves **between-box Q 5.14 on
   2 df, p 0.077** — because `bm2`'s two large cells both sit in `−15:−2.3026`, so that box now holds
   all four of the non-SGDm cells and the box axis has become partly confounded with the base axis.
   The uncontaminated test is the one taken inside a single base: over the eight SGDm cells, which
   span all three boxes, between-box Q is **0.76 on 2 df, p 0.68** (pools +0.582 ± 0.080,
   +0.629 ± 0.123, +0.523 ± 0.060). That is the number the pooling rests on, and we say so rather
   than quoting the thirteen-cell figure that the confound flatters. A `β-box` column is carried in
   Table 2 and Appendix B so that a reader who does not accept the argument can redo the split. It
   remains an exception.
2. **Table 2 row 4 is a quantity we re-derived past the point where its own scorer halts.**
   `analysis/c84_gn1_score.py` evaluates its T0 validity gates first and per run; T0.5 is box
   occupancy measured on `gn1`'s own probe records, which are not in the deposit, so the scorer
   halts at T0.5 and never reaches T1, the positive-control gate at which `D_BN` would have been
   computed. Row 4's +0.587 ± 0.153 is therefore ours, not the scorer's. The GroupNorm arm of the
   same batch, which is the contrast the scorer was written to judge, is excluded from every pool
   and quoted nowhere (§4.3, §7 T7).
3. **§4.8 reports the budget contrast on `plateau5` and declines the scorer's registered primary
   window.** `analysis/c87_hz3_score.py` fixes a 50-epoch mean as its primary reading and returns
   `GROWS` on it, with D(300) − D(100) = +0.229; `plateau5`, this paper's primary metric everywhere
   else, returns −0.149 ± 0.105 (t −1.42). We keep `plateau5` for consistency and print the
   registered verdict alongside it rather than instead of it, and §4.8 explains the mechanism of the
   disagreement — a 50-epoch trailing window at B = 100 contains the mid-training trough and at
   B = 300 does not.

There is no fourth. Every other scorer named in this section was run unedited and its printed
verdict quoted, including where the verdict cost us a subsection (§5.6, §7 T7) and including where
it refuted a mechanism we had proposed (`sm4`, §5.5). Supplying a scorer's own documented arguments
— `--root`, `--outs`, `--csv` — is not editing it.
```

---

## 6. B6 — the network list

### 6.1 What is true

`results/all_runs.csv`, network column, all 2,173 rows:

```
ResNet18 1667 | ResNet18_c100 188 | ResNet34 141 | ResNet10 110 | ResNet50 31
ResNet18_gn 17 | ResNet10_c100 9 | ResNet34_c100 9 | ResNet101 1
```

So the **corpus** does contain ResNet-10 (119 rows over two datasets) and one ResNet-101 run; the
abstract's list is not a fabrication. What is false is the implication. Every count-matched cell —
the thing the sentence introduces — is ResNet-18, ResNet-34 or ResNet-50; the ResNet-10 runs belong
to the granularity-ladder and early-screening programmes and contribute to no `D`. The abstract
already says "three networks (ResNet-18, ResNet-34, ResNet-50)" two sentences later, so as written
the abstract contradicts itself within one paragraph.

**Checked elsewhere:** `grep -n "ResNet-10\|ResNet10\|R10"` over `paper/DRAFT-v3.md` returns exactly
one hit, line 29, the abstract. §1.1 item 1, §4.3, §9 and Figure 1's caption all say ResNet-18/34/50.
**The defect is confined to the abstract.**

### 6.2 REPLACEMENT TEXT

---

#### EDIT B6-a — **Abstract**, opening sentence
(**PAIRED EDIT** on the run counts — see §7.1. If the corpus-count sweep is not being applied in the
same pass, keep `2,113` / `≈1,582` / `1,671` and change only the network clause.)

**REPLACE:**

```
approximations evaluated."* We take that question up with 2,113 runs (≈1,582 GPU-hours; 1,671
admissible) on ResNet-10/18/34/50 and CIFAR-10/100, and report one robust measurement, one
bounded null, and a mechanism we could not find.
```

**WITH:**

```
approximations evaluated."* We take that question up with 2,173 runs (≈1,625 GPU-hours; 1,724
admissible) on CIFAR-10 and CIFAR-100, spanning ResNet-10 through ResNet-50, and report one robust
measurement, one bounded null, and a mechanism we could not find. **Every count-matched
measurement below is on ResNet-18, ResNet-34 or ResNet-50**; the ResNet-10 runs belong to the
granularity-ladder and screening programmes and enter no contrast reported here.
```

*Re-derivation.* 2,173 rows; 1,724 admissible under `window_ok == 1 AND complete == 1 AND plateau5
present`; 2,150 rows carry a `wallclock_min` and they total 1,624.8 GPU-hours.

---

## 7. Cross-package notes and problems found while doing this work

### 7.1 The corpus counts are stale everywhere (NOT fixed by this package)

The ingest at `6a374f4` moved the corpus from 2,113 / 1,671 / 1,582 to **2,173 / 1,724 / 1,624.8**
(2,150 rows carry a wallclock). `grep -n "2,113\|1,671\|1,582"` finds them at lines **28, 453, 459,
786, 1875, 1904, 1908, 1954, 2212, 2213, 2279, 2344**. This package changes only line 28 (the
abstract), and only as a PAIRED EDIT. Whoever owns §3.3, §8 and Appendix A.8 should sweep the rest
in one pass; A.8 in particular is the corpus-size discrepancy register and will otherwise record a
stale "at write time" value.

### 7.2 §4.3's completeness claim is now false (NOT fixed by this package)

§4.3 asserts that Table 2 plus `ar1` is "**the complete set** of count-matched `nodewise`-versus-
uniform-chunk contrasts in this corpus … every batch that ever ran a `nodewise` arm alongside a
count-matched uniform-chunk arm is one of these eighteen". At 2,173 rows it is **twenty-two**.
Enumerated by grouping every admissible row on
`(batch prefix, network, dataset, base, meta, meta_stepsize, epochs_requested, beta_clip, alpha0,
hier, lam, eta_ratio, batch_size, augment, gamma)` and selecting the groups that carry both a
`nodewise` arm and a count-matched uniform-chunk arm — 23 groups carry a `nodewise` and *some*
chunk arm, of which `bn1` (chunk2325 only, m 4,851) is not count-matched:

| in Table 2 (16) | new since the ingest (4) | excluded, already disclosed (2) |
|---|---|---|
| cc1, mm1, pp1, gn1(BN), ml2, rl3@1e-4, rl3@3e-4, fa1, hz3, aw1, nl1(SGD), nl1(RMSProp), g3m, r50, gc1, gm2 | **bm2(SGD)** +0.9780 ± 0.0858 · **bm2(RMSProp)** +0.6313 ± 0.1492 · **sm3(AdamW/Lion)** +0.1413 ± 0.0638 · **sm4(AdamW/RMSProp-meta)** +0.8893 ± 0.2285 | `ar1` (box-void), `gn1`(GroupNorm) (scorer halt) |

**All twenty are positive; eighteen of twenty are resolved at t ≥ 3.0** (the exceptions are `ml2`
t 2.34 and `sm3` t 2.22). Whoever owns Table 2 should either add the four rows and change "16" to
"20" and "eighteen" to "twenty-two" throughout (abstract line 33, §1.1 item 1, §9), or restate the
completeness sentence as of a stated CSV revision. **This package deliberately left "16" alone** and
wrote §4.4 and the abstract so that `bm2`'s two cells are introduced by name — "the eleven of
Table 2 plus the two of the replication batch `bm2`" — which keeps the document self-consistent
under either resolution.

### 7.3 Scope item (iii) and §7 T1 are now false as written (NOT fixed by this package)

"All 367 partition-programme runs reported here use a **Lion** meta-optimiser" appears at lines
**76, 1587, 1701, 2157**. `sm4`'s twelve runs use an **RMSProp** meta-optimiser (CSV `meta` column,
all twelve rows), and `sm4` is a count-matched cell. Among the twenty count-matched cells, nineteen
are Lion and one is not. The sentence needs re-deriving by whoever owns §6.1 and §7 T1; the
defensible replacement wording is *"every count-matched cell but one uses a Lion meta-optimiser; the
exception is `sm4`, the corpus's only non-Lion partition cell (§3.5, R4)"*. This is a **weakening of
the paper's largest stated hole** and should be reported as such, not left stale.

### 7.4 The `bm2` scorer cannot be re-run from this repository

`python3 analysis/c97_bm2_score.py --csv results/all_runs.csv` (no `--root`) prints
`!!! NO PROBE DIR FOUND under None -- R0.5 is UNMEASURED` and correctly drops all four arms, so
D'_SGD and D'_RMS are `NOT READ`. This is the same defect as blocking item **A2**: every verbatim
scorer verdict in this paper is gated on probe records that the deposit excludes. This package
quotes `bm2`'s verdict as issued on the cluster and, separately, re-derives its D' values from the
CSV, which agree to the digits the scorer prints. **The A2 package should add `bm2` and `sm4` to the
list of verdicts that a reader cannot reproduce from the deposit.**

### 7.5 A number in §4.8 does not reproduce (NEW, not in the 18)

§4.8 quotes the 50-epoch registered reading as `D(300) − D(100) = **+0.229 ± 0.070, t 3.27**`. The
**point estimate reproduces exactly** from the deposited `.out` series (+0.229 over all six seeds,
+0.244 over the five box-matched), but the standard error does not reproduce under either estimator
this paper uses elsewhere:

```
paired within run, 50-epoch window, 6 seeds:   +0.229 ± 0.045  (t 5.11)
unpaired (Welch at each budget, se in quad.):  +0.229 ± 0.110  (t 2.08)
quoted in §4.8:                                +0.229 ± 0.070  (t 3.27)
```

Neither the sign nor the `GROWS` verdict is affected, and B4's exception list above deliberately
quotes only the point estimate and the verdict. But ±0.070 / t 3.27 is not re-derivable from the
deposit by the paper's own methods, and `analysis/c87_hz3_score.py` cannot be re-run here for the
same probe reason as §7.4. **This belongs in Appendix A (the discrepancy register) or in whatever
package owns §4.8; it is out of scope for this one and is not silently corrected.**

### 7.6 Figure 2 must be regenerated

See §2.7. The §4.4 replacement text and the Figure 2 caption are **PAIRED** with the
`analysis/c98_figures.py` CELLS patch. Applying the prose without the patch leaves the figure showing
eleven cells under a caption that says thirteen.

### 7.7 `analysis/c98_reproduce.py` will need new assertions

Blocking item A8 already says that script asserts 51 of the paper's numbers. This package introduces
these headline numbers, none of which is currently checked: the 13-cell pool (+0.6345 ± 0.0331), its
Q (55.4021 / 12), the four level pools and their within-level Q, the between-base Q (49.6562 / 3),
the share (89.63%), the batch-partition share (92.2%), both nested ΔQ values (5.5392 / 8 and
4.1080 / 2), the wallclock ratio (1.185) and the `hz3` equal-wallclock comparison. The A8 package
should add them.

---

## 8. Reproduction — every number in this package

All commands run from the repository root at HEAD `6a374f4`.

```bash
# B5 — corpus verification
wc -l results/all_runs.csv                       # 2174 → 2,173 data rows
python3 - <<'P'
import csv,collections
r=list(csv.DictReader(open('results/all_runs.csv')))
print(len(r), sum(1 for x in r if x['window_ok']=='1' and x['complete']=='1' and x['plateau5']))
print(collections.Counter((x['base'],x['meta']) for x in r if 'sm3' in x['run']))
print(collections.Counter(x['network'] for x in r))
print(sum(float(x['wallclock_min']) for x in r if x['wallclock_min'])/60)
P

# the published 11-cell decomposition, unedited scorer path
python3 analysis/c98_figures.py --all --numbers

# B1 — the 13-cell decomposition, the enumeration and the nested tests
#   the three scripts used are in the session scratchpad; each imports
#   analysis/c98_figures.py and reuses its arm() / welch() / meta() / chi2_sf()
#   verbatim, so the 11-cell figures reproduce c98_figures.py exactly before the
#   two bm2 cells are appended.  Reconstructing them needs only:
#     cell = welch(arm(rows,'bm2-sgd-ch','chunk777'), arm(rows,'bm2-sgd-node','nodewise'))
#     ... and the same for bm2-rms / sm3-awrms / sm4-awrms.

# B2 — the registered band, read out of the scorers rather than out of prose
grep -n "M1_REFUTE_AT\|M1_CONFIRM_AT" analysis/c76_mm1_score.py
grep -n "P2_NULL\|P2_STRONG"          analysis/c77_pp1_score.py
grep -n "NULL_HALF\|DECIDE"           analysis/c81_cc1_score.py analysis/c97_bm2_score.py
grep -n "_aw1_rule" -A 15             analysis/c88_scorers.py

# B3 — wallclock parity and the equal-wallclock comparison
#   wallclock: group results/all_runs.csv on (run prefix, granularity, node)
#   equal-wallclock: c98_figures.series('hz3-node-s*.out') / ('hz3-ch-s*.out')
#                    and c98_figures.pl5(series, B) at B in {100,105,109,113,117,119}

# B4 — the three exceptions, verified at source
grep -n "NO POOLING ACROSS BOXES"     analysis/c87_rl3_score.py     # line 143
grep -n "T0.5\|T1 " analysis/c84_gn1_score.py | head               # T0 precedes T1
grep -n "^DENSE"                      analysis/c87_hz3_score.py     # DENSE = 50

# B6 — the network census
python3 -c "import csv,collections;print(collections.Counter(r['network'] for r in csv.DictReader(open('results/all_runs.csv'))))"
grep -n "ResNet-10\|ResNet10\|R10" paper/DRAFT-v3.md                # one hit, line 29
```

---

## 9. Summary of what changed and what did not

**Claims deleted outright** (not hedged, not softened):

* "**88% of that variation is one identified moderator, the base optimiser**" — deleted from the
  abstract, from Contribution 3, from §4.4's heading and summary block, and from the Conclusion.
  The word *identified* is withdrawn; the share is restated on the correct pool (89.6% of thirteen
  cells) and immediately qualified by the rival label that beats it.
* "**At a fixed base optimiser, D is a constant … that single axis accounts for 88% of the observed
  heterogeneity**" — the §4.4 summary block. Replaced by the decomposition plus the conditional test.
* "This is consistent with §5.5, which kills second-moment normalisation as the axis" — withdrawn as
  written, because the second-moment main effect became resolved (z −3.18) when `bm2` entered.
* "`sm3` … its twelve runs are not yet ingested into the run table … a number that is not in the
  deposited run table cannot be re-derived" — false at HEAD; replaced by the registration reason.
* "an identified moderator for its heterogeneity that is not yet replicated at three of its four
  levels" (§9) — replaced; three of four levels are now replicated and the defect is elsewhere.
* "**ResNet-10**/18/34/50" as the network list for the measurement — corrected.

**Claims added, each with its own limit attached**: the base optimiser is the coarsest partition
leaving these cells homogeneous; batch identity explains more; base survives conditioning on batch
only at p 0.13; the moderator's single out-of-sample test removed 29% of squared prediction error on
two points; 0.30 pp is the campaign's pre-registered per-cell minimum interesting effect and is not
extended to the pool; the swap costs 17% wallclock in our implementation and buys about what 17%
more epochs buys; three registered-scorer exceptions exist and here they are.

**Untouched by this package**: §4.5, §4.6, §5, §6, Appendix A, Appendix B, `DRAFT-v3.md` itself, and
every analysis script.
