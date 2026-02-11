# Directive 017 Response — Sleep System Implementation

**Status:** Complete
**Tests:** 371 passing + 2 skipped (was 336 + 2 skipped; +35 new tests)
**Date:** 2026-02-11

## What Was Done

Replaced the sleep stub with a full implementation that performs three consolidation operations: subconscious cache pruning, immune threat log consolidation, and orientational field weight modification.

### Part A: Sleep System Implementation

**A1: Replaced stub** (`src/agenetic/systems/sleep.py`, 239 LOC)
- Constructor accepts `tick_interval` (default 10), `staleness_threshold` (default 50 ticks), `staleness_seconds` (default 3600)
- Tick gating: fires when `tick % tick_interval == 0` AND `tick > 0`
- Sleep state persistence via `state["sleep_state"]` dict (runtime addition, not in SystemState TypedDict)
- Preserves existing `WRITE_TOKEN = "sleep_system_authorized"`

**A2: Subconscious cache pruning**
- Removes entries where `encounter_count <= 2` AND `(tick - last_seen_tick) > staleness_threshold`
- Deeper than subconscious inline pruning (which only catches encounter_count == 1 and > 100 ticks)
- Records entries_pruned, cache_size_before, cache_size_after for signal derivation

**A3: Immune threat log consolidation**
- Promotes threats with `encounter_count >= 3` (confidence +0.1, capped at 1.0)
- Demotes stale low-encounter threats where `elapsed > staleness_seconds` AND `encounter_count <= 2` (confidence -0.1)
- Removes expired entries (confidence <= 0.0)
- Uses `datetime.fromisoformat()` for ISO datetime staleness comparison (not tick numbers)
- Handles timezone-naive timestamps by assuming UTC

**A4: Orientational field weight modification**
- Signal derivation from consolidation observations:
  - noise_ratio = entries_pruned / cache_size_before (> 0.3 triggers)
  - threat_pressure = threats_promoted / total_threats (> 0.3 triggers)
  - novelty_rate = cache_growth / ticks_since_last_sleep (> 0.5 triggers)
- Weight update per limb: gravity_decay + consolidation_delta, clamped ±0.05, absolute [0.0, 1.0]
- Convergent cluster (IDs 12, 14, 15, 17, 18) receives uniform delta from noise_ratio signal
- Areka (8) and Nivrtti (3) receive delta from threat_pressure signal
- Tarka (2) receives delta from novelty_rate signal
- Gravity: -0.01 * (weight - 0.5) — always pulls toward midpoint
- Field modified via `state["field"]["limbs"]` direct modification (OrientationalField object not accessible from SystemState)

**A5: Repair check and apoptotic condition**
- repair_check returns True when consolidation had any effect (pruning, promotion, demotion, removal, or weight change)
- apoptotic_condition triggers after 3 consecutive no-improvement sleep ticks
- Both track state via `sleep_state["consecutive_no_improvement"]` and `sleep_state["last_had_effect"]`

### Part B: Tests

Created `tests/test_sleep.py` with 35 tests:

| Category | Count | Coverage |
|---|---|---|
| Tick gating | 4 | Fires at interval, not between, not at 0, custom interval |
| Cache pruning | 5 | Prunes stale low-encounter, preserves high-encounter, preserves recent, metrics, empty cache |
| Immune consolidation | 6 | Promotes recurring, caps at 1.0, demotes stale, removes expired, empty log, ISO datetime |
| Weight modification | 9 | Noise→cluster, uniform delta, threat→Areka/Nivrtti, novelty→Tarka, gravity, clamp, bounds, no-signal, persistence |
| Repair/apoptosis | 4 | True on effect, False on no change, triggers at 3, resets on success |
| State persistence | 3 | First init, subsequent updates, survives across calls |
| Integration | 4 | Field readable, cache smaller, log consolidated, tick rate respected |

All 336 existing tests pass unchanged.

## Architectural Decision: Field Access

The OrientationalField object is not stored in SystemState. The graph's `create_default_state()` calls `field.read()` and stores the resulting dict. Sleep therefore modifies `state["field"]["limbs"]` directly rather than calling `OrientationalField.write()`. This is documented in the sleep implementation. If application code holds a reference to the OrientationalField and needs to sync after sleep processing, it must explicitly call `field.write(state["field"]["limbs"], caller_token=SleepSystem.WRITE_TOKEN)`.

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/sleep.py` | Replaced (stub → full implementation, 239 LOC) |
| `tests/test_sleep.py` | Created (35 tests) |
| `DEVLOG.md` | Updated (D017 entry) |
| `README.md` | Updated (sleep status, test count) |
| `planning/017_sleep_implementation.md` | Created (copied from handoff/state.md) |
| `planning/CURRENT.md` | Updated (rebuilt from repo inspection) |
| `handoff/017_response.md` | This file |

## Verification Checklist

- [x] `sleep.py` implements `BaseSystem` interface: `process()`, `repair_check()`, `apoptotic_condition()`, `tick_rate`
- [x] `sleep.py` preserves existing `WRITE_TOKEN` constant
- [x] `sleep.py` fires at correct tick intervals (not every cycle, not at tick 0)
- [x] `sleep.py` prunes cache entries with encounter_count <= 2 and stale beyond threshold
- [x] `sleep.py` does NOT prune entries with encounter_count > 2
- [x] `sleep.py` consolidates immune threat log using ISO datetime comparison (not tick numbers)
- [x] `sleep.py` promotes threats with encounter_count >= 3 (confidence +0.1, cap 1.0)
- [x] `sleep.py` demotes stale low-encounter threats (confidence -0.1)
- [x] `sleep.py` removes threats with confidence <= 0.0
- [x] `sleep.py` computes weight deltas from consolidation metrics (noise ratio, threat pressure, novelty rate)
- [x] `sleep.py` writes field weights via state["field"]["limbs"] direct modification (OrientationalField not accessible from SystemState)
- [x] `sleep.py` moves convergent cluster limbs (CONVERGENT_CLUSTER_IDS) with uniform delta
- [x] `sleep.py` applies gravitational decay toward 0.5 on all limbs
- [x] `sleep.py` clamps per-tick delta to ±0.05 and absolute weight to [0.0, 1.0]
- [x] `sleep.py` persists tracking data in state["sleep_state"]
- [x] `sleep.py` apoptotic_condition triggers after 3 consecutive no-improvement ticks
- [x] All sleep unit tests pass (35 tests: tick gating, pruning, consolidation, weights, repair, apoptosis, state persistence)
- [x] All sleep integration tests pass (field persistence, cache reduction, threat log modification)
- [x] All 336 existing tests still pass unchanged
- [x] No other system implementations modified
- [x] text_codec.py NOT modified (Mayavada already fixed in D016)
- [x] No historical handoff files edited
- [x] DEVLOG.md entry added
- [x] README.md updated with sleep status and test count
- [x] `handoff/state.md` copied to `planning/017_sleep_implementation.md`
- [x] `planning/CURRENT.md` rebuilt from actual repo inspection (not copied from old version)
- [x] Git commit and push pending
