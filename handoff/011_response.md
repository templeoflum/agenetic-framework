# Directive 011 Response — Conscious Layer Foundation

**Agent:** DNAgent (Claude Code CLI)
**Date:** 2026-02-09
**Status:** Complete
**Tests:** 262 passing + 1 skipped (was 238, +24 conscious tests)

---

## Summary

Replaced the conscious stub with three foundational components: ConsciousOutput contract, proceed/suppress gate, and Deliberator protocol. This is the system's crossing from signal domain into semantic domain. The conscious layer is now the first and only system that constructs meaning.

No modifications to sensory, immune, subconscious, motor, or the orientational field. No historical handoff files edited. No graph routing changes.

## Part-by-Part Report

### Part A: Type Definitions — DONE

Added to `base.py`:
- `ResponseDecision` (intent, strategy, constraints)
- `ExpressionDirectives` (field_weights, active_limbs, resting_stance, suppress_identity, state_awareness)
- `Lineage` (escalation_reason, signal_summary, field_snapshot, gate_evaluation, deliberation_model)
- `ConsciousOutput` (decision + expression + lineage + proceed + confidence)
- `conscious_output: ConsciousOutput | None` added to `SystemState`
- All 18 limb ID constants (extended from 9)
- `CONVERGENT_CLUSTER_IDS` list

Updated `graph.py`:
- `conscious_output: Any` added to `GraphState`
- `create_default_state()` includes `"conscious_output": None`
- `_make_node()` passes `conscious_output` through to `full_state`

### Part B: Proceed/Suppress Gate — DONE

Implemented as `ConsciousSystem._evaluate_gate()`. Pure Python, no LLM call. Priority order:

1. **Immune override** — `threat_action == "escalate"` → always proceed
2. **Ārēka suppression** — weight > 0.7 AND classification == "noise"
3. **Nivṛtti pause** — weight > 0.7 AND aggregate_deviation < 0.5
4. **Resting stance** — composite > 0.8 AND deviation < 0.3
5. **Default** — proceed

Gate returns full evaluation dict. Suppression produces complete ConsciousOutput (not None).

### Part C: Deliberator Protocol — DONE

Created `src/agenetic/systems/deliberator.py`:
- `Deliberator` — runtime_checkable Protocol
- `DeliberationRequest` — structured input (input_text, signal_summary, threat_summary, subconscious_summary, field_state, active_limbs, resting_stance, expression_directives)
- `MockDeliberator` — deterministic, tracks call_count and last_request

Created `src/agenetic/systems/deliberator_anthropic.py`:
- `AnthropicDeliberator` — first real LLM backend
- System prompt encodes active limb weights as behavioral instructions (14 limbs have high/low instructions)
- Uses claude-sonnet-4-20250514, max_tokens=1024
- Requests JSON response, parses into ConsciousOutput
- Fallback on parse failure: strategy="parse_fallback", confidence=0.3
- API key from ANTHROPIC_API_KEY env var (error at init time, not call time)

Added `anthropic` to pyproject.toml dependencies.

### Part D: Conscious System Integration — DONE

Replaced `src/agenetic/systems/conscious.py` (was 49 LOC stub, now ~440 LOC):
- `__init__(deliberator=None)` — accepts optional Deliberator
- `process()` — three paths:
  - Missing signal report → degradation flag, no output
  - Gate suppresses → suppression ConsciousOutput, zero LLM tokens
  - Gate proceeds → call deliberator (or degrade if none)
- `repair_check()` — lineage completeness + confidence threshold
- `apoptotic_condition()` — 3+ consecutive low-confidence streak

Helper methods:
- `_evaluate_gate()` — gate logic
- `_compute_active_limbs()` — weight outside 0.4–0.6
- `_compute_resting_stance()` — convergent cluster mean
- `_compute_expression_directives()` — full field snapshot + behavioral parameters
- `_build_deliberation_request()` — compressed state assembly
- `_compress_signal_report()` — features + deltas without hash/token_count
- `_build_suppression_output()` — complete ConsciousOutput for gate suppression
- `_build_degraded_output()` — complete ConsciousOutput for missing deliberator

### Part E: Tests — DONE

Created `tests/test_conscious.py` with 25 tests (24 pass, 1 skipped):

**Gate tests (9):** immune_override, areka_suppresses_noise, areka_permits_non_noise, nivrtti_suppresses_low_deviation, nivrtti_permits_high_deviation, resting_stance_suppresses, resting_stance_permits_deviation, default_proceeds, priority_order.

**Structure tests (3):** suppression_output_complete, lineage_always_present, no_deliberator_degrades.

**Protocol tests (3):** mock_satisfies_protocol, mock_returns_valid_output, call_count.

**Integration tests (8):** full_proceed_path, full_suppress_path, missing_signal_report, repair_check_passes, repair_check_fails_low_confidence, repair_check_fails_missing_lineage, apoptotic_after_streak, apoptotic_resets_on_high_confidence.

**Graph integration (1):** conscious_output_flows_to_motor.

**API test (1 skipped):** anthropic_deliberator_real_call — requires ANTHROPIC_API_KEY.

Updated `test_graph.py`: `_build_default_graph()` uses `MockDeliberator()`.
Updated `test_systems.py`: `_make_sample_state` includes `conscious_output: None`.

### Part F: Planning State Management — DONE

- `handoff/state.md` → `planning/011_conscious_foundation.md`
- `planning/CURRENT.md` rebuilt from repo inspection

### Part G: Documentation Updates — DONE

- `DEVLOG.md`: Directive 011 entry with gate logic, deliberator protocol, test counts
- `README.md`: Conscious system status updated, test count 238→262, Anthropic API line updated

## Verification Checklist

- [x] `ConsciousOutput`, `ResponseDecision`, `ExpressionDirectives`, `Lineage` TypedDicts exist in base.py
- [x] `conscious_output` field exists in both `SystemState` and `GraphState`
- [x] `create_default_state()` includes `conscious_output: None`
- [x] `_make_node()` passes `conscious_output` through to full_state
- [x] `ConsciousSystem.__init__` accepts optional `Deliberator`
- [x] `ConsciousSystem.process()` evaluates gate before any LLM call
- [x] Gate suppression produces complete `ConsciousOutput` with `proceed=False`
- [x] Gate respects priority order: immune override > Ārēka > Nivṛtti > resting stance > default
- [x] `ConsciousSystem.process()` calls `deliberator.deliberate()` only when gate proceeds
- [x] `ConsciousSystem.repair_check()` verifies lineage completeness
- [x] `ConsciousSystem.apoptotic_condition()` tracks low-confidence streak
- [x] `Deliberator` is a `runtime_checkable Protocol`
- [x] `MockDeliberator` satisfies the `Deliberator` protocol
- [x] `deliberator_anthropic.py` exists with Anthropic API implementation
- [x] `anthropic` is in pyproject.toml dependencies
- [x] All gate tests pass (9 tests)
- [x] All structure tests pass (3 tests)
- [x] All protocol tests pass (3 tests)
- [x] All integration tests pass with MockDeliberator (8 tests)
- [x] Graph integration test passes (1 test)
- [x] All 238 existing tests still pass
- [x] No modifications to sensory.py, immune.py, subconscious.py, or motor.py
- [x] No modifications to orientational field
- [x] No historical handoff files edited
- [x] `handoff/state.md` copied to `planning/011_conscious_foundation.md`
- [x] `planning/CURRENT.md` rebuilt from actual repo inspection
- [x] DEVLOG.md entry added
- [x] README.md updated
- [x] CURRENT.md updated from repo inspection
- [x] Git commit and push completed

## Files Changed

| File | Action |
|------|--------|
| `src/agenetic/systems/base.py` | Updated — ConsciousOutput types, all 18 limb constants, conscious_output in SystemState |
| `src/agenetic/systems/conscious.py` | Replaced — full gate + deliberator implementation (~440 LOC) |
| `src/agenetic/systems/deliberator.py` | Created — Deliberator Protocol, DeliberationRequest, MockDeliberator |
| `src/agenetic/systems/deliberator_anthropic.py` | Created — AnthropicDeliberator (Anthropic API backend) |
| `src/agenetic/network/graph.py` | Updated — conscious_output in GraphState, create_default_state, _make_node |
| `tests/test_conscious.py` | Created — 25 tests (gate, structure, protocol, integration, graph, API) |
| `tests/test_graph.py` | Updated — _build_default_graph uses MockDeliberator |
| `tests/test_systems.py` | Updated — _make_sample_state includes conscious_output |
| `pyproject.toml` | Updated — anthropic dependency added |
| `DEVLOG.md` | Updated — Directive 011 entry |
| `README.md` | Updated — Conscious system status, test count |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `planning/011_conscious_foundation.md` | Created — copied from handoff/state.md |
