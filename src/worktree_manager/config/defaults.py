from __future__ import annotations

from typing import Any

DEFAULT_CONFIG: dict[str, Any] = {
    "version": 1,
    "project": {"name": None, "default_base_ref": "main"},
    "worktrees": {
        "root": "${worktrees_root}/${project.name}",
        "id_template": "${task_slug}-${agent}-${counter}",
        "branch_template": "${branch_type}/${task_slug}-${agent}-${counter}",
    },
    "resources": {"ports": {}, "env": {}},
    "env": {"source": ".env", "output": ".env", "copy_ignored": [".env"], "overrides": {}},
    "hooks": {"pre_create": [], "post_create": [], "pre_remove": [], "post_remove": []},
}

DEFAULT_WORKTREES_ROOT = "~/projects/.worktrees"
