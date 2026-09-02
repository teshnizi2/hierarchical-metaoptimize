# PACKAGE `new-results` — folding `sm4` and `bm2` into the paper

**Scope.** Two registered scorers have been run **unedited** (STANDING RULE 16) and their verdicts
are folded in: `analysis/c97_sm4_score.py` (the second-moment corner) and
`analysis/c97_bm2_score.py` (the base-moderator replication). Everything below is either a verbatim
scorer line or a number re-derived at write time from `results/all_runs.csv` at HEAD `6a374f4`
(2,173 rows, 1,724 admissible). **Nothing is quoted from prose, including the briefing that
commissioned this package.**

This file is a patch set. Each block gives an **ANCHOR** — text that appears exactly once in
`paper/DRAFT-v3.md` — and the **REPLACEMENT** for it. Apply them in order. `paper/DRAFT-v3.md` is
not edited here; other packages are editing it concurrently.

---

## 0. Provenance — what was actually run, and where

Both scorers' `--selftest` passes locally at HEAD (`c97_sm4_score.py`: `ALL SELFTESTS PASS`;
`c97_bm2_score.py`: `79/79 checks pass`). Neither scorer can score from the run table alone — both
read the runs' own `.out` files (RULE 20's ARGS gate) and the probe `probe.jsonl` occupancy records,
and the 2.6 GB of `sm4` + `bm2` run trees live only on the cluster. The scorers were therefore
**copied unmodified** to `/data1/salehkaleybars/metaopt/c97pkg/` together with their two registered
batch scripts and the current `results/all_runs.csv`, and executed there:

```
python3 analysis/c97_sm4_score.py --runs /data1/salehkaleybars/metaopt/runs \
                                  --probes /data1/salehkaleybars/metaopt/runs/sm4
python3 analysis/c97_bm2_score.py --root /data1/salehkaleybars/metaopt/runs/bm2
```

`--runs`, `--probes` and `--root` are the scorers' own documented arguments. Supplying them is not
editing the scorer (RULE 16). No job was submitted; the only cluster writes were into a scratch
directory that no analysis reads.

**Cross-check.** Every statistic the two scorers print was independently re-derived from
`results/all_runs.csv` with a Welch difference of arm means on `plateau5`, and every one agrees to
the printed precision. The relevant identities: `bm2`-SGD `+0.9780 ± 0.0858`, `bm2`-RMSProp
`+0.6313 ± 0.1492`, `sm4` D `+0.8893 ± 0.2285`, G `+0.2607 ± 0.0806`, U `+0.3593 ± 0.0737`,
T `+0.9880 ± 0.2308`; `sm4`'s 12-run mean `plateau5` `91.5668`; the `aw1`+`sm3` 24-run anchor
`93.1608`. The run table and the raw `.out` tree do not disagree anywhere in this package.

---

## 1. The two verdicts, verbatim

### 1.1 `sm4` — `analysis/c97_sm4_score.py`, run unedited

```
--- H0a  ARGS GATE (STANDING RULE 20) -- 12 .out ---
  CLEAN -- every run's own ARGS line matches the declared design, no repeated flag,
  no Lion attribute live.

--- H0c  OPERATING-POINT GATE ---
  ON ANCHOR. 12-run mean plateau5 91.567 against the AdamW+Lion anchor 93.161
  (-1.594 pp, bar 3.0). The cell is comparable.

--- H0b  BOX GATE ---   (all four arms, worst coord_lo 0.00000, worst coord_hi 0.00000)

--- H1  PRIMARY   D = chunk777 - nodewise (count-matched, m 14,421 vs 14,420) ---
  D = chunk777 - nodewise = +0.8893 +- 0.2285   t +3.89 (df 2.3, p 0.0494)   n 3v3
  95% CI [+0.4415, +1.3371]
  VERDICT: REFUTED. D >= +0.55 at the corner where BOTH the base and the meta carry a
  second-moment normaliser. Mechanism candidate 8 -- 'D shrinks wherever a second moment
  sits' -- is false, and the AdamW/RMSProp pattern in the corpus needs another explanation.
  This is a POSITIVE result and must be reported as one, not buried.
  anchors: aw1 +0.2787 +- 0.0873 | sm3 +0.1413 +- 0.0638 | AdamW+Lion pooled
  +0.2100 +- 0.0559  (BETWEEN-BATCH comparisons, NOT a pooled n)

--- H2  SECONDARY G = chunk2325 - nodewise1d (count-matched EXACTLY, m 4,851) ---
  G = chunk2325 - nodewise1d = +0.2607 +- 0.0806   t +3.23 (df 3.7, p 0.0358)   n 3v3
  95% CI [+0.1027, +0.4187]
  VERDICT: G PERSISTS. The exactly count-matched contrast stays resolved when the meta
  also carries a second moment, as it is under AdamW+Lion (aw1 +0.232, sm3 +0.296).
  G is base-dependent, not meta-dependent, at this corner.

--- H3  MECHANISM  D - G (within batch) ---
  D-G = +0.6287 +- 0.2423   t +2.59 (df 8)   95% CI [+0.1538, +1.1035]
  VERDICT: MECHANISM CONTRAST RESOLVED at |t| >= 2 (interval [+0.154, +1.104]). Under
  AdamW+Lion it is NOT resolved in either batch (aw1 +0.047, sm3 -0.155), so a resolved
  D-G here is a finding about the meta-optimiser.

--- H4  DESCRIPTIVE ONLY ---
  U = chunk2325 - chunk777 = +0.3593 +- 0.0737  t +4.88   [the COUNT axis in batch]
  T = nodewise1d - nodewise = +0.9880 +- 0.2308  t +4.28   [COUNT-CONFOUNDED by
      construction (0.4731 decades); NOT tail removal]

--- SCOPE, CARRIED WITH EVERY VERDICT ABOVE ---
  * at aw1's own meta-stepsize 1e-4, NOT at an RMSProp-meta optimum (no ms ladder exists
    under RMSProp meta -- this corpus has ZERO other RMSProp-meta runs).
  * ResNet18 / CIFAR-10 / 100 epochs / box -15:-2.3026 only.
  * NOT pooled with aw1 or sm3: different meta-optimiser, different batch.
  * plateau5 is PRIMARY; the CSV `plateau` column (last 20) is BANNED.
```

### 1.2 `bm2` — `analysis/c97_bm2_score.py`, run unedited

```
--- R0.5  BOX OCCUPANCY, measured on bm2's own probes (box -15:-2.3026) ---
    12 probe dirs, every one T 10000, rec_lo 0.0000, rec_hi 0.0000.

--- R1  THE PRIMARY: D' = plateau5(chunk777) - plateau5(nodewise), WITHIN batch ---
    D'_SGD   base SGD      +0.9780 +- 0.0858  t 11.40   3v3   -> REPLICATES
             R1b vs nl1 +1.0353: delta -0.0573 -> AGREES WITH nl1 WITHIN THE CROSS-BATCH OFFSET
    D'_RMS   base RMSProp  +0.6313 +- 0.1492  t  4.23   3v3   -> REPLICATES
             R1b vs nl1 +0.9733: delta -0.3420 -> AGREES WITH nl1 WITHIN THE CROSS-BATCH OFFSET

--- R2  TWO-BATCH MODERATOR LEVEL (CROSS-BATCH; carries the batch floor) ---
    SGD      nl1 +1.0353+-0.1085 | bm2 +0.9780+-0.0858 -> pool +1.0000 +- 0.0673  Q 0.172 on 1 df
             -> REPLICATED (Q <= 3.841)
    RMSProp  nl1 +0.9733+-0.2515 | bm2 +0.6313+-0.1492 -> pool +0.7204 +- 0.1283  Q 1.367 on 1 df
             -> REPLICATED (Q <= 3.841)

--- R3  THE WITHIN-BATCH BASE CONTRAST  dD' = D'_SGD - D'_RMS ---
    dD' +0.3467 +- 0.1721  t  2.01  -> AGREE WITHIN RESOLUTION
    (nl1's reading of the same contrast: +0.0620 +- 0.2739)
    band 0.40 is 1.46 x the planning se -- AGREE WITHIN RESOLUTION is NOT an equivalence
    claim and may not be written as 'identical'.

--- R5  what this batch may NOT say ---
    no G / tail statement (no nodewise1d, no chunk2325 arm here);
    no pooling of SGD with RMSProp; nl1 is combined with, never overwritten;
    nothing about AdamW, SGDm, GroupNorm, R34/R50, CIFAR-100, or any other budget.
```

Every sentence written below obeys R5. `bm2` is never given a G, never pooled across bases, never
allowed to overwrite `nl1`, never asked about AdamW, and R3 is never written as "identical".

---

## 2. Re-derivation ledger

All quantities below are inverse-variance (fixed-effect) pools with Cochran Q, computed with the
same `meta()` used by `analysis/c98_figures.py`; per-cell D, G, T, U are Welch differences of arm
means on `plateau5`, with `dup_group` collapsing applied exactly as `c98_figures.arm()` applies it.

### 2.1 New count-matched cells

| new cell | base | meta | D (pp) | se | t | n | aligned arm | ρ = D/headroom |
|---|---|---|---|---|---|---|---|---|
| `bm2` (SGD) | SGD | Lion | **+0.978** | 0.086 | 11.40 | 3 v 3 | 91.203 | 0.1112 |
| `bm2` (RMSProp) | RMSProp | Lion | **+0.631** | 0.149 | 4.23 | 3 v 3 | 92.507 | 0.0843 |
| `sm3` | AdamW | Lion | **+0.141** | 0.064 | 2.22 | 3 v 3 | 93.103 | 0.0205 |
| `sm4` | AdamW | **RMSProp** | **+0.889** | 0.228 | 3.89 | 3 v 3 | 90.785 | 0.0965 |

`sm3` is included because its twelve rows are now **in** the deposited run table (they were not when
DRAFT-v3 was frozen; the run table is 2,173 rows at `6a374f4` and `sm3` contributes twelve of
them). Under RULE 20 `sm3`'s science is what its `ARGS:` line says, and that line says AdamW + Lion:
it is an independent replicate of `aw1`, which is exactly how the `sm4` scorer treats it when it
computes its own registered anchors.

### 2.2 The same-contrast pool: 11 cells → 14

Adding `bm2`(SGD), `bm2`(RMSProp) and `sm3` to the eleven cells that run the byte-identical
ResNet-18 `nodewise` → `chunk777` contrast (`cc1`, `mm1`, `pp1`, `gn1`-BN, `rl3`@1e-4, `rl3`@3e-4,
`fa1`, `hz3`, `aw1`, `nl1`-SGD, `nl1`-RMSProp):

|  | 11 cells (DRAFT-v3) | **14 cells (this package)** |
|---|---|---|
| fixed-effect pool | +0.571 ± 0.037 | **+0.530 ± 0.029** |
| Cochran Q | 36.40 on 10 df, p 7.2e-5 | **102.47 on 13 df, p 5.5e-16** |
| DerSimonian–Laird τ | 0.203 pp | **0.295 pp** |
| rms measurement se | 0.152 pp | **0.143 pp** |
| I² | 72% | **87%** |

`sm4` is **not** in this pool: its own registered scope note forbids pooling it with `aw1` or `sm3`
(different meta-optimiser, different batch). It is a Table 2 row and nothing more.

### 2.3 The base-optimiser decomposition, recomputed on 14 cells

| base optimiser | cells | batches | pooled D (pp) | level Q | p |
|---|---|---|---|---|---|
| SGD | 2 | 2 | **+1.000 ± 0.067** | 0.172 / 1 | 0.678 |
| RMSProp | 2 | 2 | **+0.720 ± 0.128** | 1.368 / 1 | 0.242 |
| SGDm | 8 | 7 | **+0.556 ± 0.045** | 4.206 / 7 | 0.756 |
| AdamW (Lion meta) | 2 | 2 | **+0.189 ± 0.052** | 1.613 / 1 | 0.204 |

- within-base **Q = 7.36 on 10 df (p 0.691)**
- between-base **Q = 95.12 on 3 df (p 1.7e-20)**
- share = 95.12 / 102.47 = **92.8%** (was 88.4% on eleven cells)
- range across levels: **+1.000 / +0.189 = a factor of 5.3** (was 3.7)

The SGD and RMSProp level pools are `bm2`'s own registered R2 output, reproduced independently.
The AdamW level pool `+0.189 ± 0.052` is the inverse-variance pool of `aw1` and `sm3`; the `sm4`
scorer's `+0.2100 ± 0.0559` is the **6 v 6 concatenated-seed** reading of the same two batches,
which that scorer explicitly labels "not a pooled n for inference". Both are reported; the
meta-analysis uses the inverse-variance one, because that is the estimator every other level uses.

Sensitivities, for the same reason the eleven-cell version carried them:
- adding `ml2` as a fifteenth cell at its corrected se: pool +0.528 ± 0.029, Q 102.61 / 14,
  between-base 95.01 / 3, share **92.6%**
- keeping the withdrawn `gn1`-GroupNorm arm as a fifth level (D +0.202 ± 0.137): pool
  +0.515 ± 0.029, Q 107.97 / 14, between-base 100.61 / 4, share **93.2%**

### 2.4 The four-level 2 × 2, recomputed

| contrast | DRAFT-v3 (11 cells) | **this package (14 cells)** |
|---|---|---|
| momentum main effect | −0.587 ± 0.145 (z −4.04) | **−0.488 ± 0.080 (z −6.09)** |
| second-moment main effect | −0.169 ± 0.145 (z −1.16) | **−0.323 ± 0.080 (z −4.03)** |
| interaction | 0.215 ± 0.291 | **−0.087 ± 0.160 (z −0.54)** |
| D(RMSProp) − D(AdamW) | +0.694 ± 0.266 (t 2.61) | **+0.531 ± 0.138 (t 3.84)** |
| momentum-collapsed residual Q inside momentum-present | 12.17 / 8 | **34.64 / 9 (p 6.9e-5)** |

**This changes a conclusion**, and it must not be written down as if it did not. On eleven cells the
second-moment main effect was unresolved (z −1.16) and the paper drew the contrast between a
resolved momentum effect and an unresolved second-moment one. On fourteen cells **both** main
effects resolve. The two-level momentum collapse now removes only 61.1% of Q against the four-level
base partition's 92.8%, so the identified moderator is still *the base optimiser* and not momentum
alone — but the sentence "they agree on which component of the base optimiser is not the axis" is no
longer supported, and §5.5 below withdraws it.

### 2.5 The AdamW base at two meta-optimisers — the new structural finding

At a fixed AdamW base, fixed α₀ = 1e-3, fixed η = 1e-4, fixed box −15:−2.3026, fixed 100 epochs,
ResNet-18/CIFAR-10, three arms of three seeds each:

| statistic | AdamW + **Lion** (`aw1`, `sm3`; IV pool of 2 batches) | AdamW + **RMSProp** (`sm4`, 1 batch) | difference (cross-batch, labelled) |
|---|---|---|---|
| D | +0.189 ± 0.052 | **+0.889 ± 0.228** | **+0.700 ± 0.234 (z 2.99)** |
| G | +0.261 ± 0.065 | **+0.261 ± 0.081** | **−0.001 ± 0.104 (z −0.01)** |
| D − G | −0.061 ± 0.085 | **+0.629 ± 0.242** | **+0.690 ± 0.257 (z 2.69)** |
| T = `nodewise1d` − `nodewise` | +0.007 ± 0.056 | **+0.988 ± 0.231** | — |

**G is invariant to the meta-optimiser to three decimal places and the entire meta effect lands in
the size-1 tail component.** The two difference columns are **cross-batch comparisons and carry the
batch floor** — F(62,85) = 5.47, p 6.9e-13 — which neither pairing nor Welch removes, and they are
not registered tests. They are reported as labelled comparisons, which is exactly how the `sm4`
scorer reports its own anchors.

### 2.6 The G family under Holm — 12 → 14 tests

The pre-specified family was "the G leg of every Table 2 cell that has one". Two of the four new
Table 2 cells have a G (`sm3`, `sm4`); `bm2` has none, and R5 forbids inventing one. So the family
grows from twelve to fourteen. The **tabled twelve reproduce byte-for-byte**; the enlarged family:

| cell | G | se | t | df | p (Welch) | p Holm (14) | p (z) | p Holm z (14) |
|---|---|---|---|---|---|---|---|---|
| `nl1` (SGD) | +0.525 | 0.294 | 1.79 | 2.8 | 0.177 | 1.00 | 0.0741 | 0.667 |
| **`sm3` (AdamW)** | **+0.296** | 0.096 | 3.07 | 3.5 | **0.044** | 0.53 | 0.00213 | **0.028** |
| **`sm4` (AdamW, RMSProp meta)** | **+0.261** | 0.081 | 3.23 | 3.7 | **0.036** | 0.47 | 0.00122 | **0.017** |
| `aw1` (AdamW) | +0.232 | 0.089 | 2.62 | 3.5 | 0.067 | 0.74 | 0.00887 | 0.106 |
| `rl3` @3e-4 (SGDm) | +0.217 | 0.128 | 1.69 | 3.9 | 0.168 | 1.00 | 0.0913 | 0.731 |
| `ml2` (SGDm) | +0.173 | 0.073 | 2.38 | 4.0 | 0.076 | 0.76 | 0.0171 | 0.189 |
| `g3m` (SGDm, R34) | +0.171 | 0.073 | 2.34 | 16.0 | 0.033 | **0.46** | 0.0195 | 0.195 |
| `r50` (SGDm, R50) | +0.153 | 0.314 | 0.49 | 3.9 | 0.653 | 1.00 | 0.627 | 1.00 |
| `gm2` (SGDm, C100) | +0.068 | 0.069 | 0.99 | 3.5 | 0.386 | 1.00 | 0.322 | 1.00 |
| `nl1` (RMSProp) | +0.020 | 0.049 | 0.41 | 3.4 | 0.710 | 1.00 | 0.686 | 1.00 |
| `cc1` (SGDm) | +0.011 | 0.147 | 0.08 | 2.4 | 0.944 | 1.00 | 0.938 | 1.00 |
| `fa1` (SGDm) | −0.001 | 0.076 | −0.01 | 9.8 | 0.993 | 1.00 | 0.993 | 1.00 |
| `rl3` @1e-4 (SGDm) | −0.011 | 0.087 | −0.12 | 2.1 | 0.913 | 1.00 | 0.902 | 1.00 |
| `hz3` (SGDm, 300 ep) | −0.057 | 0.061 | −0.93 | 6.2 | 0.389 | 1.00 | 0.354 | 1.00 |

On the **Welch** degrees of freedom — the convention the paper adopts because the normal
approximation is anti-conservative at 2–4 df — **nothing survives Holm at fourteen either**
(smallest adjusted p 0.46, `g3m`). On the normal approximation `sm3` (adjusted p 0.028) and `sm4`
(adjusted p 0.017) **do** survive, which is a change: at twelve, no tabled cell survived on either
convention. Enlarging the family to fifteen with `bn1` (which yields a G and no D): on Welch,
`bn1` reaches adjusted p 0.10 and nothing else moves; on z, `bn1` (1.2e-8), `sm4` (0.017) and
`sm3` (0.028) survive.

Family heterogeneity: twelve-cell G pool +0.067 ± 0.023, Q 18.21 / 11 (p 0.077); **fourteen-cell
G pool +0.093 ± 0.022, Q 28.25 / 13 (p 0.0084)** — the enlarged family *is* heterogeneous where the
tabled twelve was not, and the two cells that make it so are the two new AdamW-base ones.

### 2.7 Corpus census for T1

The draft's "367 of 367 partition-programme runs are meta = Lion" **could not be re-derived at write
time** under any definition of "partition-programme run" we could construct from
`results/all_runs.csv` (see §5, Integrator notes). This package therefore states the census under a
rule a reader can execute:

> A **partition-programme run** is a row of `results/all_runs.csv` whose `granularity` is
> `nodewise`, `nodewise1d`, `permnode*` or `chunk*`, **and** whose batch contains at least one
> `chunk*`, `permnode*` or `nodewise1d` arm — i.e. the batch is running a partition contrast rather
> than the granularity-ladder programme of §4.2.

Under that rule the corpus holds **354 partition-programme runs across 22 batches**: `ar1`, `aw1`,
`bm2`, `bn1`, `cc1`, `ck1`, `cx2`, `fa1`, `g3`, `gc1`, `gm2`, `gn1`, `hz3`, `ml2`, `mm1`, `nl1`,
`pp1`, `r50`, `rl3`, `rp1`, `sm3`, `sm4`. Of those, **342 are meta = Lion and 12 are meta = RMSProp**
— the twelve being `sm4`. Before `sm4` the count was 342 of 342.

### 2.8 Counts that move

| quantity | DRAFT-v3 | this package | derivation |
|---|---|---|---|
| count-matched Table 2 cells | 16 | **20** | + `bm2`(SGD), `bm2`(RMSProp), `sm3`, `sm4` |
| complete set of count-matched contrasts | 18 | **22** | 20 tabled + `gn1`-GroupNorm + `ar1` |
| cells with D > 0 | 16 / 16 | **20 / 20** | smallest is `sm3` +0.141 |
| cells resolved at t ≥ 3.0 | 15 / 16 | **18 / 20** | the two exceptions are `ml2` t 2.34 and `sm3` t 2.22 |
| candidate mechanisms | 8 | **9** | M9 is `sm4`'s pre-registered refutation |
| mechanisms refuted | 3 | **4** | M2, M3, M6, **M9** |
| meta-optimisers varied | 1 (Lion) | **2** (Lion, RMSProp) | `sm4` |
| base optimiser levels with ≥ 2 batches | 1 of 4 (SGDm) | **4 of 4** | `bm2` × 2, `sm3` × 1 |
| runs in the corpus | 2,113 | **2,173** | `wc -l results/all_runs.csv` − 1 |
| admissible runs | 1,671 | **1,724** | `window_ok=1 ∧ complete=1 ∧ plateau5` present |
| GPU-hours | ≈1,582 | **≈1,625** | Σ `wallclock_min` / 60; the 60 new rows add 43 h |

---

## 3. Replacement blocks

### 3.1 §3.5 — the heading and the batch table

**ANCHOR** (heading, line ~574):

```
### 3.5 Four pre-registered batches in flight
```

**REPLACEMENT:**

```
### 3.5 Four pre-registered batches: two scored, two still in flight
```

---

**ANCHOR:**

```
Three weaknesses this paper states about itself, and one experiment it declares was never run, are
addressed by four batches submitted while this draft was being written. **No result from any of
them enters any claim in this paper**; their registrations are stated here so that the decision
rules are on the record before the numbers are, and so that a reader can tell what this paper would
be entitled to say next and what it would not.
```

**REPLACEMENT:**

```
Three weaknesses this paper states about itself, and one experiment it declares was never run, are
addressed by four batches submitted while this draft was being written. Two of the four — `bm2`
and `sm4` — have since completed and been scored by running their registered scorers **unedited**,
and their verdicts are folded into §4.4, §4.7, §5.4, §5.5 and §7. Two — `rp1` and the `hz3` seed-5
trio — are not scored, and **no number from either enters any claim in this paper**. The
registrations are stated here in full regardless of outcome, so that the decision rules are on the
record ahead of the numbers, and so that a reader can check that the two verdicts we did read are
the ones we said we would read.
```

---

**ANCHOR** (the four-row table's body — replace the four data rows only, keeping the header):

```
| R1 | `rp1` | 24 | the alignment null's power **and** its permutation-seed confound (§4.6) | `analysis/c97_rp1_score.py` |
| R2 | `hz3` seed-5 trio | 3 | the budget cell's clip-box and GPU-class mismatch (§4.8, §7 T9) | `analysis/c87_hz3_score.py`, reused unedited |
| R3 | `bm2` | 12 | the base-optimiser moderator's single-batch SGD and RMSProp levels (§4.4) | `analysis/c97_bm2_score.py` |
| R4 | `sm4` | 12 | the second-moment corner the void batch of §6.1 failed to test | `analysis/c97_sm4_score.py` |
```

**REPLACEMENT:**

```
| tag | batch | jobs | what it repairs | registered scorer | status |
| R1 | `rp1` | 24 | the alignment null's power **and** its permutation-seed confound (§4.6) | `analysis/c97_rp1_score.py` | complete on disk, **not scored** |
| R2 | `hz3` seed-5 trio | 3 | the budget cell's clip-box and GPU-class mismatch (§4.8, §7 T9) | `analysis/c87_hz3_score.py`, reused unedited | **queued** |
| R3 | `bm2` | 12 | the base-optimiser moderator's single-batch SGD and RMSProp levels (§4.4) | `analysis/c97_bm2_score.py` | **SCORED — both levels REPLICATE (§4.4)** |
| R4 | `sm4` | 12 | the second-moment corner the void batch of §6.1 failed to test | `analysis/c97_sm4_score.py` | **SCORED — mechanism REFUTED (§5.5)** |
```

*(The table's header row gains a sixth column; the integrator must widen the `|---|` separator row
to six columns.)*

---

**ANCHOR** (the whole closing status paragraph of §3.5):

```
**Status at the time of writing, stated because "in flight" is not a uniform state.** `rp1` and
`sm4` are running; the R2 trio is queued behind a congested partition, and the original `hz3`
seed-3 and seed-4 runs waited 16 and 23 hours in the same queue, so a wait is expected rather than
anomalous. `bm2`'s twelve jobs have **completed**, 100/100 epochs each, after this draft's numbers
were frozen; it has not been scored, and it will be scored by running
`analysis/c97_bm2_score.py` unedited and quoting its verdict. We state that plainly rather than
letting a completed batch sit unmentioned: the reason no `bm2` number appears in this paper is a
freeze date and a registration, not a filter.
```

**REPLACEMENT:**

```
**Status, stated because "in flight" is not a uniform state.**

**R3 and R4 are done and are in the paper.** `bm2`'s twelve jobs and `sm4`'s twelve jobs completed
at 100/100 epochs each. Each was scored exactly as registered: the scorer file was run **unedited**,
with only its own documented `--root` / `--runs` / `--probes` arguments supplied, and its verdict is
quoted rather than paraphrased — `bm2`'s in §4.4, `sm4`'s in §5.5. Both scorers' ARGS gates (RULE 20)
returned CLEAN on the runs' own `ARGS:` lines, and both box gates were measured on the batches' own
probe records rather than inherited: `sm4`'s four arms and `bm2`'s twelve probe directories all
report `rec_lo` and `rec_hi` of exactly 0.0000 over T = 10,000 recorded steps, so neither batch
touched a clip rail.

**R1 is complete on disk and deliberately unscored.** All 24 `rp1` runs reach 100 epochs in their
own `.out` series. Seven of the twenty-four were ingested into `results/all_runs.csv` mid-flight and
their rows still carry the partial epoch counts of that snapshot, so the run table is behind the
disk for this batch. We have not run `analysis/c97_rp1_score.py`, and **no `rp1` number appears
anywhere in this paper**, including in §4.6 where it would matter most. The registration stands as
written, including the clause that binds us: if `rp1` returns an interval that still spans half of
D, the alignment leg is to be reported as **underdetermined**, not as a null.

**R2 is queued.** The three seed-5 jobs sit `PENDING` on the same congested partition on which the
original `hz3` seed-3 and seed-4 runs waited 16 and 23 hours, so a wait is expected rather than
anomalous. STANDING RULE 20's post-launch ARGS check is owed on them the moment they start.
```

### 3.2 §4.3 — Table 2 grows to twenty cells

**ANCHOR** (the last four table rows, to which the new rows are appended):

```
| 15 | gc1 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | −15:−2.3026 | 4 v 4 | **+1.640** | 0.245 | 6.71 |
| 16 | gm2 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+1.485** | 0.238 | 6.24 |
```

**REPLACEMENT:**

```
| 15 | gc1 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | −15:−2.3026 | 4 v 4 | **+1.640** | 0.245 | 6.71 |
| 16 | gm2 | ResNet-18 | **C100** | SGDm | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+1.485** | 0.238 | 6.24 |
| 17 | bm2 | ResNet-18 | C10 | **SGD** | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.978** | 0.086 | 11.40 |
| 18 | bm2 | ResNet-18 | C10 | **RMSProp** | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.631** | 0.149 | 4.23 |
| 19 | sm3 | ResNet-18 | C10 | **AdamW** | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.141** | 0.064 | 2.22 |
| 20§ | sm4 | ResNet-18 | C10 | **AdamW** | 1e-4 | 100 | −15:−2.3026 | 3 v 3 | **+0.889** | 0.228 | 3.89 |

§ **Row 20 is the only cell in this table whose meta-optimiser is not Lion.** `sm4` runs an
**RMSProp** meta-optimiser (§5.5, §7 T1); every other row in the table, and every other
count-matched contrast in the corpus, runs Lion. Its own registered scorer forbids pooling it with
`aw1` or `sm3`, so it enters no pool in §4.4 and appears here as a listed cell only. Rows 17 and 18
are `bm2`, the registered replication of §4.4's two single-batch levels at fresh seeds 3, 4, 5;
row 19 is `sm3`, which declared an RMSProp meta and ran Lion (§6.1) and is therefore an independent
replicate of `aw1` rather than the corner it was built for.
```

*(A `meta` column would be better than a footnote and the integrator may prefer to add one: every
row would read `Lion` except row 20, which reads `RMSProp`.)*

---

**ANCHOR:**

```
**D is positive in every cell.** Fifteen of the sixteen are resolved at t ≥ 3.0; the exception is
`ml2` at t 2.34, whose three independent seeds were run twice under two names.
```

**REPLACEMENT:**

```
**D is positive in every cell.** Eighteen of the twenty are resolved at t ≥ 3.0; the two exceptions
are `ml2` at t 2.34, whose three independent seeds were run twice under two names, and `sm3` at
t 2.22, which is the smallest D in the corpus (+0.141 ± 0.064) and sits at the same AdamW cell as
`aw1`.
```

---

**ANCHOR:**

```
**Table 2 together with the excluded `ar1` cell is the complete set of count-matched
`nodewise`-versus-uniform-chunk contrasts in this corpus. None is omitted, and the excluded one is
also positive.** We verified this by enumeration rather than by recollection: of the 2,113 runs,
every batch that ever ran a `nodewise` arm alongside a count-matched uniform-chunk arm is one of
these eighteen (the sixteen above, `gn1`-GroupNorm, and `ar1`), and every other batch carrying a
`nodewise` arm has no arm to match it against.
```

**REPLACEMENT:**

```
**Table 2 together with the excluded `ar1` cell is the complete set of count-matched
`nodewise`-versus-uniform-chunk contrasts in this corpus. None is omitted, and the excluded one is
also positive.** We verified this by enumeration rather than by recollection: of the 2,173 runs,
every batch that ever ran a `nodewise` arm alongside a count-matched uniform-chunk arm is one of
these twenty-two (the twenty above, `gn1`-GroupNorm, and `ar1`), and every other batch carrying a
`nodewise` arm has no arm to match it against.
```

---

**ANCHOR** (the ρ sentence in §4.3; note this text is also the subject of blocking item A1, which
this package does **not** close — see §5):

```
ResNet-18/CIFAR-10 sits on a ≈7–8 pp budget and CIFAR-100 on ≈29–30 pp. On **relative** error
reduction (Eq. 9) CIFAR-100's +1.640 pp is D/headroom = 0.055, the **smallest** value among the
cells, not the largest.
```

**REPLACEMENT:**

```
ResNet-18/CIFAR-10 sits on a ≈7–8 pp budget and CIFAR-100 on ≈29–30 pp. On **relative** error
reduction (Eq. 9) CIFAR-100's +1.640 pp is D/headroom = 0.055, which ranks **fourth of the twenty
cells from the bottom** rather than first: `sm3` reads 0.021, `aw1` 0.040 and `gm2` 0.050 below it.
The point the rule makes does not depend on the rank — the largest D in percentage points is not
the largest as a share of the error it can remove — but the superlative does, and it is wrong.
```

### 3.3 §4.4 — the moderator, now replicated at every level

**ANCHOR:**

```
Restrict Table 2 to the eleven cells that run the same ResNet-18 partition contrast
(`nodewise` → `chunk777`, count-matched to +1 group on 14,420; rows 1–4 and 6–12) so that the
contrast itself is held fixed. Those eleven are heterogeneous: the fixed-effect pool is
+0.571 ± 0.037 with

> **Q = 36.40 on 10 df, p = 7.2e-5**; DerSimonian–Laird **τ = 0.203 pp** against an rms measurement
> se of **0.152 pp**, i.e. I² = 72%.

That much the record already carried. What it did not carry is that **almost all of it is one
variable.** Split the eleven cells by the base optimiser, the axis §5.5 was already looking at:

| base optimiser | base state, from the runs' own `ARGS` line | cells | batches | pooled D (pp) |
|---|---|---|---|---|
| SGD | no momentum, no second moment | 1 | 1 | **+1.035 ± 0.109** |
| RMSProp | second moment 0.999, no momentum | 1 | 1 | **+0.973 ± 0.251** |
| SGDm | momentum 0.99, no second moment | 8 | 7 | **+0.556 ± 0.045** |
| AdamW | momentum 0.9 + second moment 0.999 | 1 | 1 | **+0.279 ± 0.087** |

**Between base optimisers, Q = 32.20 on 3 df (p = 4.8e-7) — 88% of the total.** The remaining 12%
is the within-SGDm residual, and it is not resolvable at all:
```

**REPLACEMENT:**

```
Restrict Table 2 to the fourteen cells that run the same ResNet-18 partition contrast
(`nodewise` → `chunk777`, count-matched to +1 group on 14,420; rows 1–4, 6–12, 17–19) so that the
contrast itself is held fixed. `sm4` (row 20) is **excluded from every pool in this section** by its
own registered scope note, which forbids pooling it with `aw1` or `sm3`; it runs a different
meta-optimiser and is treated in §5.5. Those fourteen are heterogeneous: the fixed-effect pool is
+0.530 ± 0.029 with

> **Q = 102.47 on 13 df, p = 5.5e-16**; DerSimonian–Laird **τ = 0.295 pp** against an rms
> measurement se of **0.143 pp**, i.e. I² = 87%.

What that heterogeneity is, is **almost entirely one variable.** Split the fourteen cells by the
base optimiser:

| base optimiser | base state, from the runs' own `ARGS` line | cells | batches | pooled D (pp) | within-level Q |
|---|---|---|---|---|---|
| SGD | no momentum, no second moment | 2 | 2 | **+1.000 ± 0.067** | 0.17 / 1 (p 0.68) |
| RMSProp | second moment 0.999, no momentum | 2 | 2 | **+0.720 ± 0.128** | 1.37 / 1 (p 0.24) |
| SGDm | momentum 0.99, no second moment | 8 | 7 | **+0.556 ± 0.045** | 4.21 / 7 (p 0.76) |
| AdamW | momentum 0.9 + second moment 0.999 | 2 | 2 | **+0.189 ± 0.052** | 1.61 / 1 (p 0.20) |

**Between base optimisers, Q = 95.12 on 3 df (p = 1.7e-20) — 92.8% of the total.** The remaining
7.2% is the within-level residual, **Q = 7.36 on 10 df (p = 0.69)**, and no level contributes a
resolvable share of it.

**Every level of this moderator now rests on at least two independent submissions.** That is new,
and it is the single most important thing `bm2` bought. The registered scorer
`analysis/c97_bm2_score.py`, run unedited on `bm2`'s own run tree, reports:

> `D'_SGD  base SGD  +0.9780 ± 0.0858  t 11.40  3v3  -> REPLICATES`
> `D'_RMS  base RMSProp  +0.6313 ± 0.1492  t 4.23  3v3  -> REPLICATES`
> `SGD      nl1 +1.0353±0.1085 | bm2 +0.9780±0.0858 -> pool +1.0000 ± 0.0673  Q 0.172 on 1 df -> REPLICATED`
> `RMSProp  nl1 +0.9733±0.2515 | bm2 +0.6313±0.1492 -> pool +0.7204 ± 0.1283  Q 1.367 on 1 df -> REPLICATED`

`bm2` is one submission of four arms at three **fresh** seeds (3, 4, 5 against `nl1`'s 0, 1, 2), at
`nl1`'s own cell read off `nl1`'s own `ARGS:` line. Independence is bought twice — a separate
submission, so the batch random effect is resampled, and fresh seeds, so the `ml2` failure mode
cannot recur. The `bm2` pools in the table above are the scorer's own R2 output; `nl1` is
**combined with** them and is not overwritten, and the two bases are **never pooled with each
other**, both of which the scorer's R5 forbids. The AdamW level's second batch is `sm3`, whose
twelve runs are now in the deposited run table and which — under RULE 20, on its own `ARGS:` line —
ran AdamW + Lion and is an independent replicate of `aw1` (§6.1).

**What `bm2` does and does not fix about the 88% figure.** The eleven-cell decomposition had a
structural weakness that arithmetic alone would have produced: three of its four levels were single
cells, contributing Q = 0 by construction, so `Q_within` was the eight SGDm cells and nothing else,
and `Q_between` was `Q_total − Q_SGDm` **identically, for any partition that isolated those three
cells**. The share was therefore label-invariant, and "88% is one identified moderator" claimed more
than the number could carry. On fourteen cells no level is a singleton: `Q_within` is 7.36 on 10 df,
of which 3.15 comes from the three non-SGDm levels, and the base partition is now a **restriction
the data could have rejected**. It did not reject it — all four levels are homogeneous
(p 0.20–0.76). That is the part `bm2` and `sm3` fix.

**What they do not fix.** The base optimiser is a *pre-specified* four-level axis, not the
best-fitting one. A four-way partition of the same fourteen cells chosen post-hoc by cutting the
cells in D order removes 97.5% of Q, and partitioning by batch identity — eleven levels on 10 df —
removes 95.8%. Neither is a competitor, because both are chosen on the outcome; they are quoted so
that "92.8%" is read as *this axis removes almost all of the heterogeneity*, not as *no other
partition could*. Two axes that are not chosen on the outcome remove essentially none of it:
β-box (three levels) 0.7%, meta-stepsize 1.2%, budget 1.5%.
```

---

**ANCHOR:**

```
So the finding is not "D varies for reasons we cannot attribute". It is:

> **At a fixed base optimiser, D is a constant.** Under SGDm it is +0.556 ± 0.045 pp and it does
> not move with the meta-stepsize, the budget, the β-box, the cluster or the batch. **Between base
> optimisers it moves by a factor of 3.7**, and that single axis accounts for 88% of the observed
> heterogeneity.

**Say which denominator.** The between-base Q of 32.20 is 88.4% of the eleven-cell Q of 36.40, which
is the pool the decomposition is computed on. Against the legacy twelve-cell Q of 43.19 — the pool
that contained the withdrawn GroupNorm cell — the same 32.20 is 74.6%. Both are true of different
denominators, and quoting the second without naming it is how "≈75%" reads as though the GroupNorm
cell were still in the partition, which it is not.
```

**REPLACEMENT:**

```
So the finding is not "D varies for reasons we cannot attribute". It is:

> **At a fixed base optimiser, D is a constant.** Under SGDm it is +0.556 ± 0.045 pp across seven
> submissions, two meta-stepsizes, two budgets, three β-boxes and two clusters; under SGD
> +1.000 ± 0.067 across two submissions; under RMSProp +0.720 ± 0.128 across two; under AdamW with
> a Lion meta +0.189 ± 0.052 across two. **Between base optimisers it moves by a factor of 5.3**,
> and that single axis accounts for **92.8%** of the observed heterogeneity.

**Say which denominator.** The between-base Q of 95.12 is 92.8% of the fourteen-cell Q of 102.47,
which is the pool the decomposition is computed on. The figure is not sensitive to the two cells
whose inclusion is arguable: adding `ml2` at its corrected se gives 92.6% (pool +0.528 ± 0.029,
Q 102.61 / 14), and restoring the withdrawn GroupNorm arm as a fifth level gives 93.2% (pool
+0.515 ± 0.029, Q 107.97 / 14). The corresponding figure on DRAFT-v3's eleven cells was 88.4%, and
against the legacy twelve-cell pool that contained the GroupNorm cell it was 74.6% — the "≈75%"
that earlier drafts quoted. All are true of different denominators; none may be quoted without
naming its own.
```

---

**ANCHOR:**

```
**What we may not conclude from the direction.** The four levels happen to arrange themselves as a
2 × 2 in the base optimiser's own state: the two levels whose base carries **no momentum term**
(SGD, RMSProp) sit at ≈ +1.0, and the two that carry one (SGDm, AdamW) sit at ≈ +0.28…+0.56. As
contrasts, a momentum main effect of **−0.587 ± 0.145 (z −4.04)** against a second-moment main
effect of **−0.169 ± 0.145 (z −1.16)**, with an interaction whose magnitude is 0.215 ± 0.291 and which the design
cannot resolve. This is consistent with §5.5, which kills second-moment normalisation as the axis
on the independent RMSProp-versus-AdamW contrast. **We register it as a prediction, not a result**,
for four reasons, and a referee should hold us to all four:

1. **Three of the four levels rest on one batch each.** Only SGDm is replicated (7 batches).
2. **SGD and RMSProp are not independent of each other:** they are the two halves of a single
   submission, `nl1` (job ids 4832408–4832431, one node pool). D is a within-batch contrast, so a
   batch-level offset cancels inside each half — but a batch × partition interaction peculiar to
   `nl1` would move both levels together, and nothing in this corpus would see it. This is strictly
   worse than "one design point per level".
3. **The momentum coefficients are not matched** (0.99 under SGDm, 0.9 under AdamW), so "momentum
   present/absent" is a two-point contrast in a continuous parameter.
4. **Momentum alone is not sufficient.** Collapsing the four levels to momentum-present /
   momentum-absent leaves a residual Q of 12.17 on 8 df inside the momentum-present group — the
   SGDm-to-AdamW gap survives the collapse. The identified moderator is *the base optimiser*, not
   any single component of it.

**R3 (`bm2`, §3.5) is exactly the experiment this weakness names**: a second, independent batch at
the SGD and RMSProp bases with fresh seeds, which would replicate the moderator at three of four
levels and break the `nl1` co-dependence. Until it is scored, "the base optimiser is a moderator of
D" is a within-corpus decomposition of eleven measurements, **not an out-of-sample prediction rule**
— which is why it does not contradict §5.8, where the predictors under test are continuous
properties of a configuration and the unit is the design point. It should also be read against §3.4:
`nl1` is one of the five batches with no scorer registered before its runs existed, so the two
levels doing the most work here are the two with the least procedural protection.
```

**REPLACEMENT:**

```
**What we may not conclude from the direction.** The four levels arrange themselves as a 2 × 2 in
the base optimiser's own state: the two levels whose base carries **no momentum term** (SGD,
RMSProp) sit at +1.000 and +0.720, and the two that carry one (SGDm, AdamW) at +0.556 and +0.189.
As contrasts on the four level pools, the momentum main effect is **−0.488 ± 0.080 (z −6.09)** and
the second-moment main effect **−0.323 ± 0.080 (z −4.03)**, with an interaction of
−0.087 ± 0.160 (z −0.54) that the design cannot resolve.

**Both main effects now resolve, and that is a change from the eleven-cell reading**, where the
second-moment effect was −0.169 ± 0.145 (z −1.16) and we drew a contrast between a resolved
momentum effect and an unresolved normalisation one. With `bm2` and `sm3` in the pools that
contrast is gone. What survives is that neither component *alone* is the moderator: collapsing the
four levels to momentum-present / momentum-absent removes 61.1% of Q against the four-level
partition's 92.8%, and leaves a residual Q of **34.64 on 9 df (p 6.9e-5)** inside the
momentum-present group — the SGDm-to-AdamW gap survives the collapse. **The identified moderator is
*the base optimiser*, not any single component of it.**

**We still register the 2 × 2 as a prediction, not a result**, for three reasons, and a referee
should hold us to all three:

1. **Each of the three non-SGDm levels rests on two batches, not more.** Two is enough to make the
   level's homogeneity testable — it passes at all three (Q 0.17, 1.37, 1.61 on 1 df) — and not
   enough to estimate a between-batch variance component at that level.
2. **The momentum coefficients are not matched** (0.99 under SGDm, 0.9 under AdamW), so "momentum
   present/absent" is a two-point contrast in a continuous parameter.
3. **`bm2` may not be asked about AdamW.** Its own registered scorer's R5 forbids `bm2` any
   statement about the AdamW, SGDm or GroupNorm bases, about ResNet-34/50, about CIFAR-100, or
   about any other budget. Everything above that involves AdamW is carried by `aw1` and `sm3`.

**What is no longer a weakness.** DRAFT-v3 stated here that three of four levels rested on one batch
each, that SGD and RMSProp were the two halves of a single submission `nl1` so that a batch ×
partition interaction peculiar to `nl1` would move both levels together with nothing in the corpus
able to see it, and that R3 was the experiment which would fix it. R3 ran. `bm2` is a separate
submission at fresh seeds, and it moves neither level outside its registered replication band. The
`nl1` co-dependence is broken: a batch × partition interaction peculiar to `nl1` would have to be
reproduced, at both bases and in the same direction, by an independently submitted batch, and the
between-batch spreads are −0.057 (SGD) and −0.342 (RMSProp) against a registered agreement band of
0.5. What remains true, and is worth keeping, is that this is a **within-corpus decomposition of
fourteen measurements, not an out-of-sample prediction rule** — which is why it does not contradict
§5.8, where the predictors under test are continuous properties of a configuration and the unit is
the design point. It should also be read against §3.4: `nl1` is one of the five batches with no
scorer registered before its runs existed, whereas `bm2` had one before any of its runs could
exist.

**The within-batch base contrast, and a phrase we may not use.** `bm2` also reads the SGD-minus-
RMSProp difference inside its own batch, which `nl1` could also do. The scorer's R3 verdict:
`dD' +0.3467 ± 0.1721, t 2.01 -> AGREE WITHIN RESOLUTION`, against `nl1`'s reading of the same
contrast, +0.0620 ± 0.2739. The scorer attaches the constraint in its own words — the agreement
band of 0.40 is 1.46× the planning standard error, so "AGREE WITHIN RESOLUTION is NOT an
equivalence claim and may not be written as 'identical'." We do not write it as identical. The two
momentum-free bases are not resolved apart by either batch, and neither batch is powered to say
they are the same.
```

---

**ANCHOR** (the stale `sm3` paragraph at the end of §4.4):

```
A second AdamW measurement exists but is not in the pool: `sm3` (§6.1) is void as designed and
salvageable only as an independent replicate of `aw1`, and its twelve runs are not yet ingested into
the run table. Re-derived from its raw `.out` series it reads D = +0.141 ± 0.064 against `aw1`'s
+0.279 ± 0.087, a replicate spread of +0.137 ± 0.108 (z 1.27). We report that as a consistency check
and do not pool it into Table 2 or into this decomposition, because a number that is not in the
deposited run table cannot be re-derived by a reader running `make reproduce`.
```

**REPLACEMENT:**

```
The second AdamW measurement is `sm3`, and it is now **in** the pool. `sm3` is void as designed
(§6.1) — it declared an RMSProp meta-optimiser and, after argparse's last-wins, ran Lion — and is
salvageable only as an independent replicate of `aw1`, which is exactly what it is used for here.
Its twelve rows are in the deposited run table, so a reader can re-derive them: D = +0.141 ± 0.064
against `aw1`'s +0.279 ± 0.087, a replicate spread of +0.137 ± 0.108 (z 1.27), pooling to
+0.189 ± 0.052 with Q = 1.61 on 1 df. The `sm4` scorer computes the same two-batch anchor its own
way, as a 6 v 6 concatenation of the seeds — D +0.2100 ± 0.0559 — and labels it, correctly, as a
between-batch comparison and **not a pooled n for inference**. We use the inverse-variance pool in
the table above because that is the estimator every other level in the table uses, and we report
both so the difference is visible rather than buried.
```

---

**ANCHOR** (Figure 2 caption):

```
**Figure 2 — the heterogeneity in D is a base-optimiser effect, not an unattributable one.**
(a) The eleven same-contrast ResNet-18 cells, grouped by base optimiser; each group's band is its
own inverse-variance pool ± 1.96 se. The eight SGDm cells — seven separate submissions, two
meta-stepsizes, two budgets and three clip boxes — are **homogeneous**: Q 4.21 on 7 df, p 0.76,
DerSimonian–Laird τ = 0.000, pooling to +0.556 ± 0.045. (b) Partitioning the eleven-cell Cochran Q
(Eq. 12): **32.20 of 36.40 (88%) is between base optimisers**, on 3 df, p 4.8e-7. (Against the
legacy twelve-cell Q of 43.19 that the withdrawn GroupNorm cell used to enter, the same 32.20 is
74.6% — the "≈75%" figure, whose denominator must always be named.) This is the figure that
replaces "for reasons we cannot attribute".
```

**REPLACEMENT:**

```
**Figure 2 — the heterogeneity in D is a base-optimiser effect, not an unattributable one, and
every level of the moderator is now replicated.** (a) The fourteen same-contrast ResNet-18 cells,
grouped by base optimiser; each group's band is its own inverse-variance pool ± 1.96 se. Every
level carries **two or more independent submissions** — SGD `nl1` + `bm2`, RMSProp `nl1` + `bm2`,
AdamW `aw1` + `sm3`, SGDm seven — and every level is homogeneous: Q 0.17 / 1, 1.37 / 1, 1.61 / 1
and 4.21 / 7 respectively. (b) Partitioning the fourteen-cell Cochran Q (Eq. 12): **95.12 of 102.47
(92.8%) is between base optimisers**, on 3 df, p 1.7e-20; the within-level remainder is 7.36 on
10 df, p 0.69. On DRAFT-v3's eleven cells the same partition read 32.20 of 36.40 (88.4%), and
against the legacy twelve-cell pool containing the withdrawn GroupNorm cell, 74.6% — the "≈75%"
figure. Every denominator must be named. `sm4` is **not** in this figure: it is the only
count-matched cell with a non-Lion meta-optimiser and its registered scorer forbids pooling it here.
```

### 3.4 §4.7 — the prescription's scope is a meta-optimiser scope, not a base scope

**ANCHOR** (last row of the T table):

```
| aw1 | R18 / C10 / **AdamW** | 3 v 3 | **+0.091** | 0.078 | 1.16 |
```

**REPLACEMENT:**

```
| aw1 | R18 / C10 / **AdamW**, Lion meta | 3 v 3 | **+0.091** | 0.078 | 1.16 |
| sm3 | R18 / C10 / **AdamW**, Lion meta | 3 v 3 | **−0.083** | 0.081 | −1.03 |
| sm4 | R18 / C10 / **AdamW**, **RMSProp meta** | 3 v 3 | **+0.988** | 0.231 | 4.28 |
```

---

**ANCHOR:**

```
The move costs nothing — it *reduces* the number of learned quantities from 14,420 to 4,851 — and
under an SGDm, SGD or RMSProp base it is worth **+0.328 to +1.363 pp** across ten within-batch
cells, every one resolved at t ≥ 3.3. **Under AdamW it is worth nothing measurable
(+0.091 ± 0.078, t 1.16).** That is the scope line, and §5.4 explains why it is where it is.

Decomposing T by Eq. 6 on `rl3` at η = 1e-4: T = +0.756 = 0.692 + 0.064. The **count**
component is 8% of the effect; the tail component is the rest. Any account that treats "merge the
1-D tensors" as a count reduction has the decomposition backwards.
```

**REPLACEMENT:**

```
The move costs nothing — it *reduces* the number of learned quantities from 14,420 to 4,851 — and
under an SGDm, SGD or RMSProp base it is worth **+0.328 to +1.363 pp** across ten within-batch
cells, every one resolved at t ≥ 3.3.

**The scope line is not where DRAFT-v3 put it.** Under an AdamW base with a **Lion** meta-optimiser
the move is worth nothing measurable, and that now rests on two independent batches rather than one:
`aw1` +0.091 ± 0.078 and `sm3` −0.083 ± 0.081, pooling to **+0.007 ± 0.056**. Under the **same AdamW
base with an RMSProp meta-optimiser** it is worth **+0.988 ± 0.231 (t 4.28)** — the largest T in the
CIFAR-10 corpus. So the exception is not "AdamW". It is "AdamW **with a Lion meta-optimiser**", and
one cell is all the evidence there is on the other side of that line. §5.5 develops what this does
to the mechanism story.

Two warnings travel with the `sm4` row, and both come from its own registered scorer, which classes
T as descriptive only. First, T is **count-confounded by construction**: it moves 0.4731 decades of
group count as well as removing the size-1 tail, so it is not a tail-removal measurement. Second,
that confound is not a constant share. Decomposing T by Eq. 6 on `rl3` at η = 1e-4 gives
T = +0.756 = 0.692 + 0.064, where the **count** component is 8% of the effect and the tail component
is the rest; the same decomposition on `sm4` gives T = +0.988 = 0.629 + 0.359, where the count
component is **36%**. Any account that treats "merge the 1-D tensors" as purely a count reduction has
the decomposition backwards, and any account that treats the count component as negligible has it
backwards at this cell.
```

### 3.5 §5 — nine candidates, four refuted

**ANCHOR:**

```
## 5. Eight candidate mechanisms — three refuted — and two nulls

This section is the second half of the contribution, not an appendix. Of the eight, **three are
refuted** (M2, M3, M6), **one is narrowed** to an SGDm base and remains alive there (M4), **one is
not separable** from the axes it is aliased with (M7), and **three cannot be decided by this
instrument or this design** (M1 untested, M5 inapplicable, M8 not identifiable). One refutation
rests on a gate registered before its data existed (M2); two are post-hoc contrasts on data
collected for other purposes (M3, M6). One further candidate, M1, had its literature attribution
withdrawn after we re-read the sources.
```

**REPLACEMENT:**

```
## 5. Nine candidate mechanisms — four refuted — and two nulls

This section is the second half of the contribution, not an appendix. Of the nine, **four are
refuted** (M2, M3, M6, M9), **one is narrowed** to a base–meta pairing rather than to a base
alone (M4), **one is not separable** from the axes it is aliased with (M7), and **three cannot be
decided by this instrument or this design** (M1 untested, M5 inapplicable, M8 not identifiable).
Two refutations rest on gates registered before their data existed (M2, M9); two are post-hoc
contrasts on data collected for other purposes (M3, M6). One further candidate, M1, had its
literature attribution withdrawn after we re-read the sources.

**M9 is the one refutation in this paper that was designed, registered, run and read in that
order.** Its bar — `REFUTED if D >= +0.55` — was committed in `bin/c97_sm4_secondmoment.sh` before
the batch was submitted, and it was cleared by a wide margin in the direction the mechanism said was
impossible. We report it as a positive result, which is what it is.
```

---

**ANCHOR** (two rows of the mechanism index, plus the two rows appended after them):

```
| M6 | The base optimiser's own second-moment normalisation | **refuted**: RMSProp and AdamW both carry one and differ by +0.694 ± 0.266 (t 2.61) | §5.5 |
```

**REPLACEMENT:**

```
| M6 | The base optimiser's own second-moment normalisation | **refuted**: RMSProp and AdamW both carry one and differ by +0.531 ± 0.138 (t 3.84) on two-batch level pools | §5.5 |
| M9 | A second-moment normaliser **anywhere in the loop** — base or meta — shrinks D | **refuted on a pre-registered bar**: at the corner where both carry one, D = +0.889 ± 0.228 (t 3.89), the **largest** D in the AdamW family, against a registered refutation threshold of D ≥ +0.55 | §5.5 |
```

---

**ANCHOR** (M4's row):

```
| M4 | The size-1 tail carries it universally | **narrowed to SGDm**: pooled D − G = +0.514 ± 0.056 over the 8 CIFAR-10 SGDm cells vs +0.047 ± 0.124 under AdamW. No individual `G` survives Holm over the 12-test family | §5.4 |
```

**REPLACEMENT:**

```
| M4 | The size-1 tail carries it universally | **narrowed to a base–meta pairing, not to a base**: pooled D − G = +0.514 ± 0.056 over the 8 CIFAR-10 SGDm cells and −0.061 ± 0.085 under AdamW + Lion (2 batches), but **+0.629 ± 0.242 (t 2.59) under AdamW + RMSProp**. No individual `G` survives Holm on Welch df over the 14-test family | §5.4, §5.5 |
```

### 3.6 §5.5 — replaced in full: the normalisation story, refuted twice

**ANCHOR** (the whole of §5.5):

```
### 5.5 Refuted: base-optimiser normalisation

If the mechanism were "a base optimiser that already normalises per coordinate does not need the
partition to do it", then RMSProp and AdamW — both carrying a second moment — should behave alike.
They do not: **D(RMSProp) − D(AdamW) = +0.694, se 0.266, t 2.61**. Whatever separates the base
optimisers here, second-moment normalisation is not it.

This is the same conclusion §4.4 reaches from the other side: in the four-level base
decomposition the second-moment main effect is −0.169 ± 0.145 (z −1.17) while the momentum main
effect is −0.587 ± 0.145 (z −4.04). Neither of those contrasts is a result — three of the four
levels are single batches — but they agree on which component of the base optimiser is *not* the
axis.
```

**REPLACEMENT:**

```
### 5.5 Refuted twice: second-moment normalisation, in the base (M6) and in the meta (M9)

**M6, the base side, post-hoc.** If the mechanism were "a base optimiser that already normalises per
coordinate does not need the partition to do it", then RMSProp and AdamW — both carrying a second
moment — should behave alike. They do not. On the two-batch level pools of §4.4,
**D(RMSProp) − D(AdamW) = +0.531 ± 0.138, t 3.84**; on the single-batch reading DRAFT-v3 quoted, the
independent `nl1`-versus-`aw1` contrast, it was +0.694 ± 0.266, t 2.61. The refutation is the same
and it is now carried by four batches instead of two. It remains a **post-hoc contrast** on data
collected for other purposes, and the AdamW half of it comes entirely from `aw1` and `sm3`: `bm2`'s
registered scorer forbids `bm2` any statement about AdamW, and none is made.

**M9, the meta side, pre-registered.** M6 leaves the strongest form of the normalisation story
standing. Every base-side comparison in this corpus varies the base while a **Lion** meta-optimiser
sits above it, and Lion's sign update carries no second moment at all. So the claim "D shrinks
wherever a second-moment normaliser sits, base **or** meta" had never been tested at the one corner
that decides it: an AdamW base with an RMSProp meta, where both components carry one. That corner
predicts the *smallest* D in the corpus. `sm3` was built to run it and did not — its own `ARGS:`
line carries `--alg-meta` twice and argparse kept the last occurrence, so it ran Lion (§6.1). The
corner was therefore untested, not refuted, and it stayed that way for a full cycle.

`sm4` runs it. Four granularity arms × three seeds at `aw1`'s own cell — ResNet-18/CIFAR-10, α₀ =
1e-3, η = 1e-4, box −15:−2.3026, 100 epochs, AUGMENT=1 — changing exactly one flag,
`--alg-meta Lion` → `--alg-meta RMSProp`, with RMSProp's own attribute set live and Lion's two
attributes set to the code's `-1` sentinel so they are dropped before the optimiser is built. The
decision rule was frozen in the batch script before submission, and we quote it from the script
rather than paraphrasing it:

> `Mechanism candidate 8 says D shrinks wherever a second-moment normaliser sits. […] This corner
> carries a second moment on BOTH sides, so the pattern predicts the SMALLEST D in the corpus.`
> `  REFUTED if D >= +0.55.`
> `CONSISTENT if D <= +0.279 (aw1's own D) with a 95% interval below the bar.`
> `UNDECIDED otherwise -- report the interval, add no seeds to this batch, and re-register a fresh
> replicate instead. All three outcomes are publishable and the scorer prints the one that fires;
> nothing here is chosen after the fact.`

Three gates fire before the contrast. The ARGS gate (RULE 20) read all twelve runs' own `ARGS:`
lines: `CLEAN — every run's own ARGS line matches the declared design, no repeated flag, no Lion
attribute live` — which is the check `sm3` would have failed. The box gate, measured on `sm4`'s own
probe records, reports `coord_lo` and `coord_hi` of exactly 0.00000 on all four arms. And an
operating-point gate, blocking and registered in advance because no RMSProp meta-optimiser had ever
run anywhere in this corpus and its meta-stepsize was matched to `aw1` rather than tuned:
`ON ANCHOR. 12-run mean plateau5 91.567 against the AdamW+Lion anchor 93.161 (−1.594 pp, bar 3.0).
The cell is comparable.` Had it fired, every contrast in the batch would have been demoted to
descriptive and labelled off-anchor — reported, not discarded.

The verdict, from `analysis/c97_sm4_score.py` run unedited:

> `D = chunk777 − nodewise = +0.8893 ± 0.2285   t +3.89 (df 2.3, p 0.0494)   n 3v3`
> `95% CI [+0.4415, +1.3371]`
> `VERDICT: REFUTED. D >= +0.55 at the corner where BOTH the base and the meta carry a
> second-moment normaliser. Mechanism candidate 8 — 'D shrinks wherever a second moment sits' — is
> false, and the AdamW/RMSProp pattern in the corpus needs another explanation. This is a POSITIVE
> result and must be reported as one, not buried.`

**The corner that predicted the smallest D in the corpus produced the largest D in the AdamW
family**: +0.889 against `aw1`'s +0.279, `sm3`'s +0.141, and their pool of +0.189 ± 0.052 — a
between-batch difference of +0.700 ± 0.234. Whatever the AdamW-versus-RMSProp pattern in §4.4 is, it
is not a count of second-moment normalisers in the loop.

**Scope, carried with the verdict because the scorer carries it.** The batch runs at `aw1`'s
meta-stepsize of 1e-4, **not at an RMSProp-meta optimum** — no meta-stepsize ladder exists under an
RMSProp meta, because this corpus contains no other RMSProp-meta run of any kind. It is ResNet-18 /
CIFAR-10 / 100 epochs / box −15:−2.3026 only. And it is **not pooled with `aw1` or `sm3`**: different
meta-optimiser, different batch. One cell refutes a claim that was stated over the whole grid; it
does not establish anything about the RMSProp-meta cell that a ladder would.

**What this does to §4.4's 2 × 2.** DRAFT-v3 read the four-level base decomposition as agreeing with
M6 about which component of the base optimiser is not the axis, on the strength of an unresolved
second-moment main effect (−0.169 ± 0.145, z −1.16). On the fourteen-cell pools that main effect
resolves (−0.323 ± 0.080, z −4.03) and the agreement is gone. **We withdraw the claim that the two
analyses agree.** What both still support is the weaker and more useful statement: neither momentum
nor second-moment normalisation, taken alone, is the moderator — the momentum collapse leaves a
residual Q of 34.64 on 9 df — and M9 shows that adding a second moment to the *meta*-optimiser moves
D in the direction opposite to the one the normalisation story requires.
```

### 3.7 §5.4 — the tail is meta-dependent, not just base-dependent

**ANCHOR** (last row of the D / G / D−G table):

```
| **aw1 (AdamW)** | +0.279 ± 0.087 | **+0.232 ± 0.089** | **+0.047 ± 0.124** | **0.38** |
```

**REPLACEMENT:**

```
| **aw1 (AdamW + Lion)** | +0.279 ± 0.087 | **+0.232 ± 0.089** | **+0.047 ± 0.124** | **0.38** |
| **sm3 (AdamW + Lion)** | +0.141 ± 0.064 | **+0.296 ± 0.096** | **−0.155 ± 0.116** | **−1.34** |
| **sm4 (AdamW + RMSProp)** | +0.889 ± 0.228 | **+0.261 ± 0.081** | **+0.629 ± 0.242** | **2.59** |
```

---

**ANCHOR:**

```
**The twelve `G` tests, corrected for multiplicity.** `G` is measured once per count-matched
cell, so the twelve values above are a family and the ones that reach nominal significance
should not be read one at a time. We declared the family as the `G` leg of every Table 2 cell
that has one — twelve tests, fixed before the correction was computed — and applied
Holm–Bonferroni step-down at α = 0.05.
```

**REPLACEMENT:**

```
**The `G` tests, corrected for multiplicity.** `G` is measured once per count-matched cell, so the
values above are a family and the ones that reach nominal significance should not be read one at a
time. We declared the family as the `G` leg of every Table 2 cell that has one — twelve tests, fixed
before the correction was computed — and applied Holm–Bonferroni step-down at α = 0.05. **Table 2
has since grown by four cells, two of which have a `G`** (`sm3` and `sm4`; `bm2` ran only
`nodewise` and `chunk777`, and its registered scorer forbids any `G` or tail statement from it), so
the same rule now yields **fourteen** tests. We report the pre-specified twelve first, unchanged,
and then the fourteen, so that the effect of enlarging the family is visible rather than absorbed.
```

---

**ANCHOR:**

```
**At most three of the twelve reach nominal α = 0.05 and none survives Holm.** On the normal
approximation the three are `aw1` (t 2.62), `ml2` (t 2.38) and `g3m` (t 2.34), with smallest
adjusted p = 0.11; on the Welch degrees of freedom only `g3m` reaches nominal α, with
smallest adjusted p = 0.39. **We therefore make no claim that `G` is resolved in any
individual cell**, and an earlier version of this section, which rested on `G` being resolved
under AdamW, is withdrawn as a per-cell claim.
```

**REPLACEMENT:**

```
**At most three of the pre-specified twelve reach nominal α = 0.05 and none survives Holm.** On the
normal approximation the three are `aw1` (t 2.62), `ml2` (t 2.38) and `g3m` (t 2.34), with smallest
adjusted p = 0.11; on the Welch degrees of freedom only `g3m` reaches nominal α, with smallest
adjusted p = 0.39.

**On the family of fourteen, the Welch verdict is unchanged and the normal-approximation verdict is
not.** Adding `sm3` (G = +0.296 ± 0.096, t 3.07, Welch df 3.5) and `sm4` (G = +0.261 ± 0.081,
t 3.23, Welch df 3.7): on Welch degrees of freedom **nothing survives Holm** (smallest adjusted
p = 0.46, `g3m`); on the anti-conservative normal approximation **`sm4` (adjusted p = 0.017) and
`sm3` (adjusted p = 0.028) both survive**, which no tabled cell did at twelve. We record that
without resting anything on it, because the normal approximation is the wrong reference at 3.5
degrees of freedom and we say so elsewhere in this paper. The enlarged family is also heterogeneous
where the pre-specified one was not — fourteen-cell G pool +0.093 ± 0.022, Q = 28.25 on 13 df
(p = 0.0084), against the twelve-cell +0.067 ± 0.023, Q = 18.21 on 11 df (p = 0.077) — and the two
cells that make it so are the two new AdamW-base ones.

**We therefore make no claim that `G` is resolved in any individual cell**, and an earlier version
of this section, which rested on `G` being resolved under AdamW, is withdrawn as a per-cell claim.
```

---

**ANCHOR:**

```
An independent AdamW measurement points the same way and is *not* pooled into the numbers above,
because its runs are not yet in the deposited run table: `sm3`, re-derived from its raw `.out`
series, gives G = +0.296 ± 0.096 and D − G = −0.155 ± 0.116 at the same cell as `aw1` (§6.1).
Taken with `aw1` that would be D − G = −0.054 ± 0.082 over six seeds. We report it as a
consistency check on the direction and make no claim from it.
```

**REPLACEMENT:**

```
The independent AdamW measurement is `sm3`, and its runs **are** now in the deposited run table, so
it enters the table above rather than sitting beside it: G = +0.296 ± 0.096, D − G = −0.155 ± 0.116
at the same cell as `aw1` (§6.1). The two AdamW + Lion batches pool to **D − G = −0.061 ± 0.085**
(Q 1.41 on 1 df); on the 6 v 6 concatenation of their seeds the same quantity reads −0.054 ± 0.082
(t −0.66). Under an AdamW base with a Lion meta-optimiser, the size-1 tail contributes nothing
measurable to D, and that now rests on two independent submissions rather than one.
```

---

**ANCHOR:**

```
**Two `G` contrasts exist in the corpus outside this table**, and we name them so the family
is auditable rather than convenient. `bn1` ran `nodewise1d` and `chunk2325` (m = 4,851 in
both arms) but no `chunk777` arm, so it yields a `G` and no `D`: G = +0.295 ± 0.048, the
largest `G` in the corpus and the only large positive `G` under an SGDm base — which cuts
against "under SGDm, removing the tail removes the gap". `sm3` yields G = +0.296 ± 0.096.
Enlarging the family to all fourteen and re-running Holm changes the count but not the verdict
on the tabled twelve: on the Welch degrees of freedom **nothing survives Holm at fourteen
either**; on the normal approximation `bn1` (adjusted p = 1.1e-8) and `sm3` (adjusted
p = 0.030) survive and no cell in the table does.
```

**REPLACEMENT:**

```
**One `G` contrast exists in the corpus outside this table**, and we name it so the family is
auditable rather than convenient. `bn1` ran `nodewise1d` and `chunk2325` (m = 4,851 in both arms)
but no `chunk777` arm, so it yields a `G` and no `D`: G = +0.295 ± 0.048, the largest `G` in the
corpus and the only large positive `G` under an SGDm base — which cuts against "under SGDm,
removing the tail removes the gap". (`sm3`'s G, which DRAFT-v3 also listed here, is now a tabled
cell.) Enlarging the family to all fifteen and re-running Holm changes the count but not the
verdict on Welch degrees of freedom, where **nothing survives**; on the normal approximation `bn1`
(adjusted p = 1.2e-8), `sm4` (0.017) and `sm3` (0.028) survive.
```

---

**ANCHOR:**

```
Under SGDm, removing the tail removes the gap. **Under AdamW it does not**: `D − G` collapses
to +0.047 ± 0.124 in `aw1`, against +0.514 ± 0.056 pooled over the eight CIFAR-10 SGDm cells.
`G` itself is positive under AdamW (+0.232 ± 0.089) but survives Holm over the `G` family in
neither convention, so the base-dependence is carried by the `D − G` contrast, which is one
pre-specified comparison, not by a per-cell `G` verdict.
```

**REPLACEMENT:**

```
Under SGDm, removing the tail removes the gap. **Under AdamW with a Lion meta it does not**:
`D − G` is +0.047 ± 0.124 in `aw1` and −0.155 ± 0.116 in `sm3`, pooling to −0.061 ± 0.085, against
+0.514 ± 0.056 pooled over the eight CIFAR-10 SGDm cells. `G` itself is positive under AdamW
(+0.232 ± 0.089 and +0.296 ± 0.096) but survives Holm over the `G` family on Welch degrees of
freedom in neither cell, so the dependence is carried by the `D − G` contrast, which is one
pre-specified comparison, not by a per-cell `G` verdict.

**The dependence is not on the base optimiser alone, and this is new.** Holding the base at AdamW
and everything else at `aw1`'s cell, and changing only the meta-optimiser from Lion to RMSProp:

| statistic | AdamW + Lion (`aw1`, `sm3`) | AdamW + RMSProp (`sm4`) | difference |
|---|---|---|---|
| D | +0.189 ± 0.052 | **+0.889 ± 0.228** | **+0.700 ± 0.234** |
| G | +0.261 ± 0.065 | **+0.261 ± 0.081** | **−0.001 ± 0.104** |
| D − G | −0.061 ± 0.085 | **+0.629 ± 0.242** | **+0.690 ± 0.257** |

**`G` does not move at all — the two readings agree to a thousandth of a percentage point — and the
whole of the meta-optimiser's effect on `D` lands in the size-1 tail component.** The `sm4` scorer
reaches the same two conclusions independently and states them as its own registered verdicts:
`G PERSISTS. The exactly count-matched contrast stays resolved when the meta also carries a second
moment, as it is under AdamW+Lion (aw1 +0.232, sm3 +0.296). G is base-dependent, not
meta-dependent, at this corner.` And on the mechanism contrast: `MECHANISM CONTRAST RESOLVED at
|t| >= 2 (interval [+0.154, +1.104]). Under AdamW+Lion it is NOT resolved in either batch (aw1
+0.047, sm3 −0.155), so a resolved D−G here is a finding about the meta-optimiser.`

**What that costs the tail story.** M4 was narrowed in DRAFT-v3 to "an SGDm base with a Lion
meta-optimiser", with AdamW as the counter-example. The counter-example does not survive as a
statement about the base: at an AdamW base the tail carries nothing under Lion and carries
+0.629 ± 0.242 under RMSProp. **The tail's contribution is a property of the base–meta pairing, not
of the base**, and this corpus has measured only two of the four pairings it would take to say
which side dominates — it has no SGDm + RMSProp cell at all. The two right-hand columns of the table
above are **cross-batch** comparisons and carry the batch floor this paper measures elsewhere
(F(62,85) = 5.47, p 6.9e-13), which neither pairing nor Welch removes; they are labelled
comparisons, not registered tests, and the `sm4` registration explicitly forbids pooling `sm4` with
`aw1` or `sm3`. What is a registered test is `sm4`'s own within-batch `D − G` = +0.629 ± 0.242
(t 2.59), and it is resolved.

> **"The gap lives in the degenerate size-1 tail" may not be written as a general claim, and may
> not be scoped to a base optimiser either.** It holds under an SGDm base with a Lion
> meta-optimiser (eight cells, seven submissions) and under an AdamW base with an RMSProp meta
> (one cell); it fails under an AdamW base with a Lion meta (two cells). The scoping variable is
> the pairing, and three of its four cells are one batch each.
```

---

**ANCHOR** (Figure 4 caption):

```
**Figure 4 — D splits into a tail-free part G and a size-1-tail part D − G, and the split is
base-dependent.** (a) For every batch that ran all four arms, D is drawn as the sum of G (hatched:
the same uniform-versus-aligned contrast with the size-1 tail *already removed from both arms*,
count-matched exactly at m = 4,851) and D − G (solid: what the tail contributes). The black tick
and whisker are D itself with its 95% interval. Under an SGDm base the hatched part is ≈0 and the
tail carries essentially all of D. Under **AdamW** it does not: G is +0.232 ± 0.089 and D − G
collapses to +0.047 ± 0.124.
```

**REPLACEMENT:**

```
**Figure 4 — D splits into a tail-free part G and a size-1-tail part D − G, and the split depends
on the base–meta pairing.** (a) For every batch that ran all four arms, D is drawn as the sum of G
(hatched: the same uniform-versus-aligned contrast with the size-1 tail *already removed from both
arms*, count-matched exactly at m = 4,851) and D − G (solid: what the tail contributes). The black
tick and whisker are D itself with its 95% interval. Under an SGDm base with a Lion meta the
hatched part is ≈0 and the tail carries essentially all of D. Under **AdamW with a Lion meta** it
does not: G is +0.232 ± 0.089 (`aw1`) and +0.296 ± 0.096 (`sm3`) while D − G is +0.047 ± 0.124 and
−0.155 ± 0.116, pooling to −0.061 ± 0.085. Under **AdamW with an RMSProp meta** (`sm4`, the only
non-Lion cell in the corpus) G is unchanged at +0.261 ± 0.081 while D − G returns to
+0.629 ± 0.242 (t 2.59) — G does not move with the meta-optimiser and the tail component does.
```

### 3.8 §6.1 — `sm3` is ingested

**ANCHOR:**

```
`--alg-meta RMSProp … --alg-meta Lion`, so it ran Lion. **The second-moment corner is untested, not
refuted**, and the batch is salvageable only as an independent replicate of `aw1`: D = +0.141 ±
0.064, G = +0.296 ± 0.096, at the same box, α₀, η and budget. Its twelve rows are not yet in the
deposited run table, so no number from it enters a claim in this paper; it appears in §4.4 and §5.4
as a consistency check and nowhere else. The properly composed replacement (R4, `sm4`) is in
flight (§3.5).
```

**REPLACEMENT:**

```
`--alg-meta RMSProp … --alg-meta Lion`, so it ran Lion. The second-moment corner was therefore
**untested, not refuted**, and the batch is salvageable only as an independent replicate of `aw1`:
D = +0.141 ± 0.064, G = +0.296 ± 0.096, at the same box, α₀, η and budget. Its twelve rows are now
in the deposited run table, so a reader can re-derive both numbers; it is Table 2 row 19, it is the
AdamW level's second batch in §4.4, and it is a cell of the `G` family in §5.4. The properly
composed replacement, R4 (`sm4`), has since run and **refuted the mechanism** the corner was built
to test (§5.5) — which is the useful sense in which this failure was recoverable, and it cost a
full cycle.
```

---

**ANCHOR:**

```
The corpus census confirms the hole is still open: **367 of 367
partition-programme runs are meta = Lion**, across four base optimisers.
```

**REPLACEMENT:**

```
At the time `ml2` was audited the corpus census confirmed the hole was total: every
partition-programme run in the corpus was meta = Lion, across four base optimisers. `sm4` has since
opened it by exactly twelve runs — see §7 T1 for the census under an explicit rule and for how
little one cell closes.
```

### 3.9 §7 T1 — how much of the largest hole is closed

**ANCHOR:**

```
**T1 — One meta-optimiser.** All 367 partition-programme runs use Lion. Lion's sign update makes the
per-group α the *only* thing setting per-coordinate update magnitude, which is precisely the regime
where the partition should matter most. So our headline is measured at the most favourable point of
the axis we never varied. §6.1 explains why the two batches built to fix this did not, and §3.5
states the replacement that is running. **This is the paper's largest hole.**
```

**REPLACEMENT:**

```
**T1 — Almost one meta-optimiser.** Lion's sign update makes the per-group α the *only* thing
setting per-coordinate update magnitude, which is precisely the regime where the partition should
matter most. Our headline is measured at the most favourable point of the axis we barely varied,
and this remains the paper's largest hole. `sm4` has narrowed it, and it is worth being exact about
by how much.

Define a **partition-programme run** as a row of the deposited run table whose `granularity` is
`nodewise`, `nodewise1d`, `permnode*` or `chunk*`, in a batch that contains at least one `chunk*`,
`permnode*` or `nodewise1d` arm — i.e. a batch running a partition contrast rather than the
granularity-ladder programme of §4.2. Under that rule the corpus holds **354 partition-programme
runs in 22 batches**, of which **342 are meta = Lion and 12 are meta = RMSProp**. Before `sm4` the
count was 342 of 342.

So the axis is no longer empty, and it is not an axis either:

- **Twelve runs, one cell, 3.4% of the partition programme.** One base optimiser (AdamW), one
  network, one dataset, one budget, one β-box, one meta-stepsize, three seeds.
- **No ladder.** The `sm4` scorer attaches the limit as part of its verdict: the batch runs at
  `aw1`'s meta-stepsize of 1e-4, **not at an RMSProp-meta optimum**, because no meta-stepsize
  ladder exists under an RMSProp meta — this corpus contains no other RMSProp-meta run of any kind.
  §4.1 shows the meta-stepsize moves the granularity gap by more than the gap, so an untuned η is
  not a minor caveat on this axis specifically.
- **The meta axis now has exactly the defect §4.4 spent a batch removing from the base axis.** Of
  its two levels, one has fourteen cells and seven-plus submissions and the other has one cell and
  one submission. A single-cell level cannot be tested for within-level homogeneity, so nothing in
  this corpus can distinguish a meta-optimiser effect from a batch effect peculiar to `sm4` — the
  same argument that made `nl1`'s two levels inadequate before `bm2` ran.

**What the one cell does buy.** It is enough to refute a claim that was stated over the whole grid:
the corner where base *and* meta both carry a second-moment normaliser produces the **largest** D in
the AdamW family, not the smallest, against a bar registered before the runs existed (§5.5, M9). And
it produces a structural result the Lion-only corpus could not have produced: at a fixed AdamW base,
switching the meta-optimiser leaves G untouched (−0.001 ± 0.104) and moves D − G by +0.690 ± 0.257,
so the tail story is scoped to a base–meta **pairing** rather than to a base (§5.4). Refuting a
universal claim takes one counter-example. Establishing the axis takes a ladder, and there is none.

**The experiment this hole still needs**, stated so that it is not confused with what was run: a
meta-stepsize ladder under an RMSProp meta at a fixed base, plus at least one non-Lion meta cell at
a base other than AdamW — SGDm is the obvious one, since it is where seven of the paper's
submissions sit and where the tail story is strongest. Neither exists, and neither is in flight.
```

### 3.10 Abstract, contributions and conclusion — sentence-level replacements

> **Note for the integrator.** Blocking item C4 replaces the abstract wholesale (922 words against a
> 120–230 target). The three abstract replacements below are written so they can be applied either
> to the current abstract or lifted as the corrected *facts* into whatever abstract C4 produces.
> Where C4 and this package disagree, the numbers here are the re-derived ones.

**ANCHOR** (abstract, corpus sentence):

```
approximations evaluated."* We take that question up with 2,113 runs (≈1,582 GPU-hours; 1,671
admissible) on ResNet-10/18/34/50 and CIFAR-10/100, and report one robust measurement, one
bounded null, and a mechanism we could not find.
```

**REPLACEMENT:**

```
approximations evaluated."* We take that question up with 2,173 runs (≈1,625 GPU-hours; 1,724
admissible) on ResNet-10/18/34/50 and CIFAR-10/100, and report one robust measurement, one
bounded null, and a mechanism we could not find.
```

---

**ANCHOR** (abstract, the measurement):

```
**The measurement.** Replacing an architecture-aligned partition (one step size per output
channel, `nodewise`) by a uniform one of the *same group count* (fixed-size chunks of K weights)
is worth a positive amount of final accuracy in **every one of 16 within-batch, count-matched
cells we measured**, spanning three networks (ResNet-18, ResNet-34, ResNet-50), 2 datasets,
4 base optimisers, 2 meta-stepsizes and 2 budgets.
```

**REPLACEMENT:**

```
**The measurement.** Replacing an architecture-aligned partition (one step size per output
channel, `nodewise`) by a uniform one of the *same group count* (fixed-size chunks of K weights)
is worth a positive amount of final accuracy in **every one of 20 within-batch, count-matched
cells we measured**, spanning three networks (ResNet-18, ResNet-34, ResNet-50), 2 datasets,
4 base optimisers, 2 meta-optimisers, 2 meta-stepsizes and 2 budgets.
```

---

**ANCHOR** (abstract, the moderator):

```
Over the eleven cells that run the same ResNet-18 partition contrast, D varies
genuinely across configurations (**Q = 36.4 on 10 df, p = 7.2e-5**, τ = 0.203 pp against 0.152 pp
rms measurement error) — and **88% of that variation is one identified moderator, the base
optimiser** (between-base Q = 32.2 on 3 df, p = 4.8e-7). At a fixed base the effect is homogeneous:
over eight SGDm cells spanning seven separate submissions, two meta-stepsizes, two budgets and three
step-size clip boxes, D = **+0.556 ± 0.045 pp** with Q = 4.21 on 7 df (p = 0.76, τ = 0.000).
```

**REPLACEMENT:**

```
Over the fourteen cells that run the same ResNet-18 partition contrast, D varies
genuinely across configurations (**Q = 102.5 on 13 df, p = 5.5e-16**, τ = 0.295 pp against 0.143 pp
rms measurement error) — and **93% of that variation is one identified moderator, the base
optimiser** (between-base Q = 95.1 on 3 df, p = 1.7e-20). **All four levels of that moderator are
replicated across at least two independent submissions**, and every one is internally homogeneous:
SGD +1.000 ± 0.067 (Q 0.17/1), RMSProp +0.720 ± 0.128 (Q 1.37/1), SGDm +0.556 ± 0.045 (Q 4.21/7,
seven submissions, two meta-stepsizes, two budgets, three clip boxes), AdamW +0.189 ± 0.052
(Q 1.61/1). The within-level remainder is Q = 7.4 on 10 df, p = 0.69.
```

---

**ANCHOR** (abstract, "what we could not find"):

```
**What we could not find.** We examined eight candidate mechanisms and refuted three of them,
narrowed a fourth to one base optimiser, found a fifth not separable from the axes it is aliased
with, and found the remaining three undecidable by this instrument or this design; we report all
eight, because they are half the contribution. Chief among them: the obvious carrier — degenerate
size-1 groups — is not it (removing 100% of a network's singletons buys +0.115 ± 0.133 pp, t 0.87);
the tail story is base-specific (pooled D − G = +0.514 ± 0.056 under SGDm, +0.047 ± 0.124 under
AdamW);
```

**REPLACEMENT:**

```
**What we could not find.** We examined nine candidate mechanisms and refuted four of them,
narrowed a fifth to a base–meta pairing, found a sixth not separable from the axes it is aliased
with, and found the remaining three undecidable by this instrument or this design; we report all
nine, because they are half the contribution. One refutation is fully pre-registered: at the one
corner where the base *and* the meta-optimiser both carry a second-moment normaliser — the corner
that predicted the smallest gap in the corpus — D = **+0.889 ± 0.228 pp (t 3.89)**, the largest in
the AdamW family, against a bar of D ≥ +0.55 committed before the runs existed. Chief among the
rest: the obvious carrier — degenerate size-1 groups — is not it (removing 100% of a network's
singletons buys +0.115 ± 0.133 pp, t 0.87); the tail story is scoped to a base–meta pairing rather
than a base (pooled D − G = +0.514 ± 0.056 under SGDm + Lion, −0.061 ± 0.085 under AdamW + Lion, and
+0.629 ± 0.242 under AdamW + RMSProp, where G itself does not move at all: −0.001 ± 0.104);
```

---

**ANCHOR** (abstract, scope item (iii)):

```
(iii) All 367 partition-programme runs reported here
use a **Lion** meta-optimiser; the base optimiser has been varied four ways, the meta-optimiser never
— a batch that was to fix this ran a different experiment from the one it declared (§6.1), and the
replacement is in flight (§3.5).
```

**REPLACEMENT:**

```
(iii) 342 of the 354 partition-programme runs reported here
use a **Lion** meta-optimiser; the base optimiser has been varied four ways with every level
replicated, the meta-optimiser exactly once, in one cell of twelve runs with no meta-stepsize ladder
under it (§7 T1). That one cell is enough to refute a mechanism and not enough to be an axis.
```

---

**ANCHOR** (abstract, the in-flight paragraph):

```
**Four pre-registered batches are in flight** and are described in §3.5 with their decision rules,
because three of them exist to repair specific weaknesses this paper states about itself: the
alignment null's power and its permutation-seed confound (`rp1`), the one budget cell's clip-box and
hardware mismatch (`hz3`-R2), the base-optimiser moderator's single-batch levels (`bm2`), and the
second-moment corner that §6.1's void batch failed to test (`sm4`). None of them contributes a
number to this draft.
```

**REPLACEMENT:**

```
**Four pre-registered batches were submitted to repair specific weaknesses this paper states about
itself, and two have been scored** by running their registered scorers unedited (§3.5): the
base-optimiser moderator's single-batch levels (`bm2` — **both levels replicate**) and the
second-moment corner that §6.1's void batch failed to test (`sm4` — **the mechanism is refuted**).
Two are not scored and contribute no number anywhere in this paper: the alignment replication with
the permutation seed decoupled (`rp1`, complete on disk, deliberately unread) and the budget cell's
box- and hardware-matched trio (`hz3`-R2, queued).
```

---

**ANCHOR** (Contribution 1):

```
1. **A count-matched isolation of the group-size distribution from the group count** in
   meta-learned step sizes, replicated in 16 within-batch cells across three networks, 2 datasets
   and 4 base optimisers (§4.3–§4.5, Table 2, Figure 1).
```

**REPLACEMENT:**

```
1. **A count-matched isolation of the group-size distribution from the group count** in
   meta-learned step sizes, replicated in 20 within-batch cells across three networks, 2 datasets,
   4 base optimisers and 2 meta-optimisers (§4.3–§4.5, Table 2, Figure 1).
```

---

**ANCHOR** (Contribution 3):

```
3. **An identified moderator for the effect's heterogeneity**: the base optimiser carries 88% of
   the between-cell Cochran Q, and inside a fixed base D is homogeneous (τ = 0.000, 95% upper limit
   0.109 pp) across seven submissions, two meta-stepsizes, two budgets and three clip boxes
   (§4.4, Figure 2).
```

**REPLACEMENT:**

```
3. **An identified moderator for the effect's heterogeneity, replicated at every level**: the base
   optimiser carries 93% of the between-cell Cochran Q (95.1 of 102.5 on 3 df), each of its four
   levels now rests on two or more independent submissions, and each is internally homogeneous
   (within-level Q 0.17/1, 1.37/1, 1.61/1 and 4.21/7). Under SGDm, D is homogeneous
   (τ = 0.000, 95% upper limit 0.109 pp) across seven submissions, two meta-stepsizes, two budgets
   and three clip boxes (§4.4, Figure 2). A pre-registered replication batch (`bm2`) bought the two
   thinnest levels, and it is what makes the decomposition a testable restriction rather than an
   arithmetic identity.
```

---

**ANCHOR** (Contribution 5):

```
5. **Eight candidate mechanisms — three refuted, one narrowed to a single base optimiser, one not
   separable, three undecidable by this design — and two nulls**, reported as a section rather than
   an appendix (§5), including the identifiability limit that makes a ninth unanswerable from this
   corpus.
```

**REPLACEMENT:**

```
5. **Nine candidate mechanisms — four refuted, one narrowed to a base–meta pairing, one not
   separable, three undecidable by this design — and two nulls**, reported as a section rather than
   an appendix (§5), including the identifiability limit that makes a tenth unanswerable from this
   corpus. One of the four refutations is fully pre-registered: the bar was committed in the batch
   script before the runs existed and the batch cleared it in the direction the mechanism forbade
   (§5.5, M9).
```

---

**ANCHOR** (Contribution 6):

```
6. **A practitioner prescription with its scope attached**: merging each one-dimensional tensor
   into a single group is worth **+0.328 ± 0.084 to +1.363 ± 0.151 pp** across ten within-batch
   cells under SGDm, SGD and RMSProp bases, and costs nothing — but under an AdamW base it is
   worth +0.091 ± 0.078, i.e. nothing measurable (§4.7, §5.4).
```

**REPLACEMENT:**

```
6. **A practitioner prescription with its scope attached, and the scope is not where we first put
   it**: merging each one-dimensional tensor into a single group is worth **+0.328 ± 0.084 to
   +1.363 ± 0.151 pp** across ten within-batch cells under SGDm, SGD and RMSProp bases, and costs
   nothing. Under an AdamW base with a **Lion** meta-optimiser it is worth nothing measurable
   (+0.007 ± 0.056 over two batches); under the same AdamW base with an **RMSProp** meta it is worth
   +0.988 ± 0.231. The exception is a base–meta pairing, not a base (§4.7, §5.4, §5.5).
```

---

**ANCHOR** (conclusion, the measurement paragraph):

```
**every one of 16 within-batch cells** across three networks, two datasets, four base
optimisers, two meta-stepsizes and two budgets; it survives tuning each arm to its own optimum
(−0.090 ± 0.178, itself an upper bound in magnitude); it is present and resolved at 3× the budget;
and its variation across configurations is dominated by one identified moderator — the base
optimiser carries 88% of the between-cell heterogeneity (Q 32.2 / 3 df), and inside a fixed base
the effect is homogeneous (Q 4.21 / 7 df, p 0.76, τ 0.000, pool +0.556 ± 0.045).
```

**REPLACEMENT:**

```
**every one of 20 within-batch cells** across three networks, two datasets, four base
optimisers, two meta-optimisers, two meta-stepsizes and two budgets; it survives tuning each arm to
its own optimum (−0.090 ± 0.178, itself an upper bound in magnitude); it is present and resolved at
3× the budget; and its variation across configurations is dominated by one identified moderator —
the base optimiser carries 93% of the between-cell heterogeneity (Q 95.1 / 3 df), every one of its
four levels is now replicated across two or more independent submissions, and inside each level the
effect is homogeneous (within-level Q 7.4 on 10 df in total, p 0.69; under SGDm Q 4.21 / 7,
τ 0.000, pool +0.556 ± 0.045).
```

---

**ANCHOR** (conclusion, the mechanisms paragraph):

```
Eight further mechanisms were examined and three
are refuted, with the other five narrowed, unseparable or undecidable: √N averaging
(untested, not refuted, and its literature attribution withdrawn), the meta-gradient correlation
field (anti-concordant at t −11.14), size-1 groups as such (+0.115 ± 0.133), the tail as a
universal carrier (SGDm-specific: pooled D − G +0.514 ± 0.056 under SGDm against +0.047 ± 0.124
under AdamW), Choi-style inclusion (granularity is state, not hyperparameters), base-optimiser
normalisation (RMSProp and AdamW differ by +0.694 ± 0.266), and any size-distribution summary
statistic (not identifiable). An eighth candidate, the aligned arm's accuracy level, is neither
confirmed nor separable:
```

**REPLACEMENT:**

```
Nine further mechanisms were examined and four
are refuted, with the other five narrowed, unseparable or undecidable: √N averaging
(untested, not refuted, and its literature attribution withdrawn), the meta-gradient correlation
field (anti-concordant at t −11.14), size-1 groups as such (+0.115 ± 0.133), the tail as a
universal carrier (scoped to a base–meta pairing: pooled D − G +0.514 ± 0.056 under SGDm + Lion,
−0.061 ± 0.085 under AdamW + Lion, +0.629 ± 0.242 under AdamW + RMSProp), Choi-style inclusion
(granularity is state, not hyperparameters), base-optimiser normalisation (RMSProp and AdamW differ
by +0.531 ± 0.138), **second-moment normalisation anywhere in the loop — refuted on a bar
registered before the data existed: the corner where base and meta both carry one gives
D = +0.889 ± 0.228, the largest in the AdamW family, against a predicted smallest** — and any
size-distribution summary statistic (not identifiable). A ninth candidate, the aligned arm's
accuracy level, is neither confirmed nor separable:
```

---

**ANCHOR** (conclusion, the honest description):

```
The honest description of this paper is therefore: **a robust, replicated, count-matched
measurement; an identified moderator for its heterogeneity that is not yet replicated at three of
its four levels; a single-batch bounded null that excludes the mechanism most people would guess as
the principal carrier without excluding it as a contributor; a prescription that costs nothing and
works under three of four base optimisers; and no mechanism.**
```

**REPLACEMENT:**

```
The honest description of this paper is therefore: **a robust, replicated, count-matched
measurement in twenty cells; an identified moderator for its heterogeneity, replicated at all four
of its levels and homogeneous inside each; a single-batch bounded null that excludes the mechanism
most people would guess as the principal carrier without excluding it as a contributor; a
prescription that costs nothing and works everywhere except one base–meta pairing; nine dead or
undecidable mechanisms, one of them killed on a bar we wrote down first; and no mechanism.**
```

---

**ANCHOR** (conclusion, the in-flight list):

```
**The experiments that would break the impasse**, in the order we would run them. Three are in
flight and are described with their decision rules in §3.5: the alignment replication with the
permutation seed decoupled (R1), the box- and hardware-matched budget trio (R2), and the
base-moderator replication at fresh seeds (R3). A fourth, R4, tests the one untested corner of the
base × meta grid that §6.1's void batch failed to reach.
```

**REPLACEMENT:**

```
**The experiments that would break the impasse**, in the order we would run them. Two of the four
registered in §3.5 have been read: R3, the base-moderator replication at fresh seeds, which
replicated both levels and is in §4.4; and R4, the second-moment corner, which refuted its
mechanism and is in §5.5. Two remain: the alignment replication with the permutation seed decoupled
(R1, complete on disk and deliberately unscored) and the box- and hardware-matched budget trio (R2,
queued). To those we now add the experiment R4 created rather than closed: **a meta-stepsize ladder
under a non-Lion meta-optimiser, and a non-Lion cell at a base other than AdamW.** `sm4` shows the
meta-optimiser moves D − G by more than the base does at one point in the space; a single cell with
no ladder under it cannot say whether that is a meta effect or a batch.
```

---

## 4. What must be regenerated

`analysis/c98_figures.py` produces Figures 1, 2 and 4 and prints the numbers this package quotes,
but its `CELLS` table is a hard-coded literal that does not yet know about the four new cells, so
running it today still reports "16 count-matched cells" and the eleven-cell pool. **The figures in
`paper/figures/` are stale with respect to this package** and must be regenerated after the
following four entries are appended to `CELLS` and the first three added to `POOL12`:

```python
 ("bm2 (SGD)", "ResNet-18", "C10", "SGD",     "1e-4", 100,
  ("bm2-sgd-ch","chunk777"), ("bm2-sgd-node","nodewise"), None, None),
 ("bm2 (RMSProp)", "ResNet-18", "C10", "RMSProp", "1e-4", 100,
  ("bm2-rms-ch","chunk777"), ("bm2-rms-node","nodewise"), None, None),
 ("sm3", "ResNet-18", "C10", "AdamW",   "1e-4", 100,
  ("sm3-awrms-ch","chunk777"), ("sm3-awrms-node","nodewise"),
  ("sm3-awrms-c23","chunk2325"), ("sm3-awrms-n1d","nodewise1d")),
 ("sm4", "ResNet-18", "C10", "AdamW-RMSmeta", "1e-4", 100,
  ("sm4-awrms-ch","chunk777"), ("sm4-awrms-node","nodewise"),
  ("sm4-awrms-c23","chunk2325"), ("sm4-awrms-n1d","nodewise1d")),
```

`sm4` must be given its own `base` string — it is **not** an AdamW-level member — and must be kept
out of `POOL12`, so that the F2 decomposition reproduces 95.12 / 102.47 rather than silently pooling
across meta-optimisers. This package does not make that edit: `analysis/c98_figures.py` is a shared
file and other packages are in flight. Whoever makes it should confirm that F1 then prints
"20 count-matched cells" and F2 prints "base explains 92.8% of the 14-cell Q".

`analysis/c98_reproduce.py` also needs the new assertions, which is blocking item A8's business, not
this package's — but note that every number introduced above is currently unasserted.

---

## 5. Integrator notes — collisions, and what this package does **not** close

**Blocking items this package closes.** None of the eighteen, in full. It is the `new-results`
package: it adds science the draft does not contain. It does, however, materially change three of
them, and one of them it partly resolves:

- **B1 (the 88% is label-invariant) — the arithmetic objection is now dead; the item is not.** The
  objection was that three of four levels were singletons, so `Q_between = Q_total − Q_SGDm`
  identically for any partition isolating them. With `bm2` and `sm3` no level is a singleton,
  `Q_within` is 7.36 on 10 df with 3.15 of it outside SGDm, and the partition is a restriction the
  data could have rejected and did not. §3.3 above writes that out, **and also writes out what it
  does not fix**: the base optimiser is a pre-specified axis, not the best-fitting one — a post-hoc
  cut on D removes 97.5% and a cut by batch identity removes 95.8%. Whoever owns B1 should read
  §3.3's two paragraphs as the proposed resolution and check the framing, not just the number.
  The number itself moves **88% → 92.8%**, and every occurrence must move together (abstract,
  Contribution 3, §4.4 × 4, Figure 2 caption, conclusion).
- **A1 (the ρ superlative) — this package makes it worse before it makes it better.** With twenty
  cells CIFAR-100's ρ = 0.055 is **fourth from the bottom, not third**: `sm3` 0.0205, `aw1` 0.0397,
  `gm2` 0.0504, `gc1` 0.0552. §3.2 supplies corrected §4.3 text; the identical superlative in the
  Figure 1 caption (`0.055 — the **smallest** value in the corpus`) is **not** patched here and is
  still A1's to fix, with the corrected ranking above.
- **B5 (`sm3` ingestion) — verified closed, and its prose consequences are handled here.** The run
  table is 2,173 rows and `sm3` contributes twelve of them, so §4.4's and §5.4's "not yet ingested
  into the run table" sentences were false as of `6a374f4`. §3.3, §3.7 and §3.8 replace all three.

**Collisions to watch when merging.**

1. **C4 (abstract, 922 → 120–230 words)** rewrites the whole abstract. Five of this package's
   replacements are abstract sentences. Apply C4 second and carry the *numbers* from §3.10 forward;
   do not carry the current abstract's numbers, all five of which are now wrong.
2. **A7 (§4.7's T table omits both `rl3` cells)** edits the same table this package appends two rows
   to. The two edits are independent — A7 adds `rl3` rows, this package adds `sm3` and `sm4` rows —
   but A7's sentence "ten cells, every one resolved at t ≥ 3.3" and this package's replacement
   scope paragraph both rewrite the prose immediately below the table. **Merge, do not clobber**:
   A7 owns the cell count, this package owns the AdamW/meta scope line.
3. **A3 (the `dup_group` count)** and **A4 (`pp1`'s nine shared-seed pairs)** may change `pp1`'s
   entry in the fourteen-cell pool. If A4 lands, the fourteen-cell Q, τ and share must be
   recomputed; §2.2 and §2.3 are the numbers to regenerate, and the recipe is `analysis/c98_figures.py`
   with the four `CELLS` entries of §4 added.
4. **A2 (the deposit excludes the probes)** is *aggravated* by this package. Both new verdicts are
   gated on probe records — `sm4`'s box gate and `bm2`'s R0.5 both read `probe.jsonl` occupancy —
   so §4.4 and §5.5 now join §4.5, §4.6, §5.2 and §5.6 in the set of verbatim scorer verdicts a
   reader cannot reproduce from the deposit. A2's fix must enumerate them.

**Two things this package deliberately did not do.**

- **`rp1` was not scored.** All 24 runs reach 100 epochs on disk, and seven rows in
  `results/all_runs.csv` are stale partials from a mid-flight ingest. Re-ingesting and scoring is
  another package's call; §3.1 states the position honestly, and no `rp1` number appears anywhere.
  Note that `analysis/c97_rp1_score.py`'s registration binds whoever runs it: an interval still
  spanning half of D must be reported as **underdetermined**, not as a null.
- **The draft's "367 of 367 partition-programme runs" could not be re-derived** from
  `results/all_runs.csv` under any definition we could construct. The nearest constructions give
  535 partition-granularity rows corpus-wide (505 Lion / 18 fixed-baseline / 12 RMSProp), 354 under
  the batch-scoped rule this package adopts and states, and 294 under that same rule before the 60
  new rows — none of them 367, and none of them 100% Lion once `sm4` is in. Rather than repair a
  number whose provenance we cannot find, §3.9 replaces it with a census under an explicitly stated,
  executable rule. **This is a live defect of the same species as A1 and A8** — a specific figure in
  the manuscript that the deposit does not reproduce — and it should be logged as such rather than
  treated as closed by this substitution.

---

## 6. Addendum — a concurrent change to `results/all_runs.csv`, and a re-verification

While this package was being written another agent ran `analysis/args_repair.py --apply`, which
writes the registered duplicate table into the CSV's `dup_group` column. The working tree now shows
`results/all_runs.csv` as modified: 36 rows gain a `dup_group` value (all twenty-four `ml2` rows and
twelve others), and the file still holds 2,173 rows. **Every number in this package was recomputed
against the repaired file and none of them moved** — the fourteen-cell pool is still
+0.530 ± 0.029 with Q 102.47 on 13 df, the level pools are still +1.000 / +0.720 / +0.556 / +0.189,
and the between-base share is still 92.8%. That is expected rather than lucky:
`c98_figures.arm()` was already collapsing duplicates from `args_repair.GROUPS` as a fallback, so
applying the patch changes the column and not the arithmetic, exactly as that function's docstring
promises.

One observation for whoever owns **A3**, offered as data and not as a fix: the repaired column now
carries **42 rows in 21 duplicate groups** (`a0-*` ×3, `c100pin-layer`, `c100smoke-layer`,
`h2-*` ×4, `ml2-*` ×12). DRAFT-v3's §3.3 and §8 say the run table marks **eighteen** pairs. Twenty-one
is not eighteen either, so A3's discrepancy is still open after the repair — the direction has
changed, not the fact of it.
