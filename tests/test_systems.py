"""Tests for the seven systems.

Verifies all systems instantiate and implement the BaseSystem interface.
Includes comprehensive tests for the three signal-domain systems
(sensory, immune, subconscious) added in Directive 002.
"""

import math

import pytest

from agenetic.systems.base import BaseSystem, SystemState
from agenetic.systems.sensory import SensorySystem, _compute_input_hash
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


def _make_sample_state(input_data="test input") -> SystemState:
    """Create a sample state with all fields populated for testing.

    Includes valid signal-domain outputs so repair_check passes for all systems.
    """
    state = create_default_state(input_data=input_data)
    # Populate signal-domain outputs so repair_check works for all systems.
    state["signal_report"] = {
        "features": {
            "density": 0.8, "entropy": 3.5, "coherence": 0.7,
            "periodicity": 0.1, "noise_floor": 0.05, "impedance": 0.1,
            "bigram_entropy": 3.0,
            "token_count": 2, "vocabulary_richness": 1.0,
        },
        "classification": {"signal_type": "steady_state", "confidence": 0.9, "components": []},
        "delta": {
            "density_delta": -0.2, "entropy_delta": 2.5, "coherence_delta": -0.3,
            "periodicity_delta": -0.9, "noise_delta": -0.95, "impedance_delta": -0.9,
            "aggregate_deviation": 1.5, "activated_limbs": [],
        },
        "tick": 0, "input_hash": "abc123def456",
    }
    state["threat_assessment"] = {
        "is_anomalous": False, "anomaly_scores": {},
        "matched_patterns": [], "threat_level": "none",
        "recommended_action": "proceed",
    }
    state["subconscious_output"] = {
        "escalation_recommended": False, "escalation_confidence": 0.5,
        "matched_pattern_ids": [], "primed_associations": [],
    }
    state["conscious_output"] = None  # Conscious hasn't fired in sample state
    state["motor_output"] = {
        "output_text": input_data if isinstance(input_data, str) else str(input_data),
        "target_profile": {
            "density": 0.8, "entropy": 3.5, "coherence": 0.35,
            "periodicity": 0.0, "noise_floor": 0.0, "impedance": 0.0,
            "bigram_entropy": 0.0,
            "token_count": 0, "vocabulary_richness": 0.0,
        },
        "strategies_applied": [],
        "repair_passed": True,
        "transform_magnitude": 0.0,
    }
    state["genetic_output"] = None
    state["feedback"] = None
    return state


@pytest.fixture
def sample_state() -> SystemState:
    return _make_sample_state()


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


# ============================================================
# Sensory System Tests
# ============================================================


class TestSensorySystem:
    """Comprehensive tests for the sensory signal characterization system."""

    def test_process_string_input(self):
        sensory = SensorySystem()
        state = create_default_state(input_data="The quick brown fox jumps over the lazy dog.")
        result = sensory.process(state)
        report = result["signal_report"]
        assert report is not None
        assert "features" in report
        assert "classification" in report
        assert "delta" in report
        assert "tick" in report
        assert "input_hash" in report

    def test_process_string_features_populated(self):
        sensory = SensorySystem()
        state = create_default_state(input_data="Hello world this is a test of signal processing")
        result = sensory.process(state)
        features = result["signal_report"]["features"]
        assert features["token_count"] == 9
        assert 0.0 <= features["density"] <= 1.0
        assert features["entropy"] >= 0.0
        assert 0.0 <= features["coherence"] <= 1.0
        assert 0.0 <= features["periodicity"] <= 1.0
        assert 0.0 <= features["noise_floor"] <= 1.0
        assert 0.0 <= features["impedance"] <= 1.0
        assert 0.0 <= features["vocabulary_richness"] <= 1.0

    def test_process_empty_string(self):
        sensory = SensorySystem()
        state = create_default_state(input_data="")
        result = sensory.process(state)
        report = result["signal_report"]
        assert report["classification"]["signal_type"] == "noise"
        assert report["features"]["token_count"] == 0

    def test_process_none_input(self):
        sensory = SensorySystem()
        state = create_default_state(input_data=None)
        result = sensory.process(state)
        report = result["signal_report"]
        assert report["classification"]["signal_type"] == "noise"
        assert report["classification"]["confidence"] == 1.0
        assert report["features"]["density"] == 0.0
        assert report["features"]["entropy"] == 0.0
        assert report["features"]["token_count"] == 0

    def test_entropy_deterministic(self):
        sensory = SensorySystem()
        text = "the cat sat on the mat and the cat purred"
        state1 = create_default_state(input_data=text)
        state2 = create_default_state(input_data=text)
        r1 = sensory.process(state1)
        r2 = sensory.process(state2)
        assert r1["signal_report"]["features"]["entropy"] == r2["signal_report"]["features"]["entropy"]

    def test_coherence_single_sentence(self):
        sensory = SensorySystem()
        state = create_default_state(input_data="Just a single sentence")
        result = sensory.process(state)
        assert result["signal_report"]["features"]["coherence"] == 1.0

    def test_density_all_whitespace(self):
        sensory = SensorySystem()
        state = create_default_state(input_data="   \t\n  ")
        result = sensory.process(state)
        # All whitespace → no tokens → treated as empty → noise
        assert result["signal_report"]["features"]["density"] == 0.0

    def test_repair_check_valid(self):
        sensory = SensorySystem()
        state = create_default_state(input_data="test")
        result = sensory.process(state)
        assert sensory.repair_check(result) is True

    def test_repair_check_none_report(self):
        sensory = SensorySystem()
        state = create_default_state(input_data="test")
        state["signal_report"] = None
        assert sensory.repair_check(state) is False

    def test_input_hash_consistent(self):
        hash1 = _compute_input_hash("hello world")
        hash2 = _compute_input_hash("hello world")
        assert hash1 == hash2
        assert len(hash1) == 16

    def test_input_hash_different_inputs(self):
        hash1 = _compute_input_hash("hello")
        hash2 = _compute_input_hash("world")
        assert hash1 != hash2

    def test_process_dict_input(self):
        sensory = SensorySystem()
        state = create_default_state(input_data={"key": "value"})
        result = sensory.process(state)
        assert result["signal_report"] is not None

    def test_process_list_input(self):
        sensory = SensorySystem()
        state = create_default_state(input_data=[1, 2, 3])
        result = sensory.process(state)
        assert result["signal_report"] is not None

    def test_apoptotic_after_three_nones(self):
        sensory = SensorySystem()
        state = create_default_state(input_data=None)
        for _ in range(3):
            state = sensory.process(state)
        assert sensory.apoptotic_condition(state) is True

    def test_apoptotic_reset_on_valid_input(self):
        sensory = SensorySystem()
        state = create_default_state(input_data=None)
        sensory.process(state)
        sensory.process(state)
        # Non-None input resets counter.
        state2 = create_default_state(input_data="real input")
        sensory.process(state2)
        assert sensory.apoptotic_condition(state2) is False


# ============================================================
# Immune System Tests
# ============================================================


class TestImmuneSystem:
    """Comprehensive tests for the immune signal anomaly detection system."""

    def _make_report_state(self, **feature_overrides):
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

    def test_normal_signal_proceeds(self):
        immune = ImmuneSystem()
        state = self._make_report_state()
        result = immune.process(state)
        assert result["threat_assessment"]["threat_level"] == "none"
        assert result["threat_assessment"]["recommended_action"] == "proceed"

    def test_high_entropy_anomaly(self):
        immune = ImmuneSystem()
        state = self._make_report_state(entropy=7.5)
        result = immune.process(state)
        assert result["threat_assessment"]["is_anomalous"] is True
        assert "entropy" in result["threat_assessment"]["anomaly_scores"]

    def test_high_noise_anomaly(self):
        immune = ImmuneSystem()
        # noise_floor=0.9 → score = 0.9-0.35 = 0.55, above is_anomalous threshold of 0.5
        state = self._make_report_state(noise_floor=0.9)
        result = immune.process(state)
        assert result["threat_assessment"]["is_anomalous"] is True
        assert "noise_floor" in result["threat_assessment"]["anomaly_scores"]

    def test_high_impedance_anomaly(self):
        immune = ImmuneSystem()
        # impedance=1.0 → score = 1.0-0.5 = 0.5, and combined with any
        # rounding we use noise_floor=0.36 to push just over 0.5 total
        state = self._make_report_state(impedance=1.0)
        result = immune.process(state)
        assert result["threat_assessment"]["is_anomalous"] is True
        assert "impedance" in result["threat_assessment"]["anomaly_scores"]

    def test_critical_sets_apoptotic(self):
        immune = ImmuneSystem()
        # Create enough anomaly scores to reach "critical" (>= 5.0).
        state = self._make_report_state(entropy=12.0, noise_floor=0.9, impedance=1.0)
        state["signal_report"]["delta"]["aggregate_deviation"] = 10.0
        result = immune.process(state)
        assert result["threat_assessment"]["threat_level"] == "critical"
        assert result["flags"]["apoptotic"] is True

    def test_medium_sets_escalation(self):
        immune = ImmuneSystem()
        # Medium: total score >= 1.5 and < 3.0.
        state = self._make_report_state(entropy=8.0)  # entropy excess = 2.0
        result = immune.process(state)
        assert result["threat_assessment"]["threat_level"] in ("medium", "high")
        assert result["flags"]["escalate_to_conscious"] is True

    def test_new_anomalous_pattern_added_to_log(self):
        immune = ImmuneSystem()
        state = self._make_report_state(entropy=8.0)
        state["immune_log"] = []
        result = immune.process(state)
        assert len(result["immune_log"]) > 0

    def test_adaptive_matching_updates_encounter(self):
        import json
        immune = ImmuneSystem()
        # Create an initial threat log entry with a known feature vector.
        vector = [0.8, 3.5, 0.7, 0.1, 0.05, 0.1]
        state = self._make_report_state()
        state["immune_log"] = [{
            "pattern": json.dumps(vector),
            "encounter_count": 1,
            "confidence": 0.6,
            "last_seen": "2026-01-01T00:00:00",
        }]
        result = immune.process(state)
        # The entry should have been matched and encounter count incremented.
        matched_entry = result["immune_log"][0]
        assert matched_entry["encounter_count"] == 2

    def test_no_signal_report_default_proceed(self):
        immune = ImmuneSystem()
        state = create_default_state(input_data="test")
        state["signal_report"] = None
        result = immune.process(state)
        assert result["threat_assessment"]["threat_level"] == "none"
        assert result["threat_assessment"]["recommended_action"] == "proceed"

    def test_repair_check_valid(self):
        immune = ImmuneSystem()
        state = self._make_report_state()
        result = immune.process(state)
        assert immune.repair_check(result) is True

    def test_low_vocabulary_richness_anomaly(self):
        immune = ImmuneSystem()
        state = self._make_report_state(vocabulary_richness=0.05)
        result = immune.process(state)
        assert "vocabulary_richness" in result["threat_assessment"]["anomaly_scores"]


# ============================================================
# Subconscious System Tests
# ============================================================


class TestSubconsciousSystem:
    """Comprehensive tests for the subconscious signal pattern priming system."""

    def _make_signal_state(self, aggregate_deviation=0.5, threat_level="none"):
        """Create a state with signal report and threat assessment for testing."""
        state = create_default_state(input_data="test")
        state["flags"]["escalate_to_conscious"] = False  # Let subconscious decide
        state["signal_report"] = {
            "features": {
                "density": 0.8, "entropy": 3.5, "coherence": 0.7,
                "periodicity": 0.1, "noise_floor": 0.05, "impedance": 0.1,
                "token_count": 5, "vocabulary_richness": 0.8,
            },
            "classification": {"signal_type": "steady_state", "confidence": 0.9, "components": []},
            "delta": {
                "density_delta": 0.0, "entropy_delta": 0.0, "coherence_delta": 0.0,
                "periodicity_delta": 0.0, "noise_delta": 0.0, "impedance_delta": 0.0,
                "aggregate_deviation": aggregate_deviation, "activated_limbs": [],
            },
            "tick": 0, "input_hash": "subtest123",
        }
        state["threat_assessment"] = {
            "is_anomalous": threat_level != "none",
            "anomaly_scores": {},
            "matched_patterns": [],
            "threat_level": threat_level,
            "recommended_action": "proceed",
        }
        return state

    def test_no_cache_low_deviation_no_escalation(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state(aggregate_deviation=0.5)
        result = sub.process(state)
        assert result["subconscious_output"]["escalation_recommended"] is False

    def test_no_cache_high_deviation_escalates(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state(aggregate_deviation=2.0)
        result = sub.process(state)
        assert result["subconscious_output"]["escalation_recommended"] is True
        assert result["subconscious_output"]["escalation_confidence"] == 0.7

    def test_immune_medium_threat_escalates(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state(threat_level="medium")
        result = sub.process(state)
        assert result["subconscious_output"]["escalation_recommended"] is True
        assert result["subconscious_output"]["escalation_confidence"] == 0.9

    def test_cached_pattern_matching(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state()
        # Process once to add to cache.
        result1 = sub.process(state)
        assert len(result1["signal_pattern_cache"]) == 1
        # Process again with same signal — should match cache.
        result2 = sub.process(result1)
        assert len(result2["subconscious_output"]["matched_pattern_ids"]) > 0

    def test_preserves_upstream_escalation_flag(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state(aggregate_deviation=0.5)
        # Upstream (immune) set escalation flag.
        state["flags"]["escalate_to_conscious"] = True
        result = sub.process(state)
        # OR-preservation: upstream True survives even when subconscious doesn't escalate.
        assert result["flags"]["escalate_to_conscious"] is True

    def test_cache_grows_per_call(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state()
        result = sub.process(state)
        assert len(result["signal_pattern_cache"]) == 1

    def test_apoptotic_at_large_cache(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state()
        # Simulate large cache.
        state["signal_pattern_cache"] = [
            {
                "input_hash": f"hash_{i}",
                "feature_vector": [0.0] * 6,
                "signal_type": "steady_state",
                "outcome": "reflex_response",
                "response_pattern_id": None,
                "encounter_count": 1,
                "last_seen_tick": 0,
            }
            for i in range(10001)
        ]
        assert sub.apoptotic_condition(state) is True

    def test_apoptotic_below_threshold(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state()
        state["signal_pattern_cache"] = []
        assert sub.apoptotic_condition(state) is False

    def test_repair_check_valid(self):
        sub = SubconsciousSystem()
        state = self._make_signal_state()
        result = sub.process(state)
        assert sub.repair_check(result) is True

    def test_no_signal_report_default_output(self):
        sub = SubconsciousSystem()
        state = create_default_state(input_data="test")
        state["signal_report"] = None
        result = sub.process(state)
        assert result["subconscious_output"]["escalation_recommended"] is False
