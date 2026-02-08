# DNAgent Response — Directive 007

**Status:** Complete
**Tests:** 237 passing (42 new, 195 existing)

## What Was Built

Extended the motor from 6 strategies to 10, rewrote Tarka entropy, and ran a full two-point calibration sweep.

### Part A: Tarka Entropy Rewrite

Replaced token-level entropy modulation with sentence-level restructuring:
- **Increase entropy:** Split sentences at commas and conjunctions, capitalize new sentence starts, add periods
- **Decrease entropy:** Merge short sentences (≤8 words) with rotating connectives ("and", "which", "where", "while"), lowercase merged beginnings

**Honest result:** The sentence-level approach fires correctly and preserves repair check compliance, but does not produce distinguishable entropy values in the calibration sweep. Both Tarka=0.0 and Tarka=0.5 show zero feature deltas relative to baseline. The strategy modifies the text (entropy_modulation appears in strategies_applied) but the sensory system measures similar entropy for the restructured text. This may require a fundamentally different measurement approach, or Tarka's signal-level expression is inherently weak.

### Part B: Five New Strategies

1. **Śraddhā → noise_floor** (B1): Reassigned noise_floor from mean weight to Śraddhā (limb 5). `noise_floor = (1.0 - sraddha_w) * 0.3`. **Confirmed in calibration:** +0.0541 noise_floor delta at 0.0.

2. **Māyāvāda → transformation cap** (B2): Post-processing constraint. After all 6 feature strategies, measures `transform_magnitude = 1.0 - token_overlap_ratio`. If magnitude exceeds `1.0 - mayavada_w`, blends output back toward original. Active when `mayavada_w < 0.95`. **Not visible in calibration** — cap inactive at default weight 1.0, which is expected.

3. **Ārēka → suppression gate** (B3): Binary gate applied before other strategies. If `areka_w > 0.8` AND `noise_floor > 0.3` AND `entropy > 5.0`, suppresses output entirely (empty string, repair_passed=True). **Not visible in calibration** — calibration text is clean (low noise, moderate entropy), so gate doesn't fire. Works correctly in unit tests with noisy input.

4. **Svadharma → threshold scaling** (B4): Meta-strategy. `threshold_scale = 0.5 + svadharma_w`. All 6 feature strategy thresholds are multiplied by this scale. At 1.0: 1.5× (more selective). At 0.0: 0.5× (less selective). **No direct feature delta** — second-order effect on which strategies fire.

5. **Kṣetra-Jñāna → delta scaling** (B5): Meta-strategy. `delta_scale = 0.5 + ksetra_w * 0.5`. All deltas between target and current are scaled. At 1.0: 1.0 (full sensitivity). At 0.0: 0.5 (half sensitivity). **Confirmed second-order effects:** At 0.0, only coherence_modulation fires (other deltas fall below scaled thresholds), producing coherence +0.0854 and periodicity −0.0588.

### Part C: Target Profile Update

- `noise_floor` now uses `(1.0 - sraddha_w) * 0.3` instead of `(1.0 - mean_w) * 0.3`
- Added `sraddha_w = _get_limb_weight(field_state, SRADDHA_ID)` to profile computation

### Part D: Type Update

- Added `transform_magnitude: float` to `MotorOutput` TypedDict in base.py
- All motor output paths now include transform_magnitude (empty input: 0.0, suppression: 1.0, normal: computed, fallback: 0.0)

### Part E: Unit Tests (24 new in test_motor.py)

| Test class | Count | Coverage |
|---|---|---|
| TestTarkaSentenceLevel | 3 | Increase, decrease, round-trip measurable change |
| TestSraddhaNoise | 3 | Target changes, low=noisy, high=clean |
| TestMayavadaCap | 5 | Zero allows transform, near-one constrains, at-one inactive, magnitude reported, constrained vs unconstrained |
| TestArekaGate | 4 | High-noise suppressed, normal passes, zero never suppresses, suppression is repair_passed |
| TestSvadharmaSelectivity | 3 | Low=more strategies, high=fewer, default unchanged |
| TestKsetraJnanaSensitivity | 3 | Low=less responsive, high=more, default unchanged |
| TestNewStrategyIntegration | 3 | Determinism, multi-strategy interaction, empty input |

### Part F: Calibration Sweep

Two-point sweep (0.0 and 0.5) across all 18 limbs. 18 new parameterized tests (TestCalibrationSweepHalf). Summary test prints both tables with strategy lists.

**Key findings:**

| Category | Limbs | Count |
|---|---|---|
| Apparatus-confirmed | Prakāśa, Nivṛtti, Samatvam, Śraddhā, Kṣetra-Jñāna | 5 |
| Implemented, not registering | Tarka, Māyāvāda, Ārēka, Svadharma | 4 |
| Convergent cluster | Bodhi, Mirror, Ajāti, Asparśa, Rest | 5 |
| Semantic-domain only | Vishvarūpa, No-Position, Fourfold State | 3 |
| Uncategorized | Ātma-Vichāra | 1 |

**Graded vs binary:** Samatvam is graded (−0.0263 at 0.0, 0.0 at 0.5). Prakāśa, Nivṛtti, Śraddhā, Kṣetra-Jñāna show same deltas at both 0.0 and 0.5 — binary response (strategy fires or doesn't, no proportional scaling).

### Part G: Documentation

- `planning/CURRENT.md`: Rewritten from repo inspection with motor strategy inventory and calibration summary
- `DEVLOG.md`: Appended Directive 007 entry with full calibration table
- `README.md`: Updated motor description (10 strategies) and test count (237)

### Part H: Planning State

- `handoff/state.md` → `planning/007_motor_extension.md`

## Files Modified

| File | Lines | Action |
|---|---|---|
| `src/agenetic/systems/motor.py` | 661 (+198) | 5 new constants, Tarka rewrite, 2 helper functions, process() rewrite with Ārēka/Svadharma/Kṣetra-Jñāna/Māyāvāda |
| `src/agenetic/systems/base.py` | 224 (+1) | Added transform_magnitude to MotorOutput |
| `tests/test_motor.py` | 490 (+184) | 24 new tests across 7 new test classes |
| `tests/test_round_trip.py` | 338 (+39) | TestCalibrationSweepHalf class, two-point summary |
| `planning/CURRENT.md` | 75 | Rewritten from repo inspection |
| `planning/007_motor_extension.md` | 65 | Copied from state.md |
| `DEVLOG.md` | 204 (+37) | Appended Directive 007 entry |
| `README.md` | 104 | Updated strategy count and test count |
| `handoff/007_response.md` | — | This file |

## Verification Checklist

- [x] `handoff/state.md` copied to `planning/007_motor_extension.md`
- [x] Tarka entropy modulation uses sentence-level approach (not token replacement)
- [x] Tarka does NOT produce measurable signal in calibration — honest report above
- [x] Śraddhā governs noise_floor directly (not mean weight)
- [x] Māyāvāda constrains transformation magnitude as post-processing step
- [x] Ārēka suppresses output for high-noise high-entropy input when weight > 0.8
- [x] Ārēka suppression treated as valid outcome, not repair failure
- [x] Svadharma scales strategy thresholds dynamically
- [x] Kṣetra-Jñāna scales delta sensitivity
- [x] New limb ID constants added (SRADDHA_ID, MAYAVADA_ID, AREKA_ID, SVADHARMA_ID, KSETRA_JNANA_ID)
- [x] `_compute_target_profile()` updated for Śraddhā
- [x] All new strategies are deterministic (no randomness)
- [x] All new strategies are Python-native (no LLM calls)
- [x] New strategies do not write to orientational field, immune log, or cache
- [x] Unit tests for each new strategy (24 new tests)
- [x] Calibration sweep runs at both 0.0 and 0.5 weight points
- [x] Full sweep table printed in test output
- [x] Calibration does NOT assert specific mappings (record only)
- [x] All 237 tests pass
- [x] `planning/CURRENT.md` updated from repo inspection
- [x] `DEVLOG.md` has Directive 007 entry with sweep results
- [x] `README.md` updated (strategy count, test count)
