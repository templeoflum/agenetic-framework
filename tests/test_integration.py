"""End-to-end path tests through the full graph.

Covers three routing paths:
- Reflex path (4 tests): subconscious doesn't escalate, motor processes directly
- Escalated path (4 tests): subconscious escalates, conscious deliberates, motor processes
- Suppression path (3 tests): conscious gate suppresses, motor produces empty output
- Routing decision tests (3 tests): default is reflex, threat triggers escalation, familiar stays reflex
- Cross-path consistency (2 tests): motor output always present, signal report preserved

All tests are deterministic — no LLM calls, no API keys.
"""

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import build_graph, create_default_state
from agenetic.systems.base import AREKA_ID
from agenetic.systems.conscious import ConsciousSystem
from agenetic.systems.deliberator import MockDeliberator
from agenetic.systems.genetic import GeneticSystem
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.subconscious import SubconsciousSystem


# -- Input constants --

# Low deviation: subconscious doesn't escalate (aggregate_deviation ~0.73).
REFLEX_INPUT = "The quick brown fox jumps over the lazy dog."

# High deviation: subconscious escalates as novel signal (aggregate_deviation ~3.57).
ESCALATION_INPUT = "test"

# Noise classified input with high deviation + high Areka → conscious gate suppresses.
NOISE_INPUT = "a ! b # c $ d % e ^ f & g * h ( i ) j + k = l ; m @ n ~ o"

# Medium threat: immune flags as medium, subconscious escalates on threat.
THREAT_INPUT = "x x x x x x x x x x x x x x x x x x x"


def _build_graph(deliberator=None):
    """Build full graph with optional deliberator."""
    if deliberator is None:
        deliberator = MockDeliberator()
    return build_graph(
        sensory=SensorySystem(),
        immune=ImmuneSystem(),
        subconscious=SubconsciousSystem(),
        conscious=ConsciousSystem(deliberator=deliberator),
        motor=MotorSystem(),
        sleep=SleepSystem(),
        genetic=GeneticSystem(),
    )


def _make_areka_field(weight=0.9):
    """Create field with high Areka weight for suppression testing."""
    field = OrientationalField()
    limbs = field.read()["limbs"]
    for limb in limbs:
        if limb["id"] == AREKA_ID:
            limb["weight"] = weight
    field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
    return field


def _get_cached_pattern(input_text, outcome="reflex_response"):
    """Pre-compute signal features and return a cache entry for the input."""
    sensory = SensorySystem()
    state = create_default_state(input_data=input_text)
    result = sensory.process(state)
    report = result["signal_report"]
    f = report["features"]
    return {
        "input_hash": report["input_hash"],
        "feature_vector": [
            f["density"], f["entropy"], f["coherence"],
            f["periodicity"], f["noise_floor"], f["impedance"],
        ],
        "signal_type": report["classification"]["signal_type"],
        "outcome": outcome,
        "response_pattern_id": None,
        "encounter_count": 5,
        "last_seen_tick": 0,
    }


# ============================================================
# Reflex path tests (4)
# ============================================================


class TestReflexPath:

    def test_reflex_path_skips_conscious(self):
        """Low-deviation input takes reflex path — conscious NOT in routing."""
        graph = _build_graph()
        state = create_default_state(input_data=REFLEX_INPUT)
        result = graph.invoke(state)
        history = result["metadata"]["routing_history"]
        assert "conscious" not in history
        assert "motor" in history

    def test_reflex_path_motor_processes_input(self):
        """Motor produces output on reflex path with restructured text."""
        graph = _build_graph()
        state = create_default_state(input_data=REFLEX_INPUT)
        result = graph.invoke(state)
        motor_output = result["motor_output"]
        assert isinstance(motor_output["output_text"], str)
        assert len(motor_output["output_text"]) > 0
        assert motor_output["repair_passed"] is True

    def test_reflex_path_subconscious_decision(self):
        """Subconscious output exists with escalation_recommended=False on reflex path."""
        graph = _build_graph()
        state = create_default_state(input_data=REFLEX_INPUT)
        result = graph.invoke(state)
        sub_output = result["subconscious_output"]
        assert sub_output is not None
        assert sub_output["escalation_recommended"] is False

    def test_reflex_path_signal_report_flows(self):
        """Signal report, threat assessment, subconscious output all populated on reflex path."""
        graph = _build_graph()
        state = create_default_state(input_data=REFLEX_INPUT)
        result = graph.invoke(state)
        assert result["signal_report"] is not None
        assert result["threat_assessment"] is not None
        assert result["subconscious_output"] is not None
        # Only conscious_output is None on reflex path.
        assert result["conscious_output"] is None


# ============================================================
# Escalated path tests (4)
# ============================================================


class TestEscalatedPath:

    def test_escalated_path_includes_conscious(self):
        """High-deviation input triggers escalation — conscious in routing."""
        graph = _build_graph()
        state = create_default_state(input_data=ESCALATION_INPUT)
        result = graph.invoke(state)
        history = result["metadata"]["routing_history"]
        assert "conscious" in history
        assert "motor" in history

    def test_escalated_path_conscious_output_present(self):
        """Conscious output exists with all required fields on escalated path."""
        graph = _build_graph()
        state = create_default_state(input_data=ESCALATION_INPUT)
        result = graph.invoke(state)
        co = result["conscious_output"]
        assert co is not None
        assert "decision" in co
        assert "expression" in co
        assert "lineage" in co
        assert "proceed" in co
        assert "confidence" in co

    def test_escalated_path_motor_receives_conscious(self):
        """Motor records conscious_strategy when conscious proceeds."""
        graph = _build_graph()
        state = create_default_state(input_data=ESCALATION_INPUT)
        result = graph.invoke(state)
        mo = result["motor_output"]
        assert mo is not None
        # MockDeliberator always proceeds.
        assert result["conscious_output"]["proceed"] is True
        assert "conscious_strategy" in mo
        assert mo["conscious_strategy"] == "direct_response"

    def test_escalated_path_uses_mock_deliberator(self):
        """Graph with MockDeliberator produces conscious_output with deliberation_model='mock'."""
        mock = MockDeliberator()
        graph = _build_graph(deliberator=mock)
        state = create_default_state(input_data=ESCALATION_INPUT)
        result = graph.invoke(state)
        assert result["conscious_output"]["lineage"]["deliberation_model"] == "mock"


# ============================================================
# Suppression path tests (3)
# ============================================================


class TestSuppressionPath:

    def test_suppression_path_motor_empty(self):
        """Conscious suppresses → motor produces empty output with conscious_suppression."""
        field = _make_areka_field(0.9)
        graph = _build_graph()
        state = create_default_state(input_data=NOISE_INPUT, field=field)
        result = graph.invoke(state)
        mo = result["motor_output"]
        assert mo["output_text"] == ""
        assert "conscious_suppression" in mo["strategies_applied"]

    def test_suppression_path_lineage(self):
        """Suppression output has proceed=False and gate explains why."""
        field = _make_areka_field(0.9)
        graph = _build_graph()
        state = create_default_state(input_data=NOISE_INPUT, field=field)
        result = graph.invoke(state)
        co = result["conscious_output"]
        assert co["proceed"] is False
        gate = co["lineage"]["gate_evaluation"]
        assert gate["reason"] == "areka_suppression"
        mo = result["motor_output"]
        assert "conscious_suppression" in mo["strategies_applied"]

    def test_suppression_path_no_deliberator_call(self):
        """On suppression, MockDeliberator's call_count should be 0."""
        mock = MockDeliberator()
        field = _make_areka_field(0.9)
        graph = _build_graph(deliberator=mock)
        state = create_default_state(input_data=NOISE_INPUT, field=field)
        result = graph.invoke(state)
        assert mock.call_count == 0


# ============================================================
# Routing decision tests (3)
# ============================================================


class TestRoutingDecisions:

    def test_routing_default_is_reflex(self):
        """create_default_state() with low-deviation input → reflex path."""
        graph = _build_graph()
        state = create_default_state(input_data=REFLEX_INPUT)
        result = graph.invoke(state)
        assert "conscious" not in result["metadata"]["routing_history"]

    def test_routing_subconscious_escalates_on_threat(self):
        """Input producing medium threat → subconscious escalates → conscious fires."""
        graph = _build_graph()
        state = create_default_state(input_data=THREAT_INPUT)
        result = graph.invoke(state)
        assert result["threat_assessment"]["threat_level"] == "medium"
        assert result["subconscious_output"]["escalation_recommended"] is True
        assert "conscious" in result["metadata"]["routing_history"]

    def test_routing_subconscious_no_escalate_on_familiar(self):
        """Cached reflex pattern → subconscious does NOT escalate → reflex path."""
        graph = _build_graph()
        state = create_default_state(input_data=REFLEX_INPUT)
        # Seed cache with a reflex_response pattern matching this input.
        state["signal_pattern_cache"] = [_get_cached_pattern(REFLEX_INPUT, "reflex_response")]
        result = graph.invoke(state)
        assert result["subconscious_output"]["escalation_recommended"] is False
        assert "conscious" not in result["metadata"]["routing_history"]


# ============================================================
# Cross-path consistency tests (2)
# ============================================================


class TestCrossPathConsistency:

    def test_both_paths_produce_motor_output(self):
        """Motor output always exists regardless of path taken."""
        graph = _build_graph()

        # Reflex path.
        state_reflex = create_default_state(input_data=REFLEX_INPUT)
        result_reflex = graph.invoke(state_reflex)
        mo_reflex = result_reflex["motor_output"]
        assert mo_reflex is not None
        assert "output_text" in mo_reflex
        assert "target_profile" in mo_reflex
        assert "strategies_applied" in mo_reflex
        assert "repair_passed" in mo_reflex
        assert "transform_magnitude" in mo_reflex

        # Escalated path.
        state_escalated = create_default_state(input_data=ESCALATION_INPUT)
        result_escalated = graph.invoke(state_escalated)
        mo_escalated = result_escalated["motor_output"]
        assert mo_escalated is not None
        assert "output_text" in mo_escalated
        assert "target_profile" in mo_escalated
        assert "strategies_applied" in mo_escalated
        assert "repair_passed" in mo_escalated
        assert "transform_magnitude" in mo_escalated

    def test_both_paths_preserve_signal_report(self):
        """Signal report is identical structure regardless of path."""
        graph = _build_graph()

        state_reflex = create_default_state(input_data=REFLEX_INPUT)
        result_reflex = graph.invoke(state_reflex)
        sr_reflex = result_reflex["signal_report"]

        state_escalated = create_default_state(input_data=ESCALATION_INPUT)
        result_escalated = graph.invoke(state_escalated)
        sr_escalated = result_escalated["signal_report"]

        # Same structure: features, classification, delta, tick, input_hash.
        for key in ["features", "classification", "delta", "tick", "input_hash"]:
            assert key in sr_reflex, f"Reflex missing {key}"
            assert key in sr_escalated, f"Escalated missing {key}"
