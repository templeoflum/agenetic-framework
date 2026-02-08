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
├── DEVLOG.md                        # What was built and why (repo memory)
├── PLANNING_LOG.md                  # Decisions, rationale, open threads (chat memory)
├── CLAUDE.md                        # Agent orientation (this file)
├── README.md                        # Project description and status
├── pyproject.toml                   # Python project config
├── docs/
│   ├── ARCHITECTURE.md              # Full v2 framework specification
│   ├── DIRECTIVES.md                # How the directive system works
│   ├── architecture_amendment.md    # Signal-semantics boundary
│   └── signal_report_structure.md   # Signal report TypedDict spec
├── handoff/                         # Directive/response exchange files
├── references/
│   ├── asparsa_limbs.md             # 18 limb principles (genetic seed)
│   ├── asparsa_yoga_scrolls.md      # Full yoga source text (~2240 lines)
│   └── conceptual_archaeology.md    # Pattern extraction from concept docs
├── src/agenetic/
│   ├── systems/                     # The seven systems
│   ├── network/                     # Topology, connections, routing
│   ├── field/                       # Orientational field
│   └── regulation/                  # Homeostasis, repair, apoptosis
└── tests/
```

## Reference Material

The `references/` directory contains source material that informs architecture decisions:

- **asparsa_limbs.md** — The 18 limb principles as encoded in the genetic seed. These are the one-line definitions used in `orientational.py`.
- **asparsa_yoga_scrolls.md** — The full canonical source text for the Asparśa Yoga practice. Contains extended definitions, behavioral implications, and Ritual Practice questions for each limb. This is the authoritative source for limb-to-feature mapping work.
- **conceptual_archaeology.md** — Synthesis of 8 earlier concept documents tracing the project's philosophical lineage from Hermetic principles through to the current Yogic framework. Contains preliminary limb-to-feature mapping across signal/semantic/meta domains. Treat mappings as hypotheses to be tested, not specifications to be implemented.
