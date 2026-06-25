from __future__ import annotations

import subprocess
from pathlib import Path


def run_git(repo: Path, args: list[str], check=True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True, check=check)

def repo_root(repo: Path) -> Path:
    return Path(run_git(repo, ["rev-parse", "--show-toplevel"]).stdout.strip()).resolve()

def create_worktree(repo: Path, path: Path, branch: str, base_ref: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    run_git(repo, ["worktree", "add", "-b", branch, str(path), base_ref])

def remove_worktree(repo: Path, path: Path, force: bool=False):
    args=["worktree", "remove"] + (["--force"] if force else []) + [str(path)]
    run_git(repo, args)

def delete_branch(repo: Path, branch: str, force: bool=False):
    run_git(repo, ["branch", "-D" if force else "-d", branch])

def list_worktrees(repo: Path) -> str:
    return run_git(repo, ["worktree", "list", "--porcelain"]).stdout

def current_status(path: Path) -> str:
    cp = run_git(path, ["status", "--porcelain"], check=False)
    return "missing" if cp.returncode else ("dirty" if cp.stdout.strip() else "clean")
