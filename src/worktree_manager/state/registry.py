from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


UPDATE_FIELDS = {"repo", "branch", "path", "task", "agent", "status", "resources"}


def default_db() -> Path:
    return Path(os.environ.get("WTM_REGISTRY", Path.home() / ".local/share/worktree-manager/registry.db"))


def connect_local_db(path: Path):
    try:
        import turso
    except ImportError as exc:
        raise RuntimeError("pyturso is required for the local Turso registry. Install with `pip install pyturso`.") from exc
    return turso.connect(str(path))


class Registry:
    def __init__(self, path: Path | None = None):
        self.path = path or default_db()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = connect_local_db(self.path)
        self.init()

    def init(self):
        self.conn.execute(
            """create table if not exists worktrees(
            id text primary key, repo text not null, branch text not null, path text not null,
            task text, agent text, status text not null, resources text not null default '{}',
            created_at text not null default current_timestamp, updated_at text not null default current_timestamp)"""
        )
        self.conn.commit()

    def add(self, rec: dict[str, Any]):
        r = dict(rec)
        r["resources"] = json.dumps(r.get("resources", {}))
        self.conn.execute(
            "insert into worktrees(id,repo,branch,path,task,agent,status,resources) values(?,?,?,?,?,?,?,?)",
            (r["id"], r["repo"], r["branch"], r["path"], r.get("task"), r.get("agent"), r["status"], r["resources"]),
        )
        self.conn.commit()

    def update(self, wid: str, **fields: Any):
        if "resources" in fields:
            fields["resources"] = json.dumps(fields["resources"])
        sets = []
        vals = []
        for key, value in fields.items():
            if key not in UPDATE_FIELDS:
                raise ValueError(f"cannot update registry field: {key}")
            sets.append(f"{key}=?")
            vals.append(value)
        sets.append("updated_at=current_timestamp")
        self.conn.execute(f"update worktrees set {', '.join(sets)} where id=?", (*vals, wid))
        self.conn.commit()

    def get(self, wid: str):
        cur = self.conn.execute("select * from worktrees where id=?", (wid,))
        row = cur.fetchone()
        return self._row(row, cur.description)

    def list(self):
        cur = self.conn.execute("select * from worktrees order by created_at desc")
        return [self._row(row, cur.description) for row in cur.fetchall()]

    def remove(self, wid: str):
        self.conn.execute("delete from worktrees where id=?", (wid,))
        self.conn.commit()

    def exists_id(self, wid: str) -> bool:
        return self.get(wid) is not None

    def used_ports(self) -> set[int]:
        ports = set()

        def walk(value):
            if isinstance(value, dict):
                for child in value.values():
                    walk(child)
            elif isinstance(value, int):
                ports.add(value)

        for rec in self.list():
            walk(rec.get("resources", {}))
        return ports

    def _row(self, row, description=None):
        if row is None:
            return None
        if isinstance(row, dict):
            data = dict(row)
        elif hasattr(row, "keys"):
            data = {key: row[key] for key in row.keys()}
        else:
            columns = [column[0] for column in description or ()]
            data = dict(zip(columns, row))
        data["resources"] = json.loads(data.get("resources") or "{}")
        return data
