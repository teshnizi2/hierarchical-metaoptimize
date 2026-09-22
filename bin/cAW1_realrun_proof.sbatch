#!/bin/bash
#SBATCH --job-name=caw1proof
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --constraint=L4
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l290_logs/%x-%j.out
# =============================================================================
# cAW1_realrun_proof.sbatch -- ONE short GPU job, NOT part of the batch (job name `caw1proof`, deliberately NOT the
# `caw1-` prefix the batch guards and the scorer read).  CORRECTIONS 290.
#   tests/test_caw1_realrun.py on cwd1's tree, UNCHANGED, 300 real CIFAR-100 steps per variant, each arm's OWN ARGS
#   through train.py's own parse_args, the launcher's own environment:
#     RA1 the AdamW base BITWISE at wd 0.1 and 1e-2, both grains; non-vacuous against the other decay and against the
#         SGDm base (the HARNESS-NULL: a base that silently fell back);  RA2 the Adam meta BITWISE, non-vacuous against
#         Lion;  RA3 the K01 control (SGDm + Lion) BITWISE;  RA4 the grain (1 vs 62 step sizes);  RA5 the witnesses;
#     RA6 the DOM_C vote decomposition on real Adam-meta and Lion-meta records;  RA7 determinism;  RA8 the five arms
#     pairwise distinct;  RA9 the decay route at alpha0 1e-6, counted, and at a TEST-ONLY alpha0 1e-2.
#
#   mkdir -p ~/l290_logs && sbatch ~/stage_caw1/bin/cAW1_realrun_proof.sbatch
#       -> copy the .out to $WS/runs/caw1/proof_caw1.log (the launcher's guard 4f reads it there)
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | BATCH=caw1"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_caw1
H=$METAOPT_WS/harness_cwd1/cifar10
sha256sum tests/test_caw1_realrun.py tests/test_grouphold_realrun.py analysis/caw1_design.py analysis/cwd_design.py
sha256sum $H/Optimizers/HF.py $H/build_network.py $H/train.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_caw1_realrun.py --tree $H --steps 300 --every 10 --seed 149 \
  --work /tmp/caw1_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/caw1_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
