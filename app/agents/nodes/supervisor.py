from app.agents.state import AgentState
from app.prompts.supervisor_prompt import SUPERVISOR_PROMPT
from app.schemas.router import SupervisorDecision
from app.gateway import get_langchain_llm

import logfire

# Initialize the LLM through the gateway
llm = get_langchain_llm(feature="supervisor")


def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor Node

    Responsibilities:
    -----------------
    • Read the latest user message.
    • Decide which specialized agent should handle it.
    • Store the selected route in state["next_node"].
    """

    # Get the latest user message
    latest_message = state["messages"][-1]["content"]

    with logfire.span("🧠 Supervisor Decision"):

        # Ask the LLM to choose the next agent
        decision: SupervisorDecision = (
            llm.with_structured_output(SupervisorDecision)
            .invoke(
                [
                    ("system", SUPERVISOR_PROMPT),
                    ("human", latest_message),
                ]
            )
        )

        logfire.info(
            f"Supervisor selected node: {decision.next_node}"
        )

    # Update state
    state["next_node"] = decision.next_node

    return state
