import uuid

import streamlit as st

from api import execute_code, get_hint , review_code , analyze_complexity


st.set_page_config(
    page_title="DSA Sensei",
    page_icon="🧠",
    layout="wide",
)

st.title("🧠 DSA Sensei")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# -------------------------------------------------
# Inputs
# -------------------------------------------------

problem = st.text_area(
    "Problem Statement",
    height=220,
)

code = st.text_area(
    "Your Code",
    height=350,
)



col1, col2, col3, col4 = st.columns(4)

with col1:

    if st.button("💡 Get Hint"):

        if not problem.strip():

            st.warning("Please enter the problem statement.")

        else:

            with st.spinner("Generating Hint..."):

                response = get_hint(
                    session_id=st.session_state.session_id,
                    problem_statement=problem,
                )

            st.subheader("💡 Hint")

            st.success(response["response"])

 
            st.caption(f"Hint Level: {response['hint_level']}")

with col2:

    if st.button("▶ Run Code"):

        if not problem.strip():

            st.warning("Please enter the problem statement.")

        elif not code.strip():

            st.warning("Please enter your code.")

        else:

            with st.spinner("Running your code..."):

                response = execute_code(
                    session_id=st.session_state.session_id,
                    problem_statement=problem,
                    user_code=code,
                )

            st.subheader("Execution Result")

            st.json(response)

with col3:

    if st.button("📝 Review"):

        if not problem.strip():
            st.warning("Please enter the problem statement.")

        elif not code.strip():
            st.warning("Please enter your code.")

        else:

            with st.spinner("Reviewing your solution..."):

                response = review_code(
                    session_id=st.session_state.session_id,
                    problem_statement=problem,
                    user_code=code,
                )

            review = response["review"]

            st.subheader("📝 Code Review")

            st.success(f"⭐ Score: {review['score']}")

            st.markdown("### 🧠 Logic")
            st.write(review["logic"])

            st.markdown("### 🐞 Bugs")
            for bug in review["bugs"]:
                st.write(f"- {bug}")

            st.markdown("### ⚠ Edge Cases")
            for edge in review["edge_cases"]:
                st.write(f"- {edge}")

            st.markdown("### 📖 Readability")
            st.write(review["readability"])

            st.markdown("### 🚀 Optimization")
            for item in review["optimization"]:
                st.write(f"- {item}")

with col4:

    if st.button("📈 Complexity"):

        if not problem.strip():
            st.warning("Please enter the problem statement.")

        elif not code.strip():
            st.warning("Please enter your code.")

        else:

            with st.spinner("Analyzing complexity..."):

                response = analyze_complexity(
                    session_id=st.session_state.session_id,
                    problem_statement=problem,
                    user_code=code,
                )

            complexity = response["complexity"]

            st.subheader("📈 Complexity Analysis")

            st.metric(
                "Time Complexity",
                complexity["time_complexity"],
            )

            st.metric(
                "Space Complexity",
                complexity["space_complexity"],
            )

            if complexity["optimal"]:
                st.success("✅ This solution is asymptotically optimal.")
            else:
                st.warning("⚠ A better complexity is possible.")

            st.markdown("### 📚 Explanation")
            st.write(complexity["explanation"])

            st.markdown("### 🚀 Better Approach")
            st.write(complexity["better_approach"])