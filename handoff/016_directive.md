# Directive 016 — Audit Remediation

**From:** Planning instance (claude.ai)
**To:** DNAgent (CLI build agent)
**Date:** 2026-02-10

## Context

Read `planning/CURRENT.md` first.

Directive 015 was the full audit phase. The mechanical audit (DNAgent) inventoried all 16 source files, 9 test files, 83 hardcoded thresholds, and 18 limb mappings. The conceptual audit (fresh adversarial instance) evaluated every finding. Both reports are in `handoff/015_mechanical_audit_report.md` and `handoff/015_conceptual_audit_report.md`.

This directive addresses the audit's **must-fix** and **should-fix** findings. Six targeted repairs, no new architecture. The system currently has 320 tests passing + 2 skipped.

**Audit findings addressed in this directive:**

| # | Finding | Severity | Fix |
|---|---------|----------|-----|
| 4 | Subconscious cache grows unbounded, apoptosis at 10,001 | Must-fix | LRU pruning in process() |
| 5 | Subconscious overwrites escalation flag, erasing upstream signals | Must-fix | OR-preserve existing flag |
| 5 | Immune escalation path is dead code in conscious gate | Must-fix | Immune sets flag for critical threats |
| 7 | Feature vectors unnormalized, entropy dominates matching | Should-fix | Min-max normalization |
| 6 | Ārēka threshold 0.3 vs 0.7 undocumented | Should-fix | Document as defense-in-depth |
| 7 | Māyāvāda formula semantically inverted | Should-fix | Invert formula direction |

**Audit findings NOT addressed (deferred):**

| # | Finding | Reason |
|---|---------|--------|
| 1 | Tautological confirmation (5/6 motor strategies) | Medium-term — needs structural redesign of motor strategies |
| 2 | Dormant gate (conscious suppression inert at default weights) | Requires sleep implementation to modify weights |
| 3 | Convergent cluster decoration (5 limbs individually inert) | Requires sleep implementation |

## Objective

Fix six audit findings across subconscious, immune, motor/codec, and conscious. All fixes are targeted code changes with test coverage. No new systems, no new architecture.

**Expected test count: 320 + ~24 new = ~344 tests.**

## Part A: Subconscious Cache Pruning

The subconscious caches every unique signal pattern. No pruning exists. At 10,001 entries, apoptotic_condition() triggers. This is a deployment time bomb.

### A1: Add pruning to SubconsciousSystem.process()

After the cache update section in `process()`, add a pruning step. Prune entries that meet ALL of these criteria:
- `encounter_count == 1` (seen only once — never reinforced)
- `last_seen_tick` is more than 100 ticks behind the current tick

The current tick is tracked in `subconscious_output["tick"]`. If no tick counter exists, add one to the subconscious output (increment each process() call).

**Pruning runs every process() call** but only removes entries meeting the criteria. This is cheap — iterate the cache dict, collect keys to remove, delete them.

**Do NOT change the apoptotic threshold** (10,000). The pruning prevents reaching it under normal operation. The threshold remains as a genuine safety net for pathological cases.

### A2: Tests (4 new)

Add to `tests/test_subconscious.py`:

1. **test_pruning_removes_stale_single_encounter**: Cache with entries at encounter_count=1, old ticks. Run process() with current tick > 100 ticks later. Verify stale entries removed.
2. **test_pruning_preserves_reinforced_entries**: Cache with entries at encounter_count > 1, old ticks. Verify these survive pruning.
3. **test_pruning_preserves_recent_entries**: Cache with entries at encounter_count=1, recent ticks. Verify these survive pruning.
4. **test_cache_does_not_reach_apoptosis_with_pruning**: Fill cache to ~9,900 entries with stale single-encounter entries, run process(). Verify cache is pruned well below 10,000.

## Part B: Escalation Flag Preservation

The subconscious currently unconditionally sets `flags["escalate_to_conscious"]` — True if escalation_recommended, False otherwise. This erases any upstream escalation signal (e.g., from immune in the future).

### B1: Change flag logic to OR-preserve

In `subconscious.py`, change the flag update section from:

```python
if escalation_recommended:
    flags["escalate_to_conscious"] = True
else:
    flags["escalate_to_conscious"] = False
```

To:

```python
existing = state["flags"].get("escalate_to_conscious", False)
flags["escalate_to_conscious"] = existing or escalation_recommended
```

This preserves any upstream True signal while still allowing subconscious to add its own escalation recommendation.

### B2: Tests (3 new)

Add to `tests/test_subconscious.py`:

1. **test_preserves_upstream_escalation_flag**: Set `flags["escalate_to_conscious"] = True` in input state. Run with input that does NOT trigger subconscious escalation. Verify flag remains True.
2. **test_subconscious_can_still_escalate**: Set flag False in input. Run with high-deviation input. Verify flag becomes True.
3. **test_both_sources_combine**: Set flag True in input. Run with high-deviation input. Verify flag remains True (OR of two Trues).

### B3: Fix existing tests

The D014 integration tests may set the flag manually or assume specific flag behavior. After changing the OR logic:
- Any test that explicitly sets `escalate_to_conscious=True` in the input and then checks it in the output should still pass (True OR anything = True).
- Any test that relies on the flag being reset to False may need adjustment. Check `test_integration.py` reflex path tests — if they pass low-deviation input with flag defaulting to False, they should be fine.

Run all tests after the change. If any fail, fix them by ensuring the input state has the correct initial flag value for the test scenario.

## Part C: Immune Escalation Connection

The conscious gate's highest-priority path checks `threat_action == "escalate"`. No system produces this value. The immune system outputs "proceed", "flag", "quarantine", or "reject" — never "escalate."

### C1: Add immune escalation flag for critical threats

In `immune.py`, at the end of `process()`, after determining the threat assessment:

If the immune system classifies the threat level as **critical** (the highest level — check the current threshold), set:
```python
flags["escalate_to_conscious"] = True
```

This uses the existing flag mechanism (which Part B now OR-preserves) rather than adding a new `threat_action="escalate"` value. The conscious gate already checks this flag for routing. The immune → conscious connection is now real.

**Do NOT add a new threat_action value.** The existing flag mechanism is the correct routing path. The dead code checking `threat_action == "escalate"` in the conscious gate should be removed or commented out with a note explaining the flag-based approach replaced it.

### C2: Tests (3 new)

Add to `tests/test_immune.py`:

1. **test_critical_threat_sets_escalation_flag**: Input with critical-level threat. Verify `flags["escalate_to_conscious"] == True` in output.
2. **test_non_critical_threat_does_not_set_flag**: Input with low/medium threat. Verify flag unchanged.
3. **test_immune_flag_combines_with_subconscious**: Integration-level test — run immune with critical input, then subconscious. Verify flag survives (Part B's OR logic preserves it).

## Part D: Feature Vector Normalization

Euclidean distance on unnormalized features means entropy (range 0–10) dominates matching while density, coherence, periodicity (range 0–1) are nearly invisible.

### D1: Add min-max normalization before distance computation

In `subconscious.py`, in the pattern matching section where Euclidean distance is computed, normalize each feature to [0, 1] range before computing distance.

Known feature ranges (from sensory output):
- `density`: 0.0 – 1.0 (already normalized)
- `coherence`: 0.0 – 1.0 (already normalized)
- `entropy`: 0.0 – ~10.0 (needs normalization — divide by 10.0, cap at 1.0)
- `periodicity`: 0.0 – 1.0 (already normalized)
- `complexity`: 0.0 – 1.0 (already normalized)
- `noise_floor`: 0.0 – 1.0 (already normalized)

In practice, only entropy needs rescaling. Apply: `normalized_entropy = min(entropy / 10.0, 1.0)`

Do this normalization ONLY for the distance computation. Do NOT modify the cached values or the sensory output. The cache stores raw values; normalization happens at comparison time.

### D2: Tests (4 new)

Add to `tests/test_subconscious.py`:

1. **test_normalized_distance_entropy_not_dominant**: Two patterns identical except entropy differs by 2.0 (raw). Another two patterns identical except density differs by 0.2 (same proportional difference at 1/10 scale). Verify the distances are approximately equal after normalization.
2. **test_matching_considers_all_features**: Pattern in cache. Query pattern with same entropy but different density. Verify no match (density difference matters now).
3. **test_normalization_does_not_alter_cached_values**: After process(), verify cached patterns contain raw (unnormalized) values.
4. **test_entropy_capped_at_one**: Input with entropy > 10.0 (edge case). Verify normalization caps at 1.0, doesn't produce values > 1.0.

## Part E: Ārēka Threshold Documentation

Ārēka (limb 8, "Inviolable Silence") has threshold 0.3 in text_codec.py and 0.7 in conscious.py. The audit flagged this as undocumented.

### E1: Document as intentional defense-in-depth

This IS intentional. The codec (motor layer) is the outer defense — it suppresses output at a lower threshold because it's the last gate before text leaves the system. The conscious gate is the inner defense — it suppresses deliberation at a higher threshold because suppressing an LLM call is a stronger action.

Add comments in both files:

In `text_codec.py`, at the Ārēka suppression check:
```python
# Ārēka defense-in-depth: codec threshold (0.3) is lower than conscious gate (0.7)
# because this is the final output gate — more cautious by design.
# See also: conscious.py Ārēka gate path.
```

In `conscious.py`, at the Ārēka gate path:
```python
# Ārēka defense-in-depth: conscious threshold (0.7) is higher than codec (0.3)
# because suppressing deliberation (LLM call) is a stronger action.
# See also: text_codec.py Ārēka suppression.
```

### E2: Add entry to ARCHITECTURE.md

In the relevant section of `docs/ARCHITECTURE.md` (near the Ārēka discussion or in a thresholds section), add a note:

> **Ārēka Defense-in-Depth:** Ārēka operates at two thresholds — 0.3 in the text codec (output suppression, outer gate) and 0.7 in the conscious gate (deliberation suppression, inner gate). The lower codec threshold reflects its position as the final output gate: more cautious because it's the last chance to suppress. The higher conscious threshold reflects that suppressing an LLM call is a more consequential action. Both require additional conditions beyond the weight threshold (noise level, entropy).

### E3: No tests needed

This is documentation only. No behavioral change.

## Part F: Māyāvāda Inversion Fix

Māyāvāda ("don't confuse map with source") controls the transformation cap via `max_allowed = 1.0 - mayavada_w`. This is semantically backwards: high humility weight (close to 1.0) produces max_allowed close to 0.0 — BUT the activation condition `mayavada_w < 0.45` means the cap never activates at high weights. The result: high humility = no constraint, low humility = constraint. Backwards.

### F1: Invert the formula

Change the Māyāvāda cap logic in `text_codec.py` from:

```python
# Current (broken):
# if mayavada_w < 0.45:  # low humility activates cap
#     max_allowed = 1.0 - mayavada_w  # low humility = high cap (inverted)
```

To:

```python
# Fixed:
# if mayavada_w > 0.55:  # high humility activates cap
#     max_allowed = 1.0 - mayavada_w  # high humility = low cap (correct)
```

The formula `max_allowed = 1.0 - mayavada_w` is actually correct in isolation — it's the activation condition that's inverted. At weight 0.7 (high humility): max_allowed = 0.3 (strong restraint). At weight 0.55 (mild humility): max_allowed = 0.45 (mild restraint). This is the correct semantic direction.

**Check the exact current code** — the above is based on the audit's description. Read `text_codec.py` and find the Māyāvāda section. The fix is: change `< 0.45` to `> 0.55` (or the equivalent threshold flip). The formula stays the same.

### F2: Update existing Māyāvāda tests

The existing test for Māyāvāda cap behavior (`test_codec.py`) tests at specific weight values. After inverting the activation condition:
- Tests at `mayavada_w=0.44` (cap active) should now test at `mayavada_w=0.56` or higher
- Tests at `mayavada_w=0.5` (cap inactive) should now test at `mayavada_w=0.5` (still inactive, below 0.55)

Read the existing tests, understand what they verify, and update the weight values to match the new activation direction.

### F3: New tests (2)

1. **test_mayavada_high_humility_constrains**: Weight 0.8 (high humility). Verify cap is active and max_allowed = 0.2 (strong restraint).
2. **test_mayavada_low_humility_unconstrained**: Weight 0.3 (low humility). Verify cap does not activate (no restraint).

## Part G: Tests — Cross-cutting Verification

### G1: Run full test suite

After all changes, run `pytest` and verify all tests pass. Report the new total.

### G2: Verify no regressions in integration tests

Run `tests/test_integration.py` specifically. The escalation flag change (Part B) and immune flag change (Part C) may affect integration path routing. Verify all three paths (reflex, escalated, suppression) still work correctly.

## Part H: Planning State Management

### H1: Copy State to Planning Entry
Copy `handoff/state.md` to `planning/016_remediation.md`.
This is the permanent numbered planning entry for this directive cycle.
Never overwrite previous planning entries.

### H2: Update CURRENT.md from Repo Inspection
After all code changes are complete and tests pass, update `planning/CURRENT.md` by inspecting the actual repo state. Rebuild from ground truth — do NOT copy from old CURRENT.md.

## Part I: Documentation Updates

### I1: DEVLOG entry

Add entry to `DEVLOG.md`:

```
## [DATE] — Directive 016: Audit Remediation

Commit: [hash]
Tests: [count] passing + 2 skipped

Addressed six findings from the D015 audit phase:
- Subconscious cache pruning (LRU, prevents 10K apoptosis time bomb)
- Escalation flag OR-preservation (upstream signals no longer erased)
- Immune escalation connection (critical threats now set escalation flag)
- Feature vector normalization (entropy no longer dominates distance)
- Ārēka threshold documented as defense-in-depth
- Māyāvāda activation condition inverted (high humility now constrains)

Deferred: tautological confirmation pattern (needs motor redesign),
dormant gate and convergent cluster (need sleep implementation).
```

## Scope Boundaries

**DO:**
- Fix the six audit findings as specified
- Add tests for each code change
- Update existing tests that break due to the changes
- Add documentation comments and ARCHITECTURE.md note
- Update DEVLOG, planning entries, CURRENT.md

**DO NOT:**
- Implement sleep or any new system
- Change the apoptotic threshold (10,000)
- Add new limbs or change limb weights
- Modify sensory.py, motor.py (orchestrator), graph.py, or prompt_assembly.py
- Redesign motor strategies (tautological confirmation is deferred)
- Change any file outside scope
- Edit historical handoff files

## Deliverables

| File | Action |
|------|--------|
| `src/agenetic/systems/subconscious.py` | Updated — cache pruning, flag OR-preservation, feature normalization |
| `src/agenetic/systems/immune.py` | Updated — escalation flag for critical threats |
| `src/agenetic/systems/conscious.py` | Updated — Ārēka comment, dead code cleanup |
| `src/agenetic/motor/text_codec.py` | Updated — Māyāvāda inversion fix, Ārēka comment |
| `docs/ARCHITECTURE.md` | Updated — Ārēka defense-in-depth note |
| `tests/test_subconscious.py` | Updated — 11 new tests (pruning 4, flag 3, normalization 4) |
| `tests/test_immune.py` | Updated — 3 new tests (escalation flag) |
| `tests/test_codec.py` | Updated — 2 new + existing tests adjusted for Māyāvāda |
| `tests/test_integration.py` | Updated — verified, adjusted if needed for flag changes |
| `DEVLOG.md` | Updated — D016 entry |
| `handoff/state.md` | Provided — planning notes for this cycle |
| `planning/016_remediation.md` | Created — copied from handoff/state.md |
| `planning/CURRENT.md` | Updated — rebuilt from repo inspection |
| `handoff/016_directive.md` | This file |
| `handoff/016_response.md` | Agent's completion report |

## Verification Checklist

- [ ] Subconscious cache pruning removes stale single-encounter entries
- [ ] Apoptotic threshold (10,000) unchanged
- [ ] Escalation flag uses OR-preservation, not unconditional set
- [ ] Immune sets escalation flag for critical threats
- [ ] Dead code `threat_action == "escalate"` in conscious gate removed or commented
- [ ] Feature normalization applied to distance computation only (cached values unchanged)
- [ ] Ārēka defense-in-depth documented in both source files and ARCHITECTURE.md
- [ ] Māyāvāda activation condition inverted (> 0.55, not < 0.45)
- [ ] Existing Māyāvāda tests updated for new activation direction
- [ ] All new tests pass (~16 new tests)
- [ ] All existing tests pass (320 + new = ~344 total expected)
- [ ] Integration tests (reflex, escalated, suppression paths) all pass
- [ ] DEVLOG entry added
- [ ] `handoff/state.md` copied to `planning/016_remediation.md`
- [ ] `planning/CURRENT.md` rebuilt from actual repo inspection
- [ ] No historical handoff files edited
- [ ] Git commit and push completed
