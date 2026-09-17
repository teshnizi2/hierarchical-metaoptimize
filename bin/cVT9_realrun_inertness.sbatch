#!/bin/bash
#SBATCH --job-name=cvt9inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l249_logs/cvt9inert-%j.out
# =============================================================================
# cVT9_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the cvt9 batch (job name `cvt9inert`, deliberately
# NOT the `cvt9-` prefix the batch guards and the scorer read).  CORRECTIONS 249.
#   (1) tests/test_windowhold.py on the cvt9 tree: W0 structure, W1 witness/init, W2 loudness, W3 schedules,
#       W4 meta-update semantics and dead state on synthetic z (CPU inside the job);
#   (2) tests/test_windowhold_realrun.py: cvt6's tree vs cvt9's tree, 300 real CIFAR-100 PlainNet18_c100 steps per
#       variant: OFF bitwise on k01 / LOWHEADPATH / HIGHHEADPATH / MIDDOSE / RESDOSE, EARLY and LATE bite, two test
#       windows depart.
#   sbatch ~/stage_cvt9/bin/cVT9_realrun_inertness.sbatch   -> copy the .out to $WS/runs/cvt9/inertness_windowhold.log
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt9
sha256sum tests/test_windowhold.py tests/test_windowhold_realrun.py tests/test_voteweight_realrun.py \
  analysis/cVT9_dosewindow_score.py patches/patch_windowhold.py patches/cvt6_headpath.json
sha256sum $METAOPT_WS/harness_cvt9/cifar10/Optimizers/HF.py $METAOPT_WS/harness_cvt9/cifar10/Optimizers/HF.py.pre_windowhold \
  $METAOPT_WS/harness_cvt6/cifar10/Optimizers/HF.py $METAOPT_WS/harness_cvt9/cifar10/Optimizers/cvt6_headpath.json
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_windowhold.py --pre $METAOPT_WS/harness_cvt9/cifar10/Optimizers/HF.py.pre_windowhold \
  --post $METAOPT_WS/harness_cvt9/cifar10/Optimizers/HF.py --cifar-dir $METAOPT_WS/harness_cvt9/cifar10
echo "TEST_WINDOWHOLD_RC $?"
cd /home/s5014158/stage_cvt9
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_windowhold_realrun.py --tree-pre $METAOPT_WS/harness_cvt6/cifar10 \
  --tree-post $METAOPT_WS/harness_cvt9/cifar10 --steps 300 --every 10 --seed 105 \
  --work /tmp/cvt9_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt9_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
