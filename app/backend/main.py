"""HCM One Prototype Backend API.
Built with FastAPI. Deterministic engine-driven. Zero dynamic LLM calls.
"""
import json
from typing import Any, Dict, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .ai_messages import AI_MESSAGES, get_message
from .auth import USERS, check_employee_access, check_query_access, get_current_user, set_active_demo_user
from .config import MOCK_DIR
from .engine_bridge import bridge
from .lifecycle import lifecycle
from .chat_router import chat_router


def load_employees_map() -> Dict[str, dict]:
    path = MOCK_DIR / "employees.json"
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        return {e["employee_id"]: e for e in data}
    return {}


EMPLOYEES_MAP = load_employees_map()


app = FastAPI(
    title="HCM One Prototype API",
    description="Deterministic Indian Payroll Prototype Backend",
    version="1.0.0"
)

# Enable CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCENARIOS_META = [
    {
        "scenario_num": 1,
        "scenario_id": "scenario-01",
        "title": "Hike with LOP",
        "description": "Employee with unpaid leave (loss of pay) whose hike is back-dated across multiple months",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E01",
        "mode": "hike",
        "platform": "desktop"
    },
    {
        "scenario_num": 2,
        "scenario_id": "scenario-02",
        "title": "Hike across PF ceiling change",
        "description": "Employee whose back-dated hike spans a statutory PF wage ceiling change on 2026-09-17",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E02",
        "mode": "hike",
        "platform": "desktop"
    },
    {
        "scenario_num": 3,
        "scenario_id": "scenario-03",
        "title": "Hike with missing attendance",
        "description": "Employee with a back-dated hike where one month's attendance record is missing",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E03",
        "mode": "hike",
        "platform": "desktop"
    },
    {
        "scenario_num": 4,
        "scenario_id": "scenario-04",
        "title": "Team bonus with joiner and notice cases",
        "description": "Bonus run covering both an annual performance bonus and a quarterly sales incentive",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": None,
        "mode": "bonus",
        "platform": "desktop"
    },
    {
        "scenario_num": 5,
        "scenario_id": "scenario-05",
        "title": "Missing performance rating",
        "description": "Bonus proposal where one employee's annual performance rating is not recorded",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E09",
        "mode": "bonus",
        "platform": "desktop"
    },
    {
        "scenario_num": 6,
        "scenario_id": "scenario-06",
        "title": "Eligible gratuity settlement",
        "description": "Exiting employee with over five years of service whose gratuity meets eligibility rules",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E10",
        "mode": "settlement",
        "platform": "desktop"
    },
    {
        "scenario_num": 7,
        "scenario_id": "scenario-07",
        "title": "Below gratuity minimum",
        "description": "Exiting employee whose service is close to but below the five-year minimum gratuity threshold",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E11",
        "mode": "settlement",
        "platform": "desktop"
    },
    {
        "scenario_num": 8,
        "scenario_id": "scenario-08",
        "title": "Asset clearance & notice shortfall",
        "description": "Exiting employee with a notice shortfall recovery and unreturned company assets",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E12",
        "mode": "settlement",
        "platform": "desktop"
    },
    {
        "scenario_num": 9,
        "scenario_id": "scenario-09",
        "title": "Salary drop with LOP",
        "description": "Employee whose take-home pay dropped between August and September due to unpaid leave (loss of pay)",
        "role": "Employee",
        "screen_id": "SCR-04",
        "employee_id": "E05",
        "mode": "salary",
        "platform": "mobile"
    },
    {
        "scenario_num": 10,
        "scenario_id": "scenario-10",
        "title": "Previous employer declaration",
        "description": "Employee whose TDS increased because they declared income from a previous employer mid-year",
        "role": "Employee",
        "screen_id": "SCR-04",
        "employee_id": "E06",
        "mode": "tds",
        "platform": "mobile"
    },
    {
        "scenario_num": 11,
        "scenario_id": "scenario-11",
        "title": "No salary earning change",
        "description": "Employee whose take-home pay changed even though gross earnings did not change",
        "role": "Employee",
        "screen_id": "SCR-04",
        "employee_id": "E16",
        "mode": "salary",
        "platform": "mobile"
    },
    {
        "scenario_num": 12,
        "scenario_id": "scenario-12",
        "title": "Another employee's data requested",
        "description": "Employee asking for another colleague's salary or tax information (permission denied)",
        "role": "Employee",
        "screen_id": "SCR-04",
        "employee_id": "E01",  # target is unauthorized for regular employees
        "mode": "permission_denied",
        "platform": "mobile"
    },
    {
        "scenario_num": 13,
        "scenario_id": "scenario-13",
        "title": "Known & unresolved settlement components",
        "description": "Exiting employee settlement with confirmed components beside an unresolved asset clearance",
        "role": "HR Admin",
        "screen_id": "SCR-02",
        "employee_id": "E12",
        "mode": "settlement",
        "platform": "desktop"
    }
]


# --- Request/Response Models ---

class LoginRequest(BaseModel):
    user_id: str


class EditProposalRequest(BaseModel):
    line: str
    proposed_value: Any
    reason: str


class ApproveProposalRequest(BaseModel):
    version: int
    selected_scope: Optional[dict] = None


class RejectProposalRequest(BaseModel):
    reason: Optional[str] = None


class BonusScopeRequest(BaseModel):
    bonus_type: str
    period: str
    selected_employee_ids: List[str]


class DraftQueryRequest(BaseModel):
    employee_id: str
    category: str
    months: List[str]
    description: str
    evidence: List[dict]


class ConfirmSendQueryRequest(BaseModel):
    draft: dict
    add_or_new: str = "new"  # 'new' or 'add'
    target_query_id: Optional[str] = None
    confirmed: bool = False


class QueryReplyRequest(BaseModel):
    reply_text: str


class QueryResolveRequest(BaseModel):
    reply_text: Optional[str] = None


class QueryDisputeRequest(BaseModel):
    reason: Optional[str] = None


# --- Authentication & User Endpoints ---

@app.get("/api/me")
def get_me(user: dict = Depends(get_current_user)):
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "role": user["role"],
        "employee_id": user.get("employee_id"),
        "allowed_employee_ids": user.get("allowed_employee_ids", []),
        "allowed_department": user.get("allowed_department")
    }


@app.get("/api/users")
def list_users():
    return list(USERS.values())


@app.get("/api/employees")
def list_employees():
    return list(EMPLOYEES_MAP.values())


@app.get("/api/employees/{employee_id}")
def get_employee(employee_id: str):
    if employee_id in EMPLOYEES_MAP:
        return EMPLOYEES_MAP[employee_id]
    raise HTTPException(status_code=404, detail="Employee not found")


@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = set_active_demo_user(req.user_id)
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "role": user["role"],
        "employee_id": user.get("employee_id"),
        "allowed_employee_ids": user.get("allowed_employee_ids", []),
        "allowed_department": user.get("allowed_department")
    }


# --- Scenario Endpoints ---

@app.get("/api/scenarios")
def list_scenarios():
    return SCENARIOS_META


@app.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: str, user: dict = Depends(get_current_user)):
    meta = next((s for s in SCENARIOS_META if s["scenario_id"] == scenario_id), None)
    if not meta:
        raise HTTPException(status_code=404, detail="Scenario not found")

    # Access control:
    # If scenario 12: explicit test of unauthorized access
    if meta["scenario_num"] == 12:
        return {
            "scenario_id": "scenario-12",
            "description": meta["description"],
            "status": "Permission denied",
            "message": get_message("C10"),
            "certainty": "Permission denied",
            "result": {"status": "Permission denied"},
            "display_inputs": {}
        }

    # For employee role: cannot access other employees' scenarios
    if user["role"] == "Employee":
        if meta["employee_id"] and meta["employee_id"] != user.get("employee_id"):
            raise HTTPException(
                status_code=403,
                detail={
                    "status": "Permission denied",
                    "message": get_message("C10"),
                    "certainty": "Permission denied"
                }
            )
    elif user["role"] == "HR Admin":
        # HR02 sees only Sales employees (E13, E14, E15)
        if meta["employee_id"] and meta["employee_id"] not in (user.get("allowed_employee_ids") or []):
            raise HTTPException(
                status_code=403,
                detail={
                    "status": "Permission denied",
                    "message": get_message("C10"),
                    "certainty": "Permission denied"
                }
            )

    data = bridge.get_scenario(meta["scenario_num"])

    # Attach runtime proposal state if it is a proposal screen
    proposal_id = None
    if meta["mode"] == "hike":
        proposal_id = f"PROP-HIKE-{meta['employee_id']}"
    elif meta["mode"] == "bonus":
        proposal_id = f"PROP-BONUS-SCENARIO-{meta['scenario_num']:02d}"
    elif meta["mode"] == "settlement":
        proposal_id = f"PROP-SETTLEMENT-{meta['employee_id']}"

    runtime_proposal = None
    if proposal_id:
        runtime_proposal = lifecycle.get_or_create_proposal(proposal_id, {
            "status": data["result"].get("proposal_status", "Calculated; needs HR approval"),
            "certainty": data["result"].get("certainty", "Complete for this scope"),
            "scope": {"employee_id": meta["employee_id"], "scenario_id": scenario_id},
            "data": data["result"]
        })

    enriched_meta = dict(meta)
    if meta.get("employee_id") and meta["employee_id"] in EMPLOYEES_MAP:
        enriched_meta["employee"] = EMPLOYEES_MAP[meta["employee_id"]]

    return {
        "meta": enriched_meta,
        "scenario": data,
        "runtime_proposal": runtime_proposal
    }


# --- Proposals & Engine Calculations ---

@app.post("/api/proposals/bonus/calculate-scope")
def calculate_bonus_scope(req: BonusScopeRequest, user: dict = Depends(get_current_user)):
    # Guard: check permissions on selected employees
    for eid in req.selected_employee_ids:
        check_employee_access(user, eid)
    res = bridge.calculate_bonus_scope(req.bonus_type, req.period, req.selected_employee_ids)
    return res


@app.post("/api/proposals/{proposal_id}/approve")
def approve_proposal(proposal_id: str, req: ApproveProposalRequest, user: dict = Depends(get_current_user)):
    if user["role"] != "HR Admin":
        raise HTTPException(status_code=403, detail="Only HR Admin can approve proposals.")
    return lifecycle.approve_proposal(proposal_id, req.version, user, req.selected_scope)


@app.post("/api/proposals/{proposal_id}/edit")
def edit_proposal(proposal_id: str, req: EditProposalRequest, user: dict = Depends(get_current_user)):
    if user["role"] != "HR Admin":
        raise HTTPException(status_code=403, detail="Only HR Admin can edit proposals.")
    return lifecycle.edit_proposal(proposal_id, user, req.line, req.proposed_value, req.reason)


@app.post("/api/proposals/{proposal_id}/reject")
def reject_proposal(proposal_id: str, req: RejectProposalRequest, user: dict = Depends(get_current_user)):
    if user["role"] != "HR Admin":
        raise HTTPException(status_code=403, detail="Only HR Admin can reject proposals.")
    return lifecycle.reject_proposal(proposal_id, user, req.reason)


# --- Payslip Comparisons & TDS Details ---

@app.get("/api/payslips/compare")
def compare_payslips(employee_id: str = Query(...), user: dict = Depends(get_current_user)):
    check_employee_access(user, employee_id)
    # Check scenario 9 (E05), scenario 10 (E06), scenario 11 (E16)
    if employee_id == "E05":
        return bridge.get_scenario(9)
    elif employee_id == "E06":
        return bridge.get_scenario(10)
    elif employee_id == "E16":
        return bridge.get_scenario(11)
    # Or query from engine bundle
    bundle = bridge.get_bundle()
    res = bundle["flows"].compare(employee_id, bundle["store"].processed[-2], bundle["store"].processed[-1])
    return {"result": res}


@app.get("/api/tds/detail")
def tds_detail(employee_id: str = Query(...), user: dict = Depends(get_current_user)):
    check_employee_access(user, employee_id)
    if employee_id == "E06":
        return bridge.get_scenario(10)
    bundle = bridge.get_bundle()
    res = bundle["flows"].compare(employee_id, bundle["store"].processed[-2], bundle["store"].processed[-1])
    return {"result": res}


# --- Queries Endpoints ---

@app.get("/api/queries")
def list_queries(user: dict = Depends(get_current_user)):
    if user["role"] == "Employee":
        return lifecycle.get_queries(employee_id=user.get("employee_id"))
    # HR Admin: return queries within allowed employees
    all_queries = lifecycle.get_queries()
    allowed = set(user.get("allowed_employee_ids") or [])
    return [q for q in all_queries if q.get("employee_id") in allowed]


@app.get("/api/queries/{query_id}")
def get_query(query_id: str, user: dict = Depends(get_current_user)):
    q = lifecycle.get_query(query_id)
    check_query_access(user, q)
    return q


@app.post("/api/queries/draft")
def draft_query(req: DraftQueryRequest, user: dict = Depends(get_current_user)):
    check_employee_access(user, req.employee_id)
    return lifecycle.draft_query(user, req.employee_id, req.category, req.months, req.description, req.evidence)


@app.post("/api/queries/confirm-send")
def confirm_send_query(req: ConfirmSendQueryRequest, user: dict = Depends(get_current_user)):
    emp_id = req.draft.get("employee_id")
    check_employee_access(user, emp_id)
    return lifecycle.confirm_send_query(user, req.draft, req.add_or_new, req.target_query_id, req.confirmed)


@app.post("/api/queries/{query_id}/take-into-review")
def take_into_review(query_id: str, user: dict = Depends(get_current_user)):
    if user["role"] != "HR Admin":
        raise HTTPException(status_code=403, detail="Only HR Admin can take queries into review.")
    q = lifecycle.get_query(query_id)
    check_query_access(user, q)
    return lifecycle.take_into_review(query_id, user)


@app.post("/api/queries/{query_id}/reply")
def reply_query(query_id: str, req: QueryReplyRequest, user: dict = Depends(get_current_user)):
    if user["role"] != "HR Admin":
        raise HTTPException(status_code=403, detail="Only HR Admin can reply to queries.")
    q = lifecycle.get_query(query_id)
    check_query_access(user, q)
    return lifecycle.reply_query(query_id, user, req.reply_text)


@app.post("/api/queries/{query_id}/resolve")
def resolve_query(query_id: str, req: QueryResolveRequest, user: dict = Depends(get_current_user)):
    if user["role"] != "HR Admin":
        raise HTTPException(status_code=403, detail="Only HR Admin can resolve queries.")
    q = lifecycle.get_query(query_id)
    check_query_access(user, q)
    return lifecycle.resolve_query(query_id, user, req.reply_text)


@app.post("/api/queries/{query_id}/dispute")
def dispute_query(query_id: str, req: QueryDisputeRequest, user: dict = Depends(get_current_user)):
    q = lifecycle.get_query(query_id)
    check_query_access(user, q)
    return lifecycle.dispute_query(query_id, user, req.reason)


@app.post("/api/queries/{query_id}/close")
def close_query(query_id: str, user: dict = Depends(get_current_user)):
    q = lifecycle.get_query(query_id)
    check_query_access(user, q)
    return lifecycle.close_query(query_id, user)


# --- Demo Reset & Messages ---

@app.post("/api/demo/reset")
def reset_demo():
    res = lifecycle.reset_demo()
    set_active_demo_user("HR01")
    return res


@app.get("/api/ai/messages")
def get_ai_messages():
    """Expose verbatim C01-C30 copy catalog."""
    return AI_MESSAGES


# --- Conversational Chat Endpoint (Chat-First Architecture) ---

class ChatRequest(BaseModel):
    user_id: Optional[str] = "HR01"
    message: Optional[str] = ""
    action: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@app.post("/api/chat")
def handle_chat_endpoint(req: ChatRequest, user: dict = Depends(get_current_user)):
    """Unified chat endpoint executing deterministic intent router per chat_contract.md."""
    target_user_id = req.user_id or user.get("user_id", "HR01")
    return chat_router.handle_chat(
        user_id=target_user_id,
        message=req.message or "",
        action=req.action,
        context=req.context or {}
    )

