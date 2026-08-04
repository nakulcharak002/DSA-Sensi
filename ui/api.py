import requests
from constants import API_BASE_URL


def post_request(endpoint: str, payload: dict) -> dict:
    """
    Send a POST request to the backend.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "message": str(e)
        }


def execute_code(
    session_id: str,
    problem_statement: str,
    user_code: str,
):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }
    return post_request(
        "/execute",
        payload,
    )


def get_hint(
    session_id: str,
    problem_statement: str,
    stuck: bool = False,
):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "stuck": stuck,
    }
    return post_request(
        "/hint",
        payload,
    )


def review_code(
    session_id: str,
    problem_statement: str,
    user_code: str,
):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }
    return post_request(
        "/review",
        payload,
    )


def analyze_complexity(
    session_id: str,
    problem_statement: str,
    user_code: str,
):
    payload = {
        "session_id": session_id,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }
    return post_request(
        "/complexity",
        payload,
    )


def chat(
    session_id: str,
    message: str,
    problem_statement: str,
    user_code: str,
):

    payload = {
        "session_id": session_id,
        "message": message,
        "problem_statement": problem_statement,
        "user_code": user_code,
    }

    return post_request(
        "/chat",
        payload,
    )