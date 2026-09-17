#!/bin/bash
#SBATCH --job-name=cvt8inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l248_logs/cvt8inert-%j.out
# =============================================================================
# cVT8_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the cvt8 batch (job name `cvt8inert`, deliberately NOT
# the `cvt8-` prefix the batch guards and the scorer read).  CORRECTIONS 248.
#   (1) tests/test_resthold.py on the cvt8 tree: R0 structure, R1 witness/init, R2 loudness, R3 schedule, R4 meta-update
#       semantics on synthetic z (CPU inside the job, on the live ResNet18_c100 model);
#   (2) tests/test_resthold_realrun.py: cvt7's tree (read only) vs cvt8's tree, 300 real CIFAR-100 ResNet18_c100 steps per
#       variant: OFF bitwise on k01, ISO and GROUP_HOLD floor / tri:8609 / tri:9428; the three REST_HOLD strings (and two
#       test-only strings) bite; open loop.
#   sbatch ~/stage_cvt8/bin/cVT8_realrun_inertness.sbatch  -> copy the .out to $WS/runs/cvt8/inertness_resthold.log
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD GROUP_HOLD COMP_HOLD REST_HOLD
H7=$METAOPT_WS/harness_cvt7/cifar10
H8=$METAOPT_WS/harness_cvt8/cifar10
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt8
sha256sum tests/test_resthold.py tests/test_resthold_realrun.py tests/test_grouphold_realrun.py \
  analysis/cVT8_doseroute_score.py patches/patch_resthold.py patches/cvt8_isopath.json
sha256sum $H8/Optimizers/HF.py $H8/Optimizers/HF.py.pre_resthold $H7/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_resthold.py --pre $H8/Optimizers/HF.py.pre_resthold \
  --post $H8/Optimizers/HF.py --cifar-dir $H8
echo "TEST_RESTHOLD_RC $?"
cd /home/s5014158/stage_cvt8
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_resthold_realrun.py --tree-pre $H7 \
  --tree-post $H8 --steps 300 --every 10 --seed 102 --work /tmp/cvt8_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt8_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
