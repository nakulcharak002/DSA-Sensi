from app.agents.state import AgentState
from app.mcp.client import MCPClient
import asyncio


def execution_node(state: AgentState) -> AgentState:
    """
    Executes the user's C++ code through the MCP server.
    """

    client = MCPClient()

    result = asyncio.run(
        client.execute_cpp(
            code=state["user_code"],
            stdin=""
        )
    )

    state["execution_result"] = result

    return state