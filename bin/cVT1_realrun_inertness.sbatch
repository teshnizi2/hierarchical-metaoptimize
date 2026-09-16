#!/bin/bash
#SBATCH --job-name=cvt1inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=00:50:00
#SBATCH --output=/home/s5014158/l227_logs/cvt1inert-%j.out
# =============================================================================
# cVT1_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the cvt1 batch
# (job name `cvt1inert`, deliberately NOT the `cvt1-` prefix the batch guards and
# the scorer read).  Runs tests/test_voteweight_realrun.py: the unpatched cpl1 tree
# vs the PATCH_VOTEWEIGHT cvt1 tree, 300 real CIFAR-100 PlainNet18_c100 steps per
# variant, bitwise beta / loss / probe.jsonl / final weights.  CORRECTIONS 227.
#   sbatch ~/stage_cvt1/bin/cVT1_realrun_inertness.sbatch
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt1
sha256sum tests/test_voteweight_realrun.py
python3 -u tests/test_voteweight_realrun.py --tree-pre $METAOPT_WS/harness_cpl1/cifar10 \
  --tree-post $METAOPT_WS/harness_cvt1/cifar10 --steps 300 --every 10 --seed 78 \
  --work /tmp/cvt1_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt1_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
