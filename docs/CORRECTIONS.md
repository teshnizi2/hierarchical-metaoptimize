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

---

## 10. The baseline comparison was NOT fair, and three experiments now fix it

Reported "MetaOptimize loses to tuned AdamW+cosine by 1.41pp." That comparison had three
structural flaws, all favouring the baseline. None invalidate the measurement; all mean it was
the wrong measurement to draw a verdict from.

### Flaw 1 — budgets were not matched
Meta arms were compared at 100 epochs against a baseline measured only at 100 epochs, while the
300-epoch meta data (93.47) was compared against the *100-epoch* baseline (94.24). MetaOptimize
optimises a **discounted sum of future losses with gamma -> 1**; it is built for the long run, so
100 epochs is the regime least favourable to it. The cosine baseline additionally **knows the
horizon** (`COS_TOTAL`) and anneals onto it — information MetaOptimize is deliberately denied.
**Running:** baseline vs best meta config at 300 and 600 epochs, budget-matched cosine, n=3.

### Flaw 2 — search budgets were not matched
The baseline consumed a 4-point LR sweep; each meta arm got a single run. **MetaOptimize's
actual claim is that it needs no tuning**, so comparing its one run against the best of four is
rigged on precisely the axis the method exists to address. The honest comparison is *expected
accuracy per unit of total compute*: for the baseline that is best-of-K LRs, for MetaOptimize it
is the typical (not best) result over K seeds.
**Running:** cosine LR sweep over 7 decades x 3 seeds, to characterise what an *untuned* choice
actually costs.

### Flaw 3 — we never ran the paper's own setup
All our runs enable augmentation. The parent paper never mentions augmentation and its released
code has none. Augmentation was the scientifically correct call (unaugmented ResNet-18 memorises
CIFAR-10 in epoch 1), but it means **we have never reproduced their claim in their setting** and
cannot answer a reviewer who asks whether it holds there. Their evidence is Fig. 1 *learning
curves*, so the comparison must be on convergence, not the endpoint.
**Running:** paper config (AdamW base + Adam meta, alpha0=1e-6, eta=1e-3, gamma=1), **AUGMENT=0**,
scalar vs 6-block vs layerwise, n=3.

### Standing rule
**Never report a comparison until budget, search budget, and setup are all matched — or until
each mismatch is stated in the same breath as the number.** Two of these three flaws were caught
by the operator, not by us.

---

## 14. The config key omitted `granularity`, and a "logging gap" was invented to explain it (cycle 25)

**What was wrong.** Cycle 24 (FINDINGS 24.1) recorded, as the campaign's "highest-value
integrity item":

> **Unresolved anomaly:** `ad-l` (92.626, n=5) and `adg-b` (91.598, n=3) agree on *every*
> recorded field yet differ by **1.03pp**, ~50x the +-0.02pp reproduction tolerance. Something
> that determines a 1pp effect is not being logged.

**What is true.** They do not agree on every recorded field. They differ in
`--stepsize-groups` — `layerwise` vs `resnet18_blocks` — which is in the ARGS line of both
`.out` files and in the `granularity` column of both CSV rows. The aggregator was correct.
Cycle 24's *analysis* grouped by an 8-field key that left out `granularity`, the single most
important field in the project, and so pooled two granularities into one cell.

**Effect on the claims.** The r=0.1 cell of the M1 ladder goes from 92.240 +-0.556 (n=8,
two granularities) to **92.626 +-0.214 (n=5, layerwise only)** — sd down 2.6x. The peak cells
(r=0.05/0.06/0.07) contained no 6-block runs and are unchanged. The curve is now monotone on
both sides of r=0.06. Nothing about the interior optimum changes; one ragged cell becomes clean.

Discharged: 24.1's standing caveat that "the r=0.1 cell stays heterogeneous until this is found."

**Rule amended.** The canonical config key is **nine** fields:
`network, dataset, batch_size, base, meta, meta_stepsize, alpha0, gamma, augment, beta_clip,
epochs_requested, granularity, hier, eta_ratio, lam` — and `granularity` is never optional.

**Process note.** The failure mode is new and worth naming separately from Rule 1. Rule 1 says
re-derive numbers from the CSV; this *was* re-derived from the CSV. The defect was in the
**grouping**, and the symptom — an unexplained gap between two supposedly-identical cells — was
attributed to the instrument (a missing log field) rather than to the analysis. **When two cells
that "should" match do not, check the grouping before concluding the data is incomplete.** The
raw artefacts answered it in one diff.

---

## 15. `_zpool`'s pooling parameter is not comparable across granularities (cycle 25)

**What was wrong.** The zpool sweep has been read across granularities as though its `r` meant
the same thing at each — e.g. comparing the layerwise and weightwise r-curves directly.

**What the code does.**

```
_zpool:            z'_b = (1-r)*SUM(z)  + r*z_b          <- SUM, scales with m
_zmpool:           z'_b = (1-r)*MEAN(z) + r*z_b          <- MEAN, m-invariant
_apply_hier (M1):  beta_prev + MEAN(d) + r*(d - MEAN(d)) <- MEAN, m-invariant
```

`_zpool`'s pooled term scales with the group count m, so the scalar->plain transition is
compressed against r=1 by a factor of m. Its **endpoints remain exact** and are verified
(FINDINGS 25.4: r=0 reproduces plain scalar to 0.009-0.032pp, r=1 reproduces plain to
0.099-0.149pp, at both layerwise and weightwise). Only the path between them is m-dependent.

**Consequence.** At weightwise (m=11.17M) the region equivalent to layerwise's interesting
r in [0.9, 1] sits at `1-r ~ 5e-8`, **below float32 eps (1.19e-7)**. `_zpool` cannot express
weak pooling at weightwise. The entire 11.13pp weightwise transition is squeezed into the two
measured cells r=0.99 and r=1, and its optimum is unlocated.

**What survives.** M1 (`additive`) and `_zmpool` are both mean-based, so *their* `r` is
comparable across granularities. Every cross-granularity pooling claim must use one of those
two operators, never `_zpool`. FINDINGS 25.3 (M1) and the `zmg-*` batch (zmpool) are built on
that basis.

## 16. `block_sizes.json` reports the wrong coordinate count for nodewise (cycle 26)

`HF._probe_init` builds `n_b` with an if/elif over `layerwise` / `scalar` / `blockwise` and
falls through to `nb = self.param_numels` for **everything else** — which lumps nodewise in
with weightwise. So for a nodewise arm `block_sizes.json` records **11,173,962** coordinates
when the arm actually has **14,420** nodes.

Nothing in the record flags this, and the wrong number is silently plausible. Any significance
statement about nodewise sign-agreement computed against `block_sizes.json` overstates its
z-score by `sqrt(11173962/14420)` = **27.8x**.

**The count is recoverable and must be recovered, not trusted.** `frac_neg` is a rational
`k/n_tot`, so the smallest denominator consistent with the observed fractions IS `n_tot`.
Verified against independently recorded counts:

| arm | inferred `n_tot` | independently recorded |
|---|---|---|
| `probe_sig_resnet18_blocks_s0` | 6 | 6 blocks |
| `probe_sig_layerwise_s0` | 62 | 62 layers |
| `probe_sig_nodewise_s0` | **14,420** | 14,420 nodes (25.3) |
| `probe_sig_weightwise_s0` | 11,173,962 | 11.17M params (25.3) |
| `p5-r34-w` | 21,282,122 | ResNet34 = 21.3M |

All five match. `bin/agree2.py` infers `n_tot` this way and never reads `block_sizes.json`.

**Standing rule:** a probe field that was *derived* at write time (group counts, block sizes,
`beta_true_min/max`) is a claim, not a measurement. Re-derive it from the raw record before
using it in a significance statement. This is the same defect class as `drift_extract.py`'s
`spread` column — a verification that could not fail — and as the `collapsed` column, which is
`0` on every row.

## 17. `drift/step` is censored by Lion's sign update, and two published slopes sit on the ceiling (cycle 26)

The meta-optimizer is **Lion**, whose update is `sign(...) * lr`. So `|d beta|` per step is
EXACTLY the meta-stepsize (1e-3), and therefore

```
drift/step  <=  meta_stepsize            (hard ceiling, not an empirical bound)
drift/step / meta_stepsize  =  net temporal sign-consistency of the meta-gradient
```

`p4-r10-scal` and `p4-c100-scal` both read **exactly 1.000e-03** — pinned at the ceiling, i.e.
the scalar step size moved in one direction on every single step. A censored point cannot
carry a regression, but both were included in the published log-log fits.

Refitting the `p4scale` drift-vs-group-size slopes without the saturated arm:

| setting | published (all 4) | unsaturated | R^2 all 4 -> unsat |
|---|---|---|---|
| ResNet10 / CIFAR-10 | +0.238 | **+0.177** | 0.68 -> 0.41 |
| ResNet18 / CIFAR-100 | +0.290 | **+0.150** | 0.36 -> **0.08** |
| ResNet34 / CIFAR-10 | +0.205 | +0.205 (none saturated) | 0.70 -> 0.70 |

**What survives:** the sqrt(N) refutation. The slope is POSITIVE in 6/6 fits across two
alpha0 (`p4scale` 1e-3, `p5scale` 1e-6) and three settings, where the model requires -0.500.
A sign inversion that robust does not depend on one censored point.

**What does not survive:** the slope magnitudes as point values, and the CIFAR-100 / a0=1e-3
cell as evidence of a *trend* at all — its R^2 falls to 0.08 once the ceiling point is
dropped. Quote the slopes as a positive range, and normalise drift by the meta-stepsize.

## 18. `z_mean` is not the meta-gradient whose signs make `frac_neg` (cycle 28)

**What was nearly claimed.** `gate1` (alice, Aug 18) is field-for-field identical in its ARGS
line to `mx/probe_sig_*`, the series 26.3's published sign-agreement ladder is built from —
same base, meta, momenta, weight decay, meta-stepsize, alpha0, network, dataset, batch size,
epochs, seeds. It had never been reduced. The obvious move was to reduce it and report it as
an independent n=3 replication of the published ladder.

**Why that is wrong.** `gate1` predates the probe's `frac_neg`/`frac_zero` fields. Its records
carry `beta`, `z_mean`, `z_std`, `snr` only. A reducer built to recover agreement from
`sign(z_mean)` (`analysis/agree_legacy.py`) was validated against `mx`, which carries BOTH
formats — same records, same window, same code path — and disagreed:

| rung | `frac_neg` (agree2.py) | `z_mean` (agree_legacy.py) | delta |
|---|---|---|---|
| resnet18_blocks (m=6) | 70.87±0.80 | 63.70±0.78 | **−7.17** |
| layerwise (m=62) | 53.26±0.19 | 54.77±1.26 | +1.51 |

`z_mean` is a per-TENSOR running mean: it has 62 entries on EVERY arm, including the
14,420-node and 11,173,962-weight arms, whose true coordinate counts `agree2.py` infers from
the `frac_neg` denominators. It is a different quantity at a different resolution, and its
disagreement is 7pp — roughly the size of the whole m=6-to-m=62 fall the ladder reports.

**The rule.** Any probe directory whose records lack `frac_zero` is on the LEGACY statistic.
Its numbers may be compared to other legacy numbers and to nothing else. `agree_legacy.py`
prints the same column layout as `agree2.py` on purpose, which makes the two easy to paste
into one table — do not. This is the second time a probe field has looked interchangeable and
was not (see CORRECTIONS 16 on `block_sizes.json`'s `n_b`).

**What survives.** Within the legacy statistic, read consistently, `gate1` reproduces `mx` to
0.055pp (m=6) and 0.083pp (m=62) — a genuine cross-batch reproducibility result (28.3) — and
`gate2` vs `gate1` is a like-for-like base-optimizer contrast (28.4). Neither may be placed on
26.3's table.

**Also recorded:** `gate3` (SGDm base, meta Adam, no beta clip) is DIVERGENT — `sd_beta` 20.5
in log space against `mx`'s 2.39 — and its `z_mean` agreement pins at exactly 100.0000% on all
three seeds at m=6. It is excluded from every agreement claim rather than reported as a low
outlier.

## 19. `agree2.py` censored every coordinate count above 20,000,000 (cycle 29)

`infer_ntot` recovered the coordinate count as the denominator of the observed `frac_neg`
rationals:

```python
best = max(best, Fraction(v).limit_denominator(20_000_000).denominator)
```

**The 20,000,000 is the tool's ceiling, not the model's.** Any arm with more coordinates than
that is reported AT the ceiling, silently.

Measured this cycle on `p7-*`: ResNet34/weightwise has **21,282,122** coordinates — summed
directly from `block_sizes.json`'s `n_b` over its 110 tensors, which for *weightwise* is the
one thing that field is reliable for, since weightwise groups ARE the parameters (contrast
CORRECTIONS 16, where the same field is wrong by 775x for nodewise). `agree2.py` reported
exactly `20,000,000`.

**What it corrupted.** The independence null is `E = 0.5 + sqrt(2/pi) / (2 sqrt(n))`, so a
censored `n` gives a null that is too HIGH and an excess-over-null that is too LOW:

| | reported n | null% | R34/weightwise excess (s1, s2) |
|---|---|---|---|
| before | 20,000,000 | 50.00892 | 0.0029, 0.0038 |
| after | 21,282,122 | 50.00865 | 0.0033, 0.0052 |

~10–35% relative on the affected cells. **No sign flipped and no ordering changed**, so
29.1's ladder is unaffected in shape — but the numbers published before this cycle for any
arm above 20M coordinates were wrong.

**Fixed** by raising the cap to `100_000_000` (`bin/agree2.py`; backup `bin/agree2.py.bak`).
Verified unaffected because they sit under the OLD cap and reproduce exactly: ResNet18
11,173,962 / ResNet10 4,903,242 / ResNet18_c100 11,220,132.

**The rule.** `infer_ntot`'s cap must exceed the largest arm's parameter count with margin.
Check it before adding any architecture above ~20M parameters — ResNet50 (25.6M) and
anything larger would be censored at the current 100M only above 100M, but the failure is
silent either way. Cross-check `infer_ntot`'s answer against `sum(block_sizes.json["n_b"])`
on every new weightwise arm; they must agree exactly.

This is the third defect in the coordinate-count layer (16: `n_b` wrong for nodewise; 17:
Lion sign-censoring of `drift/step`; 19: this). **Every one of them was silent and every one
of them moved a published number.**

## 20. Reducing an in-flight probe returns a moving number (cycle 29)

`agree2.py`'s STEADY window is "the last 50% of the records that exist", so a probe read at
89 records and again at 100 reports two different steady states. Measured on `p7-r34-lay-s1`:

| records | sys% | step% | excess |
|---|---|---|---|
| 89 | 51.4962 | 54.7917 | 0.9879 |
| 100 | 51.6727 | 55.2727 | 1.4690 |

A 49% change in the headline statistic, from nothing but reading it early. The `.out` file
shows 0 epochs while a job runs (stdout buffering), so an in-flight probe does not announce
itself the way an in-flight training run does.

**The rule.** Tabulate a probe only at its full record count — `PROBE=100` over 20 epochs
gives exactly **100 records, last step 9900**. Gate on `wc -l probe.jsonl` equal to the
expected count, exactly as the run tables gate on `epochs_done >= 100`. Cycle 29's 29.1
tabulates 24 of 32 `p7` dirs for this reason; the other 8 were at 49–96 records.

---

## 21. M1's `r` dial changes the meta-step-size as well as the pooling (cycle 33)

**What was wrong.** Two claims, both carried in `CONTINUE-HERE.md` and both built on reading
`additive` r=0 as a controlled full-pooling baseline:

1. "even full pooling helps (+1.39pp)" — CIFAR-10/ResNet18.
2. CORRECTIONS 13's framing that `r=0` is "the *maximally pooled* extreme", used as the
   endpoint against which the M1 curve is reported.

**What the code actually does** (`HF.py:265-293`, additive branch):

```
d    = beta - beta_prev          # realised Lion increment, |d_b| == ms EXACTLY
dm   = d.mean()                  # == ms*(2p-1),  p = fraction agreeing in sign
beta = beta_prev + dm + r*(d - dm)
```

CORRECTIONS 13 is right that r=0 gives every group the same increment. It is wrong that this
is a *controlled* baseline. Because Lion's increment has constant magnitude `ms`, averaging the
increments shrinks the shared step's advance to `ms·|2p−1|`. Moving r from 1 to 0 therefore
does two things at once: it pools the groups **and** it divides the meta-step-size by
`|2p−1|`. At layerwise `frac_neg` = 0.5484 → `|2p−1|` = 0.0968, a **10.3× reduction**.

**Structural verification** (measured, per Rule 4 — the r=0 endpoint that CORRECTIONS 13
inferred but never checked). A true full-pooling arm collapses every partition to one step
size, so its score cannot depend on the partition:

| granularity | m | `additive` r=0 | `zpool` r=0 |
|---|---|---|---|
| `resnet18_blocks` | 6 | 91.767 ±0.042 | — |
| `layerwise` | 62 | 92.587 ±0.674 | 87.740 ±0.138 |
| `nodewise` | 14,420 | 91.984 ±0.103 | — |
| `weightwise` | 11,173,962 | 45.005 ±2.603 | 87.763 ±0.036 |
| plain `scalar` reference | 1 | — | 87.772 ±0.139 |

`zpool` r=0 is granularity-invariant to **0.032pp** across 180,000× in m. `additive` r=0 spans
**47.582pp**. Probe evidence: `runs/zb/probe_zb-{l,w}-r0` show `z_mean` identical across all
reported tensors; `zb-l-r1` and `zb-plain` agree on `frac_neg` = 0.5483870967741935.

**Effect on the claims.**

| claim | status |
|---|---|
| "even full pooling helps (+1.39pp)" | **REFUTED.** True full pooling is −3.044pp vs plain layerwise. |
| M1 interior optimum, layerwise, +2.359pp vs r=1 (n=10) | **stands as an empirical curve**; its mechanism is not pooling |
| M1 interior optimum, nodewise, +1.140pp vs r=1 (n=3) | as above |
| 26.3's search for an agreement→gain mechanism | **explained as a confound.** The M1 gain depends on agreement because the effective meta-step-size is `ms·|2p−1|`. |
| CORRECTIONS 15's "cross-granularity pooling claims must use `additive` or `zmpool`" | **amended.** `additive`'s r is m-comparable as a formula, but its effect is dominated by the meta-LR rescaling, so it is not a pooling operator at all. |

**What decides it.** `ms-*` (52 jobs, cycle 33): a meta-step-size sweep on plain `scalar` and
plain `layerwise`. Pre-registered — if `scalar` at ms=1e-4 reaches 92.2–92.6, the whole M0/M1
family is meta-LR tuning and granularity contributes nothing to the win.

**Process note (Rule 4, third occurrence).** The first occurrence never checked the identity;
the second checked it with a statistic that could not fail; this one checked **one endpoint of
two** and inferred the other from algebra that was locally correct. The general lesson: verify
a dial at *both* extremes, and for an invariance claim, vary the thing the invariance is over —
here, the granularity.

---

## 22. The `weightwise` `additive` r=0 collapse is NOT explained by shared-term travel (cycle 34)

**The tempting sentence.** "At `weightwise`, `additive` r=0's shared step size advances at
`ms`·|2p−1| = 3.307e-7, so over 50,000 steps β travels 0.017 in log-space against the
ln(0.05/1e-6) = 10.82 it needs to escape a0=1e-6 — hence the 45.005 plateau."

**Why it is wrong.** The same arithmetic, run across the granularity ladder (FINDINGS 34.6,
startup window weighted in), predicts `nodewise` cannot escape either — β travel **1.31** vs
10.82 required — when `nodewise` plateaus at **91.984 ±0.103 (n=3)**. The model is refuted by
a case it gets backwards, not by a marginal one.

**What is actually going on.** CORRECTIONS 21 / FINDINGS 33.4 already established that
`additive` r=0 is **not** exact full pooling: it spans 47.582pp across granularities where true
`zpool` r=0 spans 0.032pp. Its pooled term is an **offset added to** each group's own update,
not a constraint replacing it. Every group's individual component still moves at ±`ms` per step
(travel 50 over a 100-epoch run) and can escape on its own. `weightwise` fails for a different
reason: at `step%` = 50.0165 against a 50.0119 null, each group's own meta-gradient is
statistically indistinguishable from noise, so β **random-walks** (RMS 1e-3·√5e4 = 0.22)
instead of drifting.

**Effect on the claims.**

| claim | status |
|---|---|
| `weightwise` `additive` r=0 = 45.005, "β cannot escape a0=1e-6" | **the number stands; the shared-term-travel explanation is REFUTED** |
| FINDINGS 33.4 "|2p−1| falls with m, so `additive` r=0 shrinks the meta-step further at finer partitions until β cannot escape" | **first clause verified (34.2), second clause REFUTED as the mechanism** |
| FINDINGS 34.3's `ms_eff` collapse curve | **stands** — it is a statement about where the five arms land, not about why weightwise dies |

**Process note (Rule 4 again).** The refuted model was checked at both *ends* of the ladder
(blk6 escapes ✓, weightwise does not ✓) and passed. It failed only at an **interior** rung.
Verifying a monotone mechanism at its two extremes is not verification — the interior is where
a wrong monotone story shows itself.

## 24. "Granularity contributes 0.04pp" (FINDINGS 38.1) — WRONG, it is +0.617pp

**Claimed (cycle 38):** at a0=1e-3, plain `scalar` with ms tuned to 1e-4 (92.405 ±0.071, n=2)
matches the best hierarchical arm (`additive` r=0.1 at ms=1e-3, 92.449 ±0.192) to 0.044pp, so
the hierarchy's only contribution is dividing the meta-step by ~10.

**Measured (cycle 39):** the comparison was not ms-matched. It put the scalar arm at *its* tuned
meta-step and the layerwise arm at ms=1e-3. With `ms-layA-1e4` complete, the 2x2 at n=3 reads:

| | ms=1e-3 | ms=1e-4 |
|---|---|---|
| scalar | 87.884 ±0.243 | 92.255 ±0.264 |
| layerwise | 91.176 ±0.148 | **92.872 ±0.041** |

**Granularity at the tuned meta-step is +0.617pp, Welch t=4.00.** It survives. What is true is the
weaker claim: **81% of the apparent granularity gain (+3.291 → +0.617) is meta-step tuning.**

**Also corrected:** the scalar cell was n=2 in 38.1; seed 2 completed at 91.956 and moved it from
92.405 ±0.071 to 92.255 ±0.264.

**What survives from 38.1:** `additive` pooling is **strictly dominated** — plain layerwise at a
tuned meta-step (92.872 ±0.041) beats the best pooled arm (92.449 ±0.192) by +0.423pp. Pooling is
a worse route to a small effective meta-step than choosing one.

**Process note.** 38.2 *itself* named `ms-layA-1e4` as the cell that could overturn 38.1, and 38.1
was written anyway. A conclusion must not be stated in the same cycle that its own text identifies
the deciding experiment as unrun. **Name the missing cell, then wait for it.**

## 25. "The baseline LR peak is an interior maximum at 1e-3" (FINDINGS 38.5) — WRONG

**Claimed (cycle 38):** `bl-adw-1e-2` (92.728) brackets the baseline peak from the right, so
1e-3 (94.093) is an interior maximum and cycle 36's grid-censoring objection is answered.

**Measured (cycle 39):** with 2e-3, 3e-3 and 5e-3 in hand, AdamW+cosine peaks **flat over
2e-3–3e-3 at ≈94.39**, +0.33pp above the 1e-3 cell. The grid was still censored; 1e-3 was still
on a rising edge.

**Cost of the error:** every deficit computed against 94.093 understates the gap. With the true
best non-meta baseline — **SGD-momentum + cosine at lr=0.03, 94.767 ±0.097 (n=5)** — the deficit
against the best MetaOptimize arm (93.306 ±0.140) is **1.461pp, not 0.787pp.**

**Process note (Rule 3, restated).** One bracketing point on one side does not locate a peak. A
maximum may be called interior only when the cells *adjacent to the argmax on both sides* are
measured — not merely when some point further out is lower.

## 26. "53.1% of 11.17M per-weight meta-gradients agree in sign (independence = 50.0000 ±0.0015%)" — a conflation of two arms, and the null is wrong (cycle 42)

**The sentence in circulation** (used to justify making the sign-agreement measurement the
project) puts the 53.1% figure and the 11.17M coordinate count in the same claim. They come
from different arms, and the quoted null belongs to neither.

**What the data says** (`analysis/killtest_idea2.py`, reproduction check on `mx/probe_sig_*`,
steady window, n=3):

| arm | m | measured agreement | its own independence null | excess |
|---|---|---|---|---|
| layerwise | 62 | 55.85% | **55.07%** | +0.79pp |
| nodewise | 14,420 | 51.18% | 50.33% | +0.85pp |
| **weightwise** | **11,173,962** | **50.028%** | **50.012%** | **+0.016pp** |

* **53.1% is the layerwise arm's system-level figure (m=62), not a per-weight one.** The
  weightwise arm reads 50.005–50.028%.
* **The null is not 50.0000%.** The cross-sectional majority statistic max(p, 1−p) has
  expectation 0.5 + √(2/π)/(2√n) under independence — 55.07pp at n=62, 50.012pp at n=11.17M.
  Quoting 53.1% against a 50.0000% null reports an arm that is **1.9pp BELOW its own floor**
  as if it were 3.1pp above it. CONTINUE-HERE's cycle-26 table (53.26 / 50.0053) had the two
  arms right; the damage was done when they were merged into one sentence.
* The honest per-arm statement is the *excess over that arm's own floor*, and the honest
  cross-arm statement is the effective sample size (FINDINGS 42.4), which is scale-free.

**Effect on the claims.**

| claim | status |
|---|---|
| "53.1% of 11.17M per-weight meta-gradients agree in sign" | **REFUTED as stated.** Two arms merged; the weightwise value is 50.028%. |
| "independence = 50.0000 ±0.0015%" | **WRONG.** The null for this statistic is n-dependent; at m=62 it is 55.07%. |
| "the 1/√N assumption is refuted" | **survives, but only off-equilibrium** — see FINDINGS 42.4, and see CORRECTIONS 27 for the sign of the correction. |

**Process note (Rule 3).** Both numbers were individually correct in FINDINGS. The error was
introduced by summarising them into one sentence in a handoff document, and that sentence then
selected the project's direction for two cycles. **A summary line that merges two rows of a
table must carry the row labels.**

## 27. The direction-C headline points the wrong way: adaptation RESTORES the 1/√N assumption (cycle 42)

**The premise the project was steered on.** "The 1/√N noise-averaging assumption that
justifies coarse granularity across the Adam-mini / Adalayer / SGG literature is
quantitatively false; nobody in that line has measured it."

**What the controlled measurement shows** (FINDINGS 42.4). The exponent s in N_eff ~ m^s,
where s=1 is exactly the independence assumption, on two batches identical in every field
except `--alg-meta`:

| design | s | n |
|---|---|---|
| β frozen (`fz-*-a3`) | **0.629 ±0.013** | 5 |
| β free (`p7-r18-*`) | **0.963 ±0.015** | 10 |

and within the free runs, s climbs 0.654 -> 0.963 over the first ~10 epochs as sd(β) rises
0.02 -> 2.05, while the frozen runs sit flat at 0.59–0.68 for the whole 20 epochs.

**The correlation is the part step-size adaptation consumes.** So the assumption is badly
wrong at uniform step sizes (N/N_eff up to 200 at m=11.17M) and approximately right at the
adapted equilibrium — which is where every method in that literature operates.

**Effect on the claims.**

| claim | status |
|---|---|
| "the 1/√N assumption is quantitatively false" (unconditional) | **REFUTED at the operating point.** s = 0.963 ±0.015 post-adaptation. |
| "the 1/√N assumption fails off-equilibrium, by a measured amount" | **STANDS**, n=5, 6 decades of m, with a validated estimator and a passing structural check. |
| "nobody in that line has measured it" | **stands** — the prior-art scout found no measurement, and this one is new either way. |
| the granularity gain should be large because coordinates are correlated | **REFUTED.** They are near-independent at equilibrium, which is *why* 42.2's gain is only +0.563pp. |

**Decision recorded.** Direction C is kept as the project but **restated**: the contribution is
the conditional result (fails before adaptation, restored by it) plus the measurement method,
not the unconditional refutation. The largest open cell is the frozen-β measurement at any
model or dataset other than ResNet18/CIFAR-10.

**Process note (Rule 4).** The frozen-β design was verified at both extremes before its
numbers were used: `beta_true_max == beta_true_min` on all 2000 records, and the five arms'
20-epoch accuracies agree to 0.010–0.030pp at matched seed. A partition that provably cannot
affect training is the only way to compare partitions.

## 28. Three process failures inherited from cycle 42's submission (cycle 42, second session)

Recorded so they are not repeated, not to relitigate the submissions.

1. **24 jobs (`I1-*`, `PP-*`, `SW-*`) were submitted with no saved submit script.** Every prior
   batch has one under `bin/c<NN>_*.sh`. Non-interactive `ssh` does not write bash history, so
   the exact `--export=` lines are recoverable **only** from the `ARGS:`/`ENV:` lines of a
   started job's `.out`, and not at all for a job that never starts. Reconstruct-and-save
   before the next cycle reads them.
2. **`PP-*` runs with `AUGMENT=0`**, against the standing rule. The nine rows are config-matched
   to `mx/probe_sig_*` (AdamW+Adam, a0=1e-6) so they are presumably a deliberate replication of
   that batch, but they carry no probe directory, so what they measure is unclear from the
   artefacts alone. **Do not pool them with augmented rows.**
3. **The `N_eff` estimator's first version used the CLT null** 0.5+√(2/π)/(2√K) and was biased
   1.571x at K=1 and 0.74x at K=2 (`analysis/neff_validate.py`, VALIDATION 1). It was caught by
   the synthetic block-model check *before* any number was published, and replaced with exact
   binomial inversion. This changed the a0=1e-6 frozen exponent from 0.395 to 0.364 and the
   m=6 N_eff from 0.70 (impossible) to 1.1. **Validate an estimator against simulated ground
   truth before reducing real data with it** — the CLT floor is the same approximation that
   produced the CORRECTIONS 26 error.

## 29. The `I1-*` schedule is UNIDENTIFIED — the +1.664pp cannot be called a cosine-prior effect (cycle 43)

**What is solid.** `I1_layer` (n=3) beats a byte-matched, same-account, non-scheduled control
(`dc-awscal-a1e3`, n=5) by **+1.664pp, t=11.6, CI [+1.35,+1.98]**. Every field of the two
`ARGS:`/`ENV:` lines is identical. A schedule was active: `HF.py.bak_sched` is timestamped
`2026-08-21 00:07:37` and the batch was submitted at `00:08:10`, so `PATCH_SCHED` was in the
loaded code. (The later `HF.py` mtime of `00:42:29` is `PATCH_PROBE4`, not `PATCH_SCHED`.)

**What is NOT solid, and must not be written.** The batch ran with no saved submit script and
`run_cifar.sh` did not yet echo `SCHED*` (that echo was added at `00:43:05`, after the jobs
started), so the schedule's **type, horizon, warmup and floor are unrecoverable from anything
on disk**. Non-interactive `ssh` writes no bash history. TensorBoard logs only
`Performance/{train_loss,train_accuracy,test_accuracy}` — no `alpha`/`beta` trace — so the
multiplier cannot be reconstructed from the run either.

**And the obvious reconstruction is refuted.** It was not a cosine matched to the 100-epoch
horizon. The arm is already **+7.2pp ahead at epoch 2** (78.46 ±0.67 vs 71.29 ±1.07, n=3/5),
i.e. at step ~1 500 of 50 000, where a matched cosine multiplier is **0.9978**. A 0.2% change
in alpha cannot produce a 7pp change in epoch-2 test accuracy. Whatever ran departed from the
control from the first epoch.

| claim | status |
|---|---|
| "`I1_layer` departs from its matched control by +1.664pp" | **STANDS**, n=3/5, t=11.6 |
| "the cosine-prior alpha_t = cosine(t)·exp(beta_t) gains +1.664pp" | **NOT SUPPORTED.** The schedule is unidentified and is provably not the matched-horizon cosine. |
| "Idea 1 loses to the tuned baseline" | **STANDS** and is schedule-independent: the arm is 1.873pp below the baseline whatever multiplier it ran. |

**Consequence.** FINDINGS 43.2's granularity-equalising table is a **provisional** mechanism
observation. Reproducing it requires a re-run from a saved script with `SCHED*` echoed — which
is NOT scheduled, because 43.1 already closed the method question. This is the second cycle in
a row damaged by CORRECTIONS 28.1; the rule is now: **a batch with no `bin/c<NN>_*.sh` submit
script is not readable as evidence about the intervention it was supposed to test.**

## 30. The tuned baseline is 94.417, not 94.093/94.24, and 3e-3 IS an interior maximum (cycle 43)

CORRECTIONS 25 withdrew "the baseline LR peak is an interior maximum at 1e-3" because 1e-3 was
the edge of the grid. `SW-*` (read this cycle, `--optimizer AdamW`, `COS_TOTAL=50000`,
`AUGMENT=1`, 100 ep) extends the grid and closes it:

| lr | 1e-5 | 3e-5 | 1e-4 | 3e-4 | 1e-3 | **3e-3** | 1e-2 |
|---|---|---|---|---|---|---|---|
| plateau (n=2) | 83.884 | 88.814 | 92.962 | 93.986 | 94.028 | **94.356** | 92.581 |

**3e-3 is bracketed on both sides.** Pooled with `fxcos-3e-3` the tuned 100-epoch baseline is
**94.417 ±0.113 (n=5)**. Every "loses by X" sentence must be recomputed against it — the
deficit for the best MetaOptimize arm (92.795) is **1.622pp**, not 1.30.

**Also: the anneal is not what the baseline is winning with.** `fxcos` uses
`COS_TOTAL=422000`, so over 50 000 steps its multiplier falls only to 0.977 — warmup then
near-constant. At lr=3e-3 it scores 94.458 ±0.103 (n=3) vs the horizon-matched anneal's
94.356 ±0.131 (n=2): **Δ = +0.10 ±0.10pp, unresolvable.** So "the gap is the schedule"
(CONTINUE-HERE, cycle 21) is **too strong**. The gap is the **peak learning rate**: at lr=1e-3
the baseline scores 94.03–94.11 and at 3e-3 it scores 94.36–94.46, while MetaOptimize's own
alpha never gets there. Rewrite the sentence as "the gap is the step size the baseline is
allowed to use, which MetaOptimize's meta-learner does not find."

## 31. The sign-agreement excess is MARGINAL BIAS, not correlation — 8b's mechanism sentence is wrong (cycle 43)

> **PARTLY SUPERSEDED BY §33, written the same cycle.** The measurement below is right and
> the *headline-statistic* conclusion survives with quantified power. The inference drawn from
> the pairwise nulls — "there is no correlation, therefore pooling is bias-limited" — is
> **withdrawn**: that test is under-powered for the correlation the tensor-level data already
> implies, by one to three orders of magnitude. Read §33 before quoting anything here.

CORRECTIONS 8b wrote: *"The signs are strongly positively correlated, so a pooled estimate does
not average toward zero — it converges to a population bias."* The conclusion is right; the
stated cause is not. `kt2_ww_a1e-3_s0` measures both channels separately at **true coordinate
granularity** (FINDINGS 43.3), which no earlier run could:

| channel | measurement | value |
|---|---|---|
| correlation between individual weights | pairwise same-sign rate vs a marginal-preserving circular-shift null | **+0.0001 pp across tensors (p=0.225), +0.0007 pp within a tensor** |
| each weight's own persistent direction | majority-agreement excess vs the same shift null | the whole of the **+0.194 pp** excess over the independence floor |

**There is no measurable correlation between per-weight meta-gradients.** The excess that the
project has been quoting since cycle 18 is each coordinate's own sign preference, which the
independence floor does not model and the circular-shift null does.

**Why this is not cosmetic.** The two channels break `1/sqrt(N)` in different ways:
* *Correlation* inflates the **variance** of a pooled estimate — more coordinates do not help
  as fast as `1/N`.
* *Marginal bias* moves the **mean** — the pooled estimate converges to a non-zero population
  bias, and pooling more coordinates does not help **at all**, at any N.

**Replicated at a0=1e-6** (FINDINGS 43.3b): every stratum is a null at both a0 values and the
two runs disagree in sign on all four, which is what independent noise at the 1e-3 pp scale
looks like. At a0=1e-6 the excess over the independence floor is +0.098pp and the excess over
the marginal-preserving null is **−0.0006pp (p=0.55)** — the bias accounts for all of it.

Our measurement says the variance channel is essentially exact at the adapted equilibrium
(Δ ≤ 0.001pp, replicated across a 1000x range of a0) and the surviving effect is entirely the
bias channel. **Restate direction C's
mechanism accordingly**: the failure of noise-averaging in this network is a bias failure, not
a correlation failure. CORRECTIONS 27's `N_eff ~ m^0.629` frozen-beta result is untouched as a
*measurement*, but its interpretation as "the coordinates are correlated off-equilibrium"
should now be checked against the same two-channel decomposition — the frozen runs have no
`PATCH_PROBE4` data, so **this is an open question, not a settled one**.

## 32. DECISION RECORD — cycle 43

**Decided, with reasons, from the data above.**

1. **Idea 1: STOP.** Pre-registered rule was "worse than the 94.24 plateau → record and stop".
   Best arm 92.544 vs a tuned baseline of 94.417 ±0.113 (n=5) = **−1.873pp**, and −0.251pp
   against our own best existing arm. Prior art caps it at a tie. No further I1 jobs. The
   short-horizon-bias prediction is **not** cleanly confirmed, because the schedule that ran is
   unidentified (§29) — recorded as untested rather than as a confirmed mechanism.
2. **Idea 2: DEAD, restated with the decisive evidence.** Cycle 42 killed it at *tensor*
   granularity. `kt2` kills it at *coordinate* granularity, which is the level the idea was
   actually about: across-tensor dependence **+0.0001pp** against a pre-registered kill
   threshold of 0.1pp, and architecture − random = +0.0002pp (p=0.29). Dropped.
3. **Direction C IS the project, and 43.3 changes what it says.** The contribution is now a
   **two-channel decomposition** of the noise model — correlation vs marginal bias — measured
   at per-weight granularity, plus the frozen/free contrast of CORRECTIONS 27. The
   `PATCH_PROBE4` probe is the instrument and it works; the estimator is validated against
   synthetic ground truth (16/16).
4. **Next experiment, when FairShare allows.** Unchanged in rank order: (a)
   `bin/c43_frozen_ladder.sh --submit` on alice2 — carries the frozen-beta measurement to
   ResNet10/ResNet34/CIFAR-100, still the campaign's largest open cell; (b) a `PATCH_PROBE4`
   probe on a **frozen-beta** run, which is new this cycle and is what §31 says is missing —
   it would decompose the off-equilibrium `s=0.629` into its bias and correlation parts, and
   it is 2 jobs; (c) `rs-node-*` / `rs-blk6-1e4` seed top-ups.
5. **Submitted nothing.** FairShare 0.3331 / 0.3356, both below the 0.35 floor, per the
   standing rule. Queues are at 1 running job total, which is the fastest available recovery.


## 33. §31's inference was under-powered — a per-weight null is what a real depth-local correlation LOOKS like (cycle 43, same tick)

**What §31 concluded, and what is wrong with it.** §31 read kt2's per-weight pairwise nulls
(across-tensor Δ = +0.0001 pp, p=0.225) as "there is no measurable correlation between
per-weight meta-gradients", and inferred that the variance channel of `1/sqrt(N)` is exact and
the surviving effect is entirely bias. **The measurement is right; the inference does not
follow**, and the arithmetic that shows why was not done before the sentence was written.

**Why.** A group meta-gradient is the **sum** of its members (`HF.py:149`). In a one-factor
model, `ρ_means = ρn / (1 + (n−1)ρ)`, so aggregating `n` coordinates amplifies a shared
component by ~`n`. Inverting KILLTEST §3's measured tensor-level within-block excess of
+1.0 pp (`ρ_means = 0.0314`) gives the per-weight correlation that produces it:

| tensor size n | per-weight ρ needed | per-weight sign excess it produces | kt2 measurement sd |
|---|---|---|---|
| 1e4 | 3.24e-6 | 0.000103 pp | **0.00017 pp** |
| 1e5 | 3.24e-7 | 0.000010 pp | 0.00017 pp |
| 1e6 | 3.24e-8 | 0.000001 pp | 0.00017 pp |

kt2's 95% upper bound is **ρ ≤ 1.68e-5**. The structure that KILLTEST already measured sits at
**ρ ~ 1e-6 to 1e-8** — 2x to 170x below the noise floor of the per-weight test. **A null at
per-weight granularity is exactly what a real depth-local correlation looks like through this
instrument.** Validated against simulated ground truth, not against any estimator in this repo:
`analysis/power_coord_vs_tensor.py`, FINDINGS 43.3c.

**What survives, with power quantified.** The tracked-subsample *majority* test (observed vs
the marginal-preserving null) has a replicate sd of 0.010–0.014 pp and would show a global
common mode of ρ = 3e-5 at +0.051 pp (~5 sd). A common mode large enough to produce the whole
headline excess needs ρ ≈ 4e-5. Measured: **+0.0047 ±0.010 pp (a0=1e-3), −0.0006 pp
(a0=1e-6)**. So:

| claim | status |
|---|---|
| the headline majority-agreement excess is **marginal bias, not a global common mode** | **STANDS**, ~5 sd |
| per-weight pairwise dependence is bounded by ρ ≤ 1.7e-5 | **STANDS** — a bound, not an absence |
| "the variance channel is essentially exact; pooling is bias-limited" (§31) | **WITHDRAWN** |
| "Idea 2 is dead" | **STANDS**, on the TENSOR-level across-block null, where the test has power |
| "Idea 2 dies by 1000x" (FINDINGS 43.3, first draft) | **WITHDRAWN** — that ratio compared an observation to a threshold, not to the test's resolution |

**Process note (Rule 3, and this is the third time).** CORRECTIONS 26 was a summary sentence
that merged two rows of a table. §31 is a null read without a power calculation. Both were
written from a single statistic without asking what the statistic could have detected.
**New standing rule: a null may not be reported as evidence of absence until the minimum
effect the test could resolve has been computed and stated next to it.** The reducer already
prints a p-value; a p-value is not a power bound.

**Consequence for the next experiment.** `bin/c44_frozen_probe4.sh` (prepared this cycle) is
still the right batch — it applies the same instrument to the frozen-beta runs — but its
pre-registered thresholds must be read against this resolution: it can only resolve
ρ > ~1.7e-5, i.e. an across-tensor excess above ~0.0005 pp. Its prediction (a) is written at
>= 0.05 pp, which is 100x the resolution, so the batch **can** discriminate outcome (a) from
(b); but a null result means "no correlation above ρ = 1.7e-5", **not** "no correlation".
The header of that script has been amended to say so.

## 34. The frozen-β deficit is DECOMPOSED, and per-weight correlation is measured, not bounded (cycle 44)

**What §33 left open, in its own words:** *"the frozen runs have no `PATCH_PROBE4` data, so
this is an open question, not a settled one."* It is now answered, from data already on disk,
with an instrument that has ~450× the resolution of the one that failed.

**Why kt2 could not see it and this can.** kt2 asked whether two *individual* weights agree;
a shared component of size ρ is invisible per-pair. `frac_neg` is an **average over all n
coordinates**, so a shared component is amplified ~n while independent noise falls as 1/n.
That is the same aggregation amplification §33 used to *predict* the failure. Resolution is
`ρ_min = 2√(2/T_eff)/n`, which **improves** with granularity: 3.7e-8 at n=11.17M against
kt2's pairwise 1.7e-5.

**The measurement** (`fz-w-a3` vs `p7-r18-w`, byte-matched `ARGS` except `--alg-meta`, both
a0=1e-3, R18/CIFAR-10, weightwise, steady half; FINDINGS 44.3):

| arm | n | bias (pp) | ρ_s | t | %bias | %common | %indep | N/N_eff |
|---|---|---|---|---|---|---|---|---|
| β frozen | 5 | 0.1680 | 1.925e-6 | 11.7 | **85.1** | 14.6 | **0.7** | 148.6 |
| β free | 10 | 0.0032 | 8.458e-8 | 6.8 | 4.0 | 45.6 | **52.4** | 1.99 |

| claim | status |
|---|---|
| "there is no measurable correlation between per-weight meta-gradients" (§31) | **REFUTED.** ρ_s = 1.9e-6, t = 11.7 over 5 seeds. §33 had already withdrawn the inference; this replaces the withdrawal with a number. |
| "the per-weight null is under-powered; the true ρ is ~1e-6…1e-8" (§33) | **CONFIRMED.** All five measured cells fall inside that band and below §33's 1.7e-5 bound. |
| the off-equilibrium N/N_eff deficit is a *bias* failure | **STANDS, and is now quantified: 85% bias / 15% common mode.** Only 0.7% of the signal is the channel 1/√N models. |
| 1/√N is approximately restored at the adapted equilibrium (§27) | **STANDS**, independently: N/N_eff = 1.99 ±0.16 from the variance budget vs 2.0 from `N_eff ~ m^s`. Two different statistics. |
| "the correlated part is what adaptation consumes" (§27) | **REFINED.** Adaptation consumes the **bias** 52.7× and the common mode only 22.8×. The bias channel is distance from meta-stationarity (E[meta-gradient] = 0 at the meta-optimum); the common mode is not removed by that mechanism and survives at t = 6.8. |

**A positive reading here is safe in a way a null would not be.** Independent-but-
heterogeneous coordinates give `Var(frac_neg) = mean_i p_i(1−p_i)/n ≤ p̄(1−p̄)/n`, so the
estimator **cannot manufacture** a common mode from heterogeneity (VALIDATION 11, simulated).
Every ρ_s is a **lower bound**.

**Two estimator bugs caught by validation before any number was published** (Rule 4, and the
same discipline that caught the CLT-floor bug in §28.3):
1. the plug-in floor `p(1−p)/n` is biased low by `(1−1/n)`; dividing by `n−1` is unbiased.
   Worth 26% of a ρ=1e-3 signal at n=62 and 20% of the floor at n=6.
2. probe records are autocorrelated (τ up to 36.3 on `kt2`), so the χ² sd overstated
   significance. `T` is now deflated by τ. Point estimates unaffected.

**And one bug caught in the VALIDATION itself, which is the reason to write validations that
can fail.** The first VALIDATION 2 of `corr_range` reported that a *true global factor*
produced a 19× spurious scale dependence. The fault was the simulation, not the estimator:
proxying 11.17M coordinates with 30 000 explicit columns injects sampling variance
0.25/30 000, which at n = 11.17M is 375× the true binomial floor. Conditioning on the latent
factor and drawing `Binom(m, P(u<τ|f))` is exact at any m. **A validation that had merely
been asserted to pass would have hidden this.**

**What is NOT claimed.** The scale profile — whether correlation is short-range — is
confounded in exactly the direction that would produce it (FINDINGS 44.5): the floor bias
grows with group size, depressing the coarse rungs and making ρ_w implied fall with k.
Reported as an open question with the confound named, **not** as a correlation length.
Per §33's standing rule, every rung below its own ρ_min is printed as `NO` and excluded —
including the layerwise rung of the controlled batch, which a hand calculation had wrongly
treated as a 67× result before the power gate caught it.

## 35. FairShare cannot recover on the timescale the standing rule assumes (cycle 44)

**Recorded because it is now the campaign's binding constraint, not because it changes a
result.** The standing rule is "if FairShare < 0.35, submit nothing and let usage decay."
The measured facts:

| | alice | alice2 |
|---|---|---|
| FairShare, cycle 43 | 0.3331 | 0.3356 |
| FairShare, cycle 44 | **0.333054** | **0.335570** |
| RawUsage | 24,375,279 | 20,035,200 |
| queue | 0 PENDING / 0 RUNNING | 0 PENDING / 0 RUNNING |

`scontrol show config`: **`PriorityDecayHalfLife = 14-00:00:00`**, `PriorityUsageResetPeriod =
NONE`, `PriorityWeightFairShare = 800000`, `PriorityWeightPartition = 1000000`,
`PriorityWeightQOS = 1000000`, `PriorityWeightAge = 10000`.

**Consequences.** Usage decays 4.9%/day, so a full cycle with both queues at zero moved
FairShare by less than the 4th decimal — consistent with the two readings above. Recovery to
0.35 is a **multi-day** process at best, and it is not under our control: FairShare is
relative, so it also depends on other `liacs` users continuing to accrue.

**Decay measured within this tick, not inferred.** With both queues at zero throughout:

| | RawUsage at tick start | at tick end | change | FairShare |
|---|---|---|---|---|
| alice | 24,375,279 | 24,354,340 | **−0.0859%** | 0.333054 → 0.333054 |
| alice2 | 20,035,200 | 20,017,989 | **−0.0859%** | 0.335570 → 0.335570 |

Both accounts decay at exactly the same rate, which is the 14-day half-life
(0.206%/hour) and nothing else. **FairShare did not move in the 6th decimal.**

**The rule's premise is that waiting works. On a 14-day half-life it works very slowly.**
Two facts that bound the other side of the trade, recorded for the operator to decide with:
* the 4-job `PATCH_PROBE5` batch below would add ~9 600 GPU-seconds, i.e. **0.04% of
  RawUsage** — about 12 minutes of natural decay. The incident that set the rule (cycle 41)
  involved 300+ jobs, a different order of magnitude.
* FINDINGS 33.9/38 measured that this campaign's pendings were **`QOSMaxGRESPerUser`-bound,
  not priority-bound** (93 of 94 on alice2), so at these queue depths FairShare was not what
  decided when jobs started.

**Decision this tick: the rule was followed as written — nothing was submitted.** It is an
explicit hard limit and the operator is away; reasoning around it unsupervised is not mine to
do. Flagged here so the operator can revise it with numbers rather than have it silently
broken. The whole of cycle 44's science was obtained at zero compute, so the cost of obeying
it this tick was zero.

## 36. DECISION RECORD — cycle 44

1. **Direction C is the project and it just got its strongest result.** The contribution is
   now a *measured two-channel decomposition* of the noise model — 85% marginal bias / 15%
   common mode off equilibrium, flipping to 52% independent noise at the adapted equilibrium
   — plus the first direct measurement of per-weight meta-gradient correlation (ρ_s = 1.9e-6,
   t = 11.7), which the Adam-mini / Adalayer / SGG line assumes is zero. §34.
2. **The long-horizon question is CLOSED as a clean negative.** n=3/n=3 at 600 epochs:
   deficit 1.937pp, flat across 300→600. No further `bg` jobs. FINDINGS 44.1.
3. **Ideas 1 and 2 remain dead.** Nothing this cycle touches them; no jobs spent on either.
4. **Next experiment, and it is now sharply defined.** `PATCH_PROBE5` — emit per-group
   negative *counts* alongside the pooled `frac_neg`, one array per run. That is the single
   change that de-confounds the scale profile (§34, FINDINGS 44.5), and the scale profile is
   the "how does agreement vary with block size" question the project is pointed at. 4 jobs,
   ~40 min each. **Prepared and self-guarded; NOT submitted** (§35).
5. **Submitted nothing**, per the standing FairShare rule. Both queues empty; no job in flight.

## 37. The FairShare floor is formally RETIRED and replaced with a batch-size rule (cycle 47)

CORRECTIONS 35 measured that the rule could not work and left the decision to the operator.
The operator has now revised it explicitly. Recorded here because §35 says "flagged so the
operator can revise it with numbers", and this is that revision:

| | old rule | new rule |
|---|---|---|
| gate | FairShare ≥ 0.35, else submit nothing | batch adds < ~0.5% of RawUsage (≈ ≤20 jobs of ~40 min) |
| hard stop | — | PENDING > 40, or a single batch > ~40 jobs |

Rationale, all of it already measured in this repo: `PriorityDecayHalfLife = 14 days` so
0.35 is unreachable on any useful timescale (§35); FairShare is *relative* to other `liacs`
users so it is not under our control; and 93 of 94 pendings were `QOSMaxGRESPerUser`-bound,
not priority-bound (FINDINGS 33.9/38), so FairShare was not gating job starts at these queue
depths. The incident that set the original rule was 300+ jobs — a different order of
magnitude from anything since. **Judge by batch size and queue depth, not by the number.**
Both scripts this cycle log the deviation as `--force-fairshare` in their own output.

## 38. The IDEA 3 verdict INVERTS against a tuned schedule, and "flatter" needs a stated metric (cycle 47)

**What cycles 45/46 set up, and what was missing.** The sweep compared MetaOptimize (arm B)
against a genuinely fixed learning rate (arm A) and `analysis/idea3_robustness.py` printed
*"REFUTED: MetaOptimize is NOT flatter than a fixed step size."* That verdict came from a
single metric — width within 1pp of each arm's own best — and it is fragile in a way the
binary print hides. On the **absolute** ≥90 criterion the same data says arm B is flatter by
2.5 decades. **A robustness verdict without its metric named is not a result.**

**The bigger omission: arm A is the wrong competitor.** Nobody ships a constant LR. The
campaign already held the right one — `SW_*`, an AdamW+cosine peak-LR sweep, config- and
account-matched — and it had never been put in the same table. Adding it as arm C (FINDINGS
47.1, `analysis/idea3_threearm.py`, selftest 22/22) gives, on the shared sub-grid:

| | A fixed | B meta | C cosine |
|---|---|---|---|
| peak | 91.796 | 93.350 | **94.028** |
| worst | 69.898 | **90.095** | 83.884 |
| width ≤1pp of own best | 0.477 | **0.000** | 0.523 |
| width ≤2pp / ≤3pp | 1.000 | 2.000 | 2.000 |
| width above absolute 90 | 0.477 | **3.000** | 2.000 |

| claim | status |
|---|---|
| "MetaOptimize is more robust to alpha0 than a fixed step size" | **STANDS** — 3.255pp span vs 21.898pp |
| "MetaOptimize is more robust than the alternative a practitioner would use" | **FAILS on the scale-free metric** (loses at 1pp, ties at 2pp and 3pp) and **HOLDS on the absolute one** (3.0 vs 2.0 decades ≥90). Report both rows or neither. |
| "the parent paper's robustness claim survives" | **SPLIT, not a tie.** The two curves have different shapes; the verdict depends on the tolerance. |
| MetaOptimize's peak cost | **1.067pp** below the tuned baseline 94.417 ±0.113 (n=5), and that is a LOWER bound — arm C's argmax 3e-3 is off this grid. |

**The honest sentence, and it is a real result either way:** *MetaOptimize buys insensitivity
to catastrophic mis-setting of the step size — at alpha0 = 1e-5 it reaches 85% in 8.7 epochs
where a fixed LR needs 89.3 and a cosine never gets there — but it does not remove the need to
tune, and it pays ~1.1pp of peak accuracy for that insurance.*

**Not final.** The c46 300-epoch convergence control has not landed; the reducer prints
NOT YET DECIDABLE. Per `docs/IDEA3-robustness.md` §7, if it prints NOT BUDGET-STABLE the
100-epoch sweep is not a valid basis for any of the above and must not be patched with a
caveat.

## 39. `idea3_robustness.py`'s clip-control line is wrong in SIGN (cycle 47)

It prints *"delta +28.103 pp — the guard IS part of arm B's top-end flatness. State it."*
That delta is one fully collapsed seed (`i3b-1e1-s2`, plateau 10.000 = chance) inside a
2-seed mean. Applying the standing `plateau > 50` collapse filter — necessary by hand because
the `collapsed` column is `0` on every row and flags nothing — inverts it: guard ON 86.858
(n=1) vs guard OFF 76.532 (n=2), i.e. the guard is worth **+10.3pp**, not −28.1pp. The cell is
**not decidable at n=2**; both third seeds were still running. FINDINGS 47.3.

**Withdrawn:** any sentence of the form "the guard is doing arm B's top-end work."
**Standing rule reaffirmed:** apply `plateau > 50` before every mean in this campaign.

## 40. DECISION RECORD — cycle 47

1. **IDEA 3 is the strongest live result and it is now three-armed.** The cycle-45/46 design
   was measuring MetaOptimize against a competitor nobody uses. Arm C fixes that at zero
   compute and it changes the verdict from "refuted" to a documented split (§38). Continue.
2. **Direction C remains the project.** The `PATCH_PROBE5` batch — the one experiment that
   de-confounds the scale profile, i.e. "how does agreement vary with block size" — is
   **submitted** (8 jobs, alice2), which cycle 44 could not do under the old FairShare rule.
3. **Ideas 1 and 2 stay dead.** Nothing this cycle touches either; zero jobs spent on them.
4. **Submitted 18 jobs, ~0.2% of RawUsage, nothing cancelled.**
   `c47_idea3_armC_cosine.sh` 10 on alice (`4700694-4700703`) — arm C at the two grid extremes
   plus band-edge seed top-ups, pre-registered C1/C2/C3 in FINDINGS 47.4.
   `c44_probe5_heterogeneity.sh` 8 on alice2 (`4700704-4700711`) — per-group marginals.
5. **A fatal bug in the prepared PROBE5 patch was caught before submission** and would have
   returned nothing from all 8 jobs (§FINDINGS 47.5). Fixed, and covered by a new regression
   test that executes the shipped bytes rather than reading them: `tests/test_probe5_block.py`,
   **10/10 PASS**. A second suspected bug was investigated and shown NOT to be one; recorded so
   it is not "fixed" later.
6. **Next tick, in order.** (a) Read the c46 300-epoch control and run
   `analysis/idea3_robustness.py` — **nothing about IDEA 3 is final until it prints
   BUDGET-STABLE**. (b) Read `i3c-*` against the C1/C2/C3 pre-registration and re-run
   `analysis/idea3_threearm.py`. (c) Reduce the `p5-*` probe dirs with the corrected floor and
   settle FINDINGS 44.5 outcome (a) vs (b). (d) Re-read the alpha0=1e-1 clip cell once its
   third seeds land (§39). (e) `bin/c43_frozen_ladder.sh` (30 jobs) — frozen-beta to
   R10/R34/CIFAR-100 — remains prepared and is the largest untouched cell.

## 41. Both IDEA 3 reducers are now divergence-aware, and the absolute-floor width is not threshold-stable (cycle 47, later in the tick)

Three changes, all made BEFORE the c46 300-epoch data landed so the budget-stability verdict
could not be tuned to it.

**(a) Divergence is a first-class outcome in both reducers.** `analysis/idea3_robustness.py`
(selftest **22/22 → 37/37**) and `analysis/idea3_threearm.py` (**22/22 → 34/34**) now (i)
compute cell means over surviving seeds only (`plateau > 50`), (ii) report the divergence
count as its own column, (iii) treat a cell with **no** survivor as missing rather than as a
low score, and (iv) **exclude any cell containing a divergence from every width band at every
tolerance**. A step size that collapses on some seeds is not one the method is robust at,
whatever the surviving seeds averaged to. This is §39 fixed in code, not just documented.

Immediate effect — the clip control now reads, and refuses to decide:

```
BETA_CLIP=-15:-2.3026 (alpha<=0.1)    86.858   n=1  diverged=1
BETA_CLIP=-15:0       (alpha<=1.0)    78.705   n=3  diverged=0
DIVERGENCE RATES DIFFER (1/2 vs 0/3) ... the two settings fail in DIFFERENT WAYS
NOT DECIDABLE: n=1 surviving seed(s) on one side.
```

And **arm A at alpha0=1e-1 has no surviving seed at all** (3 of 3 collapse) — a cleaner and
stronger statement than the 13.896 mean previously reported.

**(b) §38's "absolute floor" leg is WITHDRAWN as a standalone claim.** Arm B completed to n=3
during the tick; `i3b-1e2` moved 90.095 → **89.987**, i.e. 0.013pp under the 90 line and 7×
inside its own sd, which alone moved arm B's ">=90 width" from 3.0 decades to 2.0. The
reducer now prints a threshold scan, and the B-vs-C ranking **flips across it**: B>C at floors
≤89.5, B=C at 90–91, C>B at 92. FINDINGS 47.9.

| claim | status |
|---|---|
| "MetaOptimize is flatter than a tuned cosine on an absolute floor" (§38) | **WITHDRAWN as stated.** True only for floors ≤89.5. Must name its threshold and show the scan. |
| "MetaOptimize is not flatter on the scale-free metric" (§38) | **STANDS and strengthens** — loses at 1pp, ties at 2pp and 3pp, on complete n=3 data. |
| MetaOptimize's peak cost | **1.113pp** below 94.417 ±0.113 (was 1.067 at n=2). |
| the bottom-end rescue | **STANDS, and it is the one durable advantage.** At alpha0=1e-5: 91.535 vs the cosine's 83.884 (**+7.65pp**), and 8.7 epochs to 85% vs 89.3 for a fixed LR. |

**(c) New standing rule, and it generalises §33's.** *A width, count, or ranking measured
against an absolute threshold may not be reported until it has been recomputed across a range
of thresholds and shown to be stable. If the ranking flips, report the scan, not a row.*
§33 required a null to carry its resolution; this requires a threshold result to carry its
sensitivity. Both failures are the same failure — a number quoted without what it could have
been.

**Also amended, not submitted: `bin/c43_frozen_ladder.sh`.** It exports `PROBE=100` and no
`PROBE5=1`, so its 30 runs could not carry the heterogeneity correction the live canary shows
is material (**H = 0.833 at m=6**), and could not be corrected afterwards. Header now carries
the required change and the resolution table that motivates it. Held deliberately so the
8-job PROBE5 batch reports first.

## 42. IDEA 3 is BUDGET-STABLE — the "NOT FINAL" hold on §38 and §41 is LIFTED (cycle 48)

CORRECTIONS 38 and 41 both closed with the same caveat: *"nothing about IDEA 3 is final
until `analysis/idea3_robustness.py` prints BUDGET-STABLE"*, and
`docs/IDEA3-robustness.md` §7 said a NOT BUDGET-STABLE verdict would invalidate the
100-epoch sweep outright rather than merely qualify it. All 16 c46 jobs have now landed and
the reducer prints **THE SHAPE IS BUDGET-STABLE**: on the matched 4-point extremes sub-grid,
band membership, both widths and the A-vs-B ordering are identical at 100 and 300 epochs
(FINDINGS 48.1). The 100-epoch grid stands.

The pre-registered mechanism it was designed to catch — arm B's startup tax, which should
make a longer budget help arm B *more* at the bottom of the grid — reads **+0.228pp**
differential, inside the reducer's own **0.3pp** resolution floor at n=2. Recorded as a null
with its resolution, not as an absence (§33's standing rule).

## 43. §41(b)'s successor claim is WITHDRAWN: a cross-arm width is only defined on the SHARED grid, and an incomplete arm truncates the OTHER arms (cycle 48)

**What FINDINGS 47.9 concluded, and what is wrong with it.** 47.9, written on the
{1e-5..1e-2} sub-grid that was all arm C then had, said: *"MetaOptimize is not more robust
than a tuned cosine on any threshold-stable measure"* — losing at 1pp, tying at 2pp/3pp,
and tying at absolute floors 90–91. Arm C's two extreme cells landed this cycle. On the
complete 7-point grid the same reducer, on **byte-identical arm-B data**, gives:

| | A fixed | B meta | C cosine |
|---|---|---|---|
| width ≤2pp / ≤3pp of own best | 1.000 | **3.000** | 2.000 |
| width above 90 / above 91 | 0.477 | **3.000** | 2.000 |
| threshold scan 84→92 | — | B>C on 7 of 8 rows | C>B only at ≥92 |

**The cause is not new arm-B data — it is the shared-grid restriction.** Arm B's in-band run
`[1e-6 .. 1e-3]` was silently truncated to `[1e-5 .. 1e-3]` while arm C had no cell at
1e-6. Arm C's new cells (63.333 at 1e-6, 53.051 at 1e-1) are far outside every band and
enter none of them; they only make arm B's own 1e-6 cell countable.

| claim | status |
|---|---|
| "MetaOptimize is not more robust than a tuned cosine on any threshold-stable measure" (47.9 / §41) | **WITHDRAWN.** It wins at 2pp and 3pp tolerance and at every absolute floor from 84 to 91. |
| "B=C at floors 90–91" (§41's scan) | **SUPERSEDED** — B>C at both, by 1.0 decade. |
| "the B-vs-C ranking is not threshold-stable" (§41(c)) | **STANDS**, weakened: 7 of 8 rows now agree. The scan must still be shown. |
| "MetaOptimize loses at the 1pp tolerance" | **STANDS** — 0.000 vs 0.523 decades. Its curve has a sharp peak at 3e-4 and is flat only in the tails. |
| MetaOptimize's peak cost | **STANDS at 1.113pp** below 94.417 ±0.113 (n=5). Unchanged. |

**NEW STANDING RULE, and it generalises §33 and §41(c) again.** *A cross-arm width, band or
ranking is defined only on the sub-grid where every arm has a measurement. An arm with a
missing cell is therefore not only an incomplete measurement of itself — it silently
shortens every other arm's band. Before comparing widths, print the shared grid and the
union grid, and treat any difference between them as a pending correction to the table.*
`idea3_threearm.py` already prints both lines; nobody had read them against each other.

This is the third revision of the IDEA 3 verdict (47.1 → 47.9 → 48.2). All three were
arithmetic on incomplete grids, and each is superseded by more data rather than by a
mistake. That is not a defect in the method — but it is why §44's dial-free statistic
should be the one quoted.

## 44. The IDEA 3 comparison now has a statistic with NO free parameter, and it favours MetaOptimize by ~5pp (cycle 48)

Every width in §38, §41 and §43 has a dial on it — a tolerance, or a floor — and each
revision above moved a band edge without moving any underlying accuracy. §41(c) demanded a
sensitivity scan; the better answer is a statistic that cannot be scanned.

`analysis/idea3_threearm.py` (selftest 34/34 → **45/45**) now reports the grid mean and grid
worst under two conventions, over the shared grid (FINDINGS 48.3):

| | A fixed | B meta | C cosine |
|---|---|---|---|
| grid mean, survivors (6 pts) | 82.793 | **91.723** | 86.782 |
| grid mean, face value (7 pts, collapses at their actual score) | 72.765 | **87.058** | 81.963 |

**B − C = +4.941 pp and +5.094 pp.** The two conventions differ in whether a collapsed seed
is averaged in and they agree to 0.15pp, so the conclusion does not depend on that choice
either.

**The sentence to write, and it needs no caveat about a threshold:** *MetaOptimize's peak is
0.773pp below a tuned cosine on-grid and 1.113pp below the true tuned baseline
94.417 ±0.113, but averaged over a 7-decade alpha0 grid it is ~5pp ahead of that same
cosine. You pay ~1.1pp of peak for ~5pp of expected accuracy under an unlucky step size.*

## 45. FINDINGS 44.5's "NOT CLAIMED" scale profile is now CLAIMED — outcome (b), corrected and window-scanned (cycle 48)

FINDINGS 44.5 and CORRECTIONS 34 both refused to read the falling scale profile as a
correlation length, because the pooled independence floor is biased in exactly the direction
that manufactures one. The 8-job PROBE5 batch measures the bias and removes it. Steady half,
geometric mean over seeds, `analysis/probe5_floor.py` (15/15) and the new
`analysis/probe5_window.py` (**33/33**):

| | k=1 | k=775 | k=180,225 | span | b in rho_w ~ k^-b |
|---|---|---|---|---|---|
| uncorrected floor | 3.200e-06 | 1.130e-06 | 1.934e-08 | 165.5x | 0.412 |
| **corrected floor** | 3.200e-06 | 1.133e-06 | **4.620e-08** | **69.3x** | **0.343** |

| claim | status |
|---|---|
| "the scale profile is confounded and is NOT claimed" (FINDINGS 44.5, CORRECTIONS 34) | **RESOLVED — the confound is real and it is not enough.** It removes 58% of the excess log-span and leaves 69.3x, against a pre-registered (a) threshold of 3x and (b) threshold of 10x. |
| pre-registered outcome (b), "the correlation length is REAL" | **CONFIRMED**, and window-stable: (b) in all three of full / steady / startup (53.4x / 69.3x / 520x). |
| "heterogeneity grows with group size", the premise of the confound argument | **PARTLY REFUTED and it does not matter.** H peaks at layerwise (0.803), not blk6 (0.906). But blk6's H is estimated from 6 coordinates and is unresolvable, so this is recorded as unresolved, not as a reversal. |
| the two fine rungs are contaminated | **BOUNDED AWAY.** At tau=1, which over-states heterogeneity, H = 0.9975 (weightwise) and 0.9809 (nodewise) — the bias is at most 0.25% and 1.9%, so the k=1→775 leg is uncontaminated by construction. |
| the blk6 rung | **NULL WITH ITS RESOLUTION.** Steady-half rho_s goes negative (−3.07e-02) against rho_min 2.28e-02. Do not report a blk6 absence. |

**And the instrument is now calibrated against a previously published campaign number.**
`probe5_floor.py --profile` reduces the FULL run and disagreed with FINDINGS 44.3 by 4.2x on
a byte-matched configuration. That disagreement is **entirely the window**: on the steady
half, `p5-w-a3` reads 1.991e-06 / 2.085e-06 against 44.3's independently measured
**1.925e-06** — **+3.4% / +8.3%**, from a different job, a different sampling rate and a
different reducer (FINDINGS 48.6).

**NEW STANDING RULE.** *A time window is a dial exactly like a threshold. A statistic
computed on a window may not be reported until it has been recomputed across the campaign's
window set (full / steady half / startup quarter) and either shown stable or reported as a
scan.* This is §41(c) extended from thresholds to windows, and it is enforced in code:
`analysis/probe5_window.py` prints the scan and refuses to declare a verdict stable unless
every window agrees. Had the full-run window been quoted alone, the campaign would have
published a rho_s 4.2x above its own earlier measurement without noticing.

## 46. DECISION RECORD — cycle 48

1. **IDEA 3 IS FINISHED at R18/CIFAR-10/m=6 and it is a POSITIVE result, not a split.**
   The budget gate cleared (§42), the grid completed, and the dial-free statistic says
   MetaOptimize is **+4.94pp ahead of a tuned cosine averaged over the alpha0 grid** while
   paying 1.113pp of peak (§44). Every earlier "not more robust" sentence is withdrawn
   (§43). **No further IDEA 3 jobs at this configuration** — the remaining question is
   whether it generalises to another model or optimizer, which is a bigger spend than the
   evidence currently justifies against Direction C.
2. **Direction C IS the project, and its structural result is now claimed rather than
   withheld.** Per-weight meta-gradient sign correlation is nonzero and **short-range**:
   rho_w ~ k^-0.343 over 5.3 decades of block size, 69.3x fall, corrected for the
   heterogeneity confound that FINDINGS 44.5 refused to publish without, and stable across
   the window scan (§45). The 1/sqrt(N) noise-averaging assumption that justifies coarse
   granularity across the Adam-mini / Adalayer / SGG line is violated, and the violation is
   scale-dependent.
3. **The single biggest threat to that claim is that it is measured with beta FROZEN**, i.e.
   off the meta-optimum, while every method it is aimed at adapts. FINDINGS 44.3 measured
   that adaptation changes the system qualitatively (85%/15%/0.7% bias/common/independent →
   4%/46%/52%, rho down 22.8x). **12 jobs on alice2 test whether the profile survives
   adaptation** — with the refutation, its consequence for the paper's framing, and the
   layerwise rung's resolution all pre-registered in the script header before submission
   (FINDINGS 48.9). If it refutes, the claim narrows to "before the step size adapts" and
   that is still publishable; it must be written as that, not as a null.
4. **The second threat is that it is one architecture and one dataset.** **20 jobs on alice**
   carry the corrected profile and the frozen N_eff exponent to ResNet10, ResNet34 and
   CIFAR-100. This is c43's batch, finally submittable because it now exports `PROBE5=1` and
   `PROBE=5`; as written it could not have carried the correction and could not have been
   corrected afterwards.
5. **Ideas 1 and 2 stay dead.** Zero jobs spent on either, this cycle and the previous four.
6. **Submitted 32 jobs across two accounts, both queues were empty beforehand, nothing
   cancelled.** PATCH_PROBE5 + its fix were applied to alice and verified against the live
   file with `tests/test_probe5_block.py` (10/10, executes the shipped bytes).
7. **Next tick, in order.** (a) Reduce `fr5-*` with `probe5_window.py` and score B0/B1/B2 —
   **B0 is a validity gate: if steady-half rho_s(weightwise) is not within 3x of 8.458e-08,
   nothing else in that batch may be quoted.** (b) Reduce `fz3-*` per family, scoring
   A0/A1/A2, and remember that each family's n_weights must come from its own weightwise
   arm. (c) Run `analysis/neff_ladder.py fz3` for A3. (d) `ep_to_85` has not been re-derived
   with arm C's two new extreme cells; 47.12's arm-C column is still n=2 and still
   warmup-confounded. (e) Nothing else in IDEA 3.

## 47. §45 and §46(2) are NARROWED by their own pre-registered test, within the same cycle (cycle 48, later in the tick)

§45 (written earlier this tick) said the scale profile is *"now CLAIMED rather than
withheld"* and §46(2) called it the project's structural result. The 12-job free-beta batch
submitted alongside it — designed precisely to attack that claim — has landed and it
refutes the generalisation. Recorded here rather than by editing §45, because §45's
measurement is correct; only its scope was too wide.

**What the pre-registered test said and what it measured.** `bin/c48_free_profile_p5.sh`
(B1) predicted the k=1 → k=775 leg would fall **>= 2x** at the adapted equilibrium as it
does frozen (2.82x). Measured: **0.68x — it rises**, roughly 12 sd from the prediction.

| | frozen (`--alg-meta fixed`) | free (`--alg-meta Lion`) |
|---|---|---|
| profile span, steady half | **69.3x** | **3.4x** |
| exponent b in rho_w ~ k^-b | **0.343** | **0.065** |
| exchangeable model over-predicts by | **45.4x — REJECTED** | **2.3x — NOT rejected** |
| rho_s at weightwise | 2.037e-06 | 8.888e-08 |

| claim | status |
|---|---|
| "per-weight meta-gradients are not independent" | **STANDS AT THE ADAPTED EQUILIBRIUM** — free rho_s(weightwise) = 8.888e-08 at 3.1x its own rho_min, reproducing FINDINGS 44.3's 8.458e-08 to **+5.1%**. This is the core refutation of the Adam-mini / Adalayer / SGG independence assumption and it is untouched. |
| "the correlation is short-range, rho_w ~ k^-0.343" (§45, FINDINGS 48.5) | **NARROWED to OFF-EQUILIBRIUM.** True with beta frozen; b = 0.065 at the adapted equilibrium. Every scale-dependence sentence must carry *"before the step size adapts"*. |
| "the exchangeable one-factor model is rejected by 45x" (FINDINGS 48.11) | **NARROWED identically** — 2.3x free, not rejected. |
| "adaptation consumes the correlated component" (§27, FINDINGS 44.3) | **CONFIRMED AND REFINED, and this is the cycle's new positive result: it consumes it SCALE-SELECTIVELY** — 22.92x at k=1, 5.49x at k=775, **0.77x (none) at k=180,225**. The 22.92x independently reproduces 44.3's 22.8x. |

**The B0 validity gate passed at +5.1%**, so none of this is an instrument failure: the same
reducer reproduces the frozen arm to +3.4%/+8.3% (48.6) and the free arm to +5.1%.

## 48. The WINDOW rule of §45 was vindicated on its first contact with new data (cycle 48, same tick)

§45 introduced the standing rule that *a time window is a dial exactly like a threshold*,
and `analysis/probe5_window.py` was written to enforce it. On the free-beta batch it printed
**NOT WINDOW-STABLE** immediately:

| window | span | b | verdict |
|---|---|---|---|
| full | 25.8x | 0.263 | (b) RANGE IS REAL |
| steady .5–1 | 3.4x | 0.065 | **NEITHER** |
| startup 0–.25 | 124.7x | 0.331 | (b) RANGE IS REAL |

**`probe5_floor.py --profile`, the pre-registered reducer, defaults to the full run and
would have reported "the profile survives adaptation".** It does not. Without the scan this
cycle would have published the opposite of §47.

**And the window dependence is not noise — it is the mechanism.** The free arm's STARTUP
window (b = 0.331) is the frozen arm's STEADY window (b = 0.343) to **0.012**. Before beta
adapts, the free arm *is* the frozen arm — which FINDINGS 44.3 had already recorded from a
different statistic. The single coherent reading: **the short-range structure is present
whenever the step size is far from its meta-optimum, and is erased fine-scales-first as beta
adapts.**

## 49. DECISION RECORD — cycle 48, amended after the free-beta batch landed

Amends §46, which was written before this batch reported. Items 1, 5 and 6 are unchanged.

2. **(AMENDED) Direction C's claim splits in two, and the second half is the better paper.**
   (a) Per-weight meta-gradient correlation is non-zero **in the regime the target methods
   actually run in** — free rho ~ 9e-8, reproduced to 5% across two independent batches.
   (b) Its *structure* is set by distance from the meta-optimum: short-range and strong off
   equilibrium (b = 0.343, exchangeability rejected 45x), weak and approximately scale-free
   at it (b = 0.065, not rejected). **A step-size adapter is a high-pass filter on
   meta-gradient correlation**, suppressing 22.9x at k=1 and 0x at k=180,225.
   Do not write "the violation is scale-dependent" without "before the step size adapts".
3. **(RESOLVED, was "the single biggest threat")** The threat was real and it fired. The
   12-job batch was worth every one of them: it converted a claim that would have been
   refuted by the first reviewer into a two-part result with a measured mechanism.
4. **(UNCHANGED, and now more valuable than when it was submitted)** The 20-job `fz3-*`
   ladder is still in flight. Its frozen profile now has a **specific** thing to test:
   whether b ~ 0.34 off equilibrium replicates on R10 / R34 / CIFAR-100. And because it
   carries PROBE5 it also settles FINDINGS 48.13's open cross-check from the same runs.
7. **(AMENDED) Next tick, in order.** (a) Reduce `fz3-*` per family with
   `probe5_window.py`, scoring A0/A1/A2 — each family's n_weights from its OWN weightwise
   arm (R10 4,903,242 / R18 11,173,962 / R18_c100 11,220,132 / R34 21,282,122, all
   confirmed from live `n_tot`). (b) `analysis/neff_ladder.py fz3` for A3, then put its `s`
   next to the variance-derived `s` on the same runs and settle FINDINGS 48.13.
   (c) **The obvious next experiment, and it is cheap:** the free arm was measured at ONE
   distance from the meta-optimum. §47's mechanism predicts b should vary CONTINUOUSLY with
   that distance. A meta-stepsize ladder (`--meta-stepsize` 1e-4 / 1e-3 / 1e-2 at the four
   rungs, ~12 jobs) would turn "frozen vs free" into a curve and make the high-pass-filter
   reading testable rather than a hypothesis. **Not submitted this tick** — 32 jobs are
   already in flight and the ladder must report first.

## 50. The frozen profile GENERALISES (4/4 families) and its shape is CHANNEL-SCALED — §47's narrowing is to the beta regime only, not to the architecture (cycle 48, end of tick)

All 20 `fz3-*` jobs landed. Scored against the pre-registration in
`bin/c48_frozen_ladder_p5.sh`:

| | result |
|---|---|
| **(A0)** H <= 1 and H(w) >= H(lay) in every family | **PASS — batch valid.** Heterogeneity is <= 0.7% of the floor at weightwise and <= 6% at nodewise in all four families. |
| **(A1)** profile falls >= 10x in every family | **CONFIRMED 4/4**: r10 264.6x, r18 69.3x, c100 23.3x, r34 16.6x. Window-stable in all four. |
| **(A2)** b architecture-insensitive | **NOT DECIDABLE at the stated threshold.** Both testable clauses PASS (all b in [0.2,0.6]; across-family spread 2.08x < within-family 6.26x) but the stated refutation "varies more than 2x" is crossed **by 3.8%**, with b a 3-point fit at n=2. §41(c) applies to our own pre-registration. |
| **(A3)** frozen s below each family's free value, all in [0.55,0.75] | **CONFIRMED**: r10 0.613, r34 0.738, c100 0.572 (R18 0.629). FINDINGS 42.4's frozen/free mechanism is not a ResNet18 artefact. |
| parameter-free exchangeability rejection | **4/4**: over-predicts layerwise by 127.0x / 45.4x / 18.5x / 13.6x. |

**So §47's narrowing is to the BETA REGIME and nothing else.** Off equilibrium the profile
is real, corrected, window-stable and replicated across three further architecture/dataset
pairs. At the adapted equilibrium it flattens (b = 0.065, R18 only).

**The sharpest form of the result, and it is new (FINDINGS 48.18).** A single exponent per
family hides the structure. Per-leg:

| | weight -> channel | channel -> layer |
|---|---|---|
| b, across all four families | **0.069 – 0.181** | **0.393 – 0.816** |

Steeper in **4 of 4**, and the within-family contrast (6.3x) is 3x the across-family
contrast in the fitted b (2.08x). **Correlation is nearly scale-free within a channel and
collapses beyond it: the correlation length is approximately the channel.** That is the
direct answer to "how does agreement vary with block size" and it is architecture- and
dataset-independent in shape, where the single fitted exponent is not.

## 51. `s` is INSTRUMENT-DEPENDENT and must not be used to compare architectures (cycle 48)

§48.13 recorded a gap between the agreement-derived and variance-derived `N_eff ~ m^s` and
named two candidate causes. With all four families measured on the SAME RUNS, **one is
eliminated**: matching the null (recomputing the variance-derived s with the uncorrected
pooled floor, as `frozen_agreement.py` uses) moves the mean gap only from +0.097 to
**+0.090**.

| family | agreement s | variance s |
|---|---|---|
| c100 | **0.572** (lowest) | **0.808** (highest) |
| r10 | 0.613 | 0.630 |
| r18c10 | 0.629 | 0.706 |
| r34 | 0.738 | 0.796 |

**The two instruments reverse the family ordering** — c100 goes from last to first.

**NEW STANDING RULE.** *`s` is a summary of a curve that is not a power law (its per-leg
slopes differ by up to 6.3x, FINDINGS 48.18) and it differs by up to 0.24 between two
functionals of the same probe series. Quote it only within one instrument and one family.
Never use `s` to rank architectures, and never quote it to three decimals.* This does not
disturb A3 above, which compares frozen to free **within** a family and **within** one
instrument — the only comparison `s` supports.

## 52. DECISION RECORD — cycle 48, final

Supersedes §46 and §49. All 32 submitted jobs completed within the tick; both queues are
back to 0/0 and nothing was cancelled.

1. **IDEA 3 is CLOSED at R18/CIFAR-10/m=6, budget-stable and positive** on the only
   statistic with no dial: **B − C = +4.941pp / +5.094pp** on grid mean, against a 1.113pp
   peak deficit (§42, §44). Coverage corroborates it from an independent metric — arm B
   reaches 85% and 90% at **6 of 7** grid points against C's 4 and A's 3 (FINDINGS 48.10).
   No further IDEA 3 jobs at this configuration.
2. **Direction C is the project, and it is now TWO results, both measured this tick.**
   (a) **Survives adaptation:** per-weight meta-gradients are not independent at the
   meta-optimum — free rho_s(w) = 8.888e-08, reproducing FINDINGS 44.3 to +5.1% — and that
   is the regime Adam-mini / Adalayer / SGG run in.
   (b) **Structure is set by distance from the meta-optimum:** short-range and
   **channel-scaled** off equilibrium (b = 0.07–0.18 within a channel, 0.39–0.82 beyond it,
   4/4 families, exchangeability rejected 13.6–127x), weak and approximately scale-free at
   it (b = 0.065, not rejected). A step-size adapter is a high-pass filter on meta-gradient
   correlation, suppressing 22.92x at k=1 and 0x at k=180,225.
3. **Ideas 1 and 2 stay dead.** Zero jobs, this cycle and the previous five.
4. **THE NEXT EXPERIMENT, and it is now sharply defined by the mechanism rather than by a
   gap in coverage.** The free arm was measured at ONE distance from the meta-optimum.
   §47's high-pass-filter reading predicts b varies CONTINUOUSLY with that distance. A
   **meta-stepsize ladder** — `--meta-stepsize` in {1e-4, 1e-3, 1e-2} x the four rungs,
   ~12 jobs on the frozen recipe with `--alg-meta Lion` — turns "frozen vs free" into a
   curve and makes the filter reading testable rather than a hypothesis. **Not submitted:**
   it should be pre-registered against a predicted monotone b(meta-stepsize) before it runs,
   and this tick has already put 32 jobs through.
5. **Second priority: the free-beta ladder.** Everything in 2(b) off-equilibrium is now
   4-family; everything at equilibrium is R18 only. 12 jobs would match them.
6. **Third: close FINDINGS 48.13** by matching `frozen_agreement.py`'s window — zero
   compute, and §51 makes it a question about the instrument rather than about the science.

## 53. The high-pass filter is a SWITCH, not a dial — and CORRECTIONS 49(2)'s "distance from the meta-optimum" wording is too strong (cycle 49)

CORRECTIONS 49(2) and 52(2) both say the structure is *"set by distance from the
meta-optimum"*, which reads as a continuous dependence. The four-quarter reduction of the
c48 runs (FINDINGS 49.1, `analysis/probe5_time_ladder.py` **32/32**, zero compute) measures
that dependence directly for the first time, with the frozen arm as a training-progress
control, and it is not continuous:

| gain (frozen rho_w / free rho_w), R18 | k=1 | channel | layer |
|---|---|---|---|
| Q1, before beta moves | **1.26x** | 0.80x | 0.70x |
| Q2 | 24.83x | 7.67x | 2.17x |
| Q3 | 28.26x | 6.38x | 0.84x |
| Q4 | 23.67x | 4.57x | 0.61x |

| claim | status |
|---|---|
| "a step-size adapter is a high-pass filter on meta-gradient correlation" | **STANDS, and is now measured as a transfer function rather than inferred from two exponents.** Monotone decreasing in k in 3 of 3 adapted quarters; ~1 at layer scale. |
| "the structure is set by DISTANCE from the meta-optimum" (49(2), 52(2)) | **TOO STRONG.** The gain saturates within one quarter and is then flat to ±10% over the remaining three. On the time axis this is a switch. Write *"present before the step size has adapted, absent after"*, not *"varies with distance"*, until `ml5-*` supplies the eta_meta axis. |
| Q1 gain ~1 at every scale | **NEW, and it is the instrument's internal control.** The reducer reads 1.0 when there is nothing to measure, on the same runs that later read 24x. Not assumed — measured. |
| the 22.8x / 22.92x per-weight suppression | **REPRODUCED a third time** at 23.67x (Q4), from a third window and a third statistic. |

**And this cycle's own pre-registration failed, in a way worth recording.** The b1(t) trend
test was written as a RATIO b1(Q1)/b1(Q4). The free arm's weight→channel exponent changes
sign across the run (+0.170 → −0.081), so the ratio is undefined and the reducer printed a
meaningless −2.10x. Scored on the difference, the free arm moves −0.252 against the frozen
control's −0.073 — **3.4x the control, and the only arm that crosses zero** — so training
progress is a real but minority contributor, not the cause.

**NEW STANDING RULE, and it is the fourth of this family after thresholds (§41c), nulls
(§33) and windows (§45).** *A pre-registered test statistic must be defined over the full
range the quantity can take. A ratio may only be registered for a quantity that cannot
change sign; register a difference otherwise.* The b1 ratio was registered without checking
that b1 is a slope and slopes cross zero. The reducer now detects the sign change, refuses
the ratio, prints the difference, and labels the difference-based reading POST-HOC in its
own output — so the substitution cannot later be mistaken for the registered test.

## 54. DECISION RECORD — cycle 49

1. **The zero-compute experiment was the right first move and it produced the cycle's
   result.** Before spending a job, the same bytes that produced CORRECTIONS 45–52 were
   re-reduced on a finer time axis with a control that had never been used as one. That
   gave the filter's transfer function, the Q1 internal control, and §53's narrowing —
   none of which needed the compute CORRECTIONS 52.4 had budgeted for.
2. **A CONCURRENT SESSION is operating on this repo and it submitted the meta-stepsize
   ladder first** (`ml5-*`, 36 jobs on alice2, FINDINGS 49.2). Its script is strictly
   better resourced than this session's, so this session's ladder was **retired unrun**
   rather than duplicated. Nothing was cancelled. **Whoever reviews this must know that two
   agents were writing to `docs/` and submitting to the same accounts in the same hour** —
   check for merge damage in FINDINGS/CORRECTIONS numbering before trusting any section
   ordering.
3. **Submitted: 18 jobs on alice, `ff5-*` (4702123–4702140)** — the free-beta FAMILY
   ladder, R10 / R34 / CIFAR-100, three rungs, 2 seeds, byte-matched to `fz3` with
   `--alg-meta fixed` -> Lion. It is the complement of `ml5`, which is R18/CIFAR-10
   throughout, and it attacks the campaign's largest remaining asymmetry: **half (a) — the
   headline, that per-weight meta-gradients are not independent AT the adapted equilibrium
   — is measured in exactly one architecture**, while its off-equilibrium half is 4-family.
   Pre-registered C0–C4 in the script header, with the resolution of all nine rungs
   computed from the fz3 arms BEFORE submission and the **two thin rungs named in advance**
   (c100 weightwise at ~1.5x, r10 layerwise at ~0.5x) so that a null in either cannot later
   be read as a discovery.
4. **C2 makes §53's gain table pre-registered and 4-family.** The table in FINDINGS 49.1 is
   one family and its b1 reading was post-hoc; `ff5` scores it against fz3 as a
   registered prediction (gain in [8x,60x] at k=1, monotone decreasing in k, ~1 at layer).
5. **Ideas 1 and 2 stay dead.** Zero jobs, this cycle and the previous six.
6. **Next tick, in order.** (a) Reduce `ff5-*` with `probe5_window.py` and
   `probe5_time_ladder.py ../probes_ff5 ../probes_fz3`, scoring C0–C4; C0.2 (weightwise
   n_tot must equal fz3's exactly) is a per-family gate. (b) Score `ml5-*` against ITS
   header's L0–L3, and **check L0's clip-saturation fraction before quoting the 1e-2
   column** — a pinned beta mimics a frozen one and would read as the filter switching off.
   (c) Put §53's switch-vs-dial question to the eta_meta axis: if the gain at k=1 varies
   smoothly across `ml5`'s three rungs it IS a dial and §53's narrowing is lifted; if it
   is ~1 at 1e-4 and ~24x at both 1e-3 and 1e-2, the switch reading is confirmed on a
   second, independent axis. (d) CORRECTIONS 52.6 (close FINDINGS 48.13 by matching
   `frozen_agreement.py`'s window) remains unspent and is still zero compute.

## 55. FINDINGS 48.13 CLOSES, and CORRECTIONS 51's standing rule is REPLACED by a better one (cycle 49)

§51 forbade using `s` to rank architectures because two functionals of the same probe
series differed by up to 0.24 and reversed the family ordering, with no cause identified.
The cause is now identified, tested against a pre-registration committed before first
contact with the data (3f9fd69), and it is neither of the two candidates §51 left open.

**The agreement instrument reads the BIAS CHANNEL; the variance instrument does not.**
`neff_from_agreement` inverts `mean_t max(p_t, 1−p_t)` = 0.5 + `mean_t|p_t − 0.5|`,
i.e. deviation from the FIXED POINT 0.5. `twochannel.decompose` uses `np.var(p_t)`,
i.e. deviation from the SAMPLE MEAN. The difference is exactly b = pbar − 0.5, which
FINDINGS 44.3 measured at 85% of frozen total deviation.

| claim | status |
|---|---|
| "the window `frozen_agreement.py` reduces has not been matched" (48.19, §52.6) | **ELIMINATED BY READING THE CODE.** `arm_stats` defaults to `window=0.5`. The table was window-matched all along. |
| "the two instruments differ by up to 0.24 on the same runs" (§51) | **EXPLAINED.** Debiasing cuts the mean gap 0.143 → **0.019**, 3/3 families (FINDINGS 49.3). |
| "the two reverse the family ordering; never use `s` to rank architectures" (§51) | **REPLACED, not upheld.** The reversal is an artefact of the raw instrument. Debiased and variance orderings are identical (`r10 < c100 < r34`). |
| residual disagreement after debiasing | **NAMED AND SMALL.** First vs second absolute moment; they coincide only for Gaussian p_t. 0.019 is non-Gaussianity, not a bug. |

**NEW STANDING RULE, replacing §51's.** *`s` may be compared across families, but only
within a bias-free instrument. The RAW agreement estimator (`frozen_agreement.py`,
`neff_ladder.py`) is contaminated by a granularity-dependent bias channel and must not be
used for any cross-family or cross-regime comparison. Use the debiased agreement statistic
or the variance statistic; they agree to 0.019.* §51's caution against quoting `s` to three
decimals stands — the residual is at the second decimal.

## 56. ~HALF of the published frozen/free `s` gap was the instrument — FINDINGS 42.4 and A3 are AMENDED, not withdrawn (cycle 49)

The contamination §55 identifies is **one-sided**, and it falls on the arm the campaign's
mechanism claim is built from. Weightwise bias share: **0.659 frozen, 0.003 free**. Frozen
beta sits off the meta-optimum and carries a large b; free beta sits at it and carries
almost none. Every published frozen/free `s` contrast was therefore measured with an
instrument that is badly contaminated in one arm and clean in the other.

On the controlled, byte-matched R18/CIFAR-10 pair (`p5` vs `fr5`, FINDINGS 49.4):

| instrument | frozen s | free s | gap |
|---|---|---|---|
| agreement RAW — what FINDINGS 42.4 and 48.19's A3 quote | 0.618 | 0.961 | **0.343** |
| agreement DEBIASED | 0.754 | 0.932 | **0.178** |
| variance | 0.759 | 0.947 | **0.188** |

| claim | status |
|---|---|
| "frozen `s` is well below its own free value" (42.4, A3) | **STANDS**, on two independent clean instruments that agree to 0.010. |
| the SIZE of that gap, 0.343 (R18) | **AMENDED to ~0.18.** About **48% of the published effect was the bias channel.** Any sentence quoting the magnitude must be re-derived; sentences quoting the direction need not. |
| A3's pre-registered band "frozen s in [0.55, 0.75], 4/4" | **INSTRUMENT-SPECIFIC.** True raw (0.572–0.738); **fails in 2 of 3 families debiased** (0.690 / 0.783 / 0.819). Quote the band only with the instrument named. |
| A3's *verdict* (frozen below free in every family) | **UNAFFECTED** — free-arm raw and debiased agree to 0.029, so the free comparators were approximately clean already. |

**AND THE HEADLINE GETS A BETTER STATEMENT OUT OF THIS, not a worse one.** `N_eff/m` at
weightwise, variance instrument, steady half: **0.501 free, 0.042 frozen**. *At the adapted
equilibrium — the regime Adam-mini / Adalayer / SGG actually run in — 11.17M per-weight
meta-gradients carry the independent information of 5.6M. Half the noise-averaging the
1/sqrt(N) assumption promises is not there.* That is one number, on the clean instrument,
in the right regime, and it does not need `rho` or an exponent to say it.

## 57. DECISION RECORD — cycle 49, final

Supersedes §54's items 1 and 6(d); items 2, 3, 4 and 5 stand unchanged.

1. **Two zero-compute results this tick, and the second one corrected a published
   magnitude.** (a) The filter's transfer function with an internal control (§53).
   (b) FINDINGS 48.13 closed and ~48% of the frozen/free `s` gap reattributed to the
   instrument (§55, §56). Neither needed a job. **The lesson for the next tick is explicit:
   before submitting, ask what the bytes already on disk have not been asked.**
2. **The campaign's most-quoted mechanism number is now smaller and better founded.**
   Nothing about the direction, sign or significance of the frozen/free contrast changed;
   its magnitude halved and it gained a second, independent, clean instrument that agrees
   to 0.010. Report it as an amendment (§56), never as a withdrawal, and never quote the
   0.343 again.
3. **Queues at tick end: alice 18 PENDING (`ff5-*`, this session), alice2 25 PENDING /
   11 RUNNING (`ml5-*`, the concurrent session).** Nothing cancelled. 18 jobs submitted by
   this session, all on alice.
4. **Next tick, in order.** (a) Reduce `ff5-*`, scoring C0–C4, and run `neff_instrument.py`
   on it — the free family arms are the missing half of §56's table and will say whether
   the ~48% reattribution is R18-specific. (b) Score `ml5-*` against L0–L3, clip-saturation
   fraction FIRST. (c) Re-derive every `s` in FINDINGS and the draft under the clean
   instrument and mark each occurrence with the instrument it came from — §55's rule is
   not retroactive by itself and the raw numbers are scattered through 42.4, 48.19 and
   earlier. (d) §53's switch-vs-dial question, on `ml5`'s eta_meta axis.

---

## 58. CORRECTIONS 53 IS WITHDRAWN — the high-pass filter is a DIAL, not a switch (cycle 50)

**What 53 said.** *"The high-pass filter is a SWITCH, not a dial... write 'present before the step
size has adapted, absent after', NOT 'varies with distance from the meta-optimum' until `ml5-*`
supplies the eta_meta axis."* It was an honest reading of TWO points (beta frozen, beta free at
ms=1e-3) plus a time axis, and it explicitly deferred to this batch.

**`ml5-*` supplied the axis, and the third point lands between the two.** Steady half, R18/CIFAR-10,
weightwise, one batch, one instrument, n=3 per rung (FINDINGS 50.1):

| | frozen | ms 1e-4 | ms 1e-3 |
|---|---|---|---|
| b (steady) | 0.343 | **0.219** | 0.081 |
| suppression at k=1 | 1.00x | **3.37x** | 21.09x |
| suppression at layerwise | 1.00x | 0.75x | 0.86x |
| N_eff/m | 0.042 | **0.129** | 0.481 |

Smooth, monotone, and b(1e-4) = 0.219 falls inside the pre-registered [0.10, 0.30] band. **Write
"the suppression grows with the meta-stepsize and is confined to scales below the channel."** The
"two-state contrast" language is withdrawn. CORRECTIONS 49(2)'s original "distance from the
meta-optimum" wording is REINSTATED, with the drive named: the distance is set by the meta-stepsize.

**Why this is not a reversal-of-a-reversal to be embarrassed about.** 53 was written with two
points and said so, named the experiment that would decide it, and pre-registered the band the
answer had to fall in. The answer fell in the band. That is the process working.

**The ms=1e-2 rung does NOT refute this, and the reason was written down in advance.**
`c49_ms_ladder_p5.sh` pre-registered BETA_CLIP saturation as a KNOWN RISK with the explicit
fallback "decide L1 on {1e-4, 1e-3} plus the frozen anchor only" if the guard binds on >50% of
steps. It binds on 88.0% / 86.8% of records at layerwise / blk6. And the confounded arm behaves
exactly as the pre-registration predicted a clipped arm would — like a FROZEN one: b = 0.328
against frozen 0.343 (Δ0.015), N_eff/m = 0.050 against 0.042. **A named hazard that fires in the
predicted direction with the predicted magnitude is a validity check, not a discovery, and must
not be written up as one.**

**STANDING RULE (5)** — the fifth, after thresholds / nulls / windows / sign-ranges:
*a registered fraction must name its DENOMINATOR.* "The fraction of steps at which the guard binds"
is 0.19–28.1% per (record,tensor) cell and 11.5–88.0% per record — **opposite sides of the
pre-registered 50% line**. `analysis/c50_dial.py` (selftest 24/24) prints both and takes the
conservative reading. Had only the favourable denominator been reported, this tick would have
claimed a genuine non-monotonicity in b.

## 59. THE HEADLINE IS NO LONGER A ResNet18 RESULT (cycle 50)

`ff5-*` passed C0 18/18 and confirmed C1 and C3 in 3 of 3 families. The sentence the project is
for now carries four architecture/dataset combinations (FINDINGS 50.2):

> At the adapted equilibrium, per-weight meta-gradients carry between **16% and 55%** of the
> independent information their count implies — N_eff/m = 0.163 (R10) / 0.481 (R18) / 0.552 (R34) /
> 0.305 (CIFAR-100), against 0.033–0.082 with beta frozen.

**What to quote and what not to.**
* **QUOTE** N_eff/m, the variance instrument, the steady half, and the family. Never a bare `s`,
  never a raw-instrument `s`, never `s` to three decimals.
* **QUOTE** the per-leg exponents, not the pooled b. Free b1 (within-channel) is −0.045 / −0.013 /
  −0.099 / −0.059 across the four families — flat, in 4 of 4 — while b2 (beyond-channel) stays
  0.17–0.42. *The correlation length is approximately the channel, and adaptation SHARPENS that.*
* **DO NOT** write "the transfer function is 23x". Its SHAPE is architecture-independent (monotone
  in k, ≈1 at layer scale, 4 of 4); its DEPTH is not (≈5x for R10/CIFAR-100, ≈22x for R18/R34).
  The pre-registered [8x,60x] band fails in 2 of 3. Report shape and magnitude separately —
  `c49_free_family_ladder.sh` bundled them into one prediction and that was the defect.
* **DO NOT** count C4 as 3/3. r10's 7.8x is between the 5x pass bar and the 10x refutation bar.
  It is UNDECIDED and is written that way.

## 60. AN UNEXPLAINED EFFECT IS RECORDED AS UNEXPLAINED — the late-training rebound (cycle 50)

In R10/CIFAR-10 and R18/CIFAR-100, free-arm rho_w at k=1 **rises ×2.7–2.9 in the last quarter**
while the byte-matched frozen control keeps decaying ÷1.9–2.0. In R18 and R34 it does not. The
decomposition closes to <1% (FINDINGS 50.3), so the effect is arithmetic on measured levels, not a
fit artefact.

**Two candidate mechanisms were tested at zero compute and both fail.** (i) BETA_CLIP saturation:
0.0% of tensor betas at either guard in every weightwise arm, every quarter, every family.
(ii) beta velocity collapse: flat to ±30% across quarters against a 5x gain move. **This is written
down as an open effect with two mechanisms excluded, not as a finding with a story attached.** The
post-hoc b1≈0 separator in FINDINGS 50.3 is a hypothesis at n=4 families and is labelled as one.

**Instrumentation gap, for whoever runs the next probe:** the per-coordinate clipped fraction is
not written — only per-tensor beta and the global beta_true_min/max — so (i) is *unsupported*
rather than *excluded*. A one-line addition to PROBE5 (count of coordinates within eps of either
guard) would close it permanently and costs nothing at run time.

## 61. DECISION RECORD — cycle 50

**Data state.** Both queues 0 P / 0 R at tick start; all 54 cycle-49 jobs complete. 18 ff5 + 36 ml5
probe dirs synced (703 MB + 704 MB). CSV regenerated to 1611 runs. Five reducers selftested before
use (41/41, 32/32, 19/19, 15/15, and the new `c50_dial` 24/24).

**Decisions taken, and why.**
1. **CORRECTIONS 53 WITHDRAWN, filter re-described as a dial.** Three unconfounded points, monotone,
   with the middle one inside its pre-registered band. → §58.
2. **The ms=1e-2 column is reported as CONFOUNDED**, per the batch's own pre-registered fallback,
   under the conservative denominator. Not quoted in any b or gain claim. → §58.
3. **The headline is promoted from 1 family to 4.** C1 and C3 confirmed 3/3; both rungs named in
   advance as thin cleared. → §59.
4. **C2 is SPLIT into shape (confirmed 4/4) and magnitude (fails 2/3)** rather than scored as one
   prediction. C4's r10 is recorded as UNDECIDED, not as a pass. → §59.
5. **The late-training rebound is recorded as UNEXPLAINED** with two mechanisms excluded. → §60.
6. **The beta-displacement collapse is recorded as a NEGATIVE** so it is not re-run. → FINDINGS 50.5.
7. **STANDING RULE (5) added**: a registered fraction must name its denominator. → §58.
8. **NOT DONE, and deferred deliberately:** the "re-derive every `s` in FINDINGS and the draft under
   the clean instrument" sweep (cycle 49's item (c)). It is a documentation pass over scattered raw
   numbers, it produces no new science, and this tick had 54 jobs of fresh data to score against
   pre-registrations. §59 states the quoting rule that makes the sweep mechanical when it happens.

**Submitted.** `bin/c50_wideclip_ladder.sh` — 18 jobs on alice2, the ONE experiment that closes the
one refuted prediction of the tick. See §58: b(1e-2) = 0.328 is attributed to the clip guard, and
that attribution is currently an inference from a pre-registered hazard, not a measurement. The
batch re-runs ms=1e-2 and ms=1e-3 with BETA_CLIP widened, so the clip becomes an experimental
variable instead of a fixed confound. Pre-registration W0-W3 in the script header, written before
submission.

**Queues at tick end.** alice 0 P / 0 R. alice2 18 P / 0 R.

---

## 62. THE WIDE-CLIP BATCH MOVED THE WRONG WALL — W2 fails, W1 is uninterpretable, and the cause is an instrument-resolution error, not the science (cycle 51)

`c50_wideclip_ladder.sh` chose which bound to move from one sentence in its own header:

> "The HIGH bound is at 0.00% in EVERY arm of the whole 36-job batch. So a large meta-stepsize does
> not blow the step size UP — it overshoots DOWNWARD ... Therefore: LOW bound −15 → −30. HIGH bound
> UNCHANGED at −2.3026, **because it provably never binds**."

That 0.00% came from the probe's per-TENSOR `beta[]` list. **The clamp is applied per COORDINATE.**
Read at the resolution the clamp operates at — from `beta_true_max`, already present in the same
records — the high guard binds on **95.4% of records** at weightwise ms=1e-2, from record **92**,
against the low guard's 91.9% from record 162 (FINDINGS 51.1). The batch widened the wall that was
binding *less*.

| pre-registered item | verdict |
|---|---|
| W0.1 / W0.2 validity | **PASS** 18/18 |
| W0.3 null control at ms=1e-3 | **PASS on four independent statistics** |
| **W2** (relief must reach <5% of layerwise records) | **FAIL: 88.0% → 71.7%** |
| **W1** (the primary test) | **UNINTERPRETABLE** — W2's own text: *"If it does NOT fall ... W1 is UNINTERPRETABLE rather than refuted."* Honoured |
| W3 | not scorable |

**The batch's instruction to score W2 before W1 is what saved the tick.** Read in the registered
order, b(1e-2) = 0.364 ≥ 0.25 fires W1's REFUTATION branch and this cycle would have announced *"the
dial is non-monotone with an interior optimum near ms=1e-3"* — a bigger, more interesting, and
wrong claim. **A pre-registered ordering is a control, not paperwork.**

**CORRECTIONS 58 is NOT disturbed.** Its dial rests on {frozen, 1e-4, 1e-3}, and 51.2 strengthens
its treatment of the fourth rung: ms=1e-2 is not a confounded point on the dial, it is **not a point
on the dial at all**, because the log-stepsize distribution there spreads ballistically at ~99% of
the maximum Lion speed and exactly fills whatever box it is given (12.70 → 12.70; 27.70 → 27.70).
Write **"boundary-dominated"**, not "confounded", and do not quote it in any b or gain claim.

## 63. THE INSTRUMENTATION GAP CORRECTIONS 60 NAMED IS NOW CLOSED — PATCH_CLIPCOUNT (cycle 51)

CORRECTIONS 60 wrote, one tick before it cost us a batch:

> "the per-coordinate clipped FRACTION is not written — only per-tensor beta and the global
> beta_true_min/max — so (i) is *unsupported* rather than *excluded*. A one-line addition to PROBE5
> ... would close it permanently and costs nothing at run time."

It was named, priced at zero, and not done. **Done now.** `PATCH_CLIPCOUNT` writes `n_at_lo`,
`n_at_hi` and `n_beta` per probe record — the per-(record, coordinate) denominator, which no probe
written before this tick can supply. Applied to **both** accounts' `HF.py`, backed up to
`HF.py.pre_clipcount.bak`, compile-checked, idempotent, and verified writing on a live `cl5` job
(`n_beta=62, n_at_lo=0, n_at_hi=0` at step 0). Both new batches guard on its presence.

**STANDING RULE (6)**, the sixth, after thresholds / nulls / windows / sign-ranges / denominators:
*a fraction must be measured at the resolution the mechanism operates at.* Rule 5 forced a
denominator to be named; it did not stop a correctly-named denominator from being computed over the
wrong objects. Three denominators are now distinguishable and disagree by two orders of magnitude
on the same bytes (0.47% of tensor cells / 29.0% of tensor-records / 95.4% of coordinate-records).

## 64. CORRECTIONS 61(5) IS AMENDED — mechanism (i) for the late-training rebound was never tested (cycle 51)

61(5) recorded the Q4 rebound as *"UNEXPLAINED with two mechanisms excluded"*. Mechanism (i), clip
saturation, was rejected on "0.0% of tensor betas at either guard" — the §63 error. At coordinate
resolution the four families separate perfectly (FINDINGS 51.3): the two that rebound (r10 ×2.73,
c100 ×2.87) are the two with **100% of Q4 records at the ceiling**; the two that do not are at
28.5% (r18) and **0.0%** (r34).

| claim | status |
|---|---|
| "the rebound is unexplained" | **STANDS** — a 4-family post-hoc separation is a hypothesis, not a cause |
| "mechanism (i) FAILS" (61(5)) | **WITHDRAWN.** It was measured at the wrong resolution and is now the *leading* candidate |
| "mechanism (ii), beta-velocity collapse, fails" | **STANDS** — flat to ±30%, unaffected by resolution |
| CORRECTIONS 60's own "*unsupported*, not *excluded*" | **This was the correct wording all along.** 61(5) over-stated it when summarising |

`uc5-*` is the first actual test, with U2 pre-registered in both directions.

## 65. "AT THE ADAPTED EQUILIBRIUM" IS A STATEMENT ABOUT THE BULK, AND MUST NOT BE READ AS CONVERGENCE (cycle 51)

The headline sentence (§59) opens *"At the adapted equilibrium…"*. With the floor moved out of the
way so nothing stops it, the minimum log-stepsize is **still descending at 89–100% of the maximum
Lion speed in the last quarter of the run, in 9 of 9 arms** (FINDINGS 51.2). Nothing has converged.

The bulk *has* approximately settled — per-tensor mean betas drift at a median 3–21% of max speed in
the last quarter, with 0–9.7% of tensors above 90%. So the phrase is defensible for the bulk and
false for the tail, and the correlation statistics are computed over **all** coordinates.

**Quoting rule.** Write *"with beta free"* or *"at the adapted operating point"*. Do not write
*"at the adapted equilibrium"* without this caveat, and never use it to argue that the measurement
is budget-independent — that has not been shown at any budget.

**This does not touch the measurement.** N_eff/m is what it is over the steady half; only the word
"equilibrium" over-claims.

## 66. DECISION RECORD — cycle 51

**Data state.** Both queues 0 P / 0 R at tick start; all 18 `wc5-*` jobs complete. Probes synced
(458 MB). CSV regenerated to **1629 runs** (+18). Five reducers selftested before use
(26/26 new `c51_wideclip`, 41/41, 19/19, 32/32, 24/24).

**Decisions taken, and why.**
1. **W2 scored FIRST and honoured when it failed.** W1 is recorded UNINTERPRETABLE, not refuted.
   The registered ordering prevented a false headline. → §62.
2. **The ms=1e-2 rung is re-described as BOUNDARY-DOMINATED, not confounded** — measured
   (box-filling at ~99% of max Lion speed in two boxes), not inferred. CORRECTIONS 58 stands. → §62.
3. **STANDING RULE (6) added**: a fraction must be measured at the resolution the mechanism
   operates at. → §63.
4. **PATCH_CLIPCOUNT applied to both accounts** — the zero-cost close CORRECTIONS 60 named and 61
   deferred. Deferring it cost 18 jobs. → §63.
5. **CORRECTIONS 61(5) amended**: mechanism (i) was never tested, and is now the leading
   candidate for the rebound. → §64.
6. **The headline gains its first box-sensitivity number and keeps its meaning:** N_eff/m
   0.4808 → 0.5189 for a 2.2× deeper box; clip accuracy-neutral at +0.027 pp over 6 matched cells.
   This sets the ±0.10 bar both new batches use. → FINDINGS 51.4.
7. **"At the adapted equilibrium" is narrowed to the bulk.** The tail does not converge. → §65.
8. **Ideas 1 and 2 stay dead.** Zero jobs, this cycle and the previous eight.

**Submitted, 36 jobs, 18 per account, both queues within the 40-pending cap.**
* **`cl5-*`, 18 on alice2** (`bin/c51_ceiling_ladder.sh`) — the CEILING ladder at R18/ms=1e-3, where
  the headline lives. LO fixed at −30 (measured non-binding); HI ∈ {−4.6052, **0.0**} with wc5's
  HI=−2.3026 as the free middle point. The predicted-never-to-bind HI=0.0 arm is the **first
  completely unclipped measurement of N_eff/m** this campaign has taken. X0–X3 pre-registered, with
  **X0.3 (did the ceiling bite?) scored before X1** — the W2 lesson, applied deliberately.
* **`uc5-*`, 18 on alice** (`bin/c51_unclipped_family.sh`) — the UNCLIPPED FAMILY control, both
  walls out to −30:0.0, on the two families whose Q4 ceiling occupancy is 100% (r10, c100) plus
  **r34 as the built-in null** (0.0% occupancy; it must not move). It tests whether the two numbers
  setting the LOW end of the published "16% to 55%" range are partly the box, and it is the first
  test of mechanism (i) for the rebound. U0–U3 pre-registered, U0.3 and U0.4 scored first.

**NEXT TICK, in order.** (a) `cl5`: X0.3 dose, then X0 null (layerwise), then **X1** — if either
new arm leaves [0.42, 0.62], §59's 4-family headline needs a box column before it is written down.
(b) `uc5`: U0.3 (r34 null) **before** anything else, then U0.4, then U1, then U2 against
`probe5_time_ladder.py ../probes_uc5 ../probes_fz3`. (c) Both batches carry `n_at_lo`/`n_at_hi`, so
report the per-(record, coordinate) denominator alongside the per-record one for the first time.
(d) Still unspent, still bookkeeping not science: re-derive every raw-instrument `s` in FINDINGS
under the clean instrument (§59 makes it mechanical).

**Queues at tick end.** alice **18 P / 0 R** (`uc5`). alice2 **15 P / 3 R** (`cl5`).

---

## 67. FINDINGS 51.7's "THERE IS NO BOX-FREE CONFIGURATION" IS WITHDRAWN — it extrapolated a startup velocity (cycle 52)

51.7 was a pre-registered addendum, committed before the batches landed so it could not be fitted
afterwards. That discipline worked exactly as intended: it is now scoreable, and **it is wrong**.

It predicted that at HI=0.0 the ceiling would still bind at r10 weightwise (record ~1388/1458) and
be borderline at r18 weightwise (1871–2007), concluding: *"There is no box-free configuration of
this algorithm at this budget."* Measured (FINDINGS 52.1/52.2): **0.0% of records and 0.0000% of
coordinates at either guard**, in r10-w, r34-w and all three r18 rungs. r18's top coordinate ends
at −2.158 against a ceiling of 0.0 — the projection missed by 2.16 log units.

**THE ERROR, and it is the same family as the one 51.7 itself was written to fix.** The
"92–100% of maximum Lion speed" is the velocity of the **startup segment**. The top coordinate
decelerates ~9x at R18 (0.076 vmax in Q4) and ~3.3x at R10 (0.289). CORRECTIONS 62 established
that a *fraction* must be measured at the resolution the mechanism operates at; this is the same
mistake in the time axis instead of the parameter axis.

**STANDING RULE (7)**, the seventh, after thresholds / nulls / windows / sign-ranges /
denominators / resolutions:

> *A rate used to extrapolate must be measured on the segment being extrapolated FROM, not on the
> whole run. Startup velocities are not steady velocities, and this campaign's own transients run
> 3–12x the steady rate. Quote the window with every rate, exactly as with every fraction.*

**WHAT REPLACES IT.** A box-free configuration exists at ms=1e-3 and it is `BETA_CLIP=-30:0.0`.
**Worst-seed headroom at R18 weightwise is 22.8 epochs and at R10 5.6.** **Report the worst seed,
never the mean** — a mean of per-seed records-to-hit is a mean of ratios and one slow seed sends it
to infinity; the mean trajectory says 56.6 epochs where the worst seed says 22.8.

**AND THE MARGIN IS THIN, SO SAY THIN.** `bl5-*` spends 20 extra epochs at R18 against 22.8 of
worst-seed headroom. That is MARGINAL. It is fundable because the projection is an **upper bound**
— the climb velocity has fallen from 0.95 vmax at startup to 0.17 in Q4 and is still falling — but
"upper bound" is exactly the reasoning 51.7 got wrong in the other direction, so it earns a gate
and not a presumption. B0.3 is scored first for precisely this reason.

51.7's *scoring instructions* were sound and are kept: score the binary bar first, the
dose-response second, never let the second overwrite the first. Only its projection is withdrawn.

## 68. THE HEADLINE IS BOX-FREE. CORRECTIONS 59 NEEDS NO BOX COLUMN. (cycle 52)

The threat CORRECTIONS 62–66 opened is closed. N_eff/m (weightwise, variance, steady half):

| family | published box | BOX-FREE (−30:0.0) | Δ |
|---|---|---|---|
| R18 | 0.4808 | **0.5045** | +0.024 |
| R10 | 0.1632 | **0.1571** | −0.006 |
| R34 (the null) | 0.5517 | **0.5474** | −0.004 |
| **CIFAR-100** | 0.3047 | **0.3124** | **+0.008** |

Across FOUR boxes at R18 — spanning 15 log units of floor and 4.6 of ceiling — the total span is
**0.076** against a ±0.10 bar registered three times independently. At R10 the entire box was
removed from an arm whose Q4 ceiling occupancy was **100.0%**, and the number moved **−0.006**,
which is no more than the null's own **−0.004**. The exponent agrees: b(steady) span 0.039 across
the same four boxes (bar 0.05).

**QUOTE THIS, unchanged, and without a box caveat for R10/R18/R34:** *at the adapted operating
point per-weight meta-gradients carry 16%–55% of the independent information their count implies.*
**Add the box to the methods, not to the claim.** `uc6-*` landed inside the same tick and closed
the fourth family (FINDINGS 52.10): CIFAR-100 goes from 100.0% Q4 ceiling occupancy to **0.0%** on
all three rungs and N_eff/m moves **+0.008**. **All four families are now measured box-free**, with
a box-free range of 15.7%–54.7% — the published "16% to 55%" survives to the significant figures it
was quoted at.

**A DIRECTIONAL PREDICTION FAILED AND IS RECORDED AS FAILED.** `c51_unclipped_family.sh`
registered "unpinning should move N_eff/m UP, because coordinates frozen against a common wall
agree for a reason that has nothing to do with the meta-gradient." It did not move at all. The
pass is a pass on the ±0.10 bar, **not** a confirmation of the mechanism story, and the mechanism
story is not to be repeated.

**AND A NON-RESULT WORTH BANKING.** X3's "the ceiling is load-bearing for stability" branch did
not fire: nothing collapsed at alpha_max = 1.0, and the top coordinate stops at alpha ≈ 0.12 at
R18 on its own. **At ms=1e-3 the operating point is INTERIOR.** The box was never doing the work
anyone feared it was doing.

## 69. CORRECTIONS 61(5) IS REINSTATED — on evidence this time, not on the wrong denominator (cycle 52)

The bookkeeping arc, in full, because it is instructive:

1. **60** recorded the Q4 rebound as unexplained, with two mechanisms tested and both failing —
   and correctly noted the honest status of mechanism (i), clip saturation, was *"unsupported,
   not excluded"*.
2. **61(5)** then wrote it up as "both mechanisms fail".
3. **64** WITHDREW 61(5): (i) had been rejected on the per-TENSOR column, which reads 0.00%
   everywhere, so it had never actually been tested. At coordinate resolution the four families
   separated **perfectly** (rebound YES ⇔ 100.0% Q4 ceiling occupancy), making (i) the *leading*
   candidate.
4. **This tick tested it.** r10's Q4 ceiling occupancy went **100.0% → 0.0%** and the rebound
   ratio went **2.690 → 2.701** — unchanged to within 0.5% (FINDINGS 52.4).

**61(5)'s conclusion was right and its evidence was wrong.** It is reinstated with the correct
evidence: clip saturation is **excluded by test**. FINDINGS 51.3's perfect separation is a
**coincidence at n=4 families**, and 64's "leading candidate" reading is withdrawn in turn.

The rebound remains **OPEN**, now with two mechanisms genuinely dead rather than one dead and one
untested. That is a worse scientific outcome than a confirmation and a better record than 61(5).
**THE REPLICATION LANDED IN THE SAME TICK.** `uc6-*`'s V3: c100's Q4 ceiling occupancy went
**100.0% → 0.0%** and the rebound ratio went **2.577 → 2.583**, unchanged to 0.2%. Two independent
families, two independent tests, same answer. Clip saturation is excluded at n=2 families, not n=1.

## 70. A NEW POSITIVE RESULT, SCOPED TO ms=1e-3: THE INFORMATION FRACTION IS WORST AT NODEWISE (cycle 52)

N_eff/m is **non-monotone in the group count**, with its minimum at **nodewise**, in **9 of 9**
(family × box) cells at ms=1e-3 — R10 / R18 / R34 / CIFAR-100 crossed with the clip boxes tested,
including a box-free arm in every one of the four families (FINDINGS 52.5, 52.10). R18 box-free:
lay **0.726** / node **0.402** / w **0.504**. CIFAR-100 box-free: lay **0.532** / node **0.246** /
w **0.312**.

**THREE CONSTRAINTS ON HOW THIS MAY BE WRITTEN, all of them load-bearing:**

1. **Scope it to ms=1e-3.** At ms=1e-4 the argmin is weightwise (ml5 m4: 0.700 / 0.170 / 0.129).
   That is a **genuine counterexample** and must be reported, not omitted. The shape is a property
   of the ms=1e-3 operating point, not of the partition alone. (ml5 m2 also has argmin w, but it
   is boundary-dominated per 62 and is quoted by nothing.)
2. **It is a FRACTION.** N_eff itself rises with m — 45 → 5,791 → 5,636,970 at R18. Never write
   "nodewise carries the least information"; write "retains the smallest fraction of the
   information its count implies".
3. **It is not yet budget-tested.** `bl5-*` registers the ordering `node < w < lay` as prediction
   B2.5. If it fails at 40 epochs, the shape is budget-specific and must not be written as a
   property of the partition at all.

Subject to those, this is the most directly paper-relevant thing the campaign has produced since
the sign-agreement measurement itself: **the Adam-mini / Adalayer / SGG line places its blocks at
nodewise-or-coarser on the premise that within-block averaging recovers independent information,
and at the operating point our headline is quoted at, that is the worst available partition.**

## 71. DECISION RECORD — cycle 52

**What the data said.** All 18 `cl5` and 12 of 18 `uc5` jobs landed and were scored against their
written pre-registrations by `analysis/c52_boxfree.py` (selftest 27/27).

1. **X0 / U0 validity, X0.3 / U0.4 dose, X0.3(3) / U0.3 nulls, X3 stability, U3 / X2 accuracy and
   profile: EVERY gate PASSES.** The dose checks passed at both ends of both ladders, so nothing
   this tick is uninterpretable — the first tick since 49 of which that is true.
2. **X1 and U1 PASS: the headline is not a box artefact** (→ 68).
3. **U2's refutation branch fires: clip saturation is excluded** (→ 69).
4. **51.7's projection is refuted; a box-free configuration exists** (→ 67).
5. **A new, box-invariant, ms=1e-3-scoped positive result: the nodewise minimum** (→ 70).
6. **6 jobs void on a `--NN-name` bug in uc5's own header** (FINDINGS 52.8).

**Decisions taken, and why.**

* **STOP SPENDING ON THE BOX.** Four boxes at R18 and full removal at R10/R34 move the number by
  less than the null's reproducibility. Further box arms would buy precision on a settled
  question. The one exception is CIFAR-100, which has never been box-tested and whose ceiling
  occupancy is 100.0% — that is `uc6-*`, 6 jobs, and it closes the axis.
* **THE BUDGET IS NOW THE ONLY UNTESTED THREAT TO THE HEADLINE, so it gets the larger batch.**
  Every N_eff/m the campaign has quoted is from a 20-epoch run, in a system CORRECTIONS 65 showed
  is still descending at 89–100% of max Lion speed in its last quarter. `bl5-*` (9 jobs, alice2)
  is a 40-epoch box-free rung against the 20-epoch `cl5-*-cU-*` control already on disk. **It is
  fundable only because 52.1 refuted 51.7** — under the old projection a 40-epoch run was
  guaranteed to bind. Registered: B0, B0.3 (box-free gate, scored first), **B1.5 (the same
  ABSOLUTE window as the control, which is what makes B1 a budget contrast rather than a seed
  contrast)**, B1 with a stated direction (down), B2, B2.5, B3, B4.
  **Its header's affordability claim was WRONG AT SUBMISSION TIME and has been amended in place,
  struck rather than quietly edited**: it said "a 17-epoch margin" from the MEAN trajectory, where
  the worst seed gives 22.8 epochs of headroom against 20 spent — marginal. The B0-B4 predictions
  are untouched; only the justification changed, and the amendment is timestamped as post-hoc.
* **R10 IS EXCLUDED FROM THE BUDGET LADDER, deliberately.** Worst-seed headroom is ~6 epochs; a
  40-epoch R10 run binds around epoch 26 and would be measuring the box again. Running it anyway
  and reporting it as a budget result is precisely the cycle-50 error.
* **NEW GUARD, adopted in both scripts: "byte-matched" is a CLAIM and must be DIFFED.** The uc5
  bug and cycle 50's "the HIGH bound provably never binds" are the same failure — an unchecked
  assertion in a batch header. `c52_c100_boxfree.sh` guard 4 greps c49 for the NN-name it claims
  to match; `c52_budget_ladder.sh` guard 3 does the same against cl5.
* **SECOND NEW GUARD: count what Slurm ACCEPTED, not what we tried.** The first `--submit` of
  `c52_budget_ladder.sh` printed "9 jobs (SUBMITTED)" while sbatch had rejected all 9 on an
  invalid `--time=05:50:00` (gpu-short caps below 5h). A batch script that reports its intent
  instead of its outcome is how a tick scores a pre-registration against an empty queue. Fixed to
  03:50:00 and to counting exit status; resubmitted and verified 9/9 pending.
* **STANDING RULE (7) added**: a rate used to extrapolate must be measured on the segment being
  extrapolated from. → §67.
* **A CLAIM MADE EARLIER IN THIS SAME DECISION RECORD IS WITHDRAWN (FINDINGS 52.12).** It said a
  granularity curve is "a design question and not a code one, because `blockwise` accepts arbitrary
  group specifications". `blockwise` groups consecutive parameter TENSORS and can only reach
  granularities **coarser than layerwise**; the nodewise minimum sits between layerwise and
  weightwise, where nothing in the current vocabulary lands. Nor is it recoverable offline — the
  k-profile takes one k per ARM. **Filling that interval needs a new `stepsize_type` in `HF.py`,
  i.e. a code change to the optimizer under study, and that is flagged for an operator decision
  rather than made unsupervised.**
* **A THIRD BATCH WAS SUBMITTED after `uc6` freed alice: `ns5-*`, 12 jobs** (FINDINGS 52.13). It
  attacks the stated weakness of §70 — that the nodewise minimum is scoped to ms=1e-3 with a
  counterexample at ms=1e-4 — by locating the boundary. First it was checked that the
  counterexample is not itself a box artefact: **it is not** (0.0% at both guards in all three m4
  rungs, FINDINGS 52.11). The ladder goes DOWN from 1e-3 because measured travel (0.978 log units
  at 1e-4, 4.751 at 1e-3) says there is no box-free configuration ABOVE 1e-3 at this budget.
  N2 registers a mechanism — **adaptation extent rather than meta-stepsize** — which, if confirmed,
  makes §70 a transferable statement and yields a prediction testable against `bl5`.
* **NOT DONE, and still unspent:** the raw-instrument `s` re-derivation sweep (bookkeeping, carried
  since 51).

**LATE ADDENDUM, SAME TICK.** `uc6-*` ran in 7–10 minutes and was scored before the tick closed.
V0.1 6/6, V0.2, V0.4, V1, V2, V3, V4 — **every gate passes** (FINDINGS 52.10). Consequences already
folded into §68/§69/§70 above: the headline is box-free in **4 of 4** families, clip saturation is
excluded in **both** rebound families, and the nodewise minimum is **9 of 9**. `uc6`'s registered
direction ("no move, |Δ| < 0.02") was **confirmed** at +0.0077 — notable because it was registered
*after* uc5's opposite directional prediction failed, so it is a prediction corrected by a miss
rather than a lucky guess. **FINDINGS 51.7 is now scoreable in full: 0 of 5 "WILL BIND" rows
correct, 5 of 5 "will not bind" rows correct** — a perfectly one-sided failure, the signature of a
systematically over-fast rate, which is what §67's STANDING RULE (7) exists to prevent.

**Queues at tick end:** alice **0** (`uc6-*` complete and scored), alice2 **9 R** (`bl5-*`).
FairShare 0.333 / 0.334. **The only open batch is the budget ladder, and the budget is the only
remaining untested threat to the headline.**

---

## 72. STANDING RULE (7) GETS A COROLLARY, AND CORRECTIONS 67's OWN FIX WAS STILL NOT ENOUGH (cycle 53)

67 caught 51.7 extrapolating a **startup** velocity, added STANDING RULE (7) (*a rate used to
extrapolate must be measured on the segment being extrapolated FROM*), and replaced the mean
trajectory with the worst seed — 56.6 extra epochs of headroom became **22.8**, and "report the
worst seed, never the mean" became a rule. It funded `bl5` on that basis and called the margin thin.

**The measured bind was 10.4 extra epochs. The worst-seed projection was optimistic by 2.2x.**

Why, and it is not a fourth kind of carelessness — it is the same one in a third place (FINDINGS
53.3). The top coordinate's velocity is **not monotone in time and is seed-dependent**: seed 0
re-accelerated **3.1x** (0.123 → 0.379 v/vmax) between epochs 10–20 and 20–30 while seeds 1 and 2
kept decelerating. A *decelerating* rate is therefore not a safe upper bound either.

**STANDING RULE (7), COROLLARY:** *a monotone trend in a rate is not a property of the rate. Do not
fund a batch on an extrapolated headroom in either direction — measure the headroom, or budget the
box. An extrapolation may earn a GATE; it may never earn a PRESUMPTION.*

**AND A SECOND RULE, EIGHTH, FROM THE SAME BATCH.** `bl5`'s weightwise box-free row read "8.03% of
records at HI". That is a mean over a **binary, per-seed** event: one seed at 24.07% and two at
0.00% (FINDINGS 53.2). The pooled row concealed both the phenomenon and its size.

> **STANDING RULE (8):** *a gate on an event that either happens or does not must be scored PER
> SEED, never on the pooled fraction. Pool only after establishing the event is not seed-specific.*

Rules 5, 6 and 7 forced a fraction to name its denominator, measure at the right resolution, and
quote its window. None of them stopped a correctly-denominated, correctly-resolved, correctly-
windowed fraction from being averaged across units on which it was bimodal. All three new batches
score their box-free gate per seed.

## 73. THE HEADLINE IS **NOT** BUDGET-STABLE. CORRECTIONS 59/68 IS A **20-EPOCH** SENTENCE. (cycle 53)

The budget was named as the last untested threat and it is a **live** one. On the two rungs that
were box-free on 3/3 seeds and required no salvage of any kind (FINDINGS 53.4):

| rung | 20 ep | 40 ep | Δ | bar | verdict |
|---|---|---|---|---|---|
| layerwise | 0.7262 | 0.6912 | −0.035 | 0.10 | STATIONARY |
| **nodewise** | 0.4056 | 0.2774 | **−0.128** | 0.10 | **DRIFTING** |

**N_eff/m's budget-robustness is GRANULARITY-DEPENDENT** — that is the finding, and it was bought by
a batch whose primary test failed its own gate. On the weightwise rung the fall is far larger
(0.5064 → 0.2634 over epochs 20.0–30.4, in a window box-free on every seed), and the seed that spent
96.3% of its last quarter pinned at the ceiling returns **0.1552** against **0.1442 / 0.1455** for
the two that never touched it — a spread of 0.011. **The box is not what moved it.**

**QUOTING RULE, effective now.** Write *"over epochs 10–20"* or *"at a 20-epoch budget"* wherever
CORRECTIONS 59/68's range appears. Do **not** write the 16%–55% range without a budget, and do not
write "operating point" in a way that implies budget-independence — 65 already narrowed
"equilibrium" to the bulk; 73 says the bulk value itself moves.

**WHAT IS AND IS NOT ESTABLISHED.**

| claim | status |
|---|---|
| N_eff/m falls with budget at **nodewise** | **ESTABLISHED**, n=3, box-free 3/3, registered window, nothing post-hoc |
| N_eff/m is not shown to move at **layerwise** | **BOUND, not absence** — m=62 is marginal against rho_min ~1.1e−03 |
| N_eff/m falls with budget at **weightwise** | **SUGGESTIVE ONLY** — post-hoc window, n=2 box-free seeds. `br6-*` replicates it pre-registered |
| B1 (the registered primary test) | **UNINTERPRETABLE, as registered. NOT overturned by §53.5's post-hoc rescue** |
| the box caveat of 68 | **still not needed** — 68 is a 20-epoch statement and stands at 20 epochs |

**AND CORRECTIONS 67's LAST SENTENCE MUST NOT BE ADOPTED.** 67 floated that if deceleration
continued, "the campaign can stop treating the box as a live threat at R18 entirely". It did not
continue. At 40 epochs 1 of 3 seeds reaches alpha = 1 exactly. The box is a live threat at R18
**above ~30 epochs**, which also means X3's "at ms=1e−3 the operating point is INTERIOR" is now
known to be a **20-epoch** statement. `br6-*`'s C0.4 is a stability gate for precisely that reason.

## 74. CORRECTIONS 70 IS BUDGET-SCOPED AS WELL AS ms-SCOPED, AND ITS MECHANISM IS REFUTED (cycle 53)

Three things happened to the nodewise minimum this tick, and two of them narrow it.

1. **B2.5 REFUTES it as a property of the partition.** At 40 epochs the ordering is `w < node < lay`,
   not `node < w < lay`. Contamination of the w rung would have manufactured exactly that flip, so
   it was checked against the box-free window 0.5–0.759 — **the flip survives** (FINDINGS 53.6).
   → **The nodewise minimum is BUDGET-SPECIFIC.** It may be written as holding at 20 epochs,
   ms=1e−3. It may **not** be written as a property of the partition.
2. **N2 REFUTES the mechanism.** The registered candidate — that the governing variable is
   *adaptation extent* rather than the meta-stepsize — predicted the argmin flips to `node` where
   the weightwise beta span first exceeds ~5 log units. At ms=5e−4 the span is **8.268** and the
   argmin is still `w`. The predicate matches 1 of 4 rungs (FINDINGS 53.9). **70 stays scoped to
   the meta-stepsize; the mechanism stays OPEN.** Do not retro-fit a second variable.
3. **N1 is UNDECIDED, not passed.** At ms=2e−4 the two smallest are 0.2054 (w) and 0.2244 (node),
   a gap of **0.0190** against the registered 0.020 tolerance. One of the two admissible readings,
   **(node, w)**, is N1's own registered refutation. A test whose refutation branch is live is not a
   pass. `ns6-*` buys the third seed the ns5 header registered in advance.

**NET EFFECT ON THE ADAM-MINI SENTENCE.** 70 called it "the most paper-relevant thing since the
sign-agreement measurement": *the Adam-mini / Adalayer / SGG line places its blocks where the
retained fraction is smallest.* It now carries **three** scopes — ms=1e−3, 20 epochs, and SGDm base
— and the third has never been tested at all. `bo6-*`'s V2 tests it: those methods partition an
**Adam** second moment, and if the nodewise minimum is an SGDm phenomenon the sentence must be
**deleted, not hedged**.

## 75. A BUG IN THIS TICK'S OWN SCORER, CAUGHT AND FIXED BEFORE IT REACHED A CLAIM (cycle 53)

`c53_score.py`'s first run printed **"N1 PASSES ... the flip is monotone"**. It computed the
`decided` flag correctly (`NO` at ms=2e−4, printed in its own table) and then read the **nominal**
minimum of that rung anyway when scoring the sequence. The nominal minimum of a coin flip is a coin
flip. Fixed: the scorer now refuses an undecided argmin, prints both admissible readings, and names
the live refutation branch. FINDINGS 53.8 records the correction rather than the first output.

This is the third time this campaign a *summary statistic* has been read past its own uncertainty
flag (`s` in 51, the pooled clip fraction in 62, the argmin here). The pattern: **the flag was
computed and displayed correctly, and the conclusion ignored it.**

## 76. DECISION RECORD — cycle 53

**Data state.** Both queues 0 P / 0 R at tick start; all 12 `ns5` and all 9 `bl5` complete. Probes
synced (742 MB across two roots — the first sync used too narrow an rsync filter and omitted
`neg_counts.*`, which the reducers require; caught because `reduce_root` returned nothing, and
re-synced in full). CSV regenerated to **1686 runs** (+27). Five selftests green before use:
`c53_score` 14/14 and `c53_budget_window` 6/6 (both new), `neff_instrument` **23/23** (was 19/19;
+4 for the new `--window` option), `probe5_window` 41/41, `c52_boxfree` 27/27.

**Decisions taken, and why.**

1. **B0.3 SCORED FIRST AND HONOURED WHEN IT FAILED.** B1's −0.3563 is recorded UNINTERPRETABLE,
   not REFUTED, exactly as registered — even though the post-hoc evidence says the contamination it
   feared is absent. Overturning a registered gate with a post-hoc rescue is the move the gate
   exists to prevent. → §73.
2. **THE BUDGET THREAT IS CONFIRMED ON EVIDENCE THAT NEEDED NO SALVAGE.** The nodewise rung is
   box-free on 3/3 seeds, in the registered window, and moved −0.128 against a ±0.10 bar. The
   headline becomes a 20-epoch sentence. → §73.
3. **STANDING RULE (7) COROLLARY and STANDING RULE (8) added** — non-monotone rates, and per-seed
   scoring of binary gates. → §72.
4. **CORRECTIONS 70 narrowed twice and its mechanism refuted.** → §74.
5. **N1 recorded UNDECIDED rather than passed**, and this tick's own scorer bug that would have
   reported it as a pass is written down. → §74(3), §75.
6. **`neff_instrument.py` gained `--window` as an OPTION with the default untouched**, because
   every number the campaign quotes comes from the default and a changed default would silently
   re-derive them. Four selftests added for it, including "explicit 0.5-1.0 reproduces the default
   exactly".
7. **A NEW SCORER RATHER THAN AN EDIT TO `c52_boxfree.py`.** That file's ARMS table is a hard-coded
   list of last tick's globs and it *ignores* its positional argument — pointing it at
   `../probes_bl5` silently reprints the cycle-52 table, which is what happened on the first attempt
   this tick. Its **functions** are imported and reused unchanged; a second implementation of a
   number is a second chance to get it wrong.
8. **IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous ten.
9. **THE `stepsize_type` CODE CHANGE REMAINS UNMADE and is re-flagged for the operator.**
   CORRECTIONS 71 deferred it. Inspecting `HF.py` this tick confirms the deferral was right and
   sharpens why: `nodewise` works because its beta is shape `(p_size[0],)` and maps back to the
   parameter by a pure **broadcast view** (`node_view`). Any granularity strictly between layerwise
   and weightwise needs a **scatter/gather in the hot update path**, not a broadcast — materially
   more invasive than the existing `PATCH_GRANULARITY`, in the optimizer under study, with this
   campaign's history of instrumentation bugs costing whole batches. **Not done unsupervised.**

**Submitted, 21 jobs, all ACCEPTED BY SLURM and all RUNNING (0 pending on both accounts).**

* **`br6-*`, 12 on alice2** (`bin/c53_budget_replication.sh`) — the budget replication, **box-free
  by construction** at `BETA_CLIP=−30:2.0`, +2.0 above the **measured** pin rather than an
  extrapolated one (§72), 40 epochs, seeds **0–3**. C0, C0.3 (per seed, first), **C0.4 a new
  STABILITY gate**, C1 (**labelled NOT INDEPENDENT** — registered after seeing the post-hoc window,
  so a confirmation is a replication), **C2 the independent one** (the lay/node asymmetry, informed
  by nothing post-hoc), C2.5.
* **`ns6-*`, 3 on alice** (`bin/c53_ns_thirdseed.sh`) — N1's third seed at ms=2e−4, bought because
  the ns5 header registered buying it under exactly this condition.
* **`bo6-*`, 6 on alice** (`bin/c53_base_optimizer.sh`) — **AdamW base**. The CSV has zero
  AdamW-base nodewise runs and every N_eff/m ever quoted is SGDm. V1 registers **no direction**,
  deliberately, because no mechanism predicts one — the failure mode 68 recorded when uc5's story
  passed its bar while its stated mechanism moved nothing.

**NEXT TICK, in order.**
(a) **`br6`: C0.3 PER SEED FIRST.** If any seed binds even at +2.0, the pair (HI=0.0 → epoch 30.4,
HI=+2.0 → epoch X) is a two-point measurement of how the bind budget moves with the ceiling and
**is** the result. Then **C0.4** — an unstable run's correlation statistics measure nothing. Then
C2 (the independent prediction) **before** C1 (the labelled-dependent one), so the tick's strongest
evidence is read on the arm that no post-hoc analysis touched.
(b) **`ns6`: M0.3 per seed, then re-run `c53_score.py`** — it re-reads N1 at n=3 automatically.
(c) **`bo6`: V0.3 per seed, then V0.4 (trains-at-all), then V2 before V1** — V2 decides whether the
Adam-mini sentence survives, and V1 has no registered direction so it cannot be over-read.
(d) **Do NOT fund 80 epochs until C0.3 scores.** +2.0 is an untested ceiling; funding a longer
budget on it is the error §72 was written about.
(e) Still unspent, still bookkeeping not science: the raw-instrument `s` re-derivation sweep,
carried since 51.

**Queues at tick end.** alice **9 R / 0 P** (`ns6` 3, `bo6` 6). alice2 **12 R / 0 P** (`br6`).
FairShare 0.333 / 0.334, unchanged from cycle 52.

---

## 77. THE BUDGET THREAT IS CONFIRMED PRE-REGISTERED, BOX-FREE BY CONSTRUCTION (cycle 54)

CORRECTIONS 73 recorded the budget fall on a batch whose primary test failed its own gate, with the
weightwise leg resting on a post-hoc window at n=2. `br6-*` replaces all of that. **Every gate
passes**: box-free on **12 of 12** seeds (0.0000% of records, 0.00000% of coordinates), C0.4
stability PASS, C2 PASS, C1 PASS, C2.5 PASS (FINDINGS 54.1).

| rung | 20 ep | 40 ep (br6, n=4) | Δ | status |
|---|---|---|---|---|
| lay | 0.7262 | 0.6903 | −0.036 | stationary — **a BOUND** (m=62 marginal), never an absence |
| node | 0.4056 | 0.2796 | −0.126 | **DRIFTING**, replicated |
| w | 0.5064 | 0.1508 | **−0.356** | **COLLAPSING**, replicated |

**CORRECTIONS 73's quoting rule is upgraded from post-hoc to pre-registered.** Write *"over epochs
10–20"* or *"at a 20-epoch budget"* wherever the 16%–55% range appears — that instruction is
unchanged, but it now rests on n=4 box-free evidence rather than an n=2 window.

**C2.5 replicates the ordering flip**: at 40 epochs it is `w < node < lay`. The nodewise minimum is
**budget-specific** and may not be written as a property of the partition (74 stands, reinforced).

**A LICENCE THIS CAMPAIGN HAD BEEN USING WITHOUT MEASURING IT IS NOW MEASURED.** `br6` (HI=+2.0)
and `bl5` (HI=0.0) agree to **0.0009** (lay) and **0.0022** (node) at 40 epochs where both are
box-free. Comparing N_eff/m across *box-free* ceilings is therefore safe at the 0.002 level. Both
new batches carry a ceiling-invariance gate rather than inheriting this.

## 78. STANDING RULE (9): A TOLERANCE MUST BE SCALED TO THE NOISE OF WHAT IT MEASURES (cycle 54)

The campaign's ±0.10 N_eff/m bar came from a **box**-sensitivity measurement at weightwise (±0.038,
CORRECTIONS 62) and has been applied to all three rungs at all budgets ever since. Measured
per-seed sd this tick (FINDINGS 54.2): weightwise **0.0377 at 20 ep** but **0.0035 at 40 ep** — a
10.8× collapse — against nodewise 0.0492 → 0.0196 and layerwise 0.0227 → 0.0361.

So ±0.10 is ~2.7 sd at 20-epoch weightwise (appropriate) and **~29 sd at 40-epoch weightwise**
(not a bar at all). One number has been serving three rungs whose noise differs by 10× and two
budgets across which it moves by another 10×.

> **STANDING RULE (9):** *a registered tolerance must be stated against the measured noise of the
> statistic at the budget and unit it is applied to. A bar imported from another rung, another
> budget, or another source of variation is not a bar. Report the sd alongside the verdict.*

**NOTHING IS RE-DERIVED, AND THAT WAS CHECKED RATHER THAN ASSUMED.** Every gate ±0.10 has decided
was re-read against the sd at its own budget: cycle-52's cross-box span 0.076 is **2.0 sd** at 20
epochs, so **CORRECTIONS 68's box conclusion STANDS and is not re-opened**; C2 layerwise 1.0 sd
(already a bound); C2 nodewise 6.4 sd; C1 ~9 sd. The bar was conservative in the safe direction
everywhere it has been used. It is retired going forward, not retroactively.

The rule has a second, opposite instance in the same tick: N1's **0.02** argmin tolerance is
*tighter* than the gap it must resolve is large relative to n=3 noise (78 and 80 are the same rule
firing in both directions — too loose, and too tight).

## 79. V2 WAS READ PAST ITS OWN GATE. THE ADAM-MINI SENTENCE IS **SUSPENDED**, NOT DELETED (cycle 54)

`c54_score.py` printed **"V2 REFUTED (argmin = w) … the Adam-mini sentence must be DELETED, not
hedged."** It is not adopted (FINDINGS 54.3).

bo6's V0.3 **failed on 2 of 3 rungs, per seed** — node and w bind at epochs 15.3–18.2, up to 93.8%
of Q4 records — and those are precisely the two rungs whose values produce V2's argmin, while
`lay`, the only box-free rung, is the one V2 calls the maximum. The scorer applied the gate to V1
(correctly UNINTERPRETABLE) and not to V2. **An argmin inherits the interpretability of every rung
it ranks, not just the one it selects.** bo6's own registration says so in its resolution note:
an untrustworthy rung makes the argmin undecidable *"rather than defaulting it to one of the other
two. Say which."*

**Fourth occurrence of the same failure** (CORRECTIONS 75: `s` in 51, the pooled clip fraction in
62, the argmin in 74, this). The flag was computed and displayed correctly and the conclusion
ignored it — again. Fixed as a **tested function** (`argmin_blockers`, 5 new selftests encoding the
literal bo6 shape, including "a bound rung that is NOT the argmin still blocks"); `c54_score`
17/17.

**THE POST-HOC WINDOW DOES NOT RESCUE IT EITHER, AND THAT IS THE POINT.** On records 1000–1500
(box-free on all six arms) the ordering is identical and the gap is 0.100 vs a 0.02 bar. That is
strong — and it is still post-hoc. CORRECTIONS 76(1) forbade overturning a registered gate with a
post-hoc rescue, and **the rule is symmetric: it binds a rescue that strengthens a REFUTATION
exactly as much as one that saves a confirmation.** Deleting a claim on unregistered evidence is
the same error as keeping one.

> **THE ADAM-MINI SENTENCE IS SUSPENDED.** It may not be written and it may not be deleted until
> `bo7-*` scores. It carries three scopes — ms=1e−3, 20 epochs (§74, replicated by C2.5), and SGDm
> — and the third is now under direct pre-registered test.

## 80. N1 IS UNDECIDED AT n=3 AND THE GAP SHRANK. NOT BOUGHT — SEQUENCING, NOT COST. (cycle 54)

`ns6` delivered the third seed and it **did not decide N1**: the node−w gap at ms=2e−4 went
**0.0190 (n=2) → 0.0142 (n=3)** against a 0.020 tolerance (FINDINGS 54.4). The refutation branch
**(node, w)** stays live alongside the admissible (w, w).

The cost of deciding it is **measured, not guessed**: this rung's own pooled per-seed sd is
**0.0131**, so **n=7 per rung resolves the gap at 2 SE** — about 8 more jobs, entirely affordable.
(An earlier estimate of ~40 seeds used the cl5 sd at ms=1e−3, which is 3× looser; using the rung's
own seeds corrected it.)

**IT IS NOT BOUGHT THIS TICK, AND THE REASON IS ORDER, NOT PRICE.** N1 characterises how the
argmin flip depends on the meta-stepsize. The *only* thing the nodewise minimum has ever been for
is the Adam-mini / Adalayer / SGG sentence — and §79 has just suspended that sentence pending
`bo7`. Spending jobs to map the ms-dependence of a phenomenon that may have no surviving
application is premature. **If `bo7`'s W1 refutes (argmin stays `node` under AdamW), the sentence
lives and N1's four extra seeds become the next batch. If W1 confirms, the nodewise minimum is an
SGDm-only, 20-epoch-only, ms=1e−3-only curiosity and N1 should not be bought at all.**

This is recorded so the next tick can execute it without re-deriving it: **8 jobs, seeds 3–6 on
`node` and `w` at ms=2e−4, conditional on bo7 W1 refuting.**

## 81. DECISION RECORD — cycle 54

**Data state.** Both queues 0 P / 0 R at tick start; all 21 cycle-53 jobs landed (`br6` 12,
`ns6` 3, `bo6` 6). Probes synced in full (br6 453 MB, bo6 207 MB, ns5 re-synced to 521 MB). CSV
regenerated to **1707 runs** (+21). Five selftests green before use: `c54_score` **17/17**,
`c53_score` **14/14**, `neff_instrument` **23/23**, `c52_boxfree` **27/27**, `c53_budget_window`
**6/6**.

**Decisions taken, and why.**

1. **C2 SCORED BEFORE C1**, as registered — the independent prediction read before the
   labelled-dependent one. Both passed; C1 is written as a **replication**, never a discovery. → §77
2. **THE BUDGET THREAT IS CONFIRMED ON EVIDENCE NEEDING NO SALVAGE.** 12/12 box-free, n=4,
   registered window. CORRECTIONS 73 is upgraded from post-hoc to pre-registered. → §77
3. **V2's PRINTED VERDICT WAS REFUSED.** The scorer's own gate failed on the two rungs feeding the
   argmin. Recorded UNINTERPRETABLE; the Adam-mini sentence is **SUSPENDED, not deleted** — the
   symmetric reading of 76(1). Scorer fixed as a tested function. → §79
4. **STANDING RULE (9) added**, with the ±0.10 bar shown to be ~29 sd at 40-epoch weightwise and
   the 0.02 argmin tolerance shown to be too tight — the same rule failing in both directions. No
   past verdict changes; checked explicitly against the sd at each gate's own budget, and
   **CORRECTIONS 68 is confirmed NOT re-opened**. → §78
5. **N1's extra seeds DEFERRED on sequencing**, with the cost measured (8 jobs, n=7/rung at 2 SE)
   and the trigger written down, so the next tick executes rather than re-derives. → §80
6. **A THIRD CORRECTIONS-71 SUBMISSION FAILURE CAUGHT BEFORE SUBMISSION.** `bd7` was written with
   `--time=05:50:00` against gpu-short's 4:00:00 cap, which would have rejected all 12 jobs. Fixed,
   and **`guard 6` now reads live `sinfo` limits** so the class of error cannot recur. A comment
   was not enough twice; a guard is. → FINDINGS 54.6
7. **TWO `c53_score.py` LABEL-VS-DATA BUGS FIXED** — a hard-coded seed count producing a FAIL with
   a misattributed cause, and an `n` column printed from a table literal that concealed the third
   seed's arrival. → FINDINGS 54.5
8. **THE CEILING IS AN EXPERIMENTAL VARIABLE IN BOTH NEW BATCHES**, because br6's measured travel
   is bursty (2 of 12 runs moved +3.3 / +4.0 log units in the final 10 epochs while 10 descended).
   STANDING RULE (7) COROLLARY forbids funding either batch on an extrapolated headroom, so the
   box-dependence is measured instead of assumed.
9. **IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous eleven.
10. **THE `stepsize_type` CODE CHANGE REMAINS UNMADE and is re-flagged for the operator** (76.9,
    71). Anything strictly between layerwise and weightwise needs a scatter/gather in the hot
    update path, in the optimizer under study. **Not done unsupervised.**

**Submitted, 24 jobs, all ACCEPTED BY SLURM and all RUNNING (0 pending on both accounts).**

* **`bd7-*`, 12 on alice2** (`bin/c54_budget_curve.sh`) — the **80-epoch budget point**, ceiling as
  a variable (HI ∈ {2.0, 6.0}), seeds 0–1. D0, D0.3 (per seed per ceiling, first), D0.4, **D0.5 a
  new CEILING-INVARIANCE gate**, **D1 with NO direction registered** and three bar-defined branches
  (falls ≤0.13 / floors ±0.02 / rebounds ≥0.17), D2 the granularity contrast. Per-rung bars.
* **`bo7-*`, 12 on alice** (`bin/c54_adamw_ceiling.sh`) — the **AdamW re-run** bo6's V0.3
  prescribed, same ceiling ladder, 20 epochs. W0.3 per seed per ceiling, W0.4, W0.5, **W1 the
  argmin (LABELLED NOT INDEPENDENT)**, **W2 with no direction registered**.

**NEXT TICK, in order.**
(a) **`bo7` FIRST — it gates the most.** W0.3 per seed per ceiling; if both ceilings bind on node
and w, say "AdamW-base beta is not confinable at this ms" and make the next batch an **ms ladder**,
not a third ceiling. Then W0.4, W0.5, then **W1 before W2**. W1 decides whether the Adam-mini
sentence is deleted or reinstated, and whether §80's 8 N1 jobs are bought at all.
(b) **`bd7`: D0.3 per seed per ceiling, then D0.4, then D0.5 BEFORE D1** — pooling two ceilings
that disagree would manufacture the very budget effect D1 is measuring. Then D1's three branches,
then D2. **Report the 80-epoch per-seed sd alongside the verdict** (STANDING RULE 9).
(c) **Do NOT fund 160 epochs until D0.3 scores.** +6.0 is an untested ceiling; that is the error
§72 was written about, and §77 only licenses ceilings that have been *measured* box-free.
(d) Still unspent, still bookkeeping not science: the raw-instrument `s` re-derivation sweep,
carried since 51.

**Queues at tick end.** alice **12 R / 0 P** (`bo7`). alice2 **12 R / 0 P** (`bd7`).
FairShare 0.333054 / 0.333893, unchanged from cycles 52–53.

## 82. THE NODEWISE MINIMUM IS A **TRANSIENT**, AND THE MECHANISM 74 LEFT OPEN IS MEASURED (cycle 55)

`bo7`/`bd7` could not be read: **both ALICE login nodes are down** (FINDINGS 55.0 — gateway up,
`132.229.104.230/.231` unreachable from it, all five login aliases refused on :22). No queue was
read, nothing was synced, nothing was submitted. Everything below comes from the probe mirrors
already on disk and needed no cluster.

**THE RESULT.** Adaptation lifts N_eff/m **monotonically in block size** — 4 of 4
network-matched frozen→free pairs give lift(w) 3.84–12.03× > lift(node) 1.26–4.73× >
lift(lay) 0.72–1.19× ≈ 1 (FINDINGS 55.5). With β frozen the minimum is **weightwise in 4 of 4
families**. The "nodewise minimum" is therefore **not a property of the nodewise partition**:
it is where a large weightwise lift has carried weightwise *past* nodewise. This is
CORRECTIONS 47's scale-selective consumption, reproduced in ordering through a different
statistic on three families it was never measured on.

**AND THE LIFT IS TRANSIENT, MEASURED WITHIN ONE BOX-FREE BATCH** (FINDINGS 55.6). In absolute
epoch windows, `br6` weightwise runs 0.0092 → **0.5073** → 0.2551 → 0.1201 while nodewise runs
0.0217 → 0.4074 → 0.3270 → 0.2768. **The argmin is `w`, then `node`, then `w` again — the
crossover happens between epochs 20 and 30 inside a single set of runs**, and `bl5` (a different
batch at a different ceiling) reproduces the curve to three decimals.

> **CORRECTIONS 70's nodewise minimum is a ~10-EPOCH WINDOW OF TRAINING.** It does not exist
> before adaptation lifts weightwise and it does not survive that lift's decay.

**THIS DOES NOT DELETE THE ADAM-MINI SENTENCE AND MUST NOT BE USED TO.** It is a POST-HOC
inventory of data already on disk. CORRECTIONS 76(1), read symmetrically per 79, binds a
post-hoc rescue that strengthens a refutation exactly as hard as one that saves a confirmation.
**The sentence stays SUSPENDED** pending `bo7`. What changes is not its status but **what the
next batch should be** — see (5) below.

## 83. DECISION RECORD — cycle 55

**Data state.** Cluster unreachable for the whole tick; the outage was localised to the login
nodes by probing from the gateway rather than reported as "ssh failed". CSV unchanged at 1707
runs — **no aggregate was regenerated, because no new `.out` was fetched, and regenerating it
from unchanged inputs would have manufactured a false "+0 runs" provenance line.** Six
selftests green before use (`neff_instrument` 23/23, `c52_boxfree` 27/27, `c53_budget_window`
6/6, `c53_score` 14/14, `c54_score` 17/17, `probe5_window` 41/41) plus the new
`c55_neff_noise` **51/51**.

**Decisions taken, and why.**

1. **THE TICK WAS SPENT ON THE INVENTORY WE ALREADY OWN, NOT ON WAITING.** 5.5 GB of probes for
   16 batches were on this Mac; the cluster was needed only to *add* to them. → 55.1–55.6
2. **STANDING RULE (9) IS NOW BACKED BY 46 MEASURED CELLS INSTEAD OF 7**, and CORRECTIONS 78's
   "conservative in the safe direction everywhere" is **NARROWED**: true of the gates 78
   checked, **false of the inventory** — seven cells put ±0.10 below 2 sd, two below 1.4 sd.
   No past verdict changes; the claim's scope does. → 55.2
3. **THE DOMINANT NOISE AXIS IS THE RUNG AND THE OPERATING POINT, NOT THE BUDGET.** Median sd
   by budget is 0.0167 (20 ep) vs 0.0196 (40 ep) — nothing. Weightwise sd at a *single* budget
   already spans 94×. FINDINGS 54.2's 10.8× collapse is real for its pair (p<0.01) and is
   **not a budget law**. → 55.2
4. **12 OF 25 ARGMIN CELLS ARE UNINTERPRETABLE UNDER CORRECTIONS 79's OWN RULE**, applied
   uniformly for the first time. And `cl5/cU`, the sole control behind CORRECTIONS 70, is
   **DECIDED AT 2.81 SE** — it stands, and it has been written as if it were far safer than
   that. → 55.3
5. **THE NEXT BATCH IS NO LONGER A THIRD SCOPE ON THE OLD QUESTION.** `bo7` asks "does the
   nodewise minimum survive AdamW". The inventory says the minimum is a ~10-epoch transient
   that already fails on the budget axis and vanishes entirely with β frozen. **Whatever `bo7`
   returns, the right follow-up is the EDGES OF THE BAND — where the crossover sits as a
   function of adaptation extent — not a fourth base optimizer.** Recorded so the next tick
   executes rather than re-derives.
6. **CORRECTIONS 74 (N2) IS NOT CONTRADICTED, AND A DEFINITIONAL DEBT IS RECORDED.** 74
   rejected adaptation extent on a span of 8.27 log units at ms=5e−4; this module measures
   6.29 for the same cell on a different, stated definition. **The two statistics must be
   reconciled before either is quoted again.** Neither is adopted over the other here. → 55.4
7. **A PREDICTION FOR `bd7` IS WRITTEN DOWN BEFORE `bd7` IS READABLE** (weightwise at 80 epochs
   below 0.1509 and still falling), explicitly labelled POST-HOC-DERIVED so a confirmation is a
   replication of 55.6's curve and never a discovery. → 55.6
8. **TWO VACUOUS TESTS FOUND AND KILLED IN THE NEW MODULE'S OWN SELFTEST** — an empty glob was
   passing a coverage assertion, and three symlink-alias roots were double-counting every `ml5`
   cell. A coverage test over zero items is the silent-zero failure `c52_boxfree.records()` was
   hardened against; it is now hardened here too. → 55.1
9. **NOTHING WAS SUBMITTED AND NOTHING WAS GUESSED ABOUT THE RUNNING JOBS.** `bo7` (12, alice)
   and `bd7` (12, alice2) were RUNNING at the end of cycle 54; whether they survived the outage
   is **unknown**. A poller retries login-node reachability from the gateway every 2 minutes.
10. **IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous twelve.
11. **THE `stepsize_type` CODE CHANGE REMAINS UNMADE and is re-flagged for the operator**
    (76.9, 71, 81.10). Not done unsupervised.

**NEXT TICK, in order.**
(a) **Reachability first.** `ssh alice-gw 'nc -z login.alice.universiteitleiden.nl 22'` is the
    one-line check; the poller log is in the session scratchpad. If still down, the cluster is
    not the bottleneck and there is more inventory work (the raw-instrument `s` re-derivation,
    carried since 51, and the span-definition reconciliation owed by 83.6).
(b) **If up: `squeue` BOTH accounts before anything else** — determine whether `bo7`/`bd7`
    survived or must be resubmitted. Do not assume either.
(c) Then cycle 54's order stands: `bo7` W0.3 per seed per ceiling → W0.4 → W0.5 → **W1 before
    W2**; `bd7` D0.3 → D0.4 → **D0.5 before D1** → D2, reporting the 80-epoch per-seed sd
    beside every verdict, now against 55.2's measured table rather than ±0.10.
(d) **Score `bd7`'s D1 against 55.6's written-down expectation as a REPLICATION**, never as a
    discovery.

**Queues at tick end.** UNKNOWN — both login nodes unreachable. FairShare not readable.

## 84. CORRECTIONS 74 (N2) IS **CORRECTED**: THE FLIP DOES NOT TRACK ms (cycle 55, later in the tick)

83.6 recorded a definitional debt and refused to adopt either span statistic. It is paid
(FINDINGS 55.7). N2's own `c53_score.beta_span` reproduces **8.27 exactly**, so the two
statistics agree; **both separate the 20-epoch argmin perfectly**, N2's between 8.27 and 12.18.

**N2 REFUTED A GUESSED THRESHOLD, NOT ITS VARIABLE.** `c52_nodemin_onset.sh:93` registered the
flip at *"span first exceeds **~5** log units"*. The 5 was never measured. The boundary is
between 8.27 and 12.18, so ms=5e−4's span of 8.27 is **below** it and its `w` argmin is the
variable's prediction, not a counterexample.

**AND THE REFUTATION OF "IT TRACKS ms" IS THRESHOLD-FREE.** Eight cells sit at ms = 1e−3 and
split **4–4** on the argmin: the four FROZEN arms (span 0.00, argmin `w`) against the four FREE
arms (span 12.18–15.87, argmin `node`). **A variable held constant across a 4–4 split cannot be
the one that governs it.** N2's ladder contained no frozen arm, which is why it could not see
this; within the free arms alone ms and span remain confounded exactly as N2 said.

> **CORRECTIONS 74's sentence *"the flip tracks ms, not adaptation extent"* is WITHDRAWN.**
> Adaptation extent is not refuted; ms is. The mechanism 74 left OPEN is 82's: adaptation lifts
> N_eff/m monotonically in block size, and the argmin is `node` only on the INTERVAL of
> adaptation extent where the weightwise lift has carried weightwise past nodewise — roughly
> 8–16 log units of span at these budgets, with `w` on **both** sides (br6 at span 23.85 gives
> `w`). Span is necessary to the description and is not sufficient on its own.

**WHAT THIS DOES AND DOES NOT DO.** It does not touch the Adam-mini sentence, which stays
**SUSPENDED** pending `bo7` (82, 79). It does not license a "span threshold" number: the
boundary was located post-hoc and only the ms refutation is threshold-free. It DOES mean
CORRECTIONS 70's remaining scopes should be restated in adaptation extent rather than in ms —
and that **`bo7`, whatever it returns, is measuring a base optimizer's effect on SPAN, not a
fourth independent scope.** That reframing is the actionable consequence and it is why 83.5
already redirected the next batch to the edges of the band.

## 85. **A UNIT ERROR DROPPED THE WEIGHTWISE ARM FROM THE c40 RESPONSE SURFACE** (cycle 56)

Found by an offline audit while ALICE was down; **every number below was re-derived from
`results/all_runs.csv` at write time**, not quoted from the audit.

**THE ERROR.** FINDINGS 40.3 (Tier 2) justifies its treatment of the per-weight arm with
*"`weightwise` — which sits at 68.471 ±0.245 (n=10) at ms=1e-3"*. That number is `p7-r18-w`:

| source | n | epochs_done | plateau mean | sd |
|---|---|---|---|---|
| `p7-r18-w*` | 10 | **{'20'}** — every one | 68.472 | 0.245 |

An exact match, and **all ten are 20-EPOCH runs**. The `rs-*` response surface they were used to
reason about is **100 epochs** (`epochs_requested` = {'100'} across all 67 rows). A 20-epoch
plateau was read as if it were a 100-epoch one.

**THE CONSEQUENCE IS LIVE.** The published surface has four granularity rows —
`scalar`, `resnet18_blocks`, `layerwise`, `nodewise` — and **no `weightwise` row at all**.
The single matched 100-epoch plain weightwise run in the entire corpus at
R18/CIFAR10/SGDm+Lion/ms=1e-3/AUGMENT=1/`BETA_CLIP=-15:-2.3026` is

    kt2_ww_a1e-3_s0   alpha0=1e-3   100/100 epochs   plateau = 90.913

which is **+22.4 pp above the figure used to reason the arm away**, and **+3.10 pp above the
surface's own scalar cell at the same meta-step** (`rs-scal-1e3-s3/s4`: 87.818 / 87.801,
mean 87.810, n=2).

**THREE CAVEATS, STATED NOT BURIED.**
1. **n = 1.** One run. This licenses COMPUTE, never a claim. Nothing in the paper may cite 90.913.
2. **alpha0 is not matched.** `kt2_ww_a1e-3` runs at alpha0=1e-3; the other 100-epoch weightwise
   runs sit at alpha0=1e-6 and reach ~78.0-78.1 guarded (`mx_sig_weightwise_s0/1/2`,
   `d4_clipW_s0/1/2`, `kt2_ww_a1e-6_s0`) or **collapse to 10.0 unguarded**. So the honest
   statement is *"at 100 epochs with the guard on, weightwise is 78-91 depending on alpha0,
   not 68.5"* — the error's direction is certain even though its size is not.
3. The audit reported the scalar cell as 87.764; re-derivation gives **87.810**. The verdict is
   unchanged, but the re-derived number is the one of record (STANDING RULE 1).

**WHY THIS MATTERS BEYOND A TYPO.** `docs/PLAN.md:140` (D2) names *"weightwise recovers under
tuning"* as the fork on which the contribution becomes a **tuning-budget analysis** rather than a
**structural-failure** result. The direction of travel supports the fork being live: `ml5`
weightwise plateau is **monotone rising in meta-stepsize and has not peaked** —

    ms=1e-4  62.277  |  ms=1e-3  68.508  |  ms=1e-2  74.356      (n=3 each, 20 epochs)

and `rs-w`'s unrun grid is exactly **3e-4 / 1e-3 / 3e-3 / 1e-2**, i.e. it covers the region where
the arm is still climbing.

**ACTIONS.** (a) FINDINGS 40.3 is amended in place to say **20-epoch** — done this tick, zero
compute. (b) The 12 `rs-w-*` jobs are the highest-value resubmission on reconnect; they are
ranked in the reconnect list rather than submitted, because the cluster is down.
**Until they land, "per-weight granularity fails structurally" may not be written.**

## 86. DECISION RECORD — cycle 57 (ALICE DOWN, SECOND CONSECUTIVE TICK, ZERO JOBS)

**OUTAGE, localised not assumed.** `2026-08-22T13:26Z`: the gateway is up and answers; from
it, `nc` to `login.alice.universiteitleiden.nl:22` and to both `132.229.104.230` / `.231`
returns DOWN. `ssh alice` and `ssh alice2` fail at banner exchange. **No queue read, nothing
synced, nothing submitted. CSV unchanged at 1707 rows.** `bo7-*` (12, alice) and `bd7-*` (12,
alice2) were RUNNING at the end of cycle 54; **whether they survived is still UNKNOWN and is
still not guessed.** No ssh config was touched and no retry loop was run.

1. **A SECOND CONTAMINANT OF THE SAME CLASS AS 85, AND THIS ONE IS INSIDE THE SURFACE.**
   17 of 1707 corpus rows have `epochs_done < epochs_requested`. In `a0` (3/30) and `gate0c`
   (2/8) the loss is granularity-SYMMETRIC — power, not validity. **In `rs` it is not:
   0/22 scalar, 0/22 layerwise, 6/13 `blk6` (46%), 6/10 nodewise (60%)**, severity down to
   24/100 epochs. The `blk6` row's published shape INVERTS when they are dropped (envelope
   91.171@1e-3 → **92.581@1e-4**); every low value in it is a truncated run and the depression
   is monotone in severity. **It is not a cost effect** — throughput is 2.38–3.23 ep/min across
   all four arms and the truncations concentrate in seeds 1–2, a scheduling artifact. → 57.1

2. **FINDINGS 42.2 IS VINDICATED, NOT CORRECTED.** It already filtered `epochs_done>=100` and
   its table re-derives **exactly** (92.231 / 92.581 / 92.795 / 92.547; layerwise−scalar +0.563
   t=4.85; blk6−scalar +0.349 t=3.71; layerwise−blk6 +0.214 t=2.41). **This tick did not
   overturn a doc; it re-derived one and found the contaminant 42.2's filter was already
   blocking.** One cell moves: 42.2's scalar ms=1e-3 reads 87.764 (16); config-matched
   re-derivation gives **87.758 (n=14)**, the number of record (STANDING RULE 1). → 57.1

3. **42.2's "83% OF THE GAIN IS TUNING" IS LOCALISED: THE GAIN IS A STEP FUNCTION IN ms.**
   layerwise−scalar across the shared grid: **−0.109 (t −1.17) / +0.175 (2.16) / +0.103 (1.45)
   / +0.563 (4.85) / +3.142 (13.37) / +3.339 (43.15)** at ms = 1e-8 / 1e-5 / 3e-5 / **1e-4
   (the joint optimum)** / 3e-4 / 1e-3. Below the optimum the gain is ≤0.18pp and not
   consistently resolvable; above it, ~3.2pp at t>13. **Both arms peak at the SAME ms.** What
   differs is falloff: scalar loses **5.871 pp/decade** above its peak against blk6 1.060,
   layerwise 1.801, nodewise 2.593. → **Partitioning buys TOLERANCE TO AN OVER-LARGE
   META-STEPSIZE; peak height is a separate effect ~10x smaller, and it is the same ~0.5pp the
   campaign already declared dead.** The correct granularity sentence is a ROBUSTNESS sentence,
   not an accuracy one. **LABELLED POST-HOC** — new cuts of data already on disk. → 57.2

4. **CORRECTIONS 85's WEIGHTWISE COMPARISON IS WITHDRAWN; ITS CONCLUSION IS NOT.** 85 placed
   the one matched 100-epoch weightwise run at "+3.10pp above the surface's own scalar cell".
   That cell is `scalar @ ms=1e-3` — **scalar's WORST cell on the entire grid**, 4.47pp below
   scalar's own peak, in exactly the regime where scalar collapses and no partitioned arm does.
   Against the *tuned peak row* the run is **1.32–1.88pp BELOW every arm**, and at ms=1e-3 it
   ranks **4th of 5** (node 92.547 > blk6 91.560 > lay 91.097 > **w 90.913** > scal 87.758).
   > **The sentence "+3.10pp above the surface's own scalar cell" may not be used again.**
   **BUT D2 SURVIVES ON BETTER EVIDENCE:** at ms=1e-3, weightwise and layerwise differ by
   **0.18pp**, inside layerwise's own seed sd — the behaviour of a partitioned arm, not a
   collapsing one. 85's n=1 caveat stands in full; **nothing may cite 90.913.** → 57.3

5. **AND THE HIGHEST-RANKED RESUBMISSION WAS MIS-SPECIFIED FOR ITS OWN QUESTION.** `rs-w`'s
   grid (`c40_surface.sh:85`) is 3e-4/1e-3/3e-3/1e-2 — **it starts ABOVE the 1e-4 optimum where
   every other arm peaks.** As written it measures weightwise's falloff and **cannot measure
   its peak height, which is the whole of D2.** 85 ranked it correctly and specified it wrongly.
   **This is the tick's actionable finding, and it was worth more than the 12 jobs it saves.**

6. **WRITTEN, DRY-RUN-VALIDATED, NOT SUBMITTED: `bin/c57_rsw_peak.sh`** — 18 jobs, alice, tag
   `rw9-*`, grid **3e-5 / 1e-4 / 3e-4 / 1e-3 / 3e-3 / 1e-2** × 3 seeds, so the peak can come out
   INTERIOR (CORRECTIONS 25). Branches **W-A ≥92.0 ⇒ "per-weight granularity fails structurally"
   is FALSE**; **W-B ≤90.0 or falloff >5.871 pp/decade ⇒ TRUE but scoped to weightwise alone**;
   else UNDECIDED. **NO DIRECTION REGISTERED** — the single 90.913 point is 0.18pp from
   layerwise (W-A) and 1.88pp below its peak (W-B), and one run at one ms cannot choose
   (CORRECTIONS 68). 7 guards; `bash -n` clean; guards 3b, 4 and 7 re-run standalone and passing.
   **Guard 7 is new and encodes 57.1**: it refuses the batch unless 100 epochs fit the wall at
   the SLOWEST measured weightwise rate (46 min median / 95 slowest vs a 230 min wall, 2.4x).
   **P0 is a hard drop gate** — any job with `epochs_done < 100` is dropped, never averaged in.

7. **`bin/c55_span_dissociation.sh` (sp8, 9 jobs, alice2) IS STILL WRITTEN AND UNSUBMITTED**
   and is unaffected by anything here. On reconnect the order is: `squeue` both accounts →
   `bo7`/`bd7` survival → **`sp8` before `rw9`** (sp8 is on alice2 and 9 jobs; rw9 is on alice
   and 18; they do not compete), then the 12 truncated `rs-blk6`/`rs-node` reruns LAST.

8. **"PER-WEIGHT GRANULARITY FAILS STRUCTURALLY" REMAINS UNWRITABLE**, now for two reasons
   rather than 85's one: the arm is still unmeasured at 100 epochs beyond n=1, **and** the
   comparison 85 used to argue about it was against a mis-tuned baseline.

9. **IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous thirteen.

10. **THE `stepsize_type` CODE CHANGE REMAINS UNMADE** and is re-flagged for the operator
    (76.9, 71, 81.10, 83.11). Not done unsupervised.

11. **ORPHAN DEBT — PARTIALLY PAID, AND THE METHOD IS NOW CHEAP.** `analysis/c57_surface_truncation.py
    --audit` classifies every row by family in one call, so the recurring "≈290 uncited runs"
    sweep no longer needs re-deriving by hand each tick. This cycle retires three families from
    that list by citing them: **`rs` (67)** → 57.1/57.2, **`a0` (30)** → 57.1 (symmetric
    truncation, power-only), **`gate0c` (8)** → 57.1. The remainder stays open and is NOT
    re-discovered next tick: it is a standing item, not a finding.

**NEXT TICK, in order.**
(a) **Reachability first**, one line: `ssh alice-gw 'nc -z -w 8 login.alice.universiteitleiden.nl 22'`.
    If still down, the unspent offline work is the raw-instrument `s` re-derivation (carried
    since 51) and the rest of the orphan sweep via `--audit`.
(b) **If up: `squeue` BOTH accounts before anything else** — `bo7`/`bd7` survived or must be
    resubmitted. Do not assume either.
(c) Submit **`sp8` (alice2, 9)** then **`rw9` (alice, 18)**; both re-run their own guards.
(d) If `bo7`/`bd7` landed, cycle 54's scoring order stands, with 55.2's measured per-seed sd
    beside every verdict rather than ±0.10.
(e) **Score `rw9` P0 BEFORE P1.** The failure this cycle documented is a short run read as a
    long one, twice, in two different documents.

**Queues at tick end.** UNKNOWN — both login nodes unreachable. FairShare not readable.

## 86. **THE "BUDGET" CONTRAST IS A WINDOW CONTRAST, AND THE HEADLINE SHOULD BE THE ACCURACY REVERSAL** (cycle 56)

Three corrections and one new headline candidate. **Every number re-derived from the raw `.out`
series at write time** (STANDING RULE 1); where an audit's number and mine disagreed, mine is
the one of record.

### 86.1 THERE IS NO BUDGET VARIABLE. CORRECTIONS 73/77 AND GATES C1/C2/C2.5 MEASURE A WINDOW.

`diff` of the two ARGS lines, run directly:

    cl5-lay-cU-s0  vs  bl5-lay-e40-s0
      --num-epochs      20  ->  40
      --save-directory  .../cl5 -> .../bl5
      --run-name        cl5-lay-cU-s0 -> bl5-lay-e40-s0

**Nothing else differs.** `SCHED=none`, `gamma=1`, no budget-coupled decay. **A 40-epoch run IS
a 20-epoch run continued.** So "N_eff/m at a 20-epoch budget" (steady half = epochs 10-20) versus
"at 40 epochs" (steady half = epochs 20-40) is a **contrast between two windows of one
trajectory**, manufactured by the convention that slides the window with B.

The measurement is not wrong; **its name is.** Write **"N_eff/m is non-stationary in training
time, and the non-stationarity differs by granularity."** Do NOT write "budget-dependent",
which implies a second causal variable the corpus does not contain. CORRECTIONS 73's quoting
rule survives in substance ("over epochs 10-20"), and its *"at a 20-epoch budget"* wording
does not.

### 86.2 THE CSV `plateau` COLUMN MAY NOT BE COMPARED ACROSS BUDGETS.

`aggregate.py:85` is `plateau_of(tests, k=20)`. On a **20-epoch** run that is the mean of the
**whole run**, including the startup transient; on a 40- or 100-epoch run it is a genuine tail.
Any cross-budget table built from that column is comparing a whole-run mean against a tail mean.
Use a **matched-k plateau** (mean of the last 5 test epochs at the epoch being compared).
Within-budget comparisons (e.g. the 100-epoch baseline table) are unaffected.

### 86.3 **THE NEW HEADLINE CANDIDATE, VERIFIED: THE ACCURACY-OPTIMAL GRANULARITY REVERSES WITH TRAINING HORIZON.**

`nodewise - layerwise`, matched-k plateau (k=5), **paired within seed**, two batches at two
different ceilings, R18/C10/SGDm+Lion/ms=1e-3/alpha0=1e-3/AUGMENT=1/SCHED=none:

| epoch | br6 (n=4, ceiling +2.0) | bl5 (n=3, ceiling 0.0) | pooled (n=7) | sd | seeds favouring nodewise |
|---|---|---|---|---|---|
| 10 | -3.748 | -4.211 | **-3.946** | 0.801 | **0/7** |
| 15 | -1.360 | -0.973 | **-1.194** | 0.277 | **0/7** |
| 20 | +0.057 | +0.007 | +0.035 | 0.286 | 4/7 (tie, at the floor) |
| 25 | +0.540 | +0.971 | **+0.725** | 0.317 | **7/7** |
| 30 | +1.038 | +1.105 | +1.067 | 0.230 | 7/7 |
| 40 | +1.253 | +1.265 | **+1.258** | 0.207 | **7/7** |

**Unanimous on both sides of the crossing, monotone between, replicated across two ceilings.**
Both endpoints are 25-80x the 0.05 pp resolution floor. The crossing is bounded by unanimity
between **epoch 15 and epoch 25**; it is an interval, not a point estimate.

This claim needs **no contested estimator, no independence assumption, and no assertion about
anyone else's paper.** It is the strongest thing the campaign owns.

**N_eff/m is hereby DEMOTED to a scoped mechanism diagnostic** and must be reported with `m`,
box occupancy, and the scaling exponent `s`. It must be stated explicitly that **it does not
predict this reversal** — nodewise has far LOWER effective independence than layerwise at 40
epochs (0.2796 vs 0.6903) and yet WINS on accuracy by 1.258 pp, 7/7.

### 86.4 **UNVERIFIED HIGH-SEVERITY RISK: THE Adam-mini / Adalayer / SGG ATTRIBUTION.**

An audit reports full-text greps finding **no** sqrt(N)/noise-averaging/effective-sample
argument in any of the three, that Adam-mini argues from **Hessian block structure**, Adalayer
from **second-moment storage coarseness**, and that SGG asserts the **opposite** (intra-correlated
groups). **I could not verify this: none of the three PDFs is on local disk, and the same audit
caught a WebFetch summariser FABRICATING an SGG sentence.** So this is an open risk, not a finding.

It is load-bearing. Our own prose asserts the attribution in at least
`CORRECTIONS.md:1460`, `FINDINGS.md:8920/8945/9103/9114`, `CONTINUE-HERE.md:475/917` —
including the phrases *"the core refutation"* and *"the Adam-mini / Adalayer / SGG line assumes
exactly 0."*

**GATE, effective now: no document may assert what Adam-mini, Adalayer or SGG assume until the
three PDFs have been read locally and the specific sentence quoted.** If the attribution fails,
the measurement survives untouched — only its framing as a refutation *of those papers* dies,
and 86.3 does not depend on it at all.

## 87. DECISION RECORD — cycle 58 (ALICE DOWN, **THIRD** CONSECUTIVE TICK, ZERO JOBS)

**OUTAGE, localised not assumed.** `2026-08-22T16:25Z`: `ssh alice-gw` up and answering; from it
`nc` to `login.alice.universiteitleiden.nl:22` and to both `132.229.104.230` / `.231` returns
DOWN. `ssh alice` and `ssh alice2` fail at banner exchange. **No queue read, nothing synced,
nothing submitted. CSV unchanged at 1707 rows.** `bo7-*` (12, alice) and `bd7-*` (12, alice2)
were RUNNING at the end of cycle 54; **whether they survived is still UNKNOWN and still not
guessed.** No ssh config touched, no retry loop run.

1. **GATE 86.4 IS DISCHARGED, AND IT RESOLVES AGAINST OUR OWN PROSE.** All three papers are now
   on local disk (`paper/refs/`, arXiv full text, not a summariser). Across all three:
   `"law of large"` 0, `"effective sample"` 0, and every `"noise"` hit is a bibliography entry
   or an unrelated aside. **Adam-mini argues from Hessian block structure**, and its stated
   reasons for AVERAGING are *"grid-search is too expensive"*, borrowability from Adam, and —
   decisively — that *"they all share the same BP error term e_i … G usually has **similar
   entries within a row**"*, which is a **CORRELATION** argument. **Adalayer** argues from
   *"coarser and coarser"* second-moment **storage**. **SGG asserts the opposite of
   independence**: *"parameters in LLMs exhibit non-independent optimization behaviors,
   inherently forming intra-correlated groups."*
   > **No paper in that line justifies coarse granularity by √N noise-averaging. Every
   > sentence of the form "the Adam-mini / Adalayer / SGG line assumes exactly 0" or "the core
   > refutation" is WITHDRAWN** (≥ `CORRECTIONS.md:1460`, `FINDINGS.md:8920/8945/9103/9114`,
   > `CONTINUE-HERE.md:475/917`). The measurement survives; its framing as a refutation *of
   > those papers* does not. 86.3 never depended on it. → 58.2

2. **AND THE REAL TARGET IS BETTER THAN THE STRAWMAN.** Adam-mini's actual premise — the mean of
   a block represents the block because a row of `G = e·zᵀ` shares its BP error term — is
   directly testable on our corpus, and **a "row of G" is exactly our `nodewise` partition.**
   This is a live research direction and it is recorded as one, not acted on this tick.

3. **86.3 IS CONFIRMED TO THREE DECIMALS** by an instrument written this tick that re-derives it
   from the raw `.out` series independently (`--control` prints REPRODUCED EXACTLY at all six
   epochs). **This tick did not overturn 86.3; it generalised it and then scoped it.** → 58.1

4. **THE U IN TRAINING TIME IS GENERAL — 41 CELLS, 5 BATCH FAMILIES, 3 NETWORKS, 2 DATASETS.**
   86.3 rested on 2 batches at 1 meta-stepsize. **The CROSSING EPOCH is what is not general:**
   it falls with ms (**47 measured at 3e-4** against 20 at 1e-3; still descending at epoch 20 at
   ms ≤ 2e-4), **rises with depth** (ResNet34 still −1.1pp at epoch 20 in **5 of 5** independent
   batches), and falls with task difficulty (CIFAR-100 crossed by ~16).
   > **"between epoch 15 and 25" is a ResNet18 / CIFAR-10 / ms=1e-3 number and may not be
   > written as a general property of granularity.** [LABELLED POST-HOC.] → 58.3

5. **THE REVERSAL PERSISTS TO 100 EPOCHS AT FIXED ms** (+1.594 at epoch 100, unpaired n=1), so
   it is not a 40-epoch window artefact. → 58.4

6. **BUT UNDER PER-ARM TUNING THE CURVE IS MIRRORED, AND THAT THREATENS THE HEADLINE.** Each arm
   at its own optimum (lay@1e-4 vs node@3e-4): **+3.286 @10 → +0.317 @50 → −0.168 @100.**
   Nodewise starts AHEAD and fades to a tie. **Every cell in item 4 shares a single ms across
   both arms, and at ms=1e-3 layerwise is 1.86pp off its own peak while nodewise is 0.10pp off
   its own — so the "reversal" may be measuring distance-from-optimum, not granularity.**
   n=1 vs n=2 and unpaired; **it cannot carry the claim, and it is not being written as one.**
   → 58.5

7. **THE TUNED PEAK ROW AT 100 EPOCHS SAYS GRANULARITY-AMONG-PARTITIONS IS UNRESOLVABLE.**
   layerwise 92.824 (1e-4, n=2, sd 0.291) / nodewise 92.656 (3e-4, n=1) / blk6 92.652 (1e-4,
   n=2) / scalar 92.198 (1e-4, n=2). **The three partitioned arms span 0.172pp — inside
   layerwise's own sd. Partition-vs-none is 0.454–0.626pp and is the only resolvable effect.**
   This **independently confirms 57.2 by a different cut**: partitioning buys TOLERANCE to an
   over-large meta-stepsize; the +1.59pp nodewise advantage at ms=1e-3 is a tolerance gap, not
   an accuracy gap. → 58.6

8. **WRITTEN, VALIDATED, NOT SUBMITTED: `bin/c58_tuned_horizon.sh`** — 9 jobs, alice, `hz9-*`,
   100 epochs. Gates H0 (epochs_done==100 hard drop) → H0.3 → **H0.5 (POOLING GATE, CAN ONLY
   VOID)** → **H1** (slope; ≥+0.30 T-A the reversal survives tuning, ≤−0.30 T-B it is a
   shared-ms effect) → H1b (level, ±0.50 = 2.7 SE, **TIED is a RESULT**) → H2 (paired ms=1e-3 at
   100 epochs). **A DIRECTION IS REGISTERED, deliberately** — the pilot gives D=−0.485 and points
   at T-B, written down in advance so T-B REPLICATES rather than discovers and T-A visibly
   overturns this cycle's own read. This is the opposite of `rw9`'s "no direction registered";
   the difference is that `rw9`'s one point was consistent with both branches and this one is
   not. 7 guards, `bash -n` clean, guards 3b/4 re-run standalone, loop verified to emit exactly
   9 names. **Not new cells:** c40 requested 25 `rs-node` jobs, 10 reached the corpus, 6 of those
   are truncated — **15 nodewise jobs never landed** and `hz9` is the tuned half that never
   arrived. → 58.7

9. **SUBMISSION ORDER IS RE-RANKED ON ALICE, AND BOTH OLDER BATCHES STILL GO.** `sp8` (9, alice2)
   is unaffected and unranked against these — different account. On alice: **`hz9` (9) BEFORE
   `rw9` (18)**. Reason, stated so it can be overruled: `rw9` decides D2, a question about the
   weightwise arm; `hz9` decides whether the campaign's CURRENT HEADLINE is a claim about
   granularity or a claim about a shared, over-large meta-stepsize. More load-bearing, half the
   cost. **Nothing is cancelled and nothing is dropped.** The 12 truncated `rs-blk6`/`rs-node`
   reruns remain LAST.

10. **IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous fourteen.

11. **THE `stepsize_type` CODE CHANGE REMAINS UNMADE** and is re-flagged for the operator
    (76.9, 71, 81.10, 83.11, 86.10). Not done unsupervised.

12. **HOUSEKEEPING — A NUMBERING COLLISION IN THIS FILE.** There are **two `## 86` sections**
    (cycle 57's decision record at ~2751 and cycle 56's window/accuracy-reversal entry at
    ~2850). Both are cited elsewhere as "86". This record is 87; the collision is left in place
    rather than silently renumbered, because renumbering would break existing cross-references.
    Cite cycle-56's as **86 (cycle 56)** and cycle-57's as **86 (cycle 57)**.

13. **ORPHANS.** No new sweep this tick; the standing item from 86.11 is unchanged and is NOT
    re-discovered. Three families were retired last cycle (`rs`, `a0`, `gate0c`); this cycle
    **cites `rs` again** (58.4–58.6), and additionally cites `ml5`, `ns5`, `p7`, `ff5`, `fz3`,
    `p6f`, `uc5`, `uc6`, `fr5`, `wc5`, `p4`, `p5`, `p2`, `p3`, `bo6`, `fz` through 58.3's
    41-cell inventory. **`analysis/c58_horizon_reversal.py --inventory` is now the cheap way to
    show a family is cited**, alongside `c57_surface_truncation.py --audit`.

**NEXT TICK, in order.**
(a) **Reachability first**, one line:
    `ssh alice-gw 'nc -z -w 8 login.alice.universiteitleiden.nl 22 && echo UP || echo DOWN'`.
(b) **If up: `squeue` BOTH accounts before anything else** — `bo7`/`bd7` survived or must be
    resubmitted. Do not assume either.
(c) Submit **`sp8` (alice2, 9)**, then on alice **`hz9` (9) then `rw9` (18)**. Each re-runs its
    own guards; `hz9`'s guard 3 is the precondition for its own H1 and must not be skipped.
(d) **Score `hz9` H0 → H0.3 → H0.5 → H1 → H1b → H2, IN THAT ORDER.** H0.5 can only VOID.
(e) If `bo7`/`bd7` landed, cycle 54's scoring order stands with 55.2's measured per-seed sd.
(f) **Still unspent:** the raw-instrument `s` re-derivation, carried since 51. **New and ranked
    above it:** test Adam-mini's ACTUAL premise (item 2) — within-row similarity of `G = e·zᵀ`
    at the `nodewise` partition — against our own probes.

**Queues at tick end.** UNKNOWN — both login nodes unreachable. FairShare not readable.

### 87.14 AMENDMENT, SAME TICK — 58.6 IS CORRECTED AND A SUSPICION IS WITHDRAWN

* **The suspicion that 57.2's falloff row was contaminated is WITHDRAWN.** It reproduces exactly:
  nodewise `(92.547−91.310)/log10(3) = 2.592` against the published 2.593, on P0-clean runs.
  57.2 filtered correctly. Recorded because the suspicion was formed and acted on.
  **What is true and narrower:** nodewise's peak LOCATION is n=1 vs n=1 and moves between ms=1e-3
  (k=20) and ms=3e-4 (k=5) on a **0.098pp** difference. That is what `hz9` buys.
* **Item 7 of this record is CORRECTED.** Its table was `rs`-only. On the full 14-column config
  key, pooling the three families at that operating point (`ms`, `mx`, `rs`, which agree within
  sd): layerwise **92.906**(n=5, sd 0.166) / nodewise 92.656(**n=1**) / blk6 92.652(n=2) / scalar
  **92.262**(n=5). **The partitioned arms span 0.254pp against sd 0.166 — NOT "inside layerwise's
  own sd", and the sentence "granularity among partitions is unresolvable" is WITHDRAWN.**
  Partition-vs-none is 0.390–0.644pp and remains the resolvable effect. → 58.8
* **The tolerance sentence survives in a peak-location-independent form** — loss taken at a fixed
  over-large ms=1e-3 relative to each arm's own tuned peak: **scalar 4.480 ≫ layerwise 1.736 >
  blk6 1.022 > nodewise 0.098** (the last is n=1).
* **This caught a live bug before submission.** `hz9`'s guard 4 asserted `spread < sd` on the
  superseded `rs`-only numbers; under the corrected row that is FALSE and **the guard would have
  aborted the batch**. Guard 4 now carries the pooled row and asserts the ordering plus
  "nodewise is still n=1". `bash -n` clean, re-run standalone and passing.

## 88. DECISION RECORD — cycle 59 (ALICE DOWN, **FOURTH** CONSECUTIVE TICK, ZERO JOBS)

**OUTAGE, localised not assumed.** `2026-08-22T19:26Z`: `ssh alice-gw` up and answering
(`p-cfer-016105`); from it `nc` to `login.alice.universiteitleiden.nl:22` and to both
`132.229.104.230` / `.231` returns DOWN; `ssh alice` and `ssh alice2` fail at banner exchange.
**No queue read, nothing synced, nothing submitted. CSV unchanged at 1707 rows.** `bo7-*` (12,
alice) and `bd7-*` (12, alice2) were RUNNING at the end of cycle 54; whether they survived is
still UNKNOWN and still not guessed. No ssh config touched, no retry loop run.

1. **DECISION: spend the tick on the highest-ranked OFFLINE item rather than idling.**
   87.2 ranked "test Adam-mini's ACTUAL within-row-similarity premise at the `nodewise`
   partition" above the carried-since-51 `s` re-derivation. It needs only probes already on
   this Mac. Cycles 55 and 58 both produced real results under the same outage; this follows
   that precedent. → 59.0

2. **THE PREMISE IS TESTABLE BECAUSE OUR `nodewise` PARTITION *IS* A ROW OF `G`** — verified in
   the optimizer source (`HF_patched.py:147` groups by `p_size[0]` and sums all trailing dims),
   not inferred from the name. → 59.1

3. **SCOPE WRITTEN INTO THE INSTRUMENT ITSELF, SO IT CANNOT DRIFT.** Adam-mini's premise is
   about `G`; PATCH_PROBE5 recorded the sign of `z`, the META-gradient. The structural argument
   transfers but the quantities differ. **No document may write "we refuted Adam-mini".** The
   claim is about the premise AS IT APPLIES TO THE QUANTITY OUR PARTITION AGGREGATES. → 59.1

4. **THE COORDINATE→ROW MAP IS MEASURED, NOT ASSUMED.** A0 reconstructs
   (tensors, nodes, weights) exactly against three independent on-disk numbers in **4 of 4**
   families. A2 separates 1-D coordinates from conv coordinates at **z = 38.8–135.3** against a
   random-subset null, 4 of 4, same sign. A1 (3×3 spatial signature) is present but weak and
   the map is certified on A0+A2, with A1 reported rather than leaned on. → 59.2

5. **THE RESULT, AND IT IS A CLEAN NEGATIVE.** In **48 of 58 unique weightwise arms** the row
   explains **0.083%–0.612%** (median **0.190%**) of the within-tensor structure in per-weight
   meta-gradient sign preference, against a size-preserving within-tensor regroup null of
   **0.069%–0.175%** (median 0.091%). **97–99% of the structure is WITHIN the row.** Raw and
   noise-corrected readings agree, so the conclusion is bounded on both sides. 4 of 4 families,
   2 datasets, frozen and free beta, across the clip ladder. **The row mean does not represent
   the row.** → 59.3

6. **AND NEITHER DOES THE TENSOR** — 0.80%–2.55% of the corrected total. Per-weight sign
   preference is overwhelmingly idiosyncratic at every partition level we can form. → 59.3

7. **A STATISTIC-CONFUSION HAZARD, NAMED BEFORE IT BITES.** `p_i` (temporal persistence per
   coordinate) is NOT the campaign's 53.1% sign-agreement headline (cross-sectional imbalance
   at one step). They are different quantities, they do not conflict, and neither supersedes
   the other. Do not let 59.3's "~0.2%" be read as a retraction of 8b. → 59.3

8. **THE OBVIOUS EXPLANATION OF THE 10 EXCEPTIONS IS REFUTED BY OUR OWN CONTROL.** Six are the
   ms=1e-2 rung CORRECTIONS 62 already ruled unquotable; two are AdamW-base; one is `bl5`'s
   single documented bound seed. But **"clipping manufactures row structure" is FALSE**:
   `cl5-cD` is 75.7–76.4% pinned with R_row 0.164–0.196%, at the null. **The mechanism of the
   exceptions is OPEN and is recorded as open.** The 3/3 "modal ceiling exactly 0.000" pattern
   is n=3, POST-HOC, and labelled as not a finding. → 59.4

9. **THE PINNING DETECTOR VALIDATED ITSELF AGAINST A PUBLISHED NUMBER.** It returns bl5's
   per-seed HIGH-guard binding as 24.05% / 0.4% / 0.5% against CORRECTIONS 53's recorded
   **24.07% / 0.00% / 0.00%** — 3 s.f. on the bound seed. It also carries an explicit
   `moved` flag so a FROZEN arm (beta constant ⇒ modal fraction trivially 100%) cannot be
   mis-read as fully pinned; that false positive was caught in this tick and fixed. → 59.4

10. **59.3 CORRECTLY PREDICTS AN ORDERING WE ALREADY MEASURED, AND THAT IS ALL IT DOES.** If a
    partition's value came from its group mean representing its members, nodewise (14,420
    groups) should dominate layerwise (62). 58.8 says it does not — partitioned arms span
    0.254pp against partition-vs-none's 0.390–0.644pp. **Written as a surviving mechanism
    candidate, never as proof.** → 59.5

11. **A SWEEP HAZARD FOR EVERY FUTURE TICK.** `probes_ml5_m{2,3,4}/*` are **SYMLINKS into
    `probes_ml5/*`** (identical md5). A naive glob reports **67** weightwise arms where there
    are **58**. Deduplicate by `os.path.realpath`. This tick's first grouped table was wrong on
    exactly this and is not the version recorded. → 59.6

12. **ORPHANS.** CSV unchanged, so the SET is unchanged from 87.13; coverage is not.
    `c59_row_premise.py --report` now cites all 58 unique weightwise arms with per-arm numbers
    across **13 families** (bl5, bo6, br6, cl5, ff5, fr5, fz3, ml5, ns5, p5, uc5, uc6, wc5),
    which retires their weightwise arms from orphan status. → 59.6

13. **NOTHING SUBMITTED, NOTHING CANCELLED, NOTHING RE-RUN.** `sp8` (9, alice2), `hz9` (9,
    alice) and `rw9` (18, alice) remain written, validated and UNSUBMITTED; cycle 58's
    submission order (sp8 on alice2; hz9 then rw9 on alice) stands unchanged. Ideas 1 and 2
    stay dead — zero jobs, this cycle and the previous fifteen.

14. **THE `stepsize_type` CODE CHANGE REMAINS UNMADE** and is re-flagged for the operator
    (76.9, 71, 81.10, 83.11, 86.10, 87.11). Not done unsupervised.

**NEXT TICK, in order.**
(a) **Reachability first**, one line:
    `ssh alice-gw 'nc -z -w 8 login.alice.universiteitleiden.nl 22 && echo UP || echo DOWN'`.
(b) **If up: `squeue` BOTH accounts before anything else** — `bo7`/`bd7` survived or must be
    resubmitted. Do not assume either.
(c) Submit **`sp8` (alice2, 9)**, then on alice **`hz9` (9) then `rw9` (18)**. Unchanged.
(d) **Score `hz9` H0 → H0.3 → H0.5 → H1 → H1b → H2, IN THAT ORDER.** H0.5 can only VOID.
(e) **NEW, and cheap, and it is the natural follow-on to 59.3:** the same nested decomposition
    is available at the **nodewise** arms' own `neg_counts` (67 arms exist, `n_tot` 8660–25556),
    which measures the row-level statistic the optimizer ACTUALLY adapts on rather than the
    per-weight one aggregated offline. It needs no new mapping work — the row index IS the
    coordinate index there — and would say whether the near-zero R_row survives when the row is
    the adapted unit.
(f) **Still unspent:** the raw-instrument `s` re-derivation, carried since 51.

**Queues at tick end.** UNKNOWN — both login nodes unreachable for a fourth consecutive tick.
FairShare not readable.

### 88.15 SAME TICK — THE SHARPER TEST LANDED TOO, AND IT STRENGTHENS 5

**The ROW DIRECTION is not privileged.** Adam-mini's argument is specifically that a row is
homogeneous because its entries share the BP error term `e_i`. Scoring row / column / spatial
groupings with the same nested estimator, each against **its own** size-preserving null, over
10 arms spanning frozen and free beta, clipped and unclipped, 3 families and 2 datasets:
excess over null is **row 0.008–0.448 pp, column −0.133–0.788 pp, spatial ~0.000–0.010 pp**.

* **Claimed:** no direction carries structure a group mean could exploit; row ≈ column, both
  under ~1pp. Spatial (shares neither `e_i` nor `z_j`) at ~0 confirms the estimator is not
  reading noise as signal.
* **NOT claimed, and explicitly refused:** the row's nominal 8-of-10 edge over the column. Two
  column excesses are NEGATIVE and the single largest excess in the table is a COLUMN. That is
  an estimator scattering around zero, not an ordering.

This closes the one alternative reading item 5 left open — that rows might be weak but still
the best available grouping. They are not. → 59.7

**Instrument now 46/46 selftests**, including a planted-row-signal test that `row` recovers
(>0.999) and `spatial` is blind to (<0.01). A packaging bug was caught and fixed in-tick: the
direction functions were appended AFTER the `__main__` guard, so `--selftest` raised
`NameError` rather than silently skipping them; the guard now sits at end of file.

### 88.16 SAME TICK — THE COMPLEMENTARY HALF LANDS, AND THE MECHANISM STORY CLOSES

Run at the **nodewise arms**, where the row is the unit the optimizer actually adapts and no
offline aggregation is involved. **50 clean arms: R_tensor_cor 86.88%–97.06%, median 93.50%**,
null 0.19%–0.50%; identity error <= 1.0e-14.

**The nodewise partition fails from BOTH sides.** A row mean does not represent its weights
(59.3: 97–99% of per-weight structure is within-row) **and** rows are not distinguishable from
one another either (59.8: ~93% of row-level structure is explained by the tensor). 59.3 alone
left open that nodewise might still help by supplying 232× more adaptable units even if each
were a poor summary; **59.8 closes that reading.**

The 8 arms in the ms=1e-2 / AdamW configs INVERT (7.80%–51.42%) — the same configs as the 59.4
exceptions, opposite direction, same verdict: separately behaved, separately unquotable,
mechanism OPEN. → 59.8

Still a CONSISTENCY with 58.8 and not a proof of it: these measure `z` sign preference,
58.8 measures plateau accuracy. Unchanged from item 10.

## 89. DECISION RECORD — cycle 60 (ALICE DOWN, **FIFTH** CONSECUTIVE TICK, ZERO JOBS)

**89.0 OPERATIONS.** Outage localised, not assumed, 2026-08-22T22:26Z. `alice-gw` up and
answering (`p-cfer-016105`); from it both `132.229.104.230` and `132.229.104.231` refuse :22 and
`login.alice.universiteitleiden.nl` :22 is DOWN. `ssh alice` / `ssh alice2` fail at banner
exchange. Two probes total, no retry loop, ssh config untouched.

**QUEUE AUDIT: NOT POSSIBLE.** No `squeue` on either account. Nothing was synced, submitted or
cancelled. Per the standing rule this is reported as OUTAGE and no inference is drawn about the
science or about job survival. `bo7-*` (12, alice) / `bd7-*` (12, alice2) remain UNKNOWN.
`sp8` (9, alice2), `hz9` (9, alice), `rw9` (18, alice) remain written, validated, UNSUBMITTED.
Cycle 58's submission order stands unchanged. **CSV unchanged at 1707 rows.**

**ORPHANS.** CSV unchanged, so the orphan set is unchanged from 87.13 / 59.6. No new orphans
created (this tick added no runs) and none retired (this tick cited no new families).

**89.1 THE DECISION.** Alice unreachable for a fifth tick ⇒ the only available work is offline.
Took CONTINUE-HERE item (e), the top-ranked offline item: the mechanism of the 59.4 / 59.8
exceptions. New instrument `analysis/c60_exception_mechanism.py`, **81/81 selftests**, importing
c59's measured architecture map rather than re-deriving it. → FINDINGS 60.0–60.6

**89.2 THE 59.4 / 59.8 EXCEPTIONS ARE EXPLAINED. THE MECHANISM IS NO LONGER OPEN.**
Three hypotheses were registered in the instrument docstring **before any arm was scored**.

* **H_A (1-D bookkeeping artifact) is REFUTED, and backwards.** It is the CLEAN arms that draw a
  median **50.6%** of their numerator from 1-D tensors — 0.086% of coordinates whose "rows" have
  width 1 and therefore contribute **exactly 0** to the denominator by construction. In the
  exceptions the 1-D share is 0.07–2.9%.
* **H_C (saturation / dead channels) is REFUTED by a single number:** conv coordinates with
  `p_i ∈ {0,1}` are **0.000% in all 58 arms**.
* **H_B (genuine conv row structure) HOLDS.** Conv-only R_row_cor: exceptions **7.216–49.412%**,
  clean **0.000–0.448%**. No overlap, 16× gap. The nodewise half agrees and the conv restriction
  SHARPENS it (2.75–6.03% inverted vs 64.56–100.00% normal). → 60.2, 60.3

**89.3 A NEW MEASUREMENT THAT STRENGTHENS THE HEADLINE BY 3×, AND A SENTENCE TO STOP WRITING.**
59.3's published clean band **0.083%–0.612%, median 0.190%** is a MIXTURE over tensor kinds.
Restricted to the tensors Adam-mini's row argument is actually about — conv rows sharing an
output channel — the clean band is **0.000%–0.448%, median 0.063%**. The 1-D tensors, where
"row" and "weight" are the same object and the statistic is vacuous, supplied a median 50.6% of
the old numerator.

> **STANDING RULE (10): any row/group statistic quoted over a mixed parameter stack must state
> its tensor-class restriction.** A partition statistic computed over 1-D tensors is comparing an
> object to itself. Both the all-tensor and the conv-only figure should be given; the conv-only
> figure is the one that answers the premise. This applies retroactively to 59.3 and 59.8 — the
> published numbers are NOT withdrawn (they are correct for what they compute) but they must be
> labelled "all tensors" wherever they appear.

**89.4 THE EXCEPTION IS DYNAMICAL, NOT ARCHITECTURAL — AND THAT IS WHY IT DOES NOT RESCUE THE
PREMISE.** Where it sits IS patterned: block `conv1` carries in **43 of 80** exception tensors
vs `conv2` **5 of 80** on identical denominators (two-sided binomial **p = 1.4e-8**), `conv1 >
conv2` in **10 of 10** arms, and clean arms carry in **0 of 1,008** conv tensors. But WHICH ROWS
carry is not reproducible: cross-seed correlation of within-tensor-centred conv row means is
**0.0053 / 0.0124 / 0.0278** against nulls of 0.0103 / 0.0051 / 0.0016 — at the null in every
exception config. Two within-config controls say it directly: `bl5/e40` seed 0 reads 23.014%
while seeds 1–2 read 0.044% / 0.039%, and `br6/c2` seed 1 reads 7.216% while seeds 0/2/3 read
0.043% / 0.034% / 0.034%. **Same config, same architecture — one seed inverts by 500×.**

Adam-mini's premise is a claim about row IDENTITY (*"they all share the same BP error term
`e_i`"*): output unit `i` is homogeneous BECAUSE it is output unit `i`. 60.5 measures exactly
that quantity and finds it at the null. → 60.4, 60.5

**89.5 STATED AGAINST OUR OWN INTEREST.** Within a single run the exception arms' row structure
is REAL, and a per-row step size could exploit it *in that run*, reproducibility or not. That is
recorded, not buried. It is not Adam-mini's premise, and it is confined to configs already ruled
unquotable (ms=1e-2, CORRECTIONS 62) plus AdamW-base. **Scope unchanged: we measure `z`, the
meta-gradient; Adam-mini argues about `G`. No document may write "we refuted Adam-mini."**

**89.6 AN INSTRUMENT ARTIFACT CAUGHT BY THIS TICK'S OWN GATE, BEFORE IT REACHED A CLAIM.**
The first `--roles` pass reported clean arms carrying in 16 conv tensors, all reading **exactly
100.0%**, and a `conv1` count of 53/80 with 12/408 clean. Every one was the `max(raw−noise,0)`
within-clamp binding — a tensor whose within-row spread falls below the binomial floor reads
R_cor = 1 **by construction**. With per-tensor clamps excluded, clean hits go to **0 of 1,008**
and the exception `conv1` count to 43/80. The published table is the gated one.

The same clamp then falsified one of this tick's own selftests: the synthetic H_B control was
built with within-row spread 1e-4, below the binomial floor 2.2e-2, so it clamped. **The
assertion was wrong, not the code** — it was rewritten to assert the flag FIRES, and a second
control with above-floor spread was added. 74 → 81 selftests.

**89.7 WHAT IS STILL OPEN.** *Why* `conv1` and not `conv2`, and what the run-specific event is.
60.4 gives the signature, not the cause; deciding it needs `z` time-series the probe does not
store. This is a candidate for a future PATCH_PROBE change, **not** for a rerun of existing arms.
Ranked BELOW every cluster item — it is a curiosity about an already-unquotable regime.

**89.8 NEXT TICK, IN ORDER.** (a) reachability, then `squeue` BOTH accounts before anything.
(b) Submit `sp8` (alice2, 9), then on alice `hz9` (9) then `rw9` (18). (c) Score `hz9`
H0 → H0.3 → H0.5 → H1 → H1b → H2, in that order; H0.5 can only VOID. (d) If bo7/bd7 landed,
cycle 54's scoring order stands with 55.2's per-seed sd. (e) **DONE, do not re-run:** the row
premise (59.3), the nodewise half (59.8), the exception mechanism (60.2–60.5). (f) The next
offline item is the carried-since-51 raw-instrument `s` re-derivation — it is now the LAST
unspent offline item. (g) The 12 truncated `rs-blk6`/`rs-node` reruns remain last.

### 89.9 SAME TICK — THE `conv1` SIGNATURE REPRODUCES ON THE COMPLEMENTARY STATISTIC

60.4 was measured at the **weightwise** arms by aggregating per-weight `p_i` into rows. Repeated
at the **nodewise** arms, where each stored coordinate already IS a row mean so no aggregation
happens at all: median noise-corrected `var(row means)` per conv role gives
**V(conv1)/V(conv2) = 0.17–98.42, median 48.39** in the 8 inverted arms against **0.02–4.97,
median 0.55** in 49 normal arms. **7 of 8 inverted arms exceed the maximum of all 49 normal
arms**; Mann-Whitney **p = 5.2e-4**. → 60.7

**The one dissenter is the arm the other method predicts.** `bo6/probe_node_adw_s0` reads 0.17,
and `bo6` is the AdamW family that holds **all 5** of the corpus's weightwise `conv2` hits — the
one place 60.4 already showed the effect reaching `conv2`. The two methods disagree on that arm
for the reason each independently records.

This is the strongest form of confirmation available offline: different arms, different stored
quantity, no shared code path beyond the architecture map that already passed 59.2's A0/A1/A2.
Instrument now **87/87 selftests**. Still WHERE, never WHY — 89.7 stands unchanged.

---

## 90. A PREMISE THIS PROJECT WROTE DOWN TWICE WAS WRONG, AND IT COST AN OPEN QUESTION A RANK (cycle 61)

**90.1 THE CORRECTION.** FINDINGS 60.7 and CORRECTIONS 89.7 both end with *"`conv1` vs `conv2`
needs `z` time-series the probe does not store"*, and 89.7 explicitly ranks the question **below
every cluster item** because of it. **The probe does store one.** `_probe` accumulates `_z_sum` /
`_z_sqsum` / `_z_n` and never resets them, so `z_mean` / `z_std` are CUMULATIVE moments, and
cumulative moments difference exactly into a per-window series. OPERATIONS 22 already noted they
are "temporal" — the gap was between knowing that and acting on it.

**Corrected statement, and it must replace the old one wherever it appears:** a per-TENSOR `z`
time series IS recoverable at zero cost on every arm on this Mac; a per-ROW or per-COORDINATE one
is NOT, because the spatial mean is taken before storage. **89.7 was open at tensor resolution.**

**STANDING RULE (11)**, the eleventh: *before recording a question as unanswerable from stored
data, name the stored field and the reason it cannot answer it.* 89.7 said "the probe does not
store `z` time-series" without naming `z_mean`/`z_std` or checking whether they were cumulative.
Two consecutive handoffs then carried the claim forward unexamined. A one-line reason is what makes
such a claim auditable by the next tick.

**90.2 AND THE ACCUMULATION COUNT IN EVERY FUTURE READING OF THESE FIELDS IS `step+2`.**
`HF_patched.py:72` sets `counter = -1`; `_probe` runs at :95, the increment at :100. So the record
labelled `step=s` folds **s+2** samples. The data confirms it bit-exactly and independently of the
source: n=2 over samples {0, x} forces **`std == |mean|` exactly**, where n=1 would force
`std == 0` exactly. **Measured 0.000e+00 worst-case deviation across all 58 gated arms**, 49/49
weightwise arms at 100% of nonzero-mean tensors. **Free by-product: the first meta-gradient is
exactly zero on every tensor.** Anyone differencing these fields with `n = step+1` inherits an
O(1/n) error — 6.0e−3 at the first window, 2.1e−4 by the twentieth (measured, `--gate`).

**90.3 THE SCIENCE: THE PRE-REGISTERED NULL H3 WINS, AND IT IS REPORTED AS A NULL.**
New instrument `analysis/c61_z_timecourse.py`, **46/46 selftests**, all gates pass. H1/H2/H3 were
registered in the docstring before any arm was scored. Primary statistic — conv1/conv2 ratio of
peak window coherence, 10 exception vs 48 clean arms — is **flat: 0.84–1.17 (med 0.99) against
0.77–1.21 (med 1.02), 0 of 10 above the clean maximum, Mann-Whitney z=−0.16, p=0.87.**

**A secondary statistic did fire (mean coherence, z=+3.89, p=1.0e−4) and is NOT quoted as support**,
because registered CONTROL C1 refutes reading it as a `conv1` story: the exception arms differ at
non-conv roles too, in both directions and with larger |z| (shortcut/conv2 z=−4.61, oneD/conv2
z=−3.87). Their whole role structure is compressed — the ms=1e-2 rung behaving like itself. **A
control written in advance killed this tick's only positive number. That is the control working.**

**90.4 CONTROL C2 IS THE ONE THAT SETTLES IT.** On 60.5's two within-config seed controls, the
seed whose row structure inverts by 500× is **the LOWEST of its three seeds** (`bl5/e40` s0, rank
3 of 3) and **inside the sibling spread** (`br6/c2` s1, rank 2 of 4). A post-hoc `--ksweep` across
a 20× range of window widths (down to 50-step windows) shows the rank **wandering** rather than
sharpening, so the null is not a window-width artefact.

**90.5 WHAT IS AND IS NOT LICENSED — STATED AGAINST OUR OWN INTEREST.** This excludes one specific
rival (a tensor-wide drift episode manufacturing apparent row structure). It **does NOT confirm
H_B**: under H_B the structure is within-tensor and a spatial mean over rows destroys it *by
construction*, so this test's power against H_B was low from the start. Recorded as excluding a
rival, never as evidence for the survivor. **Nothing is withdrawn** — 59.3, 59.8 and 60.2–60.7 are
untouched. 89.7 stays OPEN, now with a specified instrument requirement instead of a vague one.

**90.6 THE DECISION, AND ITS REASON.** Direction **C stays the project** (the operator's default,
and Idea 2 is dead by `KILLTEST-idea2.md`'s own verdict while Idea 1 is crowded by Mechanic /
D-Adaptation / LARS). **The ranking of the pending cluster work CHANGES.** `KILLTEST-idea2.md` §5
already specifies an ~8-line `_probe` change (`t_neg`/`t_zero`/`t_n` per tensor plus a fixed
20,000-coordinate sign subsample, ~10 MB/run, 1–4 runs at ~1 GPU-hour) and 61.4/61.5 arrive at the
**same missing instrument from an unrelated direction**. One change serves three open items:
89.7's mechanism, the kill-test's only surviving question, and direction C's untested claim that
the sign-agreement structure is coordinate-level rather than tensor-level. **It is therefore ranked
above `rw9` (18 jobs) for the first reachable tick.** `sp8` and `hz9` keep their places — they are
cheap and already validated.

**90.7 ORPHANS CLEARED TO 12 RUNS.** 109 families, 2 orphan, 12 runs (from ~290 on 2026-08-22).
Both retired in FINDINGS 61.8 and **not to be re-run**: `gate0b` (unaugmented memorisation regime,
quotable for nothing, ABANDONED) and `gate0d` (SGDm base: blk6 +3.53pp over scalar, against HF
base's scalar +0.33pp — an uncited n=3 consistency with the H4 base-optimizer interaction, recorded
but joining no published table). A truncation note is attached: `gate0c`'s ms=1e-2 column has two
`--max-time`-truncated runs and the comparison uses ms=1e-3 only.

**90.8 NEXT TICK, IN ORDER.** (a) reachability, then `squeue` BOTH accounts before anything.
(a2) **rsync `docs/` to the cluster — it is now three cycles behind.** (b) Submit `sp8`
(alice2, 9), then on alice `hz9` (9). (c) **Then the `PATCH_PROBE` per-coordinate change and its
1–4 runs (90.6), ranked ABOVE `rw9`.** (d) Score `hz9` H0 → H0.3 → H0.5 → H1 → H1b → H2, in that
order; H0.5 can only VOID. (e) If bo7/bd7 landed, cycle 54's scoring order stands with 55.2's
per-seed sd. (f) **DONE, do not re-run:** the row premise (59.3), the nodewise half (59.8), the
exception mechanism (60.2–60.7), **and now the tensor-mean avenue for 89.7 (61.4/61.5)**. (g) The
raw-instrument `s` re-derivation is now the ONLY unspent offline item, carried since 51, and it is
bookkeeping. (h) The 12 truncated `rs-blk6`/`rs-node` reruns remain last.

---

## 91. A RECORDED IMPOSSIBILITY WAS HALF WRONG, AND THE HALF THAT WAS WRONG IS THE PAPER'S DELIVERABLE (cycle 62)

**91.0 STATE.** ALICE unreachable for a **SEVENTH** consecutive tick — gateway UP
(`p-cfer-016105`), both login IPs refusing :22 from it, both accounts failing at banner
exchange, checked **2026-08-23T04:25Z** and again at **04:43Z**. Nothing submitted, nothing
cancelled, nothing synced, no queue read. CSV unchanged at 1707. `sp8` (9, alice2), `hz9` (9,
alice), `cp9` (8, alice), `rw9` (18, alice) all remain written, validated and UNSUBMITTED;
`docs/` is now **four** cycles behind on the cluster.

**91.1 THE DECISION, AND ITS REASON.** CONTINUE-HERE's offline list was down to one item, the
carried-since-51 `s` re-derivation, explicitly labelled *bookkeeping*. Rather than spend a
seventh tick on it, I applied **STANDING RULE (11)** — the rule cycle 61 installed after
exactly this failure mode — to the one *recorded impossibility* that blocks the operator's
DEFAULT deliverable: FINDINGS **52.12**, *"the granularity curve cannot be recovered offline …
filling the layerwise↔weightwise interval requires a new `stepsize_type` in `HF.py`"*.

Naming the field, as (11) requires, splits it:

* `rho_s` / `N_eff` are derived from **`frac_neg`**, a per-record **pooled scalar**. No
  coordinate resolution ⇒ **52.12 IS CORRECT for the correlation channel and is NOT WITHDRAWN.**
  That half still needs a code change to the optimizer under study and an operator decision.
* The **marginal-bias channel** is `neg_counts.npy` — **11,173,962 per-coordinate counts** per
  R18 weightwise arm. It re-blocks post hoc at **any** block size, at zero compute.
  **52.12's final clause is WRONG and is withdrawn.**

FINDINGS 43.3 is what makes this matter rather than being a technicality: at a0=1e−6 the
marginal channel accounts for **all** of the agreement excess over the independence floor.
**The channel 52.12 declared unreachable is the one carrying the headline.** → FINDINGS 62.1

**91.2 THE INSTRUMENT.** `analysis/c62_blocksize_curve.py`, **83/83 selftests**, importing
c59's measured architecture map and c60's class/clamp machinery, and using c59's `nested_ss` /
`noise_split` verbatim. Real-data gates: **G1** — the u=1 rung equals c60's published
`R_conv_cor` via the independent c59/c60 code path to **4.337e−19** across 6 arms; **G4** —
the SS identity holds to **1.510e−14** over 102 (arm, rung) cells. It is a generalisation of a
published number, not a new statistic that happens to agree. → FINDINGS 62.2

**91.3 THREE OF THIS TICK'S OWN ASSERTIONS WERE WRONG AND ITS HARNESS CAUGHT ALL THREE.**
In each case the assertion, not the code: comparing `abs(a−b)` where both paths correctly read
`nan`; expecting an offset to add one partial block in total rather than one **per tensor**;
asserting monotonicity on the CORRECTED null, which is `nan` wherever the clamp binds.

**91.4 AND A FOURTH CATCH WAS A REAL MEASUREMENT LIMIT, RECORDED BEFORE USE, NOT AFTER.**
The recovery gate planted **perfectly constant** blocks. That makes `SS_within` pure sampling
noise, so `max(raw − noise, 0)` binds **at exactly the planted rung** — the true peak
(`E = 97.9 pp`) is excluded by CORRECTIONS 89.6's own rule and the peak is misread one rung low.

> **A perfectly homogeneous block is the one structure this readout cannot locate.** That is a
> property of the clamp and it is now stated in the instrument docstring, not discovered later.

**91.5 THE REGISTERED SCIENCE: TWO HYPOTHESES DIED, AND ONE OF THEM WAS A HOPED-FOR
CONFIRMATION.** H1/H2/H3 were registered before any arm was scored.

* **H3 (null everywhere) REFUTED**: E/res = **9.5–169 at every rung**. 59.3's one-point row
  result does not generalise — **59.3 measured the within-tensor marginal structure at the one
  block size where it is smallest.** 59.3 is not withdrawn; its scope is now known.
* **H1 (channel knee) REFUTED**: no peak at u=1. The marginal channel does **not** reproduce
  48.18's *"the correlation length is approximately the channel"*. **This was the outcome that
  would have made the campaign's sharpest result independently confirmed through a second
  statistic. It did not happen, and the dissociation is reported as the result.** 48.18 is
  untouched — it is a statement about the correlation channel and this is a different channel.
* **H2 (sub-channel) survives** on the one arm scored so far (62.4), pending 62.8's C62-C.

**91.6 S1/S2 FIRED AND S4 — REGISTERED IN ADVANCE PRECISELY TO SEPARATE THEM — REFUSED THE
OBVIOUS READING.** g=9 aligned/offset ratio **1.92** (registered ≥1.5), local max at g=9,
mod-9 direction at **0.0026 pp** reproducing 59.7's null. Every one of those is consistent with
a 3×3 *filter* object. But a filter also lies inside one input channel, and 59.7 already
measured a COLUMN excess up to +0.788 pp, so **S2 alone cannot license the word "filter"**.
S4 tests the `o × i` interaction directly:

> **F_int = 0.811 – 1.041 across ALL 50 clean weightwise arms** (13 families, 4 architectures,
> 2 datasets). The registered threshold was 1.10. **It is not reached in a single arm.**

**The g=9 phase effect is additive row + input-channel structure. There is no filter-level
object, and no document may write one.** → FINDINGS 62.5

**91.7 THE POSITIVE, PRESCRIPTIVE RESULT.** `F_row` and `F_col` are both above the null in
essentially every clean arm. Every partition in the Adam-mini / Adalayer / SGG line is at the
**output channel or coarser**, and such a partition captures the row effect exactly and the
**input-channel effect not at all, by construction** — the two directions are orthogonal to it.
This is the first prescriptive sentence the C direction has produced rather than a refutation.
**Scope unchanged: we measure `z`; they argue about `G`. No document may write "we refuted
Adam-mini."** → FINDINGS 62.6

**91.8 A POST-HOC DOSE-RESPONSE, LABELLED AS ONE.** `F_col/F_row` on the matched R18/CIFAR-10
ladder: **0.700–0.753 (β frozen) < 0.825–0.887 (ms=1e−4) < 0.892–0.917 (2e−4) <
0.957–0.958 (5e−4) < 0.994–1.107 (1e−3) < 1.411–1.578 (1e−2)** — six rungs, five adjacent
gaps, every gap clean, crossing 1.0 between 5e−4 and 1e−3. Whole-corpus Mann-Whitney
**U = 542/544, z = +5.62**, two crossing pairs. Under 76(1)/79 read symmetrically this
**may not overturn a registered gate** and does not. The ms=1e−2 rung is boundary-dominated
(62) and the trend stands without it. "Adaptation extent" is an interpretation; the
confirmation test (C62-A) is **BLOCKED** on 55.4's owed reconciliation of the two incompatible
`span` definitions, and registering it without that would repeat the CORRECTIONS 41 pathology.
→ FINDINGS 62.7, 62.8

**91.9 ORPHANS.** CSV unchanged (this tick added no runs), so the orphan set is unchanged from
90.7: **109 families, 2 orphan, 12 runs**, both already retired in FINDINGS 61.8 and not to be
re-run. This tick cites `fz3`, `p5`, `ff5`, `cl5`, `fr5`, `ml5`, `ns5`, `uc5`, `uc6`, `wc5`,
`bl5`, `br6`, `bo6` — all already-cited families, so no orphan is retired and none is created.

**91.9b THE CORPUS SWEEP LANDED AFTER 91.6 WAS WRITTEN, AND IT DEMOTES ONE OF THIS TICK'S OWN
TESTS.** Over 17 clean arms: **S2's SIGN holds 17/17** (aligned > offset-4 at g=9, sign test
p=1.5e-5) but its **registered ratio bar of 1.5 is met in only 9 of 16** scorable arms (median
1.60). **S1's registered form passes 11 of 17 and is therefore NOT reported as a result.** What
IS unanimous is the unrestricted argmax: **g <= 9 in 17 of 17 arms**, never coarser than one
3x3 kernel, with E flat below 9 (median ratio 1.10) and falling by a median **2.24x by g=27**
and **5.38x by g=576**, 17/17 in both. That shape is what 91.6's additive row+column result
PREDICTS -- an aligned block of g<=9 lies inside one (o,i) cell -- so S1/S2/S4 are one result,
and it is the additive one. S3 reproduces 59.7's null on the same arms (-0.0003 to +0.0098 pp
against the published ~0.000-0.010), which is the registered precondition for reporting any of
them. **The scale statement, with its number: the output-channel partition is 566-4608
coordinates here; the structure is maximally captured at 2-9. Every partition in that line is
60x-500x too coarse, along the one axis that leaves the other uncaptured.** -> FINDINGS 62.9

**91.10 NEXT TICK, IN ORDER.** (a) reachability, then `squeue` BOTH accounts before anything.
(a2) **rsync `docs/` — it is now FOUR cycles behind.** (b) Submit `sp8` (alice2, 9), then
`hz9` (9, alice). (c) Then `cp9` (8, alice) after applying `patches/patch_probe6_coord.py` on
the cluster; guard 2 refuses without it. Ranked above `rw9` (90.6) — and 62.5/62.6 **raise its
value again**, because the input-channel direction it would resolve at coordinate level is now
the direction carrying half the measured structure. (d) Score `hz9` H0 → H0.3 → H0.5 → H1 →
H1b → H2; H0.5 can only VOID. (e) If bo7/bd7 landed, cycle 54's order stands with 55.2's
per-seed sd. (f) **DONE, do not re-run:** 59.3, 59.8, 60.2–60.7, the tensor-mean avenue for
89.7 (61.4/61.5), **and now the filter hypothesis (62.5, 50 arms, closed)**. (g) The offline
queue is C62-C (the conv-only u-ladder on all four families), then C62-A **once 55.4's span
reconciliation is discharged**, then the carried-since-51 `s` re-derivation. (h) The 12
truncated `rs-blk6`/`rs-node` reruns remain last.

## 92. DECISION RECORD — cycle 63 (ALICE DOWN, **EIGHTH** CONSECUTIVE TICK, ZERO JOBS)

**92.0 STATE.** Reachability checked **2026-08-23T07:25Z**, localised not assumed: gateway UP
and answering (`p-cfer-016105`); `132.229.104.230` and `.231` both refuse :22 **from the
gateway**; `ssh alice` and `ssh alice2` both fail at banner exchange. **No queue read, nothing
synced, nothing submitted, nothing cancelled. CSV unchanged at 1707.** `bo7-*` (12, alice) /
`bd7-*` (12, alice2) survival still UNKNOWN and still not guessed. `sp8` (9, alice2), `hz9`
(9, alice), `cp9` (8, alice), `rw9` (18, alice) all remain written, validated and UNSUBMITTED.
**`docs/` is now FIVE cycles behind on the cluster.**

**92.1 THE DECISION, AND ITS REASON.** 91.10(g) left an ordered offline queue: C62-C first,
then C62-A **once the `span` debt is discharged**, then the carried-since-51 `s`
re-derivation. With the cluster down an eighth tick I executed that queue in its written
order rather than reopening the ranking. **All three of the first two items closed, and the
debt-discharge unblocked the third within the same tick**, so cycle 63 delivered C62-C, the
reconciliation, and C62-A. The `s` re-derivation is again the only unspent offline item and
is again explicitly bookkeeping.

**92.2 C62-C IS CLOSED, 17 OF 17, AND IT CROSS-VALIDATES TWO PUBLISHED READOUTS.**
`analysis/c63_uladder_corpus.py`, 53/53 selftests, a DRIVER over c62 whose arm set is
`c62.SPATIAL_SET` **by reference** (selftest T1). P1–P4 registered and committed (`30a5049`)
before any arm beyond 62.4's single arm was scored. P2 **17/17**, P3 **17/17**, P4 **17/17**;
P1 fires 6/17 so **H2 SURVIVES**. The channel-unit peak is a block of **1–9 coordinates**,
which is 62.9's absolute-g argmax (g ≤ 9, 17/17) reached through a different block index.
**P3 was the first time this project's two block-size readouts were compared and it carried a
branch that would have cost us either 62.4's peak or 62.9's knee.** → FINDINGS 63.1

**92.3 STATED AGAINST OUR OWN INTEREST (63.1).** `U_LADDER` bottoms at 1/1024 and **4 of 17
arms peak on that boundary rung**, so their argmax is censored from below and is a bound, not
a point. No verdict rests on them — all four are already at or below every bar — but they may
not be written as located peaks.

**92.4 THE `span` DEBT OWED SINCE CYCLE 55 IS PAID, AND THE DEBT NAMED ONLY HALF OF ITSELF.**
`analysis/c63_span_reconcile.py`, 38/38 selftests, both definitions IMPORTED not restated,
gate G0 asserting they share `c52_boxfree.records()`. **R2 is exact to 0.000e+00**, so the
time axis is one functional at two evaluation times. **R1's B-arm FAILED**, and chasing the
0.35 identified the axis the debt never named: 55.4's 6.29 is a **three-rung mean**; 74's
8.268 is **weightwise alone**. The 2×2 closes to four decimals; the gap is **1.632 log units
of TIME and 0.347 of ARM SET**. → FINDINGS 63.2

**92.5 STANDING RULE (12).** *A statistic aggregated over a parameter stack must state BOTH
its arm/tensor restriction AND its evaluation window before it is quoted.* STANDING RULE (10)
already required the tensor-class restriction; this cycle shows the window is the larger term
of the two (1.632 vs 0.347 on the debt cell) and was the one nobody wrote down.
**Effective now: `span[weightwise, terminal]` or `span[3-rung, steady-half]`. A bare "span" is
not a quantity in this campaign.**

**92.6 R3 FAILS ITS OWN BAR, AND THAT IS THE USEFUL HALF.** ρ = **0.9654** (bar ≥ 0.95 ✓) but
**6.411% discordant pairs** (bar ≤ 5% ✗) over 162 non-frozen dirs, and `A < B` in 11 of them
so `B ≤ A` is not a theorem. **The two definitions are NOT a monotone reparameterisation**, so
any claim resting on a span ORDERING must name its definition. → FINDINGS 63.3

**92.7 NEITHER PUBLISHED VERDICT MOVES.** **R4:** N2's own predicate with N2's own 5.0
threshold and N2's own argmin column matches on 3 of 4 rungs under **all four** definitions —
the 5e−4 rung is above 5 log units under every one while the argmin is still `w`.
**CORRECTIONS 74(2) stands as written.** **R5:** within 55.4's own 20-epoch scope the
threshold separates under all four, and `3rung/steady` gives max(other) = **6.289** /
min(node) = **8.879** — 55.4's published **6.29 / 8.88**, to the decimal. The BAND form is
clean under all four. **FINDINGS 55.4 stands as written.** → FINDINGS 63.4

**92.8 A TEST OF THIS TICK'S OWN THAT WAS SCORING THE WRONG SHAPE.** R5's first pass reported
"no separation" under all four definitions — because it applied a THRESHOLD test to all 10
DECIDED cells including the 40-epoch `br6/c2`. **55.4 names that exact cell as the reason its
conclusion is a BAND and not a threshold.** Scoring 55.4 by the threshold shape alone tests a
claim 55.4 explicitly disavowed. Both shapes are now scored and selftest T11 asserts the
distinction. **The near-miss was reporting a published finding as unreproducible when the
error was in the scorer's shape, not in the finding.**

**92.9 C62-A WAS UNBLOCKED AND RUN IN THE SAME TICK, AND IT PASSES EVERY REGISTERED BAR.**
`analysis/c63_c62a_travel.py`, 26/26 selftests, A0–A3 registered and committed before any arm
was scored; `MS_MAP` cites the submitting script and line per entry and returns `None` rather
than guessing for `br6`/`uc6`/`bo6`/`fr5`/`wc5`. **A1 ρ = +0.774** (p = 1e−4, n = 40),
**A2 partial ρ = +0.542** controlling `log10(ms)` (n = 29), **A2b ρ = +0.547** (p = 0.011)
within the ms=1e−3 stratum across 4 architectures and 2 datasets. All pass under all four span
definitions. **A2 is load-bearing: 62.7's dose-response is NOT purely an `ms` artifact.**
→ FINDINGS 63.7

**92.9b AND THE TICK'S OWN CONFOUND CHECKS DEMOTE IT — THIS IS REPORTED INSTEAD OF THE
+0.547.** Drop the two 40-epoch `bl5` arms and A2b goes ρ = +0.416 at **p = 0.078**. Restrict
to `r18` alone (fixed ms, architecture and dataset) and ρ = **+0.273 at p = 0.43**, with the
nine 20-epoch arms flat at **0.993–1.108**. Two arms matched on span to **0.0014 log units**
differ in F_col/F_row by **2.17×**; `r10`'s own two seeds differ by **1.76×** at matched span.
**The spread at a single matched span (1.12–2.48) EXCEEDS the entire span-driven range
(≈1.0–1.57).**

> **"Adaptation extent determines F_col/F_row" is REFUTED.** What A2b picks up at fixed `ms`
> is **budget** — a third confound 62.7 never controlled, not a mechanism. **No document may
> write "the column/row ratio measures adaptation extent."** 62.7 remains post-hoc and is now
> bounded on both sides. → FINDINGS 63.8

**92.10 FIVE WRONG ASSERTIONS IN THIS TICK'S OWN HARNESSES, AND IN EVERY CASE THE CODE WAS
RIGHT.** (i) a max-vs-min resolution bar; (ii) a flat-control assertion made over CLAMPED
rungs, which read up to **63 pp by construction** (CORRECTIONS 89.6 / 91.4); (iii) R5's
threshold-vs-band shape (92.8); (iv) demanding partial ρ ≈ 0 where `x` IS the control, which
is 0/0 and must return `nan`; (v) the same error again with `y = 2·z`. **Returning 0.0 from a
degenerate partial-correlation denominator would silently assert "no partial association" —
exactly the failure A2 exists to prevent.** All five are recorded rather than quietly cut.

**92.11 SCOPE, UNCHANGED AND NOT OPTIONAL.** Conv tensors only for the u-ladder; 3×3 conv
tensors only for the kernel-scale and F statistics. We measure `z`, the META-gradient;
Adam-mini / Adalayer / SGG argue about `G`. **No document may write "we refuted Adam-mini."**

**92.12 ORPHANS.** CSV unchanged at 1707, so the orphan set is unchanged from 91.9: **109
families, 2 orphan, 12 runs** (`gate0b`, `gate0d`), both retired in FINDINGS 61.8 and **not to
be re-run**. This tick cites only already-cited families. **None retired, none created.**

**92.13 IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous twenty.

**92.14 NEXT TICK, IN ORDER.** (a) reachability, then `squeue` **both** accounts before
anything. (a2) **rsync `docs/` — it is now FIVE cycles behind.** (b) Submit `sp8` (alice2, 9),
then `hz9` (9, alice). (c) Then `cp9` (8, alice) after applying
`patches/patch_probe6_coord.py` on the cluster; guard 2 refuses without it. Ranked above
`rw9` (90.6), and 62.5/62.6 plus **63.1's second, independent location of the 1–9 coordinate
scale** raise its value again. (d) Score `hz9` H0 → H0.3 → H0.5 → H1 → H1b → H2; H0.5 can only
VOID. (e) If bo7/bd7 landed, cycle 54's order stands with 55.2's per-seed sd. (f) **DONE, do
not re-run:** 59.3, 59.8, 60.2–60.7, the tensor-mean avenue for 89.7, the filter hypothesis
(62.5/62.9), **and now C62-C (63.1), the span reconciliation (63.2–63.4) and C62-A
(63.7–63.8)**. (g) **The offline queue is down to the carried-since-51 `s` re-derivation,
which is bookkeeping.** The next substantive C62-A step is a **fixed-architecture budget
ladder** (R18/C10, ms=1e−3, weightwise, 20/40/80 ep, n≥3) — a SUBMISSION, ranked below
`sp8`/`hz9`/`cp9` because those decide registered gates and it confirms the reading of a
post-hoc trend (63.9). (h) The 12 truncated `rs-blk6`/`rs-node` reruns remain last.

## 93. DECISION RECORD — cycle 64 (ALICE DOWN, **NINTH** CONSECUTIVE TICK, ZERO JOBS)

**93.0 STATE.** Reachability checked **2026-08-23T10:25Z**, localised not assumed: gateway UP and
answering (`p-cfer-016105`); `132.229.104.230` and `.231` both refuse :22 **from the gateway**;
`ssh alice` and `ssh alice2` both fail at banner exchange (exit 255). **No queue read, nothing
synced, nothing submitted, nothing cancelled. CSV unchanged at 1707.** `bo7-*`/`bd7-*` survival
still UNKNOWN and still not guessed. `sp8` (9, alice2), `hz9` (9, alice), `cp9` (8, alice), `rw9`
(18, alice) remain written, validated, UNSUBMITTED. **`docs/` is now SIX cycles behind.**

**93.1 THE DECISION, AND ITS REASON.** 92.14(g) left the offline queue holding exactly one item,
the carried-since-51 `s` re-derivation, explicitly labelled *bookkeeping*. Rather than spend a
ninth tick on it I applied **STANDING RULE (11)** to the operator's DEFAULT deliverable and asked
what direction C had never measured. The answer was not a refutation but a **design choice**:
62.6/91.7 established that the literature's partition captures `a[o]` and not `b[i]` **by
construction**, and then never asked whether, **at matched cost**, the output channel is the
better axis at all. **Nobody in that line compares against the transpose of their own partition.**
That is now measured. → FINDINGS 64.1

**93.2 IT IS NOT A RE-RUN OF THE CLOSED FILTER HYPOTHESIS (92.14(f)).** `out` and `in` are **not
contiguous runs at any `g`** and therefore cannot appear on 62.9's absolute-g ladder; the
input-channel partition had never been scored. `F_row`/`F_col` are SS **ratios** on a matrix of
filter means with the nine taps averaged away — not a fraction of the field, and **carrying no
cost axis**. The `E` statistic, its null, its noise correction and its clamp flags are the
PUBLISHED ones, imported **by reference**; **only the index map is new**, and gate **G1** proves
the new maps are a relabelling of validated ones on **19 real architectures**.

**93.3 THE INSTRUMENT.** `analysis/c64_partition_pareto.py`, **50/50 selftests**, registered and
committed (`cb70c47`) **before any arm was scored**. G6 join gate ties every arm to exactly one
CSV row and requires the hand-written frozen/free tag to agree with that row's `meta` column —
**the stratum is taken from the CSV, never from the tag.**

**93.4 THE REGISTERED RESULT, AND THE PRIMARY IS A NULL.** H_D (precondition, scored first)
PASSES at max|E(spatial)| = **0.0098 pp**, reproducing 59.7. **H_A: CONFIG-DEPENDENT** — E(out)>E(in)
in 10/17, E(in)>E(out) in 7/17. The expectation was registered as CONFIG-DEPENDENT **deliberately**,
so this **confirms this tick's own expectation and is the weaker of the two possible outcomes**.
The sentence it licenses is **"no fixed axis is right"**, NOT "input channel is better".
**H_B: NEITHER** (dominated 7/17 = 41%, against bars of ≥50% / ≤20%). → FINDINGS 64.3

**93.5 THE CLEANEST POSITIVE: 62.9's PEAK IS THE KERNEL, NOT CONTIGUITY.** H_C fires **17/17**:
the semantic `(o,i)` partition — built from the tensor's shape, **non-contiguous in
construction** — beats the output channel in every clean arm. 62.9 located that scale with
contiguous blocks; a partition that shares the scale but not the contiguity reproduces it.

**93.6 THE POST-HOC STRATIFICATION SEPARATES PERFECTLY, AND STAYS POST-HOC.** By the CSV `meta`
column: **β frozen — E(out)>E(in) 8/8, `out` Pareto-dominated 0/8. β free — 2/9, dominated 7/9.**
The matched-pair design (`fz3` vs `ff5`, differing in `meta` ALONE, all at 20 epochs, ms=1e−3,
alpha0=1e−3, same clip, verified per pair from the CSV) flips **6 of 6**, two-sided **p=0.031**
at the (arch,seed) unit — **n=3 at the architecture level, stated not buried** — and is **robust
to three independent null-seed sets**. Per 76(1)/79 this **may not overturn a registered gate and
does not**: H_A stands as CONFIG-DEPENDENT; the stratification **names its axis**. → FINDINGS 64.4

**93.7 THE 92.9b BOUNDARY IS RESTATED SO IT IS NOT CROSSED.** 92.9b refuted "adaptation extent
determines `F_col/F_row`" — a **continuous magnitude** claim with **budget uncontrolled**, whose
spread at a single matched span exceeded the whole span-driven range. 93.6 is a **binary contrast
at exactly matched budget**, on a different statistic, on matched pairs. The two are compatible.
**93.6 does not revive 92.9b's refuted reading, and no document may write "the column/row ratio
measures adaptation extent."** → FINDINGS 64.5

**93.8 A MEASURED LIMIT RECORDED BEFORE SCORING, NOT AFTER (cf. 91.4).** For the 9-coordinate
`oi` partition, `res_pp` **UNDERSTATES** the cell's uncertainty: structureless E wanders over
**[−0.72, +0.13] pp while res reads 0.06–0.38 pp** at a 110k stack. Written into the docstring and
asserted in selftests T13b/T13c **before the data**. **H_B is immune by construction** (`oi` costs
`O*I`, so it can never be a COST dominator — asserted); **H_C is a sign test and the bias leans
conservative**; **no per-arm E(oi) magnitude claim is licensed.** → FINDINGS 64.6

**93.9 TWO WRONG ASSERTIONS IN THIS TICK'S HARNESS, CODE RIGHT IN BOTH.** (i) The recovery test
demanded a planted `out` effect leave `oi` flat — but **`oi` REFINES `out` and `in`**, so it
captures by construction whatever they capture. The corrected, lattice-aware form is **strictly
stronger**: it tests `out`-vs-`in` discriminability, which is the H_A axis. (ii) Null calibration
ran on a **558-coordinate toy stack** where the null is unresolvable (±1 to ±16 pp). Moved to
110k, where it calibrates to ≤0.04 pp. **Both are wrong assertions about the statistic's domain,
not wrong code** — the campaign's recurring failure mode (92.10, 91.3). → FINDINGS 64.7

**93.10 STATED AGAINST OUR OWN INTEREST.** The primary hypothesis is a **null in its registered
form**. The result that separates is **post-hoc**, **n=3 at the architecture level**, and **at 20
epochs only**. And **nothing in this tick measures accuracy**: `E` is a property of the
meta-gradient field, and **no claim is made that capturing more of it improves training.** That
link is untested and remains the largest unclosed gap in direction C.

**93.11 SCOPE, UNCHANGED AND NOT OPTIONAL.** 3x3 conv tensors only; `E[3x3conv, terminal]` per
STANDING RULE (12). We measure `z`, the META-gradient; Adam-mini / Adalayer / SGG argue about `G`.
**No document may write "we refuted Adam-mini."**

**93.12 ORPHANS.** CSV unchanged at 1707, so the orphan set is unchanged from 92.12: **109
families, 2 orphan, 12 runs** (`gate0b`, `gate0d`), both retired in FINDINGS 61.8 and **not to be
re-run**. This tick cites `fz3`, `ff5`, `p5`, `cl5`, `ml5`, `bo6` — all already-cited families.
**None retired, none created.**

**93.13 IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous twenty-one.

**93.14 NEXT TICK, IN ORDER.** (a) reachability, then `squeue` **both** accounts before anything.
(a2) **rsync `docs/` — SIX cycles behind.** (b) Submit `sp8` (alice2, 9), then `hz9` (9, alice).
(c) Then `cp9` (8, alice) after applying `patches/patch_probe6_coord.py` on the cluster; guard 2
refuses without it. **64.3/64.4 raise `cp9`'s value again**: it resolves the input-channel
direction at coordinate level, and that is now the axis measured to dominate the literature's
choice on 7 of 9 free-β arms. (d) Score `hz9` H0 → H0.3 → H0.5 → H1 → H1b → H2; H0.5 can only
VOID. (e) If bo7/bd7 landed, cycle 54's order stands with 55.2's per-seed sd. (f) **DONE, do not
re-run:** 59.3, 59.8, 60.2–60.7, the tensor-mean avenue for 89.7, the filter hypothesis
(62.5/62.9), C62-C (63.1), the span reconciliation (63.2–63.4), C62-A (63.7–63.8), **and now
C64 in full (64.2–64.4)**. (g) **The offline queue is again down to the carried-since-51 `s`
re-derivation.** Two SUBMISSIONS are now queued behind the four written batches: 63.9's
fixed-architecture budget ladder, and **C64-B — the frozen/free flip at a SECOND budget**, which
is what turns 64.4 from a 20-epoch statement into a general one (n=3 at architecture level is the
binding weakness, not the p-value). (h) The 12 truncated `rs-blk6`/`rs-node` reruns remain last.

---

# CORRECTIONS 94 — cycle 65 decision record

**94.0 OUTAGE, TENTH CONSECUTIVE TICK, LOCALISED NOT ASSUMED.** Gateway `p-cfer-016105` is **up
and answering**; from it `nc -z 132.229.104.230 22` and `.231` both read **DOWN**; `ssh alice` /
`ssh alice2` fail at **banner exchange**. Checked **2026-08-23T13:27Z**. **No queue read, nothing
synced, nothing submitted, nothing cancelled. CSV unchanged at 1707.** `bo7-*` (12, alice) /
`bd7-*` (12, alice2) survival still UNKNOWN and still not guessed. `sp8` (9), `hz9` (9), `cp9`
(8), `rw9` (18) remain written, validated, UNSUBMITTED. `docs/` is now **SEVEN** cycles behind on
the cluster.

**94.1 THE TICK'S DECISION.** The offline queue held only the carried-since-51 `s` re-derivation
(bookkeeping). Instead I took the item **this campaign had itself flagged as the biggest hole**:
93.10, written against our own interest — *"`E` is a property of the meta-gradient field. No claim
is made that capturing more of it improves training. That link is untested and is the largest
unclosed gap in direction C."* It is testable **offline at zero GPU cost** on data already spent,
and it is the sentence the entire Adam-mini / Adalayer / SGG line rests on. Now measured.
→ FINDINGS 65

**94.2 THE RESULT: THE BRIDGE SENTENCE FAILS BY 5 ORDERS OF MAGNITUDE.** Put both ladders on one
axis (`u` = block size in output-channel-row units, c62's own definition; **S1 reproduces the map
against c63's recorded `bsz` on every rung**, 0/289 mismatches). The meta-gradient field peaks at
**u* ≈ 0.0017 (1–9 coordinates, the kernel scale), 17/17 clean arms**. Training peaks at
**layerwise, u ≈ 440, in 16 of 21 budget-matched cells**. **K1 (coincidence) 0/21. K2 (separation
≥2 decades) 20/21, median log10 = 5.41 ≈ 2.6×10⁵×.** At 100 epochs, K2 19/19. **Direction C is
DIAGNOSTIC, not PRESCRIPTIVE — measured, no longer merely cautioned.**

**94.3 A POST-HOC AMENDMENT, DECLARED WITH ITS CONFLICT OF INTEREST ON THE RECORD.** Scoring
revealed that **frozen-β cells have ladders flat to within noise** — necessarily so, since with β
frozen the partition **of β** is a no-op by construction. An argmax over a flat ladder is a coin
flip, and exactly one such flip (r10/frozen → weightwise, sep −0.67) was the registered scoring's
**only** K2 miss. I added a **peak-resolved gate** marking such cells UNSCORABLE (not reassigning
them): amended K2 **14/14**, K1 **0/14**. **The amendment removes this tick's only
counter-example**, so BOTH columns are reported and the amended one **never replaces** the
registered 20/21. Per 76(1)/79 the registered number remains the headline.

**94.4 K2 SURVIVES PEAK-LOCATION UNCERTAINTY, SO L4's CENSORING CANNOT REACH IT.** The corpus
samples only 5 granularities, so the true optimum could sit anywhere between nodewise and
layerwise. **The minimum separation over all resolved cells is 2.77** — placing the optimum at the
finest granularity that ever wins still fires K2. The conclusion does not depend on where in
[nodewise, layerwise] the optimum actually is, nor on layerwise being censored at the ladder top.

**94.5 K3 DOES NOT FIRE, AND THE CLAIM IS BOUNDED ACCORDINGLY.** At the two strictly-interior
(nodewise) accuracy peaks `E` **is** resolved above zero (0/2). **No document may write that the
training-best partition captures no field structure.** The licensed sentence is **mislocation**:
it captures far less than the kernel scale does. Where the accuracy peak is layerwise-or-coarser,
E = 0 is an **IDENTITY** of the null subtraction (65.1) and carries no information at all — which
is why K3 was registered as scorable ONLY on interior peaks, before the data were seen.

**94.6 THE POSITIVE CONTROL PASSES AND IS WORTH MORE THAN THE HYPOTHESIS IT GUARDS.** Frozen-β
granularity span **0.078 pp median (max 0.283)** against free-β **5.662 pp median (max 12.448)**.
Where granularity provably cannot act we measure ~0.08 pp; where it can, ~5.7 pp. This validates
the whole granularity accuracy corpus as a real measurement, not just this tick's use of it.

**94.7 A LIMIT THAT IS FORCED, AND IT SHARPENS RATHER THAN SOFTENS.** The per-coordinate field is
observable **only under weightwise training** — coarse probes store per-GROUP counts (`lay` n_tot
62, `node` 14,600, `blk6` 6) against weightwise 11,220,132. So every `E` in cycles 62–65 is
measured in the weightwise arm, and **weightwise is the WORST resolved granularity in every free
cell** (68.50 vs 74.52 layerwise on r18; 26.89 vs 38.17 on c100). The field is only observable in
the arm that trains worst. The comparison assumes the field's SHAPE is not created by the training
granularity; **that assumption is untested and untestable with recorded data**, and it is now the
largest caveat in direction C — 93.10's slot, refilled with a smaller and better-specified gap.

**94.8 WHAT THIS DOES TO THE PAPER'S SPINE.** Direction C's headline (53.1% sign agreement; the
sqrt(N) refutation) is **untouched** — it is a statement about a field and remains one. What is
now **forbidden** is the bridge: no document may write *"the field has structure at scale X,
therefore partition at scale X"*, or any sentence implying finer capture improves training. 91.7's
prescriptive sentence and 64's Pareto result are statements about **what a partition represents**,
and 65 shows that does **not** transfer to training outcome. **STANDING RULE (13): every
E-derived claim is a claim about the meta-gradient field ONLY; the accuracy link is measured and
is negative at 5 orders of magnitude.**

**94.9 ORPHANS.** CSV unchanged at 1707, so the orphan set is unchanged from 93.12: **109
families, 2 orphan, 12 runs** (`gate0b`, `gate0d`), both retired in FINDINGS 61.8 and **not to be
re-run**. This tick cites `fz3`, `ff5`, `p5`, `cl5` (E side) and the granularity accuracy corpus
(CSV side) — all already-cited families. **None retired, none created.**

**94.10 IDEAS 1 AND 2 STAY DEAD.** Zero jobs, this cycle and the previous twenty-two.

**94.11 NEXT TICK, IN ORDER.** (a) reachability, then `squeue` **both** accounts before anything.
(a2) **rsync `docs/` — SEVEN cycles behind.** (b) Submit `sp8` (alice2, 9), then `hz9` (9, alice),
then `cp9` (8, alice) after applying `patches/patch_probe6_coord.py`. (c) **65 raises `cp9`'s
value again and changes what it is FOR:** it resolves the input-channel direction at coordinate
level, which 65 now shows is a **field** question, not a training recommendation — score it that
way. (d) **The one experiment 65 makes newly worth running, and it is cheap:** a probe that
records the per-coordinate field under **layerwise or nodewise** training (currently impossible —
94.7). That is the only way to test whether the kernel-scale peak is an artifact of weightwise
training, and it is now the binding uncertainty in direction C. It needs a probe-side change, not
a new sweep. (e) **DONE, do not re-run:** everything in 93.14(f), **and now C65 in full
(65.2–65.6)**. (f) The offline queue is again down to the `s` re-derivation.

**94.12 THE INSTRUMENT FOR 94.11(d) IS WRITTEN, TESTED AND READY TO APPLY (same tick).**
`patches/patch_probe7_field_any_granularity.py`. The limit in 94.7 is an INSTRUMENT limit, not a
property of the science, and it is removable: `HF.block_product(u, v)` reduces the SAME elementwise
product `u[i]*v[i]` differently per granularity (sum-all / per-block / per-tensor / per-channel /
none), so **the per-coordinate field exists in every granularity and is merely summed away before
anything sees it**. PROBE7 counts signs on the product BEFORE the reduction and writes a sidecar
`coord_neg_counts.npy` (+ `.json`), leaving `probe.jsonl` byte-identical per CORRECTIONS 18.
Training is untouched: read-only accumulation inside the existing `torch.no_grad()` block.

**Verified locally this tick** (no cluster needed): applies to `patches/HF_patched.py`, **compiles**
(`py_compile`), composes with PATCH_PROBE5 **in either order** (the two blocks are independent and
the only diff is insertion order), and is **idempotent** (`ALREADY_PATCHED`). An initial mark-count
assert was WRONG (expected 4, actual 3) and **refused to write** rather than half-patching — the
guard behaved as designed.

**GATE P7, REGISTERED BEFORE ANY DATA:** one **weightwise** run with `PROBE5=1 PROBE7=1` and
`hier=''` must produce `coord_neg_counts.npy` **BITWISE EQUAL** to `neg_counts.npy`. Same
expression, same `range(self.num_layers)` order, and the dtype difference (existing path casts
`.float()` before comparing) is sign-preserving under a widening cast, so exact equality is the
correct bar and a near-miss is a FAILURE to investigate, never to round. **Scope: `hier=''` only** —
`_probe` runs after `_zpool`/`_zmpool`, so in a hier arm the existing `zall` is POST-pool while
PROBE7's product is PRE-pool; `hier` is written into the json so a hier run can never be mistaken
for a gate pass. **Run the gate first; it costs one 20-epoch job.**

**PRE-REGISTERED READING (STANDING RULE 10), so it cannot be chosen after the fact:** score the
c62/c63 u-ladder on a LAYERWISE- and a NODEWISE-trained run against the weightwise corpus
(65.2: u* ~ 0.0017, 17/17 arms). **u* stays at 1/512–1/1024** -> the kernel peak is a property of
the FIELD, 94.7 is discharged, and 65's separation gets STRONGER (field peak ~5 decades from the
training optimum measured IN THE SAME ARM). **u* moves to the training granularity's own scale**
(u~1 nodewise, u~O layerwise) -> the peak is an ARTIFACT of what the optimizer was allowed to
adapt, and 62.9 / 64 / 65.2 must ALL be restated with that condition attached. **Anything else is
written UNDECIDED, not rounded to a verdict.** The second outcome is the expensive one and is
precisely why the test is worth its one job.
