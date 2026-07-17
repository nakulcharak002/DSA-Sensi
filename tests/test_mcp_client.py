import asyncio

from app.mcp.client import MCPClient


cpp_code = r"""
#include <iostream>
using namespace std;

int main() {
    cout << "Hello DSA Sensei";
}
"""


async def main():
    client = MCPClient()

    result = await client.execute_cpp(
        code=cpp_code,
        stdin=""
    )

    print(result)


asyncio.run(main())