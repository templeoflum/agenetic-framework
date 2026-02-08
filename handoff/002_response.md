# Response 002 — Signal-Domain Tier Implementation

**Date:** 2026-02-07
**Status:** Complete
**Tests:** 136 passed, 0 failed

---

## Summary

Implemented the three signal-domain systems (sensory, immune, subconscious) as working Python-native processors. All three operate entirely in the signal domain — no LLM calls, no external dependencies beyond Python stdlib. Extended the shared state with `SignalReport`, `ThreatAssessment`, `SubconsciousOutput`, and `CachedSignalPattern` types. Updated graph wiring to propagate new state fields. Wrote comprehensive tests covering all three systems plus end-to-end graph flow.

---

## What Was Done

### Part A: Extended Base Types (`src/agenetic/systems/base.py`)

Added 7 new TypedDicts:
- `SignalFeatures` — 8 fields (density, entropy, coherence, periodicity, noise_floor, impedance, token_count, vocabulary_richness)
- `SignalClassification` — signal_type (5 categories), confidence, components
- `SignalDelta` — 6 per-feature deltas + aggregate_deviation + activated_limbs
- `SignalReport` — features, classification, delta, tick, input_hash
- `CachedSignalPattern` — input_hash, feature_vector, signal_type, outcome, response_pattern_id, encounter_count, last_seen_tick
- `ThreatAssessment` — is_anomalous, anomaly_scores, matched_patterns, threat_level (5 levels), recommended_action (4 actions)
- `SubconsciousOutput` — escalation_recommended, escalation_confidence, matched_pattern_ids, primed_associations

Extended `SystemState` with 4 new optional fields: `signal_report`, `threat_assessment`, `subconscious_output`, `signal_pattern_cache`.

### Part B: Sensory System (`src/agenetic/systems/sensory.py`)

Replaced stub with full signal characterization implementation:
- **density**: non-whitespace / total characters
- **entropy**: Shannon entropy over token frequency (bits per token)
- **coherence**: mean Jaccard similarity between adjacent sentences
- **periodicity**: ratio of repeated bigrams to total bigrams
- **noise_floor**: ratio of single-char + pure-punctuation tokens
- **impedance**: composite of non-ASCII ratio, mixed prose+code lines, nesting depth
- **vocabulary_richness**: unique tokens / total tokens
- **Classification**: noise (noise_floor > 0.4), periodic (periodicity > 0.3), transient (entropy_delta > 2.0), complex (multiple close), steady_state (default)
- **Delta**: computed against mean of orientational field limb weights as reference signal
- **Apoptotic condition**: 3 consecutive None inputs

### Part C: Immune System (`src/agenetic/systems/immune.py`)

Replaced stub with signal anomaly detection:
- **Innate immunity** (fixed thresholds): entropy > 6.0, noise_floor > 0.35, impedance > 0.5, aggregate_deviation > 3.0, vocabulary_richness < 0.1
- **Adaptive immunity**: Euclidean distance matching (< 0.5) against immune_log feature vectors. Matched patterns increase threat score scaled by confidence and encounter count.
- **Threat levels**: none (< 0.5), low (< 1.5), medium (< 3.0), high (< 5.0), critical (>= 5.0)
- **Actions**: proceed (none/low), flag (medium), quarantine (high), reject (critical)
- **Side effects**: escalation flag set on flag/quarantine, degraded flag on quarantine, apoptotic on reject
- **Immune log updates**: new anomalous patterns added, existing matched patterns get encounter count incremented
- **Apoptotic condition**: 3 consecutive critical ticks

### Part D: Subconscious System (`src/agenetic/systems/subconscious.py`)

Replaced stub with signal pattern priming:
- **Pattern correlation**: Euclidean distance matching (< 0.3) against signal_pattern_cache
- **Escalation decision** (priority order):
  1. Immune threat medium+ → escalate (confidence 0.9)
  2. Novel signal with aggregate_deviation > 1.5 → escalate (confidence 0.7)
  3. Cached matches with majority "escalated" outcomes → escalate
  4. Cached matches with majority "reflex_response" outcomes → no escalation
  5. Default → no escalation (confidence 0.5)
- **Flag behavior**: only sets escalate_to_conscious to True, never unsets
- **Cache management**: updates existing entries (encounter_count, last_seen_tick, outcome) or adds new entries
- **Apoptotic condition**: cache size > 10,000 entries

### Part E: Graph Wiring (`src/agenetic/network/graph.py`)

- Extended `GraphState` TypedDict with `signal_report`, `threat_assessment`, `subconscious_output`, `signal_pattern_cache`
- Updated `create_default_state()` to initialize new fields (None/[])
- Updated `_make_node()` to pass new fields through to system processing via `state.get()` with defaults

### Part F: Tests

**15 tests** for SensorySystem: string input, features, empty string, None input, entropy determinism, coherence, density, repair check, input hash, dict/list input, apoptotic conditions.

**11 tests** for ImmuneSystem: normal signal, high entropy/noise/impedance anomalies, critical apoptotic, medium escalation, immune log updates, adaptive matching, no signal report, repair check, low vocabulary richness.

**10 tests** for SubconsciousSystem: low/high deviation, immune threat escalation, cache matching, flag persistence, cache growth, apoptotic threshold, repair check, no signal report.

**6 tests** for signal-domain graph flow: new state fields present, signal report populated, processing order, reflex path, threat assessment, subconscious output.

All original 94 tests from Directive 001 continue to pass.

### Part G: CLAUDE.md

Updated project structure to include `architecture_amendment.md` and `signal_report_structure.md` docs, plus `002_directive.md` and `002_response.md` handoff files.

---

## Design Decisions

1. **Reference signal = mean of limb weights.** The orientational field's 18 limb weights (all 1.0 at init) are averaged to produce a single reference value. Delta is the difference between each measured feature and this reference. This is a v1 simplification — Phase 2 can map specific limbs to specific features.

2. **Aggregate deviation = Euclidean norm.** The six feature deltas are combined via sqrt(sum of squares). This gives a single scalar representing how far the signal deviates from "normal" as defined by the field. Consequence: any normal text input has aggregate_deviation ~2.0 because periodicity, noise_floor, and impedance are naturally near 0 while the reference is 1.0. This means novel inputs always trigger subconscious escalation until they're cached.

3. **Subconscious only sets, never unsets.** The `escalate_to_conscious` flag can only be set to True by subconscious, never reset to False. This means immune's escalation decision is preserved even if subconscious disagrees. Reset only happens at the start of a new cycle.

4. **Immune innate thresholds are conservative.** Individual anomaly scores from single threshold violations (e.g., noise_floor=0.6 → score 0.25) are often below the is_anomalous threshold (total >= 0.5). This is intentional: a single mild anomaly shouldn't trigger the alarm. Multiple mild anomalies compound.

5. **No LLM calls anywhere.** All three systems use pure Python stdlib computation. The conscious system (Phase 3) will be the first to use LLM calls.

---

## Observations for Next Directive

1. **Novel input always escalates.** Because the orientational field reference is 1.0 and normal text has periodicity/noise/impedance near 0, aggregate_deviation exceeds 1.5 for essentially any text. The subconscious therefore recommends escalation for all novel (uncached) inputs. This is correct behavior (new stimuli should get attention) but means the "reflex path" only activates for previously-seen patterns. The test for no-escalation routing pre-seeds the cache to demonstrate this.

2. **Immune adaptive matching needs seeding.** The immune_log starts empty, so adaptive immunity only activates after the first anomalous encounter. Phase 2 could add a "vaccination" mechanism.

3. **Signal pattern cache is unbounded in memory.** The apoptotic condition at 10,000 entries provides a safety valve, but there's no eviction strategy. Phase 2 sleep system should implement cache pruning.

4. **Conscious, motor, sleep, and genetic remain stubs.** They pass-through unchanged per directive scope.

---

## Files Changed

| File | Action |
|------|--------|
| `src/agenetic/systems/base.py` | Extended with 7 new TypedDicts + 4 new SystemState fields |
| `src/agenetic/systems/sensory.py` | Replaced stub with full implementation (~370 lines) |
| `src/agenetic/systems/immune.py` | Replaced stub with full implementation (~210 lines) |
| `src/agenetic/systems/subconscious.py` | Replaced stub with full implementation (~185 lines) |
| `src/agenetic/network/graph.py` | Extended GraphState + create_default_state + _make_node |
| `tests/test_systems.py` | Added 36 signal-domain tests + updated fixtures |
| `tests/test_graph.py` | Added 6 signal-domain graph flow tests |
| `CLAUDE.md` | Updated project structure |
| `handoff/002_response.md` | This file |
