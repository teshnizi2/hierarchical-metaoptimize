#!/bin/bash
#SBATCH --job-name=cvt2inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=00:50:00
#SBATCH --output=/home/s5014158/l233_logs/cvt2inert-%j.out
# =============================================================================
# cVT2_ladder_inertness.sbatch -- ONE short GPU job, NOT part of the cvt2 batch
# (job name `cvt2inert`, deliberately NOT the `cvt2-` prefix the batch guards and
# the scorer read).  Runs tests/test_voteweight_ladder_realrun.py: the unpatched cpl1
# tree vs cvt1's PATCH_VOTEWEIGHT tree, 300 real CIFAR-100 PlainNet18_c100 steps per
# variant, for EXACTLY cvt2's VOTE_W strings (read from the cvt2 scorer).  CORRECTIONS 233.
#   sbatch ~/stage_cvt2/bin/cVT2_ladder_inertness.sbatch
# Then copy the .out to $METAOPT_WS/runs/cvt2/inertness_ladder_realrun.log (guard 4g0).
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt2
sha256sum tests/test_voteweight_realrun.py tests/test_voteweight_ladder_realrun.py analysis/cVT2_injectladder_score.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_voteweight_ladder_realrun.py --tree-pre $METAOPT_WS/harness_cpl1/cifar10 \
  --tree-post $METAOPT_WS/harness_cvt1/cifar10 --scorer analysis/cVT2_injectladder_score.py --steps 300 --every 10 --seed 87 \
  --work /tmp/cvt2_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt2_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
