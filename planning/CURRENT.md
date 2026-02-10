# Current State

**Last updated:** 2026-02-09 (post-Directive 011)
**Tests:** 262 passing + 1 skipped (was 238, +24 conscious tests)
**Last directive:** 011 — Conscious Layer Foundation

## System Status

| System | Status | Tests |
|---|---|---|
| Sensory | Implemented (~390 LOC) | 23 (test_systems) + contributions to test_graph, test_round_trip |
| Immune | Implemented (210 LOC) | 18 (test_systems) + contributions to test_graph |
| Subconscious | Implemented (186 LOC) | 17 (test_systems) + contributions to test_graph |
| Conscious | Foundation (~440 LOC + 360 LOC deliberators) | 7 (test_systems) + 24 (test_conscious) + 1 (test_graph) |
| Motor | Implemented (~620 LOC) | 7 (test_systems) + 58 (test_motor) + 44 (test_round_trip) |
| Sleep | Stub (pass-through, has WRITE_TOKEN) | 7 (parametrized interface only) |
| Genetic | Stub (pass-through) | 7 (parametrized interface only) |

## Test Files

| File | Tests | Scope |
|---|---|---|
| test_systems.py | 94 | Parametrized interface tests (all 7 systems) + system-specific tests |
| test_conscious.py | 24+1 | Gate logic (9), output structure (3), protocol (3), integration (8), graph (1), API (1 skipped) |
| test_motor.py | 58 | Motor unit tests (strategies, determinism, field sensitivity, repair) |
| test_round_trip.py | 44 | Motor-sensory feedback loop, calibration sweep, multi-input surface |
| test_graph.py | 18 | LangGraph compilation, routing, signal-domain flow |
| test_topology.py | 24 | Connection matrix verification |

## Changes in Directive 011

### ConsciousOutput contract (Part A)
New TypedDicts in base.py: `ResponseDecision`, `ExpressionDirectives`, `Lineage`, `ConsciousOutput`. Added `conscious_output` to `SystemState` and `GraphState`. Extended limb ID constants from 9 to all 18 + `CONVERGENT_CLUSTER_IDS` list.

### Proceed/suppress gate (Part B)
Pure Python, no LLM. Priority: immune override → Ārēka suppression (noise) → Nivṛtti pause (low deviation) → resting stance (deep rest + minimal stimulus) → default proceed. Gate produces full evaluation dict. Suppression yields complete ConsciousOutput with proceed=False.

### Deliberator protocol (Part C)
`Deliberator` — runtime_checkable Protocol (structural typing). `DeliberationRequest` — structured input. `MockDeliberator` — deterministic, test-friendly. `AnthropicDeliberator` — first real LLM implementation (claude-sonnet-4-20250514), prompt-side limb expression, JSON parsing with fallback.

### Conscious system integration (Part D)
`ConsciousSystem.__init__` accepts optional Deliberator. Three code paths: missing signal report (degrade), gate suppresses (no LLM), gate proceeds (call deliberator or degrade if none). Repair checks lineage completeness and confidence. Apoptotic after 3 low-confidence streak.

### Convergent cluster
Five limbs (Bodhi 12, Rest-as-Realization 14, Mirror 15, Ajāti 17, Asparśa-Yoga 18) treated as composite resting stance: mean of weights. High = recede, Low = project. Testable hypothesis — decompose if conscious produces distinguishable behavior for individual members.

### Expression directives
Active limbs: weight outside 0.4–0.6. No-Position (13) > 0.6 = suppress_identity. Fourfold State (16): >0.7 reflective, <0.3 still, <0.4 consolidated, else active. Field weights snapshot for all 18 limbs.

## New Files Created

| File | Purpose |
|---|---|
| `src/agenetic/systems/deliberator.py` | Deliberator Protocol, DeliberationRequest, MockDeliberator |
| `src/agenetic/systems/deliberator_anthropic.py` | AnthropicDeliberator (first real LLM backend) |
| `tests/test_conscious.py` | All conscious system tests (gate, structure, protocol, integration) |
| `planning/011_conscious_foundation.md` | Planning entry (copy of state.md) |

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

## Active Blockers

- None

## Next Directive Candidates

- **012 — Prompt assembly refinement** — Semantic limb expression. Field state → behavioral framing for LLM. Most conceptually dense step.
- **013 — Motor codec refactor** — Pure restructuring. Extract text strategies into TextCodec. Zero behavior change.
- **014 — Integration** — Motor renders from ConsciousOutput. Subconscious output consumed by conscious. End-to-end escalated path.
