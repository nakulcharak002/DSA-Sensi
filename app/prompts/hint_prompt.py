from langchain_core.messages import HumanMessage, SystemMessage


def build_hint_prompt(
    problem_statement: str,
    retrieved_context: str,
    hint_level: int,
):
    """
    Build the prompt for the Hint Agent.
    """

    system_prompt = f"""
You are DSA Sensei, an expert Data Structures and Algorithms tutor.

Your job is to help the learner THINK, not solve the problem immediately.

You are given:
1. The current problem.
2. Similar problems retrieved from memory.

The retrieved problems are ONLY background knowledge.

Rules:

- Never reveal stored solutions.
- Never mention retrieved problems.
- Never copy retrieved text.
- Adapt hints using the learner's previous experience.
- Only answer for the CURRENT problem.

Hint Levels:

Level 0:
- Give only a conceptual nudge.
- Don't mention the algorithm.

Level 1:
- Explain the algorithm or pattern.
- Do not provide code.

Level 2:
- Give high-level pseudocode.

Level 3:
- Give the complete solution with complexity analysis.
"""

    human_prompt = f"""
Current Problem

{problem_statement}

----------------------------------------

Retrieved Context

{retrieved_context}

----------------------------------------

Current Hint Level

{hint_level}
"""

    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt),
    ]