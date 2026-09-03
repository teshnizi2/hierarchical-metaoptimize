# STATUS — operator dashboard

Updated 3 Sep 2026 (cycle 111, **post-desk-accept polish**). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **135**) > `docs/FINDINGS.md` > everything else.
Manuscript at `ae3951a`; HEAD = this dashboard commit. Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**75 pp**, `tectonic` exit 0, 0 TeX errors, 0 undefined refs, 0 orphan labels). Corpus = **2,177 rows**.
**No Slurm job was submitted this cycle. Cluster access was one read-only `rsync` (1.08 GiB of probe records). Both queues empty.**

## Verdict

| | |
|---|---|
| Cycle 107 (v6) | **MAJOR REVISIONS**, 8/10, 2 blocking |
| Cycle 110 (v7) | **DESK-ACCEPT**, **9/10**, **0 blocking** |
| **Cycle 111 (v8)** | **DESK-ACCEPT holds.** 4 of the gate's 4 named improvements applied; 2 owed items closed |
| Gate static half | `structural_gaps = []`, `passed = True` on `track=empirical` |
| Audit | `c98_reproduce.py` **exit 0, ALL 636 CHECKS PASS** (was 592), census at fixpoint **628 / 409 / 892 / 45.9%** |
| tex↔md | `paper_numeric_diff.py` — **8 residuals, all pre-existing, ZERO new** in either direction |
| Science overturned | **none.** Contribution 1 verified intact at 4 sites; the withdrawal stays confined to the slope |
| GPU to reach submission | **0 jobs, 0 hours.** Six author items, all administrative or editorial |

**Ready to submit: NO.** Not for any manuscript defect — for the six author items below.

## What cycle 111 changed

| id | edit | landed in |
|---|---|---|
| **R1** | Abstract's threats paragraph now carries the budget decline and the withdrawal: *"Within one batch, on repaired data, the gap declines from +0.632 pp at 100 epochs to +0.394 at 300, withdrawing our earlier flatness claim."* | abstract, both markups |
| **R2** | T9's clip-box / GPU-class caveat rescoped from "§4.8" to **the six-seed as-published reading alone**, with an explicit bold statement that neither exception attaches to the other two readings | §7 T9, both markups |
| **R3** | The linear zero-crossing (`0.394/(0.238/200) = 331` → **631**) is now printed, then answered with **four measured facts** instead of an assertion | §4.8, both markups |
| **R5** | The reversal's mechanics: dropping the bad seed does **not** produce it; the replacement does, by location **and** precision in equal parts — plus the leave-one-out table | §4.8, both markups |
| owed (i) | 4 × `probe.jsonl` synced from ALICE → **H1 now PASSES locally** | `runs/hz3/probe_*_hz3q_s5/` |
| owed (ii) | Figure 3 panel (b) **redrawn with all three readings**; caption in the same commit | `c98_figures.py`, both captions |
| audit | **44 new assertions**; §3.4 self-census re-iterated to a fixpoint | `c98_reproduce.py`, both markups |

## Mechanical verification — executed, not paraphrased

| check | baseline `fe957e4` | now |
|---|---|---|
| `c98_reproduce.py` | exit 0, ALL **592** PASS | **exit 0, ALL 636 PASS** |
| census fixpoint | 584 / 389 / 872 / 44.6% | **628 / 409 / 892 / 45.9%** |
| `paper_numeric_diff.py` | 3 tex-only + 5 md-only | **the same 8, byte for byte — 0 new** |
| `_abstract_defects` tex / md | 219 / 228 words, `[]` / `[]` | **217 / 228 words, `[]` / `[]`** (cap 230) |
| longest abstract sentence | 31 / 32 words | **30 / 31** (cap 62) |
| `tectonic -X compile` | exit 0, 74 pp | **exit 0, 75 pp** |
| TeX errors / undefined / `??` / orphan labels | 0 / 0 / 0 / 0 | **0 / 0 / 0 / 0** (74 labels, 74 refs) |
| `Overfull \hbox` | 2 (7.28497 pt, 12.25499 pt) | **the same 2** |
| `c99_hz3q_score.py --selftest` | 59/59 PASS | **59/59 PASS** |
| `c99` H1 box gate | **REFUSED** — no probe records | **H1 PASS, worst coordinate fraction 0.000000, n=500/arm** |
| `c99` H2 / H3 / HC | `-0.238 / 0.093 / -2.57` · `+0.394 / 0.093 / +4.25` · `+0.134` | **identical** |
| `c87_hz3_score.py` unedited | `SURVIVES`; `MECHANISM SURVIVES THE HORIZON`; `+0.229 → GROWS`; `grep -c hz3q` 0 | **identical, still 0** |
| `dup_group_guard.py` | 21 groups / 42 rows / 3 superseded, PASS; selftest 5/5 | **identical** |
| deposit, **clean checkout at the new HEAD** | — | `make verify` **140 files, 0 bad**; `make reproduce` cold **exit 0, ALL 547 PASS** (`[7] BUDGET` skips soft — R8); after `make logs` **exit 0, ALL 628 PASS** |

## Contribution 1 — unweakened, checked at four sites

| site | state |
|---|---|
| Abstract | *"wins all twenty count-matched cells … the effect is +0.556 ± 0.045 pp (calibrated 95% CI ± 0.121), homogeneous against that null (Q 4.21, median 9.4)"* — every number and qualifier kept |
| §1 Contributions, item 1 | **untouched, byte for byte** |
| §4.8 | insertions only; no existing sentence deleted or softened, including *"has read it backwards"* |
| §9 | *"…two findings, of which the second does not weaken the first"* — **unchanged** |

- `hz3q` still enters **no cell** of Table 2, and is neither a replication, a design point nor a cell.
- **"Declines" cannot be read as "disappears"** — now at **4** guard sites: `paper.tex:1283` *"does not vanish"*; `:2741` *"has read it backwards"*; new R3 *"The measured ladder stops at 300 epochs and so does the claim"*; new R5 *"a decline resolved at this budget and this design point rather than a law"*.

## Red team — 5 of 10 closed, 0 blocking

| # | finding | state |
|---|---|---|
| R1 | Abstract carried no trace of the reversal | **CLOSED** — one clause, inside the 230-word cap, measured |
| R2 | §4.8's budget table has no caption and an undefined `se` column (table = sem of six per-seed D, prose = Welch 6v6) | **open**, med |
| R3 | No rebuttal to linear extrapolation | **CLOSED** — arithmetic printed, four measured facts against it |
| R4 | Registered bar `\|t\| ≥ 2.0` at df 5 is two-sided α ≈ 0.102, undisclosed. Helps: the bar was not shopped, and repaired `p = 0.0500` sits at the line anyway | **open**, low |
| R5 | Reversal's mechanics unstated | **CLOSED** — location × precision, 50.1/49.9 in logs, plus leave-one-out |
| R6 | T9 read as scoping all three readings | **CLOSED** — scoped to the as-published reading, measured off the headers |
| R7 | `f3_budget` panel (b) drawn on the archive | **CLOSED** — redrawn, all three readings, archived ones kept |
| R8 | Deposit `make reproduce` cold skips `[7] BUDGET`; fails **soft** and announces it. After `make logs`: exit 0 | **open**, low |
| R9 | **75 pp / ~34k body words.** No TMLR cap, but the far tail — reviewer-burden desk-return is the biggest venue risk | **open**, med |
| R10 | 8 tex↔md numeric residuals, all pre-existing. One is a real md prose gap (`F(39,172)`: `paper.tex:1845`, `:4658`; `DRAFT-v4.md:3739` only) | **open**, low |

## TODO-FOR-AUTHOR — 6 open, all outside agent scope

| # | item | evidence it is still open | effort |
|---|---|---|---|
| 1 | **CRediT ↔ Funding contradiction** — "Funding acquisition" on S. Salehkaleybar against a Funding statement reading "no dedicated project funding and no grant" | both strings present verbatim in the end matter | 1 min |
| 2 | **LIACS correspondence address** to replace the gmail of record, **2 sites** | `paper.tex:56` `\thanks{}` and `\paragraph{Correspondence.}` | 2 min |
| 3 | **ORCIDs, both authors** | `grep -ci orcid` = **0 / 0** | 5 min |
| 4 | **Deposit rebuild at the submission commit** | `release/` is a gitignored build product; it pins whatever commit built it | 2 min (`python3 analysis/c98_release.py`) |
| 5 | **Mint the artefact DOI** | Data Availability: "The deposit has no DOI, because it has not been deposited" — honest, not a stub | 5 min + upload |
| 6 | **Authorship for the §5.9 design originator** | Competing Interests names them as "a researcher … who is not an author" and calls the origination "a substantial intellectual contribution rather than an acknowledgeable courtesy" | **decision, not edit** |

- Items 1–5 are mechanical. **Item 6 is an ethics decision only the authors can make, and it should be settled before submission.**
- **Do not delegate 1, 2, 3 or 6** — end matter, CRediT, funding, correspondence and the author list are the authors' by standing instruction.

## Venue

| venue | fit | accept prob. (est.) | note |
|---|---|---|---|
| **TMLR** | **best** | **0.80** | No novelty bar, no length cap; "claims supported" + "of interest" both strongly met. The pre-registered self-reversal now reaches the abstract, which is what TMLR rewards. Was 0.78 |
| ReScience / MLRC | good | 0.60 | Strong reproduction framing; wants a tighter one-paper scope |
| NeurIPS D&B | fair | 0.30 | Corpus + deposit is a real artefact, but the paper is not framed as one |
| JMLR | fair | 0.25 | Length fine; wants methodological novelty, this is an audit |
| NeurIPS / ICML / ICLR main | poor | 0.15 | 9-page limit is fatal |

**Send to TMLR: YES**, after items 1–4 and a decision on 6. Path: fix 1–4 (~10 min) → settle 6 → rebuild the deposit at the submission commit → arXiv → TMLR. Item 5 (DOI) can follow acceptance — the deposit is commit-pinned and self-verifying.

## Standing

- `plateau5` PRIMARY; CSV `plateau` column BANNED as primary.
- RULE 16 run-unedited · RULE 20 ARGS-line · RULE 21 scorer-before-batch · RULE 22 `dup_group` guard.
- **Ingest is `aggregate.py` THEN `args_repair.py --apply`** — `aggregate.py` alone silently reverts the A3 duplicate-pair repair.
- Re-derive every number at write time. Never quote prose, including this dashboard.
- `release/` is gitignored: it is a build product, regenerated, never committed.

## Open, carried from CORRECTIONS 135

1. The 8 tex↔md numeric residuals (R10) — pre-existing, in sections no package touched.
2. Two `DRAFT-v4.md` prose lines beginning with `|` will render as table rows (`|r| >= 0.632`, `|Delta plateau5|`).
3. §4.8's budget table caption / `se` column (R2).
4. §4.8's **opening** paragraph carries the same over-scoping shape R2 fixed in T9 — weaker (it names `hz3` explicitly and the next sentences introduce the re-run), flagged rather than silently edited.
5. Staging dirs `c99pkg/`, `c99pkg2/` left on ALICE.
6. Whether §9 needs a companion sentence for R3/R5 — **UNSURE**, not attempted; §9 already states the two findings separately.
