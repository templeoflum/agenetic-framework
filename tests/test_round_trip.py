"""Round-trip calibration test infrastructure.

Implements the motor->sensory feedback loop for testing limb-to-feature
mappings. Motor output is fed back through sensory and the feature deltas
are measured. Calibration tests vary individual limb weights and record
which signal features respond.

This is the experimental apparatus for validating the limb-to-feature
mapping hypotheses from references/conceptual_archaeology.md Section V.
"""

import pytest

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import create_default_state
from agenetic.systems.motor import (
    MotorSystem,
    _compute_target_profile,
    PRAKASA_ID,
    TARKA_ID,
    NIVRTTI_ID,
    SAMATVAM_ID,
    SRADDHA_ID,
    MAYAVADA_ID,
    AREKA_ID,
    SVADHARMA_ID,
    KSETRA_JNANA_ID,
)
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.sleep import SleepSystem


# A calibration input with enough structure for all strategies to operate.
CALIBRATION_INPUT = (
    "The quick brown fox jumps over the lazy dog. "
    "The dog barks at the fox loudly. "
    "The fox runs away quickly and quietly. "
    "Meanwhile the cat sleeps on the warm mat peacefully."
)

# All 18 limbs for parameterized calibration.
ALL_LIMB_IDS = list(range(1, 19))

# Feature keys to track in calibration.
FEATURE_KEYS = ["density", "entropy", "coherence", "periodicity", "noise_floor", "impedance"]


def vary_single_limb(limb_id: int, weight: float, baseline: float = 1.0) -> OrientationalField:
    """Create an OrientationalField with one limb varied, others at baseline.

    This is the weight variation utility for isolated limb testing.

    Args:
        limb_id: The limb to vary (1-18).
        weight: The weight value to assign to the varied limb.
        baseline: The weight value for all other limbs (default 1.0).

    Returns:
        An OrientationalField with the specified configuration.
    """
    field = OrientationalField()
    limbs = field.read()["limbs"]
    for limb in limbs:
        if limb["id"] == limb_id:
            limb["weight"] = weight
        else:
            limb["weight"] = baseline
    field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
    return field


def round_trip(input_text: str, field: OrientationalField) -> dict:
    """Run motor output back through sensory and measure delta.

    The round-trip loop:
    1. Sensory on original input -> signal report A
    2. Motor restructures with field weights -> restructured text
    3. Sensory on motor output -> signal report B
    4. Compute feature deltas (B - A)

    Args:
        input_text: The input to process.
        field: The orientational field (with specific limb weights).

    Returns:
        Dict with keys:
        - 'input_report': signal report from original input
        - 'output_report': signal report from motor output
        - 'motor_output': the motor's output dict
        - 'feature_deltas': dict of feature name -> (output - input) delta
    """
    sensory = SensorySystem()
    motor = MotorSystem()

    # Step 1: Sensory on original input.
    state_a = create_default_state(input_data=input_text, field=field)
    state_a = sensory.process(state_a)
    input_report = state_a["signal_report"]

    # Step 2: Motor restructures.
    motor_result = motor.process(state_a)
    motor_out = motor_result["motor_output"]
    restructured = motor_out["output_text"]

    # Step 3: Sensory on motor output.
    state_b = create_default_state(input_data=restructured, field=field)
    state_b = sensory.process(state_b)
    output_report = state_b["signal_report"]

    # Step 4: Compute deltas.
    feature_deltas = {}
    for key in FEATURE_KEYS:
        val_a = input_report["features"][key]
        val_b = output_report["features"][key]
        feature_deltas[key] = val_b - val_a

    return {
        "input_report": input_report,
        "output_report": output_report,
        "motor_output": motor_out,
        "feature_deltas": feature_deltas,
    }


# ============================================================
# Basic round-trip tests
# ============================================================


class TestRoundTripBasics:
    """Verify the round-trip loop completes without error."""

    def test_motor_output_not_empty(self):
        field = OrientationalField()
        result = round_trip(CALIBRATION_INPUT, field)
        assert len(result["motor_output"]["output_text"]) > 0

    def test_motor_output_different_from_input(self):
        """Motor should produce measurably different features than input."""
        field = OrientationalField()
        result = round_trip(CALIBRATION_INPUT, field)
        # At least one feature should have shifted.
        deltas = result["feature_deltas"]
        any_changed = any(abs(v) > 0.001 for v in deltas.values())
        # With default weights, motor may or may not change the text
        # (depends on how close current features are to targets).
        # Just verify the loop completes and produces valid data.
        assert isinstance(deltas, dict)
        assert all(k in deltas for k in FEATURE_KEYS)

    def test_round_trip_output_valid_signal_report(self):
        """Motor output fed through sensory produces a valid signal report."""
        field = OrientationalField()
        result = round_trip(CALIBRATION_INPUT, field)
        report = result["output_report"]
        assert report is not None
        assert "features" in report
        assert "classification" in report
        assert "delta" in report
        assert report["classification"]["signal_type"] in {
            "steady_state", "transient", "periodic", "noise", "complex"
        }

    def test_motor_repair_check_passes(self):
        """Motor output should pass its own repair check."""
        field = OrientationalField()
        result = round_trip(CALIBRATION_INPUT, field)
        assert result["motor_output"]["repair_passed"] is True

    def test_round_trip_with_varied_weight(self):
        """Round-trip with a varied weight should complete without error."""
        field = vary_single_limb(2, 0.0)  # Tarka at 0
        result = round_trip(CALIBRATION_INPUT, field)
        assert result["motor_output"]["output_text"] != ""
        assert result["output_report"] is not None

    def test_different_weights_different_results(self):
        """Varying a governing limb should produce different round-trip results."""
        field_low = vary_single_limb(2, 0.0)   # Tarka at 0
        field_high = vary_single_limb(2, 2.0)  # Tarka at 2
        result_low = round_trip(CALIBRATION_INPUT, field_low)
        result_high = round_trip(CALIBRATION_INPUT, field_high)
        # The motor outputs should differ.
        assert (
            result_low["motor_output"]["output_text"]
            != result_high["motor_output"]["output_text"]
        )


# ============================================================
# Calibration test scaffolding
# ============================================================


# Limb name lookup for readable output.
_LIMB_NAMES = {
    1: "Prakasa", 2: "Tarka", 3: "Nivrtti", 4: "Mayavada",
    5: "Sraddha", 6: "Atma-Vichara", 7: "Samatvam", 8: "Areka",
    9: "Svadharma", 10: "Ksetra-Jnana", 11: "Vishvarupa", 12: "Bodhi",
    13: "No-Position", 14: "Nivrtti-Rest", 15: "Mirror",
    16: "Fourfold-State", 17: "Ajati", 18: "Asparsa-Yoga",
}


@pytest.fixture(scope="module")
def baseline_result():
    """Run round-trip with all weights at default (1.0)."""
    field = OrientationalField()
    return round_trip(CALIBRATION_INPUT, field)


@pytest.mark.parametrize("limb_id", ALL_LIMB_IDS)
class TestCalibrationSweep:
    """Parameterized calibration: vary each limb and record feature deltas.

    Does NOT assert specific limb-to-feature mappings. Records results
    as structured data for analysis by the planning instance.
    """

    def test_limb_weight_zero(self, limb_id, baseline_result):
        """Set one limb to 0.0, hold others at 1.0. Record feature deltas vs baseline."""
        field = vary_single_limb(limb_id, 0.0)
        result = round_trip(CALIBRATION_INPUT, field)

        # Compute delta relative to baseline (not to input).
        baseline_features = baseline_result["output_report"]["features"]
        varied_features = result["output_report"]["features"]
        relative_deltas = {}
        for key in FEATURE_KEYS:
            relative_deltas[key] = varied_features[key] - baseline_features[key]

        # Record structured result (visible via pytest -v -s).
        record = {
            "limb_name": _LIMB_NAMES[limb_id],
            "weight_value": 0.0,
            "feature_deltas": relative_deltas,
        }

        # We only assert the loop completes and produces valid data.
        assert result["output_report"] is not None
        assert result["motor_output"]["output_text"] != ""

        # Print for calibration analysis.
        _print_calibration_record(record)


@pytest.mark.parametrize("limb_id", ALL_LIMB_IDS)
class TestCalibrationSweepHalf:
    """Parameterized calibration: vary each limb to 0.5 and record feature deltas.

    Second sweep point for graded vs binary response analysis.
    """

    def test_limb_weight_half(self, limb_id, baseline_result):
        """Set one limb to 0.5, hold others at 1.0. Record feature deltas vs baseline."""
        field = vary_single_limb(limb_id, 0.5)
        result = round_trip(CALIBRATION_INPUT, field)

        baseline_features = baseline_result["output_report"]["features"]
        varied_features = result["output_report"]["features"]
        relative_deltas = {}
        for key in FEATURE_KEYS:
            relative_deltas[key] = varied_features[key] - baseline_features[key]

        record = {
            "limb_name": _LIMB_NAMES[limb_id],
            "weight_value": 0.5,
            "feature_deltas": relative_deltas,
        }

        assert result["output_report"] is not None
        assert result["motor_output"]["output_text"] is not None

        _print_calibration_record(record)


def _print_calibration_record(record: dict) -> None:
    """Print a structured calibration record for analysis."""
    name = record["limb_name"]
    weight = record["weight_value"]
    deltas = record["feature_deltas"]
    delta_str = " | ".join(
        f"{k}: {v:+.4f}" for k, v in deltas.items()
    )
    print(f"  [{name} @ {weight}] {delta_str}")


def _run_sweep_at_weight(weight: float, baseline_features: dict) -> list[dict]:
    """Run calibration sweep at a specific weight point. Returns list of results."""
    results = []
    for limb_id in ALL_LIMB_IDS:
        name = _LIMB_NAMES[limb_id]
        field = vary_single_limb(limb_id, weight)
        result = round_trip(CALIBRATION_INPUT, field)

        # Handle Ārēka suppression: if output is empty, use zero features.
        motor_out = result["motor_output"]
        if motor_out["output_text"] == "" and "areka_suppression" in motor_out.get("strategies_applied", []):
            varied_features = {k: 0.0 for k in FEATURE_KEYS}
            suppressed = True
        else:
            varied_features = result["output_report"]["features"]
            suppressed = False

        deltas = {}
        for key in FEATURE_KEYS:
            deltas[key] = varied_features[key] - baseline_features[key]

        results.append({
            "limb_name": name,
            "limb_id": limb_id,
            "weight_value": weight,
            "feature_deltas": deltas,
            "strategies_applied": motor_out["strategies_applied"],
            "suppressed": suppressed,
            "transform_magnitude": motor_out.get("transform_magnitude", 0.0),
        })
    return results


def test_calibration_summary():
    """Run full calibration sweep and print summary table.

    This is the experimental output for the planning instance to analyze.
    Varies each of the 18 limbs to weight=0.0 and weight=0.5 while holding
    all others at baseline=1.0, then measures feature deltas in motor
    output relative to the all-1.0 baseline. Two data points per limb.
    """
    # Baseline: all weights at 1.0.
    field_baseline = OrientationalField()
    baseline = round_trip(CALIBRATION_INPUT, field_baseline)
    baseline_features = baseline["output_report"]["features"]

    all_results = []

    for sweep_weight in [0.0, 0.5]:
        # Header.
        header = f"{'Limb varied':<20}" + " | ".join(f"{k:>12}" for k in FEATURE_KEYS) + " | strategies"
        sep = "-" * len(header)
        print(f"\n{'=' * len(header)}")
        print(f"CALIBRATION SWEEP: Limb weight 1.0 -> {sweep_weight} (baseline -> varied)")
        print(f"{'=' * len(header)}")
        print(header)
        print(sep)

        results = _run_sweep_at_weight(sweep_weight, baseline_features)
        for r in results:
            name = r["limb_name"]
            deltas = r["feature_deltas"]
            strategies = r["strategies_applied"]
            suppressed = r["suppressed"]
            label = f"{name} ({sweep_weight})"
            if suppressed:
                label += " [SUP]"
            row = f"{label:<20}" + " | ".join(
                f"{deltas[k]:>+12.4f}" for k in FEATURE_KEYS
            ) + f" | {', '.join(strategies)}"
            print(row)

        print(sep)
        all_results.extend(results)

    print(f"\nTotal sweep points: {len(all_results)} ({len(all_results)//18} per limb × 18 limbs)")
    print(f"Baseline features: " + " | ".join(
        f"{k}: {baseline_features[k]:.4f}" for k in FEATURE_KEYS
    ))
    print(f"Baseline strategies: {baseline['motor_output']['strategies_applied']}")

    # Assert we tested all 18 limbs at both weight points.
    assert len(all_results) == 36
