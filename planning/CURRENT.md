# Current State

**Last updated:** 2026-02-08 (post-Directive 007)
**Tests:** 237 passing

## System Status

| System | Status | Tests |
|---|---|---|
| Sensory | Implemented (370 LOC) | 23 (test_systems) + contributions to test_graph, test_round_trip |
| Immune | Implemented (210 LOC) | 18 (test_systems) + contributions to test_graph |
| Subconscious | Implemented (186 LOC) | 17 (test_systems) + contributions to test_graph |
| Conscious | Stub (pass-through) | 7 (parametrized interface only) |
| Motor | Implemented (661 LOC) | 7 (test_systems) + 58 (test_motor) + 43 (test_round_trip) |
| Sleep | Stub (pass-through, has WRITE_TOKEN) | 7 (parametrized interface only) |
| Genetic | Stub (pass-through) | 7 (parametrized interface only) |

## Test Files

| File | Tests | Scope |
|---|---|---|
| test_systems.py | 94 | Parametrized interface tests (all 7 systems) + system-specific tests (sensory, immune, subconscious) |
| test_motor.py | 58 | Motor unit tests (strategies, determinism, field sensitivity, repair, new strategies) |
| test_round_trip.py | 43 | Motor-sensory feedback loop, calibration sweep (18 limbs × 2 weight points) |
| test_graph.py | 18 | LangGraph compilation, routing, signal-domain flow |
| test_topology.py | 24 | Connection matrix verification |

## Motor Strategy Inventory

| Strategy | Governing Limb | Type | Calibration Status |
|---|---|---|---|
| Density modulation | Mean weight | Feature modulator | Fires but no unique limb response (mean-governed) |
| Entropy modulation | Tarka (2) | Feature modulator (sentence-level) | Does not register in calibration — see notes |
| Coherence modulation | Samatvam (7) | Feature modulator | Confirmed: −0.0263 at 0.0, graded (0.0 at 0.5) |
| Impedance modulation | Nivṛtti (3) | Feature modulator | Confirmed: +0.3667 impedance |
| Periodicity modulation | Prakāśa (1) | Feature modulator | Confirmed: +0.0912 periodicity |
| Noise floor modulation | Śraddhā (5) | Feature modulator | **New, confirmed:** +0.0541 noise_floor |
| Māyāvāda cap | Māyāvāda (4) | Post-processing constraint | Implemented, no calibration signal (cap inactive at default) |
| Ārēka suppression | Ārēka (8) | Gate (binary) | Implemented, no calibration signal (gate inactive for clean input) |
| Svadharma selectivity | Svadharma (9) | Meta-strategy (threshold scaling) | Implemented, no direct feature response |
| Kṣetra-Jñāna sensitivity | Kṣetra-Jñāna (10) | Meta-strategy (delta scaling) | **New, confirmed:** second-order effects (coherence +0.0854, periodicity −0.0588) |

## Calibration Summary (Directive 007)

**Apparatus-confirmed limb-to-feature mappings (5):** Prakāśa→periodicity, Nivṛtti→impedance, Samatvam→coherence, Śraddhā→noise_floor, Kṣetra-Jñāna→second-order effects

**Implemented but not registering in calibration (4):** Tarka (entropy decrease same output), Māyāvāda (inactive at default weight), Ārēka (gate doesn't fire for clean calibration text), Svadharma (threshold scaling is second-order)

**Convergent cluster — indistinguishable at signal level (5):** Bodhi, Mirror, Ajāti, Asparśa, Rest — all produce zero delta. Needs conscious layer.

**Semantic-domain only (3):** Vishvarūpa, No-Position, Fourfold State — zero delta, needs conscious layer.

**Uncategorized (1):** Ātma-Vichāra — zero delta, may need dedicated analysis.

## Infrastructure

- Orientational field: 18 Asparsa limbs, read by all systems, write restricted to SleepSystem.WRITE_TOKEN
- LangGraph routing: sensory -> immune -> subconscious -> conditional (escalate -> conscious -> motor, else -> motor)
- Round-trip calibration: motor -> sensory feedback loop, two-point sweep (0.0 and 0.5), 5 confirmed mappings
- Connection matrix: 17 primary (weight 1.0) + 6 secondary (weight 0.5), 3 absent connections enforced

## Last Directive

Directive 007: Extended motor with 5 new strategies (Śraddhā, Māyāvāda, Ārēka, Svadharma, Kṣetra-Jñāna). Rewrote Tarka entropy to sentence-level. Added two-point calibration sweep. 42 new tests (24 motor + 18 round-trip).

## Active Blockers

- None

## Next Directive Candidates

- Conscious layer — first LLM-backed system, now with clear requirements from calibration data (8-9 limbs need semantic processing)
- Sleep layer — transfer function optimization, cache pruning, orientational field weight adjustment
- Tarka investigation — entropy modulation fires but doesn't produce distinct calibration signal; may need fundamentally different approach
