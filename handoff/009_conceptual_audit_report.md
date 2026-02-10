# Conceptual Audit: Agenetic Framework

**Date:** 2026-02-08  
**Scope:** Full conceptual audit of the agenetic-framework codebase after 9 implementation directives  
**Auditor:** Independent review (Claude Opus 4.6), fresh context  
**Relationship to Directive 009:** The mechanical audit (009) verified plumbing. This audit evaluates whether the plumbing connects to anything real.

---

## Files Examined

- `planning/CURRENT.md` — current state snapshot
- `handoff/009_audit_report.md` — mechanical audit (all 12 sections)
- `docs/ARCHITECTURE.md` — v2 specification
- `docs/architecture_amendment.md` — signal-semantics boundary
- `src/agenetic/systems/base.py` — all type definitions
- `src/agenetic/systems/sensory.py` — signal feature extraction (delta computation confirmed at source level)
- `src/agenetic/systems/motor.py` — text restructuring engine (partial direct read; full coverage via 009 audit)
- `tests/test_round_trip.py` — calibration infrastructure
- `planning/008_midpoint_migration.md` — midpoint weight rationale
- `planning/007_motor_extension.md` — motor extension rationale and convergent cluster analysis
- `references/conceptual_archaeology.md` — limb-to-feature mapping origins

---

## Finding 1: Circular Reasoning in Calibration

### What's happening

The calibration apparatus is mechanically correct. Motor takes text, restructures it based on limb weights, sensory re-measures the restructured text, deltas are computed. The 009 audit verified the loop closes properly.

The tautology is one level up. Take Samatvam (limb 7) as the clearest case. The motor's coherence strategy bridges words from previous sentences to increase coherence, or reverses sentence order to decrease it. Sensory measures coherence via Jaccard similarity on word sets between adjacent sentences. When the motor bridges words between sentences, word-set overlap between adjacent sentences goes up by construction. The calibration "confirms" this.

This pattern holds for all five "confirmed" mappings:

- **Prakāśa → periodicity:** Motor repeats phrases at intervals. Sensory measures bigram repetition. Repetition detected.
- **Nivṛtti → impedance:** Motor strips non-ASCII characters. Sensory measures non-ASCII ratio. Ratio changes.
- **Samatvam → coherence:** Motor bridges words between sentences. Sensory measures word overlap between sentences. Overlap changes.
- **Śraddhā → noise floor:** Motor inserts pipe markers. Sensory measures single-character token ratio. Ratio changes.
- **Density via mean weight:** Motor collapses/adds whitespace. Sensory measures character-to-whitespace ratio. Ratio changes.

Each motor strategy was designed to modulate the specific feature that sensory measures. Confirmation is guaranteed by construction. It would be shocking if these features *didn't* change.

### How severe

Moderate. The apparatus isn't broken — it verifies that pipes connect. But "apparatus-confirmed" implies empirical discovery, and what was discovered is only that code does what the code was written to do. The real test — whether these mappings produce meaningful behavior differences when the conscious layer interprets them — can't be evaluated until the semantic domain exists.

### Before conscious layer?

No code fix needed. The documentation should stop calling these "confirmed mappings" and call them "verified connections." The word "confirmed" implies empirical validation. This is verified plumbing.

---

## Finding 2: Self-Fulfilling Prophecy in Limb Mappings

### What's happening

The conceptual archaeology document traces the lineage honestly: Hermetic principles → ACM system design → behavioral spec → Asparśa Yoga. The limb-to-feature mapping table in Section V is explicitly labeled "Preliminary" and notes "some assignments may be wrong." The 007 planning doc categorized all 18 limbs against the question "could varying this limb produce measurably different text restructuring, without an LLM, at signal level?" before building strategies. It didn't claim all mappings were natural.

The Śraddhā → noise floor mapping illustrates the process well: "don't replace mystery with noise" was read as *literally* noise floor. The 007 doc calls this a "reassignment," not a discovery. The intellectual honesty is present in the planning layer.

But then the implementation encodes these preliminary assignments as constants (`PRAKASA_ID = 1` governs periodicity, `SAMATVAM_ID = 7` governs coherence), builds strategies around them, and runs calibration that "confirms" them. The hypothesis → implementation → validation pipeline never had a falsification step. The planning-layer caveats don't propagate to the code or test docstrings.

The deeper issue: there's no principled reason why Prakāśa (light of perception) maps to *periodicity* rather than density or coherence. The conceptual archaeology says Prakāśa is about "signal characterization without ownership" — that describes sensory's entire function, not a specific feature. Similarly, Samatvam ("harmonic tone, right proportion") could equally govern vocabulary richness, density, or the balance between features. The mapping to sequential sentence similarity is one interpretation among several.

### How severe

High conceptually, low practically. The mappings are arbitrary but functional — they produce a working system where limb weight changes cause measurable output changes. The risk is that treating arbitrary mappings as canonical will constrain the conscious layer. If the semantic domain is built on the assumption that Prakāśa *is* periodicity, that's a load-bearing assumption with no foundation.

The planning docs already carry the right caveats. The fix is smaller than the severity suggests: propagate those caveats to ARCHITECTURE.md and the test docstrings.

### Before conscious layer?

Yes. Not by changing the mappings, but by adding a clear architectural note: these are *engineering assignments*, not *philosophical derivations*. The conscious layer should be free to interpret limb meanings differently at the semantic level than the motor encodes them at the signal level. Signal-level mappings are transfer function coefficients, not truth claims about what the limbs mean.

---

## Finding 3: The Convergent Cluster

### What's happening

Five limbs (Bodhi, Mirror, Ajāti, Asparśa-Yoga, Rest as Realization — limbs 12, 15, 17, 18, 14) were declared indistinguishable at signal level in the 007 planning doc. The analysis is explicit and well-reasoned: "5 different yoga reasons for the same signal behavior. Can't tell 'pass through because mirror' from 'pass through because echo' from the signal report. Differentiating these is the conscious layer's job."

Looking at the descriptions, these are all variations on "the system in its resting state, not actively modulating." They describe *stances toward processing*, not *processing operations*. This is a domain mismatch — they're metadata about the system's relationship to its own activity, which is what the meta/semantic domain should handle.

However, the "indistinguishable at signal level" finding was declared based on what the motor can *produce*, not on what sensory can *measure*. The current feature set has six measurements: density, entropy, coherence, periodicity, noise floor, impedance. If sensory had richer measurement capabilities — sentence length variance, syntactic complexity, rhetorical structure — some of these limbs might differentiate without requiring LLM calls. "Indistinguishable given our current 6 signal features" is more precise than "indistinguishable at signal level."

Two of these limbs could plausibly express at signal level with modest feature expansion:

- **Mirror** (non-accumulating processing) could modulate signal_pattern_cache behavior — faster expiry, smaller cache, decay rates.
- **Rest as Realization** could affect the escalation threshold — a high Rest weight raising the bar for escalation, keeping more inputs in signal domain. It could also express through sentence length variance (shorter, simpler output).

### How severe

Low. The clustering is mostly correct. The 007 analysis is honest and architecturally significant.

### Before conscious layer?

Optional. Consider whether expanding the signal feature set by 2-3 features could break the cluster before resorting to full semantic differentiation. This is cheaper than building semantic-domain expression for these limbs.

---

## Finding 4: Tarka Resistance

### What's happening

Three attempts to make Tarka (entropy, limb 2) modulate entropy at signal level have failed. The 008 planning doc acknowledges this: "two approaches have failed to register entropy changes in calibration. Worth one more attempt or accept as semantic-domain."

The mechanism is clear from the source. Entropy is computed as Shannon entropy over token frequency distributions. The motor's entropy strategy splits sentences at conjunctions and merges short sentences — operations that change syntax but preserve vocabulary distribution. The same tokens are present before and after restructuring, so token-frequency entropy doesn't change.

This reveals something important about the calibration framework as a whole. Compare Tarka to Samatvam:

- **Samatvam (coherence) "works"** because the motor strategy and the sensory measurement share the same mechanism. Motor bridges words between sentences; sensory measures word-set overlap between sentences. They're looking at the same thing.
- **Tarka (entropy) "fails"** because the motor strategy and the sensory measurement operate on different levels of the text. Motor rearranges sentences; sensory counts token frequencies. They're looking at different aspects.

The strategies that "confirm" are tautological. The strategy that "fails" is the one actually attempting something non-trivial. This is a systematic property of the calibration framework, not just an entropy problem.

Entropy sits on the boundary between signal and semantics. Token-frequency entropy is technically signal-level, but modulating it requires semantic operations (word substitution). The motor, correctly constrained to structural transformation, can rearrange but can't substitute. Character-level or bigram entropy would be more responsive to structural rearrangement — sentence splitting changes character distribution and bigram patterns even when it preserves vocabulary.

### How severe

High. The pattern (tautological strategies pass, genuine strategies fail) is a systematic property that should be explicitly documented. It means the calibration data is less informative than it appears — it confirms that code does what code does, and the one case where code tried to do something genuinely different, it failed.

### Before conscious layer?

Worth changing the entropy measurement to character-level or bigram entropy, which would respond to sentence splitting/merging. Or explicitly reassign Tarka's primary expression to the conscious layer (where word choice happens) and let the motor strategy remain as a secondary, weaker channel. Either way, document the tautological-vs-genuine pattern as a known property of the calibration framework.

---

## Finding 5: Binary Threshold Effects

### What's happening

The system allows 18 continuous weights (0.0 to 1.0) but many strategies respond in binary rather than proportional ways:

- **Māyāvāda Cap:** Activates below 0.45, inactive above. A weight of 0.44 vs 0.46 is the difference between full activation and no activation.
- **Ārēka Gate:** Fires when weight > 0.3 AND noise > 0.3 AND entropy > 5.0. All-or-nothing suppression.
- **Svadharma Selectivity:** threshold_scale = 0.5 + weight. Continuous, but it scales *other* strategies' binary thresholds.
- **Kṣetra-Jñāna Sensitivity:** delta_scale = 0.5 + weight * 0.5. Continuous, but scales delta magnitudes.

The four primary feature strategies (density, coherence, periodicity, noise/impedance) use genuinely continuous target profiles: `target = base + (weight - 0.5) * range`. These are proportional.

So the picture is mixed: 6 strategies produce continuous effects, 4 are binary or quasi-binary, and 8 limbs have no signal-level expression at all. The continuous weight system promises expressiveness that many of the strategies don't deliver.

The 008 planning doc was aware of this concern: "The binary-vs-graded finding from Directive 007 might be an artifact of the 1.0 baseline. At 0.5, the symmetric formula structure should produce proportional responses by construction. If mappings are still binary at 0.5, that's a real finding about threshold effects rather than a baseline artifact." But the 009 audit doesn't report whether this question was answered after the midpoint migration. The data exists (Directive 008 ran the full sweep at 0.5) but the analysis wasn't done.

### How severe

Moderate. The continuous weight system promises expressiveness that the binary thresholds don't deliver. Not architecturally broken, but the gap between design intent and implementation behavior should be acknowledged.

### Before conscious layer?

Not blocking, but two things should happen: (1) Run the existing 0.5 calibration data through an analysis asking whether the core feature strategies show proportional response to weight, or are still binary. This answers 008's own open question using existing data, no new code needed. (2) Consider softening the binary thresholds — Māyāvāda could blend proportionally rather than switching at 0.45, Ārēka's suppression could be partial.

---

## Finding 6: Asymmetry (Suppression > Amplification)

### What's happening

At weight 0.0, impedance shows +0.3667 delta. At weight 1.0, the same limb shows much smaller effects. Suppression produces bigger signal deltas than amplification across the board.

This is a consequence of the calibration input, not an architectural flaw. The calibration text is clean structured prose. It has a baseline level of coherence, entropy, noise, etc. Degrading features is easier than enhancing features that are already near their natural ceiling. Coherence can drop from 0.7 to 0.0 (reverse sentence order) but can only rise from 0.7 toward 1.0, with diminishing returns as the text is already somewhat coherent. Noise floor starts low on clean text — you can add noise more visibly than you can remove noise that isn't there.

If the calibration text were noisy, high-entropy, incoherent prose, the reverse asymmetry would appear. The finding reveals that calibration results are input-dependent, not that the strategies are inherently asymmetric.

### How severe

Low as a bug, moderate as a documentation gap.

### Before conscious layer?

No code fix needed. Document that calibration results are relative to input characteristics. Consider running calibration against multiple input types to characterize strategy response curves more fully (see Finding 9).

---

## Finding 7: Is Seven the Right Number?

### What's happening

The seven systems trace from the Seven Hermetic Principles through the lineage documented in the conceptual archaeology. The architecture document's "Open Questions" section explicitly asks: "Is seven the structurally optimal number of subsystems, or an artifact of the analytical process?"

Assessment of each system against the codebase:

| System | Status | Earning its place? |
|---|---|---|
| Sensory | Implemented (370 LOC) | **Yes.** Real signal extraction, 6 features, classification, delta computation. Distinct function. |
| Immune | Implemented (210 LOC) | **Yes.** Anomaly detection, adaptive threat log, threat level classification. Distinct function. |
| Subconscious | Implemented (186 LOC) | **Mostly.** Signal pattern caching and escalation routing. But `subconscious_output` is written and never consumed by any downstream system. Overlap with immune in pattern matching. |
| Conscious | Stub | **TBD.** Its value depends entirely on semantic domain design. |
| Motor | Implemented (669 LOC) | **Yes.** 10 strategies, clear distinct function as reverse transduction. |
| Sleep | Stub | **TBD.** Its architectural value is clear (write access to field, consolidation), but that value is unrealized. |
| Genetic | Stub | **Questionable.** Currently an empty shell around a concept (the orientational field) that's already implemented in its own module (`orientational.py`). When sleep eventually writes to the field, it will write to `orientational.py`, not to `genetic.py`. The genetic "system" adds no behavior that isn't already provided by the field module itself. |

The **immune/subconscious boundary** is the weakest internal boundary among implemented systems. Both operate on signal reports, both do pattern matching, both contribute to escalation decisions. The subconscious's main unique contribution is the signal pattern cache, which could arguably live in the immune system's threat log. The conscious stub doesn't read `subconscious_output`, and neither does motor.

### How severe

Moderate. Seven is defensible as a design target and the architecture document is appropriately self-aware about the question. Not all seven are independently justified yet. The genetic system is currently an organizational label. Subconscious might merge with immune at the signal domain level and differentiate only at the semantic level.

### Before conscious layer?

Not blocking — the stubs don't interfere. But be honest that genetic is a label, not a system. And watch the immune/subconscious boundary when building conscious: if conscious consumes immune's threat assessment but ignores subconscious's output (which is already the case in the stub), that's a signal that subconscious isn't earning its place at the signal level.

---

## Finding 8: The Global Mean Delta (Most Consequential Technical Finding)

### What's happening

Sensory computes deltas by using the mean of ALL 18 limb weights as a single reference value, then subtracting this same scalar from every feature. From `sensory.py` lines 241-253:

```python
reference = sum(limb["weight"] for limb in limbs) / len(limbs)
density_delta = features["density"] - reference
entropy_delta = features["entropy"] - reference
coherence_delta = features["coherence"] - reference
periodicity_delta = features["periodicity"] - reference
noise_delta = features["noise_floor"] - reference
impedance_delta = features["impedance"] - reference
```

This has three compounding problems:

1. **Dimensional incoherence.** Density (a ratio around 0.8) is compared to the same reference as entropy (a value around 4.0). The features aren't on the same scale, so subtracting the same reference from all of them produces physically meaningless deltas.

2. **Insensitivity to field structure.** If Prakāśa is raised and Nivṛtti is lowered by equal amounts, the mean doesn't change, and *no deltas are produced* — even though two features should be modulating in opposite directions. The computation responds to the field's center of mass, not its internal structure.

3. **Misleading aggregate deviation.** The aggregate deviation (`sqrt(sum(d^2))`) drives escalation decisions. It's computed from these incoherent deltas. The 008 planning doc noted the symptom: "At 1.0 reference, typical text had aggregate_deviation ~2.0 because periodicity/noise/impedance are naturally near 0 while the reference was 1.0." The migration to 0.5 halved the problem but didn't fix the structural issue.

The round-trip calibration works *despite* this because `vary_single_limb` sets all other limbs to baseline, making the mean shift proportional to the single varied limb. In production with multiple limbs at different weights, the deltas would be misleading.

The code comments acknowledge this: "v1 simplification."

### How severe

High. This is the most consequential technical finding. The delta computation is the foundation of the escalation decision, and it's dimensionally incoherent. Every downstream system that reads `signal_report["delta"]` is reading values that conflate different measurement scales.

### Before conscious layer?

Yes. The delta computation should use per-feature reference values derived from the specific limbs that govern each feature, or at minimum, features should be normalized to a common scale before computing deltas. This is the one technical fix that most directly affects whether the conscious layer can trust the data it receives.

---

## Finding 9: Single Calibration Input

### What's happening

All 18 × 3 calibration sweep points use one piece of text:

```python
CALIBRATION_INPUT = (
    "The quick brown fox jumps over the lazy dog. "
    "The dog barks at the fox loudly. "
    "The fox runs away quickly and quietly. "
    "Meanwhile the cat sleeps on the warm mat peacefully."
)
```

The architecture amendment references Phosphlux's `record_sweep`, which injects *multiple known test signals* to characterize response across the input range. The current calibration uses a single test signal — equivalent to characterizing a filter by playing one note through it.

This means the calibration data tells you how each limb affects *this specific text*, not how it affects text in general. Strategy behavior is input-dependent: Ārēka only fires on high-noise high-entropy input (which this clean prose isn't), so that code path has never been exercised during calibration. The asymmetry in Finding 6 is also an artifact of using only clean prose input.

### How severe

Moderate. The calibration claims should be scoped: "these mappings are verified for structured prose input." A proper characterization sweep would use 3-5 input types (clean prose, code, noisy text, short input, long input) to map the actual response surface.

### Before conscious layer?

Not blocking, but should be done. Expanding to 3-5 calibration inputs is low-cost and would substantially increase confidence in the mapping data.

---

## Finding 10: The "Signal Processing" Label

### What's happening

The architecture amendment frames sensory/immune/subconscious as "signal domain — no LLM, pure Python computation." This is accurate but potentially misleading. What sensory computes is text statistics — token frequency distributions, bigram counts, Jaccard similarity between sentence word sets. Calling these "signal features" borrows legitimacy from signal processing (a mature engineering discipline) for what is more accurately computational stylistics or quantitative text analysis.

Signal processing has well-defined mathematical properties — linearity, time-invariance, frequency-domain analysis, convolution — that don't apply here. Text doesn't have a frequency spectrum. Shannon entropy over token counts is related to but distinct from information-theoretic signal entropy. The "transfer function" metaphor from Phosphlux is evocative but not formally grounded: there's no input-output linearity being characterized.

### How severe

Low as an engineering issue (the code works), moderate as a conceptual risk. If the conscious layer is designed assuming actual signal processing properties (superposition, convolution, frequency decomposition), it will be built on a false premise.

### Before conscious layer?

Document the boundaries of the metaphor. "Signal domain" means "sub-semantic numerical analysis of text features." It does not mean the formal signal processing framework applies. The Phosphlux analogy is useful for intuition but shouldn't drive architectural decisions that depend on mathematical properties text analysis doesn't have.

---

## Finding 11: test_motor.py Baseline Bug

### What's happening

`test_motor.py` line 55 defines `_vary_single_limb(limb_id, weight, baseline=1.0)`. The `test_round_trip.py` version was updated to `baseline=0.5` in Directive 008, but the `test_motor.py` version was not. This means motor field sensitivity tests set non-varied limbs to 1.0 instead of the intended 0.5 operating point.

With all other limbs at 1.0: mean weight is high, density modulation is in a different regime, Svadharma's threshold_scale is 1.5 for all non-varied limbs, and Kṣetra's delta_scale is at maximum. The motor is being tested in a completely different operating regime than the calibration apparatus assumes.

The tests still pass because they check relative behavior (different weights produce different outputs), not absolute behavior at the 0.5 operating point. But the data they produce doesn't correspond to the system's intended configuration.

### How severe

Moderate. Straightforward bug, easy fix, but it means motor unit test data doesn't match calibration data — they're testing different operating points.

### Before conscious layer?

Yes. This is a one-line fix (`baseline=1.0` → `baseline=0.5`).

---

## Summary Triage

### Must Fix Before Conscious Layer

| # | Finding | Fix |
|---|---|---|
| 8 | Global mean delta in sensory | Per-feature reference values or feature normalization |
| 11 | test_motor.py baseline=1.0 | Change to 0.5 |
| 4 | Tautological calibration pattern | Document that strategies sharing mechanism with measurement produce guaranteed confirmation; Tarka's failure is the informative result |
| 2 | Limb mapping provenance | Propagate "engineering assignment" caveat from planning docs to ARCHITECTURE.md; conscious layer must not be constrained by signal-level assignments |

### Should Fix, Not Blocking

| # | Finding | Fix |
|---|---|---|
| 5 | Binary thresholds unanswered | Analyze existing 0.5 sweep data for proportional-vs-binary response |
| 4 | Tarka entropy measurement | Consider character-level or bigram entropy |
| 9 | Single calibration input | Expand to 3-5 input types |
| 5 | Binary meta-strategies | Soften Māyāvāda and Ārēka toward proportional response |
| 1 | "Confirmed" language | Rename to "verified connections" in documentation |

### Watch, Don't Fix Yet

| # | Finding | What to watch |
|---|---|---|
| 3 | Convergent cluster | Whether 2-3 additional signal features could break it before requiring semantic differentiation |
| 7 | Immune/subconscious boundary | Whether conscious layer consumes subconscious_output |
| 7 | Genetic system | Whether it earns distinct function or remains a label for orientational.py |
| 10 | Signal processing metaphor | Whether conscious layer design assumes formal SP properties |
| 6 | Suppression asymmetry | Whether multi-input calibration reveals it's input-dependent |

---

## Closing Assessment

The signal domain is well-engineered infrastructure with a sophisticated but honest self-awareness problem. The planning documents are remarkably candid about uncertainty, arbitrary choices, and open questions — but that candor doesn't propagate to the code, tests, or calibration data, which present engineered assignments as empirical findings.

The most important structural insight from this audit: **the calibration strategies that "confirm" are tautological (motor and sensory measuring the same thing), and the one strategy that attempts genuine cross-level measurement (Tarka) fails.** This means the calibration framework validates plumbing, not mapping hypotheses. That's valuable but different from what the documentation claims.

The most consequential technical fix: **the global mean delta in sensory.** This is the foundation of escalation decisions and it produces dimensionally incoherent values. Everything downstream — immune threat assessment, subconscious escalation priming, conscious triggering — reads these deltas. Fixing this before the conscious layer prevents compounding the error into a system that makes meaning from meaningless numbers.

The architecture is sound. The signal-semantics boundary is a genuine structural insight. The seven-system model is defensible even where individual systems are thin. The orientational field is a clean engineering abstraction. The problems are in the space between the architecture and its current implementation — the gap between what the framework claims to know and what it actually knows.
