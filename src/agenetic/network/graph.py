"""LangGraph wiring — builds a runnable graph from the seven systems.

Phase 1 uses a simplified routing strategy:
1. Process every-cycle systems (sensory, immune, subconscious) in parallel
2. Conditionally route to conscious (if escalation flag is set)
3. Route to motor for output expression
4. Sleep and genetic are not actively routed in Phase 1 (they will be
   triggered by tick count / homeostatic conditions in Phase 2)

The full network routing with weighted connections comes in Phase 2.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from agenetic.field.orientational import OrientationalField
from agenetic.systems.base import BaseSystem, SystemState


class GraphState(TypedDict):
    """LangGraph-compatible state schema.

    Mirrors SystemState but defined here so LangGraph can register
    each key as a channel with proper state management.
    """

    input: Any
    field: dict
    immune_log: list
    metadata: dict
    flags: dict


def create_default_state(
    input_data: Any = None,
    field: OrientationalField | None = None,
) -> GraphState:
    """Create a fresh state with sensible defaults.

    Args:
        input_data: The input to process.
        field: The orientational field instance. If None, creates a new one.
    """
    if field is None:
        field = OrientationalField()

    return {
        "input": input_data,
        "field": field.read(),
        "immune_log": [],
        "metadata": {
            "tick": 0,
            "timestamps": [],
            "routing_history": [],
        },
        "flags": {
            "degraded": [],
            "escalate_to_conscious": True,  # Phase 1: always escalate
            "apoptotic": False,
        },
    }


def _make_node(system: BaseSystem):
    """Wrap a system's process method as a LangGraph node function.

    The node runs the system's process(), then its repair_check(). If
    repair fails, the system name is added to the degradation flags.
    """

    def node_fn(state: GraphState) -> GraphState:
        # Record routing.
        metadata = state["metadata"]
        history = list(metadata["routing_history"])
        history.append(system.name)
        updated_metadata = {**metadata, "routing_history": history}

        # Build full state for system processing.
        full_state: SystemState = {
            "input": state["input"],
            "field": state["field"],
            "immune_log": state["immune_log"],
            "metadata": updated_metadata,
            "flags": state["flags"],
        }

        # Process.
        result = system.process(full_state)

        # Inline repair check.
        if not system.repair_check(result):
            degraded = list(result["flags"]["degraded"])
            degraded.append(system.name)
            result = {
                **result,
                "flags": {**result["flags"], "degraded": degraded},
            }

        return result

    return node_fn


def _should_escalate(state: GraphState) -> Literal["conscious", "motor"]:
    """Route to conscious if escalation is flagged, otherwise skip to motor."""
    if state["flags"]["escalate_to_conscious"]:
        return "conscious"
    return "motor"


def build_graph(
    sensory: BaseSystem,
    immune: BaseSystem,
    subconscious: BaseSystem,
    conscious: BaseSystem,
    motor: BaseSystem,
    sleep: BaseSystem,
    genetic: BaseSystem,
) -> Any:
    """Build a LangGraph StateGraph wiring the seven systems together.

    Phase 1 simplified routing:
    - sensory runs first (transduction must happen before anything else)
    - immune and subconscious run after sensory (parallel in biology,
      sequential here for simplicity)
    - conditional routing to conscious (on escalation) or straight to motor
    - motor produces final output

    Sleep and genetic are included as nodes but not actively routed
    in Phase 1. They will be triggered by tick scheduling in Phase 2.

    Returns:
        A compiled LangGraph that can be invoked with a GraphState.
    """
    graph = StateGraph(GraphState)

    # Add all system nodes.
    graph.add_node("sensory", _make_node(sensory))
    graph.add_node("immune", _make_node(immune))
    graph.add_node("subconscious", _make_node(subconscious))
    graph.add_node("conscious", _make_node(conscious))
    graph.add_node("motor", _make_node(motor))

    # Phase 1 routing: linear flow with conditional conscious bypass.
    graph.set_entry_point("sensory")
    graph.add_edge("sensory", "immune")
    graph.add_edge("immune", "subconscious")
    graph.add_conditional_edges(
        "subconscious",
        _should_escalate,
        {"conscious": "conscious", "motor": "motor"},
    )
    graph.add_edge("conscious", "motor")
    graph.add_edge("motor", END)

    return graph.compile()
