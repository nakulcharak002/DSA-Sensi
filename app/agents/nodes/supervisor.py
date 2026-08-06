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

        history = state.get("conversation_history", [])
        last_agent = state.get("last_agent", "")
        hint_level = state.get("hint_level", 0)

        conversation = ""

        for msg in history[-10:]:
            conversation += (
                f'{msg["role"].capitalize()}: '
                f'{msg["content"]}\n'
            )

        human_prompt = f"""
Current User Message:
{latest_message}

Current Problem:
{state.get("problem_statement", "")}

Current Code:
{state.get("user_code", "")}

Last Agent:
{last_agent}

Current Hint Level:
{hint_level}

Recent Conversation:
{conversation}
"""

        # Ask the LLM to choose the next agent
        decision: SupervisorDecision = (
            llm.with_structured_output(SupervisorDecision)
            .invoke(
                [
                    ("system", SUPERVISOR_PROMPT),
                    ("human", human_prompt),
                ]
            )
        )

        logfire.info(
            f"Supervisor selected node: {decision.next_node}"
        )

        print("=" * 50)
        print("Message:", latest_message)
        print("Last Agent:", last_agent)
        print("Hint Level:", hint_level)
        print("Decision:", decision)
        print("=" * 50)

    # Update state
    state["next_node"] = decision.next_node

    if decision.next_node == "hint" and getattr(decision, "increase_hint", False):
        state["hint_level"] += 1

    return state