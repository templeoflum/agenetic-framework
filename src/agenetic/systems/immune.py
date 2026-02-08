"""Immune system — Discrimination.

Relationship to information: Evaluates. Distinguishes self from not-self,
safe from threatening.

Boundary enforcement and threat recognition. Determines what should be
processed further and what should be rejected or quarantined. Operates
in two modes:

- Innate immunity: fixed rules, pattern matching against known threat
  signatures. Fast, reflexive, no learning required.
- Adaptive immunity: maintains a threat log that persists across cycles
  and consolidates during sleep. Adversarial patterns encountered once
  get flagged faster on re-encounter.

Tick rate: Every cycle. Runs in parallel with sensory transduction.

Repair check: Is the self/not-self boundary correctly calibrated?
Are there false positives or false negatives?

Apoptotic trigger: Immune system is overwhelmed by sustained adversarial
bombardment, or self/not-self boundary has become incoherent.

State: Threat log (persistent across cycles, writable by immune,
prunable by sleep).
"""

from agenetic.systems.base import BaseSystem, SystemState


class ImmuneSystem(BaseSystem):
    """Discrimination layer — evaluates threats and enforces boundaries."""

    def __init__(self) -> None:
        super().__init__(
            name="immune",
            description="Discriminates self from not-self, enforces boundaries",
        )

    @property
    def tick_rate(self) -> str:
        return "every_cycle"

    def process(self, state: SystemState) -> SystemState:
        return state

    def repair_check(self, state: SystemState) -> bool:
        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        return False
