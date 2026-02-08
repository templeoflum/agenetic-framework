# Agenetic Framework

A biologically-inspired agent architecture where seven distinct information-processing systems operate as a weighted network, suspended in an orientational field derived from Asparśa Yoga.

**"Agenetic"** — literally *without origin* — arrived as a persistent typo of "agentic" and stayed because it's structurally honest. The framework doesn't claim to originate intelligence. It describes conditions under which intelligence unfolds. The seed isn't the source. Echo, not origin.

## What This Is

DNA doesn't contain an organism. It contains instructions for a process that unfolds in dialogue with environment. It is not a blueprint — it is a generative grammar.

This framework applies that insight to agent architecture. Rather than a monolithic prompt or a sequential pipeline, it models seven subsystems with fundamentally different relationships to information, operating at different timescales, communicating through weighted connections. The result is an agent that can process most inputs cheaply in the signal domain and only invoke expensive semantic interpretation when the input actually warrants it.

## The Seven Systems

| System | Relationship | Domain | Tick Rate |
|--------|-------------|--------|-----------|
| **Sensory** | Transduces — characterizes input as signal | Signal | Every cycle |
| **Immune** | Discriminates — detects signal anomalies | Signal | Every cycle |
| **Subconscious** | Associates — correlates signal patterns | Signal | Every cycle |
| **Conscious** | Deliberates — constructs meaning | Semantic | On escalation |
| **Motor** | Expresses — encodes output for medium | Meta | On demand |
| **Sleep** | Consolidates — optimizes transfer functions | Meta | Periodic |
| **Genetic** | Generates — the minimal seed | Meta | Read-only |

### The Signal-Semantics Boundary

The first three systems operate entirely in the **signal domain** — they extract structural features (density, entropy, coherence, periodicity, noise floor, impedance), detect anomalous patterns, and correlate against prior experience. No LLM calls. No semantic interpretation. Pure Python computation.

The **conscious** layer is the first and only system that interprets. It fires only on escalation — when the signal-domain systems determine that the input requires meaning-making. This is not a performance optimization. It is the architectural reason the system works.

### The Orientational Field

The orientational field is not a system. It is the medium in which all seven systems operate — a self-model derived from the eighteen limbs of Asparśa Yoga. It provides the reference signal against which sensory measures deviation, the identity against which immune discriminates self from not-self, and the orientation that shapes which associations surface.

The field's limb weights are transfer function coefficients. Sleep modifies them. Genetic provides the factory calibration.

## Current Status

**Phase 1 — Minimal Viable Cell** (in progress)

The signal-domain tier and motor layer are implemented and operational:

- Seven system interfaces defined with typed state passing
- Sensory system extracts six signal features from input, classifies signal type, computes delta from orientational field reference
- Immune system performs innate threshold detection and adaptive pattern matching on signal reports
- Subconscious system correlates signal patterns against cache, makes escalation decisions
- Motor system restructures text toward target signal profiles shaped by orientational field limb weights (six strategies: density, entropy, coherence, impedance, periodicity, noise floor)
- Round-trip calibration infrastructure: motor output → sensory → measure feature deltas, with parameterized limb weight variation for testing limb-to-feature mapping hypotheses
- Weighted connection matrix defines all system-to-system communication paths
- LangGraph orchestration with conditional routing (escalation → conscious, else → motor reflex)
- Orientational field with all 18 Asparśa limbs, sleep-only write access enforced
- 195 tests passing

Conscious, sleep, and genetic remain stubs awaiting implementation.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full v2 specification.

See [`docs/architecture_amendment.md`](docs/architecture_amendment.md) for the signal-semantics boundary insight.

See [`docs/signal_report_structure.md`](docs/signal_report_structure.md) for the signal report interface definition.

## Project Structure

```
agenetic-framework/
├── DEVLOG.md                        # What was built and why (repo memory)
├── PLANNING_LOG.md                  # Decisions, rationale, open threads (chat memory)
├── docs/
│   ├── ARCHITECTURE.md              # Full v2 framework specification
│   ├── DIRECTIVES.md                # How the directive system works
│   ├── architecture_amendment.md    # Signal-semantics boundary
│   └── signal_report_structure.md   # Signal report TypedDict spec
├── handoff/                         # Directive/response exchange files
├── references/                      # Background material
├── src/agenetic/
│   ├── systems/                     # The seven systems
│   ├── network/                     # Topology, connections, routing
│   ├── field/                       # Orientational field
│   └── regulation/                  # Homeostasis, repair, apoptosis
└── tests/
```

## How Development Works

This project uses a directive-based collaboration between two Claude instances:

- **Planning instance** (claude.ai): Makes architecture decisions, reviews work, writes directives
- **DNAgent** (Claude Code CLI): Reads genetic instructions (directives) and assembles functional output (code, tests, reports)

All coordination happens through files in `handoff/`. Every directive is a cold start — DNAgent has no memory of previous conversations. Everything it needs is in the directive file plus the repo contents.

## Tech Stack

- Python 3.11+
- LangGraph for orchestration
- Anthropic API for LLM calls (conscious layer, not yet implemented)
- pytest (195 tests)

## License

Not yet specified.
