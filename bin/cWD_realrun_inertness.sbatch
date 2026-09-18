#!/bin/bash
#SBATCH --job-name=cwdinert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l260_logs/%x-%j.out
# =============================================================================
# cWD_realrun_inertness.sbatch <cwd1|cwd2> -- ONE short GPU job per batch, NOT part of either batch (job names
# `cwdinert1` / `cwdinert2`, deliberately NOT the `cwd1-` / `cwd2-` prefixes the batch guards and scorers read).
# CORRECTIONS 260 / 261.
#   (1) tests/test_decaymask.py on the batch's tree: D0 structure, D1 witness/init, D2 loudness, D3 arithmetic (CPU in the job);
#   (2) tests/test_decaymask_realrun.py: parent tree vs cwd tree over 300 real CIFAR-100 steps per variant: OFF bitwise,
#       the exact masked strings, the update identity at every step, non-vacuity.
#   sbatch -J cwdinert1 ~/stage_cwd/bin/cWD_realrun_inertness.sbatch cwd1   -> copy the .out to $WS/runs/cwd1/inertness_decaymask.log
#   sbatch -J cwdinert2 ~/stage_cwd/bin/cWD_realrun_inertness.sbatch cwd2   -> copy the .out to $WS/runs/cwd2/inertness_decaymask.log
# =============================================================================
set -u
B=${1:?usage: sbatch cWD_realrun_inertness.sbatch cwd1|cwd2}
case "$B" in
  cwd1) PARENT=cvt8; SEED=128 ;;
  cwd2) PARENT=cvt9; SEED=132 ;;
  *) echo "bad batch $B"; exit 2 ;;
esac
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | BATCH=$B"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cwd
H=$METAOPT_WS/harness_$B/cifar10
sha256sum tests/test_decaymask.py tests/test_decaymask_realrun.py tests/test_voteweight_realrun.py tests/test_grouphold_realrun.py \
  analysis/cwd_design.py patches/patch_decaymask.py
sha256sum $H/Optimizers/HF.py $H/Optimizers/HF.py.pre_decaymask $METAOPT_WS/harness_$PARENT/cifar10/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask.py --pre $H/Optimizers/HF.py.pre_decaymask --post $H/Optimizers/HF.py \
  --cifar-dir $H --batch $B
echo "TEST_DECAYMASK_RC $?"
cd /home/s5014158/stage_cwd
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask_realrun.py --batch $B --tree-pre $METAOPT_WS/harness_$PARENT/cifar10 \
  --tree-post $H --steps 300 --every 10 --seed $SEED --work /tmp/${B}_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/${B}_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
