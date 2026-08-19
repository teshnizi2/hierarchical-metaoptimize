U=salehkaleybars
# 1. zb-* is the IDENTITY GATE for every per-weight claim. Widen its eligibility so it
#    takes whichever L4 slot frees first (it is 50 min, well inside gpu-short's 4h cap).
for j in $(squeue -h -u $U -o '%i %j' | awk '$2 ~ /^zb-/ {print $1}'); do
  scontrol update jobid=$j Partition=gpu-l4-24g,gpu-short 2>&1
done
# 2. a0h-* is the SGDm alpha0 ladder. Priority item 2 (alpha0 confound) CLOSED in cycle 8
#    sec.3 -- flat to <=0.38pp across alpha0 at 100 epochs. Extra seeds on a closed
#    question must not sit in front of the gate or the new budget control. nice, not cancel
#    (gotcha 14): still worth having eventually.
for j in $(squeue -h -u $U -o '%i %j %T' | awk '$3=="PENDING" && $2 ~ /^a0h-/ {print $1}'); do
  scontrol update jobid=$j nice=5000 2>&1
done
# 3. adg-*-s2 are THIRD seeds on a block whose first two seeds are in flight. Behind the gate.
for j in $(squeue -h -u $U -o '%i %j %T' | awk '$3=="PENDING" && $2 ~ /^adg-/ {print $1}'); do
  scontrol update jobid=$j nice=500 2>&1
done
echo "=== ALICE ORDER (pending, by nice) ==="
squeue -h -u $U -o '%i %j %T %r %y %P' | awk '$3=="PENDING"' | sort -k5,5n -k2,2
