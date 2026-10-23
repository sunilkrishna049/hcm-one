"""Authentication and role-based access control (GR-2.1 to GR-2.6)."""
import json
from typing import Dict, List, Optional
from fastapi import Header, HTTPException, Request

from .ai_messages import get_message
from .config import MOCK_DIR


def load_users() -> Dict[str, dict]:
    users_path = MOCK_DIR / "users.json"
    data = json.loads(users_path.read_text(encoding="utf-8-sig"))
    return {u["user_id"]: u for u in data}


USERS = load_users()
ACTIVE_DEMO_USER_ID = "HR01"


def set_active_demo_user(user_id: str):
    global ACTIVE_DEMO_USER_ID
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")
    ACTIVE_DEMO_USER_ID = user_id
    return USERS[user_id]


def get_current_user(x_user_id: Optional[str] = Header(None)) -> dict:
    user_id = x_user_id or ACTIVE_DEMO_USER_ID
    if user_id in USERS:
        return USERS[user_id]
    return USERS["HR01"]


def check_employee_access(user: dict, target_employee_id: str):
    """Enforce GR-2.1 to GR-2.6.
    If unauthorized, return HTTP 403 with C10 and NO private target context.
    """
    allowed_ids = user.get("allowed_employee_ids") or []
    if target_employee_id not in allowed_ids:
        # Refusal per GR-2.4, GR-5.3 and Scenario 12: No target name, ID or existence confirmation.
        raise HTTPException(
            status_code=403,
            detail={
                "status": "Permission denied",
                "message": get_message("C10"),
                "certainty": "Permission denied"
            }
        )


def check_query_access(user: dict, query: dict):
    """Enforce access control for query records."""
    employee_id = query.get("employee_id")
    if not employee_id:
        return
    check_employee_access(user, employee_id)
