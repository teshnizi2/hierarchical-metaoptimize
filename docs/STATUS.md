# STATUS — operator dashboard

Updated 2 Sep 2026 (cycle 101). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **128**) > `docs/FINDINGS.md` > everything else.

## Cycle 101 — DRAFT-v4 is assembled and `paper.tex` is reconciled with it

| | |
|---|---|
| Draft | `paper/DRAFT-v4.md` + `paper/paper.tex` (59 pp PDF, `tectonic` exit 0) — **one manuscript, two markups**, 47/47 key figures identical |
| Built from | the six `paper/sections/v4-*.md` packages, applied as 100 (md) + 81 (tex) anchored replacements, each asserted to match **exactly once** |
| Audit | `c98_reproduce.py` → **ALL 283 CHECKS PASS**, exit 0; coverage **216 / 725 distinct quantity-numerals = 29.8%**, printed in §3.4 as a fixpoint |
| The pool conflict | 11 / 13 / 14 cells all reproduced exactly; **14 is primary** (`sm3` is in Table 2, and the ground for excluding it did not distinguish it from `nl1`) |
| B1 | **`identified` is withdrawn.** `dQ(base given batch)` = 4.11 on 2 df, **p 0.128 — unchanged at 14 cells**, because `sm3` brings a new batch as well as a new cell. Batch identity explains 95.8% against base's 92.8% |
| Deposit | 137 files / 6.2 MB, `make verify` 137/137, `make reproduce` exit 0 (266 checks, 1 section declared skipped) |
| Still open | `rp1` unscored (7 stale CSV rows); the nine `pp_`/`PP_` pairs still outside `dup_group`; the AdamW-level separation experiment of §9; the seven TODO-FOR-AUTHOR items below |

The 18 blocking items below are recorded as the cycle-100 gate found them. Cycle 101 acts on all
of them; `docs/CORRECTIONS.md` §128 is the authority on what was done and what was re-derived
rather than carried.

## Verdict — Q1 meta-gate re-run on DRAFT-v3

| | |
|---|---|
| Draft | `paper/DRAFT-v3.md` @ `617b6c8`, 27,854 words (19,639 body) |
| Cycle-98 gate on v2 | **DESK-REJECT**, defensibility **6/10**, 15 blocking |
| Cycle-100 gate on v3 | **MAJOR REVISIONS**, defensibility **8/10**, **18 blocking** |
| Why the count went UP while the score went up | v3 closed all 15 of v2's items. Sharper instruments then found 18 smaller ones. **Zero are science.** |
| GPU needed to clear all 18 | **0 jobs, 0 hours** |
| Science overturned by any of the 18 | **none.** One reproduction claim loses resolution (§4.1), one table gains two rows, one superlative dies |
| Cluster | 2 batches COMPLETE+UNSCORED, 10 jobs running, 3 pending |

**Why not desk-accept:** two printed assertions are false (§4.3 ρ superlative; §8 deposit guarantee).
**Why not desk-reject:** the substance gate fires on none of its three conditions — significance
evidence is everywhere, attrition is fully disclosed (§8 Table 3), no sub-MIE effect is sold as positive.

## The 18 blocking items

### A — red team v3, all 8 still open at HEAD (5 re-verified independently today)

| # | item | verified how |
|---|---|---|
| A1 | §4.3 + Fig 1 caption call CIFAR-100's ρ = 0.055 "the **smallest** value in the corpus". It is **3rd of 16** | ran `c98_figures.py --all --numbers`: aw1 0.0397, gm2 0.0504, gc1 0.0552 |
| A2 | §8: *"No number in this paper requires data that is not in that deposit"* is **false**. Every verbatim scorer verdict needs the excluded 42 GB probes | ran `c77_pp1_score.py` on the released tree → `0 probe dirs`, `P2 cannot be scored` |
| A3 | `dup_group` is claimed by §3.3 and §8 to mark 18 pairs. The CSV carries **6 rows / 3 pairs**, none of them `ml2` | read `results/all_runs.csv` |
| A4 | §4.1's parent cell is 3 seeds run twice (9 `pp_`/`PP_` pairs share `--seed`). Under the paper's own rule n=3 → t 1.78 UNRESOLVED, not t 2.52 | red team, from the runs' ARGS lines |
| A5 | "four **independent** submissions of the identical configuration" share seeds 0–2; §6.3 withdraws the batch variance component that made replicate ≠ rerun | red team |
| A6 | §7 T7 misstates what `c84_gn1_score.py` does (halts at T0.5, never reaches the quoted T0.6) and misstates `COMM_MAX` | red team |
| A7 | §4.7's table omits **both** `rl3` T cells under a sentence saying "ten cells, every one at t ≥ 3.3". One is t 3.09; the next paragraph quotes the other | read §4.7; rl3 T = +0.756 is quoted 4 lines below the table |
| A8 | Header + §3.4 claim `c98_reproduce.py` asserts *every* number. It has **51 `chk(` sites / 99 PASS** against **1,602** decimal numerals | `grep -c 'chk(' analysis/c98_reproduce.py`; audit exits 0 |

### B — claims calibration (hard-questions v3 required edits)

| # | item |
|---|---|
| B1 | **The 88% is label-invariant.** 3 of 4 levels are singletons, so `Q_within` is the 8 SGDm cells alone and **any** partition isolating those 3 returns 32.19/36.40. Abstract + Contribution 3 + Conclusion must stop saying "88% is one identified moderator" |
| B2 | **No pre-registered MIE for the corpus headline.** Batch-level bands exist (`aw1` +0.30, `bm2` ≥0.30, `pp1` ±0.15); the pooled +0.556 has none. State it, or report the headline as an estimate not a threshold clearance |
| B3 | **No practical-significance paragraph.** Scope (iv) volunteers "≈0.6 pp inside a method 1.8–4.2 pp behind cosine" and never answers it. The answer is designer-facing, not practitioner-facing |
| B4 | **The registered-scorer rule is stated without its 3 exceptions** (§4.4 cross-box pooling vs `c87_rl3_score.py`'s header; Table 2 row 4 re-derived past `gn1`'s halt; §4.8 declining `c87_hz3_score.py`'s 50-epoch window). List all three in one place |
| B5 | **`sm3` still not ingested** (2,113 → 2,125) while §5.4 reports a *computed* Holm adjusted p from it. Verified: `grep -c sm3 results/all_runs.csv` = **0** |
| B6 | Abstract says ResNet-**10**/18/34/50; every count-matched cell is 18/34/50 |

### C — gate static layer (new; found by running the gate code)

| # | item | gate rule |
|---|---|---|
| C1 | **There is no `paper.tex`.** The manuscript is markdown with literal ±, →, ≈, τ, ρ. The gate's first branch is *"No paper.tex to evaluate"* → automatic fail; S6 unicode fires on the source | S6 |
| C2 | `DOI: pending` ×2 and **six** `⟨…⟩` author-only placeholders remain | S9 |
| C3 | Draft-internal phrasing: `**Draft v3.**` header, *"An earlier draft of this paper claimed…"* ×3, "camera-ready" | S10 |
| C4 | **The abstract is 922 words against a 230-word cap.** 4× over. Desk-return at every venue in the table below | text_quality (blocking) |

### NOT a defect — gate artefact, do not chase

* The gate routes this paper to **Carlini's adversarial-robustness checklist** and demands a threat
  model and adaptive attacks. Cause: **one word**, `defence`, at DRAFT-v3 line 1690.
* Under the correct profile: `ml_eval_benchmark` coverage **0.82**, `reforms_ml_science` **0.85**.
  Their only applicable miss is the leakage check, which §3.3 and §7 T12 already answer in prose.
* `sections_over_budget` and `over_venue_cap` do **not** block — the gate gates them behind
  `track == systematic_review`. 19,639 body words is a **venue-fit** problem, not a gate failure.

## Venue table (as-it-stands = the 18 open; after = the 18 closed)

| venue | as-is | after the 18 | the one thing that moves it |
|---|---|---|---|
| NeurIPS / ICML / ICLR | **1–3%** | 5–10% | a transfer probe **outside** MetaOptimize. Nothing else gets a rigor-and-nulls paper onto a main track |
| **TMLR** ← target | **25–30%** | **65–75%** | no novelty bar, no page limit, negative results in scope. Fix A1/A2 and this is the natural home |
| Machine Learning (Springer) | 15–20% | 50–60% | LaTeX production (C1–C4) + artefact DOI |
| Neurocomputing / IJMLC | ~30% | ~50% | reviewers want a *method*; "we could not find the mechanism" reads worse here than at TMLR |
| Workshop (OPT / HiLD) | 40% | ~75% | cut to one story + one figure; 4 pages |

## Cluster — verified on alice today

| batch | jobs | state | Rule 20 | scorer | next |
|---|---|---|---|---|---|
| `sm4` | 12 | **ALL COMPLETED** (00:42–00:53 each) | **PASS** — 1 `--alg-meta`, reads `RMSProp`, all 12 | `analysis/c97_sm4_score.py` (58/58 selftest) | **SCORE IT** |
| `bm2` | 12 | **ALL COMPLETED** | **PASS** — 1 `--alg-meta`, bases SGD ×6 / RMSProp ×6, seeds 3–5 | `analysis/c97_bm2_score.py` | **SCORE IT** |
| `rp1` | 12 | 2 COMPLETED, 10 RUNNING (~40 min in) | — | `analysis/c97_rp1_score.py` | wait |
| `hz3`-R2 | 3 | **PENDING** (4848866–68, Priority; gpu-2080ti-11g congested) | **OWED** — no ARGS line exists yet | `analysis/c87_hz3_score.py`, reused unedited | Rule 20 check the moment they start; `scancel` on mismatch |

**§3.5 is stale in the draft: it calls `sm4` "running". It has completed.**

## What the four in-flight batches change when they land

| batch | closes | does NOT close |
|---|---|---|
| `sm4` | **T1, the largest scientific hole.** 367/367 partition runs are Lion-meta; this is the first non-Lion cell. Also runs mechanism candidate 8 (the second-moment corner) that `sm3` was void for. Registered: REFUTED if D ≥ +0.55; CONSISTENT if D ≤ +0.279 with 95% UB < 0.55 | the corpus stays Lion-only. One cell is not an axis |
| `bm2` | the moderator's weakest flank — SGD and RMSProp stop being single-batch (`nl1`) levels | **B1.** A second batch at two levels does not make a four-level Q partition non-tautological. The label-invariance edit is required whatever bm2 says |
| `rp1` | the alignment null's power (se 0.157 → ~0.09) **and** the permutation-seed/run-seed confound. The only batch that can move a headline in either direction — pre-registered to demote §4.6 to UNDERDETERMINED if it still spans half of D | — |
| `hz3`-R2 | the one box-mismatched seed in the budget cell; restores 6v6 box-matched | the §4.8 GROWS-vs-decline disagreement. That is a **metric-window** choice (50-epoch vs plateau5), not a data problem |

**None of the four touches any of the 18 blocking items.** Do not wait on the cluster to start the text pass.

## Next cycle, in order

1. **Score `sm4` and `bm2`** — both registered scorers, **unedited**, quote the verdicts (Rule 16).
   Do this **before** the text pass: their outcomes rewrite §3.5, §4.4 and §5.4, and editing those
   twice is waste. Both are Rule-20 clean; the sweep is in this file.
2. **Kill the two false assertions.** A1 (delete the ρ superlative, §4.3 lines 799 + 816 and the
   Fig 1 caption; the commensurability argument survives verbatim) and A2 (correct §8; ship the
   kilobyte-scale per-run box-occupancy / `N_eff/m` summary and give each scorer a `--summary` path
   so the registered verdicts regenerate without the 42 GB).
3. **`analysis/args_repair.py --apply`**, re-mint `MANIFEST.md5`, drop the `PENDING_DUP` fallback
   from `c98_figures.py`, add the nine `pp_`/`PP_` pairs (census 18 → 30). Clears A3, feeds A4.
4. **Ingest `sm3`** with `aggregate.py` **unedited** (2,113 → 2,125; its last-wins parser writes
   `meta=Lion` by itself), add the `CELLS` entry, regenerate figures, re-run `c98_reproduce.py`.
   Clears B5. Table 2 → 17 cells; abstract counts and two captions move with it.
5. **B1–B4 + B6** text edits. B1 is the highest-value sentence in the cycle.
6. **A5–A8** text edits; extend `c98_reproduce.py` with ρ per cell, §4.2's U table, §4.1's
   contrasts, §5.6's four slopes, §5.8's LOO table, Appendix B's arm means. That would have caught A1.
7. **Production: build `paper.tex`.** C1–C4 in one pass — LaTeX source, unicode → macros, a
   **≤230-word** abstract (the 922-word block becomes §1), delete draft-internal phrasing, mint the
   DOI, fill the six `⟨…⟩`.
8. Verify `hz3`-R2's ARGS/ENV when it starts; score `rp1` when it finishes.

## Standing rules in force

| # | rule |
|---|---|
| 16 | If a batch has a registered scorer, run it **unedited** and quote its verdict |
| 20 | A batch's science is what the runs' own `ARGS:` line says, never what the script header says |
| 21 | No batch is submitted without a registered scorer |
| 22 | Every pooled quantity names the precision it was computed at (full-precision arm means here) |
| — | `plateau5` is PRIMARY. The CSV `plateau` column (mean-of-last-20) is **banned** |
| — | BATCH is the unit of replication; primaries must be within-batch |
| — | `BETA_CLIP` uses a **colon**. Box occupancy comes from per-coordinate rails `n_at_lo`/`n_at_hi` |

## Corpus, unchanged this cycle

| | |
|---|---|
| Runs | 2,113 rows admissible-gated to 1,671; +12 `sm3` un-ingested; +24 `sm4`/`bm2` complete, unscored |
| GPU-h | ~1,582 spent, ~1,594 with `sm3`; ~30 more in flight |
| Headline | D > 0 in **16/16** count-matched cells; SGDm pool **+0.556 ± 0.045**, Q 4.21/7, τ 0.000 |
| Alignment | bounded null, A = −0.009 ± 0.157, CI [−0.317, +0.298] = [−55%, +51%] of D |
| Mechanism | 3 refuted (M2/M3/M6), 1 narrowed (M4), 1 not separable (M7), 3 undecidable (M1/M5/M8) |
| Known dead ends | TinyStories (≥3 weeks, nobody asked); more G cells; more seeds on existing D cells |

## TODO-FOR-AUTHOR — the seven decisions the `production` package could not take

Added by the cycle-101 `production` package (C2/C3/C4). **None of these is a placeholder in the
manuscript:** every one has finished prose in place that is true of the paper as it stands. Each
row says what to edit if the answer changes. Full context in `paper/sections/v4-production.md` §11.

| # | decision | what the paper says now | if it changes |
|---|---|---|---|
| 1 | **Does the originator of the hierarchical partial-pooling design join the author list?** `docs/PLAN-appendix-collab.md:133` names him — *"Arsalan — co-author, not acknowledgement. He originated the hierarchical partial-pooling idea"* — i.e. a co-author of the parent paper. The name was **not** put into the manuscript: an author list is your decision and the source is an internal advisory note. | Two authors. Competing interests discloses that §5.9's design came from *"a researcher who is also a co-author of the parent work and who is not an author of this paper"*, and that §5.9 is negative about it. | Add to the author block and CRediT (Conceptualization, §2.4/§5.9); **add a second COI sentence naming a second parent co-author among the authors**; get his affiliation + ORCID from him. |
| 2 | **Any grant to declare?** | *"received no dedicated project funding and no grant"* | replace with funder + identifier. Nothing was invented. |
| 3 | **`Funding acquisition` sits on Saber's CRediT roles while Funding says there was no grant.** Not edited — removing a CRediT role is a statement about a person. | both stand as written | drop the role, or say in Funding that it refers to the institutional compute allocation |
| 4 | **Correspondence address** — your own address of record on this repo was used, not an institutional one. | `mohammadrezaahmaditeshnizi@gmail.com` | swap for the LIACS address; two files (DRAFT-v3 End matter, `paper.tex` `\thanks`) |
| 5 | **ORCIDs** — omitted rather than guessed. | `release/CITATION.cff` has `authors:` with names + affiliations, no `orcid:`, and a comment saying why | add `orcid:` under each author, rebuild the deposit |
| 6 | **Mint the DOI** — needs an archive account and publishes a permanent public record, so it is yours to do. | the paper prints **no DOI** and cites the artefact by commit; `CITATION.cff` has **no** `identifiers:` block, on purpose | reserve it, then write the same string into `release/README.md`, `CITATION.cff` and the Data-availability statement; rebuild. `release/README.md` § *Minting the DOI* has the five steps |
| 7 | **Rebuild the deposit from a clean checkout** — the current build stamped `DIRTY`, correctly. | warning is printed in `release/README.md` | after the integration commit: `python3 analysis/c98_release.py && cd release && make verify` |

**1 and 6 block submission. 2–5 and 7 are one-line edits.**

## Corpus, AFTER the `6a374f4` ingest — re-derived by the production package

The table above this section still prints the pre-ingest numbers; these are the current ones, and
`analysis/c98_reproduce.py` now asserts all of them (**ALL 188 CHECKS PASS, exit 0**).

| | pre-ingest | now |
|---|---|---|
| `.out` files on the two clusters | 2,193 | **2,241** |
| …with an `ARGS:` line | 2,189 | **2,237** (4 infrastructure jobs have none) |
| crashed before epoch 1 | 64 | **64** (unchanged; 2,237 − 2,173) |
| rows in `results/all_runs.csv` | 2,113 | **2,173** |
| admissible | 1,671 | **1,724** |
| GPU-h | 1,582.2 | **1,624.8** (admissible: 1,558.4) |
| truncated (`window_ok=1, complete=0`) | 17 | **24** — the 7 new ones are in-flight `rp1` snapshots at 82–87/100 |
| repeated-flag runs (`argsline_guard.py`, unedited, over all 2,241) | 36 | **36** — still exactly `ml2` 24 + `sm3` 12 |

Two manuscript sentences became **false**, not merely stale, and have exact replacements in
`v4-production.md` §5.3: *"None of the 17 is in a count-matched arm"* (seven of the 24 are
`permnode` arms) and *"all 214 uniform-chunk, `nodewise1d` and `permnode` runs are admissible"*
(now 238 of 238 excluding the in-flight `rp1`, 249 of 256 including it). A third, Appendix A.1's
*"367/367 is meta = Lion"*, is falsified by `sm4`: of the 420 admissible partition-family runs,
**408 are Lion and 12 are RMSProp**.
