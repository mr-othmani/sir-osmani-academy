"""
github_store.py
Optional persistence layer that reads/writes courses.json directly to your
GitHub repository using the GitHub Contents API. This means added/updated/
deleted courses survive Streamlit Cloud restarts, since the data is saved
permanently in your repo instead of temporary server storage.

This only activates if the required secrets are configured in your
Streamlit app (Settings -> Secrets):

    GITHUB_TOKEN  = "your_personal_access_token"
    GITHUB_REPO   = "your-username/your-repo-name"
    GITHUB_BRANCH = "main"

If these secrets are not set (e.g. while testing locally), the app
automatically falls back to plain local JSON file storage - nothing breaks.
"""

import base64
import json

try:
    import requests
except ImportError:
    requests = None

try:
    import streamlit as st
except ImportError:
    st = None


def _get_secret(key):
    if st is None:
        return None
    try:
        return st.secrets.get(key)
    except Exception:
        return None


def is_github_storage_enabled():
    """Check whether all required GitHub secrets are configured."""
    if requests is None:
        return False
    token = _get_secret("GITHUB_TOKEN")
    repo = _get_secret("GITHUB_REPO")
    return bool(token and repo)


def _api_url(file_path):
    repo = _get_secret("GITHUB_REPO")
    return f"https://api.github.com/repos/{repo}/contents/{file_path}"


def _headers():
    token = _get_secret("GITHUB_TOKEN")
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }


def load_json_from_github(file_path):
    """
    Fetch and decode a JSON file from the GitHub repo.
    Returns an empty dict if the file doesn't exist yet or on any error.
    """
    try:
        response = requests.get(_api_url(file_path), headers=_headers(), timeout=10)
        if response.status_code != 200:
            return {}
        content = response.json().get("content", "")
        decoded = base64.b64decode(content).decode("utf-8")
        return json.loads(decoded)
    except Exception:
        return {}


def save_json_to_github(file_path, data, commit_message="Update data via app"):
    """
    Save (create or update) a JSON file in the GitHub repo.
    Returns (True, None) on success, or (False, error_message) on failure.
    """
    branch = _get_secret("GITHUB_BRANCH") or "main"
    try:
        # Need the current file's SHA to update it (GitHub requires this)
        get_response = requests.get(
            _api_url(file_path),
            headers=_headers(),
            params={"ref": branch},
            timeout=10,
        )
        sha = None
        if get_response.status_code == 200:
            sha = get_response.json().get("sha")
        elif get_response.status_code not in (404,):
            return False, f"GitHub read failed ({get_response.status_code}): {get_response.text[:300]}"

        encoded_content = base64.b64encode(
            json.dumps(data, indent=4, ensure_ascii=False).encode("utf-8")
        ).decode("utf-8")

        payload = {
            "message": commit_message,
            "content": encoded_content,
            "branch": branch,
        }
        if sha:
            payload["sha"] = sha

        put_response = requests.put(
            _api_url(file_path),
            headers=_headers(),
            json=payload,
            timeout=10,
        )
        if put_response.status_code in (200, 201):
            return True, None
        return False, f"GitHub write failed ({put_response.status_code}): {put_response.text[:300]}"
    except Exception as exc:
        return False, f"GitHub request error: {exc}"
