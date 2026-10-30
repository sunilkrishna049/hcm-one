"""Daily AI Call Cap Manager.
Enforces a daily cap of 300 live AI calls per day on public links.
When the cap is reached, AI turns off automatically and safe templates answer.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("app.backend.ai.cap_manager")

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
RUNTIME_DIR = DATA_DIR / "runtime"
CAP_FILE = RUNTIME_DIR / "ai_daily_usage.json"
DAILY_CAP = 300


class AICallCapManager:
    def __init__(self, cap: int = DAILY_CAP, file_path: Path = CAP_FILE):
        self.cap = cap
        self.file_path = file_path

    def _get_today_str(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _read_state(self) -> dict:
        if self.file_path.exists():
            try:
                data = json.loads(self.file_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {"date": self._get_today_str(), "count": 0}

    def _write_state(self, state: dict):
        try:
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning("Masked warning: Unable to persist daily AI usage state.")

    def is_capped(self) -> bool:
        """Returns True if the daily limit of live AI calls has been reached."""
        state = self._read_state()
        today = self._get_today_str()
        if state.get("date") != today:
            return False
        return state.get("count", 0) >= self.cap

    def record_live_call(self) -> bool:
        """Attempts to register a live AI call.
        If under cap: increments count and returns True.
        If cap reached: logs a masked warning and returns False.
        """
        state = self._read_state()
        today = self._get_today_str()
        if state.get("date") != today:
            state = {"date": today, "count": 0}

        if state["count"] >= self.cap:
            logger.warning(
                f"Masked warning: Daily AI call cap ({self.cap}) reached for {today}. Automatically reverting to deterministic safe templates."
            )
            return False

        state["count"] += 1
        self._write_state(state)
        return True

    def get_count(self) -> int:
        state = self._read_state()
        if state.get("date") != self._get_today_str():
            return 0
        return state.get("count", 0)

    def reset(self, count: int = 0, date: Optional[str] = None):
        """Reset counter (used in tests and startup reset)."""
        state = {"date": date or self._get_today_str(), "count": count}
        self._write_state(state)


cap_manager = AICallCapManager()

