import uuid
import streamlit as st
from streamlit_ace import st_ace

from api import (
    get_hint,
    review_code,
    execute_code,
    analyze_complexity,
    chat,
    create_session,
    get_sessions,
    get_session,
    delete_session,
)
from auth_page import render_auth_page
from styles import get_custom_css


def format_ai_result(result) -> str:
    """
    Convert a chat response (str or structured dict from
    review/complexity/execute) into a single markdown string
    suitable for chat history display.
    """
    if isinstance(result, dict):

        if "score" in result:
            lines = [f"**⭐ Score:** {result.get('score', 'N/A')}"]
            lines.append(f"\n**🧠 Logic**\n{result.get('logic', '')}")
            bugs = result.get("bugs", [])
            lines.append("\n**🐞 Bugs**")
            lines.append(
                "\n".join(f"- {b}" for b in bugs) if bugs else "No bugs found."
            )
            edges = result.get("edge_cases", [])
            if edges:
                lines.append("\n**⚠ Edge Cases**")
                lines.append("\n".join(f"- {e}" for e in edges))
            if result.get("readability"):
                lines.append(f"\n**📖 Readability**\n{result.get('readability')}")
            opt = result.get("optimization", [])
            if opt:
                lines.append("\n**🚀 Optimization**")
                lines.append("\n".join(f"- {o}" for o in opt))
            return "\n".join(lines)

        if "time_complexity" in result:
            lines = [
                f"**Time Complexity:** {result.get('time_complexity', 'N/A')}",
                f"**Space Complexity:** {result.get('space_complexity', 'N/A')}",
            ]
            lines.append(
                "✅ Optimal Solution"
                if result.get("optimal")
                else "⚠ Better Solution Possible"
            )
            if result.get("explanation"):
                lines.append(f"\n**📚 Explanation**\n{result.get('explanation')}")
            if result.get("better_approach"):
                lines.append(f"\n**🚀 Better Approach**\n{result.get('better_approach')}")
            return "\n".join(lines)

        if "compiled" in result:
            lines = [
                "✅ Code Compiled Successfully"
                if result.get("compiled")
                else "❌ Compilation Failed"
            ]
            lines.append(f"\n**Output**\n```\n{result.get('stdout', '')}\n```")
            if result.get("stderr"):
                lines.append(f"\n**Errors**\n```\n{result.get('stderr')}\n```")
            lines.append(f"\nExit Code: {result.get('exit_code', 0)}")
            return "\n".join(lines)

        return f"```json\n{result}\n```"

    return str(result)


st.set_page_config(
    page_title="DSA Sensei",
    page_icon="🧠",
    layout="wide",
)

# ---------------- Auth Gate ----------------

if "access_token" not in st.session_state:
    render_auth_page()
    st.stop()

# ---------------- CSS ----------------

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ---------------- Session ----------------

if "session_id" not in st.session_state:
    session_data = create_session()
    if not session_data.get("success", True):
        st.error(f"Failed to create session: {session_data.get('message')}")
        st.stop()
    st.session_state.session_id = session_data["session_id"]

if "messages" not in st.session_state:
    st.session_state.messages = []

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
        session_data = create_session()
        if not session_data.get("success", True):
            st.error(f"Failed to create session: {session_data.get('message')}")
        else:
            st.session_state.session_id = session_data["session_id"]
            st.session_state.messages = []
            st.session_state.loaded_problem = ""
            st.session_state.loaded_code = ""
            st.rerun()

    st.divider()

    st.markdown("### 🕘 History")

    sessions_resp = get_sessions()

    if not sessions_resp.get("success", True):
        st.caption("Couldn't load history.")
    else:
        past_sessions = sessions_resp["data"]

        if not past_sessions:
            st.caption("No past sessions yet.")
        else:
            for s in past_sessions:
                label = (s.get("problem_statement") or "Untitled")[:30]
                is_current = s["session_id"] == st.session_state.session_id

                hcol1, hcol2 = st.columns([4, 1])

                with hcol1:
                    button_label = f"{'▶ ' if is_current else ''}{label}"
                    if st.button(button_label, key=f"load_{s['session_id']}"):
                        detail_resp = get_session(s["session_id"])
                        if detail_resp.get("success", True):
                            detail = detail_resp["data"]
                            st.session_state.session_id = detail["session_id"]
                            st.session_state.loaded_problem = detail.get("problem_statement") or ""
                            st.session_state.loaded_code = detail.get("user_code") or ""
                            st.session_state.messages = [
                                {"role": m["role"], "content": m["content"]}
                                for m in detail.get("messages", [])
                            ]
                            st.rerun()
                        else:
                            st.error(f"Couldn't load session: {detail_resp.get('message')}")

                with hcol2:
                    if st.button("🗑", key=f"del_{s['session_id']}"):
                        del_resp = delete_session(s["session_id"])
                        if del_resp.get("success", True):
                            if s["session_id"] == st.session_state.session_id:
                                st.session_state.pop("session_id", None)
                                st.session_state.messages = []
                            st.rerun()
                        else:
                            st.error(f"Couldn't delete session: {del_resp.get('message')}")

    st.divider()

    st.markdown("### 🚀 Features")

    st.success("🤖 Supervisor")
    st.success("💡 Hint Agent")
    st.success("📝 Review Agent")
    st.success("▶ Execution Agent")
    st.success("📈 Complexity Agent")
    st.success("📚 RAG Enabled")

    st.divider()

    st.markdown("### Account")

    if st.button("🚪 Logout"):
        for key in ("access_token", "user_id", "messages", "session_id", "loaded_problem", "loaded_code"):
            st.session_state.pop(key, None)
        st.rerun()

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
        value=st.session_state.get("loaded_problem", ""),
        height=220,
        placeholder="Paste the LeetCode / Codeforces problem here...",
    )

    st.subheader("💻 Your Code")

    code = st_ace(
        value=st.session_state.get("loaded_code", ""),
        language="c_cpp",
        theme="monokai",
        height=450,
        auto_update=True,
        font_size=15,
        key=f"cpp_editor_{st.session_state.session_id}",
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

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

message = st.chat_input("Ask DSA Sensei...")

if message and message.strip():

    st.session_state.messages.append({"role": "user", "content": message})

    with st.spinner("Thinking..."):

        response = chat(
            session_id=st.session_state.session_id,
            message=message,
            problem_statement=problem,
            user_code=code,
        )

    if not response.get("success", True):
        reply_text = f"⚠️ Request failed: {response.get('message', 'Unknown error')}"
    else:
        reply_text = format_ai_result(response["response"])

    st.session_state.messages.append({"role": "assistant", "content": reply_text})

    st.rerun()

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

            if not response.get("success", True):
                st.error(f"Request failed: {response.get('message', 'Unknown error')}")
            else:
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

            if not response.get("success", True):
                st.error(f"Request failed: {response.get('message', 'Unknown error')}")
            else:
                review = response["review"]

                st.divider()

                st.subheader("📝 Code Review")

                st.success(f"⭐ Score : {review.get('score', 'N/A')}")

                with st.expander("🧠 Logic", expanded=True):
                    st.write(review.get("logic", ""))

                with st.expander("🐞 Bugs", expanded=True):
                    bugs = review.get("bugs", [])
                    if bugs:
                        for bug in bugs:
                            st.write(f"• {bug}")
                    else:
                        st.success("No bugs found.")

                with st.expander("⚠ Edge Cases"):
                    for edge in review.get("edge_cases", []):
                        st.write(f"• {edge}")

                with st.expander("📖 Readability"):
                    st.write(review.get("readability", ""))

                with st.expander("🚀 Optimization"):
                    for item in review.get("optimization", []):
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

            if not response.get("success", True):
                st.error(f"Request failed: {response.get('message', 'Unknown error')}")
            else:
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

            if not response.get("success", True):
                st.error(f"Request failed: {response.get('message', 'Unknown error')}")
            else:
                complexity = response["complexity"]

                st.divider()

                st.subheader("📈 Complexity Analysis")

                if not complexity:
                    st.warning("No complexity data returned.")
                    st.json(response)
                else:
                    c1, c2 = st.columns(2)

                    with c1:
                        st.metric(
                            "Time Complexity",
                            complexity.get("time_complexity", "N/A"),
                        )

                    with c2:
                        st.metric(
                            "Space Complexity",
                            complexity.get("space_complexity", "N/A"),
                        )

                    if complexity.get("optimal"):

                        st.success("✅ Optimal Solution")

                    else:

                        st.warning("⚠ Better Solution Possible")

                    with st.expander("📚 Explanation", expanded=True):
                        st.write(complexity.get("explanation", ""))

                    with st.expander("🚀 Better Approach"):
                        st.write(complexity.get("better_approach", ""))