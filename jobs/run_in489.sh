#!/bin/bash
# =============================================================================
# run_in489.sh -- generic ImageNet-489 MetaOptimize runner.
#
# Deliberately a clone of jobs/run_cifar.sh's logging contract:
#   NODE= / ARGS: / ENV:   are what analysis/argsline_guard.py parses (RULE 20)
#   and what aggregate.py keys on.  Do not reword them.
#
# Everything after the script name is passed straight to train_in489.py, e.g.
#   sbatch --job-name=in489-smoke-scalar jobs/run_in489.sh \
#          --optimizer HF --stepsize-groups scalar ...
# =============================================================================
#SBATCH --partition=gpu-l4-24g
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=01:00:00
#SBATCH --output=/data1/salehkaleybars/metaopt/runs/%x-%j.out

set -e
module load Python/3.10.4-GCCcore-11.3.0
source /data1/salehkaleybars/metaopt/envs/mo/bin/activate
cd /data1/salehkaleybars/metaopt/imagenet489

echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
echo "ARGS: $@"
echo "ENV: AUGMENT=1 BETA_CLIP=${BETA_CLIP:-none} HIER=${HIER:-none} LAM=${LAM:-na} ETA_RATIO=${ETA_RATIO:-na} SCHED=${SCHED:-none} SCHED_TOTAL=${SCHED_TOTAL:-none} SCHED_WARMUP=${SCHED_WARMUP:-none} SCHED_MIN=${SCHED_MIN:-none} PROBE=${PROBE:-0} PROBE_DIR=${PROBE_DIR:-none} DATASET=imagenet489 CPUS=${SLURM_CPUS_PER_TASK:-na}"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
export PYTHONUNBUFFERED=1
python -u train_in489.py "$@"
echo "RUN_DONE"
