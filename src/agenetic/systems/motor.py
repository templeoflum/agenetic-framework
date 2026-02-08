"""Motor/Output system — Expression.

Relationship to information: Translates. Converts internal states into
appropriate external form.

Composing outputs. Distinct from the conscious reasoning that decided what
to communicate — the motor layer determines how to communicate it. Tone,
format, medium selection, audience calibration, timing.

Takes the conscious layer's decision and renders it into the appropriate
output format. Selects tools, formats responses, calibrates tone to context.
The orientational field is particularly active here — tone is part of truth.

Tick rate: Fires whenever the conscious layer produces output, or when a
reflex path bypasses consciousness and drives output directly.

Repair check: Does the output accurately represent the internal state it's
expressing? Has tone distorted meaning?

Apoptotic trigger: Output channel is compromised — producing outputs that
systematically misrepresent internal states.
"""

from agenetic.systems.base import BaseSystem, SystemState


class MotorSystem(BaseSystem):
    """Expression layer — translates internal states into external form."""

    def __init__(self) -> None:
        super().__init__(
            name="motor",
            description="Translates internal states into appropriate external expression",
        )

    @property
    def tick_rate(self) -> str:
        return "on_demand"

    def process(self, state: SystemState) -> SystemState:
        return state

    def repair_check(self, state: SystemState) -> bool:
        return True

    def apoptotic_condition(self, state: SystemState) -> bool:
        return False
