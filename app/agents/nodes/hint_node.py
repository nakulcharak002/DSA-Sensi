from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.state import AgentState
from app.config import settings
from app.gateway import get_langchain_llm
from app.services.retrieval.retriever import retrieve_similar_problems

# Ensure API key exists
settings.require("GROQ_API_KEY")

llm = get_langchain_llm(feature="hint")


HINT_TIERS = [
    {
        "name": "nudge",
        "system_prompt": (
            "You are a DSA tutor. Give ONE short conceptual nudge "
            "(1-2 sentences). Do NOT name the algorithm or pattern. "
            "Do NOT mention data structures explicitly. "
            "Make the user think differently."
        ),
    },
    {
        "name": "approach",
        "system_prompt": (
            "You are a DSA tutor. Name the general approach or pattern "
            "and explain WHY it applies. "
            "Do NOT give code or pseudocode."
        ),
    },
    {
        "name": "pseudocode",
        "system_prompt": (
            "You are a DSA tutor. Give step-by-step pseudocode only. "
            "Do NOT provide real code."
        ),
    },
    {
        "name": "solution",
        "system_prompt": (
            "You are a DSA tutor. The user has already tried multiple "
            "hints. Provide the complete solution with complexity analysis."
        ),
    },
]


def build_retrieval_context(
    retrieved_problems: list[dict],
) -> str:
    """
    Convert retrieved Qdrant results into prompt context.
    """

    if not retrieved_problems:
        return "No similar previously solved problems were found."

    context = "Previously solved similar problems:\n\n"

    for idx, problem in enumerate(retrieved_problems, start=1):

        payload = problem.get("payload", {})

        title = payload.get("title", "Unknown")
        difficulty = payload.get("difficulty", "Unknown")

        topics = payload.get("topics", [])
        topics = ", ".join(topics) if topics else "Unknown"

        context += (
            f"{idx}. {title}\n"
            f"Difficulty: {difficulty}\n"
            f"Topics: {topics}\n\n"
        )

    return context


def get_hint(
    problem_statement: str,
    tier_index: int,
    retrieved_problems: list[dict],
) -> str:
    """
    Generate a hint using retrieved similar problems.
    """

    tier_index = min(
        tier_index,
        len(HINT_TIERS) - 1,
    )

    tier = HINT_TIERS[tier_index]

    retrieval_context = build_retrieval_context(
        retrieved_problems
    )

    prompt = f"""
Current Problem:

{problem_statement}

--------------------------------------------------

{retrieval_context}

--------------------------------------------------

Use the retrieved problems ONLY as background knowledge.

Do NOT copy their solutions.

Do NOT mention the retrieved problems to the user.

Generate a hint ONLY for the current problem.

Reveal the full solution only if the current hint tier allows it.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=tier["system_prompt"],
            ),
            HumanMessage(
                content=prompt,
            ),
        ]
    )

    return response.content


def hint_node(state: AgentState) -> AgentState:
    """
    LangGraph Hint Node.
    """

    retrieved_problems = retrieve_similar_problems(
        problem_statement=state["problem_statement"],
        limit=5,
    )

    state["retrieved_problems"] = retrieved_problems

    hint = get_hint(
        problem_statement=state["problem_statement"],
        tier_index=state["hint_level"],
        retrieved_problems=retrieved_problems,
    )

    state["response"] = hint

    return state