# Collaboration & Governance Spec — Hierarchical MetaOptimize

**Status:** advisory. Written 2026-08-18, 12 days into the declared project window.
**Bottom line:** nothing here looks like misconduct, and the framing "the premise does not reproduce" is currently **stronger than the evidence supports**. The governance job is (a) to get the facts on the record without turning a scoping question into an accusation, (b) to stop the science being hostage to reply latency, and (c) to fix a live data-loss and compliance exposure that is more urgent than any of the above.

---

## P0 — do these before you talk to anyone

| # | Action | Why it is P0 | Deadline |
|---|---|---|---|
| 1 | **Get an off-cluster master copy.** LIACS GitLab repo (code, configs, scripts, logs — *not* ImageNet) + Leiden Data Store collection for run outputs. | Your filed DMP *requires* this and it does not exist. Scratch has ~1 month retention, no backup, and holds the only copy of the authors' Jan-2024 run outputs. If scratch rolls, you lose the primary evidence for everything in this document, including the parent group's own historical artifacts. | 72 hours |
| 2 | **Freeze and tag the evidence bundle** (below) before you raise anything. | Raising a code concern without an immutable, reproducible record is bad for you *and* for Saber. It also forces you to check your own claims one more time. | Before message 1 |
| 3 | **Get the DMP signed by the PI.** | An unsigned filed DMP is a live non-compliance, and item 1 is the substantive obligation inside it. Bundle 1 and 3 into one ask — it is a favour to him, not a complaint. | Week 1 |
| 4 | **Stop launching new runs under `salehkaleybars`.** Migrate to `s5014158`. | Using another person's cluster account is an ICT-policy and attribution problem, and it muddies who ran what — exactly the thing you are about to be asking questions about. Read-only access to the legacy scratch data is a separate, fine request. | Week 1 |

---

## 1. How to raise it

### 1.1 First, correct your own framing — this is not optional politeness, it is accuracy

Three things you believe are, as stated, stronger than what you have measured:

- **"The premise does not reproduce."** The premise is scale-dependent: *layerwise helps small, loses at large*. You tested CIFAR-10/ResNet-18. CIFAR-10 is the **small** end. Your result — layerwise wins by +3.3pp under SGDm — is *consistent* with the premise, not a refutation of it. You have not touched the regime where the claim lives.
- **"Layerwise was never implemented."** You verified that the released path **raises `AttributeError` at the shipped commit**, and that the MetaStep branches contain type errors that cannot execute as written. "Never executed" is an inference about history you cannot observe. Say what you verified.
- **"Layerwise" may not mean what you think.** This is the single most likely resolution of the whole thing and you should hold it as the leading hypothesis. The paper reports CIFAR-10 with **6 blocks** and calls it something; you are calling **m=62** layerwise. If the paper's "layerwise" *is* the 6-block ResNet-stage partition, then there is no missing code path behind any published number, the released repo is simply scoped to what the paper used, and the "anomaly" is a comparison between two 6-block runs at different scales. Your m=62 is then a **new granularity nobody has run**, which is a contribution, not a discrepancy.

None of this weakens the real findings. The augmentation defect, the silent `--max-time` truncation, and the non-executability of the finer-granularity paths in the released code are all solid, and the weightwise collapse is a genuine and interesting result. Lead with those.

### 1.2 Reframe the whole conversation

Not: *"I cannot reproduce your paper and your code is broken."*
Instead: **"The failure mode is real but it has moved. It is not at layerwise, it is at weightwise — and it is a collapse, not a degradation. That changes what the hierarchical fix should be regularizing toward, so I need to check some configuration details with you before I commit a year to it."**

This is true, it is more interesting, and it makes the conversation about *your thesis scope* rather than about *his released artifact*. The code questions then arrive as a subordinate item — which is also their correct weight.

### 1.3 Sequencing (do not deviate)

1. **Saber alone, privately, first.** He is supervisor, PI, co-author, gatekeeper for the ImageNet logs, and the person with the most exposure. Going to Arsalan first — or to both at once — routes a concern about his code around him and will be read as an accusation regardless of your wording.
2. **Written note → meeting.** Short factual email requesting 45 minutes, with a 1-page memo attached. Do not put interpretation in the email; put observations in the email and interpretation in the room.
3. **Meeting order: results → scoping decision → config questions → code paths last.** By the time you reach the code, he already knows you are not attacking.
4. **After Saber has read it: joint session with Arsalan.** Saber decides whether he introduces it or you do; offer him the choice explicitly.
5. **After every meeting, send a written "as I understood it, we decided…" summary.** This is standard good practice and it is also the record that protects both of you if the correction question ever becomes live.
6. **Do not** file a public GitHub issue, open a PR, post on X, or mention it in any group channel before step 4 concludes. A public issue on his repo, from his own student, is the one action that would genuinely damage this.

### 1.4 What to send — the evidence bundle

One page, plus a linked repo. The page:

- Table of Gate 1 results as you have them, with n, seeds, and "still running" marked honestly.
- Three defects, each: one sentence, exact file and line, exact command, exact traceback or exact log line showing truncation at epoch 81/85.
- Your implementation of the finer granularities + the byte-identical-inertness evidence on untouched paths, offered **for their review**, not as a fait accompli.
- The beta/alpha diagnostics for the weightwise collapse (peak alpha 5.7e-5, tensors at beta=-23.8, frozen between step 37500 and 49900) — this is your best material, it is unambiguous, and it is new to them.
- An explicit "what I have NOT shown" box: no ImageNet, no per-granularity meta-LR tuning, alpha0 and meta-stepsize inherited from your scalar/6-block defaults.

### 1.5 Draft: email to Saber

> **Subject:** Gate 1 results — and a scoping question before I lock the thesis direction
>
> Hi Saber,
>
> Gate 1 on CIFAR-10 / ResNet-18 is essentially in and I would like 45 minutes this week, because the result points somewhere different from the proposal and I would rather re-scope now than in month six.
>
> Short version: with augmentation, 100 epochs, 3 seeds, under SGDm, granularity **helps** — scalar 88.09 ±0.16, 6-block 91.56 ±0.03, layerwise (m=62) 91.34 ±0.09. So at this scale I am not seeing layerwise underperform scalar. Where things do break is at **weightwise** (m = 11.17M): one SGDm seed peaked at 70% and then collapsed to chance. The diagnostics say it is not runaway beta — step sizes collapse toward zero (peak alpha 5.7e-5 vs 1.1e-2 at layerwise), whole tensors get driven to alpha ~5e-11, the network stops learning, gradients vanish, and Lion's sign(0) freezes beta. AdamW at weightwise survives but drops to 86.05. I have not ruled out that this is just a meta-step-size that was tuned for the coarse partitions, which is one of the things I want to ask you about.
>
> Two setup issues I hit that affect how earlier numbers should be read: the released CIFAR-10 pipeline has no augmentation, so ResNet-18 hits ~0 train loss in epoch 1 and there is no optimization headroom left to measure; and `train.py` has its own `--max-time` break inside the epoch loop that silently ended two of my runs at 81 and 85 epochs. I have fixed both locally.
>
> Third thing, and this is the one I most likely have wrong: I could not get `--granularity layerwise / nodewise / weightwise` to run from the released `cifar10 HF.py` — it recognises the names but I hit an `AttributeError` with no matching branch, and the corresponding branches in the MetaStep copy on scratch raise on `.cuda()` over a list and `torch.log` over a float. I have written my own implementations to get Gate 1 done, and I would really like you to check them, because if the paper's "layerwise" means the 6-block ResNet-stage partition rather than one block per parameter tensor, then I have been comparing against the wrong thing all along. Is there a branch or an internal version where those paths are active, and which commit produced the paper's numbers?
>
> I have put a one-page memo, the configs, the tracebacks and the beta diagnostics here: [link]. Nothing here changes my read that the direction is worth a year — if anything the weightwise collapse looks like a cleaner target than the original one. I just want us agreed on what we are fixing before I spend the compute.
>
> Best,
> Reza

**Notes on the draft.** The code question is fourth, in question form, with your own most likely error named before his. The numbers are unhedged. The three defects are stated flatly and are not negotiable. Nothing in it would embarrass anyone if forwarded, which it will be.

### 1.6 Verbal opener for the meeting (if he prefers to talk first)

> "The headline is that granularity helps at CIFAR scale, so the layerwise problem in the proposal isn't visible here — but weightwise collapses completely, and I think that's the more interesting failure. Before I re-scope around it I need to check I'm even measuring the same thing you were, because I couldn't run the finer granularities from the released code and had to write them myself."

### 1.7 On Arsalan

Different relationship: not your supervisor, not your assessor, no formal obligation to you, and the author of the premise you are questioning. Be more deferential on the science and more direct on the ask. The key question for him is 1(H) below — whether "layerwise doesn't help at ImageNet scale" came from a run or from a recollection. Ask it neutrally; the honest answer may well be "an impression from experiments we didn't keep," and if so **nobody did anything wrong** and the project simply gets a cleaner starting point. Make it easy for him to say that.

---

## 2. Questions that must be answered to unblock the science

Each has a **default** you will proceed under if unanswered. Send the list *after* the first meeting, numbered, in one document, with a stated date ("I'll assume the defaults from 5 September so I can keep the queue full"). Do not stall on any of them.

**Tier 1 — blocking; the thesis direction depends on the answer**

| # | Question | Why it blocks | Default if unanswered |
|---|---|---|---|
| A | **Exactly which parameters are in each block for every granularity reported in the paper, for both CIFAR-10 and ImageNet?** Ideally the partition map or the code that builds it. Is the paper's "layerwise" m=6 or m=#tensors? | If it is 6, there is no discrepancy at all and my m=62 is new ground. Everything downstream turns on this. | Assume paper's "layerwise" = 6-block; report my m=62 as a new granularity, not a reproduction. |
| B | **Was the ImageNet granularity run the same 6-block partition as CIFAR-10, or a re-derived partition for a deeper net?** | "Same 6 blocks" across a 18-layer and a 50+-layer net means very different blocks/parameter ratios; the anomaly could be entirely this. | Assume re-derived; treat the cross-scale comparison as confounded and say so. |
| C | **Is the statement "layerwise doesn't help at ImageNet scale" backed by a run, or is it a qualitative recollection?** If a run: can I see the logs/configs? | If recollection, the project's premise has no artifact behind it and the whole framing changes — benignly. | Treat as an unverified prior; do not cite it as an established result anywhere in the thesis. |
| D | **Which base optimizer (SGDm vs AdamW), with what lr, momentum, weight decay, and schedule, produced each reported figure?** | My scalar-vs-6-block gap is +3.5pp under SGDm and a dead heat under AdamW. The base optimizer changes the sign of the story. | Report both arms for everything; never a single-optimizer claim. |
| E | **Meta-optimizer: Lion or Adam? meta-stepsize, alpha0, gamma, eligibility-trace decay, any clipping/warmup on beta?** | Lion's `sign(0)=0` is mechanically implicated in my weightwise freeze. Under Adam the collapse may not occur. | Run the weightwise collapse under both meta-optimizers before attributing it to granularity. |
| F | **Was meta-stepsize tuned per granularity, or one value across all of them? What search budget?** | This is the single confound that could void the weightwise result entirely. | Assume untuned; run per-granularity meta-LR sweeps at equal budget before any claim about weightwise. Budget this — it is not optional. |

**Tier 2 — needed for a credible paper, not for the next experiment**

| # | Question | Default |
|---|---|---|
| G | Was the reported CIFAR-10 result produced with the released no-augmentation pipeline, or an internal augmented one? At what epoch budget and with what selection rule (best test acc vs final)? | State clearly in the thesis that my numbers are augmented/100ep/best-test and are therefore not directly comparable to the paper's table. |
| H | Which directories in the Jan-2024 scratch outputs correspond to which figure/table in the paper? | Treat them as uninterpretable; do not cite. |
| I | Is there a newer or internal MetaStep branch where the finer-granularity paths execute, and which commit produced the published numbers? | Cite the public commit hash and state that finer granularities are my implementation. |
| J | Did you ever observe weightwise collapse or near-zero-alpha freezing? Known failure, or new? | Report as new, with an explicit "not previously reported to our knowledge" hedge. |
| K | Can you share ImageNet logs/configs for the granularity comparison at all — or, if not, run a small confirmatory ImageNet arm together? | Cap thesis claims at CIFAR-10/ResNet-18 scale and say so in the abstract. |

**Tier 3 — governance, ask once, in writing**

| # | Question |
|---|---|
| L | The 5TB scratch ImageNet train dir shows 489 class dirs. Is that a partial copy, and where is the canonical one? What are the licence terms under which I may use it and publish derived logs? |
| M | May I release my implementations of the finer granularities publicly, and would you like them as an upstream PR to `sabersalehk/MetaOptimize`? Any embargo or IP constraint from Openmind / Alberta / Amii on Arsalan's side? |
| N | What is the repo's licence? (Verify yourself — if unlicensed, "public on GitHub" is *not* permission to redistribute a derivative, and this needs settling before any release.) |
| O | If it turns out any published number depended on a code path that does not execute in the release — do you want a repo note, a README erratum, or nothing? **This decision is yours and Arsalan's, not mine; I just need to know it was made.** |

---

## 3. Authorship and credit

**Do this now, before results exist.** An authorship agreement is nearly free to write in month 1 and nearly impossible to negotiate in month 10 when someone's expectations have already set.

**The governing framework** is the Netherlands Code of Conduct for Research Integrity, which binds Leiden staff and under which your thesis is assessed — not ICML's or NeurIPS's, which have essentially no authorship criteria. It requires that authorship reflect substantial contribution, that authorship be agreed as early as possible, and that all authors be accountable for the work. (I am confident about the substance; I would not quote article numbers without checking the current text.)

**Proposed allocation, to be confirmed in writing:**

- **Reza — first author of the paper.** Implementation of the finer granularities, all experiments, diagnostics, and writing.
- **Arsalan — co-author, not acknowledgement.** He originated the hierarchical partial-pooling idea. Idea origination of that specificity is a substantial intellectual contribution; treating it as an acknowledgement would be wrong even though he is not formally attached to Leiden. Being at a non-partner institution affects paperwork, not credit.
- **Saber — co-author.** Supervision, problem framing, resources, and parent-work continuity. Likely last author.
- **Sutton — not by default.** Co-authorship of the parent paper does not carry forward. Include only if he contributes to this one; that is Saber and Arsalan's call to raise, not yours.
- **Order between Saber and Arsalan:** let them settle it. Do not propose one.

**Specific points to settle in the same document:**

1. **Thesis ≠ paper.** The thesis must be demonstrably your own work with an explicit contribution statement; the paper can be co-authored. Confirm with the exam committee that a co-authored paper does not compromise the thesis assessment (it normally does not, with a contribution statement).
2. **The correction question is a co-author matter.** If the eventual paper says anything that amounts to a correction of the parent work's characterization of granularity, the parent authors must be co-authors and must have the chance to shape that framing. A student publishing "we failed to reproduce my supervisor's claim" without them would be both bad practice and self-destructive; publishing it *with* them is an honest, and frankly stronger, paper. Say this to Saber out loud — it converts him from exposed party to co-owner.
3. **Code attribution.** Your work is a derivative of their repo. Keep attribution and a clear MODIFICATIONS file listing the three defects and the added granularity paths. Settle the licence question (N) before release.
4. **Offer the upstream PR regardless of what happens with the paper.** It is the single strongest signal that you are contributing, not auditing.
5. **AI-tooling disclosure — treat this as a first-class integrity item, not a footnote.** You are planning to use PaperFactory, including its *front-half* idea/design stages, on a project whose central idea came from a named human. Three obligations:
   - Tell Saber you are using it, what it does, and which stages, **before** you use it on this project. Do not let him discover it from a writing style.
   - Keep an **idea-provenance log**: every claim, hypothesis, and design choice tagged human-originated / tool-suggested / tool-drafted-human-verified. Without it you will not be able to answer "where did this come from" about your own thesis, and the boundary between Arsalan's contribution and a generated one will blur — which is unfair to him and dangerous for you.
   - Declare AI use in the thesis per Leiden/LIACS rules and per the target venue's policy. LLMs are not authors; you are accountable for every claim regardless of what generated it.
   - **Hard rule:** no autonomous stage may generate, phrase, or judge any claim about your supervisor's code or the parent paper's validity. Those sentences are written by you, from verified artifacts, or not at all. This is exactly the failure mode where an automated red-team stage produces a confidently-worded accusation from an incomplete premise.
   - Also note PaperFactory's experiment backend targets a local RTX 2060, not ALICE — so its `experiment_run` stage cannot execute this project's experiments anyway. Use it for structure, not for evidence.

---

## 4. Relationship risks, and honest mitigations

The mitigations below are about *sequencing, scope, and record* — none of them require you to state a weaker finding than you have.

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Saber hears "your code never ran" as an accusation of sloppiness**, especially in front of Arsalan. | High if mishandled; low if sequenced | Private first. Question-form. Your own likely error (partition mismatch) named *before* his. Offer the fix and the PR. And say the true thing out loud: unreachable branches in a research repo are extremely common and are not an integrity issue. |
| **Structural conflict of interest**: your supervisor is a co-author of the work your findings bear on, *and* he grades your thesis. | Present now, unavoidable | Name it early and neutrally — "I want a second reader involved from the start given the overlap." Get the second examiner appointed in month 1, not month 10. Keep written meeting summaries. Route any correction decision to the authors (and, only if it ever became necessary, the faculty integrity route) — never make that call yourself. |
| **You overclaim refutation from CIFAR-only evidence** and are corrected in public later. | Currently high — this is the live one | Put the scope limit in the abstract, not the limitations section. "We do not test the ImageNet regime where the original claim is situated." You lose nothing; the weightwise collapse carries the paper. |
| **Your own implementation is wrong** and the whole discrepancy is yours. | Non-trivial. You have verified inertness on untouched paths, which is good, but not correctness of the new ones | Ask them to review it explicitly. Add a differential test: your m=6 path must reproduce the shipped blockwise path bit-for-bit. If it does not, you have your answer before you have an argument. |
| **The project is redefined over your objection** — "do the hierarchical fix anyway." | Moderate | Do not fight it in the meeting. Propose a dated decision gate with pre-registered criteria: "if per-granularity meta-LR tuning does not rescue weightwise by [date], we target the collapse; if it does, the hierarchical prior is the right fix and we proceed as proposed." Agree the gate *before* running it. Get it in the written summary. Also: a fix that works on a failure you can *induce and characterize* is still a good thesis — this is not a lost year either way. |
| **Slow or no replies**, blocking you for weeks. | High, structurally — Arsalan has no obligation to you | Every question in §2 ships with a default. State the date you will adopt them. Do not send reminders about the code questions; send reminders about the config questions, which are uncontroversial and which they can answer in ten minutes. |
| **Escalation temptation.** | Low now, but worth pre-deciding | Nothing you have found currently warrants the confidential integrity counsellor or the faculty integrity committee. What would: being instructed to suppress a verified negative result, or to report numbers you know were produced by a truncated or unaugmented run. Pre-decide that line now, while it is hypothetical, so you are not deciding it under pressure. |

**What you do not soften, in any version, to anyone:** the three defects and their consequences; that the released code does not execute the finer granularities at the shipped commit; that all unaugmented comparisons are void; that runs truncated at 81/85 epochs are non-comparable; the Gate 1 numbers as measured; the weightwise collapse and its mechanism. State these plainly and in writing. Everything above is about *ordering and interpretation*, never about deleting a fact.

---

## 5. MSc-thesis obligations not to forget

Procedural details below are the ones I'd expect at LIACS; **verify each against the current LIACS MSc thesis regulations and your study adviser** — I am confident about the categories, not about form names or portal specifics.

**Immediate (this month)**
1. **Off-cluster master copy** — GitLab + Leiden Data Store. See P0. This is your #1 obligation and your #1 practical risk simultaneously.
2. **PI signature on the DMP.** Unsigned = non-compliant. Pair it with the storage setup so it is one meeting, not two.
3. **Thesis registration**: LIACS MSc project registration / project agreement, supervisor and **second examiner** formally recorded, correct thesis course enrolment for ECTS. Do not let the second examiner slot stay empty — see the conflict-of-interest row above.
4. **Account migration** to `s5014158` for all new runs; separate read-only request for the legacy scratch data.
5. **Written authorship agreement** (§3), signed by all three.
6. **Ethics/privacy**: no human subjects, so almost certainly no ethics review — but confirm once and record the answer. ImageNet's terms restrict redistribution: it must never enter GitLab or the Data Store, and check whether publishing derived logs is permitted.

**Ongoing**
7. **Decision log** — every meeting, every default adopted, every gate criterion, dated. Ten minutes a week; it is your defence, your methods section, and your DMP evidence.
8. **Pre-register gate criteria before running the gate.** Especially the meta-LR-tuning gate, where you have an outcome you'd prefer.
9. **AI-use declaration** maintained continuously (§3.5), not reconstructed at submission.
10. **Compute accounting** — the ~1400 A100-hour estimate (700–3500) is unfunded and per-user-capped at 2× A100-80G. Per-granularity meta-LR sweeps (question F) are *not* in that estimate and will materially increase it. Re-estimate with F included and tell Saber the number before you queue it.

**Deadlines**
11. Project window 06/08/2026 – 06/08/2027. Rough venue positions relative to it (**verify the 2027 dates — do not plan against my recollection**): ICML abstracts late January, ICLR late September, NeurIPS abstracts ~May, TMLR rolling.
12. **Recommend TMLR as the primary target.** Rolling submission removes deadline risk from a one-year unfunded project with an unresolved premise; TMLR evaluates claims-versus-evidence rather than perceived impact, which suits a careful CIFAR-scale result with an honest scope limit and a genuine negative finding; and it does not punish you for the paper the project turns out to be rather than the one that was proposed. Keep a conference as an opportunistic secondary if the weightwise story gets an ImageNet arm.
13. Work backwards from thesis submission, not from the venue: thesis defence scheduling, second-examiner reading time, and any faculty deadline for the defence typically bind earlier than you expect.