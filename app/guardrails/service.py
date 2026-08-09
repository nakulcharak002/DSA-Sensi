import logfire

from app.guardrails.initializer import get_rails


def guard(message: str) -> tuple[bool, str | None]:
    """
    Run the user message through NeMo Guardrails.

    Returns:
        (True, response)  -> Block the request.
        (False, None)     -> Continue to LangGraph.
    """

    rails = get_rails()

    with logfire.span("🛡️ Guardrails Check"):

        result = rails.generate(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ]
        )

        print("\n========== GUARDRAIL RESPONSE ==========")
        print(result)
        print("========================================\n")

        # NeMo normally returns:
        # {"role":"assistant","content":"..."}
        if isinstance(result, dict):

            content = result.get("content", "")

            # If NeMo produced a refusal instead of simply
            # forwarding the user message, treat it as blocked.
            if content:
                logfire.info("🚫 Guardrail blocked request.")
                return True, content

            return False, None

        # Fallback
        return False, None