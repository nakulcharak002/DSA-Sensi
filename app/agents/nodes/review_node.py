import json
import re

import logfire

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState
from app.gateway import get_langchain_llm
from app.prompts.review_prompt import REVIEW_PROMPT
from app.schemas.review import ReviewResponse

llm = get_langchain_llm(feature="review")


def extract_json(text: str) -> dict:
    """
    Extract JSON even if wrapped inside markdown.
    """

    text = text.strip()

    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found.")

    return json.loads(text[start:end + 1])


def review_node(state: AgentState) -> AgentState:

    problem = state["problem_statement"]
    user_code = state["user_code"]

    with logfire.span("📝 Review Agent"):

        response = llm.invoke(
            [
                SystemMessage(content=REVIEW_PROMPT),
                HumanMessage(
                    content=f"""
Problem Statement:
{problem}

User Code:
{user_code}
"""
                ),
            ]
        )

        print("\n========== REVIEW RAW RESPONSE ==========")
        print(response.content)
        print("=========================================\n")

        data = extract_json(response.content)

        review = ReviewResponse.model_validate(data)

        logfire.info("Review generated successfully.")

    state["review"] = review.model_dump()

    return state