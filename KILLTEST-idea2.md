# KILL-TEST: is the meta-gradient sign-agreement excess just architecture?

**Date:** 2026-08-21 · **Compute cost:** zero (existing probe data only)
**Code:** `analysis/killtest_idea2.py`, `analysis/killtest_hubs.py`
**Data:** `analysis/killtest_data/` (105 MB, rsynced from `alice:/data1/salehkaleybars/metaopt/runs/{mx,gate3}`)

---

## VERDICT

**Idea 2's differentiator (ii) — "our clusters cross ARCHITECTURAL boundaries" — is DEAD on
the evidence that exists.** Once each tensor's own persistent direction is accounted for,
mean cross-block dependence is **−0.04 pp (layerwise arm, p = 0.86 / 0.99 / 0.22)** and
**+0.03 pp (weightwise arm, p = 0.84 / 0.43 / 0.00)** — i.e. zero. All of the raw
across-block excess over 50 % is *marginal bias*: each tensor has its own persistent
meta-gradient direction, which **layerwise step sizes already capture for free**. Clustering
buys nothing over the existing partitions.

**One narrow survivor.** 2–5 % of cross-block tensor pairs do clear a Bonferroni threshold
against a calibrated false-positive rate of 0.07–0.14 pairs. But **78 % of them join
*adjacent* blocks** (4.1–4.2× enriched over `|Δblock| ≥ 2`; median tensor-index gap 12 vs 23
for all cross-block pairs), and the pairs that recur across seeds are `stem↔layer1`,
`layer3.1↔layer4.0`, `layer4↔linear`. That is not structure crossing architecture — it is
the 6-block cut drawn in a slightly wrong place. It argues for *moving the boundaries*, not
for *clustering by a measured statistic*.

**Two caveats bound this verdict, and one of them is serious:**

1. **The decisive sub-tensor test is impossible with stored data.** The probe never writes
   per-coordinate signs. Everything above is at **tensor** granularity. Whether the *weights
   inside* a tensor form clusters that cross tensor boundaries is **untested**. §5 gives the
   minimal probe change and the single run.
2. **The 53.1 % headline does not reproduce from anything now on the cluster.** §1.

---

## 1. (d) Reproduction check — and a problem with the headline

Reducing `mx/probe_sig_*` (3 seeds, 2000 records, 100 epochs, steady window = last 50 %)
reproduces the published ladder **exactly**:

| granularity | m | this run | CONTINUE-HERE.md |
|---|---:|---|---|
| `resnet18_blocks` | 6 | **70.87 ± 0.80 %** | 70.87 ± 0.80 % ✓ |
| `layerwise` | 62 | **53.26 ± 0.19 %** | 53.26 ± 0.19 % ✓ |
| `nodewise` | 14,420 | **51.03 ± 0.12 %** | 51.03 ± 0.12 % ✓ |
| `weightwise` | 11,173,962 | **50.0053 ± 0.0003 %** | 50.0053 ± 0.0003 % ✓ |

The reduction also reproduces CORRECTIONS §12's α₀=1e-3 control to four figures:
`bdrift3/p3-w-L1p0` weightwise, published window (steps 1000–7500) → **50.1918 %** vs the
published **50.19 %**. So the method here is the published method.

**But 53.1 % is not among these numbers, and I could not reproduce it from any probe
directory on the cluster.** I scanned every `probe.jsonl` under `runs/**` (59 run families):

- No **weightwise** run anywhere reaches 53.1 % in the published window. The maximum across
  all surviving weightwise probes is **51.57 %** (`d3/probe_g999_s1`); `mx/probe_sig_weightwise`
  gives 51.32 / 51.47 / 51.25 %. In the steady window they read **50.005 %**. (Excluded: the
  `zsw`/`zm0`/`zb` r=0 arms, which report 97–100 % on `frac_zero ≈ 1` — z is identically zero
  there, so the statistic is undefined, not high.)
- The nine directories that *do* land in 52.8–53.4 % are all `layerwise`, `blockwise` or
  `nodewise` — never `weightwise`.
- CORRECTIONS §12 records the source figure as a 6.20 % excess (→ 53.10 % agreement) at
  α₀=1e-6, paired with the bdrift3 α₀=1e-3 control that *does* still exist.

The most likely explanation is that the α₀=1e-6 run behind the headline was destroyed by one
of the trims recorded in cycles 29/33/34; the repo's own gotcha list documents several such
losses. **Action: the "53.1 % of 11.17M" sentence should not be quoted again until it is
re-measured, and REVIEW-hmkhd2.md §314 / CORRECTIONS §8b / docs/PLAN-appendix-paper.md §13
should be flagged.** The claim is not refuted — it is unsupported by anything on disk.

### 1a. The ladder is mostly an aggregation artifact

The published statistic is the cross-sectional majority fraction `max(p, 1−p)`, which is
**biased up by `0.5·√(2/π)/√n` under independence** — 16.29 pp at m=6, 5.07 pp at m=62,
0.33 pp at m=14,420, 0.012 pp at m=11.17M. Read against each arm's own floor:

| granularity | m | per-record agreement | independence floor | **excess** |
|---|---:|---|---|---|
| `resnet18_blocks` | 6 | 71.80 % | 66.29 % | **+5.51 pp** |
| `layerwise` | 62 | 56.01 % | 55.07 % | **+0.95 pp** |
| `nodewise` | 14,420 | 51.16 % | 50.33 % | **+0.83 pp** |
| `weightwise` | 11.17M | 50.028 % | 50.012 % | **+0.016 pp** |

The m=6-vs-m=62 gap shrinks from 17.6 pp to 4.6 pp once each arm is read against its own
noise floor. (CONTINUE-HERE already warns about this floor; the published table does not
apply it.)

---

## 2. What the probe actually stores — and what it therefore cannot answer

From `HF.py::_probe` (lines 344–403), every record contains:

| field | shape | what it is |
|---|---|---|
| `frac_neg`, `frac_zero` | scalar | **global** sign split over all `n_tot` coordinates |
| `z_mean`, `z_std`, `snr` | **62** | one entry per **param tensor**, on *every* arm |
| `beta` | **62** | per-tensor log-stepsize (instantaneous, not a running mean) |

`z_mean` is a *running* mean over steps and `z_std` is its *temporal* std — **not** a spatial
std within the tensor. On `weightwise`/`nodewise` arms the 62 entries are the **spatial mean**
of that tensor's per-coordinate meta-gradients.

**Consequence for the requested items:**

| requested | status |
|---|---|
| (a) sign-agreement **within** each param tensor | **NOT AVAILABLE.** Per-coordinate signs and per-tensor sign counts are never written. No run on disk can answer this. |
| (b) sign-agreement **across** tensors | **AVAILABLE, exactly** — each tensor contributes one number per record. Answered at tensor granularity. |
| (c) within- vs across-block for the 6-block partition | **AVAILABLE** — same data, `[3,12,15,15,15,2]` labels. |
| (d) the overall figure, reproduced | **DONE** — §1. |
| (4) agreement vs block size | **AVAILABLE** — §4. |

I recovered per-interval per-tensor meta-gradients by undoing the running mean
(`S_k = mean_k · n_k`, `n_k = step_k + 1`, then differencing). Validation:

- float32 differencing noise / signal = **2.4e-5** (layerwise), **9.5e-5** (weightwise);
  noise exceeds signal in 0.01 % of entries. Negligible.
- An **independent, precision-exact** estimator — the sign of the realised meta-update `Δβ`,
  which needs no differencing — gives the same layerwise split (across-block **50.42 %** vs
  **50.46 %** from `z`). *(The `Δβ` replicate is contaminated on the weightwise arm by the
  shared α₀=1e-6 climb and is not used there.)*

---

## 3. (b)/(c) THE KILL TEST

Statistic: **pairwise same-sign rate** `A_ij = P(sign z_i = sign z_j)` over intervals, whose
null is *exactly* 50.000 % with no finite-sample bias — unlike `max(p, 1−p)`, which cannot be
used to compare a within-group of 15 against an across-group of 47.

### Raw, against 50 %

| arm | all cross-tensor pairs | within-6-block | across-6-block | across 95 % CI |
|---|---|---|---|---|
| **layerwise** (m=62) | 50.882 ± 0.124 % | 52.529 ± 0.286 % | **50.461 ± 0.083 %** | [50.30, 50.56] |
| **weightwise** (m=11.17M) | 50.143 ± 0.062 % | 50.690 ± 0.134 % | **50.003 ± 0.081 %** | [49.86, 50.18] |
| **nodewise** (m=14,420) | 51.840 ± 0.228 % | 52.727 ± 0.453 % | 51.614 ± 0.183 % | [51.32, 51.96] |

A label-permutation test (block labels shuffled, block sizes held) says the within-vs-across
gap is real on the layerwise arm — observed 1.91–2.30 pp vs a permutation 95th percentile of
0.61 pp, **p < 0.0005** on all three seeds. On the weightwise arm it is marginal
(p = 0.038 / 0.013 / 0.058).

### Against the null that actually matters

**Two coordinates that each have a persistent direction agree above 50 % even when they are
statistically independent**: if coordinate *i* is negative a fraction `p_i` of the time, then
`A_ij = p_i·p_j + q_i·q_j > 0.5` with no dependence at all. That marginal bias is **already
captured by giving each tensor its own step size** — it is not correlation structure and it
cannot justify clustering.

Circularly shifting each tensor's sign series by an independent random offset destroys
cross-tensor dependence while preserving **exactly** each tensor's marginal bias and its own
autocorrelation. Anything above this null is real dependence.

| arm | within-block obs | null | **Δ** | across-block obs | null | **Δ** | p(across) |
|---|---|---|---|---|---|---|---|
| **layerwise** | 52.53 % | 51.53 % | **+1.00 pp** | 50.46 % | 50.50 % | **−0.04 pp** | 0.86 / 0.99 / 0.22 |
| **weightwise** | 50.69 % | 49.78 % | **+0.91 pp** | 50.00 % | 49.98 % | **+0.03 pp** | 0.84 / 0.43 / 0.00 |

> **Within-block dependence is real (+0.9 to +1.0 pp). Cross-block dependence is ZERO.**
> This is the DEAD branch of the pre-registered test.

Supporting: the agreement-excess matrix is **not** a single global common mode either — its
leading eigenvalue holds only 11–15 % of the spectrum — so the residual is not simply "one
shared direction the scalar partition already gets". It is genuinely heterogeneous. It just
does not cross block boundaries.

### What survives, and why it is still architecture

| arm | cross-block pairs past Bonferroni `\|z\|>4.15` (of 1506) | calibrated false positives |
|---|---|---|
| layerwise | 30 / 35 / 47 | 0.07 ± 0.26 |
| weightwise | 54 / 69 / 72 | 0.12 ± 0.33 |

Real — ~300× the false-positive rate. But **depth-local**:

| \|Δblock\| | pairs available | surviving (layerwise, 3 seeds) | rate | enrichment vs \|Δ\|≥2 |
|---:|---:|---:|---|---|
| **1** | 696 | **83** | 3.98 % | **4.20×** |
| 2 | 480 | 13 | 0.90 % | 0.95× |
| 3 | 255 | 6 | 0.78 % | 0.83× |
| 4 | 69 | 2 | 0.97 % | 1.02× |
| 5 | 6 | 2 | 11.11 % | 11.74× |

**78 %** of survivors join adjacent blocks (available share: 46 %); median tensor-index gap 12–13
vs 23. 54 pairs recur in ≥2 of 6 runs (chance: ~22). The recurring ones:

```
4/6  blk0:bn1.weight              <-> blk1:layer1.0/1.1.bn*.weight   (stem -> layer1)
4/6  blk3:layer3.1.bn2.weight     <-> blk4:layer4.1.conv1.weight     (layer3 -> layer4)
4/6  blk4:layer4.0.bn2.bias       <-> blk5:linear.bias               (layer4 -> head)
4/6  blk4:layer4.0.downsample.1.bias <-> blk5:linear.bias            (shortcut -> head)
```

Every recurring pair is depth-adjacent. The lone long-range cell (`|Δblock| = 5`, stem↔head,
2 of 6 pairs) rests on 6 available pairs and is not something to build on.

Consistent with this, spectral-clustering the agreement matrix into k=6 gives **ARI 0.05–0.24**
against the true block partition — barely above its ARI against *random contiguous* partitions
of the same sizes (0.01–0.17). The measured structure is not a partition that anyone would
discover by clustering.

---

## 4. Agreement vs block SIZE (for the measurement paper)

**Within a single arm, agreement does not rise with `n_b`.** Across the 62 tensors
(`n_b` spans 10 → 2,359,296, five decades):

| | layerwise arm | weightwise arm |
|---|---|---|
| Pearson r(log₁₀ n_b, pairwise-agreement excess) | **−0.07** | **−0.34** |
| OLS slope | −0.07 pp/decade | −0.12 pp/decade |
| Pearson r(log₁₀ n_b, temporal persistence excess) | −0.11 | **+0.34** |

The one thing that *does* rise with block size is **temporal persistence of a tensor's spatial
mean** on the weightwise arm — 54 % in the 10–100 decade to **71 %** in the 10⁶–10⁷ decade.
That is pure averaging: bigger tensors have a more stable mean because they average more
coordinates, not because their coordinates agree more.

**Coarsening the partition inside ONE run** (optimizer held fixed — a group meta-gradient is
the *sum* of its members', `HF.py:149`, so any coarser partition can be synthesised):

| tensors/group | groups | architectural | random, same sizes | **arch − random** |
|---:|---:|---|---|---|
| 1 | 62 | 50.88 % | 50.88 % | 0.00 pp |
| 2 | 31 | 50.88 % | 50.63 % | +0.25 pp |
| 4 | 16 | 50.68 % | 50.31 % | +0.37 pp |
| 8 | 8 | 51.02 % | 50.20 % | +0.82 pp |
| 16 | 4 | 51.67 % | 50.35 % | +1.32 pp |
| **true `[3,12,15,15,15,2]`** | **6** | **51.05 %** | **50.55 %** | **+0.51 pp** |

Two things follow, both of which bear on the paper:

1. **The published m=6 → m=11.17M agreement ladder is a statement about partition coarseness,
   not about coordinates.** Random groupings of the same sizes recover most of the rise.
   The ladder should be presented against both the independence floor (§1a) and a
   same-size random-grouping control, or it overstates its case.
2. **Architecture still carries ~+0.5 pp beyond size alone** at the true 6-block partition —
   small, but real and consistent across seeds. That is the honest form of "architecture
   explains the agreement".

---

## 5. What is missing, and the minimal experiment to get it

Per-coordinate signs are never written, so **within-tensor agreement (item a) is unanswerable
from every run in the campaign**, and everything above is tensor-level. Do not read §3 as a
statement about individual weights.

### Minimal probe change

In `HF.py::_probe`, `zall` (the concatenated per-coordinate meta-gradient) is *already*
materialised for `frac_neg`. Two additions, ~8 lines, no extra compute of consequence:

```python
# (1) EXACT within-tensor sign split -- 2 ints x 62 tensors per record
rec['t_neg']  = [int((zi < 0).sum()) for zi in z]
rec['t_zero'] = [int((zi == 0).sum()) for zi in z]
rec['t_n']    = [int(zi.numel())     for zi in z]

# (2) a FIXED coordinate subsample -> pairwise agreement between INDIVIDUAL weights
#     in different tensors, which is the statistic Idea 2 is actually about
if not hasattr(self, '_probe_idx'):
    g = torch.Generator(device=zall.device).manual_seed(0)
    self._probe_idx = torch.randperm(n_tot, generator=g, device=zall.device)[:20000]
    rec['probe_idx'] = self._probe_idx.cpu().tolist()   # once, on the first record
packed = torch.sign(zall[self._probe_idx]).to(torch.int8).add(1).cpu().numpy()
rec['z_sub'] = base64.b64encode(np.packbits(
    np.stack([(packed >> 1) & 1, packed & 1])).tobytes()).decode()
```

`t_neg`/`t_zero`/`t_n` give **(a) exactly** — the within-tensor split, size-weighted, no
modelling. `z_sub` gives **(b) at true coordinate granularity**: 20,000 tracked weights with a
known tensor and block label, so within-tensor, across-tensor and across-block pairwise
agreement all become directly measurable, and the marginal-preserving null in §3 applies
unchanged. Storage at PROBE=25 over 100 epochs (2000 records): ~10 MB/run packed.

### Single run needed

**One `weightwise` ResNet18 / CIFAR-10 run at the `mx/probe_sig_*` config** — 100 epochs,
α₀=1e-6, `PROBE=25`, free adaptation — so it drops straight into `analysis/killtest_idea2.py`
alongside the three existing seeds. ~1 GPU-hour.

Two riders, in priority order:

1. **Add the α₀=1e-3 twin.** CORRECTIONS §12 shows α₀ moves weightwise agreement by 16×, and
   §1 above shows the α₀=1e-6 headline run no longer exists. One run answers Idea 2 in the
   regime Rule 5 warns about; two answer it and re-establish the headline. **Do both.**
2. Because it costs nothing extra, run the probe on the `layerwise` arm too — `t_neg` there
   is a free replication of §3 at coordinate granularity.

**Decision rule, pre-registered.** Measure within-tensor and across-tensor pairwise agreement
against the circular-shift null. If across-tensor dependence is ≤ 0.1 pp above that null —
as it is at tensor granularity here — **Idea 2 is dead outright** and the sign-agreement
statistic belongs in the measurement paper as a characterisation, not as a method. If it
exceeds ~0.5 pp *and* the surviving pairs are not concentrated at `|Δblock| = 1`, Idea 2 has
a target and the differentiator survives.

---

## 6. One-paragraph summary for the paper

Meta-gradient sign-agreement in ResNet18/CIFAR-10 falls monotonically with partition
fineness (70.9 % at m=6 to 50.005 % at m=11.17M), but most of that fall is the 1/√n
independence floor of the majority statistic plus pure aggregation: random groupings of the
same sizes recover most of the rise, leaving ~+0.5 pp attributable to architecture at the
6-block partition. At tensor granularity, dependence beyond each tensor's own persistent
direction is **+1.0 pp within blocks and 0.0 pp across them**; the ~3 % of cross-block tensor
pairs that do show dependence are 4.2× enriched at adjacent blocks and recur at
stem↔layer1, layer3↔layer4 and layer4↔head. Meta-gradient correlation in this network is
**depth-local and architecture-aligned**; we find no evidence for correlation structure that
crosses architectural boundaries, and therefore no basis for clustering parameters by measured
sign-agreement in preference to the existing layerwise or blockwise partitions.
