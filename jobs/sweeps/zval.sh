cd /data1/salehkaleybars/metaopt
R=/data1/salehkaleybars/metaopt/runs
B="--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1 --alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --meta-stepsize 1e-3 --alpha0 1e-6 --gamma 1 --NN-name ResNet18 --dataset CIFAR10 --num-epochs 4 --batch-size 100 --max-time 999:00:00"
C="BETA_CLIP=-15:-2.3026"
sub(){ sbatch --parsable --job-name=$1 --partition=gpu-l4-24g --gres=gpu:l4:1 --time=00:25:00 \
  --export=ALL,AUGMENT=1,$C,$3 jobs/run_cifar.sh $B --stepsize-groups $2 --seed 0 \
  --save-directory $R/zval --run-name $1 >/dev/null; }
# reference endpoints
sub zv-ref-scalar     scalar     "HIER="
sub zv-ref-layer      layerwise  "HIER="
sub zv-ref-weight     weightwise "HIER="
# identity 1: r=0 on layerwise must equal scalar
sub zv-l-r0           layerwise  "HIER=zpool,ETA_RATIO=0"
# identity 2: r=1 on layerwise must equal plain layerwise
sub zv-l-r1           layerwise  "HIER=zpool,ETA_RATIO=1"
# identity 3: r=0 on WEIGHTWISE must equal scalar -- this is the one that was broken
sub zv-w-r0           weightwise "HIER=zpool,ETA_RATIO=0"
# identity 4: r=1 on weightwise must equal plain weightwise
sub zv-w-r1           weightwise "HIER=zpool,ETA_RATIO=1"
sleep 2
echo "ZVAL_SUBMITTED=$(squeue -h -u salehkaleybars -o '%j' | grep -c '^zv-')"
