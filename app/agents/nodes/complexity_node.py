import json
import re

import logfire

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState
from app.gateway import get_langchain_llm
from app.prompts.complexity_prompt import COMPLEXITY_PROMPT
from app.prompts.complexity_chat_prompt import COMPLEXITY_CHAT_PROMPT
from app.schemas.complexity import ComplexityResponse

llm = get_langchain_llm(feature="complexity")


def extract_json(text: str) -> dict:

    text = text.strip()

    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found.")

    return json.loads(text[start:end + 1])


def complexity_node(state: AgentState) -> AgentState:

    problem = state["problem_statement"]
    user_code = state["user_code"]

    latest_user_message = state["messages"][-1]["content"]

    conversation = "\n".join(
        f'{msg["role"].capitalize()}: {msg["content"]}'
        for msg in state.get("conversation_history", [])[-10:]
    )

    is_followup = state.get("previous_agent") == "complexity"

    system_prompt = (
        COMPLEXITY_CHAT_PROMPT
        if is_followup
        else COMPLEXITY_PROMPT
    )

    with logfire.span("📈 Complexity Agent"):

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

        print("\n========== COMPLEXITY RAW RESPONSE ==========")
        print(response.content)
        print("=============================================\n")

        if is_followup:

            logfire.info("Complexity follow-up answered.")

            state["response"] = response.content

            return state

        data = extract_json(response.content)

        data.setdefault(
            "better_approach",
            "The current solution is already asymptotically optimal."
        )

        complexity = ComplexityResponse.model_validate(data)

        logfire.info("Complexity analysis generated successfully.")

    state["complexity"] = complexity.model_dump()

    return state