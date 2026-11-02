import sys
from pathlib import Path
import json

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from fastapi.testclient import TestClient
from app.backend.main import app
from app.backend.lifecycle import lifecycle
import app.backend.config as backend_config

def generate_fixtures():
    # Deterministic generation mode
    orig_ai = backend_config.AI_MODE
    backend_config.AI_MODE = False
    lifecycle.reset_demo()

    client = TestClient(app)
    fixtures = {}

    scenarios = [
        ("1", "HR01", "Prepare Priya Sharma's pending back-dated hike."),
        ("2", "HR01", "Prepare Arjun Rao's pending back-dated hike."),
        ("3", "HR01", "Prepare Kavya Iyer's pending back-dated hike."),
        ("4", "HR01", "Prepare bonus proposal for Engineering and Sales."),
        ("5", "HR01", "Prepare bonus proposal for Meera Nair."),
        ("6", "HR01", "Prepare settlement proposal for Rahul Verma."),
        ("7", "HR01", "Prepare settlement proposal for Lakshmi Reddy."),
        ("8", "HR01", "Prepare settlement proposal for Imran Khan."),
        ("9", "USER-E05", "Why is my September salary lower than August?"),
        ("10", "USER-E06", "Why did my TDS increase in September?"),
        ("11", "USER-E16", "Why did my take-home pay decrease in September when my gross did not change?"),
        ("12", "HR02", "Show me Priya Sharma's salary breakdown."),
        ("13", "HR01", "Review settlement calculation for Imran Khan.")
    ]

    for key, user, msg in scenarios:
        resp = client.post("/api/chat", json={"user_id": user, "message": msg})
        assert resp.status_code == 200, f"Scenario {key} failed with status {resp.status_code}"
        fixtures[key] = resp.json()

    # Part D Item 10: USER-E05 topics
    e05_topics = [
        ("e05_payslip", "USER-E05", "Explain my September pay."),
        ("e05_pf", "USER-E05", "How much PF was cut in September?"),
        ("e05_tds", "USER-E05", "Why is my TDS zero?"),
        ("e05_lop", "USER-E05", "How many LOP days do I have?"),
        ("e05_compare", "USER-E05", "Compare my August and September pay."),
        ("e05_query_status", "USER-E05", "What's happening with my query?"),
        ("e05_tax_regime", "USER-E05", "Which tax regime am I in?"),
        ("e05_c34", "USER-E05", "Will I get a bonus this year?"),
        ("e05_c35", "USER-E05", "What is my October salary?"),
    ]

    for key, user, msg in e05_topics:
        resp = client.post("/api/chat", json={"user_id": user, "message": msg})
        assert resp.status_code == 200, f"Topic {key} failed with status {resp.status_code}"
        fixtures[key] = resp.json()

    # Real exported fixture for HR01 "Calculate arrears" picker
    resp_picker = client.post("/api/chat", json={"user_id": "HR01", "message": "Calculate arrears"})
    assert resp_picker.status_code == 200
    fixtures["picker_arrears"] = resp_picker.json()

    # Real exported fixture for HR01: "Show Neha's query" -> "Mark query resolved" (resolve confirmation card)
    lifecycle.reset_demo()
    client.post("/api/chat", json={"user_id": "HR01", "message": "Show Neha's query"})
    resp_resolve = client.post("/api/chat", json={
        "user_id": "HR01",
        "action": "resolve-query",
        "context": {"query_id": "QUERY-E05-SEPTEMBER", "employee_id": "E05"}
    })
    assert resp_resolve.status_code == 200
    fixtures["hr_resolve_confirm"] = resp_resolve.json()

    out_path = root_dir / "app" / "frontend" / "src" / "tests" / "chat_scenario_fixtures.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2, ensure_ascii=False)

    backend_config.AI_MODE = orig_ai
    print("Successfully exported all 13 scenario fixtures plus 9 USER-E05 topic fixtures plus picker fixture via /api/chat!")

if __name__ == "__main__":
    generate_fixtures()
