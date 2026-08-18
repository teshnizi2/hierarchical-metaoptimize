#!/bin/bash
#SBATCH --partition=gpu-short
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=01:45:00
#SBATCH --output=/data1/salehkaleybars/metaopt/runs/%x-%j.out

# Generic CIFAR-10 MetaOptimize runner. All args after the script are passed to train.py.
# e.g. sbatch --job-name=g0-6block run_cifar.sh --optimizer HF --stepsize-groups resnet18_blocks ...
set -e
module load Python/3.10.4-GCCcore-11.3.0
source /data1/salehkaleybars/metaopt/envs/mo/bin/activate
cd /data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10

echo "NODE=$(hostname) | JOB=${SLURM_JOB_NAME} ${SLURM_JOB_ID}"
echo "ARGS: $@"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
python train.py "$@"
echo "RUN_DONE"
