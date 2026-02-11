# Directive 018 — Phase Consolidation: Genetic Implementation + Structural Reckoning

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-11

## Context

Read `planning/CURRENT.md` first, then `CLAUDE.md` for orientation.

Through 17 directives, the framework has implemented six of seven systems with 371 tests passing. However, a planning review revealed that development drifted across the architecture's four phases without tracking phase boundaries. Audit-driven remediation directives (D010, D016) addressed findings by severity rather than by phase, pulling Phase 3 work (sleep weight modification, adaptive immune consolidation) into what should have been Phase 1-2 completion. The result is that no phase is cleanly complete: Phase 1 lacks genetic (the seventh system), Phase 2 is effectively done, and Phase 3 is partially implemented.

This directive has two goals: (A) implement genetic to close Phase 1's system count, and (B) establish the tracking infrastructure to prevent future phase drift. The documentation work in Part B is structural, not cosmetic — it creates the phase-awareness that was missing from the project's navigation.

**Phase this directive closes:** Phase 1 (Single Cell) — all seven systems implemented.

## Objective

Implement the genetic system as an expression profile store (the seventh and final system), update all documentation to reflect actual phase completion state, and establish audit methodology amendments and phase tracking infrastructure for future development.

## Part A: Genetic System Implementation

### A1: New TypedDicts in base.py

Add the following types to `src/agenetic/systems/base.py`, after the existing `ConsciousOutput` definition and before the `SystemState` definition:

```python
class ExpressionEntry(TypedDict):
    """A single system's expression state within the genetic profile."""
    system_name: str
    state: str  # "active" | "dormant" | "suppressed"

class ExpressionProfile(TypedDict):
    """The genetic expression profile — what capabilities are currently expressed.
    
    The factory seed (default_weights, generation 0) is immutable.
    Sleep modifies the expression profile through epigenetic feedback (Phase 4).
    """
    default_weights: dict[str, float]  # limb_name -> factory default weight
    system_expressions: list[ExpressionEntry]
    generation: int  # modification count (0 = factory, incremented by sleep in Phase 4)

class GeneticOutput(TypedDict):
    """Output of the genetic system — a snapshot of the current expression state."""
    expression_profile: ExpressionProfile
    drift_from_seed: float  # sum of |current_weight - default_weight| across all limbs
    seed_integrity: bool  # True if drift < apoptotic threshold
```

Add `genetic_output: GeneticOutput | None` to the `SystemState` TypedDict.

### A2: Update GraphState and create_default_state

In `src/agenetic/network/graph.py`:

Add `genetic_output: Any` to the `GraphState` TypedDict (after `motor_output`).

In `create_default_state()`, add `"genetic_output": None` to the returned dict.

### A3: Update _make_node in graph.py

In `_make_node()`, add `"genetic_output": state.get("genetic_output"),` to the `full_state` construction (after the `motor_output` line).

### A4: Implement GeneticSystem

Replace the stub in `src/agenetic/systems/genetic.py` with a full implementation.

**Read these files first:**
- `src/agenetic/systems/base.py` — for the new TypedDicts, all limb ID constants, FieldLimb
- `src/agenetic/field/orientational.py` — for `_DEFAULT_LIMBS` (the factory seed data)
- `src/agenetic/systems/sleep.py` — to understand sleep's field modification pattern

**Import considerations:** orientational.py already imports from sleep.py (for WRITE_TOKEN). To avoid circular imports, genetic.py should NOT import from orientational.py. Instead, define the factory defaults in genetic.py itself or import `_DEFAULT_LIMBS` from orientational.py only at function-call time (lazy import). The cleanest approach: define a module-level constant `FACTORY_SEED` in genetic.py that duplicates the 18 limb names and their 0.5 default weights. This is a deliberate copy, not DRY violation — genetic OWNS the seed, orientational.py happens to use the same defaults.

**Implementation requirements:**

```python
class GeneticSystem(BaseSystem):
    """Generation layer — the minimal generative seed read by all systems.
    
    The genetic layer does not fire actively. It stores the expression profile
    that defines what processing is possible. All other systems read from it.
    Only sleep writes to it (Phase 4 — not yet implemented).
    
    process() populates state["genetic_output"] with a snapshot of the current
    expression profile and drift measurement.
    """
    
    # Factory seed: limb_name -> default weight
    # This is the immutable baseline. Genetic owns this data.
    FACTORY_SEED: dict[str, float] = {
        "Prakasa": 0.5,
        "Tarka": 0.5,
        "Nivrtti": 0.5,
        "Mayavada": 0.5,
        "Sraddha": 0.5,
        "Atma-Vichara": 0.5,
        "Samatvam": 0.5,
        "Areka": 0.5,
        "Svadharma": 0.5,
        "Ksetra-Jnana": 0.5,
        "Vishvarupa": 0.5,
        "Bodhi": 0.5,
        "No-Position": 0.5,
        "Nivrtti-Rest": 0.5,
        "Mirror": 0.5,
        "Fourfold-State": 0.5,
        "Ajati": 0.5,
        "Asparsa-Yoga": 0.5,
    }
    
    ALL_SYSTEM_NAMES = [
        "sensory", "immune", "subconscious", "conscious", "motor", "sleep", "genetic"
    ]
    
    APOPTOTIC_DRIFT_THRESHOLD = 3.0
    
    def __init__(self, seed: dict[str, float] | None = None) -> None:
        super().__init__(
            name="genetic",
            description="Encodes the minimal generative seed from which capabilities unfold",
        )
        self._seed = dict(seed) if seed is not None else dict(self.FACTORY_SEED)
        self._expression_profile: ExpressionProfile = {
            "default_weights": dict(self._seed),
            "system_expressions": [
                {"system_name": name, "state": "active"}
                for name in self.ALL_SYSTEM_NAMES
            ],
            "generation": 0,
        }
    
    @property
    def tick_rate(self) -> str:
        return "read_only"
    
    def get_expression_profile(self) -> ExpressionProfile:
        """Direct read access to the current expression profile."""
        return self._expression_profile
    
    def compute_drift(self, field_state) -> float:
        """Compute aggregate drift of current field weights from factory seed.
        
        Returns sum of |current_weight - default_weight| across all limbs.
        """
        limbs = field_state.get("limbs", [])
        total_drift = 0.0
        for limb in limbs:
            name = limb["name"]
            default = self._seed.get(name, 0.5)
            total_drift += abs(limb["weight"] - default)
        return total_drift
    
    def process(self, state: SystemState) -> SystemState:
        """Populate state with genetic expression snapshot.
        
        Reads current field weights, computes drift from factory seed,
        and populates genetic_output for other systems to read.
        """
        drift = self.compute_drift(state["field"])
        genetic_output: GeneticOutput = {
            "expression_profile": self._expression_profile,
            "drift_from_seed": drift,
            "seed_integrity": drift < self.APOPTOTIC_DRIFT_THRESHOLD,
        }
        return {**state, "genetic_output": genetic_output}
    
    def repair_check(self, state: SystemState) -> bool:
        """Validate seed consistency.
        
        Checks that the expression profile is internally consistent:
        all 18 limbs present, all 7 systems present, generation non-negative.
        """
        profile = self._expression_profile
        if len(profile["default_weights"]) != 18:
            return False
        system_names = {e["system_name"] for e in profile["system_expressions"]}
        if len(system_names) != 7:
            return False
        if profile["generation"] < 0:
            return False
        return True
    
    def apoptotic_condition(self, state: SystemState) -> bool:
        """Has the genetic seed drifted beyond recovery?
        
        Returns True when aggregate field weight drift from factory seed
        exceeds APOPTOTIC_DRIFT_THRESHOLD (default 3.0). This means the
        system's operating point has moved so far from its original
        configuration that behavior may be incoherent.
        """
        drift = self.compute_drift(state["field"])
        return drift >= self.APOPTOTIC_DRIFT_THRESHOLD
```

**Important:** The `FACTORY_SEED` keys must match the `name` field in orientational.py's `_DEFAULT_LIMBS` exactly. Verify by reading orientational.py: Prakasa, Tarka, Nivrtti, Mayavada, Sraddha, Atma-Vichara, Samatvam, Areka, Svadharma, Ksetra-Jnana, Vishvarupa, Bodhi, No-Position, Nivrtti-Rest, Mirror, Fourfold-State, Ajati, Asparsa-Yoga.

### A5: Update _make_sample_state in test_systems.py

Add `"genetic_output": None` to the state returned by `_make_sample_state()` in `tests/test_systems.py`.

### A6: Tests — test_genetic.py

Create `tests/test_genetic.py` with the following test categories:

**Factory defaults (3 tests):**
- `test_factory_seed_has_18_limbs` — FACTORY_SEED has exactly 18 entries
- `test_factory_profile_all_active` — all 7 systems are "active" at generation 0
- `test_factory_profile_generation_zero` — generation is 0

**Expression profile access (3 tests):**
- `test_get_expression_profile_returns_profile` — get_expression_profile() returns an ExpressionProfile
- `test_custom_seed_overrides_defaults` — GeneticSystem(seed={"Prakasa": 0.7, ...}) uses custom weights
- `test_process_populates_genetic_output` — process() adds genetic_output to state

**Drift measurement (4 tests):**
- `test_drift_zero_at_factory_defaults` — all weights at 0.5 → drift = 0.0
- `test_drift_computes_absolute_distance` — one limb at 0.7 → drift = 0.2
- `test_drift_accumulates_across_limbs` — multiple limbs moved → drift = sum of absolute deltas
- `test_drift_maximum_is_nine` — all limbs at 0.0 or 1.0 → drift = 9.0

**Repair check (3 tests):**
- `test_repair_passes_at_factory` — factory defaults pass
- `test_repair_fails_with_corrupted_seed` — manually corrupt the profile (remove a limb) → False
- `test_repair_fails_with_missing_system` — remove a system expression → False

**Apoptotic condition (3 tests):**
- `test_not_apoptotic_at_factory` — factory defaults → False
- `test_apoptotic_at_high_drift` — set all field weights to 0.0 (drift = 9.0) → True
- `test_apoptotic_threshold_boundary` — drift exactly at 3.0 → True, just below → False

**Seed integrity in output (2 tests):**
- `test_seed_integrity_true_at_factory` — genetic_output.seed_integrity is True at defaults
- `test_seed_integrity_false_at_high_drift` — seed_integrity is False when drift exceeds threshold

All tests are deterministic — no LLM calls, no API keys.

## Part B: Phase Completion Documentation

### B1: Create docs/AUDIT_METHODOLOGY.md

Create a new file `docs/AUDIT_METHODOLOGY.md` with the following content:

```markdown
# Audit Methodology

## Lessons Learned (D009/D015 → D010/D016)

The project's first two audit cycles (D009/D015 mechanical + conceptual audits, D010/D016 remediation) revealed a structural problem with how audit findings were organized and addressed.

### The Problem: Severity-First Organization Causes Phase Drift

Both audits presented findings as flat severity-ranked lists: critical findings first, recommendations last. Remediation directives followed this ordering — fixing the most severe issues regardless of which architectural phase they belonged to.

The result: D010 remediated per-feature delta (Phase 1 fix) alongside calibration infrastructure (Phase 2 work) in a single directive. D016 remediated cache pruning (Phase 1 fix), escalation flag preservation (Phase 1 fix), immune escalation (Phase 1 fix), and feature normalization (Phase 1 fix) — but the cache pruning was described in Phase 3 terms (self-regulation). D017 implemented sleep with weight modification (Phase 2 scheduling + Phase 3 adaptive behavior) in one directive.

By D017, the project had partially implemented Phases 1, 2, and 3 with no phase cleanly complete.

### The Fix: Phase-First, Severity-Second

Future audits must:

1. **Classify every finding by phase** — which phase does this finding belong to? If a finding spans phases, document the dependency.

2. **Present findings grouped by phase** — within each phase group, order by severity. This makes it visible when a high-severity finding would pull remediation into a different phase.

3. **Remediation directives stay within one phase** — unless a finding is a deployment hazard (like the 10K cache time bomb). Cross-phase remediation requires explicit justification in the directive and must be tracked in CURRENT.md's phase completion section.

4. **CURRENT.md tracks phase items** — each directive documents which phase items it closes. The planning instance reviews phase completion state before scoping the next directive.

### Audit Structure Template

```
## Phase 1 Findings
### Critical
### Important  
### Informational

## Phase 2 Findings
### Critical
### Important
### Informational

## Phase 3 Findings
[...]

## Cross-Phase Findings
[Findings that span multiple phases, with dependency analysis]
```
```

### B2: Update ARCHITECTURE.md Status Section

Find the status section near the bottom of `docs/ARCHITECTURE.md`. It currently reads:

```
## Status

Phase 1 (Minimal Viable Cell) is partially implemented. The signal-domain tier (sensory, immune, subconscious) and motor layer are operational. Conscious, sleep, and genetic remain stubs. [...]
```

Replace the **entire Status section** (from `## Status` to the line before `---`) with:

```markdown
## Status

### Phase Completion

**Phase 1 — Single Cell: COMPLETE (D001–D018)**
All seven systems implemented with typed interfaces. LangGraph routing with conditional escalation. Three verified routing paths (reflex, escalated, suppression). Orientational field with sleep-only write access enforced. Signal-semantics boundary established. Genetic provides expression profiles; sleep modifies field weights. 371+ tests passing.

**Phase 2 — Temporal Stratification: COMPLETE (D011–D017)**
Conscious fires on escalation only (D014). Reflex paths bypass conscious (D014). Sleep fires periodically at configurable interval (D017). Motor fires on demand. Different tick rates operational across all seven systems.

**Phase 3 — Network Topology + Self-Regulation: NOT STARTED**
Remaining work: feedback loops (Motor→Conscious, Conscious→Sensory, Conscious→Immune), connection weight routing in graph, homeostatic monitoring, connection weight modification during sleep, system/agent-level apoptosis.

**Phase 4 — Epigenetic Adaptation: NOT STARTED**
Remaining work: sleep writes to genetic expression profiles, expression profiles modify system behavior, field expression adjusts from accumulated experience, multi-cycle validation.

### Phase Boundary Note

Phases 1 and 2 were not completed sequentially. Development followed audit-driven remediation (D010, D016) that addressed findings by severity rather than by phase, pulling Phase 2 and Phase 3 work into Phase 1 completion. See `docs/AUDIT_METHODOLOGY.md` for the corrective methodology adopted post-D018. See `planning/018_phase_consolidation.md` for the full post-mortem.

### Implementation Note

v1 → v2 changes: network topology replaces loop, temporal stratification added, inline repair added, homeostatic regulation specified (not yet implemented), apoptotic exit conditions added (process-level implemented, system/agent level pending), immune system upgraded to adaptive, implementation pathway phased for incremental building.
```

### B3: Add Phase Tracking to CURRENT.md

When rebuilding CURRENT.md, add a new section **after the System Status table** and **before the test files table**, titled `## Phase Completion`. Content:

```markdown
## Phase Completion

| Phase | Status | Closed by |
|---|---|---|
| 1 — Single Cell | **COMPLETE** | D001–D018 |
| 2 — Temporal Stratification | **COMPLETE** | D011–D017 |
| 3 — Network Topology + Self-Regulation | Not started | — |
| 4 — Epigenetic Adaptation | Not started | — |

### Phase 3 Remaining Items
- [ ] Feedback loops: Motor→Conscious, Conscious→Sensory, Conscious→Immune
- [ ] Graph uses topology.py connection weights
- [ ] Homeostatic monitoring subsystem
- [ ] Connection weight modification during sleep (distinct from field weights)
- [ ] System-level and agent-level apoptosis

### Phase 4 Remaining Items
- [ ] Sleep writes to genetic expression profiles
- [ ] Expression profiles modify system behavior in subsequent cycles
- [ ] Field expression adjusts from accumulated experience
- [ ] Multi-cycle integration validation
```

### B4: DEVLOG Entry

Add entry for D018. Format:

```markdown
## 2026-02-11 — Directive 018: Phase Consolidation — Genetic + Structural Reckoning

**Commit:** `[hash]`
**Tests:** [count] passing + 2 skipped ([new] new)

**Phase closed:** Phase 1 (Single Cell) — all seven systems now implemented.

Implemented the genetic system as an expression profile store — the seventh and final system. Genetic does not fire actively; it provides readable expression profiles (factory seed weights, system expression states, generation counter) and measures drift of current field weights from the factory baseline. Apoptotic condition triggers when aggregate drift exceeds 3.0.

Also established phase-tracking infrastructure to prevent the navigational drift that caused development to chaotically implement parts of Phases 1–3 over 17 directives without completing any phase. Key deliverables:

- `docs/AUDIT_METHODOLOGY.md` — audit findings must now be classified by phase before severity ranking, and remediation directives must stay within one phase unless a finding is a deployment hazard
- Phase tracking section added to `planning/CURRENT.md` — every directive now documents which phase items it closes
- `docs/ARCHITECTURE.md` status section updated to reflect actual completion state (was stale since D011)
- Full post-mortem on phase drift in `planning/018_phase_consolidation.md`
```

### B5: README Update

Update `README.md`:
- In the system table, change Sleep row from "Consolidates — pruning, weight modification" (if it doesn't already match) and verify Genetic row says "Generates — the minimal seed" with tick rate "Read-only"
- Update test count
- Update "Current Status" section to reflect Phase 1 complete, Phase 2 complete
- Add `docs/AUDIT_METHODOLOGY.md` to the docs listing in the project structure

## Part C: Planning State Management

### C1: Copy State to Planning Entry
Copy `handoff/state.md` to `planning/018_phase_consolidation.md`.

### C2: Update CURRENT.md from Repo Inspection
Rebuild `planning/CURRENT.md` from actual repo state. Do NOT copy old version. Include the new Phase Completion section (Part B3). Update system status table to show Genetic as "Operational" with LOC count and test count.

## Scope Boundaries

**DO:**
- Read `src/agenetic/systems/base.py` for SystemState TypedDict and limb constants
- Read `src/agenetic/field/orientational.py` for `_DEFAULT_LIMBS` limb names (verify FACTORY_SEED keys match)
- Read `src/agenetic/network/graph.py` for GraphState and create_default_state
- Read `tests/test_systems.py` for _make_sample_state and parametrized test expectations
- Read `docs/ARCHITECTURE.md` to find the status section for replacement
- Create new files: `src/agenetic/systems/genetic.py` (replace stub), `tests/test_genetic.py`, `docs/AUDIT_METHODOLOGY.md`
- Update existing files: `base.py`, `graph.py`, `test_systems.py`, `ARCHITECTURE.md`, `DEVLOG.md`, `README.md`, `CURRENT.md`

**DO NOT:**
- Modify any system implementation other than genetic.py
- Modify orientational.py (genetic reads from it conceptually but does not import from it)
- Modify sleep.py (sleep-to-genetic wiring is Phase 4)
- Modify any test file other than test_systems.py (for _make_sample_state) and test_genetic.py (new)
- Add genetic to graph routing (it is deliberately unrouted — "read_only" tick rate)
- Edit any historical handoff files (handoff/001–017_*.md)

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/genetic.py` | Replaced — full implementation |
| `src/agenetic/systems/base.py` | Updated — ExpressionEntry, ExpressionProfile, GeneticOutput TypedDicts + genetic_output in SystemState |
| `src/agenetic/network/graph.py` | Updated — genetic_output in GraphState, create_default_state, _make_node |
| `tests/test_genetic.py` | Created — 18 tests |
| `tests/test_systems.py` | Updated — genetic_output in _make_sample_state |
| `docs/AUDIT_METHODOLOGY.md` | Created — phase-first audit methodology |
| `docs/ARCHITECTURE.md` | Updated — status section replaced |
| `DEVLOG.md` | Updated — D018 entry |
| `README.md` | Updated — test count, status, docs listing |
| `handoff/state.md` | Provided — copy to planning entry |
| `planning/018_phase_consolidation.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection with Phase Completion section |
| `handoff/018_directive.md` | This file |
| `handoff/018_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `GeneticSystem` inherits from `BaseSystem` and passes all 7 parametrized interface tests
- [ ] `GeneticSystem.FACTORY_SEED` has exactly 18 entries, keys match orientational.py `_DEFAULT_LIMBS` names
- [ ] `GeneticSystem.process()` returns state with `genetic_output` populated
- [ ] `GeneticSystem.repair_check()` returns True at factory defaults
- [ ] `GeneticSystem.apoptotic_condition()` returns False at factory defaults
- [ ] `GeneticSystem.apoptotic_condition()` returns True when drift >= 3.0
- [ ] `GeneticSystem.compute_drift()` returns 0.0 when all field weights are at factory defaults
- [ ] `ExpressionProfile`, `ExpressionEntry`, `GeneticOutput` TypedDicts defined in base.py
- [ ] `SystemState` includes `genetic_output: GeneticOutput | None`
- [ ] `GraphState` includes `genetic_output: Any`
- [ ] `create_default_state()` includes `"genetic_output": None`
- [ ] `_make_node()` passes `genetic_output` through to full_state
- [ ] `_make_sample_state()` in test_systems.py includes `"genetic_output": None`
- [ ] `tests/test_genetic.py` has 18 tests, all passing
- [ ] `docs/AUDIT_METHODOLOGY.md` exists with phase-first methodology
- [ ] `docs/ARCHITECTURE.md` status section reflects Phase 1 and 2 complete
- [ ] `planning/CURRENT.md` has Phase Completion section with checklist
- [ ] `DEVLOG.md` has D018 entry
- [ ] `README.md` updated with correct test count and status
- [ ] No modifications to sleep.py, orientational.py, or any system other than genetic.py
- [ ] Genetic system NOT added to graph routing
- [ ] No circular imports introduced
- [ ] All existing 371 tests still pass
- [ ] No historical handoff files edited
- [ ] `handoff/state.md` copied to `planning/018_phase_consolidation.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection
- [ ] Git commit and push completed
