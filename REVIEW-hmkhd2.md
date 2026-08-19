# Adversarial review — "Step-Size Granularity in Online Meta-Gradient Optimisation is an Estimation Problem"

**Reviewer:** hmkhd2 · **Venue frame:** ICML/NeurIPS main track · **Recommendation:** Reject (2/10),
resubmittable after a substantial rewrite and one non-CIFAR dataset.
**Confidence:** 4/5 — I read `paper/DRAFT.md`, `docs/FINDINGS.md` (all 2,927 lines),
`docs/PRIOR-ART.md`, `docs/PAPER-CONFIG.md`, and independently re-aggregated
`results/all_runs.csv` (413 rows) rather than taking the draft's tables on trust.

---

## 0. Summary of the problem

The draft is a careful, honestly-hedged write-up of a campaign whose own lab notebook has moved
**two to four cycles past it**, and in several places has *reversed* the result the draft states.
The single most damaging fact in this review is not a methodological quibble: it is that
`results/all_runs.csv` — sitting in the repository the draft ships from — contains completed,
n=2–3 control experiments that **contradict the draft's §4 headline** and that the draft either
does not cite or describes as "in flight."

I am going to be blunt about that first, because everything else is secondary to it.

---

## 1. Claims not supported by the data

I take each headline claim, name where it appears, and check it against `FINDINGS.md` and my own
re-aggregation of `all_runs.csv`.

### C1 — "granularity … only converts into higher final accuracy when the budget is too short for the coarser arm to catch up" (Abstract L14–17; restated as "One statement covers every cell", §3 L86–89)

**Contradicted by your own 300-epoch control.** `e300-*` at α₀=1e-3, SGDm+Lion, guarded,
complete at 300/300 epochs, n=2:

| arm | plateau @100 ep | plateau @300 ep |
|---|---|---|
| scalar | 87.85 | 88.29 |
| layerwise plain | 91.22 | 91.74 |
| **granularity gap** | **+3.37pp** | **+3.45pp** |

Tripling the budget moves the contrast by **0.08pp**. The scalar arm ends at 95.2–95.5% *train*
accuracy against layerwise's 99.99% — it is not lagging toward the same solution, it converges to a
worse one. `FINDINGS.md` cycle 8 §6 (L2344–2371) states this explicitly and says in terms:
*"That reading now applies to **pooling** (which does decay) and not to **granularity**. The paper
should say so rather than keep the stronger claim."* The draft keeps the stronger claim, verbatim,
in the abstract and as the section-3 punchline, and never cites the 300-epoch control at all.

As written, C1 is not a hedge-away; it is the paper's central explanatory device (it is what
"predicts the parent paper's own ImageNet null", L88–89). It is falsified in the one configuration
where granularity actually does anything. What survives is the *AdamW* half — where every arm fully
fits (FINDINGS cycle 5 §6, L1523–1535) — and that is a per-coordinate-normalisation story (H4),
not a budget story. **You have two mechanisms and are shipping one label for both.**

### C2 — "partially pooling … improves on every fixed granularity we tested, and is insensitive to its own pooling strength across three orders of magnitude" (Abstract L16–19; §4 L97–124)

Four independent problems, any one of which is fatal on its own.

**(a) It does not improve on every fixed granularity.** At m = 11,173,962 the same operator is
catastrophic: 79.38 ± 0.46 → ~49 (FINDINGS L978–1006; my re-aggregation gives shrink λ≥0.01 at
48.9–49.7, n=2 each). At m=6 it *costs* 10.0 epochs of speed at t = 6.5 (FINDINGS cycle 4 §5,
L1089–1101). "Every fixed granularity we tested" is true only if you delete two of the four
granularities you tested. Your own FINDINGS says so at L1104–1110.

**(b) The gain is a 100-epoch budget artefact.** `e3a-*` (α₀=1e-6, 300 epochs, complete, n=2)
against the matched `e3a-lplain` baseline, plateau:

| arm | 100 ep (n=11/12) | 300 ep (n=2) | gain @100 | gain @300 |
|---|---|---|---|---|
| plain layerwise | 90.77 ± 0.18 | 91.80 ± 0.16 | — | — |
| **shrink λ=0.1** | 92.29 ± 0.08 | 91.88 ± 0.10 | **+1.51pp** | **+0.09pp** |
| additive r=0.05 | 93.09 ± 0.10 | 93.01 ± 0.09 | +2.31pp | +1.21pp |

**The operator the entire §4 is built on loses 94% of its effect at 3× budget and lands inside
seed noise.** The operator that survives — M1 additive — is not in the draft at all. This is
already on disk; I did not have to run anything.

**(c) The insensitivity is operator saturation, not robustness.** `β ← β − λ(β − β̄)` applied every
step has half-life ln2/λ steps against ~50,000 steps per run. λ = 0.001 → 693 steps; λ = 1.0 → 0.
**Every λ in your table is full pooling within the first 1.4% of training.** FINDINGS cycle 6 §3
(L1747–1755) states this and concludes the λ curve "was never a test of" partial pooling. Selling
"a hyperparameter whose value does not matter — in practice it removes a decision rather than
adding one" (L109–111) as "the strongest property of the result" is, once a reviewer reads your
operator definition, an argument that the knob is disconnected. The genuinely partial values you
*did* run (λ = 1e-5, 3e-5, 1e-4, half-lives 69k/23k/6.9k steps) give 91.37, 91.30, 91.03 — i.e.
they land back on **plain** (91.17–91.39). The dial is a step function, and the draft advertises
the flat part as evidence of a robust method.

**(d) The definitive version of this experiment has landed and it goes the other way.** §6 (L143–150)
describes the `zpool` sweep as "⏳ in flight." It is not. `results/all_runs.csv` contains it
complete at n=3 on L4 (`zsw-*`, 100/100 epochs), and it is the *only* pooling operator you have
with exact endpoints (r=0 ≡ scalar, r=1 ≡ plain per-group, both verified by the `z3` gate at
0.07–0.13pp, FINDINGS L2712–2737). Best test accuracy:

| r | layerwise (m=62) | weightwise (m=11.17M) |
|---|---|---|
| 0 (≡ scalar) | 88.14 ± 0.06 | 88.07 ± 0.04 |
| 0.1 | 90.01 ± 0.21 | 88.14 ± 0.13 |
| 0.3 | 90.07 ± 0.23 | 88.26 ± 0.18 |
| 0.5 | 89.63 ± 0.13 | 88.28 ± 0.10 |
| 0.7 | 89.55 ± 0.14 | **88.43 ± 0.10** |
| **1 (≡ plain per-group)** | **91.35 ± 0.16** | 79.35 ± 0.37 |

**At m=62, every interior r is strictly worse than no pooling at all** — the maximum interior value
(90.07) is 1.28pp *below* the unpooled endpoint, at ~6σ. Partial pooling in the correctly
parameterised space, at the granularity the paper's proposal is about, **hurts**. The only place
it wins is m=n, where r=0.7 beats scalar by +0.36pp (~3σ) and beats plain weightwise by +9.1pp —
a real but small result that is 5pp below the campaign's best arm and that the draft does not
report.

C2 is not "not yet confirmed." It is **measured, at n=3, in the opposite direction**, by the
experiment the draft nominates as decisive.

### C3 — the granularity speed table, §3 L66–71 ("monotone in granularity at every threshold ≥85%", "19% sooner")

**Wrong runs.** Those numbers are the `g2_mAdam_*` block, which is **unguarded** (`beta_clip=none`
in the CSV). §5 of the same draft (L137–138) makes the SwiftTD guard standard and calls it "a no-op
for coarser granularities." You cannot present the guard as standard in §5 and quote pre-guard
numbers as the headline in §3 without saying so. The guarded n=3 replacement exists (`a0-*`,
α₀=1e-6, all 27 runs at 100 epochs):

| arm | ep→85 | ep→88 | ep→90 | best |
|---|---|---|---|---|
| scalar | 10.7 ± 1.2 | 19.0 ± 3.0 | 32.3 ± 2.5 | 92.09 ± 0.06 |
| 6-block | 10.3 ± 0.6 | 16.0 ± 1.0 | 30.7 ± 2.1 | 92.03 ± 0.18 |
| layerwise | 10.0 ± 0.0 | 15.0 ± 1.0 | 27.0 ± 1.0 | 91.98 ± 0.12 |

On the guarded data the 19% becomes **16%**, and — more importantly — **the ep→85 ordering is not
resolvable**: 10.7 ± 1.2 vs 10.0 ± 0.0 is a 0.7-epoch gap at n=3. "Monotone in granularity at
every threshold ≥85%" survives as an ordering of means and dies as a claim with error bars at the
lowest threshold. The draft prints no error bars on this table at all.

Two further defects in the same section: the "final acc" column of the **SGDm** table (L82–84:
88.09 / 91.56 / 91.34) is not final accuracy, it is *best* accuracy — the true final values are
87.95 / 91.40 / 91.06 — while the AdamW table's "final acc" column *is* final. Two different
metrics under one column header, two tables apart. And the SGDm table is also unguarded.

### C4 — "granularity … rescues seeds on which a single shared step size diverges" (§3.1 L91–95, marked ✅)

**This is the claim your own notebook told you not to write.** FINDINGS L236–242 carries a boxed
warning: *"CONFOUND FLAGGED … Do not put the stability claim in a draft until that control
reports."* The control reported, and FINDINGS L1008–1023 corrects it:

| SGDm + Adam, scalar, α₀=1e-6 | s0 | s1 | s2 | collapsed |
|---|---|---|---|---|
| g3, guard **OFF** (what the draft quotes) | 88.45 | **18.47** | **20.71** | 2/3 |
| g4, guard **ON** | 88.12 | **20.89** | 86.78 | **1/3** |
| g4, SGDm + **Lion**, guard on | 88.00 | 88.05 | 88.46 | **0/3** |

The draft quotes the guard-off row (18.47, 20.71, 88.45) verbatim, with a ✅, with no mention of
the guard and no mention that under the *other* meta-optimizer the effect is 0/3. Beyond the
provenance problem: a 2-of-3 vs 0-of-3 contrast is a **binomial comparison with n=3**. The 95% CI
on 2/3 is roughly [0.09, 0.99]. There is no seed count in this campaign at which "2 of 3 seeds
collapsed" is a publishable stability claim, and FINDINGS L1025–1039 says as much ("state it on
the primary metric, not on collapse counts").

### C5 — "the meta-gradient going non-finite … a float32 overflow of an undecayed trace (`γ = 1` leaves `h ← h − Δw` an unbounded running sum)" (§5 L128–132)

**Refuted, by your own direct control, and the draft prints it as fact.** FINDINGS L167–178:
*"'γ = 1 leaves the trace undecayed, so it accumulates until it overflows.' **False**, and tested
directly: γ = 0.999 gives the trace a ~693-step half-life and **fails identically** (72.30 vs 72.08
peak; both → 10.00). A geometric blow-up at ×1.9/step is not something a 0.999 decay factor can
restrain."* The measured mechanism is a per-coordinate positive-feedback loop, not accumulation.
This is the single most embarrassing line in the draft: a reviewer who reads only the draft would
accept it; a reviewer who reads your appendix would find you ran the refuting experiment and then
wrote the refuted hypothesis into the paper anyway.

### C6 — "~12pp gap is the genuine granularity effect and is not a numerics story" (§5 L140–141)

Weakly supported and probably wrong in shape. Three things cut against it:

- The guarded ladder is **non-monotone with its peak above layerwise**: scalar 88.08 (n=5),
  6-block 91.69 (n=5), layerwise 91.17–91.39 (n=11), **nodewise ≈4,800 groups: 91.89 ± 0.21 (n=4)**,
  weightwise 79.38 (n=3). There is no "finer is worse" trend to attribute a granularity effect to
  — there is a plateau from m=6 to m≈4,800 and one cliff at m=n (FINDINGS cycle 8 §8, L2440–2461).
- The `zpool` weightwise column above closes ~9 of those 12 points with mild pooling
  (79.35 → 88.43 at r=0.7). Whatever the m=n deficit is, it is not irreducible.
- FINDINGS cycle 8 §4 (L2293–2318) shows most of the short-horizon fine-granularity catastrophe is
  an α₀ startup transient.

### C7 — the three implementation defects (§2 L42–59)

**These I believe, and they are the most solid thing in the paper.** The dead-granularity defect is
verified in two independent task copies (`tinystories/HF.py` as well, FINDINGS L558–566), and the
`layerwise == blockwise[1,…,1]` / `scalar == blockwise[62]` identities at max |diff| 7.5e-9 are the
right way to establish it. Keep this. It is not, on its own, an ICML paper.

---

## 2. The biggest reviewer objection

Blunt version, and it is two things fused:

> **You wrote a paper explaining an ImageNet result using only CIFAR-10/ResNet-18, and the
> mechanism you propose to explain it is contradicted by your own budget control.**

The paper's entire framing (Abstract L12–15, §3 L86–89) is: the parent paper's ImageNet null is a
*budget* phenomenon, not a *scale* phenomenon. To argue "not scale," you must vary scale. You vary
nothing: every number in the draft is CIFAR-10 / ResNet-18 (§7 L153, FINDINGS repeats it as a
standing caveat in all ten cycles). The three `sm-ResNet{34,50,101}` probes ran 2 epochs at chance
(FINDINGS L1597–1599). ImageNet is scoped out on a data-availability problem — 489/1000 classes and
a missing devkit — which is a perfectly good operational reason and a completely inadequate
*scientific* one. A reviewer's summary sentence writes itself: *"the paper's central claim is that
a scale-indexed discrepancy is not about scale; the paper contains one scale point."*

And then, at the one place you *did* vary budget (3×, `e300`), granularity did not narrow by 0.08pp.
So the budget mechanism you offer for the ImageNet null is the one thing your budget experiment
falsifies.

**Second-order but equally lethal on inspection:** the paper has **no non-MetaOptimize baseline
anywhere in 413 runs**. There is no tuned constant LR, no cosine/step schedule, no plain
SGD+momentum reference. ResNet-18 on augmented CIFAR-10 with a standard recipe is a ~94–95% task;
your best arm is 93.5. A reviewer will ask why they should adopt an online meta-gradient step-size
method that lands 1.5–2pp below the recipe everyone already uses, and the draft has no answer on
file. The parent paper at least reports MetaOptimize > fixed-step-size baselines
(`PAPER-CONFIG.md` L27–29); this paper drops that comparison entirely.

**Third, and this is the one that would get the paper torn apart rather than merely rejected:** a
referee who diffs `paper/DRAFT.md` against `results/all_runs.csv` finds §4's headline refuted by
two completed controls in the same repository, one of which the draft calls "in flight." That reads
as selective reporting even though I am confident (from the tone and discipline of FINDINGS) that
it is staleness. Fix it before anyone else finds it.

---

## 3. Statistical problems

**3.1 The λ sweep is a 7-way maximum reported at n=3, and you have direct evidence this fails.**
§4 L106 reports λ=0.01 at **+1.46pp** as the headline. The full ladder is 92.50, 92.51, 92.53,
92.54, 92.58, 92.79 across λ ∈ {0.5, 0.3, 1.0, 0.001, 0.03, 0.01} with sds of 0.08–0.23. The
observed spread (0.29pp) is comparable to the within-cell sd; the maximum of 7 correlated cells at
n=3 is upward-biased by roughly 1–1.5 sd under any reasonable model. Your own FINDINGS cycle 7 §4
(L2122–2124) reaches the same conclusion for the plateau version of this table: *"§4's λ=0.01 peak
is +0.27pp over λ=1.0 at n=3 — not resolvable. Only the train-accuracy and gap columns are being
claimed."* The draft claims the accuracy column anyway.

You also have a **measured** instance of this failure mode on an adjacent ladder: cycle 9 §1
(L2510–2535) records two n=2 peak cells on the additive ladder falling by 0.05 and 0.16pp and
*reversing their ranking* on promotion to n=5. Any reported optimum at n=3 on this apparatus is
untrustworthy by your own precedent. **The defensible statement is "any λ ≥ 0.001 gives
+1.2–1.5pp at 100 epochs," with no interior optimum claimed** — and per §1(b) above, even that
statement needs the 300-epoch caveat attached.

**3.2 "Best test accuracy over 100 epochs" is the wrong estimator and it is not the one you use
elsewhere.** `best_test` is the maximum of ~100 serially-correlated noisy evaluations. Across the
348 completed guarded runs in `all_runs.csv`, `best_test − plateau` has a median of **0.36pp**.
That inflation is *the same size as effects the draft reports as findings* (+0.47pp for 6-block
pooling, §4 L111), and it is larger for noisier arms, so it systematically flatters whichever arm
has the shakier curve. `analysis/aggregate.py` already emits `plateau` (mean of the last 20
epochs) precisely for this reason (FINDINGS L1537–1548). **Report plateau. Report best only as a
secondary column, and never difference two arms on it.**

**3.3 Epochs-to-threshold is quoted at thresholds drawn through the losing arm's asymptote.** §4's
mechanism table (L116–121) quotes ep→90, ep→91 and ep→92 for plain layerwise, whose plateau is
90.77 and which spends **51 ± 3 of 100 epochs inside [89, 91]** (FINDINGS L1216). Your own cycle-4
second pass (L1186–1325) established that ep→90 on that arm "is not measuring convergence speed at
all; it is measuring when noise first nudged an already-converged curve over a line drawn through
it," and gotcha 18 forbids quoting it for that arm at any seed count. The draft's "92%: never
(0/6)" row is a plateau statement dressed as a speed statement. Two runs of the same config and
seed differing only in cuDNN non-determinism gave ep→90 of 57 and 51 on this arm (FINDINGS
L1198–1207) — **a 6-epoch jitter at fixed seed.**

**3.4 The reproducibility floor is quoted for the wrong quantity.** §7 L159–161 says runs reproduce
to ±0.02pp and "all effects reported here are ≥1pp." That defends the *accuracy* claims. It does
not defend §3, whose headline effect is **5.7 epochs**, against a same-seed epoch jitter your own
data puts at ~6 epochs on flat-curve arms. FINDINGS cycle 4 §6 rule 4 (L1323–1325) says exactly
this: *"The ±0.02pp determinism floor does not transfer to epochs-to-target."* The limitations
section as written gives a false sense of resolution on the paper's own primary metric.

**3.5 Multiplicity across the whole campaign is unaccounted for.** 413 runs, ~10 analysis cycles,
metric definition changed at least three times (final → best → ep→90 → ep→85/88 → plateau), and
the primary metric was re-selected *after* seeing that ep→90 flattered the proposal (FINDINGS
L1269–1279 is an admirably honest account of this). Nothing in the draft discloses that the primary
metric was chosen post hoc. It must, or a reviewer who reads the appendix will call it garden of
forking paths — correctly.

**3.6 Seed counts are heterogeneous and undisclosed in the draft.** §4 compares a shrink cell at
n=3 against a plain baseline at n=6 (L102–106) — and the plain baseline is itself pooled across two
submission blocks that FINDINGS L1074–1087 showed differ by 3.6 epochs on ep→90. §3's tables carry
no n and no error bars at all. Every table in a submission needs n, sd, and the test.

**3.7 No statistical test is reported anywhere in the draft.** FINDINGS computes Welch t's
throughout; none survive into the paper. Given n=3 and 2–7 arms per comparison, you need at
minimum: n, sd, the test, and either a correction or an explicit statement that the comparisons are
exploratory.

---

## 4. The novelty question

`PRIOR-ART.md` is the most intellectually honest document in the repository and it has already
decided this: *"'Per-weight fails, per-layer works' is **not publishable** — it rediscovers
1992/2012/2024"* (L75–77). I agree, and I would go further than the draft does. §5 is currently
written as a rediscovery *plus* a residual, but the "residual" (C6 above) is exactly the part your
own guarded ladder shows to be non-monotone with its peak at nodewise.

Strike from the ledger, then, what actually remains:

| candidate contribution | verdict |
|---|---|
| per-weight collapse + guard | rediscovery (IDBD '92, Autostep '12, SwiftTD '24). Report in one paragraph. |
| granularity buys speed | real, but unguarded in the draft, within noise at ep→85 under the guard, single dataset |
| granularity stabilises | superseded (2/3 → 1/3 with guard, 0/3 under Lion), n=3 binomial |
| budget/unifying explanation of §7.3 | falsified for SGDm by your own `e300` |
| M0 shrink pooling (§4) | +1.51pp @100 ep → **+0.09pp @300 ep**; refuted at m=62 by `zpool` |
| implementation defect report | solid, and genuinely useful — but a workshop/technical note |

What is left that I have not seen elsewhere and that your data actually supports:

1. **The base-optimizer × granularity interaction (H4), stated as a measurement.** Under AdamW
   every arm reaches 99.6–99.9% train and granularity is null; under SGDm the scalar arm reaches
   94% and granularity is +3.4pp and **budget-invariant to 3×** (FINDINGS L1523–1535, cycle 8 §6).
   "Learned per-block step sizes substitute for per-coordinate normalisation, and only for it" is a
   clean, falsifiable, novel-enough claim, and it explains the parent paper's §7.3 better than the
   budget story does.
2. **The sign-agreement measurement.** 53.1% of 11.17M per-coordinate meta-gradients agree on sign,
   against 50.0000 ± 0.0015% under independence, and the measured drift-vs-N slope is −0.113 against
   a predicted −0.500 (FINDINGS cycle 7 §1, L1908–1944). This *refutes the i.i.d./1/√N variance
   model that the whole "estimation problem" title presupposes*, and it is the kind of measurement
   PRIOR-ART L44–48 identifies as the empirical core (measuring the within-block noise correlation
   `c`). It is not in the draft. **It should be the paper.**
3. **The aggregation-order effect, which nobody in this campaign has yet named.** Two operators that
   both leave the base optimizer with **exactly one step size** differ by 4.4pp: `shrink λ=1.0` on
   layerwise gives 92.53 ± 0.17, `zpool r=0` on layerwise gives 88.14 ± 0.06 (≡ scalar, identity-
   verified). The only difference is `meanᵦ sign(z_b)` versus `sign(Σᵦ z_b)`. That is a large,
   reproducible, mechanism-bearing fact about how a meta-optimizer's nonlinearity interacts with the
   reduction — and it says the effect you have been calling "granularity" is substantially an
   **aggregation-rule** effect, not a step-size-count effect. FINDINGS cycle 6 §1 (L1612–1666)
   half-noticed this; the `zpool` endpoint makes it a controlled contrast.
4. **M1 additive at r ≈ 0.05–0.07.** 93.46 ± 0.05 (n=5) / 93.48 ± 0.16 (n=5) against plain 91.21,
   with *better* train fit (99.6 vs 99.7), an interior optimum, generalisation to 6-block (+0.49)
   and to Adam meta (+0.95), and — unlike shrink — **survival at 300 epochs (+1.21pp)**. This is
   your best method and it is absent from the draft.

**Minimum additional evidence for this to be a paper**, in priority order:

- **(i) One non-CIFAR-10 result.** CIFAR-100 or ImageNet-64×64 or TinyStories — anything that
  breaks the single-scale-point objection. Non-negotiable for a main-track submission.
- **(ii) At least two architectures.** ResNet-18 → ResNet-50 and/or a small transformer. Your
  2-epoch smokes do not count.
- **(iii) A fixed-LR and a scheduled-LR baseline** on every headline table.
- **(iv) The mechanism measured, not inferred:** sign-correlation / within-block noise correlation
  `c` as a function of block size, with the SNR ∝ √(B/(1+c(B−1))) form from PRIOR-ART L46–48 fitted
  to it. This is what turns a table of outcomes into an explanation.
- **(v) Fair-tuning protocol.** Your very first "Open confound" (FINDINGS L35–38) — that comparing
  granularities at a fixed `meta_stepsize` may be unfair to finer arms — has **never been
  addressed** across ten cycles. You tuned α₀ per arm; you never tuned η per arm. A reviewer will
  raise it, and you already wrote it down yourself in cycle 1.
- **(vi) n ≥ 5 on every cell that carries a number in the paper**, with plateau as the metric.

---

## 5. Missing experiments a reviewer will demand

1. **Any dataset other than CIFAR-10.** (§1 above.) The ImageNet blocker is a devkit for
   `val` labels — that is a downloadable file, not a scientific obstacle; and ImageNet-64×64,
   CIFAR-100, and TinyImageNet are all unblocked and unstarted.
2. **Any architecture other than ResNet-18.** The paper generalises about "the correct step-size
   scale is constant within a tensor" (§8, citing μP) on one architecture family.
3. **A non-meta baseline.** Tuned constant LR; cosine schedule; SGD+momentum reference. Without it
   there is no way to know whether *any* of these arms is worth running.
4. **Per-arm tuning of the meta-step-size η at equal search budget.** You tuned α₀ (3 values × 3
   seeds × 3 arms) and found the ordering flips under AdamW (FINDINGS cycle 3 §1b, L800–808).
   η is untouched at 1e-3, the paper's default, for all 413 runs. The identical fairness argument
   applies and you have already measured that it bites.
5. **A wall-clock/memory cost accounting.** m = 11.17M step sizes doubles optimizer state. There is
   a `wallclock_min` column in the CSV and not one sentence of cost analysis in the draft. Any
   granularity paper must show the Pareto frontier, not just the accuracy column.
6. **The additive-vs-shrink ablation as a controlled comparison**, since you now know they differ in
   mechanism (shrink moves drift *and* spread; additive moves spread only, mean-preserving by
   construction — FINDINGS L1975–1998).
7. **Adalayer / Adam-mini / SOAP comparison.** PRIOR-ART L131–140 names these as the objections to
   answer; the draft's §8 promises to "address rather than dodge" them and then does not run a
   single comparison.
8. **The `zpool` sweep at the granularities in between** (6-block, nodewise). You have the operator,
   the endpoints are exact, and it is the only clean interpolation you own.
9. **Seed-2+ on `zsx`/`zsw` weightwise** and a resolution of the L4-vs-2080ti split (gotcha 28):
   half your zpool sweep is on a different GPU type from the other half.
10. **γ ablation.** The parent paper sanctions γ ≥ 0.999 (`PAPER-CONFIG.md` L35–36); you run γ=1
    everywhere and tested γ=0.999 exactly once, on a failure case.

---

## 6. Overclaimed, badly hedged, or embarrassing

- **L3–4, the ✅/⏳/⚠️ convention.** Shipping the lab-notebook confidence markers *inside the paper
  draft* is a mistake. Reviewers do not read "✅" as "confirmed"; they read it as "the authors have
  a private taxonomy of how much they believe their own results." Worse, three claims marked ✅ are
  the ones I flagged in §1 as superseded (§3, §3.1, §4). Resolve the markers before circulating.
- **§5 L128–132** — printing a hypothesis your own γ=0.999 control refuted. Fix first.
- **§3.1** — quoting the guard-off stability numbers with a ✅ after your notebook wrote
  "**Do not put the stability claim in a draft until that control reports**" in bold. This is the
  one that would look worst if a reviewer had access to the repo.
- **§6 L143–150** — describing as "in flight" a 36-cell sweep that is complete at n=3 on the L4 arm
  and refutes the claim in §4. Update or remove.
- **§4 L109–111** — "a hyperparameter whose value does not matter … removes a decision rather than
  adding one." This is the draft's most quotable sentence and it is an artefact of an operator that
  saturates at 1.4% of the run. A referee who reads `_apply_hier` will make it the centrepiece of
  their review.
- **§4 L123–124** — "reaches a level plain layerwise never reaches within the budget." True at 100
  epochs; at 300 epochs plain reaches 91.80 and shrink reaches 91.88. "Never" is doing work that
  the data does not support and that you have the control to disprove.
- **§7 L162–164** — "A control at α₀ ∈ {1e-4, 1e-3} is running." It completed two cycles ago, twice,
  on two meta-optimizers, and closed the confound (every arm flat to ≤0.38pp / ≤0.58pp across three
  decades; FINDINGS cycle 8 §3 L2277–2291 and cycle 10 §6 L2885–2901). Stale limitations sections
  signal to a reviewer that the rest of the draft may also be stale — and here, it is.
- **§7 L153–157** — "CIFAR-100 and an explicit budget sweep replace [ImageNet] as the scale axis."
  The budget sweep is not a scale axis; it is a budget axis, and it is the axis on which your
  unifying claim fails. CIFAR-100 has not been run. Do not promise a substitute you have not
  executed and that would not substitute.
- **§8 L175–177** — naming SOAP and Adalayer as "counterweights we must address rather than dodge"
  and then not addressing them *is* the dodge. Either run the comparison or state plainly that it
  is out of scope.
- **Title.** "…is an Estimation Problem" presupposes the variance/estimator framing that your own
  cycle-7 drift measurement refuted (slope −0.113 vs −0.500 predicted; 53.1% sign agreement vs
  50.0000% under independence). Either measure the correlated-noise version of the estimator story
  and earn the title, or change the title.
- **Missing entirely:** M1 additive — your best result (93.46–93.58, n=5, interior optimum,
  generalises across granularity *and* meta-optimizer, survives 3× budget). It is a strange draft
  that omits the campaign's strongest arm while leading with the arm that dies under a budget
  control.

---

## 7. What I would actually do with this

The honest paper in this repository is not the one in `paper/DRAFT.md`. It is:

> **Learned step-size granularity substitutes for per-coordinate normalisation, and the benefit is
> an aggregation effect rather than a step-size-count effect.** Under SGDm it is worth +3.4pp and
> is invariant to a 3× budget; under AdamW it is worth nothing, because every arm already fits.
> Two operators that leave the base optimizer with a single step size differ by 4.4pp depending on
> whether the meta-gradient is reduced before or after the meta-optimizer's nonlinearity. The
> per-coordinate meta-gradient signs are strongly correlated (53.1% agreement across 11.17M
> coordinates), which refutes the i.i.d. variance model this literature implicitly assumes. And the
> released implementation cannot execute the granularities its own paper names as future work.

That is a defensible NeurIPS-workshop paper today and a main-track paper with one non-CIFAR dataset
and the correlation measurement fitted. The current draft is neither, because its two headline
sections are contradicted by controls that are already sitting in `results/all_runs.csv`.

**Recommendation: Reject.** Rewrite around the surviving claims, run one more dataset, and delete
§4 as written.
