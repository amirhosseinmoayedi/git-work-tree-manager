from __future__ import annotations

from pathlib import Path
from .git_ops import current_status


def enrich(rec: dict) -> dict:
    r=dict(rec); p=Path(r["path"]); r["exists"]=p.exists(); r["git_status"]=current_status(p) if p.exists() else "missing"; return r
