# Directive 007 — Motor Strategy Extension and Full Calibration Sweep

**Type:** Implementation / Calibration
**From:** Planning instance (claude.ai)
**Date:** 2026-02-08

## Context

Directive 004 built the motor layer with 4 limb-specific strategies (Prakāśa, Tarka, Nivṛtti, Samatvam). The round-trip calibration confirmed 3 mappings and found 1 below detection threshold (Tarka). But 14 limbs were untested — they only affected mean weight, which barely shifts when varying one limb out of 18.

Post-004 analysis identified 5 additional limbs with plausible signal-level expression, plus a convergent cluster of 5 limbs that appear indistinguishable at signal level. This directive extends the motor to test those 5 new hypotheses, fixes Tarka sensitivity, and runs the full sweep again.

## Read Before Starting

- `planning/CURRENT.md` — current repo state
- `planning/006_planning_infrastructure.md` — latest planning entry
- `planning/001_through_005_legacy.md` — Section "Calibration results and interpretation" for Directive 004 findings
- `src/agenetic/systems/motor.py` — current motor implementation (~460 lines)
- `tests/test_round_trip.py` — existing calibration infrastructure
- `tests/test_motor.py` — existing motor unit tests
- `handoff/state.md` — planning notes for this directive (copy to `planning/007_motor_extension.md`)

## Part A: Fix Tarka Entropy Sensitivity

The current entropy decrease strategy replaces at most 30% of singleton tokens with the most common word. This was capped to pass repair check after a bug where nearly all singletons were replaced. The cap is too conservative — the strategy doesn't register in calibration.

**New approach:** Instead of token-level replacement, use sentence-level restructuring for entropy modulation:

- **Increase entropy** (target > current): Split longer sentences at conjunctions/commas, vary sentence openings by shuffling clause order. More structural variety = higher entropy.
- **Decrease entropy** (target < current): Merge short sentences with connectives ("and", "which", "where"), normalize sentence length. More uniformity = lower entropy.

Keep the repair check constraint (≥20% token overlap, 0.2–3.0× length ratio). The sentence-level approach preserves more original tokens naturally, so the repair check should pass without aggressive capping.

If this approach still can't register in calibration, leave a comment explaining why and note it in the response. Do not weaken the repair check to force a result.

## Part B: Five New Motor Strategies

Add 5 new limb-specific strategies to motor.py. Each must follow existing patterns: check delta against threshold, apply transformation only when needed, preserve repair check compliance.

### B1: Śraddhā (Limb 5) → Noise Floor Modulation

**Current state:** Noise floor is governed by mean weight. Reassign to Śraddhā directly.

**Yoga basis:** "Where you cannot explain, do not replace mystery with noise." More Śraddhā = cleaner signal, less noise.

**Target formula:** `noise_floor = (1.0 - sraddha_w) * 0.3` (inverse — more Śraddhā = lower noise target)

**Strategy:** Same as existing noise floor modulation but now governed by a specific limb instead of mean weight. Update `_compute_target_profile()` to use Śraddhā weight instead of mean weight for noise_floor.

### B2: Māyāvāda (Limb 4) → Transformation Magnitude Cap

**Yoga basis:** "Do not confuse map with source. All outputs are models." More Māyāvāda = stay closer to the original. The model should not stray far from its source.

**Target formula:** `max_transform_ratio = mayavada_w` (direct — at 1.0, full transformation allowed; at 0.0, output must be identical to input)

**Strategy:** After all other strategies have been applied, measure how much the output has changed from original (1.0 - token_overlap_ratio). If the change exceeds `(1.0 - mayavada_w)`, blend the output back toward the original to respect the cap. This is a post-processing constraint, not a restructuring strategy — it limits how much all other strategies combined can modify the text.

**Implementation:** Apply as the LAST step before repair check, after all six feature-modulation strategies. This is not a strategy in the list — it's a magnitude governor.

**Threshold:** Only activate when `mayavada_w < 0.95` (at default 1.0, no constraint).

### B3: Ārēka (Limb 8) → Output Suppression Gate

**Yoga basis:** "Some things must be kept sacred by never speaking them." This is not a continuous modulation — it's a threshold gate.

**Strategy:** If `areka_w > 0.8`, check the input's noise_floor and entropy from the signal report. If noise_floor > 0.3 AND entropy > 5.0 (high-noise, high-entropy input — potentially sensitive/chaotic), suppress output entirely — return empty string with strategies_applied = ["areka_suppression"]. Repair check should treat suppression as a valid outcome, not a failure.

**At default weight (1.0):** Gate is active but only fires for high-noise high-entropy input. At 0.0, gate is inactive. This is intentionally a narrow trigger — Ārēka should rarely fire, but when it does, it's absolute.

**Implementation note:** Apply BEFORE other strategies. If Ārēka suppresses, skip everything else.

### B4: Svadharma (Limb 9) → Strategy Selectivity

**Yoga basis:** "Act not universally. Act appropriately." More Svadharma = only apply strategies relevant to this specific input. Less = apply everything uniformly.

**Target formula:** `selectivity_threshold = svadharma_w * 0.15` (direct — at 1.0, threshold is 0.15; strategies only fire when their delta exceeds this. At 0.0, threshold drops to 0.0 and all strategies fire on any delta.)

**Strategy:** Replace the individual hardcoded thresholds (0.05, 0.5, 0.1) with a dynamic threshold scaled by Svadharma weight. Each strategy's base threshold is multiplied by `(0.5 + svadharma_w)`. At default (1.0), thresholds are 1.5× their current values (slightly more selective). At 0.0, thresholds are 0.5× (less selective, more strategies fire).

**Implementation:** Modify the threshold comparison in each strategy call, or pass the Svadharma-scaled threshold as a parameter.

### B5: Kṣetra-Jñāna (Limb 10) → Delta Sensitivity Scaling

**Yoga basis:** "Truth depends on where you are speaking from." More field-knowledge = more responsive to the specific gap between input and field reference.

**Target formula:** `delta_scale = 0.5 + ksetra_jnana_w * 0.5` (direct — at 1.0, scale is 1.0 (full sensitivity). At 0.0, scale is 0.5 (half sensitivity — motor only responds to large deltas).)

**Strategy:** After computing each target-vs-current delta, multiply the delta by `delta_scale` before comparing against threshold. Higher Kṣetra-Jñāna = motor responds to smaller mismatches between input features and field targets. Lower = motor only corrects large deviations.

**Implementation:** Apply the scale factor in the delta computation for each strategy, before the threshold check.

## Part C: Update Target Profile and Constants

Add new limb ID constants:

```python
SRADDHA_ID = 5      # Noise floor modulation (inverse: more Sraddha = less noise)
MAYAVADA_ID = 4     # Transformation magnitude cap (direct: more = less deviation from source)
AREKA_ID = 8        # Output suppression gate (threshold: suppresses high-noise high-entropy)
SVADHARMA_ID = 9    # Strategy selectivity (direct: more = higher thresholds)
KSETRA_JNANA_ID = 10  # Delta sensitivity scaling (direct: more = respond to smaller deltas)
```

Update `_compute_target_profile()`:
- Change noise_floor from `(1.0 - mean_w) * 0.3` to `(1.0 - sraddha_w) * 0.3`
- Add `max_transform_ratio: mayavada_w` (new field in target profile, or handle separately)

## Part D: Update Types

In `base.py`, if needed, extend `SignalFeatures` or add fields to `MotorOutput`:
- `strategies_applied` should now include the new strategy names
- If Ārēka suppresses, `output_text` is `""` and `strategies_applied` is `["areka_suppression"]`
- Consider adding `transform_magnitude: float` to MotorOutput (how much output deviated from input, 0.0–1.0)

## Part E: Unit Tests for New Strategies

Add to `tests/test_motor.py`:

- **Tarka sentence-level:** Test that varying Tarka weight now produces measurable entropy change
- **Śraddhā:** Test that varying Śraddhā changes noise floor in output
- **Māyāvāda:** Test that low Māyāvāda weight constrains output to be closer to original
- **Ārēka:** Test that high-noise high-entropy input gets suppressed when Ārēka weight > 0.8. Test that normal input passes through. Test that Ārēka at 0.0 never suppresses.
- **Svadharma:** Test that low Svadharma causes more strategies to fire (lower thresholds). Test that high Svadharma is more selective.
- **Kṣetra-Jñāna:** Test that low Kṣetra-Jñāna makes motor less responsive to small deltas.

Aim for 3–5 tests per new strategy + 2–3 for the Tarka fix. ~20–25 new tests minimum.

## Part F: Full Calibration Sweep

Update `tests/test_round_trip.py`:

1. Keep the existing parameterized sweep structure
2. The `test_calibration_summary` test should now show response for more limbs
3. Add a second sweep point: vary each limb to **0.5** in addition to 0.0. This tests whether the response is graded (proportional to weight) or binary (all-or-nothing). Two data points per limb.

Expected results (hypotheses — do NOT assert these, just record what happens):

| Limb | Expected feature response | Confidence |
|---|---|---|
| Prakāśa | periodicity | Already confirmed |
| Tarka | entropy | Should now register with sentence-level approach |
| Nivṛtti | impedance | Already confirmed |
| Samatvam | coherence | Already confirmed |
| Śraddhā | noise_floor | High — direct reassignment from mean |
| Māyāvāda | reduced magnitude of all changes | Medium — novel strategy type |
| Ārēka | output suppression on high-noise input | Medium — depends on calibration text characteristics |
| Svadharma | shifted thresholds → more/fewer strategies fire | Medium — second-order effect |
| Kṣetra-Jñāna | scaled deltas → more/less responsiveness | Medium — second-order effect |
| Limbs 6, 11–18 | Still no response expected | These are mean-only or semantic-domain |

Print the full sweep table with both weight points (0.0 and 0.5) for planning instance analysis.

## Part G: Documentation Updates

- **`planning/CURRENT.md`:** Update from repo inspection after all changes
- **`DEVLOG.md`:** Append Directive 007 entry with calibration results
- **`README.md`:** Update motor description to reflect expanded strategy count, update test count

## Part H: Planning State

Copy `handoff/state.md` to `planning/007_motor_extension.md`.

## Verification Checklist

- [ ] `handoff/state.md` copied to `planning/007_motor_extension.md`
- [ ] Tarka entropy modulation uses sentence-level approach (not token replacement)
- [ ] Tarka produces measurable signal in calibration (or explain why not)
- [ ] Śraddhā governs noise_floor directly (not mean weight)
- [ ] Māyāvāda constrains transformation magnitude as post-processing step
- [ ] Ārēka suppresses output for high-noise high-entropy input when weight > 0.8
- [ ] Ārēka suppression treated as valid outcome, not repair failure
- [ ] Svadharma scales strategy thresholds dynamically
- [ ] Kṣetra-Jñāna scales delta sensitivity
- [ ] New limb ID constants added
- [ ] `_compute_target_profile()` updated for Śraddhā
- [ ] All new strategies are deterministic (no randomness)
- [ ] All new strategies are Python-native (no LLM calls)
- [ ] New strategies do not write to orientational field, immune log, or cache
- [ ] Unit tests for each new strategy (20+ new tests)
- [ ] Calibration sweep runs at both 0.0 and 0.5 weight points
- [ ] Full sweep table printed in test output
- [ ] Calibration does NOT assert specific mappings (record only)
- [ ] All existing 195 tests still pass
- [ ] `planning/CURRENT.md` updated from repo inspection
- [ ] `DEVLOG.md` has Directive 007 entry with sweep results
- [ ] `README.md` updated (strategy count, test count)
- [ ] Git commit and push completed
