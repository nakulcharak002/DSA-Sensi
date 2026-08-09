from app.agents.state import AgentState
from app.config import settings
from app.gateway import get_langchain_llm
from app.prompts.hint_prompt import build_hint_prompt
from app.services.retrieval.retriever import retrieve_similar_problems

settings.require("GROQ_API_KEY")

llm = get_langchain_llm(feature="hint")


def build_retrieval_context(
    retrieved_problems: list[dict],
) -> str:

    if not retrieved_problems:
        return "No similar problems found."

    context = ""

    for idx, result in enumerate(retrieved_problems, start=1):

        payload = result.get("payload", {})

        context += f"""
Problem {idx}

Title:
{payload.get("title", "Unknown")}

Difficulty:
{payload.get("difficulty", "Unknown")}

Topics:
{", ".join(payload.get("topics", []))}

Summary:
{payload.get("problem", "")}

Similarity Score:
{result.get("rerank_score", result.get("score", 0))}

----------------------------------------
"""

    return context


def hint_node(state: AgentState) -> AgentState:

    # If the supervisor has already generated a response,
    # don't invoke the Hint Agent.
    if state.get("response"):
        return state

    retrieved = retrieve_similar_problems(
        problem_statement=state["problem_statement"],
        limit=5,
    )

    state["retrieved_problems"] = retrieved

    retrieval_context = build_retrieval_context(retrieved)

    latest_user_message = state["messages"][-1]["content"]

    system_prompt, human_prompt = build_hint_prompt(
        problem_statement=state["problem_statement"],
        latest_user_message=latest_user_message,
        retrieved_context=retrieval_context,
        hint_level=state["hint_level"],
    )

    messages = [
        ("system", system_prompt),
        ("human", human_prompt),
    ]

    response = llm.invoke(messages)

    state["response"] = response.content

    return state