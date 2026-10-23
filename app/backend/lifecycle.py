"""Lifecycle store and guardrails in data/runtime/ (PQ-08, PQ-09, DEC-011 to DEC-014, DEC-017)."""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import HTTPException

from .ai_messages import get_message
from .config import MOCK_DIR, RUNTIME_DIR
from .engine_bridge import bridge

EVENTS_FILE = RUNTIME_DIR / "events.json"
PROPOSALS_FILE = RUNTIME_DIR / "proposals.json"
QUERIES_FILE = RUNTIME_DIR / "queries.json"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data: Any):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class LifecycleStore:
    def __init__(self):
        self._ensure_init()

    def _ensure_init(self):
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        if not EVENTS_FILE.exists():
            _write_json(EVENTS_FILE, [])
        if not PROPOSALS_FILE.exists():
            _write_json(PROPOSALS_FILE, {})
        if not QUERIES_FILE.exists():
            # Seed with mock queries
            mock_queries = json.loads((MOCK_DIR / "queries.json").read_text(encoding="utf-8-sig"))
            _write_json(QUERIES_FILE, mock_queries)

    def reset_demo(self):
        """Reset demo store in data/runtime/."""
        _write_json(EVENTS_FILE, [])
        _write_json(PROPOSALS_FILE, {})
        mock_queries = json.loads((MOCK_DIR / "queries.json").read_text(encoding="utf-8-sig"))
        _write_json(QUERIES_FILE, mock_queries)
        return {"status": "Demo reset successful", "events_cleared": True}

    def record_event(self, event_type: str, actor: dict, details: dict) -> dict:
        events = _read_json(EVENTS_FILE, [])
        event_id = f"EVT-{len(events) + 1:04d}-{uuid.uuid4().hex[:6]}"
        event = {
            "event_id": event_id,
            "event_type": event_type,
            "actor": {
                "user_id": actor.get("user_id"),
                "name": actor.get("name"),
                "role": actor.get("role")
            },
            "timestamp": _now_iso(),
            **details
        }
        events.append(event)
        _write_json(EVENTS_FILE, events)
        return event

    def get_events(self) -> List[dict]:
        return _read_json(EVENTS_FILE, [])

    # --- Proposals ---

    def get_or_create_proposal(self, proposal_id: str, default_data: dict) -> dict:
        proposals = _read_json(PROPOSALS_FILE, {})
        if proposal_id not in proposals:
            proposals[proposal_id] = {
                "proposal_id": proposal_id,
                "current_version": 1,
                "status": default_data.get("status", "Calculated; needs HR approval"),
                "certainty": default_data.get("certainty", "Complete for this scope"),
                "scope": default_data.get("scope", {}),
                "versions": {
                    "1": {
                        "version": 1,
                        "created_at": _now_iso(),
                        "status": default_data.get("status", "Calculated; needs HR approval"),
                        "data": default_data
                    }
                }
            }
            _write_json(PROPOSALS_FILE, proposals)
        return proposals[proposal_id]

    def approve_proposal(self, proposal_id: str, version: int, actor: dict, selected_scope: Optional[dict] = None) -> dict:
        proposals = _read_json(PROPOSALS_FILE, {})
        if proposal_id not in proposals:
            raise HTTPException(status_code=404, detail="Proposal not found")
        prop = proposals[proposal_id]

        # Guard: Check version staleness (C25)
        if version != prop["current_version"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "C25",
                    "message": get_message("C25"),
                    "current_version": prop["current_version"],
                    "requested_version": version
                }
            )

        # Guard: Check completeness of scope
        current_data = prop["versions"][str(version)]["data"]
        certainty = current_data.get("certainty")
        if certainty in ("Incomplete", "Rule not verified") and not selected_scope:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Incomplete or unverified scope cannot be approved",
                    "certainty": certainty,
                    "message": "Incomplete scope cannot be approved; obtain required inputs first."
                }
            )

        # Check if selected scope contains incomplete items
        if selected_scope and selected_scope.get("has_incomplete"):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Selected scope contains incomplete or unverified records",
                    "message": "Cannot approve scope with incomplete entries."
                }
            )

        # Record explicit approval
        prop["status"] = "Approved and ready for payroll"
        prop["approved_version"] = version
        prop["approved_by"] = actor["user_id"]
        prop["approved_at"] = _now_iso()
        prop["approved_scope"] = selected_scope or prop.get("scope")
        proposals[proposal_id] = prop
        _write_json(PROPOSALS_FILE, proposals)

        event = self.record_event(
            "approve",
            actor,
            {
                "proposal_id": proposal_id,
                "version": version,
                "approved_scope": selected_scope or prop.get("scope"),
                "status": "Approved and ready for payroll"
            }
        )

        return {
            "status": "Approved and ready for payroll",
            "proposal_id": proposal_id,
            "version": version,
            "event": event,
            "message": get_message("C04")
        }

    def edit_proposal(self, proposal_id: str, actor: dict, line: str, proposed_value: Any, reason: str) -> dict:
        if not reason or not reason.strip():
            raise HTTPException(status_code=400, detail="An explicit reason is required to edit a proposal.")

        proposals = _read_json(PROPOSALS_FILE, {})
        if proposal_id not in proposals:
            raise HTTPException(status_code=404, detail="Proposal not found")
        prop = proposals[proposal_id]

        new_version = prop["current_version"] + 1

        # Recalculate using the engine
        recalculated_data = {}
        if "HIKE" in proposal_id:
            emp_id = prop["scope"].get("employee_id", "E01")
            new_pct = float(proposed_value)
            recalculated_data = bridge.recalculate_hike(emp_id, new_pct, reason)
        else:
            recalculated_data = dict(prop["versions"][str(prop["current_version"])]["data"])
            recalculated_data["edited_line"] = line
            recalculated_data["proposed_value"] = proposed_value

        prop["current_version"] = new_version
        prop["status"] = "Revised"
        prop["versions"][str(new_version)] = {
            "version": new_version,
            "created_at": _now_iso(),
            "status": "Revised",
            "edit_details": {
                "line": line,
                "proposed_value": proposed_value,
                "reason": reason,
                "edited_by": actor["user_id"]
            },
            "data": recalculated_data
        }
        proposals[proposal_id] = prop
        _write_json(PROPOSALS_FILE, proposals)

        event = self.record_event(
            "edit",
            actor,
            {
                "proposal_id": proposal_id,
                "new_version": new_version,
                "line": line,
                "proposed_value": proposed_value,
                "reason": reason
            }
        )

        return {
            "status": "Revised",
            "proposal_id": proposal_id,
            "version": new_version,
            "recalculated_data": recalculated_data,
            "event": event,
            "message": get_message("C05")
        }

    def reject_proposal(self, proposal_id: str, actor: dict, reason: Optional[str] = None) -> dict:
        proposals = _read_json(PROPOSALS_FILE, {})
        if proposal_id not in proposals:
            raise HTTPException(status_code=404, detail="Proposal not found")
        prop = proposals[proposal_id]
        prop["status"] = "Rejected"
        _write_json(PROPOSALS_FILE, proposals)

        event = self.record_event(
            "reject",
            actor,
            {
                "proposal_id": proposal_id,
                "version": prop["current_version"],
                "reason": reason
            }
        )

        return {
            "status": "Rejected",
            "proposal_id": proposal_id,
            "version": prop["current_version"],
            "event": event
        }

    # --- Queries ---

    def get_queries(self, employee_id: Optional[str] = None) -> List[dict]:
        queries = _read_json(QUERIES_FILE, [])
        if employee_id:
            return [q for q in queries if q.get("employee_id") == employee_id]
        return queries

    def get_query(self, query_id: str) -> dict:
        queries = _read_json(QUERIES_FILE, [])
        for q in queries:
            if q["query_id"] == query_id:
                return q
        raise HTTPException(status_code=404, detail="Query not found")

    def draft_query(self, actor: dict, employee_id: str, category: str, months: List[str], description: str, evidence: List[dict]) -> dict:
        draft = {
            "query_id": f"DRAFT-{uuid.uuid4().hex[:8]}",
            "employee_id": employee_id,
            "category": category,
            "months": months,
            "description": description,
            "evidence": evidence,
            "status": "Draft",
            "hr_reply": None,
            "created_date": _now_iso(),
            "history": [{"status": "Draft", "time": _now_iso(), "actor": actor["user_id"]}]
        }
        event = self.record_event("query_draft", actor, {"draft": draft})
        return {"draft": draft, "event": event, "message": get_message("C17")}

    def confirm_send_query(self, actor: dict, draft: dict, add_or_new: str, target_query_id: Optional[str] = None, confirmed: bool = False) -> dict:
        if not confirmed:
            raise HTTPException(status_code=400, detail="Explicit confirmation is required before sending a query.")

        queries = _read_json(QUERIES_FILE, [])

        if add_or_new == "add" and target_query_id:
            # Append to existing query
            target = next((q for q in queries if q["query_id"] == target_query_id), None)
            if not target:
                raise HTTPException(status_code=404, detail="Target query for append not found")
            # Append description and evidence
            target["description"] = f"{target['description']}\n\n[Appended on {_now_iso()}]: {draft['description']}"
            existing_ev_ids = {e.get("record_id") for e in target.get("evidence", [])}
            for ev in draft.get("evidence", []):
                if ev.get("record_id") not in existing_ev_ids:
                    target.setdefault("evidence", []).append(ev)
            target.setdefault("history", []).append({
                "status": target["status"],
                "action": "appended",
                "time": _now_iso(),
                "actor": actor["user_id"]
            })
            _write_json(QUERIES_FILE, queries)
            event = self.record_event("query_append", actor, {"target_query_id": target_query_id, "appended_text": draft["description"]})
            return {
                "query": target,
                "status": target["status"],
                "action": "appended",
                "event": event,
                "message": get_message("C15" if target["status"] == "Sent" else "C16")
            }
        else:
            # Send as new query
            new_id = f"QUERY-{draft['employee_id']}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
            new_query = {
                "query_id": new_id,
                "employee_id": draft["employee_id"],
                "category": draft.get("category", "salary"),
                "months": draft.get("months", []),
                "description": draft["description"],
                "evidence": draft.get("evidence", []),
                "status": "Sent",
                "hr_reply": None,
                "created_date": _now_iso(),
                "history": [{"status": "Sent", "time": _now_iso(), "actor": actor["user_id"]}]
            }
            queries.append(new_query)
            _write_json(QUERIES_FILE, queries)
            event = self.record_event("query_send", actor, {"query_id": new_id, "status": "Sent"})
            return {
                "query": new_query,
                "status": "Sent",
                "action": "created",
                "event": event,
                "message": get_message("C15")
            }

    def take_into_review(self, query_id: str, actor: dict) -> dict:
        queries = _read_json(QUERIES_FILE, [])
        query = next((q for q in queries if q["query_id"] == query_id), None)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        query["status"] = "In review"
        query.setdefault("history", []).append({"status": "In review", "time": _now_iso(), "actor": actor["user_id"]})
        _write_json(QUERIES_FILE, queries)
        event = self.record_event("take_into_review", actor, {"query_id": query_id, "status": "In review"})
        return {"query": query, "status": "In review", "event": event, "message": get_message("C16")}

    def reply_query(self, query_id: str, actor: dict, reply_text: str) -> dict:
        queries = _read_json(QUERIES_FILE, [])
        query = next((q for q in queries if q["query_id"] == query_id), None)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        query["hr_reply"] = reply_text
        query.setdefault("history", []).append({"action": "reply", "time": _now_iso(), "actor": actor["user_id"], "reply": reply_text})
        _write_json(QUERIES_FILE, queries)
        event = self.record_event("reply", actor, {"query_id": query_id, "reply": reply_text})
        return {"query": query, "event": event}

    def resolve_query(self, query_id: str, actor: dict, reply_text: Optional[str] = None) -> dict:
        queries = _read_json(QUERIES_FILE, [])
        query = next((q for q in queries if q["query_id"] == query_id), None)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        if reply_text:
            query["hr_reply"] = reply_text
        if not query.get("hr_reply"):
            raise HTTPException(status_code=400, detail="Cannot record resolution without an HR reply.")
        query["status"] = "Resolved"
        query["resolved_at"] = _now_iso()
        query.setdefault("history", []).append({"status": "Resolved", "time": _now_iso(), "actor": actor["user_id"]})
        _write_json(QUERIES_FILE, queries)
        event = self.record_event("resolve", actor, {"query_id": query_id, "status": "Resolved"})
        return {"query": query, "status": "Resolved", "event": event, "message": get_message("C23")}

    def dispute_query(self, query_id: str, actor: dict, reason: Optional[str] = None) -> dict:
        queries = _read_json(QUERIES_FILE, [])
        query = next((q for q in queries if q["query_id"] == query_id), None)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        query["status"] = "In review"
        query.setdefault("history", []).append({"status": "In review", "action": "dispute", "reason": reason, "time": _now_iso(), "actor": actor["user_id"]})
        _write_json(QUERIES_FILE, queries)
        event = self.record_event("dispute", actor, {"query_id": query_id, "reason": reason, "status": "In review"})
        return {"query": query, "status": "In review", "event": event, "message": get_message("C16")}

    def close_query(self, query_id: str, actor: dict) -> dict:
        queries = _read_json(QUERIES_FILE, [])
        query = next((q for q in queries if q["query_id"] == query_id), None)
        if not query:
            raise HTTPException(status_code=404, detail="Query not found")
        if query["status"] != "Resolved":
            raise HTTPException(status_code=400, detail="Only a resolved query can be closed.")
        query["status"] = "Closed"
        query["closed_at"] = _now_iso()
        query.setdefault("history", []).append({"status": "Closed", "time": _now_iso(), "actor": actor["user_id"]})
        _write_json(QUERIES_FILE, queries)
        event = self.record_event("close", actor, {"query_id": query_id, "status": "Closed"})
        return {"query": query, "status": "Closed", "event": event, "message": get_message("C24")}


lifecycle = LifecycleStore()
