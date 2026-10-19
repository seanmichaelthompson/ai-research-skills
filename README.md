# UXR AI Skills

A library of AI skills for qualitative user research — methods-level,
evidence-disciplined, and portable across agents that read the `SKILL.md`
format.

## Architecture

Two layers:

- **Analytical skills** (this repo's folders) run over primary material:
  thematic analysis, claim-mapping, episode indexing, actor-network tracing.
- A corpus-level practice sits above them — provenance discipline,
  cross-genre tracing, abductive memo cycles, deviant-case sweeps — that
  orchestrates the skills and produces the interpretive account.

## Catalog

| Skill | What it does | Maturity |
|---|---|---|
| [actor-network-tracing](skills/actor-network-tracing/) | Latourian tracing of a defined corpus: actant census by the difference test, associations extracted only from verifiable inscriptions, translation and mediator classification, controversy mapping, closed-world account assembly | v0.1 prototype |

## Rules of the house

- Methods only — written the way you would teach them to strangers.
- Quotes are verbatim or they do not exist. Every claim traces to a
  citable passage in one hop.
- The researcher owns interpretation. Skills prepare, propose, and
  verify; gates between passes are where judgment enters.
- Bring your own corpus. Skills ship without example data; evaluate
  them on your own material.

## Calling a skill

Install the skill folder where your agent reads skills (for Claude
Code: `~/.claude/skills/`), then either describe the task in plain
language — the agent matches the skill's description and loads it — or
name it explicitly: *"Use the actor-network-tracing skill on this
corpus."* You supply a corpus folder with a `corpus.yaml` manifest and
your research questions; the skill runs its passes and stops at its
gates for your judgment.

A personal project, published for other researchers to use and adapt.
