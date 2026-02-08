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

## What's Next

Candidates for Directive 004+:

- **Conscious layer** — first LLM-backed system, semantic domain, meaning construction from signal-domain inputs
- **Motor layer** — reverse transduction, output encoding for target medium
- **Sleep layer** — transfer function optimization, cache pruning, orientational field weight adjustment
- **Reference signal calibration** — map specific limbs to specific signal features instead of uniform mean
- **Full orientational field implementation** — expand limb definitions beyond one-line principles to operational behavioral profiles with contextual activation patterns and inter-limb relationships
