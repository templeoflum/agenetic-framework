# Directive 009 — Comprehensive Mechanical Audit Report

**Date:** 2026-02-08
**Auditor:** DNAgent
**Scope:** All source files, test files, and documentation in the agenetic-framework repository
**Constraint:** Zero code changes. Read everything, report everything, fix nothing.

---

## Section 1: Interface Compliance

### Sensory System
- [x] Implements BaseSystem ABC correctly
- [x] `process()` takes SystemState, returns SystemState
- [x] `process()` does not mutate input state (uses `{**state, "signal_report": report}`)
- [x] `repair_check()` returns bool
- [x] `apoptotic_condition()` returns bool
- [x] `tick_rate` returns "every_cycle"

### Immune System
- [x] Implements BaseSystem ABC correctly
- [x] `process()` takes SystemState, returns SystemState
- [x] `process()` does not mutate input state (uses `{**state, ...}` spread)
- [x] `repair_check()` returns bool
- [x] `apoptotic_condition()` returns bool
- [x] `tick_rate` returns "every_cycle"

### Subconscious System
- [x] Implements BaseSystem ABC correctly
- [x] `process()` takes SystemState, returns SystemState
- [x] `process()` does not mutate input state (uses `{**state, ...}` spread)
- [x] `repair_check()` returns bool
- [x] `apoptotic_condition()` returns bool
- [x] `tick_rate` returns "every_cycle"

### Conscious System (stub)
- [x] Implements BaseSystem ABC correctly
- [x] `process()` takes SystemState, returns SystemState
- **DEVIATION:** `process()` returns `state` directly (same object reference), not `{**state}`. All implemented systems create a new dict with spread. This is a mutation risk if any downstream consumer modifies the returned dict.
- [x] `repair_check()` returns bool (always True)
- [x] `apoptotic_condition()` returns bool (always False)
- [x] `tick_rate` returns "on_escalation"

### Motor System
- [x] Implements BaseSystem ABC correctly
- [x] `process()` takes SystemState, returns SystemState
- [x] `process()` does not mutate input state (uses `{**state, "motor_output": ...}`)
- [x] `repair_check()` returns bool
- [x] `apoptotic_condition()` returns bool
- [x] `tick_rate` returns "on_demand"

### Sleep System (stub)
- [x] Implements BaseSystem ABC correctly
- **DEVIATION:** `process()` returns `state` directly (same as conscious — mutation risk)
- [x] `repair_check()` returns bool (always True)
- [x] `apoptotic_condition()` returns bool (always False)
- [x] `tick_rate` returns "periodic"

### Genetic System (stub)
- [x] Implements BaseSystem ABC correctly
- **DEVIATION:** `process()` returns `state` directly (same as conscious — mutation risk)
- [x] `repair_check()` returns bool (always True)
- [x] `apoptotic_condition()` returns bool (always False)
- [x] `tick_rate` returns "read_only"

**Summary:** Three stub systems (conscious, sleep, genetic) return the input state object by reference rather than creating a new dict. All implemented systems correctly use spread to create new state.

---

## Section 2: State Flow Integrity

### 2.1 Fields initialized by `create_default_state()`

| Field | Initial Value |
|---|---|
| input | `input_data` parameter |
| field | `field.read()` (FieldState from OrientationalField) |
| immune_log | `[]` |
| metadata | `{"tick": 0, "timestamps": [], "routing_history": []}` |
| flags | `{"degraded": [], "escalate_to_conscious": True, "apoptotic": False}` |
| signal_report | `None` |
| threat_assessment | `None` |
| subconscious_output | `None` |
| signal_pattern_cache | `[]` |
| motor_output | `None` |

### 2.2 State Flow Matrix

| Field | Sensory | Immune | Subconscious | Conscious | Motor | Graph |
|---|---|---|---|---|---|---|
| input | R | - | - | - | R | R |
| field | R | - | - | - | R | R |
| immune_log | - | RW | - | - | - | R |
| metadata | R (tick) | - | - | - | - | W (routing_history) |
| flags | - | RW | RW | - | - | R (escalation check) |
| signal_report | W | R | R | - | R | - |
| threat_assessment | - | W | R | - | - | - |
| subconscious_output | - | - | W | - | - | - |
| signal_pattern_cache | - | - | RW | - | - | - |
| motor_output | - | - | - | - | W | - |

### 2.3 Findings

**Field written but never read by any system:** `subconscious_output` is written by the subconscious system but not consumed by any other system during graph processing. The conscious stub doesn't read it. The motor doesn't read it. It is only available as part of the final graph output for external consumers.

**Field read but never written except by initialization:** `metadata.timestamps` is initialized as `[]` and never written to by any system. The graph wrapper writes `routing_history` but `timestamps` is never populated.

**`GraphState` vs `SystemState` typing mismatch:** `GraphState` uses weaker types (`dict` for field/metadata/flags, `Any` for signal_report/threat_assessment/subconscious_output/motor_output, `list` for immune_log/signal_pattern_cache). `SystemState` uses proper TypedDicts. The `_make_node` wrapper in graph.py manually reconstructs a full `SystemState` from `GraphState` on every node execution (lines 92-103).

---

## Section 3: Write Access Violations

### 3.1 Only sleep writes to the orientational field

**Mechanism:** `OrientationalField.write()` requires `caller_token` matching `SleepSystem.WRITE_TOKEN`.

**Finding:** The token is a public class attribute: `WRITE_TOKEN = "sleep_system_authorized"`. Any code that imports `SleepSystem` can read the token. This is a convention, not a security boundary. Test infrastructure (`vary_single_limb` in both test_motor.py and test_round_trip.py) regularly writes to the field using this token.

**No violations found.** No system other than tests calls `OrientationalField.write()` at runtime.

### 3.2 No system writes to the genetic layer at runtime

**No violations found.** The genetic system is a pass-through stub. No code writes to it.

### 3.3 Motor does not write to immune_log or signal_pattern_cache

**No violations found.** Motor's `process()` only adds `motor_output` to state via spread. Verified by test: `test_does_not_modify_immune_log`, `test_does_not_modify_signal_pattern_cache`.

### 3.4 No motor→sensory feedback within a single cycle

**No violations found.** In the graph, motor is the terminal node (`motor → END`). The round-trip test infrastructure feeds motor output back through sensory, but this is explicitly test infrastructure (separate from the graph execution path) and is clearly labeled as such.

---

## Section 4: Type Consistency

### 4.1 SystemState completeness

All fields defined in `SystemState` TypedDict are present in every state dict created by `create_default_state()`. ✓

### 4.2 SignalReport

All fields defined in `SignalReport`, `SignalFeatures`, `SignalClassification`, and `SignalDelta` TypedDicts are populated by sensory's `process()`. ✓ Consumers (immune, subconscious, motor) read fields that exist. ✓

### 4.3 ThreatAssessment

Populated by immune. ✓ Consumed by subconscious (reads `threat_level`). ✓ Not consumed by conscious (stub). Not consumed by motor.

### 4.4 SubconsciousOutput

Populated by subconscious. ✓ **Not consumed by any system in the graph.** The data is only available in the final graph output.

### 4.5 MotorOutput

**Finding:** `_make_sample_state()` in test_systems.py (line 64-73) creates a `motor_output` dict that does NOT include the `transform_magnitude` field added in Directive 007. The dict has `output_text`, `target_profile`, `strategies_applied`, and `repair_passed` but is missing `transform_magnitude`.

This doesn't cause test failures because motor's `repair_check()` only reads `repair_passed`, and the parametrized interface tests only check for `repair_passed is True`. But it means `_make_sample_state()` produces an incomplete `MotorOutput` that doesn't match the TypedDict definition.

### 4.6 CachedSignalPattern

Structure matches what subconscious writes and reads. ✓

---

## Section 5: Connection Matrix vs Graph Routing

### 5.1 Topology connections implemented in graph

| Connection | In Topology | In Graph |
|---|---|---|
| sensory → immune | ✓ Primary | ✓ Direct edge |
| immune → subconscious | ✓ Secondary (0.5) | ✓ Direct edge (treated as primary) |
| subconscious → conscious | ✓ Primary | ✓ Conditional edge |
| subconscious → motor | ✓ Primary | ✓ Conditional edge |
| conscious → motor | ✓ Primary | ✓ Direct edge |

### 5.2 Topology connections NOT implemented in graph

| Connection | Type | Reason |
|---|---|---|
| sensory → subconscious | Primary | Subconscious receives sensory data via state flow, but no direct graph edge |
| immune → conscious | Primary | Conscious receives immune data via state flow, but no direct graph edge |
| immune → motor | Primary | Motor receives immune data via state flow, but no direct graph edge |
| sleep → {all 6} | Primary | Phase 2 |
| genetic → {all except motor} | Primary | Phase 2 |
| conscious → immune | Secondary | Phase 2 |
| conscious → sensory | Secondary | Phase 2 |
| conscious → subconscious | Secondary | Phase 2 |
| motor → conscious | Secondary | Phase 2 |
| subconscious → immune | Secondary | Phase 2 |

### 5.3 Graph edges not in topology

**Finding:** The graph has an `immune → subconscious` direct edge, but in topology this is a SECONDARY connection (weight 0.5), not primary. The graph treats it as a primary sequential step. This is a Phase 1 simplification — the linear chain sensory → immune → subconscious implements the data flow described by multiple topology connections, but the graph routing doesn't reflect the connection weights.

### 5.4 Connection weights

Connection weights in the topology module are purely declarative. The graph does not reference or use them. Weight-based routing is Phase 2.

---

## Section 6: Test Coverage Analysis

### 6.1 Source file coverage

| File | Functions/Methods | Directly Tested | Indirectly Tested | Untested |
|---|---|---|---|---|
| base.py | 6 (ABC methods) | 0 | 6 (via subclasses) | 0 |
| sensory.py | 15 | 5 | 10 | 0 |
| immune.py | 8 | 5 | 2 | 1 |
| subconscious.py | 8 | 5 | 3 | 0 |
| conscious.py | 5 | 0 | 5 (via parametrized) | 0 |
| sleep.py | 5 | 0 | 5 (via parametrized) | 0 |
| genetic.py | 5 | 0 | 5 (via parametrized) | 0 |
| motor.py | 18 | 12 | 6 | 0 |
| orientational.py | 3 | 3 | 0 | 0 |
| graph.py | 4 | 2 | 2 | 0 |
| topology.py | 3 | 3 | 0 | 0 |

**Untested specific behavior:** `ImmuneSystem.apoptotic_condition` triggering after 3 consecutive critical-level assessments. The parametrized interface test verifies it returns False for normal state, but there is no test that feeds 3 critical inputs and verifies it returns True.

### 6.2 Tests that test implementation details rather than behavior

- `test_motor.py::TestMotorHelpers` tests private helper functions (`_get_limb_weight`, `_mean_weight`, `_compute_target_profile`) by name. These test implementation details — if the motor were refactored to use different internal helpers, these tests would break even if behavior is preserved.

### 6.3 Tautological or near-tautological tests

- `test_motor.py::TestMayavadaCap::test_low_mayavada_constrains_output` — **Does nothing.** The test body ends with `pass` and a comment "This test needs revision — see test below." It always passes regardless of motor behavior.

- `test_motor.py::TestSvadharmaSelectivity::test_high_svadharma_fewer_strategies` — Only asserts `isinstance(strategies, list)`. This can never fail because `strategies_applied` is always a list by construction.

- `test_motor.py::TestSvadharmaSelectivity::test_default_svadharma_behavior` — Only asserts `repair_passed is True`. Doesn't test Svadharma behavior.

- `test_motor.py::TestKsetraJnanaSensitivity::test_high_ksetra_more_responsive` — Only asserts `repair_passed is True`. Doesn't test responsiveness.

- `test_motor.py::TestKsetraJnanaSensitivity::test_default_ksetra_unchanged` — Only asserts `repair_passed is True`. Doesn't test that behavior is unchanged.

### 6.4 Calibration tests as data collectors

The following tests have minimal assertions and primarily serve as data recording:

- `TestCalibrationSweep::test_limb_weight_zero` — Asserts `output_report is not None` and `output_text != ""`. Main purpose is `_print_calibration_record()`.
- `TestCalibrationSweepFull::test_limb_weight_full` — Asserts `output_report is not None` and `output_text is not None` (note: not even `!= ""`).
- `test_calibration_summary` — Asserts `len(all_results) == 36` (completeness check only).

These are intentionally data-recording tests per the directive documentation. The naming makes their purpose clear.

---

## Section 7: Dead Code and Unused Imports

### 7.1 Unused imports

- **`base.py` line 10:** `from dataclasses import dataclass, field` — **UNUSED.** No dataclass is defined in base.py. This import has persisted since Directive 001 when the file was scaffolded. All types use TypedDict, not dataclass.

### 7.2 Duplicated functions

- **`_to_str()`** — Identical implementation exists in both `sensory.py` (line 32) and `motor.py` (line 59). Same function name, same logic, same behavior.

- **`_euclidean_distance()`** — Identical implementation exists in both `immune.py` (line 40) and `subconscious.py` (line 36). Same function name, same logic, same behavior.

### 7.3 Unused constants/fields

- **`metadata["timestamps"]`** — Initialized as `[]` in `create_default_state()` but never written to by any system or the graph wrapper. Dead field.

### 7.4 Code paths that can never execute

No unreachable code paths found. All branches in strategy functions and system methods have plausible trigger conditions.

---

## Section 8: Documentation vs Reality

### README.md

| Claim | Accurate? | Issue |
|---|---|---|
| "237 tests" | ✓ | |
| "pytest (237 tests)" | ✓ | |
| Project structure shows `PLANNING_LOG.md` | **STALE** | Was removed in Directive 006, replaced by `planning/` directory |
| Project structure missing `planning/` | **MISSING** | Not shown in the tree |
| "10 strategies" | ✓ | The sentence grammar is ambiguous — "6 feature modulators + noise floor modulation" reads like 7, but noise floor IS one of the 6 |
| "Orientational field with all 18 Asparśa limbs" | ✓ | |
| Midpoint weight model described | ✓ | Added in D008 update |

### CLAUDE.md

| Claim | Accurate? | Issue |
|---|---|---|
| Project structure | ✓ | Shows `planning/` correctly |
| 7 systems described | ✓ | |
| Directive workflow | ✓ | |
| Reference material section | ✓ | |

### docs/ARCHITECTURE.md

| Claim | Accurate? | Issue |
|---|---|---|
| Status: "not yet implemented" | **STALE** | Much IS implemented (sensory, immune, subconscious, motor, orientational field, graph routing) |
| Phase 1: "No sleep, no homeostasis, no apoptosis" | **PARTIALLY STALE** | Apoptotic conditions ARE implemented on all systems. Sleep stub has WRITE_TOKEN. |
| Phase 1: "Orientational field as static context injection" | **STALE** | Field weights actively drive motor target profiles and strategy selection |
| Phase 1: "Fixed connection weights (no modification yet)" | ✓ | Weights are declarative only |
| Connection matrix | ✓ | Matches topology.py |
| Seven system descriptions | ✓ | Descriptions match implementations |

### docs/architecture_amendment.md

| Claim | Accurate? | Issue |
|---|---|---|
| "Status: Proposed" | **STALE** | The signal-semantics boundary IS implemented |
| Content accuracy | ✓ | Signal/semantic/meta domain descriptions match implementation |

### docs/signal_report_structure.md

| Claim | Accurate? | Issue |
|---|---|---|
| "Status: Proposed" | **STALE** | The structure IS implemented exactly as proposed |
| TypedDict definitions | ✓ | Match base.py exactly |
| SystemState extension at bottom | **INCOMPLETE** | Shows an older version of SystemState missing `threat_assessment`, `subconscious_output`, `signal_pattern_cache`, `motor_output` |

### DEVLOG.md

| Claim | Accurate? | Issue |
|---|---|---|
| All directive entries | ✓ | Complete and accurate through D008 |
| Test counts | ✓ | |
| Calibration results | ✓ | |

### planning/CURRENT.md

| Claim | Accurate? | Issue |
|---|---|---|
| System status | ✓ | |
| Test counts | ✓ | 237 passing |
| Calibration data | ✓ | Matches D008 sweep |

---

## Section 9: Motor Strategy Audit

### Strategy 1: Density Modulation

| Property | Value |
|---|---|
| Governing limb | Mean weight (all 18 limbs) |
| Target formula | `0.8 + (mean_w - 0.5) * 0.4` |
| Transformation | Collapse whitespace (increase) / Add newlines between sentences (decrease) |
| Deterministic | ✓ Regex-only, no randomness |
| Preserves repair | ✓ Whitespace changes preserve tokens |
| Calibration | No unique limb response (mean-governed) — accurate |

### Strategy 2: Entropy Modulation

| Property | Value |
|---|---|
| Governing limb | Tarka (2) |
| Target formula | `3.5 + (tarka_w - 0.5) * 3.0` |
| Transformation | Split at conjunctions/commas (increase) / Merge short sentences with connectives (decrease) |
| Deterministic | ✓ No randomness |
| Preserves repair | ✓ Sentence-level restructuring preserves most tokens |
| Calibration | Does not register |

**Why it doesn't register:** Shannon entropy is computed over token frequency distribution. Sentence-level restructuring (split/merge) preserves the same tokens — it changes syntax but not vocabulary distribution. The strategy fires (appears in `strategies_applied`) but sensory measures the same entropy on the restructured text. This is accurately documented in DEVLOG entries for D004, D007, and D008.

### Strategy 3: Coherence Modulation

| Property | Value |
|---|---|
| Governing limb | Samatvam (7) |
| Target formula | `0.35 + (samatvam_w - 0.5) * 0.7` |
| Transformation | Bridge words from previous sentence (increase) / Reverse sentence order (decrease) |
| Deterministic | ✓ |
| Preserves repair | ✓ |
| Calibration | ✓ Confirmed: −0.0263 at weight 0.0 |

### Strategy 4: Impedance Modulation

| Property | Value |
|---|---|
| Governing limb | Nivṛtti (3) |
| Target formula | `(0.5 - nivrtti_w) * 0.6` |
| Transformation | Strip non-ASCII/brackets (decrease) / Add section markers (increase) |
| Deterministic | ✓ |
| Preserves repair | ✓ |
| Calibration | ✓ Confirmed: +0.3667 at weight 0.0 |

### Strategy 5: Periodicity Modulation

| Property | Value |
|---|---|
| Governing limb | Prakāśa (1) |
| Target formula | `(0.5 - prakasa_w) * 0.6` |
| Transformation | Insert separators between repeated bigrams (decrease) / Repeat phrases at intervals (increase) |
| Deterministic | ✓ |
| Preserves repair | ✓ |
| Calibration | ✓ Confirmed: +0.0912 at weight 0.0 |

### Strategy 6: Noise Floor Modulation

| Property | Value |
|---|---|
| Governing limb | Śraddhā (5) |
| Target formula | `(0.5 - sraddha_w) * 0.6` |
| Transformation | Remove single-char/punctuation tokens (decrease) / Insert pipe markers (increase) |
| Deterministic | ✓ |
| Preserves repair | ✓ |
| Calibration | ✓ Confirmed: +0.0541 at weight 0.0 |

### Strategy 7: Māyāvāda Cap

| Property | Value |
|---|---|
| Governing limb | Māyāvāda (4) |
| Threshold | `mayavada_w < 0.45` activates cap |
| Transformation | Blend output back toward original text |
| Deterministic | ✓ |
| Preserves repair | ✓ (blending toward original increases token overlap) |
| Calibration | Does not register — At default 0.5, cap is inactive. At 0.0, `max_allowed = 1.0` (no constraint). Accurately documented. |

### Strategy 8: Ārēka Gate

| Property | Value |
|---|---|
| Governing limb | Ārēka (8) |
| Threshold | `areka_w > 0.3` AND `noise_floor > 0.3` AND `entropy > 5.0` |
| Transformation | Suppress output entirely (output_text = "") |
| Deterministic | ✓ |
| Preserves repair | Returns `repair_passed=True` explicitly |
| Calibration | Does not register — calibration text is clean (low noise, moderate entropy). Accurately documented. |

### Strategy 9: Svadharma Selectivity

| Property | Value |
|---|---|
| Governing limb | Svadharma (9) |
| Effect | `threshold_scale = 0.5 + svadharma_w` (scales all strategy thresholds) |
| Transformation | No direct text transformation; modifies which strategies fire |
| Deterministic | ✓ |
| Calibration | At 1.0, threshold_scale=1.5, strategies' thresholds too high → fewer fire. Accurately documented. |

### Strategy 10: Kṣetra-Jñāna Sensitivity

| Property | Value |
|---|---|
| Governing limb | Kṣetra-Jñāna (10) |
| Effect | `delta_scale = 0.5 + ksetra_w * 0.5` (scales all delta magnitudes) |
| Transformation | No direct text transformation; modifies delta sizes |
| Deterministic | ✓ |
| Calibration | At 0.0, delta_scale=0.5, deltas halved → fewer strategies fire. Accurately documented. |

---

## Section 10: Calibration Apparatus Integrity

### 10.1 Does `round_trip()` actually feed motor output back through sensory?

**Yes.** Data flow verified:
1. `sensory.process(state_a)` → signal_report A (line 97-98)
2. `motor.process(state_a)` → motor_output with output_text (line 101-103)
3. `create_default_state(input_data=restructured, field=field)` → new state with motor's output_text as input (line 106)
4. `sensory.process(state_b)` → signal_report B (line 107-108)
5. Feature deltas = B.features[key] - A.features[key] (lines 112-115)

The loop is correctly implemented.

### 10.2 Does `vary_single_limb()` actually vary only one limb?

**Yes.** It iterates all limbs, sets the specified one to `weight`, and all others to `baseline`. Verified in both test_round_trip.py (line 48-69) and test_motor.py (line 55-65).

### 10.3 Does the calibration sweep test all 18 limbs?

**Yes.** `ALL_LIMB_IDS = list(range(1, 19))` — covers limbs 1-18. Used by both parameterized test classes and the summary test.

### 10.4 At three weight points?

**Yes.** Parameterized classes test 0.0 and 1.0. `test_calibration_summary` tests 0.0, 0.5 (baseline verification), and 1.0.

### 10.5 Are deltas computed correctly?

**Yes.** In `test_calibration_summary`, deltas are `varied_features[key] - baseline_features[key]` where baseline is the all-0.5 round-trip output. In parameterized tests, deltas are relative to `baseline_result["output_report"]["features"]`. Consistent.

### 10.6 Could the infrastructure produce misleading results?

**Finding 1:** Each `round_trip()` call creates new `SensorySystem()` and `MotorSystem()` instances. The motor's `_consecutive_repair_failures` counter resets each call. This is correct for calibration (each sweep point is independent) but means the infrastructure cannot test repair failure accumulation or apoptotic conditions.

**Finding 2:** In the round-trip loop, step 2 passes `state_a` (which includes the signal report) to the motor. The motor uses `state_a["signal_report"]["features"]` as "current" features when computing deltas against the target profile. Then step 3 feeds the motor's output_text through sensory as a fresh input with a fresh signal report. The calibration measures the difference between sensory's characterization of the INPUT vs sensory's characterization of the OUTPUT. This is the intended measurement.

**No misleading results identified.** The apparatus measures what it claims to measure.

---

## Section 11: Orientational Field Integrity

### 11.1 All 18 limbs present with correct IDs

**Yes.** IDs 1-18, verified in `orientational.py` `_DEFAULT_LIMBS` and in `test_graph.py::TestOrientationalFieldAccess::test_all_eighteen_limbs_present`.

### 11.2 Name consistency

| ID | orientational.py | test_round_trip.py _LIMB_NAMES | motor.py constants | Consistent? |
|---|---|---|---|---|
| 1 | Prakasa | Prakasa | PRAKASA_ID = 1 | ✓ |
| 2 | Tarka | Tarka | TARKA_ID = 2 | ✓ |
| 3 | Nivrtti | Nivrtti | NIVRTTI_ID = 3 | ✓ |
| 4 | Mayavada | Mayavada | MAYAVADA_ID = 4 | ✓ |
| 5 | Sraddha | Sraddha | SRADDHA_ID = 5 | ✓ |
| 6 | Atma-Vichara | Atma-Vichara | (no constant) | ✓ |
| 7 | Samatvam | Samatvam | SAMATVAM_ID = 7 | ✓ |
| 8 | Areka | Areka | AREKA_ID = 8 | ✓ |
| 9 | Svadharma | Svadharma | SVADHARMA_ID = 9 | ✓ |
| 10 | Ksetra-Jnana | Ksetra-Jnana | KSETRA_JNANA_ID = 10 | ✓ |
| 11 | Vishvarupa | Vishvarupa | (no constant) | ✓ |
| 12 | Bodhi | Bodhi | (no constant) | ✓ |
| 13 | No-Position | No-Position | (no constant) | ✓ |
| 14 | Nivrtti-Rest | Nivrtti-Rest | (no constant) | ✓ |
| 15 | Mirror | Mirror | (no constant) | ✓ |
| 16 | Fourfold-State | Fourfold-State | (no constant) | ✓ |
| 17 | Ajati | Ajati | (no constant) | ✓ |
| 18 | Asparsa-Yoga | Asparsa-Yoga | (no constant) | ✓ |

All names consistent across all references.

### 11.3 Write access restriction

Write access enforced via `caller_token != SleepSystem.WRITE_TOKEN` check. The token is a plain string class attribute `"sleep_system_authorized"`. Any code importing `SleepSystem` can access the token. This is a convention-based guard, not a cryptographic one.

### 11.4 Could any system bypass the write restriction?

Any code that imports `SleepSystem` can call `field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)`. The restriction prevents accidental writes but not intentional bypasses. The test infrastructure does this regularly and correctly.

### 11.5 Motor limb IDs match field IDs

All motor constants (PRAKASA_ID=1 through KSETRA_JNANA_ID=10) match the corresponding limb IDs in the orientational field. ✓

---

## Section 12: Anything Else

### 12.1 `test_motor.py` baseline inconsistency (Directive 008 miss)

`test_motor.py` line 55 defines `_vary_single_limb(limb_id, weight, baseline=1.0)`. The `test_round_trip.py` version was updated to `baseline=0.5` in Directive 008, but the `test_motor.py` version was NOT updated. This means motor field sensitivity tests set non-varied limbs to 1.0 instead of the intended 0.5 operating point.

Affected tests: All tests in `TestMotorFieldSensitivity`, `TestTarkaSentenceLevel` (test_entropy_round_trip_measurable_change), `TestSraddhaNoise`, `TestMayavadaCap`, `TestArekaGate`, `TestSvadharmaSelectivity`, `TestKsetraJnanaSensitivity`, `TestNewStrategyIntegration` — any test that calls `_vary_single_limb()`.

The tests still pass because they check relative behavior (different weights produce different outputs), not absolute behavior at the 0.5 operating point.

### 12.2 `create_default_state` always escalates

`flags["escalate_to_conscious"] = True` is the Phase 1 default (graph.py line 66). Every input passes through the conscious stub. The reflex path is only tested with explicit flag override in `test_no_escalation_skips_conscious`. This is documented as intentional Phase 1 behavior.

### 12.3 Stale comment in test_graph.py

`test_no_escalation_skips_conscious` (line 77) has a comment "aggregate_deviation > 1.5 for any text input vs. field reference of 1.0" — the reference to "1.0" is stale since Directive 008 changed the field reference to 0.5.

### 12.4 `_make_sample_state` missing `transform_magnitude`

As noted in Section 4.5, `test_systems.py::_make_sample_state()` (line 64-73) creates a `motor_output` dict without the `transform_magnitude` field added in Directive 007. This doesn't cause test failures but means the sample state doesn't match the current `MotorOutput` TypedDict.

### 12.5 Immune adaptive matching uses JSON serialization

`immune.py` stores feature vectors as JSON strings in the threat log (`json.dumps(current_vector)`) and parses them back with `json.loads(entry["pattern"])`. This works but is unusual — the vectors could be stored directly as lists since the state is in-memory Python dicts, not serialized to disk. The JSON round-trip is unnecessary overhead and adds a failure mode (JSONDecodeError handling at line 125).

### 12.6 `immune.py` uses `datetime.now(timezone.utc)` for timestamps

The immune system generates timestamps via `datetime.now(timezone.utc).isoformat()` (line 105) each time it processes. This means immune processing is NOT deterministic — the same input processed at different times produces different threat log timestamps. This doesn't affect test results (no test checks timestamps) but breaks the "deterministic given same input + field state" property that sensory and motor maintain.

### 12.7 Sensory `_compute_delta` uses mean of all limb weights as reference

The sensory delta computation (sensory.py line 240-278) uses the mean of ALL limb weights as a single reference value, then subtracts this same reference from EVERY feature. This means all six feature deltas are relative to the same scalar reference. The v1 comment says "v1 simplification" — this is noted but not yet replaced with per-feature reference values.

### 12.8 Graph `_make_node` doesn't handle unknown GraphState keys

The `_make_node` wrapper (graph.py lines 92-103) manually constructs a `SystemState` dict from `GraphState` by listing specific keys. If LangGraph adds any extra keys to the GraphState during execution, they would be dropped. This is a fragility point for future LangGraph version upgrades.

### 12.9 `test_round_trip.py` Ārēka suppression handling in sweep

`_run_sweep_at_weight()` (line 296-300) has special handling for Ārēka suppression: if output_text is empty and "areka_suppression" is in strategies_applied, it uses zeroed features. However, with the D008 threshold change (`areka_w > 0.3`), the Ārēka gate would fire for the varied limb at weight=1.0 IF the calibration text had high noise+entropy. The current calibration text does not trigger this, so this code path has never been exercised.

---

*End of audit report. All 12 sections completed. Every source file, test file, and documentation file was examined.*
