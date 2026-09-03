#!/usr/bin/env python3
r"""Regression test for the _FENCE masking bug (CORRECTIONS 136).

c98_reproduce.py's _FENCE once read

    re.compile(r"```.*?```|^ {4,}\S.*$", re.S | re.M)

The shared re.S made `.` match newlines, so the indented-command branch's `.*$`
ran to the LAST `$` in the file.  One mask swallowed 49,965 of 308,256 characters
of paper/DRAFT-v4.md -- 16.1% of the draft was invisible to the coverage census,
and the census denominator is printed in the paper as a claim (S3.4).  The bug
overstated coverage as 45.9% when the true figure is 42.0%.

analysis/paper_numeric_diff.py always had it right ((?m) only, no re.S).  The two
are required to share ONE exclusion rule and S3.4 says so, so the invariant this
test pins is that they mask the SAME character positions.

Run: python3 analysis/test_fence_mask.py
"""
import importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def covered(matches):
    out = set()
    for m in matches:
        out.update(range(*m.span()))
    return out

def main():
    fails = []

    # 1. The two branches must not share a flag scope.  A single re.S over the
    #    whole alternation is the bug; assert the pattern carries inline scopes.
    src = open(os.path.join(ROOT, "analysis", "c98_reproduce.py")).read()
    line = [l for l in src.splitlines() if l.startswith("_FENCE")]
    if not line:
        fails.append("_FENCE definition not found in c98_reproduce.py")
    elif "re.S | re.M" in line[0] or "re.DOTALL" in line[0]:
        fails.append("_FENCE carries a shared re.S -- the masking bug is back: %s" % line[0])

    # 2. Synthetic: an indented line followed by prose must mask ONLY that line.
    c98 = _load("c98_fence", os.path.join(ROOT, "analysis", "c98_reproduce.py"))
    probe = "    $ scorer --run 1.111\nprose 2.222 and 3.333\nmore 4.444\n"
    masked = c98._FENCE.sub(" ", probe)
    for keep in ("2.222", "3.333", "4.444"):
        if keep not in masked:
            fails.append("_FENCE swallowed %s past the end of an indented line" % keep)
    if "1.111" in masked:
        fails.append("_FENCE failed to mask the indented command itself")

    # 3. The real invariant: c98 and paper_numeric_diff must mask the SAME
    #    positions of the live draft.
    draft = os.path.join(ROOT, "paper", "DRAFT-v4.md")
    if os.path.exists(draft):
        text = open(draft).read()
        a = covered(c98._FENCE.finditer(text))
        b = (covered(re.finditer(r"```.*?```", text, re.S))
             | covered(re.finditer(r"(?m)^ {4,}\S.*$", text)))
        if a != b:
            fails.append("c98 masks %d positions, paper_numeric_diff masks %d -- "
                         "they must share one rule (only-c98 %d, only-diff %d)"
                         % (len(a), len(b), len(a - b), len(b - a)))
        frac = 100.0 * len(a) / max(1, len(text))
        if frac > 5.0:
            fails.append("masking %.1f%% of the draft is implausible -- the bug masked 16.9%%" % frac)

    for f in fails:
        print("FAIL: %s" % f)
    print("test_fence_mask: %s" % ("ALL PASS" if not fails else "%d FAILURE(S)" % len(fails)))
    return 1 if fails else 0

if __name__ == "__main__":
    sys.exit(main())
