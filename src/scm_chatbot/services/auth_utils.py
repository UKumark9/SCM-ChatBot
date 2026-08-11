"""
Shared authentication utilities.
Used by both login_server.py (to sign) and ui.py (to verify).
"""

import hmac
import hashlib

_SECRET = "scm-chatbot-demo-2026"

USERS = {
    "admin":   {"password": "admin123",   "role": "admin",   "display": "Administrator"},
    "analyst": {"password": "analyst123", "role": "analyst", "display": "Data Analyst"},
}

ROLE_PERMISSIONS = {
    "admin": {
        "tabs":             ["chat", "docs", "stats", "perf"],
        "can_upload":       True,
        "can_delete":       True,
        "can_rebuild":      True,
        "docs_tab_visible": True,
    },
    "analyst": {
        "tabs":             ["chat", "stats", "perf"],
        "can_upload":       False,
        "can_delete":       False,
        "can_rebuild":      False,
        "docs_tab_visible": False,
    },
}


def authenticate(username: str, password: str) -> bool:
    user = USERS.get(username.strip().lower())
    return bool(user and user["password"] == password)


def get_role(username: str) -> str:
    user = USERS.get(username.strip().lower(), {})
    return user.get("role", "analyst")


def get_display(username: str) -> str:
    user = USERS.get(username.strip().lower(), {})
    return user.get("display", username)


def get_permissions(role: str) -> dict:
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["analyst"])


# ── HMAC token (stateless, no shared DB needed) ──────────────────────────────

def sign_user(username: str, role: str) -> str:
    """Create a short HMAC signature for username+role."""
    msg = f"{username}:{role}"
    return hmac.new(_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()[:24]


def verify_user(username: str, role: str, sig: str) -> bool:
    """Verify that sig was produced by sign_user() for this username+role."""
    if not all([username, role, sig]):
        return False
    try:
        expected = sign_user(username, role)
        return hmac.compare_digest(expected, sig)
    except Exception:
        return False
