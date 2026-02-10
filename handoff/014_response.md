# Directive 014 Response — Integration: Conditional Escalation, Conscious-Motor Wiring

**Status:** Complete
**Tests:** 320 passing + 2 skipped (was 304, +16 integration tests)
**Commit:** a2d7203

## What Was Done

### Part A — Conditional Escalation

Changed `escalate_to_conscious` default from `True` to `False` in `create_default_state()`. One line. Activates subconscious-driven routing that was already built into the graph.

### Part B — Motor-Conscious Integration

Added to `motor.py`:
1. **Conscious suppression check** — before codec delegation, motor checks `state["conscious_output"]`. If `proceed=False`, returns empty output with `strategies_applied=["conscious_suppression"]`, `repair_passed=True`.
2. **Conscious strategy recording** — when conscious proceeds, motor records `motor_output["conscious_strategy"]` from `conscious_output["decision"]["strategy"]`. Informational metadata only.

Two suppression paths now coexist:
- Conscious suppression: fires before codec (this directive)
- Areka suppression: fires inside codec (existing from D007/D013)
If conscious suppresses, Areka never checks. If conscious proceeds, Areka might still suppress independently.

### Part C — Subconscious Explicit Flag Reset

Added explicit `flags["escalate_to_conscious"] = False` in the else branch of escalation decision. Defense-in-depth against stale flags from previous graph invocations.

**Design note:** This change interacts with Part A. Tests that manually set `escalate_to_conscious=True` in state setup get overridden by subconscious. The fix for broken tests is to use inputs that naturally trigger escalation (high deviation or threat), not manual flag setting. See Issues section below.

### Part D — Tests

**16 new integration tests** in `tests/test_integration.py`:

| Group | Tests | What |
|-------|-------|------|
| Reflex | 4 | Low-deviation input → conscious skipped, motor processes directly, all signal-domain outputs populated |
| Escalated | 4 | High-deviation input → conscious fires, motor records strategy, MockDeliberator used |
| Suppression | 3 | High Areka + noise → conscious gate suppresses, motor empty, deliberator call_count=0 |
| Routing | 3 | Default is reflex, medium threat escalates, cached reflex patterns stay reflex |
| Cross-path | 2 | Motor output always exists, signal report structure preserved on both paths |

**Input selection:**
- `REFLEX_INPUT = "The quick brown fox jumps over the lazy dog."` — aggregate_deviation ~0.73 (< 1.5), stays reflex
- `ESCALATION_INPUT = "test"` — aggregate_deviation ~3.57 (> 1.5), novel signal escalates
- `NOISE_INPUT = "a ! b # c $ d % e ^ f & g * h ( i ) j + k = l ; m @ n ~ o"` — classified "noise", aggregate_deviation ~1.75, with Areka=0.9 triggers gate suppression
- `THREAT_INPUT = "x x x x x x x x x x x x x x x x x x x"` — immune scores medium threat, subconscious escalates on threat_level

**2 existing test fixes:**
- `test_systems.py::test_escalation_flag_never_unset` → renamed `test_escalation_flag_explicitly_reset`, assertion reversed (flag now explicitly reset to False)
- `test_conscious.py::test_graph_conscious_output_flows_to_motor` → changed input from "The quick brown fox..." (low deviation) to "test" (high deviation) so subconscious naturally escalates

## Issues Encountered and Resolved

1. **Part C overrides manual flag setting.** The directive suggested fixing broken tests by "explicitly set `escalate_to_conscious=True`." This doesn't work because subconscious (with Part C's explicit reset) overrides manual flag setting. Fix: used high-deviation inputs that naturally trigger escalation instead. This is actually more honest — tests declare what input triggers each path, not which internal flag to set.

2. **Finding inputs for each path.** Needed inputs that reliably trigger specific routing:
   - Reflex: "The quick brown fox..." has aggregate_deviation 0.73 (close to field reference at default weights)
   - Escalation: "test" has aggregate_deviation 3.57 (very short, far from reference)
   - Noise suppression: "a ! b # c $..." has noise_floor 1.0 AND aggregate_deviation 1.75 AND classified as "noise" (required for Areka gate)
   - Threat: "x x x x..." has noise_floor 1.0, aggregate_deviation 3.84, vocabulary_richness 0.05 → multiple immune thresholds → medium threat

## Verification

- [x] `create_default_state()` sets `escalate_to_conscious=False`
- [x] Subconscious sets `escalate_to_conscious=True` when `escalation_recommended=True`
- [x] Subconscious explicitly sets `escalate_to_conscious=False` when `escalation_recommended=False`
- [x] Motor checks `conscious_output` before codec delegation
- [x] Motor produces empty output with "conscious_suppression" when conscious proceed=False
- [x] Motor records `conscious_strategy` metadata when conscious proceed=True
- [x] Motor behavior unchanged when conscious_output is None (reflex path)
- [x] base.py is NOT modified
- [x] Reflex path works: low-deviation input → motor processes directly
- [x] Escalated path works: high-deviation input → conscious deliberates → motor processes
- [x] Suppression path works: Areka + noise → conscious suppresses → motor empty output
- [x] All 16 integration tests pass
- [x] All existing tests pass (320 total, 2 skipped)
- [x] Existing test fixes are minimal (assertion change for explicit reset, input change for natural escalation)
- [x] No modifications to conscious.py
- [x] No modifications to deliberator.py, prompt_assembly.py, deliberator_anthropic.py
- [x] No modifications to sensory.py, immune.py
- [x] No modifications to text_codec.py, codec.py
- [x] No modifications to base.py
- [x] No modifications to orientational field
- [x] No historical handoff files edited
- [x] `handoff/state.md` copied to `planning/014_integration.md`
- [x] `planning/CURRENT.md` rebuilt from actual repo inspection
- [x] DEVLOG.md entry added
- [x] README.md updated
- [x] Git commit and push completed (a2d7203)

## Files Changed

| File | Action |
|------|--------|
| `src/agenetic/network/graph.py` | Updated — default escalation False |
| `src/agenetic/systems/motor.py` | Updated — conscious suppression check, strategy recording |
| `src/agenetic/systems/subconscious.py` | Updated — explicit flag reset |
| `tests/test_integration.py` | Created — 16 end-to-end path tests |
| `tests/test_conscious.py` | Updated — input change for natural escalation |
| `tests/test_systems.py` | Updated — escalation flag test renamed and assertion updated |
| `planning/014_integration.md` | Created — copied from state.md |
| `planning/CURRENT.md` | Rebuilt from repo inspection |
| `DEVLOG.md` | D014 entry appended |
| `README.md` | Routing paths and test count updated |
| `handoff/014_response.md` | This file |
