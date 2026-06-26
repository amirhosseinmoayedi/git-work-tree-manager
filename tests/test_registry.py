from __future__ import annotations

import sys
from types import SimpleNamespace

import pytest

from worktree_manager import registry


COLUMNS = ("id", "repo", "branch", "path", "task", "agent", "status", "resources", "created_at", "updated_at")


class FakeCursor:
    def __init__(self, rows=()):
        self._rows = list(rows)
        self.description = [(name,) for name in COLUMNS]

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return list(self._rows)


class FakeConnection:
    def __init__(self):
        self.rows: list[dict[str, object]] = []

    def execute(self, sql, params=()):
        normalized = " ".join(sql.lower().split())
        if normalized.startswith("create table"):
            return FakeCursor()
        if normalized.startswith("insert into worktrees"):
            row = dict(zip(COLUMNS[:8], params))
            row["created_at"] = f"{len(self.rows) + 1:04d}"
            row["updated_at"] = row["created_at"]
            self.rows.append(row)
            return FakeCursor()
        if normalized == "select * from worktrees where id=?":
            rows = [self._tuple(row) for row in self.rows if row["id"] == params[0]]
            return FakeCursor(rows)
        if normalized == "select * from worktrees order by created_at desc":
            rows = [self._tuple(row) for row in sorted(self.rows, key=lambda r: r["created_at"], reverse=True)]
            return FakeCursor(rows)
        if normalized.startswith("delete from worktrees where id=?"):
            self.rows = [row for row in self.rows if row["id"] != params[0]]
            return FakeCursor()
        if normalized.startswith("update worktrees set"):
            self._update(sql, params)
            return FakeCursor()
        raise AssertionError(f"unexpected SQL: {sql}")

    def commit(self):
        return None

    def _tuple(self, row):
        return tuple(row.get(name) for name in COLUMNS)

    def _update(self, sql, params):
        set_clause = sql[sql.lower().index(" set ") + 5 : sql.lower().index(" where ")]
        assignments = [item.strip() for item in set_clause.split(",")]
        values = iter(params[:-1])
        wid = params[-1]
        row = next(row for row in self.rows if row["id"] == wid)
        for assignment in assignments:
            field, expression = [part.strip() for part in assignment.split("=", 1)]
            if expression == "?":
                row[field] = next(values)
            elif expression.lower() == "current_timestamp":
                row[field] = "updated"


def test_registry_uses_local_turso_adapter(monkeypatch, tmp_path):
    connections = []

    def connect(path):
        connections.append(path)
        return FakeConnection()

    monkeypatch.setitem(sys.modules, "turso", SimpleNamespace(connect=connect))

    reg = registry.Registry(tmp_path / "registry.db")
    assert connections == [str(tmp_path / "registry.db")]

    reg.add(
        {
            "id": "smoke-codex-01",
            "repo": "/repo",
            "branch": "agent/smoke-codex-01",
            "path": "/repo/.worktrees/smoke-codex-01",
            "task": "smoke",
            "agent": "codex",
            "status": "created",
            "resources": {"ports": {"app": 8001}},
        }
    )

    assert reg.exists_id("smoke-codex-01")
    assert reg.get("smoke-codex-01")["resources"]["ports"]["app"] == 8001
    assert reg.used_ports() == {8001}

    reg.update("smoke-codex-01", status="failed", resources={"ports": {"app": 8002}})
    assert reg.get("smoke-codex-01")["status"] == "failed"
    assert reg.used_ports() == {8002}

    reg.remove("smoke-codex-01")
    assert reg.get("smoke-codex-01") is None


def test_default_registry_path_is_local(monkeypatch, tmp_path):
    monkeypatch.setenv("WTM_REGISTRY", str(tmp_path / "custom.db"))

    assert registry.default_db() == tmp_path / "custom.db"


def test_registry_rejects_unknown_update_fields(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "turso", SimpleNamespace(connect=lambda path: FakeConnection()))
    reg = registry.Registry(tmp_path / "registry.db")

    with pytest.raises(ValueError, match="cannot update registry field"):
        reg.update("missing", created_at="bad")
