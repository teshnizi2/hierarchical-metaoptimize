# WRITEUP — the mechanism line as a bounded secondary contribution

*Draft for Reza, to read and to take to Dr Salehkaleybar. **NOT paper text and NOT for submission.** Nothing under
`paper/` was read into this file and nothing under `paper/` was touched. **REWRITTEN 2026-09-20 at CORRECTIONS 279**,
against `master` at **`97eb049`**, corpus **3,268 rows / 3375.0 GPU-hours** (`results/all_runs.csv` at `064dff6`),
`results/CORPUS-EXCLUSIONS.tsv` **183 rows**. Every number below was re-derived from a committed scorer or parser
output under `results/`, or from a batch's own committed `PARTITION-MANIFEST.txt`; where a number is a census figure
rather than a scorer figure, it says so. Prose in this file is mine; the branch words, licence sentences and bars are
the registered ones and are quoted, not paraphrased. **ZERO GPU. No Slurm job. `alice` — Saber's shared account — not
contacted.** RULE 16 held: no registered scorer, launcher, patch, `analysis/argsline_guard.py` or
`analysis/corpus_exclusions.py` was edited.*

***WHY THIS IS A REWRITE AND NOT A PATCH.*** *The 276 draft was rejected by a hostile referee at 277 and eight failures
were applied; the 278 amendment added `cwd3`. **A second hostile pass then rejected the result again**, and it found
**two FATAL omissions** — the whole adverse arm of `cvt1` (CORRECTIONS **230**) and the binding magnitude-scope
declarations of `cdep1` and `cmg1` — plus several major errors. It also did the novelty check the draft never did, and
that check is what this rewrite is built on: **the precondition half of the claim is true but near-trivial given
Lobacheva et al. (arXiv:2106.15739) and He et al. (arXiv:1812.01187); the LOCALISATION half is the real contribution
and survives every cited paper — but stated as TENSOR IDENTITY it exceeds the campaign's own record.** The claim is
therefore restated as a **BOUNDED LOCALISATION BY TERM MAGNITUDE**, and **the adverse evidence now sits in §1, before
the claim in §2, where a referee meets it first**. §2.4 lists every fatal and major finding with where it landed, and
what I declined and why.*

---

## 0. Bounds, led with

Before any claim, the **fourteen** things a reader must be told in the same breath as the result. Items 12–14 are new
at CORRECTIONS 279 and are the reason §1 exists.

1. **It is a SCOPE result, not a mechanism.** Naming a precondition is not identifying a route. §4 states exactly what
   is not shown and why the instrument cannot show it.
2. **The measured arms are the wrong arms.** `PATCH_DECAYMASK` writes `dm_norm` / `dm_absmin` / `dm_small` **only where
   the mask is on**, so the arms that actually collapse (`cwd1` `k01`; `cwd2` `k01`, `HIGHHEADPATH`; `cwd3` `k01`)
   carry **no** weight-norm record at all (CORRECTIONS 274.1 per-arm table; 278.5).
3. **~~On ResNet the decay was never removed from the three carriers alone.~~ RETIRED AT THIS CELL by `cwd3`
   (CORRECTIONS 278).** *What it said, kept verbatim because it was the draft's biggest declared gap: `cwd1`'s mask is
   the 20 BatchNorm scales of the whole network, `bn1` through `layer4` (271.4(1), 271.5 live-model check); the carriers
   are three of the twenty; the single-tensor sentence is earned on PlainNet only (`cwd2`, idx 50).* **What replaced it:**
   `cwd3` masks the three carriers **alone** on `ResNet18_c100` at `ciso1`'s cell — 1,536 of 11,220,132 parameters —
   and the collapse goes (`P_CAR` **+47.2787 pp = +89.34 SE**, `CARWD0` **inside** `NWD`'s `REC` band). **The gap is
   closed at ONE cell, on ONE network, at ONE horizon, with every arm SCALAR and no layerwise arm** — and it is closed
   with two new confounds attached, at items 10 and 11 below. **The `cwd2` single-tensor sentence is still PlainNet
   only**, and nothing here separates which ONE of the three carriers matters.
4. **`F_WD` = 1.012 is PlainNet-only**, one tensor, one dose, one cell, with the complement forced onto a replayed path
   (`COMPLEMENT-ON-HEADPATH`, `HELD-ARMS-OPEN-LOOP`).
5. **The 98.06 % figure is a CROSS-BATCH ratio and is orientation only** (271.6 F4, UNSURE): different interventions,
   different batches, no shared bar, no shared seed. It is not a decomposition and not a residual measurement.
6. **One configuration, one horizon, three seeds, axes one at a time.** CIFAR-100 (plus one CIFAR-10 association cell),
   `ResNet18_c100` / `PlainNet18_c100` per axis, 100 epochs, SGDm(0.99, wd 0.1) + Lion, meta step 1e-3, α₀ 1e-6.
   Coupled decay only — **decoupled weight decay is untested everywhere.**
7. **Two of the necessity statements are on modified algorithms** (`csv1`'s shadow vote is counterfactual; every hold is
   an exogenous step-size trajectory; `cvt1`'s INJECT re-weights a term inside the shared sum). A reviewer will name
   them as algorithm interventions, and §6 of `LIMITS-PREP` predicted exactly that.
8. **The count-matched control is a FLOOR BOUND, and it is not class-pure.** `cdep1`'s DEPTH arm is **inside** the
   registered saturation band, so the only entitled statement is `D_DEPTH ≤ 5.0 pp` — **never "recovers none of it"**
   and never a point effect (`DEPTH-FLOOR-SATURATED`, 164.6). And the triple contains **one BatchNorm shift**,
   `layer4.0.bn1.bias` (idx 48), not three scales; the class-pure pair `DEPTH2` {47, 56} gives the same bound
   (`D_DEPTH2` +0.0960 pp, `DELTA_BIAS` +0.0727 pp = +0.10 SE), so the result does not rest on the shift — **but it does
   not become a magnitude either.**
9. **`cwd3`'s two controls are FLOOR BOUNDS too, and the numbers that bound them are these** *(CORRECTIONS 278)*: at
   ±2 SE on the observed contrasts, **|P_CTL| ≤ 1.0744 pp** and **|P_CTL2| ≤ 1.1104 pp** — and
   **2 SE = 1.058364 pp is the HALF-WIDTH of the interval, not itself the bound**. Against `P_CAR` +47.2787 pp that is
   **42.6 : 1** at the 2-SE bound, or **23.6 : 1** against the registered 2.0 pp `NULL` bar. **That ratio is what
   carries the specificity claim. It is not a measured zero, and "has no effect" may not be written.**
10. **`P_SET`'s SIGN IS HORIZON-DEPENDENT** *(CORRECTIONS 278; see T18)*. `NWD` − `CARWD0` = **+0.4587 pp = +0.87 SE**
   in the registered window, but read in successive 5-epoch TEST windows it runs −0.9153 (55–59) … −0.1640 (75–79),
   **+0.1573** (80–84) … **+0.4587** (95–99): it **crosses zero near epoch 80 and is still moving at epoch 99**.
   `CARWD0` has plateaued (+0.0040 pp/ep) while `NWD` still climbs (+0.0276 pp/ep) — a 20-epoch slope difference of
   **+0.4726 pp, the same size as `P_SET` itself**. **Its sign is not a finding**, and `F_CAR` (0.9904) correspondingly
   **drifts through 1** across the horizon, which is the cleanest possible proof that it is not a decomposition.
11. **IDENTITY IS SEPARATED FROM NEITHER POSITION CLASS NOR COUNT/DOSE, and these are TWO DISTINCT confounds**
   *(CORRECTIONS 278; see T19)*. `ResNet18_c100` has exactly **five** 512-wide BN scales — {47, 50, 53, 56, 59} —
   and **three are the carriers**, so a class-pure, count-matched, **carrier-free triple cannot exist** at that depth
   (registered at 275.1; re-derived from the architecture three independent ways, and again here from
   `runs_alice2/cwd3-PARTITION-MANIFEST.txt`). On top of that, `CTLWD0`'s idx 48 is a BN **shift** with ‖w‖ 1.3e-10 at
   **record 0**, so its **effective** intervention is **two** genuine scales, not three. Therefore *"exempting ANY three
   genuine 512-wide `layer4` BN scales suffices, and two does not"* fits every number in `cwd3` **exactly as well** as
   the carrier account. **A two-carrier arm would separate them and was not run (O-12).**
12. **IDENTITY IS NOT SEPARATED FROM TERM MAGNITUDE EITHER, AND THAT LIMIT IS *BINDING ON EVERY SENTENCE* BY THE
   CAMPAIGN'S OWN REGISTRATION** *(new at 279; §1 A2, A3; T21)*. `results/SCORE-cdep1.txt` carries, under the header
   **"SCOPE, BINDING ON EVERY SENTENCE"**, the declaration that the design *"does NOT and CANNOT match them on
   DYNAMICAL MAGNITUDE"* and that an `IDENTITY-OPERATIVE` reading *"does NOT separate tensor identity from term
   magnitude"*. The gap it names is **Σ mean|L| ISO 8.1665e-01 against DEPTH 2.6482e-03 — a ratio of 308.4**, and the
   scorer's own words for it are *"the magnitude match this design CANNOT make"*. `cmg1`'s FINAL carries
   **`MAGNITUDE-NOT-SEPARATED`**; so do `cgn2`'s and `cgn3`'s; `cwd3`'s NOT-LICENSED block names it again
   (*"the carriers' vote mass is ×225 any admissible control's"*). **None of this reached the 276 or 277 drafts. It is
   why the claim in §2 is a localisation by MAGNITUDE and not by identity.**
13. **AND THERE IS A POSITIVE, LANDED, ADVERSE ARM ON EXACTLY THAT POINT** *(new at 279; §1 A1)*. `cvt1`'s INJECT arm
   (CORRECTIONS 230) gives a **NON-carrier** a carrier-sized vote (`layer4.1.bn1.weight` × 691) inside the rescued
   complement, and the complement **re-pins at epoch 37.6** and the arm falls to **30.1400**: `P_INJECT` **+34.6540 pp
   = +61.12 SE**, `D_INJ` **+18.1907 pp = +32.08 SE**, branch `STEP-SIZE-NEEDED-VOTE-SUFFICES`, stamp `INJECT-PARTIAL`.
   **A vote's collapsing effect does not require the vote to be a carrier's** — it requires it to be **large**. The
   arm is PlainNet-only, PARTIAL (it keeps 0.3442 of the HEAD gap), and timing is not separated from identity; §1 A1
   states all three.
14. **THE PRECONDITION HALF OF THE CLAIM IS NEARLY TRIVIAL PRIOR ART, AND SAYING SO IS NOT MODESTY** *(new at 279)*.
   That BN + weight decay destabilises training is Lobacheva et al. (arXiv:2106.15739); that one excludes BN scales
   from weight decay is standard practice, He et al. (arXiv:1812.01187). **What is ours is the localisation half**, and
   it is bounded as item 12 says. Selling the precondition as the finding would invite exactly the referee line the
   campaign has already written into its own limits (T1).

---

## 1. The adverse evidence — read this before the claim

**This section exists because the 276 and 277 drafts did not contain it.** Everything here is landed, registered,
committed evidence that cuts against the tensor-identity reading of the carrier account. Each row is re-derived here
from the artefact named. A referee who reads §2 without reading §1 has been misled, which is what the second hostile
pass said in those words.

### A1 — `cvt1`'s INJECT arm: a NON-carrier given a carrier-sized vote largely re-collapses the run

*Batch `cvt1`, `PlainNet18_c100` at `cpl2`'s cell, 15 runs, seeds {78, 79, 80}, 100 epochs.
**Provenance, stated because it differs from every other row in this file: NO `cvt1` scorer output is committed under
`results/` at this HEAD** (checked: `results/` contains no `cvt1` file). **So the levels and contrasts below were
RE-DERIVED BY ME from the fifteen raw `.out` files in `alice-backup/runs_alice2/`**, by a stdlib-only reader importing
no repo module (`plateau5` = mean TEST over `Epoch` lines 95–99; the CSV `plateau` column never read) — **all fifteen
runs show 100 `Epoch` lines, `RUN_DONE` and 0 tracebacks, and every figure below matches CORRECTIONS 230.3 digit for
digit.** The branch word, the stamps and the bounds are quoted from CORRECTIONS **230** (headline, 230.2's verbatim
FINAL, 230.3, 230.4(1), 230.6), which is the registered record. Tensor indices re-derived from
`runs_alice2/cwd2-PARTITION-MANIFEST.txt`, the same 53-tensor `PlainNet18_c100` frozen model. `cvt1`'s RULE 20 passed
at full coverage 15/15 before its own scoring (230.1).*

| arm | grouping / `VOTE_W` | TEST plateau5 (my re-derivation) | per seed s78 / s79 / s80 | TRAIN |
|---|---|---|---|---|
| `k01` | scalar / off | **11.9493** | 11.3820 / 11.7880 / 12.6780 | 11.8533 |
| `HEAD` (positive control) | {50} `[52,1]` / off | **64.7940** | 65.3100 / 65.1360 / 63.9360 | 79.7227 |
| `MUTE` | scalar / idx 50 × 0 | **10.9860** | 10.8520 / 10.9120 / 11.1940 | 10.9360 |
| `DOSE` | scalar / idx 50 × 0.1 | **11.9487** | 11.4760 / 12.5740 / 11.7960 | 12.0567 |
| **`INJECT`** | **HEAD's grouping, idx 47 × 691 in the complement** | **30.1400** | 30.6060 / 29.3960 / 30.4180 | 30.7727 |

* `SE_ARM_DIFF` here is **0.567010**, from `cvt1`'s own frozen prior σ **0.694443** — **not** §3's 0.556196, and not
  any other batch's (see the SE table in §3).
* **CO-PRIMARY `P_INJECT` = HEAD − INJECT = +34.6540 pp = +61.12 SE.** **KEY `D_INJ` = INJECT − `k01` = +18.1907 pp =
  +32.08 SE.** (Also re-derived: `P_VOTE` = HEAD − MUTE = +53.8080 pp = +94.90 SE; `D_HEAD` = +52.8447 pp = +93.20 SE;
  INJECT keeps **0.3442** of the HEAD − `k01` gap.) Branch **`STEP-SIZE-NEEDED-VOTE-SUFFICES`**, stamp
  **`INJECT-PARTIAL`**; the FINAL at 230.2 also carries `PATCH-BITES`, `K-FIXED-691`, `ONE-NETWORK-PLAINNET`,
  `HORIZON-100-ONLY` and `FLOOR-READINGS-ARE-BOUNDS`.
* **Who idx 47 is, stated exactly, because it matters and because it is easy to get wrong.** On `PlainNet18_c100`
  (53 tensors) idx 47 is **`layer4.1.bn1.weight`** — the `bn1` twin, in the same block, of the carrier idx 50
  `layer4.1.bn2.weight`. On `ResNet18_c100` (62 tensors) the tensor of that **same name** is **idx 56**, and idx 56 is
  a member of **both** control sets the specificity argument leans on: `cdep1`'s DEPTH triple {47, 48, 56} and its
  class-pure pair DEPTH2 {47, 56}. **This is a correspondence of NAME ACROSS TWO NETWORKS, not the same tensor index,
  and `cvt1` is PlainNet while `cdep1` / `cwd3` are ResNet. There is no INJECT arm on ResNet.** Both manifests were
  read for this paragraph.
* **What the arm shows.** `INJECT`'s complement's step size **collapses fully** — it pins at epoch **37.6 on all three
  seeds**, against `k01`'s 36.4 / 36.6 / 36.2 and HEAD's 99.8 — and the arm's TEST freezes at 30.0 from epoch 29 after
  tracking HEAD to epoch 19. The scorer's own reading (230.6): *"a vote's collapsing effect does not require the vote
  to be 50's: a non-carrier's term at the carrier's magnitude collapses the complement's step size"*, and *"This is the
  first result in the campaign in which magnitude was varied with identity held fixed."*
* **What it does NOT refute, in the registration's own words (230.4, 230.6).** (i) It is **PARTIAL**: INJECT keeps
  **0.3442** of the HEAD − `k01` gap and sits 0.14 pp **above** the top of the 8–30 band the matching `STEP-AND-VOTE`
  account registered. (ii) **Timing is not separated from identity**: the ×691 vote first outvotes the complement only
  from about epoch 18, so "a full step-size collapse that simply starts late" and "a weaker effect because the vote is
  not 50's" are not distinguished — registered **UNSURE**. (iii) **One fixed K = 691, one dose, one network, one cell,
  100 epochs.** (iv) The sentence *"a carrier-sized vote from another tensor re-collapses the complement as fully as
  50's own"* is **explicitly not licensed**.
* **Why it is nevertheless fatal to the identity framing.** The tensor-identity reading predicts that a non-carrier's
  vote, however large, should not do a carrier's work. It did **61 SE** of a carrier's work. **Any sentence of the form
  "these tensors specifically" must be written so that this arm is consistent with it** — which is what "localisation
  by term magnitude" does and "localisation by tensor identity" does not.

### A2 — `cdep1`'s scope declaration is BINDING ON EVERY SENTENCE, and it forbids the identity reading

*Artefact: `results/SCORE-cdep1.txt`, the `[P]` block and the closing SCOPE paragraph, quoted verbatim.*

> `SCOPE, BINDING ON EVERY SENTENCE: this batch matches DEPTH to ISO on group sizes, isolated numel, width, depth and
> normalisation-layer type. It does NOT and CANNOT match them on DYNAMICAL MAGNITUDE -- on the scalar trajectory the
> carriers' mean |L| exceeds every 512-parameter layer-4 non-carrier's by two to five orders of magnitude, and no set
> of members closes that gap. An IDENTITY-OPERATIVE reading therefore means 'not any three matched layer-4 BN
> parameters', and does NOT separate tensor identity from term magnitude.`

The numbers behind it, from the same artefact's `[P]` block (mean |L| on pinned records, rank out of 62):

| idx | tensor | mean \|L\| | rank |
|---|---|---|---|
| 59 | `layer4.1.bn2.weight` | 3.2984e-01 | **1** |
| 50 | `layer4.0.bn2.weight` | 2.9155e-01 | **2** |
| 53 | `layer4.0.shortcut.1.weight` | 1.9526e-01 | **3** |
| 56 | `layer4.1.bn1.weight` | 1.5166e-03 | 33 |
| 47 | `layer4.0.bn1.weight` | 1.1298e-03 | 36 |
| 48 | `layer4.0.bn1.bias` | 1.7399e-06 | **62** |

**`SUM ISO 8.1665e-01`, `SUM DEPTH 2.6482e-03`, `ratio 308.4` — the scorer's own annotation on that line is *"(the
magnitude match this design CANNOT make)"*.** The three carriers are ranks **1, 2 and 3 of 62**; the control triple's
members are ranks 33, 36 and 62. **The control is not a magnitude-matched control and cannot be made into one on this
network** (188.3, re-measured on `cdep1`'s own `k01`: the best admissible carrier-free triple is still ×225 short).

### A3 — `cmg1` stamps `MAGNITUDE-NOT-SEPARATED` on its FINAL, and says in prose what it means

*Artefact: `results/cmg1_mergecarrier_score_alice2.txt`, FINAL line and NOT-LICENSED block.*

FINAL: `NO-MERGE-HARMS | … | SIGMA-PRIOR-FROZEN | MAGNITUDE-NOT-SEPARATED | …`, and in the same file:

> `Identity vs MAGNITUDE (188.3): at a shared step size the carriers' |L| exceeds T's by x100+ (premise S), so a
> carrier-specific result does not separate which tensors from how large their terms are.`

`cmg1`'s own deciding contrast is also the cycle's second-narrowest: `D_CAR` = `KLS` − `MCAR` = **+4.1150 pp = +8.54
SE** against a `MARGIN` bar of 5.0 pp — **0.885 pp = 1.84 SE inside**, on `cmg1`'s **own** `SE_ARM_DIFF` **0.481680**
(four seeds), not on 0.556196. It is reported here and is **not** load-bearing in §2.

### A4 — the same stamp is on the GroupNorm batches, and the pattern is the same on four networks

`cgn2`'s FINAL (`results/cgn2_gn_isolation_score_alice2.txt`, CORRECTIONS 225) carries `MAGNITUDE-NOT-SEPARATED` and
`CTL-MATCHED-ON-NUMEL-NOT-CLASS`; `cgn3`'s (CORRECTIONS 231) carries `MAGNITUDE-NOT-SEPARATED` too. And the campaign's
own cross-batch reading, **CORRECTIONS 226.7**, states it as a general observation rather than a per-batch gap:

> *"On all four networks now examined, the carriers are the top DOWN-voting terms by a factor no carrier-free matched
> set can close (×225 ResNet-BN, VGG `bn8` 0.58 share, ×3.1–×14 GN, ×691 PlainNet). The confound is not a design gap in
> any one batch; it is what these trajectories look like."*

and, in the same entry:

> *"The carrier-set CARDINALITY follows the TOPOLOGY, not the normaliser."*

**Read together, A1–A4 are not four caveats. They are a positive account** — the shared vote is carried by whichever
tensors hold the large terms; which tensors those are is set by the architecture; and an intervention that moves the
magnitude moves the outcome (A1). **That account is what §2 claims. The tensor-identity account is what §2 does not
claim.**

---

## 2. The claim, in one paragraph

This is the **rewritten** paragraph. Eight over-statements were struck before it (§2.1, §2.2); `cwd3` amended it
(§2.3); and the second hostile pass at CORRECTIONS 279 **reframed** it (§2.4). Every clause about "these tensors" now
carries the identity-vs-magnitude bound, or is not written.

> The headline of the paper is unchanged: the **denominator** result — a properly tuned non-meta baseline is not beaten
> by MetaOptimize, measured most strongly on CIFAR-100 (the campaign's own registered result, `cuc1`: CORRECTIONS
> **220**, MASTER-TABLE row 19 moved `OPEN` → `CONFIRMED, RESCOPED` at **229**; see **E0**, and read E0's bounds with
> it) — together with the **count-matched partition audit**. The mechanism line is a **bounded secondary contribution,
> stated as a configuration-conditional failure mode and never as a property of BatchNorm or of the method in
> general**, and it has two halves of very unequal weight. **The precondition half is true and close to trivial**: under
> coupled L2 weight decay applied to normalisation scales — a configuration common practice avoids (He et al.,
> arXiv:1812.01187) and one already reported to destabilise BatchNorm training (Lobacheva et al., arXiv:2106.15739) — a
> single shared meta-learned **Lion** step size collapses on CIFAR-100, on both a residual and a residual-free 18-layer
> network, and removing that decay removes the collapse at every grain we tested: from every tensor and the meta trace
> on ResNet; from the **twenty** BatchNorm scales of the whole ResNet network (4,800 of 11.2 M parameters — a
> network-wide mask, not the three carriers); **on ResNet from three named scales ALONE** (1,536 of 11,220,132
> parameters, in the weight update and the meta trace together), **which removes the collapse as fully as the
> network-wide mask does** (`P_CAR` **+47.2787 pp = +89.34 SE**; the carrier-only arm lands **inside** the network-wide
> arm's recovery band); and from a **single** BatchNorm scale on PlainNet (512 parameters), where it also removes the
> damage of an externally held step **at PlainNet's measured dose (`tri:9428`)** on that same tensor **to within the
> noise floor** (`F_WD` = 1.012, the excess being `P_LEFT` −0.6253 pp = −1.12 SE, inside the 2.0 pp null bar; **PlainNet
> only**). **The second half is the contribution, and it is a LOCALISATION BY TERM MAGNITUDE, not by tensor identity**:
> what we can defend is that **the shared Lion meta-update's vote is carried by whichever tensors hold the large terms
> in the shared sum, and that at these cells those tensors are three last-block BatchNorm scales** — giving those three
> their own step-size group recovers the whole scalar-to-layerwise gap, and removing their coupled decay alone removes
> the collapse, while two matched non-carrier sets do neither. **The campaign's own registered scope notes forbid
> calling this tensor identity, and the forbidding is binding, not decorative**: `cdep1`'s scorer declares, *"BINDING ON
> EVERY SENTENCE"*, that its design *"does NOT and CANNOT match them on DYNAMICAL MAGNITUDE"* and *"does NOT separate
> tensor identity from term magnitude"* (Σ mean |L| **8.1665e-01** against **2.6482e-03**, ratio **308.4**; the carriers
> are ranks 1, 2 and 3 of 62 and every matched control member ranks 33rd or worse); `cmg1`, `cgn2` and `cgn3` all stamp
> **`MAGNITUDE-NOT-SEPARATED`**; and `cwd3`'s own NOT-LICENSED block repeats it (*"the carriers' vote mass is ×225 any
> admissible control's"*). **There is also positive evidence for the magnitude reading and against the identity
> reading, and it is landed, registered and adverse**: on PlainNet, giving a **non-carrier** — `layer4.1.bn1.weight`,
> the `bn1` twin, a tensor whose namesake on ResNet sits inside both of our control sets — a carrier-sized vote (×691)
> inside an otherwise rescued complement **re-pins that complement at epoch 37.6 and drops the arm to 30.1400**
> (`P_INJECT` **+34.6540 pp = +61.12 SE**, `D_INJ` **+18.1907 pp = +32.08 SE**, `INJECT-PARTIAL`, CORRECTIONS 230); the
> collapse is **partial**, its timing is **not** separated from its identity, and it is one dose on one network — but a
> non-carrier's term at a carrier's magnitude does most of a carrier's work, which is exactly what a magnitude account
> predicts and an identity account does not. **What remains specific, and the form in which it may be written, is an
> asymmetry between a measured rescue and BOUNDED FLOORS, never a difference between two magnitudes**: at the ResNet
> cell `P_SPEC` **+47.2627 pp = +89.31 SE** against **|P_CTL| ≤ 1.0744 pp** and **|P_CTL2| ≤ 1.1104 pp** at ±2 SE — a
> ratio of **42.6 : 1**, or 23.6 : 1 against the registered `NULL` bar — with the count-matched triple's level
> **inside** the registered saturation band, so the entitled statement is the **bound** `D_DEPTH ≤ 5.0 pp` and *"recovers
> none of it"* may not be written. (**Disclosed**: that control triple {47, 48, 56} contains one BatchNorm **shift**,
> `layer4.0.bn1.bias`, not three scales; the answering class-pure scale-only pair {47, 56} is in the same artefact,
> `D_DEPTH2` **+0.0960 pp**, itself a floor bound `≤ 5.0 pp`, with `DEPTH − DEPTH2` **+0.0727 pp = +0.10 SE**, so the
> result does not rest on the shift member — **and does not become a magnitude by being class-pure**.) At PlainNet's
> measured dose, any one of those three scales, held alone in its own group while the other 61 tensors share one step
> size, is **sufficient** to stall the ResNet run; whether that requires the other two to keep voting in the shared sum
> is **INDICATED, not established** — one arm (`ISOSPLIT`), no free-split control (`NO-FREE-SPLIT-CONTROL`), and the
> narrowest margin of the cycle, `P_SPLIT` **+3.0767 pp**, only 1.9233 pp = **3.46 SE** inside its 5 pp bar. **Three
> confounds travel with every "these three" sentence and may not be dropped: term magnitude (above); position class —
> only five 512-wide BatchNorm scales exist in this network and three of them ARE the carriers, so "these tensors" is
> not separated from "this position class" (Kim et al., arXiv:2205.07260); and count/dose — the count-matched control's
> third member is a shift carrying no effective decay dose, so "any three genuine 512-wide `layer4` scales suffice and
> two do not" fits every number in `cwd3` equally well.** The residual left to the other seventeen scales is likewise
> **bounded, not measured** (`P_SET` **+0.4587 pp = +0.87 SE**, ≤ +1.5171 pp at 2 SE, **and its sign is
> horizon-dependent**), so no share may be read off it. We do not identify the route by which the decay acts: our
> instrumentation records a carrier's weight norm only in the arms where the decay is off, and in those arms the scales
> **grow** rather than shrink, so the arms that actually collapse carry no measurement. **This is a scope and
> precondition result with a bounded localisation attached. It is not a mechanism.**

Two sentences may be added, and no more:

* The isolation rescue **transfers to a second meta step size** (3e-4: `D_ISO` +41.1567 pp) **while the vote-dominance
  nomination does not** (`DOM_C` 0.4727 against a 0.50 bar) — so at that cell the rescue and the nomination are **not
  locked together** (CORRECTIONS 268).
* Each number in the paragraph is a **one-cell** number and must carry its cell.

### 2.1 The four over-statements struck from 273.12, each with its evidence

| # | 273.12 said | Why it is not earned | Corrected form used in §2 |
|---|---|---|---|
| **O1** | "carried by a small number of **last-block** BatchNorm scales … removing the coupled decay from **those scales alone** — 4,800 of 11.2 M parameters on ResNet" | The 4,800 parameters are the **20 BatchNorm scales of the whole network**, `DECAY_MASK=normscale`, derived twice and once on the live model (271.4(1), 271.5; `results/cwd1_livemodel_normscale_check.txt`). The three carriers are 3 of those 20; **17 non-carrier scales are unmasked in the same switch.** The sentence conflates the *nomination* set (3, last block) with the *mask* set (20, network-wide). | The grain is named at each cell: every tensor + meta trace (ResNet), 20 network-wide scales (ResNet), **three carriers alone (ResNet, `cwd3`, earned at 278)**, one scale (PlainNet). |
| **O2** | "removes the damage of an externally held large step on the carrier (**F ≈ 1.0**)" as a general clause | `F_WD` = 1.012 is `cwd2` only: `PlainNet18_c100`, idx 50, one dose (`tri:9428`), 3 seeds, complement forced onto `cvt6`'s replayed head path. There is **no ResNet held-step arm under a decay mask at all.** | "(F = 1.012, **PlainNet only**)". |
| **O3** | "a reader who follows that practice **will not meet** the collapse" | A prediction about all readers from three cells. What was measured is that the collapse **did not occur at any cell we tested with the decay removed** (`cmo1` W0, `cwd1`, `cwd2`, `cwd3`). | §6 T1 states it as "did not meet it at any cell tested", never as a claim about readers. |
| **O4** | "the norm scales **recover 98.06 %** of the whole-network effect" used as a decomposition | `cwd1`'s `P_NWD` +47.8247 against `cmo1`'s `L_W0` +48.7713 is a **between-batch** ratio: different interventions, different batches, no shared bar, no shared seed — labelled UNSURE, orientation only, at 271.6 F4 and 271.7. | Quoted once, explicitly labelled **orientation, cross-batch, UNSURE**, and never used to license a residual. `F_CAR` 0.9904 is refused on the same grounds (§3.3b). |

### 2.2 The four over-statements struck by the referee pass at CORRECTIONS 277

| # | the 276 draft said | why it is not earned | corrected form |
|---|---|---|---|
| **R1** | a count-matched non-carrier triple "**recovers none of it**" | `cdep1`'s registered scorer forbids it: *"`DEPTH` level 23.5207 is INSIDE the registered saturation band [21.0940, 27.9520]: its level is a **BOUND, NOT a magnitude**. Entitled: `D_DEPTH <= 5.0 pp`."* FINAL carries `DEPTH-FLOOR-SATURATED`. | The **bound** `D_DEPTH ≤ 5.0 pp`, with the floor discipline named; `cdep1` on T7's list. |
| **R2** | "a count-matched non-carrier triple **in the same layer**", with no disclosure of what is in it | `cdep1`'s manifest: DEPTH = `layer4.0.bn1.weight` (47), **`layer4.0.bn1.bias` (48)** and `layer4.1.bn1.weight` (56). **Idx 48 is a BatchNorm SHIFT, not a scale.** | The shift is **disclosed by name** wherever the control is mentioned, with `DEPTH2` {47, 56} cited as the class-pure answer (`D_DEPTH2` +0.0960 pp, `DELTA_BIAS` +0.0727 pp = +0.10 SE, `BIAS-NULL`). |
| **R3** | "held alone at a **large** step size" | 272.6 F1: only the clamp floor and **one** measured dose (`tri:9428`) were ever run; no ladder licenses "large". | "at PlainNet's measured dose (`tri:9428`)" everywhere in my own prose. Where §2.1 O2 **quotes** 273.12 the word stays, because that is the record of what was said. |
| **R4** | "— **provided** the other two still vote in the shared sum" | One arm (`ISOSPLIT`); `NO-FREE-SPLIT-CONTROL` on `cvt10`'s FINAL; `P_SPLIT` +3.0767 pp is 1.9233 pp = **3.46 SE** inside its 5 pp bar, the cycle's narrowest. | **INDICATED, not established**, with the single arm, the missing control and the margin in the same sentence. |

**Provenance note, kept from 276/277 because it is still true.** My brief at 276 named four findings as belonging to
"the final audit". No audit report could be located under `docs/`, `results/` or the scratchpad; CORRECTIONS 274 is an
addendum correcting four descriptive `dm_*` record counts, which is a different list. **O1–O4 were each re-verified
against the committed record named in its row**, not taken on the brief's authority. **UNSURE** whether that is the
same list the audit meant.

### 2.3 What `cwd3` changed at CORRECTIONS 278, and what it did not

| | before `cwd3` | after `cwd3` |
|---|---|---|
| **the ResNet carrier-only mask** | **absent.** §0 bound 3, T2 and O-1, the top-ranked open question | **run and landed.** `P_CAR` +47.2787 pp = +89.34 SE, `CARWD0` **inside** `NWD`'s `REC` band (+4.5413 pp above the 65.7227 bar). §0 bound 3 **retired at this cell**, T2 **rewritten**, O-1 **closed** |
| **specificity of the decay result** | untested on ResNet | `P_SPEC` +47.2627 pp = +89.31 SE against **two** matched non-carrier sets, both at `k01`'s floor (**E20**) — an asymmetry against **bounds**, `\|P_CTL\| ≤ 1.0744`, `\|P_CTL2\| ≤ 1.1104` at 2 SE |
| **the other 17 scales** | unasked | `P_SET` +0.4587 pp = +0.87 SE, **bounded at ≤ +1.5171 pp at 2 SE and NOT distinguishable from zero** — and **its sign is horizon-dependent** (**T18**) |
| **identity vs position class** | the same bound, registered at 275.1 | **unchanged, and re-derived independently from the architecture**: only five 512-wide BN scales exist, three are carriers (**T19a**) |
| **identity vs count / dose** | not named anywhere | **named, and NOT excluded** (**T19b**): `CTLWD0`'s third member is a BN shift with ‖w‖ 1.3e-10 at record 0 |
| **identity vs term magnitude** | **binding since 188.3 and never written down** | **unchanged, and now written down** (§0 item 12, §1 A2–A4, **T21**) |
| **the write-up's headline** | denominator + count-matched partition audit | **unchanged** |

### 2.4 What the hostile pass of CORRECTIONS 279 struck, and where each fix landed

Every row was re-derived here from the committed artefact named, not taken from the referee's summary.

| # | severity | the finding | re-derived against | where the fix landed |
|---|---|---|---|---|
| **N1** | **FATAL** | **`cvt1`'s INJECT arm (CORRECTIONS 230) is absent from the draft.** Landed, registered, adverse evidence on the exact question the specificity argument turns on — a non-carrier given a carrier-sized vote largely re-collapses the run — and it was omitted. | **the fifteen raw `cvt1` `.out` files** (stdlib-only reader of my own; every level and contrast equals 230.3 digit for digit — no `cvt1` scorer output is committed under `results/`), plus CORRECTIONS 230's headline, 230.2's verbatim FINAL, 230.4(1)'s pin table and 230.6's licence / NOT-licensed blocks; tensor indices from `runs_alice2/cwd2-PARTITION-MANIFEST.txt` | New **§1 A1** (first-class, before the claim), **§0 item 13**, a clause **inside the §2 claim paragraph**, evidence row **E22**, and new limit **T20**. |
| **N2** | **FATAL** | **`results/SCORE-cdep1.txt`'s *"SCOPE, BINDING ON EVERY SENTENCE"* declaration, its 308.4 magnitude ratio, and `cmg1`'s `MAGNITUDE-NOT-SEPARATED` never reached the write-up.** | `results/SCORE-cdep1.txt` `[P]` block and SCOPE paragraph; `results/cmg1_mergecarrier_score_alice2.txt` FINAL + NOT-LICENSED; `cgn2` / `cgn3` FINALs; CORRECTIONS 226.7 | New **§1 A2, A3, A4**, **§0 item 12**, the reframed claim, evidence rows **E23**, **E24**, and new limit **T21**. |
| **N3** | **FATAL, consequent** | The claim was stated as a localisation **by tensor identity**, which exceeds the campaign's own record. | N1 + N2 together | **§2 rewritten as BOUNDED LOCALISATION BY TERM MAGNITUDE**; every "these tensors" clause now carries the bound or is not written. §4.1 and §5 restated to match. |
| **N4** | major | **"count-matched same-class control" is wrong.** The triple contains a BN shift; the class-pure arm is the **pair**. Two literal occurrences (§5 Arora row, §5 Mueller row) — **plus two related imprecisions I found while checking: "does not rescue" for a floor bound (Arora row) and "a carrier-specific rescue **beaten by** a count-matched non-carrier control" (§5 closing clause), which reverses the sense.** | `results/SCORE-cdep1.txt` [G1] manifest | All four corrected in **§5**. **UNSURE** which third literal instance the referee counted; only two exist in the 278 text, and I say so rather than invent one. |
| **N5** | major | **The SE preamble was wrong for `csv1` and `cmg1`.** `csv1` uses **three** SEs (0.556196 3v3, 0.481680 4v4, 0.520274 4v3); `cmg1` uses **0.481680**. | `results/csv1_shadowvote_score_alice2.txt` line *"SE(3 vs 3) 0.556196 ; SE(4 vs 4) 0.481680 ; SE(4 vs 3) 0.520274"*; `results/cmg1_…` *"SE_ARM_DIFF 0.481680 = SIGMA_USED * sqrt(2/4)"* | **§3's SE table**, per contrast, and **T6**. **I also found two more the draft never named: `cvt1` uses 0.567010 from a DIFFERENT frozen prior 0.694443, and `cuc1` (E0) uses 0.4674 from its own plateau5 prior 0.572475.** Seven distinct SE values are now tabulated. |
| **N6** | major | **E0 quoted a CROSS-SETTING comparison that 220.7 prints as *"never a token"*, and dropped `COUNTERWEIGHT-NOT-TESTED` and the AUC reversal.** | CORRECTIONS 220.7 (*"printed for orientation only (the scorer prints it under 'CROSS-SETTING (printed, never a token)')"*; `CURVE-DEFICIT-LOWER-BOUND`; −2.3489 pp AUC reversal at S\*) | **E0 rewritten**: the three-way comparison is labelled BETWEEN-BATCH, orientation only, never a token; `COUNTERWEIGHT-NOT-TESTED`, `PAPER-CONFIG-NOT-TESTED`, `ONE-GRANULARITY-CHUNK771` and the **AUC reversal** now travel with it. |
| **N7** | major | **T13's "no GroupNorm" is false**, and so are two neighbouring clauses. | CORRECTIONS **217** (`cgn1`, `ResNet18_gn_c100`, D +37.3833 pp), **225** (`cgn2`, `IDENTITY-TRANSFERS-GN`, `DELTA_ID` +41.5167 pp = +67.23 SE), **231** (`cgn3`, `RESCUE-SURVIVES`, `RHO` 1.2235 at 430 epochs); **219** (`cvh1`, VGG11_bn, ρ 1.0001 at 328); `LIMITS-PREP` §2.2 census (ResNet34_c100, ResNet10_c100, ResNet18_tin, IN-489) | **T13 rewritten.** GroupNorm **was** run and the carrier identity result **transfers** there; VGG11_bn is a non-residual family outside PlainNet and **does** carry isolation arms; ResNet34/50 exist in the corpus but carry **no** carrier arm. What survives is: every result in **§3** is ResNet18/PlainNet18; **LayerNorm untested**; nothing outside convolutional image classifiers. |
| **N8** | major | **A `dm_absmin` figure is below the quoted bound.** | `results/cwd1_normwd_score_alice2.txt`: the DESCRIPTIVE block's header says **"seed means"**, and the `G-BITE` lines give the per-seed last records — `kLNWD` **0.502388 / 0.469448 / 0.538347** (mean 0.503394 → printed "0.503") and `k01NWD` **0.981039 / 0.984450 / 0.983544** (mean 0.983011 → printed "0.983") | **§4.2 and §5's Zhou row corrected**: the printed 0.503 / 0.983 are **seed means, not minima**; the smallest per-seed final-record reading over `cwd1`'s masked arms is **0.4694**, which is **below** the 0.503 the 277 draft quoted as a bound. The conclusion is unchanged (0.4694 is still more than two orders above the 1e-3 threshold and `dm_small` is 0 everywhere it is written). **T17 rewritten.** |
| **N9** | major | `cwd3` must appear in bounded form with its two new confounds and the count/dose rival named. | CORRECTIONS 278 headline bounds (4) and (5); `results/cwd3_carrierwd_score_alice2.txt` | **§3.3b (E19–E21)**, **§0 items 9–11**, **T18**, **T19**, **O-12**; and O-12 now records that **Track 2 of this cycle is launching the batch that addresses the count/dose rival** — *nothing is registered or launched by this file, and no result from it is quoted here.* |
| **N10** | found while re-checking | **T16's evidence-row count was stale**: "19 numbered evidence rows (E0–E18)" after `cwd3` had already added E19–E21. | this file | **T16** now says **25 rows (E0–E24)** and re-states the contrast counts. |
| **N11** | found while re-checking | **The open RULE 16 defect count is wrong, and the campaign's own text is wrong with it.** "Six" is a miscount of its own enumeration: 270.6 F1 (1) + 271.6 F1, F2 (2) + 272.6 F1, F2 (2) + 273.6 F1, F2 (2) = **seven**, and each of those entries' own headers says "the … defect report(s)" in exactly that arithmetic. **278.6 D1 makes eight**, and the draft named D1 only in its provenance section. | the four entries' own fix tables and headers; 278.6 D1 | **T10 rewritten: eight open, none fixed, none hidden**, with the miscount in 277.6 / 278.6 named as a miscount rather than repeated. |
| **N12** | found while re-checking | **T8 compressed three different hardware censuses into one list.** `cmo1` ran on **two** accelerator classes (10 × RTX 2080 Ti, 17 × L4), `cwd1` on **two** (7 × L4, 2 × 2080 Ti), `cwd2` on **three** (8 × A100-MIG, 4 × L4, 3 × 2080 Ti). The draft's "(2080 Ti / L4 / A100-MIG)" reads as all three classes in all three batches. **It also omitted that `cmo1` has a FULLY hardware-confounded contrast** (`DI_M9`, labelled `HARDWARE-CONFOUNDED / UNSURE` at 264.4(4)). | CORRECTIONS 264.4(4); 271.4(5); 273 headline bound (1) | **T8 rewritten per batch**, with the registered device estimates quoted to their own precision (A100 **+0.0460**, L4 **−0.0375**, 2080 Ti **−0.0727** pp) and `DI_M9`'s confounding stated. **E18's derived "+1.5133 pp above `M9kL`" is relabelled DESCRIPTIVE** and its one mismatched seed pair disclosed. |
| **N13** | found while re-checking | **§5's Kim row read as a position-class result, which 270.6 F3 forbids.** It wrote "`ONE53` … stalls at +35.2140 pp", conflating a hold's contrast with a stall level. | CORRECTIONS 270.6 F3: *"all three singletons read `-STALLS`, so `KIM-CATEGORY-SPLIT` does not fire; the 53-vs-{50,59} difference lives only in the FREE rescue levels (57.5033 against 64.7967 / 67.7053) and in `L_LAST_DOWN` +9.9213 pp, both DESCRIPTIVE"* | **§5's Kim row rewritten** to say that the registered position-split token did **not** fire and that the ordering is DESCRIPTIVE only. |
| **N14** | found while re-checking | Two small precision slips: "‖w‖ 1.3e-10 **at init**" (it is at **record 0** of the probe, which is step 0 but is a probe reading, not an initialiser fact), and T9's superseded σ figure. | `results/cwd3_carrierwd_score_alice2.txt` DESCRIPTIVE block; CORRECTIONS 278.9 | Corrected in **§0 item 11**, **T19** and **T9**. |

**Declined, deliberately, and why.** (i) I did **not** edit any quotation. Where §2.1 O2 quotes 273.12 verbatim the
word "large" stays, and where T10 and O-8 are *about* that word it stays; editing a quotation would destroy the record
of what was said. (ii) I did **not** invent a third literal "same-class" occurrence to match the brief's count; two
exist, I corrected those two plus two related errors of the same family, and I say UNSURE about the third (N4).
(iii) I did **not** fix any registered file. The eight open RULE 16 defects — 278.6 D1 included — are reported and
stand. (iv) I did **not** score, launch or read any result of the batch Track 2 is launching; O-12 records the
intention and nothing else.

---

## 3. What is established

Every row re-derived for this file from the artefact named. Levels are `plateau5` = mean TEST over `Epoch` lines 95–99
of each run's own raw `.out`; the CSV `plateau` column is never read.

**THE STANDARD ERRORS ARE NOT ALL THE SAME, AND THE 276/277 DRAFTS GOT THIS WRONG TWICE.** Seven distinct
`SE_ARM_DIFF` values are in play across the ten artefacts this file cites. Mixing them is how a 61.56 turns into an
83.65 that no artefact prints.

| batch | frozen σ used | `SE_ARM_DIFF` | applies to |
|---|---|---|---|
| `cmo1`, `cwd1`, `cwd2`, `cvt10`, `cst2` | prior 0.681198 | **0.556196** (3 v 3) | E1, E6–E11, E16, E18 |
| `cvt1` | prior **0.694443** | **0.567010** (3 v 3) | **E22** |
| `csv1` | prior 0.681198 | **three**: **0.556196** (3 v 3), **0.481680** (4 v 4), **0.520274** (4 v 3) | E12 and E15 on 0.556196; **E14 on 0.481680**; **E13 on 0.520274** |
| `cmg1` | prior 0.681198 | **0.481680** (4 v 4) | A3, T6, T16 |
| `cdep1` | **its own**, frozen in its scorer *"from a corpus reader that excludes `cdep1-*` rows"* | **0.755682** | E4, E5 |
| `cwd3` | prior **0.648113** | **0.529182** (3 v 3) | E19–E21 |
| `cuc1` | its own plateau5 prior **0.572475** | **0.4674** | E0 |

`cdep1`'s 0.755682 is the **largest**, so E4/E5 are if anything under-stated in SE. `cwd3`'s prior is the corpus floor
re-derived at 275, not 0.681198. Every contrast in every row below is **within batch**.

### 3.0 The headline the mechanism line sits beside (not this cycle's work, cited so it is not unsourced)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E0 | **The denominator result.** On **unaugmented CIFAR-100** (`ResNet18_c100`, `AUGMENT=0` on all 30 runs) a tuned plain SGD+momentum+cosine `lr` ladder peaks **interior** at `lr = 0.4` with **65.0573** and beats the best of five MetaOptimize cells (`m1e3a1e3`, **52.8793**) by `GAP_END` **+12.1780 pp = +26.05 SE** (SE **0.4674**); branch `DEFICIT-HOLDS`, argmax interior so the token does **not** take `LOWER-BOUND`. | as stated | **No scorer output for this batch is committed under `results/` at this HEAD.** The registered record is CORRECTIONS 220 itself (scorer `analysis/cUC1_unaug_c100_score.py`, sha `9c2f752d…`, run unedited, exit 0, RULE 20 30/30) and MASTER-TABLE row 19. **Flagged: the campaign's existing registered result, cited by CORRECTIONS number, not re-derived by me from an artefact under `results/`.** | 220; verdict moved at 229 |

**Bounds that travel with E0 and must be quoted with it. Three of them the 276/277 drafts dropped.**

* **The "largest deficit" clause is BETWEEN-BATCH and is a *token-free* orientation reading.** 220.7 states it in these
  words: the three-way comparison with `cdn1` (+5.699 pp, `AUGMENT=1`, same network) and `cau1` (+3.617 pp,
  `AUGMENT=0`, CIFAR-10) *"is **between batches** and is printed for orientation only (the scorer prints it under
  'CROSS-SETTING (printed, never a token)')"*. **So "measured most strongly on CIFAR-100" is an orientation statement,
  not a measurement, and §2 must say so** — which it now does by pointing at these bounds.
* **`CURVE-DEFICIT-LOWER-BOUND`: the AUC reading REVERSES at the endpoint-best rung** (−2.3489 pp at S\*), and 220.7
  says *"Anyone quoting the parent's evidence type must quote that too."* The 277 draft did not.
* **`COUNTERWEIGHT-NOT-TESTED`**: no weight-decay or regularisation counterweight was swept on the method side, so
  *"the method needs augmentation"* is not licensed. The 277 draft dropped this stamp entirely.
* **`ONE-BASELINE-FAMILY`** (SGDm+cosine only), **`PAPER-CONFIG-NOT-TESTED`** (the parent's own α₀ 1e-6 is not on the
  grid), **`ONE-GRANULARITY-CHUNK771`**, `CIFAR100-RESNET18-ONLY`, 100 epochs only.
* **Meta-side tuning is bounded, not exhausted**: M\* sits at an edge of the grid and beats the CENTER by +0.1307 pp =
  +0.28 SE, so ms-HIGH under-tuning is *"bounded by a flat top, not excluded"*.

E0 is **not** a result of this cycle and nothing in §§3.1–3.7 rests on it.

### 3.1 The phenomenon and its carriers (ResNet18_c100, mechanism cell)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E1 | The scalar collapse, in batch | `k01` **22.7887** vs `kL` **69.0507**; `G_A` **+46.2620 pp = +83.18 SE** | `results/cmo1_momwd_score_alice2.txt` | 264 |
| E2 | Census view of the same cell (not a scorer; corpus means after `filter_rows`) | scalar **22.96** (n 44) vs layerwise **69.42** (n 32), ratio 0.331 | `LIMITS-PREP` §2.2 from `results/all_runs.csv` | 254 |
| E3 | Three tensors carry the shared vote — **and they are the three largest terms** | on the scalar arm, `layer4.1.bn2.weight`, `layer4.0.bn2.weight`, `layer4.0.shortcut.1.weight` are in the carrying set on **1239 / 1239** DISAGREE records (share 1.000 each); median \|L\| **×212 / ×188 / ×124** the median tensor, and they are **ranks 1 / 2 / 3 of 62** by median \|L\|; bn-scale class share of Σ\|L\| **0.598** | `results/ctd1_tensor_dominate/ATTACK_REPORT.txt` | 184 |
| E4 | Isolating them rescues; a **count-matched** non-carrier triple **stays on the floor** — a BOUND, not a magnitude | ISO **70.0440**, DEPTH **23.5207**, `DELTA_ID` **+46.5233 pp = +61.56 SE**; `D_ISO` +46.6920; isolated numel matched 1,536 = 1,536, all six tensors in `layer4`. **`D_DEPTH` prints +0.1687 pp but may NOT be read as an effect**: DEPTH's level is inside the registered saturation band [21.0940, 27.9520], FINAL `DEPTH-FLOOR-SATURATED`, and the scorer entitles us to **`D_DEPTH ≤ 5.0 pp`** only (164.6). **Composition, disclosed**: DEPTH = {47 `layer4.0.bn1.weight`, **48 `layer4.0.bn1.bias` — a BatchNorm SHIFT, not a scale**, 56 `layer4.1.bn1.weight`}. The **class-pure** answer is in the same artefact: `DEPTH2` = {47, 56}, `D_DEPTH2` **+0.0960 pp** (also a bound, `DEPTH2-FLOOR-SATURATED`), `DELTA_ID2` +46.5960 pp, `DELTA_BIAS` **+0.0727 pp = +0.10 SE**, FINAL `BIAS-NULL`. **SE on this row and E5 is `cdep1`'s own 0.755682.** **The same artefact's SCOPE paragraph forbids reading any of this as tensor identity — see E23.** | `results/SCORE-cdep1.txt` | 193 (ISO first at 187) |
| E5 | One carrier free also largely rescues | `ONE` ({50} alone, free) **64.8267**, `D_ONE` +41.4747 pp = **+54.88 SE** (on 0.755682) | `results/SCORE-cdep1.txt` | 193 |

### 3.2 Sufficiency of a held carrier step (ResNet18_c100, `ciso1`'s cell, PlainNet's dose `tri:9428`)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E6 | Each carrier alone, held, is **sufficient** to stall | `P_ONE50` **+43.6627** (+78.50 SE), `P_ONE59` **+46.6080** (+83.80 SE), `P_ONE53` **+35.2140** (+63.31 SE); the four stalled arms sit **below** `k01` 22.7540 (−1.6200 / −1.6567 / −0.4647 / −4.0307), so each `-AT-K01` word is a **LOCATION**, a bound, never a point estimate | `results/cvt10_onevsthree_score_alice2.txt` | 270 |
| E7 | …and the condition "only while the others vote" is **INDICATED, not established** | `ISOSPLIT` ({50} held at `tri:9428`, {53,59} free in their own group, sizes `[59,1,2]`) **67.0893** against ISO **70.1660**, `P_SPLIT` **+3.0767 pp = +5.53 SE**; the arm does **not** stall, while `ONE50BIG` sits −1.6200 pp **below** `k01`. **But `cvt10` has no free `[59,1,2]` arm** (`NO-FREE-SPLIT-CONTROL`), so `ISOSPLIT`'s non-stall cannot be separated from the `[59,1,2]` partition rescuing on its own; and this is the **narrowest margin of the cycle**, 1.9233 pp = **3.46 SE** inside its 5 pp bar, branch `SPLIT-NO-EFFECT` / `ISOSPLIT-AT-ISO`. **One arm, no control, narrowest margin — write INDICATED, never "provided".** O-9 is the measurement that would settle it. | same | 270 |

### 3.3 The weight-decay precondition, at three grains

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

### 3.3b The fourth grain — the three carriers ALONE, on ResNet (`cwd3`, CORRECTIONS 278)

`ResNet18_c100` at `ciso1`'s cell, seeds {140, 141, 142}, **every arm SCALAR**, one `DECAY_MASK` name list per arm.
`SE_ARM_DIFF` **0.529182** here; every contrast is **within batch**. Anchors reproduce: `k01` **22.9853** against
`cwd1`'s 22.9513, `NWD` **70.7227** against `cwd1`'s `k01NWD` 70.7760 (Δ 0.0533 pp, inside `MATCH`).

| # | question | intervention | arms | effect | artefact | CORR |
|---|---|---|---|---|---|---|
| **E19** | does the **carriers' own** decay carry the precondition? | `DECAY_MASK` on {50, 53, 59} — **1,536 of 11,220,132 parameters**, update **and** meta trace | `CARWD0` **70.2640** vs `k01` **22.9853** | `P_CAR` **+47.2787 pp = +89.34 SE**; `CARWD0` is `REC`, **+4.5413 pp inside** `NWD`'s recovery band | `results/cwd3_carrierwd_score_alice2.txt` | 278 |
| **E20** | is it **specific** to them? | vs `cdep1`'s count-, numel-, width- and depth-matched triple {47, 48, 56}, and vs its class-pure pair {47, 56} | `CTLWD0` **23.0013**, `CTL2WD0` **22.9333** | `P_SPEC` **+47.2627 pp = +89.31 SE**; **both controls are FLOOR BOUNDS** — `P_CTL` +0.0160 pp (+0.03 SE), `P_CTL2` −0.0520 pp (−0.10 SE), i.e. `\|effect\|` below the 2.0 pp `NULL` bar and below **1.0744 / 1.1104 pp** at ±2 SE. **Ratio 42.6 : 1 at the 2-SE bound, 23.6 : 1 at the `NULL` bar.** **Specific against what, exactly: two DEPTH-matched sets whose members rank 33rd, 36th and 62nd of 62 by term magnitude — not against a magnitude-matched set, which cannot exist here (E23).** | same | 278 |
| **E21** | how much do the other **17** scales add? | `NWD` (all 20 scales) vs `CARWD0` | `NWD` **70.7227** | `P_SET` **+0.4587 pp = +0.87 SE — A BOUND, NOT A MEASUREMENT**: ≤ +1.5171 pp at 2 SE, inside `MATCH` 5.0. **Its SIGN is horizon-dependent** (T18) | same | 278 |

**The right reading of `F_CAR` = 0.9904**: it is **DESCRIPTIVE**, a ratio of two in-batch differences, and it **drifts
through 1** across the horizon — 1.0202 (epochs 55–59), 1.0111 (65–69), 1.0035 (75–79), 0.9979 (85–89), 0.9904
(95–99). For most of training `CARWD0` sat **above** `NWD` and the ratio **exceeded 1**. **A "fraction carried" that can
exceed 1 is not a decomposition**, and writing "the carriers carry 99 % of the effect" would repeat O4 at a new grain.
The honest form is E21's bound. `D_SHIFT` = `CTLWD0` − `CTL2WD0` = **+0.0680 pp** is a difference **between two floor
readings** and is therefore **doubly a bound** — it is not "the BN shift's share".

**Gates, stated because the dangerous null here is a mask that never bit** (275.4's null (i), which would have forged
exactly the opposite verdict): `G-BITE` PASSES on **all 15 runs** — 500 probe records each, `dm_masked == k` with
k = 3 / 3 / 2 / 20, `dm_skipped == dm_n × k`, a **positive `dm_wdterm` on 6,000 of 6,000 masked records**, and **no
`dm_*` key on any of the 1,500 `k01` records**. The **cross-read** is the strongest of them: every run is read as its
own k **and as every other k in {0, 2, 3, 20}**, and all 15 pass their own while refusing all three others.

### 3.4 Necessity of the carrier's own applied step (PlainNet18_c100, `csv1`'s cell)

| # | statement | numbers | SE used | artefact | CORR |
|---|---|---|---|---|---|
| E12 | The gap to explain | `HEAD` **64.4293** vs `k01` **12.1180**, `D_HEAD` **+52.3113 pp = +94.05 SE** | 0.556196 (3 v 3) | `results/csv1_shadowvote_score_alice2.txt` | 272 |
| E13 | An applied step **above the clamp floor** is necessary for the full stall | `SHADOWLOW` **49.8790**, `P_APPLIED` **+37.7610 pp = +72.58 SE** | **0.520274 (4 v 3)** | same | 272 |
| E14 | The vote route alone costs a partial loss | `NAIVELOW` **65.2420**, `P_VOTE` **+15.3630 pp = +31.89 SE** (0.2937 of `D_HEAD`); `NAIVELOW` is `AT-HEAD` | **0.481680 (4 v 4)** | same | 272 |
| E15 | Muting 50's vote with its applied step free changes nothing | `MUTE` **11.3027**, `P_MUTE` **−0.8153 pp = −1.47 SE**, inside `NULL` — a **LOCATION** | 0.556196 (3 v 3) | same | 272 |

**Licence wording, corrected at source.** The registered `BOTH-ROUTES` licence says "a **LARGE** applied step". Only ONE
small dose was run — the clamp floor `float32(exp(float32(−15)))` = 3.059e-07, from init. The correct sentence is
**"above the clamp floor"**. This is a RULE 16 defect **reported and not fixed** (272.6 F1); the scorer was not edited.

### 3.5 The second meta step size (ResNet18_c100, ms 3e-4, frozen successor `cST2`)

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E16 | The isolation rescue **transfers** | `k01` 28.5173, ISO 69.6740, CTL 28.6980; `D_ISO` **+41.1567 pp = +74.00 SE**, `D_CTL` **+0.1807 pp**, `P` = ISO − CTL **+40.9760**. **Same disclosure as E4**: `cst2`'s `CTL` **is** `cdep1`'s DEPTH triple, so it too contains the BatchNorm shift idx 48 — `cst2`'s own FINAL stamps `CTL-HAS-A-BIAS-MEMBER`, and `CTL` 28.6980 is a **floor location** against `k01` 28.5173, not a magnitude. There is **no class-pure control at this cell** (no `DEPTH2` arm at ms 3e-4). | `results/cst2_carriervote_score_alice2.txt` | 268 |
| E17 | The vote-dominance **nomination does not** | `DOM_C` **0.4727 = 709 of 1,500** records against a 750-record bar — **misses by 41**; `TOP3_C` **0.4960 = 744 of 1,500** — misses by **six**. Calibration at ms 1e-3: pooled `DOM_C` **0.8069** | same | 268 |

So at ms 3e-4 the campaign may write *the rescue transfers, the nomination is only partial there, and the two are not
locked together at this cell*. It may **not** write *the same three carriers are nominated at a second meta step size*.

### 3.6 What was exonerated

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| E18 | **Momentum 0.99 is not required.** At SGDm momentum 0.9 the collapse persists and the isolation still rescues | `M9k01` **24.5833** vs `M9kL` **69.3913**, `G_M9` **+44.8080 pp = +80.56 SE**, ratio 0.3543 (anchor 0.3300); `M9ISO` **70.9047**. **DESCRIPTIVE, relabelled at 279**: the "+1.5133 pp above `M9kL`" the 277 draft quoted is a **derived difference of two arm means, not a registered contrast**, and it is hardware-mismatched on one of three seed pairs (`M9ISO` L/L/L against `M9kL` T/L/L) — see T8 | `results/cmo1_momwd_score_alice2.txt` | 264 |

Bound on E18: **no CTL arm exists at either new configuration** (`NO-CTL-AT-NEW-CONFIGS`), so `ISO-RESCUES` at momentum
0.9 is a **rescue** word and not a **specificity** word.

### 3.7 The adverse rows — the evidence §1 leads with, in the same table format

| # | statement | numbers | artefact | CORR |
|---|---|---|---|---|
| **E22** | **A NON-carrier given a carrier-sized vote largely re-collapses a rescued run.** PlainNet18_c100, `cpl2`'s cell. | `INJECT` (HEAD's grouping, idx 47 `layer4.1.bn1.weight` × 691 in the complement) **30.1400** against `HEAD` **64.7940** and `k01` **11.9493**; **`P_INJECT` +34.6540 pp = +61.12 SE**, **`D_INJ` +18.1907 pp = +32.08 SE** on `cvt1`'s own SE **0.567010**; complement pins at **epoch 37.6 / 37.6 / 37.6** against `k01`'s 36.4 / 36.6 / 36.2 and HEAD's 99.8. Branch `STEP-SIZE-NEEDED-VOTE-SUFFICES`, stamp `INJECT-PARTIAL`. **Bounds: PARTIAL (0.3442 of the HEAD gap kept, 0.14 pp above the registered 8–30 band); timing not separated from identity (UNSURE); one fixed K = 691; one dose; PlainNet only; 100 epochs.** | **Levels and contrasts RE-DERIVED BY ME from the 15 raw `.out` in `alice-backup/runs_alice2/` (no `cvt1` scorer output is committed under `results/`); branch, stamps, pin epochs and bounds from CORRECTIONS 230.2 / 230.3 / 230.4(1) / 230.6** | 230 |
| **E23** | **The count-matched control is DEPTH-matched and cannot be MAGNITUDE-matched, by the batch's own binding declaration.** | Σ mean \|L\| on pinned records: **ISO 8.1665e-01** vs **DEPTH 2.6482e-03**, **ratio 308.4**, annotated in the artefact as *"the magnitude match this design CANNOT make"*. Per-tensor ranks of 62: carriers **1 / 2 / 3**; controls **33 / 36 / 62**. The SCOPE paragraph, *"BINDING ON EVERY SENTENCE"*, says the design *"does NOT separate tensor identity from term magnitude"*. 188.3: the best admissible carrier-free triple is still **×225** short, and no choice of members closes it. | `results/SCORE-cdep1.txt` `[P]` block + SCOPE paragraph | 188, 193 |
| **E24** | **The same limit is stamped across the campaign, on four networks.** | `MAGNITUDE-NOT-SEPARATED` on `cmg1`'s, `cgn2`'s and `cgn3`'s FINALs; `cwd3`'s NOT-LICENSED block (*"×225 any admissible control's"*); `cwd3`'s FINAL `CTL-DEPTH-MATCHED-NOT-MAGNITUDE`. CORRECTIONS 226.7: *"On all four networks now examined, the carriers are the top DOWN-voting terms by a factor no carrier-free matched set can close (×225 ResNet-BN, VGG `bn8` 0.58 share, ×3.1–×14 GN, ×691 PlainNet). The confound is not a design gap in any one batch; it is what these trajectories look like."* | the four FINAL lines; CORRECTIONS 226.7 | 225, 226, 231, 266, 278 |

---

## 4. The mechanism as far as the evidence goes — and what is NOT shown

### 4.1 What the evidence supports

A **conjunction of one-cell results**, and nothing stronger:

1. At the ResNet mechanism cell the shared Lion vote is **dominated by the three largest terms**, which at that cell
   are three last-block BatchNorm scales (E3: ranks 1/2/3 of 62, carrying set on 1239/1239 DISAGREE records), and the
   rescue is **specific** to them against a count-matched, same-layer, same-numel, **DEPTH-matched** control (E4). The
   specificity is an **asymmetry between a measured rescue and a bounded floor** — ISO `+46.6920 pp` against
   `D_DEPTH ≤ 5.0 pp` — not a measured difference between two magnitudes; the control triple contains one BatchNorm
   **shift** (idx 48), with the class-pure pair `DEPTH2` giving the same bound. **And the control is not and cannot be
   magnitude-matched (E23), so "specific to these tensors" is not separated from "specific to the large terms".**
2. A step at PlainNet's measured dose **on** those tensors is **sufficient** to stall — one at a time on ResNet, each
   held alone in its own group while the other 61 share one step size (E6). Whether that also requires the other two to
   remain in the shared vote is **INDICATED only** (E7): one arm, no free-split control, the cycle's narrowest margin.
3. On PlainNet, both the applied step and the vote carry part of the damage (E13, E14) — **and the vote route is
   magnitude-operative rather than identity-operative as far as it has been probed**: muting the carrier's own term
   does not rescue (E15), while injecting a carrier-sized term from a non-carrier largely re-collapses (E22).
4. **Coupled weight decay on normalisation scales is a precondition** of the whole phenomenon, at **four** grains and on
   two networks (E8–E10, **E19**), and the held-step damage runs through the same factor on PlainNet (E11). **At the
   ResNet cell the precondition is carried by the three carriers' own decay** (E19), and that is **specific** against
   both matched non-carrier sets (E20) — again as an **asymmetry between a measured rescue and two bounded floors**, and
   again without separating identity from term magnitude, position class or count/dose (§0 items 11 and 12).
   **The residual left to the other seventeen scales is a BOUND, not a measurement, and its sign is horizon-dependent**
   (E21, §0 item 10).

### 4.2 What is NOT shown — stated in the same breath

* **The route is not identified.** `cmo1`'s flag, `cwd1`'s mask, `cwd2`'s `k01WD0` and `cwd3`'s name-list mask each
  change the **weight update and the meta trace `h ← γ(1 − wd·a)h − δ` together** (`MASK-UPDATE-AND-TRACE`,
  `K01WD0-BOTH-ROUTES-CHANGED`). Only `cwd2`'s three **held** arms are clean on this, because there every applied step
  is exogenous — and that is PlainNet, one tensor.
* **Tensor identity is not shown at all, and is forbidden by registration.** See §0 item 12, §1 A2–A4, E23, E24, T21.
  What is shown is a localisation whose selector — term magnitude, position class, count/dose, or literal identity —
  is not resolved. **Three of those four rivals have a named, costed experiment; none has been run.**
* **The natural story is unsupported where it can be looked at, and unmeasured where it matters.** The story — decay
  shrinks a BN scale, the shrinking scale's gradient grows, it dominates the shared vote, the shared step size runs
  away — is **UNSURE**. In every arm where `PATCH_DECAYMASK` records ‖w‖ the decay is **off** and the scales **grow**
  (`cwd1` `kLNWD` carriers 22.6 → 38.3 / 30.0 / 48.9; `cwd1` `k01NWD` 22.6 → 22.9 / 22.7 / 22.9; `cwd2` `k01WD0` idx 50
  22.63 → 23.31; `cwd3` `CARWD0` 22.6 → 22.8 / 22.7 / 22.9), **no masked run shows anything like a filter collapse**,
  and `dm_small` — the count of entries with |w| < 1e-3 — is **0 on every record of every genuine masked scale**,
  7,500 of 7,500 across `cwd1` and `cwd2` (274.1, 274.3).
  **The min-|w| figures, corrected again here (CORRECTIONS 279, N8), because the 277 correction was itself too loose.**
  The 276 draft wrote *"min |w| never leaves [0.9994, 1.020] on any masked run"*; 277 corrected that to `cwd2`'s
  interval plus `cwd1`'s **0.983** (`k01NWD`) and **0.503** (`kLNWD`) at record 499. **Those two `cwd1` figures are
  SEED MEANS, not minima** — the scorer's own DESCRIPTIVE header says *"seed means"* — and the per-seed last records in
  the same file's `G-BITE` lines are `kLNWD` **0.502388 / 0.469448 / 0.538347** (mean 0.503394) and `k01NWD`
  **0.981039 / 0.984450 / 0.983544** (mean 0.983011). **So one `dm_absmin` reading, 0.4694, sits BELOW the 0.503 the
  277 draft quoted as a bound.** The honest statement is: *over `cwd1`'s masked arms the smallest per-seed final-record
  `dm_absmin` is **0.4694**; over `cwd2`'s single masked tensor the re-measured masked minimum is **0.99941** (274.3).*
  **The conclusion is unchanged** — 0.4694 is more than two orders of magnitude above the 1e-3 threshold and
  `dm_small` is 0 on every record that carries it — but the bound as stated was wrong twice, and these are last-record
  readings at records 0 / 50 / 200 / 499, **not minima over the whole run**, which the artefact does not print.
  *(Separately: `CTLWD0`'s `dm_small` is **512** and its `dm_absmin` **8.76e-15** — that is the BatchNorm **shift**
  idx 48, whose norm is 1.3e-10 at record 0. It is not a filter collapse; it is a tensor that starts at zero, and it is
  the whole of T19b.)*
* **The collapsing arms carry no measurement at all.** `dm_*` is present only on masked arms: `cwd1` 3,000 of 4,500
  records, `cwd2` 4,500 of 7,500, `cwd3` 6,000 of 7,500. The 4,500 `cwd2` records with no readout are exactly the three
  seeds of the two **stalling** arms, `k01` and `HIGHHEADPATH`; `cwd1`'s 1,500 and `cwd3`'s 1,500 are `k01`'s
  (274.1 per-arm table; 278.5). **The arms where the collapse happens are precisely the arms with zero
  instrumentation.**
* Consequently **Zhou et al.'s filter-collapse candidate (arXiv:2001.11216) is neither confirmed nor excluded**, and
  Lobacheva et al.'s BN×WD destabilisation (arXiv:2106.15739) is consistent with the direction but **untested here**.
* **Decoupled weight decay is untested** at every cell; every result above is about **coupled** L2.
* **`cwd1` has no ISO arm**, so what the carrier isolation does *under* the mask is unknown; and `cwd1`'s reference arm
  is itself masked (`NO-WD-ON-REFERENCE-ARM`), so "the scalar arm reaches the layerwise level" is a statement about a
  **masked** layerwise arm. **`cwd3` has no layerwise arm at all.**

**One sentence for the section, and it is the honest one: naming the precondition is a SCOPE result, and localising the
vote by term magnitude is a bounded second result; neither is a mechanism.**

---

## 5. Relation to prior work

Only papers whose arXiv id was re-checked for this file are used. Each id was resolved on its arXiv **abstract page**
(HTML) and the title and author list match what is cited. **No PDF was fetched, nothing was downloaded, no licence was
accepted.** Nothing is added that is not already verified in `docs/PRIOR-ART.md` (2026-09-17 section) or in
CORRECTIONS 258.1 / 260.1 / 262.1 / 277.5.

| paper | id | what it already establishes | what remains ours |
|---|---|---|---|
| He, Zhang, Zhang, Zhang, Xie, Li — *Bag of Tricks for Image Classification with CNNs* | arXiv:1812.01187 | "no bias decay": weight decay on conv/FC weights only, BN γ/β left unregularised — **standard practice** | That this practice is **load-bearing for a meta-learned step size** (E8–E10, E19). He et al. motivate it by overfitting, not by optimiser failure. **This is the near-trivial half of our claim and §2 says so.** |
| Lobacheva, Kodryan, Chirkova, Malinin, Vetrov — *On the Periodic Behavior of NN Training with BN and Weight Decay* | arXiv:2106.15739 | BN **together with** WD produces repeated destabilisations and a periodic training regime | **The nearest published prior that the pathology NEEDS WD, and the reason our `COLLAPSE-VANISHES` is not surprising.** Theirs is about **scale-invariant** weights in a BN net; ours is WD applied to **γ itself**, which is scale-**variant**, and theirs says nothing about a meta-learned step size. It is also the live alternative explanation for our rescue decaying over 250–430 epochs, and **we have not tested it.** |
| Arora, Li, Lyu — *Theoretical Analysis of Auto Rate-Tuning by BN* | arXiv:1812.03981 | scale-invariant weights converge at any LR; only **scale-variant** parameters (γ, β, last layer) need a tuned LR | **Which** scale-variant tensors, and **how few**: three of 62 (0.014 % of parameters), **nominated by per-tensor attribution of a shared meta-update's vote**, with a **count-matched, layer-matched, DEPTH-matched non-carrier control whose result is a bounded floor** (E4 — *not* "same-class", and *not* "does not rescue"). Arora–Li–Lyu predict the class; they do not predict a three-tensor set, a last-block position, or a rescue/control asymmetry. **This is the expected referee line ("of course the γ's") and E4 is its answer — but E23 bounds that answer: our control is depth-matched, never magnitude-matched.** |
| Davis, Frank — *Revisiting Batch Norm Initialization* | arXiv:2110.13989 | γ init ≈ 0.1 and **γ learning rate ÷ 100** give significant gains — so "give γ its own smaller LR" is **already known as a practice** | Nothing in the ISO result may be sold as "γ wants its own LR". What is ours is the **vote-attribution evidence**, the **matched-control asymmetry** and the **step/vote dissociation** (E13–E15, E22) — the mechanism evidence, not the remedy. |
| Zhou, Wang, Luo, Feng, Li, Zhang — *How Does BN Increase Collapsed NN Filters?* | arXiv:2001.11216 | BN+ReLU filter collapse; sparsifying probability ∝ lr² and ∝ 1/γ²; worse at large or adaptive LR, **without any sparsity-inducing regulariser** | The **candidate mechanism we could not test**. Where our readout exists there is no collapse: `dm_small` 0 on every record that carries it; min \|w\| ≥ **0.99941** over `cwd2`'s single masked tensor and the smallest per-seed final-record reading over `cwd1`'s 20 masked scales is **0.4694** — *the 276 draft quoted `cwd2`'s figure as if it covered both, and the 277 correction quoted a SEED MEAN (0.503) as a minimum; see §4.2 and T17.* The readout exists only where the decay is off. **Neither confirmed nor excluded** — the single strongest reason the section must not be sold as a mechanism. |
| Kim, Choi, Jang, Lee, Jeong, Kim — *Guidelines for the Regularization of Gammas in BN for Deep Residual Networks* | arXiv:2205.07260 (ACM TIST 15(3) 2024, DOI 10.1145/3643860) | γ's admissibility for **L2** depends on its **position** in the residual block (last-in-branch vs projection shortcut) | The only paper that treats our carrier categories as different categories — **for L2, not for step size, and never one tensor at a time.** **And it is a CONFOUND for us before it is a contribution**: at that depth three of the five 512-wide BN scales are the carriers, so `CARWD0` vs `CTL2WD0` is {γ_last, γ_down} vs {γ_others} and this batch cannot tell "these tensors" from "this position class" (T19a). **What `cvt10` does NOT give is a position law**: all three singletons read `-STALLS` and the registered `KIM-CATEGORY-SPLIT` token **did not fire** (270.6 F3); the 53-vs-{50,59} difference lives only in the FREE rescue levels (**57.5033** against 64.7967 / 67.7053) and in `L_LAST_DOWN` **+9.9213 pp**, **both DESCRIPTIVE**, and neither is a position law from one tensor per category. |
| Mueller, Vlaar, Rolnick, Hein — *Normalization Layers Are All That SAM Needs* | arXiv:2306.04226 | Perturbing **only the affine normalisation parameters** — *"typically comprising 0.1% of the total parameters"* — in SAM's adversarial step can **outperform** perturbing all of them, across SAM variants and across **ResNet (BatchNorm) and ViT (LayerNorm)**; other sparse-perturbation schemes do not match it at that sparsity | **The closest prior art to our *fraction* sentence.** "0.014 % of parameters" is **not** ours to sell as surprising. Still ours: a **per-tensor step-size group in a meta-learned optimiser**, not an adversarial perturbation; a subset **nominated by attribution of a shared meta-update's vote**, not chosen a priori as a class; **three named tensors, not the class**; and a **count-matched, layer-matched non-carrier control** whose result is a bounded floor (E4). Their ViT/LayerNorm coverage is the sharpest form of T13 — **they cross BatchNorm and LayerNorm; we have crossed BatchNorm and GroupNorm and not LayerNorm.** |
| De, Smith — *BN Biases Residual Blocks Towards the Identity Function in Deep Networks* | arXiv:2002.10444 | BN downscales the residual branch relative to the skip by ≈√depth; BN nets train at larger learning rates | Makes a last-in-branch γ a **plausible single lever** a priori, which is why our result is not a surprise in direction. Nothing there varies **one tensor's** learning rate. |

**Not claimed as new.** That γ benefits from its own smaller LR (Davis & Frank); that scale-variant tensors are where
LR sensitivity lives (Arora–Li–Lyu); that large LR on BN parameters can damage a net (Zhou et al.); **that BN + WD
destabilises training (Lobacheva et al.) — which is most of our precondition half**; that excluding BN from weight
decay is standard (He et al.); **and that a ≈0.1 %-of-parameters normalisation subset can carry a whole training
effect, on BN and LN nets alike (Mueller et al.) — so the *fraction* in "three of 62 tensors, 0.014 % of parameters" is
not itself the contribution.**

**What the campaign claims, in three clauses, all bounded to the cells in §3.** (a) A meta-learned **shared** step size
whose Lion meta-update vote is shown, by per-tensor attribution, to be **carried by the tensors holding the largest
terms**, which at these cells are a few identified last-block normalisation scales. (b) **A carrier-specific rescue and
a carrier-specific decay-removal that two matched non-carrier sets do not reproduce** — an asymmetry between a measured
rescue and bounded floors, with the controls matched on count, numel, width, depth and layer but **never on term
magnitude**. (c) Hold, mute, inject and mask interventions dissociating **dose**, **vote route** and **weight-decay
route** — including the one that **cuts against us** (E22). The prior-art sweeps recorded at 254, 258.1, 260.1 and
262.1 found **zero** arXiv hits pairing hypergradient / meta-learned step size with normalisation or with per-layer
dominance, against a control query (`hypergradient`) returning 127 — the zero counts are real, not a broken search
(262.1).

---

## 6. Threats and limits

In the campaign's register: what a reviewer will say, and what the honest answer is.

| # | threat | answer, or concession |
|---|---|---|
| T1 | "This is a configuration pathology, not a finding." | **Largely conceded, and it must be written that way.** `LIMITS-PREP` §6 named this as the single biggest weakness and its own conditional has fired on the weight-decay branch. Momentum 0.99 is exonerated (E18); coupled WD on the norm scales is not — it is a **precondition** (E8–E11, E19). The correct statement of the ceiling is **"we did not meet the collapse at any cell tested with the decay off"**, never "a reader will not meet it". |
| T2 | "You never removed the decay from the carriers alone on ResNet." | **ANSWERED at CORRECTIONS 278** — this row previously read *"conceded, unreservedly … this is the gap"*. `cwd3`: `DECAY_MASK` on {50, 53, 59} alone, 15 runs, every arm SCALAR. `P_CAR` **+47.2787 pp = +89.34 SE**, `CARWD0` **inside** the 20-scale arm's recovery band (E19); `P_SPEC` **+47.2627 pp** against both matched controls, each a **bounded floor** (E20). **Honest scope: ONE cell, ONE network, ONE horizon, ONE WD value, three seeds, no layerwise arm, and the mask still changes weight update and meta trace together.** **Closing this gap opened T18 and T19, which must be quoted whenever this row is.** |
| T3 | "The mechanism is not measured." | **Conceded.** §4.2. The instrument records ‖w‖ only where the decay is off; the collapsing arms carry nothing. A mechanism needs a **new instrument**, not more cells. |
| T4 | "Your necessity results are on a modified algorithm." | **Partly conceded.** `csv1`'s shadow vote is counterfactual (`SHADOW-IS-COUNTERFACTUAL`); `cwd2`'s held arms are open-loop with the complement forced onto a replay (`COMPLEMENT-ON-HEADPATH`); **`cvt1`'s MUTE / DOSE / INJECT re-weight a term inside the shared meta-gradient sum** (`PATCH_VOTEWEIGHT`, proved inert off and at identity over 300 real GPU steps, 227). The necessity statements that do **not** modify the meta-update are the weight-decay ones: `cmo1` W0 is a plain CLI flag on the unpatched harness (`LIVE-HARNESS`); `cwd1` / `cwd2` / `cwd3` use `PATCH_DECAYMASK`, which changes **which tensors are decayed** — a training-configuration change — and leaves the meta-update closed-loop. |
| T5 | "One dataset family, one network per axis, one horizon." | **Conceded.** CIFAR-100 (plus one CIFAR-10 association cell, `cct1`, where nothing collapses and dominance is present but never decisive); `ResNet18` or `PlainNet18` per axis in §3; 100 epochs everywhere in this cycle, while the rescue is known to decay by 250–430 epochs elsewhere in the corpus. |
| T6 | "Three seeds." | **Conceded as a design fact, mitigated by margin.** Every deciding contrast in §3 clears its bar by 30–100 SE. **The SE is NOT one number — see §3's table; the 276 and 277 drafts each got this wrong.** `cmo1`, `cwd1`, `cwd2`, `cvt10`, `cst2` use the frozen prior 0.681198 → 0.556196 (their in-batch sigmas run 0.390–0.463, so the prior is the conservative choice). **`cvt1` uses a different frozen prior, 0.694443 → 0.567010. `csv1` prints THREE SEs — 0.556196, 0.481680, 0.520274 — and its rows use all three. `cmg1` uses 0.481680. `cdep1` uses its own 0.755682, from a corpus reader that excludes `cdep1-*` rows. `cwd3` uses 0.529182 from the re-derived prior 0.648113. `cuc1` (E0) uses 0.4674.** The exceptions to the 30–100 SE range are named: `P_SPLIT` (1.9233 pp = 3.46 SE inside its bar, E7) and `cmg1`'s `D_CAR` (+4.1150 pp, 0.885 pp = **1.84 SE on 0.481680** inside a 5 pp margin — §1 A3, not used in §2). |
| T7 | "Some arms sit **below** the scalar anchor, so 'stalls to the scalar level' is wrong." | **Conceded and already stamped.** `FLOOR-READINGS-ARE-BOUNDS` (164.6) is on the FINAL of **seven** of the batches this file cites — `cmo1`, `cst2`, `csv1`, `cvt10`, `cwd2`, **`cwd3`** (six, grepped over the committed `results/*_score_alice2.txt`) and **`cvt1`** (whose FINAL is recorded verbatim at CORRECTIONS 230.2, because no `cvt1` scorer output is committed under `results/`). *(The same stamp is on `cvt6`'s and `cvt9`'s FINALs, batches this file does not cite, and appears in `cvt5`'s body but not on its FINAL — stated so the grep is reproducible.)* It is **not** on `cwd1`, `cmg1` or `cdep1`. `HOLDBIG3-BELOW-K01` and `MUTE-BELOW-HEAD` are explicit. **`cdep1` belongs on the list too**, under `DEPTH-FLOOR-SATURATED` / `DEPTH2-FLOOR-SATURATED`, with 164.6 cited in the scorer's own words: DEPTH 23.5207 and DEPTH2 23.4480 are **inside** [21.0940, 27.9520], so the entitled statements are `D_DEPTH ≤ 5.0 pp` and `D_DEPTH2 ≤ 5.0 pp` and nothing finer. Every such reading is a **location**, never a point estimate. |
| T8 | "Hardware was not controlled." | **Disclosed, not defended — and stated PER BATCH, which the 277 draft did not do.** `cmo1`: **two** classes, 10 × RTX 2080 Ti (node858/859) and 17 × L4 (node882/883/887); the deciding contrasts `G_M9`, `G_W0` and the anchor `G_A` are hardware-**matched** seed for seed, mean L4 − 2080 Ti **+0.2392 pp** (inside the 0.681198 floor) — **but `DI_M9` = `M9ISO` − ISO is FULLY confounded and is labelled `HARDWARE-CONFOUNDED / UNSURE` at 264.4(4)**, and E18's derived `M9ISO` − `M9kL` is mismatched on one of three seed pairs. `cwd1`: **two** classes, 7 × L4, 2 × 2080 Ti; `P_NWD` mismatched on s129, per-seed spread 1.244 pp against the 47.8 pp it reads. `cwd2`: **three** classes, 8 × A100-80GB-MIG, 4 × L4, 3 × 2080 Ti; arm-centred device estimate **A100 +0.0460, L4 −0.0375, 2080 Ti −0.0727 pp**, two to three orders below the 54.9 pp the verdict turns on, branch string unchanged under every leave-one-seed-out and ±2 pp per device class. **Seed is confounded with device and cannot be separated.** **`cwd3` is the exception and the fix**: `--constraint=L4` pinned at the launcher, **15/15 name `NVIDIA L4`**, stamp `HW-UNIFORM-NVIDIA_L4`. `cvt10`, `csv1` and `cvt1` have **no** such census yet (§7 O-3). |
| T9 | "Your noise floor moved under you." | **Disclosed, and it moved twice.** The `--check` demonstration floor moved with the 273 ingest (`SIGMA_R18ALL` 0.663166 df 239 → 0.648113 df 255; `SIGMA_PLAIN` 0.459529 → 0.460632) **and again with the `cwd3` ingest at 278.9: `SIGMA_R18ALL` 0.648113 df 255 → 0.645141 df 258; `SIGMA_PLAIN` 0.460632 UNCHANGED.** **No bar reads that line** — every bar in §3 is a frozen literal set at registration, and `cwd3`'s own bars use the 0.6481128684085689 frozen at 275 — **but any future scorer re-deriving a floor from the corpus now gets 0.645141 and must quote it.** |
| T10 | "How many RULE 16 defects are open?" | **EIGHT, and the campaign's own text has been miscounting them.** Reported, none fixed, none hidden: **270.6 F1; 271.6 F1 and F2; 272.6 F1 and F2; 273.6 F1 and F2** — that is **seven**, and each of those entries' own headers says so ("the … defect report", "the two … defect reports" ×3) — **plus 278.6 D1**, the `cwd3` scorer's upper-middle `median` in a DESCRIPTIVE readout. **277.6 and 278.6 both call the first group "six", which is a miscount of their own enumeration; it is named here rather than repeated.** Exactly one of the eight touches a **licence sentence** — `cSV1`'s word "large" — and §3.4 states the corrected sentence in its place. None of the eight touches a bar, level, contrast, state, branch or stamp. |
| T11 | "The parent reports scalar (SGDm, Lion) working on ImageNet." | **Open, and it is the sharpest external counterweight.** Our IN-489 scalar sits at 1.00. The obvious untested confounder was momentum 0.99 — now exonerated (E18) — which makes coupled WD the live candidate, but we have run nothing on ImageNet and cannot. Parent §7.3 also reports blockwise no better than scalar there. |
| T12 | "Your only control is a bounded floor, and it has a BatchNorm shift in it." | **Conceded, and disclosed in §2, E4, E16, E20 and T7 rather than left for a referee to find.** Two concessions: (a) the count-matched control's result is a **bound** (`D_DEPTH ≤ 5.0 pp`), not a magnitude — "recovers none of it" is struck; (b) the triple {47, 48, 56} contains **`layer4.0.bn1.bias`, a BatchNorm shift**, so it is count-, numel-, width-, depth- and layer-matched but **not class-pure**. The answer is in the same artefact: `DEPTH2` {47, 56} is class-pure, `D_DEPTH2` +0.0960 pp, `DELTA_BIAS` +0.0727 pp = +0.10 SE (`BIAS-NULL`). The conclusion does not rest on the shift member — **but it does not become a magnitude by being class-pure**, and it does not become magnitude-matched either (T21). `cst2`'s `CTL` is the same triple (`CTL-HAS-A-BIAS-MEMBER`) with **no** class-pure partner at its cell. |
| **T13** | **"Two architectures, both 18 layers, and one of them is your own variant."** | **REWRITTEN AT 279, because the 277 version was FALSE in three clauses.** What is true: **every result in §3 is on `ResNet18_c100` or `PlainNet18_c100`** — same depth, same width, same block count, differing only in whether the residual connection is there — and `cwd1`'s own NOT-LICENSED block says *"Anything about PlainNet / VGG / GroupNorm, other cells…"*. What was **wrong**: (a) **"no GroupNorm" is false.** `cgn1` (217) replicated the gap on `ResNet18_gn_c100` (D **+37.3833 pp = +63.08 SE**); `cgn2` (225) landed **`IDENTITY-TRANSFERS-GN`** — the same three tensors isolate and rescue (55.7147 from 14.0940), the matched {47,48,56} does not move it (14.1980), `DELTA_ID` **+41.5167 pp = +67.23 SE**; `cgn3` (231) took it to 430 epochs, **`RESCUE-SURVIVES`, `RHO` 1.2235**. **So the carrier result crosses one normaliser, and that strengthens the localisation claim — while both GN batches stamp `MAGNITUDE-NOT-SEPARATED` and `GN32-ALSO-CHANGES-PER-CHANNEL-INVARIANCE`.** (b) **"no non-residual family outside our own PlainNet" is false**: `cvi1` / `cvh1` carry isolation arms on **`VGG11_bn_c100`** (`RESCUE-SURVIVES`, ρ 1.0001 at 328 epochs, 219), where the carrier set is **one** tensor, `bn8.weight`. (c) **"nothing was run on ResNet34/50" is false as a statement about the campaign** — `ResNet34_c100` and ResNet34/50 CIFAR-10 cells are in the corpus (`LIMITS-PREP` §2.2) — **what is true is that no carrier or isolation arm exists on any of them.** What still binds: **LayerNorm untested**; no carrier arm above 18 layers; nothing outside convolutional image classifiers; Mueller et al. cross BN and LN, we cross BN and GN. |
| **T14** | **"Lion is the only meta-update rule you ever ran."** | **Conceded.** Every arm in §3 is SGDm(0.99, wd 0.1) **base** + **Lion meta** at meta step 1e-3 (E16/E17's second cell is the same pair at 3e-4). Lion's update is a **sign** function, so "the vote is carried by the large terms" is a statement about a **sign-aggregated** sum in which one large-\|L\| tensor can fix the sign of the whole — **which is exactly why the magnitude framing of §2 is the right one, and exactly why it may not be carried to Adam-meta or SGD-meta, where the aggregation is not a sign vote and `DOM_C` is not even defined the same way.** The campaign has Adam-meta runs elsewhere (they are what removes the weightwise collapse, MASTER-TABLE §2), so this is a real, untested axis. **No sentence in §2 may be written about "a meta-learned step size" in general.** |
| **T15** | **"The whole carrier set comes from one instrument, and that instrument is already unstable."** | **Conceded, and it is the weakest joint in the chain.** The three carriers are nominated **only** by `ctd1`'s per-tensor \|L\| attribution on the scalar arm (E3) — one statistic, one arm, one cell. There is **no second, independent nomination instrument anywhere in the campaign**: no ablation-based ranking, no gradient-norm ranking, no leave-one-out search. And the instrument is **already fragile off its cell**: at ms 3e-4 `DOM_C` is **0.4727** against a 0.50 bar (misses by 41 of 1,500) and `TOP3_C` **0.4960** (misses by **six**), against pooled **0.8069** at ms 1e-3 — E17, branch `NOMINATION-PARTIAL`. So the rescue transfers a decade of meta step size and the nomination does not. **A referee is entitled to say the carrier set is an artefact of one statistic at one meta step size, and the campaign cannot currently refute that.** |
| **T16** | **"How many contrasts did you look at before these?"** | **Conceded: no multiplicity control anywhere in this cycle, and none was ever registered.** Across `cmo1`, `cvt1`, `cvt10`, `cwd1`, `csv1`, `cwd2`, `cwd3`, `cdep1`, `cmg1` and `cst2` this write-up reads **25 numbered evidence rows (E0–E24)** — **the 277 draft still said "19 … (E0–E18)" after `cwd3` had added three more (N10)** — and the underlying scorers print several times that many contrasts (`cvt10` alone prints **18** under `CONTRASTS` plus a DESCRIPTIVE nineteenth; `cwd3` prints six plus two DESCRIPTIVE). Every bar is a **frozen literal fixed at registration** and every contrast is **within batch and pre-registered as PRIMARY / CO-PRIMARY / KEY / DESCRIPTIVE before the runs existed**, which is a better protection than a post-hoc correction. **But no family-wise or false-discovery correction is applied to anything.** The honest statement: the 30–100 SE contrasts are unaffected by any plausible correction, and the **two narrow ones — `P_SPLIT` at 3.46 SE inside its bar (E7) and `cmg1`'s `D_CAR` at 1.84 SE inside (A3) — are exactly the ones a multiplicity argument would attack, and neither is load-bearing in §2.** Descriptive readings (`L_LAST_DOWN`, `F_CAR`, `D_SHIFT`, the `dm_*` block, the class shares) carry **no** bar and are labelled DESCRIPTIVE. |
| **T17** | **"Your own draft had an evidence error in it."** | **Three of them, disclosed rather than quietly fixed — and the third is a correction to the correction.** (1) The 276 draft asserted *"min \|w\| never leaves [0.9994, 1.020] on any masked run"*; that interval is **`cwd2`'s single masked tensor only**. (2) 277 corrected it with `cwd1`'s **0.983** and **0.503** at record 499 — **but those are SEED MEANS, not minima**, and the per-seed last records are `kLNWD` **0.502388 / 0.469448 / 0.538347** and `k01NWD` **0.981039 / 0.984450 / 0.983544**, so **0.4694 sits below the bound 277 quoted** (§4.2, N8). (3) T7's floor-discipline list was short at 276 (three FINALs) and still short at 277 (five); grepped again here it is **seven**, plus `cdep1` under its own stamps. **The conclusion is unchanged at every stage** — `dm_small` is 0 on every record that carries it and 0.4694 is more than two orders above the 1e-3 threshold — but the bound as stated was wrong twice. **274.3's sentence should not be re-quoted; the per-seed figures should be.** |
| **T18** | **"Your residual is a snapshot of a curve that has not converged."** | **Conceded, and it is the sharpest thing the refute pass of 278 added.** `P_SET` = `NWD` − `CARWD0` is **+0.4587 pp = +0.87 SE** in the registered 95–99 window, but over successive 5-epoch TEST windows it runs **−0.9153** (55–59), −0.7447, −0.5173, −0.5507, −0.1640 (75–79), **+0.1573** (80–84), +0.0973, +0.3800, **+0.4587** (95–99): it **crosses zero near epoch 80 and is still moving at epoch 99**. `CARWD0` has plateaued (mean tail slope **+0.0040** pp/ep) while `NWD` is still climbing (**+0.0276** pp/ep) — over the 20-epoch tail that slope difference is **+0.4726 pp, the same size as `P_SET` itself**. **So `P_SET` is a snapshot of a still-moving difference under `HORIZON-100-ONLY`, and its SIGN must not be reported as a finding.** `F_CAR` drifts through 1 over the same windows (1.0202 → 0.9904). **`P_CAR`, `P_SPEC`, `P_CTL` and `P_CTL2` are stable across every 5-epoch window from 75 onward** (`P_CAR` 47.1580 / 47.2220 / 47.2787 at 75–79 / 85–89 / 95–99), **so the verdict and both `NULL` states are untouched** — this limits only the residual. There is also a **TRAIN / TEST asymmetry**: `P_SET` is +0.4587 on TEST against **+2.6833 on TRAIN**, DESCRIPTIVE and unexplained (278.7). |
| **T19** | **"Your carrier result could just be a count of scales at that depth, and you cannot tell."** | **Conceded, and it is TWO separate confounds, neither excluded.** *(a) Position class, registered at 275.1 before any `cwd3` run and re-derived from the architecture three ways there and once more here from `runs_alice2/cwd3-PARTITION-MANIFEST.txt`:* `ResNet18_c100` has exactly **five** 512-wide BN scales — **{47, 50, 53, 56, 59}** — and **three are the carriers**, so a class-pure, count-matched, depth-matched, **carrier-free triple does not exist** at that depth. In Kim et al.'s taxonomy (arXiv:2205.07260), `CARWD0` vs `CTL2WD0` is **{γ_last, γ_down} vs {γ_others}** at the same depth. *(b) Count / dose, which is NOT the same thing:* `CTLWD0`'s idx 48 is a BatchNorm **shift** whose ‖w‖ is **1.3e-10 at probe record 0** (`dm_small` **512**, seed-mean absmin **8.76e-15**, only 0.0066 by record 200), so coupled decay on it does essentially nothing and **`CTLWD0`'s effective intervention is two genuine scales, not three**. With (a), **no control in this batch — and none that could exist at that depth — is at once carrier-free, class-pure and count-matched at three**, so *"exempting ANY three genuine 512-wide `layer4` BN scales suffices, and two does not"* fits **every number in `cwd3` exactly as well** as the carrier account. **A two-carrier arm (e.g. {50, 53}) would separate them and was not run (O-12).** Note also that the `dm` readout matches the controls **per tensor** (‖w‖ ≈ 22.6 each) but **not in total**: decayed scale-mass stands at **3 : 2**. |
| **T20** | **"Your own vote-injection arm says a non-carrier can do a carrier's job, and you buried it."** | **CONCEDED, AND IT WAS BURIED — the 276 and 277 drafts did not contain `cvt1` at all** (N1). It is now §1 A1, §0 item 13, a clause of the §2 claim paragraph, and E22. What the arm says: a non-carrier's term at a carrier's magnitude re-pins the complement at epoch 37.6 and costs **+34.6540 pp = +61.12 SE**. **What it does not say** (230.4, 230.6, quoted not paraphrased): it is **PARTIAL** (0.3442 of the HEAD gap kept, 0.14 pp above the registered 8–30 band); **timing is not separated from identity** and is stamped UNSURE, because the ×691 vote only turns DOWN from ≈ epoch 18, so "a full collapse starting late" and "a weaker effect because it is not 50's" are not distinguished; **one fixed K = 691, one dose, one network, one cell, 100 epochs**; and the sentence *"a carrier-sized vote from another tensor re-collapses the complement as fully as 50's own"* is **explicitly not licensed**. **The honest reading is that it refutes the strong identity claim and supports, without establishing, the magnitude claim.** The arm that would settle it is a **dose ladder on the injected magnitude with an onset control**, which is `cvt2`'s territory (registered at 233, landed at **236** as `GRADED` + `TOP-ATTENUATED`) — **on PlainNet, and not read into this file**. |
| **T21** | **"Your controls are matched on everything except the thing that matters."** | **CONCEDED, and it is binding by the campaign's own registration, not by my judgement** (N2). `cdep1`'s scorer prints, under **"SCOPE, BINDING ON EVERY SENTENCE"**, that the design *"does NOT and CANNOT match them on DYNAMICAL MAGNITUDE"* and *"does NOT separate tensor identity from term magnitude"*; the gap is **Σ mean \|L\| 8.1665e-01 vs 2.6482e-03, ratio 308.4**, with the carriers at ranks **1/2/3 of 62** and the control members at **33 / 36 / 62**; 188.3 proves the best admissible carrier-free triple is still **×225** short and that **no choice of members closes it on this network**. `cmg1`, `cgn2` and `cgn3` stamp `MAGNITUDE-NOT-SEPARATED`; `cwd3` stamps `CTL-DEPTH-MATCHED-NOT-MAGNITUDE` and repeats the ×225 in its NOT-LICENSED block; 226.7 records the same pattern on **four** networks (×225 ResNet-BN, ×691 PlainNet, ×3.1–×14 GN, VGG `bn8` 0.58 share) and calls it *"not a design gap in any one batch; it is what these trajectories look like."* **This is why §2 claims a localisation by TERM MAGNITUDE and not by tensor identity, and why no set-matched control can ever settle it. Only a magnitude intervention can — which is what `cvt1` is (T20), and `cvt1` came out on the magnitude side.** |

---

## 7. Open questions, and what each costs

Ordered by value per GPU-hour. **Nothing here is registered and nothing is launched by this file.** Costs for O-6, O-7,
O-8 are 273.12's estimates; O-2, O-9, O-11, O-12 and O-13 are my own rough guesses at ≈0.8 GPU-h per 100-epoch run and
are **UNSURE**.

| id | question | cost | what an outcome would let the section say |
|---|---|---|---|
| **O-1** | ~~**The ResNet carrier-only decay mask**~~ — **CLOSED at CORRECTIONS 278.** `cwd3` ran it (15 runs, `ResNet18_c100` at `ciso1`'s cell, every arm SCALAR) and the first branch fired. `P_CAR` **+47.2787 pp = +89.34 SE**, `P_SPEC` **+47.2627 pp** against two controls both on `k01`'s floor (E19–E21). The **second** branch did **not** fire: the nomination set and the precondition set did not come apart. | **10.7111 GPU-h actual** (`sacct`; 10.60 by the runs' own `minutes` lines) against the ≈5–8 guessed and 275.3's ≈12.6 | **Done.** What it bought: §0 bound 3 and T2 closed. What it cost: **T18 and T19**. |
| **O-12** | **A TWO-carrier decay mask on ResNet** — `DECAY_MASK` on {50, 53} alone, in batch with `cwd3`'s `CARWD0` and `k01`. **The arm that separates the two accounts T19b cannot separate**: "these three tensors" against "any three genuine 512-wide `layer4` BN scales, and two are not enough". *(Added at 278.)* **Track 2 of this cycle is launching the batch that addresses this. Nothing is registered or launched by THIS file, and no result from it is quoted anywhere in it.** | ≈ 5 GPU-h (guess, **UNSURE**; `cwd3`'s measured 0.71 GPU-h per run) | **If two carriers also recover**: the count account survives and the identity claim must narrow to "normalisation scales of this width at this depth". **If two do NOT recover while three do**: the count account is refuted at this cell. **Either outcome is publishable and either removes T19b.** T19a, the position class, would still stand — **and so would T21, the magnitude confound, which this arm does not touch.** |
| **O-13** | **THE MAGNITUDE ARM, and it is the one T21 and T20 both point at.** An injection dose ladder on ResNet — `cvt1`'s `PATCH_VOTEWEIGHT` applied to a ResNet non-carrier at several K, with an **onset control** (a vote active from step 0) to separate timing from identity, against `cwd3`/`cdep1`'s own arms in batch. *(Added at 279.)* | ≈ 10–13 GPU-h (guess, **UNSURE**) | **The only item that can settle §2's central bound.** If a ResNet non-carrier at carrier magnitude collapses the run, the localisation is by **term magnitude** and the identity claim is retired for good — a cleaner, more general and more defensible result than the one the draft was trying to claim. If it does **not**, then identity survives a magnitude intervention on the network the claim is about, which is the strongest thing the campaign could say. **`cvt1` already did this on PlainNet with one K and no onset control; `cvt2` (233) ran a dose ladder there. Neither exists on ResNet.** |
| **O-2** | **A weight-norm readout on the arms where the decay is ON** — a read-only patch (`PATCH_WNORM`-style) so the collapsing arms carry ‖w‖, min \|w\| and a small-weight count. | new patch + inertness proof + ≈ 5 GPU-h | The only item that could turn the scope result into a **mechanism**, and the only way to rule Zhou et al. in or out. **A design question for the professor, not a queue item** (273.12). |
| **O-3** | **GPU-hardware census for `cvt10`, `csv1` and `cvt1`**, read from each run's own `NODE=` line, in the form 264.4(4) / 273.4 / 278.1 used. | **ZERO GPU** | Closes T8 for the three batches without one — including the batch carrying the cycle's narrowest margin and the batch carrying E22. **Owed** since 270.4(6) and 272.4(7). |
| **O-4** | **Keep `--constraint`, or record node/GPU in `PROVENANCE`, and add a `G-HW` disclosure** on every future batch, as `cwd3` did. | ZERO | Retires the whole T8 class. `cwd3` is the worked example; the change is at the **launcher**, never the scorer. |
| **O-5** | **Close 264.6 W1's fix-track debt** — the false "each run prints `Epoch 99` twice" sentence baked into `analysis/cmo1_attack_indep.py` and its committed output. | ZERO | Removes the last factual error in a committed artefact from this cycle. |
| **O-6** | **S4 — a CTL arm at momentum 0.9.** | ≈ 5 GPU-h | Turns `cmo1`'s M9 `ISO-RESCUES` from a **rescue** word into a **specificity** word. Only worth it if the professor wants the momentum leg strengthened. |
| **O-7** | **N2 — `csv1`'s shadow-vote design on ResNet18_c100.** | ≈ 13 GPU-h | Carrier-step necessity on the second network. **A refinement, not a new claim** — and O-13 buys more per hour. |
| **O-8** | **A dose ladder on idx 50's applied step** (three values between the clamp floor and the shared step). | ≈ 10 GPU-h | Licenses the word "large" that 272.6 F1 had to strike; turns a two-point contrast into a curve. |
| **O-9** | **A PAIR of carriers** on ResNet, and a free `[59,1,2]` control for `ISOSPLIT`. Never run. | ≈ 8 GPU-h | Would make E7's condition ("only while the others vote") a measured statement instead of a single uncontrolled arm. |
| **O-10** | **Why ResNet and PlainNet differ at all** (three carriers vs one tensor — 226.7 says the cardinality follows the **topology**, not the normaliser, and that is a description, not a test), and the **closed-loop route at `k01`'s own dose** (`cvt8`'s `ROUTE-PARTIAL`, HIGHISOPATH 58.19). | unscoped | Both still open after `cvt10`. Not recommended before the discussion. |
| **O-11** | **Any further widening of L1 by dataset or network** (Tiny-ImageNet T1, S5, S6). | 20–40 GPU-h | **NOT recommended** (273.12): it buys scope for a claim whose ceiling is set by the configuration, not by the scope. |

---

## 8. Questions for the professor

1. **Framing (the live one, and it has changed shape).** Momentum 0.9 does **not** remove the collapse; weight decay 0
   on the normalisation scales **does**, on both networks and down to a single tensor. **But the precondition half is
   close to prior art (Lobacheva et al., He et al.), and the half that is genuinely ours — the localisation — can only
   be defended as a localisation by TERM MAGNITUDE, not by tensor identity** (§0 item 12, T21, and the adverse arm at
   T20). Is the section still a **mechanism section**, stated as conditional on coupled weight decay — or is it a
   **note on a configuration pitfall plus a bounded localisation result**? *(This is `LIMITS-PREP` §7 Q2, now live and
   re-shaped.)*
2. **Is the magnitude arm worth buying?** **O-13** is the one experiment that can convert §2's central bound into a
   result either way, and either way the answer is publishable. It is ≈10–13 GPU-h. 273.12's standing recommendation is
   **CONSOLIDATE — write up now**; O-1 was the exception it allowed because it repaired an over-statement. **O-13 is the
   same kind of exception: it repairs a claim we are currently not entitled to make.** Does he want it, and does he
   want **O-2** (the readout on the unmasked arms) designed at all?
3. Is "sufficiency plus a **count-matched, depth-matched** control" (E4, E6) enough necessity for the claim he wants,
   given that no set-matched control can ever be magnitude-matched on this network (E23) — or does the necessity leg
   need `csv1`'s counterfactual construction repeated on ResNet (**O-7**) despite a reviewer naming it an algorithm
   intervention?
4. How should the parent's §7.3 ImageNet result (scalar SGDm+Lion works; blockwise no better than scalar) be positioned
   against our IN-489 scalar at 1.00, now that momentum 0.99 is exonerated and coupled WD is the live candidate (T11)?
5. The isolation rescue transfers to ms 3e-4 and to GroupNorm, but the vote-dominance nomination does **not** transfer
   to ms 3e-4 (E16, E17, T13). Is that dissociation worth reporting, or does it weaken the carrier story more than it
   is worth?
6. Does the Zhou et al. filter-collapse candidate need to be ruled in or out before the discussion, given that our
   instrument **cannot** do it (§4.2)?

**On "the two judgement calls the audit left open".** My 276 brief referred to two judgement calls left open by a final
audit whose report I could not locate in the repository (see the provenance note at §2.2). **UNSURE** that these are
the two it meant; on the record itself, the two that are genuinely open and genuinely require a human are **Q1
(framing, now with the magnitude reframing attached)** and **Q2 (consolidate vs continue, and whether to buy O-13)**.
Everything else above is either answered by the data or is a costed queue item.

---

## 9. Provenance and discipline

* Written against `master` **`97eb049`**; corpus `results/all_runs.csv` at `064dff6`, **3,268** rows / **3375.0**
  GPU-hours, `results/CORPUS-EXCLUSIONS.tsv` **183** rows (re-counted here: 3,269 lines including the header; 204 lines
  including 20 comments and the header). **[SUPERSEDED headers: `2ab824c` / 3,253 rows / 3364.4 GPU-h at 277;
  `84e4bcb` at 276; `064dff6` at 278.]**
* **Every number in §§3.0–3.7 was re-derived from the committed artefact named in its row before this rewrite was
  written**, together with the rows that were re-derived for the first time at 279: **E23** from
  `results/SCORE-cdep1.txt`, **E24** from four committed FINAL lines and CORRECTIONS 226.7, and **E22 / §1 A1 from the
  fifteen raw `cvt1` `.out` files themselves** — because **no `cvt1` scorer output is committed under `results/` at
  this HEAD**, which is the same provenance flag E0 carries and is stated in both places rather than glossed. The
  `cvt1` reader is a stdlib-only script of my own (scratchpad, not committed) importing no repo module and reading no
  CSV column: it takes `plateau5` as the mean TEST over `Epoch` lines 95–99 of each run's own `.out`, and it reports
  **15/15 with 100 `Epoch` lines, `RUN_DONE`, 0 tracebacks**, arm means `k01` 11.9493 / `HEAD` 64.7940 / `MUTE`
  10.9860 / `DOSE` 11.9487 / `INJECT` 30.1400, and `P_INJECT` +34.6540, `D_INJ` +18.1907, `P_VOTE` +53.8080,
  `D_HEAD` +52.8447 — **every one equal to CORRECTIONS 230.3's registered figures digit for digit.** `cvt1`'s RULE 20
  passed at full coverage 15/15 before its own scoring (230.1); this is a re-derivation of a landed, ingested batch,
  not a new scoring.
  **Two tensor-index maps were read directly from the batches' own committed manifests** —
  `runs_alice2/cwd2-PARTITION-MANIFEST.txt` (`PlainNet18_c100`, 53 tensors, 11,046,308 params) and
  `runs_alice2/cwd3-PARTITION-MANIFEST.txt` (`ResNet18_c100`, 62 tensors, 11,220,132 params) — which is how the
  PlainNet-idx-47 / ResNet-idx-56 correspondence in §1 A1 was established rather than assumed.
* **The `dm_absmin` per-seed figures in §4.2 and T17 were read from the `G-BITE` lines of
  `results/cwd1_normwd_score_alice2.txt`**, which print each run's last record, and compared against the DESCRIPTIVE
  block's seed means (0.503394 → "0.503"; 0.983011 → "0.983"). The arithmetic is in N8.
* Census figures (E2) are labelled as census and come from `LIMITS-PREP` §2.2, which reads `results/all_runs.csv`
  through `analysis/corpus_exclusions.filter_rows`, so intervened runs are never pooled with plain ones: at this
  HEAD `results/CORPUS-EXCLUSIONS.tsv` lists **183 rows over 15 batches** (204 lines = 183 + 20 comments + 1
  header, re-counted here), and `corpus_exclusions.py --check` exited 0 `VERDICT: PASS` on this tree at 278.9.
* **Nothing under `paper/` was read into this file, opened for writing, or touched.** This file lives in `docs/`.
* **RULE 16 held**: no registered scorer, launcher, patch, `analysis/argsline_guard.py`,
  `analysis/corpus_exclusions.py`, `results/*.csv` or `results/*.tsv` was edited. No bar was re-derived and no verdict
  re-scored. **Eight RULE 16 defects stand open and unfixed** (T10).
* **Eight arXiv ids** are cited — 1812.01187, 1812.03981, 2110.13989, 2001.11216, 2106.15739, 2205.07260, 2002.10444,
  2306.04226 — plus the parent, 2402.02342. **All nine were resolved on their arXiv ABSTRACT pages (HTML) at 276/277
  and the titles and author lists match what is cited; no id was added at 279 and none was re-fetched, so no network
  access of any kind was made by this rewrite.** **No PDF was fetched, nothing was downloaded, no dataset licence was
  accepted, no notebook site or Vercel URL was opened.** *(Standing disclosure from 277.5: the local arXiv MCP index
  could not resolve 2306.04226 nor 2106.15739 and is treated as broken; it was not relied on.)*
* **ZERO GPU. No `sbatch`, no `srun`, no job submitted or cancelled, no cluster command of any kind by this rewrite.
  `alice` — Saber's shared account — NOT contacted.**
* *(Carried from 278: one RULE 16 defect reported and NOT fixed — `analysis/cWD3_carrierwd_score.py`'s `dm` readout
  takes `sorted(v)[len(v)//2]`, the upper middle, so it prints "median 16" where the true median of that 20-vector is
  13.6569; **DESCRIPTIVE, non-gating, no bar, level, contrast, state, branch or stamp reads it**, 278.6 D1.)*
