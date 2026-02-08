"""Sensory system — Transduction.

Relationship to information: Transduces. Changes format without changing content.

Converts raw input into perceivable form. Does not interpret, filter for
relevance, or assign meaning. Structures information so downstream systems
can operate on it. Standardizes heterogeneous inputs (text, code, structured
data, conversation history, tool outputs) into a uniform internal representation.

Tick rate: Every cycle. Nothing enters the system without passing through
transduction.

Repair check: Does the output preserve the informational content of the input?
Is anything lost or distorted in format conversion?

Apoptotic trigger: Input is unprocessable — corrupt, adversarial beyond
recognition, or fundamentally outside the system's transduction capability.
"""

from agenetic.systems.base import BaseSystem, SystemState


class SensorySystem(BaseSystem):
    """Transduction layer — converts raw input into uniform internal form."""

    def __init__(self) -> None:
        super().__init__(
            name="sensory",
            description="Transduces raw input into uniform internal representation",
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
