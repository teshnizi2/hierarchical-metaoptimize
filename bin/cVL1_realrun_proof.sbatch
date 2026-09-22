#!/bin/bash
#SBATCH --job-name=cvl1proof
#SBATCH --partition=gpu-short,gpu-l4-24g
#SBATCH --constraint=L4
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=00:50:00
#SBATCH --output=/home/s5014158/l302_logs/cvl1proof-%j.out
# =============================================================================
# cVL1_realrun_proof.sbatch -- ONE short GPU job, NOT part of the cvl1 batch (job name `cvl1proof`, deliberately NOT the
# `cvl1-` prefix the batch guards and the scorer read).  CORRECTIONS 302.
#   (1) tests/test_valsplit.py: V0 structure + V1 split + V2 loudness + V3 the REAL CIFAR-10 train set through the patched
#       load_data (CPU inside the job), against the cgw1 tree's pinned pre bytes;
#   (2) tests/test_valsplit_realrun.py: the cgw1 tree vs the cvl1 tree, the REAL train.py for 2 epochs per variant on the
#       GPU: RR0 determinism, RR1 OFF bitwise (unset / empty), RR2 bite (45,000 train, VAL lines, split identical across
#       run seeds 184 / 185), RR3 non-vacuity (split seed 303 differs; a malformed value fails loudly).
#   sbatch ~/stage_cvl1_proof/bin/cVL1_realrun_proof.sbatch      (from the stage copy; it cd's to its own stage)
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
WS=$METAOPT_WS
module load Python/3.10.4-GCCcore-11.3.0
source $WS/envs/mo/bin/activate
unset VAL_SPLIT VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK PROBE_TENSOR SHADOW_VOTE
export PYTHONDONTWRITEBYTECODE=1
STAGE=${CVL1_PROOF_STAGE:-/home/s5014158/stage_cvl1_proof}
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | UTC $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd "$STAGE" || exit 2
sha256sum tests/test_valsplit.py tests/test_valsplit_realrun.py patches/patch_valsplit.py bin/cVL1_stage_harness.sh
sha256sum $WS/harness_cgw1/cifar10/{load_data.py,train.py,Optimizers/HF.py} $WS/harness_cvl1/cifar10/{load_data.py,train.py,load_data.py.pre_valsplit,train.py.pre_valsplit,Optimizers/HF.py}
bash bin/cVL1_stage_harness.sh; echo "STAGE_VERIFY_RC $?"
python3 -u tests/test_valsplit.py --pre-dir $WS/harness_cgw1/cifar10 --cifar-dir $WS/harness_cvl1/cifar10 | tee /tmp/cvl1_v_${SLURM_JOB_ID}.log
echo "TEST_VALSPLIT_RC ${PIPESTATUS[0]}"
VSHA=$(grep -o 'REAL CIFAR-10 val sha (5000:302) [0-9a-f]*' /tmp/cvl1_v_${SLURM_JOB_ID}.log | awk '{print $NF}')
echo "V3_VAL_SHA ${VSHA:-none}"
python3 -u tests/test_valsplit_realrun.py --tree-pre $WS/harness_cgw1/cifar10 --tree-post $WS/harness_cvl1/cifar10 \
  --epochs 2 --work /tmp/cvl1_realrun_${SLURM_JOB_ID} ${VSHA:+--expect-val-sha $VSHA}
RC=$?
rm -rf /tmp/cvl1_realrun_${SLURM_JOB_ID} /tmp/cvl1_v_${SLURM_JOB_ID}.log
echo "REALRUN_RC $RC"
echo "UTC_END $(date -u +%FT%TZ)"
