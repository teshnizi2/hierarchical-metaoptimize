# STATUS — operator dashboard

Updated 3 Sep 2026 (**cycle 116**). Detail lives here; chat stays short.
Authority: `docs/CORRECTIONS.md` (highest number wins, now **139**) > `docs/FINDINGS.md` > everything else.
HEAD = the cycle-116 commit (parent **`58c0c85`**), working tree clean.
Draft = `paper/paper.tex` + `paper/DRAFT-v4.md` (**76 pp** — 75 until this cycle; see Plan C below). Corpus = **2,177 rows**.
**No Slurm job submitted. Both queues empty** — `squeue -u salehkaleybars` and `-u s5014158` both return a header only.
**Every row below was re-derived at this HEAD. Do not quote this file as a source; re-run the command.**

## Verdict

| | |
|---|---|
| Q1 meta-gate | **DESK-ACCEPT, 9/10, `structural_gaps = []`, `passed = True`, 0 blocking.** Returned at cycle 111 on v8 (CORRECTIONS 135). **Carried, not re-derivable here** — the gate tool is not in this tree |
| Audit | `c98_reproduce.py` **exit 0, ALL 636 CHECKS PASS**; census at fixpoint **628 / 411 / 982 / 41.9%** |
| tex↔md | `paper_numeric_diff.py` **5 residuals over 4 distinct tokens, all pre-existing, 0 new.** Three of the eight were closed this cycle |
| Science overturned | **none.** Contribution 1 intact at 4 sites; the withdrawal stays confined to the slope |
| GPU to reach submission | **0 jobs, 0 hours** |

**Ready to submit: NO** — not for any manuscript defect, for the six author items.

## Mechanical verification — commands run at this HEAD

| check | result |
|---|---|
| `python3 analysis/c98_reproduce.py` | exit 0, **ALL 636 CHECKS PASS** |
| census fixpoint (measured on `DRAFT-v4.md`, asserted against both markups) | **628 / 411 / 982 / 41.9%** — **unmoved by Plan C, as designed** |
| census internals | raw `\d+\.\d+` 3067 → **3098**, distinct **1007** (unchanged); quantities 2614 → **2615**, distinct **982** (unchanged). The `+1` is the Markdown heading numeral `1.2`; `1.2` already occurred twice as a quantity, so the asserted denominator did not move. `n_q` is asserted by nothing |
| `python3 analysis/xref_check.py` | exit 0, **596 references** (section 500, table 51, figure 22, appendix 23), **0 unresolved, 0 stale**, 8 allowlisted parent-paper refs on lines `[41, 43, 45, 287, 291, 294, 295, 297]` |
| `python3 analysis/test_fence_mask.py` | **ALL PASS** |
| `python3 analysis/paper_numeric_diff.py` | **exit 1 — and exit 1 IS the green state.** 2,606 tex numerals (994 distinct) vs 2,607 md (994 distinct); **2 tex-only** (`0.05`, `3.0`), **3 md-only** (`0.087`, `0.279`, `3.19`) |
| `tectonic -X compile paper.tex`, clean copy of `paper/` | exit 0, **76 pp**, **0** TeX errors, **0** undefined, **0** `??` in the extracted PDF text, **75 labels / 75 distinct refs, 0 orphan, 0 dangling, 0 duplicate**, **2** `Overfull \hbox` (7.28497 pt, 12.25499 pt — the same two as before Plan C, no third) |
| `python3 analysis/dup_group_guard.py` | **21 groups, 42 rows stamped, 3 superseded — PASS** |
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
- The whole cycle-116 diff is **195 insertions, 8 deletions**, and every one of the 8 removed lines is a
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
| state | **rebuilt from a clean checkout at the cycle-116 commit** — see CORRECTIONS 139 for the verification transcript |
| census in `release/README.md` | must read **41.9%** and match the paper. It shipped **45.9%** once (CORRECTIONS 138): the README interpolates `%(census)s` at build time, so a stale deposit prints a stale figure with no other symptom |
| `release/` | **gitignored** — a build product of `analysis/c98_release.py`, regenerated, never committed |

**A deposit is only as current as its last build.** It must be rebuilt once more at whatever commit is
actually submitted, and the README's coverage figure checked against the paper's. That is author item 4,
and it has already bitten once.

## TODO-FOR-AUTHOR — 6 open, all outside agent scope, each verified open at this HEAD

| # | item | evidence it is still open | effort |
|---|---|---|---|
| 1 | **CRediT ↔ Funding contradiction** — "Funding acquisition" on S. Salehkaleybar against a Funding statement reading *"no dedicated project funding and no grant"* | both strings present in **both** markups: `paper.tex:5136–5137` ("Funding\nacquisition", wrapped) + `:5115` / `DRAFT-v4.md:4139` + `:4119` | 1 min |
| 2 | **LIACS correspondence address** to replace the gmail of record | **4 sites, 2 per markup**: `paper.tex:56` (`\thanks`) and `:5169` (under `\paragraph{Correspondence.}` at `:5168`) / `DRAFT-v4.md:5` and `:4168`. The LIACS *affiliation* is already in the CRediT block; this is the address only | 2 min |
| 3 | **ORCIDs, both authors** | `grep -ci orcid` = **0** in `paper.tex`, **0** in `DRAFT-v4.md` | 5 min |
| 4 | **Deposit rebuild at the submission commit** | the on-disk deposit is only ever as current as its last build; the README's coverage figure must be checked against the paper's every time | 2 min (`python3 analysis/c98_release.py`) |
| 5 | **Mint the artefact DOI** | *"The deposit has no DOI, because it has not been deposited"* — `paper.tex:5048` / `DRAFT-v4.md:4054` — honest, not a stub | 5 min + upload |
| 6 | **Authorship for the §5.9 design originator** | Competing Interests names them as *"a researcher … who is not an author"* and calls the origination *"a substantial intellectual contribution rather than an acknowledgeable courtesy"* — `paper.tex:5106`, `:5109` / `DRAFT-v4.md:4110`, `:4113` | **decision, not edit** |

- Items 1–5 are mechanical. **Item 6 is an ethics decision only the authors can make, and it must be
  settled before submission** — the paper's own Competing Interests says so.
- **Do not delegate 1, 2, 3 or 6.** End matter, CRediT, funding, correspondence and the author list are
  the authors' by standing instruction.
- **The list is exactly six.** Nothing was added this cycle; nothing was closed.

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

**CLOSED this cycle (139), with evidence — do not re-open:** Plan C signposting (applied; census
fixpoint held; `xref_check` green on 596 refs), R10's `39,172` (one space) and R10's `9.0` pair (a
real table-content difference, no claim divergence), and the §7 threat index, which said `T9–T12`
while `T13` exists inside *Limits of the review process*.

**CLOSED in earlier cycles — do not re-open:** the two `|`-leading md prose lines (138), §4.8's `se`
column (137), §4.8's opening over-scoping (138), the ALICE staging dirs (138 — re-verified by
read-only `ssh` at this HEAD, both gone), the §9 companion-sentence question (138 — decided **NO**),
R4 (137), R8 (138).
