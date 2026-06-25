from __future__ import annotations

from pathlib import Path
from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "project": {"name": None, "default_base_ref": "main"},
    "worktrees": {
        "root": "../.worktrees/${project.name}",
        "id_template": "${task_slug}-${agent}-${counter}",
        "branch_template": "agent/${task_slug}-${agent}-${counter}",
    },
    "resources": {"ports": {}, "env": {}},
    "env": {"source": ".env", "output": ".env", "copy_ignored": [".env"], "overrides": {}},
    "hooks": {"pre_create": [], "post_create": [], "pre_remove": [], "post_remove": []},
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(repo: Path) -> dict[str, Any]:
    path = repo / ".worktree.yml"
    raw = _load_yaml(path.read_text()) if path.exists() else {}
    cfg = deep_merge(DEFAULT_CONFIG, raw or {})
    if not cfg["project"].get("name"):
        cfg["project"]["name"] = repo.name
    return cfg


def _load_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text) or {}
    except Exception:
        from .simple_yaml import loads
        return loads(text)
