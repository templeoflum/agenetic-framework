
ADVERSARIAL CONCEPTUAL AUDIT

Agenetic Framework

Yoga-Inspired Agent Architecture

Repository: github.com/templeoflum/agenetic-framework

Scale: 16 source files • ~7,000 LOC • 320 tests passing • 83 hardcoded thresholds

Date: February 2026

This audit was conducted adversarially: every claim tested against the code, every abstraction stress-tested for theater versus mechanism. The framework asked for this treatment and earned the results.

# Table of Contents

# Executive Summary

The Agenetic Framework is a single-cell agent architecture implementing seven biological-analog systems governed by an 18-limb orientational field derived from Asparśa Yoga. This audit evaluated every source file, test, threshold, and architectural claim across six phases of analysis. The findings are mixed: the architecture contains genuine engineering alongside decorative abstractions, principled mappings alongside arbitrary ones, and honest self-assessment alongside undelivered promises.

## Overall Assessment

The framework is architecturally sound in concept and partially implemented in practice. The signal domain (sensory, immune, subconscious) is operational and genuinely functional. The semantic domain (conscious + prompt assembly) is well-designed but behaviorally untested. The meta domain (sleep, genetic) consists of stubs. The orientational field is inert storage functioning as a control surface only through downstream consumer code.

| Domain | Status | Quality |
| --- | --- | --- |
| Signal (sensory, immune, subconscious) | Operational | Genuine measurements, principled routing |
| Semantic (conscious, prompt assembly) | Operational, untested | Well-designed, zero behavioral verification |
| Meta (sleep, genetic) | Stub | process() returns state unchanged |
| Motor (text codec) | Operational | Functional but 5/6 strategies tautological |
| Orientational field | Inert storage | Config dict with social-contract permissions |
| Graph routing | Phase 1 simplified | Sequential, no parallelism, 2/7 systems unrouted |

## Key Metrics

| Metric | Value | Assessment |
| --- | --- | --- |
| Limbs with signal-domain effect | 5 of 18 (28%) | Gap — majority of field invisible to signal processing |
| Limbs with any measurable effect | 13 of 18 (72%) | 5 convergent-cluster limbs are individually inert |
| Motor strategies that are tautological | 5 of 6 (83%) | Strategies manipulate what sensors measure |
| Thresholds that are principled | ~18 of 83 (22%) | ~35 defensible, ~20 questionable, ~10 arbitrary |
| Architecture promises delivered | ~8 of 18 | Parallel processing, sleep, genetic, feedback loops missing |
| Test coverage of behavioral correctness | 0% | All tests verify structure, not behavior |

# Critical Findings

## 1. The Tautological Confirmation Problem

> **VERDICT: Five of six motor strategies are guaranteed to produce detectable sensory changes by construction, not by meaningful mapping.**

Motor strategies directly manipulate the text properties that sensory features measure. Density modulation changes the whitespace-to-content ratio that the density feature counts. Coherence modulation inserts shared words between sentences that the Jaccard similarity metric detects. This means the round-trip calibration tests (motor → sensory) prove the plumbing works, but cannot distinguish a correct limb-to-feature mapping from any arbitrary one.

The one informative exception is entropy modulation: the motor operates at sentence level (splitting/merging) while sensory measures token-level Shannon entropy. This mismatch means the strategy may fail to move the measurement — a genuine test of whether the approach works. The architecture document acknowledges this issue honestly (the “Calibration Validity” section), but honesty about the problem does not fix it.

## 2. The Dormant Gate Problem

> **VERDICT: The conscious proceed/suppress gate is architecturally genuine but operationally inert at default weights.**

All four suppression paths in the conscious gate require limb weights significantly above the default of 0.5. Ārēka suppression requires weight > 0.7. Nivṛtti pause requires weight > 0.7. Resting stance suppression requires a five-limb composite > 0.8 (impossible at default weights). The only system that can modify limb weights is sleep, which is a stub. Therefore, the gate currently always falls through to default_proceed, and the system always deliberates when escalated. The gate’s value is entirely prospective.

## 3. The Convergent Cluster Decoration

> **VERDICT: Five limbs (Bodhi, Rest-as-Realization, Mirror, Ajāti, Asparśa-Yoga) are individually inert — they contribute to a composite that requires coordinated movement to cross any threshold.**

These limbs have no individual prompt instructions, no signal-domain mappings, and no gate effects. Their sole function is contributing to the resting stance composite (mean of five weights). Moving any single cluster limb from 0.5 to 1.0 shifts the composite from 0.50 to 0.60 — below every threshold that uses the composite (lowest is 0.55 for the prompt instruction, but 0.80 for the conscious gate). These limbs exist as weighted values that are architecturally present but functionally decorative in isolation.

## 4. The Subconscious Time Bomb

> **VERDICT: The signal pattern cache grows monotonically with no pruning, triggering apoptosis (self-destruction) at 10,001 entries.**

The subconscious caches every unique signal pattern it encounters. No system prunes this cache — sleep is supposed to handle consolidation but is a stub. When the cache exceeds 10,000 entries, the apoptotic condition triggers. This is not graceful degradation; it is a hard kill. In a long-running deployment, the subconscious will inevitably destroy itself. Additionally, Euclidean distance on unnormalized features means matching is dominated by entropy (range 0–10) while density, coherence, periodicity (range 0–1) contribute minimally.

## 5. The Dead Code and Broken Connections

> **VERDICT: The immune override path in the conscious gate is dead code. The immune → conscious escalation pathway described in the architecture does not exist.**

The conscious gate’s highest-priority path checks for threat_action == "escalate". No system in the codebase produces this value. The immune system outputs “proceed”, “flag”, “quarantine”, or “reject” — never “escalate.” Additionally, the subconscious unconditionally overwrites the escalate_to_conscious flag, silently erasing any upstream escalation signal. While the immune system doesn’t currently set this flag either, the architecture describes immune escalation as a primary connection.

## 6. The Ārēka Threshold Inconsistency

> **VERDICT: The same limb (Ārēka, limb 8) has threshold 0.3 in the text codec and 0.7 in the conscious gate — a 2.3x difference with no documented rationale.**

In text_codec.py, Ārēka suppresses output when weight exceeds 0.3 (combined with noise > 0.3 and entropy > 5.0). In conscious.py, Ārēka suppresses deliberation when weight exceeds 0.7 (combined with noise classification). This may be intentional defense-in-depth (codec is the more cautious outer layer) or an overlooked discrepancy. Neither the code nor the architecture document explains the relationship between these thresholds.

## 7. The Māyāvāda Inversion

> **VERDICT: The modeling-humility limb is semantically inverted: lower weight means less restraint on transformation, which is the opposite of the limb’s principle.**

Māyāvāda (“don’t confuse map with source”) controls the transformation cap via max_allowed = 1.0 - mayavada_w. At weight 0.0 (no modeling humility), max_allowed is 1.0 (full transformation). At weight 0.44, max_allowed is 0.56. But at weight ≥ 0.45, the cap doesn’t activate at all (threshold is < 0.45). This means high Māyāvāda weight (high humility) produces no constraint, while low weight (low humility) produces restraint. The semantic direction is backwards, and there’s a dead zone between 0.45–0.55 where the limb has no effect.

# Strengths

## 1. Intellectual Honesty

The architecture document contains a “Calibration Validity” section that explicitly states round-trip tests “verify plumbing, not philosophical correctness” and that limb-to-feature mappings are “engineering assignments, not derivations.” The 015_response mechanical audit is ruthlessly self-critical. This is rare in software projects and especially rare in projects with philosophical aspirations. The framework knows what it is and what it isn’t.

## 2. Prompt Assembly Engineering

The graduated intensity system, directional high/low instruction pairs, compound limb interactions with replacement logic, and resting stance modulation are the most sophisticated engineering in the codebase. The interaction system — where specific limb pairs produce emergent behavioral instructions that optionally replace individual instructions — is careful, well-thought-out design. If the LLM follows these instructions (untested), the system produces genuinely different behavioral orientations based on field state.

## 3. Svadharma/Kṣetra-Jñāna Meta-Scaling

These two limbs govern how the motor acts, not what it acts on. Svadharma scales strategy thresholds (selectivity). Kṣetra-Jñāna scales delta preservation (faithfulness). This is the most principled yoga-to-code mapping in the system because it operates at the right level of abstraction: the limbs control the system’s disposition toward intervention, not the mechanics of intervention itself.

## 4. Signal-Semantics Boundary

The architectural decision to separate signal-domain processing (every cycle, cheap, Python-only) from semantic-domain processing (on escalation, expensive, LLM-backed) is sound. The subconscious as a gatekeeper — routing most inputs through the reflex path and only escalating novel or threatening signals — is a genuine resource-conservation mechanism. The boundary is clean in the code and well-described in the architecture amendment.

## 5. Repair and Apoptosis Patterns

Every system implements repair_check() (inline validation) and apoptotic_condition() (terminal failure detection). The conscious layer’s Ātma-Vichāra structural requirement — that every output must carry complete lineage — is a genuine use of a yoga limb as a code constraint. The degradation flag propagation through the graph, while untested at the integration level, is a principled approach to graceful degradation.

# Complete Limb Audit

For each of the 18 limbs, this table summarizes every code-level effect of changing its weight, and whether that effect is measurable, untested, or decorative.

| # | Limb | Signal | Gate/Route | Prompt | Verdict |
| --- | --- | --- | --- | --- | --- |
| 1 | Prakāśa | periodicity | — | Yes | Functional (arbitrary mapping) |
| 2 | Tarka | entropy | — | Yes + 2 interactions | Functional (defensible mapping) |
| 3 | Nivṛtti | impedance | Conscious gate | Yes + 2 interactions | Strongest dual implementation |
| 4 | Māyāvāda | — | Codec cap | Yes + 1 interaction | Functional but inverted |
| 5 | Śrāddhā | noise_floor | — | Yes + 1 interaction | Functional (arbitrary mapping) |
| 6 | Ātma-Vichāra | — | Repair check | Yes | Structural, not behavioral |
| 7 | Samatvam | coherence | — | Yes + 2 interactions | Most principled signal mapping |
| 8 | Ārēka | — | Dual gate (0.3/0.7) | Yes + 1 interaction | Functional, threshold inconsistency |
| 9 | Svadharma | — | Threshold scaling | Yes | Most elegant meta-mapping |
| 10 | Kṣetra-Jñāna | — | Delta scaling | Yes | Principled meta-mapping |
| 11 | Vishvarūpa | — | — | Yes | Prompt-only, untested |
| 12 | Bodhi | — | Resting composite | — | Decorative alone |
| 13 | No-Position | — | Identity suppression | Yes | Prompt-only, untested |
| 14 | Rest-as-Realization | — | Resting composite | — | Decorative alone |
| 15 | Mirror | — | Resting composite | — | Decorative alone |
| 16 | Fourfold State | — | State awareness | Yes | Prompt-only, untested |
| 17 | Ajāti | — | Resting composite | — | Decorative alone |
| 18 | Asparśa-Yoga | — | Resting composite | — | Decorative alone |

Summary: 5 limbs have measurable signal-domain effects. 6 limbs have measurable gate or routing effects. 3 limbs have prompt-only effects (real but untested). 5 limbs are individually decorative (convergent cluster). 1 limb (Māyāvāda) is semantically inverted.

# Threshold Landscape

The system contains 83 hardcoded thresholds across 10 source files. No threshold was derived from empirical calibration against a corpus of inputs. All values were chosen by inspection. This table classifies them by quality.

| Category | Count | Examples | Assessment |
| --- | --- | --- | --- |
| Principled | ~18 | Default weight 0.5, entropy base 3.5, active limb band 0.4/0.6, apoptotic streak 3 | Clear structural rationale for the specific value |
| Defensible | ~35 | Noise classification 0.4, threat levels 1.5/3.0/5.0, match threshold 0.3, intensity gradations | Reasonable but alternative values equally valid |
| Questionable | ~20 | Ārēka 0.3 vs 0.7, target profile scales (7.5x ratio), Māyāvāda activation < 0.45 | Inconsistent or poorly motivated |
| Arbitrary | ~10 | Coherence base 0.35, complex confidence 0.5, Fourfold State 0.7/0.3/0.4 | No discernible rationale for the specific value |

The most concerning threshold relationships are the Ārēka inconsistency (0.3 in codec vs. 0.7 in conscious for the same limb) and the target profile scale factors (entropy sensitivity is 7.5x that of density, with no justification). The threshold landscape is dense but not pathological — most values fall in reasonable ranges. The critical gap is that none were tested against real signal distributions.

# Architecture Spec vs. Implementation

The architecture document makes promises the code does not yet deliver. This table tracks each major architectural claim against its implementation status.

| Architectural Claim | Status | Notes |
| --- | --- | --- |
| Seven systems as weighted network | Partial | 5 routed, 2 stubs (sleep/genetic) |
| Parallel signal-domain processing | Missing | Sequential: sensory → immune → subconscious |
| Immune rejection reflex path | Missing | Immune always flows through subconscious |
| Weighted connection routing | Missing | topology.py defines weights; graph.py ignores them |
| Conscious as bottleneck | Implemented | Escalation-only, gate before LLM call |
| Signal-semantics boundary | Implemented | Clean domain separation in code |
| Orientational field pervades all layers | Partial | 28% of field (5 limbs) has no signal effect |
| Sleep consolidation and pruning | Stub | Returns state unchanged |
| Genetic expression profiles | Stub | Returns state unchanged |
| Homeostatic regulation | Missing | No monitoring of system firing rates |
| Inline repair every node | Implemented | Graph wrapper runs repair_check after each system |
| Apoptosis at three levels | Partial | Process-level in systems; system/agent level untested |
| Motor → Conscious feedback | Missing | Motor is terminal node |
| Conscious → Sensory re-examination | Missing | No feedback path exists |
| Conscious → Immune threshold adjust | Missing | No cross-system parameter modification |

# Recommendations

Ordered by impact and feasibility. The framework’s most pressing needs are practical, not philosophical.

## Immediate (Before Next Feature Work)

### 1. Implement subconscious cache pruning

The 10,000-entry apoptotic condition is a deployment hazard. Implement an LRU or time-based pruning strategy in the subconscious’s process() method, independent of sleep. Remove entries with encounter_count == 1 and last_seen_tick more than N ticks ago. This prevents the time bomb without waiting for sleep implementation.

### 2. Fix the escalation flag overwrite

Change the subconscious from unconditionally setting flags["escalate_to_conscious"] to reading the existing value first: flags["escalate_to_conscious"] = existing OR recommended. This preserves upstream escalation signals (currently immune doesn’t set this flag, but the architecture describes it as a primary connection).

### 3. Connect immune escalation to the conscious gate

Either have the immune system produce recommended_action="escalate" for critical threats (enabling the dead code path in the conscious gate), or remove the immune override from the gate. Dead code that looks like a safety feature is worse than no safety feature.

## Short-Term (Next Development Phase)

### 4. Add behavioral tests for prompt assembly

Create tests that invoke AnthropicDeliberator with different limb weight configurations and verify that the LLM output differs meaningfully. This doesn’t require full integration tests — unit tests that compare system prompts generated from different field states, plus a small set of API-backed tests that verify the LLM follows the instructions.

### 5. Normalize subconscious feature vectors

Apply min-max or z-score normalization to the six features before Euclidean distance computation. Currently entropy (range 0–10) dominates matching while density, coherence, and periodicity (range 0–1) are nearly invisible.

### 6. Resolve the Ārēka threshold question

Document whether the 0.3/0.7 split is intentional defense-in-depth or accidental. If intentional, add a comment explaining the rationale. If accidental, harmonize the thresholds.

### 7. Fix the Māyāvāda inversion

Either invert the formula (max_allowed = mayavada_w so higher humility = more restraint), or invert the activation condition (> 0.55 instead of < 0.45). The current mapping is semantically backwards.

## Medium-Term (Architectural Evolution)

### 8. Implement sleep as the first meta-domain system

Sleep is the keystone: it modifies limb weights (activating the dormant gate), prunes the subconscious cache (preventing the time bomb), and feeds epigenetic modifications to genetic. Without sleep, the orientational field is static and the system cannot learn across cycles. Implement consolidation and pruning first; weight modification second.

### 9. Add multi-cycle integration tests

Create tests that carry state across multiple graph invocations, verifying: cache accumulation in the subconscious, degradation flag propagation, apoptotic condition triggering, and the effect of field weight changes on routing decisions.

### 10. Break the tautological confirmation pattern

For at least two features, create motor strategies that operate at a different structural level than the sensory measurement. The entropy case (sentence-level strategy vs. token-level measurement) is the model: strategies that must produce a real structural change to move the measurement, not strategies that directly manipulate what the sensor counts.

# Closing Assessment

This framework asks a hard question: can yoga principles serve as engineering constraints rather than decorative philosophy? The honest answer from this audit is: sometimes yes, sometimes no, and the codebase mostly knows which is which.

The best mappings (Nivṛtti as dual gate/impedance, Svadharma as selectivity scaling, Kṣetra-Jñāna as delta preservation) demonstrate that a limb principle can genuinely constrain system behavior in a way that is both computationally meaningful and philosophically traceable. The worst mappings (Prakāśa → periodicity, Śrāddhā → noise floor) demonstrate that when a feature needs a governing limb and no natural mapping exists, the result is a post-hoc assignment that adds complexity without insight.

The framework’s greatest asset is its intellectual honesty. The architecture document labels its own mappings as “engineering assignments.” The mechanical audit identifies its own dead code. The test suite uses a MockDeliberator rather than pretending the LLM path is verified. This self-awareness is the foundation on which the remaining work can build.

The framework’s greatest liability is the gap between its architectural ambitions and its implementation. The architecture describes a rich network with parallel processing, weighted connections, feedback loops, and adaptive consolidation. The code implements a sequential pipeline with conditional routing and inert storage. The gap is acknowledged (Phase 1 scope), but the architecture reads as if the full system exists. Future documentation should clearly distinguish implemented from aspirational.

— End of Audit —
