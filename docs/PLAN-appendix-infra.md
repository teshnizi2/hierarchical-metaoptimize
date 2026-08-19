# Infrastructure, Reproducibility & Tooling — Hierarchical MetaOptimize

**Status of this document:** every claim tagged **[measured]** was verified live on ALICE and on the local machine on 2026-08-18 during the writing of this spec. Claims tagged **[inferred]** or **[unverified]** are exactly that.

---

## 0. Triage summary

| # | Item | Severity | Effort | Why now |
|---|---|---|---|---|
| **P0-1** | Entire modified codebase is **untracked git content on 1-month scratch** | **Critical** | 2 h | One `scratch` purge deletes every line of the layerwise/nodewise/weightwise implementation and all probe code |
| **P0-2** | 51 completed runs exist **only as stdout `.out` files** | **Critical** | 4 h | Gate 0/Gate 1 numbers are currently unreproducible and un-reauditable; no config, no curve, no env |
| **P0-3** | `/data1/salehkaleybars` is mode `700` → the student's own account **cannot read the working dir** | High | 10 min | Blocks the entire two-account throughput plan (§6) |
| **P1-1** | Off-cluster master (GitLab + Leiden Data Store) required by the filed DMP, not set up | High | 1 day | Compliance + it *is* the backup |
| **P1-2** | Run-provenance schema + run harness before the next 250 runs | High | 2–3 days | Retrofitting provenance onto 250 runs is impossible; doing it now is cheap |
| **P1-3** | ImageNet copy: 489/1000 train classes **confirmed incomplete** | High | 1 day to verify + 1–3 days to refill | Blocks the only scale axis that can rescue the original premise |
| **P2-1** | Scheduling: currently using **~1 of ~42** available concurrent GPU slots per account | Medium | 1 day | 40×–80× throughput available for free |
| **P2-2** | PaperFactory integration decision | Medium | 2–4 days (recommended path) | Cheap if scoped to the back half; a multi-week sink if scoped wrong |
| **P2-3** | DMP unsigned by PI | Medium | 1 email | Formality, but it gates the Data Store collection |

---

## 1. Stop the bleeding — what must be set up NOW

### 1.1 The single worst finding

**[measured]** In `/data1/salehkaleybars/metaopt/MetaOptimize`:

```
$ git status --porcelain
?? codes/Supervised_tasks/
```

HEAD is `61a57f8 "Update README.md"`, remote `https://github.com/sabersalehk/MetaOptimize`. The directory also contains a `__MACOSX/` folder — this tree was **unzipped from an archive, not cloned**, and then a clone was overlaid.

The practical meaning: **every line the student has written — the layerwise / nodewise / weightwise implementations, the augmentation patch, the `--max-time` fix, `probe.py`, `probe_gran.py`, `beta_trace.py`, `h1_analysis.py`, the patched `HF.py` — is untracked, uncommitted, unpushed, on a filesystem with ~1 month retention and no backup.** Total footprint of `/data1/salehkaleybars/metaopt` is **4.8 GB** [measured] — small enough that there is no excuse.

Losing this is not "a setback". The three code defects took real diagnostic work to find, and the granularity implementations are the project's only genuine software contribution so far.

### 1.2 Do this today (≤ 2 hours, in this order)

**Step A — durable copy on ALICE, right now, before anything else.** The student's own home is essentially empty and is *not* scratch:

```
/zfsstore/user/s5014158  →  2.0 T total, 3.8 G used (1%)     [measured]
```

That is persistent ZFS-over-NFS, not the 1-month `/data1`. Use it:

```bash
ssh alice 'tar czf /tmp/metaopt-snapshot-$(date +%F).tgz \
    -C /data1/salehkaleybars metaopt \
    --exclude=".git" --exclude="__MACOSX" --exclude="envs"'
# then pull it to the student's own home and to the Mac
scp alice:/tmp/metaopt-snapshot-*.tgz .
scp metaopt-snapshot-*.tgz alice2:~/snapshots/
```

This is a stopgap, not the plan. It takes five minutes and removes the single-point-of-failure today.

**Step B — make the code a real repository.** Not the upstream fork; a *new* repo that you own.

```bash
# on the Mac
git init hierarchical-metaoptimize
# vendor the authors' code as a subtree or submodule pinned at 61a57f8,
# then commit YOUR changes as a visible diff against it
```

The critical design choice: **the student's modifications must be visible as a diff against a pinned upstream commit.** This is what makes the "layerwise was never implemented" claim auditable by a reviewer or by Saber. If the code lands as one blob commit, the claim becomes an assertion. Structure:

```
repo/
  upstream/            # git submodule @ 61a57f8 (or vendored + UPSTREAM_SHA file)
  patches/             # the exact diffs applied, one file per defect
    0001-add-cifar10-augmentation.patch
    0002-remove-inner-max-time-break.patch
    0003-implement-layerwise-nodewise-weightwise.patch
  src/                 # probe.py, beta_trace.py, h1_analysis.py, run harness
  configs/
  jobs/
  analysis/
  DEFECTS.md           # the three defects, with the byte-identical-inertness evidence
```

`DEFECTS.md` is not optional documentation — it is the evidentiary record for a claim you may have to defend in review and in correspondence with the parent authors.

**Step C — push off-cluster.** Two remotes, both required:

1. **LIACS GitLab** (`gitlab.liacs.leidenuniv.nl`, the student already has `ssh liacs` working as `s5014158` [measured]). This is the DMP-mandated off-cluster master.
2. **A private GitHub mirror** as a second independent copy. Different provider, different failure domain. Push both from one `git push --all` by adding two URLs to one remote.

Do **not** make the repo public yet — the parent authors have not been told about the dead-code finding, and publishing a repo whose commit history documents it is a communication decision, not an infrastructure one.

**Step D — Leiden Data Store collection.** This is the PI's action (he owns the collection). Send one email asking for: (a) the DMP signature, (b) creation of the LDS collection, (c) the student added as a depositor. Until it exists, GitLab + GitHub is your compliance story and you should say so in writing.

### 1.3 What goes where (storage tiering)

| Tier | Path | Retention | What lives there |
|---|---|---|---|
| Hot scratch | `/data1/salehkaleybars/metaopt` | **~1 month, no backup** [given] | Working dir, active job I/O, checkpoints in flight, dataset copies |
| Warm durable | `/zfsstore/user/s5014158` (2 TB, 1% used) [measured] | Persistent | Nightly rsync of `runs/` metrics + configs; the one aggregated results DB; final checkpoints worth keeping |
| Cold / off-cluster | LIACS GitLab + GitHub | Permanent | All code, all configs, all analysis scripts, the aggregated results table (it will be small — see §5) |
| Archive / DOI | Leiden Data Store → Zenodo at submission | Permanent | The §2 deposit bundle |

**Automate the warm tier immediately.** A cron on the login node, or better, a Slurm `cpu-short` job chained after each batch:

```bash
rsync -a --include='*/' --include='*.json' --include='*.jsonl' \
      --include='*.parquet' --include='*.csv' --include='*.log' --exclude='*' \
      /data1/salehkaleybars/metaopt/runs/ \
      /home/s5014158/mirror/runs/
```

Metrics and configs only — not checkpoints. At the volumes involved (§5) the entire metric corpus for 250 runs is on the order of a few GB, and the aggregated table is a few MB.

### 1.4 The permissions blocker

**[measured]**

```
drwx------. 8 salehkaleybars liacs   /data1/salehkaleybars
$ ssh alice2 'ls /data1/salehkaleybars/metaopt'
ls: cannot access '/data1/salehkaleybars/metaopt': Permission denied
```

Both accounts are `gid=1494(liacs)`. The student's own account has **no `/data1/s5014158` scratch at all** [measured]. So today, `s5014158` cannot see the code, the runs, or the ImageNet copy — which means the two-account parallelism in §6 is currently impossible.

**Recommended fix — an ACL, not a chmod.** `chmod 750` would expose the PI's scratch to the entire `liacs` group (the whole institute). A targeted ACL does not:

```bash
# run as salehkaleybars — but ASK SABER FIRST, this is his directory
setfacl -m u:s5014158:rx  /data1/salehkaleybars
setfacl -R -m u:s5014158:rwX /data1/salehkaleybars/metaopt
setfacl -R -d -m u:s5014158:rwX /data1/salehkaleybars/metaopt   # inherit for new files
setfacl -R -m u:s5014158:rX  /data1/salehkaleybars/imagenet_data
```

This is a permission change on someone else's account directory. **It requires Saber's explicit go-ahead** — do not run it unilaterally, even though the student has the credentials. Also ask ALICE helpdesk in the same round whether **`/projects`** (which exists on the cluster [measured]) can host a group-owned project directory with longer retention; that is the correct long-term home for a two-person project and removes the ACL hack entirely. Whether `/projects` is available to LIACS MSc projects is **[unverified]**.

---

## 2. Provenance — what every run must record

### 2.1 The current state

**[measured]** `runs/` contains 51 files, all of the form `<jobname>-<jobid>.out` — Slurm stdout, nothing else. No TensorBoard events anywhere in the tree, no per-run config, no metrics file, no checkpoints. The job script:

```bash
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --time=01:45:00
#SBATCH --output=/data1/.../runs/%x-%j.out
module load Python/3.10.4-GCCcore-11.3.0
source /data1/salehkaleybars/metaopt/envs/mo/bin/activate
python train.py "$@"
```

Everything about a run — which granularity, which seed, which meta-LR — is recoverable **only** by parsing the `ARGS:` echo line out of stdout, and only if that specific `.out` file survives the scratch purge. The `envs/mo` venv is never captured. There is no record of which GPU model the run landed on, and since `--gres=gpu:1` is unconstrained on `gpu-short`, runs land on A100 / L4 / MIG-slice / 2080ti interchangeably [measured: `gpu-short` spans all four].

This is not defensible a year from now. It is barely defensible next month.

### 2.2 Required per-run record

One directory per run. Nothing is ever written outside it. Schema:

```
runs/<experiment>/<config_hash>/seed<K>/
  config.resolved.json     # every parameter after defaults+CLI merge, incl. defaults
  config.hash              # sha256 of config.resolved.json, canonical-JSON serialized
  provenance.json          # §2.3
  env.lock.txt             # pip freeze --all  (from inside the job, not the login node)
  env.modules.txt          # `module list` output
  metrics.jsonl            # one JSON object per logged step/epoch
  blocks.parquet           # per-block time series (β, z_b stats, ‖w_b‖, n_b)
  events.jsonl             # LR anneals, NaNs, collapse detections, early stops
  stdout.log               # symlink or copy of the Slurm .out
  slurm.json               # job id, partition, node, GPU model, sacct accounting
  ckpt/                    # optional; see §2.5
  DONE                     # sentinel written ONLY on clean completion
```

The `DONE` sentinel matters more than it looks. Defect #2 (the silent `--max-time` truncation that produced 81- and 85-epoch "100-epoch" runs) is exactly the class of failure a completion sentinel makes impossible to overlook. **A run without `DONE` is excluded from every aggregation, by construction, not by remembering.**

### 2.3 `provenance.json` — the mandatory fields

```json
{
  "run_id": "g1-layerwise-sgdm-s0",
  "config_hash": "sha256:9f3a…",
  "code": {
    "repo_sha": "abc1234",
    "dirty": false,
    "diff_sha256": "…",          // sha of `git diff HEAD` if dirty; run REJECTED if dirty in a production sweep
    "upstream_sha": "61a57f8"
  },
  "slurm": {
    "job_id": 4653443, "array_task_id": null,
    "partition": "gpu-2080ti-11g", "node": "node8xx",
    "gres": "gpu:2080_ti:1",
    "submit_time": "…", "start_time": "…", "end_time": "…",
    "elapsed_s": 6120, "max_rss_gb": 11.2
  },
  "hardware": {
    "gpu_name": "NVIDIA GeForce RTX 2080 Ti", "gpu_count": 1,
    "driver": "550.54.15", "cuda_runtime": "12.4",
    "cpu_model": "…", "cpus_per_task": 8
  },
  "software": {
    "python": "3.10.4", "torch": "2.x.y+cu124", "torchvision": "…",
    "cudnn": "…", "numpy": "…",
    "env_lock_sha256": "…"
  },
  "determinism": {
    "seed": 0,
    "torch_deterministic": false,
    "cudnn_benchmark": true,
    "dataloader_workers": 8, "worker_seeding": "generator+worker_init_fn"
  },
  "data": {
    "dataset": "cifar10",
    "root": "/data1/…/data",
    "manifest_sha256": "…",       // sha of the sorted file list + sizes
    "n_train": 50000, "n_test": 10000,
    "augmentation": ["RandomCrop(32,padding=4)", "RandomHorizontalFlip"],
    "normalization": [[0.4914,…],[0.2470,…]]
  },
  "status": "completed",           // completed | failed | truncated | oom | timeout
  "completion_reason": "epochs_exhausted",
  "epochs_requested": 100, "epochs_completed": 100
}
```

Three fields are load-bearing and worth arguing for individually:

- **`code.dirty` / `diff_sha256`.** Given that the granularity implementations are currently *untracked*, "which version of the layerwise code produced 91.34?" is right now unanswerable. Make the harness **refuse to launch** a sweep-tagged run from a dirty tree.
- **`hardware.gpu_name`.** Because `gpu-short` mixes four GPU generations, wall-clock is meaningless across runs and numerics differ (TF32 on A100 vs 2080ti). If any claim ever rests on timing, or on a marginal accuracy difference, you need this.
- **`epochs_completed` vs `epochs_requested`.** Defect #2, encoded so it cannot recur silently.

### 2.4 What to log during the run

`PILOT.md` already specifies the right instrumentation list (per-block β, per-block meta-grad running mean/std/SNR, block sizes `n_b`, per-block ‖w_b‖, trace norm, train+test loss/top-1, wall-time/step, peak VRAM). Keep it. Two additions and one correction:

**Add:** a `collapse` detector that fires an `events.jsonl` entry when test accuracy drops below chance-plus-epsilon for N consecutive evaluations, or when the median per-block α falls below `alpha0/100`. The weightwise SGDm collapse (peak 70.09 → 10.00) was found by reading a curve; it should be found by the harness.

**Add:** the meta-optimizer's own internal state summary (Lion momentum norms per block). H3-runaway and the observed *freeze* (Lion's `sign(0)=0` locking β) are both diagnosable only from this.

**Correction — do not report "best test accuracy".** All results in the brief are "best test accuracy over 100 epochs". That is a maximum over ~100 noisy evaluations of the test set, i.e. selection on the test set, and its bias grows with evaluation frequency and with the variance of the run. It is what the parent paper does, so keep it for comparability — but **log the full per-epoch curve so that final-epoch accuracy, last-10-epoch mean, and a proper validation-selected number can all be recomputed a year later without re-running anything.** A reviewer asking "is this best-of-100 or final?" is a question you want to answer from a file, not from a re-run. This one decision is the highest-value line in this section.

### 2.5 Checkpoints

`PILOT.md` rule: checkpoint **β, H, Y, and the meta-optimizer state** alongside weights. Correct and non-negotiable — a MetaOptimize checkpoint without the trace and meta-state cannot be resumed and cannot be diagnosed.

Policy, given 250+ runs:

- Every run writes a **rolling** checkpoint (last-2) for preemption resume; deleted on `DONE`.
- Only runs flagged `keep_final: true` in the config retain a final checkpoint. Budget: one seed per *headline* configuration, ~15–25 checkpoints total.
- Every **anomalous** run (collapse, NaN, divergence) retains its last checkpoint automatically, regardless of flag. The weightwise collapse is a finding; its checkpoint is evidence.
- Never mirror checkpoints to `/zfsstore` wholesale. ResNet-18 + β + H + Y + Lion state is roughly 150–250 MB per checkpoint [inferred from 11.17 M params × several optimizer states]; 250 of those is ~50 GB, which fits in the 2 TB home but bloats the Zenodo deposit for no reviewer benefit.

### 2.6 Zenodo deposit (prepare the shape now, publish at submission)

Deposit bundle:

1. **Code**, as a git archive of a tagged release (`v1.0-icml-submission`), including the `patches/` directory and `DEFECTS.md`.
2. **All `config.resolved.json` files** — 250 small JSON files, a few hundred KB total.
3. **The aggregated results table** (§5) as a single Parquet + CSV. This is the artifact reviewers and re-users actually want.
4. **All `provenance.json` files**, concatenated to one JSONL.
5. **Per-run metrics**, gzipped. Estimate: 250 runs × ~100 epochs × ~62 blocks × ~6 quantities ≈ 10⁷ numbers ≈ 1–3 GB compressed as Parquet [inferred]. Under Zenodo's 50 GB per-record limit; fine.
6. **Figure-regeneration scripts** and a `Makefile` such that `make figures` reproduces every plot from items 3+5 with no cluster access.
7. **`MANIFEST.sha256`** over everything, and an `ENVIRONMENT.md` naming exact GPU models, driver, CUDA, and the pinned `env.lock.txt`.
8. **Explicitly not deposited:** the ImageNet copy (license), and bulk checkpoints (link to LDS instead, or deposit the ~20 kept ones separately).

Reserve the Zenodo DOI at submission time and cite it in the paper. Link the GitHub repo to Zenodo so a tag auto-archives.

---

## 3. ImageNet — verification and remediation

### 3.1 What I measured today

At `/data1/salehkaleybars/imagenet_data/ILSVRC/Data/CLS-LOC/` **[all measured 2026-08-18]**:

| Split | Entries found | Canonical ILSVRC-2012 | Verdict |
|---|---|---|---|
| `train/` | **489 class dirs** | 1000 | **Incomplete — 511 classes missing** |
| `val/` | 50,000 files | 50,000 | Count matches |
| `test/` | 100,000 files | 100,000 | Count matches |

Two further diagnostics that change the interpretation:

- **The 489 WNIDs span the full alphanumeric range** — first is `n01440764` (the canonical first class, tench), last is `n15075141` (the canonical last class, toilet tissue). So this is **not** a truncated prefix from an interrupted sequential extraction; it is a **scattered/interleaved subset**. That pattern is consistent with (a) a parallel `rsync`/`tar` that dropped roughly half its work units, (b) a copy from a source that was itself partial, or (c) a deliberate 50%-of-classes subsample. It is *not* consistent with "the tar was still extracting when someone hit Ctrl-C".
- **Ten sampled classes (5 first, 5 last) each contain exactly 1300 images.** So the classes that *are* present appear individually complete. 1300 is the ILSVRC per-class cap, and while many real classes do have exactly 1300, the true distribution runs 732–1300 with total 1,281,167. Getting 10/10 at exactly the cap is weakly suggestive of a capped/synthetic copy and needs the full count to settle.

Also note: **`val/` is 50,000 flat JPEGs, not class subdirectories.** That is the standard Kaggle/ILSVRC distribution layout and it is **not** loadable by `torchvision.ImageFolder`. Whoever runs ImageNet will need the devkit ground-truth file (`ILSVRC2012_validation_ground_truth.txt`) plus the WNID ordering to restructure it. If the authors' `train_imagenet.py` (present at `/data1/salehkaleybars/MetaStep/MetaStep/`) assumes an already-restructured val, that is a second, separate blocker. **[unverified — check before scheduling any ImageNet run.]**

A second ImageNet path exists at `/data1/salehkaleybars/MetaStep/MetaStep/imagenet` [measured] and has not been inspected. Check it before re-downloading anything.

`du -sh` on the ImageNet tree **timed out at 120 s** — the metadata operations on this filesystem are slow, so run all verification as a batch job, not interactively.

### 3.2 Verification procedure (run as a `cpu-short` job, ~1 h)

```bash
#!/bin/bash
#SBATCH --partition=cpu-short --time=02:00:00 --cpus-per-task=8 --mem=8G
cd /data1/salehkaleybars/imagenet_data/ILSVRC/Data/CLS-LOC

# 1. exact per-class counts
for d in train/*/; do printf "%s %d\n" "$(basename $d)" "$(ls -U $d | wc -l)"; done \
  > /home/s5014158/imagenet_audit/train_counts.txt

# 2. diff against the canonical 1000-WNID list (ship it in the repo)
comm -13 <(sort canonical_wnids.txt) <(cut -d' ' -f1 train_counts.txt | sort) > extra.txt
comm -23 <(sort canonical_wnids.txt) <(cut -d' ' -f1 train_counts.txt | sort) > missing.txt

# 3. total image count — must equal 1,281,167 for a complete copy
awk '{s+=$2} END {print "total:", s}' train_counts.txt

# 4. integrity, not just presence: decode-test a random 2000 images
python -c "…PIL.Image.open(p).verify() over a random sample…"

# 5. devkit present?
ls -la ../../Annotations ../../../devkit* 2>/dev/null
find /data1/salehkaleybars -maxdepth 4 -iname '*devkit*' -o -iname '*validation_ground_truth*'
```

Decision rule on the output:

- `total == 1,281,167` **and** `missing.txt` empty → complete; the 489 count was a listing artifact (it was not — but verify anyway).
- `missing.txt` has 511 entries and present-class counts match the canonical histogram → **partial copy, classes individually intact.** Refill only the missing 511.
- Present-class counts are all exactly 1300 → **capped/derived copy.** Treat the whole tree as untrusted and re-acquire, because a per-class cap silently changes the class-frequency distribution and therefore the optimization problem.

### 3.3 What to do about it

**Priority order:**

1. **Ask before downloading.** Two questions, one email, zero compute: (a) does ALICE provide a **shared, curated ImageNet**? The cluster has `/cm/shared`, `/scratchdata` and `/projects` mounts [measured] and many university clusters host ILSVRC centrally — helpdesk will know in one reply. (b) Ask Saber whether this copy was deliberately subsampled for a prior project. A 489-class scattered subset looks more like a decision than an accident.
2. **In parallel, do the zero-GPU move from `PILOT.md` §"The zero-GPU move": ask Saber and Arsalan for the ImageNet run logs and per-block β trajectories from the ICML runs.** This is still the single highest-value action in the entire project and it has apparently not been done. It answers "is the ImageNet effect large and clean or marginal and noisy" without a single GPU-hour, and it directly tests the unconfirmed claim that the ImageNet blockwise run used the same 6-block partition as CIFAR-10 — on which the entire Gate 1 design rests.
3. **Only then re-acquire.** ~150 GB over a university link; use the login node with `--bwlimit`, verify against the official MD5 manifest per tar, extract into a *new* directory (never merge into the suspect one), and record a `manifest.sha256` so §2's `data.manifest_sha256` field is meaningful. Budget 1–3 days wall-clock, mostly unattended.
4. **Meanwhile, do not block on ImageNet.** Given §Implications — the "layerwise hurts" premise does not reproduce at CIFAR-10 and the failure appears only at *weightwise* — the scale axis may not even be the right axis any more. **Tiny-ImageNet or ImageNet-100 (a documented, reproducible 100-class subset) is a defensible intermediate** that costs ~1/10 the compute and is publishable as a scale point. If ImageNet-1k turns out to require a 3-day download plus a val restructure plus per-granularity meta-LR tuning, the honest cost-benefit may favour spending that budget on the meta-LR confound instead.

**Honest uncertainty:** I do not know whether the missing 511 classes matter for the scientific question. If the phenomenon is about *granularity × parameter count* rather than about *task difficulty*, a 489-class ImageNet is arguably a perfectly good, if non-standard, large-scale task — it just can't be compared to published ImageNet numbers. That is a research call for Saber, not an infrastructure call, but the infrastructure answer should be given to him with that framing.

---

## 4. PaperFactory — concrete recommendation

### 4.1 What PaperFactory actually is here

**[measured]** at `/Users/teshnizi/PaperFactory-r3`:

- `STAGE_ORDER` = 21 stages: `improve, trend_scan, idea_generation, novelty_gate, track_selection, experiment_design, experiment_run, systematic_review, figures, writing, review_loop, hard_questions, red_team, q1_meta_gate, part_gate_written, part_gate_figures, finalize, part_gate_crosscutting, final_judge, polish, reflect`.
- `paperfactory/compute/` is a genuinely pluggable backend layer: `ComputeBackend` ABC with `dispatch / poll / fetch / cancel / checkpoint / resume / queue_state`, a `registry.select_backend()` keyed on `required_compute`, and three implementations (`LocalMacBackend` 503 LOC, `RogGpuBackend` **1387 LOC**, `CloudGpuBackend` 52 LOC stub).
- The active config's `north_star` contains a **HARD REQUIREMENT** that the primary experiment "MUST train, fine-tune, or adapt a small open-weights model on the ROG RTX 2060 (6 GB VRAM)" and evaluate "on a PUBLIC multiple-choice reasoning benchmark (ARC-Easy, HellaSwag, BoolQ)".

That last point is decisive and is easy to miss: **PaperFactory is not a neutral pipeline that happens to point at a 2060. Its configured research programme is small-LLM fine-tuning, with the hardware constraint baked into the topic selection itself.** The front half exists to *discover* an idea inside that envelope. Here the idea is fixed, half-measured, and in a different field.

### 4.2 The three options, priced

| Option | Effort | Value | Verdict |
|---|---|---|---|
| **A. Back half only** — hand PaperFactory a fixed idea + real ALICE results, run `figures → writing → review_loop → hard_questions → red_team → part_gates → final_judge → polish` | **2–4 days**, mostly integration debugging | High. This is where PF's adversarial machinery (`hard_questions`, `red_team`, `final_judge`) is worth the most, and this project *needs* adversarial review — the premise already failed once | **Recommended** |
| **B. Wire a Slurm/ALICE backend** | **1.5–3 weeks**. A `SlurmBackend` faithful to `RogGpuBackend` is ~600–900 LOC plus tests: `sbatch` submission, `squeue`/`sacct` polling, array-job handles, ProxyJump SSH through `alice-gw`, preemption-aware `resume`, artifact staging off scratch | Low **now**. It duplicates the run-management layer you must build anyway (§5), and it inserts an autonomous agent between you and a shared university cluster where a runaway submission loop is a social problem, not just a technical one | **Reject for now** |
| **C. Front half against a fixed idea** | 1 day to configure, then unbounded | **Negative.** `trend_scan`/`idea_generation`/`novelty_gate`/`track_selection` will either be no-ops or will actively propose alternatives to the fixed idea; `experiment_design` will design for a 2060 | **Reject** |

### 4.3 Recommendation

**Use PaperFactory as a back-half writing and adversarial-review engine only. Do not wire an ALICE backend. Do not run the front half.**

Concretely:

1. **Fork the config** to a new `paperfactory.metaoptimize.yaml`. Rewrite `north_star` to state the fixed research question and — critically — **delete the 2060 hard requirement and the LLM-benchmark constraints**, replacing them with "experiments are run externally on ALICE; results are supplied as a fixed artifact." Leave the rigor bar (≥3 seeds, ablation, CIs, honest baselines, no fabricated numbers) untouched: it is the part worth having.
2. **Set `experiment.allow_rog_dispatch: false`** so `select_backend` cannot route anything to the 2060, and confirm no stage silently falls back to `LocalMacBackend` and *runs something*. Verify this by inspection before the first invocation — a pipeline that quietly runs a stub experiment and then writes a paper about it is the failure mode to design against.
3. **Feed `experiment_run` a pre-computed results artifact** rather than letting it dispatch. The clean seam is the aggregated results table from §5: a single Parquet plus the `provenance.jsonl`. `Provenance` in `compute/types.py` already carries `hostname / command / seeds / wallclock_s / returncode / python_version / torch_version / backend_id` — your ALICE provenance schema (§2.3) is a strict superset, so the mapping is mechanical.
4. **Entry point risk — the one thing I could not verify.** I did not confirm that PaperFactory can be *entered mid-pipeline* with a hand-authored idea and externally-supplied results. It has `rewind_to(stage, STAGE_ORDER)` and a resumable `state.db`, which strongly suggests it can, but "rewind to an earlier stage" is not the same as "start at a later stage with fabricated upstream state." **[unverified]** Budget half a day to establish this before committing to Option A; if it turns out PF requires the front half to have run, the effort estimate rises to 5–8 days and Option A becomes marginal — at which point use PF's `hard_questions` / `red_team` / `final_judge` prompts standalone, which captures most of the value for one day of work.
5. **Never let PaperFactory write the results section unsupervised.** The paper's central claims are now *negative and contested* (the proposal's premise does not reproduce; the parent code may contain never-executed branches). Those are exactly the claims where an autonomous writer's default rhetorical register — confident, positive, contribution-framed — is most dangerous. Human-authored claims; PF for structure, figures, critique, and polish.

**Revisit Option B only if** the project ends up running 500+ jobs across many sweeps *and* the §5 harness is already stable. At that point a `SlurmBackend` is a thin adapter over infrastructure that already exists, and the estimate drops to ~4 days. Building it first inverts that.

---

## 5. Experiment management for 250+ runs

### 5.1 Principles

1. **A run is immutable and self-describing.** Everything needed to interpret it lives in its own directory (§2.2). No global state, no notebook variable, no memory.
2. **Identity is a hash of the resolved config, not a filename.** Filenames drift, get renamed, and encode only what someone thought was important at the time.
3. **Aggregation is a pure function of run directories.** Rebuildable from scratch at any time, idempotent, and it must *not* silently skip malformed runs — it must report them.
4. **Figures are a pure function of the aggregated table.** Never of raw runs, never of hand-copied numbers.

### 5.2 Config and naming

**Configs are files, not command lines.** The current `sbatch … run_cifar.sh --optimizer HF --stepsize-groups resnet18_blocks …` pattern means a run's identity exists only in a shell history and an echoed stdout line. Replace with:

```
configs/
  base/cifar10_resnet18.yaml            # everything shared
  gate1/{scalar,block6,layerwise,weightwise}.yaml   # overrides only
  gate3/hier_lambda_{1e-3,1e-2,1e-1}.yaml
```

The harness merges base + override + `--seed`, writes `config.resolved.json`, hashes it, and refuses to launch if that hash already has a `DONE` run (unless `--force`). That single rule prevents the most common 250-run failure: silently re-running a config under a slightly different name and getting two different answers.

**Two names per run, serving different consumers:**

- **Directory / canonical ID:** `<experiment>/<config_hash[:8]>/seed<K>` — stable, collision-free, order-independent.
- **Slurm `--job-name`:** `g1-lw-sgdm-s0` — short, greppable in `squeue`, *not* authoritative. Record the mapping in `slurm.json`.

Do **not** encode the full config in the directory name. `g1_sgdm_lw62_a1e-6_eta1e-3_g1_s0_ep100_aug1` is unreadable, and the moment you add a hyperparameter every path in every script breaks.

### 5.3 Submission: array jobs, not loops

For a sweep of C configs × S seeds, submit one array job per config family:

```bash
sbatch --array=0-$((C*S-1))%20 --job-name=g1 jobs/sweep.sh gate1
```

with the array index resolving to (config, seed) via a manifest file committed to git. Benefits: one job ID per sweep, `sacct -j <id>` gives the whole sweep's accounting in one query, `%N` throttling respects the QOS caps, and a failed subset is resubmittable by index list.

### 5.4 Tracking backend

**Recommend: files + a rebuildable DuckDB, not a hosted tracker — for now.**

Rationale: **[unverified but likely]** ALICE compute nodes typically have no outbound internet. A run that blocks on a W&B handshake is a wasted GPU-hour, and `wandb offline` + login-node sync is more moving parts than value at this scale. The file-based scheme is also exactly the Zenodo deposit shape (§2.6), so you build the archive for free.

```
analysis/
  aggregate.py     # walk runs/, validate, load into results.duckdb + results.parquet
  schema.sql
  figures/*.py     # each reads results.parquet ONLY
  Makefile         # `make results` → `make figures` → `make paper`
```

`aggregate.py` must emit a validation report every time:

```
251 run dirs found
  238 DONE and valid
    6 missing DONE  (listed)
    4 epochs_completed != epochs_requested  (listed — the defect-2 class)
    2 config_hash collision with differing resolved config  (FATAL)
    1 code.dirty == true  (excluded)
```

Runs are excluded by rule, and the exclusions are printed. The Gate 1 table in the brief already has "(still running)" and "2 seeds still running" cells; making partial state visible and machine-checked is precisely the point.

If Saber wants a live dashboard, add `wandb` in `offline` mode with a post-run sync from the login node — but keep files as the source of truth and the tracker as a view. **Never let a hosted tracker become the only copy of a number.**

### 5.5 Figure regeneration

One command, from a clean checkout, with no cluster access:

```bash
make figures   # results.parquet → every PDF in paper/figures/
```

Each figure script declares at the top which columns it consumes, so a schema change breaks loudly. Every figure PDF gets a sidecar `.meta.json` recording the `results.parquet` sha256 and the git SHA that produced it — so "is Figure 3 from the current data?" is a `diff`, not an argument. (PaperFactory already does this — there is a `schematic.pdf.meta.json` in its tree [measured]. Copy the idea.)

### 5.6 Analysis hygiene specific to this project

- **Store seeds as rows, never as an aggregate.** The brief reports `91.34 ±0.09` (n=3). With three seeds, a standard deviation is barely an estimate; the raw three numbers must remain in the table so any reviewer can recompute. For headline comparisons (scalar vs layerwise vs weightwise), **plan for 5 seeds**, and record the n in every reported cell.
- **The meta-LR confound needs a first-class schema slot.** The brief correctly flags that `alpha0=1e-6` and `meta_stepsize=1e-3` are the authors' scalar/6-block-tuned values, so weightwise may be losing to a tuning artifact rather than to granularity. That means the results table needs a `tuning_budget` column and every granularity comparison needs a `matched_search_budget` flag. Design this in now — retrofitting "how many configs did we search for this arm?" onto 250 completed runs is not possible.
- **Per-block time series need their own table.** 62 blocks × 100 epochs × 250 runs in a long-format Parquet is ~10⁷ rows — trivial for DuckDB, disastrous for CSV-in-pandas. Partition `blocks.parquet` by `run_id`.

---

## 6. Compute scheduling — the throughput you are leaving on the table

### 6.1 The measured limits

**[all measured 2026-08-18 via `scontrol show partition` and `sacctmgr show qos`]**

| Partition | QOS | MaxTime | **Per-user GPU cap** | Pool |
|---|---|---|---|---|
| `gpu-short` | `qos-short-gpu` | **4:00:00** | **12** (cpu=192) | 108 GPUs (a100 ×16, l4 ×32, MIG ×28, 2080ti ×32) |
| `gpu-2080ti-11g` | `qos-gpu-2080ti` | 7 days | **12** (cpu=144) | 36 |
| `gpu-l4-24g` | `qos-gpu-l4` | 7 days | **8** (cpu=256) | 28 |
| `gpu-mig-40g` | `qos-gpu-mig` | 7 days | **8** (cpu=128) | 28 (3g.40gb ×14, 4g.40gb ×14) |
| `gpu-a100-80g` | `qos-gpu-a100` | 7 days | **2** (cpu=96) | 14 |
| `interactive` | `qos-interactive` | 8:00:00 | 1 | 8 |
| `testing` | `qos-testing` | 0:30:00 | 1 (max 4 submitted) | 4 |

The project brief's "2× A100-80G, 8× L4-24G, 12× RTX2080ti" is accurate for the *long* partitions but misses two things:

1. **`gpu-short` is a separate QOS with its own 12-GPU allowance, spanning all four GPU types.** It is not a subset of the long-partition caps.
2. **Slurm `MaxTRESPerUser` is enforced per-QOS.** Since each partition has a distinct QOS, **the caps stack**. One account can therefore hold roughly **12 + 12 + 8 + 8 + 2 = 42 concurrent GPUs**. Across the two accounts: **~84**. *[This is my reading of Slurm QOS semantics — verify empirically by submitting to two partitions simultaneously and watching `squeue` before planning around it.]*

Today's job script requests `--partition=gpu-short --gres=gpu:1 --time=01:45:00` — one GPU, one partition, unconstrained type.

### 6.2 The recommended plan

**A CIFAR-10 / ResNet-18 / 100-epoch run takes ~1h45 [from the existing `--time` setting]. That fits inside `gpu-short`'s 4-hour limit with a 2× margin.** That single fact is the key: the whole CIFAR sweep programme belongs in the *short* queues, which are the least contended and where backfill scheduling favours you most.

**Lane assignment:**

| Lane | Partition | Job shape | Why |
|---|---|---|---|
| **Bulk CIFAR sweeps** | `gpu-2080ti-11g` (7d, cap 12) and `gpu-mig-40g` (7d, cap 8) | array, `--time=03:00:00`, 1 GPU | 20 concurrent slots on the *least contended* hardware. ResNet-18 on CIFAR fits an 11 GB 2080ti and a 40 GB MIG slice with room to spare. Long partition + short job = you never get killed by the 4h wall |
| **Burst / deadline** | `gpu-short` (cap 12) | array, `--time=03:30:00`, `%12` | +12 slots on top, drawing from the 108-GPU pool including A100s via backfill |
| **L4 lane** | `gpu-l4-24g` (cap 8) | array, 1 GPU | +8. L4 is slower per-step than A100 but there are 28 of them and low demand |
| **A100 reserve** | `gpu-a100-80g` (cap 2) | ImageNet / weightwise-large only | Only 14 in the cluster and a cap of 2. **Do not spend A100s on CIFAR.** The current script does exactly that whenever `gpu-short` happens to schedule it onto one |
| **Debug** | `testing` (30 min, 4 submitted) | smoke tests | Use before every sweep launch; a 30-minute smoke that catches a config error saves 40 wasted GPU-hours |

**Immediate script changes:**

```bash
#SBATCH --constraint=...            # or explicit --gres=gpu:2080_ti:1
#SBATCH --partition=gpu-2080ti-11g
#SBATCH --time=03:00:00             # 1.7x the observed 1h45 — headroom, no truncation
#SBATCH --requeue                   # survive preemption
#SBATCH --open-mode=append          # requeue must not clobber stdout
```

**Pin the GPU type per sweep.** Never let a sweep straddle 2080ti and A100 — TF32 differences and 2–3× wall-clock differences make within-sweep comparisons and any timing claim unsound. Record the type in `provenance.json` (§2.3) and *assert* homogeneity in `aggregate.py`.

### 6.3 Two-account strategy

**Prerequisite: the §1.4 ACL, and Saber's permission for it.** Without it, `s5014158` cannot even read the code.

Once unblocked:

- **Partition the *work*, not the *hardware*.** Give each account whole sweeps (e.g. `salehkaleybars` runs the granularity grid, `s5014158` runs the meta-LR tuning grid). Do not split one sweep across accounts — it doubles the ways provenance can diverge, and `sacct` accounting no longer covers a sweep in one query.
- **Write results into one shared tree** (`/data1/salehkaleybars/metaopt/runs/`) with group-write via the inherited ACL, so `aggregate.py` has one root. Record `slurm.account` in provenance so any account-correlated artifact is detectable after the fact.
- **Etiquette matters more than the caps.** Two accounts saturating 84 GPUs on a shared university cluster is technically permitted and socially conspicuous. Throttle arrays with `%N`, keep `--time` honest (over-requesting hurts *your* backfill priority most), and tell Saber the plan before the first large batch. An unfunded project that annoys the cluster admins loses more throughput than it gains.

### 6.4 Throughput estimate

Sustained: **~20–30 concurrent CIFAR runs per account** is a realistic steady state after queueing, so **40–60 across both**. At ~1.75 h/run that is roughly **25–35 runs/hour of wall-clock**, i.e. **the entire 250-run programme in well under a day of wall-clock**, versus weeks at the current one-job-at-a-time cadence. The estimated ~1400 A100-hour total budget stops being the constraint entirely; **the constraint becomes analysis throughput and experimental design**, which is precisely why §5 must be built before the sweeps and not after.

### 6.5 Unverified items worth five minutes each

- `cpu-short` advertises `gres/gpu=48` including `gpu:l4=28` [measured from partition TRES]. If GRES is actually requestable there, it is a large extra lane under `qos-short` (cpu=324). Test with one job. **[unverified]**
- Whether `MaxTRESPerUser` truly stacks across QOS as described in §6.1. Test by holding jobs in two partitions at once.
- Whether `/projects` is available for a group-owned, longer-retention project directory. One helpdesk email.
- Whether compute nodes have outbound internet (determines the tracking-backend choice in §5.4).

---

## 7. Ordered action list

**Today (2 h):**
1. Snapshot `/data1/salehkaleybars/metaopt` to `/zfsstore/user/s5014158` and to the Mac.
2. `git init` a real repo; commit the untracked `codes/Supervised_tasks/` as an explicit diff against upstream `61a57f8`; write `DEFECTS.md`.
3. Push to LIACS GitLab **and** a private GitHub mirror.

**This week (3–4 days):**
4. Email Saber: DMP signature, LDS collection, the `setfacl` permission request, the ImageNet-subset question, **and the ImageNet-logs request from `PILOT.md`**.
5. Build the run harness: config files, `config.resolved.json` + hash, `provenance.json`, `DONE` sentinel, collapse detector, full-curve logging.
6. Build `aggregate.py` + `results.parquet` + `make figures`. **Backfill what is recoverable from the 51 existing `.out` files and mark the rest as provenance-incomplete rather than pretending otherwise.**
7. Nightly rsync of metrics/configs to `/zfsstore`.

**Next week:**
8. Retarget job scripts to the multi-lane scheduling plan (§6.2); smoke-test on `testing`; launch the first array sweep.
9. Run the ImageNet audit job (§3.2).
10. Half-day spike on whether PaperFactory can be entered mid-pipeline; then commit to Option A or the standalone-prompts fallback.

**Before submission:**
11. Assemble the Zenodo bundle (§2.6), reserve the DOI, tag the release.

---

## 8. Where I am least confident

- **QOS stacking across partitions** (§6.1) is the load-bearing assumption behind the 40–80× throughput claim. It follows from standard Slurm semantics and from the measured fact that each partition has a distinct QOS, but I did not submit jobs to confirm it. If it is wrong, the ceiling is ~12 concurrent per account instead of ~42 — still a 12× improvement on the current cadence, so the plan survives, but the numbers change.
- **PaperFactory mid-pipeline entry** (§4.3 item 4). If it cannot be done, Option A's cost roughly doubles and the standalone-prompts fallback becomes the right call.
- **Whether the 489-class ImageNet is an accident or a decision** (§3.1). The scattered-WNID evidence rules out a simple interrupted extraction and points at something deliberate or at a partial source. Asking is cheaper than any amount of forensics.
- **Compute-node internet access** (§5.4). I assumed no outbound access, which drove the files-first recommendation. That recommendation is robust either way — it is the correct architecture even *with* internet — but if nodes are online, adding a hosted tracker as a *view* becomes cheap.
- **Checkpoint size estimate** (~150–250 MB) is inferred from parameter count plus β/H/Y/Lion state, not measured. It only affects retention policy sizing, not the policy itself.
---

## 3.4 ImageNet audit — RESOLVED 19 Aug 2026 (job 4680826, `audit/in-audit-4680826.out`)

The §3.2 procedure ran as a `cpu-short` job. Read-only on the PI's tree; nothing copied off ALICE.

| measurement | result | canonical | verdict |
|---|---|---|---|
| train class dirs | **489** | 1000 | 511 missing |
| train images | **627,329** | 1,281,167 | 49.0% present |
| per-class counts | min **732**, max **1300**, mean 1282.9 | 732–1300 | **matches the canonical histogram** |
| classes at exactly 1300 | 442 of 489 | ~440 of 1000 | consistent, not capped |
| decode test | **300 sampled, 0 corrupt** | — | intact |
| `val/` | 50,000 flat JPEGs, 0 class subdirs | 50,000 | present, **wrong layout** |
| devkit / `ILSVRC2012_validation_ground_truth.txt` | **not found anywhere under `/data1/salehkaleybars`** | required | **absent** |
| second ImageNet path | **contains no data at all** — it is the authors' *code* (`train_imagenet.py`, `build_network.py`, `cedar_arg_iterator_HF.sh`) | — | dead end |

**Verdict — decision rule branch 2: a genuine partial copy whose present classes are individually intact.**
The earlier worry that it might be a capped/derived copy is **refuted**: the 10-class sample that
showed 10/10 at exactly 1300 was a sampling accident. The full histogram spans 732–1300 with the
canonical shape, and the minimum is exactly the canonical 732. So the 489 classes that are present
are trustworthy; the copy is simply half a dataset.

**Consequences:**
1. **Refilling means re-acquiring 511 classes (~75 GB), not re-acquiring everything.** The existing
   489 need no re-download and no integrity remediation.
2. **`val/` is a harder blocker than `train/`.** The images are all there but the devkit ground-truth
   file is absent, so there is no way to assign labels to the 50,000 val JPEGs from what is on disk.
   Without the devkit, the val split is unusable at any number of classes. It is a small download,
   but it must be on the list.
3. **The "second ImageNet copy" avenue is closed** — that path was never data.
4. The `[RULING on B8]` default of **ImageNet-64×64** is unaffected and remains the right call; this
   audit removes the option of quietly using the on-disk copy as-is, because a 489-class run is not
   comparable to any published number and the val labels are missing regardless.

## 3.5 Found during the audit: the authors' own ImageNet launcher

`/data1/salehkaleybars/MetaStep/MetaStep/imagenet/cedar_arg_iterator_HF.sh` (dated 27 Jan 2024,
i.e. days before the arXiv v1 of 2402.02342). Line 67:

```bash
for stepsize_groups in scalar; do # scalar layerwise nodewise weightwise resnet18_blocks
```

**As configured on disk, the ImageNet sweep iterates `scalar` only.** Every other granularity —
including `resnet18_blocks`, the 6-block partition the paper's CIFAR-10 blockwise results use — sits
in the trailing comment, i.e. disabled.

Two observations, both of which are **questions for Saber, not findings to publish**:

1. If this is the state that produced the paper's ImageNet numbers, then §7.3's "the blockwise
   versions showed no improvement over the scalar versions" was not produced by *this* launcher, and
   the provenance of the ImageNet blockwise arm needs to be established before we explain its null.
   Our unifying result currently *predicts* that null; it would be careless to keep predicting it
   without checking the run existed in the form assumed.
2. The disabled list is `layerwise nodewise weightwise` — **exactly the three paths our `patch_hf2.py`
   had to implement because they are non-executable in the released code.** So had they been
   un-commented, the sweep would have crashed rather than run. That is consistent with them being
   aspirational rather than executed, and it strengthens the reproduction-study contribution.

**Ask before relying on either point.** This is one file, on scratch, in the PI's directory; it is
evidence about his unpublished work, not a result of ours. It sharpens PLAN §4 question (c) from
"was the ImageNet run the same 6-block partition?" to the far more precise **"the launcher on scratch
sweeps scalar only — where did the ImageNet blockwise arm come from?"**

**Not read, deliberately.** `/data1/salehkaleybars/MetaStep/MetaStep/outputs/` holds ~50 run-output
directories from Jan 2024. These are the PI's unpublished results and are exactly the "zero-GPU move"
the plan ranks highest (PLAN §4 item 2 of §3.3) — but reading them needs his explicit permission
(PLAN §4 question (g)), so this audit listed the directory names and stopped there. **Nothing of his
has been copied off ALICE.**
