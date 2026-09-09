"""Inertness AND decomposition of PATCH_PROBE_TENSOR on the FOUR m=2 `sets:`
(blockwise) partitions `cdep1` runs -- ISO, DEPTH, DEPTH2, ONE.

WHY THIS FILE EXISTS AND WHY THE REGISTERED TEST IS NOT EDITED.
tests/test_probe_tensor_blockwise.py was registered with `ciso1` (CORRECTIONS
187) and its SPECS dict is a LITERAL holding that batch's three arms.  STANDING
RULE 16 forbids editing a registered artefact once its data exist: it is FROZEN
and a successor is registered instead (precedent cN1/cN2 at 149, cdn1/cdn2 at
175).  This file is that successor.  It does NOT copy the registered test's
logic and it does NOT modify the file on disk -- it IMPORTS the module and
re-binds ONE module attribute, `SPECS`, before calling the registered `main()`.
Every check that runs (B0 preconditions, B2 inertness, B3 decomposition, B4 the
applied sign, B5 the header) is the registered test's own code, byte for byte,
executed against `cdep1`'s four spec strings.  The registered file's sha256 is
printed below so the CORRECTIONS entry can quote it and anyone can verify it is
unchanged.

RUN (needs torch; on the cluster against the real tree):
  python3 tests/test_probe_tensor_blockwise_cdep1.py \\
        --pre  /path/HF.py.pre_probe_tensor \\
        --post /path/Optimizers/HF.py \\
        --cifar-dir /path/cifar10 --work /path/scratch
"""
import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import test_probe_tensor_blockwise as TB    # the registered test, imported, NOT edited

# cdep1's four m=2 arms.  These strings are byte-identical to the SPEC table in
# analysis/cDP1_cdep1_depth_score.py and to the G_* variables in
# bin/cDP1_depth_control.sh; the launcher's guard 4c'' proves all three agree.
SPECS_CDEP1 = {
    "ISO": "sets:1-49,51-52,54-58,60-62/layer4.0.bn2.weight,layer4.0.shortcut.1.weight,layer4.1.bn2.weight",
    "DEPTH": "sets:1-46,49-55,57-62/layer4.0.bn1.weight,layer4.0.bn1.bias,layer4.1.bn1.weight",
    "DEPTH2": "sets:1-46,48-55,57-62/layer4.0.bn1.weight,layer4.1.bn1.weight",
    "ONE": "sets:1-49,51-62/layer4.0.bn2.weight",
}

if __name__ == "__main__":
    reg = os.path.join(HERE, "test_probe_tensor_blockwise.py")
    print("REGISTERED_TEST %s" % reg)
    print("REGISTERED_TEST_SHA256 %s" % hashlib.sha256(open(reg, "rb").read()).hexdigest())
    print("REGISTERED_TEST_SPECS_REPLACED_AT_RUNTIME %s -> %s"
          % (sorted(TB.SPECS), sorted(SPECS_CDEP1)))
    TB.SPECS = SPECS_CDEP1
    TB.main()
