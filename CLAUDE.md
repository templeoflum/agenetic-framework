# Agenetic Framework

## What This Is

A biologically-inspired agent architecture where seven distinct information-processing systems operate as a weighted network, suspended in an orientational field derived from Asparśa Yoga principles. DNA is the structural inspiration — not as metaphor, but as engineering precedent for managing complexity, adaptation, and self-regulation.

"Agenetic" means "without origin." The framework doesn't claim to originate intelligence. It describes conditions under which intelligence unfolds.

## How This Repo Works

This project uses a **directive-based collaboration** between two Claude instances:

- **Planning instance** (claude.ai chat): Makes architecture decisions, reviews work, writes directives
- **Build instance** (Claude Code CLI): Executes directives, writes code, runs tests, reports back

### The Handoff Protocol

All coordination happens through files in `handoff/`:

- `NNN_directive.md` — Instructions from planning instance to build instance
- `NNN_response.md` — Build instance's completion report

**Every directive is a cold start.** The build instance has no memory of previous conversations. Everything it needs to execute is in the directive file itself plus the repo contents.

### Workflow

1. Planning instance writes the next directive (packaged with repo or provided by human)
2. Human tells build instance to read and execute the directive
3. Build instance executes, writes `handoff/NNN_response.md`, commits, and pushes to GitHub
4. Human tells planning instance the directive is complete
5. Planning instance reads the response and changed files directly from GitHub
6. Planning instance writes next directive based on results

### Key Rules for the Build Instance

- **Read the directive fully before acting.** Don't start executing partway through.
- **Stay within scope boundaries.** Every directive has DO and DO NOT lists. Respect them.
- **Don't modify historical handoff files.** Previous directives and responses are the project's memory.
- **Report honestly.** If something didn't work, say so in the response. Don't paper over failures.
- **Commit after completing each directive.** One directive = one coherent commit (or a small series if the work is large).

## Architecture Overview

See `docs/ARCHITECTURE.md` for the full v2 specification. The short version:

Seven systems in a weighted network:
1. **Sensory** — transduction (format conversion without interpretation)
2. **Immune** — discrimination (self/not-self, innate + adaptive)
3. **Subconscious** — association (pattern matching, relevance priming)
4. **Conscious** — deliberation (explicit reasoning, the expensive bottleneck)
5. **Motor/Output** — expression (translating internal states to external form)
6. **Sleep** — consolidation (pruning, strengthening, epigenetic feedback)
7. **Genetic** — generation (the minimal seed, read by all, written only by sleep)

Plus cross-cutting concerns: inline repair, homeostatic regulation, apoptotic exit conditions.

The orientational field (Asparśa Yoga principles) pervades all systems as a shared self-model.

## Tech Stack

- **Python 3.11+**
- **LangGraph** for orchestration (graph-based agent framework)
- **Anthropic API** for LLM calls
- Tests via **pytest**

## Project Structure

```
agenetic-framework/
├── CLAUDE.md              ← You are here
├── README.md              ← Public-facing project description
├── docs/
│   ├── ARCHITECTURE.md    ← Full v2 framework specification
│   └── DIRECTIVES.md      ← How the directive system works
├── handoff/               ← Directive/response exchange files
│   ├── 001_directive.md
│   └── 001_response.md
├── references/            ← Background material, Asparśa spec, etc.
├── src/                   ← Source code
│   └── agenetic/
│       ├── __init__.py
│       ├── systems/       ← The seven systems
│       ├── network/       ← Topology, connections, routing
│       ├── field/         ← Orientational field implementation
│       └── regulation/    ← Homeostasis, repair, apoptosis
└── tests/
```
