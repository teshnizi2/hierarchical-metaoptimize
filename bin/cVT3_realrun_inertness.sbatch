#!/bin/bash
#SBATCH --job-name=cvt3inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=00:50:00
#SBATCH --output=/home/s5014158/l232_logs/cvt3inert-%j.out
# =============================================================================
# cVT3_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the cvt3 batch
# (job name `cvt3inert`, deliberately NOT the `cvt3-` prefix the batch guards and
# the scorer read).  Runs tests/test_voteweight_realrun_cvt3.py: the unpatched cpl1
# tree vs cvt1's PATCH_VOTEWEIGHT tree (unchanged), 300 real CIFAR-100 PlainNet18_c100
# steps per variant, OFF / IDENTITY bitwise and the three exact cvt3 VOTE_W strings'
# bite.  CORRECTIONS 232.
#   sbatch ~/stage_cvt3/bin/cVT3_realrun_inertness.sbatch
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt3
sha256sum tests/test_voteweight_realrun_cvt3.py tests/test_voteweight_realrun.py analysis/cVT3_downcoalition_score.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_voteweight_realrun_cvt3.py --tree-pre $METAOPT_WS/harness_cpl1/cifar10 \
  --tree-post $METAOPT_WS/harness_cvt1/cifar10 --steps 300 --every 10 --seed 84 \
  --work /tmp/cvt3_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt3_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
