"""Tests for subconscious system — D016 audit remediation.

Covers:
- Cache pruning (4 tests): stale removal, reinforced preservation, recent preservation, apoptosis prevention
- Escalation flag OR-preservation (3 tests): upstream survives, subconscious can still set, both combine
- Feature vector normalization (4 tests): entropy not dominant, all features matter, raw cache, cap at 1.0

All tests are deterministic — no LLM calls, no API keys.
"""

from agenetic.network.graph import create_default_state
from agenetic.systems.subconscious import SubconsciousSystem


def _make_signal_state(aggregate_deviation=0.5, threat_level="none", tick=0):
    """Create a state with signal report and threat assessment for testing."""
    state = create_default_state(input_data="test")
    state["flags"]["escalate_to_conscious"] = False
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
        "tick": tick, "input_hash": "subtest123",
    }
    state["threat_assessment"] = {
        "is_anomalous": threat_level != "none",
        "anomaly_scores": {},
        "matched_patterns": [],
        "threat_level": threat_level,
        "recommended_action": "proceed",
    }
    return state


def _make_cache_entry(input_hash, encounter_count=1, last_seen_tick=0,
                      feature_vector=None):
    """Create a cache entry for testing."""
    return {
        "input_hash": input_hash,
        "feature_vector": feature_vector or [0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
        "signal_type": "steady_state",
        "outcome": "reflex_response",
        "response_pattern_id": None,
        "encounter_count": encounter_count,
        "last_seen_tick": last_seen_tick,
    }


# ============================================================
# Cache pruning tests (4)
# ============================================================


class TestCachePruning:

    def test_pruning_removes_stale_single_encounter(self):
        """Stale entries (encounter_count=1, >100 ticks old) are removed."""
        sub = SubconsciousSystem()
        state = _make_signal_state(tick=200)
        state["signal_pattern_cache"] = [
            _make_cache_entry("stale_001", encounter_count=1, last_seen_tick=50),
            _make_cache_entry("stale_002", encounter_count=1, last_seen_tick=0),
        ]
        result = sub.process(state)
        cache = result["signal_pattern_cache"]
        hashes = [e["input_hash"] for e in cache]
        assert "stale_001" not in hashes
        assert "stale_002" not in hashes

    def test_pruning_preserves_reinforced_entries(self):
        """Entries with encounter_count > 1 survive even if old."""
        sub = SubconsciousSystem()
        state = _make_signal_state(tick=200)
        state["signal_pattern_cache"] = [
            _make_cache_entry("reinforced_001", encounter_count=5, last_seen_tick=50),
        ]
        result = sub.process(state)
        cache = result["signal_pattern_cache"]
        assert any(e["input_hash"] == "reinforced_001" for e in cache)

    def test_pruning_preserves_recent_entries(self):
        """Entries with encounter_count=1 but recent ticks survive."""
        sub = SubconsciousSystem()
        state = _make_signal_state(tick=200)
        state["signal_pattern_cache"] = [
            _make_cache_entry("recent_001", encounter_count=1, last_seen_tick=150),
        ]
        result = sub.process(state)
        cache = result["signal_pattern_cache"]
        assert any(e["input_hash"] == "recent_001" for e in cache)

    def test_cache_does_not_reach_apoptosis_with_pruning(self):
        """Large cache of stale entries is pruned well below apoptotic threshold."""
        sub = SubconsciousSystem()
        state = _make_signal_state(tick=200)
        state["signal_pattern_cache"] = [
            _make_cache_entry(f"stale_{i:05d}", encounter_count=1, last_seen_tick=0)
            for i in range(9900)
        ]
        result = sub.process(state)
        cache = result["signal_pattern_cache"]
        assert len(cache) < 10000
        assert sub.apoptotic_condition(result) is False


# ============================================================
# Escalation flag OR-preservation tests (3)
# ============================================================


class TestEscalationFlagPreservation:

    def test_preserves_upstream_escalation_flag(self):
        """Upstream True flag survives when subconscious doesn't escalate."""
        sub = SubconsciousSystem()
        state = _make_signal_state(aggregate_deviation=0.5)
        state["flags"]["escalate_to_conscious"] = True
        result = sub.process(state)
        # OR-preservation: True OR False = True
        assert result["flags"]["escalate_to_conscious"] is True

    def test_subconscious_can_still_escalate(self):
        """Subconscious sets flag when it recommends escalation."""
        sub = SubconsciousSystem()
        state = _make_signal_state(aggregate_deviation=2.0)
        state["flags"]["escalate_to_conscious"] = False
        result = sub.process(state)
        # Subconscious recommends escalation: False OR True = True
        assert result["flags"]["escalate_to_conscious"] is True

    def test_both_sources_combine(self):
        """Both upstream and subconscious True → flag is True."""
        sub = SubconsciousSystem()
        state = _make_signal_state(aggregate_deviation=2.0)
        state["flags"]["escalate_to_conscious"] = True
        result = sub.process(state)
        # True OR True = True
        assert result["flags"]["escalate_to_conscious"] is True


# ============================================================
# Feature vector normalization tests (4)
# ============================================================


class TestFeatureNormalization:

    def test_normalized_distance_entropy_not_dominant(self):
        """After normalization, entropy diff 2.0 and density diff 0.2 produce similar distances."""
        from agenetic.systems.subconscious import _normalize_vector, _euclidean_distance

        base = [0.5, 5.0, 0.5, 0.1, 0.05, 0.1]
        entropy_diff = [0.5, 7.0, 0.5, 0.1, 0.05, 0.1]  # Entropy +2.0
        density_diff = [0.7, 5.0, 0.5, 0.1, 0.05, 0.1]  # Density +0.2

        # Raw distances: entropy dominates
        raw_entropy_dist = _euclidean_distance(base, entropy_diff)
        raw_density_dist = _euclidean_distance(base, density_diff)
        assert raw_entropy_dist > 5 * raw_density_dist

        # Normalized distances: approximately equal
        norm_base = _normalize_vector(base)
        norm_entropy = _normalize_vector(entropy_diff)
        norm_density = _normalize_vector(density_diff)

        norm_entropy_dist = _euclidean_distance(norm_base, norm_entropy)
        norm_density_dist = _euclidean_distance(norm_base, norm_density)
        assert abs(norm_entropy_dist - norm_density_dist) < 0.01

    def test_matching_considers_all_features(self):
        """Pattern with same entropy but different density does not match."""
        sub = SubconsciousSystem()
        state = _make_signal_state(tick=1)
        # Cache entry with very different density (0.1 vs current 0.8)
        state["signal_pattern_cache"] = [
            _make_cache_entry(
                "diff_density_001",
                feature_vector=[0.1, 3.5, 0.7, 0.1, 0.05, 0.1],
            ),
        ]
        result = sub.process(state)
        assert "diff_density_001" not in result["subconscious_output"]["matched_pattern_ids"]

    def test_normalization_does_not_alter_cached_values(self):
        """Cached patterns store raw (unnormalized) feature values."""
        sub = SubconsciousSystem()
        state = _make_signal_state(tick=1)
        state["signal_report"]["features"]["entropy"] = 8.0
        result = sub.process(state)
        cache = result["signal_pattern_cache"]
        new_entry = [e for e in cache if e["input_hash"] == "subtest123"]
        assert len(new_entry) == 1
        # Entropy at index 1 should be the raw value, not normalized
        assert new_entry[0]["feature_vector"][1] == 8.0

    def test_entropy_capped_at_one(self):
        """Normalization caps entropy at 1.0 for values above 10.0."""
        from agenetic.systems.subconscious import _normalize_vector

        v = [0.5, 15.0, 0.5, 0.1, 0.05, 0.1]
        norm = _normalize_vector(v)
        assert norm[1] == 1.0  # 15.0 / 10.0 = 1.5, capped at 1.0
