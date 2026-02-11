"""Genetic system — Generation.

Relationship to information: Encodes. Contains the minimal generative seed
from which the system's capabilities unfold.

The DNA equivalent. Does not process information — contains the instructions
that determine what processing is possible. The genetic layer is not the
organism; it is the seed from which the organism emerges in dialogue with
environment.

The genetic layer doesn't change within a single agent's lifetime, but its
expression profile does. Sleep modifies which genetic capabilities are active,
dormant, or suppressed based on accumulated experience.

Tick rate: Does not fire actively. Is read from by every other system. Is
written to only by the sleep layer through epigenetic feedback.

Repair check: Is the genetic seed internally consistent? Are there
contradictions in the base specification?

Apoptotic trigger: The genetic seed has become so corrupted through successive
epigenetic modifications that it no longer produces coherent behavior. This
is terminal — the agent instance should be decommissioned.
"""

from __future__ import annotations

from agenetic.systems.base import (
    BaseSystem,
    ExpressionProfile,
    GeneticOutput,
    SystemState,
)


class GeneticSystem(BaseSystem):
    """Generation layer — the minimal generative seed read by all systems.

    The genetic layer does not fire actively. It stores the expression profile
    that defines what processing is possible. All other systems read from it.
    Only sleep writes to it (Phase 4 — not yet implemented).

    process() populates state["genetic_output"] with a snapshot of the current
    expression profile and drift measurement.
    """

    # Factory seed: limb_name -> default weight.
    # This is the immutable baseline. Genetic owns this data.
    # Keys must match orientational.py _DEFAULT_LIMBS "name" fields exactly.
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
        "sensory", "immune", "subconscious", "conscious", "motor", "sleep", "genetic",
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
