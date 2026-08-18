# Hierarchical MetaOptimize — Decision-Ready Project Plan
*Lead advisor synthesis, 18 Aug 2026. Reconciles five specialist reports + completeness critique. Where reports conflict, the decision is made here and marked **[RULING]**.*

---

## 1. WHERE THE PROJECT ACTUALLY STANDS

1. **You have three solid, defensible findings and zero validated science.** The three code defects (no augmentation → task memorized in epoch 1; a second `--max-time` break silently truncating runs to 81/85 epochs; layerwise/nodewise/weightwise being non-executable in the released code) are real, verified, and yours. But every *number* rests on granularity code that has never been checked against anything — not against the scalar path, not against a finite-difference meta-gradient, not against the authors' published table. Until that check runs, "layerwise 91.34" is an unvalidated output of unvalidated code.

2. **The premise is not falsified — it is untested.** **[RULING on B1]** The proposal's claim is *scale-dependent*: layerwise helps small, loses large. CIFAR-10/ResNet-18 **is the small end**. Your +3.3pp layerwise win is *consistent with* the premise, not a refutation of it. Two of five reports (Research, Paper §0) overstate this and Research's entire re-aiming is built on the overstatement. Do not carry "the premise is dead" into any email, thesis chapter, or abstract. What you can say: *the failure the proposal names does not appear at CIFAR-10 scale; a different failure appears at a granularity the proposal did not consider.*

3. **The most load-bearing number in the project is missing.** Gate 0 AdamW-scalar (92.13, n=2, different campaign) beats every Gate 1 number. If the Gate 1 AdamW-scalar cell lands near 92, then under AdamW the ordering is scalar > 6-block > layerwise, **the anomaly does reproduce at CIFAR scale**, and this becomes a base-optimizer story (H4), not a scale story. That single cell can invert the project's direction. It is still running.

4. **The weightwise collapse — currently the most interesting result — may dissolve under a dtype change.** Your own diagnostics describe an absorbing state: α→5e-11 → Δw underflows → H stops accumulating → z→0 → Lion's `sign(0)=0` → β frozen forever. That is a floating-point/optimizer-convention interaction, not necessarily a statement about granularity. Three of the five reports build a narrative on it; none of them gated it behind a numerics check.

5. **The binding constraint is you, not compute.** Compute is effectively free and 12–40× underused. The five reports collectively prescribe ~40 "cheap, do today" items totalling 6–10 weeks of serial human work, for one unfunded student who must also write a thesis, inside a 12-month window of which 12 days are gone. Nothing in them cuts anything. This plan cuts.

---

## 2. THE REFRAMED RESEARCH QUESTION

**Primary (adopted).**
> **Step-size granularity in online meta-gradient methods is an estimation problem, not a parameterization problem. How fine can a partition be before the meta-gradient signal per block is too weak to estimate — and can a hierarchical (partially pooled) estimator make the partition a non-decision?**

The pivot is from *"why does layerwise hurt at scale"* to *"what sets the usable granularity, and can we remove the choice."* This survives every outcome of the open questions: if the failure is at m=n, pooling is the direct remedy; if per-granularity tuning rescues m=n, the contribution becomes "granularity buys nothing once tuned, and here's the estimator-theoretic reason"; if the AdamW-scalar cell inverts the ordering, the same framing absorbs it as an adaptivity-substitutes-for-granularity result. Crucially it does **not** require the proposal's anomaly to exist. Success criterion for the method: `hierarchical(m=n) ≥ max_m plain(m)` at matched tuning budget, with the scalar arm's robustness volume.

**Alternatives, ranked:**

- **Alt-1 (fallback, ~35% likely to become primary): "The fine-granularity failure mode."** A tight instability paper: the causal chain of the weightwise collapse, its phase diagram over (α₀, η, m), and a minimal fix. Becomes primary if D1 shows the collapse is real and D2 shows it survives tuning, but the method (Phase 4) does not win. Smallest evidence bill, workshop-ready by month 6.
- **Alt-2 (~20%): "Adaptivity substitutes for granularity."** Becomes primary if AdamW-scalar ≈ 92 and the ordering inverts under AdamW. Two-axis story: granularity × base-optimizer per-coordinate adaptivity, with an interior optimum that shifts coarser as adaptivity rises. Needs a third and fourth base optimizer (Lion, RMSProp) to be a curve rather than two points.
- **Alt-3 (floor, always available): "A reproduction study with three defects and a corrected release."** Guaranteed thesis, TMLR/MLRC-plausible paper. Do not aim here, but it is the safety net and it costs nothing extra because Phases 0–2 produce it as a by-product.

**Explicitly retired:** "we explain a known anomaly" (the anomaly's provenance is unverified); H3 runaway β (refuted by your own probe — retire it in writing).

---

## 3. PHASED PLAN (Aug 2026 – Aug 2027)

Critical path marked **[CP]**. Durations are *person-weeks*, not GPU time. Compute is not the constraint; assume every listed sweep completes in ≤2 days wall-clock on the existing single account.

### Phase 0 — Survival, provenance, prior art (18 Aug – 4 Sep, 2.5 wks) **[CP]**
**Deliverables:** private git repo on LIACS GitLab + GitHub mirror, with your changes as a visible diff against upstream `61a57f8` and a `DEFECTS.md`; nightly rsync of metrics to `/zfsstore/user/s5014158`; signed DMP; the supervisor email sent; a 3-page prior-art memo on the IDBD lineage; a written authorship agreement circulated.
**No new experiments.** Finish only the AdamW-scalar Gate 1 cell and the two outstanding weightwise seeds.
**[RULING on Infra §1.2 Step A]** Snapshot **only your own work**, to your own `/zfsstore`. Do **not** tar and scp the PI's scratch directory to your Mac — it contains his unpublished Jan-2024 outputs and sits adjacent to a licence-restricted ImageNet copy. Ask before anything of his leaves ALICE.

### Phase 1 — Implementation validation + numerics gate + metric fix (5 Sep – 2 Oct, 4 wks) **[CP]**
**Deliverables:** the seven-test validation suite of §5 passing, with results committed; the numerics gate resolved (**D1**); a run harness with `config.resolved.json` + hash, `provenance.json`, a `DONE` sentinel, full per-epoch curve logging and a collapse detector; `aggregate.py` → `results.parquet` → `make figures`; a small-MLP development testbed where the full-batch meta-gradient is exactly computable; a pre-registration document distinguishing **exploratory** (Gate 0/1, already seen) from **confirmatory** (everything after).
**Experiments:** ~30 runs, mostly CPU or minutes-long. Plus 3 *unaugmented* verification runs (scalar, 6-block) compared against the parent paper's published table — **[RULING on B7]** these are void for science but are your only external anchor for whether the scalar/blockwise paths still match the authors'. Label them verification-only in the repo and in the thesis.
**[RULING on B3]** Primary metric from here on: **final-epoch test accuracy and mean of last 5 epochs**, on 5 confirmation seeds, selected on a fixed 5,000-image validation split carved from train. Best-of-100 is logged always, reported only in the one table that compares to the parent paper. Reporting a collapsed run's pre-collapse peak (70.09) is a correctness error, not a style choice.

### Phase 2 — De-confounding campaign (5 Oct – 27 Nov, 8 wks) **[CP]**
The single highest-value block of the project. One pre-registered campaign, ~250 runs, answers four questions at once.
**Arms:** base ∈ {SGDm, AdamW, Lion, RMSProp} × granularity ∈ {1, 6, 20 (module-grouped), 62 (tensor), ~10³ (nodewise/channel), n}. Tunable per arm: **η and α₀ only**, on an identical fully-crossed 5×3 grid, 1 seed for selection, 5 fresh seeds at the winner.
**Bolted-on controls, all cheap and all decisive:**
- **Tuned baselines** — SGDm+cosine and AdamW+cosine at matched search budget. Every current number is 3–6pp below a competent ResNet-18/CIFAR-10 baseline (94.5–95.5%). Until you show this harness can reach ~94.5, you do not know whether you are studying a method or a misconfiguration.
- **Random partitions at matched cardinality and size distribution** for m ∈ {62, 10³, 10⁴}. Separates *block size / SNR* from *layer structure*. If random-62 ≈ layerwise-62, "early layers want bigger steps" is fiction and shrink-toward-scalar is the wrong prior.
- **Horizon sweep**: {6, 62, n} × {100, 300, 600 epochs} × 3 seeds. Tests the one variable H1 says is decisive, at 1/50 the cost of ImageNet. If the gap inverts with horizon, you have explained ImageNet without running it.
- **κ-decoupling arm** **[RULING on B6]**: one arm with the trace decay decoupled from the learned α. Otherwise Blind-spots' trace-horizon mechanism is untestable and κ·α means per-block α is silently per-block weight decay.
- **Collapse rate as a Bernoulli**: 10 seeds at weightwise/SGDm, reported as a rate with a Clopper–Pearson CI and a collapse-epoch survival curve. **[RULING on B9]** Seed policy: 3 exploratory, 5 headline, 10 for collapse rates.
- **Train loss and test accuracy reported separately** for every arm. Free, and it decides whether this is an optimization paper or a generalization paper.
**Deliverables:** Table 1 of the paper; tuning curves (expected-best-val vs trial budget) per arm; robustness volume (fraction of grid within 1pp of arm best) as a headline number; **D2** resolved.

### Phase 3 — Mechanism (30 Nov – 29 Jan, 8 wks incl. holidays)
**Deliverables:** the money-plot triptych. (i) SNR vs n_b against the **correlation-corrected** prediction `SNR ∝ √(n_b/(1+(n_b−1)ρ̄))` with ρ̄ measured directly — this converts H1's failed slope (0.114 vs 0.50) into a quantitative fit and hands Phase 4 a *computable* shrinkage coefficient. (ii) `E[sign z_b]` vs n_b against the Gaussian prediction, with the gap labelled as skew (the sign/median mechanism). (iii) predicted β drift (η × E[sign z_b] × steps) vs measured β drift, per block, no free parameters.
**Method:** frozen-point variance decomposition at K≈10 checkpoints — freeze (w,H), evaluate z_b on M=64 independent minibatches; full-batch z_b as ground truth at 2–3 checkpoints. No running-window SNR (it confounds drift with noise). Random partitions in the probe so n_b is randomised w.r.t. layer identity. Mixed-effects analysis; blocks within a run are not independent.
**Cost:** ~5 instrumented runs. This rides on runs you are doing anyway. **D3** resolved here.

### Phase 4 — Method (1 Feb – 9 Apr, 10 wks)
**Develop on the 200-parameter MLP first**, where the meta-gradient is exact and a λ/η_δ identifiability check takes minutes. Only then CIFAR.
- **M1**: β_b = β₀ + δ_b, η₀ ≫ η_δ. Write down the estimator before implementing it. Note: ∂/∂β₀ = Σ_b z_b *exactly*, so under a linear meta-optimizer M1 *is* the scalar arm — its entire content lives in the sign nonlinearity and the η₀/η_δ ratio. State this; it decides whether M1 is a method or a reparameterization. Impose Σδ_b = 0 or a λ>0 prior — the parameterization is overdetermined by one dof and under a sign meta-optimizer that flat direction random-walks.
- **M3**: empirical-Bayes λ_b derived from the measured ρ̄ / the meta-optimizer's own running variance. This is the principled contribution and it is what makes shrinkage *derived* rather than tuned. **If Phase 0's prior-art memo shows Autostep/normalized-IDBD already does this, M3 is a re-derivation — say so and re-aim to M2.**
- **M5** (trust region on δ) as the blunt baseline shrinkage must beat. **M4** (z_b/n_b) in the ablation — note it is a *no-op under a sign meta-optimizer*, itself a sharp mechanism prediction.
- **M2** (multi-level tree / μP- or role-centered prior rather than flat-scalar-centered) only if Phase 2's random-partition control says structure matters.
**D4** resolved here.

### Phase 5 — Scale point + paper (12 Apr – 28 May, 7 wks)
**[RULING on B8]** One scale point, costed once, chosen at D4: **ImageNet-64×64 (full 1.28M images, full 1000 classes, full step count)** is the default — it preserves the two variables that matter (dataset scale, horizon) and sacrifices only resolution, at ~1/10 the cost of ImageNet-1k. Full ImageNet-1k only if the 489-class audit comes back clean *and* the method won at D4. A ~100M transformer LM is the substitute if the ImageNet copy is unrepairable and the story is about heterogeneity rather than scale. Budget: 5 arms × 3 seeds, ≤400 A100-h, ≥13 days wall-clock at the 2-A100 cap — schedule it, do not assume it.
**Paper drafted here.** TMLR is the primary target (rolling, evaluates claims-vs-evidence, no novelty bar, suits a careful diagnosis paper with an honest scope limit). NeurIPS 2027 (abstract ~May) is an opportunistic secondary only if D4 landed *and* the scale point is in.

### Phase 6 — Thesis (1 Jun – 6 Aug, 10 wks) **[CP]**
Writing, second-examiner reading window, defence. **This is non-negotiable and is why Phases 2–5 must be cut, not extended.** The thesis is a different artifact from the paper: it needs chapters, a contribution statement, an AI-use declaration, and a defensible shape *even if every result is null*. Draft the thesis outline in Phase 1, not Phase 6.

### Explicitly CUT or DEFERRED (in writing, so it stays cut)
- Full ImageNet-1k as a premise-reproduction exercise. Deleted.
- The two-account 84-GPU plan. Deleted (see Risk 5 and §7).
- PaperFactory front half (`trend_scan`, `idea_generation`, `novelty_gate`, `track_selection`, `experiment_design`). Deleted. **[RULING on B5]** Novelty *is* needed — but by reading IDBD/Autostep for an afternoon, not by running a stage whose configured research programme is small-LLM fine-tuning on a 6GB 2060.
- `experiment_run` on any backend other than ALICE. Hard rule: every number in the manuscript traces to an ALICE job ID and a logged config.
- A `SlurmBackend` for PaperFactory. Deferred indefinitely — it duplicates the harness you must build anyway.
- Multi-architecture (GroupNorm / no-norm / ViT) sweeps. Deferred to Phase 5 as a single 18-run robustness table, not a Phase 2 axis.
- CIFAR-100 / TinyImageNet as a second dataset. Deferred; the horizon and capacity axes buy more per hour.
- Wandb / hosted tracking. Files + DuckDB only.

---

## 4. IMMEDIATE ACTIONS (next 1–2 weeks)

1. **Snapshot your own work off scratch, today, before anything else.** `/data1/.../metaopt` minus `.git`, `envs`, `__MACOSX`, and anything of Saber's, to `/zfsstore/user/s5014158`. Twenty minutes. Everything else in this document is worthless if scratch rolls.
2. **Make it a real repository.** `git init`, vendor upstream pinned at `61a57f8`, commit *your* changes as a visible diff (`patches/0001-augmentation`, `0002-max-time`, `0003-granularity-paths`), write `DEFECTS.md` with the exact file/line/traceback evidence and the byte-identical-inertness test. Push to LIACS GitLab **and** a private GitHub mirror. Keep it private — publishing a commit history that documents the dead-code finding before the authors have been told is a communication decision, not an infrastructure one.
3. **Finish the AdamW-scalar Gate 1 cell and the two weightwise seeds.** Nothing else queued. This cell can invert the project.
4. **Send the email to Saber** (private, him alone, before Arsalan). Structure: results → scoping question → config questions → code paths last, in question form, with your own most likely error named before his. **Ask for:** (a) DMP signature + Leiden Data Store collection + you added as depositor; (b) **exactly which parameters are in each block for every granularity in the paper — is the paper's "layerwise" m=6 or m=#tensors?** (this is the single most likely resolution of the whole thing, and if it is 6, there is no discrepancy and your m=62 is new ground); (c) was the ImageNet run the same 6-block partition; (d) is "layerwise doesn't help at scale" backed by a run or a recollection, and can you see the logs/β trajectories; (e) was meta-stepsize ever tuned per granularity; (f) is the 489-class ImageNet a deliberate subsample; (g) read-only access to the legacy scratch data — **not** write access, **not** a `setfacl` on his directory; (h) repo licence and whether he wants your granularity implementations as an upstream PR; (i) second examiner appointed now, given he is both co-author of the parent work and your assessor.
5. **Read the IDBD lineage. One afternoon, before any method work.** IDBD (Sutton 1992) is per-weight *by construction*; Normalized-IDBD/Autostep (Mahmood, Sutton et al. 2012) exists **specifically because per-weight meta-learned step sizes are unstable unless the meta-update is normalized by a running estimate of the meta-gradient's magnitude**. Your collapse may be the known failure and M3 may be the known fix. Also: hypergradient descent (Baydin), SMD (Schraudolph), MARTHE, Adam-mini, and the prescriptive per-layer family (LARS, LAMB, μP) that Blind-spots caught. Sutton is a co-author of the parent paper — this is the closest relative and it is unread. **Highest expected-value hour in the project.**
6. **Read the public record on the parent paper.** OpenReview reviews/rebuttals for ICML 2025 and the arXiv v1→vN diff for 2402.02342 are free and may answer questions (b), (c), (e) before the email is even answered. Do this *before* sending, it may change what you ask.
7. **Run the two zero-GPU checks on logs you already have.** (i) Scalar's α(t) vs the geometric mean of layerwise α(t) — if scalar is stuck near α₀, "+3.3pp for granularity" is an artifact of a broken scalar run and Gate 1's headline inverts. (ii) β-spread growth exponent vs t — a free preview of the horizon hypothesis. One afternoon, existing data.
8. **Write the pre-registration and the cut list.** One page in the repo, dated: primary metric, seed policy, effect size that counts (Δ ≥ 0.5pp, 95% paired CI excluding 0), which analyses are exploratory (Gate 0/1) vs confirmatory (Phase 2+), and the Phase-3-onward items you have deleted. **[RULING on the "pre-register before looking" issue]** You have already looked. Calling Phase 2 pre-registered is honest; calling Gate 0/1 pre-registered is not. Say which is which.

---

## 5. VALIDATION OF THE NEW CODE — critical path, blocks everything

Every result in this project comes from code the original authors never executed and nobody has checked. "Byte-identical inertness on the untouched paths" proves the *old* paths are unharmed; it says nothing about whether the *new* paths compute the right thing. A subtly wrong `z_b` would produce **exactly** the pattern you observe: coarse fine, fine degrading, weightwise collapsing. Run all seven before another sweep. Total cost: near-zero GPU, ~1 person-week.

**[RULING on B10 — tolerance.]** "Bit-for-bit" is unachievable across different reduction orders with `cudnn.benchmark=true` and will produce a false "my implementation is wrong" panic. Specify: **exact match at step 1 under `torch.use_deterministic_algorithms(True)`, `cudnn.benchmark=False`, fp64**; relative tolerance 1e-10 (fp64) / 1e-5 (fp32) thereafter, with divergence tracked as a function of step count and reported.

| # | Test | Catches | Pass criterion |
|---|---|---|---|
| V1 | **Sum identity.** From identical (w, H, batch): `Σ_b z_b == z_scalar` | Reduction/broadcast errors; the strongest single check, costs one step | rel. err < 1e-10 in fp64 |
| V2 | **Partition equivalence.** Express the authors' 6-block partition *through the new generic code*; compare to the legacy blockwise path | The generic machinery is sound, or it isn't | exact at step 1, tolerance to step 1000 |
| V3 | **Tied-β control.** Run the weightwise path with all β forced equal | Separates "partition machinery wrong" from "fine granularity genuinely differs" | must reproduce the scalar run |
| V4 | **Finite-difference meta-gradient.** 200-param MLP, small γ, 10-step horizon: implemented `z_b` vs numerically differentiated ∂F/∂β_b, and vs brute-force forward-mode H | Sign errors, missing factors, wrong Jacobian term | agreement to 1e-4 relative |
| V5 | **Off-by-one / trace-timing audit.** Does the meta-update consume `H_t` (pre-base-update) or `H_{t+1}`? Does the trace decay use `α_t` or `α_{t+1}`? | A one-step-stale H penalizes fine granularity far more than coarse — it would **manufacture your headline finding** | manual trace + V4 |
| V6 | **Permutation invariance + κ·α broadcast.** Relabel blocks at fixed seed; check `H_{t+1}=γ(1−κα_t)H_t+Δw` with α a length-n vector | Indexing bugs; silent shape broadcast at m=n | identical results; explicit shape assertions |
| V7 | **η=0 and dtype/AMP audit.** Weightwise with the meta-step disabled is just fixed α₀=1e-6 SGDm — must train badly but **not collapse**. Grep every path touching H, z, m̄ for fp16/bf16 | If η=0 collapses, the collapse has nothing to do with meta-learning. If any accumulation is in fp16, the collapse is a rounding artifact, full stop | no collapse; all meta-state in fp32 minimum |

**External anchor (V8).** Run the *unaugmented* config once per granularity at the authors' settings and compare scalar/6-block against the parent paper's published table. Void for science, valid for verification. If your scalar/6-block numbers don't match theirs, stop and find out why before anything else.

**Structural guarantees (not tests, but they prevent the defect class).** The harness refuses to launch a sweep-tagged run from a dirty git tree; `epochs_completed` vs `epochs_requested` in every manifest; a `DONE` sentinel, with `aggregate.py` excluding non-`DONE` runs *by construction* and printing the exclusion list. Defect #2 must be structurally impossible, not remembered.

---

## 6. DECISION POINTS

**D1 — Numerics gate (end of Phase 1). This is new; no report gated it, and it sits upstream of everything.** **[RULING on B2]**
*Test:* re-run weightwise/SGDm with (a) H, z, m̄ accumulated in fp64, (b) an explicit "z underflowed to exactly 0" counter, (c) a β floor / α clamp, (d) meta-optimizer = Adam and = SGD instead of Lion.
- **Collapse survives all four** → it is a real granularity/statistics phenomenon. Alt-1 is live; Phase 3's mechanism work is the paper's core; the method has a target.
- **Collapse dissolves under fp64 or a non-sign meta-optimizer** → it is an implementation pathology. Report it as such (a genuine, useful contribution about a widely-shared design), **delete Alt-1**, and the project's centre of gravity moves to the Phase-2 tuning/adaptivity result and the Phase-4 method. Decide this *now*, while it is hypothetical, so you don't spend a month defending it.
- Note: `sign(0) → +1` is a valid *diagnostic* and an **invalid fix** — at m=n a large fraction of coordinates have exactly-zero meta-gradient, so it injects systematic upward drift into every dead coordinate. Do not let it reach the method section.

**D2 — The tuning confound (mid Phase 2).**
*Test:* does any granularity failure survive per-granularity (η, α₀) tuning at equal search budget? And what is the AdamW-scalar cell?
- **Weightwise recovers under tuning** → "the anomaly was a hyperparameter." Legitimate and publishable; the contribution becomes the tuning-budget and robustness-volume analysis plus the mechanism for *why* fine granularity needs a different η. Alt-1 dies; the method's target becomes F2 (tuning fragility) rather than F1 (collapse).
- **Weightwise fails across the whole grid** → the failure is structural; primary RQ and Alt-1 both live; proceed at full speed.
- **AdamW-scalar ≈ 92 and the ordering inverts under AdamW** → Alt-2 becomes primary, the anomaly *does* reproduce at CIFAR scale as a base-optimizer effect, and the ImageNet question becomes much less urgent. Add Lion and RMSProp arms to make adaptivity a curve.

**D3 — Which mechanism (end of Phase 3).** Three candidates, three different methods:
- **Block-size / SNR (H1 corrected by ρ̄)** → shrink toward the pooled scalar. M1+M3 as planned.
- **Sign/median skew under a sign-based meta-optimizer** → the fix is normalization of the meta-update (which is Autostep — check the prior art first), not pooling.
- **α-dependent trace horizon (κ·α)** → small α → stale trace → wrong-sign z → smaller α. The fix is decoupling the trace decay (explicit γ_H < 1), **not shrinkage at all**, and it is a more interesting paper than Eq. (1).
- **Random-partition control says structure matters** → shrink-toward-flat-scalar is the wrong prior; the target becomes a μP- or parameter-role-centered prior, and M2 becomes the headline instead of an afterthought.
*Criterion:* the mechanism that predicts the measured β drift rate with no free parameters wins. If none does, report the refutations honestly and ship the descriptive paper.

**D4 — Does the method earn a section (end of Phase 4).**
- `hierarchical(n) ≥ max_m plain(m)` on 5 seeds at matched tuning budget, **and** robustness volume ≥ scalar's → write the method section, run the scale point, attempt a conference.
- Ties only → "removes a hyperparameter, plus a mechanism." TMLR, good thesis, honest. Ship it.
- Loses → **cut the method, keep the paper.** The primary RQ's descriptive + mechanistic halves stand alone. This is precisely why the method is not the spine.

---

## 7. TOP RISKS (most under-weighted first)

**R1 — Single-person serial capacity. Unmentioned by four reports, half-a-sentence in the fifth, and the mechanism by which every other risk actually bites.** The backup doesn't get made because the sweep is queued; the equivalence tests get skipped because the results look plausible; the email doesn't get sent because the framing needs another day. *Mitigation:* the cut list in §3 is binding and lives in the repo. Phase 6 (10 weeks of thesis writing) is fenced and cannot be borrowed from. One weekly written state file, 10 minutes, doubling as the decision log and DMP evidence. Any new experiment proposed after Phase 2 must displace a listed one, in writing.

**R2 — Prior-art collapse (IDBD/Autostep).** If normalized-IDBD already contains both the per-weight instability and a normalization fix that is M3 in disguise, the method contribution shrinks to a re-derivation — and Sutton is a co-author of the parent paper, so a reviewer will know. *Mitigation:* Action 5, one afternoon, **before** ~600 GPU-hours and 10 person-weeks go into Phase 4. If it lands badly, re-aim to M2 (structured/μP-centered prior) or to the mechanism-only paper.

**R3 — The implementation is wrong and everything downstream is fiction.** Currently unvalidated, currently untracked, and it produces exactly the pattern that would be expected from a subtle `z_b` bug. *Mitigation:* §5 in full, on the critical path, before Phase 2. Ask Saber and Arsalan to review the implementations explicitly — it is both the best check available and the most collaborative possible framing of the code question.

**R4 — Overclaiming refutation, and the relationship cost of the code finding.** Three separable claims with three evidence levels: *the released repo at `61a57f8` has no branch for the finer granularities* (verifiable — write it plainly, with commit hash and line numbers); *the MetaStep branches contain type errors that cannot execute as written* (verifiable — write it plainly); *therefore the parent paper's granularity was held at 6 blocks because the finer path never ran* (an inference about code you cannot see — **never write this**). Maximum permissible: "the released code does not support granularities beyond the block partition, so we implemented them." Main text gets one neutral sentence with the verb **extend**; the forensic detail goes in an appendix titled "Reproducibility notes on the reference implementation," itemized, no blame verbs, with an explicit statement that your numbers are therefore not directly comparable to the parent table. With Saber as co-author this is self-disclosure by the original team — which is the right framing **because the parent authors must be able to shape any statement about their own work**, not because it plays well with reviewers.

**R5 — Data loss and account/quota exposure.** No backup, ~1 month scratch retention, DMP filed but unsigned, all work on the PI's account. *Mitigation:* Actions 1–2 and 4(a),(g). **[RULING on B4]** Migrate all new runs to `s5014158`; request **read-only** access to the legacy data; do not run `setfacl` on his directory; **drop the two-account 84-GPU plan entirely.** Using someone else's quota is quota circumvention regardless of who holds the credentials, and doing it on the account of the person whose code you are questioning is indefensible. The single-account improvement over the current one-job-at-a-time cadence is still 12–40×, which is far more than this plan needs.

**R6 — Thesis/paper objective conflict, and venue drift.** The thesis tolerates a null result; a conference paper does not, which creates quiet pressure to keep chasing an effect. *Mitigation:* declare in writing, now, that the **thesis is primary and the paper is optional**, and that **TMLR is the default venue** (rolling deadlines remove deadline gambling from a one-year unfunded project; it evaluates claims-vs-evidence, which is exactly what this project will have). ICLR 2027 is unreachable; ICML 2027 requires Phase 2 done by November and is not worth distorting the plan for; NeurIPS 2027 is opportunistic only. Verify all 2027 dates yourself. Also settle authorship (you first; Arsalan co-author, not acknowledgement — idea origination of that specificity is a substantial contribution; Saber last; Sutton not by default) and get the second examiner appointed in month 1, not month 10.

---

## 8. WHAT WAS NOT PREVIOUSLY CONSIDERED

Surfaced by the adversarial and completeness passes; absent from the student's NOTES/PILOT:

**Scientific**
- **The IDBD → Autostep / normalized-IDBD lineage** — the direct ancestor, per-weight by construction, with a known instability and a known normalization fix. Plus hypergradient descent, SMD, MARTHE, Adam-mini. The whole *meta-learned* per-weight family is unread.
- **LARS / LAMB / μP** — prescriptive per-layer step sizes that demonstrably work at ImageNet and LLM scale. If prescribed per-layer scaling works where learned per-layer scaling allegedly fails, the failure is in **online estimation**, not in the parameterization — a stronger and more current thesis, and a guaranteed reviewer question.
- **No standard baseline exists in the table.** Every measured number is 3–6pp below a competently tuned ResNet-18/CIFAR-10 baseline. You may be studying a misconfiguration.
- **The scalar arm may be broken rather than layerwise good** — observationally identical from accuracy alone; distinguishable in one afternoon from logs you already have.
- **Best-test-accuracy is a biased estimator whose bias scales with the treatment**, and it reports a collapsed run at its pre-collapse peak. Also: no validation split exists, so all selection is on test.
- **SNR ∝ √n_eff, not √n_b.** Within-block correlation ρ̄ makes effective sample size saturate near 1/ρ̄ — which quantitatively explains the measured slope of 0.114 instead of 0.50 and converts a failed prediction into a working one.
- **n_b is confounded with layer identity** in the H1 regression (BN scales are small *and* scale-invariant; the classifier is small *and* has different statistics). Random partitions with matched size distributions fix it, and simultaneously answer whether layer structure carries any information at all.
- **The trace horizon is α-dependent** (`H_{t+1}=γ(1−κα_t)H_t+Δw`, γ=1): small α → the trace never forgets → stale sensitivity → systematic wrong-sign z → smaller α. A self-reinforcing collapse with a different fix entirely.
- **κ·α means per-block α is per-block weight decay.** "Granularity of step size" and "granularity of regularization" are not separated anywhere in the current design; the +3.3pp gap may be a regularization effect.
- **Horizon, not scale.** CIFAR is 50k steps, ImageNet-90ep is ~450k. Testable on CIFAR for ~40 L4-hours; if the gap inverts with horizon, "scale" in the title becomes "horizon" and ImageNet is explained without running it.
- **Capacity ratio.** CIFAR-10/ResNet-18 is grossly overparameterized (your own defect #1 proves it); ImageNet/ResNet-18 is underparameterized. That regime change, not size, may be the whole effect — and it is testable on CIFAR in hours.
- **"Layerwise" = 62 tensors ≠ ~20 modules.** m=62 gives BN scales and biases their own step sizes — exactly the parameters with scale-invariance pathologies. Add module-grouped m≈20, and a "62 tensors with BN/bias pinned to scalar" variant.
- **Nodewise/channel-wise (~10³) is implemented and is nobody's headline arm** — yet it is exactly where LARS/Adam-mini/μP operate, and the most likely location of the actual cliff between 62 and 11.17M.
- **The unaugmented runs are void for science but are the only external verification anchor** for whether your scalar/6-block paths still match the authors'.
- **Collapse is a Bernoulli outcome, not a mean.** 1/3 seeds gives essentially no information; averaging a collapsed run with two healthy ones produces a number describing nothing.

**Methodological / estimator-theoretic**
- **Nobody wrote down the hierarchical estimator.** β_b = β₀ + δ_b is overparameterized by one dof; λ and η_δ are not separately identifiable under sign updates (so a "λ sensitivity curve" at fixed η_δ is meaningless); and ∂/∂β₀ = Σ_b z_b exactly, so under a linear meta-optimizer M1 *is* the scalar arm. No memory/time cost analysis for a two-level trace at m=n.
- **No small-scale development testbed.** A 200-parameter MLP with an exactly computable full-batch meta-gradient turns GPU-days of method debugging into minutes.
- **Tuning curves and robustness volume** — expected-best-val vs trial budget, and the fraction of grid within 1pp of arm best — are the analyses that pre-empt "did you just tune one arm harder," and the second is a target the method can fix even where mean accuracy ties.

**Project / process**
- **No person-time budget and no thesis-writing time** in any plan. This is the actual binding constraint.
- **No plan for the thesis as an artifact** — chapters, contribution statement, what a defended null result looks like.
- **The public record on the parent paper** (OpenReview reviews, arXiv version diff) was never consulted, and may answer the blocking questions for free.
- **Scooping risk from the proposer's own group**, not from strangers — the proposal is nine months old. Ask directly.
- **AI-tooling disclosure and an idea-provenance log** as first-class integrity items, given the idea originated with a named human and PaperFactory is in the loop. Hard rule: no autonomous stage generates, phrases, or judges any claim about the supervisor's code or the parent paper's validity.
- **PaperFactory's configured research programme is small-LLM fine-tuning on a 6GB 2060, baked into its `north_star`** — it is not a neutral pipeline pointed at the wrong hardware. Back half only (`figures`, `writing`, `review_loop`, `hard_questions`, `red_team`, `polish`), with `allow_rog_dispatch: false` verified by inspection before first invocation.