# Planning State — Directive 016: Audit Remediation

## Decision Record

### Triage from Conceptual Audit

The audit (015) produced 10 recommendations across three priority tiers. This directive addresses 6 of them (the must-fix and should-fix items). Three findings are deferred because they require sleep implementation or structural motor redesign — both are architectural changes beyond remediation scope.

**Addressed:**
1. Subconscious cache pruning — must-fix, deployment hazard
2. Escalation flag preservation — must-fix, broken connection
3. Immune escalation — must-fix, dead code
4. Feature vector normalization — should-fix, matching quality
5. Ārēka threshold documentation — should-fix, undocumented design decision
6. Māyāvāda inversion — should-fix, semantically backwards

**Deferred:**
- Tautological confirmation (Finding 1): Needs motor strategies at different structural level than sensory measurement. This is a design rethink, not a fix.
- Dormant gate (Finding 2): Conscious suppression paths require limb weights > 0.5. Only sleep can modify weights. Sleep is a stub. Gate value is prospective until sleep exists.
- Convergent cluster (Finding 3): Five limbs individually inert. Same dependency on sleep for weight modification.

### Design Decisions

**Cache pruning strategy:** LRU-style, prune entries with encounter_count=1 and age > 100 ticks. Conservative — only removes patterns seen exactly once that are stale. Reinforced patterns survive regardless of age. This is independent of sleep; sleep can later implement more sophisticated consolidation.

**Flag preservation:** OR-logic instead of unconditional set. This is the standard pattern for flag propagation in a pipeline — any upstream system can raise the flag, downstream systems can add but not remove. The D014 explicit-False-in-else-branch was defense-in-depth for single invocations, but the audit correctly identified it as erasing upstream signals.

**Immune escalation via flag, not threat_action:** The conscious gate checks threat_action=="escalate" but nobody produces that value. Rather than adding a new threat_action value, we use the existing escalation flag. This is cleaner — the flag is the routing mechanism, threat_action is the immune's output classification. The dead code checking threat_action=="escalate" gets removed.

**Ārēka as defense-in-depth:** The 0.3/0.7 split IS intentional. Codec (0.3) is the outer gate — final chance to suppress, more cautious. Conscious (0.7) is the inner gate — suppressing an LLM call is a stronger action. Documenting this makes the design legible.

**Māyāvāda fix:** Only the activation condition is inverted, not the formula. `max_allowed = 1.0 - w` is correct (high weight = low cap = more restraint). The bug is `< 0.45` should be `> 0.55`.

### Test Strategy

~24 new tests across three test files. No new test files — all additions to existing test modules. Integration tests re-verified after flag logic changes.

## Observations

- The audit correctly identified the most pressing issues. The subconscious time bomb and escalation flag overwrite are genuine deployment hazards.
- The Māyāvāda inversion is a sign that threshold-heavy code needs better inline documentation of semantic direction. Future directives should include "semantic check: does higher weight produce the effect the limb name implies?"
- Feature normalization is a straightforward fix but reveals a broader question: should the subconscious matching distance metric be configurable? Deferred for now.
- After this directive, the next major work is sleep implementation (audit recommendation #8), which unblocks the dormant gate and convergent cluster findings.

## Roadmap

011 ✓ Conscious layer foundation. 262 tests.
012 ✓ Prompt assembly refinement. 292 tests.
013 ✓ Motor codec refactor. 304 tests.
014 ✓ Integration wiring. 320 tests.
015 ✓ Full audit phase (mechanical + conceptual).
015a ✓ Audit artifact cleanup.
016 — **This directive.** Audit remediation. ~344 tests expected.
017 — Sleep implementation (first meta-domain system). Unblocks dormant gate + convergent cluster.
