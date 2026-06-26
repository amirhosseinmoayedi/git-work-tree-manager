from __future__ import annotations

from pathlib import Path
from typing import Any

from .defaults import DEFAULT_CONFIG
from .yaml_loader import load_yaml


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(repo: Path, config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or repo / ".worktree.yml"
    raw = load_yaml(path.read_text()) if path.exists() else {}
    cfg = deep_merge(DEFAULT_CONFIG, raw or {})
    if not cfg["project"].get("name"):
        cfg["project"]["name"] = repo.name
    return cfg
