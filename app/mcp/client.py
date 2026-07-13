from mcp import ClientSession
import json
from mcp.client.stdio import stdio_client, StdioServerParameters


class MCPClient:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command="python",
            args=["-m", "app.mcp.server"],
        )

    async def execute_cpp(self, code: str, stdin: str = ""):

        async with stdio_client(self.server_params) as (read, write):

            async with ClientSession(read, write) as session:

                await session.initialize()

                response = await session.call_tool(
                    "execute_cpp",
                    {
                        "code": code,
                        "stdin": stdin,
                    },
                )

                return json.loads(response.content[0].text)