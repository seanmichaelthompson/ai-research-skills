#!/usr/bin/env python3
"""Graph metrics for an actor-network-tracing run (stdlib only).

Usage: graph_metrics.py <state_dir>

Reads state/actants.jsonl, state/associations.jsonl and
state/passages.jsonl. Prints: degree and betweenness (Brandes) per
actant, nominations for obligatory passage points, per-edge inscription
counts and genre coverage, and orphan actants.
"""
import json
import sys
from collections import defaultdict, deque
from pathlib import Path


def load_jsonl(path):
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def betweenness(nodes, edges):
    adj = defaultdict(set)
    for s, t in edges:
        adj[s].add(t)
        adj[t].add(s)
    cb = dict.fromkeys(nodes, 0.0)
    for s in nodes:
        stack, pred = [], {w: [] for w in nodes}
        sigma = dict.fromkeys(nodes, 0.0)
        sigma[s] = 1.0
        dist = dict.fromkeys(nodes, -1)
        dist[s] = 0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in adj[v]:
                if dist[w] < 0:
                    queue.append(w)
                    dist[w] = dist[v] + 1
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = dict.fromkeys(nodes, 0.0)
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]
    # undirected graphs count each unordered pair twice
    cb = {k: v / 2.0 for k, v in cb.items()}
    n = len(nodes)
    norm = (n - 1) * (n - 2) / 2 if n > 2 else 1
    return {k: round(v / norm, 3) for k, v in cb.items()}


def main():
    state = Path(sys.argv[1])
    actants = load_jsonl(state / "actants.jsonl")
    assoc = load_jsonl(state / "associations.jsonl")
    passages = {p["id"]: p for p in load_jsonl(state / "passages.jsonl")}

    ids = [a["id"] for a in actants]
    labels = {a["id"]: a.get("label", a["id"]) for a in actants}
    edges = [(e["source"], e["target"]) for e in assoc if e.get("source") and e.get("target")]

    degree = defaultdict(int)
    for s, t in edges:
        degree[s] += 1
        degree[t] += 1
    betw = betweenness(ids, edges) if ids else {}

    print("== Actants by betweenness (OPP nominations first) ==")
    for aid in sorted(ids, key=lambda x: -betw.get(x, 0)):
        print(f"{labels[aid]:<28} degree={degree.get(aid, 0):<3} betweenness={betw.get(aid, 0)}")

    print("\n== Edges: inscriptions and genre coverage ==")
    for e in assoc:
        pid = e.get("passage")
        genre = passages.get(pid, {}).get("genre", "?") if pid else "?"
        print(f"{labels.get(e['source'], e['source'])} -> {labels.get(e['target'], e['target'])}"
              f"  inscriptions={e.get('inscriptions', 1)}  genre={genre}"
              f"  moment={e.get('moment', 'unclassified')}  mediation={e.get('mediation', 'untested')}")

    orphans = [labels[i] for i in ids if degree.get(i, 0) == 0]
    print(f"\nOrphan actants (no associations): {orphans or 'none'}")
    print(f"Totals: {len(ids)} actants, {len(edges)} associations")


if __name__ == "__main__":
    main()
