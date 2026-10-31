import os
from pathlib import Path
from dotenv import load_dotenv

# Paths relative to repository root
BACKEND_DIR = Path(__file__).resolve().parent
APP_DIR = BACKEND_DIR.parent
ROOT_DIR = APP_DIR.parent
ENGINE_DIR = ROOT_DIR / "engine"
DATA_DIR = ROOT_DIR / "data"
GENERATED_DIR = DATA_DIR / "generated"
MOCK_DIR = DATA_DIR / "mock"
RULES_DIR = DATA_DIR / "rules"
RUNTIME_DIR = DATA_DIR / "runtime"

# Ensure runtime directory exists
RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

# Safe .env loading without printing or exposing secrets
ENV_FILE = BACKEND_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
AI_MODE_RAW = os.getenv("AI_MODE", "false").lower()
AI_MODE = AI_MODE_RAW in ("true", "1", "yes", "on")
AI_TIMEOUT_MS = int(os.getenv("AI_TIMEOUT_MS", "20000"))
AI_MAX_OUTPUT_TOKENS = int(os.getenv("AI_MAX_OUTPUT_TOKENS", "120"))
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")

# DEC-044: The AI understands; approved templates speak.
# AI sentence drafting is turned OFF for all intents.
AI_DRAFTING_ENABLED: bool = False


def is_ai_enabled() -> bool:
    """Returns True only if AI_MODE is enabled, a non-empty OPENAI_API_KEY exists,
    and the daily AI call cap (300/day) has not been reached.
    """
    if not (AI_MODE and OPENAI_API_KEY and OPENAI_API_KEY.strip()):
        return False
    try:
        from .ai.cap_manager import cap_manager
        return not cap_manager.is_capped()
    except Exception:
        return True
