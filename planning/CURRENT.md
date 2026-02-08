# Current State

**Last updated:** 2026-02-08 (post-Directive 008)
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
| test_round_trip.py | 43 | Motor-sensory feedback loop, calibration sweep (18 limbs × 3 weight points) |
| test_graph.py | 18 | LangGraph compilation, routing, signal-domain flow |
| test_topology.py | 24 | Connection matrix verification |

## Orientational Field — Midpoint Weight Model

All 18 Asparśa limbs default to **0.5** (midpoint). This is the factory calibration — maximum information entropy, equally capable of amplification (>0.5) or suppression (<0.5). Changed from 1.0 in Directive 008.

Target profile formulas use symmetric structure: `target = base + (weight - 0.5) * scale`

| Feature | Formula | At 0.5 (baseline) |
|---|---|---|
| density | `0.8 + (mean_w - 0.5) * 0.4` | 0.8 |
| entropy | `3.5 + (tarka_w - 0.5) * 3.0` | 3.5 |
| coherence | `0.35 + (samatvam_w - 0.5) * 0.7` | 0.35 |
| periodicity | `(0.5 - prakasa_w) * 0.6` | 0.0 |
| noise_floor | `(0.5 - sraddha_w) * 0.6` | 0.0 |
| impedance | `(0.5 - nivrtti_w) * 0.6` | 0.0 |

## Motor Strategy Inventory

| Strategy | Governing Limb | Type | Calibration Status (0.5 midpoint) |
|---|---|---|---|
| Density modulation | Mean weight | Feature modulator | No unique limb response (mean-governed) |
| Entropy modulation | Tarka (2) | Feature modulator (sentence-level) | Does not register — same finding as D007 |
| Coherence modulation | Samatvam (7) | Feature modulator | Confirmed: −0.0263 at 0.0, graded |
| Impedance modulation | Nivṛtti (3) | Feature modulator | Confirmed: +0.3667 at 0.0 |
| Periodicity modulation | Prakāśa (1) | Feature modulator | Confirmed: +0.0912 at 0.0 |
| Noise floor modulation | Śraddhā (5) | Feature modulator | Confirmed: +0.0541 at 0.0 |
| Māyāvāda cap | Māyāvāda (4) | Post-processing constraint | Cap inactive at default (threshold < 0.45) |
| Ārēka suppression | Ārēka (8) | Gate (binary) | Gate inactive for clean calibration text |
| Svadharma selectivity | Svadharma (9) | Meta-strategy (threshold scaling) | Confirmed: at 1.0, strategies drop to zero (threshold too high) |
| Kṣetra-Jñāna sensitivity | Kṣetra-Jñāna (10) | Meta-strategy (delta scaling) | Confirmed: at 0.0, strategies drop to zero (delta scaled to zero) |

## Calibration Summary (Directive 008 — 0.5 midpoint)

**Baseline check:** All limbs at 0.5 produce zero delta (correct — midpoint is neutral).

**Suppression (0.0) — confirmed responses:**
- Prakāśa: periodicity +0.0912, entropy −0.0768, coherence +0.0345
- Nivṛtti: impedance +0.3667, entropy +0.1646
- Samatvam: coherence −0.0263, entropy −0.0595
- Śraddhā: noise_floor +0.0541, entropy +0.0576
- Kṣetra-Jñāna: strategies drop to zero → coherence +0.0345, periodicity −0.0588 (second-order)

**Amplification (1.0) — confirmed responses:**
- Tarka: coherence +0.0854, periodicity −0.0588 (second-order via strategy change, not entropy)
- Svadharma: strategies drop to zero → same pattern as Kṣetra-Jñāna at 0.0

**Asymmetric responses:** Suppression produces more visible effects than amplification. This is because baseline strategies (entropy_modulation, coherence_modulation) already fire at 0.5. Suppression (0.0) adds new strategies or changes deltas. Amplification (1.0) mostly makes existing strategies fire harder but within same feature space.

**Convergent cluster — zero delta at both 0.0 and 1.0 (8 limbs):**
Ātma-Vichāra, Vishvarūpa, Bodhi, No-Position, Nivṛtti-Rest, Mirror, Fourfold-State, Ajāti, Asparśa-Yoga

These limbs have no motor strategies. They are semantic-domain or meta-domain — conscious layer is required.

## Infrastructure

- Orientational field: 18 Asparsa limbs at 0.5 midpoint, read by all systems, write restricted to SleepSystem.WRITE_TOKEN
- LangGraph routing: sensory -> immune -> subconscious -> conditional (escalate -> conscious -> motor, else -> motor)
- Round-trip calibration: motor -> sensory feedback loop, three-point sweep (0.0, 0.5, 1.0), 5 confirmed primary mappings + 2 meta-strategy effects
- Connection matrix: 17 primary (weight 1.0) + 6 secondary (weight 0.5), 3 absent connections enforced

## Last Directive

Directive 008: Migrated all 18 limb weights from 1.0 to 0.5 (midpoint model). Rebalanced target profile formulas with symmetric structure. Adjusted Ārēka and Māyāvāda thresholds. Three-point calibration sweep confirms same 5 primary mappings + 2 meta-strategy effects. Baseline check passes (0.5 = zero delta).

## Active Blockers

- None

## Next Directive Candidates

- **Conscious layer** — first LLM-backed system, clear requirements from calibration (8-9 limbs need semantic processing), convergent cluster needs differentiation
- **Sleep layer** — transfer function optimization, cache pruning, orientational field weight adjustment
- **Tarka investigation** — three approaches failed (token-level, sentence-level, midpoint rebalance). Accept as semantic-domain or try fundamentally different approach
