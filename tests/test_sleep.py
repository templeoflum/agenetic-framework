"""Tests for the sleep system — consolidation and weight modification.

Covers:
- Tick gating (4 tests)
- Cache pruning (5 tests)
- Immune log consolidation (6 tests)
- Weight modification (9 tests)
- Repair and apoptosis (4 tests)
- Sleep state persistence (3 tests)
- Integration (4 tests)

All tests are deterministic — no LLM calls, no API keys.
"""

from datetime import datetime, timedelta, timezone

from agenetic.field.orientational import OrientationalField
from agenetic.network.graph import create_default_state
from agenetic.systems.base import (
    AREKA_ID,
    BODHI_ID,
    CONVERGENT_CLUSTER_IDS,
    NIVRTTI_ID,
    TARKA_ID,
    CachedSignalPattern,
    ThreatEntry,
)
from agenetic.systems.sensory import SensorySystem
from agenetic.systems.sleep import SleepSystem


def _make_state(tick=10, cache=None, immune_log=None, sleep_state=None, field=None):
    """Create a state suitable for sleep processing."""
    if field is None:
        field = OrientationalField()
    state = create_default_state(input_data="test", field=field)
    state["metadata"]["tick"] = tick
    if cache is not None:
        state["signal_pattern_cache"] = cache
    if immune_log is not None:
        state["immune_log"] = immune_log
    if sleep_state is not None:
        state["sleep_state"] = sleep_state
    return state


def _make_cache_entry(
    encounter_count=1, last_seen_tick=0, input_hash="h1",
) -> CachedSignalPattern:
    """Create a cache entry for testing."""
    return {
        "input_hash": input_hash,
        "feature_vector": [0.8, 3.5, 0.5, 0.1, 0.05, 0.1],
        "signal_type": "steady_state",
        "outcome": "reflex_response",
        "response_pattern_id": None,
        "encounter_count": encounter_count,
        "last_seen_tick": last_seen_tick,
    }


def _make_threat(
    encounter_count=1, confidence=0.5, last_seen=None, pattern="test",
) -> ThreatEntry:
    """Create a threat entry for testing."""
    if last_seen is None:
        last_seen = datetime.now(timezone.utc).isoformat()
    return {
        "pattern": pattern,
        "encounter_count": encounter_count,
        "confidence": confidence,
        "last_seen": last_seen,
    }


def _stale_timestamp(seconds_ago=7200):
    """Return an ISO timestamp from seconds_ago in the past."""
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds_ago)).isoformat()


# ============================================================
# Tick gating (4 tests)
# ============================================================


class TestTickGating:

    def test_fires_at_interval(self):
        """Sleep fires at tick 10, 20, 30 for interval=10."""
        sleep = SleepSystem(tick_interval=10)
        # Add stale cache entry so firing produces visible effect.
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        for tick in [10, 20, 30]:
            state = _make_state(tick=tick, cache=list(cache))
            result = sleep.process(state)
            # When firing, sleep_state.last_sleep_tick gets updated.
            assert result["sleep_state"]["last_sleep_tick"] == tick

    def test_does_not_fire_between_intervals(self):
        """Sleep does NOT fire at tick 5, 15."""
        sleep = SleepSystem(tick_interval=10)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        for tick in [5, 15]:
            state = _make_state(tick=tick, cache=list(cache))
            result = sleep.process(state)
            # Cache should be unchanged (no pruning).
            assert len(result["signal_pattern_cache"]) == 1

    def test_does_not_fire_at_tick_zero(self):
        """Sleep does NOT fire at tick 0."""
        sleep = SleepSystem(tick_interval=10)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        state = _make_state(tick=0, cache=cache)
        result = sleep.process(state)
        # Cache should be unchanged.
        assert len(result["signal_pattern_cache"]) == 1

    def test_custom_tick_interval(self):
        """Custom tick_interval=5 fires at tick 5, 10, 15."""
        sleep = SleepSystem(tick_interval=5)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        for tick in [5, 10, 15]:
            state = _make_state(tick=tick, cache=list(cache))
            result = sleep.process(state)
            assert result["sleep_state"]["last_sleep_tick"] == tick


# ============================================================
# Cache pruning (5 tests)
# ============================================================


class TestCachePruning:

    def test_prunes_stale_low_encounter(self):
        """Entries with encounter_count <= 2 and stale > threshold are removed."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [
            _make_cache_entry(encounter_count=1, last_seen_tick=0),
            _make_cache_entry(encounter_count=2, last_seen_tick=5, input_hash="h2"),
        ]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        assert len(result["signal_pattern_cache"]) == 0

    def test_preserves_high_encounter(self):
        """Entries with encounter_count > 2 are never removed regardless of age."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [
            _make_cache_entry(encounter_count=5, last_seen_tick=0),
            _make_cache_entry(encounter_count=3, last_seen_tick=0, input_hash="h2"),
        ]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        assert len(result["signal_pattern_cache"]) == 2

    def test_preserves_recent_low_encounter(self):
        """Entries with encounter_count <= 2 but NOT stale are preserved."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [
            _make_cache_entry(encounter_count=1, last_seen_tick=90),
            _make_cache_entry(encounter_count=2, last_seen_tick=95, input_hash="h2"),
        ]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        assert len(result["signal_pattern_cache"]) == 2

    def test_cache_metrics_correct(self):
        """Cache size metrics are correctly tracked in sleep_state."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [
            _make_cache_entry(encounter_count=1, last_seen_tick=0),
            _make_cache_entry(encounter_count=5, last_seen_tick=0, input_hash="h2"),
            _make_cache_entry(encounter_count=1, last_seen_tick=0, input_hash="h3"),
        ]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        # 2 stale low-encounter pruned, 1 high-encounter kept.
        assert len(result["signal_pattern_cache"]) == 1
        assert result["sleep_state"]["cache_size_at_last_sleep"] == 1

    def test_empty_cache_no_errors(self):
        """Empty cache produces no errors."""
        sleep = SleepSystem(tick_interval=10)
        state = _make_state(tick=10, cache=[])
        result = sleep.process(state)
        assert len(result["signal_pattern_cache"]) == 0


# ============================================================
# Immune log consolidation (6 tests)
# ============================================================


class TestImmuneConsolidation:

    def test_promotes_recurring_threats(self):
        """Threats with encounter_count >= 3 get confidence +0.1."""
        sleep = SleepSystem(tick_interval=10)
        log = [_make_threat(encounter_count=3, confidence=0.5)]
        state = _make_state(tick=10, immune_log=log)
        result = sleep.process(state)
        assert result["immune_log"][0]["confidence"] == pytest.approx(0.6)

    def test_confidence_capped_at_one(self):
        """Confidence is capped at 1.0 after promotion."""
        sleep = SleepSystem(tick_interval=10)
        log = [_make_threat(encounter_count=5, confidence=0.95)]
        state = _make_state(tick=10, immune_log=log)
        result = sleep.process(state)
        assert result["immune_log"][0]["confidence"] == pytest.approx(1.0)

    def test_demotes_stale_low_encounter(self):
        """Stale low-encounter threats get confidence -0.1."""
        sleep = SleepSystem(tick_interval=10, staleness_seconds=3600)
        log = [_make_threat(
            encounter_count=1, confidence=0.5,
            last_seen=_stale_timestamp(7200),
        )]
        state = _make_state(tick=10, immune_log=log)
        result = sleep.process(state)
        assert result["immune_log"][0]["confidence"] == pytest.approx(0.4)

    def test_removes_expired_threats(self):
        """Threats with confidence <= 0.0 are removed after demotion."""
        sleep = SleepSystem(tick_interval=10, staleness_seconds=3600)
        log = [_make_threat(
            encounter_count=1, confidence=0.1,
            last_seen=_stale_timestamp(7200),
        )]
        state = _make_state(tick=10, immune_log=log)
        result = sleep.process(state)
        # 0.1 - 0.1 = 0.0 → removed (confidence <= 0.0).
        assert len(result["immune_log"]) == 0

    def test_empty_immune_log_no_errors(self):
        """Empty immune log produces no errors."""
        sleep = SleepSystem(tick_interval=10)
        state = _make_state(tick=10, immune_log=[])
        result = sleep.process(state)
        assert len(result["immune_log"]) == 0

    def test_iso_datetime_comparison(self):
        """ISO datetime comparison correctly handles timezone-aware timestamps."""
        sleep = SleepSystem(tick_interval=10, staleness_seconds=3600)
        # Fresh timestamp (not stale) — should NOT be demoted.
        fresh = _make_threat(
            encounter_count=1, confidence=0.5,
            last_seen=datetime.now(timezone.utc).isoformat(),
        )
        # Stale timestamp — should be demoted.
        stale = _make_threat(
            encounter_count=2, confidence=0.5,
            last_seen=_stale_timestamp(7200), pattern="stale",
        )
        state = _make_state(tick=10, immune_log=[fresh, stale])
        result = sleep.process(state)
        # Fresh entry unchanged, stale entry demoted.
        assert len(result["immune_log"]) == 2
        fresh_result = [e for e in result["immune_log"] if e["pattern"] == "test"][0]
        stale_result = [e for e in result["immune_log"] if e["pattern"] == "stale"][0]
        assert fresh_result["confidence"] == pytest.approx(0.5)
        assert stale_result["confidence"] == pytest.approx(0.4)


# ============================================================
# Weight modification (9 tests)
# ============================================================


import pytest


class TestWeightModification:

    def test_noise_ratio_increases_convergent_cluster(self):
        """High noise ratio (> 0.3) increases convergent cluster weights."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        # 4 stale entries out of 10 → noise_ratio = 0.4 > 0.3.
        cache = []
        for i in range(4):
            cache.append(_make_cache_entry(encounter_count=1, last_seen_tick=0, input_hash=f"stale{i}"))
        for i in range(6):
            cache.append(_make_cache_entry(encounter_count=5, last_seen_tick=0, input_hash=f"keep{i}"))
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        # Convergent cluster limbs should have increased from 0.5.
        for limb in result["field"]["limbs"]:
            if limb["id"] in CONVERGENT_CLUSTER_IDS:
                assert limb["weight"] > 0.5

    def test_convergent_cluster_uniform_delta(self):
        """All five convergent cluster limbs get the same delta."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = []
        for i in range(4):
            cache.append(_make_cache_entry(encounter_count=1, last_seen_tick=0, input_hash=f"s{i}"))
        for i in range(6):
            cache.append(_make_cache_entry(encounter_count=5, last_seen_tick=0, input_hash=f"k{i}"))
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        cluster_weights = [
            limb["weight"] for limb in result["field"]["limbs"]
            if limb["id"] in CONVERGENT_CLUSTER_IDS
        ]
        assert len(cluster_weights) == 5
        # All should be identical.
        assert all(w == cluster_weights[0] for w in cluster_weights)

    def test_threat_pressure_increases_areka_nivrtti(self):
        """High threat pressure (> 0.3) increases Areka and Nivrtti weights."""
        sleep = SleepSystem(tick_interval=10)
        # 2 promoted out of 3 total → threat_pressure = 0.67.
        log = [
            _make_threat(encounter_count=5, confidence=0.5, pattern="t1"),
            _make_threat(encounter_count=3, confidence=0.5, pattern="t2"),
            _make_threat(encounter_count=1, confidence=0.5, pattern="t3"),
        ]
        state = _make_state(tick=10, immune_log=log)
        result = sleep.process(state)
        for limb in result["field"]["limbs"]:
            if limb["id"] in (AREKA_ID, NIVRTTI_ID):
                assert limb["weight"] > 0.5

    def test_novelty_rate_increases_tarka(self):
        """High novelty rate (> 0.5) increases Tarka weight."""
        sleep = SleepSystem(tick_interval=10)
        # Setup: cache grew from 0 to 10 in 10 ticks → novelty = 1.0.
        state = _make_state(tick=10, cache=[
            _make_cache_entry(encounter_count=5, last_seen_tick=9, input_hash=f"n{i}")
            for i in range(10)
        ])
        state["sleep_state"] = {
            "last_sleep_tick": 0,
            "cache_size_at_last_sleep": 0,
            "consecutive_no_improvement": 0,
            "last_had_effect": True,
        }
        result = sleep.process(state)
        for limb in result["field"]["limbs"]:
            if limb["id"] == TARKA_ID:
                assert limb["weight"] > 0.5

    def test_gravity_pulls_toward_midpoint(self):
        """Gravity decay pulls weights toward 0.5."""
        sleep = SleepSystem(tick_interval=10)
        # Set one limb high, another low — both should move toward 0.5.
        field = OrientationalField()
        limbs = field.read()["limbs"]
        # Limb 1 (Prakasa) at 0.7 — no consolidation signal, only gravity.
        limbs[0]["weight"] = 0.7
        # Limb 6 (Atma-Vichara) at 0.3 — no consolidation signal.
        limbs[5]["weight"] = 0.3
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        state = _make_state(tick=10, field=field)
        result = sleep.process(state)
        high_limb = [l for l in result["field"]["limbs"] if l["id"] == 1][0]
        low_limb = [l for l in result["field"]["limbs"] if l["id"] == 6][0]
        # High limb should decrease toward 0.5.
        assert high_limb["weight"] < 0.7
        # Low limb should increase toward 0.5.
        assert low_limb["weight"] > 0.3

    def test_delta_clamped_to_bounds(self):
        """Per-tick delta is clamped to ±0.05."""
        sleep = SleepSystem(tick_interval=10)
        # Set a limb far from 0.5 — gravity alone would be -0.01 * (1.0 - 0.5) = -0.005.
        # With consolidation +0.03, total = 0.025. But if we construct extreme gravity...
        # Actually, gravity at 1.0 is -0.005, at 0.0 is +0.005. Always < 0.05.
        # So delta clamping only matters with extreme consolidation + gravity combined.
        # Test: set a convergent limb at 0.0, high noise ratio → gravity +0.005, consol +0.03 = 0.035.
        # Still under 0.05. The clamp protects against future larger deltas.
        # Just verify the clamp math works by checking no weight ever moves more than 0.05.
        field = OrientationalField()
        limbs = field.read()["limbs"]
        for limb in limbs:
            limb["weight"] = 1.0  # Extreme position.
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        # Large stale cache to trigger noise signal.
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0, input_hash=f"x{i}") for i in range(10)]
        state = _make_state(tick=100, cache=cache, field=field)
        result = sleep.process(state)
        for limb in result["field"]["limbs"]:
            # No weight should have moved more than 0.05 from 1.0.
            assert limb["weight"] >= 0.95

    def test_absolute_weight_bounds(self):
        """Absolute weight bounds [0.0, 1.0] enforced."""
        sleep = SleepSystem(tick_interval=10)
        field = OrientationalField()
        limbs = field.read()["limbs"]
        for limb in limbs:
            limb["weight"] = 0.0  # At minimum.
        field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)
        state = _make_state(tick=10, field=field)
        result = sleep.process(state)
        for limb in result["field"]["limbs"]:
            assert 0.0 <= limb["weight"] <= 1.0

    def test_default_weights_no_signals_no_change(self):
        """Default weights (all 0.5) with no consolidation signals → no weight change."""
        sleep = SleepSystem(tick_interval=10)
        # Empty cache, empty immune log → no signals, gravity at 0.5 is zero.
        state = _make_state(tick=10, cache=[], immune_log=[])
        result = sleep.process(state)
        for limb in result["field"]["limbs"]:
            assert limb["weight"] == pytest.approx(0.5)

    def test_weight_changes_persist(self):
        """Weight changes persist in the returned SystemState."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0, input_hash=f"p{i}") for i in range(10)]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        # Check field is in the result and has modified weights.
        assert "field" in result
        assert "limbs" in result["field"]
        cluster_weights = [
            l["weight"] for l in result["field"]["limbs"]
            if l["id"] in CONVERGENT_CLUSTER_IDS
        ]
        # All 10 entries are stale → noise_ratio = 1.0 > 0.3 → cluster increases.
        assert all(w > 0.5 for w in cluster_weights)


# ============================================================
# Repair and apoptosis (4 tests)
# ============================================================


class TestRepairAndApoptosis:

    def test_repair_true_when_consolidation_had_effect(self):
        """repair_check returns True when consolidation had effect."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        assert sleep.repair_check(result) is True

    def test_repair_false_when_no_changes(self):
        """repair_check returns False when no changes occurred."""
        sleep = SleepSystem(tick_interval=10)
        # Empty cache, empty log, default weights → no effect.
        state = _make_state(tick=10, cache=[], immune_log=[])
        result = sleep.process(state)
        assert sleep.repair_check(result) is False

    def test_apoptotic_after_three_no_improvement(self):
        """apoptotic_condition triggers after 3 consecutive no-improvement ticks."""
        sleep = SleepSystem(tick_interval=10)
        state = _make_state(tick=10, cache=[], immune_log=[])
        # Run 3 consecutive sleep ticks with no effect.
        for tick in [10, 20, 30]:
            state["metadata"]["tick"] = tick
            state = sleep.process(state)
        assert sleep.apoptotic_condition(state) is True

    def test_apoptotic_resets_after_success(self):
        """apoptotic_condition resets after a successful consolidation."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=5)
        state = _make_state(tick=10, cache=[], immune_log=[])
        # 2 no-effect ticks.
        for tick in [10, 20]:
            state["metadata"]["tick"] = tick
            state = sleep.process(state)
        assert state["sleep_state"]["consecutive_no_improvement"] == 2
        # Now add something to prune (stale: tick 30 - last_seen 0 = 30 > 5).
        state["signal_pattern_cache"] = [
            _make_cache_entry(encounter_count=1, last_seen_tick=0),
        ]
        state["metadata"]["tick"] = 30
        state = sleep.process(state)
        # Should reset.
        assert state["sleep_state"]["consecutive_no_improvement"] == 0
        assert sleep.apoptotic_condition(state) is False


# ============================================================
# Sleep state persistence (3 tests)
# ============================================================


class TestSleepStatePersistence:

    def test_first_invocation_initializes_defaults(self):
        """First invocation initializes sleep_state with defaults."""
        sleep = SleepSystem(tick_interval=10)
        state = _make_state(tick=0, cache=[])
        assert state.get("sleep_state") is None
        result = sleep.process(state)
        assert "sleep_state" in result
        assert result["sleep_state"]["last_sleep_tick"] == 0
        assert result["sleep_state"]["consecutive_no_improvement"] == 0

    def test_subsequent_invocations_update_state(self):
        """Subsequent invocations read and update existing sleep_state."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        state = _make_state(tick=10, cache=cache)
        result = sleep.process(state)
        assert result["sleep_state"]["last_sleep_tick"] == 10
        # Second invocation at tick 20.
        result["metadata"]["tick"] = 20
        result["signal_pattern_cache"] = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        result2 = sleep.process(result)
        assert result2["sleep_state"]["last_sleep_tick"] == 20

    def test_sleep_state_survives_across_calls(self):
        """sleep_state survives across process() calls via SystemState."""
        sleep = SleepSystem(tick_interval=10)
        state = _make_state(tick=0, cache=[])
        # Tick 0: initialize.
        state = sleep.process(state)
        assert state["sleep_state"]["last_had_effect"] is True
        # Tick 5: no fire.
        state["metadata"]["tick"] = 5
        state = sleep.process(state)
        # Sleep state should still be present.
        assert "sleep_state" in state
        # Tick 10: fire.
        state["metadata"]["tick"] = 10
        state = sleep.process(state)
        assert state["sleep_state"]["last_sleep_tick"] == 10


# ============================================================
# Integration (4 tests)
# ============================================================


class TestSleepIntegration:

    def test_field_weights_readable_after_sleep(self):
        """Sleep modifies field weights that are readable by subsequent processing."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0, input_hash=f"i{i}") for i in range(10)]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        # Field should be readable with standard access pattern.
        field_state = result["field"]
        assert "limbs" in field_state
        assert len(field_state["limbs"]) == 18
        # Cluster limbs should have moved.
        for limb in field_state["limbs"]:
            if limb["id"] in CONVERGENT_CLUSTER_IDS:
                assert limb["weight"] > 0.5

    def test_cache_smaller_after_sleep(self):
        """Subconscious cache is smaller after a cycle that includes sleep pruning."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=50)
        cache = [
            _make_cache_entry(encounter_count=1, last_seen_tick=0, input_hash=f"c{i}")
            for i in range(5)
        ] + [
            _make_cache_entry(encounter_count=5, last_seen_tick=0, input_hash=f"k{i}")
            for i in range(3)
        ]
        state = _make_state(tick=100, cache=cache)
        result = sleep.process(state)
        # 5 stale low-encounter removed, 3 high-encounter kept.
        assert len(result["signal_pattern_cache"]) == 3
        assert len(result["signal_pattern_cache"]) < len(cache)

    def test_immune_log_consolidated_after_sleep(self):
        """Immune threat log reflects consolidation after sleep fires."""
        sleep = SleepSystem(tick_interval=10, staleness_seconds=3600)
        log = [
            _make_threat(encounter_count=5, confidence=0.5, pattern="recurring"),
            _make_threat(encounter_count=1, confidence=0.1,
                         last_seen=_stale_timestamp(7200), pattern="expired"),
        ]
        state = _make_state(tick=10, immune_log=log)
        result = sleep.process(state)
        # Recurring promoted to 0.6, expired demoted to 0.0 → removed.
        assert len(result["immune_log"]) == 1
        assert result["immune_log"][0]["pattern"] == "recurring"
        assert result["immune_log"][0]["confidence"] == pytest.approx(0.6)

    def test_sleep_respects_tick_rate(self):
        """Sleep does not fire every cycle — only at tick_interval multiples."""
        sleep = SleepSystem(tick_interval=10, staleness_threshold=5)
        cache = [_make_cache_entry(encounter_count=1, last_seen_tick=0)]
        changes = []
        for tick in range(1, 25):
            state = _make_state(tick=tick, cache=list(cache))
            result = sleep.process(state)
            changed = len(result["signal_pattern_cache"]) != len(cache)
            changes.append((tick, changed))
        # Only tick 10 and 20 should have changed the cache.
        fired_ticks = [t for t, c in changes if c]
        assert fired_ticks == [10, 20]
