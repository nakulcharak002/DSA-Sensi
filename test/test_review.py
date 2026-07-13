from app.agents.nodes.review_node import review_node

state = {
    "session_id": "123",
    "messages": [],
    "problem_statement": "Two Sum",
    "user_code": """
vector<int> twoSum(vector<int>& nums, int target){
    for(int i=0;i<nums.size();i++){
        for(int j=i+1;j<nums.size();j++){
            if(nums[i]+nums[j]==target)
                return {i,j};
        }
    }
}
""",
    "request_type": "review",
    "hint_level": 0,
    "response": "",
    "review": "",
    "next_node": ""
}

result = review_node(state)

print(result["review"])