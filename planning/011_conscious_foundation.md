# 011 — Conscious Layer Foundation

Date: 2026-02-09
Directive type: System Implementation (first semantic-domain system)

## What This Directive Does

This is the crossing from signal domain into semantic domain. The conscious layer is the first and only system that constructs meaning — everything upstream compresses raw input into numerical signal reports, and everything downstream renders intentions into output media.

Three foundational components:
1. **ConsciousOutput type** — the contract between deliberation and expression
2. **Proceed/suppress gate** — pure Python, no LLM, fires before any token is spent
3. **Deliberator protocol** — abstraction between framing (conscious owns) and engine (swappable)

## Design Decisions and Rationale

### Conscious produces structured semantic intention, not text

The entire downstream vision is multi-modal output: text, audio, visual, tool-use. If conscious produces text, motor becomes a polishing layer and every future codec has to work with text as intermediate representation. If conscious produces structured intention, motor is genuinely free to render in any medium.

`ConsciousOutput` contains:
- `ResponseDecision` — what to communicate (medium-independent)
- `ExpressionDirectives` — how to frame it (field-derived behavioral parameters)
- `Lineage` — where it came from (Ātma-Vichāra structural requirement)
- `proceed` — gate result
- `confidence` — deliberation quality

### The proceed/suppress gate fires before any LLM call

Cost optimization is the primary design goal of the entire framework. The signal domain is the reducing valve — most inputs should resolve without burning tokens. The gate is the last filter before tokens are spent.

Gate priority order (first match wins):
1. Immune override → always proceed (boundary enforcement overrides silence)
2. Ārēka suppression → high weight + noise classification (sacred silence for genuine noise)
3. Nivṛtti pause → high weight + low deviation (sacred pause when input doesn't warrant engagement)
4. Resting stance → very high composite + very low deviation (deep rest, minimal stimulus)
5. Default → proceed

Thresholds are deliberately conservative. The gate should suppress only when clearly appropriate. False negatives (proceeding when could have suppressed) waste tokens but produce correct output. False positives (suppressing when should have proceeded) lose information.

### Limb expression happens in prompt assembly, not output evaluation

Two options were considered:
- **Prompt-side:** Build system prompt encoding limb weights as behavioral instructions. LLM response naturally expresses limbs. One LLM call.
- **Output-side:** LLM generates response, second LLM call evaluates whether limbs expressed correctly. More verifiable. Two LLM calls.

Chose prompt-side. The cost of a second evaluation call is high, and the recursion problem (who evaluates the evaluator?) is unresolvable. Trust the framing. The signal domain provides lightweight quality checks on output (motor's text strategies already operate on sensory-like features).

### Convergent cluster as composite resting stance

Five limbs (Bodhi, Mirror, Ajāti, Asparśa-Yoga, Rest as Realization) were found indistinguishable at signal level in the 007 analysis and confirmed in the audit. At semantic level, they describe facets of the same orientation: reflect without internalizing, echo without claiming origin, observe without engaging.

Rather than attempting to differentiate five philosophical lenses that produce no measurably different behavior, treat them as one behavioral dimension: the mean of their weights. High composite = system recedes from its own output. Low composite = system projects into output.

This is a testable hypothesis. If the conscious layer can't produce distinguishably different outputs for Bodhi-high vs Ajāti-high (with other cluster members at midpoint), the composite treatment is validated. If it can, the cluster can be decomposed in a later directive.

### Ātma-Vichāra is structural, not modulated

Every `ConsciousOutput` carries lineage: what triggered deliberation, what field state shaped it, what the gate considered, which LLM backend deliberated. This isn't a weight that makes the system more or less self-aware — it's a structural requirement. The system always knows where its outputs came from.

The weight may later modulate how visible lineage is in final rendered output (does the response explain its reasoning to the user?), but the metadata is always produced.

### Deliberator protocol uses structural typing

Python's `Protocol` (PEP 544), not ABC. Any object with a `deliberate(request) -> ConsciousOutput` method is a Deliberator. This keeps the abstraction lightweight and doesn't force inheritance on future implementations. A local model wrapper, a Claude Code native context adapter, or an OpenAI backend all just need the right method signature.

### Motor codec refactor is NOT in this directive

The vision includes motor refactoring into a codec registry (TextCodec, AudioCodec, VisualCodec, etc.). This directive does NOT touch motor. Motor continues operating as-is. The codec refactor is Directive 013 (pure restructuring, zero behavior change). Motor integration with ConsciousOutput is Directive 014.

## Broader Roadmap (011–017)

011 — **This directive.** ConsciousOutput type, gate, Deliberator protocol, first implementation.
012 — Prompt assembly and semantic limb expression. Field state → behavioral framing for LLM. This is where the yoga limbs meet the LLM's instruction-following. Most conceptually dense step.
013 — Motor codec refactor. Pure restructuring. Extract 10 text strategies into TextCodec. Add codec selection. Zero behavior change. 238+ tests still pass.
014 — Integration. Motor renders from ConsciousOutput. Subconscious output consumed by conscious. End-to-end escalated path fires.
015 — Mechanical audit. DNAgent reads everything, reports raw. Zero code changes.
016 — Conceptual audit. Fresh planning instance, adversarial posture. Key question: does the LLM actually behave differently when limb weights change, or is the prompt assembly theater?
017 — Remediation. Fix what the audit found.

## What to Watch

- **Does the gate suppress too aggressively or too conservatively?** The thresholds are guesses. Real usage data will calibrate them.
- **Does the Deliberator protocol actually support swappable backends?** The Anthropic implementation is the test case, but the real question is whether the protocol constraints work for a 7B local model with different capabilities.
- **Does ConsciousOutput's structure support the motor codec vision?** If motor can't meaningfully render from `ResponseDecision`, the medium-independence goal fails.
- **The subconscious problem.** Nobody reads `subconscious_output`. This directive makes conscious read escalation_reason from it, but the richer pattern associations (cached signal shapes) aren't consumed yet. Directive 014 is where subconscious earns its place or gets absorbed into immune.

## Relationship to Audit Findings

This directive builds directly on the signal domain audit remediation (010). Key connections:

- **Finding 8 (per-feature delta):** Fixed in 010. Conscious now receives dimensionally coherent deltas.
- **Finding 4 (Tarka as semantic-domain):** Confirmed by bigram entropy test in 010. Tarka is the conscious layer's responsibility.
- **Finding 3 (convergent cluster):** Treated as composite resting stance in the gate. Differentiation deferred to semantic expression (012).
- **Finding 7 (subconscious earning its place):** Conscious reads subconscious_output's escalation_reason. Deeper integration in 014.
- **Finding 2 (engineering assignments):** ConsciousOutput's ExpressionDirectives carry field weights as behavioral parameters, not as truth claims about limb meanings. The Deliberator translates weights into prompt framing — that translation is an engineering decision, documented as such.
