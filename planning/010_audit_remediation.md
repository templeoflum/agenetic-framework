# 010 — Audit Remediation

**Date:** 2026-02-09
**Directive type:** Bug Fix / Documentation / Infrastructure

## Decisions

### Addressing the sensory delta computation first

The conceptual audit's Finding 8 is the most consequential technical issue. Sensory subtracts a single scalar (mean of all limb weights) from every feature value to produce deltas. Density (~0.8) and entropy (~4.0) compared against the same reference. Dimensionally incoherent, insensitive to field structure, and the foundation of every escalation decision downstream.

The fix uses per-feature references matching the motor's target profile formulas. This means sensory and motor share the same understanding of "expected" — which is what the architecture always intended. Extracting the shared computation prevents the formulas from drifting apart.

This will change all delta values, which means all downstream thresholds need review. DNAgent should run tests, see what breaks, and adjust based on actual values rather than guessing.

### The tautological calibration finding changes how we talk about results

The audit's sharpest conceptual insight: strategies that share mechanism with their measurement produce guaranteed confirmation. Coherence "works" because motor bridges words between sentences and sensory measures word overlap between sentences — same mechanism, different names. Tarka "fails" because motor rearranges sentences and sensory counts token frequencies — different mechanisms.

This doesn't mean the calibration is useless — it validates plumbing, which matters. But calling results "confirmed mappings" implies empirical discovery. "Verified connections" is accurate. The distinction matters for the conscious layer: it should not treat signal-level assignments as canonical truths.

### Multi-input calibration addresses three findings at once

Adding 3-5 input types to the calibration sweep addresses:
- Finding 9 (single input): characterizes the response surface, not just one operating point
- Finding 6 (asymmetry): tests whether suppression > amplification is input-dependent (the audit predicts it is)
- Finding 3 (Ārēka): gives the gate an input it can actually fire on (noisy text)

This is the largest infrastructure change in the directive but has compounding value.

### Tarka gets one more shot with a different measurement

Character bigram entropy responds to structural rearrangement (sentence splitting changes punctuation, capitalization, whitespace patterns). If Tarka registers against bigram entropy, it's a verified connection at signal level. If not, Tarka is definitively semantic-domain and the conscious layer owns it. Either result is useful; the current ambiguity is not.

### Audit protocol formalized

This is the first audit. Making it repeatable means:
- Mechanical audit via zero-code-change directive (DNAgent reads everything, reports raw)
- Conceptual audit via fresh planning chat (adversarial, no inherited assumptions)
- Remediation directive follows with triaged fixes

Triggered before major architectural transitions. The pattern proved its value immediately — Finding 8 (sensory delta) was invisible from inside the planning momentum but obvious to fresh eyes.

## What the audit got right

The closing assessment is worth preserving: "The signal domain is well-engineered infrastructure with a sophisticated but honest self-awareness problem. The planning documents are remarkably candid about uncertainty, arbitrary choices, and open questions — but that candor doesn't propagate to the code, tests, or calibration data, which present engineered assignments as empirical findings."

The fix isn't changing the engineering — it's making the documentation match the engineering's actual epistemic status.

## What the audit flagged but we're not fixing yet

- **Convergent cluster:** Audit suggests 2-3 additional signal features might break it. Worth exploring but not before conscious — the conscious layer needs to exist to evaluate whether the differentiation matters semantically.
- **Binary thresholds:** Māyāvāda and Ārēka could be softened to proportional. Real concern but lower priority than the delta fix and calibration expansion.
- **Immune/subconscious boundary:** Nobody reads subconscious_output. Watch whether conscious layer consumes it — if not, subconscious isn't earning its place at signal level.
- **Genetic system:** Currently a label. Watch whether it earns distinct function.
- **"Signal processing" label:** Accurate to say "sub-semantic numerical analysis." The formal SP framework (linearity, convolution, frequency decomposition) doesn't apply. The conscious layer should not be designed assuming SP properties.

## Sequencing Notes

After 010, the signal domain will be:
- Delta computation fixed (per-feature references)
- Calibration against multiple input types
- Documentation honest about what calibration does and doesn't prove
- Tarka resolved one way or the other
- Audit protocol established

That clears the path to the conscious layer. 011 should be the conscious layer directive — the first LLM-backed system, the semantic domain crossing, informed by everything the signal domain can and can't do.
