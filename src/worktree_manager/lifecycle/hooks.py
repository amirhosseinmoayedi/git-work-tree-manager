from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from ..templating import render


def run_hooks(name: str, cfg: dict[str, Any], cwd: Path, values: dict[str, Any], approve: bool = False):
    for cmd in cfg.get("hooks", {}).get(name, []) or []:
        rendered = render(cmd, values)
        if not approve:
            raise RuntimeError(f"hook approval required for {name}: {rendered}")
        print(f"[wtm] {name}: {rendered}")
        subprocess.run(rendered, cwd=cwd, shell=True, check=True)
