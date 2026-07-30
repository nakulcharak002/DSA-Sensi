"""
Streamlit Session State Management
"""
import streamlit as st

from ui.constants import (
    DEFAULT_CODE,
    DEFAULT_INPUT,
    DEFAULT_PROBLEM,
)


def initialize_state() -> None:
    """
    Initialize all Streamlit session state variables.
    """

    defaults = {


        "problem_statement": DEFAULT_PROBLEM,

        "user_code": DEFAULT_CODE,

        "stdin": DEFAULT_INPUT,

        "compiled": False,

        "stdout": "",

        "stderr": "",

        "exit_code": None,

        "hint": "",

        "review": "",

        "complexity": "",
        "session_id": "default-session",

            
    "hint_level": 0,
    "messages": [],
    "retrieved_problems": [],
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value