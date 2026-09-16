#!/bin/bash
#SBATCH --job-name=cvt6inert
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=6
#SBATCH --mem=16G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l242_logs/cvt6inert-%j.out
# =============================================================================
# cVT6_realrun_inertness.sbatch -- ONE short GPU job, NOT part of the cvt6 batch (job name `cvt6inert`,
# deliberately NOT the `cvt6-` prefix the batch guards and the scorer read).  CORRECTIONS 242.
#   (1) tests/test_comphold.py on the cvt6 tree: C0 structure, C1 witness/init, C2 loudness, C3 schedules,
#       C4 meta-update semantics and dead state on synthetic z (CPU inside the job);
#   (2) tests/test_comphold_realrun.py: cvt4's tree (unpatched by PATCH_COMPHOLD) vs cvt6's tree, 300 real
#       CIFAR-100 PlainNet18_c100 steps per variant: OFF bitwise on k01 / HEAD / HOLDLOW / HOLDHIGH, the three exact
#       COMP_HOLD strings bite, two test-only strings depart.
#   sbatch ~/stage_cvt6/bin/cVT6_realrun_inertness.sbatch    -> copy the .out to $WS/runs/cvt6/inertness_comphold.log
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cvt6
sha256sum tests/test_comphold.py tests/test_comphold_realrun.py tests/test_voteweight_realrun.py \
  analysis/cVT6_complementpath_score.py patches/patch_comphold.py patches/cvt6_headpath.json patches/cvt6_testdown.json
sha256sum $METAOPT_WS/harness_cvt6/cifar10/Optimizers/HF.py $METAOPT_WS/harness_cvt6/cifar10/Optimizers/HF.py.pre_comphold \
  $METAOPT_WS/harness_cvt4/cifar10/Optimizers/HF.py $METAOPT_WS/harness_cvt6/cifar10/Optimizers/cvt6_headpath.json
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_comphold.py --pre $METAOPT_WS/harness_cvt6/cifar10/Optimizers/HF.py.pre_comphold \
  --post $METAOPT_WS/harness_cvt6/cifar10/Optimizers/HF.py --cifar-dir $METAOPT_WS/harness_cvt6/cifar10
echo "TEST_COMPHOLD_RC $?"
cd /home/s5014158/stage_cvt6
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_comphold_realrun.py --tree-pre $METAOPT_WS/harness_cvt4/cifar10 \
  --tree-post $METAOPT_WS/harness_cvt6/cifar10 --steps 300 --every 10 --seed 96 \
  --work /tmp/cvt6_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cvt6_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
