"""Tests for feedback loops — Motor→Conscious retry, Conscious→Sensory re-examination,
Conscious→Immune threshold adjustment, and FeedbackSignals infrastructure.

All tests are deterministic — no LLM calls, no API keys.
"""

from unittest.mock import patch

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import (
    _after_conscious,
    _after_motor,
    _default_feedback,
    build_graph,
    create_default_state,
)
from agenetic.systems.conscious import ConsciousSystem
from agenetic.systems.deliberator import DeliberationRequest, MockDeliberator
from agenetic.systems.genetic import GeneticSystem
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.subconscious import SubconsciousSystem


# -- Inputs --

# High deviation: subconscious escalates as novel signal.
ESCALATION_INPUT = "test"

# Low deviation: subconscious doesn't escalate.
REFLEX_INPUT = "The quick brown fox jumps over the lazy dog."


# -- Custom deliberators --


class _ReExamineOnceDeliberator:
    """Deliberator that requests re-examination on first call, then proceeds normally."""

    def __init__(self):
        self.call_count = 0

    def deliberate(self, request: DeliberationRequest):
        self.call_count += 1
        base = MockDeliberator().deliberate(request)
        if self.call_count == 1:
            base["re_examine"] = True
        else:
            base["re_examine"] = False
        return base


class _AlwaysReExamineDeliberator:
    """Deliberator that always requests re-examination."""

    def deliberate(self, request: DeliberationRequest):
        base = MockDeliberator().deliberate(request)
        base["re_examine"] = True
        return base


# -- Custom codec that always fails quality check --


class _FailingCodec:
    """Codec whose quality_check always returns False, triggering motor repair failure."""

    @property
    def name(self):
        return "failing_test"

    def encode(self, input_data, current_features, target_profile, field_state):
        return {
            "output": input_data,
            "strategies_applied": ["test_noop"],
            "transform_magnitude": 0.0,
        }

    def quality_check(self, original, output):
        return False


# -- Helpers --


def _build_graph(deliberator=None, failing_motor=False):
    """Build full graph with optional deliberator and failing motor."""
    if deliberator is None:
        deliberator = MockDeliberator()
    motor = MotorSystem()
    if failing_motor:
        motor._codec = _FailingCodec()
    return build_graph(
        sensory=SensorySystem(),
        immune=ImmuneSystem(),
        subconscious=SubconsciousSystem(),
        conscious=ConsciousSystem(deliberator=deliberator),
        motor=motor,
        sleep=SleepSystem(),
        genetic=GeneticSystem(),
    )


def _make_escalation_state(input_data=ESCALATION_INPUT):
    """Create default state with escalation input."""
    return create_default_state(input_data=input_data)


# =========================================================
# Motor→Conscious retry tests (5)
# =========================================================


class TestMotorRetryOnRepairFailure:
    """Motor→Conscious feedback: retry when repair fails."""

    def test_motor_retry_on_repair_failure(self):
        """When motor repair fails, graph retries via conscious."""
        graph = _build_graph(failing_motor=True)
        state = _make_escalation_state()
        result = graph.invoke(state)

        history = result["metadata"]["routing_history"]
        # Motor and conscious should each appear twice (original + retry).
        assert history.count("motor") == 2
        assert history.count("conscious") == 2

    def test_motor_no_retry_on_success(self):
        """Normal motor success: no retry, motor appears once."""
        graph = _build_graph()
        state = _make_escalation_state()
        result = graph.invoke(state)

        history = result["metadata"]["routing_history"]
        assert history.count("motor") == 1

    def test_motor_max_one_retry(self):
        """Motor that always fails: exactly 2 motor attempts, not infinite."""
        graph = _build_graph(failing_motor=True)
        state = _make_escalation_state()
        result = graph.invoke(state)

        history = result["metadata"]["routing_history"]
        assert history.count("motor") == 2  # Original + 1 retry, no more.

    def test_motor_retry_count_incremented(self):
        """After a retry, feedback.motor_retry_count is 1."""
        graph = _build_graph(failing_motor=True)
        state = _make_escalation_state()
        result = graph.invoke(state)

        feedback = result.get("feedback")
        assert feedback is not None
        assert feedback["motor_retry_count"] == 1

    def test_motor_retry_disabled_when_weight_zero(self):
        """_after_motor returns __end__ when topology weight is 0."""
        state = {
            "motor_output": {"repair_passed": False},
            "feedback": _default_feedback(),
        }
        with patch(
            "agenetic.network.graph._get_topology_weight", return_value=0.0
        ):
            assert _after_motor(state) == "__end__"


# =========================================================
# Conscious→Sensory re-examination tests (4)
# =========================================================


class TestConscousReExamination:
    """Conscious→Sensory feedback: re-examination loop."""

    def test_re_examine_routes_back_to_sensory(self):
        """When deliberator requests re-examine, sensory runs again."""
        deliberator = _ReExamineOnceDeliberator()
        graph = _build_graph(deliberator=deliberator)
        state = _make_escalation_state()
        result = graph.invoke(state)

        history = result["metadata"]["routing_history"]
        assert history.count("sensory") == 2

    def test_re_examine_max_one(self):
        """Always-re-examine deliberator: sensory runs at most twice."""
        deliberator = _AlwaysReExamineDeliberator()
        graph = _build_graph(deliberator=deliberator)
        state = _make_escalation_state()
        result = graph.invoke(state)

        history = result["metadata"]["routing_history"]
        assert history.count("sensory") == 2  # Original + 1 re-examine, capped.

    def test_re_examine_count_incremented(self):
        """After re-examination, feedback.re_examine_count is 1."""
        deliberator = _ReExamineOnceDeliberator()
        graph = _build_graph(deliberator=deliberator)
        state = _make_escalation_state()
        result = graph.invoke(state)

        feedback = result.get("feedback")
        assert feedback is not None
        assert feedback["re_examine_count"] == 1

    def test_no_re_examine_when_false(self):
        """Default MockDeliberator (re_examine=False): sensory runs once."""
        graph = _build_graph()
        state = _make_escalation_state()
        result = graph.invoke(state)

        history = result["metadata"]["routing_history"]
        assert history.count("sensory") == 1


# =========================================================
# Conscious→Immune threshold adjustment tests (4)
# =========================================================


class TestImmuneThresholdAdjustment:
    """Conscious→Immune: threshold adjustments via state propagation."""

    def _make_immune_state(self, entropy=5.0, feedback=None):
        """Create a state suitable for immune processing."""
        state = create_default_state(input_data="test input")
        state["signal_report"] = {
            "features": {
                "density": 0.8, "entropy": entropy, "coherence": 0.7,
                "periodicity": 0.1, "noise_floor": 0.05, "impedance": 0.1,
                "bigram_entropy": 3.0,
                "token_count": 10, "vocabulary_richness": 0.5,
            },
            "classification": {"signal_type": "steady_state", "confidence": 0.9, "components": []},
            "delta": {
                "density_delta": 0.0, "entropy_delta": 0.0, "coherence_delta": 0.0,
                "periodicity_delta": 0.0, "noise_delta": 0.0, "impedance_delta": 0.0,
                "aggregate_deviation": 1.0, "activated_limbs": [],
            },
            "tick": 0, "input_hash": "test_hash",
        }
        state["feedback"] = feedback
        return state

    def test_immune_uses_default_thresholds_without_feedback(self):
        """Without feedback, entropy > 6.0 triggers anomaly."""
        immune = ImmuneSystem()
        # Entropy 5.0 — below default 6.0 threshold, no anomaly.
        state = self._make_immune_state(entropy=5.0, feedback=None)
        result = immune.process(state)
        assert "entropy" not in result["threat_assessment"]["anomaly_scores"]

    def test_immune_respects_threshold_adjustment(self):
        """Lowering entropy threshold from 6.0 to 4.0 triggers anomaly at 5.0."""
        immune = ImmuneSystem()
        feedback = {
            "motor_retry_count": 0,
            "re_examine_count": 0,
            "immune_threshold_adjustments": {"entropy_threshold": -2.0},
        }
        state = self._make_immune_state(entropy=5.0, feedback=feedback)
        result = immune.process(state)
        assert "entropy" in result["threat_assessment"]["anomaly_scores"]
        assert result["threat_assessment"]["anomaly_scores"]["entropy"] == 1.0  # 5.0 - 4.0

    def test_immune_multiple_adjustments(self):
        """Multiple threshold adjustments all take effect."""
        immune = ImmuneSystem()
        feedback = {
            "motor_retry_count": 0,
            "re_examine_count": 0,
            "immune_threshold_adjustments": {
                "entropy_threshold": -2.0,
                "noise_floor_threshold": -0.3,
            },
        }
        # Entropy 5.0 (threshold lowered to 4.0) + noise_floor 0.1 (threshold lowered to 0.05)
        state = self._make_immune_state(entropy=5.0, feedback=feedback)
        state["signal_report"]["features"]["noise_floor"] = 0.1
        result = immune.process(state)
        assert "entropy" in result["threat_assessment"]["anomaly_scores"]
        assert "noise_floor" in result["threat_assessment"]["anomaly_scores"]

    def test_immune_adjustment_zero_is_noop(self):
        """Explicit zero adjustment is identical to no feedback."""
        immune = ImmuneSystem()
        feedback = {
            "motor_retry_count": 0,
            "re_examine_count": 0,
            "immune_threshold_adjustments": {"entropy_threshold": 0.0},
        }
        # Entropy 5.0 — below threshold 6.0, no anomaly even with explicit 0.0 adjustment.
        state = self._make_immune_state(entropy=5.0, feedback=feedback)
        result = immune.process(state)
        assert "entropy" not in result["threat_assessment"]["anomaly_scores"]


# =========================================================
# FeedbackSignals infrastructure tests (3)
# =========================================================


class TestFeedbackInfrastructure:
    """FeedbackSignals TypedDict and graph plumbing."""

    def test_default_state_has_feedback_none(self):
        """create_default_state() returns feedback: None."""
        state = create_default_state()
        assert "feedback" in state
        assert state["feedback"] is None

    def test_graph_preserves_feedback(self):
        """Feedback set in initial state survives graph invocation."""
        graph = _build_graph()
        state = create_default_state(input_data=REFLEX_INPUT)
        state["feedback"] = {
            "motor_retry_count": 0,
            "re_examine_count": 0,
            "immune_threshold_adjustments": {"entropy_threshold": -1.0},
        }
        result = graph.invoke(state)
        assert result.get("feedback") is not None
        assert result["feedback"]["immune_threshold_adjustments"]["entropy_threshold"] == -1.0

    def test_conscious_output_has_re_examine(self):
        """After escalation, conscious_output includes re_examine bool."""
        graph = _build_graph()
        state = _make_escalation_state()
        result = graph.invoke(state)
        conscious_output = result.get("conscious_output")
        assert conscious_output is not None
        assert "re_examine" in conscious_output
        assert isinstance(conscious_output["re_examine"], bool)
