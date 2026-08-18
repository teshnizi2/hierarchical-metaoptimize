# Completeness Critique — what all five reports still miss

## (a) Not covered by any report

**A1. The IDBD/Autostep lineage — the direct ancestor, absent from all five.**
MetaOptimize is a descendant of IDBD (Sutton 1992), which is *per-weight by construction*, and of Normalized-IDBD/Autostep (Mahmood, Sutton et al. 2012), which exists **specifically because per-weight meta-learned step sizes are unstable unless the meta-update is normalized by a running estimate of the meta-gradient's own magnitude**. Your weightwise collapse may be the known IDBD failure, and M3-style normalization may be the known 30-year-old fix. Also missing: hypergradient descent (Baydin et al.), SMD (Schraudolph), MARTHE, Adam-mini. Blind-spots caught LARS/LAMB/μP (prescriptive per-layer) but not the *meta-learned* per-weight family — which is the closer relative, and Sutton is a co-author of the parent paper. **Cost to resolve: one afternoon of reading. Risk if skipped: the mechanism section and the method are both potentially non-novel.**

**A2. The public record on the parent paper was never consulted.**
ICML 2025 → OpenReview reviews, rebuttals, and the arXiv v1→vN diff for 2402.02342 are public and free. They very likely state what granularity was run, whether reviewers asked about ImageNet, and whether "layerwise" means 6 blocks or 62 tensors — i.e. Tier-1 blocking questions A, B, C in the Collaboration spec. Every report routes those questions through a human who may take weeks to answer. Read the public record *before* sending the email; it may also change what you ask.

**A3. No derivation, and no identifiability analysis, of the hierarchical estimator itself.**
Five reports argue about *whether* to build M1/M3 and nobody writes down what it is. Specifically unaddressed:
- β_b = β₀ + δ_b is **overparameterized by one degree of freedom** (β₀+c, δ_b−c is observationally identical). Without a constraint (Σδ_b = 0, or λ > 0 acting as the identifying prior) there is a flat direction in the meta-parameter space. Under a sign-based meta-optimizer that flat direction is a random walk, not a null-space you can ignore.
- λ and η_δ are **not separately identifiable under sign updates** (Lion moves δ by ±η_δ regardless of gradient scale). A "λ sensitivity curve" measured at fixed η_δ is meaningless.
- ∂/∂β₀ = Σ_b z_b exactly. So the global level under a *linear* meta-optimizer is literally the scalar arm — M1's entire content lives in the sign nonlinearity and in η₀ ≫ η_δ. Nobody has stated this, and it determines whether M1 is a method or a reparameterization.
- No cost analysis: the eligibility trace H at two levels, at m = n, in memory and time.

**A4. κ·α coupling means per-block α *is* per-block weight decay.**
`H_{t+1} = γ(1−κα_t)H_t + Δw` and the coupled decay κ mean that changing α per block changes the effective regularization per block. So "granularity of step size" and "granularity of weight decay" are not separated anywhere in the design. The +3.3pp scalar→6-block gap under SGDm may be a *regularization-granularity* effect. Blind-spots gets adjacent (Q6: optimization vs generalization) but never names the coupling. Free control: run one arm with κ decoupled from the learned α.

**A5. Nodewise/channel-wise is implemented and is not a first-class arm anywhere.**
The grid everyone plans is {1, 6, 62, n}. The student implemented **nodewise**, and ~10³–10⁴ channel blocks is exactly the granularity LARS, Adam-mini, and μP operate at — i.e. the point where the "prescriptive works, learned fails" comparison is sharpest, and the most likely location of the actual cliff between 62 and 11.17M. Research mentions "~500 (channel-wise)" once, in P2; it should be a headline arm.

**A6. No person-time budget, and no thesis-writing time.**
Compute is free; the student is one unfunded person. The three "next ten days" lists (Research §2 P0–P9, Infra §7, Blind-spots §7) contain ~40 items and, honestly costed, ~6–10 weeks of *human* work — much of it serial (harness → sweeps → analysis). Nobody allocated the 8–12 weeks of thesis writing, the second-examiner reading window, or the fact that a 250-run campaign produces analysis load, not just results. This is the schedule the project will actually be judged against and it does not exist.

**A7. No small-scale development testbed for the method.**
All method work is gated behind full CIFAR gates. A 200-parameter MLP where the full-batch meta-gradient is exactly computable would let M1/M3 be derived, debugged, and its λ/η_δ identifiability checked in minutes rather than GPU-days. Research proposes such a net for finite-difference *validation* but not as the method's development environment.

**A8. Nobody plans the artifact the *thesis* is (chapters, contribution statement, what a null result looks like as a defended document)** — only the paper is planned, in three different ways.

---

## (b) Contradictions between reports that require a decision

| # | Conflict | Who says what | Decision needed |
|---|---|---|---|
| **B1** | **Is the premise falsified?** | Research §0 and Paper §0: "the premise is dead / falsified at CIFAR scale," and Research's entire re-aiming follows from it. Collaboration §1.1: CIFAR-10 **is** the small end, so your result is *consistent* with the premise, not a refutation. Paper §1 agrees ("you have not contradicted the parent paper"). | Research's whole reframe rests on a reading that two other reports call an overclaim. Settle this **before** the email to Saber, because the email's framing encodes the answer. |
| **B2** | **Is the weightwise collapse the spine, or a numerical artifact about to dissolve?** | Paper makes it narrative A+B — the paper's core. Blind-spots §1.2 [MED→HIGH] and Research §4 (Event B) both say it is probably fp-underflow + `sign(0)=0`. | Nobody wrote the conditional: **if fp64 + a β floor dissolve the collapse, Paper's recommended narrative has no core and Gate A doesn't catch it** (Gate A tests tuning only). Add a numerics gate *upstream* of Gate A, and pre-decide the narrative if it fires. |
| **B3** | **Primary metric.** | Infra §2.4: keep best-test-accuracy "for comparability with the parent paper." Research §3 and Blind-spots §1.4: it is test-set selection and a biased estimator whose bias scales with the treatment. | Pick one primary. (Recommended: final-epoch + last-5-mean primary, val-selected secondary, best-of-100 logged and reported *only* in the parent-comparison table.) |
| **B4** | **Run under the PI's account?** | Infra §6.3 builds the 40–80× throughput plan on **two accounts, one of them the supervisor's**, plus a `setfacl` on his directory. Collaboration P0-4: stop launching under `salehkaleybars` — ICT policy, attribution, and it muddies "who ran what" exactly while you raise a code question. | These are incompatible. Note the throughput plan loses half its ceiling under Collaboration's rule — and Collaboration is right. |
| **B5** | **PaperFactory front half — specifically `novelty_gate`.** | Research §7: run `novelty_gate` and `hard_questions` on the reframed RQs. Blind-spots §5: use `novelty_gate`. Paper §10: **do not use the front half**, naming `novelty_gate` explicitly. Infra §4.3: back half only. | 2–2 split on one stage. Given A1 (unread prior art), a novelty check is genuinely needed — but do it by reading IDBD, not by running a stage configured for small-LLM fine-tuning. |
| **B6** | **Are κ, γ, ρ frozen or swept?** | Research §3 freezes everything but (η, α₀) — "two tunables is the right scope." Blind-spots §3.3 makes **κ the candidate mechanism** (α-dependent trace horizon → stale trace → self-reinforcing collapse). | If κ is frozen, H7-trace is untestable and the campaign cannot distinguish it from H1/H7-skew. Add a κ-decoupling arm or drop the hypothesis explicitly. |
| **B7** | **Run the unaugmented config or not?** | Research and Paper: all unaugmented comparisons are void; never scheduled. Blind-spots §0.3: it is the **only external anchor** that can verify your scalar/6-block paths match the authors'. | "Void for science ≠ void for verification" is correct and unrebutted. Schedule 3 unaugmented runs as verification-only, clearly labelled. |
| **B8** | **The scale point.** | Research: ImageNet-64. Paper: ImageNet **or a ~100M transformer LM** (and says the LM is arguably better in 2026). Infra: TinyImageNet or ImageNet-100. Blind-spots: full ImageNet is now affordable, ~30–40 A100-h/run. | Four different answers, and the cost estimates disagree by ~3× (Research 500–900 A100-h; Blind-spots ~30–40/run). Pick one and cost it once. Note Blind-spots' figure × 5 granularities × 3 seeds = ~600 A100-h at a **2-A100 cap** = ~13 days wall-clock minimum. |
| **B9** | **Seed policy.** | 3 (current), 5 (Research headline, Infra), 8+ with Clopper–Pearson (Research §4, collapse as Bernoulli). | One written policy, per claim class, pre-registered. |
| **B10** | **Equivalence-test tolerance.** | Collaboration §4 and Research P0: the new 6-block path must reproduce the legacy path **"bit-for-bit."** Blind-spots §1.1: "to float tolerance, step for step." | Bit-for-bit across different reduction orders with `cudnn.benchmark=true` is unachievable and will fail for benign reasons, burning days and possibly producing a false "my implementation is wrong" panic. Specify: exact match on step 1 under deterministic mode; tolerance-based thereafter. |

---

## (c) Recommendations that are unsafe, unethical, or unsound

1. **Infra §1.2 Step A — `tar` the PI's scratch directory and `scp` it to the student's Mac.** This copies another person's account data (including the authors' unpublished Jan-2024 run outputs, and a tree adjacent to an ImageNet copy with redistribution restrictions) off-cluster without permission, and stages it in `/tmp` on a shared login node in the meantime. Snapshot **only the student's own work**, to the student's own `/zfsstore`, and ask before moving anything of Saber's or anything ImageNet-derived off ALICE. *(Unsound as written; also directly contradicts the same document's own ImageNet licence caveat.)*

2. **Blind-spots §1.2 — "try `sign(0) → +1`."** As a *diagnostic* it is fine. As a fix it is wrong: at m = n a large fraction of coordinates will have exactly-zero meta-gradient, so `sign(0)=+1` injects a systematic upward drift into every dead coordinate — trading a collapse for an unjustified divergence. The correct interventions are fp64 accumulation, a β floor / α clamp, and an explicit underflow counter. Do not let this reach the method section.

3. **Infra §6.3 — saturating ~84 GPUs across two accounts on a shared, free university cluster.** Even with the etiquette caveat attached, the plan's ceiling *depends* on using someone else's quota for your work. That is quota circumvention regardless of who holds the credentials, and it is the same account whose owner's code you are about to raise questions about. Drop to one account; the 12–42× improvement on the current one-job-at-a-time cadence is more than enough.

4. **Paper §6 Step 4 — "the co-authorship judo."** The substance (self-disclosure by the original team) is right. The framing — push for it because it "neutralizes the criticism" and reviewers read it as integrity — instrumentalizes an authorship decision for reviewer perception. State the reason plainly instead: the parent authors must be able to shape any statement about their own work. Same action, defensible motive.

5. **Research §3 — "pre-register... before looking"** is prescribed *after* several arms have already been run and the reframe written. Pre-registration applied to a hypothesis derived from the data you already saw is not pre-registration. It is still worth doing, but the document must say which analyses are confirmatory (new data) and which are exploratory (Gate 0/1). As written it would misrepresent the epistemic status of the campaign.

6. **Infra §2.4's "keep best-test-accuracy for comparability"** — keeping it is fine; keeping it as the *reported* number is selection on the test set, and at least one cell (weightwise 70.09 → 10.00 reported as 70.09) is already actively misleading. Not a strategy question; a correctness one.

---

## (d) The single most under-weighted risk

**Single-person serial capacity — the project's actual binding constraint, mentioned once and then ignored.**

Blind-spots states it in half a sentence ("the binding constraint is now your attention and analysis throughput, not GPU-hours") and then adds seven more work items. The five reports collectively prescribe, as "cheap" or "do today": a git/GitLab/GitHub/LDS migration, a provenance schema and run harness, an aggregation + figure pipeline, a six-test implementation-validation suite, a frozen-point SNR instrument, a random-partition probe, an ImageNet audit, a PaperFactory integration spike, an authorship agreement, a DMP signature chase, a pre-registration document, a 160-run tuning campaign, a 60-run granularity curve, a 24-run horizon sweep, a 40-run collapse study, and a delicate multi-party conversation — for one unfunded MSc student who also has to write a thesis inside twelve months, of which twelve days are already gone.

Every other risk in these documents has a bounded fix (backups: two hours; ImageNet: one audit job; the tuning confound: 160 free GPU-hours). This one has no fix, no owner, and no slack — and it is the mechanism by which all the others actually bite: the backup doesn't get made because the sweep is queued; the equivalence tests get skipped because the results look plausible; the email doesn't get sent because the framing needs another day. **Nothing in the five reports converts the prescriptions into a dated, ordered, capacity-checked plan with items explicitly cut.** Until roughly half of the above is deleted or deferred in writing, the realistic outcome is a partially-instrumented campaign, an unvalidated implementation, and an unfinished thesis — not because any single recommendation was wrong, but because all of them were adopted.

Adjacent and also under-weighted: **prior-art risk (A1)**. If Autostep/normalized-IDBD already contains both the collapse and the shrinkage-flavoured fix, the method contribution shrinks to a re-derivation — and that is discoverable this week, for free, before ~600 GPU-hours are committed to it.