"""Immune system — Signal Anomaly Detection.

Relationship to information: Evaluates. Distinguishes self from not-self.

Operates in the signal domain: reads the signal report produced by sensory,
never the raw input. Detects anomalies through innate thresholds (fixed
pattern matching) and adaptive matching (threat log correlation).

Tick rate: Every cycle. Boundary enforcement is continuous.

Uses only Python stdlib — no LLM calls, no external dependencies.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone

from agenetic.systems.base import (
    BaseSystem,
    SystemState,
    ThreatAssessment,
    ThreatEntry,
)


def _feature_vector(features: dict) -> list[float]:
    """Extract the six-element feature vector from signal features."""
    return [
        features["density"],
        features["entropy"],
        features["coherence"],
        features["periodicity"],
        features["noise_floor"],
        features["impedance"],
    ]


def _euclidean_distance(a: list[float], b: list[float]) -> float:
    """Euclidean distance between two vectors."""
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _default_assessment() -> ThreatAssessment:
    """Default "proceed" assessment when no signal report is available."""
    return {
        "is_anomalous": False,
        "anomaly_scores": {},
        "matched_patterns": [],
        "threat_level": "none",
        "recommended_action": "proceed",
    }


class ImmuneSystem(BaseSystem):
    """Signal anomaly detection layer — innate thresholds + adaptive matching.

    Operates entirely in the signal domain: reads signal_report, not input.
    Produces a ThreatAssessment consumed by subconscious and conscious.
    """

    ADAPTIVE_MATCH_THRESHOLD = 0.5

    def __init__(self) -> None:
        super().__init__(
            name="immune",
            description="Detects signal anomalies through innate thresholds and adaptive pattern matching",
        )
        self._consecutive_critical_count = 0

    @property
    def tick_rate(self) -> str:
        return "every_cycle"

    def process(self, state: SystemState) -> SystemState:
        report = state.get("signal_report")
        if report is None:
            return {**state, "threat_assessment": _default_assessment()}

        features = report["features"]
        delta = report["delta"]
        anomaly_scores: dict[str, float] = {}

        # --- Innate immunity: fixed threshold checks ---
        if features["entropy"] > 6.0:
            anomaly_scores["entropy"] = features["entropy"] - 6.0

        if features["noise_floor"] > 0.35:
            anomaly_scores["noise_floor"] = features["noise_floor"] - 0.35

        if features["impedance"] > 0.5:
            anomaly_scores["impedance"] = features["impedance"] - 0.5

        if delta["aggregate_deviation"] > 3.0:
            anomaly_scores["aggregate_deviation"] = delta["aggregate_deviation"] - 3.0

        if features["vocabulary_richness"] < 0.1:
            anomaly_scores["vocabulary_richness"] = 0.1 - features["vocabulary_richness"]

        # --- Adaptive immunity: threat log pattern matching ---
        current_vector = _feature_vector(features)
        immune_log = list(state.get("immune_log", []))
        matched_patterns: list[str] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for i, entry in enumerate(immune_log):
            try:
                logged_vector = json.loads(entry["pattern"])
                if isinstance(logged_vector, list) and len(logged_vector) == 6:
                    dist = _euclidean_distance(current_vector, logged_vector)
                    if dist < self.ADAPTIVE_MATCH_THRESHOLD:
                        matched_patterns.append(entry["pattern"])
                        # Update encounter count and timestamp.
                        immune_log[i] = {
                            **entry,
                            "encounter_count": entry["encounter_count"] + 1,
                            "last_seen": now_iso,
                        }
                        # Matched patterns increase overall threat.
                        anomaly_scores["adaptive_match"] = (
                            anomaly_scores.get("adaptive_match", 0.0)
                            + entry["confidence"] * (1.0 + 0.1 * entry["encounter_count"])
                        )
            except (json.JSONDecodeError, TypeError, KeyError):
                continue

        # --- Compute threat level ---
        total_score = sum(anomaly_scores.values())
        if total_score < 0.5:
            threat_level = "none"
        elif total_score < 1.5:
            threat_level = "low"
        elif total_score < 3.0:
            threat_level = "medium"
        elif total_score < 5.0:
            threat_level = "high"
        else:
            threat_level = "critical"

        # --- Compute recommended action ---
        if threat_level in ("none", "low"):
            action = "proceed"
        elif threat_level == "medium":
            action = "flag"
        elif threat_level == "high":
            action = "quarantine"
        else:
            action = "reject"

        is_anomalous = total_score >= 0.5

        assessment: ThreatAssessment = {
            "is_anomalous": is_anomalous,
            "anomaly_scores": anomaly_scores,
            "matched_patterns": matched_patterns,
            "threat_level": threat_level,
            "recommended_action": action,
        }

        # --- Update flags ---
        flags = {**state["flags"]}
        if action in ("flag", "quarantine"):
            flags["escalate_to_conscious"] = True
        if action == "quarantine":
            degraded = list(flags["degraded"])
            degraded.append("immune")
            flags["degraded"] = degraded
        if action == "reject":
            flags["apoptotic"] = True
        if threat_level == "critical":
            flags["escalate_to_conscious"] = True

        # --- Add new anomalous pattern to immune_log ---
        if threat_level in ("medium", "high", "critical") and not matched_patterns:
            pattern_str = json.dumps(current_vector)
            confidence_map = {"medium": 0.6, "high": 0.8, "critical": 1.0}
            new_entry: ThreatEntry = {
                "pattern": pattern_str,
                "encounter_count": 1,
                "confidence": confidence_map.get(threat_level, 0.5),
                "last_seen": now_iso,
            }
            immune_log.append(new_entry)

        # Track consecutive critical ticks for apoptotic condition.
        if threat_level == "critical":
            self._consecutive_critical_count += 1
        else:
            self._consecutive_critical_count = 0

        return {
            **state,
            "threat_assessment": assessment,
            "immune_log": immune_log,
            "flags": flags,
        }

    def repair_check(self, state: SystemState) -> bool:
        assessment = state.get("threat_assessment")
        if assessment is None:
            return False
        valid_levels = {"none", "low", "medium", "high", "critical"}
        if assessment.get("threat_level") not in valid_levels:
            return False
        valid_actions = {"proceed", "flag", "quarantine", "reject"}
        if assessment.get("recommended_action") not in valid_actions:
            return False
        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        return self._consecutive_critical_count >= 3
