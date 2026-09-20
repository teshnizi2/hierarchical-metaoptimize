#!/bin/bash
#SBATCH --job-name=cwd5bite
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --constraint=L4
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=/home/s5014158/l281_logs/%x-%j.out
# =============================================================================
# cWD5_realrun_bite.sbatch -- ONE short GPU job, NOT part of the batch (job name `cwd5bite`, deliberately NOT the
# `cwd5-` prefix the batch guards and the scorer read).  CORRECTIONS 281.
#   (1) tests/test_decaymask.py --structural-only on cwd1's tree: the three PATCH_DECAYMASK regions delete back to
#       cvt8's HF.py byte for byte (D0).  The tree is cwd1's, UNCHANGED (cwd3 and cwd4 ran on the same bytes).
#   (2) tests/test_decaymask_realrun_cwd5.py on cvt8's tree vs cwd1's tree, 300 real CIFAR-100 steps per variant:
#       RW-EQ  the NEW wd-parameterised child == the REGISTERED child of tests/test_decaymask_realrun.py, BITWISE,
#              at wd 0.1 (the only value the registered one can run) -- the additive code is proved, not trusted;
#       RW0/1  determinism, and inertness of cwd1's tree at the anchor;
#       RW2    THE LADDER'S PREMISE: at EACH of the four rung tokens (0.1 / 1e-2 / 1e-3 / 5e-4) the update is BITWISE
#              the coupled formula with THE PASSED weight decay, the same run FAILS the formula at another rung's wd
#              (non-vacuity), and the four rungs' final weights are PAIRWISE DISTINCT -- the flag bites;
#       RW3    PATCH_DECAYMASK at a weight decay it has NEVER run at: the three ctd1 carriers at wd 1e-2, the witness
#              `wd=0.01 ... masked=3 ... idx=50,53,59`, the record contract, the masked update identity and
#              non-vacuity against the unmasked run at the same wd;
#       RW4    LOUDNESS at the new value, including the patch's own `a mask would be vacuous` error at wd 0.
#   (3) EXPORT PROBE: the three-name carrier string, which contains `+` and `.`, is passed through sbatch's --export
#       list exactly as the launcher passes DECAY_MASK, and echoed back unchanged.
#
#   mkdir -p ~/l281_logs && sbatch --export=ALL,CWD5_EXPORT_PROBE=layer4.0.bn2.weight+layer4.0.shortcut.1.weight+layer4.1.bn2.weight \
#       ~/stage_cwd5/bin/cWD5_realrun_bite.sbatch
#       -> copy the .out to $WS/runs/cwd5/bite_decaymask_cwd5.log (the launcher's guard 4f reads it there)
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | BATCH=cwd5"
echo "EXPORT_PROBE ${CWD5_EXPORT_PROBE:-unset}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cwd5
H=$METAOPT_WS/harness_cwd1/cifar10
P=$METAOPT_WS/harness_cvt8/cifar10
sha256sum tests/test_decaymask.py tests/test_decaymask_realrun.py tests/test_decaymask_realrun_cwd5.py tests/test_grouphold_realrun.py \
  analysis/cwd_design.py analysis/cwd5_design.py patches/patch_decaymask.py
sha256sum $H/Optimizers/HF.py $H/Optimizers/HF.py.pre_decaymask $P/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask.py --pre $H/Optimizers/HF.py.pre_decaymask --post $H/Optimizers/HF.py \
  --structural-only
echo "TEST_DECAYMASK_D0_RC $?"
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask_realrun_cwd5.py --tree-pre $P --tree-post $H \
  --steps 300 --every 10 --seed 146 --work /tmp/cwd5_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cwd5_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
