# Directive 014 — Integration: Conditional Escalation, Conscious-Motor Wiring, End-to-End Paths

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-10

## Context

Read these files first, in this order:
1. `planning/CURRENT.md` — factual snapshot of where things stand
2. `CLAUDE.md` — project conventions, agent roles, directive protocol
3. `docs/ARCHITECTURE.md` — the v2 specification
4. `docs/architecture_amendment.md` — the signal-semantics boundary
5. `src/agenetic/network/graph.py` — current routing (what this directive changes)
6. `src/agenetic/systems/subconscious.py` — escalation decision (already works, just masked by default)
7. `src/agenetic/systems/conscious.py` — deliberation layer
8. `src/agenetic/systems/motor.py` — motor orchestrator (gets conscious integration)
9. `src/agenetic/systems/text_codec.py` — text codec (unchanged)
10. `planning/013_motor_codec.md` — previous directive's design decisions

**What happened before this directive:**

Directives 001–010: Complete signal domain. 238 tests.
Directive 011: Conscious layer foundation — ConsciousOutput, gate, Deliberator protocol, Anthropic implementation. 262 tests.
Directive 012: Prompt assembly refinement — graduated intensity, limb interactions, observation harness. 292 tests.
Directive 013: Motor codec refactor — TextCodec extraction behind Codec protocol. 304 tests.

The architecture currently has a structural gap: all pieces exist but aren't wired together properly.

**Gap 1: Routing is hardcoded.** `create_default_state()` sets `escalate_to_conscious=True` always. Subconscious computes a real escalation decision but the flag is pre-set. The conditional routing in the graph (`_should_escalate`) reads the flag, but it's always True. Result: every input goes through conscious, defeating the purpose of subconscious escalation gating.

**Gap 2: Motor ignores conscious output.** Motor reads `state["input"]` and `state["field"]`. It never checks `state["conscious_output"]`. When conscious suppresses (proceed=False), motor still processes the raw input and produces output. Conscious suppression is currently semantic-only — it produces a suppression record but motor doesn't act on it.

**Gap 3: No end-to-end path tests.** The graph integration test (`test_graph_conscious_output_flows_to_motor`) uses MockDeliberator and hardcoded escalation. There are no tests for: reflex path (subconscious decides not to escalate, motor processes directly), suppression path (conscious gate suppresses, motor receives suppression), or conditional routing driven by actual subconscious decisions.

This directive closes all three gaps.

**What this directive does NOT do:**
- Does NOT modify conscious.py (the conscious system's process flow is unchanged)
- Does NOT modify deliberator.py, prompt_assembly.py, deliberator_anthropic.py
- Does NOT modify sensory.py, immune.py
- Does NOT modify text_codec.py, codec.py
- Does NOT modify base.py types
- Does NOT modify the orientational field
- Does NOT change connection weights or topology

## Objective

Wire conditional escalation, conscious-motor integration, and end-to-end path testing. Subconscious drives escalation. Motor respects conscious suppression. Both reflex and escalated paths are tested end-to-end through the graph.

## Part A: Fix Routing — Conditional Escalation

### A1: Change default escalation flag

In `graph.py`, `create_default_state()`:

Change:
```python
"escalate_to_conscious": True,  # Phase 1 default: always escalate
```

To:
```python
"escalate_to_conscious": False,  # Subconscious drives escalation
```

This is the single most impactful one-line change in the project. It activates subconscious-driven routing.

### A2: Verify subconscious already sets the flag correctly

Subconscious already has this logic (no changes needed):
```python
if escalation_recommended:
    flags["escalate_to_conscious"] = True
```

But subconscious only sets to True, never explicitly to False. Since the default is now False, this is correct: if subconscious doesn't recommend escalation, the flag stays False and motor processes directly.

### A3: Impact assessment

Changing the default breaks existing tests that assume escalation always happens. Specifically:

- `test_graph_conscious_output_flows_to_motor` in `test_conscious.py` — creates state via `create_default_state()`, expects conscious to fire. **Fix: explicitly set `escalate_to_conscious=True` in test setup.**
- Any other graph tests that assume conscious always fires. **Fix: same approach — set the flag explicitly in tests that need escalation.**
- Tests that test the reflex path may now pass that previously couldn't be reached.

**The fix pattern:** Tests that specifically test the escalated path should explicitly set `flags["escalate_to_conscious"] = True` in their state setup. Tests that test the reflex path should leave the default (False). This is more honest — tests declare which path they're testing.

Scan ALL test files for uses of `create_default_state()` that flow through the graph and expect conscious to fire. Fix each one by explicitly setting the flag. Do NOT change tests that don't run through the graph (unit tests that call `ConsciousSystem.process()` directly set up their own state with explicit flag values).

## Part B: Motor-Conscious Integration

### B1: Motor respects conscious suppression

In `motor.py`, `MotorSystem.process()`, add a check BEFORE codec delegation:

```python
# Check conscious output for suppression.
conscious_output = state.get("conscious_output")
if conscious_output is not None and not conscious_output.get("proceed", True):
    # Conscious suppressed — motor produces empty output.
    motor_output = {
        "output_text": "",
        "target_profile": target,
        "strategies_applied": ["conscious_suppression"],
        "repair_passed": True,
        "transform_magnitude": 0.0,
    }
    return {**state, "motor_output": motor_output}
```

This goes AFTER target computation but BEFORE empty-input check. Conscious suppression takes priority over everything except the target profile computation (which motor always does for consistency).

### B2: Motor records conscious strategy

When conscious output exists and proceed=True, motor should record the conscious strategy in its output for lineage tracking. Add to the `motor_output` dict construction (after codec delegation):

```python
# Record conscious strategy if available.
if conscious_output is not None and conscious_output.get("proceed"):
    motor_output["conscious_strategy"] = conscious_output["decision"].get("strategy", "unknown")
```

This is metadata only — it doesn't change motor's processing behavior. The conscious strategy could influence text restructuring in a future directive, but for now motor just records it.

### B3: Update MotorOutput type (optional)

If `motor_output["conscious_strategy"]` requires a type update in base.py, add it as an optional field. However, since MotorOutput is a TypedDict and existing code constructs it without this field, the simplest approach is to NOT change the TypedDict and let the field be an ad-hoc addition. TypedDict allows extra keys at runtime.

**Decision: Do NOT modify base.py.** The conscious_strategy field is informational metadata, not a structural contract. This avoids touching base.py (which has widespread imports) for a metadata field.

## Part C: Subconscious Minor Improvement

### C1: Explicit flag reset

Currently subconscious only sets `escalate_to_conscious = True` when recommending escalation. With the default now False, this works correctly. However, for clarity and defensive programming, add an explicit else:

```python
if escalation_recommended:
    flags["escalate_to_conscious"] = True
else:
    flags["escalate_to_conscious"] = False
```

This is defense-in-depth. If state somehow arrives with the flag already True from a previous cycle, subconscious now explicitly resets it. Without this, a stale True flag from a previous graph invocation could cause spurious escalation.

## Part D: Tests

### D1: Fix existing tests broken by default change

Scan all test files. For any test that:
1. Creates state via `create_default_state()`
2. Invokes the graph (via `graph.invoke()`)
3. Expects `conscious` in the routing history

Add `state["flags"]["escalate_to_conscious"] = True` to the test setup. Document the change with a comment: `# Explicitly escalate for this test`.

Likely candidates:
- `test_conscious.py::TestConsciousGraphIntegration::test_graph_conscious_output_flows_to_motor`
- Any graph tests in `test_graph.py` that expect conscious routing

### D2: New end-to-end tests in `tests/test_integration.py`

Create a new test file for end-to-end path tests. These test the full graph with real routing decisions.

**Reflex path tests (4):**

1. **test_reflex_path_skips_conscious**: Input with low deviation (subconscious doesn't escalate) → graph runs sensory → immune → subconscious → motor. Conscious NOT in routing history. Motor output exists. Conscious output is None.

2. **test_reflex_path_motor_processes_input**: Same setup as #1. Motor output contains restructured text. Motor used the input text directly (no conscious mediation).

3. **test_reflex_path_subconscious_decision**: Verify subconscious output exists and `escalation_recommended=False` on the reflex path.

4. **test_reflex_path_signal_report_flows**: Verify signal_report, threat_assessment, and subconscious_output are all populated even on the reflex path. Only conscious_output is None.

**Escalated path tests (4):**

5. **test_escalated_path_includes_conscious**: Input that triggers escalation (high deviation, novel signal) → graph runs sensory → immune → subconscious → conscious → motor. Both conscious and motor in routing history.

6. **test_escalated_path_conscious_output_present**: Conscious output exists with all required fields (decision, expression, lineage, proceed, confidence).

7. **test_escalated_path_motor_receives_conscious**: Motor output exists. If conscious proceeded, motor_output has `conscious_strategy` field. If conscious suppressed, motor_output has `strategies_applied=["conscious_suppression"]`.

8. **test_escalated_path_uses_mock_deliberator**: Graph built with MockDeliberator. Escalated path produces conscious_output with `deliberation_model="mock"`.

**Suppression path tests (3):**

9. **test_suppression_path_motor_empty**: Set up state where conscious gate suppresses (e.g., high Ārēka + noise). Motor should produce empty output with "conscious_suppression" strategy.

10. **test_suppression_path_lineage**: On suppression, conscious_output has proceed=False and gate_evaluation explains why. Motor output has `strategies_applied=["conscious_suppression"]`.

11. **test_suppression_path_no_deliberator_call**: Build graph with MockDeliberator. On suppression path, mock's call_count should be 0 (gate suppressed before deliberation).

**Routing decision tests (3):**

12. **test_routing_default_is_reflex**: `create_default_state()` with no overrides → graph takes reflex path (conscious NOT in routing history).

13. **test_routing_subconscious_escalates_on_threat**: State with threat_level="high" → subconscious recommends escalation → graph routes to conscious.

14. **test_routing_subconscious_no_escalate_on_familiar**: Use signal_pattern_cache with matching patterns that had "reflex_response" outcomes → subconscious does NOT recommend escalation → reflex path.

**Cross-path consistency tests (2):**

15. **test_both_paths_produce_motor_output**: Whether escalated or reflex, motor_output always exists and has all required fields.

16. **test_both_paths_preserve_signal_report**: Signal report is identical regardless of which path was taken (conscious doesn't modify it).

### D3: Total new test count

16 new tests in `test_integration.py`.

### D4: Existing tests — fixes only, no new assertions

Update broken tests per D1. No new assertions added to existing tests. The fix is always the same: explicitly set `escalate_to_conscious=True` where escalation is assumed.

## Part E: Planning State Management

### E1: Copy State to Planning Entry

Copy `handoff/state.md` to `planning/014_integration.md`.

### E2: Update CURRENT.md from Repo Inspection

After all code changes and tests pass, rebuild `planning/CURRENT.md` from ground truth.

## Part F: Documentation Updates

### F1: DEVLOG Entry

Add entry for Directive 014. Prose summary: conditional escalation activated, conscious-motor wiring, three path types verified (reflex, escalated, suppression).

### F2: README Status Update

Update README.md: describe the three routing paths, update test count.

## Scope Boundaries

**DO:**
- Change `escalate_to_conscious` default from True to False in `graph.py`
- Add conscious suppression check to `motor.py`
- Add conscious_strategy metadata recording to `motor.py`
- Add explicit flag reset to `subconscious.py`
- Fix existing tests broken by default change
- Create `tests/test_integration.py` with 16 end-to-end path tests
- Update DEVLOG.md, README.md, CURRENT.md
- Copy state.md to planning entry

**DO NOT:**
- Modify conscious.py
- Modify deliberator.py, prompt_assembly.py, deliberator_anthropic.py
- Modify sensory.py, immune.py
- Modify text_codec.py, codec.py
- Modify base.py (no type changes)
- Modify the orientational field
- Change connection weights or topology
- Edit any historical handoff files (001–013)
- Add semantic rendering to motor (motor doesn't interpret conscious decisions, just records and respects suppress/proceed)

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/network/graph.py` | Updated — default escalation False |
| `src/agenetic/systems/motor.py` | Updated — conscious suppression check, strategy recording |
| `src/agenetic/systems/subconscious.py` | Updated — explicit flag reset |
| `tests/test_integration.py` | Created — 16 end-to-end path tests |
| `tests/test_conscious.py` | Updated — fix broken test(s) with explicit escalation flag |
| `tests/test_graph.py` | Updated — fix broken test(s) with explicit escalation flag (if any) |
| `handoff/state.md` | Provided — planning notes for this cycle |
| `planning/014_integration.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `DEVLOG.md` | Updated — Directive 014 entry |
| `README.md` | Updated — routing paths, test count |
| `handoff/014_directive.md` | This file |
| `handoff/014_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `create_default_state()` sets `escalate_to_conscious=False`
- [ ] Subconscious sets `escalate_to_conscious=True` when `escalation_recommended=True`
- [ ] Subconscious explicitly sets `escalate_to_conscious=False` when `escalation_recommended=False`
- [ ] Motor checks `conscious_output` before codec delegation
- [ ] Motor produces empty output with "conscious_suppression" strategy when conscious proceeds=False
- [ ] Motor records `conscious_strategy` metadata when conscious proceeds=True
- [ ] Motor behavior unchanged when conscious_output is None (reflex path)
- [ ] base.py is NOT modified
- [ ] Reflex path works: low-deviation input → subconscious doesn't escalate → motor processes directly
- [ ] Escalated path works: high-deviation/threat input → subconscious escalates → conscious deliberates → motor processes
- [ ] Suppression path works: Ārēka + noise → conscious suppresses → motor produces empty output
- [ ] All 16 integration tests pass
- [ ] All existing tests pass (304 prior + fixes for default change)
- [ ] Existing test fixes are ONLY explicit flag setting (no assertion changes)
- [ ] No modifications to conscious.py
- [ ] No modifications to deliberator.py, prompt_assembly.py, deliberator_anthropic.py
- [ ] No modifications to sensory.py, immune.py
- [ ] No modifications to text_codec.py, codec.py
- [ ] No modifications to base.py
- [ ] No modifications to orientational field
- [ ] No historical handoff files edited
- [ ] `handoff/state.md` copied to `planning/014_integration.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection
- [ ] DEVLOG.md entry added
- [ ] README.md updated
- [ ] Git commit and push completed
