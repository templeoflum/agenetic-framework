"""Network topology and graph wiring for the Agenetic Framework."""

from agenetic.network.graph import build_graph, create_default_state
from agenetic.network.topology import (
    ALL_CONNECTIONS,
    PRIMARY_CONNECTIONS,
    SECONDARY_CONNECTIONS,
    SYSTEM_NAMES,
    Connection,
    ConnectionType,
    connection_exists,
    get_connections,
    get_weight,
)

__all__ = [
    "build_graph",
    "create_default_state",
    "ALL_CONNECTIONS",
    "PRIMARY_CONNECTIONS",
    "SECONDARY_CONNECTIONS",
    "SYSTEM_NAMES",
    "Connection",
    "ConnectionType",
    "connection_exists",
    "get_connections",
    "get_weight",
]
