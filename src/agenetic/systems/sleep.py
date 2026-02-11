"""Sleep system — Consolidation and weight modification.

Relationship to information: Integrates. Prunes, strengthens, error-corrects,
and restructures.

Intentional consolidation between processing stages. Not background
maintenance — an architecturally mandated phase where the system stops
processing new inputs and instead processes its own state. During sleep:

- Prunes low-value associations from the subconscious layer
- Strengthens high-value associations based on use frequency and outcome quality
- Consolidates the immune threat log
- Modifies orientational field weights based on consolidation observations

Tick rate: Periodic. Fires every N cycles (default 10). Does not process new
inputs during sleep.

Repair check: Did consolidation actually improve system state? Returns True if
any consolidation effect was observed (pruning, promotion, demotion, removal,
or weight change). Returns False if sleep fired but produced no effect.

Apoptotic trigger: Sleep has failed to produce measurable consolidation for 3
consecutive sleep ticks — the consolidation mechanism itself is broken.

Critical architectural rule: Sleep is the ONLY system with write access to
the orientational field via OrientationalField.write().
"""

from __future__ import annotations

from datetime import datetime, timezone

from agenetic.systems.base import (
    AREKA_ID,
    CONVERGENT_CLUSTER_IDS,
    NIVRTTI_ID,
    TARKA_ID,
    BaseSystem,
    SystemState,
)


class SleepSystem(BaseSystem):
    """Consolidation layer — prunes, strengthens, and restructures state.

    Fires periodically (every tick_interval cycles). Prunes subconscious
    cache, consolidates immune threat log, modifies orientational field
    weights based on consolidation signals.

    ONLY system with write access to OrientationalField via write().
    """

    # Token used to authorize writes to the orientational field.
    WRITE_TOKEN = "sleep_system_authorized"

    def __init__(
        self,
        tick_interval: int = 10,
        staleness_threshold: int = 50,
        staleness_seconds: int = 3600,
    ) -> None:
        super().__init__(
            name="sleep",
            description="Consolidates system state through pruning, strengthening, and restructuring",
        )
        self._tick_interval = tick_interval
        self._staleness_threshold = staleness_threshold
        self._staleness_seconds = staleness_seconds

    @property
    def tick_rate(self) -> str:
        return "periodic"

    def process(self, state: SystemState) -> SystemState:
        tick = state["metadata"]["tick"]

        # Initialize sleep state on first invocation.
        sleep_state = state.get("sleep_state") or {
            "last_sleep_tick": 0,
            "cache_size_at_last_sleep": len(state.get("signal_pattern_cache", [])),
            "consecutive_no_improvement": 0,
            "last_had_effect": True,
        }

        # Tick gating: don't fire at tick 0, only at multiples of tick_interval.
        if tick == 0 or tick % self._tick_interval != 0:
            return {**state, "sleep_state": sleep_state}

        # === A2: Subconscious cache pruning (deeper than inline) ===
        cache = list(state.get("signal_pattern_cache", []))
        cache_size_before = len(cache)

        indices_to_remove = [
            i for i, entry in enumerate(cache)
            if entry["encounter_count"] <= 2
            and (tick - entry["last_seen_tick"]) > self._staleness_threshold
        ]
        for i in reversed(indices_to_remove):
            del cache[i]

        entries_pruned = len(indices_to_remove)
        cache_size_after = len(cache)

        # === A3: Immune threat log consolidation ===
        immune_log = [dict(entry) for entry in state.get("immune_log", [])]
        now = datetime.now(timezone.utc)

        threats_promoted = 0
        threats_demoted = 0
        total_threats = len(immune_log)

        for entry in immune_log:
            if entry["encounter_count"] >= 3:
                entry["confidence"] = min(entry["confidence"] + 0.1, 1.0)
                threats_promoted += 1
            else:
                # Check staleness via ISO datetime for low-encounter threats.
                try:
                    last_seen = datetime.fromisoformat(entry["last_seen"])
                    if last_seen.tzinfo is None:
                        last_seen = last_seen.replace(tzinfo=timezone.utc)
                    elapsed = (now - last_seen).total_seconds()
                    if elapsed > self._staleness_seconds:
                        entry["confidence"] -= 0.1
                        threats_demoted += 1
                except (ValueError, TypeError):
                    pass

        # Remove expired entries (confidence <= 0.0 after demotion).
        before_removal = len(immune_log)
        immune_log = [e for e in immune_log if e["confidence"] > 0.0]
        threats_removed = before_removal - len(immune_log)

        # === A4: Orientational field weight modification ===

        # Signal derivation from consolidation observations.
        noise_ratio = entries_pruned / cache_size_before if cache_size_before > 0 else 0.0
        threat_pressure = threats_promoted / total_threats if total_threats > 0 else 0.0

        ticks_since_last = tick - sleep_state["last_sleep_tick"]
        cache_growth = cache_size_before - sleep_state["cache_size_at_last_sleep"]
        novelty_rate = cache_growth / ticks_since_last if ticks_since_last > 0 else 0.0

        # Copy field limbs for modification.
        field_state = state["field"]
        limbs = [{**limb} for limb in field_state["limbs"]]

        weight_changed = False
        for limb in limbs:
            old_weight = limb["weight"]

            # Gravity: always pulls toward 0.5 midpoint.
            gravity_decay = -0.01 * (old_weight - 0.5)

            # Consolidation delta: derived from pruning/consolidation signals.
            consolidation_delta = 0.0
            if limb["id"] in CONVERGENT_CLUSTER_IDS:
                if noise_ratio > 0.3:
                    consolidation_delta = 0.03
            elif limb["id"] == AREKA_ID:
                if threat_pressure > 0.3:
                    consolidation_delta = 0.03
            elif limb["id"] == NIVRTTI_ID:
                if threat_pressure > 0.3:
                    consolidation_delta = 0.03
            elif limb["id"] == TARKA_ID:
                if novelty_rate > 0.5:
                    consolidation_delta = 0.02

            total_delta = gravity_decay + consolidation_delta

            # Clamp per-tick delta to ±0.05.
            total_delta = max(-0.05, min(0.05, total_delta))

            # Apply and clamp absolute weight to [0.0, 1.0].
            new_weight = max(0.0, min(1.0, old_weight + total_delta))
            limb["weight"] = new_weight

            if abs(new_weight - old_weight) > 1e-10:
                weight_changed = True

        # Write updated field back to state.
        # Note: OrientationalField object is not accessible from SystemState.
        # The graph stores field.read() (a dict) in state, not the object.
        # Sleep modifies state["field"]["limbs"] directly. If the caller holds
        # a reference to the OrientationalField and needs to sync, it must
        # call field.write(state["field"]["limbs"], caller_token=WRITE_TOKEN)
        # after processing.
        updated_field = {"limbs": limbs}

        # === A5: Repair check and apoptotic tracking ===
        had_effect = (
            entries_pruned > 0
            or threats_promoted > 0
            or threats_demoted > 0
            or threats_removed > 0
            or weight_changed
        )

        if had_effect:
            consecutive_no_improvement = 0
        else:
            consecutive_no_improvement = sleep_state["consecutive_no_improvement"] + 1

        new_sleep_state = {
            "last_sleep_tick": tick,
            "cache_size_at_last_sleep": cache_size_after,
            "consecutive_no_improvement": consecutive_no_improvement,
            "last_had_effect": had_effect,
        }

        return {
            **state,
            "signal_pattern_cache": cache,
            "immune_log": immune_log,
            "field": updated_field,
            "sleep_state": new_sleep_state,
        }

    def repair_check(self, state: SystemState) -> bool:
        """Did consolidation improve or maintain system state?

        Returns True if sleep hasn't fired yet, or if the last sleep tick
        produced a measurable consolidation effect.
        """
        sleep_state = state.get("sleep_state")
        if sleep_state is None:
            return True
        return sleep_state.get("last_had_effect", True)

    def apoptotic_condition(self, state: SystemState) -> bool:
        """Has sleep failed to produce consolidation for 3 consecutive ticks?

        Returns True when the consolidation mechanism itself appears broken.
        """
        sleep_state = state.get("sleep_state")
        if sleep_state is None:
            return False
        return sleep_state.get("consecutive_no_improvement", 0) >= 3
