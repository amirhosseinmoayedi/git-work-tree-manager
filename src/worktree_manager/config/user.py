from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .defaults import DEFAULT_WORKTREES_ROOT
from .yaml_loader import load_yaml


def user_config_path() -> Path:
    return Path(os.environ.get("WTM_CONFIG", "~/.config/worktree-manager/config.yml")).expanduser()


def load_user_config() -> dict[str, Any]:
    path = user_config_path()
    return load_yaml(path.read_text()) if path.exists() else {}


def default_worktrees_root() -> str:
    root = os.environ.get("WTM_WORKTREES_ROOT") or load_user_config().get("worktrees_root") or DEFAULT_WORKTREES_ROOT
    return str(Path(root).expanduser())
