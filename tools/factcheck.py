#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factcheck.py — Layer 1 (deterministic) of the fact-check protocol (brain/14).

Usage:
    python tools/factcheck.py episodes/E0XX-slug/05-script.md episodes/E0XX-slug/03-source-log.csv

Writes a markdown report to stdout. No judgement — pure consistency:
  1. Every [S..] tag in the script resolves to a source-log row.
  2. Every source-log row has a tier (A/B/C/D) and a rights_status.
  3. Orphan-claim heuristic: sentences with a number / date / proper noun / quote
     marks but NO [S..] tag are flagged for a human to check.
  4. Tier check: claims whose only [S..] points to Tier C/D.
  5. Counts.

Exit code 0 = PASS, 1 = FAIL (unresolved tag or tier errors).
"""
import csv
import io
import re
import sys
from pathlib import Path

# force UTF-8 stdout on Windows consoles
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TAG_RE = re.compile(r"\[S(\d{1,3}[a-z]?)\]")
# lines that are structural, not narration
SKIP_PREFIXES = ("#", "|", ">", "```", "[EN PANTALLA]", "[NOTA]", "[EXPLICADOR]",
                 "[PLANT]", "[PAY]", "[NARRACIÓN]", "---", "[S", "- [ ]", "- [x]",
                 "‹", "**")
SKIP_AFTER_HEADING = ("autorrevisión", "índice de tags", "foreshadowing", "interludios explicadores")
NUMBERISH = re.compile(r"\d")
MONTHS = r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
DATE_RE = re.compile(MONTHS + r"|\b1[0-9]{3}\b|\b20[0-9]{2}\b", re.I)
# crude proper-noun heuristic: a capitalised word that is not at sentence start
PROPER_RE = re.compile(r"(?<=[a-záéíóúñ,;:]\s)[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}")
QUOTE_RE = re.compile(r"[«»\"“”]")


def load_sources(csv_path):
    rows = {}
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            sid = (r.get("id") or "").strip()
            if not sid:
                continue
            key = sid[1:] if sid.upper().startswith("S") else sid
            rows[key.lower()] = r
    return rows


def read_narration(md_path):
    """Yield (lineno, text) for narration-ish lines only."""
    in_skip_section = False
    for i, raw in enumerate(Path(md_path).read_text(encoding="utf-8").splitlines(), 1):
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            in_skip_section = any(k in s.lower() for k in SKIP_AFTER_HEADING)
            continue
        if in_skip_section:
            continue
        if s.startswith(SKIP_PREFIXES):
            continue
        yield i, s


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    script_path, csv_path = sys.argv[1], sys.argv[2]

    sources = load_sources(csv_path)
    all_text = Path(script_path).read_text(encoding="utf-8")

    used_tags = [m.group(1).lower() for m in TAG_RE.finditer(all_text)]
    used_unique = sorted(set(used_tags), key=lambda x: (len(x), x))

    errors, warnings = [], []

    # 1. tags resolve
    unresolved = [t for t in used_unique if t not in sources]
    for t in unresolved:
        errors.append(f"`[S{t}]` used in script but not in source-log")

    # 2. source rows well-formed
    for key, r in sources.items():
        tier = (r.get("tier") or "").strip().upper()
        rights = (r.get("rights_status") or "").strip()
        if tier not in {"A", "B", "C", "D"}:
            errors.append(f"source S{key}: tier is '{tier}' (must be A/B/C/D)")
        if not rights:
            errors.append(f"source S{key}: rights_status is empty")

    # 4. tier check per claim-tag
    cd_only = []
    for t in used_unique:
        r = sources.get(t)
        if r and (r.get("tier") or "").strip().upper() in {"C", "D"}:
            cd_only.append(t)
    for t in cd_only:
        errors.append(f"`[S{t}]` is Tier {sources[t]['tier'].upper()} — a claim cannot "
                      f"rest only on this; upgrade or reframe as disputed on screen")

    # unused sources (warn only)
    unused = [k for k in sources if k not in set(used_unique)]
    for k in sorted(unused, key=lambda x: (len(x), x)):
        warnings.append(f"source S{k} defined but never cited in the script")

    # 3. orphan-claim heuristic
    orphans = []
    for lineno, text in read_narration(script_path):
        if TAG_RE.search(text):
            continue
        looks_factual = (
            bool(DATE_RE.search(text))
            or bool(QUOTE_RE.search(text))
            or (NUMBERISH.search(text) and len(text) > 40)
            or len(PROPER_RE.findall(text)) >= 2
        )
        if looks_factual:
            snippet = text if len(text) <= 140 else text[:137] + "…"
            orphans.append((lineno, snippet))

    # report
    out = []
    out.append("# Fact-check — Layer 1 (deterministic)\n")
    out.append(f"- Script: `{script_path}`")
    out.append(f"- Source-log: `{csv_path}`")
    out.append(f"- Tags used: {len(used_tags)} ({len(used_unique)} unique)")
    tiers = {}
    for r in sources.values():
        tiers[(r.get('tier') or '?').strip().upper()] = tiers.get((r.get('tier') or '?').strip().upper(), 0) + 1
    out.append(f"- Sources: {len(sources)} — " + ", ".join(f"{k}:{v}" for k, v in sorted(tiers.items())))
    out.append(f"- Orphan-claim candidates: {len(orphans)}")
    out.append("")

    if errors:
        out.append("## ERRORS (must fix — Layer 1 FAILS)\n")
        for e in errors:
            out.append(f"- {e}")
        out.append("")
    if orphans:
        out.append("## Orphan-claim candidates (human: tag or confirm non-factual)\n")
        for ln, sn in orphans:
            out.append(f"- L{ln}: {sn}")
        out.append("")
    if warnings:
        out.append("## Warnings\n")
        for w in warnings:
            out.append(f"- {w}")
        out.append("")

    verdict = "FAIL" if errors else "PASS"
    out.append(f"## Verdict: **{verdict}**")
    if verdict == "PASS" and orphans:
        out.append("\n(PASS on consistency, but the orphan candidates above still need a human pass.)")

    print("\n".join(out))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
