# Rewrite package `byte-identical-T9`

**Closes:** R0 checklist item 4 ("Delete 'byte-identical'"), R0 checklist item 5 ("Rewrite T9"),
gate blocking #4, red-team #2, Q11.
**Owns:** the six literal occurrences of "byte-identical" in `paper/DRAFT-v2.md`, correction **T9**
in §7, the budget paragraph in **§4.8**, the **Table 2 caption**, and the `hz3` half of **A.2**.
**Does not own** (numbers quoted here are for the integrator's cross-check only): the §4.4
heterogeneity rewrite (R0 item 2), the `ml2` argsline package, Table 2 row 9's published value, the
abstract's cell counts (R0 item 1).

Every number below was re-derived at write time from the runs' own `ARGS`/`ENV` lines, the raw
`.out` epoch series and the per-coordinate probe rails. Nothing is quoted from prose, including from
the briefing that commissioned this package — and **two of its statements did not survive
re-derivation**. They are flagged inline as **[BRIEF CORRECTED]** and the corrections are load-
bearing: they change what §4.8 is allowed to say. Reproduction commands are in §R.

---

## 0. The finding, verified from primary sources

### 0.1 `hz3` is two submissions in two β-boxes

The twenty-four `hz3` `.out` files each carry an `ENV:` line. Read verbatim, they split **21 / 3**:

| runs | `BETA_CLIP` | job ids |
|---|---|---|
| `hz3-node-s{0..5}`, `hz3-ch-s{0..4}`, `hz3-n1d-s{0..4}`, `hz3-c23-s{0..4}` (21 runs) | `-30:9.0` | 4782007 – 4782027 |
| **`hz3-ch-s5`, `hz3-n1d-s5`, `hz3-c23-s5`** (3 runs) | **`-15:-2.3026`** | 4814293 – 4814295 |

Job span **4814295 − 4782007 = 32,288**. The seed-5 D pair is `hz3-ch-s5` (`-15:-2.3026`) against
`hz3-node-s5` (`-30:9.0`) — **box-mismatched inside the pair**.

`BETA_CLIP` is the **only** effective difference. Diffing the `ARGS` line of each s5 run against its
own arm's s4 run, modulo `--seed`, `--run-name` and `--save-directory`, returns **identical** for all
four arms; diffing the `ENV` lines returns `BETA_CLIP` and `PROBE_DIR` (an output path) and nothing
else.

**The CSV is right.** All 24 `results/all_runs.csv` rows agree field-for-field with their own run's
`ENV` line, `beta_clip` included. CORRECTIONS 124.4(a) called this a *"CSV METADATA DEFECT"*; it is
not one, and entry 125 supersedes it. The defect is in the **experiment**, and it is therefore not
repairable by editing a column.

### 0.2 When the narrower floor actually binds: epoch 162, not epoch 0 — **[BRIEF CORRECTED]**

House rule: box occupancy is read from the per-coordinate rails `n_at_lo` / `n_at_hi`, never from the
62-element β summary. Sweeping **all 30,000 probe records** of all 24 runs (`PROBE=5`, 500 steps per
epoch → 100 records per epoch × 300 epochs):

| | `n_at_hi` ever > 0 | `n_at_lo` ever > 0 | first step at the floor | peak `n_at_lo` |
|---|---|---|---|---|
| the 21 runs at `-30:9.0` | never | never | — | 0 |
| `hz3-ch-s5` | never | yes | **step 81,000 = epoch 162** | 138 / 14,421 |
| `hz3-n1d-s5` | never | yes | **step 81,000 = epoch 162** | 100 / 4,851 |
| `hz3-c23-s5` | never | yes | **step 81,000 = epoch 162** | 46 / 4,851 |

The ceiling is never touched by any run in either box, so the ceiling half of the box difference
(`-2.3026` against `+9.0`) is **inert**. The floor half is inert too **until epoch 162** — before
that no coordinate in any run is at any rail, so up to epoch 162 a `-15` run and a `-30` run are the
same optimiser.

**Two consequences, and the briefing has them the wrong way round.**

* **D(100) is box-clean.** At the 100-epoch reading no rail has been touched by any of the 24 runs.
  Seed 5's D(100) = +0.148 is therefore a legitimate sixth measurement of the same quantity, **not a
  box artefact**. The briefing's framing — that seed 5 is a contaminated pair whose removal repairs
  the budget verdict — does not survive this check at the 100-epoch end.
* **D(200) and D(300) are box-contaminated**, one-sidedly, on `chunk777` — the arm D favours. The
  contamination is small (0.95% of coordinates at peak, against the registered 5% gate) and the
  registered scorer's H0 passes it as box-free, but it is real and it is asymmetric.

### 0.3 A second mismatch nobody has recorded: the seed-5 trio ran on different hardware

Reading the GPU banner of each `.out`:

| seed | `node` | `ch` | `n1d` | `c23` |
|---|---|---|---|---|
| 0, 1, 2 | L4 | L4 | L4 | L4 |
| 3, 4 | 2080 Ti | 2080 Ti | 2080 Ti | 2080 Ti |
| **5** | **2080 Ti** | **A100 80 GB** | **A100 80 GB** | **A100 80 GB** |

`analysis/c87_hz3_score.py` hard-codes `SEED_CLASS = {…, 5: "gpu-2080ti-11g"}` and states its reason
in the header: *hz3 assigns the GPU class by seed "so that all four arms of a seed share it — the fix
for CLOSEOUT 2.2(3)'s finding that mm1 and ar1 were arm-imbalanced on hardware and nobody reported
it."* **The resubmission broke exactly the property the design existed to guarantee**, and the
scorer's H4 table consequently prints `ch gpu-2080ti-11g n=3` for a set that is two 2080 Tis and one
A100. This is a defect in the registered scorer's metadata, not in its statistics: it mislabels the
hardware of three runs and would mislabel a hardware contrast built on that label. Every other
quantity it prints is unaffected.

This matters for §4.8 because it applies at **every** budget, including 100 — so there is no clean
6-seed reading of D at any budget, and the reason to set seed 5 aside is hardware at 100 epochs and
hardware **plus** box at 200 and 300.

**Direction, since a referee will ask.** §6.3's own hardware measurement is A100 − 2080 Ti = **+0.112
pp** (n = 5), and the A100 sits on the `chunk777` arm — so the mismatch should **inflate** seed 5's
D. Seed 5 is nonetheless the batch's **smallest** D(100) by a factor of 3.7. Neither the box nor the
hardware explains the outlier; it is unexplained, and we say so rather than manufacturing a cause.

### 0.4 Which contrasts are affected

| contrast | seed-5 pair | box-matched in pair? | GPU-matched in pair? |
|---|---|---|---|
| **D** = `chunk777` − `nodewise` | `ch-s5` (−15, A100) vs `node-s5` (−30, 2080 Ti) | **NO** (from ep 162) | **NO** |
| **T** = `nodewise1d` − `nodewise` | `n1d-s5` (−15, A100) vs `node-s5` (−30, 2080 Ti) | **NO** (from ep 162) | **NO** |
| G = `chunk2325` − `nodewise1d` | `c23-s5` vs `n1d-s5` (both −15, both A100) | yes | yes |
| U = `chunk2325` − `chunk777` | `c23-s5` vs `ch-s5` (both −15, both A100) | yes | yes |

D and T are the affected quantities. G and U are matched inside their pairs at every seed (they still
pool two boxes *across* seeds from epoch 162, which is a weaker objection, disclosed as such).

### 0.5 The 12-cell pool spans three β-boxes

Re-derived from `results/all_runs.csv` over the `nodewise`/`chunk777` rows of every batch in the §4.4
pool (Table 2 rows 1–4, 6–13):

| β-box | cells | which |
|---|---|---|
| `-15:-2.3026` | 8 | cc1, mm1, pp1, gn1-BN, gn1-GN, aw1, nl1-SGD, nl1-RMSProp |
| `-30:9.0` | 3 | rl3 @1e-4, rl3 @3e-4, **hz3** (21 of its 24 runs) |
| `-25:-2.3026` | 1 | fa1 |

`analysis/c87_rl3_score.py`'s own header, verbatim: **"NO POOLING ACROSS BOXES … Pooling them is
forbidden"**, and *"a box change moves the optimiser and not merely the instrument"*. So
"byte-identical" is false three times over: across boxes, and — for `hz3` — inside a single cell.

**The good news, and it should be printed.** The box explains none of the heterogeneity.
Fixed-effect Q decomposition over those 12 cells (Table 2 values, inverse-variance weights):

```
ALL 12    pool +0.545  se 0.036   Q 43.00 on 11 df, p 1.1e-05
  within-box    Q 42.40 on  9 df, p 2.7e-06
  between-box   Q  0.61 on  2 df, p 0.74
```

Deleting the false warrant therefore costs §4.4 nothing: the heterogeneity is *within* box, not
between. Say that, rather than saying nothing.

---

## 1. The six "byte-identical" occurrences

Five are this package's. The sixth (§6.1, line 838) belongs to the `ml2` package; a note is filed in
§5.

### 1.1 Abstract — opening block (DRAFT-v2 line 29)

**REPLACE**

> 0.238. Over the twelve cells sharing a byte-identical contrast the fixed-effect pool is +0.546
> with **Q = 43.2 on 11 df, p = 1.0e-5** — D varies genuinely across configurations
> (τ = 0.215 pp against 0.151 pp rms measurement error), not just noisily.

**WITH**

> 0.238. Over the twelve cells that run the same `nodewise` → `chunk777` contrast on ResNet-18 the
> fixed-effect pool is +0.545 with **Q = 43.0 on 11 df, p = 1.1e-5** — D varies genuinely across
> configurations (τ = 0.215 pp against 0.151 pp rms measurement error), not just noisily. Those
> twelve cells span **three step-size clip boxes**; the heterogeneity is entirely within box
> (between-box Q = 0.61 on 2 df, p = 0.74), so the pool is reported with the box stated rather than
> assumed away.

*Re-derivation.* Inverse-variance pool of Table 2 rows 1–4 and 6–13 = **+0.5447**; Q = **43.005** on
11 df, p = **1.08e-5**. The draft's "+0.546 / Q 43.2" is a transcription slip against CORRECTIONS'
own "Q = 43.0". τ is unchanged at 0.215.

### 1.2 §4.4 "D is genuinely heterogeneous" (DRAFT-v2 lines 453–454)

**REPLACE**

> Over the twelve cells that share a **byte-identical** partition contrast (ResNet-18
> `nodewise` → `chunk777`; rows 1–4, 6–13 above), the fixed-effect pool is **+0.546** with

**WITH**

> Over the twelve cells that run the **same partition contrast** — ResNet-18, `nodewise` →
> `chunk777`, count-matched to +1 group on 14,420; rows 1–4, 6–13 above — the fixed-effect pool is
> **+0.545** with

and **INSERT** immediately after the blockquote that follows (i.e. before "Dropping the GroupNorm
cell:"):

> **These twelve cells are not one configuration, and we do not call them one.** They span three
> step-size clip boxes — `-15:-2.3026` (8 cells), `-30:9.0` (3), `-25:-2.3026` (1) — and
> `analysis/c87_rl3_score.py`'s registered header forbids pooling across boxes, on the ground that a
> box change moves the optimiser and not merely the instrument. We pool anyway, and we justify it by
> measurement rather than by assertion: partitioning Q by box gives **between-box Q = 0.61 on 2 df
> (p = 0.74)** against **within-box Q = 42.40 on 9 df**. The box carries none of the heterogeneity. A
> `box` column is carried in Table 2 and in Appendix B so the reader can redo this split.

*Note for the §4.4 owner (R0 item 2):* the within-SGDm+BN subgroup (k = 8, Q 4.22/7) is untouched;
the box partition is orthogonal to the base partition and both can be printed.

### 1.3 §5.8 "Null: D is not predictable" (DRAFT-v2 line 760)

**REPLACE**

> The seventeen D cells of Table 2 collapse to **11 distinct design points** (the six byte-identical ResNet-18/SGDm/
> η=1e-4/100-epoch batches are one point; the two CIFAR-100 batches are one).

**WITH**

> The seventeen D cells of Table 2 collapse to **11 distinct design points** (the six ResNet-18 /
> SGDm / η = 1e-4 / 100-epoch batches are one point — they agree on every configuration column except
> the clip box, where five sit at `-15:-2.3026` and `rl3` at `-30:9.0`; the two CIFAR-100 batches are
> one).

*Re-derivation.* The six are cc1, mm1, pp1, gn1-BN, ml2, rl3 @1e-4. Box census over their
`nodewise`/`chunk777` rows: five at `-15:-2.3026`, one (`rl3`) at `-30:9.0`. Two boxes, not one. The
design-point count of 11 is unaffected.

### 1.4 §6.3 replacement statement (DRAFT-v2 line 890, first line of the blockquote)

**REPLACE**

> At byte-identical science and n ≥ 3 per batch, cross-batch offsets on this cluster are bounded by

**WITH**

> At matched science — same network, dataset, granularity, base, meta, η, α₀, γ, augmentation, clip
> box, budget — and n ≥ 3 per batch, cross-batch offsets on this cluster are bounded by

*Why.* The 26-configuration / 237-run reduction behind this bound already keys on the full
configuration tuple, `beta_clip` included, so the sentence is true; only the word is wrong. Nothing
numeric changes.

### 1.5 Appendix A.4 (DRAFT-v2 lines 1086–1089)

**REPLACE**

> DerSimonian–Laird on the twelve byte-identical cells with Welch standard errors gives
> **τ = 0.215 pp** against an **rms se of 0.151 pp**. Q reproduces exactly (43.2 vs 43.0 on 11 df;
> 36.4 vs 36.3 on 10 df dropping GroupNorm).

**WITH**

> DerSimonian–Laird on the twelve same-contrast cells with Welch standard errors gives
> **τ = 0.215 pp** against an **rms se of 0.151 pp**. Q reproduces (43.0 vs 43.0 on 11 df; 36.3 vs
> 36.3 on 10 df dropping GroupNorm); the "43.2" and "36.4" carried in an earlier draft of this
> appendix were a transcription slip and are corrected here.

*Re-derivation.* From the Table 2 values, Q = **43.005** on 11 df; dropping gn1-GN, Q = **36.29** on
10 df with pool **+0.570**. The word "exactly" was doing work a 43.2-vs-43.0 mismatch does not
support; "reproduces" is the honest verb.

---

## 2. T9 — the rewrite

**REPLACE** (DRAFT-v2 §7, lines 947–950)

> **T9 — Excluded and unusable data.** One batch (`ar1`, D = +0.697 ± 0.118) is excluded as box-void
> throughout. Three `hz3` rows carry a `beta_clip` metadata value inconsistent with their batch; any
> scorer that groups on that column silently drops them and reads D(300) = +0.464 instead of the
> authoritative +0.428. Neither exclusion changes a verdict; both are disclosed because they are the
> asymmetries a referee finds first.

**WITH**

> **T9 — Excluded data, and one batch that is two.** One batch (`ar1`, D = +0.697 ± 0.118) is
> excluded as box-void throughout: it bound on the step-size guards asymmetrically, in the direction
> that inflates D.
>
> `hz3` carries a second, different defect, and it is a **configuration** defect, not a metadata one.
> The batch is two submissions: twenty-one runs at job ids 4782007–4782027 in the clip box `-30:9.0`,
> and three seed-5 runs — `chunk777`, `nodewise1d`, `chunk2325` — resubmitted 32,288 job ids later at
> 4814293–4814295 in the narrower box `-15:-2.3026`. Their `ENV` lines say so and
> `results/all_runs.csv` records it faithfully; nothing here is repairable by fixing a column.
> `BETA_CLIP` is the only effective difference: every `ARGS` flag matches the corresponding seed-4
> run exactly.
>
> Two things follow, and they are not the same thing.
>
> *First, the box.* Sweeping all 30,000 probe records of all 24 runs, no coordinate of any run
> reaches either rail before **step 81,000 = epoch 162**; from there the three narrow-box runs sit on
> their floor to the end (peak 138/14,421, 100/4,851 and 46/4,851 coordinates), while all
> twenty-one wide-box runs stay at 0/N throughout and the ceiling is never touched by anything. So
> the box difference is **inert at the 100-epoch reading and live at the 200- and 300-epoch
> readings**, one-sidedly, on the arm D favours. It is small — 0.95% of coordinates at its peak,
> against the registered 5% occupancy gate, which the batch's scorer duly passes — but it is real and
> it is asymmetric.
>
> *Second, the hardware.* The resubmitted trio also ran on an A100 80 GB while their seed-5
> `nodewise` partner ran, with the rest of the original submission, on an RTX 2080 Ti. The batch was
> designed to assign GPU class **by seed** precisely so that a seed's four arms share it; the
> resubmission broke that, and the batch's registered scorer still labels all four seed-5 runs
> `gpu-2080ti-11g`. This mismatch applies at **every** budget, the 100-epoch reading included.
>
> Consequently §4.8's within-run pairing cancels seed, run and batch, but **not** the clip box (from
> epoch 162) and **not** the GPU class (throughout). As originally written it claimed both, and that
> was wrong. The same applies to T = `nodewise1d` − `nodewise`; G and U are matched inside their pairs
> at every seed and are unaffected.
>
> Seed 5 is also the batch's per-seed outlier at 100 epochs — D(100) = **+0.148** against **+0.548,
> +0.564, +0.586, +0.622, +0.990** — and unremarkable at 300 (+0.290, against a seed-2 low of
> +0.168). We note explicitly that **neither defect explains that outlier**: the box is inert at 100
> epochs, and the hardware term (§6.3: A100 − 2080 Ti = +0.112 pp) sits on the arm that would
> *inflate* D, not deflate it. The 100-epoch outlier is unexplained. §4.8 reports the budget contrast
> both with and without seed 5 for this reason, and a replacement seed-5 trio in the original box and
> on matched hardware is registered as run **R2**.
>
> Finally, for reuse: a scorer that groups on `beta_clip` drops exactly those three runs, keeps
> `nodewise` seed 5, and reads an **unbalanced** D(300) = +0.464 ± 0.084 in place of the balanced
> +0.428 ± 0.086. That is an artefact of the grouping, not a second estimate.
>
> Neither `ar1`'s exclusion nor `hz3`'s split changes a **sign**. The `hz3` split does move one
> verdict's **margin**, which is why §4.8 carries it inline rather than leaving it here.

*Re-derivations behind every number above.* Per-seed `plateau5` (mean of the last 5 test epochs of
the first B epochs), from the raw `.out` series:

| seed | box, GPU (`ch` / `node`) | D(100) | D(200) | D(300) | D(300) − D(100) |
|---|---|---|---|---|---|
| 0 | −30, L4 / −30, L4 | +0.586 | +0.294 | +0.432 | −0.154 |
| 1 | −30, L4 / −30, L4 | +0.564 | +0.956 | +0.476 | −0.088 |
| 2 | −30, L4 / −30, L4 | +0.622 | +0.452 | +0.168 | −0.454 |
| 3 | −30, 2080 Ti / −30, 2080 Ti | +0.990 | +0.436 | +0.550 | −0.440 |
| 4 | −30, 2080 Ti / −30, 2080 Ti | +0.548 | +0.738 | +0.650 | +0.102 |
| **5** | **−15, A100 / −30, 2080 Ti** | **+0.148** | +0.210 | +0.290 | **+0.142** |

Unbalanced `beta_clip`-grouped reading: `ch` seeds 0–4 against `node` seeds 0–5 →
**+0.464 ± 0.084, t 5.51**, reproducing CORRECTIONS 124.4(a)'s +0.464.

---

## 3. §4.8 — the budget headline, now carrying its sensitivity

**REPLACE** (DRAFT-v2 lines 540–556: the heading through the paragraph ending "See Appendix A.2.)")

> ### 4.8 Budget: the effect is present at 3× the budget and is statistically flat
>
> `hz3` ran the four arms for 300 epochs at 6 seeds in one batch, so D at 100 and at 300 epochs can
> be taken **within run**, per seed, cancelling seed, run, batch, box and GPU class identically.
> From the raw epoch series:
>
> | budget | D (paired, n = 6) | se |
> |---|---|---|
> | 100 | +0.576 | 0.109 |
> | 200 | +0.514 | 0.115 |
> | 300 | +0.428 | 0.071 |
>
> **D(300) − D(100) = −0.149 ± 0.105, t −1.42.** So D is present and resolved at a 3× budget and is
> statistically **flat** from 100 to 300 epochs. It is not an artefact of the last fifth of training,
> and it does **not** grow. (An earlier internal reading claimed growth; that reading used a 50-epoch
> trailing window, which at B = 100 spans epochs 50–99 and therefore *contains* the mid-training
> trough documented below, while at B = 300 it contains none. The window injects the trough at
> exactly one budget: at w = 50 the same data give +0.229 ± 0.045, t +5.11. See Appendix A.2.)

**WITH**

> ### 4.8 Budget: the effect survives 3× the budget; whether it decays is not resolved
>
> `hz3` ran the four arms for 300 epochs at 6 seeds, so D at 100, 200 and 300 epochs can be taken
> **within run**, per seed. That pairing cancels the seed, the run and the batch identically. It does
> **not** cancel the step-size clip box or the GPU class, because `hz3` is two submissions: its
> seed-5 `chunk777`, `nodewise1d` and `chunk2325` runs were resubmitted in the narrower box
> `-15:-2.3026` and on an A100, while everything else — including their own seed-5 `nodewise` partner
> — ran at `-30:9.0` on an L4 or a 2080 Ti (T9). We therefore report the budget contrast **twice**:
> as submitted, and over the five clean seeds.
>
> | budget | D, 6 seeds as submitted | se | D, 5 clean seeds | se |
> |---|---|---|---|---|
> | 100 | +0.576 | 0.109 | **+0.662** | 0.083 |
> | 200 | +0.514 | 0.115 | **+0.575** | 0.119 |
> | 300 | +0.428 | 0.071 | **+0.455** | 0.081 |
>
> **The level is robust, and it is the claim we make.** D(300) reads +0.428 ± 0.086 at 6 v 6
> (t 4.94) and +0.455 ± 0.096 at 5 v 5 (t 4.75) on the Welch estimator used everywhere else in this
> paper; all six seeds favour `chunk777` at 300 epochs (exact binomial p = 0.0156). **The partition
> gap is not an artefact of a 100-epoch budget.**
>
> **The trend is not robust, and we do not claim it.** Within-run, D(300) − D(100) = **−0.149 ±
> 0.105, t −1.42** over all six seeds and **−0.207 ± 0.107, t −1.94** over the five clean ones.
> Neither resolves at |t| ≥ 2, but the second is close enough that the difference matters, so we say
> where it comes from: 76% of the shift is at the **100-epoch** end (the six-seed D(100) rises by
> 0.086 pp when seed 5 is removed, against 0.027 pp at 300 epochs), and seed 5's low D(100) is
> **not** explained by either defect — the clip box is provably inert before epoch 162, and the
> hardware term (§6.3) points the other way. It is an unexplained extreme value in an n = 6 cell.
> The honest statement is therefore the weaker one: **D does not grow with budget from 100 to 300
> epochs, and we cannot resolve whether it decays.** We do not report flatness as a result. A
> box- and hardware-matched replacement trio (run R2) is registered and will settle it; until it
> lands this cell carries its sensitivity in the text.
>
> One further reading must be disclosed rather than buried, because the batch's own registered scorer
> prints it. `analysis/c87_hz3_score.py` fixes its primary window at **50 epochs**, not at
> `plateau5`'s 5, and on that window returns D(300) − D(100) = **+0.229 ± 0.070, t 3.27**, verdict
> `GROWS`. The windows disagree because at B = 100 a 50-epoch trailing mean spans epochs 50–99 and
> therefore *contains* the mid-training trough documented below, while at B = 300 it contains none:
> the window injects the trough at exactly one budget. `plateau5` is this paper's primary metric
> throughout and we do not switch it here — but the registered verdict is `GROWS`, our
> primary-window reading is a non-significant decline, and a reader is entitled to both. See
> Appendix A.2.

*Re-derivations.* Paired-over-seeds estimator on the `plateau5` window, from the raw `.out` series.
**6 seeds:** D(100) +0.5763 ± 0.1088, D(200) +0.5143 ± 0.1148, D(300) +0.4283 ± 0.0714; change
**−0.1487 ± 0.1047, t −1.4193** on 5 df. **5 clean seeds:** D(100) +0.6620 ± 0.0827, D(200)
+0.5747 ± 0.1192, D(300) +0.4553 ± 0.0807; change **−0.2068 ± 0.1067, t −1.9379** on 4 df, two-sided
p = 0.125. The "−1.93" in CORRECTIONS 124 and in STATUS's R2 row is this same quantity rounded one
digit low; the value is **−1.9379 → −1.94**, and the text above uses −1.94. Shift decomposition:
D(100) moves +0.0857 and D(300) moves +0.0270 when seed 5 is dropped, so the 100-epoch end supplies
0.0857 / (0.0857 + 0.0270) = **76.0%** of the change in the contrast. Welch readings on the same
rows: D(300) 6 v 6 +0.428 ± 0.086 (t 4.94, df 9.7), 5 v 5 +0.455 ± 0.096 (t 4.75, df 6.8). The
`GROWS` figures are quoted unedited from the scorer's own H3 block.

---

## 4. Knock-on edits inside this package's scope

### 4.1 Table 2 caption (DRAFT-v2 lines 415–418)

**REPLACE**

> Welch difference of arm means; se from the two arm variances; every cell is a
> separate contiguous submission except the two `rl3` rungs and the two `nl1` bases, which share a
> batch.

**WITH**

> Welch difference of arm means; se from the two arm variances. Every cell is a separate contiguous
> submission except the two `rl3` rungs and the two `nl1` bases, which share a batch, and **`hz3`
> (row 9), which is two submissions 32,288 job ids apart, in two clip boxes and on two GPU classes**
> — see T9. A `box` column is carried in Appendix B for all seventeen cells.

### 4.2 Table 2 row 9 — footnote, not a value change

Row 9 stays at its published **+0.428 ± 0.086, 6 v 6**. Mark the row `9†` and add below the table:

> † `hz3`'s seed-5 `chunk777` run sits in a narrower clip box and on a different GPU class from its
> `nodewise` partner (T9). The matched 5 v 5 reading is **+0.455 ± 0.096, t 4.75**; the cell's sign,
> magnitude and resolution are unchanged, the difference being 0.027 pp against a 0.086 pp se. Run R2
> restores a matched 6 v 6.

*Re-derivation.* +0.4553 − 0.4283 = 0.0270 pp = 0.31 se. Substituting the 5 v 5 value into the §4.4
pool moves the fixed effect from **+0.545 to +0.553** and Q from **43.0 to 42.0** on 11 df
(p 1.1e-5 → 1.7e-5). No verdict moves in either direction, which is why the published row is left
alone and the sensitivity is carried as a footnote.

### 4.3 §5.4 D − G table, `hz3` row — optional footnote only

The G leg is matched inside its pair, so this row needs no change. For the record, matched at 5 v 5
it reads D +0.455 ± 0.096, G −0.050 ± 0.075, **D − G +0.506 ± 0.121, t 4.16** against the published
+0.484 ± 0.106, t 4.57 — same verdict. Suggested footnote if the §5.4 owner wants one: *"`hz3`'s
seed-5 trio ran in a narrower clip box and on different hardware (T9); matched at 5 v 5 this row
reads +0.506 ± 0.121, t 4.16."*

### 4.4 §4.7 T table, `hz3` row — footnote recommended

T = `nodewise1d` − `nodewise` **is** mismatched at seed 5 on both axes. Published +0.337 ± 0.069,
t 4.85; matched 5 v 5 **+0.328 ± 0.084, t 3.89**. The claim "every one resolved at t ≥ 3.3" survives
(3.89 ≥ 3.3); the range "+0.337 to +1.363 pp" becomes "+0.328 to +1.363 pp" if the §4.7 owner prefers
the matched value. Suggested footnote: *"`hz3` matched at 5 v 5: +0.328 ± 0.084, t 3.89 (T9)."*

### 4.5 Appendix A.2 (DRAFT-v2 lines 1074–1078)

**REPLACE**

> G(AdamW) = **+0.232 ± 0.089, t 2.62**; and the budget effect is **−0.149 ± 0.105, t −1.42** — flat.
> Both replacements match the project's own later corrections; we record the originals so the
> supersession is visible.

**WITH**

> G(AdamW) = **+0.232 ± 0.089, t 2.62**; and the budget effect is **−0.149 ± 0.105, t −1.42**, i.e. a
> decline that does not resolve — **−0.207 ± 0.107, t −1.94** once `hz3`'s mismatched seed-5 pair is
> set aside (T9, §4.8). Both replacements match the project's own later corrections; we record the
> originals so the supersession is visible. Note that the 50-epoch reading is not merely a discarded
> internal note: it is the **registered primary** of `analysis/c87_hz3_score.py`, whose verdict is
> `GROWS`. We keep `plateau5` as this paper's primary metric and print both, rather than quietly
> preferring the window that suits the narrative.

---

## 5. Coordination notes — occurrences and knock-ons this package does **not** apply

1. **§6.1, line 838** — *"its two nominal halves are byte-identical configurations"* (`ml2`). Belongs
   to the `ml2`/argsline package. For its owner: the ARGS audit found the halves identical
   **including `--seed`**, differing only in `PROBE_DIR`, so the accurate wording is *"the same
   command line including `--seed`, differing only in an output path"* — and the accompanying *"two
   independent 3 v 3 measurements"* must become *"two nondeterministic reruns of one 3 v 3
   measurement"*, with the 0.197 pp spread relabelled a **nondeterminism** bound.
2. **`docs/STATUS.md` line 34** — *"sm3 is a byte-identical independent replicate of `aw1`"*. False at
   the ARGS level: `sm3` carries a residual `--normalizer-param-meta 0.999` that `aw1` does not (inert
   — Lion ignores it — but present). Replace with *"identical in every effective flag that Lion
   reads"*. Owned by the `sm3` package; recorded here because it is the same word.
3. **§4.4's "Q = 43.2" and "Q = 36.4"** (lines 456, 459) are the §4.4 owner's; the re-derived values
   are **43.005 / 11 df** and **36.29 / 10 df**. Corrected in §1.1 and §1.5 above only because those
   two sentences are this package's.
4. **`analysis/c87_hz3_score.py`'s `SEED_CLASS`** mislabels three runs as 2080 Ti when they ran on an
   A100 (§0.3). Under STANDING RULE 19 the file is frozen and **must not be edited**; the correct
   remedy is a note in the batch report and in T9, both delivered here. If R2 re-runs the trio, the
   label becomes true again and the file needs no change at all.
5. **Appendix B box column** — gate blocking #4 asks for a box column in Table 2 *and* Appendix B.
   §4.1 adds the Table 2 caption pointer; the Appendix B table is the reproducibility package's. The
   census it needs is §0.5 above, extended: g3m, r50, gc1, gm2 and `ar1` are all `-15:-2.3026`.
6. **R2's specification should be tightened.** As registered in STATUS it says only "re-run in box
   −30:9.0". On the evidence of §0.3 it must also **pin the GPU class to the seed-5 partner's
   (2080 Ti)**, or the replacement will repair one mismatch and keep the other.

---

## R. Reproduction

```bash
cd "/Users/teshnizi/Saber Optimization/alice-backup"

# 0.1  the ENV lines and the ARGS diff, all 24 runs
for f in runs/hz3-*.out; do printf '%s\t' "$(basename "$f")"; \
  grep -m1 -o 'BETA_CLIP=[^ ]*' "$f"; done
for a in ch n1d c23 node; do
  A=$(grep -m1 '^ARGS' runs/hz3-$a-s4-*.out | sed 's/--seed [0-9]*//;s#--save-directory [^ ]*##;s/--run-name [^ ]*//')
  B=$(grep -m1 '^ARGS' runs/hz3-$a-s5-*.out | sed 's/--seed [0-9]*//;s#--save-directory [^ ]*##;s/--run-name [^ ]*//')
  [ "$A" = "$B" ] && echo "$a: ARGS identical" || echo "$a: ARGS DIFFER"; done

# 0.2  every probe record of every run: when does a rail first bind?
python3 - <<'PY'
import json, os
for a in ("node","ch","n1d","c23"):
    for s in range(6):
        recs=[json.loads(l) for l in open("runs/hz3/probe_%s_hz3_s%d/probe.jsonl"%(a,s))]
        f=next((r["step"] for r in recs if r["n_at_lo"]>0), None)
        print(a, s, len(recs), "max_lo", max(r["n_at_lo"] for r in recs),
              "first_lo_step", f, "max_hi", max(r["n_at_hi"] for r in recs))
PY

# 0.3  GPU class per run
for f in runs/hz3-*.out; do printf '%-30s ' "$(basename "$f")"; \
  grep -m1 -E 'NVIDIA|Tesla' "$f"; done

# 3.  the registered scorer, run UNEDITED (STANDING RULE 16)
cd hierarchical-metaoptimize
python3 analysis/c87_hz3_score.py \
  --runs   "/Users/teshnizi/Saber Optimization/alice-backup/runs" \
  --probes "/Users/teshnizi/Saber Optimization/alice-backup/runs/hz3"
```

The scorer confirms, unedited: `coord_lo` non-zero on exactly `ch`/`n1d`/`c23` seed 5 at the 200- and
300-epoch windows and zero at 100 and on the other 21 runs; `D(100)` plateau5-comparable
`+0.576 se 0.122`; `D(300)` plateau5-comparable `+0.428 se 0.086`; H3
`D(300) - D(100) = +0.229 se 0.070 t 3.27 -> GROWS` on its registered 50-epoch window.

D at budget B is `plateau5` on the truncated series: the mean of test accuracy over epochs
`B−5 … B−1`, per run, from the `Epoch n, Train Accuracy: …, Test Accuracy: …` lines of each `.out`.
Paired estimator = mean over seeds of (`ch` − `node`), se = sd/√n. Welch estimator = difference of
arm means, se = √(s²_A/n_A + s²_B/n_B), as used throughout Table 2.
