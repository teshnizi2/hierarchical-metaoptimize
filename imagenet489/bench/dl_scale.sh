#!/bin/bash
#SBATCH --partition=cpu-short
#SBATCH --cpus-per-task=48
#SBATCH --mem=64G
#SBATCH --time=00:50:00
#SBATCH --job-name=in489-dlscale
#SBATCH --output=/data1/salehkaleybars/metaopt/runs/in489-dlscale-%j.out
module load Python/3.10.4-GCCcore-11.3.0
source /data1/salehkaleybars/metaopt/envs/mo/bin/activate
export PYTHONUNBUFFERED=1
echo "NODE=$(hostname) CPUS=${SLURM_CPUS_PER_TASK}"
# Does ImageNet-489 throughput scale with dataloader workers?  If it does, the
# bottleneck is per-request BeeGFS latency and more outstanding requests fix it;
# if it plateaus, the ladder is hard-capped and the budget must shrink.
for NW in 4 12 24 44; do
  python -u /data1/salehkaleybars/metaopt/scratch_in489/dl_bench.py \
    /data1/salehkaleybars/metaopt/data/imagenet489 256 $NW 50
done
echo DLSCALE_DONE
