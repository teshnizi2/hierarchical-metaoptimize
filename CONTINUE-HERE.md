# Continue here — self-contained handoff

Any fresh session (primary account, `claude2`, or a scheduled task) can resume from this file.
Nothing below depends on prior conversation context.

## Access
* `ssh alice`  — user `salehkaleybars`, workspace `/data1/salehkaleybars/metaopt` (5 TB scratch)
* `ssh alice2` — user `s5014158` (Reza's own), workspace `~/metaopt` (2 TB home)
* Both are passwordless key auth from this Mac. Slurm scheduler. Compute is free and uncapped;
  per-user concurrency caps are 2x A100 / 8x L4 / 12x 2080ti, so **use both accounts**.
* This repo is mirrored at `/data1/salehkaleybars/metaopt/hierarchical-metaoptimize`.

## Read these first, in order
1. `docs/FINDINGS.md`   — every measured result, with confirmed/pending status
2. `paper/DRAFT.md`     — the write-up; rows tagged ✅ confirmed / ⏳ in flight / ⚠️ untrustworthy
3. `docs/OPERATIONS.md` — the gotchas below, in full
4. `docs/PAPER-CONFIG.md` — the parent paper's exact config, extracted from its PDF
5. `docs/PRIOR-ART.md`  — what is novel vs a rediscovery (read before claiming anything)

## The state of the science, in one paragraph (rewritten cycle 21; see cycle 26 above for the mechanism)
Three results now carry the paper. **(1) The sqrt(N) noise model is refuted with the sign
INVERTED**, in three architectures across two datasets: holding beta common (`HIER=shrink,
LAM=1.0`) and varying only the group size, drift *rises* with group size (log-log slopes
+0.179 / +0.268 / +0.203 where the model requires -0.500), at alpha0=1e-3 and with
weightwise sign-agreement excess of only 0.08-0.47% -- so independence *holds* and the
prediction *still* fails. **(2) The granularity gain tracks TASK DIFFICULTY, not parameter
count.** On CIFAR-10 at alpha0=1e-6 the gain (layerwise - scalar) falls 19.88 -> 2.87 -> 0.90
across ResNet10/18/34, which looks like the parent paper's premise -- but the LAYERWISE arm is
flat (90.220-90.686, a 0.47pp spread) while the SCALAR arm moves 18.58pp; the whole trend is
scalar catching up. CIFAR-100 at the *middle* model size then gives **+47.6pp**, the campaign's
largest effect, and it does not care about alpha0 (+47.59 at 1e-6, +47.64 at 1e-3). `cs-*`
(submitted cycle 21) supplies the missing CIFAR-100 model sizes that turn this from hypothesis
into result. **(3) M1's `r` is NOT a pooling dial (cycle 33; CORRECTIONS 21).** `r=1` is plain layerwise
(verified: 90.863 +-0.063 vs 90.891). `r=0` was believed to be FULL pooling; it is not. Under
Lion every group's realised beta increment has magnitude exactly `ms`, so `additive`'s mean-of-
increments shrinks the shared step to `ms*|2p-1|` -- a 10.3x meta-step-size cut at layerwise.
`additive` r=0 therefore spans 47.58pp across granularities (45.005 weightwise -> 92.587
layerwise) where a true pooling arm must be granularity-invariant; `zpool` r=0 is, to 0.032pp.
**"Even full pooling helps" is REFUTED**: true full pooling is -3.044pp vs plain layerwise.
The M1 interior optimum survives as an EMPIRICAL curve (layerwise +2.359pp n=10, nodewise
+1.140pp n=3, absent at blk6 and weightwise) but has no pooling interpretation. On CIFAR-100
the same r=0.07 costs -43.7pp. **Do not write any "pooling helps" sentence.**
**The correction that bounds all method claims:** a tuned non-meta baseline now WINS. AdamW +
cosine at lr 1e-3 reaches **94.093 +-0.036** under matched budget (100ep, AUGMENT=1, ResNet18,
CIFAR-10) against the best MetaOptimize arm's **93.306 +-0.140** -- a 0.79pp deficit. Earlier
cycles compared against *constant-LR* AdamW (91.86), which MetaOptimize does beat by +1.38pp.
The gap is the schedule, not the optimizer. Results (1)-(3) are statements about
MetaOptimize's internals and are untouched; any "our method is better" sentence is not.


## Running / next (cycle 51) -- **EVERY CLIP FRACTION THIS CAMPAIGN QUOTED WAS AT THE WRONG RESOLUTION**

**Read `docs/CORRECTIONS.md` 62-66 and `docs/FINDINGS.md` 51.1-51.5 before quoting any clip
fraction, any ms=1e-2 number, or the phrase "at the adapted equilibrium". 62 explains why
`wc5` came back uninterpretable. 64 WITHDRAWS CORRECTIONS 61(5)'s "both mechanisms fail".
65 narrows the headline's opening clause.**

* **BOTH QUEUES WERE 0/0 AT TICK START; all 18 `wc5-*` landed. CSV 1629 runs (+18).**
* **THE FINDING OF THE TICK, and it is about the instrument.** `BETA_CLIP` is applied
  **per coordinate**. Every clip fraction the campaign has quoted was read from the probe's
  per-TENSOR `beta[]` list (one MEAN per tensor). At coordinate resolution, from
  `beta_true_max` which was already in the same records: **the HIGH guard binds on 95.4% of
  records at weightwise ms=1e-2, from record 92** -- MORE and EARLIER than the low guard --
  while the per-tensor column reads **0.00%**. `analysis/c51_wideclip.py` (**26/26**) prints
  all three denominators. **STANDING RULE (6): a fraction must be measured at the resolution
  the mechanism operates at.**
* **`wc5` THEREFORE MOVED THE WRONG WALL.** Its header chose to widen only the floor because
  "the HIGH bound provably never binds". **W2 FAILS** (layerwise record-binding 88.0% ->
  71.7%, bar 5%) and **W1 is UNINTERPRETABLE**, per W2's own fallback text. **Scoring W2
  before W1, as the pre-registration ordered, is what saved the tick** -- read in the other
  order, b(1e-2)=0.364 fires W1's REFUTATION branch and this cycle announces a non-monotone
  dial, which would have been wrong.
* **CORRECTIONS 58 IS NOT DISTURBED, and its fourth rung gets a better name.** At ms=1e-2 the
  log-stepsize distribution spreads **ballistically at ~99% of the maximum Lion speed, in both
  directions, and exactly fills whatever box it is given** (12.70-wide box -> span 12.70;
  27.70-wide box -> span 27.70; same velocity to 0.2%). Write **"boundary-dominated"**, not
  "confounded", and never quote it in a b or gain claim.
* **THE HEADLINE GETS ITS FIRST BOX-SENSITIVITY NUMBER AND SURVIVES IT.** N_eff/m (weightwise,
  variance, steady half, R18/ms=1e-3): **0.4808 at LO=-15 -> 0.5189 at LO=-30**, i.e. +0.038
  for a 2.2x deeper box. Plateau is clip-neutral: **+0.027 pp** over 6 matched cells at n=3.
  That +-0.038 sets the +-0.10 bar both new batches pre-register.
* **CORRECTIONS 61(5) IS WITHDRAWN (see 64).** The Q4 rebound's mechanism (i), clip saturation,
  was rejected on the per-tensor column and was **never actually tested**. At coordinate
  resolution the four families separate **perfectly**: rebound YES = r10 / c100, whose Q4
  ceiling occupancy is **100.0% / 100.0%**; rebound no = r18 / r34 at **28.5% / 0.0%**.
  Post-hoc at n=4 and labelled as such -- but (i) is now the LEADING candidate, not a
  refuted one.
* **"AT THE ADAPTED EQUILIBRIUM" IS NARROWED TO THE BULK (65).** With the floor moved out of
  the way the minimum log-stepsize is **still descending at 89-100% of max Lion speed in the
  last quarter, 9 of 9 arms**. Per-tensor means ARE near-stationary. Write "with beta free"
  or "at the adapted operating point". The measurement is untouched; only the word.
* **PATCH_CLIPCOUNT APPLIED TO BOTH ACCOUNTS (63).** Writes `n_at_lo` / `n_at_hi` / `n_beta`
  per record -- the per-(record, coordinate) denominator no earlier probe can supply.
  CORRECTIONS 60 named this gap, priced it at zero, and 61 deferred it; the deferral cost 18
  jobs. Backed up to `HF.py.pre_clipcount.bak`, compile-checked, verified writing on a live job.
* **SUBMITTED, 36 jobs, 18 per account.** (1) **`cl5-*` on alice2** --
  `bin/c51_ceiling_ladder.sh`, the CEILING ladder at R18/ms=1e-3 where the headline lives.
  LO fixed at -30 (measured non-binding); HI in {-4.6052, **0.0**}, with wc5's HI=-2.3026 as a
  free middle point. **The HI=0.0 arm is predicted never to bind and is therefore the first
  completely UNCLIPPED measurement of N_eff/m this campaign has taken.** X0-X3 pre-registered.
  (2) **`uc5-*` on alice** -- `bin/c51_unclipped_family.sh`, both walls out to -30:0.0 on the
  two 100%-occupancy families (r10, c100) plus **r34 as the built-in NULL** (0.0% occupancy;
  it must not move). Tests whether the two numbers setting the LOW end of the published
  "16% to 55%" range are partly the box, and is the first test of rebound mechanism (i).
  U0-U3 pre-registered.
* **NEXT TICK, in order.** (a) `cl5`: **X0.3 (did the ceiling bite?) FIRST**, then the
  layerwise null, then X1 -- if either arm leaves [0.42, 0.62], CORRECTIONS 59's 4-family
  headline needs a box column before it is written down. (b) `uc5`: **U0.3 (the r34 null)
  before anything else**, then U0.4, U1, then U2 via
  `probe5_time_ladder.py ../probes_uc5 ../probes_fz3`. (c) Both batches carry the new
  per-coordinate counts -- report that denominator alongside the per-record one.
  (d) Still unspent, still bookkeeping: the raw-instrument `s` re-derivation sweep.
* Queues at tick end: alice **18 P / 0 R** (`uc5`), alice2 **15 P / 3 R** (`cl5`).

## Running / next (cycle 50) -- THE FILTER IS A **DIAL**; THE HEADLINE IS NOW **4-FAMILY**

**Read `docs/CORRECTIONS.md` 58-61 and `docs/FINDINGS.md` 50.1-50.6 before quoting any `b`,
any gain, or any N_eff. 58 WITHDRAWS CORRECTIONS 53. 59 replaces the "one architecture"
caveat everywhere.**

> **NOTE ON DOC NUMBERING.** The cycle-49 concurrent session left FINDINGS with TWO blocks
> numbered 49.1-49.4 (merge damage, warned about in the cycle-49 handoff). Cycle 50 uses
> 50.x, which is unambiguous. Do not renumber 49.x -- both blocks are real and cited.

* **BOTH CYCLE-49 BATCHES LANDED (54 jobs) AND BOTH WERE SCORED AGAINST THEIR
  PRE-REGISTRATIONS.** Queues were 0/0 at tick start. CSV 1611 runs (+87).
* **CORRECTIONS 53's "SWITCH" IS WITHDRAWN -- IT IS A DIAL (CORRECTIONS 58).** `ml5-*`
  supplied the eta_meta axis 53 explicitly deferred to. Steady half, R18/CIFAR-10,
  weightwise, n=3/rung: **b = 0.343 frozen -> 0.219 at ms=1e-4 -> 0.081 at ms=1e-3**, and
  suppression at k=1 **1.00x -> 3.37x -> 21.09x** while layerwise stays **0.75/0.86/0.94**,
  i.e. ~1 throughout. b(1e-4) landed INSIDE its pre-registered [0.10,0.30] band.
  **Write "the suppression grows with the meta-stepsize and is confined to scales below the
  channel."** CORRECTIONS 49(2)'s "distance from the meta-optimum" is REINSTATED.
* **THE ms=1e-2 RUNG IS CONFOUNDED, EXACTLY AS PRE-REGISTERED.** b(1e-2) = 0.328 is back at
  the frozen 0.343 -- but the BETA_CLIP guard binds on **88.0%/86.8%** of records at
  lay/blk6, and `c49_ms_ladder_p5.sh` named that hazard in advance WITH the fallback rule
  that was then applied. A named hazard firing in the predicted direction is a validity
  check, not a discovery. **Do not write it up as a non-monotonicity.**
* **NEW STANDING RULE (5), the fifth: A REGISTERED FRACTION MUST NAME ITS DENOMINATOR.**
  "Fraction of steps at which the guard binds" is **0.19-28.1%** per (record,tensor) cell
  and **11.5-88.0%** per record -- opposite sides of the pre-registered 50% line. The
  conservative reading was taken. `analysis/c50_dial.py` (selftest **24/24**) prints both.
* **THE HEADLINE IS NO LONGER A ResNet18 RESULT (CORRECTIONS 59).** `ff5-*` passed C0
  **18/18** (beta moved everywhere, n_tot byte-matches fz3, 2000 records). **C1 and C3
  confirmed 3/3**, and BOTH rungs named in advance as thin (c100 weightwise, r10 layerwise)
  cleared. **QUOTE THIS:** *at the adapted equilibrium per-weight meta-gradients carry
  **16%-55%** of the independent information their count implies* --
  **N_eff/m = 0.163 (R10) / 0.481 (R18) / 0.552 (R34) / 0.305 (CIFAR-100)** against
  **0.033-0.082 frozen**. Variance instrument, steady half, weightwise.
* **THE CORRELATION LENGTH IS THE CHANNEL, AND ADAPTATION SHARPENS THAT.** Free b1
  (within-channel) = **-0.045 / -0.013 / -0.099 / -0.059** across the four families -- flat
  in 4 of 4, against frozen +0.069..+0.181 -- while b2 (beyond-channel) stays **0.17-0.42**.
  **Quote the per-leg exponents, never the pooled b.**
* **C2 SPLITS, AND THE PRE-REGISTRATION BUNDLED TWO CLAIMS.** The transfer function's
  SHAPE replicates (monotone in k, 4 of 4; the non-monotone refutation did NOT fire) but its
  DEPTH does not (k=1 gain **4.93x c100 / 5.80x r10 / 21.84x r34 / 22.9x r18**; the
  pre-registered [8x,60x] band fails 2 of 3). **Never write "the transfer function is 23x".**
  C4 is 2/3 pass with **r10 at 7.8x UNDECIDED** (between the 5x pass bar and 10x refutation
  bar) -- do not count it as a pass.
* **AN UNEXPLAINED EFFECT, RECORDED AS UNEXPLAINED (CORRECTIONS 60).** In R10 and CIFAR-100
  free rho_w at k=1 **REBOUNDS x2.7-2.9 in Q4** while the byte-matched frozen control keeps
  decaying /1.9-2.0; in R18/R34 it does not. The decomposition closes to <1%. **Two
  mechanisms tested and BOTH FAIL**: clip saturation (0.0% of tensor betas at either guard
  in every weightwise arm) and beta-velocity collapse (flat to +-30% against a 5x gain move).
  The b1~0 separator is POST-HOC at n=4 families and is labelled as one.
* **NEGATIVE, do not re-run:** b does NOT collapse onto beta displacement (FINDINGS 50.5).
* **INSTRUMENTATION GAP worth one line of PROBE5:** the per-coordinate clipped FRACTION is
  not written (only per-tensor beta + global min/max), so the clip mechanism is
  *unsupported*, not *excluded*. Adding a count of coordinates within eps of either guard
  would close it permanently at zero run-time cost.
* **SUBMITTED: 18 jobs on alice2, `wc5-*`** -- `bin/c50_wideclip_ladder.sh`, the WIDE-CLIP
  control. It closes the one refuted prediction of the tick by making the clip an
  EXPERIMENTAL VARIABLE instead of a fixed confound. **The binding guard is the LOW one**
  (HI is at 0.00% in all 36 ml5 arms; a large meta-stepsize overshoots DOWNWARD and pins
  groups at alpha~3e-7, i.e. kills them), so **only the low bound moves: -15 -> -30**.
  ms {1e-3, 1e-2} x {w,node,lay} x 3 seeds. The ms=1e-3 arm is the NULL CONTROL -- the guard
  binds on 0.00% of its weightwise cells, so widening it cannot matter, and if it does
  nothing in the batch is quotable. W0-W3 pre-registered in the script header before submission.
* **NEXT TICK, in order.** (a) **Score W2 BEFORE W1** -- W1 is meaningless if the guard was
  not actually relieved. (b) Then W0.3 (the null control), then W1: wide-clip b(1e-2) <=0.15
  confirms the dial across all four rungs; >=0.25 with the guard relieved means the dial is
  genuinely NON-MONOTONE with an interior optimum near ms=1e-3 -- a different and more
  interesting claim, and CORRECTIONS 58 must then be rewritten rather than retreating to
  "confounded" a second time. (c) Still deferred, and it is bookkeeping not science:
  re-derive every raw-instrument `s` scattered through FINDINGS 42.4 / 48.19 under the clean
  instrument; CORRECTIONS 59 states the quoting rule that makes it mechanical.
* Queues at tick end: alice **0 P / 0 R**, alice2 **18 P / 0 R** (`wc5`).

## Running / next (cycle 49) -- TWO ZERO-COMPUTE RESULTS; A PUBLISHED MAGNITUDE IS HALVED; TWO AGENTS ARE RUNNING

**Read `docs/CORRECTIONS.md` 53-57 and `docs/FINDINGS.md` 49.1-49.4 before quoting any `s`
or any frozen/free gap. 56 AMENDS FINDINGS 42.4 and 48.19's A3 magnitude.**

> **FIRST, AN OPS WARNING.** A **CONCURRENT SESSION** was operating on this repo and these
> accounts during cycle 49 (FINDINGS 49.2). It submitted `bin/c49_ms_ladder_p5.sh` --
> **36 jobs, `ml5-*`, 4702083-4702118 on alice2** -- a meta-stepsize ladder written
> independently against the same CORRECTIONS 52.4. **Check FINDINGS/CORRECTIONS section
> numbering for merge damage before trusting any section ordering.** Nothing was cancelled.
> This session's own ladder (`bin/c49_meta_stepsize_ladder.sh`) was **retired unrun** as a
> strict subset; its header says so and is kept because the two pre-registrations were
> written blind and agree on both hazards (monotone b, and BETA_CLIP saturation at
> eta_meta=1e-2 mimicking a frozen arm -- score that fraction BEFORE quoting the 1e-2 column).

* **THE `s` INSTRUMENT GAP IS CLOSED, AND IT COST NOTHING (CORRECTIONS 55).** FINDINGS
  48.13's open item is not the window -- `frozen_agreement.arm_stats` already defaults to
  the steady half. It is the **BIAS CHANNEL**: the agreement estimator inverts
  `mean|p_t - 0.5|` (deviation from the fixed point, **b included**) while the variance
  estimator uses `Var(p_t)` (**b excluded**). Debiasing cuts the mean gap **0.143 -> 0.019**
  in 3/3 families and **reconciles the ordering** the raw instrument reversed. E1/E2 were
  pre-registered and committed (3f9fd69) before first contact with data.
  **CORRECTIONS 51's "never use `s` to rank architectures" is REPLACED**: rank freely, but
  only within a bias-free instrument. `frozen_agreement.py` / `neff_ladder.py` are the
  contaminated ones. Use `analysis/neff_instrument.py` (**19/19**).
* **~48% OF THE PUBLISHED FROZEN/FREE `s` GAP WAS THE INSTRUMENT (CORRECTIONS 56).** The
  contamination is one-sided -- weightwise bias share **0.659 frozen vs 0.003 free** -- so
  it falls entirely on the arm the mechanism claim is built from. Controlled R18 pair:
  gap **0.343 raw -> 0.178 debiased / 0.188 variance**. The direction, sign and
  significance are UNTOUCHED and now carry two clean instruments agreeing to 0.010.
  **Never quote 0.343 again.** A3's band `[0.55,0.75]` is raw-instrument-only and fails in
  2 of 3 families debiased.
* **QUOTE `N_eff/m`, NOT rho.** Weightwise, variance instrument, steady half:
  **0.501 free / 0.042 frozen**. *At the adapted equilibrium -- the regime Adam-mini /
  Adalayer / SGG run in -- 11.17M per-weight meta-gradients carry the independent
  information of 5.6M.* One number, clean instrument, right regime, no exponent needed.
* **THE HIGH-PASS FILTER IS A SWITCH, NOT A DIAL (CORRECTIONS 53).**
  `analysis/probe5_time_ladder.py` (**32/32**) reduces the c48 runs over four quarters with
  the frozen arm as a training-progress control. Gain = frozen rho_w / free rho_w:
  **Q1 1.26x / 0.80x / 0.70x** (k=1 / channel / layer) -- before beta moves the free arm IS
  the frozen arm, which is the instrument's **internal control, measured not assumed** --
  then **24.83 / 28.26 / 23.67** at k=1 across Q2-Q4, flat to +-10%. Monotone in k in 3/3
  adapted quarters. **Write "present before the step size has adapted, absent after", NOT
  "varies with distance from the meta-optimum"** until `ml5-*` supplies the eta_meta axis.
* **This tick's own pre-registration failed, usefully.** The b1(t) trend test was registered
  as a RATIO; b1 crosses zero (+0.170 -> -0.081) and a ratio through zero is not a
  magnitude. **NEW STANDING RULE (53), the fourth after thresholds/nulls/windows:** *a
  registered statistic must be defined over the full range the quantity can take; register
  a difference, not a ratio, for anything that can change sign.* On the difference the free
  arm moves **3.4x** the frozen control and is the only arm crossing zero.
* **SUBMITTED: 18 jobs on alice, `ff5-*` (4702123-4702140)** -- the free-beta FAMILY ladder
  (R10 / R34 / CIFAR-100 x lay/node/w x 2 seeds), byte-matched to `fz3` with
  `--alg-meta fixed` -> Lion. It attacks the campaign's largest asymmetry: **the headline --
  correlation survives adaptation -- is measured in ONE architecture** while its
  off-equilibrium half is 4-family. `ml5` does not touch it (R18/CIFAR-10 throughout).
  C0-C4 pre-registered in the script header, resolution of all nine rungs computed from
  `fz3` BEFORE submission, and the **two thin rungs named in advance** (c100 weightwise
  ~1.5x, r10 layerwise ~0.5x) so a null in either cannot later be read as a discovery.
* **NEXT TICK, in order.** (a) Reduce `ff5-*`: `probe5_window.py`, then
  `probe5_time_ladder.py ../probes_ff5 ../probes_fz3` for C2, then **`neff_instrument.py`
  on it** -- the free family arms are the missing half of CORRECTIONS 56's table and say
  whether the ~48% reattribution is R18-specific. (b) Score `ml5-*` against L0-L3,
  clip-saturation fraction FIRST. (c) **Re-derive every `s` in FINDINGS and the draft under
  the clean instrument, tagging each with its instrument** -- rule 55 is not retroactive by
  itself and raw numbers are scattered through 42.4, 48.19 and earlier. (d) Switch-vs-dial
  on `ml5`'s eta_meta axis: smooth across the three rungs = a dial, 53's narrowing lifts;
  ~1x at 1e-4 and ~24x at both 1e-3 and 1e-2 = the switch confirmed on a second axis.
* Queues at tick end: alice **18 P / 0 R** (`ff5`, this session), alice2 **25 P / 11 R**
  (`ml5`, the other session). CSV 1525 runs -- unchanged, no new runs landed this tick.

## Running / next (cycle 48) -- IDEA 3 CLOSES POSITIVE; DIRECTION C's PROFILE IS OFF-EQUILIBRIUM ONLY

**Read `docs/CORRECTIONS.md` 42-49 and `docs/FINDINGS.md` 48.1-48.16 before quoting any
number below. 48.2 SUPERSEDES 47.9's table; 48.6 supersedes any full-run rho_s; and
48.14-48.16 / CORRECTIONS 47-49 NARROW the profile bullet further down this section --
read them before quoting the b = 0.343 exponent.**

> **AMENDMENT, made later in the same tick.** The 12-job free-beta batch landed and
> **REFUTED its own pre-registered B1**. The scale profile is an **off-equilibrium**
> phenomenon: b = **0.343** with beta frozen, **0.065** at the adapted equilibrium, and
> the exchangeable model is rejected 45.4x frozen but only 2.3x free (not rejected).
> **What SURVIVES adaptation is the thing that matters most:** per-weight meta-gradients
> are still not independent at the meta-optimum -- free rho_s(weightwise) = **8.888e-08**
> at 3.1x its own resolution, reproducing FINDINGS 44.3's 8.458e-08 to **+5.1%** -- and
> that is the regime Adam-mini / Adalayer / SGG actually run in.
> **The new positive result is the mechanism:** adaptation suppresses correlation
> **scale-selectively** -- **22.92x** at k=1 (reproducing 44.3's 22.8x independently),
> **5.49x** at k=775, and **0.77x, i.e. not at all**, at k=180,225. A step-size adapter
> behaves as a high-pass filter on meta-gradient co-fluctuation.
> **The window scan added earlier this tick fired on its first new data** and printed
> NOT WINDOW-STABLE for the free arm; `probe5_floor.py --profile` defaults to the FULL run
> and would have reported "the profile survives adaptation", which is the opposite of the
> truth. The free arm's STARTUP window (b = 0.331) is the frozen arm's STEADY window
> (b = 0.343) to 0.012 -- before beta adapts, the free arm IS the frozen arm.
> **Never quote a profile number without naming its window and its beta regime.**

> **FINAL STATE OF THIS TICK. All 32 jobs completed; both queues are back to 0/0.**
> **The frozen profile GENERALISES: A1 CONFIRMED in 4 of 4 families** (span **264.6x** r10 /
> **69.3x** r18 / **23.3x** c100 / **16.6x** r34, window-stable in every one), exchangeability
> rejected **13.6x-127x**, and **A3 CONFIRMED** (frozen s = 0.613 / 0.738 / 0.572 against free
> 0.912 / 1.012 / 0.911) -- so FINDINGS 42.4's frozen/free mechanism is not a ResNet18 artefact
> either. **A2 is NOT DECIDABLE**: its stated "b varies >2x across families" refutation is
> crossed by **3.8%** with b a 3-point fit at n=2.
> **THE SHARPEST FORM OF THE RESULT (FINDINGS 48.18), and it is new:** a single exponent per
> family hides the structure. Per-leg, **weight -> channel b = 0.069-0.181** and
> **channel -> layer b = 0.393-0.816**, steeper in **4 of 4**, with the within-family contrast
> (6.3x) three times the across-family one (2.08x). **Correlation is nearly scale-free WITHIN
> a channel and collapses beyond it -- the correlation length is approximately the channel**,
> and that shape is architecture- and dataset-independent where the single fitted b is not.
> **CAUTION (CORRECTIONS 51): `s` is INSTRUMENT-DEPENDENT.** The agreement-derived and
> variance-derived `N_eff ~ m^s` differ by up to 0.24 on the SAME runs and **reverse the
> family ordering** (c100 last by one, first by the other). Matching the null does not explain
> it (+0.097 -> +0.090). Never use `s` to rank architectures; never quote it to 3 decimals.
> **NEXT EXPERIMENT (CORRECTIONS 52.4), pre-register it before running:** a **meta-stepsize
> ladder** ({1e-4, 1e-3, 1e-2} x 4 rungs, ~12 jobs) turns "frozen vs free" into a curve and
> makes the high-pass-filter reading testable rather than a hypothesis. Second priority: a
> free-beta LADDER -- everything off-equilibrium is now 4-family, everything at equilibrium is
> R18 only.

* **IDEA 3 is BUDGET-STABLE and it is FINISHED at R18/CIFAR-10/m=6.** All 16 c46 300-epoch
  jobs landed; `analysis/idea3_robustness.py` (37/37) prints **THE SHAPE IS BUDGET-STABLE**.
  CORRECTIONS 38/41's "NOT FINAL" hold is lifted. **No further IDEA 3 jobs.**
* **THE VERDICT FLIPPED AGAIN, IN ARM B's FAVOUR, and NOT because of new arm-B data.**
  Arm C completed at 1e-6 and 1e-1, so the shared sub-grid is now the FULL 7 points. Arm B's
  in-band run `[1e-6..1e-3]` had been silently TRUNCATED to `[1e-5..1e-3]` while arm C had
  no 1e-6 cell. On complete data, n=3 (A,B) / n=2-4 (C):

  | full 7-pt grid | A fixed | B meta m=6 | C cosine |
  |---|---|---|---|
  | peak | 91.796 | 93.304 | **94.077** |
  | worst | 68.680 | **83.596** | 53.051 |
  | width <=1pp of own best | 0.477 | 0.000 | **0.523** |
  | width <=2pp / <=3pp | 1.000 | **3.000** | 2.000 |
  | width above 90 / 91 | 0.477 | **3.000** | 2.000 |
  | **grid mean, survivors (no dial)** | 82.793 | **91.723** | 86.782 |
  | **grid mean, face value (no dial)** | 72.765 | **87.058** | 81.963 |

  47.9's *"not more robust than a tuned cosine on any threshold-stable measure"* is
  **WITHDRAWN** (CORRECTIONS 43). Threshold scan: **B>C on 7 of 8 rows**, C>B only at >=92.
* **QUOTE THE DIAL-FREE ROW.** Every width has a tolerance or a floor on it and three
  successive revisions moved band edges without moving any accuracy. The threshold-free
  statistic (new in `idea3_threearm.py`, selftest **45/45**) says **B - C = +4.941pp
  (survivors) / +5.094pp (face value)**. The honest sentence: *MetaOptimize's peak is
  1.113pp below the tuned baseline 94.417 +-0.113 (n=5), but averaged over a 7-decade
  alpha0 grid it is ~5pp AHEAD of a tuned cosine. ~1.1pp of peak buys ~5pp of expected
  accuracy under an unlucky step size.*
* **DIRECTION C HEADLINE -- the scale profile is now CLAIMED, not withheld.** All 8 PROBE5
  jobs landed. Steady half, corrected floor, geometric mean over seeds:
  **rho_w = 3.200e-06 (k=1) -> 1.133e-06 (k=775) -> 4.620e-08 (k=180,225)**, span **69.3x**,
  **rho_w ~ k^-0.343**. Pre-registered outcome **(b): the correlation length is REAL**.
  The heterogeneity correction removes 58% of the excess log-span (165.5x -> 69.3x) and does
  NOT remove the profile. FINDINGS 44.5's "NOT CLAIMED" is resolved (CORRECTIONS 45).
* **The instrument is calibrated against a published campaign number.** `probe5_floor.py
  --profile` defaults to the FULL run and disagreed with FINDINGS 44.3 by 4.2x on a
  byte-matched config. That is **entirely the window**: on the steady half `p5-w-a3` reads
  1.991e-06 / 2.085e-06 against 44.3's **1.925e-06** -- **+3.4% / +8.3%**.
  **NEW STANDING RULE: a time window is a dial exactly like a threshold.** Enforced in code
  by `analysis/probe5_window.py` (**33/33**), which prints full / steady / startup and
  refuses to call a verdict stable unless all three agree. They do: 53.4x / 69.3x / 520x,
  all outcome (b).
* **`probe5_floor.py` hardcodes `N_WEIGHTS_R18` and that would rescale the ResNet10 and
  ResNet34 curves of the batch now in flight.** `probe5_window.py` takes each family's
  n_weights from **that family's own weightwise n_tot** and REFUSES a family with no
  weightwise arm. Never `block_sizes.json` (CORRECTIONS 16).
* **PATCH_PROBE5 + PATCH_PROBE5_FIX are now on BOTH accounts.** Applied to alice this cycle
  (backup `HF.py.bak.pre_probe5`); `tests/test_probe5_block.py` **10/10** against the live
  file, which executes the shipped bytes.
* **SUBMITTED 32 jobs, both queues were 0/0 beforehand, nothing cancelled.**
  `bin/c48_frozen_ladder_p5.sh` **20 on alice** (`4701789-4701808`) -- the corrected profile
  + frozen N_eff exponent on **R10 / R34 / CIFAR-100**, pre-registered A0/A1/A2/A3.
  Supersedes `bin/c43_frozen_ladder.sh`, which exported `PROBE=100` and no `PROBE5=1` and
  therefore could not have carried the correction.
  `bin/c48_free_profile_p5.sh` **12 on alice2** (`4701809-4701820`) -- does the profile
  survive at the ADAPTED equilibrium (`--alg-meta Lion`, one field changed from the frozen
  recipe)? Pre-registered B0/B1/B2 **with the layerwise rung's resolution computed before
  submission** (FINDINGS 48.9): weightwise and nodewise resolve, **layerwise will NOT** --
  so B1 is written on the k=1->775 leg and a layerwise null is a bound, not an absence.
  **B0 is a validity gate**: steady-half rho_s(weightwise) must land within 3x of 44.3's
  8.458e-08 or nothing else in that batch may be quoted.
* Account assignment is BY COMPARATOR and it is the reverse of c43's: the frozen ladder goes
  to alice (its comparators `p7-r18-*` / `p7-c100-*` are there), the free batch to alice2
  (its comparator `p5-*-a3` is there).
* CSV **1525 runs** (985 + 690). Queues after submit: alice 8P/12R, alice2 3P/9R.
  FairShare 0.333054 / 0.333893 -- informational only per CORRECTIONS 37.

## Running / next (cycle 47) -- IDEA 3 GOES THREE-ARMED, and the verdict changes

**Read `docs/CORRECTIONS.md` 37-41 and `docs/FINDINGS.md` 47.1-47.12 before quoting any IDEA 3
number. 47.9 SUPERSEDES 47.1's table** (arm B completed to n=3 mid-tick and one cell crossed a
threshold).

* **THE HEADLINE.** Cycles 45/46 measured MetaOptimize's alpha0 robustness against a
  *genuinely fixed* LR (arm A). Nobody ships a constant LR. The campaign already held the right
  competitor -- **`SW_*`, an AdamW+cosine peak-LR sweep, config- and account-matched** -- and it
  had never been put in the same table. Added as **arm C** at zero compute, it changes the
  answer. On the shared sub-grid {1e-5..1e-2}, all cells n=3 (A, B) / n=2 (C):

  | | A fixed | B meta m=6 | C cosine |
  |---|---|---|---|
  | peak | 91.796 | 93.304 | **94.028** |
  | worst | 70.541 | **89.987** | 83.884 |
  | width <=1pp of own best | 0.477 | **0.000** | 0.523 |
  | width <=2pp / <=3pp | 1.000 | 2.000 | 2.000 |

  **MetaOptimize is not more robust than a tuned cosine on any threshold-stable measure**
  (loses at 1pp, ties at 2pp/3pp) and its peak is **1.113pp** below the tuned baseline
  94.417 +-0.113. **Its one durable advantage is the bottom end:** at alpha0=1e-5 it scores
  **91.535 vs the cosine's 83.884 (+7.65pp)**, and the cosine **never reaches 85%** there while
  MetaOptimize does in 8.7 epochs. Write it as *insurance against a step size set far too
  small, bought for ~1.1pp of peak* -- not as robustness.
* **The "absolute floor" leg is WITHDRAWN as a standalone claim (CORRECTIONS 41).** `i3b-1e2`
  landed at **89.987**, 0.013pp under the 90 line and 7x inside its own sd, which alone moved
  arm B's ">=90 width" 3.0 -> 2.0 decades. The B-vs-C ranking **flips across the threshold
  scan**: B>C at floors <=89.5, B=C at 90-91, C>B at 92. **New standing rule: a threshold
  result must carry its sensitivity scan, exactly as a null must carry its resolution.**
* **Both reducers are now divergence-aware.** `analysis/idea3_robustness.py` **37/37** and
  `analysis/idea3_threearm.py` **34/34** -- run both before trusting any number. Cell means are
  over survivors (`plateau > 50`), divergence counts are their own column, and a cell with any
  divergence is excluded from every width band. This is CORRECTIONS 39 fixed in code: the clip
  control now reports `NOT DECIDABLE` instead of a sign-flipped delta. **Arm A at alpha0=1e-1
  has no surviving seed at all** (3 of 3 collapse).
* **NOTHING ABOUT IDEA 3 IS FINAL** until `analysis/idea3_robustness.py` prints
  **BUDGET-STABLE**. The c46 300-epoch control was still running at tick end. Per
  `docs/IDEA3-robustness.md` §7, a NOT BUDGET-STABLE verdict invalidates the 100-epoch sweep --
  do not patch it with a caveat. **Also read FINDINGS 47.8:** "arm C at 300 epochs" is not
  well defined (it is horizon-matched), and that choice must be made explicitly before any
  three-arm claim is extended to 300 ep.
* **SUBMITTED 18 jobs, ~0.2% of RawUsage, nothing cancelled.**
  `bin/c47_idea3_armC_cosine.sh` **10 on alice** (`4700694-4700703`) -- arm C at the two grid
  extremes 1e-6/1e-1 plus band-edge seed top-ups. Pre-registered C1/C2/C3 in FINDINGS 47.4;
  **C3's arithmetic was invalidated mid-tick by new data, not by being wrong -- see 47.11.**
  `bin/c44_probe5_heterogeneity.sh` **8 on alice2** (`4700704-4700711`) -- per-group marginals,
  the one experiment that de-confounds the scale profile (FINDINGS 44.5).
* **A fatal bug in the prepared PROBE5 patch was caught before submission.** `np.save` appends
  `.npy` to a string path lacking it, so the atomic write's `os.replace` would have raised
  `FileNotFoundError` at record 500 = **5 epochs into every one of the 8 jobs**. Fixed by
  `patches/patch_probe5_fix.py`; regression test `tests/test_probe5_block.py` **10/10 PASS**
  executes the block lifted verbatim out of the live HF.py rather than reading it. **Verified
  end-to-end on the live canary**, which wrote `neg_counts.json` at record 500 and kept running.
  A second suspected bug (`os` scope) was investigated and shown NOT to be one -- FINDINGS 47.5.
* **`bin/c43_frozen_ladder.sh` is AMENDED, still not submitted.** It exports `PROBE=100` and no
  `PROBE5=1`, so its 30 runs could not carry the heterogeneity correction and could not be
  corrected afterwards. The live canary reads **H = 0.833 at m=6** -- 17% of the pooled floor
  is heterogeneity, so this matters. Header now carries the required change plus the resolution
  table. Held until the PROBE5 batch reports.
* **New reducer, written and validated BEFORE its data:** `analysis/probe5_floor.py`
  (**selftest 15/15**, including the case where a true global common mode must NOT be read as
  heterogeneity). Structural check #3 already passes on live canary data to 1.1e-16.
* **CONTROL: no resolvable account effect** (+0.114 +-0.076pp, t=1.49, 9 cells), so arm C being
  single-account is safe at the resolution that matters. FINDINGS 47.7.
* CSV **1505 runs** (956 + 672). Queues at tick end: alice 2P/16R, alice2 5P/11R.
  FairShare 0.333054 / 0.333893 -- overridden per **CORRECTIONS 37**, which formally retires the
  0.35 floor and replaces it with a batch-size rule.

## Running / next (cycle 46) -- IDEA 3 CONVERGENCE CONTROL SUBMITTED, 16 jobs at 300 ep

**The cycle-45 sweep runs at 100 epochs and 100 epochs is not converged.** FINDINGS 44.1:
94.417 -> 94.999 -> 95.138 (cosine) and 92.795 -> 93.033 -> 93.201 (meta) at 100/300/600.
Worse, the under-convergence is DIFFERENTIAL and it is differential in the worst possible
place: at alpha0=1e-6 arm B must first grow its own step size, costing **+11.4 to +19.0
epochs** on `ep_to_85` (audit 5's correction to standing rule R5 -- the floor is ~11, not the
"14-25" this project used to quote, and the damaging part is the DIFFERENTIAL, up to 7.6 epochs
between two arms compared directly). So a 100-epoch budget understates arm B at exactly the
extreme the robustness claim is about, and **a negative IDEA 3 verdict at 100 epochs would not
be falsifiable** -- "not robust" would be indistinguishable from "not enough budget".
This project has already had a budget change move a shape: audit 5's rule R6 (FINDINGS 36.2).

* **`bin/c46_idea3_budget_control.sh`, 16 jobs, 300 epochs.** alpha0 in
  {1e-6, 1e-5, 1e-2, 1e-1} -- **the four EXTREMES only** -- x both arms x seeds {0,1}.
  alice `4700666-4700673` (seed 0), alice2 `4700674-4700681` (seed 1); every cell is
  `{alice x1, alice2 x1}` so account cannot confound the 100-vs-300 contrast either.
  Pending after submit: alice 24, alice2 9. Nothing cancelled; all 45 c45 jobs untouched.
* **The middle of the grid is NOT re-run at 300 ep, on purpose.** The startup tax is a
  bottom-end effect and the guard is a top-end effect; the interior is where a budget artefact
  CANNOT flip the shape. Extremes-only is the design, not a compromise on it.
* **`gpu-short` is dropped for this batch** -- it caps at 4:00:00 and `bg600-meta-s1` on a
  2080ti ran 7:41:51/600ep = ~3:51 for 300. `--time=08:30:00` on the four long partitions,
  exactly what `bg300-*` used. This is the one deviation from "all five partitions".
* **Run names are `i3a300-*` / `i3b300-*`, and that matters.** They do NOT match
  `startswith("i3a-")`/`("i3b-")`, so a 300-epoch row cannot be pooled into a 100-epoch cell.
  The reducer now ALSO filters per-arm on `epochs_done` (>=300 for these). Two independent
  mechanisms, both unit-tested.
* **Arm A is still a genuinely fixed LR at 300 ep -- verified against the live scheduler
  object** out to 150,000 steps: 1.000000000e-3 -> 9.999944484e-4, i.e. constant to **5.55e-6**
  relative, no warmup. The 50,000-step column reproduces the c45 check exactly.
* **The reducer reports every metric at BOTH budgets and prints an explicit shape verdict.**
  `analysis/idea3_robustness.py --selftest` is **22/22 PASS**. Budget stability is judged on the
  matched 4-point sub-grid (100ep metrics RECOMPUTED there, never 7 points vs 4) and requires
  all three: band membership unchanged, both widths unchanged, A-vs-B ordering unchanged.
  **If it prints NOT BUDGET-STABLE, the 100-epoch sweep is not a valid basis for the robustness
  claim -- do not patch it with a caveat.** Full rationale: `docs/IDEA3-robustness.md` §7.
* FairShare overridden again (0.333054 / 0.335570, unchanged -- CORRECTIONS 35's 14-day
  half-life), recorded as `--force-fairshare` in the script's own log.

## Running / next (cycle 45) -- IDEA 3 SUBMITTED, 45 jobs, both accounts

**The project stopped measuring peak accuracy and started measuring the thing the paper
actually claims.** Full design, predictions and limits: **`docs/IDEA3-robustness.md`** -- read
that before touching any `i3*` row.

Queues at submit: alice **0/0** (FairShare 0.333054), alice2 **0/0** (0.335570). Both below the
0.35 floor; **the floor was overridden by explicit operator instruction**, recorded in the
script as `--force-fairshare` so the deviation is visible in its own log. CORRECTIONS 35 is why
the rule could not be waited out (14-day half-life; an idle cycle moved FairShare by <1e-4).

* **What is in flight.** `bin/c45_idea3_alpha0_robustness.sh`, 45 jobs, 100 ep, R18/CIFAR-10,
  AUGMENT=1, guard on, `--max-time 999:00:00`, all five partitions.
  **Arm A `i3a-*`** = plain AdamW at a **genuinely fixed** lr; **arm B `i3b-*`** = AdamW base +
  Adam meta at `resnet18_blocks` (m=6, the paper's setting); alpha0/lr in
  {1e-6,1e-5,1e-4,3e-4,1e-3,1e-2,1e-1} x 3 seeds. Plus **`i3bc-*`** (3 jobs), the clip control.
  Split by SEED, never by arm: alice seeds 0,1 (28 jobs), alice2 seed 2 + the clip controls
  (17). Every cell is `{alice x2, alice2 x1}` so **account cannot confound anything** here
  (the failure mode that cost CORRECTIONS 10 a whole claim).
* **Arm A is a NEW arm and this is not obvious.** `AdamW_optimizer` ALWAYS builds a
  `CosineDecayWithWarmupScheduler` -- there is no un-scheduled path -- so every "fixed-LR
  AdamW" row already in the CSV (`fx_adamw_*`, `bl-adw-*`, `fxcos-*`) carries a **10,000-step
  (20-epoch) linear warmup**, and `SW_*` is a true cosine. Arm A sets `COS_WARMUP=0`,
  `COS_TOTAL=100000000`, **verified against the live scheduler object**: lr holds at
  1.000000e-3 -> 9.999994e-4 over all 50,000 steps. Do NOT compare `i3a-*` to the older
  "fixed" rows -- they are warmed-up arms.
* **`i3bc-*` exists because `BETA_CLIP` caps alpha at 0.0999998**, so arm B's top grid point
  (alpha0=1e-1) starts pinned at its own ceiling. `i3bc-1e1-s{0,1,2}` re-runs that one cell at
  `BETA_CLIP=-15:0`. Lands on `i3b-1e1` -> the guard is not doing the work; lands far below ->
  arm B's top-end flatness is partly the guard. Rule 4: measure the dial, do not write the
  caveat.
* **Pre-registered, in `docs/IDEA3-robustness.md` §4.** (P1) arm A collapses at the bottom
  (1e-6 < 60, 1e-5 < 85) and its within-1pp width is <= 1.5 decades; (P2) arm B is within 1pp
  of its own best across all of [1e-6,1e-3] -- **nearly forced** by three cells already in the
  CSV (`a0-blk6-*`: 91.663 / 91.638 / 92.071 at 1e-6 / 1e-4 / 1e-3), so the sweep's real
  information is at **1e-5, 3e-4, 1e-2, 1e-1**; (P3) both peaks below 94.417.
  **Refutation (publishable either way): if arm B is NOT strictly flatter than arm A, the
  parent paper's own robustness claim fails on its own configuration.** Write it as that.
* **Reducer is written and unit-tested BEFORE the data** -- `analysis/idea3_robustness.py`,
  `--selftest` **9/9 PASS**. It reports, per arm, (i) width within 1pp/2pp of that arm's own
  best in decades, (ii) worst case, (iii) peak, then the tradeoff line. The width convention
  (longest **contiguous** in-band run; a lone cell is 0 decades, not half a grid spacing;
  gapped in-band sets are flagged) is the only judgement call and it is what the tests cover.
* **Nothing about peak accuracy changed.** CORRECTIONS 30's **1.622pp** deficit stands and must
  appear in the same breath as any width claim. Reference peak is **94.417 +-0.113 (n=5)** --
  not 94.093, 94.24 or "94.4".
* **Read with:** `epochs_done >= 100`, `superseded == 0`. `.out` files land in the ROOT of
  `runs/`, not `runs/i3/`. No probe dirs in this batch.

## Running / next (cycle 44) -- ZERO COMPUTE, and it produced the campaign's best result

Queues: alice **0 PENDING / 0 RUNNING**, alice2 **0 / 0** -- nothing in flight anywhere.
FairShare **0.333054 / 0.335570**, both below the 0.35 floor -> **0 submitted**.
CSV re-aggregated: **1446 runs** (878 + 618), +1 since cycle 43 (`bg600-meta-s2`).
Probe sweep: **no unreduced probe data on either account** (`fzp4`, `fz2` are empty dry-run
artefacts of cycle 43's prepared batches).

**Direction C now has a measured mechanism, obtained entirely from data already on disk.**

* **44.3 -- THE HEADLINE. The frozen-beta N/N_eff deficit is 85% MARGINAL BIAS, 15% common
  mode, 0.7% independent noise.** `fz-w-a3` vs `p7-r18-w` are byte-matched `ARGS` except
  `--alg-meta fixed` vs `Lion` (both a0=1e-3 -- verified from beta at step 0; `neff_ladder.py`
  said 1e-6 and was wrong):

  | arm | n | bias pp | rho_s | t | %bias | %com | %indep | N/N_eff |
  |---|---|---|---|---|---|---|---|---|
  | beta FROZEN | 5 | 0.1680 | 1.925e-6 | 11.7 | **85.1** | 14.6 | **0.7** | **148.6** |
  | beta FREE | 10 | 0.0032 | 8.458e-8 | 6.8 | 4.0 | 45.6 | **52.4** | **1.99** |

  Independent confirmation of CORRECTIONS 27 from a different statistic (that one got
  199.8 -> 2.0 via `N_eff ~ m^s`). Window-robust; in the STARTUP window the free arm reads
  130.4, i.e. before beta adapts it behaves like the frozen arm.
  **Adaptation consumes the BIAS (52.7x) more than the correlation (22.8x)** -- mechanically
  what a step-size adapter is, since E[meta-gradient] = 0 at the meta-optimum. So the
  marginal-bias channel measures distance from meta-stationarity.
* **44.4 -- per-weight correlation is MEASURED, not bounded, and CORRECTIONS 33 was right.**
  §33 predicted the true rho is ~1e-6..1e-8 and that kt2's pairwise test (resolution 1.7e-5)
  could not see it. Five cells now measured, **all inside that band and all below 1.7e-5**.
  CORRECTIONS 31's "there is no measurable correlation" is **REFUTED**; §33's diagnosis
  **CONFIRMED**. `mx` and `kt2` agree to 5% at matched config across independent batches.
* **44.1 -- the long-horizon question is CLOSED.** `bg600-meta-s2` landed; n=3/n=3 at 600 ep
  gives a **1.937pp** deficit (was 1.797 at n=2). 1.622 / 1.967 / 1.937 at 100/300/600.
  Both arms saturating. **No further `bg` jobs.**
* **44.5 -- the SCALE PROFILE is NOT claimed.** The raw profile falls (85x on `fz/a6`, 25x on
  `mx`), which looks like short-range correlation -- but the estimator's floor bias grows with
  group size and produces exactly that signature. Recorded as an open question with the
  confound named. Per-rung `rho_s` values are unaffected and are **lower bounds**.
* **The instrument.** `analysis/twochannel.py` (+ `corr_range.py`), validated
  `tests/test_twochannel.py` **11/11** and `tests/test_corr_range.py` **3/3** --
  **run both before trusting any number they print.** Two estimator bugs and one *validation*
  bug were caught this way; see CORRECTIONS 34.
* **Next cycle, in order.** (1) **Re-check FairShare first** -- see CORRECTIONS 35: the
  half-life is **14 days**, so recovery to 0.35 is a multi-day process and a full idle cycle
  moved it by <1e-4. The operator should decide whether the rule stands as written.
  (2) `bash bin/c44_probe5_heterogeneity.sh --submit` on alice2 (8 jobs, dry-run-validated,
  self-guarded) -- **first apply `patches/patch_probe5.py`**; the script refuses to submit
  without it. This de-confounds 44.5, the one question cycle 44 opened.
  (3) `bin/c43_frozen_ladder.sh` (30 jobs) -- frozen-beta to R10/R34/CIFAR-100.
  (4) **Do NOT submit `bin/c44_frozen_probe4.sh`** -- superseded; its instrument is 50x
  coarser than the correlation 44.3 already measured, so it would return an uninformative null.
* Local probe copies: `analysis/killtest_data/{mx,gate3,fz,p7free,p6free,kt2}` (118 MB).

## Running / next (cycle 43) -- COLLECTION + REDUCTION, nothing submitted

Queues: alice **0 PENDING / 1 RUNNING** (`bg600-meta-s2`, 479/600 -- do not read), alice2
**0/0**. FairShare **0.3331 / 0.3356**, both below the 0.35 floor -> **0 submitted**.
CSV re-aggregated: **1446 runs** (878 + 618), +12 since cycle 42. Cycle 42's read list is
cleared: `I1-*`, `SW-*` and `PP-*` are all read, and the two `kt2` probe runs are reduced.

**BOTH REMAINING SIDE-IDEAS ARE NOW DEAD. Direction C is the project, and cycle 43 changed
what C says.**

* **43.1 -- IDEA 1 IS DEAD.** `I1-*` read against **byte-matched, same-account** controls.
  Best arm (layerwise) **92.544 +-0.207 (n=3)**; tuned baseline **94.417 +-0.113 (n=5)** ->
  **-1.873pp**. It is also **-0.251pp** below our own best existing arm (42.2's 92.795). Prior
  art caps it at a tie. Stop; no further I1 jobs.
* **43.2 -- but the schedule prior is granularity-EQUALISING**, and that is a mechanism result
  for C: +1.664 layerwise / +0.137 blk6 / **-0.465 scalar**, collapsing the granularity spread
  **1.803 -> 0.405pp** and inverting the ordering. **PROVISIONAL -- read CORRECTIONS 29 before
  quoting it.** The `I1-*` schedule is *unidentified* (no saved script, no `SCHED` echo, no
  alpha/beta in TensorBoard) and is provably NOT a matched-horizon cosine: the arm is **+7.2pp
  ahead at epoch 2**, where a matched cosine multiplier is 0.9978.
* **43.3 -- IDEA 2 STAYS DEAD, now also at per-weight granularity** (but read 43.3c /
  CORRECTIONS 33 before quoting the SIZE of this null -- the per-weight test is under-powered
  by 1-3 orders of magnitude for the structure that is actually there, so the kill still rests
  on the TENSOR-level across-block null).** `kt2_ww_*` carry
  `PATCH_PROBE4` (raw per-coordinate signs, 20k tracked weights) -- the one experiment
  KILLTEST-idea2 sec.5 pre-registered and no earlier run could answer. Estimator validated
  16/16 against synthetic ground truth *before* use. Pairwise same-sign rate between
  **individual weights**, vs a marginal-preserving circular-shift null: across-tensor
  **+0.0001pp**, across-block **-0.0001pp**, architecture - random same-size **+0.0002pp
  (p=0.29)**. Kill threshold was 0.1pp. **Replicated at a0=1e-6** (43.3b) where all four
  strata flip sign -- i.e. pure noise.
* **43.3/43.3c -- THE HEADLINE MECHANISM IS PARTLY WRONG, AND THE POWER CALCULATION IS THE
  REAL RESULT.** The **+0.194pp** majority-agreement excess over the independence floor is
  **marginal bias, not a global common mode** -- a common mode big enough to produce it would
  show at ~5 sd and does not (+0.0047 +-0.010pp; -0.0006pp at a0=1e-6). CORRECTIONS 8b's
  "the signs are strongly positively correlated" is wrong for THAT statistic.
  **But do NOT extend it to "there is no correlation".** A group meta-gradient is a SUM, so
  aggregation amplifies a shared component by ~n: the depth-local structure KILLTEST sec.3
  measured between tensor MEANS needs only rho ~ 1e-6..1e-8 per weight, against a per-weight
  detection limit of rho = 1.7e-5. **The per-weight null is 2x-170x under-powered.**
  CORRECTIONS 31's inference is WITHDRAWN by CORRECTIONS 33, same tick.
  **New standing rule: a null may not be reported as evidence of absence until the minimum
  effect the test could resolve is computed and stated next to it.**
* **43.4/30 -- the baseline is re-tuned and the LR curve is CLOSED.** `SW-*` (horizon-matched
  `COS_TOTAL=50000`) gives 83.88 / 88.81 / 92.96 / 93.99 / 94.03 / **94.36** / 92.58 across
  lr 1e-5..1e-2. **3e-3 is a bracketed interior maximum**; pooled with `fxcos-3e-3` the tuned
  100-ep baseline is **94.417 +-0.113 (n=5)**, not 94.093/94.24. **Recompute every "loses by X"
  sentence.** Also: horizon-matching the cosine is worth **+0.10 +-0.10pp -- unresolvable**, so
  "the gap is the schedule" is too strong. **The gap is the peak LR.**
* **43.5 -- long-horizon deficit, n=3 baseline seeds at every horizon:** 1.622pp @100ep /
  1.966 @300 / 1.797 @600. Does not close.
* **43.6 -- `PP-*` read** (AUGMENT=0, kept separate per CORRECTIONS 28.2): blk6 74.349 >
  scalar 73.717 > layerwise 73.365. A third setup where "finer is better" fails at the coarse end.
* **Next cycle, in order.** (1) **Re-check FairShare first** -- both queues are at 1 job total,
  which is the fastest possible recovery; the moment either clears 0.35, submit. (2)
  `bash bin/c43_frozen_ladder.sh --submit` on alice2 (30 jobs, prepared + dry-run-validated +
  self-guarded) -- frozen-beta to R10/R34/CIFAR-100, still the largest open cell. (3) **NEW and
  cheap: a `PATCH_PROBE4` probe on a FROZEN-beta run (2 jobs).** CORRECTIONS 31 leaves the
  off-equilibrium `s=0.629` undecomposed -- we do not know whether the off-equilibrium failure
  is bias or correlation, and `kt2`'s instrument answers it directly. This is now the single
  most informative cheap experiment in the campaign. (4) `rs-node-*` / `rs-blk6-1e4` seed
  top-ups. (5) `bg600-meta-s2` when it lands.
* Local probe copies: `analysis/killtest_data/{mx,gate3,fz,p7free,p6free,kt2}` (118 MB).
  Reducer for the new data: `analysis/killtest2_coords.py` (tests in
  `tests/test_killtest2_coords.py` -- **run them before trusting any number it prints**).

## Running / next (cycle 42) -- COLLECTION + REDUCTION, nothing submitted

Queues: alice 0 PENDING / 25 RUNNING (FairShare **0.3331**), alice2 **0 / 0** (**0.3356**).
Both below the 0.35 floor -> **0 submitted**. CSV re-aggregated: **1434 runs** (866 + 618),
+127 since cycle 41. Cycle 41's entire read list is cleared and its two unreduced probe
batches (`fz-*` 50 dirs, `p7free` 92 dirs) are reduced.

**THE DIRECTION CHANGED. Read CORRECTIONS 26 and 27 before writing any sentence about
sign agreement.** The handoff line "53.1% of 11.17M per-weight meta-gradients agree in sign,
independence = 50.0000 +-0.0015%" merges two different arms and quotes a null that belongs to
neither: 53.1% is the LAYERWISE arm (m=62) whose own independence floor is **55.07%**, so that
arm sits 1.9pp *below* its floor; the weightwise arm reads 50.028% against a 50.012% floor.

**What replaces it (FINDINGS 42.4), and it is stronger.** Effective independent count
N_eff ~ m^s, s=1 being exactly the 1/sqrt(N) assumption the Adam-mini / Adalayer / SGG line
makes. Two batches identical in every field except `--alg-meta`:

| design | s | n | N/N_eff at m=11.17M |
|---|---|---|---|
| beta FROZEN (`fz-*-a3`, `--alg-meta fixed`) | **0.629 +-0.013** | 5 | **199.8** |
| beta FREE (`p7-r18-*`, `--alg-meta Lion`) | **0.963 +-0.015** | 10 | 2.0 |

and inside the free runs s climbs 0.654 -> 0.963 over the first ~10 epochs as sd(beta) rises
0.02 -> 2.05, while the frozen runs stay flat at 0.59-0.68 for all 20 epochs. **The correlated
part of the meta-gradient is exactly the part step-size adaptation consumes.** So the 1/sqrt(N)
assumption is wrong by up to 200x in variance at uniform step sizes and approximately right at
the adapted equilibrium -- the *opposite* of the unconditional refutation the project was
steered on. Structural check passed: all 2000 records have `beta_true_max == beta_true_min`,
and the five arms' 20-epoch accuracies agree to 0.010-0.030pp at matched seed.

* **42.1 -- the long-horizon question is ANSWERED and it is a clean negative.** AdamW+cosine vs
  AdamW+Adam-layerwise: deficit **1.732pp @100ep -> 1.966 @300ep (n=3/n=3) -> 1.949 @600ep
  (n=3/n=1)**. 41.4 pre-registered that parity at 300ep needed MetaOptimize to gain +2.638pp;
  it gained +0.672pp. Both baseline numbers are lower bounds (lr=1e-3 is off the 2e-3-3e-3
  cosine argmax), so the true deficit is larger.
* **42.2 -- granularity SURVIVES meta-step tuning; 40.1's pre-registration is FALSIFIED.** At
  each arm's own tuned meta-step: scalar 92.231 +-0.190 (n=5), blk6 92.581 +-0.057 (n=2),
  layerwise **92.795 +-0.177 (n=5)**, nodewise 92.547 (n=1). layerwise-scalar = **+0.563pp**,
  t=4.85, CI [+0.296,+0.831] -- clears PLAN.md's standard. **Verdict declared.** But the gain
  is non-monotone with an **interior optimum at m=62**, and 83% of the raw +3.348pp gain at
  ms=1e-3 is meta-step tuning.
* **42.3 -- IDEA 2 IS DEAD.** Across-architectural-block pairwise agreement on the weightwise
  arm is **50.003 +-0.081%** -- the null exactly (pairwise null is exactly 0.5, unbiased).
  Spectral clusters score ARI 0.05-0.24 vs the 6-block partition, no better than a random
  contiguous partition. Dropped, not pursued.
* **IDEA 1 is in flight and its schedule status is UNVERIFIED.** `I1-*` (9 jobs) was submitted
  by the previous session with **no saved script**, and `run_cifar.sh` did not echo `SCHED`, so
  nothing on disk proves the cosine prior was actually enabled. The discriminator is ready:
  exact matched non-scheduled controls exist at n=3/3/8 -- scalar **92.684 +-0.178**
  (`a0-scal-1e3`), blk6 **92.002 +-0.138**, layerwise **90.860 +-0.174**. If I1 lands on those,
  SCHED was off and the batch is a duplicate; if it departs, the delta IS the Idea-1 effect.
  `run_cifar.sh` on both accounts now echoes SCHED/SCHED_TOTAL/PROBE (backup `.bak_c42`).
* **Next cycle, in order.** (1) `bash bin/c43_frozen_ladder.sh --submit` on alice2 -- 30 jobs,
  prepared and dry-run-validated, self-guarded on FairShare>=0.35 and pending<=10. It carries
  the frozen-beta measurement to ResNet10/ResNet34/CIFAR-100 and is the campaign's largest open
  cell: 42.4's frozen half exists at ResNet18/CIFAR-10 ONLY. Pre-registered predictions and the
  refutation condition are in the script header. (2) Read `I1-*` against the controls above.
  (3) `rs-node-*` seeds 1-2 (nodewise peak is n=1 at every cell) and `rs-blk6-1e4` seeds 2-4,
  to close 42.2's interior optimum. (4) `bg600-meta` s1/s2.
* Local probe copies: `analysis/killtest_data/{mx,gate3,fz,p7free,p6free}` (66 MB). Reducers:
  `analysis/frozen_agreement.py`, `neff_ladder.py`, `neff_timecourse.py`, `neff_validate.py`
  (synthetic ground-truth validation -- run it before trusting any N_eff number),
  `killtest_idea2.py`.

## Running / next (cycle 41) -- COLLECTION CYCLE, nothing submitted

Queues: alice 94 PENDING / 19 RUNNING (FairShare **0.3331**), alice2 50 / 12 (**0.3356**). Both
below the 0.35 floor and above the 40-pending cap -> **0 submitted**, deliberately. CSV
re-aggregated: **1307 runs** (778 alice + 529 alice2), +26 since cycle 40.

* **The scalar meta-step curve now has a measured cliff** (FINDINGS 41.1). `msa-*` -- built as a
  collapse test, ruled not-identified by 36.6 -- turns out to be exactly the extra scalar grid
  points the `rs-*` surface needs. Scalar peaks at ms~1e-4 (92.255 +-0.264) and falls **4.787pp**
  by ms=3.947e-4, then flattens onto a floor (87.47 -> 87.75 out to 1e-3). Usable window < 1 decade.
* **The granularity gain shrinks 5.5x with meta-step** (41.2): +3.392pp at ms=1e-3 (n=12 vs n=12)
  -> +0.617pp at ms=1e-4 (n=3 vs n=3). Strongest reparameterisation evidence so far, and the
  ms=1e-3 end is now n=12 per arm.
* **"Finer is better" is already false at the coarse end**: at ms=1e-3, blk6 (m=6) 91.548 +-0.108
  beats layerwise (m=62) 91.141 +-0.171 by +0.407pp (t=5.6).
* **40.1's pre-registration is under strain in the FALSIFICATION direction** (41.3). Scalar's peak
  is bracketed at ~92.26; layerwise at ms=1e-4 is already 92.872 +-0.041 and its own peak is not
  yet located. Gap >= +0.617pp, CI [+0.308,+0.925] -- excludes 0, does NOT clear PLAN.md's
  Delta>=0.5pp standard. **No verdict declared.** Deciding cells all in flight.
* **`bg300_cos` = 94.999 +-0.164 (n=3, 300 ep)**, +0.906pp over its own 100-epoch 94.093. The
  meta half (`bg300_meta`) is at 250-254/300 -- NOT read. For parity it must gain **+2.638pp**
  over its own 100-epoch 92.361 +-0.433. Also: `bg300_cos` runs at lr=1e-3, off the cosine argmax
  of 2e-3-3e-3 (39.2), so 94.999 is a LOWER bound -- conservative in MetaOptimize's favour.
* **Batch health: 0 failures anywhere.** `rs-*` 106 submitted / 5 complete / 11 running / 90
  pending (all 25 `rs-blk6` present at nice 50 -- they were mis-reported absent by a squeue
  bucketing error; `sacct -o JobName%22` RIGHT-justifies, so `grep "^rs-"` returns 0. Use `%-24`).
* **No unreduced probe batches**: 234 dirs on alice + 124 on alice2 across 28 batch names, all
  referenced in FINDINGS/CORRECTIONS.
* **Next cycle reads, in order:** `bg300_meta` (priority 1, ~3 epochs out); `rs-scal-3e5`/`1e5`
  (does scalar's peak hide between 3e-5 and 1e-4?); `rs-lay-3e4` (where is layerwise's peak?);
  then the n=5 diagonal top-ups that decide 41.3.

## Running / next (cycle 38) -- COLLECTION CYCLE, nothing submitted

**The pre-registered meta-step control fired against granularity (FINDINGS 38.1).** At a0=1e-3,
R18/CIFAR-10, SGDm+Lion: plain `scalar` with ms tuned 1e-3 -> 1e-4 scores **92.405 +-0.071
(n=2)** -- inside cycle 33's pre-registered [92.2,92.6] window. That matches the BEST
hierarchical arm (`additive` r=0.1, 92.449 +-0.192, n=3) to **0.044pp** and beats plain
layerwise (91.093 +-0.220, n=5) by 1.312pp. The whole +4.87pp scalar->layerwise "granularity
gain" is reproduced by changing one scalar hyperparameter. With 33.1 (r rescales the effective
meta-step by |2p-1| ~ 0.097) this closes the loop: **the hierarchy's only measured contribution
is dividing the meta-step by ~10, and doing that directly with one group is equal or better.**

* **`ms-layA-1e4` (3 seeds, PENDING alice2) is now the most informative job in the campaign.**
  Layerwise at the tuned ms=1e-4 / a0=1e-3. Above 92.405 => granularity earns something back at
  its own tuned meta-step. Level => 38.1 is the whole story.
* `ms-scalA-1e4` is **n=2**; s2 sits at 89/100 and must not be read. Needs n=5.
* **alpha0=1e-6 escape confound quantified: 51.04pp** (ms=1e-4 scores 41.368 at a0=1e-6 vs
  92.405 at a0=1e-3). It inverts the SHAPE of the ms curve. No ms claim off a0=1e-6 runs.
* **Baseline win holds across architecture.** R34 now n=3 both sides: 94.674 +-0.026 vs 93.930
  +-0.143 = 0.744pp, matching R18's 0.787pp. Not a ResNet18 artefact; does not close at scale.
  lr=1e-3 is argmax at R18/R34/R50 -- the baseline's tuning transfers. R50 baseline is n=1.
* **LR grid decensored** (answers 36's objection): 1e-4 92.851 / 3e-4 94.062 / 1e-3 94.093 /
  1e-2 92.728. 1e-3 is an INTERIOR maximum. A 10x-mistuned cosine still beats the best matched-a0
  meta arm by 0.28pp.
* **Ops: submitted NOTHING.** FairShare 0.3356 / 0.3381 (below the 0.35 floor); pending 59 / 94
  (above the 40 cap); 93 of 94 alice2 pendings blocked on `QOSMaxGRESPerUser` = GPU-cap-bound,
  not priority-bound, so extra jobs could not have started anything sooner. Every open question
  above already has its deciding cell queued.
* Priority inversion (LR sweep ahead of `bg300`/`bg600`) noted and **deliberately not corrected**
  -- post-36.1 the sweep is the decisive line and `bg` is downstream of it.

## Running / next (cycle 33)  -- queues: alice 174, alice2 164 = 338 jobs

**Cycle 33 refuted the campaign's pooling story and found the mechanism 26.3 was missing.**
Three arms that all end in ONE uniform step size score 4.85pp apart, ordered by their
EFFECTIVE meta-step-size and nothing else (FINDINGS 33.1):

| arm | effective meta-step | n | plateau |
|---|---|---|---|
| `zpool` r=0 / plain `scalar` | `ms` = 1e-3 | 5 / 12 | 87.740 / 87.772 |
| `shrink` lam=1.0 | `ms`*\|2p-1\| ~ 9.7e-5 | 3 | 92.199 |
| `additive` r=0 | `ms`*\|2p-1\| ~ 9.7e-5 | 8 | 92.587 |

`_zpool` pools the meta-GRADIENT before Lion (magnitude survives); `_apply_hier` pools the
REALISED increments after Lion (magnitude collapses to the sign-agreement excess). So M1's `r`
moves pooling and meta-step-size together. **The M1 gain depends on agreement because the
effective meta-LR does** -- that is the mechanism, and it is a confound, not a result.

**The meta-step-size axis is unexplored: 1042 of 1075 runs sit at `ms`=1e-3.**

* **`ms-scal-*` (26, alice) / `ms-lay-*` (26, alice2) -- PRE-REGISTERED, DECISIVE.**
  `scalar` and plain `layerwise` x ms in {1e-5, 3e-5, 1e-4, 3e-4}, n=5, plus a0=1e-3 controls.
  **Pre-reg: `scalar` at ms=1e-4 lands 92.2-92.6** (on `shrink` lam=1 / `additive` r=0) => the
  whole M0/M1 family is meta-LR tuning and granularity contributes nothing. Staying near 87.8
  saves the pooling arms. Whether the layerwise ms curve reaches 93.222 decides M1.
* **`zp-w-*` / `zp-l-*` (17, alice2) -- PRE-REGISTERED.** True-pooling curve: weightwise
  r in {0.9,0.95,0.99} to n=5, NEW cells r in {0.995,0.999}, layerwise r=0.99 to n=3.
  33.2's weightwise interior optimum (+11.130pp at r=0.99) is n=2 and its cliff is unlocated.
* Still front-of-queue from cycle 32: `p7-c100r*` (30), `sc50-*` (18+6 running), `r34r-*` (9),
  `f5cos-*` (12) on alice; `r34f-*` (11), `bp-*`/`bo-*` (~39), `ag-*`/`ap-*` (36),
  `mx-h4-*` (20) on alice2. All pre-registered; none is blocked by this cycle's submissions.
* **Cancelled 97 jobs**, each with a reason recorded in FINDINGS 33.8. Net queue change -45.
* Ops: throughput is STILL 24 concurrent. The per-account cap of 42 GPUs is not reachable --
  the QOS pools are per-partition and every long partition is fully allocated by other users,
  so multi-partition submission cannot spread into them (FINDINGS 33.9). Also: fair-share has
  fallen far enough that a fresh nice-0 job now ranks BELOW old nice-400 jobs; the only way to
  promote an old low-priority batch is cancel-and-resubmit.

## Running / next (cycle 32)  -- queues: alice 189, alice2 214 = 403 jobs

**Cycle 32 found two batches that finished cycles ago and were never tabulated** (`sc50-*` =
ResNet50 n=1; `cs-r10/cs-r34-*` = CIFAR-100 x model scale n=3). Reducing them gives a
FOUR-architecture model-scale ladder on CIFAR-10 and a THREE-row one on CIFAR-100, and the two
scale effects run in OPPOSITE directions (FINDINGS 32.5-32.6):

| | R10 4.9M | R18 11.2M | R34 21.3M | R50 23.5M |
|---|---|---|---|---|
| M1 pooling gain (r=0.06 vs r=1), a0=1e-6 | +0.166 (null) | +2.446 | +2.594 | +3.237 (n=1) |
| plain granularity gain (layerwise - scalar) | +19.877 | +3.043 | +0.835 | **-1.394 (n=1)** |

**ResNet50 at a0=1e-6 is the first architecture where the parent paper's premise reproduces**
-- layerwise loses to scalar. It is ONE SEED. `sc50` s1-s4 are queued at nice 50; do not state
it until they land.

**The paper core got stronger.** `p9-*` landed: the agreement/drift ladder is n=10 at all four
rungs on BOTH datasets, and all 8 slopes have bootstrap 95% CIs that exclude -0.500 (32.1).
A 9th fit at a0=1e-6/100ep gives -0.2363 and shows the drift-vs-m curve is **non-monotone**
(rises 6 -> 62, then falls), so sqrt(N) has the wrong FUNCTIONAL FORM, not just the wrong
exponent (32.2). 31 of 32 leave-one-rung-out sub-spans also stay above -0.500; the one
exception (-0.5248, R10/STARTUP/node->weight, n=2) is anchored on the weightwise startup drift,
which is a near-cancellation biased toward zero and therefore biases that slope steep (32.3).

**26.3's mechanism is refuted.** `gp-node-*` landed at M1 gain +1.204 against a LOWER agreement
than layerwise's +2.446. Agreement is monotone in m; the gain is not (32.8). The campaign has
no single mechanism right now.

* **`p7-c100r10-*` / `p7-c100r34-*` (30, alice, nice 0) -- PRE-REGISTERED.** C100 x {R10,R34}
  agreement ladder; predicts every slope stays above -0.500. 20-ep probes, ~15 min each.
* **`sc50-*-s{2,3,4}` (18, nice 50)** + s1 promoted -> n=5 on the ResNet50 rung.
* **`f5cos-r34-*` / `f5cos-r50-*` (12, nice 150).** The tuned non-meta baseline exists only at
  ResNet18 (94.093). Our best arm is 93.884 at **R34** -- currently a cross-architecture
  comparison. Until these land, no "wins/loses by X" sentence may name R34 or R50.
* **`r34r-r{0005,001,0015}` (9, nice 150) -- PRE-REGISTERED.** R34's optimum r=0.02 is the
  smallest non-zero point on its grid. Candidate law r* ~ 1/N (r*.N = 0.5M +-0.12M): predicts
  all three land below 93.884 and above 93.098; a peak at r<=0.01 refutes the 1/N form.
* **Cancelled `sw-cos-*` (21)** -- duplicate of the already-complete `fxcos-*` sweep.
* **Not touched: `kc-*` (39)** -- inspected first (30.0's lesson); it is the C100 M1 r-curve
  (R18_c100 to n=5, plus a new R10_c100 curve) and is the n>=5 follow-up to 32.6(d).
* Ops: throughput is still capped at 24 concurrent `gpu-short` jobs on a full cluster.
  `scontrol update Nice=` must EXCEED the job's accrued age (~700 points per half-day), not
  just beat the other job's nice -- see 32.10.

## Running / next (cycle 28)  -- queues: alice 299, alice2 250 = 549 jobs

**Cycle 28 found three more unreduced probe batches, and one of them inverts the mechanism.**
`gate1`/`gate2`/`gate3` (Aug 18, 33 dirs across both accounts) had zero mentions in FINDINGS
or CORRECTIONS. `gate2` is base **AdamW**, and its sign-agreement RISES with partition
fineness (m=6 71.20 -> m=62 79.96) where every SGDm batch in the campaign has it FALL
(`gate1`: 63.64 -> 54.69). 26.3's monotone fall is base-optimizer-specific, and that is the
mechanism H4 has been missing since cycle 12. See FINDINGS 28.4.

**Do not tabulate those numbers with 26.3's.** `gate1`/`gate2` predate the probe's `frac_neg`
field; the recovered `z_mean` statistic disagrees with the published one by 7.2pp at m=6.
Validated and recorded as CORRECTIONS 18. `gate3` is divergent (`sd_beta` 20.5) and excluded.

**Also this cycle:** `r10c-*` landed and the ResNet10 M1 interior optimum **disappears** at
a0=1e-3 -- the r-curve is monotone increasing over the whole grid and its best interior point
is 0.21pp BELOW plain layerwise, against a clean +1.00pp interior optimum at a0=1e-6 (28.5).
With 27.4 (R18: +2.40 -> +1.29) the a0-dependence of the M1 gain is now a pattern, and on
ResNet10 it goes to zero.

* **`ap-*` (9) + `ag-*` (27), alice2, submitted this cycle -- PRE-REGISTERED.** The AdamW
  agreement ladder in the modern probe format ({blk6, node, weight}; layerwise is the already
  queued `bp-adamw-s*`), plus the AdamW M1 r-curve that mirrors `sub_gp.sh` field for field
  with only the base changed. Predicts (a) the ladder inverts on `frac_neg` too, (b) the gain
  ladder therefore runs the opposite way to SGDm's. See FINDINGS 28.6.
* **`p7-*` (33) promoted to the front of alice**, `bp-*` (12) to the front of alice2. Both are
  20-epoch probe blocks; together they cost ~40 min of the 24-GPU allocation and they are what
  makes this cycle's contrast readable.
* `r34r-*` and `gp-*` rows are now in the CSV at 3-75 epochs -- IN FLIGHT, correctly excluded
  by the `epochs_done >= 100` filter. Do not read them yet.

## Running / next (cycle 26)  -- queues: alice 271, alice2 184 = 455 jobs

**Cycle 26 found the mechanism, in data that was already on disk.** Three probe batches had
never been reduced (`mx/probe_sig_*`, `p5scale`, `p6mech` -- 43 dirs, zero mentions in
FINDINGS or CORRECTIONS). Reducing `mx/probe_sig_*` (the only free-adaptation, 100-epoch,
dense-probe granularity series, config-matched to the 25.3 r-curve) gives:

| granularity | m | sign agreement | M1 pooling gain |
|---|---|---|---|
| resnet18_blocks | 6 | **70.87 ±0.80 %** | +0.415 |
| layerwise | 62 | **53.26 ±0.19 %** | +2.399 |
| nodewise | 14,420 | **51.03 ±0.12 %** | in flight (`gp-node-*`) |
| weightwise | 11,173,962 | **50.0053 ±0.0003 %** | +11.13 (zpool, 25.5) |

**Agreement falls monotonically with partition fineness and the pooling gain runs OPPOSITE
to it.** One mechanism for three previously unrelated results: 25.3's granularity-dependent
gain, 25.5's weightwise interior optimum, and 24.3's null on CIFAR-100. See FINDINGS 26.3.

Also this cycle: **the full-pooling identity is verified STRUCTURALLY at last** -- `p6mech`
shows `sd_beta` = exactly 0.0000 at r=0 on both seeds, and 2.47 at r=1 against plain
layerwise's 2.39 (26.4). Rule 4 satisfied; CORRECTIONS 13's open item closed.

* **`cw-*` (alice, 36) -- submitted this cycle. THE falsification test.** CIFAR-100 x
  {weightwise, nodewise} M1 r-curve, with agreement probes on the r=1 seed so gain and
  agreement come from the SAME run family. Pre-registered prediction: pooling is useless at
  C100/layerwise (already measured, 24.3) but LARGE at C100/weightwise. If it is not, 26.3
  dies. See FINDINGS 26.7.
* **`gp-node-*` / `gp-w-*` (alice2, 48) -- PROMOTED rank ~40 -> 25** by niceing `m0c-*` to
  30000. These supply the two missing cells of the gain column above and make it one run
  family instead of three.
* **`p6f-*` (alice, rank 1-9)** -- free-adaptation agreement on {C100, R10, R34} x
  {layer, node, weight}. Pairs with `mx/probe_sig_*` for the model-scale agreement ladder,
  which 25.6 predicts should FALL with model size.
* **`r34r-*` (alice, 27)** -- R34 r-curve; 25.6's third row is still one point.
* Niced to 30000: `m0c-*` (15, M0 shrink on CIFAR-100 -- raises a null 24.3 settled).

**Two corrections this cycle, both in the measurement layer, both recorded (CORRECTIONS
16-17):** `block_sizes.json` reports 11,173,962 coordinates for nodewise arms that have
14,420 (a 27.8x significance inflation if trusted); and `drift/step` is **censored** by
Lion's sign update at exactly the meta-stepsize, with two published `p4scale` slopes sitting
on that ceiling. The sqrt(N) refutation survives both (positive slope in 6/6 fits across two
alpha0); the slope magnitudes do not.

## Gotchas that cost hours — do not rediscover these
* **A probe directory with no `frac_zero` field is on the LEGACY statistic.** `gate1`/`gate2`
  carry only `beta`/`z_mean`/`z_std`/`snr`. `z_mean` is a per-TENSOR running mean (62 entries
  on every arm, including the 14,420-node and 11.17M-weight ones) and its agreement disagrees
  with the published `frac_neg` one by **7.2pp at m=6**. `analysis/agree_legacy.py` prints the
  same columns as `agree2.py` deliberately -- that makes the two easy to paste into one table.
  Do not. CORRECTIONS 18.
* **The Aug-18 `gate*` batches were STILL unread at cycle 27**, two cycles after the sweep
  that was supposed to catch exactly this. Sweeping by `find -name probe.jsonl` is not enough
  -- grep every top-level probe DIRECTORY name against FINDINGS and CORRECTIONS and reduce the
  ones that come back zero. Cycle 28 did that and found 33 dirs, one of which inverts 26.3.
* **Three probe batches sat unreduced for multiple cycles and one of them was the
  mechanism.** Before submitting ANY new probe run, sweep both accounts with
  `find <runs> -name probe.jsonl -size +1k` and grep every dir name against FINDINGS and
  CORRECTIONS. Cycle 26 found 43 unreduced dirs, including the only free-adaptation
  100-epoch granularity series in the campaign.
* **`block_sizes.json`'s `n_b` is WRONG for nodewise** (reports total params, 11.17M, for a
  14,420-node arm). Infer `n_tot` from the `frac_neg` rational denominators instead --
  `analysis/infer_ntot.py`. Verified against five independently recorded counts.
* **`drift/step` is censored at the meta-stepsize.** Lion's update is sign-based, so
  `|d beta|` per step is exactly `meta_stepsize`; `drift/step = 1.000e-03` means "pinned at
  the ceiling", not "very fast". Two published slopes were fitted through such a point.
  Normalise by the meta-stepsize before regressing.
* **`drift_extract2.py`'s window (steps 1000-7500) is the a0=1e-6 STARTUP transient** on any
  100-epoch run (50k steps). Use `analysis/agree2.py`, which reports a steady window (last
  50%) and startup separately.
* **Sign-agreement excess must be read against its own noise floor.** At n_tot=62 the
  per-record independence floor is 6.35pp, at n_tot=11.17M it is 0.015pp -- a 400x
  difference. Raw excess is NOT comparable across granularities without it.
* **`LAM=na` / `ETA_RATIO=na` KILL the job.** `HF.py` lines 24-25 `float()` both env vars
  unconditionally. `na` is what `run_cifar.sh` *echoes* for an UNSET variable, so healthy runs
  display it -- copying that into `--export=` cost 48 jobs. Non-hierarchical arms must export
  **none** of `HIER`/`LAM`/`ETA_RATIO`; under `HIER=additive` use `LAM=0`.
* **The `collapsed` column in `all_runs.csv` is `0` on EVERY row — it flags nothing.** One
  ResNet18/scalar/a0=1e-6 run plateaus at 20.5; it inflated that cell's sd to 14.16 and the
  reported granularity gain from +1.73 to **+4.60**. Filter `plateau > 50` explicitly until the
  aggregator is fixed. Audited cycle 23: this is the only affected cell in the CIFAR-10 plain
  ladder, and the additive r-curves have no collapses at all.
* **`resnet18_blocks` is ResNet18-only** -- `ZeroDivisionError` at `HF.py:175` on ResNet10/34
  (6 `sc-*-blk6` jobs died). Use `scalar`/`layerwise` on other architectures.
* **12 running per account IS the ceiling, not a bug.** Every non-`gpu-short` GPU node reports
  `AllocTRES` = its full GPU count (other users hold them); `qos-gpu-short` caps at
  `gres/gpu=12` per user. Confirm with `scontrol show node <n> | grep AllocTRES` before
  "fixing" anything. Negative `Nice` is denied, **but `scontrol update JobId=<j> Nice=0` on a
  previously-niced job IS accepted and is a large promotion** (cycle 24: `p6f` went 651704 ->
  671710, back of the queue to #2). You do NOT have to nice other blocks back to promote one.
* **Compare against a SCHEDULED baseline, not a constant-LR one.** AdamW+cosine 94.09 beats
  the best MetaOptimize arm 93.31; constant-LR AdamW 91.86 loses to it by 1.38pp. Which
  baseline you pick flips the sign of the headline method claim.
* **`r` in the additive hierarchy is RETENTION: r=1 = plain layerwise, r=0 = FULL pooling.**
  Three cycles quoted the M1 gain against r=0 as if it were the no-pooling control. See
  CORRECTIONS 13.
* **`bin/drift_extract.py`'s `spread` column is a verification that cannot fail** -- it reads
  `beta_true_max - beta_true_min`, which the probe writes identically on every arm. Use
  `bin/drift_extract2.py` (`sd_beta`) instead. Its `frac_neg` is also meaningless on scalar
  arms (1-element list -> it measures a time-fraction, not agreement).
* **The cluster's `analysis/aggregate.py` drifts stale.** It lost the
  `network`/`dataset`/`batch_size` columns; re-aggregating without pushing the repo version
  first silently drops every cross-architecture and cross-dataset claim. `scp` it before use.
* **Login-node python needs `module load Python/3.10.4-GCCcore-11.3.0` BEFORE
  `source envs/mo/bin/activate`**, else `libpython3.10.so.1.0: cannot open shared object file`.
* **CIFAR-100 is staged on BOTH accounts** (`.../cifar10/data/cifar-100-python`), and alice2's
  `build_network.py` supports `ResNet18_c100`/`ResNet34`. It is not single-account bound.
* Pending jobs at reason `(None)` are not held -- that is the scheduler's per-user evaluation
  depth (~top 100). Order the front of the queue; do not submit less.
* **`HIER=none` is TRUTHY and silently enables the hierarchy branch.** `HF.py` does
  `self._hier = os.environ.get('HIER','')` then `if self._hier:`. Existing `sc-*` runs log
  `HIER=none` **only** because `run_cifar.sh` echoes `${HIER:-none}` over an *unset* variable.
  Non-hierarchical arms must leave `HIER` **unset**. This nearly corrupted 18 control runs.
* **On alice2 the runner is `jobs/run_cifar.sh`** (already the s5014158 variant, with
  `/home/s5014158` paths baked in). `run_cifar_alice2.sh` exists only in the git repo, not on
  that account -- using that name gives `sbatch: error: Unable to open file`.
* **`sc50` = ResNet50, `sc101` = ResNet101 -- and R50 DOES finish inside `gpu-short`.**
  Measured cycle 24 from live TensorBoard scalars: ~44 epochs/hour, 100 epochs in ~2:20
  inside the 3:50 limit. The cycle-23 prose "31-34 epochs in 4h, needs a 7-day partition"
  was wrong and nearly cost six healthy running jobs. Read the event files, not the prose.
* **A running job's progress is readable without `probe.jsonl`.** `sc50` had no probe dir;
  `EventAccumulator` over `runs/<b>/Tensorboard_outputs/<run>/events*` gives the epoch count
  directly (`len(a.Scalars('Performance/train_accuracy'))`). Use it before cancelling anything.
* **`gpu-short` caps at 4:00:00** (`sinfo`); the other four GPU partitions allow 7 days. Use
  `--time=03:50:00` to stay eligible, and drop `gpu-short` for anything longer.
* **Check whether an "alpha0 control" already exists before submitting one.** `mx-a1e3-*` was
  an exact match to `sc-ResNet18-*` on every field but alpha0; 9 of 27 submitted jobs were
  redundant and had to be cancelled. Grep the CSV for the config, not the run-name prefix.
* Helper scripts go in `/data1/salehkaleybars/metaopt/bin`, **never `/tmp`** (node-local; the
  login nodes round-robin between nodelogin03/04, so scp'd files vanish between calls).
* Pattern that works: write locally → `scp` to that dir → `ssh alice 'bash <path>' 2>&1 | tail -N`.
  Filtering with `sed` over the SSH banner is unreliable; use `tail`.
* **Always** `--max-time 999:00:00` — `train.py` has its own truncation break that silently
  shortens runs.
* **Always** `--export=ALL,AUGMENT=1` — without augmentation ResNet-18 memorises CIFAR-10 in
  epoch 1 and the comparison is meaningless.
* `BETA_CLIP` uses a **colon** (`-15:-2.3026`); a comma breaks both the parser and `sbatch --export`.
* Pin GPUs: `--partition=gpu-l4-24g --gres=gpu:l4:1`. Mixing GPU types makes timing incomparable.
* A running job's `.out` shows **0 epochs** because Python buffers stdout. Read
  `PROBE_DIR/probe.jsonl` for true progress (`last_step / 500` = epochs). Three healthy jobs were
  killed on this misreading.
* Runs reproduce to ~**±0.02pp, not bitwise** (cuDNN autotuning). Effects under ~0.05pp need more
  seeds.
* **Reduce every probe dir that already exists BEFORE submitting new ones.** Cycle 18 found
  two complete, never-analysed drift series (`bdrift3/p3-*`, `bdrift4/p4-ad-*`); one of them
  downgraded a headline effect 16x and the other showed the headline has no mechanism. Sweep:
  `find <runs> -name probe.jsonl -size +1k`. Reducer: `bin/drift_extract.py` (validated -- it
  reproduces the published p2 table exactly).
* **`plateau` is the mean of the last 20 epochs, not 5** (code wins over prose; see
  CORRECTIONS 11). Filter `epochs_done >= 100` before comparing plateaus -- in-flight runs
  carry a plateau value that is not comparable.
* Pin GPUs **only** when timing matters. For epochs-to-target/plateau claims mix freely and
  always submit all five partitions; `gpu-short` caps at 4h so 300-epoch arms must omit it.
* Name new probe batches carefully: `p4-*` already existed on alice2 (`runs/bdrift4`) and was
  unrelated to cycle 18's `p4-*` on alice.
* ImageNet on `/data1` is **489 of 1000 classes** — scoped out; do not train on it and call it
  ImageNet.

## Standing instruction
Full autonomy was granted: decide and act, do not ask permission. The one thing that genuinely
needs the account holder is ImageNet credentials (and it is already scoped out).
