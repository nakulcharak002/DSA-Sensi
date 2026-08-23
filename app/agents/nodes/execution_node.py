from app.agents.state import AgentState
from app.mcp.client import MCPClient
from app.services.retrieval.qdrant_service import store_solved_problem
import asyncio


def execution_node(state: AgentState) -> AgentState:
    client = MCPClient()

    result = asyncio.run(
        client.execute_cpp(
            code=state["user_code"],
            stdin="",
        )
    )

    state["execution_result"] = result

    if (
        result.get("compiled") is True
        and result.get("exit_code") == 0
        and state.get("problem_statement", "").strip()
    ):
        store_solved_problem(
            problem_statement=state["problem_statement"],
            solution_code=state["user_code"],
            execution_result=result,
            user_id=state["user_id"],
        )

    return state
