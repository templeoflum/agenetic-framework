"""Motor/Output system — Signal-level text restructuring engine.

Relationship to information: Translates. Converts internal states into
appropriate external form.

Operates at the signal level: restructures text structurally to match target
signal profiles derived from orientational field limb weights. No LLM calls,
no semantic interpretation. Pure Python computation.

Serves dual purpose: output encoding AND calibration instrument for testing
limb-to-feature mappings via motor->sensory round-trip feedback loops.

Tick rate: On demand -- fires on both reflex path and post-conscious path.

Uses only Python stdlib -- deterministic given same input + field state.

Text restructuring is delegated to TextCodec (see text_codec.py).
MotorSystem handles orchestration: field reading, target computation,
codec delegation, repair checking, apoptotic tracking.
"""

from __future__ import annotations

from agenetic.systems.base import (
    AREKA_ID,
    BaseSystem,
    KSETRA_JNANA_ID,
    MAYAVADA_ID,
    MotorOutput,
    PRAKASA_ID,
    SAMATVAM_ID,
    SRADDHA_ID,
    SVADHARMA_ID,
    SignalFeatures,
    SystemState,
    TARKA_ID,
    compute_target_profile as _compute_target_profile,
    get_limb_weight as _get_limb_weight,
    mean_limb_weight as _mean_weight,
    NIVRTTI_ID,
)
from agenetic.systems.text_codec import (
    TextCodec,
    # Re-export modulation functions for backward compatibility with tests.
    _modulate_density,
    _modulate_entropy,
    _modulate_coherence,
    _modulate_impedance,
    _modulate_periodicity,
    _modulate_noise_floor,
    _compute_transform_magnitude,
    _blend_toward_original,
)


def _to_str(input_data) -> str:
    """Convert any input to string representation."""
    if input_data is None:
        return ""
    if isinstance(input_data, str):
        return input_data
    return str(input_data)


# ============================================================
# Motor system
# ============================================================


class MotorSystem(BaseSystem):
    """Signal-level text restructuring engine.

    Reverse transduction: where sensory extracts signal features FROM text,
    motor adjusts text TO target signal profiles shaped by the orientational
    field. Delegates text restructuring to TextCodec.

    Deterministic given the same input + field state.
    """

    def __init__(self) -> None:
        super().__init__(
            name="motor",
            description="Restructures text toward target signal profiles shaped by orientational field weights",
        )
        self._consecutive_repair_failures = 0
        self._codec = TextCodec()

    @property
    def tick_rate(self) -> str:
        return "on_demand"

    def process(self, state: SystemState) -> SystemState:
        raw_input = state["input"]
        field_state = state["field"]
        signal_report = state.get("signal_report")

        text = _to_str(raw_input)

        # Compute target profile from field weights.
        target = _compute_target_profile(field_state)

        # Handle empty/None input.
        if not text:
            motor_output: MotorOutput = {
                "output_text": "",
                "target_profile": target,
                "strategies_applied": [],
                "repair_passed": True,
                "transform_magnitude": 0.0,
            }
            return {**state, "motor_output": motor_output}

        # Get current features from signal report (if available).
        if signal_report is not None:
            current = signal_report["features"]
        else:
            # No signal report -- use neutral defaults.
            current: SignalFeatures = {
                "density": 0.5, "entropy": 2.0, "coherence": 0.5,
                "periodicity": 0.0, "noise_floor": 0.0, "impedance": 0.0,
                "bigram_entropy": 0.0,
                "token_count": len(text.split()), "vocabulary_richness": 0.5,
            }

        # Delegate to codec.
        result = self._codec.encode(text, current, target, field_state)

        # Areka suppression produces valid empty output — skip quality check.
        if "areka_suppression" in result["strategies_applied"]:
            motor_output = {
                "output_text": result["output"],
                "target_profile": target,
                "strategies_applied": result["strategies_applied"],
                "repair_passed": True,
                "transform_magnitude": result["transform_magnitude"],
            }
            return {**state, "motor_output": motor_output}

        # Repair check: verify output preserves content adequately.
        repair_passed = self._codec.quality_check(text, result["output"])

        if not repair_passed:
            self._consecutive_repair_failures += 1
            # Fall back to original text on repair failure.
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

    def repair_check(self, state: SystemState) -> bool:
        motor_output = state.get("motor_output")
        if motor_output is None:
            return False
        return motor_output.get("repair_passed", False)

    def apoptotic_condition(self, state: SystemState) -> bool:
        if state["input"] is None:
            return True
        return self._consecutive_repair_failures >= 3
