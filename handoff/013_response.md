# Directive 013 Response — Motor Codec Refactor

**Status:** Complete
**Tests:** 304 passing + 2 skipped (was 292, +12 codec tests)
**Commit:** fea3fbc

## What Was Done

### Part A — Codec Protocol (`src/agenetic/systems/codec.py`, ~55 LOC)

Created `Codec` — a `runtime_checkable Protocol` with:
- `name` property (str)
- `encode(input_data, current_features, target_profile, field_state) -> CodecResult`
- `quality_check(original, output) -> bool`

Created `CodecResult` TypedDict: `output`, `strategies_applied`, `transform_magnitude`.

Mirrors the Deliberator pattern from the conscious layer — structural typing, swappable implementations.

### Part B — TextCodec + Motor Refactor

**`src/agenetic/systems/text_codec.py` (~430 LOC)**

Moved from motor.py without modification:
- 6 modulation functions: `_modulate_density`, `_modulate_entropy`, `_modulate_coherence`, `_modulate_impedance`, `_modulate_periodicity`, `_modulate_noise_floor`
- `_compute_transform_magnitude`
- `_blend_toward_original`

TextCodec class wraps these into the Codec protocol:
- `encode()` runs the full strategy pipeline: Areka suppression gate -> Svadharma/Ksetra-Jnana scaling -> 6 feature modulations -> Mayavada cap
- `quality_check()` contains old `_check_output_quality()` logic

**`src/agenetic/systems/motor.py` (~165 LOC, down from ~620)**

MotorSystem is now orchestrator only:
- Creates `self._codec = TextCodec()` in `__init__`
- `process()` reads field, computes target, delegates to `self._codec.encode()`, checks quality via `self._codec.quality_check()`
- Retains: `_to_str()`, empty-input handling, repair failure tracking, `repair_check()`, `apoptotic_condition()`
- Re-exports moved functions for backward compatibility (test_motor.py imports them from motor.py)

**Areka suppression fix:** Old code returned early before quality check when Areka fired. After refactor, codec returns empty output which then failed quality_check. Fixed by checking for `"areka_suppression"` in strategies_applied before quality check, returning early with `repair_passed=True`.

### Part C — Codec Tests (`tests/test_codec.py`, 12 tests)

| Group | Tests | What |
|-------|-------|------|
| Protocol | 3 | isinstance(TextCodec(), Codec), name=="text", CodecResult structure |
| Equivalence | 4 | density modulation, entropy modulation, Areka suppression, Mayavada cap boundary |
| Quality check | 2 | normal passes, empty fails |
| Motor delegation | 3 | uses TextCodec, process() unchanged, repair delegates to codec |

### Part D — Documentation

- `planning/013_motor_codec.md` — copied from state.md
- `planning/CURRENT.md` — rebuilt from repo inspection
- `DEVLOG.md` — D013 entry appended
- `README.md` — motor description updated, test count 292->304

## Issues Encountered and Resolved

1. **Areka suppression path** — Empty output from codec failed quality_check, causing 2 test failures. Fixed by adding early return in motor.process() for areka_suppression strategy.

2. **Test input selection for equivalence tests** — SAMPLE_TEXT was too clean for density/entropy modulation to produce visible changes. Used purpose-built inputs: spacious text with extra whitespace for density, complex sentences with conjunctions for entropy.

3. **Mayavada cap test** — At mayavada_w=0.0, max_allowed=1.0, so cap never fires. Changed test to verify behavioral contract at mayavada_w=0.44 (cap active) vs 0.5 (cap inactive).

## Verification

- [x] All 304 tests pass (292 existing unchanged + 12 new)
- [x] 2 skipped (API tests, expected)
- [x] No import cycles
- [x] test_motor.py imports work via re-export
- [x] test_round_trip.py unchanged and passing
- [x] Zero behavior change — existing tests prove equivalence
- [x] `planning/CURRENT.md` rebuilt from repo inspection
- [x] DEVLOG.md entry added
- [x] README.md updated
- [x] Git commit and push completed (fea3fbc)

## Files Changed

| File | Action |
|------|--------|
| `src/agenetic/systems/codec.py` | Created — Codec protocol + CodecResult |
| `src/agenetic/systems/text_codec.py` | Created — TextCodec + all modulation functions |
| `src/agenetic/systems/motor.py` | Refactored — orchestrator only, delegates to codec |
| `tests/test_codec.py` | Created — 12 codec tests |
| `planning/013_motor_codec.md` | Created — copied from state.md |
| `planning/CURRENT.md` | Rebuilt from repo inspection |
| `DEVLOG.md` | D013 entry appended |
| `README.md` | Motor description + test count updated |
| `handoff/013_response.md` | This file |
