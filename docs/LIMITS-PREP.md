# LIMITS-PREP — scoping the BatchNorm-carrier finding for the discussion with Dr Salehkaleybar

*Written 2026-09-17 (CORRECTIONS 254). Preparation notes, NOT paper text. Read-only work: nothing registered,
submitted or launched, zero GPU, no dataset or PDF downloaded, no licence accepted, `alice` not contacted, `paper/`
untouched. plateau5 is the only metric used. Cell means come from `results/all_runs.csv` after
`analysis/corpus_exclusions.filter_rows` (the 108 intervention runs are never pooled). Every citation below was
checked against an arXiv abstract page, ar5iv/arXiv HTML, an official proceedings page or the official repo; anything
that could not be checked is marked UNVERIFIED or left out.*

## 0. The finding being scoped (one paragraph)

MetaOptimize with ONE shared step size (`k01`, scalar) collapses at the campaign's CIFAR-100 cells (ResNet18_c100
22.96 vs layerwise 69.42; PlainNet18_c100 11.81 vs 68.96). The shared Lion meta-update's vote is dominated by a few
last-block normalisation SCALE tensors (`ctd1`). Giving those carriers their own step-size group rescues the gap
(`ciso1`, +46.9 pp); a matched non-carrier BN set does not (`cdep1`). The rescue replicates on VGG11_bn (bn8 alone),
GroupNorm ResNet18 and residual-free PlainNet18, and lasts 250–430 epochs. The hold interventions (`cvt4`, `cvt6`–`cvt9`)
show that a LARGE held step-size trajectory on the carriers is SUFFICIENT to stall to the scalar level (PlainNet: one
tensor; ResNet: three tensors at PlainNet's dose), a small one keeps the rescue, the complement's early collapse adds a
separate partial loss, and the damage is graded in dose and spread across the rise and fall of the trajectory.

## 1. The three limits at a glance

| | Limit, one sentence | Corpus says | Prior art says | Can a MUST-tier batch move it? |
|---|---|---|---|---|
| **L1** | One training setting per network, CIFAR only (ImageNet-1k impossible here, `docs/DATASETS.md`). | Collapse: 17/58 paired cells (R50). Mechanism evidence: 8/58 cells, ALL at one hyper-parameter point. CIFAR-10 at the same hyper-parameters does NOT collapse. | Small-scale scope is normal for this literature. The parent itself ran scalar (SGDm, Lion) successfully on ImageNet. | Partly: S1 (momentum 0.9, WD 0, norm-WD 0), S2 (meta step 3e-4), S3 (CIFAR-10 dominance). |
| **L2** | The interventions show SUFFICIENCY at that setting, not NECESSITY and not other settings. | Every hold, ISO and CTL arm sits at meta step 1e-3, alpha0 1e-6, SGDm 0.99 / wd 0.1 + Lion, CIFAR-100. | No paper establishes necessity for any per-group LR either; the claim is not weaker than the field norm. | Yes, at one cell: N1 (shadow-vote necessity), N3 (merge inside layerwise), N4 (weight-decay route). |
| **L3** | On ResNet, `cvt8` resolved the dose (`DOSE-FULL`) but the held set still differs (3 carriers vs PlainNet's 1 tensor); the route is partial at `k01`'s dose. | `cvt8`: HOLDBIG 19.38 and BIGISOPATH 19.42 (both below `k01` 23.06); HIGHISOPATH 58.19 (`ROUTE-PARTIAL`). | Only lead: Kim et al. (position-dependent gamma roles, under L2 not step size). | Yes: R1 (one tensor vs three at PlainNet's dose, 8 arms, no new code). |

### 1.1 RESULTS SO FAR — the first four MUST-tier batches, landed 18 Sep 2026 (CORRECTIONS 264, 265, 266)

*Added after the tier was approved and run. Registered verdicts only; the authority is `docs/CORRECTIONS.md`,
and each sentence below is licensed at ONE cell only. Corpus is now 3,181 rows (the four batches ingested once,
+54 rows, 0 changed, commit `77c6de9`).*

| id | batch | registered verdict | what it does to the limit |
|---|---|---|---|
| **S1a** | `cmo1`, 27 runs (264) | `M9:COLLAPSE-PERSISTS/ISO-RESCUES` + `W0:COLLAPSE-IS-CONFIG/ISO-UNREADABLE` | **L1 widens on momentum, NARROWS on weight decay.** At SGDm momentum 0.9 the collapse persists (`M9k01` 24.58 vs `M9kL` 69.39, ratio 0.354) and the carrier isolation still rescues (`M9ISO` 70.90). At base weight decay 0 the collapse is GONE — `W0k01` 71.56 is the BEST arm in the batch, +3.39 pp ABOVE its own layerwise arm and +48.77 pp above the anchor `k01`, so there is no gap and ISO is unreadable. **Coupled base weight decay is NECESSARY for the collapse at this cell; momentum 0.99 is not.** §6's conditional has fired: the carrier account must now be written as conditional on coupled weight decay. |
| **S2** | `cst1`, 9 runs (265) | `UNRESOLVED-DECOMPOSITION` — a GATE, no branch | **L1 UNMOVED.** The registered scorer stopped on a tolerance defect (an absolute 1e-3 bar on a quotient whose float32 noise is 1.59e-03 at ms 3e-4), not a harness failure — the harness's update is bit-exact on 6,876 of 6,876 unclamped coordinates. The runs are sound and RULE-20-clean; a FROZEN SUCCESSOR SCORER must be registered before any of it is read. Zero GPU to finish. |
| **S3** | `cct1`, 6 runs (265) | `NOT-COLLAPSED+CARRIERS-DO-NOT-DOMINATE` | **L1 answered on the CIFAR-10 axis, as an ASSOCIATION.** On CIFAR-10 nothing collapses (ratio 0.964) and there the three carriers are still the largest single terms — top-3 on 69 % of records, tensor 59 the argmax on 83 % — but never decisive: `DOM_C` is 0 on all 1,500 records against 0.81 at the collapsing CIFAR-100 cell. **Dominance co-occurs with collapse across these two cells.** Dataset and head width co-vary, so it is not causation. |
| **N3** | `cmg1`, 12 runs (266) | `NO-MERGE-HARMS` | **L2 moves, narrowly and at a near bar.** Keeping the three carriers out of ONE shared group with the rest of `layer4` is NOT necessary for the layerwise level, within ±5 pp — but `D_CAR` = +4.115 pp is only 0.885 pp inside that 5 pp margin and is +8.54 SE from zero in all four seeds, so the honest gloss is **"this merge costs ~4 pp, just under the bar"**, a BOUND, not "costs nothing". The control {47,48,56} is count- and width-matched but NOT role-matched (two weights and a bias, against three weights). |
| **R1 / L3** | `cvt10`, not landed | — | **L3 UNMOVED.** |

**Net effect on §6's "single biggest remaining weakness".** Half answered, half confirmed: **momentum 0.99 is
exonerated, coupled weight decay is not — it is a precondition of the collapse at this cell.** What `cmo1` cannot
say is WHICH weight-decay route acts, because `--weight-decay-base 0` removes decay from every tensor AND from the
meta trace in one flag. **That is exactly what S1b (`cwd1`, `WD_SCALE=normscale:0`) separates, which is why it is now
the highest-value GPU item in the remaining tier** (ranked in full at CORRECTIONS 266.11: 1 the frozen `cst1`
successor at zero GPU, 2 `cwd1`, 3 `csv1` for carrier necessity, 4 `cwd2`, 5 `cvt10`, 6 the newly live S4 CTL-at-M9
arm without which M9's `ISO-RESCUES` can never become a specificity statement).

**Question 2 of §7 is now live and should be put to the professor in this form:** momentum 0.9 does NOT remove the
collapse, but base weight decay 0 DOES. Is the paper still the mechanism, stated as conditional on coupled weight
decay, or does it become a note on a configuration pitfall?

### 1.1b RESULTS SO FAR, CONTINUED — the remaining five MUST-tier readings, landed 19 Sep 2026 (CORRECTIONS 268, 270, 271, 272, 273), **plus the three ResNet weight-decay landings of 20-21 Sep 2026: S1c (`cwd3`, CORRECTIONS 278), S1d (`cwd4`, CORRECTIONS 283) and S1e (`cwd5`, the LADDER, CORRECTIONS 285, landed 2026-09-20T22Z, i.e. just past midnight local on the 21st)**

*Registered verdicts only; the authority is `docs/CORRECTIONS.md`, and each sentence below is licensed at ONE cell only.
Corpus is now **3,316 rows / 3407.9 GPU-hours** (`cwd5` ingested once at CORRECTIONS **285**, +27 rows, 0 changed,
0 of 124,982 pre-existing field-cells changed, commit `91fcd57`); `results/CORPUS-EXCLUSIONS.tsv` 201 -> **222** rows
(21 `ARGS_WD_BASE` rows -- 7 non-anchor arms x 3 seeds -- of which the three `CARW2` rows are the corpus's **first
TWO-AXIS rows**, listed with the ARGS witness and their `DECAY_MASK: on ... wd=0.01 ...` line held by `MULTI_KIND`
in the shape CORRECTIONS **284** registered; `corpus_exclusions.py` NOT edited by the ingest), `--check` PASS,
`c98b` exit 0 with the same verdict as at 283 / 278 / 273 / 266 / 253 / 247. **[SUPERSEDED: 3,289 rows / 3389.7
GPU-hours, `cwd4` ingested once at 283, +21 rows, commit `8b9fbd2`; exclusions 183 -> 201.]**
**[SUPERSEDED: 3,268 rows / 3375.0 GPU-hours, `cwd3` ingested once at 278, +15 rows,
commit `064dff6`; exclusions 171 -> 183.]** **[SUPERSEDED: 3,253 rows / 3364.4 GPU-hours, the four batches ingested once,
+72 rows, 0 changed, commit `66a19fb`; exclusions 126 -> 171.]** **DISCLOSED, and it moved again:** the `--check`
noise-floor demonstration is now `SIGMA_R18ALL` **0.641573 (df 267)** **[SUPERSEDED: 0.645653, df 261]**
**[SUPERSEDED: 0.645141, df 258]**
**[SUPERSEDED: 0.648113, df 255]**, `SIGMA_PLAIN` 0.460632 unchanged; **no bar reads that line** and every registered
floor was frozen at its registration -- `cwd5` (281) correctly froze 0.645141 against the pre-`cwd4` corpus and is
unaffected -- but the next registration must quote the new value.*

| id | batch | registered verdict | what it does to the limit |
|---|---|---|---|
| **S2** | `cst1`, 9 runs, read by the FROZEN SUCCESSOR `cST2` (268) | `NOMINATION-PARTIAL+ISO-RESCUES+CTL-NULL` | **L1 HALF-ANSWERED, replacing 1.1's "UNMOVED".** At a second meta step size (3e-4) the ISOLATION RESCUE TRANSFERS -- `D_ISO` **+41.1567 pp = +74.00 SE** while the count-matched non-carrier triple moves **+0.1807 pp** -- but the VOTE-DOMINANCE NOMINATION DOES NOT: `DOM_C` falls from 0.8069 at ms 1e-3 to **0.4727 = 709 of 1,500 records against a 750-record bar, missing by 41**, and `TOP3_C` by **six**. The campaign may write *the rescue transfers, the nomination is only partial there, and the two are not locked together at this cell*; it may NOT write *the same three carriers are nominated at a second meta step size*. Zero GPU: the successor was registered and pushed before it read a single record, with the 256.5 bars proved unmoved. |
| **S1b** | `cwd1`, 9 runs (271) | `COLLAPSE-VANISHES` | **L1 NARROWS AGAIN, and the WD precondition is LOCALISED.** Removing coupled weight decay from the **20 BatchNorm scales only** -- 4,800 of 11,220,132 parameters, conv and linear weights keeping WD 0.1 -- removes the collapse: `k01NWD` **70.7760** against `k01` 22.9513, `P_NWD` **+47.8247 pp = +85.99 SE**, and the scalar arm sits 1.4340 pp **above** its own masked layerwise reference. That is **98.06 %** of `cmo1`'s whole-network W0 effect. **This is the decomposition 264 could not do.** It still does NOT separate the weight-shrink route from the meta-trace route -- the mask changes both -- and there is no ISO arm. |
| **N1** | `csv1`, 18 runs (272) | `BOTH-ROUTES` | **L2 CLOSES on carrier necessity, at one cell and on a modified algorithm.** With idx 50's applied step pinned at the clamp floor, its COUNTERFACTUAL shadow vote alone costs **+15.3630 pp** of the 52.3113 pp HEAD-minus-`k01` gap, and an applied step **ABOVE THE CLAMP FLOOR** is necessary for the remaining **+37.7610 pp**. **The registered licence says "a LARGE applied step"; only the floor was tested, so the correct sentence is "above the clamp floor" -- a RULE 16 defect reported and not fixed (272.6 F1).** The shadow vote is counterfactual, so this is an algorithm intervention, exactly as §6 predicted a reviewer would say. |
| **N4** | `cwd2`, 15 runs (273) | `WD-ROUTE` + `SCALAR-NEEDS-CARRIER-WD` | **L2 MOVES AGAIN, on the cleanest design of the cycle, and L1's precondition reaches a SECOND NETWORK.** In three open-loop held arms the mask can touch only idx 50's weight update, and removing the coupled decay on that ONE tensor removes the whole held-step damage: `P_WD` **+54.9133 pp** against `R_HIGH` +54.2880, **`F_WD` 1.012**, with `HIGHWD0` 0.6253 pp (inside the null bar) from the control. The PlainNet scalar collapse needs the same tensor's decay: `k01WD0` **65.7500** against `k01` 12.0673. **240 / 246 / 253's "own large step size" is REINTERPRETED as acting through the shrinkage it multiplies.** |
| **R1 / L3** | `cvt10`, 30 runs (270) | `ONE-SUFFICES+ONE50-STALLS+ONE59-STALLS+ONE53-STALLS+SPLIT-NO-EFFECT` | **L3 MOVES, and the counting question CLOSES at this cell.** Each of the three carriers, isolated alone and held on PlainNet's dose, stalls the ResNet run (`P_ONE50` +43.66, `P_ONE59` +46.61, `P_ONE53` +35.21 pp), so 252.8(1)'s held-set confound is gone and 240 / 246's PlainNet sentence transfers to `ResNet18_c100` per carrier. **With the condition:** the same 50-hold does nothing once 53 and 59 are lifted into their own free group (`ISOSPLIT` 67.0893 against ISO 70.1660), so the one-tensor stall **needs the remaining carriers voting in the shared step size**. Still open: why the two networks differ, the closed-loop route at `k01`'s own dose, any PAIR. |

| **S1c** | `cwd3`, 15 runs (**278**) | `CARRIER-DECAY-SUFFICES` + `CAR-REC+CTL-NULL+CTL2-NULL` | **L1's LAST OPEN HALF ON THE WD AXIS CLOSES AT THIS CELL, and it closes with two new confounds attached.** `cwd1` (S1b) masked all **20** BN scales network-wide and therefore could not say *which* tensors carry the precondition. `cwd3` masks the **three `ctd1` carriers ALONE** -- 1,536 of 11,220,132 parameters, in the weight update AND the meta trace -- and the collapse goes: `CARWD0` **70.2640** against `k01` **22.9853**, `P_CAR` **+47.2787 pp = +89.34 SE**, and `CARWD0` lands **INSIDE** `NWD`'s recovery band (+4.5413 pp above the 65.7227 bar; `NWD` **70.7227** replicates `cwd1`'s `k01NWD` 70.7760 in batch). **It is SPECIFIC against both matched non-carrier sets -- `P_SPEC` +47.2627 pp = +89.31 SE -- but that specificity is an ASYMMETRY BETWEEN A MEASURED RESCUE AND TWO BOUNDED FLOORS, not a difference between two magnitudes**: `CTLWD0` (`cdep1`'s DEPTH triple {47,48,56}) and `CTL2WD0` (its class-pure DEPTH2 pair {47,56}) are LOCATIONS at `k01`'s floor -- `P_CTL` +0.0160 pp, `P_CTL2` -0.0520 pp, i.e. below the 2.0 pp `NULL` bar and below **1.0744 / 1.1104 pp at +/-2 SE** (2 SE = 1.058364 pp is the HALF-WIDTH, not the bound), a ratio of **42.6 : 1** at the 2-SE bound. **The other 17 scales' residual is likewise a BOUND: `P_SET` = `NWD` - `CARWD0` = +0.4587 pp = +0.87 SE, <= +1.5171 pp at 2 SE -- AND ITS SIGN IS HORIZON-DEPENDENT** (it crosses zero near epoch 80 and is still moving at 99), so **no share may be read off it and `F_CAR` 0.9904 is DESCRIPTIVE, drifting through 1 across the horizon**. **TWO confounds, both registered and neither excluded: (a) only FIVE 512-wide BN scales exist in `ResNet18_c100`, {47,50,53,56,59}, and THREE are the carriers, so a class-pure carrier-free triple CANNOT exist at that depth (275.1; Kim et al. arXiv:2205.07260); (b) `CTLWD0`'s idx 48 is a BN SHIFT carrying essentially no decay dose, so its EFFECTIVE intervention is TWO scales, not three, and a COUNT/DOSE account fits every number here as well as the carrier account.** ONE cell, ONE network, ONE horizon, every arm SCALAR, one switch changing both routes, three seeds |

| **S1d** | `cwd4`, 21 runs (**283**) | `ONE-SUFFICES-PARTIAL` + `TWO-REC+CTL2-NULL+ONE50-REC+ONE53-PART+ONE59-REC` | **THE COUNT/DOSE RIVAL THAT S1c COULD NOT EXCLUDE IS REFUTED AT THIS CELL, AND THE OTHER TWO CONFOUNDS GET WORSE.** At count **two** -- where a class-pure, width-, depth-, numel- AND count-matched CARRIER-FREE pair `CTL2WD0` {47,56} DOES exist, which at count three it arithmetically could not -- the two accounts come apart: `TWOWD0` {50,53} reaches **67.0713** (`REC`) while `CTL2WD0` stays at **22.8547** (`NULL`), **`P_2SPEC` +44.2167 pp = +83.94 SE**, `TWO-SPECIFIC`. **And ONE carrier scale alone -- 512 of 11,220,132 parameters -- can suffice**: `ONE59` **67.9567** (`REC`), `ONE50` **65.2233** (`REC`, but only **+0.40 SE** past the bar -- DESCRIPTIVE / UNSURE), `ONE53` **58.5780** (`PART`, and still climbing at epoch 99). **`D_TWO` = `CARWD0` - `TWOWD0` = +2.9387 pp = +5.58 SE**, so the third carrier still adds something; **`ONE59` - `TWOWD0` = +0.8853 pp = +1.68 SE, NOT resolved**, so the ladder is not cleanly monotone. **The control reading is a BOUND, not a measured zero**: `P_CTL2` +0.0333 pp = +0.06 SE, +/-2 SE **[-1.0202, +1.0868] spanning zero**, per-seed signs flipping -- the licensed form is *"leaves the run at `k01`'s floor"*, never *"does nothing"*. **A "dose of removed decay" reading is closed with an IN-BATCH number**: at probe record 0 every BN scale is still 1.0 and `dm_wdterm` is a pure function of k, so `TWOWD0` and `CTL2WD0` remove NUMERICALLY IDENTICAL decay at init and still differ by 44.2167 pp. **BUT: this batch separates COUNT and nothing else.** `MAGNITUDE-NOT-SEPARATED` and `POSITION-CLASS-NOT-SEPARATED` are unconditional, and both confounds are now SHARPER than at S1c -- the two `REC` singles {50,59} are both Kim **γ_last** and the `PART` single {53} is **γ_down**, and the three singles land in exactly the mean-`|L|` rank order RE-DERIVED IN BATCH (59 3.1188e-01 > 50 2.7474e-01 > 53 1.8077e-01, ranks 1/2/3 of 62 against controls at 33 and 38, a **140.1x** gap; set ratio **340.2**) with BOTH gaps resolved and `SINGLES-SATURATED` absent, which is evidence **FOR** the magnitude rival. ONE cell, ONE network, **ONE WD value (coupled 0.1)**, ONE horizon, every arm SCALAR with no layerwise arm, three seeds |

| **S1e** | `cwd5`, 27 runs, **the LADDER** (**285**) | `THRESHOLD-W1-W2` + `W1-COLLAPSE+W2-NOGAP+W3-NOGAP+W4-NOGAP+CAR-UNREADABLE` | **THE SCOPE OF S1b / S1c / S1d IS NOW MEASURED, AND IT IS NARROW: THE COLLAPSE EXISTS AT THE CAMPAIGN'S COUPLED WEIGHT DECAY 0.1 AND AT NO LOWER RUNG.** Four rungs -- **0.1 / 1e-2 / 1e-3 / 5e-4** -- with **BOTH grains run IN BATCH at every rung**, so every gap is a within-rung contrast and the reference at each rung is that rung's OWN layerwise arm. `G_W1` = `kLW1` - `k01W1` = 69.2940 - 23.2240 = **+46.0700 pp = +87.46 SE**, state **`COLLAPSE`** (the scalar arm is 11.4230 pp below its rung's 0.50x bar). `G_W2` **-1.0893 pp**, `G_W3` **-4.1607 pp**, and the **CO-PRIMARY `G_W4` = -4.5267 pp = -8.59 SE at the standard CIFAR 5e-4**: all three **`NOGAP`**, with the scalar arm **35.2203 / 38.3293 / 38.4673 pp ABOVE** those rungs' collapse bars and, at W3 and W4, **resolved slightly ABOVE its own layerwise arm**. **The account replicates on every individual seed.** The anchor replicates between batch (`k01W1` 23.2240 against `cwd3`'s 22.9853, **+0.2387 pp**, inside the 5 pp `MATCH` bar), so the threshold is not an artefact of a failed anchor. **This is the ADVERSE, PRE-REGISTERED outcome: the referee's corner-case charge LANDS**, and `WRITEUP-mechanism`'s O-14 CLOSES against the generality of the result. **FOUR BOUNDS, and none softens it: (a) the ladder has FOUR points, so the transition is a BRACKETING PAIR between 1e-2 and 0.1 and NOTHING inside that decade may be named (`LADDER-IS-FOUR-POINTS`) -- *"the collapse exists only at 0.1"* is forbidden; (b) `NOGAP` is a BOUND, *"below the 10 pp `GAP_BAR`"*, never *"the grains are equal"*, and `G_W2` is itself NOT RESOLVED (-2.07 SE, +/-2 SE [-2.1428, -0.0358], upper end 0.04 pp from zero -- DESCRIPTIVE / UNSURE), so W2 may not be pooled with W3 and W4; (c) what is identified is the CONJUNCTION of scalar grouping with a coupled decay at or near 0.1 -- at 0.1 the grain matters enormously and below it neither grain reaches the bar -- so neither *"a general granularity effect"* nor *"a property of wd 0.1 independent of grain"* is writable; (d) DECOUPLED weight decay is NOT TESTED in either direction (`DECOUPLED-NOT-TESTED`, descoped with reasons at 281.2) and WHICH ROUTE the decay acts through is not separated.** **The carrier companion is UNREADABLE and is read as nothing**: `CARW2` was pre-registered to be read ONLY if rung W2 collapses, W2 is `NOGAP`, so `CAR-UNREADABLE` fires, `P_CARW2` / `D_CARW2` were never computed, and **71.8327 is a LEVEL only** -- nothing about the carrier account is licensed at 1e-2, in either direction. **The mask DID bite** (positive `dm_wdterm` on 1,500 of 1,500 masked records, `MASK-UPDATE-AND-TRACE`), so this is a **design-scope limit, not a patch failure**. **It RETRACTS NOTHING**: S1b / S1c / S1d measured what they measured at wd 0.1 and every number in them stands. ONE cell, ONE network, ONE horizon, three seeds; every reading WITHIN batch |

**NET EFFECT, replacing 1.1's "half answered, half confirmed": §6's single biggest remaining weakness is now FULLY
CONFIRMED on the weight-decay axis, and localised.** Coupled L2 weight decay on normalisation scales is a
**PRECONDITION of the scalar collapse on BOTH networks and at FOUR grains** **[was "three grains" before CORRECTIONS
278]** -- every tensor plus the meta trace on ResNet (`cmo1`, +48.77 pp), the 20 BatchNorm scales on ResNet (`cwd1`,
+47.82 pp), **the THREE CARRIERS ALONE on ResNet (`cwd3`, +47.2787 pp -- CORRECTIONS 278)**, ONE BatchNorm scale on
PlainNet (`cwd2`, +53.68 pp) -- and **the held-step damage runs through the same factor** (`cwd2`, `F_WD` 1.012).
**At the ResNet cell the precondition is now LOCALISED TO THE CARRIERS THEMSELVES, and is specific against two matched
non-carrier sets -- but as an asymmetry against BOUNDS, and without separating carrier IDENTITY from POSITION CLASS or
from COUNT/DOSE (CORRECTIONS 278, bounds (4) and (5)).** **[AMENDED at CORRECTIONS 283: the COUNT/DOSE half is now
REFUTED at this cell by `cwd4` (S1d) -- at matched count two the carrier pair recovers and the carrier-free pair stays
at the floor, and a SINGLE carrier scale can suffice, so the precondition is localised further, to 512 of 11,220,132
parameters. POSITION CLASS and TERM MAGNITUDE are NOT separated, are unconditional stamps on `cwd4`'s FINAL, and are
both SHARPER after that batch than before it. And the whole of S1b/S1c/S1d sits at coupled weight decay 0.1: whether
any of it exists at normal values is what `cwd5` (registered at 281, 27 runs, not landed) must decide.]**
**[AMENDED AGAIN at CORRECTIONS 285, and this is the amendment that matters most to L1: `cwd5` HAS decided, and the
answer is that NONE of it exists at normal values (S1e). The collapse is PRESENT at coupled wd 0.1 and ABSENT at
1e-2, 1e-3 and 5e-4, so the ENTIRE precondition result -- all four grains, both networks, S1b / S1c / S1d and the
`cmo1` / `cwd2` cells with them -- is now known to sit at ONE weight decay, the one at which this configuration
breaks. NOTHING IS RETRACTED: every number stands, and what changes is that their scope is MEASURED instead of
assumed. What L1 may now say is that the precondition is real AT THAT CONFIGURATION and that the configuration is a
corner case, not a hazard; what L1 may NOT say is where between 1e-2 and 0.1 the failure begins (four rungs BRACKET
and do not locate), that the grains are equal at low decay (`NOGAP` is a bound), or anything at all about DECOUPLED
decay (`DECOUPLED-NOT-TESTED`). The practical consequence for the write-up is at `WRITEUP-mechanism` SS1 A5, SS3.3d
and SS10: the mechanism line becomes a DIAGNOSTIC that qualifies the audit's own scalar row, which is the framing an
area chair recommended for other reasons and is now the only one the data support.]** Momentum 0.99
stays exonerated (264). **He et al. (arXiv:1812.01187, "no bias decay") is the standard reference for NOT applying
weight decay to BatchNorm parameters and biases, so the configuration is one common practice explicitly avoids.**

**WHAT THE CYCLE DOES NOT ESTABLISH, and must be said in the same breath:** the mechanism BY WHICH the decay matters is
**not measured**. `PATCH_DECAYMASK` records weight norms only on the arms where the decay is OFF, and there the scales
**grow** (`cwd1` `kLNWD` carriers 22.6 -> up to 48.9; `cwd2` `k01WD0` 22.63 -> 23.31) with zero tiny weights at all
**7,500** masked probe records **[UNCHANGED by CORRECTIONS 283: `cwd4` adds 9,000 masked records of its own (18 masked
runs x 500; its 3 `k01` runs carry NO `dm_*` key at all and are NOT in that denominator), on all 9,000 of which
`dm_wdterm` is positive and `dm_small` is 0; on its masked arms the scales GROW (22.6 -> 22.8-23.2 by record 499) and
only the floored `CTL2WD0` does not move. The arms that actually collapse still carry no readout.]**
**[UNCHANGED by CORRECTIONS 285: `cwd5` adds only 1,500 masked records (its 3 `CARW2` runs x 500; the other 24 runs
carry NO `dm_*` key at all and contribute 12,000 unmasked records to no denominator here), on all 1,500 of which
`dm_wdterm` is positive and `dm_small` is 0. Its collapsing arm -- `k01W1`, the wd-0.1 scalar anchor -- again carries
NO readout, so the ladder does not move this limit either: the batch that finally measured the decay AXIS still
measures no weight norm on the arm that fails.]** **[UNCHANGED by CORRECTIONS 278: `cwd3` adds 6,000 masked records of its own, on all of
which `dm_wdterm` is positive and `dm_small` is 0 for `CARWD0` / `CTL2WD0` / `NWD`; its `CTLWD0` arm is the one exception
and it is the SHIFT member, idx 48, whose 512 entries sit below 1e-3 from init -- which is evidence about that control's
DOSE, not about filter collapse. `cwd3`'s own collapsing arm `k01` again carries NO readout at all.]** **[CORRECTED at CORRECTIONS 274 from "12,000 masked probe records": 12,000 is the two
batches' WHOLE probe corpus; the MASKED subset that carries a `dm_*` key at all is 7,500 (cwd1 3,000 of 4,500, cwd2
4,500 of 7,500). Every reading is unchanged — `dm_small` is 0 on every record that carries it]**, while the arms that
actually collapse carry no readout at all. Zhou et al.'s
filter-collapse candidate (arXiv:2001.11216) is **neither confirmed nor excluded**. **Naming the precondition is a
SCOPE result, not yet a mechanism.**

**Question 2 of §7 is now ANSWERED by the data and needs only the professor's decision on framing:** momentum 0.9 does
not remove the collapse, weight decay 0 on the normalisation scales does, on both networks and down to a single
tensor, **and at the ResNet cell the three carriers' own decay suffices (278)**. **The recommendation of CORRECTIONS
273.12 is CONSOLIDATE -- write up now**, with the denominator result and the count-matched partition audit keeping the
headline and the mechanism line stated as a bounded, configuration-conditional failure mode. The claim wording proposed
for the paper is at 273.12, **corrected by the referee pass at 277 and AMENDED for `cwd3` at 278; the current text lives
in `docs/WRITEUP-mechanism.md` §1, with §1.3 stating exactly what `cwd3` moved and the two new limits (T18, T19) it
opened.** **`cwd3` CLOSED the write-up's own top-ranked open question O-1; the arm that would separate the count account
from the identity account -- a TWO-carrier mask {50, 53} -- is now O-12 and is NOT registered and NOT launched.**



---

## 2. L1 — narrow scope

### 2.1 The limit

The carrier account is supported at exactly one hyper-parameter point, on four networks from one trunk family, CIFAR-100
only.

### 2.2 What the corpus already shows (read-only census, re-derived independently; both derivations agree exactly)

Gates: 3,127 rows → 3,019 after `filter_rows` → 2,577 admissible (window_ok, complete, plateau5) → 2,363 MetaOptimize
rows (214 fixed-step baselines set aside). Rows sharing a `dup_group` are averaged before n is counted. A cell is every
config field except granularity and seed (CSV columns plus momentum / WD / Lion beta2 / schedule read from `.out`
ARGS/ENV). MERGED view (441 rows without a local `.out` filled from launchers) = 58 paired cells; STRICT = 71. Same
qualitative picture in both.

**Collapse definition (primary): R50** = scalar plateau5 ≤ 0.50 × the reference arm (layerwise if present, else the
best finer arm). Near-chance is not usable (ResNet18_c100 scalar ≈ 23% ≫ 1%).

| definition | MERGED (of 58) | STRICT (of 71) |
|---|---|---|
| R50 vs ref | **17** | 21 |
| R75 vs ref | 21 | 25 |
| R90 vs ref | 25 | 29 |
| R50 vs best finer | 18 | 22 |
| D ≥ 10 pp | 24 | 28 |

**Collapse cells (CIFAR-100 and harder; SGDm(0.99, wd 0.1) + Lion, gamma 1, clip −15:−2.3026, aug 1, bs 100)**

| cell | meta step | alpha0 | ep | scalar (n) | ref (n) | ratio | R50 | carrier/ISO evidence |
|---|---|---|---|---|---|---|---|---|
| PlainNet18_c100 | 1e-3 | 1e-6 | 100 | 11.81 (24) | 68.96 (6) | 0.171 | Y | yes |
| PlainNet18_c100 | 1e-3 | 1e-6 | 300 | 11.67 (3) | ISO 64.31 (3) | 0.181 | Y | yes |
| ResNet10_c100 | 1e-3 | 1e-3 | 100 | 12.97 (3) | 68.52 (3) | 0.189 | Y | none |
| ResNet18_c100 | 3e-3 | 1e-3 / 1e-6 | 100 | 16.35 / 16.81 | 69.86 / 69.61 | 0.234 / 0.241 | Y | none |
| **ResNet18_c100 (mechanism cell)** | 1e-3 | 1e-6 | 100 | 22.96 (44) | 69.42 (32) | 0.331 | Y | **yes** |
| ResNet18_c100 | 1e-3 | 1e-3 | 100 | 22.49 (8) | 69.66 (11) | 0.323 | Y | none |
| ResNet18_c100 | 1e-3 | 1e-6 | 250 | 23.16 (3) | 70.37 (3) | 0.329 | Y | yes |
| ResNet18_c100 | 1e-3 | 1e-6 | 772 | 23.27 (6) | 56.24 (9, no layerwise) | 0.414 | Y | none |
| ResNet18_c100 | 3e-4 | 1e-3 / 1e-6 | 100 | 29.78 / 28.63 | 70.19 / 68.29 | 0.424 / 0.419 | Y | none |
| ResNet18_c100 | 1e-4 | 1e-3 | 100 | 35.79 | 71.08 | 0.504 | N (D +35.3) | none |
| ResNet18_gn_c100 | 1e-3 | 1e-6 | 100 / 430 | 14.26 / 14.84 | 52.86 / 66.39 | 0.270 / 0.224 | Y | yes |
| ResNet34_c100 | 1e-3 | 1e-3 | 100 | 30.86 (3) | 68.12 (3) | 0.453 | Y | none |
| VGG11_bn_c100 | 1e-3 | 1e-6 | 100 / 328 | 35.34 / 35.40 | 66.29 / 66.91 | 0.533 / 0.529 | N (R75 Y) | yes |
| ResNet18_tin (Tiny-ImageNet) | 1e-3 | 1e-6 | 100 | 9.86 (3) | 50.83 (3) | 0.194 | Y | none |
| resnet18, ImageNet-489 subset (NOT ImageNet) | 1e-3 | 1e-6 | 84, bs 256 | 1.00 (5) | 49.21 (5) | 0.020 | Y | none |

Not interpretable (both arms stuck / ref unhealthy): ResNet18_c100 meta 1e-4 alpha0 1e-6 (10.55 vs 10.96); meta 3e-5
and 1e-5 at alpha0 1e-3 (ratio 0.54, 0.77 with an unhealthy layerwise arm).

**Non-collapse cells (the core L1 evidence)**

| cell | pairing | ratio | note |
|---|---|---|---|
| ResNet18 / CIFAR-10, 13 cells incl. the exact mechanism hyper-parameters (C13: 87.91 n15 vs 90.92 n26) | SGDm(0.99) + Lion | 0.962–1.001 | changing CIFAR-100 → CIFAR-10 (and the head 100 → 10) removes the collapse |
| ResNet34, ResNet50 / CIFAR-10 | SGDm + Lion | 0.987–1.015 | |
| ResNet18 / CIFAR-10 | AdamW + Adam (6 cells), AdamW + Lion, Lion + Lion | 0.979–1.017 | |
| ResNet10 / CIFAR-10 | SGDm + Lion | 0.77–0.78 | partial (D ≈ +20 pp) |
| ResNet18 / CIFAR-10, alpha0 1e-6 | SGDm + Adam | 0.468 (clip none), 0.783 (clip on) | **seed-bimodal**: 3 of 7 scalar seeds at 18–21%, the rest 87–88%; no carrier evidence |

**Coverage (58 MERGED cells)**

| axis | values seen | varied at the collapse setting? |
|---|---|---|
| dataset | CIFAR-10 36 (1 R50), CIFAR-100 20 (14), Tiny-ImageNet 1 (1), IN-489 1 (1) | — |
| base optimiser | SGDm 48, AdamW 9 (all CIFAR-10), Lion 1 (CIFAR-10) | **no** (SGDm only) |
| meta optimiser | Lion 46, Adam 12 (all CIFAR-10) | **no** (Lion only) |
| SGDm momentum | 0.99 everywhere; the parent's 0.9 never used | **never varied anywhere** |
| base weight decay | 0.1 in every one of 2,973 ARGS lines carrying the flag | **never varied anywhere** |
| meta weight decay, gamma, hier, schedule | 0, 1, none, default | never varied |
| augmentation, beta clip, batch size | varied only on CIFAR-10 | **no** |
| meta step size | 1e-5 … 3e-3 (cru1) | yes, no carrier runs there |
| alpha0 | 1e-6, 1e-3 (C43 ratio 0.323) | yes, no carrier runs there |
| epochs | 100 plus 250/300/328/430/772 | yes (collapse persists) |

**How narrow, plainly.** The collapse is a CIFAR-100(-and-harder) × SGDm(0.99, wd 0.1) + Lion phenomenon (plus one
bimodal CIFAR-10 SGDm+Adam cell). It is graded in depth (ResNet10_c100 0.19, 18 0.33, 34 0.45) and in meta step size
(0.24 at 3e-3 → 0.50 at 1e-4), each from single batches of n = 3. The carrier account rests on 8/58 cells at one point:
CIFAR-100, SGDm(0.99, wd 0.1) + Lion(0.99, 0.9, wd 0), meta step 1e-3, alpha0 1e-6, gamma 1, clip −15:−2.3026, aug 1,
bs 100. Dataset is confounded with collapse (CIFAR-10 at identical hyper-parameters: no collapse; head width changes too).

### 2.3 Relation to the parent paper's configuration (`docs/PAPER-CONFIG.md`; local text of arXiv 2402.02342)

* CIFAR-10 Table 2: ResNet-18, bs 100, pairings (AdamW, Adam), (Lion, Lion), (RMSprop, Adam), (SGDm, Adam); SGDm row
  rho 0.9, kappa 0.1, alpha0 1e-6, eta 1e-3, gamma 1. No augmentation or beta clip stated; epochs UNSURE.
* **Correction to the census draft:** SGDm + Lion IS a parent pairing. Appendix Table 4 (ImageNet) has an (SGDm, Lion)
  scalar row, parsed as rho 0.9, kappa 0.1, alpha0 1e-5, eta 1e-3, gamma 1 (column alignment UNSURE), and §7.3 /
  Appendix D name MetaOptimize (SGDm, Lion) among the best on ImageNet.
* The mechanism cell therefore differs from the parent's use of this pairing in **SGDm momentum (0.99 vs 0.9)**, alpha0
  (1e-6 vs 1e-5), dataset (CIFAR-100 vs ImageNet), augmentation and the beta clip. It matches on WD 0.1, meta step 1e-3,
  gamma 1, bs 100.
* Consequence: our IN-489 scalar sits at 1.00 while the parent reports scalar (SGDm 0.9, Lion) working on full
  ImageNet. The obvious untested confounder is momentum 0.99. "Collapse needs momentum 0.99" is untested, not refuted.
* Parent §7.3 (quoted from local text): blockwise showed no improvement over scalar on ImageNet. That is the one scope
  counterweight a professor may raise.

### 2.4 What else is feasible without new data or licences (read-only feasibility check on alice2)

| option | status | new code | GPU-h / 100-ep run |
|---|---|---|---|
| CIFAR-100 at other settings (momentum 0.9, WD 0, base/meta optimiser, meta step, alpha0, bs) | available now | none (CLI flags) | 0.66–0.82 |
| carrier contrast at ResNet10_c100 / ResNet34_c100 / ResNet18_gn_c100 | available now | small; probe hard-codes 62 tensors (needs generalising for ResNet10/34) | 0.35–1.1 |
| Tiny-ImageNet-200, ResNet18_tin | on disk, verified, no terms page | none for ResNet18_tin | 1.2–1.6 (>4 h at 300 ep: 7-day partitions) |
| CIFAR-100 upsampled to 64 px | available | small | ≈1.2–1.6 (UNSURE) |
| MNIST M1/M2 (no-norm control) | needs staging; licence not checked | none after staging | <0.3 (UNSURE) |
| SVHN / STL-10 / CINIC-10 | usage terms or licence → **Reza decides** | moderate | — |
| ImageNet32/64 | image-net.org terms → **Reza's own login only** | moderate | ≈25× CIFAR (UNSURE) |
| TinyStories (llama2.c) | CDLA-Sharing-1.0, ~7.6 GB, tokenizer licence UNSURE | large | unmeasured |
| ImageNet-1k | **impossible on this cluster** (not re-litigated) | — | — |

Compute on alice2 alone: L4/MIG/A100 ≈ 0.66–0.77 GPU-h per ResNet18_c100 100-epoch run, 2080 Ti ≈ 2×; `cvt8`/`cvt9`
batch means 0.79–0.82. Peak running concurrency 20–26 (14–17 Sep); good day ≈ 150–190 GPU-h. QOS caps
(≈42 GPUs theoretical) were read once and not re-checked.

---

## 3. L2 — sufficiency, not necessity

### 3.1 The limit

Holding the carriers' step size shows what is SUFFICIENT to stall or rescue at one cell; nothing shows the large carrier
step is NECESSARY, and nothing speaks to other settings.

### 3.2 What the corpus shows

| batch | network | reading (registered, as sufficiency at this cell) |
|---|---|---|
| `ciso1` / `cdep1` | ResNet18_c100 | ISO rescues (+46.9 pp); matched CTL {47, 48, 56} does not |
| `cvt4` (240) | PlainNet18_c100 | large held step on idx 50 stalls; small keeps rescue |
| `cvt6` (246) | PlainNet18_c100 | large step stalls with complement forced onto a recorded path; early complement collapse adds a partial loss |
| `cvt7` (247) | ResNet18_c100 | `k01`'s own trajectory replayed on the three carriers: partial loss (HOLDHIGH ≈ 50) |
| `cvt8` (252) | ResNet18_c100 | `DOSE-FULL+ROUTE-PARTIAL+BIGROUTE-DIRECT` (HOLDBIG 19.38, HIGHISOPATH 58.19, ISO 70.26, `k01` 23.06) |
| `cvt9` (253) | PlainNet18_c100 | `DOSE-GRADED \| WINDOW-GRADED` (HIGHHEADPATH 11.21, MIDDOSE 55.86, RESDOSE 21.84, EARLY 18.37, LATE 27.71) |

Two facts that change how L2 is argued (both read in the repo, not assumptions):

* **Weight decay is 0.1 on the base in every run, and it acts on BN gamma.** `patches/HF_patched.py` lines 592–598:
  `delta = a*(m + wd*w)` and `h = gamma*(1-wd*a)*h - delta`, applied to every tensor, no normalisation exclusion. A large
  carrier step is therefore also strong shrinkage of that gamma (1% per step at the α = 0.1 ceiling), and WD enters the
  meta trace `h`. An earlier prior-art draft assumed WD 0; that was wrong.
* `PROBE_TENSOR` does not log weight norms (`z_tensor`, `m_tensor`, `z_agg`, `mom_pre`, `beta_pre`, `pt_mp`, `pt_b2`),
  so "do the carrier gammas go to zero?" cannot be read from existing probe records.

### 3.3 Prior art (verified only) — what is known, what looks new

| paper | id / URL | venue (verified) | relation | what it establishes |
|---|---|---|---|---|
| Arora, Li, Lyu, *Theoretical Analysis of Auto Rate-Tuning by Batch Normalization* | arXiv:1812.03981; openreview.net/forum?id=rkxQ-nA9FX | ICLR 2019 (forum read; decision page not read) | EXPLAINS-PART | scale-invariant weights converge at any LR; only scale-variant params (gamma/beta, last layer) need a tuned LR (ar5iv body) — predicts WHICH class of tensor carries |
| You, Gitman, Ginsburg, *Large Batch Training of Convolutional Networks* (LARS) | arXiv:1708.03888 | arXiv | EXPLAINS-PART / ADJACENT | per-layer ‖w‖/‖g‖ spans 5.76 → 1345 in AlexNet-BN; one global LR limited by a few layers |
| Zhou, Wang, Luo, Feng, Li, Zhang, *How Does BN Increase Collapsed Neural Network Filters?* | arXiv:2001.11216 | UNVERIFIED | **CANDIDATE MECHANISM (untested here)** | BN+ReLU filter collapse, probability ∝ lr² and ∝ 1/gamma², worse with large/adaptive LR |
| Davis, Frank, *Revisiting Batch Norm Initialization* | arXiv:2110.13989; github.com/osu-cvl/revisiting-bn-init | ECCV 2022 (repo README) | ALREADY-SHOWN (partial) | gamma init ≈ 0.1 and gamma LR ÷ 100 give significant gains (LR detail in README only) |
| Kosson, Messmer, Jaggi, *Rotational Equilibrium* | arXiv:2305.17212 | ICML 2024 | EXPLAINS-PART | under AdamW/Lion/SGDm **with WD**, per-layer angular updates equilibrate; shared LR gives unequal effective rates until then |
| Lobacheva, Kodryan, Chirkova, Malinin, Vetrov, *Periodic Behavior … BN and WD* | arXiv:2106.15739 | NeurIPS 2021 | ADJACENT, **live alternative** | BN + WD periodic destabilisation — a candidate for the rescue lasting only 250–430 epochs (WD is 0.1 here) |
| Li, Arora, *An Exponential Learning Rate Schedule for Deep Learning* | arXiv:1910.07454 | ICLR 2020 | ADJACENT | exp LR ≡ standard schedules under BN + WD + momentum (preconditions hold here) |
| Mehmeti-Göpel, Wand, *On the Weight Dynamics of Deep Normalized Networks* | arXiv:2306.00700 | UNVERIFIED | ADJACENT | effective-LR gaps between layers hurt trainability beyond a critical LR (scale-invariant weights) |
| Mueller, Vlaar, Rolnick, Hein, *Normalization Layers Are All That SAM Needs* | arXiv:2306.04226 | NeurIPS 2023 | ADJACENT (design precedent) | perturbing only norm-affine params (~0.1%) beats all; matched sparse sets do not — same shape as ISO vs CTL |
| Frankle, Schwab, Morcos, *Training BatchNorm and Only BatchNorm* | arXiv:2003.00152 | ICLR 2021 | ADJACENT | BN-affine-only training reaches 82% on CIFAR-10; BN gates features off |
| van Laarhoven, *L2 Regularization versus Batch and Weight Normalization* | arXiv:1706.05350 | arXiv | ADJACENT | L2 on pre-norm weights only changes the effective LR |
| Hoffer, Banner, Golan, Soudry, *Norm matters* | arXiv:1803.01814 | NeurIPS 2018 (arXiv journal-ref) | ADJACENT | norm / WD / LR coupling in normalised nets |
| Heo et al., *AdamP* | arXiv:2006.08217 | ICLR 2021 | ADJACENT | momentum inflates scale-invariant weight norms, shrinking their effective step |

**Known — cite, do not claim:** gamma benefits from its own smaller LR (Davis & Frank); scale-variant tensors are where
LR sensitivity lives (Arora–Li–Lyu); one global LR can be held back by a few layers (LARS); a tiny norm-affine subset can
control an optimiser-level effect where a matched subset cannot (SAM-ON); large LR on BN params can collapse filters
(Zhou et al., candidate); BN + WD produces periodic instabilities (Lobacheva et al.).

**Looks new (nothing found pre-empts it; ~70 papers screened across two sweeps):** (a) a meta-learned SHARED step size
whose meta-update vote is shown, by per-tensor attribution, to be dominated by a few identified last-block
normalisation-scale tensors; (b) the carrier-specific rescue beaten by a matched non-carrier control, replicated across
BN, GN and residual-free nets; (c) hold interventions dissociating dose and route, with a graded dose effect. Searches
combining hypergradient / meta-learned LR with normalisation returned 0 arXiv hits.

**Expected referee line:** "of course BN gammas — they are the only scale-variant parameters" (Arora–Li–Lyu). Answer:
`cdep1` (other gammas do not rescue) and last-block specificity. Note the GN replication is also scale-invariant, so it
supports rather than weakens that argument.

**Necessity:** none of these papers establishes necessity for any per-group LR, so L2 is not weaker than the field norm.

---

## 4. L3 — the ResNet open part

### 4.1 The limit

At PlainNet's dose ResNet stalls (`DOSE-FULL`), but the held set is three carriers together (`layer4.0.bn2.weight`,
`layer4.0.shortcut.1.weight`, `layer4.1.bn2.weight`), not one tensor as on PlainNet; at `k01`'s own dose the route is
partial (HIGHISOPATH 58.19, 3.56 pp above the `ROUTE-DIRECT` bar).

### 4.2 What the corpus shows

`cdep1`'s ONE arm ({`layer4.0.bn2.weight`} alone, free) 64.83 — one tensor largely rescues on ResNet. `cgn2`/`cgn3`: ONE
partial on GN. No ResNet arm has held ONE tensor at PlainNet's dose. `GROUP_HOLD` accepts a one-member group (patch
validation read locally), so this needs no new code.

### 4.3 Prior art

Only lead: Kim, Choi, Jang, Lee, Jeong, Kim, *Guidelines for the Regularization of Gammas in Batch Normalization for Deep
Residual Networks*, arXiv:2205.07260, ACM TIST 15(3) 2024, DOI 10.1145/3643860 — ADJACENT: gamma's role depends on its
position in the residual block (for L2, not step size). No paper explains 3-vs-1.

---

## 5. Ranked experiment program (NOT registered, NOTHING launched; each batch needs its own registration and Reza's go-ahead)

Conventions: 3 seeds/arm (SE ≈ 0.6 pp; effects of interest ≥ 9 pp); 0.82 GPU-h per ResNet18_c100 / PlainNet18_c100 /
CIFAR-10 run, 1.5 for ResNet18_tin; 100 epochs; every batch carries its own `k01` and reference; within-batch contrasts
only; "≈" judged against a pre-registered ±5 pp margin; `PROBE_TENSOR=1` on every `k01` arm.

### 5.0 Zero-GPU checks first (day 0)

| id | check | effect |
|---|---|---|
| Z1 | `ls` alice2 for cvt4/6/8/9 and ctd1 checkpoints; if present read carrier gamma norms and fraction \|gamma\| < 1e-3 (touches run artefacts — needs Reza's OK) | answers Zhou et al. with no runs; else add read-only `PATCH_WNORM` |
| Z2 | grep cru1/cvh1/cgn*/CIFAR-10 `k01` `.out` for `PROBE_TENSOR: on`; run `analysis/cTD1_tensor_dominate_score.py` unedited | free dominance readings; cancels S3 if CIFAR-10 records exist |
| Z3 | put WD-on-gamma and the Σα / WD-shrink table into discussion notes | pre-empts "any BN scale on that much step stalls" |
| Z4 | settle parent Table 4 (SGDm, Lion) column alignment | fixes the "parent config" S1 cites |
| Z5 | dry-parse every `sets:` / `GROUP_HOLD` string in the target trees | avoids a lost night |

### 5.1 MUST-HAVE before the discussion — 106 runs, ≈87 GPU-h raw (≈109 with 25% overhead, +≈2 registration)

| id | limit | question | arms × seeds | runs | GPU-h | new code | licensed sentence (if …) | not licensed |
|---|---|---|---|---|---|---|---|---|
| **S1a** | L1 | Does the collapse, and the ISO rescue, need SGDm momentum 0.99 or base WD? ResNet18_c100 mechanism cell | base {k01, kL}; `--momentum-param-base 0.9` {k01, kL, ISO}; `--weight-decay-base 0` {k01, kL, ISO} | 24 | 19.7 | none | persists: "the collapse does not require momentum 0.99 / base WD" (+ISO: "and isolating the carriers still rescues"); vanishes: "the collapse requires X" (momentum 0.9 would also explain the parent's ImageNet result) | specificity without CTL; other nets/datasets; interactions; WD0 cannot separate weight vs meta-trace route |
| **S1b** | L1 | Does it need WD on normalisation scales only? | k01, kL with `WD_SCALE=normscale:0` | 6 | 4.9 | PATCH_WDMASK (40–80 lines, bitwise inert at s=1) | vanishes: "needs coupled WD on norm scales", which common practice avoids — narrows novelty | decoupled WD |
| **S2** | L1 | Same carriers nominated, ISO rescues, CTL not, at meta step 3e-4 (ratio 0.42)? | k01+probe, ISO, CTL | 9 | 7.4 | none | nominated {50,53,59} and ISO≫CTL: "the carrier rescue holds at a second meta step size" | other datasets; necessity |
| **S3** | L1/L2 | Do carriers dominate the vote on CIFAR-10, where nothing collapses? | k01+probe | 3 | 2.5 | none | dominate: "dominance is not sufficient for collapse"; not: "dominance co-occurs with collapse" | causation (dataset and head co-vary) |
| **N3** | L2 | Inside healthy layerwise, does merging the 3 carriers into one group with a fixed neighbour set collapse, while merging `cdep1`'s {47,48,56} does not? | kL, kL-MERGE-CARRIERS, kL-MERGE-CDEP1 | 9 | 7.4 | none (`sets:`) | "keeping the carriers off a shared vote is necessary for healthy layerwise at this cell" (or not) | all groupings / cells |
| **R1** | L3 | One tensor vs three at PlainNet's dose on ResNet | k01; ISO; HOLDBIG3 `tri:9428`; ONE50 {layer4.0.bn2} free / BIG; ONE59 {layer4.1.bn2} free / BIG; ISO-SPLIT ({53,59} free, {50} BIG) | 24 | 19.7 | none | ONE-BIG ≈ k01: "one isolated carrier on the large dose suffices on ResNet too"; both BETWEEN: "held set differs by network" | why nets differ; dose functional form; closed-loop route |
| **N1** | L2 | Is a large carrier step NECESSARY for the stall, with its shared-step vote intact? PlainNet, cvt1 cell | k01; SHADOW-INERT (1 seed, must equal k01 bitwise); SHADOW-LOW; NAIVE-LOW; MUTE (`VOTE_W=50:0`); HEAD | 16 | 13.1 | PATCH_SHADOWVOTE (60–100 lines, list-capable) | SHADOW-LOW ≈ HEAD: "large applied step necessary, vote dominance alone not sufficient" (token e.g. `APPLIED-STEP-NECESSARY`); ≈ k01: "vote route sufficient"; BETWEEN: "both routes" | ResNet; other doses/horizons; unmodified MetaOptimize (shadow is counterfactual) |
| **N4** | L2 | Is the held step's damage a coupled-WD effect? PlainNet, cvt9 tree | k01, k01-carrierWD0, HIGHHEADPATH, HIGHHEADPATH-carrierWD0, LOWHEADPATH-carrierWD0 | 15 | 12.3 | PATCH_WDMASK (compatible with BETA_HOLD) | HIGH-WD0 ≈ LOW: "damage goes through WD on the carrier scale" (novelty narrows); ≈ HIGH: "gradient-step route" | ResNet; filter-collapse path (needs Z1/WNORM) |
| | | | **total** | **106** | **87.0** | | | |

### 5.2 SHOULD-HAVE — 72 runs, ≈65 GPU-h (gated on S1 / N1)

| id | limit | question | runs | GPU-h | code | gate |
|---|---|---|---|---|---|---|
| T1 | L1 | Tiny-ImageNet ResNet18_tin k01+probe / ISO / CTL (nomination check) | 9 | 13.5 | merge tin patch into probe tree | S1a keeps collapse; 7-day partitions beyond 100 ep |
| S4 | L1 | CTL where ISO rescued at momentum 0.9 / WD0 | 6 | 4.9 | none | after S1a |
| S5 | L1 | alpha0 1e-3 carrier contrast (C43, 0.323) | 9 | 7.4 | none | after S2 |
| S6 | L1/L2 | SGDm + Adam meta on CIFAR-100 (does it need the Lion sign vote?) k01×5, kL, ISO | 11 | 9.0 | none | independent |
| N2 | L2/L3 | N1 on the three ResNet carriers | 13 | 10.7 | SHADOWVOTE lists | N1 clean |
| G1 | L2 | large carrier trajectory inside healthy layerwise, PlainNet | 9 | 7.4 | none | independent |
| R3 | L2/L3 | hold transfer to GN (BN-only Zhou alternative) | 9 | 7.4 | merge GROUPHOLD into cgn1 tree | after Z1/WNORM |
| S1c | L1 | beta clip removed, k01 / kL | 6 | 4.9 | none (ENV) | independent |

### 5.3 NICE-TO-HAVE — 83 runs, ≈69 GPU-h

ResNet dose ladder + window on ISO group (21 runs, 17.3); necessity at a second setting (6–9, ≈7); ResNet10_c100 and
ResNet34_c100 two-stage carrier tests (9 + 12 runs, 4.5 + 13.2; probe generalisation); AdamW pairings on CIFAR-100 (18,
14.8); meta 3e-3 ISO (6, 4.9); CIFAR-10 ISO beside S3 (3, 2.5); ResNet shortcut singleton ONE53 (6, 4.9).

### 5.4 NOT recommended

| item | reason |
|---|---|
| augmentation off | overfit-dominated plateau5; parent does not state augmentation |
| TWINBIG | Σα / WD-shrink table already answers the generic version |
| ResNet50_c100 | ≈22.5 GPU-h, new name + probe generalisation; weakest value per GPU-h |
| longer horizons before S1/N4 | Lobacheva's BN+WD alternative must be read first |
| "finer beats scalar" at new cells as a claim | not new (parent §7; Shea & Schmidt arXiv:2406.17954; Ivgi et al. arXiv:2302.12022) |
| another "gamma wants a smaller LR" test | Davis & Frank already show it |
| MNIST MLP | no norm tensors; needs staging |
| SVHN / STL-10 / CINIC-10 / ImageNet32/64 | licence/terms decisions are Reza's |
| ImageNet-1k | impossible on this cluster |
| TinyStories | large new code, cost unmeasured |

### 5.5 Calendar (alice2, ≈40 jobs/night, each night separately registered)

| day | daytime | night |
|---|---|---|
| 0 | Z1–Z5; register night 1; start SHADOWVOTE, WDMASK, WNORM | S1a + S2 + S3 = 36 |
| 1 | patch inertness tests (each needs a go-ahead); read night 1 | R1 + N3 = 33 (+S1b if WDMASK passes) |
| 2 | review SHADOWVOTE; read night 2; decide S1-gated SHOULD items | N1 + N4 (+S1b) = 31–37 |
| 3 | analysis, discussion notes | spare / reruns |
| **4–5** | **discussion possible** | SHOULD: T1 + S4 + S5 + S6 = 35 |
| 6–7 | | N2 + G1 + R3 + S1c = 37 |
| 8–10 | | NICE, 2–3 nights |

MUST alone ≈ 1 week to discussion-ready. Full program 261 jobs, ≈221 GPU-h raw (≈276 with overhead), 7–8 compute
nights, 2.5–3 weeks wall clock. Pacing is patches, their proofs and registrations, not GPU-h.

---

## 6. Reviewer critique after the MUST tier

* **L1.** Still CIFAR-100 only; every scope axis on ResNet18 only; axes one at a time; the momentum-0.9 arm keeps alpha0
  1e-6 (not the parent's exact Table 4 row); CIFAR-10 contrast co-varies dataset and head; all runs 100 epochs while the
  rescue decays by 250–430. Expected line: "one dataset family, one network per axis, one horizon."
* **L2.** N1's necessity is one PlainNet cell, one floor dose, with a counterfactual shadow vote a reviewer will call an
  algorithm intervention. N3 covers one merge. No ResNet necessity until N2. 3 seeds with ±5 pp margins do not support
  BETWEEN readings well.
* **L3.** R1 settles how many tensors are held, not why ResNet and PlainNet differ, nor the closed-loop route at `k01`'s
  dose.
* **Single biggest remaining weakness.** Every carrier claim sits at one configuration that departs from both the parent
  and common practice — SGDm momentum 0.99 (parent 0.9), coupled L2 weight decay 0.1 applied to normalisation scales,
  and a hard beta clip — while the parent reports scalar (SGDm, Lion) working on ImageNet. A reviewer can call the
  collapse a configuration pathology. S1 and N4 aim directly at this; if momentum 0.9 or norm-WD 0 removes the collapse,
  the finding narrows to a mechanism under that configuration and must be stated so.
* **Wasted by prior art?** Nothing in MUST, provided ISO is framed as mechanism evidence (vote dominance, CTL
  specificity, step/vote dissociation), not as "gamma needs its own LR".

## 7. Questions for the professor

1. Is a finding stated as "at this configuration (SGDm 0.99, coupled WD 0.1 on norm scales, beta clip, CIFAR-100)"
   acceptable, or must S1 (momentum 0.9, WD 0, norm-WD 0) come back before the carrier account is discussed further?
2. If momentum 0.9 removes the collapse, is the paper still the mechanism, or does it become a note on a configuration
   pitfall?
3. Is necessity (N1's shadow-vote design, a modified algorithm) worth the patch, or is sufficiency plus the matched
   control (`cdep1`, N3) enough for the claim he wants?
4. Which widening of L1 does he value most: a second hyper-parameter axis (S2/S5), a second dataset that needs no
   licence (Tiny-ImageNet, T1), or a second pairing (S6 Adam meta)?
5. Any datasets with terms (SVHN non-commercial, CINIC-10 licence, ImageNet32/64 via image-net.org) he wants accepted —
   by Reza, never by an agent?
6. How should the parent's §7.3 ImageNet result (blockwise no better than scalar; scalar SGDm+Lion works) be positioned
   against our IN-489 scalar at 1.00?
7. Does the Zhou et al. filter-collapse candidate (lr²/gamma²) need to be ruled in or out (Z1 checkpoints) before the
   discussion?

## 8. Housekeeping and provenance

* Census scripts and outputs (scratch, not committed): `…/scratchpad/limits_prep/census/scalar_collapse_census.py`,
  `census_merged.txt`, `census_strict.txt`, `cells_*.tsv/json`; independent re-derivation `…/scratchpad/verify/census4.py`,
  `merged4.txt`, `strict4.txt`. Re-derivation trap: `ml2` ARGS lines carry duplicate `--alg-meta` flags (CORRECTIONS
  125.2); argparse last-wins gives 58 cells.
* WebFetch auto-saved three unreadable PDFs (arXiv 2102.06356, 2008.07277, 1708.03888) under
  `~/.claude/projects/-Users-teshnizi-Saber-Optimization/7abb0c79-bcc7-424b-856d-f4a9fed472c1/tool-results/`. Not
  requested; nothing was read from them. Reza decides whether to delete.
* Claims deliberately NOT carried forward (unverified): Nado et al. (arXiv:2102.06356) "LAMB diverges when applied to all
  params"; "TF LARS excludes BN by default" (defaults are None; BN/bias given only as an example); Bjorck et al.
  (arXiv:1806.02375) last-layer-BN claim; MimicNorm's (arXiv:2010.09278) dataset list; Semantic Scholar's list of 6
  MetaOptimize citers.
