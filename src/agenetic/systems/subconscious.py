"""Subconscious system — Signal Pattern Priming.

Relationship to information: Resonates. Surfaces relevant patterns without
explicit reasoning.

Operates in the signal domain: correlates the current signal report against
cached patterns from prior cycles. Determines whether escalation to conscious
is needed based on pattern novelty, deviation magnitude, and immune assessment.

Tick rate: Every cycle, accumulating across cycles.

Uses only Python stdlib — no LLM calls, no external dependencies.
"""

from __future__ import annotations

import math

from agenetic.systems.base import (
    BaseSystem,
    CachedSignalPattern,
    SubconsciousOutput,
    SystemState,
)

MATCH_THRESHOLD = 0.3


def _feature_vector_from_report(report: dict) -> list[float]:
    """Extract six-element feature vector from a signal report."""
    f = report["features"]
    return [f["density"], f["entropy"], f["coherence"],
            f["periodicity"], f["noise_floor"], f["impedance"]]


def _euclidean_distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between two vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _normalize_vector(v: list[float]) -> list[float]:
    """Normalize feature vector for distance computation.

    Only entropy (index 1) needs rescaling: divide by 10.0, cap at 1.0.
    Other features are already in [0, 1] range.
    """
    return [v[0], min(v[1] / 10.0, 1.0), v[2], v[3], v[4], v[5]]


def _default_output() -> SubconsciousOutput:
    """Default "no recommendation" output."""
    return {
        "escalation_recommended": False,
        "escalation_confidence": 0.5,
        "matched_pattern_ids": [],
        "primed_associations": [],
    }


class SubconsciousSystem(BaseSystem):
    """Signal pattern priming layer — correlates current signal against cached patterns.

    Reads signal_report and threat_assessment (not raw input).
    Produces escalation recommendations and primed associations.
    Maintains the signal_pattern_cache across cycles.
    """

    def __init__(self) -> None:
        super().__init__(
            name="subconscious",
            description="Correlates signal patterns against cache, primes associations, recommends escalation",
        )

    @property
    def tick_rate(self) -> str:
        return "every_cycle"

    def process(self, state: SystemState) -> SystemState:
        report = state.get("signal_report")
        if report is None:
            return {**state, "subconscious_output": _default_output()}

        threat = state.get("threat_assessment")
        cache = list(state.get("signal_pattern_cache", []))
        current_vector = _feature_vector_from_report(report)
        current_hash = report["input_hash"]
        signal_type = report["classification"]["signal_type"]
        aggregate_dev = report["delta"]["aggregate_deviation"]
        tick = report["tick"]

        # --- Pattern correlation ---
        matched_ids: list[str] = []
        matched_outcomes: list[str] = []
        primed_associations: list[str] = []

        norm_current = _normalize_vector(current_vector)
        for pattern in cache:
            norm_pattern = _normalize_vector(pattern["feature_vector"])
            dist = _euclidean_distance(norm_current, norm_pattern)
            if dist < MATCH_THRESHOLD:
                matched_ids.append(pattern["input_hash"])
                matched_outcomes.append(pattern["outcome"])
                hash_prefix = pattern["input_hash"][:8]
                count = pattern["encounter_count"]
                outcome = pattern["outcome"]
                primed_associations.append(
                    f"Signal pattern [{hash_prefix}] seen [{count}] times, last outcome: [{outcome}]"
                )

        # --- Escalation decision ---
        threat_level = threat.get("threat_level", "none") if threat else "none"

        if threat_level in ("medium", "high", "critical"):
            escalation_recommended = True
            escalation_confidence = 0.9
        elif not matched_ids and aggregate_dev > 1.5:
            # Novel signal with significant deviation.
            escalation_recommended = True
            escalation_confidence = 0.7
        elif matched_ids:
            escalated_count = sum(1 for o in matched_outcomes if o == "escalated")
            reflex_count = sum(1 for o in matched_outcomes if o == "reflex_response")
            total_matched = len(matched_outcomes)
            if escalated_count > reflex_count:
                escalation_recommended = True
                escalation_confidence = escalated_count / total_matched
            elif reflex_count > escalated_count:
                escalation_recommended = False
                escalation_confidence = reflex_count / total_matched
            else:
                # Tie — default to not escalating.
                escalation_recommended = False
                escalation_confidence = 0.5
        else:
            # No matches, low deviation.
            escalation_recommended = False
            escalation_confidence = 0.5

        # --- Update flags (OR-preserve: upstream True signals survive) ---
        flags = {**state["flags"]}
        existing = state["flags"].get("escalate_to_conscious", False)
        flags["escalate_to_conscious"] = existing or escalation_recommended

        # --- Update cache ---
        outcome = "escalated" if escalation_recommended else "reflex_response"
        existing_idx = None
        for i, p in enumerate(cache):
            if p["input_hash"] == current_hash:
                existing_idx = i
                break

        if existing_idx is not None:
            existing = cache[existing_idx]
            cache[existing_idx] = {
                **existing,
                "encounter_count": existing["encounter_count"] + 1,
                "last_seen_tick": tick,
                "outcome": outcome,
            }
        else:
            new_entry: CachedSignalPattern = {
                "input_hash": current_hash,
                "feature_vector": current_vector,
                "signal_type": signal_type,
                "outcome": outcome,
                "response_pattern_id": None,
                "encounter_count": 1,
                "last_seen_tick": tick,
            }
            cache.append(new_entry)

        # --- Prune stale single-encounter entries ---
        indices_to_remove = [
            i for i, entry in enumerate(cache)
            if entry["encounter_count"] == 1
            and (tick - entry["last_seen_tick"]) > 100
        ]
        for i in reversed(indices_to_remove):
            del cache[i]

        output: SubconsciousOutput = {
            "escalation_recommended": escalation_recommended,
            "escalation_confidence": escalation_confidence,
            "matched_pattern_ids": matched_ids,
            "primed_associations": primed_associations,
        }

        return {
            **state,
            "subconscious_output": output,
            "signal_pattern_cache": cache,
            "flags": flags,
        }

    def repair_check(self, state: SystemState) -> bool:
        output = state.get("subconscious_output")
        if output is None:
            return False
        conf = output.get("escalation_confidence")
        if conf is None or not (0.0 <= conf <= 1.0):
            return False
        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        cache = state.get("signal_pattern_cache", [])
        return len(cache) > 10000
