# Corrections — what actually holds

Written after an adversarial review (`REVIEW-hmkhd2.md`) checked the draft against
`results/all_runs.csv` and found several headline claims refuted by controls **in this repo**.
Each item below was re-verified against raw run outputs before being written here.

## 1. The pooling gain is budget-dependent, and the ordering INVERTS

Corrected (meta-gradient-space) pooling, `z'_b = (1-r) sum_j z_j + r z_b`, layerwise m=62:

| arm | 100 epochs (n=3) | 300 epochs (n=2) |
|---|---|---|
| scalar (r=0) | 88.14 | **92.68** |
| plain layerwise (r=1) | **91.35** | 92.01 |
| z-pool r=0.1 | 90.01 (−1.34) | **93.47 (+1.46)** |
| z-pool r=0.05 | — | **93.47 (+1.46)** |
| beta-shrink lam=0.1 | 92.79 (+1.46) | 92.61 (+0.59 best / +0.25 final) |

**At 100 epochs pooling hurts. At 300 epochs pooling wins, and scalar overtakes plain
layerwise.** The optimum in the pooling parameter moves with budget. This is the
bias–variance optimum the literature says is the defensible form of the claim — but it is
*not* the claim the draft made.

Note also that **scalar > plain layerwise at 300 epochs** reproduces the parent paper's
ImageNet observation on CIFAR-10 by lengthening the budget alone. That is a stronger version
of our budget argument than the draft's, and it is free.

## 2. The two "hierarchical" operators are NOT the same method

The draft conflated them. They are different interventions with different effects:

* **beta-shrink** (`HIER=shrink`): contract beta toward the group mean *after* the meta update.
  Helps at 100 ep (+1.46pp), fades by 300 ep (+0.25pp on plateau).
* **z-pool** (`HIER=zpool`): mix the *meta-gradient* before the update. Has exact endpoints
  (verified: sd(beta)=0.000e+00 at r=0). Hurts at 100 ep, wins at 300 ep.

They must be reported separately. Only z-pool has validated endpoints.

## 3. The +1.46pp best-lambda WAS cherry-picked
Max of 7 cells at n=3, spread 0.29pp against per-cell sd 0.08–0.23. Reporting the max of a
sweep as "the" effect is selection bias. The honest statement is the *range* across lambda
(+1.17 to +1.46), and even that is 100-epoch-specific.

Related: "flat over three orders of magnitude" is **operator saturation**, not robustness — a
per-step lambda has half-life <= 693 steps against a 50,000-step run, so every lambda >= 0.001
is fully saturated by the end. The draft presented an artefact as the method's best property.

## 4. Metric hygiene
`best-of-100-epochs` inflates over plateau accuracy by ~0.36pp median — the same order as the
effects being claimed. **Primary metric must be plateau (mean of last 5 epochs) or
epochs-to-target; best-of-run is reportable only alongside, never alone.**

## 5. Claims withdrawn
* The §3 speed table came from **unguarded** runs; with the guard the gain is ~16%, not 19%,
  and ep→85% (10.7 ± 1.2 vs 10.0 ± 0.0) is not resolvable at the ±0.02pp floor.
* §3.1's "scalar fails on 2 of 3 seeds" was already corrected to 1/3 in FINDINGS (0/3 under
  Lion). The draft quoted the superseded number.
* §5's gamma=1 trace-overflow mechanism was **refuted by our own gamma=0.999 control**, which
  failed identically. The overflow is real; the stated cause is not established.

## 6. What survives, and is missing from the draft
* **H4 base-optimizer interaction** — granularity helps under SGDm, null under AdamW. Large,
  multi-seed, unaffected by any of the above.
* **The budget inversion** (§1 here) — now the strongest result in the project.
* Results the routine produced that the draft never mentioned: a 53.1% sign-agreement
  measurement, a 4.4pp aggregation-order effect, and M1 additive reaching 93.46 at n=5.
  These need checking and, if they hold, they belong in the paper.

## 7. Process failure to avoid repeating
The refuting controls **had already completed** when the draft was written; they were produced
by the hourly routine and never reviewed. Writing prose from remembered results instead of from
`results/all_runs.csv` is what caused this. **Re-derive every table from the CSV at write time.**

---

## 8. The three "unreviewed" results, now verified — two are major

### 8a. M1 additive has a genuine interior optimum (plateau metric, n=5–10)

> **SUPERSEDED BY §10.** The table below pools two meta-optimizers into the same
> cells and its per-cell numbers and n are wrong. The interior optimum itself
> survives — see §10 for the corrected, stratified table.

| r | plateau | n |
|---|---|---|
| 0 (= scalar) | 92.15 | 5 |
| 0.03 | 92.14 | 8 |
| **0.05** | **93.06** | 7 |
| **0.07** | **93.22** | 5 |
| 0.1 | 92.28 | 10 |
| 0.2 | 91.39 | 3 |
| 0.3 | 90.96 | 3 |

A clean inverted-U peaking at r ≈ 0.05–0.07, **+1.07pp over r=0**, measured on plateau rather
than best-of-run, at n=5–7. This is the bias–variance optimum in partial pooling that the
project set out to find, and it is the best-supported positive result we have.

### 8b. The i.i.d. / sqrt(N) noise model is REFUTED by direct measurement

The premise behind "finer granularity is noisier" is that per-coordinate meta-gradients are
near-independent, so pooling N of them shrinks drift as 1/sqrt(N). The probe measures the
premise directly:

> **53.1% of all 11,173,962 per-weight meta-gradients agree on sign.**
> Independence would give 50.0000 ± 0.0015%.

Predicted log-log slope of drift vs N: **−0.500**. Measured: **−0.113**.

The signs are strongly positively correlated, so a pooled estimate does not average toward zero —
it converges to a population bias. **Drift is governed by how much the coordinates agree, which
is a property of the partition, not by N through a sampling-noise channel.** This is the
within-block correlation the prior-art sweep identified as the one unclaimed empirical
contribution available here, and it is now measured rather than assumed.

### 8c. The alpha0 confound is quantified, and it accounts for the short-budget orderings

Pooled layerwise is 17.6pp *behind* scalar at 20 epochs and 4.5pp *ahead* at 100. The 20-epoch
ordering is fully explained by startup cost: beta must climb 6.9 log units from ln(1e-6) before
alpha is useful, and the arms escape at different rates —

| arm | epochs merely to reach a useful alpha |
|---|---|
| scalar | 13.8 |
| 6-block | 14.0 |
| layerwise | 17.3 |
| nodewise | 25.1 |

**A substantial part of what earlier tables called "the granularity effect" at short budgets is
the arms escaping a deliberately crippled initialisation at different rates.** Every
short-budget comparison at alpha0 = 1e-6 must be read with this in mind, and the alpha0 control
runs are the correct basis for any steady-state claim.

## 9. Fixes applied this round
* `analysis/aggregate.py` now emits **plateau** (mean of last 5 epochs) as primary, plus
  `ep_to_85/88/90` and guard/hier/lambda/eta_ratio provenance. Measured: best-of-run inflates
  over plateau by **0.37pp median** across 356 runs — the same order as the effects claimed.
* **Non-meta baseline launched** — plain AdamW at 4 fixed learning rates x 2 seeds. Across the
  first 275 runs there was *not one* non-meta-learned optimiser to compare against; a reviewer
  would have asked immediately.
* **Seeds raised to 5** on the 300-epoch headline cells (plain / zpool r=0.1 / scalar).

---

## 10. §8a pooled two meta-optimizers; the optimum survives, the table did not

Re-deriving §8a from `results/all_runs.csv` (rule 1) showed its cells were not homogeneous.
Two different run families were being averaged together:

* `ad-l-*` — `--alg-meta Lion`, account `s5014158`
* `adg-A-*` — `--alg-meta Adam`, account `salehkaleybars`

The Adam family sits ~1.3pp lower at matched `r`. The pooling was **unbalanced across the
sweep**: r=0.05 and r=0.07 contain Lion runs only, while r=0.03 and r=0.1 mix in Adam runs.
That pulled the shoulder cells down and the peak cells not at all — i.e. the pooling
manufactured part of the contrast it was being used to demonstrate. This is the same
failure mode as §3 (reporting a heterogeneous max), one level further down.

### The corrected table — one meta-optimizer, one account

`hier=additive`, `granularity=layerwise`, 100 epochs, plateau (mean of last 20 epochs),
`superseded==0`, `--alg-meta Lion`, account `s5014158`:

| r | n | plateau | sd | Δ vs r=0 |
|---|---|---|---|---|
| 0 | 3 | 92.20 | 0.04 | +0.00 |
| 0.03 | 5 | 92.64 | 0.16 | +0.44 |
| 0.05 | 5 | 93.09 | 0.10 | +0.89 |
| **0.07** | **5** | **93.22** | **0.14** | **+1.02** |
| 0.1 | 5 | 92.63 | 0.21 | +0.43 |
| 0.2 | 3 | 91.39 | 0.14 | −0.81 |
| 0.3 | 3 | 90.96 | 0.08 | −1.24 |

**The interior optimum is real and is now cleaner than the pooled version.** Stratifying
turns the ragged 92.15 / 92.14 / 93.06 opening of the old table into a monotone rise to a
peak at r=0.07 and a monotone fall after it. The effect at the peak is +1.02pp against a
per-cell sd of 0.04–0.21, so it is 5–25x the noise. What changed is the shape's credibility,
not its existence.

Corrections to the individual cells of §8a: r=0.03 was 92.14, is **92.64**; r=0.1 was 92.28,
is **92.63**; r=0 was 92.15 at n=5, is **92.20 at n=3**; r=0.05 was 93.06 at n=7, is **93.09
at n=5**. The inflated n came from counting the pooled Adam runs.

### The generalisation claim is not yet testable — meta-optimizer is confounded with account

Every Lion additive run is on `s5014158`; every Adam additive run is on `salehkaleybars`. The
1.3pp gap is therefore **not attributable to the meta-optimizer** — it could equally be a
difference in the two accounts' code or environment state. Nothing about "the optimum is
Lion-specific" can be read off the current data.

Worse, the Adam arm has **no r=0 anchor at all**, so it has no within-arm baseline and cannot
show an interior optimum even in principle. That is why its Δ column is empty above.

**Launched this round to break it:** `amx-r{0,05,07}-s{0..4}` — 15 jobs, Adam meta, layerwise,
100 epochs, n=5, submitted on `s5014158`, the *same* account as the Lion sweep and identical
to it in every argument except `--alg-meta`. Reading the result:

* rises ~92.2 → ~93.2 → the optimum generalises across meta-optimizers, and the old 1.3pp gap
  was the account, not the method
* stays ~1.3pp low but still inverted-U → the optimum generalises; the offset is the
  meta-optimizer
* flat → the optimum is Lion-specific, and the headline result needs that caveat in the paper

Any of the three is publishable; the current state, which cannot distinguish them, is not.

## 11. Two aggregator bugs found and fixed

**`account` was wrong on every row.** It was inferred from `"/home/s5014158" in path`, which
holds on the cluster but not in the local backup, where alice2's runs sit under `runs_alice2/`.
All 428 rows read `salehkaleybars`, so *any* per-account analysis was void — including the
confound check in §10, which is why that confound went unnoticed until now. It now reads the
recorded `--save-directory`, which travels with the artefact, and falls back to the path.
Corrected split: 263 `salehkaleybars` / 165 `s5014158`.

**`run` is not a unique key.** A resubmission reuses `--run-name`, so a finished run and an
in-flight one can share a name; any analysis keying a dict on `run` silently keeps whichever
was parsed last. Three completed 100-epoch alpha0 controls (`a0-{scal,layer,blk6}-1e4_s0`,
plateau 91.75 / 92.05 / 91.75) were being shadowed by 30-epoch reruns this way — the partial
value would have replaced the real one in any downstream table. The CSV now carries
`dup_group` and `superseded`, aggregate.py warns on stderr, and **every analysis must filter
`superseded == 0`**.

### Housekeeping in the same pass
* **12 redundant jobs cancelled** on `s5014158`. The whole queued `a0-*` batch (2 alpha0
  values x 3 granularities x 2 seeds) re-ran configurations that had *already completed* at
  100/100 epochs; each was verified against its finished counterpart before cancelling
  (argument lists identical up to flag order, ENV lines identical). They were consuming 4
  running GPU slots and would have created 12 further run-name collisions.
* **13 pending jobs widened** on `salehkaleybars`. A blanket widen fails on the 6-hour
  300-epoch arms with "Requested time limit is invalid" — `gpu-short` caps at 4h. Those 9 go
  to the four 7-day GPU partitions only; `bin/widen_long.sh` now branches on the job's own
  time limit.

### A documentation mismatch, resolved in favour of the code
`plateau` in the CSV is the mean of the **last 20 epochs**, but §4 and §9 of this document,
`PLAN.md` and `PLAN-appendix-research.md` all describe it as the mean of the last 5. The
20-epoch window is what every number in this repo actually is. Checked rather than assumed:
recomputing the whole M1 sweep at k=5 moves no cell by more than 0.15pp and leaves the peak at
r=0.07, so no conclusion depends on the choice — but **the prose is what is wrong, not the
code**, and it should be corrected to "last 20 epochs" wherever it appears.

## 12. The sign-agreement headline is measured in the regime Rule 5 warns about (cycle 18)

`runs/bdrift3/p3-*` — cycle 7's own α₀=1e-3 control for the β-drift/sign-agreement probe — had
been sitting in this repo unreduced since it ran. Reduced now with the published methodology
(drift = |Δβ̄|/step over steps 1000–7500, `frac_neg` averaged over the same window).

**What survives.** The √N noise model predicts a log-log drift-vs-N slope of −0.500. Measured
**−0.110 at α₀=1e-6 and −0.136 at α₀=1e-3**. The refutation holds in *both* regimes and is now
robust to the α₀ confound rather than merely asserted against it. This remains the campaign's
most defensible result.

**What must be qualified.** Weightwise sign-agreement (excess over a balanced split,
|2·frac_neg − 1|) is **6.20% at α₀=1e-6 and 0.38% at α₀=1e-3 — a 16× collapse.** Much of the
"coordinates strongly agree" reading is the shared climb out of a 7-log-unit hole: coordinates
being driven the same way by a bad init agree trivially. At steady state the excess is 0.38%,
which over 11.17M coordinates is still **+12.7σ** from independence — genuinely non-independent,
but a *small* bias, not a strong one.

> **The "53.1% of 11.17M meta-gradients agree on sign" number is an α₀=1e-6 measurement and
> must never be quoted without that qualifier.** At the steady-state control it is 50.19%.

**What is withdrawn.** Cycle 6 predicted and cycle 7 marked **CONFIRMED** that "drift falls
monotonically with N". At α₀=1e-3 it does not: scalar 3.04e-4 > nodewise 1.84e-4 > layerwise
1.57e-4 > 6-block 1.03e-4 > weightwise 1.70e-5. Monotonicity is an α₀=1e-6 artefact; only the
endpoints (scalar highest, weightwise ~18× lower) survive at both α₀.

**Also corrected:** ResNet18 `nodewise` N has been recorded as "~4,800" since cycle 7. Measured
by direct instantiation it is **14,420**. Refitting the slope with the corrected N moves it from
−0.1130 to −0.1095 — immaterial, but the wrong N should not be re-quoted. Full N ladder for all
four architectures is in FINDINGS cycle 18 §2.

**Process note (Rule 1, third occurrence).** The refuting artefact was already in the repo. The
first two occurrences were controls that sat unread; this one was a control that *was
deliberately submitted for exactly this purpose* in cycle 7, completed, and then was never
reduced. Reducing every probe dir that exists should precede submitting new ones.

---

## 13. The M1 pooling baseline was the wrong endpoint (cycle 20)

**What was wrong.** Cycles 16–19 quoted the M1 additive-pooling gain against `r=0`, describing
it as the no-pooling control — e.g. "interior optimum r ≈ 0.05–0.07, plateau 93.06–93.22 vs
**92.15 at r=0**".

**What the code actually does.** `patches/HF_patched.py::_apply_hier`, additive branch:

```
d    = beta - beta_prev
dm   = d.mean()
beta = beta_prev + dm + r*(d - dm)
```

`r` is the **retention of the group-specific part of the update**. At `r=1` the expression
telescopes to `beta_prev + d = beta`, the exact identity — **plain layerwise**. At `r=0` every
group takes the mean update — **full pooling**. So `r=0` is the *maximally pooled* extreme and
was being used as the *un*-pooled baseline.

**Structural verification** (not asserted from the algebra — measured, per Rule 4).
ResNet18/CIFAR-10, α₀=1e-6, plateau, `epochs_done>=100`:

| arm | n | plateau |
|---|---|---|
| additive r=1 | 3 | 90.863 ±0.063 |
| plain layerwise, `HIER` unset | 47 | 90.891 ±0.492 |

0.028pp apart — inside the ±0.02–0.05pp reproduction band.

**Effect on the claims.** No run changed and no measurement was wrong; only the baseline was
misnamed. The corrected headline is **larger**, not smaller:

| | old phrasing | corrected |
|---|---|---|
| ResNet18/C10, α₀=1e-6, r*=0.06 | +1.07pp "vs r=0" | **+2.40pp vs no pooling (r=1)** |
| | | (+1.07pp vs full pooling, r=0) |

The curve is unimodal with **both** endpoints now measured, which is a better result than the
one it replaces. What it costs is transferability: the ResNet10 ladder, read correctly, is
+1.00pp rather than the +8.7pp that "vs r=0" implied, and on CIFAR-100 the same r is
**−43.7pp**.

**Process note (Rule 4, second occurrence).** The first occurrence was a pooling identity that
was never checked at all. This one is worse: a check *existed* — `drift_extract.py` printed a
`spread` column advertised as verifying that pooled arms carry one step size — but it read
`beta_true_max − beta_true_min`, two probe fields that are written **identically on every arm**.
It reported 0.0000 by construction and could never have failed. A verification that cannot fail
is worse than no verification, because it is recorded as evidence. Replaced by `sd_beta` in
`bin/drift_extract2.py`.
