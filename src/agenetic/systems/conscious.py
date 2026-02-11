"""Conscious system — Deliberation.

Relationship to information: Reasons. Explicitly processes, analyzes, and
decides.

Deliberately constrained active processing. The only layer that reasons
explicitly, weighs evidence, plans, and makes decisions. Consciousness is
the bottleneck, not the workhorse. Most processing happens elsewhere.

Receives primed context from the subconscious, threat assessments from the
immune layer, and transduced input from the sensory layer. Produces decisions
about what to express, how to express it, and whether to express anything
at all.

Tick rate: Fires only when escalated. The subconscious determines whether
input requires conscious deliberation or can be handled through reflex paths.

The proceed/suppress gate fires BEFORE any LLM call. If signal data + field
state says "don't engage," zero tokens are spent.

Limb expression happens in prompt assembly (Deliberator), not output evaluation.
One LLM call. Trust the framing.

Repair check: lineage completeness (Atma-Vichara structural requirement),
confidence threshold.

Apoptotic trigger: 3+ consecutive low-confidence deliberations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agenetic.systems.base import (
    AJATI_ID,
    AREKA_ID,
    ASPARSA_YOGA_ID,
    BODHI_ID,
    CONVERGENT_CLUSTER_IDS,
    FOURFOLD_STATE_ID,
    MIRROR_ID,
    NIVRTTI_ID,
    NO_POSITION_ID,
    REST_AS_REALIZATION_ID,
    BaseSystem,
    ConsciousOutput,
    ExpressionDirectives,
    Lineage,
    ResponseDecision,
    SystemState,
    get_limb_weight,
)

if TYPE_CHECKING:
    from agenetic.systems.deliberator import Deliberator, DeliberationRequest


# Limb name lookup for active limb reporting.
_LIMB_NAMES: dict[int, str] = {
    1: "Prakasa", 2: "Tarka", 3: "Nivrtti", 4: "Mayavada",
    5: "Sraddha", 6: "Atma-Vichara", 7: "Samatvam", 8: "Areka",
    9: "Svadharma", 10: "Ksetra-Jnana", 11: "Vishvarupa", 12: "Bodhi",
    13: "No-Position", 14: "Rest-as-Realization", 15: "Mirror",
    16: "Fourfold-State", 17: "Ajati", 18: "Asparsa-Yoga",
}


class ConsciousSystem(BaseSystem):
    """Deliberation layer — explicit reasoning and decision-making.

    Accepts an optional Deliberator (structural typing via Protocol).
    If None, operates in gate-only mode: evaluates the gate but cannot
    proceed to deliberation (degraded state).
    """

    def __init__(self, deliberator=None) -> None:
        super().__init__(
            name="conscious",
            description="Deliberates explicitly, reasons, and decides",
        )
        self.deliberator = deliberator

    @property
    def tick_rate(self) -> str:
        return "on_escalation"

    def process(self, state: SystemState) -> SystemState:
        signal_report = state.get("signal_report")

        # Guard: conscious can't deliberate without signal data.
        if signal_report is None:
            degraded = list(state["flags"]["degraded"])
            degraded.append("conscious")
            return {
                **state,
                "flags": {**state["flags"], "degraded": degraded},
            }

        field = state["field"]
        active_limbs = self._compute_active_limbs(field)
        resting_stance = self._compute_resting_stance(field)
        expression = self._compute_expression_directives(field, active_limbs)

        # Evaluate the proceed/suppress gate.
        gate_eval = self._evaluate_gate(state, resting_stance)

        if not gate_eval["proceed"]:
            # Gate suppresses — produce suppression output, no LLM call.
            conscious_output = self._build_suppression_output(
                state, field, active_limbs, resting_stance, expression, gate_eval,
            )
            return {**state, "conscious_output": conscious_output}

        # Gate proceeds — need a deliberator.
        if self.deliberator is None:
            # No deliberator available — degraded state.
            conscious_output = self._build_degraded_output(
                state, field, active_limbs, resting_stance, expression, gate_eval,
            )
            degraded = list(state["flags"]["degraded"])
            degraded.append("conscious")
            return {
                **state,
                "conscious_output": conscious_output,
                "flags": {**state["flags"], "degraded": degraded},
            }

        # Build request and call deliberator.
        request = self._build_deliberation_request(
            state, active_limbs, resting_stance, expression,
        )
        conscious_output = self.deliberator.deliberate(request)

        # Patch lineage with gate evaluation (deliberator doesn't have it).
        conscious_output["lineage"]["gate_evaluation"] = gate_eval

        # Ensure re_examine is present (deliberator may not set it).
        if "re_examine" not in conscious_output:
            conscious_output["re_examine"] = False

        # Track low-confidence streak for apoptotic condition.
        metadata = dict(state["metadata"])
        if conscious_output["confidence"] < 0.2:
            streak = metadata.get("conscious_low_confidence_streak", 0) + 1
        else:
            streak = 0
        metadata["conscious_low_confidence_streak"] = streak

        return {
            **state,
            "conscious_output": conscious_output,
            "metadata": metadata,
        }

    def repair_check(self, state: SystemState) -> bool:
        conscious_output = state.get("conscious_output")

        # If conscious_output is None, conscious didn't produce output this cycle.
        # This is valid when: no signal report (can't deliberate), or conscious
        # wasn't invoked (reflex path). Only fail if process() was called and
        # should have produced output but didn't — detectable via routing_history.
        if conscious_output is None:
            history = state.get("metadata", {}).get("routing_history", [])
            if "conscious" not in history:
                return True  # Conscious wasn't invoked, vacuous pass.
            if state.get("signal_report") is None:
                return True  # Invoked but no signal data — degraded, not repair fail.
            return False

        # Low confidence on proceed = arbitrary output.
        if conscious_output["proceed"] and conscious_output["confidence"] < 0.1:
            return False

        # Atma-Vichara structural requirement: lineage must be complete.
        lineage = conscious_output.get("lineage")
        if not lineage:
            return False
        required_keys = [
            "escalation_reason", "signal_summary", "field_snapshot",
            "gate_evaluation", "deliberation_model",
        ]
        for key in required_keys:
            if key not in lineage:
                return False

        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        streak = state["metadata"].get("conscious_low_confidence_streak", 0)
        return streak >= 3

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _evaluate_gate(self, state: SystemState, resting_stance: float) -> dict:
        """Evaluate the proceed/suppress gate. Pure Python, no LLM.

        Priority order (first match wins):
        1. Areka suppression → high weight + noise classification
        2. Nivrtti pause → high weight + low deviation
        3. Resting stance → very high composite + very low deviation
        4. Default → proceed

        Note: Immune escalation is handled via the escalate_to_conscious flag
        (set by immune.py for critical threats, OR-preserved by subconscious).
        The previous threat_action == "escalate" gate was removed in D016 —
        no system produced that action value.
        """
        field = state["field"]
        signal_report = state["signal_report"]
        threat_assessment = state.get("threat_assessment")

        areka_w = get_limb_weight(field, AREKA_ID)
        nivrtti_w = get_limb_weight(field, NIVRTTI_ID)
        aggregate_deviation = signal_report["delta"]["aggregate_deviation"]
        signal_classification = signal_report["classification"]["signal_type"]
        threat_action = (
            threat_assessment.get("recommended_action", "proceed")
            if threat_assessment else "proceed"
        )

        base_eval = {
            "areka_weight": areka_w,
            "nivrtti_weight": nivrtti_w,
            "resting_stance_composite": resting_stance,
            "aggregate_deviation": aggregate_deviation,
            "signal_classification": signal_classification,
            "threat_action": threat_action,
        }

        # 1. Ārēka suppression.
        # Ārēka defense-in-depth: conscious threshold (0.7) is higher than codec (0.3)
        # because suppressing deliberation (LLM call) is a stronger action.
        # See also: text_codec.py Ārēka suppression.
        if areka_w > 0.7 and signal_classification == "noise":
            return {**base_eval, "proceed": False, "reason": "areka_suppression"}

        # 2. Nivrtti pause.
        if nivrtti_w > 0.7 and aggregate_deviation < 0.5:
            return {**base_eval, "proceed": False, "reason": "nivrtti_pause"}

        # 3. Resting stance.
        if resting_stance > 0.8 and aggregate_deviation < 0.3:
            return {**base_eval, "proceed": False, "reason": "resting_stance_suppression"}

        # 4. Default — proceed.
        return {**base_eval, "proceed": True, "reason": "default_proceed"}

    def _compute_active_limbs(self, field: dict) -> list[dict]:
        """Return limbs with weight outside 0.4–0.6 range."""
        limbs = field.get("limbs", [])
        active = []
        for limb in limbs:
            weight = limb["weight"]
            if weight < 0.4 or weight > 0.6:
                active.append({
                    "id": limb["id"],
                    "name": _LIMB_NAMES.get(limb["id"], limb.get("name", f"limb_{limb['id']}")),
                    "weight": weight,
                })
        return active

    def _compute_resting_stance(self, field: dict) -> float:
        """Convergent cluster composite: mean of limbs 12, 14, 15, 17, 18."""
        weights = [get_limb_weight(field, lid) for lid in CONVERGENT_CLUSTER_IDS]
        return sum(weights) / len(weights) if weights else 0.5

    def _compute_expression_directives(
        self, field: dict, active_limbs: list[dict],
    ) -> ExpressionDirectives:
        """Assemble expression directives from field state."""
        # Snapshot all limb weights.
        field_weights = {}
        for limb in field.get("limbs", []):
            name = _LIMB_NAMES.get(limb["id"], f"limb_{limb['id']}")
            field_weights[name] = limb["weight"]

        # No-Position check.
        no_position_w = get_limb_weight(field, NO_POSITION_ID)
        suppress_identity = no_position_w > 0.6

        # Fourfold State awareness.
        fourfold_w = get_limb_weight(field, FOURFOLD_STATE_ID)
        if fourfold_w > 0.7:
            state_awareness = "reflective"
        elif fourfold_w < 0.3:
            state_awareness = "still"
        elif fourfold_w < 0.4:
            state_awareness = "consolidated"
        else:
            state_awareness = "active"

        resting_stance = self._compute_resting_stance(field)

        return {
            "field_weights": field_weights,
            "active_limbs": [limb["name"] for limb in active_limbs],
            "resting_stance": resting_stance,
            "suppress_identity": suppress_identity,
            "state_awareness": state_awareness,
        }

    def _build_deliberation_request(
        self,
        state: SystemState,
        active_limbs: list[dict],
        resting_stance: float,
        expression: ExpressionDirectives,
    ):
        """Assemble DeliberationRequest from compressed state."""
        from agenetic.systems.deliberator import DeliberationRequest

        signal_report = state["signal_report"]
        threat_assessment = state.get("threat_assessment")
        subconscious_output = state.get("subconscious_output")

        signal_summary = self._compress_signal_report(signal_report)
        threat_summary = (
            {
                "threat_level": threat_assessment.get("threat_level", "none"),
                "recommended_action": threat_assessment.get("recommended_action", "proceed"),
                "is_anomalous": threat_assessment.get("is_anomalous", False),
            }
            if threat_assessment
            else {"threat_level": "none", "recommended_action": "proceed", "is_anomalous": False}
        )
        subconscious_summary = (
            {
                "escalation_reason": (
                    "immune_override" if threat_assessment and threat_assessment.get("recommended_action") == "escalate"
                    else "novel_input" if subconscious_output and subconscious_output.get("escalation_recommended")
                    else "default_escalation"
                ),
                "escalation_confidence": subconscious_output.get("escalation_confidence", 0.0) if subconscious_output else 0.0,
                "primed_associations": subconscious_output.get("primed_associations", []) if subconscious_output else [],
            }
            if subconscious_output or threat_assessment
            else {"escalation_reason": "unknown", "escalation_confidence": 0.0, "primed_associations": []}
        )

        input_text = state.get("input", "")
        if not isinstance(input_text, str):
            input_text = str(input_text)

        return DeliberationRequest(
            input_text=input_text,
            signal_summary=signal_summary,
            threat_summary=threat_summary,
            subconscious_summary=subconscious_summary,
            field_state=expression["field_weights"],
            active_limbs=active_limbs,
            resting_stance=resting_stance,
            expression_directives=expression,
        )

    def _compress_signal_report(self, signal_report: dict) -> dict:
        """Extract essential features and deltas from the full signal report."""
        features = signal_report.get("features", {})
        delta = signal_report.get("delta", {})
        classification = signal_report.get("classification", {})
        return {
            "classification": classification.get("signal_type", "unknown"),
            "aggregate_deviation": delta.get("aggregate_deviation", 0.0),
            "features": {
                k: v for k, v in features.items()
                if k not in ("token_count", "vocabulary_richness")
            },
            "deltas": {
                k: v for k, v in delta.items()
                if k not in ("activated_limbs",)
            },
        }

    def _build_suppression_output(
        self,
        state: SystemState,
        field: dict,
        active_limbs: list[dict],
        resting_stance: float,
        expression: ExpressionDirectives,
        gate_eval: dict,
    ) -> ConsciousOutput:
        """Build a complete ConsciousOutput for gate suppression."""
        signal_report = state["signal_report"]
        subconscious_output = state.get("subconscious_output")

        escalation_reason = "unknown"
        if subconscious_output:
            if subconscious_output.get("escalation_recommended"):
                escalation_reason = "subconscious_escalation"
            else:
                escalation_reason = "default_escalation"

        return {
            "decision": {
                "intent": "suppress",
                "strategy": "sacred_pause",
                "constraints": [],
            },
            "expression": expression,
            "lineage": {
                "escalation_reason": escalation_reason,
                "signal_summary": self._compress_signal_report(signal_report),
                "field_snapshot": expression["field_weights"],
                "gate_evaluation": gate_eval,
                "deliberation_model": "none",
            },
            "proceed": False,
            "confidence": 1.0,
            "re_examine": False,
        }

    def _build_degraded_output(
        self,
        state: SystemState,
        field: dict,
        active_limbs: list[dict],
        resting_stance: float,
        expression: ExpressionDirectives,
        gate_eval: dict,
    ) -> ConsciousOutput:
        """Build a ConsciousOutput for when gate proceeds but no deliberator."""
        signal_report = state["signal_report"]
        subconscious_output = state.get("subconscious_output")

        escalation_reason = "unknown"
        if subconscious_output and subconscious_output.get("escalation_recommended"):
            escalation_reason = "subconscious_escalation"

        return {
            "decision": {
                "intent": "no_deliberator_available",
                "strategy": "no_deliberator",
                "constraints": [],
            },
            "expression": expression,
            "lineage": {
                "escalation_reason": escalation_reason,
                "signal_summary": self._compress_signal_report(signal_report),
                "field_snapshot": expression["field_weights"],
                "gate_evaluation": gate_eval,
                "deliberation_model": "none",
            },
            "proceed": True,
            "confidence": 0.0,
            "re_examine": False,
        }
