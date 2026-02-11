"""Tests for immune system escalation — D016 audit remediation.

Covers:
- Critical threat sets escalation flag (1 test)
- Non-critical threat does not set flag (1 test)
- Immune flag combines with subconscious via OR-preservation (1 test)

All tests are deterministic — no LLM calls, no API keys.
"""

from agenetic.network.graph import create_default_state
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.subconscious import SubconsciousSystem


def _make_report_state(**feature_overrides):
    """Create a state with a custom signal report for immune testing."""
    state = create_default_state(input_data="test")
    defaults = {
        "density": 0.8, "entropy": 3.5, "coherence": 0.7,
        "periodicity": 0.1, "noise_floor": 0.05, "impedance": 0.1,
        "token_count": 10, "vocabulary_richness": 0.8,
    }
    defaults.update(feature_overrides)
    state["signal_report"] = {
        "features": defaults,
        "classification": {"signal_type": "steady_state", "confidence": 0.9, "components": []},
        "delta": {
            "density_delta": 0.0, "entropy_delta": 0.0, "coherence_delta": 0.0,
            "periodicity_delta": 0.0, "noise_delta": 0.0, "impedance_delta": 0.0,
            "aggregate_deviation": 0.5, "activated_limbs": [],
        },
        "tick": 0, "input_hash": "test123",
    }
    return state


class TestImmuneEscalation:

    def test_critical_threat_sets_escalation_flag(self):
        """Critical-level threat sets escalate_to_conscious flag."""
        immune = ImmuneSystem()
        state = _make_report_state(entropy=12.0, noise_floor=0.9, impedance=1.0)
        state["signal_report"]["delta"]["aggregate_deviation"] = 10.0
        result = immune.process(state)
        assert result["threat_assessment"]["threat_level"] == "critical"
        assert result["flags"]["escalate_to_conscious"] is True

    def test_non_critical_threat_does_not_set_flag(self):
        """Low/none threat does not set escalation flag."""
        immune = ImmuneSystem()
        state = _make_report_state()
        result = immune.process(state)
        assert result["threat_assessment"]["threat_level"] == "none"
        assert result["flags"]["escalate_to_conscious"] is False

    def test_immune_flag_combines_with_subconscious(self):
        """Immune sets flag for critical threat, subconscious OR-preserves it."""
        immune = ImmuneSystem()
        sub = SubconsciousSystem()

        state = _make_report_state(entropy=12.0, noise_floor=0.9, impedance=1.0)
        state["signal_report"]["delta"]["aggregate_deviation"] = 10.0

        # Run immune first — sets flag
        state = immune.process(state)
        assert state["flags"]["escalate_to_conscious"] is True

        # Run subconscious — flag survives via OR-preservation
        state = sub.process(state)
        assert state["flags"]["escalate_to_conscious"] is True
