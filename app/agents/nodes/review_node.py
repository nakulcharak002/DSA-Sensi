from app.agents.state import AgentState
from app.prompts.review_prompt import REVIEW_PROMPT
from app.schemas.review import ReviewResponse
from app.gateway import get_langchain_llm

import logfire

llm = get_langchain_llm(feature="review")


def review_node(state: AgentState) -> AgentState:
    """
    Review Node

    Responsibilities:
    -----------------
    • Analyze the user's submitted code.
    • Review correctness.
    • Review bugs.
    • Review edge cases.
    • Analyze time & space complexity.
    • Never reveal the optimal solution.
    """

    problem = state["problem_statement"]
    user_code = state["user_code"]

    prompt = f"""
{REVIEW_PROMPT}

Problem Statement:
------------------
{problem}

User Code:
----------
{user_code}
"""

    with logfire.span("📝 Review Agent"):

        review: ReviewResponse = (
            llm.with_structured_output(ReviewResponse)
            .invoke(prompt)
        )

        logfire.info("Review generated successfully.")

    state["review"] = review.model_dump()

    return state