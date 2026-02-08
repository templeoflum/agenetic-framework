"""Unit tests for the motor/output system.

Verifies signal-level text restructuring, determinism, field-weight
sensitivity, repair checking, and apoptotic conditions.
"""

import pytest

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import create_default_state
from agenetic.systems.motor import (
    MotorSystem,
    _compute_target_profile,
    _get_limb_weight,
    _mean_weight,
    _modulate_density,
    _modulate_entropy,
    _modulate_coherence,
    _modulate_impedance,
    _modulate_periodicity,
    _modulate_noise_floor,
    PRAKASA_ID,
    TARKA_ID,
    NIVRTTI_ID,
    SAMATVAM_ID,
)
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.sleep import SleepSystem


SAMPLE_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "The dog barks at the fox. "
    "The fox runs away quickly."
)


def _make_motor_state(input_text=SAMPLE_TEXT, field=None):
    """Create a state ready for motor processing with signal report populated."""
    if field is None:
        field = OrientationalField()
    state = create_default_state(input_data=input_text, field=field)
    # Run sensory to produce a valid signal report.
    sensory = SensorySystem()
    state = sensory.process(state)
    return state


def _vary_single_limb(limb_id: int, weight: float, baseline: float = 1.0):
    """Create an OrientationalField with one limb varied, others at baseline."""
    field = OrientationalField()
    limbs = field.read()["limbs"]
    for limb in limbs:
        if limb["id"] == limb_id:
            limb["weight"] = weight
        else:
            limb["weight"] = baseline
    field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
    return field


class TestMotorBasics:
    """Basic motor system interface and behavior tests."""

    def test_process_returns_motor_output(self):
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        assert "motor_output" in result
        assert result["motor_output"] is not None

    def test_motor_output_has_required_fields(self):
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        output = result["motor_output"]
        assert "output_text" in output
        assert "target_profile" in output
        assert "strategies_applied" in output
        assert "repair_passed" in output

    def test_output_text_is_string(self):
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        assert isinstance(result["motor_output"]["output_text"], str)

    def test_output_text_not_empty(self):
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        assert len(result["motor_output"]["output_text"]) > 0

    def test_empty_input_produces_empty_output(self):
        motor = MotorSystem()
        state = _make_motor_state(input_text="")
        result = motor.process(state)
        assert result["motor_output"]["output_text"] == ""
        assert result["motor_output"]["repair_passed"] is True

    def test_none_input_produces_empty_output(self):
        motor = MotorSystem()
        state = _make_motor_state(input_text=None)
        result = motor.process(state)
        assert result["motor_output"]["output_text"] == ""

    def test_preserves_input_in_state(self):
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        assert result["input"] == SAMPLE_TEXT

    def test_does_not_modify_field(self):
        motor = MotorSystem()
        field = OrientationalField()
        original_field = field.read()
        state = _make_motor_state(field=field)
        motor.process(state)
        assert field.read() == original_field

    def test_does_not_modify_immune_log(self):
        motor = MotorSystem()
        state = _make_motor_state()
        state["immune_log"] = [{"pattern": "test", "encounter_count": 1,
                                 "confidence": 0.5, "last_seen": "2026-01-01T00:00:00"}]
        result = motor.process(state)
        assert result["immune_log"] == state["immune_log"]

    def test_does_not_modify_signal_pattern_cache(self):
        motor = MotorSystem()
        state = _make_motor_state()
        state["signal_pattern_cache"] = []
        result = motor.process(state)
        assert result["signal_pattern_cache"] == []


class TestMotorDeterminism:
    """Motor must be deterministic: same input + same field = same output."""

    def test_same_input_same_field_same_output(self):
        motor = MotorSystem()
        state1 = _make_motor_state()
        state2 = _make_motor_state()
        result1 = motor.process(state1)
        result2 = motor.process(state2)
        assert result1["motor_output"]["output_text"] == result2["motor_output"]["output_text"]

    def test_same_input_same_strategies(self):
        motor = MotorSystem()
        state1 = _make_motor_state()
        state2 = _make_motor_state()
        result1 = motor.process(state1)
        result2 = motor.process(state2)
        assert result1["motor_output"]["strategies_applied"] == result2["motor_output"]["strategies_applied"]


class TestMotorFieldSensitivity:
    """Motor output should vary when limb weights change."""

    def test_tarka_weight_changes_output(self):
        """Varying Tarka weight (entropy) should change motor output."""
        motor = MotorSystem()
        field_low = _vary_single_limb(TARKA_ID, 0.0)
        field_high = _vary_single_limb(TARKA_ID, 2.0)
        state_low = _make_motor_state(field=field_low)
        state_high = _make_motor_state(field=field_high)
        result_low = motor.process(state_low)
        result_high = motor.process(state_high)
        # Different field weights should produce different outputs.
        assert result_low["motor_output"]["output_text"] != result_high["motor_output"]["output_text"]

    def test_samatvam_weight_changes_output(self):
        """Varying Samatvam weight (coherence) should change motor output."""
        motor = MotorSystem()
        field_low = _vary_single_limb(SAMATVAM_ID, 0.0)
        field_high = _vary_single_limb(SAMATVAM_ID, 2.0)
        state_low = _make_motor_state(field=field_low)
        state_high = _make_motor_state(field=field_high)
        result_low = motor.process(state_low)
        result_high = motor.process(state_high)
        assert result_low["motor_output"]["output_text"] != result_high["motor_output"]["output_text"]

    def test_target_profile_changes_with_weights(self):
        """Target profile should reflect limb weight changes."""
        field_low = _vary_single_limb(TARKA_ID, 0.0)
        field_high = _vary_single_limb(TARKA_ID, 2.0)
        target_low = _compute_target_profile(field_low.read())
        target_high = _compute_target_profile(field_high.read())
        assert target_low["entropy"] < target_high["entropy"]


class TestMotorRepairCheck:
    """Repair check and apoptotic condition tests."""

    def test_repair_check_passes_after_process(self):
        motor = MotorSystem()
        state = _make_motor_state()
        result = motor.process(state)
        assert motor.repair_check(result) is True

    def test_repair_check_fails_without_motor_output(self):
        motor = MotorSystem()
        state = create_default_state(input_data="test")
        assert motor.repair_check(state) is False

    def test_apoptotic_false_normal_input(self):
        motor = MotorSystem()
        state = _make_motor_state()
        assert motor.apoptotic_condition(state) is False

    def test_apoptotic_true_none_input(self):
        motor = MotorSystem()
        state = _make_motor_state(input_text=None)
        assert motor.apoptotic_condition(state) is True


class TestMotorStrategies:
    """Test individual restructuring strategy functions."""

    def test_density_increase(self):
        text = "hello   world   test"
        result = _modulate_density(text, target=0.9, current=0.5)
        assert "   " not in result

    def test_density_decrease(self):
        text = "hello world. Test sentence."
        result = _modulate_density(text, target=0.3, current=0.9)
        assert len(result) >= len(text)

    def test_entropy_increase(self):
        text = "the cat and the dog and the bird"
        result = _modulate_entropy(text, target=5.0, current=2.0)
        assert "the-" in result  # repeated "the" gets suffixed

    def test_entropy_decrease(self):
        text = "apple banana cherry date elderberry fig grape"
        result = _modulate_entropy(text, target=0.0, current=2.8)
        # Some unique words should be replaced with the most common.
        assert result != text

    def test_coherence_increase(self):
        text = "The cat sleeps. The dog runs."
        result = _modulate_coherence(text, target=0.9, current=0.2)
        # Bridge word from first sentence should appear in second.
        assert result != text

    def test_coherence_decrease(self):
        text = "The cat sleeps. The dog runs. The bird sings."
        result = _modulate_coherence(text, target=0.0, current=0.8)
        # Sentences should be reversed.
        assert result.startswith("The bird")

    def test_impedance_decrease(self):
        text = "Hello [world] (test)"
        result = _modulate_impedance(text, target=0.0, current=0.3)
        assert "[" not in result
        assert "(" not in result

    def test_periodicity_increase(self):
        text = "one two three four five six seven eight nine"
        result = _modulate_periodicity(text, target=0.5, current=0.0)
        assert len(result.split()) > len(text.split())

    def test_noise_floor_decrease(self):
        text = "hello - world ! test & more"
        result = _modulate_noise_floor(text, target=0.0, current=0.4)
        tokens = result.split()
        # Single-char punctuation tokens should be removed.
        assert "-" not in tokens
        assert "!" not in tokens
        assert "&" not in tokens

    def test_no_op_when_close_to_target(self):
        text = "hello world test"
        assert _modulate_density(text, target=0.8, current=0.78) == text
        assert _modulate_entropy(text, target=2.0, current=1.8) == text
        assert _modulate_impedance(text, target=0.1, current=0.12) == text


class TestMotorHelpers:
    """Test helper functions."""

    def test_get_limb_weight_found(self):
        field = OrientationalField()
        assert _get_limb_weight(field.read(), PRAKASA_ID) == 1.0

    def test_get_limb_weight_not_found(self):
        assert _get_limb_weight({"limbs": []}, 999) == 1.0

    def test_mean_weight_default(self):
        field = OrientationalField()
        assert _mean_weight(field.read()) == 1.0

    def test_mean_weight_empty(self):
        assert _mean_weight({"limbs": []}) == 1.0

    def test_target_profile_default_weights(self):
        field = OrientationalField()
        target = _compute_target_profile(field.read())
        assert target["density"] == pytest.approx(0.8)
        assert target["entropy"] == pytest.approx(3.5)
        assert target["coherence"] == pytest.approx(0.7)
        assert target["periodicity"] == pytest.approx(0.0)
        assert target["noise_floor"] == pytest.approx(0.0)
        assert target["impedance"] == pytest.approx(0.0)
