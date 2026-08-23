import json
import logfire

from app.agents.state import AgentState
from app.prompts.supervisor_prompt import SUPERVISOR_PROMPT
from app.schemas.router import SupervisorDecision
from app.gateway.llm_gateway import get_langchain_llm


llm = get_langchain_llm(feature="supervisor")


def supervisor_node(state: AgentState) -> AgentState:
    """
    Supervisor Node.

    Responsibilities:
    -----------------
    1. Read the latest user message.
    2. Read conversation history.
    3. Read the current problem and user code.
    4. Ask the LLM which specialized agent should handle
       the request.
    5. Handle hint escalation.
    6. Store the selected route in state["next_node"].
    7. Persist the last agent and hint level in state.
    """

    # =====================================================
    # 1. Get latest user message
    # =====================================================

    latest_message = state["messages"][-1]["content"]

    problem = state.get(
        "problem_statement",
        "",
    ).strip()

    # =====================================================
    # 2. Problem statement is required
    # =====================================================

    if not problem:

        state["next_node"] = "hint"

        state["response"] = (
            "Please paste the problem statement first "
            "so I can help you."
        )

        return state

    # =====================================================
    # 3. Supervisor
    # =====================================================

    with logfire.span("Supervisor Decision"):

        history = state.get(
            "conversation_history",
            [],
        )

        last_agent = state.get(
            "last_agent",
            "",
        )

        hint_level = state.get(
            "hint_level",
            0,
        )

        # =================================================
        # Build recent conversation
        # =================================================

        conversation = ""

        for msg in history[-10:]:

            conversation += (
                f'{msg["role"].capitalize()}: '
                f'{msg["content"]}\n'
            )

        # =================================================
        # Build supervisor prompt
        # =================================================

        human_prompt = f"""
Current User Message:
{latest_message}

Current Problem:
{state.get("problem_statement", "")}

Current Code:
{state.get("user_code", "")}

Last Agent:
{last_agent}

Current Hint Level:
{hint_level}

Recent Conversation:
{conversation}
"""

        # =================================================
        # 4. Ask LLM for routing decision
        # =================================================

        response = llm.invoke(
            [
                ("system", SUPERVISOR_PROMPT),
                ("human", human_prompt),
            ]
        )

        raw_content = response.content

        # =================================================
        # 5. Normalize LLM response
        # =================================================

        if isinstance(raw_content, list):

            raw_content = "".join(
                item.get("text", "")
                if isinstance(item, dict)
                else str(item)
                for item in raw_content
            )

        raw_content = str(
            raw_content
        ).strip()

        # =================================================
        # 6. Remove markdown JSON fences
        # =================================================

        if raw_content.startswith("```"):

            raw_content = raw_content.replace(
                "```json",
                "",
            )

            raw_content = raw_content.replace(
                "```",
                "",
            )

            raw_content = raw_content.strip()

        # =================================================
        # 7. Parse supervisor decision
        # =================================================

        try:

            decision_data = json.loads(
                raw_content
            )

            decision = SupervisorDecision.model_validate(
                decision_data
            )

        except Exception as error:

            logfire.error(
                f"Invalid supervisor response: "
                f"{raw_content}"
            )

            print(
                "Supervisor parsing error:",
                error,
            )

            print(
                "Raw response:",
                raw_content,
            )

            # Safe fallback
            decision = SupervisorDecision(
                next_node="hint",
                increase_hint=False,
            )

        # =================================================
        # 8. Force hint escalation
        # =================================================

        message_lower = latest_message.lower()

        follow_up_hint_phrases = [
            "another hint",
            "next hint",
            "more hint",
            "more hints",
            "further hint",
            "stronger hint",
            "still stuck",
            "don't understand",
            "do not understand",
            "explain the hint",
            "explain this hint",
            "give me another clue",
            "another clue",
        ]

        if (
            decision.next_node == "hint"
            and any(
                phrase in message_lower
                for phrase in follow_up_hint_phrases
            )
        ):

            decision.increase_hint = True

        # =================================================
        # 9. Logging
        # =================================================

        logfire.info(
            f"Supervisor selected node: "
            f"{decision.next_node}"
        )

        print("=" * 50)

        print(
            "Message:",
            latest_message,
        )

        print(
            "Last Agent:",
            last_agent,
        )

        print(
            "Current Hint Level:",
            hint_level,
        )

        print(
            "Decision:",
            decision,
        )

        print(
            "Increase Hint:",
            decision.increase_hint,
        )

        print("=" * 50)

    # =====================================================
    # 10. Update selected agent
    # =====================================================

    state["next_node"] = decision.next_node

    # Persist which agent is handling this request
    state["previous_agent"] = last_agent

    state["last_agent"] = decision.next_node

    # =====================================================
    # 11. Handle hint level
    # =====================================================

    if decision.next_node == "hint":

        # ---------------------------------------------
        # First time entering hint agent
        # ---------------------------------------------

        if last_agent != "hint":

            state["hint_level"] = state.get("hint_level", 0)

        # ---------------------------------------------
        # Continuing hint conversation
        # ---------------------------------------------

        elif decision.increase_hint:

            state["hint_level"] = (
                state.get("hint_level", 0) + 1
            )

    return state