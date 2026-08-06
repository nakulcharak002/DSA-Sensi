import json
import re

import logfire

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState
from app.gateway import get_langchain_llm
from app.prompts.review_prompt import REVIEW_PROMPT
from app.prompts.review_chat_prompt import REVIEW_CHAT_PROMPT
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

    latest_user_message = state["messages"][-1]["content"]

    conversation = "\n".join(
        f'{msg["role"].capitalize()}: {msg["content"]}'
        for msg in state.get("conversation_history", [])[-10:]
    )

    followups = [
        "why",
        "explain",
        "elaborate",
        "what do you mean",
        "tell me more",
        "how",
        "can you explain",
        "can you elaborate",
        "more",
        "details",
        "optimization",
        "bug",
        "logic",
        "readability",
        "edge case",
    ]

    latest_lower = latest_user_message.lower()

    is_followup = (
        state.get("last_agent") == "review"
        and any(phrase in latest_lower for phrase in followups)
    )

    system_prompt = REVIEW_CHAT_PROMPT if is_followup else REVIEW_PROMPT

    with logfire.span("📝 Review Agent"):

        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(
                    content=f"""
Problem Statement:
{problem}

User Code:
{user_code}

Latest User Message:
{latest_user_message}

Conversation History:
{conversation}
"""
                ),
            ]
        )

        print("\n========== REVIEW RAW RESPONSE ==========")
        print(response.content)
        print("=========================================\n")

        if is_followup:

            logfire.info("Review follow-up answered.")

            state["response"] = response.content

            return state

        data = extract_json(response.content)

        review = ReviewResponse.model_validate(data)

        logfire.info("Review generated successfully.")

    state["review"] = review.model_dump()

    return state