from __future__ import annotations

from typing import Any


def load_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore

        return yaml.safe_load(text) or {}
    except Exception:
        from .simple_yaml import loads

        return loads(text)
