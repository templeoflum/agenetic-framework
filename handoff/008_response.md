# DNAgent — Directive 008 Response

**Directive:** 008 — Midpoint Weight Migration and Recalibration
**Status:** Complete
**Tests:** 237 passing (5 expectations updated, no tests added or removed)

## What Was Done

### Part A: Default Limb Weights → 0.5

Changed all 18 `"weight": 1.0` entries in `orientational.py` to `"weight": 0.5`. Also updated fallback defaults in motor helpers (`_get_limb_weight`, `_mean_weight`) from 1.0 to 0.5.

### Part B: Target Profile Formula Rebalancing

Adopted symmetric `target = base + (weight - 0.5) * scale` pattern for all six features:

- `density`: `0.8 + (mean_w - 0.5) * 0.4` — at 0.5 → 0.8
- `entropy`: `3.5 + (tarka_w - 0.5) * 3.0` — at 0.5 → 3.5
- `coherence`: `0.35 + (samatvam_w - 0.5) * 0.7` — at 0.5 → 0.35
- `periodicity`: `(0.5 - prakasa_w) * 0.6` — at 0.5 → 0.0
- `noise_floor`: `(0.5 - sraddha_w) * 0.6` — at 0.5 → 0.0
- `impedance`: `(0.5 - nivrtti_w) * 0.6` — at 0.5 → 0.0

Adjusted meta-strategy thresholds:
- Ārēka gate: `areka_w > 0.8` → `areka_w > 0.3`
- Māyāvāda cap: `mayavada_w < 0.95` → `mayavada_w < 0.45`

### Part C: Sensory Reference Signal

Changed fallback reference from 1.0 to 0.5 in `sensory.py` line 247. The mean-of-limb-weights computation already handles the change automatically when limbs are present, but the fallback for empty limb lists needed updating.

### Part D: Strategy Threshold Review

Reviewed all strategy thresholds. The existing thresholds (0.05 for feature modulators, 0.5 for entropy) work correctly at 0.5 midpoint because the symmetric formulas produce appropriate deltas. No threshold changes needed beyond Ārēka and Māyāvāda (covered in Part B).

### Part E: Test Fixes

5 expectations updated in `tests/test_motor.py::TestMotorHelpers`:
- `_get_limb_weight` found value: 1.0 → 0.5
- `_get_limb_weight` not-found fallback: 1.0 → 0.5
- `_mean_weight` default: 1.0 → 0.5
- `_mean_weight` empty fallback: 1.0 → 0.5
- `_compute_target_profile` coherence: 0.7 → 0.35

No tests removed. No tests weakened.

### Part F: Three-Point Calibration Sweep

Updated `tests/test_round_trip.py`:
- Changed `vary_single_limb` baseline default from 1.0 to 0.5
- Replaced `TestCalibrationSweepHalf` (at 0.5) with `TestCalibrationSweepFull` (at 1.0)
- Updated `test_calibration_summary` for three-point sweep (0.0, 0.5, 1.0) with baseline verification

**Baseline check passed:** All 18 limbs at 0.5 produce zero delta.

### Part G: Documentation

- `planning/CURRENT.md` updated from repo inspection
- `DEVLOG.md` — Directive 008 entry with formula comparison table and full calibration data
- `README.md` — updated orientational field description with midpoint model

### Part H: Planning State

`handoff/state.md` → `planning/008_midpoint_migration.md`

## Calibration Findings

### Confirmed mappings (same 5 as Directive 007):
1. **Prakāśa → periodicity** (+0.0912 at 0.0)
2. **Nivṛtti → impedance** (+0.3667 at 0.0)
3. **Samatvam → coherence** (−0.0263 at 0.0)
4. **Śraddhā → noise_floor** (+0.0541 at 0.0)
5. **Kṣetra-Jñāna → second-order** (strategies drop to zero at 0.0, producing coherence/periodicity shifts)

### Meta-strategy effects (newly visible):
- **Svadharma at 1.0**: threshold_scale = 1.5, causing all strategy thresholds to become too high → no strategies fire → same pattern as Kṣetra-Jñāna at 0.0
- **Kṣetra-Jñāna at 0.0**: delta_scale = 0.5, causing all deltas to halve → strategies don't fire → coherence/periodicity shift as second-order effect

### Key observation: asymmetric response
Suppression (0.0) produces more visible effects than amplification (1.0). Reason: baseline strategies (entropy_modulation, coherence_modulation) already fire at 0.5 because input features naturally diverge from targets. Suppression adds new strategies or changes deltas beyond what already fires. Amplification mostly intensifies existing behavior.

### Tarka still silent
Entropy modulation fires (appears in strategies_applied) but produces the same sensory-measured entropy after round-trip. This has been consistent across three attempts: token-level (D004), sentence-level (D007), and midpoint rebalance (D008). The signal-level entropy approach may have reached its limit — Tarka's expression may require semantic-level variety (word choice, concept diversity) rather than structural rearrangement.

## Verification Checklist

- [x] `handoff/state.md` copied to `planning/008_midpoint_migration.md`
- [x] All 18 limb weights default to 0.5 in orientational field
- [x] Motor target profile formulas produce reasonable targets at 0.5
- [x] At 0.5 default, motor produces output close to original input (minimal transformation)
- [x] Sensory reference signal works correctly at 0.5
- [x] Strategy thresholds reviewed and adjusted for 0.5 baseline
- [x] Māyāvāda activation threshold adjusted for 0.5 baseline
- [x] Ārēka gate threshold adjusted for 0.5 baseline
- [x] All existing tests pass (with updated expectations where needed)
- [x] No test removed — only expectations adjusted
- [x] Three-point calibration sweep runs (0.0, 0.5, 1.0)
- [x] 0.5 baseline produces near-zero deltas (verified)
- [x] Full sweep table printed in test output
- [x] `planning/CURRENT.md` updated from repo inspection
- [x] `DEVLOG.md` has Directive 008 entry with calibration table
- [x] `README.md` updated
- [ ] Git commit and push completed
