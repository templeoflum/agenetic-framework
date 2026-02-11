# Directive 019 — Feedback Loops + Topology Consultation

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-11

## Context

Read `planning/CURRENT.md` first, then `CLAUDE.md` for orientation.

Phase 1 (Single Cell) and Phase 2 (Temporal Stratification) are complete as of D018. The current graph is a pipeline: sensory → immune → subconscious → (conscious?) → motor → END. Information flows in one direction only.

Phase 3 (Network Topology + Self-Regulation) turns this pipeline into a network by wiring feedback loops — secondary connections that allow downstream systems to influence upstream ones. The architecture specifies six secondary connections in `src/agenetic/network/topology.py`. This directive wires three:

1. **Motor→Conscious** (weight 0.5): "Output feedback — expression difficulties escalated"
2. **Conscious→Sensory** (weight 0.5): "Re-examination requests"
3. **Conscious→Immune** (weight 0.5): "Deliberation adjusts threat thresholds"

These three represent the highest-value feedback paths: retry on failure, re-examine on uncertainty, and learning from deliberation. The remaining three secondaries (Conscious→Subconscious, Immune→Subconscious, Subconscious→Immune) are deferred.

**Phase items this directive closes:**
- Feedback loops: Motor→Conscious ✓
- Feedback loops: Conscious→Sensory ✓
- Feedback loops: Conscious→Immune ✓
- Graph uses topology.py connection weights (partial — secondary connection gating)

## Objective

Wire three feedback loops into the LangGraph routing, add immune threshold adjustment via state propagation, and establish topology weight consultation as the gating mechanism for secondary connections.

## Part A: Feedback State Infrastructure

### A1: FeedbackSignals TypedDict in base.py

Add to `src/agenetic/systems/base.py`, after the `GeneticOutput` definition and before `SystemState`:

```python
class FeedbackSignals(TypedDict):
    """Coordination state for feedback loops between systems.

    Tracks retry/re-examination counts (to enforce max iterations)
    and carries threshold adjustments from conscious to immune.
    """
    motor_retry_count: int  # times motor has retried via conscious (max 1)
    re_examine_count: int  # times conscious requested re-examination (max 1)
    immune_threshold_adjustments: dict[str, float]  # threshold_name -> delta
```

### A2: Add feedback to SystemState and GraphState

In `SystemState` (base.py), add: `feedback: FeedbackSignals | None`

In `GraphState` (graph.py), add: `feedback: Any`

In `create_default_state()` (graph.py), add: `"feedback": None`

In `_make_node()` (graph.py), add to the full_state construction: `"feedback": state.get("feedback"),`

### A3: Add re_examine to ConsciousOutput

In `ConsciousOutput` (base.py), add after the `confidence` field:

```python
    re_examine: bool  # Requests sensory re-examination (default False)
```

### A4: Update all ConsciousOutput builders

In `src/agenetic/systems/conscious.py`:

**`_build_suppression_output()`** — add `"re_examine": False` to the returned dict.

**`_build_degraded_output()`** — add `"re_examine": False` to the returned dict.

**`process()` after deliberator call** — the deliberator returns ConsciousOutput. After the `conscious_output["lineage"]["gate_evaluation"] = gate_eval` line, add:
```python
        # Ensure re_examine is present (deliberator may not set it).
        if "re_examine" not in conscious_output:
            conscious_output["re_examine"] = False
```

### A5: Update MockDeliberator

In `src/agenetic/systems/deliberator.py`, in `MockDeliberator.deliberate()`, add `"re_examine": False` to the returned dict (after the `"confidence": 0.8` line).

### A6: Update _make_sample_state

In `tests/test_systems.py`, add `"feedback": None` to the state returned by `_make_sample_state()`.

## Part B: Motor→Conscious Feedback (Retry on Failure)

### B1: Retry gate node in graph.py

Add a passthrough function that increments the motor retry counter:

```python
def _increment_motor_retry(state: GraphState) -> GraphState:
    """Gate node: increment motor retry count before routing to conscious."""
    feedback = dict(state.get("feedback") or _default_feedback())
    feedback["motor_retry_count"] = feedback.get("motor_retry_count", 0) + 1
    return {**state, "feedback": feedback}
```

Add a helper for default feedback:

```python
def _default_feedback() -> dict:
    """Create default feedback signals."""
    return {
        "motor_retry_count": 0,
        "re_examine_count": 0,
        "immune_threshold_adjustments": {},
    }
```

### B2: After-motor conditional function

Replace the current `motor → END` edge with a conditional:

```python
def _after_motor(state: GraphState) -> Literal["retry_gate", "__end__"]:
    """Route after motor: retry via conscious or finish.

    Fires the motor→conscious secondary connection if:
    1. Motor repair check failed
    2. Haven't already retried (max 1 retry)
    3. Topology weight for motor→conscious > 0
    """
    motor_output = state.get("motor_output")
    repair_failed = (
        motor_output is not None
        and not motor_output.get("repair_passed", True)
    )

    feedback = state.get("feedback") or _default_feedback()
    retry_count = feedback.get("motor_retry_count", 0)

    if repair_failed and retry_count < 1 and _get_topology_weight("motor", "conscious") > 0:
        return "retry_gate"

    return "__end__"
```

### B3: Topology weight helper

Add a helper that wraps topology import (to keep the import clean and testable):

```python
def _get_topology_weight(source: str, target: str) -> float:
    """Get connection weight from topology. Returns 0.0 if absent."""
    from agenetic.network.topology import get_weight
    return get_weight(source, target)
```

Use a lazy import to avoid potential import-time issues.

## Part C: Conscious→Sensory Feedback (Re-examination)

### C1: Re-examine gate node in graph.py

```python
def _increment_re_examine(state: GraphState) -> GraphState:
    """Gate node: increment re-examination count before routing to sensory."""
    feedback = dict(state.get("feedback") or _default_feedback())
    feedback["re_examine_count"] = feedback.get("re_examine_count", 0) + 1
    return {**state, "feedback": feedback}
```

### C2: After-conscious conditional function

Replace the current `conscious → motor` edge with a conditional:

```python
def _after_conscious(state: GraphState) -> Literal["re_examine_gate", "motor"]:
    """Route after conscious: re-examine or proceed to motor.

    Fires the conscious→sensory secondary connection if:
    1. Conscious requested re-examination
    2. Haven't already re-examined (max 1)
    3. Topology weight for conscious→sensory > 0
    """
    conscious_output = state.get("conscious_output")
    re_examine = (
        conscious_output is not None
        and conscious_output.get("re_examine", False)
    )

    feedback = state.get("feedback") or _default_feedback()
    re_examine_count = feedback.get("re_examine_count", 0)

    if re_examine and re_examine_count < 1 and _get_topology_weight("conscious", "sensory") > 0:
        return "re_examine_gate"

    return "motor"
```

## Part D: Conscious→Immune Threshold Adjustment

### D1: Immune reads threshold adjustments

In `src/agenetic/systems/immune.py`, in `process()`, after the line `features = report["features"]` and before the innate immunity checks, add:

```python
        # Read threshold adjustments from conscious feedback (if present).
        feedback = state.get("feedback") or {}
        adjustments = feedback.get("immune_threshold_adjustments", {})

        # Apply adjustments to innate thresholds for this invocation.
        entropy_threshold = 6.0 + adjustments.get("entropy_threshold", 0.0)
        noise_floor_threshold = 0.35 + adjustments.get("noise_floor_threshold", 0.0)
        impedance_threshold = 0.5 + adjustments.get("impedance_threshold", 0.0)
        deviation_threshold = 3.0 + adjustments.get("deviation_threshold", 0.0)
        vocabulary_threshold = 0.1 + adjustments.get("vocabulary_threshold", 0.0)
        adaptive_threshold = self.ADAPTIVE_MATCH_THRESHOLD + adjustments.get("adaptive_match_threshold", 0.0)
```

Then replace the hardcoded threshold values in the innate immunity checks:

```python
        if features["entropy"] > entropy_threshold:
            anomaly_scores["entropy"] = features["entropy"] - entropy_threshold
        if features["noise_floor"] > noise_floor_threshold:
            anomaly_scores["noise_floor"] = features["noise_floor"] - noise_floor_threshold
        if features["impedance"] > impedance_threshold:
            anomaly_scores["impedance"] = features["impedance"] - impedance_threshold
        if delta["aggregate_deviation"] > deviation_threshold:
            anomaly_scores["aggregate_deviation"] = delta["aggregate_deviation"] - deviation_threshold
        if features["vocabulary_richness"] < vocabulary_threshold:
            anomaly_scores["vocabulary_richness"] = vocabulary_threshold - features["vocabulary_richness"]
```

And in the adaptive matching section, replace `self.ADAPTIVE_MATCH_THRESHOLD` with `adaptive_threshold`.

**Important:** The default behavior (no adjustments) must produce IDENTICAL results to the current implementation. All adjustment deltas default to 0.0.

## Part E: Updated build_graph

### E1: Update build_graph function

Replace the current routing section in `build_graph()` with:

```python
    graph = StateGraph(GraphState)

    # System nodes.
    graph.add_node("sensory", _make_node(sensory))
    graph.add_node("immune", _make_node(immune))
    graph.add_node("subconscious", _make_node(subconscious))
    graph.add_node("conscious", _make_node(conscious))
    graph.add_node("motor", _make_node(motor))

    # Feedback gate nodes (increment counters at routing boundaries).
    graph.add_node("retry_gate", _increment_motor_retry)
    graph.add_node("re_examine_gate", _increment_re_examine)

    # Signal domain: always runs in order.
    graph.set_entry_point("sensory")
    graph.add_edge("sensory", "immune")
    graph.add_edge("immune", "subconscious")

    # Escalation gate: subconscious decides conscious involvement.
    graph.add_conditional_edges(
        "subconscious",
        _should_escalate,
        {"conscious": "conscious", "motor": "motor"},
    )

    # After conscious: re-examine or proceed to motor.
    graph.add_conditional_edges(
        "conscious",
        _after_conscious,
        {"re_examine_gate": "re_examine_gate", "motor": "motor"},
    )

    # Re-examination loop: gate → sensory (re-runs signal domain).
    graph.add_edge("re_examine_gate", "sensory")

    # After motor: retry via conscious or finish.
    graph.add_conditional_edges(
        "motor",
        _after_motor,
        {"retry_gate": "retry_gate", "__end__": END},
    )

    # Retry loop: gate → conscious (re-deliberation).
    graph.add_edge("retry_gate", "conscious")

    return graph.compile()
```

### E2: Update graph.py module docstring

Replace the current docstring with:

```python
"""LangGraph wiring — builds a runnable graph from the seven systems.

Phase 3 routing with feedback loops:
1. Signal domain (sensory, immune, subconscious) processes every cycle
2. Conditional escalation to conscious (subconscious decides)
3. Conscious may request re-examination → routes back to sensory (max 1)
4. Motor produces output
5. Motor may fail repair → routes back to conscious for retry (max 1)

Sleep and genetic are not actively routed (called outside the graph).

Secondary connections gated by topology weights:
- motor→conscious (0.5): retry on repair failure
- conscious→sensory (0.5): re-examination request
- conscious→immune: threshold adjustment via state propagation (no routing)

Setting a topology weight to 0.0 disables the corresponding feedback path.
"""
```

## Part F: Tests

### F1: Create tests/test_feedback.py

Create `tests/test_feedback.py` with the following test categories. All tests are deterministic — no LLM calls.

**Motor→Conscious retry (5 tests):**

- `test_motor_retry_on_repair_failure` — Set up a state where motor will fail repair (use a MotorSystem with conditions that cause repair failure — e.g., an input that produces empty output after transformation). Invoke the graph. Verify routing_history contains "conscious" and "motor" appearing twice (original + retry).

- `test_motor_no_retry_on_success` — Normal input through graph. Verify motor appears exactly once in routing_history.

- `test_motor_max_one_retry` — Force motor to fail on both attempts. Verify motor appears exactly twice (not infinite loop). This needs a motor that always fails repair — use a custom input or mock.

- `test_motor_retry_count_incremented` — After a retry, verify `feedback["motor_retry_count"]` is 1 in the result state.

- `test_motor_retry_disabled_when_weight_zero` — This test is observational: verify that `_after_motor` returns `"__end__"` when called with a state where repair failed but the function would check topology weight. (Testing the topology gating directly via the function, not the full graph, since we can't modify topology weights at runtime without mocking.)

**Conscious→Sensory re-examination (4 tests):**

- `test_re_examine_routes_back_to_sensory` — Create a custom deliberator that sets `re_examine=True` on first call, `re_examine=False` on second. Invoke graph with escalation. Verify routing_history shows sensory appearing twice.

- `test_re_examine_max_one` — Custom deliberator always sets `re_examine=True`. Verify sensory appears exactly twice (not infinite).

- `test_re_examine_count_incremented` — After re-examination, verify `feedback["re_examine_count"]` is 1.

- `test_no_re_examine_when_false` — Default MockDeliberator (re_examine=False). Verify sensory appears exactly once.

**Conscious→Immune threshold adjustment (4 tests):**

- `test_immune_uses_default_thresholds_without_feedback` — Invoke immune with no feedback in state. Verify behavior matches current implementation exactly (entropy > 6.0 triggers anomaly).

- `test_immune_respects_threshold_adjustment` — Set `feedback["immune_threshold_adjustments"]["entropy_threshold"]` to -2.0 (lowers threshold from 6.0 to 4.0). Provide signal with entropy=5.0. Without adjustment: no anomaly. With adjustment: anomaly detected.

- `test_immune_multiple_adjustments` — Set adjustments for entropy and noise_floor. Verify both take effect.

- `test_immune_adjustment_zero_is_noop` — Set adjustment to 0.0 explicitly. Verify identical behavior to no feedback.

**FeedbackSignals infrastructure (3 tests):**

- `test_default_state_has_feedback_none` — `create_default_state()` returns state with `feedback: None`.

- `test_graph_preserves_feedback` — Set feedback in initial state, invoke graph, verify feedback is present in result.

- `test_conscious_output_has_re_examine` — Invoke graph with escalation, verify `conscious_output["re_examine"]` exists and is a bool.

**Total: 16 new tests.**

## Part G: Planning State Management

### G1: Copy State to Planning Entry
Copy `handoff/state.md` to `planning/019_feedback_loops.md`.

### G2: Update CURRENT.md from Repo Inspection
Rebuild `planning/CURRENT.md` from actual repo state. Update Phase Completion section:

```markdown
| Phase | Status | Closed by |
|---|---|---|
| 1 — Single Cell | **COMPLETE** | D001–D018 |
| 2 — Temporal Stratification | **COMPLETE** | D011–D017 |
| 3 — Network Topology + Self-Regulation | **In progress** | D019– |
| 4 — Epigenetic Adaptation | Not started | — |
```

Update Phase 3 remaining items — check off feedback loops, mark topology weights as partial.

## Part H: Documentation

### H1: DEVLOG Entry

```markdown
## 2026-02-11 — Directive 019: Feedback Loops + Topology Consultation

**Commit:** `[hash]`
**Tests:** [count] passing + 2 skipped ([new] new)

**Phase items closed:** Three feedback loops (Motor→Conscious, Conscious→Sensory, Conscious→Immune), partial topology weight consultation.

Wired three secondary connections from the architecture into the LangGraph routing, transforming the processing pipeline into a network with bounded cycles:

- **Motor→Conscious** (retry): when motor's repair check fails, routes back to conscious for re-deliberation, then motor retries. Max 1 retry per invocation. Bounded by feedback counter.
- **Conscious→Sensory** (re-examination): conscious can request the signal domain re-analyze the input. Routes back to sensory, re-runs immune and subconscious, then conscious decides again. Max 1 re-examination. Currently dormant (MockDeliberator never requests it).
- **Conscious→Immune** (threshold adjustment): conscious writes threshold deltas to state; immune reads them and adjusts innate detection thresholds. Takes effect on re-examination loops or next invocation.

All three secondary connections are gated by topology.py weights — setting weight to 0.0 disables the feedback path. Introduced FeedbackSignals TypedDict for cross-system coordination and passthrough gate nodes as the LangGraph pattern for state mutation at routing boundaries.
```

### H2: README Update
- Update test count
- Note Phase 3 in progress in status section

## Scope Boundaries

**DO:**
- Read `src/agenetic/systems/base.py` for SystemState, ConsciousOutput TypedDicts
- Read `src/agenetic/network/graph.py` for GraphState, create_default_state, build_graph
- Read `src/agenetic/network/topology.py` for get_weight function signature
- Read `src/agenetic/systems/immune.py` for innate threshold values
- Read `src/agenetic/systems/conscious.py` for output builder methods
- Read `src/agenetic/systems/deliberator.py` for MockDeliberator return structure
- Read `tests/test_systems.py` for _make_sample_state

**DO NOT:**
- Modify topology.py (connection definitions are correct as-is)
- Modify sensory.py, subconscious.py, motor.py, sleep.py, genetic.py
- Modify orientational.py
- Wire the other three secondary connections (Conscious→Subconscious, Immune→Subconscious, Subconscious→Immune)
- Make topology weights mutable at runtime (Phase 4)
- Edit any historical handoff files (handoff/001–018_*.md)

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/base.py` | Updated — FeedbackSignals TypedDict, re_examine in ConsciousOutput, feedback in SystemState |
| `src/agenetic/network/graph.py` | Updated — feedback routing, gate nodes, topology consultation, updated docstring |
| `src/agenetic/systems/immune.py` | Updated — reads threshold adjustments from feedback |
| `src/agenetic/systems/conscious.py` | Updated — re_examine=False in output builders |
| `src/agenetic/systems/deliberator.py` | Updated — re_examine=False in MockDeliberator |
| `tests/test_feedback.py` | Created — 16 tests |
| `tests/test_systems.py` | Updated — feedback in _make_sample_state |
| `DEVLOG.md` | Updated — D019 entry |
| `README.md` | Updated — test count, status |
| `handoff/state.md` | Provided — copy to planning entry |
| `planning/019_feedback_loops.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `handoff/019_directive.md` | This file |
| `handoff/019_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `FeedbackSignals` TypedDict defined in base.py with motor_retry_count, re_examine_count, immune_threshold_adjustments
- [ ] `SystemState` includes `feedback: FeedbackSignals | None`
- [ ] `GraphState` includes `feedback: Any`
- [ ] `create_default_state()` includes `"feedback": None`
- [ ] `_make_node()` passes `feedback` through to full_state
- [ ] `ConsciousOutput` includes `re_examine: bool`
- [ ] `_build_suppression_output()` returns `re_examine: False`
- [ ] `_build_degraded_output()` returns `re_examine: False`
- [ ] `conscious.process()` ensures re_examine is present after deliberator call
- [ ] `MockDeliberator.deliberate()` returns `re_examine: False`
- [ ] `_make_sample_state()` in test_systems.py includes `"feedback": None`
- [ ] `_default_feedback()` helper function exists in graph.py
- [ ] `_get_topology_weight()` helper exists in graph.py and calls `topology.get_weight()`
- [ ] `_after_motor()` routes to retry_gate when repair fails, retry_count < 1, and weight > 0
- [ ] `_after_motor()` routes to `__end__` when repair passes or retry exhausted
- [ ] `_after_conscious()` routes to re_examine_gate when re_examine=True, count < 1, weight > 0
- [ ] `_after_conscious()` routes to motor when re_examine=False or count exhausted
- [ ] `_increment_motor_retry()` increments feedback["motor_retry_count"]
- [ ] `_increment_re_examine()` increments feedback["re_examine_count"]
- [ ] `retry_gate` node edges to conscious
- [ ] `re_examine_gate` node edges to sensory
- [ ] Immune reads `feedback.immune_threshold_adjustments` and applies as deltas
- [ ] Immune default behavior unchanged when no adjustments present
- [ ] Immune innate checks use variable thresholds, not hardcoded values
- [ ] `tests/test_feedback.py` has 16 tests, all passing
- [ ] No modifications to topology.py, sensory.py, subconscious.py, motor.py, sleep.py, genetic.py, orientational.py
- [ ] No circular imports introduced (graph.py lazy-imports topology)
- [ ] All existing 389 tests still pass
- [ ] Graph still compiles and basic routing works (existing test_graph.py tests pass)
- [ ] No historical handoff files edited
- [ ] `handoff/state.md` copied to `planning/019_feedback_loops.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection
- [ ] Git commit and push completed
