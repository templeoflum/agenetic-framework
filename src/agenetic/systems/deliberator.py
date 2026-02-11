"""Deliberator protocol — the abstraction between conscious framing and LLM engine.

The conscious layer owns what the LLM sees (prompt assembly from compressed state)
and how the response is structured (parsed into ConsciousOutput). The engine behind
the protocol is swappable: Anthropic API, local models, Claude Code native context.

The protocol uses Python's Protocol (structural typing) rather than ABC. Any object
with the right method signatures is a Deliberator. No inheritance required.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from agenetic.systems.base import ConsciousOutput


class DeliberationRequest:
    """Structured input to a Deliberator — what the LLM should reason about.

    Assembled by the conscious layer from compressed signal state + field.
    The Deliberator implementation translates this into whatever format
    its backend expects (messages API, local model prompt, etc.).
    """

    def __init__(
        self,
        input_text: str,
        signal_summary: dict,
        threat_summary: dict,
        subconscious_summary: dict,
        field_state: dict[str, float],
        active_limbs: list[dict],
        resting_stance: float,
        expression_directives: dict,
    ):
        self.input_text = input_text
        self.signal_summary = signal_summary
        self.threat_summary = threat_summary
        self.subconscious_summary = subconscious_summary
        self.field_state = field_state
        self.active_limbs = active_limbs
        self.resting_stance = resting_stance
        self.expression_directives = expression_directives


@runtime_checkable
class Deliberator(Protocol):
    """Protocol for LLM backends that perform conscious deliberation.

    Any object implementing deliberate() with the right signature is a Deliberator.
    No inheritance required — structural typing via Protocol.
    """

    def deliberate(self, request: DeliberationRequest) -> ConsciousOutput:
        """Perform deliberation and return structured conscious output.

        The implementation is responsible for:
        1. Translating the DeliberationRequest into its backend's format
        2. Making the LLM call (or equivalent)
        3. Parsing the response into ConsciousOutput

        Must set lineage.deliberation_model to identify which backend was used.
        """
        ...


class MockDeliberator:
    """Deterministic deliberator for testing. No API calls."""

    def __init__(self, default_strategy: str = "direct_response"):
        self.default_strategy = default_strategy
        self.call_count = 0
        self.last_request: DeliberationRequest | None = None

    def deliberate(self, request: DeliberationRequest) -> ConsciousOutput:
        self.call_count += 1
        self.last_request = request

        return {
            "decision": {
                "intent": f"respond_to_{request.signal_summary.get('classification', 'unknown')}",
                "strategy": self.default_strategy,
                "constraints": [limb["name"] for limb in request.active_limbs],
            },
            "expression": {
                "field_weights": request.field_state,
                "active_limbs": [limb["name"] for limb in request.active_limbs],
                "resting_stance": request.resting_stance,
                "suppress_identity": any(
                    limb["id"] == 13 and limb["weight"] > 0.6
                    for limb in request.active_limbs
                ),
                "state_awareness": "active",
            },
            "lineage": {
                "escalation_reason": request.subconscious_summary.get(
                    "escalation_reason", "unknown"
                ),
                "signal_summary": request.signal_summary,
                "field_snapshot": request.field_state,
                "gate_evaluation": {"proceed": True, "reason": "default_proceed"},
                "deliberation_model": "mock",
            },
            "proceed": True,
            "confidence": 0.8,
            "re_examine": False,
        }
