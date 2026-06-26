from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from . import git_backend
from .config import default_worktrees_root, load_config
from .lifecycle import run_hooks, write_env, write_marker
from .runtime import allocate, enrich
from .state import Registry
from .templating import render, slug


def _countered(reg: Registry, cfg, values):
    counter = 1
    while True:
        vals = {**values, "counter": f"{counter:02d}"}
        wid = render(cfg["worktrees"]["id_template"], vals)
        if not reg.exists_id(wid):
            return wid, vals
        counter += 1


def _repo(path: Path | None) -> Path:
    return git_backend.repo_root((path or Path.cwd()).resolve())


def cmd_create(args):
    repo = _repo(args.repo)
    cfg = load_config(repo, args.config)
    reg = Registry()
    values = {
        "repo_path": str(repo),
        "worktrees_root": default_worktrees_root(),
        "task": args.task,
        "task_slug": slug(args.task),
        "branch_type": args.branch_type,
        "agent": args.agent,
        "project": cfg["project"],
    }
    wid, values = _countered(reg, cfg, values)
    values["worktree_id"] = wid
    branch = render(cfg["worktrees"]["branch_template"], values)
    values["branch"] = branch
    root = Path(render(cfg["worktrees"]["root"], values))
    if not root.is_absolute():
        root = (repo / root).resolve()
    wt_path = (root / wid).resolve()
    values["worktree_path"] = str(wt_path)
    resources = allocate(cfg, reg, values)
    values["resources"] = resources
    run_hooks("pre_create", cfg, repo, values, args.approve_hooks)
    try:
        git_backend.create_worktree(repo, wt_path, branch, args.base_ref or cfg["project"].get("default_base_ref", "main"))
        rec = {
            "id": wid,
            "repo": str(repo),
            "branch": branch,
            "path": str(wt_path),
            "task": args.task,
            "agent": args.agent,
            "status": "created",
            "resources": resources,
        }
        reg.add(rec)
        write_env(repo, wt_path, cfg, values)
        write_marker(wt_path, rec)
        run_hooks("post_create", cfg, wt_path, values, args.approve_hooks)
        if args.launch:
            subprocess.run(args.launch, cwd=wt_path, shell=True, check=True)
    except Exception:
        if reg.exists_id(wid):
            reg.update(wid, status="failed")
        raise
    print(json.dumps({"id": wid, "path": str(wt_path), "branch": branch, "resources": resources}, indent=2))


def cmd_list(args):
    for rec in Registry().list():
        e = enrich(rec)
        print(f"{e['id']}\t{e['git_status']}\t{e['branch']}\t{e['path']}")


def cmd_info(args):
    rec = Registry().get(args.id)
    if not rec:
        sys.exit(f"unknown worktree: {args.id}")
    print(json.dumps(enrich(rec), indent=2))


def cmd_shell(args):
    rec = Registry().get(args.id)
    if not rec:
        sys.exit(f"unknown worktree: {args.id}")
    print(f"cd {rec['path']}")


def cmd_remove(args):
    reg = Registry()
    rec = reg.get(args.id)
    if not rec:
        sys.exit(f"unknown worktree: {args.id}")
    repo = Path(rec["repo"])
    cfg = load_config(repo)
    values = {**rec, "worktree_id": args.id, "worktree_path": rec["path"], "repo_path": rec["repo"]}
    run_hooks("pre_remove", cfg, Path(rec["path"]), values, args.approve_hooks)
    git_backend.remove_worktree(repo, Path(rec["path"]), args.force)
    if args.delete_branch:
        git_backend.delete_branch(repo, rec["branch"], force=True)
    reg.remove(args.id)
    run_hooks("post_remove", cfg, repo, values, args.approve_hooks)
    print(f"removed {args.id}")


def cmd_doctor(args):
    subprocess.run(["git", "--version"], check=True)
    print(f"registry={Registry().path}")
    if args.repo:
        repo = _repo(args.repo)
        print(f"repo={repo} config_version={load_config(repo).get('version')}")
