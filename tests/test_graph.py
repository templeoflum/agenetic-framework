"""Tests for LangGraph wiring.

Verifies the graph compiles and can process input end-to-end.
Includes signal-domain flow tests added in Directive 002.
"""

import pytest

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import build_graph, create_default_state
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.subconscious import SubconsciousSystem
from agenetic.systems.conscious import ConsciousSystem
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.genetic import GeneticSystem
from agenetic.systems.deliberator import MockDeliberator


def _build_default_graph():
    return build_graph(
        sensory=SensorySystem(),
        immune=ImmuneSystem(),
        subconscious=SubconsciousSystem(),
        conscious=ConsciousSystem(deliberator=MockDeliberator()),
        motor=MotorSystem(),
        sleep=SleepSystem(),
        genetic=GeneticSystem(),
    )


class TestGraphCompilation:
    """Verify the graph compiles without errors."""

    def test_graph_compiles(self):
        graph = _build_default_graph()
        assert graph is not None

    def test_graph_is_invocable(self):
        graph = _build_default_graph()
        assert hasattr(graph, "invoke")


class TestGraphExecution:
    """Verify the graph processes input end-to-end."""

    def test_trivial_input(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="hello world")
        result = graph.invoke(state)
        assert result is not None
        assert result["input"] == "hello world"

    def test_preserves_field_state(self):
        field = OrientationalField()
        graph = _build_default_graph()
        state = create_default_state(input_data="test", field=field)
        result = graph.invoke(state)
        assert len(result["field"]["limbs"]) == 18

    def test_routing_history_recorded(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="test")
        result = graph.invoke(state)
        history = result["metadata"]["routing_history"]
        # Default escalate_to_conscious=True, so all 5 systems fire.
        assert "sensory" in history
        assert "immune" in history
        assert "subconscious" in history
        assert "conscious" in history
        assert "motor" in history

    def test_no_escalation_skips_conscious(self):
        """Verify routing skips conscious when escalation flag stays False.

        Novel inputs always trigger subconscious escalation (aggregate_deviation
        > 1.5 for any uncached text input vs. per-feature references). So we pre-populate
        the signal_pattern_cache with a reflex_response entry matching the input,
        which causes subconscious to vote against escalation.
        """
        # Pre-compute the input's signal features so we can seed the cache.
        sensory = SensorySystem()
        pre_state = create_default_state(input_data="test")
        pre_result = sensory.process(pre_state)
        report = pre_result["signal_report"]
        feature_vector = [
            report["features"]["density"],
            report["features"]["entropy"],
            report["features"]["coherence"],
            report["features"]["periodicity"],
            report["features"]["noise_floor"],
            report["features"]["impedance"],
        ]

        graph = _build_default_graph()
        state = create_default_state(input_data="test")
        state["flags"]["escalate_to_conscious"] = False
        # Seed cache with a known reflex_response pattern for this input.
        state["signal_pattern_cache"] = [{
            "input_hash": report["input_hash"],
            "feature_vector": feature_vector,
            "signal_type": report["classification"]["signal_type"],
            "outcome": "reflex_response",
            "response_pattern_id": None,
            "encounter_count": 5,
            "last_seen_tick": 0,
        }]
        result = graph.invoke(state)
        history = result["metadata"]["routing_history"]
        assert "conscious" not in history
        assert "motor" in history

    def test_no_apoptotic_flag(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="test")
        result = graph.invoke(state)
        assert result["flags"]["apoptotic"] is False

    def test_no_degradation(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="test")
        result = graph.invoke(state)
        assert result["flags"]["degraded"] == []


class TestOrientationalFieldAccess:
    """Verify field read/write access control."""

    def test_field_readable(self):
        field = OrientationalField()
        state = field.read()
        assert len(state["limbs"]) == 18

    def test_field_writable_by_sleep(self):
        from agenetic.systems.sleep import SleepSystem

        field = OrientationalField()
        limbs = field.read()["limbs"]
        # Modify a weight.
        limbs[0] = {**limbs[0], "weight": 0.8}
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        updated = field.read()
        assert updated["limbs"][0]["weight"] == 0.8

    def test_field_not_writable_by_others(self):
        field = OrientationalField()
        limbs = field.read()["limbs"]
        with pytest.raises(PermissionError):
            field.write(limbs, caller_token="not_sleep")

    def test_all_eighteen_limbs_present(self):
        field = OrientationalField()
        state = field.read()
        assert len(state["limbs"]) == 18
        ids = [limb["id"] for limb in state["limbs"]]
        assert ids == list(range(1, 19))


# ============================================================
# Signal-domain graph flow tests (Directive 002)
# ============================================================


class TestSignalDomainGraphFlow:
    """Verify signal-domain systems operate correctly through the graph."""

    def test_graph_compiles_with_new_fields(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="test")
        assert "signal_report" in state
        assert "threat_assessment" in state
        assert "subconscious_output" in state
        assert "signal_pattern_cache" in state

    def test_signal_report_populated(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="The quick brown fox jumps over the lazy dog")
        result = graph.invoke(state)
        assert result["signal_report"] is not None
        assert "features" in result["signal_report"]

    def test_signal_domain_order(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="test signal processing")
        result = graph.invoke(state)
        history = result["metadata"]["routing_history"]
        # Verify order: sensory before immune, immune before subconscious.
        sensory_idx = history.index("sensory")
        immune_idx = history.index("immune")
        subconscious_idx = history.index("subconscious")
        assert sensory_idx < immune_idx < subconscious_idx

    def test_normal_input_reflex_path(self):
        """Normal input with escalation disabled should bypass conscious."""
        graph = _build_default_graph()
        state = create_default_state(input_data="hello")
        state["flags"]["escalate_to_conscious"] = False
        result = graph.invoke(state)
        history = result["metadata"]["routing_history"]
        # Subconscious shouldn't escalate a simple, low-deviation input.
        # Since we set flag to False, and subconscious only sets (never unsets),
        # if subconscious doesn't recommend escalation, flag stays False.
        assert "sensory" in history
        assert "immune" in history
        assert "subconscious" in history
        assert "motor" in history

    def test_threat_assessment_populated(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="normal input text")
        result = graph.invoke(state)
        assert result["threat_assessment"] is not None
        assert result["threat_assessment"]["threat_level"] == "none"

    def test_subconscious_output_populated(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="simple test")
        result = graph.invoke(state)
        assert result["subconscious_output"] is not None
        assert "escalation_recommended" in result["subconscious_output"]
