from langgraph.graph import StateGraph, START, END

from app.agents.state import AgentState
from app.agents.nodes.supervisor import supervisor_node
from app.agents.nodes.hint_node import hint_node
from app.agents.nodes.review_node import review_node
from app.agents.nodes.execution_node import execution_node
from app.agents.nodes.complexity_node import complexity_node


# Create workflow
builder = StateGraph(AgentState)

# --------------------------------------------------
# Register Nodes
# --------------------------------------------------
builder.add_node("supervisor", supervisor_node)
builder.add_node("hint", hint_node)
builder.add_node("review", review_node)
builder.add_node("execution", execution_node)
builder.add_node("complexity", complexity_node)

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
        "review": "review",
        "complexity": "complexity",
        "execution": "execution",
    },
)

# --------------------------------------------------
# Exit
# --------------------------------------------------

builder.add_edge("hint", END)
builder.add_edge("execution", END)
builder.add_edge("review", END)
builder.add_edge("complexity", END)


graph = builder.compile()