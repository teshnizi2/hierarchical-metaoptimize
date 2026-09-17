#!/bin/bash
#SBATCH --job-name=csv1inert
#SBATCH --partition=testing,gpu-2080ti-11g,gpu-short,gpu-l4-24g,gpu-mig-40g,gpu-a100-80g
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/home/s5014158/l262_logs/csv1inert-%j.out
# =============================================================================
# cSV1_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the csv1 batch (job name `csv1inert`, deliberately
# NOT the `csv1-` prefix the batch guards and the scorer read).  CORRECTIONS 262.
#   (1) tests/test_shadowvote.py on the csv1 tree: S0 structure, S1 witness/init, S2 loudness, S3 step semantics (CPU
#       inside the job);
#   (2) tests/test_shadowvote_realrun.py: cvt9's tree vs csv1's tree, 300 real CIFAR-100 PlainNet18_c100 steps per
#       variant: OFF bitwise on k01 / MUTE / HEAD, the two inert on-paths bitwise k01, the LOW strings bite.
#   sbatch ~/stage_csv1/bin/cSV1_realrun_inertness.sbatch   -> copy the .out to $WS/runs/csv1/inertness_shadowvote.log
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD SHADOW_VOTE
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_csv1
sha256sum tests/test_shadowvote.py tests/test_shadowvote_realrun.py tests/test_voteweight_realrun.py \
  analysis/cSV1_shadowvote_score.py patches/patch_shadowvote.py
sha256sum $METAOPT_WS/harness_csv1/cifar10/Optimizers/HF.py $METAOPT_WS/harness_csv1/cifar10/Optimizers/HF.py.pre_shadowvote \
  $METAOPT_WS/harness_cvt9/cifar10/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_shadowvote.py --pre $METAOPT_WS/harness_csv1/cifar10/Optimizers/HF.py.pre_shadowvote \
  --post $METAOPT_WS/harness_csv1/cifar10/Optimizers/HF.py --cifar-dir $METAOPT_WS/harness_csv1/cifar10
echo "TEST_SHADOWVOTE_RC $?"
cd /home/s5014158/stage_csv1
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_shadowvote_realrun.py --tree-pre $METAOPT_WS/harness_cvt9/cifar10 \
  --tree-post $METAOPT_WS/harness_csv1/cifar10 --steps 300 --every 10 --seed 136 \
  --work /tmp/csv1_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/csv1_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
