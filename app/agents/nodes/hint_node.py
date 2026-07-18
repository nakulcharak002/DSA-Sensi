from app.gateway import get_langchain_llm
from app.config import settings
from app.agents.state import AgentState
from langchain_core.messages import SystemMessage, HumanMessage

# Ensure the API key exists
settings.require("GROQ_API_KEY")

llm = get_langchain_llm(feature="hint")

HINT_TIERS = [
    {
        "name": "nudge",
        "system_prompt": (
            "You are a DSA tutor. Give ONE short conceptual nudge "
            "(1-2 sentences). Do NOT name the algorithm or pattern. "
            "Do NOT mention data structures explicitly. Just make the "
            "user think about the problem differently."
        ),
    },
    {
        "name": "approach",
        "system_prompt": (
            "You are a DSA tutor. Now name the general APPROACH or "
            "PATTERN (e.g. 'this is a sliding window problem') and "
            "explain WHY it applies, in 2-3 sentences. "
            "Do NOT give code. Do NOT give pseudocode."
        ),
    },
    {
        "name": "pseudocode",
        "system_prompt": (
            "You are a DSA tutor. Give step-by-step PSEUDOCODE only. "
            "No real code in any language. Keep it high level so the "
            "user still has to translate it into code."
        ),
    },
    {
        "name": "solution",
        "system_prompt": (
            "You are a DSA tutor. The user has asked for the full "
            "solution after trying earlier hints. Give clean, working "
            "code with a brief complexity analysis."
        ),
    },
]


def get_hint(problem_statement: str, tier_index: int) -> str:
    tier = HINT_TIERS[tier_index]

    response = llm.invoke(
        [
            SystemMessage(content=tier["system_prompt"]),
            HumanMessage(content=f"Problem:\n{problem_statement}")
        ]
    )

    return response.content


def hint_node(state: AgentState) -> AgentState:
    """
    LangGraph Hint Node.

    Input:
        AgentState

    Output:
        Updated AgentState with AI-generated hint.
    """

    hint = get_hint(
        problem_statement=state["problem_statement"],
        tier_index=state["hint_level"],
    )

    state["response"] = hint

    return state