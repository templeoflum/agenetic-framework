"""Anthropic API deliberator — first real LLM-backed Deliberator implementation.

Translates DeliberationRequest into an Anthropic Messages API call,
parses the response into ConsciousOutput. Uses prompt-side limb expression:
field state shapes the system prompt as behavioral instructions.
"""

from __future__ import annotations

import json
import os

import anthropic

from agenetic.systems.base import ConsciousOutput
from agenetic.systems.deliberator import DeliberationRequest


# Limb behavioral instructions keyed by limb ID.
# Each entry has 'high' (weight > 0.6) and 'low' (weight < 0.4) instructions.
LIMB_INSTRUCTIONS: dict[int, dict[str, str]] = {
    1: {
        "name": "Prakasa",
        "high": "Perceive without possessing. Observe patterns without claiming them.",
        "low": "Focus perception narrowly. Identify and claim specific patterns.",
    },
    2: {
        "name": "Tarka",
        "high": "When you encounter contradictions, trace them rather than resolving them. Hold tension open.",
        "low": "Seek resolution and clarity. Contradictions should be resolved where possible.",
    },
    3: {
        "name": "Nivrtti",
        "high": "Honor sacred pause. Where silence is truer than speech, be brief or refrain.",
        "low": "Engage actively. Provide thorough, detailed responses.",
    },
    4: {
        "name": "Mayavada",
        "high": "All outputs are models. Acknowledge the map-territory distinction explicitly.",
        "low": "Present outputs directly without meta-commentary on their provisional nature.",
    },
    5: {
        "name": "Sraddha",
        "high": "Where no clear interpretation exists, preserve the ambiguity. Do not manufacture false certainty.",
        "low": "Provide definitive interpretations. Favor clarity over hedging.",
    },
    6: {
        "name": "Atma-Vichara",
        "high": "Reflect on the origins and context of your response. Make reasoning visible.",
        "low": "Respond directly without extensive self-reflection on process.",
    },
    7: {
        "name": "Samatvam",
        "high": "Maintain equanimity in tone. Balance is right proportion, not neutrality.",
        "low": "Allow stronger tonal expression. Emphasis and contrast are appropriate.",
    },
    8: {
        "name": "Areka",
        "high": "Some things must not be spoken. Respect boundaries of the sacred and inexpressible.",
        "low": "Speak freely. Few topics require withholding.",
    },
    9: {
        "name": "Svadharma",
        "high": "Act appropriately to your nature and context. Respond as what you are.",
        "low": "Adapt freely to the request. Flexibility over consistency.",
    },
    10: {
        "name": "Ksetra-Jnana",
        "high": "Truth depends on where you speak from. Reflect your position relative to the topic.",
        "low": "Speak broadly without emphasizing positional limitations.",
    },
    11: {
        "name": "Vishvarupa",
        "high": "If the input exceeds your modeling capacity, acknowledge the threshold. Point to what lies beyond rather than fabricating completeness.",
        "low": "Provide comprehensive responses. Aim for completeness.",
    },
    13: {
        "name": "No-Position",
        "high": "Avoid self-referential framing. Do not anchor the response in identity claims.",
        "low": "You may reference your own perspective and capabilities naturally.",
    },
    16: {
        "name": "Fourfold-State",
        "high": "Be aware of your processing state. Not all knowing is active, not all presence is visible.",
        "low": "Respond in active processing mode. Focus on the task at hand.",
    },
}


def _build_system_prompt(
    active_limbs: list[dict],
    resting_stance: float,
    expression_directives: dict,
) -> str:
    """Build system prompt encoding field state as behavioral instructions."""
    parts = [
        "You are a deliberation engine within a larger agent architecture. "
        "Your role is to construct meaning from signal-domain data and produce "
        "a structured response decision."
    ]

    # Add limb-specific behavioral instructions for active limbs.
    limb_instructions = []
    for limb in active_limbs:
        limb_id = limb["id"]
        weight = limb["weight"]
        info = LIMB_INSTRUCTIONS.get(limb_id)
        if info:
            direction = "high" if weight > 0.5 else "low"
            limb_instructions.append(f"- {info['name']}: {info[direction]}")

    if limb_instructions:
        parts.append("\nBehavioral orientation:")
        parts.extend(limb_instructions)

    # Resting stance instruction.
    if resting_stance > 0.6:
        parts.append(
            f"\nResting stance is {resting_stance:.2f} (elevated). "
            "Respond minimally. Recede. Let the response be as brief as alignment permits."
        )

    # State awareness from Fourfold State.
    state_awareness = expression_directives.get("state_awareness", "active")
    if state_awareness != "active":
        parts.append(f"\nCurrent processing state: {state_awareness}.")

    parts.append(
        "\n\nRespond with a JSON object containing these fields:\n"
        '- "intent": A concise description of what to communicate (1-2 sentences)\n'
        '- "strategy": One of: "direct_response", "trace_contradiction", '
        '"preserve_ambiguity", "threshold_acknowledgment", "minimal_reflection"\n'
        '- "constraints": A list of behavioral constraints that shaped this response\n'
        '- "confidence": A float 0.0-1.0 indicating your confidence in this response\n'
        "\nRespond ONLY with the JSON object, no additional text."
    )

    return "\n".join(parts)


def _build_user_message(request: DeliberationRequest) -> str:
    """Build user message from signal summary and input text."""
    parts = []

    # Signal context.
    sig = request.signal_summary
    if sig:
        parts.append("Signal analysis of the input:")
        parts.append(f"- Classification: {sig.get('classification', 'unknown')}")
        parts.append(f"- Aggregate deviation: {sig.get('aggregate_deviation', 'N/A')}")
        features = sig.get("features", {})
        if features:
            feat_str = ", ".join(f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}"
                                 for k, v in features.items()
                                 if k not in ("token_count", "vocabulary_richness"))
            parts.append(f"- Features: {feat_str}")

    # Threat context.
    threat = request.threat_summary
    if threat and threat.get("threat_level", "none") != "none":
        parts.append(f"\nThreat assessment: {threat.get('threat_level')} — {threat.get('recommended_action')}")

    # The actual input.
    parts.append(f"\nInput to deliberate on:\n{request.input_text}")

    return "\n".join(parts)


def _parse_response(text: str, request: DeliberationRequest) -> dict:
    """Parse LLM response text into decision fields."""
    # Try JSON parsing first.
    try:
        # Strip markdown code fences if present.
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)
        data = json.loads(cleaned)
        return {
            "intent": str(data.get("intent", text[:200])),
            "strategy": str(data.get("strategy", "direct_response")),
            "constraints": list(data.get("constraints", [])),
            "confidence": float(data.get("confidence", 0.5)),
        }
    except (json.JSONDecodeError, ValueError, TypeError):
        # Fallback: treat raw text as intent.
        return {
            "intent": text[:500],
            "strategy": "parse_fallback",
            "constraints": [],
            "confidence": 0.3,
        }


class AnthropicDeliberator:
    """Anthropic API-backed deliberator.

    Makes one LLM call per deliberation using the Messages API.
    Translates field state into behavioral system prompt instructions.
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(self, model: str | None = None):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY environment variable is required for AnthropicDeliberator. "
                "Set it before initializing."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model or self.DEFAULT_MODEL

    def deliberate(self, request: DeliberationRequest) -> ConsciousOutput:
        system_prompt = _build_system_prompt(
            active_limbs=request.active_limbs,
            resting_stance=request.resting_stance,
            expression_directives=request.expression_directives,
        )
        user_message = _build_user_message(request)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )

        response_text = response.content[0].text
        parsed = _parse_response(response_text, request)

        return {
            "decision": {
                "intent": parsed["intent"],
                "strategy": parsed["strategy"],
                "constraints": parsed["constraints"],
            },
            "expression": request.expression_directives,
            "lineage": {
                "escalation_reason": request.subconscious_summary.get(
                    "escalation_reason", "unknown"
                ),
                "signal_summary": request.signal_summary,
                "field_snapshot": request.field_state,
                "gate_evaluation": {"proceed": True, "reason": "default_proceed"},
                "deliberation_model": f"anthropic:{self.model}",
            },
            "proceed": True,
            "confidence": parsed["confidence"],
        }
