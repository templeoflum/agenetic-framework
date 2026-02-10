# Current State

**Last updated:** 2026-02-09 (post-Directive 010)
**Tests:** 238 passing (was 237, +1 multi-input calibration surface)
**Last directive:** 010 — Audit Remediation

## System Status

| System | Status | Tests |
|---|---|---|
| Sensory | Implemented (~390 LOC) | 23 (test_systems) + contributions to test_graph, test_round_trip |
| Immune | Implemented (210 LOC) | 18 (test_systems) + contributions to test_graph |
| Subconscious | Implemented (186 LOC) | 17 (test_systems) + contributions to test_graph |
| Conscious | Stub (pass-through) | 7 (parametrized interface only) |
| Motor | Implemented (~620 LOC) | 7 (test_systems) + 58 (test_motor) + 44 (test_round_trip) |
| Sleep | Stub (pass-through, has WRITE_TOKEN) | 7 (parametrized interface only) |
| Genetic | Stub (pass-through) | 7 (parametrized interface only) |

## Test Files

| File | Tests | Scope |
|---|---|---|
| test_systems.py | 94 | Parametrized interface tests (all 7 systems) + system-specific tests |
| test_motor.py | 58 | Motor unit tests (strategies, determinism, field sensitivity, repair) |
| test_round_trip.py | 44 | Motor-sensory feedback loop, calibration sweep, multi-input surface |
| test_graph.py | 18 | LangGraph compilation, routing, signal-domain flow |
| test_topology.py | 24 | Connection matrix verification |

## Changes in Directive 010

### Per-feature delta computation (Part A — biggest change)
Sensory delta now uses per-feature references from the shared `compute_target_profile()` function in base.py, matching the motor's target profile formulas. Both systems import the same function. The old global-mean delta was dimensionally incoherent.

Aggregate deviation for clean prose at default weights: ~0.97 (was ~2.0 with global mean). The subconscious escalation threshold (1.5) is now above the clean-prose deviation, meaning clean text no longer automatically escalates.

### Shared target profile (Part A)
`compute_target_profile()`, `get_limb_weight()`, `mean_limb_weight()`, and all limb ID constants extracted from motor.py into base.py. Motor and sensory both import from base.py. Formulas can no longer drift apart.

### Bigram entropy (Part G)
`bigram_entropy` added to SignalFeatures (Shannon entropy over character bigram frequency distribution). Tarka does NOT register against bigram_entropy — sentence-level restructuring preserves character bigram patterns as well as token frequencies. **Tarka is definitively semantic-domain.**

### Multi-input calibration surface (Part F)
5 input types: clean_prose, noisy_text, short_input, code_like, long_repetitive. 180 sweep points (5 inputs x 18 limbs x 2 weights). Key finding: Tarka DOES produce measurable entropy delta on long_repetitive input (+0.39 at weight 0.0) — the response is input-dependent.

### Documentation (Parts C/D/E/H)
- "Calibration Validity" section added to ARCHITECTURE.md (tautological pattern documented)
- "Engineering Assignments" section added to ARCHITECTURE.md (limb mappings are design decisions)
- "confirmed" → "verified" across DEVLOG.md, CURRENT.md, planning entries
- Status labels updated: architecture_amendment.md and signal_report_structure.md now say "Implemented"
- ARCHITECTURE.md status section rewritten to reflect actual implementation state
- Audit protocol section added to CLAUDE.md
- README.md project tree fixed

### Bug fixes
- `test_motor.py::_vary_single_limb` baseline fixed from 1.0 to 0.5 (Part B)
- `_make_sample_state` in test_systems.py: added `transform_magnitude`, fixed `coherence` target from 0.7 to 0.35
- Stale comment in test_graph.py updated (field reference 1.0 → per-feature)
- Unused `dataclass` import removed from base.py

## Orientational Field

All 18 Asparśa limbs at 0.5 midpoint. Per-feature reference formulas:

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

## Active Blockers

- None

## Next Directive Candidates

- **Conscious layer** — first LLM-backed system, semantic domain crossing. Signal domain is audited, remediated, and documented. 8-9 limbs identified as needing semantic processing. Convergent cluster needs differentiation.
