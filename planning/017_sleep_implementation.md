# 017 — Sleep System Implementation

**Date:** 2026-02-11
**Directive type:** Implementation (new system, first meta-domain)

## Decisions

### Sleep scope: consolidation + weight modification, epigenetic deferred

Architecture describes five sleep responsibilities. Audit says "consolidation/pruning first, weight modification second." But three audit findings require weight modification to unblock the dormant gate, convergent cluster, and static field. Chose to include consolidation + weight modification in D017, defer epigenetic feedback and connection weight modification (genetic is still a stub, nothing to write to).

### Tick rate: 10 cycles, configurable

Too frequent = field never stabilizes between weight changes. Too infrequent = cache fills toward 10K apoptotic limit. 10 cycles = several sleep ticks before a pattern reaches subconscious's own 100-tick staleness threshold. Configurable for testing.

### Weight triggers: consolidation-derived

Sleep observes what it prunes and consolidates, then derives weight signals from those observations. Three signals: noise ratio (pruned/cache_size → resting stance), threat pressure (promoted/total → Ārēka, Nivṛtti), novelty rate (growth/ticks → Tarka). No external monitoring infrastructure needed.

### Weight bounds: ±0.05 per tick, gravity toward 0.5

Reaching the 0.7 gate threshold from 0.5 default takes minimum 4 sleep cycles (40 processing ticks). Gravitational decay (-0.01 × distance from 0.5) makes it asymmetric — easier to return to default than to move away. This prevents runaway weights while still allowing the field to shift meaningfully under sustained signal pressure.

### Convergent cluster moves as group

The five resting-stance limbs (Bodhi, Nivrtti-Rest, Mirror, Ajāti, Asparśa-Yoga — `CONVERGENT_CLUSTER_IDS` in base.py) get uniform consolidation delta. This is the only way the resting stance composite (mean of five) can cross gate thresholds, since moving a single limb barely shifts the mean.

### Māyāvāda fix NOT in this directive

The Māyāvāda activation inversion was already fixed in D016 (Part F of 016_response.md). Activation condition is already `> 0.55` in the current codebase. Do not duplicate this work.

## Observations

### Sleep's dual nature

Sleep crosses the signal-semantics boundary — but only in the read direction. It reads signal-domain data (cache statistics, threat log) and produces meta-domain outputs (weight modifications). It never interprets semantic content or calls an LLM. This makes it the first system that integrates across domains without entering the semantic domain.

### Threshold calibration is provisional

The 0.3 noise/threat thresholds, +0.03/+0.02 deltas, 0.5 novelty rate threshold — these are engineering assignments, not derived from any principle. They exist to make the system functional. Real calibration requires observing how the field actually responds to sustained signal pressure over many cycles. The audit pattern (mechanical → conceptual → remediation) can be applied to sleep parameters after deployment data exists.

### Immune log uses datetime, not ticks

Critical implementation detail: immune's `ThreatEntry.last_seen` is an ISO datetime string, not a tick number. Subconscious cache entries use `last_seen_tick` (integer). Sleep must handle both data formats correctly — tick-based comparison for cache, datetime-based comparison for immune log.

### Subconscious already prunes its own cache

D016 added inline pruning to subconscious.py: removes `encounter_count == 1` entries older than 100 ticks. Sleep's pruning is DEEPER — catches `encounter_count <= 2` entries using a shorter threshold (50 ticks). These complement each other: subconscious does lightweight garbage collection every cycle, sleep does deeper consolidation periodically.

### OrientationalField.write() takes full limb list

The field's write method signature is `write(limbs: list[FieldLimb], *, caller_token: str)`. It replaces the entire field state. Sleep must read, copy, modify individual weights, then write back the whole list. It cannot do incremental single-limb updates.

### Post-D017 landscape

After D017, sleep is the third operational system crossing domain boundaries (after motor in signal, conscious in semantic). The remaining stubs are genetic only. The orientational field becomes dynamic. The next major decision point is whether to implement genetic next or to focus on the feedback loops the architecture describes (motor → conscious, conscious → sensory, conscious → immune) which are all listed as missing in the audit.

## What to Watch

- **OrientationalField access pattern.** Sleep needs the actual OrientationalField object to call `write()`, or must modify state["field"] directly and rely on the graph to sync. DNAgent must read graph.py to determine which approach is correct. The directive instructs DNAgent to choose based on what exists.

- **Subconscious cache field names.** The directive specifies `encounter_count` and `last_seen_tick`. These match the `CachedSignalPattern` TypedDict in base.py. Verify the actual subconscious code uses these exact names.

- **Immune log `confidence` field.** The directive says `confidence`. The `ThreatEntry` TypedDict in base.py confirms this is `confidence` (not `confidence_score`). Verified against actual source.

- **Sleep state persistence.** `SystemState` is a TypedDict with no `sleep_state` key. Sleep adds it as a plain dict. This should work because SystemState is used as a dict in practice, but tests need to verify the key survives through graph processing.

- **Convergent cluster limb IDs.** base.py defines `CONVERGENT_CLUSTER_IDS = [BODHI_ID, REST_AS_REALIZATION_ID, MIRROR_ID, AJATI_ID, ASPARSA_YOGA_ID]` = [12, 14, 15, 17, 18]. Verified against actual source. The field calls limb 14 "Nivrtti-Rest" (not "Rest-as-Realization" — that's the English name, not the field name).

- **Existing parametrized tests.** Sleep already has 7 parametrized interface tests in test_systems.py from D001. The new sleep implementation must still pass these — they test `process()`, `repair_check()`, `apoptotic_condition()`, `tick_rate`, `name`, `description` on all seven systems.
