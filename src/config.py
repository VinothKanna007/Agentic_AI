import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = ROOT_DIR / ".env"

if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH, override=False)
else:
    load_dotenv(override=False)


def get_env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


TIGER_AI_GATEWAY_URL = get_env(
    "TIGER_AI_GATEWAY_URL",
    "https://api.ai-gateway.tigeranalytics.com",
)
TIGER_AI_GATEWAY_API_KEY = get_env("TIGER_AI_GATEWAY_API_KEY")
TIGER_AI_GATEWAY_MODEL = get_env("TIGER_AI_GATEWAY_MODEL", "gpt-5-nano")

__all__ = [
    "TIGER_AI_GATEWAY_URL",
    "TIGER_AI_GATEWAY_API_KEY",
    "TIGER_AI_GATEWAY_MODEL",
    "get_env",
]
