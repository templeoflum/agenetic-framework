"""LangGraph wiring — builds a runnable graph from the seven systems.

Phase 3 routing with feedback loops:
1. Signal domain (sensory, immune, subconscious) processes every cycle
2. Conditional escalation to conscious (subconscious decides)
3. Conscious may request re-examination → routes back to sensory (max 1)
4. Motor produces output
5. Motor may fail repair → routes back to conscious for retry (max 1)

Sleep and genetic are not actively routed (called outside the graph).

Secondary connections gated by topology weights:
- motor→conscious (0.5): retry on repair failure
- conscious→sensory (0.5): re-examination request
- conscious→immune: threshold adjustment via state propagation (no routing)

Setting a topology weight to 0.0 disables the corresponding feedback path.
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
    signal_report: Any  # SignalReport | None
    threat_assessment: Any  # ThreatAssessment | None
    subconscious_output: Any  # SubconsciousOutput | None
    signal_pattern_cache: list
    conscious_output: Any  # ConsciousOutput | None
    motor_output: Any  # MotorOutput | None
    genetic_output: Any  # GeneticOutput | None
    feedback: Any  # FeedbackSignals | None


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
            "escalate_to_conscious": False,  # Subconscious drives escalation
            "apoptotic": False,
        },
        "signal_report": None,
        "threat_assessment": None,
        "subconscious_output": None,
        "signal_pattern_cache": [],
        "conscious_output": None,
        "motor_output": None,
        "genetic_output": None,
        "feedback": None,
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
            "signal_report": state.get("signal_report"),
            "threat_assessment": state.get("threat_assessment"),
            "subconscious_output": state.get("subconscious_output"),
            "signal_pattern_cache": state.get("signal_pattern_cache", []),
            "conscious_output": state.get("conscious_output"),
            "motor_output": state.get("motor_output"),
            "genetic_output": state.get("genetic_output"),
            "feedback": state.get("feedback"),
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


def _default_feedback() -> dict:
    """Create default feedback signals."""
    return {
        "motor_retry_count": 0,
        "re_examine_count": 0,
        "immune_threshold_adjustments": {},
    }


def _get_topology_weight(source: str, target: str) -> float:
    """Get connection weight from topology. Returns 0.0 if absent."""
    from agenetic.network.topology import get_weight
    return get_weight(source, target)


def _increment_motor_retry(state: GraphState) -> GraphState:
    """Gate node: increment motor retry count before routing to conscious."""
    feedback = dict(state.get("feedback") or _default_feedback())
    feedback["motor_retry_count"] = feedback.get("motor_retry_count", 0) + 1
    return {**state, "feedback": feedback}


def _increment_re_examine(state: GraphState) -> GraphState:
    """Gate node: increment re-examination count before routing to sensory."""
    feedback = dict(state.get("feedback") or _default_feedback())
    feedback["re_examine_count"] = feedback.get("re_examine_count", 0) + 1
    return {**state, "feedback": feedback}


def _after_motor(state: GraphState) -> Literal["retry_gate", "__end__"]:
    """Route after motor: retry via conscious or finish.

    Fires the motor→conscious secondary connection if:
    1. Motor repair check failed
    2. Haven't already retried (max 1 retry)
    3. Topology weight for motor→conscious > 0
    """
    motor_output = state.get("motor_output")
    repair_failed = (
        motor_output is not None
        and not motor_output.get("repair_passed", True)
    )

    feedback = state.get("feedback") or _default_feedback()
    retry_count = feedback.get("motor_retry_count", 0)

    if repair_failed and retry_count < 1 and _get_topology_weight("motor", "conscious") > 0:
        return "retry_gate"

    return "__end__"


def _after_conscious(state: GraphState) -> Literal["re_examine_gate", "motor"]:
    """Route after conscious: re-examine or proceed to motor.

    Fires the conscious→sensory secondary connection if:
    1. Conscious requested re-examination
    2. Haven't already re-examined (max 1)
    3. Topology weight for conscious→sensory > 0
    """
    conscious_output = state.get("conscious_output")
    re_examine = (
        conscious_output is not None
        and conscious_output.get("re_examine", False)
    )

    feedback = state.get("feedback") or _default_feedback()
    re_examine_count = feedback.get("re_examine_count", 0)

    if re_examine and re_examine_count < 1 and _get_topology_weight("conscious", "sensory") > 0:
        return "re_examine_gate"

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

    Phase 3 routing with feedback loops:
    - Signal domain (sensory, immune, subconscious) processes every cycle
    - Conditional escalation to conscious (subconscious decides)
    - Conscious may request re-examination → routes back to sensory (max 1)
    - Motor produces output
    - Motor may fail repair → routes back to conscious for retry (max 1)

    Sleep and genetic are not actively routed (called outside the graph).

    Returns:
        A compiled LangGraph that can be invoked with a GraphState.
    """
    graph = StateGraph(GraphState)

    # System nodes.
    graph.add_node("sensory", _make_node(sensory))
    graph.add_node("immune", _make_node(immune))
    graph.add_node("subconscious", _make_node(subconscious))
    graph.add_node("conscious", _make_node(conscious))
    graph.add_node("motor", _make_node(motor))

    # Feedback gate nodes (increment counters at routing boundaries).
    graph.add_node("retry_gate", _increment_motor_retry)
    graph.add_node("re_examine_gate", _increment_re_examine)

    # Signal domain: always runs in order.
    graph.set_entry_point("sensory")
    graph.add_edge("sensory", "immune")
    graph.add_edge("immune", "subconscious")

    # Escalation gate: subconscious decides conscious involvement.
    graph.add_conditional_edges(
        "subconscious",
        _should_escalate,
        {"conscious": "conscious", "motor": "motor"},
    )

    # After conscious: re-examine or proceed to motor.
    graph.add_conditional_edges(
        "conscious",
        _after_conscious,
        {"re_examine_gate": "re_examine_gate", "motor": "motor"},
    )

    # Re-examination loop: gate → sensory (re-runs signal domain).
    graph.add_edge("re_examine_gate", "sensory")

    # After motor: retry via conscious or finish.
    graph.add_conditional_edges(
        "motor",
        _after_motor,
        {"retry_gate": "retry_gate", "__end__": END},
    )

    # Retry loop: gate → conscious (re-deliberation).
    graph.add_edge("retry_gate", "conscious")

    return graph.compile()
