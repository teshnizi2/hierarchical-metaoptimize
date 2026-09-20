#!/bin/bash
#SBATCH --job-name=cwd4bite
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --constraint=L4
#SBATCH --cpus-per-task=6
#SBATCH --mem=24G
#SBATCH --time=02:00:00
#SBATCH --output=/home/s5014158/l280_logs/%x-%j.out
# =============================================================================
# cWD4_realrun_bite.sbatch -- ONE short GPU job, NOT part of the batch (job name `cwd4bite`, deliberately NOT the `cwd4-`
# prefix the batch guards and the scorer read).  CORRECTIONS 280.
#   (1) tests/test_decaymask.py --structural-only on cwd1's tree: the three PATCH_DECAYMASK regions delete back to cvt8's
#       HF.py byte for byte (D0) -- the tree is cwd1's, UNCHANGED (cwd3 ran on the same bytes);
#   (2) tests/test_decaymask_realrun_cwd4.py: cvt8's tree vs cwd1's tree over 300 real CIFAR-100 steps per variant:
#       OFF bitwise, cwd4's SIX exact masked strings (k = 3 / 2 / 2 / 1 / 1 / 1 -- the k=1 form has never run on THIS
#       network, and {50,53} has never run at all), the update identity at every step, and -- the point of the job --
#       SET DISCRIMINATION BETWEEN THE ARMS WHOSE k COLLIDES (TWOWD0 vs CTL2WD0 at k=2; the three singles at k=1),
#       plus loudness of the name-list grammar on the ONE-name form.
#   (3) EXPORT PROBE: the two-name carrier string, which contains `+` and `.`, is passed through sbatch's --export list
#       exactly as the launcher passes DECAY_MASK, and echoed back -- proof that such a value rides --export unmangled.
#   mkdir -p ~/l280_logs && sbatch --export=ALL,CWD4_EXPORT_PROBE=layer4.0.bn2.weight+layer4.0.shortcut.1.weight \
#       ~/stage_cwd4/bin/cWD4_realrun_bite.sbatch
#       -> copy the .out to $WS/runs/cwd4/bite_decaymask_cwd4.log (the launcher's guard 4f reads it there)
# =============================================================================
set -u
export METAOPT_WS=/home/s5014158/metaopt
module load Python/3.10.4-GCCcore-11.3.0
source $METAOPT_WS/envs/mo/bin/activate
unset VOTE_W BETA_HOLD COMP_HOLD WINDOW_HOLD GROUP_HOLD REST_HOLD DECAY_MASK
echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID} | BATCH=cwd4"
echo "EXPORT_PROBE ${CWD4_EXPORT_PROBE:-unset}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
cd /home/s5014158/stage_cwd4
H=$METAOPT_WS/harness_cwd1/cifar10
P=$METAOPT_WS/harness_cvt8/cifar10
sha256sum tests/test_decaymask.py tests/test_decaymask_realrun.py tests/test_decaymask_realrun_cwd4.py tests/test_grouphold_realrun.py \
  analysis/cwd_design.py analysis/cwd4_design.py patches/patch_decaymask.py
sha256sum $H/Optimizers/HF.py $H/Optimizers/HF.py.pre_decaymask $P/Optimizers/HF.py
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask.py --pre $H/Optimizers/HF.py.pre_decaymask --post $H/Optimizers/HF.py \
  --structural-only
echo "TEST_DECAYMASK_D0_RC $?"
PYTHONDONTWRITEBYTECODE=1 python3 -u tests/test_decaymask_realrun_cwd4.py --tree-pre $P --tree-post $H \
  --steps 300 --every 10 --seed 143 --work /tmp/cwd4_realrun_${SLURM_JOB_ID}
RC=$?
rm -rf /tmp/cwd4_realrun_${SLURM_JOB_ID}
echo "REALRUN_RC $RC"
