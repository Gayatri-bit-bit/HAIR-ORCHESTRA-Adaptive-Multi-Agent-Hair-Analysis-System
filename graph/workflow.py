from langgraph.graph import StateGraph, END

from graph.state import HairState
from agents.planner import planner_agent
from agents.vision import vision_agent
from agents.context import context_agent
from agents.knowledge import knowledge_agent
from agents.decision import decision_agent
from agents.review import review_agent


def build_workflow():
    graph = StateGraph(HairState)

    graph.add_node("planner", planner_agent)
    graph.add_node("vision", vision_agent)
    graph.add_node("context", context_agent)
    graph.add_node("knowledge", knowledge_agent)
    graph.add_node("decision", decision_agent)
    graph.add_node("review", review_agent)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "vision")
    graph.add_edge("vision", "context")
    graph.add_edge("context", "knowledge")
    graph.add_edge("knowledge", "decision")

    def route_after_decision(state):
        if state.get("decision", {}).get("reliable", True):
            return END
        return "review"

    graph.add_conditional_edges("decision", route_after_decision)
    graph.add_edge("review", END)

    return graph.compile()