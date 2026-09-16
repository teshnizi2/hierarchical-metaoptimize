#!/bin/bash
#SBATCH --job-name=cvt4inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=01:00:00
#SBATCH --output=/home/s5014158/l237_logs/cvt4inert-%j.out
# =============================================================================
# cVT4_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the cvt4 batch (job name `cvt4inert`,
# deliberately NOT the `cvt4-` prefix the batch guards and the scorer read).  CORRECTIONS 237.
#   (1) tests/test_betahold.py on the cvt4 tree: B0 structure, B1 witness/init, B2 loudness, B3 schedule,
#       B4 meta-update semantics on synthetic z (CPU inside the job);
#   (2) tests/test_betahold_realrun.py: cvt1's tree (unpatched by PATCH_BETAHOLD) vs cvt4's tree, 300 real
#       CIFAR-100 PlainNet18_c100 steps per variant: OFF bitwise, the four exact BETA_HOLD strings bite,
#       HOLDSHARED vs MUTE.
#   sbatch ~/stage_cvt4/bin/cVT4_realrun_inertness.sbatch    -> copy the .out to $WS/runs/cvt4/inertness_betahold.log
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt4
sha256sum tests/test_betahold.py tests/test_betahold_realrun.py tests/test_voteweight_realrun.py \
  analysis/cVT4_betahold_score.py patches/patch_betahold.py
sha256sum $METAOPT_WS/harness_cvt4/cifar10/Optimizers/HF.py $METAOPT_WS/harness_cvt4/cifar10/Optimizers/HF.py.pre_betahold \
  $METAOPT_WS/harness_cvt1/cifar10/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_betahold.py --pre $METAOPT_WS/harness_cvt4/cifar10/Optimizers/HF.py.pre_betahold \
  --post $METAOPT_WS/harness_cvt4/cifar10/Optimizers/HF.py --cifar-dir $METAOPT_WS/harness_cvt4/cifar10
echo "TEST_BETAHOLD_RC $?"
cd /home/s5014158/stage_cvt4
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_betahold_realrun.py --tree-pre $METAOPT_WS/harness_cvt1/cifar10 \
  --tree-post $METAOPT_WS/harness_cvt4/cifar10 --steps 300 --every 10 --seed 90 \
  --work /tmp/cvt4_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt4_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
