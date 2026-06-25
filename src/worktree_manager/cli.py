from __future__ import annotations

import argparse, json, subprocess, sys
from pathlib import Path

from .config import load_config
from .templates import slug, render
from .registry import Registry
from .resources import allocate
from .env_files import write_env, write_marker
from .hooks import run_hooks
from . import git_ops
from .status import enrich


def _countered(reg: Registry, cfg, values):
    counter=1
    while True:
        vals={**values, "counter": f"{counter:02d}"}
        wid=render(cfg["worktrees"]["id_template"], vals)
        if not reg.exists_id(wid): return wid, vals
        counter += 1

def _repo(path: Path | None) -> Path:
    return git_ops.repo_root((path or Path.cwd()).resolve())

def cmd_create(args):
    repo=_repo(args.repo); cfg=load_config(repo); reg=Registry()
    values={"repo_path": str(repo), "task": args.task, "task_slug": slug(args.task), "agent": args.agent, "project": cfg["project"]}
    wid, values=_countered(reg, cfg, values); values["worktree_id"]=wid
    branch=render(cfg["worktrees"]["branch_template"], values); values["branch"]=branch
    root=Path(render(cfg["worktrees"]["root"], values))
    if not root.is_absolute(): root=(repo/root).resolve()
    wt_path=(root/wid).resolve(); values["worktree_path"]=str(wt_path)
    resources=allocate(cfg, reg, values); values["resources"]=resources
    run_hooks("pre_create", cfg, repo, values, args.approve_hooks)
    try:
        git_ops.create_worktree(repo, wt_path, branch, args.base_ref or cfg["project"].get("default_base_ref", "main"))
        rec={"id":wid,"repo":str(repo),"branch":branch,"path":str(wt_path),"task":args.task,"agent":args.agent,"status":"created","resources":resources}
        reg.add(rec); write_env(repo, wt_path, cfg, values); write_marker(wt_path, rec)
        run_hooks("post_create", cfg, wt_path, values, args.approve_hooks)
        if args.launch: subprocess.run(args.launch, cwd=wt_path, shell=True, check=True)
    except Exception:
        if reg.exists_id(wid): reg.update(wid, status="failed")
        raise
    print(json.dumps({"id": wid, "path": str(wt_path), "branch": branch, "resources": resources}, indent=2))

def cmd_list(args):
    for r in Registry().list():
        e=enrich(r); print(f"{e['id']}\t{e['git_status']}\t{e['branch']}\t{e['path']}")

def cmd_info(args):
    rec=Registry().get(args.id)
    if not rec: sys.exit(f"unknown worktree: {args.id}")
    print(json.dumps(enrich(rec), indent=2))

def cmd_shell(args):
    rec=Registry().get(args.id)
    if not rec: sys.exit(f"unknown worktree: {args.id}")
    print(f"cd {rec['path']}")

def cmd_remove(args):
    reg=Registry(); rec=reg.get(args.id)
    if not rec: sys.exit(f"unknown worktree: {args.id}")
    repo=Path(rec["repo"]); cfg=load_config(repo); values={**rec, "worktree_id": args.id, "worktree_path": rec["path"], "repo_path": rec["repo"]}
    run_hooks("pre_remove", cfg, Path(rec["path"]), values, args.approve_hooks)
    git_ops.remove_worktree(repo, Path(rec["path"]), args.force)
    if args.delete_branch: git_ops.delete_branch(repo, rec["branch"], force=True)
    reg.remove(args.id); run_hooks("post_remove", cfg, repo, values, args.approve_hooks)
    print(f"removed {args.id}")

def cmd_doctor(args):
    subprocess.run(["git", "--version"], check=True)
    print(f"registry={Registry().path}")
    if args.repo:
        r=_repo(args.repo); print(f"repo={r} config_version={load_config(r).get('version')}")

def build_parser():
    p=argparse.ArgumentParser(prog="wtm", description="Git worktree and environment manager for agent workflows.")
    sub=p.add_subparsers(required=True)
    c=sub.add_parser("create"); c.add_argument("--repo", type=Path, required=True); c.add_argument("--task", required=True); c.add_argument("--agent", default="default"); c.add_argument("--base-ref"); c.add_argument("--approve-hooks", action="store_true"); c.add_argument("--launch"); c.set_defaults(func=cmd_create)
    l=sub.add_parser("list"); l.set_defaults(func=cmd_list)
    i=sub.add_parser("info"); i.add_argument("id"); i.set_defaults(func=cmd_info)
    s=sub.add_parser("shell"); s.add_argument("id"); s.set_defaults(func=cmd_shell)
    r=sub.add_parser("remove"); r.add_argument("id"); r.add_argument("--force", action="store_true"); r.add_argument("--delete-branch", action="store_true"); r.add_argument("--approve-hooks", action="store_true"); r.set_defaults(func=cmd_remove)
    d=sub.add_parser("doctor"); d.add_argument("--repo", type=Path); d.set_defaults(func=cmd_doctor)
    return p

def main(argv=None):
    args=build_parser().parse_args(argv); return args.func(args)

if __name__ == "__main__": main()
