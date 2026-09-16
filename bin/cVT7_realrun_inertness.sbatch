#!/bin/bash
#SBATCH --job-name=cvt7inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/home/s5014158/l243_logs/cvt7inert-%j.out
# =============================================================================
# cVT7_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the cvt7 batch (job name `cvt7inert`,
# deliberately NOT the `cvt7-` prefix the batch guards and the scorer read).  CORRECTIONS 243.
#   (1) tests/test_grouphold.py on the cvt7 tree: G0 structure, G1 witness/init, G2 loudness, G3 schedule,
#       G4 meta-update semantics on synthetic z (CPU inside the job, on the live ResNet18_c100 model);
#   (2) tests/test_grouphold_realrun.py: the LIVE ResNet harness (the tree ciso1 / cdep1 / ciso2 ran from; read only)
#       vs cvt7's tree, 300 real CIFAR-100 ResNet18_c100 steps per variant: OFF bitwise on k01 and ISO, the three
#       exact GROUP_HOLD strings (and a test-only tri:100) bite, non-vacuity.
#   sbatch ~/stage_cvt7/bin/cVT7_realrun_inertness.sbatch    -> copy the .out to $WS/runs/cvt7/inertness_grouphold.log
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD GROUP_HOLD
LIVE=$METAOPT_WS/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10
H7=$METAOPT_WS/harness_cvt7/cifar10
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt7
sha256sum tests/test_grouphold.py tests/test_grouphold_realrun.py tests/test_voteweight_realrun.py \
  analysis/cVT7_grouphold_score.py patches/patch_grouphold.py
sha256sum $H7/Optimizers/HF.py $H7/Optimizers/HF.py.pre_grouphold $H7/Optimizers/HF.py.pre_betahold \
  $H7/Optimizers/HF.py.pre_voteweight $LIVE/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_grouphold.py --pre $H7/Optimizers/HF.py.pre_grouphold \
  --post $H7/Optimizers/HF.py --cifar-dir $H7
echo "TEST_GROUPHOLD_RC $?"
cd /home/s5014158/stage_cvt7
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_grouphold_realrun.py --tree-pre $LIVE \
  --tree-post $H7 --steps 300 --every 10 --seed 99 \
  --work /tmp/cvt7_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt7_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
