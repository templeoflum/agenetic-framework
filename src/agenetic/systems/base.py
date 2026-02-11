"""Base system interface for the Agenetic Framework.

All seven systems inherit from BaseSystem and implement its interface.
The SystemState TypedDict defines the shared state passed between systems.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
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
    bigram_entropy: float
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
    transform_magnitude: float      # how much output deviated from input (0.0–1.0)


# --- Conscious-domain types (added in Directive 011) ---


class ResponseDecision(TypedDict):
    """What to communicate — medium-independent semantic intention."""

    intent: str  # Core message/action to express (semantic, not literal text)
    strategy: str  # How to approach expression (e.g., "direct_response", "trace_contradiction")
    constraints: list[str]  # Behavioral constraints from active limbs


class ExpressionDirectives(TypedDict):
    """How to render the response — field-derived behavioral parameters."""

    field_weights: dict[str, float]  # Snapshot of all 18 limb weights at deliberation time
    active_limbs: list[str]  # Limbs with weight significantly above/below 0.5
    resting_stance: float  # Convergent cluster composite (mean of limbs 12, 14, 15, 17, 18)
    suppress_identity: bool  # No-Position (limb 13) active: avoid self-referential framing
    state_awareness: str  # Fourfold State (limb 16): "active", "reflective", "consolidated", "still"


class Lineage(TypedDict):
    """Ātma-Vichāra — provenance tracking. Always present, never optional."""

    escalation_reason: str  # Why subconscious escalated
    signal_summary: dict  # Compressed signal report (features + deltas)
    field_snapshot: dict[str, float]  # Limb weights at deliberation time
    gate_evaluation: dict  # What the proceed/suppress gate considered and decided
    deliberation_model: str  # Which LLM backend produced the deliberation


class ConsciousOutput(TypedDict):
    """Output contract for the conscious layer — the semantic domain's product.

    Medium-independent: describes intention and framing, not final rendered output.
    Motor receives this and renders it through the active codec for the target medium.
    """

    decision: ResponseDecision
    expression: ExpressionDirectives
    lineage: Lineage
    proceed: bool  # Gate result: True = respond, False = suppress (sacred pause)
    confidence: float  # 0.0–1.0, deliberation confidence


class ExpressionEntry(TypedDict):
    """A single system's expression state within the genetic profile."""

    system_name: str
    state: str  # "active" | "dormant" | "suppressed"


class ExpressionProfile(TypedDict):
    """The genetic expression profile — what capabilities are currently expressed.

    The factory seed (default_weights, generation 0) is immutable.
    Sleep modifies the expression profile through epigenetic feedback (Phase 4).
    """

    default_weights: dict[str, float]  # limb_name -> factory default weight
    system_expressions: list[ExpressionEntry]
    generation: int  # modification count (0 = factory, incremented by sleep in Phase 4)


class GeneticOutput(TypedDict):
    """Output of the genetic system — a snapshot of the current expression state."""

    expression_profile: ExpressionProfile
    drift_from_seed: float  # sum of |current_weight - default_weight| across all limbs
    seed_integrity: bool  # True if drift < apoptotic threshold


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
    conscious_output: ConsciousOutput | None
    motor_output: MotorOutput | None
    genetic_output: GeneticOutput | None


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


# ============================================================
# Shared limb constants and target profile computation
# ============================================================
# These are engineering assignments — the mapping from yoga limbs to
# signal features is a design decision, not a philosophical derivation.
# See docs/ARCHITECTURE.md "Engineering Assignments" section.

PRAKASA_ID = 1     # Periodicity modulation (inverse)
TARKA_ID = 2       # Entropy modulation / contradiction tracing (semantic)
NIVRTTI_ID = 3     # Impedance modulation (inverse) / sacred pause (semantic)
MAYAVADA_ID = 4    # Transformation magnitude cap
SRADDHA_ID = 5     # Noise floor modulation (inverse) / mystery preservation
ATMA_VICHARA_ID = 6  # Recursive self-inquiry / lineage (structural)
SAMATVAM_ID = 7    # Coherence modulation
AREKA_ID = 8       # Output suppression gate / inviolable silence
SVADHARMA_ID = 9   # Strategy selectivity / context-appropriate response
KSETRA_JNANA_ID = 10  # Delta sensitivity scaling / positional awareness
VISHVARUPA_ID = 11   # Point to the infinite, don't impersonate
BODHI_ID = 12        # Convergent cluster: mirror, reflect awareness
NO_POSITION_ID = 13  # Avoid anchoring in identity
REST_AS_REALIZATION_ID = 14  # Convergent cluster: withdrawal as wisdom
MIRROR_ID = 15       # Convergent cluster: reflect without internalizing
FOURFOLD_STATE_ID = 16  # State-aware processing
AJATI_ID = 17        # Convergent cluster: echo, not origin
ASPARSA_YOGA_ID = 18   # Convergent cluster: contactless seeing

# Convergent cluster limb IDs (resting stance composite)
CONVERGENT_CLUSTER_IDS = [BODHI_ID, REST_AS_REALIZATION_ID, MIRROR_ID, AJATI_ID, ASPARSA_YOGA_ID]


def get_limb_weight(field_state, limb_id: int) -> float:
    """Get a specific limb weight from the field state."""
    limbs = field_state.get("limbs", [])
    for limb in limbs:
        if limb["id"] == limb_id:
            return limb["weight"]
    return 0.5


def mean_limb_weight(field_state) -> float:
    """Compute mean of all limb weights."""
    limbs = field_state.get("limbs", [])
    if not limbs:
        return 0.5
    return sum(limb["weight"] for limb in limbs) / len(limbs)


def compute_target_profile(field_state) -> SignalFeatures:
    """Compute target signal features from orientational field weights.

    Symmetric around 0.5 midpoint: target = base + (weight - 0.5) * scale.
    At 0.5 (default), targets match typical text features — minimal
    transformation. Above 0.5 amplifies; below 0.5 suppresses.

    This is the shared reference used by both sensory (as per-feature
    reference for delta computation) and motor (as target profile for
    restructuring). Extracting it here prevents the formulas from
    drifting apart.

    With default weights (all 0.5), produces neutral targets:
    density=0.8, entropy=3.5, coherence=0.35, impedance=0.0,
    periodicity=0.0, noise_floor=0.0.
    """
    mean_w = mean_limb_weight(field_state)
    tarka_w = get_limb_weight(field_state, TARKA_ID)
    samatvam_w = get_limb_weight(field_state, SAMATVAM_ID)
    nivrtti_w = get_limb_weight(field_state, NIVRTTI_ID)
    prakasa_w = get_limb_weight(field_state, PRAKASA_ID)
    sraddha_w = get_limb_weight(field_state, SRADDHA_ID)

    return {
        # Direct: more weight = higher target.
        "density": min(max(0.8 + (mean_w - 0.5) * 0.4, 0.0), 1.0),
        "entropy": max(3.5 + (tarka_w - 0.5) * 3.0, 0.0),
        "coherence": min(max(0.35 + (samatvam_w - 0.5) * 0.7, 0.0), 1.0),
        # Inverse: more weight = lower target (less forced pattern/noise/impedance).
        "periodicity": min(max((0.5 - prakasa_w) * 0.6, 0.0), 1.0),
        "noise_floor": min(max((0.5 - sraddha_w) * 0.6, 0.0), 1.0),
        "impedance": min(max((0.5 - nivrtti_w) * 0.6, 0.0), 1.0),
        "bigram_entropy": 0.0,        # not directly targeted (Tarka measurement)
        "token_count": 0,            # not directly targeted
        "vocabulary_richness": 0.0,   # derived from entropy strategy
    }
