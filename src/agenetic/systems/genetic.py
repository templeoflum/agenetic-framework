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

from agenetic.systems.base import BaseSystem, SystemState


class GeneticSystem(BaseSystem):
    """Generation layer — the minimal generative seed read by all systems."""

    def __init__(self) -> None:
        super().__init__(
            name="genetic",
            description="Encodes the minimal generative seed from which capabilities unfold",
        )

    @property
    def tick_rate(self) -> str:
        return "read_only"

    def process(self, state: SystemState) -> SystemState:
        return state

    def repair_check(self, state: SystemState) -> bool:
        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        return False
