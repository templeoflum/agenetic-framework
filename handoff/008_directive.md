# Directive 008 — Midpoint Weight Migration and Recalibration

**Type:** Refactoring / Calibration
**From:** Planning instance (claude.ai)
**Date:** 2026-02-08

## Context

The orientational field has used uniform 1.0 limb weights since Directive 001. The intended operating point from the earliest concept documents is 0.5 — "All values are represented as a cycle of 0 to 1 resting at ≈0.5." The midpoint model is more expressive: it allows both amplification (>0.5) and suppression (<0.5) relative to baseline. In signal processing terms, 0.5 is maximum information entropy — the most receptive state.

This was listed as "blocked on sleep + calibration data" but that blocker was misidentified. The default weight is a genetic/field concern, not a sleep concern. Sleep optimizes weights at runtime; genetic sets the factory calibration. Neither needs to be implemented to change the starting position.

All calibration data from Directives 004 and 007 was collected against a 1.0 baseline we plan to change. The strategies and plumbing are validated, but the mapping landscape may look different at 0.5. This directive changes the defaults and re-runs the full sweep.

## Read Before Starting

- `planning/CURRENT.md` — current repo state
- `planning/007_motor_extension.md` — latest planning entry
- `src/agenetic/field/orientational.py` — where limb weights are defined
- `src/agenetic/systems/motor.py` — target profile formulas that depend on weights
- `src/agenetic/systems/sensory.py` — reference signal computation (mean of limb weights)
- `tests/test_round_trip.py` — calibration sweep infrastructure
- `handoff/state.md` — planning notes for this directive (copy to `planning/008_midpoint_migration.md`)

## Part A: Change Default Limb Weights

In `src/agenetic/field/orientational.py`, change all 18 limb weights from `1.0` to `0.5`.

This is the factory calibration — the genetic seed's resting state. Every limb starts at the midpoint, equally capable of amplification or suppression.

## Part B: Review and Adjust Target Profile Formulas

The motor's `_compute_target_profile()` was designed against 1.0 defaults. Review every formula and adjust so the *default behavior at 0.5* produces reasonable targets — motor should still produce moderate, non-extreme output at the baseline.

Current formulas and their behavior at 0.5:

| Feature | Current formula | At 1.0 | At 0.5 | Notes |
|---|---|---|---|---|
| density | `mean_w * 0.8` | 0.8 | 0.4 | May be too low — review |
| entropy | `tarka * 3.5` | 3.5 | 1.75 | Significantly lower — review |
| coherence | `samatvam * 0.7` | 0.7 | 0.35 | May be too low — review |
| impedance | `(1.0 - nivrtti) * 0.3` | 0.0 | 0.15 | Now non-zero at default — review |
| periodicity | `(1.0 - prakasa) * 0.3` | 0.0 | 0.15 | Now non-zero at default — review |
| noise_floor | `(1.0 - sraddha) * 0.3` | 0.0 | 0.15 | Now non-zero at default — review |

The goal is: at 0.5 (midpoint), the target profile should represent a neutral, balanced output — moderate density, moderate entropy, moderate coherence, near-zero impedance/periodicity/noise. The formulas may need rebalancing to achieve this.

**Design principle:** At 0.5, motor should produce output very close to the original input (minimal transformation). Amplification above 0.5 increases transformation in each feature's direction. Suppression below 0.5 increases transformation in the opposite direction.

Consider restructuring the formulas so they're symmetric around 0.5:
- `target = base + (weight - 0.5) * scale`

Where `base` is the neutral value for that feature and `scale` controls sensitivity. This makes the weight's direction and magnitude both meaningful. But only adopt this if it makes the system cleaner — don't over-engineer. If simpler adjustments to the existing formulas work, use those.

## Part C: Review Sensory Reference Signal

The sensory system computes a reference signal as the mean of all limb weights. At 1.0 this was 1.0; at 0.5 this becomes 0.5. Check that:

1. The aggregate_deviation computation still works correctly
2. The signal classification isn't thrown off
3. The subconscious escalation thresholds are still reasonable

At 0.5 reference, the deviation between typical text features and the field should actually be *smaller* — periodicity/noise/impedance naturally near 0, and the reference drops from 1.0 toward 0.5 (closer to reality). This might mean fewer escalations, which is actually more correct behavior — the "everything escalates" issue from Directive 002 may partially resolve.

## Part D: Review Strategy Thresholds

Motor strategy thresholds (0.05, 0.5, 0.1, etc.) and the Svadharma scaling were tuned against 1.0 defaults. At 0.5 the deltas between target and current features will be different. Review each threshold to ensure strategies still fire when they should.

Similarly, the Māyāvāda cap (`mayavada_w < 0.95` to activate) needs adjustment for 0.5 — it should activate at some threshold below 0.5, not 0.95.

The Ārēka gate threshold (`areka_w > 0.8`) also needs adjustment — at 0.5 default, the gate should be active. Consider `areka_w > 0.3` or use `areka_w > mean_weight * 0.6` for a relative threshold.

## Part E: Fix Existing Tests

Many existing tests create state with explicit weight values or rely on default behavior. Tests that check specific output values will need updating. Tests that check *relative* behavior (e.g., "varying weight X changes output") should still pass.

Approach:
1. Run pytest first with the new defaults to see what breaks
2. Fix tests that have hardcoded expectations about 1.0 behavior
3. Ensure all tests that verify *relative* behavior (weight sensitivity, determinism) still pass
4. Do not weaken any test — if a test fails, fix the expectation to match the new correct behavior, don't remove the test

## Part F: Three-Point Calibration Sweep

Update `tests/test_round_trip.py`:

Run the sweep at three weight points per limb: **0.0**, **0.5** (now the baseline), and **1.0**.

- 0.0 → full suppression
- 0.5 → baseline (should show zero delta — this IS the default)
- 1.0 → full amplification

This gives us the response curve for each limb: does it respond symmetrically? Is the effect proportional? Are there nonlinearities?

Print the full three-point table for planning instance analysis. Format:

```
Limb varied    | weight | density | entropy | coherence | periodicity | noise_floor | impedance | strategies
Prakasa        |   0.0  | ...     | ...     | ...       | ...         | ...         | ...       | [list]
Prakasa        |   1.0  | ...     | ...     | ...       | ...         | ...         | ...       | [list]
Tarka          |   0.0  | ...     | ...     | ...       | ...         | ...         | ...       | [list]
Tarka          |   1.0  | ...     | ...     | ...       | ...         | ...         | ...       | [list]
...
```

(0.5 is baseline so deltas should be ~0.0 for all — no need to print those rows, but DO verify they're near-zero and report any that aren't.)

## Part G: Documentation Updates

- **`planning/CURRENT.md`:** Update from repo inspection after all changes
- **`DEVLOG.md`:** Append Directive 008 entry with:
  - The midpoint rationale (0.5 = maximum information entropy, symmetric amplification/suppression)
  - Any formula changes made
  - Full three-point calibration table
  - Comparison notes: what changed from the 1.0 baseline data
- **`README.md`:** Update test count, note midpoint weight model in orientational field description

## Part H: Planning State

Copy `handoff/state.md` to `planning/008_midpoint_migration.md`.

## Verification Checklist

- [ ] `handoff/state.md` copied to `planning/008_midpoint_migration.md`
- [ ] All 18 limb weights default to 0.5 in orientational field
- [ ] Motor target profile formulas produce reasonable targets at 0.5
- [ ] At 0.5 default, motor produces output close to original input (minimal transformation)
- [ ] Sensory reference signal works correctly at 0.5
- [ ] Strategy thresholds reviewed and adjusted for 0.5 baseline
- [ ] Māyāvāda activation threshold adjusted for 0.5 baseline
- [ ] Ārēka gate threshold adjusted for 0.5 baseline
- [ ] All existing tests pass (with updated expectations where needed)
- [ ] No test removed — only expectations adjusted
- [ ] Three-point calibration sweep runs (0.0, 0.5, 1.0)
- [ ] 0.5 baseline produces near-zero deltas (verified)
- [ ] Full sweep table printed in test output
- [ ] `planning/CURRENT.md` updated from repo inspection
- [ ] `DEVLOG.md` has Directive 008 entry with calibration table
- [ ] `README.md` updated
- [ ] Git commit and push completed
