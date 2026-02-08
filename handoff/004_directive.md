# Directive 004 — Motor Layer Implementation with Round-Trip Calibration Infrastructure

**From:** Planning instance (claude.ai)
**To:** Transducer Archive (CLI agent)
**Date:** 2026-02-08

## Context

After Directives 001 (scaffold), 002 (signal-domain tier), and 003 (documentation sync), the signal domain is operational: sensory characterizes input as signal features, immune detects anomalies, subconscious correlates patterns and makes escalation decisions. 136 tests pass.

The next architectural question is how to validate the limb-to-feature mappings — the assignments connecting specific Asparśa Yoga limbs to specific signal features. The preliminary mapping exists in `references/conceptual_archaeology.md` Section V, but it was drafted theoretically. Some assignments are confident (Prakāśa → signal characterization), others tentative (Samatvam → coherence, Tarka → entropy). The planning decision is: **these are hypotheses to test, not specs to implement.**

The motor layer serves dual purpose in this directive: it is the output encoding system (reverse transduction) AND the experimental apparatus for testing limb-to-feature mappings. The biological precedent is **reafference** — sensory-motor systems develop in tandem because the feedback loop between them calibrates both. You cannot develop accurate sensing without producing output and measuring what comes back.

Since the conscious layer is not yet implemented, motor operates at the **signal level** — restructuring text structurally rather than generating semantic content. This is sufficient for round-trip calibration.

Read `PLANNING_LOG.md` at the repo root first — it contains full context on all active decisions including the motor-as-calibration-instrument rationale, limb-to-feature hypotheses, and the Hermetic provenance insight.

## Objective

Implement the motor/output system as a signal-level text restructuring engine that reads orientational field weights, implement round-trip test infrastructure (motor output → sensory input → measure delta), and add calibration test scaffolding that varies individual limb weights and records which signal features respond.

## Part A: Motor System Implementation

### A1: Replace motor stub in `src/agenetic/systems/motor.py`

The motor system is reverse transduction. Where sensory extracts signal features FROM text, motor adjusts text TO target signal profiles shaped by the orientational field.

**Relationship to information:** Translates. Converts internal states into appropriate external form.

**Tick rate:** Fires on demand (when there's something to express — conscious output or reflex path).

**Input:** The motor system receives `SystemState` containing at minimum:
- `signal_report` (from sensory — the input's signal profile)
- `field` (the orientational field — limb weights shape output)
- `input` (the original text to restructure)
- Optionally: `subconscious_output` (for cached pattern info)

**Output:** Motor produces a `MotorOutput` (new type — see Part B) containing:
- `output_text`: the restructured text
- `target_profile`: the signal feature values motor was aiming for (derived from field weights)
- `strategies_applied`: list of which restructuring strategies fired

**Signal-level restructuring strategies:**

Motor should implement at least the following text restructuring operations, each governed by specific limb weights from the orientational field:

1. **Density modulation** — Adjust character density by expanding or compressing text. Higher density = more compact expression. Lower density = more spacious, padded output. Governed by overall field activation level (mean of weights).

2. **Entropy modulation** — Adjust vocabulary richness. Higher entropy target = more varied word choice, synonym substitution, less repetition. Lower entropy = more repetitive, constrained vocabulary. Candidate limb: Tarka (discerning resonance — more Tarka = more variety in expression).

3. **Coherence modulation** — Adjust sentence-to-sentence similarity. Higher coherence = sentences share more vocabulary, tighter thematic threading. Lower coherence = more disjoint, associative. Candidate limb: Samatvam (harmonic tone — more Samatvam = more coherent output).

4. **Impedance modulation** — Adjust structural complexity. Higher impedance = mixed formats, nested structures, non-ASCII. Lower impedance = clean, simple, uniform structure. Candidate limb: Nivṛtti (sacred pause — more Nivṛtti = lower impedance, simpler output).

5. **Periodicity modulation** — Adjust repetitive structural patterns. Higher periodicity = more repeated bigrams, rhythmic phrasing. Lower periodicity = less structural repetition. Candidate limb: Prakāśa (perception — more Prakāśa = less forced pattern, more natural flow).

6. **Noise floor modulation** — Adjust proportion of low-information tokens. Governed by overall field coherence.

Each strategy should:
- Read the relevant limb weight(s) from `state['field']` via `OrientationalField.read()`
- Compute a target value for the corresponding signal feature
- Apply text transformations to move the output toward that target
- Be independently toggleable (some strategies may be disabled for calibration isolation)

**Repair check:** Does the output text still preserve the informational content of the input? Has restructuring distorted meaning beyond recognition? Compare input and output signal reports — if delta exceeds a threshold, flag degradation.

**Apoptotic trigger:** Motor cannot produce output that passes repair check after max retries. Or: input is empty/None.

### A2: Motor design constraints

- Motor is Python-native. No LLM calls. Signal-level operations only.
- Motor must be deterministic given the same input + field state (for reproducible calibration).
- Motor must work with the existing `BaseSystem` interface: `process()`, `repair_check()`, `apoptotic_condition()`, `tick_rate`.
- Motor should NOT modify the orientational field, immune log, or signal pattern cache. It is output-only.
- Motor reads from the field via `OrientationalField.read()` — the existing sleep-only write enforcement remains.

## Part B: New Types

### B1: Add `MotorOutput` to `src/agenetic/systems/base.py`

Add a new TypedDict:

```python
class MotorOutput(TypedDict):
    output_text: str
    target_profile: SignalFeatures  # what motor was aiming for
    strategies_applied: list[str]   # which restructuring strategies fired
    repair_passed: bool             # did output pass motor's own repair check
```

### B2: Extend `SystemState` in `base.py`

Add `motor_output: MotorOutput` as an optional field in `SystemState` (following the same pattern as `signal_report`, `threat_assessment`, `subconscious_output`).

## Part C: Round-Trip Test Infrastructure

### C1: Create `tests/test_round_trip.py`

This is the calibration apparatus. It implements the motor→sensory feedback loop:

1. Take input text
2. Run through sensory → get signal report A
3. Run through motor (with given field state) → get restructured text
4. Run restructured text through sensory → get signal report B
5. Compare signal reports A and B → compute feature deltas

The test file should include:

**Round-trip utility function:**
```python
def round_trip(input_text: str, field: OrientationalField) -> dict:
    """Run motor output back through sensory and measure delta."""
    # sensory on original input
    # motor restructures with field weights
    # sensory on motor output
    # return both signal reports + delta
```

**Basic round-trip tests:**
- Motor output produces valid text (not empty, not None)
- Motor output produces measurably different signal features than input (motor actually does something)
- Motor output fed back through sensory produces a valid signal report (round-trip completes without error)
- Motor repair check flags when output diverges too far from input

**Calibration test scaffolding:**
- A parameterized test that varies a single limb weight while holding all others constant
- Measures which signal features shift in response
- Does NOT assert specific mappings (those are hypotheses to evaluate, not specs to enforce)
- Records results in a structured format: `{limb_name: str, weight_value: float, feature_deltas: dict[str, float]}`

The calibration tests should be runnable as a suite that produces a summary table:

```
Limb varied    | density_Δ | entropy_Δ | coherence_Δ | periodicity_Δ | noise_Δ | impedance_Δ
---------------|-----------|-----------|-------------|---------------|---------|------------
Prakāśa (0→1)  |    ...    |    ...    |     ...     |      ...      |   ...   |     ...
Tarka (0→1)    |    ...    |    ...    |     ...     |      ...      |   ...   |     ...
...
```

This table is the experimental output that the planning instance will analyze to validate or reject limb-to-feature mapping hypotheses.

### C2: Weight variation helper

Create a utility (can be in the test file or in `src/agenetic/field/`) that:
- Takes the current orientational field
- Sets a single limb to a specified weight value while holding all others at a baseline (1.0 for now, 0.5 when we migrate)
- Returns the modified field

This enables isolated limb testing without manually constructing field states.

## Part D: Graph Wiring Update

### D1: Wire motor into the LangGraph graph

Motor should now appear in the graph routing. Update `src/agenetic/network/` to:
- Add motor as a real node (not a stub pass-through)
- Motor fires on the reflex path (subconscious → motor when escalation=False)
- Motor fires after conscious (conscious → motor when escalation=True, though conscious is still a stub)
- Motor output is stored in `SystemState['motor_output']`

The existing routing logic should remain: sensory → immune → subconscious → conditional (escalate → conscious → motor, else → motor).

## Part E: Documentation Updates

### E1: Update README.md

In the "Current Status" section of README.md, update the status to reflect motor implementation:

- Add motor to the list of implemented systems (sensory, immune, subconscious, motor)
- Update test count to whatever the new total is after this directive
- Add a line about the round-trip calibration infrastructure
- In the "Conscious, motor, sleep, and genetic remain stubs" sentence, remove "motor" from the stubs list

### E2: Append DEVLOG.md entry

Append the following entry to DEVLOG.md:

```markdown
## 2026-02-08 — Directive 004: Motor Layer with Round-Trip Calibration

**Commit:** [agent fills in]
**Tests:** [agent fills in — expected: 136 existing + new motor + round-trip tests]

Implemented the motor/output system as a signal-level text restructuring engine. Motor is reverse transduction — where sensory extracts signal features FROM text, motor adjusts text TO target signal profiles shaped by orientational field limb weights.

Six restructuring strategies implemented, each governed by specific limb weights:
- Density modulation (overall field activation)
- Entropy modulation (candidate: Tarka)
- Coherence modulation (candidate: Samatvam)
- Impedance modulation (candidate: Nivṛtti)
- Periodicity modulation (candidate: Prakāśa)
- Noise floor modulation (overall field coherence)

Built round-trip test infrastructure: motor output → sensory → measure feature delta. This enables empirical testing of limb-to-feature mappings. Calibration test scaffolding varies individual limb weights and records which signal features respond.

The motor layer is both an output system and a calibration instrument. The biological precedent is reafference — sensory-motor systems develop in tandem because the feedback loop calibrates both. Limb-to-feature mappings from `references/conceptual_archaeology.md` Section V are treated as hypotheses to test, not specs to implement.

Motor is Python-native, deterministic, signal-level only (no LLM calls). Wired into LangGraph graph on both reflex and escalation paths.
```

### E3: Replace PLANNING_LOG.md

Replace `PLANNING_LOG.md` at the repo root with the version included in this directive's commit. The updated log contains new sections on motor-as-calibration-instrument, limb-to-feature hypotheses, Hermetic provenance of the seven-layer pattern, and revised sequencing rationale.

## Scope Boundaries

**DO:**
- Replace motor stub with working signal-level restructuring implementation
- Add `MotorOutput` type and extend `SystemState`
- Create round-trip test infrastructure with calibration scaffolding
- Add weight variation utility for isolated limb testing
- Wire motor into the LangGraph graph on both reflex and escalation paths
- Update README.md status section
- Append DEVLOG.md entry
- Replace PLANNING_LOG.md with provided version
- Run all tests (existing 136 + new) and report results
- Git commit and push

**DO NOT:**
- Implement the conscious layer (still a stub)
- Implement the sleep layer
- Modify the orientational field write access rules (sleep-only remains)
- Modify existing sensory, immune, or subconscious implementations
- Modify existing signal report types (SignalFeatures, SignalClassification, SignalDelta)
- Edit historical handoff files (001_, 002_, 003_)
- Make motor non-deterministic (must be reproducible for calibration)
- Assert specific limb-to-feature mappings in tests (hypotheses, not specs)
- Call any LLM APIs from motor

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/motor.py` | Replaced (stub → implementation) |
| `src/agenetic/systems/base.py` | Updated (MotorOutput type, SystemState extension) |
| `src/agenetic/network/` | Updated (motor wired into graph) |
| `tests/test_round_trip.py` | Created |
| `tests/test_motor.py` | Created (unit tests for motor system) |
| `README.md` | Updated (status section) |
| `DEVLOG.md` | Updated (new entry appended) |
| `PLANNING_LOG.md` | Replaced (full update from planning instance) |
| `handoff/004_directive.md` | This file |
| `handoff/004_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `src/agenetic/systems/motor.py` implements `BaseSystem` interface with `process()`, `repair_check()`, `apoptotic_condition()`, `tick_rate`
- [ ] Motor reads orientational field weights and produces text restructured toward target signal profile
- [ ] Motor is deterministic (same input + same field = same output)
- [ ] Motor does not write to orientational field, immune log, or signal pattern cache
- [ ] `MotorOutput` TypedDict exists in `base.py` with `output_text`, `target_profile`, `strategies_applied`, `repair_passed`
- [ ] `SystemState` includes optional `motor_output` field
- [ ] `tests/test_round_trip.py` exists with round-trip utility function
- [ ] Round-trip test: motor output fed back through sensory produces valid signal report
- [ ] Calibration scaffolding: parameterized test varies single limb weight, records feature deltas
- [ ] Calibration does NOT assert specific limb-to-feature mappings
- [ ] Weight variation utility exists (set one limb, hold others at baseline)
- [ ] Motor is wired into LangGraph graph on reflex path (subconscious → motor)
- [ ] Motor is wired into LangGraph graph on escalation path (conscious → motor)
- [ ] All existing 136 tests still pass
- [ ] New motor unit tests pass
- [ ] New round-trip tests pass
- [ ] README.md status section updated (motor no longer listed as stub, test count updated)
- [ ] DEVLOG.md has Directive 004 entry appended
- [ ] PLANNING_LOG.md replaced with updated version
- [ ] No historical handoff files edited
- [ ] Git commit and push completed
