from app.agents.nodes.execution_node import execution_node

state = {
    "user_code": r"""
#include <iostream>
using namespace std;

int main() {
    cout << "Execution Node Works!";
    return 0;
}
""",
    "problem_statement": "",
}

result = execution_node(state)

print(result["execution_result"])