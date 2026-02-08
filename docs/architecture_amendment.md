# Architecture Amendment: The Signal-Semantics Boundary

**Date:** 2026-02-08  
**Status:** Proposed  
**Affects:** All seven systems, temporal stratification, core principles  

---

## Summary

This amendment documents a structural insight that emerged during sensory layer implementation design: **text is signal before it is language.** The sensory layer should extract signal-level features — density, entropy, coherence, periodicity, impedance — without interpreting semantic content.

This reframes sensory from "language processing" to "signal processing" and reveals a fundamental boundary that was *implicit* in the architecture's tick rate assignments but never named.

## The Signal-Semantics Boundary

The escalation boundary between subconscious and conscious is the crossing point from signal processing into meaning-making. This is not a performance optimization — it is the architectural reason the tick rate division exists.

The seven systems divide into three processing domains based on their relationship to meaning:

### Signal Domain (every cycle · cheap · no LLM)

**Systems:** Sensory, Immune, Subconscious

These systems operate on structural properties of input — not on what the input *means*, but on what it *looks like* as signal. They fire every cycle because signal processing is fast: no LLM call, no semantic interpretation, pure Python computation.

- **Sensory** — Signal characterization. Measures density, entropy, coherence, periodicity, noise floor, impedance. Classifies by signal type (steady-state, transient, periodic, noise). Computes delta from expected state using the orientational field as reference signal. Outputs a structured **signal report**.

- **Immune** — Signal anomaly detection. Biological immune systems detect pathogen-associated molecular patterns (PAMPs) without "understanding" pathogens. The immune layer operates on the signal report: is entropy abnormally high? Does a transient match known anomalous patterns? Is impedance outside normal range? Pure pattern matching on signal features, not semantic threat assessment.

- **Subconscious** — Signal pattern priming. "I've seen this signal shape before" — not "I understand what this means." Associates the current signal report against cached signal signatures from prior cycles. Primes for escalation when signal matches patterns that previously required conscious deliberation. Routes to motor when signal matches a cached response pattern.

### Semantic Domain (on escalation · expensive · LLM-backed)

**Systems:** Conscious

The conscious layer is the first and only system that interprets. It receives a signal report (sensory), a threat assessment (immune), and primed associations (subconscious) — all in signal-domain terms — and constructs meaning. The LLM call happens here.

Most inputs can be processed entirely in the signal domain without ever crossing into semantic interpretation.

### Meta Domain (periodic · read-only)

**Systems:** Sleep, Genetic, Motor

These systems don't process individual inputs through the signal-semantics pipeline:

- **Sleep** — Transfer function optimization. Consolidates signal patterns into updated transfer functions. Writes to orientational field, modifying limb weights (transfer function coefficients). Analogous to Phosphlux's `record_sweep`: characterizes system response across input range, optimizes response profile.

- **Genetic** — Reference signal specification. The eighteen limbs at default weights are the system's baseline transfer function — factory calibration. Everything sensory measures is measured against this reference.

- **Motor** — Reverse transduction (semantics → signal encoding). Takes deliberated output and encodes it for the output medium. If the channel is chat, shape for chat. If it's a tool call, different encoding. Motor doesn't decide *what* to say — it decides *how to encode it* for the target medium.

## Architectural Validation

The tick rate assignments from the original architecture now have deeper justification:

| Domain | Systems | Tick Rate | Why |
|--------|---------|-----------|-----|
| Signal | Sensory, Immune, Subconscious | Every cycle | Signal-domain ops are fast — Python-native, no LLM |
| Semantic | Conscious | On escalation | Meaning construction is expensive — LLM call |
| Meta | Sleep, Genetic | Periodic / read-only | System optimization, not input processing |
| Meta | Motor | On demand | Reverse transduction fires when there's output |

This wasn't arbitrary — it naturally emerged from signal vs. semantic processing requirements. The architecture already encoded this boundary. This amendment names it.

## The Orientational Field as Reference Signal

The orientational field is not metaphorical in this framing — it is literally the reference signal that sensory compares against to produce deltas. Just as Phosphlux's workbench injects known test signals (colorbars, ramps) to characterize a shader's transfer function, the orientational field provides the baseline against which sensory measures deviation.

The field's limb weights are transfer function coefficients. Sleep modifies these coefficients based on accumulated experience. Genetic provides the factory-calibrated defaults.

## Amendment to Core Architectural Principles

Add as a new core principle:

> **Signal before semantics.** The first three systems (sensory, immune, subconscious) operate in the signal domain — they characterize, pattern-match, and correlate without constructing meaning. Semantic interpretation happens only at the conscious layer, only on escalation. This boundary is the architectural reason the tick rate division exists, and it ensures the system can process most inputs without expensive meaning-making operations.

## Where This Goes in ARCHITECTURE.md

This principle should be inserted in the **Core Architectural Principles** section, and the signal/semantic/meta domain framing should be added to the **Temporal Stratification** section as the explanation for *why* the tick rates are assigned as they are.

Individual system descriptions in **The Seven Systems** section should be amended to reflect their signal-domain or semantic-domain role, but the existing relationship-to-information framing remains valid — it just gains a new layer of specificity.
