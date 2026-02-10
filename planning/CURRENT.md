# Current State

**Last updated:** 2026-02-10 (post-Directive 012)
**Tests:** 292 passing + 2 skipped (was 262, +24 prompt assembly + 6 observation)
**Last directive:** 012 — Prompt Assembly Refinement

## System Status

| System | Status | Tests |
|---|---|---|
| Sensory | Implemented (~390 LOC) | 23 (test_systems) + contributions to test_graph, test_round_trip |
| Immune | Implemented (210 LOC) | 18 (test_systems) + contributions to test_graph |
| Subconscious | Implemented (186 LOC) | 17 (test_systems) + contributions to test_graph |
| Conscious | Foundation (~440 LOC + ~100 LOC deliberator + ~380 LOC prompt assembly) | 7 (test_systems) + 30 (test_conscious) + 1 (test_graph) + 24 (test_prompt_assembly) |
| Motor | Implemented (~620 LOC) | 7 (test_systems) + 58 (test_motor) + 44 (test_round_trip) |
| Sleep | Stub (pass-through, has WRITE_TOKEN) | 7 (parametrized interface only) |
| Genetic | Stub (pass-through) | 7 (parametrized interface only) |

## Test Files

| File | Tests | Scope |
|---|---|---|
| test_systems.py | 94 | Parametrized interface tests (all 7 systems) + system-specific tests |
| test_conscious.py | 30+2 | Gate logic (9), output structure (3), protocol (3), integration (8), graph (1), observations (6), API (2 skipped) |
| test_prompt_assembly.py | 24 | Intensity (4), individual instructions (4), interactions (6), resting stance (5), full assembly (3), regression (2) |
| test_motor.py | 58 | Motor unit tests (strategies, determinism, field sensitivity, repair) |
| test_round_trip.py | 44 | Motor-sensory feedback loop, calibration sweep, multi-input surface |
| test_graph.py | 18 | LangGraph compilation, routing, signal-domain flow |
| test_topology.py | 24 | Connection matrix verification |

## Changes in Directive 012

### Prompt assembly extraction (Part A)
Created `prompt_assembly.py` — the conscious layer's "what the LLM sees." Moved `LIMB_INSTRUCTIONS` and prompt construction out of `deliberator_anthropic.py`. Any Deliberator can import and use or override.

### Graduated intensity
`compute_intensity(weight)` → (descriptor, intensity). Four levels: slightly (< 0.3), moderately (0.3–0.6), strongly (0.6–0.85), intensely (≥ 0.85). Descriptors prepended to instruction text.

### Limb interactions
Six compound instructions for emergent limb pairs. `replaces_individual` flag controls whether compound replaces or adds to individual instructions. Multiple interactions can fire simultaneously.

### Graduated resting stance
Five levels: below threshold (no instruction), slightly elevated, elevated, high, very high. Replaces binary > 0.6 from Directive 011.

### Observation harness
Six deterministic observation tests recording structural prompt differences. One API-optional observation test (skipped without credentials). Recording infrastructure for semantic-domain audit (Directive 016).

## New Files Created

| File | Purpose |
|---|---|
| `src/agenetic/systems/prompt_assembly.py` | Extracted/extended prompt logic (LIMB_INSTRUCTIONS, LIMB_INTERACTIONS, intensity, assembly) |
| `tests/test_prompt_assembly.py` | 24 deterministic prompt structure tests |
| `planning/012_prompt_assembly.md` | Planning entry (copy of state.md) |

## Prompt Assembly Architecture

### LIMB_INSTRUCTIONS (13 entries, unchanged from D011)
Limbs 1–11, 13, 16. Each with name, high instruction, low instruction.

### LIMB_INTERACTIONS (6 entries)
| Pair | Condition | Replaces? |
|---|---|---|
| Tarka + Śraddhā | both_high | No |
| Nivṛtti + Samatvam | both_high | Yes |
| Prakāśa + Kṣetra-Jñāna | both_high | Yes |
| Vishvarūpa + Māyāvāda | both_high | Yes |
| Tarka + Samatvam | high_low | No |
| Ārēka + Nivṛtti | both_high | Yes |

### Assembly pipeline
`build_limb_instructions(active_limbs)` → check interactions → generate graduated individuals → return interactions + individuals. `assemble_system_prompt()` → role + behavioral orientation + resting stance + state awareness + output format.

## Orientational Field

All 18 Asparśa limbs at 0.5 midpoint. Per-feature reference formulas unchanged from D010:

| Feature | Formula | At 0.5 |
|---|---|---|
| density | `0.8 + (mean_w - 0.5) * 0.4` | 0.8 |
| entropy | `3.5 + (tarka_w - 0.5) * 3.0` | 3.5 |
| coherence | `0.35 + (samatvam_w - 0.5) * 0.7` | 0.35 |
| periodicity | `(0.5 - prakasa_w) * 0.6` | 0.0 |
| noise_floor | `(0.5 - sraddha_w) * 0.6` | 0.0 |
| impedance | `(0.5 - nivrtti_w) * 0.6` | 0.0 |

## Infrastructure

- Orientational field: 18 Asparsa limbs at 0.5 midpoint, read by all systems, write restricted to SleepSystem.WRITE_TOKEN
- LangGraph routing: sensory -> immune -> subconscious -> conditional (escalate -> conscious -> motor, else -> motor)
- Round-trip calibration: motor -> sensory feedback loop, multi-input surface (5 inputs x 18 limbs x 2 weights = 180 points)
- Connection matrix: 17 primary (weight 1.0) + 6 secondary (weight 0.5), 3 absent connections enforced
- Shared target profile in base.py (sensory + motor import same function)
- Deliberator protocol: structural typing, swappable backends (Mock, Anthropic API)
- Prompt assembly: extracted module, graduated intensity, limb interactions, observation harness

## Active Blockers

- None

## Next Directive Candidates

- **013 — Motor codec refactor** — Pure restructuring. Extract text strategies into TextCodec. Zero behavior change.
- **014 — Integration** — Motor renders from ConsciousOutput. Subconscious output consumed by conscious. End-to-end escalated path.
- **015 — Mechanical audit** — DNAgent reads everything, reports raw. Zero code changes.
- **016 — Conceptual audit** — Fresh planning instance, adversarial posture. Key question: prompt assembly theater or genuine expression?
