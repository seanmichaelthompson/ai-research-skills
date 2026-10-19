#!/usr/bin/env python3
"""Verify the inscription discipline of an actor-network-tracing run.

Usage: verify_citations.py <state_dir> [--account <account.md>]

Checks, using state/passages.jsonl, state/actants.jsonl and
state/associations.jsonl:
  1. Every association's relation_quote is a verbatim substring of its
     cited passage (whitespace-normalized).
  2. Every actant has at least one difference_passage that exists.
  3. Association endpoints are registered actants.
With --account: every actant label/alias mentioned in the account must
be registered (closed-world check); unregistered capitalized candidate
names are reported as warnings only.

Exit code 0 = all hard checks pass; 1 = failures (listed).
"""
import json
import re
import sys
from pathlib import Path


def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()


def main():
    state = Path(sys.argv[1])
    account = None
    if "--account" in sys.argv:
        account = Path(sys.argv[sys.argv.index("--account") + 1])

    passages = {p["id"]: p["text"] for p in load_jsonl(state / "passages.jsonl")}
    actants = load_jsonl(state / "actants.jsonl")
    assoc = load_jsonl(state / "associations.jsonl")
    failures, warnings = [], []

    by_id = {a["id"]: a for a in actants}
    for a in actants:
        diffs = a.get("difference_passages") or []
        if not diffs:
            failures.append(f"actant {a['id']}: no difference_passage")
        for pid in diffs:
            if pid not in passages:
                failures.append(f"actant {a['id']}: difference_passage {pid} not found")

    for i, e in enumerate(assoc):
        tag = f"association[{i}] {e.get('source')}->{e.get('target')}"
        for end in ("source", "target"):
            if e.get(end) not in by_id:
                failures.append(f"{tag}: {end} '{e.get(end)}' not a registered actant")
        pid, quote = e.get("passage"), norm(e.get("relation_quote"))
        if pid not in passages:
            failures.append(f"{tag}: passage {pid} not found")
        elif quote and quote not in norm(passages[pid]):
            failures.append(f"{tag}: relation_quote is NOT a verbatim substring of {pid}")
        if not quote:
            failures.append(f"{tag}: missing relation_quote")

    if account and account.exists():
        text = account.read_text()
        known = set()
        for a in actants:
            known.add(a.get("label", ""))
            known.update(a.get("aliases") or [])
        for name in sorted(known):
            if name and name in text:
                pass  # registered and used: fine
        # warn on likely proper names in the account that match no actant
        candidates = set(re.findall(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+){0,2}\b", text))
        known_blob = " | ".join(known)
        for cand in sorted(candidates):
            if cand not in known_blob and len(cand) > 3:
                warnings.append(f"account mentions '{cand}' — not a registered label/alias (check closed world)")

    for f in failures:
        print("FAIL:", f)
    for w in warnings:
        print("WARN:", w)
    print(f"{len(actants)} actants, {len(assoc)} associations; "
          f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
