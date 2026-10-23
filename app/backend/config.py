"""Backend configuration and paths."""
from pathlib import Path

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
