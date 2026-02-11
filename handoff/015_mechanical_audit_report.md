# Directive 015 — Mechanical Audit Report

**Scale:** 16 source files, 9 test files, ~7,094 LOC, 320 tests, 83 thresholds
**Date:** 2026-02-10

---

## 1. Summary

| Metric | Count |
|--------|-------|
| Source files | 16 |
| Test files | 9 |
| Source LOC | ~3,558 |
| Test LOC | ~3,536 |
| Total LOC | ~7,094 |
| Tests passing | 320 |
| Tests skipped | 2 (both require ANTHROPIC_API_KEY) |
| Limb constants defined | 18 |
| Hardcoded thresholds | 83 |

---

## 2. Architecture Document Summaries

### docs/ARCHITECTURE.md (~470 lines)
Full v2 specification of the single-cell architecture. Defines seven systems (sensory, immune, subconscious, conscious, motor, sleep, genetic), each with a relationship to information, tick rate, repair check, and apoptotic trigger. Describes connection matrix (primary/secondary/absent), orientational field (18 Asparsa limbs), and cross-cutting concerns (inline repair, homeostatic regulation, apoptosis). Includes engineering assignments for limb-to-feature mappings.

### docs/architecture_amendment.md (~60 lines)
Documents the signal-semantics boundary. Text is signal before it is language. Three processing domains: signal domain (sensory, immune, subconscious — every cycle, cheap, no LLM), semantic domain (conscious — on escalation, expensive, LLM), and output domain (motor — on demand). The escalation boundary between subconscious and conscious is the crossing point from signal processing into meaning-making.

### references/asparsa_limbs.md
The 18 limb principles as one-line definitions. These are the genetic seed values used in `orientational.py`. Each limb has id (1-18), Sanskrit name, English name, and principle text.

### references/conceptual_archaeology.md
Synthesis of 8 earlier concept documents tracing philosophical lineage. Section V contains preliminary limb-to-feature mappings across signal/semantic/meta domains. Mappings are hypotheses, not specifications.

---

## 3. Source File Reports

### 3.1 src/agenetic/systems/base.py (355 LOC)

**Purpose:** Defines all shared types, limb constants, and the BaseSystem abstract class.

**Exports:** 18 TypedDicts (ThreatEntry, Metadata, Flags, FieldLimb, FieldState, SignalFeatures, SignalClassification, SignalDelta, SignalReport, CachedSignalPattern, ThreatAssessment, SubconsciousOutput, MotorOutput, ResponseDecision, ExpressionDirectives, Lineage, ConsciousOutput, SystemState), BaseSystem ABC, 18 limb ID constants (PRAKASA_ID through ASPARSA_YOGA_ID), CONVERGENT_CLUSTER_IDS list, helper functions (get_limb_weight, mean_limb_weight, compute_target_profile).

**Imports (project):** None — this is the root dependency.

**Key data:**
- 18 limb ID constants (1-18)
- CONVERGENT_CLUSTER_IDS = [12, 14, 15, 17, 18]
- compute_target_profile: density=0.8+(mean_w-0.5)*0.4, entropy=3.5+(tarka_w-0.5)*3.0, coherence=0.35+(samatvam_w-0.5)*0.7, periodicity=(0.5-prakasa_w)*0.6, noise_floor=(0.5-sraddha_w)*0.6, impedance=(0.5-nivrtti_w)*0.6
- get_limb_weight default: 0.5
- mean_limb_weight default: 0.5

**Connections:** Imported by every other source file. Central dependency hub.

**Observations:**
- All 18 limb IDs are assigned. ATMA_VICHARA_ID (6) has a constant but no signal-domain feature mapping in compute_target_profile.
- compute_target_profile returns bigram_entropy=0.0, token_count=0, vocabulary_richness=0.0 as unused placeholders.
- MotorOutput TypedDict does not include `conscious_strategy` key — motor.py adds it dynamically (line 176).
- SystemState uses `Any` for `input` field — no type constraint on what enters the system.

---

### 3.2 src/agenetic/field/orientational.py (181 LOC)

**Purpose:** Implements the orientational field — shared self-model with token-authenticated write access.

**Exports:** OrientationalField class.

**Imports (project):** base.FieldLimb, base.FieldState, sleep.SleepSystem.

**Key data:**
- _DEFAULT_LIMBS: 18 FieldLimb dicts, all weights at 0.5
- Each limb has id, name, english_name, principle, weight

**Connections:** Read by all systems via state["field"]. Write only by SleepSystem.WRITE_TOKEN.

**Observations:**
- Imports SleepSystem at module level to access WRITE_TOKEN for authorization. This creates a circular dependency path: orientational imports sleep, sleep imports base, base is imported by orientational.
- read() returns a shallow copy of the limbs list (list() call), but each limb dict is the same reference as _limbs entries. write() deep-copies with {**limb}.
- Limb 14 is named "Nivrtti-Rest" in orientational.py. The constant REST_AS_REALIZATION_ID in base.py refers to it. These names differ from the architecture doc naming.

---

### 3.3 src/agenetic/systems/sensory.py (398 LOC)

**Purpose:** Signal characterization — extracts 9 structural features from input without semantic interpretation.

**Exports:** SensorySystem class, _compute_input_hash (used in tests).

**Imports (project):** base.BaseSystem, base.SignalClassification, base.SignalDelta, base.SignalFeatures, base.SignalReport, base.SystemState, base.compute_target_profile.

**Key data:**
- 9 signal features: density, entropy, coherence, periodicity, noise_floor, impedance, bigram_entropy, token_count, vocabulary_richness
- Classification thresholds: noise_floor > 0.4, periodicity > 0.3, entropy_delta_abs > 2.0
- "Close" thresholds at 80%: noise 0.32, periodicity 0.24, transient 1.6
- Confidence: min 0.3, complex 0.5

**Connections:** Produces signal_report consumed by immune, subconscious, conscious. Uses compute_target_profile from base.py for delta computation.

**Observations:**
- _compute_delta uses compute_target_profile as reference — same function motor uses for target. Sensory and motor share reference formulas.
- activated_limbs computation uses max_abs_delta across all features multiplied by each limb weight. Product > 0.1 threshold activates a limb. This means ALL limbs activate for any non-trivial input when weights are at 0.5 (max_abs_delta * 0.5 > 0.1 requires max_abs_delta > 0.2).
- Empty/None input classified as "noise" with confidence 1.0.
- Apoptotic: 3 consecutive None inputs. Counter is instance state (_consecutive_none_count).

---

### 3.4 src/agenetic/systems/immune.py (211 LOC)

**Purpose:** Signal anomaly detection through innate thresholds and adaptive pattern matching.

**Exports:** ImmuneSystem class.

**Imports (project):** base.BaseSystem, base.SystemState, base.ThreatAssessment, base.ThreatEntry.

**Key data:**
- ADAPTIVE_MATCH_THRESHOLD = 0.5
- Innate thresholds: entropy > 6.0, noise_floor > 0.35, impedance > 0.5, aggregate_deviation > 3.0, vocabulary_richness < 0.1
- Threat level boundaries: total_score <0.5→none, <1.5→low, <3.0→medium, <5.0→high, ≥5.0→critical
- Action mapping: none/low→proceed, medium→flag, high→quarantine, critical→reject
- New pattern confidence: medium=0.6, high=0.8, critical=1.0

**Connections:** Reads signal_report. Writes threat_assessment, updates immune_log and flags.

**Observations:**
- Immune sets escalate_to_conscious=True on flag/quarantine actions (medium/high threat). This can be overridden by subconscious, which explicitly resets the flag.
- Sets apoptotic=True on reject (critical threat level).
- Adaptive matching uses Euclidean distance < 0.5 on 6-element feature vectors stored as JSON strings.
- Adaptive encounter scoring: confidence * (1.0 + 0.1 * encounter_count). Accumulative — multiple matches add up.
- Apoptotic: 3 consecutive critical ticks. Counter is instance state.

---

### 3.5 src/agenetic/systems/subconscious.py (189 LOC)

**Purpose:** Pattern correlation and escalation recommendation based on signal novelty, deviation, and threat.

**Exports:** SubconsciousSystem class, MATCH_THRESHOLD (used indirectly by tests).

**Imports (project):** base.BaseSystem, base.CachedSignalPattern, base.SubconsciousOutput, base.SystemState.

**Key data:**
- MATCH_THRESHOLD = 0.3
- Escalation conditions: threat medium/high/critical (confidence 0.9), novel + aggregate_deviation > 1.5 (confidence 0.7), cached escalated > reflex (confidence = ratio), tie (no escalation, 0.5), default (no escalation, 0.5)

**Connections:** Reads signal_report and threat_assessment. Writes subconscious_output, signal_pattern_cache, flags.

**Observations:**
- Explicitly sets escalate_to_conscious to True or False (both branches). This means subconscious always overwrites whatever immune set.
- Cache entries use input_hash for exact match and feature_vector for similarity match. Both are used: existing_idx lookup by hash, matched_ids by vector distance.
- Outcome is "escalated" or "reflex_response" — stored in cache. Used for subsequent pattern-based escalation decisions.
- Apoptotic: cache > 10000 entries. No pruning mechanism exists (sleep is a stub).

---

### 3.6 src/agenetic/systems/conscious.py (440 LOC)

**Purpose:** Deliberation — gate evaluation, expression directive assembly, deliberator invocation.

**Exports:** ConsciousSystem class.

**Imports (project):** base (12 limb IDs, BaseSystem, ConsciousOutput, ExpressionDirectives, Lineage, ResponseDecision, SystemState, get_limb_weight), deliberator (Deliberator, DeliberationRequest — TYPE_CHECKING only).

**Key data:**
- _LIMB_NAMES: dict mapping all 18 limb IDs to names
- Gate priority: immune_override → areka_suppression → nivrtti_pause → resting_stance_suppression → default_proceed
- Gate thresholds: areka_w > 0.7 + signal_type=="noise", nivrtti_w > 0.7 + agg_dev < 0.5, resting_stance > 0.8 + agg_dev < 0.3
- Active limb range: weight < 0.4 or weight > 0.6
- No-Position: weight > 0.6 → suppress_identity=True
- Fourfold State: >0.7 reflective, <0.3 still, <0.4 consolidated, else active
- Low confidence streak threshold: confidence < 0.2 increments streak, ≥0.2 resets

**Connections:** Reads signal_report, threat_assessment, subconscious_output, field. Writes conscious_output, may update flags (degraded), metadata (streak).

**Observations:**
- immune_override gate condition checks for threat_action=="escalate". No system currently sets recommended_action to "escalate" — the immune system uses "proceed", "flag", "quarantine", "reject". This means the immune_override gate condition can never fire through the current system.
- Accepts deliberator=None for gate-only mode. When gate proceeds but no deliberator, produces degraded output with confidence=0.0.
- _compress_signal_report strips token_count, vocabulary_richness from features and activated_limbs from deltas.
- Escalation reason determination: "immune_override" if threat_assessment.recommended_action=="escalate" (unreachable per above), "novel_input" if subconscious recommended, else "default_escalation".

---

### 3.7 src/agenetic/systems/deliberator.py (108 LOC)

**Purpose:** Protocol definition for LLM backends + MockDeliberator for testing.

**Exports:** DeliberationRequest class, Deliberator Protocol, MockDeliberator class.

**Imports (project):** base.ConsciousOutput.

**Key data:**
- DeliberationRequest: 8 fields (input_text, signal_summary, threat_summary, subconscious_summary, field_state, active_limbs, resting_stance, expression_directives)
- MockDeliberator: returns confidence=0.8, proceed=True, deliberation_model="mock", strategy from constructor default_strategy

**Connections:** Consumed by conscious.py and deliberator_anthropic.py.

**Observations:**
- MockDeliberator tracks call_count and last_request. Used extensively in tests.
- MockDeliberator's gate_evaluation is hardcoded: {"proceed": True, "reason": "default_proceed"}. This gets overwritten by conscious.py line 135 (patches gate_evaluation into lineage).
- Deliberator Protocol uses @runtime_checkable — isinstance() works.

---

### 3.8 src/agenetic/systems/deliberator_anthropic.py (104 LOC)

**Purpose:** Anthropic API deliberator implementation.

**Exports:** AnthropicDeliberator class.

**Imports (project):** base.ConsciousOutput, deliberator.DeliberationRequest, prompt_assembly.assemble_system_prompt, prompt_assembly.assemble_user_message.

**Key data:**
- DEFAULT_MODEL = "claude-sonnet-4-20250514"
- max_tokens = 1024
- JSON parse fallback confidence: 0.3
- Successful parse confidence from response data, default 0.5

**Connections:** Uses prompt_assembly for prompt building. Called by conscious via Deliberator protocol.

**Observations:**
- Requires ANTHROPIC_API_KEY environment variable at __init__ time.
- Always sets proceed=True in output — cannot produce suppression. Gate suppression happens before this is called.
- gate_evaluation is hardcoded to {"proceed": True, "reason": "default_proceed"} — same as MockDeliberator. Gets overwritten by conscious.py.
- expression field in output is request.expression_directives (passthrough), not computed.

---

### 3.9 src/agenetic/systems/prompt_assembly.py (380 LOC)

**Purpose:** Translates field state into behavioral framing for LLM deliberation prompts.

**Exports:** LIMB_INSTRUCTIONS dict, LIMB_INTERACTIONS list, compute_intensity, build_limb_instructions, build_resting_stance_instruction, assemble_system_prompt, assemble_user_message.

**Imports (project):** deliberator.DeliberationRequest.

**Key data:**
- LIMB_INSTRUCTIONS: 13 entries for limbs 1-11, 13, 16. High/low instruction pairs.
- LIMB_INTERACTIONS: 6 interaction rules for limb pairs {2,5}, {3,7}, {1,10}, {11,4}, {2,7}, {8,3}
- Intensity descriptors: <0.3 slightly, <0.6 moderately, <0.85 strongly, ≥0.85 intensely
- Resting stance levels: <0.55 none, <0.65 slightly, <0.75 elevated, <0.85 high, ≥0.85 very high
- Interaction conditions: both_high (all > 0.6), both_low (all < 0.4), high_low (mixed)

**Connections:** Called by deliberator_anthropic.py and tested in test_prompt_assembly.py.

**Observations:**
- LIMB_INSTRUCTIONS covers 13 of 18 limbs. Missing: limbs 12 (Bodhi), 14 (Rest-as-Realization), 15 (Mirror), 17 (Ajati), 18 (Asparsa-Yoga). These 5 are the CONVERGENT_CLUSTER_IDS — they contribute to resting_stance composite rather than individual instructions.
- Limb 6 (Atma-Vichara) has instructions but no signal-domain feature mapping. It appears in prompt_assembly (semantic domain) but not in compute_target_profile (signal domain).
- _OUTPUT_FORMAT lists 5 strategies: "direct_response", "trace_contradiction", "preserve_ambiguity", "threshold_acknowledgment", "minimal_reflection". MockDeliberator always returns default_strategy ("direct_response").

---

### 3.10 src/agenetic/systems/codec.py (52 LOC)

**Purpose:** Protocol definition for motor output codecs.

**Exports:** CodecResult TypedDict, Codec Protocol.

**Imports (project):** base.SignalFeatures.

**Key data:**
- CodecResult: output (str), strategies_applied (list[str]), transform_magnitude (float)
- Codec protocol: name property, encode() method, quality_check() method

**Connections:** Implemented by TextCodec. Protocol checked at runtime.

**Observations:**
- Codec.encode() takes input_data as str. Motor.process() converts to str before delegating.
- quality_check takes (original, output) but Codec Protocol doesn't specify return behavior for empty output (TextCodec returns False for empty).

---

### 3.11 src/agenetic/systems/text_codec.py (534 LOC)

**Purpose:** Text restructuring codec — 6 modulation strategies + 4 limb gates.

**Exports:** TextCodec class, all 6 _modulate functions, _compute_transform_magnitude, _blend_toward_original.

**Imports (project):** base (AREKA_ID, KSETRA_JNANA_ID, MAYAVADA_ID, SignalFeatures, SVADHARMA_ID, get_limb_weight), codec.CodecResult.

**Key data:**
- 6 modulation strategies: density, entropy, coherence, impedance, periodicity, noise_floor
- 4 limb gates: Areka suppression (> 0.3), Svadharma threshold scaling (0.5 + svadharma_w), Ksetra-Jnana delta scaling (0.5 + ksetra_w * 0.5), Mayavada cap (< 0.45 activates)
- Strategy delta thresholds (base): density 0.05, entropy 0.5, coherence 0.1, impedance 0.05, periodicity 0.05, noise 0.05
- Areka codec gate: areka_w > 0.3 AND noise_floor > 0.3 AND entropy > 5.0
- Mayavada: activates when mayavada_w < 0.45, max_allowed = 1.0 - mayavada_w
- Quality check: non-empty output, length ratio 0.2-3.0x, token overlap ≥ 0.2

**Connections:** Instantiated by MotorSystem. Functions re-exported via motor.py for backward compatibility.

**Observations:**
- Areka threshold in text_codec (> 0.3) differs from Areka threshold in conscious gate (> 0.7). These are two independent suppression mechanisms at different sensitivity levels.
- Mayavada cap at mayavada_w < 0.45. At default weight 0.5, Mayavada cap is inactive (0.5 ≥ 0.45). Only activates when Mayavada weight is lowered below 0.45.
- _blend_toward_original has O(n²) behavior: for each position, it counts changes in all prior positions. For typical text lengths this is not a performance concern.
- _modulate_entropy sentence splitting uses a fixed set of conjunctions. Splitting at the first conjunction only — not recursive.
- _modulate_coherence bridge word strategy: takes last alpha word from prior sentence and prepends to next. This can produce grammatically awkward text.
- Svadharma threshold_scale at default (0.5): scale = 0.5 + 0.5 = 1.0 (neutral). At 0.0: scale = 0.5 (halved thresholds, more strategies fire). At 1.0: scale = 1.5 (50% higher thresholds, fewer strategies fire).
- Ksetra-Jnana delta_scale at default (0.5): scale = 0.5 + 0.5 * 0.5 = 0.75. At 0.0: 0.5. At 1.0: 1.0. Default is not 1.0 — at default weights, deltas are scaled to 75%.

---

### 3.12 src/agenetic/systems/motor.py (190 LOC)

**Purpose:** Orchestrator — target computation, conscious integration, codec delegation, repair.

**Exports:** MotorSystem class. Re-exports from text_codec: _modulate_density, _modulate_entropy, _modulate_coherence, _modulate_impedance, _modulate_periodicity, _modulate_noise_floor, _compute_transform_magnitude, _blend_toward_original. Also re-exports from base: all limb IDs, _compute_target_profile, _get_limb_weight, _mean_weight.

**Imports (project):** base (11 limb IDs, BaseSystem, MotorOutput, SignalFeatures, SystemState, compute_target_profile, get_limb_weight, mean_limb_weight, NIVRTTI_ID), text_codec (TextCodec + 8 functions).

**Key data:**
- Conscious suppression check: conscious_output exists AND proceed is False
- Empty input check: text is falsy
- Fallback on repair failure: original text, transform_magnitude=0.0
- Conscious strategy recording: conscious_output.decision.strategy

**Connections:** Reads input, field, signal_report, conscious_output. Writes motor_output. Delegates to TextCodec.

**Observations:**
- motor.py imports NIVRTTI_ID from base but never uses it in its own code. It is imported but unused at runtime.
- Re-exports 8 functions from text_codec and 3+ identifiers from base. Comment says "for backward compatibility with tests" — test_motor.py imports from motor.py rather than text_codec.py.
- conscious_strategy is added as a dynamic key on motor_output dict (line 176). The MotorOutput TypedDict in base.py doesn't declare this key.
- When conscious_output exists and proceed=True but no signal_report, motor uses neutral defaults for current features.
- Apoptotic: returns True if input is None OR 3 consecutive repair failures.

---

### 3.13 src/agenetic/systems/sleep.py (56 LOC)

**Purpose:** Stub — holds WRITE_TOKEN for field authorization.

**Exports:** SleepSystem class.

**Imports (project):** base.BaseSystem, base.SystemState.

**Key data:**
- WRITE_TOKEN = "sleep_system_authorized"

**Connections:** process() is pass-through (returns state unchanged). Token used by orientational.py write authorization.

**Observations:**
- Stub implementation. process() returns state unchanged. repair_check returns True. apoptotic_condition returns False.
- No consolidation logic (pruning, strengthening, epigenetic feedback) is implemented.
- WRITE_TOKEN is a plain string constant — not a cryptographic secret.

---

### 3.14 src/agenetic/systems/genetic.py (50 LOC)

**Purpose:** Stub — read-only genetic seed.

**Exports:** GeneticSystem class.

**Imports (project):** base.BaseSystem, base.SystemState.

**Key data:** None beyond base class.

**Connections:** process() is pass-through. tick_rate is "read_only".

**Observations:**
- Stub implementation. No actual genetic seed data is stored here — the seed is the 18 limbs in orientational.py.
- Not actively routed in the graph (Phase 1). build_graph() accepts genetic as parameter but doesn't add it as a node.

---

### 3.15 src/agenetic/network/graph.py (177 LOC)

**Purpose:** LangGraph wiring — builds runnable graph from seven systems.

**Exports:** GraphState TypedDict, create_default_state, build_graph.

**Imports (project):** field.orientational.OrientationalField, base.BaseSystem, base.SystemState.

**Key data:**
- GraphState: mirrors SystemState with looser typing (Any, dict, list)
- create_default_state: tick=0, escalate_to_conscious=False, all outputs None
- _should_escalate: checks flags.escalate_to_conscious
- Phase 1 routing: sensory → immune → subconscious → conditional(conscious/motor) → motor → END

**Connections:** Imports OrientationalField, BaseSystem. All test files import from here.

**Observations:**
- GraphState uses `Any` for signal_report, threat_assessment, subconscious_output, conscious_output, motor_output. SystemState in base.py uses specific TypedDicts | None. The types don't exactly match.
- build_graph accepts sleep and genetic parameters but never adds them as nodes. They are unused.
- _make_node wrapper: runs process(), then repair_check(). On repair failure, adds system name to degraded list.
- _make_node builds full SystemState from GraphState, including .get() for optional fields with defaults.

---

### 3.16 src/agenetic/network/topology.py (133 LOC)

**Purpose:** Connection matrix data — which systems connect to which.

**Exports:** ConnectionType enum, Connection dataclass, SYSTEM_NAMES, PRIMARY_CONNECTIONS, SECONDARY_CONNECTIONS, ALL_CONNECTIONS, get_connections, connection_exists, get_weight.

**Imports (project):** None (only stdlib).

**Key data:**
- SYSTEM_NAMES: 7 system names
- PRIMARY_CONNECTIONS: 17 connections at weight 1.0
- SECONDARY_CONNECTIONS: 6 connections at weight 0.5
- ALL_CONNECTIONS: 23 total
- Absent by design: any(except sleep)→genetic, motor→sensory, genetic→motor

**Connections:** Standalone data module. Not used by graph.py at runtime — graph routing is hardcoded.

**Observations:**
- topology.py defines connection weights but graph.py does not read them. The graph routing is hardcoded (Phase 1 simplified routing). The topology data structure is for Phase 2.
- The absent connections are documented in comments but not enforced programmatically (the test file verifies them).

---

## 4. Test File Reports

### 4.1 tests/test_systems.py (515 LOC, 94 tests)

**What it tests:** All seven systems' interface conformance (parametrized) + system-specific tests for sensory (20), immune (12), subconscious (10).

**Coverage gaps:** Sleep system only tested via parametrized interface (7 tests). Genetic system only tested via parametrized interface (7 tests). No system-specific sleep or genetic tests.

**Observations:**
- Parametrized fixture instantiates each system class with no arguments. ConsciousSystem() gets deliberator=None.
- _make_sample_state() populates signal_report, threat_assessment, subconscious_output, motor_output so repair_check passes for all systems.
- TestSubconsciousSystem._make_signal_state explicitly sets escalate_to_conscious=False in setup.

---

### 4.2 tests/test_graph.py (222 LOC, 18 tests)

**What it tests:** Graph compilation, execution, routing history, escalation skip, field access control, signal-domain flow.

**Coverage gaps:** No test for apoptotic flag propagation through the graph. No test for degradation propagation through the graph.

**Observations:**
- _build_default_graph() always uses MockDeliberator.
- test_no_escalation_skips_conscious pre-computes signal features to seed cache with reflex_response — sophisticated setup to avoid natural escalation.
- Comment in test_routing_history_recorded says "Default escalate_to_conscious=True" — this is stale (default is now False as of D014). The test still passes because "test" input naturally escalates.

---

### 4.3 tests/test_topology.py (144 LOC, 24 tests)

**What it tests:** Connection matrix verification — all primary, secondary, and absent connections match architecture spec.

**Coverage gaps:** None for its scope. Covers all 17 primary, 6 secondary, and 3 absent connections.

**Observations:**
- Pure data verification, no behavioral tests. Tests that the static topology matches the architecture document.

---

### 4.4 tests/test_motor.py (621 LOC, 58 tests)

**What it tests:** Motor basics (11), determinism (2), field sensitivity (3), repair/apoptotic (4), individual strategies (9), helpers (5), Tarka sentence-level (3), Sraddha noise (3), Mayavada cap (5), Areka gate (4), Svadharma selectivity (3), Ksetra-Jnana sensitivity (3), integration (3).

**Coverage gaps:** No test for motor behavior when signal_report is None (uses neutral defaults). No test for fallback_to_original path with specific inputs. test_low_mayavada_constrains_output has `pass` (acknowledged as needing revision).

**Observations:**
- Imports from motor.py (re-exported functions), not directly from text_codec.py.
- _vary_single_limb sets all other limbs to baseline (0.5) for isolation.
- HIGH_NOISE_TEXT uses punctuation and single chars for Areka gate testing.
- Some Areka/Mayavada tests use conditional assertions (if noise_floor > 0.3 and entropy > 5.0) — the assertion is conditional on input characteristics.

---

### 4.5 tests/test_round_trip.py (493 LOC, 44 tests)

**What it tests:** Motor→sensory feedback loop (6 basics), parameterized calibration sweep at 0.0 (18 tests), parameterized sweep at 1.0 (18 tests), calibration summary (1), multi-input calibration surface (1).

**Coverage gaps:** No assertion on specific limb-to-feature mappings — sweep records data for analysis only.

**Observations:**
- CALIBRATION_INPUTS: 5 input types (clean_prose, noisy_text, short_input, code_like, long_repetitive).
- _LIMB_NAMES defined locally — duplicates the same mapping in conscious.py and orientational.py.
- test_calibration_summary runs 36 sweep points (18 limbs x 2 weights). test_calibration_surface runs 180 points (5 inputs x 18 limbs x 2 weights).
- Areka suppression handled specially in sweep: empty output uses zeroed features.

---

### 4.6 tests/test_conscious.py (723 LOC, 32 tests)

**What it tests:** Gate logic (9), ConsciousOutput structure (3), Deliberator protocol (3), integration with MockDeliberator (8), graph integration (1), prompt observations (6), API tests (2 skipped).

**Coverage gaps:** No test for the specific case where immune sets escalate_to_conscious=True and subconscious overrides it. No test for consecutive low-confidence apoptotic using real deliberator.

**Observations:**
- Helper functions create controlled states with specific field overrides, signal types, and threat actions.
- test_gate_immune_override_always_proceeds tests with threat_action="escalate" — but no system currently produces "escalate" as recommended_action.
- Prompt observation tests verify structural prompt differences without asserting LLM behavior.

---

### 4.7 tests/test_prompt_assembly.py (282 LOC, 24 tests)

**What it tests:** Intensity computation (4), individual instructions (4), interactions (6), resting stance (5), full assembly (3), regression (2).

**Coverage gaps:** No test for assemble_user_message. No test for non-active state_awareness in full prompt assembly.

**Observations:**
- Tests cover all 6 interaction rules and all 4 intensity levels.
- test_inactive_limb_excluded acknowledges that build_limb_instructions doesn't filter — conscious.py does the filtering before calling.
- Regression test verifies deliberator_anthropic.py imports from prompt_assembly (not hardcoded).

---

### 4.8 tests/test_codec.py (228 LOC, 12 tests)

**What it tests:** Protocol conformance (3), behavioral equivalence with old motor (4), quality check (2), motor delegation (3).

**Coverage gaps:** No test for quality_check boundary conditions (ratio exactly 3.0, overlap exactly 0.2). No test for Svadharma/Ksetra-Jnana effects through codec.

**Observations:**
- Equivalence tests verify TextCodec produces same behavior as pre-refactor motor.
- test_encode_mayavada_cap tests both capped (0.44) and uncapped (0.5) — validates the 0.45 boundary.
- Imports AREKA_ID, MAYAVADA_ID from base, KSETRA_JNANA_ID aliased in test.

---

### 4.9 tests/test_integration.py (308 LOC, 16 tests)

**What it tests:** End-to-end path tests: reflex (4), escalated (4), suppression (3), routing decisions (3), cross-path consistency (2).

**Coverage gaps:** No test for the degraded-conscious path through the full graph. No test for multi-cycle graph invocation.

**Observations:**
- 4 carefully selected input constants: REFLEX_INPUT (agg_dev ~0.73), ESCALATION_INPUT (agg_dev ~3.57), NOISE_INPUT (classified "noise", agg_dev ~1.75), THREAT_INPUT (medium threat).
- _get_cached_pattern utility pre-computes signal features for cache seeding.
- Suppression path tests use Areka weight 0.9 and NOISE_INPUT to trigger conscious gate → conscious_suppression → motor empty output.

---

## 5. Cross-Cutting Observations

### A. Type Flow

Data flows through the graph as `GraphState` (defined in graph.py):

```
Input → sensory.process(SystemState) → signal_report (SignalReport)
      → immune.process(SystemState) → threat_assessment (ThreatAssessment)
      → subconscious.process(SystemState) → subconscious_output (SubconsciousOutput), signal_pattern_cache, flags
      → [conditional] conscious.process(SystemState) → conscious_output (ConsciousOutput)
      → motor.process(SystemState) → motor_output (MotorOutput)
```

**State type at each handoff:**
- `state["input"]` is `Any` throughout — never typed or validated.
- `state["signal_report"]` starts as None, becomes SignalReport (dict) after sensory.
- `state["threat_assessment"]` starts as None, becomes ThreatAssessment (dict) after immune.
- `state["conscious_output"]` stays None on reflex path. Becomes ConsciousOutput (dict) if escalated.
- `state["motor_output"]` becomes MotorOutput (dict) after motor. Motor may add `conscious_strategy` key not in the TypedDict definition.

**Loosely-typed handoffs:**
- GraphState uses `Any` for 5 fields that SystemState types as specific TypedDict | None.
- motor_output may contain `conscious_strategy` key not declared in MotorOutput TypedDict.
- DeliberationRequest fields are plain dict types (not TypedDicts): signal_summary, threat_summary, subconscious_summary.

---

### B. Limb Coverage

| Limb ID | Name | Signal domain | Semantic domain | Motor/Codec | Tests |
|---------|------|--------------|-----------------|-------------|-------|
| 1 | Prakasa | compute_target_profile (periodicity) | prompt_assembly (instruction) | text_codec (periodicity) | test_motor, test_round_trip |
| 2 | Tarka | compute_target_profile (entropy) | prompt_assembly (instruction + 2 interactions) | text_codec (entropy) | test_motor, test_round_trip, test_prompt_assembly, test_conscious |
| 3 | Nivrtti | compute_target_profile (impedance) | prompt_assembly (instruction + 2 interactions), conscious gate | text_codec (impedance) | test_motor, test_round_trip, test_prompt_assembly, test_conscious |
| 4 | Mayavada | — | prompt_assembly (instruction + 1 interaction) | text_codec (cap) | test_motor, test_codec |
| 5 | Sraddha | compute_target_profile (noise_floor) | prompt_assembly (instruction + 1 interaction) | text_codec (noise_floor) | test_motor, test_round_trip, test_prompt_assembly |
| 6 | Atma-Vichara | — | prompt_assembly (instruction) | — | — |
| 7 | Samatvam | compute_target_profile (coherence) | prompt_assembly (instruction + 2 interactions) | text_codec (coherence) | test_motor, test_round_trip, test_prompt_assembly |
| 8 | Areka | — | prompt_assembly (instruction + 1 interaction), conscious gate | text_codec (suppression) | test_motor, test_codec, test_conscious, test_integration |
| 9 | Svadharma | — | prompt_assembly (instruction) | text_codec (threshold scale) | test_motor |
| 10 | Ksetra-Jnana | — | prompt_assembly (instruction) | text_codec (delta scale) | test_motor, test_codec |
| 11 | Vishvarupa | — | prompt_assembly (instruction + 1 interaction) | — | — |
| 12 | Bodhi | — | conscious (convergent cluster) | — | test_conscious |
| 13 | No-Position | — | prompt_assembly (instruction), conscious (suppress_identity) | — | test_conscious |
| 14 | Rest-as-Realization | — | conscious (convergent cluster) | — | test_conscious |
| 15 | Mirror | — | conscious (convergent cluster) | — | test_conscious |
| 16 | Fourfold-State | — | prompt_assembly (instruction), conscious (state_awareness) | — | test_conscious |
| 17 | Ajati | — | conscious (convergent cluster) | — | test_conscious |
| 18 | Asparsa-Yoga | — | conscious (convergent cluster) | — | test_conscious |

**Limbs with no signal-domain mapping:** 4, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18 (13 of 18).
**Limbs with signal-domain mapping:** 1, 2, 3, 5, 7 (5 of 18).
**Limbs with no code reference at all:** None — all 18 appear somewhere.
**Limb 6 (Atma-Vichara):** Has prompt_assembly instruction but no signal-domain feature mapping and no motor/codec strategy. Its structural requirement (lineage completeness) is checked in conscious.repair_check.

---

### C. Threshold Inventory

| # | File | Function/Context | Value | What it gates |
|---|------|-----------------|-------|---------------|
| 1 | base.py | get_limb_weight | 0.5 | Default weight for missing limbs |
| 2 | base.py | mean_limb_weight | 0.5 | Default mean for empty limbs |
| 3 | base.py | compute_target_profile | 0.8 | Density base value |
| 4 | base.py | compute_target_profile | 0.4 | Density scale factor |
| 5 | base.py | compute_target_profile | 3.5 | Entropy base value |
| 6 | base.py | compute_target_profile | 3.0 | Entropy scale factor |
| 7 | base.py | compute_target_profile | 0.35 | Coherence base value |
| 8 | base.py | compute_target_profile | 0.7 | Coherence scale factor |
| 9 | base.py | compute_target_profile | 0.6 | Periodicity scale (inverse) |
| 10 | base.py | compute_target_profile | 0.6 | Noise floor scale (inverse) |
| 11 | base.py | compute_target_profile | 0.6 | Impedance scale (inverse) |
| 12 | sensory.py | _compute_coherence | 1.0 | Single sentence coherence value |
| 13 | sensory.py | _classify (noise) | 0.4 | Noise floor classification threshold |
| 14 | sensory.py | _classify (noise close) | 0.32 | 80% of noise threshold |
| 15 | sensory.py | _classify (periodic) | 0.3 | Periodicity classification threshold |
| 16 | sensory.py | _classify (periodic close) | 0.24 | 80% of periodicity threshold |
| 17 | sensory.py | _classify (transient) | 2.0 | Entropy delta threshold |
| 18 | sensory.py | _classify (transient close) | 1.6 | 80% of entropy delta threshold |
| 19 | sensory.py | _classify (complex) | 0.5 | Complex confidence value |
| 20 | sensory.py | _classify (min confidence) | 0.3 | Minimum confidence floor |
| 21 | sensory.py | _compute_delta (limb activation) | 0.1 | Product threshold for limb activation |
| 22 | sensory.py | _compute_impedance | 10.0 | Nesting depth divisor |
| 23 | sensory.py | _compute_impedance | 1.0 | Nesting depth cap |
| 24 | sensory.py | apoptotic_condition | 3 | Consecutive None input count |
| 25 | immune.py | ADAPTIVE_MATCH_THRESHOLD | 0.5 | Euclidean distance for adaptive match |
| 26 | immune.py | innate (entropy) | 6.0 | High entropy threshold |
| 27 | immune.py | innate (noise_floor) | 0.35 | High noise threshold |
| 28 | immune.py | innate (impedance) | 0.5 | High impedance threshold |
| 29 | immune.py | innate (aggregate_deviation) | 3.0 | High deviation threshold |
| 30 | immune.py | innate (vocabulary_richness) | 0.1 | Low vocab richness threshold |
| 31 | immune.py | threat_level (none) | 0.5 | Total score < 0.5 |
| 32 | immune.py | threat_level (low) | 1.5 | Total score < 1.5 |
| 33 | immune.py | threat_level (medium) | 3.0 | Total score < 3.0 |
| 34 | immune.py | threat_level (high) | 5.0 | Total score < 5.0 |
| 35 | immune.py | confidence_map (medium) | 0.6 | New pattern confidence |
| 36 | immune.py | confidence_map (high) | 0.8 | New pattern confidence |
| 37 | immune.py | confidence_map (critical) | 1.0 | New pattern confidence |
| 38 | immune.py | adaptive_match scoring | 0.1 | Encounter count multiplier |
| 39 | immune.py | is_anomalous | 0.5 | Total score for anomalous flag |
| 40 | immune.py | apoptotic_condition | 3 | Consecutive critical count |
| 41 | subconscious.py | MATCH_THRESHOLD | 0.3 | Feature vector distance for cache match |
| 42 | subconscious.py | escalation (novel) | 1.5 | Aggregate deviation for novel escalation |
| 43 | subconscious.py | escalation (threat confidence) | 0.9 | Threat-triggered escalation confidence |
| 44 | subconscious.py | escalation (novel confidence) | 0.7 | Novel-signal escalation confidence |
| 45 | subconscious.py | escalation (default confidence) | 0.5 | Default/tie confidence |
| 46 | subconscious.py | apoptotic_condition | 10000 | Cache size limit |
| 47 | conscious.py | active limb (low) | 0.4 | Weight below which limb is active-low |
| 48 | conscious.py | active limb (high) | 0.6 | Weight above which limb is active-high |
| 49 | conscious.py | gate: areka | 0.7 | Areka weight threshold for gate suppression |
| 50 | conscious.py | gate: nivrtti | 0.7 | Nivrtti weight threshold for sacred pause |
| 51 | conscious.py | gate: nivrtti deviation | 0.5 | Aggregate deviation below which nivrtti suppresses |
| 52 | conscious.py | gate: resting stance | 0.8 | Resting stance composite for suppression |
| 53 | conscious.py | gate: resting stance deviation | 0.3 | Aggregate deviation below which resting stance suppresses |
| 54 | conscious.py | No-Position | 0.6 | Weight above which suppress_identity activates |
| 55 | conscious.py | Fourfold State (reflective) | 0.7 | Weight above which state is "reflective" |
| 56 | conscious.py | Fourfold State (still) | 0.3 | Weight below which state is "still" |
| 57 | conscious.py | Fourfold State (consolidated) | 0.4 | Weight below which state is "consolidated" |
| 58 | conscious.py | repair (low confidence) | 0.1 | Proceed with < 0.1 confidence fails repair |
| 59 | conscious.py | apoptotic (streak threshold) | 0.2 | Confidence below which streak increments |
| 60 | conscious.py | apoptotic (streak count) | 3 | Consecutive low-confidence for apoptosis |
| 61 | deliberator_anthropic.py | max_tokens | 1024 | LLM max response tokens |
| 62 | deliberator_anthropic.py | parse fallback confidence | 0.3 | Confidence when JSON parse fails |
| 63 | deliberator_anthropic.py | parse default confidence | 0.5 | Default confidence from parsed JSON |
| 64 | prompt_assembly.py | intensity (slightly) | 0.3 | Distance < 0.3 from midpoint |
| 65 | prompt_assembly.py | intensity (moderately) | 0.6 | Distance < 0.6 from midpoint |
| 66 | prompt_assembly.py | intensity (strongly) | 0.85 | Distance < 0.85 from midpoint |
| 67 | prompt_assembly.py | interaction (high) | 0.6 | Weight > 0.6 for "both_high" |
| 68 | prompt_assembly.py | interaction (low) | 0.4 | Weight < 0.4 for "both_low" |
| 69 | prompt_assembly.py | resting stance (inactive) | 0.55 | Below this, no instruction |
| 70 | prompt_assembly.py | resting stance (slightly) | 0.65 | Below this, "slightly elevated" |
| 71 | prompt_assembly.py | resting stance (elevated) | 0.75 | Below this, "elevated" |
| 72 | prompt_assembly.py | resting stance (high) | 0.85 | Below this, "high" |
| 73 | text_codec.py | areka gate (weight) | 0.3 | Areka weight above which codec suppression checks |
| 74 | text_codec.py | areka gate (noise) | 0.3 | Noise floor above which codec suppresses |
| 75 | text_codec.py | areka gate (entropy) | 5.0 | Entropy above which codec suppresses |
| 76 | text_codec.py | mayavada (activation) | 0.45 | Mayavada weight below which cap activates |
| 77 | text_codec.py | quality check (max ratio) | 3.0 | Length ratio above which quality fails |
| 78 | text_codec.py | quality check (min ratio) | 0.2 | Length ratio below which quality fails |
| 79 | text_codec.py | quality check (overlap) | 0.2 | Token overlap below which quality fails |
| 80 | text_codec.py | strategy (density) | 0.05 | Base delta threshold for density |
| 81 | text_codec.py | strategy (entropy) | 0.5 | Base delta threshold for entropy |
| 82 | text_codec.py | strategy (coherence) | 0.1 | Base delta threshold for coherence |
| 83 | text_codec.py | strategy (impedance/periodicity/noise) | 0.05 | Base delta threshold for 3 features |

---

### D. Import Graph

**Source → Source imports:**

| Source file | Imports from |
|-------------|-------------|
| base.py | (none) |
| orientational.py | base, sleep |
| sensory.py | base |
| immune.py | base |
| subconscious.py | base |
| conscious.py | base, deliberator (TYPE_CHECKING) |
| deliberator.py | base |
| deliberator_anthropic.py | base, deliberator, prompt_assembly |
| prompt_assembly.py | deliberator |
| codec.py | base |
| text_codec.py | base, codec |
| motor.py | base, text_codec |
| sleep.py | base |
| genetic.py | base |
| graph.py | orientational, base |
| topology.py | (none) |

**Most imported:** base.py — imported by 14 of 15 other source files (all except topology.py).
**Most imports:** motor.py — imports from base (11+ identifiers) + text_codec (8 functions + class).
**Second most imported:** deliberator.py — imported by conscious.py, deliberator_anthropic.py, prompt_assembly.py.

**Test → Source imports:**

| Test file | Imports from |
|-----------|-------------|
| test_systems.py | base, sensory, immune, subconscious, conscious, motor, sleep, genetic, graph |
| test_graph.py | orientational, graph, sensory, immune, subconscious, conscious, motor, sleep, genetic, deliberator |
| test_topology.py | topology |
| test_motor.py | orientational, graph, motor, sensory, sleep |
| test_round_trip.py | orientational, graph, motor, sensory, sleep |
| test_conscious.py | orientational, graph, conscious, deliberator, prompt_assembly, immune, motor, sensory, subconscious, sleep, genetic |
| test_prompt_assembly.py | prompt_assembly |
| test_codec.py | orientational, graph, base, codec, motor, sensory, sleep, text_codec |
| test_integration.py | orientational, graph, base, conscious, deliberator, genetic, immune, motor, sensory, sleep, subconscious |

---

### E. Test Surface

| Source file | Exercised by (test files) | Direct test count |
|-------------|--------------------------|-------------------|
| base.py | All 9 test files (indirectly) | 0 (no dedicated test file) |
| orientational.py | test_graph, test_motor, test_round_trip, test_codec, test_conscious, test_integration | 4 (in test_graph) |
| sensory.py | test_systems, test_graph, test_motor, test_round_trip, test_codec, test_conscious, test_integration | 20 (in test_systems) |
| immune.py | test_systems, test_graph, test_conscious, test_integration | 12 (in test_systems) |
| subconscious.py | test_systems, test_graph, test_integration | 10 (in test_systems) |
| conscious.py | test_systems, test_conscious, test_graph, test_integration | 32 (in test_conscious) |
| deliberator.py | test_conscious, test_graph, test_integration | 3 (in test_conscious) |
| deliberator_anthropic.py | test_conscious (skipped), test_prompt_assembly (regression) | 2 (both require API key or check imports) |
| prompt_assembly.py | test_prompt_assembly, test_conscious | 24 (in test_prompt_assembly) |
| codec.py | test_codec | 3 (protocol tests) |
| text_codec.py | test_motor, test_codec, test_round_trip | 58+ (via motor tests) |
| motor.py | test_motor, test_round_trip, test_codec, test_graph, test_integration | 58 (in test_motor) |
| sleep.py | test_systems (parametrized), test_motor (WRITE_TOKEN) | 7 (parametrized only) |
| genetic.py | test_systems (parametrized) | 7 (parametrized only) |
| graph.py | test_graph, test_integration, test_motor, test_round_trip, test_codec, test_conscious, test_systems | 18 (in test_graph) |
| topology.py | test_topology | 24 (in test_topology) |

**Source files with minimal direct testing:** sleep.py (7 parametrized, stub), genetic.py (7 parametrized, stub), base.py (0 direct — all indirect through consumers).

---

### F. Dead Code

| Item | Defined in | Status |
|------|-----------|--------|
| `NIVRTTI_ID` import in motor.py | motor.py line 40 | Imported from base but never used in motor.py's own code |
| `sleep` and `genetic` params in build_graph() | graph.py line 132 | Accepted as parameters but never added as graph nodes |
| `_ROLE_DESCRIPTION` | prompt_assembly.py | Used (not dead) |
| `_OUTPUT_FORMAT` | prompt_assembly.py | Used (not dead) |
| topology.py exports | topology.py | Used only by test_topology.py — not used at runtime in graph routing |

**Notes:**
- motor.py imports 11 limb IDs from base but only re-exports them. Some are used by text_codec (which imports directly from base). The motor re-imports are for test backward compatibility.
- topology.py is a data definition — its connections are verified by tests but not read by graph.py at runtime (Phase 1 hardcoded routing). It is not dead code in the project sense (it validates architecture), but it is runtime-unused.

---

### G. Consistency

**Limb naming:**
- orientational.py: "Prakasa", "Tarka", "Nivrtti", "Mayavada", "Sraddha", "Atma-Vichara", "Samatvam", "Areka", "Svadharma", "Ksetra-Jnana", "Vishvarupa", "Bodhi", "No-Position", "Nivrtti-Rest", "Mirror", "Fourfold-State", "Ajati", "Asparsa-Yoga"
- conscious.py _LIMB_NAMES: Same as above except limb 14 is "Rest-as-Realization" (orientational uses "Nivrtti-Rest")
- test_round_trip.py _LIMB_NAMES: Limb 14 is "Nivrtti-Rest" (matches orientational)
- base.py constant: REST_AS_REALIZATION_ID (name suggests "Rest-as-Realization")

**Inconsistency:** Limb 14 has two names. "Nivrtti-Rest" in orientational.py/test_round_trip.py, "Rest-as-Realization" in conscious.py. The base.py constant name implies "Rest-as-Realization."

**Dict key conventions:**
- state keys: snake_case throughout (signal_report, threat_assessment, etc.) — consistent.
- TypedDict field names: snake_case throughout — consistent.
- Limb names in field_weights dict (conscious.py): Title-Case with hyphens ("No-Position", "Fourfold-State") — matches orientational.py naming.

**Feature key conventions:**
- SignalFeatures keys: snake_case (density, entropy, etc.) — consistent across sensory, immune, motor, text_codec.
- SignalDelta keys: snake_case with _delta suffix — consistent.

**Threshold alignment observations:**
- Noise floor classification (sensory): > 0.4. Immune innate noise threshold: > 0.35. These are different thresholds on the same feature at different layers.
- Areka suppression threshold: > 0.7 in conscious gate, > 0.3 in text_codec. Two different sensitivity levels for the same limb.
- "Active limb" range in conscious: < 0.4 or > 0.6. Interaction "high" in prompt_assembly: > 0.6. These are aligned.

---

## 6. Raw Observation List

1. base.py defines 18 TypedDicts and 18 limb ID constants.
2. base.py's compute_target_profile maps 5 of 18 limbs to signal features (1, 2, 3, 5, 7).
3. base.py's compute_target_profile returns bigram_entropy=0.0, token_count=0, vocabulary_richness=0.0 as non-targeted placeholders.
4. base.py's MotorOutput TypedDict does not include `conscious_strategy` key, but motor.py adds it dynamically.
5. base.py's SystemState uses `Any` for the `input` field.
6. orientational.py imports SleepSystem at module level to access WRITE_TOKEN.
7. orientational.py defines all 18 limbs with default weight 0.5.
8. orientational.py's read() returns a shallow copy of the limbs list.
9. Limb 14 is named "Nivrtti-Rest" in orientational.py but "Rest-as-Realization" in conscious.py.
10. sensory.py extracts 9 signal features from input text using pure Python.
11. sensory.py uses compute_target_profile as the reference for delta computation — same formulas motor uses.
12. sensory.py classifies empty/None input as "noise" with confidence 1.0.
13. sensory.py's limb activation threshold (product > 0.1) means all 18 limbs activate for typical non-trivial input at default weights.
14. sensory.py triggers apoptosis after 3 consecutive None inputs.
15. immune.py has 5 innate thresholds on different features: entropy > 6.0, noise_floor > 0.35, impedance > 0.5, aggregate_deviation > 3.0, vocabulary_richness < 0.1.
16. immune.py's noise threshold (0.35) differs from sensory's classification threshold (0.4) for the same feature.
17. immune.py sets escalate_to_conscious=True on flag/quarantine actions, but subconscious may override this.
18. immune.py adds new patterns to immune_log for medium/high/critical threats with no matching pattern.
19. immune.py triggers apoptosis after 3 consecutive critical threat assessments.
20. subconscious.py uses MATCH_THRESHOLD = 0.3 for cache pattern matching (vs immune's 0.5).
21. subconscious.py escalates on novel signals with aggregate_deviation > 1.5.
22. subconscious.py explicitly sets escalate_to_conscious to False when not recommending escalation — overriding any prior value set by immune.
23. subconscious.py stores outcomes as "escalated" or "reflex_response" in the cache.
24. subconscious.py triggers apoptosis at cache size > 10000 — no pruning mechanism exists.
25. conscious.py's gate checks for threat_action=="escalate" (immune_override), but no system currently produces "escalate" as recommended_action.
26. conscious.py's gate has 4 suppression paths: immune_override (proceed), areka_suppression, nivrtti_pause, resting_stance_suppression.
27. conscious.py's Areka gate threshold (> 0.7) is different from text_codec's Areka threshold (> 0.3).
28. conscious.py determines active limbs using 0.4-0.6 range. prompt_assembly's interaction check uses the same 0.4/0.6 thresholds.
29. conscious.py's _build_degraded_output sets confidence=0.0, which fails the repair check (< 0.1).
30. conscious.py low-confidence streak uses 0.2 threshold for increment. Repair check uses 0.1 threshold for failure. Different levels.
31. deliberator.py's MockDeliberator hardcodes gate_evaluation, which conscious.py overwrites after the call.
32. deliberator_anthropic.py requires ANTHROPIC_API_KEY at init time.
33. deliberator_anthropic.py always sets proceed=True — cannot produce suppression.
34. deliberator_anthropic.py DEFAULT_MODEL is "claude-sonnet-4-20250514".
35. prompt_assembly.py contains instructions for 13 of 18 limbs. Missing: 12, 14, 15, 17, 18 (convergent cluster).
36. prompt_assembly.py has 6 limb interaction rules covering 10 unique limb IDs.
37. prompt_assembly.py's intensity gradient has 4 levels: slightly, moderately, strongly, intensely.
38. prompt_assembly.py's resting stance has 5 levels from "none" to "very high".
39. codec.py defines the Codec protocol with 3 methods: name, encode, quality_check.
40. text_codec.py has 6 modulation strategies and 4 limb gates.
41. text_codec.py's Areka gate (> 0.3) is much more sensitive than conscious.py's Areka gate (> 0.7).
42. text_codec.py's Mayavada cap activates at weight < 0.45. At default 0.5, it is inactive.
43. text_codec.py's Ksetra-Jnana delta_scale at default weight (0.5) is 0.75, not 1.0. All deltas are scaled to 75% at default weights.
44. text_codec.py's _blend_toward_original has O(n²) behavior in the number of tokens.
45. text_codec.py quality check requires token overlap ≥ 0.2 and length ratio between 0.2 and 3.0.
46. motor.py imports NIVRTTI_ID from base but never uses it in its own code.
47. motor.py re-exports 8 functions from text_codec for backward compatibility with tests.
48. motor.py adds `conscious_strategy` key to motor_output dict that is not in the MotorOutput TypedDict.
49. motor.py's apoptotic condition triggers on None input (immediate) or 3 consecutive repair failures.
50. sleep.py is a stub — process returns state unchanged, WRITE_TOKEN is a plain string.
51. genetic.py is a stub — process returns state unchanged, tick_rate is "read_only".
52. graph.py's GraphState uses looser typing (Any, dict, list) than base.py's SystemState.
53. graph.py's build_graph accepts sleep and genetic parameters but does not add them as graph nodes.
54. graph.py's create_default_state sets escalate_to_conscious=False (changed from True in D014).
55. graph.py's _make_node wrapper runs process() then repair_check() for inline repair.
56. topology.py defines 23 connections (17 primary + 6 secondary) but graph.py does not read them at runtime.
57. topology.py is verified by test_topology.py but is runtime-unused in Phase 1.
58. test_graph.py line 67 has stale comment: "Default escalate_to_conscious=True" (default is now False).
59. test_motor.py test_low_mayavada_constrains_output contains `pass` — acknowledged as needing revision.
60. test_motor.py imports all modulation functions from motor.py, not directly from text_codec.py.
61. test_round_trip.py defines _LIMB_NAMES locally — duplicates the same mapping in conscious.py.
62. test_conscious.py tests immune_override gate with threat_action="escalate", but no system produces this action.
63. test_codec.py tests both the Codec protocol and TextCodec equivalence with pre-refactor motor behavior.
64. test_integration.py uses 4 carefully selected input constants that reliably trigger each routing path.
65. No test file tests multi-cycle graph invocation (carrying state across multiple invocations).
66. No test file tests sleep or genetic system behavior beyond parametrized interface checks.
67. No test file tests degradation propagation through the full graph.
68. The total of all tests counted per file is 322, but pytest reports 320 passed + 2 skipped — the discrepancy of 0 suggests the count of 32 in test_conscious.py includes the 2 skipped API tests.
69. CONVERGENT_CLUSTER_IDS = [12, 14, 15, 17, 18] — 5 limbs that form the resting stance composite.
70. Limb 6 (Atma-Vichara) has a constant (ATMA_VICHARA_ID = 6) and prompt_assembly instruction but no signal feature mapping and no motor/codec strategy. Its role is structural (lineage completeness in repair check).
71. The signal-semantics boundary is at the subconscious-to-conscious transition: signal domain systems (sensory, immune, subconscious) use no LLM; semantic domain (conscious) uses LLM.
72. Motor serves dual purpose: output encoding AND calibration instrument for testing limb-to-feature mappings.
73. Three routing paths exist: reflex (skip conscious), escalated (through conscious), suppression (conscious suppresses).
74. Two independent suppression mechanisms exist: conscious gate (before codec) and Areka codec gate (inside codec). They fire in sequence — if conscious suppresses, codec never checks.
75. All default limb weights are 0.5 (midpoint). At midpoint, compute_target_profile produces: density=0.8, entropy=3.5, coherence=0.35, periodicity=0.0, noise_floor=0.0, impedance=0.0.
