# ICML-PLAN — what paper could clear the ICML bar, and what must be run to get it

*Written 2026-09-21, cycle after CORRECTIONS 287. **Planning document only.** Nothing here is registered, nothing
was launched, no Slurm job was submitted, `alice` was not contacted, nothing under `paper/` was read. Every campaign
number below cites a committed file; every outside paper is one read by the synthesis inputs (arXiv/OpenReview/
proceedings pages, ids given). GPU-hour figures are **estimates** scaled from measured per-run costs
(`cwd5`: 27 runs = 18.2 GPU-h, CORRECTIONS 285.1; ResNet18 0.67, ResNet18_c100 0.70, VGG11_bn_c100 0.37,
PlainNet18_c100 0.65, ResNet18_tin 1.56 GPU-h per 100 epochs on L4, from `results/all_runs.csv`). None is registered.
The recorded entry is CORRECTIONS 288.*

---

## 0. The short answer

1. **The existing count-matched audit is not an ICML paper, and it now has a live threat.** Its effect is +0.5556 ±
   0.0448 pp (MASTER-TABLE line 175, CORRECTIONS 211.2), every audit cell ran at `--weight-decay-base 0.1`, and at the
   one rung where both grains were measured at standard decay the ranking reverses: scalar **72.4080** vs layerwise
   **67.8813**, `G_W4` = **−4.5267 pp = −8.59 SE** (CORRECTIONS 285, table line ~37612). Its right venue stays TMLR
   (STATUS.md ~1741-1747), **but it must be re-run at 5e-4 before it goes anywhere** (§4, gate G3).
2. **The one framing with a plausible ICML path** is a cross-method analysis paper: *"A step size shared across
   tensors is a magnitude-weighted vote; under step-size-scaled decay a few normalisation gains capture that vote, and
   whether finer granularity helps depends on the decay."* It is plausible **only if** the capture is shown in at
   least one adapter other than MetaOptimize, or at a standard setting (AdamW/Lion at κ = 0.1). Today it is shown in
   neither. That is the kill gate.
3. **The "parent's granularity result is a weight-decay artefact" claim is unsupported now and partly contradicted**
   by our own data (§3, C3). It is testable cheaply (≈28 GPU-h minimal) but must go through Dr Salehkaleybar first.
4. **Honest ceiling:** even if every gate passes, the paper has no ImageNet-1k (impossible, `docs/DATASETS.md`) and no
   language model unless Reza clears TinyStories. I put ICML acceptance at roughly **15-25 %** conditional on the
   gates passing, and roughly **5 %** unconditionally from today. The realistic best venue is **TMLR** for the
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
| B2 | Controlled manipulation, tuned per condition | peer analysis papers (Kunstner ICLR 2023, Crowded Valley ICML 2021) | HAVE for the denominator; PARTIAL for the collapse (4-rung bracket) |
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

**A naming hazard to fix in any ICML text.** The parent rule is Δw = −αm − καw (parent text line ~662) and the harness
does the same (`patches/HF_patched.py` ~592-598). In Loshchilov & Hutter's vocabulary (arXiv:1711.05101) that is
*decoupled* (SGDW-style) decay. What the campaign calls "coupled" means "multiplied by the learned α". An ICML referee
will read "coupled" as L2. Call it **α-scaled decay**; the missing control is **α-independent decay**.

---

## 2. Candidate papers

### C1 — "Vote capture": shared adaptive step sizes are magnitude-weighted votes *(analysis + diagnostic + small fix)*

> **Thesis:** "A step size shared across tensors follows a magnitude-weighted vote over their hypergradient terms;
> under α-scaled decay a few normalisation gains capture that vote and collapse training, and at standard decay the
> ranking reverses, so whether finer granularity helps is decided by the decay, not by the granularity."

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

> **Thesis:** "For MetaOptimize, the sign of the granularity benefit depends on α-scaled weight decay: layerwise wins
> by a floor-sized margin at κ = 0.1 and scalar wins at 5e-4, because a few BatchNorm gains own the shared vote only
> when decay keeps their terms large."

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
| 1.3 | **Capture generalises beyond MetaOptimize** | **MISSING**: no Prodigy/D-Adapt/DoG/Mechanic/Baydin-HD run anywhere in docs (grep, novelty stage) | ResNet18_c100, κ {0.1, 5e-4}: Baydin HD (exact γ=0 case) scalar vs layerwise; Mechanic (can decrease) scalar; Prodigy (non-decreasing contrast) scalar; per-tensor attribution probe on each | pilot 24 runs ≈ 17 GPU-h; full (4 adapters × κ {0.1,1e-2,5e-4} × 2 grains where defined × 3 seeds) ≈ 60-72 runs ≈ 45-50 GPU-h | HD: ~10-line `SGD_meta_update`; Mechanic/Prodigy: pip in a **separate venv** + 30-60-line wrappers + inertness test; probe generalisation | pip install on alice2 login node (PyPI reachable) — Reza's go-ahead | **MUST** (kill gate) |
| 1.4 | Capture happens at a *standard* setting | **MISSING**: AdamW/Lion bases never run on CIFAR-100 (LIMITS-PREP coverage table: AdamW 9 cells, all CIFAR-10) | T2: AdamW+Adam and Lion+Lion bases, ResNet18_c100, κ {0.1, 1e-2}, scalar vs layerwise, 3 seeds (κ 0.1 is the parent's standard for these) | 24 runs ≈ 17 GPU-h | none (flags exist) | registration | **MUST** (kill gate, with 1.3) |
| 1.5 | The transition is *located*, and expressed on the realised per-step shrink α·κ | **PARTIAL**: bracketed in (1e-2, 0.1) only (285, `LADDER-IS-FOUR-POINTS`) | (a) zero-GPU T0: compute α·κ from committed probe β records for every `cwd5` rung and the AdamW C10 cells; (b) κ {0.02, 0.03, 0.05} × 2 grains × 5 seeds | (b) 30 runs ≈ 21 GPU-h | none | registration | MUST |
| 1.6 | The route is identified: weight shrink vs meta-trace, and α-independent decay | **MISSING** (`DECOUPLED-NOT-TESTED`, 281.2; one flag moves both routes) | 3 variants at κ 0.1 on ResNet18_c100: shrink-only, trace-only, α-independent (matched on initial per-step shrink) × 2 grains × 3 seeds | 18 runs ≈ 13 GPU-h | 40-80-line opt-in patch like `PATCH_DECAYMASK` + inertness proof | registration | MUST (reviewers will ask) |
| 1.7 | The reversal (scalar > layerwise at 5e-4) replicates | **PARTIAL**: one network, 3 seeds (`G_W4`, 285) | PlainNet18_c100, VGG11_bn_c100, ResNet18/CIFAR-10 at κ 5e-4 (+0.1 anchor) × 2 grains × 5 seeds | 60 runs ≈ 35 GPU-h | PlainNet in isolated trees only; probe hard-codes 62 tensors | registration | MUST |
| 1.8 | N_eff predicts collapse early, out of sample | **MISSING** | (a) zero-GPU: compute N_eff from committed per-tensor probes (`ctd1`, `cct1`, `cwd5`) — does early N_eff separate C100 vs C10 and κ 0.1 vs 5e-4? (b) pre-register it on the new Phase-2 cells | (a) 0; (b) rides on other batches | analysis script only | — | MUST (it is the "insight") |
| 1.9 | A normalised-vote fix removes the collapse and loses nothing at 5e-4 | **MISSING** (earlier pooling designs M0/M1/zpool failed their controls, PRIOR-ART) | per-tensor-normalised (or median) vote × κ {0.1, 5e-4} × {ResNet18_c100, PlainNet, VGG, R18/C10, Tiny-ImageNet} × 3-5 seeds, vs scalar and layerwise, plus the tuned SGD+cosine row for context | ≈ 40-50 runs ≈ 35-40 GPU-h | new aggregation patch + proof | registration | NICE (MUST if framed as a method) |
| 1.10 | Holds on a transformer | **MISSING** | small ViT on CIFAR-100 (torchvision 0.15.2 builds it; 13 LN scales, 52 1-D tensors), AdamW base, κ {0.1, 1e-2}, LN gains decayed vs exempt, 2 grains, 3 seeds. A null is publishable scope | 24 runs; cost **UNMEASURED** (smoke job first; guess ≤ 1 GPU-h/run) | `--NN-name` entry, probe generalisation, augmentation/epoch recipe | registration | **MUST** for ICML (B3) |
| 1.11 | Holds on a language model | **MISSING, BLOCKED**: llama2.c on alice2 is code-only, hard-coded data path, no sentencepiece, its HF.py crashes at layerwise (feasibility; OPERATIONS §11) | TinyStories ~15M (the parent's own setup), AdamW, κ {0.1, 1e-2}, 2 grains, 3 seeds | 24 runs; cost UNMEASURED | LARGE: port granularity/guard/probe patches, re-stage ~7 GB | **Reza**: TinyStories licence (CDLA-Sharing-1.0), tokenizer licence UNSURE, staging | NICE on this cluster (the ViT stands in); MUST in an ideal paper |
| 1.12 | Scale beyond CIFAR | **PARTIAL**: Tiny-ImageNet 9.86 vs 50.83, IN-489 1.00 vs 49.21, single batches (LIMITS-PREP §2.2) | Tiny-ImageNet, κ {0.1, 5e-4}, 2 grains, 3 seeds, with attribution probe | 12 runs ≈ 19 GPU-h (7-day partition) | none | — ; ImageNet32/64 would need Reza's image-net.org login | MUST (Tiny-ImageNet); NICE (ImageNet32) |
| 1.13 | A toy model predicts the threshold | **MISSING** | analytic: noisy quadratic (Wu et al.) + one scale-variant gain group under α-scaled decay and a Lion/sign meta-vote; predict the capture threshold in α·κ and check against 1.5 | 0 GPU; ~1-2 weeks of Reza/Saber time | — | Saber (theory ownership) | MUST (B5) |
| 1.14 | Validation-split reporting | **MISSING** (CORRECTIONS 135.1) | 45k/5k split, re-select and re-report the headline cells (1.1, 1.3-1.4, 1.7, 1.9) on validation | ≈ 30 runs ≈ 21 GPU-h | split flag in the loader (small) | registration | MUST (B10) |
| 1.15 | 5+ seeds on every load-bearing contrast | **PARTIAL** (3 seeds) | top-ups folded into 1.5/1.7/1.9; plus 2 seeds on 1.1 | ≈ 20 runs ≈ 14 GPU-h | none | — | MUST for sub-1-pp effects; NICE for 40-pp effects |
| 1.16 | Practical context: tuned non-meta baseline | **HAVE**: `cdn1` +5.699 pp = +18.80 SE (171/175), `cau1` +3.617 = +9.92 SE (209), `cuc1` +12.178 = +26.05 SE (220) | re-run the MetaOptimize comparison arm at κ 5e-4 (the `cdn1` arm ran at 0.1) — cheap, removes the wd confound | 6 runs ≈ 4 GPU-h | none | — | MUST (fairness) |

### C2 — Decay decides granularity

Required claims = C1 rows **1.1, 1.2, 1.5, 1.6, 1.7, 1.8(a), 1.12, 1.14, 1.15, 1.16**, all as costed above. Drops 1.3,
1.4, 1.9, 1.10, 1.11, 1.13. Adds: none. **Cost ≈ 150-170 GPU-h.** Ceiling: TMLR strong; ICML weak (B1, B3 fail).

### C3 — Parent-conditional claim

| # | Claim | Status + evidence | Experiment | Runs / GPU-h | New code | Decision | Bar |
|---|---|---|---|---|---|---|---|
| 3.1 | The parent measured granularity only at κ = 0.1 | **HAVE**: parent Tables 2-4 (local text); PAPER-CONFIG.md; CORRECTIONS 254 | — | — | — | Saber to confirm SGDm-row alignment | MUST |
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
| 4.2 | **…and it is not a κ = 0.1 phenomenon** | **MISSING** | G3: core count-matched cells (chunk vs nodewise at two counts; ResNet18 on CIFAR-10 and CIFAR-100; SGDm+Lion) × κ {5e-4, 1e-2} × 3 seeds, plus scalar/layerwise in batch | 24-36 runs ≈ 17-25 GPU-h |
| 4.3 | Stale sentences ("1.8-4.2 pp", "none of nine mechanisms") updated | PARTIAL (project memory) | writing only | 0 |

---

## 4. Ranking and recommendation

Scores are my judgement: P = probability the experiments deliver an ICML-quality result; V = value if they do
(1-5); C = GPU-h + calendar cost.

| Rank | Candidate | P(ICML-quality result) | Value | Cost (GPU-h) | P×V/C (relative) | Verdict |
|---|---|---|---|---|---|---|
| 1 | **C1 vote capture** | ~0.25 (gated on 1.3/1.4) | 5 | ~400-450 + theory | **highest**, because Phase 1 is cheap and decisive | **PRIMARY** |
| 2 | C2 decay decides granularity | ~0.10 for ICML; ~0.7 for TMLR | 3 | ~150-170 | medium | **FALLBACK** (to TMLR, merged with C4 or standalone) |
| 3 | C4 audit | ~0.05 ICML; 0.8 TMLR (STATUS) | 2 | ~20-25 (G3) | high for TMLR, n/a for ICML | ship to TMLR regardless, after G3 |
| 4 | C3 parent-conditional | not an ICML paper; ~0.3 that P1 even shows an interaction | 2 (high sensitivity) | 28-83 | low standalone | fold into C1 **only** with Saber's agreement |

### Phased plan

**Phase 0 — zero GPU, ~1 week (do first; nothing needs registration).**
- T0: realised per-step shrink α·κ from committed probe β records (`cwd5` rungs, AdamW C10 cells). Tells us whether
  "κ 0.1 on SGDm" and "κ 0.1 on AdamW" are the same dose at all.
- N_eff from committed per-tensor probes (`ctd1`, `cct1`, `cwd5`). If early N_eff does **not** separate collapsing
  from healthy runs, the diagnostic contribution (1.8) is dead and C1 loses its central insight — a soft gate.
- Prior-art sweep (standing memory rule) focused on arXiv:2605.19095 §6.1 and anything newer on shared/global
  step-size adaptation × normalisation × decay; then Reza's go-ahead.
- Meet Saber: parent epochs/seeds/Fig. 1 pairings, any other κ ever run, Table 2/4 SGDm alignment, whether he wants
  P1, and who owns the toy-model theory (1.13).
- Decide the TMLR timing of the audit (dual-submission) and the public-repo anonymity question (B9).

**Phase 1 — the kill-or-continue gate, ~1.5 weeks, ≈ 55-60 GPU-h, ≈ 80 runs.**
- **G1** cross-method pilot (1.3): Baydin HD + Mechanic + Prodigy at ResNet18_c100, κ {0.1, 5e-4}. ≈ 17 GPU-h, plus
  the HD patch and two wrappers.
- **G2** standard-setting test (1.4): AdamW+Adam, Lion+Lion bases on CIFAR-100 at κ {0.1, 1e-2}. ≈ 17 GPU-h, no code.
- **G3** audit survival at 5e-4 (4.2). ≈ 17-25 GPU-h, no code. Serves the fallback, not the gate.
- **Gate rule (to be pre-registered):** continue C1 **iff** G1 shows collapse *and* top-3 vote dominance in ≥ 1
  non-MetaOptimize adapter, **or** G2 shows R50 collapse for AdamW or Lion at κ 0.1. Also require Phase 0's N_eff to
  separate at least the `cwd5` κ 0.1 vs 5e-4 arms. **If neither G1 nor G2 fires, C1 is dead**: write C2 + C4 for TMLR
  and stop spending on ICML scope (1.10, 1.11, 1.13).
- If Prodigy is immune and HD/Mechanic are not, that is still a pass, with the claim narrowed to adapters that can
  decrease the step size.

**Phase 2 — build the paper, ~4-6 weeks, ≈ 300-350 GPU-h** (only if Phase 1 passes). In order: 1.6 route patch; 1.5
located boundary; 1.7 reversal replication; 1.3 full cross-method; 1.10 ViT (smoke job first); 1.12 Tiny-ImageNet;
1.9 fix; 1.14 validation re-report; 1.15 seed top-ups; 1.16 κ-matched denominator arm; 1.2 O-13 (+ O-2 if Saber
agrees). P1 (C3) in parallel only on Saber's say-so. Theory (1.13) in parallel, human time.

**Phase 3 — optional, Reza-gated:** TinyStories LM arm (1.11); ImageNet32 (image-net.org terms, his login).

**Totals (estimates, not registered):** Phase 1 ≈ 55-60 GPU-h; Phase 2 ≈ 300-350 GPU-h; P1 +28-83; overall
**≈ 400-500 GPU-h, ≈ 550-700 runs**. alice2 delivered 301-545 GPU-h/week recently (sacct, feasibility stage), so GPU
is ~1-1.5 weeks of throughput; the real pacing limit is patches, inertness proofs and registrations (~40 jobs/night,
LIMITS-PREP §5.5). **Calendar: ~7-9 weeks of experiments + ~3-4 weeks of writing ≈ 10-13 weeks from go-ahead**, i.e.
late December 2026 at the earliest. Against an unverified late-January ICML 2027 deadline that is feasible but has
little slack; the theory item and the ViT recipe are the schedule risks.

---

## 5. The ceiling, stated plainly

- **Without Phase 1 passing, no candidate clears ICML with this cluster and this evidence.** C2/C4 are single-method,
  CIFAR-scale results with a self-conceded corner-case setting; the reviewer form's "limited evaluation" caps them at
  Weak Accept at best, and prior art (arXiv:2605.19095, 2305.17212, 2607.21005) makes "well-known result" objections
  likely.
- **With Phase 1 passing**, C1 is a credible ICML submission but still missing ImageNet-1k (impossible here) and,
  unless Reza unblocks TinyStories, a language model. The ViT arm and a toy-model theory are what substitute for
  them, following the Lobacheva (NeurIPS 2021) / Kosson (ICML 2024) precedent.
- **Best realistic venue if the gate fails: TMLR**, with the audit (after G3) and the decay × granularity mechanism
  either merged or as two papers; ReScience/MLRC for the reproduction angle. The C3 question, whatever it returns,
  goes to Saber, not into a venue.

---

## 6. What this file does NOT do

It registers nothing, launches nothing, and licenses no new sentence in any write-up. It names no threshold inside the
unrun 1e-2…0.1 decade. It makes no claim about the parent paper beyond what Table 2-4 state and what our own
committed runs show. Every experiment above needs its own registration, a prior-art check and Reza's go-ahead;
anything touching the parent needs Saber first.
