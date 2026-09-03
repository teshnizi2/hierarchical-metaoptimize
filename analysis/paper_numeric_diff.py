#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""paper_numeric_diff.py -- the integration-time numeric diff between the two markups.

The house rule is that **every edit lands in BOTH `paper/paper.tex` and
`paper/DRAFT-v4.md`**, and that a numeric diff between them is run at integration and
must come back clean.  This is that diff, made mechanical so it cannot be skipped.

WHAT IS COMPARED.  The same token class §3.4's coverage census counts -- a decimal
numeral `\\d+\\.\\d+` -- plus thousands-grouped integers (`2{,}177` in TeX, `2,177` in
Markdown), which are the corpus counts.  Both files are normalised first so that the
two idioms for the same number compare equal:

    2{,}177   ==  2,177          $\\mathbf{-0.238}$  ==  **-0.238**
    $-0.149$  ==  -0.149         \\%                 ==  %
    U+2212 (minus)  ==  "-"      U+00B1 (plus-minus) ==  "+-"

WHAT IS EXCLUDED, and why.  Verbatim scorer output is quoted in both files but wrapped
differently (```fences``` in Markdown, `verbatim`/`lstlisting` in TeX, indented blocks
in both), and the numerals inside it belong to the scorers, not to us -- the census
excludes them for the same reason.  Cross-references (§4.8, Table 2, A.11, T9, R2,
arXiv ids) and software versions are excluded by the census's own two regexes, reused
here rather than restated.

The comparison is a MULTISET comparison: a number printed twice in one file and once in
the other is a residual, because that is exactly how a half-applied edit shows up.

    python3 analysis/paper_numeric_diff.py            # exit 0 iff clean
    python3 analysis/paper_numeric_diff.py --show 40  # more context per residual
"""
import argparse, collections, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
TEX = os.path.join(ROOT, "paper", "paper.tex")
MD = os.path.join(ROOT, "paper", "DRAFT-v4.md")

# --- the census's own two exclusion regexes, imported rather than restated -----
sys.path.insert(0, HERE)
import c98_reproduce as C98                                       # noqa: E402
_XREF, _VERSION = C98._XREF, C98._VERSION

NUM = re.compile(r"\d{1,3}(?:,\d{3})+|\d+\.\d+")

# --------------------------------------------------------------- normalisation
def _common(s):
    s = s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "---")
    s = s.replace("\u00b1", "+-").replace("\u00d7", "x")
    s = re.sub(r"[ \t]+", " ", s)
    return s

def norm_tex(s):
    s = re.sub(r"(?m)^\s*%.*$", " ", s)                # comments
    s = re.sub(r"(?<!\\)%.*", " ", s)                  # trailing comments
    # quoted scorer output: `verbatim`/`lstlisting` and the `quote` environment,
    # whose Markdown counterparts are the ``` fence and the `>` block.
    s = re.sub(r"\\begin\{(verbatim|lstlisting|Verbatim|quote)\}.*?\\end\{\1\}", " ",
               s, flags=re.S)
    s = re.sub(r"\\verb\|[^|]*\|", " ", s)
    # \S7.1 is the same cross-reference the Markdown writes as \u00a77.1; make the
    # census's cross-reference regex see it.
    s = s.replace("\\S", "\u00a7")
    # typesetting lengths -- column specs, minipage widths, em/pt/ex dimensions and
    # \setlength values -- have no counterpart in the Markdown and are not quantities.
    s = re.sub(r"\\begin\{(tabular|minipage|tabularx)\}(\[[^\]]*\])?\{[^{}]*(\{[^{}]*\}[^{}]*)*\}",
               " ", s)
    # NB the unit list deliberately excludes `in`/`cm`: "2,173 in and out" would
    # otherwise lose its second numeral to a phantom length.
    s = re.sub(r"[-+]?\d*\.?\d+\s*(?:em|ex|pt|\\linewidth|\\textwidth|\\columnwidth)"
               r"(?![a-zA-Z])", " ", s)
    s = re.sub(r"\\(?:setlength|captionsetup|arrayrulewidth|tabcolsep|hbadness|vbadness)"
               r"\s*(\{[^{}]*\})*", " ", s)
    s = s.replace("{,}", ",")                          # 2{,}177 -> 2,177
    s = s.replace(r"\%", "%").replace(r"\,", " ").replace(r"\;", " ")
    s = re.sub(r"\\(?:label|ref|eqref|cite[a-z]*|includegraphics|bibliography\w*|"
               r"usepackage|documentclass|newcommand|renewcommand|input|def|"
               r"hspace|vspace|rule)\s*(\[[^\]]*\])?(\{[^{}]*\})*", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)              # remaining macros
    s = re.sub(r"[{}$&\\~^_]", " ", s)
    return _common(s)

def norm_md(s):
    s = re.sub(r"```.*?```", " ", s, flags=re.S)       # quoted scorer output
    s = re.sub(r"(?m)^ {4,}\S.*$", " ", s)             # indented verbatim
    s = re.sub(r"(?m)^\s*>.*$", " ", s)                # block-quoted scorer output
    # the Markdown embeds LaTeX display math verbatim, thousands separators included
    s = s.replace("{,}", ",")                          # 14{,}421 -> 14,421
    # ATX heading numerals ("### 4.8 Budget: ...") are the Markdown's section numbers;
    # the TeX carries them as \subsection with no printed numeral, so they are the
    # one structural idiom that has no counterpart and are dropped here.
    s = re.sub(r"(?m)^\s*#{1,6}\s*\d+(?:\.\d+)*", " ", s)
    s = re.sub(r"[`*_]", " ", s)
    return _common(s)

def quantities(text):
    """(multiset, first-context map) of the quantity numerals in normalised text."""
    bag, ctx = collections.Counter(), {}
    for m in NUM.finditer(text):
        pre = text[max(0, m.start() - 24):m.start()]
        if _XREF.search(pre) or _VERSION.search(pre):
            continue
        tok = m.group(0)
        bag[tok] += 1
        ctx.setdefault(tok, text[max(0, m.start() - 70):m.end() + 40].strip())
    return bag, ctx

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", type=int, default=110, help="context characters printed")
    a = ap.parse_args()

    t_bag, t_ctx = quantities(norm_tex(open(TEX, encoding="utf-8").read()))
    m_bag, m_ctx = quantities(norm_md(open(MD, encoding="utf-8").read()))

    print("=" * 78)
    print("NUMERIC DIFF -- paper/paper.tex  vs  paper/DRAFT-v4.md")
    print("=" * 78)
    print("  quantity numerals in paper.tex     %5d  (%d distinct)"
          % (sum(t_bag.values()), len(t_bag)))
    print("  quantity numerals in DRAFT-v4.md   %5d  (%d distinct)"
          % (sum(m_bag.values()), len(m_bag)))

    only_t = sorted((t_bag - m_bag).elements())
    only_m = sorted((m_bag - t_bag).elements())
    print("  in paper.tex and NOT in DRAFT-v4.md   %3d" % len(only_t))
    print("  in DRAFT-v4.md and NOT in paper.tex   %3d" % len(only_m))

    for name, extra, ctx in (("paper.tex", only_t, t_ctx), ("DRAFT-v4.md", only_m, m_ctx)):
        if not extra: continue
        print("\n  -- present in %s only ------------------------------------------" % name)
        for tok in sorted(set(extra)):
            n = extra.count(tok)
            print("     %-10s x%d   %s" % (tok, n, ctx[tok][:a.show].replace("\n", " ")))

    clean = not only_t and not only_m
    print("\n  VERDICT: %s" % ("CLEAN -- the two markups agree numeral for numeral"
                               if clean else "RESIDUALS -- the two markups disagree"))
    return 0 if clean else 1

if __name__ == "__main__":
    sys.exit(main())
