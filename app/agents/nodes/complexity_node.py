from app.agents.state import AgentState
from app.prompts.complexity_prompt import COMPLEXITY_PROMPT
from app.schemas.complexity import ComplexityResponse
from app.gateway import get_langchain_llm

import logfire

# Initialize LLM through the gateway
llm = get_langchain_llm(feature="complexity")


def complexity_node(state: AgentState) -> AgentState:
    """
    Complexity Agent

    Responsibilities
    ----------------
    • Analyze Time Complexity
    • Analyze Space Complexity
    • Decide whether the solution is optimal
    • Explain why
    • Never reveal a better algorithm
    """

    problem = state["problem_statement"]
    user_code = state["user_code"]

    prompt = f"""
{COMPLEXITY_PROMPT}

Problem Statement:
------------------
{problem}

User Code:
----------
{user_code}
"""

    with logfire.span("📈 Complexity Agent"):

        complexity: ComplexityResponse = (
            llm.with_structured_output(ComplexityResponse)
            .invoke(prompt)
        )

        logfire.info("Complexity analysis generated successfully.")

    state["complexity"] = complexity.model_dump()

    return state