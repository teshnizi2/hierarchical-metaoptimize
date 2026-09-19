# WRITEUP — the mechanism line as a bounded secondary contribution

*Draft for Reza, to read and to take to Dr Salehkaleybar. **NOT paper text and NOT for submission.** Nothing under
`paper/` was read into this file and nothing under `paper/` was touched. Written against `master` at commit **`84e4bcb`**,
corpus **3,253 rows / 3364.4 GPU-hours** (`results/all_runs.csv` at `66a19fb`). Every number below was re-derived from a
committed scorer or parser output under `results/`; where a number is a census figure rather than a scorer figure, it says
so. Prose in this file is mine; the branch words, licence sentences and bars are the registered ones and are quoted, not
paraphrased. Written 2026-09-19 at CORRECTIONS **276**. **ZERO GPU. No Slurm job. `alice` — Saber's shared account — not
contacted.** RULE 16 held: no registered scorer, launcher, patch, `analysis/argsline_guard.py` or
`analysis/corpus_exclusions.py` was edited.*

***REVISED 2026-09-19 at CORRECTIONS 277**, against `master` at `2ab824c`, after a hostile referee pass **rejected this
draft as it stood**. Eight failures were raised; **all eight are applied** — four substantive over-statements (§1.2 R1–R4),
the `cdep1` SE mix-up (§2 preamble, T6), the unsourced headline (new **E0**), and six omissions in the limits (**T12–T17**).
**Two further errors I found while re-checking every number in §2 against its artefact are corrected and disclosed, not
buried**: the min-|w| bound in §3.2 was `cwd2`'s quoted as if it covered `cwd1` too (T17), and T7's floor-discipline list
named three FINALs where the committed outputs carry five. **Every number in §§2.0–2.6 was re-derived from the committed
artefact named in its row before this revision was written, and RULE 20 for `cwd3` was re-run at full coverage 15/15
first (277.1).** Still **ZERO GPU**, still nothing under `paper/` read or touched, still RULE 16.*

---

## 0. Bounds, led with

Before any claim, the **eight** things a reader must be told in the same breath as the result *(the eighth was added at
CORRECTIONS 277; the referee's first and second failures were both that §1 stated it as a magnitude and hid the
composition)*:

1. **It is a SCOPE result, not a mechanism.** Naming a precondition is not identifying a route. §3 states exactly what is
   not shown and why the instrument cannot show it.
2. **The measured arms are the wrong arms.** `PATCH_DECAYMASK` writes `dm_norm` / `dm_absmin` / `dm_small` **only where
   the mask is on**, so the arms that actually collapse (`cwd1` `k01`; `cwd2` `k01`, `HIGHHEADPATH`) carry **no**
   weight-norm record at all (CORRECTIONS 274.1, per-arm table).
3. **On ResNet the decay was never removed from the three carriers alone.** `cwd1`'s mask is the **20 BatchNorm scales of
   the whole network**, `bn1` through `layer4` (271.4(1), 271.5 live-model check). The carriers are three of the twenty.
   The single-tensor sentence is earned on **PlainNet only** (`cwd2`, idx 50).
4. **`F_WD` = 1.012 is PlainNet-only**, one tensor, one dose, one cell, with the complement forced onto a replayed path
   (`COMPLEMENT-ON-HEADPATH`, `HELD-ARMS-OPEN-LOOP`).
5. **The 98.06 % figure is a CROSS-BATCH ratio and is orientation only** (271.6 F4, UNSURE): different interventions,
   different batches, no shared bar, no shared seed. It is not a decomposition and not a residual measurement.
6. **One configuration, one horizon, three seeds, axes one at a time.** CIFAR-100 (plus one CIFAR-10 association cell),
   `ResNet18_c100` / `PlainNet18_c100` per axis, 100 epochs, SGDm(0.99, wd 0.1) + Lion, meta step 1e-3, α₀ 1e-6.
   Coupled decay only — **decoupled weight decay is untested everywhere.**
7. **Two of the necessity statements are on modified algorithms** (`csv1`'s shadow vote is counterfactual; every hold is
   an exogenous step-size trajectory). A reviewer will name them as algorithm interventions, and §6 of `LIMITS-PREP`
   predicted exactly that.
8. **The count-matched control is a FLOOR BOUND, and it is not class-pure.** `cdep1`'s DEPTH arm is **inside** the
   registered saturation band, so the only entitled statement is `D_DEPTH ≤ 5.0 pp` — **never "recovers none of it"**
   and never a point effect (`DEPTH-FLOOR-SATURATED`, 164.6). And the triple contains **one BatchNorm shift**,
   `layer4.0.bn1.bias`, not three scales; the class-pure pair `DEPTH2` {47, 56} gives the same bound
   (`D_DEPTH2` +0.0960 pp, `DELTA_BIAS` +0.0727 pp = +0.10 SE), so the result does not rest on the shift — **but it does
   not become a magnitude either.**

---

## 1. The claim, in one paragraph

This is the **corrected** version of the paragraph proposed at CORRECTIONS 273.12. Four over-statements in that draft are
struck; §1.1 lists them with the evidence. **A hostile referee pass at CORRECTIONS 277 struck four more**: a floor level
read as a magnitude, an undisclosed BatchNorm shift in the count-matched control, the word "large" for the held step, and
a condition asserted from one uncontrolled arm. **The paragraph below is the version after all eight strikes**; §1.2 lists
the referee's four with their evidence.

> The headline of the paper is unchanged: the **denominator** result — a properly tuned non-meta baseline is not beaten by
> MetaOptimize, measured most strongly on CIFAR-100 (the campaign's own registered result, `cuc1`: CORRECTIONS **220**,
> MASTER-TABLE row 19 moved `OPEN` → `CONFIRMED, RESCOPED` at **229**; see **E0**) — together with the **count-matched
> partition audit**. The mechanism
> line is a **bounded secondary contribution, stated as a configuration-conditional failure mode and never as a property
> of BatchNorm or of the method in general**: *Under coupled L2 weight decay applied to normalisation scales — a
> configuration common practice avoids (He et al., arXiv:1812.01187) — a single shared meta-learned step size collapses on
> CIFAR-100, on both a residual and a residual-free 18-layer network. At the ResNet-18 cell the shared Lion meta-update's
> vote is dominated by three last-block BatchNorm scales, and giving those three their own step-size group recovers the
> whole scalar-to-layerwise gap, while a count-matched non-carrier triple in the same layer **stays on the floor**: its
> level sits inside the registered saturation band, so the batch's own scorer entitles us to the **bound**
> `D_DEPTH ≤ 5.0 pp` and **not** to a point effect, and "recovers none of it" may not be written. (**Disclosed**: that control triple
> contains one BatchNorm **shift**, `layer4.0.bn1.bias` (idx 48), not a scale. The answering arm is in the same artefact —
> the class-pure scale-only pair {47, 56}, `D_DEPTH2` **+0.0960 pp**, itself a floor bound `≤ 5.0 pp`, with
> `DEPTH − DEPTH2` **+0.0727 pp = +0.10 SE**. The result does **not** rest on the shift member.) At PlainNet's measured
> dose (`tri:9428`), any one of those three, held alone in its own group while the other 61 tensors share one step size,
> is **sufficient** to stall the ResNet run. Whether that requires the other two to keep voting in the shared sum is
> **INDICATED, not established**: it rests on a single arm (`ISOSPLIT`), there is **no free-split control**
> (`NO-FREE-SPLIT-CONTROL`), and it is the narrowest margin of the cycle — `P_SPLIT` **+3.0767 pp**, only 1.9233 pp =
> **3.46 SE** inside its 5 pp bar. Removing the coupled decay removes the collapse at
> every grain we tested: from every tensor and the meta trace on ResNet; from the **twenty** BatchNorm scales of the whole
> ResNet network (4,800 of 11.2 M parameters — **a network-wide mask, not the three carriers; we have no ResNet arm that
> removes the decay from the carriers alone**); and from a **single** BatchNorm scale on PlainNet (512 parameters), where
> it also removes the damage of an externally held step **at that same dose** on that same tensor **to within the noise
> floor** (`F_WD` = 1.012, the excess being `P_LEFT` −0.6253 pp = −1.12 SE, inside the 2.0 pp null bar; **PlainNet
> only**). We
> do not identify the route by which the decay acts: our instrumentation records a carrier's weight norm only in the arms
> where the decay is off, and in those arms the scales **grow** rather than shrink, so the arms that actually collapse
> carry no measurement. **This is a scope and precondition result, not a mechanism.***

Two sentences may be added, and no more:

* The isolation rescue **transfers to a second meta step size** (3e-4: `D_ISO` +41.1567 pp) **while the vote-dominance
  nomination does not** (`DOM_C` 0.4727 against a 0.50 bar) — so at that cell the rescue and the nomination are **not
  locked together** (CORRECTIONS 268).
* Each number in the paragraph is a **one-cell** number and must carry its cell.

### 1.1 The four over-statements struck from 273.12, each with its evidence

| # | 273.12 said | Why it is not earned | Corrected form used in §1 |
|---|---|---|---|
| **O1** | "carried by a small number of **last-block** BatchNorm scales … removing the coupled decay from **those scales alone** — 4,800 of 11.2 M parameters on ResNet" | The 4,800 parameters are the **20 BatchNorm scales of the whole network**, `DECAY_MASK=normscale`, derived twice and once on the live model (271.4(1), 271.5; `results/cwd1_livemodel_normscale_check.txt`). The three carriers are 3 of those 20; **17 non-carrier scales are unmasked in the same switch.** No ResNet arm masks the carriers alone. The sentence conflates the *nomination* set (3, last block) with the *mask* set (20, network-wide). | The grain is named at each cell: every tensor + meta trace (ResNet), 20 network-wide scales (ResNet), one scale (PlainNet); and the ResNet gap is stated as a gap. |
| **O2** | "removes the damage of an externally held large step on the carrier (**F ≈ 1.0**)" as a general clause | `F_WD` = 1.012 is `cwd2` only: `PlainNet18_c100`, idx 50, one dose (`tri:9428`), 3 seeds, complement forced onto `cvt6`'s replayed head path. There is **no ResNet held-step arm under a decay mask at all.** | "(F = 1.012, **PlainNet only**)". |
| **O3** | "a reader who follows that practice **will not meet** the collapse" | A prediction about all readers from three cells. What was measured is that the collapse **did not occur at any cell we tested with the decay removed** (`cmo1` W0, `cwd1`, `cwd2`). | §5 states it as "did not meet it at any cell tested", never as a claim about readers. |
| **O4** | "the norm scales **recover 98.06 %** of the whole-network effect" used as a decomposition | `cwd1`'s `P_NWD` +47.8247 against `cmo1`'s `L_W0` +48.7713 is a **between-batch** ratio: different interventions (20 tensors vs every tensor + the meta trace), different batches, no shared bar, no shared seed — labelled UNSURE, orientation only, at 271.6 F4 and 271.7. | Quoted once, explicitly labelled **orientation, cross-batch, UNSURE**, and never used to license a residual. |

### 1.2 The four over-statements struck by the referee pass at CORRECTIONS 277, each with its evidence

Every row below was **re-derived here from the committed artefact named**, not taken from the referee's summary.

| # | the 276 draft said | why it is not earned | corrected form used in §1 |
|---|---|---|---|
| **R1** | a count-matched non-carrier triple "**recovers none of it**" | `cdep1`'s own registered scorer forbids that reading: *"`DEPTH` level 23.5207 is INSIDE the registered saturation band [21.0940, 27.9520]: its level is a **BOUND, NOT a magnitude**. Entitled: `D_DEPTH <= 5.0 pp`. NOT entitled: the point value as an effect size, or any residual against the floor read as agreement (`164.6`)"* — and the FINAL carries `DEPTH-FLOOR-SATURATED`. "Recovers none" is a point claim about a floor-saturated level. | The **bound** `D_DEPTH ≤ 5.0 pp`, stated as a bound, with the floor discipline named. `cdep1` is added to T7's floor-reading list. |
| **R2** | "a count-matched non-carrier triple **in the same layer**", with no disclosure of what is in it | `cdep1`'s manifest: `DEPTH`'s isolated group is `layer4.0.bn1.weight` (47), **`layer4.0.bn1.bias` (48)** and `layer4.1.bn1.weight` (56). **Idx 48 is a BatchNorm SHIFT, not a scale** — so a "same-class" reading of the control is wrong for one of its three members, and a referee finds it in the artefact before we disclose it. | The shift is **disclosed by name**, and the answering arm — already in the same artefact — is cited: the class-pure pair `DEPTH2` {47, 56}, `D_DEPTH2` **+0.0960 pp** (also a bound), `DELTA_BIAS` = `DEPTH − DEPTH2` **+0.0727 pp = +0.10 SE**, FINAL `BIAS-NULL`. The result does not rest on the shift member. |
| **R3** | "held alone at a **large** step size"; "an externally held **large** step" | The draft strikes exactly this word at §2.4 as a RULE 16 defect (272.6 F1): only the clamp floor and **one** measured dose (`tri:9428`) were ever run, so no dose ladder licenses "large". Using it in §1 while striking it in §2.4 is the same over-statement, twice. | "large" is removed from §1 and replaced by the dose that was run — **"at PlainNet's measured dose (`tri:9428`)"** — everywhere. (Where §1.1 **quotes** 273.12 verbatim the word stays, because that is the record of what was said.) |
| **R4** | "— **provided** the other two still vote in the shared sum" (asserted as a condition) | One arm, `ISOSPLIT` (`cvt10`), carries it. `cvt10`'s own FINAL stamps `NO-FREE-SPLIT-CONTROL`: there is **no** free `[59,1,2]` arm, so `ISOSPLIT`'s non-stall cannot be separated from the `[59,1,2]` partition simply rescuing on its own, as `ISO` does. And `P_SPLIT` **+3.0767 pp** is the **narrowest margin of the cycle**, 1.9233 pp = **3.46 SE** inside its 5 pp bar (every other deciding contrast in §2 clears by 30–100 SE). | Downgraded to **INDICATED, not established**, with the single arm, the missing control and the margin all stated in the same sentence. |

**Provenance note, stated because it matters.** My brief named these four as findings of "the final audit". I could not
locate an audit report under `docs/`, `results/` or the scratchpad at `84e4bcb`; CORRECTIONS **274** is an addendum that
corrects four *descriptive `dm_*` record counts*, which is a different list. **Every one of O1–O4 above was therefore
re-verified by me against the committed record named in its row**, not taken on the brief's authority. **UNSURE** whether
this is the same list the audit meant.

---

## 2. What is established

Every row re-derived for this file from the artefact named. Levels are `plateau5` = mean TEST over `Epoch` lines 95–99 of
each run's own raw `.out`; the CSV `plateau` column is never read. SE is the frozen prior sigma's
`SE_ARM_DIFF` = 0.556196 (= σ 0.681198 × √(2/3)) unless the row says otherwise. **One row-set says otherwise, and it must
be stated rather than assumed: `cdep1` (E4, E5) does NOT use the frozen prior sigma.** Its bars are frozen in its own
scorer at **`SE_ARM_DIFF` = 0.755682 pp**, derived from *"a corpus reader that excludes `cdep1-*` rows"*, and every SE
figure printed in E4 and E5 is on that larger, more conservative bar (e.g. `DELTA_ID` 46.5233 / 0.755682 = 61.56 SE).
Mixing the two is how a 61.56 turns into an 83.65 that no artefact prints.

### 2.0 The headline the mechanism line sits beside (not this cycle's work, cited so it is not unsourced)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E0 | **The denominator result.** On **unaugmented CIFAR-100** (`ResNet18_c100`, `AUGMENT=0` on all 30 runs) a tuned plain SGD+momentum+cosine `lr` ladder peaks **interior** at `lr = 0.4` with **65.0573** and beats the best of five MetaOptimize cells (`m1e3a1e3`, **52.8793**) by `GAP_END` **+12.1780 pp = +26.05 SE**; branch `DEFICIT-HOLDS`. It is the **largest** deficit the campaign has measured (+12.178 unaugmented CIFAR-100, +5.699 augmented on the same network, +3.617 unaugmented CIFAR-10), which is what licenses "measured most strongly on CIFAR-100". | as stated | **No scorer output for this batch is committed under `results/` at this HEAD.** The registered record is CORRECTIONS 220 itself (scorer `analysis/cUC1_unaug_c100_score.py`, sha `9c2f752d…`, run unedited, exit 0, RULE 20 30/30) and MASTER-TABLE row 19. **This row is therefore flagged: it is the campaign's existing registered result, cited by its CORRECTIONS number, not re-derived by me from an artefact under `results/`.** | 220; verdict moved at 229 |

Bounds that travel with E0 and are written into MASTER-TABLE row 19 at 229: **one baseline family** (SGD+momentum+cosine);
the paper's own **α₀ 1e-6 is untested on CIFAR-100**; **one granularity per batch**, so meta-side tuning is bounded, not
exhausted. E0 is **not** a result of this cycle and nothing in §§2.1–2.6 rests on it.

### 2.1 The phenomenon and its carriers (ResNet18_c100, mechanism cell)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E1 | The scalar collapse, in batch | `k01` **22.7887** vs `kL` **69.0507**; `G_A` **+46.2620 pp = +83.18 SE** | `results/cmo1_momwd_score_alice2.txt` | 264 |
| E2 | Census view of the same cell (not a scorer; corpus means after `filter_rows`) | scalar **22.96** (n 44) vs layerwise **69.42** (n 32), ratio 0.331 | `LIMITS-PREP` §2.2 from `results/all_runs.csv` | 254 |
| E3 | Three carriers carry the shared vote | on the scalar arm, `layer4.1.bn2.weight`, `layer4.0.bn2.weight`, `layer4.0.shortcut.1.weight` are in the carrying set on **1239 / 1239** DISAGREE records (share 1.000 each); median |L| ×212 / ×188 / ×124 the median tensor; bn-scale class share of Σ|L| 0.598 | `results/ctd1_tensor_dominate/ATTACK_REPORT.txt` | 184 |
| E4 | Isolating them rescues; a **count-matched** non-carrier triple **stays on the floor** — a BOUND, not a magnitude | ISO **70.0440**, DEPTH **23.5207**, `DELTA_ID` **+46.5233 pp = +61.56 SE**; `D_ISO` +46.6920; isolated numel matched 1,536 = 1,536, all six tensors in `layer4`. **`D_DEPTH` prints +0.1687 pp but may NOT be read as an effect**: DEPTH's level is inside the registered saturation band [21.0940, 27.9520], FINAL `DEPTH-FLOOR-SATURATED`, and the scorer entitles us to **`D_DEPTH ≤ 5.0 pp`** only (164.6). **Composition, disclosed**: DEPTH = {47 `layer4.0.bn1.weight`, **48 `layer4.0.bn1.bias` — a BatchNorm SHIFT, not a scale**, 56 `layer4.1.bn1.weight`}. The **class-pure** arm answering that is in the same artefact: `DEPTH2` = {47, 56}, `D_DEPTH2` **+0.0960 pp** (also a bound, `DEPTH2-FLOOR-SATURATED`), `DELTA_ID2` +46.5960 pp, `DELTA_BIAS` = DEPTH − DEPTH2 **+0.0727 pp = +0.10 SE**, FINAL `BIAS-NULL`. **SE on this row and E5 is `cdep1`'s own 0.755682, not 0.556196.** | `results/SCORE-cdep1.txt` | 193 (ISO first at 187) |
| E5 | One carrier free also largely rescues | `ONE` ({50} alone, free) **64.8267**, `D_ONE` +41.4747 pp = **+54.88 SE** (on 0.755682) | `results/SCORE-cdep1.txt` | 193 |

### 2.2 Sufficiency of a held carrier step (ResNet18_c100, `ciso1`'s cell, PlainNet's dose `tri:9428`)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E6 | Each carrier alone, held, is **sufficient** to stall | `P_ONE50` **+43.6627** (+78.50 SE), `P_ONE59` **+46.6080** (+83.80 SE), `P_ONE53` **+35.2140** (+63.31 SE); the four stalled arms sit **below** `k01` 22.7540 (−1.6200 / −1.6567 / −0.4647 / −4.0307), so each `-AT-K01` word is a **LOCATION**, a bound, never a point estimate | `results/cvt10_onevsthree_score_alice2.txt` | 270 |
| E7 | …and the condition "only while the others vote" is **INDICATED, not established** | `ISOSPLIT` ({50} held at `tri:9428`, {53,59} free in their own group, sizes `[59,1,2]`) **67.0893** against ISO **70.1660**, `P_SPLIT` **+3.0767 pp = +5.53 SE**; the arm does **not** stall, while `ONE50BIG` (the same hold with 53 and 59 left in the shared group) sits −1.6200 pp **below** `k01`. **But `cvt10` has no free `[59,1,2]` arm** (`NO-FREE-SPLIT-CONTROL`), so `ISOSPLIT`'s non-stall cannot be separated from the `[59,1,2]` partition rescuing on its own the way ISO does; and this is the **narrowest margin of the cycle**, 1.9233 pp = **3.46 SE** inside its 5 pp bar, branch `SPLIT-NO-EFFECT` / `ISOSPLIT-AT-ISO`. **One arm, no control, narrowest margin — write INDICATED, never "provided".** The measurement that would settle it is O-9. | same | 270 |

### 2.3 The weight-decay precondition, at three grains

| # | grain | intervention | scalar arm without the decay | its own anchor | effect | artefact | CORR |
|---|---|---|---|---|---|---|---|
| E8 | every tensor **+ the meta trace**, ResNet | `--weight-decay-base 0` | `W0k01` **71.5600** | `k01` 22.7887 | `L_W0` **+48.7713 pp = +87.69 SE**; `W0k01` is **+3.3900 pp above** its own layerwise arm, so ISO is **unreadable** (`W0-ISO-AT-REF`) | `results/cmo1_momwd_score_alice2.txt` | 264 |
| E9 | the **20 network-wide** BatchNorm scales, ResNet | `DECAY_MASK=normscale` (update **and** meta trace) | `k01NWD` **70.7760** | `k01` 22.9513 | `P_NWD` **+47.8247 pp = +85.99 SE**; `G_NWD` = `kLNWD` − `k01NWD` = **−1.4340 pp** (scalar **above** its masked layerwise reference); `RATIO` **1.0207**, so the cell does not meet the R50 collapse criterion at all | `results/cwd1_normwd_score_alice2.txt` | 271 |
| E10 | **one** BatchNorm scale (idx 50), PlainNet | `DECAY_MASK=layer4.1.bn2.weight` | `k01WD0` **65.7500** | `k01` 12.0673 | `P_SC` **+53.6827 pp = +96.52 SE** | `results/cwd2_carrierwd_score_alice2.txt` | 273 |
| E11 | the **held-step damage** runs through the same factor, PlainNet | same mask, three **open-loop** held arms | `HIGHWD0` **65.6260** vs `HIGHHEADPATH` **10.7127** | damage `R_HIGH` = **+54.2880** | `P_WD` **+54.9133 pp = +98.73 SE**, `F_WD` **1.012**; `P_LEFT` = `LOWWD0` − `HIGHWD0` = **−0.6253 pp = −1.12 SE**, inside `NULL` 2.0 | same | 273 |

**The right reading of `F_WD` > 1**: the excess **is** `P_LEFT`, −0.6253 pp, inside the null bar. The honest sentence is
*"removing the decay on idx 50 removes the held-step damage to within the noise floor, and `HIGHWD0` is statistically
indistinguishable from the in-batch control"* — **not** "removes 101.2 %" (273.4).

**Orientation only, cross-batch, UNSURE** (271.6 F4): `P_NWD` +47.8247 against `L_W0` +48.7713 = **98.06 %**. Different
interventions, different batches, no shared bar, no shared seed.

### 2.4 Necessity of the carrier's own applied step (PlainNet18_c100, `cvt1`'s cell)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E12 | The gap to explain | `HEAD` **64.4293** vs `k01` **12.1180**, `D_HEAD` **+52.3113 pp = +94.05 SE** | `results/csv1_shadowvote_score_alice2.txt` | 272 |
| E13 | An applied step **above the clamp floor** is necessary for the full stall | `SHADOWLOW` **49.8790**, `P_APPLIED` **+37.7610 pp = +72.58 SE** | same | 272 |
| E14 | The vote route alone costs a partial loss | `NAIVELOW` **65.2420**, `P_VOTE` **+15.3630 pp = +31.89 SE** (≈ 29 % of `D_HEAD`); `NAIVELOW` is `AT-HEAD` | same | 272 |
| E15 | Muting 50's vote with its applied step free changes nothing | `MUTE` **11.3027**, `P_MUTE` **−0.8153 pp = −1.47 SE**, inside `NULL` — a **LOCATION** | same | 272 |

**Licence wording, corrected at source.** The registered `BOTH-ROUTES` licence says "a **LARGE** applied step". Only ONE
small dose was run — the clamp floor `float32(exp(float32(−15)))` = 3.059e-07, from init. The correct sentence is **"above
the clamp floor"**. This is a RULE 16 defect **reported and not fixed** (272.6 F1); the scorer was not edited.

### 2.5 The second meta step size (ResNet18_c100, ms 3e-4, frozen successor `cST2`)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E16 | The isolation rescue **transfers** | `k01` 28.5173, ISO 69.6740, CTL 28.6980; `D_ISO` **+41.1567 pp = +74.00 SE**, `D_CTL` **+0.1807 pp**, `P` = ISO − CTL **+40.9760**. **Same disclosure as E4**: `cst2`'s `CTL` **is** `cdep1`'s DEPTH triple, so it too contains the BatchNorm shift idx 48 — `cst2`'s own FINAL stamps `CTL-HAS-A-BIAS-MEMBER`, and `CTL` 28.6980 is a **floor location** against `k01` 28.5173, not a magnitude. There is **no class-pure control at this cell** (no `DEPTH2` arm at ms 3e-4). | `results/cst2_carriervote_score_alice2.txt` | 268 |
| E17 | The vote-dominance **nomination does not** | `DOM_C` **0.4727 = 709 of 1,500** records against a 750-record bar — **misses by 41**; `TOP3_C` **0.4960 = 744 of 1,500** — misses by **six**. Calibration at ms 1e-3: pooled `DOM_C` **0.8069** | same | 268 |

So at ms 3e-4 the campaign may write *the rescue transfers, the nomination is only partial there, and the two are not
locked together at this cell*. It may **not** write *the same three carriers are nominated at a second meta step size*.

### 2.6 What was exonerated

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E18 | **Momentum 0.99 is not required.** At SGDm momentum 0.9 the collapse persists and the isolation still rescues | `M9k01` **24.5833** vs `M9kL` **69.3913**, `G_M9` **+44.8080 pp**, ratio 0.3543 (anchor 0.3300); `M9ISO` **70.9047**, +1.5133 pp **above** `M9kL` | `results/cmo1_momwd_score_alice2.txt` | 264 |

Bound on E18: **no CTL arm exists at either new configuration** (`NO-CTL-AT-NEW-CONFIGS`), so `ISO-RESCUES` at momentum 0.9
is a **rescue** word and not a **specificity** word.

---

## 3. The mechanism as far as the evidence goes — and what is NOT shown

### 3.1 What the evidence supports

A **conjunction of one-cell results**, and nothing stronger:

1. At the ResNet mechanism cell the shared Lion vote is **dominated** by three last-block BatchNorm scales (E3), and the
   rescue is **specific** to them against a count-matched, same-layer, same-numel control (E4). The specificity is an
   **asymmetry between a measured rescue and a bounded floor** — ISO `+46.6920 pp` against `D_DEPTH ≤ 5.0 pp` — not a
   measured difference between two magnitudes, and the control triple contains one BatchNorm **shift** (idx 48), with
   the class-pure pair `DEPTH2` giving the same bound (E4).
2. A step at PlainNet's measured dose **on** those tensors is **sufficient** to stall — one at a time on ResNet, each
   held alone in its own group while the other 61 share one step size (E6). Whether that also requires the other two to
   remain in the shared vote is **INDICATED only** (E7): one arm, no free-split control, the cycle's narrowest margin.
3. On PlainNet, both the applied step and the vote carry part of the damage (E13, E14).
4. **Coupled weight decay on normalisation scales is a precondition** of the whole phenomenon, at three grains and on two
   networks (E8–E10), and the held-step damage runs through the same factor on PlainNet (E11).

### 3.2 What is NOT shown — stated in the same breath

* **The route is not identified.** `cmo1`'s flag, `cwd1`'s mask and `cwd2`'s `k01WD0` each change the **weight update and
  the meta trace `h ← γ(1 − wd·a)h − δ` together** (`MASK-UPDATE-AND-TRACE`, `K01WD0-BOTH-ROUTES-CHANGED`). Only `cwd2`'s
  three **held** arms are clean on this, because there every applied step is exogenous — and that is PlainNet, one tensor.
* **The natural story is unsupported where it can be looked at, and unmeasured where it matters.** The story — decay
  shrinks a BN scale, the shrinking scale's gradient grows, it dominates the shared vote, the shared step size runs away —
  is **UNSURE**. In every arm where `PATCH_DECAYMASK` records ‖w‖ the decay is **off** and the scales **grow**
  (`cwd1` `kLNWD` carriers 22.6 → 38.3 / 30.0 / 48.9; `cwd1` `k01NWD` 22.6 → 22.9 / 22.7 / 22.9; `cwd2` `k01WD0` idx 50
  22.63 → 23.31), **no masked run shows anything like a filter collapse**, and `dm_small` — the count of entries with
  |w| < 1e-3 — is **0 on every record that carries it, 7,500 of 7,500** across the two batches (274.1, 274.3).
  **Correction made here (CORRECTIONS 277), because the 276 draft over-stated the min-|w| bound:** the interval
  **[0.9994, 1.020] is `cwd2`'s, and `cwd2`'s only** — it is min |w| over a **single** masked tensor (idx 50, 512
  parameters; `cwd2` masked minimum 0.99941, maximum 1.02). On **`cwd1`**, where `dm_absmin` is the minimum over **all
  20** masked scales, it leaves that interval on both masked arms: `k01NWD` **0.983** and `kLNWD` **0.503** at record 499
  (`results/cwd1_normwd_score_alice2.txt`, DESCRIPTIVE block). The conclusion is unchanged — 0.503 is three orders above
  the 1e-3 small-weight threshold and `dm_small` is 0 there too — but the sentence *"min |w| never leaves [0.9994, 1.020]
  on any masked run"*, which 274.3 writes and the 276 draft copied, is **wrong as a cross-batch claim** and is replaced
  by the per-batch figures above. 273's own bound (2) is correctly scoped ("min |w₅₀| ≥ 0.9994"); 274.3 generalised it.
* **The collapsing arms carry no measurement at all.** `dm_*` is present only on masked arms: `cwd1` 3,000 of 4,500
  records, `cwd2` 4,500 of 7,500. The 4,500 `cwd2` records with no readout are exactly the three seeds of the two
  **stalling** arms, `k01` and `HIGHHEADPATH`; `cwd1`'s 1,500 are `k01`'s (274.1 per-arm table). **The arms where the
  collapse happens are precisely the arms with zero instrumentation.**
* Consequently **Zhou et al.'s filter-collapse candidate (arXiv:2001.11216) is neither confirmed nor excluded**, and
  Lobacheva et al.'s BN×WD destabilisation (arXiv:2106.15739) is consistent with the direction but **untested here**.
* **On ResNet, the carriers alone were never unmasked.** The decomposition stops at 20 tensors. See §6 O-1.
* **Decoupled weight decay is untested** at every cell; every result above is about **coupled** L2.
* **`cwd1` has no ISO arm**, so what the carrier isolation does *under* the mask is unknown; and `cwd1`'s reference arm is
  itself masked (`NO-WD-ON-REFERENCE-ARM`), so "the scalar arm reaches the layerwise level" is a statement about a
  **masked** layerwise arm.

**One sentence for the section, and it is the honest one: naming the precondition is a SCOPE result; it is not yet a
mechanism.**

---

## 4. Relation to prior work

Only papers whose arXiv id I re-checked for this file are used. Each id below was resolved on its arXiv **abstract page**
(HTML) on 2026-09-19 and the title and author list match what is cited. **No PDF was fetched, nothing was downloaded, no
licence was accepted.** Nothing is added that is not already verified in `docs/PRIOR-ART.md` (2026-09-17 section) or in
CORRECTIONS 258.1 / 260.1 / 262.1.

| paper | id | verified | what it already establishes | what remains ours |
|---|---|---|---|---|
| He, Zhang, Zhang, Zhang, Xie, Li — *Bag of Tricks for Image Classification with Convolutional Neural Networks* | arXiv:1812.01187 | title + 6 authors on the abstract page | "no bias decay": weight decay on conv/FC weights only, BN γ/β left unregularised — **standard practice** | That this practice is **load-bearing for a meta-learned step size**: with the decay on the scales the shared step size collapses, with it off the collapse is gone (E8–E10). He et al. motivate the practice by overfitting, not by optimiser failure. |
| Arora, Li, Lyu — *Theoretical Analysis of Auto Rate-Tuning by Batch Normalization* | arXiv:1812.03981 | title + 3 authors | scale-invariant weights converge at any LR; only **scale-variant** parameters (γ, β, last layer) need a tuned LR | **Which** scale-variant tensors, and **how few**: three of the 62 (0.014 % of parameters), identified by per-tensor attribution of a shared meta-update's vote, with a count-matched same-class control that does **not** rescue (E4). Arora–Li–Lyu predict the class; they do not predict a three-tensor set, a last-block position, or a rescue/control asymmetry. **This is also the expected referee line** ("of course the γ's"), and E4 is its answer. |
| Davis, Frank — *Revisiting Batch Norm Initialization* | arXiv:2110.13989 | title + 2 authors | γ init ≈ 0.1 and **γ learning rate ÷ 100** give significant gains — so "give γ its own smaller LR" is **already known as a practice** | Nothing in the ISO result may be sold as "γ wants its own LR". What is ours is the **vote-dominance evidence**, the **matched-control specificity**, and the **step/vote dissociation** (E13–E15) — the mechanism evidence, not the remedy. |
| Zhou, Wang, Luo, Feng, Li, Zhang — *How Does BN Increase Collapsed Neural Network Filters?* | arXiv:2001.11216 | title + 6 authors | BN+ReLU filter collapse; sparsifying probability ∝ lr² and ∝ 1/γ²; worse at large or adaptive LR, **without any sparsity-inducing regulariser** | The **candidate mechanism we could not test**. Where our readout exists there is no collapse at all (`dm_small` 0 on 7,500 of 7,500; min \|w\| ≥ **0.99941** over `cwd2`'s single masked tensor and ≥ **0.503** over `cwd1`'s 20 masked scales — see the correction in §3.2, the 276 draft quoted the tighter `cwd2` figure as if it covered both), but the readout exists only where the decay is off. **Neither confirmed nor excluded** — and this is the single strongest reason the section must not be sold as a mechanism. |
| Lobacheva, Kodryan, Chirkova, Malinin, Vetrov — *On the Periodic Behavior of Neural Network Training with BN and Weight Decay* | arXiv:2106.15739 | title + 5 authors | BN **together with** WD produces repeated destabilisations and a periodic training regime | The nearest published prior that the pathology **needs** WD — and the strongest reason our `COLLAPSE-VANISHES` is not surprising. Theirs is about **scale-invariant** weights in a BN net; ours is WD applied to **γ itself**, which is scale-**variant**, and theirs says nothing about a meta-learned step size. It is also the live alternative explanation for our rescue decaying over 250–430 epochs, and **we have not tested it**. |
| Kim, Choi, Jang, Lee, Jeong, Kim — *Guidelines for the Regularization of Gammas in BN for Deep Residual Networks* | arXiv:2205.07260 (ACM TIST 15(3) 2024, DOI 10.1145/3643860) | title + 6 authors | γ's admissibility for **L2** depends on its **position** in the residual block (last-in-branch vs projection shortcut) | The only paper that treats our carrier categories as different categories — **for L2, not for step size, and never one tensor at a time.** `cvt10` makes the position contrast a within-batch one: `ONE53` (the projection shortcut) stalls at +35.2140 pp against +43.6627 / +46.6080 for the two last-in-branch scales (E6, `L_LAST_DOWN` +9.9213 pp, descriptive). Kim et al. do not predict that ordering under a step-size intervention. |
| Mueller, Vlaar, Rolnick, Hein — *Normalization Layers Are All That Sharpness-Aware Minimization Needs* | arXiv:2306.04226 | title + 4 authors on the abstract page, resolved 2026-09-19 (v1 7 Jun 2023, v2 17 Nov 2023) | Perturbing **only the affine normalisation parameters** — *"typically comprising 0.1% of the total parameters"* — in SAM's adversarial step can **outperform** perturbing all of them; it generalises across SAM variants and across **ResNet (BatchNorm) and ViT (LayerNorm)**; alternative sparse-perturbation schemes do **not** match it at that sparsity, so the behaviour is specific to the normalisation layers | **Added at CORRECTIONS 277 on the referee's prompt, and it is the closest prior art to our *fraction* sentence — it must be cited before a referee finds it.** Theirs is the strongest published statement that a tiny normalisation-parameter subset carries a training effect, so "0.014 % of parameters" is **not** ours to sell as surprising. What is still ours: the intervention is a **per-tensor step-size group in a meta-learned optimiser**, not an adversarial perturbation in SAM; the subset is **nominated by per-tensor attribution of a shared meta-update's vote**, not chosen a priori as a class; it is **three named tensors, not the class**; and there is a **count-matched non-carrier control from the same class and layer** whose result is a bounded floor (E4). Their result also **weakens** any "the normalisation parameters are special" novelty claim and **strengthens** T1: it is further evidence the phenomenon lives in a normalisation-parameter configuration. Their ViT/LayerNorm coverage is also the sharpest form of our architecture limit (T13) — they show the class effect crosses architectures; **we have not**. |
| De, Smith — *Batch Normalization Biases Residual Blocks Towards the Identity Function in Deep Networks* | arXiv:2002.10444 | title + 2 authors | BN downscales the residual branch relative to the skip by ≈√depth; BN nets train at larger learning rates | Makes a last-in-branch γ a **plausible single lever** a priori, which is why our result is not a surprise in direction. Nothing there varies **one tensor's** learning rate, and the shortcut BN is not contrasted with the branch BN. Our ordering result (previous row) is not available from it. |

**Not claimed as new.** That γ benefits from its own smaller LR (Davis & Frank); that scale-variant tensors are where LR
sensitivity lives (Arora–Li–Lyu); that large LR on BN parameters can damage a net (Zhou et al.); that BN+WD destabilises
(Lobacheva et al.); that excluding BN from weight decay is standard (He et al.); **and that a ≈0.1 %-of-parameters
normalisation subset can carry a whole training effect, on BN and LN nets alike (Mueller et al.) — so the *fraction* in
"three of 62 tensors, 0.014 % of parameters" is not itself the contribution.**

**What the campaign claims, in three clauses, all bounded to the cells in §2.** (a) A meta-learned **shared** step size
whose meta-update vote is shown, by per-tensor attribution, to be dominated by a few identified last-block
normalisation-scale tensors. (b) A carrier-specific rescue beaten by a **count-matched** non-carrier control. (c) Hold and
mask interventions dissociating **dose**, **vote route** and **weight-decay route**. The prior-art sweeps recorded at 254,
258.1, 260.1 and 262.1 found **zero** arXiv hits pairing hypergradient / meta-learned step size with normalisation or with
per-layer dominance, against a control query (`hypergradient`) returning 127 — the zero counts are real, not a broken
search (262.1).

---

## 5. Threats and limits

In the campaign's register: what a reviewer will say, and what the honest answer is.

| # | threat | answer, or concession |
|---|---|---|
| T1 | "This is a configuration pathology, not a finding." | **Largely conceded, and it must be written that way.** `LIMITS-PREP` §6 named this as the single biggest weakness and its own conditional has fired on the weight-decay branch. Momentum 0.99 is exonerated (E18); coupled WD on the norm scales is not — it is a **precondition** (E8–E11). The section is therefore a configuration-conditional failure mode, and the practical ceiling is set by the configuration. The correct statement of that ceiling is **"we did not meet the collapse at any cell tested with the decay off"**, never "a reader will not meet it". |
| T2 | "You never removed the decay from the carriers alone on ResNet." | **Conceded, unreservedly.** `cwd1`'s mask is network-wide (20 scales). This is the gap. It is the one open item that can be closed cheaply, and Track A is registering exactly that batch (§6 O-1). |
| T3 | "The mechanism is not measured." | **Conceded.** §3.2. The instrument records ‖w‖ only where the decay is off; the collapsing arms carry nothing. A mechanism needs a **new instrument**, not more cells. |
| T4 | "Your necessity results are on a modified algorithm." | **Partly conceded.** `csv1`'s shadow vote is counterfactual (`SHADOW-IS-COUNTERFACTUAL`) and the registration says so in every licence token. `cwd2`'s held arms are open-loop with the complement forced onto a replay (`COMPLEMENT-ON-HEADPATH`). The necessity statements that do **not** modify the meta-update are the weight-decay ones: `cmo1` W0 is a plain CLI flag on the unpatched harness (`LIVE-HARNESS`); `cwd1` / `cwd2` `k01WD0` use `PATCH_DECAYMASK`, which changes **which tensors are decayed** — a training-configuration change — and leaves the meta-update closed-loop. |
| T5 | "One dataset family, one network per axis, one horizon." | **Conceded.** CIFAR-100 (plus one CIFAR-10 association cell, `cct1`, where nothing collapses and dominance is present but never decisive); `ResNet18` or `PlainNet18` per axis; 100 epochs everywhere in this cycle, while the rescue is known to decay by 250–430 epochs elsewhere in the corpus. |
| T6 | "Three seeds." | **Conceded as a design fact, mitigated by margin.** Every deciding contrast in §2 clears its bar by 30–100 SE. In `cmo1`, `cwd1`, `cwd2`, `csv1`, `cvt10` and `cst2` the bar is the **frozen prior sigma** 0.681198 (`SIGMA-PRIOR-FROZEN` on each FINAL; the conservative choice over that batch's own in-batch sigma, which runs 0.390–0.481), giving `SE_ARM_DIFF` 0.556196. **`cdep1` is the exception and the 276 draft got it wrong: it does NOT use 0.681198.** Its bars are frozen in its own scorer at `SE_ARM_DIFF` **0.755682 pp**, from *"a corpus reader that excludes `cdep1-*` rows"* — a **larger** bar than the frozen prior's, so E4/E5 are if anything under-stated in SE, not over-stated. The exceptions to the 30–100 SE range are named: `P_SPLIT` (1.9233 pp = 3.46 SE inside its bar, E7) and `cmg1`'s `D_CAR` (+4.115 pp, 0.885 pp inside a 5 pp margin — reported elsewhere, not used in §1). |
| T7 | "Some arms sit **below** the scalar anchor, so 'stalls to the scalar level' is wrong." | **Conceded and already stamped.** `FLOOR-READINGS-ARE-BOUNDS` (164.6) is on the `cmo1`, `cvt10`, `csv1`, `cwd2` and `cst2` FINALs — five, not the three the 276 draft listed, verified by grep over the committed outputs; `HOLDBIG3-BELOW-K01` is explicit. **`cdep1` belongs on this list too and the 276 draft omitted it** (R1): its FINAL carries `DEPTH-FLOOR-SATURATED` and `DEPTH2-FLOOR-SATURATED`, and its scorer cites 164.6 in the same words — DEPTH 23.5207 and DEPTH2 23.4480 are **inside** the registered saturation band [21.0940, 27.9520], so the entitled statements are `D_DEPTH ≤ 5.0 pp` and `D_DEPTH2 ≤ 5.0 pp` and nothing finer. Every such reading is a **location**, a bound, never a point estimate — and that applies to the E4 control exactly as it applies to `cvt10`'s stalled arms. |
| T8 | "Hardware was not controlled." | **Disclosed, not defended.** `cmo1`, `cwd1` and `cwd2` ran across mixed accelerators (2080 Ti / L4 / A100-MIG), unregistered and ungated. For `cwd2` the arm-centred device estimate is +0.046 / −0.038 / −0.073 pp — inside the noise floor and two to three orders below the 54.9 pp the verdict turns on; the branch string survives every leave-one-seed-out and ±2 pp per device class. **Seed is confounded with device and cannot be separated.** `cvt10` and `csv1` have **no** such census yet (§6 O-3). |
| T9 | "Your noise floor moved under you." | **Disclosed.** The `--check` demonstration floor moved with the ingest (`SIGMA_R18ALL` 0.663166 df 239 → **0.648113 df 255**; `SIGMA_PLAIN` 0.459529 → 0.460632). **No bar reads that line** — every bar in §2 is a frozen literal set at registration — but any future scorer re-deriving a floor from the corpus must quote the new value. |
| T10 | "Six RULE 16 defects are open." | **Reported, none fixed, none hidden**: 270.6 F1, 271.6 F1 + F2, 272.6 F1 + F2, 273.6 F1 + F2. Exactly one of them touches a **licence sentence** — `cSV1`'s word "large" — and §2.4 states the corrected sentence in its place. |
| T11 | "The parent reports scalar (SGDm, Lion) working on ImageNet." | **Open, and it is the sharpest external counterweight.** Our IN-489 scalar sits at 1.00. The obvious untested confounder was momentum 0.99 — now exonerated (E18) — which makes coupled WD the live candidate, but we have run nothing on ImageNet and cannot. Parent §7.3 also reports blockwise no better than scalar there. |
| **T12** | **"Your only control is a bounded floor, and it has a BatchNorm shift in it."** | **Conceded, and now disclosed in §1, E4, E16 and T7 rather than left for a referee to find** (R1, R2). Two separate concessions: (a) the count-matched control's result is a **bound** (`D_DEPTH ≤ 5.0 pp`), not a magnitude — "recovers none of it" is struck; (b) the triple {47, 48, 56} contains **`layer4.0.bn1.bias`, a BatchNorm shift**, so it is count-matched and layer-matched but **not class-pure**. The answer is in the same artefact and costs nothing: `DEPTH2` {47, 56} is class-pure, `D_DEPTH2` +0.0960 pp, `DELTA_BIAS` +0.0727 pp = +0.10 SE (`BIAS-NULL`). The conclusion does not rest on the shift member — **but it also does not become a magnitude by being class-pure**; DEPTH2 is floor-saturated too. `cst2`'s `CTL` is the same triple (`CTL-HAS-A-BIAS-MEMBER`) and has **no** class-pure partner at its cell. |
| **T13** | **"Two architectures, both 18 layers, and one of them is your own variant."** | **Conceded, unreservedly, and it is a wider limit than T5's "one network per axis" made it sound.** Every result in §2 is on `ResNet18_c100` or `PlainNet18_c100` — **the same depth, the same width, the same block count**, differing only in whether the residual connection is there. Nothing was run on ResNet34/50 (which the campaign *does* own elsewhere), on any non-residual family outside our own PlainNet, on any normalisation other than BatchNorm (**no GroupNorm, no LayerNorm**), and on nothing outside convolutional image classifiers. `cwd1`'s own scorer says this in its NOT-LICENSED block: *"Anything about PlainNet / VGG / GroupNorm, other cells…"*. Mueller et al. (arXiv:2306.04226) is the sharp form of the gap: they show the normalisation-parameter effect crossing **BN ResNets and LN Vision Transformers**; we have **not** crossed anything. |
| **T14** | **"Lion is the only meta-update rule you ever ran."** | **Conceded, and it was missing from the 276 draft's limits entirely.** Every arm in §§2.1–2.6 is SGDm(0.99, wd 0.1) **base** + **Lion meta** at meta step 1e-3 (E16/E17's second cell is the same pair at 3e-4). The carrier account is stated in terms of *the shared **Lion** meta-update's vote* — and Lion's update is a **sign** function, so "three tensors dominate the vote" is a statement about a **sign-aggregated** sum in which one large-\|L\| tensor can fix the sign of the whole. **Under Adam-meta or SGD-meta the aggregation is not a sign vote and the dominance statistic `DOM_C` is not even defined the same way.** The campaign has Adam-meta runs elsewhere (they are what removes the weightwise collapse, MASTER-TABLE §2), so this is a real and untested axis, not a hypothetical one. **No sentence in §1 may be written about "a meta-learned step size" in general; it is about a Lion meta-update.** |
| **T15** | **"The whole carrier set comes from one instrument, and that instrument is already unstable."** | **Conceded, and it is the weakest joint in the chain.** The three carriers are nominated **only** by `ctd1`'s per-tensor \|L\| attribution on the scalar arm (E3) — one attribution statistic, on one arm, at one cell. There is **no second, independent nomination instrument anywhere in the campaign**: no ablation-based ranking, no gradient-norm ranking, no leave-one-out search. And the instrument is **already known to be fragile off its cell**: at ms 3e-4 the same statistic gives `DOM_C` **0.4727** against a 0.50 bar (misses by 41 records of 1,500) and `TOP3_C` **0.4960** (misses by **six**), against a pooled **0.8069** at ms 1e-3 — E17, branch `NOMINATION-PARTIAL`. So the rescue transfers a decade of meta step size and the nomination does not. **A referee is entitled to say the carrier set is an artefact of one statistic at one meta step size, and the campaign cannot currently refute that.** |
| **T16** | **"How many contrasts did you look at before these?"** | **Conceded: there is no multiplicity control anywhere in this cycle, and none was ever registered.** Across `cmo1`, `cvt10`, `cwd1`, `csv1`, `cwd2`, `cdep1` and `cst2` this write-up reads **19 numbered evidence rows** (E0–E18), and the underlying scorers print several times that many contrasts (`cvt10` alone prints **18** under `CONTRASTS`, plus a DESCRIPTIVE nineteenth). Every bar is a **frozen literal fixed at registration** and every contrast is **within batch and pre-registered as PRIMARY / CO-PRIMARY / KEY / DESCRIPTIVE before the runs existed** — which is what protects the deciding numbers, and it is a better protection than a post-hoc correction would be. **But no family-wise or false-discovery correction is applied to anything**, so the honest statement is: the 30–100 SE contrasts are unaffected by any plausible correction, and the **two narrow ones — `P_SPLIT` at 3.46 SE inside its bar (E7) and `cmg1`'s `D_CAR` at 1.84 SE inside (T6) — are exactly the ones a multiplicity argument would attack, and neither is load-bearing in §1 any more after R4.** Descriptive readings (`L_LAST_DOWN`, the `dm_*` block, the class shares) carry **no** bar at all and are labelled DESCRIPTIVE. |
| **T17** | **"Your own draft had an evidence error in it."** | **Disclosed rather than quietly fixed.** The 276 draft asserted *"min \|w\| never leaves [0.9994, 1.020] on any masked run"*. That interval is **`cwd2`'s single masked tensor only**; on `cwd1`, where the readout minimises over all **20** masked scales, it reaches **0.983** (`k01NWD`) and **0.503** (`kLNWD`). Corrected in §3.2 at CORRECTIONS 277. **The conclusion is unchanged** — 0.503 is three orders above the 1e-3 threshold and `dm_small` is 0 on all 7,500 records that carry it, so Zhou et al. remains neither confirmed nor excluded — but the bound as stated was wrong, and it was inherited from 274.3, which generalised 273's correctly-scoped `min \\|w₅₀\| ≥ 0.9994`. **Anyone quoting 274.3's sentence should quote the per-batch figures instead.** |

---

## 6. Open questions, and what each costs

Ordered by value per GPU-hour. **Nothing here is registered and nothing is launched by this file.** Costs for O-6, O-7,
O-8 are 273.12's estimates; O-1, O-2, O-9 and O-11 are my own rough guesses at ≈0.8 GPU-h per 100-epoch run and are
**UNSURE**.

| id | question | cost | what an outcome would let the section say |
|---|---|---|---|
| **O-1** | **The ResNet carrier-only decay mask** — `DECAY_MASK` on {50, 53, 59} alone, against `cwd1`'s 20-scale mask and against `k01`. This is the batch Track A is registering in parallel as this draft is written (expected id `cwd3`; **nothing of it is in the repository at `84e4bcb`, so everything about it here is UNSURE and must be re-read from CORRECTIONS 275**). | ≈ 5–8 GPU-h (guess, UNSURE) | **If the three alone remove the collapse**: O1 is repaired and §1 may say "the collapse is carried by a few last-block scales **and** removing their decay removes it" on **ResNet as well as PlainNet** — the cleanest sentence the line can have. **If they do not** (and the other 17 scales are needed): the carrier account and the decay account **come apart**, the nomination set and the precondition set are different sets, and that is a more interesting and more honest result than the one 273.12 proposed. **If partial**: a bounded fraction, stated as a fraction, with `cwd1` as the ceiling. **Either way the gap closes.** |
| **O-2** | **A weight-norm readout on the arms where the decay is ON** — a read-only patch (`PATCH_WNORM`-style) so the collapsing arms carry ‖w‖, min |w| and a small-weight count. | new patch + inertness proof + ≈ 5 GPU-h | The only item that could turn the scope result into a **mechanism**, and the only way to rule Zhou et al. in or out. **This is a design question for the professor, not a queue item** (273.12). |
| **O-3** | **GPU-hardware census for `cvt10` and `csv1`**, read from each run's own device line, in the form 264.4(4) / 273.4 used. | **ZERO GPU** | Closes T8 for the two batches carrying the cycle's narrowest margin. **Owed** since 270.4(6) and 272.4(7). |
| **O-4** | **Pin `--constraint`, or record node/GPU in `PROVENANCE`, and add a `G-HW` disclosure** for any future batch. A launcher change, not a scorer edit. | ZERO | Retires the whole T8 class. Owed since 264.4(4). |
| **O-5** | **Close 264.6 W1's fix-track debt** — the false "each run prints `Epoch 99` twice" sentence baked into `analysis/cmo1_attack_indep.py` and its committed output. | ZERO | Removes the last factual error in a committed artefact from this cycle. |
| **O-6** | **S4 — a CTL arm at momentum 0.9.** | ≈ 5 GPU-h | Turns `cmo1`'s M9 `ISO-RESCUES` from a **rescue** word into a **specificity** word. Only worth it if the professor wants the momentum leg strengthened. |
| **O-7** | **N2 — `csv1`'s shadow-vote design on ResNet18_c100.** | ≈ 13 GPU-h | Carrier-step necessity on the second network. **A refinement, not a new claim.** |
| **O-8** | **A dose ladder on idx 50's applied step** (three values between the clamp floor and the shared step). | ≈ 10 GPU-h | Licenses the word "large" that 272.6 F1 had to strike; turns a two-point contrast into a curve. Lowest value of the GPU items. |
| **O-9** | **A PAIR of carriers** on ResNet, and a free `[59,1,2]` control for `ISOSPLIT`. Never run. | ≈ 8 GPU-h | Would make E7's condition ("only while the others vote") a measured statement instead of a single uncontrolled arm. |
| **O-10** | **Why ResNet and PlainNet differ at all** (three carriers vs one tensor), and the **closed-loop route at `k01`'s own dose** (`cvt8`'s `ROUTE-PARTIAL`, HIGHISOPATH 58.19). | unscoped | Both still open after `cvt10`. Not recommended before the discussion. |
| **O-11** | **Any further widening of L1 by dataset or network** (Tiny-ImageNet T1, S5, S6). | 20–40 GPU-h | **NOT recommended** (273.12): it buys scope for a claim whose ceiling is set by the configuration, not by the scope. |

---

## 7. Questions for the professor

1. **Framing (the live one).** Momentum 0.9 does **not** remove the collapse; weight decay 0 on the normalisation scales
   **does**, on both networks and down to a single tensor. Is the mechanism line still a **mechanism section** of the
   paper, stated as conditional on coupled weight decay — or does it become a **note on a configuration pitfall**? The
   data has answered the question; only the framing decision is left. *(This is `LIMITS-PREP` §7 Q2, now live.)*
2. **Consolidate or continue?** 273.12's recommendation is **CONSOLIDATE — write up now**, on the argument that the
   practical ceiling is set by the configuration and that a mechanism needs a new instrument rather than more cells. The
   one exception this draft would make is **O-1** (the ResNet carrier-only mask), because it repairs an over-statement
   rather than widening a claim. Does he agree with that exception — and does he want **O-2** (the readout on the
   unmasked arms) designed at all?
3. Is "sufficiency plus a **count-matched** control" (E4, E6) enough necessity for the claim he wants, or does the
   necessity leg need `csv1`'s counterfactual construction repeated on ResNet (**O-7**) despite a reviewer naming it an
   algorithm intervention?
4. How should the parent's §7.3 ImageNet result (scalar SGDm+Lion works; blockwise no better than scalar) be positioned
   against our IN-489 scalar at 1.00, now that momentum 0.99 is exonerated and coupled WD is the live candidate (T11)?
5. The isolation rescue transfers to ms 3e-4 but the vote-dominance nomination does not (E16, E17). Is that dissociation
   worth reporting in the section, or does it weaken the carrier story more than it is worth?
6. Does the Zhou et al. filter-collapse candidate need to be ruled in or out before the discussion, given that our
   instrument **cannot** do it (§3.2)?

**On "the two judgement calls the audit left open".** My brief refers to two judgement calls left open by a final audit
whose report I could not locate in the repository at `84e4bcb` (see the provenance note at §1.1). **UNSURE** that these are
the two it meant; on the record itself, the two calls that are genuinely open and genuinely require a human are **Q1
(framing)** and **Q2 (consolidate vs continue, and whether to build a new instrument)**. Everything else above is either
answered by the data or is a costed queue item.

---

## 8. Provenance and discipline

* Written against `master` `84e4bcb`; corpus `results/all_runs.csv` at `66a19fb`, **3,253 rows / 3364.4 GPU-hours**;
  `results/CORPUS-EXCLUSIONS.tsv` 171 rows.
* Every number in §2 was re-derived from the committed artefact named in its row. Census figures (E2) are labelled as
  census and come from `LIMITS-PREP` §2.2, which reads `results/all_runs.csv` through
  `analysis/corpus_exclusions.filter_rows` — the 108 intervention runs are never pooled.
* **Nothing under `paper/` was read into this file, opened for writing, or touched.** This file lives in `docs/`.
* **RULE 16 held**: no registered scorer, launcher, patch, `analysis/argsline_guard.py`, `analysis/corpus_exclusions.py`,
  `results/*.csv` or `results/*.tsv` was edited. No bar was re-derived and no verdict re-scored.
* **Eight** arXiv ids were re-checked on their **abstract pages (HTML)** on 2026-09-19 — 1812.01187, 1812.03981,
  2110.13989, 2001.11216, 2106.15739, 2205.07260, 2002.10444, and **2306.04226 (added at CORRECTIONS 277)** — plus the
  parent, 2402.02342. All nine resolve with the titles and author lists cited. **No PDF was fetched, nothing was
  downloaded, no dataset licence was accepted, no notebook site or Vercel URL was opened.** *(Disclosure: the local arXiv
  MCP index could not resolve 2306.04226 — nor 2106.15739, an id this file already cites and which certainly exists — so
  that index is **broken here and was not relied on**; 2306.04226 was verified on `arxiv.org/abs/2306.04226` itself,
  returning Mueller, Vlaar, Rolnick, Hein, "Normalization Layers Are All That Sharpness-Aware Minimization Needs", v1
  7 Jun 2023 / v2 17 Nov 2023, with the abstract quoted in §4.)*
* **ZERO GPU. No `sbatch`, no `srun`, no job submitted, cancelled or queried. `alice` — Saber's shared account — NOT
  contacted.**
