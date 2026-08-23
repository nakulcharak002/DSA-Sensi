import requests
import streamlit as st
from constants import API_BASE_URL


def _register(email: str, password: str):
    resp = requests.post(
        f"{API_BASE_URL}/auth/register",
        json={"email": email, "password": password},
    )
    resp.raise_for_status()
    return resp.json()


def _login(email: str, password: str):
    resp = requests.post(
        f"{API_BASE_URL}/auth/login",
        json={"email": email, "password": password},
    )
    resp.raise_for_status()
    return resp.json()


def render_auth_page():
    st.title("🧠 DSA Sensei")
    st.caption("Sign in to continue")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login")

        if submitted:
            if not email or not password:
                st.warning("Enter both email and password.")
            else:
                try:
                    data = _login(email, password)
                    st.session_state.access_token = data["access_token"]
                    st.session_state.user_id = data["user_id"]
                    st.rerun()
                except requests.HTTPError as e:
                    detail = e.response.json().get("detail", "Login failed")
                    st.error(detail)
                except requests.ConnectionError:
                    st.error("Can't reach the backend. Is the API running?")

    with tab_register:
        with st.form("register_form"):
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm = st.text_input("Confirm Password", type="password", key="register_confirm")
            submitted = st.form_submit_button("Create Account")

        if submitted:
            if not email or not password:
                st.warning("Enter both email and password.")
            elif password != confirm:
                st.warning("Passwords don't match.")
            else:
                try:
                    _register(email, password)
                    st.success("Account created. Switch to the Login tab to sign in.")
                except requests.HTTPError as e:
                    detail = e.response.json().get("detail", "Registration failed")
                    st.error(detail)
                except requests.ConnectionError:
                    st.error("Can't reach the backend. Is the API running?")
