# Directive 013 — Motor Codec Refactor: Extract TextCodec, Define Codec Interface

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-10

## Context

Read these files first, in this order:
1. `planning/CURRENT.md` — factual snapshot of where things stand
2. `CLAUDE.md` — project conventions, agent roles, directive protocol
3. `docs/ARCHITECTURE.md` — the v2 specification (especially Motor System section)
4. `docs/architecture_amendment.md` — the signal-semantics boundary
5. `src/agenetic/systems/motor.py` — the current motor system (~620 LOC, what this directive refactors)
6. `src/agenetic/systems/base.py` — shared types including MotorOutput
7. `tests/test_motor.py` — 58 motor unit tests (must all pass unchanged)
8. `tests/test_round_trip.py` — 44 round-trip tests (must all pass unchanged)
9. `planning/012_prompt_assembly.md` — previous directive's design decisions

**What happened before this directive:**

Directives 001–010 built the complete signal domain: sensory, immune, subconscious, motor, orientational field, graph routing, round-trip calibration. 238 tests. Directives 011–012 built the conscious layer foundation: ConsciousOutput type, proceed/suppress gate, Deliberator protocol, Anthropic API deliberator, graduated prompt assembly with limb interactions and observation harness. 292 tests.

The motor system (~620 LOC) currently contains everything inline in a single file:
- 6 signal-feature modulation functions (_modulate_density, _modulate_entropy, _modulate_coherence, _modulate_impedance, _modulate_periodicity, _modulate_noise_floor)
- 2 utility functions (_compute_transform_magnitude, _blend_toward_original)
- Ārēka suppression gate (pre-strategy)
- Māyāvāda transformation cap (post-strategy)
- Svadharma threshold scaling and Kṣetra-Jñāna delta scaling (modifiers)
- MotorSystem class with process(), _check_output_quality(), repair_check(), apoptotic_condition()

This works but has a structural limitation: all text restructuring logic lives directly in motor.py's process() method. When Directive 014 wires motor to consume ConsciousOutput (rendering semantic decisions into signal-level output), motor needs to select HOW to render. A codec architecture lets motor delegate the "how" to a swappable codec while keeping orchestration (field reading, strategy selection, repair check) in MotorSystem.

**This directive is pure restructuring.** The TextCodec produces byte-identical output for the same inputs. All 292 existing tests pass unchanged. No new behavior, no new features. The value is architectural: motor gains the codec interface before 014 adds ConsciousOutput consumption.

**What this directive does NOT do:**
- Does NOT change motor behavior (every input/output pair is identical before and after)
- Does NOT add ConsciousOutput consumption (that's 014)
- Does NOT modify conscious.py, deliberator.py, prompt_assembly.py, or any conscious-layer code
- Does NOT modify sensory.py, immune.py, subconscious.py
- Does NOT modify the orientational field
- Does NOT change graph routing
- Does NOT change base.py types

## Objective

Extract motor's text restructuring logic into a TextCodec class behind a Codec protocol. MotorSystem delegates to the codec for text transformation while retaining orchestration (field reading, repair checking, apoptotic tracking). All existing tests pass unchanged — this is a pure refactor with zero behavior change.

## Part A: Define Codec Protocol

### A1: Create `src/agenetic/systems/codec.py`

Define the Codec protocol — the interface any output codec must satisfy.

```python
"""Codec protocol — interface for motor output encoding.

A Codec transforms input data toward a target signal profile.
TextCodec is the first implementation (text restructuring).
Future codecs could handle audio, visual, or other modalities.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from agenetic.systems.base import SignalFeatures


@runtime_checkable
class Codec(Protocol):
    """Protocol for motor output codecs.
    
    A codec takes input data, current signal features, a target profile,
    and field state, then produces transformed output with metadata.
    """

    @property
    def name(self) -> str:
        """Codec identifier (e.g., 'text', 'audio')."""
        ...

    def encode(
        self,
        input_data: str,
        current_features: SignalFeatures,
        target_profile: SignalFeatures,
        field_state: dict,
    ) -> "CodecResult":
        """Transform input toward target profile.
        
        Returns CodecResult with transformed output and metadata.
        """
        ...

    def quality_check(self, original: str, output: str) -> bool:
        """Verify output preserves content adequately."""
        ...
```

Also define the CodecResult type in the same file:

```python
from typing import TypedDict


class CodecResult(TypedDict):
    """Result of a codec encode operation."""
    output: str
    strategies_applied: list[str]
    transform_magnitude: float
```

### A2: Important design notes

The Codec protocol is deliberately minimal:
- `encode()` takes all context needed to produce output
- `quality_check()` is separated from encode so MotorSystem can decide when/whether to check
- `field_state` is passed through so codecs can read limb weights for their own gates (Ārēka, Māyāvāda, etc.)
- The protocol uses `runtime_checkable` for the same reason Deliberator does — structural typing, swappable implementations

## Part B: Create TextCodec

### B1: Create `src/agenetic/systems/text_codec.py`

Move ALL text restructuring logic from motor.py into TextCodec:

**Functions to move (unchanged):**
- `_modulate_density()`
- `_modulate_entropy()`
- `_modulate_coherence()`
- `_modulate_impedance()`
- `_modulate_periodicity()`
- `_modulate_noise_floor()`
- `_compute_transform_magnitude()`
- `_blend_toward_original()`

These remain module-level functions (not methods), unchanged in implementation. They're internal to text_codec.py.

**TextCodec class:**

```python
class TextCodec:
    """Text restructuring codec — signal-level text transformation.
    
    Implements the Codec protocol for text output. Restructures text
    toward target signal profiles using six feature modulation strategies,
    governed by Ārēka suppression, Māyāvāda cap, Svadharma threshold
    scaling, and Kṣetra-Jñāna delta scaling.
    
    This is a pure extraction from MotorSystem.process() — identical
    behavior, new home.
    """

    @property
    def name(self) -> str:
        return "text"

    def encode(
        self,
        input_data: str,
        current_features: SignalFeatures,
        target_profile: SignalFeatures,
        field_state: dict,
    ) -> CodecResult:
        """Apply text restructuring strategies toward target profile."""
        # All the logic currently in MotorSystem.process() between
        # "Get current features" and "Repair check" moves here.
        # This includes:
        # - Ārēka suppression gate
        # - Svadharma threshold scaling
        # - Kṣetra-Jñāna delta scaling
        # - 6 feature modulation calls
        # - Māyāvāda transformation cap
        # Returns CodecResult (not MotorOutput — MotorSystem wraps it).
        ...

    def quality_check(self, original: str, output: str) -> bool:
        """Check text restructuring preserved content adequately.
        
        Moved from MotorSystem._check_output_quality() — same logic.
        """
        ...
```

**Critical: The encode() method must produce identical output to the current MotorSystem.process() for the same inputs.** This means:

1. Same strategy ordering (density → entropy → coherence → impedance → periodicity → noise_floor)
2. Same Ārēka suppression check (before strategies)
3. Same Svadharma/Kṣetra-Jñāna scaling (same formulas)
4. Same Māyāvāda cap (after strategies)
5. Same threshold values
6. Same delta computations

The only difference: encode() returns `CodecResult` (output, strategies_applied, transform_magnitude) instead of `MotorOutput`. MotorSystem wraps the CodecResult into MotorOutput.

### B2: What stays in motor.py

MotorSystem retains:
- `__init__()` — now also creates a TextCodec instance
- `process()` — orchestration: read field, compute target, delegate to codec, build MotorOutput, repair check, apoptotic tracking
- `repair_check()` — unchanged
- `apoptotic_condition()` — unchanged
- `_to_str()` helper — stays in motor.py (input coercion is motor's job, not the codec's)

MotorSystem.process() becomes roughly:

```python
def process(self, state: SystemState) -> SystemState:
    raw_input = state["input"]
    field_state = state["field"]
    signal_report = state.get("signal_report")
    text = _to_str(raw_input)
    
    # Compute target profile from field weights.
    target = _compute_target_profile(field_state)
    
    # Handle empty input (unchanged).
    if not text:
        # ... same empty-input handling ...
    
    # Get current features (unchanged).
    if signal_report is not None:
        current = signal_report["features"]
    else:
        current = { ... }  # same neutral defaults
    
    # Delegate to codec.
    result = self._codec.encode(text, current, target, field_state)
    
    # Repair check (delegates to codec's quality_check).
    repair_passed = self._codec.quality_check(text, result["output"])
    
    if not repair_passed:
        self._consecutive_repair_failures += 1
        output_text = text
        strategies = ["fallback_to_original"]
        transform_magnitude = 0.0
    else:
        self._consecutive_repair_failures = 0
        output_text = result["output"]
        strategies = result["strategies_applied"]
        transform_magnitude = result["transform_magnitude"]
    
    motor_output = {
        "output_text": output_text,
        "target_profile": target,
        "strategies_applied": strategies,
        "repair_passed": repair_passed,
        "transform_magnitude": transform_magnitude,
    }
    return {**state, "motor_output": motor_output}
```

This is structurally identical to current behavior — the codec encapsulates the same logic that was inline.

## Part C: Tests

### C1: New tests in `tests/test_codec.py`

Structural tests for the codec protocol and TextCodec. All deterministic, no LLM.

**Protocol tests (3):**

1. **test_text_codec_satisfies_protocol**: `isinstance(TextCodec(), Codec)` is True.
2. **test_text_codec_name**: `TextCodec().name == "text"`.
3. **test_codec_result_structure**: Call `TextCodec().encode()` with simple input → result has keys "output", "strategies_applied", "transform_magnitude".

**Equivalence tests (4):**

These are the critical tests — they verify the refactor didn't change behavior.

4. **test_encode_matches_old_density**: Input with known density mismatch. TextCodec.encode() output matches what the old inline MotorSystem would have produced. (Compare against a hardcoded expected output, or run both paths and compare.)
5. **test_encode_matches_old_entropy**: Same pattern for entropy modulation.
6. **test_encode_areka_suppression**: Input with high noise + high entropy + Ārēka weight > 0.3 → codec returns empty output with "areka_suppression" strategy.
7. **test_encode_mayavada_cap**: Input where Māyāvāda weight < 0.45 → codec applies blending cap, transform_magnitude is reduced.

**Quality check tests (2):**

8. **test_quality_check_passes**: Normal input/output pair → True.
9. **test_quality_check_fails_empty_output**: Empty output → False.

**Motor delegation tests (3):**

10. **test_motor_uses_text_codec**: `MotorSystem()._codec` is an instance of TextCodec.
11. **test_motor_process_unchanged**: Run MotorSystem.process() with known inputs, verify output is identical to a pre-recorded expected output. This is the ultimate equivalence check.
12. **test_motor_repair_delegates_to_codec**: Verify motor's repair path uses codec.quality_check().

### C2: Total new test count

12 new tests in `test_codec.py`.

### C3: Existing tests MUST NOT be modified

All 58 tests in test_motor.py and 44 tests in test_round_trip.py must pass unchanged. These are the behavioral equivalence guarantee — if the refactor changed any behavior, these tests catch it.

## Part D: Planning State Management

### D1: Copy State to Planning Entry

Copy `handoff/state.md` to `planning/013_motor_codec.md`.

### D2: Update CURRENT.md from Repo Inspection

After all code changes are complete and tests pass, update `planning/CURRENT.md` by inspecting the actual repo state. Rebuild from ground truth.

## Part E: Documentation Updates

### E1: DEVLOG Entry

Add entry for Directive 013. Format: date, directive number, commit hash, test count, prose summary: codec protocol, TextCodec extraction, zero behavior change, architectural preparation for 014.

### E2: README Status Update

Update README.md: Motor system description should mention codec architecture. Update test count.

## Scope Boundaries

**DO:**
- Create `src/agenetic/systems/codec.py` with Codec protocol and CodecResult type
- Create `src/agenetic/systems/text_codec.py` with TextCodec class and all moved modulation functions
- Refactor `src/agenetic/systems/motor.py` to delegate to TextCodec
- Create `tests/test_codec.py` with 12 structural and equivalence tests
- Update DEVLOG.md, README.md, CURRENT.md
- Copy state.md to planning entry

**DO NOT:**
- Change any motor behavior (byte-identical outputs for same inputs)
- Modify any existing test files (test_motor.py, test_round_trip.py, test_conscious.py, etc.)
- Modify conscious.py, deliberator.py, prompt_assembly.py, deliberator_anthropic.py
- Modify sensory.py, immune.py, subconscious.py
- Modify base.py (no type changes)
- Modify graph.py (no routing changes)
- Modify the orientational field
- Edit any historical handoff files (001–012)
- Add ConsciousOutput consumption to motor (that's 014)

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/codec.py` | Created — Codec protocol + CodecResult type |
| `src/agenetic/systems/text_codec.py` | Created — TextCodec class + all modulation functions moved from motor.py |
| `src/agenetic/systems/motor.py` | Updated — delegates to TextCodec, orchestration only |
| `tests/test_codec.py` | Created — 12 structural and equivalence tests |
| `handoff/state.md` | Provided — planning notes for this cycle |
| `planning/013_motor_codec.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `DEVLOG.md` | Updated — Directive 013 entry |
| `README.md` | Updated — motor description, test count |
| `handoff/013_directive.md` | This file |
| `handoff/013_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `src/agenetic/systems/codec.py` exists with Codec protocol (runtime_checkable) and CodecResult TypedDict
- [ ] Codec protocol has: name property, encode() method, quality_check() method
- [ ] `src/agenetic/systems/text_codec.py` exists with TextCodec class
- [ ] All 6 modulation functions moved from motor.py to text_codec.py (unchanged implementation)
- [ ] `_compute_transform_magnitude()` moved to text_codec.py
- [ ] `_blend_toward_original()` moved to text_codec.py
- [ ] TextCodec.encode() contains: Ārēka gate, Svadharma/Kṣetra-Jñāna scaling, 6 feature modulations, Māyāvāda cap
- [ ] TextCodec.quality_check() contains logic from old `_check_output_quality()`
- [ ] TextCodec satisfies Codec protocol (`isinstance(TextCodec(), Codec)` is True)
- [ ] `motor.py` creates TextCodec in __init__
- [ ] `motor.py` process() delegates to self._codec.encode() and self._codec.quality_check()
- [ ] `motor.py` retains: __init__, process (orchestration), repair_check, apoptotic_condition, _to_str
- [ ] `motor.py` no longer contains modulation functions or _compute_transform_magnitude or _blend_toward_original
- [ ] All 12 codec tests pass
- [ ] All 58 test_motor.py tests pass UNCHANGED
- [ ] All 44 test_round_trip.py tests pass UNCHANGED
- [ ] All 292 existing tests pass (no regressions anywhere)
- [ ] No modifications to conscious.py, deliberator.py, prompt_assembly.py, deliberator_anthropic.py
- [ ] No modifications to sensory.py, immune.py, subconscious.py
- [ ] No modifications to base.py, graph.py
- [ ] No modifications to orientational field
- [ ] No historical handoff files edited
- [ ] `handoff/state.md` copied to `planning/013_motor_codec.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection
- [ ] DEVLOG.md entry added
- [ ] README.md updated
- [ ] Git commit and push completed
