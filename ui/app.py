import uuid
import streamlit as st
from streamlit_ace import st_ace

from api import (
    get_hint,
    review_code,
    execute_code,
    analyze_complexity,
    chat,
)

st.set_page_config(
    page_title="DSA Sensei",
    page_icon="🧠",
    layout="wide",
)

# ---------------- CSS ----------------

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:1rem;
}

.stButton>button{
    width:100%;
    height:45px;
    border-radius:10px;
    font-weight:600;
}

textarea{
    border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Session ----------------

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# ---------------- Sidebar ----------------

with st.sidebar:

    st.title("🧠 DSA Sensei")

    st.success("🟢 Supervisor Active")
    st.success("🟢 RAG Enabled")
    st.success("🟢 Memory Enabled")

    st.divider()

    st.markdown("### Session")

    st.code(st.session_state.session_id[:8])

    if st.button("🔄 New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

    st.divider()

    st.markdown("### 🚀 Features")

    st.success("🤖 Supervisor")
    st.success("💡 Hint Agent")
    st.success("📝 Review Agent")
    st.success("▶ Execution Agent")
    st.success("📈 Complexity Agent")
    st.success("📚 RAG Enabled")

# ---------------- Header ----------------

st.title("🧠 DSA Sensei")

st.caption(
    "AI Powered DSA Mentor • Supervisor Agent • RAG • LangGraph"
)

# ---------------- Layout ----------------

left, right = st.columns([2, 1])

with left:

    problem = st.text_area(
        "📄 Problem Statement",
        height=220,
        placeholder="Paste the LeetCode / Codeforces problem here...",
    )

    st.subheader("💻 Your Code")

    code = st_ace(
        language="c_cpp",
        theme="monokai",
        height=450,
        auto_update=True,
        font_size=15,
        key="cpp_editor",
    )

with right:

    st.markdown("### 🤖 AI Mentor")

    st.info(
        """
Try asking:

- I'm stuck

- Review my code

- Run this code

- Analyze complexity
"""
    )

# ---------- Quick Chat ----------

st.divider()

st.subheader("💬 Ask DSA Sensei")

message = st.chat_input("Ask DSA Sensei...")

if message and message.strip():

    with st.spinner("Thinking..."):

        response = chat(
            session_id=st.session_state.session_id,
            message=message,
            problem_statement=problem,
            user_code=code,
        )

    st.subheader("🤖 AI Response")

    result = response["response"]

    if isinstance(result, dict):

        # Review
        if "score" in result:
            st.success(f"⭐ Score : {result.get('score', 'N/A')}")

            with st.expander("🧠 Logic", expanded=True):
                st.write(result.get("logic", ""))

            with st.expander("🐞 Bugs", expanded=True):
                bugs = result.get("bugs", [])
                if bugs:
                    for bug in bugs:
                        st.write(f"• {bug}")
                else:
                    st.success("No bugs found.")

            with st.expander("⚠ Edge Cases"):
                for edge in result.get("edge_cases", []):
                    st.write(f"• {edge}")

            with st.expander("📖 Readability"):
                st.write(result.get("readability", ""))

            with st.expander("🚀 Optimization"):
                for item in result.get("optimization", []):
                    st.write(f"• {item}")

        # Complexity
        elif "time_complexity" in result:
            c1, c2 = st.columns(2)

            with c1:
                st.metric("Time Complexity", result.get("time_complexity", "N/A"))

            with c2:
                st.metric("Space Complexity", result.get("space_complexity", "N/A"))

            if result.get("optimal"):
                st.success("✅ Optimal Solution")
            else:
                st.warning("⚠ Better Solution Possible")

            with st.expander("📚 Explanation", expanded=True):
                st.write(result.get("explanation", ""))

            with st.expander("🚀 Better Approach"):
                st.write(result.get("better_approach", ""))

        # Execute
        elif "compiled" in result:
            if result.get("compiled"):
                st.success("✅ Code Compiled Successfully")
            else:
                st.error("❌ Compilation Failed")

            st.markdown("### Output")
            st.code(result.get("stdout", ""))

            if result.get("stderr"):
                st.markdown("### Errors")
                st.code(result.get("stderr"))

            st.metric("Exit Code", result.get("exit_code", 0))

        else:
            st.json(result)

    else:
        st.success(result)

st.divider()

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

            st.divider()

            st.subheader("💡 Hint")

            st.success(response["response"])

            st.caption(f"Hint Level : {response['hint_level']}")

# ----------------------------------------------------

with col2:

    if st.button("📝 Review"):

        if not problem.strip():

            st.warning("Please enter the problem statement.")

        elif not code.strip():

            st.warning("Please enter your code.")

        else:

            with st.spinner("Reviewing code..."):

                response = review_code(
                    session_id=st.session_state.session_id,
                    problem_statement=problem,
                    user_code=code,
                )

            review = response["review"]

            st.divider()

            st.subheader("📝 Code Review")

            st.success(f"⭐ Score : {review['score']}")

            with st.expander("🧠 Logic", expanded=True):
                st.write(review["logic"])

            with st.expander("🐞 Bugs", expanded=True):
                for bug in review["bugs"]:
                    st.write(f"• {bug}")

            with st.expander("⚠ Edge Cases"):
                for edge in review["edge_cases"]:
                    st.write(f"• {edge}")

            with st.expander("📖 Readability"):
                st.write(review["readability"])

            with st.expander("🚀 Optimization"):
                for item in review["optimization"]:
                    st.write(f"• {item}")

# ----------------------------------------------------

with col3:

    if st.button("▶ Execute"):

        if not problem.strip():

            st.warning("Please enter the problem statement.")

        elif not code.strip():

            st.warning("Please enter your code.")

        else:

            with st.spinner("Executing Code..."):

                response = execute_code(
                    session_id=st.session_state.session_id,
                    problem_statement=problem,
                    user_code=code,
                )

            st.divider()

            st.subheader("▶ Execution Result")

            if response["compiled"]:

                st.success("✅ Code Compiled Successfully")

            else:

                st.error("❌ Compilation Failed")

            st.markdown("### Output")

            st.code(response["stdout"])

            if response["stderr"]:

                st.markdown("### Errors")

                st.code(response["stderr"])

            st.metric(
                "Exit Code",
                response["exit_code"],
            )

# ----------------------------------------------------

with col4:

    if st.button("📈 Complexity"):

        if not problem.strip():

            st.warning("Please enter the problem statement.")

        elif not code.strip():

            st.warning("Please enter your code.")

        else:

            with st.spinner("Analyzing Complexity..."):

                response = analyze_complexity(
                    session_id=st.session_state.session_id,
                    problem_statement=problem,
                    user_code=code,
                )

            complexity = response["complexity"]

            st.divider()

            st.subheader("📈 Complexity Analysis")

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "Time Complexity",
                    complexity["time_complexity"],
                )

            with c2:
                st.metric(
                    "Space Complexity",
                    complexity["space_complexity"],
                )

            if complexity["optimal"]:

                st.success("✅ Optimal Solution")

            else:

                st.warning("⚠ Better Solution Possible")

            with st.expander("📚 Explanation", expanded=True):
                st.write(complexity["explanation"])

            with st.expander("🚀 Better Approach"):
                st.write(complexity["better_approach"])