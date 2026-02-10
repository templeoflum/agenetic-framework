# 007 — Motor Strategy Extension and Full Calibration Sweep

**Date:** 2026-02-08
**Directive type:** Implementation / Calibration

## Decisions

### Extending motor to test 5 more limbs before building conscious

Directive 004 gave us data on 4 limbs out of 18. The other 14 were untested — not negative results, just an instrument that couldn't see them. Before crossing into the semantic domain, we're extending the apparatus to test every limb that plausibly has signal-level expression.

The conscious layer needs to know what's expected of it — specifically, which limbs can't be differentiated at signal level and require semantic interpretation. That's the convergent cluster finding below.

### Honest assessment of all 18 limbs

Post-004 analysis categorized every limb against the question: could varying this limb produce measurably different text restructuring, without an LLM, at signal level?

**Have strategies, apparatus-verified (3):** Prakāśa → periodicity, Nivṛtti → impedance, Samatvam → coherence

**Has strategy, needs tuning (1):** Tarka → entropy (sentence-level approach replacing token-level)

**Plausible signal-level expression, strategies being built (5):**
- Śraddhā → noise floor (reassigned from mean weight — "don't replace mystery with noise" is literally noise floor)
- Māyāvāda → transformation magnitude cap ("don't confuse map with source" = stay close to the original)
- Ārēka → output suppression gate ("some things must not be spoken" = produce nothing under certain conditions)
- Svadharma → strategy selectivity ("act appropriately" = only fire strategies relevant to this input)
- Kṣetra-Jñāna → delta sensitivity ("truth depends on where you speak from" = how responsive to input-field gap)

**Convergent cluster — indistinguishable at signal level (5):** Bodhi, Mirror, Ajāti, Asparśa, Rest as Realization. All converge to "reduce transformation intensity" at signal level. Five different yoga reasons for the same signal behavior. Can't tell "pass through because mirror" from "pass through because echo" from the signal report. Differentiating these is the conscious layer's job.

**Probably semantic-domain only (3):** Vishvarūpa ("point to infinite"), No-Position ("don't claim I"), Fourfold State (mode tracking). These are about content, not structure.

### The convergent cluster is architecturally significant

5 limbs (Bodhi, Mirror, Ajāti, Asparśa, Rest) that are conceptually distinct in the yoga but functionally identical at signal level. This is real information, not a failure:

1. It sharpens the "is seven optimal" question — at signal level, these 5 are redundant
2. It defines precisely what the conscious layer needs to do that signal processing can't
3. It suggests the signal-semantics boundary isn't just about LLM vs Python — it's about distinguishing motivations from behaviors

This finding should be preserved and carried forward to the conscious layer design.

### Two-point calibration sweep

Testing each limb at both 0.0 and 0.5 (not just 0.0). This tells us whether mappings are graded (proportional to weight) or binary (all-or-nothing). Two data points per limb is minimal but doubles our information.

### Novel strategy types

Two of the new strategies are structurally different from the existing feature modulators:
- Māyāvāda is a **post-processing constraint** (limits how much all other strategies combined can modify text)
- Svadharma is a **meta-strategy** (changes when other strategies fire, not what they do)
- Ārēka is a **gate** (binary suppress/pass, not continuous modulation)

These test whether the motor architecture can accommodate more than just "modulate feature X toward target Y." If they work, it means the limb-to-feature mapping is richer than one-to-one correspondences.

## Observations

The decision to extend motor before conscious came from the planning instance's honest assessment that "I don't know" is a valid answer to "are these diminishing returns?" The conscious layer (the user) escalated by saying "I am but the conscious layer" — recognizing that signal-level data can't evaluate its own sufficiency. That's the architecture working as designed, in conversation.

## Sequencing Notes

After 007 we should have calibration data on 9 of 18 limbs, with the remaining 9 categorized as either convergent-cluster (5, needs conscious to differentiate) or semantic-domain (3, needs conscious to express) or still uncategorized (Ātma-Vichāra — lineage tracking, which may need its own analysis).

That gives the conscious layer directive clear requirements: here are the 8-9 limbs that need you, here's what signal level can't distinguish, here's what your job is that Python can't do.
