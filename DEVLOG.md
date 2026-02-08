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

## What's Next

Candidates for Directive 006+:

- **Conscious layer** — first LLM-backed system, semantic domain, meaning construction from signal-domain inputs
- **Sleep layer** — transfer function optimization, cache pruning, orientational field weight adjustment
- **Tarka entropy tuning** — refine entropy modulation strategy to register in calibration
- **Reference signal calibration** — refine limb-to-feature mappings based on round-trip calibration data
