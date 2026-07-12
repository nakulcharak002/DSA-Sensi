from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.nodes.supervisor import supervisor_node
from app.agents.nodes.hint_node import hint_node
from app.agents.nodes.review_node import review_node


# Create workflow
builder = StateGraph(AgentState)

# --------------------------------------------------
# Register Nodes
# --------------------------------------------------

builder.add_node("supervisor", supervisor_node)
builder.add_node("hint", hint_node)
builder.add_node("review", review_node)

# --------------------------------------------------
# Entry Point
# --------------------------------------------------

builder.add_edge(START, "supervisor")


# --------------------------------------------------
# Conditional Routing
# --------------------------------------------------

def route(state: AgentState):
    """
    Reads the decision made by the supervisor and
    tells LangGraph which node to execute next.
    """
    return state["next_node"]


builder.add_conditional_edges(
    "supervisor",
    route,
    {
        "hint": "hint",
    },
)

# --------------------------------------------------
# Exit
# --------------------------------------------------

builder.add_edge("hint", END)


graph = builder.compile()