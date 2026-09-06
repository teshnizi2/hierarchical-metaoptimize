# STATUS — operator dashboard

Updated 6 Sep 2026 (**cycle 133**). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **157**) > `docs/FINDINGS.md` > everything else.
Manuscript and deposit are both at **`2f4fd9a`** (parent `58c0c85`). **Nothing under `paper/` touched this cycle** (`git status --porcelain paper/` empty).
Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**76 pp**). Corpus = **2,555 rows (UNCHANGED this cycle — `cpk2` LAUNCHED, nothing landed, nothing scored, nothing ingested)**. `alice2` now holds **18 `cpk2` jobs**; `in489g2` still runs on `alice` and is **not ours**.
**`c98_reproduce.py` STILL EXITS 1** — reported as-is, inherited, **author scope, deliberately not fixed**. Stale draft numerals (CORRECTIONS 141.6 / 142.6). 628 `chk()` sites, 411 distinct quantity numerals, 41.9% coverage.
**This cycle LANDED, SCORED and INGESTED `cts3` — the 772-epoch horizon test.** CORRECTIONS **156**. **TWO verdicts, and neither is quotable without the other:** the `k=49 → k=50` cliff **SURVIVED** the horizon (`DE` **19.3427 pp = 26.00 SE**, 1.56× the survive bar) and **SHRINKS** on it (`dD` **−5.6747 pp = −5.39 SE**, bar ±2.1040). **`SHRINKS` was the REGISTERED PREDICTION** (−7.3320 pp; measured landed **+1.58 SE** inside the same branch) — **not a surprise and not a null.** **THE CONSEQUENCE IS A RESCOPING, NOT A RE-LITIGATION:** CORRECTIONS 147's cliff numerals (**24.834 / 25.163 / 24.767 pp**) are **budget-dependent** and now require **“at 100 epochs”** in the same sentence, and `cpk1`'s capture curve, its single-peakedness and its argmax **`k*=49`** are **100-epoch objects** that `cts1`/`cts2`/`scl1` all inherit. **No MASTER-TABLE verdict moves.**

## Cycle 132 — the deliverables

| # | deliverable | outcome |
|---|---|---|
| 1 | `cts3` — the 772-epoch horizon test | **LANDED 6/6, SCORED, INGESTED.** **SURVIVED** *and* **SHRINKS**, both on the registered rule |
| 2 | the rescoping those verdicts force | **147's cliff numerals + `cpk1`'s `k*=49` are 100-epoch objects.** Scope annotated in `docs/STATUS.md`; **`docs/FINDINGS.md` and `docs/MASTER-TABLE.md` need no edit — they never cite them** |
| 3 | ingest | **+6 rows, 0 changed, 0 removed.** Corpus **2,549 → 2,555.** First **>100-epoch** rows the corpus has ever held |
| 4 | corpus-derived constant drift (the CORRECTIONS 155 class) | **CHECKED, NONE.** `cQ1` row 24 **bit-identical** post-ingest. But the `cts3` scorer's `--selftest` **FAILS 5 checks** — 2 correctly, 3 from a **`scl1`-driven** drift that predates this cycle |
| 5 | `docs/MASTER-TABLE.md` | **NOT EDITED** — no cliff numeral or `cpk1` argmax appears in it. Its stale header count is carried, not silently fixed |

## `cts3` — LANDED, SCORED, INGESTED (CORRECTIONS 156)

Scorer `analysis/cO1_cts3_score.py` run **UNEDITED**, sha256 `ba8cac24…77ccf3ad`, **identical on the Mac and in the `alice2` staging checkout** and identical to the blob at the registration commit `327e3f0`; `git diff -- analysis/` **empty**. **`runsdir` is POSITIONAL, not `--runs`**; `--tb` is a documented argument, so passing it is **not an edit** — without it the clamp note prints `UNREAD`.

    python3 analysis/cO1_cts3_score.py /home/s5014158/metaopt/runs \
        --tb /home/s5014158/metaopt/runs/cts3/Tensorboard_outputs

| arm | test@100 | test@E | train@100 | train@E |
|---|---|---|---|---|
| **k49** `[49,13]` | 55.2353 | **56.2487** | 62.4253 | 64.1033 |
| **k50** `[50,12]` | 30.2180 | **36.9060** | 31.9353 | 43.8327 |

| axis | verdict | evidence |
|---|---|---|
| **(a) SIZE at long budget** | **SURVIVED** | `DE` **19.3427 pp = 26.00 SE_ARM_DIFF** — **1.56×** survive bar 12.4170, **13.00×** collapse bar 1.4878 |
| **(b) DIRECTION** | **SHRINKS** | `dD` **−5.6747 pp = −5.39 SE_dD**, bar ±2.1040 |

- **Neither verdict is quotable alone.** "SURVIVED" alone overstates; "SHRINKS" alone understates. The cliff is still **26 SE** wide at 772 epochs, but **22.7% smaller** than these same runs' own 100-epoch cliff — so the 100-epoch numeral **overstates the cliff once the losing arm has converged** (R4: k50 converged at E, not at 100). **Two budgets, two measurements — NOT a monotone trend and NOT an asymptote**; the registration forbids both.
- **`SHRINKS` was PRE-REGISTERED.** Predicted **−7.3320 pp (−6.97 SE)**; measured **−5.6747 (−5.39 SE)** — **+1.58 SE** inside the same branch. **May never be retold as a surprise or as a null.**
- **DECOMPOSITION — the losing arm improves, the winner does not decay.** `d(k49)` **+1.0133**, `d(k50)` **+6.6880**; k50 gains **6.60×** more.
- **Gates.** G0 PASS (6 runs, 6 job ids, 772/772, NAME==ARGS==ENV). **R1 PREMISE PASS** in batch from epochs 95–99 of these same runs: `D100` **25.0173 pp = 33.63 SE**, bar 12.4170 (`cts1`'s own cliff **24.8340**, DESCRIPTIVE only — **no batch splice**). **R2 PASS. R3 NOISE PASS** (worst cell SD 1.6129 ≤ 2.7333). **R4 HORIZON EFFECTIVENESS PASS** — k50's terminal 20-ep OLS slope **+0.03966 at 100 → −0.00199 at E** (bar 0.024235; `cts2` measured 0.04847; registered prediction at E 0.004329). k49 **+0.00239 → +0.00287**, converged at both. **The 772 epochs were not decorative.**
- **RULE 20** `--batch-consistency`: **6 clean, 0 mismatch, 0 without an ARGS line — PASS.** **RULE 21** margin **62 s** (`327e3f0` 12:46:11 → all six `Submit` **12:47:13, zero spread** = ONE submission). 6/6 `COMPLETED`, 6/6 `RUN_DONE`, **0 tracebacks**. ENV **6/6 `AUGMENT=1`**, **6/6 `BETA_CLIP=-15:-2.3026`**, `PROBE=0` 6/6.
- **Cost measured, not projected:** elapsed 04:33:01–05:33:11 × 6 = **31.12 GPU-h** (projected 33.0).

**CLAMP SCOPE (with `--tb`) — reported, never a gate.** Both arms' fine group (`block1`) sits on the −15 floor **95.2–95.4%** of the trace, last value exactly **−15.0000**. The arms differ on the coarse group:

| arm | `block0` min | `block0` last | on-floor |
|---|---|---|---|
| **k49** | **−15.0000** (3/3 reach it) | −14.9230 / −14.4218 / −14.7449 | **4.3 / 6.1 / 3.1%** |
| **k50** | **−13.8155** = the init — **never reaches it** | −13.4934 / −12.9812 / −12.9512 | **0.0 / 0.0 / 0.0%** |

**MAY NOT CLAIM:** the asymptote (registration says so in advance); any horizon but 100 and 772; the released floor at long budget; any cut but 49/50 — **`cpk1`'s `k*` at long budget is UNMEASURED**; any CAPTURE; any other cell; the **mechanism** of the shrinkage.

**NEXT EXPERIMENT — `cpk2`, the argmax at a long budget.** `cts3` leaves exactly one gap open and names it: `k*=49` is an argmax **measured at 100 epochs**, and `cts3` shows the two arms either side of it converge at **very different rates** (k50 +6.6880 vs k49 +1.0133). **Nothing in the corpus establishes that the argmax is still 49 once both arms have converged**, and a two-point contrast cannot relocate it.

| | |
|---|---|
| shape | `k` ∈ {45, 47, 49, 51, 53} × seeds **{3,4,5}** = **15 runs**, at the `cts3` horizon (772 ep) |
| controls | the 100-epoch control **in batch** (as `cts3` did) — no cross-batch splice |
| also fixes | **fresh seeds break the {0,1,2} reuse** CORRECTIONS 152 flagged across `cpk1`/`cts1`/`cts2`/`scl1` |
| cost | ~5.2 GPU-h/run ⇒ **~78 GPU-h** — the thread's most expensive batch |
| must register in advance | **whether it predicts `k*` to move**, and the σ_w it uses (**re-derived, not 0.9111 copied forward**) |

**Cheaper alternatives, recorded so they are not confused with the above:** re-running `cpk1`'s full ladder at 772 ep is ~10× the cost and buys resolution the question does not need; and any 100-epoch batch, however large, **cannot** address a scope defect that is by construction about budget.

## The rescoping — every doc row touched

**`docs/FINDINGS.md` and `docs/MASTER-TABLE.md`: ZERO edits, and that is a measurement, not an omission.** Both files contain **0 occurrences** of `cpk1`, `cts1`, `cts2`, `cts3` and `scl1`, and **0 occurrences** of 24.834 / 25.163 / 24.767. (`FINDINGS.md:9327/9337/9595` contain the string `24.83x` — an unrelated **startup/steady ratio**, deliberately **not** touched. `MASTER-TABLE.md:77`'s "argmax" is the pooling `r*`, not `k*`.) **The whole cut-position thread lives in `docs/STATUS.md` + `docs/CORRECTIONS.md`.**

| file | line (this HEAD) | numeral rescoped | edited? |
|---|---|---|---|
| `docs/STATUS.md` | **483** (threat row 10) | `cts2`'s cliff **24.7673 pp** → "**at 100 epochs**"; *"147's cliff needs no regime qualifier"* now carries an explicit **budget** qualifier, with the 772-epoch value **19.3427 pp** beside it | **YES** |
| `docs/STATUS.md` | **285** | cliff left-edges **k=49 / k=52** — flagged as `cpk1` grid points **measured at 100 epochs** | **YES** |
| `docs/STATUS.md` | **294** | `cpk1`'s **k=45 → k=49** window — flagged **a 100-epoch window**, and `k*=49` a 100-epoch argmax | **YES** |
| `docs/STATUS.md` | **261** | `cpk1`'s second cliff **14.9700 pp** — **at 100 epochs** | **YES** |
| `docs/STATUS.md` | **273** | `scl1`'s **15.8080 pp** single-tensor attribution | **no** — the sentence already opens *"CIFAR-100 / `ResNet18_c100`, …, 100 ep"*. **Checked, correct as written** |
| `docs/FINDINGS.md` | — | — | **no** — 0 occurrences of the numerals or the batch names |
| `docs/MASTER-TABLE.md` | — | — | **no** — same; its rows 56/57 are the CIFAR-100 **granularity** arms, not cut position |

**4 rows edited, 1 verified-and-left, 2 files untouched. No verdict changed anywhere.**

## `cfr2` — LANDED, SCORED, INGESTED (CORRECTIONS 155)

Scorer `analysis/cO2_cfr2_score.py` run **UNEDITED**, sha256 `1e4f531a…d2a3b3ba` **identical on the Mac and in the `alice2` checkout**, `git diff -- analysis/` **empty on both**. `--selftest` **PASSED 0 failures pre- AND post-ingest** (the RULE 21 gate correctly degrading to `[INFO] NOT APPLICABLE`) — **the registration's claim about its own selftest is TRUE, unlike `cfr1`'s**. Every figure below re-derived this cycle from the raw `.out` files and the **6,000 raw probe records** with independent parsers.

| arm | box | **plateau5** | sd | train5 | sd |
|---|---|---|---|---|---|
| scalar | CLAMPED `-15:-2.3026` | **88.7680** | 0.1376 | 93.6340 | 0.4240 |
| layerwise | CLAMPED | **92.0647** | 0.0888 | 99.9127 | 0.0031 |
| scalar | RELEASED `-80:-2.3026` | **89.0780** | **0.4146** | 93.6833 | 0.3898 |
| layerwise | RELEASED | **92.0507** | 0.0842 | 99.9147 | 0.0064 |

| contrast | pp | SE units |
|---|---|---|
| `G_C` (lay − sc, CLAMPED) | **+3.2967** | 18.78 `SE_GAP` (train +6.2787) |
| `G_R` (lay − sc, RELEASED) | **+2.9727** | 16.93 `SE_GAP` (train +6.2313) |
| **`DID = G_R − G_C`** | **−0.3240** | **−1.31 `SE_DID`**, bar 0.4966, CI **[−0.8106, +0.1626]** |
| negative control (scalar `R − C`) | **+0.3100** | bar ±0.3512 — **88.3% of its own bar**, `cfr1` read +0.0067 |
| layerwise `R − C` | **−0.0140** | — |

- **G0/R1/R2/R3/R4 all PASS.** 12/12 COMPLETED, 12/12 `RUN_DONE`, 0 tracebacks, 100/100 epochs. RULE 21 margin **114 s** (`dfd9339` 16:31:52 → all 12 `Submit` 16:33:46, **zero spread**). RULE 20 `--batch-consistency`: **12 clean, 0 mismatch, PASS**, every non-axis flag identical. ENV audit **6 × `-15` / 6 × `-80`**, `PROBE=100` 12/12.
- **Detector validated empirically, not assumed:** largest single-stride `|dβ|` anywhere in the batch = **0.030041** ≤ the registered tolerance **0.0304**, so the wall detector has **no false negatives**.
- **`R4(ii)` PASSED — and the premise it tested is now measured for the first time.** Clamped layerwise **3/3** reach exactly −15.0000, first arrival at **99.5–99.9%** of the theoretically earliest step (26,975) — **free-fall** — with occupancy at this rung's **0.4600** ceiling (`lay-C-s0` sits exactly on it, 230/230). Released layerwise bottoms at −21.80…−21.83, **99.3–99.5%** of the float32 travel bound −21.907576, `n_at_lo = 0` at every record, never within 0.0304 of −80. **Ceiling untouched 12/12** ⇒ the floor is the only wall and a one-factor release is a **complete** box audit here.
- **cfr2's CLAMPED cells replicate the corpus cell** (agreement, never a splice): scalar 88.7680 vs 88.7444, layerwise 92.0647 vs 91.9264, gap 3.2967 vs 3.1820 (inside `2·SE_GAP` = 0.3511).

**Four attacks — 2 land hard, 1 is a scope fix, 1 is a refusal.**

| attack | found |
|---|---|
| **the interval (LANDS)** | CI as % of `G_C` = **[−24.59%, +4.93%]**, point **−9.83%**; `ATTENUATED` is **0.70 SE** away (`cfr1`: 1.87 SE). **80% power only against ≥0.7055 pp = 21.40% of `G_C`; 24% power against the effect actually seen.** *"Within the bar"* at this width licenses **"bounded above by ~25%"**, **not** *"does not move the gap"* |
| **the negative control (LANDS HARDEST)** | **it is not a control.** 3/3 clamped scalar runs hit −15.0000 and sit there **31.6–31.8%** of the trajectory; at the **coordinate** denominator `m=1` is pinned **5.7×** more than `m=62` (**31.7%** vs **5.53%**). Released, the scalar coordinate descends to **−19.70 = 85.3% of maximum travel** (vs **8.3%** at `cfr1`'s rung) and **ends training frozen**, 0.30 nats from the registered `COLLAPSED-BY-FREEZING` threshold. `DID` = (lay −0.0140) − (sc **+0.3100**): **the arm assumed inert supplies 100% of the estimate.** Per seed **+0.232 / +0.628 / +0.070 — 3/3 same sign** (layerwise is sign-mixed), with a **31.6% counterfactual dose** measured in the same runs. `sigma_w` **is** understated for that one cell (sd 0.4146, `P(χ²₂>x)` = 0.024) though the batch's pooled 0.2268 (df 8) is consistent with the registered 0.2150; on the batch's own sigma the CI only **widens** to [−0.8374, +0.1894] |
| **direction / pooling (REFUSAL)** | `cfr1` +0.0320 and `cfr2` −0.3240 are **statistically indistinguishable** (`Q` = 1.02, df 1, p 0.312; direct contrast z = −1.01). Fixed-effect pool **−0.1468 ± 0.1760, p 0.404**. **Legitimate ONLY as a joint-null test** — recorded, **never quotable as an effect size**: exposure differs structurally (**83.81%** vs **46.05%** of trajectory), `BATCH` is the unit of replication, and the scalar arm binds at one rung and not the other. Even the pooled CI still admits **−0.49 pp** |
| **the premise / 148.4 (SCOPE FIX)** | `cfr2` is the **first probe of any `m=62` or `m=1` run at `ms=3e-4`**. 153.8's *"100% bound"* was, when written, an extrapolation from a `m ≥ 777` census (154.5) — **amended in CORRECTIONS 155.8: the claim survives, its provenance is corrected from 148.4 to `cfr2`** (`m=62` 3/3, `m=1` 3/3). The *"94.7%"* in the same line is the `cfr1`-excluded reading; with `cfr1`'s rows in it is **93.12%**. Both recorded |

**ADDITION TO 148.5's m-LADDER (scope caution, not refutation).** 148.5 is headed *"Core set, `ms=1e-3`"*, where `m=1` reads **0.0%**. At **`ms=3e-4`** the run-level ladder is **FLAT** (scalar 3/3 = 100%, layerwise 3/3 = 100%) and the **coordinate-level ladder is INVERTED** (31.7% vs 5.5%). Binding is **non-monotone in `ms`** for `m=1`. **148.5's monotone-in-`m` reading may not be extended to `ms=3e-4`.**

## Row 24 — DISCHARGED / CONSTRAINED / UNAUDITABLE (CORRECTIONS 155.9)

| segment | status |
|---|---|
| `scalar`/`layerwise` @ **`ms=1e-4`** | **DISCHARGED by arithmetic** — min reachable β **−11.914545** > −15; no wall can exist |
| `scalar`/`layerwise` @ **`ms=1e-3`** | **DISCHARGED** (`cfr1`) |
| `scalar`/`layerwise` @ **`ms=3e-4`** | **CONSTRAINED, NOT DISCHARGED** — wall-driven refuted at 7.87 SE, but ≤24.6% not excluded and the estimate rides the mislabelled control arm |
| **peak-location-free headline** (loss at fixed `ms=1e-3` vs own peak), scalar vs layerwise | **DISCHARGED AT BOTH ENDPOINTS** — it uses only `1e-4` (arithmetic) and `1e-3` (`cfr1`). This is row 24's preferred headline and it is now the box-audited one |
| `blk6`, `nodewise` (incl. nodewise's peak @ `3e-4`) | **UNAUDITED** — neither `cfr1` nor `cfr2` ran those arms; `cQ1`'s stratum is the **clamped** box |
| **every rung above `ms=1e-3`** (`3e-3`, `1e-2`) | **UNAUDITABLE WITH THIS BOX** — travel bound at `3e-3` is **−156.9**, so the released **−80 floor is itself reachable**. `blk6`'s and `nodewise`'s **upper chords sit here** |

**Which rungs the four numerals rest on:** `scalar` (peak `1e-4` → `3e-4`, `1e-3`) and `layerwise` (same) now rest **entirely on audited rungs**; `blk6` and `nodewise` each carry a chord on an **unauditable** rung, and `nodewise`'s **peak** sits on clamped `3e-4`. A second, independent reason not to claim the sub-ordering 154 already declined.

## Row 24's numerals DRIFTED on this ingest — measured, not discovered later

`cfr2`'s six **clamped** rows are legitimately inside `cQ1`'s stratum, so ingesting this batch **moves row 24's own re-derived numerals**. `cQ1` re-run **UNEDITED** (sha `aa0bf548…`), `--selftest` **38/38**:

| arm | CORRECTIONS 154 | **post-`cfr2` HEAD** | Δ |
|---|---|---|---|
| `scalar` | 5.8976 ± 0.1659 | **5.8884 ± 0.1547** | −0.0092 |
| `blk6` | 0.9148 ± 0.1843 | **0.9148 ± 0.1827** | 0.0000 |
| `layerwise` | 1.8437 ± 0.1319 | **1.7893 ± 0.1183** | **−0.0544** |
| `nodewise` | 0.7532 ± 0.1701 | **0.7532 ± 0.1687** | 0.0000 |

`sigma_w` 0.1967 (df 216) → **0.1951 (df 222)**; the `ms=3e-4` cells go **n=5 → 8** for both arms; the corpus clamped gap at that rung **3.1820 → 3.2250** and the share-of-decade **93.12% → 94.68%**. **No conclusion moves** — Test A still 3 of 4 AGREE with `nodewise` still DISAGREEing by −1.8398, Test B still resolved at 2 SE, and **B-ALT is completely unchanged** (4.4219 / 0.9144 / 1.6749 / 0.1993) because it touches only cells `cfr2` does not populate. Row 24's printed numerals are **re-stamped and dated**. **This is FINDINGS 58.8(a)'s corpus-growth fragility — the one that broke `nodewise` at 154 — biting `scalar` and `layerwise`, harmlessly, and it will bite again on the next ingest into this stratum.**


## Row 24 — the numerals RE-DERIVED (CORRECTIONS 154, `cQ1`)

`analysis/cQ1_row24_falloff_score.py` (`573c08c`, sha256 `aa0bf548…`) run **UNEDITED**: `--selftest` **38/38**, then `--score`. Zero GPU. Pooled `sigma_w(plateau5)` re-derived at run time = **0.1967** (df 216, 39 cells). Recipe = **mean chord slope** from each arm's peak to every higher rung of the canonical ladder.

**The two questions are scored SEPARATELY and they do not agree.**

| arm | peak (n) | **falloff ± SE** | printed | Δ | 2 SE | **Test A** |
|---|---|---|---|---|---|---|
| `scalar` | 92.2624 @ `1e-4` (5) | **5.8976 ± 0.1659** | 5.871 | +0.0266 | 0.3318 | **AGREE** |
| `blk6` | 92.5300 @ `1e-4` (5) | **0.9148 ± 0.1843** | 1.060 | −0.1452 | 0.3685 | **AGREE** [N1] |
| `layerwise` | 92.8865 @ `1e-4` (11) | **1.8437 ± 0.1319** | 1.801 | +0.0427 | 0.2639 | **AGREE** |
| `nodewise` | 92.4533 @ **`3e-4`** (11) | **0.7532 ± 0.1701** | 2.593 | **−1.8398** | 0.3401 | **DISAGREE** [N1] |

| test | PRIMARY (ladder) | SECONDARY_ALL (every rung) |
|---|---|---|
| `scalar − blk6` | **+4.9829** (2 SE 0.4959) | +5.0228 (0.8347) |
| `scalar − layerwise` | **+4.0540** (2 SE 0.4239) | +4.0939 (0.7950) |
| `scalar − nodewise` | **+5.1445** (2 SE 0.4752) | +5.1844 (0.8229) |
| verdict | **B-POINT + B-2SE HOLD** | **B-POINT + B-2SE HOLD** |

- **B-ALT (peak-location-free, preferred headline)** — loss at the FIXED over-large `ms=1e-3` below each arm's own peak: scalar **4.4219** ≫ layerwise **1.6749** > blk6 **0.9144** > nodewise **0.1993** pp. **HOLDS**, and reproduces FINDINGS 58.8's ordering (4.480/1.736/1.022/0.098) at enlarged `n`.
- **Registered branch (i) fires: sentence CONFIRMED, numerals CORRECTED.** Row 24's verdict stays **CONFIRMED** — attached to **the sentence, not the numerals**.
- **CORRECTIONS 153's blanket "the four numerals do not re-derive" is PARTLY SUPERSEDED, in BOTH directions:** too broad on the values (3 of 4 AGREE), right about `nodewise` and right about the provenance.
- **The column swap is NOT what broke the row.** On the banned `plateau` column the same recipe gives 5.8895 / 0.9249 / 1.8207 / 0.6745 — every arm within **0.08 pp/decade**. The breakage is **corpus growth**: `nodewise`'s peak migrated `1e-3 → 3e-4` as `n` went **1 → 11** — the fragility FINDINGS 58.8(a) flagged and nothing acted on.
- **PROVENANCE DEFECT — the printed row is MIXED-COLUMN.** blk6/layerwise/nodewise reproduce on `plateau` (residuals ≤0.001); **scalar reproduces on `best_test`** (5.8706) and FAILS on `plateau` (+0.0209). Asserted as selftests **T1/T2**, not as a remark. Computed by an **uncommitted ad-hoc script** in cycle 57 (`775eb6b`) — whose CSV **has no `plateau5` column at all** (verified: `plateau` col 33 only; this HEAD has 33 **and** 35). Every `5.871` under `analysis/`+`bin/` is a comment or a registered constant, **never a computation**.
- **NOT claimed:** the sub-ordering among partitions (nodewise 0.753 < blk6 0.915 < layerwise 1.844 — finer is **not** monotonically more tolerant). Both rest on **n=1** cells. Only **partition-vs-none** is asserted.
- **Clamp scope UNCHANGED.** `cQ1`'s stratum **is** the clamped box `-15:-2.3026`; the recomputed `blk6` and `nodewise` falloffs sit on a **still-clamped** surface — and they are the two arms whose numerals moved.

## `cfr2` — the LAUNCH record (CORRECTIONS 154), retained; **superseded by the LANDED section above**

One-factor floor release at **`ms=3e-4`**, the rung `cfr1` left open. `{scalar, layerwise}` × box `{C = -15:-2.3026, R = -80:-2.3026}` × seeds `{0,1,2}`, **all four cells IN BATCH**. Byte-match to `cfr1` proven: `diff` of the two launchers' sbatch composition blocks is **EMPTY**; the only scalar-setting difference is `MST=1e-3 → MST=3e-4`.

| guard | result |
|---|---|
| **ONE submission** | ids **4913096–4913107** contiguous, **all `Submit` 16:33:46, zero spread across 12** |
| **RULE 21** | commit `dfd9339` 16:31:52 → earliest Submit 16:33:46 = **114 s** |
| **RULE 16** | `git diff --name-status 90d314b..HEAD -- analysis/` = **`A`,`A`**; 0 deletions, 0 modifications |
| **RULE 20** | `--batch-consistency` over 7 started `.out`: *"every non-axis flag identical across 7 runs / 7 clean, 0 mismatch"* → **PASS** |
| **ENV audit** (separate — `BETA_CLIP`/`PROBE` cannot ride `ARGS`) | **7/7 agree with run NAME**: 4 × `-15:-2.3026`, 3 × `-80:-2.3026`; `AUGMENT=1 HIER=none SCHED=none PROBE=100`, distinct `PROBE_DIR` each |
| **axes, checked independently of the guard** | `--meta-stepsize 3e-4` in **7/7**; granularity and seed match the name in **7/7** |
| **outcome** | **no mismatch → nothing cancelled.** Re-run at commit time after an 8th job started: **8 clean, 0 mismatch, PASS**; `cfr2-lay-R-s1` (4913103) carries `-80:-2.3026`/`layerwise`/`seed 1`/`3e-4`, all agreeing with its NAME. **4 `PENDING`** get the same audit on start |

- **Instrument re-verified at this rung on the live source.** Float32 travel bound at `ms=3e-4` = **[−21.907576, +8.090129]**. **−80 UNREACHABLE** (58.09 nats / 193,641 non-existent meta-steps — a **wider** margin than `cfr1`'s 23.11). **−15 REACHABLE** (6.9076 nats / 23,025 steps spare; first attainable at meta-step **26,975 = 53.95%**), capping floor exposure at **46.05%** of a run vs 83.81% at `cfr1`'s rung. `T` measured: 50,000 imgs / batch 100 / no `drop_last` → **50,000 meta-steps**. Guard 4f fails closed and passed.
- **Registered bars** (re-derived by the selftest, not quoted): `sigma_w` **0.2150** (df 80, 32 cells; `cfr2-` excluded, `cfr1`'s rows IN), `SE_GAP` 0.1755, `SE_DID` **0.2483**, bar **0.4966**. Power **1.0000** at the registered stake, **0.8857** at 25% of the gap; 80% power against any wall carrying **≥22.17%**.
- **`R4(ii)` is a LIVE gate, not a formality** — see the census defect below.
- **Refused:** a `blk6` arm at this rung (148.5's dose-response table is headed *"Core set, `ms=1e-3`"*; `blk6`'s binding rate at `3e-4` is **unmeasured**, so the arm would open a **second** unmeasured premise); loosening `PROBE` to 333; repeating `cfr1`'s false "selftest stays green post-ingest" claim.

## CORRECTIONS 148.4's census is NARROWER than it has been cited as being

Re-verified this cycle by joining every `ms=3e-4` `HIER=none` run on `alice2` to its **own** `ENV` line:

| granularity at `ms=3e-4` | probe |
|---|---|
| `chunk2325` ×3, `chunk777` ×3, `nodewise` ×3, `nodewise1d` ×3 | `PROBE=5` — **all `m ≥ 777` or `nodewise`** |
| **`scalar` ×5, `layerwise` ×5** | **NO `PROBE` AT ALL** |
| `scalar` ×4, `layerwise` ×3 at `PROBE=100` | **`cfr2`'s own, launched this cycle** |

- 148.4's *"ms=3e-4, n=15, floor 100.0%"* is measured on **`m ≥ 777` / `nodewise` runs ONLY**. **Binding at `m=1` or `m=62` at `ms=3e-4` is UNMEASURED IN THE CORPUS.**
- It is cited in **CORRECTIONS 153.8** and in **row 24's CORRECTIONS-153 annotation** as evidence the layerwise arm binds at that rung. **It is not evidence of that.** Row 24's annotation was narrowed at 154; **153.8 was amended at CORRECTIONS 155.8** — both are now done.
- **SETTLED.** `cfr2`'s clamped arms are the measurement: **`m=62` 3/3 and `m=1` 3/3 reach −15.0000 at `ms=3e-4`**. **The claim survives; its evidence is now `cfr2`, not 148.4.** And the undesigned half — `m=1` binding at all — is what broke the design's negative control (CORRECTIONS 155.6).

## `cfr1` — LANDED, SCORED, INGESTED (CORRECTIONS 153)

12/12 COMPLETED, scorer `analysis/cO1_cfr1_score.py` run **UNEDITED** (sha256 `3c52e678…e41114c`; `git diff -- analysis/` empty). Every figure re-derived here from the raw `.out` files and the 12 `probe.jsonl` traces with an independent parser and an independent probe reducer.

| arm | box | **plateau5** | sd | train5 |
|---|---|---|---|---|
| scalar | CLAMPED `-15:-2.3026` | **87.8707** | 0.2392 | 93.8987 |
| layerwise | CLAMPED | **91.3133** | 0.1406 | 99.8920 |
| scalar | RELEASED `-80:-2.3026` | **87.8773** | 0.0221 | 94.0340 |
| layerwise | RELEASED | **91.3520** | 0.3083 | 99.8933 |

| contrast | pp | SE units |
|---|---|---|
| `G_C` (lay − sc, CLAMPED) | **3.4427** | 19.52 `SE_GAP` |
| `G_R` (lay − sc, RELEASED) | **3.4747** | 19.70 `SE_GAP` |
| **`DID = G_R − G_C`** | **+0.0320** | **0.13 `SE_DID`** (bar 0.4988) |
| negative control (scalar `R − C`) | **+0.0067** | bar ±0.3527, **unmoved** |
| layerwise `R − C` | **+0.0387** | — |

- `VERDICT ROW24-SURVIVES`. G0/R1/R2/R3/R4 all PASS. Ceiling never touched on any clamped layerwise run (12/12) ⇒ the floor is the only wall **at this cell**.
- **Manipulation, coordinate denominator, full trajectory (500 records/run, `n_beta` 62 lay / 1 sc):** clamped layerwise hits exactly **−15.0000** in 3/3 with **27–30 of 62** coordinates pinned and **83.2–83.4%** of records bound against a theoretical maximum of **83.8%**; released layerwise bottoms at −56.51…−56.60, within **0.29–0.38 nats** of the exact float32 bound −56.888439 and **23.4 nats clear** of −80, `n_at_lo = 0` at every record; scalar never within **3.74 nats** of the floor in either box.
- **Bars re-derived independently of the scorer:** `sigma_w` **0.2160** (df 76, 30 cells, **cfr1 excluded**), `SE_GAP` 0.1763, `SE_DID` 0.2494, bar 0.4988 — all exact. **80% power against any wall carrying ≥20.6% of `G_C`**; power ≈ **1.0000** against the registered threat magnitude 2.7343 pp. 95% CI on `DID` **[−0.457, +0.521]** = **[−13.3%, +15.1%] of `G_C`**. **Not an underpowered null.**

**Five attacks — 3 land, 2 do not. None dented a number.**

| attack | found |
|---|---|
| **scope (LANDS)** | row 24 is a multi-rung slope; `cfr1` audits ONE rung. `ms=3e-4` is **100% bound** (census, n=15) and carries **94.7%** of the `ms=1e-3` gap — **unaudited**. Above `ms=1e-3` the **−80 floor is itself reachable** (min −156.9 at 3e-3, −506.9 at 1e-2), so the instrument does not transfer. `blk6` (68.8% bound) and `nodewise` unaudited by registration |
| **wrong cell (DOES NOT LAND)** | FINDINGS 57.2's stratum re-derived from the CSV **is** `cfr1`'s cell — R18/CIFAR-10/SGDm+Lion/**a0=1e-3**/AUG=1/100 ep/canonical box — and the `ms=1e-3` cell is **six ARM-BALANCED families**, not `rs-`-only |
| **which row (LANDS as a re-label)** | 3.44 pp is **row 23's** quantity, not row 24's. Upside: **row 23's headline now replicates inside ONE submission** — 3.4427 vs 3.3585 cross-batch, **0.48 `SE_GAP`** apart |
| **statistical (DOES NOT LAND)** | every registered constant re-derives to 4 dp; power ≈ 1 against every stated form of the threat |
| **numerals (LANDS, unasked)** | row 24's **5.871 / 1.060 / 1.801 / 2.593 do not re-derive** — no script computes them, they sit on the **BANNED k=20 `plateau`** column, and at this HEAD the two natural recipes give 3.778/1.119/1.942/0.285 and 4.427/0.761/1.693/1.125. The **SENTENCE** survives: on plateau5 scalar's drop below its own peak is **3.66×** layerwise's at 3e-4 and **2.61×** at 1e-3 (57.2 published 3.8× / 2.6×) |

- **Mechanism, disclosed:** `exp(−15) = 3.06e−07` vs the same runs' largest coordinate at `1.75e−02…2.34e−02`. Releasing the floor moves pinned coordinates from **4.8** to **22.8** orders of magnitude below the live ones — **off in both boxes** — and both boxes reach **99.89%** train. The measured content is *"nearly-off vs utterly-off costs +0.03 ± 0.49 pp"*. Written so the null is not banked as a surprising rescue.
- **DISCHARGED:** the `1e-4 → 1e-3` decade for the scalar/layerwise pair (lower endpoint clamp-free **by arithmetic**, min reachable β **−11.9078** > −15; upper endpoint now box-free to ±0.5 pp). **NOT DISCHARGED:** `ms=3e-4`; every rung above `1e-3`; `blk6` + `nodewise`; row 24's printed numerals.
- **`row N` = MASTER-TABLE FILE LINE N** — verified (lines 23/24/27/31/100/106 all resolve, incl. the `blk6`-refusal citation). The convention is written down nowhere; any line inserted above the tables silently re-numbers every citation.

## `scl1` — LANDED, SCORED, INGESTED (CORRECTIONS 152)

12/12 COMPLETED, scorer `analysis/cP1_scl1_score.py` run **UNEDITED** (sha256 `c2024f4b…880883e` = `git show aac1bf0:` blob; `git diff -- analysis/` empty). Every figure re-derived from the raw `.out` files with an independent parser, exact to 4 dp, additivity exact.

| cut | spec | n | **plateau5** | sd | train5 |
|---|---|---|---|---|---|
| k52 | `[52,10]` | 3 | **37.8833** | 1.0716 | 41.9247 |
| k53 | `[53,9]` | 3 | **22.0753** | 0.8840 | 22.2713 |
| k54 | `[54,8]` | 3 | **22.2133** | 0.7409 | 22.3507 |
| k55 | `[55,7]` | 3 | **23.3347** | 1.0822 | 23.4853 |

| step | k→k+1 | tensor that moves | params | **dTEST pp** | SE | **dTRAIN pp** |
|---|---|---|---|---|---|---|
| DROP1 | 52→53 | `layer4.0.shortcut.1.weight` (BN **scale**) | 512 | **15.8080** | **21.25** | **19.6533** |
| DROP2 | 53→54 | `layer4.0.shortcut.1.bias` (same BN's **shift**) | 512 | **−0.1380** | −0.19 | −0.0793 |
| DROP3 | 54→55 | `layer4.1.conv1.weight` (**conv**) | 2,359,296 | **−1.1213** | −1.51 | −1.1347 |
| TOTAL | 52→55 | all three | 2,360,320 | **14.5487** | 19.56 | 18.4393 |

- `FINAL: CLIFF CLIFF-REPRODUCES | SPLIT SINGLE-TENSOR-MAJORITY | TENSOR layer4.0.shortcut.1.weight | MECHANISM SHARED-MECHANISM`. R1/R2/R3 none fire. Q1/Q3/Q4/Q5/Q6/Q7 HELD, **Q2 REFUTED**. DROP1 leads **3/3** seeds (16.574 / 15.472 / 15.378).
- Bars re-derived pre-ingest by calling the scorer's own functions: `SIGMA_W` **0.9110578** (df 50, 25 cells, **no `scl1` row** — not circular), `SE_ARM_DIFF` 0.743910, `SE_ADJ` 1.288490, `CLIFF_BAR` 7.4850, `EVEN_BAND`/`SEPARATION`/`ASYM` 2.3476.
- `cpk1`'s own second cliff, DESCRIPTIVE, different batch, **at 100 epochs** (CORRECTIONS 156): **14.9700 pp**.

**Five lenses, 5 of 5 refuted or narrowed the interpretation. Not one dented a number.**

| lens | found |
|---|---|
| arithmetic / narrowing | 147.6 withdrew a claim about predicting **capture LEVEL across cut positions**; `scl1` measured a **within-step attribution** at a step selected for being costly. Different propositions |
| independence | **6 of 12 runs are exact-configuration re-executions** (`[52,10]` in `cpk1`+`cts1`; `[55,7]` in `cpk1`+`cbl1`); only `[53,9]`/`[54,8]` are new. `SIGMA_REPRO` **0.2266** vs `SIGMA_W` 0.9111 = **4.02×**; `CLIFF_BAR` sits **28.6 re-execution SE** below `cpk1`'s own value ⇒ **R1 had no power** |
| structural / live model | the two winners are the **two branch scales of ONE `layer4.0` residual junction**, 1-based indices **50 and 53**; the structural condition holds at **20 of 61 cuts (32.8%)** — an artefact of `named_parameters()` order |
| mechanism / optimiser state | at k53/k54/k55 **both** groups sit at the −15 clamp floor for **58–64%** of the logged trace — the same occupancy as the **scalar** arm `cts1-k01` (0.63); at k52 the leading group ends −10.21 with **0.00** at the floor |
| implementation / provenance | **no defect.** Scorer byte-identical to registration, glob prefix-isolated under a deliberately contaminated run dir, `--selftest` clean pre-ingest, every bar traceable to the corpus |

**THE CLAIM THE CORPUS IS ENTITLED TO** — CIFAR-100 / `ResNet18_c100`, SGDm+Lion, `ms=1e-3`, `alpha0=1e-6`, 100 ep, m=2, this `named_parameters()` order, seeds {0,1,2}: cliff 2 is carried by a single **512-parameter normalisation scale** — moving `layer4.0.shortcut.1.weight` out of the trailing group costs **15.8080 pp (21.25 SE)**, its own 512-param bias one step later costs **−0.1380 pp**, and the adjacent **2,359,296**-param conv **gains** 1.1213 pp; TRAIN agrees. That drop **exceeds the k=52 arm's entire 15.1342 pp advantage** over the pooled same-cell m=1 scalar baseline (**22.7492**, n=17, six batches).

**WHAT MAY NOT BE WRITTEN.**

| forbidden | why |
|---|---|
| *"147.6's withdrawal was TOO CAUTIOUS"* / *"a PATTERN for this sub-class"* | **in the registration blob `aac1bf0` (twice)** — pre-registered, and pre-registration does not license an inference. **147.6 STANDS.** Verdict string NOT edited (RULE 16); its **interpretation** is withheld, exactly as 147.6 did to `BN-LEVERAGE-FAVOURED` |
| any **share-of-TOTAL** for DROP1 (≈109%) | 147.6's fifth narrowing: the denominator is a non-monotone path sum with two negative legs. **Print no percentage** |
| *"reproduces in an INDEPENDENT batch"* | submission independent, **sample is not** — seeds {0,1,2} shared with `cpk1`/`cts1`/`cts2`; `cpk1-k55-s0` and `scl1-k55-s0` both return **23.696** |
| *"at a DIFFERENT site"* | one residual junction, two branch scales, three indices apart |
| *"the matched 512-vs-512 control shows a shift lacks a scale's leverage"* | **not identified at cliff 2** — k53 (−1.18 SE), k54 (−0.94 SE), k55 (+1.03 SE) are **at** the scalar baseline, so DROP2≈0 / DROP3≤0 is what a floor predicts for **any** class. And Q5's statistic `15.9460` is **bit-identical to R3's**. `cts1`'s k50 sits **+7.5855 pp / +13.30 SE** above the same baseline — cliff 1 has no such defect. `SCALE-SHIFT-ASYMMETRIC` stays **descriptive at ONE site** |

**THE `first tensor to leave` RIVAL CANNOT BE SEPARATED BY EXISTING DATA — said plainly.** Both winners are `DROP1` and **had to be**: both cliff left-edges (k=49, k=52 — **`cpk1` grid points measured at 100 epochs**, CORRECTIONS 156) are `cpk1` grid points immediately after a conv, so the tensor at k is necessarily a BN scale. All **six** single-tensor steps in the corpus run **scale → shift → conv**, because `named_parameters()` orders conv → `bn.weight` → `bn.bias` and `--stepsize-groups [k,62−k]` takes a **contiguous prefix** — **no contiguous-prefix cut on this architecture can move a shift before its own scale**. Three rivals stay live: **norm scale**, **first to leave**, **clamp turnover**.

**147.6's grounds, all re-derived here and all untouched.**

- Condition satisfied at `cpk1` k31/k49/k52/k55 with captures **+0.2190 / +0.6965 / +0.3324 / +0.0139** — the peak and the **worst** cut. It also holds at **both** k=52 (37.8833) and k=55 (23.3347) **inside `scl1`**, 14.5487 pp / 19.56 SE apart.
- Base rate: of `cpk1`'s adjacent m=2 steps moving ≥1 norm scale out, **7 RAISE, 2 LOWER** — and `scl1` decomposed one of the 2. **Selection on the dependent variable.**
- Counterexample k=45→47 moves a 512-param BN scale out and **GAINS +3.4487 pp**. Unaddressed.
- **CORPUS NUMERAL CORRECTED:** 147.5c's *"10 steps, 8 raise, 2 lower"* is **7 of 9** on the same manifest (k47→49 moves no scale). 147.6's conclusion is unaffected; **do not re-quote 8/10**.

**NEXT EXPERIMENT — one batch breaks BOTH confounds (class×ordinal and seed reuse).** Decompose `cpk1`'s **k=45 → k=49** window (**a 100-epoch window**; CORRECTIONS 156 makes `k*=49` a 100-epoch argmax) at single-tensor resolution, on seeds **{3,4,5}**, with in-batch anchors:

| step | tensor | class | params |
|---|---|---|---|
| 45→46 | `layer4.0.conv1.weight` | **conv** | 1,179,648 |
| 46→47 | `layer4.0.bn1.weight` | **scale** | 512 |
| 47→48 | `layer4.0.bn1.bias` | **shift** | 512 |
| 48→49 | `layer4.0.conv2.weight` | **conv** | 2,359,296 |

- Class-by-position order is **conv, scale, shift, conv** ⇒ a conv is first to leave and a scale sits in position 2. **No code change, no non-contiguous partition, no scorer exemption.**
- **Off the floor throughout**: `cpk1` M(45)=42.2393, M(47)=45.6880, M(49)=55.4473 — 19.5–32.7 pp above the 22.7492 scalar baseline — and the window **RISES** +13.21 pp net.
- Seeds {3,4,5} make it the **first batch that samples the seed nuisance instead of re-executing it**.
- Shape: k∈{45,46,47,48,49} × {3,4,5} = 15 jobs **+ `scalar` and `layerwise` anchors × {3,4,5}** = 6 ⇒ **21 jobs**, ~15 GPU-h, non-axis flags byte-matched to `scl1`.
- Register in advance: (a) *norm scale* → largest step at 46→47; (b) *first to leave* → 45→46; (c) *clamp turnover* → wherever the leading group's terminal β crosses the floor. **The scorer MUST carry a floor gate**: no drop scored informative if either neighbouring arm is within 2 SE of the in-batch m=1 anchor.
- Weaker variants, recorded so they are not confused with this one: k=56/57 added to `scl1` (6 jobs) breaks the ordinal confound alone **but lands on the saturated floor**; a third cliff on seeds {0,1,2} adds a step and **no** independence.

## Queue — re-derived from `squeue` at this HEAD

| account | batch | jobs | run | pend | done | state | scorer |
|---|---|---|---|---|---|---|---|
| `alice2` | **`cpk2`** | **18** | **5** | **13** | 0 | **REGISTERED AND LAUNCHED this cycle** (CORRECTIONS 157). Cut-position ladder `k∈{45,47,49,50,52}` + `scalar` floor anchor × seeds **{3,4,5}** at **772 ep**, ONE submission, ids **4914387–4914404**. 100-ep control **in run** (ep 95–99). **RULE 21 margin 94 s**; RULE 20 batch-consistency **PASS (5/18 started)**; ENV audit **1 distinct `ENV:` line**. ~93 GPU-h. **Do NOT score or ingest.** | `cR1_cpk2_score.py` (`d5c6eb6`) |
| `alice2` | **`cts3`** | 6 | 0 | 0 | **6** | **LANDED, SCORED, INGESTED this cycle** (CORRECTIONS 156). 6/6 `COMPLETED`, 6/6 `RUN_DONE`, 0 tracebacks, **772/772 epochs** | `cO1_cts3_score.py` (`327e3f0`), run **UNEDITED** |
| `alice2` | **`cfr2`** | 12 | 0 | 0 | **12** | landed, scored, ingested last cycle (CORRECTIONS 155) | `cO2_cfr2_score.py` (`dfd9339`) |
| `alice2` | `cfr1` | 12 | 0 | 0 | **12** | landed, scored, ingested last cycle (CORRECTIONS 153) | `cO1_cfr1_score.py` (`dbf90db`), run UNEDITED |
| `alice` | `in489g2` | 14 | — | — | — | **RUNNING — NOT OURS, never touch.** `squeue` read-only. Never `scancel`, never submit, nothing written to `/data1/salehkaleybars` | `cI2_in489g2_score.py` (`571707b`) |
| `alice2` | `scl1` | 12 | 0 | 0 | **12** | landed and ingested last cycle (CORRECTIONS 152) | `cP1_scl1_score.py` (`aac1bf0`) |

- **`alice2` holds 18 `cpk2` jobs** (5 RUNNING, 13 PENDING). Slurm's own `--start` puts the last (4914404) at **2026-09-09T16:15**; those estimates ignore backfill, so the honest range to completion is **~1.5–3.2 days**. `cts3` cleared its queue in 44 min, but that is **not** claimed here.
- **NOTHING WAS INGESTED THIS CYCLE.** Corpus stays **2,555 rows**. `cpk2` has not landed; **do not score it and do not ingest it.**
- Re-run when all 18 have started: `export METAOPT_WS=/home/s5014158/metaopt; python3 analysis/argsline_guard.py $METAOPT_WS/runs --name cpk2- --batch-consistency --strict`
- `in489g2` on `alice` is **NOT OURS**. **Read with `squeue` only. Never cancel, requeue, modify or submit.** Nothing was written to `/data1/salehkaleybars`.
- **This session cancelled nothing and requeued nothing on either account, and submitted only the 18 `cpk2` jobs on `alice2`.** Remote writes: the staging checkout `/home/s5014158/metaopt/hmo-cpk2/` (at `d5c6eb6`, tree clean, scorer sha256 identical to the Mac's) and `runs/cpk2/PARTITION-MANIFEST.txt`.

## INGEST — `cts3`, **+6 rows** (CORRECTIONS 156.7)

    python3 analysis/aggregate.py ../runs ../runs_alice2 > results/all_runs.csv   # STDOUT, not a log
    python3 analysis/args_repair.py --apply

| | |
|---|---|
| **ADDED** | **6** — exactly `cts3`, ids 4912733–4912738 |
| **CHANGED** | **0** |
| **REMOVED** | **0** |
| corpus | **2,549 → 2,555** |

- **`epochs_requested=772` CHECKED, not assumed.** All six land `epochs_requested=772`, `epochs_done=772`, `window_ok=1`, `complete=1` — **not dropped, not truncated, not coerced to 100**. Each row's `plateau5` equals the scorer's own per-seed `test@E` to the digit.
- **A DRAFTED CLAIM WAS WRONG AND IS CORRECTED:** it is **not** true that no earlier row exceeds 100 epochs — **72 do** (300 and 600), **all on `network=ResNet18`**. What is new is the **value 772**, and any horizon >100 **on `ResNet18_c100`** (previous max **exactly 100**). Only the latter flips a registered premise.
- **`args_repair` reported "36 rows updated"; the keyed diff shows 0 changed fields — and this cycle establishes WHY.** Diffing the tool's own backup shows all 36 touch **exactly one field, `dup_group`**, always `'' → '<name>'`: `aggregate.py` **blanks** it, `args_repair` **restores** it. **A fixed round-trip artefact that will recur on every ingest.** Never read it as a corpus change.

## Corpus-derived constants — the CORRECTIONS 155 class, checked

- **`cQ1` row 24: BIT-IDENTICAL post-ingest.** `sigma_w` 0.1951 (df 222, 39 cells); `scalar` 5.8884±0.1547, `blk6` 0.9148±0.1827, `layerwise` 1.7893±0.1183, `nodewise` 0.7532±0.1687; B-ALT 4.4219 / 0.9144 / 1.6749. **Structurally immune** — `cQ1` pins CIFAR-10 / `ResNet18` / 100 **both** epoch columns; `cts3` fails all three.
- **Every scorer carrying a verdict pins epochs (usually twice) or reads by run-name prefix.** What moves is **bookkeeping**, and **every counter was already stale before this cycle**: `c73` header (2,537/2,222.0 vs CSV **2,555/2,263.7**), `cH1`'s *"ZERO int-list partitions"* (105 → **111**, asserting 0 since `cpk1`), `c98`/`c68` row censuses, `c57`'s denominator. `c69_orphan_census`: `cts3` is **STRICT-CITED**, so **no new orphan** — ORPHAN stays **1 family / 1 run**.
- **`docs/MASTER-TABLE.md` was NOT edited.** Two of `c73`'s five failures (74 vs 73 rows; CONFIRMED 32 vs 31) cannot be fixed without re-litigating verdicts. **Carried, visible, not silently patched.**

## `cts3` scorer `--selftest` — **FAILS 5 CHECKS. 2 ARE THE BATCH SUCCEEDING.**

| check | got | want | reading |
|---|---|---|---|
| `RULE 21: no cts3- row exists` | 6 | 0 | **CORRECT — the rows landed** |
| `no ResNet18_c100 run exceeds 100 ep` | 772 | 100 | **CORRECT — the entire point of the batch** |
| `SIGMA_W` / `df` / `cells` | 0.9173 / 58 / 29 | 0.9111 / 50 / 25 | **`scl1`-driven drift that PREDATES this cycle** |

- **The scorer registered this in advance:** *"once cts3 rows land, the 'no cts3 row exists' check and the corpus-dependent noise floor may legitimately move, and the scorer is NOT edited to make them green (RULE 16, precedent CORRECTIONS 150.7)."*
- **At the registration commit `327e3f0` the corpus reproduced 0.9111 / df 50 / 25 cells EXACTLY.** The stratum then grew 75 → 87 members; the twelve additions are **`scl1-k52/k53/k54/k55 × s{0,1,2}`** (ids 4912717–4912728), which entered at **`c6a282c` (15:17:43) — 2.5 h AFTER** the cts3 registration. **`cts3` itself added nothing** (`_in_cell` pins `epochs_done == 100`).
- **No verdict can move:** `SIGMA_W` is a **frozen literal** and every bar derives from it; only `--selftest` re-derives. The scorer was run **before and after** ingest and the PRIMARY block is **bit-identical**. **The FAIL is the audit working.**
- **Carried:** on the live corpus the honest bar is `sigma_w` **0.9173** (`NOISY_BAR` 2.7519 vs 2.7333). R3 passes under either (worst cell SD 1.6129). **No future `cts*` registration should copy 0.9111 forward without re-deriving it.**

## INGEST (cycle 129, `cfr1`) — the diff, read both ways (CORRECTIONS 146.7)

    python3 analysis/aggregate.py ../runs ../runs_alice2 > results/all_runs.csv   # STDOUT, not a log
    python3 analysis/args_repair.py --apply

| | |
|---|---|
| before / after | **2,525 → 2,537 rows** |
| **ADDED** | **12** — `cfr1-{sc,lay}-{C,R}-s{0,1,2}`, job ids `4912745`–`4912756` |
| **CHANGED** | **0** (keyed on `run`+`job_id`, whole-row compare) |
| **REMOVED** | **0** |
| `args_repair.py --apply` | 36 `dup_group` stamps re-applied (aggregate regenerates without them); **0 accuracy/config values changed**, 0 `superseded` changed. Net vs the pre-ingest CSV: **0 changed rows** |
| ingested rows spot-check | all 12 `epochs_done=100`; the four cell means reproduce the scorer exactly (87.8707 / 91.3133 / 87.8773 / 91.3520) |
| **NOT ingested** | — (that cycle's deferral of `cts3` was discharged this cycle: **+6 rows**, CORRECTIONS 156.7) |

**RULE 20 — `cfr2` 8/8 started runs, re-derived at this HEAD** (4 `PENDING` get the same audit on start):

    export METAOPT_WS=/home/s5014158/metaopt
    python3 analysis/argsline_guard.py --name cfr2- --batch-consistency /home/s5014158/metaopt/runs/cfr2-*.out

- **8 clean, 0 with repeated flags or design mismatch, 0 without an ARGS line — VERDICT PASS.** *"every non-axis flag is identical across 8 runs"*. (Audited at 7 started, re-run at 8 when `cfr2-lay-R-s1` began; both PASS.)
- **`BETA_CLIP` and `PROBE` audited SEPARATELY from each run's own `ENV` line** — they are environment variables and **cannot ride the `ARGS` line**. 4 × `-15:-2.3026`, 3 × `-80:-2.3026`, **each agreeing with its run NAME**; `AUGMENT=1 HIER=none SCHED=none PROBE=100` and a distinct `PROBE_DIR` in all seven.
- **Axes checked independently of the guard:** `--meta-stepsize 3e-4` in 7/7; `--stepsize-groups` and `--seed` match the run name in 7/7. **No mismatch → nothing cancelled.**

**RULE 20 — `cfr1` 12/12 (cycle 129). This CLOSED CORRECTIONS 151.4's 11/12 INCOMPLETE audit.**

    python3 analysis/argsline_guard.py --name cfr1- --batch-consistency ../runs_alice2/cfr1-*.out   # exit 0

- **12 clean, 0 with repeated flags or design mismatch, 0 without an ARGS line — VERDICT PASS.** *"every non-axis flag is identical across 12 runs"*.
- ENV audit (`BETA_CLIP` cannot ride the ARGS line — RULE 20's known blind spot): **6** runs `-15:-2.3026`, **6** runs `-80:-2.3026`, each agreeing with its own run NAME. `RUN_DONE` 12/12, tracebacks 0/12, 12 distinct job ids.

**RULE 21 — `cfr2` 114 s.**

| batch | commit | commit epoch | earliest `sacct` Submit | **margin** | spread |
|---|---|---|---|---|---|
| **`cfr2`** | **`dfd9339`** | 1788705112 (16:31:52) | 1788705226 (16:33:46) | **114 s** | **0 s across all 12** |
| `cfr1` | `dbf90db` | 1788691708 (12:48:28) | 1788691838 (12:50:38) | **130 s** | 1 s |
| `cts3` | `327e3f0` | 1788691571 | 1788691633 | 62 s | 0 s |
| `scl1` | `aac1bf0` | 1788691465 | 1788691498 | 33 s | 1 s |

**RULE 16 — no scorer edited, by anyone, at any point this cycle.** `git diff --name-status 90d314b..HEAD -- analysis/` returns **`A`, `A` and nothing else**; `--numstat` gives `1484/0` (`cO2_cfr2_score.py`), `654/0` (`cQ1_row24_falloff_score.py`) — **0 deletions, 0 modifications**. sha256 parity Mac ↔ `alice2` holds for `cO2_cfr2_score.py` (`1e4f531a…`) and its launcher (`ac782ce7…`); the `alice2` checkout is clean at `dfd9339`.

**RULE 21 does NOT apply to `cQ1`, and the weaker guarantee is stated instead of the label.** `cQ1` has **no runs of its own** — it is a zero-GPU re-derivation over rows that predate it, so no ordering against an `sacct` Submit exists. What is proven is **commit-before-first-execution**: `573c08c` at 16:23:31, first execution 3 s later. Disclosed: a `py_compile` byte-compile preceded the commit; it does not execute the module body.

| check | result |
|---|---|
| `git status --porcelain analysis/ paper/` | **empty**, start and end |
| `git diff --stat -- analysis/` | **empty** |
| `shasum -a 256 analysis/cO1_cfr1_score.py` | `3c52e678cbd086df5acaeb8d0c7b270dbc2d38a4f23c49f5ae48d79cbe41114c` (matches registration) |
| `--selftest` **pre**-ingest | **PASSED, 0 failures** |
| `--selftest` **post**-ingest | **FAILED, 1 failure — BY CONSTRUCTION**: *"no `cfr1-` row exists in the corpus yet"* (12 found), the RULE 21 pre-registration guard, which can only pass before landing. `SIGMA_W` / `CORPUS_GAP` / every bar still re-derive **green** (the registration exempted `SIGMA_W` from `cfr1`'s rows but not this guard, so its claim that the selftest *"stays green after landing"* is **false**). **NOT edited** (RULE 16) |
| score output pre- vs post-ingest | **byte-identical** — the scorer reads `.out` files and probes, not the CSV |

**Cost — `cfr1` spent, measured from `sacct`.**

| batch | state | GPU-h |
|---|---|---|
| `cfr1` | **SPENT** — 12 runs, elapsed 31:26–1:31:56, summed | **9.98** |
| `scl1` | **SPENT** — landed last cycle | 9.80 |
| `cts3` | **SPENT** — landed this cycle | **31.12** |
| `in489g2` | **NOT OURS** (`alice`) | ~348.5, **not counted** |

**NEXT EXPERIMENT — `cfr2`, the rung that actually closes row 24.** `{scalar, layerwise}` × `{-15:-2.3026, -80:-2.3026}` × seeds `{0,1,2}` at **`ms = 3e-4`**, every other flag byte-matched to `cfr1`. It is the only *binding* rung inside row 24's own decade with no clamp-free replicate, it carries **93.5%** of the granularity rise, and `-80` stays unreachable there (min reachable **−21.91**) so the one-factor instrument transfers unchanged. 12 jobs, ~10 GPU-h. Secondary: `cfr3`, `blk6` × `{-15, -80}` × 3 seeds at `ms=1e-3`, 6 jobs, converting the census's 68.8% into the middle rung of a 0% / 68.8% / 100% dose-response. Zero-GPU: re-derive row 24's four falloffs on **plateau5** with a committed script and a stated recipe.

**Live-model manifest — verified here, not accepted from the launcher.**

- `PARTITION-MANIFEST.txt`: **62** tensors, **11,220,132** params. I set-differenced the `FIRSTGROUP` name lists myself and checked the 1-based convention against **all four** specs (`FIRSTGROUP == names[:k]`). Partition **nested**, each step moves **exactly one** tensor, and it is the registered one. Leading-group params 6,447,168 → 6,447,680 → 6,448,192 → 8,807,488.
- The three steps move **49.4519%** of the k=52 trailing group vs `cts1`'s 2.6931% — **homologous in CLASS, not in MASS**, and registered as such in advance.
- **Terminology, once:** at m=2 both groups carry exactly **one** `β` (`HF.py` blockwise), so neither is "finer". Write **trailing → leading**, not "fine → coarse".

**Cost — `scl1` spent, measured.**

| batch | state | GPU-h |
|---|---|---|
| `scl1` | **SPENT** — 12 runs, elapsed 35:07–1:25:38, summed | **9.80** |
| `cfr1` | **SPENT** — landed and ingested THIS cycle (CORRECTIONS 153) | **9.98** |
| `cts3` | **SPENT** — landed this cycle | **31.12** |
| `in489g2` | **NOT OURS** (`alice`) | ~348.5, **not counted** |

## Clamp census — CORRECTIONS 148.3–148.10

**Read-only, 1,171 probe dirs on both accounts (665 `alice` / 506 `alice2`), 1,091 joined to their own `.out`. Nothing written into either runs tree. THE HEADLINE IS A NULL: no finding is refuted; one family is re-labelled.**

| rail (terminal record, n=1,091) | rate |
|---|---|
| FLOOR | 301/1091 = **27.6%** |
| CEILING | 98/1091 = **9.0%** |
| either | 331/1091 = **30.3%** |

**The meta-stepsize is the first-order axis, not granularity.** Core set = canonical box `-15:-2.3026`, `HIER=none`, live meta, n=501:

| `ms` | n | floor | ceiling | binds |
|---|---|---|---|---|
| `1e-4` | 297 | 1.0% | 1.7% | **2.7%** |
| `3e-4` | 15 | 100.0% | 6.7% | 100.0% |
| `1e-3` | 177 | 77.4% | 27.1% | **78.0%** |
| `1e-2` | 12 | 100.0% | 50.0% | 100.0% |

- The 8 binds at `ms=1e-4` are named and **none is an SGDm+Lion primary at the correct box**: `aw1-node-s{0,1,2}` (AdamW, ceiling), `sm3-awrms-node-s{0,1}` (AdamW+RMSProp, ceiling), and the **three `hz3` seed-5 rows already known to carry the wrong box** (CORRECTIONS 8114).
- m-ladder at `ms=1e-3`: scalar **0/10** → blk6 68.8% (R18) → layerwise/nodewise/weightwise **100%** on R10, R18, R18_c100. Two exceptions, both ResNet34: nodewise (m=25,556) **0/5**, weightwise (m=21.3M) **40%**.
- Same ladder at `ms=1e-4`: **34 rungs, n=297, highest single rung 9.1%**, pooled 2.7%. **The rise with `m` exists only where `ms` is past its optimum.**
- Structural nulls: frozen-beta arms **0/78**; `HIER=shrink` **0/26**.
- All **33 scalar probe runs** in the corpus: floor 0/33, ceiling 0/33, and 0/33 touch either wall at any sampled record. FINDINGS 36.3's scalar sentence is **confirmed corpus-wide**.
- **A DETECTOR TRAP, recorded because it produced a wrong answer here first.** `float32(-2.3026) = -2.3025999069213867 ≠ -2.3026`, so exact equality is a clean floor detector and a **broken ceiling** one. The first pass read the corpus ceiling as **2.8%** (true **9.0%**) and CIFAR-100's as **0.0%** (true **68.6%**). Compare against `float32(wall)`. With the tolerance the two detectors agree on **all 667 records carrying both — 0 disagreements**.
- **Pipeline validated against three already-recorded results**, reproduced without being told: `ar1` 12/12 floor (6203) · `fa1` nodewise ceiling 5/6 with the other three arms 0/6 (117.1) · `hz3`'s three seed-5 rows floor-bound while all 21 `-30:9.0` rows are clean (8114).

**MOSTLY ALREADY KNOWN — the confound is FINDINGS 36.3's finding, not this cycle's.** Four prior audits: **36.3** (named the confound) · **51.1** (established the coordinate denominator this census uses) · **51.2/51.4/51.6** (mechanism; frozen half clip-clean 28/28) · **52.2/52.3/52.4** (box-free controls; clip saturation already excluded) · **117.1** (the paper's D already audited) · **147** (`cts1` 12/12) · **6190–6215**, **8114**, **OPERATIONS.md:447**.

**Genuinely new — three things, and they are modest:** corpus-wide scope (all 1,171 probe dirs vs named batches); **`ms` rather than granularity as the dominant axis**; and a coverage statement plus the float32 trap.

**FINDINGS AT RISK — per finding.**

| # | finding | state |
|---|---|---|
| **1** | **MASTER-TABLE row 24** — *"partitioning buys TOLERANCE to an over-large `ms`"* (falloff scalar 5.871 vs blk6 1.060 / lay 1.801 / node 2.593 pp/decade) | **AT RISK, THE WORST CASE.** Its content IS the region above the `ms` peak = the clamped region for partitioned arms, interior for scalar. Restating it as "clamped regime" does not save it — **the regime IS the finding**. Its own instrumentation is absent: the c40 `ms-` family is **0/52** rows with any trajectory (also `ac` 0/42, `bl` 0/30, `ad` 0/29, `r34r` 0/27, `dc` 0/25, `r10` 0/24, `i3a` 0/21, `mx` 0/46) |
| **2** | **MASTER-TABLE row 23** — finer partition helps: **+3.339** shared-`ms`, **+0.564** tuned | **SURVIVES RESTATEMENT.** Tuned figure **clean** (layerwise 0/6 at `ms=1e-4`; floor 8.09 nats away vs 5 nats of Lion travel). Shared-`ms` figure is clamp-asymmetric and must be **labelled clamped-regime** |
| 3 | MASTER-TABLE row 31 — shared-`ms` contrast confounded with preferred `ms` (`hz9`) | **SURVIVES, strengthened.** But `hz9` has no probe dir and no TB trace — its own occupancy is **UNMEASURED, not clean**; disclosed |
| 4 | CLOSEOUT 3 / CORRECTIONS 114.3 — **THE PAPER's D** (+0.5805 ± 0.0939) | **UNTOUCHED.** Already audited at 117.1; this census reproduces it exactly. All 14 count-matched cells at `ms=1e-4` box-inert. `ar1` already VOID, `fa1` already disclosed |
| 5 | CLOSEOUT item 5a — unaugmented parent cell, guard caveat | **CAVEAT DISCHARGED; the CLOSEOUT entry is STALE.** `ub9` at `-60:6.0` measures **0/9**, and releasing the box made the granularity step **larger** — the campaign's one direct test came out **against** the artefact hypothesis |
| 6 | MASTER-TABLE rows 56/57 — CIFAR-100 granularity (+47 pp) | **SURVIVES.** Maximally clamp-asymmetric on paper (scalar 0/2 vs lay/node/weight 13/13, ceiling 68.6%), but a 47 pp effect is not manufacturable by a stepsize wall, and `cts1` reproduces the ordering at `m=2`. Row 57 is a **within-clamped-regime** contrast |
| 7 | MASTER-TABLE row 27 (H4) | **OPEN, not worsened.** `bo6` 4/6 (all ceiling — already recorded as a failed gate); `bo7` **0/12 and on disk** |
| 8 | rows 36/37/38, CLOSEOUT 2 — horizon reversal | **CLEAN.** `br6` 0/12, `bl5` 1/9, `sp8` 0/9, `ns5` 0/15 — already run in released boxes |
| 9 | Direction C (53.1% sign-agreement, frozen profile, `N_eff/m`) | **UNTOUCHED.** Frozen 0/78; already box-tested at 52.3 |
| 10 | CORRECTIONS 146/147 (`cpk1`, `cts1`) | **SETTLED at this contrast by `cts2`** (CORRECTIONS 150): floor released 65 nats, cliff `24.7673 pp` **at 100 epochs**, `INT` `0.3953 pp` = 0.38 SE_INT. 147's cliff needs no **regime** qualifier — but **CORRECTIONS 156 adds a BUDGET one**: at 772 epochs the same contrast reads **19.3427 pp**, so `24.834 / 25.163 / 24.767` are **100-epoch numerals and an upper bound on the converged cliff**. Nothing else in 147.6 is restored |
| 11 | `hz3` wrong-box rows (8114) | A known metadata discrepancy is now **measured to be a real regime difference** |

**COVERAGE — the honest limit. 1,356 of 2,501 rows (54.2%) have a beta trajectory; 1,145 (45.8%) have none.** *(Measured on the pre-`cts2` 2,501-row corpus. The 12 `cts2` rows all carry a trajectory. `scl1`'s 12 rows ran `PROBE=0` and have **no `probe.jsonl`** (verified: 0 probe files under `runs/scl1/`), though they do carry TB `beta_block*` traces because m=2 — so the probe-based numerator is **unmoved** and the denominator is not: **1,368/2,525 = 54.2%**. Every stratum row below is unrestated.)*

| stratum | with a trajectory |
|---|---|
| scalar | 33/246 = **13.4%** |
| layerwise | 344/995 = 34.6% |
| weightwise | 170/248 = 68.5% |
| nodewise | 227/286 = 79.4% |
| `resnet18_blocks` | 242/242 = 100% |
| `ms=1e-3` | 852/1721 = 49.5% |
| `ms=1e-4` | 349/376 = **92.8%** |

- TB `beta_block*` exists on only **339** run dirs and only ever logs `m ≤ 6`, so it can never measure a layerwise/nodewise/weightwise arm. **For any batch not named above the clamp status is NOT MEASURED, and is not inferred.**
- **INFERRED, labelled:** that scalar at `ms=1e-4` is box-free — **no scalar probe exists at any `ms` but `1e-3`**; the argument is algebraic (`β ∈ [ln a0 ∓ ms·T]` = `[−11.908, −1.908]`), and it does **not** exclude the ceiling.
- **Direction of harm is NOT measured.** 117.1 argues a floor INFLATES D for `ar1`; `ub9` measures the opposite. Neither generalises; this cycle claims neither.
- Sampling is the terminal record + 10 interior byte-quantiles, so "bound at some sampled record" is a **lower bound**; the terminal flag is exact.

**THE NEXT EXPERIMENT.**

- **Step 0, zero GPU-h, STILL NOT DONE.** `tc1` (12 rows, `-30:6.0`, measured **1/12**) and `ub9` (9 rows, `-60:6.0`, measured **0/9**) are the only two of the corpus's **24** non-canonical-box cells that contain a **scalar** arm — `wc5`/`cl5`/`uc5`/`uc6`/`bl5`/`br6`/`bo6`/`bo7`/`bd7`/`bf8`/`bf9`/`ns5`/`sp8` are `{layerwise, nodewise, weightwise}` only. **Deliberately not differenced**: their data already exist, so RULE 21 requires a scorer registered and committed first. At n=2 per (arm, `alpha0`) `tc1` is a **direction check, not a settlement**.
- **Step 1 — SUPERSEDED AND EXECUTED AS `cfr1` THIS CYCLE. The design written here was DEFECTIVE; do not resurrect it.** The old text specified box `{-15:-2.3026}` × `{-30:6.0}`, which **moves BOTH walls at once** — CORRECTIONS 149 showed that exact defect is what makes `tc1`/`ub9` ambiguous, and it would have made Step 1 ambiguous in the same way. `cfr1` is the **one-factor** replacement: ceiling **identical at `-2.3026`** in both arms, floor released `-15 → -80` only. Registered `dbf90db`, RULE 21 margin 130 s, running now — see the queue section.
- **What `cfr1` fixed beyond the box.** The released floor is **provably unreachable** (`TRAVEL_LO −56.888439` vs `−80`, from `|Δβ| ≤ ms` over `META_STEPS 50000`), not merely "measured-free" as `-30:6.0` was. Occupancy is read at the **coordinate denominator** with a stride bound (`ms·PROBE = 0.1` nats) that gives the wall detector **no false negatives** — the direct answer to CORRECTIONS 149.7's lower-bound problem. And gate **R4(ii)** requires the clamped fine arm to **actually reach the wall**, so a null cannot be laundered into a vindication of row 24.
- **The ceiling was refused as a third level, on the record**: FINDINGS 6190–6215 measured **2/2 fatal collapses** at `+6.0`, and a diverged arm is `UNRESOLVED-DIVERGED` by gate R2. A `SURVIVES` verdict from `cfr1` therefore discharges the **floor half of the threat only** — the ceiling release is the registered next experiment if the diagnostic shows any clamped layerwise coordinate on `-2.3026`.
- **Extending the census is NOT worth GPU-hours.** The 1,145 un-instrumented rows cannot be re-instrumented without re-running them, and for the modern cells the answer is already "inert".

**COST — measured from history, not guessed.**

| batch | reference | mean/run | projected | worst case (walltime cap) |
|---|---|---|---|---|
| `scl1` (**in flight**) | `cpk1` 39 runs on this cell, 0 TIMEOUT | **42.0 min** | **8.40 GPU-h** | 30.0 (`--time 02:30:00`) |
| `cfr1` (**in flight**) | 191 layerwise + 65 scalar R18/C10 runs on this account | 42.9 / 67.2 min | **11.01 GPU-h** | 36.0 (`--time 03:00:00`) |
| `cts3` (**SPENT**) | **measured**: elapsed 04:33:01–05:33:11 over 6 runs | **4.55–5.55 h** | **31.12 GPU-h** (projected 33.00) | 66.0 (`--time 11:00:00`) |
| **total committed this cycle** | 30 jobs, `alice2` | | **52.41 GPU-h** | **132.0** |
| `cts2` (**DONE**, cycle 126) | measured: 528 wallclock-min over 12 runs | **44.0 min** | **8.80 GPU-h** (spent) | 30.0 |
| `in489g2` (**NOT OURS**, `alice`) | `in489g1` 12 runs = 298.7 GPU-h | **24.89 h** | **348.5 GPU-h** | 476.0 |

**Every row below was re-derived at this HEAD. Do not quote this file as a source; re-run the command.**

## Verdict

| | |
|---|---|
| Q1 meta-gate | **DESK-ACCEPT, 9/10, `structural_gaps = []`, `passed = True`, 0 blocking.** Returned at cycle 111 on v8 (CORRECTIONS 135). **Carried, not re-derivable here** — the gate tool is not in this tree |
| Audit | `c98_reproduce.py` **exit 1 — 8 CHECKS FAIL** at this HEAD after the `cfr2` ingest (rows **2549**/2177, admissible **2107**/1735, wallclock **2534**/2162, GPU-h **2233**/1642, best R18/C10 **93.328**/93.317, deficit **1.796**/1.807, partition-family rows **437**/431, Lion **425**/419). **All 4 substantive numerals (93.328, 1.796, 437, 425) are BIT-IDENTICAL across this ingest** — `cfr2`'s 12 rows are not in the partition families; **only the 4 census counts moved** (2537→**2549**, 2095→**2107**, 2522→**2534**, 2222→**2233**), and the failure count stays at **8**. **No claim reverses.** Historical note, unchanged: verified both ways by restoring the pre-ingest CSV. The 4 **substantive** numerals are bit-identical across the ingest (best R18/C10 arm **93.328** vs paper 93.317; deficit **1.796** vs 1.807; partition-family rows **434** vs 431, Lion **422** vs 419). Only the 4 census counts moved: rows 2,357 → **2,399**, admissible 1,915 → **1,957**, wallclock 2,342 → **2,384**, GPU-h 1,805 → **1,833**. **No claim reverses**, no new claim went stale — baseline unmoved at 95.124 (se 0.047). Fix = edit both markups; **author scope**, CORRECTIONS 141.6 / 142.6 |
| tex↔md | `paper_numeric_diff.py` **5 residuals over 4 distinct tokens** (2 tex-only: `0.05`, `3.0`; 3 md-only: `0.087`, `0.279`, `3.19`). **All pre-existing, 0 new this cycle** — nothing under `paper/` was touched. Both markups carry 994 distinct quantity numerals |
| Science overturned | **none.** Contribution 1 intact at 4 sites; the withdrawal stays confined to the slope |
| GPU to reach submission | **0 jobs, 0 hours.** `cfr1`'s **9.98** GPU-h are spent and landed (CORRECTIONS 153); `scl1`'s 9.80 landed at 152; `cts3`'s **31.12** are spent and landed (CORRECTIONS 156); `in489g2`'s ~348.5 on `alice` are **not ours**. None of it is this manuscript's science |

**Ready to submit: NO** — not for any manuscript defect, for the **seven** author items (§ TODO-FOR-AUTHOR).

## Mechanical verification — commands run at this HEAD

| check | result |
|---|---|
| `python3 analysis/c98_reproduce.py` | **exit 1, 8 CHECK(S) FAILED** at this HEAD — stale draft numerals, not a moved result; **inherited, author scope, deliberately NOT fixed**. Derived vs paper after the `cfr2` ingest: rows **2549**/2177, admissible **2107**/1735, wallclock **2534**/2162, GPU-h **2233**/1642, best R18/C10 **93.328**/93.317, deficit **1.796**/1.807, partition-family **437**/431, Lion **425**/419 — the 4 substantive numerals **bit-identical** to the pre-ingest HEAD. Historical detail from cycle 127, unchanged: `git diff --name-only 94c6e4f..HEAD` over `paper/`, `results/` and `c98_reproduce.py` = **0 files**, so every input is byte-identical to the pre-cycle HEAD. Derived vs paper: rows 2444/2177, admissible 2002/1735, wallclock 2429/2162, GPU-h 2153.85/1642, best R18/C10 93.328/93.317, deficit 1.796/1.807, partition rows 437/431, Lion 425/419. `c98` exited 0 only against the 2,177-row corpus of cycle 116. **A detached worktree is NOT a valid control** — it reports 14, the 6 extra being coverage-census checks that move because gitignored `hz3` `.out` files are absent. See CORRECTIONS 141.6 / 142.6 / 145.4 |
| census fixpoint (measured on `DRAFT-v4.md`, asserted against both markups) | **628 / 411 / 982 / 41.9%** — **unmoved by Plan C, as designed** |
| census internals | raw `\d+\.\d+` 3067 → **3098**, distinct **1007** (unchanged); quantities 2614 → **2615**, distinct **982** (unchanged). The `+1` is the Markdown heading numeral `1.2`; `1.2` already occurred twice as a quantity, so the asserted denominator did not move. `n_q` is asserted by nothing |
| `python3 analysis/xref_check.py` | exit 0, **596 references** (section 500, table 51, figure 22, appendix 23), **0 unresolved, 0 stale**, 8 allowlisted parent-paper refs on lines `[41, 43, 45, 287, 291, 294, 295, 297]` |
| `python3 analysis/test_fence_mask.py` | **ALL PASS** |
| `python3 analysis/paper_numeric_diff.py` | **exit 1 — and exit 1 IS the green state.** 2,606 tex numerals (994 distinct) vs 2,607 md (994 distinct); **2 tex-only** (`0.05`, `3.0`), **3 md-only** (`0.087`, `0.279`, `3.19`) |
| `tectonic -X compile paper.tex`, clean copy of `paper/` | exit 0, **76 pp**, **0** TeX errors, **0** undefined, **0** `??` in the extracted PDF text, **75 labels / 75 distinct refs, 0 orphan, 0 dangling, 0 duplicate**, **2** `Overfull \hbox` (7.28497 pt, 12.25499 pt — the same two as before Plan C, no third) |
| `python3 analysis/dup_group_guard.py` | **21 groups, 42 rows stamped, 3 superseded — PASS**, unmoved by the 42-row ingest (RULE 22) |
| `python3 analysis/c99_hz3q_score.py --selftest` | **59/59 PASS** |
| `c99` gates, raw records supplied | **H0 PASS** (all four arms `NVIDIA L4` / `-30:9.0` / seed 5 / 300 ep) · **H1 PASS** worst coordinate fraction **0.000000**, bar 0.05 · **H2** repaired `-0.238 / 0.093 / -2.57` → **NOT FLAT, D DECLINES WITH BUDGET** · **H3** repaired `D(300) +0.394 / 0.093 / +4.25`, `G(300) -0.048` · **HC** `+0.134 pp`, bar 1.00 → GPU class not first-order on the level. RULE 13 still refuses the archive on both GPU model and `beta_clip` |
| `c87_hz3_score.py` unedited | **VERDICT: SURVIVES** · **MECHANISM SURVIVES THE HORIZON** · `D(300)-D(100) = +0.229` → **GROWS** · `grep -c hz3q` = **0** |
| abstract | **byte-identical to `58c0c85` in both markups** — this cycle did not touch it, so the gate's own figures stand. Plain counts: tex **222** (agrees with the gate's 222); md **231** by plain count against the gate's recorded **228** and a **230** cap. Longest sentence **33 words** in each, bar 62 |

**The abstract has no headroom and the plain count is not the authority.** `_extract_abstract`,
`clean_abstract_text` and `_abstract_defects` are **not in this tree**, so 228 cannot be
re-derived here; a plain count gives 231, over the cap. The difference is three words the gate's
cleaner drops. **Anyone editing the abstract must run the gate, not a word count.**

**OPERATIONAL TRAP — read this before calling a scorer red.** The raw `.out` and `probe.jsonl`
records are **not in the repo** (`runs/` is gitignored). They live one level **above** it, at
`../runs` and `../runs_alice2`. `c98_figures.series()` finds them by itself; `c87_hz3_score.py`
and `c99_hz3q_score.py` do **not** — their `--runs` default is the relative `runs`. Run bare,
`c87` prints *"this batch has NOT been submitted"* and `c99` **REFUSES** under RULE 13. Correct
invocation:

    R="$(cd .. && pwd)/runs"
    python3 analysis/c87_hz3_score.py --runs "$R"
    python3 analysis/c99_hz3q_score.py --runs "$R" --probes "$R/hz3"

**Second trap — `grep` across a line wrap.** The two markups wrap at different columns, so a
single-line `grep` for a phrase longer than roughly 60 characters reports a **false** "missing
from the other markup". This has produced **four** false alarms so far (§9's companion sentence;
CRediT's "Funding acquisition"; §4.8's "identically in all three readings below"; and this
cycle, §4.8's *"the ladder stops at 300 epochs"* guard, which wraps across `DRAFT-v4.md:2273–2274`).
Search a flattened copy (`tr '\n' ' '`, or a whitespace-collapsed buffer) before reporting a divergence.

## Plan C signposting — APPLIED this cycle (R9's mitigation)

| | |
|---|---|
| what was added | a new **§1.2 "Reader's guide and evidence map"** (lead, ten-row evidence map, closing caveat); **ten italic one-shot section openers** at the heads of §3.3, §3.4, §3.5, §4.4, §4.4's endpoint block, §4.7, §5.4, §7 *evidence*, §7 *process*, §8; and **one forward pointer** to §1.2 in §1's closing sentence |
| size | **932 words**, measured — **not** the "≈ 500" `paper/sections/v9-plan.md` asserts. Zero quantities |
| what moved | **nothing.** No section, subsection, table, figure, equation, appendix or threat renumbered; no existing sentence rewritten; no `\label` or `\ref` changed. One new label, `sec:guide`, referenced exactly once |
| the map | a non-floating `center`+`tabular`, so it takes **no table number** and shifts no float numbering. `>{\raggedright\arraybackslash}p{}` columns — without `\raggedright` it generated 32 extra underfull warnings |
| **cost, disclosed** | **75 pp → 76 pp.** Not recoverable: roughly half the growth is the ten openers spread through the document, so no configuration of this package keeps 75 pp. `v9-plan.md`'s Plan C row asserting "75 pp, unchanged" was **wrong by one page** |
| consequential edit | `analysis/xref_check.py`'s `PARENT_LINES` allowlist is **by line number** and five of its eight lines sit after the §1.2 insertion. Re-derived (not pasted): `{41, 43, 45, 287, 291, 294, 295, 297}`. Each was confirmed to carry a genuine parent-paper `§7.x` reference before being listed |
| two deviations from `v9-plan.md` §8 | its §8.3 per-contribution pointers were **dropped** — all seven §1.1 items already end in a bracket naming their sections and floats, so the one-step property already held; and the opener set was **re-chosen on measurement** — §4.6 dropped (893 w), §4.7 added (2,430 w), and §4.8 (2,916 w) deliberately **not** opened, because an opener licenses triage and §4.8 is one of the four things a referee must not skip. It is named in §1.2's load-bearing list instead |

**The functional test is met by three one-hop routes**, each verified against the live text:
§1.1 → section + float (already true); §1.2's map → section + float + the numbered
`c98_reproduce.py` section that re-derives the number + the `make` target that re-runs it (new,
and the only route to the last two); section head → triage answer without reading the section (new).

## Contribution 1 — unweakened, four guard sites, both markups

| site | state |
|---|---|
| Abstract | *"wins all twenty count-matched cells … +0.556 ± 0.045 pp … homogeneous against that null (Q 4.21, median 9.4)"* — `paper.tex:71` / `DRAFT-v4.md:17`. **Byte-identical to `58c0c85`** |
| §1 Contributions item 1 | untouched |
| §4.8 | insertions only; no existing sentence deleted or softened |
| §9 | *"…two findings, of which the second does not weaken the first"* — `paper.tex:4718` / `DRAFT-v4.md:3771` |

- `hz3q` enters **no cell** of Table 2 — `hz3q` count over the `tab:D` row block = **0**.
- **"Declines" cannot be read as "disappears"** — 4 guard sentences, each present exactly once in **both** markups:
  `paper.tex:1363` / `DRAFT-v4.md:1072` *"does not vanish"* · `paper.tex:2856` / `:2249` *"has read it backwards"* ·
  `paper.tex:2882` / `:2273–2274` *"The measured ladder stops at 300 epochs and so does the claim"* ·
  `paper.tex:2944` / `:2331` *"a decline resolved at this budget and this design point rather than a law"*.
- The manuscript-and-check diff for cycle 116 is **195 insertions, 8 deletions**, and every one of the 8 removed lines is a
  line that was rewritten in place (2 forward pointers, 2 threat-index tokens, 1 `F(39,172)` spacing,
  2 `T`-table rows, 1 `PARENT_LINES`). **No sentence was deleted and none was softened.**

## Red team — 10 of 10 answered, 0 blocking

| # | finding | state |
|---|---|---|
| R1 | Abstract carried no trace of the reversal | **CLOSED** (135) — one clause, inside the 230-word cap |
| R2 | §4.8's budget table: no caption, undefined `se` column | **CLOSED on the `se` limb** (137) — both estimators named, general rule stated in both markups (`paper.tex:2832` / `DRAFT-v4.md:2229`). **Caption limb OPEN BY DECISION** — see Open item 2 |
| R3 | No rebuttal to linear extrapolation | **CLOSED** (135) — arithmetic printed, four measured facts against it |
| R4 | Registered bar `\|t\| ≥ 2.0` at df 5 is two-sided α ≈ 0.102, undisclosed | **CLOSED** (137) — disclosed at the site, with both mitigations |
| R5 | Reversal's mechanics unstated | **CLOSED** (135) — location × precision, plus leave-one-out |
| R6 | T9 read as scoping all three readings | **CLOSED** (135) |
| R7 | `f3_budget` panel (b) drawn on the archive | **CLOSED** (135) — redrawn, all three readings |
| R8 | Deposit `make reproduce` cold-skips `[7] BUDGET` | **CLOSED as documented** (138) — the soft skip is the correct behaviour; the README names the section, why it cannot read, that the skip is announced, and the one-command fix |
| R9 | **Length.** Reviewer-burden desk-return is the biggest venue risk | **RESTRUCTURE DECLINED ON MEASUREMENT; MITIGATION APPLIED** (139). Body 67 pp / 46,288 words at 691 w/pp, so a 15-pp body needs ≈ 7,600 words of new number-dense prose in both markups: a rewrite, not a reorganisation. Costing in `paper/sections/v9-plan.md` (whose census figures are stale — see below). Plan C signposting applied instead, at a disclosed cost of one page |
| R10 | tex↔md numeric residuals | **DIAGNOSED ONE AT A TIME AND PARTLY CLOSED** (139). Was 8 occurrences over 7 distinct tokens; **3 closed**, **5 remain over 4 distinct tokens**. None was ever a content gap. Full per-token verdicts in `paper/sections/v11-residuals.md`; the inherited label "all formatting" was **wrong for the `9.0` pair** and was not applied |

## R10 — the residual ledger, per token

| token | side | was | now | verdict, re-derived at this HEAD |
|---|---|---|---|---|
| `0.05` | tex-only ×1 | open | **OPEN, irreducible** | The `\caption` of `\label{tab:holm}` (`paper.tex:3255–3256`). **Causation measured**, not inferred: deleting that caption takes tex 23 → 22 and balances md's 22 exactly. Markdown pipe tables have no caption construct. The caption's claim — *"At most three reach nominal α = 0.05 and none survives Holm"* — is restated in the sentence after the table in **both** markups |
| `3.0` | tex-only ×1 | open | **OPEN, irreducible** | The `\caption` of `\label{tab:T}` (`paper.tex:2554–2556`). Same measurement: deleting it takes tex 4 → 3 and balances md's 3. Both halves of the caption's claim are in the md prose in a **sharper** form (the weakest `t` 3.09, not the rounded `≥ 3.0` bar) |
| `39,172` | tex-only ×1 | open | **CLOSED (139)** | **One space.** `DRAFT-v4.md` wrote `F(39, 172)` where `paper.tex:1930` writes `F(39,172)`; the diff's thousands-group branch `\d{1,3}(?:,\d{3})+` has no optional space, so the spaced form registers no token. All three `F(39,172)` statements were always in both files — there was never a prose gap. Every other `F(a,b)` pair is spelled identically across the two files, so the md line was the sole convention violation. Fixed at `DRAFT-v4.md:1491`; measured tex 2 / md 2 |
| `0.087` | md-only ×1 | open | **OPEN, justified** | One shared cause with the two below: a single md line, `DRAFT-v4.md:2674`, quoting `c88_scorers.py`'s printed dict in an **inline single-backtick span**. `paper.tex:3414–3418` carries the identical dict inside `\begin{quote}`, which `norm_tex` strips as quoted scorer output; `norm_md` strips fences, 4-space indents and `>` blocks but **not** inline backtick spans. **Causation measured**: deleting those three md lines (`:2673–2675`) takes `0.087` 10 → 9, `0.279` 8 → 7, `3.19` 2 → 1 — each landing exactly on the tex count. A pure exclusion asymmetry between the two normalisers |
| `0.279` | md-only ×1 | open | **OPEN, justified** | as above |
| `3.19` | md-only ×1 | open | **OPEN, justified** | as above |
| `9.0` | md-only ×2 | open | **CLOSED (139)** | **NOT a formatting artefact, and the inherited label was refused.** No normaliser was involved: `DRAFT-v4.md` printed `box −30:9.0` in two `rl3` rows of §4.7's `T` table and `paper.tex` did not. That is a difference in what the two tables print. **But no claim diverged** — the clip box for those two rungs is in Table 2 rows 6/7 of both markups and both markups' `T`-table footnote points there. Closed on the **tex** side (`paper.tex:2564`, `:2568`), adding the annotation rather than deleting a true one from the md. Measured tex 24 / md 24 |

- **The optional `E4`** (fencing the md's inline dict to match the tex's display block) **was declined.** It
  would close the last three, but it is cosmetic, it rewrites a prose line into a code block that the
  authors did not ask for, and §1.4–1.6 of `paper/sections/v11-residuals.md` justifies the three on their
  own. The alternative `E2` (stripping the box from the md rows) was also declined — it deletes a true
  annotation from the markup that has it.
- **`paper_numeric_diff.py` will keep exiting 1**, because the two captions are irreducible.
  **Read this check by its printed list, not by its exit code.** A shrinking list makes it tempting to
  expect exit 0; exit 0 is not reachable without inventing caption prose for Markdown pipe tables.
- **The printed context is the FIRST occurrence, not the extra one.** `quantities()` uses
  `ctx.setdefault`, and a multiset difference cannot identify *which* occurrence is surplus. Every
  causal claim in the table above was established by deleting the candidate site and re-counting —
  never by reading the printed context, which is misleading for all five surviving residuals.

## Census history — a printed claim that was wrong twice

| triple | why it moved |
|---|---|
| 628 / 409 / 892 / **45.9%** | the `_FENCE` masking bug: one mask swallowed 16.9% of the draft, so the denominator was measured on a manuscript with a sixth of it invisible |
| 628 / 411 / 978 / **42.0%** | CORRECTIONS 136 fixed the shared `re.S`; coverage ticked **down** and was reported, not absorbed |
| **628 / 411 / 982 / 41.9%** | CORRECTIONS 137's R2/R4 prose added four distinct quantity-numerals; re-iterated to a **fixpoint** in two passes. **Held through cycles 115 and 116** |

- `paper/sections/v9-plan.md` still prints the pre-136 figures (`892`, `45.9%`) and the sentence *"the
  asserted census stays at 892"*. **STALE.** Any future census simulation must run against **982**.
  Left unedited: it is a superseded planning document, and its Plan C conclusion (no quantities added,
  so the triple does not move) proved correct — only its printed denominator is wrong.
- Three checks must be run every cycle, not two: **`analysis/xref_check.py`** (cycle 113 — and the check
  that mattered most in cycle 116, since Plan C added 51 cross-references), **`analysis/test_fence_mask.py`**
  (CORRECTIONS 136 regression pin), and **`analysis/paper_numeric_diff.py`** read by its list.

## Deposit

| | |
|---|---|
| built from | commit **`2f4fd9a`**, **from a genuinely clean checkout** — the README's build stamp carries no DIRTY suffix. This is the first deposit since CORRECTIONS 138 for which that is true |
| verified | `make verify` **140 files, 0 bad** · cold `make reproduce` **ALL 547 CHECKS PASS** with **both** skips announced (`[7] BUDGET` — raw `hz3` `.out` series absent; `censuscheck` — the deposit ships no manuscript) · after `make logs`, `make reproduce` **ALL 628 CHECKS PASS** with only the `censuscheck` skip · `make clean` then `make verify` **140 / 0 bad**, restored to shipped state |
| census in `release/README.md` | **41.9%**, and it matches the paper — `README.md:34`, `paper.tex:1119`, `DRAFT-v4.md:880`, all three re-read. It shipped **45.9%** once (CORRECTIONS 138): the README interpolates `%(census)s` at build time, so a stale deposit prints a stale figure with no other symptom |
| `release/` | **gitignored** — a build product of `analysis/c98_release.py`, regenerated, never committed |

**A deposit is only as current as its last build.** It must be rebuilt once more at whatever commit is
actually submitted, and the README's coverage figure checked against the paper's. That is author item 4,
and it has already bitten once.

## TODO-FOR-AUTHOR — 7 open, all outside agent scope, each verified open at this HEAD

| # | item | evidence it is still open | effort |
|---|---|---|---|
| 1 | **CRediT ↔ Funding contradiction** — "Funding acquisition" on S. Salehkaleybar against a Funding statement reading *"no dedicated project funding and no grant"* | both strings present in **both** markups: `paper.tex:5136–5137` ("Funding\nacquisition", wrapped) + `:5115` / `DRAFT-v4.md:4139` + `:4119` | 1 min |
| 2 | **LIACS correspondence address** to replace the gmail of record | **4 sites, 2 per markup**: `paper.tex:56` (`\thanks`) and `:5169` (under `\paragraph{Correspondence.}` at `:5168`) / `DRAFT-v4.md:5` and `:4168`. The LIACS *affiliation* is already in the CRediT block; this is the address only | 2 min |
| 3 | **ORCIDs, both authors** | `grep -ci orcid` = **0** in `paper.tex`, **0** in `DRAFT-v4.md` | 5 min |
| 4 | **Deposit rebuild at the submission commit** | the on-disk deposit is only ever as current as its last build; the README's coverage figure must be checked against the paper's every time | 2 min (`python3 analysis/c98_release.py`) |
| 5 | **Mint the artefact DOI** | *"The deposit has no DOI, because it has not been deposited"* — `paper.tex:5048` / `DRAFT-v4.md:4054` — honest, not a stub | 5 min + upload |
| 6 | **Authorship for the §5.9 design originator** | Competing Interests names them as *"a researcher … who is not an author"* and calls the origination *"a substantial intellectual contribution rather than an acknowledgeable courtesy"* — `paper.tex:5106`, `:5109` / `DRAFT-v4.md:4110`, `:4113` | **decision, not edit** |

| 7 | **Refresh the 8 corpus numerals the ingest made stale, in BOTH markups, then re-run to a fixpoint** | `c98_reproduce.py` **exit 1, 8 CHECK(S) FAILED**; the same script on the pre-ingest CSV exits **0**. Census: rows **2177→2357**, admissible **1735→1915**, wallclock **2162→2342**, GPU-h **1642→1805.4**. Substantive: best R18/C10 arm **93.317→93.328** (`i3b-3e4`→`eb1-a06`), deficit **1.807→1.796**, partition-family rows **431→434** / Lion **419→422** | 15 min |

- Items 1–5 are mechanical. **Item 6 is an ethics decision only the authors can make, and it must be
  settled before submission** — the paper's own Competing Interests says so.
- **Item 7 is new this cycle and is the only one an agent created.** It is author scope solely because
  the fix edits `paper/DRAFT-v4.md` and `paper/paper.tex`. **No scientific claim reverses**: the
  baseline is unmoved at **95.124 (se 0.047)** and the deficit is still ~1.8 pp. Edit the pair together
  and re-run `c98_reproduce.py` to a fixpoint — CORRECTIONS 141.6.
- **Do not delegate 1, 2, 3 or 6.** End matter, CRediT, funding, correspondence and the author list are
  the authors' by standing instruction.
- **The list is seven.** Item 7 was added this cycle; nothing was closed.

## Venue

| venue | fit | accept prob. (est.) | note |
|---|---|---|---|
| **TMLR** | **best** | **0.80** | No novelty bar, no length cap; "claims supported" + "of interest" both strongly met. The pre-registered self-reversal reaches the abstract |
| ReScience / MLRC | good | 0.60 | Strong reproduction framing; wants a tighter one-paper scope |
| NeurIPS D&B | fair | 0.30 | Corpus + deposit is a real artefact, but the paper is not framed as one |
| JMLR | fair | 0.25 | Length fine; wants methodological novelty, this is an audit |
| NeurIPS / ICML / ICLR main | poor | 0.15 | 9-page limit is fatal |

**Send to TMLR: YES**, after items 1–4 and a decision on 6. Path: fix 1–4 → settle 6 → rebuild the
deposit at the submission commit → arXiv → TMLR. Item 5 (DOI) can follow acceptance; the deposit is
commit-pinned and self-verifying.

## Standing

- `plateau5` PRIMARY; the CSV `plateau` column **BANNED** as primary.
- RULE 16 registered scorers run **unedited** · RULE 20 the ARGS line is the truth · RULE 21 scorer before batch · RULE 22 `dup_group` guard.
- **Ingest is `aggregate.py` THEN `args_repair.py --apply`** — `aggregate.py` alone silently reverts the `dup_group` repair and drops `ml2`'s `se` from 0.195 to 0.142.
- **Re-derive every number at write time. Never quote prose, including this dashboard.**
- Never fabricate an ORCID, affiliation, grant number or DOI.
- `release/` and `runs/` are gitignored build/data products.

## Open — re-derived at this HEAD, nothing carried forward unchecked

| # | item | state |
|---|---|---|
| 1 | **R10's three md-only residuals** (`0.087`, `0.279`, `3.19`) | **OPEN, JUSTIFIED.** One cause, one md line: an inline-backtick dict the tex sets in `\begin{quote}`. Causation measured. Optional fix `E4` exists and was declined as cosmetic |
| 2 | **R10's two irreducible residuals** — the `tab:holm` and `tab:T` `\caption`s | **OPEN BY DECISION.** Markdown pipe tables have no caption construct; both captions' claims sit in the adjacent prose of both markups. Closing them means writing new number-bearing prose into the markup the census reads, to satisfy a diff |
| 3 | **§4.8's budget table has no caption and no label** — `paper.tex:2810–2822` is an unfloated `center`/`tabular`; the md is a bare pipe table | **OPEN, RECORDED NOT CLOSED.** This is R2's *other* limb. CORRECTIONS 137 closed the `se` limb and did not mention this one; 137, 138 and the previous dashboard then all carried R2 as closed. Verified at this HEAD: no `\caption`, no `\label`. Acceptable as-is — nothing cross-references it and the following prose *"In the table, se is…"* does a caption's job in both markups — **but the record said fixed when it was not** |
| 4 | **`analysis/c98_reproduce.py` prints the section label `[15]` twice** — line 621 (partition-family meta-optimiser census) and line 987 (metric sensitivity) | **OPEN, NOT FIXED ON PURPOSE.** Registered audit machinery; the numbering is cosmetic; renumbering mid-cycle would churn 636 output lines. §1.2's evidence map deliberately cites neither. Rename to `[18]` at the next machinery change |
| 5 | **The abstract has no headroom, and the gate that measures it is not in this tree** | **OPEN, a standing hazard.** md 231 by plain count against a recorded 228 and a 230 cap. Any abstract edit must be gated, not counted |
| 6 | **A code comment now points at a section this rewrite deleted** — `analysis/c98_reproduce.py:275` reads *"docs/STATUS.md R0 item 3 prints the upper limit as +0.299"* | **OPEN, NOT EDITED ON PURPOSE.** This dashboard no longer has an R0 section, so the comment is stale. It is a **comment inside registered audit machinery** and the assertion beside it re-derives 0.298 independently, so nothing is wrong with the check — but the pointer is dead. Fix at the next machinery change, not by editing the audit mid-cycle |

**CLOSED this cycle (139), with evidence — do not re-open:** Plan C signposting (applied; census
fixpoint held; `xref_check` green on 596 refs), R10's `39,172` (one space) and R10's `9.0` pair (a
real table-content difference, no claim divergence), and the §7 threat index, which said `T9–T12`
while `T13` exists inside *Limits of the review process*.

**CLOSED in earlier cycles — do not re-open:** the two `|`-leading md prose lines (138), §4.8's `se`
column (137), §4.8's opening over-scoping (138), the ALICE staging dirs (138 — re-verified by
read-only `ssh` at this HEAD, both gone), the §9 companion-sentence question (138 — decided **NO**),
R4 (137), R8 (138).
