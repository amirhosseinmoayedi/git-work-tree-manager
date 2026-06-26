from __future__ import annotations

import hashlib
import re
from string import Template
from typing import Any


def slug(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "worktree"


def db(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_").lower()
    if not value or value[0].isdigit():
        value = f"wt_{value}"
    return value[:63]


def port_hash(value: str, start: int = 8000, end: int = 8999) -> int:
    span = end - start + 1
    digest = hashlib.sha256(value.encode()).hexdigest()
    return start + (int(digest[:8], 16) % span)


def flatten(data: dict[str, Any], prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            out.update(flatten(value, name))
        else:
            out[name] = str(value)
    return out


class DotTemplate(Template):
    idpattern = r"(?a:[_a-z][_a-z0-9]*(?:\.[_a-z][_a-z0-9]*)*)"


def render(template: Any, values: dict[str, Any]) -> str:
    if template is None:
        return ""
    text = str(template)
    flat = flatten(values)
    text = re.sub(r"\$\{([^}|]+)\|([^}]+)\}", lambda m: _filter(m.group(1), m.group(2), flat), text)
    return DotTemplate(text).safe_substitute(flat)


def _filter(name: str, filt: str, values: dict[str, str]) -> str:
    value = values.get(name, "")
    if filt in {"slug", "safe_slug"}:
        return slug(value)
    if filt in {"db", "db_name", "db_safe"}:
        return db(value)
    if filt.startswith("port_hash"):
        nums = [int(n) for n in re.findall(r"\d+", filt)]
        return str(port_hash(value, *(nums[:2] or [8000, 8999])))
    return value
