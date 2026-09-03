#!/usr/bin/env python3
r"""xref_check.py -- resolve every hand-typed cross-reference in paper/DRAFT-v4.md.

WHY THIS EXISTS (CORRECTIONS 136 open item).  DRAFT-v4.md carries several hundred
cross-references typed by hand as literal text: "S4.4", "Table 2", "Figure 3",
"Appendix A.8".  NOTHING in the repo could see an error in any of them.  Both
analysis/paper_numeric_diff.py and c98_reproduce.py's coverage census route through
their _XREF exclusion, which deliberately drops any numeral preceded by S, Table,
Figure, App. or Eq. -- because those numerals are labels, not quantities.  The
consequence is that a wrong section number gives: numeric diff clean, c98 ALL PASS,
tectonic exit 0, 0 undefined refs.  Only a human reading every string would catch it.

In paper/paper.tex the same references are \ref{} and LaTeX guarantees them.  The
Markdown has no such guarantee and is a SHIPPED artefact, so it needs this.

THE PARENT-PAPER TRAP.  A handful of "SN.M" strings point at the sections of the
PARENT paper (arXiv:2402.02342), not ours, and are typographically identical to
references to our own sections.  In the TeX they are distinguishable (literal
\S<digit> for the parent, \ref{} for ours); in the Markdown they are not.  They are
allowlisted BY LINE NUMBER below, and the allowlist is itself checked: if a listed
line no longer contains a parent-paper reference the run FAILS, so the allowlist
cannot silently rot as the draft moves.

Run: python3 analysis/xref_check.py [--selftest]
"""
import os, re, sys

ROOT  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = os.path.join(ROOT, "paper", "DRAFT-v4.md")

# Lines whose "SN.M" refers to the PARENT paper's own sections, not ours.
PARENT_LINES = {41, 43, 45, 250, 254, 257, 258, 260}

_FENCE = re.compile(r"(?s:```.*?```)|(?m:^ {4,}\S.*$)")

def headings(text):
    """Section numbers the draft actually defines, from its heading tree."""
    secs, tables, figures, apps = set(), set(), set(), set()
    for line in text.splitlines():
        m = re.match(r"^#{2,6}\s+(\d+(?:\.\d+)*)\.?\s", line)
        if m:
            secs.add(m.group(1))
            continue
        m = re.match(r"^#{2,6}\s+Appendix\s+([A-Z])\b", line)
        if m:
            apps.add(m.group(1))
    # Appendix subsections are bold run-in heads: **A.3b - ...**
    for m in re.finditer(r"^\*\*([A-Z]\.\d+[a-z]?)\s*[-—]", text, re.M):
        apps.add(m.group(1))
    for m in re.finditer(r"^\**Table\s+(\d+)", text, re.M):
        tables.add(m.group(1))
    for m in re.finditer(r"^\**Figure\s+(\d+)", text, re.M):
        figures.add(m.group(1))
    return secs, tables, figures, apps

def refs(text):
    """Every hand-typed cross-reference, with its 1-based line number."""
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(r"§\s?(\d+(?:\.\d+)*)", line):
            out.append(("section", m.group(1), i, m.group(0)))
        for m in re.finditer(r"\bTable\s+(\d+)", line):
            out.append(("table", m.group(1), i, m.group(0)))
        for m in re.finditer(r"\bFigure\s+(\d+)", line):
            out.append(("figure", m.group(1), i, m.group(0)))
        for m in re.finditer(r"\bAppendix\s+([A-Z](?:\.\d+[a-z]?)?)", line):
            out.append(("appendix", m.group(1), i, m.group(0)))
    return out

def check(path=DRAFT, quiet=False):
    raw  = open(path).read()
    body = _FENCE.sub(lambda m: " " * len(m.group(0)), raw)   # keep line numbering
    secs, tables, figures, apps = headings(raw)
    allrefs = refs(body)

    bad, parent_used = [], set()
    for kind, val, line, literal in allrefs:
        if kind == "section" and line in PARENT_LINES:
            parent_used.add(line)
            continue
        known = {"section": secs, "table": tables,
                 "figure": figures, "appendix": apps}[kind]
        if val not in known:
            bad.append((kind, val, line, literal))

    # the allowlist must not rot
    stale = sorted(PARENT_LINES - parent_used)

    if not quiet:
        print("=" * 78)
        print("XREF CHECK -- %s" % os.path.relpath(path, ROOT))
        print("=" * 78)
        print("  sections defined      %3d   %s" % (len(secs), " ".join(sorted(secs, key=_key))))
        print("  appendix units        %3d   %s" % (len(apps), " ".join(sorted(apps))))
        print("  tables / figures      %3d / %d" % (len(tables), len(figures)))
        print("  references found      %3d   (section %d, table %d, figure %d, appendix %d)"
              % (len(allrefs),
                 sum(1 for r in allrefs if r[0] == "section"),
                 sum(1 for r in allrefs if r[0] == "table"),
                 sum(1 for r in allrefs if r[0] == "figure"),
                 sum(1 for r in allrefs if r[0] == "appendix")))
        print("  parent-paper refs     %3d   allowlisted lines %s"
              % (len(parent_used), sorted(parent_used)))
        if bad:
            print("\n  UNRESOLVED REFERENCES")
            for kind, val, line, literal in bad:
                print("    %s:%d  %-9s %r -> no such %s" % (
                    os.path.basename(path), line, kind, literal, kind))
        if stale:
            print("\n  STALE ALLOWLIST -- these lines no longer carry a parent-paper "
                  "reference: %s" % stale)
        ok = not bad and not stale
        print("\n  VERDICT: %s" % ("PASS -- every reference resolves" if ok
                                   else "FAIL -- %d unresolved, %d stale allowlist entries"
                                        % (len(bad), len(stale))))
    return bad, stale

def _key(s):
    return [int(p) for p in s.split(".")]

def selftest():
    fails = []
    probe = ("## 4. Results\n### 4.8 Budget\n## Appendix A. Register\n"
             "**A.3 - thing**\n**Table 2** cap\n**Figure 1** cap\n"
             "text §4.8 and Table 2 and Figure 1 and Appendix A.3 are fine\n"
             "text §9.9 and Table 7 and Appendix A.99 are not\n")
    secs, tables, figures, apps = headings(probe)
    if secs != {"4", "4.8"}: fails.append("headings: sections %r" % secs)
    if apps != {"A", "A.3"}: fails.append("headings: appendix %r" % apps)
    if tables != {"2"} or figures != {"1"}: fails.append("headings: floats")
    got = {(k, v) for k, v, _, _ in refs(probe)}
    for want in (("section", "4.8"), ("table", "2"), ("figure", "1"), ("appendix", "A.3"),
                 ("section", "9.9"), ("table", "7"), ("appendix", "A.99")):
        if want not in got: fails.append("refs missed %r" % (want,))
    for f in fails: print("FAIL: %s" % f)
    print("xref_check selftest: %s" % ("5/5 PASS" if not fails else "%d FAILURE(S)" % len(fails)))
    return 1 if fails else 0

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    bad, stale = check()
    sys.exit(1 if (bad or stale) else 0)
