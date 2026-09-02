# v4 package: **false-claims** — A1, A2, A6, A8

Closes A1 (the ρ superlative), A2 (the deposit guarantee), A6 (the two `gn1` scorer
misstatements) and A8 (the verification gap that let A1 through).

**Do not apply anything in this file by judgement.** Every replacement below is keyed to a
DRAFT-v3 heading and quotes the exact string it replaces. Numbers are re-derived here, not
carried from any briefing; the derivation is shown for each one.

**One file outside `paper/sections/` was edited by this package:**
`analysis/c98_reproduce.py` (item A8 mandates it). Nothing else was touched. No commit was made.

---

## 0. Evidence log — what was actually run, and its exact output

All commands were run from the repository root at HEAD `6a374f4`, unedited, with only their own
documented arguments.

| # | command | outcome |
|---|---|---|
| E1 | `python3 analysis/c98_figures.py --all --numbers` | exit 0; printed the sixteen-cell `rel` (= ρ) column reproduced in §1 below |
| E2 | `python3 analysis/c77_pp1_score.py` | exit 0; `0 probe dirs`, every arm `n=0 NO DATA`, `P1 cannot be scored`, `P2 ... cannot be scored`, `P5b cannot be scored` |
| E3 | `python3 analysis/c84_gn1_score.py` | **exit 1**; halts at `T0 VERDICT: 4 of 4 arms void or dropped` → `**THE WHOLE BATCH IS VOID.**`. It never prints T0.6 |
| E4 | `python3 analysis/c98_reproduce.py` **before** this package | exit 1, 51 `chk(` sites, 99 executed assertions, 93 PASS / 6 FAIL |
| E5 | `python3 analysis/c98_reproduce.py` **after** this package | 105 `chk(` sites, 188 executed assertions, coverage census printed. First run: exit 1, 183 PASS / 5 FAIL on stale §8 counts. Final run after a concurrent package moved those constants: exit 0, 188/188 PASS — see §5.1 |
| E6 | `c76_mm1`, `c78_bn1`, `c79_ar1`, `c81_cc1`, `c82_fa1`, `c83_gc1` | run unedited; see the register in §2 |
| E7 | `python3 analysis/c87_rl3_score.py --runs ../runs_alice2` | exit 0; prints §4.5's H3 block **in full** |
| E8 | `python3 analysis/c87_hz3_score.py --runs ../runs` | exit 0; prints §4.8's readings in full |

E3 is the single most important line in this package: **the paper says the `gn1` scorer halts at
its commensurability gate; run on the deposited tree it halts two gates earlier, at T0, with a
different message.** Both facts are now stated.

---

## 1. A1 — the ρ superlative is false

### 1.1 The derivation

`analysis/c98_figures.py --all --numbers`, unedited, prints one `rel` value per count-matched
cell, where `rel` is Eq. 9's ρ = D / (100 − aligned). Sorted ascending, the sixteen cells are:

| rank | cell | base | dataset | D (pp) | aligned | **ρ** |
|---|---|---|---|---|---|---|
| 1 | `aw1` | AdamW | C10 | +0.279 | 92.978 | **0.0397** |
| 2 | `gm2` | SGDm | **C100** | +1.485 | 70.569 | **0.0504** |
| 3 | `gc1` | SGDm | **C100** | +1.640 | 70.311 | **0.0552** |
| 4 | `ml2` | SGDm | C10 | +0.456 | 92.064 | 0.0574 |
| 5 | `hz3` | SGDm | C10 | +0.428 | 92.816 | 0.0595 |
| 6 | `mm1` | SGDm | C10 | +0.485 | 92.044 | 0.0610 |
| 7 | `pp1` | SGDm | C10 | +0.581 | 92.012 | 0.0727 |
| 8 | `gn1` (BN) | SGDm | C10 | +0.587 | 92.000 | 0.0734 |
| 9 | `g3m` | SGDm | C10 | +0.666 | 91.336 | 0.0768 |
| 10 | `rl3` @3e-4 | SGDm | C10 | +0.591 | 92.507 | 0.0789 |
| 11 | `fa1` | SGDm | C10 | +0.629 | 92.327 | 0.0820 |
| 12 | `rl3` @1e-4 | SGDm | C10 | +0.681 | 91.908 | 0.0842 |
| 13 | `r50` | SGDm | C10 | +0.881 | 89.631 | 0.0850 |
| 14 | `cc1` | SGDm | C10 | +0.727 | 91.890 | 0.0896 |
| 15 | `nl1` (SGD) | SGD | C10 | +1.035 | 91.156 | 0.1171 |
| 16 | `nl1` (RMSProp) | RMSProp | C10 | +0.973 | 92.155 | 0.1241 |

Three facts follow, and all three are now asserted by `c98_reproduce.py --rho`:

1. The cell §4.3 names — the +1.640 pp CIFAR-100 cell, `gc1` — has ρ = 0.055 and is the **third
   smallest of sixteen**, not the smallest. Two cells are smaller.
2. One of the two smaller cells is **the other CIFAR-100 cell**, `gm2` at ρ = 0.050. So the
   superlative is not merely wrong about the corpus; it is wrong about CIFAR-100.
3. The half of the sentence that *is* true is the half that carries the argument: `gc1`'s +1.640 pp
   **is** the largest D in the corpus (0 cells exceed it), and on ρ it falls below every CIFAR-10
   cell except `aw1` — 1 of the 14 CIFAR-10 cells is below it, and the CIFAR-10 median ρ is 0.078.
   The inversion the commensurability rule is built on survives intact.

**Do not replace one superlative with another.** The replacements below state the rank.

### 1.2 Replacement — §4.3, the paragraph beginning "**A commensurability warning we obey.**"

REPLACE:

> **A commensurability warning we obey.** A percentage point is not comparable across error budgets.
> ResNet-18/CIFAR-10 sits on a ≈7–8 pp budget and CIFAR-100 on ≈29–30 pp. On **relative** error
> reduction (Eq. 9) CIFAR-100's +1.640 pp is D/headroom = 0.055, the **smallest** value among the
> cells, not the largest. We therefore never average CIFAR-10 and CIFAR-100 D's, and never plot them
> on one axis.

WITH:

> **A commensurability warning we obey.** A percentage point is not comparable across error budgets.
> ResNet-18/CIFAR-10 sits on a ≈7–8 pp budget and CIFAR-100 on ≈29–30 pp. The two CIFAR-100 cells
> carry the two **largest** D in the corpus, +1.640 pp (`gc1`) and +1.485 pp (`gm2`). On **relative**
> error reduction (Eq. 9) they are ρ = 0.055 and ρ = 0.050 — the **third and second smallest of the
> sixteen**, above only `aw1`'s 0.040 and below every other CIFAR-10 cell, whose median ρ is 0.078.
> The pp ordering and the commensurable ordering are therefore close to inverted, which is why we
> never average CIFAR-10 and CIFAR-100 D's and never plot them on one axis.

*(Leave the following sentence — "The rule is worth something measurable … 4.52 on 7 df to 17.17 on
8 df" — exactly as it stands. It is correct: verified by `c98_reproduce.py --tail`, which prints
`+0.558 ± 0.055 with Q 17.17/8 instead of Q 4.52/7`.)*

### 1.3 Replacement — the Figure 1 caption, panel (b)

REPLACE:

> (b) The same sixteen contrasts as a share of the aligned arm's remaining error,
> ρ = D / (100 − aligned) (Eq. 9), which *is* commensurable. On that scale CIFAR-100's +1.640 pp is
> 0.055 — the **smallest** value in the corpus, not the largest. The inset
> gives the fixed-effect pool over the eleven cells that run the same ResNet-18 partition contrast.

WITH:

> (b) The same sixteen contrasts as a share of the aligned arm's remaining error,
> ρ = D / (100 − aligned) (Eq. 9), which *is* commensurable. The ordering changes: CIFAR-100's
> +1.640 pp, the **largest** D in panel (a), is ρ = 0.055 — the **third smallest of the sixteen**,
> behind `aw1` (0.040) and the other CIFAR-100 cell `gm2` (0.050). The inset
> gives the fixed-effect pool over the eleven cells that run the same ResNet-18 partition contrast.

### 1.4 A second, smaller false number found in the same subsection

§4.3's dagger footnote to row 9 says the 6 v 6 and 5 v 5 `hz3` readings differ by "0.027 pp".
Re-derived at full precision the difference is **+0.4552 − 0.42767 = 0.02753 → 0.028 pp**; 0.027
is what you get by subtracting the *rounded* table entries. In a paper whose header note (§0,
"Meta-analytic convention") makes exactly this distinction a stated convention, the wrong side of
it should not be printed.

REPLACE, in §4.3's dagger footnote:

> the difference being 0.027 pp against a 0.086 pp se

WITH:

> the difference being 0.028 pp at full precision (0.027 from the rounded table entries) against a
> 0.086 pp se

---

## 2. A2 — the deposit guarantee is false, and this is the fatal one

### 2.1 What running the scorers on the deposited tree actually does

`python3 analysis/c77_pp1_score.py`, unedited, exit 0, prints:

```
c77 -- pp1: THE THREE-WAY DECOMPOSITION OF mm1's +0.485.  0 probe dirs
    nodewise     m=14420    n=0  NO DATA
    permnode<S>  m=14420    n=0  NO DATA
    chunk777     m=14421    n=0  NO DATA
    **P0/P0.2 INCOMPLETE (0 dirs, expected 9) -- NOTHING BELOW IS SCORED.**
--- P2  **THE PRIMARY.  THE ALIGNMENT LEG. ...**
    NO DATA on at least one arm -- P2 cannot be scored.
```

§4.6 quotes that `P2` block verbatim, as an eight-line code fence, as the evidence for the
alignment null. A reader with the deposit cannot regenerate a single line of it.

Every registered scorer named in §3.4 was then run unedited. The result is a three-state register,
now carried in the code as `DEPOSIT_SCORERS` in `analysis/c98_reproduce.py` and printed by
`python3 analysis/c98_reproduce.py --deposit`:

| scorer | the paper quotes it for | on the deposit alone | why |
|---|---|---|---|
| `c76_mm1_score.py` | §4.3 `mm1` cell | **BLOCKED** | M1 cannot be scored; M0–M0.4 read 0/0 |
| `c77_pp1_score.py` | §4.6's `P2` block | **BLOCKED** | P1/P2/P5b all `NO DATA` |
| `c78_bn1_score.py` | §5.4's G at m = 4,851 | **BLOCKED** | every arm reads `n=0` |
| `c79_ar1_score.py` | §4.3's box-void **exclusion** | **BLOCKED** | A0.4 reads 0/0 — the ground of the exclusion is unreproducible |
| `c81_cc1_score.py` | §5.2's verbatim field block | **PARTIAL** | C2 `REPLICATES` / C3 `COLLAPSES` regenerate from the CSV; C1 and every `N_eff/m` in §5.2 do not |
| `c82_fa1_score.py` | §3.4's scorer list | **BLOCKED** | **exit 1**: `0 probe dirs. THAT IS ALWAYS A SYNC FAULT, NEVER A FINDING … Nothing scored.` |
| `c83_gc1_score.py` | §4.3 `gc1` cell | **PARTIAL** | S1 `CLOSE-CONFIRMED` regenerates; S0.4's arm-asymmetry guard does not run, and the scorer says so: *"S1 is reported WITHOUT its registered guard check and must carry that caveat"* |
| `c84_gn1_score.py` | §5.6, §7 T7 | **BLOCKED** | **exit 1** at the T0 verdict; never reaches T0.6 |
| `c87_rl3_score.py` | §4.5's H3 block | **REACHED** | `--runs <unpacked logs>`; no probe dependency |
| `c87_hz3_score.py` | §4.8's window | **REACHED** | `--runs <unpacked logs>`; no probe dependency |

**Two corrections to the record while I am here.** (i) §4.5 is *not* one of the blocked sections:
`c87_rl3_score.py --runs ../runs_alice2` reproduces §4.5's quoted H3 block in full, including
`D(ms=1e-4) = +0.681 se 0.126`, `dD = -0.090 se 0.178 t -0.51 (16 df)` and the `RULE 11 CLOSED`
verdict, from the `.out` logs the deposit ships. (ii) §4.3's *exclusion* of `ar1` — which the paper
presents as a discipline win — is itself unreproducible from the deposit, because the asymmetric
guard bind that voids the batch lives only in `probes_ar1`. That was not on anyone's list.

### 2.2 The three ways to make §8 true, priced

**Option 1 — ship the probes.** `probe*.jsonl` is ≈42 GB (the paper's own figure; not verifiable
offline from this machine, but consistent with the measured per-job figure recorded at CORRECTIONS
118/guard 5: `probes_ar1` is 1.1 GB over 12 dirs, i.e. **0.100 GB per job**, so ≈42 GB is ≈420
probe-carrying jobs). This makes the claim true and destroys three others: the deposit stops being
"≈6 MB in 137 files", `make verify` stops being an md5 sweep a laptop finishes, and "reproduces
every number … on a laptop in seconds" becomes a multi-hour transfer. **Cost ≈ 7,000× the current
deposit.** A narrowed variant — ship probes only for the eight batches whose verdicts the paper
quotes (`mm1` 6, `pp1` 9, `bn1` 9, `cc1` 12, `fa1` 24, `gc1` 8, `gn1` 24, `ar1` 12 = **104 jobs**)
— is ≈**10.4 GB** at the measured per-job figure. Still ≈1,700×.

**Option 2 — ship reduced probe summaries.** *This was tried and it failed, and the failure is in
the project record.* CORRECTIONS 110.1: a "pull just the small files" shortcut (**1.3 MB instead of
1.1 GB**, i.e. the `neg_counts.json`/`.npy` a scorer names in its own source) *"also failed — it
reaches `probe.jsonl` indirectly via `c52_boxfree.records()`"*, and the standing rule minted from
it reads *"a probe-reading scorer needs the FULL `probe_*` dirs incl. `probe.jsonl`"*.
`c82_fa1_score.py` prints that rule at the reader today. Making a kilobyte summary sufficient
therefore requires teaching `c52_boxfree.occupancy`/`records` — or every scorer's argument list — to
read it. **That re-mints the md5 of every scorer §3.4 pins**, and dissolves the one property the
titled contribution rests on: that the scorer was committed *before* the runs existed and was run
unedited. Buying reproducibility by editing the artefact whose un-editedness is the claim is not a
fix; it is the defect wearing the fix's clothes.

**Option 3 — replace the guarantee with an accurate statement, and make the accurate statement
machine-checkable.** Cost: zero GB, and it converts an unfalsifiable promise into a table a referee
can re-run.

### 2.3 The option taken, and why

**Option 3, with Option 2 adopted as a *forward* rule only.** The reasoning is not economy — it is
that Options 1 and 2 both cost more of this paper's actual contribution than they buy. Option 1
buys literal truth by making the "laptop in seconds" artefact claim false. Option 2 buys it by
editing the scorers, which is the one thing §3.4 and §6.2 promise was never done. Option 3 costs a
sentence and gains a check. A referee's objection to §8 is not "42 GB is missing" — that is
disclosed already, two lines later — it is *"you told me nothing needs it, and the first scorer I
ran needed it."* Deleting the false universal and printing the exact register answers that
objection completely.

For future batches the Option-2 discipline is right and is stated as such: a scorer registered from
now on ships a `--summary` path **at registration time**, so its deposit-reproducibility is part of
what was committed before the runs existed rather than retrofitted afterwards. That is a
recommendation in the paper, not a retroactive edit.

### 2.4 Replacement — End matter, **Data availability**

REPLACE:

> The archive is
> ≈6 MB, carries an md5 manifest for every file, and reproduces every number in this paper with
> `make reproduce` on a laptop in seconds, with no GPU and no dependency beyond `python3` and
> `matplotlib`. **No number in this paper requires data that is not in that deposit.** Two
> exceptions, stated because they are exceptions: the per-group β trajectories (`probe*.jsonl`,
> ≈42 GB) are excluded for size and are available from the authors on request, with the
> box-occupancy summaries derived from them carried in the run table's `beta_clip` column and in
> the scorers' printed output; and the twelve `sm3` runs quoted as a consistency check in §4.4,
> §5.4 and Appendix B are not yet ingested into the run table, which is why no claim rests on them.

WITH:

> The archive is
> ≈6 MB, carries an md5 manifest for every file, and re-derives every number `make reproduce`
> checks — the list is in §3.4 — on a laptop in seconds, with no GPU and no dependency beyond
> `python3` and `matplotlib`. **One class of number requires data the deposit does not carry, and
> we state exactly which.** The per-group β trajectories (`probe*.jsonl`, ≈42 GB) are excluded for
> size and are available from the authors on request. They are not a supplement: they are the input
> to the box-occupancy and meta-gradient-field gates inside the registered scorers, so a reader
> with the deposit alone regenerates **two** of the ten scorer verdicts we quote in full
> (`c87_rl3`, §4.5; `c87_hz3`, §4.8), **two** in part (`c81_cc1`'s D and G legs but not §5.2's
> field block; `c83_gc1`'s S1 but not its arm-asymmetry guard), and **six** not at all — including
> §4.6's `P2` alignment block, §5.6/§7 T7's `gn1` halt, and the box-occupancy evidence that
> **excludes** `ar1` in §4.3. `python3 analysis/c98_reproduce.py --deposit` prints that register
> and its counts. Everything else the deposit reproduces without the probes: `results/all_runs.csv`
> and the raw `.out` series carry every arm mean, every D, G, U, T and ρ, every pool and every Q in
> this paper.

**Note on what the replacement drops.** The old paragraph's second "exception" — the twelve `sm3`
runs "not yet ingested into the run table" — is **deleted deliberately, not lost**: `sm3` was
ingested at commit `6a374f4` and `grep -c '^sm3' results/all_runs.csv` returns **12**. Leaving it
in would print a third false statement in the same paragraph.

### 2.5 Replacement — §8, "**One command.**"

REPLACE:

> **One command.** The deposit reproduces every number in this paper:

WITH:

> **One command.** The deposit re-derives and asserts the numbers that carry a claim in this paper;
> §3.4 states that scope exactly and `make reproduce --census` measures it:

### 2.6 Addition — §8, immediately after the `**Code.**` paragraph

INSERT a new paragraph:

> **What the deposit does not let you re-run, stated as a table rather than as a caveat.** Ten
> registered scorers are quoted or relied on in this paper. Run unedited against the deposit alone,
> two reach their quoted verdict in full, two reach part of it, and six halt or print `NO DATA`,
> because their box-occupancy and meta-gradient-field gates read the excluded `probe*.jsonl`.
> `python3 analysis/c98_reproduce.py --deposit` prints which is which and why, and
> `python3 analysis/c77_pp1_score.py` on the deposit tree prints `0 probe dirs` and
> `P2 ... cannot be scored` — we would rather a referee find that in this paragraph than at a
> terminal. The rule we adopt going forward, and recommend: **a scorer registered from now on ships
> a `--summary` input path at registration time**, so that its deposit-reproducibility is part of
> what was committed before the runs existed. Retrofitting one onto the scorers already quoted here
> would re-mint every md5 in the provenance table of this section and destroy the very property —
> committed-before-the-data, run unedited — that makes those quotes worth anything.

---

## 3. A6 — the two `gn1` misstatements

### 3.1 What the scorer really does

Two different things are true at two different trees, and the paper conflates them.

**(a) On the deposited tree** (`python3 analysis/c84_gn1_score.py`, no probes): **exit 1**, halting
at

```
--- T0 VERDICT: 4 of 4 arms void or dropped (bn-node, bn-ch, gn-node, gn-ch)
    -> **THE WHOLE BATCH IS VOID.**  Registered in advance.
    T3.1: a VOID GN cell is NOT EVIDENCE OF ANYTHING. ...
```

because T0.5, the box-occupancy gate, reports `0 probe dirs, box-free on 0 -> NO PROBE -- cannot be
gated` on all four arms and `VOID_ARMS = 2` is met. **T0.6 is never reached and the string "NO
TRANSFER VERDICT IS ISSUED" is never printed.** The paper's sentence "its scorer halts before
computing either contrast" is true; "its pre-registered commensurability gate fired" is not true of
this invocation.

**(b) On the full tree** (`--root ../runs_alice2/gn1`, the documented argument, probes present):
T0.5 passes (`rec_lo = rec_hi = 0.0000` on all four arms), and T0.6 fires. That run is the one the
paper is quoting, and it is legitimate under RULE 16 — `--root` is a documented argument, not an
edit. The paper simply never says which invocation produced the verdict, and §8 asserts the
deposit is sufficient, so a reader reasonably runs (a) and gets a different halt with a different
message.

**(c) The COMM_MAX misstatement.** From the source, `COMM_MAX = 2.0` with the comment
"`|mean plateau5 over the GN arms - mean over the BN arms|`", and the gate is
`comm_ok = abs(gap_lvl) <= COMM_MAX`. The gated quantity is a **level difference in percentage
points**, not a ratio. Re-derived from the CSV (n = 8 BN runs, n = 16 GN runs, `plateau5`, dup-group
collapsed):

| quantity | value |
|---|---|
| BatchNorm level (bn-node + bn-ch, n = 8) | **92.293** → budget **7.707 pp** |
| GroupNorm level (gn-node + gn-ch, n = 16) | **89.431** → budget **10.569 pp** |
| **the gated quantity**: GN level − BN level | **−2.862 pp** |
| registered bar `COMM_MAX` | **2.0 pp** |
| exceedance | **0.862 pp** |
| budget ratio 10.569 / 7.707 (printed alongside; **not** the gate) | **1.371×** |

So "the gate fired on a 1.37× error-budget ratio … registered bar 2.0 pp" compares a dimensionless
ratio with a bar in percentage points. It fired because **|−2.862| > 2.0 pp**. All six quantities
are now asserted by `c98_reproduce.py --gn1gate`.

### 3.2 Replacement — §7, T7 (first sentence through "…halts before computing either contrast")

REPLACE:

> `gn1` was the designated separator and
> **issued no verdict**: its pre-registered commensurability gate fired on a 1.37× error-budget
> ratio between the BatchNorm and GroupNorm halves (7.707 pp against 10.569 pp, registered bar
> 2.0 pp), and its scorer halts before computing either contrast.

WITH:

> `gn1` was the designated separator and
> **issued no verdict**. Its pre-registered commensurability gate T0.6 tests the **difference in
> level** between the two halves against a bar of 2.0 pp: the BatchNorm arms sit at 92.293
> (error budget 7.707 pp) and the GroupNorm arms at 89.431 (budget 10.569 pp), a difference of
> **−2.862 pp**, which exceeds the bar by 0.862 pp. (The scorer also prints the budget *ratio*,
> 1.37×, next to that line; the ratio is descriptive and is not the gated quantity.) The gate fires
> before either contrast is computed and the scorer stops there.

### 3.3 Addition — §7, T7, immediately after the sentence above

INSERT:

> Two invocations of that scorer must be distinguished, because §8's deposit does not carry the
> input the second one needs. Run with `--root` pointed at the batch's own run directory — probes
> present, the invocation whose output we quote — `c84_gn1_score.py` passes T0.5 with
> `rec_lo = rec_hi = 0.0000` on all four arms and then fails T0.6 as above. Run against the
> deposited tree, where `probe*.jsonl` is excluded, it never reaches T0.6: T0.5 reports
> `0 probe dirs … NO PROBE -- cannot be gated` on all four arms, `VOID_ARMS = 2` is met, and the
> scorer exits at `T0 VERDICT: 4 of 4 arms void or dropped → THE WHOLE BATCH IS VOID`. Both halts
> refuse a GroupNorm contrast, but they are different refusals for different reasons, and a reader
> reproducing from the deposit will see the second. §8 says which scorers this affects.

### 3.4 Replacement — §4.3, the `gn1`-GroupNorm exclusion sentence

REPLACE:

> Its
> registered scorer's commensurability gate fired (BatchNorm error budget 7.707 pp against GroupNorm's
> 10.569 pp, ratio 1.37×, registered bar 2.0 pp)

WITH:

> Its
> registered scorer's commensurability gate fired: the two halves sit 2.862 pp apart in level
> (BatchNorm 92.293, error budget 7.707 pp; GroupNorm 89.431, budget 10.569 pp) against a
> registered bar of 2.0 pp on that difference

### 3.5 Replacement — Appendix B, the `§` footnote

REPLACE:

> the registered scorer's commensurability gate fired at a 1.37× error-budget ratio and
> issued no verdict (§7 T7)

WITH:

> the registered scorer's commensurability gate fired on a 2.862 pp difference in level against its
> 2.0 pp bar, and issued no verdict (§7 T7)

### 3.6 Replacement — §3.4, the `c84_gn1_score.py` clause

REPLACE:

> and `c84_gn1_score.py`
> (md5 `82c515d1ad490228ecb20f83288a510f`), **which halted `gn1` at its commensurability gate and
> issued no verdict; we report that outcome rather than the contrast it declined to compute
> (§5.6, §7 T7).**

WITH:

> and `c84_gn1_score.py`
> (md5 `82c515d1ad490228ecb20f83288a510f`), **which halted `gn1` at its commensurability gate T0.6 —
> a 2.862 pp difference in level against a 2.0 pp bar — and issued no verdict; we report that
> outcome rather than the contrast it declined to compute (§5.6, §7 T7). Run instead against the
> deposit, which excludes the probe files, the same scorer halts one gate earlier and for a
> different reason (§7 T7, §8).**

---

## 4. A8 — the audit now asserts what it claims to assert

### 4.1 What was wrong

`analysis/c98_reproduce.py` had **51 `chk(` sites**, executing 99 assertions, against a manuscript
containing 1,602 decimal numerals. It checked **no ρ at all**, which is the entire reason A1
survived two review cycles: A1 is a claim about a *ranking*, and the audit checked neither the
values nor the ranking. Meanwhile the header and §3.4 said it "re-derives every number in the text
and asserts it against what is printed here."

### 4.2 What was done — **both** halves of the choice offered

Coverage was extended substantially **and** the claim was narrowed to the truth, because either one
alone still leaves a mismatch: extending coverage to 100% of 1,602 numerals is not achievable
(many are quotations from scorer output, section labels, or software versions), and narrowing the
claim without extending coverage would have left ρ unchecked.

Six new sections were added to `analysis/c98_reproduce.py`:

| flag | what it now asserts |
|---|---|
| `--rho` | ρ for all sixteen cells, **and the rank of each named cell** — the check that catches A1. Nine assertions. |
| `--gn1gate` | T0.6's two levels, two budgets, the gated **difference**, `COMM_MAX`, the exceedance, the ratio, and T7's ten-cell drop pool. Twelve assertions. |
| `--countaxis` | all twelve cells of §4.2's U table with se, the sign count, max \|U\|, the banned six-run `ml2` reading, and the five-rung `ck1` ladder with its ascent and t. Thirty-three assertions. |
| `--tuning` | §4.1's η pair — both arms, both rungs, both differences, both t, and the two "better at 1e-4 by" figures. Sixteen assertions. |
| `--appendices` | Appendix A.4's printed-table pools *and* their full-precision counterparts (43.01/36.29 vs 43.19/36.40), §7 T9's hz3 5 v 5 reading, and the ml2 6 v 6 se and t the paper names as wrong. Nine assertions. |
| `--deposit` | the ten-scorer deposit-reachability register of §2.1, with its REACHED/PARTIAL/BLOCKED counts. Three assertions. |

Plus a **coverage census** (`--census`, and printed at the end of every full run) which counts the
draft's numerals mechanically and reports the fraction this script asserts, so §3.4's number can
never drift from the code again. Its filter is stated in the source and reproduces the gate's own
raw figure of 1,602 exactly.

### 4.3 The honest new coverage figure

| | before | after |
|---|---|---|
| `chk(` sites in the file | 51 | **105** |
| assertions executed in a full run | 99 | **188** |
| PASS / FAIL | 93 / 6 | **188 / 0** |
| distinct quantity-numerals asserted | — | **147 of 579 (25.4%)** |
| exit status | 1 | 0 — but see §5.1, this is now *too* green |

The 579 denominator is 1,602 raw numerals minus code blocks and indented verbatim scorer output
(327), minus section/table/figure/equation labels, arXiv ids and software versions (156), reduced
to distinct strings. **25.4% is the true figure and the paper must print it, not "every number".**

### 4.4 Replacement — the draft header, second sentence

REPLACE:

> Every number in this document was re-derived from `results/all_runs.csv` and from the
> raw per-epoch `.out` series at the time of writing, under the admissibility gate
> `window_ok == 1 AND complete == 1 AND plateau5 present`, and is asserted against what this text
> prints by `analysis/c98_reproduce.py`, which exits non-zero if any headline fails to reproduce.

WITH:

> Every number in this document was re-derived from `results/all_runs.csv` and from the
> raw per-epoch `.out` series at the time of writing, under the admissibility gate
> `window_ok == 1 AND complete == 1 AND plateau5 present`. The numbers that carry a claim — the
> corpus counts, every cell of Table 2, the commensurable ratio ρ **and its ranking**, the pools and
> their heterogeneity partition, the alignment legs, T, U, the tail decomposition, the budget ladder
> and the competitiveness deficit — are additionally *asserted* against what this text prints by
> `analysis/c98_reproduce.py`, which exits non-zero if any of them fails. That audit executes 188
> assertions covering 147 of the 579 distinct quantity-numerals in this manuscript;
> `python3 analysis/c98_reproduce.py --census` prints that count and how it is computed. **It is
> not a claim that every numeral is machine-checked, and §3.4 says what is outside it.**

### 4.5 Replacement — §3.4, final paragraph

REPLACE:

> Every figure in this paper is generated by `analysis/c98_figures.py` directly from
> `results/all_runs.csv` and the raw `.out` series; `--numbers` prints each plotted value,
> and `analysis/c98_reproduce.py` re-derives every number in the text and asserts it
> against what is printed here. **No figure contains a value that was typed.**

WITH:

> Every figure in this paper is generated by `analysis/c98_figures.py` directly from
> `results/all_runs.csv` and the raw `.out` series; `--numbers` prints each plotted value.
> **No figure contains a value that was typed.**
>
> `analysis/c98_reproduce.py` re-derives and asserts the numbers that carry a claim, and we state
> its scope rather than let "the audit passes" be read as coverage. It asserts: the corpus and
> admissibility counts (§8); every cell of Table 2 with its standard error and the count of
> positive cells; the commensurable ratio ρ of Eq. 9 for all sixteen cells **and the rank of each
> cell we name** (§4.3); the eleven- and twelve-cell pools, τ, and the within/between-base Q
> partition (§4.4); the alignment legs A and B and the additivity identity (§4.6); the prescription
> table T (§4.7); the tail decomposition D = G + (D − G) and its pools (§5.4); the count axis U and
> the `ck1` ladder (§4.2); the meta-stepsize pair (§4.1); the budget ladder read within run from the
> raw series (§4.8); the competitiveness deficit (§7 T4); the `gn1` commensurability gate's levels,
> budgets and gated difference (§7 T7); Appendix A.4's printed-table pools; and the deposit
> reachability register of §8. It does **not** assert: prose-only quantities, group counts, the
> attrition ledger's upstream cluster-side rows, wallclock and byte counts, Appendix B's arm means,
> or any value that exists only inside a registered scorer's own printed output — those are quoted
> from the scorer, not re-derived. Measured by
> `python3 analysis/c98_reproduce.py --census`, the audit executes **188 assertions covering 147 of
> the 579 distinct quantity-numerals** in this manuscript (1,602 decimal numerals before removing
> quoted scorer output, cross-reference labels and software versions). We print the fraction rather
> than a superlative because a superlative is exactly the kind of claim this audit exists to catch:
> the first version of it checked no ρ, and a false ρ superlative survived two review cycles in
> §4.3 as a result.

### 4.6 The run, pasted

`python3 analysis/c98_reproduce.py`, exit **0**, 188/188 PASS. Full output is 288 lines; the
unchanged sections [2]–[8] are elided at the marked point. **Read §5.1 before trusting the [1]
CORPUS block**: those eight expectations were changed from the draft's printed values to the
derived ones by a *concurrent* package while this one was running.

```
==============================================================================
REPRODUCTION AUDIT -- results/all_runs.csv
==============================================================================

[1] CORPUS  (§8 Reproducibility, Appendix A.8)
  rows in results/all_runs.csv                   2173 | paper 2173 | PASS   abstract, §8
  admissible rows                                1724 | paper 1724 | PASS   §3.3, A.8
  runs carrying a wallclock                      2150 | paper 2150 | PASS   §8
  GPU-hours                                      1625 | paper 1625 | PASS   abstract, §8
  distinct nodes                                 29 | paper 29 | PASS   §8
  rows failing window_ok                         425 | paper 425 | PASS   §3.3 attrition
  rows failing complete                          24 | paper 24 | PASS   §3.3 attrition
  rows with no plateau5                          25 | paper 25 | PASS   §3.3 attrition

  ... sections [2] TABLE 2, [3] HETEROGENEITY, [4] ALIGNMENT, [5] PRESCRIPTION,
      [6] TAIL, [7] BUDGET, [8] COMPETITIVENESS -- unchanged, all PASS ...

[9] COMMENSURABLE RATIO rho = D / (100 - aligned)  (Eq. 9, §4.3, Fig. 1b)
   1  aw1            AdamW    C10    D +0.279  aligned  92.978  rho 0.0397
   2  gm2            SGDm     C100   D +1.485  aligned  70.569  rho 0.0504
   3  gc1            SGDm     C100   D +1.640  aligned  70.311  rho 0.0552
   4  ml2            SGDm     C10    D +0.456  aligned  92.064  rho 0.0574
   5  hz3            SGDm     C10    D +0.428  aligned  92.816  rho 0.0595
   6  mm1            SGDm     C10    D +0.485  aligned  92.044  rho 0.0610
   7  pp1            SGDm     C10    D +0.581  aligned  92.012  rho 0.0727
   8  gn1 (BN)       SGDm     C10    D +0.587  aligned  92.000  rho 0.0734
   9  g3m            SGDm     C10    D +0.666  aligned  91.336  rho 0.0768
  10  rl3 @3e-4      SGDm     C10    D +0.591  aligned  92.507  rho 0.0789
  11  fa1            SGDm     C10    D +0.629  aligned  92.327  rho 0.0820
  12  rl3 @1e-4      SGDm     C10    D +0.681  aligned  91.908  rho 0.0842
  13  r50            SGDm     C10    D +0.881  aligned  89.631  rho 0.0850
  14  cc1            SGDm     C10    D +0.727  aligned  91.890  rho 0.0896
  15  nl1 (SGD)      SGD      C10    D +1.035  aligned  91.156  rho 0.1171
  16  nl1 (RMSProp)  RMSProp  C10    D +0.973  aligned  92.155  rho 0.1241
  rho, gc1 (the CIFAR-100 cell §4.3 names)       0.055 | paper 0.055 | PASS   §4.3, Fig. 1 caption
     its RANK from the bottom, of 16             3 | paper 3 | PASS   §4.3 rewrite -- NOT 'the smallest'
  rho, the actual smallest (aw1)                 0.040 | paper 0.040 | PASS   §4.3 rewrite
  rho, gm2 -- the OTHER CIFAR-100 cell           0.050 | paper 0.050 | PASS   §4.3 rewrite
     gm2's rank from the bottom                  2 | paper 2 | PASS   §4.3 rewrite
  largest D in pp is gc1's                       +1.640 | paper +1.640 | PASS   §4.3 (the half that IS true)
     cells with a larger D                       0 | paper 0 | PASS   §4.3
  median rho over the 14 CIFAR-10 cells          0.078 | paper 0.078 | PASS   §4.3 rewrite
  CIFAR-10 cells with rho below gc1's            1 | paper 1 | PASS   §4.3 rewrite

[10] THE gn1 COMMENSURABILITY GATE  (c84_gn1_score.py T0.6; §4.3, §7 T7)
  BatchNorm level, n=8                           92.293 | paper 92.293 | PASS   §7 T7 (derived)
     its error budget                            7.707 | paper 7.707 | PASS   §4.3, §7 T7
  GroupNorm level, n=16                          89.431 | paper 89.431 | PASS   §7 T7 (derived)
     its error budget                            10.569 | paper 10.569 | PASS   §4.3, §7 T7
  **the gated quantity**: level difference       -2.862 | paper -2.862 | PASS   §4.3 + §7 T7 rewrite -- THIS is what meets COMM_MAX
     COMM_MAX, the registered bar (pp)           2.0 | paper 2.0 | PASS   c84 source, §4.3, §7 T7
     |difference| exceeds the bar by             +0.862 | paper +0.862 | PASS   §4.3 + §7 T7 rewrite
  the budget RATIO (printed, NOT the gate)       1.371 | paper 1.371 | PASS   §4.3 + §7 T7: quoted as 1.37x
  T7's ten-cell pool, gn1 (BN) dropped too       +0.570 | paper +0.570 | PASS   §7 T7
     se                                          0.038 | paper 0.038 | PASS   §7 T7
     Q                                           36.39 | paper 36.39 | PASS   §7 T7
     df                                          9 | paper 9 | PASS   §7 T7

  ... [11] COUNT AXIS U (33 assertions, all PASS), [12] TUNING AXES (16, all PASS),
      [13] APPENDIX A.4 + T9 (9, all PASS) ...

[14] WHAT THE DEPOSIT ALONE LETS A REGISTERED SCORER DO  (§8, End matter)
    scorer           quoted for                     state     note
    c76_mm1_score.py §4.3 mm1 cell                  BLOCKED   M1 cannot be scored; M0-M0.4 read 0/0 (0 probe dirs)
    c77_pp1_score.py §4.6 alignment null P2         BLOCKED   P1/P2/P5b NO DATA -- §4.6's verbatim block is unreachable
    c78_bn1_score.py §5.4 G at m=4,851              BLOCKED   every arm reads n=0 (0 probe dirs)
    c79_ar1_score.py §4.3 the box-void exclusion    BLOCKED   A0.4 reads 0/0 -- the ground of the exclusion is unreproducible
    c81_cc1_score.py §5.2 field concordance         PARTIAL   C2 REPLICATES / C3 COLLAPSES regenerate; C1 and every N_eff/m in §5.2 do not
    c82_fa1_score.py §3.4 scorer list               BLOCKED   exits 1: '0 probe dirs ... Nothing scored.'
    c83_gc1_score.py §4.3 gc1 cell                  PARTIAL   S1 CLOSE-CONFIRMED regenerates; S0.4's arm-asymmetry guard does not run
    c84_gn1_score.py §5.6 / §7 T7                   BLOCKED   exits 1 at the T0 VERDICT (T0.5 ungateable) -- never reaches T0.6
    c87_rl3_score.py §4.5 the RULE-11 closure       REACHED   --runs <unpacked logs>; no probe dependency
    c87_hz3_score.py §4.8 the budget window         REACHED   --runs <unpacked logs>; no probe dependency
  registered scorers REACHED on the deposit      2 | paper 2 | PASS   §8 + End-matter rewrite (A2)
     PARTIAL                                     2 | paper 2 | PASS   §8 + End-matter rewrite (A2)
     BLOCKED by the excluded probe files         6 | paper 6 | PASS   §8 + End-matter rewrite (A2)

==============================================================================
ALL 188 CHECKS PASS.
==============================================================================

==============================================================================
COVERAGE CENSUS -- paper/DRAFT-v3.md
==============================================================================
  every /\d+[.]\d+/ in the file                         1602  (678 distinct)
  ...minus code blocks and indented verbatim scorer
     output (numbers the SCORERS print, not ours)       1275  (590 distinct)
  ...minus section, table, figure and equation labels,
     arXiv ids and software versions  = QUANTITIES      1119  (579 distinct)
  chk() assertion sites executed in this run             188
  distinct quantity-numerals this run asserts            147
  coverage of distinct quantity-numerals                25.4%
  **This script asserts the numbers that carry a claim, not every
    numeral the draft prints.  §3.4 states that scope; do not widen it
    in prose without widening it here.**
```

---

## 5. New problems found, and NOT closed by this package

### 5.1 **URGENT for the integrator: the audit is now green while §8 is still wrong**

The five failures this package's first run surfaced were real and were caused by commit `6a374f4`
(the `sm3`/`sm4`/`bm2`/`rp1` ingest, 2,113 → 2,173 rows). They were the strengthened audit doing
its job: the paper prints 2,113 rows and the file holds 2,173.

**While this package was running, a concurrent package changed those five expectation constants in
`analysis/c98_reproduce.py` from the draft's printed values to the derived ones** (`2113→2173`,
`1671→1724`, `2098→2150`, `1582→1625`, `complete 17→24`). The audit consequently now exits **0**
with 188/188 PASS. **The draft has not moved with it.** At the time of writing,
`grep -n "2,113" paper/DRAFT-v3.md` still returns six sites — the abstract (line 28), §3.3 (lines
453, 459), §4.3 (786), §8 **Data** (1875), §8 Table 3 (1904) — plus `1,671` at 459/1908, `2,098` at
1904/1954, `1,582` at 28/1954 and `−17` at 1907.

That is the A8 defect running in the opposite direction and it is worse than the original: an audit
that prints ALL CHECKS PASS while the manuscript prints a different number is a stronger false
assurance than one that fails loudly. **Either the paper-side edits below land in the same commit
as those constants, or the constants must be reverted.** Do not ship a green audit against a
manuscript that says 2,113.

The five paper-side replacements, all derivable from the deposit:

| §8 / abstract string | replace with | derivation |
|---|---|---|
| `2,113 runs` / `2,113 rows` (abstract L28, §3.3 L453 L459, §4.3 L786, §8 L1875, Table 3 L1904, End matter) | `2,173` | `wc -l results/all_runs.csv − 1` |
| `**1,671**` admissible (§3.3 L459, Table 3 L1908) | `**1,724**` | `window_ok AND complete AND plateau5` |
| `2,098 carry a wallclock` (Table 3 L1904, §8 L1954) | `2,150` | non-empty `wallclock_min` |
| `1,582 GPU-hours` / `1,582.2` (abstract L28, Table 3 L1904, §8 L1954) | `1,625` / `1,624.8` | Σ`wallclock_min` / 60 |
| `− \`window_ok = 1\`, \`complete = 0\` \| −17` (Table 3 L1907) | `−24` | rows with `complete != 1` |
| `17 of 2,113 runs pass window_ok while having completed under 95%` (§3.3 L453) | `24 of 2,173` | same |

The jump in `complete` failures from 17 to 24 is **exactly the seven `rp1` runs still in flight**:
all 24 `rp1` rows are ingested while the batch was 17/24 complete, so seven carry `complete = 0`.
They are inadmissible and enter no contrast. (`sm3` 12 + `sm4` 12 + `bm2` 12 + `rp1` 24 = 60 new
rows, matching 2,173 − 2,113 exactly.)

**Table 3's upstream rows cannot be repaired offline and must not be guessed.** The lines
`Slurm .out files on the two clusters 2,193`, `−4 infrastructure`, `2,189 entered the training
script`, `−64 crashed before epoch 1` and `−12 sm3 not ingested` are cluster-side counts. The
`sm3` line is now zero (it *is* ingested), and 2,189 − 64 = 2,125 ≠ 2,173, so the `.out` totals
have grown too with `sm4`/`bm2`/`rp1`. **This needs a fresh sweep of both clusters' `.out` trees
before Table 3 is reprinted**, and `c98_reproduce.py` does not and should not assert those rows.

### 5.2 `analysis/c98_release.py` repeats the over-claim

Line 301 of `analysis/c98_release.py` writes the deposit's own README with
`| code/c98_reproduce.py | the audit. Re-derives every headline and checks it |`, and line 193 of
the generated Makefile is the `make reproduce` target. **That file is outside this package's
mandate** (item (d) named only `analysis/c98_reproduce.py`) and was not edited. It should be
brought into line with §3.4's new scope sentence in the production package.

### 5.3 §4.5 was wrongly listed as probe-gated

The blocking-item list attributes §4.5's verbatim verdict to the excluded probes. It is not:
`c87_rl3_score.py --runs <logs>` reproduces §4.5's H3 block in full from the `.out` series the
deposit ships. The genuinely blocked verbatim sections are **§4.6, §5.2 and §5.6/T7**, plus §4.3's
`ar1` exclusion, which nobody had flagged. §2.4's replacement text says exactly that.

---

## 6. Integrator checklist

Apply in this order. Nothing here needs GPU, the cluster, or a decision.

- [ ] **§4.3** — swap the commensurability paragraph (§1.2 above).
- [ ] **§4.3** — swap the `gn1`-GroupNorm exclusion clause (§3.4 above).
- [ ] **§4.3** — swap `0.027 pp` → `0.028 pp at full precision (0.027 from the rounded table entries)` in the row-9 dagger (§1.4 above).
- [ ] **Figure 1 caption, panel (b)** — swap (§1.3 above).
- [ ] **§3.4** — swap the `c84_gn1_score.py` clause (§3.6 above).
- [ ] **§3.4** — swap the final paragraph (§4.5 above).
- [ ] **Draft header** — swap the second sentence (§4.4 above).
- [ ] **§7 T7** — swap the first sentence and insert the two-invocations paragraph (§3.2, §3.3 above).
- [ ] **§8** — swap "**One command.**" lead-in (§2.5 above); insert the new paragraph after "**Code.**" (§2.6 above).
- [ ] **End matter, Data availability** — swap (§2.4 above).
- [ ] **Appendix B `§` footnote** — swap (§3.5 above).
- [ ] `analysis/c98_reproduce.py` is **already edited** in the working tree. Do not re-apply.
- [ ] **DO THIS OR REVERT — see §5.1.** The corpus-count constants in `c98_reproduce.py`'s `corpus()` were already moved to the derived values by a concurrent package. Apply the matching paper-side edits of §5.1 in the **same commit**, or revert those five constants. A green audit against a manuscript that still prints 2,113 is a worse defect than the one this package was sent to fix. Table 3's upstream rows need a cluster sweep first and stay unasserted.
- [ ] Re-run `python3 analysis/c98_reproduce.py` and confirm the only remaining failures are the ones you have deliberately left open.
