#!/bin/bash
# Two control blocks that decide what the z3 identity gate actually proved.
#
# BACKGROUND. FINDINGS cycle 10 sec.1 cleared HIER=zpool on FINAL ACCURACY only
# (r=0 vs scalar 0.13pp, r=1 vs plain 0.07pp).  The PROBE=100 beta trajectories
# that z3 also recorded were never read, and they tell a different story:
#
#   pair                    max|d beta| over the run     anchor separation
#   w-r1 == ref-weight              4.1e-03              1.74   <- exact
#   l-r1 == ref-layer               3.3e-02              0.91   <- exact
#   l-r0 == ref-scalar              1.7e-01              0.91   <- 50x looser
#   w-r0 == ref-scalar              1.4e-01              1.74   <- 50x looser
#   w-r0 == l-r0                    1.8e-01                     <- and they differ
#                                                                  from EACH OTHER
#
# The r=1 endpoints are exact.  The r=0 endpoints are only approximate, and the
# two arms that must BOTH equal scalar differ from each other by more than either
# differs from scalar.
#
# _zpool uses tot = sum(z), which IS algebraically the scalar meta-gradient (one
# beta shared by all layers => d/dbeta is the sum of the per-group partials), so
# the operator is not wrong.  The residual has to enter after it.  Two candidate
# mechanisms, and they make opposite predictions:
#
#   H-sign   float32 summation ORDER differs between the three arms (1 term vs 62
#            terms vs 11.17M terms), so `tot` differs in its last bits; Lion's
#            sign() turns a last-bit difference into a FULL +-eta step that is
#            never corrected, and those random-walk apart.  This is the same
#            mechanism as the project's own D1 result.
#            => under Adam meta (non-sign) the r=0 identity should tighten by
#               orders of magnitude, because a tiny difference in `tot` then
#               produces a proportionally tiny difference in the update.
#
#   H-bug    the r=0 path genuinely computes something else.
#            => the gap survives the switch to Adam meta.
#
# dt2 measures the noise floor H-sign implies; z4 tests H-sign directly.
# Both mirror z3 cell-for-cell (alpha0=1e-3, 20 epochs, guard, augment, seed 0,
# 2080ti) so nothing is compared across regimes or GPU types (gotchas 3, 24, 28).
set -e
cd /home/s5014158/metaopt
R=/home/s5014158/metaopt/runs
C="BETA_CLIP=-15:-2.3026"

BL="--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1 --alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --meta-stepsize 1e-3 --alpha0 1e-3 --gamma 1 --NN-name ResNet18 --dataset CIFAR10 --num-epochs 20 --batch-size 100 --max-time 999:00:00"
BA="--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1 --alg-meta Adam --normalizer-param-meta 0.999 --momentum-param-meta 0.9 --weight-decay-meta 0 --meta-stepsize 1e-3 --alpha0 1e-3 --gamma 1 --NN-name ResNet18 --dataset CIFAR10 --num-epochs 20 --batch-size 100 --max-time 999:00:00"

# $1 job name  $2 stepsize-groups  $3 extra env  $4 base args  $5 subdir
sub(){ sbatch --parsable --job-name=$1 --partition=gpu-2080ti-11g --gres=gpu:2080_ti:1 --time=01:00:00 \
  --export="ALL,AUGMENT=1,$C,$3,PROBE=100,PROBE_DIR=$R/$5/$1" jobs/run_cifar.sh $4 \
  --stepsize-groups $2 --seed 0 --save-directory $R/$5 --run-name $1 >/dev/null; }

# ---- dt2: same-seed determinism floor AT A TRAINING REGIME -------------------
# The existing det-* block ran 5 epochs at alpha0=1e-6 and sat at 12.87% against a
# 10% chance baseline -- the same void regime gotcha 25 was written about.  Its
# "+-0.02pp reproducibility floor" therefore bounds nothing while the net is
# actually learning, and it is the number the r=0 gap has to be judged against.
# Identical config, identical seed, replicated; the only difference is the run name.
sub dt2-scal-a  scalar     "HIER="                    "$BL" dt2
sub dt2-scal-b  scalar     "HIER="                    "$BL" dt2
sub dt2-scal-c  scalar     "HIER="                    "$BL" dt2
sub dt2-w-r0-a  weightwise "HIER=zpool,ETA_RATIO=0"   "$BL" dt2
sub dt2-w-r0-b  weightwise "HIER=zpool,ETA_RATIO=0"   "$BL" dt2

# ---- z4: the whole z3 gate again under ADAM meta (non-sign) ------------------
# Self-anchoring: carries its own ref-scalar / ref-layer / ref-weight, so it is
# read only against itself (gotcha 28).
sub z4-ref-scalar  scalar     "HIER="                    "$BA" z4
sub z4-ref-layer   layerwise  "HIER="                    "$BA" z4
sub z4-ref-weight  weightwise "HIER="                    "$BA" z4
sub z4-l-r0        layerwise  "HIER=zpool,ETA_RATIO=0"   "$BA" z4
sub z4-l-r1        layerwise  "HIER=zpool,ETA_RATIO=1"   "$BA" z4
sub z4-w-r0        weightwise "HIER=zpool,ETA_RATIO=0"   "$BA" z4
sub z4-w-r1        weightwise "HIER=zpool,ETA_RATIO=1"   "$BA" z4

sleep 3
# gotcha 27: print the post-state, so the receipt is in the same output as the action
echo "DT2_SUBMITTED=$(squeue -h -u s5014158 -o '%j' | grep -c '^dt2-')"
echo "Z4_SUBMITTED=$(squeue -h -u s5014158 -o '%j' | grep -c '^z4-')"
squeue -h -u s5014158 -o '%i %j %T %r %P' | grep -E '^[0-9]+ (dt2|z4)-' | sort -k2
