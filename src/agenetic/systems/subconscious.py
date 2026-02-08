"""Subconscious system — Association.

Relationship to information: Resonates. Surfaces relevant patterns without
explicit reasoning.

Non-reporting preprocessing. Pattern matching, relevance priming, contextual
association. Operates below the threshold of explicit reasoning — the system
"notices" things without being able to articulate why. Includes RAG retrieval,
embedding similarity, and any process that surfaces information based on
resonance rather than explicit query.

Tick rate: Every cycle, but accumulates across cycles. A single tick produces
associations; sustained ticks strengthen or weaken associative pathways.

Repair check: Are surfaced associations actually relevant, or is the layer
pattern-matching on noise?

Apoptotic trigger: Associative capacity has collapsed — surfacing everything
(no discrimination) or nothing (no resonance).
"""

from agenetic.systems.base import BaseSystem, SystemState


class SubconsciousSystem(BaseSystem):
    """Association layer — surfaces relevant patterns through resonance."""

    def __init__(self) -> None:
        super().__init__(
            name="subconscious",
            description="Surfaces relevant patterns through associative resonance",
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
