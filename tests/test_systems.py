"""Tests for the seven system stubs.

Verifies all systems instantiate, implement the BaseSystem interface,
and pass through state correctly as no-ops.
"""

import pytest

from agenetic.systems.base import BaseSystem, SystemState
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.subconscious import SubconsciousSystem
from agenetic.systems.conscious import ConsciousSystem
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.genetic import GeneticSystem
from agenetic.network.graph import create_default_state


ALL_SYSTEM_CLASSES = [
    SensorySystem,
    ImmuneSystem,
    SubconsciousSystem,
    ConsciousSystem,
    MotorSystem,
    SleepSystem,
    GeneticSystem,
]


@pytest.fixture
def sample_state() -> SystemState:
    return create_default_state(input_data="test input")


@pytest.fixture(params=ALL_SYSTEM_CLASSES)
def system(request) -> BaseSystem:
    return request.param()


class TestSystemInterface:
    """Verify all systems implement the BaseSystem interface."""

    def test_inherits_from_base(self, system: BaseSystem):
        assert isinstance(system, BaseSystem)

    def test_has_name(self, system: BaseSystem):
        assert isinstance(system.name, str)
        assert len(system.name) > 0

    def test_has_description(self, system: BaseSystem):
        assert isinstance(system.description, str)
        assert len(system.description) > 0

    def test_has_tick_rate(self, system: BaseSystem):
        valid_rates = {"every_cycle", "on_escalation", "on_demand", "periodic", "read_only"}
        assert system.tick_rate in valid_rates

    def test_process_returns_state(self, system: BaseSystem, sample_state: SystemState):
        result = system.process(sample_state)
        assert isinstance(result, dict)
        assert "input" in result
        assert "field" in result
        assert "immune_log" in result
        assert "metadata" in result
        assert "flags" in result

    def test_process_passes_through(self, system: BaseSystem, sample_state: SystemState):
        result = system.process(sample_state)
        assert result["input"] == sample_state["input"]

    def test_repair_check_returns_true(self, system: BaseSystem, sample_state: SystemState):
        assert system.repair_check(sample_state) is True

    def test_apoptotic_condition_returns_false(self, system: BaseSystem, sample_state: SystemState):
        assert system.apoptotic_condition(sample_state) is False


class TestSystemNames:
    """Verify all seven expected systems exist with correct names."""

    def test_all_seven_exist(self):
        systems = [cls() for cls in ALL_SYSTEM_CLASSES]
        names = {s.name for s in systems}
        expected = {"sensory", "immune", "subconscious", "conscious", "motor", "sleep", "genetic"}
        assert names == expected

    def test_tick_rates(self):
        systems = {cls().name: cls() for cls in ALL_SYSTEM_CLASSES}
        assert systems["sensory"].tick_rate == "every_cycle"
        assert systems["immune"].tick_rate == "every_cycle"
        assert systems["subconscious"].tick_rate == "every_cycle"
        assert systems["conscious"].tick_rate == "on_escalation"
        assert systems["motor"].tick_rate == "on_demand"
        assert systems["sleep"].tick_rate == "periodic"
        assert systems["genetic"].tick_rate == "read_only"
