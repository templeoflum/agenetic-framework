"""Tests for the conscious system — gate logic, deliberator protocol, integration.

Covers:
- E1: Gate tests (deterministic, no LLM) — 9 tests
- E2: ConsciousOutput structure tests — 3 tests
- E3: Deliberator protocol tests — 3 tests
- E4: Integration tests with MockDeliberator — 7 tests
- E6: Graph integration test — 1 test
- E7: Anthropic API test (optional, requires credentials) — 1 test
"""

import os

import pytest

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import build_graph, create_default_state
from agenetic.systems.conscious import ConsciousSystem
from agenetic.systems.deliberator import DeliberationRequest, Deliberator, MockDeliberator
from agenetic.systems.immune import ImmuneSystem
from agenetic.systems.motor import MotorSystem
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.subconscious import SubconsciousSystem
from agenetic.systems.sleep import SleepSystem
from agenetic.systems.genetic import GeneticSystem


# ============================================================
# Helpers
# ============================================================


def _make_field_with_overrides(overrides):
    """Create a field state with specific limb weight overrides.

    Args:
        overrides: dict mapping limb_id (int) -> weight (float).
    """
    field = OrientationalField()
    state = field.read()
    for limb in state["limbs"]:
        if limb["id"] in overrides:
            limb["weight"] = overrides[limb["id"]]
    return state


def _make_signal_report(
    signal_type="steady_state",
    aggregate_deviation=1.0,
    **feature_overrides,
):
    """Create a minimal signal report for gate testing."""
    features = {
        "density": 0.8, "entropy": 3.5, "coherence": 0.5,
        "periodicity": 0.1, "noise_floor": 0.05, "impedance": 0.1,
        "bigram_entropy": 3.0, "token_count": 10, "vocabulary_richness": 0.8,
    }
    features.update(feature_overrides)
    return {
        "features": features,
        "classification": {"signal_type": signal_type, "confidence": 0.9, "components": []},
        "delta": {
            "density_delta": -0.2, "entropy_delta": 0.5, "coherence_delta": -0.1,
            "periodicity_delta": 0.1, "noise_delta": 0.05, "impedance_delta": 0.1,
            "aggregate_deviation": aggregate_deviation, "activated_limbs": [],
        },
        "tick": 0, "input_hash": "test_hash_123",
    }


def _make_conscious_state(
    input_data="test input",
    field_overrides=None,
    signal_type="steady_state",
    aggregate_deviation=1.0,
    threat_action="proceed",
    threat_level="none",
):
    """Build a full state suitable for conscious system testing."""
    state = create_default_state(input_data=input_data)
    if field_overrides:
        state["field"] = _make_field_with_overrides(field_overrides)
    state["signal_report"] = _make_signal_report(
        signal_type=signal_type,
        aggregate_deviation=aggregate_deviation,
    )
    state["threat_assessment"] = {
        "is_anomalous": threat_action != "proceed",
        "anomaly_scores": {},
        "matched_patterns": [],
        "threat_level": threat_level,
        "recommended_action": threat_action,
    }
    state["subconscious_output"] = {
        "escalation_recommended": True,
        "escalation_confidence": 0.7,
        "matched_pattern_ids": [],
        "primed_associations": [],
    }
    return state


# ============================================================
# E1: Gate Tests (deterministic, no LLM)
# ============================================================


class TestGateLogic:
    """Tests for the proceed/suppress gate. All use deliberator=None."""

    def test_gate_immune_override_always_proceeds(self):
        """Immune escalation overrides all suppression conditions."""
        system = ConsciousSystem(deliberator=None)
        # Set conditions that would normally suppress (high Areka + noise).
        state = _make_conscious_state(
            field_overrides={8: 0.9},  # Areka high
            signal_type="noise",
            aggregate_deviation=0.2,
            threat_action="escalate",
            threat_level="high",
        )
        result = system.process(state)
        output = result["conscious_output"]
        # Gate should proceed because immune override takes priority.
        assert output["lineage"]["gate_evaluation"]["proceed"] is True
        assert output["lineage"]["gate_evaluation"]["reason"] == "immune_override"

    def test_gate_areka_suppresses_noise(self):
        """High Areka weight + noise classification = suppress."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={8: 0.8},  # Areka > 0.7
            signal_type="noise",
        )
        result = system.process(state)
        output = result["conscious_output"]
        assert output["proceed"] is False
        assert output["lineage"]["gate_evaluation"]["reason"] == "areka_suppression"

    def test_gate_areka_permits_non_noise(self):
        """High Areka weight + non-noise classification = proceed."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={8: 0.8},
            signal_type="steady_state",
        )
        result = system.process(state)
        output = result["conscious_output"]
        gate = output["lineage"]["gate_evaluation"]
        # Areka doesn't suppress non-noise — gate should proceed (or be
        # caught by another rule). With default Nivrtti at 0.5, default
        # resting stance at 0.5, and deviation at 1.0, gate proceeds.
        assert gate["reason"] != "areka_suppression"

    def test_gate_nivrtti_suppresses_low_deviation(self):
        """High Nivrtti weight + low aggregate deviation = suppress."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={3: 0.8},  # Nivrtti > 0.7
            aggregate_deviation=0.3,   # < 0.5
        )
        result = system.process(state)
        output = result["conscious_output"]
        assert output["proceed"] is False
        assert output["lineage"]["gate_evaluation"]["reason"] == "nivrtti_pause"

    def test_gate_nivrtti_permits_high_deviation(self):
        """High Nivrtti weight + high deviation = proceed."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={3: 0.8},  # Nivrtti > 0.7
            aggregate_deviation=1.0,   # > 0.5
        )
        result = system.process(state)
        output = result["conscious_output"]
        gate = output["lineage"]["gate_evaluation"]
        assert gate["reason"] != "nivrtti_pause"

    def test_gate_resting_stance_suppresses(self):
        """All convergent cluster limbs high + very low deviation = suppress."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={12: 0.9, 14: 0.9, 15: 0.9, 17: 0.9, 18: 0.9},
            aggregate_deviation=0.2,  # < 0.3
        )
        result = system.process(state)
        output = result["conscious_output"]
        assert output["proceed"] is False
        assert output["lineage"]["gate_evaluation"]["reason"] == "resting_stance_suppression"

    def test_gate_resting_stance_permits_deviation(self):
        """All convergent cluster limbs high + high deviation = proceed."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={12: 0.9, 14: 0.9, 15: 0.9, 17: 0.9, 18: 0.9},
            aggregate_deviation=1.0,  # > 0.3
        )
        result = system.process(state)
        output = result["conscious_output"]
        gate = output["lineage"]["gate_evaluation"]
        assert gate["reason"] != "resting_stance_suppression"

    def test_gate_default_proceeds(self):
        """All weights at 0.5, normal signal report = proceed."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state()  # All defaults (0.5 weights)
        result = system.process(state)
        output = result["conscious_output"]
        gate = output["lineage"]["gate_evaluation"]
        assert gate["proceed"] is True
        assert gate["reason"] == "default_proceed"

    def test_gate_priority_order(self):
        """Immune override beats Areka suppression."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={8: 0.9},  # Areka would suppress noise
            signal_type="noise",
            threat_action="escalate",  # But immune override wins
            threat_level="critical",
        )
        result = system.process(state)
        output = result["conscious_output"]
        gate = output["lineage"]["gate_evaluation"]
        assert gate["proceed"] is True
        assert gate["reason"] == "immune_override"


# ============================================================
# E2: ConsciousOutput Structure Tests
# ============================================================


class TestConsciousOutputStructure:
    """Verify ConsciousOutput completeness for proceed and suppress paths."""

    def test_suppression_output_complete(self):
        """Gate suppression produces complete ConsciousOutput."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state(
            field_overrides={8: 0.8},
            signal_type="noise",
        )
        result = system.process(state)
        output = result["conscious_output"]

        # All top-level fields present.
        assert "decision" in output
        assert "expression" in output
        assert "lineage" in output
        assert "proceed" in output
        assert "confidence" in output

        # Proceed is False.
        assert output["proceed"] is False
        assert output["confidence"] == 1.0

        # Decision fields.
        assert output["decision"]["intent"] == "suppress"
        assert output["decision"]["strategy"] == "sacred_pause"

        # Lineage has gate_evaluation.
        assert "gate_evaluation" in output["lineage"]
        assert output["lineage"]["gate_evaluation"]["reason"] == "areka_suppression"
        assert output["lineage"]["deliberation_model"] == "none"

    def test_lineage_always_present(self):
        """Both proceed and suppress paths have complete lineage."""
        required_lineage_keys = [
            "escalation_reason", "signal_summary", "field_snapshot",
            "gate_evaluation", "deliberation_model",
        ]

        # Suppress path.
        system_suppress = ConsciousSystem(deliberator=None)
        state_suppress = _make_conscious_state(
            field_overrides={3: 0.8},
            aggregate_deviation=0.3,
        )
        result_suppress = system_suppress.process(state_suppress)
        lineage_suppress = result_suppress["conscious_output"]["lineage"]
        for key in required_lineage_keys:
            assert key in lineage_suppress, f"Suppress path missing lineage key: {key}"

        # Proceed path (with mock deliberator).
        mock = MockDeliberator()
        system_proceed = ConsciousSystem(deliberator=mock)
        state_proceed = _make_conscious_state()
        result_proceed = system_proceed.process(state_proceed)
        lineage_proceed = result_proceed["conscious_output"]["lineage"]
        for key in required_lineage_keys:
            assert key in lineage_proceed, f"Proceed path missing lineage key: {key}"

    def test_no_deliberator_degrades(self):
        """ConsciousSystem with no deliberator + proceed gate = degraded output."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state()
        result = system.process(state)

        output = result["conscious_output"]
        assert output["proceed"] is True
        assert output["confidence"] == 0.0
        assert output["decision"]["strategy"] == "no_deliberator"
        assert "conscious" in result["flags"]["degraded"]


# ============================================================
# E3: Deliberator Protocol Tests
# ============================================================


class TestDeliberatorProtocol:
    """Verify the Deliberator protocol and MockDeliberator."""

    def test_mock_deliberator_satisfies_protocol(self):
        """MockDeliberator is an instance of Deliberator (runtime_checkable)."""
        mock = MockDeliberator()
        assert isinstance(mock, Deliberator)

    def test_mock_deliberator_returns_valid_output(self):
        """MockDeliberator.deliberate() returns all ConsciousOutput fields."""
        mock = MockDeliberator()
        request = DeliberationRequest(
            input_text="test",
            signal_summary={"classification": "steady_state", "aggregate_deviation": 0.5},
            threat_summary={"threat_level": "none", "recommended_action": "proceed"},
            subconscious_summary={"escalation_reason": "novel_input"},
            field_state={"Prakasa": 0.5, "Tarka": 0.5},
            active_limbs=[],
            resting_stance=0.5,
            expression_directives={"state_awareness": "active"},
        )
        output = mock.deliberate(request)

        assert "decision" in output
        assert "expression" in output
        assert "lineage" in output
        assert "proceed" in output
        assert "confidence" in output
        assert output["proceed"] is True
        assert output["lineage"]["deliberation_model"] == "mock"

    def test_deliberator_call_count(self):
        """MockDeliberator tracks call count correctly."""
        mock = MockDeliberator()
        request = DeliberationRequest(
            input_text="test",
            signal_summary={},
            threat_summary={},
            subconscious_summary={},
            field_state={},
            active_limbs=[],
            resting_stance=0.5,
            expression_directives={},
        )
        assert mock.call_count == 0
        mock.deliberate(request)
        assert mock.call_count == 1
        mock.deliberate(request)
        assert mock.call_count == 2
        assert mock.last_request is request


# ============================================================
# E4: Integration Tests (with MockDeliberator)
# ============================================================


class TestConsciousIntegration:
    """Integration tests using MockDeliberator for deterministic behavior."""

    def test_conscious_full_proceed_path(self):
        """Normal escalated state → gate proceeds → deliberator called → output."""
        mock = MockDeliberator()
        system = ConsciousSystem(deliberator=mock)
        state = _make_conscious_state()
        result = system.process(state)

        assert mock.call_count == 1
        output = result["conscious_output"]
        assert output["proceed"] is True
        assert output["confidence"] == 0.8  # MockDeliberator default
        assert output["lineage"]["deliberation_model"] == "mock"
        assert output["lineage"]["gate_evaluation"]["proceed"] is True

    def test_conscious_full_suppress_path(self):
        """Areka + noise → gate suppresses → deliberator NOT called."""
        mock = MockDeliberator()
        system = ConsciousSystem(deliberator=mock)
        state = _make_conscious_state(
            field_overrides={8: 0.9},
            signal_type="noise",
        )
        result = system.process(state)

        assert mock.call_count == 0  # Deliberator never called
        output = result["conscious_output"]
        assert output["proceed"] is False
        assert output["decision"]["intent"] == "suppress"

    def test_conscious_missing_signal_report(self):
        """No signal report → degradation flag, no ConsciousOutput."""
        system = ConsciousSystem(deliberator=MockDeliberator())
        state = create_default_state(input_data="test")
        state["signal_report"] = None
        result = system.process(state)

        assert "conscious" in result["flags"]["degraded"]
        assert result.get("conscious_output") is None

    def test_conscious_repair_check_passes(self):
        """Normal ConsciousOutput passes repair check."""
        mock = MockDeliberator()
        system = ConsciousSystem(deliberator=mock)
        state = _make_conscious_state()
        result = system.process(state)

        assert system.repair_check(result) is True

    def test_conscious_repair_check_fails_low_confidence(self):
        """proceed=True with confidence < 0.1 fails repair check."""
        system = ConsciousSystem(deliberator=None)
        state = _make_conscious_state()
        result = system.process(state)
        # No deliberator → degraded output: proceed=True, confidence=0.0
        output = result["conscious_output"]
        assert output["proceed"] is True
        assert output["confidence"] < 0.1
        assert system.repair_check(result) is False

    def test_conscious_repair_check_fails_missing_lineage(self):
        """ConsciousOutput with incomplete lineage fails repair check."""
        system = ConsciousSystem(deliberator=MockDeliberator())
        state = _make_conscious_state()
        result = system.process(state)
        # Remove a required lineage key.
        del result["conscious_output"]["lineage"]["escalation_reason"]
        assert system.repair_check(result) is False

    def test_conscious_apoptotic_after_streak(self):
        """3 consecutive low-confidence deliberations → apoptotic."""
        # Create a mock that always returns low confidence.
        class LowConfidenceMock:
            def deliberate(self, request):
                return {
                    "decision": {"intent": "low", "strategy": "test", "constraints": []},
                    "expression": {
                        "field_weights": {}, "active_limbs": [],
                        "resting_stance": 0.5, "suppress_identity": False,
                        "state_awareness": "active",
                    },
                    "lineage": {
                        "escalation_reason": "test", "signal_summary": {},
                        "field_snapshot": {}, "gate_evaluation": {},
                        "deliberation_model": "low_confidence_mock",
                    },
                    "proceed": True,
                    "confidence": 0.1,  # Below 0.2 threshold
                }

        system = ConsciousSystem(deliberator=LowConfidenceMock())
        state = _make_conscious_state()

        # Run 3 cycles, carrying forward metadata.
        for i in range(3):
            result = system.process(state)
            state = result  # Carry forward (especially metadata)

        assert result["metadata"]["conscious_low_confidence_streak"] == 3
        assert system.apoptotic_condition(result) is True

    def test_conscious_apoptotic_resets_on_high_confidence(self):
        """High-confidence result resets the low-confidence streak."""
        mock = MockDeliberator()  # Returns confidence=0.8
        system = ConsciousSystem(deliberator=mock)
        state = _make_conscious_state()

        # Manually set a streak.
        state["metadata"]["conscious_low_confidence_streak"] = 2
        result = system.process(state)

        # MockDeliberator returns confidence=0.8, which resets streak.
        assert result["metadata"]["conscious_low_confidence_streak"] == 0
        assert system.apoptotic_condition(result) is False


# ============================================================
# E6: Graph Integration Test
# ============================================================


class TestConsciousGraphIntegration:
    """Verify conscious output flows through the graph to motor."""

    def test_graph_conscious_output_flows_to_motor(self):
        """Full graph with MockDeliberator produces conscious_output in state."""
        graph = build_graph(
            sensory=SensorySystem(),
            immune=ImmuneSystem(),
            subconscious=SubconsciousSystem(),
            conscious=ConsciousSystem(deliberator=MockDeliberator()),
            motor=MotorSystem(),
            sleep=SleepSystem(),
            genetic=GeneticSystem(),
        )
        state = create_default_state(input_data="The quick brown fox jumps over the lazy dog.")
        result = graph.invoke(state)

        # Conscious should have fired (default escalate_to_conscious=True).
        assert "conscious" in result["metadata"]["routing_history"]

        # conscious_output should be present.
        assert result["conscious_output"] is not None
        assert result["conscious_output"]["proceed"] is True
        assert result["conscious_output"]["lineage"]["deliberation_model"] == "mock"

        # Motor should also have fired after conscious.
        assert "motor" in result["metadata"]["routing_history"]
        assert result["motor_output"] is not None


# ============================================================
# E7: Anthropic API Test (optional — requires credentials)
# ============================================================


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="No ANTHROPIC_API_KEY — skipping live API test",
)
class TestAnthropicDeliberator:
    """Live API test. Only runs when ANTHROPIC_API_KEY is set."""

    def test_anthropic_deliberator_real_call(self):
        from agenetic.systems.deliberator_anthropic import AnthropicDeliberator

        deliberator = AnthropicDeliberator()
        request = DeliberationRequest(
            input_text="What is the nature of consciousness?",
            signal_summary={
                "classification": "steady_state",
                "aggregate_deviation": 0.8,
                "features": {"density": 0.85, "entropy": 4.0, "coherence": 0.6},
            },
            threat_summary={"threat_level": "none", "recommended_action": "proceed"},
            subconscious_summary={"escalation_reason": "novel_input"},
            field_state={"Tarka": 0.7, "Sraddha": 0.6},
            active_limbs=[
                {"id": 2, "name": "Tarka", "weight": 0.7},
                {"id": 5, "name": "Sraddha", "weight": 0.6},
            ],
            resting_stance=0.5,
            expression_directives={
                "state_awareness": "active",
                "suppress_identity": False,
            },
        )
        output = deliberator.deliberate(request)

        # Verify structure.
        assert "decision" in output
        assert "expression" in output
        assert "lineage" in output
        assert "proceed" in output
        assert "confidence" in output
        assert output["proceed"] is True
        assert "anthropic:" in output["lineage"]["deliberation_model"]
