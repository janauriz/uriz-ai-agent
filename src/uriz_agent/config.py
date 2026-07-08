"""Configuration helpers."""

from __future__ import annotations

import os
from pathlib import Path


def load_environment(env_file: str | Path = ".env") -> None:
    """Load `.env` values without making python-dotenv mandatory for offline tests."""

    try:
        from dotenv import load_dotenv

        load_dotenv(env_file)
        return
    except ImportError:
        pass

    path = Path(env_file)
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

