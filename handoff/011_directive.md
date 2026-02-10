# Directive 011 — Conscious Layer Foundation: Output Contract, Proceed/Suppress Gate, Deliberator Protocol

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-09

## Context

Read these files first, in this order:
1. `planning/CURRENT.md` — factual snapshot of where things stand
2. `CLAUDE.md` — project conventions, agent roles, directive protocol
3. `docs/ARCHITECTURE.md` — the v2 specification (especially Calibration Validity, Engineering Assignments, and the Conscious Layer section)
4. `docs/architecture_amendment.md` — the signal-semantics boundary
5. `handoff/009_conceptual_audit_report.md` — adversarial audit of the entire codebase
6. `planning/010_audit_remediation.md` — what was fixed after the audit
7. `references/asparsa_limbs.md` — the 18 limb principles
8. `references/conceptual_archaeology.md` — Section V, limb-to-feature mapping (especially Signal vs Semantic domain assignments)

**What happened before this directive:**

The signal domain is complete and audited. 238 tests passing. 7 signal features (density, entropy, coherence, periodicity, noise_floor, impedance, bigram_entropy), 10 motor strategies, 5-input calibration surface, per-feature delta computation with shared target profiles in base.py. The audit established that signal-level calibration validates plumbing (verified connections), not semantic meaning. Tarka is definitively semantic-domain for typical input. 5 limbs form a convergent cluster indistinguishable at signal level (Bodhi, Mirror, Ajāti, Asparśa-Yoga, Rest as Realization). 3 limbs are content-focused and require semantic processing (Vishvarūpa, No-Position, Fourfold State). Ātma-Vichāra is uncategorized — lineage tracking, cross-cutting concern.

**What this directive does:**

This is the first implementation of the conscious layer — the system's crossing from signal domain into semantic domain. The conscious layer is the first and only system that constructs meaning. It replaces the current pass-through stub with three foundational components:

1. **ConsciousOutput type** — the contract between deliberation and expression. Medium-independent: describes *what to communicate and how to frame it*, not the final text/audio/visual output. Motor's job is rendering this into a specific medium.

2. **Proceed/suppress gate** — the first decision conscious makes, before any LLM call. Evaluates whether the input warrants engagement based on signal data + field state. This is where Nivṛtti (sacred pause), Ārēka (inviolable silence), and the convergent cluster (resting stance) express at semantic level. Pure Python, no LLM, deterministic.

3. **Deliberator protocol** — the abstraction between conscious (which owns framing) and the LLM engine (which is swappable). First implementation uses the Anthropic API. The protocol is the extensibility point for local models, Claude Code native context, or any other LLM backend.

**Key design decisions (rationale follows each):**

- **Conscious produces structured semantic intention, not text.** Motor handles rendering into specific media. This enables multi-modal output (text, audio, visual, tool-use) without conscious being text-specific. `ConsciousOutput` is the contract.

- **The proceed/suppress gate fires before any LLM call.** Cost optimization: if signal data + field state says "don't engage," zero tokens are spent. The gate is the reducing valve's final filter.

- **Limb expression happens in prompt assembly, not output evaluation.** Field state shapes what the LLM sees and how it's framed. No second LLM call to judge output quality. Trust the framing. The signal domain provides lightweight quality checks on the way out (motor's text strategies already operate on sensory-like features).

- **Ātma-Vichāra is structural, not modulated.** Every ConsciousOutput carries lineage metadata: what signal data triggered deliberation, what field state shaped it, what escalation path led here. The weight may later modulate visibility of lineage in final output, but lineage itself is always produced.

- **The convergent cluster is a composite resting stance.** Bodhi (12), Mirror (15), Ajāti (17), Asparśa-Yoga (18), Rest as Realization (14) — five limbs describing facets of the same orientation: reflect without internalizing, echo without claiming origin, observe without engaging. Treated as one behavioral dimension (mean of the five weights) that modulates how "present" the system is in its own output. High composite = recede. Low composite = project.

- **The Deliberator protocol uses Python's Protocol (structural typing), not ABC.** Any object with the right method signature is a Deliberator. This keeps the abstraction lightweight and doesn't force inheritance on future implementations.

## Objective

Replace the conscious stub with a foundational implementation: define the `ConsciousOutput` contract, implement the proceed/suppress gate (pure Python, no LLM), define the `Deliberator` protocol, build a first Anthropic API-backed deliberator, and wire them into `ConsciousSystem.process()`. The system should fire on escalation (as currently routed), evaluate the gate, and if proceeding, make one LLM call through the Deliberator to produce a structured `ConsciousOutput`. Tests should cover the gate logic deterministically and the Deliberator protocol via mock.

## Part A: Type Definitions

### A1: ConsciousOutput TypedDict in base.py

Add to `src/agenetic/systems/base.py`:

```python
class ResponseDecision(TypedDict):
    """What to communicate — medium-independent semantic intention."""
    intent: str  # Core message/action to express (semantic, not literal text)
    strategy: str  # How to approach expression (e.g., "trace_contradiction", "preserve_ambiguity", "direct_response", "threshold_acknowledgment")
    constraints: list[str]  # Behavioral constraints from active limbs (e.g., ["hold_contradictions_open", "no_false_certainty"])

class ExpressionDirectives(TypedDict):
    """How to render the response — field-derived behavioral parameters."""
    field_weights: dict[str, float]  # Snapshot of all 18 limb weights at deliberation time
    active_limbs: list[str]  # Limbs with weight significantly above/below 0.5 (±0.1 threshold)
    resting_stance: float  # Convergent cluster composite (mean of limbs 12, 14, 15, 17, 18)
    suppress_identity: bool  # No-Position (limb 13) active: avoid self-referential framing
    state_awareness: str  # Fourfold State (limb 16): "active", "reflective", "consolidated", or "still"

class Lineage(TypedDict):
    """Ātma-Vichāra — provenance tracking. Always present, never optional."""
    escalation_reason: str  # Why subconscious escalated (e.g., "novel_input", "high_deviation", "immune_override")
    signal_summary: dict  # Compressed signal report (features + deltas, not the full report)
    field_snapshot: dict[str, float]  # Limb weights at deliberation time
    gate_evaluation: dict  # What the proceed/suppress gate considered and decided
    deliberation_model: str  # Which LLM backend produced the deliberation (e.g., "anthropic:claude-sonnet-4-20250514")

class ConsciousOutput(TypedDict):
    """Output contract for the conscious layer — the semantic domain's product.

    Medium-independent: describes intention and framing, not final rendered output.
    Motor receives this and renders it through the active codec for the target medium.
    """
    decision: ResponseDecision
    expression: ExpressionDirectives
    lineage: Lineage
    proceed: bool  # Gate result: True = respond, False = suppress (sacred pause)
    confidence: float  # 0.0–1.0, deliberation confidence. Below threshold → apoptotic
```

Also add `conscious_output: ConsciousOutput | None` to the `SystemState` TypedDict (alongside the existing `motor_output`, `signal_report`, etc.).

Also add `conscious_output` to `GraphState` in `src/agenetic/network/graph.py` as `conscious_output: Any  # ConsciousOutput | None` and include it in `create_default_state()` as `"conscious_output": None`, and in `_make_node()`'s `full_state` construction as `"conscious_output": state.get("conscious_output")`.

### A2: Limb ID constants needed

The following limb ID constants should already exist in `base.py` from Directive 010 (verify). If any are missing, add them:

```python
# Convergent cluster limbs (resting stance composite)
BODHI_ID = 12
REST_AS_REALIZATION_ID = 14
MIRROR_ID = 15
AJATI_ID = 17
ASPARSA_YOGA_ID = 18

# Semantic-domain limbs (conscious layer)
TARKA_ID = 2       # Already exists (entropy/contradiction)
NIVRTTI_ID = 3     # Already exists (sacred pause / impedance)
AREKA_ID = 8       # Already exists (inviolable silence)
SVADHARMA_ID = 9   # Already exists (context-appropriate response)
KSETRA_JNANA_ID = 10  # Already exists (positional awareness)
VISHVARUPA_ID = 11 # Point to the infinite, don't impersonate
NO_POSITION_ID = 13  # Avoid anchoring in identity
FOURFOLD_STATE_ID = 16  # State-aware processing
SRADDHA_ID = 5     # Already exists (mystery preservation)
ATMA_VICHARA_ID = 6  # Already exists (recursive self-inquiry / lineage)
```

## Part B: Proceed/Suppress Gate

### B1: Gate Implementation in conscious.py

The gate is a pure Python function (no LLM call) that evaluates whether the input warrants conscious engagement. It fires BEFORE any Deliberator call. If the gate suppresses, `ConsciousOutput.proceed` is False and no LLM tokens are spent.

Implement as a private method `_evaluate_gate(self, state: SystemState) -> dict` in `ConsciousSystem` that returns a gate evaluation dict with the decision and reasoning.

**Gate inputs:**
- Signal report: `state["signal_report"]` (features, deltas, classification, aggregate_deviation)
- Threat assessment: `state["threat_assessment"]` (threat_level, action)
- Field state: `state["field"]` (all 18 limb weights)
- Subconscious output: `state["subconscious_output"]` (escalation_reason, cached patterns)

**Gate logic (evaluate in this order, first match wins):**

1. **Immune override — always proceed.** If `threat_assessment` action is `"escalate"`, the gate always proceeds. The immune system escalated for a reason; suppressing it would undermine boundary enforcement.

2. **Ārēka suppression.** Read limb 8 (Ārēka) weight. If weight > 0.7 AND the signal report's classification is `"noise"`, suppress. "Some things must not be spoken" — but only for genuinely noisy input, not for everything. This is the semantic-level equivalent of the motor's Ārēka gate but with a higher threshold (motor fires at 0.3) because suppressing a response entirely is a stronger action than suppressing motor output.

3. **Nivṛtti pause.** Read limb 3 (Nivṛtti) weight. If weight > 0.7 AND aggregate_deviation < 0.5, suppress. High Nivṛtti + low deviation = "this input doesn't require engagement, and the field says honor sacred pause." Low deviation alone doesn't suppress (the input might still need a response). High Nivṛtti alone doesn't suppress (the input might be urgent).

4. **Resting stance.** Compute convergent cluster composite: mean of weights for limbs 12, 14, 15, 17, 18. If composite > 0.8 AND aggregate_deviation < 0.3, suppress. Very high resting stance + very low signal deviation = the system is in deep rest and the input barely registers. This is the most conservative suppression — it requires both extreme field configuration and minimal input.

5. **Default — proceed.** If none of the above triggered, the gate proceeds.

The gate evaluation dict should record:
```python
{
    "proceed": bool,
    "reason": str,  # Which rule triggered, or "default_proceed"
    "areka_weight": float,
    "nivrtti_weight": float,
    "resting_stance_composite": float,
    "aggregate_deviation": float,
    "signal_classification": str,
    "threat_action": str,
}
```

### B2: Gate produces minimal ConsciousOutput on suppression

When the gate suppresses, `ConsciousSystem.process()` should still produce a full `ConsciousOutput` (not None), but with `proceed=False` and a minimal decision:

```python
ConsciousOutput(
    decision=ResponseDecision(
        intent="suppress",
        strategy="sacred_pause",
        constraints=[],
    ),
    expression=ExpressionDirectives(
        field_weights={...},  # Current field snapshot
        active_limbs=[...],   # Computed from field
        resting_stance=...,   # Computed composite
        suppress_identity=...,
        state_awareness=...,
    ),
    lineage=Lineage(
        escalation_reason=...,  # From subconscious_output
        signal_summary={...},   # Compressed from signal_report
        field_snapshot={...},
        gate_evaluation={...},  # The full gate eval dict
        deliberation_model="none",  # No LLM was called
    ),
    proceed=False,
    confidence=1.0,  # Suppression is a confident decision
)
```

## Part C: Deliberator Protocol

### C1: Protocol Definition

Create a new file `src/agenetic/systems/deliberator.py`:

```python
"""Deliberator protocol — the abstraction between conscious framing and LLM engine.

The conscious layer owns what the LLM sees (prompt assembly from compressed state)
and how the response is structured (parsed into ConsciousOutput). The engine behind
the protocol is swappable: Anthropic API, local models, Claude Code native context.

The protocol uses Python's Protocol (structural typing) rather than ABC. Any object
with the right method signatures is a Deliberator. No inheritance required.
"""

from typing import Protocol, Any, runtime_checkable

from agenetic.systems.base import ConsciousOutput, SystemState


class DeliberationRequest:
    """Structured input to a Deliberator — what the LLM should reason about.

    Assembled by the conscious layer from compressed signal state + field.
    The Deliberator implementation translates this into whatever format
    its backend expects (messages API, local model prompt, etc.)."""

    def __init__(
        self,
        input_text: str,
        signal_summary: dict,
        threat_summary: dict,
        subconscious_summary: dict,
        field_state: dict[str, float],
        active_limbs: list[dict],
        resting_stance: float,
        expression_directives: dict,
    ):
        self.input_text = input_text
        self.signal_summary = signal_summary
        self.threat_summary = threat_summary
        self.subconscious_summary = subconscious_summary
        self.field_state = field_state
        self.active_limbs = active_limbs
        self.resting_stance = resting_stance
        self.expression_directives = expression_directives


@runtime_checkable
class Deliberator(Protocol):
    """Protocol for LLM backends that perform conscious deliberation.

    Any object implementing deliberate() with the right signature is a Deliberator.
    No inheritance required — structural typing via Protocol.
    """

    def deliberate(self, request: DeliberationRequest) -> ConsciousOutput:
        """Perform deliberation and return structured conscious output.

        The implementation is responsible for:
        1. Translating the DeliberationRequest into its backend's format
        2. Making the LLM call (or equivalent)
        3. Parsing the response into ConsciousOutput

        Must set lineage.deliberation_model to identify which backend was used.
        """
        ...
```

### C2: Mock Deliberator for Testing

In the same file or in a test helper, provide a `MockDeliberator` that returns deterministic `ConsciousOutput` without making any API calls. This is essential for testing the conscious system without requiring API credentials.

```python
class MockDeliberator:
    """Deterministic deliberator for testing. No API calls."""

    def __init__(self, default_strategy: str = "direct_response"):
        self.default_strategy = default_strategy
        self.call_count = 0
        self.last_request: DeliberationRequest | None = None

    def deliberate(self, request: DeliberationRequest) -> ConsciousOutput:
        self.call_count += 1
        self.last_request = request

        # Build deterministic output from request
        return {
            "decision": {
                "intent": f"respond_to_{request.signal_summary.get('classification', 'unknown')}",
                "strategy": self.default_strategy,
                "constraints": [limb["name"] for limb in request.active_limbs],
            },
            "expression": {
                "field_weights": request.field_state,
                "active_limbs": [limb["name"] for limb in request.active_limbs],
                "resting_stance": request.resting_stance,
                "suppress_identity": any(
                    limb["id"] == 13 and limb["weight"] > 0.6
                    for limb in request.active_limbs
                ),
                "state_awareness": "active",
            },
            "lineage": {
                "escalation_reason": request.subconscious_summary.get("escalation_reason", "unknown"),
                "signal_summary": request.signal_summary,
                "field_snapshot": request.field_state,
                "gate_evaluation": {"proceed": True, "reason": "default_proceed"},
                "deliberation_model": "mock",
            },
            "proceed": True,
            "confidence": 0.8,
        }
```

### C3: Anthropic API Deliberator (First Real Implementation)

Create `src/agenetic/systems/deliberator_anthropic.py`:

This is the first real Deliberator that makes an actual LLM call. It should:

1. **Import `anthropic`** (the `anthropic` Python package). Add `anthropic` to `pyproject.toml` dependencies.

2. **Translate `DeliberationRequest` into a system prompt + user message.** The system prompt encodes the field state as behavioral framing. The user message presents the signal summary and the original input text.

3. **System prompt construction** — this is where semantic limb expression happens. For each active limb (weight significantly above or below 0.5), include a behavioral instruction derived from the limb's meaning. Use the limb descriptions from `references/asparsa_limbs.md`. Examples:
   - Tarka (limb 2) active high: "When you encounter contradictions, trace them rather than resolving them. Hold tension open."
   - Tarka (limb 2) active low: "Seek resolution and clarity. Contradictions should be resolved where possible."
   - Śraddhā (limb 5) active high: "Where no clear interpretation exists, preserve the ambiguity. Do not manufacture false certainty."
   - Vishvarūpa (limb 11) active high: "If the input exceeds your modeling capacity, acknowledge the threshold. Point to what lies beyond rather than fabricating completeness."
   - No-Position (limb 13) active high: "Avoid self-referential framing. Do not anchor the response in identity claims."
   - Fourfold State (limb 16): Include awareness of system state (active processing, reflection, consolidated, still).
   - Resting stance composite high: "Respond minimally. Recede. Let the response be as brief as alignment permits."

4. **Make one API call** using `anthropic.Anthropic().messages.create()`. Use model `claude-sonnet-4-20250514` (cost-efficient for deliberation). Set `max_tokens` to 1024.

5. **Request structured output.** The user message should end with an instruction to respond in a specific format that can be parsed into `ConsciousOutput`. Use a simple structured format — ask the LLM to respond with clearly delimited sections for intent, strategy, constraints, and confidence. Parse the response text into the `ConsciousOutput` TypedDict.

6. **Handle parse failures gracefully.** If the response can't be parsed into the expected structure, produce a fallback `ConsciousOutput` with `strategy="parse_fallback"`, the raw response text in `intent`, and `confidence=0.3`.

7. **Set `lineage.deliberation_model`** to `f"anthropic:{model_name}"`.

8. **The API key** should be read from environment variable `ANTHROPIC_API_KEY`. If not set, raise a clear error at initialization time (not at call time).

**Important:** The Anthropic deliberator is for testing the pipeline. During normal development with Claude Code, the conscious layer's "deliberation" is happening in the planning instance / agent context itself. The API deliberator proves the abstraction works and enables CI testing. It is NOT the primary production path — it's the first swappable backend.

## Part D: Conscious System Integration

### D1: Replace the Stub

Replace the body of `ConsciousSystem` in `src/agenetic/systems/conscious.py`. The class must:

1. **Accept a `Deliberator` in `__init__`.** Store it as `self.deliberator`. If None is passed, the system operates in gate-only mode (evaluates the gate, produces suppression output if gate suppresses, but cannot proceed because there's no deliberator to call — treat missing deliberator + proceed gate as a degraded state).

2. **`process(state) -> SystemState`:**
   - Extract signal_report, threat_assessment, subconscious_output, field from state
   - If any required upstream data is missing (signal_report is None), return state unchanged with a degradation flag (conscious can't deliberate without signal data)
   - Compute active limbs (weight > 0.6 or < 0.4 — i.e., ±0.1 from midpoint 0.5)
   - Compute resting stance composite (mean of limbs 12, 14, 15, 17, 18)
   - Compute expression directives (field snapshot, active limbs, resting stance, No-Position check, Fourfold State)
   - Evaluate proceed/suppress gate via `_evaluate_gate(state)`
   - If gate suppresses: produce suppression ConsciousOutput, write to state["conscious_output"], return
   - If gate proceeds AND deliberator is available: build DeliberationRequest, call `self.deliberator.deliberate(request)`, write result to state["conscious_output"]
   - If gate proceeds AND deliberator is None: produce degraded ConsciousOutput (proceed=True, confidence=0.0, strategy="no_deliberator"), add "conscious" to degraded flags

3. **`repair_check(state) -> bool`:**
   - If conscious_output is None: fail (should always produce output when fired)
   - If conscious_output["proceed"] is True and confidence < 0.1: fail (arbitrary output)
   - If conscious_output["lineage"] is missing any required fields: fail (Ātma-Vichāra structural requirement)
   - Otherwise: pass

4. **`apoptotic_condition(state) -> bool`:**
   - Track consecutive low-confidence deliberations (confidence < 0.2) via state metadata
   - If 3+ consecutive low-confidence results: apoptotic (reasoning has collapsed)
   - Implementation: store count in metadata under key "conscious_low_confidence_streak"

5. **Keep `tick_rate` as `"on_escalation"`** — unchanged from stub.

6. **Read-only field access.** Conscious reads `state["field"]` but never writes to it. This constraint is unchanged from all non-sleep systems.

### D2: Helper Methods

Implement these as private methods on `ConsciousSystem`:

- `_compute_active_limbs(field: dict) -> list[dict]`: Returns list of `{"id": int, "name": str, "weight": float}` for limbs with weight outside 0.4–0.6 range.
- `_compute_resting_stance(field: dict) -> float`: Mean of weights for limbs 12, 14, 15, 17, 18.
- `_compute_expression_directives(field: dict, active_limbs: list) -> ExpressionDirectives`: Assembles the full expression directives from field state.
- `_build_deliberation_request(state: SystemState, active_limbs: list, resting_stance: float, expression: ExpressionDirectives) -> DeliberationRequest`: Assembles the request from compressed state.
- `_compress_signal_report(signal_report: dict) -> dict`: Extracts the essential features and deltas from the full signal report for lineage. Drop the raw input hash.

## Part E: Tests

### E1: Gate Tests (deterministic, no LLM)

Create test functions in `tests/test_conscious.py`. All gate tests use `ConsciousSystem(deliberator=None)` and craft specific state configurations:

1. **test_gate_immune_override_always_proceeds**: Set threat_assessment action to "escalate". Gate should proceed regardless of other weights.
2. **test_gate_areka_suppresses_noise**: Set Ārēka weight to 0.8, signal classification to "noise". Gate should suppress.
3. **test_gate_areka_permits_non_noise**: Set Ārēka weight to 0.8, signal classification to "steady_state". Gate should proceed (Ārēka only suppresses noise).
4. **test_gate_nivrtti_suppresses_low_deviation**: Set Nivṛtti weight to 0.8, aggregate_deviation to 0.3. Gate should suppress.
5. **test_gate_nivrtti_permits_high_deviation**: Set Nivṛtti weight to 0.8, aggregate_deviation to 1.0. Gate should proceed (input needs attention despite pause preference).
6. **test_gate_resting_stance_suppresses**: Set all convergent cluster limbs to 0.9, aggregate_deviation to 0.2. Gate should suppress.
7. **test_gate_resting_stance_permits_deviation**: Set all convergent cluster limbs to 0.9, aggregate_deviation to 1.0. Gate should proceed.
8. **test_gate_default_proceeds**: All weights at 0.5, normal signal report. Gate should proceed.
9. **test_gate_priority_order**: Set conditions for both Ārēka suppression AND immune override. Immune override should win (it's checked first).

### E2: ConsciousOutput Structure Tests

10. **test_suppression_output_complete**: After gate suppresses, verify ConsciousOutput has all required fields, proceed=False, lineage present with gate_evaluation.
11. **test_lineage_always_present**: For both proceed and suppress paths, verify lineage has all required fields (Ātma-Vichāra structural requirement).
12. **test_no_deliberator_degrades**: ConsciousSystem with deliberator=None, gate proceeds, system should produce degraded output and flag degradation.

### E3: Deliberator Protocol Tests

13. **test_mock_deliberator_satisfies_protocol**: Verify `isinstance(MockDeliberator(), Deliberator)` is True (runtime_checkable).
14. **test_mock_deliberator_returns_valid_output**: Call MockDeliberator.deliberate() with a crafted request. Verify output has all ConsciousOutput fields.
15. **test_deliberator_call_count**: Verify MockDeliberator tracks call count correctly.

### E4: Integration Tests (with MockDeliberator)

16. **test_conscious_full_proceed_path**: ConsciousSystem with MockDeliberator, normal escalated state. Should evaluate gate (proceed), call deliberator, produce ConsciousOutput with proceed=True.
17. **test_conscious_full_suppress_path**: ConsciousSystem with MockDeliberator, Ārēka=0.9 + noise classification. Should evaluate gate (suppress), NOT call deliberator (verify call_count=0), produce ConsciousOutput with proceed=False.
18. **test_conscious_missing_signal_report**: State with signal_report=None. Should return state with degradation flag, no ConsciousOutput.
19. **test_conscious_repair_check_passes**: Normal ConsciousOutput with confidence > 0.1, all lineage fields present.
20. **test_conscious_repair_check_fails_low_confidence**: ConsciousOutput with proceed=True, confidence=0.05. Repair should fail.
21. **test_conscious_repair_check_fails_missing_lineage**: ConsciousOutput with incomplete lineage. Repair should fail.
22. **test_conscious_apoptotic_after_streak**: Simulate 3 consecutive low-confidence deliberations. Apoptotic should trigger.

### E5: Parametrized Interface Tests

The existing parametrized tests in `test_systems.py` that test all 7 systems already cover ConsciousSystem's basic interface (process returns SystemState, repair_check returns bool, etc.). These should continue to pass. The stub state construction helper `_make_sample_state` in test_systems.py needs updating to include `conscious_output: None`.

### E6: Graph Integration Test

23. **test_graph_conscious_output_flows_to_motor**: Build full graph with real signal-domain systems + ConsciousSystem(MockDeliberator) + real MotorSystem. Run an escalated input through. Verify conscious_output is present in state after conscious fires, and motor receives it. Motor doesn't need to USE conscious_output yet (that's Directive 014) — just verify it's in state.

### E7: Anthropic API Test (Optional — requires credentials)

24. **test_anthropic_deliberator_real_call**: Mark with `@pytest.mark.skipif(not os.environ.get("ANTHROPIC_API_KEY"), reason="No API key")`. Make one real API call through the Anthropic deliberator. Verify the response parses into a valid ConsciousOutput. This test should NOT run in CI by default — it requires credentials and costs tokens.

## Part F: Planning State Management

### F1: Copy State to Planning Entry

Copy `handoff/state.md` to `planning/011_conscious_foundation.md`. This is the permanent numbered planning entry for this directive cycle. Never overwrite previous planning entries.

### F2: Update CURRENT.md from Repo Inspection

After all code changes are complete and tests pass, update `planning/CURRENT.md` by inspecting the actual repo state. Include: new test count, conscious system status change (stub → foundation), new files created, any changes to system status table. Do NOT copy from old CURRENT.md — rebuild from ground truth.

## Part G: Documentation Updates

### G1: DEVLOG Entry

Add entry for Directive 011. Format: date, directive number, commit hash (fill in), test count (fill in), prose summary.

### G2: README Status Update

Update README.md system status: Conscious should change from "Stub (pass-through)" to "Foundation (gate + deliberator protocol, LLM-backed deliberation)".

## Scope Boundaries

**DO:**
- Replace the conscious stub with the gate + deliberator implementation
- Add ConsciousOutput and related types to base.py
- Create deliberator.py (protocol + mock)
- Create deliberator_anthropic.py (first real implementation)
- Add conscious_output to SystemState and GraphState
- Create test_conscious.py with all specified tests
- Update _make_sample_state in test_systems.py to include conscious_output
- Add `anthropic` to pyproject.toml dependencies
- Update DEVLOG.md, README.md, CURRENT.md

**DO NOT:**
- Modify sensory.py, immune.py, subconscious.py, or motor.py implementations
- Modify the orientational field
- Change graph routing logic (conscious is already wired in the graph)
- Make motor consume ConsciousOutput (that's Directive 014)
- Build prompt assembly logic for ALL 18 limbs — only build what the Anthropic deliberator needs for a working first implementation. Prompt assembly refinement is Directive 012.
- Edit any historical handoff files (001-010)
- Attempt to build non-text codecs for motor
- Add sleep or genetic implementation
- Modify connection weights or topology

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/base.py` | Updated — ConsciousOutput, ResponseDecision, ExpressionDirectives, Lineage types added; conscious_output added to SystemState |
| `src/agenetic/systems/conscious.py` | Replaced — full gate + deliberator implementation |
| `src/agenetic/systems/deliberator.py` | Created — Deliberator protocol, DeliberationRequest, MockDeliberator |
| `src/agenetic/systems/deliberator_anthropic.py` | Created — Anthropic API deliberator |
| `src/agenetic/network/graph.py` | Updated — conscious_output added to GraphState and create_default_state |
| `tests/test_conscious.py` | Created — all gate, protocol, integration, and graph tests |
| `tests/test_systems.py` | Updated — _make_sample_state includes conscious_output |
| `pyproject.toml` | Updated — anthropic dependency added |
| `DEVLOG.md` | Updated — Directive 011 entry |
| `README.md` | Updated — Conscious system status |
| `planning/CURRENT.md` | Updated — from repo inspection |
| `handoff/state.md` | Provided — planning notes for this cycle |
| `planning/011_conscious_foundation.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `handoff/011_directive.md` | This file |
| `handoff/011_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `ConsciousOutput`, `ResponseDecision`, `ExpressionDirectives`, `Lineage` TypedDicts exist in base.py
- [ ] `conscious_output` field exists in both `SystemState` and `GraphState`
- [ ] `create_default_state()` includes `conscious_output: None`
- [ ] `_make_node()` passes `conscious_output` through to full_state
- [ ] `ConsciousSystem.__init__` accepts optional `Deliberator`
- [ ] `ConsciousSystem.process()` evaluates gate before any LLM call
- [ ] Gate suppression produces complete `ConsciousOutput` with `proceed=False`
- [ ] Gate respects priority order: immune override > Ārēka > Nivṛtti > resting stance > default
- [ ] `ConsciousSystem.process()` calls `deliberator.deliberate()` only when gate proceeds
- [ ] `ConsciousSystem.repair_check()` verifies lineage completeness
- [ ] `ConsciousSystem.apoptotic_condition()` tracks low-confidence streak
- [ ] `Deliberator` is a `runtime_checkable Protocol`
- [ ] `MockDeliberator` satisfies the `Deliberator` protocol
- [ ] `deliberator_anthropic.py` exists with Anthropic API implementation
- [ ] `anthropic` is in pyproject.toml dependencies
- [ ] All gate tests pass (9 tests)
- [ ] All structure tests pass (3 tests)
- [ ] All protocol tests pass (3 tests)
- [ ] All integration tests pass with MockDeliberator (7 tests)
- [ ] Graph integration test passes (1 test)
- [ ] All 238 existing tests still pass
- [ ] No modifications to sensory.py, immune.py, subconscious.py, or motor.py
- [ ] No modifications to orientational field
- [ ] No historical handoff files edited
- [ ] `handoff/state.md` copied to `planning/011_conscious_foundation.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection (not copied from old version)
- [ ] DEVLOG.md entry added
- [ ] README.md updated
- [ ] CURRENT.md updated from repo inspection
- [ ] Git commit and push completed
