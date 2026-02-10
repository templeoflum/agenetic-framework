# 014 — Integration: Conditional Escalation, Conscious-Motor Wiring

Date: 2026-02-10
Directive type: Integration (wiring existing systems, behavior changes)

## What This Directive Does

Closes three structural gaps that kept the systems isolated despite being individually complete:

1. **Routing default flip.** One line: `escalate_to_conscious=False`. Subconscious now drives escalation instead of everything always escalating. This activates the conditional routing that was already built into the graph.

2. **Conscious-motor wiring.** Motor now checks conscious_output. If conscious suppressed (proceed=False), motor produces empty output. If conscious proceeded, motor records the strategy as metadata. Motor's text restructuring behavior is unchanged — it still delegates to TextCodec with the same logic. The integration is suppression-awareness and metadata, not semantic rendering.

3. **End-to-end path tests.** Three paths verified through the full graph: reflex (subconscious → motor, no conscious), escalated (subconscious → conscious → motor), and suppression (conscious gate says no → motor suppresses).

## Design Decisions and Rationale

### Why not semantic rendering in motor?

Motor could theoretically adjust its restructuring based on conscious strategy (e.g., "trace_contradiction" → boost entropy modulation, "minimal_reflection" → boost resting stance). This is tempting but premature. The audit (015–016) needs to evaluate whether prompt assembly produces genuine behavioral differences BEFORE motor starts acting on those decisions. If conscious output turns out to be theater (the audit's key question), then motor rendering of that theater compounds the problem.

Motor records the strategy as metadata. If the audit validates conscious output as genuine, a future directive can add strategy-influenced modulation. For now: suppress/proceed binary + metadata recording.

### Subconscious explicit flag reset — defense in depth

Subconscious previously only set `escalate_to_conscious=True`, never False. With the default now False, the "never sets False" behavior is technically fine for single invocations. But if the graph is invoked multiple times with state carried forward (which the architecture allows), a stale True flag from a previous cycle could cause spurious escalation. Explicit reset prevents this.

### Test fixing strategy — explicit over implicit

Tests broken by the default change are fixed by adding `state["flags"]["escalate_to_conscious"] = True`. Not by restoring the old default. This makes each test declare which path it's testing. Explicit is better than implicit — the old default was hiding that every test implicitly tested the escalated path.

### 16 integration tests — four groups

- **Reflex (4):** Subconscious doesn't escalate, motor processes directly. Verifies the path exists and works.
- **Escalated (4):** Subconscious escalates, conscious deliberates, motor receives output. Verifies the full pipeline.
- **Suppression (3):** Conscious gate suppresses, motor produces empty. Verifies suppression propagates.
- **Cross-path (2) + routing (3):** Structural invariants that hold regardless of path. Default routing is reflex. Threat triggers escalation. Familiar patterns stay reflex.

## Broader Roadmap (011–017)

011 ✓ ConsciousOutput type, gate, Deliberator protocol. 262 tests.
012 ✓ Prompt assembly refinement. Graduated intensity, limb interactions. 292 tests.
013 ✓ Motor codec refactor. TextCodec extraction. 304 tests.
014 — **This directive.** Integration wiring. Conditional escalation, conscious-motor, end-to-end paths.
015 — Mechanical audit. DNAgent reads everything, reports raw. Zero code changes.
016 — Conceptual audit. Fresh planning instance, adversarial posture.
017 — Remediation.

## What to Watch

- **Test breakage from default flip.** The single most likely issue. Every graph test that doesn't explicitly set the escalation flag will now take the reflex path. If a test expects conscious output but doesn't set the flag, it fails. The fix is always the same one line.

- **Subconscious escalation sensitivity.** With default False, the actual escalation logic in subconscious matters. Current thresholds: threat_level medium/high/critical → escalate; novel signal with aggregate_dev > 1.5 → escalate; past patterns with more escalated outcomes → escalate. Inputs with low deviation and no threat stay reflex. The integration tests need inputs that actually trigger these conditions.

- **Motor suppression vs Ārēka suppression.** Motor now has TWO suppression paths: conscious suppression (new, this directive) and Ārēka suppression (existing, in TextCodec). They're not conflicting — conscious suppression fires BEFORE codec delegation, Ārēka suppression fires INSIDE the codec. If conscious suppresses, Ārēka never gets to check. If conscious proceeds, Ārēka might still suppress at the codec level. Both record different strategy strings.
