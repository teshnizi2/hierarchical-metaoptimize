#!/bin/bash
# =============================================================================
# Cycle 43 -- PREPARED, NOT SUBMITTED (FairShare below the 0.35 floor at cycle 42).
#
# OPEN QUESTION IT ANSWERS
#   FINDINGS 42.4 measured the OFF-EQUILIBRIUM effective-sample-size exponent
#       N_eff ~ m^s ,   s = 0.629 +-0.013  (beta frozen, n=5)
#   against the post-adaptation s = 0.963 +-0.015 (beta free, n=10), and concluded that
#   step-size adaptation consumes the correlated component of the meta-gradient.
#   The frozen-beta half of that contrast exists at **ResNet18 / CIFAR-10 only**.
#   Every other family in the campaign (p7free/p6free/mx) is free-adapting and therefore
#   measures only the post-adaptation exponent.  If s=0.629 is a ResNet18/CIFAR-10
#   artefact the whole of 42.4 collapses to one cell.  This batch is the generalisation.
#
# PRE-REGISTERED PREDICTION (write the verdict against this, not against whatever lands)
#   (a) Every frozen family lands with s well below its own free-beta value:
#       R10 free 0.912 -> frozen predicted <= 0.75;  R34 free 1.012 -> <= 0.80;
#       C100 free 0.911 -> <= 0.75.
#   (b) The frozen exponent does NOT vary much with model size (all within 0.55-0.75),
#       because the common mode is a property of "the step size is uniform and wrong",
#       not of parameter count.
#   REFUTATION: any frozen family at s >= 0.85 means the frozen/free gap is
#   ResNet18-specific and 42.4's mechanism claim must be withdrawn to a single cell.
#
# DESIGN.  Byte-for-byte the `fz-*` recipe (alice2, cycle 41) with only --NN-name and
# --dataset changed:  --alg-meta fixed freezes beta, so the partition cannot affect the
# parameter update and all arms of a family run the identical optimizer.  The
# 20-epoch/PROBE=100 setting gives exactly 100 records (CORRECTIONS 20: tabulate only at
# the full record count).
#
# NOT INCLUDED, deliberately: `resnet18_blocks` on ResNet10/ResNet34 -- it is ResNet18-only
# and dies with ZeroDivisionError at HF.py:175 (six jobs already lost to this).  Those two
# families therefore span lay->w (3 rungs), the same span p7free gives them.
#
# USAGE
#   bash c43_frozen_ladder.sh            # dry run: prints every sbatch line, submits nothing
#   bash c43_frozen_ladder.sh --submit   # submits, but ONLY if the guards below pass
# =============================================================================
set -u

ROOT=/home/s5014158/metaopt                       # alice2
RUNNER=$ROOT/jobs/run_cifar.sh
OUT=$ROOT/runs/fz2
PARTS=gpu-short,gpu-l4-24g,gpu-2080ti-11g,gpu-mig-40g,gpu-a100-80g
SUBMIT=0
[ "${1:-}" = "--submit" ] && SUBMIT=1

# ---- guards (the two hard limits this campaign has already been bitten by) ----
FS=$(sshare -U -n -o FairShare 2>/dev/null | tr -d ' ' | head -1)
PEND=$(squeue -h -u "$USER" -t PENDING | wc -l)
echo "guard: FairShare=$FS  pending=$PEND  (need FairShare >= 0.35 and pending + 30 <= 40)"
if [ "$SUBMIT" = "1" ]; then
  awk -v f="$FS" 'BEGIN{exit !(f>=0.35)}' || { echo "ABORT: FairShare $FS below the 0.35 floor"; exit 1; }
  [ "$PEND" -le 10 ] || { echo "ABORT: $PEND pending, 30 more would exceed the 40 cap"; exit 1; }
fi

mkdir -p "$OUT"
n=0
sub () {   # sub <family> <nn-name> <dataset> <gran-token> <stepsize-groups> <seed>
  local fam=$1 nn=$2 ds=$3 gtok=$4 groups=$5 s=$6
  local name="fz2-${fam}-${gtok}-s${s}"
  n=$((n+1))
  local cmd=(sbatch --job-name="$name" --partition="$PARTS"
    --export=ALL,AUGMENT=1,BETA_CLIP=-15:-2.3026,PROBE=100,PROBE_DIR=$OUT/$name
    "$RUNNER"
    --optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1
    --alg-meta fixed
    --dataset "$ds" --NN-name "$nn" --batch-size 100
    --max-time 999:00:00 --gamma 1 --meta-stepsize 1e-3 --alpha0 1e-3
    --num-epochs 20 --stepsize-groups "$groups" --seed "$s"
    --save-directory "$OUT" --run-name "$name")
  if [ "$SUBMIT" = "1" ]; then "${cmd[@]}"; else printf '%s\n' "${cmd[*]}"; fi
}

for s in 0 1 2; do
  # ResNet10 / CIFAR-10   (free-beta comparator: s = 0.912 +-0.028, n=2)
  sub r10  ResNet10      CIFAR10  lay  layerwise  "$s"
  sub r10  ResNet10      CIFAR10  node nodewise   "$s"
  sub r10  ResNet10      CIFAR10  w    weightwise "$s"
  # ResNet34 / CIFAR-10   (free-beta comparator: s = 1.012 +-0.006, n=2)
  sub r34  ResNet34      CIFAR10  lay  layerwise  "$s"
  sub r34  ResNet34      CIFAR10  node nodewise   "$s"
  sub r34  ResNet34      CIFAR10  w    weightwise "$s"
  # ResNet18 / CIFAR-100  (free-beta comparator: s = 0.911 +-0.021, n=10)
  sub c100 ResNet18_c100 CIFAR100 blk6 resnet18_blocks "$s"
  sub c100 ResNet18_c100 CIFAR100 lay  layerwise  "$s"
  sub c100 ResNet18_c100 CIFAR100 node nodewise   "$s"
  sub c100 ResNet18_c100 CIFAR100 w    weightwise "$s"
done
echo "---- $n jobs ($( [ "$SUBMIT" = 1 ] && echo SUBMITTED || echo 'dry run, nothing submitted' )) ----"
echo "reduce with:  python3 analysis/neff_ladder.py fz2   (after rsync of runs/fz2 probe dirs)"
