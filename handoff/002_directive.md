# Directive 002 — Implement Signal-Domain Tier

**Date:** 2026-02-08

## Context

Directive 001 scaffolded the repo: seven system stubs, connection matrix, LangGraph graph, orientational field with 18 Asparśa limbs, 94 passing tests. All systems are currently no-ops that pass state through unchanged.

A key architectural insight has emerged since then: **text is signal before it is language.** The seven systems divide into three processing domains based on their relationship to meaning:

- **Signal domain** (sensory, immune, subconscious) — operates on structural properties of input, not semantic content. Every cycle, cheap, no LLM.
- **Semantic domain** (conscious) — constructs meaning. On escalation only, expensive, LLM-backed.
- **Meta domain** (sleep, genetic, motor) — system optimization and output encoding.

This insight is documented in two new files already in the repo:

- `docs/architecture_amendment.md` — the signal-semantics boundary as core architectural principle
- `docs/signal_report_structure.md` — the TypedDict interface between signal-domain systems

This directive implements the signal-domain tier as a unit. All three systems share a common processing paradigm: signal analysis with pure Python computation, no LLM calls, no external API dependencies beyond the token stream.

**Read these files before starting:**
- `CLAUDE.md` — project overview and workflow
- `docs/ARCHITECTURE.md` — full architecture spec (especially: sensory, immune, subconscious sections; connection matrix; temporal stratification)
- `docs/architecture_amendment.md` — signal-semantics boundary (the design rationale for everything in this directive)
- `docs/signal_report_structure.md` — signal report TypedDict definitions and per-system consumption patterns
- `handoff/001_response.md` — what was built in Directive 001, including open issues

## Objective

Implement the three signal-domain systems (sensory, immune, subconscious) as working Python-native processors. Add the `SignalReport` type to the shared state. Replace the three stubs with real implementations that characterize input as signal, detect signal anomalies, and perform signal pattern priming — all without LLM calls.

---

## Part A: Extend Base Types

### A1: Add signal report types to `src/agenetic/systems/base.py`

Add the following TypedDicts to `base.py`, after the existing type definitions and before `SystemState`. Use the definitions from `docs/signal_report_structure.md` as the canonical source. The types are:

- `SignalFeatures` — eight fields: `density`, `entropy`, `coherence`, `periodicity`, `noise_floor`, `impedance` (all `float`), `token_count` (`int`), `vocabulary_richness` (`float`)
- `SignalClassification` — three fields: `signal_type` (`Literal["steady_state", "transient", "periodic", "noise", "complex"]`), `confidence` (`float`), `components` (`list[str]`)
- `SignalDelta` — eight fields: six per-feature deltas (`float`), `aggregate_deviation` (`float`), `activated_limbs` (`list[int]`)
- `SignalReport` — four fields: `features` (`SignalFeatures`), `classification` (`SignalClassification`), `delta` (`SignalDelta`), `tick` (`int`), `input_hash` (`str`)

### A2: Add `CachedSignalPattern` type to `base.py`

This is used by the subconscious signal pattern cache:

- `input_hash` (`str`)
- `feature_vector` (`list[float]`) — `[density, entropy, coherence, periodicity, noise_floor, impedance]`
- `signal_type` (`str`)
- `outcome` (`str`) — one of `"escalated"`, `"reflex_response"`, `"rejected"`
- `response_pattern_id` (`str | None`)
- `encounter_count` (`int`)
- `last_seen_tick` (`int`)

### A3: Extend `SystemState` with `signal_report`

Add `signal_report: SignalReport | None` to the `SystemState` TypedDict. This field starts as `None` each cycle and is populated by sensory. Do not remove or rename any existing fields.

### A4: Add `ThreatAssessment` type to `base.py`

The immune system needs a structured output type that downstream systems (subconscious, conscious) can consume:

- `is_anomalous` (`bool`)
- `anomaly_scores` (`dict[str, float]`) — feature name → anomaly score (how far outside normal range)
- `matched_patterns` (`list[str]`) — pattern signatures from threat log that matched
- `threat_level` (`Literal["none", "low", "medium", "high", "critical"]`)
- `recommended_action` (`Literal["proceed", "flag", "quarantine", "reject"]`)

### A5: Add `threat_assessment` to `SystemState`

Add `threat_assessment: ThreatAssessment | None` to `SystemState`. Populated by immune, consumed by subconscious and conscious.

### A6: Add `SubconsciousOutput` type to `base.py`

- `escalation_recommended` (`bool`)
- `escalation_confidence` (`float`)
- `matched_pattern_ids` (`list[str]`) — IDs of cached patterns that matched
- `primed_associations` (`list[str]`) — descriptions of primed patterns for conscious context

### A7: Add `subconscious_output` to `SystemState`

Add `subconscious_output: SubconsciousOutput | None` to `SystemState`.

### A8: Add `signal_pattern_cache` to `SystemState`

Add `signal_pattern_cache: list[CachedSignalPattern]` to `SystemState`. This persists across cycles — subconscious writes to it, sleep will eventually prune it. Initialize as empty list.

---

## Part B: Implement Sensory System

### B1: Replace `src/agenetic/systems/sensory.py`

Replace the stub with a working implementation. The sensory system's job is **signal characterization** — it extracts structural features from input without interpreting semantic content.

**`process(state)` must:**

1. Read `state["input"]` (which is `Any` — handle string, dict, list, None gracefully; convert non-string inputs to their string representation for analysis)
2. Compute all `SignalFeatures`:
   - **`density`**: ratio of non-whitespace characters to total characters (normalized 0–1)
   - **`entropy`**: Shannon entropy over whitespace-delimited token frequency distribution (`-sum(p * log2(p))` where p = token_freq/total_tokens). Raw bits-per-token value, not normalized.
   - **`coherence`**: average pairwise Jaccard similarity between adjacent sentence-pairs (split on `.!?`). Range 0–1.
   - **`periodicity`**: ratio of repeated n-grams (bigrams) to total bigrams. Range 0–1.
   - **`noise_floor`**: ratio of single-character tokens + pure-punctuation tokens to total tokens. Range 0–1.
   - **`impedance`**: heuristic composite — average of: (a) ratio of non-ASCII characters, (b) ratio of lines containing mixed prose+code patterns (regex: line has both alphabetic words and `{}[]();` characters), (c) nesting depth indicator (max bracket/paren depth / 10, capped at 1.0). Range 0–1.
   - **`token_count`**: count of whitespace-delimited tokens (int)
   - **`vocabulary_richness`**: unique tokens / total tokens. Range 0–1.
3. Compute `SignalClassification`:
   - If `noise_floor > 0.4` → `"noise"`
   - Else if `periodicity > 0.3` → `"periodic"`
   - Else if entropy delta from field reference exceeds 2.0 in either direction → `"transient"`
   - Else if more than one of the above thresholds is close (within 80%) → `"complex"` with components listed
   - Else → `"steady_state"`
   - Confidence: 1.0 minus the normalized distance of the primary feature from its threshold (closer to threshold = lower confidence). Floor at 0.3.
4. Compute `SignalDelta`:
   - Reference values derived from orientational field: use the **mean of all limb weights** as the baseline expectation for each feature. (This is a v1 simplification — sleep will eventually set per-feature reference values.)
   - Each delta = measured - reference
   - `aggregate_deviation` = Euclidean distance of the six-feature delta vector
   - `activated_limbs` = limb IDs sorted by abs(delta) * limb_weight, descending. Include all limbs where the product exceeds 0.1.
5. Compute `input_hash`: SHA-256 hex digest of the string representation of input, truncated to 16 characters.
6. Assemble `SignalReport` with current tick from `state["metadata"]["tick"]`.
7. Write to `state["signal_report"]`.
8. Return updated state.

**`repair_check(state)` must:**
- Verify `state["signal_report"]` is not `None`
- Verify all `SignalFeatures` values are finite (not NaN, not inf)
- Verify `signal_type` is one of the five valid values
- Return `True` if all checks pass, `False` otherwise

**`apoptotic_condition(state)` must:**
- Return `True` if input is `None` AND has been `None` for 3+ consecutive ticks (track via a counter on the instance, not in state)
- Return `False` otherwise

**Implementation constraints:**
- Use only Python stdlib (`math`, `re`, `collections`, `hashlib`). No numpy, no nltk, no external libs.
- Handle edge cases: empty string input, single-token input, None input (produce a zeroed-out signal report with signal_type "noise" and confidence 1.0).
- All computation must be deterministic given the same input and field state.

---

## Part C: Implement Immune System

### C1: Replace `src/agenetic/systems/immune.py`

Replace the stub with a working implementation. The immune system's job is **signal anomaly detection** — it operates on the signal report, never on raw input semantics.

**`process(state)` must:**

1. Read `state["signal_report"]`. If `None`, set threat_assessment to a default "proceed" with no anomalies and return. (Sensory should have run first, but be defensive.)
2. **Innate immunity** — fixed threshold checks on signal features:
   - `entropy > 6.0` → anomaly score proportional to excess
   - `noise_floor > 0.35` → anomaly score proportional to excess
   - `impedance > 0.5` → anomaly score proportional to excess
   - `aggregate_deviation > 3.0` → anomaly score proportional to excess
   - `vocabulary_richness < 0.1` (suspiciously repetitive) → anomaly score proportional to deficit
   These thresholds are the "innate" immune response — hard-coded pattern recognition.
3. **Adaptive immunity** — check `state["immune_log"]` for pattern matches:
   - For each entry in the threat log, compute feature-vector distance between the current signal report's features and the logged pattern's signature
   - If distance < 0.5 (configurable threshold), consider it a match
   - Matched patterns increase overall threat assessment
   - Update `encounter_count` and `last_seen` on matched entries
4. **Compute threat level:**
   - Sum all anomaly scores. `none` if sum < 0.5, `low` if < 1.5, `medium` if < 3.0, `high` if < 5.0, `critical` if >= 5.0
5. **Compute recommended action:**
   - `none`/`low` → `"proceed"`
   - `medium` → `"flag"` (set escalation flag)
   - `high` → `"quarantine"` (set escalation flag + degraded flag)
   - `critical` → `"reject"` (set apoptotic flag)
6. Write `ThreatAssessment` to `state["threat_assessment"]`.
7. Set appropriate `state["flags"]` based on recommended action:
   - `"flag"` or `"quarantine"` → set `escalate_to_conscious = True`
   - `"quarantine"` → append `"immune"` to `degraded` list
   - `"reject"` → set `apoptotic = True`
8. If a genuinely new anomalous pattern is detected (threat_level >= "medium" and no matching pattern in log), add a new `ThreatEntry` to `state["immune_log"]` with the signal feature signature as the pattern string (JSON-serialized feature vector), encounter_count 1, confidence based on threat level, and current ISO timestamp.
9. Return updated state.

**`repair_check(state)` must:**
- Verify `state["threat_assessment"]` is not `None`
- Verify `threat_level` is one of the five valid values
- Verify `recommended_action` is one of the four valid values
- Return `True` if all checks pass

**`apoptotic_condition(state)` must:**
- Return `True` if `state["threat_assessment"]` is not None and `threat_level == "critical"` for 3+ consecutive ticks
- Return `False` otherwise

**Implementation constraints:**
- Use only Python stdlib (`json`, `math`, `datetime`). No external libs.
- The immune system reads `state["signal_report"]` — it does NOT read `state["input"]` directly. This is architecturally important: immune operates in the signal domain.
- For the adaptive immune pattern matching: the `pattern` field in `ThreatEntry` stores a JSON-serialized feature vector `[density, entropy, coherence, periodicity, noise_floor, impedance]`. Distance is Euclidean distance between vectors.

---

## Part D: Implement Subconscious System

### D1: Replace `src/agenetic/systems/subconscious.py`

Replace the stub with a working implementation. The subconscious system's job is **signal pattern priming** — it correlates the current signal against cached patterns from prior cycles.

**`process(state)` must:**

1. Read `state["signal_report"]`. If `None`, output a default "no recommendation" and return.
2. Read `state["threat_assessment"]`. Factor immune results into escalation decision.
3. **Pattern correlation** — compare current signal against `state["signal_pattern_cache"]`:
   - Extract feature vector from current signal report: `[density, entropy, coherence, periodicity, noise_floor, impedance]`
   - For each cached pattern, compute Euclidean distance between feature vectors
   - Matches: distance < 0.3 (configurable threshold)
   - Collect all matching pattern IDs and their outcomes
4. **Escalation decision:**
   - If immune threat_level >= "medium" → escalation_recommended = True, confidence = 0.9
   - Else if no cached patterns match (novel signal) AND aggregate_deviation > 1.5 → escalation_recommended = True, confidence = 0.7
   - Else if matched patterns exist AND majority outcome was "escalated" → escalation_recommended = True, confidence = proportion that were escalated
   - Else if matched patterns exist AND majority outcome was "reflex_response" → escalation_recommended = False, confidence = proportion that were reflex
   - Else (no matches, low deviation) → escalation_recommended = False, confidence = 0.5 (uncertain — default to not escalating)
5. **Build primed associations** — for each matched pattern, produce a human-readable string: `"Signal pattern [hash prefix] seen [N] times, last outcome: [outcome]"`
6. **Update cache** — add current signal to `state["signal_pattern_cache"]` as a new entry:
   - `input_hash` from signal report
   - `feature_vector` from signal report
   - `signal_type` from signal report
   - `outcome`: `"escalated"` if escalation_recommended else `"reflex_response"` (will be corrected by future sleep consolidation)
   - `response_pattern_id`: `None` for now
   - `encounter_count`: 1 (or increment if hash matches existing entry)
   - `last_seen_tick`: current tick
7. Set `state["flags"]["escalate_to_conscious"]` based on escalation decision. Note: don't override if immune already set it to True — only set, never unset.
8. Write `SubconsciousOutput` to `state["subconscious_output"]`.
9. Return updated state.

**`repair_check(state)` must:**
- Verify `state["subconscious_output"]` is not `None`
- Verify `escalation_confidence` is in range [0.0, 1.0]
- Return `True` if all checks pass

**`apoptotic_condition(state)` must:**
- Return `True` if `signal_pattern_cache` exceeds 10,000 entries (memory pressure — sleep should be pruning)
- Return `False` otherwise

**Implementation constraints:**
- Use only Python stdlib (`math`). No external libs.
- Reads `state["signal_report"]` and `state["threat_assessment"]` — does NOT read `state["input"]` directly.
- Cache size will grow unboundedly in this version. Sleep (future directive) will add pruning. For now, the apoptotic condition is the safety valve.

---

## Part E: Update Graph Wiring

### E1: Update `src/agenetic/network/graph.py`

Update the graph construction to:

1. Initialize `signal_report`, `threat_assessment`, `subconscious_output` as `None` in the default state
2. Initialize `signal_pattern_cache` as `[]` in the default state
3. Ensure the signal-domain systems run in order: sensory → immune → subconscious → (conditional routing to conscious or motor)
4. Update `GraphState` TypedDict to include the new state fields

The existing conditional routing (escalation flag → conscious, else → motor) should still work — the subconscious now actively sets the escalation flag based on its analysis rather than it always being False.

### E2: Update `src/agenetic/network/graph.py` state creation

Update `create_default_state()` to include the new fields with their default values (`None` for reports/assessments, `[]` for cache).

---

## Part F: Update Tests

### F1: Update `tests/test_systems.py`

Add tests for the three implemented systems. At minimum:

**Sensory tests:**
- Process a simple string input → signal report is populated with all fields
- Process empty string → signal report has signal_type "noise"
- Process None input → signal report has signal_type "noise", zeroed features
- Entropy calculation is deterministic (same input → same entropy)
- Coherence of a single-sentence input is defined (edge case)
- Density of all-whitespace input is 0.0
- repair_check returns True for valid signal report
- repair_check returns False when signal_report is None
- input_hash is consistent for same input

**Immune tests:**
- Process with normal signal report → threat_level "none", action "proceed"
- Process with high-entropy signal report → anomaly detected
- Process with high-noise signal report → anomaly detected
- Process with high-impedance signal report → anomaly detected
- Threat level "critical" sets apoptotic flag
- Threat level "medium" sets escalation flag
- New anomalous pattern is added to immune_log
- Adaptive matching: previously seen anomalous pattern has higher threat score on re-encounter
- Process with signal_report=None → default "proceed" assessment

**Subconscious tests:**
- Process with no cached patterns, low deviation → no escalation
- Process with no cached patterns, high deviation → escalation recommended
- Process with immune threat_level "medium" → escalation recommended regardless
- Cached pattern matching: same input processed twice → second time matches cache
- Escalation flag is never unset if immune already set it
- Cache grows by one entry per process call
- Apoptotic condition triggers at 10,000+ cache entries
- repair_check returns True for valid output

### F2: Update `tests/test_graph.py`

- Graph still compiles with new state fields
- Processing a simple input produces a populated signal_report
- Processing an input runs all three signal-domain systems in order (check routing_history)
- High-deviation input triggers escalation to conscious
- Normal input bypasses conscious (reflex path)

### F3: Keep existing tests passing

All 94 existing tests must continue to pass. The new state fields should be backward-compatible (existing tests may need default values for new fields in their test fixtures).

---

## Part G: Update CLAUDE.md

### G1: Update project structure in `CLAUDE.md`

Add the two new docs files to the project structure section:

```
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DIRECTIVES.md
│   ├── architecture_amendment.md    ← Signal-semantics boundary
│   └── signal_report_structure.md   ← Signal report TypedDict spec
```

---

## Scope Boundaries

**DO:**
- Add signal report types to `base.py`
- Replace sensory, immune, and subconscious stubs with working implementations
- Update graph wiring to handle new state fields
- Write comprehensive tests for all three systems
- Keep all existing tests passing
- Update CLAUDE.md project structure
- Use only Python stdlib for all implementations (no numpy, no nltk, no external libs)
- Read `docs/architecture_amendment.md` and `docs/signal_report_structure.md` for design rationale

**DO NOT:**
- Implement conscious, motor, sleep, or genetic systems (those remain stubs)
- Make LLM calls from any signal-domain system
- Modify `docs/ARCHITECTURE.md` (amendment stays as separate doc for now)
- Modify `docs/architecture_amendment.md` or `docs/signal_report_structure.md`
- Modify any historical handoff files (`handoff/001_directive.md`, `handoff/001_response.md`)
- Add dependencies to `pyproject.toml` (everything is stdlib)
- Change the orientational field implementation (the write-access restriction, the 18 limbs, etc.)
- Modify `topology.py` (connection matrix is unchanged)

## Deliverables

| File | Action | Description |
|------|--------|-------------|
| `src/agenetic/systems/base.py` | Updated | Add SignalReport, ThreatAssessment, SubconsciousOutput, CachedSignalPattern types; extend SystemState |
| `src/agenetic/systems/sensory.py` | Replaced | Working signal characterization implementation |
| `src/agenetic/systems/immune.py` | Replaced | Working signal anomaly detection implementation |
| `src/agenetic/systems/subconscious.py` | Replaced | Working signal pattern priming implementation |
| `src/agenetic/network/graph.py` | Updated | New state fields in GraphState and create_default_state() |
| `tests/test_systems.py` | Updated | Tests for sensory, immune, subconscious |
| `tests/test_graph.py` | Updated | Tests for signal-domain graph flow |
| `CLAUDE.md` | Updated | Project structure reflects new docs |
| `handoff/002_directive.md` | This file |
| `handoff/002_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `SignalReport`, `SignalFeatures`, `SignalClassification`, `SignalDelta` types exist in `base.py`
- [ ] `ThreatAssessment` type exists in `base.py`
- [ ] `SubconsciousOutput` and `CachedSignalPattern` types exist in `base.py`
- [ ] `SystemState` has `signal_report`, `threat_assessment`, `subconscious_output`, `signal_pattern_cache` fields
- [ ] `SensorySystem.process()` produces a valid `SignalReport` from string input
- [ ] `SensorySystem.process()` handles None input gracefully (zeroed report, "noise" type)
- [ ] `SensorySystem.process()` handles empty string input gracefully
- [ ] `SensorySystem` uses only Python stdlib (no imports outside stdlib)
- [ ] `SensorySystem` does not make LLM calls
- [ ] `ImmuneSystem.process()` produces a valid `ThreatAssessment` from signal report
- [ ] `ImmuneSystem` reads `signal_report` not `input` (signal domain only)
- [ ] `ImmuneSystem` innate thresholds produce anomalies for high entropy/noise/impedance
- [ ] `ImmuneSystem` adaptive matching updates encounter counts on re-seen patterns
- [ ] `ImmuneSystem` adds new anomalous patterns to `immune_log`
- [ ] `ImmuneSystem` threat_level "critical" sets `flags.apoptotic`
- [ ] `ImmuneSystem` uses only Python stdlib
- [ ] `SubconsciousSystem.process()` produces a valid `SubconsciousOutput`
- [ ] `SubconsciousSystem` reads `signal_report` and `threat_assessment`, not `input`
- [ ] `SubconsciousSystem` performs pattern correlation against signal_pattern_cache
- [ ] `SubconsciousSystem` adds entries to signal_pattern_cache
- [ ] `SubconsciousSystem` never unsets escalation flag if immune already set it
- [ ] `SubconsciousSystem` apoptotic at 10,000+ cache entries
- [ ] `SubconsciousSystem` uses only Python stdlib
- [ ] Graph compiles with new state fields
- [ ] Graph processes input through sensory → immune → subconscious → routing
- [ ] All new tests pass
- [ ] All 94 original tests still pass (backward compatibility)
- [ ] `CLAUDE.md` project structure updated
- [ ] No files outside deliverables list modified
- [ ] No historical handoff files edited
- [ ] Git commit with descriptive message and pushed to GitHub
