set -e
cd /data1/salehkaleybars/metaopt
R=/data1/salehkaleybars/metaopt/runs
B="--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1 --alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --meta-stepsize 1e-3 --alpha0 1e-6 --gamma 1 --dataset CIFAR10 --num-epochs 2 --batch-size 100 --max-time 999:00:00"
for nn in ResNet34 ResNet50 ResNet101; do
  sbatch --parsable --job-name=sm-$nn --partition=gpu-l4-24g --gres=gpu:l4:1 --time=00:40:00 \
    --export="ALL,AUGMENT=1,BETA_CLIP=-15:-2.3026" \
    jobs/run_cifar.sh $B --NN-name $nn --stepsize-groups layerwise --seed 0 \
    --save-directory $R/smoke_scale --run-name sm_${nn} >/dev/null
done
sleep 2
echo "SMOKE_SUBMITTED=$(squeue -h -u salehkaleybars -o '%j' | grep -c '^sm-')"
