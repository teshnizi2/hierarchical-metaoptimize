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
