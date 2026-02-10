"""Anthropic API deliberator — first real LLM-backed Deliberator implementation.

Translates DeliberationRequest into an Anthropic Messages API call,
parses the response into ConsciousOutput. Prompt assembly is delegated to
the prompt_assembly module; this module handles API communication and
response parsing only.
"""

from __future__ import annotations

import json
import os

import anthropic

from agenetic.systems.base import ConsciousOutput
from agenetic.systems.deliberator import DeliberationRequest
from agenetic.systems.prompt_assembly import assemble_system_prompt, assemble_user_message


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
        system_prompt = assemble_system_prompt(
            active_limbs=request.active_limbs,
            resting_stance=request.resting_stance,
            expression_directives=request.expression_directives,
        )
        user_message = assemble_user_message(request)

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
