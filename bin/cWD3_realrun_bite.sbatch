#!/bin/bash
#SBATCH --job-name=cwd3bite
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --constraint=L4
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=01:30:00
#SBATCH --output=/home/s5014158/l275_logs/%x-%j.out
# =============================================================================
# cWD3_realrun_bite.sbatch -- ONE short GPU job, NOT part of the batch (job name `cwd3bite`, deliberately NOT the `cwd3-`
# prefix the batch guards and the scorer read).  CORRECTIONS 275.
#   (1) tests/test_decaymask.py --structural-only on cwd1's tree: the three PATCH_DECAYMASK regions delete back to cvt8's
#       HF.py byte for byte (D0) -- the tree is cwd1's, UNCHANGED;
#   (2) tests/test_decaymask_realrun_cwd3.py: cvt8's tree vs cwd1's tree over 300 real CIFAR-100 steps per variant:
#       OFF bitwise, cwd3's four exact masked strings, the update identity at every step, set discrimination at a
#       test-only alpha0, loudness of the name-list grammar.
#   (3) EXPORT PROBE: the carrier string, which contains `+` and `.`, is passed through sbatch's --export list exactly as
#       the launcher passes DECAY_MASK, and echoed back -- proof that such a value rides --export unmangled.
#   mkdir -p ~/l275_logs && sbatch --export=ALL,CWD3_EXPORT_PROBE=layer4.0.bn2.weight+layer4.0.shortcut.1.weight+layer4.1.bn2.weight \
#       ~/stage_cwd3/bin/cWD3_realrun_bite.sbatch
#       -> copy the .out to $WS/runs/cwd3/bite_decaymask_cwd3.log (the launcher's guard 4f reads it there)
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | BATCH=cwd3"
echo "EXPORT_PROBE ${CWD3_EXPORT_PROBE:-unset}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cwd3
H=$METAOPT_WS/harness_cwd1/cifar10
P=$METAOPT_WS/harness_cvt8/cifar10
sha256sum tests/test_decaymask.py tests/test_decaymask_realrun.py tests/test_decaymask_realrun_cwd3.py tests/test_grouphold_realrun.py \
  analysis/cwd_design.py analysis/cwd3_design.py patches/patch_decaymask.py
sha256sum $H/Optimizers/HF.py $H/Optimizers/HF.py.pre_decaymask $P/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask.py --pre $H/Optimizers/HF.py.pre_decaymask --post $H/Optimizers/HF.py \
  --structural-only
echo "TEST_DECAYMASK_D0_RC $?"
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask_realrun_cwd3.py --tree-pre $P --tree-post $H \
  --steps 300 --every 10 --seed 140 --work /tmp/cwd3_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cwd3_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
