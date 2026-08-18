# Hierarchical MetaOptimize — experiment code

MSc project (LIACS, Leiden). Extends **MetaOptimize** (Sharifnassab, Salehkaleybar,
Sutton, ICML 2025) to hierarchical / partially-pooled step-size granularity.

## Layout
| path | contents |
|---|---|
| `patches/` | patches applied to the upstream MetaOptimize CIFAR-10 code |
| `tests/`   | correctness tests for the granularity implementations |
| `analysis/`| probe analysis (H1 SNR regression, beta traces) + run aggregation |
| `jobs/`    | Slurm job scripts |
| `results/` | aggregated run tables (CSV) |

## Upstream and patches
Upstream: <https://github.com/sabersalehk/MetaOptimize> (training code ships zipped
in `codes/Supervised_tasks.zip`). Three defects were found and patched:

1. **No data augmentation** (`patches/patch_augment.py`) — ResNet-18 reached ~0 train
   loss in epoch 1, leaving no optimization headroom. Enabled via `AUGMENT=1`.
2. **`layerwise` / `nodewise` / `weightwise` were never implemented**
   (`patches/patch_hf2.py`) — `HF.py` recognised the names but had no branch, raising
   `AttributeError`. The upstream `MetaStep` variant has branches but they are dead
   code that cannot execute (`.cuda()` on a list; `torch.log(float)`).
3. **Silent truncation** — `train.py` has its own `--max-time` break inside the epoch
   loop. Always pass `--max-time 999:00:00` and bound runs with Slurm's `--time`.

`patches/patch_probe.py` adds an inert probe (`PROBE`, `PROBE_DIR`) recording per-group
beta and meta-gradient SNR. Probe on/off both reproduce unpatched runs digit-for-digit.

## Correctness
`tests/test_granularity.py` validates the new granularities against the **upstream
blockwise path**, which the patch does not touch:

* `layerwise` == `blockwise[1,1,...,1]` (62 singleton groups)
* `scalar` == `blockwise[62]`
* every granularity is identical at `meta_stepsize=0` (step sizes frozen)
* `weightwise` == `nodewise` on an all-1-D network
* `block_product` equals explicit per-group inner products

All pass to float32 tolerance (max |diff| 7.5e-9).

## Reproducing a run
```bash
module load Python/3.10.4-GCCcore-11.3.0
source /data1/salehkaleybars/metaopt/envs/mo/bin/activate
sbatch --export=ALL,AUGMENT=1,PROBE=100,PROBE_DIR=<dir> jobs/run_cifar.sh \
  --optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1 \
  --alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 \
  --meta-stepsize 1e-3 --alpha0 1e-6 --gamma 1 --NN-name ResNet18 --dataset CIFAR10 \
  --num-epochs 100 --batch-size 100 --max-time 999:00:00 --stepsize-groups <G> --seed <S> \
  --save-directory <dir> --run-name <name>
```
`<G>` ∈ `scalar` | `resnet18_blocks` | `layerwise` | `nodewise` | `weightwise`.

## Aggregating results
```bash
python analysis/aggregate.py /data1/salehkaleybars/metaopt/runs > results/all_runs.csv
```

## Environment
torch 2.0.1+cu118, torchvision 0.15.2, numpy<2 (torch 2.0.1 is incompatible with
numpy 2.x), tensorboard. ALICE compute nodes have no internet — datasets must be
staged from a login node.

## Acknowledgement (required by the facility)
> This work was performed using the compute resources from the Academic Leiden
> Interdisciplinary Cluster Environment (ALICE) provided by Leiden University.
