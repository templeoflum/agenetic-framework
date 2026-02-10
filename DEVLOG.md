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
- Apparatus-vs-hypothesis interpretation caveat (verified plumbing works, semantic validation requires conscious layer)
- Updated limb-to-feature mapping status (3 apparatus-verified, 1 below threshold, rest pending)
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
| Nivṛtti | impedance +0.3667 | Verified (both points) |
| Māyāvāda | 0.0 | Cap inactive at default weight (expected) |
| Śraddhā | noise_floor +0.0541 | **New, verified** |
| Ātma-Vichāra | 0.0 | Uncategorized |
| Samatvam | coherence −0.0263 | Verified, graded (0.0 at half-weight) |
| Ārēka | 0.0 | Gate inactive for clean calibration text (expected) |
| Svadharma | 0.0 | Threshold scaling is second-order (expected) |
| Kṣetra-Jñāna | coherence +0.0854, periodicity −0.0588 | **New, second-order verified** |
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
- Same 5 primary mappings verified: Prakāśa→periodicity, Nivṛtti→impedance, Samatvam→coherence, Śraddhā→noise_floor, Kṣetra-Jñāna→second-order
- Tarka still does not register as entropy change despite sentence-level approach and new formula
- Asymmetric response pattern: suppression (0.0) produces more visible effects than amplification (1.0), because baseline strategies already fire at 0.5
- Meta-strategies (Svadharma, Kṣetra-Jñāna) now clearly visible: they produce effects by *disabling* other strategies rather than directly modulating features
- Baseline strategies at 0.5: entropy_modulation + coherence_modulation (because current features diverge from targets)

**Tests updated (5):** All in TestMotorHelpers — expectations changed from 1.0 to 0.5 for weight helpers and coherence target. No tests removed, no tests weakened.

---

## 2026-02-08 — Directive 009: Comprehensive Mechanical Audit

**Tests:** 237 passing (no change — zero code modifications)

Full codebase audit before crossing into the semantic domain. Read every source file (16), every test file (6), every documentation file (5+), and pyproject.toml. Produced 12-section audit report at `handoff/009_audit_report.md`.

**No code was changed.** This directive was read-only by design — "find problems" and "fix problems" must not happen in the same pass.

**Key findings (raw data for conceptual audit):**

| Category | Finding |
|---|---|
| Interface compliance | 3 stub systems return state by reference (mutation risk) |
| State flow | `subconscious_output` written but never consumed; `metadata.timestamps` dead field |
| Type consistency | `_make_sample_state()` missing `transform_magnitude` |
| Test baseline | `test_motor.py::_vary_single_limb` still uses `baseline=1.0` (D008 miss) |
| Tautological tests | `test_low_mayavada_constrains_output` body is `pass`; 4 tests assert only `repair_passed` or `isinstance` |
| Dead code | Unused `dataclass` import in base.py; duplicated `_to_str()` and `_euclidean_distance()` |
| Documentation drift | ARCHITECTURE.md status stale; amendment/signal_report still say "Proposed"; README tree stale |
| Determinism | Immune uses `datetime.now()` for timestamps (non-deterministic) |
| Stale reference | test_graph.py comment references field reference of 1.0 (now 0.5) |

**Verified correct:**
- Write access constraints (no violations)
- Calibration apparatus (measures what it claims)
- All 18 limbs consistent across field, motor constants, and test references
- All 10 motor strategies deterministic
- Connection matrix matches topology module

**What this directive did NOT do:** Interpret findings. The planning instance will analyze the audit report in a fresh context (conceptual audit) to evaluate concerns about circular reasoning in calibration, self-fulfilling limb mappings, the convergent cluster, and Tarka resistance.

---

## 2026-02-09 — Directive 010: Audit Remediation

**Tests:** 238 passing (1 new, 237 existing)

Addressed all must-fix findings and low-cost should-fix items from the conceptual audit (`handoff/009_conceptual_audit.md`). The biggest change is the sensory delta fix; the rest is documentation, calibration infrastructure, and a new signal feature.

### Per-feature delta computation (Part A — most consequential)

The conceptual audit's Finding 8: sensory subtracted a single scalar (mean of all limb weights) from every feature value. Density (~0.8) and entropy (~4.0) compared against the same reference. Dimensionally incoherent.

**Fix:** Per-feature references using the same formulas as motor's target profile. Extracted `compute_target_profile()`, `get_limb_weight()`, `mean_limb_weight()`, and all limb ID constants from motor.py into base.py. Both sensory and motor now import the same function. Formulas cannot drift apart.

Aggregate deviation for clean prose at default weights: ~0.97 (was ~2.0 with global mean). The subconscious escalation threshold (1.5) is now above the clean-prose deviation — clean text no longer automatically escalates.

### Bigram entropy (Part G)

Added `bigram_entropy` to SignalFeatures — Shannon entropy over character bigram frequency distribution. Tarka does NOT register against bigram_entropy for clean prose — sentence-level restructuring preserves character bigram patterns as well as token frequencies. **Tarka is definitively semantic-domain** for typical text.

However, the multi-input sweep (Part F) revealed that Tarka DOES produce +0.39 entropy delta on long_repetitive input. The response is input-dependent.

### Multi-input calibration surface (Part F)

5 input types × 18 limbs × 2 weights = 180 sweep points. Key findings by input type:

**clean_prose** (baseline: 2 strategies fire)
```
Suppression (0.0):
  Prakasa      periodicity: +0.0912, bigram_entropy: -0.0388
  Nivrtti      impedance: +0.3667, bigram_entropy: +0.1175
  Sraddha      noise_floor: +0.0541
  Samatvam     coherence: -0.0263
  Ksetra-Jnana periodicity: -0.0588 (second-order, delta scaled to zero)
Amplification (1.0):
  Tarka        coherence: +0.0854, entropy: +0.0244
  Svadharma    periodicity: -0.0588 (threshold too high, no strategies fire)
```

**noisy_text** (baseline: 4 strategies fire — density, entropy, impedance, noise_floor)
```
Suppression: Prakasa periodicity: +0.1290, coherence: +0.1287; Samatvam coherence: -0.0238
Amplification: Tarka noise_floor: +0.0769 (input-dependent side effect)
```

**short_input** (baseline: density + entropy only)
```
Suppression: Nivrtti impedance: +0.3667, entropy: +0.5850
Amplification: (none — no limb variation produces additional strategies)
```

**code_like** (baseline: density, coherence, impedance)
```
Suppression: Prakasa periodicity: +0.1429, coherence: -0.8283
Amplification: Tarka coherence: -1.0000 (single-sentence input); Ksetra-Jnana noise_floor: -0.0625
```

**long_repetitive** (baseline: coherence + periodicity)
```
Suppression: Tarka entropy: +0.3893 (Tarka's strongest signal!); Nivrtti impedance: +0.3667; Sraddha noise_floor: +0.0525
Amplification: Samatvam entropy: +0.2140, coherence: +0.0302
```

Key insight: Strategy behavior is significantly input-dependent. Tarka produces zero entropy delta on clean prose but +0.39 on long repetitive text. Noisy text fires 4 baseline strategies (vs 2 for clean prose). Short input has minimal response surface.

### Documentation (Parts C/D/E/H)

- "Calibration Validity" section added to ARCHITECTURE.md — documents tautological pattern
- "Engineering Assignments" section added to ARCHITECTURE.md — limb mappings are design decisions, not philosophical derivations
- "confirmed" → "verified" across DEVLOG.md, CURRENT.md, planning entries
- Status labels updated: architecture_amendment.md and signal_report_structure.md now say "Implemented (Directive 002)"
- ARCHITECTURE.md status section rewritten to reflect actual implementation state
- Audit protocol section added to CLAUDE.md
- README.md project tree fixed

### Bug fixes

- `test_motor.py::_vary_single_limb` baseline fixed from 1.0 to 0.5 (Part B)
- `_make_sample_state` in test_systems.py: added `transform_magnitude`, added `bigram_entropy`, fixed `coherence` target from 0.7 to 0.35
- Stale comment in test_graph.py updated (field reference 1.0 → per-feature)
- Unused `dataclass` import removed from base.py

---

## 2026-02-09 — Directive 011: Conscious Layer Foundation

**Tests:** 262 passing (24 new, 238 existing, 1 skipped)

First implementation of the conscious layer — the system's crossing from signal domain into semantic domain. Replaced the pass-through stub with three foundational components: ConsciousOutput contract, proceed/suppress gate, and Deliberator protocol.

### ConsciousOutput contract (Part A)

Defined 4 new TypedDicts in base.py: `ResponseDecision` (intent, strategy, constraints), `ExpressionDirectives` (field weights, active limbs, resting stance, suppress_identity, state_awareness), `Lineage` (Ātma-Vichāra structural requirement — always present), `ConsciousOutput` (decision + expression + lineage + proceed + confidence). Added `conscious_output` to SystemState and GraphState.

Added all 18 limb ID constants to base.py (was 9, now 18). Added `CONVERGENT_CLUSTER_IDS` list for the resting stance composite.

### Proceed/suppress gate (Part B)

Pure Python, no LLM call. Fires BEFORE any tokens are spent. Priority order (first match wins):

1. **Immune override** — always proceed (threat_action == "escalate")
2. **Ārēka suppression** — weight > 0.7 AND classification == "noise"
3. **Nivṛtti pause** — weight > 0.7 AND aggregate_deviation < 0.5
4. **Resting stance** — convergent cluster composite > 0.8 AND deviation < 0.3
5. **Default** — proceed

Gate produces a full evaluation dict with all weights, thresholds, and the triggering reason. Suppression produces a complete ConsciousOutput (proceed=False, confidence=1.0, strategy="sacred_pause") — not None.

### Deliberator protocol (Part C)

`Deliberator` is a `runtime_checkable Protocol` (structural typing, not ABC). Any object with `deliberate(request: DeliberationRequest) -> ConsciousOutput` is a Deliberator.

Three implementations:
- **MockDeliberator** — deterministic, tracks call count and last request. Used in all tests.
- **AnthropicDeliberator** — first real LLM-backed implementation. Translates field state into behavioral system prompt instructions, makes one API call (claude-sonnet-4-20250514), parses JSON response. Handles parse failures with fallback.
- Protocol is extensible to local models, Claude Code native context, or any other backend.

### Conscious system (Part D)

`ConsciousSystem.__init__` accepts optional `Deliberator`. Handles three paths:

- **No signal report** — returns state with degradation flag, no output
- **Gate suppresses** — produces suppression ConsciousOutput, zero LLM tokens spent
- **Gate proceeds + deliberator** — builds DeliberationRequest, calls deliberator, patches lineage with gate evaluation
- **Gate proceeds + no deliberator** — degraded output (proceed=True, confidence=0.0)

Repair check verifies: lineage completeness (Ātma-Vichāra structural requirement), confidence threshold (proceed=True + confidence < 0.1 = fail). Apoptotic condition triggers after 3 consecutive low-confidence deliberations.

### Convergent cluster as composite resting stance

Five limbs (Bodhi, Mirror, Ajāti, Asparśa-Yoga, Rest as Realization) treated as one behavioral dimension: mean of their weights. High composite = system recedes from output. Low composite = system projects into output. This is a testable hypothesis — if conscious produces distinguishably different outputs for individual cluster members, the composite can be decomposed later.

### Expression directives

Field state translated into behavioral parameters:
- Active limbs: weight outside ±0.1 of 0.5 midpoint
- Resting stance: convergent cluster composite
- suppress_identity: No-Position (limb 13) weight > 0.6
- state_awareness: Fourfold State (limb 16) — "active", "reflective", "consolidated", "still"
- Limb behavioral instructions in Anthropic deliberator system prompt

### Tests

24 new tests in test_conscious.py: 9 gate logic, 3 structure, 3 protocol, 8 integration (including graph flow), 1 API (skipped without credentials). Updated test_graph.py to use MockDeliberator. Updated test_systems.py sample state with conscious_output.

---

## What's Next

Conscious layer foundation is in place. Next directives:

- **012 — Prompt assembly refinement** — Semantic limb expression. Field state → behavioral framing for LLM. Most conceptually dense step.
- **013 — Motor codec refactor** — Pure restructuring. Extract text strategies into TextCodec. Zero behavior change.
- **014 — Integration** — Motor renders from ConsciousOutput. Subconscious output consumed by conscious. End-to-end escalated path.
