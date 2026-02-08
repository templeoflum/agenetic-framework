"""Base system interface for the Agenetic Framework.

All seven systems inherit from BaseSystem and implement its interface.
The SystemState TypedDict defines the shared state passed between systems.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict


class ThreatEntry(TypedDict):
    """A single entry in the immune threat log."""

    pattern: str
    encounter_count: int
    confidence: float
    last_seen: str  # ISO timestamp


class Metadata(TypedDict):
    """Processing metadata tracked across ticks."""

    tick: int
    timestamps: list[str]
    routing_history: list[str]


class Flags(TypedDict):
    """System-wide signal flags."""

    degraded: list[str]  # system names that produced degraded output
    escalate_to_conscious: bool
    apoptotic: bool


class FieldLimb(TypedDict):
    """A single limb of the orientational field."""

    id: int
    name: str
    english_name: str
    principle: str
    weight: float


class FieldState(TypedDict):
    """The orientational field state."""

    limbs: list[FieldLimb]


# --- Signal-domain types (added in Directive 002) ---


class SignalFeatures(TypedDict):
    """Raw signal measurements extracted from input.

    Describes the structural properties of the input as signal.
    """

    density: float
    entropy: float
    coherence: float
    periodicity: float
    noise_floor: float
    impedance: float
    token_count: int
    vocabulary_richness: float


class SignalClassification(TypedDict):
    """Signal type classification based on features."""

    signal_type: Literal["steady_state", "transient", "periodic", "noise", "complex"]
    confidence: float
    components: list[str]


class SignalDelta(TypedDict):
    """Delta between measured signal and orientational field reference."""

    density_delta: float
    entropy_delta: float
    coherence_delta: float
    periodicity_delta: float
    noise_delta: float
    impedance_delta: float
    aggregate_deviation: float
    activated_limbs: list[int]


class SignalReport(TypedDict):
    """The output of the sensory layer — consumed by immune, subconscious, conscious."""

    features: SignalFeatures
    classification: SignalClassification
    delta: SignalDelta
    tick: int
    input_hash: str


class CachedSignalPattern(TypedDict):
    """A stored signal pattern from prior processing (subconscious cache)."""

    input_hash: str
    feature_vector: list[float]  # [density, entropy, coherence, periodicity, noise_floor, impedance]
    signal_type: str
    outcome: str  # "escalated", "reflex_response", "rejected"
    response_pattern_id: str | None
    encounter_count: int
    last_seen_tick: int


class ThreatAssessment(TypedDict):
    """Structured output of the immune system."""

    is_anomalous: bool
    anomaly_scores: dict[str, float]
    matched_patterns: list[str]
    threat_level: Literal["none", "low", "medium", "high", "critical"]
    recommended_action: Literal["proceed", "flag", "quarantine", "reject"]


class SubconsciousOutput(TypedDict):
    """Structured output of the subconscious system."""

    escalation_recommended: bool
    escalation_confidence: float
    matched_pattern_ids: list[str]
    primed_associations: list[str]


class MotorOutput(TypedDict):
    """Structured output of the motor/output system."""

    output_text: str
    target_profile: SignalFeatures  # what motor was aiming for
    strategies_applied: list[str]   # which restructuring strategies fired
    repair_passed: bool             # did output pass motor's own repair check


class SystemState(TypedDict):
    """The shared state object passed between all systems in the network.

    This is the core data structure that flows through the LangGraph graph.
    Each system reads from and writes to this state according to its role.
    """

    input: Any
    field: FieldState
    immune_log: list[ThreatEntry]
    metadata: Metadata
    flags: Flags
    signal_report: SignalReport | None
    threat_assessment: ThreatAssessment | None
    subconscious_output: SubconsciousOutput | None
    signal_pattern_cache: list[CachedSignalPattern]
    motor_output: MotorOutput | None


class BaseSystem(ABC):
    """Abstract base class for all seven systems in the Agenetic Framework.

    Each system has a defined relationship to information, a tick rate,
    inline repair checking, and apoptotic exit conditions. Systems
    communicate through weighted connections in a network topology.
    """

    def __init__(self, name: str, description: str) -> None:
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        """The system's identifier."""
        return self._name

    @property
    def description(self) -> str:
        """What this system does — its relationship to information."""
        return self._description

    @property
    @abstractmethod
    def tick_rate(self) -> str:
        """How often this system fires.

        Returns a string descriptor: 'every_cycle', 'on_escalation',
        'on_demand', 'periodic', or 'read_only'.
        """
        ...

    @abstractmethod
    def process(self, state: SystemState) -> SystemState:
        """Process the current system state and return updated state.

        This is the system's core operation. Each system transforms
        the state according to its specific relationship to information.
        The orientational field is available via state['field'].
        """
        ...

    @abstractmethod
    def repair_check(self, state: SystemState) -> bool:
        """Validate this system's output before passing it downstream.

        Returns True if the output passes the system's own constraints.
        Returns False if the output is degraded and should be flagged.
        """
        ...

    @abstractmethod
    def apoptotic_condition(self, state: SystemState) -> bool:
        """Check whether this system's exit conditions are met.

        Returns True if the system should terminate (apoptosis triggered).
        Returns False under normal operation.
        """
        ...
