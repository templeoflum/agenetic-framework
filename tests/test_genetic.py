"""Tests for the genetic system — expression profile store and drift measurement.

Covers:
- Factory defaults (3 tests)
- Expression profile access (3 tests)
- Drift measurement (4 tests)
- Repair check (3 tests)
- Apoptotic condition (3 tests)
- Seed integrity in output (2 tests)

All tests are deterministic — no LLM calls, no API keys.
"""

import pytest

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import create_default_state
from agenetic.systems.genetic import GeneticSystem
from agenetic.systems.sleep import SleepSystem


def _make_state(field=None):
    """Create a state suitable for genetic processing."""
    if field is None:
        field = OrientationalField()
    return create_default_state(input_data="test", field=field)


def _make_field_with_weights(weight_overrides: dict[int, float]) -> OrientationalField:
    """Create a field with specific limb weights overridden."""
    field = OrientationalField()
    limbs = field.read()["limbs"]
    for limb in limbs:
        if limb["id"] in weight_overrides:
            limb["weight"] = weight_overrides[limb["id"]]
    field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
    return field


# ============================================================
# Factory defaults (3 tests)
# ============================================================


class TestFactoryDefaults:

    def test_factory_seed_has_18_limbs(self):
        """FACTORY_SEED has exactly 18 entries."""
        assert len(GeneticSystem.FACTORY_SEED) == 18

    def test_factory_profile_all_active(self):
        """All 7 systems are 'active' at generation 0."""
        genetic = GeneticSystem()
        profile = genetic.get_expression_profile()
        for entry in profile["system_expressions"]:
            assert entry["state"] == "active"
        assert len(profile["system_expressions"]) == 7

    def test_factory_profile_generation_zero(self):
        """Generation is 0 at factory defaults."""
        genetic = GeneticSystem()
        profile = genetic.get_expression_profile()
        assert profile["generation"] == 0


# ============================================================
# Expression profile access (3 tests)
# ============================================================


class TestExpressionProfileAccess:

    def test_get_expression_profile_returns_profile(self):
        """get_expression_profile() returns an ExpressionProfile with required keys."""
        genetic = GeneticSystem()
        profile = genetic.get_expression_profile()
        assert "default_weights" in profile
        assert "system_expressions" in profile
        assert "generation" in profile

    def test_custom_seed_overrides_defaults(self):
        """GeneticSystem(seed={...}) uses custom weights."""
        custom_seed = dict(GeneticSystem.FACTORY_SEED)
        custom_seed["Prakasa"] = 0.7
        custom_seed["Tarka"] = 0.3
        genetic = GeneticSystem(seed=custom_seed)
        profile = genetic.get_expression_profile()
        assert profile["default_weights"]["Prakasa"] == 0.7
        assert profile["default_weights"]["Tarka"] == 0.3

    def test_process_populates_genetic_output(self):
        """process() adds genetic_output to state."""
        genetic = GeneticSystem()
        state = _make_state()
        result = genetic.process(state)
        assert result["genetic_output"] is not None
        assert "expression_profile" in result["genetic_output"]
        assert "drift_from_seed" in result["genetic_output"]
        assert "seed_integrity" in result["genetic_output"]


# ============================================================
# Drift measurement (4 tests)
# ============================================================


class TestDriftMeasurement:

    def test_drift_zero_at_factory_defaults(self):
        """All weights at 0.5 → drift = 0.0."""
        genetic = GeneticSystem()
        state = _make_state()
        drift = genetic.compute_drift(state["field"])
        assert drift == pytest.approx(0.0)

    def test_drift_computes_absolute_distance(self):
        """One limb at 0.7 → drift = 0.2."""
        genetic = GeneticSystem()
        field = _make_field_with_weights({1: 0.7})  # Prakasa at 0.7
        state = _make_state(field=field)
        drift = genetic.compute_drift(state["field"])
        assert drift == pytest.approx(0.2)

    def test_drift_accumulates_across_limbs(self):
        """Multiple limbs moved → drift = sum of absolute deltas."""
        genetic = GeneticSystem()
        # Limb 1 at 0.7 (delta 0.2), limb 2 at 0.3 (delta 0.2), limb 3 at 0.9 (delta 0.4)
        field = _make_field_with_weights({1: 0.7, 2: 0.3, 3: 0.9})
        state = _make_state(field=field)
        drift = genetic.compute_drift(state["field"])
        assert drift == pytest.approx(0.8)

    def test_drift_maximum_is_nine(self):
        """All limbs at 0.0 → drift = 9.0 (18 × 0.5)."""
        genetic = GeneticSystem()
        field = OrientationalField()
        limbs = field.read()["limbs"]
        for limb in limbs:
            limb["weight"] = 0.0
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        state = _make_state(field=field)
        drift = genetic.compute_drift(state["field"])
        assert drift == pytest.approx(9.0)


# ============================================================
# Repair check (3 tests)
# ============================================================


class TestRepairCheck:

    def test_repair_passes_at_factory(self):
        """Factory defaults pass repair check."""
        genetic = GeneticSystem()
        state = _make_state()
        assert genetic.repair_check(state) is True

    def test_repair_fails_with_corrupted_seed(self):
        """Manually corrupt the profile (remove a limb) → False."""
        genetic = GeneticSystem()
        # Remove a limb from default_weights.
        del genetic._expression_profile["default_weights"]["Prakasa"]
        state = _make_state()
        assert genetic.repair_check(state) is False

    def test_repair_fails_with_missing_system(self):
        """Remove a system expression → False."""
        genetic = GeneticSystem()
        # Remove last system expression.
        genetic._expression_profile["system_expressions"].pop()
        state = _make_state()
        assert genetic.repair_check(state) is False


# ============================================================
# Apoptotic condition (3 tests)
# ============================================================


class TestApoptoticCondition:

    def test_not_apoptotic_at_factory(self):
        """Factory defaults → False."""
        genetic = GeneticSystem()
        state = _make_state()
        assert genetic.apoptotic_condition(state) is False

    def test_apoptotic_at_high_drift(self):
        """All field weights at 0.0 (drift = 9.0) → True."""
        genetic = GeneticSystem()
        field = OrientationalField()
        limbs = field.read()["limbs"]
        for limb in limbs:
            limb["weight"] = 0.0
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        state = _make_state(field=field)
        assert genetic.apoptotic_condition(state) is True

    def test_apoptotic_threshold_boundary(self):
        """Drift exactly at 3.0 → True, just below → False."""
        genetic = GeneticSystem()

        # Drift exactly 3.0: 6 limbs at 1.0 (each contributes 0.5), rest at 0.5.
        field_at = OrientationalField()
        limbs = field_at.read()["limbs"]
        for i in range(6):
            limbs[i]["weight"] = 1.0
        field_at.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        state_at = _make_state(field=field_at)
        assert genetic.compute_drift(state_at["field"]) == pytest.approx(3.0)
        assert genetic.apoptotic_condition(state_at) is True

        # Drift just below 3.0: 5 limbs at 1.0 (drift=2.5).
        field_below = OrientationalField()
        limbs = field_below.read()["limbs"]
        for i in range(5):
            limbs[i]["weight"] = 1.0
        field_below.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        state_below = _make_state(field=field_below)
        assert genetic.compute_drift(state_below["field"]) == pytest.approx(2.5)
        assert genetic.apoptotic_condition(state_below) is False


# ============================================================
# Seed integrity in output (2 tests)
# ============================================================


class TestSeedIntegrity:

    def test_seed_integrity_true_at_factory(self):
        """genetic_output.seed_integrity is True at defaults."""
        genetic = GeneticSystem()
        state = _make_state()
        result = genetic.process(state)
        assert result["genetic_output"]["seed_integrity"] is True

    def test_seed_integrity_false_at_high_drift(self):
        """seed_integrity is False when drift exceeds threshold."""
        genetic = GeneticSystem()
        field = OrientationalField()
        limbs = field.read()["limbs"]
        for limb in limbs:
            limb["weight"] = 0.0
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        state = _make_state(field=field)
        result = genetic.process(state)
        assert result["genetic_output"]["seed_integrity"] is False
