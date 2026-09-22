# ICML-PLAN — what paper could clear the ICML bar, and what must be run to get it

*Written 2026-09-21, cycle after CORRECTIONS 287. **Planning document only.** Nothing here is registered, nothing
was launched, no Slurm job was submitted, `alice` was not contacted, nothing under `paper/` was read. Every campaign
number below cites a committed file; every outside paper is one read by the synthesis inputs (arXiv/OpenReview/
proceedings pages, ids given). GPU-hour figures are **estimates** scaled from measured per-run costs
(`cwd5`: 27 runs = 18.2 GPU-h, CORRECTIONS 285.1; ResNet18 0.67, ResNet18_c100 0.70, VGG11_bn_c100 0.37,
PlainNet18_c100 0.65, ResNet18_tin 1.56 GPU-h per 100 epochs on L4, from `results/all_runs.csv`). None is registered.
The recorded entry is CORRECTIONS 288.*

***AMENDED 2026-09-22 at CORRECTIONS 289 (Step 0, zero GPU, descriptive): the registered `DOM_C` lead-lag cannot lead
the β turn by construction (disclosed as a finding about the test); on the FAIR event — the same-seed test gap to a
healthy partner — the accuracy deficit opens 700-1,700 steps BEFORE the turn on 15 / 15 pairs while β is identical in
both arms, so the decay dose acts first and **C1's causal "vote capture" framing is UNSUPPORTED (UNSURE, leaning
against)**; early N_eff does not separate collapsing from healthy runs (1.8's early form is dead). Changed here: C1's
thesis note, rows 1.5 / 1.8 / 1.19, Phase 0's N_eff bullet, Phase 1's Step 0 bullet and the gate rule.***

***AMENDED 2026-09-22 at CORRECTIONS 292 (zero GPU): the hostile area chair's corrections applied, and the naming fixed.***
*The chair's verdict, recorded rather than argued with: **no candidate below is an ICML accept as planned.** What changed
here because of it: two direct threats added to §1 (He et al. arXiv:1812.01187, Wu et al. arXiv:1803.02021) and
Defazio arXiv:2605.19095 §6.1 named as the prior art that pre-empts the broad story; B2, 1.16 and 3.1 retagged
**PARTIAL**; C2's thesis restated as "absent the collapse, scalar ≥ layerwise"; four missing experiments added (1.17-1.20);
the G1-led Phase 1 replaced by **Step 0 + the AdamW gate + G3** (§4); the gate's dominance criterion is now **`DOM_C`**,
not top-3 membership; Prodigy is out of the gate; the conditional ceiling lowered to **~10-15 %**. Every outside
citation added at 292 was checked on its arXiv abstract page (and, for the section-level claims, the arXiv/ar5iv HTML)
before it was written. No level, bar, contrast, stamp or licence sentence moved.*

***AMENDED 2026-09-22 at CORRECTIONS 297 (THE PATH DECISION, zero GPU, autopilot): THE GATE HAS RETURNED, AND IT CLOSES
C1 ON BOTH HALVES.** Step 0's clause was not met (289), and Step 1 does not fire: `caw2` (295) lands
`NO-COLLAPSE-CONTROL-DOSE-NOT-REACHED | M-COLLAPSE+L-NOGAP+A-NOGAP+X-NOGAP+K-COLLAPSED | ATTR-BASE-PROTECTS |
GATE-DOES-NOT-FIRE` — the harness's standard AdamW + Adam does not collapse at `ResNet18_c100` (`G_A` −5.1053 pp = −9.75
SE, NOGAP, a bound), the meta swap alone still collapses, the base swap alone does not (and cuts the realised shrink
~50×), and the dose arm reached only `RHO_X` 0.0591 of the control's shrink, so immunity at the control's dose is
UNDECIDED. G3 has landed too: `cgw1` (296) `AUDIT-UNDECIDED | SCALAR-BEATS-BEST | W1-SURVIVES+W2-SURVIVES+W4-UNDECIDED` —
the count-matched sign survives in batch at 0.1 (+0.3693) and 1e-2 (+0.4533), is undecided at 5e-4 (+0.2410, ±2 SE
[−0.0120, +0.4940]), and at 5e-4 plain scalar is above both partitions by 2.6–2.8 pp; W4's realised shrink is 115–883×
below a standard recipe's, so the decay-artefact question is NOT settled. **By §4's own rule, C1 is dead: the campaign
writes ONE paper, for TMLR — the count-matched audit with its headline rewritten, the denominator, and the collapse as a
bounded configuration-conditional section (C2 merged into C4). No ICML submission is planned.** The ranked live queue is
§4a below. Everything else in this file is kept as the history of the plan; where it disagrees with this paragraph,
this paragraph wins.***

***AMENDED 2026-09-22 at CORRECTIONS 309 + 310 (LANDING of §4a ranks 2 and 3, zero GPU): THE SCALAR ROW IS WEAKENED
TO A TIE; T-C IS EXCLUDED AS A SUFFICIENT RIVAL, FOR A CONSTANT γ.** `crt1` (309) lands `WEAKENED-TO-TIE |
TUNED-SCALAR-TIES-BEST | ORACLE-SCALAR-TIES-BEST`: after per-grain re-tuning of the meta step size and α0 over a
four-point grid at α-scaled 5e-4, every grain selects A2 (α0 1e-2, the grid edge), `cgw1`'s +2.6-2.8 pp closes to
T_ch +0.4487 / T_nd +0.6880 pp, and net of the selection bound B 0.1485 the chunk777 lead misses the 2 SE resolution
clause by 0.1078 pp — so the TMLR row is rewritten from "beats" to **"ties (a bound) after re-tuning"** (the registered
`LICENCE[WEAKENED-TO-TIE]`). It is NOT refuted (`HEADLINE-REFUTED-BY-RETUNE` not reached) and NOT robust; the branch
rests on the in-batch σ 0.2498 lying above the break-even 0.2014 (at the floor σ the rule would read
NOT-A-TUNING-ARTEFACT), and the grid did not locate any optimum. `csh1` (310) lands `HORIZON-DOES-NOT-REPRODUCE |
A-NOGAP+M-NOGAP+P-NOGAP`, the registered prediction: with the decay dose removed, neither the matched γ 0.999685 nor
the dominating γ 0.99941 collapses the scalar arm (G = −4.01 / −5.63 / −3.68 pp, scalar ahead), so short-horizon bias
through the trace (T-C, Wu et al. arXiv:1803.02021) is **not sufficient** for the collapse at this cell — a bound, for
a constant γ only, sufficiency not necessity; the learned horizon is `crd1`'s TR arm (307.7), not yet run. **What it
does to the ONE TMLR paper (310.10):** the audit headline keeps the count-matched sign at 0.1 with the 5e-4 interval;
the scalar row is restated as "untuned +2.6-2.8 pp; after re-tuning, a tie (a bound)", at this cell, with the α-scaled,
under-decay, grid-edge and σ-margin qualifiers, and is no longer stated as a win; the collapse section gains 310.8's
T-C sentence with its two bounds. The practical-significance qualification stands in weaker form (no audited
partition is resolved above scalar before or after re-tuning). Venue TMLR, unchanged; its 0.6-0.7 is a judgement, not
re-estimated. The joint ingest is `5db62be` (3,437 rows, 322 exclusions).*** *[CORRECTIONS 311: on the scalar row this paragraph governs over the 297 paragraph above; the untuned +2.6-2.8 pp travels with "at least in part, a tuning artefact" (309.8); α0 above 1e-2 is untested (grid edge), so the 0.6-0.7 is an un-argued judgement, UNSURE.]*

***AMENDED 2026-09-22 at CORRECTIONS 312 (LANDING of 1.14, zero GPU): THE AUDIT CELL IS RE-READ ON A HELD-OUT SPLIT;
THE PARTITION STATES CHANGE BUT NOT RESOLVABLY, AND VALIDATION SELECTS THE SAME CONFIGURATION.** `cvl1` (312) lands
`VAL-DIFFERS-UNRESOLVED | SELECT-SAME | W1-TUNDECIDED/VSURVIVES+W4-TUNDECIDED/VVANISHES+SC-TSCALAR-BEATS-BEST/VSCALAR-BEATS-BEST`
at `cgw1`'s cell (ms 1e-4, α0 1e-3; wd 0.1 and 5e-4; 45,000 training images; one 5,000-image split; four seeds).
Bounds first: ms and α0 were NOT re-selected (`MS-ALPHA0-NOT-RESELECTED`; ms 1e-4 is the one core-cell hyperparameter
known to be chosen on test, 302.1); the primary token hangs on one seed (dropping s187 gives `VAL-AGREES`); the modal
token licenses no sentence. Numbers: D_W1 TEST +0.2590 UNDECIDED / VAL +0.4330 SURVIVES, D_W4 TEST +0.1660 UNDECIDED /
VAL −0.0920 VANISHES (a bound), paired gaps +0.1740 / −0.2580 not resolved (paired SE 0.2012); SC SCALAR-BEATS-BEST on
both readers (16–17 SE), gap +0.2525 not resolved; both readers pick kLW1 (VAL margin +0.0940 pp). **Licences, as
registered:** "the change is not distinguishable from reader noise at this seed count; report both states and the paired
intervals; no sentence that the ranking does or does not hold on validation" and "selecting on validation would have
picked the same one, among these 8". **What it does to the ONE TMLR paper (312.10):** 1.14 closes for its RE-REPORTING
half at the audit cell only and stays OPEN for its RE-SELECTION half (tagged PARTIAL); the draft states that every audit
number is a TEST reading with ms chosen on test, reports `cvl1`'s states with their paired intervals and the selection
licence verbatim, and may not say any ranking holds (or fails) on validation. The scalar row stays "ties (a bound) after
re-tuning" (309; `cvl1` runs `crt1`'s untuned M2, 311 A5). Venue TMLR, unchanged; the 0.6-0.7 is not re-estimated. The
ingest is `5545d88` (3,469 rows, 354 exclusions).***

***AMENDED 2026-09-22 at CORRECTIONS 315 (LANDING of §4a rank 1, `g3b`, zero GPU): ON THE AUDIT's SECOND DATASET THE
0.1 SIGN REPRODUCES IN BATCH, THE 5e-4 CONTRAST IS UNREADABLE (BOX-BOUND), SCALAR BEATS BOTH PARTITIONS UNTUNED, AND THE
DENOMINATOR HOLDS WITH THE MetaOptimize ARM AT 5e-4.** `g3b` (315) lands `UNRESOLVED-BOXBOUND-W4 | SCALAR-BEATS-BEST |
DENOM-HOLDS | W1-SURVIVES+W4-BOXBOUND` at the audit's CIFAR-100 cell (`ResNet18_c100`, SGDm 0.99 + Lion, ms 1e-4, α0
1e-3; α-scaled wd 0.1 and 5e-4; four grains; four seeds). Bounds first: one CIFAR-100 cell, two rungs, never pooled
with `cgw1`; α-scaled decay only; 5e-4 is a nominal value (every W4 arm 38.9–709.8× below a standard recipe's shrink,
and up to 18.2× apart among the arms); the denominator is between batches with the SGD lr chosen on test (1.14); the
chunk771 W4 arm is box-bound on all four seeds (≤ 0.027 % of its groups at the upper edge from epoch ≈ 92), so the
registered 5 % box gate makes the primary unreadable; kLW4 is box-bound too; the scalar reading is `crt1`'s untuned M2
(311 A5); σ in-batch 0.431036, 57.6 % above the floor. Numbers: D_W1 **+1.2170** pp (+3.99 SE, SURVIVES,
`ANCHOR-MATCHES-POOL`); D_W4 +0.0645 [−0.5451, +0.6741], BOXBOUND; Tch / Tnd_W4 **+6.0345 / +6.0990** pp (19.8 / 20.0
SE); GAPch_W4 **+14.5857** pp (+44.61 SE; descriptively +5.71 at 0.1). **Licences, as registered:** primary "a
primary-rung partition arm is box-bound; the contrast is not an audit replication. Itself a fact: at 5e-4 the step sizes
reach the box."; scalar "… on this CIFAR-100 cell, no audited partition beats a single shared step size -- cgw1's reading
holds on the audit's second dataset." (cgw1's UNTUNED reading; its +2.6-2.8 pp travels with "at this cell cgw1's
+2.6-2.8 pp was, at least in part, a tuning artefact"); denom "… the denominator deficit is not an artefact of running
the MetaOptimize arm at 0.1 (ICML-PLAN 1.16), at this cell, between batches, with the SGD arm's lr chosen on the test
set (1.14)." **What it does to the ONE TMLR paper (315.10):** the 0.1 sign is now reproduced in batch on both datasets;
the 5e-4 partition question still rests on ONE readable cell (`cgw1`'s interval), and for CIFAR-100 the draft may state
only the box fact, no survive / vanish sentence; the scalar row gains the CIFAR-100 untuned +6.03 / +6.10 pp beside
`cgw1`'s untuned +2.6–2.8 pp and keeps "ties (a bound) after re-tuning" as its CIFAR-10 headline (tuning untested on
CIFAR-100, not refuted); **1.16 is PARTIAL — LANDED (315) for `cdn1`**: its κ confound is not supported in the
nominal-value form (lowering the MetaOptimize arm's decay widens the gap), a realised-decay match was not tested, and
`cau1` / `cuc1` were not re-run at 5e-4. Venue TMLR, unchanged; the 0.6-0.7 is not re-estimated. The ingest is
`4f7e191` (3,501 rows, 370 exclusions).***

***AMENDED 2026-09-22 at CORRECTIONS 317 + 318 (LANDING of the two α-independent batches, row 1.6, zero GPU): THE
COLLAPSE ROUTE IS THE α-SCALED WEIGHT SHRINK; AT THE AUDIT's CELL α-INDEPENDENT DECAY IS RUN AND UNREADABLE AT BOTH
STANDARD-RECIPE Λ, SO THE HEADLINE IS NEITHER CONFIRMED NOR REMOVED.** `crd1` (317) lands `ROUTE-IS-WEIGHT-SHRINK |
INDEP-NOGAP | S-COLLAPSE+T-NOGAP+I-NOGAP`, the registered prediction (prior 0.25): at the mechanism cell
(`ResNet18_c100`, wd 0.1) the α-scaled weight shrink with the trace factor dropped still collapses the scalar arm
(22.7653 against its own layerwise 70.0587, G +47.2933 pp, 3/3 seeds at the bar), the LEARNED trace factor with the
weights undecayed does not (G −3.4747 pp, scalar ahead), and α-independent decay at the onset-matched dose Λ 3.15e-4
collapses neither grain (G +0.6393 pp). Bounds first: sufficiency not necessity; S's trace keeps the direct term
−a·wd·w UNDECAYED, so no sentence may say "the shrink alone" (307.11); T's null rests on a reference only +5.2460 pp
above REF_MIN; ONE Λ, constant schedule, 13.37× the source's cumulative shrink, both I grains under-fitting
(TRAIN ≈ 71); no in-batch OFF anchor. **With `csh1` (307.7): T-C is excluded as a SUFFICIENT account in BOTH forms**,
the constant γ and the learned horizon, as bounds. `cai1` (318) lands `AI-UNREADABLE | SC-PARTIAL |
I5-BOXBOUND+I4-UNHEALTHY | I5-SCALAR-UNRESOLVED+I4-SCALAR-COLLAPSED` at `cgw1`'s own cell: at Λ 5e-5 all four grains
are healthy (90.13–90.77) but chunk777's step sizes reach the box on 7.0–7.4 % of records, so the registered 5 % gate
makes the rung unreadable; at Λ 5e-4 — a standard recipe's own per-step shrink, verified on all 320,000 records — every
arm is below HEALTH_MIN 85 (77.42–80.78). **`AI-SURVIVES` was not reached and neither was `AI-ARTEFACT-VANISHES` /
`-REVERSES` (the registered artefact prior 0.30).** **What it does to the ONE TMLR paper (317.10, 318.10):** the
collapse section gains the route sentence with its parenthesis, the two-form exclusion of T-C, and "a property of
α-scaled decay (PyTorch AdamW's default form), not of decay as such" — at this cell, with `ONE-LAMBDA` and the
rotational-equilibrium caveat; the audit headline is UNCHANGED and keeps its "at α-scaled decay" qualifier, with the
control recorded as RUN and UNREADABLE and its levels reportable; the scalar row stays "ties (a bound) after
re-tuning". **`DECOUPLED-NOT-TESTED` is retired for the COLLAPSE section at the mechanism cell only, and is NOT lifted
for the audit headline; row 1.6 is re-tagged PARTIAL — LANDED (317, 318).** Venue TMLR, unchanged; the 0.6-0.7 is not
re-estimated. The ONE ingest is `fecd462` (3,551 rows, 420 exclusions).***

> **NAMING (CORRECTIONS 292): the campaign's weight decay is "α-scaled", not "coupled".** The harness's base update
> is `delta = a*(m + wd*w)` and its meta trace is `h <- gamma*(1 - wd*a)*h - delta` (`patches/HF_patched.py`
> ~588-657, the same form for every base optimiser), so the decay is **multiplied by the learned step size**
> a = exp(β) and is added outside the momentum buffer and any preconditioner — the form PyTorch's `AdamW` uses by
> default, where the per-step shrink is lr·wd (here a·wd) — and it is **not** L2 regularisation, which is what a referee
> hears in the word "coupled". (With a plain-SGD base and no momentum the two forms coincide.) **Nor is it Loshchilov &
> Hutter's decoupled decay as they wrote it** (arXiv:1711.05101, ICLR 2019; this sentence corrected at CORRECTIONS 293,
> which struck 292's "In Loshchilov & Hutter's vocabulary that is decoupled, SGDW/AdamW-style decay"): their SGDW and
> AdamW (Algorithms 1-2) also apply the decay outside the gradient step and the preconditioner, but scale it by the
> **schedule multiplier η_t only, not by the step size α** — SGDW `θ_t ← θ_{t−1} − m_t − η_t λ θ_{t−1}` with
> `m_t ← β1 m_{t−1} + η_t α g_t`; AdamW `θ_t ← θ_{t−1} − η_t (α m̂_t/(√v̂_t + ε) + λ θ_{t−1})`. The harness shares their
> placement and not their scaling: its shrink moves with the LEARNED α, theirs does not (in form, the untested
> α-independent control below is their decay). The campaign's older word "coupled"
> only ever meant "multiplied by the learned α", so from CORRECTIONS 292 on this file says **α-scaled weight decay**
> (alpha-scaled), and the untested control, decay at a rate that does not move with α, is **α-independent weight
> decay**. Registered tokens, stamps and quotations keep their original spelling and are read through this
> definition: the stamp `DECOUPLED-NOT-TESTED` stays verbatim and means *α-independent decay not tested*, and quoted
> text that says "coupled" means α-scaled. **No number, bar, state, contrast or stamp changes with the name.**

---

## 0. The short answer

1. **The existing count-matched audit is not an ICML paper, and it now has a live threat.** Its effect is +0.5556 ±
   0.0448 pp (MASTER-TABLE line 175, CORRECTIONS 211.2), every audit cell ran at `--weight-decay-base 0.1`, and at the
   one rung where both grains were measured at standard decay the ranking reverses: scalar **72.4080** vs layerwise
   **67.8813**, `G_W4` = **−4.5267 pp = −8.59 SE** (CORRECTIONS 285, table line ~37612). Its right venue stays TMLR
   (STATUS.md ~1741-1747), **but it must be re-run at 5e-4 before it goes anywhere** (§4, gate G3). *(292: G3 now runs
   FIRST or alongside Step 1, not after the gate: plain scalar at 5e-4 (72.4080, `cwd5` `k01W4`) already lands at or
   above the audit's best partitions — **72.054** (`gm2` `chunk771`, 3 seeds) and 72.000 (`gm2` `chunk2293`), CIFAR-100
   ResNet18 SGDm+Lion at κ 0.1, re-derived at CORRECTIONS 293 from the raw `.out` files and `results/all_runs.csv`
   (292 quoted the chair's "72.41 / 72.00"; 72.41 is the scalar's own level, not an audit arm) — so the audit's
   +0.56 pp may itself be a κ 0.1 artefact. **Between-batch only:** 72.4080 (`cwd5`, seeds 146-148, meta step 1e-3,
   α0 1e-6, κ 5e-4) and 72.054 (`gm2`, seeds 0-2, meta step 1e-4, α0 1e-3, κ 0.1) are DIFFERENT BATCHES, so "scalar
   ties or beats the audit best" is orientation, not a contrast, until G3 puts both in one batch.)* *(297: G3 has put
   them in one batch on the CIFAR-10 core cell — `cgw1`, 296: D at 5e-4 is UNDECIDED and scalar beats both partitions
   by 2.6–2.8 pp, resolved, at the decay VALUE 5e-4 applied α-scaled. The audit goes to TMLR with its headline
   rewritten; it is the campaign's one paper.)*
2. **The one framing with a plausible ICML path** is a cross-method analysis paper: *"A step size shared across
   tensors is a magnitude-weighted vote; under step-size-scaled decay a few normalisation gains capture that vote, and
   whether finer granularity helps depends on the decay."* It is plausible **only if** the capture is shown in at
   least one adapter other than MetaOptimize, or at a standard setting (AdamW/Lion at κ = 0.1). Today it is shown in
   neither. That is the kill gate. *(292: the gate is now Step 0 + the AdamW cell + G3, §4; and Defazio
   arXiv:2605.19095 §6.1 already argues that learning-rate adaptation breaks weight decay, so only the per-tensor
   vote-capture part of this sentence is unclaimed.)* *(289: Step 0 finds the decay dose acting BEFORE capture —
   the same-seed accuracy gap leads the β turn by 700-1,700 steps on 15 / 15 pairs — so "capture … collapses
   training" is unsupported as a causal claim (UNSURE, leaning against); §2 C1 and §4 carry the consequence.)*
   *(297: CLOSED. Step 1 (`caw2`, 295) does not fire — at this cell the standard recipe does not collapse — so neither
   condition of the gate holds, and the ICML line is not pursued.)*
3. **The "parent's granularity result is a weight-decay artefact" claim is unsupported now and partly contradicted**
   by our own data (§3, C3). It is testable cheaply (≈28 GPU-h minimal) but must go through Dr Salehkaleybar first.
4. **Honest ceiling:** even if every gate passes, the paper has no ImageNet-1k (impossible, `docs/DATASETS.md`) and no
   language model unless Reza clears TinyStories. I put ICML acceptance at roughly **~10-15 %** conditional on the
   gates passing *(lowered at 292 from 15-25 %, on the area chair's attack: two direct threats and a pre-empting
   prior-art section were not priced in)*, and **under 5 %** unconditionally from today. The realistic best venue is **TMLR** for the
   audit + mechanism, with the vote-capture paper aimed at ICML only if Phase 1 passes. These probabilities are my
   judgement, not measurements.

---

## 1. What the ICML bar is (condensed from the synthesis inputs)

Sources read by the bar/guidelines stages: icml.cc 2026 Call for Papers, Reviewer Instructions, Author Instructions,
Peer Review FAQ; icml.cc 2025 Reviewer Instructions; the NeurIPS paper checklist. **No ICML 2027 call was found on
icml.cc; the deadline is UNSURE** (a third-party aggregator's 22 Jan 2027 is unverified).

| # | Bar item | Where it comes from | Campaign status today |
|---|---|---|---|
| B1 | A claim of general interest, not a corner case | Significance; "Reject" names weak/limited evaluation | **FAILING** — CORRECTIONS 285 itself concedes a corner case |
| B2 | Controlled manipulation, tuned per condition | peer analysis papers (Kunstner ICLR 2023, Crowded Valley ICML 2021) | **PARTIAL** *(retagged at 292; was "HAVE for the denominator")*: the MetaOptimize comparison arms of the denominator ran at α-scaled κ 0.1, where the scalar grain collapses, and nothing was re-tuned at 5e-4 (1.16, 1.18); the collapse itself is a 4-rung bracket |
| B3 | Breadth: >1 architecture family, incl. a transformer | every step-size method paper reviewed has an LM/transformer task (D-Adaptation arXiv:2301.07733, Prodigy arXiv:2306.06101, DoG arXiv:2302.12022, Mechanic arXiv:2306.00144, Schedule-Free arXiv:2405.15682, the parent arXiv:2402.02342) | **MISSING** transformer; HAVE ResNet/VGG/GN/PlainNet |
| B4 | Scale beyond CIFAR | same | PARTIAL: Tiny-ImageNet and IN-489 single batches (LIMITS-PREP §2.2); ImageNet-1k impossible |
| B5 | Mechanism with formal or toy-model support (for CNN-only analysis papers) | Lobacheva et al. NeurIPS 2021 (arXiv:2106.15739), Wu et al. ICLR 2018 (arXiv:1803.02021) | **MISSING** |
| B6 | Statistics: error bars defined, 3-10 seeds | NeurIPS checklist; peers | HAVE in-batch SE contrasts; seeds 3 (5+ wanted for sub-1-pp effects) |
| B7 | Novelty vs known results ("well-known results" = Strong Reject) | reviewer form | PARTIAL; see §2 prior-art threats |
| B8 | Honest scope / limitations section | CfP, checklist | HAVE (LIMITS-PREP.md) |
| B9 | Reproducibility + anonymised code | Author Instructions | PARTIAL: public repo `teshnizi2/hierarchical-metaoptimize` exists — anonymity handling **UNSURE**, decide before submission |
| B10 | No tuning on test | checklist norm | **MISSING**: every number is test-set `plateau5`; LR ladders argmaxed on test (CORRECTIONS 135.1) |
| B11 | Not substantially similar to a paper under review elsewhere | CfP dual-submission rule | Depends on the audit's TMLR timing; the ICML paper must be substantially different |

Prior art that pre-empts the **broad** "decay breaks step-size adaptation" story (all read as abstract/HTML pages by
the novelty stage): Defazio, ScheduleFree+, arXiv:2605.19095 §6.1 ("Learning Rate Adaptation Breaks Weight Decay");
Kosson, Messmer, Jaggi, ICML 2024, arXiv:2305.17212; Li, Zhou, Xu, arXiv:2607.21005; Amin, Chang, Khanna,
arXiv:2609.09116; Summers & Dinneen, arXiv:1906.03548; LARS, arXiv:1708.03888. **What none of them does**: attribute a
shared *meta-learned* step size's failure to per-tensor dominance of a summed vote by scale-*variant* normalisation
gains, with causal interventions, or measure the scalar-vs-finer gap as a function of decay. That is the unclaimed
ground.

**Threat list (added at 292, from the area chair's attack; each checked on its arXiv abstract page, and the section
claims on the arXiv/ar5iv HTML, before writing).**

| # | Paper | What it says (paraphrase) | Why it threatens us | What answers it |
|---|---|---|---|---|
| T-A | **Defazio, "ScheduleFree+", arXiv:2605.19095, §6.1 "Learning Rate Adaptation Breaks Weight Decay"** | Adapting the learning rate changes the gradient-to-weight-norm balance of normalised layers, which feeds back into the gradient norms — a loop the section says breaks learning-rate adaptation; it proposes an AdamC-style decay term with a squared learning rate | **Pre-empts the broad story** ("decay breaks step-size adaptation") in 2026, so C1 cannot claim it; what is left is the per-tensor vote capture and the granularity reversal | Frame C1 as a *mechanism inside* that loop for shared meta-learned step sizes; cite §6.1 as the known phenomenon |
| T-B | **He et al., "Bag of Tricks for Image Classification with CNNs", arXiv:1812.01187, §3.1 "No bias decay"** | The standard recipe applies weight decay only to conv and fully-connected weights and leaves biases and BN γ, β undecayed | **Direct threat**: the collapse needs decay on the BN scales (WRITEUP E8-E11, E19), which the standard recipe exempts, so our configuration is non-standard on two axes at once (κ 0.1 AND decayed 1-D tensors) | **1.17** — the standard-practice all-1-D exemption arm |
| T-C | **Wu, Ren, Liao, Grosse, "Understanding Short-Horizon Bias in Stochastic Meta-Optimization", arXiv:1803.02021 (ICLR 2018)** | Gradient-based meta-optimisation over short horizons systematically picks learning rates that are too small | **Rival mechanism**: the harness's trace is `h <- gamma*(1 - wd*a)*h - delta`, so α-scaled decay also **shortens the hypergradient horizon** to ~1/(κα) at γ = 1; a collapsed scalar step could be short-horizon bias, not vote capture | **1.20** — the short-horizon γ control (and 1.6's trace-only variant) |
| T-D | Kosson, Messmer, Jaggi arXiv:2305.17212; Li, Zhou, Xu arXiv:2607.21005; Amin, Chang, Khanna arXiv:2609.09116; Summers & Dinneen arXiv:1906.03548; LARS arXiv:1708.03888 | (as read at 288) | background to T-A | — |

**Naming.** See the definition at the top of this file: the harness's decay is **α-scaled** (placed like Loshchilov & Hutter's
decoupled decay, arXiv:1711.05101, outside the gradient step and the preconditioner, but multiplied by the learned
α = exp(β) where theirs is multiplied by the schedule multiplier η_t only; CORRECTIONS 293 corrected 292's "decoupled,
SGDW/AdamW-style, in Loshchilov & Hutter's vocabulary"), never "coupled"; the missing control is **α-independent**.
*(This paragraph replaced 288's "naming hazard" note, which said the same and cited `patches/HF_patched.py` ~592-598;
the decay term is in every base update, ~588-657.)*

---

## 2. Candidate papers

### C1 — "Vote capture": shared adaptive step sizes are magnitude-weighted votes *(analysis + diagnostic + small fix)*

> **Thesis:** "A step size shared across tensors follows a magnitude-weighted vote over their hypergradient terms;
> under α-scaled decay a few normalisation gains capture that vote and collapse training, and at standard decay the
> ranking reverses, so whether finer granularity helps is decided by the decay, not by the granularity."

> **289 (Step 0): the causal half of this thesis — "capture that vote and collapse training" — is UNSUPPORTED
> (UNSURE, leaning against).** Every observational ordering puts the decay's effect first: the same-seed test gap to a
> healthy partner sustains 0.5 pp 700-1,700 steps before the β turn and 1,100-2,100 steps before the first `DOM_C`
> record, on 15 / 15 pairs, with β identical in both arms; the carriers' magnitude (sign-free) exceeds the rest's only
> 200-500 steps AFTER the turn; and the same peak dose on CIFAR-10 (`cct1`, 4.7e-4) does not collapse. Not refuted —
> nothing held the vote while the dose ran. What survives is descriptive: dose → early deficit → a carrier-pivotal
> turn → capture → β pinned at the floor, with capture as a candidate LOCK-IN stage, not the onset. Any use of this
> thesis must be re-scoped to that, or wait for an intervention (e.g. `BETA_HOLD`, CORRECTIONS 237) that holds the turn.

* **Type:** analysis paper with a predictive diagnostic (effective number of voters, N_eff = 1/Σp_i²,
  p_i = |term_i|/Σ|term_j|) and a per-tensor-normalised vote as a small fix.
* **Why it could clear ICML:** the reviewer form explicitly credits "novel insights by evaluating existing methods";
  the campaign already has the causal evidence few analysis papers have (ISO +46.9307 pp = +62.10 SE, `ciso1`,
  CORRECTIONS 187; depth-matched control +0.1687, `cdep1`, 193; decay masks `cwd3`/`cwd4`, 278/283; the reversal
  `G_W4` −8.59 SE, 285); the unclaimed ground in §1 is real.
* **Why it might not:** if no second adapter shows capture it is a MetaOptimize note about one extreme setting (B1
  fails). Non-decreasing adapters (Prodigy, D-Adaptation, DoG) may be immune by construction, per Defazio
  arXiv:2605.19095. No ImageNet-1k; LM arm blocked on Reza's decisions; theory not yet written.
* **Relation to the audit draft:** disjoint content (the mechanism line is not in `paper.tex` @ 2f4fd9a per project
  memory), so no dual-submission conflict if the audit goes to TMLR. The audit's 1-D-tensor localisation becomes a
  *consequence* C1 can explain; do not re-use the audit's headline.
* **Relation to the parent / supervisor:** C1 does not need any claim about the parent. The parent's κ = 0.1 is cited
  as the setting the campaign inherited. Saber co-authors; the framing is "an extension of the parent's §9 open
  question", not a correction.

### C2 — "Decay decides granularity" *(analysis, MetaOptimize-specific)*

> **Thesis (restated at 292):** "For MetaOptimize, **absent the collapse, scalar ≥ layerwise**: the one regime in
> which the finer grain wins is the α-scaled-decay collapse at κ = 0.1, and there it wins because the scalar arm is
> broken, not because granularity helps."

*The 288 thesis ("layerwise wins by a floor-sized margin at κ = 0.1 and scalar wins at 5e-4, because a few BatchNorm
gains own the shared vote only when decay keeps their terms large") claimed a mechanism for the sign flip that the
data do not yet carry; the restated form claims only what the ladder shows and names what must hold for it: `G_W2`
is **not resolved** (−2.07 SE, 285), so "≥" rests on W3 and W4 on ONE network, and 1.7 (replication) and 1.18
(retune at 5e-4) are what would make it a result.*

* **Type:** analysis, single method. This is C1 with the cross-method section (and the fix) removed.
* **Why it could clear:** clean controlled manipulation with huge SE; the reversal is new.
* **Why it probably won't:** one method, CIFAR-scale, a corner-case setting by the campaign's own verdict (285).
  Likely a 3-4 ("limited evaluation") at ICML. Better as the **core of a TMLR mechanism paper**.
* **Relation:** it is the minimal viable subset of C1 and the natural fallback if the Phase 1 gate fails.

### C3 — "The parent's CIFAR-10 granularity advantage is conditional on κ" *(correction / follow-up)*

> **Thesis:** "At the parent's own Table 2 configuration, the blockwise-over-scalar advantage is present at κ = 0.1
> and absent at κ ≤ 1e-2."

* **Status: UNSUPPORTED and partly contradicted.** Verified facts:
  - The parent uses κ = 0.1 on every CIFAR-10 row including SGDm ρ 0.9 + Adam meta, α0 1e-6 (local text
    `~/.arxiv-mcp-server/papers/2402.02342.md`, Table 2, ~lines 3017-3057; SGDm-row column alignment UNSURE).
  - On the parent's own unaugmented AdamW+Adam setting at κ 0.1, blockwise-6 **74.352 ± 0.441** vs scalar
    **73.830 ± 0.253**, +0.522 pp, Welch t 2.52, with a β-clip guard caveat (`docs/CLOSEOUT.md` item 5a). No collapse.
  - ResNet18/CIFAR-10 at the campaign's SGDm(0.99)+Lion κ 0.1: 13 cells, ratio **0.962-1.001**, no collapse
    (`docs/LIMITS-PREP.md` §2.2 non-collapse table).
  - The only CIFAR-10 cell that collapses is SGDm+Adam at α0 1e-6: ratio 0.468 (clip none) / 0.783 (clip on),
    **seed-bimodal, 3 of 7 scalar seeds at 18-21 %** (same table) — at momentum 0.99, not the parent's 0.9.
  - The parent's ImageNet blockwise runs at κ 0.1 showed "no improvement over the scalar versions" (§7.3).
* **Why it can't be an ICML main-track paper:** the genre (a correction of one paper) is TMLR/reproducibility-track
  material, and even the strongest outcome covers CIFAR-10 SGDm only.
* **Sensitivity:** Saber co-authored the parent and wrote its implementation. **Nothing about the parent goes into
  any draft, preprint, the notebook site or any public channel until he has seen the data and agreed the wording.**
  Raise it privately as a scope question about the campaign's own finding. Best outcome: a joint section of C1 or a
  joint erratum-style note. Never the word "artefact" before the test lands, and probably not after.

### C4 — The existing count-matched partition audit *(TMLR, not ICML)*

> **Thesis:** "At matched group count, a uniform partition beats an architecture-aligned one in 20/20 cells
> (~+0.56 pp); alignment itself is a null; MetaOptimize loses to tuned SGD+cosine by 3.6-12.2 pp."

* **ICML:** STATUS.md's venue table already rates NeurIPS/ICML/ICLR main "poor, 0.15" and TMLR "best, 0.80". I agree.
* **New must-fix before TMLR:** the audit ran entirely at κ = 0.1. If the uniform-vs-aligned sign does not survive at
  5e-4, the headline becomes "a κ = 0.1 phenomenon" and must be rewritten. Gate G3 below serves the audit, not C1.
* **Venue fit, other:** ReScience/MLRC 0.60 (STATUS.md ~1742).

---

## 3. Required claims per candidate

Tags: **HAVE** (committed, cited) / **PARTIAL** (what is missing) / **MISSING**. **MUST** = needed to clear the §1 bar;
**NICE** = strengthens but not required. Costs are estimates (see header). "Reza" = needs his decision or licence
acceptance; "Saber" = needs the supervisor.

### C1 — Vote capture

| # | Claim | Status + evidence | Experiment that supplies it | Runs / GPU-h | New code | Decision needed | Bar |
|---|---|---|---|---|---|---|---|
| 1.1 | A shared MetaOptimize step size collapses at α-scaled κ 0.1 and not at 1e-2, 1e-3, 5e-4 | **HAVE** (one cell): `cwd5`, CORRECTIONS 285, scalar 23.22/69.35/72.50/72.41 vs layerwise 69.29/68.26/68.34/67.88 | — | — | — | — | MUST |
| 1.2 | The collapse is carried by term magnitude of a few tensors, and removing their decay removes it | **PARTIAL**: ISO (`ciso1`, 187), depth control (`cdep1`, 193), inject re-collapse on PlainNet (`cvt1`, 230), masks (`cwd3` 278, `cwd4` 283). Magnitude vs identity on ResNet unseparated; weight norms unmeasured | **O-13** magnitude/dose ladder on a ResNet non-carrier with onset control (WRITEUP-mechanism ~983); **O-2** weight-norm readout on the κ 0.1 arms | O-13 ≈ 10-13 GPU-h (WRITEUP's guess, UNSURE); O-2 ≈ 5 GPU-h + patch | O-13: existing `PATCH_VOTEWEIGHT`; O-2: read-only patch + inertness proof | O-2 flagged "a design question for the professor" (273.12) — Saber | MUST (O-13), NICE (O-2) |
| 1.3 | **Capture generalises beyond MetaOptimize** | **MISSING**: no Prodigy/D-Adapt/DoG/Mechanic/Baydin-HD run anywhere in docs (grep, novelty stage) | ResNet18_c100, κ {0.1, 5e-4}: Baydin HD (exact γ=0 case) scalar vs layerwise; Mechanic (can decrease) scalar; Prodigy (non-decreasing contrast) scalar; per-tensor attribution probe on each | pilot 24 runs ≈ 17 GPU-h; full (4 adapters × κ {0.1,1e-2,5e-4} × 2 grains where defined × 3 seeds) ≈ 60-72 runs ≈ 45-50 GPU-h | HD: ~10-line `SGD_meta_update`; Mechanic/Prodigy: pip in a **separate venv** + 30-60-line wrappers + inertness test; probe generalisation | pip install on alice2 login node (PyPI reachable) — Reza's go-ahead | **MUST**, but no longer the gate *(292: runs only after Step 1 fires; Prodigy is a scope contrast, not a gate arm)* |
| 1.4 | Capture happens at a *standard* setting | **MISSING**: AdamW/Lion bases never run on CIFAR-100 (LIMITS-PREP coverage table: AdamW 9 cells, all CIFAR-10) | T2: AdamW+Adam and Lion+Lion bases, ResNet18_c100, κ {0.1, 1e-2}, scalar vs layerwise, 3 seeds (κ 0.1 is the parent's standard for these) | 24 runs ≈ 17 GPU-h | none (flags exist) | registration | **MUST**; its AdamW cell at the usual decay is now **Step 1, the gate** *(292)* |
| 1.5 | The transition is *located*, and expressed on the realised per-step shrink α·κ | **PARTIAL**: bracketed in (1e-2, 0.1) only (285, `LADDER-IS-FOUR-POINTS`); **(a) DONE at 289**: collapse peak α·κ 5.45-5.56e-4 (`cwd5` W1, `cmo1`, `ctd1`), healthy W2 1.6e-4, W4 2.4e-5; AdamW CIFAR-10 cells 3-5e-5 (not the same dose as SGDm at κ 0.1); `cct1` CIFAR-10 carries 4.7e-4 and does not collapse (dose not sufficient alone) | (a) zero-GPU T0: compute α·κ from committed probe β records for every `cwd5` rung and the AdamW C10 cells; (b) κ {0.02, 0.03, 0.05} × 2 grains × 5 seeds | (b) 30 runs ≈ 21 GPU-h | none | registration | MUST |
| 1.6 | The route is identified: weight shrink vs meta-trace, and α-independent decay | **PARTIAL — LANDED (CORRECTIONS 317, 318)**: patch `PATCH_DECAYROUTE` PROVED (305, job 5081090, 410/0); **`crd1`** (317) lands `ROUTE-IS-WEIGHT-SHRINK | INDEP-NOGAP` at the mechanism cell (18 jobs 5081273–5081290, 11.66 GPU-h by `sacct`) — the α-scaled weight shrink is SUFFICIENT for the collapse (with its undecayed direct term, 307.11), the learned trace factor is not, and α-independent decay at Λ 3.15e-4 collapses neither grain, so the collapse needs the decay to move with α; **`cai1`** (318) lands `AI-UNREADABLE | SC-PARTIAL` at the AUDIT cell (32 jobs 5081292–5081323, 35.49 GPU-h) — both Λ rungs unreadable (I5 through the 5 % box gate, I4 through health), no partition reading under α-independent decay there.  **`DECOUPLED-NOT-TESTED` is retired for the collapse section at the mechanism cell only; for the audit headline the control is RUN and UNREADABLE, not lifted** *[was: MISSING — LAUNCHED, NOT LANDED (cycle-5 audit); `DECOUPLED-NOT-TESTED` STANDS until both land]* | 3 variants at κ 0.1 on ResNet18_c100: shrink-only, trace-only, α-independent (matched on initial per-step shrink) × 2 grains × 3 seeds | 18 runs ≈ 13 GPU-h | 40-80-line opt-in patch like `PATCH_DECAYMASK` + inertness proof | registration | MUST (reviewers will ask) |
| 1.7 | The reversal (scalar > layerwise at 5e-4) replicates | **PARTIAL**: one network, 3 seeds (`G_W4`, 285) | PlainNet18_c100, VGG11_bn_c100, ResNet18/CIFAR-10 at κ 5e-4 (+0.1 anchor) × 2 grains × 5 seeds | 60 runs ≈ 35 GPU-h | PlainNet in isolated trees only; probe hard-codes 62 tensors | registration | MUST |
| 1.8 | N_eff predicts collapse early, out of sample | **(a) FAILED at 289**: early N_eff (epochs 1-5) overlaps on every paired cell (`cwd5` W1 3.21/3.09/3.50 vs W4 3.17/3.05/3.47); best single cut 47/171 vs base rate 53/171 — the Phase 0 soft gate is met, the early-diagnostic form is dead; (b) not attempted | (a) zero-GPU: compute N_eff from committed per-tensor probes (`ctd1`, `cct1`, `cwd5`) — does early N_eff separate C100 vs C10 and κ 0.1 vs 5e-4? (b) pre-register it on the new Phase-2 cells | (a) 0; (b) rides on other batches | analysis script only | — | MUST (it is the "insight") |
| 1.9 | A normalised-vote fix removes the collapse and loses nothing at 5e-4 | **MISSING** (earlier pooling designs M0/M1/zpool failed their controls, PRIOR-ART) | per-tensor-normalised (or median) vote × κ {0.1, 5e-4} × {ResNet18_c100, PlainNet, VGG, R18/C10, Tiny-ImageNet} × 3-5 seeds, vs scalar and layerwise, plus the tuned SGD+cosine row for context | ≈ 40-50 runs ≈ 35-40 GPU-h | new aggregation patch + proof | registration | NICE (MUST if framed as a method) |
| 1.10 | Holds on a transformer | **MISSING** | small ViT on CIFAR-100 (torchvision 0.15.2 builds it; 13 LN scales, 52 1-D tensors), AdamW base, κ {0.1, 1e-2}, LN gains decayed vs exempt, 2 grains, 3 seeds. A null is publishable scope | 24 runs; cost **UNMEASURED** (smoke job first; guess ≤ 1 GPU-h/run) | `--NN-name` entry, probe generalisation, augmentation/epoch recipe | registration | **MUST** for ICML (B3) |
| 1.11 | Holds on a language model | **MISSING, BLOCKED**: llama2.c on alice2 is code-only, hard-coded data path, no sentencepiece, its HF.py crashes at layerwise (feasibility; OPERATIONS §11) | TinyStories ~15M (the parent's own setup), AdamW, κ {0.1, 1e-2}, 2 grains, 3 seeds | 24 runs; cost UNMEASURED | LARGE: port granularity/guard/probe patches, re-stage ~7 GB | **Reza**: TinyStories licence (CDLA-Sharing-1.0), tokenizer licence UNSURE, staging | NICE on this cluster (the ViT stands in); MUST in an ideal paper |
| 1.12 | Scale beyond CIFAR | **PARTIAL**: Tiny-ImageNet 9.86 vs 50.83, IN-489 1.00 vs 49.21, single batches (LIMITS-PREP §2.2) | Tiny-ImageNet, κ {0.1, 5e-4}, 2 grains, 3 seeds, with attribution probe | 12 runs ≈ 19 GPU-h (7-day partition) | none | — ; ImageNet32/64 would need Reza's image-net.org login | MUST (Tiny-ImageNet); NICE (ImageNet32) |
| 1.13 | A toy model predicts the threshold | **MISSING** | analytic: noisy quadratic (Wu et al.) + one scale-variant gain group under α-scaled decay and a Lion/sign meta-vote; predict the capture threshold in α·κ and check against 1.5 | 0 GPU; ~1-2 weeks of Reza/Saber time | — | Saber (theory ownership) | MUST (B5) |
| 1.14 | Validation-split reporting | **PARTIAL — LANDED (CORRECTIONS 312)** as `cvl1` at the audit cell: `VAL-DIFFERS-UNRESOLVED \| SELECT-SAME` — re-reporting half answered (no sentence either way on the partition ranking; SC same state on both readers; validation selects the same configuration among 8); re-selection half (ms, α0 on validation) NOT done, `MS-ALPHA0-NOT-RESELECTED` *[was: **MISSING** (CORRECTIONS 135.1)]* | 45k/5k split, re-select and re-report the headline cells (1.1, 1.3-1.4, 1.7, 1.9) on validation | ≈ 30 runs ≈ 21 GPU-h | split flag in the loader (small) | registration | MUST (B10) |
| 1.15 | 5+ seeds on every load-bearing contrast | **PARTIAL** (3 seeds) | top-ups folded into 1.5/1.7/1.9; plus 2 seeds on 1.1 | ≈ 20 runs ≈ 14 GPU-h | none | — | MUST for sub-1-pp effects; NICE for 40-pp effects |
| 1.16 | Practical context: tuned non-meta baseline | **PARTIAL — LANDED (CORRECTIONS 315) for `cdn1`** as `g3b`'s chW4 arm (`cdn1-m`'s configuration at α-scaled 5e-4, 4 seeds): `DENOM-HOLDS`, GAPch_W4 +14.5857 pp (+44.61 SE, between batches; descriptively +5.71 at 0.1), so for the CIFAR-100 denominator the κ confound is not supported in its nominal-value form; a realised-decay match was not tested, the SGD lr was chosen on test (1.14), the 5e-4 arm runs the 0.1-tuned ms / α0 and is box-bound; `cau1` and `cuc1` were not re-run at 5e-4 *[was: PARTIAL, as follows]* **PARTIAL** *(retagged at 292; was HAVE)*: `cdn1` +5.699 pp = +18.80 SE (171/175), `cau1` +3.617 = +9.92 SE (209), `cuc1` +12.178 = +26.05 SE (220) — but every MetaOptimize arm in those contrasts ran at α-scaled κ 0.1, so the denominator is not yet separated from the κ 0.1 configuration | re-run the MetaOptimize comparison arm at κ 5e-4 (the `cdn1` arm ran at 0.1) — cheap, removes the wd confound | 6 runs ≈ 4 GPU-h | none | — | MUST (fairness) |
| 1.17 | **Standard-practice exemption** (He et al. §3.1, threat T-B): with ALL 1-D tensors (biases, BN γ and β) undecayed, does the collapse exist at κ 0.1, and is scalar ≥ layerwise at 5e-4? | **MISSING** (`cwd1` masked the 20 BN scales only, 271) | ResNet18_c100, κ {0.1, 5e-4}, `DECAY_MASK` = the explicit list of every 1-D parameter (the existing `<name>+<name>` form, derived on the LIVE model), 2 grains, 3 seeds | 12 runs ≈ 8.4 GPU-h (0.70/run) | none if the name list fits the one-token `--export` limit — UNSURE, check at registration | registration | **MUST** |
| 1.18 | **Retune at 5e-4**: the mechanism cell's meta step 1e-3 and α₀ 1e-6 were chosen at κ 0.1; is the 5e-4 ranking robust to re-tuning each grain? | **MISSING** | ResNet18_c100, κ 5e-4, meta step {3e-4, 1e-3, 3e-3} × 2 grains × 3 seeds, each grain's best reported | 18 runs ≈ 12.6 GPU-h | none | registration | **MUST** (B2) |
| 1.19 | **Lead-lag**: does the carriers' vote share (and the realised shrink α·κ) move BEFORE the scalar arm's accuracy falls, or after it? | **DONE at 289 — CAPTURE LAGS.** The `DOM_C` onset test is structurally uninformative (its sign clause is false on every late-ascent record, 3,392 / 3,392 pre-turn records have s = −1); the collapsed runs never "fall" (FALL undefined 39/39); on the fair event (same-seed gap to a healthy partner, sustained ≥ 0.5 pp) the accuracy deficit leads the β turn by 700-1,700 steps on 15/15 pairs, while a·κ is 1.1-3.0e-4 | zero GPU: from committed per-record probes (`cwd5` W1 arms, `ctd1`, `ciso1` `k01`), time of DOM_C onset vs time of the accuracy/β drop, per seed | 0 GPU | analysis script only | — | **MUST** (Step 0): if capture LAGS the collapse, it is a symptom and C1's causal framing dies |
| 1.20 | **Short-horizon γ control** (Wu et al., threat T-C): does shortening the hypergradient horizon WITHOUT decay reproduce the collapse? | **MISSING** | ResNet18_c100, κ 5e-4, γ chosen so γ matches the realised (1 − κα) of the κ 0.1 scalar arm (from Step 0), plus γ = 1 anchor, 2 grains, 3 seeds | 12 runs ≈ 8.4 GPU-h | none (`--gamma` exists; the cell runs `--gamma 1`, read from `cwd5`'s ARGS lines) | registration | **MUST** (rival mechanism) |

### C2 — Decay decides granularity

Required claims = C1 rows **1.1, 1.2, 1.5, 1.6, 1.7, 1.8(a), 1.12, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 1.20**, all as
costed above (1.17-1.20 added at 292, ≈ 29 GPU-h together). Drops 1.3,
1.4, 1.9, 1.10, 1.11, 1.13. Adds: none. **Cost ≈ 180-200 GPU-h** *(was 150-170 before 1.17-1.20)*. Ceiling: TMLR strong; ICML weak (B1, B3 fail).

### C3 — Parent-conditional claim

| # | Claim | Status + evidence | Experiment | Runs / GPU-h | New code | Decision | Bar |
|---|---|---|---|---|---|---|---|
| 3.1 | The parent measured granularity only at κ = 0.1 | **PARTIAL** *(retagged at 292; was HAVE)*: parent Tables 2-4 (local text); PAPER-CONFIG.md; CORRECTIONS 254 — the tables show κ = 0.1 on every row reported, but the SGDm-row alignment is UNSURE and whether other κ were run and not reported is unknown; only Saber can close it | — | — | — | Saber to confirm SGDm-row alignment | MUST |
| 3.2 | At the parent's exact SGDm row, blockwise − scalar at κ 0.1 is resolved | **MISSING** (the exact row, ρ 0.9 + Adam meta on CIFAR-10, was never run) | P1-min: CIFAR-10, ResNet18, bs 100, AUGMENT=0, SGDm 0.9 + Adam, α0 1e-6, η 1e-3, γ 1, wide β box −60:6.0; scalar vs `resnet18_blocks` × κ {0.1, 1e-3} × 5 seeds; same for AdamW+Adam | 40 runs ≈ 28 GPU-h | none (flags exist; `resnet18_blocks` = [3,12,15,15,15,2] in `HF_patched.py` ~215 — whether it equals the parent's six blocks is UNSURE, same code lineage) | **Saber first**; registration | MUST |
| 3.3 | The gap shrinks/reverses at low κ (interaction I resolved) | **MISSING** | P1-full: + (Lion, Lion), (RMSprop, Adam), κ {0.1, 1e-2, 1e-3}, 5 seeds | 120 runs ≈ 83 GPU-h | none | Saber | MUST |
| 3.4 | The β-clip floor did not manufacture the gap | **PARTIAL**: CLOSEOUT 5a guard caveat (1.184 nats above the floor) | covered by the wide box in P1, plus the 9-job `BETA_CLIP=-15:0` control CLOSEOUT names | 9 runs ≈ 6 GPU-h | none | — | MUST |
| 3.5 | The parent's epoch count, seeds and Fig. 1 pairings are known | **MISSING** (§7.1 states no seeds, no error bars — PAPER-CONFIG.md) | ask Saber | 0 | — | Saber | MUST |
| 3.6 | ImageNet rows | **IMPOSSIBLE** here; Tiny-ImageNet proxy P2 can only confirm a null | 36 runs ≈ 45-55 GPU-h; 6-block partition for ResNet18_tin may need code | small | — | NICE |

**A-priori prediction from existing data:** (AdamW, Adam) and (Lion, Lion) show no κ dependence; (SGDm, Adam) is the
only live candidate. If P1 finds no interaction, the claim dies and becomes the scope sentence *"the collapse does not
reach the parent's CIFAR-10 cells"* — which C1 needs anyway.

### C4 — Audit to TMLR (for completeness; not ICML)

| # | Claim | Status | Experiment | Runs / GPU-h |
|---|---|---|---|---|
| 4.1 | Uniform > aligned at matched count, 20/20 | HAVE at κ 0.1 (211.2) | — | — |
| 4.2 | **…and it is not a κ = 0.1 phenomenon** | **MISSING** — and now urgent: plain scalar at 5e-4 (72.4080, `cwd5` `k01W4`) lands at or above the audit's best partitions (**72.054** `gm2` `chunk771` / 72.000 `gm2` `chunk2293`, re-derived at CORRECTIONS 293; 292's "72.41" was the scalar's own level) — a DIFFERENT BATCH, so between-batch orientation only until G3 lands | G3: core count-matched cells (chunk vs nodewise at two counts; ResNet18 on CIFAR-10 and CIFAR-100; SGDm+Lion) × κ {5e-4, 1e-2} × 3 seeds, plus scalar/layerwise in batch | 24-36 runs ≈ 17-25 GPU-h |
| 4.3 | Stale sentences ("1.8-4.2 pp", "none of nine mechanisms") updated | PARTIAL (project memory) | writing only | 0 |

---

## 4. Ranking and recommendation

Scores are my judgement: P = probability the experiments deliver an ICML-quality result; V = value if they do
(1-5); C = GPU-h + calendar cost.

| Rank | Candidate | P(ICML-quality result) | Value | Cost (GPU-h) | P×V/C (relative) | Verdict |
|---|---|---|---|---|---|---|
| 1 | **C1 vote capture** | ~0.15 (gated on Step 0 + the AdamW cell; lowered at 292) — *289: Step 0's clause failed and the causal thesis is unsupported, so this figure now applies only to a re-scoped, descriptive C1 and is an upper bound (judgement, not re-estimated)* | 5 | ~430-480 + theory | **highest**, because Phase 1 is cheap and decisive | ~~PRIMARY~~ **CLOSED at 297** (Step 0 not met, 289; Step 1 does not fire, 295) |
| 2 | C2 absent the collapse, scalar ≥ layerwise | ~0.10 for ICML; ~0.7 for TMLR | 3 | ~180-200 | medium | ~~FALLBACK~~ **MERGED INTO C4 at 297** (the collapse becomes the audit paper's bounded configuration-conditional section; not written standalone) |
| 3 | C4 audit | ~0.05 ICML; 0.8 TMLR (STATUS) | 2 | ~20-25 (G3) | high for TMLR, n/a for ICML | **THE CAMPAIGN's ONE PAPER at 297** — G3 has landed (`cgw1`, 296); TMLR with the headline rewritten (CORRECTIONS 296.7-296.8, 297.2) |
| 4 | C3 parent-conditional | not an ICML paper; ~0.3 that P1 even shows an interaction | 2 (high sensitivity) | 28-83 | low standalone | fold into C1 **only** with Saber's agreement |

### Phased plan

**Phase 0 — zero GPU, ~1 week (do first; nothing needs registration).**
- T0: realised per-step shrink α·κ from committed probe β records (`cwd5` rungs, AdamW C10 cells). Tells us whether
  "κ 0.1 on SGDm" and "κ 0.1 on AdamW" are the same dose at all.
- N_eff from committed per-tensor probes (`ctd1`, `cct1`, `cwd5`). If early N_eff does **not** separate collapsing
  from healthy runs, the diagnostic contribution (1.8) is dead and C1 loses its central insight — a soft gate.
  **289: MET — early N_eff does not separate (every pair overlaps; 47/171 misclassified at the best cut, base rate
  53/171). 1.8's early-diagnostic form is dead.** T0 (the shrink) is also done at 289 (1.5 row).
- Prior-art sweep (standing memory rule) focused on arXiv:2605.19095 §6.1 and anything newer on shared/global
  step-size adaptation × normalisation × decay; then Reza's go-ahead.
- Meet Saber: parent epochs/seeds/Fig. 1 pairings, any other κ ever run, Table 2/4 SGDm alignment, whether he wants
  P1, and who owns the toy-model theory (1.13).
- Decide the TMLR timing of the audit (dual-submission) and the public-repo anonymity question (B9).

**Phase 1 — REPLACED at 292 by the area chair's cheapest decisive gate: Step 0 + the AdamW cell + G3.** *(The 288
version led with G1, a three-adapter cross-method pilot needing new code and a pip install. The chair's point: that is
neither the cheapest nor the most decisive first move, and top-3 membership is the wrong dominance test. These three
now run as **CORRECTIONS 289-291**, registered by concurrent tracks; which number is which, and their status, is in
those entries — none of them had reached `origin/master` when this was written.)*
- **Step 0 — zero GPU.** (a) The **realised per-step shrink** α·κ from committed probe β records, for every `cwd5` rung
  and the AdamW CIFAR-10 cells (1.5a); (b) the **lead-lag check** (1.19): does `DOM_C` onset precede the scalar arm's
  fall? If capture lags the collapse, C1's causal framing is dead before any GPU is spent.
  **DONE at CORRECTIONS 289 (zero GPU).** (a) Collapse peak α·κ 5.45-5.56e-4; AdamW CIFAR-10 3-5e-5. (b) The
  registered `DOM_C` lead-lag is **structurally biased toward "lag"** — `DOM_C` needs the carriers' sum to carry the
  APPLIED sign, which is −1 on every ascent record while the carriers push +1, so it cannot be true before the turn;
  its "lag" is uninformative and is not used. The accuracy "fall" does not exist (the collapsed runs plateau near 23 %).
  On the **fair event** (same-seed test gap to a healthy partner, sustained ≥ 0.5 pp) the deficit opens **700-1,700
  steps before the β turn on 15 / 15 pairs**, with β identical across the pair and before any `DOM_C` record;
  healthy-vs-healthy null pairs never sustain 0.5 pp before epoch 41. **Capture lags the collapse's onset.**
- **Step 1 — one standard-recipe cell.** AdamW base at its usual decay, ResNet18_c100, scalar vs layerwise, 3 seeds
  (a subset of 1.4; decay value and meta settings fixed in that registration, not here). It asks the question that
  decides everything else: **is the collapse a hazard at a standard recipe, or a corner case of SGDm(0.99) at κ 0.1?**
- **G3 — first or alongside, not after.** The count-matched audit's core cells at standard decay (4.2). Every audit
  cell ran at κ 0.1, and plain scalar at 5e-4 (72.4080) already lands at or above the audit's best partition (72.054,
  `gm2` `chunk771`; a different batch, so between-batch orientation only until G3 lands), so the audit's +0.56 pp may
  itself be a κ 0.1 artefact. G3 serves the TMLR paper and must not wait on the ICML gate.
- **Gate rule (to be pre-registered with frozen literal bars):** continue C1 **iff** Step 1 shows the scalar arm
  collapsing (R ≤ 0.50 against its own in-batch layerwise arm) **and** the declared carrier set dominating the shared
  vote by **`DOM_C`** — `sign(Σ_C L_i)` equals the applied sign **and** `|Σ_C L_i| > Σ_{i∉C} |L_i|`, the criterion
  defined at CORRECTIONS 256 — on ≥ 0.50 of its scalar records, with C fixed from early records before the rest are
  read; **and** Step 0's lead-lag does not show capture lagging the collapse. ***289: this third clause is NOT MET.***
  *On the fair event capture lags the onset, and the `DOM_C`-onset form of the test cannot answer the question at all
  (289.3), so no future `DOM_C`-onset result can satisfy this clause either. Autopilot decision recorded at 289.6:
  C1 does not continue as a CAUSAL "vote capture" paper on this gate, whatever Step 1 shows. Step 1 still runs: it
  decides "hazard vs corner case" for C2/C4 and for a re-scoped, descriptive C1 (capture as the lock-in stage), which
  would additionally need an intervention that holds the turn while the dose runs (e.g. `BETA_HOLD`, 237) before any
  causal sentence is written. UNSURE whether that re-scoped C1 clears ICML; on present evidence, likely not.* **Top-3 membership is not the test**: at
  `cct1` the carriers were top-3 on 69 % of CIFAR-10 records with `DOM_C` = 0 on all 1,500 and no collapse (265), so
  top-3 can fire where nothing is captured. **If Step 1 does not fire, C1 is dead**: write C2 + C4 for TMLR and stop
  spending on ICML scope (1.10, 1.11, 1.13).
  ***297: Step 1 did NOT fire (`caw2`, CORRECTIONS 295: `GATE-DOES-NOT-FIRE`). This rule is applied: C1 is dead; C2 is
  merged into C4 for TMLR; 1.3, 1.9, 1.10, 1.11, 1.12 (at ICML scope) and 1.13 are stopped. 1.14 stays open, unranked.***
- **G1 (cross-method) moves after the gate** and only if Step 1 fires: Baydin HD and Mechanic (adapters that can
  decrease the step size), with the same `DOM_C` criterion. **Prodigy is dropped from the gate**: a non-decreasing
  adapter is immune by construction (Defazio arXiv:2605.19095's framing), so it can only fail to fire; it stays in
  Phase 2 as a scope contrast, not as a gate arm.
- G2's Lion+Lion half and the rest of 1.4 move to Phase 2.

**Phase 2 — build the paper, ~4-6 weeks, ≈ 330-380 GPU-h** (only if Phase 1 passes). In order: 1.17 all-1-D
exemption; 1.20 short-horizon γ control; 1.18 retune at 5e-4; 1.6 route patch; 1.5
located boundary; 1.7 reversal replication; 1.3 full cross-method; 1.10 ViT (smoke job first); 1.12 Tiny-ImageNet;
1.9 fix; 1.14 validation re-report; 1.15 seed top-ups; 1.16 κ-matched denominator arm; 1.2 O-13 (+ O-2 if Saber
agrees). P1 (C3) in parallel only on Saber's say-so. Theory (1.13) in parallel, human time.

**Phase 3 — optional, Reza-gated:** TinyStories LM arm (1.11); ImageNet32 (image-net.org terms, his login).

**Totals (estimates, not registered; re-summed at 292):** Step 0 = 0; Step 1 + G3 ≈ 20-30 GPU-h; G1 ≈ 17 if the gate
fires; Phase 2 ≈ 330-380 GPU-h; P1 +28-83; overall **≈ 430-540 GPU-h, ≈ 600-750 runs**. alice2 delivered 301-545 GPU-h/week recently (sacct, feasibility stage), so GPU
is ~1-1.5 weeks of throughput; the real pacing limit is patches, inertness proofs and registrations (~40 jobs/night,
LIMITS-PREP §5.5). **Calendar: ~7-9 weeks of experiments + ~3-4 weeks of writing ≈ 10-13 weeks from go-ahead**, i.e.
late December 2026 at the earliest. Against an unverified late-January ICML 2027 deadline that is feasible but has
little slack; the theory item and the ViT recipe are the schedule risks.

### 4a. THE LIVE QUEUE (CORRECTIONS 297) — at most three, ranked; **all three REGISTERED AND LAUNCHED 2026-09-22 (299–301), plus 1.14 (`cvl1`, 303) and the two α-independent batches (`cai1` 306, `crd1` 307); ranks 2 and 3 LANDED (309 `crt1` WEAKENED-TO-TIE, 310 `csh1` HORIZON-DOES-NOT-REPRODUCE); off-queue 1.14 LANDED (312 `cvl1` VAL-DIFFERS-UNRESOLVED + SELECT-SAME, PARTIAL); rank 1 LANDED (315 `g3b` UNRESOLVED-BOXBOUND-W4 + SCALAR-BEATS-BEST + DENOM-HOLDS); the two α-independent batches LANDED (317 `crd1` ROUTE-IS-WEIGHT-SHRINK + INDEP-NOGAP, 318 `cai1` AI-UNREADABLE + SC-PARTIAL), so **every batch of this queue except `crt2` has landed**** *[was: none landed (`crt1` 36 / 36 COMPLETED, unscored)]*

Each needs its own registration (scorer before batch), a prior-art check first, and fresh seeds. Costs are ESTIMATES.

| rank | experiment | question | cost | why it outranks the others | status (cycle-5 audit, 2026-09-22 10:01 UTC) |
|---|---|---|---|---|---|
| 1 | **G3b**: the audit's CIFAR-100 cell (`gc1` / `cdn1`: `ResNet18_c100`, SGDm 0.99 + Lion, ms 1e-4, α0 1e-3) at κ {0.1 anchor, 5e-4} × {chunk771, nodewise, scalar, layerwise} × 4 seeds, realised shrink reported | Do `SCALAR-BEATS-BEST` and the count-matched sign hold on the audit's second dataset? The chunk771 arm at 5e-4 is also 1.16's denominator arm | 32 runs ≈ 26 GPU-h | the rewritten headline rests on ONE cell; this is the referee's first question and it folds in 1.16 | **LAUNCHED** as `g3b`, CORRECTIONS 299: 32 jobs **5080798–5080829**, seeds 170–173, 8 arms (wd 0.1 / 5e-4 × chunk771 / nodewise / scalar / layerwise); 24.4 GPU-h expected, 64 bound; **LANDED (CORRECTIONS 315)**: 32 / 32 `COMPLETED 0:0`, 33.7636 GPU-h by `sacct`; **`UNRESOLVED-BOXBOUND-W4 \| SCALAR-BEATS-BEST \| DENOM-HOLDS \| W1-SURVIVES+W4-BOXBOUND`** — D_W1 +1.2170 SURVIVES (anchor matches the CIFAR-100 pool); D_W4 +0.0645 unreadable (chunk771 box-bound at 5e-4; no survive / vanish sentence); scalar above both partitions at 5e-4 by +6.03 / +6.10 pp (untuned, 311 A5); chW4 +14.5857 pp below tuned SGD (1.16 PARTIAL — LANDED for `cdn1`, nominal-value form); ingested at `4f7e191` *[was: 32 / 32 `COMPLETED` by 14:07Z, NOT scored — landing owed; amended at CORRECTIONS 314; before that 0 / 32 started (32 pending)]* |
| 2 | **Retune at 5e-4 on the core cell** (1.18 applied to the audit): ResNet18 / CIFAR-10, κ 5e-4, meta step {3e-5, 1e-4, 3e-4} × {chunk777, nodewise, scalar} × 3 seeds | Is `SCALAR-BEATS-BEST` a tuning artefact of hyperparameters chosen at 0.1? | 27 runs ≈ 20 GPU-h | it can REFUTE the new headline's strongest claim (B2), where G3b can only replicate it | **LANDED (CORRECTIONS 309)** as `crt1`: 36 jobs **5080605, 5080607–5080626, 5080628–5080642**, seeds 176–178; 31.05 GPU-h by `sacct`; **`WEAKENED-TO-TIE \| TUNED-SCALAR-TIES-BEST \| ORACLE-SCALAR-TIES-BEST`** — every grain selects A2 (α0 1e-2, grid edge), T_ch +0.4487 / T_nd +0.6880 pp, chunk777 misses the 2 SE clause by 0.1078 net of B; the row becomes "ties (a bound) after re-tuning"; NOT refuted, NOT robust; σ-margin bound (break-even 0.2014); ingested at `5db62be` *[was: 36 / 36 COMPLETED, not yet scored or ingested]* *[CORRECTIONS 313 / 314: the follow-on `crt2` (the retune past `crt1`'s α0 grid edge, five-point plus grid × {chunk777, nodewise, scalar} × seeds 200–202) REGISTERED at `986e165` and SUBMITTED: 45 jobs **5083795–5083839**, 40.25 GPU-h expected, 90 bound; 45 PENDING at 14:12Z]* |
| 3 | **1.20 short-horizon γ control** at the mechanism cell | Does a shortened hypergradient horizon without decay reproduce the collapse (T-C)? | 12 runs ≈ 8.4 GPU-h | the one live rival mechanism against the collapse section's causal sentences; 1.17 is largely decided by `cwd1` (271) | **LANDED (CORRECTIONS 310)** as `csh1`: 18 jobs **5080645–5080662**, seeds 180–182; 12.45 GPU-h by `sacct`; **`HORIZON-DOES-NOT-REPRODUCE \| A-NOGAP+M-NOGAP+P-NOGAP`** (the registered prediction) — G −4.0127 / −5.6273 / −3.6780 pp, scalar ahead in every cell; T-C excluded as a SUFFICIENT account at this cell, a bound, constant γ only; cell P's reference +1.97 pp over REF_MIN; the learned horizon waits for `crd1` (307.7); ingested at `5db62be` *[was: 13 COMPLETED / 5 running]* |
| off-queue | **1.14 validation split** (`PATCH_VALSPLIT`, 302): `cgw1`'s cell at wd 0.1 / 5e-4 × four grains with 5,000 held-out images | Do the audit's TEST rankings hold on VAL, and would VAL select the same configuration? | 32 runs ≈ 21.7 GPU-h | the audit's ms 1e-4 was chosen on TEST (302.1) | **LANDED (CORRECTIONS 312)** as `cvl1`: 32 jobs **5080667–5080698**, seeds 184–187; 26.58 GPU-h by `sacct`; **`VAL-DIFFERS-UNRESOLVED \| SELECT-SAME \| W1-TUNDECIDED/VSURVIVES+W4-TUNDECIDED/VVANISHES+SC-TSCALAR-BEATS-BEST/VSCALAR-BEATS-BEST`** — W1 / W4 change state between readers with neither paired gap resolved (no sentence either way); SC SCALAR-BEATS-BEST on both; both readers pick kLW1; primary seed-fragile (drop s187 → AGREES); ms / α0 not re-selected, so 1.14 is PARTIAL; ingested at `5545d88` *[was: 10 running / 22 pending]* |
| off-queue | **α-independent audit** (`PATCH_DECAYROUTE`, 305): `cgw1`'s cell at wd 0 with `DECAY_ROUTE=alpha_indep:Λ`, Λ ∈ {5e-5, 5e-4} × four grains × 4 seeds | Does the count-matched sign survive, and `SCALAR-BEATS-BEST` hold, when the decay no longer moves with α (`DECOUPLED-NOT-TESTED`)? | 32 runs ≈ 27.0 GPU-h | the paper's biggest open referee point: every result uses α-scaled decay | **LANDED (CORRECTIONS 318)** as `cai1`: 32 jobs **5081292–5081323**, seeds 192–195; 35.49 GPU-h by `sacct`; **`AI-UNREADABLE \| SC-PARTIAL \| I5-BOXBOUND+I4-UNHEALTHY \| I5-SCALAR-UNRESOLVED+I4-SCALAR-COLLAPSED`** — both Λ rungs unreadable (I5 box-bound at 7.0–7.4 % of chunk777's records, I4 every arm below 85 at 77.4–80.8), so no partition reading under α-independent decay at this cell; the artefact branch (prior 0.30) and the survive branch (0.15) were both NOT reached; the headline keeps its α-scaled qualifier and is not removed *[was: LAUNCHED, 0 / 32 started; CORRECTIONS 314: 7 running / 25 pending at 14:12Z]* |
| off-queue | **1.6 the collapse route** (§3 row 1.6) | shrink vs trace vs α-independent at the mechanism cell | 18 runs ≈ 12.3 GPU-h | row 1.6, MUST | **LANDED (CORRECTIONS 317)** as `crd1`: 18 jobs **5081273–5081290**, seeds 196–198; 11.66 GPU-h by `sacct`; **`ROUTE-IS-WEIGHT-SHRINK \| INDEP-NOGAP \| S-COLLAPSE+T-NOGAP+I-NOGAP`** (the registered prediction) — G_S +47.2933 / G_T −3.4747 / G_I +0.6393 pp; the shrink route is sufficient (with its undecayed direct term), the learned trace route is not, and the collapse needs the decay to move with α; with `csh1` (307.7) T-C is excluded as a sufficient account in both forms *[was: LAUNCHED, 0 / 18 started; CORRECTIONS 314: 9 / 18 COMPLETED at 14:12Z; not read]* |

---

## 5. The ceiling, stated plainly

- **Without Phase 1 passing, no candidate clears ICML with this cluster and this evidence.** C2/C4 are single-method,
  CIFAR-scale results with a self-conceded corner-case setting; the reviewer form's "limited evaluation" caps them at
  Weak Accept at best, and prior art (arXiv:2605.19095, 2305.17212, 2607.21005) makes "well-known result" objections
  likely.
- **The area chair's verdict (292): no candidate is an ICML accept as planned.** With the gate passing, **~10-15 %**
  conditional, not 15-25 %; Defazio §6.1 takes the broad story, He et al. makes the configuration doubly
  non-standard, and Wu et al. offers a rival mechanism that must be excluded (1.17, 1.20).
- **With Phase 1 passing**, C1 is a credible ICML submission but still missing ImageNet-1k (impossible here) and,
  unless Reza unblocks TinyStories, a language model. The ViT arm and a toy-model theory are what substitute for
  them, following the Lobacheva (NeurIPS 2021) / Kosson (ICML 2024) precedent.
- **297: the gate FAILED (289 + 295). The venue is TMLR, for ONE paper** (the audit with the collapse as a bounded
  section); TMLR acceptance ≈ 0.6–0.7 after the rewrite, a judgement.
- **Best realistic venue if the gate fails: TMLR**, with the audit (after G3) and the decay × granularity mechanism
  either merged or as two papers; ReScience/MLRC for the reproduction angle. The C3 question, whatever it returns,
  goes to Saber, not into a venue.

---

## 6. What this file does NOT do

It registers nothing, launches nothing, and licenses no new sentence in any write-up. It names no threshold inside the
unrun 1e-2…0.1 decade. It makes no claim about the parent paper beyond what Table 2-4 state and what our own
committed runs show. Every experiment above needs its own registration, a prior-art check and Reza's go-ahead;
anything touching the parent needs Saber first.
