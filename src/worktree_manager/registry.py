from __future__ import annotations

import json, os, sqlite3
from pathlib import Path
from typing import Any


def default_db() -> Path:
    return Path(os.environ.get("WTM_REGISTRY", Path.home()/".local/share/worktree-manager/registry.sqlite"))

class Registry:
    def __init__(self, path: Path | None = None):
        self.path = path or default_db(); self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path); self.conn.row_factory = sqlite3.Row; self.init()
    def init(self):
        self.conn.execute("""create table if not exists worktrees(
            id text primary key, repo text not null, branch text not null, path text not null,
            task text, agent text, status text not null, resources text not null default '{}',
            created_at text not null default current_timestamp, updated_at text not null default current_timestamp)""")
        self.conn.commit()
    def add(self, rec: dict[str, Any]):
        r = dict(rec); r["resources"] = json.dumps(r.get("resources", {}))
        self.conn.execute("insert into worktrees(id,repo,branch,path,task,agent,status,resources) values(:id,:repo,:branch,:path,:task,:agent,:status,:resources)", r); self.conn.commit()
    def update(self, wid: str, **fields: Any):
        if "resources" in fields: fields["resources"] = json.dumps(fields["resources"])
        fields["updated_at"] = "CURRENT_TIMESTAMP"
        sets=[]; vals={"id":wid}
        for k,v in fields.items():
            if v == "CURRENT_TIMESTAMP": sets.append(f"{k}=CURRENT_TIMESTAMP")
            else: sets.append(f"{k}=:{k}"); vals[k]=v
        self.conn.execute(f"update worktrees set {', '.join(sets)} where id=:id", vals); self.conn.commit()
    def get(self, wid: str):
        row = self.conn.execute("select * from worktrees where id=?", (wid,)).fetchone(); return self._row(row)
    def list(self):
        return [self._row(r) for r in self.conn.execute("select * from worktrees order by created_at desc")]
    def remove(self, wid: str):
        self.conn.execute("delete from worktrees where id=?", (wid,)); self.conn.commit()
    def exists_id(self, wid: str) -> bool: return self.get(wid) is not None
    def used_ports(self) -> set[int]:
        ports=set()
        for r in self.list():
            def walk(x):
                if isinstance(x, dict):
                    for v in x.values(): walk(v)
                elif isinstance(x, int): ports.add(x)
            walk(r.get("resources", {}))
        return ports
    def _row(self, row):
        if row is None: return None
        d=dict(row); d["resources"]=json.loads(d.get("resources") or "{}"); return d
