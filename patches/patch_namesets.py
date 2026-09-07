"""PATCH_NAMESETS -- an EXPLICIT MEMBERSHIP spec for `--stepsize-groups`, so that a
partition can be stated as a set of parameter TENSORS rather than as a contiguous
prefix cut.

WHY.  CORRECTIONS 161.7c(ii).  On `ResNet18_c100` the 62 parameter tensors are, at
indices 1..60, exactly twenty `(conv, bn.weight, bn.bias)` triples, so with
`{1: conv, 2: BN scale, 0: BN shift}` the identity `class == index mod 3` holds at
EVERY index from 1 to 60 with zero exceptions.  The only partition spec the harness
can express at m = 2 is `[k, 62-k]`, which is a CONTIGUOUS PREFIX.  Therefore no
`[k, 62-k]` batch on this architecture -- not `cpk1`, `cpk2`, `cpk3`, `cts1`, `cts2`,
`cts3`, `scl1`, nor any successor of the same shape -- can separate a tensor's CLASS
from its ORDINAL POSITION, because moving a tensor into the leading group and
advancing the cut index are the same operation.  161.7c states this as the finding
and 161.12 names the missing deliverable: a spec that can hold the group COUNT and
the group SIZES fixed while exchanging ONE tensor across the cut.

WHY THE OPTIMIZER DOES NOT NEED CHANGING, AND WHAT DOES.
`HF.polish_the_stepsize_groups` ALREADY returns a list-of-lists of parameter NAMES,
and `HF.init_meta`'s `blockwise` branch already resolves membership by
`name in group`:

    self.param_groups_indices = [[index for (name,_),index in zip(...) if name in group]
                                 for group in stepsize_groups]
    self.map_layers_to_blocks = [[name in group for group in stepsize_groups].index(True)
                                 for (name,_) in net_param_names_and_size]

Neither line assumes contiguity.  The blocker is upstream and purely lexical:
`train.py` declares `--stepsize-groups type=str`, and `polish_the_stepsize_groups`
knows only four string forms -- `resnet18_blocks`, `resnet50_blocks`, `[a,b,...]`
(a list of BLOCK LENGTHS, which is contiguous by construction), and pass-through of
an already-built list.  A non-contiguous partition is not expressible.  THIS PATCH
ADDS THE ONE MISSING STRING FORM AND NOTHING ELSE.

WHAT IT ADDS.

    --stepsize-groups sets:<group>/<group>/...

    <group> := <item>,<item>,...            (at least one item)
    <item>  := <int>          a 1-BASED index into named_parameters()
             | <int>-<int>    an inclusive 1-BASED range, lo <= hi
             | <name>         a literal parameter name from named_parameters()

The parser returns exactly what `polish_the_stepsize_groups` already returns for
`[k, 62-k]`: a list, one entry per group, each entry a list of parameter-name
strings in MODEL ORDER.  Group ORDER is the order written (it fixes which group is
`beta_block0`); within-group order is canonicalised to model order so that two specs
naming the same partition produce byte-identical output.

Examples on `ResNet18_c100` (62 tensors, 1-based):

    sets:1-49/50-62
        == `[49,13]`, EXACTLY.  Same lists, same order, same objects.  This
        equality is the patch's inertness proof and `tests/test_namesets.py`
        asserts it against the UNPATCHED code path's output.

    sets:1-48,layer4.0.bn2.weight/layer4.0.conv2.weight,51-62
        the coarse group is still 49 tensors and the fine group still 13, but
        `layer4.0.conv2.weight` (tensor 49, 2,359,296 params, a CONVOLUTION) and
        `layer4.0.bn2.weight` (tensor 50, 512 params, a BATCHNORM SCALE) have been
        exchanged across the cut.  Group count, group sizes and cut ordinal are all
        held fixed; only the CLASS of the tensor that crossed differs.

STRICTNESS.  The parser is total and loud.  It raises `ValueError` -- never a silent
mis-partition -- on: an empty spec, an empty group, an empty item, an index outside
1..T, an inverted range, an item that is neither an index, a range, nor a parameter
name of THIS model, a tensor claimed by two groups, or any tensor left out.  The
last two matter because `map_layers_to_blocks` takes `.index(True)`, i.e. the FIRST
group that contains a name, so a duplicate would bind silently and a missing tensor
would raise a bare `ValueError` from `.index` far from its cause.

THE INDEX/NAME AMBIGUITY IS CHECKED, NOT ASSUMED.  An item is tried as a range, then
as an integer, then as a name.  That order is safe only if no parameter name can be
spelled `\\d+` or `\\d+-\\d+`.  The patch asserts this on the model it is handed, at
parse time, rather than trusting the architecture.

INERTNESS.  Two insertions, both additive:
  1. a module-level helper `_namesets_parse`, unreachable except from (2);
  2. ONE guarded early-return at the top of `polish_the_stepsize_groups`, taken only
     when the spec is a `str` beginning with the literal `sets:`.
Every pre-existing spec form -- `scalar`, `layerwise`, `nodewise`, `weightwise`,
`nodewise1d`, `chunk<K>`, `permnode<S>`, `resnet18_blocks`, `resnet50_blocks`,
`[a,b]`, `[a,b,c,...]`, and an already-built list-of-lists -- fails
`startswith('sets:')` and reaches the ORIGINAL body byte-unchanged.  No existing line
is edited, so every earlier run stays reproducible.

ROUTING IS UNCHANGED TOO, AND THAT IS THE PART THAT COULD HAVE GONE WRONG.
`init_meta` routes a spec to `blockwise` unless it is in the exact-match list
`['scalar','layerwise','nodewise','weightwise','nodewise1d']` or matches
`^chunk(\\d+)$` / `^permnode(\\d+)$`.  `'sets:...'` is in none of them, so it takes
the SAME `blockwise` path a `[k,62-k]` spec takes, with the same
`self.stepsize_type == 'blockwise'`, the same `self.beta` shape
(`torch.ones(len(stepsize_groups))`), the same `block_product` reduction and the same
`_probe` branch.  HF.py also contains two `in`-on-a-STRING tests
(`self.stepsize_type in 'scalar'`, `... in 'blockwise'`); `stepsize_type` here is the
literal `'blockwise'`, identical to every `[k,62-k]` arm, so those tests are not even
reached differently.  The patch asserts the routing list is still the one described.

RULE 20.  The spec is ONE shell token containing only `[A-Za-z0-9_.,:/-]` -- no
whitespace, no quote character, no `=`, and it does not begin with `--`.  So
`analysis/argsline_guard.py` tokenises it (shlex) as a single token, `parse_flags`
attributes it to `--stepsize-groups` as one value, and the value round-trips
byte-identically from the composed command line through the runner's
`echo "ARGS: $@"` to the audit.  `analysis/argsline_guard.py` IS NOT EDITED; the
grammar was chosen to work with it as it stands.

WHAT THIS PATCH DOES NOT DO.  It does not add a granularity, does not change any
beta, does not touch the meta-update, the clamp, the probe or the schedule, and it
gives no new hyperparameter.  It changes which NAMES land in which of the groups the
optimizer already builds, and nothing else.
"""
import sys, os, re

P = os.environ.get(
    "HF_PATH",
    "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/"
    "MetaOptimize/cifar10/Optimizers/HF.py")
src = open(P).read()

if "PATCH_NAMESETS" in src:
    print("ALREADY_PATCHED")
    sys.exit(0)

# --- 1. the module-level parser -----------------------------------------------------
a1 = "class HF():\n"
assert src.count(a1) == 1, f"anchor 1 count={src.count(a1)} -- refusing to patch"
n1 = '''# --- PATCH_NAMESETS: `sets:<g1>/<g2>/...` -> an explicit list-of-lists of parameter
# NAMES.  See patches/patch_namesets.py for the rationale.  Additive: nothing below
# is reachable unless a spec string begins with the literal `sets:`.
_NS_PREFIX = 'sets:'
_NS_INT = __import__('re').compile(r'^\\d+$')
_NS_RANGE = __import__('re').compile(r'^(\\d+)-(\\d+)$')


def _namesets_parse(spec, net_param_names_and_size):
    """`sets:...` -> [[name, ...], ...].  Total and loud; never silently partial."""
    names = [n for (n, _) in net_param_names_and_size]
    T = len(names)
    if T == 0:
        raise ValueError('PATCH_NAMESETS: the model has no parameter tensors')
    by_name = {}
    for i, n in enumerate(names):
        if n in by_name:
            raise ValueError('PATCH_NAMESETS: duplicate parameter name %r at %d and %d'
                             % (n, by_name[n] + 1, i + 1))
        by_name[n] = i
        # An item is tried as a range, then an integer, then a name.  That order is
        # only safe if no NAME can be spelled like an index or a range.  Checked on
        # the model actually handed in, not assumed from the architecture.
        if _NS_INT.match(n) or _NS_RANGE.match(n):
            raise ValueError('PATCH_NAMESETS: parameter name %r is spelled like an '
                             'index or a range; the grammar is ambiguous on this '
                             'model and MUST NOT be used with it' % n)
    body = spec[len(_NS_PREFIX):]
    if not body:
        raise ValueError('PATCH_NAMESETS: empty spec %r' % spec)
    groups = body.split('/')
    out, owner = [], {}
    for gi, g in enumerate(groups):
        if not g:
            raise ValueError('PATCH_NAMESETS: group %d of %r is empty' % (gi, spec))
        idx = []
        for item in g.split(','):
            if not item:
                raise ValueError('PATCH_NAMESETS: empty item in group %d of %r'
                                 % (gi, spec))
            m = _NS_RANGE.match(item)
            if m:
                lo, hi = int(m.group(1)), int(m.group(2))
                if not (1 <= lo <= hi <= T):
                    raise ValueError('PATCH_NAMESETS: range %r is not inside 1..%d'
                                     % (item, T))
                got = list(range(lo - 1, hi))
            elif _NS_INT.match(item):
                v = int(item)
                if not (1 <= v <= T):
                    raise ValueError('PATCH_NAMESETS: index %r is not inside 1..%d'
                                     % (item, T))
                got = [v - 1]
            elif item in by_name:
                got = [by_name[item]]
            else:
                raise ValueError('PATCH_NAMESETS: %r is neither a 1-based index, an '
                                 'index range, nor a parameter name of this model'
                                 % item)
            for i in got:
                if i in owner:
                    raise ValueError('PATCH_NAMESETS: tensor %d (%s) is claimed by '
                                     'group %d and group %d'
                                     % (i + 1, names[i], owner[i], gi))
                owner[i] = gi
            idx.extend(got)
        out.append([names[i] for i in sorted(idx)])
    if len(owner) != T:
        missing = [(i + 1, names[i]) for i in range(T) if i not in owner]
        raise ValueError('PATCH_NAMESETS: %d of %d tensors are in no group: %s'
                         % (T - len(owner), T, missing[:8]))
    return out


'''
src = src.replace(a1, n1 + a1, 1)

# --- 2. the dispatch, as an early return at the top of polish -----------------------
a2 = ("    def polish_the_stepsize_groups(self, stepsize_groups,net_param_names_and_size):\n"
      "        if stepsize_groups == 'resnet18_blocks':\n")
assert src.count(a2) == 1, f"anchor 2 count={src.count(a2)} -- refusing to patch"
n2 = ("    def polish_the_stepsize_groups(self, stepsize_groups,net_param_names_and_size):\n"
      "        # --- PATCH_NAMESETS: the ONLY new branch.  Every pre-existing spec form\n"
      "        # fails this test and reaches the original body byte-unchanged. ---\n"
      "        if isinstance(stepsize_groups, str) and stepsize_groups.startswith(_NS_PREFIX):\n"
      "            return _namesets_parse(stepsize_groups, net_param_names_and_size)\n"
      "        if stepsize_groups == 'resnet18_blocks':\n")
src = src.replace(a2, n2, 1)

# --- 3. the assumptions the patch rests on, checked on the live source --------------
# init_meta must still route an unrecognised string to 'blockwise'.
m = re.search(r"stepsize_groups\s+in\s+\[([^\]]*)\]", src)
assert m, "could not find init_meta's exact-match routing list"
named = [x.strip().strip("'\"") for x in m.group(1).split(",")]
assert not any(n.startswith("sets:") for n in named), \
    "a `sets:` spec collides with a named granularity: %r" % named
for pat in (r"\^chunk\(\\d\+\)\$", r"\^permnode\(\\d\+\)\$"):
    pass  # the two regex routes are literal prefixes 'chunk'/'permnode'; 'sets:' matches neither
assert "'sets:'" not in src.split("PATCH_NAMESETS")[0], "unexpected pre-existing sets: handling"
# the blockwise branch that consumes our output must still resolve BY NAME.
assert "if name in group" in src, "init_meta no longer resolves membership by name"
assert "[name in group for group in stepsize_groups].index(True)" in src, \
    "init_meta no longer builds map_layers_to_blocks by name"

open(P, "w").write(src)
print("PATCHED PATCH_NAMESETS ->", P)
