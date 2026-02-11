# Directive 017 — Sleep System: Consolidation and Weight Modification

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-11

## Context

Read `planning/CURRENT.md` first — it contains the current factual state of the repo. Then read `CLAUDE.md` for repo orientation.

The sleep system is the keystone of the agenetic framework's meta-domain. It is the only system permitted to write to the orientational field via `OrientationalField.write()`, making it the sole mechanism by which the field transitions from static configuration to dynamic adaptation.

Sleep is currently a stub at `src/agenetic/systems/sleep.py` — its `process()` returns state unchanged. It already defines `WRITE_TOKEN = "sleep_system_authorized"`.

Three findings from the conceptual audit (`handoff/015_conceptual_audit_report.md`) are blocked until sleep is functional:

1. **Dormant gate (Finding #2):** The conscious system's proceed/suppress gate has four suppression paths, all requiring limb weights above the default of 0.5 (Ārēka > 0.7, Nivṛtti > 0.7, resting stance composite > 0.8). Since only sleep can modify weights and sleep is a stub, the gate always falls through to `default_proceed`. The conscious system always deliberates when escalated.

2. **Convergent cluster (Finding #3):** Five limbs (Bodhi, Nivrtti-Rest, Mirror, Ajāti, Asparśa-Yoga) have no individual effects. They contribute only to the resting stance composite (mean of five weights). Moving a single cluster limb from 0.5 → 1.0 shifts the composite from 0.50 → 0.60, below every gate threshold. These limbs are decorative until sleep can move them as a coordinated group.

3. **Static field (Recommendation #8):** Without sleep, the orientational field is inert storage. The system cannot learn across cycles.

The subconscious already has inline pruning of single-encounter stale entries (D016 fix: removes `encounter_count == 1` entries older than 100 ticks). However, multi-encounter stale entries and the immune threat log have no consolidation mechanism. More importantly, the subconscious cache still grows monotonically for recurring patterns, and at 10,001 entries the apoptotic condition triggers. Sleep provides deeper pruning that subconscious cannot perform on its own.

**Current repo state:** 336 tests passing, 2 skipped. D016 remediation complete (includes Māyāvāda fix, cache pruning, flag OR-preservation, immune escalation, feature normalization, Ārēka documentation). Signal domain and motor layer operational. Conscious operational but gate dormant. Sleep and genetic are stubs.

### Design Decisions

These decisions were made during planning and are not open for reinterpretation:

- **Tick rate:** Default of 10 cycles, configurable via constructor parameter.
- **Weight change triggers:** Consolidation-derived. Sleep observes what it prunes and consolidates, then derives weight adjustment signals from those observations. No external monitoring infrastructure required.
- **Weight change bounds:** Maximum ±0.05 per limb per sleep tick. Absolute bounds [0.0, 1.0]. Slight gravitational decay toward 0.5 (default) each tick.
- **Convergent cluster:** The five resting-stance limbs (IDs 12, 14, 15, 17, 18 — defined as `CONVERGENT_CLUSTER_IDS` in `base.py`) always receive the same delta, preserving their function as a coordinated group.
- **Scope:** Consolidation + pruning + weight modification. Epigenetic feedback to genetic, connection weight modification, and error correction are deferred to a future directive.

## Objective

Implement the sleep system as a functional `BaseSystem` that performs deeper pruning on the subconscious pattern cache, consolidates the immune threat log, and modifies orientational field limb weights based on consolidation observations.

## Part A: Sleep System Implementation

### A1: Replace the Sleep Stub

Replace the stub in `src/agenetic/systems/sleep.py` with a full implementation. Read the current stub first — it already has `WRITE_TOKEN`.

Read these files to understand the interfaces sleep interacts with:
- `src/agenetic/systems/base.py` — `BaseSystem` interface, `SystemState`, all type definitions, limb ID constants, `CONVERGENT_CLUSTER_IDS`
- `src/agenetic/field/orientational.py` — the `write()` method signature and authorization mechanism
- `src/agenetic/systems/subconscious.py` — `CachedSignalPattern` type, cache data format, existing inline pruning
- `src/agenetic/systems/immune.py` — `ThreatEntry` type, immune log data format

**Sleep state persistence:** `SystemState` does not currently have a key for sleep-specific tracking data. Sleep must store its cross-invocation state (last_sleep_tick, cache_size_at_last_sleep, consecutive_no_improvement) in a new `sleep_state` key added to the state dict. This is a plain dict, not a TypedDict addition — sleep writes `state["sleep_state"] = {...}` in its returned state. If `state.get("sleep_state")` is None on first invocation, initialize with defaults.

**Interface contract:**

```python
class SleepSystem(BaseSystem):
    """
    Consolidation system. Fires periodically (every N cycles).
    Prunes subconscious cache, consolidates immune threat log,
    modifies orientational field weights based on consolidation signals.
    
    ONLY system with write access to OrientationalField via write().
    """
    WRITE_TOKEN = "sleep_system_authorized"  # Already exists
    
    def __init__(self, tick_interval: int = 10):
        # tick_interval: how many processing cycles between sleep ticks
        ...
    
    @property
    def tick_rate(self) -> str:
        return "periodic"  # Already exists
    
    def process(self, state: SystemState) -> SystemState:
        # 1. Check if it's time to fire (current tick % tick_interval)
        # 2. If not time, return state unchanged
        # 3. If time: run A2 (prune), A3 (consolidate), A4 (weights), A5 (repair)
        ...
    
    def repair_check(self, state: SystemState) -> bool:
        # Did consolidation improve or at least not degrade system state?
        ...
    
    def apoptotic_condition(self, state: SystemState) -> bool:
        # Has sleep failed to produce measurable consolidation for
        # 3 consecutive sleep ticks?
        ...
```

**Tick gating:** Sleep reads `state["metadata"]["tick"]` to determine the current tick. It fires when `tick % tick_interval == 0` AND `tick > 0` (don't fire on the first tick). When not firing, `process()` returns state unchanged.

### A2: Subconscious Cache Pruning (Deeper Than Inline)

The subconscious already prunes single-encounter entries older than 100 ticks during its own processing. Sleep performs DEEPER pruning that subconscious cannot do:

**Pruning rules:**
- Remove entries where `encounter_count <= 2` AND `(current_tick - last_seen_tick) > staleness_threshold`
- Default `staleness_threshold`: 50 ticks (configurable via constructor parameter)
- This catches entries that subconscious's inline pruning misses: the 2-encounter patterns that never recurred enough to demonstrate value
- Entries with `encounter_count > 2` are never pruned by this rule (they have demonstrated sustained value)
- Record: entries_pruned, cache_size_before, cache_size_after — these are consolidation metrics used by A4 and A5

The cache lives at `state["signal_pattern_cache"]` as a `list[CachedSignalPattern]`. Each entry has: `input_hash`, `feature_vector`, `signal_type`, `outcome`, `response_pattern_id`, `encounter_count`, `last_seen_tick`.

**Do not** modify the subconscious system itself. Sleep operates on the cache in `SystemState`.

### A3: Immune Threat Log Consolidation

The immune threat log lives at `state["immune_log"]` as a `list[ThreatEntry]`. Each entry has: `pattern` (JSON-encoded feature vector string), `encounter_count`, `confidence` (float), `last_seen` (ISO datetime string).

**IMPORTANT:** The immune log uses ISO datetime strings for `last_seen`, NOT tick numbers. Staleness comparison for immune entries must parse the datetime and compare against current time, not against tick numbers. Use `datetime.fromisoformat()` and compare against `datetime.now(timezone.utc)`. Define a `staleness_seconds` threshold (default: 3600 seconds = 1 hour) for immune log aging. This is separate from the tick-based staleness used for cache pruning.

**Consolidation rules:**
- **Promote:** For threats with `encounter_count >= 3`, increase `confidence` by 0.1 (capped at 1.0). These are confirmed recurring threats.
- **Demote:** For threats where time since `last_seen` exceeds `staleness_seconds` AND `encounter_count <= 2`, decrease `confidence` by 0.1. Stale, unconfirmed threats fade.
- **Remove:** Drop entries where `confidence <= 0.0` after demotion. These are fully expired.
- Record: threats_promoted, threats_demoted, threats_removed, total_threats — these are consolidation metrics used by A4.

### A4: Orientational Field Weight Modification

After pruning and consolidation, sleep computes weight adjustment signals and applies them to the orientational field.

**Read `src/agenetic/field/orientational.py` carefully.** The actual method is:

```python
field.write(limbs: list[FieldLimb], *, caller_token: str)
```

This takes the FULL list of limb dicts and replaces the field state entirely. Sleep must:
1. Read the current field from state: `field_state = state["field"]`
2. Copy the limbs list: `limbs = [{**limb} for limb in field_state["limbs"]]`
3. Modify individual weights in the copied list
4. Update `state["field"]` with the new limbs so downstream systems see changes

**Accessing the OrientationalField object:** The `OrientationalField` instance may not be directly accessible from `SystemState`. Read `src/agenetic/network/graph.py` to understand how the field is injected into state and whether the graph reads state["field"] back into the OrientationalField after processing. If the field object IS accessible (e.g., passed through state or available as a graph attribute), use `field.write(limbs, caller_token=SleepSystem.WRITE_TOKEN)`. If NOT, modify `state["field"]["limbs"]` directly and document that the graph must sync these changes. Choose the approach that matches the existing architecture — do not modify graph.py.

**Signal derivation (consolidation-derived):**

1. **Noise ratio** = entries_pruned / cache_size_before (0.0 if cache was empty)
   - High noise ratio (> 0.3) → system accumulating junk → increase resting stance cluster
   - Low noise ratio (< 0.1) → system retaining well → no signal

2. **Threat pressure** = threats_promoted / total_threats (0.0 if no threats)
   - High threat pressure (> 0.3) → sustained threat → increase Ārēka (8) and Nivṛtti (3) toward gate thresholds

3. **Novelty rate** = cache_growth_since_last_sleep / ticks_since_last_sleep (requires sleep_state tracking)
   - High novelty (> 0.5 new entries per tick) → lots of new patterns → increase Tarka (2, discernment)

**Weight update procedure:**

```
For each limb in the copied limbs list:
    1. Compute gravity_decay = -0.01 * (current_weight - 0.5)
       (Always pulls toward 0.5. Magnitude proportional to distance from center.)
    
    2. Compute consolidation_delta from signals above:
       - Convergent cluster (IDs in CONVERGENT_CLUSTER_IDS): +0.03 if noise_ratio > 0.3, else 0.0
       - Ārēka (limb 8): +0.03 if threat_pressure > 0.3, else 0.0
       - Nivṛtti (limb 3): +0.03 if threat_pressure > 0.3, else 0.0
       - Tarka (limb 2): +0.02 if novelty_rate > 0.5, else 0.0
       - All other limbs: 0.0
    
    3. total_delta = gravity_decay + consolidation_delta
    
    4. Clamp: total_delta = max(-0.05, min(0.05, total_delta))
    
    5. new_weight = max(0.0, min(1.0, current_weight + total_delta))
    
    6. Update limb["weight"] = new_weight in the copied list
```

After updating, write changes back via the mechanism determined above.

### A5: Repair Check and Apoptotic Condition

**Repair check:** Consolidation had effect if ANY of:
- Cache size decreased (entries were pruned)
- Immune log changed (promotions, demotions, or removals occurred)
- At least one weight moved (any limb weight differs from pre-sleep value)

If none of these occurred, repair_check returns False.

**Apoptotic condition:** Track `consecutive_no_improvement` in `state["sleep_state"]`. Increment when repair_check would return False. Reset to 0 when repair_check returns True. Trigger apoptosis when `consecutive_no_improvement >= 3`.

## Part B: Tests

### B1: Sleep Unit Tests

Create `tests/test_sleep.py` with tests covering:

Tick gating:
- Sleep fires at tick intervals (tick 10, 20, 30 for interval=10)
- Sleep does NOT fire between intervals (tick 5, 15)
- Sleep does NOT fire at tick 0
- Custom tick_interval is respected

Cache pruning:
- Entries with encounter_count <= 2 and stale > threshold are removed
- Entries with encounter_count > 2 are never removed regardless of age
- Entries with encounter_count <= 2 but NOT stale are preserved
- Cache size metrics are correctly computed
- Empty cache produces no errors

Immune log consolidation:
- Threats with encounter_count >= 3 get confidence +0.1
- Confidence capped at 1.0
- Stale low-encounter threats get confidence -0.1
- Threats with confidence <= 0.0 are removed
- Empty immune log produces no errors
- ISO datetime comparison works correctly

Weight modification:
- High noise ratio increases convergent cluster weights
- All five convergent cluster limbs get the same delta
- High threat pressure increases Ārēka and Nivṛtti weights
- High novelty rate increases Tarka weight
- Gravity decay pulls weights toward 0.5
- Per-tick delta clamped to ±0.05
- Absolute weight bounds [0.0, 1.0] enforced
- Default weights (all 0.5) with no consolidation signals → only gravity (no change since already at 0.5)
- Weight changes persist in the returned SystemState

Repair and apoptosis:
- repair_check returns True when consolidation had effect
- repair_check returns False when no changes occurred
- apoptotic_condition triggers after 3 consecutive no-improvement ticks
- apoptotic_condition resets after a successful consolidation

Sleep state persistence:
- First invocation initializes sleep_state with defaults
- Subsequent invocations read and update existing sleep_state
- sleep_state survives across process() calls via SystemState

### B2: Sleep Integration Tests

Create integration tests that verify sleep operates correctly within the graph:

- Sleep modifies field weights that are readable by subsequent system invocations
- Subconscious cache is smaller after a cycle that includes sleep
- Immune threat log reflects consolidation after sleep fires
- Sleep respects tick_rate — does not fire every cycle

## Part C: Planning State Management

### C1: Copy State to Planning Entry

Copy `handoff/state.md` to `planning/017_sleep_implementation.md`. This is the permanent numbered planning entry for this directive cycle. Never overwrite previous planning entries.

### C2: Update CURRENT.md from Repo Inspection

After all code changes are complete and tests pass, rebuild `planning/CURRENT.md` by inspecting the actual repo state. Include updated test count, system statuses (sleep should now show as operational), and any blockers that changed. Do NOT copy from old CURRENT.md — extract from ground truth.

## Part D: Documentation

### D1: DEVLOG Entry

Append an entry to `DEVLOG.md`:

```
## [DATE] — Directive 017: Sleep System Implementation

**Commit:** [agent fills in]
**Tests:** [agent fills in total count]

Implemented sleep as the first meta-domain system. Sleep fires every 10 cycles
(configurable) and performs three consolidation operations:

1. Subconscious cache pruning — deeper than inline pruning (catches 2-encounter
   stale patterns), preventing monotonic cache growth toward the 10K apoptotic limit.
2. Immune threat log consolidation — promotes confirmed recurring threats,
   demotes stale unconfirmed threats, removes expired entries. Uses datetime-based
   staleness (1hr default) matching immune's ISO timestamp format.
3. Orientational field weight modification — derives adjustment signals from
   consolidation observations (noise ratio, threat pressure, novelty rate)
   and applies bounded weight deltas (±0.05 max per tick) with gravitational
   decay toward the 0.5 default. Uses OrientationalField.write() with
   SleepSystem.WRITE_TOKEN authorization.

The convergent cluster (Bodhi, Nivrtti-Rest, Mirror, Ajāti, Asparśa-Yoga)
moves as a coordinated group, enabling the resting stance composite to eventually
cross gate thresholds.

Unblocks: dormant gate (audit finding #2), convergent cluster (finding #3),
static field (recommendation #8). Mitigates: cache growth (finding #4).
```

### D2: README Update

Update the system status table in `README.md`:
- Sleep: change from "Stub" to "Operational — consolidation and weight modification"
- Update test count to reflect new total

## Scope Boundaries

**DO:**
- Implement sleep system in `src/agenetic/systems/sleep.py`
- Add unit and integration tests for sleep
- Update DEVLOG.md, README.md
- Read all referenced source files to understand actual interfaces and data structures
- Read `references/asparsa_limbs.md` to correctly identify limbs by their existing identifiers
- Read `src/agenetic/network/graph.py` to understand field injection and state flow

**DO NOT:**
- Modify sensory, immune, subconscious, conscious, motor, or genetic system implementations
- Modify text_codec.py (Māyāvāda fix already complete in D016)
- Add homeostatic monitoring or triggers — sleep fires on fixed schedule only
- Implement epigenetic feedback to genetic layer
- Modify connection weights in network topology
- Modify the `OrientationalField` class itself (use `write()` as-is)
- Add LLM calls — sleep is meta-domain but pure Python
- Edit any historical handoff files
- Change the BaseSystem interface or SystemState TypedDict definition
- Hardcode limb-to-feature mappings as architectural truth — weight signals are engineering assignments

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/sleep.py` | Replaced (stub → full implementation) |
| `tests/test_sleep.py` | Created (or integrated into existing test structure) |
| `DEVLOG.md` | Updated (D017 entry) |
| `README.md` | Updated (sleep status, test count) |
| `handoff/state.md` | Provided — copy to planning entry |
| `planning/017_sleep_implementation.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `handoff/017_directive.md` | This file |
| `handoff/017_response.md` | Agent's completion report |

## Verification Checklist

- [ ] `sleep.py` implements `BaseSystem` interface: `process()`, `repair_check()`, `apoptotic_condition()`, `tick_rate`
- [ ] `sleep.py` preserves existing `WRITE_TOKEN` constant
- [ ] `sleep.py` fires at correct tick intervals (not every cycle, not at tick 0)
- [ ] `sleep.py` prunes cache entries with encounter_count <= 2 and stale beyond threshold
- [ ] `sleep.py` does NOT prune entries with encounter_count > 2
- [ ] `sleep.py` consolidates immune threat log using ISO datetime comparison (not tick numbers)
- [ ] `sleep.py` promotes threats with encounter_count >= 3 (confidence +0.1, cap 1.0)
- [ ] `sleep.py` demotes stale low-encounter threats (confidence -0.1)
- [ ] `sleep.py` removes threats with confidence <= 0.0
- [ ] `sleep.py` computes weight deltas from consolidation metrics (noise ratio, threat pressure, novelty rate)
- [ ] `sleep.py` writes field weights via `OrientationalField.write()` with `caller_token=SleepSystem.WRITE_TOKEN` (or equivalent state-based mechanism determined from graph.py)
- [ ] `sleep.py` moves convergent cluster limbs (CONVERGENT_CLUSTER_IDS) with uniform delta
- [ ] `sleep.py` applies gravitational decay toward 0.5 on all limbs
- [ ] `sleep.py` clamps per-tick delta to ±0.05 and absolute weight to [0.0, 1.0]
- [ ] `sleep.py` persists tracking data in state["sleep_state"]
- [ ] `sleep.py` apoptotic_condition triggers after 3 consecutive no-improvement ticks
- [ ] All sleep unit tests pass (tick gating, pruning, consolidation, weights, repair, apoptosis, state persistence)
- [ ] All sleep integration tests pass (field persistence, cache reduction, threat log modification)
- [ ] All 336 existing tests still pass unchanged
- [ ] No other system implementations modified
- [ ] text_codec.py NOT modified (Māyāvāda already fixed in D016)
- [ ] No historical handoff files edited
- [ ] DEVLOG.md entry added with commit hash and test count
- [ ] README.md updated with sleep status and test count
- [ ] `handoff/state.md` copied to `planning/017_sleep_implementation.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection (not copied from old version)
- [ ] Git commit and push completed
