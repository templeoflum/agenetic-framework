# Current State

**Last updated:** 2026-02-10 (post-Directive 015a)
**Tests:** 320 passing + 2 skipped (unchanged from D014)
**Last directive:** 015a — Audit Artifact Cleanup (015 = mechanical audit, 015a = artifact separation + conceptual audit commit)

## System Status

| System | Status | Tests |
|---|---|---|
| Sensory | Implemented (~390 LOC) | 23 (test_systems) + contributions to test_graph, test_round_trip, test_integration |
| Immune | Implemented (210 LOC) | 18 (test_systems) + contributions to test_graph, test_integration |
| Subconscious | Implemented (188 LOC) | 17 (test_systems) + contributions to test_graph, test_integration |
| Conscious | Foundation (~440 LOC + ~100 LOC deliberator + ~380 LOC prompt assembly) | 7 (test_systems) + 30 (test_conscious) + 1 (test_graph) + 24 (test_prompt_assembly) + contributions to test_integration |
| Motor | Integrated (~189 LOC orchestrator + ~55 LOC codec.py + ~430 LOC text_codec.py) | 7 (test_systems) + 58 (test_motor) + 44 (test_round_trip) + 12 (test_codec) + contributions to test_integration |
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
| test_codec.py | 12 | Protocol conformance (3), equivalence (4), quality check (2), motor delegation (3) |
| test_integration.py | 16 | End-to-end paths: reflex (4), escalated (4), suppression (3), routing (3), cross-path (2) |
| test_graph.py | 18 | LangGraph compilation, routing, signal-domain flow |
| test_topology.py | 24 | Connection matrix verification |

## Audit Phase Complete (D015 + D015a)

### Mechanical Audit (D015)
Full codebase inventory: 16 source files, 9 test files, ~7,094 LOC, 83 hardcoded thresholds, 75 numbered observations. Zero code changes.
- Report: `handoff/015_mechanical_audit_report.md`

### Conceptual Audit (produced by fresh planning instance)
Adversarial evaluation of architecture claims, limb mappings, threshold quality, and implementation gaps. 7 critical findings, 5 strengths, 10 recommendations.
- Report: `handoff/015_conceptual_audit_report.md`

### Key Audit Findings (triage for remediation directive)
**Must fix:**
1. Subconscious cache grows without pruning — apoptotic at 10,001 entries (time bomb)
2. Escalation flag overwrite — subconscious unconditionally overwrites immune's escalation signal
3. Immune override dead code — conscious gate checks for "escalate" action no system produces

**Should fix:**
4. Mayavada inversion — high weight = no constraint (semantically backwards)
5. Areka threshold inconsistency — 0.3 in codec vs 0.7 in conscious gate (undocumented rationale)
6. Feature vector normalization — entropy dominates Euclidean distance matching
7. Limb 14 naming — "Nivrtti-Rest" vs "Rest-as-Realization" inconsistency

**Watch:**
8. Tautological motor strategies — 5/6 strategies manipulate what sensors measure
9. Convergent cluster decorative alone — 5 limbs individually inert at any weight
10. Dormant gate — all suppression paths require weights sleep can't yet modify

## Three Routing Paths

| Path | Condition | Route | Motor behavior |
|---|---|---|---|
| Reflex | Low deviation, no threat | sensory → immune → subconscious → motor | Processes input directly via codec |
| Escalated | High deviation or threat | sensory → immune → subconscious → conscious → motor | Records conscious_strategy, processes via codec |
| Suppression | Conscious gate suppresses | sensory → immune → subconscious → conscious → motor | Empty output, strategies=["conscious_suppression"] |

## Orientational Field

All 18 Asparsa limbs at 0.5 midpoint. Per-feature reference formulas unchanged from D010:

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
- LangGraph routing: sensory → immune → subconscious → conditional (escalate → conscious → motor, else → motor)
- Conditional escalation: subconscious drives routing based on deviation, threat, and pattern history
- Round-trip calibration: motor → sensory feedback loop, multi-input surface (5 inputs x 18 limbs x 2 weights = 180 points)
- Connection matrix: 17 primary (weight 1.0) + 6 secondary (weight 0.5), 3 absent connections enforced
- Shared target profile in base.py (sensory + motor import same function)
- Deliberator protocol: structural typing, swappable backends (Mock, Anthropic API)
- Prompt assembly: extracted module, graduated intensity, limb interactions, observation harness
- Codec protocol: structural typing, swappable codecs (TextCodec first implementation)
- Conscious-motor integration: suppression propagation, strategy metadata recording

## Active Blockers

- None

## Next Directive Candidates

- **016 — Remediation** — Address must-fix items from audit (cache pruning, escalation flag, immune override dead code) plus low-cost should-fix items.
