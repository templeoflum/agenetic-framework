# 019 — Feedback Loops + Topology Consultation

**Date:** 2026-02-11
**Directive type:** Implementation
**Phase:** 3 (Network Topology + Self-Regulation) — partial closure

## Decisions

### Three feedback loops, three different mechanisms

The six secondary connections in topology.py represent different kinds of feedback. D019 wires three:

1. **Motor→Conscious** (graph cycle): retry on motor repair failure, max 1 retry
2. **Conscious→Sensory** (graph cycle): re-examination of input, max 1 re-examine
3. **Conscious→Immune** (state propagation): threshold adjustment, no routing change

The remaining three secondaries (Conscious→Subconscious, Immune→Subconscious, Subconscious→Immune) are left for future work — they're lower priority and partially implicit already.

### Motor→Conscious: graph cycle with retry gate

When motor.repair_check() fails, the graph routes back to conscious for re-deliberation. Conscious receives the failed motor_output in state and can adjust its strategy. Motor tries again. Max 1 retry (2 total motor attempts per invocation).

Implementation: passthrough node `retry_gate` increments `feedback["motor_retry_count"]`, then edges to conscious. Conditional function `_after_motor` checks: repair_passed == False AND motor_retry_count < 1 AND topology.get_weight("motor", "conscious") > 0.

### Conscious→Sensory: graph cycle with re-examination gate

Conscious can request re-examination by setting `re_examine: True` in its output. Graph routes back to sensory, re-running the signal domain pipeline. Max 1 re-examination.

Implementation: passthrough node `re_examine_gate` increments `feedback["re_examine_count"]`, edges to sensory. Conditional `_after_conscious` checks: re_examine AND re_examine_count < 1 AND topology.get_weight("conscious", "sensory") > 0.

Currently MockDeliberator always sets re_examine=False — the path is wired but dormant until a deliberator learns to use it.

### Conscious→Immune: state propagation

Conscious writes threshold adjustments to `feedback["immune_threshold_adjustments"]`. Immune reads these and applies as deltas to innate thresholds. In the current pipeline, immune runs before conscious, so adjustments take effect on re-examination loops or next invocation. This is architecturally correct.

### FeedbackSignals TypedDict

```python
class FeedbackSignals(TypedDict):
    motor_retry_count: int
    re_examine_count: int
    immune_threshold_adjustments: dict[str, float]
```

Added to SystemState as `feedback: FeedbackSignals | None`. GraphState gets `feedback: Any`.

### ConsciousOutput gets re_examine field

All output builders set `re_examine: False` by default. MockDeliberator updated to include it.

### Topology weight consultation is binary gating

Conditional functions check `topology.get_weight(source, target) > 0`. Binary: path fires or doesn't. Weight modulation is Phase 4. If weight is set to 0.0 by sleep (future), the feedback path disables.

### Rejected: full topology-driven graph building

Topology has connections (sleep→all, genetic→all) that aren't graph routing. Primary connections stay as hardcoded edges. Secondary connections use topology weights in conditional functions.

## Observations

### Pipeline becomes network

Current graph is a tree with one branch point (escalation). With feedback, it gains two cycles: motor→conscious (retry) and conscious→sensory (re-examine). This is the Phase 3 transition from pipeline to network.

### Cross-cycle state is new

Immune threshold adjustments are the first state that carries meaning across invocations. Application layer must persist and forward feedback state.

### Gate nodes are LangGraph pattern for state mutation at routing boundaries

LangGraph conditional functions can't modify state — they only return route names. Passthrough gate nodes handle state mutation before routing.

## What to Watch

### ConsciousOutput re_examine backward compatibility
TypedDict is structural — missing keys don't error at runtime. But tests constructing ConsciousOutput manually need updating. Also MockDeliberator in deliberator.py must include it.

### _make_sample_state needs feedback: None
Same pattern as genetic_output in D018.

### graph.py imports topology
New import: `from agenetic.network.topology import get_weight`. Verify no circular imports.

### Immune threshold key names
Must match immune.py's inline thresholds: "entropy_threshold" (6.0), "noise_floor_threshold" (0.35), "impedance_threshold" (0.5), "deviation_threshold" (3.0), "vocabulary_threshold" (0.1), "adaptive_match_threshold" (0.5).

### Gate nodes don't appear in routing_history
Gate functions don't use _make_node (which records routing). Existing tests checking routing_history won't break.

### Existing test_integration.py and test_graph.py
Tests verify specific routing paths. Motor→END is now Motor→conditional. Tests need updating for the new conditional but should still pass if motor succeeds (the default case routes to END).
