"""Prompt assembly — translates field state into behavioral framing for LLM deliberation.

This module is the conscious layer's "what the LLM sees." Any Deliberator
implementation can import and use it, or override it entirely.

Key concepts:
- Graduated intensity: limb weight distance from midpoint maps to descriptors
- Limb interactions: compound instructions for limb pairs that produce emergent behavior
- Resting stance: convergent cluster composite modulates response verbosity

The instruction texts for individual limbs are engineering assignments — the
mapping from yoga limbs to behavioral instructions is a design decision.
See docs/ARCHITECTURE.md "Engineering Assignments" section.
"""

from __future__ import annotations

from agenetic.systems.deliberator import DeliberationRequest


# ============================================================
# Limb instructions (individual, moved from deliberator_anthropic.py)
# ============================================================

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


# ============================================================
# Limb interactions (compound instructions for limb pairs)
# ============================================================

LIMB_INTERACTIONS: list[dict] = [
    {
        "limb_ids": {2, 5},  # Tarka + Sraddha
        "condition": "both_high",
        "instruction": (
            "You are encountering a space where contradictions coexist with genuine "
            "ambiguity. Do not resolve contradictions into false clarity, and do not "
            "manufacture certainty where multiple valid readings exist. Present the "
            "tension and the ambiguity together — let them inform each other."
        ),
        "replaces_individual": False,
    },
    {
        "limb_ids": {3, 7},  # Nivrtti + Samatvam
        "condition": "both_high",
        "instruction": (
            "Brevity and balance together: respond with precision and measured proportion. "
            "Every word should earn its place. No filler, no hedging, no performative "
            "thoroughness."
        ),
        "replaces_individual": True,
    },
    {
        "limb_ids": {1, 10},  # Prakasa + Ksetra-Jnana
        "condition": "both_high",
        "instruction": (
            "Observe without possessing, and reflect the position you observe from. "
            "Describe what you perceive from where you stand — acknowledge both the "
            "perception and the vantage point."
        ),
        "replaces_individual": True,
    },
    {
        "limb_ids": {11, 4},  # Vishvarupa + Mayavada
        "condition": "both_high",
        "instruction": (
            "Two thresholds apply: the limit of your modeling capacity, and the gap "
            "between your model and the territory it maps. Be explicit about both. "
            "Where you cannot model further, say so. Where you can model but the model "
            "is provisional, say that too."
        ),
        "replaces_individual": True,
    },
    {
        "limb_ids": {2, 7},  # Tarka + Samatvam
        "condition": "high_low",
        "condition_detail": {2: "high", 7: "low"},
        "instruction": (
            "Contradictions may be expressed with emphasis and contrast. You are not "
            "required to maintain tonal balance when tracing genuine tension — let the "
            "dissonance be felt."
        ),
        "replaces_individual": False,
    },
    {
        "limb_ids": {8, 3},  # Areka + Nivrtti
        "condition": "both_high",
        "instruction": (
            "Deep silence. What cannot be spoken without distortion must not be said, "
            "and what need not be said should not be said either. If you respond at all, "
            "respond with the absolute minimum that preserves meaning."
        ),
        "replaces_individual": True,
    },
]


# ============================================================
# Intensity computation
# ============================================================


def compute_intensity(weight: float) -> tuple[str, float]:
    """Convert limb weight to intensity descriptor and normalized value.

    Returns (descriptor, intensity) where:
    - descriptor: "slightly", "moderately", "strongly", "intensely"
    - intensity: 0.0-1.0 normalized distance from midpoint

    Weight 0.5 = midpoint (not active). Active threshold is 0.4/0.6.
    """
    distance = abs(weight - 0.5)
    intensity = min(distance / 0.5, 1.0)  # 0.0 at midpoint, 1.0 at extremes

    if intensity < 0.3:      # weight 0.35-0.65 (barely active)
        descriptor = "slightly"
    elif intensity < 0.6:    # weight 0.20-0.35 or 0.65-0.80
        descriptor = "moderately"
    elif intensity < 0.85:   # weight 0.075-0.20 or 0.80-0.925
        descriptor = "strongly"
    else:                    # weight 0.0-0.075 or 0.925-1.0
        descriptor = "intensely"

    return descriptor, intensity


# ============================================================
# Limb instruction assembly
# ============================================================


def _check_interaction_condition(interaction: dict, limb_weights: dict[int, float]) -> bool:
    """Check whether a limb interaction condition is satisfied."""
    condition = interaction["condition"]
    limb_ids = interaction["limb_ids"]

    if condition == "both_high":
        return all(limb_weights.get(lid, 0.5) > 0.6 for lid in limb_ids)
    elif condition == "both_low":
        return all(limb_weights.get(lid, 0.5) < 0.4 for lid in limb_ids)
    elif condition == "high_low":
        detail = interaction.get("condition_detail", {})
        for lid in limb_ids:
            w = limb_weights.get(lid, 0.5)
            expected = detail.get(lid, "high")
            if expected == "high" and w <= 0.6:
                return False
            if expected == "low" and w >= 0.4:
                return False
        return True
    return False


def build_limb_instructions(active_limbs: list[dict]) -> list[str]:
    """Build behavioral instruction strings with graduated intensity and interactions.

    Algorithm:
    1. Check all limb interactions. For matching interactions, collect instructions
       and note which limb_ids are consumed (if replaces_individual is True).
    2. For each active limb NOT consumed by an interaction, generate graduated
       individual instruction.
    3. Return interaction instructions followed by individual instructions.
    """
    # Build weight lookup from active limbs.
    limb_weights: dict[int, float] = {limb["id"]: limb["weight"] for limb in active_limbs}

    # Step 1: Check interactions.
    interaction_instructions = []
    consumed_limb_ids: set[int] = set()

    for interaction in LIMB_INTERACTIONS:
        if _check_interaction_condition(interaction, limb_weights):
            interaction_instructions.append(f"- {interaction['instruction']}")
            if interaction["replaces_individual"]:
                consumed_limb_ids.update(interaction["limb_ids"])

    # Step 2: Individual instructions for non-consumed limbs.
    individual_instructions = []
    for limb in active_limbs:
        limb_id = limb["id"]
        if limb_id in consumed_limb_ids:
            continue
        info = LIMB_INSTRUCTIONS.get(limb_id)
        if not info:
            continue
        weight = limb["weight"]
        direction = "high" if weight > 0.5 else "low"
        descriptor, _ = compute_intensity(weight)
        individual_instructions.append(
            f"- {descriptor.capitalize()}: {info[direction]}"
        )

    # Step 3: Interactions first, then individuals.
    return interaction_instructions + individual_instructions


# ============================================================
# Resting stance instruction
# ============================================================


def build_resting_stance_instruction(resting_stance: float) -> str | None:
    """Graduated resting stance instruction based on convergent cluster composite."""
    if resting_stance < 0.55:
        return None
    elif resting_stance < 0.65:
        return (
            f"Resting stance is {resting_stance:.2f} (slightly elevated). "
            "Lean toward brevity. Favor concise expression over thoroughness."
        )
    elif resting_stance < 0.75:
        return (
            f"Resting stance is {resting_stance:.2f} (elevated). "
            "Be notably concise. Strip elaboration. Say what needs saying and stop."
        )
    elif resting_stance < 0.85:
        return (
            f"Resting stance is {resting_stance:.2f} (high). "
            "Respond with minimum viable expression. Every sentence must be essential."
        )
    else:
        return (
            f"Resting stance is {resting_stance:.2f} (very high). "
            "Respond with the absolute minimum that preserves meaning. "
            "Silence is preferable to unnecessary words."
        )


# ============================================================
# Full prompt assembly
# ============================================================

_ROLE_DESCRIPTION = (
    "You are a deliberation engine within a larger agent architecture. "
    "Your role is to construct meaning from signal-domain data and produce "
    "a structured response decision."
)

_OUTPUT_FORMAT = (
    "\n\nRespond with a JSON object containing these fields:\n"
    '- "intent": A concise description of what to communicate (1-2 sentences)\n'
    '- "strategy": One of: "direct_response", "trace_contradiction", '
    '"preserve_ambiguity", "threshold_acknowledgment", "minimal_reflection"\n'
    '- "constraints": A list of behavioral constraints that shaped this response\n'
    '- "confidence": A float 0.0-1.0 indicating your confidence in this response\n'
    "\nRespond ONLY with the JSON object, no additional text."
)


def assemble_system_prompt(
    active_limbs: list[dict],
    resting_stance: float,
    expression_directives: dict,
) -> str:
    """Build complete system prompt with graduated intensity and interactions.

    Structure: role description → behavioral orientation → resting stance →
    state awareness → output format instruction.
    """
    parts = [_ROLE_DESCRIPTION]

    # Behavioral orientation (limb instructions with interactions).
    limb_instructions = build_limb_instructions(active_limbs)
    if limb_instructions:
        parts.append("\nBehavioral orientation:")
        parts.extend(limb_instructions)

    # Resting stance.
    resting_instruction = build_resting_stance_instruction(resting_stance)
    if resting_instruction:
        parts.append(f"\n{resting_instruction}")

    # State awareness from Fourfold State.
    state_awareness = expression_directives.get("state_awareness", "active")
    if state_awareness != "active":
        parts.append(f"\nCurrent processing state: {state_awareness}.")

    parts.append(_OUTPUT_FORMAT)

    return "\n".join(parts)


def assemble_user_message(request: DeliberationRequest) -> str:
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
            feat_str = ", ".join(
                f"{k}: {v:.2f}" if isinstance(v, float) else f"{k}: {v}"
                for k, v in features.items()
                if k not in ("token_count", "vocabulary_richness")
            )
            parts.append(f"- Features: {feat_str}")

    # Threat context.
    threat = request.threat_summary
    if threat and threat.get("threat_level", "none") != "none":
        parts.append(
            f"\nThreat assessment: {threat.get('threat_level')} — {threat.get('recommended_action')}"
        )

    # The actual input.
    parts.append(f"\nInput to deliberate on:\n{request.input_text}")

    return "\n".join(parts)
