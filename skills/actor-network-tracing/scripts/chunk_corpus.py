#!/usr/bin/env python3
"""Chunk a registered corpus into passages with stable IDs.

Usage: chunk_corpus.py <corpus_dir> <out_passages.jsonl>

Reads corpus.yaml in <corpus_dir> (simple YAML subset: a list of docs,
each with id, path, genre, title, date, source). Splits each document
into passages by genre:
  - transcript:      grouped speaker turns (lines starting "NAME:")
  - fieldnotes:      episode blocks split on "## " headers
  - everything else: paragraph blocks
Passage IDs are "docID:p<start>-p<end>" using 1-based paragraph indices
within the whole document's passage list. Emits JSONL: {id, doc, genre,
n, text}.
"""
import json
import re
import sys
from pathlib import Path


def parse_manifest(text):
    docs, cur = [], None
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("- "):
            cur = {}
            docs.append(cur)
            line = line[2:]
        if cur is None or ":" not in line:
            continue
        key, _, val = line.strip().partition(":")
        cur[key.strip()] = val.strip().strip('"').strip("'")
    return [d for d in docs if d.get("id") and d.get("path")]


def blocks_paragraph(text):
    return [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]


def blocks_fieldnotes(text):
    parts = re.split(r"(?m)^(## .+)$", text)
    out, pending = [], None
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.startswith("## "):
            pending = part
        elif pending:
            out.append(pending + "\n" + part)
            pending = None
        else:
            out.append(part)
    if pending:
        out.append(pending)
    return out


def blocks_transcript(text):
    paras = blocks_paragraph(text)
    out, cur = [], None
    turn = re.compile(r"^[A-Z][A-Za-z .]{0,30}:")
    for para in paras:
        if turn.match(para):
            if cur:
                out.append(cur)
            cur = para
        else:
            cur = (cur + "\n" + para) if cur else para
    if cur:
        out.append(cur)
    return out


SPLITTERS = {"fieldnotes": blocks_fieldnotes, "transcript": blocks_transcript}


def main():
    corpus_dir, out_path = Path(sys.argv[1]), Path(sys.argv[2])
    docs = parse_manifest((corpus_dir / "corpus.yaml").read_text())
    rows = []
    for doc in docs:
        text = (corpus_dir / doc["path"]).read_text()
        splitter = SPLITTERS.get(doc.get("genre", ""), blocks_paragraph)
        passages = splitter(text)
        for i, passage in enumerate(passages, start=1):
            rows.append({
                "id": f'{doc["id"]}:p{i}',
                "doc": doc["id"],
                "genre": doc.get("genre", ""),
                "n": i,
                "text": passage,
            })
    with out_path.open("w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    print(f"{len(rows)} passages from {len(docs)} documents -> {out_path}")


if __name__ == "__main__":
    main()
