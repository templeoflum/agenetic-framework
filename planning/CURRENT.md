# Current State

**Last updated:** 2026-02-11 (post-Directive 018)
**Tests:** 389 passing + 2 skipped
**Last directive:** 018 — Phase Consolidation: Genetic Implementation + Structural Reckoning

## System Status

| System | Status | Tests |
|---|---|---|
| Sensory | Implemented (~390 LOC) | 23 (test_systems) + contributions to test_graph, test_round_trip, test_integration |
| Immune | Implemented (~213 LOC) — sets escalation flag for critical threats | 18 (test_systems) + 3 (test_immune) + contributions to test_graph, test_integration |
| Subconscious | Implemented (~200 LOC) — cache pruning, OR-preserve flags, normalized distance | 17 (test_systems) + 11 (test_subconscious) + contributions to test_graph, test_integration |
| Conscious | Foundation (~435 LOC + ~100 LOC deliberator + ~380 LOC prompt assembly) | 7 (test_systems) + 32 (test_conscious) + 1 (test_graph) + 24 (test_prompt_assembly) + contributions to test_integration |
| Motor | Integrated (~189 LOC orchestrator + ~55 LOC codec.py + ~440 LOC text_codec.py) | 7 (test_systems) + 58 (test_motor) + 44 (test_round_trip) + 14 (test_codec) + contributions to test_integration |
| Sleep | Operational (~239 LOC) — consolidation + weight modification | 7 (test_systems) + 35 (test_sleep) |
| Genetic | Operational (~152 LOC) — expression profile store, drift measurement | 7 (test_systems) + 18 (test_genetic) |

## Phase Completion

| Phase | Status | Closed by |
|---|---|---|
| 1 — Single Cell | **COMPLETE** | D001–D018 |
| 2 — Temporal Stratification | **COMPLETE** | D011–D017 |
| 3 — Network Topology + Self-Regulation | Not started | — |
| 4 — Epigenetic Adaptation | Not started | — |

### Phase 3 Remaining Items
- [ ] Feedback loops: Motor→Conscious, Conscious→Sensory, Conscious→Immune
- [ ] Graph uses topology.py connection weights
- [ ] Homeostatic monitoring subsystem
- [ ] Connection weight modification during sleep (distinct from field weights)
- [ ] System-level and agent-level apoptosis

### Phase 4 Remaining Items
- [ ] Sleep writes to genetic expression profiles
- [ ] Expression profiles modify system behavior in subsequent cycles
- [ ] Field expression adjusts from accumulated experience
- [ ] Multi-cycle integration validation

## Test Files

| File | Tests | Scope |
|---|---|---|
| test_systems.py | 94 | Parametrized interface tests (all 7 systems) + system-specific tests |
| test_motor.py | 58 | Motor unit tests (strategies, determinism, field sensitivity, repair) |
| test_round_trip.py | 44 | Motor-sensory feedback loop, calibration sweep, multi-input surface |
| test_sleep.py | 35 | Tick gating (4), cache pruning (5), immune consolidation (6), weight modification (9), repair/apoptosis (4), state persistence (3), integration (4) |
| test_conscious.py | 30+2 | Gate logic (9), output structure (3), protocol (3), integration (8), graph (1), observations (6), API (2 skipped) |
| test_topology.py | 24 | Connection matrix verification |
| test_prompt_assembly.py | 24 | Intensity (4), individual instructions (4), interactions (6), resting stance (5), full assembly (3), regression (2) |
| test_graph.py | 18 | LangGraph compilation, routing, signal-domain flow |
| test_genetic.py | 18 | Factory defaults (3), expression profile (3), drift (4), repair (3), apoptotic (3), seed integrity (2) |
| test_integration.py | 16 | End-to-end paths: reflex (4), escalated (4), suppression (3), routing (3), cross-path (2) |
| test_codec.py | 14 | Protocol conformance (3), equivalence (4), quality check (2), Mayavada (2), motor delegation (3) |
| test_subconscious.py | 11 | Cache pruning (4), flag OR-preservation (3), feature normalization (4) |
| test_immune.py | 3 | Critical threat escalation flag (1), non-critical no flag (1), immune+subconscious integration (1) |

## D018 Summary

Two-part directive closing Phase 1:

**Part A — Genetic implementation:**
- Added TypedDicts to base.py: ExpressionEntry, ExpressionProfile, GeneticOutput
- Added genetic_output to SystemState, GraphState, create_default_state, _make_node
- Replaced genetic stub with full implementation: factory seed (18 limbs × 0.5), expression profile, drift measurement, apoptotic condition (threshold 3.0)
- 18 new tests in test_genetic.py

**Part B — Phase tracking infrastructure:**
- Created docs/AUDIT_METHODOLOGY.md — phase-first audit methodology
- Updated docs/ARCHITECTURE.md status section — Phase 1+2 complete, Phase 3+4 remaining
- Added Phase Completion section to CURRENT.md

## Three Routing Paths

| Path | Condition | Route | Motor behavior |
|---|---|---|---|
| Reflex | Low deviation, no threat | sensory → immune → subconscious → motor | Processes input directly via codec |
| Escalated | High deviation or threat | sensory → immune → subconscious → conscious → motor | Records conscious_strategy, processes via codec |
| Suppression | Conscious gate suppresses | sensory → immune → subconscious → conscious → motor | Empty output, strategies=["conscious_suppression"] |

## Orientational Field

18 Asparsa limbs at 0.5 midpoint (dynamic — sleep modifies weights). Per-feature reference formulas:

| Feature | Formula | At 0.5 |
|---|---|---|
| density | `0.8 + (mean_w - 0.5) * 0.4` | 0.8 |
| entropy | `3.5 + (tarka_w - 0.5) * 3.0` | 3.5 |
| coherence | `0.35 + (samatvam_w - 0.5) * 0.7` | 0.35 |
| periodicity | `(0.5 - prakasa_w) * 0.6` | 0.0 |
| noise_floor | `(0.5 - sraddha_w) * 0.6` | 0.0 |
| impedance | `(0.5 - nivrtti_w) * 0.6` | 0.0 |

## Infrastructure

- Orientational field: 18 Asparsa limbs, read by all systems, write restricted to SleepSystem.WRITE_TOKEN, dynamic (sleep modifies weights)
- LangGraph routing: sensory → immune → subconscious → conditional (escalate → conscious → motor, else → motor)
- Sleep and genetic NOT in graph routing — called directly by application code
- Conditional escalation: subconscious drives routing based on deviation, threat, and pattern history
- Escalation flag OR-preserved: immune (critical) and subconscious both contribute, neither erases
- Cache pruning: two layers — subconscious inline (encounter_count=1, >100 ticks) + sleep deep (encounter_count<=2, >50 ticks)
- Feature normalization: entropy /10.0 capped at 1.0 for distance computation
- Round-trip calibration: motor → sensory feedback loop, multi-input surface (5 inputs × 18 limbs × 2 weights = 180 points)
- Connection matrix: 17 primary (weight 1.0) + 6 secondary (weight 0.5), 3 absent connections enforced
- Shared target profile in base.py (sensory + motor import same function)
- Deliberator protocol: structural typing, swappable backends (Mock, Anthropic API)
- Prompt assembly: extracted module, graduated intensity, limb interactions, observation harness
- Codec protocol: structural typing, swappable codecs (TextCodec first implementation)
- Conscious-motor integration: suppression propagation, strategy metadata recording
- Areka defense-in-depth: 0.3 in codec (outer gate), 0.7 in conscious (inner gate)
- Mayavada: high humility (> 0.55) constrains transformation; low humility unconstrained
- Sleep state persistence: state["sleep_state"] dict (runtime addition)
- Genetic expression profile: factory seed (18 × 0.5), drift measurement, apoptotic threshold 3.0

## Active Blockers

- None

## Next Directive Candidates

- **Phase 3 — Feedback loops** (Motor→Conscious, Conscious→Sensory, Conscious→Immune)
- **Phase 3 — Graph topology routing** (use connection weights from topology.py)
- **Phase 3 — Homeostatic monitoring** (trigger sleep/suppress based on system health)
