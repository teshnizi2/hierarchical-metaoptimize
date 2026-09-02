# STATUS — operator dashboard

Updated 3 Sep 2026 (cycle 107, **final pre-submission gate**). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **131**) > `docs/FINDINGS.md` > everything else.
HEAD = this dashboard commit. **Manuscript, code and deposit unchanged since `ea9058b`** — this cycle edited no markup, no scorer and no run. Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**71 pp**, `tectonic` exit 0, 0 TeX errors, 0 undefined refs).

## Verdict — Q1 meta-gate re-run on `paper.tex`

| | |
|---|---|
| Cycle 98 (v2) | **DESK-REJECT**, 6/10, 15 blocking |
| Cycle 100 (v3) | **MAJOR REVISIONS**, 8/10, 18 blocking |
| Cycle 103 (v4) | **MAJOR REVISIONS**, 7/10, 15 blocking |
| Cycle 105 (v5) | **MAJOR REVISIONS**, 7/10, 7 blocking |
| **Cycle 107 (candidate)** | **MAJOR REVISIONS**, **8/10**, **2 blocking** |
| Gate static half | **`structural_gaps = []`, `passed = True`** on `track=empirical` — second cycle running |
| Prior 7 items (B1–B7) | **7 / 7 genuinely closed.** Re-derived, not read |
| B8 (major, non-blocking) | **closed** — Table T re-derived cell-for-cell on all four endpoints, exact match |
| Why not desk-accept | **two numbers are false as printed**, both in the end matter, neither touching a result |
| GPU to clear both | **0 jobs, 0 hours.** ~10 min of editing + one audit fixpoint |
| Science overturned | **none.** The calibration repair is itself correctly calibrated — verified by independent re-implementation |

**Not desk-reject:** the gate's own blocking list is empty and the deepest methodological attack is repaired.
**Not desk-accept:** `6.3 MB` and `entry 128` are both false, and the house rule is *correct, do not soften*.

## Gate checks — executed, not paraphrased

`/Users/teshnizi/PaperFactory/paperfactory/agents/q1_meta_gate.py`, `_static_checks` + `_apply_static_gate`, `track=empirical`.

| check | rubric | value | verdict |
|---|---|---|---|
| `placeholder_figures` | S1 | `False` | PASS |
| `hardcoded_hex` | S2 | `False` | PASS |
| equations labelled + `\ref`'d | S3 | 12 envs, 12 labels, **0 unreferenced** | PASS |
| `unresolved_refs` / orphans / dupes | S4 | 74 labels, 74 refs, **0 / 0 / 0** | PASS |
| `endmatter_missing` | S5 | `[]` — all 6 + AI-assistance disclosure | PASS |
| `unicode_math` | S6 | `False` | PASS |
| `hyperref` | S8 | `\usepackage[hidelinks]{hyperref}` | PASS |
| TODO / TBD / `??` / DOI stub | S9 | **0 / 0 / 0 / 0** | PASS |
| draft-internal phrasing | S10 | 0 | PASS |
| absolute novelty claims | S11 | 0; **T11 explicitly disclaims priority** | PASS |
| compile hygiene | S12 | exit 0, 71 pp, 0 `!`, 0 undefined, **3 overfull hbox at the pre-existing widths** | PASS |
| `abstract_missing_items` | — | `[]` | PASS |
| `reporting_missing_items` | — | `[]` (`se_empirical`, **17/17**) | PASS |
| `text_quality_defects` | — | `[]` (abstract 0, section 0, caption 0) | PASS |
| abstract length | — | tex **219** w, md **228** w (cap 230); longest sentence 31 w | PASS |
| `empirical_substance_gaps` | — | `[]` (significance signal present) | PASS |
| `analysis/c98_reproduce.py` | — | **exit 0, ALL 565 CHECKS PASS**, census at fixpoint | PASS |
| tex ↔ md numeric diff | house | md-only 5 arXiv ids + 2× `9.0`; tex-only 21 layout params / parent-§ numbers. **0 result numbers diverge** | PASS |

**Track sensitivity — unchanged fragility.** `_resolve_track` defaults to `systematic_review` with no idea blob. On that track four more checks block: `over_venue_cap` (body **32,027** w vs cap 5,000), `sections_over_budget` (6 sections; Results +949%), `likely_text_heavy`, `sections_without_display_support` (Conclusion 1,009 w; Discrepancy register 1,305 w). `display_items_total = 37`. Irrelevant at TMLR; fatal at a page-limited venue.

## Independent bootstrap — re-implemented from scratch, nothing imported from `c98_figures` / `c99_qcalibration`

Own CSV read, own admissibility, own `dup_group` collapse, own Welch / DerSimonian–Laird / Cochran `Q`, **numpy PCG64** (not the paper's Mersenne Twister), **200,000 draws**, seeds 1–3 + 7.

| quantity | paper prints | independent re-derivation | verdict |
|---|---|---|---|
| Welch df of the 14 cells | 2.04–9.68, median 2.91 | 2.04–9.68, median 2.91, mean 3.88 | **exact** |
| FE pool / `Q` / τ / I² | +0.530 ± 0.029, 102.47/13, 0.295, 87% | +0.5297 ± 0.0294, 102.4739, 0.2948, 87.3% | **exact** |
| MC `p`(Q = 102.47) | **0.013** (0.002 common-sd); "0.011–0.013 over 3 seeds, 0.012 at 200k" | **0.0115** at 200k; 0.0111/0.0111/0.0112/0.0122 at 20k | **confirmed, and the paper quotes the conservative end** |
| between-base `Q` = 95.12/3 | MC **0.005** (0.0007) | **0.0045** (0.00072) | **confirmed** |
| within-level `Q` = 7.36/10 | χ² 0.69, MC **0.86** | χ² 0.6912, MC **0.851** at 200k (registered 20k run = 0.8554 → 0.86) | confirmed; 2nd decimal is 20k noise |
| four level MC `p` | 0.70 / 0.30 / 0.25 / 0.86 | 0.6929 / 0.3045 / 0.2489 / 0.8611 | **exact** |
| null `Q`/13 mean, median, p95 | 26.9, —, — | 26.75, 21.40, 61.73 | **confirmed** |
| SGDm null median / percentile | 9.4 / 14th | 9.411 / 13.9th | **exact** |
| τ, I² recentred | 0.271 pp, 74% | 0.271 pp, 73.9% | **exact** |
| SGDm ±1.96 se coverage / calibrated half-width | 73% / ±0.121 | 73.0% / 0.1210 | **exact** |
| 14-cell FE coverage / half-width | 65% / 0.089 | 65.8% / 0.0898 | **exact** |
| pooled within-arm sd | 0.186 pp on 70 df | 0.1856 on 70 df | **exact** |
| `Q > 3.841` realised size / crit | 0.10 / 6.22 | **0.1019 / 6.222** (600k draws) | **exact** |
| weight-free permutation | η² 0.840, rank 9 of 45,045, `p` 0.00020 | **η² 0.8396, rank 9/45045, p 0.000200** | **exact** |
| published weighted cross-check | rank 14, `p` 0.00031 | **rank 14, p 0.00031** | **exact** |
| four endpoints, MC `p` | 0.013 / 0.24 / 0.90 / 0.16 | 0.0118 / 0.240 / 0.902 / 0.157 | **exact** |
| their between-base MC `p` | 0.005 / 0.099 / 0.60 / 0.025 | 0.0046 / 0.100 / 0.602 / 0.024 | **exact** |
| G-family + momentum residual | 0.42 / 0.26 / 0.12 / 0.074 | reproduced through the registered module at its own seed | **confirmed** |
| "3 of 9 χ² readings clear `p` < 0.05 calibrated" | 3 | **3** (plateau5 total, plateau5 between, final_test between) | **exact** |
| "the correction moved every `p` **up**" | universal | **true on all 14 calibrated statistics I checked** | **holds** |
| τ Q-profile limit, the one that moves the other way | 0.109 → 0.097 | 0.109 (χ²₇) → 0.0967 calibrated | **printed at both sites** |

**Other headline claims, re-derived independently:**

| claim | re-derived | verdict |
|---|---|---|
| `D` sign 20/20, 20/20, 20/20, 19/20 | 20/20, 20/20, 20/20, **19/20** (bm2-SGD, final_test, −0.073) | exact |
| zero attrition inside the cells | **154/154 admissible** across the 40 primary arms | exact |
| Table T (Contribution 6) | **all 15 rows reproduce to 3 dp**, incl. `t` | exact |
| endpoint knife on T | 12/12, 12/12, 12/12, 12/12 positive; `t ≥ 3` in **12 / 12 / 8 / 6**; AdamW+Lion pool +0.007 / +0.051 / −0.111 / +0.106, all inside ±0.15 | exact |
| T4 deficits 1.807 / 2.558 / 4.214 | −1.807±0.095, −2.558±0.063, −4.214±0.260; SGD lr grid is an interior max | exact |
| B4 log counts | `find` + `grep -L` on both mirrors → **2,241 / 2,237 / 2,113 / 128** | exact |

## The 7 prior blocking items — closure verified by execution

| # | verified how | state |
|---|---|---|
| B1 | full independent bootstrap above; T13 prints both `p`'s at every resolving site; tex disclosure vocabulary: `Monte-Carlo` ×38, `calibrat` ×17, `simulat` ×22, `anticonservative` ×6 (all were **0** at cycle 105) | **CLOSED** |
| B2 | abstract carries `calibrated 95% CI ±0.121`; T13 item 3 prints 73% / 65% coverage; FE pools labelled as such | **CLOSED** |
| B3 | `88.4` now ×3 in tex, ×3 in md; all three past-tense and scoped to the superseded 11-cell pool | **CLOSED** |
| B4 | exact scoped counts printed; the four ARGS-less jobs named; job-id bounds given; word "most" absent | **CLOSED** |
| B5 | abstract names SGD+cosine / AdamW+cosine R34 / AdamW+cosine R50; superlative gone; `se_empirical` still 17/17 | **CLOSED** |
| B6 | **10 design points** throughout; `11 distinct design points` absent; §5.6 refit at 9 CIFAR-10 points | **CLOSED** |
| B7 | audit §[16] prints **8 rows** (4 per markup), all PASS; §3.4 prose names both files and the measurement file | **CLOSED** |
| B8 | Table T endpoint knife present at tex:2483–2500 and reproduces exactly | **CLOSED** |

## NEW blocking items — found this cycle, shortest path first

| # | item | evidence | cost |
|---|---|---|---|
| **N1** | **Data Availability says the archive is `6.3 MB`.** It is **6.4 MB** — 139 manifest files, **6,440,785 bytes**, while §8 says `6.4 MB in 139 files`. The two statements are 635 lines apart in the same document and contradict each other. Internal contradiction in a Q1-mandatory end-matter section | `paper.tex:4660`, `DRAFT-v4.md:3735` vs `paper.tex:4025`, `DRAFT-v4.md:3216`; `MANIFEST.md5` header | 2 min |
| **N2** | **A.8 says "The correction register runs to entry 128."** `docs/CORRECTIONS.md` runs to **131** — entries 129, 130 and 131 were written by the three cycles that produced this candidate | `paper.tex:4559–4560`, `DRAFT-v4.md:3658`; `grep '^## 1' docs/CORRECTIONS.md` → 131 | 2 min |
| N3 | **hazard, not yet false.** The same A.8 sentence says "nothing awaiting ingest". True right now; **becomes false the moment the `hz3q` quartet finishes** (~02:30 CEST). Either ingest+score it or scope the sentence to the run table | `sacct` → 4864632–35 RUNNING, 01:10 elapsed | scope: 2 min |

- Both N1 and N2 sit inside the **56.2%** of quantity-numerals `c98_reproduce.py` does not assert — exactly the gap §3.4 declares. Neither is a result. Third consecutive cycle in which an integration left a stale integer behind.
- After the edits: re-run `python3 analysis/c98_reproduce.py` to a census fixpoint, then `tectonic`. Expect no numeric movement (`6.3`→`6.4` and `128`→`131` are both unasserted).

## Polish, non-blocking

- §3.3's universal *"on every statistic we have calibrated the correction moved the `p` up"* is literally true (the τ exception is an interval limit, not a `p`), but sits one clause from T13 item 4. Scope it to `p`-values.
- Abstract's *"homogeneous against that null"* has no antecedent for **that** inside the abstract.
- Figure 2's in-panel `MC 0.86` inherits the 20k second-decimal noise (200k value 0.85). Harmless; both read "homogeneous".
- `release/` on disk carries **3 stray `__pycache__/*.pyc`** from the last `make reproduce`. Manifest is 139 and correct; rebuild clean before upload.

## TODO-FOR-AUTHOR — verified 3 Sep 2026, nothing invented, nothing dropped

| # | item | state | evidence |
|---|---|---|---|
| A1 | **Author-list decision on the originator of the §5.9 hierarchical-pooling design** (co-author of the audited parent work; §5.9 is negative about it) | **OPEN** | Competing Interests: *"proposed to us by a researcher who is also a co-author of the parent work and who is **not** an author of this paper"* + *"we regard origination of a design at that specificity as a substantial intellectual contribution"*. The paper asserts a substantial intellectual contribution and then does not confer authorship — resolve before submission |
| A2 | **Mint the artefact DOI** | **OPEN** | *"The deposit has no DOI, because it has not been deposited"*; `CITATION.cff` carries no `identifiers:` block. Honest, not false — but the deposit is the paper's only artefact identifier |
| A3 | grant identifier | **CLOSED — none exists** | Funding: *"no dedicated project funding and no grant"* |
| A4 | **"Funding acquisition" on S. Salehkaleybar's CRediT contradicts a Funding statement that says there was no grant** | **OPEN** | Author Contributions lists it; Funding denies it. Same defect class as N1/N2 — drop the role, or scope Funding to the ALICE allocation |
| A5 | **Institutional LIACS correspondence address to replace the gmail of record** | **OPEN** | gmail at **2 sites**: `\thanks` (`paper.tex:56`) and Correspondence (`paper.tex:4774`) |
| A6 | **ORCIDs for both authors** | **OPEN** | `grep -ic orcid paper.tex` → **0** |
| A7 | **Approval to rebuild the deposit from a clean checkout at the final submission commit** | **OPEN, narrowed** | `release/README.md:9` now reads *"Built 2026-09-02 from commit ea9058b…"* with **no DIRTY warning**, and `ea9058b` is the commit that built it. What remains: rebuild once at the final commit, and drop the 3 stray `.pyc` |

## Submission readiness

**Send to TMLR today: NO. After N1 + N2 (≈10 min, zero GPU): YES.**

- The four author decisions (A1, A4, A5, A6) are not gate items but **A1 and A4 should be settled before upload** — A1 is an authorship-ethics exposure, A4 is a printed self-contradiction.
- A2 and A7 strengthen the artefact; neither blocks TMLR, which accepts a repository link.
- **Defensibility 8/10** (was 7). The deepest attack available to a referee — the wrong reference distribution for `Q` — is found, owned, calibrated, and independently reproduced to the digit. What is left is bookkeeping and reviewer burden.

| venue | fit | P(accept) as-is | P(accept) after N1+N2 | note |
|---|---|---|---|---|
| **TMLR** | **best** | **0.62** | **0.72** | Criterion 1 (claims supported) is now the paper's strongest axis; criterion 2 (audience interest) easily met. No page limit. Main risk is **reviewer burden at 71 pp**, not correctness |
| TMLR + *Reproducibility Certification* | best | — | **0.60** | request it at submission; `make reproduce` + 139-file md5 manifest is built for exactly this |
| Machine Learning (Springer) | good | 0.35 | **0.48** | empirical-audit shape fits; long form tolerated |
| JMLR | fair | 0.10 | **0.16** | wants a methodological/theoretical contribution, not a measurement |
| NeurIPS D&B | fair | 0.14 | **0.20** | artefact is strong; the contribution is a measurement, not a resource |
| ICML / NeurIPS / ICLR main | poor | 0.08 | **0.12** | negative-leaning audit, +0.6 pp at CIFAR scale, 8–9 pp limit |
| Neurocomputing / IEEE Access | poor | 0.55 | **0.62** | would accept, but 32,027-word body vs a ~5,000-word band forces a rewrite that destroys the evidence chain |

**Recommendation: TMLR, with a Reproducibility Certification request.** Consider a 12–15 pp main body with §§5–8 moved to a clearly signposted appendix — it does not change a number and it halves the burden that is the one real acceptance risk.

## Cluster — `hz3q` quartet (disclosed sensitivity analysis on hz3 seed 5)

| | |
|---|---|
| State | **RUNNING**, 01:10:14 elapsed — 4864632 `hz3q-node-s5`, 4864633 `hz3q-ch-s5`, 4864634 `hz3q-n1d-s5`, 4864635 `hz3q-c23-s5`, all on node883 (L4) |
| Expected finish | ~02:30–03:10 CEST 3 Sep; Slurm cap 04:00:53 |
| `.out` on cluster | 4 present, incomplete |
| Local mirror | **not synced.** `results/all_runs.csv` = **2,173 rows**, unchanged |
| Paper dependency | **none.** `hz3q` appears nowhere in `paper.tex` or `DRAFT-v4.md` |
| On completion | sync → `python3 analysis/c99_hz3q_score.py --runs runs --probes runs/hz3` → re-run `c87_hz3_score.py` **UNEDITED** and confirm unchanged (non-overwrite check, not optional) → ingest 4 rows named `hz3q-*`, **no `dup_group`, no supersession**. Not a replication, not a new batch, not a new design point, not a new cell |
| Actions this cycle | **none.** No `sbatch`, no `scancel`, nothing disturbed |

## Known-open, by design

- **Six χ² `p`-values remain uncalibrated**, enumerated by name in §3.3 with the direction argument (all support null readings; every calibrated statistic moved its `p` up).
- **Appendix A.3b's `rp1` seed disagreement** is unreconciled by design: run seed `F(5,10) = 4.634, p = 0.019` against the corpus seed null `F 1.21, p 0.213`.
- **§4.7 still opens "The practitioner's move"** four paragraphs before "this paper recommends nothing". One-word repair (`designer's`), own entry.
- **§4.7's `bn1`/`ml2` footnote prints `z 1.06`**; re-derives to 0.1927/0.1805 = 1.068 → **1.07**. Pre-existing, unasserted, no package owns it.
- **`c97_bm2_score.py --outs` crashes** (`AttributeError: 'float' has no attribute 'strip'`). The `--csv` path — the one the verdict was issued from — is unaffected. Logged, not edited (RULE 16).
- **Nine `pp_`/`PP_` cross-submission pairs** remain outside `dup_group` (A.4).

## House rules (unchanged)

- `plateau5` is PRIMARY; the CSV `plateau` column is BANNED as a primary, read only as an endpoint disclosure.
- RULE 16 — run a registered scorer UNEDITED and quote its verdict; documented args are not edits.
- RULE 20 — a batch's science is what the runs' own `ARGS:` line says, never the script header.
- RULE 21 — no batch is submitted without a registered scorer committed first.
- Re-derive every number at write time. Never quote prose.
- **Do not close an item by softening wording. A false claim is deleted or corrected.**
- Never fabricate an affiliation, ORCID, grant number or DOI — it goes on TODO-FOR-AUTHOR.
