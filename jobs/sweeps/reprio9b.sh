U=s5014158
# 1. z2-* is the VOID 4-epoch identity design (FINDINGS cycle 8 sec.7 / gotcha 25). Cycle 8
#    recorded it as "cancelled before it ran" -- it was NOT; all 6 are still queued. It can
#    only reproduce a result already known to carry zero information, and it sits in front of
#    z3-*, its own replacement. This is the one block worth scancel rather than nice.
Z2=$(squeue -h -u $U -o '%i %j' | awk '$2 ~ /^z2-/ {print $1}')
echo "Z2_TO_CANCEL: $Z2"
[ -n "$Z2" ] && scancel $Z2
# 2. a0A-* pending: alpha0 confound CLOSED (cycle 8 sec.3). Extra seeds go behind the
#    identity gate and the peak-location cells. nice, not cancel (gotcha 14).
for j in $(squeue -h -u $U -o '%i %j %T' | awk '$3=="PENDING" && $2 ~ /^a0A-/ {print $1}'); do
  scontrol update jobid=$j nice=5000
done
sleep 2
echo "=== ALICE2 ORDER (pending, by nice) ==="
squeue -h -u $U -o '%i %j %T %r %y %P' | awk '$3=="PENDING"' | sort -k5,5n -k2,2
echo "=== RUNNING ==="
squeue -h -u $U -t R -o '%i %j %M'
