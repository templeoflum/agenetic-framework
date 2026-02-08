"""Conscious system — Deliberation.

Relationship to information: Reasons. Explicitly processes, analyzes, and
decides.

Deliberately constrained active processing. The only layer that reasons
explicitly, weighs evidence, plans, and makes decisions. Consciousness is
the bottleneck, not the workhorse. Most processing happens elsewhere.

Receives primed context from the subconscious, threat assessments from the
immune layer, and transduced input from the sensory layer. Produces decisions
about what to express, how to express it, and whether to express anything
at all.

Tick rate: Fires only when escalated. The subconscious determines whether
input requires conscious deliberation or can be handled through reflex paths.

Repair check: Is the reasoning internally consistent? Does the output follow
from the inputs? Check for motivated reasoning.

Apoptotic trigger: Reasoning has entered an irrecoverable loop, or confidence
has collapsed below a threshold where any output would be arbitrary.
"""

from agenetic.systems.base import BaseSystem, SystemState


class ConsciousSystem(BaseSystem):
    """Deliberation layer — explicit reasoning and decision-making."""

    def __init__(self) -> None:
        super().__init__(
            name="conscious",
            description="Deliberates explicitly, reasons, and decides",
        )

    @property
    def tick_rate(self) -> str:
        return "on_escalation"

    def process(self, state: SystemState) -> SystemState:
        return state

    def repair_check(self, state: SystemState) -> bool:
        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        return False
