import requests
import streamlit as st
from constants import API_BASE_URL


def post_request(endpoint: str, payload: dict) -> dict:
    """
    Send a POST request to the backend.
    """
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": str(e)
        }


def _auth_headers() -> dict:
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def get_request(endpoint: str) -> dict:
    try:
        response = requests.get(
            f"{API_BASE_URL}{endpoint}",
            headers=_auth_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": str(e)}


def delete_request(endpoint: str) -> dict:
    try:
        response = requests.delete(
            f"{API_BASE_URL}{endpoint}",
            headers=_auth_headers(),
            timeout=30,
        )
        response.raise_for_status()
        return {"success": True}
    except requests.exceptions.RequestException as e:
        return {"success": False, "message": str(e)}


def create_session(problem_statement: str = ""):
    payload = {
        "problem_statement": problem_statement,
    }
    return post_request("/sessions", payload)


def get_sessions():
    return get_request("/sessions")


def get_session(session_id: str):
    return get_request(f"/sessions/{session_id}")


def delete_session(session_id: str):
    return delete_request(f"/sessions/{session_id}")


def execute_code(session_id: str, problem_statement: str, user_code: str):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }
    return post_request("/execute", payload)


def get_hint(session_id: str, problem_statement: str, stuck: bool = False):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "stuck": stuck,
    }
    return post_request("/hint", payload)


def review_code(session_id: str, problem_statement: str, user_code: str):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }
    return post_request("/review", payload)


def analyze_complexity(session_id: str, problem_statement: str, user_code: str):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }
    return post_request("/complexity", payload)


def chat(session_id: str, message: str, problem_statement: str, user_code: str):
    payload = {
        "session_id": session_id,
        "message": message,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }
    return post_request("/chat", payload)
