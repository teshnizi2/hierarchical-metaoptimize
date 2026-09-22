#!/bin/bash
#SBATCH --job-name=caw2proof
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --constraint=L4
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l290_logs/%x-%j.out
# =============================================================================
# cAW2_realrun_proof.sbatch -- ONE short GPU job, NOT part of the batch (job name `caw2proof`, deliberately NOT the
# `caw2-` prefix the batch guards and the scorer read).  CORRECTIONS 290.
#   tests/test_caw2_realrun.py on cwd1's tree, UNCHANGED, 300 real CIFAR-100 steps per variant, each of the NINE arms'
#   OWN ARGS through train.py's own parse_args, the launcher's own environment (RC1-RC8; see the driver's docstring).
#
#   mkdir -p ~/l290_logs && sbatch ~/stage_caw2/bin/cAW2_realrun_proof.sbatch
#       -> copy the .out to $WS/runs/caw2/proof_caw2.log (the launcher's guard 4f reads it there)
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | BATCH=caw2"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_caw2
H=$METAOPT_WS/harness_cwd1/cifar10
sha256sum tests/test_caw2_realrun.py tests/test_caw1_realrun.py tests/test_grouphold_realrun.py analysis/caw2_design.py analysis/cwd_design.py
sha256sum $H/Optimizers/HF.py $H/build_network.py $H/train.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_caw2_realrun.py --tree $H --steps 300 --every 10 --seed 160 \
  --work /tmp/caw2_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/caw2_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
