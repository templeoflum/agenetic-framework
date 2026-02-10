# Directive 012 Response — Prompt Assembly Refinement

**Agent:** DNAgent (Claude Code CLI)
**Date:** 2026-02-10
**Status:** Complete
**Tests:** 292 passing + 2 skipped (was 262, +24 prompt assembly + 6 observation)

---

## Summary

Extracted prompt assembly into a dedicated module, implemented graduated intensity scaling and limb interaction composition, and built an observation harness for the semantic-domain audit. The conscious layer's prompt construction now produces structurally different prompts for different limb weights — verified deterministically.

No modifications to conscious.py, deliberator.py, base.py, graph.py, or any signal-domain systems. No historical handoff files edited. No graph routing changes.

## Part-by-Part Report

### Part A: Prompt Assembly Module — DONE

Created `src/agenetic/systems/prompt_assembly.py` (~380 LOC):

**LIMB_INSTRUCTIONS** — moved from `deliberator_anthropic.py`. Same 13 entries (limbs 1–11, 13, 16), unchanged content.

**LIMB_INTERACTIONS** — 6 interaction entries:
| Pair | Condition | Replaces individual? |
|---|---|---|
| Tarka + Sraddha (2, 5) | both_high | No |
| Nivrtti + Samatvam (3, 7) | both_high | Yes |
| Prakasa + Ksetra-Jnana (1, 10) | both_high | Yes |
| Vishvarupa + Mayavada (11, 4) | both_high | Yes |
| Tarka + Samatvam (2, 7) | high_low | No |
| Areka + Nivrtti (8, 3) | both_high | Yes |

**`compute_intensity(weight)`** — maps distance from 0.5 midpoint to four descriptors:
- slightly (intensity < 0.3)
- moderately (0.3–0.6)
- strongly (0.6–0.85)
- intensely (>= 0.85)

**`_check_interaction_condition()`** — supports both_high, both_low, high_low conditions.

**`build_limb_instructions(active_limbs)`** — interaction-aware graduated assembly:
1. Check all interactions, collect matching compound instructions
2. Track consumed limb IDs (replaces_individual=True)
3. Generate graduated individual instructions for unconsumed limbs
4. Return interactions first, then individuals

**`build_resting_stance_instruction(resting_stance)`** — 5 graduated levels:
- < 0.55: None (no instruction)
- 0.55–0.65: "slightly elevated" — lean toward brevity
- 0.65–0.75: "elevated" — be notably concise
- 0.75–0.85: "high" — minimum viable expression
- >= 0.85: "very high" — absolute minimum

**`assemble_system_prompt()`** — role + behavioral orientation + resting stance + state awareness + output format.

**`assemble_user_message()`** — moved from deliberator_anthropic.py, unchanged logic.

### Part A2: Refactor deliberator_anthropic.py — DONE

Removed from `deliberator_anthropic.py`:
- `LIMB_INSTRUCTIONS` dict (67 lines)
- `_build_system_prompt()` function (49 lines)
- `_build_user_message()` function (26 lines)

Added import: `from agenetic.systems.prompt_assembly import assemble_system_prompt, assemble_user_message`

Updated `AnthropicDeliberator.deliberate()` to call imported functions.

Retained: `_parse_response()` (backend-specific), `AnthropicDeliberator` class. File went from ~250 LOC to ~100 LOC.

### Part B: Tests — DONE

Created `tests/test_prompt_assembly.py` with 24 tests:

**Intensity (4):** midpoint (0.5→slightly), moderate (0.7→moderately), strong (0.85→strongly), extreme (0.98→intensely).

**Individual instructions (4):** Tarka high at 0.8 (Strongly:), Tarka low at 0.2 (Strongly:), Prakasa barely active at 0.62 (Slightly:), empty active list (no instructions).

**Interactions (6):** both_high matches, both_high doesn't match when one low, replaces_individual=True removes individuals, replaces_individual=False keeps individuals, two interactions simultaneously, high_low condition.

**Resting stance (5):** below threshold (None), slightly elevated (0.6), elevated (0.7), high (0.8), very high (0.9).

**Full assembly (3):** includes role description, includes output format, no active limbs → no behavioral section.

**Regression (2):** deliberator_anthropic imports from prompt_assembly (not hardcoded), deterministic (same inputs → same output).

### Part C: Observation Harness — DONE

Added `TestPromptObservations` class to `test_conscious.py` with 6 deterministic tests:

1. **test_observe_tarka_high_vs_low_prompt_diff** — Tarka 0.9 vs 0.1 produce structurally different prompts
2. **test_observe_interaction_vs_individual_prompt_diff** — interaction adds content not in individual-only prompt
3. **test_observe_intensity_gradient** — 4 weights (0.62, 0.75, 0.85, 0.95) produce 4 distinct prompts
4. **test_observe_resting_stance_gradient** — 5 stance levels produce 5 distinct prompts
5. **test_observe_all_limbs_high_prompt_length** — all 13 limbs at 0.9 → prompt < 3000 chars
6. **test_observe_all_limbs_low_prompt_length** — all 13 limbs at 0.1 → prompt < 3000 chars

Added `TestPromptObservationsAPI` class with 1 API-optional test (skipped without ANTHROPIC_API_KEY):
7. **test_observe_api_tarka_high_vs_low** — records LLM responses for manual review, does not assert behavior

### Parts D+E: Documentation and Planning — DONE

- `handoff/state.md` → `planning/012_prompt_assembly.md` (permanent numbered entry)
- `planning/CURRENT.md` rebuilt from repo inspection
- `DEVLOG.md`: Directive 012 entry with graduated intensity, interactions, observation harness
- `README.md`: Conscious system description updated, test count 262→292

## Verification Checklist

- [x] `src/agenetic/systems/prompt_assembly.py` exists with all specified functions
- [x] `LIMB_INSTRUCTIONS` moved from `deliberator_anthropic.py` to `prompt_assembly.py` (13 entries, unchanged content)
- [x] `LIMB_INTERACTIONS` defined with 6 interaction entries
- [x] `compute_intensity()` returns graduated descriptors ("slightly", "moderately", "strongly", "intensely")
- [x] `build_limb_instructions()` applies interactions before individual instructions
- [x] `build_limb_instructions()` respects `replaces_individual` flag
- [x] `build_resting_stance_instruction()` returns graduated instructions at 5 levels
- [x] `assemble_system_prompt()` produces complete prompt with role + limb instructions + resting stance + output format
- [x] `assemble_user_message()` produces same output as previous `_build_user_message()`
- [x] `deliberator_anthropic.py` imports from `prompt_assembly` (no hardcoded LIMB_INSTRUCTIONS)
- [x] `_parse_response()` remains in `deliberator_anthropic.py` (unchanged)
- [x] `AnthropicDeliberator.deliberate()` external behavior preserved
- [x] All 24 prompt assembly tests pass (intensity, individual, interaction, resting stance, full assembly, regression)
- [x] All 6 deterministic observation tests pass
- [x] Optional API observation test exists (skipped without credentials)
- [x] All 262 existing tests still pass (including all 011 conscious tests)
- [x] No modifications to conscious.py
- [x] No modifications to deliberator.py (protocol)
- [x] No modifications to base.py, graph.py
- [x] No modifications to sensory.py, immune.py, subconscious.py, or motor.py
- [x] No modifications to orientational field
- [x] No historical handoff files edited
- [x] `handoff/state.md` copied to `planning/012_prompt_assembly.md`
- [x] `planning/CURRENT.md` rebuilt from actual repo inspection
- [x] DEVLOG.md entry added
- [x] README.md updated
- [x] Git commit and push completed (e0975b6)

## Files Changed

| File | Action |
|------|--------|
| `src/agenetic/systems/prompt_assembly.py` | Created — extracted and extended prompt logic (~380 LOC) |
| `src/agenetic/systems/deliberator_anthropic.py` | Updated — imports from prompt_assembly, reduced from ~250 to ~100 LOC |
| `tests/test_prompt_assembly.py` | Created — 24 deterministic prompt structure tests |
| `tests/test_conscious.py` | Updated — 7 observation tests added (TestPromptObservations + TestPromptObservationsAPI) |
| `planning/012_prompt_assembly.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `DEVLOG.md` | Updated — Directive 012 entry |
| `README.md` | Updated — conscious system description, test count |
| `handoff/012_response.md` | This file |
