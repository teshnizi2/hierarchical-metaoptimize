#!/bin/bash
#SBATCH --partition=interactive,testing,gpu-short,gpu-l4-24g,gpu-mig-40g,gpu-a100-80g,gpu-2080ti-11g
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=24G
#SBATCH --time=00:25:00
#SBATCH --job-name=in489-gpuonly
#SBATCH --output=/data1/salehkaleybars/metaopt/runs/in489-gpuonly-%j.out
module load Python/3.10.4-GCCcore-11.3.0
source /data1/salehkaleybars/metaopt/envs/mo/bin/activate
export PYTHONUNBUFFERED=1
echo "NODE=$(hostname)"
nvidia-smi --query-gpu=name --format=csv,noheader
python -u /data1/salehkaleybars/metaopt/scratch_in489/gpu_only.py
echo GPUONLY_DONE
