# 018 — Phase Consolidation: Genetic + Structural Reckoning

**Date:** 2026-02-11
**Directive type:** Implementation + Documentation (mixed — justified by structural need)

## Decisions

### Genetic as expression profile store, not active processor

The architecture says genetic "does not fire actively" and "is read from by every other system." Its tick_rate is `read_only`. It's not routed in the graph. So `process()` is not the primary interface — direct method access is.

Genetic provides:
1. **Factory seed** — the immutable default field weights (currently hardcoded as 0.5 × 18 in orientational.py). Genetic owns this data; orientational.py reads from it.
2. **Expression profile** — which capabilities are active/dormant/suppressed, plus system parameters. Sleep will write to this in Phase 4. For now, all systems are active, all parameters are defaults.
3. **Drift measurement** — how far current field weights have moved from factory seed. This enables the apoptotic condition: if accumulated drift exceeds a threshold, the genetic seed is considered corrupted.

Rejected alternatives:
- Making genetic an active processor that transforms state each cycle — violates architecture's "does not fire actively"
- Making genetic just a data class (not a BaseSystem) — breaks the parametrized test contract and the seven-system promise
- Deferring genetic entirely to Phase 4 — leaves the system count incomplete and blocks phase completion documentation

### process() populates genetic_output in state

Even though genetic isn't routed in the graph, `process()` still needs to do something meaningful for the parametrized tests and for application code that calls it directly. It reads the current expression profile and populates `state["genetic_output"]` with a snapshot. This is the read interface — other systems check `state["genetic_output"]` for expression data.

This requires adding `genetic_output: GeneticOutput | None` to SystemState and GraphState.

### Expression profile is a new TypedDict, not freeform dict

```python
class ExpressionEntry(TypedDict):
    system_name: str
    state: str  # "active" | "dormant" | "suppressed"

class ExpressionProfile(TypedDict):
    default_weights: dict[str, float]  # limb_name -> factory weight
    system_expressions: list[ExpressionEntry]
    generation: int  # modification count (0 = factory, incremented by sleep)

class GeneticOutput(TypedDict):
    expression_profile: ExpressionProfile
    drift_from_seed: float  # aggregate distance of current weights from defaults
    seed_integrity: bool  # True if drift < apoptotic threshold
```

Using `limb_name` (string) as key rather than `limb_id` (int) for readability in the profile. The mapping is unambiguous since names are unique.

### Apoptotic threshold: aggregate drift > 3.0

With 18 limbs at 0.5 default, maximum possible drift is 18 × 0.5 = 9.0 (all weights at 0.0 or 1.0). A threshold of 3.0 means the average limb has moved ±0.167 from default — significant sustained pressure. This is an engineering assignment like all other thresholds.

### repair_check validates seed consistency

Checks that the expression profile is internally consistent: all 18 limbs present in default_weights, all seven systems present in system_expressions, generation count non-negative. Does NOT check field weights against profile — that's drift measurement, not corruption.

### Phase drift post-mortem goes in planning entry, not in code

The post-mortem is a planning document, not a code artifact. It belongs in `planning/018_phase_consolidation.md` (this file, via the copy mechanism). The code changes are: ARCHITECTURE.md status update, CURRENT.md phase tracking section, and a new `docs/AUDIT_METHODOLOGY.md` documenting the amended audit approach.

### Restructured phase definitions

The original four phases were defined before any code existed. Now that we have 17 directives of implementation data, the phases should reflect actual dependency structure, not the original speculative sequence.

**Revised phases:**

**Phase 1 — Single Cell (COMPLETE after D018)**
All seven systems implemented with typed interfaces. LangGraph routing with conditional escalation. Three verified paths (reflex, escalated, suppression). Orientational field with read/write access control. Signal-semantics boundary established. Genetic provides expression profiles; sleep modifies field weights.

**Phase 2 — Temporal Stratification (COMPLETE as of D014/D017)**
Conscious fires on escalation only. Reflex paths bypass conscious. Sleep fires periodically (every N cycles). Motor fires on demand. Different tick rates operational.

**Phase 3 — Network Topology + Self-Regulation (D019-D020)**
Feedback loops wired (Motor→Conscious, Conscious→Sensory, Conscious→Immune). Graph uses topology connection weights. Homeostatic monitoring. Connection weight modification during sleep. System/agent-level apoptosis.

**Phase 4 — Epigenetic Adaptation (future)**
Sleep writes to genetic expression profiles. Expression profiles modify system behavior. Field expression adjusts from accumulated experience. Multi-cycle validation.

Key change: Phase 3 is now about network topology and self-regulation (the things that make the pipeline into a network). Phase 4 is clearly about genetic feedback (the things that make the system learn across lifetimes).

### Audit methodology amendment

Future audits must:
1. Classify findings by phase before ranking by severity
2. Remediation directives must stay within one phase unless a finding is a safety hazard
3. Cross-phase dependencies must be documented explicitly when they occur
4. The planning instance tracks which phase items each directive closes in CURRENT.md

## Observations

### Genetic is architecturally unusual

Every other system transforms state: sensory adds signal_report, immune adds threat_assessment, subconscious adds subconscious_output, conscious adds conscious_output, motor adds motor_output, sleep modifies field/cache/immune_log. Genetic doesn't transform — it provides. It's a data source, not a processor. The BaseSystem interface fits awkwardly but is necessary for the seven-system contract.

### The factory seed is currently implicit

The 18 limbs at 0.5 weight are defined in orientational.py's `_DEFAULT_LIMBS`. This IS the genetic seed — but it's not owned by the genetic system. D018 makes this ownership explicit without moving the data (orientational.py still defines the limbs, genetic reads them as factory defaults). Moving the data would be a refactor with no behavioral change and would complicate imports.

### Phase drift was predictable

The audit-severity-first pattern was never a conscious choice. It emerged from the audit's presentation format (severity-ranked flat list) and from remediation directives following that structure. Nobody decided "let's ignore phase boundaries." The boundaries were never tracked, so they couldn't be violated — they were invisible.

### Documentation directives have historically been weak

D003, D005, D006 were documentation/housekeeping directives scoped as cleanup rather than structural decisions. D018's documentation work is different — it establishes tracking infrastructure that prevents navigational errors.

## What to Watch

### genetic_output in SystemState
Adding a new field to SystemState means updating `_make_sample_state()` in test_systems.py, GraphState in graph.py, and `create_default_state()` in graph.py. DNAgent must find all three locations.

### OrientationalField import cycle
orientational.py imports SleepSystem (for WRITE_TOKEN). If genetic.py imports from orientational.py, there's a circular import risk. DNAgent should read factory defaults from orientational.py's `_DEFAULT_LIMBS` via a function or constant, not through OrientationalField itself. Or define defaults in base.py.

### Parametrized test expectations
The 7 existing parametrized tests assert: inherits BaseSystem, has name, has description, tick_rate in valid set, process returns state dict, repair_check returns bool, apoptotic_condition returns bool. Genetic must still pass all of these at factory defaults (repair_check=True, apoptotic_condition=False).

### ARCHITECTURE.md status section is stale
Currently says "Conscious, sleep, and genetic remain stubs." DNAgent must find and replace this specific text.

### Phase tracking in CURRENT.md
New section goes after system status table, before infrastructure section. Must not disrupt existing structure.
