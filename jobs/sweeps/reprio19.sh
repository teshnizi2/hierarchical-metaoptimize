set -e
# CYCLE 19 REPRIORITISATION.
# rc100 (14 jobs) is the M1 r-ladder ON CIFAR-100 -- a SECOND-order refinement of an
# axis whose FIRST-order result (c100-1e6/1e3 granularity comparison) is not in yet,
# and whose scalar arm is currently sitting at 23.08% test. Spending 14 slots on the
# r-ladder before knowing the base comparison works is out of order. Demote it behind
# the scale-ladder extension (sc50/sc101/sc-ResNet34), which is robust either way
# because it was submitted at BOTH alpha0.
# c100-* itself (the first-order comparison) is untouched and stays at the queue front.
n=0
for j in $(squeue -h -u salehkaleybars -t PENDING -o "%i %j" | awk '$2 ~ /^rc100-/ {print $1}'); do
  scontrol update JobId=$j Nice=3000 && n=$((n+1))
done
echo "RC100_DEMOTED=$n"
sleep 2
squeue -u salehkaleybars -h -t PENDING -o "%j" --sort=-p,i | nl | sed 's/-s[0-9]*$//' \
  | awk '{n=$2; if(!(n in mn)) mn[n]=$1; mx[n]=$1} END {for (k in mn) printf "%-24s %4d-%4d\n", k, mn[k], mx[k]}' \
  | sort -k2 -n | sed -n '1,26p'
