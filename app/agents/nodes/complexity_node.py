import json
import re

import logfire

from langchain_core.messages import SystemMessage, HumanMessage

from app.agents.state import AgentState
from app.gateway import get_langchain_llm
from app.prompts.complexity_prompt import COMPLEXITY_PROMPT
from app.schemas.complexity import ComplexityResponse

llm = get_langchain_llm(feature="complexity")


def extract_json(text: str) -> dict:
    """
    Extract JSON even if wrapped inside markdown.
    """

    text = text.strip()

    # Remove ```json ... ```
    text = re.sub(r"^```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("No JSON object found.")

    return json.loads(text[start : end + 1])


def complexity_node(state: AgentState) -> AgentState:
    """
    Complexity Analysis Node
    """

    problem = state["problem_statement"]
    user_code = state["user_code"]

    with logfire.span("📈 Complexity Agent"):

        response = llm.invoke(
            [
                SystemMessage(content=COMPLEXITY_PROMPT),
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

        print("\n========== COMPLEXITY RAW RESPONSE ==========")
        print(response.content)
        print("=============================================\n")

        data = extract_json(response.content)

        print("\n========== PARSED JSON ==========")
        print(json.dumps(data, indent=4))
        print("=================================\n")

        # Default value if the model forgets this field
        data.setdefault(
            "better_approach",
            "The current solution is already asymptotically optimal."
        )

        complexity = ComplexityResponse.model_validate(data)

        logfire.info("Complexity analysis generated successfully.")

    state["complexity"] = complexity.model_dump()

    return state