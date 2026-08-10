import logfire

from nemoguardrails.rails.llm.options import GenerationOptions

from app.guardrails.initializer import get_rails

REFUSAL_MESSAGE = "I'm sorry, I can't respond to that."


def guard(message: str) -> tuple[bool, str | None]:
    """
    Run the user message through NeMo Guardrails.

    Returns:
        (True, response)  -> Block the request.
        (False, None)     -> Continue to LangGraph.
    """

    rails = get_rails()

    with logfire.span("🛡️ Guardrails Check"):

        options = GenerationOptions(
            log={
                "activated_rails": True,
                "llm_calls": True,
            }
        )

        response = rails.generate(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            options=options,
        )

        result = response.response[0] if response.response else {}

        print("\n========== GUARDRAIL RESPONSE ==========")
        print(result)
        print("---------- RAW LLM SELF-CHECK CALLS ----------")
        if response.log and response.log.llm_calls:
            for call in response.log.llm_calls:
                print("TASK:", getattr(call, "task", None))
                print("PROMPT:", getattr(call, "prompt", None))
                print("COMPLETION:", getattr(call, "completion", None))
                print("-" * 40)
        print("========================================\n")

        if isinstance(result, dict):

            content = result.get("content", "")

            if content.strip() == REFUSAL_MESSAGE:
                logfire.info("🚫 Guardrail blocked request.")
                return True, content

            return False, None

        return False, None