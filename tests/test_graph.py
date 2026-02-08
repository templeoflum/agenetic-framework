"""Tests for LangGraph wiring.

Verifies the graph compiles and can process a trivial input end-to-end,
even with all systems as no-ops.
"""

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import build_graph, create_default_state
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.subconscious import SubconsciousSystem
from agenetic.systems.conscious import ConsciousSystem
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.genetic import GeneticSystem


def _build_default_graph():
    return build_graph(
        sensory=SensorySystem(),
        immune=ImmuneSystem(),
        subconscious=SubconsciousSystem(),
        conscious=ConsciousSystem(),
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
        # Phase 1 with escalation: sensory -> immune -> subconscious -> conscious -> motor
        assert "sensory" in history
        assert "immune" in history
        assert "subconscious" in history
        assert "conscious" in history
        assert "motor" in history

    def test_no_escalation_skips_conscious(self):
        graph = _build_default_graph()
        state = create_default_state(input_data="test")
        # Disable escalation.
        state["flags"]["escalate_to_conscious"] = False
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
        import pytest

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
