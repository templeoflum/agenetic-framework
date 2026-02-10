# Directive 012 — Prompt Assembly Refinement: Graduated Expression, Limb Interactions, Observation Harness

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-10

## Context

Read these files first, in this order:
1. `planning/CURRENT.md` — factual snapshot of where things stand
2. `CLAUDE.md` — project conventions, agent roles, directive protocol
3. `docs/ARCHITECTURE.md` — the v2 specification (especially Calibration Validity and Engineering Assignments sections)
4. `docs/architecture_amendment.md` — the signal-semantics boundary
5. `references/asparsa_limbs.md` — the 18 limb principles
6. `references/conceptual_archaeology.md` — Section V, limb-to-feature mapping (Signal vs Semantic domain assignments)
7. `src/agenetic/systems/deliberator_anthropic.py` — the current prompt assembly logic (what this directive refines)
8. `src/agenetic/systems/conscious.py` — the conscious system that calls the Deliberator
9. `planning/011_conscious_foundation.md` — design decisions from the previous directive

**What happened before this directive:**

Directive 011 built the conscious layer foundation: `ConsciousOutput` contract, proceed/suppress gate, `Deliberator` protocol, and the first Anthropic API-backed deliberator. 262 tests passing (238 existing + 24 conscious). The conscious layer crosses from signal to semantic domain — it's the first and only system that constructs meaning.

The Anthropic deliberator (`deliberator_anthropic.py`) already has working prompt assembly:
- 13 limb instruction pairs (high/low) for limbs 1–11, 13, 16 (everything except the convergent cluster which expresses through resting stance composite)
- `_build_system_prompt()` concatenates active limb instructions, adds resting stance instruction, includes Fourfold State awareness
- `_build_user_message()` presents signal summary + input text
- JSON structured output request with parse fallback at confidence 0.3

This works but has three limitations this directive addresses:

1. **Binary expression.** Each limb gets either its "high" or "low" instruction. A limb at weight 0.65 produces the same instruction as one at 0.95. Real behavioral modulation requires graduated intensity.

2. **Independent concatenation.** Limb instructions are listed independently. But limbs interact — Tarka-high + Śraddhā-high together produce a specific intellectual posture (hold contradictions open AND preserve ambiguity) that's different from the sum of parts. The prompt should compose interactions, not just list individuals.

3. **No observation infrastructure.** The critical question for the semantic-domain audit (Directive 016) is: "does the LLM actually behave differently when limb weights change, or is the prompt assembly theater?" We need a harness that generates prompts under controlled limb configurations and records observations for later evaluation. Without this, the audit has nothing to evaluate against.

**What this directive does NOT do:**
- Does NOT modify the conscious system (`conscious.py`) — the process flow, gate logic, and Deliberator calling convention are unchanged
- Does NOT modify the Deliberator protocol (`deliberator.py`) — the interface contract is unchanged
- Does NOT modify motor, sensory, immune, subconscious, or the orientational field
- Does NOT change graph routing

This directive modifies ONLY:
- `deliberator_anthropic.py` — refactored prompt assembly
- A new `prompt_assembly.py` module — extracted and extended prompt logic
- New tests in `test_prompt_assembly.py` — deterministic prompt structure tests
- New observation tests in `test_conscious.py` — behavioral observation harness (recording, not asserting)

## Objective

Extract prompt assembly into its own module, implement graduated intensity scaling and limb interaction composition, and build an observation harness that records prompt-level behavioral differences for the semantic-domain audit. All existing tests must pass unchanged. The Anthropic deliberator's external behavior is preserved — only its internal prompt construction improves.

## Part A: Extract Prompt Assembly Module

### A1: Create `src/agenetic/systems/prompt_assembly.py`

Extract prompt construction logic from `deliberator_anthropic.py` into a dedicated module. This module is the conscious layer's "what the LLM sees" — any Deliberator implementation can import and use it, or override it entirely.

The module should contain:

1. **`LIMB_INSTRUCTIONS`** — moved from `deliberator_anthropic.py`. Same 13 limb entries (limbs 1–11, 13, 16), each with `name`, `high`, and `low` instruction text. These instruction texts remain unchanged from Directive 011.

2. **`LIMB_INTERACTIONS`** — new. A dict of interaction pairs/groups that produce compound behavioral instructions when multiple limbs are simultaneously active. Structure:

```python
LIMB_INTERACTIONS: list[dict] = [
    {
        "limb_ids": {2, 5},  # Tarka + Śraddhā
        "condition": "both_high",  # Both weights > 0.6
        "instruction": (
            "You are encountering a space where contradictions coexist with genuine "
            "ambiguity. Do not resolve contradictions into false clarity, and do not "
            "manufacture certainty where multiple valid readings exist. Present the "
            "tension and the ambiguity together — let them inform each other."
        ),
        "replaces_individual": False,  # Compound adds to, not replaces, individual instructions
    },
    {
        "limb_ids": {3, 7},  # Nivṛtti + Samatvam
        "condition": "both_high",
        "instruction": (
            "Brevity and balance together: respond with precision and measured proportion. "
            "Every word should earn its place. No filler, no hedging, no performative "
            "thoroughness."
        ),
        "replaces_individual": True,  # Compound replaces individual Nivṛtti and Samatvam instructions
    },
    {
        "limb_ids": {1, 10},  # Prakāśa + Kṣetra-Jñāna
        "condition": "both_high",
        "instruction": (
            "Observe without possessing, and reflect the position you observe from. "
            "Describe what you perceive from where you stand — acknowledge both the "
            "perception and the vantage point."
        ),
        "replaces_individual": True,
    },
    {
        "limb_ids": {11, 4},  # Vishvarūpa + Māyāvāda
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
        "condition": "high_low",  # Tarka high, Samatvam low
        "condition_detail": {2: "high", 7: "low"},
        "instruction": (
            "Contradictions may be expressed with emphasis and contrast. You are not "
            "required to maintain tonal balance when tracing genuine tension — let the "
            "dissonance be felt."
        ),
        "replaces_individual": False,
    },
    {
        "limb_ids": {8, 3},  # Ārēka + Nivṛtti
        "condition": "both_high",
        "instruction": (
            "Deep silence. What cannot be spoken without distortion must not be said, "
            "and what need not be said should not be said either. If you respond at all, "
            "respond with the absolute minimum that preserves meaning."
        ),
        "replaces_individual": True,
    },
]
```

The interaction list is intentionally small (6 entries). These are the combinations where the compound instruction is genuinely different from the sum of individual instructions. Other combinations (e.g., Svadharma + Kṣetra-Jñāna) are adequately served by concatenating their individual instructions.

**Interaction matching rules:**
- An interaction matches when ALL limb_ids in the entry have weights that satisfy the condition
- `"both_high"` means all listed limbs have weight > 0.6
- `"both_low"` means all listed limbs have weight < 0.4
- `"high_low"` uses `condition_detail` to specify which limb is high vs low
- When `replaces_individual` is True, the matched interaction REPLACES the individual instructions for those limbs (avoids redundancy). When False, the interaction instruction is ADDED alongside the individuals.
- Multiple interactions can match simultaneously. They are all included.

3. **`compute_intensity(weight: float) -> tuple[str, float]`** — new. Converts a limb weight to an intensity descriptor and normalized intensity value:

```python
def compute_intensity(weight: float) -> tuple[str, float]:
    """Convert limb weight to intensity descriptor and normalized value.
    
    Returns (descriptor, intensity) where:
    - descriptor: "slightly", "moderately", "strongly", "intensely"
    - intensity: 0.0–1.0 normalized distance from midpoint
    
    Weight 0.5 = midpoint (not active). Active threshold is 0.4/0.6.
    """
    distance = abs(weight - 0.5)
    intensity = min(distance / 0.5, 1.0)  # 0.0 at midpoint, 1.0 at extremes
    
    if intensity < 0.3:    # weight 0.35–0.65 (barely active)
        descriptor = "slightly"
    elif intensity < 0.6:  # weight 0.20–0.35 or 0.65–0.80
        descriptor = "moderately"
    elif intensity < 0.85: # weight 0.075–0.20 or 0.80–0.925
        descriptor = "strongly"
    else:                  # weight 0.0–0.075 or 0.925–1.0
        descriptor = "intensely"
    
    return descriptor, intensity
```

4. **`build_limb_instructions(active_limbs: list[dict]) -> list[str]`** — new. The core prompt assembly function. Takes the active limbs list (each with `id`, `name`, `weight`) and returns a list of behavioral instruction strings, with graduated intensity and interaction composition applied.

Algorithm:
1. Check all limb interactions. For each matching interaction, collect its instruction and note which limb_ids are "consumed" (if `replaces_individual` is True).
2. For each active limb NOT consumed by an interaction, generate its graduated individual instruction:
   - Look up the limb in `LIMB_INSTRUCTIONS`
   - Determine direction: "high" if weight > 0.5, "low" if weight < 0.5
   - Compute intensity via `compute_intensity(weight)`
   - Prepend the intensity descriptor to the instruction: e.g., `"Moderately: When you encounter contradictions, trace them..."`
3. Return interaction instructions followed by individual instructions.

5. **`build_resting_stance_instruction(resting_stance: float) -> str | None`** — new. Graduated resting stance expression:

```python
def build_resting_stance_instruction(resting_stance: float) -> str | None:
    """Graduated resting stance instruction based on convergent cluster composite."""
    if resting_stance < 0.55:
        return None  # Not elevated enough to warrant instruction
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
```

6. **`assemble_system_prompt(active_limbs: list[dict], resting_stance: float, expression_directives: dict) -> str`** — refactored version of the current `_build_system_prompt()`. Uses the above functions to build the complete system prompt. Keeps the same overall structure (role description → behavioral orientation → resting stance → state awareness → output format instruction) but with graduated, interaction-aware content.

7. **`assemble_user_message(request) -> str`** — moved from `_build_user_message()` in `deliberator_anthropic.py`. No changes to logic.

### A2: Refactor `deliberator_anthropic.py`

Remove the following from `deliberator_anthropic.py`:
- `LIMB_INSTRUCTIONS` dict
- `_build_system_prompt()` function
- `_build_user_message()` function

Replace with imports from `prompt_assembly.py`:

```python
from agenetic.systems.prompt_assembly import (
    assemble_system_prompt,
    assemble_user_message,
)
```

`AnthropicDeliberator.deliberate()` now calls:
```python
system_prompt = assemble_system_prompt(
    active_limbs=request.active_limbs,
    resting_stance=request.resting_stance,
    expression_directives=request.expression_directives,
)
user_message = assemble_user_message(request)
```

Keep `_parse_response()` in `deliberator_anthropic.py` — response parsing is backend-specific (different LLMs may need different parsing strategies).

The external interface of `AnthropicDeliberator` is unchanged. Only internal prompt construction changes.

## Part B: Tests — Deterministic Prompt Structure

### B1: Create `tests/test_prompt_assembly.py`

All tests in this file are deterministic — no LLM calls, no API keys. They test that prompt assembly produces expected structural outputs for given inputs.

**Intensity tests (4):**

1. **test_intensity_midpoint**: Weight 0.5 → intensity 0.0, descriptor "slightly"
2. **test_intensity_moderate**: Weight 0.7 → intensity 0.4, descriptor "moderately"
3. **test_intensity_strong**: Weight 0.85 → intensity 0.7, descriptor "strongly"
4. **test_intensity_extreme**: Weight 0.98 → intensity 0.96, descriptor "intensely"

**Individual instruction tests (4):**

5. **test_individual_instruction_high**: Tarka at weight 0.8 (no interactions active). Output should contain Tarka's high instruction with "Strongly:" prefix.
6. **test_individual_instruction_low**: Tarka at weight 0.2. Output should contain Tarka's low instruction with "Strongly:" prefix (same intensity, opposite direction).
7. **test_individual_instruction_barely_active**: Prakāśa at weight 0.62. Output should contain Prakāśa's high instruction with "Slightly:" prefix.
8. **test_inactive_limb_excluded**: Limb at weight 0.5 (midpoint). Should produce no instruction.

**Interaction tests (6):**

9. **test_interaction_both_high_matches**: Tarka at 0.8 + Śraddhā at 0.75. Both high → Tarka+Śraddhā interaction instruction should be present.
10. **test_interaction_both_high_no_match_when_one_low**: Tarka at 0.8 + Śraddhā at 0.3. Only Tarka high → interaction should NOT match.
11. **test_interaction_replaces_individual**: Nivṛtti at 0.8 + Samatvam at 0.75. Interaction `replaces_individual=True` → individual Nivṛtti and Samatvam instructions should NOT be present, only the compound.
12. **test_interaction_adds_to_individual**: Tarka at 0.8 + Śraddhā at 0.75. Interaction `replaces_individual=False` → both individual instructions AND the compound instruction should be present.
13. **test_multiple_interactions_simultaneously**: Craft a limb config where two interactions match. Both compound instructions should appear.
14. **test_high_low_interaction**: Tarka at 0.8 + Samatvam at 0.3 (Tarka high, Samatvam low). The `high_low` interaction should match.

**Resting stance tests (5):**

15. **test_resting_stance_below_threshold**: Composite 0.5 → no instruction (returns None).
16. **test_resting_stance_slightly_elevated**: Composite 0.6 → instruction contains "slightly elevated" and "brevity".
17. **test_resting_stance_elevated**: Composite 0.7 → instruction contains "elevated" and "concise".
18. **test_resting_stance_high**: Composite 0.8 → instruction contains "high" and "minimum viable".
19. **test_resting_stance_very_high**: Composite 0.9 → instruction contains "very high" and "absolute minimum".

**Full prompt assembly tests (3):**

20. **test_assemble_system_prompt_includes_role**: Any limb config → prompt starts with role description ("You are a deliberation engine...").
21. **test_assemble_system_prompt_includes_output_format**: Any limb config → prompt ends with JSON output format instruction.
22. **test_assemble_system_prompt_no_active_limbs**: All limbs at 0.5 → prompt has role + output format, no behavioral instructions section.

**Regression tests (2):**

23. **test_anthropic_deliberator_uses_prompt_assembly**: Verify `AnthropicDeliberator` imports from `prompt_assembly` (not hardcoded instructions). This is a structural check, not a behavioral test.
24. **test_prompt_assembly_deterministic**: Same inputs twice → same prompt output. Verifies no randomness in assembly.

### B2: Total new test count

24 new tests in `test_prompt_assembly.py`.

## Part C: Observation Harness

### C1: Add observation tests to `tests/test_conscious.py`

These tests are NOT assertions about LLM behavior. They are **recording infrastructure** for the semantic-domain audit (Directive 016). They generate prompts under controlled conditions and record structural observations about how prompt content varies.

Add a new test class `TestPromptObservations` in `test_conscious.py`.

**Observation tests (6):**

25. **test_observe_tarka_high_vs_low_prompt_diff**: 
    - Build two `DeliberationRequest`s: one with Tarka at 0.9, one at 0.1. All other limbs at 0.5.
    - Call `assemble_system_prompt()` for each.
    - Record the diff: which instruction lines differ, what intensity descriptors are used.
    - Assert: the two prompts are NOT identical (they must differ structurally). This is a minimal sanity check — if the prompts are identical for opposite weights, assembly is broken.

26. **test_observe_interaction_vs_individual_prompt_diff**:
    - Build two requests: one with Tarka=0.8 + Śraddhā=0.8 (interaction active), one with Tarka=0.8 + Śraddhā=0.5 (no interaction).
    - Call `assemble_system_prompt()` for each.
    - Assert: the interaction prompt contains content not present in the individual-only prompt.

27. **test_observe_intensity_gradient**:
    - Build requests with Tarka at 0.65, 0.75, 0.85, 0.95. All others at 0.5.
    - Call `assemble_system_prompt()` for each.
    - Assert: the four prompts are all different from each other.
    - Record: the instruction text for each intensity level.

28. **test_observe_resting_stance_gradient**:
    - Build requests with convergent cluster weights all at 0.55, 0.65, 0.75, 0.85, 0.95.
    - Call `assemble_system_prompt()` for each.
    - Assert: prompts at 0.55 and 0.95 differ.
    - Record: the resting stance instruction at each level.

29. **test_observe_all_limbs_high_prompt_length**:
    - Build request with ALL 13 individually-instructed limbs at 0.9.
    - Call `assemble_system_prompt()`.
    - Record: total prompt length, number of instruction lines, number of interaction instructions.
    - Assert: prompt length is reasonable (< 3000 chars — the system prompt shouldn't be a novel).

30. **test_observe_all_limbs_low_prompt_length**:
    - Same but all limbs at 0.1.
    - Record same metrics.
    - Assert: prompt length is reasonable.

These observation tests produce output that the conceptual audit (016) will evaluate. The observations are about prompt structure, not LLM behavior — LLM behavioral observation is deferred to when the audit actually runs the API deliberator.

### C2: Optional API observation (skipped without credentials)

31. **test_observe_api_tarka_high_vs_low** (skipped without ANTHROPIC_API_KEY):
    - Call `AnthropicDeliberator.deliberate()` with Tarka at 0.9 and then at 0.1.
    - Record both responses.
    - Do NOT assert behavioral differences — just record.
    - Print or log the observations for manual review.
    - This test is for development-time observation, not CI.

## Part D: Planning State Management

### D1: Copy State to Planning Entry

Copy `handoff/state.md` to `planning/012_prompt_assembly.md`.
This is the permanent numbered planning entry for this directive cycle.
Never overwrite previous planning entries.

### D2: Update CURRENT.md from Repo Inspection

After all code changes are complete and tests pass, update `planning/CURRENT.md` by inspecting the actual repo state. Rebuild from ground truth — do NOT copy from old CURRENT.md.

## Part E: Documentation Updates

### E1: DEVLOG Entry

Add entry for Directive 012. Format: date, directive number, commit hash (fill in), test count (fill in), prose summary of what was built: prompt assembly extraction, graduated intensity, limb interactions, observation harness.

### E2: README Status Update

Update README.md: Conscious system description should add "graduated prompt assembly" or similar. Update test count.

## Scope Boundaries

**DO:**
- Create `src/agenetic/systems/prompt_assembly.py` with extracted and extended prompt logic
- Refactor `deliberator_anthropic.py` to import from `prompt_assembly.py`
- Implement graduated intensity scaling (`compute_intensity`)
- Implement limb interaction composition (`LIMB_INTERACTIONS`, `build_limb_instructions`)
- Implement graduated resting stance instruction
- Create `tests/test_prompt_assembly.py` with 24 deterministic tests
- Add 7 observation tests (6 deterministic + 1 API-optional) to `tests/test_conscious.py`
- Update DEVLOG.md, README.md, CURRENT.md
- Copy state.md to planning entry

**DO NOT:**
- Modify `conscious.py` (the conscious system's process flow is unchanged)
- Modify `deliberator.py` (the Deliberator protocol is unchanged)
- Modify `base.py` (no type changes)
- Modify `graph.py` (no routing changes)
- Modify sensory.py, immune.py, subconscious.py, or motor.py
- Modify the orientational field
- Change the `_parse_response()` function in `deliberator_anthropic.py` (response parsing is unchanged)
- Change the JSON output format requested from the LLM
- Change the `DeliberationRequest` structure
- Edit any historical handoff files (001–011)
- Modify connection weights or topology

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/prompt_assembly.py` | Created — extracted and extended prompt logic |
| `src/agenetic/systems/deliberator_anthropic.py` | Updated — imports from prompt_assembly, LIMB_INSTRUCTIONS and build functions removed |
| `tests/test_prompt_assembly.py` | Created — 24 deterministic prompt structure tests |
| `tests/test_conscious.py` | Updated — 7 observation tests added (TestPromptObservations class) |
| `handoff/state.md` | Provided — planning notes for this cycle |
| `planning/012_prompt_assembly.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `DEVLOG.md` | Updated — Directive 012 entry |
| `README.md` | Updated — conscious system description, test count |
| `handoff/012_directive.md` | This file |
| `handoff/012_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `src/agenetic/systems/prompt_assembly.py` exists with all specified functions
- [ ] `LIMB_INSTRUCTIONS` moved from `deliberator_anthropic.py` to `prompt_assembly.py` (13 entries, unchanged content)
- [ ] `LIMB_INTERACTIONS` defined with 6 interaction entries
- [ ] `compute_intensity()` returns graduated descriptors ("slightly", "moderately", "strongly", "intensely")
- [ ] `build_limb_instructions()` applies interactions before individual instructions
- [ ] `build_limb_instructions()` respects `replaces_individual` flag
- [ ] `build_resting_stance_instruction()` returns graduated instructions at 5 levels
- [ ] `assemble_system_prompt()` produces complete prompt with role + limb instructions + resting stance + output format
- [ ] `assemble_user_message()` produces same output as previous `_build_user_message()`
- [ ] `deliberator_anthropic.py` imports from `prompt_assembly` (no hardcoded LIMB_INSTRUCTIONS)
- [ ] `_parse_response()` remains in `deliberator_anthropic.py` (unchanged)
- [ ] `AnthropicDeliberator.deliberate()` external behavior preserved
- [ ] All 24 prompt assembly tests pass (intensity, individual, interaction, resting stance, full assembly, regression)
- [ ] All 6 deterministic observation tests pass
- [ ] Optional API observation test exists (skipped without credentials)
- [ ] All 262 existing tests still pass (including all 011 conscious tests)
- [ ] No modifications to conscious.py
- [ ] No modifications to deliberator.py (protocol)
- [ ] No modifications to base.py, graph.py
- [ ] No modifications to sensory.py, immune.py, subconscious.py, or motor.py
- [ ] No modifications to orientational field
- [ ] No historical handoff files edited
- [ ] `handoff/state.md` copied to `planning/012_prompt_assembly.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection
- [ ] DEVLOG.md entry added
- [ ] README.md updated
- [ ] Git commit and push completed
