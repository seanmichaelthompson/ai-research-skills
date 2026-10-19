---
name: actor-network-tracing
description: "Use when a researcher wants a Latourian actor-network account of a defined corpus (mixed literature, interview transcripts/notes, ethnographic fieldnotes): identify actants by the difference they make, extract associations only from verifiable inscriptions, classify translations and mediators, map controversies, and assemble an account under a closed-world rule. Not for thematic coding (use a thematic analysis skill) and not for corpora the researcher cannot define and bound."
---

# Actor-Network Tracing

Build an actor-network account of a **defined corpus** by following the
actors — human and nonhuman — through the inscriptions they leave in the
material. The method is Latour's, operationalized: no actant without a
difference it makes, no association without a citable inscription, no
explanation by appeal to aggregates ("power", "culture", "the market")
that the corpus itself does not trace.

This skill prepares and proposes; the researcher ratifies. There are three
human gates (corpus review, census review, and the cut declaration) that must not be skipped.

## Inputs

- The researcher's questions, stated up front.
- Either an existing corpus (a folder with a `corpus.yaml` manifest —
  every document registered: `id`, `path`, `genre` (literature |
  transcript | interview-notes | fieldnotes), `title`, `date`,
  `source`) or a source plan naming where the material lives (local
  files, a repository, a forum, an archive). If no corpus exists yet,
  Pass 0 constructs it; unregistered material does not exist for this
  skill either way.
- A working directory for state (created if absent): `state/`.

If the questions are missing, ask. Do not invent a frame.

## State files (the skill's memory)

- `state/sources.jsonl` — the provenance register: one line per
  acquired source: `id`, `origin` (path or URL), `acquired` (date),
  `basis` (public | consented | orientation-only), `genre`. Written
  in Pass 0; nothing enters the corpus without a line here.
- `state/passages.jsonl` — chunked passages with stable IDs
  (`docID:pStart-pEnd`), produced by `scripts/chunk_corpus.py`.
  Chunking is genre-aware: transcripts at speaker turns, fieldnotes at
  episode boundaries (a scene is never split), literature at paragraphs.
- `state/actants.jsonl` — one line per actant: `id`, `label`, `aliases`,
  `difference_passages` (passage IDs where it makes a difference),
  `composition` (optional: sub-actants, if it is a black box).
- `state/associations.jsonl` — one line per claimed association:
  `source`, `target`, `relation_quote` (verbatim, from one passage),
  `passage` (its ID), `moment` (problematization | interessement |
  enrolment | mobilization | unclassified), `mediation`
  (mediator | intermediary | untested), `inscriptions` (count of
  independent passages supporting this edge).
- `state/cut.md` — the researcher's cut declaration and what lies
  beyond it.

## Procedure

### Pass 0 — Construct the corpus

A corpus is made, not found. If the researcher brings one, verify it
against the steps below; if not, build it with them.

1. **Boundary first.** State the questions; declare the corpus
   boundary — period, sources, genres — and record it in
   `state/cut.md` before any acquisition. The boundary is the first
   cut: name what lies beyond it and which claims the exclusion
   forbids, the same discipline Gate 2 applies at the end.
2. **Source plan.** Inventory where the material lives. Assign each
   source a genre *before* reading its content: provenance before
   content, always. A plan template ships with the skill
   (`templates/corpus-plan.md`).
3. **Acquire.** Collect the material into the corpus folder, one file
   per document, originals unmodified. Patterns: local files are
   taken as-is; platform exports keep their thread structure (a
   thread is a document, its comments become passages when chunked);
   web material is captured as text with its URL and capture date.
   Register every acquisition in `state/sources.jsonl` with its
   origin, date, genre, and basis.
4. **Basis check (hard stop).** Every source carries a basis:
   *public* (published to the world — usable and citable),
   *consented* (private material the researcher has a recorded basis
   to use), or *orientation-only* (member-space material — closed
   channels, internal lists: it may inform the researcher's judgment
   but is never registered, chunked, or quoted). A source whose basis
   is unclear is excluded and the exclusion is logged. De-identify at
   intake where the design requires it.
5. **Assemble and chunk.** Write `corpus.yaml` from the register
   (each manifest `source` matches a `sources.jsonl` line), then run
   `scripts/chunk_corpus.py`. A document that yields zero passages is
   a failed intake, not an empty source — fix or exclude it, and log
   which. Prefer genre coverage and inscription density over volume;
   if the corpus is too large to census honestly, narrow the boundary
   rather than sampling silently. Any sampling is declared in
   `state/cut.md` with its rule and rationale.

**Gate 0 — Corpus review.** Present the register, the boundary
statement, and the exclusion log. The researcher ratifies the corpus
before chunking. Material they strike is removed from the folder, not
merely ignored.

### Pass 1 — Actant census
Scan passages in windows. Nominate an actant only with a
**difference-passage**: a passage where its presence, absence, or
alteration changes another actant's action. Frequency of mention is
not difference; a much-discussed object that changes nothing is not an
actant, however thematic it feels. Resolve aliases aggressively — one
actant, many names ("the Hill", "North Slope", "up there") is one
registry entry with aliases listed; a fragmented graph is a failed run.
Humans and nonhumans are nominated by the same test.

**Gate 1 — Census review.** Present the registry: each actant, its
difference-passage, its alias list. The researcher may merge, split,
rename, or strike. Do not proceed on an unreviewed census.

### Pass 2 — Association extraction
Window by window, extract relational statements among registered
actants. Each association requires a verbatim `relation_quote` from a
single passage and that passage's ID. When a statement implicates
something unregistered, loop back to Pass 1 rather than extending the
graph informally. Retrieval of further material on an actant is by its
traces — names, aliases, citations — never by topical similarity.

### Pass 3 — Verification (script, not judgment)
Run `scripts/verify_citations.py`. It substring-matches every
`relation_quote` against its cited passage and checks every actant has
at least one valid difference-passage. Failures are rejected, not
repaired. A run with rejected inscriptions is reported with them named.

### Pass 4 — Classification
For each association (or stable cluster), classify:
- **Translation moment** (Callon): enrolment requires an inscription
  of changed behavior, not assent; a proposal that was never taken up is
  interessement, however warm the language around it.
- **Mediation**: mediator if an inscription shows output differing from
  input (transformation, delay, filtering, aggregation); intermediary
  only if transport without transformation is what the inscriptions
  show; otherwise untested. Do not award mediator status for narrative
  importance.

### Pass 5 — Black boxes and passage points
Mark punctualizations: actants the corpus once showed being assembled
and later treats as a single voice. Record their `composition`. Run
`scripts/graph_metrics.py` for degree, betweenness, inscription counts,
and genre coverage per edge. High-betweenness actants are *nominated*
obligatory passage points; the researcher confirms or rejects each
nomination at Gate 2.

### Pass 6 — Controversy map
Where actants' inscriptions make incompatible claims about the same
relation or event, record a controversy: each position, its holders,
its inscriptions. Controversies are reported unresolved. A position
resting on a single inscription is flagged as such.

### Gate 2 — The cut
Relations extend indefinitely; the account must stop somewhere, and
where it stops is the researcher's declared choice, not the corpus
running out. The researcher declares which actants/threads will not be
followed. Record in `state/cut.md`: the cut, its rationale, and a
"beyond the cut" note stating what was excluded and which kinds of
claims the exclusion forbids.

### Pass 7 — Account assembly (closed world)
Write the account tracing the network for the researcher's questions.
Rules, verified by `scripts/verify_citations.py --account`:
- Only registered actants may be named.
- Only registered associations may be claimed.
- Every claimed association cites its passage(s).
- No aggregate explanations: if "the organization" or "users" appears
  as an explainer, it must be a registered actant with inscriptions, or
  the sentence comes out.

## Guardrails

- Unregistered material does not exist: no source, no passage; no
  passage, no claim. Orientation-only material never crosses into the
  corpus, however relevant it feels.
- Verbatim or nothing: quotes are never paraphrased, cleaned, or
  completed. Notes-genre material is flagged as recall; its quotes
  support substance, not wording.
- Genre is never erased: an edge resting only on interviews is
  reported differently from one also inscribed in fieldnotes or
  literature, and `graph_metrics.py` prints the coverage so the
  researcher sees it.
- Absence is data to report, not to fill: an actant everyone discusses
  but no inscription shows acting is reported as exactly that.
- The skill does not resolve controversies, average positions, or
  promote a position because it is the researcher's favorite.
- Interpretive leaps beyond the inscriptions are labeled as the
  researcher's (recorded in memos), never laundered into findings.

## Outputs

1. `state/sources.jsonl` (provenance register), `state/actants.jsonl`,
   and `state/associations.jsonl` (reviewed).
2. A controversy map (positions × inscriptions).
3. `state/cut.md` (boundary + cut + beyond-the-cut note).
4. The account: a trace narrative in which every claim is one hop
   from a verified inscription.

## Scripts

- `scripts/chunk_corpus.py <corpus_dir> <out_passages.jsonl>`
- `scripts/verify_citations.py <state_dir> [--account account.md]`
- `scripts/graph_metrics.py <state_dir>`
