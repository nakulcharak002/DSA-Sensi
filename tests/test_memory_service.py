from app.services.retrieval.memory_service import save_solved_problem

problem = """
Given an array of integers nums and an integer target,
return the indices of the two numbers such that they add up to target.
"""

solution = """
class Solution {
public:
    vector<int> twoSum(vector<int>& nums, int target) {

        unordered_map<int,int> mp;

        for(int i=0;i<nums.size();i++){

            int need = target - nums[i];

            if(mp.count(need))
                return {mp[need], i};

            mp[nums[i]] = i;
        }

        return {};
    }
};
"""

problem_id = save_solved_problem(
    problem=problem,
    solution=solution,
    language="C++",
    hint_level=1,
    attempts=2,
    review_score=9,
)

print("\nSaved Problem ID:")
print(problem_id)