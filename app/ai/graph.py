from langgraph.graph import END, START, StateGraph

from app.ai.state import ComplaintState
from app.ai.nodes.extraction import extraction_node
from app.ai.nodes.completeness import completeness_node
from app.ai.nodes.duplicate import duplicate_node
from app.ai.nodes.risk import risk_node


def build_complaint_graph():
    graph = StateGraph(ComplaintState)

    graph.add_node(
        "extraction",
        extraction_node,
    )

    graph.add_node(
        "completeness",
        completeness_node,
    )

    graph.add_node(
        "duplicate",
        duplicate_node,
    )

    graph.add_node(
        "risk",
        risk_node,
    )

    graph.add_edge(
        START,
        "extraction",
    )

    graph.add_edge(
        "extraction",
        "completeness",
    )

    graph.add_edge(
        "completeness",
        "duplicate",
    )

    graph.add_edge(
        "duplicate",
        "risk",
    )

    graph.add_edge(
        "risk",
        END,
    )

    return graph.compile()


complaint_graph = build_complaint_graph()