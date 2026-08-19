set -e
cd /data1/salehkaleybars/metaopt
R=/data1/salehkaleybars/metaopt/runs
# CYCLE 8. Two jobs in one block.
#
# (1) adg-*: does the M1 additive INTERIOR OPTIMUM generalise off the cell it was found on?
#     Found on layerwise + SGDm+Lion. Test it on (i) 6-block (m=6, so the shared-mean
#     component is pooled over 6 estimates not 62) and (ii) the PAPER's meta-optimizer
#     (Adam, not Lion) -- if the peak is a sign-nonlinearity artefact of Lion it should
#     vanish under Adam. Shrink generalised across both (FINDINGS: +0.47 blk6, +1.51 Adam),
#     so this is the matched contrast.
#
# (2) nd-*: the guarded plain ladder is non-monotone and PEAKS AT NODEWISE
#     (88.08 / 91.69 / 91.23 / 92.10 / 79.38 for m = 1 / 6 / 62 / ~4.8k / 11.17M)
#     but the nodewise cell is n=1. If it holds at n=5 the paper's ladder is
#     "broad plateau with a cliff only at m=n", not "layerwise is the sweet spot".
#     Highest-value seeds in the campaign right now.
#
# alice's gpu-l4-24g is at its 8-GPU cap; gpu-short is empty and holds L4 nodes
# (node880/881/882/885), so dual-partition with the GRES still pinned to l4 keeps
# timing comparability (gotcha 3) while drawing on the separate gpu-short cap (gotcha 13).
BL="--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1 --alg-meta Lion --momentum-param-meta 0.99 --Lion-beta2-meta 0.9 --weight-decay-meta 0 --meta-stepsize 1e-3 --alpha0 1e-6 --gamma 1 --NN-name ResNet18 --dataset CIFAR10 --num-epochs 100 --batch-size 100 --max-time 999:00:00"
BA="--optimizer HF --alg-base SGDm --momentum-param-base 0.99 --weight-decay-base 0.1 --alg-meta Adam --normalizer-param-meta 0.999 --momentum-param-meta 0.9 --weight-decay-meta 0 --meta-stepsize 1e-3 --alpha0 1e-6 --gamma 1 --NN-name ResNet18 --dataset CIFAR10 --num-epochs 100 --batch-size 100 --max-time 999:00:00"
C="BETA_CLIP=-15:-2.3026"
# $1 name  $2 base-args  $3 granularity  $4 HIER-env  $5 seed
sub(){ sbatch --parsable --job-name=$1-s$5 --partition=gpu-l4-24g,gpu-short --gres=gpu:l4:1 --time=01:30:00 \
  --export="ALL,AUGMENT=1,$C,$4" \
  jobs/run_cifar.sh $2 --stepsize-groups $3 --seed $5 \
  --save-directory $R/addit2 --run-name $1_s$5 >/dev/null; }
for s in 0 1 2; do
  # (1i) 6-block additive at the peak and its inner shoulder
  sub adg-b-r003  "$BL" resnet18_blocks "HIER=additive,ETA_RATIO=0.03" $s
  sub adg-b-r01   "$BL" resnet18_blocks "HIER=additive,ETA_RATIO=0.1"  $s
  # (1ii) layerwise additive under the PAPER's Adam meta
  sub adg-A-r003  "$BA" layerwise       "HIER=additive,ETA_RATIO=0.03" $s
  sub adg-A-r01   "$BA" layerwise       "HIER=additive,ETA_RATIO=0.1"  $s
done
# (2) nodewise plain to n=5 (s0 done, s1 in flight under n1-*)
for s in 2 3 4; do sub nd-node-plain "$BL" nodewise "HIER=" $s; done
sleep 3
echo "ADG_SUBMITTED=$(squeue -h -u salehkaleybars -o '%j' | grep -c '^adg-')"
echo "ND_SUBMITTED=$(squeue -h -u salehkaleybars -o '%j' | grep -c '^nd-')"
echo "TOTAL_QUEUE=$(squeue -h -u salehkaleybars | wc -l)"
