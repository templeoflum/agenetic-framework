# 012 — Prompt Assembly Refinement

Date: 2026-02-10
Directive type: Refinement (no new systems, no new types, no routing changes)

## What This Directive Does

Refines the prompt assembly layer that translates field state into behavioral framing for the LLM deliberator. The foundation was built in 011 (13 limb instruction pairs, basic concatenation). This directive adds graduated intensity, limb interaction composition, and an observation harness for the audit.

This is the most conceptually dense step in the conscious layer build. It's where the yoga limbs meet the LLM's instruction-following. The question being set up (not answered — that's the audit's job): does prompt-side limb expression produce distinguishable behavior?

## Design Decisions and Rationale

### Graduated intensity over binary expression

A limb at weight 0.65 should produce weaker behavioral instruction than one at 0.95. Binary high/low loses this information. The intensity function maps weight distance from midpoint (0.5) to four descriptors: slightly, moderately, strongly, intensely.

The descriptors are prepended to the instruction text rather than rewriting the instruction itself. This means LIMB_INSTRUCTIONS content is unchanged from 011 — only the framing around them changes. Minimal diff, maximal effect.

Thresholds for the descriptors (0.3, 0.6, 0.85 on 0–1 normalized intensity) are engineering choices. They can be tuned based on audit observations.

### Limb interactions as compound instructions

Six interaction entries, deliberately small. The philosophy: only create compound instructions when the combination produces genuinely emergent behavior — when the whole is different from the sum of parts.

Examples of what IS an interaction:
- Tarka + Śraddhā (contradiction + ambiguity → present tension and ambiguity together)
- Ārēka + Nivṛtti (sacred silence + sacred pause → deep silence, absolute minimum)

Examples of what is NOT an interaction (and therefore not included):
- Prakāśa + Samatvam (observe + balanced tone → just observe with balanced tone, no emergence)
- Svadharma + Kṣetra-Jñāna (act appropriately + know your position → just act appropriately from your position)

The `replaces_individual` flag matters. When True, the compound instruction replaces both individual instructions — this avoids redundancy. When False (e.g., Tarka + Śraddhā), the compound adds a framing note while keeping individual instructions because they carry content the compound doesn't.

### Extraction into prompt_assembly.py

The prompt assembly logic is consciousness's core competence — it defines what the LLM sees. Keeping it in `deliberator_anthropic.py` ties it to one backend. Extracting it means:
- Any Deliberator implementation can import the same prompt assembly
- The module can be tested independently (no API keys needed)
- Future Deliberators (local models, Claude Code native) can use the same assembly or override it

`_parse_response()` stays in `deliberator_anthropic.py` because response parsing IS backend-specific. Different LLMs return different formats.

### Observation harness is recording, not asserting

The 016 audit will need evidence that prompt assembly produces meaningful behavioral differences. But the evidence can't come from the build agent — it would be self-confirming. The observation harness creates the measurement points:

- Structural observations (prompt diff for different weights) are deterministic and assertable
- Behavioral observations (LLM response diff) are recorded but not asserted

The audit evaluates the observations. The build agent just creates the recording infrastructure.

This avoids the circular reasoning the conceptual audit identified in the signal domain: "we prompted for X, the LLM mentioned X, therefore X is confirmed." Instead: "we prompted differently, here's how the prompts differ structurally. Whether the LLM's behavior differs meaningfully is for fresh eyes to evaluate."

### Interaction list is intentionally incomplete

Six interactions is not exhaustive. With 13 individually-instructed limbs, there are 78 possible pairs. Most pairs don't produce emergent behavior. The six chosen are the ones where the planning instance could articulate a genuinely compound instruction that differs from concatenation.

The audit may find that additional interactions are needed, or that some of these don't produce measurable behavioral differences. That's remediation territory (017), not build territory.

## Broader Roadmap (011–017)

011 ✓ ConsciousOutput type, gate, Deliberator protocol, first implementation. 262 tests.
012 — **This directive.** Prompt assembly refinement. Graduated intensity, limb interactions, observation harness.
013 — Motor codec refactor. Pure restructuring. Extract 10 text strategies into TextCodec. Zero behavior change.
014 — Integration. Motor renders from ConsciousOutput. Subconscious output consumed by conscious. End-to-end escalated path.
015 — Mechanical audit. DNAgent reads everything, reports raw. Zero code changes.
016 — Conceptual audit. Fresh planning instance, adversarial posture. Key question: prompt assembly theater or genuine expression?
017 — Remediation.

## What to Watch

- **Prompt length explosion.** With 13 possible individual instructions + 6 possible interactions + resting stance + role + output format, the system prompt could get long. The observation harness measures this (test_observe_all_limbs_high_prompt_length). If prompts exceed ~3000 chars, the instructions may compete for the LLM's attention rather than compound.

- **Interaction conflicts.** What if Tarka+Śraddhā fires AND Tarka+Samatvam fires simultaneously (Tarka=0.8, Śraddhā=0.8, Samatvam=0.3)? Both are included. Does the compound set of instructions still cohere? The observation harness doesn't test this directly — edge case for the audit.

- **Intensity descriptor effectiveness.** "Strongly: When you encounter contradictions..." — does the LLM actually modulate behavior based on that prefix? Or does it treat all instructions equally regardless of the descriptor? This is the fundamental empirical question. The audit needs to answer it.

- **The Tarka problem revisited.** The signal domain audit found Tarka indistinguishable from others at signal level. The conscious layer is Tarka's home — this is where contradiction-holding must produce measurable behavioral differences. If it doesn't work at prompt level either, Tarka may need a different implementation strategy entirely (not prompt instruction, but structural — e.g., multi-pass deliberation where contradictions are identified first, then held open).
