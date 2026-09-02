#!/bin/bash
# =============================================================================
# _lib_guards.sh -- SOURCEABLE GUARD LIBRARY.  STANDING RULES 20 AND 21.
#
# Two batches (`ml2`, `sm3`) were composed with a duplicated `--alg-meta`,
# submitted, run to completion and reported before anyone read a run's own
# ARGS line.  argparse keeps the LAST occurrence, so both ran an optimiser
# nobody had declared.  This library makes that class of bug impossible to
# carry all the way to a result:
#
#   guard_presubmit   <CMD> [flag=value ...]   BEFORE sbatch.  Composes nothing
#                                              itself: it reads the exact string
#                                              the script is about to `eval`,
#                                              rejects any repeated flag, and
#                                              checks the declared design.
#   guard_postlaunch  <OUTDIR> <PREFIX> [flag=value ...]
#                                              AFTER sbatch.  Waits for the
#                                              first run's own ARGS line and
#                                              aborts the batch if it does not
#                                              match the declared design.
#
# HOW TO USE IT IN A SUBMISSION SCRIPT
#   . "$(dirname "$0")/_lib_guards.sh"
#   DESIGN=(alg-base=AdamW alg-meta=RMSProp meta-stepsize=1e-4 alpha0=1e-3 \
#           num-epochs=100 dataset=CIFAR10 NN-name=ResNet18)
#   ...
#   CMD="sbatch ... $RUNNER --optimizer HF $BFLAGS ..."
#   guard_presubmit "$CMD" "${DESIGN[@]}" || { echo "ABORTED"; exit 2; }
#   [ "$SUBMIT" = 1 ] && eval "$CMD"
#   ...
#   guard_postlaunch "$WS/runs" "sm3-" "${DESIGN[@]}" || exit 2
#
# The heavy lifting is done by analysis/argsline_guard.py so that the
# pre-submission check and the post-hoc audit share ONE parser.  If that file
# is unreachable the library falls back to a pure-awk duplicate detector, which
# is weaker (no design check) but never silently passes.
#
# ABORTING A LAUNCHED BATCH.  guard_postlaunch never cancels jobs on its own by
# default -- it prints the exact `scancel` line and returns non-zero.  Export
# ARGSGUARD_AUTOCANCEL=1 to have it run that scancel itself.
#
# TUNABLES (environment)
#   ARGSGUARD_WAIT=600        seconds to wait for the first ARGS line
#   ARGSGUARD_POLL=15         seconds between polls
#   ARGSGUARD_AUTOCANCEL=0    1 = scancel the batch on a post-launch failure
#   ARGSGUARD_PY=<path>       override the location of argsline_guard.py
# =============================================================================

# ---- venv activation preamble (house rules; guards that import torch fail
# ---- without it -- five consecutive submission aborts were caused by this)
WS=${METAOPT_WS:-/data1/salehkaleybars/metaopt}
module load Python/3.10.4-GCCcore-11.3.0 >/dev/null 2>&1 || true
# shellcheck disable=SC1091
[ -f "$WS/envs/mo/bin/activate" ] && . "$WS/envs/mo/bin/activate" 2>/dev/null || true

# ---- locate the shared parser ------------------------------------------------
_ag_here="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
ARGSGUARD_PY="${ARGSGUARD_PY:-}"
if [ -z "$ARGSGUARD_PY" ]; then
  for _c in "$_ag_here/../analysis/argsline_guard.py" \
            "$_ag_here/../hierarchical-metaoptimize/analysis/argsline_guard.py" \
            "$WS/hierarchical-metaoptimize/analysis/argsline_guard.py" \
            "$WS/analysis/argsline_guard.py"; do
    [ -f "$_c" ] && { ARGSGUARD_PY="$(cd "$(dirname "$_c")" && pwd)/$(basename "$_c")"; break; }
  done
fi
ARGSGUARD_WAIT=${ARGSGUARD_WAIT:-600}
ARGSGUARD_POLL=${ARGSGUARD_POLL:-15}
ARGSGUARD_AUTOCANCEL=${ARGSGUARD_AUTOCANCEL:-0}

_ag_py() { command -v python3 >/dev/null 2>&1 && echo python3 || echo python; }

# ---- pure-awk fallback: duplicate detection only -----------------------------
# stdin: the token stream.  stdout: "flag count v1 | v2 | ..." per repeated flag.
_ag_awk_dupes() {
  awk '
    function flush(  s,i) { if (cur != "") { n[cur]++; v[cur, n[cur]] = val; } }
    {
      for (i = 1; i <= NF; i++) {
        t = $i
        if (substr(t,1,2) == "--" && length(t) > 2) {
          flush()
          if (index(t,"=") > 0) { cur = substr(t,1,index(t,"=")-1); val = substr(t,index(t,"=")+1); flush(); cur=""; val="" }
          else { cur = t; val = "" }
        } else if (cur != "") {
          val = (val == "" ? t : val " " t)
        }
      }
    }
    END {
      flush()
      for (f in n) if (n[f] > 1) {
        s = ""
        for (i = 1; i <= n[f]; i++) s = s (i>1 ? " | " : "") "\047" v[f,i] "\047"
        printf "%s x%d  %s   -> EFFECTIVE \047%s\047\n", f, n[f], s, v[f,n[f]]
      }
    }'
}

_ag_normalise_cmd() {
  # collapse line continuations and newlines so the token stream is flat
  printf '%s\n' "$1" | sed -e ':a' -e 'N' -e '$!ba' -e 's/\\\n/ /g' | tr '\n' ' '
}

_ag_expect_args() {
  # turn "flag=value ..." into "--expect flag=value ..."
  local out="" e
  for e in "$@"; do out="$out --expect $e"; done
  printf '%s' "$out"
}

# =============================================================================
# guard_presubmit  <CMD> [flag=value ...]
#   Rejects the command line BEFORE sbatch if any flag is repeated (in the
#   sbatch half or the train.py half) or if the effective value of a declared
#   design flag is not what was declared.  Returns 0 on PASS, 1 on FAIL.
# =============================================================================
guard_presubmit() {
  local cmd="$1"; shift
  local flat; flat="$(_ag_normalise_cmd "$cmd")"
  local rc=0

  if [ -n "$ARGSGUARD_PY" ] && [ -f "$ARGSGUARD_PY" ]; then
    "$(_ag_py)" "$ARGSGUARD_PY" --quiet --cmdline "$flat" $(_ag_expect_args "$@") || rc=1
  else
    echo "guard_presubmit: WARNING -- analysis/argsline_guard.py not found; "\
"awk fallback (duplicate detection only, NO design check)"
    local dupes; dupes="$(printf '%s\n' "$flat" | _ag_awk_dupes)"
    if [ -n "$dupes" ]; then
      echo "  !!! REPEATED FLAGS -- argparse keeps the LAST value:"
      printf '%s\n' "$dupes" | sed 's/^/      /'
      rc=1
    else
      echo "guard_presubmit: no repeated flag"
    fi
  fi

  if [ "$rc" != 0 ]; then
    echo "!!! GUARD FAIL (STANDING RULE 20): the command line does not say what"
    echo "!!! the script header claims.  NOTHING SUBMITTED.  Fix the composition"
    echo "!!! (a flag appended after a \$BFLAGS block is the usual cause)."
  else
    echo "guard_presubmit: PASS -- command line matches the declared design"
  fi
  return $rc
}

# =============================================================================
# guard_postlaunch  <OUTDIR> <JOBNAME_PREFIX> [flag=value ...]
#   Waits (ARGSGUARD_WAIT s) for the first "<OUTDIR>/<PREFIX>*.out" to carry an
#   ARGS line, then audits that run's OWN ARGS line against the declared design.
#   On failure it prints the scancel line, and runs it when
#   ARGSGUARD_AUTOCANCEL=1.  Returns 0 on PASS, 1 on FAIL, 2 if no ARGS line
#   appeared before the timeout (UNVERIFIED -- treat as a failure).
# =============================================================================
guard_postlaunch() {
  local outdir="$1" prefix="$2"; shift 2
  local waited=0 first=""

  echo "guard_postlaunch: watching $outdir/$prefix*.out for the first ARGS line"
  while [ "$waited" -lt "$ARGSGUARD_WAIT" ]; do
    first="$(ls -1t "$outdir"/"$prefix"*.out 2>/dev/null | while read -r f; do
               grep -q '^ARGS:' "$f" 2>/dev/null && { echo "$f"; break; }; done)"
    [ -n "$first" ] && break
    sleep "$ARGSGUARD_POLL"; waited=$((waited + ARGSGUARD_POLL))
  done

  if [ -z "$first" ]; then
    echo "!!! guard_postlaunch: NO ARGS line under $outdir/$prefix*.out after"
    echo "!!! ${ARGSGUARD_WAIT}s.  The batch is UNVERIFIED -- audit it by hand"
    echo "!!! before any number from it is quoted:"
    echo "!!!   python3 analysis/argsline_guard.py $outdir --name $prefix"
    return 2
  fi

  echo "guard_postlaunch: auditing $first"
  echo "--- the run's OWN ARGS line, verbatim ---"
  grep -m1 '^ARGS:' "$first"
  echo "-----------------------------------------"

  local rc=0
  if [ -n "$ARGSGUARD_PY" ] && [ -f "$ARGSGUARD_PY" ]; then
    "$(_ag_py)" "$ARGSGUARD_PY" --quiet "$first" $(_ag_expect_args "$@") || rc=1
  else
    local dupes
    dupes="$(grep -m1 '^ARGS:' "$first" | sed 's/^ARGS://' | _ag_awk_dupes)"
    if [ -n "$dupes" ]; then
      echo "  !!! REPEATED FLAGS in the run's own ARGS line:"
      printf '%s\n' "$dupes" | sed 's/^/      /'
      rc=1
    fi
  fi

  if [ "$rc" != 0 ]; then
    echo "!!! GUARD FAIL (STANDING RULE 20): the LAUNCHED batch does not match"
    echo "!!! the declared design.  It is VOID AS DESIGNED.  Abort it now:"
    echo "!!!   scancel --name=\$(squeue -h -u \$USER -o %j | grep '^$prefix' | tr '\\n' ',' | sed 's/,\$//')"
    if [ "$ARGSGUARD_AUTOCANCEL" = 1 ]; then
      local names
      names="$(squeue -h -u "${USER:-$(whoami)}" -o %j 2>/dev/null | grep "^$prefix" | sort -u | tr '\n' ',' | sed 's/,$//')"
      if [ -n "$names" ]; then
        echo "ARGSGUARD_AUTOCANCEL=1 -> scancel --name=$names"
        scancel --name="$names" 2>&1 || echo "  (scancel failed; cancel by hand)"
      else
        echo "ARGSGUARD_AUTOCANCEL=1 but no queued job starts with '$prefix'"
      fi
    else
      echo "!!! (set ARGSGUARD_AUTOCANCEL=1 to have this guard scancel for you)"
    fi
  else
    echo "guard_postlaunch: PASS -- the run's own ARGS line matches the design"
  fi
  return $rc
}

# =============================================================================
# guard_scorer_registered  <analysis/xx_score.py>   -- STANDING RULE 21
#   No batch is submitted without a registered scorer.  Prints the scorer's
#   sha256 so the batch report can quote it (Rule 19).
# =============================================================================
guard_scorer_registered() {
  local scorer="$1"
  if [ ! -f "$scorer" ]; then
    echo "!!! GUARD FAIL (STANDING RULE 21): no registered scorer at '$scorer'."
    echo "!!! Write the scorer FIRST; a batch with no scorer has no verdict."
    return 1
  fi
  local h
  h="$( (sha256sum "$scorer" 2>/dev/null || shasum -a 256 "$scorer" 2>/dev/null) | awk '{print $1}')"
  echo "guard_scorer_registered: $scorer  sha256 ${h:-unavailable}"
  return 0
}
