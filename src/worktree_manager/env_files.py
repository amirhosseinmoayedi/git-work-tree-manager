from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any
from .templates import render


def write_env(repo: Path, wt_path: Path, cfg: dict[str, Any], values: dict[str, Any]):
    envcfg=cfg.get("env", {})
    source=repo / envcfg.get("source", ".env")
    output=wt_path / envcfg.get("output", ".env")
    if source.exists() and source.resolve() != output.resolve():
        output.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(source, output)
    data={}
    if output.exists():
        for line in output.read_text().splitlines():
            if line and not line.lstrip().startswith('#') and '=' in line:
                k,v=line.split('=',1); data[k]=v
    for key, tmpl in envcfg.get("overrides", {}).items():
        data[key]=render(tmpl, values)
    if data:
        output.write_text("\n".join(f"{k}={v}" for k,v in data.items()) + "\n")

def write_marker(path: Path, rec: dict[str, Any]):
    (path/"WORKTREE.md").write_text(f"# Worktree {rec['id']}\n\n- Branch: `{rec['branch']}`\n- Task: `{rec.get('task')}`\n- Agent: `{rec.get('agent')}`\n")
