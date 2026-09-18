#!/bin/bash
#SBATCH --job-name=cvt10bite
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l258_logs/cvt10bite-%j.out
# =============================================================================
# cVT10_realrun_bite.sbatch -- ONE short GPU job, NOT part of the cvt10 batch (job name `cvt10bite`, deliberately NOT the
# `cvt10-` prefix the batch guards and the scorer read).  CORRECTIONS 258.
#   tests/test_cvt10_hold_realrun.py on cvt8's tree (UNCHANGED): 300 real CIFAR-100 ResNet18_c100 steps per variant --
#   RB0 determinism; RB1 the five registered GROUP_HOLD strings bite (one-tensor groups; group 1 of [59,1,2]) and pass the
#   scorer's own bite_check; RB2 the free specs never run (ONE59, ONE53, [59,1,2]); RB3 non-vacuity (test-only floor
#   strings, one on group 2); RB4 loudness on the live model (CPU).
#   sbatch ~/stage_cvt10/bin/cVT10_realrun_bite.sbatch  -> copy the .out to $WS/runs/cvt10/bite_grouphold.log
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD GROUP_HOLD COMP_HOLD REST_HOLD WINDOW_HOLD
H8=$METAOPT_WS/harness_cvt8/cifar10
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt10
sha256sum tests/test_cvt10_hold_realrun.py tests/test_grouphold_realrun.py analysis/cVT10_onevsthree_score.py
sha256sum $H8/Optimizers/HF.py $H8/build_network.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_cvt10_hold_realrun.py --tree $H8 --steps 300 --every 10 --seed 120 \
  --work /tmp/cvt10_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt10_realrun_${SLURM_JOB_ID}
echo "BITE_RC $RC"
