# Development Log

Chronological record of what was built, what was decided, and why.

---

## 2026-02-07 — Directive 001: Initialize Repository and Scaffold Phase 1

**Commit:** `905d0b0`  
**Tests:** 94 passing  

Scaffolded the entire project from the architecture spec. Established:

- **Base interface** (`BaseSystem` ABC) with `process()`, `repair_check()`, `apoptotic_condition()`, `tick_rate` — every system implements this contract.
- **Typed state** (`SystemState` TypedDict) with `input`, `field`, `immune_log`, `metadata`, `flags` — the data structure that flows through the graph.
- **Seven system stubs** — all no-ops, but properly typed and documented. Each inherits from `BaseSystem` with correct tick rates.
- **Connection matrix** — 17 primary connections (always active, weight 1.0) and 6 secondary connections (context-dependent, weight 0.5). Three explicitly absent connections enforced by design: no runtime writes to genetic, no motor→sensory feedback within a cycle, no genetic→motor direct drive.
- **LangGraph graph** — compiles and routes: sensory → immune → subconscious → conditional (escalation → conscious, else → motor). Phase 1 simplified routing.
- **Orientational field** — all 18 Asparśa limbs with `read()` (all systems) and `write()` (sleep-only, enforced via token).

**Open issues from agent:**
- LangGraph requires its own `GraphState` TypedDict separate from `SystemState` (minor duplication)
- Sleep/genetic not yet in graph routing (by design — Phase 2)
- Topology data structure and actual graph routing are not yet synchronized (topology is source of truth, graph implements Phase 1 subset)

---

## 2026-02-08 — Architecture Amendment: Signal-Semantics Boundary

**Not a directive** — emerged from planning session during sensory layer design.

Key insight: **text is signal before it is language.** The seven systems divide into three processing domains:

- **Signal domain** (sensory, immune, subconscious) — structural properties, no LLM, every cycle
- **Semantic domain** (conscious) — meaning construction, LLM call, on escalation only
- **Meta domain** (sleep, genetic, motor) — system optimization and output encoding

The escalation boundary between subconscious and conscious is the crossing point from signal processing into meaning-making. This was implicit in the tick rate assignments from v2 but never named. The amendment names it.

Also reframes the orientational field as literal reference signal (not metaphor) — the baseline sensory measures deltas against. Limb weights are transfer function coefficients.

Documented in `docs/architecture_amendment.md` and `docs/signal_report_structure.md`.

---

## 2026-02-08 — Directive 002: Implement Signal-Domain Tier

**Commit:** `088d1f6`  
**Tests:** 136 passing (42 new, 94 existing)  

Replaced all three signal-domain stubs with working implementations. The signal-domain tier now operates as a unit: sensory characterizes → immune evaluates → subconscious correlates → routing decision.

**Sensory** (~370 lines) — computes six signal features from input:
- Density (character-level), entropy (Shannon over token frequency), coherence (Jaccard between adjacent sentences), periodicity (repeated bigrams), noise floor (single-char/punctuation tokens), impedance (composite: non-ASCII, mixed prose+code, nesting depth)
- Classifies: steady_state, transient, periodic, noise, complex
- Computes delta from orientational field reference (mean of limb weights as v1 simplification)
- SHA-256 input hash for pattern matching

**Immune** (~210 lines) — innate + adaptive anomaly detection:
- Innate: fixed thresholds on entropy (>6.0), noise_floor (>0.35), impedance (>0.5), aggregate_deviation (>3.0), vocabulary_richness (<0.1)
- Adaptive: Euclidean distance matching against immune_log feature vectors
- Five threat levels → four actions → flag/escalation/apoptotic side effects
- Adds new anomalous patterns to immune_log automatically

**Subconscious** (~185 lines) — signal pattern priming:
- Euclidean distance correlation against signal_pattern_cache
- Escalation decision tree: immune override → novel+deviant → cached majority outcome → default
- Only sets escalation flag, never unsets (immune decision preserved)
- Cache grows unboundedly (sleep will prune — apoptotic at 10k entries)

**New types added to `base.py`:**
- `SignalReport` (with `SignalFeatures`, `SignalClassification`, `SignalDelta`)
- `ThreatAssessment`
- `SubconsciousOutput`
- `CachedSignalPattern`
- `SystemState` extended with `signal_report`, `threat_assessment`, `subconscious_output`, `signal_pattern_cache`

**Known behavior:** Novel input always escalates because orientational field defaults (limb weights 1.0) diverge from typical text signal profiles (periodicity/noise/impedance near 0). Aggregate deviation exceeds subconscious threshold of 1.5 for essentially any uncached input. This is correct (new stimuli should get attention) but means reflex path only activates for previously-seen patterns. Fix comes via sleep optimizing the reference signal.

---

## 2026-02-08 — Directive 003: Documentation and Reference Material Sync

**Tests:** No change (136 passing)

Housekeeping pass. Synchronized all documentation and reference material produced during planning sessions:

- Verified README.md, DEVLOG.md, PLANNING_LOG.md present at repo root
- Added yoga scrolls and conceptual archaeology synthesis to `references/`
- Updated CLAUDE.md project structure and added reference material context
- No code changes

This directive clears the documentation backlog so future directives operate against an accurate repo state.

---

## 2026-02-08 — Directive 004: Motor Layer with Round-Trip Calibration

**Commit:** `869581b`
**Tests:** 195 passing (59 new, 136 existing)

Replaced motor stub with full signal-level text restructuring engine. Motor is the reverse of sensory: where sensory extracts signal features FROM text, motor adjusts text TO target signal profiles shaped by orientational field limb weights. Also built round-trip calibration infrastructure (motor→sensory feedback loop) for testing limb-to-feature mapping hypotheses.

**Motor system** (~460 lines) — six restructuring strategies:
- **Density modulation** (governed by mean weight) — collapse/expand whitespace
- **Entropy modulation** (governed by Tarka, limb 2) — deduplicate repeated tokens (increase) or replace singletons with most common word (decrease, capped at 30% of singletons)
- **Coherence modulation** (governed by Samatvam, limb 7) — bridge words between sentences (increase) or reverse sentence order (decrease)
- **Impedance modulation** (governed by Nivrtti, limb 3, inverse) — strip non-ASCII/brackets (decrease) or add section markers (increase)
- **Periodicity modulation** (governed by Prakasa, limb 1, inverse) — break repeated bigrams (decrease) or repeat key phrases at intervals (increase)
- **Noise floor modulation** (governed by mean weight) — remove punctuation tokens (decrease) or add structural markers (increase)

**Target profile computation:** density=mean_w×0.8, entropy=tarka×3.5, coherence=samatvam×0.7, impedance=(1−nivrtti)×0.3, periodicity=(1−prakasa)×0.3, noise=(1−mean)×0.3

**Repair check:** Token overlap ≥20%, length ratio 0.2–3.0×, non-empty output. Falls back to original text on failure. Apoptotic after 3 consecutive repair failures.

**Round-trip calibration infrastructure:**
- `vary_single_limb()` — isolated weight variation utility
- `round_trip()` — full motor→sensory feedback loop returning both signal reports + feature deltas
- Parameterized calibration sweep across all 18 limbs
- Results confirm governing limb mappings: Prakasa→periodicity (+0.035), Nivrtti→impedance (+0.367), Samatvam→coherence (−0.081), non-governing limbs show no response

**New types:** `MotorOutput` TypedDict added to base.py, `motor_output` field added to SystemState and GraphState.

**Bug fix during development:** Entropy modulation threshold was initially 0.3, causing entropy decrease to fire on the calibration input (current 3.88, target 3.5, delta −0.38). The decrease strategy replaced almost all singleton tokens with "The", dropping token overlap to 13% and failing repair check. Fixed by increasing threshold to 0.5 and capping replacement at 30% of singletons.

---

## 2026-02-08 — Directive 005: Housekeeping — Agent Identity and Documentation Sync

Tests: No change (195 passing)

Cleanup pass. No code changes.

**Agent identity formalized:** The CLI build agent is now **DNAgent** (DNA + Agent). Updated CLAUDE.md and all handoff response headers. The name captures the framework relationship — agenetic (without origin) is the architecture, DNAgent reads genetic instructions (directives) and assembles functional output.

**Planning log replaced:** Full replacement with post-Directive 004 analysis including:
- Calibration results table from round-trip sweep
- Apparatus-vs-hypothesis interpretation caveat (confirmed plumbing works, semantic validation requires conscious layer)
- Updated limb-to-feature mapping status (3 apparatus-confirmed, 1 below threshold, rest pending)
- DNAgent identity decision
- Updated sequencing (Directive 006+ candidates: conscious layer, Tarka tuning, or sleep)

**What changed:** CLAUDE.md (agent name), handoff/*_response.md headers (Transducer Archive → DNAgent), PLANNING_LOG.md (full replacement), DEVLOG.md (this entry).

---

## 2026-02-08 — Directive 006: Planning Infrastructure Migration

Tests: No change (195 passing)

Migrated from monolithic PLANNING_LOG.md to entry-based planning structure. No code changes.

**New structure:** `planning/` directory with numbered entries (one per planning session, never rewritten) and `CURRENT.md` (factual snapshot maintained by DNAgent from repo inspection).

**New workflow:** Each directive cycle, the planning instance provides a state file alongside the directive. DNAgent saves it as a numbered entry and extracts factual state into CURRENT.md. This replaces the monolithic planning log that was being fully rewritten every cycle.

**Files:** Created `planning/` directory. Moved PLANNING_LOG.md → `planning/001_through_005_legacy.md`. Created `planning/006_planning_infrastructure.md` (first entry in new format). Created `planning/CURRENT.md` (factual snapshot). Updated CLAUDE.md and docs/DIRECTIVES.md to describe new pattern.

---

## 2026-02-08 — Directive 007: Motor Strategy Extension and Full Calibration Sweep

**Tests:** 237 passing (42 new, 195 existing)

Extended the motor with 5 new limb-specific strategies and rewrote Tarka entropy modulation. Ran two-point calibration sweep (0.0 and 0.5) across all 18 limbs.

**New strategies implemented:**
- **Śraddhā → noise floor modulation** (limb 5, inverse) — reassigned from mean weight to dedicated limb. "Don't replace mystery with noise."
- **Māyāvāda → transformation magnitude cap** (limb 4, post-processing) — limits total output deviation. "Don't confuse map with source."
- **Ārēka → output suppression gate** (limb 8, binary gate) — suppresses output for high-noise high-entropy input. "Some things must not be spoken."
- **Svadharma → strategy selectivity** (limb 9, meta-strategy) — scales all strategy thresholds. "Act appropriately."
- **Kṣetra-Jñāna → delta sensitivity** (limb 10, meta-strategy) — scales delta magnitude. "Truth depends on where you speak from."

**Tarka rewrite:** Replaced token-level entropy modulation (append occurrence indices / replace singletons) with sentence-level restructuring (split at conjunctions/commas to increase, merge short sentences with connectives to decrease). The sentence-level approach preserves more original tokens naturally.

**New MotorOutput field:** `transform_magnitude: float` (0.0–1.0) tracks how much output deviated from input.

**Calibration results (two-point sweep: 0.0 and 0.5):**

| Limb | Feature response | Status |
|---|---|---|
| Prakāśa | periodicity +0.0912 | Confirmed (both points) |
| Tarka | entropy 0.0 | Still not registering — sentence-level merging produces same features |
| Nivṛtti | impedance +0.3667 | Confirmed (both points) |
| Māyāvāda | 0.0 | Cap inactive at default weight (expected) |
| Śraddhā | noise_floor +0.0541 | **New, confirmed** |
| Ātma-Vichāra | 0.0 | Uncategorized |
| Samatvam | coherence −0.0263 | Confirmed, graded (0.0 at half-weight) |
| Ārēka | 0.0 | Gate inactive for clean calibration text (expected) |
| Svadharma | 0.0 | Threshold scaling is second-order (expected) |
| Kṣetra-Jñāna | coherence +0.0854, periodicity −0.0588 | **New, second-order confirmed** |
| Limbs 11–18 | 0.0 | Convergent cluster + semantic domain (expected) |

**Tarka honest report:** Entropy modulation fires (strategy applied) but the resulting text feeds back the same signal features through sensory. The sentence-level merge/split approach is deterministic and preserves token overlap for repair check, but the structural changes don't produce distinguishable entropy values in the sensory measurement. This may need a fundamentally different approach — or it may be that Tarka's signal-level expression is inherently weak compared to semantic-level variety.

**Motor architecture note:** The three novel strategy types (post-processing constraint, binary gate, meta-strategy) all work correctly. The motor can accommodate more than one-to-one feature modulators. Svadharma and Kṣetra-Jñāna's second-order effects are visible in the sweep — Kṣetra-Jñāna at 0.0 causes fewer strategies to fire (coherence_modulation only), which shifts multiple features.

---

## 2026-02-08 — Directive 008: Midpoint Weight Migration and Recalibration

**Tests:** 237 passing (no new tests, 5 expectations updated)

Migrated all 18 orientational field limb weights from 1.0 to 0.5 and rebalanced the entire motor target profile system. This is the first directive that changes operating conditions of already-working systems rather than building new ones.

**Rationale:** 0.5 is the point of maximum information entropy on a 0-to-1 scale — the most receptive state, equally capable of amplification or suppression. At 1.0, every limb was maxed out with nowhere to go but down. The 0.5 midpoint model allows symmetric bidirectional modulation and aligns with the yoga's principle of receptive openness (Prakāśa).

**Formula restructuring:** Adopted symmetric `target = base + (weight - 0.5) * scale` pattern:

| Feature | Old formula (1.0) | New formula (0.5) | At 0.5 |
|---|---|---|---|
| density | `mean_w * 0.8` | `0.8 + (mean_w - 0.5) * 0.4` | 0.8 |
| entropy | `tarka * 3.5` | `3.5 + (tarka_w - 0.5) * 3.0` | 3.5 |
| coherence | `samatvam * 0.7` | `0.35 + (samatvam_w - 0.5) * 0.7` | 0.35 |
| periodicity | `(1.0 - prakasa) * 0.3` | `(0.5 - prakasa_w) * 0.6` | 0.0 |
| noise_floor | `(1.0 - sraddha) * 0.3` | `(0.5 - sraddha_w) * 0.6` | 0.0 |
| impedance | `(1.0 - nivrtti) * 0.3` | `(0.5 - nivrtti_w) * 0.6` | 0.0 |

**Threshold adjustments:**
- Ārēka gate: `areka_w > 0.8` → `areka_w > 0.3` (active range now includes above-midpoint values)
- Māyāvāda cap: `mayavada_w < 0.95` → `mayavada_w < 0.45` (active below midpoint)
- Sensory reference fallback: 1.0 → 0.5
- Motor helper fallbacks: 1.0 → 0.5

**Three-point calibration sweep (0.0, 0.5, 1.0):**

Baseline check: All limbs at 0.5 produce zero delta (correct).

Suppression (weight → 0.0):
```
Limb              density   entropy   coherence  periodicity  noise_floor  impedance  strategies
Prakasa          +0.0119   -0.0768   +0.0345    +0.0912      +0.0000      +0.0000    entropy, coherence, periodicity
Nivrtti          -0.0041   +0.1646   -0.0143    -0.0048      +0.0000      +0.3667    entropy, coherence, impedance
Samatvam         -0.0011   -0.0595   -0.0263    +0.0037      +0.0000      +0.0000    entropy, coherence
Sraddha          -0.0067   +0.0576   +0.0175    -0.0033      +0.0541      +0.0000    entropy, coherence, noise_floor
Ksetra-Jnana     -0.0006   -0.0946   +0.0345    -0.0588      +0.0000      +0.0000    (none - delta scaled to zero)
```

Amplification (weight → 1.0):
```
Limb              density   entropy   coherence  periodicity  noise_floor  impedance  strategies
Tarka            +0.0019   +0.0244   +0.0854    -0.0588      +0.0000      +0.0000    coherence
Svadharma        -0.0006   -0.0946   +0.0345    -0.0588      +0.0000      +0.0000    (none - threshold too high)
```

All other limbs: zero delta at both 0.0 and 1.0 (no motor strategies assigned).

**Comparison with 1.0 baseline data (Directive 007):**
- Same 5 primary mappings confirmed: Prakāśa→periodicity, Nivṛtti→impedance, Samatvam→coherence, Śraddhā→noise_floor, Kṣetra-Jñāna→second-order
- Tarka still does not register as entropy change despite sentence-level approach and new formula
- Asymmetric response pattern: suppression (0.0) produces more visible effects than amplification (1.0), because baseline strategies already fire at 0.5
- Meta-strategies (Svadharma, Kṣetra-Jñāna) now clearly visible: they produce effects by *disabling* other strategies rather than directly modulating features
- Baseline strategies at 0.5: entropy_modulation + coherence_modulation (because current features diverge from targets)

**Tests updated (5):** All in TestMotorHelpers — expectations changed from 1.0 to 0.5 for weight helpers and coherence target. No tests removed, no tests weakened.

---

## What's Next

Candidates for Directive 009+:

- **Conscious layer** — first LLM-backed system. Clean calibration data at correct midpoint, 8-9 limbs confirmed as needing semantic processing, convergent cluster (8 limbs) needs differentiation
- **Sleep layer** — transfer function optimization, cache pruning, orientational field weight adjustment
- **Tarka investigation** — three approaches failed (token-level D004, sentence-level D007, midpoint rebalance D008). Accept as semantic-domain or fundamentally rethink
