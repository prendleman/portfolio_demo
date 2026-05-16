"""Load repository-root ``.env`` into ``os.environ`` when ``python-dotenv`` is installed."""

from __future__ import annotations

from pathlib import Path


def load_repo_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    root = Path(__file__).resolve().parents[1]
    path = root / ".env"
    if path.is_file():
        load_dotenv(path)
