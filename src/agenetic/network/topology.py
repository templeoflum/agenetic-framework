"""Network topology — the connection matrix between the seven systems.

Defines which systems connect to which, connection type (primary vs secondary),
direction, and default weight. This is a data structure, not executable routing.

From ARCHITECTURE.md, Section: Connection Matrix.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConnectionType(Enum):
    """Whether a connection is always active or context-dependent."""

    PRIMARY = "primary"      # Strong, always active (default weight 1.0)
    SECONDARY = "secondary"  # Variable weight, context-dependent (default weight 0.5)


@dataclass(frozen=True)
class Connection:
    """A directed, weighted connection between two systems."""

    source: str
    target: str
    connection_type: ConnectionType
    weight: float
    description: str


# All system names for reference.
SYSTEM_NAMES = [
    "sensory",
    "immune",
    "subconscious",
    "conscious",
    "motor",
    "sleep",
    "genetic",
]

# Primary connections (strong, always active, default weight 1.0).
PRIMARY_CONNECTIONS: list[Connection] = [
    Connection("sensory", "immune", ConnectionType.PRIMARY, 1.0,
               "Raw input immediately evaluated for threats"),
    Connection("sensory", "subconscious", ConnectionType.PRIMARY, 1.0,
               "Raw input primes associative retrieval"),
    Connection("immune", "conscious", ConnectionType.PRIMARY, 1.0,
               "Threat assessments escalated for deliberation"),
    Connection("immune", "motor", ConnectionType.PRIMARY, 1.0,
               "Immediate rejection responses (reflex path)"),
    Connection("subconscious", "conscious", ConnectionType.PRIMARY, 1.0,
               "Primed associations delivered for deliberation"),
    Connection("subconscious", "motor", ConnectionType.PRIMARY, 1.0,
               "Cached/reflexive responses bypass deliberation"),
    Connection("conscious", "motor", ConnectionType.PRIMARY, 1.0,
               "Deliberated decisions sent for expression"),
    # Sleep → all systems
    Connection("sleep", "sensory", ConnectionType.PRIMARY, 1.0,
               "Consolidation affects sensory state"),
    Connection("sleep", "immune", ConnectionType.PRIMARY, 1.0,
               "Consolidation affects immune state"),
    Connection("sleep", "subconscious", ConnectionType.PRIMARY, 1.0,
               "Consolidation affects subconscious state"),
    Connection("sleep", "conscious", ConnectionType.PRIMARY, 1.0,
               "Consolidation affects conscious state"),
    Connection("sleep", "motor", ConnectionType.PRIMARY, 1.0,
               "Consolidation affects motor state"),
    Connection("sleep", "genetic", ConnectionType.PRIMARY, 1.0,
               "Consolidation writes epigenetic modifications"),
    # Genetic → all systems (read access)
    Connection("genetic", "sensory", ConnectionType.PRIMARY, 1.0,
               "Base specification read by sensory"),
    Connection("genetic", "immune", ConnectionType.PRIMARY, 1.0,
               "Base specification read by immune"),
    Connection("genetic", "subconscious", ConnectionType.PRIMARY, 1.0,
               "Base specification read by subconscious"),
    Connection("genetic", "conscious", ConnectionType.PRIMARY, 1.0,
               "Base specification read by conscious"),
    Connection("genetic", "sleep", ConnectionType.PRIMARY, 1.0,
               "Base specification read by sleep"),
]

# Secondary connections (variable weight, context-dependent, default weight 0.5).
SECONDARY_CONNECTIONS: list[Connection] = [
    Connection("conscious", "immune", ConnectionType.SECONDARY, 0.5,
               "Deliberation adjusts threat thresholds"),
    Connection("conscious", "sensory", ConnectionType.SECONDARY, 0.5,
               "Re-examination requests"),
    Connection("conscious", "subconscious", ConnectionType.SECONDARY, 0.5,
               "Directed retrieval"),
    Connection("motor", "conscious", ConnectionType.SECONDARY, 0.5,
               "Output feedback — expression difficulties escalated"),
    Connection("immune", "subconscious", ConnectionType.SECONDARY, 0.5,
               "Threat context shapes associative priming"),
    Connection("subconscious", "immune", ConnectionType.SECONDARY, 0.5,
               "Pattern recognition informs threat detection"),
]

# Absent connections (by design) — documented for completeness.
# These are NOT in the connection lists above.
# - Any (except sleep) → genetic: Only sleep writes to genetic expression
# - Motor → sensory: Output does not loop back as input within a single cycle
# - Genetic → motor: Base specification does not directly drive output

# All connections combined.
ALL_CONNECTIONS: list[Connection] = PRIMARY_CONNECTIONS + SECONDARY_CONNECTIONS


def get_connections(source: str | None = None, target: str | None = None) -> list[Connection]:
    """Filter connections by source and/or target system name."""
    result = ALL_CONNECTIONS
    if source is not None:
        result = [c for c in result if c.source == source]
    if target is not None:
        result = [c for c in result if c.target == target]
    return result


def connection_exists(source: str, target: str) -> bool:
    """Check if a connection exists between two systems."""
    return any(c.source == source and c.target == target for c in ALL_CONNECTIONS)


def get_weight(source: str, target: str) -> float:
    """Get the weight of a connection. Returns 0.0 if absent."""
    for c in ALL_CONNECTIONS:
        if c.source == source and c.target == target:
            return c.weight
    return 0.0
