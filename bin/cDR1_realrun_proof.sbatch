#!/bin/bash
#SBATCH --job-name=cdr1proof
#SBATCH --partition=testing
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=/home/s5014158/l305_logs/cdr1proof-%j.out
# =============================================================================
# cDR1_realrun_proof.sbatch -- ONE short GPU job, NOT part of any batch (job name `cdr1proof`, deliberately NOT a
# `cdr1-` / `c306-` / `c307-` prefix any batch guard or scorer reads).  CORRECTIONS 305.  Partition `testing` (node887,
# L4, 30-min cap, its own QOS): the gpu-short queue is saturated by g3b / crt1 / csh1 / cvl1 and this job must not wait
# behind them or take a slot from them.
#   (1) tests/test_decayroute.py --device cuda: R0 structure, R1 parser, R2 OFF inert (CPU), R3 per-term bitwise on CPU
#       AND on the GPU, R4 finite-difference hypergradient (CPU float64), R5 probe shrink (CPU float64), R6 realised
#       shrink on the GPU on the live ResNet18's shapes -- against the cdr1 tree's own HF.py.pre_decayroute / HF.py;
#   (2) tests/test_decayroute_realrun.py: the cgw1 tree vs the cdr1 tree, the REAL train.py for 2 epochs per variant on
#       the GPU under deterministic kernels: RR0 determinism, RR1 OFF bitwise (unset / empty), RR2 bite (shrink_only,
#       trace_only, alpha_indep:5e-05; realised shrink), RR3 loudness.
#   sbatch ~/stage_cdr1_proof/bin/cDR1_realrun_proof.sbatch      (from the stage copy; it cd's to its own stage)
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
WS=$METAOPT_WS
module load Python/3.10.4-GCCcore-11.3.0
source $WS/envs/mo/bin/activate
unset DECAY_ROUTE VAL_SPLIT VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK PROBE_TENSOR SHADOW_VOTE PROBE PROBE_DIR SCHED
export PYTHONDONTWRITEBYTECODE=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8
STAGE=${CDR1_PROOF_STAGE:-/home/s5014158/stage_cdr1_proof}
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | UTC $(date -u +%FT%TZ)"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd "$STAGE" || exit 2
sha256sum tests/test_decayroute.py tests/test_decayroute_realrun.py patches/patch_decayroute.py bin/cDR1_stage_harness.sh bin/cDR1_realrun_proof.sbatch
sha256sum $WS/harness_cgw1/cifar10/{train.py,Optimizers/HF.py} $WS/harness_cdr1/cifar10/{train.py,Optimizers/HF.py,Optimizers/HF.py.pre_decayroute}
bash bin/cDR1_stage_harness.sh; echo "STAGE_VERIFY_RC $?"
python3 -u tests/test_decayroute.py --pre $WS/harness_cdr1/cifar10/Optimizers/HF.py.pre_decayroute \
  --post $WS/harness_cdr1/cifar10/Optimizers/HF.py --device cuda --cifar-dir $WS/harness_cdr1/cifar10
echo "TEST_DECAYROUTE_RC $?"
python3 -u tests/test_decayroute_realrun.py --tree-pre $WS/harness_cgw1/cifar10 --tree-post $WS/harness_cdr1/cifar10 \
  --epochs 2 --work /tmp/cdr1_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cdr1_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
echo "UTC_END $(date -u +%FT%TZ)"
